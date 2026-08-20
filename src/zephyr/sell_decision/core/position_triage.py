# [BLUEPRINT] MOD-SELL-000 | docs/03_modules/_domain_sell_decision/position_triage/blueprint.md
# [MODULE] zephyr.sell_decision.core.position_triage
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.position.core.position_drift_monitor
# [CONSUMERS] D-POSITION(持仓漂移监控) ; MOD-SELL-007(融合引擎) ; MOD-SELL-009(紧迫度评分)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 距止损<1.5×ATR→WATCH; 深度盈利>3×ATR且远离止损→HOLD; 中间→MONITOR; ATR缺失降级MONITOR; |threshold_delta|≤0.10
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTriageInputError
# [TESTS] tests/sell_decision/test_position_triage.py
# [A_module] module_id=MOD-SELL-000 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Position Triage — 持仓分级判定器 (MOD-SELL-000)

按持仓盈亏状态与止损距离输出 TriageLevel(WATCH/MONITOR/HOLD)，
驱动不同扫描频率与卖出决策权重。

设计说明:
    - 消费方: position_drift_monitor 已定义 TriageLevel 枚举(注释"来自 SELL-00"),
      本模块作为生产方输出分级结果, import 复用其枚举(真源唯一, 避免双向同步)
    - ATR 缺失时降级默认 MONITOR(spec §3.2"正常持仓"中间档——WATCH过度监控/
      HOLD漏监控, MONITOR最保守)
    - 无状态设计: 不持久化, 每次扫描重新判定
    - 与 §3.3 双向反馈契约联动: threshold_delta 正值放宽/负值收紧, 硬封顶±0.10

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/42_sell_flow.md §3.2
SSoT: depgraph MOD-SELL-000
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 持仓快照 SellPositionSnapshot
#   fields: entry_price(入场价)+current_price(现价)+strategy_type(策略类型,影响降级参数)
#   code: SellPositionSnapshot dataclass
# - id: I2
#   name: ATR值 atr_value float
#   fields: ATR(14)数值, 可None(触发降级)
#   code: triage() 参数
# - id: I3
#   name: 止损价位 stop_loss_price float
#   fields: 当前止损锚定价(来自MOD-SELL-005 Chandelier)
#   code: triage() 参数
# - id: I4
#   name: 阈值动态调整量 threshold_delta float
#   fields: 来自BM-POS-09双向反馈, 默认0.0, 范围[-0.10,+0.10]
#   code: triage() 参数
# 层: 算法
# - id: A1
#   name_zh: ① 输入合法性校验
#   name_en: _validate
#   intro: 检查价格和ATR参数合法性, 不合法直接抛错
#   desc: entry_price>0 / current_price>0 / stop_loss_price>0; ATR None或<=0时降级固定%
#   inputs: I1 I2 I3
#   outputs: 合法输入或异常
# - id: A2
#   name_zh: ② ATR自适应分级判定
#   name_en: _triage_atr
#   intro: 用ATR距离驱动三级判定, 高波动股自动给更多缓冲
#   desc: 绝对价格距离比较(与spec伪代码数学等价,消除法防浮点尾差); distance_abs<1.5×ATR-delta_abs→WATCH / profit_abs>3.0×ATR-delta_abs→HOLD / 中间→MONITOR; delta正放宽负收紧
#   inputs: I1 I2 I3 I4
#   outputs: TriageLevel
#   invariant: 距止损<1.5×ATR→WATCH; 深度盈利>3×ATR→HOLD
# - id: A3
#   name_zh: ③ ATR缺失降级
#   name_en: 降级默认MONITOR
#   intro: ATR缺失无法判定接近程度, 降级到"正常持仓"中间档, 不过度监控不漏监控
#   desc: atr None或<=0 → 直接返回MONITOR(§3.2"正常持仓"档), 记debug日志
#   inputs: I2
#   outputs: TriageLevel.MONITOR
#   invariant: ATR缺失时仍有分级输出(最保守中间档)
# 层: 输出
# - id: O1
#   name_zh: 持仓分级 TriageLevel
#   name_en: TriageLevel
#   intro: WATCH(分钟级)/MONITOR(5分钟级)/HOLD(事件驱动), 决定扫描频率
#   downstream: D-POSITION(漂移监控) ; MOD-SELL-007(融合) ; MOD-SELL-009(紧迫度)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I1 --> A2
# I2 --> A2
# I3 --> A2
# I4 --> A2
# I2 --> A3
# A2 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.position.core.position_drift_monitor import TriageLevel
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "SellPositionSnapshot",
    "StrategyType",
    "PositionTriage",
    "InvalidTriageInputError",
]

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────────

_WATCH_ATR_MULTIPLIER: Final[float] = 1.5
_HOLD_ATR_MULTIPLIER: Final[float] = 3.0
_MAX_THRESHOLD_DELTA: Final[float] = 0.10


