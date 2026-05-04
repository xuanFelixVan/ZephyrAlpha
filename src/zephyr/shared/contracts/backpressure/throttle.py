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
ZephyrAlpha — shared/contracts/throttle.py

CTR-BP-002: BackpressureThrottle / 背压降速信号

下游处理压力较大但不至于暂停时，向上游发出降速信号。上游将下发速率降至指定值。

SSoT: cross-layer-contracts.yaml → CTR-BP-002
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    THROTTLE 比 PAUSE 轻：不是完全暂停，而是降到每秒 max_rate_per_sec 条。 典型的场景是下游队列开始堆积但还没满——先降速观察，如果仍然堆积再升级为 PAUSE。
"""


@dataclass(frozen=True)
class BackpressureThrottle:
    signal_id: str
    symbol: str
    max_rate_per_sec: int
    reason: str
    action: str = "THROTTLE"
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None
