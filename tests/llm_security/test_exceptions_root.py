# [A_test] module_id: SRC-TST-0877 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.test_exceptions
# [INVARIANTS] all_exceptions_inherit_AgentRbacError;default_messages_match_source
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest_exit_0
# [TESTS] pytest tests/test_exceptions.py -q
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

from zephyr.security.access_control.exceptions import (
    AgentRbacError,
    ColdStartLockedError,
    DegradationBlockedError,
    KillSwitchTrippedError,
    OverrideTokenExpiredError,
    PermissionDeniedError,
)


class TestAgentRbacError:
    def test_default_message(self):
        err = AgentRbacError()
        assert str(err) == "Agent RBAC error"

    def test_custom_message(self):
        err = AgentRbacError(message="custom")
        assert str(err) == "custom"

    def test_default_layer_and_rule_id(self):
        err = AgentRbacError()
        assert err.layer == ""
        assert err.rule_id == ""

    def test_custom_layer_and_rule_id(self):
        err = AgentRbacError(layer="L0", rule_id="R-001")
        assert err.layer == "L0"
        assert err.rule_id == "R-001"

    def test_is_exception(self):
        assert issubclass(AgentRbacError, Exception)

    def test_raise_and_catch(self):
        with pytest.raises(AgentRbacError) as exc_info:
            raise AgentRbacError(message="boom", layer="L1", rule_id="X")
        assert exc_info.value.layer == "L1"
        assert exc_info.value.rule_id == "X"
        assert str(exc_info.value) == "boom"

    def test_empty_string_args(self):
        err = AgentRbacError(message="", layer="", rule_id="")
        assert str(err) == ""
        assert err.layer == ""
        assert err.rule_id == ""


class TestPermissionDeniedError:
    def test_default_message(self):
        err = PermissionDeniedError()
        assert str(err) == "Permission denied"

    def test_inherits_agent_rbac_error(self):
        assert issubclass(PermissionDeniedError, AgentRbacError)

    def test_operation_attribute(self):
        err = PermissionDeniedError(operation="write")
        assert err.operation == "write"

    def test_default_operation(self):
        err = PermissionDeniedError()
        assert err.operation == ""

    def test_layer_and_rule_id_propagated(self):
        err = PermissionDeniedError(layer="L2", rule_id="PD-001")
        assert err.layer == "L2"
        assert err.rule_id == "PD-001"

    def test_catch_as_base_class(self):
        with pytest.raises(AgentRbacError):
            raise PermissionDeniedError(operation="delete")


class TestColdStartLockedError:
    def test_default_message(self):
        err = ColdStartLockedError()
        assert str(err) == "System is in cold-start lock"

    def test_inherits_agent_rbac_error(self):
        assert issubclass(ColdStartLockedError, AgentRbacError)

    def test_fixed_layer(self):
        err = ColdStartLockedError()
        assert err.layer == "L1"

    def test_fixed_rule_id(self):
        err = ColdStartLockedError()
        assert err.rule_id == "CSL-001"

    def test_custom_message(self):
        err = ColdStartLockedError(message="locked out")
        assert str(err) == "locked out"
        assert err.layer == "L1"
        assert err.rule_id == "CSL-001"


class TestOverrideTokenExpiredError:
    def test_default_message(self):
        err = OverrideTokenExpiredError()
        assert str(err) == "Override token expired"

    def test_inherits_agent_rbac_error(self):
        assert issubclass(OverrideTokenExpiredError, AgentRbacError)

    def test_issued_at_attribute(self):
        err = OverrideTokenExpiredError(issued_at=1700000000.0)
        assert err.issued_at == 1700000000.0

    def test_default_issued_at(self):
        err = OverrideTokenExpiredError()
        assert err.issued_at == 0.0

    def test_layer_and_rule_id(self):
        err = OverrideTokenExpiredError()
        assert err.layer == "L1"
        assert err.rule_id == "OVR-001"

    def test_zero_issued_at(self):
        err = OverrideTokenExpiredError(issued_at=0.0)
        assert err.issued_at == 0.0


class TestKillSwitchTrippedError:
    def test_default_message(self):
        err = KillSwitchTrippedError()
        assert str(err) == "Kill switch tripped"

    def test_inherits_agent_rbac_error(self):
        assert issubclass(KillSwitchTrippedError, AgentRbacError)

    def test_trigger_attribute(self):
        err = KillSwitchTrippedError(trigger="manual")
        assert err.trigger == "manual"

    def test_default_trigger(self):
        err = KillSwitchTrippedError()
        assert err.trigger == ""

    def test_layer_and_rule_id(self):
        err = KillSwitchTrippedError()
        assert err.layer == "L0"
        assert err.rule_id == "KSW-001"

    def test_empty_trigger(self):
        err = KillSwitchTrippedError(trigger="")
        assert err.trigger == ""


class TestDegradationBlockedError:
    def test_default_message(self):
        err = DegradationBlockedError()
        assert str(err) == "Engine degraded — all operations blocked"

    def test_inherits_agent_rbac_error(self):
        assert issubclass(DegradationBlockedError, AgentRbacError)

    def test_fixed_layer(self):
        err = DegradationBlockedError()
        assert err.layer == "L0"

    def test_fixed_rule_id(self):
        err = DegradationBlockedError()
        assert err.rule_id == "DEG-001"

    def test_catch_as_base_class(self):
        with pytest.raises(AgentRbacError):
            raise DegradationBlockedError()
