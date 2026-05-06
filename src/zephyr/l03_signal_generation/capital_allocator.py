# ---
# layer: l03_signal_generation
# category: allocation
# status: active
# created: "2026-05-05"
# ---

"""L03 — Capital Allocator（兼容导出）

``CapitalAllocatorBase`` 真源在 ``aggregator_base.py``（与 ``SignalAggregatorBase`` / ``DegradationMonitorBase`` 同文件）。
``CapitalAllocationResult`` 真源在 ``zephyr.shared.contracts.capital_allocation_result``（CTR-P1-003）。

本模块仅作向后兼容 re-export，禁止在此重复定义契约类型或 ABC。
"""
from __future__ import annotations

from zephyr.l03_signal_generation.aggregator_base import CapitalAllocatorBase
from zephyr.shared.contracts.capital_allocation_result import CapitalAllocationResult

__all__ = ["CapitalAllocationResult", "CapitalAllocatorBase"]
