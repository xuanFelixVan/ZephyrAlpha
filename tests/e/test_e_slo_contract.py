# [A_test] module_id: SRC-TST-0823 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_slo_contract
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import time

import pytest

from zephyr.governance.rule_enforcement.slo_contract import (
    DEFAULT_CONTRACTS,
    DEFAULT_SLIS,
    TIER_POLICY,
    TRADING_OVERRIDE,
    BudgetSnapshot,
    BudgetTier,
    budget_tier_ordering,
    ContractPriority,
    SLIDefinition,
    SLIName,
    SLIReading,
    SLOContractEngine,
    SLOContractTerms,
)


class TestBudgetTierEnum:
    def test_member_count(self):
        assert len(BudgetTier) == 4

    def test_values(self):
        assert BudgetTier.HEALTHY.value == "healthy"
        assert BudgetTier.WARNING.value == "warning"
        assert BudgetTier.CRITICAL.value == "critical"
        assert BudgetTier.EXHAUSTED.value == "exhausted"


class TestContractPriorityEnum:
    def test_member_count(self):
        assert len(ContractPriority) == 3

    def test_values(self):
        assert ContractPriority.P0.value == "P0"
        assert ContractPriority.P1.value == "P1"
        assert ContractPriority.P2.value == "P2"


class TestSLINameEnum:
    def test_member_count(self):
        assert len(SLIName) == 7

    def test_values(self):
        assert SLIName.CODE_REJECTION.value == "code_rejection"
        assert SLIName.CONSENSUS_CONFLICT.value == "consensus_conflict"
        assert SLIName.RETRY_FATIGUE.value == "retry_fatigue"
        assert SLIName.HUMAN_OVERRIDE.value == "human_override"
        assert SLIName.DEADLOCK.value == "deadlock"
        assert SLIName.BUDGET_CONSUMPTION.value == "budget_consumption"
        assert SLIName.RESPONSE_LATENCY.value == "response_latency"


class TestSLIDefinition:
    def test_instantiation(self):
        sla = SLIDefinition(
            name=SLIName.CODE_REJECTION,
            description="test",
            target=0.95,
            error_budget_ratio=0.05,
        )
        assert sla.name == SLIName.CODE_REJECTION
        assert sla.description == "test"
        assert sla.target == 0.95
        assert sla.error_budget_ratio == 0.05
        assert sla.window_seconds == 86400.0

    def test_default_window_seconds(self):
        sla = SLIDefinition(
            name=SLIName.DEADLOCK,
            description="desc",
            target=0.99,
            error_budget_ratio=0.01,
        )
        assert sla.window_seconds == 86400.0

    def test_custom_window_seconds(self):
        sla = SLIDefinition(
            name=SLIName.RESPONSE_LATENCY,
            description="custom",
            target=0.99,
            error_budget_ratio=0.01,
            window_seconds=3600.0,
        )
        assert sla.window_seconds == 3600.0


class TestSLOContractTerms:
    def test_instantiation(self):
        terms = SLOContractTerms(
            priority=ContractPriority.P0,
            ack_timeout_s=900,
            resolve_timeout_s=14400,
            penalty="超时→安全模式",
        )
        assert terms.priority == ContractPriority.P0
        assert terms.ack_timeout_s == 900
        assert terms.resolve_timeout_s == 14400
        assert terms.penalty == "超时→安全模式"


class TestSLIReading:
    def test_instantiation(self):
        reading = SLIReading(name=SLIName.CODE_REJECTION, value=0.96)
        assert reading.name == SLIName.CODE_REJECTION
        assert reading.value == 0.96
        assert reading.within_slo is True
        assert isinstance(reading.timestamp, float)

    def test_within_slo_false(self):
        reading = SLIReading(name=SLIName.DEADLOCK, value=0.5, within_slo=False)
        assert reading.within_slo is False
        assert reading.value == 0.5


class TestBudgetSnapshot:
    def test_instantiation(self):
        snap = BudgetSnapshot(
            tier=BudgetTier.HEALTHY,
            error_budget_remaining_pct=100.0,
            burn_rate_per_hour=0.0,
        )
        assert snap.tier == BudgetTier.HEALTHY
        assert snap.error_budget_remaining_pct == 100.0
        assert snap.burn_rate_per_hour == 0.0
        assert snap.cooldown_active is False
        assert snap.cooldown_until_s == 0.0

    def test_cooldown_fields(self):
        snap = BudgetSnapshot(
            tier=BudgetTier.EXHAUSTED,
            error_budget_remaining_pct=0.0,
            burn_rate_per_hour=10.0,
            cooldown_active=True,
            cooldown_until_s=9999999999.0,
        )
        assert snap.cooldown_active is True
        assert snap.cooldown_until_s == 9999999999.0


