# [A_test] module_id: SRC-TST-1549 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_self_audit
# [INVARIANTS] SelfAudit.policy_violations is list[dict]
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_self_audit.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.guard.self_audit import SelfAudit


class TestSelfAuditInstantiation:
    def test_default_violations_empty(self):
        obj = SelfAudit()
        assert obj.policy_violations == []

    def test_custom_violations(self):
        violations = [{"rule": "R001", "detail": "breach"}]
        obj = SelfAudit(policy_violations=violations)
        assert obj.policy_violations == violations

    def test_violations_is_list_type(self):
        obj = SelfAudit()
        assert isinstance(obj.policy_violations, list)


class TestSelfAuditPolicyViolations:
    def test_append_violation(self):
        obj = SelfAudit()
        obj.policy_violations.append({"rule": "R001", "detail": "breach"})
        assert len(obj.policy_violations) == 1
        assert obj.policy_violations[0]["rule"] == "R001"

    def test_multiple_violations(self):
        obj = SelfAudit()
        obj.policy_violations.append({"rule": "R001"})
        obj.policy_violations.append({"rule": "R002"})
        assert len(obj.policy_violations) == 2

    def test_separate_instances_independent(self):
        a = SelfAudit()
        b = SelfAudit()
        a.policy_violations.append({"rule": "R001"})
        assert len(b.policy_violations) == 0

    def test_violation_dict_structure(self):
        obj = SelfAudit()
        violation = {"rule": "R183", "action": "repair", "severity": "high"}
        obj.policy_violations.append(violation)
        assert obj.policy_violations[0]["severity"] == "high"
