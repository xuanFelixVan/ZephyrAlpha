---
module_id: KE-2212------src-zephyr-kb-000
status: active
title: 4.1 代码层（`src/zephyr/kb/`）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4.1 代码层（`src/zephyr/kb/`）

4.1 代码层（`src/zephyr/kb/`）

```
src/zephyr/kb/
├── __init__.py                # 包初始化
├── chromadb_init.py           # ChromaDB 4 Collection 初始化（140行）✅
├── kb_repo.py                 # 核心仓储：10状态机 + SQLite + ChromaDB（422行）✅
├── unified_memory_api.py      # RI-02 统一内存 API：remember/learn/forget/recall（714行）✅
│
├── [G1] ingest.py             # G1 摄取门禁：格式校验 + 输入消毒（266行）✅
├── [G2] triage.py             # G2 分拣门禁：分类 + 评分 + 优先级（372行）✅
├── [G3] analyze.py            # G3 分析门禁：深度评估 + 矛盾检测（314行）✅
├── [G4] activate.py           # G4 激活门禁：INDEXED→VERIFIED + 审计触发（263行）✅
├── [G5] extract.py            # G5 提取门禁：知识提取 + 外部注入（361行）✅
│
├── batch_ingest.py            # 批量入库：Session Log→KE 自动提取（227行）✅
├── reranker.py                # 两阶段检索重排序：Cross-Encoder BGE-reranker-v2-m3（beta 新增）📋
├── graph_validator.py         # 图谱完整性校验：depends_on→DAG→深度≤3（275行）✅
├── embedding_migrate.py       # Embedding 模型迁移管线：升级/降级/回滚（313行）✅
│
└── _future/                   # 4 未来模块（规划中）
    ├── mcp_server_kb.py       # KB MCP Server 独立部署
    ├── query_understanding.py # Query expansion + 查询分解 + jieba分词优化
    ├── memory_consolidation.py# KE聚类 + 知识摘要 + 冗余检测
    └── decay_engine.py        # 知识衰减自动化引擎
    ├── knowledge_decay_engine.py  # 知识衰减自动检测
    └── cross_agent_consistency.py # 跨Agent知识一致性校验
```

> **✅ 表示 experimental 已实现**（12 个 Python 模块，约 3600 行代码）。