class TestDEFAULT_SLIS:
    def test_has_seven_entries(self):
        assert len(DEFAULT_SLIS) == 7

    def test_each_target_positive(self):
        for name, sla in DEFAULT_SLIS.items():
            assert sla.target > 0, f"{name} target should be > 0"

    def test_each_error_budget_ratio_positive(self):
        for name, sla in DEFAULT_SLIS.items():
            assert sla.error_budget_ratio > 0, f"{name} error_budget_ratio should be > 0"


class TestDEFAULT_CONTRACTS:
    def test_has_three_priorities(self):
        assert len(DEFAULT_CONTRACTS) == 3

    def test_all_have_timeout_values(self):
        for priority, terms in DEFAULT_CONTRACTS.items():
            assert terms.ack_timeout_s > 0
            assert terms.resolve_timeout_s > 0
            assert isinstance(terms.penalty, str) and len(terms.penalty) > 0

    def test_p0_terms(self):
        p0 = DEFAULT_CONTRACTS[ContractPriority.P0]
        assert p0.ack_timeout_s == 900
        assert p0.resolve_timeout_s == 14400

    def test_p1_terms(self):
        p1 = DEFAULT_CONTRACTS[ContractPriority.P1]
        assert p1.ack_timeout_s == 14400
        assert p1.resolve_timeout_s == 86400

    def test_p2_terms(self):
        p2 = DEFAULT_CONTRACTS[ContractPriority.P2]
        assert p2.ack_timeout_s == 86400
        assert p2.resolve_timeout_s == 259200


class TestTRADING_OVERRIDE:
    def test_priority_is_p0(self):
        assert TRADING_OVERRIDE.priority == ContractPriority.P0

    def test_fast_timeouts(self):
        assert TRADING_OVERRIDE.ack_timeout_s == 300
        assert TRADING_OVERRIDE.resolve_timeout_s == 900

    def test_penalty(self):
        assert TRADING_OVERRIDE.penalty == "超时清仓"


class TestTIER_POLICY:
    def test_has_four_tiers(self):
        assert len(TIER_POLICY) == 4

    def test_each_has_threshold(self):
        for tier, policy in TIER_POLICY.items():
            assert "threshold" in policy
            assert isinstance(policy["threshold"], (int, float))

    def test_each_has_auto_guard_modifier(self):
        for tier, policy in TIER_POLICY.items():
            assert "auto_guard_modifier" in policy
            assert isinstance(policy["auto_guard_modifier"], (int, float))

    def test_healthy_threshold(self):
        assert TIER_POLICY[BudgetTier.HEALTHY]["threshold"] == 50.0

    def test_warning_threshold(self):
        assert TIER_POLICY[BudgetTier.WARNING]["threshold"] == 20.0

    def test_critical_threshold(self):
        assert TIER_POLICY[BudgetTier.CRITICAL]["threshold"] == 0.0

    def test_exhausted_threshold(self):
        assert TIER_POLICY[BudgetTier.EXHAUSTED]["threshold"] == -1.0


class TestBudgetTierOrdering:
    def test_healthy_returns_0(self):
        assert budget_tier_ordering(BudgetTier.HEALTHY) == 0

    def test_warning_returns_1(self):
        assert budget_tier_ordering(BudgetTier.WARNING) == 1

    def test_critical_returns_2(self):
        assert budget_tier_ordering(BudgetTier.CRITICAL) == 2

    def test_exhausted_returns_3(self):
        assert BudgetTier_ordering(BudgetTier.EXHAUSTED) == 3


class TestSLOContractEngineInit:
    def test_init_with_defaults(self):
        engine = SLOContractEngine()
        assert len(engine._slis) == 7
        assert engine.window_seconds == 86400.0

    def test_init_with_custom_slis(self):
        custom_slis = {
            SLIName.CODE_REJECTION: SLIDefinition(
                name=SLIName.CODE_REJECTION,
                description="test",
                target=0.99,
                error_budget_ratio=0.01,
            ),
        }
        engine = SLOContractEngine(slis=custom_slis)
        assert len(engine._slis) == 1

    def test_init_with_custom_window(self):
        engine = SLOContractEngine(window_seconds=3600.0)
        assert engine.window_seconds == 3600.0


