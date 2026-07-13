# [A_test] module_id: SRC-TST-1460 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_retirement_planner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.retirement_planner
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_retirement_planner.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.reliability.retirement_planner import RetirementPlanner


class TestRetirementPlannerInstantiation:
    def test_default_instantiation(self):
        rp = RetirementPlanner()
        assert rp.rules == {}

    def test_instantiation_with_rules(self):
        rp = RetirementPlanner(rules={"rule-001": 0.8})
        assert rp.rules["rule-001"] == 0.8


class TestMarkForRetirement:
    def test_mark_new_rule(self):
        rp = RetirementPlanner()
        rp.mark_for_retirement("rule-001")
        assert rp.rules["rule-001"] == -1.0

    def test_mark_overwrites_existing_rule(self):
        rp = RetirementPlanner(rules={"rule-001": 0.9})
        rp.mark_for_retirement("rule-001")
        assert rp.rules["rule-001"] == -1.0

    def test_mark_multiple_rules(self):
        rp = RetirementPlanner()
        rp.mark_for_retirement("rule-001")
        rp.mark_for_retirement("rule-002")
        assert rp.rules["rule-001"] == -1.0
        assert rp.rules["rule-002"] == -1.0
        assert len(rp.rules) == 2

    def test_retirement_value_is_negative(self):
        rp = RetirementPlanner()
        rp.mark_for_retirement("rule-003")
        assert rp.rules["rule-003"] < 0


class TestRetirementPlannerBoundaries:
    def test_mark_empty_string_rule_id(self):
        rp = RetirementPlanner()
        rp.mark_for_retirement("")
        assert rp.rules[""] == -1.0

    def test_mark_none_rule_id_accepted_by_dict(self):
        rp = RetirementPlanner()
        rp.mark_for_retirement(None)
        assert None in rp.rules

    def test_mark_idempotent(self):
        rp = RetirementPlanner()
        rp.mark_for_retirement("rule-004")
        rp.mark_for_retirement("rule-004")
        assert rp.rules["rule-004"] == -1.0
        assert len(rp.rules) == 1
