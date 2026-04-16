---
module_id: AUDIT_REPO_THREE_ZONE_CLEANUP
version: 1.0.0
status: Active
created_date: '2026-04-16'
owner: Project Owner
---

# 仓库三区域清理执行记录（2026-04-16）

## 1. docs/07_RESEARCH/

- 已删除根目录重复文件 `experiment-tracking.md`，保留 `04_EXPERIMENT_TRACKING/experiment-tracking.md`。
- 已更新 `INDEX.md` 中 orphan 链接指向子目录版本。
- 已重写 `04_EXPERIMENT_TRACKING/README.md` 为单一合法 YAML frontmatter。

## 2. scripts/archive/ → scripts/hooks/ + scripts/ci_audit/

- **原因**：pre-commit 与 GitHub Actions 仍依赖 `scripts/archive/` 下脚本，不能直接整目录删除。
- **处置**：将 5 个 pre-commit 脚本复制至 `scripts/hooks/` 并修正 `PROJECT_ROOT`（`parents[2]`）；将 14 个 CI 脚本复制至 `scripts/ci_audit/`，修正硬编码 `D:\ZephyrAlpha` 与 `project_root`。
- 已更新：`.pre-commit-config.yaml`、`.github/workflows/document_quality_check.yml`、`doc-quality-check.yml`、`periodic-audit.yml`、`document_audit.yml`。
- 已更新：`scripts/governance/generate_blueprint_registry.py` 的 `SKIP_DIRS`（`scripts/ci_audit`）。
- 已删除：`scripts/archive/` 整目录（原 ~692 文件）。
- 已更新：`docs/subsystem-registry.yaml`（新增 `SCRIPTS_CI_AUDIT`，移除 `SCRIPTS_ARCHIVE`）。

## 3. Git refs

- `doc-repair-v5.1`、`audit/backup-20260408`、`docs/remediation-openclaw-20260408` 均已 **merge-base 确认为 master 祖先**（已合入）。
- 已删除本地分支：`backup/*`（37 个）、`backup-before-audit-cleanup-20260403`、`backup-before-refactoring`。
- 已删除本地标签：匹配 `audit-backup-*`、`backup-*`、`doc-milestone-*` 共 27 个。
- 已执行：`git gc --prune=now --aggressive`。

## 未按计划删除的分支（保留）

- `docs/blueprint-*`、`docs/blueprint-trae-*`、`traeredteam-*`、`construction_phase` 等未在计划中列为删除对象，**保留**。
