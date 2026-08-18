# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md
# [MODULE] zephyr.integration
# [DOMAIN] D_INTEGRATION
# [A_module] module_id=MOD-INF-042 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable  # noqa: blueprint-amodule-cross-check [BLUEPRINT]==[A_module] same module
# [TTL] permanent
"""D_INTEGRATION 集成域包入口。

子域蓝图归属（各子域以其蓝图为准）：
- mcp/               → MOD-INF-013（model_context_protocol_servers）
- vector_memory/     → MOD-INF-011（VMS）
- local_model/       → MOD-INF-042（Local Model）
- behavioral_admission / budget_enforcer / shared / pipeline_orchestrator / ports → D_INTEGRATION 域内组件

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求
#   fields: import zephyr.integration（消费者拿门面符号与子模块命名空间）
#   code: L15-16 from-import + __all__
# 层: 算法
# - id: A1
#   name_zh: 门面再导出
#   name_en: facade_reexport
#   intro: 无业务逻辑——LLMBridge/get_asset_summary 顶层再导出，__all__ 声明子模块全集
# 层: 输出
# - id: O1
#   name_zh: 包门面符号
#   name_en: facade_symbols
#   intro: LLMBridge / get_asset_summary + 12 个子模块命名空间
#   downstream: D_INTEGRATION 全部消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
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
    "preemption_manager",
    "routing_plugins",
    "shared",
    "vector_memory",
]
