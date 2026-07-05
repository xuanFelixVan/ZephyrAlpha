# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.backpressure.pause
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
# [A_module] module_id=MOD-SHR_pause | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Import from shared-internal _types.py — eliminates circular import to infrastructure


__all__ = ["BackpressurePause"]

# ==== BEGIN CODGEN:CTR-BP-001 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.backpressure.pause
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
ZephyrAlpha — shared/contracts/pause.py

CTR-BP-001: BackpressurePause / 背压暂停信号

下游（D_FACTOR/D_SIGNAL）处理能力不足时，向上游（D_DATA）发出暂停信号。D_DATA 暂停该标的的数据下发。

SSoT: cross_layer_contracts.yaml -> CTR-BP-001
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    如果下游处理速度跟不上上游产生速度，你可以通过 emit PAUSE 背压信号来告诉上游暂停。 PAUSE 会暂停指定标的的数据下发 duration_ms 毫秒，到期后自动恢复。 不要静默丢弃数据——上游不知道下游爆了，只会继续发，最终内存溢出。
"""

@dataclass(frozen=True)
class BackpressurePause:
    duration_ms: int
    idempotency_key: str
    reason: str
    signal_id: str
    symbol: str
    action: str = "PAUSE"
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-BP-001 ====








