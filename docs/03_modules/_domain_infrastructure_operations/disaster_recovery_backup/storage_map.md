---
module_id: MOD-INF-043
title: "storage_map — 四盘存储地图（INFRA-STORE-003 永久手册）"
doc_type: register
ttl: permanent
status: Active
version: "1.0.0"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
date: "2026-09-23"
last_updated: "2026-09-23"
summary: "四盘分工与存储地图永久手册（INFRA-STORE-003）：D=生产、F=冷储专项、G=备份总仓、offsite=Owner 月度离场盘；冷库/冷储/备份/backup/四盘/storage 关键词锚点；提炼自磁盘重整战役 a3 定案"
tags: [storage, backup, cold-storage, four-drive, INFRA-STORE-003, MOD-INF-043]
responsibility_domain: 
design_maturity: production
---

# storage_map — 四盘存储地图（INFRA-STORE-003 永久手册）

> **读者**：任何需要"找冷库 / 找备份 / 判断数据在哪块盘"的 AI 或人。
> **真源**：架构登记 = `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml` 的 **INFRA-STORE-003** 条目；本手册是其"怎么用"面的永久提炼。
> **知识出处**：磁盘重整战役 `docs/_working/disk_reorg_campaign/a3_safe_construction_checklist.md`（Owner 2026-09-21 定案，task_bound TTL——永久知识以本手册为准，战役件过期不追）。

## 1. 四盘分工（一句话版）

| 盘 | 角色 | 一句话 |
|---|---|---|
| **D** | 生产 | 工作区 + CH 热层，唯一活跃写入面 |
| **F** | 冷储专项（纯冷库） | `F:/zephyr_cold`——CH 老分区 Parquet 冷库 + 研报原文；只进不改 |
| **G** | 备份总仓 | `G:/backup`——一套完整备份（vault/db_dumps/git_bundles/offrepo/ch_vm_backup 五目录） |
| **offsite** | 离场盘 | Owner 手动月度拿第三块盘离场（手册=`docs/_working/disk_reorg_campaign/offsite_monthly_manual.md`，≥2T 专盘建议） |

此组合 = 标准 **3-2-1**：3 副本（D+G+离场）/ 2 介质（内置+USB）/ 1 离场。

## 2. 关键词→落点速查

| 你在找 | 去哪 |
|---|---|
| 冷库 / 冷储 / 历史分区 Parquet | `F:/zephyr_cold`（DuckDB 直读 Parquet；清单 `archive_manifest.jsonl`） |
| 冷库归档/恢复操作 | `python scripts/ch/archiver.py archive-range\|list\|stats\|restore`（五重安全阀 v1.3.0 契约） |
| 备份 / backup / 还原 | `G:/backup`（`scripts/backup/backup.ps1` 六阶段备份；`restore.ps1` 恢复） |
| CH 备份 | 双链：F 盘 `ch_backup_disk.vhdx`（主链）+ G 盘 `ch_backup_disk2.vhdx`（第二链，SCSI 热挂） |
| 代码仓备份 | `G:/backup/git_bundles`（留 2 份） |
| 工作区快照 | `G:/backup/working_vault`（14 天滚动） |
| DB 导出 | `G:/backup/db_dumps`（14 天滚动） |
| 离场月度流程 | offsite 手册六步（每月一次，Owner 手动） |
| 保留期/删除政策 | `docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml` |

## 3. 铁律（数据第一公理）

1. **任何 drop/删除前必须有两份验证过的副本**（对账三件套：文件数+字节数+5% 抽样 hash 全平）。
2. **先 copy → 后 verify → 最后才动源**；删源前留观 ≥7 天（冷储原件 30 天）。
3. 冷储 immutable、append-only（数据永不删除、仅分层，INV-RET-001~003）。
4. 备份版本化：working_vault 14 天 / db_dumps 14 天 / git bundle 留 2 份 / CH 双链。
5. 计划任务 `ZephyrAlpha-DailyBackup` 是备份链自动触发器（06:00 全自动）——禁长期暂停。

## 4. 遗留与待办指针（截至 2026-09-23）

- 阶段 5（~2026-10-05）：F 旧 CH 链盘（`ch_backup_disk.vhdx`）摘除评估 + `ch_vm_backup` B 瘦身裁决。
- 阶段 7：vhdx 压缩（需 Owner 在场窗，禁未批执行）。
- F 侧旧 vault/offrepo 留观至 2026-09-28 到期删。
- 施工与对账流程细则见战役件 a3（task_bound）；永久通则以本手册 §3 为准。
