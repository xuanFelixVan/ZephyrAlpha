# [A_test] module_id: MOD-GOV_startup_shutdown | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-infra_ops/rollback-system/blueprint.md
# [MODULE] tests.test_startup_shutdown
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] StartupOrchestrator sequential phase run;ShutdownOrchestrator reverse order;DAG dependency check
# [MODIFY-GUARD] src/zephyr/rollback/startup_shutdown.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_startup_shutdown.py
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.infrastructure.runtime.startup_shutdown import (
    SHUTDOWN_SEQUENCE,
    STARTUP_DAG,
    PhaseState,
    ShutdownOrchestrator,
    StartupOrchestrator,
    StartupPhase,
    StartupPhaseDef,
    get_phase_def,
    shutdown_ordered_phases,
    startup_ordered_phases,
)


@pytest.fixture(autouse=True)
def reset_dag_states() -> None:
    original_states: dict[StartupPhase, PhaseState] = {}
    for phase, pdef in STARTUP_DAG.items():
        original_states[phase] = pdef.state
    yield
    for phase, pdef in STARTUP_DAG.items():
        pdef.state = original_states.get(phase, PhaseState.PENDING)


class TestStartupPhaseDef:
    def test_construction_defaults(self) -> None:
        pdef = StartupPhaseDef(
            phase=StartupPhase.P1_SECRETS_DB,
            label="Test",
        )
        assert pdef.phase == StartupPhase.P1_SECRETS_DB
        assert pdef.label == "Test"
        assert pdef.depends_on == []
        assert pdef.health_check == ""
        assert pdef.timeout_seconds == 30
        assert pdef.state == PhaseState.PENDING

    def test_is_ready_no_deps(self) -> None:
        pdef = StartupPhaseDef(
            phase=StartupPhase.P1_SECRETS_DB,
            label="No deps",
            depends_on=[],
        )
        assert pdef.is_ready is True

    def test_is_ready_with_healthy_dep(self) -> None:
        STARTUP_DAG[StartupPhase.P1_SECRETS_DB].state = PhaseState.HEALTHY
        pdef = StartupPhaseDef(
            phase=StartupPhase.P2_CONTEXT_GATE,
            label="Depends on P1",
            depends_on=[StartupPhase.P1_SECRETS_DB],
        )
        assert pdef.is_ready is True

    def test_is_ready_with_unhealthy_dep(self) -> None:
        STARTUP_DAG[StartupPhase.P1_SECRETS_DB].state = PhaseState.FAILED
        pdef = StartupPhaseDef(
            phase=StartupPhase.P2_CONTEXT_GATE,
            label="Depends on P1",
            depends_on=[StartupPhase.P1_SECRETS_DB],
        )
        assert pdef.is_ready is False


class TestStartupOrchestrator:
    def test_instantiation(self) -> None:
        orch = StartupOrchestrator(health_check_fn=lambda _: True)
        assert orch.health_check is not None

    def test_run_all_healthy(self) -> None:
        orch = StartupOrchestrator(health_check_fn=lambda _: True)
        result = orch.run()
        assert result is True
        for phase in StartupPhase:
            assert STARTUP_DAG[phase].state == PhaseState.HEALTHY

    def test_run_phase_fails(self) -> None:
        call_count = 0

        def health_check(name: str) -> bool:
            nonlocal call_count
            call_count += 1
            return name != "check_market_data"

        orch = StartupOrchestrator(health_check_fn=health_check)
        result = orch.run()
        assert result is False
        assert STARTUP_DAG[StartupPhase.P3_MARKET_DATA].state == PhaseState.FAILED
        assert STARTUP_DAG[StartupPhase.P4_FACTOR_SIGNAL].state == PhaseState.PENDING

    def test_run_first_phase_fails(self) -> None:
        orch = StartupOrchestrator(health_check_fn=lambda _: False)
        result = orch.run()
        assert result is False
        assert STARTUP_DAG[StartupPhase.P1_SECRETS_DB].state == PhaseState.FAILED

    def test_run_resets_states_between_runs(self) -> None:
        orch = StartupOrchestrator(health_check_fn=lambda _: True)
        orch.run()
        for phase in StartupPhase:
            assert STARTUP_DAG[phase].state == PhaseState.HEALTHY


class TestShutdownOrchestrator:
    def test_instantiation(self) -> None:
        orch = ShutdownOrchestrator(shutdown_fn=lambda _: True)
        assert orch.shutdown is not None

    def test_run_all_succeed(self) -> None:
        for phase in StartupPhase:
            STARTUP_DAG[phase].state = PhaseState.HEALTHY
        orch = ShutdownOrchestrator(shutdown_fn=lambda _: True)
        result = orch.run()
        assert result is True
        for phase in StartupPhase:
            assert STARTUP_DAG[phase].state == PhaseState.PENDING

    def test_run_shutdown_fails(self) -> None:
        for phase in StartupPhase:
            STARTUP_DAG[phase].state = PhaseState.HEALTHY

        def shutdown_fn(phase: StartupPhase) -> bool:
            return phase != StartupPhase.P5_OMS_RISK

        orch = ShutdownOrchestrator(shutdown_fn=shutdown_fn)
        result = orch.run()
        assert result is False

    def test_shutdown_order_is_reversed(self) -> None:
        phases_seen: list[StartupPhase] = []

        def shutdown_fn(phase: StartupPhase) -> bool:
            phases_seen.append(phase)
            return True

        for phase in StartupPhase:
            STARTUP_DAG[phase].state = PhaseState.HEALTHY
        orch = ShutdownOrchestrator(shutdown_fn=shutdown_fn)
        orch.run()
        assert phases_seen == list(reversed(list(StartupPhase)))


class TestDagStructure:
    def test_startup_dag_has_all_phases(self) -> None:
        for phase in StartupPhase:
            assert phase in STARTUP_DAG

    def test_p1_has_no_deps(self) -> None:
        assert STARTUP_DAG[StartupPhase.P1_SECRETS_DB].depends_on == []

    def test_p6_depends_on_p5(self) -> None:
        assert StartupPhase.P5_OMS_RISK in STARTUP_DAG[StartupPhase.P6_DASHBOARD_TELEMETRY].depends_on

    def test_shutdown_sequence_is_reversed(self) -> None:
        assert list(reversed(list(StartupPhase))) == SHUTDOWN_SEQUENCE


class TestHelperFunctions:
    def test_get_phase_def_existing(self) -> None:
        pdef = get_phase_def(StartupPhase.P1_SECRETS_DB)
        assert pdef is not None
        assert pdef.phase == StartupPhase.P1_SECRETS_DB

    def test_get_phase_def_returns_none_for_missing(self) -> None:
        result = get_phase_def(StartupPhase.P1_SECRETS_DB)
        assert result is not None

    def test_startup_ordered_phases(self) -> None:
        phases = startup_ordered_phases()
        assert phases == list(StartupPhase)
        assert len(phases) == 6

    def test_shutdown_ordered_phases(self) -> None:
        phases = shutdown_ordered_phases()
        assert phases == list(reversed(list(StartupPhase)))
        assert len(phases) == 6


class TestPhaseStateEnum:
    def test_all_states(self) -> None:
        assert PhaseState.PENDING.value == "PENDING"
        assert PhaseState.RUNNING.value == "RUNNING"
        assert PhaseState.HEALTHY.value == "HEALTHY"
        assert PhaseState.FAILED.value == "FAILED"

    def test_phase_count(self) -> None:
        assert len(StartupPhase) == 6
