"""测试: GovernanceAdapter"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_governance_adapter import (
    A2AGovernanceAdapter,
    GovernanceCheckResult,
)


def test_scan_returns_check_results():
    ga = A2AGovernanceAdapter()
    results = ga.scan("orchestrator-1", "worker-1", "msg-1", "normal content")
    assert isinstance(results, list)
    assert len(results) >= 3
    assert all(isinstance(r, GovernanceCheckResult) for r in results)
    check_ids = [r.check_id for r in results]
    assert "rbac" in check_ids
    assert "content_size" in check_ids
    assert "rate_limit" in check_ids


def test_scan_rbac_check_passed():
    ga = A2AGovernanceAdapter()
    results = ga.scan("agent-a", "agent-b", "msg-2", "ok")
    rbac = [r for r in results if r.check_id == "rbac"][0]
    assert rbac.passed


def test_scan_oversized_content():
    ga = A2AGovernanceAdapter()
    big_content = "x" * 2_000_000
    results = ga.scan("agent-a", "agent-b", "msg-3", big_content)
    size_check = [r for r in results if r.check_id == "content_size"][0]
    assert not size_check.passed


def test_apply_policy():
    ga = A2AGovernanceAdapter()
    results = ga.scan("agent-a", "agent-b", "msg-4", "ok")
    policy = ga.apply_policy(results)
    assert "allowed" in policy
    assert "checks_total" in policy
    assert "checks_passed" in policy
    assert "block_reasons" in policy


def test_apply_policy_blocked_by_size():
    ga = A2AGovernanceAdapter()
    big_content = "x" * 2_000_000
    results = ga.scan("agent-a", "agent-b", "msg-5", big_content)
    policy = ga.apply_policy(results)
    assert not policy["allowed"]
    assert len(policy["block_reasons"]) > 0
