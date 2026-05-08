---
module_id: KE-documentat-8_2-000
title: 8.2 门禁触发与失败处理
category: documentation
---

# 8.2 门禁触发与失败处理

8.2 门禁触发与失败处理

| 严重级 | 触发动作 | 处理 |
|--------|---------|------|
| 🔴 Fatal（schema 违反 / 重复主键） | 阻塞 ingest，告警 | 修数据源或修代码，**不绕过** |
| 🟠 Critical（range 越界 / freshness 严重超时） | 数据隔离到 quarantine，下游消费方收到 stale 标记 | Steward 24h 内裁决 |
| 🟡 Warning（drift / 缺失率小幅升高） | 告警 + dashboard | 进入 backlog 排查 |
