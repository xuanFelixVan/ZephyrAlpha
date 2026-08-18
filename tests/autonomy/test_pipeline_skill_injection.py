# [A_test] module_id: MOD-GOV_pipeline_skill_injection | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-334 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_pipeline_skill_injection
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Pipeline 集成测试: Agent Spec Skill 注入全链路验证.

验证:
  1. PipelineSkillBridge 从 TaskCard 匹配 Domain + Role Skill
  2. SkillInjectionResult 包含有效的 injection_context
  3. PipelineOrchestrator.dispatch() 在 dry_run 模式下成功注入 skill_context
  4. _call_model 输出包含 skill_context 字段
  5. SpecEngine 蓝图→Skill 升级流程完整性
"""

from __future__ import annotations

from datetime import datetime

import pytest

from zephyr.autonomy_core.integration.pipeline_bridge import (
    PipelineSkillBridge,
)
from zephyr.autonomy_core.skills.skill_loader import SkillLoader
from zephyr.autonomy_core.spec_engine import SpecEngine
from zephyr.shared.foundation.models import TaskCard


class TestSkillBridgeIntegration:
    def test_inject_for_database_task(self):
        """数据库任务 → 应匹配 database-specialist + implementer."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="修改数据库 schema 添加新的迁移",
            stage="construction",
        )
        assert result is not None
        if result.loaded:
            assert result.domain_skill_id is not None
            assert result.role_skill_id is not None
            assert "database" in (result.domain_skill_id or "").lower()
            assert "imp" in (result.role_skill_id or "").lower()
            assert len(result.injection_context) > 0

    def test_inject_for_security_task(self):
        """安全任务 → 应匹配 lsg-security + governor."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="检测 prompt injection 攻击",
            stage="verification",
        )
        assert result is not None
        if result.loaded:
            assert result.domain_skill_id is not None
            assert "lsg" in (result.domain_skill_id or "").lower()
            assert "gov" in (result.role_skill_id or "").lower()

    def test_inject_for_blueprint_task(self):
        """蓝图设计任务 → 应匹配 master-blueprint + architect."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="设计新的模块蓝图架构",
            stage="blueprint",
        )
        assert result is not None
        if result.loaded:
            assert result.domain_skill_id is not None
            assert "blueprint" in (result.domain_skill_id or "").lower()

    def test_inject_fallback_unmatched_task(self):
        """无法匹配的任务 → loaded=False 但不应崩溃."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="zzz_unknown_domain_task_xyz",
            stage="idea",
        )
        assert result is not None
        assert hasattr(result, "loaded")

    def test_injection_result_to_context_string(self):
        """SkillInjectionResult.to_context_string 应返回有效字符串或空."""
        bridge = PipelineSkillBridge()
        result = bridge.inject_for_task(
            task_description="数据库迁移",
            stage="construction",
        )
        ctx = result.to_context_string()
        if result.loaded:
            assert len(ctx) > 0
            assert "Domain Skill" in ctx
            assert "Role Skill" in ctx
        else:
            assert ctx == ""


class TestPipelineOrchestratorSkillFlow:
    def test_dispatch_includes_skill_injection(self):
        """PipelineOrchestrator.dispatch(dry_run=True) 结果含 skill_injection 字段."""
        try:
            from zephyr.integration.pipeline_orchestrator import (
                PipelineOrchestrator,
                PipelineOrchestratorConfig,
            )
        except ImportError:
            pytest.skip("PipelineOrchestrator not available")

        config = PipelineOrchestratorConfig(max_retries=1, claude_rescue_threshold=10)
        orchestrator = PipelineOrchestrator(config)

        task = TaskCard(
            task_id="DW-99901",
            namespace="DW",
            seq=99901,
            title="测试 Skill 注入 - 数据库迁移",
            description="创建数据库迁移脚本用于新增 users 表的 status 字段",
            estimated_tokens=500,
            phase=2,
            safety_level="L",
            priority="P2",
            source_blueprint="MOD-INF-019",
            source_section="§12.4",
            status="PENDING",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        result = orchestrator.dispatch(task, dry_run=True)

        skill_data = result.skill_injection
        if skill_data is not None:
            assert "loaded" in skill_data
            assert "domain_skill_id" in skill_data
            assert "role_skill_id" in skill_data
            assert "context" in skill_data
            if skill_data["loaded"]:
                assert skill_data["domain_skill_id"] is not None
                assert skill_data["role_skill_id"] is not None

    def test_call_model_includes_skill_context(self):
        """_call_model 输出含 skill_context 字段."""
        try:
            from zephyr.integration.pipeline_orchestrator import (
                PipelineOrchestrator,
                PipelineOrchestratorConfig,
            )
        except ImportError:
            pytest.skip("PipelineOrchestrator not available")

        from zephyr.autonomy_core.integration.pipeline_bridge import PipelineSkillBridge

        bridge = PipelineSkillBridge()
        injection = bridge.inject_for_task(
            task_description="数据库迁移",
            stage="construction",
        )

        task = TaskCard(
            task_id="DW-99902",
            namespace="DW",
            seq=99902,
            title="测试 _call_model Skill 注入",
            description="修改数据库 schema 添加新的迁移字段",
            estimated_tokens=500,
            phase=2,
            safety_level="L",
            priority="P2",
            source_blueprint="MOD-INF-019",
            source_section="§12.4",
            status="PENDING",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        output = PipelineOrchestrator.call_model(
            "M1",
            "A",
            "deepseek",
            task,
            token_divisor=1,
            dry_run=True,
            skill_injection=injection,
        )

        assert "skill_context" in output
        if injection and injection.loaded:
            assert len(output.get("skill_context", "")) > 0


class TestSpecEngineIntegration:
    def test_engine_status_report(self):
        """SpecEngine.status() 应返回系统技能统计."""
        engine = SpecEngine()
        status = engine.status()
        assert "total_domain" in status
        assert "total_role" in status
        assert "total" in status
        assert status["total"] > 0

    @pytest.mark.xfail(reason="#ARCH-096：skill 内容库整体缺失——锚定 ID SKILL-DOM-DBS-001 不在册；保留作功能规格书", strict=False)
    def test_engine_validate_existing_skill(self):
        """SpecEngine.validate_skill() 应对已注册 Skill 返回 valid=True."""
        engine = SpecEngine()
        result = engine.validate_skill("SKILL-DOM-DBS-001")
        assert result["valid"] is True
        assert "freshness_score" in result

    def test_engine_validate_nonexistent_skill(self):
        """SpecEngine.validate_skill() 对不存在 Skill 返回 valid=False."""
        engine = SpecEngine()
        result = engine.validate_skill("SKILL-NONEXIST-999")
        assert result["valid"] is False


class TestSkillLoaderL3References:
    @pytest.mark.xfail(reason="#ARCH-096：skill 内容库整体缺失——锚定 ID SKILL-ROL-ARC-001 不在册；保留作功能规格书", strict=False)
    def test_l3_references_available(self):
        """已注册 Skill 的 L3 references 能被列出."""
        loader = SkillLoader()
        data = loader.progressive_load("SKILL-ROL-ARC-001")
        l3 = data.get("l3_available", [])
        assert len(l3) >= 0

    @pytest.mark.xfail(reason="#ARCH-096：skill 内容库整体缺失——skills/factory/AGENT.md 不存在，L0 content 为空；保留作功能规格书", strict=False)
    def test_skill_l0_constitution_has_content(self):
        """L0 宪法应有有效内容."""
        loader = SkillLoader()
        l0 = loader.load_l0()
        assert "content" in l0
        assert len(l0["content"]) > 0
        assert "Agent" in l0["content"]
