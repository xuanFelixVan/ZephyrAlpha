---
module_id: KE-2334--------vms-006
status: active
title: 6. 架构分层——VMS 内部模块分解
category: module_blueprint
---

# 6. 架构分层——VMS 内部模块分解

6. 架构分层——VMS 内部模块分解

```
InProcessVectorMemory (统一入口)
├── CollectionManager        ← 8 Collection 生命周期（create/migrate/archive）
│   ├── decisions            ← 1024d BGE-M3, semantic chunker
│   ├── code_context         ← 1024d BGE-M3, AST-aware chunker
│   ├── lessons              ← 1024d BGE-M3, paragraph chunker (← failure_patterns)
│   ├── knowledge            ← 1024d BGE-M3, heading-aware chunker (← ke_entries)
│   ├── rules                ← 1024d BGE-M3, rule-level (← vibe_rules)
│   ├── blueprints           ← 512d bge-small, section-aware (← blueprints)
│   ├── session_snapshots    ← 512d bge-small, session-level
│   └── execution_traces     ← 512d bge-small, time-window
├── EmbeddingRouter          ← 双模型路由 (§3.1)
├── ChunkStrategyRouter      ← 分块策略调度 (§2.1)
├── HybridRetriever          ← Vector + BM25 + RRF (§3.2)
├── ProvenanceEnforcer       ← WriteTrace 强制 + CBAC 集成 (§1)
├── IndexHealthMonitor       ← 自检 + 自动修复 + 告警
├── RetrievalFeedback        ← FLE 检索质量信号消费
├── CacheLayer               ← Embedding memoization + 查询结果 LRU
├── BridgeLayer              ← 与现有 kb/ 4 Collection 双向桥接 (§5.2)
├── VectorBridge             ← CE/KB 外部集成适配器 (§8)
└── InMemoryMemoryBackend    ← ChromaDB 不可用时的降级兜底
```
