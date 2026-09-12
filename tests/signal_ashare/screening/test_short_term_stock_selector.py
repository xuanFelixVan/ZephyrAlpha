"""D-SIGNAL-23 短线选股引擎单元测试。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.short_term_stock_selector import (
    LimitUpPotential,
    ShortTermStockSelector,
    ShortTermStockSelectorConfig,
    StockSelectionInput,
    StrongStockType,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def selector() -> ShortTermStockSelector:
    return ShortTermStockSelector()


@pytest.fixture
def config() -> ShortTermStockSelectorConfig:
    return ShortTermStockSelectorConfig()


def make_input(**kwargs) -> StockSelectionInput:
    """构造短线选股输入——提供合理默认值。"""
    defaults = dict(
        symbol="600000",
        target_price=15.0,
        current_price=10.0,
        fundamental_score=70.0,
        technical_trend_score=70.0,
        liquidity_score=70.0,
        corr_with_market=0.5,
        turnover_rate=5.0,
        large_order_ratio=0.08,
        consecutive_limit_ups=0,
        seal_order_amount=0.0,
        float_market_cap=50.0,
        sector_hot_score=60.0,
        open_board_count=0,
        seal_time_minutes=30,
        catalyst_strength=60.0,
        main_force_phase="未知",
        capital_flow_pattern="未知",
    )
    defaults.update(kwargs)
    return StockSelectionInput(**defaults)


# ============================================================================
# 维度1: 机构选股评分器
# ============================================================================


class TestInstitutionalScoring:
    def test_high_target_space(self, selector: ShortTermStockSelector):
        """目标价空间 50% → 目标价维度满分。"""
        result = selector.analyze(make_input(target_price=15.0, current_price=10.0))
        assert result.institutional_breakdown["目标价空间"] == 100.0

    def test_zero_target_space(self, selector: ShortTermStockSelector):
        """目标价等于当前价 → 0 分。"""
        result = selector.analyze(make_input(target_price=10.0, current_price=10.0))
        assert result.institutional_breakdown["目标价空间"] == 0.0

    def test_half_target_space(self, selector: ShortTermStockSelector):
        """目标价空间 25% → 50 分。"""
        result = selector.analyze(make_input(target_price=12.5, current_price=10.0))
        assert result.institutional_breakdown["目标价空间"] == 50.0

    def test_capped_target_space(self, selector: ShortTermStockSelector):
        """目标价空间超过 50% → 封顶 100 分。"""
        result = selector.analyze(make_input(target_price=30.0, current_price=10.0))
        assert result.institutional_breakdown["目标价空间"] == 100.0

    def test_zero_current_price(self, selector: ShortTermStockSelector):
        """当前价为 0 → 目标价维度 0 分。"""
        result = selector.analyze(make_input(target_price=10.0, current_price=0.0))
        assert result.institutional_breakdown["目标价空间"] == 0.0

    def test_score_range(self, selector: ShortTermStockSelector):
        result = selector.analyze(make_input())
        assert 0.0 <= result.institutional_score <= 100.0

    def test_score_clamps_inputs(self, selector: ShortTermStockSelector):
        """基本面/技术/流动性评分超出 0~100 → 截断。"""
        result = selector.analyze(
            make_input(
                fundamental_score=200.0,
                technical_trend_score=-50.0,
                liquidity_score=150.0,
            )
        )
        assert result.institutional_breakdown["基本面"] == 100.0
        assert result.institutional_breakdown["技术趋势"] == 0.0
        assert result.institutional_breakdown["流动性"] == 100.0


# ============================================================================
# 维度2: 强庄股识别器
# ============================================================================


class TestStrongStockIdentification:
    def test_strong_main_force(self, selector: ShortTermStockSelector):
        """走势独立 + 换手异常 + 神秘大单 → 强庄股。"""
        result = selector.analyze(
            make_input(
                corr_with_market=0.2,
                turnover_rate=12.0,
                large_order_ratio=0.2,
            )
        )
        assert result.strong_stock_type == StrongStockType.STRONG_MAIN_FORCE.value
        assert result.strong_stock_confidence >= 70

    def test_normal_stock(self, selector: ShortTermStockSelector):
        """中等指标 → 普通股。"""
        result = selector.analyze(
            make_input(
                corr_with_market=0.4,
                turnover_rate=6.0,
                large_order_ratio=0.1,
            )
        )
        assert result.strong_stock_type == StrongStockType.NORMAL.value
        assert 40 <= result.strong_stock_confidence < 70

    def test_weak_stock(self, selector: ShortTermStockSelector):
        """与大盘高度相关 + 低换手 + 无大单 → 弱势。"""
        result = selector.analyze(
            make_input(
                corr_with_market=0.9,
                turnover_rate=2.0,
                large_order_ratio=0.01,
            )
        )
        assert result.strong_stock_type == StrongStockType.WEAK.value
        assert result.strong_stock_confidence < 40


# ============================================================================
# 维度3: 连板潜力评分卡
# ============================================================================


class TestLimitUpPotential:
    def test_high_potential(self, selector: ShortTermStockSelector):
        """7维全强 → 高潜力。"""
        result = selector.analyze(
            make_input(
                consecutive_limit_ups=3,
                seal_order_amount=5000.0,  # 封流比 1%
                float_market_cap=50.0,
                sector_hot_score=90.0,
                open_board_count=0,
                seal_time_minutes=5,
                catalyst_strength=90.0,
            )
        )
        assert result.limitup_potential == LimitUpPotential.HIGH.value
        assert result.limitup_score >= 75

    def test_low_potential(self, selector: ShortTermStockSelector):
        """7维全弱 → 低潜力。"""
        result = selector.analyze(
            make_input(
                consecutive_limit_ups=0,
                seal_order_amount=0.0,
                float_market_cap=500.0,  # 大市值
                sector_hot_score=20.0,
                open_board_count=3,
                seal_time_minutes=300,
                catalyst_strength=20.0,
            )
        )
        assert result.limitup_potential == LimitUpPotential.LOW.value
        assert result.limitup_score < 50

    def test_none_potential(self, selector: ShortTermStockSelector):
        """无连板且全 0 → 无潜力。"""
        result = selector.analyze(
            make_input(
                consecutive_limit_ups=0,
                seal_order_amount=0.0,
                float_market_cap=0.0,
                sector_hot_score=0.0,
                open_board_count=0,
                seal_time_minutes=0,
                catalyst_strength=0.0,
            )
        )
        assert result.limitup_potential == LimitUpPotential.NONE.value
        assert result.limitup_score == 0.0

    def test_consecutive_height_scoring(self, selector: ShortTermStockSelector):
        """连板高度评分：1板=40, 2板=70, 3板=90, 4板=100, 5板=80。"""
        cases = [
            (1, 40.0),
            (2, 70.0),
            (3, 90.0),
            (4, 100.0),
            (5, 80.0),
            (6, 80.0),
        ]
        for count, expected in cases:
            result = selector.analyze(make_input(consecutive_limit_ups=count))
            assert result.limitup_breakdown["连板高度"] == expected, f"连板高度 {count} 应为 {expected}"

    def test_seal_strength_high_ratio(self, selector: ShortTermStockSelector):
        """封流比 >= 1% → 100 分。"""
        result = selector.analyze(make_input(seal_order_amount=5000.0, float_market_cap=50.0))
        assert result.limitup_breakdown["封单强度"] == 100.0

    def test_seal_strength_zero(self, selector: ShortTermStockSelector):
        """无封单 → 0 分。"""
        result = selector.analyze(make_input(seal_order_amount=0.0, float_market_cap=50.0))
        assert result.limitup_breakdown["封单强度"] == 0.0

    def test_market_liquidity_mid_cap(self, selector: ShortTermStockSelector):
        """中小市值(20~100亿) → 100 分。"""
        result = selector.analyze(make_input(float_market_cap=50.0))
        assert result.limitup_breakdown["市值流动性"] == 100.0

    def test_market_liquidity_large_cap(self, selector: ShortTermStockSelector):
        """大市值(>300亿) → 40 分。"""
        result = selector.analyze(make_input(float_market_cap=500.0))
        assert result.limitup_breakdown["市值流动性"] == 40.0

    def test_seal_time_early(self, selector: ShortTermStockSelector):
        """开盘即封(<=5分钟) → 100 分。"""
        result = selector.analyze(make_input(seal_time_minutes=3))
        assert result.limitup_breakdown["封板时间"] == 100.0

    def test_seal_time_late(self, selector: ShortTermStockSelector):
        """尾盘封板(>300分钟) → 15 分。"""
        result = selector.analyze(make_input(seal_time_minutes=400))
        assert result.limitup_breakdown["封板时间"] == 15.0

    def test_divergence_score_zero_open(self, selector: ShortTermStockSelector):
        """连板且 0 次开板 → 100 分。"""
        result = selector.analyze(make_input(consecutive_limit_ups=2, open_board_count=0))
        assert result.limitup_breakdown["分歧程度"] == 100.0

    def test_divergence_score_many_open(self, selector: ShortTermStockSelector):
        """连板且 3 次开板 → 20 分。"""
        result = selector.analyze(make_input(consecutive_limit_ups=2, open_board_count=3))
        assert result.limitup_breakdown["分歧程度"] == 20.0

    def test_divergence_score_no_limitup(self, selector: ShortTermStockSelector):
        """无连板时分歧维度不适用 → 0 分。"""
        result = selector.analyze(make_input(consecutive_limit_ups=0, open_board_count=0))
        assert result.limitup_breakdown["分歧程度"] == 0.0


# ============================================================================
# 连板分歧程度评估器
# ============================================================================


class TestDivergenceEvaluation:
    def test_no_limit_up_no_divergence(self, selector: ShortTermStockSelector):
        """无连板 → 无分歧。"""
        result = selector.analyze(make_input(consecutive_limit_ups=0))
        assert result.divergence_degree == "无分歧"

    def test_low_divergence(self, selector: ShortTermStockSelector):
        """连板但未开板 → 低分歧。"""
        result = selector.analyze(make_input(consecutive_limit_ups=2, open_board_count=0))
        assert result.divergence_degree == "低分歧"

    def test_medium_divergence(self, selector: ShortTermStockSelector):
        """1 次开板 → 中分歧。"""
        result = selector.analyze(make_input(consecutive_limit_ups=2, open_board_count=1))
        assert result.divergence_degree == "中分歧"

    def test_high_divergence(self, selector: ShortTermStockSelector):
        """2+ 次开板 → 高分歧。"""
        result = selector.analyze(make_input(consecutive_limit_ups=2, open_board_count=2))
        assert result.divergence_degree == "高分歧"


# ============================================================================
# 推荐意见
# ============================================================================


class TestRecommendation:
    def test_strong_recommendation(self, selector: ShortTermStockSelector):
        """综合分>=80 + 强庄股 → 强烈推荐。"""
        result = selector.analyze(
            make_input(
                target_price=20.0,  # 目标价空间 100% → 100
                current_price=10.0,
                fundamental_score=90.0,
                technical_trend_score=90.0,
                liquidity_score=90.0,
                corr_with_market=0.2,
                turnover_rate=12.0,
                large_order_ratio=0.2,
                consecutive_limit_ups=3,
                seal_order_amount=5000.0,
                float_market_cap=50.0,
                sector_hot_score=90.0,
                open_board_count=0,
                seal_time_minutes=5,
                catalyst_strength=90.0,
            )
        )
        assert result.strong_stock_type == StrongStockType.STRONG_MAIN_FORCE.value
        assert result.overall_score >= 80
        assert result.recommendation == "强烈推荐"

    def test_recommend(self, selector: ShortTermStockSelector):
        """综合分 65~80 + 非高分歧 → 推荐。"""
        result = selector.analyze(
            make_input(
                target_price=15.0,  # 目标价空间 50% → 100
                current_price=10.0,
                fundamental_score=75.0,
                technical_trend_score=75.0,
                liquidity_score=75.0,
                corr_with_market=0.4,
                turnover_rate=6.0,
                large_order_ratio=0.1,
                consecutive_limit_ups=2,
                open_board_count=1,  # 中分歧
            )
        )
        assert result.strong_stock_type == StrongStockType.NORMAL.value
        assert result.overall_score >= 65
        assert result.recommendation == "推荐"

    def test_watch(self, selector: ShortTermStockSelector):
        """综合分 45~65 → 观望。"""
        result = selector.analyze(
            make_input(
                target_price=15.0,  # 目标价空间 50% → 100
                current_price=10.0,
                fundamental_score=60.0,
                technical_trend_score=60.0,
                liquidity_score=60.0,
                corr_with_market=0.4,  # +15
                turnover_rate=4.0,  # +0
                large_order_ratio=0.01,  # +0 → 15 → 弱势
                consecutive_limit_ups=0,
                float_market_cap=50.0,
                sector_hot_score=100.0,
                seal_time_minutes=5,  # → 100
                catalyst_strength=100.0,
            )
        )
        assert 45 <= result.overall_score < 65
        assert result.recommendation == "观望"

    def test_avoid(self, selector: ShortTermStockSelector):
        """综合分 < 45 → 回避。"""
        result = selector.analyze(
            make_input(
                target_price=10.0,  # 0 空间
                current_price=10.0,
                fundamental_score=20.0,
                technical_trend_score=20.0,
                liquidity_score=20.0,
                corr_with_market=0.9,  # +0
                turnover_rate=2.0,  # +0
                large_order_ratio=0.01,  # +0 → 0 → 弱势
                consecutive_limit_ups=0,
                sector_hot_score=10.0,
                catalyst_strength=10.0,
            )
        )
        assert result.overall_score < 45
        assert result.recommendation == "回避"

    def test_high_divergence_blocks_recommend(self, selector: ShortTermStockSelector):
        """高分歧时即使综合分 >= 65 也不推荐（降级为观望）。"""
        result = selector.analyze(
            make_input(
                target_price=15.0,
                current_price=10.0,
                fundamental_score=75.0,
                technical_trend_score=75.0,
                liquidity_score=75.0,
                corr_with_market=0.4,
                turnover_rate=6.0,
                large_order_ratio=0.1,
                consecutive_limit_ups=3,
                open_board_count=2,  # 高分歧
                seal_order_amount=3000.0,
                sector_hot_score=80.0,
                seal_time_minutes=10,
                catalyst_strength=80.0,
            )
        )
        assert result.divergence_degree == "高分歧"
        # 高分歧 → 不进入"推荐"分支
        assert result.recommendation != "推荐"


# ============================================================================
# 综合
# ============================================================================


class TestOverall:
    def test_overall_score_range(self, selector: ShortTermStockSelector):
        result = selector.analyze(make_input())
        assert 0.0 <= result.overall_score <= 100.0

    def test_audit_trail_populated(self, selector: ShortTermStockSelector):
        result = selector.analyze(make_input())
        assert len(result.audit_trail) >= 4
        dims = [e["dimension"] for e in result.audit_trail]
        assert "institutional_scoring" in dims
        assert "strong_stock" in dims
        assert "limitup_potential" in dims
        assert "divergence" in dims

    def test_empty_symbol_degraded(self, selector: ShortTermStockSelector):
        result = selector.analyze(make_input(symbol=""))
        assert result.is_degraded is True
        assert result.recommendation == "回避"

    def test_negative_price_degraded(self, selector: ShortTermStockSelector):
        result = selector.analyze(make_input(current_price=-5.0))
        assert result.is_degraded is True

    def test_symbol_preserved(self, selector: ShortTermStockSelector):
        result = selector.analyze(make_input(symbol="000001"))
        assert result.symbol == "000001"


# ============================================================================
# 配置可定制性
# ============================================================================


class TestConfigCustomization:
    def test_custom_potential_thresholds(self):
        """自定义潜力等级阈值。"""
        cfg = ShortTermStockSelectorConfig(
            potential_high_threshold=90.0,
            potential_medium_threshold=70.0,
        )
        selector = ShortTermStockSelector(cfg)
        # 构造一个评分约 80 的输入 → 默认高潜力，但自定义阈值 90 → 中潜力
        result = selector.analyze(
            make_input(
                consecutive_limit_ups=2,
                seal_order_amount=2000.0,  # 封流比 0.4% → 60
                float_market_cap=50.0,
                sector_hot_score=70.0,
                open_board_count=0,
                seal_time_minutes=10,
                catalyst_strength=70.0,
            )
        )
        # 评分应在 70~90 区间 → 自定义阈值下为中潜力
        assert 70 <= result.limitup_score < 90
        assert result.limitup_potential == LimitUpPotential.MEDIUM.value

    def test_custom_independence_threshold(self):
        """自定义独立性阈值——更宽松。"""
        cfg = ShortTermStockSelectorConfig(independence_corr_threshold=0.6)
        selector = ShortTermStockSelector(cfg)
        # corr=0.5 → 默认阈值 0.3 不满足独立(+15)，但 0.6 满足(+35)
        result = selector.analyze(
            make_input(
                corr_with_market=0.5,
                turnover_rate=12.0,
                large_order_ratio=0.2,
            )
        )
        # +35(独立) + 35(换手) + 30(大单) = 100 → 强庄股
        assert result.strong_stock_type == StrongStockType.STRONG_MAIN_FORCE.value

    def test_custom_divergence_open_count_threshold(self):
        """自定义分歧开板次数阈值——3 次才算高分歧。"""
        cfg = ShortTermStockSelectorConfig(divergence_open_count_threshold=3)
        selector = ShortTermStockSelector(cfg)
        # open_board_count=2 → 默认高分歧，但自定义阈值 3 → 中分歧
        result = selector.analyze(make_input(consecutive_limit_ups=2, open_board_count=2))
        assert result.divergence_degree == "中分歧"

    def test_frozen_config(self):
        """配置不可变。"""
        cfg = ShortTermStockSelectorConfig()
        with pytest.raises(AttributeError):
            cfg.potential_high_threshold = 99.0  # type: ignore[misc]

    def test_custom_weights_sum(self, selector: ShortTermStockSelector):
        """默认 7 维权重和 = 100。"""
        cfg = selector._config
        total = (
            cfg.limitup_weight_height
            + cfg.limitup_weight_seal
            + cfg.limitup_weight_sector
            + cfg.limitup_weight_divergence
            + cfg.limitup_weight_liquidity
            + cfg.limitup_weight_seal_time
            + cfg.limitup_weight_catalyst
        )
        assert total == 100.0

    def test_custom_institutional_weights_sum(self, selector: ShortTermStockSelector):
        """默认机构评分 4 维权重和 = 100。"""
        cfg = selector._config
        total = (
            cfg.institutional_weight_target_space
            + cfg.institutional_weight_fundamental
            + cfg.institutional_weight_technical
            + cfg.institutional_weight_liquidity
        )
        assert total == 100.0
