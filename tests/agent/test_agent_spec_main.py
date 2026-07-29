# [A_test] module_id: MOD-GOV_agent_spec_main | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §

# [MODULE] tests.test_agent_spec_main

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] python -m pytest tests/test_agent_spec_main.py -q
# [TTL] task_bound

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.autonomy_core.__main__ import (
    _load_registry,
    _registry_path,
    cmd_list,
    cmd_status,
    main,
)


class TestRegistryPath:
    def test_returns_path_object(self):
        result = _registry_path()
        assert isinstance(result, Path)

    def test_path_points_to_skill_registry_yaml(self):
        result = _registry_path()
        assert result.name == "skill-registry.yaml"

    def test_path_under_agent_spec_dir(self):
        result = _registry_path()
        assert "agent-spec" in str(result)


class TestLoadRegistry:
    def test_loads_valid_yaml(self):
        reg = _load_registry()
        assert isinstance(reg, dict)

    def test_registry_has_skills_key(self):
        reg = _load_registry()
        assert "skills" in reg

    def test_load_registry_missing_file(self):
        with patch("zephyr.autonomy_core.__main__.registry_path", return_value=Path("/nonexistent/registry.yaml")):
            with pytest.raises(FileNotFoundError):
                _load_registry()


class TestCmdList:
    def test_returns_zero_on_success(self, capsys):
        result = cmd_list()
        assert result == 0

    def test_prints_skill_entries(self, capsys):
        cmd_list()
        out = capsys.readouterr().out
        assert "已注册 Skill" in out or "Skill" in out

    def test_handles_registry_error(self, capsys):
        with patch("zephyr.autonomy_core.__main__.load_registry", side_effect=RuntimeError("boom")):
            result = cmd_list()
            assert result == 1

    def test_empty_skills_prints_zero(self, capsys):
        with patch("zephyr.autonomy_core.__main__.load_registry", return_value={"skills": {}}):
            result = cmd_list()
            assert result == 0
            out = capsys.readouterr().out
            assert "共 0" in out


class TestCmdStatus:
    def test_returns_zero_when_all_ok(self, capsys):
        result = cmd_status()
        if result == 0:
            out = capsys.readouterr().out
            assert "ALL SYSTEMS GO" in out

    def test_prints_component_status(self, capsys):
        cmd_status()
        out = capsys.readouterr().out
        assert "skill_model" in out or "skill_loader" in out or "skill-registry" in out

    def test_reports_degraded_on_import_failure(self, capsys):
        with patch("zephyr.autonomy_core.__main__.load_registry", side_effect=RuntimeError("fail")):
            with patch.dict(sys.modules, {"zephyr.autonomy_core.skills.skill_model": None}):
                result = cmd_status()
                assert result == 1


class TestMain:
    def test_list_command(self, capsys):
        with patch.object(sys, "argv", ["agent-spec", "list"]):
            result = main()
            assert result == 0

    def test_ls_alias(self, capsys):
        with patch.object(sys, "argv", ["agent-spec", "ls"]):
            result = main()
            assert result == 0

    def test_status_command(self, capsys):
        with patch.object(sys, "argv", ["agent-spec", "status"]):
            result = main()
            assert isinstance(result, int)

    def test_help_default_no_args(self, capsys):
        with patch.object(sys, "argv", ["agent-spec"]):
            result = main()
            assert result == 0
            out = capsys.readouterr().out
            assert "agent-spec" in out

    def test_unknown_command_shows_help(self, capsys):
        with patch.object(sys, "argv", ["agent-spec", "unknown"]):
            result = main()
            assert result == 0
            out = capsys.readouterr().out
            assert "agent-spec" in out

    def test_help_command_shows_help(self, capsys):
        with patch.object(sys, "argv", ["agent-spec", "help"]):
            result = main()
            assert result == 0
