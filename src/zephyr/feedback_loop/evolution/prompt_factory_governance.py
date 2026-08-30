# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution.prompt_factory_governance
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Prompt Factory Governance — v0.16.0 R224

Blindspot: Prompt templates proliferate without version control; no AB testing of prompt variants.
Risk: R224 — Unversioned prompt changes degrade diagnosis quality; no controlled experiment.

Mitigation: Prompt template factory with versioning, audit trail, and A/B test support.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: prompt_factory_governance.py
# 层: 算法
# - id: A1
#   name_zh: ① PromptFactoryGovernance
#   name_en: PromptFactoryGovernance
#   intro: class PromptFactoryGovernance 源码 L73-L94
#   desc: 公共方法（定义序）: register, latest；源码 L73-L94
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: PromptFactoryGovernance
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class PromptVariant:
    variant_id: str
    template_id: str
    version: int
    content: str
    content_hash: str
    created_at: float = field(default_factory=time.time)
    ab_group: str = "control"


@dataclass
class PromptFactoryGovernance:
    variants: dict[str, list[PromptVariant]] = field(default_factory=dict)

    def register(self, template_id: str, content: str) -> PromptVariant:
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        existing = self.variants.get(template_id, [])
        version = len(existing) + 1
        variant = PromptVariant(
            variant_id=f"{template_id}-v{version}",
            template_id=template_id,
            version=version,
            content=content,
            content_hash=content_hash,
        )
        if template_id not in self.variants:
            self.variants[template_id] = []
        self.variants[template_id].append(variant)
        return variant

    def latest(self, template_id: str) -> PromptVariant | None:
        variants = self.variants.get(template_id, [])
        return variants[-1] if variants else None
