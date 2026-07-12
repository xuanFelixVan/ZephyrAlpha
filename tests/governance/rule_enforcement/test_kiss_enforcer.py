# [A_test] module_id: SRC-TST-1189 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_kiss_enforcer
# [INVARIANTS] KissEnforcer.MAX_CLASSES=3;MAX_METHOD_LINES=30;MAX_INHERITANCE=2
# [MODIFY-GUARD] source-change:re-read-kiss_enforcer
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises:TypeError-on-non-int-input
# [TESTS] self
# [TTL] task_bound

import pytest

from zephyr.gov_enforcement.rule_enforcement.kiss_enforcer import KissEnforcer


class TestKissEnforcerInstantiation:
    def test_default_constants(self):
        enforcer = KissEnforcer()
        assert enforcer.MAX_CLASSES == 3
        assert enforcer.MAX_METHOD_LINES == 30
        assert enforcer.MAX_INHERITANCE == 2

    def test_instance_is_independent(self):
        a = KissEnforcer()
        b = KissEnforcer()
        a.MAX_CLASSES = 99
        assert b.MAX_CLASSES == 3


class TestCheckClassCount:
    def test_within_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_class_count(2)
        assert passed is True
        assert msg == "OK"

    def test_at_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_class_count(3)
        assert passed is True
        assert msg == "OK"

    def test_over_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_class_count(4)
        assert passed is False
        assert "4" in msg and "3" in msg

    def test_zero(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_class_count(0)
        assert passed is True
        assert msg == "OK"

    def test_negative(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_class_count(-1)
        assert passed is True
        assert msg == "OK"

    def test_none_raises(self):
        enforcer = KissEnforcer()
        with pytest.raises(TypeError):
            enforcer.check_class_count(None)

    def test_string_raises(self):
        enforcer = KissEnforcer()
        with pytest.raises(TypeError):
            enforcer.check_class_count("three")


class TestCheckMethodLength:
    def test_within_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_method_length(20)
        assert passed is True
        assert msg == "OK"

    def test_at_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_method_length(30)
        assert passed is True
        assert msg == "OK"

    def test_over_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_method_length(31)
        assert passed is False
        assert "31" in msg and "30" in msg

    def test_zero(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_method_length(0)
        assert passed is True
        assert msg == "OK"

    def test_none_raises(self):
        enforcer = KissEnforcer()
        with pytest.raises(TypeError):
            enforcer.check_method_length(None)

    def test_float_accepted(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_method_length(10.5)
        assert passed is True
        assert msg == "OK"


class TestCheckInheritanceDepth:
    def test_within_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_inheritance_depth(1)
        assert passed is True
        assert msg == "OK"

    def test_at_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_inheritance_depth(2)
        assert passed is True
        assert msg == "OK"

    def test_over_limit(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_inheritance_depth(3)
        assert passed is False
        assert "3" in msg and "2" in msg

    def test_zero(self):
        enforcer = KissEnforcer()
        passed, msg = enforcer.check_inheritance_depth(0)
        assert passed is True
        assert msg == "OK"

    def test_none_raises(self):
        enforcer = KissEnforcer()
        with pytest.raises(TypeError):
            enforcer.check_inheritance_depth(None)


class TestSelfCheck:
    def test_all_pass(self):
        enforcer = KissEnforcer()
        assert enforcer.self_check(2, 25, 1) is True

    def test_all_at_boundary(self):
        enforcer = KissEnforcer()
        assert enforcer.self_check(3, 30, 2) is True

    def test_class_count_fails(self):
        enforcer = KissEnforcer()
        assert enforcer.self_check(4, 25, 1) is False

    def test_method_length_fails(self):
        enforcer = KissEnforcer()
        assert enforcer.self_check(2, 31, 1) is False

    def test_inheritance_depth_fails(self):
        enforcer = KissEnforcer()
        assert enforcer.self_check(2, 25, 3) is False

    def test_all_fail(self):
        enforcer = KissEnforcer()
        assert enforcer.self_check(4, 31, 3) is False

    def test_zero_values(self):
        enforcer = KissEnforcer()
        assert enforcer.self_check(0, 0, 0) is True

    def test_none_raises(self):
        enforcer = KissEnforcer()
        with pytest.raises(TypeError):
            enforcer.self_check(None, 25, 1)
