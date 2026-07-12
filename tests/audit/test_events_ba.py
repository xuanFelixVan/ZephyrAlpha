# [A_test] module_id: SRC-TST-0870 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_events_ba
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_events_ba.py -q
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime

from zephyr.gov_drift.events import (
    ManagedDriftEvent,
    ManagedDriftState,
    DriftType,
)


class TestDriftTypeEnum:
    def test_all_values_defined(self):
        assert DriftType.CODE_DIVERGENCE.value == "CODE_DIVERGENCE"
        assert DriftType.CONFIG_DRIFT.value == "CONFIG_DRIFT"
        assert DriftType.SCHEMA_DRIFT.value == "SCHEMA_DRIFT"
        assert DriftType.DEPENDENCY_DRIFT.value == "DEPENDENCY_DRIFT"
        assert DriftType.INTERFACE_DRIFT.value == "INTERFACE_DRIFT"

    def test_enum_count(self):
        assert len(DriftType) == 5

    def test_string_comparison(self):
        assert DriftType.CODE_DIVERGENCE == "CODE_DIVERGENCE"
        assert DriftType.CONFIG_DRIFT == "CONFIG_DRIFT"

    def test_from_value(self):
        assert DriftType("CODE_DIVERGENCE") == DriftType.CODE_DIVERGENCE
        assert DriftType("SCHEMA_DRIFT") == DriftType.SCHEMA_DRIFT


class TestManagedDriftStateEnum:
    def test_all_values_defined(self):
        assert ManagedDriftState.DETECTED.value == "DETECTED"
        assert ManagedDriftState.FIXED.value == "FIXED"
        assert ManagedDriftState.MANUAL_REQUIRED.value == "MANUAL_REQUIRED"
        assert ManagedDriftState.IGNORED.value == "IGNORED"

    def test_enum_count(self):
        assert len(ManagedDriftState) == 4

    def test_string_comparison(self):
        assert ManagedDriftState.DETECTED == "DETECTED"
        assert ManagedDriftState.FIXED == "FIXED"

    def test_from_value(self):
        assert ManagedDriftState("DETECTED") == ManagedDriftState.DETECTED
        assert ManagedDriftState("FIXED") == ManagedDriftState.FIXED


class TestManagedDriftEventInstantiation:
    def test_required_fields(self):
        evt = ManagedDriftEvent(drift_id="d-001", target="src/module.py")
        assert evt.drift_id == "d-001"
        assert evt.target == "src/module.py"

    def test_default_drift_type(self):
        evt = ManagedDriftEvent(drift_id="d-002", target="file.py")
        assert evt.drift_type == DriftType.CODE_DIVERGENCE

    def test_default_state(self):
        evt = ManagedDriftEvent(drift_id="d-003", target="file.py")
        assert evt.state == ManagedDriftState.DETECTED

    def test_default_auto_fixable(self):
        evt = ManagedDriftEvent(drift_id="d-004", target="file.py")
        assert evt.auto_fixable is False

    def test_default_severity(self):
        evt = ManagedDriftEvent(drift_id="d-005", target="file.py")
        assert evt.severity == "MEDIUM"

    def test_default_empty_strings(self):
        evt = ManagedDriftEvent(drift_id="d-006", target="file.py")
        assert evt.fix_suggestion == ""
        assert evt.agent_id == ""

    def test_detected_at_auto_generated(self):
        evt = ManagedDriftEvent(drift_id="d-007", target="file.py")
        assert evt.detected_at != ""
        parsed = datetime.fromisoformat(evt.detected_at)
        assert parsed.tzinfo is not None

    def test_custom_fields(self):
        evt = ManagedDriftEvent(
            drift_id="d-008",
            target="src/core.py",
            drift_type=DriftType.SCHEMA_DRIFT,
            fix_suggestion="Run migration",
            auto_fixable=True,
            state=ManagedDriftState.MANUAL_REQUIRED,
            agent_id="agent-001",
            severity="HIGH",
        )
        assert evt.drift_type == DriftType.SCHEMA_DRIFT
        assert evt.fix_suggestion == "Run migration"
        assert evt.auto_fixable is True
        assert evt.state == ManagedDriftState.MANUAL_REQUIRED
        assert evt.agent_id == "agent-001"
        assert evt.severity == "HIGH"


class TestManagedDriftEventMarkFixed:
    def test_mark_fixed_transitions_state(self):
        evt = ManagedDriftEvent(drift_id="d-010", target="file.py")
        assert evt.state == ManagedDriftState.DETECTED
        evt.mark_fixed()
        assert evt.state == ManagedDriftState.FIXED

    def test_mark_fixed_from_manual_required(self):
        evt = ManagedDriftEvent(
            drift_id="d-011",
            target="file.py",
            state=ManagedDriftState.MANUAL_REQUIRED,
        )
        evt.mark_fixed()
        assert evt.state == ManagedDriftState.FIXED


class TestManagedDriftEventMarkManualRequired:
    def test_mark_manual_required_transitions_state(self):
        evt = ManagedDriftEvent(drift_id="d-012", target="file.py")
        assert evt.state == ManagedDriftState.DETECTED
        evt.mark_manual_required()
        assert evt.state == ManagedDriftState.MANUAL_REQUIRED

    def test_mark_manual_required_from_ignored(self):
        evt = ManagedDriftEvent(
            drift_id="d-013",
            target="file.py",
            state=ManagedDriftState.IGNORED,
        )
        evt.mark_manual_required()
        assert evt.state == ManagedDriftState.MANUAL_REQUIRED


class TestManagedDriftEventBoundary:
    def test_empty_drift_id(self):
        evt = ManagedDriftEvent(drift_id="", target="file.py")
        assert evt.drift_id == ""

    def test_empty_target(self):
        evt = ManagedDriftEvent(drift_id="d-014", target="")
        assert evt.target == ""

    def test_long_fix_suggestion(self):
        long_suggestion = "x" * 1000
        evt = ManagedDriftEvent(
            drift_id="d-015",
            target="file.py",
            fix_suggestion=long_suggestion,
        )
        assert len(evt.fix_suggestion) == 1000

    def test_all_drift_types_assignable(self):
        for dt in DriftType:
            evt = ManagedDriftEvent(drift_id=f"d-{dt.value}", target="f.py", drift_type=dt)
            assert evt.drift_type == dt

    def test_all_drift_states_assignable(self):
        for ds in ManagedDriftState:
            evt = ManagedDriftEvent(drift_id=f"d-{ds.value}", target="f.py", state=ds)
            assert evt.state == ds

    def test_model_serialization(self):
        evt = ManagedDriftEvent(drift_id="d-016", target="file.py")
        data = evt.model_dump()
        assert "drift_id" in data
        assert "target" in data
        assert data["drift_id"] == "d-016"

    def test_model_from_dict(self):
        data = {"drift_id": "d-017", "target": "src/main.py"}
        evt = ManagedDriftEvent(**data)
        assert evt.drift_id == "d-017"
        assert evt.target == "src/main.py"
