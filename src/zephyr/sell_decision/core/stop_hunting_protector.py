# [BLUEPRINT] MOD-SELL-015 | docs/03_modules/_domain_sell_decision/stop_hunting_protector/blueprint.md
# [MODULE] zephyr.sell_decision.core.stop_hunting_protector
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors ; zephyr.sell_decision.core.sell_signal_collector
# [CONSUMERS] MOD-SELL-005(止损策略族消费AdjustedStopLevel) ; MOD-SELL-007(融合引擎)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 止损位偏移1-2%防猎杀; 软止损=触及→OBSERVING→确认跌破→CONFIRMED; 观察期收回→CLEARED; confidence∈[0,1]
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidStopHuntInputError
# [TESTS] tests/sell_decision/test_stop_hunting_protector.py
# [A_module] module_id=MOD-SELL-015 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Stop-Hunting Protector — 止损猎杀防护器 (MOD-SELL-015)

防护做市商/HFT 主动猎杀止损位:
    ① 止损位偏移: 不精确设在技术位, 偏移 1-2% 防猎杀
    ② 软止损模式: 到达止损位→不立即执行→进入 OBSERVING 观察期
       → 观察期确认跌破(收盘价<止损位)→执行
       → 观察期收回(价格回升)→解除(CLEARED)

设计说明:
    - A类基础设施: 纯防护逻辑, 不涉及"止损位怎么算"(SELL-05 职责)
    - 输入契约: 原始止损位 + 当前价/收盘价 + 软止损状态(由调用方维护)
    - 无状态设计: 软止损状态作为输入参数, 检测器不持久化(可并发)
    - 偏移方向: 默认 BELOW(止损位下移, 防向上猎杀), 可配置 ABOVE
    - 输出 AdjustedStopLevel 喂给 SELL-05 止损策略族 + SELL-07 融合引擎

依据: D:\临时工作区\依赖图-D-SELL-DECISION-卖出决策域.md §1.2 SELL-15
SSoT: depgraph MOD-SELL-015
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 原始止损位 技术位
#   fields: symbol + original_stop(>0) + offset_pct(可选,默认2%) + direction(BELOW/ABOVE)
#   code: adjust_stop_level 参数
# - id: I2
#   name: 行情价格 盘中价与收盘价
#   fields: current_price(盘中,>0) + close_price(确认跌破用,>0)
#   code: evaluate_soft_stop 参数
# - id: I3
#   name: 软止损状态 调用方维护
#   fields: current_state(NORMAL/OBSERVING/CONFIRMED/CLEARED) 无状态设计不持久化
#   code: evaluate_soft_stop 参数 current_state
# 层: 算法
# - id: A1
#   name_zh: ① 止损位偏移防猎杀
#   name_en: StopHuntingProtector.adjust_stop_level
#   intro: 止损位不精确挂在技术位上，故意偏移1-2%让猎杀单扫不到
#   desc: 入参校验后 BELOW: adjusted=original×(1-pct); ABOVE: adjusted=original×(1+pct); 默认pct=0.02∈(0,0.1]
#   inputs: I1
#   outputs: AdjustedStopLevel(state=NORMAL, confirmed=False)
#   invariant: 止损位偏移1-2%防猎杀
# - id: A2
#   name_zh: ② 软止损状态机转移
#   name_en: _transition
#   intro: 触及止损不立刻卖，先进观察期，收盘价确认跌破才执行，价格回升就解除
#   desc: NORMAL/CLEARED+现价≤止损位→OBSERVING; OBSERVING+收盘价<止损位→CONFIRMED; OBSERVING+现价>止损位→CLEARED; CONFIRMED为终态由调用方重置
#   inputs: I2 I3
#   outputs: 新软止损状态 SoftStopState
#   invariant: 软止损=触及→OBSERVING→确认跌破→CONFIRMED; 观察期收回→CLEARED
# - id: A3
#   name_zh: ③ 状态到置信度与卖出方向映射
#   name_en: evaluate_soft_stop
#   intro: 把状态机结果翻译成置信度和卖出方向，CONFIRMED清仓、OBSERVING减仓、其余占位不卖
#   desc: CONFIRMED→conf=1.0/CLEAR; OBSERVING→conf=0.5/REDUCE; CLEARED/NORMAL→conf=0.0/REPLACE占位; 软止损评估不重复偏移(offset_pct=0)
#   inputs: A2
#   outputs: AdjustedStopLevel(含新状态+置信度+方向) 并_notify回调通知
#   invariant: confidence∈[0,1]
# 层: 输出
# - id: O1
#   name_zh: 止损猎杀防护结果 AdjustedStopLevel
#   name_en: AdjustedStopLevel
#   intro: 含偏移后止损位/软止损状态/是否确认跌破/置信度/卖出方向，并通过on_adjusted回调广播
#   invariant: offset_pct∈[0,1]; confidence∈[0,1]; adjusted_stop>0
#   downstream: MOD-SELL-005(止损策略族消费AdjustedStopLevel) ; MOD-SELL-007(融合引擎)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I3 --> A2
# A2 --> A3
# A1 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Final

