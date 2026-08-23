# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [TTL] permanent
"""选股漏斗第一层 分级指标过滤（BM-SEL-16，MOD-SIG-046）单元测试——含板块幅度/边界/降级用例。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.tiered_screening_filter import (
    Board,
    TieredFilterConfig,
    TieredFilterRecord,
    filter_tiered,
    is_limit_locked_price,
    limit_pct_for,
)


def _rec(symbol: str, **kw) -> TieredFilterRecord:
    return TieredFilterRecord(symbol=symbol, **kw)


class TestLimitPctFor:
    @pytest.mark.parametrize(
        ("board", "expected"),
        [(Board.MAIN, 0.10), (Board.STAR_CHINEXT, 0.20), (Board.BJ, 0.30), ("MAIN", 0.10)],
    )
    def test_board_limit(self, board, expected):
        assert limit_pct_for(board) == pytest.approx(expected)

    def test_st_main_same_pct_2026_rule(self):
        """2026-07-06 新规：主板 ST ±10% 与主板同幅度。"""
        assert limit_pct_for(Board.MAIN, is_st=True) == pytest.approx(0.10)

    def test_unknown_board_raises(self):
        with pytest.raises(ValueError):
            limit_pct_for("NYSE")


class TestIsLimitLockedPrice:
    def test_limit_up_locked(self):
        assert is_limit_locked_price(11.0, 10.0, 0.10) is True

    def test_limit_down_locked(self):
        assert is_limit_locked_price(9.0, 10.0, 0.10) is True

    def test_normal_move_not_locked(self):
        assert is_limit_locked_price(10.05, 10.0, 0.10) is False

    def test_star_board_15pct_not_locked(self):
        """科创/创业板 ±20% 幅度下 +15% 不算封死。"""
        assert is_limit_locked_price(11.5, 10.0, 0.20) is False

    def test_missing_prev_close_unknown(self):
        assert is_limit_locked_price(11.0, 0.0, 0.10) is None


class TestFilterTiered:
    def test_physical_exclusions(self):
        recs = [
            _rec("LIMIT", close=11.0, prev_close=10.0),  # 主板涨停封死
            _rec("SUSP", is_suspended=True),
            _rec("ST", is_st=True),
            _rec("OK", close=10.2, prev_close=10.0),
        ]
        out = filter_tiered(recs)
        assert out.kept == ("OK",)
        assert out.excluded["LIMIT"] == "physical:limit_locked"
        assert out.excluded["SUSP"] == "physical:suspended"
        assert out.excluded["ST"] == "physical:st"
        assert out.degraded is False

    def test_board_aware_limit(self):
        """同一涨幅在不同板块判定不同：+15% 主板封死、科创未封死。"""
        recs = [
            _rec("M", board="MAIN", close=11.5, prev_close=10.0),
            _rec("S", board="STAR_CHINEXT", close=11.5, prev_close=10.0),
        ]
        out = filter_tiered(recs)
        assert "M" in out.excluded
        assert "S" in out.kept

    def test_gate_tier_prob_exclusions_and_boundary(self):
        recs = [
            _rec("NEW29", list_days=29),
            _rec("NEW30", list_days=30),  # 边界=放行
            _rec("LOWAMT", avg_daily_amount=4_999_999.0),
            _rec("AMTOK", avg_daily_amount=5_000_000.0),  # 边界=放行
            _rec("ABANDON", dealer_abandon_prob=0.96),
            _rec("PROBOK", dealer_abandon_prob=0.95),  # 边界=放行
        ]
        out = filter_tiered(recs)
        assert "NEW29" in out.excluded
        assert "LOWAMT" in out.excluded
        assert "ABANDON" in out.excluded
        assert set(out.kept) == {"NEW30", "AMTOK", "PROBOK"}

    def test_missing_prev_close_not_excluded_by_limit(self):
        """prev_close<=0 → 涨跌停状态不明，不据此排除（其余规则照常）。"""
        out = filter_tiered([_rec("NOPREV", close=0.0, prev_close=0.0)])
        assert out.kept == ("NOPREV",)

    def test_degraded_only_physical(self):
        recs = [
            _rec("LIMIT", close=11.0, prev_close=10.0),
            _rec("SUSP", is_suspended=True),
            _rec("BAD", is_st=True, list_days=1, avg_daily_amount=0.0, dealer_abandon_prob=1.0),
        ]
        out = filter_tiered(recs, degraded=True)
        assert out.degraded is True
        assert out.kept == ("BAD",)
        assert set(out.excluded) == {"LIMIT", "SUSP"}

    def test_custom_config(self):
        cfg = TieredFilterConfig(new_stock_min_list_days=60)
        out = filter_tiered([_rec("A", list_days=45)], config=cfg)
        assert "A" in out.excluded

    def test_empty_input(self):
        out = filter_tiered([])
        assert out.kept == ()
        assert out.excluded == {}
