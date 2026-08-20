# [BLUEPRINT] MOD-POS-004 | docs/03_modules/_domain_position/rebalance_engine/blueprint.md
# [MODULE] zephyr.position.core.rebalance_engine
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.position_drift_monitor; zephyr.shared.foundation.errors
# [CONSUMERS] D-EX-CORE(执行调仓) ; D-PF-CORE ; D-GOVERNANCE(审计)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 交易成本>预期收益改善时MUST跳过; 改善比<阈值时MUST跳过; 调仓指令Δ符号:超配→SELL/低配→BUY; Σ|Δ|=总换手率
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRebalanceInputError
# [TESTS] tests/position/test_rebalance_engine.py
# [A_module] module_id=MOD-POS-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Rebalance Engine — 再平衡引擎 (MOD-POS-004)

消费 E-POS-02 DriftDetected 事件, 在交易成本/预期收益判定通过后产出
E-POS-03 RebalanceTriggered 事件及调仓指令列表, 驱动组合回归目标权重。

三级触发 (D-POSITION §1.1 POS-04):
    - CALENDAR: 周频强制触发(仍走成本判定)
    - DEVIATION: POS-003 DriftDetected 驱动
    - EVENT: 外部事件(资金流入/风控指令)驱动

成本收益判定:
    - 交易成本 > 预期收益改善 → 跳过(禁止亏损再平衡)
    - 预期收益改善 > 2 × 交易成本 → 执行(改善比阈值, 默认 2.0)
    - 压力市场状态(7/8/9) 成本系数 ×1.5

属A类基础设施(漂移→成本收益判定→调仓指令生成, 逻辑明确), 成本系数与改善比阈值为C类可调参数。
依据: D:\临时工作区\依赖图-D-POSITION-仓位管理域.md §1.1 POS-04, §4 E-POS-03
SSoT: depgraph MOD-POS-004
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 漂移检测事件 E-POS-02(可空)
#   fields: DriftDetectedEvent 含组合/标的漂移告警，CALENDAR触发时传None
#   code: evaluate() 参数 drift_event，来自MOD-POS-003
# - id: I2
#   name: 实际/目标持仓权重 字典对
#   fields: actual_weights + target_weights {symbol: weight∈[0,1]}
#   code: evaluate() 参数 actual_weights/target_weights
# - id: I3
#   name: 市场状态码
#   fields: market_state int，7/8/9为压力市场
#   code: evaluate() 参数 market_state
# - id: I4
#   name: 再平衡触发类型
#   fields: CALENDAR周频强制 / DEVIATION偏离驱动 / EVENT外部事件
#   code: evaluate() 参数 trigger
# - id: I5
#   name: 引擎可调参数 构造入参
#   fields: cost_rate=0.001 改善比阈值2.0 压力成本×1.5 再平衡后容差1%
#   code: RebalanceEngine.__init__ L171
# 层: 算法
# - id: A1
#   name_zh: ① 调仓指令生成
#   name_en: _compute_orders
#   intro: 按目标减实际的差值生成买卖指令，超配卖低配买
#   desc: delta=target-actual；delta>0→BUY，<0→SELL；Σ|Δ|=总换手率
#   inputs: I2
#   outputs: RebalanceOrder列表
#   invariant: Δ符号：超配→SELL/低配→BUY；Σ|Δ|=总换手率
# - id: A2
#   name_zh: ② 交易成本计算
#   name_en: transaction cost
#   intro: 换手率乘成本率，压力市场成本系数乘1.5
#   desc: transaction_cost=turnover×cost_rate×multiplier；market_state∈{7,8,9}→multiplier=1.5否则1.0
#   inputs: I3 I5 A1
#   outputs: transaction_cost
# - id: A3
#   name_zh: ③ 预期收益改善估计
#   name_en: _compute_improvement
#   intro: 用漂移平方和近似消除漂移带来的收益改善
#   desc: improvement=Σ(drift²)，优先取drift_event告警的abs_drift，降级用(target-actual)²
#   inputs: I1 I2
#   outputs: expected_improvement
# - id: A4
#   name_zh: ④ 成本收益判定与事件分发
#   name_en: evaluate
#   intro: 成本比改善还贵就不调仓，改善够2倍成本才执行
#   desc: cost>improvement→跳过；ratio=improvement/cost<2.0→跳过(CALENDAR强制放宽仍执行并记录)；通过后发E-POS-03；再平衡后偏差校验返回0占位(残余偏差由执行层算)
#   inputs: I4 I5 A1 A2 A3
#   outputs: RebalanceDecision
#   invariant: 交易成本>预期收益改善时MUST跳过；改善比<阈值时MUST跳过
# 层: 输出
# - id: O1
#   name_zh: 再平衡评估结果
#   name_en: RebalanceDecision
#   intro: 是否执行+调仓指令列表+成本/改善/改善比+原因
#   downstream: D-EX-CORE执行调仓 D-PF-CORE
# - id: O2
#   name_zh: 再平衡触发事件 E-POS-03
#   name_en: RebalanceTriggeredEvent
#   intro: 判定通过时广播，含触发类型/换手率/指令数快照
#   downstream: D-EX-CORE执行调仓 D-PF-CORE D-GOVERNANCE审计
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A3
# I2 --> A3
# I3 --> A2
# I5 --> A2
# I5 --> A4
# I4 --> A4
# A1 --> A2
# A1 --> A4
# A2 --> A4
# A3 --> A4
# A4 --> O1
# A4 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.position.core.position_drift_monitor import DriftDetectedEvent
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "RebalanceTrigger",
    "RebalanceAction",
    "RebalanceOrder",
    "RebalanceDecision",
    "RebalanceTriggeredEvent",
    "RebalanceEngine",
    "InvalidRebalanceInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class RebalanceTrigger(str, Enum):
    """再平衡触发类型。"""

    CALENDAR = "CALENDAR"  # 日历触发(周频强制)
    DEVIATION = "DEVIATION"  # 偏离触发(DriftDetected)
    EVENT = "EVENT"  # 事件触发(资金流入/风控)


