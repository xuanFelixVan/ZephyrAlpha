---
module_id: KE-4237
title: 9.2 下游消费者
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 9.2 下游消费者

9.2 下游消费者

| 下游 | 关系 | 调用姿态 |
|------|------|---------|
| **Feedback Loop Engine** | 必须 | Orchestrator push 指标（task_completed / failed / hallucinated / duration / cost） |
| Dashboard `task_overview.py` | 可选 | `await orc.list_tasks() / stats()` |
| CI/CD | 可选 | submit_task 触发验收任务 |