# ──────────────────────────────────────────────────────────────────────────────
# 枚举 / 数据模型
# ──────────────────────────────────────────────────────────────────────────────


class StrategyType(str, Enum):
    """策略类型——影响止损降级参数与M值调整(42号 §3.3)。

    MVP 对齐 spec 五类范式(§2.3)的最小集: 短线/趋势/均值回归/其他。
    完整五类(趋势/均值回归/高频/Carry/套利)归 MOD-SELL-014(待G04校准)。
    """

    SHORT_TERM = "short_term"  # 短线/高频(降级4%, M不调整)
    TREND = "trend"  # 趋势(M+0.5, 宽止损防被震出)
    MEAN_REVERSION = "mean_reversion"  # 均值回归(M-0.5, 紧止损)
    OTHER = "other"  # 其他/默认(降级8%, M不调整)


@dataclass(frozen=True)
class SellPositionSnapshot:
    """持仓快照——分级判定所需最小字段集。"""

    symbol: str
    entry_price: float
    current_price: float
    strategy_type: StrategyType = StrategyType.OTHER


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidTriageInputError(ZephyrBaseError):
    """持仓分级输入数据非法(如价格≤0、符号空)。"""

    error_code = "ZA-SELL-0000"


# ──────────────────────────────────────────────────────────────────────────────
# 算法
# ──────────────────────────────────────────────────────────────────────────────


def _validate(
    position: SellPositionSnapshot,
    stop_loss_price: float,
) -> None:
    """输入合法性校验。"""
    if not position.symbol:
        raise InvalidTriageInputError("symbol 不能为空")
    if position.entry_price <= 0:
        raise InvalidTriageInputError("entry_price 必须 > 0")
    if position.current_price <= 0:
        raise InvalidTriageInputError("current_price 必须 > 0")
    if stop_loss_price <= 0:
        raise InvalidTriageInputError("stop_loss_price 必须 > 0")


def _triage_atr(
    position: SellPositionSnapshot,
    atr_value: float,
    stop_loss_price: float,
    threshold_delta: float,
) -> TriageLevel:
    """ATR 自适应分级判定(绝对价格距离比较, 与spec伪代码数学等价)。

    spec: distance_to_stop(%) < 1.5×ATR(%) 两边同乘 entry 消去除法,
          避免浮点计算顺序尾差(42号 §3.2 伪代码同序)。
    """
    entry = position.entry_price
    current = position.current_price

    # 绝对价格量纲
    profit_abs = current - entry  # 有利移动(可负)
    distance_abs = abs(current - stop_loss_price)  # 距止损绝对距离

    # 应用 threshold_delta(双向反馈契约, §3.3 BM-POS-09)
    # delta 正值=放宽(更难WATCH+更易HOLD, 给利润奔跑), 负值=收紧(更敏感)
    # delta 是相对entry的比例, 转绝对价格移动量后从阈值扣除
    delta_abs = threshold_delta * entry
    watch_abs = _WATCH_ATR_MULTIPLIER * atr_value - delta_abs
    hold_abs = _HOLD_ATR_MULTIPLIER * atr_value - delta_abs

    # 距止损近 → WATCH(亏损区或盈利回撤接近止损)
    if distance_abs < watch_abs:
        return TriageLevel.WATCH

    # 深度盈利且远离止损 → HOLD
    if profit_abs > hold_abs:
        return TriageLevel.HOLD

    return TriageLevel.MONITOR


class PositionTriage:
    """持仓分级判定器——产出 TriageLevel 驱动扫描频率。"""

    @staticmethod
    def triage(
        position: SellPositionSnapshot,
        atr_value: float | None,
        stop_loss_price: float,
        *,
        threshold_delta: float = 0.0,
    ) -> TriageLevel:
        """判定持仓分级。

        Args:
            position: 持仓快照
            atr_value: ATR(14) 数值, None 时降级固定%
            stop_loss_price: 当前止损锚定价(来自 Chandelier)
            threshold_delta: BM-POS-09 双向反馈调整量, 默认 0.0, 硬封顶 ±0.10

        Returns:
            TriageLevel.WATCH / MONITOR / HOLD

        Raises:
            InvalidTriageInputError: 输入非法
        """
        _validate(position, stop_loss_price)

        # 硬封顶 threshold_delta(契约 §3.3: |delta| ≤ 0.10)
        delta = max(-_MAX_THRESHOLD_DELTA, min(_MAX_THRESHOLD_DELTA, threshold_delta))

        if atr_value is None or atr_value <= 0:
            # ATR缺失降级: 无法判定接近程度, 默认MONITOR正常监控档
            # (WATCH过度监控/HOLD漏监控, MONITOR是spec §3.2"正常持仓"中间档)
            logger.debug("ATR缺失, symbol=%s 降级默认MONITOR", position.symbol)
            return TriageLevel.MONITOR

        return _triage_atr(position, atr_value, stop_loss_price, delta)
