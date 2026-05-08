---
task_id: "TASK-KB-0039"
source_blueprint: "MOD-KB-001"
source_section: "§3.4 KE 索引结构——向量语义 + 标签精确匹配 + FTS5 全文检索"

title: "KE 三路索引检索实现——向量语义检索 + 标签精确匹配 + SQLite FTS5 全文检索"
description: |
  实现蓝图 §3.4 定义的 KE 索引结构——当前仅有 ChromaDB 向量语义检索，蓝图要求三路轮辐式查询模型：
  (1) 向量语义检索（ChromaDB cosine similarity, 384d）——解决"找相似的"；
  (2) 标签精确匹配——按 category/domain/layer/priority 等五轴维度标签做 SQLite WHERE 精确过滤——解决"找某一类"；
  (3) FTS5 全文检索——在 SQLite 建 `knowledge_entries_fts` 虚拟表（索引 title+body+description 三列），支持 BM25 排序和 snippet 高亮——解决"找包含这个关键词的"；
  (4) RRF Reciprocal Rank Fusion 融合三路结果——`RRF(d) = Σ 1/(k + rank_i(d)), k=60`——保证三个维度各占权重（不做 weighted-sum 避免归一化问题）。

  此外必须在统一检索入口 `refine_search()` 构建三路查询并发——类 Metasearch。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\fts_search.py"
    description: "新建——FTS5 虚拟表 CREATE + insert_ke_index() + search_fts(query)→List[ke_id+snippet]"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
    description: "新增 refine_search(query, category=None, priority=None) → 三路并发→RRF fusion→merge top_k"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
    description: "追加 knowledge_entries_fts 表 + insert/update/delete 触发器——KE变更时自动更新FTS索引"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\fts_search.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§3.4 完整描述 KE 索引结构——三路并进 + RRF 融合 + 标签_sync"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "FTS5 虚拟表 knowledge_entries_fts 建在 SQLite 中——content=knowledge_entries——索引 title+body+description"
  - "INSERT/UPDATE/DELETE 触发器——KE变更时自动同步 FTS5 索引"
  - "fts_search.py search_fts(query)→List[FtsResult](ke_id, snippet, bm25_score)"
  - "refine_search() 同时查询 3 个维度——向量ChromaDB + 标签SQLite + FTS查询——RRF k=60 融合"
  - "单路故障(如 FTS5 损坏)→其余两路仍工作并组合RANK——降级非全阻断"
  - "search_tests/ 测试——query='E501'→向量可无但 FTS5 exact-hits"

rollback_instructions: |
  1. 删除 src/zephyr/kb/fts_search.py
  2. git checkout -- src/zephyr/kb/unified_memory_api.py src/zephyr/kb/kb_repo.py
  3. DROP TABLE IF EXISTS knowledge_entries_fts
  4. 若 KE 变更时 FTS 触发器已激活→移除 trigger: DROP TRIGGER tr_ke_fts_insert/update/delete

depends_on: ["TASK-KB-0021"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
