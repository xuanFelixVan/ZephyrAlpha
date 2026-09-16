# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure/asset_inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.mcp_server
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.asset_inventory.__init__
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
# [A_module] module_id=MOD-INF-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AssetInventory MCP Server — MOD-INF-026 蓝图 §21

2 tool + 1 resource 暴露盘点功能给 IDE AI agent。
通过 FastMCP 协议。

2026-09-06 宽口径 v2 收敛（Owner 批二 ③ 派生面处置）：
  - dashboard.json/reconciliation-report.md/classified-assets.json 三派生物退役
    （零活消费方，内容停在 2026-08-16 窄口径）；get_health_dashboard 改读索引
    health/orphan_risk/summary。
  - get_asset_detail/search_asset_by_type/tag/layer、list_all_tags、
    list_registry_ids 六工具随窄口径 assets[] 数组退役——宽口径 v2 索引为计数
    聚合 schema，无明细数组，工具语义不可实现（零生产挂载实证，rg dispatch_tool
    零调用方）。

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/asset_inventory/mcp_server.yaml
"""

import json
import logging
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

INDEX_PATH = REPO_ROOT / "data" / "asset_index" / "unified-asset-index.yaml"

try:
    import yaml

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def _load_index() -> dict[str, Any] | None:
    if not INDEX_PATH.exists():
        return None
    if _HAS_YAML:
        return yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8"))
    return None


def get_asset_summary() -> str:
    """资产总览（宽口径 v2 schema：total_assets/health/orphan_risk/by_category）。"""
    index = _load_index()
    if not index:
        return json.dumps({"error": "unified-asset-index.yaml not found — run generate_asset_index.py first"})

    return json.dumps(
        {
            "total_assets": index.get("total_assets"),
            "health": index.get("health"),
            "orphan_risk": index.get("orphan_risk"),
            "modules": index.get("modules"),
            "by_category": index.get("by_category"),
            "by_directory": index.get("by_directory"),
            "summary": index.get("summary"),
            "generated_at": index.get("generated_at"),
        },
        ensure_ascii=False,
        indent=2,
    )


def get_health_dashboard() -> str:
    """健康面板——读索引 health/orphan_risk/summary（2026-09-06 起不再读已退役的 dashboard.json）。"""
    index = _load_index()
    if not index:
        return json.dumps({"error": "unified-asset-index.yaml not found — run generate_asset_index.py first"})

    return json.dumps(
        {
            "health": index.get("health"),
            "orphan_risk": index.get("orphan_risk"),
            "summary": index.get("summary"),
            "generated_at": index.get("generated_at"),
        },
        ensure_ascii=False,
        indent=2,
    )


MCP_TOOLS = {
    "get_asset_summary": {
        "description": "获取项目资产盘点总览（宽口径 v2）：总数、健康度、孤儿风险、按类型/目录分布",
        "function": get_asset_summary,
    },
    "get_health_dashboard": {
        "description": "获取健康面板——健康评分/等级、孤儿风险与摘要（真源 unified-asset-index.yaml）",
        "function": get_health_dashboard,
    },
}

MCP_RESOURCES = {
    "asset_index://unified": {
        "description": "统一的资产索引 YAML 文件——项目 SSoT（单一事实来源）",
        "path": str(INDEX_PATH),
    },
}


def dispatch_tool(name: str, **kwargs: str) -> str:
    tool = MCP_TOOLS.get(name)
    if not tool:
        return json.dumps({"error": f"unknown tool: {name}", "available": list(MCP_TOOLS)})

    func = tool["function"]
    try:
        if kwargs:
            return func(**kwargs)
        return func()
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.exception("MCP tool '%s' failed", name, exc_info=True)
        return json.dumps({"error": "internal error"})


def list_tools() -> list[dict[str, str]]:
    return [{"name": k, "description": v["description"]} for k, v in MCP_TOOLS.items()]


def list_resources() -> list[dict[str, str]]:
    return [{"name": k, "description": v["description"], "path": v["path"]} for k, v in MCP_RESOURCES.items()]
