# [A_test] module_id: MOD-GOV_exceptions_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_exceptions
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试 AgentRbac 异常类型"""

from zephyr.security.access_control.exceptions import (
    AgentRbacError,
    ColdStartLockedError,
    DegradationBlockedError,
    KillSwitchTrippedError,
    OverrideTokenExpiredError,
    PermissionDeniedError,
)


class TestExceptions:
    def test_agent_rbac_error_inheritance(self):
        err = PermissionDeniedError("test")
        assert isinstance(err, AgentRbacError)
        assert isinstance(err, Exception)

    def test_permission_denied_fields(self):
        err = PermissionDeniedError("No access", operation="write:src", layer="L1", rule_id="RBAC-001")
        assert err.operation == "write:src"
        assert err.layer == "L1"
        assert err.rule_id == "RBAC-001"

    def test_cold_start_locked_defaults(self):
        err = ColdStartLockedError()
        assert err.layer == "L1"
        assert err.rule_id == "CSL-001"

    def test_override_token_expired(self):
        err = OverrideTokenExpiredError("expired", issued_at=1234567890)
        assert err.issued_at == 1234567890
        assert err.layer == "L1"

    def test_kill_switch_tripped(self):
        err = KillSwitchTrippedError("triggered", trigger="rapid_file_deletion")
        assert err.trigger == "rapid_file_deletion"
        assert err.layer == "L0"

    def test_degradation_blocked(self):
        err = DegradationBlockedError()
        assert err.layer == "L0"
        assert err.rule_id == "DEG-001"
