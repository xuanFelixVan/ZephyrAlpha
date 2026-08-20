# [BLUEPRINT] MOD-SELL-019 | docs/03_modules/_domain_sell_decision/sell_execution_planner/blueprint.md
# [MODULE] zephyr.sell_decision.core.sell_execution_planner
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D-EX-CORE(40号执行层订单分解) ; MOD-SELL-009(紧迫度评分消费排序结果)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 强制清仓任何时段市价单立即执行绕过融合; 止损盘中立即限价单; 止盈尾盘集中14:50-14:57; 跌停不提交排队次日; 当日买入T+1不可卖; 跌停排队亏损最大先排; KillSwitch清仓流动性差先卖
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidExecutionPlanInputError
# [TESTS] tests/sell_decision/test_sell_execution_planner.py
# [A_module] module_id=MOD-SELL-019 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Sell Execution Planner — 卖出执行编排器 (MOD-SELL-019)

卖出信号→执行计划编排: 执行时序(止损盘中立即/止盈尾盘集中/强制清仓市价立即)
+ 跌停板排队优先级 + Kill Switch 强制清仓排序。产出喂给40号执行层订单分解。

设计说明:
    - schedule_sell_order(42号 §3.8): 信号类型→(时序,订单类型)映射;
      落地T+1硬约束(当日买入不可卖)与跌停约束(不提交排队次日)
    - rank_limit_down_orders(42号 §3.8): 多标的同跌停时次日集合竞价挂单顺序——
      紧迫度降序→亏损升序→仓位降序
    - rank_kill_switch_liquidation(42号 §3.9): Kill Switch清仓顺序——
      流动性升序(差的先卖防封死跌停)→仓位降序→亏损升序
    - 合规基线: 上交所2026修订§2.4.2, 14:57-15:00收盘集合竞价不可撤单
    - 与41号买入窗口错峰: 止盈/换仓14:50-14:57与建仓同窗口方向相反(置换再平衡)

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/42_sell_flow.md §3.8/§3.9
SSoT: depgraph MOD-SELL-019
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 卖出信号类型 signal_type SellExecutionSignal
#   fields: KILL_SWITCH/BLACK_SWAN/BREAKOUT_FAIL_K/ATR_STOP/CHANDELIER_STOP/SUPPORT_BROKEN/TRAILING_TP/REBALANCE/SENTIMENT_EBB
#   code: schedule_sell_order() 参数
# - id: I2
#   name: 当前时间 current_time time
#   fields: 交易时段判断(14:57收盘竞价不可撤单分界), 可注入测试
#   code: schedule_sell_order() 参数
# - id: I3
#   name: T+1与跌停状态 buy_date/is_limit_down
#   fields: buy_date拟卖仓位买入日期(可选,T+1校验) + is_limit_down当前是否跌停
#   code: schedule_sell_order() 关键字参数
# - id: I4
#   name: 跌停持仓列表 LimitDownPosition列表
#   fields: symbol+urgency_score+unrealized_pnl_pct+position_value
#   code: rank_limit_down_orders() 参数
# - id: I5
#   name: 清仓持仓列表 LiquidationPosition列表
#   fields: symbol+liquidity_score+position_value+unrealized_pnl_pct
#   code: rank_kill_switch_liquidation() 参数
# 层: 算法
# - id: A1
#   name_zh: ① 执行时序映射
#   name_en: schedule_sell_order
#   intro: 信号类型查表得时序与订单类型, 先查T+1/跌停硬约束再排时序
#   desc: 当日买入→BLOCKED_T1(强制清仓亦不例外,交易所物理约束); 止损/止盈遇跌停→LIMIT_DOWN_QUEUE(强制清仓例外仍挂跌停价); 强制清仓→MARKET_ORDER_NOW; 止损→14:57前LIMIT_ORDER_NOW后CLOSING_AUCTION_LIMIT; 止盈换仓退潮→TAIL_BATCH_14_50
#   inputs: I1 I2 I3
#   outputs: SellOrderPlan
#   invariant: 强制清仓市价单立即执行; 止损盘中立即; 止盈尾盘集中; T+1/跌停硬约束
# - id: A2
#   name_zh: ② 跌停排队优先级排序
#   name_en: rank_limit_down_orders
#   intro: 亏损越大风控优先级越高越先排队
#   desc: sorted按(-urgency_score, unrealized_pnl_pct, -position_value)三级键排序
#   inputs: I4
#   outputs: 排序后LimitDownPosition列表
#   invariant: 紧迫度降序→亏损升序→仓位降序
# - id: A3
#   name_zh: ③ Kill Switch清仓排序
#   name_en: rank_kill_switch_liquidation
#   intro: 流动性差的先卖防封死跌停无法成交
#   desc: sorted按(liquidity_score升序, -position_value, unrealized_pnl_pct)三级键排序; 首要目标全部成交非卖好价
#   inputs: I5
#   outputs: 排序后LiquidationPosition列表
#   invariant: 流动性升序→仓位降序→亏损升序
# 层: 输出
# - id: O1
#   name_zh: 卖出执行计划 SellOrderPlan
#   name_en: SellOrderPlan
#   intro: 含action/订单类型/时序窗口说明/理由, 喂给40号执行层订单分解与PricingPolicy
#   downstream: D-EX-CORE(40号执行层)
# - id: O2
#   name_zh: 排序后持仓列表
#   name_en: list[LimitDownPosition] / list[LiquidationPosition]
#   intro: 跌停挂单顺序/KillSwitch清仓顺序, 喂给40号OpenOrderResolver
#   downstream: D-EX-CORE(40号OpenOrderResolver/PricingPolicy)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A2
# I5 --> A3
# A1 --> O1
# A2 --> O2
# A3 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, time
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "SellExecutionSignal",
    "SellOrderAction",
    "SellOrderPlan",
    "LimitDownPosition",
    "LiquidationPosition",
    "SellExecutionPlanner",
    "InvalidExecutionPlanInputError",
]

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 常量(42号 §3.8, 上交所2026修订§2.4.2)
# ──────────────────────────────────────────────────────────────────────────────

