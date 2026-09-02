# [BLUEPRINT] MOD-BT-027 | docs/03_modules/_domain_backtest/layered_validation_pipeline/blueprint.md | §test
# [MODULE] tests.backtest.test_layered_validation_pipeline
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.services.layered_validation_pipeline
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_layered_validation_pipeline.py
# [A_test] module_id: MOD-BT-027 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-BT-027 单元测试: C-003 自动回测与仿真分层验证管道。

覆盖: 层计划映射（§20.7.1）、未知 kind/空 id/runner 缺失 Fail-Closed、层层递进
不可跳级（失败中止剩余 not_run）、runner 异常记 error 层失败、过拟合门禁否决/
未配置、归档成功/失败留痕不吞裁决、端到端 提交→分层→门禁→归档。
"""

from __future__ import annotations

import pytest

from zephyr.backtest.services.layered_validation_pipeline import (
    SUBJECT_LAYER_PLAN,
    LayeredValidationError,
    LayeredValidationReport,
    LayerResult,
    ValidationSubmission,
    run_layered_validation,
)


def _sub(kind: str = "strategy", sid: str = "strat_alpha_001") -> ValidationSubmission:
    return ValidationSubmission(subject_kind=kind, subject_id=sid)


def _ok_runner(metrics_key: str = "sharpe"):
    def runner(submission: ValidationSubmission, layer: str) -> LayerResult:
        return LayerResult(layer=layer, passed=True, metrics={metrics_key: 1.5}, detail=f"{layer} 通过")

    return runner


def _fail_runner(layer_seen: list[str]):
    def runner(submission: ValidationSubmission, layer: str) -> LayerResult:
        layer_seen.append(layer)
        return LayerResult(layer=layer, passed=False, metrics={}, detail=f"{layer} 未达标")

    return runner


class TestSubmissionAndPlan:
    def test_layer_plan_mapping(self) -> None:
        assert SUBJECT_LAYER_PLAN["factor"] == ("V1",)
        assert SUBJECT_LAYER_PLAN["signal"] == ("V2", "V5")
        assert SUBJECT_LAYER_PLAN["strategy"] == ("V3",)
        assert SUBJECT_LAYER_PLAN["pipeline"] == ("V4",)

    def test_unknown_kind_fail_closed(self) -> None:
        with pytest.raises(LayeredValidationError):
            run_layered_validation(_sub(kind="unknown"), layer_runners={})

    def test_empty_subject_id_fail_closed(self) -> None:
        with pytest.raises(LayeredValidationError):
            run_layered_validation(_sub(sid="  "), layer_runners={"V3": _ok_runner()})

    def test_non_submission_fail_closed(self) -> None:
        with pytest.raises(LayeredValidationError):
            run_layered_validation({"kind": "strategy"}, layer_runners={})  # type: ignore[arg-type]

    def test_missing_runner_fail_closed(self) -> None:
        with pytest.raises(LayeredValidationError):
            run_layered_validation(_sub("signal"), layer_runners={"V2": _ok_runner()})  # 缺 V5


class TestProgressiveExecution:
    def test_all_pass_no_gate_no_sink(self) -> None:
        report = run_layered_validation(_sub("strategy"), layer_runners={"V3": _ok_runner()})
        assert isinstance(report, LayeredValidationReport)
        assert report.passed is True
        assert report.layers_planned == ("V3",)
        assert len(report.layer_results) == 1
        assert report.layer_results[0].status == "passed"
        assert report.layer_results[0].metrics == {"sharpe": 1.5}
        assert report.gate_status == "not_configured"
        assert report.is_overfitting is False
        assert report.archive_status == "not_configured"

    def test_layer_fail_halts_remaining_not_run(self) -> None:
        seen: list[str] = []
        report = run_layered_validation(
            _sub("signal"),
            layer_runners={"V2": _fail_runner(seen), "V5": _ok_runner()},
        )
        assert report.passed is False
        assert seen == ["V2"]  # V2 失败即中止，V5 未执行
        statuses = {r.layer: r.status for r in report.layer_results}
        assert statuses == {"V2": "failed", "V5": "not_run"}

    def test_runner_exception_marks_error_and_halts(self) -> None:
        def boom(submission: ValidationSubmission, layer: str) -> LayerResult:
            raise RuntimeError("引擎崩溃")

        report = run_layered_validation(_sub("signal"), layer_runners={"V2": boom, "V5": _ok_runner()})
        assert report.passed is False
        statuses = {r.layer: r.status for r in report.layer_results}
        assert statuses == {"V2": "error", "V5": "not_run"}
        assert any("引擎崩溃" in r.detail for r in report.layer_results)

    def test_runner_bad_return_fail_closed(self) -> None:
        def bad(submission: ValidationSubmission, layer: str):
            return {"layer": layer, "passed": True}

        with pytest.raises(LayeredValidationError):
            run_layered_validation(_sub("strategy"), layer_runners={"V3": bad})


class TestOverfittingGate:
    def test_gate_veto(self) -> None:
        def gate(submission: ValidationSubmission, results: tuple[LayerResult, ...]) -> dict:
            return {"is_overfitting": True, "reasons": ["IS/OOS Sharpe 衰减>50%"]}

        report = run_layered_validation(_sub("strategy"), layer_runners={"V3": _ok_runner()}, overfitting_gate=gate)
        assert report.passed is False
        assert report.gate_status == "evaluated"
        assert report.is_overfitting is True
        assert any("过拟合" in r for r in report.reasons)

    def test_gate_pass(self) -> None:
        def gate(submission: ValidationSubmission, results: tuple[LayerResult, ...]) -> dict:
            return {"is_overfitting": False, "reasons": []}

        report = run_layered_validation(_sub("strategy"), layer_runners={"V3": _ok_runner()}, overfitting_gate=gate)
        assert report.passed is True
        assert report.gate_status == "evaluated"

    def test_gate_bad_return_fail_closed(self) -> None:
        def bad_gate(submission: ValidationSubmission, results: tuple[LayerResult, ...]) -> dict:
            return {"verdict": "ok"}  # 缺 is_overfitting

        with pytest.raises(LayeredValidationError):
            run_layered_validation(_sub("strategy"), layer_runners={"V3": _ok_runner()}, overfitting_gate=bad_gate)

    def test_gate_not_called_when_layer_failed(self) -> None:
        called: list[bool] = []

        def gate(submission: ValidationSubmission, results: tuple[LayerResult, ...]) -> dict:
            called.append(True)
            return {"is_overfitting": False, "reasons": []}

        seen: list[str] = []
        report = run_layered_validation(
            _sub("signal"),
            layer_runners={"V2": _fail_runner(seen), "V5": _ok_runner()},
            overfitting_gate=gate,
        )
        assert report.passed is False
        assert called == []  # 层失败短路，不再跑过拟合门禁
        assert report.gate_status == "skipped_layer_failure"


class TestArchive:
    def test_archive_success(self) -> None:
        archived: list[LayeredValidationReport] = []
        report = run_layered_validation(
            _sub("strategy"),
            layer_runners={"V3": _ok_runner()},
            report_sink=archived.append,
        )
        assert report.archive_status == "archived"
        assert len(archived) == 1
        assert archived[0].subject_id == "strat_alpha_001"

    def test_archive_failure_preserves_verdict(self) -> None:
        def bad_sink(report: LayeredValidationReport) -> None:
            raise OSError("磁盘满")

        report = run_layered_validation(
            _sub("strategy"),
            layer_runners={"V3": _ok_runner()},
            report_sink=bad_sink,
        )
        assert report.passed is True  # 裁决不被归档失败吞掉
        assert report.archive_status == "archive_failed"
        assert any("归档失败" in r for r in report.reasons)

    def test_end_to_end_full_chain(self) -> None:
        archived: list[LayeredValidationReport] = []

        def gate(submission: ValidationSubmission, results: tuple[LayerResult, ...]) -> dict:
            return {"is_overfitting": False, "reasons": []}

        report = run_layered_validation(
            _sub("pipeline", "pipe_daily_001"),
            layer_runners={"V4": _ok_runner()},
            overfitting_gate=gate,
            report_sink=archived.append,
        )
        assert report.passed is True
        assert report.gate_status == "evaluated"
        assert report.archive_status == "archived"
        assert archived[0].layers_planned == ("V4",)