from zephyr.sell_decision.core.sell_signal_collector import SellDirection
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "StopHuntOffsetDirection",
    "SoftStopState",
    "AdjustedStopLevel",
    "StopHuntingProtector",
    "InvalidStopHuntInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class StopHuntOffsetDirection(str, Enum):
    """止损位偏移方向。"""

    BELOW = "BELOW"  # 偏移到技术位下方(止损位下移, 防向上猎杀)
    ABOVE = "ABOVE"  # 偏移到技术位上方(止损位上移)


class SoftStopState(str, Enum):
    """软止损状态机。"""

    NORMAL = "NORMAL"  # 正常(价格 > 止损位)
    OBSERVING = "OBSERVING"  # 观察期(价格触及止损位, 等待确认)
    CONFIRMED = "CONFIRMED"  # 确认跌破(收盘价 < 止损位, 执行卖出)
    CLEARED = "CLEARED"  # 解除(观察期收回, 价格回升)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidStopHuntInputError(ZephyrBaseError):
    """止损猎杀防护输入数据非法(如止损位≤0、偏移比例越界)。"""

    error_code = "ZA-SELL-0015"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AdjustedStopLevel:
    """止损猎杀防护结果 (SELL-15 产出, SELL-05/SELL-07 消费)。

    Attributes:
        symbol: 标的代码
        original_stop: 原始止损位(技术位)
        adjusted_stop: 偏移后止损位
        offset_pct: 偏移比例[0,1]
        offset_direction: 偏移方向(BELOW/ABOVE)
        soft_stop_state: 软止损状态(NORMAL/OBSERVING/CONFIRMED/CLEARED)
        confirmed: 是否确认跌破(执行卖出)
        confidence: 置信度[0,1](CONFIRMED=1.0)
        direction: 卖出方向(CONFIRMED→CLEAR, OBSERVING→REDUCE, 其他→REPLACE占位)
        reason: 人类可读原因
        metadata: 附加数据
        timestamp: 检测时间
    """

    symbol: str
    original_stop: float
    adjusted_stop: float
    offset_pct: float
    offset_direction: StopHuntOffsetDirection
    soft_stop_state: SoftStopState
    confirmed: bool
    confidence: float
    direction: SellDirection
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.symbol:
            raise InvalidStopHuntInputError("symbol must not be empty")
        if self.original_stop <= 0:
            raise InvalidStopHuntInputError(f"original_stop must be > 0, got {self.original_stop}")
        if self.adjusted_stop <= 0:
            raise InvalidStopHuntInputError(f"adjusted_stop must be > 0, got {self.adjusted_stop}")
        if not 0.0 <= self.offset_pct <= 1.0:
            raise InvalidStopHuntInputError(f"offset_pct must be in [0,1], got {self.offset_pct}")
        if not 0.0 <= self.confidence <= 1.0:
            raise InvalidStopHuntInputError(f"confidence must be in [0,1], got {self.confidence}")


# ──────────────────────────────────────────────────────────────────────────────
# 防护器
# ──────────────────────────────────────────────────────────────────────────────


# 默认偏移比例: 2% (设计文档 §1.2 SELL-15, 偏移1-2%)
_DEFAULT_OFFSET_PCT: Final = 0.02

