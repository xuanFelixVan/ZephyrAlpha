# [BLUEPRINT] MOD-INF-019 | 03_modules/l01_infrastructure/agent-spec/blueprint.md | §

# [MODULE] zephyr.agent_spec.agent_observability

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Agent Observability
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0
"""

from datetime import datetime, timezone
from typing import Dict, Any, List


class AgentObservability:
    """Agent Trace 全链路可观测性"""

    def __init__(self):
        self._traces: Dict[str, Dict[str, Any]] = {}

    def start_trace(self, skill_id: str) -> str:
        trace_id = f"trace-{skill_id}-{datetime.now(timezone.utc).timestamp()}"
        self._traces[trace_id] = {"skill_id": skill_id, "spans": [], "start_time": datetime.now(timezone.utc).isoformat()}
        return trace_id

    def add_span(self, trace_id: str, span_name: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        if trace_id not in self._traces:
            raise KeyError(f"Trace {trace_id} not found")
        span = {"name": span_name, "metadata": metadata or {}, "timestamp": datetime.now(timezone.utc).isoformat()}
        self._traces[trace_id]["spans"].append(span)
        return span

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        return self._traces.get(trace_id, {})
