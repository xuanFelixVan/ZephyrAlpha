# [BLUEPRINT] MOD-SELL-005 | docs/03_modules/_domain_sell_decision/stop_loss_strategy/blueprint.md
# [MODULE] zephyr.sell_decision.core.stop_loss_strategy
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.sell_decision.core.position_triage
# [CONSUMERS] MOD-SELL-015(猎杀防护偏移) ; MOD-SELL-007(融合引擎) ; D-POSITION(止损锚定)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 亏损区宽M=3.0/盈利区紧M=2.0; ATR缺失降级固定%; 策略类型调整M值(趋势+0.5/均值回归-0.5); 时间止损5天1×ATR
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SellStopLossInputError
# [TESTS] tests/sell_decision/test_stop_loss_strategy.py
# [A_module] module_id=MOD-SELL-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Stop Loss Strategy — 止损策略族 (MOD-SELL-005)

Chandelier Exit 统一止损: ATR自适应波动率止损 + 移动止损一体化,
替代两套独立%参数。配套时间止损算法(第⑦类信号源)。

设计说明:
    - Chandelier Exit: 止损线 = Highest_Close(N) - M × ATR(14)
      亏损区(N=10, M=3.0, 宽trailing防噪声扫出)
      盈利区(N=22, M=2.0, 紧trailing锁定利润)
    - 策略类型差异化(MVP简化版, 替代MOD-SELL-014完整范式):
      趋势策略 M+0.5 / 均值回归 M-0.5 / 其他 M+0.0
    - ATR缺失降级: 固定%止损(短线4%/中长线8%, eastmoney 2026-07)
    - 时间止损(check_time_stop): 5天未移动1×ATR→FORCE_EXIT_EVALUATION,
      喂给MOD-SELL-001收集器第⑦类TIME_STOP信号
    - 与risk域default_stop_loss_engine并存: 本模块管策略级退出价位,
      risk域管账户级硬止损(分层防御, 见42号§7待定问题)

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/42_sell_flow.md §3.3/§3.2
SSoT: depgraph MOD-SELL-005
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 持仓快照 SellPositionSnapshot
#   fields: entry_price+current_price+strategy_type(见MOD-SELL-000)
#   code: compute_stop_loss() / check_time_stop() 参数
# - id: I2
#   name: ATR值 atr_value float
#   fields: ATR(14)数值, None触发降级
#   code: compute_stop_loss() 参数
# - id: I3
#   name: 最高收盘价回调 highest_close_fn Callable
#   fields: 传入回看N日→返回最高收盘价, 由调用方注入K线数据
#   code: compute_stop_loss() 参数
# - id: I4
#   name: 持仓阶段 phase str
#   fields: "loss"(亏损区,宽M) / "profit"(盈利区,紧M), 调用方显式传入
#   code: compute_stop_loss() 参数
# - id: I5
#   name: 持仓天数 holding_days int
#   fields: 已持仓交易日数, 用于时间止损
#   code: check_time_stop() 参数
# 层: 算法
# - id: A1
#   name_zh: ① 输入合法性校验
#   name_en: validate_position_snapshot
#   intro: 检查价格合法性和回调函数可调用性, 不合法直接抛错
#   desc: symbol非空/entry_price>0/current_price>0/highest_close_fn可调用/phase∈{loss,profit}
#   inputs: I1 I3 I4
#   outputs: 合法输入或异常
# - id: A2
#   name_zh: ② 策略类型M值调整
#   name_en: _adjust_m
#   intro: 按策略类型微调Chandelier M值, 趋势宽/均值回归紧
#   desc: trend→M+0.5 / mean_reversion→M-0.5 / 其他→M不变; MVP简化替代MOD-SELL-014
#   inputs: I1
#   outputs: 调整后M值
# - id: A3
#   name_zh: ③ Chandelier止损计算
#   name_en: compute_stop_loss
#   intro: 一套公式两个参数, 按持仓阶段切换M/N, ATR缺失降级固定%
#   desc: ATR缺失→entry×(1-fallback_pct); 否则highest_close_fn(N)-M×ATR; 亏损区N=10/M=3.0/盈利区N=22/M=2.0
#   inputs: I1 I2 I3 I4 A2
#   outputs: 止损价位 stop_price
#   invariant: 亏损区宽M=3.0/盈利区紧M=2.0; ATR缺失降级固定%
# - id: A4
#   name_zh: ④ ATR自适应时间止损
#   name_en: check_time_stop
#   intro: 5天未移动1×ATR有利方向→触发退出评估, ATR缺失用固定%
#   desc: favorable_move=current-entry; atr_threshold=1×ATR; 5天未达→FORCE_EXIT_EVALUATION; ATR缺失→1%固定阈值
#   inputs: I1 I2 I5
#   outputs: TimeStopSignal或None
#   invariant: 时间止损阈值1×ATR自适应波动率
# 层: 输出
# - id: O1
#   name_zh: 止损价位 stop_price float
#   name_en: stop_price
#   intro: Chandelier Exit止损锚定价, 喂给MOD-SELL-015猎杀防护偏移
#   downstream: MOD-SELL-015(猎杀防护) ; MOD-SELL-007(融合) ; D-POSITION
# - id: O2
#   name_zh: 时间止损信号 TimeStopSignal
#   name_en: TimeStopSignal
#   intro: FORCE_EXIT_EVALUATION枚举, 喂给收集器第⑦类TIME_STOP
#   downstream: MOD-SELL-001(收集器第⑦类)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I4 --> A1
# I1 --> A2
# I1 --> A3
# I2 --> A3
# I3 --> A3
# I4 --> A3
# A2 --> A3
# I1 --> A4
# I2 --> A4
# I5 --> A4
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

