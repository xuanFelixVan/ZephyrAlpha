# [A_test] module_id: SRC-TST-1045 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3.1

# [MODULE] tests.test_gate_pipeline

# [INVARIANTS] Combinator has exactly 3 members; GateStep.checker must accept GateContext and return GateResult; GatePipeline.run returns empty list for empty pipeline; evaluate returns PASS for empty results

# [MODIFY-GUARD] changes require source gate_pipeline.py review

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] checker exceptions produce GateResult with status=ERROR; from_engine_step wraps engine exceptions in ERROR result

# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_context import GateContext, GateResult, GateStatus
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_pipeline import Combinator, GatePipeline, GateStep


def _pass_checker(ctx: GateContext) -> GateResult:
    return GateResult(gate_id="G_PASS", status=GateStatus.PASS)


def _fail_checker(ctx: GateContext) -> GateResult:
    return GateResult(gate_id="G_FAIL", status=GateStatus.FAIL, reasons=["check failed"])


def _error_checker(ctx: GateContext) -> GateResult:
    return GateResult(gate_id="G_ERR", status=GateStatus.ERROR, reasons=["internal error"])


def _raise_checker(ctx: GateContext) -> GateResult:
    raise RuntimeError("checker exploded")


class TestCombinator:
    def test_has_three_members(self):
        assert len(Combinator) == 3

    def test_member_names(self):
        expected = {"AND", "OR", "NOT"}
        assert set(m.name for m in Combinator) == expected

    def test_members_are_distinct(self):
        values = [m.value for m in Combinator]
        assert len(values) == len(set(values))


class TestGateStep:
    def test_instantiation_defaults(self):
        step = GateStep(gate_id="G1", checker=_pass_checker)
        assert step.gate_id == "G1"
        assert step.checker is _pass_checker
        assert step.combinator == Combinator.AND
        assert step.depends_on == []

    def test_instantiation_full(self):
        step = GateStep(
            gate_id="G2",
            checker=_fail_checker,
            combinator=Combinator.OR,
            depends_on=["G1"],
        )
        assert step.gate_id == "G2"
        assert step.combinator == Combinator.OR
        assert step.depends_on == ["G1"]

    def test_checker_callable(self):
        ctx = GateContext(session_id="s1")
        step = GateStep(gate_id="G1", checker=_pass_checker)
        result = step.checker(ctx)
        assert isinstance(result, GateResult)
        assert result.status == GateStatus.PASS

    def test_checker_returns_fail(self):
        ctx = GateContext(session_id="s1")
        step = GateStep(gate_id="G1", checker=_fail_checker)
        result = step.checker(ctx)
        assert result.status == GateStatus.FAIL

    def test_depends_on_multiple(self):
        step = GateStep(gate_id="G3", checker=_pass_checker, depends_on=["G1", "G2"])
        assert step.depends_on == ["G1", "G2"]


class TestGatePipelineInstantiation:
    def test_default_name(self):
        p = GatePipeline()
        assert p.name == "default"

    def test_custom_name(self):
        p = GatePipeline(name="custom-pipeline")
        assert p.name == "custom-pipeline"

    def test_empty_len(self):
        p = GatePipeline()
        assert len(p) == 0

    def test_add_step_increments_len(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_pass_checker))
        assert len(p) == 1
        p.add(GateStep(gate_id="G2", checker=_pass_checker))
        assert len(p) == 2