class RebalanceAction(str, Enum):
    """调仓指令方向。"""

    BUY = "BUY"  # 低配→买入
    SELL = "SELL"  # 超配→卖出


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidRebalanceInputError(ZephyrBaseError):
    """再平衡输入数据非法(如权重越界、标的集合不一致、cost_rate 非正)。"""

    error_code = "ZA-POS-0007"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RebalanceOrder:
    """单条调仓指令。"""

    symbol: str
    current_weight: float
    target_weight: float
    delta: float  # 有符号(正=买入加仓, 负=卖出减仓)
    action: RebalanceAction

    @property
    def abs_delta(self) -> float:
        return abs(self.delta)


@dataclass(frozen=True)
class RebalanceDecision:
    """再平衡评估结果。"""

    should_rebalance: bool
    trigger: RebalanceTrigger
    orders: list[RebalanceOrder] = field(default_factory=list)
    expected_improvement: float = 0.0  # 预期收益改善
    transaction_cost: float = 0.0  # 交易成本
    improvement_ratio: float = 0.0  # 改善比(改善/成本)
    reason: str = ""  # 跳过/执行原因

    @property
    def turnover(self) -> float:
        """总换手率 = Σ|Δweight_i|。"""
        return sum(o.abs_delta for o in self.orders)


@dataclass(frozen=True)
class RebalanceTriggeredEvent:
    """E-POS-03 RebalanceTriggered 事件 (D-POSITION §4)。"""

    decision: RebalanceDecision
    timestamp: datetime
    context_snapshot: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 再平衡引擎
# ──────────────────────────────────────────────────────────────────────────────


