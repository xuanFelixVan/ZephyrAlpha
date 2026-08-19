# [A_test] module_id: MOD-EXE-daban_signal_decision_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_core.test_daban_signal_decision
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""打板信号前置门控 + 7 类交易动作决策单元测试（§3.14 缺失#8 / §3.13 缺失#3）。

覆盖：
  - pre_validate_daban_signal：四权重打分（健康40/高度20/共振20/跟风20）、
    ≥70 放行 / 50-70 CONDITIONAL 降仓 / <50 否决三档门控、各退化组合
  - classify_decision_v192：冰点/反核+跌停反抽→REFLUSH_DIVE 门控、
    主升/疯狂 BOARD 路径、CONTINUE/INVERSE_BOARD/WATCH/WAIT/REJECT 六类、
    退潮阈值拉满事实禁板、未知 phase KeyError

依据：24_daban_strategy_detail.md v1.9.3 §3.14 缺失#8 / v1.9.2 §3.13 缺失#3
"""

from __future__ import annotations

import pytest

from zephyr.ex_core.daban_signal_decision import (
    PHASE_THRESHOLDS,
    classify_decision_v192,
    pre_validate_daban_signal,
)

# ---------------------------------------------------------------------
# pre_validate_daban_signal（§3.14#8）
# ---------------------------------------------------------------------


class TestPreValidateDabanSignal:
    def test_full_quality_pass(self):
        """PERFECT+2板+共振1.0+跟风5只→满分100→放行。"""
        out = pre_validate_daban_signal('PERFECT', 2, 1.0, 5)
        assert out['pass'] is True
        assert out['score'] == 100

    def test_pass_boundary_70(self):
        """PERFECT(40)+1板(10)+共振0.5(10)+跟风3只(12)=72→放行。"""
        out = pre_validate_daban_signal('PERFECT', 1, 0.5, 3)
        assert out['pass'] is True
        assert out['score'] == 72

    def test_conditional_band(self):
        """FRACTURE(15)+3板(15)+共振0.8(16)+跟风3只(12)=58→CONDITIONAL 降仓50%。"""
        out = pre_validate_daban_signal('FRACTURE', 3, 0.8, 3)
        assert out['pass'] == 'CONDITIONAL'
        assert out['score'] == 58
        assert '降仓50%' in out['reason']

    def test_reject_lone_dragon(self):
        """LONE_DRAGON(5)+1板(10)+共振0.1(2)+跟风0只(0)=17→否决。"""
        out = pre_validate_daban_signal('LONE_DRAGON', 1, 0.1, 0)
        assert out['pass'] is False
        assert '质量极低' in out['reason']
        assert '梯队单薄' in out['reason']

    def test_reject_collapse(self):
        """COLLAPSE(0)+6板(5)+共振0(0)+跟风0(0)=5→否决，含高度风险理由。"""
        out = pre_validate_daban_signal('COLLAPSE', 6, 0.0, 0)
        assert out['pass'] is False
        assert '6板高度风险' in out['reason']

    def test_height_2_optimal(self):
        """2板最优拿满 20 分（晋级率~50% 主升期最佳标的）。"""
        out = pre_validate_daban_signal('PERFECT', 2, 0.3, 3)
        assert out['score'] == 40 + 20 + 6 + 12

    def test_height_3_4_mid(self):
        """3-4板各 15 分。"""
        out3 = pre_validate_daban_signal('PERFECT', 3, 0.3, 3)
        out4 = pre_validate_daban_signal('PERFECT', 4, 0.3, 3)
        assert out3['score'] == 40 + 15 + 6 + 12
        assert out4['score'] == 40 + 15 + 6 + 12

    def test_follow_count_capped_at_20(self):
        """跟风股权重 min(n*4,20) 封顶——10只→20 分。"""
        out = pre_validate_daban_signal('PERFECT', 2, 0.5, 10)
        assert out['score'] == 40 + 20 + 10 + 20

    def test_sector_resonance_low_reason(self):
        """共振<0.3→记入孤板风险理由。"""
        out = pre_validate_daban_signal('FRACTURE', 2, 0.2, 5)
        assert '板块共振不足→孤板风险' in out['reason']

    def test_unknown_health_zero_score(self):
        """退化：未知 health 字符串→健康度 0 分不崩。"""
        out = pre_validate_daban_signal('UNKNOWN', 2, 0.8, 5)
        assert out['score'] == 0 + 20 + 16 + 20
        assert out['pass'] == 'CONDITIONAL'


# ---------------------------------------------------------------------
# classify_decision_v192（§3.13#3）
# ---------------------------------------------------------------------


class TestClassifyDecisionV192:
    def test_reflush_dive_ice_point(self):
        """冰点+跌停反抽+游资40+量化60→REFLUSH_DIVE 反核入场。"""
        assert classify_decision_v192(40, 60, '冰点', is_limit_down_rebound=True) == 'REFLUSH_DIVE'

    def test_reflush_dive_fanhe_phase(self):
        """反核期+跌停反抽+双分达标→REFLUSH_DIVE。"""
        assert classify_decision_v192(50, 70, '反核', is_limit_down_rebound=True) == 'REFLUSH_DIVE'

    def test_reflush_dive_insufficient_scores_wait(self):
        """冰点+跌停反抽但游资<40→WAIT。"""
        assert classify_decision_v192(30, 70, '冰点', is_limit_down_rebound=True) == 'WAIT'

    def test_ice_point_without_rebound_not_reflush(self):
        """冰点但无跌停反抽→走打板路径（threshold=20，非主升/疯狂→WATCH）。"""
        assert classify_decision_v192(25, 65, '冰点', is_limit_down_rebound=False) == 'WATCH'

    def test_board_main_uptrend(self):
        """主升：游资≥40+量化≥60→BOARD。"""
        assert classify_decision_v192(50, 60, '主升') == 'BOARD'

    def test_board_frenzy(self):
        """疯狂：游资≥65+量化≥60→BOARD。"""
        assert classify_decision_v192(70, 60, '疯狂') == 'BOARD'

    def test_frenzy_below_threshold_watch(self):
        """疯狂期游资 60<65 但≥52(=65*0.8)+量化≥70→CONTINUE。"""
        assert classify_decision_v192(60, 70, '疯狂') == 'CONTINUE'

    def test_continue(self):
        """主升：游资≥32(=40*0.8)+量化≥70→CONTINUE。"""
        assert classify_decision_v192(35, 70, '主升') == 'CONTINUE'

    def test_inverse_board(self):
        """游资≥60+量化≥75（且未命中 BOARD/CONTINUE 门槛）→INVERSE_BOARD 地天反包。"""
        # 主升 threshold=40：emotion=60≥40 且 tech=78≥60 → BOARD 先命中。
        # 用疯狂期绕开 BOARD：emotion 60<65，tech 78<... continue 需 tech≥70 且 emotion≥52→60≥52 命中 CONTINUE。
        # 构造：退潮期 threshold=85——emotion 60<85，60<68(85*0.8)，emotion≥60+tech≥75→INVERSE_BOARD。
        assert classify_decision_v192(60, 75, '退潮') == 'INVERSE_BOARD'

    def test_watch(self):
        """游资≥40+量化≥50→WATCH（退潮期绕开 BOARD）。"""
        assert classify_decision_v192(45, 55, '退潮') == 'WATCH'

    def test_wait_emotion_below_20(self):
        """游资<20→WAIT 冰点等待。"""
        assert classify_decision_v192(15, 30, '退潮') == 'WAIT'

    def test_reject_default(self):
        """游资 25（20-40 之间无分支命中）→REJECT。"""
        assert classify_decision_v192(25, 30, '退潮') == 'REJECT'

    def test_retreat_phase_blocks_board(self):
        """退潮期 threshold=85：游资 80+量化 90 仍不到 85→不 BOARD（事实禁板）。"""
        assert classify_decision_v192(80, 90, '退潮') != 'BOARD'

    def test_unknown_phase_key_error(self):
        """退化：未知 phase→KeyError（spec 假定合法阶段，调用方负责）。"""
        with pytest.raises(KeyError):
            classify_decision_v192(50, 60, '横盘')

    def test_phase_thresholds_cover_five_phases(self):
        """PHASE_THRESHOLDS 覆盖 §3.2 五阶段。"""
        assert set(PHASE_THRESHOLDS) == {'冰点', '反核', '主升', '疯狂', '退潮'}
