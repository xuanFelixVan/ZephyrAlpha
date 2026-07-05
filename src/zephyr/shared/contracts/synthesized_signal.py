# ==== BEGIN CODGEN:CTR-P1-015 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.synthesized_signal
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
# [TTL] permanent
from dataclasses import dataclass, field

from datetime import datetime, timezone
from typing import Dict
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
ZephyrAlpha — shared/contracts/synthesized_signal.py

CTR-P1-015: SynthesizedSignal / 合成交易信号

D_SIGNAL → D_RISK/D_PORTFOLIO_CORE 合成交易信号契约。D_SIGNAL 信号合成引擎聚合多个 FactorSignal 后产出的综合交易信号。

SSoT: cross_layer_contracts.yaml -> CTR-P1-015
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 D_SIGNAL 信号合成引擎完成因子信号聚合后，MUST 产出 SynthesizedSignal。 每个 SynthesizedSignal 代表一个标的在一个时间截面上的综合交易判断。 signal_value 是标准化后的合成信号值（-3 到 3），正值为做多信号，负值为做空信号。 contributing_factors 记录参与合成的因子 ID 及其权重——用于归因分析。 D_RISK 风控层使用此信号做 pre-trade risk check。D_PORTFOLIO_CORE 组合构建层使用此信号做组合优化输入。 generation_latency_ms 记录信号合成耗时，用于 SLO 监控。
"""

@dataclass(frozen=True)
class SynthesizedSignal:
    as_of_timestamp: datetime
    confidence: float
    generation_latency_ms: int
    idempotency_key: str
    signal_direction: str
    signal_id: str
    signal_value: float
    symbol: str
    contributing_factors: Dict[str, float] = field(default_factory=dict)
    is_degraded: bool = False
    regime: str = ""
    schema_version: str = "1.0"
    suggested_position_pct: float = 0
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-P1-015 ====








