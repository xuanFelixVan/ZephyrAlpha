# [BLUEPRINT] MOD-MODEL_ROUTER_ORCH | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/11_evidence_skill_router.md | §4.3
# [MODULE] tests.intelligence.model_routing.test_runtime_assembly
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""
test_runtime_assembly.py — 模型路由级联运行时装配单测（11号文 §4.3 Phase 1 收尾）
====================================================================================
CascadeOrchestrator/BudgetEngine/日历/审计落盘全 fake 或 tmp_path，零网络零真 LLM。
覆盖四缝+主链：
- 装配链路：assemble_agent_router 全缝 fake 注入后 route 走通
- dict 契约映射：model/provider/reasons 字段、complexity 枚举化、intraday->trading
- 级联异常降级不阻断：orchestrator 抛异常 route 仍返回，model=None 走门面静态兜底
- cost_ledger 缝：BudgetEngine 台账取值 / 台账异常 0.0 观测降级 / 装配进门面
- audit_sink 缝：16号文统一事件信封 JSONL 落盘字段完整
- period 缝：盘前/竞价/盘中/盘后边界、非交易日、日历异常 fail-closed=trading
- CLI 冒烟：router_factory 注入 dry-run 打印；非法参数 fail-closed
- 懒加载：装配期不构造 CascadeOrchestrator（缺策略文件也不炸），首次 route 才解析
"""

from __future__ import annotations

import json
from datetime import datetime

import pytest

ra = pytest.importorskip("zephyr.intelligence.model_routing.runtime_assembly")
orch_mod = pytest.importorskip("zephyr.intelligence.model_routing.cascade_orchestrator")
lar_mod = pytest.importorskip("zephyr.intelligence.llm_agent_router")
router_mod = pytest.importorskip("zephyr.governance.intelligence_governance.model_router")

CascadeDecision = orch_mod.CascadeDecision
AgentRouterConfig = lar_mod.AgentRouterConfig
RouteRequest = lar_mod.RouteRequest
TaskComplexity = router_mod.TaskComplexity

TASK = "signal_generation"
MODEL = "qwen3:8b"


def _config(budget: float = 10.0) -> AgentRouterConfig:
    return AgentRouterConfig(
        daily_budget_usd=budget,
        period_rules={"task_kinds": {TASK: "local"}},
    )


class _FakeOrchestrator:
    """duck-typed .route：记录调用参数，返回固定 CascadeDecision 或抛异常。"""

    def __init__(self, decision=None, exc=None):
        self._decision = decision
        self._exc = exc
        self.calls: list[dict] = []

    def route(self, task_type, candidates, *, complexity, period=None, required_capabilities=None):
        self.calls.append(
            {
                "task_type": task_type,
                "candidates": list(candidates),
                "complexity": complexity,
                "period": period,
                "required_capabilities": required_capabilities,
            }
        )
        if self._exc is not None:
            raise self._exc
        return self._decision


def _decision(**over) -> CascadeDecision:
    base = {
        "task_type": TASK,
        "model_key": MODEL,
        "provider": "ollama",
        "tier": "UNTIERED",
        "reason": "local-first|l2:fused|fake",
    }
    base.update(over)
    return CascadeDecision(**base)


def _period_req(**over) -> RouteRequest:
    base = {"task_type": TASK, "candidates": [MODEL], "period": "post_close"}
    base.update(over)
    return RouteRequest(**base)


# ── 装配链路 + dict 契约映射 ──


class TestAssembleChain:
    def test_route_through_assembled_router(self):
        orch = _FakeOrchestrator(decision=_decision())
        audits = []
        router = ra.assemble_agent_router(
            _config(),
            orchestrator=orch,
            cost_ledger=lambda: 1.25,
            audit_sink=audits.append,
        )
        dec = router.route(_period_req())
        assert dec.selected_model == MODEL
        assert dec.provider == "ollama"
        assert any("local-first" in r for r in dec.reasons)
        assert len(orch.calls) == 1
        assert len(audits) == 1  # audit_sink 被门面调用

    def test_dict_contract_field_mapping(self):
        orch = _FakeOrchestrator(
            decision=_decision(
                alerts=["L1 全部候选无护照，降级为不过滤（静态映射兜底上游）"],
                degraded_stages=["L1"],
            )
        )
        engine = ra.cascade_decision_engine(orch)
        out = engine(_period_req(complexity="complex"))
        assert out["model"] == MODEL
        assert out["provider"] == "ollama"
        assert out["reasons"][0] == "local-first|l2:fused|fake"
        assert any("无护照" in r for r in out["reasons"])
        assert any(r == "degraded_stages:L1" for r in out["reasons"])
        # complexity 字符串 -> 枚举；period 原样透传（post_close 本是级联词表）
        assert orch.calls[0]["complexity"] is TaskComplexity.COMPLEX
        assert orch.calls[0]["period"] == "post_close"

    def test_unknown_complexity_falls_back_moderate(self):
        orch = _FakeOrchestrator(decision=_decision())
        ra.cascade_decision_engine(orch)(_period_req(complexity="bogus"))
        assert orch.calls[0]["complexity"] is TaskComplexity.MODERATE

    def test_facade_intraday_mapped_to_cascade_trading(self):
        orch = _FakeOrchestrator(decision=_decision())
        ra.cascade_decision_engine(orch)(_period_req(period="intraday"))
        assert orch.calls[0]["period"] == "trading"

    def test_risk_locked_reason_tagged(self):
        orch = _FakeOrchestrator(
            decision=_decision(source="risk_locked", risk_locked=True, model_key="deepseek:pro", provider="deepseek")
        )
        out = ra.cascade_decision_engine(orch)(_period_req(task_type="risk_diagnosis"))
        assert out["model"] == "deepseek:pro"
        assert any("HB-09" in r for r in out["reasons"])


# ── 级联异常降级不阻断 ──


class TestCascadeExceptionDegrades:
    def test_engine_returns_model_none_on_exception(self):
        engine = ra.cascade_decision_engine(_FakeOrchestrator(exc=RuntimeError("boom")))
        out = engine(_period_req())
        assert out["model"] is None
        assert any("级联异常降级" in r for r in out["reasons"])

    def test_route_not_blocked_and_static_fallback(self):
        router = ra.assemble_agent_router(
            _config(),
            orchestrator=_FakeOrchestrator(exc=RuntimeError("boom")),
            cost_ledger=lambda: 0.0,
            audit_sink=lambda rec: None,
        )
        dec = router.route(_period_req())
        assert dec.selected_model is None  # 门面既有静态兜底路径（decision_engine 缺省同径）
        assert any("级联异常降级" in r for r in dec.reasons)

    def test_lazy_orchestrator_construction_failure_degrades(self, tmp_path):
        # 装配期不构造 orchestrator：缺策略文件也不炸；首次 route 才解析并降级
        router = ra.assemble_agent_router(
            _config(),
            policy_path=tmp_path / "missing_policy.yaml",
            cost_ledger=lambda: 0.0,
            audit_sink=lambda rec: None,
        )
        dec = router.route(_period_req())
        assert dec.selected_model is None
        assert any("级联异常降级" in r for r in dec.reasons)


# ── cost_ledger 缝 ──


class TestCostLedger:
    class _FakeBudgetEngine:
        def __init__(self, summary=None, exc=None):
            self._summary = summary
            self._exc = exc

        def get_consumption_summary(self):
            if self._exc is not None:
                raise self._exc
            return self._summary

    def test_reads_cost_policy_daily(self):
        eng = self._FakeBudgetEngine({"BP-COST-001": {"daily": 7.5, "hourly": 1.0}})
        assert ra.budget_cost_ledger(eng)() == 7.5

    def test_missing_policy_returns_zero(self):
        assert ra.budget_cost_ledger(self._FakeBudgetEngine({}))() == 0.0

    def test_engine_exception_degrades_to_zero(self):
        ledger = ra.budget_cost_ledger(self._FakeBudgetEngine(exc=RuntimeError("db down")))
        assert ledger() == 0.0  # 观测降级不阻断

    def test_assembled_router_holds_ledger(self):
        router = ra.assemble_agent_router(
            _config(),
            orchestrator=_FakeOrchestrator(decision=_decision()),
            cost_ledger=lambda: 42.0,
            audit_sink=lambda rec: None,
        )
        assert router._cost_ledger() == 42.0


# ── audit_sink 缝 ──


class TestAuditSink:
    def test_jsonl_unified_event_envelope(self, tmp_path):
        path = tmp_path / "audit" / "agent_router_audit.jsonl"
        router = ra.assemble_agent_router(
            _config(),
            orchestrator=_FakeOrchestrator(decision=_decision()),
            cost_ledger=lambda: 0.0,
            audit_sink=ra.jsonl_audit_sink(path),
        )
        router.route(_period_req())
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["schema_version"] == ra.AUDIT_SCHEMA_VERSION
        assert event["event_id"]
        assert event["ts"]
        assert event["source"] == "llm_agent_router"
        assert event["event_type"] == "agent_route_decision"
        payload = event["payload"]
        assert payload["decision"]["task_type"] == TASK
        assert payload["decision"]["selected_model"] == MODEL
        assert payload["period"] == "post_close"

    def test_append_only_two_routes_two_lines(self, tmp_path):
        path = tmp_path / "audit.jsonl"
        sink = ra.jsonl_audit_sink(path)
        router = ra.assemble_agent_router(
            _config(),
            orchestrator=_FakeOrchestrator(decision=_decision()),
            cost_ledger=lambda: 0.0,
            audit_sink=sink,
        )
        router.route(_period_req())
        router.route(_period_req())
        assert len(path.read_text(encoding="utf-8").strip().splitlines()) == 2


# ── period 缝：data/calendar 交易时段真源 ──


class TestTradingPeriod:
    class _FakeCalendar:
        def __init__(self, trading=True, exc=None):
            self._trading = trading
            self._exc = exc

        def is_trading_day(self, day=None):
            if self._exc is not None:
                raise self._exc
            return self._trading

    @pytest.mark.parametrize(
        ("hour", "minute", "expected"),
        [
            (8, 30, "pre_open"),  # 盘前
            (9, 14, "pre_open"),
            (9, 15, "call_auction"),  # 集合竞价 [9:15, 9:30)
            (9, 29, "call_auction"),
            (9, 30, "trading"),  # 盘中 [9:30, 15:00)
            (14, 59, "trading"),
            (15, 0, "post_close"),  # 盘后
            (23, 0, "post_close"),
        ],
    )
    def test_period_boundaries(self, hour, minute, expected):
        now = datetime(2026, 8, 28, hour, minute)  # naive -> 按 Asia/Shanghai 解释
        cal = self._FakeCalendar(trading=True)
        assert ra.current_trading_period(now, calendar=cal) == expected

    def test_non_trading_day_is_post_close(self):
        now = datetime(2026, 8, 28, 10, 0)
        assert ra.current_trading_period(now, calendar=self._FakeCalendar(trading=False)) == "post_close"

    def test_calendar_exception_fail_closed_trading(self):
        now = datetime(2026, 8, 28, 8, 30)  # 墙钟盘前，但日历故障 -> 最严时段
        cal = self._FakeCalendar(exc=RuntimeError("calendar io error"))
        assert ra.current_trading_period(now, calendar=cal) == "trading"


# ── CLI 冒烟 ──


class TestCliSmoke:
    def test_dry_run_prints_decision(self, capsys):
        class _FakeRouter:
            def __init__(self, sink):
                self._sink = sink

            def route(self, request):
                decision = lar_mod.AgentRouteDecision(
                    task_type=request.task_type,
                    selected_model=MODEL,
                    provider="ollama",
                    source="agent_router",
                    degraded_to_local=False,
                    reasons=("fake",),
                    latency_violations=(),
                )
                self._sink(
                    lar_mod.RouteAuditRecord(
                        request_fingerprint=f"{request.task_type}:{request.period}",
                        classification=lar_mod.TaskClassification(
                            task_type=request.task_type, kind="local", local_pref=True, reason="rules"
                        ),
                        decision=decision,
                        daily_cost_before=0.0,
                        daily_cost_after=0.0,
                        period=request.period,
                    )
                )
                return decision

        rc = ra.main(
            ["--task-type", TASK, "--candidates", MODEL, "--period", "post_close"],
            router_factory=lambda **kw: _FakeRouter(kw["audit_sink"]),
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert '"selected_model": "qwen3:8b"' in out
        assert "audit:" in out  # dry-run 审计打印到 stdout 不落盘

    def test_empty_candidates_fail_closed(self):
        with pytest.raises(ValueError):
            ra.main(["--task-type", TASK, "--candidates", ""], router_factory=lambda **kw: None)


# ── task_gate 缝：06号文 §2.1 dispatch 硬门（opt-in，默认关闭零行为变化）──


class TestTaskGateWiring:
    def test_assemble_default_task_gate_off(self):
        router = ra.assemble_agent_router(
            _config(),
            orchestrator=_FakeOrchestrator(decision=_decision()),
            cost_ledger=lambda: 0.0,
            audit_sink=lambda rec: None,
        )
        assert router._task_gate is None  # 默认不启用

    def test_assemble_task_gate_callable_injected(self):
        orch = _FakeOrchestrator(decision=_decision())
        calls = []

        def fake_gate(model_id, capability):
            calls.append((model_id, capability))
            return (False, "low_accuracy: x")

        router = ra.assemble_agent_router(
            _config(),
            orchestrator=orch,
            cost_ledger=lambda: 0.0,
            audit_sink=lambda rec: None,
            task_gate=fake_gate,
        )
        dec = router.route(_period_req())
        assert dec.selected_model is None  # 唯一候选被拦截 -> 阻断标记
        assert calls == [(MODEL, TASK)]
        assert any("task_gate" in r for r in dec.reasons)

    def test_assemble_task_gate_true_wires_lazy_hook(self):
        router = ra.assemble_agent_router(
            _config(),
            orchestrator=_FakeOrchestrator(decision=_decision()),
            cost_ledger=lambda: 0.0,
            audit_sink=lambda rec: None,
            task_gate=True,
        )
        assert callable(router._task_gate)  # 懒构造：首次调用才建 TaskGate/调度器

    def test_dispatch_hook_delegates_to_scheduler_check_and_record(self):
        class _FakeGate:
            def can_dispatch(self, model_id, capability):
                return (False, "low_accuracy: x")

        class _FakeScheduler:
            def __init__(self):
                self.calls = []

            def check_and_record(self, gate, model_id, capability):
                self.calls.append((gate, model_id, capability))
                return gate.can_dispatch(model_id, capability)

        gate = _FakeGate()
        sched = _FakeScheduler()
        hook = ra.task_gate_dispatch_hook(gate=gate, scheduler=sched)
        assert hook(MODEL, "code_fix") == (False, "low_accuracy: x")
        assert sched.calls == [(gate, MODEL, "code_fix")]  # 登记拦截计数经调度器

    def test_dispatch_hook_exception_fail_closed(self):
        class _BadScheduler:
            def check_and_record(self, gate, model_id, capability):
                raise RuntimeError("scheduler down")

        hook = ra.task_gate_dispatch_hook(gate=object(), scheduler=_BadScheduler())
        allowed, reason = hook("m", "c")
        assert allowed is False  # 钩子异常 fail-closed 按拦截处理，不抛出
        assert "task_gate 异常" in reason
