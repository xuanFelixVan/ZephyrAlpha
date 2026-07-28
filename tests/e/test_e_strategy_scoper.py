# [A_test] module_id: MOD-GOV_e_strategy_scoper | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §

# [MODULE] tests.test_e_strategy_scoper

# [INVARIANTS] test完整性

# [MODIFY-GUARD] none

# [CONSUMERS] none

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.financial_governance.strategy_scoper import ScopeLevel, StrategyScoper


class TestScopeLevel:
    def test_enum_members(self):
        assert len(ScopeLevel) == 3
        assert ScopeLevel.SIG.value == "sig"
        assert ScopeLevel.STRATEGY.value == "strategy"
        assert ScopeLevel.CAPITAL.value == "capital"


class TestStrategyScoperInit:
    def test_init_empty_scopes(self):
        scoper = StrategyScoper()
        assert scoper.scopes == {}


class TestAssignScope:
    def test_assign_adds_agent_to_dict(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent-1", ScopeLevel.SIG)
        assert scoper.scopes == {"agent-1": ScopeLevel.SIG}

    def test_assign_multiple_agents(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent-1", ScopeLevel.SIG)
        scoper.assign_scope("agent-2", ScopeLevel.STRATEGY)
        assert scoper.scopes["agent-1"] == ScopeLevel.SIG
        assert scoper.scopes["agent-2"] == ScopeLevel.STRATEGY
        assert len(scoper.scopes) == 2


class TestCanAccess:
    def test_sig_agent_access(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent-sig", ScopeLevel.SIG)
        assert scoper.can_access("agent-sig", ScopeLevel.SIG) is True
        assert scoper.can_access("agent-sig", ScopeLevel.STRATEGY) is True
        assert scoper.can_access("agent-sig", ScopeLevel.CAPITAL) is True

    def test_strategy_agent_access(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent-strategy", ScopeLevel.STRATEGY)
        assert scoper.can_access("agent-strategy", ScopeLevel.SIG) is False
        assert scoper.can_access("agent-strategy", ScopeLevel.STRATEGY) is True
        assert scoper.can_access("agent-strategy", ScopeLevel.CAPITAL) is True

    def test_capital_agent_access(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent-capital", ScopeLevel.CAPITAL)
        assert scoper.can_access("agent-capital", ScopeLevel.SIG) is False
        assert scoper.can_access("agent-capital", ScopeLevel.STRATEGY) is False
        assert scoper.can_access("agent-capital", ScopeLevel.CAPITAL) is True

    def test_unassigned_agent_denied(self):
        scoper = StrategyScoper()
        assert scoper.can_access("unknown-agent", ScopeLevel.SIG) is False
        assert scoper.can_access("unknown-agent", ScopeLevel.STRATEGY) is False
        assert scoper.can_access("unknown-agent", ScopeLevel.CAPITAL) is False

    def test_overwrite_scope_for_same_agent(self):
        scoper = StrategyScoper()
        scoper.assign_scope("agent-1", ScopeLevel.SIG)
        assert scoper.scopes["agent-1"] == ScopeLevel.SIG
        scoper.assign_scope("agent-1", ScopeLevel.CAPITAL)
        assert scoper.scopes["agent-1"] == ScopeLevel.CAPITAL

    def test_empty_agent_id_boundary(self):
        scoper = StrategyScoper()
        scoper.assign_scope("", ScopeLevel.SIG)
        assert scoper.can_access("", ScopeLevel.SIG) is True
        assert scoper.can_access("", ScopeLevel.STRATEGY) is True
        assert scoper.can_access("", ScopeLevel.CAPITAL) is True
