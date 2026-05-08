---
task_id: "TASK-INF-0215"
source_blueprint: "MOD-INF-011"
source_section: "§12.3 Phase 2：8 Collection 落地"

title: "Phase 2 施工——8 Collection 落地 + 4 旧 Collection 数据迁移 + 迁移后验证"
description: |
  执行蓝图 §12.3 Phase 2 的 8 Collection 落地施工：
  1. 迁移顺序严格遵守蓝图定义：
     a. 先建 rules / blueprints / knowledge / lessons——从现有 Collection 迁移数据（含重嵌入升级）
     b. 再建 decisions / code_context / session_snapshots / execution_traces——全新创建
     c. BridgeLayer 双读期间（Phase 2-3 过渡）保持兼容
     d. 迁移完成后冻结 kb/chromadb_init.py（标记 deprecated，不再新增写入）
  2. 迁移数据操作：
     - ke_entries → knowledge: 迁移 + 重命名 + 重嵌入至 1024d
     - vibe_rules → rules: 迁移 + 重命名 + 强制重嵌入至 1024d
     - blueprints → blueprints: 保留 512d + 仅重命名
     - failure_patterns → lessons: 迁移 + 重命名 + 重嵌入至 1024d
     - unified_memory → 按 topic 拆分到对应 Collection（先 dry-run）
  3. 验证：8 个 Collection 可创建/写入/检索/删除 + 迁移 4 旧 Collection 数据无损 + Collection Schema 与蓝图 §2 一致 + 嵌入维度正确 + WriteTrace 每条都有
  4. 产出 InProcessVectorMemory 统一入口
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_migration_dry_run.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "Phase 2 全功能版——8 Collection 全部 created + 旧数据已迁移 + search/put 路由到 8 Collection"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
    description: "冻结标记——文件顶部追加 '# DEPRECATED: This file is frozen as of MOD-INF-011 Phase 2. All new data goes to VMS.'"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_phase2_migration.py"
    description: "Phase 2 迁移执行脚本——按顺序迁移 4+1 旧 Collection → 8 VMS Collection + 验证数据无损"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"
    description: "Phase 2 迁移集成测试——迁移前后 NDCG@5 比较 + 数据无损验证 + 维度校验"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_phase2_migration.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_vector_memory.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"

applicable_rules:
  - module_id: "ADR-0031"
    section: "全篇"
    reason: "Phase 2 ChromaDB 基线——迁移操作基于现有 kb/ ChromaDB 数据"
  - module_id: "ADR-0016"
    section: "§3"
    reason: "BGE-M3 嵌入规范——重嵌入至 1024d 的模型配置"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§12.3 Phase 2 定义——8 Collection 落地 + 迁移顺序 + 验收标准 + G7 检查项"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
    reason: "现有 Collection 数据源——迁移前必须确认当前数据状态"
  - file_path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_migration_dry_run.py"
    reason: "dry-run 输出——正式迁移前 Owner 审核用"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
  - "M4"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "8 个 Collection 全部创建成功——collection_manager.list_collections() 返回 8 条记录"
  - "rules Collection 数据从 vibe_rules 迁移完毕——42 条 rules 全部重嵌入至 1024d"
  - "knowledge Collection 数据从 ke_entries 迁移完毕——所有 KE 条目重嵌入至 1024d"
  - "lessons Collection 数据从 failure_patterns 迁移完毕——所有失败模式重嵌入至 1024d"
  - "blueprints Collection 从 blueprints 迁移完毕——保留 512d + 仅重命名"
  - "unified_memory 按 topic 拆分正确——每条记录路由到正确的目标 Collection"
  - "decisions / code_context / session_snapshots / execution_traces 全新创建——为空初始状态"
  - "迁移前后 NDCG@5 差异 ≤ 10%——数据无损验证通过"
  - "每个 Collection 的 WriteTrace 完整——provenance_enforcer 全员通过"
  - "kb/chromadb_init.py 已标记 DEPRECATED——不再允许新数据写入"
  - "BridgeLayer 双读期间 CE 可同时访问新旧 Collection——不中断现有服务"

rollback_instructions: |
  1. 迁移后数据损坏 → 从 kb/ 旧 Collection 重新迁移—BridgeLayer 回退到仅读 kb/
  2. kb/chromadb_init.py 可以取消冻结——移除 DEPRECATED 标记即可恢复写入能力
  3. 删除 VMS 8 Collection 中的错误数据 → collection_manager.archive_collection() → 重新迁移
  4. 如果 unified_memory topic 拆分错误 → 手动修正映射表 → 重新执行拆分
  5. 从 snapshot 恢复整个 ChromaDB 数据——TASK-INF-0212 的 vms_snapshot_backup.py

depends_on:
  - "TASK-INF-0214"
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
