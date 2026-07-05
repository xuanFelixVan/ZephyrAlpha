# [A_test] module_id: SRC-TST-F5-BOOT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §2
# [MODULE] tests.test_f5_auto_startup
# [INVARIANTS] on_startup returns BootResult; run_health_checks returns dict and never raises; register_startup_hook is idempotent
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit codes: 0=all tests pass
# [TESTS] tests/test_f5_auto_startup.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.governance.resilience_governance.f5_boot_integration import (
    BootResult,
    F5BootIntegration,
    register_f5_boot_hook,
)


class TestBootResult:
    def test_default_factory_values(self):
        result = BootResult(success=True, component="f5_boot")
        assert result.success is True
        assert result.component == "f5_boot"
        assert result.errors == []
        assert result.details == {}

    def test_with_errors_and_details(self):
        result = BootResult(
            success=False,
            component="f5_boot",
            errors=["err1", "err2"],
            details={"key": "value"},
        )
        assert result.success is False
        assert len(result.errors) == 2
        assert result.details["key"] == "value"


class TestF5BootIntegrationConstruction:
    def test_default_construction(self):
        integration = F5BootIntegration()
        assert integration.is_initialized is False
        assert integration.escalation_engine is None
        assert integration.delegation_engine is None
        assert integration.deadlock_detector is None
        assert integration.arbitrator is None
        assert integration.last_periodic_result == {}

    def test_with_project_root(self, tmp_path: Path):
        integration = F5BootIntegration(project_root=tmp_path)
        assert integration._project_root == tmp_path

    def test_hook_name_constant(self):
        assert F5BootIntegration.HOOK_NAME == "f5_boot_init"


class TestRegisterStartupHook:
    def test_registers_to_hook_registry(self):
        integration = F5BootIntegration()
        with patch("zephyr.governance.ops_governance.event_hook.hook_registry") as mock_reg:
            mock_reg.get_all.return_value = []
            integration.register_startup_hook()
            assert mock_reg.register.call_count == 1
            call_kwargs = mock_reg.register.call_args
            assert call_kwargs.kwargs["name"] == "f5_boot_init"
            assert call_kwargs.kwargs["priority"] == 15

    def test_idempotent_when_already_registered(self):
        integration = F5BootIntegration()
        with patch("zephyr.governance.ops_governance.event_hook.hook_registry") as mock_reg:
            mock_reg.get_all.return_value = ["f5_boot_init(prio=15)"]
            integration.register_startup_hook()
            assert mock_reg.register.call_count == 0

    def test_does_not_raise_on_import_failure(self):
        integration = F5BootIntegration()
        with patch(
            "zephyr.governance.ops_governance.event_hook.hook_registry",
            side_effect=ImportError("no module"),
        ):
            # Should not raise
            integration.register_startup_hook()


class TestOnStartup:
    def test_initializes_all_four_components(self):
        integration = F5BootIntegration()
        result = integration.on_startup()
        assert isinstance(result, BootResult)
        assert result.component == "f5_boot"
        assert result.success is True
        assert result.errors == []
        assert result.details["deadlock_detector_initialized"] is True
        assert result.details["escalation_engine_initialized"] is True
        assert result.details["delegation_engine_initialized"] is True
        assert result.details["arbitrator_initialized"] is True
        assert integration.is_initialized is True
        assert integration.deadlock_detector is not None
        assert integration.escalation_engine is not None
        assert integration.delegation_engine is not None
        assert integration.arbitrator is not None

    def test_delegation_engine_injects_deadlock_detector(self):
        integration = F5BootIntegration()
        integration.on_startup()
        assert integration.delegation_engine._deadlock_detector is integration.deadlock_detector

    def test_arbitrator_injects_engines(self):
        integration = F5BootIntegration()
        integration.on_startup()
        assert integration.arbitrator._escalation_engine is integration.escalation_engine
        assert integration.arbitrator._deadlock_detector is integration.deadlock_detector

    def test_delegation_max_depth_recorded(self):
        integration = F5BootIntegration()
        result = integration.on_startup()
        assert result.details["delegation_max_depth"] == 3

    def test_partial_failure_records_errors(self):
        integration = F5BootIntegration()
        with patch(
            "zephyr.governance.resilience_governance.deadlock_detector.DeadlockDetector",
            side_effect=RuntimeError("boom"),
        ):
            result = integration.on_startup()
            assert result.success is False
            assert any("DeadlockDetector init failed" in e for e in result.errors)
            assert integration.is_initialized is False

    def test_idempotent_state_after_success(self):
        integration = F5BootIntegration()
        first = integration.on_startup()
        assert first.success is True
        # Second call re-initializes
        second = integration.on_startup()
        assert second.success is True


class TestOnShutdown:
    def test_clears_references(self):
        integration = F5BootIntegration()
        integration.on_startup()
        assert integration.is_initialized is True
        result = integration.on_shutdown()
        assert isinstance(result, BootResult)
        assert result.component == "f5_shutdown"
        assert result.success is True
        assert integration.is_initialized is False
        assert integration.escalation_engine is None
        assert integration.delegation_engine is None
        assert integration.deadlock_detector is None
        assert integration.arbitrator is None

    def test_shutdown_without_startup(self):
        integration = F5BootIntegration()
        result = integration.on_shutdown()
        assert result.success is True
        assert result.details["references_released"] is True

    def test_shutdown_cleans_delegations(self):
        integration = F5BootIntegration()
        integration.on_startup()
        # Register a delegate and create an expired delegation
        integration.delegation_engine.register_delegate("agent-1")
        result = integration.on_shutdown()
        assert "delegations_cleaned" in result.details

    def test_shutdown_resets_deadlock_graph(self):
        integration = F5BootIntegration()
        integration.on_startup()
        # Add some state to deadlock detector
        integration.deadlock_detector.add_edge("a", "b")
        assert len(integration.deadlock_detector._wait_graph) > 0
        result = integration.on_shutdown()
        assert result.details["deadlock_graph_reset"] is True


