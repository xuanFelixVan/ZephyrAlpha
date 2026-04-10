---
standard_type: audit_state
applicable_scope: 内容级重复（按后缀白名单）
generated_date: '20260411'
generated_by: scripts/governance/scan_duplicate_file_content.py
---

# 内容重复扫描报告（SHA256）

> **机器真源**：[`DUPLICATE_CONTENT_BY_HASH_20260411.json`](./DUPLICATE_CONTENT_BY_HASH_20260411.json)
> **后缀白名单**：`md` ｜ **候选**：已跟踪 3187 ｜ **重复簇数**：0

## 说明

- 仅 **Git 已跟踪**且后缀匹配的文件。
- 每条路径在 JSON `members[].git_source` 中标注 **tracked** / **untracked**（便于优先处理「该入库却未 add」的重复）。
- **合并/删稿**须按 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3**（C1）与 [文件删除与保留裁决 Playbook](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/FILE_DELETION_OR_RETENTION_PLAYBOOK.md) 执行，勿仅凭本报告自动删除。

## 读盘失败（路径不在工作区或非文件）

- `docs/06_ARCHIVE/temp_pending/temp_alerting_blueprint.md`
- `docs/06_ARCHIVE/temp_pending/temp_alternative_data.md`
- `docs/06_ARCHIVE/temp_pending/temp_gap_analysis.md`
- `docs/06_ARCHIVE/temp_pending/temp_head_blueprint.md`
- `docs/06_ARCHIVE/temp_pending/temp_opensource.md`
- `docs/06_ARCHIVE/temp_pending/temp_risk_budget_v2.md`

## 重复簇（仅 count>1）
