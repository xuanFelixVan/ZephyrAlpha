---
module_id: KE-468
title: 6.4 图表引擎策略
category: documentation
ttl: permanent
---

# 6.4 图表引擎策略

6.4 图表引擎策略

| 用途 | 选型 | 理由 |
|------|------|------|
| **金融 K 线 / 深度 / 分时** | TradingView lightweight-charts v4 | 开源、性能强、金融图表业界标配 |
| **PnL / Risk 仪表** | Recharts + D3 | React 生态、声明式、可控性强 |
| **Grafana 风格监控**（L12）| iframe 嵌入 Grafana（短期）/ react-grafana-panel（长期）| 不重造轮子 |
