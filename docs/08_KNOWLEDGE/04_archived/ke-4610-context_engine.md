---
module_id: KE-4444
title: 6.2 Context Engine 对其他服务的调用
category: session_log
ttl: permanent
---

# 6.2 Context Engine 对其他服务的调用

6.2 Context Engine 对其他服务的调用

| 调用 | 目的 |
|------|------|
| `orchestrator.get_open_tasks()` | 查询未完成任务填充 `open_tasks` |
| `orchestrator.get_hallucination_events()` | 查询幻觉事件 |
| `orchestrator.restore_open_tasks()` | 下次启动时恢复任务队列 |
| `vms.get_recent_retrievals()` | 填充 `context_state.recent_retrievals` |
| `lsg.scan_for_secrets()` | 写入前扫描，防止敏感信息泄漏 |
| `fle.collect_metric()` | 上报 session 生命周期指标 |
