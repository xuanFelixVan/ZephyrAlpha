# [A_test] module_id: MOD-GOV_skill_factory | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_factory
# [INVARIANTS] SkillFactory generates domain skills from blueprints
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError on missing blueprint
# [TESTS] pytest tests/test_skill_factory.py -q
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.autonomy_core.skills.skill_factory import SkillFactory


class TestSkillFactoryInstantiation:
    def test_class_exists(self):
        assert SkillFactory is not None

    def test_can_instantiate(self):
        obj = SkillFactory()
        assert isinstance(obj, SkillFactory)

    def test_template_path_set(self):
        obj = SkillFactory()
        assert obj.template_path is not None
        assert isinstance(obj.template_path, Path)


class TestSanitizeDirName:
    def test_basic_name(self):
        sf = SkillFactory()
        assert sf.sanitize_dir_name("my-module") == "my-module"

    def test_uppercase_lowered(self):
        sf = SkillFactory()
        assert sf.sanitize_dir_name("MyModule") == "mymodule"

    def test_spaces_replaced(self):
        sf = SkillFactory()
        assert sf.sanitize_dir_name("my module name") == "my-module-name"

    def test_special_chars_removed(self):
        sf = SkillFactory()
        result = sf.sanitize_dir_name("mod@#$!")
        assert all(c.isalnum() or c in "-_" for c in result)

    def test_empty_string(self):
        sf = SkillFactory()
        result = sf.sanitize_dir_name("")
        assert isinstance(result, str)


class TestFindSection:
    def test_finds_heading(self):
        sf = SkillFactory()
        content = "# Core Operations\n- op1\n- op2\n## Next Section"
        result = sf.find_section(content, ["Core Operations"])
        assert "op1" in result

    def test_finds_by_alternate_keyword(self):
        sf = SkillFactory()
        content = "# Constraints\n- c1\n- c2\n# Other"
        result = sf.find_section(content, ["约束", "Constraints"])
        assert "c1" in result

    def test_returns_empty_on_no_match(self):
        sf = SkillFactory()
        result = sf.find_section("no relevant content", ["Missing"])
        assert result == ""

    def test_empty_content(self):
        sf = SkillFactory()
        result = sf.find_section("", ["Core Operations"])
        assert result == ""


class TestExtractModuleInfo:
    def test_basic_extraction(self):
        sf = SkillFactory()
        blueprint = "# Core Operations\n- op1\n- op2\n# Constraints\n- c1\n# Common Errors\n- e1\n"
        info = sf.extract_module_info("test-mod", blueprint)
        assert info["module_name"] == "test-mod"
        assert "op1" in info["core_operations"]
        assert "c1" in info["unique_constraints"]
        assert "e1" in info["common_errors"]

    def test_missing_sections_use_placeholder(self):
        sf = SkillFactory()
        info = sf.extract_module_info("empty-mod", "no sections here")
        assert info["core_operations"] == "待填写"
        assert info["unique_constraints"] == "待填写"
        assert info["common_errors"] == "待填写"


class TestRenderTemplate:
    def test_basic_render(self):
        sf = SkillFactory()
        template = (
            "Module: {{MODULE_NAME}}\n"
            "Ops: {{CORE_OPERATIONS}}\n"
            "Constraints: {{UNIQUE_CONSTRAINTS}}\n"
            "Errors: {{COMMON_ERRORS}}"
        )
        info = {
            "module_name": "test-mod",
            "core_operations": "op1, op2",
            "unique_constraints": "c1",
            "common_errors": "e1",
        }
        result = sf.render_template(template, info)
        assert "test-mod" in result
        assert "op1, op2" in result
        assert "c1" in result
        assert "e1" in result

    def test_no_unreplaced_placeholders(self):
        sf = SkillFactory()
        info = {
            "module_name": "mod",
            "core_operations": "ops",
            "unique_constraints": "cons",
            "common_errors": "errs",
        }
        result = sf.render_template("{{MODULE_NAME}}-{{CORE_OPERATIONS}}", info)
        assert "{{" not in result


class TestGenerateSkillId:
    def test_basic_id_format(self):
        sf = SkillFactory()
        with patch.object(sf, "_count_domain_skills", return_value=5):
            sid = sf.generate_skill_id("database-migration")
        assert sid.startswith("SKILL-DOM-")
        assert len(sid) > 10

    def test_abbreviation_from_name(self):
        sf = SkillFactory()
        with patch.object(sf, "_count_domain_skills", return_value=0):
            sid = sf.generate_skill_id("database-migration")
        assert "DM" in sid

    def test_single_word_name(self):
        sf = SkillFactory()
        with patch.object(sf, "_count_domain_skills", return_value=0):
            sid = sf.generate_skill_id("security")
        assert "S" in sid


class TestReadBlueprint:
    def test_absolute_path(self, tmp_path):
        bp = tmp_path / "blueprint.md"
        bp.write_text("# Test Blueprint", encoding="utf-8")
        sf = SkillFactory()
        result = sf.read_blueprint(str(bp))
        assert "Test Blueprint" in result

    def test_nonexistent_path_raises(self):
        sf = SkillFactory()
        with pytest.raises((FileNotFoundError, OSError)):
            sf.read_blueprint("/nonexistent/path/blueprint.md")


class TestBootstrapSequence:
    def test_yields_four_steps(self):
        sf = SkillFactory()
        with patch.object(sf, "generate_domain_skill", return_value=Path("/fake/skill.md")):
            steps = list(sf.bootstrap_sequence("test-mod", "fake/blueprint.md"))
        assert len(steps) == 4
        labels = [s[0] for s in steps]
        assert "create_blueprint" in labels
        assert "factory_generate" in labels
        assert "human_review" in labels
        assert "register" in labels
