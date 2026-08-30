# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.agent_observability
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
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""




MOD-INF-019: Agent Spec — Agent Observability
Blueprint: docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
Author: factory-agent
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: agent_observability.py
# 层: 算法
# - id: A1
#   name_zh: ① AgentObservability
#   name_en: AgentObservability
#   intro: Agent Trace 全链路可观测性
#   desc: Agent Trace 全链路可观测性；公共方法（定义序）: traces, traces, start_trace, add_span, get_trace；源码 L58-L88
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AgentObservability
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import UTC, datetime
from typing import Any


class AgentObservability:
    """Agent Trace 全链路可观测性"""

    def __init__(self):
        self._traces: dict[str, dict[str, Any]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def traces(self) -> dict[str, dict[str, Any]]:
        """只读：traces（Stage 4 公共化）。"""
        return self._traces

    @traces.setter
    def traces(self, value):
        """写入：traces（Stage 4 公共化）。"""
        self._traces = value

    def start_trace(self, skill_id: str) -> str:
        trace_id = f"trace-{skill_id}-{datetime.now(UTC).timestamp()}"
        self._traces[trace_id] = {"skill_id": skill_id, "spans": [], "start_time": datetime.now(UTC).isoformat()}
        return trace_id

    def add_span(self, trace_id: str, span_name: str, metadata: dict[str, Any] = None) -> dict[str, Any]:
        if trace_id not in self._traces:
            raise KeyError("Trace not found")
        span = {"name": span_name, "metadata": metadata or {}, "timestamp": datetime.now(UTC).isoformat()}
        self._traces[trace_id]["spans"].append(span)
        return span

    def get_trace(self, trace_id: str) -> dict[str, Any]:
        return self._traces.get(trace_id, {})
