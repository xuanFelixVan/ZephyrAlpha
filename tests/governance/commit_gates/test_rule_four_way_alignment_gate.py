# [A_test] module_id: SRC-TST-2225 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-rule_four_way_alignment_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_rule_four_way_alignment_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_rule_four_way_alignment_gate.py — RULE-FOUR-WAY-ALIGN 门禁单测

权威依据：rule_four_way_alignment_gate.py（make_rule_four_way_alignment_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestTriggerLogic: _should_trigger 触发判定
  （规则文件 .yaml/.yml/.md 触发 / catalog 触发 / .py 不触发 /
   不存在文件跳过 / tests/ 豁免 / 无关路径不触发）
- TestGatewayIntegration: mock gateway 流程
  - exit0 放行 / exit1 阻断 / exit2 fail-open / 超时 fail-open / 异常 fail-open
  - checker 缺失 → fail-open
  - 无触发文件 → 跳过放行
  - worktree toplevel 失败 → 回退 project_root

注意：rule_four_way_alignment_gate 是 thin wrapper，检测逻辑真源在
check_rule_four_way_alignment.py（subprocess 调用 --ci）。本测试 mock
subprocess.run，不调用真实脚本；用 tmp_path 创建真实文件使 _should_trigger
的 os.path.isfile 与 checker_path.is_file() 通过。触发条件=staged 文件含
docs/01_policies_and_standards/ 下规则文件或 rule_catalog_registry.yaml。

测试隔离：MagicMock 模拟 gateway._run_git + monkeypatch subprocess.run，不读/不写真实仓库。
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.rule_four_way_alignment_gate import (  # noqa: E402
    _CHECKER_REL,
    _should_trigger,
    make_rule_four_way_alignment_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


@dataclass
class _SubResult:
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


def _make_gateway(project_root, toplevel=None, toplevel_fails=False):
    """构造 mock gateway：project_root 必须是 Path（gate 用 project_root / _CHECKER_REL）；
    git rev-parse --show-toplevel 返回 worktree root。"""
    gw = MagicMock()
    gw.project_root = project_root

    def _run_git(cmd):
        cmd_str = " ".join(cmd)
        if "rev-parse" in cmd_str and "--show-toplevel" in cmd_str:
            if toplevel_fails:
                return _MockResult(1, "")
            return _MockResult(0, toplevel or str(project_root))
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


def _create_file(tmp_path, rel):
    """在 tmp_path 下创建真实文件，返回绝对路径。"""
    fpath = tmp_path.joinpath(*rel.split("/"))
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text("# dummy\n", encoding="utf-8")
    return str(fpath)


def _create_checker(tmp_path):
    """在 tmp_path 下创建 dummy checker 脚本（使 checker_path.is_file() 通过）。"""
    checker = tmp_path / _CHECKER_REL
    checker.parent.mkdir(parents=True, exist_ok=True)
    checker.write_text("# dummy checker\n", encoding="utf-8")


def _patch_subprocess(monkeypatch, result=None, raises=None):
    """patch subprocess.run：返回固定 result 或抛指定异常。"""
    if raises is not None:
        def _raise(*a, **k):
            raise raises
        monkeypatch.setattr(subprocess, "run", _raise)
    else:
        res = result or _SubResult(0, "", "")
        monkeypatch.setattr(subprocess, "run", lambda *a, **k: res)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_rule_four_way_alignment_gate(), GateSpec)

    def test_gate_id(self):
        assert make_rule_four_way_alignment_gate().gate_id == "RULE-FOUR-WAY-ALIGN"

    def test_priority(self):
        assert make_rule_four_way_alignment_gate().priority == 76


