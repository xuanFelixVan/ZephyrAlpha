# ==== BEGIN CODGEN:CTR-P1-012 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.compliance_rule
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from dataclasses import dataclass, field

from datetime import datetime, timezone
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/compliance_rule.py

CTR-P1-012: ComplianceRule / 合规规则

D_COMPLIANCE → 合规规则定义契约。包含规则注册、评估接口和规则元数据。

SSoT: cross_layer_contracts.yaml -> CTR-P1-012
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class ComplianceRule:
    created_at: datetime
    description: str
    enforcement_action: str
    idempotency_key: str
    is_active: bool
    jurisdiction: str
    rule_id: str
    rule_logic: str
    rule_name: str
    rule_type: str
    severity: str
    updated_at: datetime
    version: str
    schema_version: str = "1.0"

# ==== END CODGEN:CTR-P1-012 ====











