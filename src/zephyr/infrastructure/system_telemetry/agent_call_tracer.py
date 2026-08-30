# [BLUEPRINT] MOD-INF-083 | docs/03_modules/_domain_infrastructure_operations/agent_call_tracer/blueprint.md
# [MODULE] zephyr.infrastructure.system_telemetry.agent_call_tracer
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] 无（纯内存；时钟/审计回调全注入，不触网）
# [CONSUMERS] 运行时装配批（Agent 调用链回放 / 审计落链 / 超预算巡检）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SpanKind 四段词表闭合(intent|tool_call|llm|decision); span_id 按 trace 内自增序号确定性生成; 父子须同 trace 且父未闭合; 已闭合 span 禁二次闭合; over_budget=时长>budget_ms; 未闭合查询告警; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/agent_call_tracer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AgentCallTracerError(占位 ZA-INF-UNREGISTERED-AGENT-TRACER)——空trace_id/空name/非法kind/负预算/未知父/跨trace父/父已闭合/未知span/二次闭合/非法状态迁移时抛
# [TESTS] tests/infrastructure/test_agent_call_tracer.py
# [A_module] module_id=MOD-INF-083 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
AgentCallTracer — AI Agent 调用链追踪器（MOD-INF-083）。

B14-04637（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRATEL-003，A9运维架构）：
Agent 调用链 Span 模型（意图 INTENT → 工具调用 TOOL_CALL → LLM → 决策输出
DECISION 四段）关联 TraceID，Span 树构建/闭合校验（未闭合查询告警），异常/
超预算调用高亮标记（over_budget），调用链落审计回调供回放。LangSmith 式追踪
单机内存版。

查重分工（蓝图 §0）：a2a_tracing=A2A 协议层追踪（本件为 Agent 内部四段调用
语义，不重建协议层）；observability_triad=三支柱门面（本件产出 Span 供其消
费，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: agent_call_tracer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: agent_call_tracer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AgentSpan
#   name_en: AgentSpan
#   intro: Agent 调用链 Span（frozen；end_span 以 replace 生成闭合实例）。
#   desc: Agent 调用链 Span（frozen；end_span 以 replace 生成闭合实例）。；公共方法（定义序）: duration_ms；源码 L115-L135
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② AgentCallTracer
#   name_en: AgentCallTracer
#   intro: Agent 调用链追踪器（Span 树构建 + 闭合校验 + 高亮 + 审计）。
#   desc: Agent 调用链追踪器（Span 树构建 + 闭合校验 + 高亮 + 审计）。；公共方法（定义序）: start_span, end_span, get_span, unclosed_spans, trace_spa…
#   inputs: clock audit_sink
#   outputs: 返回值
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: AgentSpan, AgentCallTracer
#   downstream: 运行时装配批（Agent 调用链回放 / 审计落链 / 超预算巡检）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AgentCallTracer",
    "AgentCallTracerError",
    "AgentSpan",
    "SpanKind",
    "SpanStatus",
]


class AgentCallTracerError(Exception):
    """调用链追踪输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-AGENT-TRACER。
    """


class SpanKind(str, Enum):
    """Agent 调用链四段（词表闭合）。"""

    INTENT = "intent"
    TOOL_CALL = "tool_call"
    LLM = "llm"
    DECISION = "decision"


class SpanStatus(str, Enum):
    """Span 状态机（RUNNING → OK|ERROR）。"""

    RUNNING = "running"
    OK = "ok"
    ERROR = "error"


@dataclass(frozen=True)
class AgentSpan:
    """Agent 调用链 Span（frozen；end_span 以 replace 生成闭合实例）。"""

    span_id: str
    trace_id: str
    parent_id: str | None
    kind: SpanKind
    name: str
    start: datetime.datetime
    end: datetime.datetime | None
    status: SpanStatus
    budget_ms: float | None
    over_budget: bool
    error: str | None

    @property
    def duration_ms(self) -> float | None:
        """已闭合 span 的时长（毫秒）；未闭合 → None。"""
        if self.end is None:
            return None
        return (self.end - self.start).total_seconds() * 1000.0


