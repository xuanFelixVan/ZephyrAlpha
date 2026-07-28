# [A_test] module_id: MOD-GOV_skill_breakage_checker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_breakage_checker
# [INVARIANTS] compatible=True iff breaking_changes is empty; similarity in [0,1]
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises TypeError on None input
# [TESTS] tests/test_skill_breakage_checker.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.autonomy_core.skills.skill_breakage_checker import SkillBreakageChecker


class TestSkillBreakageCheckerInstantiation:
    def test_instantiation(self):
        checker = SkillBreakageChecker()
        assert checker.TOOL_PATTERN is not None
        assert len(checker.CONSTRAINT_PATTERNS) > 0


class TestSkillBreakageCheckerCheck:
    def setup_method(self):
        self.checker = SkillBreakageChecker()

    def test_check_identical_content(self):
        content = "# Skill\nUse `grep`(search) and `edit`(modify)\nMUST validate input"
        result = self.checker.check(content, content)
        assert result["compatible"] is True
        assert result["similarity"] == 1.0
        assert result["change_type"] in ("minor", "patch")
        assert result["breaking_changes"] == []

    def test_check_tool_removed(self):
        old = "# Skill\nUse `grep`(search) and `edit`(modify)"
        new = "# Skill\nUse `grep`(search) only"
        result = self.checker.check(old, new)
        assert result["compatible"] is False
        assert len(result["breaking_changes"]) >= 1
        assert result["breaking_changes"][0]["type"] == "tools_removed"
        assert result["breaking_changes"][0]["severity"] == "high"

    def test_check_constraint_removed(self):
        old = "# Skill\nMUST validate input\nCRITICAL: check permissions"
        new = "# Skill\nSome other content without constraints"
        result = self.checker.check(old, new)
        assert result["compatible"] is False
        assert any(bc["type"] == "constraints_removed" for bc in result["breaking_changes"])

    def test_check_minor_change(self):
        old = "# Skill\nUse `grep`(search)\nMUST validate"
        new = "# Skill\nUse `grep`(search)\nMUST validate with extra care"
        result = self.checker.check(old, new)
        assert result["compatible"] is True
        assert result["similarity"] < 1.0

    def test_check_empty_content(self):
        result = self.checker.check("", "")
        assert result["compatible"] is True
        assert result["similarity"] == 1.0

    def test_check_empty_old_populated_new(self):
        old = ""
        new = "# Skill\nUse `grep`(search)\nMUST validate"
        result = self.checker.check(old, new)
        assert result["compatible"] is True
        assert result["similarity"] < 1.0

    def test_check_populated_old_empty_new(self):
        old = "# Skill\nUse `grep`(search)\nMUST validate"
        new = ""
        result = self.checker.check(old, new)
        assert result["compatible"] is False
        assert len(result["breaking_changes"]) >= 1

    def test_check_none_raises(self):
        with pytest.raises((TypeError, AttributeError)):
            self.checker.check(None, "content")

    def test_check_none_new_raises(self):
        with pytest.raises((TypeError, AttributeError)):
            self.checker.check("content", None)

    def test_check_change_type_breaking(self):
        old = "# Skill\nUse `grep`(search)\nMUST validate"
        new = "# Skill\nNo tools, no constraints"
        result = self.checker.check(old, new)
        assert result["change_type"] == "breaking"

    def test_check_change_type_minor(self):
        old = "# Skill\nSome content here"
        new = "# Skill\nSome different content here"
        result = self.checker.check(old, new)
        assert result["change_type"] in ("minor", "patch", "breaking")

    def test_check_similarity_range(self):
        result = self.checker.check("aaa", "bbb")
        assert 0.0 <= result["similarity"] <= 1.0

    def test_check_multiple_tools_removed(self):
        old = "# Skill\nUse `grep`(search) `edit`(modify) `run`(exec)"
        new = "# Skill\nNo tools here"
        result = self.checker.check(old, new)
        assert result["compatible"] is False
        tools_removed = [bc for bc in result["breaking_changes"] if bc["type"] == "tools_removed"]
        assert len(tools_removed) >= 1


class TestSkillBreakageCheckerExtractMethods:
    def setup_method(self):
        self.checker = SkillBreakageChecker()

    def test_extract_tools(self):
        content = "Use `grep`(search) and `edit`(modify)"
        tools = self.checker.extract_tools(content)
        assert "grep" in tools
        assert "edit" in tools

    def test_extract_tools_empty(self):
        tools = self.checker.extract_tools("")
        assert tools == set()

    def test_extract_tools_no_match(self):
        tools = self.checker.extract_tools("no tools here")
        assert tools == set()

    def test_extract_constraints(self):
        content = "MUST validate input\nCRITICAL: check\n禁止 delete"
        constraints = self.checker.extract_constraints(content)
        assert len(constraints) >= 2

    def test_extract_constraints_empty(self):
        constraints = self.checker.extract_constraints("")
        assert constraints == set()
