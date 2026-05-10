"""Backward-compatibility re-exports from l12_system_telemetry.

SRC-0035: telemetry/ → l12_system_telemetry/ merge.
All functionality now lives in zephyr.l12_system_telemetry.
This module remains as a thin compatibility shim.
"""

# Re-export from l12_system_telemetry for backward compatibility
from zephyr.l12_system_telemetry import (
    AIBehaviorEvent,
    AlertLevel,
    AlertSubsystem,
    ContractMetricsCollector,
    DriftAlert,
    ErrorContext,
    HealthSubsystem,
    ProfileSubsystem,
    SchemaSubsystem,
    SlaRecord,
    Span,
    SpanEvent,
    Telemetry,
    TraceContext,
    TraceSampler,
    emit_ai_behavior_event,
    get_contract_metrics,
    get_global_telemetry,
    get_trace_tree,
    list_active_spans,
    logs_flush,
    next_archive_batch_id,
    noop_span,
    validate_error_context,
)
from zephyr.l12_system_telemetry.health_aggregator import (
    AnnualHealthReport,
    HealthAggregator,
    SystemHealthSnapshot,
)

# Also re-export from migrated health/watchdog modules
from zephyr.l12_system_telemetry.health_probes import (
    SPECIAL_RULES,
    SYSTEMS,
    HealthProbeManager,
    HealthzProbe,
    LivenessProbe,
    ProbeStatus,
    ReadinessProbe,
)
from zephyr.l12_system_telemetry.watchdog import Watchdog, WatchdogHeartbeat

__all__ = [
    "ContractMetricsCollector",
    "DriftAlert",
    "SlaRecord",
    "get_contract_metrics",
    "Telemetry",
    "get_global_telemetry",
    "HealthProbeManager",
    "SYSTEMS",
    "ProbeStatus",
    "HealthAggregator",
    "Watchdog",
]
