# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.errors.signal_degradation_warning
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
# [A_module] module_id=MOD-SHR_signal_degradation_warning | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import importlib

_TARGET_MODULE = "zephyr.trading.trading_contracts.market.signal_degradation_warning"


def __getattr__(name):
    # dunder 属性（如 __all__）直接 raise，避免 from .xxx import * 触发循环 import
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    mod = importlib.import_module(_TARGET_MODULE)
    if hasattr(mod, name):
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# ==== BEGIN CODGEN:CTR-ERR-003 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.errors.signal_degradation_warning
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

from typing import List
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
ZephyrAlpha — shared/contracts/signal_degradation_warning.py

CTR-ERR-003: SignalDegradationWarning / 信号质量下降警告

D_SIGNAL 检测到信号质量显著下降时发出的警告。非致命，但 D_RISK/D_PORTFOLIO_CORE 应据此调低仓位或暂停交易。

SSoT: cross_layer_contracts.yaml -> CTR-ERR-003
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 D_SIGNAL 信号合成引擎检测到以下情况时，MUST 发布 SignalDegradationWarning： - confidence_below_threshold：合成后的信号置信度低于阈值 - regime_change_detected：检测到市场状态切换（如趋势→震荡） - factor_decay_triggered：某个依赖的因子 ICIR 大幅下降 这不是错误——信号仍然产出，但 D_RISK/D_PORTFOLIO_CORE 应对此做降级处理（如减半仓位）。
"""

@dataclass(frozen=True)
class SignalDegradationWarning:
    degradation_level: str
    idempotency_key: str
    reason: str
    suggested_action: str
    warning_id: str
    affected_factor_ids: List[str] = field(default_factory=list)
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-ERR-003 ====








