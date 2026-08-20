# [BLUEPRINT] MOD-H1_REDIS_HOT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""sector_ranking_engine 单元测试。"""

from __future__ import annotations

import pytest

from zephyr.data.sector_ranking_engine import (
    _calc_change_pct,
    _calc_momentum,
    _get_benchmark_change,
    _pct_rank,
    compute_ranking,
)


class TestPctRank:
    """百分位排名测试。"""

    def test_basic(self):
        values = [10, 20, 30, 40, 50]
        ranks = _pct_rank(values)
        assert ranks[0] == 0.0
        assert ranks[-1] == 1.0
        assert ranks[2] == 0.5

    def test_single(self):
        ranks = _pct_rank([42])
        assert ranks == [0.5]

    def test_empty(self):
        ranks = _pct_rank([])
        assert ranks == []

    def test_duplicate_values(self):
        values = [10, 10, 20]
        ranks = _pct_rank(values)
        assert ranks[0] < ranks[2]
        assert ranks[0] == ranks[1] or ranks[1] < ranks[2]


class TestCalcChangePct:
    """涨跌幅计算测试。"""

    def test_normal(self):
        assert _calc_change_pct(11, 10) == pytest.approx(0.1)

    def test_negative(self):
        assert _calc_change_pct(9, 10) == pytest.approx(-0.1)

    def test_zero_close(self):
        assert _calc_change_pct(10, 0) == 0.0

    def test_no_change(self):
        assert _calc_change_pct(10, 10) == 0.0


class TestCalcMomentum:
    """5分钟动量计算测试。"""

    def test_positive(self):
        assert _calc_momentum(11, 10) == pytest.approx(0.1)

    def test_negative(self):
        assert _calc_momentum(9, 10) == pytest.approx(-0.1)

    def test_zero_before(self):
        assert _calc_momentum(10, 0) == 0.0


class TestGetBenchmarkChange:
    """大盘基准测试。"""

    def test_with_benchmark(self):
        rows = [
            ("880001.SH", 3300, 3200, 3280, 1e9, 100, 100),
            ("880735.SH", 100, 99, 98, 5e8, 50, 50),
        ]
        result = _get_benchmark_change(rows)
        assert result == pytest.approx((3300 - 3200) / 3200)

    def test_without_benchmark(self):
        rows = [
            ("880735.SH", 110, 100, 105, 5e8, 50, 50),
            ("880861.SH", 90, 100, 95, 3e8, 30, 30),
        ]
        result = _get_benchmark_change(rows)
        # 均值: (0.1 + (-0.1)) / 2 = 0.0
        assert result == pytest.approx(0.0)

    def test_empty(self):
        assert _get_benchmark_change([]) == 0.0


class TestComputeRanking:
    """完整排名计算测试。"""

    def test_basic(self):
        rows = [
            ("880001.SH", 3300, 3200, 3280, 1e9, 100, 100),
            ("880735.SH", 110, 100, 105, 5e8, 50, 50),
            ("880861.SH", 90, 100, 95, 3e8, 30, 30),
        ]
        ranking = compute_ranking(rows)
        assert len(ranking) == 3
        assert all(isinstance(s, float) for _, s in ranking)
        # 按分数降序
        scores = [s for _, s in ranking]
        assert scores == sorted(scores, reverse=True)

    def test_empty(self):
        assert compute_ranking([]) == []

    def test_single(self):
        rows = [("880001.SH", 3300, 3200, 3280, 1e9, 100, 100)]
        ranking = compute_ranking(rows)
        assert len(ranking) == 1
        assert ranking[0][0] == "880001.SH"

    def test_score_range(self):
        rows = [
            ("880001.SH", 3300, 3200, 3280, 1e9, 100, 100),
            ("880735.SH", 110, 100, 105, 5e8, 50, 50),
            ("880861.SH", 90, 100, 95, 3e8, 30, 30),
        ]
        ranking = compute_ranking(rows)
        for _, score in ranking:
            assert 0.0 <= score <= 1.0
