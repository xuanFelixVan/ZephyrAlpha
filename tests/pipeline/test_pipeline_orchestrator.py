# [A_test] module_id: SRC-TST-1926 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-545 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.pipeline.test_pipeline_orchestrator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""M1-M11 Pipeline Orchestrator 单元测试"""

import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from zephyr.infrastructure.pipeline.models import (
    M_MODULE_SPECS,
    M_MODULES,
    PipelineStatus,
)
from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator
from zephyr.shared.foundation.models import TaskCard


def _make_task(task_id: str, **overrides) -> TaskCard:
    from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace
    from zephyr.integration.shared.schema.severity_types import Priority

    parts = task_id.split("-", 2)
    ns_name = parts[0] if len(parts) >= 2 else "TASK"
    seq_str = parts[-1] if len(parts) >= 2 else "1"
    seq = int(seq_str) if seq_str.isdigit() else 1
    ns = getattr(TaskNamespace, ns_name.upper(), TaskNamespace.CP)

    defaults = dict(
        task_id=task_id,
        namespace=ns,
        seq=seq,
        source_blueprint="MOD-INF-039",
        source_section="test",
        title="M1-M5 生产管线任务卡测试",
        description="验证 PipelineOrchestrator 能正确调度 DeepSeek 主力模型执行 A 区 5 个模块",
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level="L",
        upstream_files=["D:\\ZephyrAlpha\\\\docs\\03_modules\\l01-infrastructure\\task-system\\blueprint.md"],
        downstream_outputs=[{"path": "D:\\test\\output.py", "description": "test"}],
        allowed_touch=["D:\\test\\"],
        forbidden_touch=["D:\\system\\"],
        applicable_rules=[{"module_id": "ADR-0040", "section": "test", "reason": "test"}],
        context_assembly_manifest=[
            {
                "file_path": "D:\\ZephyrAlpha\\\\docs\\03_modules\\l01-infrastructure\\task-system\\blueprint.md",
                "reason": "test",
            }
        ],
        estimated_tokens=8000,
        timeout_minutes=5,
        rollback_instructions="所有产出均为临时文件，删除 D:\\test\\ 目录即可完全撤销所有修改",
        acceptance=["管线产出 ModuleResult"],
        tags=["test", "l01-infrastructure", "deepseek", "MOD-INF-039"],
        assigned_pipeline="A",
        created_at="2026-05-02T00:00:00",
        updated_at="2026-05-02T00:00:00",
    )
    defaults.update(overrides)
    return TaskCard(**defaults)


class TestMModules:
    def test_all_modules_loaded(self) -> None:
        assert len(M_MODULES) == 11

    def test_a_pipeline_modules(self) -> None:
        a_m = [m for m in M_MODULES if M_MODULE_SPECS[m]["pipeline"] == "A"]
        assert a_m == ["M1", "M2", "M3", "M4", "M5"]

    def test_b_pipeline_modules(self) -> None:
        b_m = [m for m in M_MODULES if M_MODULE_SPECS[m]["pipeline"] == "B"]
        assert b_m == ["M6", "M7", "M8", "M9", "M10", "M11"]

    def test_glm_modules(self) -> None:
        glm_m = [m for m in M_MODULES if M_MODULE_SPECS[m]["model"] == "glm"]
        assert glm_m == ["M5", "M7"]


class TestPipelineDispatch:
    def test_a_pipeline_dispatch(self) -> None:
        task = _make_task("CP-0099")
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.overall_status == PipelineStatus.SUCCESS
        assert len(r.modules_executed) == 5
        assert all(m.status.value == "success" for m in r.modules_executed)

    def test_b_pipeline_dispatch(self) -> None:
        task = _make_task(
            "CP-0098",
            assigned_pipeline="B",
            title="M6-M11 B区审计管线测试",
            description="验证 B 区 6 个模块能正确调度，且 M7 必须指定 GLM 模型",
        )
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.overall_status == PipelineStatus.SUCCESS
        assert len(r.modules_executed) == 6
        m7 = next(m for m in r.modules_executed if m.module_id == "M7")
        assert m7.model == "glm"

    def test_experimental_triggers_claude_rescue(self) -> None:
        task = _make_task("CP-0097", tags=["test", "l01-infrastructure", "deepseek", "MOD-INF-039", "experimental"])
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.needs_claude_rescue is True

    def test_security_triggers_claude_rescue(self) -> None:
        task = _make_task("CP-0096", tags=["test", "l01-infrastructure", "deepseek", "MOD-INF-039", "security"])
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.needs_claude_rescue is True

    def test_ct_pipe_ops_slices_from_m2(self) -> None:
        task = _make_task(
            "CP-0101",
            tags=[
                "test",
                "l01-infrastructure",
                "deepseek",
                "MOD-INF-039",
                "ct_pipe.task_type=OPS",
            ],
        )
        r = PipelineOrchestrator().dispatch(task)
        assert r.ct_pipe_route is not None
        assert r.ct_pipe_route.node_id == "M2"
        mids = [m.module_id for m in r.modules_executed]
        assert mids == ["M2", "M3", "M4", "M5"]

    def test_ct_pipe_audit_p0_vs_assigned_pipeline_b_warns(self) -> None:
        from zephyr.integration.shared.schema.severity_types import Priority

        task = _make_task(
            "CP-0102",
            pipeline_task_type="AUDIT",
            priority=Priority.P0,
            assigned_pipeline="B",
        )
        r = PipelineOrchestrator().dispatch(task)
        assert r.ct_pipe_route is not None
        assert r.ct_pipe_route.node_id == "M3"
        assert r.pipeline == "A"
        assert any("CT-PIPE" in w or "assigned_pipeline" in w for w in r.ct_pipe_warnings)

    def test_ct_pipe_doc_write_missing_layer_is_failure(self) -> None:
        task = _make_task("CP-0103", pipeline_task_type="DOC_WRITE")
        r = PipelineOrchestrator().dispatch(task)
        assert r.overall_status == PipelineStatus.FAILURE
        assert r.ct_pipe_warnings
        assert r.modules_executed == []

    def test_ct_pipe_model_build_high_enters_m1(self) -> None:
        task = _make_task(
            "CP-0104",
            tags=[
                "test",
                "l01-infrastructure",
                "MOD-INF-039",
                "ct_pipe.task_type=MODEL_BUILD",
                "ct_pipe.complexity=HIGH",
            ],
        )
        r = PipelineOrchestrator().dispatch(task)
        assert r.ct_pipe_route is not None
        assert r.ct_pipe_route.node_id == "M1"
        assert [m.module_id for m in r.modules_executed] == ["M1", "M2", "M3", "M4", "M5"]


