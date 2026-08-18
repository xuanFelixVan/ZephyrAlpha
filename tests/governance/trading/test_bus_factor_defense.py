# [A_test] module_id: MOD-GOV_bus_factor_defense | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-356 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_bus_factor_defense
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] evaluate_bus_factor sets risk based on owner count; onboarding_complete requires all 3 flags
# [MODIFY-GUARD] Changes must sync with bus_factor_defense.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_bus_factor_defense.py
# [A_module] module_id=MOD-TEST-356 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.factor.bus_factor_defense import (
    BusFactorRisk,
    DecisionLog,
    ModuleOwnership,
    OpsRunbook,
    create_decision_log,
    evaluate_bus_factor,
    generate_runbook,
)


class TestBusFactorRisk:
    def test_enum_values(self):
        assert BusFactorRisk.SAFE.value == "SAFE"
        assert BusFactorRisk.AT_RISK.value == "AT_RISK"
        assert BusFactorRisk.DANGER.value == "DANGER"


class TestModuleOwnership:
    def test_defaults(self):
        m = ModuleOwnership(module_id="MOD-001")
        assert m.owners == []
        assert m.bus_factor == 0
        assert m.risk == BusFactorRisk.DANGER

    def test_onboarding_complete_all_true(self):
        m = ModuleOwnership(
            module_id="MOD-001",
            onboarding_readme=True,
            onboarding_diagram=True,
            onboarding_key_funcs=True,
        )
        assert m.onboarding_complete is True

    def test_onboarding_complete_partial(self):
        m = ModuleOwnership(
            module_id="MOD-001",
            onboarding_readme=True,
            onboarding_diagram=False,
            onboarding_key_funcs=True,
        )
        assert m.onboarding_complete is False

    def test_onboarding_complete_none(self):
        m = ModuleOwnership(module_id="MOD-001")
        assert m.onboarding_complete is False

    def test_onboarding_time_estimate_complete(self):
        m = ModuleOwnership(
            module_id="MOD-001",
            onboarding_readme=True,
            onboarding_diagram=True,
            onboarding_key_funcs=True,
        )
        assert "15min" in m.onboarding_time_estimate

    def test_onboarding_time_estimate_incomplete(self):
        m = ModuleOwnership(module_id="MOD-001")
        assert "INCOMPLETE" in m.onboarding_time_estimate


class TestCheckBusFactor:
    def test_zero_owners_danger(self):
        m = ModuleOwnership(module_id="MOD-001")
        result = evaluate_bus_factor(m)
        assert result.risk == BusFactorRisk.DANGER
        assert result.bus_factor == 0

    def test_one_owner_at_risk(self):
        m = ModuleOwnership(module_id="MOD-001", owners=["alice"])
        result = evaluate_bus_factor(m)
        assert result.risk == BusFactorRisk.AT_RISK
        assert result.bus_factor == 1

    def test_two_owners_safe(self):
        m = ModuleOwnership(module_id="MOD-001", owners=["alice", "bob"])
        result = evaluate_bus_factor(m)
        assert result.risk == BusFactorRisk.SAFE
        assert result.bus_factor == 2

    def test_many_owners_safe(self):
        m = ModuleOwnership(module_id="MOD-001", owners=["a", "b", "c", "d"])
        result = evaluate_bus_factor(m)
        assert result.risk == BusFactorRisk.SAFE
        assert result.bus_factor == 4


class TestDecisionLog:
    def test_creation(self):
        dl = DecisionLog(decision_id="KBG-001", problem="test problem")
        assert dl.decision_id == "KBG-001"
        assert dl.decision == ""

    def test_with_options(self):
        dl = DecisionLog(
            decision_id="KBG-002",
            problem="p",
            options=["opt-a", "opt-b"],
            decision="opt-a",
        )
        assert len(dl.options) == 2


class TestCreateDecisionLog:
    def test_creates_with_review_date(self):
        dl = create_decision_log(
            decision_id="KBG-010",
            problem="test",
            options=["a", "b"],
            decision="a",
            rationale="best option",
        )
        assert dl.decision_id == "KBG-010"
        assert dl.review_date is not None
        assert len(dl.review_date) > 0

    def test_custom_review_days(self):
        dl = create_decision_log(
            decision_id="KBG-011",
            problem="p",
            options=[],
            decision="d",
            rationale="r",
            review_days=30,
        )
        assert dl.review_date is not None


class TestOpsRunbook:
    def test_creation(self):
        rb = OpsRunbook(module_id="MOD-001")
        assert rb.auto_generated is True

    def test_custom_content(self):
        rb = OpsRunbook(module_id="MOD-001", content="Custom content")
        assert rb.content == "Custom content"


class TestGenerateRunbook:
    def test_generates_with_content(self):
        rb = generate_runbook("MOD-001", "Step 1: Do thing")
        assert rb.module_id == "MOD-001"
        assert rb.content == "Step 1: Do thing"
        assert rb.auto_generated is True
        assert len(rb.generated_at) > 0

    def test_generates_default_content(self):
        rb = generate_runbook("MOD-002")
        assert "MOD-002" in rb.content
        assert rb.auto_generated is True
