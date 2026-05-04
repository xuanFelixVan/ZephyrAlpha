"""M1-M11 Pipeline Orchestrator 单元测试"""

from __future__ import annotations

import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


from zephyr.core.models import TaskCard
from zephyr.pipeline import (
    M_MODULE_SPECS,
    M_MODULES,
    PipelineOrchestrator,
    PipelineStatus,
)


def _make_task(task_id: str, **overrides) -> TaskCard:
    from zephyr.shared.schemas import Priority, TaskNamespace

    parts = task_id.split("-", 2)
    ns_name = parts[0] if len(parts) >= 2 else "TASK"
    seq_str = parts[-1] if len(parts) >= 2 else "1"
    seq = int(seq_str) if seq_str.isdigit() else 1
    ns = getattr(TaskNamespace, ns_name.upper(), TaskNamespace.CP)

    defaults = dict(
        task_id=task_id,
        namespace=ns,
        seq=seq,
        source_blueprint="MOD-INF-006",
        source_section="test",
        title="M1-M5 生产管线任务卡测试",
        description="验证 PipelineOrchestrator 能正确调度 DeepSeek 主力模型执行 A 区 5 个模块",
        priority=Priority.P2,
        phase=1,
        execution_model="deepseek",
        safety_level="L",
        upstream_files=["D:\\ZephyrAlpha\\\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"],
        downstream_outputs=[{"path": "D:\\test\\output.py", "description": "test"}],
        allowed_touch=["D:\\test\\"],
        forbidden_touch=["D:\\system\\"],
        applicable_rules=[{"module_id": "ADR-0040", "section": "test", "reason": "test"}],
        context_assembly_manifest=[
            {
                "file_path": "D:\\ZephyrAlpha\\\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md",
                "reason": "test",
            }
        ],
        estimated_tokens=8000,
        timeout_minutes=5,
        rollback_instructions="所有产出均为临时文件，删除 D:\\test\\ 目录即可完全撤销所有修改",
        acceptance=["管线产出 ModuleResult"],
        tags=["test", "l01_infrastructure", "deepseek", "MOD-INF-006"],
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
        task = _make_task("CP-0097", tags=["test", "l01_infrastructure", "deepseek", "MOD-INF-006", "experimental"])
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.needs_claude_rescue is True

    def test_security_triggers_claude_rescue(self) -> None:
        task = _make_task("CP-0096", tags=["test", "l01_infrastructure", "deepseek", "MOD-INF-006", "security"])
        o = PipelineOrchestrator()
        r = o.dispatch(task)
        assert r.needs_claude_rescue is True
