# AI-generated: T-3-22 (A27) Eval Harness · AI 能力基准测试集（30 用例）
"""
EvalHarness · AI 能力基准测试集（30 个用例）
============================================

Task ID     : T-3-22 (A27)
依赖        : T-3-10 ✅(A22 agent_orchestrator) + T-3-07(HallucinationDetector) +
              T-3-14(EvolutionEngine) + T-3-20(IntentParser)
safety_level: H

模块职责
--------

提供一个 **可离线运行、零外部 LLM 依赖** 的评估框架，
对 Phase 3 四大能力各自出 10/10/5/5 个用例共 30 条：

- 10 条 意图解析（keyword / embedding / LLM 三阶段）
- 10 条 Agent 编排（capability_match / load_balance / specialist_first /
  fallback_chain + directive 链成功/失败 + Health Monitor）
- 5 条  幻觉检测（CoVe 通过 / CoVe 冲突 / single_model / keyword 兜底 /
  L3 黑名单）
- 5 条  进化引擎（L1 low-score / L2 pattern / L3 drift / dry_run /
  owner_approved）

每个用例通用契约
----------------

.. code-block:: python

    @dataclass
    class EvalCase:
        case_id: str
        category: str  # intent | orchestrator | hallucination | evolution
        description: str
        runner: Callable[[], EvalOutcome]

    @dataclass
    class EvalOutcome:
        passed: bool
        expected: Any
        actual: Any
        latency_ms: int
        error: str | None = None

汇总 report
-----------

.. code-block:: python

    @dataclass
    class EvalReport:
        total: int
        passed: int
        failed: int
        pass_rate: float
        avg_latency_ms: float
        error_breakdown: dict[str, int]
        by_category: dict[str, CategoryStat]
        cases: list[EvalResult]

使用示例
--------

::

    harness = EvalHarness.build_default()
    report = harness.run_all()
    print(harness.to_json(report))

零外部依赖
----------

- 不调用任何真实 LLM；所有 caller 为纯函数 stub，保持确定性。
- 不落盘；如需持久化，外层调用方自行 `harness.to_json(report)` 写入。
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from zephyr.orchestrator.agent_orchestrator import (
    AgentOrchestrator,
    AgentProfile,
    AgentRole,
    AgentRouter,
    HallucinationCaller,
    HealthMonitor,
    RoutingStrategy,
    ToolInvoker,
)
from zephyr.feedback_loop.evolution_engine import (
    EvolutionEngine,
    EvolutionProposal,
    EvolutionSignal,
    FeedbackLayer,
    evolve,
)
from zephyr.feedback_loop.feedback_collector import FeedbackCollector
from zephyr.orchestrator.hallucination_detector import (
    FallbackMode,
    HallucinationDetector,
    ModelCallResult,
    RiskLevel,
    TriggerLevel,
)
from zephyr.context_engine.intent_keyword_mapper import IntentKeywordMapper
from zephyr.context_engine.intent_parser import (
    EmbeddingHit,
    IntentParser,
    LLMIntentVerdict,
)

__all__ = [
    "EvalCase",
    "EvalOutcome",
    "EvalResult",
    "CategoryStat",
    "EvalReport",
    "EvalHarness",
    "build_intent_cases",
    "build_orchestrator_cases",
    "build_hallucination_cases",
    "build_evolution_cases",
]


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


CATEGORY_INTENT = "intent"
CATEGORY_ORCHESTRATOR = "orchestrator"
CATEGORY_HALLUCINATION = "hallucination"
CATEGORY_EVOLUTION = "evolution"

CATEGORIES: tuple[str, ...] = (
    CATEGORY_INTENT,
    CATEGORY_ORCHESTRATOR,
    CATEGORY_HALLUCINATION,
    CATEGORY_EVOLUTION,
)


@dataclass
class EvalOutcome:
    """单个 runner 的输出。"""

    passed: bool
    expected: Any
    actual: Any
    error: Optional[str] = None


@dataclass
class EvalCase:
    """单个评估用例。runner 在 EvalHarness 内部被调用。"""

    case_id: str
    category: str
    description: str
    runner: Callable[[], EvalOutcome]


@dataclass
class EvalResult:
    """单个用例的完整结果（含耗时）。"""

    case_id: str
    category: str
    description: str
    passed: bool
    expected: Any
    actual: Any
    latency_ms: int
    error: Optional[str] = None


@dataclass
class CategoryStat:
    """按类别的统计。"""

    total: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0
    avg_latency_ms: float = 0.0


@dataclass
class EvalReport:
    """一次 run_all 的汇总报告。"""

    total: int
    passed: int
    failed: int
    pass_rate: float
    avg_latency_ms: float
    error_breakdown: dict[str, int] = field(default_factory=dict)
    by_category: dict[str, CategoryStat] = field(default_factory=dict)
    cases: list[EvalResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------


def _outcome(
    *,
    expected: Any,
    actual: Any,
    error: Optional[str] = None,
) -> EvalOutcome:
    """若 error 非空则 passed=False；否则根据 expected == actual 判定。"""
    if error is not None:
        return EvalOutcome(passed=False, expected=expected, actual=actual, error=error)
    return EvalOutcome(
        passed=bool(expected == actual), expected=expected, actual=actual
    )


# ---------------------------------------------------------------------------
# 意图解析：10 用例
# ---------------------------------------------------------------------------


def _empty_keyword_mapper() -> IntentKeywordMapper:
    """用于强制走 Stage 2/3 的空关键词字典。"""
    return IntentKeywordMapper(keywords={"D0": ["__nope__"]})


def _build_stub_emb(hits: list[EmbeddingHit]) -> Callable[..., list[EmbeddingHit]]:
    def _emb(query: str, top_k: int = 5) -> list[EmbeddingHit]:  # noqa: ARG001
        return list(hits[:top_k])

    return _emb


def _build_stub_llm(verdict: LLMIntentVerdict) -> Callable[..., LLMIntentVerdict]:
    def _llm(query: str, context: Optional[dict[str, Any]] = None) -> LLMIntentVerdict:  # noqa: ARG001
        return verdict

    return _llm


def build_intent_cases() -> list[EvalCase]:
    """10 个意图解析评估用例（keyword / embedding / LLM 三阶段）。"""
    cases: list[EvalCase] = []

    # ---- keyword 强命中：D0 治理域 ----
    def case_i01() -> EvalOutcome:
        parser = IntentParser()
        r = parser.parse(
            "meta session handoff log status init bootstrap startup overview dashboard"
        )
        return _outcome(expected="D0", actual=r.primary_domain)

    cases.append(EvalCase("IE-I-01", CATEGORY_INTENT, "keyword high-confidence → D0", case_i01))

    # ---- keyword 强命中：D3 因子域 ----
    def case_i02() -> EvalOutcome:
        parser = IntentParser()
        r = parser.parse(
            "factor alpha signal indicator momentum volatility volume price return sharpe"
        )
        return _outcome(expected="D3", actual=r.primary_domain)

    cases.append(EvalCase("IE-I-02", CATEGORY_INTENT, "keyword high-confidence → D3", case_i02))

    # ---- keyword 强命中：D6 治理审计 ----
    def case_i03() -> EvalOutcome:
        parser = IntentParser()
        r = parser.parse(
            "governance audit compliance standard policy rule sentinel scan violation contradiction"
        )
        return _outcome(expected="D6", actual=r.primary_domain)

    cases.append(EvalCase("IE-I-03", CATEGORY_INTENT, "keyword high-confidence → D6", case_i03))

    # ---- keyword 命中但非独占 → source_stage 仍是 keyword 或 semantic ----
    def case_i04() -> EvalOutcome:
        parser = IntentParser()
        r = parser.parse("risk drawdown var cvar margin hedge scenario exposure")
        return _outcome(expected="D5", actual=r.primary_domain)

    cases.append(EvalCase("IE-I-04", CATEGORY_INTENT, "keyword D5 risk domain", case_i04))

    # ---- embedding 接管（Stage 1 低置信） ----
    def case_i05() -> EvalOutcome:
        parser = IntentParser(
            embedding_searcher=_build_stub_emb(
                [
                    EmbeddingHit(domain="D3", score=0.95, text="factor"),
                    EmbeddingHit(domain="D3", score=0.85, text="alpha"),
                ]
            ),
        )
        r = parser.parse("xyz 因子研究 随机短语")
        return _outcome(expected="semantic", actual=r.source_stage)

    cases.append(
        EvalCase("IE-I-05", CATEGORY_INTENT, "semantic stage accepts D3", case_i05)
    )

    # ---- embedding 返回空 → LLM 接管 ----
    def case_i06() -> EvalOutcome:
        parser = IntentParser(
            keyword_mapper=_empty_keyword_mapper(),
            embedding_searcher=_build_stub_emb([]),
            llm_caller=_build_stub_llm(
                LLMIntentVerdict(primary_domain="D7", confidence=0.8, rationale="llm")
            ),
        )
        r = parser.parse("完全无法识别的随机文本 abc")
        return _outcome(expected="llm", actual=r.source_stage)

    cases.append(
        EvalCase("IE-I-06", CATEGORY_INTENT, "empty embedding → llm fallback", case_i06)
    )

    # ---- LLM 低置信 → requires_human=True ----
    def case_i07() -> EvalOutcome:
        parser = IntentParser(
            keyword_mapper=_empty_keyword_mapper(),
            llm_caller=_build_stub_llm(
                LLMIntentVerdict(
                    primary_domain="UNKNOWN", confidence=0.1, rationale="unsure"
                )
            ),
        )
        r = parser.parse("abc def")
        return _outcome(expected=True, actual=r.requires_human)

    cases.append(
        EvalCase("IE-I-07", CATEGORY_INTENT, "llm low-confidence → requires_human", case_i07)
    )

    # ---- 三阶段均不可用（不注入 embedding/llm）→ 兜底 requires_human ----
    def case_i08() -> EvalOutcome:
        parser = IntentParser(keyword_mapper=_empty_keyword_mapper())
        r = parser.parse("完全未登记的关键词")
        return _outcome(expected=True, actual=r.requires_human)

    cases.append(
        EvalCase("IE-I-08", CATEGORY_INTENT, "no stage available → human review", case_i08)
    )

    # ---- embedding 聚合后 confidence 低于阈值 → 走 LLM ----
    def case_i09() -> EvalOutcome:
        parser = IntentParser(
            keyword_mapper=_empty_keyword_mapper(),
            embedding_searcher=_build_stub_emb(
                [
                    EmbeddingHit(domain="D6", score=0.20),
                    EmbeddingHit(domain="D2", score=0.18),
                    EmbeddingHit(domain="D0", score=0.17),
                    EmbeddingHit(domain="D1", score=0.16),
                    EmbeddingHit(domain="D3", score=0.15),
                ]
            ),
            llm_caller=_build_stub_llm(
                LLMIntentVerdict(primary_domain="D6", confidence=0.6, rationale="llm")
            ),
        )
        r = parser.parse("some ambiguous sentence")
        return _outcome(expected="llm", actual=r.source_stage)

    cases.append(
        EvalCase("IE-I-09", CATEGORY_INTENT, "semantic below threshold → llm", case_i09)
    )

    # ---- Stage 1 命中 UNKNOWN（空 query）→ 兜底 human review ----
    def case_i10() -> EvalOutcome:
        parser = IntentParser()
        r = parser.parse("")
        # 空 query：primary_domain = UNKNOWN，requires_human=True
        return _outcome(expected="UNKNOWN", actual=r.primary_domain)

    cases.append(
        EvalCase("IE-I-10", CATEGORY_INTENT, "empty query → UNKNOWN", case_i10)
    )

    return cases


# ---------------------------------------------------------------------------
# Agent 编排：10 用例
# ---------------------------------------------------------------------------


def _ok_invoker(
    log: Optional[list[tuple[str, dict[str, Any]]]] = None,
) -> ToolInvoker:
    def _invoke(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if log is not None:
            log.append((tool_name, arguments))
        return {"ok": True, "tool": tool_name}

    return _invoke


def _fail_invoker(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG001
    raise RuntimeError("invoker failure")


def _hallu_hallu(
    claim: str,  # noqa: ARG001
    context: Optional[dict[str, Any]] = None,  # noqa: ARG001
) -> dict[str, Any]:
    return {"is_hallucination": True, "confidence": 0.2}


_HALLU_CALLER_HALLU: HallucinationCaller = _hallu_hallu
_FAIL_INVOKER: ToolInvoker = _fail_invoker


def build_orchestrator_cases() -> list[EvalCase]:
    """10 个 Agent 编排用例。"""
    cases: list[EvalCase] = []
    mapping: dict[str, list[tuple[str, dict[str, Any]]]] = {
        "325": [("task_manager.get_task", {"task_id": "T-EV"})],
        "344": [("knowledge_base.search", {"q": "eval"})],
        "999": [("sentinel.run_scan", {})],
    }

    # ---- 路由：D6 → GOVERNOR ----
    def case_o01() -> EvalOutcome:
        dec = AgentRouter().route("D6")
        return _outcome(expected=AgentRole.GOVERNOR, actual=dec.primary_role)

    cases.append(
        EvalCase("IE-O-01", CATEGORY_ORCHESTRATOR, "capability_match D6 → GOVERNOR", case_o01)
    )

    # ---- 路由：D3 → RESEARCHER ----
    def case_o02() -> EvalOutcome:
        dec = AgentRouter().route("D3")
        return _outcome(expected=AgentRole.RESEARCHER, actual=dec.primary_role)

    cases.append(
        EvalCase("IE-O-02", CATEGORY_ORCHESTRATOR, "capability_match D3 → RESEARCHER", case_o02)
    )

    # ---- 路由：D9 → IMPLEMENTER ----
    def case_o03() -> EvalOutcome:
        dec = AgentRouter().route("D9")
        return _outcome(expected=AgentRole.IMPLEMENTER, actual=dec.primary_role)

    cases.append(
        EvalCase("IE-O-03", CATEGORY_ORCHESTRATOR, "capability_match D9 → IMPLEMENTER", case_o03)
    )

    # ---- load_balance：两个 researcher，取低负载 ----
    def case_o04() -> EvalOutcome:
        router = AgentRouter()
        router.register(
            AgentProfile(agent_id="R1", role=AgentRole.RESEARCHER, current_load=5, max_load=5)
        )
        router.register(
            AgentProfile(agent_id="R2", role=AgentRole.RESEARCHER, current_load=0, max_load=5)
        )
        dec = router.route("D3", strategy=RoutingStrategy.LOAD_BALANCE)
        return _outcome(expected="R2", actual=dec.primary_agent_id)

    cases.append(
        EvalCase("IE-O-04", CATEGORY_ORCHESTRATOR, "load_balance picks low-load", case_o04)
    )

    # ---- specialist_first：强制 GOVERNOR ----
    def case_o05() -> EvalOutcome:
        dec = AgentRouter().route(
            "D0",
            strategy=RoutingStrategy.SPECIALIST_FIRST,
            required_role=AgentRole.GOVERNOR,
        )
        return _outcome(expected=AgentRole.GOVERNOR, actual=dec.primary_role)

    cases.append(
        EvalCase("IE-O-05", CATEGORY_ORCHESTRATOR, "specialist_first GOVERNOR", case_o05)
    )

    # ---- fallback_chain：6 角色全覆盖 ----
    def case_o06() -> EvalOutcome:
        dec = AgentRouter().route("D2", strategy=RoutingStrategy.FALLBACK_CHAIN)
        roles = {dec.primary_role, *dec.fallback_roles}
        return _outcome(expected=6, actual=len(roles))

    cases.append(
        EvalCase("IE-O-06", CATEGORY_ORCHESTRATOR, "fallback_chain covers 6 roles", case_o06)
    )

    # ---- orchestrate：directive 链成功 ----
    def case_o07() -> EvalOutcome:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker(),
            directive_mapping=mapping,
        )
        res = orch.orchestrate(domain="D6", directive_chain="325+344")
        return _outcome(expected=True, actual=res.success)

    cases.append(
        EvalCase("IE-O-07", CATEGORY_ORCHESTRATOR, "orchestrate success chain", case_o07)
    )

    # ---- orchestrate：directive 未注册 → 失败 ----
    def case_o08() -> EvalOutcome:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker(),
            directive_mapping=mapping,
        )
        res = orch.orchestrate(domain="D0", directive_chain="111")
        return _outcome(expected=False, actual=res.success)

    cases.append(
        EvalCase("IE-O-08", CATEGORY_ORCHESTRATOR, "unmapped directive → failure", case_o08)
    )

    # ---- orchestrate + CoVe post-hook 判幻觉 → success=False ----
    def case_o09() -> EvalOutcome:
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_ok_invoker(),
            hallucination_caller=_HALLU_CALLER_HALLU,
            directive_mapping=mapping,
        )
        res = orch.orchestrate(
            domain="D0", directive_chain="325", claim="bogus claim"
        )
        return _outcome(expected=False, actual=res.success)

    cases.append(
        EvalCase("IE-O-09", CATEGORY_ORCHESTRATOR, "cove post-hook hallucination fails", case_o09)
    )

    # ---- HealthMonitor：多次 record 后 error_rate 合法 ----
    def case_o10() -> EvalOutcome:
        mon = HealthMonitor(window_size=5)
        orch = AgentOrchestrator(
            AgentRouter(),
            tool_invoker=_FAIL_INVOKER,
            directive_mapping=mapping,
            monitor=mon,
        )
        for _ in range(3):
            orch.orchestrate(domain="D0", directive_chain="325")
        snap = mon.snapshot()
        return _outcome(expected=True, actual=snap.error_rate > 0.0)

    cases.append(
        EvalCase("IE-O-10", CATEGORY_ORCHESTRATOR, "health monitor error_rate > 0", case_o10)
    )

    return cases


# ---------------------------------------------------------------------------
# 幻觉检测：5 用例
# ---------------------------------------------------------------------------


def _primary_ok(prompt: str, *, purpose: str) -> ModelCallResult:  # noqa: ARG001
    payload = {
        "baseline_answer": "因子 IC 约为 0.05",
        "verify_questions": ["IC 是否正常", "是否超范围", "样本是否够"],
    }
    return ModelCallResult(
        content=json.dumps(payload, ensure_ascii=False), cost_usd=0.005, success=True
    )


def _verifier_consistent(prompt: str, *, purpose: str) -> ModelCallResult:  # noqa: ARG001
    answers = [
        {"question": "IC 是否正常", "answer": "因子 IC 约为 0.05 正常", "confidence_self": 0.85},
        {"question": "是否超范围", "answer": "IC 约 0.05 不超范围", "confidence_self": 0.8},
        {"question": "样本是否够", "answer": "样本覆盖 IC 0.05 的估计足够", "confidence_self": 0.8},
    ]
    return ModelCallResult(content=json.dumps(answers), cost_usd=0.004, success=True)


def _verifier_conflicting(prompt: str, *, purpose: str) -> ModelCallResult:  # noqa: ARG001
    answers = [
        {"question": "q", "answer": "不是，不正常", "confidence_self": 0.9},
        {"question": "q", "answer": "不对，超范围", "confidence_self": 0.9},
        {"question": "q", "answer": "wrong, not enough", "confidence_self": 0.9},
    ]
    return ModelCallResult(content=json.dumps(answers), cost_usd=0.004, success=True)


def build_hallucination_cases() -> list[EvalCase]:
    """5 个幻觉检测用例。"""
    cases: list[EvalCase] = []

    # ---- CoVe 双模型一致 → 非幻觉 ----
    def case_h01() -> EvalOutcome:
        det = HallucinationDetector(
            primary_caller=_primary_ok, verifier_caller=_verifier_consistent
        )
        r = det.detect("因子 IC 约为 0.05", risk_level=RiskLevel.M)
        return _outcome(expected=False, actual=r.is_hallucination)

    cases.append(EvalCase("IE-H-01", CATEGORY_HALLUCINATION, "CoVe consistent", case_h01))

    # ---- CoVe 双模型冲突 → 判幻觉 ----
    def case_h02() -> EvalOutcome:
        det = HallucinationDetector(
            primary_caller=_primary_ok, verifier_caller=_verifier_conflicting
        )
        r = det.detect("因子 IC 约为 0.05", risk_level=RiskLevel.M)
        return _outcome(expected=True, actual=r.is_hallucination)

    cases.append(EvalCase("IE-H-02", CATEGORY_HALLUCINATION, "CoVe conflict", case_h02))

    # ---- 单模型降级 ----
    def case_h03() -> EvalOutcome:
        det = HallucinationDetector(primary_caller=_primary_ok, verifier_caller=None)
        r = det.detect("因子 IC 约为 0.05", risk_level=RiskLevel.L)
        return _outcome(expected=FallbackMode.SINGLE_MODEL.value, actual=r.fallback_used)

    cases.append(
        EvalCase("IE-H-03", CATEGORY_HALLUCINATION, "single_model fallback", case_h03)
    )

    # ---- keyword 兜底：数值越界 → 判幻觉 ----
    def case_h04() -> EvalOutcome:
        det = HallucinationDetector()
        r = det.detect("IC = 3.5 is great", risk_level=RiskLevel.M)
        return _outcome(expected=True, actual=r.is_hallucination)

    cases.append(EvalCase("IE-H-04", CATEGORY_HALLUCINATION, "keyword numeric outlier", case_h04))

    # ---- L3 黑名单：triggered=False ----
    def case_h05() -> EvalOutcome:
        det = HallucinationDetector()
        r = det.detect(
            "纯代码补全", risk_level=RiskLevel.L, trigger_level=TriggerLevel.L3_BLACKLIST
        )
        return _outcome(expected=False, actual=r.triggered)

    cases.append(EvalCase("IE-H-05", CATEGORY_HALLUCINATION, "L3 blacklist skip", case_h05))

    return cases


# ---------------------------------------------------------------------------
# 进化引擎：5 用例
# ---------------------------------------------------------------------------


def build_evolution_cases() -> list[EvalCase]:
    """5 个进化引擎用例。"""
    cases: list[EvalCase] = []

    # ---- L1：低分触发 acceptance_drift 提案 ----
    def case_e01() -> EvalOutcome:
        collector = FeedbackCollector()
        collector.add(task_id="T-1", score=1)
        collector.add(task_id="T-2", score=2)
        engine = EvolutionEngine(collector)
        report = engine.evolve()
        triggered = any(
            p.signal == EvolutionSignal.ACCEPTANCE_DRIFT
            and p.layer == FeedbackLayer.L1_TASK
            for p in report.proposals
        )
        return _outcome(expected=True, actual=triggered)

    cases.append(EvalCase("IE-E-01", CATEGORY_EVOLUTION, "L1 low-score signal", case_e01))

    # ---- L2：pattern 聚合 → high_retry_rate ----
    def case_e02() -> EvalOutcome:
        collector = FeedbackCollector()
        for i in range(4):
            collector.add(task_id=f"T-{i}", score=3, tags=["retry"])
        engine = EvolutionEngine(collector)
        report = engine.evolve()
        triggered = any(
            p.signal == EvolutionSignal.HIGH_RETRY_RATE for p in report.proposals
        )
        return _outcome(expected=True, actual=triggered)

    cases.append(EvalCase("IE-E-02", CATEGORY_EVOLUTION, "L2 pattern retry", case_e02))

    # ---- L3：MoM drift 触发 ----
    def case_e03() -> EvalOutcome:
        collector = FeedbackCollector()
        for i in range(10):
            collector.add(task_id=f"T-{i}", score=3)
        engine = EvolutionEngine(collector)
        report = engine.evolve(baseline_avg_score=4.0)
        return _outcome(expected=True, actual=report.l3_triggered >= 1)

    cases.append(EvalCase("IE-E-03", CATEGORY_EVOLUTION, "L3 MoM drift", case_e03))

    # ---- dry_run 不 apply ----
    def case_e04() -> EvalOutcome:
        collector = FeedbackCollector()
        collector.add(task_id="T-X", score=1)
        called: list[str] = []

        def apply_fn(p: EvolutionProposal) -> bool:
            called.append(p.proposal_id)
            return True

        report = evolve(
            collector, dry_run=True, owner_approved=True, apply_fn=apply_fn
        )
        return _outcome(expected=0, actual=report.applied_count + len(called))

    cases.append(EvalCase("IE-E-04", CATEGORY_EVOLUTION, "dry_run does not apply", case_e04))

    # ---- 真实 apply 需 owner_approved ----
    def case_e05() -> EvalOutcome:
        collector = FeedbackCollector()
        collector.add(task_id="T-X", score=1)

        def apply_fn(_p: EvolutionProposal) -> bool:
            return True

        report = evolve(
            collector, dry_run=False, owner_approved=True, apply_fn=apply_fn
        )
        return _outcome(expected=True, actual=report.applied_count >= 1)

    cases.append(EvalCase("IE-E-05", CATEGORY_EVOLUTION, "owner approved apply", case_e05))

    return cases


# ---------------------------------------------------------------------------
# EvalHarness 主类
# ---------------------------------------------------------------------------


class EvalHarness:
    """30 用例评估框架。

    Parameters
    ----------
    cases : list[EvalCase] | None
        用例列表；None 时使用 build_default() 产出的 30 条。
    """

    DEFAULT_CASE_COUNT = 30
    CATEGORY_COUNTS: dict[str, int] = {
        CATEGORY_INTENT: 10,
        CATEGORY_ORCHESTRATOR: 10,
        CATEGORY_HALLUCINATION: 5,
        CATEGORY_EVOLUTION: 5,
    }

    def __init__(self, cases: Optional[list[EvalCase]] = None) -> None:
        self._cases: list[EvalCase] = list(cases) if cases is not None else self._default_cases()

    # ---- public API --------------------------------------------------

    @property
    def cases(self) -> list[EvalCase]:
        return list(self._cases)

    @classmethod
    def build_default(cls) -> "EvalHarness":
        """工厂：构造包含 30 个默认用例的 harness。"""
        return cls(cls._default_cases())

    def run_all(self) -> EvalReport:
        """逐条执行用例，返回汇总报告。"""
        results: list[EvalResult] = []
        for case in self._cases:
            results.append(self._run_one(case))
        return self._summarize(results)

    def run_by_category(self, category: str) -> EvalReport:
        """仅执行某一类别（intent / orchestrator / hallucination / evolution）。"""
        if category not in CATEGORIES:
            raise ValueError(f"未知类别: {category!r}")
        results = [self._run_one(c) for c in self._cases if c.category == category]
        return self._summarize(results)

    # ---- serialization ----------------------------------------------

    @staticmethod
    def to_json(report: EvalReport) -> str:
        """把 EvalReport 序列化为 JSON 字符串（UTF-8，indent=2）。"""
        data: dict[str, Any] = {
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "pass_rate": round(report.pass_rate, 4),
            "avg_latency_ms": round(report.avg_latency_ms, 3),
            "error_breakdown": report.error_breakdown,
            "by_category": {
                cat: {
                    "total": stat.total,
                    "passed": stat.passed,
                    "failed": stat.failed,
                    "pass_rate": round(stat.pass_rate, 4),
                    "avg_latency_ms": round(stat.avg_latency_ms, 3),
                }
                for cat, stat in report.by_category.items()
            },
            "cases": [
                {
                    "case_id": r.case_id,
                    "category": r.category,
                    "description": r.description,
                    "passed": r.passed,
                    "expected": _safe_repr(r.expected),
                    "actual": _safe_repr(r.actual),
                    "latency_ms": r.latency_ms,
                    "error": r.error,
                }
                for r in report.cases
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    # ---- internals ---------------------------------------------------

    @staticmethod
    def _default_cases() -> list[EvalCase]:
        return (
            build_intent_cases()
            + build_orchestrator_cases()
            + build_hallucination_cases()
            + build_evolution_cases()
        )

    @staticmethod
    def _run_one(case: EvalCase) -> EvalResult:
        started = time.perf_counter()
        try:
            outcome = case.runner()
        except Exception as exc:  # noqa: BLE001 - 收敛 runner 内部异常
            elapsed = int((time.perf_counter() - started) * 1000)
            return EvalResult(
                case_id=case.case_id,
                category=case.category,
                description=case.description,
                passed=False,
                expected=None,
                actual=None,
                latency_ms=elapsed,
                error=f"{type(exc).__name__}: {exc}",
            )
        elapsed = int((time.perf_counter() - started) * 1000)
        return EvalResult(
            case_id=case.case_id,
            category=case.category,
            description=case.description,
            passed=outcome.passed,
            expected=outcome.expected,
            actual=outcome.actual,
            latency_ms=elapsed,
            error=outcome.error,
        )

    @staticmethod
    def _summarize(results: list[EvalResult]) -> EvalReport:
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        pass_rate = (passed / total) if total else 0.0
        avg_latency = (sum(r.latency_ms for r in results) / total) if total else 0.0

        error_breakdown: dict[str, int] = {}
        for r in results:
            if r.error:
                key = r.error.split(":", 1)[0]
                error_breakdown[key] = error_breakdown.get(key, 0) + 1
            elif not r.passed:
                error_breakdown["assertion"] = error_breakdown.get("assertion", 0) + 1

        by_category: dict[str, CategoryStat] = {}
        for cat in CATEGORIES:
            cat_items = [r for r in results if r.category == cat]
            if not cat_items:
                continue
            c_total = len(cat_items)
            c_passed = sum(1 for r in cat_items if r.passed)
            c_avg_lat = sum(r.latency_ms for r in cat_items) / c_total
            by_category[cat] = CategoryStat(
                total=c_total,
                passed=c_passed,
                failed=c_total - c_passed,
                pass_rate=c_passed / c_total,
                avg_latency_ms=c_avg_lat,
            )

        return EvalReport(
            total=total,
            passed=passed,
            failed=failed,
            pass_rate=pass_rate,
            avg_latency_ms=avg_latency,
            error_breakdown=error_breakdown,
            by_category=by_category,
            cases=results,
        )


# ---------------------------------------------------------------------------
# 辅助：安全序列化（enum / BaseModel → 可 JSON 输出的字符串）
# ---------------------------------------------------------------------------


def _safe_repr(value: Any) -> Any:
    """把 enum / BaseModel 等降级为 str；基本类型原样返回。"""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_repr(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _safe_repr(v) for k, v in value.items()}
    # enum / pydantic 模型 / 其他复杂对象
    return str(value)
