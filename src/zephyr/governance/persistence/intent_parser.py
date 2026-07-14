# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md
# [MODULE] zephyr.governance.persistence.intent_parser
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__; zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_intent_parser | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-3-20 (V-09) three-stage intent parser (
"""
IntentParser · 意图三阶段级联解析器（V-09）
============================================

Task ID     : T-3-20 (A26)
KBG         :  三阶段、ChromaDB、LLM fallback）
Depends     : T-2-21（C46 intent_keyword_mapper）
safety_level: M

职责总览
--------

将用户 query 转换为 ``IntentResult`` 输出，**级联**三个阶段：

  Stage 1 — keyword 匹配（``IntentKeywordMapper``）
    confidence ≥ 0.9  -> 直接执行
  Stage 2 — embedding 语义检索（ChromaDB，Protocol 注入）
    confidence ≥ 0.7  -> 直接执行
  Stage 3 — LLM 深度理解（Protocol 注入）
    **兜底**，永远返回一个结果（可能 requires_human=True）

所有 Stage 都按 ``IntentResult`` 契约输出（兼容 Stage 1 已有字段），
叠加：

- ``stage_trace`` — 本次 parse 实际经历的阶段序列（"keyword"/"semantic"/"llm"）
- 最终 ``source_stage`` 为"产出可信结果"的阶段；全部兜底时置 ``"llm"``

与下游集成
----------
- ``dos_launcher.py``：根据 ``IntentResult.suggested_directives`` 组装
  directive 链后调用 ``DOSLauncher.load_chain``。本模块提供
  ``IntentParser.plan_directive_chain()`` 辅助函数。
- ``context_injector.py``：``IntentResult.primary_domain`` 可作为
  ``RetrievalMode.MODULE_ID`` 的键；提供 ``inject_context_for(parser, injector)``
  辅助函数。

零外部依赖
----------
- 不引入 chromadb / httpx 等库；embedding 检索通过 ``EmbeddingSearcher``
  Protocol 注入；LLM 调用通过 ``LLMIntentCaller`` Protocol 注入。
- 生产环境的 ChromaDB / Anthropic SDK 由调用方适配。
"""

from __future__ import annotations

from typing import Final
import time
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from zephyr.governance.persistence.intent_keyword_mapper import (
    IntentKeywordMapper,
    IntentResult,
    StageLiteral,
)
from zephyr.integration.shared.schema.schemas import BASE_CONFIG

__all__ = [
    "DEFAULT_STAGE_THRESHOLDS",
    "EmbeddingHit",
    "EmbeddingSearcher",
    "IntentClassifyFailure",
    "IntentParseTrace",
    "IntentParser",
    "IntentType",
    "LLMIntentCaller",
    "LLMIntentVerdict",
    "classify",
    "inject_context_for",
    "plan_directive_chain",
]

# ---------------------------------------------------------------------------
# 阈值常量（ §4）
# ---------------------------------------------------------------------------

DEFAULT_STAGE_THRESHOLDS: Final[dict[str, float]] = {
    "stage1_accept": 0.90,  # Stage 1 confidence ≥ 0.9 直接执行
    "stage2_accept": 0.70,  # Stage 2 confidence ≥ 0.7 直接执行
    # Stage 3 为兜底，无阈值
    "stage3_human_floor": 0.30,  # LLM 结果 confidence < 此值 -> requires_human=True
}

# ---------------------------------------------------------------------------
# Pydantic 契约（Stage 2/3 输入输出）
# ---------------------------------------------------------------------------


class EmbeddingHit(BaseModel):
    """ChromaDB 检索返回的单条结果（由 EmbeddingSearcher 封装）。"""

    model_config = BASE_CONFIG

    domain: str = Field(min_length=1, description="该 hit 所属域 D0-D9")
    score: float = Field(ge=0.0, le=1.0, description="相似度分（0-1，1 最相似）")
    text: str = Field(default="", description="命中文本片段（用于 rationale）")
    source: str = Field(default="", description="来源（KE id / 文件路径等）")


class LLMIntentVerdict(BaseModel):
    """LLM 深度理解的结构化返回值。"""

    model_config = BASE_CONFIG

    primary_domain: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    secondary_domains: list[str] = Field(default_factory=list)
    rationale: str = Field(default="")
    cost_usd: float = Field(default=0.0, ge=0.0)
    suggested_directives: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Protocol（依赖注入）
# ---------------------------------------------------------------------------


@runtime_checkable
class EmbeddingSearcher(Protocol):
    """ChromaDB 封装协议；生产适配器调用 chromadb.Collection.query。"""

    def __call__(self, query: str, *, top_k: int = 5) -> list[EmbeddingHit]:  # pragma: no cover - Protocol 签名
        ...


@runtime_checkable
class LLMIntentCaller(Protocol):
    """LLM 深度理解协议；生产实现可以是 Sonnet 4.6 / GLM-5.1。"""

    def __call__(
        self, query: str, *, context: dict[str, Any] | None = None
    ) -> LLMIntentVerdict:  # pragma: no cover - Protocol 签名
        ...


# ---------------------------------------------------------------------------
# Trace
# ---------------------------------------------------------------------------


class IntentParseTrace(BaseModel):
    """单次 parse 的阶段追踪信息。"""

    model_config = BASE_CONFIG

    query: str = Field(min_length=1)
    stages: list[str] = Field(default_factory=list, description="实际经过的阶段顺序")
    stage1_confidence: float | None = Field(default=None)
    stage2_confidence: float | None = Field(default=None)
    stage3_confidence: float | None = Field(default=None)
    total_latency_ms: int = Field(default=0, ge=0)
    total_cost_usd: float = Field(default=0.0, ge=0.0)


# ---------------------------------------------------------------------------
# IntentParser
# ---------------------------------------------------------------------------


class IntentParser:
    """三阶段级联意图解析器。

    Parameters
    ----------
    keyword_mapper : IntentKeywordMapper | None
        Stage 1 关键字匹配器；None 时使用默认实例。
    embedding_searcher : EmbeddingSearcher | None
        Stage 2 ChromaDB 检索；None 时 Stage 2 跳过。
    llm_caller : LLMIntentCaller | None
        Stage 3 LLM 深度理解；None 时 Stage 3 返回兜底 UNKNOWN。
    thresholds : dict[str, float] | None
        阈值覆盖，详见 ``DEFAULT_STAGE_THRESHOLDS``。
    """

    def __init__(
        self,
        keyword_mapper: IntentKeywordMapper | None = None,
        *,
        embedding_searcher: EmbeddingSearcher | None = None,
        llm_caller: LLMIntentCaller | None = None,
        thresholds: dict[str, float] | None = None,
    ) -> None:
        self._kw = keyword_mapper or IntentKeywordMapper()
        self._emb = embedding_searcher
        self._llm = llm_caller
        self._thresh = {**DEFAULT_STAGE_THRESHOLDS, **(thresholds or {})}
        self._last_trace: IntentParseTrace | None = None

    # ---- accessors ---------------------------------------------------

    @property
    def thresholds(self) -> dict[str, float]:
        return dict(self._thresh)

    @property
    def last_trace(self) -> IntentParseTrace | None:
        return self._last_trace

    # ---- main --------------------------------------------------------

    def parse(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> IntentResult:
        """按三阶段级联解析 query，返回最终 IntentResult。"""
        start = time.perf_counter()
        trace = IntentParseTrace(query=query or "_empty_")
        total_cost = 0.0

        # Stage 1 ----------------------------------------------------
        trace.stages.append("keyword")
        s1 = self._kw.map_intent(query, context)
        trace.stage1_confidence = s1.confidence
        total_cost += s1.cost_usd

        if s1.confidence >= self._thresh["stage1_accept"] and s1.primary_domain != "UNKNOWN":
            return self._finalize(s1, trace, total_cost, start, source_stage="keyword")

        # Stage 2 ----------------------------------------------------
        if self._emb is not None and query.strip():
            trace.stages.append("semantic")
            s2 = self._run_stage2(query, s1)
            trace.stage2_confidence = s2.confidence
            total_cost += s2.cost_usd
            if s2.confidence >= self._thresh["stage2_accept"] and s2.primary_domain != "UNKNOWN":
                return self._finalize(s2, trace, total_cost, start, source_stage="semantic")
            # semantic 不过阈值时继续到 LLM，记住这个结果以便与 Stage 1 结合
            fallback_mid = s2
        else:
            fallback_mid = s1

        # Stage 3 ----------------------------------------------------
        if self._llm is not None and query.strip():
            trace.stages.append("llm")
            s3 = self._run_stage3(query, context, fallback_mid)
            trace.stage3_confidence = s3.confidence
            total_cost += s3.cost_usd
            return self._finalize(s3, trace, total_cost, start, source_stage="llm")

        # 兜底：三阶段都不可用 -> 返回 Stage 2 或 Stage 1 的结果并 requires_human
        fallback_mid.requires_human = True
        fallback_mid.fallback_hint = fallback_mid.fallback_hint or "all-stages-unavailable"
        return self._finalize(fallback_mid, trace, total_cost, start, source_stage=fallback_mid.source_stage)

    # ---- Stage 2 -----------------------------------------------------

    def _run_stage2(self, query: str, stage1: IntentResult) -> IntentResult:
        """调用注入的 EmbeddingSearcher，按域聚合得分产出 IntentResult。"""
        if self._emb is None: raise RuntimeError("embedding service not injected")  # 5.88.5 修复: assert->if/raise
        try:
            hits = self._emb(query, top_k=5)
        except Exception as exc:  # — 检索失败降级到 Stage 3
            return self._failed_stage(query, stage="semantic", reason=f"semantic_error: {type(exc).__name__}: {exc}")

        if not hits:
            return self._failed_stage(query, stage="semantic", reason="semantic: no hits")

        domain_scores: dict[str, float] = {}
        sources: list[str] = []
        for h in hits:
            prev = domain_scores.get(h.domain, 0.0)
            # 加和聚合：多次命中提升置信
            domain_scores[h.domain] = prev + h.score
            if h.source and h.source not in sources:
                sources.append(h.source)

        ranked = sorted(domain_scores.items(), key=lambda x: -x[1])
        top_domain, top_sum = ranked[0]
        # 归一：以所有命中分之和为分母
        total = sum(h.score for h in hits) or 1.0
        confidence = min(top_sum / total, 1.0)

        secondary = [d for d, _ in ranked[1:4] if d != top_domain]

        # 合并 Stage 1 已匹配的 keywords 作为 evidence
        matched = list(stage1.matched_keywords)

        return IntentResult(
            query=query,
            primary_domain=top_domain,
            secondary_domains=secondary,
            confidence=round(confidence, 4),
            matched_keywords=matched,
            source_stage="semantic",
            suggested_directives=stage1.suggested_directives,
            requires_human=False,
            rationale=f"semantic: top_domain={top_domain}, hits={len(hits)}, sources={sources[:3]}",
            latency_ms=0,
            cost_usd=0.0,
            fallback_hint=None if confidence >= self._thresh["stage2_accept"] else "stage-2-low",
        )

    # ---- Stage 3 -----------------------------------------------------

    def _run_stage3(
        self,
        query: str,
        context: dict[str, Any] | None,
        mid: IntentResult,
    ) -> IntentResult:
        """调用注入的 LLM，返回兜底 IntentResult。"""
        if self._llm is None: raise RuntimeError("LLM service not injected")  # 5.88.5 修复: assert->if/raise
        try:
            verdict = self._llm(query, context=context)
        except Exception as exc:  # — LLM 失败时保守兜底
            return self._failed_stage(
                query,
                stage="llm",
                reason=f"llm_error: {type(exc).__name__}: {exc}",
                prev=mid,
            )

        low_floor = self._thresh["stage3_human_floor"]
        requires_human = verdict.confidence < low_floor or verdict.primary_domain == "UNKNOWN"
        directives = verdict.suggested_directives or mid.suggested_directives or ["999"]

        return IntentResult(
            query=query,
            primary_domain=verdict.primary_domain,
            secondary_domains=verdict.secondary_domains,
            confidence=round(verdict.confidence, 4),
            matched_keywords=mid.matched_keywords,
            source_stage="llm",
            suggested_directives=directives,
            requires_human=requires_human,
            rationale=verdict.rationale or "llm stage fallback",
            latency_ms=0,
            cost_usd=verdict.cost_usd,
            fallback_hint=None,
        )

    # ---- helpers -----------------------------------------------------

    def _failed_stage(
        self,
        query: str,
        *,
        stage: StageLiteral,
        reason: str,
        prev: IntentResult | None = None,
    ) -> IntentResult:
        if prev is not None:
            return IntentResult(
                query=query,
                primary_domain=prev.primary_domain,
                secondary_domains=prev.secondary_domains,
                confidence=prev.confidence * 0.5,
                matched_keywords=prev.matched_keywords,
                source_stage=stage,
                suggested_directives=prev.suggested_directives,
                requires_human=True,
                rationale=reason,
                latency_ms=0,
                cost_usd=0.0,
                fallback_hint=f"{stage}-failed",
            )
        return IntentResult(
            query=query,
            primary_domain="UNKNOWN",
            confidence=0.0,
            matched_keywords=[],
            source_stage=stage,
            suggested_directives=["999"],
            requires_human=True,
            rationale=reason,
            latency_ms=0,
            cost_usd=0.0,
            fallback_hint=f"{stage}-failed",
        )

    def _finalize(
        self,
        result: IntentResult,
        trace: IntentParseTrace,
        total_cost: float,
        start_time: float,
        *,
        source_stage: StageLiteral,
    ) -> IntentResult:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        trace.total_latency_ms = elapsed_ms
        trace.total_cost_usd = round(total_cost, 6)
        self._last_trace = trace

        # 构造一个新的 IntentResult（model_copy 避免 validate_assignment 报 extra）
        final = result.model_copy(
            update={
                "latency_ms": elapsed_ms,
                "cost_usd": round(total_cost, 6),
                "source_stage": source_stage,
            }
        )
        return final


# ---------------------------------------------------------------------------
# 集成辅助函数
# ---------------------------------------------------------------------------


def plan_directive_chain(result: IntentResult, separator: str = "+") -> str:
    """把 IntentResult.suggested_directives 转成 DOSLauncher 用的链字符串。

    Returns
    -------
    str
        ``"325+344+999"`` 格式；若列表为空，退化为 ``"999"``（兜底）。
    """
    directives = [d.strip() for d in (result.suggested_directives or []) if d.strip()]
    if not directives:
        return "999"
    return separator.join(directives)


def inject_context_for(
    parser_result: IntentResult,
    injector: object,
) -> object:
    """用 IntentResult 的 primary_domain 去 ContextInjector 拉 KE 注入。

    Parameters
    ----------
    parser_result : IntentResult
        ``IntentParser.parse()`` 的输出。
    injector : Any
        ``ContextInjector`` 实例（鸭子类型，需具备 ``inject_by_module_id``/
        ``inject_by_keyword`` 方法，避免强依赖导入）。

    Returns
    -------
    Any
        ``InjectedContext`` 实例（由 injector 定义）。
    """
    if parser_result.primary_domain != "UNKNOWN" and hasattr(injector, "inject_by_module_id"):
        return injector.inject_by_module_id(parser_result.primary_domain)
    if hasattr(injector, "inject_by_keyword"):
        return injector.inject_by_keyword(parser_result.query)
    raise AttributeError(
        "injector 缺少 inject_by_module_id / inject_by_keyword 方法；"
        "请传入 zephyr.autonomy_core.context.context_injector.ContextInjector 实例"
    )


class IntentType(str, Enum):
    """任务意图类型——10 分类，覆盖 task_type 枚举 + QUERY/DEBUG 辅助模式。

    DD4 决策：10 分类覆盖 task_type 枚举 + QUERY/DEBUG 辅助模式。
    否决方案: "30+ 细粒度" — 分类过多->keyword 精度下降。
    重评条件: 混淆率 > 10%。
    """

    CODE_GEN = "CODE_GEN"
    CODE_REVIEW = "CODE_REVIEW"
    ANALYSIS = "ANALYSIS"
    OPS_FIX = "OPS_FIX"
    DOC = "DOC"
    REFACTOR = "REFACTOR"
    TEST = "TEST"
    AUDIT = "AUDIT"
    QUERY = "QUERY"
    DEBUG = "DEBUG"


class IntentClassifyFailure(Exception):
    """意图分类失败异常——BUILD-C00 flag 模式（不阻断，仅标记）。"""

    def __init__(self, message: str, user_prompt: str = "") -> None:
        super().__init__(message)
        self.user_prompt = user_prompt


_INTENT_KEYWORD_MAP: dict[str, IntentType] = {
    "生成": IntentType.CODE_GEN,
    "创建": IntentType.CODE_GEN,
    "实现": IntentType.CODE_GEN,
    "编写": IntentType.CODE_GEN,
    "新建": IntentType.CODE_GEN,
    "generate": IntentType.CODE_GEN,
    "create": IntentType.CODE_GEN,
    "implement": IntentType.CODE_GEN,
    "build": IntentType.CODE_GEN,
    "code gen": IntentType.CODE_GEN,
    "审查": IntentType.CODE_REVIEW,
    "检查": IntentType.CODE_REVIEW,
    "review": IntentType.CODE_REVIEW,
    "inspect": IntentType.CODE_REVIEW,
    "code review": IntentType.CODE_REVIEW,
    "分析": IntentType.ANALYSIS,
    "评估": IntentType.ANALYSIS,
    "analysis": IntentType.ANALYSIS,
    "analyze": IntentType.ANALYSIS,
    "report": IntentType.ANALYSIS,
    "修复": IntentType.OPS_FIX,
    "漏洞": IntentType.OPS_FIX,
    "fix": IntentType.OPS_FIX,
    "bug": IntentType.OPS_FIX,
    "hotfix": IntentType.OPS_FIX,
    "patch": IntentType.OPS_FIX,
    "安全事故": IntentType.OPS_FIX,
    "安全漏洞": IntentType.OPS_FIX,
    "文档": IntentType.DOC,
    "doc": IntentType.DOC,
    "documentation": IntentType.DOC,
    "readme": IntentType.DOC,
    "重构": IntentType.REFACTOR,
    "refactor": IntentType.REFACTOR,
    "restructure": IntentType.REFACTOR,
    "重写": IntentType.REFACTOR,
    "测试": IntentType.TEST,
    "test": IntentType.TEST,
    "pytest": IntentType.TEST,
    "单元测试": IntentType.TEST,
    "审计": IntentType.AUDIT,
    "audit": IntentType.AUDIT,
    "合规": IntentType.AUDIT,
    "compliance": IntentType.AUDIT,
    "查询": IntentType.QUERY,
    "问题": IntentType.QUERY,
    "question": IntentType.QUERY,
    "query": IntentType.QUERY,
    "调试": IntentType.DEBUG,
    "debug": IntentType.DEBUG,
    "排查": IntentType.DEBUG,
    "troubleshoot": IntentType.DEBUG,
    "diagnose": IntentType.DEBUG,
}


def classify(user_prompt: str) -> IntentType:
    """BUILD-C00 入口——将用户提示词分类为 IntentType。

    使用关键词匹配进行分类。BUILD-C00 要求 on_failure=flag（仅标记，不阻断后续流程）。

    Parameters
    ----------
    user_prompt : str
        用户输入的任务提示词

    Returns
    -------
    IntentType
        识别的意图类型；无法识别时返回 CODE_GEN（默认兜底）

    Raises
    ------
    IntentClassifyFailure
        仅当 user_prompt 为空字符串时抛出（flag 模式——调用方自行处理）

    Examples
    --------
    >>> classify("帮我修复安全漏洞")
    <IntentType.OPS_FIX: 'OPS_FIX'>
    >>> classify("审查这段代码")
    <IntentType.CODE_REVIEW: 'CODE_REVIEW'>
    """
    if not user_prompt or not user_prompt.strip():
        raise IntentClassifyFailure("BUILD-C00: user_prompt 为空，无法分类", user_prompt=user_prompt)

    prompt_lower = user_prompt.strip().lower()

    scored: dict[IntentType, int] = {}
    for keyword, intent in _INTENT_KEYWORD_MAP.items():
        if keyword in prompt_lower:
            scored[intent] = scored.get(intent, 0) + 1

    if not scored:
        return IntentType.CODE_GEN

    best = max(scored, key=lambda k: scored[k])
    return best
