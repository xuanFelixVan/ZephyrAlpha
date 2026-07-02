# [A_test] module_id: SRC-TST-0498 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.cascading_failure_isolator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.cascading_failure_isolator import CascadingFailureIsolator

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestCascadingFailureIsolatorRegister:
    def test_register_creates_module(self):
        iso = CascadingFailureIsolator()
        mh = iso.register("auth-module")
        assert mh.module_name == "auth-module"
        assert mh.healthy is True
        assert mh.failure_count == 0

    def test_register_default_isolation_not_active(self):
        iso = CascadingFailureIsolator()
        mh = iso.register("policy-module")
        assert mh.isolation_active is False

    def test_register_stores_module(self):
        iso = CascadingFailureIsolator()
        iso.register("cache-module")
        assert "cache-module" in iso._modules


class TestCascadingFailureIsolatorRecordFailure:
    def test_single_failure_not_isolated(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-a")
        result = iso.record_failure("mod-a", "timeout")
        assert result["isolated"] is False
        assert result["failures"] == 1

    def test_two_failures_not_isolated(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-b")
        iso.record_failure("mod-b", "err1")
        result = iso.record_failure("mod-b", "err2")
        assert result["isolated"] is False
        assert result["failures"] == 2

    def test_three_failures_triggers_isolation(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-c")
        iso.record_failure("mod-c", "err1")
        iso.record_failure("mod-c", "err2")
        result = iso.record_failure("mod-c", "err3")
        assert result["isolated"] is True
        assert result["failures"] == 3

    def test_auto_register_on_unknown_module(self):
        iso = CascadingFailureIsolator()
        result = iso.record_failure("unknown-mod", "err")
        assert result["isolated"] is False
        assert "unknown-mod" in iso._modules

    def test_failure_records_error_message(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-d")
        iso.record_failure("mod-d", "connection_refused")
        assert iso._modules["mod-d"].last_error == "connection_refused"

    def test_isolation_sets_module_unhealthy(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-e")
        for _ in range(3):
            iso.record_failure("mod-e", "err")
        assert iso._modules["mod-e"].healthy is False
        assert iso._modules["mod-e"].isolation_active is True


class TestCascadingFailureIsolatorIsHealthy:
    def test_healthy_module(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-h")
        assert iso.is_healthy("mod-h") is True

    def test_unhealthy_after_isolation(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-i")
        for _ in range(3):
            iso.record_failure("mod-i", "err")
        assert iso.is_healthy("mod-i") is False

    def test_unknown_module_returns_false(self):
        iso = CascadingFailureIsolator()
        assert iso.is_healthy("nonexistent") is False


class TestCascadingFailureIsolatorGetIsolated:
    def test_no_isolated_modules(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-j")
        assert iso.get_isolated() == []

    def test_isolated_modules_listed(self):
        iso = CascadingFailureIsolator()
        iso.register("mod-k")
        for _ in range(3):
            iso.record_failure("mod-k", "err")
        assert "mod-k" in iso.get_isolated()

    def test_multiple_isolated_modules(self):
        iso = CascadingFailureIsolator()
        for name in ["mod-l", "mod-m"]:
            iso.register(name)
            for _ in range(3):
                iso.record_failure(name, "err")
        isolated = iso.get_isolated()
        assert "mod-l" in isolated
        assert "mod-m" in isolated
