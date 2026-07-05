# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §observability
# [MODULE] zephyr.security.access_control.observability
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_observability_agent_rbac.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] metrics never lost before reset; anomaly detection deterministic for same inputs
# [MODIFY-GUARD] blueprint.md §observability
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] all methods never raise; detect_* return AnomalyResult
# [TESTS] tests/agent_rbac/test_observability_agent_rbac.py
# [A_module] module_id=MOD-SEC_observability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ObservabilityReporter — 指标上报与异常检测.

依据蓝图 MOD-INF-018 §observability:
- 记录权限决策指标
- 检测操作密度异常
- 检测非工作时间破坏性操作
- 检测成熟度越级
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AnomalyResult:
    """异常检测结果.

    Attributes:
        anomaly: 是否检测到异常
        reason: 异常原因
        agent_id: 相关 agent ID
        metric: 相关指标名
    """

    anomaly: bool = False
    reason: str = ""
    agent_id: str = ""
    metric: str = ""


@dataclass
class MetricEntry:
    """指标条目.

    Attributes:
        agent_id: agent ID
        layer: 检查层
        decision: 决策结果
        timestamp: 记录时间戳
    """

    agent_id: str = ""
    layer: str = ""
    decision: str = ""
    timestamp: float = field(default_factory=time.time)


_MATURITY_ORDER = ["L0_INTERN", "L1_JUNIOR", "L2_REGULAR", "L3_SENIOR", "L4_PRINCIPAL"]


class ObservabilityReporter:
    """指标上报器与异常检测器."""

    def __init__(self) -> None:
        self._metrics: list[MetricEntry] = []
        self._noise_count: int = 0
        self._noise_sources: list[str] = []
        self._density_window: dict[str, list[float]] = {}

    def record_decision(self, agent_id: str, layer: str, decision: str) -> None:
        """记录权限决策指标."""
        entry = MetricEntry(
            agent_id=agent_id,
            layer=layer,
            decision=decision,
        )
        self._metrics.append(entry)
        now = time.time()
        if agent_id not in self._density_window:
            self._density_window[agent_id] = []
        self._density_window[agent_id].append(now)

    def record_noise(self, source: str) -> None:
        """记录噪声事件."""
        self._noise_count += 1
        self._noise_sources.append(source)

    @property
    def signal_noise_ratio(self) -> float:
        """信噪比 — signal / (noise + 1)."""
        signal = len(self._metrics)
        return signal / (self._noise_count + 1)

    def check_signal_noise_alert(self) -> bool:
        """检查是否触发信噪比告警（噪声 >= 10）."""
        return self._noise_count >= 10

    def detect_density_anomaly(
        self,
        agent_id: str,
        count: int,
        threshold_per_minute: int = 60,
    ) -> AnomalyResult:
        """检测操作密度异常."""
        if count > threshold_per_minute:
            return AnomalyResult(
                anomaly=True,
                reason=f"density anomaly: {count} > threshold {threshold_per_minute}",
                agent_id=agent_id,
                metric="density",
            )
        return AnomalyResult(
            anomaly=False,
            reason=f"density normal: {count} <= threshold {threshold_per_minute}",
            agent_id=agent_id,
            metric="density",
        )

    def detect_off_hours_destructive(
        self,
        agent_id: str,
        operation: str,
        timestamp: float | None = None,
    ) -> AnomalyResult:
        """检测非工作时间破坏性操作."""
        if timestamp is None:
            timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
        hour = dt.hour
        is_off_hours = hour < 8 or hour >= 18
        is_destructive = operation.startswith("delete:") or operation.startswith("destroy")
        if is_off_hours and is_destructive:
            return AnomalyResult(
                anomaly=True,
                reason=f"off-hours destructive: {operation} at hour {hour}",
                agent_id=agent_id,
                metric="off_hours_destructive",
            )
        return AnomalyResult(
            anomaly=False,
            reason=f"normal: {operation} at hour {hour}",
            agent_id=agent_id,
            metric="off_hours_destructive",
        )

    def detect_maturity_escalation(
        self,
        agent_id: str,
        from_level: str,
        to_level: str,
    ) -> AnomalyResult:
        """检测成熟度越级（跳级 > 1 为异常）."""
        try:
            from_idx = _MATURITY_ORDER.index(from_level)
            to_idx = _MATURITY_ORDER.index(to_level)
        except ValueError:
            return AnomalyResult(
                anomaly=False,
                reason=f"unknown maturity level: {from_level} -> {to_level}",
                agent_id=agent_id,
                metric="maturity_escalation",
            )
        jump = to_idx - from_idx
        if jump > 1:
            return AnomalyResult(
                anomaly=True,
                reason=f"maturity jump {jump}: {from_level} -> {to_level}",
                agent_id=agent_id,
                metric="maturity_escalation",
            )
        return AnomalyResult(
            anomaly=False,
            reason=f"normal step {jump}: {from_level} -> {to_level}",
            agent_id=agent_id,
            metric="maturity_escalation",
        )

    def get_metrics_summary(self) -> dict:
        """返回指标摘要."""
        return {
            "total_metrics": len(self._metrics),
            "noise_count": self._noise_count,
            "signal_noise_ratio": self.signal_noise_ratio,
        }

    def reset(self) -> None:
        """重置所有指标."""
        self._metrics.clear()
        self._noise_count = 0
        self._noise_sources.clear()
        self._density_window.clear()


__all__ = [
    "AnomalyResult",
    "MetricEntry",
    "ObservabilityReporter",
]