class AgentCallTracer:
    """Agent 调用链追踪器（Span 树构建 + 闭合校验 + 高亮 + 审计）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[AgentSpan], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._spans: dict[str, AgentSpan] = {}
        self._seq = 0

    # ── Span 生命周期 ─────────────────────────────────────────────────────

    def start_span(
        self,
        trace_id: str,
        kind: SpanKind,
        name: str,
        *,
        parent_id: str | None = None,
        budget_ms: float | None = None,
    ) -> AgentSpan:
        """开启 Span：父校验（同 trace 且未闭合）→ 确定性 span_id → RUNNING。"""
        if not trace_id:
            raise AgentCallTracerError("trace_id 为空")
        if not name:
            raise AgentCallTracerError("span name 为空")
        if not isinstance(kind, SpanKind):
            raise AgentCallTracerError(f"非法 SpanKind: {kind!r}")
        if budget_ms is not None and budget_ms < 0:
            raise AgentCallTracerError(f"budget_ms 非法: {budget_ms!r}")
        if parent_id is not None:
            parent = self._spans.get(parent_id)
            if parent is None:
                raise AgentCallTracerError(f"未知父 span: {parent_id!r}")
            if parent.trace_id != trace_id:
                raise AgentCallTracerError(f"跨 trace 父子非法: 父 {parent.trace_id!r} != {trace_id!r}")
            if parent.status is not SpanStatus.RUNNING:
                raise AgentCallTracerError(f"父 span 已闭合，禁止再开子 span: {parent_id!r}")
        self._seq += 1
        span = AgentSpan(
            span_id=f"{trace_id}-{self._seq:04d}",
            trace_id=trace_id,
            parent_id=parent_id,
            kind=kind,
            name=name,
            start=self._clock(),
            end=None,
            status=SpanStatus.RUNNING,
            budget_ms=budget_ms,
            over_budget=False,
            error=None,
        )
        self._spans[span.span_id] = span
        return span

    def end_span(
        self,
        span_id: str,
        status: SpanStatus = SpanStatus.OK,
        *,
        error: str | None = None,
    ) -> AgentSpan:
        """闭合 Span：状态迁移 + 超预算/异常高亮 + 落审计回调。"""
        span = self._spans.get(span_id)
        if span is None:
            raise AgentCallTracerError(f"未知 span: {span_id!r}")
        if span.status is not SpanStatus.RUNNING:
            raise AgentCallTracerError(f"span 已闭合，禁止二次闭合: {span_id!r}")
        if not isinstance(status, SpanStatus) or status is SpanStatus.RUNNING:
            raise AgentCallTracerError(f"非法闭合状态: {status!r}")
        closed = replace(
            span,
            end=self._clock(),
            status=status,
            error=error,
        )
        over = closed.budget_ms is not None and closed.duration_ms is not None and closed.duration_ms > closed.budget_ms
        if over:
            closed = replace(closed, over_budget=True)
            _log.warning(
                "超预算调用高亮: %s (%s) %.1fms > %.1fms",
                span_id,
                closed.name,
                closed.duration_ms,
                closed.budget_ms,
            )
        if status is SpanStatus.ERROR:
            _log.warning("异常调用标记: %s (%s) error=%s", span_id, closed.name, error)
        self._spans[span_id] = closed
        if self._audit_sink is not None:
            try:
                self._audit_sink(closed)
            except Exception:  # noqa: BLE001 — 审计失败不阻断追踪
                _log.exception("audit_sink 回调失败: %s", span_id)
        return closed

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get_span(self, span_id: str) -> AgentSpan:
        """单 Span 查询（未知 → Fail-Closed）。"""
        span = self._spans.get(span_id)
        if span is None:
            raise AgentCallTracerError(f"未知 span: {span_id!r}")
        return span

    def unclosed_spans(self, trace_id: str | None = None) -> tuple[AgentSpan, ...]:
        """未闭合 Span 查询（存在即告警留痕；按 (start, span_id) 排序）。"""
        out = [
            s
            for s in self._spans.values()
            if s.status is SpanStatus.RUNNING and (trace_id is None or s.trace_id == trace_id)
        ]
        out.sort(key=lambda s: (s.start, s.span_id))
        if out:
            _log.warning("未闭合 span 告警: %s", [s.span_id for s in out])
        return tuple(out)

    def trace_spans(self, trace_id: str) -> tuple[AgentSpan, ...]:
        """单 trace 全 Span（按 (start, span_id) 确定性排序）。"""
        out = [s for s in self._spans.values() if s.trace_id == trace_id]
        out.sort(key=lambda s: (s.start, s.span_id))
        return tuple(out)

    def trace_tree(self, trace_id: str) -> tuple[dict, ...]:
        """Span 树（根→子嵌套 dict；子节点按 (start, span_id) 排序）。"""
        spans = self.trace_spans(trace_id)
        children: dict[str | None, list[AgentSpan]] = {}
        for span in spans:
            children.setdefault(span.parent_id, []).append(span)

        def _node(span: AgentSpan) -> dict:
            return {
                "span": span,
                "children": tuple(_node(c) for c in children.get(span.span_id, [])),
            }

        return tuple(_node(root) for root in children.get(None, []))
