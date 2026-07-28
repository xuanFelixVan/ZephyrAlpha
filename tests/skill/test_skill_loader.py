# [A_test] module_id: MOD-GOV_skill_loader | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_loader
# [INVARIANTS] SkillLoader must use registry_path; no path traversal allowed
# [MODIFY-GUARD] changes require review of skill_loader.py API
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises KeyError on invalid skill_id; raises ValueError on path traversal
# [TESTS] pytest tests/test_skill_loader.py -q
# [TTL] task_bound

from unittest.mock import patch

import pytest
import yaml

from zephyr.autonomy_core.skills.skill_loader import SkillLoader, _count_tokens, _tokenize


@pytest.fixture
def tmp_registry_dir(tmp_path):
    skills_dir = tmp_path / "skills" / "domain"
    skills_dir.mkdir(parents=True)
    skill_file = skills_dir / "test-skill.md"
    skill_file.write_text(
        "---\n"
        "skill_id: SKILL-DOM-TS-001\n"
        "name: Test Skill\n"
        "description: A test skill\n"
        "allowed_tools:\n"
        "  - read_file\n"
        "model_hint: deepseek-v3\n"
        "freshness_score: 95.0\n"
        "last_validated: 2026-01-01\n"
        "---\n"
        "## CRITICAL Rules\n"
        "Always check before write.\n"
        "## Other Section\n"
        "Some body text here.\n",
        encoding="utf-8",
    )
    registry = {
        "skills": {
            "domain": {
                "SKILL-DOM-TS-001": {
                    "path": "test-skill.md",
                    "references": [{"name": "coding_conventions", "path": "coding-conventions.md"}],
                }
            },
            "role": {},
        }
    }
    reg_file = tmp_path / "skill-registry.yaml"
    reg_file.write_text(yaml.dump(registry, allow_unicode=True), encoding="utf-8")
    refs_dir = tmp_path / "references"
    refs_dir.mkdir(parents=True)
    ref_file = refs_dir / "coding-conventions.md"
    ref_file.write_text("# Coding Conventions\nUse UTF-8.\n", encoding="utf-8")
    factory_dir = tmp_path / "skills" / "factory"
    factory_dir.mkdir(parents=True)
    agent_md = factory_dir / "AGENT.md"
    agent_md.write_text("# Agent Constitution\nBe helpful.\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def loader(tmp_registry_dir):
    sl = SkillLoader(registry_path=tmp_registry_dir / "skill-registry.yaml")
    sl.l0_cache = None
    return sl


@pytest.fixture
def patched_loader(tmp_registry_dir, loader):
    with patch("zephyr.autonomy_core.skills.skill_loader._BASE_DIR", tmp_registry_dir):
        yield loader


class TestTokenizeAndCount:
    def test_tokenize_simple(self):
        result = _tokenize("hello world")
        assert "hello" in result
        assert "world" in result

    def test_tokenize_empty(self):
        assert _tokenize("") == []

    def test_count_tokens_returns_int(self):
        assert isinstance(_count_tokens("abc def"), int)

    def test_count_tokens_empty(self):
        assert _count_tokens("") == 0


class TestSkillLoaderInstantiation:
    def test_default_registry_path(self):
        sl = SkillLoader()
        assert sl.registry_path is not None
        assert sl.l0_cache is None

    def test_custom_registry_path(self, tmp_path):
        custom = tmp_path / "custom.yaml"
        custom.write_text("skills: {}", encoding="utf-8")
        sl = SkillLoader(registry_path=custom)
        assert sl.registry_path == custom

    def test_none_registry_path_uses_default(self):
        sl = SkillLoader(registry_path=None)
        assert sl.registry_path is not None


class TestParseYamlFrontmatter:
    def test_valid_frontmatter(self, loader):
        content = "---\nskill_id: X\nname: Y\n---\nBody"
        fm = loader._parse_yaml_frontmatter(content)
        assert fm.get("skill_id") == "X"
        assert fm.get("name") == "Y"

    def test_no_frontmatter(self, loader):
        content = "Just plain text"
        fm = loader._parse_yaml_frontmatter(content)
        assert fm == {}

    def test_empty_frontmatter(self, loader):
        content = "---\n---\nBody"
        fm = loader._parse_yaml_frontmatter(content)
        assert fm == {}


class TestExtractBody:
    def test_with_frontmatter(self, loader):
        content = "---\nskill_id: X\n---\nHello body"
        assert loader._extract_body(content) == "Hello body"

    def test_without_frontmatter(self, loader):
        content = "Just body text"
        assert loader._extract_body(content) == "Just body text"

    def test_empty_body_after_frontmatter(self, loader):
        content = "---\nskill_id: X\n---\n"
        assert loader._extract_body(content) == ""


class TestResolveSkillPath:
    def test_valid_skill(self, patched_loader):
        path = patched_loader._resolve_skill_path("SKILL-DOM-TS-001")
        assert path.exists()

    def test_invalid_skill_raises_keyerror(self, patched_loader):
        with pytest.raises(KeyError, match="not found"):
            patched_loader._resolve_skill_path("NONEXISTENT")

    def test_empty_skill_id_raises_keyerror(self, patched_loader):
        with pytest.raises(KeyError, match="Invalid skill_id"):
            patched_loader._resolve_skill_path("")

    def test_path_traversal_raises_valueerror(self, patched_loader):
        with pytest.raises(ValueError, match="Path traversal"):
            patched_loader._resolve_skill_path("../etc/passwd")

    def test_whitespace_skill_id_raises_keyerror(self, patched_loader):
        with pytest.raises(KeyError, match="Invalid skill_id"):
            patched_loader._resolve_skill_path("  skill  ")


class TestLoadL0:
    def test_load_l0_returns_dict(self, patched_loader):
        result = patched_loader.load_l0()
        assert "constitution_path" in result
        assert "content" in result

    def test_load_l0_caches(self, patched_loader):
        r1 = patched_loader.load_l0()
        r2 = patched_loader.load_l0()
        assert r1 is r2

    def test_load_l0_reads_constitution(self, patched_loader):
        result = patched_loader.load_l0()
        assert "Be helpful" in result["content"]

    def test_load_l0_missing_constitution(self, tmp_path):
        reg = tmp_path / "skill-registry.yaml"
        reg.write_text("skills: {domain: {}, role: {}}", encoding="utf-8")
        sl = SkillLoader(registry_path=reg)
        with patch("zephyr.autonomy_core.skills.skill_loader._BASE_DIR", tmp_path):
            result = sl.load_l0()
            assert result["content"] == ""


class TestProgressiveLoad:
    def test_progressive_load_keys(self, patched_loader):
        result = patched_loader.progressive_load("SKILL-DOM-TS-001")
        assert "l1" in result
        assert "l2" in result
        assert "l3_available" in result
        assert "token_count_l2" in result

    def test_progressive_load_l1_fields(self, patched_loader):
        result = patched_loader.progressive_load("SKILL-DOM-TS-001")
        l1 = result["l1"]
        assert l1["skill_id"] == "SKILL-DOM-TS-001"
        assert l1["name"] == "Test Skill"

    def test_progressive_load_l2_body(self, patched_loader):
        result = patched_loader.progressive_load("SKILL-DOM-TS-001")
        assert isinstance(result["l2"], str)
        assert len(result["l2"]) > 0

    def test_progressive_load_nonexistent_raises(self, patched_loader):
        with pytest.raises(KeyError):
            patched_loader.progressive_load("NONEXISTENT")


class TestProgressiveLoadFull:
    def test_full_load_includes_l3(self, patched_loader):
        result = patched_loader.progressive_load_full("SKILL-DOM-TS-001")
        assert "l3_contents" in result
        assert "coding_conventions" in result["l3_contents"]

    def test_full_load_missing_ref_gives_none(self, tmp_path):
        skills_dir = tmp_path / "skills" / "domain"
        skills_dir.mkdir(parents=True)
        skill_file = skills_dir / "s.md"
        skill_file.write_text("---\nskill_id: SKILL-DOM-XX-001\n---\nBody", encoding="utf-8")
        registry = {
            "skills": {
                "domain": {
                    "SKILL-DOM-XX-001": {
                        "path": "s.md",
                        "references": [{"name": "nonexistent_ref", "path": "nope.md"}],
                    }
                },
                "role": {},
            }
        }
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text(yaml.dump(registry, allow_unicode=True), encoding="utf-8")
        sl = SkillLoader(registry_path=reg_file)
        with patch("zephyr.autonomy_core.skills.skill_loader._BASE_DIR", tmp_path):
            result = sl.progressive_load_full("SKILL-DOM-XX-001")
            assert result["l3_contents"]["nonexistent_ref"] is None


class TestLoadL3Reference:
    def test_existing_reference(self, patched_loader):
        content = patched_loader.load_l3_reference("SKILL-DOM-TS-001", "coding_conventions")
        assert "UTF-8" in content

    def test_missing_reference_raises(self, patched_loader):
        with pytest.raises(FileNotFoundError, match="not found"):
            patched_loader.load_l3_reference("SKILL-DOM-TS-001", "no_such_ref")


class TestCheckTokenBudget:
    def test_within_budget(self, patched_loader):
        result = patched_loader.check_token_budget("SKILL-DOM-TS-001", "SKILL-DOM-TS-001")
        assert "domain_tokens" in result
        assert "role_tokens" in result
        assert "total_tokens" in result
        assert "within_budget" in result
        assert "budget_limit" in result
        assert result["budget_limit"] == 800

    def test_nonexistent_skill_raises(self, patched_loader):
        with pytest.raises(KeyError):
            patched_loader.check_token_budget("NONEXISTENT", "SKILL-DOM-TS-001")


class TestCompressToCriticalRules:
    def test_extracts_critical_section(self, loader):
        body = "## CRITICAL Rules\nDo this.\n## Other\nSkip.\n"
        result = loader._compress_to_critical_rules(body)
        assert "Do this." in result
        assert "Skip." not in result

    def test_no_critical_takes_first_20_lines(self, loader):
        lines = [f"Line {i}" for i in range(30)]
        body = "\n".join(lines)
        result = loader._compress_to_critical_rules(body)
        assert "Line 0" in result

    def test_empty_body(self, loader):
        result = loader._compress_to_critical_rules("")
        assert result == ""
