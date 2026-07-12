# [A_test] module_id: SRC-TST-1073 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_governance_drift_fix
# [INVARIANTS] auto_fixable=True => fixed=True; auto_fixable=False => fixed=False and MANUAL_REQUIRED
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError on invalid event; TypeError on wrong types
# [TESTS] tests/test_governance_drift_fix.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.drift_fix import DriftFixHandler
from zephyr.gov_drift.events import ManagedDriftEvent, ManagedDriftState, DriftType


class TestDriftFixHandlerInstantiation:
    def test_can_instantiate(self):
        handler = DriftFixHandler()
        assert handler is not None

    def test_is_instance_of_correct_class(self):
        handler = DriftFixHandler()
        assert isinstance(handler, DriftFixHandler)


class TestOnDriftFix:
    def test_auto_fixable_event_returns_fixed_true(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-001",
            target="src/main.py",
            drift_type=DriftType.CODE_DIVERGENCE,
            fix_suggestion="Revert to commit abc123",
            auto_fixable=True,
        )
        result = handler.on_drift_fix(event)

        assert result["fixed"] is True
        assert result["action"] == "AUTO_FIXED"
        assert result["drift_id"] == "drift-001"
        assert result["target"] == "src/main.py"
        assert result["fix_suggestion"] == "Revert to commit abc123"

    def test_auto_fixable_event_marks_state_as_fixed(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-002",
            target="config.yaml",
            drift_type=DriftType.CONFIG_DRIFT,
            auto_fixable=True,
        )
        handler.on_drift_fix(event)
        assert event.state == ManagedDriftState.FIXED

    def test_not_auto_fixable_event_returns_fixed_false(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-003",
            target="schema.sql",
            drift_type=DriftType.SCHEMA_DRIFT,
            auto_fixable=False,
        )
        result = handler.on_drift_fix(event)

        assert result["fixed"] is False
        assert result["action"] == "MANUAL_REQUIRED"
        assert result["reason"] == "auto_fixable=False"

    def test_not_auto_fixable_event_marks_state_as_manual_required(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-004",
            target="deps.txt",
            drift_type=DriftType.DEPENDENCY_DRIFT,
            auto_fixable=False,
        )
        handler.on_drift_fix(event)
        assert event.state == ManagedDriftState.MANUAL_REQUIRED

    def test_result_contains_drift_type(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-005",
            target="api.py",
            drift_type=DriftType.INTERFACE_DRIFT,
            auto_fixable=True,
        )
        result = handler.on_drift_fix(event)
        assert result["drift_type"] == "INTERFACE_DRIFT"


class TestOnDriftFixBoundaryCases:
    def test_auto_fixable_with_empty_fix_suggestion(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-006",
            target="f.py",
            drift_type=DriftType.CODE_DIVERGENCE,
            fix_suggestion="",
            auto_fixable=True,
        )
        result = handler.on_drift_fix(event)
        assert result["fixed"] is True
        assert result["fix_suggestion"] == ""

    def test_not_auto_fixable_with_empty_drift_id(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="",
            target="f.py",
            drift_type=DriftType.CONFIG_DRIFT,
            auto_fixable=False,
        )
        result = handler.on_drift_fix(event)
        assert result["drift_id"] == ""
        assert result["fixed"] is False

    def test_auto_fixable_with_empty_target(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-007",
            target="",
            drift_type=DriftType.CODE_DIVERGENCE,
            auto_fixable=True,
        )
        result = handler.on_drift_fix(event)
        assert result["target"] == ""

    def test_each_drift_type(self):
        handler = DriftFixHandler()
        for dt in DriftType:
            event = ManagedDriftEvent(
                drift_id=f"drift-{dt.value}",
                target="f.py",
                drift_type=dt,
                auto_fixable=True,
            )
            result = handler.on_drift_fix(event)
            assert result["drift_type"] == dt.value
            assert result["fixed"] is True
