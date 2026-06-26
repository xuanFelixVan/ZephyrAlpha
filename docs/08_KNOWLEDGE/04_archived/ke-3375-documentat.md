---
module_id: KE-3254
title: 3.10 异步架构约束
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.10 异步架构约束

3.10 异步架构约束

> **对标**：项目全局异步架构决策（5 份 AI 工程接口规范一致声明）。

| #      | 禁止行为                | 原因                                       | 替代方案                                           | 来源                                                                   |
| ------ | ------------------- | ---------------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------- |
| ABS-40 | 使用 `threading.Lock` | 项目全局异步架构，`threading.Lock` 会阻塞事件循环导致全服务卡死 | 进程内锁用 `asyncio.Lock`，跨进程锁用 `filelock.FileLock` | context-engine-interface.md, agent-orchestrator-interface.md 等 5 份接口 |
