---
ttl: task_bound
title: "F09 备份 3-2-1 双链——六库备份+CH vhdx 双链+离场月度复飞案卷"
session: zc-l01-20260927
---

# F09 备份 3-2-1 双链（复飞案卷，首次单独立卷）

> 前序：M1 册 04_cold_storage.md D9 半卷（备份族）+storage_map.md（INFRA-STORE-003 手册）；总册标"built（M5 补挖项）"；本卷按总册职责独立立卷+本日计划任务实测。

## 一、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游 | 全库对象：PG db_dumps/CH 数据（vhdx）/git bundles/离场盘/working_vault；backup.ps1 五阶段（:6 Stages：Pre-check→DB dump→CH backup→Code backup→Report） |
| 下游 | 灾备恢复（restore.ps1/restore_drill.py）；审计考古；G:/backup 五目录（ch_vm_backup/db_dumps/git_bundles/offrepo/predelete_deltas/working_vault 实列） |
| 自动触发 | 本日 schtasks 实测：ZephyrAlpha-DailyBackup **Ready**（06:00）/ZephyrAlpha-WeeklyVMBackup **Ready**（smart weekly）/ZephyrAlpha_LibraryLedgerBackup+Drill **Ready**/ZEPHYR-RESTORE-DRILL **Ready**；backup_ch_vm.ps1 刻意排除 ch_backup_disk.vhdx 防自我覆盖（:6-12） |
| 真源注册表 | INFRA-STORE-003（storage_map.md，MOD-INF-043，2026-09-23）；宪法 §7 存储分工（冷库=F:/zephyr_cold、备份总仓=G:/backup、CH 双链 F 主/G 二）；backup_config.yaml（scripts/backup/ 在盘实核） |
| 门禁质量尺 | backup_reconciler（清单 vs 实物对账）；library_ledger 演练对（Backup+Drill 双任务）；04 册 S3 勘误：storage_map.md:42 称"六阶段"vs 脚头实写 5 Stages——文档矛盾在案未修 |
| 运行状态 | **绿**：五计划任务全 Ready（零 Disabled，本日实测）；CH 双链 F ch_backup_disk.vhdx 主+G ch_backup_disk2.vhdx 二（storage_map.md:45）；G 侧旧 vault/offrepo 留观至 2026-09-28 到期（明日到期，挂 04 册 S5） |

## 二、子模块三级枚举

1. 备份核（scripts/backup/ 实列 11 件）：backup.ps1/backup_daily_trigger.ps1/backup_manual.ps1/backup_ch_vm.ps1/ch_vm_ssh.py/backup_config.yaml/backup_reconciler.py/restore.ps1/restore_drill.py/library_ledger_backup.py
2. CH 双链：F 主 vhdx+G 二 vhdx（backup_ch_vm.ps1 Full 模式停机 30-90min Owner 在场；boot.vhdx+data.vhdx 555GB）
3. 演练面：ZEPHYR-RESTORE-DRILL+LibraryLedgerDrill 双计划任务（Ready 实测）；h1_redis 三件 e2e 测试在册（test_h1_*）
4. 离场 3-2-1：Owner 月度离场盘（storage_map 六步流程）；predelete_deltas 删除前增量
5. 相邻账：F116 四盘存储地图（M 段横切）=布局真源横切段，本卷不重复立册；G 侧 zephyr_cold 只读保留至 2026-10-21（09 册）

## 三、接线四态独立复核

- 总册：built（M5 补挖项）/P1/D9。独立复核：**built 成立**（五任务 Ready+双链在册+演练对在册）；"M5 补挖项"指备份冷储性能水位（归 M5 车道），非本环节缺件。
- 勘误⑭（04 册 S3 传递）：storage_map.md "六阶段"vs backup.ps1 五 Stages 文档矛盾未修（本日复核仍在）——修册可直开。
- 勘误⑮：M5 接线普查 §1.6 D 类"heartbeat_daemon 无对应计划任务"与备份面无关（属 F13 算力心跳域），防止本环节误挂该账。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| B1 | "六阶段 vs 五 Stages"修册 | 施工：safe_write_text 改 storage_map.md | P2 |
| B2 | G 侧旧 vault/offrepo 留观 2026-09-28 到期删 | 挂起+解锁=明日日历到期（Owner 定案执行） | P1 |
| B3 | vhdx 压缩=Owner 在场窗 | Owner 门（storage_map 阶段 7） | P2 |
| B4 | 阶段 5 F 旧 CH 链盘摘除评估（~2026-10-05） | 挂起+解锁=日历 | P2 |
| B5 | backup_reconciler 与 rolling_archive_reconciler 对账内核重复 | 施工：共享对账内核（04 册提速项，内收判据） | P2 |

## 五、自审闸三态

挖干可施工（本日五任务实测+脚本族实列双源）；B1/B5 可施工；B2/B4 挂起日历；B3 Owner 门。首次单独立卷；04 册沿用处已注明。

## 六、复跑命令

```bash
powershell -NoProfile -Command "Get-ScheduledTask |? {\$_.TaskName -match 'Backup|RESTORE|LibraryLedger'} | ft TaskName,State"
ls scripts/backup/ G:/backup/
sed -n '1,12p' scripts/backup/backup_ch_vm.ps1       # 排除自覆盖
grep -n "vhdx" docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md  # 双链 :45
sed -n '6p' scripts/backup/backup.ps1                # 5 Stages 原文
```
