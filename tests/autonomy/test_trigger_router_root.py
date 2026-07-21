# [A_test] module_id: MOD-GOV_trigger_router_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_trigger_router
# [INVARIANTS] route always returns (role, domain); role is never None
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_trigger_router_root.py
# [TTL] task_bound

from zephyr.autonomy_core.trigger_router import ConstructionStage, TriggerRouter


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

    def test_from_label_pre_audit(self):
        assert ConstructionStage.from_label("审计（施工前）") == ConstructionStage.PRE_AUDIT
        assert ConstructionStage.from_label("审计(施工前)") == ConstructionStage.PRE_AUDIT

    def test_from_label_blueprint(self):
        assert ConstructionStage.from_label("蓝图") == ConstructionStage.BLUEPRINT
        assert ConstructionStage.from_label("设计") == ConstructionStage.BLUEPRINT

    def test_from_label_construction(self):
        assert ConstructionStage.from_label("施工") == ConstructionStage.CONSTRUCTION
        assert ConstructionStage.from_label("实现") == ConstructionStage.CONSTRUCTION

    def test_from_label_verification(self):
        assert ConstructionStage.from_label("验收") == ConstructionStage.VERIFICATION
        assert ConstructionStage.from_label("验证") == ConstructionStage.VERIFICATION

    def test_from_label_post_audit(self):
        assert ConstructionStage.from_label("审计（施工后）") == ConstructionStage.POST_AUDIT
        assert ConstructionStage.from_label("审计(施工后)") == ConstructionStage.POST_AUDIT

    def test_from_label_unknown_returns_none(self):
        assert ConstructionStage.from_label("unknown_label") is None

    def test_from_label_empty_returns_none(self):
        assert ConstructionStage.from_label("") is None


class TestTriggerRouterInstantiation:
    def test_init(self):
        router = TriggerRouter()
        assert router.STAGE_ROUTING is not None
        assert len(router.STAGE_ROUTING) == 6

    def test_task_routing_populated(self):
        router = TriggerRouter()
        assert len(router.TASK_ROUTING) > 0


class TestRoute:
    def setup_method(self):
        self.router = TriggerRouter()

    def test_route_construction_stage_with_task(self):
        role, domain = self.router.route(ConstructionStage.CONSTRUCTION, "implement the module")
        assert role == "implementer"

    def test_route_idea_stage(self):
        role, domain = self.router.route(ConstructionStage.IDEA, "new feature idea")
        assert role == "architect"
        assert domain == "master-blueprint"

    def test_route_pre_audit_stage(self):
        role, domain = self.router.route(ConstructionStage.PRE_AUDIT, "preliminary review")
        assert role == "governor"
        assert domain == "gate-engine"

    def test_route_post_audit_stage(self):
        role, domain = self.router.route(ConstructionStage.POST_AUDIT, "post audit check")
        assert role == "governor"
        assert domain == "drift-detector"

    def test_route_none_stage_with_task_routing(self):
        role, domain = self.router.route(None, "database migration task")
        assert domain == "database-specialist"
        assert role == "implementer"

    def test_route_none_stage_no_match(self):
        role, domain = self.router.route(None, "random task with no keywords")
        assert role == "implementer"

    def test_route_gate_task(self):
        role, domain = self.router.route(None, "update gate policy")
        assert domain == "gate-specialist"
        assert role == "governor"

    def test_route_blueprint_task(self):
        role, domain = self.router.route(None, "create blueprint for module")
        assert domain == "master-blueprint"
        assert role == "architect"

    def test_route_mcp_task(self):
        role, domain = self.router.route(None, "build mcp server")
        assert domain == "mcp-specialist"

    def test_route_knowledge_task(self):
        role, domain = self.router.route(None, "update knowledge base")
        assert domain == "knowledge-specialist"

    def test_route_feedback_task(self):
        role, domain = self.router.route(None, "implement feedback loop")
        assert domain == "feedback-specialist"

    def test_route_permission_task(self):
        role, domain = self.router.route(None, "configure permission rbac")
        assert domain == "agent-specialist"
        assert role == "governor"

    def test_route_stage_overrides_domain_default_when_task_matches(self):
        role, domain = self.router.route(ConstructionStage.CONSTRUCTION, "database schema change")
        assert domain == "database-specialist"

    def test_route_empty_task_description(self):
        role, domain = self.router.route(ConstructionStage.CONSTRUCTION, "")
        assert role is not None

    def test_route_verification_stage(self):
        role, domain = self.router.route(ConstructionStage.VERIFICATION, "verify module")
        assert role == "governor"

    def test_route_blueprint_stage_with_domain_match(self):
        role, domain = self.router.route(ConstructionStage.BLUEPRINT, "design database blueprint")
        assert domain == "database-specialist"


class TestMatchTaskRouting:
    def setup_method(self):
        self.router = TriggerRouter()

    def test_match_database(self):
        result = self.router._match_task_routing("run database migration")
        assert result is not None
        assert result[0] == "database-specialist"

    def test_match_audit(self):
        result = self.router._match_task_routing("perform audit compliance check")
        assert result is not None
        assert result[0] == "drift-detector"

    def test_no_match(self):
        result = self.router._match_task_routing("random text nothing matches")
        assert result is None

    def test_match_case_insensitive(self):
        result = self.router._match_task_routing("SQL MIGRATION")
        assert result is not None
        assert result[0] == "database-specialist"


class TestMatchDomain:
    def setup_method(self):
        self.router = TriggerRouter()

    def test_match_domain_returns_domain(self):
        result = self.router._match_domain("database migration")
        assert result == "database-specialist"

    def test_match_domain_no_match(self):
        result = self.router._match_domain("nothing here")
        assert result is None
