---
module_id: KE-module_blu-2_1___________d-019-01-004
title: 2.1 四层架构总览（决策 D-019-01 修订）
category: module_blueprint
---

# 2.1 四层架构总览（决策 D-019-01 修订）

2.1 四层架构总览（决策 D-019-01 修订）

> **决策 D-019-01（修订）**：采用四层架构组织 Agent Skills——不再按角色单体聚合为 3 个 Skill Pack，而是将"领域知识"和"角色模式"分层解耦。
>
> **修订依据（v0.3.0）**：
> - Codified Context 的 19 个 Agent 按领域分（coordinate-wizard 只管等距坐标，不管数据库），不是一个"万能架构师"
> - 数据库的 ATM 两阶段提交模式和 MCP 的 stdio 协议模式完全不同——统一的"读蓝图 §3 + 写代码 + 跑测试"指令无法覆盖这些差异
> - 14 层扩展场景下，3 个角色型 Skill Pack 无法承载不同领域的特异性——按领域创建 Domain Skill，新领域不影响已有 Skill
> - Anthropic Claude Skills 原生支持多 Skill 同时加载——组合 Domain Skill + Role Skill 是标准实践

```
┌──────────────────────────────────────────────────────────────────┐
│  L0: AGENTS.md 宪法（热记忆 ~800 tokens，always loaded）            │
│  • 项目拓扑 + 关键路径索引                                          │
│  • Skill 触发表（Task-Type → Domain Skill + Role Skill 映射表）     │
│  • Build/Test/Lint 标准命令 + 编码铁律                              │
│  • 会话交接约定（Session Resume 协议）                              │
│  ★ 对标 Codified Context Tier 1 Constitution                     │
├──────────────────────────────────────────────────────────────────┤
│  L1: Domain Skills（领域技能 ~500 tokens each，按触发条件加载）       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │
│  │ database  │ │ mcp-svr   │ │ context   │ │ feedback  │  ...   │
│  │ specialist│ │ specialist│ │ specialist│ │ specialist│        │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │
│  • 每个 Domain Skill 只负责一个模块/系统（Bounded Domain）           │
│  • 遵循 agentskills.io SKILL.md 格式 + YAML frontmatter          │
│  • 嵌入：领域代码模式 + 常见 bug 清单 + 模块专属门禁 + 关键文件索引     │
│  ★ 对标 Codified Context Tier 2 domain-expert agents             │
├──────────────────────────────────────────────────────────────────┤
│  L2: Role Skills（角色技能 ~300 tokens each，与 Domain Skill 组合）   │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐                       │
│  │ architect │ │ implement │ │ governor  │                       │
│  └───────────┘ └───────────┘ └───────────┘                       │
│  • 定义跨领域的操作规范（"怎么读蓝图"、"怎么跑门禁"、"怎么写审计日志"）  │
│  • 与 Domain Skills 组合加载——Domain 提供"什么"，Role 提供"怎么做"    │
│  • 包含升级/委托协议：遇到需要人类决策的情况走什么路径                  │
│  ★ ZephyrAlpha 独有创新——业界无角色层                               │
├──────────────────────────────────────────────────────────────────┤
│  L3: Cold Memory（冷记忆 ~8000 tokens per module，通过 MCP 按需检索）  │
│  • 蓝图全文（blueprint.md §1-§12）                                │
│  • 通过 MCP context retrieval server 按需检索                      │
│  • ★ 对标 Codified Context Tier 3 + MCP retrieval               │
└──────────────────────────────────────────────────────────────────┘
```

**关键创新**：Domain Skills（领域知识）和 Role Skills（执行方式）**分层解耦**。当一个任务需要"实现数据库的新接口"时，AI 同时加载 `database-specialist`（知道数据库的 ATM 两阶段提交模式）和 `implementer`（知道怎么按蓝图 §3 接口契约写代码 + 跑 pytest + 修 lint）。两者不冲突——Domain Skill 告诉你"这段代码的特殊约束是什么"，Role Skill 告诉你"代码写完后要做哪些步骤"。

**冲突消除规则**：当 Domain Skill 和 Role Skill 对同一操作给出不同指令时，**Domain Skill 优先**（更具体、更符合该领域的实际要求）。
