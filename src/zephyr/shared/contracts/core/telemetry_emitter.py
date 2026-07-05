# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.telemetry_emitter
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
# [A_module] module_id=MOD-SHR_telemetry_emitter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

# ==== BEGIN CODGEN:CTR-P1-013 ====
from dataclasses import dataclass, field
from datetime import datetime

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/telemetry_emitter.py

CTR-P1-013: TelemetryEmitter / 遥测发射器

遥测 → 全系统遥测发射器契约。提供结构化指标、日志、追踪的发射接口。

SSoT: cross_layer_contracts.yaml -> CTR-P1-013
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class TelemetryEmitter:
    correlation_id: str
    emitter_id: str
    emitter_type: str
    idempotency_key: str
    metric_name: str
    metric_type: str
    metric_value: float
    source_module: str
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)
    message: str = ""
    parent_span_id: str = ""
    schema_version: str = "1.0"
    severity: str = ""
    span_id: str = ""
    trace_id: str = ""


# ==== END CODGEN:CTR-P1-013 ====
