# [A_test] module_id: MOD-GOV_budget_engine_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §2-4
# [MODULE] tests.test_budget_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_budget_engine_root.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.budget_engine import BudgetEngine
from zephyr.governance.ops_governance.budget_models import (
    BudgetDimension,
    BudgetPolicy,
    GateDecision,
    ModelTier,
)


class TestBudgetEngineInstantiation:
    def test_default_policies(self):
        engine = BudgetEngine()
        assert engine.get_active_policy(BudgetDimension.TOKEN) is not None
        assert engine.get_active_policy(BudgetDimension.COST) is not None
        assert engine.get_active_policy(BudgetDimension.TIME) is not None

    def test_default_consumption_summary(self):
        engine = BudgetEngine()
        summary = engine.get_consumption_summary()
        assert len(summary) == 3


class TestBudgetEnginePreFlight:
    def test_pre_flight_allow(self):
        engine = BudgetEngine()
        result = engine.pre_flight_check("req-001", estimated_tokens=100, estimated_cost=0.01)
        assert result.decision == GateDecision.ALLOW

    def test_pre_flight_narrow_per_request_limit(self):
        engine = BudgetEngine()
        result = engine.pre_flight_check("req-002", estimated_tokens=100_000)
        assert result.decision == GateDecision.NARROW

    def test_pre_flight_deny_hard_stop(self):
        engine = BudgetEngine()
        policy = engine.get_active_policy(BudgetDimension.TOKEN)
        engine.record_consumption(
            policy.policy_id,
            tokens=int(policy.daily_limit * policy.hard_stop_threshold) + 1,
            cost=0.0,
            time_minutes=0.0,
        )
        result = engine.pre_flight_check("req-003", estimated_tokens=1)
        assert result.decision == GateDecision.DENY

    def test_pre_flight_degrade(self):
        engine = BudgetEngine()
        policy = engine.get_active_policy(BudgetDimension.TOKEN)
        engine.record_consumption(
            policy.policy_id,
            tokens=int(policy.daily_limit * policy.emergency_threshold) + 1,
            cost=0.0,
            time_minutes=0.0,
        )
        result = engine.pre_flight_check("req-004", estimated_tokens=1)
        assert result.decision in (GateDecision.DEGRADE, GateDecision.DENY)


class TestBudgetEngineRecordConsumption:
    def test_record_consumption_token(self):
        engine = BudgetEngine()
        policy = engine.get_active_policy(BudgetDimension.TOKEN)
        engine.record_consumption(policy.policy_id, tokens=500, cost=0.0, time_minutes=0.0)
        summary = engine.get_consumption_summary()
        assert summary[policy.policy_id]["daily"] == 500.0

    def test_record_consumption_cost(self):
        engine = BudgetEngine()
        policy = engine.get_active_policy(BudgetDimension.COST)
        engine.record_consumption(policy.policy_id, tokens=0, cost=0.5, time_minutes=0.0)
        summary = engine.get_consumption_summary()
        assert summary[policy.policy_id]["daily"] == 0.5

    def test_record_consumption_time(self):
        engine = BudgetEngine()
        policy = engine.get_active_policy(BudgetDimension.TIME)
        engine.record_consumption(policy.policy_id, tokens=0, cost=0.0, time_minutes=10.0)
        summary = engine.get_consumption_summary()
        assert summary[policy.policy_id]["daily"] == 10.0

    def test_record_consumption_unknown_policy(self):
        engine = BudgetEngine()
        engine.record_consumption("nonexistent", tokens=100, cost=0.0, time_minutes=0.0)
        summary = engine.get_consumption_summary()
        assert "nonexistent" not in summary


