---
module_id: KE-4127
title: 5. 依赖关系
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5. 依赖关系

5. 依赖关系

| 依赖 | 类型 | 内容 | 版本 |
|------|:---:|------|------|
| PS-STD-001 | 必须 | §7——task_id / 语义28 / 追踪3 / Task共31 / 状态机 | ≥2.0.0 |
| PS-STD-011 | 必须 | MTH-012 涌现式设计 + MTH-013 路径合规 | ≥2.6.0 |
| GOV-DOC-002 | 必须 | §5.1.2 路径映射 | — |
| GOV-TASK-001 | 必须 | 任务卡操作指南 | ≥3.0.0 |
| GOV-TASK-004 | 必须 | 取消权限、优先级裁决 | ≥2.0.0 |
| GOV-TASK-005 | 必须 | 关闭三步法 | ≥1.1.0 |
| MOD-INF-005 | 必须 | 脚本系统 12 维度 | ≥3.0.0 |
| TEMPLATE-TASK-001 | 必须 | 任务卡 .md 模板 | ≥1.0.0 |
| REG-LLM-001 | 必须 | 模型基准排名 | ≥1.1.0 |
| GOV-AI-002 | 必须 | 模型路由策略 | ≥2.0.0 |
| shared/schemas.py | 必须 | `Task` 31 字段（语义28+追踪3）TaskCard 基座 | 现有代码 |
| task_repo.py | 必须 | SQLite CRUD + 10状态机 + N:N task_files + BatchCoordination (v16) | 现有代码 |
| task-completion-gate.py | 必须 | G7 门禁逻辑——需同步 | 现有代码 |
| task-card-meta-registry.md | scaffold | 任务卡系统迁移追踪 | V-13 |

---
