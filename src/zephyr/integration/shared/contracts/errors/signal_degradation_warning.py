# [BLUEPRINT] MOD-INTEGRATION
# [MODULE] zephyr.integration.shared.contracts.errors.signal_degradation_warning
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.contracts.core.trace_context
# [CONSUMERS] zephyr.integration.shared.contracts.errors.__init__; tests.test_signal_generation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# ==== BEGIN CODGEN:CTR-ERR-003 ====
from dataclasses import dataclass, field

from zephyr.shared.contracts.core.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
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
    当 D_SIGNAL 信号合成引擎检测到以下情况时，MUST 发布 SignalDegradationWarning： - confidence_below_threshold：合成后的信号置信度低于阈值 - regime_change_detected：检测到市场状态切换（如趋势->震荡） - factor_decay_triggered：某个依赖的因子 ICIR 大幅下降 这不是错误——信号仍然产出，但 D_RISK/D_PORTFOLIO_CORE 应对此做降级处理（如减半仓位）。
"""


@dataclass(frozen=True)
class SignalDegradationWarning:
    degradation_level: str
    idempotency_key: str
    idempotency_key: str
    idempotency_key: str
    reason: str
    suggested_action: str
    warning_id: str
    affected_factor_ids: list[str] = field(default_factory=list)
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-ERR-003 ====
