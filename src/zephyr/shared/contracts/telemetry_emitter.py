from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/telemetry_emitter.py

CTR-P1-013: TelemetryEmitter / 遥测发射器

L12 → 全系统遥测发射器契约。提供结构化指标、日志、追踪的发射接口。

SSoT: cross-layer-contracts.yaml → CTR-P1-013
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""

@dataclass(frozen=True)
class TelemetryEmitter:
    emitter_id: str
    emitter_type: str
    metric_name: str
    metric_value: float
    metric_type: str
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime
    source_module: str
    correlation_id: str
    schema_version: str = "1.0"
    severity: str
    message: str
    span_id: str
    trace_id: str
    parent_span_id: str
