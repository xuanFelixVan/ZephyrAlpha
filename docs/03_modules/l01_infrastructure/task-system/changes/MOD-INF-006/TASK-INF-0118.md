---
task_id: "TASK-INF-0118"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #32 + 盲点 #42"

title: "实现 SQLite Schema 版本化迁移框架"
description: |
  SQLite Schema 版本化——migration 表记录版本 + 版本间迁移脚本。
  自动化向前迁移——task_repo 启动时检查 schema_version 并自动升级。
  回滚支持——支持向后迁移到上一版本。
  Schema 校验——启动时验证表结构是否符合预期。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\data\\tasks.db"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\shared\migration.py"
    description: "SchemaMigration——版本检测 + 升级 + 回滚 + 校验"
  - path: "D:\\ZephyrAlpha\\data\\migrations\\001_initial.sql"
    description: "初始 Schema 迁移脚本"
  - path: "D:\\ZephyrAlpha\\data\\migrations\\002_add_v0_6_0_fields.sql"
    description: "v0.6.0 字段追加迁移脚本"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\migrations.py"
  - "D:\\ZephyrAlpha\\data\\migrations\\001_initial.sql"
  - "D:\\ZephyrAlpha\\data\\migrations\\002_add_v0_6_0_fields.sql"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\data\\tasks.db"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #32"
    reason: "Schema 迁移——版本检测+自动升级+回滚"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #32 + 盲点 #42"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M4"
estimated_tokens: 10000
timeout_minutes: 30

acceptance_criteria:
  - "task_repo 启动时自动检测 schema_version 并升级"
  - "migration 表存在——含 version/applied_at 列"
  - "支持回滚——降级到上一版本"
  - "Schema 校验通过——表/列匹配预期"

rollback_instructions: |
  1. 删除 migrations.py 和 .sql 迁移脚本
  2. 恢复 task_repo.py 到无迁移的版本

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "db"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 实现 SQLite Schema 版本化迁移框架

## 目标

1. Schema 版本化——migration 表
2. 自动化向前迁移
3. 回滚支持
4. Schema 校验

## 触发条件

- TASK-INF-0102 完成
- data/tasks.db 存在

## 执行步骤

### 做
1. 实现 SchemaMigration 类
2. 编写初始迁移脚本 + v0.6.0 迁移脚本
3. 集成到 task_repo 初始化流程

### 产
- migrations.py + 2 个 .sql 文件

### 检
```python
from zephyr.db.migrations import SchemaMigration
mig = SchemaMigration("D:/ZephyrAlpha/data/tasks.db")
mig.upgrade()
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | 迁移执行成功 |
| 2 | test | 升级/回滚/校验 均有测试 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 数据丢失——升级失败导致 | 升级前备份 tasks.db 到 tasks.db.bak |
