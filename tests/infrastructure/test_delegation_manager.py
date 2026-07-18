# [A_test] module_id: SRC-TST-0148 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-305 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_delegation_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Test Delegation Manager."""

from zephyr.governance.intelligence_governance.delegation_manager import DelegateResult, DelegationManager


def test_self_delegation_blocked():
    mgr = DelegationManager()
    ok, result, msg = mgr.delegate({"caller": "agent1", "source_agent": "agent1"}, "cap1")
    assert not ok
    assert result == DelegateResult.SELF_DELEGATION


def test_depth_exceeded():
    mgr = DelegationManager()
    for i in range(4):
        mgr.delegate({"caller": f"agent{i}", "task_id": f"t{i}"}, "cap")
    ok, result, _ = mgr.delegate({"caller": "agent4", "task_id": "t4"}, "cap")
    assert not ok
    assert result == DelegateResult.DEPTH_EXCEEDED


def test_cycle_detected():
    mgr = DelegationManager()
    mgr.delegate({"caller": "agent1"}, "cap")
    mgr.delegate({"caller": "agent2"}, "cap")
    ok, result, _ = mgr.delegate({"caller": "agent1"}, "cap")
    assert not ok or result != DelegateResult.GRANTED
