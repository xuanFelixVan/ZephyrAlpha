# [A_test] module_id=MOD-TEST-market-quality-validator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain-data/datasource-core/blueprint.md | §quality_gate
# [MODULE] tests.data.test_market_quality_validator
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.quality_gate
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 四门禁：异常行置 quality_flag=0，通过行保持 1；非 OHLC 表跳过
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound
"""#ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测试。"""

from __future__ import annotations

from decimal import Decimal

from zephyr.gov_enforcement.rule_enforcement.quality_gate import (
    MarketDataValidator,
    _gate_adjustment,
    _gate_ohlc_logic,
    _gate_price_change,
    _gate_swing,
    _to_decimal,
    apply_quality_gate,
)


class TestGateOhlcLogic:
    def test_valid_ohlc(self):
        assert _gate_ohlc_logic(Decimal("10"), Decimal("11"), Decimal("9.5"), Decimal("10.5"))

    def test_high_below_close(self):
        assert not _gate_ohlc_logic(Decimal("10"), Decimal("9"), Decimal("9.5"), Decimal("10.5"))

    def test_low_above_open(self):
        assert not _gate_ohlc_logic(Decimal("10"), Decimal("11"), Decimal("10.5"), Decimal("10.5"))

    def test_negative_price(self):
        assert not _gate_ohlc_logic(Decimal("-1"), Decimal("11"), Decimal("9"), Decimal("10"))

    def test_zero_price(self):
        assert not _gate_ohlc_logic(Decimal("0"), Decimal("11"), Decimal("9"), Decimal("10"))

    def test_none_value(self):
        assert not _gate_ohlc_logic(None, Decimal("11"), Decimal("9"), Decimal("10"))

    def test_equal_ohlc(self):
        # 全平（停牌一字）应通过
        assert _gate_ohlc_logic(Decimal("10"), Decimal("10"), Decimal("10"), Decimal("10"))


class TestGatePriceChange:
    def test_within_limit(self):
        assert _gate_price_change(Decimal("10"), Decimal("11"), None, Decimal("0.20"))

    def test_beyond_limit(self):
        assert not _gate_price_change(Decimal("10"), Decimal("15"), None, Decimal("0.20"))

    def test_uses_prev_close(self):
        # open=10 close=10.5，但 prev_close=8 → 涨幅 31% 超限
        assert not _gate_price_change(Decimal("10"), Decimal("10.5"), Decimal("8"), Decimal("0.20"))

    def test_no_ref_passes(self):
        # 无基准（open=0 且无 prev_close）保守放行
        assert _gate_price_change(Decimal("0"), Decimal("10"), None, Decimal("0.20"))

    def test_close_none_passes(self):
        assert _gate_price_change(Decimal("10"), None, None, Decimal("0.20"))


class TestGateSwing:
    def test_normal_range(self):
        assert _gate_swing(Decimal("10"), Decimal("10.5"), Decimal("9.8"), Decimal("0.30"))

    def test_implausibly_wide(self):
        # (11-1)/10 = 1.0 > 0.30
        assert not _gate_swing(Decimal("10"), Decimal("11"), Decimal("1"), Decimal("0.30"))

    def test_no_open_passes(self):
        assert _gate_swing(Decimal("0"), Decimal("11"), Decimal("9"), Decimal("0.30"))

    def test_none_passes(self):
        assert _gate_swing(None, Decimal("11"), Decimal("9"), Decimal("0.30"))


class TestGateAdjustment:
    def test_valid_factor(self):
        assert _gate_adjustment(Decimal("1.5"), Decimal("1000"))

    def test_zero_factor(self):
        assert not _gate_adjustment(Decimal("0"), Decimal("1000"))

    def test_negative_factor(self):
        assert not _gate_adjustment(Decimal("-1"), Decimal("1000"))

    def test_huge_factor(self):
        assert not _gate_adjustment(Decimal("100000"), Decimal("1000"))

    def test_none_passes(self):
        assert _gate_adjustment(None, Decimal("1000"))


class TestToDecimal:
    def test_int(self):
        assert _to_decimal(10) == Decimal("10")

    def test_float(self):
        assert _to_decimal(10.5) == Decimal("10.5")

    def test_string(self):
        assert _to_decimal("10.5") == Decimal("10.5")

    def test_none(self):
        assert _to_decimal(None) is None

    def test_nan(self):
        assert _to_decimal(float("nan")) is None

    def test_invalid(self):
        assert _to_decimal("abc") is None


