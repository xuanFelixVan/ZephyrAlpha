# [A_module] module_id=MOD-INT_vector_memory | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md
# [TTL] permanent
"""Vector Memory Service (VMS) — MOD-INF-011 · v0.7.0
=============================================================

    全系统统一向量记忆体 — 可审计 · 可自愈 · 可持续

八大 Collection
--------------
┌──────────────────────┬──────────┬─────────────────────┬───────────┐
│ Collection            │ 嵌入维度  │ 分块策略              │ AI自治级别  │
├──────────────────────┼──────────┼─────────────────────┼───────────┤
│ decisions             │ 1024d    │ semantic 500-800tk    │ supervised │
│ code_context          │ 1024d    │ AST-aware func/class  │ autonomous │
│ lessons               │ 1024d    │ paragraph 300-500tk   │ autonomous │
│ knowledge             │ 1024d    │ heading-aware 500-800 │ supervised │
│ rules                 │ 1024d    │ rule-level 整条存储    │ human-gated│
│ blueprints            │  512d    │ section-aware 按§拆分  │ supervised │
│ session_snapshots     │  512d    │ session-level 单摘要   │ autonomous │
│ execution_traces      │  512d    │ time-window 1min窗口   │ autonomous │
└──────────────────────┴──────────┴─────────────────────┴───────────┘

双嵌入维度
----------
  · BGE-M3 ONNX 1024d — 主嵌入模型，精度优先（decisions/lessons/knowledge/rules/code_context）
  · bge-small-zh-v1.5 512d — 轻量嵌入模型，吞吐优先（blueprints/session_snapshots/execution_traces）

四 Phase 施工规划（蓝图 §4）
-----------------------------
  · Phase 0 — 蓝图-SSoT 重建 ······ ✅ 完成
  · Phase 1 — 基础设施对齐（6模块） ·· ✅ 完成
  · Phase 2 — 8 Collection 落地+迁移 ·· ✅ 完成
  · Phase 3 — 检索质量闭环 ·········· ✅ 完成
  · Phase 4 — 运维自动化 ············· 📋 backlog

基础设施
--------
  存储      : ChromaDB 0.6 PersistentClient (SQLite + HNSW)
  数据目录   : data/vector_db/
  模型缓存   : models/bge-m3/  +  models/bge-small-zh-v1.5/
  嵌入缓存   : data/vector_db/_embedding_cache/
  索引快照   : data/vector_db/_snapshots/

蓝图真源  : docs/03_modules/_domain_knowledge/vector_memory/blueprint.md v0.7.0
SSoT     : architecture_model/layers/b_vector_memory.yaml
ADR      : ADR-0019(FLE单向依赖) + ADR-0031(ChromaDB选型) + ADR-0016(BGE-M3嵌入契约)
审计     : 四轮80盲点全覆盖（R1:33/R2:22/R3:19/R4:6）— 蓝图纸面~95-96/100
"""

from __future__ import annotations

from zephyr.gov_kb.unified_memory_api import UnifiedMemoryAPI, get_unified_memory_api
from zephyr.integration.vector_memory.delegated_vector_memory import UnifiedVectorMemoryAdapter
from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory
from zephyr.integration.vector_memory.interface import (
    EmbeddingEngineBase,
    MemoryEntry,
    VectorMemoryBase,
)
from zephyr.integration.vector_memory.ollama_embedding import OllamaEmbedder
from zephyr.integration.vector_memory.vector_bridge import VectorBridge

__all__ = [
    "EmbeddingEngineBase",
    "InProcessVectorMemory",
    "MemoryEntry",
    "UnifiedMemoryAPI",
    "UnifiedVectorMemoryAdapter",
    "VectorBridge",
    "VectorMemoryBase",
    "bm25_index",
    "bridge_layer",
    "cache_layer",
    "chunk_strategy_router",
    "collection_manager",
    "collection_schemas",
    "cross_collection_retriever",
    "delegated_vector_memory",
    "design_principles",
    "embedding_router",
    "faiss_collection_manager",
    "get_unified_memory_api",
    "hybrid_retriever",
    "in_memory_fake_vms",
    "in_memory_memory_backend",
    "in_process_vector_memory",
    "index_health_monitor",
    "interface",
    "migrate_chroma_to_faiss",
    "ollama_chat",
    "ollama_embedding",
    "provenance_enforcer",
    "retrieval_feedback",
    "sqlite_metadata_store",
    "vector_bridge",
    "vms_errors",
    "vms_schemas",
'context_ingest', 'vector_writer']
