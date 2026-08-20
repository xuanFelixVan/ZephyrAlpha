# [A_test] module_id: SRC-TST-2701 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER | docs/03_modules/_domain_governance/blueprint.md | §runtime-violation-snapshot-reconciler
# [MODULE] tests.governance.audit.test_runtime_violation_snapshot_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_runtime_violation_snapshot_reconciler.py — reconciler 单测

#ARCH-GOV-CONVERGENCE-META Phase 3.4b（病根1 治本）

测试 make_runtime_violation_snapshot_reconciler 工厂函数：
- factory 返回正确 ReconcilerSpec（gate_id, priority, callables）
- trigger 逻辑：src/zephyr/*.py 触发、trae_060 yaml 触发、其他不触发
- reconcile 成功：返回 clean + 保存 snapshot
- reconcile 失败：返回 warn（不抛异常）

测试隔离：用 tmp_path + mock，不触碰生产 data/ 目录或真实 git 仓库。
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec  # noqa: E402
from zephyr.governance.audit.runtime_violation_snapshot_reconciler import (  # noqa: E402
    _GATE_ID,
    _PRIORITY,
    _matches_trigger,
    make_runtime_violation_snapshot_reconciler,
)


class _FakeGateway:
    """模拟 GitCommitGateway，仅提供 project_root / _run_git。"""

    def __init__(self, project_root: Path, head_sha: str = "abc1234567"):
        self.project_root = project_root
        self._head_sha = head_sha

    def run_git(self, cmd: list[str]):
        mock = MagicMock()
        mock.returncode = 0
        mock.stderr = ""
        if "rev-parse" in cmd and "HEAD" in cmd:
            mock.stdout = self._head_sha
        else:
            mock.stdout = ""
        return mock

    def _run_git(self, cmd: list[str]):
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.run_git(cmd)


class TestFactorySpec:
    """make_runtime_violation_snapshot_reconciler 工厂返回值测试。"""

    def test_factory_returns_spec(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        assert isinstance(spec, ReconcilerSpec)

    def test_factory_gate_id(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        assert spec.gate_id == _GATE_ID
        assert spec.gate_id == "GATE-RUNTIME-VIOLATION-SNAPSHOT"

    def test_factory_priority(self, tmp_path):
        """priority=850（晚于业务 reconciler，早于 remediation_progress=900）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        assert spec.priority == _PRIORITY
        assert spec.priority == 850

    def test_factory_callables(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        assert callable(spec.trigger)
        assert callable(spec.reconcile)


class TestMatchesTrigger:
    """_matches_trigger 函数测试。"""

    def test_src_zephyr_py_triggers(self):
        assert _matches_trigger("src/zephyr/governance/audit/foo.py") is True

    def test_scripts_governance_py_triggers(self):
        assert _matches_trigger("scripts/governance/d3_metadata/check.py") is True

    def test_trae_060_yaml_triggers(self):
        assert _matches_trigger("docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml") is True

    def test_other_yaml_does_not_trigger(self):
        assert _matches_trigger("docs/01_policies_and_standards/rules/trae_057.yaml") is False

    def test_docs_md_does_not_trigger(self):
        assert _matches_trigger("docs/02_enterprise_architecture/foo.md") is False

    def test_root_py_does_not_trigger(self):
        assert _matches_trigger("setup.py") is False

    def test_tests_py_does_not_trigger(self):
        assert _matches_trigger("tests/governance/test_foo.py") is False


class TestTrigger:
    """trigger 函数测试。"""

    def test_trigger_with_src_py(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        assert spec.trigger(files) is True

    def test_trigger_with_trae_060_yaml(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        files = [str(tmp_path / "docs" / "01_policies_and_standards" / "rules" / "trae_060_inward_consolidation.yaml")]
        assert spec.trigger(files) is True

    def test_trigger_empty_files(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        assert spec.trigger([]) is False

    def test_trigger_non_matching_files(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        files = [str(tmp_path / "README.md"), str(tmp_path / "setup.py")]
        assert spec.trigger(files) is False


class TestReconcile:
    """reconcile 函数测试。"""

    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.generate_snapshot")
    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.save_snapshot")
    def test_reconcile_success_returns_clean(self, mock_save, mock_gen, tmp_path):
        """reconcile 成功返回 action='clean'。"""
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        mock_gen.return_value = {
            "summary": {"drift_count": 2, "total_detected": 5, "total_claimed": 109},
        }
        mock_save.return_value = tmp_path / "latest.json"

        result = spec.reconcile([], "test-session")

        assert result.action == "clean"
        assert result.gate_id == _GATE_ID
        assert "drift_count=2" in result.detail
        assert "detected=5" in result.detail

    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.generate_snapshot")
    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.save_snapshot")
    def test_reconcile_failure_returns_warn(self, mock_save, mock_gen, tmp_path):
        """generate_snapshot 抛异常时返回 action='warn'。"""
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        mock_gen.side_effect = RuntimeError("boom")

        result = spec.reconcile([], "test-session")

        assert result.action == "warn"
        assert result.gate_id == _GATE_ID
        assert "boom" in result.detail

    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.generate_snapshot")
    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.save_snapshot")
    def test_reconcile_save_failure_returns_warn(self, mock_save, mock_gen, tmp_path):
        """save_snapshot 抛异常时返回 action='warn'。"""
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        mock_gen.return_value = {"summary": {"drift_count": 0, "total_detected": 0, "total_claimed": 0}}
        mock_save.side_effect = OSError("disk full")

        result = spec.reconcile([], "test-session")

        assert result.action == "warn"
        assert "disk full" in result.detail

    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.generate_snapshot")
    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.save_snapshot")
    def test_reconcile_never_raises(self, mock_save, mock_gen, tmp_path):
        """reconcile 永不抛异常（所有异常降级为 warn）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        mock_gen.side_effect = ValueError("unexpected")
        mock_save.side_effect = RuntimeError("should not reach")

        result = spec.reconcile([], "test-session")
        assert result.action == "warn"

    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.generate_snapshot")
    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.save_snapshot")
    def test_reconcile_includes_commit_sha(self, mock_save, mock_gen, tmp_path):
        """reconcile 从 gateway.run_git 获取 commit sha。"""
        gw = _FakeGateway(tmp_path, head_sha="deadbeef1234")
        spec = make_runtime_violation_snapshot_reconciler(gw)
        mock_gen.return_value = {"summary": {"drift_count": 0, "total_detected": 0, "total_claimed": 0}}
        mock_save.return_value = tmp_path / "latest.json"

        spec.reconcile([], "test-session")

        _, kwargs = mock_gen.call_args
        assert kwargs.get("commit_sha") == "deadbeef1234"[:12]

    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.generate_snapshot")
    @patch("zephyr.governance.audit.runtime_violation_snapshot_reconciler.save_snapshot")
    def test_reconcile_passes_session_id(self, mock_save, mock_gen, tmp_path):
        """reconcile 传递 session_id 到 generate_snapshot。"""
        gw = _FakeGateway(tmp_path)
        spec = make_runtime_violation_snapshot_reconciler(gw)
        mock_gen.return_value = {"summary": {"drift_count": 0, "total_detected": 0, "total_claimed": 0}}
        mock_save.return_value = tmp_path / "latest.json"

        spec.reconcile([], "my-session-123")

        _, kwargs = mock_gen.call_args
        assert kwargs.get("session_id") == "my-session-123"
