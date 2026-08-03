# [A_test] module_id: MOD-GOV_strategy_scoper | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_strategy_scoper
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_strategy_scoper.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.financial_governance.strategy_scoper import (
    ScopeLevel,
    StrategyScoper,
)


class TestScopeLevel:
    def test_enum_values(self):
        assert ScopeLevel.SIG.value == "sig"
        assert ScopeLevel.STRATEGY.value == "strategy"
        assert ScopeLevel.CAPITAL.value == "capital"

    def test_enum_member_count(self):
        assert len(ScopeLevel) == 3


class TestStrategyScoperInstantiation:
    def test_empty_on_creation(self):
        scoper = StrategyScoper()
        assert scoper.scopes == {}

    def test_independent_instances(self):
        s1 = StrategyScoper()
        s2 = StrategyScoper()
        s1.assign_scope("a", ScopeLevel.SIG)
        assert "a" not in s2.scopes


class TestAssignScope:
    def test_assign_sig(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent_1", ScopeLevel.SIG)
        assert scoper.scopes["agent_1"] is ScopeLevel.SIG

    def test_assign_strategy(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent_2", ScopeLevel.STRATEGY)
        assert scoper.scopes["agent_2"] is ScopeLevel.STRATEGY

    def test_assign_capital(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent_3", ScopeLevel.CAPITAL)
        assert scoper.scopes["agent_3"] is ScopeLevel.CAPITAL

    def test_reassign_overwrites(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent_1", ScopeLevel.SIG)
        scoper.assign_scope("agent_1", ScopeLevel.CAPITAL)
        assert scoper.scopes["agent_1"] is ScopeLevel.CAPITAL

    def test_multiple_agents(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.SIG)
        scoper.assign_scope("b", ScopeLevel.STRATEGY)
        scoper.assign_scope("c", ScopeLevel.CAPITAL)
        assert len(scoper.scopes) == 3


class TestCanAccess:
    def test_sig_can_access_sig(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.SIG)
        assert scoper.can_access("a", ScopeLevel.SIG) is True

    def test_sig_can_access_strategy(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.SIG)
        assert scoper.can_access("a", ScopeLevel.STRATEGY) is True

    def test_sig_can_access_capital(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.SIG)
        assert scoper.can_access("a", ScopeLevel.CAPITAL) is True

    def test_strategy_cannot_access_sig(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.STRATEGY)
        assert scoper.can_access("a", ScopeLevel.SIG) is False

    def test_strategy_can_access_strategy(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.STRATEGY)
        assert scoper.can_access("a", ScopeLevel.STRATEGY) is True

    def test_strategy_can_access_capital(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.STRATEGY)
        assert scoper.can_access("a", ScopeLevel.CAPITAL) is True

    def test_capital_cannot_access_sig(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.CAPITAL)
        assert scoper.can_access("a", ScopeLevel.SIG) is False

    def test_capital_cannot_access_strategy(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.CAPITAL)
        assert scoper.can_access("a", ScopeLevel.STRATEGY) is False

    def test_capital_can_access_capital(self):
        scoper = StrategyScoper()
        scoper.assign_scope("a", ScopeLevel.CAPITAL)
        assert scoper.can_access("a", ScopeLevel.CAPITAL) is True

    def test_unassigned_agent_cannot_access(self):
        scoper = StrategyScoper()
        assert scoper.can_access("unknown", ScopeLevel.SIG) is False

    def test_unassigned_agent_cannot_access_capital(self):
        scoper = StrategyScoper()
        assert scoper.can_access("unknown", ScopeLevel.CAPITAL) is False
