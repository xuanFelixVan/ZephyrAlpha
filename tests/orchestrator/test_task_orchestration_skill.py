# [BLUEPRINT] MOD-ORCH-003 | docs/03_modules/_domain_orchestrator/task_orchestration_skill/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ORCH-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.orchestrator.test_task_orchestration_skill
# [TESTS] src/zephyr/orchestrator/task_orchestration_skill.py
"""MOD-ORCH-003 单元测试：task_orchestration_skill 任务编排技能。

蓝图验收（B11-02579/CAND-ORCH-003，A7）：任务分解 → 轻量 DAG（拓扑分层 +
循环拒绝）→ 波次调度 → 失败重试/DLQ + 技能契约 Schema 登记 + 编排计划
human_gated 确认硬约束（未确认执行 Fail-Closed）。执行器/DLQ/时钟全注入
内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.orchestrator.task_orchestration_skill",
    reason="task_orchestration_skill not importable",
)

from zephyr.orchestrator.task_orchestration_skill import (  # noqa: E402
    SkillContract,
    TaskNode,
    TaskOrchestrationError,
    TaskOrchestrationSkill,
    TaskStatus,
    WorkDAG,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _node(task_id: str, depends_on=(), max_retries: int = 0) -> TaskNode:
    return TaskNode(
        task_id=task_id,
        name=f"任务-{task_id}",
        payload={"kind": "noop"},
        depends_on=tuple(depends_on),
        max_retries=max_retries,
    )


def _skill(executed: list | None = None, executor=None, dlq: list | None = None) -> TaskOrchestrationSkill:
    if executor is None:
        executor = (lambda n: executed.append(n.task_id)) if executed is not None else (lambda n: None)
    return TaskOrchestrationSkill(
        clock=lambda: _T0,
        executor=executor,
        dlq_sink=(lambda n, e: dlq.append((n.task_id, e))) if dlq is not None else None,
    )


def _contract(name: str = "task-orchestration") -> SkillContract:
    return SkillContract(
        skill_name=name,
        input_schema={"type": "object", "required": ["tasks"]},
        output_schema={"type": "object", "required": ["plan_id"]},
        registered_at=_T0,
    )


def _confirmed_plan(skill: TaskOrchestrationSkill, plan_id: str = "plan-1", nodes=None):
    plan = skill.decompose(plan_id, nodes if nodes is not None else [_node("a")])
    skill.confirm_plan(plan_id)
    return plan


# ──────────────────────────────────────────────────────────────────────────────
# 技能契约登记
# ──────────────────────────────────────────────────────────────────────────────


class TestContract:
    def test_register_and_query(self) -> None:
        skill = _skill()
        skill.register_contract(_contract())
        got = skill.contract_of("task-orchestration")
        assert got.input_schema["required"] == ["tasks"]

    def test_register_empty_name_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().register_contract(_contract(name=""))

    def test_register_duplicate_raises(self) -> None:
        skill = _skill()
        skill.register_contract(_contract())
        with pytest.raises(TaskOrchestrationError):
            skill.register_contract(_contract())

    def test_register_bad_schema_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().register_contract(
                SkillContract(skill_name="s", input_schema="not-a-mapping", output_schema={}, registered_at=_T0)
            )

    def test_contract_of_unknown_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().contract_of("ghost-skill")

    def test_contracts_sorted(self) -> None:
        skill = _skill()
        skill.register_contract(_contract("zeta"))
        skill.register_contract(_contract("alpha"))
        assert skill.contracts() == ("alpha", "zeta")


# ──────────────────────────────────────────────────────────────────────────────
# 任务分解 → DAG（拓扑分层 + 循环拒绝）
# ──────────────────────────────────────────────────────────────────────────────


class TestDecompose:
    def test_waves_topological(self) -> None:
        skill = _skill()
        plan = skill.decompose(
            "plan-1",
            [
                _node("c", depends_on=("a", "b")),
                _node("a"),
                _node("b", depends_on=("a",)),
                _node("d"),
            ],
        )
        assert plan.waves == (("a", "d"), ("b",), ("c",))  # 层内按 task_id 排序

    def test_decompose_empty_plan_id_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().decompose("", [_node("a")])

    def test_decompose_duplicate_plan_raises(self) -> None:
        skill = _skill()
        skill.decompose("plan-1", [_node("a")])
        with pytest.raises(TaskOrchestrationError):
            skill.decompose("plan-1", [_node("b")])

    def test_decompose_empty_tasks_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().decompose("plan-1", [])

    def test_decompose_duplicate_task_id_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().decompose("plan-1", [_node("a"), _node("a")])

    def test_decompose_unknown_dependency_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().decompose("plan-1", [_node("a", depends_on=("ghost",))])

    def test_decompose_cycle_rejected(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().decompose(
                "plan-1",
                [
                    _node("a", depends_on=("c",)),
                    _node("b", depends_on=("a",)),
                    _node("c", depends_on=("b",)),
                ],
            )

    def test_decompose_self_loop_rejected(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().decompose("plan-1", [_node("a", depends_on=("a",))])

    def test_decompose_negative_retries_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().decompose("plan-1", [_node("a", max_retries=-1)])

    def test_workdag_standalone(self) -> None:
        dag = WorkDAG()
        dag.add_node("a")
        dag.add_node("b", ("a",))
        assert dag.nodes() == ("a", "b")
        assert dag.dependencies("b") == ("a",)
        assert dag.waves() == (("a",), ("b",))
        with pytest.raises(TaskOrchestrationError):
            dag.dependencies("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# human_gated 确认 + 波次执行（重试/DLQ）
# ──────────────────────────────────────────────────────────────────────────────


class TestExecute:
    def test_execute_without_confirm_raises(self) -> None:
        skill = _skill()
        skill.decompose("plan-1", [_node("a")])
        with pytest.raises(TaskOrchestrationError):
            skill.execute("plan-1")

    def test_execute_rejected_plan_raises(self) -> None:
        skill = _skill()
        skill.decompose("plan-1", [_node("a")])
        skill.confirm_plan("plan-1", approved=False)
        assert skill.is_confirmed("plan-1") is False
        with pytest.raises(TaskOrchestrationError):
            skill.execute("plan-1")

    def test_execute_without_executor_raises(self) -> None:
        skill = TaskOrchestrationSkill(clock=lambda: _T0)
        skill.decompose("plan-1", [_node("a")])
        skill.confirm_plan("plan-1")
        with pytest.raises(TaskOrchestrationError):
            skill.execute("plan-1")

    def test_execute_wave_order_deterministic(self) -> None:
        executed: list[str] = []
        skill = _skill(executed)
        _confirmed_plan(
            skill,
            nodes=[
                _node("c", depends_on=("a", "b")),
                _node("a"),
                _node("b", depends_on=("a",)),
            ],
        )
        report = skill.execute("plan-1")
        assert executed == ["a", "b", "c"]  # 波次+层内字典序
        assert report.succeeded is True
        assert report.dlq_task_ids == ()
        assert all(r.attempts == 1 for r in report.records)

    def test_execute_retry_then_success(self) -> None:
        calls: list[str] = []

        def _flaky(node: TaskNode) -> None:
            calls.append(node.task_id)
            if len(calls) < 3:
                raise RuntimeError("瞬时故障")

        skill = _skill(executor=_flaky)
        _confirmed_plan(skill, nodes=[_node("a", max_retries=2)])
        report = skill.execute("plan-1")
        assert report.succeeded is True
        assert report.status_of("a") is TaskStatus.SUCCEEDED
        assert len(calls) == 3  # 1 + 2 次重试内成功

    def test_execute_retry_exhausted_to_dlq(self) -> None:
        dlq: list = []

        def _always_fail(node: TaskNode) -> None:
            raise ValueError("永久故障")

        skill = _skill(executor=_always_fail, dlq=dlq)
        _confirmed_plan(skill, nodes=[_node("a", max_retries=1)])
        report = skill.execute("plan-1")
        assert report.succeeded is False
        assert report.dlq_task_ids == ("a",)
        assert report.records[0].attempts == 2  # 1 + 1 重试
        assert "永久故障" in report.records[0].error
        assert dlq == [("a", report.records[0].error)]  # DLQ 回调留痕

    def test_execute_cascade_skip(self) -> None:
        def _fail_on_b(node: TaskNode) -> None:
            if node.task_id == "b":
                raise RuntimeError("b 故障")

        skill = _skill(executor=_fail_on_b)
        _confirmed_plan(
            skill,
            nodes=[
                _node("a"),
                _node("b"),
                _node("c", depends_on=("b",)),
                _node("d", depends_on=("c",)),
            ],
        )
        report = skill.execute("plan-1")
        assert report.status_of("a") is TaskStatus.SUCCEEDED
        assert report.status_of("b") is TaskStatus.DLQ
        assert report.status_of("c") is TaskStatus.SKIPPED
        assert report.status_of("d") is TaskStatus.SKIPPED  # 级联
        assert report.records[2].attempts == 0  # SKIPPED 不执行

    def test_execute_unknown_plan_raises(self) -> None:
        with pytest.raises(TaskOrchestrationError):
            _skill().execute("ghost-plan")

    def test_report_query_and_status_of(self) -> None:
        skill = _skill()
        _confirmed_plan(skill)
        with pytest.raises(TaskOrchestrationError):
            skill.report_of("plan-1")  # 未执行无报告
        report = skill.execute("plan-1")
        assert skill.report_of("plan-1") is report
        assert skill.plan_of("plan-1").plan_id == "plan-1"
        with pytest.raises(TaskOrchestrationError):
            report.status_of("ghost-task")
        with pytest.raises(TaskOrchestrationError):
            skill.plan_of("ghost-plan")