# 14:57 收盘集合竞价开始(不可撤单分界)
_CLOSING_AUCTION_START: Final[time] = time(14, 57)
# 尾盘集中执行窗口起点(14:50-14:57, 与41号建仓窗口错峰同段反向)
_TAIL_BATCH_WINDOW: Final[str] = "14:50-14:57"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举 / 数据模型
# ──────────────────────────────────────────────────────────────────────────────


class SellExecutionSignal(str, Enum):
    """卖出执行信号类型(执行编排层分类, 与收集器8类信号正交)。"""

    KILL_SWITCH = "KILL_SWITCH"  # Kill Switch 强制清仓
    BLACK_SWAN = "BLACK_SWAN"  # 黑天鹅事件(L2-D)
    BREAKOUT_FAIL_K = "BREAKOUT_FAIL_K"  # 第K次突破失败(K≥3)
    ATR_STOP = "ATR_STOP"  # ATR止损触发
    CHANDELIER_STOP = "CHANDELIER_STOP"  # Chandelier移动止损触发
    SUPPORT_BROKEN = "SUPPORT_BROKEN"  # 支撑位破位
    TRAILING_TP = "TRAILING_TP"  # 移动止盈触发
    REBALANCE = "REBALANCE"  # 置换/再平衡卖出
    SENTIMENT_EBB = "SENTIMENT_EBB"  # 情绪退潮减仓


class SellOrderAction(str, Enum):
    """卖出执行动作。"""

    MARKET_ORDER_NOW = "MARKET_ORDER_NOW"  # 市价单立即执行
    LIMIT_ORDER_NOW = "LIMIT_ORDER_NOW"  # 限价单立即挂出
    CLOSING_AUCTION_LIMIT = "CLOSING_AUCTION_LIMIT"  # 收盘集合竞价限价单
    TAIL_BATCH_14_50 = "TAIL_BATCH_14_50"  # 尾盘14:50-14:57集中挂限价单
    LIMIT_DOWN_QUEUE = "LIMIT_DOWN_QUEUE"  # 跌停不提交, 排队次日集合竞价
    BLOCKED_T1 = "BLOCKED_T1"  # 当日买入T+1不可卖
    HOLD = "HOLD"  # 无信号继续持有


@dataclass(frozen=True)
class SellOrderPlan:
    """卖出执行计划——喂给40号执行层订单分解。"""

    action: SellOrderAction
    order_type: str  # MARKET / LIMIT / NONE
    window_note: str  # 时序窗口说明
    reason: str


