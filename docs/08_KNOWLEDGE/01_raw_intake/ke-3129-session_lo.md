---
module_id: KE-3027
title: 4.1 触发点
category: session_log
ttl: permanent
---

# 4.1 触发点

4.1 触发点

| 触发场景 | 触发方式 | 必须字段 |
|---------|---------|---------|
| IDE 正常关闭 | 监听 IDE close 钩子 | `ended_reason: ide_close` |
| 用户显式命令 `/session save` | 用户手动触发 | `ended_reason: user_command` |
| IDE 崩溃后恢复 | 启动时检查上次是否异常退出 | `ended_reason: crash`（后补写）|
| IDE 空闲超时（> 30 min）| FLE 定时触发 | `ended_reason: idle_timeout` |
| Context Engine 正常关闭 | `CE.shutdown()` 前置 | `ended_reason: normal_shutdown` |
