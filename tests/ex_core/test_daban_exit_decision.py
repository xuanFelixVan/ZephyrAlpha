# [A_test] module_id: MOD-EXE-daban_exit_decision_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_core.test_daban_exit_decision
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""打板次日出场决策族单元测试（24_daban_strategy_detail §3.13 缺失#1/#7）。

覆盖：
  - NextDayExitDecision.decide：硬退出①低开闷杀 / ②持仓超时 / ③炸板+退潮、
    高开两档止盈（≥5%全卖 / ≥3%卖半）、分歧度软退出、连板晋级持有、默认等盘中确认
  - 判定优先级：硬退出先于止盈（低开闷杀不会被高开分支截胡）
  - classify_position_status：连板晋级三要件（涨停收盘+封单+梯队非孤板）、炸板判定、
    退化输入（limit_up_price=0 / 缺字段）
  - reflush_next_day_exit_decision：高开止盈 / 区间观察 / 时间止盈 / 低开止损
  - 退化：cost_basis<=0 拒绝决策（Fail-Closed，不抛异常）

依据：24_daban_strategy_detail.md v1.9.2 §3.13 缺失#1/#7
"""

from __future__ import annotations

from zephyr.ex_core.daban_exit_decision import (
    NextDayExitDecision,
    reflush_next_day_exit_decision,
)

# ---------------------------------------------------------------------
# NextDayExitDecision.decide —— 硬退出三件套
# ---------------------------------------------------------------------


class TestNextDayExitHardExit:
    def test_low_open_stop_loss(self):
        """低开≥5%→核按钮闷杀 STOP_LOSS 全卖。"""
        dec = NextDayExitDecision()
        pos = {'cost_basis': 10.0}
        out = dec.decide(pos, {'open_price': 9.4}, {}, holding_days=1)
        assert out['action'] == 'STOP_LOSS'
        assert out['qty_ratio'] == 1.0
        assert '闷杀' in out['reason']

    def test_low_open_boundary_exactly_minus_5pct(self):
        """边界：恰好 -5.0% 触发硬止损（<= 阈值）。"""
        dec = NextDayExitDecision()
        out = dec.decide({'cost_basis': 10.0}, {'open_price': 9.5}, {}, holding_days=1)
        assert out['action'] == 'STOP_LOSS'

    def test_holding_timeout_exit(self):
        """持仓≥3天且未晋级→时间退出 SELL_ALL。"""
        dec = NextDayExitDecision()
        pos = {'cost_basis': 10.0, 'consecutive_board': False}
        out = dec.decide(pos, {'open_price': 10.1}, {}, holding_days=3)
        assert out['action'] == 'SELL_ALL'
        assert '时间退出' in out['reason']

    def test_holding_timeout_but_consecutive_board_not_triggered(self):
        """持仓≥3天但已连板晋级→不触发时间退出。"""
        dec = NextDayExitDecision()
        pos = {'cost_basis': 10.0, 'consecutive_board': True}
        out = dec.decide(pos, {'open_price': 10.1}, {}, holding_days=5)
        assert out['action'] == 'HOLD'
        assert '连板晋级' in out['reason']

    def test_exploded_plus_retreat_hard_exit(self):
        """炸板+退潮→硬退出。"""
        dec = NextDayExitDecision()
        pos = {'cost_basis': 10.0, 'exploded': True, 'consecutive_board': False}
        out = dec.decide(pos, {'open_price': 10.1}, {'phase': '退潮'}, holding_days=1)
        assert out['action'] == 'SELL_ALL'
        assert '炸板+退潮' in out['reason']

    def test_exploded_without_retreat_not_hard_exit(self):
        """炸板但非退潮期→不触发硬退出③。"""
        dec = NextDayExitDecision()
        pos = {'cost_basis': 10.0, 'exploded': True, 'consecutive_board': False}
        out = dec.decide(pos, {'open_price': 10.1}, {'phase': '主升'}, holding_days=1)
        assert out['action'] == 'HOLD'


# ---------------------------------------------------------------------
# NextDayExitDecision.decide —— 止盈/软退出/持有
# ---------------------------------------------------------------------


class TestNextDayExitProfitAndHold:
    def test_high_open_tier2_sell_all(self):
        """高开≥5%→全卖。"""
        dec = NextDayExitDecision()
        out = dec.decide({'cost_basis': 10.0}, {'open_price': 10.6}, {}, holding_days=1)
        assert out['action'] == 'SELL_ALL'
        assert '≥5%' in out['reason']

    def test_high_open_tier1_sell_half(self):
        """高开≥3%但<5%→竞价卖50%。"""
        dec = NextDayExitDecision()
        out = dec.decide({'cost_basis': 10.0}, {'open_price': 10.4}, {}, holding_days=1)
        assert out['action'] == 'SELL_HALF'
        assert out['qty_ratio'] == 0.5

    def test_high_open_tier1_boundary(self):
        """边界：恰好 +3.0% 触发卖半（>= 阈值）。"""
        dec = NextDayExitDecision()
        out = dec.decide({'cost_basis': 10.0}, {'open_price': 10.3}, {}, holding_days=1)
        assert out['action'] == 'SELL_HALF'

    def test_divergence_soft_exit(self):
        """分歧度>0.5→软退出卖半。"""
        dec = NextDayExitDecision()
        out = dec.decide({'cost_basis': 10.0}, {'open_price': 10.1}, {'divergence': 0.6}, holding_days=1)
        assert out['action'] == 'SELL_HALF'
        assert '分歧度' in out['reason']

    def test_consecutive_board_hold(self):
        """连板晋级+高开→持有。"""
        dec = NextDayExitDecision()
        pos = {'cost_basis': 10.0, 'consecutive_board': True}
        out = dec.decide(pos, {'open_price': 10.2}, {}, holding_days=1)
        assert out['action'] == 'HOLD'
        assert '连板晋级' in out['reason']

    def test_default_wait_intraday(self):
        """平开无信号→等盘中确认。"""
        dec = NextDayExitDecision()
        out = dec.decide({'cost_basis': 10.0}, {'open_price': 10.0}, {}, holding_days=1)
        assert out['action'] == 'HOLD'
        assert out['qty_ratio'] == 0.0
        assert '等盘中确认' in out['reason']

    def test_priority_hard_exit_before_take_profit(self):
        """判定优先级：低开闷杀不会被止盈分支截胡（spec 判定顺序）。"""
        dec = NextDayExitDecision()
        out = dec.decide({'cost_basis': 10.0}, {'open_price': 9.0}, {'divergence': 0.9}, holding_days=1)
        assert out['action'] == 'STOP_LOSS'

    def test_degenerate_zero_cost_basis(self):
        """退化：cost_basis=0→HOLD+人工复核（不抛异常、不误导卖出）。"""
        dec = NextDayExitDecision()
        out = dec.decide({'cost_basis': 0}, {'open_price': 10.0}, {}, holding_days=1)
        assert out['action'] == 'HOLD'
        assert '人工复核' in out['reason']

    def test_degenerate_missing_cost_basis(self):
        """退化：position 缺 cost_basis 键→同上拒绝决策。"""
        dec = NextDayExitDecision()
        out = dec.decide({}, {'open_price': 10.0}, {}, holding_days=1)
        assert out['action'] == 'HOLD'
        assert '人工复核' in out['reason']


# ---------------------------------------------------------------------
# classify_position_status
# ---------------------------------------------------------------------


class TestClassifyPositionStatus:
    def test_consecutive_board_all_conditions(self):
        """连板晋级：涨停收盘+封单存在+梯队非孤板。"""
        pos = {'cost_basis': 10.0}
        t1 = {'close': 11.0, 'high': 11.0, 'limit_up_price': 11.0, 'seal_ratio': 0.05}
        out = NextDayExitDecision.classify_position_status(pos, t1, 'PERFECT')
        assert out['consecutive_board'] is True
        assert out['exploded'] is False
        assert pos['consecutive_board'] is True  # 就地回写
        assert pos['exploded'] is False

    def test_consecutive_board_rejected_by_lone_dragon(self):
        """梯队孤龙→即使涨停收盘也不算晋级。"""
        pos = {}
        t1 = {'close': 11.0, 'high': 11.0, 'limit_up_price': 11.0, 'seal_ratio': 0.05}
        out = NextDayExitDecision.classify_position_status(pos, t1, 'LONE_DRAGON')
        assert out['consecutive_board'] is False

    def test_consecutive_board_rejected_by_no_seal(self):
        """封流比≤0.1%→无封单→不算晋级。"""
        pos = {}
        t1 = {'close': 11.0, 'high': 11.0, 'limit_up_price': 11.0, 'seal_ratio': 0.0005}
        out = NextDayExitDecision.classify_position_status(pos, t1, 'PERFECT')
        assert out['consecutive_board'] is False

    def test_exploded_touched_limit_not_sealed(self):
        """炸板：盘中触涨停但收盘未封住。"""
        pos = {}
        t1 = {'close': 10.5, 'high': 11.0, 'limit_up_price': 11.0, 'seal_ratio': 0.0}
        out = NextDayExitDecision.classify_position_status(pos, t1, 'FRACTURE')
        assert out['exploded'] is True
        assert out['consecutive_board'] is False

    def test_not_exploded_when_never_touched_limit(self):
        """盘中未触涨停→不算炸板。"""
        pos = {}
        t1 = {'close': 10.2, 'high': 10.8, 'limit_up_price': 11.0, 'seal_ratio': 0.0}
        out = NextDayExitDecision.classify_position_status(pos, t1, 'PERFECT')
        assert out['exploded'] is False

    def test_degenerate_zero_limit_up_price(self):
        """退化：limit_up_price=0→晋级/炸板均 False（不崩）。"""
        pos = {}
        out = NextDayExitDecision.classify_position_status(pos, {}, 'PERFECT')
        assert out['consecutive_board'] is False
        assert out['exploded'] is False


# ---------------------------------------------------------------------
# reflush_next_day_exit_decision（§3.13#7）
# ---------------------------------------------------------------------


class TestReflushNextDayExit:
    def test_high_open_take_profit(self):
        """反核后高开≥5%→止盈全卖。"""
        out = reflush_next_day_exit_decision({'cost_basis': 10.0}, {'open_price': 10.5}, holding_days=1)
        assert out['action'] == 'SELL_ALL'
        assert '止盈' in out['reason']

    def test_mid_range_observe(self):
        """-3%<低开<+5% 且持有<5天→观察等反抽。"""
        out = reflush_next_day_exit_decision({'cost_basis': 10.0}, {'open_price': 10.1}, holding_days=2)
        assert out['action'] == 'HOLD'
        assert '观察等反抽' in out['reason']

    def test_mid_range_time_exit_after_5_days(self):
        """区间内但持有≥5天→时间止盈。"""
        out = reflush_next_day_exit_decision({'cost_basis': 10.0}, {'open_price': 10.1}, holding_days=5)
        assert out['action'] == 'SELL_ALL'
        assert '时间止盈' in out['reason']

    def test_low_open_stop_loss(self):
        """低开≤-3%→止损。"""
        out = reflush_next_day_exit_decision({'cost_basis': 10.0}, {'open_price': 9.6}, holding_days=1)
        assert out['action'] == 'STOP_LOSS'
        assert '止损' in out['reason']

    def test_low_open_boundary_exactly_minus_3pct(self):
        """边界：恰好 -3.0% 触发止损（<= 阈值）。"""
        out = reflush_next_day_exit_decision({'cost_basis': 10.0}, {'open_price': 9.7}, holding_days=1)
        assert out['action'] == 'STOP_LOSS'

    def test_degenerate_zero_cost_basis(self):
        """退化：cost_basis=0→HOLD+人工复核。"""
        out = reflush_next_day_exit_decision({'cost_basis': 0}, {'open_price': 10.0}, holding_days=1)
        assert out['action'] == 'HOLD'
        assert '人工复核' in out['reason']
