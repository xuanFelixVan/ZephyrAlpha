# [BLUEPRINT] MOD-GOV_CHECK_ALGO_FLOW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §
# [A_module] module_id=MOD-GOV_CHECK_ALGO_FLOW | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""compare_pytest_configs 行为锚点测试（2026-09-15 外审遗留②配套）。

覆盖：对齐通过 / markers 漂移检出 / 单行分号 markers（pytest linelist 只注册第一个，
历史失效写法）检出 / timeout 漂移检出 / cache_dir 禁入检出 / ini 缺失检出
（精简跑法寄居根目录既有纳管件 py.ini 的 [pytest] 段，裁定#275→#278：
DCR-005 禁 config/*.ini，独立件需 .gitignore 放行=撞 PROTECTED-PATHS Owner 闸）/
误段名 [tool:pytest] 检出（.ini 中该段被 pytest 整体忽略=configfile 照打而零配置，
2026-09-16 移植当日探针实证）/ addopts 缺 --strict-markers 检出 / 非法 TOML 降级 exit 2。
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[4] / "scripts" / "governance" / "d7_code" / "compare_pytest_configs.py"
_spec = importlib.util.spec_from_file_location("compare_pytest_configs", _SCRIPT)
cpc = importlib.util.module_from_spec(_spec)
sys.modules["compare_pytest_configs"] = cpc
_spec.loader.exec_module(cpc)

_ALIGNED_PYPROJECT = """
[tool.pytest.ini_options]
addopts = ["-v"]
timeout = 120
markers = [
    "slow: marks slow tests",
    "financial: marks financial calculation tests",
]
"""

_ALIGNED_INI = """
[pytest]
addopts = -q --strict-markers
timeout = 120
markers =
    slow: marks slow tests
    financial: marks financial calculation tests
"""


def _make_repo(tmp_path: Path, pyproject: str, ini: str | None) -> Path:
    (tmp_path / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    if ini is not None:
        (tmp_path / "py.ini").write_text(ini, encoding="utf-8")
    return tmp_path


def test_aligned_configs_pass(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, _ALIGNED_INI)
    findings, _ = cpc.compare(root)
    assert findings == []


def test_marker_set_drift_detected(tmp_path: Path) -> None:
    ini = _ALIGNED_INI.replace("    financial: marks financial calculation tests\n", "")
    assert "financial" not in ini  # 前置自证：确已删掉该 marker 行
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, _ = cpc.compare(root)
    assert any("financial" in f and "pyproject" in f for f in findings)


def test_ini_single_line_semicolon_markers_detected(tmp_path: Path) -> None:
    """历史失效写法钉扎：pytest markers 是 linelist，单行分号只注册第一个→必判漂移。"""
    ini = (
        "[pytest]\naddopts = -q --strict-markers\ntimeout = 120\n"
        "markers = slow: marks slow tests; financial: marks financial calculation tests\n"
    )
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, detail = cpc.compare(root)
    assert detail["markers_ini"] == ["slow"]
    assert any("financial" in f and "pyproject" in f for f in findings)


def test_timeout_drift_detected(tmp_path: Path) -> None:
    ini = _ALIGNED_INI.replace("timeout = 120", "timeout = 60")
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, _ = cpc.compare(root)
    assert any("timeout" in f for f in findings)
    # markers 集合同值→timeout 是唯一漂移源（防空断言：另一类漂移不得混进来）
    assert len(findings) == 1


def test_cache_dir_in_ini_rejected(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, _ALIGNED_INI + "\ncache_dir = .runtime/tmp/pytest_cache\n")
    findings, _ = cpc.compare(root)
    assert any("cache_dir" in f for f in findings)


def test_missing_ini_detected(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, None)
    findings, _ = cpc.compare(root)
    hit = [f for f in findings if "py.ini 缺失" in f]
    assert hit, findings
    assert not any("pytest_min.ini" in f for f in hit), hit


def test_inert_tool_pytest_section_detected(tmp_path: Path) -> None:
    """钉扎 2026-09-16 实测缺陷：.ini 里写 [tool:pytest] 被 pytest 整体忽略。

    pytest 按后缀分支——.ini 只读 [pytest]，[tool:pytest] 仅 .cfg 生效。误段名时
    pytest 仍打印 `configfile: py.ini`，但 markers/--strict-markers/timeout/
    norecursedirs 全部零生效："看着有配置、实则无任何配置"的静默放宽，
    必须判漂移（否则精简跑法比缺失更危险——缺失至少会报，误段名什么都不报）。
    """
    ini = _ALIGNED_INI.replace("[pytest]", "[tool:pytest]")
    assert "[pytest]" not in ini
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, detail = cpc.compare(root)
    assert detail["ini_section"] == "tool:pytest"
    assert any("[tool:pytest]" in f for f in findings), findings
    # 早退语义：段无效时不再叠加 markers/timeout 比对噪声
    assert len(findings) == 1, findings


def test_ini_without_strict_markers_detected(tmp_path: Path) -> None:
    """精简跑法丢 --strict-markers = A 类漂移不可见（收窄语义被悄悄放宽）。"""
    ini = _ALIGNED_INI.replace("addopts = -q --strict-markers", "addopts = -q")
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, detail = cpc.compare(root)
    assert detail["strict_markers_in_ini"] is False
    assert any("strict-markers" in f for f in findings), findings


def test_repo_py_ini_actually_aligned() -> None:
    """真仓 py.ini vs pyproject 必须零漂移（防"测试全用 tmp fixture、真配置烂了没人知道"）。"""
    root = Path(__file__).resolve().parents[4]
    if not (root / "py.ini").is_file():
        pytest.skip("py.ini 缺失=检出破损（根目录既有纳管件）")
    findings, detail = cpc.compare(root)
    assert findings == [], findings
    assert "slow" in detail["markers_ini"] and detail["ini_section"] == "pytest"


def test_deselect_single_side_drift_detected(tmp_path: Path) -> None:
    """看守项 E 判别力自证（甲案断源，统筹 2026-10-13 追加③）：单侧点名排除必须判漂移。

    双侧同名单时必须零 findings——否则 E 项恒红＝无判别力的尺（在册教训：判通过的
    脚本须先证明它能红）。ini 侧用多行续行写法，同时钉住"续行确实被解析成 addopts 值"。
    """
    one = "tests/backtest/test_sim_daily_runner.py::test_plan_bridge_attack_state_is_unexecutable"
    py = _ALIGNED_PYPROJECT.replace('addopts = ["-v"]', f'addopts = ["-v", "--deselect={one}"]')
    # 单侧：pyproject 有、ini 无 → 必判漂移
    root = _make_repo(tmp_path, py, _ALIGNED_INI)
    findings, detail = cpc.compare(root)
    assert any("--deselect" in f for f in findings), findings
    assert detail["deselect_pyproject"] == [one]
    assert detail["deselect_ini"] == []
    # 双侧等值（ini 缩进续行）→ 零 findings
    both = tmp_path / "both"
    both.mkdir()
    ini = _ALIGNED_INI.replace("addopts = -q --strict-markers", f"addopts = -q --strict-markers\n    --deselect={one}")
    _make_repo(both, py, ini)
    findings2, detail2 = cpc.compare(both)
    assert findings2 == [], findings2
    assert detail2["deselect_ini"] == [one]


def test_repo_deselect_roster_is_live_and_effective() -> None:
    """真配置面钉扎：名单存在＋指向真实（防陈旧排除）＋两种跑法实际排除生效。

    三件各有病根：①双配置不等值＝假止血（精简跑法照写生产）；②测试改名后陈旧
    --deselect 静默零命中＝断源悄悄失效；③反向对照——同文件其余用例必须仍被收集，
    防"整文件/整目录被跳过"式过度止血被当成精确断源。
    """
    root = Path(__file__).resolve().parents[4]
    if not (root / "py.ini").is_file():
        pytest.skip("py.ini 缺失=检出破损（根目录既有纳管件）")
    findings, detail = cpc.compare(root)
    assert findings == [], findings
    roster = detail["deselect_pyproject"]
    assert len(roster) >= 6, f"甲案六支触库 node id 为下限，现名册 {len(roster)} 支"
    assert roster == detail["deselect_ini"]
    for node in roster:
        file_part, _, fn = node.partition("::")
        host = root / file_part
        assert host.is_file(), f"排除名单指向缺失文件（陈旧排除=静默假止血）: {node}"
        text = host.read_text(encoding="utf-8", errors="replace")
        assert f"def {fn}(" in text, f"排除名单里的函数名在宿主文件中不存在: {node}"

    target = roster[0].partition("::")[0]
    names = {n.partition("::")[2] for n in roster if n.startswith(f"{target}::")}
    out = subprocess.run(
        [sys.executable, "-m", "pytest", target, "--collect-only", "-q"],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=600,
    ).stdout
    for fn in names:
        assert not re.search(rf"\b{re.escape(fn)}\b", out), f"{fn} 仍出现在收集面（排除未生效）"
    m = re.search(r"(\d+)/(\d+) tests? collected(?: \((\d+) deselected\))?", out)
    assert m, out[-400:]
    assert int(m.group(3) or 0) == len(names), f"排除支数与名册不符: {out[-300:]}"
    assert int(m.group(1)) >= 5, f"同文件其余用例须仍被收集（反向对照）: {out[-300:]}"


def test_main_never_raises_on_garbage(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "pyproject.toml").write_text("not [valid toml", encoding="utf-8")
    rc = cpc.main([], repo_root=tmp_path)
    assert rc in (cpc.EXIT_FINDINGS, cpc.EXIT_ERROR)
    assert rc != cpc.EXIT_PASS
