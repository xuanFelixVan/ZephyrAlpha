---
module_id: KE-3277
title: 3.9 代码执行安全
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.9 代码执行安全

3.9 代码执行安全

> **对标**：OWASP LLM Top 10 #8（Agent 权限过大）、Devin sandbox、KBG-0018 Agent Sandbox 设计。

| #      | 禁止行为                      | 原因                                            | 替代方案                          | 来源                     |
| ------ | ------------------------- | --------------------------------------------- | ----------------------------- | ---------------------- |
| ABS-38 | AI 在沙箱外执行不可信代码            | 不可信代码可能包含恶意操作（文件删除、网络访问、权限提升）                 | 不可信代码必须在沙箱环境中执行，沙箱限制文件系统和网络访问 | OWASP LLM #8, KBG-0018 |
| ABS-39 | AI 在未确认的情况下执行破坏性 shell 命令 | `rm -rf`、`format`、`del /s` 等命令不可逆，AI 无法评估完整影响 | 破坏性命令必须经 Owner 确认后方可执行        | Claude Code 确认机制       |
