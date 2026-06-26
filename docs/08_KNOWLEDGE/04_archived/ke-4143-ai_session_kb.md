---
module_id: KE-3988--------ai-session----kb-001
title: 2.1 必读文档（新 AI session 接手 KB 模块时按此顺序）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 必读文档（新 AI session 接手 KB 模块时按此顺序）

2.1 必读文档（新 AI session 接手 KB 模块时按此顺序）

| # | 文件 | 说明 |
|---|------|------|
| 1 | 本文件 `knowledge-base/blueprint.md` | KB 系统唯一真源蓝图 |
| 2 | `src/zephyr/kb/kb_repo.py` | 核心仓储——10状态机 + SQLite + ChromaDB |
| 3 | `src/zephyr/kb/unified_memory_api.py` | RI-02 统一内存 API——remember/learn/forget/recall |
| 4 | `src/zephyr/kb/chromadb_init.py` | ChromaDB 4 Collection 初始化 |
| 5 | `architecture_model/layers/b_kb.yaml` | 架构 YAML SSoT——KB 模块登记 |
| 6 | MOD-TASK_SYSTEM `task-system/blueprint.md` | 任务系统——KB 施工任务追踪格式 |
