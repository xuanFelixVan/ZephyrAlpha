---
module_id: KE-2478-----burn-rate-000
status: active
title: 8.3 消耗率（Burn Rate）多窗口监控
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8.3 消耗率（Burn Rate）多窗口监控

8.3 消耗率（Burn Rate）多窗口监控

对标 Google SRE Workbook §5.4 Multi-Window Multi-Burn-Rate Alerts：

| 窗口 | 消耗率阈值 | 对应级别 | 说明 |
|------|-----------|---------|------|
| 1h | > 14.4× | Emergency（立即） | 1 小时内消耗了 2% 预算——极端异常，可能 DDoS 或死循环 |
| 6h | > 6× | Critical（快速） | 6 小时内消耗了 5% 预算——严重异常 |
| 3d | > 3× | Cautious（慢速） | 3 天内消耗了 10% 预算——趋势恶化 |
| 30d | > 1× | Warning（基线） | 整窗口消耗超预算——持续性问题 |

> **短窗口 vs 长窗口**：短窗口抓脉冲式异常（如 1 小时内突发大量错误），长窗口抓慢性问题（如每天漏一点预算，月度总结才发现超支）。两者必须同时监控——单窗口会有盲区。
