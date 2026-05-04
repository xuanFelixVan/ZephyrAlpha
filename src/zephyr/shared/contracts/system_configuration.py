from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime, timezone
from typing import Any
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/system_configuration.py

CTR-P1-010: SystemConfiguration / 系统配置

L01 → 全系统配置契约。基于dataclass的配置加载API，支持环境变量覆盖和热重载。

SSoT: cross-layer-contracts.yaml → CTR-P1-010
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class SystemConfiguration:
    config_id: str
    config_type: str
    version: str
    environment: str
    config_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    is_active: bool
    timeout_ms: int = 1000
    retry_policy: str = "linear"
    max_retries: int = 3
    schema_version: str = "1.0"
    exceptions: List[str] = field(default_factory=list)
