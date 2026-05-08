"""
ZephyrAlpha — l12_system_telemetry/contract_metrics.py

跨层契约 SLA 测量管道 + 契约漂移检测框架 —— L12 预留接口。

当前状态: 框架定义（Framework-Ready）。实际测量在层实现（L00~L07 落盘后）启动。

提供
----
- measure_sla            — 测量跨层数据流的端到端延迟
- detect_contract_drift  — 检测运行时数据与契约定义的统计偏差
- record_contract_violation — 记录 ContractEnforcer 的违规事件

设计原则
--------
- 非侵入：通过 TraceContext（CTR-TRACE-001）的 span 时间戳测量延迟
- 统计式漂移检测：比较近期窗口与历史基准（不变式是架构适应度函数的运行时版本）
- 集成点：ContractEnforcer 违规 → 本模块记录 → Grafana dashboard 展示

SSoT: cross-layer-contracts.yaml → CTR-SLA-001~006
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime

_logger = logging.getLogger("zephyr.telemetry.contract_metrics")


@dataclass
class SlaRecord:
    contract_id: str
    trace_id: str
    latency_us: int
    start_span_id: str
    end_span_id: str
    passed: bool
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class DriftAlert:
    contract_id: str
    field_name: str
    statistic: str
    current_value: float
    baseline_value: float
    deviation_pct: float
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ContractMetricsCollector:
    """L12 Telemetry: 契约 SLA + 漂移检测采集器。

    在 L12 落盘前，此 Collector 作为框架存在——提供标准接口供未来
    各层调用。当前为 no-op 模式（记录日志，不持久化）。
    """

    def __init__(self) -> None:
        self._enabled: bool = False
        self._sla_buffer: list[SlaRecord] = []
        self._drift_buffer: list[DriftAlert] = []
        self._violation_counts: dict[str, int] = defaultdict(int)
        self._field_baselines: dict[str, dict[str, float]] = defaultdict(dict)

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def measure_sla(
        self,
        contract_id: str,
        trace_id: str,
        latency_us: int,
        sla_p99_us: int,
        start_span_id: str = "",
        end_span_id: str = "",
    ) -> SlaRecord:
        passed = latency_us <= sla_p99_us
        record = SlaRecord(
            contract_id=contract_id,
            trace_id=trace_id,
            latency_us=latency_us,
            start_span_id=start_span_id,
            end_span_id=end_span_id,
            passed=passed,
        )

        self._sla_buffer.append(record)
        if not passed:
            _logger.warning(
                "[SLA] %s 超限: %d us > %d us (trace=%s)",
                contract_id,
                latency_us,
                sla_p99_us,
                trace_id[:8],
            )

        if len(self._sla_buffer) >= 100:
            pass_count = sum(1 for r in self._sla_buffer[-100:] if r.passed)
            if pass_count < 95:
                _logger.warning(
                    "[SLA] %s 最近 100 次中通过率=%d%% (<95%%)",
                    contract_id,
                    pass_count,
                )

        return record

    def detect_contract_drift(
        self,
        contract_id: str,
        field_name: str,
        current_value: float,
        baseline_median: float | None = None,
        baseline_std: float | None = None,
    ) -> DriftAlert | None:
        if baseline_median is None or baseline_std is None:
            key = f"{contract_id}:{field_name}"
            if key in self._field_baselines:
                baseline_median = self._field_baselines[key].get("median", 0.0)
                baseline_std = self._field_baselines[key].get("std", 1.0)
            else:
                return None

        if baseline_std == 0:
            baseline_std = 0.001

        deviation = abs(current_value - baseline_median) / baseline_std

        if deviation > 5.0:
            deviation_pct = abs(current_value - baseline_median) / max(abs(baseline_median), 0.001) * 100
            alert = DriftAlert(
                contract_id=contract_id,
                field_name=field_name,
                statistic="z_score",
                current_value=current_value,
                baseline_value=baseline_median,
                deviation_pct=deviation_pct,
            )
            self._drift_buffer.append(alert)
            _logger.warning(
                "[Drift] %s.%s z-score=%.1f — 可能发生契约漂移",
                contract_id,
                field_name,
                deviation,
            )
            return alert

        return None

    def record_violation(self, contract_id: str) -> None:
        self._violation_counts[contract_id] += 1

        if self._violation_counts[contract_id] > 10:
            _logger.error(
                "[ContractMetrics] %s 违规次数=%d — 检查上游数据源",
                contract_id,
                self._violation_counts[contract_id],
            )

    def get_stats(self) -> dict:
        recent_sla = self._sla_buffer[-100:] if self._sla_buffer else []
        recent_passed = sum(1 for r in recent_sla if r.passed)
        return {
            "sla_p99_pass_rate_100": recent_passed / max(len(recent_sla), 1) * 100,
            "total_violations": sum(self._violation_counts.values()),
            "active_drift_alerts": len(self._drift_buffer),
            "tracked_contracts": len(self._field_baselines),
        }


_collector: ContractMetricsCollector | None = None


def get_contract_metrics() -> ContractMetricsCollector:
    global _collector
    if _collector is None:
        _collector = ContractMetricsCollector()
    return _collector