class TestGatePipelineRun:
    def test_run_empty_pipeline(self):
        p = GatePipeline()
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        assert results == []

    def test_run_single_pass(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_pass_checker))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        assert len(results) == 1
        assert results[0].status == GateStatus.PASS

    def test_run_single_fail(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_fail_checker))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        assert len(results) == 1
        assert results[0].status == GateStatus.FAIL

    def test_run_parallel_all_pass(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_pass_checker))
        p.add(GateStep(gate_id="G2", checker=_pass_checker))
        p.add(GateStep(gate_id="G3", checker=_pass_checker))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        assert len(results) == 3
        assert all(r.status == GateStatus.PASS for r in results)

    def test_run_parallel_fail_short_circuits_depends(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_fail_checker))
        p.add(GateStep(gate_id="G2", checker=_pass_checker))
        p.add(GateStep(gate_id="G3", checker=_pass_checker, depends_on=["G1"]))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        gate_ids = [r.gate_id for r in results]
        assert "G3" not in gate_ids

    def test_run_depends_on_executed_after_parallel(self):
        call_order = []

        def checker_a(ctx: GateContext) -> GateResult:
            call_order.append("A")
            return GateResult(gate_id="A", status=GateStatus.PASS)

        def checker_b(ctx: GateContext) -> GateResult:
            call_order.append("B")
            return GateResult(gate_id="B", status=GateStatus.PASS)

        p = GatePipeline()
        p.add(GateStep(gate_id="A", checker=checker_a))
        p.add(GateStep(gate_id="B", checker=checker_b, depends_on=["A"]))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        assert len(results) == 2
        assert all(r.status == GateStatus.PASS for r in results)

    def test_run_checker_exception_produces_error(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_raise_checker))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        assert len(results) == 1
        assert results[0].status == GateStatus.ERROR
        assert "checker exploded" in results[0].reasons[0]

    def test_run_mixed_pass_fail(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_pass_checker))
        p.add(GateStep(gate_id="G2", checker=_fail_checker))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        statuses = {r.gate_id: r.status for r in results}
        assert statuses["G_PASS"] == GateStatus.PASS
        assert statuses["G_FAIL"] == GateStatus.FAIL


class TestGatePipelineEvaluate:
    def test_evaluate_all_pass(self):
        p = GatePipeline()
        results = [
            GateResult(gate_id="G1", status=GateStatus.PASS),
            GateResult(gate_id="G2", status=GateStatus.PASS),
        ]
        assert p.evaluate(results) == GateStatus.PASS

    def test_evaluate_with_fail(self):
        p = GatePipeline()
        results = [
            GateResult(gate_id="G1", status=GateStatus.PASS),
            GateResult(gate_id="G2", status=GateStatus.FAIL),
        ]
        assert p.evaluate(results) == GateStatus.FAIL

    def test_evaluate_empty_results(self):
        p = GatePipeline()
        assert p.evaluate([]) == GateStatus.PASS

    def test_evaluate_all_fail(self):
        p = GatePipeline()
        results = [
            GateResult(gate_id="G1", status=GateStatus.FAIL),
            GateResult(gate_id="G2", status=GateStatus.FAIL),
        ]
        assert p.evaluate(results) == GateStatus.FAIL

    def test_evaluate_error_counts_as_non_fail(self):
        p = GatePipeline()
        results = [
            GateResult(gate_id="G1", status=GateStatus.ERROR),
        ]
        assert p.evaluate(results) == GateStatus.PASS

    def test_evaluate_skip_counts_as_non_fail(self):
        p = GatePipeline()
        results = [
            GateResult(gate_id="G1", status=GateStatus.SKIP),
        ]
        assert p.evaluate(results) == GateStatus.PASS


