# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.contract_metrics
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.drift_detection.contract_drift_detector
# [CONSUMERS] zephyr.security.access_control
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] non-invasive trace-context-based measurement; statistical drift detection window; SSoT: cross_layer_contracts.yaml
# [MODIFY-GUARD] schema.py; facade.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError; RuntimeError
# [TESTS] tests/system-telemetry/test_contract_metrics.py
# [A_module] module_id=MOD-INF_contract_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ZephyrAlpha — system-telemetry/contract_metrics.py

跨层契约 SLA 测量管道 + 契约漂移检测框架 —— 遥测 预留接口。

当前状态: 框架定义（Framework-Ready）。实际测量在层实现（D_DATA~D_REPORTING 落盘后）启动。

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

SSoT: cross_layer_contracts.yaml → CTR-SLA-001~006
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime

_logger = logging.getLogger("zephyr.data.telemetry.contract_metrics")

# 5.137.2 修复：SLO 通过率阈值魔数提取为命名常量
_SLA_PASS_RATE_THRESHOLD = 95
_SLA_BUFFER_SIZE = 100


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
    _MAX_SLA_BUFFER = 1000
    _MAX_DRIFT_BUFFER = 500

    def __init__(self) -> None:
        self._enabled: bool = True
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
        if len(self._sla_buffer) > self._MAX_SLA_BUFFER:
            self._sla_buffer = self._sla_buffer[-self._MAX_SLA_BUFFER :]
        if not passed:
            _logger.warning(
                "[SLA] %s 超限: %d us > %d us (trace=%s)",
                contract_id,
                latency_us,
                sla_p99_us,
                trace_id[:8],
            )

        if len(self._sla_buffer) >= _SLA_BUFFER_SIZE:
            pass_count = sum(1 for r in self._sla_buffer[-_SLA_BUFFER_SIZE:] if r.passed)
            if pass_count < _SLA_PASS_RATE_THRESHOLD:
                _logger.warning(
                    "[SLA] %s 最近 %d 次中通过率=%d%% (<%d%%)",
                    contract_id,
                    _SLA_BUFFER_SIZE,
                    pass_count,
                    _SLA_PASS_RATE_THRESHOLD,
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
        from zephyr.governance.drift_detection.contract_drift_detector import detect_contract_drift as _detect

        return _detect(
            contract_id=contract_id,
            field_name=field_name,
            current_value=current_value,
            baseline_median=baseline_median,
            baseline_std=baseline_std,
            field_baselines=self._field_baselines,
            drift_buffer=self._drift_buffer,
        )

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


CT_TEL_SLA: dict[str, dict] = {
    "CT-TEL-001": {
        "name": "TelemetryMetrics",
        "sla_p99_us": 1_000_000,
        "description": "指标采集延迟<1s",
        "physical_path": "src/zephyr/infra_ops/observability/contract_metrics.py",
    },
    "CT-TEL-002": {
        "name": "TelemetryLogs",
        "sla_p99_us": 5_000_000,
        "description": "日志持久化延迟<5s",
        "physical_path": "src/zephyr/system-telemetry/logs/structured_sink.py",
    },
    "CT-TEL-003": {
        "name": "TelemetryTraces",
        "sla_p99_us": 2_000_000,
        "description": "链路追踪采样率可配置",
        "physical_path": "src/zephyr/infra_ops/observability/span_stub.py",
    },
    "CT-TEL-004": {
        "name": "TelemetryHealth",
        "sla_p99_us": 30_000_000,
        "description": "健康检查心跳间隔30s",
        "physical_path": "src/zephyr/infra_ops/observability/health_probes.py",
    },
}


def measure_ct_tel_sla(
    contract_id: str,
    trace_id: str,
    latency_us: int,
    start_span_id: str = "",
    end_span_id: str = "",
) -> SlaRecord | None:
    if contract_id not in CT_TEL_SLA:
        _logger.warning("[CT-TEL] unknown contract_id: %s", contract_id)
        return None
    sla_p99 = CT_TEL_SLA[contract_id]["sla_p99_us"]
    return get_contract_metrics().measure_sla(
        contract_id=contract_id,
        trace_id=trace_id,
        latency_us=latency_us,
        sla_p99_us=sla_p99,
        start_span_id=start_span_id,
        end_span_id=end_span_id,
    )


def get_ct_tel_stats() -> dict:
    collector = get_contract_metrics()
    stats = collector.get_stats()
    return {
        **stats,
        "ct_tel_sla_definitions": list(CT_TEL_SLA.keys()),
    }
