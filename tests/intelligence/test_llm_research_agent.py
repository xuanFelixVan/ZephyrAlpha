# [BLUEPRINT] MOD-INT-RESEARCH-AGENT | docs/03_modules/_domain_intelligence/llm_research_agent/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-RESEARCH-AGENT | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.intelligence.test_llm_research_agent
# [TESTS] src/zephyr/intelligence/llm_research_agent.py
"""MOD-INT-RESEARCH-AGENT 单元测试：llm_research_agent LLM 研究助手。

蓝图验收（B6-08553/CAND-AISA-017，B6 D-RESEARCH-11）：
规划器（任务→步骤计划）+ 工具白名单（白名单外拒绝）+ ReAct 反思循环
（思考-行动-观察-反思，轮次护栏）+ 记忆写 KB 回调 + 关键数字/标的强制
事实回查（未注入/未过 Fail-Closed）+ 仅辅助研究硬标注 advisory。
规划/思考/反思/回查/KB 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.intelligence.llm_research_agent",
    reason="llm_research_agent not importable",
)

from zephyr.intelligence.llm_research_agent import (  # noqa: E402
    ADVISORY_DISCLAIMER,
    LlmResearchAgent,
    LlmResearchAgentError,
    ResearchReport,
    ResearchStep,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _tools(calls: list | None = None) -> dict:
    def search(q: str) -> str:
        if calls is not None:
            calls.append(("search", q))
        return f"检索结果[{q}]"

    def calc(expr: str) -> str:
        if calls is not None:
            calls.append(("calc", expr))
        return "计算值 12.5%"

    return {"search": search, "calc": calc}


def _step(
    step_id: str = "s1",
    tool: str = "search",
    tool_input: str = "茅台 600519 调研",
    action: str = "检索标的资料",
) -> ResearchStep:
    return ResearchStep(step_id=step_id, action=action, tool=tool, tool_input=tool_input)


def _agent(
    *,
    tools: dict | None = None,
    steps: list | None = None,
    fact_checker=lambda c: True,
    kb_writer=None,
    max_rounds: int = 8,
    thinker=None,
    reflector=None,
) -> LlmResearchAgent:
    return LlmResearchAgent(
        tools=tools if tools is not None else _tools(),
        planner=lambda task: (steps if steps is not None else [_step()]),
        thinker=thinker,
        reflector=reflector,
        fact_checker=fact_checker,
        kb_writer=kb_writer,
        clock=lambda: _T0,
        max_rounds=max_rounds,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 装配校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_tools_raises(self) -> None:
        with pytest.raises(LlmResearchAgentError):
            LlmResearchAgent(tools={}, planner=lambda t: [_step()])

    def test_non_callable_tool_raises(self) -> None:
        with pytest.raises(LlmResearchAgentError):
            LlmResearchAgent(tools={"search": "not-callable"}, planner=lambda t: [_step()])

    def test_non_callable_planner_raises(self) -> None:
        with pytest.raises(LlmResearchAgentError):
            LlmResearchAgent(tools=_tools(), planner="not-callable")

    def test_invalid_max_rounds_raises(self) -> None:
        for bad in (0, -1, True, "8"):
            with pytest.raises(LlmResearchAgentError):
                LlmResearchAgent(tools=_tools(), planner=lambda t: [_step()], max_rounds=bad)


# ──────────────────────────────────────────────────────────────────────────────
# 规划器（任务→步骤计划）
# ──────────────────────────────────────────────────────────────────────────────


class TestPlan:
    def test_plan_ok(self) -> None:
        agent = _agent()
        plan = agent.plan("调研茅台基本面")
        assert plan.plan_id == "plan-0001"
        assert plan.task == "调研茅台基本面"
        assert plan.steps == (_step(),)
        assert plan.created_at == _T0

    def test_plan_id_increments(self) -> None:
        agent = _agent()
        agent.plan("任务一")
        plan2 = agent.plan("任务二")
        assert plan2.plan_id == "plan-0002"
        assert [p.plan_id for p in agent.plans()] == ["plan-0001", "plan-0002"]

    def test_empty_task_raises(self) -> None:
        agent = _agent()
        for bad in ("", "   "):
            with pytest.raises(LlmResearchAgentError):
                agent.plan(bad)

    def test_empty_steps_raises(self) -> None:
        agent = _agent(steps=[])
        with pytest.raises(LlmResearchAgentError):
            agent.plan("空计划任务")

    def test_duplicate_step_id_raises(self) -> None:
        agent = _agent(steps=[_step("s1"), _step("s1")])
        with pytest.raises(LlmResearchAgentError):
            agent.plan("重复步骤任务")

    def test_unknown_tool_rejected(self) -> None:
        agent = _agent(steps=[_step(tool="ghost_tool")])
        with pytest.raises(LlmResearchAgentError):
            agent.plan("白名单外工具任务")


# ──────────────────────────────────────────────────────────────────────────────
# 工具白名单
# ──────────────────────────────────────────────────────────────────────────────


class TestInvokeTool:
    def test_invoke_ok(self) -> None:
        agent = _agent()
        assert agent.invoke_tool("search", "季报") == "检索结果[季报]"

    def test_invoke_result_coerced_str(self) -> None:
        agent = _agent(tools={"num": lambda p: 42})
        assert agent.invoke_tool("num", "x") == "42"

    def test_whitelist_reject(self) -> None:
        agent = _agent()
        with pytest.raises(LlmResearchAgentError):
            agent.invoke_tool("ghost_tool", "x")

    def test_invalid_args_raise(self) -> None:
        agent = _agent()
        with pytest.raises(LlmResearchAgentError):
            agent.invoke_tool("", "x")
        with pytest.raises(LlmResearchAgentError):
            agent.invoke_tool("search", 123)

    def test_tool_exception_wrapped(self) -> None:
        def boom(p: str) -> str:
            raise RuntimeError("db down")

        agent = _agent(tools={"search": boom})
        with pytest.raises(LlmResearchAgentError):
            agent.invoke_tool("search", "x")


# ──────────────────────────────────────────────────────────────────────────────
# ReAct 反思循环 + 事实回查 + KB 写库 + advisory 硬标注
# ──────────────────────────────────────────────────────────────────────────────


class TestRun:
    def test_run_ok_rounds(self) -> None:
        calls: list = []
        agent = _agent(
            tools=_tools(calls),
            steps=[_step("s1"), _step("s2", tool="calc", tool_input="PE 计算", action="计算估值")],
        )
        report = agent.run("调研茅台")
        assert [r.round_no for r in report.rounds] == [1, 2]
        assert report.rounds[0].thought == "思考：准备执行 检索标的资料"
        assert report.rounds[0].observation == "检索结果[茅台 600519 调研]"
        assert "反思" in report.rounds[0].reflection
        assert calls == [("search", "茅台 600519 调研"), ("calc", "PE 计算")]
        assert "检索结果" in report.conclusion and "12.5%" in report.conclusion

    def test_run_advisory_label(self) -> None:
        report = _agent().run("调研茅台")
        assert report.advisory_only is True
        assert report.disclaimer == ADVISORY_DISCLAIMER
        assert "不直连交易" in report.disclaimer

    def test_round_guardrail(self) -> None:
        agent = _agent(steps=[_step("s1"), _step("s2"), _step("s3")], max_rounds=2)
        with pytest.raises(LlmResearchAgentError):
            agent.run("超轮次任务")

    def test_fact_check_records(self) -> None:
        checked: list[str] = []
        agent = _agent(
            steps=[_step("s1"), _step("s2", tool="calc", tool_input="PE 计算")],
            fact_checker=lambda c: checked.append(c) or True,
        )
        report = agent.run("调研茅台")
        assert checked == ["12.5%", "600519"]  # 确定性排序
        assert [fc.claim for fc in report.fact_checks] == ["12.5%", "600519"]
        assert all(fc.passed for fc in report.fact_checks)

    def test_fact_checker_missing_raises(self) -> None:
        agent = LlmResearchAgent(
            tools=_tools(),
            planner=lambda t: [_step()],
            clock=lambda: _T0,
        )
        with pytest.raises(LlmResearchAgentError):
            agent.run("含关键标的任务")  # 观察含 600519，回查器未注入 Fail-Closed

    def test_fact_check_fail_raises(self) -> None:
        agent = _agent(fact_checker=lambda c: False)
        with pytest.raises(LlmResearchAgentError):
            agent.run("调研茅台")

    def test_no_claims_no_checker_ok(self) -> None:
        agent = LlmResearchAgent(
            tools=_tools(),
            planner=lambda t: [_step(tool_input="行业定性调研")],
            clock=lambda: _T0,
        )
        report = agent.run("定性任务")
        assert report.fact_checks == ()
        assert report.conclusion == "检索结果[行业定性调研]"

    def test_kb_writer_called(self) -> None:
        written: list[ResearchReport] = []
        report = _agent(kb_writer=written.append).run("调研茅台")
        assert written == [report]

    def test_kb_writer_exception_swallowed(self) -> None:
        def boom(r: ResearchReport) -> None:
            raise RuntimeError("kb down")

        report = _agent(kb_writer=boom).run("调研茅台")  # 不阻断
        assert report.advisory_only is True

    def test_thinker_reflector_injected(self) -> None:
        agent = _agent(
            thinker=lambda s: f"T:{s.step_id}",
            reflector=lambda s, t, o: f"R:{t}:{len(o)}",
        )
        report = agent.run("调研茅台")
        assert report.rounds[0].thought == "T:s1"
        assert report.rounds[0].reflection.startswith("R:T:s1:")

    def test_determinism(self) -> None:
        r1 = _agent().run("调研茅台")
        r2 = _agent().run("调研茅台")
        assert r1 == r2  # 同输入必同输出
