# [A_test] module_id: MOD-GOV_skill_constructor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_constructor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_constructor.py
# [TTL] task_bound

from __future__ import annotations

import textwrap
from unittest.mock import MagicMock, patch

import pytest

from zephyr.autonomy_core.skills.skill_constructor import SkillConstructor


class TestSkillConstructorInit:
    def test_instantiation_with_default_dir(self):
        sc = SkillConstructor()
        assert sc.base_dir is not None
        assert sc.skills_dir == sc.base_dir / "skills"
        assert sc.registry_path == sc.base_dir / "skill-registry.yaml"

    def test_instantiation_with_custom_dir(self, tmp_path):
        sc = SkillConstructor(base_dir=tmp_path)
        assert sc.base_dir == tmp_path
        assert sc.skills_dir == tmp_path / "skills"
        assert sc.registry_path == tmp_path / "skill-registry.yaml"

    def test_keyword_map_not_empty(self):
        assert len(SkillConstructor.KEYWORD_MAP) > 0


class TestParseBlueprint:
    def test_parse_with_frontmatter(self, tmp_path):
        bp_content = textwrap.dedent("""\
            ---
            module_id: MOD-TEST-001
            version: 1.0.0
            ---
            # Test Blueprint
            Some body text.
        """)
        bp_file = tmp_path / "test_bp.md"
        bp_file.write_text(bp_content, encoding="utf-8")
        sc = SkillConstructor(base_dir=tmp_path)
        result = sc.parse_blueprint(str(bp_file))
        assert result["frontmatter"]["module_id"] == "MOD-TEST-001"
        assert "Test Blueprint" in result["body"]

    def test_parse_without_frontmatter(self, tmp_path):
        bp_content = "# No Frontmatter\nJust body."
        bp_file = tmp_path / "no_fm.md"
        bp_file.write_text(bp_content, encoding="utf-8")
        sc = SkillConstructor(base_dir=tmp_path)
        result = sc.parse_blueprint(str(bp_file))
        assert result["frontmatter"] == {}
        assert "No Frontmatter" in result["body"]

    def test_parse_nonexistent_file_raises(self, tmp_path):
        sc = SkillConstructor(base_dir=tmp_path)
        with pytest.raises(Exception):
            sc.parse_blueprint(str(tmp_path / "nonexistent.md"))


class TestExtractSections:
    def test_extract_multiple_sections(self):
        body = "# Section One\nContent 1\n# Section Two\nContent 2"
        sc = SkillConstructor()
        sections = sc.extract_sections(body)
        assert "section one" in sections
        assert "section two" in sections

    def test_extract_no_headers(self):
        body = "Just some text\nNo headers"
        sc = SkillConstructor()
        sections = sc.extract_sections(body)
        assert "preamble" in sections

    def test_extract_empty_body(self):
        sc = SkillConstructor()
        sections = sc.extract_sections("")
        assert "preamble" in sections


class TestExtractCoreOperations:
    def test_extract_from_matching_section(self):
        sections = {"核心操作": "# 核心操作\n- op1\n- op2\n- op3"}
        sc = SkillConstructor()
        result = sc.extract_core_operations(sections, "")
        assert result != ""

    def test_extract_from_body_fallback(self):
        sections = {}
        body = "1. First step\n2. Second step\ndef my_function():"
        sc = SkillConstructor()
        result = sc.extract_core_operations(sections, body)
        assert "First step" in result or "my_function" in result

    def test_extract_nothing(self):
        sc = SkillConstructor()
        result = sc.extract_core_operations({}, "plain text only")
        assert result == ""


class TestExtractConstraints:
    def test_extract_must_constraint(self):
        body = "You MUST validate all inputs before processing."
        sc = SkillConstructor()
        result = sc.extract_constraints({}, body)
        assert "validate all inputs" in result

    def test_extract_no_constraints(self):
        body = "This is a simple description with no rules."
        sc = SkillConstructor()
        result = sc.extract_constraints({}, body)
        assert result == ""


class TestExtractCommonErrors:
    def test_extract_from_matching_section(self):
        sections = {"常见错误": "# 常见错误\n- error1\n- error2"}
        sc = SkillConstructor()
        result = sc.extract_common_errors(sections)
        assert result != ""

    def test_extract_no_matching_section(self):
        sc = SkillConstructor()
        result = sc.extract_common_errors({})
        assert result == ""


