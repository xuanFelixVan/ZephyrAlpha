# [A_test] module_id: MOD-GOV_budget_engine_budget_enforcer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-457 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.budget_enforcer.test_budget_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

from __future__ import annotations

"""Test suite: budget_engine"""


import pytest

from zephyr.governance.ops_governance.budget_engine import BudgetEngine
from zephyr.governance.ops_governance.budget_models import (
    BudgetAlert,
    BudgetDimension,
    BudgetLevel,
    BudgetPolicy,
    GateDecision,
    GateResult,
    ModelTier,
)


@pytest.fixture
def engine() -> BudgetEngine:
    return BudgetEngine()


class TestBudgetEngineInstantiation:
    def test_creates_with_defaults(self) -> None:
        eng = BudgetEngine()
        assert eng is not None

    def test_has_default_policies(self, engine: BudgetEngine) -> None:
        for dim in BudgetDimension:
            policy = engine.get_active_policy(dim)
            assert policy is not None, f"Missing default policy for {dim.name}"

    def test_default_policy_token_limits(self, engine: BudgetEngine) -> None:
        policy = engine.get_active_policy(BudgetDimension.TOKEN)
        assert policy is not None
        assert policy.daily_limit == 1_000_000
        assert policy.hourly_limit == 100_000
        assert policy.per_request_limit == 16_000

    def test_default_policy_cost_limits(self, engine: BudgetEngine) -> None:
        policy = engine.get_active_policy(BudgetDimension.COST)
        assert policy is not None
        # ARCH-303（2026-08-31 校准）：单位=元人民币，对齐 Owner sanction 口径
        assert policy.daily_limit == 10.0
        assert policy.hourly_limit == 3.0
        assert policy.per_request_limit == 0.5

    def test_default_policy_time_limits(self, engine: BudgetEngine) -> None:
        policy = engine.get_active_policy(BudgetDimension.TIME)
        assert policy is not None
        assert policy.daily_limit == 480.0
        assert policy.hourly_limit == 60.0
        assert policy.per_request_limit == 5.0


class TestPreFlightCheck:
    def test_allow_when_budget_available(self, engine: BudgetEngine) -> None:
        result = engine.pre_flight_check("req-001", estimated_tokens=100, estimated_cost=0.01)
        assert isinstance(result, GateResult)
        assert result.decision == GateDecision.ALLOW
        assert result.reason == "OK"

    def test_narrow_when_per_request_exceeded(self, engine: BudgetEngine) -> None:
        result = engine.pre_flight_check("req-002", estimated_tokens=20_000, estimated_cost=0.0)
        assert result.decision == GateDecision.NARROW
        assert "Per-request limit exceeded" in result.reason

    def test_allow_zero_request(self, engine: BudgetEngine) -> None:
        result = engine.pre_flight_check("req-003")
        assert result.decision == GateDecision.ALLOW

    def test_result_has_request_id(self, engine: BudgetEngine) -> None:
        result = engine.pre_flight_check("req-004")
        assert result.request_id == "req-004"

    def test_result_has_budget_level(self, engine: BudgetEngine) -> None:
        result = engine.pre_flight_check("req-005")
        assert isinstance(result.budget_level, BudgetLevel)

    def test_deny_when_daily_consumed_past_hard_stop(self, engine: BudgetEngine) -> None:
        token_policy = engine.get_active_policy(BudgetDimension.TOKEN)
        assert token_policy is not None
        engine.record_consumption(
            token_policy.policy_id,
            tokens=int(token_policy.daily_limit * 0.99),
            cost=0.0,
            time_minutes=0.0,
        )
        result = engine.pre_flight_check("req-006", estimated_tokens=100)
        assert result.decision == GateDecision.DENY

    def test_deny_when_cost_daily_past_hard_stop(self, engine: BudgetEngine) -> None:
        """ARCH-303：COST 为预算硬门主维度——元成本日耗≥hard_stop 即 DENY（与 token 无关）。"""
        cost_policy = engine.get_active_policy(BudgetDimension.COST)
        assert cost_policy is not None
        engine.record_consumption(
            cost_policy.policy_id,
            tokens=0,
            cost=cost_policy.daily_limit * 0.99,
            time_minutes=0.0,
        )
        result = engine.pre_flight_check("req-cost-001", estimated_tokens=100, estimated_cost=0.01)
        assert result.decision == GateDecision.DENY
        assert "COST" in result.reason

    def test_degrade_when_daily_consumed_past_emergency(self, engine: BudgetEngine) -> None:
        cost_policy = engine.get_active_policy(BudgetDimension.COST)
        assert cost_policy is not None
        engine.record_consumption(
            cost_policy.policy_id,
            tokens=0,
            cost=cost_policy.daily_limit * 0.96,
            time_minutes=0.0,
        )
        result = engine.pre_flight_check("req-007", estimated_tokens=0, estimated_cost=0.01)
        assert result.decision in {GateDecision.DEGRADE, GateDecision.DENY}

    def test_gate_history_recorded(self, engine: BudgetEngine) -> None:
        engine.pre_flight_check("req-008")
        engine.pre_flight_check("req-009")
        assert len(engine.gate_history) == 2


