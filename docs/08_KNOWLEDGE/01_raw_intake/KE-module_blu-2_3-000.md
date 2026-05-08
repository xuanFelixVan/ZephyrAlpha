---
module_id: KE-module_blu-2_3-000
title: 2.3 不包含的职责
category: module_blueprint
---

# 2.3 不包含的职责

2.3 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | SQLite CRUD + 10状态机 + N:N映射 | `task_repo.py`（`src/zephyr/db/`）— 已有生产级代码 |
| 2 | Task 模型基座（Pydantic V2 31字段） | `shared/schemas.py`（`src/zephyr/shared/`）— metadata-registry.md §7 真源 |
| 3 | MCP Server Web 层 | `task_manager_server.py`（`src/zephyr/mcp/`）— 本蓝图更新后重写 |
| 4 | 审计脚本 | MOD-INF-005 — 已有 9+ 脚本 |
| 5 | context_engine | `context_engine/` — 已有 7 模块 + experimental 补齐 |
| 6 | dashboard | `dashboard/` — 已有代码 |
| 7 | Phase 5 AI 自治 | 预留字段不实现——但五级枚举已在 GOV-TASK-004 中定义 |
| 8 | 模型注册表完整建设 | 独立小任务——model-registry.yaml 另排 |
| 9 | 全功能看板 UI | 排除——CLI 摘要视图替代 |
| 10 | 多 Agent 并行辩论 | v0.5.0+ 的事——当前串行管线 + 三层防御足够 |

---
