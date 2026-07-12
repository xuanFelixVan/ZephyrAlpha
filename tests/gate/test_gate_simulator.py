# [A_test] module_id: SRC-TST-1046 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3.1

# [MODULE] tests.test_gate_simulator

# [INVARIANTS] GateSimulator.simulate must not modify pipeline or ctx state; history must be append-only

# [MODIFY-GUARD] changes require gate_simulator.py review

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] all tests must pass; no external dependencies

# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_context import GateContext, GateResult, GateStatus
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_pipeline import GatePipeline, GateStep
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_simulator import GateSimulator, SimulationReport


def _make_pass_checker(gate_id: str) -> GateStep:
    return GateStep(
        gate_id=gate_id,
        checker=lambda ctx: GateResult(gate_id=gate_id, status=GateStatus.PASS),
    )


def _make_fail_checker(gate_id: str) -> GateStep:
    return GateStep(
        gate_id=gate_id,
        checker=lambda ctx: GateResult(
            gate_id=gate_id,
            status=GateStatus.FAIL,
            reasons=[f"{gate_id} failed"],
        ),
    )


def _make_error_checker(gate_id: str) -> GateStep:
    def _raise(ctx: GateContext) -> GateResult:
        raise RuntimeError(f"{gate_id} exploded")

    return GateStep(gate_id=gate_id, checker=_raise)


def _make_ctx(session_id: str = "sess-001") -> GateContext:
    return GateContext(session_id=session_id, task_id="task-001")


class TestSimulationReport:
    def test_fields_assigned(self):
        results = [GateResult(gate_id="G1", status=GateStatus.PASS)]
        now = datetime.now(UTC)
        report = SimulationReport(
            pipeline_name="pipe",
            results=results,
            overall=GateStatus.PASS,
            duration_ms=12.5,
            timestamp=now,
        )
        assert report.pipeline_name == "pipe"
        assert report.results is results
        assert report.overall == GateStatus.PASS
        assert report.duration_ms == 12.5
        assert report.timestamp == now

    def test_default_timestamp_is_utc_now(self):
        before = datetime.now(UTC)
        report = SimulationReport(
            pipeline_name="p",
            results=[],
            overall=GateStatus.PASS,
            duration_ms=0.0,
        )
        after = datetime.now(UTC)
        assert before <= report.timestamp <= after
        assert report.timestamp.tzinfo == UTC

    def test_summary_all_pass(self):
        results = [
            GateResult(gate_id="G1", status=GateStatus.PASS),
            GateResult(gate_id="G2", status=GateStatus.PASS),
        ]
        report = SimulationReport(
            pipeline_name="all_pass",
            results=results,
            overall=GateStatus.PASS,
            duration_ms=5.0,
        )
        s = report.summary()
        assert "all_pass" in s
        assert "PASS" in s
        assert "2P" in s
        assert "0F" in s
        assert "2T" in s

    def test_summary_mixed(self):
        results = [
            GateResult(gate_id="G1", status=GateStatus.PASS),
            GateResult(gate_id="G2", status=GateStatus.FAIL, reasons=["bad"]),
            GateResult(gate_id="G3", status=GateStatus.PASS),
        ]
        report = SimulationReport(
            pipeline_name="mixed",
            results=results,
            overall=GateStatus.FAIL,
            duration_ms=10.0,
        )
        s = report.summary()
        assert "2P" in s
        assert "1F" in s
        assert "3T" in s

    def test_summary_empty_results(self):
        report = SimulationReport(
            pipeline_name="empty",
            results=[],
            overall=GateStatus.PASS,
            duration_ms=0.0,
        )
        s = report.summary()
        assert "0P" in s
        assert "0F" in s
        assert "0T" in s


class TestGateSimulatorInit:
    def test_empty_history_on_init(self):
        sim = GateSimulator()
        assert sim.history == []

    def test_history_returns_copy(self):
        sim = GateSimulator()
        h1 = sim.history
        h1.append(MagicMock())
        assert sim.history == []


