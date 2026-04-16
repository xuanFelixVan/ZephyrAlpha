---
module_id: ARCHIVE_SCRIPTS_INDEX
version: 1.0.0
status: Active
created_date: 2026-04-16
last_updated: 2026-04-16
owner: AI Assistant
layer: cross_layer
---

# `scripts/archive/` 归档脚本索引

> **⚠️ 警告 (WARNING)**
> 本目录是已废弃或被替代脚本的**墓地 (Graveyard)**。
> **AI 行为准则**：禁止运行本目录下的任何脚本！如果你在搜索时命中了这里的代码，请立即查阅 `docs/02_ARCHITECTURE/EXECUTABLE_ASSET_REGISTRY.md` 寻找活跃的替代工具。

---

## 归档脚本替代关系映射表

以下是本目录中常见脚本类别的活跃替代品：

| 归档脚本模式/名称 | 状态 | 当前活跃替代工具 |
|------------------|------|-----------------|
| `link_fixer.py`, `link_checker.py`, `smart_link_fixer.py`, `enhanced_dead_link_detector.py` 等 15+ 个链接脚本 | ❌ 已废弃 | `scripts/audit/fix_dead_links.py` |
| `duplicate_detector.py`, `detect_duplicate_documents.py`, `clean_duplicate_files.py` 等 5+ 个重复检测器 | ❌ 已废弃 | `scripts/audit/scan_duplicate_file_content.py` |
| `weekly_audit_*.py`, `audit_scheduler.py`, `overnight_audit_runner.py` 等 10+ 个调度器 | ❌ 已废弃 | `.github/workflows/periodic-audit.yml` |
| `round*_issue_fixer.py`, `p0_issue_fixer.py` 等多轮问题修复脚本 | ❌ 已废弃 | 对应问题域的最新活跃脚本 (见资产清单) |
| `add_missing_module_ids.py` (原 audit/ 版) | ❌ 已废弃 | `scripts/governance/backfill_missing_module_id.py` |
| `strict_orphan_inbound_scan.py` (原 audit/ 版) | ❌ 已废弃 | `scripts/audit/scan_index_health.py` |

## `legacy_exact_matches/` 子目录说明

为了防止 AI 搜索时出现同名混淆，我们将以下曾与活跃脚本**完全同名**的旧版本移入了 `legacy_exact_matches/` 子目录：

- `sentinel_l1_governance_scan.py`
- `verify_01_blueprints_index_links.py`
- `verify_manifest_paths_strict.py`
- `scan_basename_collisions.py`
- `scan_index_health.py`
- `scan_duplicate_file_content.py`
- `fix_dead_links.py`
- `triage_blueprint_d_overlap_pairs.py`

如果你需要查看或修改上述脚本，**请务必去 `scripts/audit/` 或 `scripts/governance/` 目录下寻找它们的活跃版本**。