---
module_id: KE-4015
title: 第二轮 — 上下文与集成层（#21-#40）
category: module_blueprint
---

# 第二轮 — 上下文与集成层（#21-#40）

第二轮 — 上下文与集成层（#21-#40）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 21 | 跨 Agent 上下文压缩缺失 | 🟠 P1 | KBG-0041 P0-P3 压缩 | §2.11 |
| 22 | 上下文污染检测缺失 | 🟠 P1 | OWASP ASI06 Memory Poisoning | §2.11 |
| 23 | 上下文新鲜度/TTL 未定义 | 🟡 P2 | — | §2.11 |
| 24 | 上下文溯源缺失 | 🟡 P2 | MOD-INF-022 §2.15 anti_sycophancy | §2.11 |
| 25 | 委托代价评估缺失 | 🟠 P1 | MOD-INF-022 §2.4 | §2.12 |
| 26 | 全链路 Token 预算未定义 | 🟠 P1 | Anthropic Claude Code token budget | §2.12 |
| 27 | Agent 能力 vs 成本路由缺失 | 🟡 P2 | Augment per-task model routing | §2.12 |
| 28 | 模型降级策略缺失 | 🟡 P2 | MOD-INF-022 model_cascading | §2.12 |
| 29 | 分布式追踪缺失 | 🟡 P2 | OpenTelemetry SpanContext | §2.13 |
| 30 | A2A 专属指标缺失 | 🟡 P2 | — | §2.13 |
| 31 | Agent 信誉/评分缺失 | 🟡 P2 | — | §2.13 |
| 32 | Agent 生命周期管理缺失 | 🟡 P2 | — | §2.5 status |
| 33 | 优雅降级（Agent 消失）缺失 | 🟡 P2 | — | §2.13 Dead Letter Queue |
| 34 | Agent Card 版本/向后兼容缺失 | 🟡 P2 | Google A2A Agent Card versioning | §2.2 |
| 35 | Agent A/B 测试缺失 | 🔵 P3 | — | Phase beta |
| 36 | 陈旧 Agent 检测缺失 | 🟡 P2 | — | §2.1 agent_card.status |
| 37 | 消息路由一致性缺失 | 🟡 P2 | OWASP ASI07 | §2.10 |
| 38 | 任务幂等性缺失 | 🟡 P2 | — | Phase scaffold |
| 39 | 任务优先级继承缺失 | 🟡 P2 | Priority Inversion OS classic | §2.9 L3 |
| 40 | 资源公平性调度缺失 | 🟡 P2 | — | §2.5 Filter/Score |
