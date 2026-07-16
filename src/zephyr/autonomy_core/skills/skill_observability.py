# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_observability
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Observability
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 可观测性 —— Trace/Span/Metric/Log 四维信号.
集成: skill_feedback -> metrics, skill_executor -> traces, skill_lifecycle -> events.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Span:
    name: str
    start_ms: int = 0
    end_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": self.end_ms - self.start_ms if self.end_ms else 0,
            "metadata": self.metadata,
        }


@dataclass
class Trace:
    trace_id: str
    skill_id: str
    start_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    end_ms: int = 0
    spans: list[Span] = field(default_factory=list)
    status: str = "running"

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "skill_id": self.skill_id,
            "start_ms": self.start_ms,
            "duration_ms": self.end_ms - self.start_ms if self.end_ms else 0,
            "spans": [s.to_dict() for s in self.spans],
            "status": self.status,
        }


class SkillObservability:
    """Skill 可观测性 —— Trace/Span/Metric/Log."""

    _TRACES: dict[str, Trace] = {}
    _METRICS: dict[str, list[dict[str, Any]]] = {}
    _EVENT_LOG = Path("_journals/skill_events.jsonl")
    _MAX_EVENTS = 500

    # ---- Trace API ----

    @classmethod
    def start_trace(cls, skill_id: str) -> dict[str, Any]:
        trace_id = f"trace-{skill_id}-{int(time.time() * 1000)}"
        trace = Trace(trace_id=trace_id, skill_id=skill_id)
        cls._TRACES[trace_id] = trace
        return {"trace_id": trace_id, "skill_id": skill_id, "status": "started"}

    @classmethod
    def add_span(cls, trace_id: str, span_name: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        trace = cls._TRACES.get(trace_id)
        if not trace:
            return {"error": f"Trace not found: {trace_id}"}
        span = Span(name=span_name, start_ms=int(time.time() * 1000), metadata=metadata or {})
        trace.spans.append(span)
        return {"trace_id": trace_id, "span_name": span_name, "status": "span_added"}

    @classmethod
    def end_span(cls, trace_id: str, span_name: str) -> dict[str, Any]:
        trace = cls._TRACES.get(trace_id)
        if not trace:
            return {"error": f"Trace not found: {trace_id}"}
        for span in reversed(trace.spans):
            if span.name == span_name and not span.end_ms:
                span.end_ms = int(time.time() * 1000)
                return {"trace_id": trace_id, "span_name": span_name, "status": "span_ended"}
        return {"error": f"Running span '{span_name}' not found in trace {trace_id}"}

    @classmethod
    def end_trace(cls, trace_id: str, status: str = "completed") -> dict[str, Any]:
        trace = cls._TRACES.get(trace_id)
        if not trace:
            return {"error": f"Trace not found: {trace_id}"}
        trace.end_ms = int(time.time() * 1000)
        trace.status = status
        for span in trace.spans:
            if not span.end_ms:
                span.end_ms = trace.end_ms
        return trace.to_dict()

    @classmethod
    def get_trace(cls, trace_id: str) -> dict[str, Any] | None:
        trace = cls._TRACES.get(trace_id)
        return trace.to_dict() if trace else None

    # ---- Metrics API ----

    @classmethod
    def record_metric(
        cls, skill_id: str, metric_name: str, value: float, tags: dict[str, str] | None = None
    ) -> dict[str, Any]:
        entry = {
            "skill_id": skill_id,
            "metric": metric_name,
            "value": value,
            "tags": tags or {},
            "timestamp": time.time(),
        }
        cls._METRICS.setdefault(skill_id, []).append(entry)
        if len(cls._METRICS[skill_id]) > cls._MAX_EVENTS:
            cls._METRICS[skill_id] = cls._METRICS[skill_id][-cls._MAX_EVENTS :]
        return entry

    @classmethod
    def get_metrics(
        cls, skill_id: str | None = None, metric_name: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        if skill_id:
            entries = cls._METRICS.get(skill_id, [])
        else:
            entries = []
            for sid, vals in cls._METRICS.items():
                entries.extend(vals)
        if metric_name:
            entries = [e for e in entries if e["metric"] == metric_name]
        return entries[-limit:]

    # ---- Event Log API ----

    @classmethod
    def log_event(cls, skill_id: str, event_type: str, detail: dict[str, Any] | None = None) -> dict[str, Any]:
        event = {
            "skill_id": skill_id,
            "event_type": event_type,
            "detail": detail or {},
            "timestamp": time.time(),
        }
        try:
            cls._EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(cls._EVENT_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            pass
        return event

    # ---- Health Summary ----

    @classmethod
    def health_summary(cls) -> dict[str, Any]:
        return {
            "active_traces": len(cls._TRACES),
            "skills_with_metrics": len(cls._METRICS),
            "total_metric_entries": sum(len(v) for v in cls._METRICS.values()),
        }

    @classmethod
    def clear_all(cls):
        cls._TRACES.clear()
        cls._METRICS.clear()


__all__ = ["SkillObservability", "Span", "Trace"]
