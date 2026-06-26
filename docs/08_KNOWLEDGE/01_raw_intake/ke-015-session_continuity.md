---
module_id: KE-015
status: active
title: 5.3 Session Continuity — 自动交接协议
category: agent_instruction
ttl: permanent
---

# 5.3 Session Continuity — 自动交接协议

5.3 Session Continuity — 自动交接协议

> **痛点**：AI 每次新 session 是零记忆的。你不知道上回做到哪了、哪些任务在等、哪些被阻塞了。
>
> **解决**：`src/zephyr/core/session_continuity.py` 提供自动交接机制——session 结束时自动汇总状态，下一个 session 开始时自动恢复上下文。
>
> **触发**：本节由 AI **在 session 结束前** 和 **session 开始时** 主动调用。这是第 11 条铁律级别的要求。
