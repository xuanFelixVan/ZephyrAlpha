# [A_test] module_id: MOD-GOV_sandbox_enforcer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_sandbox_enforcer
# [INVARIANTS] SandboxEnforcer exit code 39 on breach; NONE mode never breaches
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.runtime.sandbox_enforcer import (
    SandboxBreachResult,
    SandboxEnforcer,
    SandboxMode,
    SandboxStatus,
)


class TestSandboxMode:
    def test_enum_values(self):
        assert SandboxMode.STRICT.value == "strict"
        assert SandboxMode.LAX.value == "lax"
        assert SandboxMode.NONE.value == "none"

    def test_str_enum_comparison(self):
        assert SandboxMode.STRICT == "strict"
        assert SandboxMode.LAX == "lax"


class TestSandboxEnforcerInit:
    def test_default_project_root(self):
        enforcer = SandboxEnforcer()
        assert enforcer.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        assert enforcer.project_root == tmp_path

    def test_default_mode_strict(self):
        enforcer = SandboxEnforcer()
        assert enforcer.mode == SandboxMode.STRICT

    def test_custom_mode(self):
        enforcer = SandboxEnforcer(mode=SandboxMode.LAX)
        assert enforcer.mode == SandboxMode.LAX

    def test_mode_property(self):
        enforcer = SandboxEnforcer(mode=SandboxMode.NONE)
        assert enforcer.mode == SandboxMode.NONE


class TestIsInSandbox:
    def test_not_in_sandbox_by_default(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        assert enforcer.is_in_sandbox() is False

    def test_in_sandbox_after_activate(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        enforcer.activate_sandbox()
        assert enforcer.is_in_sandbox() is True

    def test_not_in_sandbox_after_deactivate(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        enforcer.activate_sandbox()
        enforcer.deactivate_sandbox()
        assert enforcer.is_in_sandbox() is False


class TestEnforce:
    def test_breach_when_not_in_sandbox_strict(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.STRICT)
        result = enforcer.enforce()
        assert isinstance(result, SandboxBreachResult)
        assert result.breached is True
        assert result.exit_code == 39
        assert result.mitigating_action == "SUSPEND_AGENT_EXECUTION"

    def test_breach_when_not_in_sandbox_lax(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.LAX)
        result = enforcer.enforce()
        assert result.breached is True
        assert result.exit_code == 39

    def test_no_breach_when_none_mode(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.NONE)
        result = enforcer.enforce()
        assert result.breached is False
        assert result.exit_code == 0

    def test_no_breach_when_in_sandbox(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.STRICT)
        enforcer.activate_sandbox()
        result = enforcer.enforce()
        assert result.breached is False
        assert result.exit_code == 0


class TestActivateDeactivate:
    def test_activate_creates_marker(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        assert enforcer.activate_sandbox() is True
        marker = tmp_path / ".zephyr" / "sandbox_active"
        assert marker.exists()

    def test_deactivate_removes_marker(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        enforcer.activate_sandbox()
        assert enforcer.deactivate_sandbox() is True
        marker = tmp_path / ".zephyr" / "sandbox_active"
        assert not marker.exists()

    def test_deactivate_when_not_active(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        assert enforcer.deactivate_sandbox() is True


class TestStatus:
    def test_status_strict_not_in_sandbox(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.STRICT)
        status = enforcer.status()
        assert isinstance(status, SandboxStatus)
        assert status.enforced is True
        assert status.mode == SandboxMode.STRICT
        assert status.in_sandbox is False

    def test_status_none_mode(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.NONE)
        status = enforcer.status()
        assert status.enforced is False

    def test_status_in_sandbox(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.STRICT)
        enforcer.activate_sandbox()
        status = enforcer.status()
        assert status.in_sandbox is True


class TestValidateFileAccess:
    def test_access_within_project_root(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        enforcer.activate_sandbox()
        assert enforcer.validate_file_access(tmp_path / "some_file.py") is True

    def test_access_outside_project_root(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path)
        enforcer.activate_sandbox()
        assert enforcer.validate_file_access(Path("/etc/passwd")) is False

    def test_access_when_not_in_sandbox_strict(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.STRICT)
        assert enforcer.validate_file_access(tmp_path / "file.py") is False

    def test_access_when_none_mode(self, tmp_path):
        enforcer = SandboxEnforcer(project_root=tmp_path, mode=SandboxMode.NONE)
        assert enforcer.validate_file_access(tmp_path / "file.py") is True