class TestBudgetAlert:
    def test_create_alert(self) -> None:
        alert = BudgetAlert(
            policy_id="BP-TOKEN-001",
            dimension=BudgetDimension.TOKEN,
            level=BudgetLevel.L1_WARNING,
            message="Token usage at 75%",
        )
        assert alert.policy_id == "BP-TOKEN-001"
        assert alert.dimension == BudgetDimension.TOKEN
        assert alert.level == BudgetLevel.L1_WARNING
        assert alert.acknowledged is False
        assert alert.alert_id != ""

    def test_get_alerts_empty(self, engine: BudgetEngine) -> None:
        alerts = engine.get_alerts()
        assert isinstance(alerts, list)

    def test_acknowledge_nonexistent_alert(self, engine: BudgetEngine) -> None:
        result = engine.acknowledge_alert("nonexistent-id")
        assert result is False

    def test_acknowledge_existing_alert(self, engine: BudgetEngine) -> None:
        alert = BudgetAlert(
            policy_id="BP-TOKEN-001",
            dimension=BudgetDimension.TOKEN,
            level=BudgetLevel.L1_WARNING,
            message="Test alert",
        )
        engine.alerts.append(alert)
        result = engine.acknowledge_alert(alert.alert_id)
        assert result is True
        assert alert.acknowledged is True

    def test_get_unacknowledged_only(self, engine: BudgetEngine) -> None:
        a1 = BudgetAlert(policy_id="p1", dimension=BudgetDimension.TOKEN, level=BudgetLevel.L1_WARNING, message="a1")
        a2 = BudgetAlert(policy_id="p2", dimension=BudgetDimension.COST, level=BudgetLevel.L2_THROTTLED, message="a2")
        a2.acknowledged = True
        engine.alerts.extend([a1, a2])
        unack = engine.get_alerts(unacknowledged_only=True)
        assert len(unack) == 1
        assert unack[0].alert_id == a1.alert_id

    def test_get_all_alerts(self, engine: BudgetEngine) -> None:
        a1 = BudgetAlert(policy_id="p1", dimension=BudgetDimension.TOKEN, level=BudgetLevel.L1_WARNING, message="a1")
        a2 = BudgetAlert(policy_id="p2", dimension=BudgetDimension.COST, level=BudgetLevel.L2_THROTTLED, message="a2")
        a2.acknowledged = True
        engine.alerts.extend([a1, a2])
        all_alerts = engine.get_alerts(unacknowledged_only=False)
        assert len(all_alerts) == 2


class TestCostTracking:
    def test_record_token_consumption(self, engine: BudgetEngine) -> None:
        policy = engine.get_active_policy(BudgetDimension.TOKEN)
        assert policy is not None
        engine.record_consumption(policy.policy_id, tokens=500, cost=0.0, time_minutes=0.0)
        summary = engine.get_consumption_summary()
        assert policy.policy_id in summary
        assert summary[policy.policy_id]["daily"] == 500

    def test_record_cost_consumption(self, engine: BudgetEngine) -> None:
        policy = engine.get_active_policy(BudgetDimension.COST)
        assert policy is not None
        engine.record_consumption(policy.policy_id, tokens=0, cost=1.5, time_minutes=0.0)
        summary = engine.get_consumption_summary()
        assert summary[policy.policy_id]["daily"] == 1.5

    def test_record_time_consumption(self, engine: BudgetEngine) -> None:
        policy = engine.get_active_policy(BudgetDimension.TIME)
        assert policy is not None
        engine.record_consumption(policy.policy_id, tokens=0, cost=0.0, time_minutes=5.0)
        summary = engine.get_consumption_summary()
        assert summary[policy.policy_id]["daily"] == 5.0

    def test_consumption_accumulates(self, engine: BudgetEngine) -> None:
        policy = engine.get_active_policy(BudgetDimension.TOKEN)
        assert policy is not None
        engine.record_consumption(policy.policy_id, tokens=100, cost=0.0, time_minutes=0.0)
        engine.record_consumption(policy.policy_id, tokens=200, cost=0.0, time_minutes=0.0)
        summary = engine.get_consumption_summary()
        assert summary[policy.policy_id]["daily"] == 300

    def test_record_consumption_unknown_policy_noop(self, engine: BudgetEngine) -> None:
        engine.record_consumption("NONEXISTENT-POLICY", tokens=100, cost=0.0, time_minutes=0.0)
        summary = engine.get_consumption_summary()
        assert "NONEXISTENT-POLICY" not in summary

    def test_get_consumption_summary_structure(self, engine: BudgetEngine) -> None:
        summary = engine.get_consumption_summary()
        assert isinstance(summary, dict)
        for policy_id, data in summary.items():
            assert "daily" in data
            assert "hourly" in data


