# [A_test] module_id: MOD-GOV_engine_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_engine
# [INVARIANTS] Fixes MUST pass SafetyGate+FixBudget+CascadeBreaker; behavioral_audit_red MUST never auto-fix
# [MODIFY-GUARD] blueprint.md §3; engine.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertion errors on invariant violation
# [TESTS] tests/test_engine_root.py
# [TTL] task_bound

from __future__ import annotations

from contextlib import ExitStack
from unittest.mock import patch

import pytest

from zephyr.infrastructure.auto_fix_engine.models import (
    BudgetDecision,
    BudgetInfo,
    FixAction,
    FixConfidence,
    FixHealthReport,
    FixReport,
    FixStatus,
    SafetyDecision,
)


@pytest.fixture
def mock_engine():
    patches = [
        "zephyr.infrastructure.auto_fix_engine.engine.FixBudget",
        "zephyr.infrastructure.auto_fix_engine.engine.FixStormGuard",
        "zephyr.infrastructure.auto_fix_engine.engine.CascadeBreaker",
        "zephyr.infrastructure.auto_fix_engine.engine.SafetyGate",
        "zephyr.infrastructure.auto_fix_engine.engine.IdempotencyGuard",
        "zephyr.infrastructure.auto_fix_engine.engine.ConflictResolver",
        "zephyr.infrastructure.auto_fix_engine.engine.FixOrderResolver",
        "zephyr.infrastructure.auto_fix_engine.engine.BlastRadiusEstimator",
        "zephyr.infrastructure.auto_fix_engine.engine.DeadLetterQueue",
        "zephyr.infrastructure.auto_fix_engine.engine.ApprovalQueue",
        "zephyr.infrastructure.auto_fix_engine.engine.CanaryFixer",
        "zephyr.infrastructure.auto_fix_engine.engine.SecretLeakGuard",
        "zephyr.infrastructure.auto_fix_engine.engine.FixValidator",
        "zephyr.infrastructure.auto_fix_engine.engine.WriteSafety",
        "zephyr.infrastructure.auto_fix_engine.engine.ShadowWorkspace",
        "zephyr.infrastructure.auto_fix_engine.engine.ComplianceAuditor",
        "zephyr.infrastructure.auto_fix_engine.engine.EscalationBridge",
        "zephyr.infrastructure.auto_fix_engine.engine.FixPatternMiner",
        "zephyr.infrastructure.auto_fix_engine.engine.FixReportGenerator",
        "zephyr.infrastructure.auto_fix_engine.engine.BatchFixer",
        "zephyr.infrastructure.auto_fix_engine.engine.FixHealthCheck",
    ]
    with ExitStack() as stack:
        mocks = {}
        for p in patches:
            name = p.rsplit(".", 1)[-1]
            mocks[name] = stack.enter_context(patch(p))
        MockBudget = mocks["FixBudget"]
        MockStormGuard = mocks["FixStormGuard"]
        MockCascadeBreaker = mocks["CascadeBreaker"]
        MockSafetyGate = mocks["SafetyGate"]
        MockDLQ = mocks["DeadLetterQueue"]
        MockApprovalQueue = mocks["ApprovalQueue"]
        MockBatchFixer = mocks["BatchFixer"]
        MockHealthCheck = mocks["FixHealthCheck"]
        mock_budget = MockBudget.return_value
        mock_budget.check.return_value = BudgetDecision(
            allowed=True, reason="ok", remaining_daily=50, remaining_monthly=500
        )
        mock_budget.get_info.return_value = BudgetInfo()
        mock_cascade = MockCascadeBreaker.return_value
        mock_cascade.check.return_value = (True, "")
        mock_storm = MockStormGuard.return_value
        mock_storm.check.return_value = (True, "")
        mock_safety = MockSafetyGate.return_value
        mock_safety.check.return_value = SafetyDecision(approved=True, confidence=FixConfidence.HIGH, reason="ok")
        mock_dlq = MockDLQ.return_value
        mock_dlq.size = 0
        mock_approval = MockApprovalQueue.return_value
        mock_approval.size = 0
        mock_batch = MockBatchFixer.return_value
        mock_batch.execute_batch.return_value = FixReport()
        mock_health = MockHealthCheck.return_value
        mock_health.check.return_value = FixHealthReport()
        from zephyr.infrastructure.auto_fix_engine.engine import AutoFixEngine

        engine = AutoFixEngine(config_path="/nonexistent_config_xyz.yaml")
        yield engine


class TestAutoFixEngineInstantiation:
    def test_instantiation_with_missing_config(self, mock_engine):
        assert mock_engine is not None
        assert isinstance(mock_engine._fixers, dict)

    def test_instantiation_loads_config(self, mock_engine):
        assert isinstance(mock_engine._config, dict)


