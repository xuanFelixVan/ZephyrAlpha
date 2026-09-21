# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4.5
# [MODULE] zephyr.library.collectors.mcp_collector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.schema
# [CONSUMERS] zephyr.library.collectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读两真源（config/mcp.json + tool_contracts.yaml）；契约与注册双向差异直接入 tags（漂移现行自动化）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一真源缺失折叠为 [{"error": ...}]
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""mcp_collector — MCP server/工具采集器（契约 SSOT + 注册配置双向核对）。

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/mcp_collector.yaml
"""

import json
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.library.ledger_schema import derive_asset_id

__all__ = ["collect"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

_CONTRACTS = "src/zephyr/integration/mcp/tool_contracts.yaml"
_MCP_JSON = "config/mcp.json"


def _server_tools(contracts: dict[str, Any]) -> dict[str, int]:
    """从契约 SSOT 统计每 server 的 tool 数（兼容多种布局）。"""
    out: dict[str, int] = {}
    for key, value in contracts.items():
        if isinstance(value, dict) and value:
            out[key] = sum(1 for v in value.values() if isinstance(v, (dict, list)))
    return out


def collect() -> list[dict[str, Any]]:
    """枚举 MCP server，产出 TOOL: 资产（带契约/注册双向差异标签）。

        Returns:
            资产字典列表；真源缺失折叠为 [{"error": ...}]。

    # [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/mcp_collector.yaml
    """
    try:
        contracts = yaml.safe_load(Path(_CONTRACTS).read_text(encoding="utf-8")) or {}
        mcp_conf = json.loads(Path(_MCP_JSON).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — fail-soft
        return [{"error": f"{type(exc).__name__}: {exc}"}]
    tool_counts = _server_tools(contracts)
    registered = set(mcp_conf.get("servers", mcp_conf).keys()) if isinstance(mcp_conf, dict) else set()
    contract_servers = set(tool_counts) | {k for k in contracts if isinstance(contracts.get(k), dict)}
    on_disk = {p.stem for p in Path("src/zephyr/integration/mcp").glob("*_server.py")}
    all_servers = sorted(contract_servers | registered | on_disk)
    out: list[dict[str, Any]] = []
    for server in all_servers:
        if not server:
            continue
        tags = ["mcp"]
        if server not in registered:
            tags.append("未注册_mcp.json")
        if server not in contracts:
            tags.append("无契约")
        out.append(
            {
                "asset_id": derive_asset_id("mcp_tool", f"mcp:{server}"),
                "kind": "mcp_tool",
                "home": f"mcp:{server}",
                "fingerprint_sha256": None,
                "fingerprint_aux": {"tools": tool_counts.get(server, 0)},
                "title": server,
                "ai_contract": None,
                "owner_domain": None,
                "tags": tags,
            }
        )
    return out
