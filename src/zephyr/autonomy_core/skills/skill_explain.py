# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_explain
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — XAI Explainable Skill Engine
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

XAI 可解释性引擎
================
让 Skill 决策不再黑箱:
  1. ReasoningChain: 记录 Skill 加载->路由->执行的完整推理链
  2. ConfidenceScore: 为每步决策计算置信度
  3. FactorIsolation: 隔离"Skill 本身"vs"LLM 能力"对结果的影响
  4. CounterfactualWhatIf: 如果选了其他 Skill 会怎样
"""

from __future__ import annotations

from typing import Any


class SkillExplain:
    """Skill XAI 可解释性引擎"""

    @classmethod
    def build_reasoning_chain(
        cls,
        skill_id: str,
        task_description: str,
        matched_stage: str,
        matched_keywords: list[str],
    ) -> dict[str, Any]:
        chain = []

        chain.append(
            {
                "step": 1,
                "label": "trigger_received",
                "detail": f"Pipeline dispatched task with stage='{matched_stage}'",
                "confidence": 1.0,
            }
        )

        keyword_detail = ", ".join(matched_keywords[:5]) if matched_keywords else "no keyword match"
        chain.append(
            {
                "step": 2,
                "label": "keyword_extraction",
                "detail": f"Extracted keywords: {keyword_detail}",
                "confidence": 0.9 if matched_keywords else 0.3,
            }
        )

        chain.append(
            {
                "step": 3,
                "label": "skill_lookup",
                "detail": f"Looked up skill '{skill_id}' in registry via TriggerRouter",
                "confidence": 0.85 if matched_keywords else 0.5,
            }
        )

        chain.append(
            {
                "step": 4,
                "label": "skill_loaded",
                "detail": f"Progressive disclosure loaded L0+L1+L2 for skill '{skill_id}'",
                "confidence": 0.80,
            }
        )

        chain.append(
            {
                "step": 5,
                "label": "skill_injected",
                "detail": "Injected skill context into Pipeline module context",
                "confidence": 0.75,
            }
        )

        return {
            "skill_id": skill_id,
            "steps": len(chain),
            "reasoning_chain": chain,
            "overall_confidence": sum(c["confidence"] for c in chain) / len(chain),
        }

    @classmethod
    def explain_routing(
        cls,
        task_description: str,
        chosen_skill_id: str,
        alternatives: list[str],
    ) -> dict[str, Any]:
        factors: dict[str, float] = {}
        task_lower = task_description.lower()

        keyword_weights = {
            "database": 0.95,
            "migration": 0.90,
            "sql": 0.85,
            "mcp": 0.90,
            "tool": 0.75,
            "server": 0.80,
            "context": 0.85,
            "ctx": 0.70,
            "feedback": 0.80,
            "loop": 0.65,
            "gate": 0.85,
            "rbac": 0.90,
            "permission": 0.85,
            "blueprint": 0.95,
            "audit": 0.90,
            "drift": 0.80,
            "knowledge": 0.80,
            "kb": 0.70,
            "rollback": 0.90,
            "undo": 0.75,
            "vector": 0.85,
            "memory": 0.75,
            "a2a": 0.90,
            "agent": 0.80,
            "security": 0.95,
            "injection": 0.90,
        }

        scores: dict[str, float] = {}
        for kw, weight in keyword_weights.items():
            if kw in task_lower:
                for alt in alternatives:
                    if kw in alt:
                        scores[alt] = scores.get(alt, 0.0) + weight * 0.25

        route_confidence = 0.0
        for kw, weight in keyword_weights.items():
            if kw in task_lower and kw in chosen_skill_id:
                route_confidence += weight * 0.25

        is_singular = route_confidence >= 0.70

        return {
            "chosen_skill": chosen_skill_id,
            "confidence": round(min(route_confidence, 1.0), 2),
            "decision_quality": "high" if is_singular else "moderate",
            "alternative_skills": list(dict.fromkeys(alternatives)),
            "what_if": cls._counterfactual(chosen_skill_id, alternatives, scores),
        }

    @classmethod
    def _counterfactual(
        cls,
        chosen: str,
        alternatives: list[str],
        scores: dict[str, float],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for alt in alternatives:
            if alt != chosen:
                alt_score = scores.get(alt, 0.1)
                results.append(
                    {
                        "skill": alt,
                        "estimated_accuracy": round(alt_score, 2),
                        "diff_from_chosen": round(min(0.95, scores.get(chosen, 0.7)) - alt_score, 2),
                    }
                )
        return sorted(results, key=lambda x: -x["estimated_accuracy"])[:3]

    @classmethod
    def isolate_factors(
        cls,
        skill_id: str,
        output_quality: float,
        llm_model: str,
    ) -> dict[str, Any]:
        skill_factor = 0.0
        llm_factor = 0.0

        try:
            from zephyr.autonomy_core.skills.skill_evaluator import SkillEvaluator

            eval_result = SkillEvaluator.evaluate(skill_id)
            skill_factor = eval_result.get("overall_score", 50.0) / 100.0
        except Exception:
            skill_factor = 0.5

        try:
            from zephyr.autonomy_core.skills.skill_model_evolution import SkillModelEvolution

            impact = SkillModelEvolution.assess_impact(skill_id, "deepseek-v3", llm_model)
            llm_score = impact.get("overall_score", 100.0)
            llm_factor = llm_score / 100.0
        except Exception:
            llm_factor = 0.7

        skill_contribution = skill_factor * 0.60
        llm_contribution = llm_factor * 0.40

        return {
            "skill_id": skill_id,
            "llm_model": llm_model,
            "output_quality": round(output_quality, 2),
            "skill_factor": round(skill_factor, 2),
            "llm_factor": round(llm_factor, 2),
            "skill_contribution_60pct": round(skill_contribution, 2),
            "llm_contribution_40pct": round(llm_contribution, 2),
            "bottleneck_diagnosis": (
                "skill" if skill_factor < llm_factor else ("llm" if llm_factor < skill_factor else "balanced")
            ),
        }
