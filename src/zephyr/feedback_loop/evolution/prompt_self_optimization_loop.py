# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution.prompt_self_optimization_loop
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
R502: PromptSelfOptimizationLoop
DSPy/GEPA封闭自提示进化闭环 — 观察效果->LLM反思->生成变体->A/B测试->采纳

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: prompt_self_optimization_loop.py
# 层: 算法
# - id: A1
#   name_zh: ① PromptSelfOptimizationLoop
#   name_en: PromptSelfOptimizationLoop
#   intro: class PromptSelfOptimizationLoop 源码 L75-L164
#   desc: 公共方法（定义序）: get_baseline_effectiveness, register_current_prompt, record_effectiveness, propose_variant, evalua…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: PromptSelfOptimizationLoop
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum


class PromptVariantStatus(str, Enum):
    CANDIDATE = "candidate"
    TESTING = "testing"
    ADOPTED = "adopted"
    REJECTED = "rejected"


@dataclass
class PromptVariant:
    variant_id: str
    content: str
    parent_hash: str
    status: PromptVariantStatus = PromptVariantStatus.CANDIDATE
    effectiveness_score: float = 0.0
    test_results: dict = field(default_factory=dict)
    created_at: float = 0.0


@dataclass
class PromptSelfOptimizationLoop:
    current_prompt_hash: str = ""

    def get_baseline_effectiveness(self) -> float:
        """公共接口：get_baseline_effectiveness（Stage 4 公共化）。"""
        return self._get_baseline_effectiveness()

    variants: dict[str, PromptVariant] = field(default_factory=dict)
    effectiveness_history: list[dict] = field(default_factory=list)
    max_history: int = 50
    improvement_threshold: float = 0.05
    cooldown_cycles: int = 20
    cycles_since_last_optimization: int = 0

    def register_current_prompt(self, content: str) -> str:
        h = hashlib.sha256(content.encode()).hexdigest()[:16]
        self.current_prompt_hash = h
        self.cycles_since_last_optimization = 0
        return h

    def record_effectiveness(self, metrics: dict) -> None:
        metrics["timestamp"] = time.time()
        self.effectiveness_history.append(metrics)
        if len(self.effectiveness_history) > self.max_history:
            self.effectiveness_history = self.effectiveness_history[-self.max_history :]
        self.cycles_since_last_optimization += 1

    def propose_variant(self, variant_content: str) -> str | None:
        if self.cycles_since_last_optimization < self.cooldown_cycles:
            return None

        variant_hash = hashlib.sha256(variant_content.encode()).hexdigest()[:12]
        variant_id = f"PV-{variant_hash}"

        if variant_id in self.variants:
            return None

        self.variants[variant_id] = PromptVariant(
            variant_id=variant_id,
            content=variant_content,
            parent_hash=self.current_prompt_hash,
            created_at=time.time(),
        )
        return variant_id

    def evaluate_variant(self, variant_id: str, test_score: float) -> dict:
        variant = self.variants.get(variant_id)
        if not variant:
            return {"error": "variant_not_found"}

        baseline = self._get_baseline_effectiveness()

        variant.effectiveness_score = test_score
        variant.test_results = {
            "score": test_score,
            "baseline": baseline,
            "improvement": test_score - baseline,
        }

        if test_score - baseline > self.improvement_threshold:
            return self._adopt_variant(variant)
        else:
            variant.status = PromptVariantStatus.REJECTED
            return {"action": "rejected", "score": test_score, "baseline": baseline}

    def _adopt_variant(self, variant: PromptVariant) -> dict:
        variant.status = PromptVariantStatus.ADOPTED
        self.current_prompt_hash = hashlib.sha256(variant.content.encode()).hexdigest()[:16]
        self.cycles_since_last_optimization = 0
        return {
            "action": "adopted",
            "new_hash": self.current_prompt_hash,
            "improvement": variant.test_results.get("improvement", 0),
        }

    def _get_baseline_effectiveness(self) -> float:
        if not self.effectiveness_history:
            return 0.5
        recent = self.effectiveness_history[-10:]
        scores = [m.get("overall_score", m.get("accuracy", 0.5)) for m in recent]
        return sum(scores) / len(scores)

    def get_optimization_status(self) -> dict:
        return {
            "total_variants": len(self.variants),
            "adopted_count": sum(1 for v in self.variants.values() if v.status is PromptVariantStatus.ADOPTED),
            "cycles_since_last": self.cycles_since_last_optimization,
            "cooldown_remaining": max(0, self.cooldown_cycles - self.cycles_since_last_optimization),
            "can_propose": self.cycles_since_last_optimization >= self.cooldown_cycles,
        }
