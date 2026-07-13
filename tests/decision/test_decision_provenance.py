# [A_test] module_id: SRC-TST-0719 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_decision_provenance
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_decision_provenance.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.correlation.decision_provenance import DecisionProvenance


class TestDecisionProvenanceInstantiation:
    def test_default_instantiation(self):
        dp = DecisionProvenance()
        assert dp is not None
        assert dp.decisions == []

    def test_is_dataclass(self):
        dp = DecisionProvenance()
        assert hasattr(dp, "__dataclass_fields__")

    def test_default_decisions_is_empty(self):
        dp = DecisionProvenance()
        assert len(dp.decisions) == 0


class TestRecord:
    def test_record_appends_decision(self):
        dp = DecisionProvenance()
        dp.record({"action": "repair", "target": "module_a"})
        assert len(dp.decisions) == 1
        assert dp.decisions[0]["action"] == "repair"

    def test_record_multiple_decisions(self):
        dp = DecisionProvenance()
        dp.record({"action": "repair", "target": "module_a"})
        dp.record({"action": "rollback", "target": "module_b"})
        assert len(dp.decisions) == 2

    def test_record_preserves_order(self):
        dp = DecisionProvenance()
        dp.record({"step": 1})
        dp.record({"step": 2})
        dp.record({"step": 3})
        assert [d["step"] for d in dp.decisions] == [1, 2, 3]

    def test_record_empty_dict(self):
        dp = DecisionProvenance()
        dp.record({})
        assert len(dp.decisions) == 1
        assert dp.decisions[0] == {}

    def test_record_with_nested_data(self):
        dp = DecisionProvenance()
        dp.record({"action": "repair", "factors": {"severity": "high", "confidence": 0.9}})
        assert dp.decisions[0]["factors"]["severity"] == "high"
