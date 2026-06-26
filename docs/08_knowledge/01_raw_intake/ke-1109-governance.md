---
module_id: KE-1024
status: active
title: 8. 完整示例
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 8. 完整示例

8. 完整示例

```yaml
task_id: SRC-042
title: 实现 SQLite 任务仓库 CRUD + 10 状态机
phase: implement
status: PENDING
priority: P1
execution_model: claude-sonnet-4.6
model_rationale: Sonnet 擅长结构化代码编写且便宜，本任务涉及 3 个文件修改，无需 Opus 架构推理
safety_level: M
classification: public
evolution_policy: rewritable
estimate_hours: 2.5
files_in_scope:
  - D:\ZephyrAlpha\src\zephyr\shared\schemas.py
  - D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py
  - D:\ZephyrAlpha\src\zephyr\db\task_repo.py
  - D:\ZephyrAlpha\src\zephyr\cli\task_cli.py
deliverables:
  - D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py
  - D:\ZephyrAlpha\src\zephyr\db\task_repo.py
  - D:\ZephyrAlpha\tests\test_task_repo.py
depends_on:
  - SRC-041
acceptance:
  - "CRUD 全覆盖（INSERT/SELECT/UPDATE/DELETE）"
  - "10 状态机转换全部实现"
tags:
  -
  - datalayer
  - origin:#17
