"""D-SIGNAL-34 量化短线强度引擎单元测试。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.quant_short_term_strength_engine import (
    QuantShortTermStrengthEngine,
    QuantStrengthConfig,
    QuantStrengthInput,
    StockCategory,
    StrengthGrade,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def engine() -> QuantShortTermStrengthEngine:
    return QuantShortTermStrengthEngine()


@pytest.fixture
def config() -> QuantStrengthConfig:
    return QuantStrengthConfig()


def make_input(
    momentum: float = 0.0,
    sector_change: float = 0.0,
    stock_change: float = 0.0,
    market_change: float = 0.0,
    capital_inflow: float = 0.0,
    float_mcap: float = 1e9,
    technical: float = 50.0,
    risk: float = 50.0,
    youzi_score: float = 50.0,
    consecutive: int = 0,
    is_main_line: bool = False,
) -> QuantStrengthInput:
    return QuantStrengthInput(
        momentum_z_score=momentum,
        sector_change_pct=sector_change,
        stock_change_pct=stock_change,
        market_change_pct=market_change,
        capital_inflow=capital_inflow,
        float_market_cap=float_mcap,
        technical_score=technical,
        risk_score=risk,
        youzi_emotion_score=youzi_score,
        consecutive_limit_ups=consecutive,
        is_main_line=is_main_line,
    )


# ============================================================================
# 维度1: 价格动量
# ============================================================================


class TestMomentum:
    def test_excellent_momentum(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_momentum(2.5)
        assert d.score == 20.0

    def test_good_momentum(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_momentum(1.5)
        assert d.score == 15.0

    def test_fair_momentum(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_momentum(0.5)
        assert d.score == 8.0

    def test_negative_momentum(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_momentum(-1.0)
        assert 0.0 <= d.score < 8.0


# ============================================================================
# 维度2: 行业强度
# ============================================================================


class TestSectorStrength:
    def test_excellent(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_sector_strength(4.0)
        assert d.score == 15.0

    def test_good(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_sector_strength(2.0)
        assert d.score == 11.0

    def test_fair(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_sector_strength(0.5)
        assert d.score == 6.0

    def test_negative(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_sector_strength(-2.0)
        assert d.score >= 0.0


# ============================================================================
# 维度3: 相对强度
# ============================================================================


class TestRelativeStrength:
    def test_excellent(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_relative_strength(8.0, 1.0)  # 超大盘7%
        assert d.score == 20.0

    def test_good(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_relative_strength(5.0, 1.0)  # 超大盘4%
        assert d.score == 15.0

    def test_fair(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_relative_strength(2.0, 1.0)  # 超大盘1%
        assert d.score == 8.0

    def test_underperform(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_relative_strength(-2.0, 1.0)  # 落后大盘3%
        assert d.score < 8.0


# ============================================================================
# 维度4: 资金
# ============================================================================


class TestCapital:
    def test_zero_mcap(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_capital(1e8, 0.0)
        assert d.score == 0.0

    def test_excellent(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_capital(6e7, 1e9)  # 6%
        assert d.score == 15.0

    def test_good(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_capital(3e7, 1e9)  # 3%
        assert d.score == 11.0

    def test_fair(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_capital(1e7, 1e9)  # 1%
        assert d.score == 6.0

    def test_outflow(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_capital(-5e7, 1e9)  # -5%
        assert d.score >= 0.0


# ============================================================================
# 维度5: 技术
# ============================================================================


class TestTechnical:
    def test_excellent(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_technical(85.0)
        assert d.score == 20.0

    def test_good(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_technical(65.0)
        assert d.score == 15.0

    def test_fair(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_technical(45.0)
        assert d.score == 8.0

    def test_poor(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_technical(20.0)
        assert d.score < 8.0


# ============================================================================
# 维度6: 风险（反向评分）
# ============================================================================


class TestRisk:
    def test_low_risk(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_risk(10.0)
        assert d.score == 10.0

    def test_good_risk(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_risk(30.0)
        assert d.score == 7.0

    def test_fair_risk(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_risk(50.0)
        assert d.score == 4.0

    def test_high_risk(self, engine: QuantShortTermStrengthEngine):
        d = engine.score_risk(80.0)
        assert d.score < 4.0


# ============================================================================
# A~E五级评级
# ============================================================================


class TestGrade:
    def test_grade_a(self, engine: QuantShortTermStrengthEngine):
        assert engine.determine_grade(85.0) == StrengthGrade.A.value

    def test_grade_b(self, engine: QuantShortTermStrengthEngine):
        assert engine.determine_grade(70.0) == StrengthGrade.B.value

    def test_grade_c(self, engine: QuantShortTermStrengthEngine):
        assert engine.determine_grade(55.0) == StrengthGrade.C.value

    def test_grade_d(self, engine: QuantShortTermStrengthEngine):
        assert engine.determine_grade(40.0) == StrengthGrade.D.value

    def test_grade_e(self, engine: QuantShortTermStrengthEngine):
        assert engine.determine_grade(20.0) == StrengthGrade.E.value

    def test_boundary_a_b(self, engine: QuantShortTermStrengthEngine):
        assert engine.determine_grade(80.0) == StrengthGrade.A.value
        assert engine.determine_grade(79.9) == StrengthGrade.B.value


# ============================================================================
# 6类输出分类
# ============================================================================


class TestCategoryClassification:
    def test_main_leader(self, engine: QuantShortTermStrengthEngine):
        """量化>=80 + 游资>=70 + 主线 → 主升龙头。"""
        result = engine.analyze(
            make_input(
                momentum=2.5,
                sector_change=4.0,
                stock_change=10.0,
                market_change=1.0,
                capital_inflow=8e7,
                float_mcap=1e9,
                technical=90.0,
                risk=15.0,
                youzi_score=75.0,
                is_main_line=True,
            )
        )
        assert result.category == StockCategory.MAIN_LEADER.value

    def test_second_to_third(self, engine: QuantShortTermStrengthEngine):
        """量化>=65 + 连板>=2 → 二进三。"""
        result = engine.analyze(
            make_input(
                momentum=2.0,
                sector_change=3.0,
                stock_change=10.0,
                market_change=1.0,
                capital_inflow=6e7,
                float_mcap=1e9,
                technical=80.0,
                risk=20.0,
                youzi_score=50.0,
                consecutive=2,
            )
        )
        assert result.category == StockCategory.SECOND_TO_THIRD.value

    def test_recovery(self, engine: QuantShortTermStrengthEngine):
        """量化>=70 + 游资40-65 → 复苏。"""
        result = engine.analyze(
            make_input(
                momentum=2.0,
                sector_change=2.0,
                stock_change=8.0,
                market_change=1.0,
                capital_inflow=5e7,
                float_mcap=1e9,
                technical=80.0,
                risk=25.0,
                youzi_score=55.0,
                consecutive=0,
            )
        )
        assert result.category == StockCategory.RECOVERY.value

    def test_fake_strong(self, engine: QuantShortTermStrengthEngine):
        """游资>=60 + 量化<50 → 伪强。"""
        result = engine.analyze(
            make_input(
                momentum=-0.5,
                sector_change=-1.0,
                stock_change=2.0,
                market_change=1.0,
                capital_inflow=-1e7,
                float_mcap=1e9,
                technical=35.0,
                risk=55.0,
                youzi_score=65.0,
                consecutive=1,
            )
        )
        assert result.category == StockCategory.FAKE_STRONG.value

    def test_follower(self, engine: QuantShortTermStrengthEngine):
        """量化50-65 + 游资40-65 → 跟风。"""
        result = engine.analyze(
            make_input(
                momentum=1.0,
                sector_change=1.0,
                stock_change=4.0,
                market_change=1.0,
                capital_inflow=2e7,
                float_mcap=1e9,
                technical=55.0,
                risk=35.0,
                youzi_score=50.0,
                consecutive=1,
            )
        )
        assert result.category == StockCategory.FOLLOWER.value

    def test_inverse_board(self, engine: QuantShortTermStrengthEngine):
        """连板=1 + 涨停 + 高风险 → 地天反包。"""
        result = engine.analyze(
            make_input(
                momentum=1.5,
                sector_change=2.0,
                stock_change=10.0,  # 涨停
                market_change=0.5,
                capital_inflow=3e7,
                float_mcap=1e9,
                technical=60.0,
                risk=65.0,  # 高风险
                youzi_score=50.0,
                consecutive=1,
            )
        )
        assert result.category == StockCategory.INVERSE_BOARD.value


# ============================================================================
# 综合
# ============================================================================


class TestOverall:
    def test_total_score_range(self, engine: QuantShortTermStrengthEngine):
        result = engine.analyze(make_input())
        assert 0.0 <= result.total_score <= 100.0

    def test_six_dimensions_returned(self, engine: QuantShortTermStrengthEngine):
        result = engine.analyze(make_input(momentum=1.5))
        assert len(result.dimension_scores) == 6
        names = [d.name for d in result.dimension_scores]
        assert "价格动量" in names
        assert "行业强度" in names
        assert "相对强度" in names
        assert "资金" in names
        assert "技术" in names
        assert "风险" in names

    def test_audit_trail_populated(self, engine: QuantShortTermStrengthEngine):
        result = engine.analyze(make_input())
        assert len(result.audit_trail) >= 8  # 6维度 + 评级 + 分类

    def test_high_score_scenario(self, engine: QuantShortTermStrengthEngine):
        """全面强势 → 高分 + A级。"""
        result = engine.analyze(
            make_input(
                momentum=2.5,
                sector_change=4.0,
                stock_change=9.0,
                market_change=1.0,
                capital_inflow=8e7,
                float_mcap=1e9,
                technical=90.0,
                risk=10.0,
            )
        )
        assert result.total_score >= 80.0
        assert result.grade == StrengthGrade.A.value

    def test_low_score_scenario(self, engine: QuantShortTermStrengthEngine):
        """全面弱势 → 低分 + E级。"""
        result = engine.analyze(
            make_input(
                momentum=-1.5,
                sector_change=-2.0,
                stock_change=-3.0,
                market_change=1.0,
                capital_inflow=-5e7,
                float_mcap=1e9,
                technical=25.0,
                risk=75.0,
            )
        )
        assert result.total_score < 35.0
        assert result.grade == StrengthGrade.E.value


# ============================================================================
# 降级
# ============================================================================


class TestDegradation:
    def test_negative_mcap(self, engine: QuantShortTermStrengthEngine):
        result = engine.analyze(make_input(float_mcap=-1))
        assert result.is_degraded is True

    def test_invalid_technical(self, engine: QuantShortTermStrengthEngine):
        result = engine.analyze(make_input(technical=150.0))
        assert result.is_degraded is True

    def test_invalid_risk(self, engine: QuantShortTermStrengthEngine):
        result = engine.analyze(make_input(risk=-10.0))
        assert result.is_degraded is True


# ============================================================================
# 配置可定制性
# ============================================================================


class TestConfigCustomization:
    def test_custom_momentum_thresholds(self):
        cfg = QuantStrengthConfig(momentum_z_excellent=3.0, momentum_z_good=2.0)
        engine = QuantShortTermStrengthEngine(cfg)
        d = engine.score_momentum(2.5)
        # 2.5 < 3.0 but >= 2.0 → good tier
        assert d.score == 15.0

    def test_custom_grade_thresholds(self):
        cfg = QuantStrengthConfig(grade_a_min=90.0, grade_b_min=75.0)
        engine = QuantShortTermStrengthEngine(cfg)
        assert engine.determine_grade(85.0) == StrengthGrade.B.value
        assert engine.determine_grade(92.0) == StrengthGrade.A.value

    def test_custom_category_thresholds(self):
        """自定义主升龙头阈值——更高要求。"""
        cfg = QuantStrengthConfig(
            main_leader_quant_min=90.0,
            main_leader_youzi_min=80.0,
        )
        engine = QuantShortTermStrengthEngine(cfg)
        result = engine.analyze(
            make_input(
                momentum=2.5,
                sector_change=4.0,
                stock_change=10.0,
                market_change=1.0,
                capital_inflow=8e7,
                float_mcap=1e9,
                technical=90.0,
                risk=15.0,
                youzi_score=75.0,  # < 80 → not main leader
                is_main_line=True,
            )
        )
        # 量化可能>=90 但游资75<80 → 不是主升龙头
        assert result.category != StockCategory.MAIN_LEADER.value

    def test_frozen_config(self):
        cfg = QuantStrengthConfig()
        with pytest.raises(AttributeError):
            cfg.momentum_z_excellent = 5.0  # type: ignore[misc]
