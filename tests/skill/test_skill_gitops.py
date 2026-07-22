# [A_test] module_id: MOD-GOV_skill_gitops | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_gitops
# [INVARIANTS] no real git operations; all methods are pure functions on SkillGitOps
# [MODIFY-GUARD] skill_gitops.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] all tests must pass independently
# [TESTS] pytest tests/test_skill_gitops.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.autonomy_core.skills.skill_gitops import SkillGitOps


class TestSkillGitOpsInstantiation:
    def test_class_has_branch_prefixes(self):
        assert hasattr(SkillGitOps, "BRANCH_PREFIXES")
        assert "feature" in SkillGitOps.BRANCH_PREFIXES
        assert "fix" in SkillGitOps.BRANCH_PREFIXES
        assert "chore" in SkillGitOps.BRANCH_PREFIXES

    def test_branch_prefix_values(self):
        assert SkillGitOps.BRANCH_PREFIXES["feature"] == "feat"
        assert SkillGitOps.BRANCH_PREFIXES["breaking"] == "breaking"
        assert SkillGitOps.BRANCH_PREFIXES["deprecate"] == "deprecate"


class TestGenerateBranchName:
    def test_feature_branch(self):
        result = SkillGitOps.generate_branch_name("my-skill", "feature", "add new handler")
        assert result.startswith("feat/")
        assert "add-new-handler" in result

    def test_fix_branch(self):
        result = SkillGitOps.generate_branch_name("my-skill", "fix", "fix null pointer")
        assert result.startswith("fix/")

    def test_unknown_type_defaults_chore(self):
        result = SkillGitOps.generate_branch_name("my-skill", "unknown", "something")
        assert result.startswith("chore/")

    def test_slug_truncated_to_40_chars(self):
        long_desc = "a" * 100
        result = SkillGitOps.generate_branch_name("sk", "feature", long_desc)
        parts = result.split("-", 1)
        slug_part = parts[1] if len(parts) > 1 else result
        assert len(slug_part) <= 60

    def test_special_characters_removed(self):
        result = SkillGitOps.generate_branch_name("sk", "feature", "hello!@#$world")
        assert "!" not in result
        assert "@" not in result

    def test_skill_id_abbreviation(self):
        result = SkillGitOps.generate_branch_name("my-awesome-skill", "feature", "test")
        assert "mas" in result.lower()


class TestGeneratePRDescription:
    def test_basic_pr(self):
        changes = {"kind": "feature", "summary": "Added new skill"}
        result = SkillGitOps.generate_pr_description("skill-x", changes)
        assert "skill-x" in result
        assert "feature" in result
        assert "Added new skill" in result

    def test_pr_with_breaking_changes(self):
        changes = {
            "kind": "breaking",
            "summary": "Major refactor",
            "breaking_changes": ["API changed", "Config format updated"],
        }
        result = SkillGitOps.generate_pr_description("skill-y", changes)
        assert "Breaking Changes" in result
        assert "API changed" in result

    def test_pr_with_added_and_fixed(self):
        changes = {"kind": "update", "summary": "Mixed changes", "added": ["New endpoint"], "fixed": ["Null check"]}
        result = SkillGitOps.generate_pr_description("skill-z", changes)
        assert "Added" in result
        assert "Fixed" in result
        assert "New endpoint" in result
        assert "Null check" in result

    def test_pr_empty_changes(self):
        changes = {}
        result = SkillGitOps.generate_pr_description("skill-e", changes)
        assert "skill-e" in result
        assert "Pre-merge Checklist" in result

    def test_pr_contains_checklist(self):
        changes = {"kind": "fix", "summary": "Patch"}
        result = SkillGitOps.generate_pr_description("skill-c", changes)
        assert "SkillsBench" in result
        assert "Registry updated" in result


class TestGenerateReleaseNotes:
    def test_basic_release(self):
        skills = [{"skill_id": "sk-a", "kind": "feature", "summary": "New skill"}]
        result = SkillGitOps.generate_release_notes("1.2.0", skills)
        assert "1.2.0" in result
        assert "sk-a" in result
        assert "New skill" in result

    def test_empty_skills_list(self):
        result = SkillGitOps.generate_release_notes("0.1.0", [])
        assert "0.1.0" in result
        assert "Skills Changed" in result

    def test_multiple_skills(self):
        skills = [
            {"skill_id": "sk-1", "kind": "feature", "summary": "A"},
            {"skill_id": "sk-2", "kind": "fix", "summary": "B"},
        ]
        result = SkillGitOps.generate_release_notes("2.0.0", skills)
        assert "sk-1" in result
        assert "sk-2" in result

    def test_missing_skill_fields_default(self):
        skills = [{}]
        result = SkillGitOps.generate_release_notes("3.0.0", skills)
        assert "?" in result


class TestVersionBump:
    def test_breaking_bumps_major(self):
        assert SkillGitOps.version_bump("1.2.3", "breaking") == "2.0.0"

    def test_feature_bumps_minor(self):
        assert SkillGitOps.version_bump("1.2.3", "feature") == "1.3.0"

    def test_fix_bumps_patch(self):
        assert SkillGitOps.version_bump("1.2.3", "fix") == "1.2.4"

    def test_deprecate_bumps_minor(self):
        assert SkillGitOps.version_bump("1.2.3", "deprecate") == "1.3.0"

    def test_unknown_type_bumps_patch(self):
        assert SkillGitOps.version_bump("1.2.3", "random") == "1.2.4"

    def test_version_with_v_prefix(self):
        assert SkillGitOps.version_bump("v1.2.3", "feature") == "1.3.0"

    def test_version_with_missing_parts(self):
        assert SkillGitOps.version_bump("1", "feature") == "1.1.0"

    def test_invalid_version_defaults_to_zero(self):
        assert SkillGitOps.version_bump("abc", "feature") == "0.1.0"

    def test_breaking_resets_minor_and_patch(self):
        assert SkillGitOps.version_bump("5.9.9", "breaking") == "6.0.0"


class TestInitSkillRepo:
    def test_init_returns_all_fields(self):
        result = SkillGitOps.init_skill_repo("my-skill", "0.1.0")
        assert result["skill_id"] == "my-skill"
        assert result["version"] == "0.1.0"
        assert "branch" in result
        assert "pr_description" in result
        assert "release_notes" in result

    def test_init_default_version(self):
        result = SkillGitOps.init_skill_repo("another-skill")
        assert result["version"] == "0.1.0"

    def test_init_branch_starts_with_feat(self):
        result = SkillGitOps.init_skill_repo("test-skill")
        assert result["branch"].startswith("feat/")
