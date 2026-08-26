# [BLUEPRINT] MOD-INF-078 | docs/03_modules/_domain_infrastructure_runtime/ml_pipeline_process/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-078 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_runtime.test_ml_pipeline_process
# [TESTS] src/zephyr/infra_runtime/ml_pipeline_process.py
"""MOD-INF-078 单元测试：ml_pipeline_process P5 ML 管线进程编排。

蓝图验收（B14-04526/CAND-H1FS-011，A9 运维架构 §进程拓扑）：
四职责任务队列（inference/training/vram_mgmt/model_version 入队/出队/优先级）+
资源声明（核 16-19 + 20GB）+ 优先级 40 最低交易时段退让（training 挂起）+
GPU 夜间时分互斥（时段表注入）。时钟/交易时段/GPU 时段表全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infra_runtime.ml_pipeline_process",
    reason="ml_pipeline_process not importable",
)

from zephyr.infra_runtime.ml_pipeline_process import (  # noqa: E402
    BASE_PRIORITY,
    DECLARED_CORES,
    MEMORY_BUDGET_GB,
    MlPipelineError,
    MlPipelineProcess,
    MlTask,
    TaskKind,
)

_T0 = datetime.datetime(2026, 8, 25, 22, 0, 0)


def _proc(
    trading: bool = False,
    gpu_ok: bool = True,
) -> MlPipelineProcess:
    return MlPipelineProcess(
        clock=lambda: _T0,
        is_trading_hours=lambda: trading,
        gpu_schedule=lambda _now: gpu_ok,
    )


def _task(
    task_id: str = "t-1",
    kind: TaskKind = TaskKind.INFERENCE,
    priority: int = 40,
    requires_gpu: bool = False,
) -> MlTask:
    return MlTask(task_id=task_id, kind=kind, priority=priority, requires_gpu=requires_gpu)


# ──────────────────────────────────────────────────────────────────────────────
# 资源声明
# ──────────────────────────────────────────────────────────────────────────────


class TestResourceDeclaration:
    def test_declaration_constants(self) -> None:
        decl = MlPipelineProcess.resource_declaration()
        assert decl["cores"] == DECLARED_CORES == (16, 17, 18, 19)
        assert decl["memory_gb"] == MEMORY_BUDGET_GB == 20
        assert decl["base_priority"] == BASE_PRIORITY == 40


# ──────────────────────────────────────────────────────────────────────────────
# 入队（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestEnqueue:
    def test_enqueue_four_kinds(self) -> None:
        proc = _proc()
        for i, kind in enumerate(TaskKind):
            proc.enqueue(_task(task_id=f"t-{i}", kind=kind))
        assert proc.queue_size() == 4

    def test_empty_task_id_raises(self) -> None:
        with pytest.raises(MlPipelineError):
            _proc().enqueue(_task(task_id=""))

    def test_duplicate_task_id_raises(self) -> None:
        proc = _proc()
        proc.enqueue(_task())
        with pytest.raises(MlPipelineError):
            proc.enqueue(_task())

    def test_invalid_kind_raises(self) -> None:
        with pytest.raises(MlPipelineError):
            _proc().enqueue(_task(kind="bogus"))  # type: ignore[arg-type]

    def test_priority_out_of_range_raises(self) -> None:
        proc = _proc()
        with pytest.raises(MlPipelineError):
            proc.enqueue(_task(priority=-1))
        with pytest.raises(MlPipelineError):
            proc.enqueue(_task(priority=41))

    def test_priority_boundary_ok(self) -> None:
        proc = _proc()
        proc.enqueue(_task(task_id="hi", priority=0))
        proc.enqueue(_task(task_id="lo", priority=40))
        assert proc.queue_size() == 2

    def test_non_task_object_raises(self) -> None:
        with pytest.raises(MlPipelineError):
            _proc().enqueue("not-a-task")  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 出队（优先级 + 退让 + 互斥）
# ──────────────────────────────────────────────────────────────────────────────


class TestDequeue:
    def test_dequeue_priority_order(self) -> None:
        proc = _proc()
        proc.enqueue(_task(task_id="low", priority=40))
        proc.enqueue(_task(task_id="high", priority=5))
        assert proc.dequeue().task_id == "high"  # 数值小者先出
        assert proc.dequeue().task_id == "low"
        assert proc.dequeue() is None

    def test_dequeue_fifo_tie_break(self) -> None:
        proc = _proc()
        proc.enqueue(_task(task_id="first", priority=40))
        proc.enqueue(_task(task_id="second", priority=40))
        assert proc.dequeue().task_id == "first"
        assert proc.dequeue().task_id == "second"

    def test_training_suspended_during_trading_hours(self) -> None:
        proc = _proc(trading=True)
        proc.enqueue(_task(task_id="train", kind=TaskKind.TRAINING, priority=0))
        proc.enqueue(_task(task_id="infer", kind=TaskKind.INFERENCE, priority=40))
        # 交易时段 training 挂起退让，即使优先级更高也不出队
        assert proc.dequeue().task_id == "infer"
        assert proc.dequeue() is None
        assert proc.queue_size() == 1

    def test_training_resumes_after_hours(self) -> None:
        flag = {"trading": True}
        proc = MlPipelineProcess(
            clock=lambda: _T0,
            is_trading_hours=lambda: flag["trading"],
            gpu_schedule=lambda _now: True,
        )
        proc.enqueue(_task(task_id="train", kind=TaskKind.TRAINING))
        assert proc.dequeue() is None
        flag["trading"] = False  # 盘后恢复
        assert proc.dequeue().task_id == "train"

    def test_gpu_task_blocked_outside_window(self) -> None:
        proc = _proc(gpu_ok=False)
        proc.enqueue(_task(task_id="gpu-job", requires_gpu=True))
        proc.enqueue(_task(task_id="cpu-job", requires_gpu=False, priority=40))
        assert proc.dequeue().task_id == "cpu-job"
        assert proc.dequeue() is None

    def test_gpu_task_allowed_inside_window(self) -> None:
        proc = _proc(gpu_ok=True)
        proc.enqueue(_task(task_id="gpu-job", requires_gpu=True))
        assert proc.dequeue().task_id == "gpu-job"

    def test_dequeue_empty_returns_none(self) -> None:
        assert _proc().dequeue() is None

    def test_is_suspended_flags(self) -> None:
        gpu_task = _task(task_id="g", requires_gpu=True)
        train_task = _task(task_id="tr", kind=TaskKind.TRAINING)
        infer_task = _task(task_id="i", kind=TaskKind.INFERENCE)
        proc = _proc(trading=True, gpu_ok=False)
        assert proc.is_suspended(gpu_task)
        assert proc.is_suspended(train_task)
        assert not proc.is_suspended(infer_task)


# ──────────────────────────────────────────────────────────────────────────────
# 取消与查询（确定性）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_cancel_ok(self) -> None:
        proc = _proc()
        proc.enqueue(_task())
        assert proc.cancel("t-1").task_id == "t-1"
        assert proc.queue_size() == 0

    def test_cancel_unknown_raises(self) -> None:
        with pytest.raises(MlPipelineError):
            _proc().cancel("ghost")

    def test_pending_kind_filter(self) -> None:
        proc = _proc()
        proc.enqueue(_task(task_id="a", kind=TaskKind.INFERENCE))
        proc.enqueue(_task(task_id="b", kind=TaskKind.TRAINING))
        assert [t.task_id for t in proc.pending(TaskKind.TRAINING)] == ["b"]

    def test_pending_invalid_kind_raises(self) -> None:
        with pytest.raises(MlPipelineError):
            _proc().pending("bogus")  # type: ignore[arg-type]

    def test_pending_deterministic_order(self) -> None:
        def build() -> list[str]:
            proc = _proc()
            proc.enqueue(_task(task_id="c", priority=30))
            proc.enqueue(_task(task_id="a", priority=10))
            proc.enqueue(_task(task_id="b", priority=10))
            return [t.task_id for t in proc.pending()]

        assert build() == build() == ["a", "b", "c"]  # 同输入必同输出
