"""MOD-SIG-142 sector_strength_aggregator 单元测试（night-gw-2300 自裁批）。

红蓝手法：红-边界（负分/NaN/权重不归一/调节越界/空池）/红-契约（等权默认+池比例）
/红-前视（无墙钟）/红-竞态（frozen+稳定序）。
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.core.sector_strength_aggregator import (
    CANDIDATE_POOL_RATIO,
    DEFAULT_WEIGHTS,
    SectorStrength,
    SectorStrengthInputError,
    aggregate_sector_strength,
    build_sector_strengths,
    select_candidate_pool,
)


def _s(sector: str, composite: float) -> SectorStrength:
    return SectorStrength(
        sector=sector,
        structure_score=composite,
        momentum_activity=composite,
        multi_period_momentum=composite,
        capital_flow=composite,
        market_adjustment=0.0,
        composite=composite,
    )


class TestContract:
    def test_default_weights_equal_quarter(self) -> None:
        assert DEFAULT_WEIGHTS == (0.25, 0.25, 0.25, 0.25)
        assert CANDIDATE_POOL_RATIO == 0.15

    def test_empty_sector_fail_closed(self) -> None:
        with pytest.raises(SectorStrengthInputError, match="板块名为空"):
            aggregate_sector_strength("  ", 50, 50, 50, 50)

    def test_negative_score_fail_closed(self) -> None:
        with pytest.raises(SectorStrengthInputError, match="为负"):
            aggregate_sector_strength("半导体", -1, 50, 50, 50)

    def test_nan_score_fail_closed(self) -> None:
        with pytest.raises(SectorStrengthInputError, match="非有限"):
            aggregate_sector_strength("半导体", float("nan"), 50, 50, 50)

    def test_weights_not_normalized_fail_closed(self) -> None:
        with pytest.raises(SectorStrengthInputError, match="权重不归一"):
            aggregate_sector_strength("半导体", 50, 50, 50, 50, weights=(0.5, 0.5, 0.5, 0.5))

    def test_composite_formula(self) -> None:
        """等权合成：四路 80/60/40/20 + 调节 +5 → 50+5=55。"""
        out = aggregate_sector_strength("半导体", 80, 60, 40, 20, market_adjustment=5.0)
        assert out.composite == pytest.approx(55.0)


class TestBoundaries:
    def test_market_adjustment_clamped_at_plus_10(self) -> None:
        out = aggregate_sector_strength("半导体", 99, 99, 99, 99, market_adjustment=50)
        assert out.composite == 100.0
        assert out.market_adjustment == 10.0

    def test_negative_adjustment_clamped(self) -> None:
        out = aggregate_sector_strength("半导体", 1, 1, 1, 1, market_adjustment=-50)
        assert out.composite == 0.0
        assert out.market_adjustment == -10.0

    def test_score_above_100_clamped(self) -> None:
        out = aggregate_sector_strength("半导体", 120, 120, 120, 120)
        assert out.composite == 100.0


class TestCandidatePool:
    def test_top_15_percent_ceil(self) -> None:
        """10 板块 × 15% → ceil(1.5)=2 个进池。"""
        rows = [_s(f"S{i:02d}", 50.0 + i) for i in range(10)]
        pool = select_candidate_pool(rows)
        assert sum(1 for s in pool if s.in_candidate_pool) == 2
        assert pool[0].in_candidate_pool and pool[1].in_candidate_pool
        assert not pool[-1].in_candidate_pool

    def test_single_sector_pool_of_one(self) -> None:
        pool = select_candidate_pool([_s("半导体", 77)])
        assert len(pool) == 1 and pool[0].in_candidate_pool

    def test_empty_pool(self) -> None:
        assert select_candidate_pool([]) == []

    def test_tie_broken_by_sector_name(self) -> None:
        """平分按板块名稳定序（确定性）。"""
        rows = [_s("BB", 60.0), _s("AA", 60.0)]
        pool = select_candidate_pool(rows)
        assert pool[0].sector == "AA"

    def test_invalid_ratio_fail_closed(self) -> None:
        with pytest.raises(SectorStrengthInputError, match="候选池比例非法"):
            select_candidate_pool([_s("A", 50)], ratio=0.0)


class TestBuildAndPurity:
    def test_build_batch_marks_pool(self) -> None:
        rows = [
            {"sector": f"S{i}", "structure_score": 50 + i, "momentum_activity": 50,
             "multi_period_momentum": 50, "capital_flow": 50, "market_adjustment": 0}
            for i in range(10)
        ]
        out = build_sector_strengths(rows)
        assert len(out) == 10
        assert sum(1 for s in out if s.in_candidate_pool) == 2

    def test_deterministic(self) -> None:
        a = aggregate_sector_strength("半导体", 80, 60, 40, 20, market_adjustment=5)
        b = aggregate_sector_strength("半导体", 80, 60, 40, 20, market_adjustment=5)
        assert a == b

    def test_frozen(self) -> None:
        out = aggregate_sector_strength("半导体", 50, 50, 50, 50)
        with pytest.raises(Exception):
            out.composite = 1  # type: ignore[misc]

    def test_to_dict_json_round_trip(self) -> None:
        payload = aggregate_sector_strength("半导体", 80, 60, 40, 20, market_adjustment=5).to_dict()
        restored = json.loads(json.dumps(payload, ensure_ascii=False))
        assert restored["composite"] == pytest.approx(55.0)
        assert set(restored) == {
            "sector", "structure_score", "momentum_activity", "multi_period_momentum",
            "capital_flow", "market_adjustment", "composite", "in_candidate_pool",
        }

    def test_no_wall_clock_in_output(self) -> None:
        d = aggregate_sector_strength("半导体", 50, 50, 50, 50).to_dict()
        assert not any(k.lower().startswith(("ts", "time", "now", "date")) for k in d)
