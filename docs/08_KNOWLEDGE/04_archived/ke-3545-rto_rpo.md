---
module_id: KE-3405---rpo-000
title: 8.1 RTO / RPO 核心链路分层矩阵
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 8.1 RTO / RPO 核心链路分层矩阵

8.1 RTO / RPO 核心链路分层矩阵

| 链路 | 资产级别 | RTO（市场时段） | RTO（非市场） | RPO | 激活 Tier |
|-----|---------|----------------|-------------|-----|----------|
| **L06 订单 + 成交回报** | 🔴 金融资金 | ≤ 5 min | ≤ 24 h | **0（零丢失）** | 热备 |
| **L2 Audit Log** | 🔴 合规审计 | ≤ 15 min | ≤ 24 h | **0（append-only）** | 热备 |
| **L00 数据源 + L05 信号** | 🟡 业务核心 | ≤ 15 min | ≤ 4 h | ≤ 5 min | 温备 |
| **L02 因子 + L04 风控** | 🟡 业务核心 | ≤ 30 min | ≤ 4 h | ≤ 15 min（可重算） | 温备 |
| **L07 归因 + L13 实验** | 🟢 离线分析 | ≤ 4 h | ≤ 48 h | ≤ 1 h | 冷备 |
| **L12 Telemetry** | 🟢 辅助 | ≤ 4 h | ≤ 24 h | ≤ 30 min | 冷备 |
| **中间缓存** | 🟢 可丢弃 | — | — | ∞ | 无备份 |
