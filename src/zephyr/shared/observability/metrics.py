# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.observability.metrics
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
metrics.py —— 轻量级 Metrics 收集基础设施（Phase 9 新增 | 盲点 B17 修复）

痛点修复：health.py 能回答"是否健康"，但不能回答"有多快/多少错误"——
  1. 没有 Counter / Gauge / Histogram → 无法追踪 API 调用成功率/延迟分布
  2. 没有 Prometheus 风格的指标 → DevOps 无法接入监控系统
  3. AI agent 的性能指标缺失 → 无法做 AI 工程质量分析

设计对标：
  - Prometheus Python client（Counter / Gauge / Histogram / Summary）
  - Spring Boot Actuator Metrics（Micrometer facade）
  - OpenTelemetry Metrics API

设计原则：
  - 零依赖第三方库——只用 Python 标准库
  - Prometheus 兼容的文本格式输出（方便接入 Grafana）
  - 线程安全——所有指标操作使用 Lock
  - 轻量——指标本身不产生显著的 CPU/内存开销

AI 施工约定：
  - 任何外部 API 调用 MUST 记录 duration + status 指标
  - 任何 AI agent 的决策点 SHOULD 记录 counter 指标
  - 健康检查 + 指标暴露 = 完整的可观测性三角

SSoT: MOD-INF-016 §2.16 shared-metrics
Version: 0.1.0
"""

from __future__ import annotations

from typing import Final
import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum, unique
from typing import Any

_logger = logging.getLogger(__name__)

__all__ = [
    "COUNT_API_ERRORS",
    "COUNT_LLM_CALLS",
    "HIST_LATENCY",
    "MetricSnapshot",
    "MetricType",
    "MetricsRegistry",
    "get_registry",
]

COUNT_LLM_CALLS: Final[str] = "zephyr_llm_calls_total"
COUNT_API_ERRORS: Final[str] = "zephyr_api_errors_total"
HIST_LATENCY: Final[str] = "zephyr_request_latency_seconds"


@unique
class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class MetricSnapshot:
    name: str
    type: MetricType
    value: float
    labels: dict[str, str]


class MetricsRegistry:
    """线程安全的轻量级 Metrics 注册表。

    对标 Prometheus 的 Counter / Gauge / Histogram 三分类。

    Usage::

        reg = get_registry()
        reg.inc("llm_calls_total", {"model":"deepseek","status":"success"})
        reg.observe("request_latency_seconds", 0.523, {"endpoint":"/chat"})
        print(reg.prometheus_text())
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, dict[tuple[tuple[str, str], ...], float]] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, dict[tuple[tuple[str, str], ...], list[float]]] = {}
        self._histogram_buckets: list[float] = [
            0.001,
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            10.0,
            30.0,
            60.0,
        ]

    def _label_key(self, labels: dict[str, str]) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(labels.items()))

    def inc(self, name: str, labels: dict[str, str] | None = None) -> None:
        with self._lock:
            if name not in self._counters:
                self._counters[name] = {}
            key = self._label_key(labels or {})
            self._counters[name][key] = self._counters[name].get(key, 0.0) + 1.0

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = {}
            key = self._label_key(labels or {})
            if key not in self._histograms[name]:
                self._histograms[name][key] = []
            self._histograms[name][key].append(value)
            if len(self._histograms[name][key]) > 10000:
                self._histograms[name][key] = self._histograms[name][key][-5000:]
                _logger.warning(
                    "Metrics histogram '%s' truncated to 5000 samples (labels=%s) — "
                    "p99/p50 may be biased toward recent observations",
                    name,
                    dict(key),
                )

    def measure(self, name: str, labels: dict[str, str] | None = None) -> _TimingContext:
        return _TimingContext(self, name, labels)

    def prometheus_text(self) -> str:
        """导出 Prometheus 兼容的文本格式。

        可在 /metrics 端点直接输出。
        """
        lines: list[str] = []
        with self._lock:
            for name, data in self._counters.items():
                for label_key, value in data.items():
                    label_str = self._format_labels(dict(label_key))
                    lines.append(f"{name}{{{label_str}}} {value:.0f}")
            for name, value in self._gauges.items():
                lines.append(f"{name} {value}")
            for name, data in self._histograms.items():
                for label_key, observations in data.items():
                    label_dict = dict(label_key)
                    label_str = self._format_labels(label_dict)
                    count = len(observations)
                    total = sum(observations)
                    lines.append(f"{name}_count{{{label_str}}} {count}")
                    lines.append(f"{name}_sum{{{label_str}}} {total:.6f}")
                    sorted_obs = sorted(observations)
                    for bucket in self._histogram_buckets:
                        le_count = sum(1 for v in sorted_obs if v <= bucket)
                        bucket_name = f'{name}_bucket{{{label_str},le="{bucket}"}}'
                        lines.append(f"{bucket_name} {le_count}")
                    bucket_name = f'{name}_bucket{{{label_str},le="+Inf"}}'
                    lines.append(f"{bucket_name} {len(observations)}")

        return "\n".join(lines) + "\n"

    def snapshot(self) -> list[MetricSnapshot]:
        snapshots: list[MetricSnapshot] = []
        with self._lock:
            for name, data in self._counters.items():
                for label_key, value in data.items():
                    snapshots.append(
                        MetricSnapshot(
                            name=name,
                            type=MetricType.COUNTER,
                            value=value,
                            labels=dict(label_key),
                        )
                    )
            for name, value in self._gauges.items():
                snapshots.append(
                    MetricSnapshot(
                        name=name,
                        type=MetricType.GAUGE,
                        value=value,
                        labels={},
                    )
                )
            for name, data in self._histograms.items():
                for label_key, observations in data.items():
                    snapshots.append(
                        MetricSnapshot(
                            name=f"{name}_count",
                            type=MetricType.COUNTER,
                            value=float(len(observations)),
                            labels=dict(label_key),
                        )
                    )
                    snapshots.append(
                        MetricSnapshot(
                            name=f"{name}_sum",
                            type=MetricType.COUNTER,
                            value=sum(observations),
                            labels=dict(label_key),
                        )
                    )
        return snapshots

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()

    @staticmethod
    def _format_labels(labels: dict[str, str]) -> str:
        return ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))


