---
module_id: KE-2157
status: active
title: 3.9 #63: TaskHeartbeatMonitor (M-45)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.9 #63: TaskHeartbeatMonitor (M-45)

3.9 #63: TaskHeartbeatMonitor (M-45)

文件：`D:\ZephyrAlpha\src\zephyr\shared\task_heartbeat.py`

- HEARTBEAT_TIMEOUT=600s, MAX_CONSECUTIVE_MISSES=3
- `_cleanup_crash_zombies()`: 系统启动时清理上次崩溃遗留
- `check_all()`: 30min无心跳→标记zombie+回滚半写入文件
- `heartbeat(task_id)`: AI Agent每次tool_call后调用
