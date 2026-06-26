---
module_id: KE-3467
title: 1.2 与其他视图的边界
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 1.2 与其他视图的边界

1.2 与其他视图的边界

本视图 **NOT** 覆盖以下内容（由其他视图承载）：

| 边界 | 落在哪个视图 | 本视图如何引用 |
|---|---|---|
| docs/ 文档抽屉治理规则 | `02-information_architecture.md` | §4 A-01/A-03 引用 |
| src/ 14 层代码分层规则 | `03-application_architecture.md` | §4 A-16 引用 |
| scripts/ 治理代码拓扑 | `03-application_architecture.md §5` | §2 Factory 层引用 |
| 数据层治理（PIT / Survivorship / Lineage）| `05-data_architecture.md §8` | §4 A-07 F 函数引用 |
| 集成契约治理 | `07-integration_architecture.md §6` | §4 A-15 OCP 引用 |
| 安全威胁治理（IAM / KMS / Audit）| `06-security_architecture.md`（skeleton）| §4 A-10 引用 |
| 运维治理（监控 / Runbook / DR）| `08-operations_architecture.md`（skeleton）| §6 T1-T6 联动 |
| 前端治理（ESLint / TypeScript strict / A11y）| `10-frontend_architecture.md` | §4 A-05 扩展 |
| **运行平面切分（Hot/Warm/Cold）** | **`04bis-runtime_planes.md`** | **§1.2bis 铁律** |
