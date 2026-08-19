# [A_test] module_id: MOD-EXE-daban_named_functions_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_core.test_daban_named_functions
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""打板 8 具名函数单元测试（24_daban_strategy_detail §3.1/§3.9/§3.11）。

覆盖：梯队健康四档 / 死亡池扣分 / 竞价三维门控 / 纸老虎否决 / 封单结构双指标 /
次日溢价三维预测 / 回封生死线 / 量化席位双阈值，含边界与退化输入。

依据：24_daban_strategy_detail.md §3.1（v1.5.0）/ §3.9（v1.6.0）/ §3.11（v1.8.0）
"""

from __future__ import annotations

import pytest

from zephyr.ex_core.daban_named_functions import (
    classify_echelon_health,
    classify_reflush_board,
    detect_auction_paper_tiger,
    detect_quant_seat_warning,
    forecast_next_day_premium,
    score_auction_3d,
    score_consecutive_height_with_death_pool,
    score_seal_structure,
)

# ---------------------------------------------------------------------
# classify_echelon_health（§3.1）
# ---------------------------------------------------------------------


class TestClassifyEchelonHealth:
    def test_perfect_ladder(self):
        assert classify_echelon_health({1: 8, 2: 4, 3: 2}) == 'PERFECT'

    def test_fracture_mid_gap(self):
        """中位断层：1板/3板有、2板断档→FRACTURE。"""
        assert classify_echelon_health({1: 8, 3: 2}) == 'FRACTURE'

    def test_fracture_no_first_board(self):
        """最高板≥2 但无首板支撑→FRACTURE。"""
        assert classify_echelon_health({2: 3}) == 'FRACTURE'

    def test_lone_dragon_single_stock(self):
        """全场仅存 1 只（孤板/孤龙）→LONE_DRAGON。"""
        assert classify_echelon_health({1: 1}) == 'LONE_DRAGON'
        assert classify_echelon_health({3: 1}) == 'LONE_DRAGON'

    def test_collapse_empty(self):
        assert classify_echelon_health({}) == 'COLLAPSE'

    def test_collapse_all_zero_counts(self):
        """退化：家数全 0→视同崩塌。"""
        assert classify_echelon_health({1: 0, 2: 0}) == 'COLLAPSE'

    def test_single_level_multi_stock_perfect(self):
        """仅首板但多家→单级完整梯队 PERFECT。"""
        assert classify_echelon_health({1: 5}) == 'PERFECT'


# ---------------------------------------------------------------------
# score_consecutive_height_with_death_pool（§3.1）
# ---------------------------------------------------------------------


class TestDeathPool:
    def test_fracture_3_board_deduct_40(self):
        out = score_consecutive_height_with_death_pool(80, 3, 'FRACTURE')
        assert out['score'] == 40
        assert out['deduction'] == 40

    def test_lone_dragon_4_board_deduct_30(self):
        out = score_consecutive_height_with_death_pool(80, 4, 'LONE_DRAGON')
        assert out['score'] == 50
        assert out['deduction'] == 30

    def test_perfect_no_deduction(self):
        """完美梯队维持原评分。"""
        out = score_consecutive_height_with_death_pool(80, 3, 'PERFECT')
        assert out['score'] == 80
        assert out['deduction'] == 0

    def test_fracture_2_board_no_deduction(self):
        """死亡池只扣 3/4 板——2 板不扣。"""
        out = score_consecutive_height_with_death_pool(80, 2, 'FRACTURE')
        assert out['deduction'] == 0

    def test_collapse_3_board_deduct(self):
        """COLLAPSE 按死亡池同口径扣分（保守延伸）。"""
        out = score_consecutive_height_with_death_pool(80, 3, 'COLLAPSE')
        assert out['deduction'] == 40

    def test_degenerate_score_floor_zero(self):
        """退化：低分再扣→下限 0 不为负。"""
        out = score_consecutive_height_with_death_pool(20, 3, 'FRACTURE')
        assert out['score'] == 0


# ---------------------------------------------------------------------
# score_auction_3d（§3.9）
# ---------------------------------------------------------------------


class TestScoreAuction3d:
    def test_confirm(self):
        out = score_auction_3d(28, 27, 38)
        assert out['total'] == 93
        assert out['decision'] == 'CONFIRM'

    def test_confirm_boundary_80(self):
        out = score_auction_3d(25, 25, 30)
        assert out['total'] == 80
        assert out['decision'] == 'CONFIRM'

    def test_watch_band(self):
        out = score_auction_3d(20, 20, 25)
        assert out['total'] == 65
        assert out['decision'] == 'WATCH'

    def test_reject_below_60(self):
        out = score_auction_3d(10, 15, 20)
        assert out['total'] == 45
        assert out['decision'] == 'REJECT'

    def test_degenerate_clamp_negative_and_overflow(self):
        """退化：负分夹 0、超上限夹 30/30/40。"""
        out = score_auction_3d(-5, 99, 99)
        assert out['market'] == 0
        assert out['sector'] == 30
        assert out['stock'] == 40
        assert out['total'] == 70


# ---------------------------------------------------------------------
# detect_auction_paper_tiger（§3.9）
# ---------------------------------------------------------------------


class TestPaperTiger:
    def test_paper_tiger_veto(self):
        """涨幅 7.5%+匹配量 2%→纸老虎一票否决。"""
        out = detect_auction_paper_tiger(0.075, 0.02)
        assert out['is_paper_tiger'] is True
        assert out['veto'] is True

    def test_boundary_gain_band(self):
        """涨幅恰 7%/8% 仍在判定带内。"""
        assert detect_auction_paper_tiger(0.07, 0.02)['is_paper_tiger'] is True
        assert detect_auction_paper_tiger(0.08, 0.02)['is_paper_tiger'] is True

    def test_volume_exactly_3pct_not_tiger(self):
        """匹配量恰 3%→<3% 不成立→非纸老虎。"""
        assert detect_auction_paper_tiger(0.075, 0.03)['is_paper_tiger'] is False

    def test_gain_outside_band_not_tiger(self):
        """涨幅 9%（超带）即使量小也不是纸老虎口径。"""
        assert detect_auction_paper_tiger(0.09, 0.01)['is_paper_tiger'] is False

    def test_normal_auction(self):
        out = detect_auction_paper_tiger(0.05, 0.10)
        assert out['veto'] is False


# ---------------------------------------------------------------------
# score_seal_structure（§3.11①）
# ---------------------------------------------------------------------


class TestSealStructure:
    def test_stable(self):
        """封流比 6%+封成比 12→双稳定 STABLE。"""
        out = score_seal_structure(0.06, 12)
        assert out['score'] == 100
        assert out['label'] == 'STABLE'

    def test_weak_both(self):
        """封流比 1%+封成比 0.5→双弱 WEAK。"""
        out = score_seal_structure(0.01, 0.5)
        assert out['score'] == 0
        assert out['label'] == 'WEAK'

    def test_flow_boundary_5pct(self):
        out = score_seal_structure(0.05, 12)
        assert out['score'] == 100

    def test_flow_boundary_2pct(self):
        out = score_seal_structure(0.02, 12)
        assert out['score'] == 75  # 25+50

    def test_success_boundary_10(self):
        out = score_seal_structure(0.06, 10)
        assert out['score'] == 75  # 50+25（>10 才满分）

    def test_neutral_band(self):
        out = score_seal_structure(0.03, 5)
        assert out['score'] == 50
        assert out['label'] == 'NEUTRAL'


# ---------------------------------------------------------------------
# forecast_next_day_premium（§3.11②）
# ---------------------------------------------------------------------


class TestForecastPremium:
    def test_strong_premium(self):
        """9:55 首封+量比 3+封流比 6%→强溢价区间 [2%,5%]。"""
        out = forecast_next_day_premium('09:55', 3.0, 0.06)
        assert out['score'] == 100
        assert out['premium_low'] == 0.02
        assert out['premium_high'] == 0.05
        assert '持有' in out['advice']

    def test_neutral_premium(self):
        """11:00 封板(25)+量比 6(15)+封流比 3%(15)=55→中性区间。"""
        out = forecast_next_day_premium('11:00', 6.0, 0.03)
        assert out['score'] == 55
        assert out['premium_low'] == -0.01
        assert out['premium_high'] == 0.02

    def test_weak_premium_tail_raid(self):
        """14:45 尾盘偷袭(0)+缩量 0.5(5)+封流比 1%(5)=10→低开预警。"""
        out = forecast_next_day_premium('14:45', 0.5, 0.01)
        assert out['score'] == 10
        assert out['premium_high'] == -0.01
        assert '低开预警' in out['advice']

    def test_time_boundary_10am(self):
        """边界：恰 10:00 首封仍满分（≤10:00，对齐 §3.4 C8）。"""
        out = forecast_next_day_premium('10:00', 3.0, 0.06)
        assert out['score'] == 100

    def test_degenerate_extreme_volume(self):
        """退化：爆量>8→量能 5 分不崩。"""
        out = forecast_next_day_premium('09:45', 12.0, 0.06)
        assert out['score'] == 40 + 5 + 30


# ---------------------------------------------------------------------
# classify_reflush_board（§3.11③）
# ---------------------------------------------------------------------


class TestReflushBoard:
    def test_benign_reseal(self):
        """10 分钟内回封+封单递增→良性持有。"""
        out = classify_reflush_board(True, 10, True)
        assert out['label'] == 'BENIGN_RESEAL'
        assert out['action'] == 'HOLD'

    def test_benign_boundary_15min(self):
        out = classify_reflush_board(True, 15, True)
        assert out['label'] == 'BENIGN_RESEAL'

    def test_weak_reseal_slow(self):
        """18 分钟才回封→弱回封预警。"""
        out = classify_reflush_board(True, 18, True)
        assert out['label'] == 'WEAK_RESEAL'

    def test_weak_reseal_seal_not_increasing(self):
        """快速回封但封单递减→弱回封。"""
        out = classify_reflush_board(True, 10, False)
        assert out['label'] == 'WEAK_RESEAL'

    def test_support_collapse(self):
        """25 分钟无法回封→承接崩塌离场。"""
        out = classify_reflush_board(False, 25, False)
        assert out['label'] == 'SUPPORT_COLLAPSE'
        assert out['action'] == 'EXIT'

    def test_collapse_boundary_20min(self):
        out = classify_reflush_board(False, 20, False)
        assert out['label'] == 'SUPPORT_COLLAPSE'

    def test_observe_window(self):
        """炸板 16 分钟未回封→15-20 分钟生死线观察窗。"""
        out = classify_reflush_board(False, 16, False)
        assert out['label'] == 'OBSERVE'
        assert out['action'] == 'WATCH'


# ---------------------------------------------------------------------
# detect_quant_seat_warning（§3.11④）
# ---------------------------------------------------------------------


class TestQuantSeatWarning:
    def test_hard(self):
        out = detect_quant_seat_warning(0.75)
        assert out['level'] == 'HARD'
        assert out['weight_discount'] == pytest.approx(0.30)
        assert out['alert'] is True

    def test_hard_boundary_70pct_not_trigger(self):
        """恰 70%→>70% 不成立→落 SOFT。"""
        out = detect_quant_seat_warning(0.70)
        assert out['level'] == 'SOFT'
        assert out['weight_discount'] == pytest.approx(0.15)

    def test_soft(self):
        out = detect_quant_seat_warning(0.60)
        assert out['level'] == 'SOFT'
        assert out['alert'] is False

    def test_soft_boundary_58pct_not_trigger(self):
        """恰 58%→>58% 不成立→NONE。"""
        out = detect_quant_seat_warning(0.58)
        assert out['level'] == 'NONE'
        assert out['weight_discount'] == 0.0

    def test_none(self):
        out = detect_quant_seat_warning(0.30)
        assert out['level'] == 'NONE'
