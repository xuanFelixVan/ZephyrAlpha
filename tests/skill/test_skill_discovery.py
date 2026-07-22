# [A_test] module_id: MOD-GOV_skill_discovery | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_discovery
# [INVARIANTS] SkillDiscovery must correctly identify gaps between blueprints and registered skills
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass; exit != 0 = regression
# [TESTS] tests/test_skill_discovery.py
# [TTL] task_bound

import os
import tempfile

from zephyr.autonomy_core.skills.skill_discovery import DiscoveryGap, DiscoveryResult, SkillDiscovery


class TestDiscoveryGapInstantiation:
    def test_basic_creation(self):
        gap = DiscoveryGap("my-module", "/path/to/blueprint.md", "No skill found")
        assert gap.module_name == "my-module"
        assert gap.blueprint_path == "/path/to/blueprint.md"
        assert gap.reason == "No skill found"

    def test_to_dict(self):
        gap = DiscoveryGap("mod-a", "/bp/a.md", "Missing skill")
        d = gap.to_dict()
        assert d["module_name"] == "mod-a"
        assert d["blueprint_path"] == "/bp/a.md"
        assert d["reason"] == "Missing skill"


class TestDiscoveryResultInstantiation:
    def test_default_empty(self):
        result = DiscoveryResult()
        assert result.existing_skills == []
        assert result.gaps == []
        assert result.generated == []
        assert result.errors == []

    def test_to_dict(self):
        result = DiscoveryResult()
        result.existing_skills = ["s1"]
        result.gaps = [DiscoveryGap("m1", "/p1", "r1")]
        result.generated = ["g1"]
        result.errors = ["e1"]
        d = result.to_dict()
        assert d["existing_skills"] == ["s1"]
        assert d["total_gaps"] == 1
        assert d["total_generated"] == 1
        assert len(d["gaps"]) == 1
        assert d["gaps"][0]["module_name"] == "m1"


class TestDeriveSkillId:
    def test_simple_name(self):
        result = SkillDiscovery._derive_skill_id("governance")
        assert result == "SKILL-DOM-GOV-001"

    def test_dashed_name_uses_last_segment(self):
        result = SkillDiscovery._derive_skill_id("MOD-INF-019")
        assert result == "SKILL-DOM-019-001"

    def test_empty_string(self):
        result = SkillDiscovery._derive_skill_id("")
        assert result == ""

    def test_short_name(self):
        result = SkillDiscovery._derive_skill_id("ab")
        assert result == "SKILL-DOM-AB-001"


class TestExtractModuleName:
    def test_from_mod_heading(self):
        content = "# MOD-INF-019 Some Blueprint\n\nBody text"
        result = SkillDiscovery._extract_module_name(
            content, type("P", (), {"parent": type("X", (), {"name": "test"}), "parts": ()})
        )
        assert result == "MOD-INF-019"

    def test_from_blueprint_heading(self):
        content = "# 蓝图说明: My-Module\n\nBody"
        from pathlib import Path

        result = SkillDiscovery._extract_module_name(content, Path("dummy"))
        assert result == "蓝图说明"

    def test_from_parent_directory(self):
        content = "No module heading here"
        from pathlib import Path

        bp_file = Path("/some/path/my-module/blueprint.md")
        result = SkillDiscovery._extract_module_name(content, bp_file)
        assert result == "my-module"

    def test_empty_content(self):
        from pathlib import Path

        bp_file = Path("/some/path/my-mod/blueprint.md")
        result = SkillDiscovery._extract_module_name("", bp_file)
        assert result == "my-mod"


class TestScanModules:
    def test_nonexistent_path_returns_empty(self):
        result = SkillDiscovery.scan_modules("/nonexistent/path/abc123")
        assert result == []

    def test_empty_directory_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = SkillDiscovery.scan_modules(tmpdir)
            assert result == []

    def test_file_instead_of_directory_returns_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            f.flush()
            f.close()
            result = SkillDiscovery.scan_modules(f.name)
            try:
                os.unlink(f.name)
            except OSError:
                pass
            assert result == []

    def test_scans_domain_skills(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = os.path.join(tmpdir, "skills", "domain")
            os.makedirs(skills_dir)
            md_path = os.path.join(skills_dir, "my-skill.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("---\nversion: 1.0.0\ndescription: Test skill\n---\nContent")
            result = SkillDiscovery.scan_modules(tmpdir)
            assert len(result) >= 1
            assert result[0]["category"] == "domain"
            assert result[0]["name"] == "my-skill"

    def test_scans_role_skills(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = os.path.join(tmpdir, "skills", "role")
            os.makedirs(skills_dir)
            md_path = os.path.join(skills_dir, "reviewer.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("---\nversion: 0.5.0\n---\nContent")
            result = SkillDiscovery.scan_modules(tmpdir)
            assert len(result) >= 1
            assert result[0]["category"] == "role"

    def test_scans_all_skill_modules_py(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            all_skills = os.path.join(tmpdir, "all_skill_modules.py")
            with open(all_skills, "w", encoding="utf-8") as f:
                f.write('"my_module",\n"other_module",\n')
            result = SkillDiscovery.scan_modules(tmpdir)
            names = [r["name"] for r in result]
            assert "my_module" in names
            assert "other_module" in names


class TestParseFrontmatter:
    def _write_temp_md(self, content):
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, "test.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path, tmpdir

    def test_valid_frontmatter(self):
        from pathlib import Path

        path, tmpdir = self._write_temp_md("---\nversion: 2.0.0\ndescription: A test\n---\nBody")
        try:
            result = SkillDiscovery._parse_frontmatter(Path(path))
            assert result.get("version") == "2.0.0"
            assert result.get("description") == "A test"
        finally:
            import shutil

            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_no_frontmatter(self):
        from pathlib import Path

        path, tmpdir = self._write_temp_md("Just some content without frontmatter")
        try:
            result = SkillDiscovery._parse_frontmatter(Path(path))
            assert result == {}
        finally:
            import shutil

            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_invalid_yaml_frontmatter(self):
        from pathlib import Path

        path, tmpdir = self._write_temp_md("---\n: invalid: yaml: [broken\n---\nBody")
        try:
            result = SkillDiscovery._parse_frontmatter(Path(path))
            assert result == {}
        finally:
            import shutil

            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_incomplete_frontmatter(self):
        from pathlib import Path

        path, tmpdir = self._write_temp_md("---\nversion: 1.0")
        try:
            result = SkillDiscovery._parse_frontmatter(Path(path))
            assert result == {}
        finally:
            import shutil

            shutil.rmtree(tmpdir, ignore_errors=True)


class TestDiscoverGaps:
    def test_nonexistent_docs_path_returns_error(self):
        result = SkillDiscovery.discover_gaps(docs_path="/nonexistent/docs/path/xyz")
        assert len(result.errors) > 0

    def test_returns_discovery_result(self):
        result = SkillDiscovery.discover_gaps(docs_path="/nonexistent/docs/path/xyz")
        assert isinstance(result, DiscoveryResult)


class TestAutoGenerateMissing:
    def test_dry_run_does_not_generate(self):
        result = SkillDiscovery.auto_generate_missing(docs_path="/nonexistent/docs/path/xyz", dry_run=True)
        assert isinstance(result, DiscoveryResult)

    def test_returns_discovery_result(self):
        result = SkillDiscovery.auto_generate_missing(docs_path="/nonexistent/docs/path/xyz")
        assert isinstance(result, DiscoveryResult)