class TestRegisterPolicy:
    def test_register_custom_policy(self, engine: BudgetEngine) -> None:
        custom = BudgetPolicy(
            policy_id="BP-CUSTOM-001",
            name="Custom Token Budget",
            dimension=BudgetDimension.TOKEN,
            daily_limit=500_000,
            hourly_limit=50_000,
            per_request_limit=8_000,
        )
        engine.register_policy(custom)
        retrieved = engine.get_active_policy(BudgetDimension.TOKEN)
        assert retrieved is not None
        assert retrieved.policy_id == "BP-CUSTOM-001"
        assert retrieved.daily_limit == 500_000


class TestTryClaimBudget:
    def test_successful_claim(self, engine: BudgetEngine) -> None:
        ok, version, msg = engine.try_claim_budget(
            "provider-1",
            BudgetDimension.TOKEN,
            100.0,
        )
        assert ok is True
        assert version >= 0
        assert msg == "OK"

    def test_claim_exceeds_daily_budget(self, engine: BudgetEngine) -> None:
        ok, version, msg = engine.try_claim_budget(
            "provider-2",
            BudgetDimension.COST,
            100.0,
        )
        assert ok is False
        assert "Insufficient daily budget" in msg

    def test_claim_version_mismatch(self, engine: BudgetEngine) -> None:
        ok, version, msg = engine.try_claim_budget(
            "provider-3",
            BudgetDimension.TOKEN,
            100.0,
            expected_version=999,
        )
        assert ok is False
        assert "Version mismatch" in msg

    def test_commit_claim(self, engine: BudgetEngine) -> None:
        engine.try_claim_budget("provider-4", BudgetDimension.TOKEN, 100.0)
        committed = engine.commit_claim("provider-4", BudgetDimension.TOKEN, 80.0)
        assert committed is True

    def test_rollback_claim(self, engine: BudgetEngine) -> None:
        engine.try_claim_budget("provider-5", BudgetDimension.TOKEN, 100.0)
        rolled_back = engine.rollback_claim("provider-5", BudgetDimension.TOKEN)
        assert rolled_back is True

    def test_rollback_nonexistent_provider(self, engine: BudgetEngine) -> None:
        rolled_back = engine.rollback_claim("nonexistent-provider", BudgetDimension.TOKEN)
        assert rolled_back is True


class TestDegradation:
    def test_initial_degradation_level(self, engine: BudgetEngine) -> None:
        assert engine.current_degradation_level == BudgetLevel.L0_NORMAL
        assert engine.active_step_idx == 0

    def test_advance_degradation(self, engine: BudgetEngine) -> None:
        advanced = engine.advance_degradation()
        assert advanced is True
        assert engine.active_step_idx == 1
        assert engine.current_degradation_level == BudgetLevel.L1_WARNING

    def test_advance_degradation_max(self, engine: BudgetEngine) -> None:
        for _ in range(10):
            engine.advance_degradation()
        assert engine.active_step_idx == len(engine.degradation_steps) - 1
        result = engine.advance_degradation()
        assert result is False

    def test_retreat_degradation(self, engine: BudgetEngine) -> None:
        engine.advance_degradation()
        retreated = engine.retreat_degradation()
        assert retreated is True
        assert engine.active_step_idx == 0

    def test_retreat_degradation_min(self, engine: BudgetEngine) -> None:
        result = engine.retreat_degradation()
        assert result is False

    def test_model_router_recommendation(self, engine: BudgetEngine) -> None:
        tier, max_tokens = engine.get_model_router_recommendation()
        assert isinstance(tier, ModelTier)
        assert isinstance(max_tokens, int)
        assert max_tokens > 0


class TestComputeHash:
    def test_hash_deterministic(self, engine: BudgetEngine) -> None:
        h1 = engine.compute_hash()
        h2 = engine.compute_hash()
        assert h1 == h2

    def test_hash_changes_after_consumption(self, engine: BudgetEngine) -> None:
        h_before = engine.compute_hash()
        policy = engine.get_active_policy(BudgetDimension.TOKEN)
        assert policy is not None
        engine.record_consumption(policy.policy_id, tokens=100, cost=0.0, time_minutes=0.0)
        h_after = engine.compute_hash()
        assert h_before != h_after


class TestConsumptionVersion:
    def test_initial_version_zero(self, engine: BudgetEngine) -> None:
        for dim in BudgetDimension:
            version = engine.get_consumption_version(dim)
            assert version == 0

    def test_version_increments_on_claim(self, engine: BudgetEngine) -> None:
        v0 = engine.get_consumption_version(BudgetDimension.TOKEN)
        engine.try_claim_budget("provider-v", BudgetDimension.TOKEN, 100.0)
        v1 = engine.get_consumption_version(BudgetDimension.TOKEN)
        assert v1 > v0