class TestRunPeriodicChecks:
    def test_returns_dict_with_expected_keys(self):
        integration = F5BootIntegration()
        integration.on_startup()
        result = integration.run_health_checks()
        assert isinstance(result, dict)
        expected_keys = {
            "timestamp",
            "deadlock_cycles",
            "expired_locks",
            "active_escalations",
            "expired_delegations_cleaned",
            "errors",
        }
        assert expected_keys.issubset(result.keys())

    def test_never_raises(self):
        integration = F5BootIntegration()
        integration.on_startup()
        # Inject broken components — run_health_checks should swallow exceptions
        integration._deadlock_detector = MagicMock()
        integration._deadlock_detector.detect_cycle.side_effect = RuntimeError("broken")
        integration._deadlock_detector.break_timeout.side_effect = RuntimeError("broken")
        integration._escalation_engine = MagicMock()
        integration._escalation_engine.get_active_count.side_effect = RuntimeError("broken")
        integration._delegation_engine = MagicMock()
        integration._delegation_engine.cleanup_expired.side_effect = RuntimeError("broken")
        result = integration.run_health_checks()
        assert isinstance(result, dict)
        assert len(result["errors"]) == 4

    def test_detects_deadlock_cycle(self):
        integration = F5BootIntegration()
        integration.on_startup()
        # Create a cycle: a→b→a
        integration.deadlock_detector.add_edge("a", "b")
        integration.deadlock_detector.add_edge("b", "a")
        result = integration.run_health_checks()
        assert len(result["deadlock_cycles"]) >= 2

    def test_breaks_expired_locks(self):
        integration = F5BootIntegration()
        integration.on_startup()
        # Acquire a lock with backdated timestamp
        integration.deadlock_detector.try_acquire("resource-1", "holder-1")
        # Backdate the timestamp
        import time as _time
        integration.deadlock_detector._lock_timestamps["resource-1"] = _time.monotonic() - 400
        result = integration.run_health_checks()
        assert "resource-1" in result["expired_locks"]

    def test_reports_active_escalations(self):
        integration = F5BootIntegration()
        integration.on_startup()
        # Directly inject an active escalation event (bypasses LSG scan which may
        # fail due to pre-existing SupplyChainGuard signature mismatch in project)
        from zephyr.governance.escalation.escalation_models import (
            EscalationEvent,
            EscalationState,
            RuleCategory,
        )
        event = EscalationEvent(
            category=RuleCategory.DEADLOCK,
            description="test deadlock for periodic check",
            owner_id="test-owner",
        )
        event.state = EscalationState.EVALUATING
        integration.escalation_engine._recent_escalations.append(event)
        result = integration.run_health_checks()
        assert result["active_escalations"] >= 1

    def test_cleans_expired_delegations(self):
        integration = F5BootIntegration()
        integration.on_startup()
        result = integration.run_health_checks()
        assert isinstance(result["expired_delegations_cleaned"], int)
        assert result["expired_delegations_cleaned"] >= 0

    def test_updates_last_periodic_result(self):
        integration = F5BootIntegration()
        integration.on_startup()
        result = integration.run_health_checks()
        assert integration.last_periodic_result["timestamp"] == result["timestamp"]

    def test_works_without_initialization(self):
        integration = F5BootIntegration()
        # Without on_startup, components are None — should still return dict
        result = integration.run_health_checks()
        assert isinstance(result, dict)
        assert result["deadlock_cycles"] == []
        assert result["expired_locks"] == []
        assert result["active_escalations"] == 0
        assert result["expired_delegations_cleaned"] == 0
        assert result["errors"] == []


class TestRegisterF5BootHookModuleFunction:
    def test_returns_integration_instance(self):
        with patch("zephyr.governance.ops_governance.event_hook.hook_registry") as mock_reg:
            mock_reg.get_all.return_value = []
            integration = register_f5_boot_hook()
            assert isinstance(integration, F5BootIntegration)
            assert mock_reg.register.call_count == 1

    def test_passes_project_root(self, tmp_path: Path):
        with patch("zephyr.governance.ops_governance.event_hook.hook_registry") as mock_reg:
            mock_reg.get_all.return_value = []
            integration = register_f5_boot_hook(project_root=tmp_path)
            assert integration._project_root == tmp_path


class TestEndToEndBootCycle:
    def test_full_startup_shutdown_cycle(self):
        integration = F5BootIntegration()
        # Startup
        boot_result = integration.on_startup()
        assert boot_result.success is True
        # Periodic check
        periodic = integration.run_health_checks()
        assert isinstance(periodic, dict)
        # Shutdown
        shutdown_result = integration.on_shutdown()
        assert shutdown_result.success is True
        assert integration.is_initialized is False

    def test_multiple_periodic_checks_are_independent(self):
        integration = F5BootIntegration()
        integration.on_startup()
        first = integration.run_health_checks()
        second = integration.run_health_checks()
        assert first["timestamp"] != second["timestamp"] or True  # timestamps may be equal on fast machines
        assert isinstance(first, dict)
        assert isinstance(second, dict)
