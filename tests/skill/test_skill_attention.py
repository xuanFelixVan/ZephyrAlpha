# [A_test] module_id: MOD-GOV_skill_attention | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §

# [MODULE] tests.test_skill_attention

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] python -m pytest tests/test_skill_attention.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.autonomy_core.skills.skill_attention import (
    AttentionPlan,
    AttentionSlot,
    SkillAttention,
)


class TestAttentionSlot:
    def test_creation(self):
        slot = AttentionSlot(skill_id="s1", allocated_tokens=100, priority=0.8, freshness=0.9)
        assert slot.skill_id == "s1"
        assert slot.allocated_tokens == 100
        assert slot.priority == 0.8
        assert slot.freshness == 0.9


class TestAttentionPlan:
    def test_default_values(self):
        plan = AttentionPlan()
        assert plan.slots == []
        assert plan.total_budget == 0
        assert plan.total_allocated == 0
        assert plan.overflow_skills == []

    def test_to_dict(self):
        slot = AttentionSlot(skill_id="s1", allocated_tokens=100, priority=0.5, freshness=50.0)
        plan = AttentionPlan(slots=[slot], total_budget=800, total_allocated=100, overflow_skills=["s2"])
        d = plan.to_dict()
        assert d["total_budget"] == 800
        assert len(d["slots"]) == 1
        assert d["slots"][0]["skill_id"] == "s1"
        assert d["overflow_skills"] == ["s2"]


class TestSkillAttentionAllocate:
    def test_empty_candidates(self):
        plan = SkillAttention.allocate([])
        assert plan.slots == []
        assert plan.total_allocated == 0

    def test_single_candidate(self):
        candidates = [{"skill_id": "s1", "priority": 1.0, "freshness_score": 100.0}]
        plan = SkillAttention.allocate(candidates)
        assert len(plan.slots) == 1
        assert plan.slots[0].skill_id == "s1"

    def test_multiple_candidates_sorted_by_weight(self):
        candidates = [
            {"skill_id": "low", "priority": 0.1, "freshness_score": 10.0},
            {"skill_id": "high", "priority": 1.0, "freshness_score": 100.0},
            {"skill_id": "mid", "priority": 0.5, "freshness_score": 50.0},
        ]
        plan = SkillAttention.allocate(candidates)
        assert plan.slots[0].skill_id == "high"

    def test_overflow_skills(self):
        candidates = [{"skill_id": f"s{i}", "priority": 1.0 - i * 0.1, "freshness_score": 100.0} for i in range(8)]
        plan = SkillAttention.allocate(candidates, max_skills=4)
        assert len(plan.slots) == 4
        assert len(plan.overflow_skills) == 4

    def test_custom_window_size(self):
        candidates = [{"skill_id": "s1", "priority": 1.0, "freshness_score": 100.0}]
        plan = SkillAttention.allocate(candidates, window_size=2000)
        assert plan.total_budget == 2000

    def test_minimum_allocation(self):
        candidates = [{"skill_id": f"s{i}", "priority": 0.01, "freshness_score": 1.0} for i in range(10)]
        plan = SkillAttention.allocate(candidates, window_size=100, max_skills=10)
        for slot in plan.slots:
            assert slot.allocated_tokens >= 50

    def test_default_priority_and_freshness(self):
        candidates = [{"skill_id": "s1"}]
        plan = SkillAttention.allocate(candidates)
        assert plan.slots[0].priority == 0.5
        assert plan.slots[0].freshness == 50.0


class TestSkillAttentionInjectContext:
    def test_empty_plan(self):
        plan = AttentionPlan()
        result = SkillAttention.inject_context(plan, {})
        assert result == ""

    def test_single_skill(self):
        slot = AttentionSlot(skill_id="s1", allocated_tokens=100, priority=0.5, freshness=50.0)
        plan = AttentionPlan(slots=[slot])
        bodies = {"s1": "Hello world content"}
        result = SkillAttention.inject_context(plan, bodies)
        assert "s1" in result
        assert "Hello world" in result

    def test_missing_body_skipped(self):
        slot = AttentionSlot(skill_id="s1", allocated_tokens=100, priority=0.5, freshness=50.0)
        plan = AttentionPlan(slots=[slot])
        result = SkillAttention.inject_context(plan, {})
        assert result == ""

    def test_truncation(self):
        slot = AttentionSlot(skill_id="s1", allocated_tokens=10, priority=0.5, freshness=50.0)
        plan = AttentionPlan(slots=[slot])
        long_body = "A" * 1000
        bodies = {"s1": long_body}
        result = SkillAttention.inject_context(plan, bodies)
        assert len(result) < len(long_body)

    def test_multiple_skills(self):
        slots = [
            AttentionSlot(skill_id="s1", allocated_tokens=100, priority=0.5, freshness=50.0),
            AttentionSlot(skill_id="s2", allocated_tokens=100, priority=0.5, freshness=50.0),
        ]
        plan = AttentionPlan(slots=slots)
        bodies = {"s1": "Content 1", "s2": "Content 2"}
        result = SkillAttention.inject_context(plan, bodies)
        assert "s1" in result
        assert "s2" in result
