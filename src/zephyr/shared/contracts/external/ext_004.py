# ==== BEGIN CODGEN:EXT-004 ====

from __future__ import annotations

from dataclasses import dataclass, field
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/ext_004.py

EXT-004: Feishu / 飞书通知接口

非关键路径；发送失败不影响主流程；重试 3 次后记录日志 (INV-007: events crossing this boundary must carry idempotency_key)

SSoT: cross-layer-contracts.yaml → EXT-004
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class Feishu:
    pass

# ==== END CODGEN:EXT-004 ====