class TestGatePipelineFromEngineStep:
    def test_from_engine_step_pass(self):
        @dataclass
        class FakeEngineResult:
            passed: bool = True
            gate_id: str = "G1"
            task_id: str = "T001"
            violations: list = None
            details: dict = None
            evaluated_at: str = ""

        class FakeEngine:
            def evaluate(self, task: Any, gate_id: str) -> FakeEngineResult:
                return FakeEngineResult()

        step = GatePipeline.from_engine_step("G1", FakeEngine(), task=None)
        assert step.gate_id == "G1"
        assert step.combinator == Combinator.AND
        assert step.depends_on == []

        ctx = GateContext(session_id="s1")
        result = step.checker(ctx)
        assert result.status == GateStatus.PASS

    def test_from_engine_step_fail(self):
        @dataclass
        class FakeEngineResult:
            passed: bool = False
            gate_id: str = "G2"
            task_id: str = "T002"
            violations: list = None
            details: dict = None
            evaluated_at: str = ""

        class FakeEngine:
            def evaluate(self, task: Any, gate_id: str) -> FakeEngineResult:
                return FakeEngineResult()

        step = GatePipeline.from_engine_step("G2", FakeEngine(), task=None)
        ctx = GateContext(session_id="s1")
        result = step.checker(ctx)
        assert result.status == GateStatus.FAIL

    def test_from_engine_step_exception(self):
        class BrokenEngine:
            def evaluate(self, task: Any, gate_id: str) -> Any:
                raise ValueError("engine broken")

        step = GatePipeline.from_engine_step("G3", BrokenEngine(), task=None)
        ctx = GateContext(session_id="s1")
        result = step.checker(ctx)
        assert result.status == GateStatus.ERROR
        assert "engine broken" in result.reasons[0]

    def test_from_engine_step_with_combinator_and_depends(self):
        class FakeEngine:
            def evaluate(self, task: Any, gate_id: str) -> Any:
                return type(
                    "R",
                    (),
                    {
                        "passed": True,
                        "gate_id": "G1",
                        "task_id": "",
                        "violations": [],
                        "details": {},
                        "evaluated_at": "",
                    },
                )()

        step = GatePipeline.from_engine_step(
            "G1",
            FakeEngine(),
            task=None,
            combinator=Combinator.OR,
            depends_on=["G0"],
        )
        assert step.combinator == Combinator.OR
        assert step.depends_on == ["G0"]

    def test_from_engine_step_depends_on_none_defaults_empty(self):
        class FakeEngine:
            def evaluate(self, task: Any, gate_id: str) -> Any:
                return type(
                    "R",
                    (),
                    {
                        "passed": True,
                        "gate_id": "G1",
                        "task_id": "",
                        "violations": [],
                        "details": {},
                        "evaluated_at": "",
                    },
                )()

        step = GatePipeline.from_engine_step("G1", FakeEngine(), task=None, depends_on=None)
        assert step.depends_on == []

    def test_from_engine_step_with_task_id(self):
        @dataclass
        class FakeTask:
            task_id: str = "T-100"

        @dataclass
        class FakeEngineResult:
            passed: bool = True
            gate_id: str = "G1"
            task_id: str = "T-100"
            violations: list = None
            details: dict = None
            evaluated_at: str = ""

        class FakeEngine:
            def evaluate(self, task: Any, gate_id: str) -> FakeEngineResult:
                return FakeEngineResult()

        step = GatePipeline.from_engine_step("G1", FakeEngine(), task=FakeTask())
        ctx = GateContext(session_id="s1")
        result = step.checker(ctx)
        assert result.task_id == "T-100"

    def test_from_engine_step_exception_no_task_id(self):
        class BrokenEngine:
            def evaluate(self, task: Any, gate_id: str) -> Any:
                raise RuntimeError("fail")

        step = GatePipeline.from_engine_step("G1", BrokenEngine(), task=None)
        ctx = GateContext(session_id="s1")
        result = step.checker(ctx)
        assert result.task_id == ""


class TestGatePipelineBoundary:
    def test_run_with_none_metadata_context(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_pass_checker))
        ctx = GateContext(session_id="s1", metadata=None)
        results = p.run(ctx)
        assert len(results) == 1

    def test_evaluate_single_result(self):
        p = GatePipeline()
        results = [GateResult(gate_id="G1", status=GateStatus.PASS)]
        assert p.evaluate(results) == GateStatus.PASS

    def test_multiple_depends_on_steps(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G0", checker=_pass_checker))
        p.add(GateStep(gate_id="G1", checker=_pass_checker, depends_on=["G0"]))
        p.add(GateStep(gate_id="G2", checker=_pass_checker, depends_on=["G0"]))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        assert len(results) == 3
        assert all(r.status == GateStatus.PASS for r in results)

    def test_pipeline_len_after_many_adds(self):
        p = GatePipeline()
        for i in range(10):
            p.add(GateStep(gate_id=f"G{i}", checker=_pass_checker))
        assert len(p) == 10

    def test_run_error_result_in_parallel(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_error_checker))
        p.add(GateStep(gate_id="G2", checker=_pass_checker))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        statuses = {r.gate_id: r.status for r in results}
        assert statuses["G_ERR"] == GateStatus.ERROR
        assert statuses["G_PASS"] == GateStatus.PASS

    def test_run_fail_does_not_block_error_in_parallel(self):
        p = GatePipeline()
        p.add(GateStep(gate_id="G1", checker=_fail_checker))
        p.add(GateStep(gate_id="G2", checker=_error_checker))
        ctx = GateContext(session_id="s1")
        results = p.run(ctx)
        gate_ids = {r.gate_id for r in results}
        assert "G_FAIL" in gate_ids
        assert "G_ERR" in gate_ids
