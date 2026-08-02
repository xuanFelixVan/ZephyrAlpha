"""D-SIGNAL-35 双引擎融合决策引擎单元测试。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.dual_engine_fusion_decision_engine import (
    DualEngineFusionDecisionEngine,
    FusionDecision,
    FusionDecisionConfig,
    FusionDecisionInput,
    SignalDirection,
)
from zephyr.signal_ashare.quant_short_term_strength_engine import (
    QuantStrengthResult,
    StockCategory,
    StrengthGrade,
)
from zephyr.signal_ashare.youzi_relay_emotion_engine import (
    EmotionPhase,
    StrategyAction,
    YouziEmotionResult,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def engine() -> DualEngineFusionDecisionEngine:
    return DualEngineFusionDecisionEngine()


@pytest.fixture
def config() -> FusionDecisionConfig:
    return FusionDecisionConfig()


def make_youzi_result(
    score: float = 50.0,
    phase: str = EmotionPhase.MAIN_RISE.value,
) -> YouziEmotionResult:
    return YouziEmotionResult(
        total_score=score,
        factor_scores=[],
        emotion_phase=phase,
        phase_confidence=70.0,
        strategy_action=StrategyAction.CORE_POSITION.value,
    )


def make_quant_result(
    score: float = 50.0,
    grade: str = StrengthGrade.C.value,
    category: str = StockCategory.NEUTRAL.value,
) -> QuantStrengthResult:
    return QuantStrengthResult(
        total_score=score,
        dimension_scores=[],
        grade=grade,
        category=category,
    )


def make_input(
    youzi_score: float = 50.0,
    quant_score: float = 50.0,
    phase: str = EmotionPhase.MAIN_RISE.value,
    consecutive: int = 0,
    is_main_line: bool = False,
    stock_change: float = 5.0,
    market_change: float = 1.0,
    risk: float = 40.0,
) -> FusionDecisionInput:
    return FusionDecisionInput(
        youzi_result=make_youzi_result(youzi_score, phase),
        quant_result=make_quant_result(quant_score),
        consecutive_limit_ups=consecutive,
        is_main_line=is_main_line,
        stock_change_pct=stock_change,
        market_change_pct=market_change,
        risk_score=risk,
    )


# ============================================================================
# Step1: 情绪周期自适应权重
# ============================================================================


class TestAdaptiveWeights:
    def test_freezing_weights(self, engine: DualEngineFusionDecisionEngine):
        """冰点期: 量化70% + 游资30%。"""
        yw, qw = engine.determine_adaptive_weights(EmotionPhase.FREEZING.value)
        assert yw == pytest.approx(0.30)
        assert qw == pytest.approx(0.70)

    def test_reversal_weights(self, engine: DualEngineFusionDecisionEngine):
        """反核期: 均衡50%/50%。"""
        yw, qw = engine.determine_adaptive_weights(EmotionPhase.REVERSAL.value)
        assert yw == pytest.approx(0.50)
        assert qw == pytest.approx(0.50)

    def test_main_rise_weights(self, engine: DualEngineFusionDecisionEngine):
        """主升期: 游资70% + 量化30%。"""
        yw, qw = engine.determine_adaptive_weights(EmotionPhase.MAIN_RISE.value)
        assert yw == pytest.approx(0.70)
        assert qw == pytest.approx(0.30)

    def test_mania_weights(self, engine: DualEngineFusionDecisionEngine):
        """疯狂期: 游资80% + 量化20%。"""
        yw, qw = engine.determine_adaptive_weights(EmotionPhase.MANIA.value)
        assert yw == pytest.approx(0.80)
        assert qw == pytest.approx(0.20)

    def test_retreat_weights(self, engine: DualEngineFusionDecisionEngine):
        """退潮期: 量化60% + 游资40%。"""
        yw, qw = engine.determine_adaptive_weights(EmotionPhase.RETREAT.value)
        assert yw == pytest.approx(0.40)
        assert qw == pytest.approx(0.60)

    def test_unknown_phase_default(self, engine: DualEngineFusionDecisionEngine):
        """未知阶段 → 基准权重60%/40%。"""
        yw, qw = engine.determine_adaptive_weights(EmotionPhase.UNKNOWN.value)
        assert yw == pytest.approx(0.60)
        assert qw == pytest.approx(0.40)

    def test_weights_sum_to_one(self, engine: DualEngineFusionDecisionEngine):
        """所有阶段权重和为1.0。"""
        for phase in EmotionPhase:
            yw, qw = engine.determine_adaptive_weights(phase.value)
            assert yw + qw == pytest.approx(1.0)


# ============================================================================
# Step2: 融合评分
# ============================================================================


class TestFusedScore:
    def test_fused_score_range(self, engine: DualEngineFusionDecisionEngine):
        result = engine.analyze(make_input())
        assert 0.0 <= result.fused_score <= 100.0

    def test_main_rise_fused_score(self, engine: DualEngineFusionDecisionEngine):
        """主升期: 融合分 = 0.7*youzi + 0.3*quant。"""
        result = engine.analyze(make_input(youzi_score=80.0, quant_score=60.0, phase=EmotionPhase.MAIN_RISE.value))
        expected = 0.7 * 80.0 + 0.3 * 60.0  # 74.0
        assert result.fused_score == pytest.approx(expected)

    def test_freezing_fused_score(self, engine: DualEngineFusionDecisionEngine):
        """冰点期: 融合分 = 0.3*youzi + 0.7*quant。"""
        result = engine.analyze(make_input(youzi_score=20.0, quant_score=50.0, phase=EmotionPhase.FREEZING.value))
        expected = 0.3 * 20.0 + 0.7 * 50.0  # 41.0
        assert result.fused_score == pytest.approx(expected)

    def test_capped_at_100(self, engine: DualEngineFusionDecisionEngine):
        """融合分不超过100。"""
        result = engine.analyze(make_input(youzi_score=100.0, quant_score=100.0, phase=EmotionPhase.MANIA.value))
        assert result.fused_score <= 100.0


# ============================================================================
# Step3: 6类决策分类
# ============================================================================


class TestDecisionClassification:
    def test_main_leader(self, engine: DualEngineFusionDecisionEngine):
        """融合>=80 + 游资>=70 + 量化>=70 + 主线 → 主升龙头。"""
        result = engine.analyze(
            make_input(
                youzi_score=85.0,
                quant_score=80.0,
                phase=EmotionPhase.MAIN_RISE.value,
                is_main_line=True,
            )
        )
        assert result.decision == FusionDecision.MAIN_LEADER.value

    def test_second_to_third(self, engine: DualEngineFusionDecisionEngine):
        """融合>=65 + 连板>=2 → 二进三。"""
        result = engine.analyze(
            make_input(
                youzi_score=70.0,
                quant_score=65.0,
                phase=EmotionPhase.MAIN_RISE.value,
                consecutive=2,
            )
        )
        assert result.decision == FusionDecision.SECOND_TO_THIRD.value

    def test_recovery(self, engine: DualEngineFusionDecisionEngine):
        """量化>=70 + 游资40-65 → 复苏。"""
        result = engine.analyze(
            make_input(
                youzi_score=50.0,
                quant_score=75.0,
                phase=EmotionPhase.REVERSAL.value,
                consecutive=0,
            )
        )
        assert result.decision == FusionDecision.RECOVERY.value

    def test_fake_strong(self, engine: DualEngineFusionDecisionEngine):
        """游资>=60 + 量化<50 → 伪强。"""
        result = engine.analyze(
            make_input(
                youzi_score=65.0,
                quant_score=40.0,
                phase=EmotionPhase.MANIA.value,
            )
        )
        assert result.decision == FusionDecision.FAKE_STRONG.value

    def test_follower(self, engine: DualEngineFusionDecisionEngine):
        """融合分50-65 → 跟风。"""
        result = engine.analyze(
            make_input(
                youzi_score=55.0,
                quant_score=55.0,
                phase=EmotionPhase.REVERSAL.value,
            )
        )
        assert result.decision == FusionDecision.FOLLOWER.value

    def test_inverse_board(self, engine: DualEngineFusionDecisionEngine):
        """连板=1 + 涨停 + 高风险 → 地天反包。"""
        result = engine.analyze(
            make_input(
                youzi_score=60.0,
                quant_score=55.0,
                phase=EmotionPhase.REVERSAL.value,
                consecutive=1,
                stock_change=10.0,
                risk=65.0,
            )
        )
        assert result.decision == FusionDecision.INVERSE_BOARD.value

    def test_neutral(self, engine: DualEngineFusionDecisionEngine):
        """低分且不匹配任何类别 → 中性。"""
        result = engine.analyze(
            make_input(
                youzi_score=20.0,
                quant_score=30.0,
                phase=EmotionPhase.FREEZING.value,
            )
        )
        assert result.decision == FusionDecision.NEUTRAL.value


# ============================================================================
# Step4: PDF分布信号
# ============================================================================


class TestPDFSignal:
    def test_long_signal(self, engine: DualEngineFusionDecisionEngine):
        """融合分>=65 → 做多。"""
        result = engine.analyze(make_input(youzi_score=80.0, quant_score=80.0, phase=EmotionPhase.MAIN_RISE.value))
        assert result.pdf_signal.direction == SignalDirection.LONG.value

    def test_short_signal(self, engine: DualEngineFusionDecisionEngine):
        """融合分<=35 → 做空。"""
        result = engine.analyze(make_input(youzi_score=20.0, quant_score=20.0, phase=EmotionPhase.FREEZING.value))
        assert result.pdf_signal.direction == SignalDirection.SHORT.value

    def test_neutral_signal(self, engine: DualEngineFusionDecisionEngine):
        """融合分35-65 → 观望。"""
        result = engine.analyze(make_input(youzi_score=50.0, quant_score=50.0, phase=EmotionPhase.REVERSAL.value))
        assert result.pdf_signal.direction == SignalDirection.NEUTRAL.value

    def test_confidence_range(self, engine: DualEngineFusionDecisionEngine):
        result = engine.analyze(make_input())
        assert 0.0 <= result.pdf_signal.confidence <= 100.0

    def test_high_confidence_extreme_score(self, engine: DualEngineFusionDecisionEngine):
        """极端分数 → 高置信度。"""
        result = engine.analyze(make_input(youzi_score=95.0, quant_score=95.0, phase=EmotionPhase.MAIN_RISE.value))
        assert result.pdf_signal.confidence >= 80.0

    def test_tail_risk_high(self, engine: DualEngineFusionDecisionEngine):
        """高风险评分 → 高尾部风险。"""
        result = engine.analyze(make_input(youzi_score=60.0, quant_score=60.0, risk=65.0))
        assert result.pdf_signal.tail_risk == "高"

    def test_tail_risk_low(self, engine: DualEngineFusionDecisionEngine):
        """低风险评分 → 低尾部风险。"""
        result = engine.analyze(make_input(youzi_score=60.0, quant_score=60.0, risk=20.0))
        assert result.pdf_signal.tail_risk == "低"

    def test_relative_value_good(self, engine: DualEngineFusionDecisionEngine):
        """超额收益>=5% → 相对价值好。"""
        result = engine.analyze(
            make_input(
                youzi_score=60.0,
                quant_score=60.0,
                stock_change=10.0,
                market_change=2.0,
            )
        )
        assert result.pdf_signal.relative_value == "好"

    def test_relative_value_poor(self, engine: DualEngineFusionDecisionEngine):
        """跑输大盘 → 相对价值差。"""
        result = engine.analyze(
            make_input(
                youzi_score=40.0,
                quant_score=40.0,
                stock_change=-2.0,
                market_change=1.0,
            )
        )
        assert result.pdf_signal.relative_value == "差"


# ============================================================================
# 综合
# ============================================================================


class TestOverall:
    def test_audit_trail_populated(self, engine: DualEngineFusionDecisionEngine):
        result = engine.analyze(make_input())
        assert len(result.audit_trail) >= 4  # 引擎输入+权重+融合+决策+PDF

    def test_emotion_phase_propagated(self, engine: DualEngineFusionDecisionEngine):
        """情绪周期从游资引擎传播到融合结果。"""
        result = engine.analyze(make_input(phase=EmotionPhase.MANIA.value))
        assert result.emotion_phase == EmotionPhase.MANIA.value

    def test_weights_in_result(self, engine: DualEngineFusionDecisionEngine):
        """结果包含实际使用的权重。"""
        result = engine.analyze(make_input(phase=EmotionPhase.MAIN_RISE.value))
        assert result.youzi_weight == pytest.approx(0.70)
        assert result.quant_weight == pytest.approx(0.30)

    def test_full_strong_scenario(self, engine: DualEngineFusionDecisionEngine):
        """全面强势 → 主升龙头 + 做多。"""
        result = engine.analyze(
            make_input(
                youzi_score=90.0,
                quant_score=85.0,
                phase=EmotionPhase.MAIN_RISE.value,
                is_main_line=True,
                consecutive=3,
                stock_change=10.0,
                market_change=1.0,
                risk=15.0,
            )
        )
        assert result.decision == FusionDecision.MAIN_LEADER.value
        assert result.pdf_signal.direction == SignalDirection.LONG.value
        assert result.fused_score >= 80.0

    def test_full_weak_scenario(self, engine: DualEngineFusionDecisionEngine):
        """全面弱势 → 中性 + 做空。"""
        result = engine.analyze(
            make_input(
                youzi_score=15.0,
                quant_score=20.0,
                phase=EmotionPhase.FREEZING.value,
                stock_change=-3.0,
                market_change=1.0,
                risk=70.0,
            )
        )
        assert result.decision == FusionDecision.NEUTRAL.value
        assert result.pdf_signal.direction == SignalDirection.SHORT.value
        assert result.pdf_signal.tail_risk == "高"


# ============================================================================
# 降级
# ============================================================================


class TestDegradation:
    def test_none_youzi_result(self, engine: DualEngineFusionDecisionEngine):
        inp = FusionDecisionInput(
            youzi_result=None,  # type: ignore[arg-type]
            quant_result=make_quant_result(),
        )
        result = engine.analyze(inp)
        assert result.is_degraded is True

    def test_none_quant_result(self, engine: DualEngineFusionDecisionEngine):
        inp = FusionDecisionInput(
            youzi_result=make_youzi_result(),
            quant_result=None,  # type: ignore[arg-type]
        )
        result = engine.analyze(inp)
        assert result.is_degraded is True

    def test_negative_consecutive(self, engine: DualEngineFusionDecisionEngine):
        result = engine.analyze(make_input(consecutive=-1))
        assert result.is_degraded is True

    def test_invalid_risk(self, engine: DualEngineFusionDecisionEngine):
        result = engine.analyze(make_input(risk=150.0))
        assert result.is_degraded is True


# ============================================================================
# 配置可定制性
# ============================================================================


class TestConfigCustomization:
    def test_custom_base_weights(self):
        """自定义基准权重——量化主导。"""
        cfg = FusionDecisionConfig(
            base_youzi_weight=0.30,
            base_quant_weight=0.70,
        )
        engine = DualEngineFusionDecisionEngine(cfg)
        yw, qw = engine.determine_adaptive_weights(EmotionPhase.UNKNOWN.value)
        assert yw == pytest.approx(0.30)
        assert qw == pytest.approx(0.70)

    def test_custom_phase_weights(self):
        """自定义主升期权重——更极端游资主导。"""
        cfg = FusionDecisionConfig(
            phase_weights_main_rise=(0.90, 0.10),
        )
        engine = DualEngineFusionDecisionEngine(cfg)
        yw, qw = engine.determine_adaptive_weights(EmotionPhase.MAIN_RISE.value)
        assert yw == pytest.approx(0.90)
        assert qw == pytest.approx(0.10)

    def test_custom_decision_thresholds(self):
        """自定义主升龙头阈值——更高要求。"""
        cfg = FusionDecisionConfig(
            main_leader_fused_min=90.0,
            main_leader_youzi_min=85.0,
            main_leader_quant_min=85.0,
        )
        engine = DualEngineFusionDecisionEngine(cfg)
        result = engine.analyze(
            make_input(
                youzi_score=80.0,
                quant_score=80.0,
                phase=EmotionPhase.MAIN_RISE.value,
                is_main_line=True,
            )
        )
        # 80 < 85 → 不满足自定义阈值
        assert result.decision != FusionDecision.MAIN_LEADER.value

    def test_custom_pdf_thresholds(self):
        """自定义PDF阈值——更保守(做多需>=75)。"""
        cfg = FusionDecisionConfig(long_threshold=75.0)
        engine = DualEngineFusionDecisionEngine(cfg)
        result = engine.analyze(
            make_input(
                youzi_score=65.0,
                quant_score=65.0,
                phase=EmotionPhase.REVERSAL.value,
            )
        )
        # 融合分≈65 < 75 → 观望(而非做多)
        assert result.pdf_signal.direction == SignalDirection.NEUTRAL.value

    def test_frozen_config(self):
        cfg = FusionDecisionConfig()
        with pytest.raises(AttributeError):
            cfg.base_youzi_weight = 0.50  # type: ignore[misc]
