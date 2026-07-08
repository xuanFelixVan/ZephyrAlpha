# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_anomaly_detector
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_anomaly_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 统计异常检测引擎 — 基线学习 + 实时异常判断

监控每个 Agent 的运行时行为指标，检测偏离历史基线的异常:
  - task_rate: 任务提交速率异常 — 突增(DoS前兆) / 突降(Agent僵死前兆)
  - file_touch_rate: 文件触碰速率异常 — 过少(无产出) / 过多(无差别修改前兆)
  - lock_contention: 锁竞争频率异常 — 频繁抢锁(资源争抢)
  - error_rate: 错误率异常 — 持续偏高(Agent故障)
  - message_size: 跨Agent消息大小异常 — 超大消息(上下文泄漏前兆)

方法: 基于 Z-Score 的相对基线偏离检测
  基线: 过去 N 个时间窗口的滑动平均值 + 标准差
  异常: |z_score| > threshold -> 触发告警
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum


class MetricKey(str, Enum):
    TASK_RATE = "task_rate"
    FILE_TOUCH_RATE = "file_touch_rate"
    LOCK_CONTENTION = "lock_contention"
    ERROR_RATE = "error_rate"
    MESSAGE_SIZE = "message_size"


class AnomalyLevel(str, Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyRecord:
    agent_id: str
    metric: MetricKey
    level: AnomalyLevel
    z_score: float
    current_value: float
    baseline_mean: float
    baseline_std: float
    timestamp: float
    description: str = ""


@dataclass
class MetricBaseline:
    window_size: int = 30
    history: deque[float] = field(default_factory=lambda: deque(maxlen=30))
    _mean: float = 0.0
    _m2: float = 0.0
    _count: int = 0

    def update(self, value: float):
        self.history.append(value)
        self._count = min(self._count + 1, self.window_size)
        delta = value - self._mean
        self._mean += delta / max(1, len(self.history))
        delta2 = value - self._mean
        self._m2 += delta * delta2

    @property
    def mean(self) -> float:
        if not self.history:
            return 0.0
        return self._mean

    @property
    def std(self) -> float:
        if len(self.history) < 2:
            return 1.0
        variance = self._m2 / max(1, len(self.history) - 1)
        return max(abs(variance) ** 0.5, 0.001)

    def z_score(self, value: float) -> float:
        if self.std == 0:
            return 0.0
        return (value - self.mean) / self.std


class A2AAnomalyDetector:
    """Agent 行为统计异常检测器.

    学习每个 (Agent, Metric) 对的基线，偏差超过阈值时报告异常.
    """

    _ZSCORE_THRESHOLDS = {
        AnomalyLevel.ELEVATED: 2.0,
        AnomalyLevel.HIGH: 3.0,
        AnomalyLevel.CRITICAL: 5.0,
    }

    def __init__(
        self,
        baseline_window: int = 30,
        min_samples_before_detect: int = 5,
    ):
        self._baselines: dict[str, dict[MetricKey, MetricBaseline]] = {}
        self._baseline_window = baseline_window
        self._min_samples = min_samples_before_detect

    def record(
        self,
        agent_id: str,
        metric: MetricKey,
        value: float,
    ) -> AnomalyRecord | None:
        if agent_id not in self._baselines:
            self._baselines[agent_id] = {}
        if metric not in self._baselines[agent_id]:
            self._baselines[agent_id][metric] = MetricBaseline(window_size=self._baseline_window)

        baseline = self._baselines[agent_id][metric]
        baseline.update(value)

        if len(baseline.history) < self._min_samples:
            return None

        z = baseline.z_score(value)
        level = self._zscore_to_level(z)

        if level is AnomalyLevel.NORMAL:
            return None

        return AnomalyRecord(
            agent_id=agent_id,
            metric=metric,
            level=level,
            z_score=round(z, 3),
            current_value=round(value, 3),
            baseline_mean=round(baseline.mean, 3),
            baseline_std=round(baseline.std, 3),
            timestamp=time.time(),
            description=f"{agent_id}/{metric.value}: z={z:.2f}, "
            f"val={value:.2f}, μ={baseline.mean:.2f}, σ={baseline.std:.2f}",
        )

    def record_batch(
        self,
        agent_id: str,
        values: dict[MetricKey, float],
    ) -> list[AnomalyRecord]:
        records: list[AnomalyRecord] = []
        for metric, value in values.items():
            result = self.record(agent_id, metric, value)
            if result is not None:
                records.append(result)
        return records

    def get_baseline(self, agent_id: str, metric: MetricKey) -> MetricBaseline | None:
        if agent_id not in self._baselines:
            return None
        return self._baselines[agent_id].get(metric)

    def get_baseline_stats(self, agent_id: str) -> dict[str, dict]:
        if agent_id not in self._baselines:
            return {}
        return {
            metric.value: {
                "samples": len(bl.history),
                "mean": round(bl.mean, 3),
                "std": round(bl.std, 3),
                "recent_5": list(bl.history)[-5:] if len(bl.history) >= 5 else list(bl.history),
            }
            for metric, bl in self._baselines[agent_id].items()
        }

    def _zscore_to_level(self, z: float) -> AnomalyLevel:
        abs_z = abs(z)
        if abs_z >= self._ZSCORE_THRESHOLDS[AnomalyLevel.CRITICAL]:
            return AnomalyLevel.CRITICAL
        if abs_z >= self._ZSCORE_THRESHOLDS[AnomalyLevel.HIGH]:
            return AnomalyLevel.HIGH
        if abs_z >= self._ZSCORE_THRESHOLDS[AnomalyLevel.ELEVATED]:
            return AnomalyLevel.ELEVATED
        return AnomalyLevel.NORMAL

    @staticmethod
    def is_anomaly(records: list[AnomalyRecord]) -> bool:
        return len(records) > 0

    @staticmethod
    def anomaly_summary(records: list[AnomalyRecord]) -> dict:
        levels: dict[str, int] = {}
        metrics: dict[str, int] = {}
        for r in records:
            levels[r.level.value] = levels.get(r.level.value, 0) + 1
            metrics[r.metric.value] = metrics.get(r.metric.value, 0) + 1
        return {
            "total_anomalies": len(records),
            "by_level": levels,
            "by_metric": metrics,
            "worst_z": max(abs(r.z_score) for r in records) if records else 0.0,
        }
