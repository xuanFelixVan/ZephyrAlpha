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
ZephyrAlpha — shared/contracts/factor_computation_error.py

CTR-ERR-002: FactorComputationError / 因子计算失败错误

L02 因子计算过程中遇到无法处理的异常时抛出的错误。

SSoT: cross-layer-contracts.yaml → CTR-ERR-002
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 L02 中的因子 compute() 方法遇到不可恢复的错误时，MUST 抛出 FactorComputationError。 常见 failure_reason：input_missing（缺少所需行情）、division_by_zero（除零）、window_insufficient（历史窗口不足）、 memory_exceeded（内存超限）、invalid_parameter（参数非法）。 不要吞掉错误返回一个 is_valid=False 的 FactorSignal——后者用于逻辑判断（如低置信度），前者用于系统级故障。
"""

@dataclass(frozen=True)
class FactorComputationError:
    error_id: str
    factor_id: str
    symbol: str
    failure_reason: str
    recovery_hint: str
    schema_version: str = "1.0"
    detail: Optional[str] = None
    trace_context: Optional[TraceContext] = None