# ============================================================================
# B171: v0.9.0 新特性测试覆盖
# ============================================================================


class TestIdempotency:
    """B149: dispatch() 幂等防护"""

    def test_duplicate_dispatch_rejected(self) -> None:
        task = _make_task("CP-0030")
        o = PipelineOrchestrator()
        r1 = o.dispatch(task)
        r2 = o.dispatch(task)
        assert r1.overall_status == PipelineStatus.SUCCESS
        assert r2.overall_status == PipelineStatus.FAILURE
        assert any("IDEMPOTENCY" in w for w in (r2.ct_pipe_warnings or []))


class TestCircuitBreaker:
    """B151: 断路器三态"""

    def test_initial_closed(self) -> None:
        o = PipelineOrchestrator()
        assert not o._circuit_breaker_states

    def test_reset_returns_zero_if_no_breaker(self) -> None:
        o = PipelineOrchestrator()
        assert o.reset_circuit_breakers() == 0


class TestEmergencyFallback:
    """B147: 三模全失败降级"""

    def test_no_fallback_on_success(self) -> None:
        task = _make_task("CP-0031")
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.fallback_plan is None

    def test_fallback_detects_all_failure(self) -> None:
        task = _make_task("CP-0032")
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        plan = o._emergency_fallback(r.modules_executed, task)
        assert not plan.activated


class TestImpactAssessment:
    """B157: AI 影响评估"""

    def test_normal_task_is_low_risk(self) -> None:
        task = _make_task("CP-0033")
        o = PipelineOrchestrator()
        impact = o._assess_impact(task)
        assert impact.risk_tier == "low"
        assert not impact.human_review_required

    def test_security_tag_is_critical(self) -> None:
        task = _make_task("CP-0034", tags=["security", "auth"])
        o = PipelineOrchestrator()
        impact = o._assess_impact(task)
        assert impact.risk_tier == "critical"
        assert impact.human_review_required


class TestRateLimit:
    """B162: 速率限制感知"""

    def test_no_backpressure_for_first_call(self) -> None:
        o = PipelineOrchestrator()
        limited, wait = o._check_rate_limit("deepseek")
        assert not limited
        assert wait == 0.0


class TestCostTracking:
    """B161: $ 成本追踪"""

    def test_dispatch_includes_cost(self) -> None:
        task = _make_task("CP-0035", estimated_tokens=50000)
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.cost_total_usd >= 0.0
        assert len(r.cost_records) > 0

    def test_get_cost_summary(self) -> None:
        task = _make_task("CP-0036")
        o = PipelineOrchestrator()
        o.dispatch(task)
        summary = o.get_cost_summary()
        assert "total_usd" in summary
        assert "by_model" in summary


class TestDeadLetterQueue:
    """B169: 死信队列"""

    def test_get_dead_letters_initially_empty(self) -> None:
        o = PipelineOrchestrator()
        assert o.get_dead_letters() == []


class TestConfigPersistence:
    """B153: Config 持久化"""

    def test_save_state_includes_config(self) -> None:
        o = PipelineOrchestrator()
        state = o.save_state()
        assert "config" in state
        assert state["config"]["max_retries"] == 3

    def test_load_state_restores_custom_config(self) -> None:
        o = PipelineOrchestrator()
        state = o.save_state()
        state["config"]["max_retries"] = 7
        o2 = PipelineOrchestrator()
        o2.load_state(state)
        assert o2._cfg.max_retries == 7


class TestExperimentRouting:
    """B159: A/B 实验路由"""

    def test_no_experiment_returns_none(self) -> None:
        o = PipelineOrchestrator()
        task = _make_task("CP-0037")
        assert o._resolve_experiment(task) is None

    def test_register_experiment(self) -> None:
        o = PipelineOrchestrator()
        o.register_experiment("exp-test", "route-a", "route-b")
        exps = o.get_experiments()
        assert "exp-test" in exps


class TestModelCollapseIntegration:
    """B132+B158: 模型崩塌 + 置信度 集成"""

    def test_dispatch_includes_collapse_field(self) -> None:
        task = _make_task("CP-0038", tags=["l01-infrastructure", "test"])
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.model_collapse is None

    def test_text_similarity_on_identical(self) -> None:
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator as PO

        assert PO._text_similarity("hello world", "hello world") == 1.0

    def test_text_similarity_on_different(self) -> None:
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator as PO

        sim = PO._text_similarity("hello world", "foo bar baz")
        assert sim < 0.5


class TestHealthCheckSelfHealing:
    """B168: health_check 含自愈建议"""

    def test_health_check_includes_new_fields(self) -> None:
        o = PipelineOrchestrator()
        health = o.health_check()
        assert "dead_letters" in health
        assert "cost_total_usd" in health
        assert "circuit_breakers_open" in health
        assert "active_dispatches" in health
