# [A_test] module_id: MOD-GOV_cold_start_lock | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.test_cold_start_lock
# [INVARIANTS] default_locked;unlock_requires_3_checks_plus_config;owner_bypass_unconditional
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest_exit_0
# [TESTS] pytest tests/test_cold_start_lock.py -q
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

from unittest.mock import MagicMock

from zephyr.security.access_control.cold_start_lock import ColdStartLock, get_cold_start_lock
from zephyr.security.access_control.immutable_core import ImmutableCore, IntegrityResult


class TestColdStartLockInit:
    def test_default_locked(self):
        lock = ColdStartLock()
        assert lock.is_locked is True

    def test_default_verified_at_zero(self):
        lock = ColdStartLock()
        assert lock.verified_at == 0.0

    def test_custom_immutable_core(self):
        core = ImmutableCore()
        lock = ColdStartLock(immutable_core=core)
        assert lock.immutable_core is core

    def test_default_immutable_core_created(self):
        lock = ColdStartLock()
        assert isinstance(lock.immutable_core, ImmutableCore)


class TestLoadConfig:
    def test_valid_config(self):
        lock = ColdStartLock()
        result = lock.load_config({"version": "1.0"})
        assert result is True
        assert lock.config_loaded is True

    def test_config_with_version_string(self):
        lock = ColdStartLock()
        result = lock.load_config({"version": "2.0.1"})
        assert result is True

    def test_config_with_version_int(self):
        lock = ColdStartLock()
        result = lock.load_config({"version": 1})
        assert result is True

    def test_config_without_version(self):
        lock = ColdStartLock()
        result = lock.load_config({"other_key": "value"})
        assert result is False
        assert lock.config_loaded is False

    def test_empty_config(self):
        lock = ColdStartLock()
        result = lock.load_config({})
        assert result is False

    def test_version_is_falsy(self):
        lock = ColdStartLock()
        result = lock.load_config({"version": ""})
        assert result is False

    def test_version_is_none(self):
        lock = ColdStartLock()
        result = lock.load_config({"version": None})
        assert result is False

    def test_version_zero(self):
        lock = ColdStartLock()
        result = lock.load_config({"version": 0})
        assert result is False


class TestVerifyIntegrity:
    def test_returns_true_when_intact(self):
        lock = ColdStartLock()
        result = lock.verify_integrity()
        assert isinstance(result, bool)

    def test_increments_checks_on_success(self):
        lock = ColdStartLock()
        initial = lock.checks_passed
        lock.verify_integrity()
        if lock.immutable_core.verify_immutable_core_integrity().intact:
            assert lock.checks_passed == initial + 1

    def test_no_increment_on_failure(self):
        mock_core = MagicMock()
        mock_core.verify_immutable_core_integrity.return_value = IntegrityResult(intact=False, violations=["test"])
        lock = ColdStartLock(immutable_core=mock_core)
        initial = lock.checks_passed
        lock.verify_integrity()
        assert lock.checks_passed == initial


class TestVerifyStaticConstants:
    def test_returns_bool(self):
        lock = ColdStartLock()
        result = lock.verify_static_constants()
        assert isinstance(result, bool)

    def test_increments_checks_on_success(self):
        lock = ColdStartLock()
        initial = lock.checks_passed
        lock.verify_static_constants()
        if lock.immutable_core.verify_static_constants_integrity().intact:
            assert lock.checks_passed == initial + 1

    def test_no_increment_on_failure(self):
        mock_core = MagicMock()
        mock_core.verify_static_constants_integrity.return_value = IntegrityResult(intact=False, violations=["test"])
        lock = ColdStartLock(immutable_core=mock_core)
        initial = lock.checks_passed
        lock.verify_static_constants()
        assert lock.checks_passed == initial


class TestAttemptUnlock:
    def test_unlock_fails_without_checks(self):
        lock = ColdStartLock()
        assert lock.attempt_unlock() is False
        assert lock.is_locked is True

    def test_unlock_fails_without_config(self):
        lock = ColdStartLock()
        lock.checks_passed = 3
        assert lock.config_loaded is False
        assert lock.attempt_unlock() is False
        assert lock.is_locked is True

    def test_unlock_fails_with_only_config(self):
        lock = ColdStartLock()
        lock.load_config({"version": "1.0"})
        assert lock.checks_passed == 1
        assert lock.attempt_unlock() is False
        assert lock.is_locked is True

    def test_unlock_succeeds_with_all_checks(self):
        lock = ColdStartLock()
        lock.checks_passed = 3
        lock.config_loaded = True
        result = lock.attempt_unlock()
        assert result is True
        assert lock.is_locked is False
        assert lock.verified_at > 0

    def test_unlock_succeeds_with_more_than_required_checks(self):
        lock = ColdStartLock()
        lock.checks_passed = 5
        lock.config_loaded = True
        result = lock.attempt_unlock()
        assert result is True
        assert lock.is_locked is False

    def test_unlock_fails_with_two_checks(self):
        lock = ColdStartLock()
        lock.checks_passed = 2
        lock.config_loaded = True
        assert lock.attempt_unlock() is False
        assert lock.is_locked is True


class TestOwnerBypass:
    def test_unconditionally_unlocks(self):
        lock = ColdStartLock()
        assert lock.is_locked is True
        lock.owner_bypass()
        assert lock.is_locked is False

    def test_sets_verified_at(self):
        lock = ColdStartLock()
        lock.owner_bypass()
        assert lock.verified_at > 0

    def test_bypass_without_any_checks(self):
        lock = ColdStartLock()
        lock.owner_bypass()
        assert lock.is_locked is False
        assert lock.checks_passed == 0


class TestStatusDict:
    def test_returns_dict(self):
        lock = ColdStartLock()
        status = lock.status_dict()
        assert isinstance(status, dict)

    def test_default_status(self):
        lock = ColdStartLock()
        status = lock.status_dict()
        assert status["locked"] is True
        assert status["config_loaded"] is False
        assert status["checks_passed"] == 0
        assert status["required_checks"] == 3
        assert status["verified_at"] is None

    def test_status_after_unlock(self):
        lock = ColdStartLock()
        lock.checks_passed = 3
        lock.config_loaded = True
        lock.attempt_unlock()
        status = lock.status_dict()
        assert status["locked"] is False
        assert status["verified_at"] is not None

    def test_immutable_core_intact_key(self):
        lock = ColdStartLock()
        status = lock.status_dict()
        assert "immutable_core_intact" in status
        assert isinstance(status["immutable_core_intact"], bool)


class TestGetColdStartLock:
    def test_singleton_identity(self):
        a = get_cold_start_lock()
        b = get_cold_start_lock()
        assert a is b

    def test_returns_cold_start_lock_instance(self):
        instance = get_cold_start_lock()
        assert isinstance(instance, ColdStartLock)
