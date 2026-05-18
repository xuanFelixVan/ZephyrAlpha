---

skill_id: SKILL-DOM-VMS-001
name: vector-memory
description: "Vector Memory Service — ChromaDB 8-collection vector store with BGE-M3 ONNX embeddings"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Vector Memory Specialist

## CRITICAL Rules

1. VMS is the PRIMARY system-wide vector memory backend (MOD-INF-011, blueprint v0.7.0)
2. All vector operations MUST go through `InProcessVectorMemory` — NEVER use raw ChromaDB client directly
3. **MCP Entry**: Use MCP tools `vector_memory.search` / `vector_memory.write` / `vector_memory.recall` / `vector_memory.list_collections` / `vector_memory.health_check` — these are the canonical AI→VMS interface
4. Provenance metadata (origin/audit_chain/arbitration) is MANDATORY on every `write()`
5. Collection names are STRICT — only the 8 defined collections (decisions/code_context/lessons/knowledge/rules/blueprints/session_snapshots/execution_traces)
6. KB module's `chromadb_init.py` (4 legacy collections) is superseded by VMS — use `VectorBridge` for KB↔VMS sync

## Core Operations

- Vector storage and retrieval via InProcessVectorMemory
- Semantic search with HybridRetriever (Vector + BM25 + RRF fusion)
- Embedding generation via EmbeddingRouter (BGE-M3 ONNX 1024d / bge-small 384d)
- Collection lifecycle management (create/list/health_check) via CollectionManager
- Provenance enforcement — every write traceable to origin/audit_chain
- KB↔VMS bridging via VectorBridge (sync_knowledge, sync_rules, write_decision, etc.)
- Index health monitoring with auto-repair capability
- Chunk strategy routing (semantic/AST-aware/paragraph/heading/rule/section/session/time-window)

## Unique Constraints

- 8 Collections with different embedding dimensions and AI autonomy levels:
  - decisions/lessons/knowledge/rules/code_context: BGE-M3 1024d
  - blueprints/session_snapshots/execution_traces: bge-small 512d
- AI autonomy: supervised → autonomous → human-gated (varies by collection)
- Embedding cache: memoization via CacheLayer for frequently embedded texts
- Degraded mode: InMemoryMemoryBackend fallback when ChromaDB unavailable
- TTL support: per-collection configurable TTL (ttl_days), default 0 (no expiry)

## Common Error Patterns

- ImportNotFound for InProcessVectorMemory → check vector_memory/__init__.py exports
- Collection not found → verify 8 canonical collection names, use list_collections()
- Provenance validation failure → ensure metadata has origin/audit_chain/arbitration fields
- Embedding dimension mismatch → verify collection was created with correct dim (1024 vs 512)
- ChromaDB telemetry noise → VMS.start() disables telemetry env vars automatically

## Checklist

- [ ] Verify VMS is started (call .start() before write/search)
- [ ] Check collection exists before write (init_all_collections if needed)
- [ ] Include provenance metadata on every write
- [ ] Use appropriate chunk strategy for content type
- [ ] Run health_check() before bulk operations
- [ ] Sync KB knowledge to VMS via VectorBridge after KE creation

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| COLLECTION_COUNT | 8 | Number of VMS collections |
| BGE_M3_DIM | 1024 | Primary embedding dimension |
| BGE_SMALL_DIM | 512 | Lightweight embedding dimension |
| DEFAULT_CHUNK_SIZE | 512 | Default text chunk size (tokens) |
| DEFAULT_OVERLAP | 64 | Default chunk overlap (tokens) |
| MAX_WORKERS | 8 | ThreadPoolExecutor workers for batch ops |
| PERSIST_DIR | data/vector_db/ | ChromaDB persistence directory |

## References (L3, on-demand)

- Blueprint: docs/03_modules/l01_infrastructure/vector-memory/blueprint.md v0.7.0
- Interface: docs/03_modules/_b_track_interfaces/vector-memory-service-interface.md
- SSoT: architecture-model/layers/b_vector_memory.yaml
- Unit tests: tests/unit/vector_memory/test_vector_memory.py (23 tests)
- Adversarial: tests/adversarial/test_cross_layer_systems_red_team.py (7 VMS tests)
- ADRs: ADR-0016 (BGE-M3 embedding contract), ADR-0031 (ChromaDB selection)