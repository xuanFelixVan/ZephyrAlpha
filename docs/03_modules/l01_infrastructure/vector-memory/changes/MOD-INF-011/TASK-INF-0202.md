---
task_id: "TASK-INF-0202"
source_blueprint: "MOD-INF-011"
source_section: "§2 八大 Collection Schema"

title: "8 Collection Schema 实现——CollectionManager 创建/写入/检索/删除全生命周期"
description: |
  实现 CollectionManager 对蓝图 §2 定义的八大 Collection 的全生命周期管理。
  八大 Collection Schema：
  1. decisions（写入方:Orchestrator, 读取方:CE+FLE, 1024d BGE-M3, semantic 500-800 token chunker, permanent TTL, 预估 1000-5000 条）
  2. code_context（写入方:Script System+Orc, 读取方:CE, 1024d BGE-M3, AST-aware function/class chunker, 90d TTL, 预估 500-2000 条）
  3. lessons（写入方:FLE+Script System, 读取方:CE+KB, 1024d BGE-M3, paragraph 300-500 token chunker, permanent TTL, 预估 100-500 条, 继承自 failure_patterns）
  4. knowledge（写入方:KB, 读取方:CE, 1024d BGE-M3, heading-aware 500-800 token chunker, permanent TTL, 预估 100-1000 条, 继承自 ke_entries）
  5. rules（写入方:Governance, 读取方:CE+Orc, 1024d BGE-M3, rule-level 整条存储, permanent TTL, 预估 200-500 条, 继承自 vibe_rules, AI 自治级别 human-gated）
  6. blueprints（写入方:Doc System, 读取方:CE+Orc, 512d bge-small, section-aware 按§拆分, permanent TTL, 预估 10000-30000 条, 继承自 blueprints）
  7. session_snapshots（写入方:SessionManager, 读取方:CE, 512d bge-small, session-level 单摘要, 90d TTL, 预估 50-200 条, 新建）
  8. execution_traces（写入方:All systems, 读取方:FLE+CE, 512d bge-small, time-window 1min窗口, 30d TTL, 预估 1000-5000 条, 新建, 替代 runtime_logs）
  每个 Collection 创建时绑定 embedding_model / chunk_strategy / TTL / AI 自治级别元数据。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
    description: "CollectionManager 类——create_collection(name, dim, chunk_strategy, ttl, ai_autonomy_level) / migrate_collection(from, to) / archive_collection(name) / get_collection(name) / list_collections()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "InProcessVectorMemory 统一入口——集成 CollectionManager 作为子模块"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"

applicable_rules:
  - module_id: "ADR-0031"
    section: "§4.2"
    reason: "ChromaDB 基线选型——CollectionManager 基于 ChromaDB PersistentClient"
  - module_id: "ADR-0016"
    section: "§3"
    reason: "BGE-M3 生产级嵌入与分块契约——1024d 嵌入真源"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——Collection 元数据模型"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§2 八大 Collection Schema 完整定义——维度/TTL/分块策略/自治级别绝对真源"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
    reason: "现有 ChromaDB PersistentClient + 4+1 Collection 创建/重置/状态查询（幂等）——实现参考"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
    reason: "WriteTrace 三件套(recall/write/search) + CBAC 集成——CollectionManager 写入溯源参考"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "CollectionManager.create_collection('decisions', dim=1024, chunk_strategy='semantic', ttl_days=0) 成功创建并配置 metadata"
  - "CollectionManager.create_collection('code_context', dim=1024, chunk_strategy='ast_aware', ttl_days=90) 成功创建"
  - "CollectionManager.create_collection('lessons', dim=1024, chunk_strategy='paragraph', ttl_days=0) 成功创建"
  - "CollectionManager.create_collection('knowledge', dim=1024, chunk_strategy='heading_aware', ttl_days=0) 成功创建"
  - "CollectionManager.create_collection('rules', dim=1024, chunk_strategy='rule_level', ttl_days=0, ai_autonomy='human-gated') 成功创建"
  - "CollectionManager.create_collection('blueprints', dim=512, chunk_strategy='section_aware', ttl_days=0) 成功创建"
  - "CollectionManager.create_collection('session_snapshots', dim=512, chunk_strategy='session_level', ttl_days=90) 成功创建"
  - "CollectionManager.create_collection('execution_traces', dim=512, chunk_strategy='time_window', ttl_days=30) 成功创建"
  - "CollectionManager.list_collections() 返回 8 个 Collection 完整元数据"
  - "每个 Collection 的 metadata 包含 embedding_model、dimension、chunk_strategy、ttl_days、ai_autonomy_level"
  - "create_collection 幂等——对已存在 Collection 重复调用不抛异常且不重复创建"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\vector_memory\collection_manager.py
  2. 从 D:\ZephyrAlpha\src\zephyr\vector_memory\in_process_vector_memory.py 移除 CollectionManager 集成代码（如已添加）
  3. 删除 D:\ZephyrAlpha\data\vector_db\ 下由测试创建的 ChromaDB 数据文件（删除 *.sqlite3 文件，保留目录结构）
  4. 如果 InProcessVectorMemory 创建了 ChromaDB PersistentClient 实例——确保该实例已正确关闭

depends_on:
  - "TASK-INF-0201"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "data"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
