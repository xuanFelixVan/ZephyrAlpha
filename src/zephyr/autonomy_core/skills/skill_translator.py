# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_translator
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
# [A_module] module_id=MOD-ORC_skill_translator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Translator
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

跨模型 Skill 翻译器
===================
将 DeepSeek 风格的 Skill 指令翻译为 Claude/GLM/GPT 风格的等效指令:
  1. StyleAdaptation: 从 {structured, step-by-step, table} -> {section-by-section, chain-of-thought}
  2. TerminologyTranslation: 从 DeepSeek 术语 -> Claude 等效术语
  3. ToolRemapping: 工具名差异校正
"""

from __future__ import annotations

from typing import Any

_MODEL_ADAPTATIONS: dict[str, dict[str, Any]] = {
    "deepseek": {
        "style": "structured, step-by-step, table-heavy",
        "phrases": {
            "MUST": "MUST",
            "必须确保": "必须确保",
            "不可": "不可",
            "CRITICAL": "CRITICAL",
        },
        "tool_prefix": "read_file",
    },
    "claude": {
        "style": "section-by-section, chain-of-thought, descriptive",
        "phrases": {
            "MUST": "MUST ALWAYS ensure that",
            "必须确保": "you are required to verify and guarantee that",
            "不可": "under no circumstances should you",
            "CRITICAL": "CRITICAL (non-negotiable constraint)",
        },
        "tool_prefix": "read_file",
    },
    "openai": {
        "style": "markdown-structured, explicit, checklist-friendly",
        "phrases": {
            "MUST": "The agent MUST output",
            "必须确保": "Verify with explicit evidence that",
            "不可": "Do not – under any condition –",
            "CRITICAL": "HARD RULE (block if violated)",
        },
        "tool_prefix": "read_file",
    },
    "glm": {
        "style": "concise, checklist, step-numbered",
        "phrases": {
            "MUST": "要求:",
            "必须确保": "需确认:",
            "不可": "禁止:",
            "CRITICAL": "【强制】",
        },
        "tool_prefix": "read_file",
    },
}


class SkillTranslator:
    """跨模型 Skill 翻译器"""

    @classmethod
    def _infer_source_family(cls, body: str) -> str:
        body_lower = body[:500].lower()
        if any(w in body_lower for w in ["claude", "anthropic"]):
            return "claude"
        if any(w in body_lower for w in ["glm", "智谱", "chatglm"]):
            return "glm"
        if any(w in body_lower for w in ["gpt", "openai"]):
            return "openai"
        return "deepseek"

    @classmethod
    def _apply_adaptation(
        cls,
        body: str,
        target_adaptation: dict[str, Any],
        source_adaptation: dict[str, Any],
    ) -> str:
        result = body

        target_style = target_adaptation.get("style", "")
        result = result.replace(
            source_adaptation.get("style", "structured"),
            target_style,
        )

        target_phrases = target_adaptation.get("phrases", {})
        source_phrases = source_adaptation.get("phrases", {})

        for phrase_key in target_phrases:
            if phrase_key in source_phrases:
                result = result.replace(
                    source_phrases[phrase_key],
                    f"{source_phrases[phrase_key]} ({target_phrases[phrase_key]})",
                )

        return result

    @classmethod
    def translate(
        cls,
        skill_id: str,
        target_model_family: str,
        custom_body: str | None = None,
    ) -> dict[str, Any]:
        body = custom_body
        if body is None:
            try:
                from zephyr.autonomy_core.skills.skill_loader import SkillLoader

                loader = SkillLoader()
                loaded = loader.progressive_load(skill_id)
                body = loaded.get("l2", "")
            except Exception:
                return {
                    "skill_id": skill_id,
                    "target_model_family": target_model_family,
                    "status": "translation_failed",
                    "error": "failed_to_load_skill",
                    "original": "",
                    "translated": "",
                }

        source_family = cls._infer_source_family(body)

        source_adaptation = _MODEL_ADAPTATIONS.get(source_family, _MODEL_ADAPTATIONS["deepseek"])
        target_adaptation = _MODEL_ADAPTATIONS.get(target_model_family)
        if target_adaptation is None:
            return {
                "skill_id": skill_id,
                "target_model_family": target_model_family,
                "status": "translation_failed",
                "error": f"Unknown target model family: {target_model_family}",
                "source_family": source_family,
                "original": body[:500],
                "translated": "",
            }

        translated = cls._apply_adaptation(body, target_adaptation, source_adaptation)

        header = f"[Auto-translated by SkillTranslator: {source_family.capitalize()} -> {target_model_family.capitalize()}]\n\n"
        translated = header + translated

        return {
            "skill_id": skill_id,
            "source_family": source_family,
            "target_model_family": target_model_family,
            "status": "translated",
            "original_preview": body[:300],
            "translated_preview": translated[:300],
            "translated": translated,
            "original_length": len(body),
            "translated_length": len(translated),
        }
