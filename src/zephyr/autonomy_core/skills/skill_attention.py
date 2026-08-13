# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_attention
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Skill 候选列表 字典列表
#   fields: skill_id + priority(默认0.5) + freshness_score(默认50.0)
#   code: allocate(skill_candidates) L79
# - id: I2
#   name: 窗口预算参数 整数
#   fields: window_size（L2 token 预算，默认 800）+ max_skills（最多注入数，默认 6）
#   code: DEFAULT_L2_TOKEN_BUDGET/DEFAULT_MAX_SKILLS L74-75
# - id: I3
#   name: Skill 正文 字典
#   fields: {skill_id: body 文本}
#   code: inject_context(skill_bodies) L122
# 层: 算法
# - id: A1
#   name_zh: ① 加权评分排序筛选
#   name_en: SkillAttention.allocate（评分段）
#   intro: 按 优先级×新鲜度 给每个 Skill 打分，高的留下，多的进溢出名单
#   desc: score=priority×freshness_score/100 → 降序排序 → 取前 max_n 个，其余记 overflow_skills；空候选直接返回空 plan
#   inputs: I1 I2
#   outputs: 入选名单 + 溢出名单
# - id: A2
#   name_zh: ② 预算按比例分配
#   name_en: SkillAttention.allocate（分配段）
#   intro: 按分数权重瓜分 token 预算，每个最少保底 50
#   desc: allocated = max(50, int(budget × weight / total_weight))，逐 slot 累计 total_allocated
#   inputs: I1 I2 A1
#   outputs: AttentionPlan（slots/total_budget/total_allocated/overflow_skills）
# - id: A3
#   name_zh: ③ 上下文拼装注入
#   name_en: SkillAttention.inject_context
#   intro: 按配额截断各 Skill 正文，拼成一段注入上下文
#   desc: body[:allocated×4] 截断 + "[Skill: id | budget=N tokens]" 头，"\n\n---\n\n" 连接
#   inputs: I3 A2
#   outputs: 注入上下文字符串
# 层: 输出
# - id: O1
#   name_zh: 注意力分配方案
#   name_en: AttentionPlan
#   intro: 各 Skill 的 token 配额与溢出名单（可 to_dict 序列化）
#   downstream: 无下游/内部使用（Agent Spec 技能注入流程内部调用，[CONSUMERS] 头为空）
# - id: O2
#   name_zh: 注入上下文字符串
#   name_en: injected context str
#   intro: 拼好可直接塞进提示词的多 Skill 上下文文本
#   downstream: 无下游/内部使用（Agent 提示词组装环节）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A2
# I3 --> A3
# A2 --> A3
# A2 --> O1
# A3 --> O2
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