@dataclass(frozen=True)
class LimitDownPosition:
    """跌停持仓——排队优先级排序输入。"""

    symbol: str
    urgency_score: float  # 紧迫度(来自MOD-SELL-009)
    unrealized_pnl_pct: float  # 浮动盈亏比例(负=亏损)
    position_value: float  # 持仓金额


@dataclass(frozen=True)
class LiquidationPosition:
    """Kill Switch 待清仓持仓——清仓排序输入。"""

    symbol: str
    liquidity_score: float  # 流动性评分(低=流动性差)
    position_value: float  # 持仓金额
    unrealized_pnl_pct: float  # 浮动盈亏比例(负=亏损)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidExecutionPlanInputError(ZephyrBaseError):
    """卖出执行编排输入数据非法。"""

    error_code = "ZA-SELL-0019"


# ──────────────────────────────────────────────────────────────────────────────
# 算法
# ──────────────────────────────────────────────────────────────────────────────

# 强制清仓信号集(绕过融合, 紧迫度1.0, 市价单)
_FORCED_CLEAR_SIGNALS: Final[frozenset[SellExecutionSignal]] = frozenset(
    {
        SellExecutionSignal.KILL_SWITCH,
        SellExecutionSignal.BLACK_SWAN,
        SellExecutionSignal.BREAKOUT_FAIL_K,
    }
)

# 止损类信号集(盘中触发立即执行)
_STOP_LOSS_SIGNALS: Final[frozenset[SellExecutionSignal]] = frozenset(
    {
        SellExecutionSignal.ATR_STOP,
        SellExecutionSignal.CHANDELIER_STOP,
        SellExecutionSignal.SUPPORT_BROKEN,
    }
)

# 止盈/换仓/退潮信号集(尾盘集中执行)
_TAIL_BATCH_SIGNALS: Final[frozenset[SellExecutionSignal]] = frozenset(
    {
        SellExecutionSignal.TRAILING_TP,
        SellExecutionSignal.REBALANCE,
        SellExecutionSignal.SENTIMENT_EBB,
    }
)


