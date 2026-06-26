---
module_id: KE-2436------should-003
status: active
title: 7.2 Token 加载策略（SHOULD）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 7.2 Token 加载策略（SHOULD）

7.2 Token 加载策略（SHOULD）

对标 Codified Context 的三层内存消耗模型（热记忆/领域触发/冷记忆），本体系推荐以下加载策略：

| 蓝图层级 | 加载策略 | 包含内容 | Token 预算 | 怎么加载 |
|:---|:------|------|:---:|------|
| **热内存** | 自动加载 (每次会话) | PS-STD-005 §3 + §4 + §7 + Level 0 总蓝图 §1（系统清单+拓扑图）| ~800 | AGENTS.md 自动注入 |
| **领域触发** | 领域触发 (按任务) | 对应 Level 1 域集成蓝图 + 该域内 ≥ 3 个 Module 蓝图 §1 | ~2000 | Gate Engine 或 Pipeline Router 自动加载 |
| **冷内存** | 按需检索 (Index→full) | Level 2 模块蓝图全文 §1-§12 | ~8000/模块 | MCP 检索 + CE build→compress→inject |

**三层内存对应关系**：

| Codified Context | ZephyrAlpha PS-STD-005 |
|------|------|
| Tier 1 Constitution（热记忆 660 行） | = Level 0 总蓝图 §0 + Level 1 域蓝图 §1 |
| Tier 2 Domain Experts（19 Agent 按触发）| = Level 1 域蓝图 + 本域内的 Level 2 模块蓝图 |
| Tier 3 Knowledge Base（34 按需检索）| = Level 2 模块蓝图 §1-§12 全文 + 02_enterprise_architecture/ 架构视图 |

**冷启动检查清单**：新 AI session 打开项目后，**MUST** 先读 §2 SSoT 声明的真源（§3 蓝图金字塔 + §4 目录结构），再按 §7.1 逐级下钻。
**禁止**：跳过 Level 0/1 直接读 Level 2——没有跨系统上下文。

---
