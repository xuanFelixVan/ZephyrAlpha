---
module_id: KE-2457--------v2-0-0--000
status: active
title: 8. Error Budget 五级响应机制（v2.0.0 新增，v2.1.0 三级→五级升级）
category: module_blueprint
---

# 8. Error Budget 五级响应机制（v2.0.0 新增，v2.1.0 三级→五级升级）

8. Error Budget 五级响应机制（v2.0.0 新增，v2.1.0 三级→五级升级）

对标 Google SRE Workbook §4 Error Budgets + §5 Alerting on SLOs + §5.4 Multi-Window Multi-Burn-Rate Alerts。

> **v2.1.0 升级原因**：三级（Healthy/Cautious/Critical）在高频 AI 变更场景下粒度过粗。Healthy 50%→Cautious 25% 中间 25% 是盲区——消耗率上升时没有预警级。Critical <25%→Exhausted 0% 也有 25% 盲区——预算快耗尽时没有紧急响应级。Google SRE Workbook 2025 修订版明确推荐五级粒度。
