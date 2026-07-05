# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
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
# [A_module] module_id=MOD-INF_mcp_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AssetInventory MCP Server — MOD-INF-026 蓝图 §21

8 tool + 2 resource 暴露盘点功能给 IDE AI agent。
通过 FastMCP 协议。
"""

import json
import logging
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

INDEX_PATH = REPO_ROOT / "data" / "asset_index" / "unified-asset-index.yaml"
DASHBOARD_PATH = REPO_ROOT / "data" / "reports" / "dashboard.json"
SCAN_PATH = REPO_ROOT / "data" / "scans" / "raw-asset-scan.json"

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


def _load_dashboard() -> dict[str, Any] | None:
    if not DASHBOARD_PATH.exists():
        return None
    return json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))


def get_asset_summary() -> str:
    index = _load_index()
    if not index:
        return json.dumps({"error": "unified-asset-index.yaml not found — run index_generator first"})

    return json.dumps(
        {
            "total_assets": index.get("total_assets"),
            "health_score": index.get("health_score"),
            "orphan_rate_pct": index.get("orphan_rate_pct"),
            "ghost_rate_pct": index.get("ghost_rate_pct"),
            "drift_rate_pct": index.get("drift_rate_pct"),
            "by_type": index.get("by_type"),
            "by_layer": index.get("by_layer"),
            "by_status": index.get("by_status"),
        },
        ensure_ascii=False,
        indent=2,
    )


def get_asset_detail(path: str) -> str:
    index = _load_index()
    if not index:
        return json.dumps({"error": "index not found"})

    for asset in index.get("assets", []):
        if isinstance(asset, dict) and asset.get("relative_path") == path:
            return json.dumps(asset, ensure_ascii=False, indent=2)
    return json.dumps({"error": f"asset not found: {path}"})


def search_asset_by_type(asset_type: str, limit: int = 50) -> str:
    index = _load_index()
    if not index:
        return json.dumps({"error": "index not found"})

    matches = [a for a in index.get("assets", []) if isinstance(a, dict) and a.get("asset_type") == asset_type][:limit]
    return json.dumps(matches, ensure_ascii=False, indent=2)


def search_asset_by_tag(tag: str, limit: int = 50) -> str:
    index = _load_index()
    if not index:
        return json.dumps({"error": "index not found"})

    matches = [a for a in index.get("assets", []) if isinstance(a, dict) and tag in a.get("tags", [])][:limit]
    return json.dumps(matches, ensure_ascii=False, indent=2)


def search_asset_by_layer(layer: str, limit: int = 50) -> str:
    index = _load_index()
    if not index:
        return json.dumps({"error": "index not found"})

    matches = [a for a in index.get("assets", []) if isinstance(a, dict) and a.get("layer") == layer][:limit]
    return json.dumps(matches, ensure_ascii=False, indent=2)


def list_all_tags() -> str:
    index = _load_index()
    if not index:
        return json.dumps({"error": "index not found"})

    tag_counts: dict[str, int] = {}
    for a in index.get("assets", []):
        if isinstance(a, dict):
            for t in a.get("tags", []):
                tag_counts[t] = tag_counts.get(t, 0) + 1

    return json.dumps(
        sorted(tag_counts.items(), key=lambda x: (-x[1], x[0])),
        ensure_ascii=False,
        indent=2,
    )


def get_health_dashboard() -> str:
    dash = _load_dashboard()
    if not dash:
        return json.dumps({"error": "dashboard.json not found — run dashboard generator first"})
    return json.dumps(dash, ensure_ascii=False, indent=2)


def list_registry_ids() -> str:
    index = _load_index()
    if not index:
        return json.dumps({"error": "index not found"})

    reg_ids: dict[str, int] = {}
    for a in index.get("assets", []):
        if isinstance(a, dict):
            for rid in a.get("registered_in", []):
                reg_ids[rid] = reg_ids.get(rid, 0) + 1

    return json.dumps(
        sorted(reg_ids.items(), key=lambda x: (-x[1], x[0])),
        ensure_ascii=False,
        indent=2,
    )


MCP_TOOLS = {
    "get_asset_summary": {
        "description": "获取项目资产盘点总览：总数、健康评分、孤儿率/幽灵率/漂移率、按类型/层级/状态分布",
        "function": get_asset_summary,
    },
    "get_asset_detail": {
        "description": "查询单个资产的详细信息：类型、层级、状态、大小、SHA-256、注册表引用",
        "function": get_asset_detail,
        "params": {"path": "str (required) — 资产相对路径如 'src/zephyr/asset-inventory/scanner.py'"},
    },
    "search_asset_by_type": {
        "description": "按资产类型搜索所有资产（module/script/gate/doc/config/test/data/registry）",
        "function": search_asset_by_type,
        "params": {"asset_type": "str (required)", "limit": "int (default=50)"},
    },
    "search_asset_by_tag": {
        "description": "按自定义标签搜索资产——找出所有标记为某标签的文件",
        "function": search_asset_by_tag,
        "params": {"tag": "str (required)", "limit": "int (default=50)"},
    },
    "search_asset_by_layer": {
        "description": "按项目层级搜索资产（L00~L04 / cross_layer）",
        "function": search_asset_by_layer,
        "params": {"layer": "str (required)", "limit": "int (default=50)"},
    },
    "list_all_tags": {
        "description": "列出项目所有被使用的标签及其出现次数",
        "function": list_all_tags,
    },
    "get_health_dashboard": {
        "description": "获取健康仪表盘——最新健康评分、趋势数据和告警",
        "function": get_health_dashboard,
    },
    "list_registry_ids": {
        "description": "列出所有资产注册表ID及其登记资产数量",
        "function": list_registry_ids,
    },
}

MCP_RESOURCES = {
    "asset_index://unified": {
        "description": "统一的资产索引 YAML 文件——项目 SSoT（单一事实来源）",
        "path": str(INDEX_PATH),
    },
    "asset_index://dashboard": {
        "description": "健康仪表盘 JSON 文件——当前健康状态 + 趋势 + 告警",
        "path": str(DASHBOARD_PATH),
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
    except Exception as exc:
        logger.exception("MCP tool '%s' failed", name, exc_info=True)
        return json.dumps({"error": "internal error"})


def list_tools() -> list[dict[str, str]]:
    return [{"name": k, "description": v["description"]} for k, v in MCP_TOOLS.items()]


def list_resources() -> list[dict[str, str]]:
    return [{"name": k, "description": v["description"], "path": v["path"]} for k, v in MCP_RESOURCES.items()]