# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""ic_ir_evaluator 模块测试——多因子评估报告器。"""
from __future__ import annotations

import pandas as pd
import pytest

from zephyr.factor.analysis import ic_ir_evaluator
from zephyr.factor.core.evaluation.backtest import EvaluationResult


def _make_result(fid: str, ic: float = 0.05, ir: float = 0.6) -> EvaluationResult:
    return EvaluationResult(
        factor_id=fid, ic_mean=ic, ic_std=0.1, ir=ir,
        oos_positive_rate=0.55, is_overfitted=False, sample_size=50,
    )


class TestEvaluateMultiple:
    def test_empty_factor_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # 空列表不应调用 evaluate_factor
        called: list[str] = []
        monkeypatch.setattr(
            ic_ir_evaluator, "evaluate_factor",
            lambda fid, *a, **kw: called.append(fid) or _make_result(fid),
        )
        results = ic_ir_evaluator.evaluate_multiple(
            [], ["000001"], "2026-01-01", "2026-06-01",
        )
        assert results == {}
        assert called == []

    def test_multiple_factors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mapping = {
            "mom_5d": _make_result("mom_5d", 0.08, 0.7),
            "value_5d": _make_result("value_5d", 0.03, 0.4),
        }
        monkeypatch.setattr(
            ic_ir_evaluator, "evaluate_factor",
            lambda fid, *a, **kw: mapping[fid],
        )
        results = ic_ir_evaluator.evaluate_multiple(
            ["mom_5d", "value_5d"], ["000001"], "2026-01-01", "2026-06-01",
        )
        assert set(results.keys()) == {"mom_5d", "value_5d"}
        assert results["mom_5d"].ic_mean == 0.08
        assert results["value_5d"].ir == 0.4

    def test_unregistered_factor_skipped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _eval(fid, *a, **kw):
            if fid == "unknown":
                raise KeyError(fid)
            return _make_result(fid)

        monkeypatch.setattr(ic_ir_evaluator, "evaluate_factor", _eval)
        results = ic_ir_evaluator.evaluate_multiple(
            ["good", "unknown"], ["000001"], "2026-01-01", "2026-06-01",
        )
        assert "good" in results
        assert "unknown" not in results

    def test_evaluation_failure_skipped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _eval(fid, *a, **kw):
            if fid == "bad":
                raise RuntimeError("db error")
            return _make_result(fid)

        monkeypatch.setattr(ic_ir_evaluator, "evaluate_factor", _eval)
        results = ic_ir_evaluator.evaluate_multiple(
            ["good", "bad"], ["000001"], "2026-01-01", "2026-06-01",
        )
        assert "good" in results
        assert "bad" not in results

    def test_arguments_forwarded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict = {}

        def _eval(fid, symbols, start, end, horizon, oos_ratio):
            captured.update(
                fid=fid, symbols=symbols, start=start, end=end,
                horizon=horizon, oos_ratio=oos_ratio,
            )
            return _make_result(fid)

        monkeypatch.setattr(ic_ir_evaluator, "evaluate_factor", _eval)
        ic_ir_evaluator.evaluate_multiple(
            ["f1"], ["000001", "000002"], "2026-01-01", "2026-06-30",
            horizon=10, oos_ratio=0.4,
        )
        assert captured["fid"] == "f1"
        assert captured["symbols"] == ["000001", "000002"]
        assert captured["start"] == "2026-01-01"
        assert captured["end"] == "2026-06-30"
        assert captured["horizon"] == 10
        assert captured["oos_ratio"] == 0.4


class TestFormatReport:
    def test_empty_results(self) -> None:
        report = ic_ir_evaluator.format_report({})
        assert report == "（无评估结果）"

    def test_single_factor_report(self) -> None:
        results = {"f1": _make_result("f1", 0.05, 0.6)}
        report = ic_ir_evaluator.format_report(results)
        assert "多因子评估报告" in report
        assert "f1" in report
        assert "0.0500" in report
        # 非过拟合应显示"否"
        assert "否" in report

    def test_overfitted_flag_display(self) -> None:
        overfitted = EvaluationResult(
            factor_id="f2", ic_mean=0.02, ic_std=0.1, ir=0.2,
            oos_positive_rate=0.3, is_overfitted=True, sample_size=30,
        )
        results = {"f2": overfitted}
        report = ic_ir_evaluator.format_report(results)
        assert "是" in report

    def test_multiple_factors_sorted(self) -> None:
        results = {
            "zzz": _make_result("zzz", 0.01),
            "aaa": _make_result("aaa", 0.09),
        }
        report = ic_ir_evaluator.format_report(results)
        # sorted 按 factor_id 升序，aaa 应在 zzz 之前
        assert report.index("aaa") < report.index("zzz")

    def test_report_structure(self) -> None:
        results = {"f1": _make_result("f1")}
        report = ic_ir_evaluator.format_report(results)
        lines = report.split("\n")
        # 首尾应为分隔线
        assert lines[0] == "=" * 78
        assert lines[1] == "多因子评估报告"
        assert lines[2] == "=" * 78
        assert "-" * 78 in lines
        assert lines[-1] == "=" * 78
