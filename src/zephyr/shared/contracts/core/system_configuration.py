# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.system_configuration
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_system_configuration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

# ==== BEGIN CODGEN:CTR-P1-010 ====
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/system_configuration.py

CTR-P1-010: SystemConfiguration / 系统配置

基础设施 → 全系统配置契约。基于dataclass的配置加载API，支持环境变量覆盖和热重载。

SSoT: cross_layer_contracts.yaml -> CTR-P1-010
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------

"""


@dataclass(frozen=True)
class SystemConfiguration:
    config_id: str
    config_type: str
    created_at: datetime
    environment: str
    idempotency_key: str
    is_active: bool
    updated_at: datetime
    version: str
    config_data: dict[str, Any] = field(default_factory=dict)
    exceptions: list[str] = field(default_factory=list)
    max_retries: int = 3
    retry_policy: str = "linear"
    schema_version: str = "1.0"
    timeout_ms: int = 1000


# ==== END CODGEN:CTR-P1-010 ====
