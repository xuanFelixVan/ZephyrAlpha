---
module_id: KE-636-------v0-003
status: active
title: Stage 7：从"工作区 v0"到"前置项目会话留痕机制迁移"
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# Stage 7：从"工作区 v0"到"前置项目会话留痕机制迁移"

Stage 7：从"工作区 v0"到"前置项目会话留痕机制迁移"

继续讨论后，又把前置项目"为什么所有对话像是自动保存在项目里"这件事拆清了：

它其实不是一个单点按钮，而是两层机制叠在一起：

1. **Cursor / 客户端层**：原始 transcript 自动保存在本机（JSONL / 对话记录）。
2. **仓库规则层**：前置项目通过 `.cursor/rules`、`AGENTS.md`、session-log-template 和会话管理规则，要求每次会话结束前把整理后的 **Session Log** 写入项目目录。

这说明前置项目并不是"把所有原始对话自动塞进仓库"，而是：

**原始 transcript 自动留在本机；项目内保存的是面向交接和提炼的 session log。**

这一步把一个重要问题讲清楚了：

- **要迁移的不是"一个神秘功能"**
- 而是要把"原始 transcript + 项目内 Session Log + 关键决策升格"这套机制，在新树里重新建立

因此当前又形成三个新判断：

1. **新树也需要保留两层**：外部 transcript + 项目内 session log。
2. **新树正式 session log 路径应进入 `18_audit_and_evidence/session-logs/`**，与新 IA 对齐。
3. **前置项目聊天记录要吸收，但不应原样全部复制进新项目**；应先登记来源地址，再按 `raw / candidate / active` 思路分批吸收。
