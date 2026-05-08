---
task_id: "TASK-INF-0208"
source_blueprint: "MOD-INF-011"
source_section: "§6 架构分层——VMS 内部模块分解 + §5.3 VMS 目标代码文件"

title: "架构分层落地——InProcessVectorMemory 统一入口 + 11 子模块组装 + 全部待建文件骨架"
description: |
  实现蓝图 §6 定义的 VMS 内部模块分解架构和 §5.3 定义的全部 12 个待建源码文件的骨架创建：
  1. InProcessVectorMemory 统一入口单例——编排 11 个子模块的初始化 + 生命周期管理 + 统一对外 API
  2. CollectionManager（§2 + TASK-INF-0202）
  3. EmbeddingRouter（§3.1 + TASK-INF-0204/0205）
  4. ChunkStrategyRouter——分块策略调度（AST-aware / heading-aware / time-window / section-aware / semantic / paragraph）
  5. HybridRetriever（§3.2 + TASK-INF-0206）
  6. ProvenanceEnforcer——WriteTrace 强制 + CBAC 集成
  7. IndexHealthMonitor——自检 + 自动修复 + 告警
  8. RetrievalFeedback——FLE 检索质量信号消费
  9. CacheLayer——Embedding memoization + 查询结果 LRU
  10. BridgeLayer（§5.2 + TASK-INF-0207）
  11. VectorBridge——CE/KB 外部集成适配器
  12. InMemoryMemoryBackend——ChromaDB 不可用时的降级兜底
  13. CrossCollectionRetriever——跨 Collection 联合检索（Phase 3）
  创建全部 12 个 .py 骨架文件（含类声明、方法签名、docstring）+ tests/unit/test_vector_memory.py
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\__init__.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "InProcessVectorMemory 单例——VMS.__init__() 编排 11 子模块 + search() / put() / health() / close() 公共 API"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\chunk_strategy_router.py"
    description: "ChunkStrategyRouter 类——route(text, strategy) → list[Chunk] + 支持 6 种策略"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
    description: "ProvenanceEnforcer 类——validate(WriteTrace) → bool / attach(vector_id, provenance)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
    description: "IndexHealthMonitor 类——check_all() → HealthReport / auto_repair(collection) / detect_drift() / schedule_maintenance()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
    description: "CacheLayer 类——get_embedding(text_hash) / put_embedding(text_hash, vec) / invalidate_all() / Collection 级缓存策略"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vector_bridge.py"
    description: "VectorBridge 类——CE集成适配器（search_for_ce()）+ KB同步写入（sync_knowledge()）"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
    description: "RetrievalFeedback 类——record(hit_id, was_useful, task_id) / get_feedback_stats(collection)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cross_collection_retriever.py"
    description: "CrossCollectionRetriever 类——search_across(query, collections, k) → 跨 Collection 联合检索 + 结果合并排序"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"
    description: "单元测试骨架——pytest fixtures + FakeVMS + 8 Collection 创建/写入/检索测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\chunk_strategy_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vector_bridge.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cross_collection_retriever.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2 BaseModel——所有模块的数据类"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径映射——源码 src/zephyr/vector_memory/ + 测试 tests/unit/"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§6 架构分层树状图 + §5.3 完整待建文件清单——所有模块名称/职责/接口定义真源"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 15000
timeout_minutes: 45

acceptance_criteria:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\ 下存在 12 个 .py 文件（含 __init__.py）"
  - "in_process_vector_memory.py 包含 InProcessVectorMemory 类——def __init__(self, config) + def search() + def put() + def health() + def close()"
  - "chunk_strategy_router.py 包含 ChunkStrategyRouter 类——def route(text, strategy) → list[Chunk]"
  - "provenance_enforcer.py 包含 ProvenanceEnforcer 类——def validate(WriteTrace) → bool"
  - "index_health_monitor.py 包含 IndexHealthMonitor 类——def check_all() → HealthReport"
  - "cache_layer.py 包含 CacheLayer 类——def get_embedding(text_hash) / def put_embedding(text_hash, vec)"
  - "vector_bridge.py 包含 VectorBridge 类——def search_for_ce(query, k) / def sync_knowledge(ke_id)"
  - "retrieval_feedback.py 包含 RetrievalFeedback 类——def record(hit_id, was_useful, task_id)"
  - "cross_collection_retriever.py 包含 CrossCollectionRetriever 类——def search_across(query, collections, k)"
  - "tests/unit/test_vector_memory.py 存在 pytest fixture 骨架"
  - "每个 .py 文件有完整的 module docstring——说明模块职责和对应蓝图节号"

rollback_instructions: |
  1. 逐个删除 TASK-INF-0208 创建的 9 个新 .py 文件 + test_vector_memory.py
  2. 保留 TASK-INF-0202/0204/0205/0206/0207 创建的已实现模块文件
  3. 确保 InProcessVectorMemory.__init__() 中移除对已删除模块的导入引用

depends_on:
  - "TASK-INF-0202"
  - "TASK-INF-0204"
  - "TASK-INF-0205"
  - "TASK-INF-0206"
  - "TASK-INF-0207"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
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
