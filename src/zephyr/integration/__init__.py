# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md
# [MODULE] zephyr.integration
# [DOMAIN] D_INTEGRATION
# [A_module] module_id=MOD-INTEGRATION | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_INTEGRATION 集成域包入口。

子域蓝图归属（各子域以其蓝图为准）：
- mcp/               → MOD-INF-013（model_context_protocol_servers）
- vector_memory/     → MOD-INF-011（VMS）
- local_model/       → MOD-INF-042（Local Model）
- behavioral_admission / budget_enforcer / shared / pipeline_orchestrator / ports → D_INTEGRATION 域内组件
"""

from zephyr.integration.llm_bridge import LLMBridge
from zephyr.integration.mcp_server import get_asset_summary

__all__ = [
    "LLMBridge",
    "behavioral_admission",
    "budget_enforcer",
    "get_asset_summary",
    "llm_bridge",
    "local_model",
    "mcp",
    "mcp_server",
    "pipeline_orchestrator",
    "ports",
    "shared",
    "vector_memory",
]
