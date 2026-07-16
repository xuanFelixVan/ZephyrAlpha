# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_attention
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
MOD-INF-019: Agent Spec — Skill Attention Management
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 注意力管理 —— 上下文窗口预算分配与裁剪。
在多 Skill 并发注入时，按优先级 + freshness 动态分配 token 配额。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AttentionSlot:
    skill_id: str
    allocated_tokens: int
    priority: float
    freshness: float


@dataclass
class AttentionPlan:
    slots: list[AttentionSlot] = field(default_factory=list)
    total_budget: int = 0
    total_allocated: int = 0
    overflow_skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slots": [
                {
                    "skill_id": s.skill_id,
                    "allocated_tokens": s.allocated_tokens,
                    "priority": s.priority,
                    "freshness": s.freshness,
                }
                for s in self.slots
            ],
            "total_budget": self.total_budget,
            "total_allocated": self.total_allocated,
            "overflow_skills": self.overflow_skills,
        }


class SkillAttention:
    """Skill 注意力管理 —— 上下文窗口优化.

    使用策略:
      - Domain + Role 双 Skill 注入时，按 priority × freshness 加权分配 L2 body token 预算
      - 超过窗口上限时按加权分裁剪，最低分 Skill 降级为 L1-only（仅 frontmatter）
    """

    DEFAULT_L2_TOKEN_BUDGET = 800
    DEFAULT_MAX_SKILLS = 6

    @staticmethod
    def allocate(
        skill_candidates: list[dict[str, Any]],
        window_size: int | None = None,
        max_skills: int | None = None,
    ) -> AttentionPlan:
        budget = window_size or SkillAttention.DEFAULT_L2_TOKEN_BUDGET
        max_n = max_skills or SkillAttention.DEFAULT_MAX_SKILLS

        scored = []
        for c in skill_candidates:
            priority = float(c.get("priority", 0.5))
            freshness = float(c.get("freshness_score", 50.0)) / 100.0
            scored.append((c["skill_id"], priority * freshness, c))

        scored.sort(key=lambda x: x[1], reverse=True)
        selected = scored[:max_n]
        overflow = [s[0] for s in scored[max_n:]]

        if not selected:
            return AttentionPlan(slots=[], total_budget=budget, total_allocated=0, overflow_skills=overflow)

        total_weight = sum(s[1] for s in selected) or 1.0
        slots = []
        total_alloc = 0
        for sid, weight, candidate in selected:
            allocated = max(50, int(budget * weight / total_weight))
            slots.append(
                AttentionSlot(
                    skill_id=sid,
                    allocated_tokens=allocated,
                    priority=candidate.get("priority", 0.5),
                    freshness=candidate.get("freshness_score", 50.0),
                )
            )
            total_alloc += allocated

        return AttentionPlan(
            slots=slots,
            total_budget=budget,
            total_allocated=total_alloc,
            overflow_skills=overflow,
        )

    @staticmethod
    def inject_context(plan: AttentionPlan, skill_bodies: dict[str, str]) -> str:
        parts = []
        for slot in plan.slots:
            body = skill_bodies.get(slot.skill_id, "")
            if not body:
                continue
            truncated = body[: slot.allocated_tokens * 4]
            parts.append(f"[Skill: {slot.skill_id} | budget={slot.allocated_tokens} tokens]\n{truncated}")
        return "\n\n---\n\n".join(parts)
