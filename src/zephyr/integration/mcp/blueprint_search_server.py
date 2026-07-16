# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.blueprint_search_server
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.mcp._base_server; zephyr.shared.io.paths
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-013 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
BlueprintSearchServer — MCP Server for blueprint discovery
=============================================================
Task ID  : T-V2-010 (experimental RI-07 — Blueprint Routing MCP Server)
Spec     : MOD-INF-013 §3（MCP Tool 清单）+ MOD-INF-009 §8（蓝图触发路由表）
Protocol : MCP/0.3 (JSON-RPC 2.0 over stdio, ADR-0033)
关联决策  : R90 (蓝图三级金字塔架构) + R91 (MCP 蓝图检索 tool 落地)

This MCP server provides **AI agents** with the capability to discover which
blueprint documents are relevant to the current task—resolving the P0 gap
identified in the PS-STD-005 architecture audit: "AI agent has no way to
know which blueprint to read."

对标
----
Codified Context (arXiv 2602.20478) §3.3.1 Knowledge Retrieval Service:
  find_relevant_context(task) -> queries Tier 3 (Cold Memory) via keyword search

This server extends the pattern from Tier-3 document retrieval to
**blueprint-level** routing: given a task description, it ranks all
19 blueprints by keyword relevance and returns the top candidates.

Usage
-----
::

    python src/zephyr/mcp/blueprint_search_server.py

The server listens on stdio for JSON-RPC 2.0 requests.

Registered Tools
----------------
- ``blueprint_search.find_relevant_blueprint``:
    Input: task_description (str), optional num_results (int, default=5)
    Output: ranked list of {blueprint_id, title, relevance_score, description}
    Source: ``config/blueprint_routing.yaml`` §routes
