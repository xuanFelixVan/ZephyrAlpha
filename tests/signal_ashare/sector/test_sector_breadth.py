"""板块宽度归一化与资金性质板块级聚合 单元测试（22 号 spec §3.1①）"""

import pytest

from zephyr.signal_ashare.sector_breadth import (
    aggregate_capital_nature_to_sector,
    capital_nature_multiplier,
    classify_limit_up_breadth,
    limit_up_breadth_score,
    sector_limit_up_ratio,
)

# ------------------------------------------------------------------
# 1. 板块涨停比归一化
# ------------------------------------------------------------------


class TestSectorLimitUpRatio:
    def test_spec_example_cross_sector_comparable(self):
        """spec 案例：电力设备 19/200≈9.5% vs 油气 3/30=10%，归一化后可比"""
        power = sector_limit_up_ratio(19, 200)
        oil = sector_limit_up_ratio(3, 30)
        assert power == pytest.approx(0.095)
        assert oil == pytest.approx(0.10)
        assert oil > power  # 绝对数 3<19，但涨停比油气更高

    def test_zero_constituents_returns_zero(self):
        assert sector_limit_up_ratio(5, 0) == 0.0

    def test_negative_constituents_returns_zero(self):
        assert sector_limit_up_ratio(5, -3) == 0.0

    def test_zero_limit_up(self):
        assert sector_limit_up_ratio(0, 100) == 0.0

    def test_clip_upper_bound(self):
        assert sector_limit_up_ratio(150, 100) == 1.0


class TestClassifyLimitUpBreadth:
    @pytest.mark.parametrize(
        ("ratio", "expected"),
        [
            (0.11, "极强"),
            (0.101, "极强"),
            (0.10, "强"),  # 边界：>10% 才极强
            (0.06, "强"),
            (0.051, "强"),
            (0.05, "中"),  # 边界：>5% 才强
            (0.02, "中"),  # 边界：<2% 才弱
            (0.019, "弱"),
            (0.0, "弱"),
        ],
    )
    def test_thresholds(self, ratio, expected):
        assert classify_limit_up_breadth(ratio) == expected


class TestLimitUpBreadthScore:
    @pytest.mark.parametrize(
        ("ratio", "expected"),
        [
            (0.11, 40.0),
            (0.06, 32.0),
            (0.03, 20.0),
            (0.01, 10.0),
            (0.0, 5.0),
        ],
    )
    def test_score_mapping(self, ratio, expected):
        assert limit_up_breadth_score(ratio) == expected

    def test_score_never_exceeds_40(self):
        assert limit_up_breadth_score(1.0) == 40.0


# ------------------------------------------------------------------
# 2. 资金性质板块级聚合
# ------------------------------------------------------------------


class TestAggregateCapitalNatureToSector:
    def test_turnover_weighted_big_cap_dominates(self):
        """成交额加权：大票权重高，加权分偏向大票资金性质"""
        constituents = ["BIG", "SMALL"]
        scores = {"BIG": 1.0, "SMALL": -1.0}  # 大票拉升，小票出货
        # BIG 成交额 90 vs SMALL 10 → 加权 = (1×90 + (-1)×10)/100 = 0.8
        score, label = aggregate_capital_nature_to_sector(constituents, scores, {"BIG": 90.0, "SMALL": 10.0})
        assert score == pytest.approx(0.8)
        assert label == "主力流入"

    def test_equal_weight_fallback_when_turnover_missing(self):
        """成交额权重和为 0 → 退化等权"""
        score, label = aggregate_capital_nature_to_sector(["A", "B"], {"A": 1.0, "B": -1.0}, {})
        assert score == pytest.approx(0.0)
        assert label == "中性"

    def test_missing_stock_score_defaults_zero(self):
        """缺失个股资金性质按 0（弱托底）"""
        score, _ = aggregate_capital_nature_to_sector(["A", "B"], {"A": 1.0}, {"A": 1.0, "B": 1.0})
        assert score == pytest.approx(0.5)

    def test_empty_constituents_returns_neutral(self):
        assert aggregate_capital_nature_to_sector([], {"A": 1.0}, {"A": 1.0}) == (
            0.0,
            "中性",
        )

    @pytest.mark.parametrize(
        ("score_value", "expected_label"),
        [
            (0.31, "主力流入"),
            (0.3, "中性"),  # 边界：>0.3 才主力流入
            (-0.09, "中性"),
            (-0.1, "对倒主导"),  # 边界：严格 >-0.1 才中性
            (-0.49, "对倒主导"),
            (-0.5, "主力流出"),  # 边界：严格 >-0.5 才对倒主导
            (-0.51, "主力流出"),
        ],
    )
    def test_label_thresholds(self, score_value, expected_label):
        """标签 4 级阈值边界（单票等权直接命中得分）"""
        _, label = aggregate_capital_nature_to_sector(["A"], {"A": score_value}, {"A": 1.0})
        assert label == expected_label

    def test_score_clipped_to_unit_interval(self):
        score, _ = aggregate_capital_nature_to_sector(["A"], {"A": 5.0}, {"A": 1.0})
        assert score == 1.0


class TestCapitalNatureMultiplier:
    @pytest.mark.parametrize(
        ("label", "expected"),
        [
            ("主力流入", 1.1),
            ("中性", 1.0),
            ("对倒主导", 0.8),
            ("主力流出", 0.6),
        ],
    )
    def test_known_labels(self, label, expected):
        assert capital_nature_multiplier(label) == expected

    def test_unknown_label_falls_back_to_neutral(self):
        assert capital_nature_multiplier("不存在的标签") == 1.0
