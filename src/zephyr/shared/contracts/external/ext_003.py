# ==== BEGIN CODGEN:EXT-003 ====

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
ZephyrAlpha — shared/contracts/ext_003.py

EXT-003: LLM Providers / 大模型推理接口

支持降级（LLM 不可用时跳过 AI 增强，主流程不中断）；调用必须经过 AI Agent Ops 层，L02-L07 禁止直接调用 (INV-007: events crossing this boundary must carry idempotency_key)

SSoT: cross-layer-contracts.yaml → EXT-003
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    
"""

@dataclass(frozen=True)
class LLM_Providers:
    pass

# ==== END CODGEN:EXT-003 ====















