# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.experiment.experiment_result
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.core.trace_context
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_experiment_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

# ==== BEGIN CODGEN:CTR-P1-014 ====
from dataclasses import dataclass, field
from datetime import datetime

from zephyr.shared.contracts.core.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/experiment_result.py

CTR-P1-014: ExperimentResult / 实验结论

实验 -> D_RESEARCH/D_ML_TRAIN 实验结论契约。Scout Agent 完成对照实验后产出的结构化结论。

SSoT: cross_layer_contracts.yaml -> CTR-P1-014
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 实验 的 Scout Agent 完成一个实验周期后，MUST 产出 ExperimentResult。 每个 ExperimentResult 代表一次完整的对照实验结论——包含实验设计、执行过程、结果指标和可操作建议。 confidence 用于衡量结论的统计可靠性：>0.9 = 高度可信，0.7-0.9 = 中等，<0.7 = 不发布。 D_RESEARCH 研究创新层读取历史实验结论指导研究方向。D_ML_TRAIN ML Platform 读取实验结论调整模型策略。
"""


@dataclass(frozen=True)
class ExperimentResult:
    conclusion: str
    confidence: float
    end_timestamp: datetime
    experiment_id: str
    experiment_name: str
    experiment_type: str
    hypothesis: str
    idempotency_key: str
    p_value: float
    sample_size: int
    start_timestamp: datetime
    variant_a_description: str
    variant_b_description: str
    variant_b_improvement: float
    actionable_suggestions: list[str] = field(default_factory=list)
    affected_factor_ids: list[str] = field(default_factory=list)
    affected_strategy_ids: list[str] = field(default_factory=list)
    archived_to_kms: bool = False
    metrics: dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-P1-014 ====
