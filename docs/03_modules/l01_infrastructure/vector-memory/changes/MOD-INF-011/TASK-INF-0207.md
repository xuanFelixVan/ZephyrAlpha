---
task_id: "TASK-INF-0207"
source_blueprint: "MOD-INF-011"
source_section: "§5 已实现代码完整路径索引 + §5.1 源码文件 + §5.2 过渡期 Collection 映射"

title: "代码路径索引导航与 kb/→VMS 过渡桥接——BridgeLayer + 迁移路线图"
description: |
  实现蓝图 §5 定义的"代码地址簿"导航能力和 kb/→VMS 过渡桥接基础设施：
  1. 从蓝图 §5.1 确认 kb/ 现有代码状态：chromadb_init.py（4+1 Collection）+ unified_memory_api.py（WriteTrace 三件套）+ vector_memory/__init__.py（skeleton）
  2. 从蓝图 §5.2 确认过渡期 Collection 映射：ke_entries→knowledge / vibe_rules→rules / blueprints→blueprints / failure_patterns→lessons / unified_memory→按 topic 拆分
  3. 实现 BridgeLayer（§6）：与现有 kb/ 4+1 Collection 双向桥接——Phase 1-2 过渡期同时检索 kb/ 和 VMS Collection
  4. BridgeLayer 路径澄清：kb/ 过渡期路径 `.audit_cache/vector_index/`（shared/paths.py 集中管理）→ VMS 投产路径 `data/vector_db/` → BridgeLayer 负责读取旧路径写入新路径
  5. 迁移完成后 `.audit_cache/vector_index/` 归档保留 30 天作为回滚保险
  6. 创建迁移 dry-run 脚本（R15 缓解）：输出 unified_memory topic → target Collection 映射表
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\paths.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
    description: "BridgeLayer 类——search_both(query, collection, k) → 同时检索 kb/ 和 VMS + 结果合并/去重 / migrate_collection(from_kb, to_vms) / dry_run_topic_split()"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_migration_dry_run.py"
    description: "迁移 dry-run 脚本——解析 unified_memory topic → 输出 topic→Collection 映射表（供 Owner 审核）"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_migration_dry_run.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\paths.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"

applicable_rules:
  - module_id: "ADR-0031"
    section: "§4.2"
    reason: "kb/ 现有 ChromaDB 路径与实现依据"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "迁移脚本路径合规——scripts/governance/ 目录"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§5 代码路径索引 + §5.2 过渡期 Collection 映射表——路径/模型/维度/迁移操作完整定义"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
    reason: "现有 Collection 创建代码——BridgeLayer 需要知道 kb/ 已有哪些 Collection"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
    reason: "VMS 目标 Collection——BridgeLayer 写入目标"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "BridgeLayer.search_both('test', 'knowledge', k=5) 同时检索 kb/ke_entries 和 VMS/knowledge → 合并去重返回"
  - "BridgeLayer.migrate_collection('ke_entries', 'knowledge') 从 kb/ 读取数据 → 写入 VMS/knowledge（含重嵌入至 1024d）"
  - "BridgeLayer.migrate_collection('vibe_rules', 'rules') 强制重嵌入至 1024d（治理级精度要求）"
  - "BridgeLayer.migrate_collection('failure_patterns', 'lessons') 迁移 + 重嵌入至 1024d"
  - "BridgeLayer.migrate_collection('blueprints', 'blueprints') 保留 512d + 仅重命名"
  - "vms_migration_dry_run.py 输出 topic→Collection 映射表——Owner 审核通过后才能正式迁移"
  - "迁移完成后 old `.audit_cache/vector_index/` 数据归档保留——不物理删除"
  - "BridgeLayer 支持从旧路径 `.audit_cache/vector_index/` 读取 PersistentClient"

rollback_instructions: |
  1. 如果迁移导致数据损坏 → 从 `.audit_cache/vector_index/` 重新读取 kb/ 旧 Collection 数据→重新迁移
  2. 回退 BridgeLayer 到仅读 kb/ 模式——设置 BRIDGE_MODE=kb_only 环境变量
  3. 删除 VMS target Collection 中已迁移的错误数据——通过 archive_collection() 然后重新 create_collection()
  4. 如果 dry-run 脚本结果错误 → Owner 手动审查 topic→Collection 映射表并修正

depends_on:
  - "TASK-INF-0202"
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
