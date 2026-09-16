# [A_test] module_id: MOD-TEST_ollama_version_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | scripts/ops/ollama_version_guard.py | §
# [MODULE] tests.ops.test_ollama_version_guard
# [INVARIANTS] 版本解析容错；合规判定=严格大于崩溃构建天花板(0.32.1)；SHA-256 完整性校验为唯一落装前置；--check 零副作用幂等；--upgrade 无完整性锚拒绝盲装
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/ops/test_ollama_version_guard.py -q
# [TTL] permanent
"""#移交③ Ollama 版本守卫治本钉（2026-09-16，lane J）。

证明：崩溃构建天花板判定正确（0.32.1 非合规、0.34.1 合规）；完整性校验是落装唯一前置；
--check 默认零副作用且幂等；--upgrade 无校验和=拒绝盲装（软件安装 Owner 门位不破）。
纯函数测试 hermetic（不触网、不安装、不写生产）；live --check 断言现装版本已合规（待办解除凭据）。
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "ops" / "ollama_version_guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("_ollama_version_guard_under_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # 注册到 sys.modules：脚本内 @dataclass + from __future__ import annotations 的
    # 字段类型解析需装饰期能找到所属模块。
    import sys

    sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.modules.pop(spec.name, None)
    return mod


@pytest.fixture(scope="module")
def g():
    return _load()


class TestParseVersion:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("0.34.1", (0, 34, 1)),
            ("ollama version is 0.32.1", (0, 32, 1)),
            ("Warning: could not connect\nWarning: client version is 0.34.1", (0, 34, 1)),
            ("v1.2.3", (1, 2, 3)),
        ],
    )
    def test_parse(self, g, text, expected):
        assert g.parse_version(text) == expected

    @pytest.mark.parametrize("bad", ["", "no digits here", None])
    def test_parse_none(self, g, bad):
        assert g.parse_version(bad) is None


class TestComplianceJudgment:
    def test_crash_bearer_ceiling_is_0_32_1(self, g):
        assert g.CRASH_BEARING_CEILING == (0, 32, 1)

    @pytest.mark.parametrize("v", [(0, 32, 1), (0, 31, 0), (0, 0, 1)])
    def test_at_or_below_ceiling_non_compliant(self, g, v):
        assert g.is_compliant(v) is False

    @pytest.mark.parametrize("v", [(0, 32, 2), (0, 33, 0), (0, 34, 1), (1, 0, 0)])
    def test_above_ceiling_compliant(self, g, v):
        assert g.is_compliant(v) is True

    def test_none_non_compliant(self, g):
        assert g.is_compliant(None) is False

    def test_judge_verdict(self, g):
        v = g.judge((0, 34, 1))
        assert v.installed is True and v.compliant is True and v.version == "0.34.1"
        v0 = g.judge(None)
        assert v0.installed is False and v0.compliant is False


class TestIntegrityVerify:
    def test_sha256_matches(self, g, tmp_path):
        f = tmp_path / "payload.bin"
        f.write_bytes(b"ollama-installer-bytes")
        digest = g.sha256_of(f)
        assert g.verify_sha256(f, digest) is True
        assert g.verify_sha256(f, digest.upper()) is True  # 大小写不敏感

    def test_sha256_mismatch(self, g, tmp_path):
        f = tmp_path / "payload.bin"
        f.write_bytes(b"good")
        assert g.verify_sha256(f, "0" * 64) is False

    def test_empty_expected_rejected(self, g, tmp_path):
        f = tmp_path / "payload.bin"
        f.write_bytes(b"good")
        assert g.verify_sha256(f, "") is False

    def test_missing_file_rejected(self, g, tmp_path):
        assert g.verify_sha256(tmp_path / "absent.bin", "a" * 64) is False


class TestCheckNoSideEffectAndIdempotent:
    def test_check_monkeypatched_compliant_exit0(self, g, monkeypatch):
        monkeypatch.setattr(g, "detect_installed_version", lambda *_a, **_k: (0, 34, 1))
        assert g.cmd_check(False, "ollama") == g.EXIT_PASS

    def test_check_monkeypatched_noncompliant(self, g, monkeypatch, capsys):
        monkeypatch.setattr(g, "detect_installed_version", lambda *_a, **_k: (0, 32, 1))
        rc = g.cmd_check(False, "ollama")
        assert rc == g.EXIT_NOT_COMPLIANT
        assert "🔴" in capsys.readouterr().out

    def test_check_not_installed(self, g, monkeypatch):
        monkeypatch.setattr(g, "detect_installed_version", lambda *_a, **_k: None)
        assert g.cmd_check(False, "ollama") == g.EXIT_NOT_INSTALLED

    def test_check_repeatable(self, g, monkeypatch):
        monkeypatch.setattr(g, "detect_installed_version", lambda *_a, **_k: (0, 34, 1))
        assert g.cmd_check(False, "ollama") == g.cmd_check(False, "ollama") == g.EXIT_PASS


class TestUpgradeRefusesBlindInstall:
    def test_upgrade_without_integrity_anchor_rejected(self, g):
        rc = g.main(["--upgrade", "--installer-path", "whatever.exe"])
        assert rc == g.EXIT_ERROR

    def test_upgrade_compliant_idempotent_noop(self, g, monkeypatch, tmp_path):
        monkeypatch.setattr(g, "detect_installed_version", lambda *_a, **_k: (0, 34, 1))
        inst = tmp_path / "OllamaSetup.exe"
        inst.write_bytes(b"installer")
        rc = g.main(["--upgrade", "--installer-path", str(inst), "--expected-sha256", "ab" * 32])
        assert rc == g.EXIT_PASS  # 已合规 → no-op（不重装、不校验）

    def test_upgrade_integrity_fail_aborts_without_install(self, g, monkeypatch, tmp_path):
        # 强制走升级（当前非合规）→ 完整性校验失败 → 中止且不落装
        calls: list[list[str]] = []
        monkeypatch.setattr(g, "detect_installed_version", lambda *_a, **_k: (0, 32, 1))
        monkeypatch.setattr(g, "_run_or_print", lambda cmd, dry: calls.append(cmd) or 0)
        inst = tmp_path / "OllamaSetup.exe"
        inst.write_bytes(b"tampered")
        rc = g.main(["--upgrade", "--installer-path", str(inst), "--expected-sha256", "ff" * 32])
        assert rc == g.EXIT_ERROR
        assert calls == [], "完整性校验失败仍尝试落装——违反不变量"


class TestLiveSystemEvidence:
    """交付凭据：现装 Ollama 已 > 崩溃构建（待办即时阻断在环境层已解除）。"""

    def test_installed_ollama_compliant_or_absent(self, g):
        ver = g.detect_installed_version("ollama")
        if ver is None:
            pytest.skip("ollama 不在本执行环境 PATH（不影响守卫逻辑正确性）")
        assert g.is_compliant(ver) is True, f"现装 {ver} 仍非合规——须走 --upgrade"


class TestServeTaskPreconditionPin:
    """机器化前置钉（2026-09-16 Ollama 依赖定性）：注册脚本的版本地板与本守卫同源。

    `scripts/register_ollama_serve_task.ps1` 在注册 ZephyrAlpha_OllamaServe 常驻任务前
    自检 `ollama --version`，<= 地板即 throw（附本守卫 --upgrade 一条命令）。两处阈值
    若漂移，本测试即红——把"记得升级 Ollama"的人工待办转成断言，不再靠口头。
    """

    PS1_PATH = REPO_ROOT / "scripts" / "register_ollama_serve_task.ps1"

    def _ps1_text(self) -> str:
        assert self.PS1_PATH.exists(), "注册脚本消失——Ollama 常驻服务失去版本前置"
        return self.PS1_PATH.read_text(encoding="utf-8")

    def test_floor_matches_guard_ceiling(self, g):
        m = re.search(r'\$MinOllamaVersion\s*=\s*"([\d.]+)"', self._ps1_text())
        assert m, "register_ollama_serve_task.ps1 丢失 $MinOllamaVersion 前置（人工待办会复发）"
        floor = tuple(int(x) for x in m.group(1).split("."))
        assert floor == tuple(g.CRASH_BEARING_CEILING), f"阈值漂移: ps1={floor} guard={g.CRASH_BEARING_CEILING}"

    def test_floor_is_itself_non_compliant(self, g):
        """两侧语义一致：地板版本本身判非合规（严格大于）。"""
        assert g.is_compliant(tuple(g.CRASH_BEARING_CEILING)) is False
        assert g.is_compliant((g.CRASH_BEARING_CEILING[0], g.CRASH_BEARING_CEILING[1], g.CRASH_BEARING_CEILING[2] + 1))

    def test_ps1_mentions_actionable_remediation(self):
        text = self._ps1_text()
        assert "ollama_version_guard.py --upgrade" in text, "前置消息未给出可执行修复命令"

    def test_ps1_is_pure_ascii(self):
        """宪法 §9.7：PowerShell 5.1 无 BOM 按 GBK 解码，非 ASCII 注释=假语法错误。"""
        raw = self.PS1_PATH.read_bytes()
        offenders = [i for i, b in enumerate(raw) if b > 127]
        assert not offenders, f"ps1 含非 ASCII 字节 @ {offenders[:5]}"
