---
module_id: KE-3255
title: 3.11 安全服务故障处置
category: documentation
ttl: permanent
---

# 3.11 安全服务故障处置

3.11 安全服务故障处置

> **对标**：LSG fail-closed 设计、KBG-0018 Agent Sandbox、OWASP LLM #8。

| #      | 禁止行为                   | 原因                                           | 替代方案                         | 来源                                            |
| ------ | ---------------------- | -------------------------------------------- | ---------------------------- | --------------------------------------------- |
| ABS-41 | 安全服务（LSG）故障时 fail-open | 放水一秒都可能导致 prompt injection 成功，安全服务挂了必须拒绝所有流量 | LSG 故障时 fail-closed，宁可全部拒绝流量 | llm-security-gateway-interface.md             |
| ABS-42 | 沙箱创建失败时降级为无沙箱执行        | 宁可任务全挂也不能让 Agent 裸跑，降级 = 安全红线突破              | 沙箱创建失败 → 任务 FAILED，不降级       | agent-orchestrator-interface.md (DEGRADE-003) |
| ABS-43 | 使用 `shell=True` 执行子进程  | `shell=True` 绕过路径白名单检查，允许注入任意命令              | 所有命令必须以 `list[str]` 形式传入     | process\_sandbox.py                           |
