---
module_id: KE-494------experimental-000
status: active
title: 7.2 AI Agent 身份模型（experimental P0）
category: documentation
---

# 7.2 AI Agent 身份模型（experimental P0）

7.2 AI Agent 身份模型（experimental P0）

虽然无多人 IAM，但 **AI Agent 必须有独立身份**：

| Agent | 身份 | 权限集 | 实现 |
|-------|------|-------|------|
| Cursor Agent | `agent:cursor` | Sandbox RW + LSG 配额 A | Orc 签发 Session Token |
| Trae Agent | `agent:trae` | Sandbox RW + LSG 配额 B | Orc 签发 Session Token |
| Human Owner | `human:owner` | 全权（绕过 Sandbox）| 无 Token，文件系统直接操作 |

**关键约束**：AI Agent 的每次调用都带 `agent_id`，Session Log 按 agent_id 分流，便于事后追溯（"这次污染是哪个 Agent 造成的"）。
