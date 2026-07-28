# [A_test] module_id: MOD-GOV_pipeline_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_pipeline_bridge
# [INVARIANTS] SkillInjectionResult.loaded defaults False; to_context_string returns "" when not loaded
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_pipeline_bridge.py
# [TTL] task_bound

from unittest.mock import MagicMock, patch

from zephyr.autonomy_core.integration.pipeline_bridge import (
    PipelineSkillBridge,
    SkillContextInjector,
    SkillInjectionResult,
)
from zephyr.autonomy_core.trigger_router import ConstructionStage


class TestSkillInjectionResult:
    def test_default_values(self):
        result = SkillInjectionResult(
            skill_id="test",
            domain_skill_id=None,
            role_skill_id=None,
            l0_constitution={},
        )
        assert result.loaded is False
        assert result.l2_domain_body == ""
        assert result.l2_role_body == ""
        assert result.token_budget == {}

    def test_to_context_string_not_loaded(self):
        result = SkillInjectionResult(
            skill_id="test",
            domain_skill_id=None,
            role_skill_id=None,
            l0_constitution={},
            loaded=False,
        )
        assert result.to_context_string() == ""

    def test_to_context_string_loaded_with_bodies(self):
        result = SkillInjectionResult(
            skill_id="d+r",
            domain_skill_id="domain_skill",
            role_skill_id="role_skill",
            l0_constitution={},
            l2_domain_body="domain content",
            l2_role_body="role content",
            loaded=True,
        )
        ctx = result.to_context_string()
        assert "Domain Skill: domain_skill" in ctx
        assert "domain content" in ctx
        assert "Role Skill: role_skill" in ctx
        assert "role content" in ctx

    def test_to_context_string_loaded_no_bodies(self):
        result = SkillInjectionResult(
            skill_id="d+r",
            domain_skill_id="domain_skill",
            role_skill_id="role_skill",
            l0_constitution={},
            loaded=True,
        )
        ctx = result.to_context_string()
        assert ctx == ""

    def test_to_context_string_only_domain_body(self):
        result = SkillInjectionResult(
            skill_id="d+r",
            domain_skill_id="domain_skill",
            role_skill_id="role_skill",
            l0_constitution={},
            l2_domain_body="domain only",
            loaded=True,
        )
        ctx = result.to_context_string()
        assert "domain only" in ctx
        assert "Role Skill" not in ctx


class TestSkillContextInjector:
    def test_instantiation_default_loader(self):
        injector = SkillContextInjector()
        assert injector.loader is not None

    def test_instantiation_custom_loader(self):
        mock_loader = MagicMock()
        injector = SkillContextInjector(loader=mock_loader)
        assert injector.loader is mock_loader

    def test_inject_success(self):
        mock_loader = MagicMock()
        mock_loader.progressive_load.side_effect = [
            {"l1": {"name": "domain"}, "l2": "domain body", "l3_available": []},
            {"l1": {"name": "role"}, "l2": "role body", "l3_available": []},
        ]
        mock_loader.load_l0.return_value = {"constitution": "test"}
        mock_loader.check_token_budget.return_value = {"total": 100}
        injector = SkillContextInjector(loader=mock_loader)

        result = injector.inject("domain_skill", "role_skill")
        assert result.loaded is True
        assert result.domain_skill_id == "domain_skill"
        assert result.role_skill_id == "role_skill"
        assert result.l2_domain_body == "domain body"
        assert result.l2_role_body == "role body"

    def test_inject_failure_returns_not_loaded(self):
        mock_loader = MagicMock()
        mock_loader.progressive_load.side_effect = Exception("load failed")
        injector = SkillContextInjector(loader=mock_loader)

        result = injector.inject("bad_domain", "bad_role")
        assert result.loaded is False
        assert result.l0_constitution == {}

    def test_inject_with_l3(self):
        mock_loader = MagicMock()
        mock_loader.progressive_load.side_effect = [
            {"l1": {}, "l2": "domain body", "l3_available": ["l3 ref 1"]},
            {"l1": {}, "l2": "role body", "l3_available": ["l3 ref 2"]},
        ]
        mock_loader.load_l0.return_value = {}
        mock_loader.check_token_budget.return_value = {}
        injector = SkillContextInjector(loader=mock_loader)

        result = injector.inject("d", "r", load_l3=True)
        assert result.loaded is True
        assert "l3 ref 1" in result.injection_context or "L3 References" in result.injection_context

    def test_inject_single_success(self):
        mock_loader = MagicMock()
        mock_loader.progressive_load.return_value = {"l1": {"name": "skill"}, "l2": "skill body"}
        mock_loader.load_l0.return_value = {}
        injector = SkillContextInjector(loader=mock_loader)

        result = injector.inject_single("my_skill")
        assert result.loaded is True
        assert result.domain_skill_id == "my_skill"
        assert result.role_skill_id is None

    def test_inject_single_failure(self):
        mock_loader = MagicMock()
        mock_loader.progressive_load.side_effect = Exception("fail")
        injector = SkillContextInjector(loader=mock_loader)

        result = injector.inject_single("bad_skill")
        assert result.loaded is False


class TestPipelineSkillBridge:
    def test_instantiation(self):
        bridge = PipelineSkillBridge()
        assert bridge.router is not None
        assert bridge.injector is not None

    def test_stage_map_populated(self):
        bridge = PipelineSkillBridge()
        assert "construction" in bridge.stage_map
        assert bridge.stage_map["construction"] == ConstructionStage.CONSTRUCTION

    def test_inject_for_task_with_stage(self):
        bridge = PipelineSkillBridge()
        with patch.object(bridge.injector, "inject") as mock_inject:
            mock_inject.return_value = SkillInjectionResult(
                skill_id="test",
                domain_skill_id="d",
                role_skill_id="r",
                l0_constitution={},
                loaded=True,
            )
            with patch.object(bridge.injector.loader, "_load_registry") as mock_reg:
                mock_reg.return_value = {
                    "skills": {
                        "domain": {"domain-1": {"name": "database-specialist"}},
                        "role": {"role-1": {"name": "implementer"}},
                    }
                }
                result = bridge.inject_for_task("database migration", stage="construction")
                assert result is not None

    def test_inject_for_task_unknown_stage(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task("random task", stage="unknown_stage_xyz")
        assert result is not None

    def test_inject_for_task_no_stage(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task("random task without stage")
        assert result is not None

    def test_inject_for_task_empty_description(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task("", stage="construction")
        assert result is not None

    def test_inject_for_task_none_stage(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task("database migration", stage=None)
        assert result is not None

    def test_inject_for_task_idea_stage(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task("new feature idea", stage="idea")
        assert result is not None

    def test_inject_for_task_blueprint_stage(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task("design blueprint", stage="blueprint")
        assert result is not None

    def test_inject_for_task_audit_stage(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task("post audit review", stage="post_audit")
        assert result is not None
