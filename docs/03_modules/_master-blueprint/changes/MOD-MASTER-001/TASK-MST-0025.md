---
task_id: "TASK-MST-0025"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §二十六 零停机滚动升级——CT-DEPLOY-001 + §二十七 DB Schema演化——CT-SCHEMA-MIGRATE-001"

title: "实现零停机滚动升级 + 数据库 Schema 演化契约"
description: |
  实现 §二十六 CT-DEPLOY-001 零停机滚动升级 + §二十七 CT-SCHEMA-MIGRATE-001 SQLite表结构演化。
  升级策略：(1)blue_green(CE/VMS/Pipeline/Gates)——新版本备用端口→ready→FeatureFlag切换→drain 30s；
  (2)rolling_replace(Orc/Script/FLE/Telemetry/DB)——暂停 IN_PROGRESS→重启→readyz→恢复 60s；
  (3)hot_reload(MCP/LSG)——reload config+re-init 无需重启。
  Pre-deploy: CT-HEALTH/CT-CDC(Can-I-Deploy)/CT-BACKUP/FeatureFlag/DLQ 5项检查。
  Post-deploy: CT-HEALTH 3次确认/CT-BENCH <10%/FLE 10min观察窗口。
  自动回滚触发: readyz 503连续3次 /FLE检测 PERFORMANCE_DEGRADATION / 错误率>基线2x 5min。
  Schema Migration: V{SEQ}__{description}.sql——每条UP有对应DOWN/migration chain CI校验连续。
  Breaking change safety: GATE-MIGRATE-1——BREAKING migration需Owner审批+30天consumer通知。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\startup_sequencer.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\deploy_manager.py"
    description: "零停机部署管理器——CT-DEPLOY-001——3策略+pre/post+auto rollback"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\schema_migration.py"
    description: "Schema迁移管理器——CT-SCHEMA-MIGRATE-001——UP/DOWN+chain validate+GATE-MIGRATE-1"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_deploy_manager.py"
    description: "部署管理器单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_schema_migration.py"
    description: "Schema迁移管理器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\deploy_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\schema_migration.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_deploy_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_schema_migration.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§二十六——CT-DEPLOY-001 + §二十七——CT-SCHEMA-MIGRATE-001 完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "deploy_manager.py 实现 3 种升级策略(blue_green/rolling_replace/hot_reload)对应不同系统组"
  - "pre_deploy: 5项检查(CT-HEALTH/CT-CDC/CT-BACKUP/FeatureFlag/DLQ)→任一项FAIL→停止"
  - "post_deploy: 3次readyz 200+CT-BENCH<10%退化+FLE 10min观察"
  - "auto rollback: readyz 503连续3次/FLE DEGRADATION/错误率>2x 5min"
  - "schema_migration.py 支持 UP/DOWN migration + CI chain validate连续+GATE-MIGRATE-1 BREAKING审批"
  - "新增column MUST有DEFAULT值 / 修改column type→BREAKING→2版本过渡 / 删除column→BREAKING→deprecation流程"
  - "CI 对比 db.schema_migrations 与 migrations/ 目录 → 不一致→FAIL"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\deploy_manager.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\schema_migration.py
  3. 删除新增的测试文件
  4. 如有创建的 migrations/ 目录 → 备份后删除

depends_on: ["TASK-MST-0013", "TASK-MST-0015"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
