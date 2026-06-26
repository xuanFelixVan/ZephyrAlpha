---
module_id: KE-010
status: active
title: 5.3.1 Session 结束时（保存交接包）
category: agent_instruction
ttl: permanent
doc_type: knowledge_entry
---

# 5.3.1 Session 结束时（保存交接包）

5.3.1 Session 结束时（保存交接包）

```python
from zephyr.core.session_continuity import SessionContinuity

sc = SessionContinuity()
sc.generate_and_save(session_id="2026-05-05-a", task_repo=task_repo)
```

这会自动从 `task_repo` 汇总统：
- COMPLETED / VERIFIED 的任务 → `completed_tasks`
- IN_PROGRESS 的任务 → `in_progress_tasks`
- BLOCKED 的任务 + 阻塞原因 → `blocked_items`
- READY / RETRY / PENDING 的任务 → `next_actions`（按 priority 排序，最多10个）
- 自动生成的人类可读 `context_summary`

写入 `handoffs` 表（同库 `data/databases/governance.db`）。
