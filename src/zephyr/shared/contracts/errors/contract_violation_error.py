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
ZephyrAlpha — shared/contracts/contract_violation_error.py

CTR-ERR-006: ContractViolationError / 契约违反错误

运行时跨层数据契约校验失败时抛出的通用错误。任何层的数据入站/出站校验均可抛出。

SSoT: cross-layer-contracts.yaml → CTR-ERR-006
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 ContractEnforcer 装饰器检测到数据不符合 CRT 契约定义时，MUST 抛出 ContractViolationError。 你的代码不需要手动抛出这个错误——ContractEnforcer 自动完成。 如果你收到这个错误，说明上游传递的数据格式不符合 YAML 契约定义——检查数据来源，而不是修改校验逻辑。
"""


@dataclass(frozen=True)
class ContractViolationError:
    error_id: str
    contract_id: str
    violation_type: str
    detail: str
    schema_version: str = "1.0"
    field_name: Optional[str] = None
    expected_type: Optional[str] = None
    actual_type: Optional[str] = None
    trace_context: Optional[TraceContext] = None
