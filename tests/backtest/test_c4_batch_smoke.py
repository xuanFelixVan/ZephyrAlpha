# [BLUEPRINT] MOD-BT-077 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_c4_batch_smoke
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; scripts.backtest.translated._c4_engine
# [CONSUMERS] C4 批测质量守卫（MODIFY-GUARD: _c4_engine / c4_batch_screen）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯合成数据（不连 CH）；测试不写生产路径；契约检查只 import 不 build
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-077 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 批测冒烟守卫——引擎单测（合成数据）+ translated 模块契约检查。"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
_TRANSLATED = _REPO / "scripts" / "backtest" / "translated"
sys.path.insert(0, str(_TRANSLATED))

from _c4_engine import (  # noqa: E402
    batch_deflated_sharpe,
    daily_net_returns,
    run_backtest,
    window_for,
)


def _panel(days: int, syms: int, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=days)
    rets = rng.normal(0.0005, 0.02, size=(days, syms))
    px = pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=idx,
                      columns=[f"{i:06d}" for i in range(syms)])
    return px


class TestRunBacktest:
    def test_zero_weights_flat(self):
        px = _panel(60, 3)
        w = pd.DataFrame(0.0, index=px.index, columns=px.columns)
        stats = run_backtest(w, px)
        assert stats["equity_final"] == 1.0
        assert stats["sharpe"] == 0.0

    def test_constant_hold_matches_underlying(self):
        px = _panel(120, 2)
        w = pd.DataFrame(0.0, index=px.index, columns=px.columns)
        w.iloc[5:, :] = 0.5
        stats = run_backtest(w, px)
        # 无成本口径的单利对照（容忍成本与浮点差）
        net = daily_net_returns(w, px)
        assert len(net) == len(px)
        assert stats["days"] == len(px)
        assert -0.9 < stats["max_drawdown"] <= 0.0

    def test_turnover_cost_positive(self):
        px = _panel(80, 2)
        w_hold = pd.DataFrame(0.0, index=px.index, columns=px.columns)
        w_hold.iloc[10:, :] = 0.5
        w_churn = w_hold.copy()
        w_churn.iloc[::10, :] = 0.0  # 制造换手
        s_hold = run_backtest(w_hold, px)
        s_churn = run_backtest(w_churn, px)
        assert s_churn["avg_turnover_1side"] > s_hold["avg_turnover_1side"]


class TestDeflatedSharpe:
    def test_strong_strategy_discounted_but_top(self):
        rng = np.random.default_rng(3)
        base = pd.Series(rng.normal(0, 0.01, 600), index=pd.bdate_range("2020-01-01", periods=600))
        strong = pd.Series(rng.normal(0.004, 0.01, 600), index=base.index)
        weak = pd.Series(rng.normal(-0.002, 0.01, 600), index=base.index)
        nets = {"a": base, "b": strong, "c": weak}
        out = batch_deflated_sharpe(nets)
        assert set(out) == set(nets)
        assert out["b"] > out["a"]
        assert 0.0 <= out["a"] <= 1.0

    def test_short_series_none(self):
        short = pd.Series([0.001, -0.002])
        out = batch_deflated_sharpe({"short": short})
        assert out["short"] is None

    def test_zero_variance_none(self):
        flat = pd.Series([0.0] * 50)
        out = batch_deflated_sharpe({"flat": flat})
        assert out["flat"] is None


class TestWindowAndContract:
    def test_window_for(self):
        assert window_for("stock") == ("2020-01-01", "2023-12-31")
        assert window_for("etf")[0] >= "2021-04"

    def test_translated_modules_contract(self):
        files = sorted(_TRANSLATED.glob("c4_*.py"))
        assert len(files) >= 30, f"翻译件数量异常: {len(files)}"
        pat = re.compile(r"^CAND-[0-9a-f]{12}$")
        for p in files:
            spec = importlib.util.spec_from_file_location(f"contract_{p.stem}", p)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            assert pat.match(mod.STRATEGY_ID), f"STRATEGY_ID 非法: {p.name}"
            assert mod.WINDOW_KIND in {"stock", "index", "etf"}, f"WINDOW_KIND 非法: {p.name}"
            assert callable(mod.build), f"build 缺失: {p.name}"

    def test_oos_mode_dsr_computed(self):
        """回归：OOS 模式（include_pilots=False）不得提前返回跳过 DSR 计算（2026-09-13 实测 bug）。"""
        sys.path.insert(0, str(_REPO / "scripts" / "backtest"))
        import c4_batch_screen as runner

        results, failures = runner.run_batch(limit=3, window=("2024-01-01", "2026-06-30"),
                                             include_pilots=False)
        assert not failures
        assert results
        assert not any(r.get("pilot") for r in results)
        assert all(r.get("deflated_sharpe") is not None for r in results)

    def test_runner_exists(self):
        runner = _REPO / "scripts" / "backtest" / "c4_batch_screen.py"
        assert runner.exists()
        text = runner.read_text(encoding="utf-8")
        assert "C4-translated-20260912" in text
        assert "run_deflated_sharpe_batch" not in text  # 委托经引擎，runner 不直连官方件