class TestApplyQualityGate:
    COLS = ["symbol", "trade_date", "open", "high", "low", "close", "volume", "quality_flag"]

    def _row(self, o, h, l, c, qf=1):
        return ("000001", "2026-07-23", o, h, l, c, 1000, qf)

    def test_all_valid_no_flag(self):
        rows = [self._row(10, 10.5, 9.8, 10.2)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["flagged"] == 0
        assert stats["checked"] == 1
        assert out[0][7] == 1  # quality_flag unchanged

    def test_bad_ohlc_flagged(self):
        rows = [self._row(10, 9, 9.5, 10.5)]  # high < close
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["flagged"] == 1
        assert stats["by_gate"]["ohlc"] == 1
        assert out[0][7] == 0  # quality_flag set to 0

    def test_negative_price_flagged(self):
        rows = [self._row(-1, 10, 9, 10)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["flagged"] == 1
        assert out[0][7] == 0

    def test_huge_swing_flagged(self):
        rows = [self._row(10, 100, 1, 10)]  # (100-1)/10 = 9.9 > 0.30
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["flagged"] == 1

    def test_mixed_rows(self):
        rows = [
            self._row(10, 10.5, 9.8, 10.2),  # valid
            self._row(10, 9, 9.5, 10.5),  # bad ohlc
            self._row(10, 10.5, 9.8, 10.2),  # valid
        ]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["flagged"] == 1
        assert out[0][7] == 1
        assert out[1][7] == 0
        assert out[2][7] == 1

    def test_non_ohlc_table_skipped(self):
        cols = ["symbol", "name", "industry"]
        rows = [("000001", "平安银行", "银行")]
        out, stats = apply_quality_gate("stock_list", cols, rows)
        assert stats["checked"] == 0
        assert stats["flagged"] == 0
        assert out is rows  # 原样返回

    def test_column_alias_detection(self):
        cols = ["sym", "dt", "open_price", "high_price", "low_price", "close_price", "qf"]
        rows = [("000001", "2026-07-23", 10, 9, 9.5, 10.5, 1)]  # bad ohlc
        out, stats = apply_quality_gate("kline_x", cols, rows)
        assert stats["checked"] == 1
        assert stats["flagged"] == 1
        assert out[0][6] == 0  # qf column

    def test_adj_factor_column(self):
        cols = ["sym", "open", "high", "low", "close", "adj_factor", "quality_flag"]
        rows = [("000001", 10, 10.5, 9.8, 10.2, -1, 1)]  # bad adj
        out, stats = apply_quality_gate("kline_hfq", cols, rows)
        assert stats["by_gate"]["adj"] == 1
        assert out[0][6] == 0

    def test_tuple_preserved(self):
        rows = [self._row(10, 10.5, 9.8, 10.2)]
        out, _ = apply_quality_gate("kline_daily", self.COLS, rows)
        assert isinstance(out[0], tuple)

    def test_list_preserved(self):
        rows = [list(self._row(10, 10.5, 9.8, 10.2))]
        out, _ = apply_quality_gate("kline_daily", self.COLS, rows)
        assert isinstance(out[0], list)

    def test_prev_close_used(self):
        cols = ["sym", "open", "high", "low", "close", "prev_close", "quality_flag"]
        # open=10 close=10.5 prev_close=8 → 31% 涨幅超 20% 限
        rows = [("000001", 10, 10.5, 9.8, 10.5, 8, 1)]
        out, stats = apply_quality_gate("kline_daily", cols, rows)
        assert stats["by_gate"]["change"] == 1
        assert out[0][6] == 0

    def test_no_quality_flag_column(self):
        # 无 quality_flag 列时，异常行仍被统计但无法置 0
        cols = ["sym", "open", "high", "low", "close"]
        rows = [("000001", 10, 9, 9.5, 10.5)]
        out, stats = apply_quality_gate("kline_daily", cols, rows)
        assert stats["flagged"] == 1
        assert len(out[0]) == 5  # 行不变

    def test_empty_rows(self):
        out, stats = apply_quality_gate("kline_daily", self.COLS, [])
        assert stats["total"] == 0
        assert stats["checked"] == 0

    def test_validator_custom_limits(self):
        v = MarketDataValidator(change_limit=Decimal("0.05"))
        # 涨幅 10% 超 5% 限
        rows = [self._row(10, 11, 9.8, 11)]
        _, stats = apply_quality_gate("kline_daily", self.COLS, rows, validator=v)
        assert stats["by_gate"]["change"] == 1


class TestInferChangeLimit:
    """#209③：板块前缀→涨跌幅门禁阈值推断（口径对齐 matching_engine._infer_limit_pct）。"""

    def test_bj_prefixes_30pct(self):
        from zephyr.gov_enforcement.rule_enforcement.quality_gate import _infer_change_limit

        for sym in ("430047", "830799", "920001", "430047.BJ", "8A0000"):
            assert _infer_change_limit(sym, Decimal("0.20")) == Decimal("0.30")

    def test_kcb_cyb_20pct(self):
        from zephyr.gov_enforcement.rule_enforcement.quality_gate import _infer_change_limit

        assert _infer_change_limit("688001", Decimal("0.20")) == Decimal("0.20")
        assert _infer_change_limit("300750.SZ", Decimal("0.20")) == Decimal("0.20")

    def test_mainboard_10pct(self):
        from zephyr.gov_enforcement.rule_enforcement.quality_gate import _infer_change_limit

        assert _infer_change_limit("600519", Decimal("0.20")) == Decimal("0.10")
        assert _infer_change_limit("000001.SH", Decimal("0.20")) == Decimal("0.10")

    def test_unrecognized_falls_back_default(self):
        from zephyr.gov_enforcement.rule_enforcement.quality_gate import _infer_change_limit

        assert _infer_change_limit("00700", Decimal("0.20")) == Decimal("0.20")  # 港股 5 位
        assert _infer_change_limit(None, Decimal("0.20")) == Decimal("0.20")
        assert _infer_change_limit("", Decimal("0.20")) == Decimal("0.20")
        assert _infer_change_limit("ABC", Decimal("0.15")) == Decimal("0.15")  # 回退传入默认


class TestBoardAwareChangeGate:
    """#209③：默认 validator + symbol 列时按板块推断涨跌幅阈值。"""

    COLS = ["symbol", "trade_date", "open", "high", "low", "close", "prev_close", "quality_flag"]

    def _row(self, symbol, o, h, l, c, pc, qf=1):
        return (symbol, "2026-08-20", o, h, l, c, pc, qf)

    def test_bj_25pct_legit_not_flagged(self):
        """北交所 +25%（±30% 内合法）原一刀切 0.20 误标，修复后放行。"""
        rows = [self._row("830799", 10, 12.6, 9.9, 12.5, 10)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["by_gate"]["change"] == 0
        assert stats["flagged"] == 0
        assert out[0][7] == 1

    def test_bj_over_30pct_flagged(self):
        """北交所 +31% 超 ±30% 仍判异常。"""
        rows = [self._row("920001", 10, 13.2, 9.9, 13.1, 10)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["by_gate"]["change"] == 1
        assert out[0][7] == 0

    def test_kcb_25pct_flagged(self):
        """科创板 +25% 超 ±20% 判异常。"""
        rows = [self._row("688001", 10, 12.6, 9.9, 12.5, 10)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["by_gate"]["change"] == 1
        assert out[0][7] == 0

    def test_cyb_within_20pct_passes(self):
        """创业板 +19%（±20% 内）放行。"""
        rows = [self._row("300750", 10, 12.0, 9.9, 11.9, 10)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["flagged"] == 0

    def test_mainboard_15pct_flagged(self):
        """主板 +15% 超 ±10% 判异常（原 0.20 会放行，板块推断后收紧）。"""
        rows = [self._row("600519", 10, 11.6, 9.9, 11.5, 10)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["by_gate"]["change"] == 1
        assert out[0][7] == 0

    def test_mainboard_exactly_10pct_passes(self):
        """主板恰好 +10%（涨停边界）放行。"""
        rows = [self._row("000001", 10, 11.0, 9.9, 11.0, 10)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["by_gate"]["change"] == 0

    def test_ts_code_suffix_bj(self):
        """带交易所后缀的 ts_code（430047.BJ）同样识别北交所。"""
        rows = [self._row("430047.BJ", 10, 12.9, 9.9, 12.8, 10)]
        out, stats = apply_quality_gate("kline_daily", self.COLS, rows)
        assert stats["by_gate"]["change"] == 0

    def test_unknown_symbol_uses_default(self):
        """无法识别板块（港股 5 位代码）回退默认 0.20：+15% 放行。"""
        rows = [self._row("00700", 10, 11.6, 9.9, 11.5, 10)]
        out, stats = apply_quality_gate("kline_hk", self.COLS, rows)
        assert stats["by_gate"]["change"] == 0

    def test_no_symbol_column_flat_default(self):
        """无 symbol 列时维持原一刀切默认 0.20（+15% 放行）。"""
        cols = ["open", "high", "low", "close", "prev_close", "quality_flag"]
        rows = [(10, 11.6, 9.9, 11.5, 10, 1)]
        out, stats = apply_quality_gate("kline_daily", cols, rows)
        assert stats["by_gate"]["change"] == 0

    def test_custom_change_limit_disables_inference(self):
        """显式自定义 change_limit=调用方接管：主板 +7% 在 0.05 下一刀切判异
        （若被板块推断覆盖为 0.10 则会放行——本用例锁定自定义不被覆盖）。"""
        v = MarketDataValidator(change_limit=Decimal("0.05"))
        rows = [self._row("600519", 10, 10.8, 9.9, 10.7, 10)]
        _, stats = apply_quality_gate("kline_daily", self.COLS, rows, validator=v)
        assert stats["by_gate"]["change"] == 1