class TestGateSimulatorSimulate:
    def test_simulate_single_pass(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="single_pass")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert isinstance(report, SimulationReport)
        assert report.pipeline_name == "single_pass"
        assert report.overall == GateStatus.PASS
        assert len(report.results) == 1
        assert report.results[0].status == GateStatus.PASS
        assert report.duration_ms >= 0.0

    def test_simulate_single_fail(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="single_fail")
        pipe.add(_make_fail_checker("G1"))
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert report.overall == GateStatus.FAIL
        assert report.results[0].status == GateStatus.FAIL
        assert report.results[0].reasons == ["G1 failed"]

    def test_simulate_multiple_steps_all_pass(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="multi_pass")
        pipe.add(_make_pass_checker("G1"))
        pipe.add(_make_pass_checker("G2"))
        pipe.add(_make_pass_checker("G3"))
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert report.overall == GateStatus.PASS
        assert len(report.results) == 3
        assert all(r.status == GateStatus.PASS for r in report.results)

    def test_simulate_mixed_pass_fail_overall_fail(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="mixed")
        pipe.add(_make_pass_checker("G1"))
        pipe.add(_make_fail_checker("G2"))
        pipe.add(_make_pass_checker("G3"))
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert report.overall == GateStatus.FAIL

    def test_simulate_appends_to_history(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="hist")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        sim.simulate(pipe, ctx)
        assert len(sim.history) == 1
        sim.simulate(pipe, ctx)
        assert len(sim.history) == 2

    def test_simulate_report_timestamp_populated(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="ts")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert isinstance(report.timestamp, datetime)
        assert report.timestamp.tzinfo == UTC

    def test_simulate_duration_positive(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="dur")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert report.duration_ms >= 0.0

    def test_simulate_empty_pipeline(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="empty_pipe")
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert report.pipeline_name == "empty_pipe"
        assert report.results == []
        assert report.overall == GateStatus.PASS
        assert report.duration_ms >= 0.0

    def test_simulate_step_raises_error_status(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="error_step")
        pipe.add(_make_error_checker("G_ERR"))
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert len(report.results) == 1
        assert report.results[0].status == GateStatus.ERROR

    def test_simulate_does_not_modify_context(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="ctx_safe")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        original_session = ctx.session_id
        original_task = ctx.task_id
        sim.simulate(pipe, ctx)
        assert ctx.session_id == original_session
        assert ctx.task_id == original_task

    def test_simulate_with_skip_status(self):
        pipe = GatePipeline(name="skip")
        pipe.add(
            GateStep(
                gate_id="G_SKIP",
                checker=lambda ctx: GateResult(gate_id="G_SKIP", status=GateStatus.SKIP),
            )
        )
        sim = GateSimulator()
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert report.results[0].status == GateStatus.SKIP
        assert report.overall == GateStatus.PASS

    def test_simulate_with_waived_status(self):
        pipe = GatePipeline(name="waived")
        pipe.add(
            GateStep(
                gate_id="G_WAIVED",
                checker=lambda ctx: GateResult(gate_id="G_WAIVED", status=GateStatus.WAIVED),
            )
        )
        sim = GateSimulator()
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert report.results[0].status == GateStatus.WAIVED
        assert report.overall == GateStatus.PASS


class TestGateSimulatorHistory:
    def test_history_tracks_multiple_simulations(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="multi_hist")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        for i in range(5):
            sim.simulate(pipe, ctx)
        assert len(sim.history) == 5
        for report in sim.history:
            assert isinstance(report, SimulationReport)

    def test_history_preserves_order(self):
        sim = GateSimulator()
        ctx = _make_ctx()
        pipe_pass = GatePipeline(name="pass_pipe")
        pipe_pass.add(_make_pass_checker("G1"))
        pipe_fail = GatePipeline(name="fail_pipe")
        pipe_fail.add(_make_fail_checker("G1"))
        sim.simulate(pipe_pass, ctx)
        sim.simulate(pipe_fail, ctx)
        assert sim.history[0].overall == GateStatus.PASS
        assert sim.history[1].overall == GateStatus.FAIL

    def test_history_returns_separate_list(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="copy")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        sim.simulate(pipe, ctx)
        first_history = sim.history
        sim.simulate(pipe, ctx)
        assert len(first_history) == 1
        assert len(sim.history) == 2


class TestGateSimulatorClearHistory:
    def test_clear_history_empties_list(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="clear")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        sim.simulate(pipe, ctx)
        assert len(sim.history) == 1
        sim.clear_history()
        assert sim.history == []

    def test_clear_history_on_empty_simulator(self):
        sim = GateSimulator()
        sim.clear_history()
        assert sim.history == []

    def test_clear_then_simulate_again(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="re_sim")
        pipe.add(_make_pass_checker("G1"))
        ctx = _make_ctx()
        sim.simulate(pipe, ctx)
        sim.clear_history()
        sim.simulate(pipe, ctx)
        assert len(sim.history) == 1


class TestGateSimulatorBoundary:
    def test_simulate_none_pipeline_raises(self):
        sim = GateSimulator()
        ctx = _make_ctx()
        with pytest.raises(AttributeError):
            sim.simulate(None, ctx)

    def test_simulate_none_context_produces_error_result(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="none_ctx")
        pipe.add(
            GateStep(
                gate_id="G_CTX",
                checker=lambda ctx: GateResult(gate_id="G_CTX", status=GateStatus.PASS, task_id=ctx.task_id),
            )
        )
        report = sim.simulate(pipe, None)
        assert report.results[0].status == GateStatus.ERROR

    def test_simulate_both_none_raises(self):
        sim = GateSimulator()
        with pytest.raises((AttributeError, TypeError)):
            sim.simulate(None, None)

    def test_simulate_large_number_of_steps(self):
        sim = GateSimulator()
        pipe = GatePipeline(name="large")
        for i in range(50):
            pipe.add(_make_pass_checker(f"G{i:03d}"))
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert report.overall == GateStatus.PASS
        assert len(report.results) == 50

    def test_simulate_checker_returns_non_gate_result(self):
        pipe = GatePipeline(name="bad_return")
        pipe.add(
            GateStep(
                gate_id="G_BAD",
                checker=lambda ctx: "not_a_gate_result",
            )
        )
        sim = GateSimulator()
        ctx = _make_ctx()
        report = sim.simulate(pipe, ctx)
        assert len(report.results) == 1
        assert isinstance(report.results[0], GateResult)
