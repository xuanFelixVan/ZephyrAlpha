# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] zephyr.integration.mcp_server
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.infrastructure.asset_inventory.mcp_server
# [CONSUMERS] zephyr.integration.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AssetInventory MCP Server 兼容 shim — MOD-INF-026 蓝图 §21

真源唯一（SSoT）：实现已收敛至 ``zephyr.infrastructure.asset_inventory.mcp_server``
（与 asset_inventory 包 scanner/index_generator 等同域共置）。
本模块仅作 ``zephyr.integration`` 包的公共导入路径兼容层，全部符号再导出自真源，
禁止在此新增/修改实现。

2026-09-06 宽口径 v2 收敛：get_asset_detail/search_asset_by_type/tag/layer、
list_all_tags、list_registry_ids、DASHBOARD_PATH 随窄口径 assets[] 派生面退役
移出再导出（真源已删，详见 mcp_server.py 模块头注）。
"""

from typing import Final

from zephyr.infrastructure.asset_inventory.mcp_server import (  # noqa: F401
    INDEX_PATH,
    MCP_RESOURCES,
    MCP_TOOLS,
    SCAN_PATH,
    dispatch_tool,
    get_asset_summary,
    get_health_dashboard,
    list_resources,
    list_tools,
)

__all__: Final = [
    "INDEX_PATH",
    "MCP_RESOURCES",
    "MCP_TOOLS",
    "SCAN_PATH",
    "dispatch_tool",
    "get_asset_summary",
    "get_health_dashboard",
    "list_resources",
    "list_tools",
]
