# [A_test] module_id: SRC-TST-1681 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_startup_sequencer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_startup_sequencer.py
# [TTL] task_bound


from zephyr.orchestrator.lifecycle.startup_sequencer import (
    GLOBAL_TIMEOUT_S,
    STARTUP_COMPONENTS,
    STARTUP_ORDER,
    StartupLayer,
    StartupSequencer,
    StartupState,
)


class TestStartupLayerEnum:
    def test_has_five_layers(self):
        assert len(StartupLayer) == 5

    def test_layer_values(self):
        assert StartupLayer.L1_DATABASE.value == "L1_database"
        assert StartupLayer.L2_VMS.value == "L2_vector_memory"
        assert StartupLayer.L3_FLE.value == "L3_feedback_loop"
        assert StartupLayer.L4_CORE_SERVICES.value == "L4_core_services"
        assert StartupLayer.L5_TELEMETRY.value == "L5_telemetry"


class TestStartupOrder:
    def test_order_has_five_layers(self):
        assert len(STARTUP_ORDER) == 5

    def test_order_starts_with_database(self):
        assert STARTUP_ORDER[0] == StartupLayer.L1_DATABASE

    def test_order_ends_with_telemetry(self):
        assert STARTUP_ORDER[-1] == StartupLayer.L5_TELEMETRY

    def test_order_is_correct(self):
        expected = [
            StartupLayer.L1_DATABASE,
            StartupLayer.L2_VMS,
            StartupLayer.L3_FLE,
            StartupLayer.L4_CORE_SERVICES,
            StartupLayer.L5_TELEMETRY,
        ]
        assert list(STARTUP_ORDER) == expected


class TestGlobalTimeout:
    def test_timeout_is_120(self):
        assert GLOBAL_TIMEOUT_S == 120.0


class TestStartupComponents:
    def test_l4_has_core_services(self):
        components = STARTUP_COMPONENTS[StartupLayer.L4_CORE_SERVICES]
        assert "orchestrator" in components
        assert "script_system" in components
        assert "knowledge_base" in components

    def test_l1_has_database(self):
        assert STARTUP_COMPONENTS[StartupLayer.L1_DATABASE] == ["database"]


class TestStartupStateModel:
    def test_default_values(self):
        state = StartupState(layer=StartupLayer.L1_DATABASE)
        assert state.status == "pending"
        assert state.started_at is None
        assert state.completed_at is None


class TestStartupSequencerInstantiation:
    def test_create_instance(self):
        seq = StartupSequencer()
        assert seq is not None

    def test_has_get_order(self):
        seq = StartupSequencer()
        assert callable(seq.get_order)

    def test_has_start_layer(self):
        seq = StartupSequencer()
        assert callable(seq.start_layer)

    def test_has_complete_layer(self):
        seq = StartupSequencer()
        assert callable(seq.complete_layer)


class TestGetOrder:
    def test_returns_list(self):
        seq = StartupSequencer()
        result = seq.get_order()
        assert isinstance(result, list)

    def test_returns_five_strings(self):
        seq = StartupSequencer()
        result = seq.get_order()
        assert len(result) == 5
        assert all(isinstance(v, str) for v in result)

    def test_first_is_database(self):
        seq = StartupSequencer()
        result = seq.get_order()
        assert result[0] == "L1_database"


class TestGetLayerComponents:
    def test_l1_components(self):
        seq = StartupSequencer()
        result = seq.get_layer_components(StartupLayer.L1_DATABASE)
        assert "database" in result

    def test_l4_components(self):
        seq = StartupSequencer()
        result = seq.get_layer_components(StartupLayer.L4_CORE_SERVICES)
        assert len(result) > 1

    def test_unknown_layer_returns_empty(self):
        seq = StartupSequencer()
        result = seq.get_layer_components(StartupLayer.L1_DATABASE)
        assert isinstance(result, list)


class TestStartLayer:
    def test_start_first_layer(self):
        seq = StartupSequencer()
        result = seq.start_layer(StartupLayer.L1_DATABASE)
        assert result is True

    def test_start_second_without_first_completed(self):
        seq = StartupSequencer()
        result = seq.start_layer(StartupLayer.L2_VMS)
        assert result is False

    def test_start_second_after_first_completed(self):
        seq = StartupSequencer()
        seq.start_layer(StartupLayer.L1_DATABASE)
        seq.complete_layer(StartupLayer.L1_DATABASE)
        result = seq.start_layer(StartupLayer.L2_VMS)
        assert result is True

    def test_full_sequential_startup(self):
        seq = StartupSequencer()
        for layer in STARTUP_ORDER:
            assert seq.start_layer(layer) is True
            seq.complete_layer(layer)

    def test_start_layer_sets_status_running(self):
        seq = StartupSequencer()
        seq.start_layer(StartupLayer.L1_DATABASE)
        assert seq._states[StartupLayer.L1_DATABASE].status == "running"


class TestCompleteLayer:
    def test_complete_sets_status(self):
        seq = StartupSequencer()
        seq.start_layer(StartupLayer.L1_DATABASE)
        seq.complete_layer(StartupLayer.L1_DATABASE)
        assert seq._states[StartupLayer.L1_DATABASE].status == "completed"

    def test_complete_sets_timestamp(self):
        seq = StartupSequencer()
        seq.start_layer(StartupLayer.L1_DATABASE)
        seq.complete_layer(StartupLayer.L1_DATABASE)
        assert seq._states[StartupLayer.L1_DATABASE].completed_at is not None
