# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.agent_health_monitor
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.integration.shared.schema.schemas; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_agent_health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-3-11 Agent Health Monitor
"""
AgentHealthMonitor · Agent 健康监控（三态 + 5 项 SLO）
======================================================

Task ID     : T-3-11
Depends     : T-3-10（agent_orchestrator.py HealthMonitor / OrchestrationResult）
safety_level: M

核心职责
--------
1. **三态健康判定**：HEALTHY / DEGRADED / UNHEALTHY
   - HEALTHY：所有 SLO 达标
   - DEGRADED：1-2 项 SLO 超出软阈值但未超出硬阈值
   - UNHEALTHY：任何 SLO 超出硬阈值

2. **5 项 SLO 监控**
   - latency_p99 < 5000ms（硬）/ 3000ms（软）
   - error_rate < 5%（硬）/ 3%（软）
   - throughput > 10/min（硬）/ 15/min（软）
   - hallucination_rate < 10%（硬）/ 7%（软）
   - context_utilization > 60%（硬）/ 70%（软）

3. **与 agent_orchestrator.py 集成**
   - 消费 OrchestrationResult 事件
   - 生成 HealthStatus 供上层决策

零外部依赖：仅 pydantic + 标准库。
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import default_now
from zephyr.trading.orchestrator.agent_orchestrator import OrchestrationResult

__all__ = [
    "AgentHealthMonitor",
    "HealthState",
    "HealthStatus",
    "SLOConfig",
    "SLOViolation",
]


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


class SLOConfig(BaseModel):
    model_config = BASE_CONFIG

    latency_p99_ms_hard: float = 5000.0
    latency_p99_ms_soft: float = 3000.0
    error_rate_hard: float = 0.05
    error_rate_soft: float = 0.03
    throughput_per_min_hard: float = 10.0
    throughput_per_min_soft: float = 15.0
    hallucination_rate_hard: float = 0.10
    hallucination_rate_soft: float = 0.07
    context_utilization_hard: float = 0.60
    context_utilization_soft: float = 0.70


class SLOViolation(BaseModel):
    """SLO 违规记录模型（指标名 + 实际值 + 阈值 + 违规方向）。

    用于 AgentHealthMonitor 在检测到 SLO 指标越过 hard/soft 阈值时
    构造结构化违规对象，供审计日志记录和降级策略触发。
    """

    model_config = BASE_CONFIG

    metric: str
    value: float
    threshold: float
    severity: str = Field(description="hard or soft")


class HealthStatus(BaseModel):
    model_config = BASE_CONFIG

    state: HealthState
    violations: list[SLOViolation] = Field(default_factory=list)
    latency_p99_ms: float = 0.0
    error_rate: float = 0.0
    throughput_per_min: float = 0.0
    hallucination_rate: float = 0.0
    context_utilization: float = 0.0
    sample_count: int = 0
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentHealthMonitor:
    """三态 Agent 健康监控器，消费 OrchestrationResult 事件。

    Parameters
    ----------
    window_size : int
        滑动窗口大小（最近 N 次 orchestrate 结果）。
    slo_config : SLOConfig | None
        SLO 阈值配置；默认使用 SLOConfig 默认值。
    throughput_window_sec : int
        吞吐量统计窗口（秒）。
    now : Callable[[], datetime]
        时间源（便于测试）。
    """

    def __init__(
        self,
        window_size: int = 100,
        slo_config: SLOConfig | None = None,
        throughput_window_sec: int = 60,
        now: Callable[[], datetime] = default_now,
    ) -> None:
        if window_size < 1:
            raise ValueError("window_size 必须 >= 1")
        self._window = window_size
        self._slo = slo_config or SLOConfig()
        self._throughput_window_sec = throughput_window_sec
        self._now = now
        self._latencies: deque[float] = deque(maxlen=window_size)
        self._errors: deque[int] = deque(maxlen=window_size)
        self._hallu: deque[int] = deque(maxlen=window_size)
        self._ctx_util: deque[float] = deque(maxlen=window_size)
        self._completions: deque[datetime] = deque(maxlen=window_size * 4)

    def record(self, result: OrchestrationResult) -> None:
        self._latencies.append(float(result.latency_ms))
        self._errors.append(0 if result.success else 1)
        is_hallu = bool(result.hallucination is not None and result.hallucination.get("is_hallucination"))
        self._hallu.append(1 if is_hallu else 0)
        if result.token_budget > 0:
            self._ctx_util.append(result.token_used / result.token_budget)
        else:
            self._ctx_util.append(0.0)
        self._completions.append(self._now())

    def evaluate(self) -> HealthStatus:
        latency_p99 = self._percentile(list(self._latencies), 99) if self._latencies else 0.0
        error_rate = (sum(self._errors) / len(self._errors)) if self._errors else 0.0
        hallu_rate = (sum(self._hallu) / len(self._hallu)) if self._hallu else 0.0
        ctx_util = sum(self._ctx_util) / len(self._ctx_util) if self._ctx_util else 0.0
        throughput = self._throughput_per_min()

        violations: list[SLOViolation] = []
        hard_count = 0

        if latency_p99 > self._slo.latency_p99_ms_hard:
            violations.append(
                SLOViolation(
                    metric="latency_p99_ms",
                    value=latency_p99,
                    threshold=self._slo.latency_p99_ms_hard,
                    severity="hard",
                )
            )
            hard_count += 1
        elif latency_p99 > self._slo.latency_p99_ms_soft:
            violations.append(
                SLOViolation(
                    metric="latency_p99_ms",
                    value=latency_p99,
                    threshold=self._slo.latency_p99_ms_soft,
                    severity="soft",
                )
            )

        if error_rate > self._slo.error_rate_hard:
            violations.append(
                SLOViolation(
                    metric="error_rate",
                    value=error_rate,
                    threshold=self._slo.error_rate_hard,
                    severity="hard",
                )
            )
            hard_count += 1
        elif error_rate > self._slo.error_rate_soft:
            violations.append(
                SLOViolation(
                    metric="error_rate",
                    value=error_rate,
                    threshold=self._slo.error_rate_soft,
                    severity="soft",
                )
            )

        if throughput < self._slo.throughput_per_min_hard and len(self._latencies) >= self._window:
            violations.append(
                SLOViolation(
                    metric="throughput_per_min",
                    value=throughput,
                    threshold=self._slo.throughput_per_min_hard,
                    severity="hard",
                )
            )
            hard_count += 1
        elif throughput < self._slo.throughput_per_min_soft and len(self._latencies) >= self._window:
            violations.append(
                SLOViolation(
                    metric="throughput_per_min",
                    value=throughput,
                    threshold=self._slo.throughput_per_min_soft,
                    severity="soft",
                )
            )

        if hallu_rate > self._slo.hallucination_rate_hard:
            violations.append(
                SLOViolation(
                    metric="hallucination_rate",
                    value=hallu_rate,
                    threshold=self._slo.hallucination_rate_hard,
                    severity="hard",
                )
            )
            hard_count += 1
        elif hallu_rate > self._slo.hallucination_rate_soft:
            violations.append(
                SLOViolation(
                    metric="hallucination_rate",
                    value=hallu_rate,
                    threshold=self._slo.hallucination_rate_soft,
                    severity="soft",
                )
            )

        if ctx_util < self._slo.context_utilization_hard and len(self._latencies) >= self._window:
            violations.append(
                SLOViolation(
                    metric="context_utilization",
                    value=ctx_util,
                    threshold=self._slo.context_utilization_hard,
                    severity="hard",
                )
            )
            hard_count += 1
        elif ctx_util < self._slo.context_utilization_soft and len(self._latencies) > 0:
            violations.append(
                SLOViolation(
                    metric="context_utilization",
                    value=ctx_util,
                    threshold=self._slo.context_utilization_soft,
                    severity="soft",
                )
            )

        if hard_count > 0:
            state = HealthState.UNHEALTHY
        elif len(violations) > 0:
            state = HealthState.DEGRADED
        else:
            state = HealthState.HEALTHY

        return HealthStatus(
            state=state,
            violations=violations,
            latency_p99_ms=round(latency_p99, 3),
            error_rate=round(error_rate, 4),
            throughput_per_min=round(throughput, 3),
            hallucination_rate=round(hallu_rate, 4),
            context_utilization=round(min(ctx_util, 1.0), 4),
            sample_count=len(self._latencies),
            evaluated_at=self._now(),
        )

    def reset(self) -> None:
        self._latencies.clear()
        self._errors.clear()
        self._hallu.clear()
        self._ctx_util.clear()
        self._completions.clear()

    @staticmethod
    def _percentile(values: list[float], pct: float) -> float:
        if not values:
            return 0.0
        sorted_v = sorted(values)
        if len(sorted_v) == 1:
            return sorted_v[0]
        rank = max(1, int(round(len(sorted_v) * pct / 100.0 + 0.5)) - 1)
        rank = min(rank, len(sorted_v) - 1)
        return sorted_v[rank]

    def _throughput_per_min(self) -> float:
        if not self._completions:
            return 0.0
        now = self._now()
        window_start = now.timestamp() - self._throughput_window_sec
        count = sum(1 for ts in self._completions if ts.timestamp() >= window_start)
        return count * (60.0 / self._throughput_window_sec)

    @property
    def sample_count(self) -> int:
        return len(self._latencies)
