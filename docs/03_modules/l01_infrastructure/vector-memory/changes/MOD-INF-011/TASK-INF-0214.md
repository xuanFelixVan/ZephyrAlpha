---
task_id: "TASK-INF-0214"
source_blueprint: "MOD-INF-011"
source_section: "§12.3 Phase 1：基础设施对齐"

title: "Phase 1 基础设施对齐——6 模块全功能集成 + BridgeLayer 双读启用"
description: |
  执行蓝图 §12.3 Phase 1 的基础设施对齐施工——将 Phase 0 已完成 TASK-INF-0201~0212 产生的基础设施模块全功能集成：
  1. ProvenanceEnforcer 可校验 WriteTrace（§10.3 R10/R12 + §6.1 契约 #4）
  2. EmbeddingRouter 可按 Collection 路由到不同模型 + 降级链正常（§3.1 + §10.2 R2）
  3. BridgeLayer 可同时检索 kb/ 和 VMS（§5.2 + §10.4 R14）：启动双读模式 + 测试双读数据一致性
  4. ChunkStrategyRouter 6 种分块策略全部启用（§2.1 原则 #3）
  5. CacheLayer：Embedding memoization 持续命中 + 查询结果 LRU 缓存（§3 技术选型）
  6. IndexHealthMonitor：detect_drift() + integrity_check() 运行正常（§10.1 R0 + §10.2 R4）
  Phase 1 产出：D:\ZephyrAlpha\src\zephyr\vector_memory\ 下 6 个模块文件的全功能集成 + 集成测试通过
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\chunk_strategy_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "Phase 1 集成版——InProcessVectorMemory.search() / put() / health() 全功能启用 + 6 子模块全部 initialized"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"
    description: "Phase 1 集成测试——provenance_validation / embedding_routing / bridge_dual_read / chunk_strategy / cache_hit / health_detect_drift"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\chunk_strategy_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\provenance_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\cache_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——所有测试 payload 类型"
  - module_id: "GOV-TASK-005"
    section: "全篇"
    reason: "任务关闭三步法——Phase 1 完成验收依据"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§12.3 Phase 1 定义——6 模块的验收标准 + G7 检查项 + 蓝图契约对齐"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "ProvenanceEnforcer 可校验 WriteTrace——validate() 对合法 provenance 返回 True，对缺失 origin 返回 False"
  - "EmbeddingRouter 可按 Collection 路由到不同模型——rules→1024d / blueprints→512d"
  - "BridgeLayer 可同时检索 kb/ 和 VMS——search_both() 返回合并去重结果"
  - "BridgeLayer 双读测试通过——kb/ 和 VMS 查询结果的 NDCG@5 差异 ≤ 10%"
  - "ChunkStrategyRouter 6 种策略均可路由——text 无默认 fallback 统一策略"
  - "CacheLayer embedding memoization 命中时返回缓存向量——round-trip 延迟 < 1ms"
  - "IndexHealthMonitor detect_drift() 运行成功——输出 DriftReport"
  - "InProcessVectorMemory 启动时 6 子模块全部 initialized——无 import error"
  - "蓝图漂移自检通过——启动日志无 drift warning"

rollback_instructions: |
  1. 每个模块可独立降级——设置 VMS_MODULE_{NAME}=disabled 环境变量跳过初始化
  2. 还原 InProcessVectorMemory.__init__() 至 TASK-INF-0213 完成后的版本
  3. 还原 tests/unit/test_vector_memory.py 至 Phase 1 之前的版本
  4. Phase 1 失败不阻止后续 Phase 独立进行——Phase 1 模块用 skip 降级

depends_on:
  - "TASK-INF-0202"
  - "TASK-INF-0204"
  - "TASK-INF-0205"
  - "TASK-INF-0207"
  - "TASK-INF-0208"
  - "TASK-INF-0209"
  - "TASK-INF-0212"
  - "TASK-INF-0213"
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
