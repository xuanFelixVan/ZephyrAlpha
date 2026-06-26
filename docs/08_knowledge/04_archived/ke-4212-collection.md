---
module_id: KE-4212
title: 3.1 Collection 概念（4 个预定义）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.1 Collection 概念（4 个预定义）

3.1 Collection 概念（4 个预定义）

VMS 管理 **4 个预定义 Collection**，按检索用途分区，支持跨 Collection 联合检索（允许动态创建自定义，但 4 个预定义不可删除）：

| Collection | 用途 | 典型 Document 来源 |
|-----------|------|-------------------|
| `decisions` | 架构决策与合约 | **KB:decisions**（SQLite `knowledge`，`category=architecture_decision`，`ke_id=ADR-*`）、`03_modules/_b_track_interfaces/*interface*.md` |
| `code_context` | 代码与配置 | `src/**/*.py`、`src/**/*.yaml`、`docs/03_modules/**/*.md` |
| `task_history` | 任务卡与执行历史 | `docs/03_modules/_domain-infra_ops/task-system/changes/**/*.md`（拆卡/任务卡样例）、`src/zephyr/db/task_repo.py` 持久化任务元数据（见 MOD-TASK_SYSTEM） |
| `lessons` | 经验教训与审计 | `docs/_working/audit/reports/`、`docs/_working/audit/findings/` |
