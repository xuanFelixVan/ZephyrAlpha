"""l12_system_telemetry — 系统遥测模块（MOD-INF-015 v0.9.0）.

9 子系统: metrics | logs | traces | ai_behavior | health | profiles | alerts | schema | archive

一行接入:
    from zephyr.l12_system_telemetry import Telemetry
    telemetry = Telemetry("my_module", test_mode=False)
"""

from zephyr.l12_system_telemetry.ai_behavior import (
    AIBehaviorEvent,
    ErrorContext,
    emit_ai_behavior_event,
    validate_error_context,
)
from zephyr.l12_system_telemetry.alerts import AlertLevel, AlertSubsystem
from zephyr.l12_system_telemetry.archive import next_archive_batch_id
from zephyr.l12_system_telemetry.auto_bootstrap import get_global_telemetry
from zephyr.l12_system_telemetry.contract_metrics import (
    ContractMetricsCollector,
    DriftAlert,
    SlaRecord,
    get_contract_metrics,
)
from zephyr.l12_system_telemetry.facade import Telemetry
from zephyr.l12_system_telemetry.health import HealthSubsystem
from zephyr.l12_system_telemetry.logs import flush as logs_flush
from zephyr.l12_system_telemetry.profiles import ProfileSubsystem
from zephyr.l12_system_telemetry.schema import SchemaSubsystem
from zephyr.l12_system_telemetry.traces import (
    Span,
    SpanEvent,
    TraceContext,
    TraceSampler,
    get_trace_tree,
    list_active_spans,
    noop_span,
)

__all__ = [
    "Telemetry",
    "ContractMetricsCollector",
    "SlaRecord",
    "DriftAlert",
    "get_contract_metrics",
    "get_global_telemetry",
    "AlertLevel",
    "AlertSubsystem",
    "HealthSubsystem",
    "ProfileSubsystem",
    "SchemaSubsystem",
    "next_archive_batch_id",
    "noop_span",
    "TraceContext",
    "Span",
    "SpanEvent",
    "TraceSampler",
    "list_active_spans",
    "get_trace_tree",
    "AIBehaviorEvent",
    "ErrorContext",
    "emit_ai_behavior_event",
    "validate_error_context",
    "logs_flush",
    "auto_bootstrap",
    "contract_metrics",
    "facade",
    "alerts",
    "health",
    "profiles",
    "schema",
    "archive",
    "traces",
    "ai_behavior",
    "logs",
]