class SellExecutionPlanner:
    """卖出执行编排器——时序映射 + 跌停排队 + Kill Switch 清仓排序。"""

    @staticmethod
    def schedule_sell_order(
        signal_type: SellExecutionSignal,
        current_time: time,
        *,
        buy_date: date | None = None,
        is_limit_down: bool = False,
        today: date | None = None,
    ) -> SellOrderPlan:
        """卖出执行时序映射(42号 §3.8)。

        止损/止盈触发盘中立即执行(不等尾盘), 强制清仓任何时段市价单,
        止盈/换仓可尾盘集中。落地T+1与跌停硬约束。

        Args:
            signal_type: 卖出执行信号类型
            current_time: 当前时间(判断14:57收盘竞价分界)
            buy_date: 拟卖仓位买入日期(可选, 提供时做T+1校验)
            is_limit_down: 当前是否跌停(跌停不提交, 排队次日)
            today: 当日日期(测试注入, None取date.today())

        Returns:
            SellOrderPlan

        Raises:
            InvalidExecutionPlanInputError: 输入非法
        """
        if not isinstance(signal_type, SellExecutionSignal):
            raise InvalidExecutionPlanInputError("signal_type 必须是 SellExecutionSignal 枚举")
        if not isinstance(current_time, time):
            raise InvalidExecutionPlanInputError("current_time 必须是 time 对象")

        # T+1 硬约束: 当日买入不可卖(交易所物理约束, 强制清仓亦不例外)
        if buy_date is not None:
            trade_date = today if today is not None else date.today()
            if buy_date >= trade_date:
                return SellOrderPlan(
                    action=SellOrderAction.BLOCKED_T1,
                    order_type="NONE",
                    window_note="T+1约束",
                    reason="当日买入次日才能卖(T+1), 本交易日不可提交卖单",
                )

        # 强制清仓: 任何时段市价单立即执行, 绕过融合, 紧迫度1.0
        # (跌停时仍挂跌停价排队——P0优先级, 确保有买盘即成交)
        if signal_type in _FORCED_CLEAR_SIGNALS:
            note = "市价单立即执行, 绕过融合, 紧迫度1.0"
            if is_limit_down:
                note += "; 当前跌停, 挂跌停价排队(P0优先级)"
            return SellOrderPlan(
                action=SellOrderAction.MARKET_ORDER_NOW,
                order_type="MARKET",
                window_note=note,
                reason=f"强制清仓信号 {signal_type.value}, 生存底线最高优先级",
            )

        # 跌停约束(非强制清仓): 不提交卖单, 标记待执行排队次日集合竞价
        if is_limit_down:
            return SellOrderPlan(
                action=SellOrderAction.LIMIT_DOWN_QUEUE,
                order_type="NONE",
                window_note="次日集合竞价",
                reason=(f"信号 {signal_type.value} 遇跌停板, 无法成交不提交, 标记跌停待执行排队次日集合竞价(§3.8)"),
            )

        # 止损触发: 盘中触发立即挂限价单(14:57前可撤改挂, 后吃收盘价)
        if signal_type in _STOP_LOSS_SIGNALS:
            if current_time < _CLOSING_AUCTION_START:
                return SellOrderPlan(
                    action=SellOrderAction.LIMIT_ORDER_NOW,
                    order_type="LIMIT",
                    window_note="盘中立即, 14:57前可撤改挂",
                    reason=f"止损信号 {signal_type.value}, 认错要快, 盘中立即执行",
                )
            return SellOrderPlan(
                action=SellOrderAction.CLOSING_AUCTION_LIMIT,
                order_type="LIMIT",
                window_note="14:57后不可撤单, 吃唯一收盘价",
                reason=f"止损信号 {signal_type.value} 14:57后触发, 挂收盘竞价单",
            )

        # 止盈/换仓/退潮减仓: 尾盘集中执行(与41号建仓同窗口方向相反)
        if signal_type in _TAIL_BATCH_SIGNALS:
            return SellOrderPlan(
                action=SellOrderAction.TAIL_BATCH_14_50,
                order_type="LIMIT",
                window_note=f"{_TAIL_BATCH_WINDOW} 尾盘集中挂限价单",
                reason=(f"信号 {signal_type.value} 非紧急, 尾盘U型高流动性段成交更优, 与41号建仓窗口错峰(方向相反)"),
            )

        return SellOrderPlan(
            action=SellOrderAction.HOLD,
            order_type="NONE",
            window_note="—",
            reason="无卖出信号, 继续持有",
        )

    @staticmethod
    def rank_limit_down_orders(
        positions_in_limit_down: list[LimitDownPosition],
    ) -> list[LimitDownPosition]:
        """跌停排队优先级(42号 §3.8): 亏损越大→风控优先级越高→越先排队。

        排序键(三级):
        1. 紧迫度降序(Kill Switch强制清仓 > 风控减仓 > 止损 > 止盈)
        2. 亏损升序(亏损最大的先排)
        3. 仓位金额降序(大仓先排, 减少暴露)

        挂单价格建议(§3.8表格): P0 Kill Switch/P1 回撤L3L4/P2 ATR止损→跌停价;
        P3 止盈换仓→次日开盘价-0.5%。

        Args:
            positions_in_limit_down: 跌停持仓列表

        Returns:
            排序后列表(队首=最优先挂单)
        """
        return sorted(
            positions_in_limit_down,
            key=lambda p: (
                -p.urgency_score,
                p.unrealized_pnl_pct,
                -p.position_value,
            ),
        )

    @staticmethod
    def rank_kill_switch_liquidation(
        positions: list[LiquidationPosition],
    ) -> list[LiquidationPosition]:
        """Kill Switch 强制清仓排序(42号 §3.9): 流动性差的先卖(防封死跌停)。

        排序键(三级):
        1. 流动性升序(流动性差→成交量小→先卖, 防封跌停无法成交)
        2. 仓位金额降序(大仓先卖, 快速降低暴露)
        3. 亏损升序(亏损最大的先卖)

        为何流动性优先而非亏损优先: Kill Switch首要目标是"全部成交"而非"卖好价"。
        流动性差标的后卖可能被封死跌停→暴露无法消除(§3.9)。

        Args:
            positions: 待清仓持仓列表

        Returns:
            排序后列表(队首=最先清仓)
        """
        return sorted(
            positions,
            key=lambda p: (
                p.liquidity_score,
                -p.position_value,
                p.unrealized_pnl_pct,
            ),
        )
