from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime, timezone
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/compliance_rule.py

CTR-P1-012: ComplianceRule / 合规规则

L10 → 合规规则定义契约。包含规则注册、评估接口和规则元数据。

SSoT: cross-layer-contracts.yaml → CTR-P1-012
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class ComplianceRule:
    rule_id: str
    rule_name: str
    rule_type: str
    jurisdiction: str
    description: str
    severity: str
    enforcement_action: str
    rule_logic: str
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    schema_version: str = "1.0"
