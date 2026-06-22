# [A_module] module_id=MOD-INT_throttle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-157 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.backpressure.throttle
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# Re-export shim — canonical location is now zephyr.integration.backpressure_types

import importlib as _il

_mod = _il.import_module("zephyr.integration.backpressure_types")
BackpressureThrottle = _mod.BackpressureThrottle

__all__ = ["BackpressureThrottle"]

# ==== BEGIN CODGEN:CTR-BP-002 ====
from dataclasses import dataclass

from zephyr.integration.shared_08.contracts.core.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
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
    idempotency_key: str
    idempotency_key: str
    max_rate_per_sec: int
    reason: str
    signal_id: str
    symbol: str
    action: str = "THROTTLE"
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-BP-002 ====
