# [BLUEPRINT] MOD-POS-003 | docs/03_modules/_domain_position/position_drift_monitor/blueprint.md
# [MODULE] zephyr.position.core.position_drift_monitor
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-004(再平衡引擎) ; D-PF-CORE ; D-GOVERNANCE(审计)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 组合漂移>±2%触发再平衡评估; 单标的漂移>±3%触发标的级评估; 漂移阈值可配置(默认设计值)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDriftInputError
# [TESTS] tests/position/test_position_drift_monitor.py
# [A_module] module_id=MOD-POS-003 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Position Drift Monitor — 仓位漂移监控器 (MOD-POS-003)

监控实际持仓权重与目标权重的偏离, 超阈值产出 E-POS-02 DriftDetected 事件。

两级阈值 (D-POSITION §1.1 POS-03):
    - 组合总仓位漂移 > ±2% → 触发组合级再平衡评估
    - 单标的漂移 > ±3% → 触发标的级再平衡评估

三级监控频率 (消费 SELL-00 持仓分级):
    - WATCH(红): 实时秒级监控(亏损接近止损/主力异常)
    - MONITOR(黄): 5分钟级(正常持仓)
    - HOLD(绿): 仅重大事件(深度盈利长期持有)

属A类基础设施(漂移计算+阈值判定+分级, 逻辑明确), 阈值为C类可调参数。
依据: D:\临时工作区\依赖图-D-POSITION-仓位管理域.md §1.1 POS-03, §4 E-POS-02
SSoT: depgraph MOD-POS-003
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 实际持仓权重 字典
#   fields: {symbol: weight} 权重∈[0,1]
#   code: check() 参数 actual_weights
# - id: I2
#   name: 目标持仓权重 字典
#   fields: {symbol: weight} 权重∈[0,1]，标的必须都在actual中
#   code: check() 参数 target_weights
# - id: I3
#   name: 持仓分级 字典(可选)
#   fields: {symbol: TriageLevel} WATCH红秒级/MONITOR黄5分钟/HOLD绿重大事件，来自SELL-00
#   code: check() 参数 triage_levels
# 层: 算法
# - id: A1
#   name_zh: ① 输入合法性校验
#   name_en: _validate
#   intro: 检查权重越界和标的集合不一致，非法直接抛错
#   desc: 权重必须∈[0,1]；target的标的必须都在actual中，否则抛InvalidDriftInputError
#   inputs: I1 I2
#   outputs: 校验通过或异常
# - id: A2
#   name_zh: ② 组合级漂移检测
#   name_en: portfolio drift check
#   intro: 总实际仓位减总目标仓位，偏离超±2%就告警
#   desc: portfolio_drift=Σactual-Σtarget；|drift|>0.02触发组合级告警，默认WATCH级
#   inputs: I1 I2
#   outputs: 组合级DriftAlert(可空)
#   invariant: 组合漂移>±2%触发再平衡评估
# - id: A3
#   name_zh: ③ 标的级漂移检测
#   name_en: symbol drift check
#   intro: 逐个标的算实际减目标权重，偏离超±3%就告警
#   desc: drift=actual-target；|drift|>0.03触发标的级告警，按triage_levels分级缺省MONITOR
#   inputs: I1 I2 I3
#   outputs: 标的级DriftAlert列表
#   invariant: 单标的漂移>±3%触发标的级评估
# - id: A4
#   name_zh: ④ 漂移事件分发
#   name_en: _emit
#   intro: 检测到任何超阈值漂移才广播事件，监听器异常不阻断主流程
#   desc: has_drift为真时构造DriftDetectedEvent(含漂移快照)分发给订阅者
#   inputs: A2 A3
#   outputs: E-POS-02事件
# 层: 输出
# - id: O1
#   name_zh: 漂移检测结果
#   name_en: DriftResult
#   intro: 组合级+标的级告警列表，附时间戳
#   downstream: MOD-POS-004再平衡引擎消费
# - id: O2
#   name_zh: 漂移检测事件 E-POS-02
#   name_en: DriftDetectedEvent
#   intro: 超阈值漂移时广播给订阅者
#   downstream: MOD-POS-004再平衡引擎 D-PF-CORE D-GOVERNANCE审计
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# I3 --> A3
# A1 --> A2
# A1 --> A3
# A2 --> A4
# A3 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "DriftScope",
    "TriageLevel",
    "DriftAlert",
    "DriftResult",
    "DriftDetectedEvent",
    "PositionDriftMonitor",
    "InvalidDriftInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class DriftScope(str, Enum):
    """漂移检测范围。"""

    PORTFOLIO = "PORTFOLIO"  # 组合级
    SYMBOL = "SYMBOL"  # 标的级


class TriageLevel(str, Enum):
    """持仓分级 (来自 SELL-00, 决定监控频率)。"""

    WATCH = "WATCH"  # 红色: 实时秒级
    MONITOR = "MONITOR"  # 黄色: 5分钟级
    HOLD = "HOLD"  # 绿色: 仅重大事件


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidDriftInputError(ZephyrBaseError):
    """漂移输入数据非法(如权重越界、标的集合不一致)。"""

    error_code = "ZA-POS-0004"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DriftAlert:
    """单条漂移告警。"""

    scope: DriftScope
    symbol: str | None  # 组合级为 None
    actual_weight: float
    target_weight: float
    drift: float  # 有符号漂移(正=超配, 负=低配)
    threshold: float  # 触发阈值
    triage: TriageLevel = TriageLevel.MONITOR

    @property
    def abs_drift(self) -> float:
        return abs(self.drift)

    @property
    def is_overweight(self) -> bool:
        """是否超配(actual > target)。"""
        return self.drift > 0


