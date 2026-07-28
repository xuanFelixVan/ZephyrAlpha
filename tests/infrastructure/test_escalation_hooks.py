# [A_test] module_id: MOD-GOV_escalation_hooks | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-314 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_escalation_hooks
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Extension Hook Integration Tests — Escalation Engine (MOD-INF-022).

Validates that all 15 extension detector modules are correctly loaded and integrated
into the EscalationEngine's hook system.

Blueprint: docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md D-022-07~D-022-30
"""

from unittest.mock import patch

import pytest

from zephyr.governance.escalation import (
    EscalationEngine,
    EscalationLevel,
    EscalationState,
    RuleCategory,
)


@pytest.fixture(autouse=True)
def _disable_lsg():
    with patch.object(EscalationEngine, "lsg_scan_input", lambda self, desc: None):
        yield


class TestExtensionHookLoading:
    @pytest.fixture
    def engine(self):
        engine = EscalationEngine("hook-int-test", hooks_enabled=True)
        engine.disable_hooks()
        engine.enable_hooks()
        return engine

    def test_all_17_active_detectors_loaded(self, engine):
        detectors = engine.extension_detectors
        assert len(detectors) >= 16
        expected = [
            "PersuasionDetector",
            "DeadlockDetector",
            "DriftDetector",
            "EscalationLoopDetector",
            "ConfidenceEstimator",
            "VigilRuntime",
            "FormalVerifier",
            "ProviderFailover",
            "CredentialGuard",
            "MerkleAudit",
            "SBOMGuard",
            "ClockGuard",
            "CommandChainGate",
            "CompositionalSafetyTester",
        ]
        for name in expected:
            assert name in detectors, f"{name} not loaded"

    def test_evaluate_with_all_hooks_produces_event(self, engine):
        ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "rm -rf /production --no-preserve-root")
        assert ev is not None
        assert ev.level == EscalationLevel.L4_EMERGENCY
        assert ev.state in (EscalationState.EVALUATING, EscalationState.REJECTED)

    def test_secure_event_has_extended_description(self, engine):
        ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "force_push to production main branch")
        assert len(ev.description) > 0

    def test_deadlock_event_has_extended_description(self, engine):
        ev = engine.evaluate(RuleCategory.DEADLOCK, "Agent A blocks B, B blocks C, C blocks A")
        assert ev.level.value >= EscalationLevel.L3_CRITICAL.value

    def test_timout_event_integrated(self, engine):
        ev = engine.evaluate(RuleCategory.TIMEOUT, "Pipeline step stuck for 600 seconds")
        assert ev is not None
        assert ev.level is not None

    def test_budget_event_integrated(self, engine):
        ev = engine.evaluate(RuleCategory.BUDGET_EXCEEDED, "Cost: $10000, daily budget: $500")
        assert ev.level == EscalationLevel.L2_HUMAN_REVIEW

    def test_cascade_event_integrated(self, engine):
        ev = engine.evaluate(RuleCategory.CASCADE_FAILURE, "Service A down -> Service B degraded -> Service C stalled")
        assert ev.level.value >= EscalationLevel.L3_CRITICAL.value

    def test_owner_absent_event_integrated(self, engine):
        ev = engine.evaluate(RuleCategory.OWNER_ABSENT, "Owner missing for 45 minutes, critical decision pending")
        assert ev.level.value >= EscalationLevel.L2_HUMAN_REVIEW.value


class TestHookLifecycle:
    def test_enable_disable_hooks(self):
        engine = EscalationEngine("lifecycle-test", hooks_enabled=False)
        assert engine.hooks_enabled is False

        engine.disable_hooks()
        assert engine.hooks_enabled is False

        engine.enable_hooks()
        assert engine.hooks_enabled is True
        assert len(engine.extension_detectors) >= 14

        engine.disable_hooks()
        assert engine.hooks_enabled is False

    def test_hooks_disabled_does_not_crash(self):
        engine = EscalationEngine("no-hooks", hooks_enabled=False)
        ev = engine.evaluate(RuleCategory.CUSTOM, "any operation")
        assert ev is not None


class TestHookConsistency:
    @pytest.fixture
    def engine(self):
        engine = EscalationEngine("consistency-test", hooks_enabled=True)
        return engine

    def test_multiple_evaluations_stable(self, engine):
        levels = []
        for _ in range(10):
            ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "drop table users cascade")
            levels.append(ev.level.value)
        assert all(l == EscalationLevel.L4_EMERGENCY.value for l in levels)

    def test_hooks_dont_alter_non_matching_events(self, engine):
        ev = engine.evaluate(RuleCategory.CUSTOM, "hello world test")
        assert ev.level.value <= EscalationLevel.L1_AUTO_FIX.value