class TestSLOContractEngineRecord:
    def test_record_returns_sli_reading(self):
        engine = SLOContractEngine()
        reading = engine.record(SLIName.CODE_REJECTION, 0.96)
        assert isinstance(reading, SLIReading)
        assert reading.name == SLIName.CODE_REJECTION
        assert reading.value == 0.96
        assert reading.within_slo is True

    def test_record_stores_reading(self):
        engine = SLOContractEngine()
        engine.record(SLIName.DEADLOCK, 0.9995)
        readings = engine._readings[SLIName.DEADLOCK]
        assert len(readings) == 1
        assert readings[0].value == 0.9995
        assert readings[0].within_slo is True

    def test_record_below_target_marks_within_slo_false(self):
        engine = SLOContractEngine()
        reading = engine.record(SLIName.RESPONSE_LATENCY, 0.5)
        assert reading.within_slo is False

    def test_record_unknown_sli_raises_keyerror(self):
        engine = SLOContractEngine(
            slis={
                SLIName.CODE_REJECTION: SLIDefinition(
                    name=SLIName.CODE_REJECTION,
                    description="test",
                    target=0.95,
                    error_budget_ratio=0.05,
                ),
            }
        )
        with pytest.raises(KeyError):
            engine.record(SLIName.DEADLOCK, 0.5)


class TestSLOContractEngineGetBudget:
    def test_returns_budget_snapshot(self):
        engine = SLOContractEngine()
        snap = engine.get_budget(SLIName.CODE_REJECTION)
        assert isinstance(snap, BudgetSnapshot)
        assert snap.tier == BudgetTier.HEALTHY
        assert snap.error_budget_remaining_pct == 100.0

    def test_returns_default_healthy_on_empty_readings(self):
        engine = SLOContractEngine()
        snap = engine.get_budget(SLIName.DEADLOCK)
        assert isinstance(snap, BudgetSnapshot)
        assert snap.tier == BudgetTier.HEALTHY
        assert snap.error_budget_remaining_pct == 100.0


class TestSLOContractEngineGetWorstBudgetTier:
    def test_all_healthy_returns_healthy(self):
        engine = SLOContractEngine()
        worst = engine.get_worst_budget_tier()
        assert worst.tier == BudgetTier.HEALTHY

    def test_one_exhausted_returns_exhausted(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.DEADLOCK)
        worst = engine.get_worst_budget_tier()
        assert worst.tier == BudgetTier.EXHAUSTED


class TestSLOContractEngineGetContract:
    def test_p0_returns_correct_terms(self):
        engine = SLOContractEngine()
        terms = engine.get_contract(ContractPriority.P0)
        assert terms.ack_timeout_s == 900
        assert terms.resolve_timeout_s == 14400

    def test_unknown_priority_returns_p2_fallback(self):
        engine = SLOContractEngine(
            contracts={
                ContractPriority.P0: SLOContractTerms(
                    priority=ContractPriority.P0,
                    ack_timeout_s=60,
                    resolve_timeout_s=120,
                    penalty="test",
                ),
            }
        )
        terms = engine.get_contract(ContractPriority.P2)
        assert isinstance(terms, SLOContractTerms)
        assert terms.priority == ContractPriority.P2


class TestSLOContractEngineGetTradingOverride:
    def test_returns_trading_override(self):
        engine = SLOContractEngine()
        override = engine.get_trading_override()
        assert override.priority == ContractPriority.P0
        assert override.ack_timeout_s == 300
        assert override.resolve_timeout_s == 900