# ---------------------------------------------------------------------------
# TestTriggerLogic — _should_trigger 触发判定
# ---------------------------------------------------------------------------
class TestTriggerLogic:
    def test_yaml_rule_file_triggers(self, tmp_path):
        rel = "docs/01_policies_and_standards/rules/foo.yaml"
        f = _create_file(tmp_path, rel)
        triggered, reason = _should_trigger([f], tmp_path)
        assert triggered
        assert "规则文件变更" in reason

    def test_catalog_registry_triggers(self, tmp_path):
        rel = "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml"
        f = _create_file(tmp_path, rel)
        triggered, reason = _should_trigger([f], tmp_path)
        assert triggered
        assert "catalog 变更" in reason

    def test_yml_rule_file_triggers(self, tmp_path):
        rel = "docs/01_policies_and_standards/rules/bar.yml"
        f = _create_file(tmp_path, rel)
        triggered, reason = _should_trigger([f], tmp_path)
        assert triggered

    def test_md_rule_file_triggers(self, tmp_path):
        rel = "docs/01_policies_and_standards/rules/baz.md"
        f = _create_file(tmp_path, rel)
        triggered, reason = _should_trigger([f], tmp_path)
        assert triggered

    def test_py_file_does_not_trigger(self, tmp_path):
        rel = "src/zephyr/trading/mod.py"
        f = _create_file(tmp_path, rel)
        triggered, reason = _should_trigger([f], tmp_path)
        assert not triggered

    def test_nonexistent_file_skipped(self, tmp_path):
        # deletion commit：文件不存在 → 跳过
        f = str(tmp_path / "docs/01_policies_and_standards/rules/deleted.yaml")
        triggered, reason = _should_trigger([f], tmp_path)
        assert not triggered

    def test_tests_dir_exempt_no_trigger(self, tmp_path):
        rel = "tests/governance/test_rule.yaml"
        f = _create_file(tmp_path, rel)
        triggered, reason = _should_trigger([f], tmp_path)
        assert not triggered  # tests/ 豁免

    def test_unrelated_path_does_not_trigger(self, tmp_path):
        rel = "src/zephyr/some_other.yaml"
        f = _create_file(tmp_path, rel)
        triggered, reason = _should_trigger([f], tmp_path)
        assert not triggered  # 不在 docs/01_policies_and_standards/ 下


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_exit_zero_passes(self, tmp_path, monkeypatch):
        _create_checker(tmp_path)
        f = _create_file(tmp_path, "docs/01_policies_and_standards/rules/foo.yaml")
        _patch_subprocess(monkeypatch, _SubResult(0, "", ""))
        gw = _make_gateway(tmp_path, toplevel=str(tmp_path))
        passed, msg = make_rule_four_way_alignment_gate().check(gw, [f])
        assert passed
        assert msg == ""

    def test_exit_one_blocks(self, tmp_path, monkeypatch):
        _create_checker(tmp_path)
        f = _create_file(tmp_path, "docs/01_policies_and_standards/rules/foo.yaml")
        _patch_subprocess(monkeypatch, _SubResult(1, "YAML/Catalog mismatch\n", ""))
        gw = _make_gateway(tmp_path, toplevel=str(tmp_path))
        passed, msg = make_rule_four_way_alignment_gate().check(gw, [f])
        assert not passed
        assert "RULE_FOUR_WAY_ALIGN_VIOLATION" in msg
        assert "触发原因" in msg

    def test_exit_two_fail_open(self, tmp_path, monkeypatch):
        _create_checker(tmp_path)
        f = _create_file(tmp_path, "docs/01_policies_and_standards/rules/foo.yaml")
        _patch_subprocess(monkeypatch, _SubResult(2, "", "checker error"))
        gw = _make_gateway(tmp_path, toplevel=str(tmp_path))
        passed, msg = make_rule_four_way_alignment_gate().check(gw, [f])
        assert passed  # 脚本异常 fail-open
        assert msg == ""

    def test_timeout_fail_open(self, tmp_path, monkeypatch):
        _create_checker(tmp_path)
        f = _create_file(tmp_path, "docs/01_policies_and_standards/rules/foo.yaml")
        _patch_subprocess(
            monkeypatch,
            raises=subprocess.TimeoutExpired(cmd=["x"], timeout=30),
        )
        gw = _make_gateway(tmp_path, toplevel=str(tmp_path))
        passed, msg = make_rule_four_way_alignment_gate().check(gw, [f])
        assert passed
        assert msg == ""

    def test_subprocess_exception_fail_open(self, tmp_path, monkeypatch):
        _create_checker(tmp_path)
        f = _create_file(tmp_path, "docs/01_policies_and_standards/rules/foo.yaml")
        _patch_subprocess(monkeypatch, raises=OSError("boom"))
        gw = _make_gateway(tmp_path, toplevel=str(tmp_path))
        passed, msg = make_rule_four_way_alignment_gate().check(gw, [f])
        assert passed
        assert msg == ""

    def test_checker_missing_fail_open(self, tmp_path, monkeypatch):
        # 不创建 checker → checker_path.is_file() False → fail-open
        f = _create_file(tmp_path, "docs/01_policies_and_standards/rules/foo.yaml")
        _patch_subprocess(monkeypatch, _SubResult(1, "violation\n", ""))
        gw = _make_gateway(tmp_path, toplevel=str(tmp_path))
        passed, msg = make_rule_four_way_alignment_gate().check(gw, [f])
        assert passed
        assert msg == ""

    def test_no_trigger_files_skipped(self, tmp_path, monkeypatch):
        _create_checker(tmp_path)
        # .py 文件不触发 → 跳过，subprocess 不应被调用
        f = _create_file(tmp_path, "src/zephyr/trading/mod.py")
        called = {"n": 0}

        def _spy(*a, **k):
            called["n"] += 1
            return _SubResult(1, "should not happen\n", "")
        monkeypatch.setattr(subprocess, "run", _spy)
        gw = _make_gateway(tmp_path, toplevel=str(tmp_path))
        passed, msg = make_rule_four_way_alignment_gate().check(gw, [f])
        assert passed
        assert msg == ""
        assert called["n"] == 0  # 未触发检测

    def test_toplevel_failure_fallback_to_project_root(self, tmp_path, monkeypatch):
        _create_checker(tmp_path)
        f = _create_file(tmp_path, "docs/01_policies_and_standards/rules/foo.yaml")
        _patch_subprocess(monkeypatch, _SubResult(0, "", ""))
        # toplevel 解析失败 → 回退 project_root，subprocess 仍正常执行
        gw = _make_gateway(tmp_path, toplevel_fails=True)
        passed, msg = make_rule_four_way_alignment_gate().check(gw, [f])
        assert passed
        assert msg == ""
