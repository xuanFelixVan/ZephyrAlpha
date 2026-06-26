---
module_id: KE-1280
title: 第一轮基础盲点 — 协议层（#1-#20）
category: module_blueprint
ttl: permanent
---

# 第一轮基础盲点 — 协议层（#1-#20）

第一轮基础盲点 — 协议层（#1-#20）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 1 | Agent Card / 能力声明模型缺失 | 🔴 P0 | Google A2A AgentCard §5.5 + Anthropic Agent Spec | §2.2 + D-025-02 |
| 2 | A2A 任务状态机缺失 | 🔴 P0 | Google A2A TaskState §6.3 | §2.3 + D-025-03 |
| 3 | Message/Part 类型缺失 | 🔴 P0 | Google A2A Part union type §6.5 + MMA2A 模态原生 | §2.4 + D-025-04 |
| 4 | Supervisor/Coordinator 缺失 | 🔴 P0 | Anthropic Agent Teams Team Lead + Augment Code Coordinator | §2.5 + D-025-05 |
| 5 | Agent 间认证缺失 | 🔴 P0 | Google A2A Auth §4 + OWASP ASI03 | §2.10 + D-025-10 |
| 6 | 死锁防护缺失 | 🔴 P0 | MIT CORDIAL + DPBench 95-100% 死锁率 | §2.9 + D-025-09 |
| 7 | 活锁防护缺失 | 🔴 P0 | Mirror Mirror Loop 社区实战 + Politeness Spiraling | §2.9 + D-025-09 |
| 8 | 语义冲突检测缺失 | 🔴 P0 | Augment Code semantic contradictions + AST diff | §2.7 + D-025-07 |
| 9 | Living Spec 冲突预防缺失 | 🔴 P0 | Coware + Augment spec-scoped decomposition | §2.6 + D-025-06 |
| 10 | OWASP ASI07 完全暴露 | 🔴 P0 | OWASP Agentic Top 10 2026 + Palo Alto Unit 42 | §2.10 |
| 11 | Agent Session Smuggling 无防御 | 🔴 P0 | Palo Alto Unit 42 Nov 2025 | §2.10 |
| 12 | 级联故障防护缺失 | 🔴 P0 | OWASP ASI08 + Bulkhead Pattern | §2.13 + §2.10 |
| 13 | Rogue Agent 检测缺失 | 🔴 P0 | OWASP ASI10 + card_integrity | §2.10 |
| 14 | 消息完整性校验缺失 | 🔴 P0 | JWT RS256 + nonce replay protection | §2.10 |
| 15 | A2A 三层架构蓝图未定义 | 🔴 P0 | Google A2A full stack + MOD-INF-022 三层对标 | §2.1 + D-025-01 |
| 16 | 施工自指悖论未处理 | 🔴 P0 | MOD-INF-022 §2.20 + 100% AI 施工 | §2.14 + D-025-11 |
| 17 | 经济护栏缺失（跨 Agent 链） | 🟠 P1 | MOD-INF-022 §2.4 + AICosts.ai | §2.12 |
| 18 | SSE 流式传输缺失 | 🟠 P1 | Google A2A §3.3 | §2.4 |
| 19 | Push Notification 缺失 | 🟠 P1 | Google A2A §6.8-6.10 | §2.4 |
| 20 | 输入协商（input-required）缺失 | 🟠 P1 | Google A2A §4.5 in-task auth | §2.3 |
