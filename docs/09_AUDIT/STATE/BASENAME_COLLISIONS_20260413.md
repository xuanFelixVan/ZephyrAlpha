---
standard_type: audit_state
applicable_scope: 同名不同路径（basename · C2 输入）
generated_date: '20260413'
generated_by: scripts/governance/scan_basename_collisions.py
---

# Basename 碰撞报表（同名不同路径）

> **机器真源**：[`BASENAME_COLLISIONS_20260413.json`](./BASENAME_COLLISIONS_20260413.json)
> **范围**：docs/ ｜ **后缀**：`md`
> **候选路径数**：3366 ｜ **发生碰撞的 basename 数**：10

## 说明

- 与 **C1（内容 hash 相同）** 不同：basename 相同**不**表示正文相同，**禁止自动合并**；处置见 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3.3**。
- 下列 **`INDEX.md` / `README.md` 等**在机构式文档树中**常**多份并存；默认单独统计，避免与「意外同名」混淆。

## 摘要

| 类别 | basename 数 |
|------|------------:|
| 非导航名（优先人工审） | 6 |
| 导航名（`changelog.md, contributing.md, index.md, license.md, readme.md, sitemap.md`） | 4 |

## 非导航名碰撞（逐条展开）

### `correlation-analysis.md` · 2 条路径

- `docs/07_RESEARCH/02_EXPLORATORY_ANALYSIS/correlation-analysis.md`
- `docs/09_ARCHIVE/factor_library/correlation-analysis.md`

### `deep-audit-report-v2-20260407.md` · 2 条路径

- `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v2-20260407.md`
- `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/deep-audit-report-v2-20260407.md`

### `deep-audit-report-v4-20260407.md` · 2 条路径

- `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/deep-audit-report-v4-20260407.md`
- `docs/09_AUDIT/REPORTS/deep-audit-report-v4-20260407.md`

### `experiment-tracking.md` · 2 条路径

- `docs/07_RESEARCH/04_EXPERIMENT_TRACKING/experiment-tracking.md`
- `docs/07_RESEARCH/experiment-tracking.md`

### `statistical-tools.md` · 2 条路径

- `docs/07_RESEARCH/02_EXPLORATORY_ANALYSIS/statistical-tools.md`
- `docs/09_ARCHIVE/blueprints/statistical-tools.md`

### `technical-indicators.md` · 2 条路径

- `docs/03_TRADING_TACTICS/99_ARCHIVE/technical-indicators.md`
- `docs/09_ARCHIVE/TECHNICAL_SPECIFICATIONS/technical-indicators.md`

## 导航名碰撞（统计表）

| basename | 路径条数 |
|----------|----------:|
| `INDEX.md` | 265 |
| `README.md` | 115 |
| `SITEMAP.md` | 5 |
| `CHANGELOG.md` | 2 |
