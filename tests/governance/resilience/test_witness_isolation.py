# [A_test] module_id: MOD-GOV_witness_isolation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_witness_isolation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_witness_isolation.py -q
# [TTL] task_bound

import pytest

from zephyr.governance.resilience_governance.witness_isolation import WitnessIsolator


class TestWitnessIsolatorInstantiation:
    def test_default_witnesses_empty(self):
        obj = WitnessIsolator()
        assert obj._witnesses == {}

    def test_initial_majority_is_no_decision(self):
        obj = WitnessIsolator()
        assert obj.majority_decision() == "no_decision"

    def test_initial_disagree_count_is_zero(self):
        obj = WitnessIsolator()
        with pytest.raises(ValueError):
            obj.disagree_count()


class TestRegisterWitness:
    def test_register_single_witness(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        assert obj._witnesses == {"w1": "approve"}

    def test_register_multiple_witnesses(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "reject")
        assert len(obj._witnesses) == 2

    def test_register_overwrites_existing(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w1", "reject")
        assert obj._witnesses["w1"] == "reject"


class TestMajorityDecision:
    def test_unanimous_decision(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "approve")
        obj.register_witness("w3", "approve")
        assert obj.majority_decision() == "approve"

    def test_majority_with_minority(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "approve")
        obj.register_witness("w3", "reject")
        assert obj.majority_decision() == "approve"

    def test_no_consensus_when_split(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "reject")
        assert obj.majority_decision() == "no_consensus"

    def test_single_witness_has_majority(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        assert obj.majority_decision() == "approve"

    def test_empty_returns_no_decision(self):
        obj = WitnessIsolator()
        assert obj.majority_decision() == "no_decision"

    def test_three_way_split_no_consensus(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "reject")
        obj.register_witness("w3", "abstain")
        assert obj.majority_decision() == "no_consensus"


class TestDisagreeCount:
    def test_unanimous_zero_disagree(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "approve")
        assert obj.disagree_count() == 0

    def test_two_against_one(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "approve")
        obj.register_witness("w3", "reject")
        assert obj.disagree_count() == 1

    def test_single_witness_zero_disagree(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        assert obj.disagree_count() == 0

    def test_even_split(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "reject")
        assert obj.disagree_count() == 1


class TestDisagreeCountBoundary:
    def test_five_witnesses_four_disagree(self):
        obj = WitnessIsolator()
        obj.register_witness("w1", "approve")
        obj.register_witness("w2", "reject")
        obj.register_witness("w3", "reject")
        obj.register_witness("w4", "reject")
        obj.register_witness("w5", "reject")
        assert obj.disagree_count() == 1

    def test_large_group_consensus(self):
        obj = WitnessIsolator()
        for i in range(100):
            obj.register_witness(f"w{i}", "approve")
        assert obj.disagree_count() == 0
