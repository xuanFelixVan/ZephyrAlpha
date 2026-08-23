# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [TTL] permanent
"""选股漏斗第二层 初筛漏斗（BM-SEL-17，MOD-SIG-047）单元测试——含五维/容量截断/降级用例。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.coarse_screening_funnel import (
    CoarseScreenConfig,
    CoarseScreenRecord,
    screen_coarse,
)


def _rec(symbol: str, **kw) -> CoarseScreenRecord:
    return CoarseScreenRecord(symbol=symbol, **kw)


class TestFiveDimensions:
    def test_all_pass_kept(self):
        out = screen_coarse([_rec("A"), _rec("B")])
        assert out.kept == ("A", "B")
        assert out.excluded == {}
        assert out.degraded is False
        assert out.truncated is False

    @pytest.mark.parametrize(
        ("kw", "reason_prefix"),
        [
            ({"technical_pass": False}, "dim:technical"),
            ({"volume_ratio": 1.2}, "dim:volume_ratio"),
            ({"turnover_rate_pct": -1.0}, "dim:turnover_rate"),
            ({"sector_strength_rank_pct": 0.45}, "dim:sector_rank"),
            ({"main_force_pass": False}, "dim:main_force"),
            ({"market_state_pass": False}, "dim:market_state"),
        ],
    )
    def test_each_dimension_excludes(self, kw, reason_prefix):
        out = screen_coarse([_rec("X", **kw), _rec("OK")])
        assert out.kept == ("OK",)
        assert out.excluded["X"].startswith(reason_prefix)

    def test_volume_ratio_boundary(self):
        """量比 >1.5 放行；=1.5 排除（契约：>1.5）。"""
        out = screen_coarse([_rec("EQ", volume_ratio=1.5), _rec("GT", volume_ratio=1.51)])
        assert "EQ" in out.excluded
        assert "GT" in out.kept

    def test_sector_rank_boundary(self):
        """板块强度排名前 30% 放行（含边界），>30% 排除。"""
        out = screen_coarse([_rec("IN", sector_strength_rank_pct=0.30), _rec("OUT", sector_strength_rank_pct=0.31)])
        assert "IN" in out.kept
        assert "OUT" in out.excluded


class TestCapacityTruncation:
    def test_over_capacity_truncated_by_liquidity(self):
        cfg = CoarseScreenConfig(capacity_target=2)
        recs = [
            _rec("LOW", liquidity_score=1.0),
            _rec("MID", liquidity_score=2.0),
            _rec("HIGH", liquidity_score=3.0),
        ]
        out = screen_coarse(recs, config=cfg)
        assert out.truncated is True
        assert out.kept == ("HIGH", "MID")
        assert "LOW" not in out.excluded  # 截断非规则排除

    def test_under_capacity_not_truncated(self):
        cfg = CoarseScreenConfig(capacity_target=10)
        out = screen_coarse([_rec("A"), _rec("B")], config=cfg)
        assert out.truncated is False
        assert out.kept == ("A", "B")

    def test_same_liquidity_deterministic_order(self):
        cfg = CoarseScreenConfig(capacity_target=2)
        recs = [_rec("C", liquidity_score=1.0), _rec("A", liquidity_score=1.0), _rec("B", liquidity_score=1.0)]
        out = screen_coarse(recs, config=cfg)
        assert out.kept == ("A", "B")  # 同分按 symbol 字典序，确定性

    def test_invalid_capacity_raises(self):
        with pytest.raises(ValueError):
            screen_coarse([_rec("A")], config=CoarseScreenConfig(capacity_target=0))


class TestDegraded:
    def test_degraded_passthrough(self):
        recs = [_rec("BAD", technical_pass=False, volume_ratio=0.1), _rec("OK")]
        out = screen_coarse(recs, degraded=True)
        assert out.degraded is True
        assert out.kept == ("BAD", "OK")  # 全量放行进精筛

    def test_empty_input(self):
        out = screen_coarse([])
        assert out.kept == ()
