---
task_id: "TASK-KB-0021"
source_blueprint: "MOD-KB-001"
source_section: "§7.5 SQLite Schema 16表+UPSERT语义 + §7.6 三层同步机制(File↔SQLite↔ChromaDB)"

title: "SQLite Schema 验证与增强——16表UPSERT语义 + 三层同步File→SQLite→ChromaDB + §7.6.5决策一致性检查"
description: |
  验证并增强蓝图 §7.5 定义的 SQLite 16张表：(1)对 knowledge_entries 表的 28 列 schema 进行对照审计（确认MTH-001 frozen字段 MTH-007 adopt_count MTH-008 新增列 alignment）；(2)对于 UPSERT 语义(INSERT OR REPLACE)的表(knowledge_entries/kb_rules/metadata)确保 id+version 双主键正确 + AUTO UPDATE 触发器+stale 标记；(3)实现 §7.6 三层同步——File↔SQLite↔ChromaDB file→SQLite 加载(不重复)、SQLite→ChromaDB 索引(按status)、ChromaDB→SQLite 逆向同步(missing标记stale)；(4)§7.6.5 决策一致性检查——decision_consistency_checker 苏醒193个ADR变更→A/B判KE stale+schema_version bump→推送Owner YOU DECIDE update/archive/skip。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\sync_manager.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
    description: "修改——UPSERT 语义 INSERT OR REPLACE + AUTO UPDATE 触发器+stale 标记——修正 knowledge_entries/kb_rules/metadata 三表"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\sync_manager.py"
    description: "新建——三层同步核心 File↔SQLite↔ChromaDB——push_sync/pull_sync/validate_sync/repair_orphans"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decision_consistency_checker.py"
    description: "新建——苏醒193个ADR变更→A/B判 KE stale→schema_version bump→推送Owner——绑定 §7.6.5 + Sentinel 3"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
    description: "修改——追加 scan_ghost_ke() 幽灵向量清扫(§7.4.1) + chromadb_health_check() 红绿灯探测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\embedding_migrate.py"
    description: "修改——Embedding 模型迁移 SOP(§7.4.2)：新模型注册表 schema + 渐进式迁移(migrate_5pct→validate→migrate_all) + revert_migration 回滚"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\sync_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decision_consistency_checker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\embedding_migrate.py"
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
    reason: "§7.5 SQLite Schema + §7.6 三层同步 + §7.6.5 决策一致性检查"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "knowledge_entries/kb_rules/metadata 三表使用 INSERT OR REPLACE + id+version 双主键"
  - "show tables → 16张表清单完整"
  - "sync_manager.py push_sync(file→SQLite) 不重复插入同一KE"
  - "sync_manager.py push_sync(SQLite→ChromaDB) 仅推送 status≥INDEXED 的KE"
  - "sync_manager.py validate_sync 三类一致性对比→返回 drift 报告"
  - "decision_consistency_checker 代替 manual watchdog——自动探测ADR变更→KE stale→推Owner裁决"
  - "sync_manager.py chromadb_health_check(ke_entries_collection)→返回 (healthy:bool, latency_ms, error)——失败重试3次→仍失败→ACTIVATE BM25 fallback"
  - "unified_memory_api.recall() ChromaDB returns empty→自动降级 BM25 FTS5 召回——LOG WARN 'ChromaDB unhealthy, falling back to BM25'"
  - "sync_manager.py scan_ghost_ke()——weekly cron 对比 SQLite vs ChromaDB ID——发现 ghost→修复: ChromaDB.delete(ghost_ids) + SQLite mark stale"
  - "chromadb_init.py——追加 scan_ghost_ke() 幽灵向量清扫(§7.4.1 col.count() vs SQLite 差异>5%→告警) + chromadb_health_check() 红绿灯探测"
  - "embedding_migrate.py——model_registry schema + migrate_5pct()→validate_5pct()→migrate_all()→revert_migration() 完整SOP"

rollback_instructions: |
  1. git checkout -- src/zephyr/kb/kb_repo.py
  2. git checkout -- src/zephyr/kb/chromadb_init.py
  3. git checkout -- src/zephyr/kb/embedding_migrate.py
  4. 删除 src/zephyr/kb/sync_manager.py, decision_consistency_checker.py
  5. SQLite 若表结构已变更→用备份的 kb_state.db 覆盖 data/sqlite/kb_state.db

depends_on: ["TASK-KB-0011"]
blocked_by: []
status: "done"
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
