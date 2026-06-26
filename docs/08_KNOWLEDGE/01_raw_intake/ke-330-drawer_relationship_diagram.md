---
module_id: KE-302
status: active
title: 4. Drawer relationship diagram / 抽屉关系图
category: documentation
ttl: permanent
---

# 4. Drawer relationship diagram / 抽屉关系图

4. Drawer relationship diagram / 抽屉关系图

```
         ┌──────────────── Governance layer / 治理层 ──────────────┐
         │ 00_governance  01_standards                            │
         │ 16_compliance  17_risk  18_audit                      │
         └───────┬─────────────────────────────────────────────┘
                 │ Policies / standards / risk controls
                 │ 政策 / 标准 / 风控
                 ↓
         ┌──────────────── Architecture layer / 架构层 ───────────┐
         │ 02_enterprise  03_domain                              │
         │ 03_modules                                         │
         └───────┬─────────────────────────────────────────────┘
                 │ Blueprints / construction plans / 蓝图 / 施工图
                 ↓
         ┌──────────────── Business value chain / 业务价值链 ──────┐
         │ 09 → 10 → 11 → 12 → 13 → 14                          │ ← Core flow / 核心流动
         │ Data  Research  Model  Strategy  Exec  Report         │
         │ 数据  研究      模型   策略      执行  报告             │
         └───────┬─────────────────────────────────────────────┘
                 │ Runtime support / 运行时支撑
                 ↓
         ┌──────────────── Platform capability / 平台能力层 ───────┐
         │ 06_security  07_sre  08_ai_engineering                │ ← Serves all domains / 服务所有业务域
         └──────────────────────────────────────────────────────┘
                 ↓ Accumulate / 沉淀
         ┌──────────────── Knowledge layer / 知识层 ──────────────┐
         │ 08_knowledge                                     │
         └──────────────────────────────────────────────────────┘
                 ↑ In-progress / 讨论区       ↓ Expired / 过期
              19_workspace               99_archive
```

> **📊 文档拓扑图**：见 [`diagrams/docs_drawer_topology.mmd`](diagrams/docs_drawer_topology.mmd) — docs/ 20 抽屉分类拓扑

---
