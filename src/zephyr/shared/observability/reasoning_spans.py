# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.observability.reasoning_spans
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.feedback_loop.__init___from_obs; tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class ReasoningSpan:
    span_id: str
    operation: str
    start_time: float
    end_time: float = 0.0
    parent_id: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000


class ReasoningSpans:
    def __init__(self):
        self._spans: list[ReasoningSpan] = []

    def start(self, operation: str, parent_id: str = "", **metadata: str) -> ReasoningSpan:
        span = ReasoningSpan(str(uuid.uuid4())[:8], operation, time.time(), parent_id=parent_id, metadata=metadata)
        self._spans.append(span)
        return span

    def end(self, span_id: str) -> ReasoningSpan | None:
        for s in self._spans:
            if s.span_id == span_id:
                s.end_time = time.time()
                return s
        return None

    def get_trace(self, root_span_id: str) -> list[ReasoningSpan]:
        return [s for s in self._spans if s.span_id == root_span_id or s.parent_id == root_span_id]
