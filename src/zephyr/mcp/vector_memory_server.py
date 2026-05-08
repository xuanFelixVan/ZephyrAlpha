"""
VectorMemoryServer: VMS 向量记忆 MCP Server (MOD-INF-011 v0.7.0)
==================================================================
Server   : vector_memory (tool_contracts.yaml Server 9)
Protocol : ADR-0033（JSON-RPC 2.0 over stdio / process-inline）
Backend  : InProcessVectorMemory (11子模块 + 8 Collection + HybridRetriever)

实现工具
--------
- vector_memory.search           — 语义检索 (HybridRetriever → EmbeddingRouter)
- vector_memory.write            — 写入记忆 (provenance强制)
- vector_memory.recall           — 时间序召回
- vector_memory.list_collections — 列举8 Collection
- vector_memory.health_check     — 全景健康检查
"""

from __future__ import annotations

from typing import Any

from zephyr.mcp._base_server import BaseMCPServer

__all__ = ["VectorMemoryServer", "create_server"]

VMS_COLLECTION_NAMES = [
    "decisions", "code_context", "lessons", "knowledge",
    "rules", "blueprints", "session_snapshots", "execution_traces",
]


class VectorMemoryServer(BaseMCPServer):
    SERVER_ID = "vector_memory"
    VERSION = "1.0.0"
    DESCRIPTION = "全系统统一向量记忆体 — 8 Collection + HybridRetriever(Vector+BM25+RRF)"

    def __init__(self, *, enable_rbac: bool = True) -> None:
        super().__init__(self.SERVER_ID, self.VERSION, self.DESCRIPTION, enable_rbac=enable_rbac)
        self._vms: Any = None
        self._init_vms()

        self.register_tool(
            name="vector_memory.search",
            description="语义检索——HybridRetriever(Vector+BM25+RRF) → EmbeddingRouter 双模型降级，跨8 Collection",
            input_schema={
                "type": "object",
                "required": ["collection_name", "query"],
                "additionalProperties": False,
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "enum": VMS_COLLECTION_NAMES,
                    },
                    "query": {"type": "string", "minLength": 1},
                    "k": {"type": "integer", "minimum": 1, "maximum": 50, "default": 5},
                },
            },
            handler=self._search,
            safety_level="L",
        )

        self.register_tool(
            name="vector_memory.write",
            description="写入向量记忆——强制 provenance（origin/audit_chain/arbitration）",
            input_schema={
                "type": "object",
                "required": ["collection_name", "content"],
                "additionalProperties": False,
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "enum": VMS_COLLECTION_NAMES,
                    },
                    "content": {"type": "string", "minLength": 1},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string"},
                            "audit_chain": {"type": "array", "items": {"type": "string"}},
                            "arbitration": {"type": "string"},
                        },
                    },
                },
            },
            handler=self._write,
            safety_level="H",
        )

        self.register_tool(
            name="vector_memory.recall",
            description="按时间倒序召回最近K条记录（不做语义相似度）",
            input_schema={
                "type": "object",
                "required": ["collection_name"],
                "additionalProperties": False,
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "enum": VMS_COLLECTION_NAMES,
                    },
                    "k": {"type": "integer", "minimum": 1, "maximum": 100, "default": 5},
                },
            },
            handler=self._recall,
            safety_level="L",
        )

        self.register_tool(
            name="vector_memory.list_collections",
            description="列出全部8个 Collection 的元信息（维度/分块策略/AI自治级别/是否存在）",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._list_collections,
            safety_level="L",
        )

        self.register_tool(
            name="vector_memory.health_check",
            description="VMS 全景健康检查——Collections/Embedding/Index 三维诊断 + 漂移检测",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._health_check,
            safety_level="L",
        )

    def _init_vms(self) -> None:
        try:
            from zephyr.vector_memory.in_process_vector_memory import InProcessVectorMemory

            self._vms = InProcessVectorMemory()
            self._vms.init_all_collections()
            self._vms.start()
        except Exception:
            self._vms = None

    def _search(self, collection_name: str, query: str, k: int = 5) -> dict[str, Any]:
        if self._vms is None:
            return {"error": "VMS 未就绪", "hits": []}
        hits = self._vms.search(collection_name, query, k=k)
        return {"hits": hits, "collection": collection_name, "query": query}

    def _write(self, collection_name: str, content: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._vms is None:
            return {"error": "VMS 未就绪", "written": False}
        from zephyr.vector_memory.collection_manager import COLLECTION_SCHEMAS

        schema = COLLECTION_SCHEMAS.get(collection_name, {})
        if schema.get("ai_autonomy_level") == "human-gated":
            return {
                "error": f"Collection '{collection_name}' 为 human-gated，拒绝 AI 写入",
                "written": False,
            }
        try:
            doc_id = self._vms.write(collection_name, content, metadata=metadata)
            return {"doc_id": doc_id, "collection": collection_name, "written": True}
        except Exception as e:
            return {"error": str(e), "written": False}

    def _recall(self, collection_name: str, k: int = 5) -> dict[str, Any]:
        if self._vms is None:
            return {"error": "VMS 未就绪", "records": []}
        records = self._vms.recall(collection_name, k=k)
        return {"records": records, "collection": collection_name}

    def _list_collections(self) -> dict[str, Any]:
        if self._vms is None:
            return {"collections": [], "error": "VMS 未就绪"}
        infos = self._vms.list_collections()
        return {
            "collections": [
                {
                    "name": c.name,
                    "dimension": c.dimension,
                    "chunk_strategy": c.chunk_strategy,
                    "ttl_days": c.ttl_days,
                    "ai_autonomy_level": c.ai_autonomy_level,
                    "embedding_model": c.embedding_model,
                    "exists": c.exists,
                }
                for c in infos
            ]
        }

    def _health_check(self) -> dict[str, Any]:
        if self._vms is None:
            return {"status": "unhealthy", "error": "VMS 未就绪"}
        return self._vms.health_check()


def create_server() -> VectorMemoryServer:
    return VectorMemoryServer()
