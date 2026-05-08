---
module_id: KE-agent_inst-5_3_2_session-000
title: 5.3.2 Session 开始时（恢复上下文）
category: agent_instruction
---

# 5.3.2 Session 开始时（恢复上下文）

5.3.2 Session 开始时（恢复上下文）

```python
from zephyr.core.session_continuity import SessionContinuity

sc = SessionContinuity()
sc.print_restore_summary()
```

输出样例：

```
============================================================
  [Session Continuity] 欢迎回来！
  上次 session: 2026-05-05-a
  交接时间: 2026-05-05 14:30 UTC
============================================================
  ✅ 已完成: 3 个任务
       CP-1
       CP-2
  🔄 进行中: 1 个任务
       CP-3
  🚫 阻塞: 0 个
  📋 下一步行动:
       [1] CP-3: [Session Continuity] HandoffPackage 自动生成 + session 恢复
  📝 上下文摘要: 完成 2 个任务, 1 个进行中, 0 个阻塞. 总计 1 个任务有活动记录.
============================================================
```
