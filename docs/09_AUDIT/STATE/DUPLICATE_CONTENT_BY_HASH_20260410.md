---
module_id: DOCS_09_AUDIT_STATE_DUPLICATE_CONTENT_BY_HASH_20260410
standard_type: audit_state
applicable_scope: 内容级重复（按后缀白名单）
generated_date: '20260410'
generated_by: scripts/governance/scan_duplicate_file_content.py
---

# 内容重复扫描报告（SHA256）

> **机器真源**：[`DUPLICATE_CONTENT_BY_HASH_20260410.json`](./DUPLICATE_CONTENT_BY_HASH_20260410.json)
> **后缀白名单**：`md` ｜ **候选**：已跟踪 3187 + 未跟踪 0 ｜ **重复簇数**：5

## 说明

- Git **已跟踪** + `--others --exclude-standard` 未跟踪候选（与 `--ext` 匹配）。
- 每条路径在 JSON `members[].git_source` 中标注 **tracked** / **untracked**（便于优先处理「该入库却未 add」的重复）。
- **合并/删稿**须按 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3**（C1）与 [文件删除与保留裁决 Playbook](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/FILE_DELETION_OR_RETENTION_PLAYBOOK.md) 执行，勿仅凭本报告自动删除。

## 重复簇（仅 count>1）

### 簇 1 · `f01a374e9c81e3db…` · 3 个路径

- `docs/06_ARCHIVE/temp_pending/temp_alerting_blueprint.md` （tracked）
- `docs/06_ARCHIVE/temp_pending/temp_risk_budget.md` （tracked）
- `docs/06_ARCHIVE/temp_pending/temp_risk_budget_v2.md` （tracked）

### 簇 2 · `c086d9c9b58c78c2…` · 2 个路径

- `docs/06_ARCHIVE/temp_pending/temp_alternative.md` （tracked）
- `docs/06_ARCHIVE/temp_pending/temp_alternative_data.md` （tracked）

### 簇 3 · `08bc68f3a08b60e5…` · 2 个路径

- `docs/06_ARCHIVE/temp_pending/temp_blueprint.md` （tracked）
- `docs/06_ARCHIVE/temp_pending/temp_head_blueprint.md` （tracked）

### 簇 4 · `39d7e05eb225c4c4…` · 2 个路径

- `docs/06_ARCHIVE/temp_pending/temp_gap.md` （tracked）
- `docs/06_ARCHIVE/temp_pending/temp_gap_analysis.md` （tracked）

### 簇 5 · `89e79395c95a1832…` · 2 个路径

- `docs/06_ARCHIVE/temp_pending/temp_open_source.md` （tracked）
- `docs/06_ARCHIVE/temp_pending/temp_opensource.md` （tracked）
