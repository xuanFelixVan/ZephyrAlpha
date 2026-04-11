---
module_id: ARCHIVE_DOUBLE_YAML_DRYRUN_SAMPLE_001
version: 1.0.1
status: Active
created_date: 2026-04-10
last_updated: '2026-04-11'
owner: 仓库 Owner
responsibility:
  - 说明本目录为历史 dry-run 产物，非活动审计 STATE
standard_type: 归档说明
applicable_scope: 双 YAML 修复演练样本
---

# 双 YAML dry-run 样本（2026-04-08）

本目录含 **50** 个 `.diff` 文件，为 [OpenClaw 整改执行手册](../../09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md) 所述 **dry-run** 输出留存；已从 `docs/09_AUDIT/STATE/` **迁出**至 `06_ARCHIVE/`，避免与当前 STATE 快照混淆。

如需复跑同类样本，请在新批次目录下输出，并更新程序文档中的路径说明。

---

## 上级与接力

- [06_ARCHIVE 索引](../INDEX.md)
- [全仓库文件治理任务清单 §7](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md#7-一次性深度治理目录队列与退出标准)
- [治理工具总索引](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)
- [09_AUDIT STATE 索引](../../09_AUDIT/STATE/INDEX.md)
- [OpenClaw 整改执行手册](../../09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md)

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（最新）**：[../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260423.md](../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260423.md)（`scan_index_health.py --prefix docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample --date 20260423`；**zero_inbound=0**；候选 md **1**；目录内其余为 `.diff`，不在本扫描口径内）
- **rollup（深度 3 前缀条数）**：[../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md](../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md)（检索 `docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample` **51** 条）