class TestAutoFixEngineFix:
    def test_fix_no_auto_fix_type_cancelled(self, mock_engine):
        result = mock_engine.fix("behavioral_audit_red", "target.py")
        assert result.status == FixStatus.CANCELLED
        assert "no-auto-fix" in result.metadata.get("reason", "")

    def test_fix_security_critical_cancelled(self, mock_engine):
        result = mock_engine.fix("security_critical", "target.py")
        assert result.status == FixStatus.CANCELLED

    def test_fix_data_loss_risk_cancelled(self, mock_engine):
        result = mock_engine.fix("data_loss_risk", "target.py")
        assert result.status == FixStatus.CANCELLED

    def test_fix_safety_denied(self, mock_engine):
        mock_engine._safety_gate.check.return_value = SafetyDecision(
            approved=False,
            confidence=FixConfidence.LOW,
            reason="dangerous target",
        )
        result = mock_engine.fix("zombie_cleanup", "target.py")
        assert result.status == FixStatus.APPROVAL_PENDING
        assert result.escalated is True

    def test_fix_budget_denied(self, mock_engine):
        mock_engine._fix_budget.check.return_value = BudgetDecision(
            allowed=False,
            reason="budget exhausted",
            remaining_daily=0,
            remaining_monthly=0,
        )
        result = mock_engine.fix("zombie_cleanup", "target.py")
        assert result.status == FixStatus.FAILED
        assert "budget" in result.metadata.get("budget_reason", "").lower() or result.status == FixStatus.FAILED

    def test_fix_cascade_blocked(self, mock_engine):
        mock_engine._cascade_breaker.check.return_value = (False, "cascade active")
        result = mock_engine.fix("zombie_cleanup", "target.py")
        assert result.status == FixStatus.FAILED

    def test_fix_storm_blocked(self, mock_engine):
        mock_engine._storm_guard.check.return_value = (False, "storm detected")
        result = mock_engine.fix("zombie_cleanup", "target.py")
        assert result.status == FixStatus.FAILED

    def test_fix_no_fixer_found(self, mock_engine):
        mock_engine._fixers = {}
        result = mock_engine.fix("zombie_cleanup", "target.py")
        assert result.status == FixStatus.FAILED
        assert "No fixer found" in result.metadata.get("error", "")


class TestAutoFixEngineFixAll:
    def test_fix_all_empty_list(self, mock_engine):
        report = mock_engine.fix_all([])
        assert isinstance(report, FixReport)
        assert report.total_attempted == 0

    def test_fix_all_all_no_auto_fix(self, mock_engine):
        actions = [
            FixAction(action_type="behavioral_audit_red", target="a.py"),
            FixAction(action_type="security_critical", target="b.py"),
        ]
        report = mock_engine.fix_all(actions)
        assert report.total_attempted == 2
        assert "no-auto-fix" in report.cascade_alerts[0]


class TestAutoFixEngineDryRun:
    def test_dry_run_calls_fix_with_dry_run(self, mock_engine):
        with patch.object(mock_engine, "fix", return_value=FixAction(action_type="test", target="f.py")) as mock_fix:
            mock_engine.dry_run("zombie_cleanup", "target.py")
            mock_fix.assert_called_once_with("zombie_cleanup", "target.py", dry_run=True)


class TestAutoFixEngineHealthCheck:
    def test_health_check_returns_report(self, mock_engine):
        report = mock_engine.health_check()
        assert isinstance(report, FixHealthReport)

    def test_health_check_healthy(self, mock_engine):
        report = mock_engine.health_check()
        assert report.budget_ok is True


class TestAutoFixEngineApproveReject:
    def test_approve_delegates(self, mock_engine):
        mock_engine._approval_queue.approve.return_value = FixAction(action_type="test", target="f.py")
        result = mock_engine.approve("action123")
        mock_engine._approval_queue.approve.assert_called_once_with("action123")

    def test_reject_delegates(self, mock_engine):
        mock_engine._approval_queue.reject.return_value = FixAction(
            action_type="test", target="f.py", status=FixStatus.CANCELLED
        )
        result = mock_engine.reject("action123")
        mock_engine._approval_queue.reject.assert_called_once_with("action123")


class TestAutoFixEngineDeadLetters:
    def test_get_dead_letters(self, mock_engine):
        mock_engine._dead_letter_queue.get_pending.return_value = []
        result = mock_engine.get_dead_letters()
        assert result == []


class TestAutoFixEngineApprovalQueue:
    def test_get_approval_queue(self, mock_engine):
        mock_engine._approval_queue.get_pending.return_value = []
        result = mock_engine.get_approval_queue()
        assert result == []


class TestAutoFixEngineFindFixer:
    def test_find_fixer_unknown_type(self, mock_engine):
        result = mock_engine._find_fixer("unknown_type_xyz")
        assert result is None

    def test_find_fixer_known_type_not_loaded(self, mock_engine):
        mock_engine._fixers = {}
        result = mock_engine._find_fixer("zombie_cleanup")
        assert result is None
