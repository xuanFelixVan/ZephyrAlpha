---
ttl: permanent
---

# 治理报告索引（03_governance_reports）

> **目录定位**：归集 ZephyrAlpha 架构治理过程中的调研报告、病根分析与治本施工方案。每份报告为独立可引用真源；本索引仅作导航，不重复报告内容、不复制 frontmatter 元数据（ttl 等以各文件 frontmatter 为准）。
> **维护方式**：新增报告时在本索引追加条目；ttl 判定遵循 `ttl_vocabulary.yaml` 决策树（核心病根调研/裁定 → `permanent`；执行/延续施工计划 → `task_bound`）。

---

## 一、Schema 健康度治本系列

迁自 `.trae/documents/`（2026-06-26 规范化，#ARCH-014 Stage7.5）。围绕 `depgraph.db` schema 漂移与死表堆积问题的根因调研、修订执行计划与延续执行。

| # | 文档 | 标题 |
|---|------|------|
| 1 | [schema_health_root_cure_plan.md](schema_health_root_cure_plan.md) | Schema 健康度治本方案：depgraph.db 漂移修复与死表清理 |
| 2 | [schema_health_revised_execution_plan.md](schema_health_revised_execution_plan.md) | Schema 健康度治本方案：修订执行计划（v2） |
| 3 | [schema_health_continuation_plan.md](schema_health_continuation_plan.md) | Schema 健康度治本：延续执行计划（v2 续作） |

## 二、D-SIGNAL 改名系列

围绕 D-SIGNAL* 4 域改名（推翻裁定 #ARCH-002 / #ARCH-004）的执行方案与阻塞裁定。

| # | 文档 | 标题 |
|---|------|------|
| 4 | [d_signal_rename_plan.md](d_signal_rename_plan.md) | D-SIGNAL* 4 域改名执行方案（施工细节版 v2） |
| 5 | [d_signal_rename_blocker_adjudication.md](d_signal_rename_blocker_adjudication.md) | D-SIGNAL 改名任务卡执行阻塞——病根调研与裁定报告 |

## 三、DB 与架构病根调研

| # | 文档 | 标题 |
|---|------|------|
| 6 | [preexisting_db_issues_investigation_report.md](preexisting_db_issues_investigation_report.md) | 预存DB问题深度调研报告与治本方案 |
| 7 | [blueprint_placement_violations_root_cause_report.md](blueprint_placement_violations_root_cause_report.md) | 蓝图物理位置与 belongs_to 归属链违规——病根调研与裁定报告 |
| 8 | [vocabulary_sync_chain_repair_plan.md](vocabulary_sync_chain_repair_plan.md) | Vocabulary 自动同步链路断裂修复方案（施工细节版 v1） |
| 9 | [constraint_violations.md](constraint_violations.md) | 架构约束违规报告 |

## 四、统计与清理审查

| # | 文档 | 标题 |
|---|------|------|
| 10 | [capacity_report.md](capacity_report.md) | 域容量报告 |
| 11 | [design_vs_production.md](design_vs_production.md) | 设计态vs运营态统计报告 |
| 12 | [orphan_cleanup_audit.md](orphan_cleanup_audit.md) | 孤儿/僵尸清理统一审查文档 |

---

## 附：目录维护约定

- **新增报告**：放入本目录后，在本索引对应分类下追加表格行（# 号顺延）。
- **ttl 判定**：遵循 `ttl_vocabulary.yaml` 决策树——核心病根调研/裁定报告 → `permanent`；执行/延续施工计划 → `task_bound`。ttl 以各文件 frontmatter 为准，本索引不复制，避免双源漂移。
- **晋升门禁**：本目录属永久区（`docs/02_enterprise_architecture/`），新文件入库须经 GitCommitGateway `--allow-promote`（AI 不得自行批准）。
- **辅助脚本**：`_update_audit_doc.py` 为本目录报告自动更新工具，非报告本身，不入本索引。
