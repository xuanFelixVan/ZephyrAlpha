# [TTL] permanent
"""detect_private_key 豁免登记册机制红蓝测试（st-govfix-g4-20261007）。

被测：scripts/governance/d7_code/detect_private_key.py 的
config/governance/private_key_exempt_registry.yaml 白名单通道：
- 册加载（合法/缺失/损坏/空册 → 内建 fallback）
- 精确路径豁免（POSIX 归一化；旧址路径退役后不再豁免）
- _scan_files 红蓝（白名单外私钥必报 / 登记件豁免 / 反斜杠路径归一）
- 陈旧豁免审计（index 与盘面均无 → STALE 计数）

测试隔离：全部走 tmp_path 与 monkeypatch，零写生产路径、零真实 git 依赖
（存活性判定注入 fake checker）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "governance" / "d7_code" / "detect_private_key.py"
sys.path.insert(0, str(SCRIPT.parent))

import detect_private_key as dpk  # noqa: E402

_PEM = "-----BEGIN RSA PRIVATE KEY-----\nbody\n-----END RSA PRIVATE KEY-----\n"


def _write_registry(tmp_path: Path, entries: list[dict]) -> Path:
    """写临时豁免登记册 YAML，monkeypatch 检测器的册路径指向它。"""
    reg = tmp_path / "private_key_exempt_registry.yaml"
    lines = ["exempt_paths:"]
    for e in entries:
        lines.append(f"- path: {e['path']}")
        lines.append(f"  reason: {e.get('reason', 'test')}")
    reg.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return reg


@pytest.fixture()
def isolated_registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """隔离册路径上下文：_EXEMPT_REGISTRY_PATH 指向 tmp_path 下的册文件。"""
    reg = tmp_path / "private_key_exempt_registry.yaml"
    monkeypatch.setattr(dpk, "_EXEMPT_REGISTRY_PATH", reg)
    return reg


def test_load_registry_blue(isolated_registry: Path) -> None:
    """蓝：合法册加载——路径集与条目一致。"""
    isolated_registry.write_text(
        "exempt_paths:\n"
        "- path: src/zephyr/security/llm_defense/llm_security/patterns/secrets.py\n"
        "  reason: pattern truth source\n"
        "- path: tests/ai/llm_security/test_secrets.py\n"
        "  reason: fixture\n",
        encoding="utf-8",
    )
    paths = dpk._load_exempt_registry()
    assert paths == {
        "src/zephyr/security/llm_defense/llm_security/patterns/secrets.py",
        "tests/ai/llm_security/test_secrets.py",
    }


def test_load_registry_missing_falls_back(isolated_registry: Path, capsys: pytest.CaptureFixture) -> None:
    """红：册缺失 → 退化内建最小集（2 条真源件）+ stderr 告警。"""
    paths = dpk._load_exempt_registry()
    assert paths == set(dpk._FALLBACK_EXEMPT_PATHS)
    assert len(paths) == 2
    assert "退化" in capsys.readouterr().err


def test_load_registry_corrupt_falls_back(isolated_registry: Path) -> None:
    """红：册损坏（非 dict 结构）→ 内建最小集。"""
    isolated_registry.write_text("not: [a, valid, registry]\n", encoding="utf-8")
    assert dpk._load_exempt_registry() == set(dpk._FALLBACK_EXEMPT_PATHS)


def test_load_registry_empty_entries_falls_back(isolated_registry: Path) -> None:
    """红：册存在但 exempt_paths 为空 → 内建最小集（防空册形同全豁免失效）。"""
    isolated_registry.write_text("exempt_paths: []\n", encoding="utf-8")
    assert dpk._load_exempt_registry() == set(dpk._FALLBACK_EXEMPT_PATHS)


def test_is_exempt_posix_normalization(isolated_registry: Path) -> None:
    """豁免比对 POSIX 归一化：反斜杠 staged 路径命中正斜杠册条目。"""
    exempt = {"tests/meta/fix/test_fix_safety.py"}
    assert dpk._is_exempt("tests\\meta\\fix\\test_fix_safety.py", exempt)
    assert not dpk._is_exempt("tests/meta/fix/other.py", exempt)


def test_scan_red_unregistered_path_reports(tmp_path: Path, isolated_registry: Path) -> None:
    """红：白名单外文件含 PEM 标记 → 必报。"""
    isolated_registry.write_text("exempt_paths:\n- path: tests/meta/fix/test_fix_safety.py\n", encoding="utf-8")
    target = tmp_path / "unregistered_key.py"
    target.write_text(_PEM, encoding="utf-8")
    findings = dpk._scan_files([str(target)], dpk._load_exempt_registry())
    assert len(findings) == 1
    assert "1 处私钥标记" in findings[0]


def test_scan_blue_registered_path_exempt(tmp_path: Path, isolated_registry: Path) -> None:
    """蓝：登记 fixture 路径含 PEM 标记 → 豁免不报（机制化主用例）。"""
    isolated_registry.write_text("exempt_paths:\n- path: tests/meta/fix/test_fix_safety.py\n", encoding="utf-8")
    target = tmp_path / "test_fix_safety.py"
    target.write_text(_PEM, encoding="utf-8")
    # 相对路径形（模拟 staged rel path）：cwd 切到 tmp_path 使 Path(rel).exists() 命中
    import os

    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        findings = dpk._scan_files(["tests/meta/fix/test_fix_safety.py"], dpk._load_exempt_registry())
    finally:
        os.chdir(old)
    assert findings == []


def test_scan_old_stale_path_not_exempt(tmp_path: Path, isolated_registry: Path) -> None:
    """红：旧硬编码 4 条 tests/ 旧址路径不在新册 → 不再豁免（退役生效）。"""
    isolated_registry.write_text("exempt_paths: []\n", encoding="utf-8")
    exempt = dpk._load_exempt_registry()  # fallback：真源件 2 条
    assert not dpk._is_exempt("tests/llm_security/test_secrets.py", exempt)
    assert not dpk._is_exempt("tests/test_credential_rotation_trigger.py", exempt)


def test_stale_audit_counts_dead_entries(isolated_registry: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """陈旧审计：index 与盘面均无 → STALE 计数；盘面存在 → 活。"""
    exempt = {"tests/ghost/dead.py", "tests/meta/fix/test_fix_safety.py"}
    monkeypatch.setattr(dpk, "_is_registry_path_alive", lambda p: p == "tests/meta/fix/test_fix_safety.py")
    assert dpk._audit_stale_exemptions(exempt) == 1


def test_real_registry_loads_in_repo() -> None:
    """真册冒烟：仓库登记册可加载且 ≥6 条（2 真源 + 4 fixture 迁移）。"""
    paths = dpk._load_exempt_registry()
    assert len(paths) >= 6
    assert "src/zephyr/security/llm_defense/llm_security/patterns/secrets.py" in paths
    assert "tests/ai/llm_security/test_secrets.py" in paths
