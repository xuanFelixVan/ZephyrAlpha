# [BLUEPRINT] MOD-INFRA_RUNTIME
# [MODULE] zephyr.infrastructure.observability.health_probes
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.observability.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# ==== BEGIN CODGEN:CT-TEL-004 ====
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/health_probes.py

CT-TEL-004: TelemetryHealth / 遥测健康检查

L12 → L01/L06 遥测健康检查契约。Liveness/Readiness/Healthz 三级探针，心跳间隔30s。

SSoT: cross_layer_contracts.yaml -> CT-TEL-004
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass
class TelemetryHealth:
    heartbeat_interval_s: int
    last_heartbeat: datetime
    module_id: str
    probe_type: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"


# ==== END CODGEN:CT-TEL-004 ====
