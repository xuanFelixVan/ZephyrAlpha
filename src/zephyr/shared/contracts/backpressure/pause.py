from __future__ import annotations

from dataclasses import dataclass

from zephyr.shared.contracts.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/pause.py

CTR-BP-001: BackpressurePause / 背压暂停信号

下游（L02/L03）处理能力不足时，向上游（L00）发出暂停信号。L00 暂停该标的的数据下发。

SSoT: cross-layer-contracts.yaml → CTR-BP-001
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    如果下游处理速度跟不上上游产生速度，你可以通过 emit PAUSE 背压信号来告诉上游暂停。 PAUSE 会暂停指定标的的数据下发 duration_ms 毫秒，到期后自动恢复。 不要静默丢弃数据——上游不知道下游爆了，只会继续发，最终内存溢出。
"""

@dataclass(frozen=True)
class BackpressurePause:
    signal_id: str
    symbol: str
    duration_ms: int
    reason: str
    action: str = "PAUSE"
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None
