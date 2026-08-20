# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md
# [MODULE] zephyr.infrastructure.system_telemetry.otel_instrumentation
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""otel_instrumentation.py — 全链路 OTel (B12, DD86, TASK-015 beta v)"""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineTraceSpan:
    name: str
    start_time: float
    end_time: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "OK"


class OTelInstrumentation:
    """OTEL trace Orc->CE.build->compress->validate->inject->Agent Action (DD86)."""

    def __init__(self) -> None:
        self._spans: list[PipelineTraceSpan] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def spans(self) -> list[PipelineTraceSpan]:
        """只读：spans（Stage 4 公共化）。"""
        return self._spans

    @spans.setter
    def spans(self, value):
        """写入：spans（Stage 4 公共化）。"""
        self._spans = value

    def start_span(self, name: str, attrs: dict[str, Any] | None = None) -> PipelineTraceSpan:
        span = PipelineTraceSpan(name=name, start_time=time.time(), attributes=attrs or {})
        self._spans.append(span)
        return span

    def end_span(self, span: PipelineTraceSpan) -> None:
        span.end_time = time.time()
