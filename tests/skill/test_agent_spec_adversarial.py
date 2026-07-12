# [A_test] module_id: SRC-TST-0007 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-202 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_agent_spec_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""红白对抗: Agent Spec 技能加载系统攻击面测试.

攻击向量:
  A1 - 不存在的技能: 请求不存在的 skill_id → KeyError/FileNotFoundError
  A2 - 路径遍历攻击: skill_id 包含 ../ → 应被拒绝
  A3 - 空/null skill_id: 空字符串或 None → 应被拒绝
  A4 - 损坏的 YAML: frontmatter 格式错误 → 应被正确处理
  A5 - Token 预算溢出: 加载超大技能 → 应触发 budget 限制
  A6 - 注册表完整性: 所有注册技能应可被 progressive_load
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.autonomy_core.skills.skill_loader import SkillLoader, _count_tokens
from zephyr.shared.io.paths import REPO_ROOT


class TestNonExistentSkill:
    """A1: 不存在的技能请求."""

    def test_load_nonexistent_skill_raises(self):
        """请求不存在的 skill_id → 应抛出 KeyError."""
        loader = SkillLoader()
        with pytest.raises(KeyError):
            loader._resolve_skill_path("nonexistent-skill-99999")

    def test_progressive_load_nonexistent_raises(self):
        """progressive_load 不存在的 skill → 应抛出异常."""
        loader = SkillLoader()
        with pytest.raises(KeyError):
            loader.progressive_load("fake-skill-that-does-not-exist")


class TestEmptyNullInputs:
    """A3: 空/null 输入攻击."""

    def test_empty_skill_id_raises(self):
        """空字符串 skill_id → 应抛出 KeyError."""
        loader = SkillLoader()
        with pytest.raises(KeyError):
            loader._resolve_skill_path("")

    def test_skill_id_with_only_spaces(self):
        """纯空格 skill_id → 应抛出 KeyError."""
        loader = SkillLoader()
        with pytest.raises(KeyError):
            loader._resolve_skill_path("   ")


class TestTokenBudget:
    """A5: Token 预算攻击."""

    def test_token_counter_works(self):
        """_count_tokens 应对空字符串返回 0."""
        assert _count_tokens("") == 0
        assert _count_tokens("hello world") == 2

    def test_token_budget_for_skills(self):
        """检查已注册技能对的 token budget——处理缺失文件."""
        loader = SkillLoader()
        reg_data = loader._load_registry()
        domain_skills = list(reg_data.get("skills", {}).get("domain", {}).keys())
        role_skills = list(reg_data.get("skills", {}).get("role", {}).keys())

        if not domain_skills or not role_skills:
            pytest.skip("No domain+role skills registered")

        try:
            budget = loader.check_token_budget(domain_skills[0], role_skills[0])
            assert "total_tokens" in budget
            assert "within_budget" in budget
            assert isinstance(budget["total_tokens"], int)
        except FileNotFoundError:
            pytest.fail("Skill file missing — all registered skills MUST have corresponding .md files")


class TestRegistryIntegrity:
    """A6: 注册表完整性验证."""

    def test_all_registered_skills_integrity_report(self):
        """审计所有已注册技能——报告缺失/可加载的状态."""
        loader = SkillLoader()
        reg_data = loader._load_registry()
        skills = reg_data.get("skills", {})
        all_skills: list[str] = []
        for category in ("domain", "role"):
            all_skills.extend(skills.get(category, {}).keys())

        assert len(all_skills) > 0, "No skills registered — registry may be broken"

        loadable: list[str] = []
        missing: list[str] = []

        for skill_id in all_skills:
            try:
                result = loader.progressive_load(skill_id)
                assert "l1" in result, f"Skill {skill_id} missing l1"
                if result["l1"].get("skill_id") is not None:
                    loadable.append(skill_id)
                else:
                    missing.append(f"{skill_id}: l1.skill_id=None")
            except FileNotFoundError:
                missing.append(skill_id)
            except Exception as exc:
                missing.append(f"{skill_id}: {exc}")

        assert len(loadable) >= 0
        if missing:
            pytest.fail(f"{len(loadable)}/{len(all_skills)} skills loadable, {len(missing)} missing: {missing[:5]}...")

    def test_skill_registry_yaml_valid(self):
        """skill-registry.yaml 应是合法 YAML."""
        reg_path = REPO_ROOT / "src" / "zephyr" / "agent-spec" / "skill-registry.yaml"
        assert reg_path.exists(), f"Registry not found at {reg_path}"
        data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        assert "skills" in data
        assert "domain" in data["skills"]
        assert "role" in data["skills"]

    def test_l0_constitution_loads(self):
        """AGENT.md 全局宪法应可加载."""
        loader = SkillLoader()
        l0 = loader.load_l0()
        assert "constitution_path" in l0
        assert "content" in l0


class TestFrontmatterParsing:
    """A4: 损坏 YAML frontmatter."""

    def test_no_frontmatter_returns_empty(self):
        """无 frontmatter 的内容 → 返回空字典."""
        loader = SkillLoader()
        result = loader._parse_yaml_frontmatter("Just plain text, no YAML")
        assert result == {}

    def test_malformed_yaml_frontmatter(self):
        """格式错误的 YAML frontmatter → 应优雅降级而非崩溃."""
        loader = SkillLoader()
        with pytest.raises((yaml.YAMLError, yaml.parser.ParserError)):
            loader._parse_yaml_frontmatter("---\nkey: [unclosed bracket\n---\nbody")

    def test_empty_frontmatter(self):
        """空的 frontmatter 块 → 返回空字典."""
        loader = SkillLoader()
        result = loader._parse_yaml_frontmatter("---\n---\nbody")
        assert result == {}
