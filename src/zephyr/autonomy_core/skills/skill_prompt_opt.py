# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_prompt_opt
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
# [A_module] module_id=MOD-ORC_skill_prompt_opt | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Prompt Optimizer
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill Prompt 自动优化器
=======================
机制:
  1. ReadabilityScore: 评估 Skill 正文可读性(Flesch 近似)
  2. Compression: 在不丢失语义的前提下压缩冗余措辞
  3. StructuralOptimization: 重组 section 顺序到最优阅读流
  4. TokenReduction: 量化压缩带来的 Token 节省
"""

from __future__ import annotations

import re
from typing import Any


class SkillPromptOptimizer:
    """Skill Prompt 自动优化器"""

    REDUNDANT_PATTERNS = [
        (r"it\s+is\s+important\s+to\s+note\s+that\s+", ""),
        (r"please\s+be\s+aware\s+that\s+", ""),
        (r"in\s+order\s+to\s+", "to "),
        (r"due\s+to\s+the\s+fact\s+that\s+", "because "),
        (r"at\s+this\s+point\s+in\s+time\s+", "now "),
        (r"in\s+the\s+event\s+that\s+", "if "),
        (r"a\s+number\s+of\s+", "several "),
        (r"the\s+majority\s+of\s+", "most "),
        (r"despite\s+the\s+fact\s+that\s+", "although "),
        (r"in\s+close\s+proximity\s+to\s+", "near "),
    ]

    OPTIMAL_SECTION_ORDER = [
        "前置条件",
        "核心操作",
        "独特约束",
        "常见错误模式",
        "示例",
        "返回格式",
        "参考",
    ]

    @classmethod
    def compute_readability(cls, text: str) -> dict[str, Any]:
        words = len(re.findall(r"\b\w+\b", text))
        sentences = max(len(re.findall(r"[.!?。！？]+", text)), 1)
        syllables = len(re.findall(r"[aeiouyáéíóúàèìòùäëïöü]+", text, re.IGNORECASE))
        chars = len(text)

        if words == 0:
            return {"readability": 0.0, "level": "unknown"}

        avg_words_per_sentence = words / sentences
        avg_syllables_per_word = syllables / words

        flesch = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * avg_syllables_per_word
        flesch = max(0.0, min(100.0, flesch))

        if flesch >= 70:
            level = "easy"
        elif flesch >= 50:
            level = "moderate"
        elif flesch >= 30:
            level = "difficult"
        else:
            level = "very_difficult"

        return {
            "readability_score": round(flesch, 1),
            "level": level,
            "words": words,
            "sentences": sentences,
            "characters": chars,
        }

    @classmethod
    def compress(cls, body: str) -> tuple[str, dict[str, Any]]:
        compressed = body

        reductions: list[dict[str, Any]] = []
        for pattern, replacement in cls.REDUNDANT_PATTERNS:
            matches = list(re.finditer(pattern, compressed, re.IGNORECASE))
            if matches:
                saved = sum(m.end() - m.start() for m in matches)
                compressed = re.sub(pattern, replacement, compressed, flags=re.IGNORECASE)
                reductions.append(
                    {
                        "pattern": pattern[:50],
                        "occurrences": len(matches),
                        "chars_saved": saved,
                    }
                )

        blank_lines = len(re.findall(r"\n{3,}", compressed))
        if blank_lines:
            compressed = re.sub(r"\n{3,}", "\n\n", compressed)

        total_saved = len(body) - len(compressed)
        pct = (total_saved / max(len(body), 1)) * 100.0

        return compressed, {
            "original_length": len(body),
            "compressed_length": len(compressed),
            "chars_saved": total_saved,
            "reduction_pct": round(pct, 1),
            "reductions": reductions,
        }

    @classmethod
    def reorder_sections(cls, body: str) -> str:
        sections: dict[str, str] = {}
        current_section = "preamble"
        current_lines: list[str] = []

        for line in body.split("\n"):
            match = re.match(r"^#{1,3}\s+(.+)$", line)
            if match:
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                title = match.group(1).strip()
                current_section = title
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections[current_section] = "\n".join(current_lines)

        result_lines: list[str] = []
        if "preamble" in sections:
            result_lines.append(sections["preamble"])

        for optimal_section in cls.OPTIMAL_SECTION_ORDER:
            for real_section in sections:
                if real_section == "preamble":
                    continue
                if optimal_section in real_section.lower():
                    result_lines.append(sections.pop(real_section, ""))
                    break

        for remaining in sections.values():
            result_lines.append(remaining)

        return "\n".join(result_lines)

    @classmethod
    def optimize(cls, skill_id: str, body: str | None = None) -> dict[str, Any]:
        if body is None:
            try:
                from zephyr.autonomy_core.skills.skill_loader import SkillLoader

                loader = SkillLoader()
                loaded = loader.progressive_load(skill_id)
                body = loaded.get("l2", "")
            except Exception:
                return {
                    "skill_id": skill_id,
                    "improvement_pct": 0.0,
                    "error": "failed_to_load_skill",
                    "original": "",
                    "optimized": "",
                }

        readability = cls.compute_readability(body)

        compressed, comp_stats = cls.compress(body)

        reordered = cls.reorder_sections(compressed)
        reordered_readability = cls.compute_readability(reordered)

        token_saved = max(0, len(body) - len(reordered))
        est_token_saving = token_saved // 4

        improvement = comp_stats["reduction_pct"]
        if reordered_readability["readability_score"] > readability["readability_score"]:
            improvement += 2.0

        return {
            "skill_id": skill_id,
            "improvement_pct": round(min(improvement, 100.0), 1),
            "original_stats": readability,
            "optimized_stats": reordered_readability,
            "compression": comp_stats,
            "estimated_token_saving": est_token_saving,
            "original_preview": body[:300],
            "optimized_preview": reordered[:300],
            "optimized": reordered,
        }
