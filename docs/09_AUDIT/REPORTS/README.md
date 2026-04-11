---
module_id: 09_AUDIT_REPORTS_README_001
version: 1.0.2
status: Active
created_date: 2026-04-12
last_updated: '2026-04-14'
owner: 文档治理系统
responsibility:
  - 本目录门面说明与导航入口（非长列表真源）
standard_type: 索引文档
applicable_scope: docs/09_AUDIT/REPORTS
---

# REPORTS — 审计报告区（门面）

本目录存放**审计与进度类报告**（体量较大）。**完整可点列表**以 [`INDEX.md`](./INDEX.md) 与分组表 [`INDEX_GROUPED_REPORTS_20260408.md`](./INDEX_GROUPED_REPORTS_20260408.md) 为准。

## 推荐阅读顺序

1. [`INDEX_GROUPED_REPORTS_20260408.md`](./INDEX_GROUPED_REPORTS_20260408.md) — 按主题分组浏览  
2. [`INDEX.md`](./INDEX.md) — 全量索引与快速入口  
3. 夜间审计快照：[`../STATE/overnight_runs/INDEX.md`](../STATE/overnight_runs/INDEX.md)  
4. 整仓按目录尽治（REPO_WIDE **§7**）：[`../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md`](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md#7-一次性深度治理目录队列与退出标准)

## 目录体量（与仓库快照对齐）

- **深度 3 前缀路径数**：以 `git ls-files` rollup 为准 → **最新** [`../STATE/REPO_DIRECTORY_ROLLUP_20260414.md`](../STATE/REPO_DIRECTORY_ROLLUP_20260414.md)（**`docs/09_AUDIT/REPORTS` = 499** 条，快照 `20260414`）；历史 [`20260413`](../STATE/REPO_DIRECTORY_ROLLUP_20260413.md)

## Git 列表与路径字面值（锚点 B）

统计或脚本消费 **`git ls-files`** 时，建议 `git -c core.quotePath=false …` 或使用 **`-z` + UTF-8**，避免非 ASCII 路径被 C-quoting 后与磁盘路径对账失败。登记与回放见 [`../STATE/GIT_TRACKED_PATH_ANOMALIES_20260411.md`](../STATE/GIT_TRACKED_PATH_ANOMALIES_20260411.md)。

## 索引健全性（本前缀）

- **零入链扫描（最新 · 20260414）**：[`../STATE/INDEX_HEALTH_ORPHAN_20260414.md`](../STATE/INDEX_HEALTH_ORPHAN_20260414.md)（`scan_index_health.py --prefix docs/09_AUDIT/REPORTS --date 20260414`；**zero_inbound=0**）
- **历史快照**：[`../STATE/INDEX_HEALTH_ORPHAN_20260412.md`](../STATE/INDEX_HEALTH_ORPHAN_20260412.md)（`20260412`）
- **同目录旁系**：`docs/09_AUDIT/STATE` 前缀的健全性为**另一份**机器报告 → [`../STATE/INDEX_HEALTH_ORPHAN_20260413.md`](../STATE/INDEX_HEALTH_ORPHAN_20260413.md)（日期 **20260413**，勿与上条 REPORTS 报告混读）

## 上级入口

- [审计域总索引 `../INDEX.md`](../INDEX.md)  
- [STATE 子域索引 `../STATE/INDEX.md`](../STATE/INDEX.md)（机器产出 / 台账 / rollup）  
- [治理工具总索引 `GOVERNANCE_TOOLS_INDEX.md`](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)  
- [L1 治理快照（20260408）`SENTINEL_L1_SCAN_20260408`](../STATE/SENTINEL_L1_SCAN_20260408.md)  
- [文档总入口 `../../INDEX.md`](../../INDEX.md)
