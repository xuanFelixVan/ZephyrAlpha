# [A_test] module_id: SRC-TST-1663 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §test

# [MODULE] tests.test_slo_contract

# [INVARIANTS] test_slo_contract covers SLOContractEngine+BudgetTier+SLIName+ContractPriority

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest raises on failure

# [TESTS] test_slo_contract
# [TTL] task_bound
from __future__ import annotations

from zephyr.gov_enforcement.rule_enforcement.slo_contract import (
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


class TestBudgetTier:
    def test_four_members(self):
        assert len(BudgetTier) == 4

    def test_values(self):
        assert BudgetTier.HEALTHY.value == "healthy"
        assert BudgetTier.EXHAUSTED.value == "exhausted"

    def test_ordering(self):
        assert budget_tier_ordering(BudgetTier.HEALTHY) < budget_tier_ordering(BudgetTier.WARNING)
        assert budget_tier_ordering(BudgetTier.WARNING) < budget_tier_ordering(BudgetTier.CRITICAL)
        assert budget_tier_ordering(BudgetTier.CRITICAL) < budget_tier_ordering(BudgetTier.EXHAUSTED)


class TestContractPriority:
    def test_three_members(self):
        assert len(ContractPriority) == 3

    def test_values(self):
        assert ContractPriority.P0.value == "P0"
        assert ContractPriority.P2.value == "P2"


class TestSLIName:
    def test_seven_members(self):
        assert len(SLIName) == 7

    def test_all_in_defaults(self):
        for sli in SLIName:
            assert sli in DEFAULT_SLIS


class TestSLIDefinition:
    def test_create(self):
        d = SLIDefinition(name=SLIName.CODE_REJECTION, description="test", target=0.95, error_budget_ratio=0.05)
        assert d.target == 0.95
        assert d.window_seconds == 86400.0

    def test_custom_window(self):
        d = SLIDefinition(
            name=SLIName.DEADLOCK, description="t", target=0.99, error_budget_ratio=0.01, window_seconds=3600
        )
        assert d.window_seconds == 3600


class TestSLOContractTerms:
    def test_create(self):
        t = SLOContractTerms(priority=ContractPriority.P0, ack_timeout_s=300, resolve_timeout_s=900, penalty="test")
        assert t.ack_timeout_s == 300


class TestSLIReading:
    def test_create(self):
        r = SLIReading(name=SLIName.CODE_REJECTION, value=0.97, within_slo=True)
        assert r.within_slo is True
        assert r.timestamp > 0


class TestBudgetSnapshot:
    def test_defaults(self):
        s = BudgetSnapshot(tier=BudgetTier.HEALTHY, error_budget_remaining_pct=100.0, burn_rate_per_hour=0.0)
        assert s.cooldown_active is False
        assert s.cooldown_until_s == 0.0


class TestDefaultConstants:
    def test_default_slis_complete(self):
        assert len(DEFAULT_SLIS) == 7

    def test_default_contracts_complete(self):
        assert len(DEFAULT_CONTRACTS) == 3

    def test_trading_override_is_p0(self):
        assert TRADING_OVERRIDE.priority == ContractPriority.P0
        assert TRADING_OVERRIDE.ack_timeout_s == 300

    def test_tier_policy_four_entries(self):
        assert len(TIER_POLICY) == 4

    def test_tier_policy_thresholds_descending(self):
        thresholds = [TIER_POLICY[t]["threshold"] for t in BudgetTier]
        assert thresholds == sorted(thresholds, reverse=True)


class TestSLOContractEngine:
    def test_instantiation_default(self):
        e = SLOContractEngine()
        assert e.window_seconds == 86400.0
        assert e.cooldown_active is False

    def test_instantiation_custom(self):
        e = SLOContractEngine(window_seconds=3600)
        assert e.window_seconds == 3600

    def test_record_with_empty_slis_uses_defaults(self):
        e = SLOContractEngine(slis={})
        r = e.record(SLIName.CODE_REJECTION, 0.97)
        assert r.within_slo is True

    def test_record_within_slo(self):
        e = SLOContractEngine()
        r = e.record(SLIName.CODE_REJECTION, 0.97)
        assert r.within_slo is True

    def test_record_below_slo(self):
        e = SLOContractEngine()
        r = e.record(SLIName.CODE_REJECTION, 0.80)
        assert r.within_slo is False

    def test_get_budget_healthy_initially(self):
        e = SLOContractEngine()
        b = e.get_budget(SLIName.CODE_REJECTION)
        assert b.tier == BudgetTier.HEALTHY
        assert b.error_budget_remaining_pct == 100.0

    def test_get_worst_budget_tier(self):
        e = SLOContractEngine()
        worst = e.get_worst_budget_tier()
        assert worst.tier == BudgetTier.HEALTHY

    def test_get_contract(self):
        e = SLOContractEngine()
        c = e.get_contract(ContractPriority.P0)
        assert c.ack_timeout_s == 900

    def test_get_trading_override(self):
        e = SLOContractEngine()
        t = e.get_trading_override()
        assert t.ack_timeout_s == 300

    def test_should_escalate_within_thresholds(self):
        e = SLOContractEngine()
        escalate, reason = e.should_escalate(SLIName.CODE_REJECTION, 0.97)
        assert escalate is False

    def test_should_escalate_exhausted(self):
        e = SLOContractEngine()
        for _ in range(20):
            e.record(SLIName.CODE_REJECTION, 0.50)
        escalate, reason = e.should_escalate(SLIName.CODE_REJECTION, 0.50)
        assert escalate is True

    def test_force_exhaust(self):
        e = SLOContractEngine()
        e.force_exhaust(SLIName.CODE_REJECTION)
        b = e.get_budget(SLIName.CODE_REJECTION)
        assert b.tier == BudgetTier.EXHAUSTED
        assert b.cooldown_active is True

    def test_reset_budget_single(self):
        e = SLOContractEngine()
        e.force_exhaust(SLIName.CODE_REJECTION)
        e.reset_budget(SLIName.CODE_REJECTION)
        b = e.get_budget(SLIName.CODE_REJECTION)
        assert b.tier == BudgetTier.HEALTHY

    def test_reset_budget_all(self):
        e = SLOContractEngine()
        e.force_exhaust(SLIName.CODE_REJECTION)
        e.reset_budget()
        b = e.get_budget(SLIName.CODE_REJECTION)
        assert b.tier == BudgetTier.HEALTHY

    def test_get_recommended_scaling_healthy(self):
        e = SLOContractEngine()
        s = e.get_recommended_scaling()
        assert s["current_tier"] == "healthy"
        assert s["escalation_level_offset"] == 0

    def test_summary_structure(self):
        e = SLOContractEngine()
        s = e.summary()
        assert "scaling_recommendation" in s
        assert "budgets" in s
        assert "contract_slo" in s
        assert len(s["budgets"]) == 7

    def test_cooldown_active_after_force_exhaust(self):
        e = SLOContractEngine()
        e.force_exhaust(SLIName.CODE_REJECTION)
        assert e.cooldown_active is True

    def test_multiple_records_degrade_tier(self):
        e = SLOContractEngine()
        for _ in range(10):
            e.record(SLIName.CODE_REJECTION, 0.50)
        b = e.get_budget(SLIName.CODE_REJECTION)
        assert b.tier in (BudgetTier.CRITICAL, BudgetTier.EXHAUSTED)
