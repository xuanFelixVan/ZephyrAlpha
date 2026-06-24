---
module_id: KE-2348
title: 6. 产出物存放目录
category: module_blueprint
---

# 6. 产出物存放目录

6. 产出物存放目录

> ⚠️ 所有路径必须与 GOV-DOC-002 §5.1.2 一致。MTH-013 强制。

| 产出物 | 完整绝对路径 | 存储介质 |
|--------|------------|:--:|
| 蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01-infrastructure\task-system\blueprint.md` | .md |
| 任务卡（SQLite 真源）| `D:\ZephyrAlpha\data/databases/governance.db` — tasks 表 | SQLite |
| Task 模型基座（31 字段）| `D:\ZephyrAlpha\src\zephyr\shared\schemas.py` | .py |
| TaskCard 扩展模型（52字段）| `D:\ZephyrAlpha\src\zephyr\core\models.py` | .py |
| SQLite CRUD + 状态机 | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | .py |
| SQLite Schema + 迁移链 | `D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py` | .py |
| N:N 文件映射 | `D:\ZephyrAlpha\src\zephyr\orchestrator\file_task_mapper.py` | .py |
| 蓝图拆解器 | `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py` | .py |
| MCP Server（5 Tool）| `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py` | .py |
| MCP Tool 契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool-contracts.yaml` | .yaml |
| 知识审阅池 | `D:\ZephyrAlpha\src\zephyr\kb\triage.py` | .py |
| 管线编排器 | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py` | .py |
| 上下文装配器 | `D:\ZephyrAlpha\src\zephyr\context-engine\context_assembler.py` | .py |
| G7 任务完成门禁 | `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` | .py |
| 蓝图-代码同步校验 | `D:\ZephyrAlpha\scripts\governance\d5_architecture\validate_blueprint_code_sync.py` | .py |
| 架构模型（DB 层）| `D:\ZephyrAlpha\architecture_model\layers\b_db.yaml` | .yaml |
| 测试 | `D:\ZephyrAlpha\tests\` | .py |

---