class _TimingContext:
    def __init__(self, registry: MetricsRegistry, name: str, labels: dict[str, str] | None = None) -> None:
        self._reg = registry
        self._name = name
        self._labels = labels
        self._start: float = 0.0

    def __enter__(self) -> _TimingContext:
        self._start = time.monotonic()
        return self

    def __exit__(self, *args: Any) -> None:
        elapsed = time.monotonic() - self._start
        self._reg.observe(self._name, elapsed, self._labels)

    async def __aenter__(self) -> _TimingContext:
        self._start = time.monotonic()
        return self

    async def __aexit__(self, *args: Any) -> None:
        elapsed = time.monotonic() - self._start
        self._reg.observe(self._name, elapsed, self._labels)


_global_registry: MetricsRegistry | None = None


def get_registry() -> MetricsRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = MetricsRegistry()
    return _global_registry


# ── DM-201248: 事件订阅指标记录 ──────────────────────────────────────────

_metrics_events_subscribed = False


def subscribe_metrics_events() -> None:
    """订阅统一 EventBus 事件并记录指标 — DM-201248.

    当事件发生时，自动递增 counter 指标：
    - zephyr_event_f5_deadlock_total
    - zephyr_event_fle_anomaly_total
    - zephyr_event_audit_finding_total

    幂等：重复调用不会重复订阅。
    安全：handler 永不抛异常。
    """
    global _metrics_events_subscribed
    if _metrics_events_subscribed:
        return
    _metrics_events_subscribed = True

    try:
        from zephyr.shared.events.event_bus import bus

        registry = get_registry()

        def _on_f5_deadlock(payload: Any) -> None:
            try:
                registry.inc("zephyr_event_f5_deadlock_total")
            except Exception as e:
                _logger.warning("suppressed error in metrics", exc_info=True)

        def _on_fle_anomaly(payload: Any) -> None:
            try:
                registry.inc("zephyr_event_fle_anomaly_total")
            except Exception as e:
                _logger.warning("suppressed error in metrics", exc_info=True)

        def _on_audit_finding(payload: Any) -> None:
            try:
                registry.inc("zephyr_event_audit_finding_total")
            except Exception as e:
                _logger.warning("suppressed error in metrics", exc_info=True)

        bus.subscribe("f5.deadlock_detected", _on_f5_deadlock)
        bus.subscribe("fle.anomaly", _on_fle_anomaly)
        bus.subscribe("audit.finding_created", _on_audit_finding)
    except Exception as e:
        _logger.warning("suppressed error in metrics", exc_info=True)
