---
module_id: KE-1967
title: 26.1 核心面板配置
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 26.1 核心面板配置

26.1 核心面板配置

| 面板 | 数据源 | 刷新率 | 告警 |
|------|------|:--:|------|
| 系统健康 (11 SLI) | MOD-INF-015 Telemetry | 10s | SLI>SLO |
| 成本仪表板 | Token Counter + Data APIs | 1h | 超预算20% |
| 订单流 | OMS (MOD-INF-005) | 实时 | 异常模式 |
| 模型漂移 | Drift Monitor (§37) | 1h | >阈值 |

---
