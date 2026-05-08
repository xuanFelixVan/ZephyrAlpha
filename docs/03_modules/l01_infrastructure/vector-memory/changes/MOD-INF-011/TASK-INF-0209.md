---
task_id: "TASK-INF-0209"
source_blueprint: "MOD-INF-011"
source_section: "§6.1 模块接口契约"

title: "模块接口契约落地——全部 7 条接口契约的 Python Protocol/ABC 实现"
description: |
  实现蓝图 §6.1 定义的 7 条核心模块接口契约：
  1. CollectionManager: create_collection(name, dim, chunk_strategy, ttl) / migrate_collection(from, to) / archive_collection(name)
  2. EmbeddingRouter: embed(text, collection_name) → ndarray
  3. HybridRetriever: search(query, collection, k) → list[ScoredHit]（含 timeout_ms 参数 + RetrievalTrace）
  4. ProvenanceEnforcer: validate(WriteTrace) → bool / attach(vector_id, provenance)
  5. IndexHealthMonitor: check_all() → HealthReport / auto_repair(collection)
  6. RetrievalFeedback: record(hit_id, was_useful: bool, task_id)
  7. CacheLayer: get_embedding(text_hash) → ndarray | None / put_embedding(text_hash, vec)
  使用 Pydantic V2 BaseModel 定义返回值类型：ScoredHit / HealthReport / RetrievalTrace / Chunk / WriteTrace
  创建 shared 数据模型文件 vms_schemas.py。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vms_schemas.py"
    description: "VMS 共享数据模型——ScoredHit / HealthReport / RetrievalTrace / Chunk / WriteTrace / CollectionMetadata（全部 Pydantic V2 BaseModel）"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
    description: "追加 validate() / attach() 实现——基于 WriteTrace 模型的 CBAC 校验逻辑"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
    description: "追加 check_all() → HealthReport 实现"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
    description: "追加 get_embedding() / put_embedding() 实现"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vms_schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2 BaseModel——禁止 dataclass"
  - module_id: "PS-STD-001"
    section: "§7.1"
    reason: "TaskCard 语义 28 字段——与 vms_schemas 无冲突验证"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§6.1 接口契约表——7 条接口的完整签名 + 调用方 + 返回值定义"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    reason: "Task 基类模型——WriteTrace 继承和 CBAC 字段参考"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "vms_schemas.py 定义 ScoredHit: content/score/score_breakdown/why_top/metadata/provenance/partial"
  - "vms_schemas.py 定义 HealthReport: collection_name/status/issue_count/recommendations/last_check"
  - "vms_schemas.py 定义 RetrievalTrace: query/hits/source_collection/rerank_info/embedding_model_version"
  - "vms_schemas.py 定义 Chunk: text/start_pos/end_pos/overlap_with_prev/overlap_with_next"
  - "vms_schemas.py 定义 WriteTrace: origin/audit_chain/arbitration/content_hash/timestamp"
  - "vms_schemas.py 定义 CollectionMetadata: name/dimension/embedding_model/chunk_strategy/ttl_days/ai_autonomy_level"
  - "ProvenanceEnforcer.validate(WriteTrace) 验证 origin 非空 + audit_chain 完整 + arbitration 有效"
  - "IndexHealthMonitor.check_all() 返回 8 个 Collection 的 HealthReport 列表"
  - "CacheLayer.get_embedding(text_hash) 在缓存命中时返回 ndarray，miss 时返回 None"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\vector_memory\vms_schemas.py
  2. 还原 provenance_enforcer.py / index_health_monitor.py / cache_layer.py 至 TASK-INF-0208 的骨架状态
  3. 检查 InProcessVectorMemory 和其他模块是否有对 vms_schemas 的 import——如有则移除

depends_on:
  - "TASK-INF-0202"
  - "TASK-INF-0204"
  - "TASK-INF-0206"
  - "TASK-INF-0208"
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
