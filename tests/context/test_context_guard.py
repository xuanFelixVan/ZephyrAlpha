# [A_test] module_id: MOD-GOV_context_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-368 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_context_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_context_guard.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.infrastructure.reliability.context_guard import (
    AccessCheck,
    ContextGuard,
    ContextGuardResult,
)


class TestContextGuardInstantiation:
    def test_default_construction(self):
        guard = ContextGuard()
        assert guard._project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        guard = ContextGuard(project_root=tmp_path)
        assert guard._project_root == tmp_path


class TestValidateAccess:
    def test_all_allowed_files_pass(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": ["src/a.py", "src/b.py"],
            "forbidden_touch": [],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_access(task_card, ["src/a.py", "src/b.py"])
        assert result.all_allowed is True
        assert len(result.blocked_files) == 0
        assert len(result.warning_files) == 0

    def test_forbidden_file_is_blocked(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": ["src/a.py"],
            "forbidden_touch": ["src/secret.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_access(task_card, ["src/secret.py"])
        assert result.all_allowed is False
        assert "src/secret.py" in result.blocked_files
        assert len(result.checks) == 1
        assert result.checks[0].is_forbidden_touch is True

    def test_unlisted_file_generates_warning(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": ["src/a.py"],
            "forbidden_touch": [],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_access(task_card, ["src/unknown.py"])
        assert result.all_allowed is True
        assert "src/unknown.py" in result.warning_files
        assert len(result.blocked_files) == 0

    def test_upstream_files_are_allowed(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": [],
            "forbidden_touch": [],
            "upstream_files": [{"file_path": "src/input.py"}],
            "downstream_outputs": [],
        }
        result = guard.validate_access(task_card, ["src/input.py"])
        assert result.all_allowed is True
        assert result.checks[0].allowed is True

    def test_downstream_outputs_are_allowed(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": [],
            "forbidden_touch": [],
            "upstream_files": [],
            "downstream_outputs": [{"path": "src/output.py"}],
        }
        result = guard.validate_access(task_card, ["src/output.py"])
        assert result.all_allowed is True
        assert result.checks[0].allowed is True

    def test_empty_actual_touched(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": ["src/a.py"],
            "forbidden_touch": [],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_access(task_card, [])
        assert result.all_allowed is True
        assert len(result.checks) == 0

    def test_empty_task_card(self):
        guard = ContextGuard()
        result = guard.validate_access({}, ["src/a.py"])
        assert "src/a.py" in result.warning_files

    def test_none_task_card_fields(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": None,
            "forbidden_touch": None,
            "upstream_files": None,
            "downstream_outputs": None,
        }
        with pytest.raises(TypeError):
            guard.validate_access(task_card, ["src/a.py"])

    def test_forbidden_takes_priority_over_allowed(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": ["src/a.py"],
            "forbidden_touch": ["src/a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_access(task_card, ["src/a.py"])
        assert result.all_allowed is False
        assert "src/a.py" in result.blocked_files

    def test_allowed_touch_flag_set(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": ["src/a.py"],
            "forbidden_touch": [],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_access(task_card, ["src/a.py"])
        assert result.checks[0].is_allowed_touch is True

    def test_upstream_file_not_flagged_as_allowed_touch(self):
        guard = ContextGuard()
        task_card = {
            "allowed_touch": [],
            "forbidden_touch": [],
            "upstream_files": [{"file_path": "src/up.py"}],
            "downstream_outputs": [],
        }
        result = guard.validate_access(task_card, ["src/up.py"])
        assert result.checks[0].is_allowed_touch is False


class TestCheckForbidden:
    def test_forbidden_files_detected(self):
        guard = ContextGuard()
        checks = guard.check_forbidden(
            ["src/a.py", "src/b.py"],
            ["src/a.py"],
        )
        assert len(checks) == 1
        assert checks[0].file_path == "src/a.py"
        assert checks[0].allowed is False
        assert checks[0].is_forbidden_touch is True

    def test_no_forbidden_files(self):
        guard = ContextGuard()
        checks = guard.check_forbidden(
            ["src/a.py"],
            ["src/b.py"],
        )
        assert len(checks) == 0

    def test_empty_actual_touched(self):
        guard = ContextGuard()
        checks = guard.check_forbidden([], ["src/a.py"])
        assert len(checks) == 0

    def test_empty_forbidden_list(self):
        guard = ContextGuard()
        checks = guard.check_forbidden(["src/a.py"], [])
        assert len(checks) == 0

    def test_all_files_forbidden(self):
        guard = ContextGuard()
        checks = guard.check_forbidden(
            ["src/a.py", "src/b.py"],
            ["src/a.py", "src/b.py"],
        )
        assert len(checks) == 2


class TestAccessCheckDataclass:
    def test_default_values(self):
        check = AccessCheck(file_path="a.py", allowed=True, reason="ok")
        assert check.is_allowed_touch is False
        assert check.is_forbidden_touch is False


class TestContextGuardResultDataclass:
    def test_fields(self):
        result = ContextGuardResult(
            all_allowed=True,
            checks=[],
            blocked_files=[],
            warning_files=[],
        )
        assert result.all_allowed is True
        assert len(result.checks) == 0
