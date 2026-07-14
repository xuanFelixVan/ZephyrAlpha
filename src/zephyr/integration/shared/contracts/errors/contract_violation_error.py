# [BLUEPRINT] MOD-INTEGRATION | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared.contracts.errors.contract_violation_error
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.contracts.core.trace_context
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_contract_violation_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:CTR-ERR-006 ====
from dataclasses import dataclass

from zephyr.shared.contracts.core.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/contract_violation_error.py

CTR-ERR-006: ContractViolationError / 契约违反错误

运行时跨层数据契约校验失败时抛出的通用错误。任何层的数据入站/出站校验均可抛出。

SSoT: cross_layer_contracts.yaml -> CTR-ERR-006
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 ContractEnforcer 装饰器检测到数据不符合 CRT 契约定义时，MUST 抛出 ContractViolationError。 你的代码不需要手动抛出这个错误——ContractEnforcer 自动完成。 如果你收到这个错误，说明上游传递的数据格式不符合 YAML 契约定义——检查数据来源，而不是修改校验逻辑。
"""


@dataclass(frozen=True)
class ContractViolationError:
    contract_id: str
    detail: str
    error_id: str
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    violation_type: str
    actual_type: str | None = None
    expected_type: str | None = None
    field_name: str | None = None
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-ERR-006 ====
