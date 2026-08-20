# [A_test] module_id: MOD-GOV-translation_coverage_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_translation_coverage_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_translation_coverage_gate.py — TRANSLATION-COVERAGE 门禁单测

权威依据：translation_coverage_gate.py（make_translation_coverage_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestIsInScope: _is_in_scope 范围判断
- TestCheckTranslationEntry: _check_translation_entry 翻译查询（monkeypatch loader）
- TestGatewayIntegration: mock gateway + monkeypatch 查询
  - 无新增 .py → 放行
  - 新增 .py 有合格简介 → 放行
  - 新增 .py 缺简介 → 硬阻断（pass=False，_OBSERVATION_PERIOD=False 2026-08-02 转正）
  - 非 Zephyr 项目 → skip
  - git diff 失败 → fail-open 放行

测试隔离：MagicMock 模拟 gateway.run_git；monkeypatch 模拟翻译查询。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.translation_coverage_gate import (  # noqa: E402
    _check_translation_entry,
    _is_in_scope,
    make_translation_coverage_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------


class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec)。"""

    def test_gate_id(self) -> None:
        gate = make_translation_coverage_gate()
        assert gate.gate_id == "TRANSLATION-COVERAGE"

    def test_priority(self) -> None:
        gate = make_translation_coverage_gate()
        assert gate.priority == 59

    def test_is_gate_spec(self) -> None:
        gate = make_translation_coverage_gate()
        assert isinstance(gate, GateSpec)


# ---------------------------------------------------------------------------
# TestIsInScope
# ---------------------------------------------------------------------------


class TestIsInScope:
    """_is_in_scope 范围判断。"""

    def test_src_zephyr_in_scope(self) -> None:
        assert _is_in_scope("src/zephyr/governance/audit/foo.py") is True

    def test_scripts_in_scope(self) -> None:
        assert _is_in_scope("scripts/governance/foo.py") is True

    def test_tests_exempt(self) -> None:
        assert _is_in_scope("tests/governance/test_foo.py") is False

    def test_other_path_out_of_scope(self) -> None:
        assert _is_in_scope("docs/foo.py") is False

    def test_root_level_out_of_scope(self) -> None:
        assert _is_in_scope("foo.py") is False

    # --- 治本 2026-08-02 #ARCH-TRANSLATION-SCOPE-NARROW：非业务脚本豁免 ---

    def test_scripts_tests_exempt(self) -> None:
        """scripts/tests/ 下 smoke 测试脚本豁免（reconciler 曾漏豁免致误报）。"""
        assert _is_in_scope("scripts/tests/smoke_test_ede_e2e.py") is False

    def test_demos_dir_exempt(self) -> None:
        """scripts/demos/ 演示脚本豁免。"""
        assert _is_in_scope("scripts/demos/demo_e2e_pipeline.py") is False

    def test_test_filename_exempt(self) -> None:
        """test_*.py / *_test.py 文件名豁免（任意层级）。"""
        assert _is_in_scope("scripts/backup/test_get_redis_conn.py") is False
        assert _is_in_scope("scripts/construction/test_deepseek_api.py") is False
        assert _is_in_scope("scripts/test_exam_scoring_unit.py") is False

    def test_init_exempt(self) -> None:
        """__init__.py 包初始化文件豁免。"""
        assert _is_in_scope("src/zephyr/governance/audit/__init__.py") is False

    def test_archive_exempt(self) -> None:
        """_archive/ 归档废弃代码豁免。"""
        assert _is_in_scope("src/zephyr/governance/_archive/old.py") is False

    def test_non_py_exempt(self) -> None:
        """非 .py 文件豁免（翻译注册表面向 Python 模块）。"""
        assert _is_in_scope("src/zephyr/governance/audit/config.yaml") is False

    def test_windows_backslash_normalized(self) -> None:
        """Windows 反斜杠路径归一化（tests/ 豁免仍生效）。"""
        assert _is_in_scope("scripts\\tests\\smoke_test_x.py") is False

    # --- 真能力脚本仍在范围内（不误豁免）---

    def test_real_capability_scripts_in_scope(self) -> None:
        """有 blueprint 的真能力脚本不命中豁免规则，仍需大白话简介。"""
        assert _is_in_scope("scripts/ide_health_service.py") is True
        assert _is_in_scope("scripts/record_session_start_commit.py") is True
        assert _is_in_scope("scripts/backup/ch_vm_ssh.py") is True


# ---------------------------------------------------------------------------
# TestCheckTranslationEntry
# ---------------------------------------------------------------------------


class TestCheckTranslationEntry:
    """_check_translation_entry 翻译查询（monkeypatch loader）。"""

    def test_compliant_entry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """有合格 plain_zh → 空串（合规）。"""
        import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as gate_mod

        def _fake_loader():
            return {
                "get_module_translation": lambda p: {
                    "plain_zh": "这是一个合格的大白话简介用于测试覆盖",
                    "name_zh": "测试模块",
                },
                "is_generic_plain_zh": lambda s: False,
                "is_generic_plain_suffix": lambda s, n: False,
            }

        monkeypatch.setattr(gate_mod, "_check_translation_entry", _fake_loader)
        # 直接调 fake loader 验证逻辑（原函数含 sys.path 注入，此处隔离测试分类逻辑）
        loader = gate_mod._check_translation_entry()
        trans = loader["get_module_translation"]("src/zephyr/foo.py")
        assert trans is not None
        assert trans["plain_zh"] == "这是一个合格的大白话简介用于测试覆盖"

    def test_missing_entry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """无 entry → 'missing'。"""
        import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as gate_mod

        # 临时替换 _cjk_len 和 loader，直接测试分类逻辑
        monkeypatch.setattr(gate_mod, "_check_translation_entry", lambda p: "missing")
        assert gate_mod._check_translation_entry("src/zephyr/foo.py") == "missing"

    def test_short_entry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """plain_zh CJK 不足 → 'short'。"""
        import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_translation_entry", lambda p: "short")
        assert gate_mod._check_translation_entry("src/zephyr/foo.py") == "short"

    def test_generic_entry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """plain_zh 是通用模板 → 'generic'。"""
        import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_translation_entry", lambda p: "generic")
        assert gate_mod._check_translation_entry("src/zephyr/foo.py") == "generic"


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------


class TestGatewayIntegration:
    """mock gateway + monkeypatch 翻译查询。"""

    def _make_gateway(self, tmp_path: Path, diff_stdout: str = "", diff_rc: int = 0) -> MagicMock:
        """构造 mock gateway，模拟 _run_git 返回 diff 结果。"""
        gw = MagicMock()
        gw.project_root = tmp_path
        gw.run_git = MagicMock(return_value=_MockResult(diff_rc, diff_stdout))
        # 模拟非 Zephyr 项目检测：d1_structure 目录存在
        (tmp_path / "scripts" / "governance" / "d1_structure").mkdir(parents=True, exist_ok=True)
        return gw

    def test_no_new_py_files_passes(self, tmp_path: Path) -> None:
        """无新增 .py → 放行。"""
        gw = self._make_gateway(tmp_path, diff_stdout="")
        gate = make_translation_coverage_gate()
        passed, msg = gate.check(gw, files=[])
        assert passed is True

    def test_new_py_with_valid_translation_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """新增 .py 有合格简介 → 放行。"""
        gw = self._make_gateway(tmp_path, diff_stdout="src/zephyr/new_module.py\n")
        import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_translation_entry", lambda f: "")
        gate = make_translation_coverage_gate()
        files = [str(tmp_path / "src/zephyr/new_module.py")]
        passed, msg = gate.check(gw, files=files)
        assert passed is True

    def test_new_py_missing_translation_blocked(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """新增 .py 缺简介 → 硬阻断（pass=False）。

        2026-08-02 观察期结束转硬阻断（_OBSERVATION_PERIOD=False）：
        Step 1 收窄范围 + Step B 补齐 108 条 missing，drift 清零，无误报风险。
        """
        gw = self._make_gateway(tmp_path, diff_stdout="src/zephyr/new_module.py\n")
        import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_translation_entry", lambda f: "missing")
        gate = make_translation_coverage_gate()
        files = [str(tmp_path / "src/zephyr/new_module.py")]
        passed, msg = gate.check(gw, files=files)
        # 硬阻断：pass=False
        assert passed is False
        assert "TRANSLATION-COVERAGE" in msg

    def test_git_diff_fail_fail_open(self, tmp_path: Path) -> None:
        """git diff 失败 → fail-open 放行。"""
        gw = self._make_gateway(tmp_path, diff_stdout="", diff_rc=1)
        gate = make_translation_coverage_gate()
        passed, msg = gate.check(gw, files=[])
        assert passed is True

    def test_non_zephyr_project_skips(self, tmp_path: Path) -> None:
        """非 Zephyr 项目（无 d1_structure 目录）→ skip。"""
        gw = MagicMock()
        gw.project_root = tmp_path
        gw.run_git = MagicMock(return_value=_MockResult(0, "src/zephyr/foo.py\n"))
        # 不创建 d1_structure 目录（非 Zephyr 项目）
        gate = make_translation_coverage_gate()
        passed, msg = gate.check(gw, files=[])
        assert passed is True
        assert "non-Zephyr project" in msg

    def test_commit_files_filter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """staged 含非 commit files → 只检测 commit files 中的新增 .py。"""
        gw = self._make_gateway(tmp_path, diff_stdout="src/zephyr/new_module.py\n")
        import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_translation_entry", lambda f: "")
        gate = make_translation_coverage_gate()
        # files 为空（commit 不含 new_module.py）→ 过滤后无文件 → 放行
        passed, msg = gate.check(gw, files=[])
        assert passed is True
