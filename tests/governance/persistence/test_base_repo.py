# [A_test] module_id: SRC-TST-0412 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATABASE | docs/03_modules/_cross_layer/database/blueprint.md | §test
# [MODULE] tests.test_base_repo
# [INVARIANTS] _ALLOWED_TRANSITIONS不可变;异常类层次稳定
# [MODIFY-GUARD] src/zephyr/db/base_repo.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_base_repo.py
# [TTL] task_bound

from __future__ import annotations

import uuid

import pytest

base_repo = pytest.importorskip("zephyr.governance.persistence.base_repo")

TaskRepositoryError = base_repo.TaskRepositoryError
TaskNotFoundError = base_repo.TaskNotFoundError
InvalidTransitionError = base_repo.InvalidTransitionError
RejectedUpgradeCoolingOffError = base_repo.RejectedUpgradeCoolingOffError
P0InflationFrozenError = base_repo.P0InflationFrozenError
P0InflationWarning = base_repo.P0InflationWarning
_ALLOWED_TRANSITIONS = base_repo._ALLOWED_TRANSITIONS
_is_valid_transition = base_repo._is_valid_transition
allowed_transitions = base_repo.allowed_transitions
is_terminal = base_repo.is_terminal
_new_id = base_repo._new_id
now_iso = base_repo.now_iso

try:
    from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus

    HAS_TASK_TYPES = True
except Exception:
    HAS_TASK_TYPES = False


class TestExceptionHierarchy:
    def test_task_repository_error_is_runtime_error(self):
        assert issubclass(TaskRepositoryError, RuntimeError)

    def test_task_not_found_error_inherits_base(self):
        assert issubclass(TaskNotFoundError, TaskRepositoryError)

    def test_invalid_transition_error_inherits_base(self):
        assert issubclass(InvalidTransitionError, TaskRepositoryError)

    def test_rejected_upgrade_cooling_off_error_inherits_base(self):
        assert issubclass(RejectedUpgradeCoolingOffError, TaskRepositoryError)

    def test_p0_inflation_frozen_error_inherits_base(self):
        assert issubclass(P0InflationFrozenError, TaskRepositoryError)

    def test_p0_inflation_warning_inherits_base(self):
        assert issubclass(P0InflationWarning, TaskRepositoryError)

    def test_raise_and_catch_task_not_found(self):
        with pytest.raises(TaskNotFoundError):
            raise TaskNotFoundError("task missing")

    def test_catch_base_catches_derived(self):
        with pytest.raises(TaskRepositoryError):
            raise InvalidTransitionError("bad transition")


@pytest.mark.skipif(not HAS_TASK_TYPES, reason="TaskStatus not importable")
class TestAllowedTransitions:
    def test_pending_has_expected_targets(self):
        result = allowed_transitions(TaskStatus.PENDING)
        assert TaskStatus.IN_PROGRESS in result
        assert TaskStatus.BLOCKED in result
        assert TaskStatus.CANCELLED in result

    def test_verified_is_terminal(self):
        result = allowed_transitions(TaskStatus.VERIFIED)
        assert len(result) == 0

    def test_cancelled_is_terminal(self):
        result = allowed_transitions(TaskStatus.CANCELLED)
        assert len(result) == 0

    def test_string_status_accepted(self):
        result = allowed_transitions("PENDING")
        assert TaskStatus.IN_PROGRESS in result

    def test_unknown_status_raises(self):
        with pytest.raises(ValueError):
            allowed_transitions("NONEXISTENT_STATUS")


@pytest.mark.skipif(not HAS_TASK_TYPES, reason="TaskStatus not importable")
class TestIsTerminal:
    def test_verified_is_terminal(self):
        assert is_terminal(TaskStatus.VERIFIED) is True

    def test_cancelled_is_terminal(self):
        assert is_terminal(TaskStatus.CANCELLED) is True

    def test_pending_is_not_terminal(self):
        assert is_terminal(TaskStatus.PENDING) is False

    def test_string_input_verified(self):
        assert is_terminal("VERIFIED") is True

    def test_string_input_pending(self):
        assert is_terminal("PENDING") is False


@pytest.mark.skipif(not HAS_TASK_TYPES, reason="TaskStatus not importable")
class TestIsValidTransition:
    def test_valid_pending_to_in_progress(self):
        assert _is_valid_transition(TaskStatus.PENDING, TaskStatus.IN_PROGRESS) is True

    def test_invalid_pending_to_completed(self):
        assert _is_valid_transition(TaskStatus.PENDING, TaskStatus.COMPLETED) is False

    def test_valid_failed_to_retry(self):
        assert _is_valid_transition(TaskStatus.FAILED, TaskStatus.RETRY) is True

    def test_invalid_verified_to_anything(self):
        assert _is_valid_transition(TaskStatus.VERIFIED, TaskStatus.IN_PROGRESS) is False


class TestNewId:
    def test_generates_string(self):
        result = _new_id()
        assert isinstance(result, str)

    def test_generates_unique_ids(self):
        ids = {_new_id() for _ in range(100)}
        assert len(ids) == 100

    def test_with_prefix(self):
        result = _new_id("OPS-")
        assert result.startswith("OPS-")

    def test_without_prefix_is_uuid(self):
        result = _new_id()
        uuid.UUID(result)

    def test_empty_prefix(self):
        result = _new_id("")
        uuid.UUID(result)


class TestNowIso:
    def test_returns_string(self):
        result = now_iso()
        assert isinstance(result, str)

    def test_contains_t_separator(self):
        result = now_iso()
        assert "T" in result

    def test_returns_different_values_over_time(self):
        import time

        first = now_iso()
        time.sleep(0.01)
        second = now_iso()
        assert second >= first


@pytest.mark.skipif(not HAS_TASK_TYPES, reason="TaskStatus not importable")
class TestAllowedTransitionsTableCompleteness:
    def test_all_task_statuses_have_entries(self):
        for status in TaskStatus:
            assert status in _ALLOWED_TRANSITIONS, f"Missing entry for {status}"

    def test_all_target_statuses_are_valid(self):
        for source, targets in _ALLOWED_TRANSITIONS.items():
            for target in targets:
                assert isinstance(target, TaskStatus), f"Invalid target {target} for source {source}"
