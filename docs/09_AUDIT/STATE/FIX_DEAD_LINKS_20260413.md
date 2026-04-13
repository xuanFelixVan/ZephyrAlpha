---
module_id: AUDIT_FIX_DEAD_LINKS_20260413
standard_type: audit_state
generated_by: scripts/audit/fix_dead_links.py
---

# 断链修复报告（apply）

> **生成时间**: 20260413
> **断链总数**: 4422

## 操作统计

| 操作 | 数量 |
|------|------|
| REPLACE | 4398 |
| REMOVE_LINK | 24 |

## 策略命中分布

| 策略 | 数量 |
|------|------|
| global_unique_basename | 2465 |
| global_closest_basename | 1722 |
| directory_guided_nav | 203 |
| kebab_case_fallback | 8 |

## 置信度分布（仅 REPLACE）

| 置信度 | 数量 |
|--------|------|
| medium | 2676 |
| low | 1722 |

## 高置信修复样本（共 0 条，展示前 30）


## 无法自动修复（REMOVE_LINK，共 24 条，展示前 30）

- `docs/03_TRADING_TACTICS/strategy-spec-s001.md`: `../02_FACTOR_LIBRARY/05_BACKTEST/`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260411.txt`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260411.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260410.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260411.txt`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260411.txt`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/REPO_GIT_TRACKED_FILES_20260410.txt`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260411.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_20260411.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/BASENAME_COLLISIONS_20260411.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_20260412.json`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl`
- `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE/repo-wide-file-governance-task-list.md`: `../../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260410.json`
- `docs/07_RESEARCH/INDEX.md`: `../02_FACTOR_LIBRARY/05_BACKTEST/`
- `docs/09_AUDIT/REPORTS/seven_dimensional_audit_report.md`: `../02_FACTOR_LIBRARY/05_BACKTEST/`
- `docs/09_AUDIT/STATE/directory_naming_violations_report_20260412.md`: `./module_designs/`
- `docs/09_AUDIT/STATE/directory_naming_violations_report_20260412.md`: `./12_MODULE_DESIGNS/`
- `docs/09_AUDIT/STATE/orphan_eradication_master_plan_20260413.md`: `./{f.name}`
- `docs/09_AUDIT/STATE/orphan_governance_program_20260413.md`: `path`
- `docs/09_AUDIT/STATE/orphan_governance_program_20260413.md`: `./{orphan_rel}.md`