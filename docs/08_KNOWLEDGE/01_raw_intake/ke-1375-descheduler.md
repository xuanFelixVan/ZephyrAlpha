---
module_id: KE-1286
status: active
title: 1. Descheduler（后台定时扫描）
category: module_blueprint
---

# 1. Descheduler（后台定时扫描）

1. Descheduler（后台定时扫描）

```python
class PipelineDescheduler:
    scan_interval_s: int = 300  # 每5分钟扫描

    def scan(self) -> list[dict]:
        stale_tasks = self._find_stale()        # >30min无状态推进
        misrouted_tasks = self._find_misrouted() # 路由与结果明显不匹配
        stuck_tasks = self._find_claude_stuck() # Claude Rescue超时5min

        for task in stale_tasks + misrouted_tasks + stuck_tasks:
            self._reschedule(task)  # 重新路由或升级到Claude
```
