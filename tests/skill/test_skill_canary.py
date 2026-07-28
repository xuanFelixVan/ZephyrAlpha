# [A_test] module_id: MOD-GOV_skill_canary | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_canary
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_canary.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.autonomy_core.skills.skill_canary import SkillCanary


class TestSkillCanaryInit:
    def test_instantiation_creates_empty_canary_dict(self):
        sc = SkillCanary()
        assert sc.canary == {}

    def test_steps_constant(self):
        assert SkillCanary.STEPS == [5, 10, 25, 50, 100]


class TestDeployCanary:
    def test_deploy_canary_returns_entry(self):
        sc = SkillCanary()
        result = sc.deploy_canary("skill-abc", "1.0.0")
        assert result["skill_id"] == "skill-abc"
        assert result["version"] == "1.0.0"
        assert result["mode"] == "canary"
        assert result["traffic_percent"] == 5
        assert result["stage"] == 0
        assert "deployed_at" in result

    def test_deploy_canary_stores_in_internal_dict(self):
        sc = SkillCanary()
        sc.deploy_canary("skill-x", "2.0.0")
        assert "skill-x" in sc.canary
        assert sc.canary["skill-x"]["version"] == "2.0.0"

    def test_deploy_canary_overwrites_existing(self):
        sc = SkillCanary()
        sc.deploy_canary("skill-x", "1.0.0")
        sc.deploy_canary("skill-x", "2.0.0")
        assert sc.canary["skill-x"]["version"] == "2.0.0"

    def test_deploy_canary_empty_skill_id(self):
        sc = SkillCanary()
        result = sc.deploy_canary("", "0.1.0")
        assert result["skill_id"] == ""
        assert result["mode"] == "canary"

    def test_deploy_canary_empty_version(self):
        sc = SkillCanary()
        result = sc.deploy_canary("skill-y", "")
        assert result["version"] == ""
        assert result["skill_id"] == "skill-y"


class TestPromote:
    def test_promote_existing_canary(self):
        sc = SkillCanary()
        sc.deploy_canary("skill-abc", "1.0.0")
        result = sc.promote("skill-abc")
        assert result["status"] == "promoted"
        assert result["traffic_percent"] == 100
        assert result["skill_id"] == "skill-abc"

    def test_promote_updates_internal_state(self):
        sc = SkillCanary()
        sc.deploy_canary("skill-abc", "1.0.0")
        sc.promote("skill-abc")
        assert sc.canary["skill-abc"]["mode"] == "stable"
        assert sc.canary["skill-abc"]["traffic_percent"] == 100

    def test_promote_nonexistent_canary(self):
        sc = SkillCanary()
        result = sc.promote("nonexistent")
        assert result["status"] == "promoted"
        assert result["traffic_percent"] == 100

    def test_promote_empty_skill_id(self):
        sc = SkillCanary()
        result = sc.promote("")
        assert result["skill_id"] == ""
        assert result["traffic_percent"] == 100


class TestRollbackCanary:
    def test_rollback_existing_canary(self):
        sc = SkillCanary()
        sc.deploy_canary("skill-abc", "1.0.0")
        result = sc.rollback_canary("skill-abc")
        assert result["action"] == "rolled_back"
        assert result["traffic_percent"] == 0
        assert result["skill_id"] == "skill-abc"

    def test_rollback_updates_internal_state(self):
        sc = SkillCanary()
        sc.deploy_canary("skill-abc", "1.0.0")
        sc.rollback_canary("skill-abc")
        assert sc.canary["skill-abc"]["mode"] == "rolled_back"
        assert sc.canary["skill-abc"]["traffic_percent"] == 0

    def test_rollback_nonexistent_canary(self):
        sc = SkillCanary()
        result = sc.rollback_canary("nonexistent")
        assert result["action"] == "rolled_back"
        assert result["traffic_percent"] == 0

    def test_rollback_empty_skill_id(self):
        sc = SkillCanary()
        result = sc.rollback_canary("")
        assert result["skill_id"] == ""
        assert result["traffic_percent"] == 0


class TestCanaryWorkflow:
    def test_deploy_then_promote_then_rollback(self):
        sc = SkillCanary()
        sc.deploy_canary("skill-wf", "3.0.0")
        assert sc.canary["skill-wf"]["mode"] == "canary"
        sc.promote("skill-wf")
        assert sc.canary["skill-wf"]["mode"] == "stable"
        sc.rollback_canary("skill-wf")
        assert sc.canary["skill-wf"]["mode"] == "rolled_back"
        assert sc.canary["skill-wf"]["traffic_percent"] == 0

    def test_multiple_skills_independent(self):
        sc = SkillCanary()
        sc.deploy_canary("skill-a", "1.0.0")
        sc.deploy_canary("skill-b", "2.0.0")
        sc.promote("skill-a")
        assert sc.canary["skill-a"]["mode"] == "stable"
        assert sc.canary["skill-b"]["mode"] == "canary"
