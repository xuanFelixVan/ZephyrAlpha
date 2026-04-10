# 根目录临时 Markdown 归档（整改 P0-A）

根目录 `temp_*.md` 已于 2026-04-08 迁入本目录，避免污染仓库根与编码损坏文件长期暴露。

若某文件已有正式版替代，可删除对应副本；若需恢复 UTF-8 正文，请单独转码后并入 `docs/` 正式路径。

## C1 同内容合并记录（2026-04-11）

依据 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3.2** 与 **宽松**归档策略（§3.1 Owner 裁定），对 `DUPLICATE_CONTENT_BY_HASH_20260410` 所报簇保留单一副本，已删字节级相同副件：

| 保留（canonical） | 已删除副本 |
|-------------------|------------|
| `temp_risk_budget.md` | `temp_alerting_blueprint.md`、`temp_risk_budget_v2.md` |
| `temp_alternative.md` | `temp_alternative_data.md` |
| `temp_blueprint.md` | `temp_head_blueprint.md` |
| `temp_gap.md` | `temp_gap_analysis.md` |
| `temp_open_source.md` | `temp_opensource.md` |

验证：`python scripts/governance/sentinel_l1_governance_scan.py`（Invalid links = 0）；`scan_duplicate_file_content.py --ext md --date 20260411` → [`DUPLICATE_CONTENT_BY_HASH_20260411.md`](../../09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_20260411.md)（`duplicate_clusters=0`）。