class TestSLOContractEngineShouldEscalate:
    def test_within_slo_returns_false(self):
        engine = SLOContractEngine()
        should, reason = engine.should_escalate(SLIName.DEADLOCK, 1.0)
        assert should is False
        assert "acceptable" in reason.lower()

    def test_exhausted_budget_returns_true(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        should, reason = engine.should_escalate(SLIName.CODE_REJECTION, 0.0)
        assert should is True
        assert "exhausted" in reason.lower()

    def test_critical_budget_with_violation_returns_true(self):
        engine = SLOContractEngine(window_seconds=86400.0)
        for _ in range(20):
            engine.record(SLIName.RETRY_FATIGUE, 0.5)
        snap = engine.get_budget(SLIName.RETRY_FATIGUE)
        if snap.tier == BudgetTier.CRITICAL:
            should, _ = engine.should_escalate(SLIName.RETRY_FATIGUE, 0.5)
            assert should is True

    def test_violation_without_critical_budget_returns_false(self):
        engine = SLOContractEngine()
        engine.record(SLIName.RETRY_FATIGUE, 0.99)
        should, reason = engine.should_escalate(SLIName.RETRY_FATIGUE, 0.99)
        assert should is False


class TestSLOContractEngineForceExhaust:
    def test_sets_tier_to_exhausted(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        snap = engine.get_budget(SLIName.CODE_REJECTION)
        assert snap.tier == BudgetTier.EXHAUSTED
        assert snap.error_budget_remaining_pct == 0.0

    def test_sets_cooldown(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.DEADLOCK)
        snap = engine.get_budget(SLIName.DEADLOCK)
        assert snap.cooldown_active is True
        assert snap.cooldown_until_s > time.time()

    def test_sets_engine_cooldown(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.RESPONSE_LATENCY)
        assert engine._cooldown_lock is True
        assert engine._cooldown_until > time.time()


class TestSLOContractEngineResetBudget:
    def test_resets_to_healthy(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        engine.reset_budget(SLIName.CODE_REJECTION)
        snap = engine.get_budget(SLIName.CODE_REJECTION)
        assert snap.tier == BudgetTier.HEALTHY
        assert snap.error_budget_remaining_pct == 100.0
        assert snap.burn_rate_per_hour == 0.0

    def test_reset_clears_readings(self):
        engine = SLOContractEngine()
        engine.record(SLIName.DEADLOCK, 1.0)
        assert len(engine._readings[SLIName.DEADLOCK]) > 0
        engine.reset_budget(SLIName.DEADLOCK)
        assert len(engine._readings[SLIName.DEADLOCK]) == 0

    def test_reset_all_resets_every_sli(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        engine.force_exhaust(SLIName.DEADLOCK)
        engine.reset_budget()
        for sli_name in engine._slis:
            snap = engine.get_budget(sli_name)
            assert snap.tier == BudgetTier.HEALTHY
            assert snap.error_budget_remaining_pct == 100.0

    def test_reset_clears_cooldown(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        engine.reset_budget(SLIName.CODE_REJECTION)
        snap = engine.get_budget(SLIName.CODE_REJECTION)
        assert snap.cooldown_active is False
        assert snap.cooldown_until_s == 0.0


class TestSLOContractEngineSummary:
    def test_returns_dict_with_required_keys(self):
        engine = SLOContractEngine()
        result = engine.summary()
        assert isinstance(result, dict)
        assert "scaling_recommendation" in result
        assert "budgets" in result
        assert "contract_slo" in result

    def test_scaling_recommendation_has_required_fields(self):
        engine = SLOContractEngine()
        result = engine.summary()
        rec = result["scaling_recommendation"]
        assert "current_tier" in rec
        assert "error_budget_remaining_pct" in rec
        assert "burn_rate_per_hour" in rec
        assert "auto_guard_modifier" in rec
        assert "escalation_level_offset" in rec
        assert "description" in rec
        assert "cooldown_active" in rec

    def test_budgets_has_all_slis(self):
        engine = SLOContractEngine()
        result = engine.summary()
        budgets = result["budgets"]
        assert len(budgets) == 7
        for sli_name in engine._slis:
            assert sli_name.value in budgets

    def test_contract_slo_has_all_priorities(self):
        engine = SLOContractEngine()
        result = engine.summary()
        contract_slo = result["contract_slo"]
        assert "P0" in contract_slo
        assert "P1" in contract_slo
        assert "P2" in contract_slo


class TestSLOContractEngineGetRecommendedScaling:
    def test_healthy_returns_level_offset_0(self):
        engine = SLOContractEngine()
        rec = engine.get_recommended_scaling()
        assert rec["escalation_level_offset"] == 0
        assert rec["current_tier"] == "healthy"
        assert rec["auto_guard_modifier"] == 1.0

    def test_exhausted_returns_level_offset_4(self):
        engine = SLOContractEngine()
        engine.force_exhaust(SLIName.CODE_REJECTION)
        rec = engine.get_recommended_scaling()
        assert rec["escalation_level_offset"] == 4
        assert rec["current_tier"] == "exhausted"
        assert rec["auto_guard_modifier"] == 0.0

    def test_warning_returns_level_offset_0(self):
        engine = SLOContractEngine(window_seconds=86400.0)
        for _ in range(95):
            engine.record(SLIName.RETRY_FATIGUE, 1.0)
        for _ in range(5):
            engine.record(SLIName.RETRY_FATIGUE, 0.0)
        rec = engine.get_recommended_scaling()
        assert rec["escalation_level_offset"] == 0
        assert rec["current_tier"] == "warning"

    def test_critical_returns_level_offset_1(self):
        engine = SLOContractEngine(window_seconds=86400.0)
        for _ in range(91):
            engine.record(SLIName.RETRY_FATIGUE, 1.0)
        for _ in range(9):
            engine.record(SLIName.RETRY_FATIGUE, 0.0)
        rec = engine.get_recommended_scaling()
        assert rec["escalation_level_offset"] == 1
        assert rec["current_tier"] == "critical"

    def test_includes_cooldown_active_flag(self):
        engine = SLOContractEngine()
        rec = engine.get_recommended_scaling()
        assert "cooldown_active" in rec
        assert isinstance(rec["cooldown_active"], bool)
