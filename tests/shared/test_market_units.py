# [A_test] module_id: MOD-GOV_market_units | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.shared.test_market_units
# [DOMAIN] D_SHARED
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/shared/test_market_units.py
# [TTL] task_bound
"""车道 K P0-1/P0-2 公共量纲件回归锁（`zephyr.shared.utils.market_units`）。

覆盖：
- P0-1 成交量量纲：`kline_daily.volume` **混存**（主进料=手 / tushare·Baostock=股）
  的逐行自洽探测——单一全局 ×100 会把 5.4% 行错 100 倍，故必须逐行判决；
  不可判定行按同标的主流量纲回填，无先验才退声明口径并计入 `default_applied`+
  `suspect`（显式告警，绝不静默算错）；
- 量价联合不变量：归一后 median(amount/(close×volume)) ≈ 1（绊线）；
- P0-2 复权：后复权真值按**窗口末锚定**（等价窗内前复权）——除权幻影归零、
  价格量级贴近可交易真实价、`close×adj_factor ≡ 后复权真值`；
- 缺因子的两种退化：单日缺→同标的携带补齐（不注入假跳变）；
  整标的缺→全窗退不复权（组内一致，亦不注入假跳变）并计入披露件；
- 纯函数契约：不就地改入参、报告挂 `attrs[REPORT_ATTR]`、`format_report` 可用人读。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.shared.utils.market_units import (
    CONSISTENCY_TOL,
    PRICE_FIELDS,
    REPORT_ATTR,
    SHARES_PER_LOT,
    MarketPanelReport,
    format_report,
    normalize_market_panel,
    probe_volume_unit,
)

_COLS = ["symbol", "trade_date", "open", "high", "low", "close", "volume", "amount"]


def _frame(rows: list[tuple], *, multi_index: bool = False) -> pd.DataFrame:
    """行元组 → 面板（trade_date 统一 datetime；可选 (symbol,trade_date) MultiIndex）。"""
    df = pd.DataFrame(rows, columns=_COLS)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y-%m-%d")
    if multi_index:
        return df.set_index(["symbol", "trade_date"]).sort_index()
    return df


def _lots_rows(symbol="600519", n=3, close=10.0, lots=1000.0):
    """主进料口径：volume=手（amount=close×股数=close×lots×100）。"""
    rows = []
    for i in range(n):
        c = close + i
        shares = lots * SHARES_PER_LOT
        rows.append((symbol, f"2026-01-0{i + 1}", c * 0.98, c * 1.02, c * 0.97, c, lots, c * shares))
    return rows


def _shares_rows(symbol="000001", n=3, close=20.0, shares=50000.0):
    """tushare/Baostock 写入腿口径：volume=股。"""
    rows = []
    for i in range(n):
        c = close + i
        rows.append((symbol, f"2026-01-0{i + 1}", c * 0.98, c * 1.02, c * 0.97, c, shares, c * shares))
    return rows


def _hfq_frame(symbol: str, closes: list[float]) -> pd.DataFrame:
    """后复权收盘价面板（index=(symbol, trade_date)，列 close）。"""
    rows = [(f"2026-01-0{i + 1}", symbol, c) for i, c in enumerate(closes)]
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "close"])
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y-%m-%d")
    return df.set_index(["symbol", "trade_date"]).sort_index()


class TestProbeVolumeUnit:
    def test_lots_rows_detected_as_times_100(self):
        df = _frame(_lots_rows())
        mult, probe = probe_volume_unit(df, groups=df["symbol"])
        assert (mult == SHARES_PER_LOT).all()
        assert probe.suspect is False
        assert probe.counts_by_multiplier[SHARES_PER_LOT] == 3
        assert probe.default_applied == 0

    def test_share_rows_detected_as_times_1(self):
        df = _frame(_shares_rows())
        mult, probe = probe_volume_unit(df, groups=df["symbol"])
        assert (mult == 1.0).all()
        assert probe.counts_by_multiplier[1.0] == 3
        assert probe.suspect is False

    def test_mixed_panel_needs_per_row_decision(self):
        """P0-1 关键回归：混存量纲必须逐行判决——全局 ×100 会错一半的行。"""
        df = _frame(_lots_rows() + _shares_rows())
        mult, probe = probe_volume_unit(df, groups=df["symbol"])
        assert list(mult[df["symbol"] == "600519"]) == [100.0] * 3
        assert list(mult[df["symbol"] == "000001"]) == [1.0] * 3
        assert probe.counts_by_multiplier == {1.0: 3, 100.0: 3}
        assert probe.suspect is False

    def test_unresolvable_row_filled_from_symbol_mode(self):
        """零量日（amount=0 不可判定）按同标的主流量纲回填，而非退回声明口径。"""
        rows = _lots_rows(n=4)
        rows[2] = (*rows[2][:6], 0.0, 0.0)  # 第 3 日零量零额（停牌/半日）
        df = _frame(rows)
        mult, probe = probe_volume_unit(df, groups=df["symbol"])
        assert mult.iloc[2] == SHARES_PER_LOT
        assert probe.chosen_by_fill == 1
        assert probe.default_applied == 0

    def test_no_prior_at_all_declares_default_and_suspect(self):
        """全不可判定（amount 与两种量纲都不自洽）→ 退声明口径 + suspect 告警位。"""
        rows = [(s, f"2026-01-0{i + 1}", 10.0, 11.0, 9.0, 10.0, 1000.0, 5_000_000.0)
                for s in ("A", "B") for i in range(2)]
        df = _frame(rows)
        mult, probe = probe_volume_unit(df, groups=df["symbol"])
        assert (mult == 1.0).all()
        assert probe.default_applied == len(df)
        assert probe.suspect is True

    def test_missing_high_low_uses_ratio_judgement(self):
        """无价界时退化为 amount≈close×volume 判据（仍能区分手/股）。"""
        df = _frame(_lots_rows()).drop(columns=["high", "low"])
        mult, _ = probe_volume_unit(df, groups=df["symbol"])
        assert (mult == SHARES_PER_LOT).all()

    def test_missing_required_column_raises(self):
        df = pd.DataFrame([{"symbol": "A", "close": 1.0}])
        with pytest.raises(KeyError):
            probe_volume_unit(df, groups=df["symbol"])


class TestNormalizeVolume:
    def test_volume_becomes_shares_and_raw_kept(self):
        df = _frame(_lots_rows() + _shares_rows())
        out, report = normalize_market_panel(df)
        assert out.loc[out["symbol"] == "600519", "volume"].tolist() == [100000.0] * 3
        assert out.loc[out["symbol"] == "000001", "volume"].tolist() == [50000.0] * 3
        assert out.loc[out["symbol"] == "600519", "volume_lots"].tolist() == [1000.0] * 3
        assert isinstance(report, MarketPanelReport)
        assert report.volume.suspect is False
        assert report.adjustment_enabled is False

    def test_consistency_invariant_holds(self):
        """归一后 median(amount/(close×volume)) ≈ 1（绊线，越界即 suspect）。"""
        df = _frame(_lots_rows() + _shares_rows())
        out, report = normalize_market_panel(df)
        ratio = out["amount"] / (out["close"] * out["volume"])
        assert abs(float(ratio.median()) - 1.0) < 1e-9
        assert abs(report.volume.consistency_median - 1.0) < CONSISTENCY_TOL

    def test_input_frame_not_mutated(self):
        df = _frame(_lots_rows())
        before = df.copy(deep=True)
        normalize_market_panel(df)
        pd.testing.assert_frame_equal(df, before)

    def test_missing_column_raises(self):
        with pytest.raises(KeyError):
            normalize_market_panel(pd.DataFrame([{"close": 1.0, "volume": 1.0}]))


class TestAdjustment:
    def _exdiv_frames(self, symbol="600519"):
        """10送10 除权：raw close 20→10（幻影 -50%），hfq close 恒 20。"""
        raw_closes = [20.0, 20.0, 20.0, 10.0, 10.0, 10.0]
        # 送转后股数翻倍：raw 手数 1000→2000（主进料=手），amount 恒 2,000,000 元
        lots = [1000.0, 1000.0, 1000.0, 2000.0, 2000.0, 2000.0]
        rows = []
        for i, (c, lv) in enumerate(zip(raw_closes, lots)):
            date = f"2026-01-0{i + 1}"
            rows.append((symbol, date, c * 0.98, c * 1.02, c * 0.97, c, lv, 2_000_000.0))
        df = _frame(rows, multi_index=True)
        adjusted = _hfq_frame(symbol, [20.0] * 6)
        return df, adjusted

    def test_ex_dividend_phantom_return_gone(self):
        """P0-2 主回归：除权日幻影 -50% 归零（对照组仍 -50%）。"""
        df, adjusted = self._exdiv_frames()
        out, report = normalize_market_panel(df, adjusted=adjusted)
        adj_ret = out["close"].pct_change().dropna()
        assert (adj_ret.abs() < 1e-12).all(), f"仍有除权幻影: {adj_ret.tolist()}"
        # 对照组：未归一的 raw close 在同一天必被判为腰斩（证明修复确有必要）
        raw_ret = df["close"].pct_change()
        assert raw_ret.iloc[3] == pytest.approx(-0.5)
        assert report.adjustment_enabled is True
        assert report.symbols == 1
        assert report.unadjusted_rows == 0

    def test_window_end_anchor_keeps_tradable_price_level(self):
        """锚定窗口末：末日价格=真实价（hfq 裸值 20 不退），早期按 k 缩放。"""
        df, adjusted = self._exdiv_frames()
        out, _ = normalize_market_panel(df, adjusted=adjusted)
        assert out["close"].iloc[-1] == pytest.approx(10.0)  # 末日仍贴近真实可交易价
        assert out["close"].iloc[0] == pytest.approx(10.0)  # 20×k(=0.5)
        assert out["close_raw"].iloc[0] == pytest.approx(20.0)
        assert out["volume"].iloc[0] == pytest.approx(1000.0 * 100 / 0.5)

    def test_adj_factor_reproduces_hfq_truth(self):
        """不变量：close × adj_factor == 后复权真值（逐标的常数锚点）。"""
        df, adjusted = self._exdiv_frames()
        out, _ = normalize_market_panel(df, adjusted=adjusted)
        recon = (out["close"] * out["adj_factor"]).rename("adj_close")
        expected = adjusted["close"].rename("adj_close")
        pd.testing.assert_series_equal(recon, expected, atol=1e-9)
        assert (out["adj_factor"] == 2.0).all()

    def test_volume_continuous_across_split_after_normalize(self):
        """量价同缩放：送转后真实股数翻倍，但复权空间成交量逐日不变→参与率不失真。"""
        df, adjusted = self._exdiv_frames()
        out, _ = normalize_market_panel(df, adjusted=adjusted)
        assert np.allclose(out["volume"].to_numpy(), 200000.0)
        ratio = out["amount"] / (out["close"] * out["volume"])
        assert np.allclose(ratio.to_numpy(), 1.0)

    def test_single_missing_factor_day_carried_not_reset(self):
        """单日缺因子：同标的携带补齐（绝不变 1.0 → 否则造出新幻影跳变）。"""
        df, adjusted = self._exdiv_frames()
        adjusted = adjusted.drop(index=adjusted.index[2])
        out, report = normalize_market_panel(df, adjusted=adjusted)
        assert (out["close"].pct_change().fillna(0).abs() < 1e-12).all()
        assert report.carried_rows == 1
        assert report.unadjusted_symbols == 0
        assert np.allclose(out["adj_factor"].to_numpy(), 2.0)  # 缺因子日仍用同标的锚点

    def test_symbol_without_factor_falls_back_wholesale(self):
        """整标的无因子：全窗退不复权（组内一致无假跳变）并显式计数。"""
        df1, adj1 = self._exdiv_frames("600519")
        df2 = _frame(_lots_rows(symbol="000001", n=6, close=15.0), multi_index=True)
        out, report = normalize_market_panel(pd.concat([df1, df2]), adjusted=adj1)
        assert report.unadjusted_symbols == 1
        assert report.unadjusted_rows == 6
        syms = out.index.get_level_values("symbol")
        b = out[syms == "000001"]
        assert np.allclose(b["close"].to_numpy(), b["close_raw"].to_numpy())  # 退不复权
        assert np.allclose(b["adj_factor"].to_numpy(), 1.0)
        a = out[syms == "600519"]
        assert (a["close"].pct_change().fillna(0).abs() < 1e-12).all()  # 有因子腿仍连续

    def test_adjusted_none_keeps_legacy_adj_factor_passthrough(self):
        """无因子源：不动 adj_factor 列（#197 close×adj_factor 语义原样透传）。"""
        df = _frame(_lots_rows(n=2), multi_index=True)
        df["adj_factor"] = [3.0, np.nan]
        out, report = normalize_market_panel(df, adjusted=None)
        assert report.adjustment_enabled is False
        assert out["adj_factor"].iloc[0] == 3.0
        assert pd.isna(out["adj_factor"].iloc[1])
        assert np.allclose(out["close"].to_numpy(), out["close_raw"].to_numpy())


class TestReportPlumbing:
    def test_report_attached_to_attrs(self):
        out, report = normalize_market_panel(_frame(_lots_rows()))
        assert out.attrs[REPORT_ATTR] is report
        d = report.as_dict()
        assert d["volume"]["counts_by_multiplier"]["100.0"] == 3
        assert d["adjustment_enabled"] is False

    def test_format_report_mentions_calibers(self):
        _, report = normalize_market_panel(_frame(_lots_rows() + _shares_rows()))
        line = format_report(report, "load_history")
        assert "load_history" in line
        assert "×100" in line and "×1" in line
        assert "复权[未启用" in line

    def test_format_report_mentions_adjustment(self):
        case = TestAdjustment()
        df, adjusted = case._exdiv_frames()
        _, report = normalize_market_panel(df, adjusted=adjusted)
        line = format_report(report, "load_history")
        assert "复权[已启用" in line and "覆盖=6行" in line

    def test_price_fields_constant(self):
        assert PRICE_FIELDS == ("open", "high", "low", "close")
        assert SHARES_PER_LOT == 100.0
