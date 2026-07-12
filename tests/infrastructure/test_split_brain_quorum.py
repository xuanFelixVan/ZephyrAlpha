# [A_test] module_id: SRC-TST-1671 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_split_brain_quorum
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.split_brain_quorum
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_split_brain_quorum.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.resilience.split_brain_quorum import (
    QuorumState,
    SplitBrainQuorum,
)


class TestSplitBrainQuorumInstantiation:
    def test_default_instantiation(self):
        sbq = SplitBrainQuorum(instance_id="inst-1")
        assert sbq.lease_ttl == 30.0
        assert sbq.min_instances == 2
        assert sbq.instance_id == "inst-1"
        assert sbq.state == QuorumState.IDLE
        assert sbq.current_owner == ""
        assert sbq.lease_expires_at == 0.0
        assert sbq.known_instances == {}

    def test_custom_instantiation(self):
        sbq = SplitBrainQuorum(lease_ttl=60.0, min_instances=3, instance_id="inst-2")
        assert sbq.lease_ttl == 60.0
        assert sbq.min_instances == 3


class TestHeartbeat:
    def test_heartbeat_registers_self(self):
        sbq = SplitBrainQuorum(instance_id="inst-1")
        sbq.heartbeat()
        assert "inst-1" in sbq.known_instances

    def test_heartbeat_expires_stale(self):
        sbq = SplitBrainQuorum(instance_id="inst-1", lease_ttl=0.001)
        sbq.known_instances["old"] = time.time() - 100
        sbq.heartbeat()
        assert "old" not in sbq.known_instances


class TestAcquire:
    def test_acquire_with_quorum(self):
        sbq = SplitBrainQuorum(instance_id="inst-1", min_instances=1)
        sbq.heartbeat()
        result = sbq.acquire("action-1")
        assert result is True
        assert sbq.state == QuorumState.OWNER
        assert sbq.current_owner == "inst-1"

    def test_acquire_without_quorum(self):
        sbq = SplitBrainQuorum(instance_id="inst-1", min_instances=5)
        sbq.heartbeat()
        result = sbq.acquire("action-1")
        assert result is False
        assert sbq.state == QuorumState.IDLE

    def test_acquire_while_already_owner(self):
        sbq = SplitBrainQuorum(instance_id="inst-1", min_instances=1, lease_ttl=9999.0)
        sbq.heartbeat()
        sbq.acquire("action-1")
        result = sbq.acquire("action-2")
        assert result is True


class TestRelease:
    def test_release_by_owner(self):
        sbq = SplitBrainQuorum(instance_id="inst-1", min_instances=1, lease_ttl=9999.0)
        sbq.heartbeat()
        sbq.acquire("action-1")
        sbq.release()
        assert sbq.current_owner == ""
        assert sbq.state == QuorumState.IDLE

    def test_release_by_non_owner_is_noop(self):
        sbq = SplitBrainQuorum(instance_id="inst-1", min_instances=1, lease_ttl=9999.0)
        sbq.heartbeat()
        sbq.acquire("action-1")
        sbq2 = SplitBrainQuorum(instance_id="inst-2")
        sbq2.current_owner = "inst-1"
        sbq2.release()
        assert sbq2.current_owner == "inst-1"


class TestIsOwner:
    def test_is_owner_when_active_lease(self):
        sbq = SplitBrainQuorum(instance_id="inst-1", min_instances=1, lease_ttl=9999.0)
        sbq.heartbeat()
        sbq.acquire("action-1")
        assert sbq.is_owner is True

    def test_not_owner_initially(self):
        sbq = SplitBrainQuorum(instance_id="inst-1")
        assert sbq.is_owner is False
