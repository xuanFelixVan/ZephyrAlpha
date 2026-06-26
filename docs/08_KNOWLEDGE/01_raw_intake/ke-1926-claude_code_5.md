---
module_id: KE-1835----------claude-code-5----000
status: active
title: 2.25 权限模式管理器——Claude Code 5 模式 + Codex CLI Profiles（决策 D-018-23）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.25 权限模式管理器——Claude Code 5 模式 + Codex CLI Profiles（决策 D-018-23）

2.25 权限模式管理器——Claude Code 5 模式 + Codex CLI Profiles（决策 D-018-23）

> **决策 D-018-23**：氛围编程中Owner需要动态切换权限模式。参照Claude Code的Shift+Tab（5种模式）和Codex CLI的profiles机制，引入**权限模式管理器**。
>
> **可信主体**：Claude Code 5种权限模式（default/acceptEdits/plan/bypassPermissions/auto）+ Shift+Tab切换。Codex CLI profiles（多配置文件）+ --full-auto + /permissions mid-session切换。

```yaml
