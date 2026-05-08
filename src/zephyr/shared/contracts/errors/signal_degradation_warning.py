"""
CTR-ERR-003: SignalDegradationWarning / 信号质量下降警告

L03 检测到信号质量显著下降时发出的警告。非致命，但 L04/L05 应据此调低仓位或暂停交易。

SSoT: cross-layer-contracts.yaml → CTR-ERR-003
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 L03 信号合成引擎检测到以下情况时，MUST 发布 SignalDegradationWarning： - confidence_below_threshold：合成后的信号置信度低于阈值 - regime_change_detected：检测到市场状态切换（如趋势→震荡） - factor_decay_triggered：某个依赖的因子 ICIR 大幅下降 这不是错误——信号仍然产出，但 L04/L05 应对此做降级处理（如减半仓位）。
"""


# ==== BEGIN CODGEN:CTR-ERR-003 ====
from dataclasses import dataclass, field

from typing import List
from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/signal_degradation_warning.py

CTR-ERR-003: SignalDegradationWarning / 信号质量下降警告

L03 检测到信号质量显著下降时发出的警告。非致命，但 L04/L05 应据此调低仓位或暂停交易。

SSoT: cross-layer-contracts.yaml -> CTR-ERR-003
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 L03 信号合成引擎检测到以下情况时，MUST 发布 SignalDegradationWarning： - confidence_below_threshold：合成后的信号置信度低于阈值 - regime_change_detected：检测到市场状态切换（如趋势→震荡） - factor_decay_triggered：某个依赖的因子 ICIR 大幅下降 这不是错误——信号仍然产出，但 L04/L05 应对此做降级处理（如减半仓位）。
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





































