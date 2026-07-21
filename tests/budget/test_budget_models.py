# [A_test] module_id: MOD-GOV_budget_models | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_budget_models
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_budget_models.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.budget_models import (
    BudgetAlert,
    BudgetConsumption,
    BudgetDimension,
    BudgetLevel,
    BudgetPolicy,
    DegradationStep,
    GateDecision,
    GateResult,
    ModelTier,
)


class TestBudgetDimension:
    def test_all_members(self):
        assert BudgetDimension.TOKEN.value == "TOKEN"
        assert BudgetDimension.COST.value == "COST"
        assert BudgetDimension.TIME.value == "TIME"

    def test_member_count(self):
        assert len(BudgetDimension) == 3


class TestBudgetLevel:
    def test_all_members(self):
        assert BudgetLevel.L0_NORMAL.value == 0
        assert BudgetLevel.L6_LOCKDOWN.value == 6

    def test_member_count(self):
        assert len(BudgetLevel) == 7

    def test_ordering(self):
        assert BudgetLevel.L0_NORMAL.value < BudgetLevel.L1_WARNING.value
        assert BudgetLevel.L5_HARD_STOP.value < BudgetLevel.L6_LOCKDOWN.value


class TestGateDecision:
    def test_all_members(self):
        assert GateDecision.ALLOW.value == "ALLOW"
        assert GateDecision.DENY.value == "DENY"
        assert GateDecision.DEGRADE.value == "DEGRADE"
        assert GateDecision.BORROW.value == "BORROW"
        assert GateDecision.NARROW.value == "NARROW"

    def test_member_count(self):
        assert len(GateDecision) == 5


class TestModelTier:
    def test_all_members(self):
        assert ModelTier.PREMIUM.value == "PREMIUM"
        assert ModelTier.STANDARD.value == "STANDARD"
        assert ModelTier.ECONOMY.value == "ECONOMY"
        assert ModelTier.MINIMAL.value == "MINIMAL"

    def test_member_count(self):
        assert len(ModelTier) == 4


class TestBudgetPolicy:
    def test_defaults(self):
        bp = BudgetPolicy()
        assert bp.name == ""
        assert bp.dimension == BudgetDimension.TOKEN
        assert bp.daily_limit == 1_000_000.0
        assert bp.hourly_limit == 100_000.0
        assert bp.per_request_limit == 16_000.0
        assert bp.enabled is True

    def test_custom_values(self):
        bp = BudgetPolicy(
            policy_id="BP-CUSTOM",
            name="Custom Policy",
            dimension=BudgetDimension.COST,
            daily_limit=100.0,
            hourly_limit=10.0,
            per_request_limit=1.0,
        )
        assert bp.policy_id == "BP-CUSTOM"
        assert bp.dimension == BudgetDimension.COST
        assert bp.daily_limit == 100.0

    def test_threshold_ordering(self):
        bp = BudgetPolicy()
        assert bp.warning_threshold < bp.throttle_threshold
        assert bp.throttle_threshold < bp.degrade_threshold
        assert bp.degrade_threshold < bp.emergency_threshold
        assert bp.emergency_threshold < bp.hard_stop_threshold

    def test_auto_uuid(self):
        bp1 = BudgetPolicy()
        bp2 = BudgetPolicy()
        assert bp1.policy_id != bp2.policy_id


class TestBudgetConsumption:
    def test_defaults(self):
        bc = BudgetConsumption()
        assert bc.consumed_daily == 0.0
        assert bc.consumed_hourly == 0.0
        assert bc.consumed_per_request == 0.0
        assert bc.request_count_daily == 0

    def test_custom_policy_id(self):
        bc = BudgetConsumption(policy_id="BP-001", dimension=BudgetDimension.COST)
        assert bc.policy_id == "BP-001"
        assert bc.dimension == BudgetDimension.COST

    def test_auto_uuid(self):
        bc1 = BudgetConsumption()
        bc2 = BudgetConsumption()
        assert bc1.consumption_id != bc2.consumption_id

    def test_reset_timestamps(self):
        bc = BudgetConsumption()
        assert bc.last_reset_daily is not None
        assert bc.last_reset_hourly is not None


class TestGateResult:
    def test_creation(self):
        gr = GateResult(request_id="req-1", decision=GateDecision.ALLOW)
        assert gr.request_id == "req-1"
        assert gr.decision == GateDecision.ALLOW
        assert gr.budget_level == BudgetLevel.L0_NORMAL
        assert gr.reason == ""

    def test_deny_result(self):
        gr = GateResult(
            request_id="req-2",
            decision=GateDecision.DENY,
            reason="hard stop",
            budget_level=BudgetLevel.L5_HARD_STOP,
        )
        assert gr.decision == GateDecision.DENY
        assert gr.budget_level == BudgetLevel.L5_HARD_STOP


class TestBudgetAlertModel:
    def test_defaults(self):
        ba = BudgetAlert()
        assert ba.acknowledged is False
        assert ba.dimension == BudgetDimension.TOKEN
        assert ba.level == BudgetLevel.L0_NORMAL

    def test_custom(self):
        ba = BudgetAlert(
            alert_id="a-1",
            policy_id="BP-001",
            dimension=BudgetDimension.COST,
            level=BudgetLevel.L2_THROTTLED,
            message="over limit",
        )
        assert ba.alert_id == "a-1"
        assert ba.level == BudgetLevel.L2_THROTTLED


class TestDegradationStep:
    def test_creation(self):
        ds = DegradationStep(
            step_id=0,
            description="Normal",
            model_tier=ModelTier.PREMIUM,
            auto_trigger_level=BudgetLevel.L0_NORMAL,
        )
        assert ds.step_id == 0
        assert ds.max_tokens_per_request == 16_000
        assert ds.cooldown_seconds == 300

    def test_custom_params(self):
        ds = DegradationStep(
            step_id=3,
            description="Emergency",
            model_tier=ModelTier.MINIMAL,
            auto_trigger_level=BudgetLevel.L4_EMERGENCY,
            max_tokens_per_request=2000,
            cooldown_seconds=600,
        )
        assert ds.max_tokens_per_request == 2000
        assert ds.cooldown_seconds == 600
