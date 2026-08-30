# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.contract_metrics
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.gov_drift.contract_drift_detector
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
# [A_module] module_id=MOD-INF-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
- 集成点：ContractEnforcer 违规 -> 本模块记录 -> Grafana dashboard 展示

SSoT: cross_layer_contracts.yaml -> CTR-SLA-001~006

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: contract_id 参数
#   fields: 参数 contract_id，类型注解 str
#   code: contract_metrics.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: trace_id 参数
#   fields: 参数 trace_id，类型注解 str
#   code: contract_metrics.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: latency_us 参数
#   fields: 参数 latency_us，类型注解 int
#   code: contract_metrics.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: start_span_id 参数
#   fields: 参数 start_span_id，类型注解 str
#   code: contract_metrics.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ContractMetricsCollector
#   name_en: ContractMetricsCollector
#   intro: class ContractMetricsCollector 源码 L147-L276
#   desc: 公共方法（定义序）: sla_buffer, enabled, violation_counts, field_baselines, enable, disable, measure_sla, detect_contr…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_contract_metrics
#   name_en: get_contract_metrics
#   intro: get_contract_metrics() 源码 L283-L287
#   desc: 源码 L283-L287
#   inputs: 无参数
#   outputs: ContractMetricsCollector
# - id: A3
#   name_zh: ③ measure_ct_tel_sla
#   name_en: measure_ct_tel_sla
#   intro: measure_ct_tel_sla(contract_id, trace_id, latency_us, start…
#   desc: 源码 L318-L336
#   inputs: contract_id trace_id latency_us start_span_id end_span_id
#   outputs: SlaRecord | None
# - id: A4
#   name_zh: ④ get_ct_tel_stats
#   name_en: get_ct_tel_stats
#   intro: get_ct_tel_stats() 源码 L339-L345
#   desc: 源码 L339-L345
#   inputs: 无参数
#   outputs: dict
#   （注：A4 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ContractMetricsCollector
#   name_en: ContractMetricsCollector
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.security.access_control
# - id: O2
#   name_zh: SlaRecord | None
#   name_en: SlaRecord | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.security.access_control
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
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

    @property
    def sla_buffer(self) -> list[SlaRecord]:
        """只读：sla_buffer（Stage 4 公共化）。"""
        return self._sla_buffer

    @property
    def enabled(self) -> bool:
        """只读：enabled（Stage 4 公共化）。"""
        return self._enabled

    @property
    def violation_counts(self) -> dict[str, int]:
        """只读：violation_counts（Stage 4 公共化）。"""
        return self._violation_counts

    @violation_counts.setter
    def violation_counts(self, value):
        """写入：violation_counts（Stage 4 公共化）。"""
        self._violation_counts = value

    @property
    def field_baselines(self) -> dict[str, dict[str, float]]:
        """只读：field_baselines（Stage 4 公共化）。"""
        return self._field_baselines

    @field_baselines.setter
    def field_baselines(self, value):
        """写入：field_baselines（Stage 4 公共化）。"""
        self._field_baselines = value

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
        from zephyr.gov_drift.contract_drift_detector import detect_contract_drift as _detect

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
collector = _collector  # public alias（Stage 4 公共化）


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