"""

from __future__ import annotations

from typing import Final
import logging
import time
from typing import Any

import yaml

from zephyr.integration.mcp._base_server import BaseMCPServer
from zephyr.shared.io.paths import REPO_ROOT

__all__ = ["BlueprintSearchServer", "main"]

_logger = logging.getLogger(__name__)

SERVER_ID: Final[str] = "blueprint_search"
SERVER_VERSION: Final[str] = "1.0.0"
SERVER_DESCRIPTION: Final[tuple] = (
    "Blueprint discovery MCP server — finds relevant blueprint documents "
    "for a given task via keyword matching over config/blueprint_routing.yaml. "
    "experimental (T-V2-010)."
)

# ---------------------------------------------------------------------------
# Path resolution（与全仓 SSoT paths 对齐）
# ---------------------------------------------------------------------------

ROUTING_YAML_PATH: Final[Path] = REPO_ROOT / "config" / "blueprint_routing.yaml"
BLUEPRINT_REGISTRY_PATH: Final[Path] = REPO_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------


def _score_routes(
    routes: list[dict[str, Any]],
    task_lower: str,
    include_retired: bool,
) -> list[tuple[int, dict[str, Any]]]:
    scored: list[tuple[int, dict[str, Any]]] = []
    for route in routes:
        if not route.get("enabled", True):
            continue
        if not include_retired and route.get("enabled") is False:
            continue

        keywords: list[str] = route.get("task_keywords", []) or []
        score = 0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in task_lower:
                score += 5
            elif any(word in task_lower for word in kw_lower.split()):
                score += 2

        if score > 0:
            scored.append((score, route))

    return scored


def _build_search_results(
    top_n: list[tuple[int, dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    cross_read_hints: list[str] = []
    for score, route in top_n:
        results.append(
            {
                "blueprint_id": route.get("blueprint_id", ""),
                "blueprint_level": route.get("blueprint_level", "module"),
                "route_id": route.get("route_id", ""),
                "relevance_score": score,
                "priority": route.get("priority", 50),
                "description": route.get("description", ""),
                "path_patterns": route.get("path_patterns", []),
            }
        )
        cross_hint = route.get("cross_read_hint", "")
        if cross_hint:
            cross_read_hints.append(cross_hint)
    return results, cross_read_hints


class BlueprintSearchServer(BaseMCPServer):
    """MCP server for discovering relevant blueprint documents.

    Phase 4 升级：LRU 缓存 + 索引增量更新（关闭 B13）。
    """

    def __init__(self) -> None:
        super().__init__(SERVER_ID, SERVER_VERSION, SERVER_DESCRIPTION)
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._cache_ttl: float = 30.0
        self._index_version: int = 0

        self.register_tool(
            name="blueprint_search.refresh_index",
            description="增量刷新索引——重载 blueprint_routing.yaml + 清空缓存",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._refresh_index,
        )
        self.register_tool(
            name="blueprint_search.find_relevant_blueprint",
            description=(
                "给定任务描述，返回与之最相关的蓝图列表（按相关性排序）。"
                "AI agent MUST 在任务开始前调用此 tool 以确定需要阅读哪些蓝图。"
                "beta 硬合规：G6 门禁强制检查——未读蓝图则代码变更被 REJECT。"
                "对标 Codified Context (arXiv 2602.20478) 的 find_relevant_context MCP tool。"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "任务的自然语言描述（中英文均可）",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "返回的最大蓝图数（默认 3，beta 建议 3-5）",
                        "default": 3,
                    },
                    "include_retired": {
                        "type": "boolean",
                        "description": "是否包含已退役的蓝图（默认 false）",
                        "default": False,
                    },
                },
                "required": ["task_description"],
            },
            handler=self._find_relevant_blueprint,
        )

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    def _find_relevant_blueprint(
        self,
        task_description: str,
        num_results: int = 3,
        include_retired: bool = False,
    ) -> dict[str, Any]:
        """Find blueprints relevant to the given task description.

        Phase 4：LRU 缓存（TTL=30s）。cache_key = (task_description[:80], num_results, include_retired)。
        """
        cache_key = task_description[:80] + str(num_results) + str(include_retired)
        now = time.monotonic()
        cached = self._cache.get(cache_key)
        if cached:
            if (now - cached[0]) < self._cache_ttl:
                result = dict(cached[1])
                result["_cached"] = True
                result["_cache_age_s"] = round(now - cached[0], 2)
                return result
            # 5.65.10 修复：原过期项仅返回miss，不从dict删除；只有手动 _refresh_index() 才 clear()。
            # 读路径发现过期时删除条目，避免过期项堆积导致内存泄漏。
            del self._cache[cache_key]

        routes = self._load_routes()
        if not routes:
            _logger.warning("No routes loaded from %s", ROUTING_YAML_PATH)
            return {"results": [], "count": 0, "source": "blueprint_routing.yaml", "error": "no_routes_loaded"}

        task_lower = task_description.lower()
        scored = _score_routes(routes, task_lower, include_retired)

        scored.sort(key=lambda x: x[0], reverse=True)
        top_n = scored[: max(1, num_results)]

        results, cross_read_hints = _build_search_results(top_n)

        result = {
            "results": results,
            "count": len(results),
            "source": "config/blueprint_routing.yaml",
            "strategy": "keyword_fuzzy_match",
            "phase": "P2_hard_compliance",
            "hint": (
                "beta 硬合规: AI MUST read ALL returned blueprints' §1 (system boundary + topology) "
                "BEFORE any code change. G6 gate will REJECT unverified changes. "
                "Use record_blueprint_read() to register blueprint consumption."
            ),
            "cross_read_hints": cross_read_hints if cross_read_hints else None,
        }

        self._cache[cache_key] = (now, result)
        result["_cached"] = False
        return result

    def _refresh_index(self) -> dict[str, Any]:
        """增量刷新索引——重载路由配置 + 清空缓存。"""
        cache_size = len(self._cache)
        self._cache.clear()
        self._index_version += 1
        routes = self._load_routes()
        return {
            "index_version": self._index_version,
            "routes_count": len(routes),
            "cache_cleared": cache_size,
            "refreshed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_routes(self) -> list[dict[str, Any]]:
        """Load route definitions from blueprint_routing.yaml."""
        if not ROUTING_YAML_PATH.exists():
            _logger.warning("blueprint_routing.yaml not found at %s", ROUTING_YAML_PATH)
            return []

        try:
            with open(ROUTING_YAML_PATH, encoding="utf-8") as fh:
                config = yaml.safe_load(fh)
        except Exception as exc:
            _logger.error("Failed to load blueprint_routing.yaml: %s", exc, exc_info=True)
            return []

        return config.get("routes", [])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the blueprint search MCP server on stdio."""
    import sys as _sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        stream=_sys.stderr,
    )

    server = BlueprintSearchServer()
    server.run()


if __name__ == "__main__":
    main()
