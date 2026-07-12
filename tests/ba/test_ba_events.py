# [A_test] module_id: SRC-TST-0399 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ba_events
# [INVARIANTS] 事件定义不可修改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] behavioral_auditor包内所有模块
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] 定义所有漂移事件类型
# [TESTS] tests/test_ba_events.py
# [TTL] task_bound


from zephyr.gov_drift.events import (
    ManagedDriftEvent,
    ManagedDriftState,
    DriftType,
)


class TestDriftType:
    def test_all_types_exist(self):
        expected = {
            "CODE_DIVERGENCE",
            "CONFIG_DRIFT",
            "SCHEMA_DRIFT",
            "DEPENDENCY_DRIFT",
            "INTERFACE_DRIFT",
        }
        actual = {t.value for t in DriftType}
        assert actual == expected

    def test_type_is_str_enum(self):
        assert isinstance(DriftType.CODE_DIVERGENCE, str)
        assert DriftType.CODE_DIVERGENCE == "CODE_DIVERGENCE"


class TestManagedDriftState:
    def test_all_states_exist(self):
        expected = {"DETECTED", "FIXED", "MANUAL_REQUIRED", "IGNORED"}
        actual = {s.value for s in ManagedDriftState}
        assert actual == expected

    def test_state_is_str_enum(self):
        assert isinstance(ManagedDriftState.DETECTED, str)
        assert ManagedDriftState.DETECTED == "DETECTED"


class TestManagedDriftEvent:
    def test_instantiation_with_required_fields(self):
        evt = ManagedDriftEvent(drift_id="drift-001", target="src/module.py")
        assert evt.drift_id == "drift-001"
        assert evt.target == "src/module.py"
        assert evt.drift_type == DriftType.CODE_DIVERGENCE
        assert evt.state == ManagedDriftState.DETECTED
        assert evt.auto_fixable is False
        assert evt.fix_suggestion == ""
        assert evt.agent_id == ""
        assert evt.severity == "MEDIUM"

    def test_custom_fields(self):
        evt = ManagedDriftEvent(
            drift_id="drift-002",
            target="config.yaml",
            drift_type=DriftType.CONFIG_DRIFT,
            fix_suggestion="Update config",
            auto_fixable=True,
            state=ManagedDriftState.FIXED,
            agent_id="agent-1",
            severity="HIGH",
        )
        assert evt.drift_type == DriftType.CONFIG_DRIFT
        assert evt.fix_suggestion == "Update config"
        assert evt.auto_fixable is True
        assert evt.state == ManagedDriftState.FIXED
        assert evt.severity == "HIGH"

    def test_detected_at_auto_set(self):
        evt = ManagedDriftEvent(drift_id="drift-003", target="test.py")
        assert evt.detected_at != ""
        assert "T" in evt.detected_at

    def test_mark_fixed(self):
        evt = ManagedDriftEvent(drift_id="drift-004", target="test.py")
        evt.mark_fixed()
        assert evt.state == ManagedDriftState.FIXED

    def test_mark_manual_required(self):
        evt = ManagedDriftEvent(drift_id="drift-005", target="test.py")
        evt.mark_manual_required()
        assert evt.state == ManagedDriftState.MANUAL_REQUIRED

    def test_model_dump(self):
        evt = ManagedDriftEvent(drift_id="drift-006", target="test.py")
        data = evt.model_dump()
        assert "drift_id" in data
        assert "target" in data
        assert "drift_type" in data
        assert "state" in data