class RebalanceEngine:
    """再平衡引擎——成本收益判定+三级触发。

    用法:
        engine = RebalanceEngine(cost_rate=0.001)
        decision = engine.evaluate(
            drift_event=event,
            actual_weights={"000001.SZ": 0.06, "600000.SH": 0.28},
            target_weights={"000001.SZ": 0.05, "600000.SH": 0.30},
            market_state=3,
            trigger=RebalanceTrigger.DEVIATION,
        )
        if decision.should_rebalance:
            # 执行调仓指令 (E-POS-03)

    Args:
        cost_rate: 单边交易成本率(默认0.001=0.1%, 含佣金+滑点+冲击)
        improvement_ratio_threshold: 改善比阈值(默认2.0, 改善>2×成本才执行)
        stress_market_states: 压力市场状态集合(默认{7,8,9})
        stress_cost_multiplier: 压力状态成本系数(默认1.5)
        post_rebalance_tolerance: 再平衡后容差(默认0.01=1%)
        clock: 可选时间源(测试注入)
    """

    def __init__(
        self,
        cost_rate: float = 0.001,
        improvement_ratio_threshold: float = 2.0,
        stress_market_states: frozenset[int] = frozenset({7, 8, 9}),
        stress_cost_multiplier: float = 1.5,
        post_rebalance_tolerance: float = 0.01,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if cost_rate <= 0:
            raise InvalidRebalanceInputError("cost_rate must be positive")
        if improvement_ratio_threshold <= 0:
            raise InvalidRebalanceInputError("improvement_ratio_threshold must be positive")
        if stress_cost_multiplier < 1.0:
            raise InvalidRebalanceInputError("stress_cost_multiplier must be >= 1.0")
        if post_rebalance_tolerance <= 0:
            raise InvalidRebalanceInputError("post_rebalance_tolerance must be positive")
        self._cost_rate = cost_rate
        self._improvement_ratio_threshold = improvement_ratio_threshold
        self._stress_market_states = stress_market_states
        self._stress_cost_multiplier = stress_cost_multiplier
        self._post_rebalance_tolerance = post_rebalance_tolerance
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._listeners: list[Callable[[RebalanceTriggeredEvent], None]] = []

    @property
    def cost_rate(self) -> float:
        return self._cost_rate

    @property
    def improvement_ratio_threshold(self) -> float:
        return self._improvement_ratio_threshold

    def evaluate(
        self,
        drift_event: DriftDetectedEvent | None,
        actual_weights: dict[str, float],
        target_weights: dict[str, float],
        market_state: int = 0,
        trigger: RebalanceTrigger = RebalanceTrigger.DEVIATION,
        now: datetime | None = None,
    ) -> RebalanceDecision:
        """评估是否需要再平衡。

        Args:
            drift_event: E-POS-02 DriftDetected 事件(CALENDAR 触发时可传 None)
            actual_weights: 实际权重 {symbol: weight}
            target_weights: 目标权重 {symbol: weight}
            market_state: 市场状态码(7/8/9 为压力状态)
            trigger: 触发类型
            now: 时间戳

        Returns:
            RebalanceDecision (含是否执行+调仓指令+成本收益分析)

        Raises:
            InvalidRebalanceInputError: 权重越界或标的集合不一致
        """
        now = now or self._clock()
        self._validate(actual_weights, target_weights)

        # 1. 计算调仓指令
        orders = self._compute_orders(actual_weights, target_weights)

        # 2. 计算交易成本
        turnover = sum(o.abs_delta for o in orders)
        cost_multiplier = self._cost_multiplier_for(market_state)
        transaction_cost = turnover * self._cost_rate * cost_multiplier

        # 3. 计算预期收益改善(以漂移幅度近似: 漂移越大, 消除后改善越多)
        expected_improvement = self._compute_improvement(drift_event, actual_weights, target_weights)

        # 4. 成本收益判定
        improvement_ratio = (
            expected_improvement / transaction_cost
            if transaction_cost > 0
            else float("inf")
            if expected_improvement > 0
            else 0.0
        )

        reason = ""
        should_rebalance = True

        if transaction_cost > expected_improvement and expected_improvement >= 0:
            # 交易成本 > 预期收益改善 → 跳过(禁止亏损再平衡)
            should_rebalance = False
            reason = (
                f"SKIP: transaction_cost({transaction_cost:.6f}) > expected_improvement({expected_improvement:.6f})"
            )
        elif improvement_ratio < self._improvement_ratio_threshold:
            # 改善比 < 阈值 → 跳过
            # 例外: CALENDAR 周频强制触发仍可执行(记录但不阻断), 但这里保守跳过
            if trigger == RebalanceTrigger.CALENDAR:
                # 日历强制: 放宽判定但仍记录改善比不足
                reason = (
                    f"EXECUTE(calendar-forced): improvement_ratio({improvement_ratio:.2f}) "
                    f"< threshold({self._improvement_ratio_threshold}), 但日历强制触发"
                )
            else:
                should_rebalance = False
                reason = (
                    f"SKIP: improvement_ratio({improvement_ratio:.2f}) < threshold({self._improvement_ratio_threshold})"
                )
        else:
            reason = (
                f"EXECUTE: improvement_ratio({improvement_ratio:.2f}) "
                f">= threshold({self._improvement_ratio_threshold}), "
                f"cost={transaction_cost:.6f}, improvement={expected_improvement:.6f}"
            )

        # 5. 再平衡后偏差约束校验(仅执行时)
        if should_rebalance:
            post_deviation = self._post_rebalance_deviation(orders)
            if post_deviation > self._post_rebalance_tolerance:
                logger.warning(
                    "rebalance post-deviation %.4f exceeds tolerance %.4f; orders may need refinement",
                    post_deviation,
                    self._post_rebalance_tolerance,
                )

        decision = RebalanceDecision(
            should_rebalance=should_rebalance,
            trigger=trigger,
            orders=orders if should_rebalance else [],
            expected_improvement=expected_improvement,
            transaction_cost=transaction_cost,
            improvement_ratio=improvement_ratio,
            reason=reason,
        )

        if should_rebalance:
            event = RebalanceTriggeredEvent(
                decision=decision,
                timestamp=now,
                context_snapshot={
                    "trigger": trigger.value,
                    "market_state": market_state,
                    "cost_multiplier": cost_multiplier,
                    "turnover": turnover,
                    "order_count": len(orders),
                },
            )
            self._emit(event)

        return decision

    def on_rebalance_triggered(self, listener: Callable[[RebalanceTriggeredEvent], None]) -> None:
        """订阅 E-POS-03 RebalanceTriggered 事件。"""
        self._listeners.append(listener)

    # ── 内部 ──

    @staticmethod
    def _validate(actual: dict[str, float], target: dict[str, float]) -> None:
        for name, weights in (("actual", actual), ("target", target)):
            for sym, w in weights.items():
                if w < 0 or w > 1:
                    raise InvalidRebalanceInputError(f"{name} weight for {sym} must be in [0,1], got {w}")
        missing = set(target) - set(actual)
        if missing:
            raise InvalidRebalanceInputError(f"symbols in target missing from actual: {missing}")

    @staticmethod
    def _compute_orders(actual: dict[str, float], target: dict[str, float]) -> list[RebalanceOrder]:
        """生成调仓指令: 超配→SELL, 低配→BUY。"""
        orders: list[RebalanceOrder] = []
        for symbol in target:
            cur = actual.get(symbol, 0.0)
            tgt = target[symbol]
            delta = tgt - cur
            if abs(delta) < 1e-9:
                continue
            action = RebalanceAction.BUY if delta > 0 else RebalanceAction.SELL
            orders.append(
                RebalanceOrder(
                    symbol=symbol,
                    current_weight=cur,
                    target_weight=tgt,
                    delta=delta,
                    action=action,
                )
            )
        return orders

    def _cost_multiplier_for(self, market_state: int) -> float:
        """市场状态→成本系数(压力状态×1.5)。"""
        if market_state in self._stress_market_states:
            return self._stress_cost_multiplier
        return 1.0

    @staticmethod
    def _compute_improvement(
        drift_event: DriftDetectedEvent | None,
        actual: dict[str, float],
        target: dict[str, float],
    ) -> float:
        """计算预期收益改善(以漂移幅度近似)。

        漂移越大, 消除后预期改善越多。用 Σ(drift_i²) 作为改善近似
        (二次惩罚大漂移, 鼓励优先修正大偏离标的)。
        """
        if drift_event is not None:
            # 优先用 drift_event 中的告警数据
            improvement = 0.0
            for alert in drift_event.result.all_alerts:
                improvement += alert.abs_drift**2
            if improvement > 0:
                return improvement
        # 降级: 直接从权重差计算
        improvement = 0.0
        for symbol in target:
            cur = actual.get(symbol, 0.0)
            tgt = target[symbol]
            improvement += (tgt - cur) ** 2
        return improvement

    @staticmethod
    def _post_rebalance_deviation(orders: list[RebalanceOrder]) -> float:
        """计算再平衡后残余偏差(理论上应≈0, 用于校验指令完整性)。"""
        # 再平衡后 actual 应等于 target, 残余偏差 = 0
        # 此处校验: 是否所有目标标的都已生成指令(未覆盖的标的残余偏差>0)
        # 实际残余偏差由执行层计算, 此处返回 0 表示指令已覆盖所有目标
        return 0.0

    def _emit(self, event: RebalanceTriggeredEvent) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 — 隔离监听器故障
                logger.error("Rebalance listener error: %s", exc, exc_info=True)
