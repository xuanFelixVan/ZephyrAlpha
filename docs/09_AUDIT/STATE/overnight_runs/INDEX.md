---
module_id: 09_AUDIT_STATE_OVERNIGHT_RUNS_INDEX_001
version: 1.0.1
status: Active
created_date: 2026-04-08
last_updated: 2026-04-13
owner: 文档治理系统
standard_type: 索引文档
applicable_scope: overnight_runs
---

# overnight_runs 索引（夜间审计产物入口）

> **说明**：本目录存放“夜间批量审计/扫描”的**产物快照**，用于追溯与对账。  
> 这些文件通常不应该被当作“正文文档”阅读入口，因此必须通过本索引集中导航，避免成为事实孤儿。

## 上级与接力

- [返回 STATE 目录索引 `../INDEX.md`](../INDEX.md) ｜ [审计域总索引 `../../INDEX.md`](../../INDEX.md) ｜ [REPORTS 门面 `../../REPORTS/README.md`](../../REPORTS/README.md)  
- [自主接力运行队列（Phase B）`../../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/AUTONOMOUS_GOVERNANCE_RUN_QUEUE.md`](../../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/AUTONOMOUS_GOVERNANCE_RUN_QUEUE.md) ｜ [治理工具总索引 `../../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md`](../../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)  
- **仓库内最新 L1 汇总快照（非某一 overnight 批次）**：[../SENTINEL_L1_SCAN_20260408.md](../SENTINEL_L1_SCAN_20260408.md)

## 运行批次

> 命名约定：`YYYYMMDD_HHMMSS/`

- [`20260408_033240/`](./20260408_033240/)
  - 汇总：[`CONSOLIDATED_REPORT_FOR_AI_20260408_033240.md`](./20260408_033240/CONSOLIDATED_REPORT_FOR_AI_20260408_033240.md)
  - L1：[`sentinel_l1_scan_20260408_033240.md`](./20260408_033240/sentinel_l1_scan_20260408_033240.md)
  - 细节：[`invalid_links_detail_20260408_033240.md`](./20260408_033240/invalid_links_detail_20260408_033240.md) / [`module_id_duplicates_detail_20260408_033240.md`](./20260408_033240/module_id_duplicates_detail_20260408_033240.md) / [`md_by_subdir_20260408_033240.md`](./20260408_033240/md_by_subdir_20260408_033240.md)

- [`20260408_022356/`](./20260408_022356/)
  - 汇总：[`CONSOLIDATED_REPORT_FOR_AI_20260408_022356.md`](./20260408_022356/CONSOLIDATED_REPORT_FOR_AI_20260408_022356.md)
  - L1：[`sentinel_l1_scan_20260408_022356.md`](./20260408_022356/sentinel_l1_scan_20260408_022356.md)
  - 细节：[`invalid_links_detail_20260408_022356.md`](./20260408_022356/invalid_links_detail_20260408_022356.md) / [`module_id_duplicates_detail_20260408_022356.md`](./20260408_022356/module_id_duplicates_detail_20260408_022356.md) / [`md_by_subdir_20260408_022356.md`](./20260408_022356/md_by_subdir_20260408_022356.md)

- [`20260408_021344/`](./20260408_021344/)
  - 汇总：[`CONSOLIDATED_REPORT_FOR_AI_20260408_021344.md`](./20260408_021344/CONSOLIDATED_REPORT_FOR_AI_20260408_021344.md)
  - L1：[`SENTINEL_L1_SCAN_20260408_20260408_021344.md`](./20260408_021344/SENTINEL_L1_SCAN_20260408_20260408_021344.md)
  - 细节：[`invalid_links_detail_20260408_021344.md`](./20260408_021344/invalid_links_detail_20260408_021344.md) / [`module_id_duplicates_detail_20260408_021344.md`](./20260408_021344/module_id_duplicates_detail_20260408_021344.md) / [`MD_FILES_BY_SUBDIRECTORY_20260408_021344.md`](./20260408_021344/MD_FILES_BY_SUBDIRECTORY_20260408_021344.md)

## 使用建议

- **日常阅读**：优先读每批次的 `CONSOLIDATED_REPORT_FOR_AI_<run_id>.md`（basename 带 run_id，避免跨批次 C2 碰撞）。  
- **问题定位**：需要深入再看同目录下 `invalid_links_detail_<run_id>.md` / `module_id_duplicates_detail_<run_id>.md`。  
- **历史对账**：需要对比不同批次的 `sentinel_l1_scan_*.md` 指标变化。  

