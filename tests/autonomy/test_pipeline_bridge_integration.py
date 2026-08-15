# [A_test] module_id: MOD-GOV_pipeline_bridge_integration | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-211 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_pipeline_bridge_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""集成测试: PipelineSkillBridge — Agent Spec 到 Pipeline 双向桥接.

Covers:
  B1 - inject_for_task 阶段路由
  B2 - inject_for_task 关键词路由
  B3 - SkillContextInjector 单技能注入
  B4 - SkillInjectionResult 序列化
  B5 - fallback 路径
  B6 - SkillContextInjector 错误恢复
"""

from __future__ import annotations

import pytest

from zephyr.autonomy_core.integration.pipeline_bridge import (
    PipelineSkillBridge,
    SkillContextInjector,
    SkillInjectionResult,
)
from zephyr.autonomy_core.skills.skill_loader import SkillLoader


class TestPipelineSkillBridge:
    """B1-B2: PipelineSkillBridge 任务注入测试."""

    @pytest.mark.xfail(reason="#ARCH-096：skill 内容库整体缺失——skill-registry.yaml 仅 2 条 domain 条目且 path 指向的 SKILL.md 文件全部不存在，role 类清空；测试锚定 ID（SKILL-DOM-DBS-001/SKILL-ROL-*）均不在册")
    def test_inject_construction_stage(self):
        """construction 阶段 → implementer role."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="修改数据库模型，添加新的 migration",
            stage="construction",
        )
        assert isinstance(result, SkillInjectionResult)
        assert result.loaded is True
        if result.role_skill_id:
            assert "IMP" in result.role_skill_id

    def test_inject_idea_stage(self):
        """idea 阶段 → architect role."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="设计新的MCP服务器接口",
            stage="idea",
        )
        assert isinstance(result, SkillInjectionResult)

    def test_inject_audit_stage(self):
        """audit 阶段 → governor role + drift-detector."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="审计系统合规状态",
            stage="audit",
        )
        assert isinstance(result, SkillInjectionResult)

    @pytest.mark.xfail(reason="#ARCH-096：skill 内容库整体缺失（SKILL.md 文件不存在）——loaded=True 依赖内容库恢复")
    def test_inject_with_database_keyword(self):
        """database 关键词 → database-specialist domain."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="Add a new SQL migration for the database",
            stage="construction",
        )
        assert result.loaded is True
        if result.domain_skill_id:
            assert "DBS" in result.domain_skill_id or "database" in str(result.l2_domain_body).lower()

    def test_inject_with_mcp_keyword(self):
        """mcp 关键词 → mcp-specialist."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="Implement a new MCP server tool",
            stage="construction",
        )
        assert isinstance(result, SkillInjectionResult)

    def test_inject_without_stage(self):
        """无 stage → 使用 task 关键词路由."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="audit all governance rules",
        )
        assert isinstance(result, SkillInjectionResult)

    def test_inject_has_constitution(self):
        """注入结果应包含 L0 constitution."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="Fix database migration bug",
            stage="construction",
        )
        if result.loaded:
            l0 = result.l0_constitution
            assert "constitution_path" in l0 or "content" in l0
        else:
            l0 = result.l0_constitution
            assert isinstance(l0, dict)


class TestSkillContextInjector:
    """B3 + B6: SkillContextInjector 测试."""

    @pytest.mark.xfail(reason="#ARCH-096：测试锚定 SKILL-DOM-DBS-001/SKILL-ROL-IMP-001 不在现注册表——内容库整体缺失待裁定")
    def test_inject_valid_pair(self):
        injector = SkillContextInjector()
        result = injector.inject("SKILL-DOM-DBS-001", "SKILL-ROL-IMP-001")
        assert isinstance(result, SkillInjectionResult)
        assert result.loaded is True
        assert result.domain_skill_id == "SKILL-DOM-DBS-001"
        assert result.role_skill_id == "SKILL-ROL-IMP-001"
        assert result.l0_constitution is not None

    @pytest.mark.xfail(reason="#ARCH-096：测试锚定 SKILL-ROL-ARC-001 不在现注册表（role 类清空）——内容库整体缺失待裁定")
    def test_inject_single_skill(self):
        injector = SkillContextInjector()
        result = injector.inject_single("SKILL-ROL-ARC-001")
        assert isinstance(result, SkillInjectionResult)
        assert result.loaded is True
        assert result.role_skill_id is None

    def test_inject_invalid_skill_returns_not_loaded(self):
        injector = SkillContextInjector()
        result = injector.inject("nonexistent-domain", "SKILL-ROL-IMP-001")
        assert result.loaded is False

    def test_inject_single_invalid_returns_not_loaded(self):
        injector = SkillContextInjector()
        result = injector.inject_single("nonexistent-skill")
        assert result.loaded is False

    def test_inject_with_l3(self):
        injector = SkillContextInjector()
        result = injector.inject("SKILL-DOM-DBS-001", "SKILL-ROL-IMP-001", load_l3=True)
        assert isinstance(result, SkillInjectionResult)


class TestSkillInjectionResult:
    """B4: SkillInjectionResult 序列化测试."""

    def test_loaded_result_to_context_string(self):
        result = SkillInjectionResult(
            skill_id="test+arc",
            domain_skill_id="SKILL-DOM-DBS-001",
            role_skill_id="SKILL-ROL-ARC-001",
            l0_constitution={},
            l2_domain_body="Database operations guide",
            l2_role_body="Architect design patterns",
            loaded=True,
        )
        ctx = result.to_context_string()
        assert "Database operations guide" in ctx
        assert "Architect design patterns" in ctx

    def test_not_loaded_returns_empty(self):
        result = SkillInjectionResult(
            skill_id="fallback",
            domain_skill_id=None,
            role_skill_id=None,
            l0_constitution={},
            loaded=False,
        )
        assert result.to_context_string() == ""

    def test_injection_context_set(self):
        result = SkillInjectionResult(
            skill_id="test",
            domain_skill_id="SD1",
            role_skill_id="SR1",
            l0_constitution={},
            l2_domain_body="body",
            l2_role_body="role body",
            injection_context="full context",
            loaded=True,
        )
        assert result.injection_context == "full context"


class TestPipelineSkillBridgeFallback:
    """B5: fallback 路径."""

    def test_empty_task_description(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(task_description="", stage="construction")
        assert isinstance(result, SkillInjectionResult)
        assert result.loaded is False
        assert result.skill_id == "fallback"

    def test_unknown_stage_name(self):
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(task_description="do something", stage="unknown_stage_xyz")
        assert isinstance(result, SkillInjectionResult)


class TestIntegrationBridgeEndToEnd:
    """全链路: SkillLoader → TriggerRouter → PipelineSkillBridge."""

    @pytest.mark.xfail(reason="#ARCH-096：health_check 已退役+total_skills 2<3+loaded 依赖缺失内容库——整链待内容库恢复后跟进")
    def test_full_chain_loads_and_routes(self):
        loader = SkillLoader()
        bridge = PipelineSkillBridge()

        assert loader.health_check()["registry"]["total_skills"] >= 3

        result = bridge.inject_for_task(
            task_description="Add new SQL migration for user table",
            stage="construction",
        )

        assert isinstance(result, SkillInjectionResult)
        assert result.loaded is True
        assert result.l2_domain_body or result.l2_role_body

        ctx = result.injection_context if result.injection_context else result.to_context_string()
        if ctx:
            assert len(ctx) > 0