from zephyr.sell_decision.core.position_triage import SellPositionSnapshot, StrategyType
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "PositionPhase",
    "TimeStopSignal",
    "StopLossStrategy",
    "SellStopLossInputError",
    "validate_position_snapshot",
]

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────────

# Chandelier 参数(42号 §3.3 MVP 值)
_LOSS_N: Final[int] = 10
_LOSS_M: Final[float] = 3.0
_PROFIT_N: Final[int] = 22
_PROFIT_M: Final[float] = 2.0

# 策略类型 M 调整(42号 §2.3/§4.1 MVP简化版)
_TREND_M_ADJUST: Final[float] = 0.5
_MEAN_REVERSION_M_ADJUST: Final[float] = -0.5

# ATR缺失降级(42号 §3.3, eastmoney 2026-07)
_FALLBACK_PCT_SHORT: Final[float] = 0.04
_FALLBACK_PCT_LONG: Final[float] = 0.08

# 时间止损(42号 §3.2, journalplus 2026)
_TIME_STOP_DAYS: Final[int] = 5
_TIME_STOP_ATR_MULT: Final[float] = 1.0
_TIME_STOP_FALLBACK_PCT: Final[float] = 0.01


# ──────────────────────────────────────────────────────────────────────────────
# 枚举 / 数据模型
# ──────────────────────────────────────────────────────────────────────────────


class PositionPhase(str, Enum):
    """持仓阶段——决定 Chandelier 参数。"""

    LOSS = "loss"
    PROFIT = "profit"


class TimeStopSignal(str, Enum):
    """时间止损信号——喂给收集器第⑦类。"""

    FORCE_EXIT_EVALUATION = "FORCE_EXIT_EVALUATION"


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class SellStopLossInputError(ZephyrBaseError):
    """止损策略输入数据非法(如价格≤0、phase非法、回调不可调用)。"""

    error_code = "ZA-SELL-0005"


# ──────────────────────────────────────────────────────────────────────────────
# 算法
# ──────────────────────────────────────────────────────────────────────────────


def validate_position_snapshot(position: SellPositionSnapshot) -> None:
    """持仓输入合法性校验(MOD-SELL-004/005 共用)。"""
    if not position.symbol:
        raise SellStopLossInputError("symbol 不能为空")
    if position.entry_price <= 0:
        raise SellStopLossInputError("entry_price 必须 > 0")
    if position.current_price <= 0:
        raise SellStopLossInputError("current_price 必须 > 0")


