# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.errors.risk_limit_violation_error
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.errors.__init__
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
# [A_module] module_id=MOD-SHR_risk_limit_violation_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import importlib

_TARGET_MODULE = "zephyr.trading.trading_contracts.risk.risk_limit_violation_error"


def __getattr__(name):
    # dunder 属性（如 __all__）直接 raise，避免 from .xxx import * 触发循环 import
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    mod = importlib.import_module(_TARGET_MODULE)
    if hasattr(mod, name):
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# ==== BEGIN CODGEN:CTR-ERR-004 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.errors.risk_limit_violation_error
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
ZephyrAlpha — shared/contracts/risk_limit_violation_error.py

CTR-ERR-004: RiskLimitViolationError / 风险限额突破错误

D_RISK 检测到当前或计划操作将突破风险限额时抛出的硬错误。D_PORTFOLIO_CORE/D_EXECUTION_CORE MUST 据此阻止订单生成和执行。

SSoT: cross_layer_contracts.yaml -> CTR-ERR-004
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 D_RISK 风控系统检测到任何风险约束被突破时，MUST 抛出 RiskLimitViolationError。 这是一个 HALT 级别的错误——下游（D_PORTFOLIO_CORE/D_EXECUTION_CORE）MUST 拒绝继续处理并停止当前调仓周期。 violated_constraint 精确指出是哪条规则被突破（position_limit / leverage_limit / var_breach / drawdown_trigger / sector_concentration）。 不要降级为 WARNING——如果这是代码逻辑导致的，降级等于资金安全风险。
"""

@dataclass(frozen=True)
class RiskLimitViolationError:
    actual_value: float
    error_id: str
    idempotency_key: str
    limit_value: float
    portfolio_id: str
    recovery_hint: str
    violated_constraint: str
    violation_detail: str
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-ERR-004 ====








