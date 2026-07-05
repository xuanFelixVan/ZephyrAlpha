# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.backpressure.throttle
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
# [A_module] module_id=MOD-SHR_throttle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Import from shared-internal _types.py — eliminates circular import to infrastructure


__all__ = ["BackpressureThrottle"]

# ==== BEGIN CODGEN:CTR-BP-002 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.backpressure.throttle
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
ZephyrAlpha — shared/contracts/throttle.py

CTR-BP-002: BackpressureThrottle / 背压降速信号

下游处理压力较大但不至于暂停时，向上游发出降速信号。上游将下发速率降至指定值。

SSoT: cross_layer_contracts.yaml -> CTR-BP-002
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    THROTTLE 比 PAUSE 轻：不是完全暂停，而是降到每秒 max_rate_per_sec 条。 典型的场景是下游队列开始堆积但还没满——先降速观察，如果仍然堆积再升级为 PAUSE。
"""

@dataclass(frozen=True)
class BackpressureThrottle:
    idempotency_key: str
    max_rate_per_sec: int
    reason: str
    signal_id: str
    symbol: str
    action: str = "THROTTLE"
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-BP-002 ====








