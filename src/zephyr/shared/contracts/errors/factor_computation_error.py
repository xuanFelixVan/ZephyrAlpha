# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.errors.factor_computation_error
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.core.trace_context
# [CONSUMERS] factor.factor_base
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_factor_computation_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CTR-ERR-002: FactorComputationError / 因子计算失败错误

D_FACTOR 因子计算过程中遇到无法处理的异常时抛出的错误。

SSoT: cross_layer_contracts.yaml -> CTR-ERR-002
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 D_FACTOR 中的因子 compute() 方法遇到不可恢复的错误时，MUST 抛出 FactorComputationError。 常见 failure_reason：input_missing（缺少所需行情）、division_by_zero（除零）、window_insufficient（历史窗口不足）、 memory_exceeded（内存超限）、invalid_parameter（参数非法）。 不要吞掉错误返回一个 is_valid=False 的 FactorSignal——后者用于逻辑判断（如低置信度），前者用于系统级故障。
"""

# ==== BEGIN CODGEN:CTR-ERR-002 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.errors.factor_computation_error
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
ZephyrAlpha — shared/contracts/factor_computation_error.py

CTR-ERR-002: FactorComputationError / 因子计算失败错误

D_FACTOR 因子计算过程中遇到无法处理的异常时抛出的错误。

SSoT: cross_layer_contracts.yaml -> CTR-ERR-002
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 D_FACTOR 中的因子 compute() 方法遇到不可恢复的错误时，MUST 抛出 FactorComputationError。 常见 failure_reason：input_missing（缺少所需行情）、division_by_zero（除零）、window_insufficient（历史窗口不足）、 memory_exceeded（内存超限）、invalid_parameter（参数非法）。 不要吞掉错误返回一个 is_valid=False 的 FactorSignal——后者用于逻辑判断（如低置信度），前者用于系统级故障。
"""

@dataclass(frozen=True)
class FactorComputationError:
    error_id: str
    factor_id: str
    failure_reason: str
    idempotency_key: str
    recovery_hint: str
    symbol: str
    detail: Optional[str] = None
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-ERR-002 ====









