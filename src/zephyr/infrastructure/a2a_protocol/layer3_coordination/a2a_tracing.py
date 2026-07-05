# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_tracing
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_tracing | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 分布式追踪 — 跨 Agent 请求链追踪 (Span-based)

每个跨 Agent 请求生成一个 TraceId + 每跳生成 Span:
  Span 记录: trace_id / span_id / parent_span_id / agent_id / action / duration

方法: 类似 OpenTelemetry Span 模型, Agent 级分布式追踪
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Span:
    span_id: str
    trace_id: str
    parent_span_id: str | None
    agent_id: str
    action: str
    resource: str
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


class A2ATracing:
    def __init__(self):
        self._traces: dict[str, list[Span]] = {}

    def start_span(
        self,
        trace_id: str,
        span_id: str,
        agent_id: str,
        action: str,
        resource: str,
        parent_span_id: str | None = None,
        start_time: float = 0.0,
    ) -> Span:
        import time as _time

        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            agent_id=agent_id,
            action=action,
            resource=resource,
            start_time=start_time or _time.time(),
        )
        if trace_id not in self._traces:
            self._traces[trace_id] = []
        self._traces[trace_id].append(span)
        return span

    def end_span(self, span: Span, end_time: float = 0.0):
        import time as _time

        span.end_time = end_time or _time.time()

    def get_trace(self, trace_id: str) -> list[Span]:
        return self._traces.get(trace_id, [])

    def summary(self, trace_id: str) -> dict:
        spans = self.get_trace(trace_id)
        if not spans:
            return {}
        return {
            "trace_id": trace_id,
            "span_count": len(spans),
            "agents": list({s.agent_id for s in spans}),
            "total_duration": max(s.end_time for s in spans) - min(s.start_time for s in spans),
        }
