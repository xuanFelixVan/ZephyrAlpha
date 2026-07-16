# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_evaluator
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
MOD-INF-019: Agent Spec — Skill Evaluator
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 质量评估器 — 多维度输出质量评分
======================================
维度:
  1. StructureQuality: frontmatter 完整性、section 覆盖率
  2. ContentDensity: 信息密度（指令数/行数）
  3. ConstraintCoverage: 约束定义的覆盖范围
  4. FreshnessDecay: 综合考虑衰减因子
  5. TokenEfficiency: 信息量/Token 比率
"""

from __future__ import annotations

import re
from typing import Any


class SkillEvaluator:
    """Skill 多维度质量评估器"""

    STRUCTURE_WEIGHT = 0.25
    DENSITY_WEIGHT = 0.25
    CONSTRAINT_WEIGHT = 0.20
    FRESHNESS_WEIGHT = 0.15
    TOKEN_EFF_WEIGHT = 0.15

    ESSENTIAL_SECTIONS = [
        "核心操作",
        "约束",
        "常见错误",
        "前置条件",
        "返回格式",
    ]

    @classmethod
    def _evaluate_structure(cls, body: str, l1_data: dict[str, Any]) -> Tuple[float, list[str]]:
        score = 0.0
        issues: list[str] = []

        if l1_data.get("skill_id") and l1_data.get("name"):
            score += 20
        else:
            issues.append("missing_id_or_name")

        if l1_data.get("allowed_tools"):
            score += 15
        else:
            issues.append("no_tool_allowlist")

        if l1_data.get("description"):
            score += 10
        else:
            issues.append("no_description")

        body_lower = body.lower()
        section_hits = 0
        for section in cls.ESSENTIAL_SECTIONS:
            if section in body_lower:
                section_hits += 1

        score += (section_hits / len(cls.ESSENTIAL_SECTIONS)) * 40

        if "version" in l1_data:
            score += 10

        if l1_data.get("model_hint"):
            score += 5

        return score, issues

    @classmethod
    def _evaluate_density(cls, body: str) -> Tuple[float, dict[str, Any]]:
        lines = [l for l in body.split("\n") if l.strip()]
        if len(lines) < 5:
            return 0.0, {"line_count": len(lines), "detail": "too_short"}

        directives = len(re.findall(r"(?:MUST|必须|不可|禁止|不要|确保|要求|always|never|ensure|require)", body))

        examples = len(re.findall(r"^```", body, re.MULTILINE)) // 2
        checklists = len(re.findall(r"^\s*-\s+\[[ x]\]", body, re.MULTILINE))
        steps = len(re.findall(r"^\d+[.\)]\s", body, re.MULTILINE))

        density = (directives + examples * 2 + checklists + steps) / max(len(lines), 1)
        score = min(100.0, density * 80)

        return score, {
            "line_count": len(lines),
            "directives": directives,
            "examples": examples,
            "checklists": checklists,
            "steps": steps,
            "density_ratio": round(density, 3),
        }

    @classmethod
    def _evaluate_constraints(cls, body: str) -> Tuple[float, list[str]]:
        constraint_categories = {
            "security": ["安全", "security", "injection", "注入", "sandbox"],
            "performance": ["性能", "performance", "latency", "延迟", "budget"],
            "correctness": ["正确", "correct", "准确", "accuracy", "验证"],
            "consistency": ["一致", "consist", "idempotent", "幂等"],
            "reversibility": ["回滚", "rollback", "checkpoint", "恢复"],
        }

        covered = 0
        missing: list[str] = []
        body_lower = body.lower()

        for cat, keywords in constraint_categories.items():
            if any(kw in body_lower for kw in keywords):
                covered += 1
            else:
                missing.append(cat)

        score = (covered / len(constraint_categories)) * 100.0
        return score, missing

    @classmethod
    def _evaluate_freshness(cls, freshness_data: dict[str, Any] | None = None) -> Tuple[float, dict[str, Any]]:
        if freshness_data is None:
            return 50.0, {"detail": "no_freshness_data"}

        score = freshness_data.get("freshness_score", 50.0)
        return score, freshness_data

    @classmethod
    def _evaluate_token_efficiency(cls, body: str, token_count: int) -> Tuple[float, dict[str, Any]]:
        if token_count == 0:
            return 0.0, {"detail": "zero_tokens"}

        directives = len(re.findall(r"(?:MUST|必须|不可|禁止|不要|确保|要求|always|never|ensure|require)", body))
        examples = len(re.findall(r"^```", body, re.MULTILINE)) // 2
        useful = directives + examples * 2

        efficiency = useful / max(token_count / 10, 1)
        score = min(100.0, efficiency * 50)

        return score, {
            "tokens": token_count,
            "useful_elements": useful,
            "efficiency_ratio": round(efficiency, 3),
        }

    @classmethod
    def evaluate(cls, skill_id: str) -> dict[str, Any]:
        try:
            from zephyr.autonomy_core.skills.skill_freshness import FreshnessDecayModel
            from zephyr.autonomy_core.skills.skill_loader import SkillLoader

            loader = SkillLoader()
            loaded = loader.progressive_load(skill_id)

            l1 = loaded.get("l1", {})
            l2 = loaded.get("l2", "")
            token_count = loaded.get("token_count_l2", 0)

            struct_score, struct_issues = cls._evaluate_structure(l2, l1)
            density_score, density_detail = cls._evaluate_density(l2)
            constraint_score, constraint_missing = cls._evaluate_constraints(l2)

            try:
                freshness = FreshnessDecayModel()
                current = freshness.current_state(skill_id)
                fresh_score, fresh_detail = cls._evaluate_freshness(current)
            except Exception:
                fresh_score = 50.0
                fresh_detail = {"detail": "freshness_errored"}

            token_score, token_detail = cls._evaluate_token_efficiency(l2, token_count)

            overall = (
                struct_score * cls.STRUCTURE_WEIGHT
                + density_score * cls.DENSITY_WEIGHT
                + constraint_score * cls.CONSTRAINT_WEIGHT
                + fresh_score * cls.FRESHNESS_WEIGHT
                + token_score * cls.TOKEN_EFF_WEIGHT
            )

            grade = (
                "A"
                if overall >= 90
                else ("B" if overall >= 75 else ("C" if overall >= 60 else ("D" if overall >= 40 else "F")))
            )

            return {
                "skill_id": skill_id,
                "overall_score": round(overall, 1),
                "grade": grade,
                "dimensions": {
                    "structure": {"score": round(struct_score, 1), "issues": struct_issues},
                    "density": {"score": round(density_score, 1), **density_detail},
                    "constraints": {"score": round(constraint_score, 1), "missing_categories": constraint_missing},
                    "freshness": {"score": round(fresh_score, 1), **fresh_detail},
                    "token_efficiency": {"score": round(token_score, 1), **token_detail},
                },
                "issues": struct_issues + [f"missing_constraint_category:{c}" for c in constraint_missing],
            }

        except ImportError:
            return {
                "skill_id": skill_id,
                "overall_score": 0.0,
                "grade": "F",
                "error": "skill_loader_unavailable",
                "issues": [],
                "dimensions": {},
            }
        except (KeyError, FileNotFoundError) as e:
            return {
                "skill_id": skill_id,
                "overall_score": 0.0,
                "grade": "F",
                "error": str(e),
                "issues": [str(e)],
                "dimensions": {},
            }
