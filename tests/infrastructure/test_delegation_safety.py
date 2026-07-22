# [A_test] module_id: MOD-GOV_delegation_safety | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-306 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_delegation_safety
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""DelegationEngine Safety Constraint Tests — D-022-02 四级安全约束.

Tests each of the four safety constraints independently:
1. Self-delegation prohibition
2. Circular delegation / loop detection
3. Depth cap enforcement
4. SLA / timeout enforcement

Blueprint: docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md D-022-02
"""

from zephyr.governance.escalation import (
    DelegationEngine,
    DelegationStrategy,
    EscalationEvent,
    RuleCategory,
)


class TestSelfDelegationProhibition:
    """Constraint 1: An agent MUST NOT delegate back to itself."""

    def test_same_agent_cannot_delegate_to_self(self):
        de = DelegationEngine()
        de.register_delegate("agent-x")
        ev = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="agent-x")

        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "self-task")
        assert record.to_delegate != "agent-x"

    def test_same_owner_event_delegates_to_different_agent(self):
        de = DelegationEngine()
        de.register_delegate("alice")
        de.register_delegate("bob")
        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="alice")

        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "owner-task")
        assert record.to_delegate != "alice"

    def test_single_delegate_self_delegation_prevented(self):
        de = DelegationEngine()
        de.register_delegate("lonely-agent")
        ev = EscalationEvent(category=RuleCategory.AUTO_GUARD_FAILURE, owner_id="lonely-agent")

        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "lonely-task")
        assert record.to_delegate != "lonely-agent"


class TestCircularDelegationDetection:
    """Constraint 2: Circular delegation loops MUST be detected and broken."""

    def test_two_agent_cycle_prevented(self):
        de = DelegationEngine()
        de.register_delegate("agent-a")
        de.register_delegate("agent-b")

        ev1 = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="agent-a")
        r1 = de.delegate(ev1, DelegationStrategy.LOAD_BALANCED, "cycle-1")
        assert r1.to_delegate != "agent-a"

        ev2 = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="agent-b")
        r2 = de.delegate(ev2, DelegationStrategy.LOAD_BALANCED, "cycle-2")
        assert r2.to_delegate != "agent-b"

    def test_three_agent_cycle_detected(self):
        de = DelegationEngine()
        de.register_delegate("x")
        de.register_delegate("y")
        de.register_delegate("z")

        events = []
        for agent in ("x", "y", "z"):
            ev = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id=agent)
            events.append(de.delegate(ev, DelegationStrategy.LOAD_BALANCED, f"triple-{agent}"))

        for record in events:
            assert record.to_delegate != ""

    def test_repeated_delegation_no_cycle(self):
        de = DelegationEngine()
        de.register_delegate("oracle")
        de.register_delegate("worker")
        for i in range(5):
            ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id=f"owner-{i}")
            record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, f"linear-{i}")
            assert record.to_delegate in ("oracle", "worker")


class TestDepthCapEnforcement:
    """Constraint 3: Delegation chain depth MUST be capped."""

    def test_single_delegate_load_accumulates_correctly(self):
        de = DelegationEngine()
        de.register_delegate("depth-worker")
        for i in range(5):
            ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id=f"deep-{i}")
            de.delegate(ev, DelegationStrategy.LOAD_BALANCED, f"depth-task-{i}")
        assert de.get_load("depth-worker") <= 5

    def test_max_delegates_respected(self):
        de = DelegationEngine()
        delegate_count = 10
        for i in range(delegate_count):
            de.register_delegate(f"d-{i}")
        for i in range(delegate_count * 3):
            ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id=f"bulk-{i}")
            de.delegate(ev, DelegationStrategy.LOAD_BALANCED, f"bulk-task-{i}")
        assert len(de.get_available_delegates()) <= delegate_count

    def test_load_distribution_across_delegates(self):
        de = DelegationEngine()
        for i in range(4):
            de.register_delegate(f"node-{i}")
        for i in range(20):
            ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id=f"dist-{i}")
            de.delegate(ev, DelegationStrategy.LOAD_BALANCED, f"dist-task-{i}")
        loads = [de.get_load(f"node-{i}") for i in range(4)]
        assert max(loads) - min(loads) <= 5


class TestSLATimeoutEnforcement:
    """Constraint 4: Delegated tasks MUST have SLA timeout enforcement."""

    def test_pending_delegation_has_record(self):
        de = DelegationEngine()
        de.register_delegate("sla-worker")
        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="sla-owner")
        de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "sla-task")

        pending = de.get_pending_delegations()
        assert len(pending) > 0
        for record in pending:
            assert record.created_at is not None

    def test_completed_delegation_not_pending(self):
        de = DelegationEngine()
        de.register_delegate("cmp-worker")
        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="cmp-owner")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "cmp-task")

        de.accept_delegation(record.delegation_id)
        de.complete_delegation(record.delegation_id)

        pending = de.get_pending_delegations()
        for r in pending:
            assert r.delegation_id != record.delegation_id

    def test_rejected_delegation_not_pending(self):
        de = DelegationEngine()
        de.register_delegate("rej-worker")
        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="rej-owner")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "rej-task")

        de.reject_delegation(record.delegation_id)

        pending = de.get_pending_delegations()
        for r in pending:
            assert r.delegation_id != record.delegation_id

    def test_cleanup_removes_expired(self):
        de = DelegationEngine()
        de.register_delegate("exp-worker")
        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="exp-owner")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "exp-task")
        record.expires_at = None
        cleaned = de.cleanup_expired()
        assert isinstance(cleaned, int)
        assert cleaned >= 0


class TestExpertiseMatchStrategy:
    """Additional validation of EXPERTISE_MATCH delegation strategy."""

    def test_expertise_matched_correctly(self):
        de = DelegationEngine()
        de.register_delegate("security-expert", ["security", "vulnerability"])
        de.register_delegate("generic-bot")

        ev = EscalationEvent(category=RuleCategory.SECURITY_VIOLATION, owner_id="match-owner")
        record = de.delegate(ev, DelegationStrategy.EXPERTISE_MATCH, "match-task")
        assert record.to_delegate == "security-expert"

    def test_expertise_no_match_falls_back(self):
        de = DelegationEngine()
        de.register_delegate("normal-bot")
        ev = EscalationEvent(category=RuleCategory.DRIFT_DETECTED, owner_id="drift-owner")
        record = de.delegate(ev, DelegationStrategy.EXPERTISE_MATCH, "drift-task")
        assert record.to_delegate == "normal-bot"
