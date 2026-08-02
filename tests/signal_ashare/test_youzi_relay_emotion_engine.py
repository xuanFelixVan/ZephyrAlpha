"""D-SIGNAL-33 游资接力情绪引擎单元测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from zephyr.signal_ashare.youzi_relay_emotion_engine import (
    EmotionPhase,
    StrategyAction,
    YouziEmotionConfig,
    YouziEmotionInput,
    YouziRelayEmotionEngine,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def engine() -> YouziRelayEmotionEngine:
    return YouziRelayEmotionEngine()


@pytest.fixture
def config() -> YouziEmotionConfig:
    return YouziEmotionConfig()


def make_input(
    consecutive: int = 0,
    seal_amount: float = 0.0,
    float_mcap: float = 1e9,
    seal_time: datetime | None = None,
    open_boards: int = 0,
    auction_rise: float = 0.0,
    auction_vol_ratio: float = 1.0,
    sector_lu: int = 0,
    market_lu: int = 50,
    breadth: float = 0.5,
) -> YouziEmotionInput:
    return YouziEmotionInput(
        consecutive_limit_ups=consecutive,
        seal_amount=seal_amount,
        float_market_cap=float_mcap,
        seal_time=seal_time,
        open_board_count=open_boards,
        auction_rise_pct=auction_rise,
        auction_volume_ratio=auction_vol_ratio,
        sector_limit_up_count=sector_lu,
        market_limit_up_count=market_lu,
        market_breadth_ratio=breadth,
    )


# ============================================================================
# 因子1: 连板高度
# ============================================================================


class TestConsecutiveHeight:
    def test_zero_consecutive(self, engine: YouziRelayEmotionEngine):
        f = engine.score_consecutive_height(0)
        assert f.score == 0.0

    def test_first_board(self, engine: YouziRelayEmotionEngine):
        f = engine.score_consecutive_height(1)
        assert f.score > 0
        assert f.score <= f.max_score

    def test_high_consecutive_capped(self, engine: YouziRelayEmotionEngine):
        """高连板封顶25分。"""
        f = engine.score_consecutive_height(10)
        assert f.score == f.max_score  # 25
        assert f.score == 25.0

    def test_monotonic_increase(self, engine: YouziRelayEmotionEngine):
        f1 = engine.score_consecutive_height(1)
        f3 = engine.score_consecutive_height(3)
        assert f3.score > f1.score


# ============================================================================
# 因子2: 封单质量
# ============================================================================


class TestSealQuality:
    def test_zero_mcap(self, engine: YouziRelayEmotionEngine):
        f = engine.score_seal_quality(1e8, 0.0)
        assert f.score == 0.0

    def test_excellent_seal(self, engine: YouziRelayEmotionEngine):
        """封流比>=10% → 满分20。"""
        f = engine.score_seal_quality(1e8, 5e8)  # 20%
        assert f.score == 20.0

    def test_good_seal(self, engine: YouziRelayEmotionEngine):
        """封流比>=5% → 15分。"""
        f = engine.score_seal_quality(5e7, 8e8)  # 6.25%
        assert f.score == 15.0

    def test_fair_seal(self, engine: YouziRelayEmotionEngine):
        """封流比>=2% → 10分。"""
        f = engine.score_seal_quality(2e7, 7e8)  # ~2.86%
        assert f.score == 10.0

    def test_poor_seal(self, engine: YouziRelayEmotionEngine):
        """封流比<2% → 按比例。"""
        f = engine.score_seal_quality(1e6, 1e9)  # 0.1%
        assert 0 < f.score < 10.0


# ============================================================================
# 因子3: 涨停时间
# ============================================================================


class TestSealTime:
    def test_none_time(self, engine: YouziRelayEmotionEngine):
        f = engine.score_seal_time(None)
        assert f.score == 0.0

    def test_one_word_board(self, engine: YouziRelayEmotionEngine):
        """9:25前 → 满分15。"""
        f = engine.score_seal_time(datetime(2026, 8, 1, 9, 20))
        assert f.score == 15.0

    def test_early_morning(self, engine: YouziRelayEmotionEngine):
        """9:25-10:00 → 12分。"""
        f = engine.score_seal_time(datetime(2026, 8, 1, 9, 35))
        assert f.score == 12.0

    def test_morning(self, engine: YouziRelayEmotionEngine):
        """10:00-11:00 → 8分。"""
        f = engine.score_seal_time(datetime(2026, 8, 1, 10, 30))
        assert f.score == 8.0

    def test_noon(self, engine: YouziRelayEmotionEngine):
        """11:00-13:30 → 5分。"""
        f = engine.score_seal_time(datetime(2026, 8, 1, 13, 0))
        assert f.score == 5.0

    def test_afternoon(self, engine: YouziRelayEmotionEngine):
        """13:30-14:30 → 3分。"""
        f = engine.score_seal_time(datetime(2026, 8, 1, 14, 0))
        assert f.score == 3.0

    def test_late(self, engine: YouziRelayEmotionEngine):
        """14:30后 → 1分。"""
        f = engine.score_seal_time(datetime(2026, 8, 1, 14, 45))
        assert f.score == 1.0


# ============================================================================
# 因子4: 开板次数
# ============================================================================


class TestOpenBoard:
    def test_zero_open(self, engine: YouziRelayEmotionEngine):
        f = engine.score_open_board(0)
        assert f.score == 15.0

    def test_one_open(self, engine: YouziRelayEmotionEngine):
        f = engine.score_open_board(1)
        assert f.score == 8.0

    def test_two_open(self, engine: YouziRelayEmotionEngine):
        f = engine.score_open_board(2)
        assert f.score == 3.0

    def test_three_plus_open(self, engine: YouziRelayEmotionEngine):
        f = engine.score_open_board(5)
        assert f.score == 0.0


# ============================================================================
# 因子5: 竞价强度
# ============================================================================


class TestAuctionStrength:
    def test_excellent_auction(self, engine: YouziRelayEmotionEngine):
        """竞价涨>=5% + 量比>=2 → 满分10。"""
        f = engine.score_auction_strength(6.0, 2.5)
        assert f.score == 10.0

    def test_good_auction(self, engine: YouziRelayEmotionEngine):
        """竞价涨3-5% → 5分+量比分。"""
        f = engine.score_auction_strength(4.0, 1.5)
        assert 5.0 < f.score < 10.0

    def test_zero_auction(self, engine: YouziRelayEmotionEngine):
        f = engine.score_auction_strength(0.0, 1.0)
        assert f.score < 5.0


# ============================================================================
# 因子6: 助攻梯队
# ============================================================================


class TestAssistEchelon:
    def test_excellent(self, engine: YouziRelayEmotionEngine):
        f = engine.score_assist_echelon(6)
        assert f.score == 10.0

    def test_good(self, engine: YouziRelayEmotionEngine):
        f = engine.score_assist_echelon(3)
        assert f.score == 7.0

    def test_fair(self, engine: YouziRelayEmotionEngine):
        f = engine.score_assist_echelon(1)
        assert f.score == 4.0

    def test_zero(self, engine: YouziRelayEmotionEngine):
        f = engine.score_assist_echelon(0)
        assert f.score == 0.0


# ============================================================================
# 情绪周期4+1阶段
# ============================================================================


class TestEmotionPhase:
    def test_freezing_phase(self, engine: YouziRelayEmotionEngine):
        """低分 + 少涨停 → 冰点。"""
        result = engine.analyze(make_input(consecutive=0, market_lu=3))
        assert result.emotion_phase == EmotionPhase.FREEZING.value

    def test_reversal_phase(self, engine: YouziRelayEmotionEngine):
        """中低分 → 反核。"""
        result = engine.analyze(make_input(consecutive=1, seal_amount=2e7, float_mcap=1e9, sector_lu=2))
        assert result.emotion_phase in (
            EmotionPhase.REVERSAL.value,
            EmotionPhase.FREEZING.value,
        )

    def test_main_rise_phase(self, engine: YouziRelayEmotionEngine):
        """中高分(40-65) → 主升。"""
        result = engine.analyze(
            make_input(
                consecutive=2,
                seal_amount=3e7,
                float_mcap=5e8,
                seal_time=datetime(2026, 8, 1, 9, 40),
                open_boards=0,
                sector_lu=3,
            )
        )
        assert result.emotion_phase == EmotionPhase.MAIN_RISE.value

    def test_mania_phase(self, engine: YouziRelayEmotionEngine):
        """高分 → 疯狂。"""
        result = engine.analyze(
            make_input(
                consecutive=5,
                seal_amount=2e8,
                float_mcap=5e8,
                seal_time=datetime(2026, 8, 1, 9, 20),
                open_boards=0,
                auction_rise=8.0,
                auction_vol_ratio=3.0,
                sector_lu=8,
            )
        )
        assert result.emotion_phase == EmotionPhase.MANIA.value

    def test_retreat_phase_by_breadth(self, engine: YouziRelayEmotionEngine):
        """高分但广度下降 → 退潮。"""
        result = engine.analyze(
            make_input(
                consecutive=6,
                seal_amount=2e8,
                float_mcap=5e8,
                seal_time=datetime(2026, 8, 1, 9, 20),
                open_boards=0,
                sector_lu=8,
                breadth=0.3,  # 广度下降
            )
        )
        assert result.emotion_phase == EmotionPhase.RETREAT.value

    def test_retreat_phase_by_open_boards(self, engine: YouziRelayEmotionEngine):
        """高连板但频繁开板 → 退潮。"""
        result = engine.analyze(
            make_input(
                consecutive=4,
                seal_amount=1e8,
                float_mcap=5e8,
                seal_time=datetime(2026, 8, 1, 9, 40),
                open_boards=4,
                sector_lu=5,
            )
        )
        assert result.emotion_phase == EmotionPhase.RETREAT.value


# ============================================================================
# 策略映射
# ============================================================================


class TestStrategyMapping:
    def test_freezing_strategy(self, engine: YouziRelayEmotionEngine):
        assert engine.map_strategy(EmotionPhase.FREEZING.value) == StrategyAction.WAIT.value

    def test_reversal_strategy(self, engine: YouziRelayEmotionEngine):
        assert engine.map_strategy(EmotionPhase.REVERSAL.value) == StrategyAction.SMALL_TRIAL.value

    def test_main_rise_strategy(self, engine: YouziRelayEmotionEngine):
        assert engine.map_strategy(EmotionPhase.MAIN_RISE.value) == StrategyAction.CORE_POSITION.value

    def test_mania_strategy(self, engine: YouziRelayEmotionEngine):
        assert engine.map_strategy(EmotionPhase.MANIA.value) == StrategyAction.LEADER_ONLY.value

    def test_retreat_strategy(self, engine: YouziRelayEmotionEngine):
        assert engine.map_strategy(EmotionPhase.RETREAT.value) == StrategyAction.CLEAR_WAIT.value


# ============================================================================
# 综合
# ============================================================================


class TestOverall:
    def test_total_score_range(self, engine: YouziRelayEmotionEngine):
        result = engine.analyze(make_input())
        assert 0.0 <= result.total_score <= 100.0

    def test_six_factors_returned(self, engine: YouziRelayEmotionEngine):
        result = engine.analyze(make_input(consecutive=2, seal_amount=5e7))
        assert len(result.factor_scores) == 6
        names = [f.name for f in result.factor_scores]
        assert "连板高度" in names
        assert "封单质量" in names
        assert "涨停时间" in names
        assert "开板次数" in names
        assert "竞价强度" in names
        assert "助攻梯队" in names

    def test_audit_trail_populated(self, engine: YouziRelayEmotionEngine):
        result = engine.analyze(make_input(consecutive=3))
        assert len(result.audit_trail) >= 8  # 6因子 + 阶段 + 策略

    def test_phase_confidence_range(self, engine: YouziRelayEmotionEngine):
        result = engine.analyze(make_input())
        assert 0.0 <= result.phase_confidence <= 100.0

    def test_high_score_scenario(self, engine: YouziRelayEmotionEngine):
        """全面强势 → 高分。"""
        result = engine.analyze(
            make_input(
                consecutive=4,
                seal_amount=1e8,
                float_mcap=5e8,
                seal_time=datetime(2026, 8, 1, 9, 25),
                open_boards=0,
                auction_rise=6.0,
                auction_vol_ratio=3.0,
                sector_lu=6,
            )
        )
        assert result.total_score > 70.0

    def test_low_score_scenario(self, engine: YouziRelayEmotionEngine):
        """全面弱势 → 低分。"""
        result = engine.analyze(
            make_input(
                consecutive=0,
                seal_amount=0,
                open_boards=3,
                sector_lu=0,
                market_lu=3,
            )
        )
        assert result.total_score < 20.0


# ============================================================================
# 降级
# ============================================================================


class TestDegradation:
    def test_negative_consecutive(self, engine: YouziRelayEmotionEngine):
        result = engine.analyze(make_input(consecutive=-1))
        assert result.is_degraded is True
        assert result.emotion_phase == EmotionPhase.UNKNOWN.value

    def test_negative_open_boards(self, engine: YouziRelayEmotionEngine):
        result = engine.analyze(make_input(open_boards=-1))
        assert result.is_degraded is True


# ============================================================================
# 配置可定制性
# ============================================================================


class TestConfigCustomization:
    def test_custom_height_scoring(self):
        """自定义连板评分——更激进。"""
        cfg = YouziEmotionConfig(consecutive_height_step=10)
        engine = YouziRelayEmotionEngine(cfg)
        f = engine.score_consecutive_height(3)
        # base(1) + (3-1)*10 = 21
        assert f.score == 21.0

    def test_custom_seal_thresholds(self):
        """自定义封单阈值——更严格。"""
        cfg = YouziEmotionConfig(
            seal_ratio_excellent=0.20,
            seal_ratio_good=0.10,
            seal_ratio_fair=0.05,
        )
        engine = YouziRelayEmotionEngine(cfg)
        f = engine.score_seal_quality(1e8, 1e9)  # 10% < 20% but >= 10%
        assert f.score == 15.0  # good tier

    def test_custom_phase_thresholds(self):
        """自定义阶段阈值——冰点范围更大。"""
        cfg = YouziEmotionConfig(phase_freezing_max=35.0, phase_reversal_max=55.0)
        engine = YouziRelayEmotionEngine(cfg)
        result = engine.analyze(make_input(consecutive=1, market_lu=10, sector_lu=1))
        # 低分应该在冰点或反核范围
        assert result.total_score <= 55.0

    def test_frozen_config(self):
        cfg = YouziEmotionConfig()
        with pytest.raises(AttributeError):
            cfg.consecutive_height_step = 99  # type: ignore[misc]
