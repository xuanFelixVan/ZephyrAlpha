# [A_test] module_id: MOD-GOV_skill_router | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_system_master/blueprint.md | §
# [MODULE] tests.test_skill_router
# [INVARIANTS] SkillRouter uses FALLBACK_TASK_ROUTING when registry YAML missing
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] route returns (role, domain) tuple always
# [TESTS] tests/test_skill_router.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.autonomy_core.skills.skill_router import ConstructionStage, SkillRouter, TriggerRouter

_MISSING_REGISTRY = Path("/nonexistent/skill_registry_for_test.yaml")


@pytest.fixture
def fallback_router():
    return SkillRouter(registry_path=_MISSING_REGISTRY)


class TestConstructionStage:
    def test_enum_values(self):
        assert ConstructionStage.IDEA.value == "idea"
        assert ConstructionStage.PRE_AUDIT.value == "pre_audit"
        assert ConstructionStage.BLUEPRINT.value == "blueprint"
        assert ConstructionStage.CONSTRUCTION.value == "construction"
        assert ConstructionStage.VERIFICATION.value == "verification"
        assert ConstructionStage.POST_AUDIT.value == "post_audit"

    def test_from_label_idea(self):
        assert ConstructionStage.from_label("想法") == ConstructionStage.IDEA
        assert ConstructionStage.from_label("草稿") == ConstructionStage.IDEA

    def test_from_label_construction(self):
        assert ConstructionStage.from_label("施工") == ConstructionStage.CONSTRUCTION
        assert ConstructionStage.from_label("实现") == ConstructionStage.CONSTRUCTION

    def test_from_label_unknown(self):
        assert ConstructionStage.from_label("unknown_label") is None

    def test_from_label_empty(self):
        assert ConstructionStage.from_label("") is None

    def test_from_label_none_type(self):
        assert ConstructionStage.from_label(None) is None


class TestSkillRouterInstantiation:
    def test_default_construction(self):
        router = SkillRouter()
        assert router.registry_path is not None

    def test_custom_registry_path(self):
        custom_path = Path("/tmp/fake_registry.yaml")
        router = SkillRouter(registry_path=custom_path)
        assert router.registry_path == custom_path

    def test_trigger_router_alias(self):
        assert TriggerRouter is SkillRouter


class TestRouteFallback:
    def test_route_with_stage_idea(self, fallback_router):
        role, domain = fallback_router.route(ConstructionStage.IDEA, "unrelated xyz")
        assert role == "architect"
        assert domain == "master-blueprint"

    def test_route_with_stage_post_audit(self, fallback_router):
        role, domain = fallback_router.route(ConstructionStage.POST_AUDIT, "unrelated xyz")
        assert role == "governor"
        assert domain == "drift-detector"

    def test_route_with_task_keyword_database(self, fallback_router):
        role, domain = fallback_router.route(None, "database migration task")
        assert domain == "database-specialist"
        assert role == "implementer"

    def test_route_with_task_keyword_gate(self, fallback_router):
        role, domain = fallback_router.route(None, "update gate policy")
        assert domain == "gate-specialist"
        assert role == "governor"

    def test_route_with_task_keyword_blueprint(self, fallback_router):
        role, domain = fallback_router.route(None, "create blueprint for new module")
        assert domain == "master-blueprint"
        assert role == "architect"

    def test_route_no_stage_no_keyword(self, fallback_router):
        role, domain = fallback_router.route(None, "random unrelated xyz")
        assert role == "implementer"
        assert domain is None

    def test_route_empty_task_description(self, fallback_router):
        role, domain = fallback_router.route(None, "")
        assert role == "implementer"
        assert domain is None

    def test_route_stage_fills_role_when_no_task_match(self, fallback_router):
        role, domain = fallback_router.route(ConstructionStage.VERIFICATION, "unrelated xyz")
        assert role == "governor"

    def test_route_stage_construction(self, fallback_router):
        role, domain = fallback_router.route(ConstructionStage.CONSTRUCTION, "unrelated xyz")
        assert role == "implementer"

    def test_route_task_keyword_overrides_stage_role(self, fallback_router):
        role, domain = fallback_router.route(ConstructionStage.IDEA, "update gate policy")
        assert domain == "gate-specialist"
        assert role == "governor"


class TestListRegisteredSkills:
    def test_returns_dict_when_no_registry(self):
        router = SkillRouter(registry_path=_MISSING_REGISTRY)
        result = router.list_registered_skills()
        assert isinstance(result, dict)

    def test_returns_empty_when_file_missing(self):
        router = SkillRouter(registry_path=_MISSING_REGISTRY)
        result = router.list_registered_skills()
        assert result == {}

    def test_real_registry_returns_skills(self):
        router = SkillRouter()
        result = router.list_registered_skills()
        assert isinstance(result, dict)
        assert len(result) > 0


class TestMatchTaskRoutingFallback:
    def test_matches_mcp_keyword(self, fallback_router):
        result = fallback_router.match_task_routing("set up mcp server")
        assert result is not None
        assert result[0] == "mcp-specialist"

    def test_matches_knowledge_keyword(self, fallback_router):
        result = fallback_router.match_task_routing("update knowledge base")
        assert result is not None
        assert result[0] == "knowledge-specialist"

    def test_no_match_for_unrelated(self, fallback_router):
        result = fallback_router.match_task_routing("paint a picture")
        assert result is None

    def test_empty_string_no_match(self, fallback_router):
        result = fallback_router.match_task_routing("")
        assert result is None


class TestMatchDomainFallback:
    def test_returns_domain_on_match(self, fallback_router):
        result = fallback_router.match_domain("run database migration")
        assert result == "database-specialist"

    def test_returns_none_on_no_match(self, fallback_router):
        result = fallback_router.match_domain("eat lunch")
        assert result is None
