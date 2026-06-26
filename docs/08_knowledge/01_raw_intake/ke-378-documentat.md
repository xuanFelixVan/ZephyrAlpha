---
module_id: KE-378
status: active
title: 4.3 指标采集拓扑
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.3 指标采集拓扑

4.3 指标采集拓扑

```
各服务 (VMS/CE/Orc/FLE/LSG)
        │ metrics.emit()
        ▼
┌────────────────────────┐
│   FLE collect_metric() │ ──→ SQLite .runtime/sqlite/feedback.db
└───────┬────────────────┘     （数据量 > 100 万/天 触发 TECH-13 升级 InfluxDB）
        │
        ▼
┌────────────────────────┐
│   detect_anomaly()     │ EMA + 滑动窗口
└───────┬────────────────┘
        │
        ▼
┌────────────────────────────────────┐
│   dispatch_action() via Protocol   │
│   [ CE.降级 / Orc.限流 / 人工告警 ]│
└────────────────────────────────────┘
```

**导出通道**：

- `infra_ops/` 定期从 FLE 导出到本地文件（JSON Lines）
- beta 启用 OpenTelemetry Collector → Prometheus/Grafana 标准栈

> 🚧 **beta 扩展**：Grafana Dashboard 模板、On-Call 流程、Alertmanager 规则集待 beta 补齐（本文档届时升级为 v1.0.0 active）。

---
