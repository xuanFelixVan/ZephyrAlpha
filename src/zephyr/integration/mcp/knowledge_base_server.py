# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.knowledge_base_server
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.mcp._base_server
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
# [A_module] module_id=MOD-INF-knowledge_base_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""KnowledgeBase MCP Server（MOD-INF-013 §2 Phase 2 skeleton）。

skeleton 实现：6 个工具均返回占位响应。Phase 2 完成后接入 ChromaDB/SQLite。
工具契约 SSoT：src/zephyr/integration/mcp/tool_contracts.yaml §knowledge_base。

暴露工具
--------
- knowledge_base.query        — 跨 collection 语义检索（safety=L）
- knowledge_base.recall       — 时间序召回（safety=L）
- knowledge_base.write        — 写入 KE 条目（safety=H）
- knowledge_base.delete        — 删除 KE 条目（safety=H）
- knowledge_base.reindex      — 重建索引（safety=H）
- knowledge_base.health_check — 健康检查（safety=L）
"""

from __future__ import annotations

import time
from typing import Any, Final

from zephyr.integration.mcp._base_server import BaseMCPServer

__all__ = ["KnowledgeBaseServer", "main"]

_log = None  # lazy logger to avoid import-time side effects

SERVER_ID: Final[str] = "knowledge_base"
SERVER_VERSION: Final[str] = "1.1.0"
SERVER_DESCRIPTION: Final[str] = "知识库语义检索（KE / 规则 / 蓝图 / 失败模式 4 collection）"


class KnowledgeBaseServer(BaseMCPServer):
    """知识库 MCP Server（skeleton）。

    Phase 2 完成后接入 knowledge_indexer.py + ChromaDB。当前返回占位结果，
    满足 Gateway 路由、ACL 校验、tools/list 聚合等契约层测试需求。
    """

    def __init__(self) -> None:
        super().__init__(SERVER_ID, SERVER_VERSION, SERVER_DESCRIPTION)
        self.register_tool(
            name="knowledge_base.query",
            description="跨 collection 语义检索（KE/规则/蓝图/失败模式）",
            input_schema={
                "type": "object",
                "required": ["query_text"],
                "additionalProperties": False,
                "properties": {
                    "query_text": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "collection": {
                        "type": "string",
                        "enum": ["ke_entries", "vibe_rules", "blueprints", "failure_patterns"],
                        "default": "ke_entries",
                    },
                    "n_results": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                },
            },
            handler=self._query,
            safety_level="L",
        )
        self.register_tool(
            name="knowledge_base.recall",
            description="按时间序召回历史 KE 条目",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "since": {"type": "string", "description": "ISO 8601 timestamp"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                },
            },
            handler=self._recall,
            safety_level="L",
        )
        self.register_tool(
            name="knowledge_base.write",
            description="写入新的 KE 条目",
            input_schema={
                "type": "object",
                "required": ["title", "content"],
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string", "minLength": 1},
                    "content": {"type": "string", "minLength": 1},
                    "collection": {"type": "string"},
                },
            },
            handler=self._write,
            safety_level="H",
        )
        self.register_tool(
            name="knowledge_base.delete",
            description="删除指定 KE 条目",
            input_schema={
                "type": "object",
                "required": ["ke_id"],
                "additionalProperties": False,
                "properties": {
                    "ke_id": {"type": "string"},
                },
            },
            handler=self._delete,
            safety_level="H",
        )
        self.register_tool(
            name="knowledge_base.reindex",
            description="重建知识库索引",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "collection": {"type": "string"},
                },
            },
            handler=self._reindex,
            safety_level="H",
        )
        self.register_tool(
            name="knowledge_base.health_check",
            description="知识库健康检查",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._health_check,
            safety_level="L",
        )

    def _query(
        self,
        query_text: str,
        collection: str = "ke_entries",
        n_results: int = 5,
    ) -> dict[str, Any]:
        return {
            "status": "skeleton",
            "query": query_text,
            "collection": collection,
            "hits": [],
            "total_scanned": 0,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _recall(self, since: str = "", limit: int = 20) -> dict[str, Any]:
        return {
            "status": "skeleton",
            "since": since,
            "limit": limit,
            "items": [],
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _write(self, title: str, content: str, collection: str = "ke_entries") -> dict[str, Any]:
        return {
            "status": "skeleton",
            "title": title,
            "collection": collection,
            "written": False,
            "message": "KnowledgeBaseServer skeleton — write not persisted",
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _delete(self, ke_id: str) -> dict[str, Any]:
        return {
            "status": "skeleton",
            "ke_id": ke_id,
            "deleted": False,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _reindex(self, collection: str = "") -> dict[str, Any]:
        return {
            "status": "skeleton",
            "collection": collection,
            "reindexed": False,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _health_check(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "server_id": SERVER_ID,
            "version": SERVER_VERSION,
            "collections": ["ke_entries", "vibe_rules", "blueprints", "failure_patterns"],
            "implementation": "skeleton",
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def main() -> None:
    server = KnowledgeBaseServer()
    server.run()


if __name__ == "__main__":
    main()
