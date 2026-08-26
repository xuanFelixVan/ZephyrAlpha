# [BLUEPRINT] MOD-KNW-014 | docs/03_modules/_domain_knowledge/research_workflow_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_research_workflow_engine
# [TESTS] src/zephyr/knowledge/research_workflow_engine.py
"""MOD-KNW-014 单元测试：research_workflow_engine 研究工作流引擎。

蓝图验收（B6-08551/CAND-KNW-017，B6 D-RESEARCH-09）：
DAG 节点依赖拓扑执行（循环检测 Fail-Closed）+ 研究模板注册表
（因子挖掘→IC验证→注册→灰度）+ 任务重试指数退避（注入时钟/sleeper 不真睡）+
审计留痕 + 上线门禁注入（拒绝即阻断该节点并标记）。
时钟/sleeper/门禁/审计全注入内存替身，不触网不真睡。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.research_workflow_engine",
    reason="research_workflow_engine not importable",
)

from zephyr.knowledge.research_workflow_engine import (  # noqa: E402
    NodeStatus,
    ResearchTemplate,
    ResearchWorkflowEngine,
    ResearchWorkflowError,
    RunStatus,
    WorkflowNode,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _engine(*, gate=None, sink=None, sleeps=None, base=1.0, maxb=60.0) -> ResearchWorkflowEngine:
    return ResearchWorkflowEngine(
        clock=lambda: _T0,
        sleeper=(lambda s: sleeps.append(s)) if sleeps is not None else None,
        gate=gate,
        audit_sink=(lambda e: sink.append(e)) if sink is not None else None,
        base_backoff_seconds=base,
        max_backoff_seconds=maxb,
    )


def _task(log: list | None = None, value=None):
    def _run(ctx):
        if log is not None:
            log.append(ctx.node_id)
        return value if value is not None else ctx.node_id

    return _run


def _node(node_id, *, deps=(), retries=0, gate=False, task=None) -> WorkflowNode:
    return WorkflowNode(
        node_id=node_id,
        task=task if task is not None else _task(),
        depends_on=tuple(deps),
        max_retries=retries,
        requires_gate=gate,
    )


def _template(tid: str = "tpl", nodes=()) -> ResearchTemplate:
    return ResearchTemplate(template_id=tid, description="测试模板", nodes=tuple(nodes))


# ──────────────────────────────────────────────────────────────────────────────
# 模板注册表（结构校验 + 循环检测 Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterTemplate:
    def test_register_and_list_sorted(self) -> None:
        engine = _engine()
        engine.register_template(_template("b-tpl", [_node("n1")]))
        engine.register_template(_template("a-tpl", [_node("n1")]))
        assert [t.template_id for t in engine.list_templates()] == ["a-tpl", "b-tpl"]
        assert engine.get_template("b-tpl").description == "测试模板"

    def test_duplicate_template_raises(self) -> None:
        engine = _engine()
        engine.register_template(_template("tpl", [_node("n1")]))
        with pytest.raises(ResearchWorkflowError):
            engine.register_template(_template("tpl", [_node("n1")]))

    def test_empty_template_id_raises(self) -> None:
        engine = _engine()
        with pytest.raises(ResearchWorkflowError):
            engine.register_template(_template("", [_node("n1")]))

    def test_duplicate_node_id_raises(self) -> None:
        engine = _engine()
        with pytest.raises(ResearchWorkflowError):
            engine.register_template(_template("tpl", [_node("n1"), _node("n1")]))

    def test_unknown_dependency_raises(self) -> None:
        engine = _engine()
        with pytest.raises(ResearchWorkflowError):
            engine.register_template(_template("tpl", [_node("n1", deps=("ghost",))]))

    def test_self_loop_raises(self) -> None:
        engine = _engine()
        with pytest.raises(ResearchWorkflowError):
            engine.register_template(_template("tpl", [_node("n1", deps=("n1",))]))

    def test_cycle_detected_raises(self) -> None:
        engine = _engine()
        nodes = [
            _node("a", deps=("c",)),
            _node("b", deps=("a",)),
            _node("c", deps=("b",)),
        ]
        with pytest.raises(ResearchWorkflowError):
            engine.register_template(_template("tpl", nodes))


# ──────────────────────────────────────────────────────────────────────────────
# DAG 拓扑执行
# ──────────────────────────────────────────────────────────────────────────────


class TestRun:
    def test_run_unknown_template_raises(self) -> None:
        engine = _engine()
        with pytest.raises(ResearchWorkflowError):
            engine.run("ghost")

    def test_linear_dag_executes_in_order(self) -> None:
        log: list[str] = []
        engine = _engine()
        engine.register_template(_template("tpl", [
            _node("n1", task=_task(log)),
            _node("n2", deps=("n1",), task=_task(log)),
            _node("n3", deps=("n2",), task=_task(log)),
        ]))
        result = engine.run("tpl")
        assert log == ["n1", "n2", "n3"]
        assert result.status is RunStatus.SUCCEEDED
        assert [r.node_id for r in result.node_results] == ["n1", "n2", "n3"]
        assert all(r.status is NodeStatus.SUCCEEDED for r in result.node_results)

    def test_outputs_passed_to_dependents(self) -> None:
        seen: dict = {}

        def _downstream(ctx):
            seen["upstream"] = ctx.outputs["n1"]
            return "done"

        engine = _engine()
        engine.register_template(_template("tpl", [
            _node("n1", task=_task(value=42)),
            _node("n2", deps=("n1",), task=_downstream),
        ]))
        result = engine.run("tpl", context={"tag": "exp-1"})
        assert result.status is RunStatus.SUCCEEDED
        assert seen["upstream"] == 42

    def test_parallel_branches_deterministic_order(self) -> None:
        log: list[str] = []
        engine = _engine()
        engine.register_template(_template("tpl", [
            _node("root", task=_task(log)),
            _node("b", deps=("root",), task=_task(log)),
            _node("a", deps=("root",), task=_task(log)),
        ]))
        engine.run("tpl")
        assert log == ["root", "a", "b"]  # Kahn ready 按 node_id 排序

    def test_duplicate_run_id_raises(self) -> None:
        engine = _engine()
        engine.register_template(_template("tpl", [_node("n1")]))
        engine.run("tpl", run_id="run-x")
        with pytest.raises(ResearchWorkflowError):
            engine.run("tpl", run_id="run-x")

    def test_default_run_id_deterministic(self) -> None:
        engine = _engine()
        engine.register_template(_template("tpl", [_node("n1")]))
        first = engine.run("tpl")
        second = engine.run("tpl")
        assert first.run_id == "tpl-run-0001"
        assert second.run_id == "tpl-run-0002"
        assert [r.run_id for r in engine.list_runs()] == ["tpl-run-0001", "tpl-run-0002"]
        assert engine.get_run("tpl-run-0001") is first

    def test_node_failure_failed_and_downstream_skipped(self) -> None:
        def _boom(ctx):
            raise RuntimeError("ic check failed")

        engine = _engine()
        engine.register_template(_template("tpl", [
            _node("n1"),
            _node("n2", deps=("n1",), task=_boom),
            _node("n3", deps=("n2",)),
        ]))
        result = engine.run("tpl")
        assert result.status is RunStatus.FAILED
        by_id = {r.node_id: r for r in result.node_results}
        assert by_id["n2"].status is NodeStatus.FAILED
        assert by_id["n2"].attempts == 1  # 默认 max_retries=0
        assert "ic check failed" in by_id["n2"].error
        assert by_id["n3"].status is NodeStatus.SKIPPED
        assert "上游未成功" in by_id["n3"].error


# ──────────────────────────────────────────────────────────────────────────────
# 重试指数退避（注入 sleeper 不真睡）
# ──────────────────────────────────────────────────────────────────────────────


class TestRetry:
    def test_retry_backoff_sleeps_exponential(self) -> None:
        sleeps: list[float] = []

        def _boom(ctx):
            raise RuntimeError("boom")

        engine = _engine(sleeps=sleeps)
        engine.register_template(_template("tpl", [_node("n1", retries=2, task=_boom)]))
        result = engine.run("tpl")
        assert sleeps == [1.0, 2.0]  # base * 2^0, base * 2^1
        node_result = result.node_results[0]
        assert node_result.status is NodeStatus.FAILED
        assert node_result.attempts == 3

    def test_backoff_capped_at_max(self) -> None:
        sleeps: list[float] = []

        def _boom(ctx):
            raise RuntimeError("boom")

        engine = _engine(sleeps=sleeps, base=10.0, maxb=15.0)
        engine.register_template(_template("tpl", [_node("n1", retries=2, task=_boom)]))
        engine.run("tpl")
        assert sleeps == [10.0, 15.0]  # 第二次 20 被 max 截断

    def test_retry_eventually_succeeds(self) -> None:
        sleeps: list[float] = []
        calls = {"n": 0}

        def _flaky(ctx):
            calls["n"] += 1
            if calls["n"] < 3:
                raise RuntimeError("flaky")
            return "ok"

        engine = _engine(sleeps=sleeps)
        engine.register_template(_template("tpl", [_node("n1", retries=2, task=_flaky)]))
        result = engine.run("tpl")
        assert result.status is RunStatus.SUCCEEDED
        assert result.node_results[0].attempts == 3
        assert result.node_results[0].output == "ok"
        assert sleeps == [1.0, 2.0]

    def test_invalid_backoff_params_raise(self) -> None:
        with pytest.raises(ResearchWorkflowError):
            _engine(base=0.0)
        with pytest.raises(ResearchWorkflowError):
            _engine(maxb=0.0)


# ──────────────────────────────────────────────────────────────────────────────
# 上线门禁（拒绝即阻断该节点并标记）
# ──────────────────────────────────────────────────────────────────────────────


class TestGate:
    def test_gate_deny_blocks_node_and_skips_downstream(self) -> None:
        log: list[str] = []
        engine = _engine(gate=lambda run_id, node_id: False)
        engine.register_template(_template("tpl", [
            _node("n1", task=_task(log)),
            _node("n2", deps=("n1",), gate=True, task=_task(log)),
            _node("n3", deps=("n2",), task=_task(log)),
        ]))
        result = engine.run("tpl")
        assert log == ["n1"]  # 被拒节点 task 未执行
        assert result.status is RunStatus.BLOCKED
        by_id = {r.node_id: r for r in result.node_results}
        assert by_id["n2"].status is NodeStatus.BLOCKED
        assert "门禁拒绝" in by_id["n2"].error
        assert by_id["n3"].status is NodeStatus.SKIPPED

    def test_gate_not_injected_fail_closed_blocks(self) -> None:
        engine = _engine()  # 未注入 gate
        engine.register_template(_template("tpl", [_node("n1", gate=True)]))
        result = engine.run("tpl")
        assert result.status is RunStatus.BLOCKED
        assert "未注入" in result.node_results[0].error

    def test_gate_exception_treated_as_deny(self) -> None:
        def _boom(run_id, node_id):
            raise RuntimeError("gate down")

        engine = _engine(gate=_boom)
        engine.register_template(_template("tpl", [_node("n1", gate=True)]))
        result = engine.run("tpl")
        assert result.status is RunStatus.BLOCKED
        assert "异常" in result.node_results[0].error

    def test_gate_receives_run_and_node_id(self) -> None:
        seen: list[tuple[str, str]] = []
        engine = _engine(gate=lambda run_id, node_id: seen.append((run_id, node_id)) or True)
        engine.register_template(_template("tpl", [_node("n1", gate=True)]))
        result = engine.run("tpl", run_id="run-g1")
        assert seen == [("run-g1", "n1")]
        assert result.status is RunStatus.SUCCEEDED


# ──────────────────────────────────────────────────────────────────────────────
# 审计留痕
# ──────────────────────────────────────────────────────────────────────────────


class TestAudit:
    def test_audit_trail_ordered_events(self) -> None:
        sink: list = []
        engine = _engine(sink=sink)
        engine.register_template(_template("tpl", [
            _node("n1"),
            _node("n2", deps=("n1",)),
        ]))
        engine.run("tpl", run_id="run-a1")
        events = [(e.event, e.node_id) for e in sink]
        assert events == [
            ("run_started", None),
            ("node_succeeded", "n1"),
            ("node_succeeded", "n2"),
            ("run_finished", None),
        ]
        seqs = [e.seq for e in sink]
        assert seqs == sorted(seqs) and len(set(seqs)) == len(seqs)  # seq 单调唯一
        trail = engine.audit_trail("run-a1")
        assert len(trail) == 4
        assert engine.audit_trail("other-run") == ()
        assert all(e.at == _T0 for e in trail)

    def test_audit_sink_exception_swallowed(self) -> None:
        def _boom(event):
            raise RuntimeError("audit bus down")

        engine = _engine(sink=_boom)
        engine.register_template(_template("tpl", [_node("n1")]))
        result = engine.run("tpl")  # 审计路由异常不阻断执行
        assert result.status is RunStatus.SUCCEEDED
        assert engine.audit_trail()  # 引擎内留痕仍在


# ──────────────────────────────────────────────────────────────────────────────
# 因子研究标准模板
# ──────────────────────────────────────────────────────────────────────────────


class TestFactorTemplate:
    def test_factor_research_template_stages(self) -> None:
        log: list[str] = []
        tasks = {
            "factor_mining": _task(log),
            "ic_validation": _task(log),
            "registration": _task(log),
            "canary_release": _task(log),
        }
        template = ResearchTemplate.factor_research(tasks)
        engine = _engine(gate=lambda run_id, node_id: True)
        engine.register_template(template)
        result = engine.run("factor_research")
        assert log == ["factor_mining", "ic_validation", "registration", "canary_release"]
        assert result.status is RunStatus.SUCCEEDED
        canary = template.nodes[-1]
        assert canary.requires_gate is True  # 灰度阶段强制上线门禁

    def test_factor_template_missing_task_raises(self) -> None:
        with pytest.raises(ResearchWorkflowError):
            ResearchTemplate.factor_research({"factor_mining": _task()})