class TestBudgetEngineClaimBudget:
    def test_try_claim_success(self):
        engine = BudgetEngine()
        ok, version, msg = engine.try_claim_budget("prov-1", BudgetDimension.COST, 1.0)
        assert ok is True
        assert version >= 0
        assert msg == "OK"

    def test_try_claim_version_mismatch(self):
        engine = BudgetEngine()
        v = engine.get_consumption_version(BudgetDimension.COST)
        ok, _, _ = engine.try_claim_budget("prov-1", BudgetDimension.COST, 1.0, expected_version=v)
        assert ok is True
        ok2, _, msg2 = engine.try_claim_budget("prov-2", BudgetDimension.COST, 1.0, expected_version=v)
        assert ok2 is False
        assert "Version mismatch" in msg2

    def test_try_claim_insufficient_daily(self):
        engine = BudgetEngine()
        policy = engine.get_active_policy(BudgetDimension.COST)
        ok, _, _ = engine.try_claim_budget("prov-1", BudgetDimension.COST, policy.daily_limit + 1)
        assert ok is False

    def test_commit_claim(self):
        engine = BudgetEngine()
        engine.try_claim_budget("prov-1", BudgetDimension.COST, 1.0)
        result = engine.commit_claim("prov-1", BudgetDimension.COST, 0.8)
        assert result is True

    def test_rollback_claim(self):
        engine = BudgetEngine()
        engine.try_claim_budget("prov-1", BudgetDimension.COST, 1.0)
        result = engine.rollback_claim("prov-1", BudgetDimension.COST)
        assert result is True

    def test_rollback_claim_no_existing(self):
        engine = BudgetEngine()
        result = engine.rollback_claim("prov-none", BudgetDimension.COST)
        assert result is True


class TestBudgetEngineDegradation:
    def test_initial_degradation_level(self):
        engine = BudgetEngine()
        tier, max_tok = engine.get_model_router_recommendation()
        assert tier == ModelTier.PREMIUM

    def test_advance_degradation(self):
        engine = BudgetEngine()
        assert engine.advance_degradation() is True
        tier, _ = engine.get_model_router_recommendation()
        assert tier == ModelTier.STANDARD

    def test_advance_degradation_max(self):
        engine = BudgetEngine()
        for _ in range(10):
            engine.advance_degradation()
        assert engine.advance_degradation() is False

    def test_retreat_degradation(self):
        engine = BudgetEngine()
        engine.advance_degradation()
        assert engine.retreat_degradation() is True
        tier, _ = engine.get_model_router_recommendation()
        assert tier == ModelTier.PREMIUM

    def test_retreat_degradation_min(self):
        engine = BudgetEngine()
        assert engine.retreat_degradation() is False


class TestBudgetEngineAlerts:
    def test_get_alerts_empty(self):
        engine = BudgetEngine()
        assert engine.get_alerts() == []

    def test_acknowledge_nonexistent_alert(self):
        engine = BudgetEngine()
        assert engine.acknowledge_alert("nonexistent") is False


class TestBudgetEngineRegisterPolicy:
    def test_register_custom_policy(self):
        engine = BudgetEngine()
        custom = BudgetPolicy(
            policy_id="custom-001",
            name="Custom",
            dimension=BudgetDimension.TOKEN,
            daily_limit=500.0,
            hourly_limit=50.0,
            per_request_limit=10.0,
        )
        engine.register_policy(custom)
        assert engine.get_active_policy(BudgetDimension.TOKEN).policy_id == "custom-001"


class TestBudgetEngineComputeHash:
    def test_hash_deterministic(self):
        engine = BudgetEngine()
        h1 = engine.compute_hash()
        h2 = engine.compute_hash()
        assert h1 == h2

    def test_hash_changes_after_consumption(self):
        engine = BudgetEngine()
        h1 = engine.compute_hash()
        policy = engine.get_active_policy(BudgetDimension.TOKEN)
        engine.record_consumption(policy.policy_id, tokens=100, cost=0.0, time_minutes=0.0)
        h2 = engine.compute_hash()
        assert h1 != h2


class TestBudgetEngineConsumptionVersion:
    def test_initial_version(self):
        engine = BudgetEngine()
        v = engine.get_consumption_version(BudgetDimension.TOKEN)
        assert v == 0

    def test_version_after_claim(self):
        engine = BudgetEngine()
        engine.try_claim_budget("prov-1", BudgetDimension.TOKEN, 100)
        v = engine.get_consumption_version(BudgetDimension.TOKEN)
        assert v == 1

    def test_version_no_policy(self):
        engine = BudgetEngine()
        engine.policies.pop(BudgetDimension.TIME, None)
        v = engine.get_consumption_version(BudgetDimension.TIME)
        assert v == -1
