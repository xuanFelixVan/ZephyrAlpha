# [A_test] module_id: SRC-TST-1300 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_multi_instance_coord
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.multi_instance_coord
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_multi_instance_coord.py
# [TTL] task_bound


from zephyr.feedback_loop.resilience.multi_instance_coord import (
    InstanceInfo,
    InstanceRole,
    MultiInstanceCoord,
)


class TestMultiInstanceCoordInstantiation:
    def test_default_instantiation(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        assert mic.instance_id == "node-1"
        assert mic.peers == []
        assert mic.role == InstanceRole.FOLLOWER
        assert mic.current_term == 0
        assert mic.voted_for is None
        assert mic.leader_id is None

    def test_custom_instantiation(self):
        mic = MultiInstanceCoord(
            instance_id="node-2",
            peers=["node-1", "node-3"],
            role=InstanceRole.CANDIDATE,
            current_term=5,
        )
        assert mic.peers == ["node-1", "node-3"]
        assert mic.role == InstanceRole.CANDIDATE
        assert mic.current_term == 5


class TestStartElection:
    def test_start_election_increments_term(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        mic.start_election()
        assert mic.current_term == 1
        assert mic.role == InstanceRole.CANDIDATE
        assert mic.voted_for == "node-1"

    def test_start_election_multiple_times(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        mic.start_election()
        mic.start_election()
        assert mic.current_term == 2


class TestBecomeLeader:
    def test_become_leader(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        mic.become_leader()
        assert mic.role == InstanceRole.LEADER
        assert mic.leader_id == "node-1"
        assert mic.is_leader is True


class TestStepDown:
    def test_step_down(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        mic.become_leader()
        mic.step_down()
        assert mic.role == InstanceRole.FOLLOWER
        assert mic.leader_id is None
        assert mic.is_leader is False


class TestCheckSplitBrain:
    def test_split_brain_detected(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        mic.become_leader()
        assert mic.check_split_brain("node-2") is True

    def test_no_split_brain_self(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        mic.become_leader()
        assert mic.check_split_brain("node-1") is False

    def test_no_split_brain_empty(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        mic.become_leader()
        assert mic.check_split_brain("") is False

    def test_no_split_brain_as_follower(self):
        mic = MultiInstanceCoord(instance_id="node-1")
        assert mic.check_split_brain("node-2") is False


class TestInstanceInfo:
    def test_instance_info_defaults(self):
        info = InstanceInfo(instance_id="n1")
        assert info.role == InstanceRole.FOLLOWER
        assert info.term == 0
