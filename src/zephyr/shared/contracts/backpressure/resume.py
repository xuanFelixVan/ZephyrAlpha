# ==== BEGIN CODGEN:CTR-BP-003 ====
from dataclasses import dataclass, field

from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/resume.py

CTR-BP-003: BackpressureResume / 背压恢复信号

下游处理能力恢复后，向上游发出恢复信号。上游恢复正常下发速率。

SSoT: cross-layer-contracts.yaml -> CTR-BP-003
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





