# 软止损置信度
_NORMAL_CONFIDENCE: Final = 0.0
_OBSERVING_CONFIDENCE: Final = 0.5
_CONFIRMED_CONFIDENCE: Final = 1.0
_CLEARED_CONFIDENCE: Final = 0.0


class StopHuntingProtector:
    """止损猎杀防护器——止损位偏移 + 软止损观察期。

    用法:
        protector = StopHuntingProtector()
        # ① 止损位偏移
        adjusted = protector.adjust_stop_level("000001.SZ", 10.00)
        # adjusted.adjusted_stop == 9.80 (下移2%)
        # ② 软止损评估
        result = protector.evaluate_soft_stop("000001.SZ", 9.80, 9.70, 9.75, SoftStopState.NORMAL)

    不变量:
        - 偏移方向 BELOW: adjusted = original × (1 - offset_pct)
        - 偏移方向 ABOVE: adjusted = original × (1 + offset_pct)
        - 软止损状态转移:
            NORMAL + 价格≤止损位 → OBSERVING
            OBSERVING + 收盘价<止损位 → CONFIRMED(执行)
            OBSERVING + 价格>止损位 → CLEARED(解除)
            CONFIRMED/CLEARED 保持(由调用方重置)
    """

    def __init__(
        self,
        default_offset_pct: float = _DEFAULT_OFFSET_PCT,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not 0.0 < default_offset_pct <= 0.1:
            raise InvalidStopHuntInputError(f"default_offset_pct must be in (0, 0.1], got {default_offset_pct}")
        self._default_offset_pct = default_offset_pct
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._adjusted_callbacks: list[Callable[[AdjustedStopLevel], None]] = []

    # ── 止损位偏移 ──

    def adjust_stop_level(
        self,
        symbol: str,
        original_stop: float,
        offset_pct: float | None = None,
        direction: StopHuntOffsetDirection = StopHuntOffsetDirection.BELOW,
        now: datetime | None = None,
    ) -> AdjustedStopLevel:
        """止损位偏移: 不精确设在技术位, 偏移防猎杀。

        Args:
            symbol: 标的代码
            original_stop: 原始止损位(技术位, >0)
            offset_pct: 偏移比例[0,1], 默认用构造器默认值
            direction: 偏移方向(BELOW下移/ABOVE上移)
            now: 时间

        Returns:
            AdjustedStopLevel(soft_stop_state=NORMAL, confirmed=False)
        """
        if not symbol:
            raise InvalidStopHuntInputError("symbol must not be empty")
        if original_stop <= 0:
            raise InvalidStopHuntInputError(f"original_stop must be > 0, got {original_stop}")
        pct = offset_pct if offset_pct is not None else self._default_offset_pct
        if not 0.0 <= pct <= 1.0:
            raise InvalidStopHuntInputError(f"offset_pct must be in [0,1], got {pct}")

        now = now or self._clock()
        if direction is StopHuntOffsetDirection.BELOW:
            adjusted = original_stop * (1.0 - pct)
        else:
            adjusted = original_stop * (1.0 + pct)

        result = AdjustedStopLevel(
            symbol=symbol,
            original_stop=original_stop,
            adjusted_stop=adjusted,
            offset_pct=pct,
            offset_direction=direction,
            soft_stop_state=SoftStopState.NORMAL,
            confirmed=False,
            confidence=_NORMAL_CONFIDENCE,
            direction=SellDirection.REPLACE,  # 占位: 仅调整止损位, 不卖出
            reason=f"止损位 {original_stop} 偏移 {pct:.1%}({direction.value}) → {adjusted:.4f}",
            metadata={"adjusted": True},
            timestamp=now,
        )
        self._notify(result)
        return result

    # ── 软止损评估 ──

    def evaluate_soft_stop(
        self,
        symbol: str,
        stop_level: float,
        current_price: float,
        close_price: float,
        current_state: SoftStopState = SoftStopState.NORMAL,
        now: datetime | None = None,
    ) -> AdjustedStopLevel:
        """软止损状态机评估: 触及止损位→OBSERVING→确认跌破→CONFIRMED。

        Args:
            symbol: 标的代码
            stop_level: 止损位(已偏移, >0)
            current_price: 当前价格(盘中, >0)
            close_price: 收盘价(用于确认跌破, >0)
            current_state: 当前软止损状态(由调用方维护)
            now: 时间

        Returns:
            AdjustedStopLevel(含新状态)

        状态转移:
            NORMAL + current_price <= stop_level → OBSERVING
            OBSERVING + close_price < stop_level → CONFIRMED(执行)
            OBSERVING + current_price > stop_level → CLEARED(解除)
            CONFIRMED → CONFIRMED(保持, 由调用方重置)
            CLEARED + current_price <= stop_level → OBSERVING(重新触发)
        """
        if not symbol:
            raise InvalidStopHuntInputError("symbol must not be empty")
        if stop_level <= 0:
            raise InvalidStopHuntInputError(f"stop_level must be > 0, got {stop_level}")
        if current_price <= 0:
            raise InvalidStopHuntInputError(f"current_price must be > 0, got {current_price}")
        if close_price <= 0:
            raise InvalidStopHuntInputError(f"close_price must be > 0, got {close_price}")

        now = now or self._clock()
        new_state = self._transition(current_state, stop_level, current_price, close_price)

        if new_state is SoftStopState.CONFIRMED:
            confidence = _CONFIRMED_CONFIDENCE
            confirmed = True
            direction = SellDirection.CLEAR
            reason = f"收盘价 {close_price} < 止损位 {stop_level}, 确认跌破, 执行清仓"
        elif new_state is SoftStopState.OBSERVING:
            confidence = _OBSERVING_CONFIDENCE
            confirmed = False
            direction = SellDirection.REDUCE
            reason = f"价格 {current_price} 触及止损位 {stop_level}, 进入观察期"
        elif new_state is SoftStopState.CLEARED:
            confidence = _CLEARED_CONFIDENCE
            confirmed = False
            direction = SellDirection.REPLACE  # 占位: 解除, 不卖出
            reason = f"观察期价格回升 {current_price} > 止损位 {stop_level}, 解除"
        else:  # NORMAL
            confidence = _NORMAL_CONFIDENCE
            confirmed = False
            direction = SellDirection.REPLACE  # 占位: 正常, 不卖出
            reason = f"价格 {current_price} > 止损位 {stop_level}, 正常持有"

        result = AdjustedStopLevel(
            symbol=symbol,
            original_stop=stop_level,
            adjusted_stop=stop_level,  # 软止损评估不偏移(偏移由 adjust_stop_level 负责)
            offset_pct=0.0,
            offset_direction=StopHuntOffsetDirection.BELOW,
            soft_stop_state=new_state,
            confirmed=confirmed,
            confidence=confidence,
            direction=direction,
            reason=reason,
            metadata={"prev_state": current_state.value, "new_state": new_state.value},
            timestamp=now,
        )
        self._notify(result)
        return result

    @staticmethod
    def _transition(
        state: SoftStopState,
        stop_level: float,
        current_price: float,
        close_price: float,
    ) -> SoftStopState:
        """软止损状态转移逻辑。"""
        if state is SoftStopState.CONFIRMED:
            # CONFIRMED 是终态(由调用方重置为 NORMAL/CLEARED)
            return SoftStopState.CONFIRMED

        if state is SoftStopState.OBSERVING:
            # 观察期: 确认跌破(收盘价<止损位) → CONFIRMED
            if close_price < stop_level:
                return SoftStopState.CONFIRMED
            # 观察期: 价格回升 → CLEARED
            if current_price > stop_level:
                return SoftStopState.CLEARED
            # 观察期: 维持
            return SoftStopState.OBSERVING

        # NORMAL 或 CLEARED
        # 触及止损位(价格≤止损位) → OBSERVING
        if current_price <= stop_level:
            return SoftStopState.OBSERVING
        return SoftStopState.NORMAL

    # ── 事件回调 ──

    def on_adjusted(self, callback: Callable[[AdjustedStopLevel], None]) -> None:
        """注册防护结果生成回调。"""
        self._adjusted_callbacks.append(callback)

    def _notify(self, result: AdjustedStopLevel) -> None:
        for cb in self._adjusted_callbacks:
            try:
                cb(result)
            except Exception as exc:  # noqa: BLE001 — 隔离回调故障
                logger.error("Stop hunt callback failed: %s", exc, exc_info=True)