def _adjust_m(strategy_type: StrategyType, base_m: float) -> float:
    """策略类型 M 值调整(MVP简化版, 42号 §3.3注释/§4.1)。

    趋势+0.5(宽止损防被震出) / 均值回归-0.5(紧止损) / 其他不调整。
    完整五类范式(趋势/均值回归/高频/Carry/套利)归 MOD-SELL-014(待G04校准)。
    """
    if strategy_type == StrategyType.TREND:
        return base_m + _TREND_M_ADJUST
    if strategy_type == StrategyType.MEAN_REVERSION:
        return base_m + _MEAN_REVERSION_M_ADJUST
    return base_m


class StopLossStrategy:
    """止损策略族——Chandelier Exit 统一止损 + 时间止损。"""

    @staticmethod
    def compute_stop_loss(
        position: SellPositionSnapshot,
        atr_value: float | None,
        highest_close_fn: Callable[[int], float],
        phase: PositionPhase,
    ) -> float:
        """Chandelier Exit 止损计算。

        公式: 止损线 = Highest_Close(N) - M × ATR(14)
        - 亏损区(loss): N=10, M=3.0, 宽trailing防噪声扫出
        - 盈利区(profit): N=22, M=2.0, 紧trailing锁定利润
        - ATR缺失降级: 固定%止损(短线4%/中长线8%)

        Args:
            position: 持仓快照
            atr_value: ATR(14), None时降级固定%
            highest_close_fn: 回调函数, 传入回看N日→返回最高收盘价
            phase: 持仓阶段(loss/profit), 由调用方显式传入
                   (与MOD-SELL-004 compute_exit_price自动判定phase不同,
                    本函数适用于调用方已持有phase上下文的场景)

        Returns:
            止损价位(float)

        Raises:
            SellStopLossInputError: 输入非法
        """
        validate_position_snapshot(position)
        if not callable(highest_close_fn):
            raise SellStopLossInputError("highest_close_fn 必须可调用")
        if not isinstance(phase, PositionPhase):
            raise SellStopLossInputError("phase 必须是 PositionPhase 枚举")

        # ATR缺失降级: 固定%止损(42号 §3.3)
        if atr_value is None or atr_value <= 0:
            fallback_pct = (
                _FALLBACK_PCT_SHORT if position.strategy_type == StrategyType.SHORT_TERM else _FALLBACK_PCT_LONG
            )
            logger.debug(
                "ATR缺失, symbol=%s 降级固定%%止损 %.2f%%",
                position.symbol,
                fallback_pct * 100,
            )
            return position.entry_price * (1 - fallback_pct)

        # 按持仓阶段取参数
        if phase == PositionPhase.LOSS:
            n, base_m = _LOSS_N, _LOSS_M
        else:
            n, base_m = _PROFIT_N, _PROFIT_M

        # 策略类型M值调整
        m = _adjust_m(position.strategy_type, base_m)

        return highest_close_fn(n) - m * atr_value

    @staticmethod
    def check_time_stop(
        position: SellPositionSnapshot,
        atr_value: float | None,
        holding_days: int,
    ) -> TimeStopSignal | None:
        """ATR自适应时间止损——第⑦类信号源(42号 §3.2)。

        规则: N天内未移动1×ATR有利方向→强制退出评估。
        用ATR自适应波动率而非固定N天:
        - 高波动股阈值自动抬高(给更多时间)
        - 低波动股阈值自动降低(更快触发)

        Args:
            position: 持仓快照
            atr_value: ATR(14), None时降级固定1%阈值
            holding_days: 已持仓交易日数

        Returns:
            TimeStopSignal.FORCE_EXIT_EVALUATION 或 None

        Raises:
            SellStopLossInputError: 输入非法
        """
        validate_position_snapshot(position)
        if holding_days < 0:
            raise SellStopLossInputError("holding_days 必须 >= 0")

        favorable_move = position.current_price - position.entry_price

        if atr_value is None or atr_value <= 0:
            # ATR缺失降级: 固定1%阈值
            threshold = position.entry_price * _TIME_STOP_FALLBACK_PCT
        else:
            threshold = atr_value * _TIME_STOP_ATR_MULT

        if favorable_move < threshold and holding_days >= _TIME_STOP_DAYS:
            logger.info(
                "时间止损触发, symbol=%s 持仓%d天 有利移动%.4f < 阈值%.4f",
                position.symbol,
                holding_days,
                favorable_move,
                threshold,
            )
            return TimeStopSignal.FORCE_EXIT_EVALUATION

        return None
