# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_delegation_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""Test Delegation Manager."""
from zephyr.escalation_engine.delegation_manager import DelegationManager,DelegateResult

def test_self_delegation_blocked():
    mgr=DelegationManager()
    ok,result,msg=mgr.delegate({"caller":"agent1","source_agent":"agent1"},"cap1")
    assert not ok
    assert result==DelegateResult.SELF_DELEGATION

def test_depth_exceeded():
    mgr=DelegationManager()
    for i in range(4):
        mgr.delegate({"caller":f"agent{i}","task_id":f"t{i}"},"cap")
    ok,result,_=mgr.delegate({"caller":"agent4","task_id":"t4"},"cap")
    assert not ok
    assert result==DelegateResult.DEPTH_EXCEEDED

def test_cycle_detected():
    mgr=DelegationManager()
    mgr.delegate({"caller":"agent1"},"cap")
    mgr.delegate({"caller":"agent2"},"cap")
    ok,result,_=mgr.delegate({"caller":"agent1"},"cap")
    assert not ok or result!=DelegateResult.GRANTED