@dataclass(frozen=True)
class DriftResult:
    """漂移检测结果。"""

    portfolio_alert: DriftAlert | None
    symbol_alerts: list[DriftAlert] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def has_drift(self) -> bool:
        """是否检测到任何超阈值漂移。"""
        return self.portfolio_alert is not None or len(self.symbol_alerts) > 0

    @property
    def all_alerts(self) -> list[DriftAlert]:
        result: list[DriftAlert] = []
        if self.portfolio_alert is not None:
            result.append(self.portfolio_alert)
        result.extend(self.symbol_alerts)
        return result


@dataclass(frozen=True)
class DriftDetectedEvent:
    """E-POS-02 DriftDetected 事件 (D-POSITION §4)。"""

    result: DriftResult
    timestamp: datetime
    context_snapshot: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 漂移监控器
# ──────────────────────────────────────────────────────────────────────────────


class PositionDriftMonitor:
    """仓位漂移监控器——两级阈值检测+三级分级。

    用法:
        monitor = PositionDriftMonitor()
        result = monitor.check(
            actual_weights={"000001.SZ": 0.06, "600000.SH": 0.28},
            target_weights={"000001.SZ": 0.05, "600000.SH": 0.30},
            triage_levels={"000001.SZ": TriageLevel.WATCH},
        )
        if result.has_drift:
            # 触发再平衡评估 (E-POS-02)

    Args:
        portfolio_threshold: 组合漂移阈值(默认0.02=±2%, 设计值)
        symbol_threshold: 标的漂移阈值(默认0.03=±3%, 设计值)
        clock: 可选时间源(测试注入)
    """

    def __init__(
        self,
        portfolio_threshold: float = 0.02,
        symbol_threshold: float = 0.03,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if portfolio_threshold <= 0 or symbol_threshold <= 0:
            raise InvalidDriftInputError("thresholds must be positive")
        self._portfolio_threshold = portfolio_threshold
        self._symbol_threshold = symbol_threshold
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._listeners: list[Callable[[DriftDetectedEvent], None]] = []

    @property
    def portfolio_threshold(self) -> float:
        return self._portfolio_threshold

    @property
    def symbol_threshold(self) -> float:
        return self._symbol_threshold

    def check(
        self,
        actual_weights: dict[str, float],
        target_weights: dict[str, float],
        triage_levels: dict[str, TriageLevel] | None = None,
        now: datetime | None = None,
    ) -> DriftResult:
        """检测持仓漂移。

        Args:
            actual_weights: 实际权重 {symbol: weight}
            target_weights: 目标权重 {symbol: weight}
            triage_levels: 持仓分级 {symbol: TriageLevel}(来自 SELL-00), 缺省 MONITOR
            now: 时间戳

        Returns:
            DriftResult (含组合级+标的级告警)

        Raises:
            InvalidDriftInputError: 权重越界或标的集合不一致
        """
        now = now or self._clock()
        triage_levels = triage_levels or {}
        self._validate(actual_weights, target_weights)

        # 组合级漂移: 总仓位差异
        actual_total = sum(actual_weights.values())
        target_total = sum(target_weights.values())
        portfolio_drift = actual_total - target_total
        portfolio_alert: DriftAlert | None = None
        if abs(portfolio_drift) > self._portfolio_threshold:
            portfolio_alert = DriftAlert(
                scope=DriftScope.PORTFOLIO,
                symbol=None,
                actual_weight=actual_total,
                target_weight=target_total,
                drift=portfolio_drift,
                threshold=self._portfolio_threshold,
                triage=TriageLevel.WATCH,  # 组合级漂移默认 WATCH
            )

        # 标的级漂移
        symbol_alerts: list[DriftAlert] = []
        for symbol in target_weights:
            actual = actual_weights.get(symbol, 0.0)
            target = target_weights[symbol]
            drift = actual - target
            if abs(drift) > self._symbol_threshold:
                symbol_alerts.append(
                    DriftAlert(
                        scope=DriftScope.SYMBOL,
                        symbol=symbol,
                        actual_weight=actual,
                        target_weight=target,
                        drift=drift,
                        threshold=self._symbol_threshold,
                        triage=triage_levels.get(symbol, TriageLevel.MONITOR),
                    )
                )

        result = DriftResult(
            portfolio_alert=portfolio_alert,
            symbol_alerts=symbol_alerts,
            timestamp=now,
        )
        if result.has_drift:
            event = DriftDetectedEvent(
                result=result,
                timestamp=now,
                context_snapshot={
                    "portfolio_drift": portfolio_drift,
                    "symbol_drift_count": len(symbol_alerts),
                    "symbols": [a.symbol for a in symbol_alerts],
                },
            )
            self._emit(event)
        return result

    def on_drift_detected(self, listener: Callable[[DriftDetectedEvent], None]) -> None:
        """订阅 E-POS-02 DriftDetected 事件。"""
        self._listeners.append(listener)

    # ── 内部 ──

    @staticmethod
    def _validate(actual: dict[str, float], target: dict[str, float]) -> None:
        for name, weights in (("actual", actual), ("target", target)):
            for sym, w in weights.items():
                if w < 0 or w > 1:
                    raise InvalidDriftInputError(f"{name} weight for {sym} must be in [0,1], got {w}")
        # target 的标的必须都有 actual (actual 可多不可少)
        missing = set(target) - set(actual)
        if missing:
            raise InvalidDriftInputError(f"symbols in target missing from actual: {missing}")

    def _emit(self, event: DriftDetectedEvent) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: 隔离监听器故障
                logger.error("Drift listener error: %s", exc, exc_info=True)
