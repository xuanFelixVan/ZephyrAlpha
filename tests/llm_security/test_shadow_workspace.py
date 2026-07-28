# [A_test] module_id: MOD-GOV_shadow_workspace | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_shadow_workspace
# [INVARIANTS] 预演失败MUST阻止应用;沙箱目录MUST在验证后清理
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml shadow_workspace段
# [CONSUMERS] CI/CD;pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_shadow_workspace.py
# [TTL] task_bound

from __future__ import annotations

import tempfile
from pathlib import Path

from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    ShadowResult,
)
from zephyr.infrastructure.auto_fix_engine.shadow_workspace import ShadowWorkspace


class TestShadowWorkspaceInstantiation:
    def test_default_config(self):
        ws = ShadowWorkspace()
        assert ws.run_pytest is True
        assert ws.run_mypy is True
        assert ws.run_ruff is True
        assert ws.pytest_timeout == 120

    def test_custom_config(self):
        cfg = {
            "base_dir": "/tmp/custom_shadow",
            "run_pytest": False,
            "run_mypy": False,
            "run_ruff": False,
            "pytest_timeout": 60,
        }
        ws = ShadowWorkspace(config=cfg)
        assert ws.base_dir == "/tmp/custom_shadow"
        assert ws.run_pytest is False
        assert ws.run_mypy is False
        assert ws.run_ruff is False
        assert ws.pytest_timeout == 60

    def test_none_config_uses_defaults(self):
        ws = ShadowWorkspace(config=None)
        assert ws.run_pytest is True


class TestShadowWorkspacePreflight:
    def test_preflight_returns_not_safe_for_missing_target(self):
        ws = ShadowWorkspace(config={"run_pytest": False, "run_mypy": False, "run_ruff": False})
        action = FixAction(
            action_type="test",
            target="/nonexistent/file.py",
            after="print('hello')\n",
        )
        result = ws.preflight(action)
        assert result.safe_to_apply is False
        assert "Target not found" in result.error

    def test_preflight_cleans_up_shadow_dir(self):
        ws = ShadowWorkspace(config={"run_pytest": False, "run_mypy": False, "run_ruff": False})
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            target_file.write_text("print('hello')\n", encoding="utf-8")
            action = FixAction(
                action_type="test",
                target=str(target_file),
                after="print('fixed')\n",
            )
            result = ws.preflight(action, project_root=tmpdir)
            shadow_dir = result.shadow_dir
            assert not Path(shadow_dir).exists() or not list(Path(shadow_dir).iterdir())

    def test_preflight_with_all_checks_disabled(self):
        ws = ShadowWorkspace(config={"run_pytest": False, "run_mypy": False, "run_ruff": False})
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            target_file.write_text("print('hello')\n", encoding="utf-8")
            action = FixAction(
                action_type="test",
                target=str(target_file),
                after="print('fixed')\n",
            )
            result = ws.preflight(action, project_root=tmpdir)
            assert result.safe_to_apply is True

    def test_preflight_handles_exception_gracefully(self):
        ws = ShadowWorkspace(config={"run_pytest": False, "run_mypy": False, "run_ruff": False})
        action = FixAction(
            action_type="test",
            target="/nonexistent/file.py",
            after="content",
        )
        result = ws.preflight(action)
        assert isinstance(result, ShadowResult)
        assert result.safe_to_apply is False

    def test_preflight_with_non_py_file_skips_checks(self):
        ws = ShadowWorkspace()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.yaml"
            target_file.write_text("key: value\n", encoding="utf-8")
            action = FixAction(
                action_type="test",
                target=str(target_file),
                after="key: fixed\n",
            )
            result = ws.preflight(action, project_root=tmpdir)
            assert result.test_result is None
            assert result.type_result is None
            assert result.lint_result is None


class TestShadowWorkspaceRunTest:
    def test_run_test_handles_timeout(self):
        ws = ShadowWorkspace(config={"pytest_timeout": 1})
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ws.run_test(tmpdir)
            assert isinstance(result, dict)
            assert "passed" in result

    def test_run_test_returns_dict(self):
        ws = ShadowWorkspace()
        result = ws.run_test("/nonexistent/dir")
        assert isinstance(result, dict)
        assert "passed" in result


class TestShadowWorkspaceRunTypeCheck:
    def test_run_type_check_returns_dict(self):
        ws = ShadowWorkspace()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text("x: int = 1\n", encoding="utf-8")
            result = ws.run_type_check(str(py_file))
            assert isinstance(result, dict)
            assert "passed" in result


class TestShadowWorkspaceRunLint:
    def test_run_lint_returns_dict(self):
        ws = ShadowWorkspace()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text("x = 1\n", encoding="utf-8")
            result = ws.run_lint(str(py_file))
            assert isinstance(result, dict)
            assert "passed" in result
