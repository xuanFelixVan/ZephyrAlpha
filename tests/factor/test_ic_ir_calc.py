# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""ic_ir_calc 模块测试——批量 IC/IR 计算器。"""
from __future__ import annotations

import pandas as pd
import pytest

from zephyr.factor.analysis import ic_ir_calc
from zephyr.factor.core.evaluation.backtest import EvaluationResult


def _make_result(fid: str, ic: float = 0.05, ir: float = 0.6) -> EvaluationResult:
    return EvaluationResult(
        factor_id=fid, ic_mean=ic, ic_std=0.1, ir=ir,
        oos_positive_rate=0.55, is_overfitted=False, sample_size=50,
    )


class TestComputeIcIrTable:
    def test_empty_factor_ids(self) -> None:
        df = ic_ir_calc.compute_ic_ir_table([], ["000001"], "2026-01-01", "2026-06-01")
        assert df.empty

    def test_multiple_factors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        results = {
            "mom_5d": _make_result("mom_5d", 0.08, 0.7),
            "value_5d": _make_result("value_5d", 0.03, 0.4),
        }
        monkeypatch.setattr(
            ic_ir_calc, "evaluate_factor",
            lambda fid, *a, **kw: results[fid],
        )
        df = ic_ir_calc.compute_ic_ir_table(
            ["mom_5d", "value_5d"], ["000001"], "2026-01-01", "2026-06-01",
        )
        assert len(df) == 2
        assert set(df["factor_id"]) == {"mom_5d", "value_5d"}
        assert df.loc[df["factor_id"] == "mom_5d", "ic_mean"].iloc[0] == 0.08

    def test_unregistered_factor(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _raise_keyerror(fid, *a, **kw):
            raise KeyError(fid)
        monkeypatch.setattr(ic_ir_calc, "evaluate_factor", _raise_keyerror)
        df = ic_ir_calc.compute_ic_ir_table(
            ["unknown"], ["000001"], "2026-01-01", "2026-06-01",
        )
        assert len(df) == 1
        assert df.iloc[0]["ic_mean"] == 0.0
        assert bool(df.iloc[0]["is_overfitted"]) is True

    def test_evaluation_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _raise_error(fid, *a, **kw):
            raise RuntimeError("db error")
        monkeypatch.setattr(ic_ir_calc, "evaluate_factor", _raise_error)
        df = ic_ir_calc.compute_ic_ir_table(
            ["bad"], ["000001"], "2026-01-01", "2026-06-01",
        )
        assert len(df) == 1
        assert df.iloc[0]["sample_size"] == 0

    def test_columns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            ic_ir_calc, "evaluate_factor",
            lambda fid, *a, **kw: _make_result(fid),
        )
        df = ic_ir_calc.compute_ic_ir_table(
            ["f1"], ["000001"], "2026-01-01", "2026-06-01",
        )
        expected_cols = {
            "factor_id", "ic_mean", "ic_std", "ir",
            "oos_positive_rate", "is_overfitted", "sample_size",
        }
        assert set(df.columns) == expected_cols
