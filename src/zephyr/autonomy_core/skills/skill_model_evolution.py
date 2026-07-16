# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_model_evolution
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
MOD-INF-019: Agent Spec — Skill Model Evolution
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

LLM 升级影响评估引擎
====================
评估 Skill 在底层 LLM 模型升级时的兼容性风险:
  1. ToolCompatibility: 检查 Skill 中引用的工具在新模型中是否可用
  2. PromptStyleCompat: 评估 Skill 的指令风格是否与新模型对齐
  3. TokenBudgetImpact: 模型切换后 Token 预算是否仍满足
  4. FallbackPlan: 若不兼容，生成降级/回退方案
"""

from __future__ import annotations

from typing import Any

_MODEL_PROFILES: dict[str, dict[str, Any]] = {
    "deepseek-v3": {
        "family": "deepseek",
        "max_context": 65536,
        "recommended_style": ["structured", "step-by-step", "table"],
        "tool_support": ["read_file", "write_file", "search_replace", "grep", "glob", "run_command"],
        "strengths": ["code_generation", "structured_output", "reasoning"],
        "token_efficiency": 0.85,
    },
    "deepseek-r1": {
        "family": "deepseek",
        "max_context": 131072,
        "recommended_style": ["structured", "step-by-step", "table", "chain-of-thought"],
        "tool_support": ["read_file", "write_file", "search_replace", "grep", "glob", "run_command"],
        "strengths": ["reasoning", "deep_analysis", "code_generation"],
        "token_efficiency": 0.90,
    },
    "claude-sonnet-4": {
        "family": "claude",
        "max_context": 200000,
        "recommended_style": ["structured", "chain-of-thought", "section-by-section"],
        "tool_support": ["read_file", "write_file", "search_replace", "grep", "glob", "run_command"],
        "strengths": ["reasoning", "analysis", "code_generation", "creative"],
        "token_efficiency": 0.80,
    },
    "claude-opus-4-7": {
        "family": "claude",
        "max_context": 200000,
        "recommended_style": ["structured", "chain-of-thought", "section-by-section", "expert"],
        "tool_support": ["read_file", "write_file", "search_replace", "grep", "glob", "run_command"],
        "strengths": ["deep_reasoning", "expert_analysis", "security", "rescue"],
        "token_efficiency": 0.75,
    },
    "glm-5.1": {
        "family": "glm",
        "max_context": 32768,
        "recommended_style": ["step-by-step", "concise", "checklist"],
        "tool_support": ["read_file", "write_file", "search_replace", "grep", "glob"],
        "strengths": ["review", "audit", "validation"],
        "token_efficiency": 0.70,
    },
    "gpt-4o": {
        "family": "openai",
        "max_context": 128000,
        "recommended_style": ["structured", "table", "markdown"],
        "tool_support": ["read_file", "write_file", "search_replace", "grep", "glob", "run_command"],
        "strengths": ["code_generation", "structured_output", "compliance"],
        "token_efficiency": 0.80,
    },
}


class SkillModelEvolution:
    """Skill 模型进化兼容性评估器"""

    @classmethod
    def _find_model(cls, model_ref: str) -> dict[str, Any] | None:
        model_lower = model_ref.lower().replace(" ", "-")
        for key, profile in _MODEL_PROFILES.items():
            if key in model_lower or model_lower in key:
                return profile
        for key, profile in _MODEL_PROFILES.items():
            family = profile["family"]
            if family in model_lower:
                return profile
        return None

    @classmethod
    def _check_tool_compat(
        cls,
        old_profile: dict[str, Any],
        new_profile: dict[str, Any],
    ) -> dict[str, Any]:
        old_tools = set(old_profile.get("tool_support", []))
        new_tools = set(new_profile.get("tool_support", []))
        lost = old_tools - new_tools
        gained = new_tools - old_tools

        score = 100.0
        if old_tools:
            score = max(0.0, (1.0 - len(lost) / len(old_tools)) * 100.0)

        return {
            "compatible": len(lost) == 0,
            "score": round(score, 1),
            "tools_lost": sorted(lost),
            "tools_gained": sorted(gained),
        }

    @classmethod
    def _check_style_compat(
        cls,
        old_profile: dict[str, Any],
        new_profile: dict[str, Any],
    ) -> dict[str, Any]:
        old_styles = set(old_profile.get("recommended_style", []))
        new_styles = set(new_profile.get("recommended_style", []))

        common = old_styles & new_styles
        score = (len(common) / max(len(old_styles), 1)) * 100.0

        return {
            "compatible": len(common) >= 2,
            "score": round(score, 1),
            "styles_shared": sorted(common),
            "styles_new_only": sorted(new_styles - old_styles),
        }

    @classmethod
    def _check_budget_impact(
        cls,
        old_profile: dict[str, Any],
        new_profile: dict[str, Any],
    ) -> dict[str, Any]:
        old_eff = old_profile.get("token_efficiency", 1.0)
        new_eff = new_profile.get("token_efficiency", 1.0)
        old_ctx = old_profile.get("max_context", 0)
        new_ctx = new_profile.get("max_context", 0)

        eff_change = (new_eff - old_eff) / max(old_eff, 0.01) * 100.0
        ctx_ratio = new_ctx / max(old_ctx, 1)

        score = 100.0
        if eff_change < -10:
            score -= 20
        if ctx_ratio < 0.5:
            score -= 30
        if eff_change < -20:
            score -= 30

        return {
            "compatible": score >= 50,
            "score": round(max(0.0, score), 1),
            "efficiency_change_pct": round(eff_change, 1),
            "context_ratio": round(ctx_ratio, 2),
            "old_eff": old_eff,
            "new_eff": new_eff,
        }

    @classmethod
    def _compute_risk(cls, scores: list[float]) -> str:
        avg = sum(scores) / len(scores) if scores else 100.0
        if avg >= 90:
            return "minimal"
        if avg >= 70:
            return "low"
        if avg >= 50:
            return "medium"
        if avg >= 30:
            return "high"
        return "critical"

    @classmethod
    def _generate_actions(
        cls,
        tool_compat: dict[str, Any],
        style_compat: dict[str, Any],
        budget_impact: dict[str, Any],
        risk: str,
    ) -> list[dict[str, str]]:
        actions: list[dict[str, str]] = []

        if tool_compat.get("tools_lost"):
            actions.append(
                {
                    "priority": "P0",
                    "action": f"Replace lost tools: {', '.join(tool_compat['tools_lost'])}",
                }
            )

        if not style_compat.get("compatible"):
            missing = style_compat.get("styles_new_only", [])
            actions.append(
                {
                    "priority": "P1",
                    "action": f"Adapt skill style to: {', '.join(missing[:3])}",
                }
            )

        if not budget_impact.get("compatible"):
            actions.append(
                {
                    "priority": "P1",
                    "action": f"Compact skill body to fit new context window ({budget_impact.get('context_ratio', 0):.0%})",
                }
            )

        if risk in ("high", "critical"):
            actions.append(
                {
                    "priority": "P0",
                    "action": "Run full SkillsBench before production deployment",
                }
            )

        if risk == "minimal":
            actions.append(
                {
                    "priority": "P3",
                    "action": "No changes required — safe upgrade",
                }
            )

        return actions

    @classmethod
    def assess_impact(
        cls,
        skill_id: str,
        old_model: str,
        new_model: str,
    ) -> dict[str, Any]:
        old_prof = cls._find_model(old_model)
        new_prof = cls._find_model(new_model)

        if old_prof is None:
            return {
                "skill_id": skill_id,
                "old_model": old_model,
                "new_model": new_model,
                "risk": "unknown",
                "error": f"Unknown old model: {old_model}",
                "scores": {},
                "actions": [],
            }

        if new_prof is None:
            return {
                "skill_id": skill_id,
                "old_model": old_model,
                "new_model": new_model,
                "risk": "unknown",
                "error": f"Unknown new model: {new_model}",
                "scores": {},
                "actions": [],
            }

        tool_compat = cls._check_tool_compat(old_prof, new_prof)
        style_compat = cls._check_style_compat(old_prof, new_prof)
        budget_impact = cls._check_budget_impact(old_prof, new_prof)

        scores = [
            tool_compat["score"],
            style_compat["score"],
            budget_impact["score"],
        ]
        risk = cls._compute_risk(scores)
        actions = cls._generate_actions(tool_compat, style_compat, budget_impact, risk)

        return {
            "skill_id": skill_id,
            "old_model": old_model,
            "new_model": new_model,
            "old_profile": {"family": old_prof["family"], "max_context": old_prof["max_context"]},
            "new_profile": {"family": new_prof["family"], "max_context": new_prof["max_context"]},
            "risk": risk,
            "overall_score": round(sum(scores) / len(scores), 1),
            "scores": {
                "tool_compatibility": tool_compat,
                "style_compatibility": style_compat,
                "budget_impact": budget_impact,
            },
            "actions": actions,
        }