class TestInferSkillName:
    def test_infer_from_module_id(self):
        bp = {"frontmatter": {"module_id": "MOD-DATABASE-001"}, "body": ""}
        sc = SkillConstructor()
        name = sc.infer_skill_name(bp)
        assert name == "database-specialist"

    def test_infer_from_body(self):
        bp = {"frontmatter": {"module_id": "MOD-XYZ"}, "body": "This module handles security and injection prevention."}
        sc = SkillConstructor()
        name = sc.infer_skill_name(bp)
        assert name == "lsg-security"

    def test_default_to_master_blueprint(self):
        bp = {"frontmatter": {"module_id": "MOD-UNKNOWN"}, "body": "generic content"}
        sc = SkillConstructor()
        name = sc.infer_skill_name(bp)
        assert name == "master-blueprint"


class TestGenerateSkillContent:
    def test_generate_with_all_fields(self):
        sc = SkillConstructor()
        content = sc.generate_skill_content(
            "test-skill",
            "SKILL-DOM-TES-001",
            "op1\nop2",
            "constraint1",
            "error1",
        )
        assert "test-skill" in content
        assert "SKILL-DOM-TES-001" in content
        assert "op1" in content
        assert "constraint1" in content
        assert "error1" in content

    def test_generate_without_optional_fields(self):
        sc = SkillConstructor()
        content = sc.generate_skill_content(
            "minimal-skill",
            "SKILL-DOM-MIN-001",
            "",
            "",
            "",
        )
        assert "minimal-skill" in content
        assert "独特约束" not in content
        assert "常见错误模式" not in content


class TestConstruct:
    def test_construct_with_valid_blueprint(self, tmp_path):
        bp_content = textwrap.dedent("""\
            ---
            module_id: MOD-DATABASE-001
            version: 1.0.0
            ---
            # Database Module

            You MUST backup before migration.
            1. create_table
            2. run_migration
        """)
        bp_file = tmp_path / "db_bp.md"
        bp_file.write_text(bp_content, encoding="utf-8")
        sc = SkillConstructor(base_dir=tmp_path)
        with patch.object(sc, "update_registry"):
            result = sc.construct(str(bp_file))
        assert result["status"] == "constructed"
        assert result["skill_name"] == "database-specialist"
        assert result["skill_id"] is not None
        assert len(result["files"]) > 0

    def test_construct_with_nonexistent_blueprint(self, tmp_path):
        sc = SkillConstructor(base_dir=tmp_path)
        result = sc.construct(str(tmp_path / "nonexistent.md"))
        assert result["status"] == "parse_failed"
        assert result["skill_id"] is None

    def test_construct_empty_blueprint(self, tmp_path):
        bp_file = tmp_path / "empty_bp.md"
        bp_file.write_text("", encoding="utf-8")
        sc = SkillConstructor(base_dir=tmp_path)
        with patch.object(sc, "update_registry"):
            result = sc.construct(str(bp_file))
        assert result["status"] == "constructed"


class TestValidateConstruction:
    def test_validate_missing_skill(self):
        sc = SkillConstructor()
        with patch(
            "zephyr.autonomy_core.skills.skill_loader.SkillLoader",
            side_effect=KeyError("not found"),
        ):
            result = sc.validate_construction("SKILL-NONEXISTENT")
        assert result["valid"] is False
        assert "skill_not_registered" in result["issues"]

    def test_validate_file_not_found(self):
        sc = SkillConstructor()
        with patch(
            "zephyr.autonomy_core.skills.skill_loader.SkillLoader",
            side_effect=FileNotFoundError("missing"),
        ):
            result = sc.validate_construction("SKILL-MISSING-FILE")
        assert result["valid"] is False
        assert "skill_file_missing" in result["issues"]

    def test_validate_valid_skill(self):
        mock_loader = MagicMock()
        mock_loader.progressive_load.return_value = {
            "l1": {"skill_id": "SKILL-DOM-TES-001"},
            "l2": "some content",
            "token_count_l2": 100,
        }
        sc = SkillConstructor()
        with patch(
            "zephyr.autonomy_core.skills.skill_loader.SkillLoader",
            return_value=mock_loader,
        ):
            result = sc.validate_construction("SKILL-DOM-TES-001")
        assert result["valid"] is True
        assert result["issues"] == []

    def test_validate_over_budget(self):
        mock_loader = MagicMock()
        mock_loader.progressive_load.return_value = {
            "l1": {"skill_id": "SKILL-DOM-TES-002"},
            "l2": "x" * 600,
            "token_count_l2": 600,
        }
        sc = SkillConstructor()
        with patch(
            "zephyr.autonomy_core.skills.skill_loader.SkillLoader",
            return_value=mock_loader,
        ):
            result = sc.validate_construction("SKILL-DOM-TES-002")
        assert result["valid"] is False
        assert "l2_over_budget" in result["issues"]
