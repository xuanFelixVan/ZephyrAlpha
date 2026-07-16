# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_team_optimizer
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
MOD-INF-019: Agent Spec — Skill Team Optimizer
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 团队组合优化器
"""

from __future__ import annotations

from typing import Any

_SKILL_PAIRS_COMPAT: dict[str, dict[str, float]] = {
    "database-specialist": {
        "implementer": 0.95,
        "reviewer": 0.85,
        "rollback-specialist": 0.90,
        "drift-detector": 0.65,
    },
    "mcp-specialist": {
        "implementer": 0.90,
        "reviewer": 0.80,
        "lsg-security": 0.95,
        "system-telemetry": 0.85,
    },
    "gate-specialist": {
        "reviewer": 0.95,
        "auditor": 0.90,
        "drift-detector": 0.85,
        "lsg-security": 0.80,
    },
    "lsg-security": {
        "reviewer": 0.90,
        "auditor": 0.95,
        "drift-detector": 0.85,
        "system-telemetry": 0.75,
    },
    "code-dedup-engine": {
        "implementer": 0.85,
        "auto-fix-engine": 0.95,
        "rollback-specialist": 0.70,
    },
    "auto-fix-engine": {
        "implementer": 0.90,
        "code-dedup-engine": 0.95,
        "rollback-specialist": 0.85,
    },
}


def _match_skills(task_lower: str) -> tuple[list[str], list[str]]:
    keyword_map = {
        "database": "database-specialist",
        "migration": "database-specialist",
        "sql": "database-specialist",
        "mcp": "mcp-specialist",
        "tool": "mcp-specialist",
        "feedback": "feedback-specialist",
        "gate": "gate-specialist",
        "permission": "agent-specialist",
        "rbac": "agent-specialist",
        "audit": "drift-detector",
        "drift": "drift-detector",
        "rollback": "rollback-specialist",
        "knowledge": "knowledge-specialist",
        "security": "lsg-security",
        "injection": "lsg-security",
        "dedu": "code-dedup-engine",
        "fix": "auto-fix-engine",
        "repair": "auto-fix-engine",
        "context": "context-specialist",
        "vector": "vector-memory",
        "memory": "vector-memory",
        "a2a": "a2a-protocol",
    }
    skills_matched: list[str] = []
    keywords: list[str] = []
    for kw, skill in keyword_map.items():
        if kw in task_lower:
            keywords.append(kw)
            if skill not in skills_matched:
                skills_matched.append(skill)
    return keywords, skills_matched


def _build_rationale(best_coverage: float, best_compat: float, skills_matched: list[str]) -> str:
    rationale_parts: list[str] = []
    if best_coverage > 0.6:
        rationale_parts.append(f"high coverage ({best_coverage:.0%})")
    if best_compat > 0.7:
        rationale_parts.append(f"high compatibility ({best_compat:.0%})")
    if skills_matched:
        rationale_parts.append(f"{len(skills_matched)} skills matched")
    if not rationale_parts:
        rationale_parts.append("default_first_three")
    return ", ".join(rationale_parts)


class SkillTeamOptimizer:
    @classmethod
    def _compat_score(cls, skill_a: str, skill_b: str) -> float:
        base_a = skill_a.split("/")[-1]
        base_b = skill_b.split("/")[-1]
        if base_a == base_b:
            return 0.3
        for key, compat in _SKILL_PAIRS_COMPAT.items():
            if key in base_a or base_a in key:
                for other, score in compat.items():
                    if other in base_b or base_b in other:
                        return score
        for key, compat in _SKILL_PAIRS_COMPAT.items():
            if key in base_b or base_b in key:
                for other, score in compat.items():
                    if other in base_a or base_a in other:
                        return score
        return 0.5

    @classmethod
    def _coverage(cls, team: list[str], task_keywords: list[str]) -> float:
        matched = sum(1 for kw in task_keywords for s in team if kw.lower() in s.lower())
        return min(matched / max(len(task_keywords), 1), 1.0)

    @classmethod
    def _team_score(cls, team: list[str], task_keywords: list[str]) -> tuple[float, float, float]:
        if len(team) < 2:
            return 0.3, 0.5, 0.4
        pairs = 0
        compat_sum = 0.0
        for i in range(len(team)):
            for j in range(i + 1, len(team)):
                compat_sum += cls._compat_score(team[i], team[j])
                pairs += 1
        avg_compat = compat_sum / max(pairs, 1)
        coverage = cls._coverage(team, task_keywords)
        total = avg_compat * 0.4 + coverage * 0.4 + min(len(team) / 3.0, 1.0) * 0.2
        return total, avg_compat, coverage

    @classmethod
    def optimize(
        cls,
        task_description: str,
        available_skills: list[str] | None = None,
        max_team_size: int = 3,
    ) -> dict[str, Any]:
        task_lower = task_description.lower()
        keywords, skills_matched = _match_skills(task_lower)

        candidates = available_skills or skills_matched
        if len(candidates) < 3:
            domain = [
                "database-specialist",
                "mcp-specialist",
                "context-specialist",
                "feedback-specialist",
                "gate-specialist",
                "agent-specialist",
                "rollback-specialist",
                "knowledge-specialist",
                "lsg-security",
                "drift-detector",
                "code-dedup-engine",
                "auto-fix-engine",
                "vector-memory",
                "a2a-protocol",
                "system-telemetry",
            ]
            extra = [s for s in domain if s not in candidates]
            candidates = candidates + extra[: max_team_size - len(candidates)]

        best_team: list[str] = candidates[:max_team_size]
        best_score = 0.0
        best_compat = 0.0
        best_coverage = 0.0
        for i in range(len(candidates)):
            for j in range(i + 1, min(len(candidates), i + 5)):
                for k in range(j + 1, min(len(candidates), j + 5)):
                    team = [candidates[i], candidates[j], candidates[k]]
                    score, compat, coverage = cls._team_score(team, keywords)
                    if score > best_score:
                        best_score = score
                        best_compat = compat
                        best_coverage = coverage
                        best_team = list(team)

        rationale = _build_rationale(best_coverage, best_compat, skills_matched)

        return {
            "task_keywords": keywords,
            "best_team": best_team,
            "team_score": round(best_score, 2),
            "compatibility": round(best_compat, 2),
            "coverage": round(best_coverage, 2),
            "rationale": rationale,
            "alternatives": (
                [{"team": best_team[:2], "score": round(best_score * 0.85, 2)}] if len(best_team) == 3 else []
            ),
        }
