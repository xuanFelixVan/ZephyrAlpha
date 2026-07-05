# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.agent_observability
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_agent_observability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Agent Observability
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0
"""

from datetime import UTC, datetime
from typing import Any


class AgentObservability:
    """Agent Trace 全链路可观测性"""

    def __init__(self):
        self._traces: dict[str, dict[str, Any]] = {}

    def start_trace(self, skill_id: str) -> str:
        trace_id = f"trace-{skill_id}-{datetime.now(UTC).timestamp()}"
        self._traces[trace_id] = {"skill_id": skill_id, "spans": [], "start_time": datetime.now(UTC).isoformat()}
        return trace_id

    def add_span(self, trace_id: str, span_name: str, metadata: dict[str, Any] = None) -> dict[str, Any]:
        if trace_id not in self._traces:
            raise KeyError(f"Trace {trace_id} not found")
        span = {"name": span_name, "metadata": metadata or {}, "timestamp": datetime.now(UTC).isoformat()}
        self._traces[trace_id]["spans"].append(span)
        return span

    def get_trace(self, trace_id: str) -> dict[str, Any]:
        return self._traces.get(trace_id, {})
