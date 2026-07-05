# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.backpressure.resume
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.backpressure._types
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_resume | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Import from shared-internal _types.py — eliminates circular import to infrastructure


__all__ = ["BackpressureResume"]

# ==== BEGIN CODGEN:CTR-BP-003 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.backpressure.resume
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
from dataclasses import dataclass, field

from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/resume.py

CTR-BP-003: BackpressureResume / 背压恢复信号

下游处理能力恢复后，向上游发出恢复信号。上游恢复正常下发速率。

SSoT: cross_layer_contracts.yaml -> CTR-BP-003
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当之前的 PAUSE/THROTTLE 条件解除后（如队列清空、GC 完成），MUST 发送 RESUME 恢复信号。 不要在 RESUME 后立即取消——先观察一个周期确认稳定。
"""

@dataclass(frozen=True)
class BackpressureResume:
    idempotency_key: str
    reason: str
    signal_id: str
    symbol: str
    action: str = "RESUME"
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-BP-003 ====








