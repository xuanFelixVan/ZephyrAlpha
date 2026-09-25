---
ttl: task_bound
lane: M1 数据链
segment: D8 冷库归档运维 + D9 备份 3-2-1 双链（骨架册标注"未归属"，本册主张归 M1）
mined_at: 2026-09-25
session: st-commitspeed-tbl-20260924
---

# 04_cold_storage — 冷储/备份段作业簿（D8/D9）

> 归属声明：骨架册 00_skeleton_fullflow.md D8/D9 归属列="未归属"。本车道按任务令（"数据链：采集→清洗→入库→**冷储**→交叉轴"）挖干并**主张收编**，请总筹在车道注册表改注 M1。

## 一、环节定义与边界

一句话：CH 老分区 export→verify→drop 三阶段进 F:/zephyr_cold Parquet 冷库；全资产 3-2-1 备份（D 生产+G 备份总仓+Owner 月度离场盘），CH VM vhdx 双链（F 主/G 二）。
- **供料方**：03_ch_warehouse 的老分区；库外语料抓取物。
- **消费方**：恢复演练/审计考古/深史回看（bdpan tick 回补先例 3.19 亿行）。

## 二、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游输入 | CH c1_market 老分区（ETF/LOF 分钟史已归档：F:/zephyr_cold/50_archive/c1_market/ 实列 10 目录）；语料/web 快照（20_raw A-J 十大类+30_corpus 实列在盘） |
| 下游消费 | restore_partition 回灌 CH（archiver.py:793）；RETENTION.md 保留政策；data_retention_contract.yaml（storage_map.md:50 指针） |
| 自动化触发 | ZephyrAlpha-DailyBackup **Ready**（06:00 全自动，storage_map.md:58 "禁长期暂停"）；ZephyrAlpha-WeeklyVMBackup Ready（backup_ch_vm.ps1 smart weekly）；ZephyrAlpha_LibraryLedgerBackup/Drill Ready（library 台账备份+演练）；rolling_archive_reconciler.py（归档对账）。归档本身=**手动/事件触发**（archiver CLI），无常驻 |
| 真源与注册表 | 架构登记=infrastructure_registry.yaml **INFRA-STORE-003** 条目；用法手册=docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md（MOD-INF-043，2026-09-23）；归档清单=F:/zephyr_cold/00_manifest/drawers.jsonl（5 行实读）+archiver 自身 manifest（_append_manifest :456）；保留合同=docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml |
| 门禁与质量尺 | 五重安全阀（storage_map.md:43 "v1.3.0 契约"）：export→verify（文件数+字节数+5% 抽样 hash 对账三件套）→drop；数据第一公理（storage_map.md §3）：drop 前两份验证副本/删源留观≥7 天/冷储原件 30 天/immutable append-only；RULE-DATA-OPS 三步验证适用于一切破坏性操作 |
| 当前运行状态 | **绿（带 4 处小账）**。F:/zephyr_cold 实列：00_manifest/10_inbox(空)/20_raw(A-J，A_market 空)/30_corpus(A-J+announcements)/40_migration/50_archive(c1_market 10 目录+by_project altdata_p1_p2_20260924 等 6 项)/90_tmp/library/README/RETENTION；G:/backup 实列五目录：ch_vm_backup/db_dumps/git_bundles/offrepo/predelete_deltas/working_vault；CH 双链：F ch_backup_disk.vhdx 主+G ch_backup_disk2.vhdx 二（storage_map.md:45；backup_ch_vm.ps1:7 VM 备份刻意排除 ch_backup_disk.vhdx 防自我覆盖） |

## 三、子模块清单

| 模块 | 入口 | 状态 |
|---|---|---|
| archiver.py | scripts/ch/archiver.py（920 行）：archive-range/list/stats/restore/export-only；export_partition :191/verify_partition :383（5% 抽样 hash+_compare_sample_rows :320）/drop_partition :435（dry_run 参数）/restore :793 | production（v1.3.0 契约） |
| rolling_archive_reconciler.py | scripts/ch/（归档对账） | production |
| storage_tiering.py | src/zephyr/data/storage_tiering.py | **已退役（裁定#383，2026-09-20）**：纸面模块零消费，物理摘除归 src/zephyr/data 域后续批次；摘除前禁新增调用方（模块头原文）——净零内收正面案例 |
| backup.ps1 / restore.ps1 / backup_daily_trigger.ps1 / backup_reconciler.py | scripts/backup/（脚本头 :6 Stages: Pre-check→DB dump→CH backup→Code backup→Report） | production |
| backup_ch_vm.ps1 / ch_vm_ssh.py | VM 整机备份（boot.vhdx+data.vhdx 555GB，:6-12；Full 模式停机 30-90min Owner 在场） | production |
| restore_drill.py / ZEPHYR-RESTORE-DRILL 计划任务 | 恢复演练 Ready | production |
| library_ledger_backup.py | library 台账备份（计划任务在册） | production |
| 冷库抽屉体系 | F:/zephyr_cold 00_manifest/drawers.jsonl（20_raw/30_corpus/研报库 F6万+E3万 迁入计划） | production（altdata 语料线在用） |

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| S1 | drawers.jsonl 第 5 行 path 写 **G:/zephyr_cold/30_corpus/...**——但抽屉体系在 F 盘；manifest 记录路径与实物盘符矛盾 | 登记时笔误或曾双盘并存未校准 | 核实物后修正 manifest 行（safe_write_text CAS） | 0.2 天 | 是 |
| S2 | storage_map.md:42 称冷库清单="archive_manifest.jsonl"（F 根）——根目录实查无此文件，实际清单=00_manifest/drawers.jsonl（archiver 的 manifest 另在其写目录） | 手册措辞与实物漂移 | 手册行改指 00_manifest/drawers.jsonl | 0.1 天 | 是 |
| S3 | storage_map.md:44 称 backup.ps1"六阶段备份"，脚本头实写 5 Stages（:6） | 文档矛盾=事故（宪法 §4.4） | 以脚本为准改手册或脚本补阶段 | 0.1 天 | 是 |
| S4 | storage_tiering.py 已裁退役未物理摘除（文件+re-export 仍在 src 树） | 裁定#383 明示"归后续批次执行" | 按 WO 批次摘除+depgraph 重建 | 0.5 天 | 是（施工批） |
| S5 | 遗留在案（storage_map.md:60-64）：阶段 5（~2026-10-05）F 旧 CH 链盘摘除评估+ch_vm_backup B 瘦身裁决；阶段 7 vhdx 压缩=Owner 在场窗；F 侧旧 vault/offrepo 留观至 2026-09-28 到期删 | 有日历有主人，非病灶 | 到期执行即可 | — | 登记转 M5 提醒 |
| S6 | 病灶闭环核验：①tick 21 月误删事故→"drop 前三件套对账"铁律+archiver 五重安全阀**已闭环**；②2026-09-21 磁盘重整战役定案→storage_map 永久手册**已闭环**（3-2-1+双链+离场六步） | — | — | — | — |

## 五、提速与合并机会

1. 归档触发自动化：ETF/LOF 分钟史归档先例是手动 CLI——可按 RETENTION 政策表驱动（lifecycle: hot_90d 等字段已在 business_data_categories.yaml）挂月班自动出归档候选单（dry_run 递 Owner 批）。
2. backup_reconciler 与 rolling_archive_reconciler 同为"清单 vs 实物对账"，可共享对账内核。

## 六、自审闸三态

**挖干可施工**（S1-S4 修正/摘除可直开；S5 到期事项挂日历；归档自动化候选单生成可施工，实际 export/drop 仍 Owner 门）。

## 七、复核命令

```bash
ls F:/zephyr_cold/ F:/zephyr_cold/00_manifest/ F:/zephyr_cold/50_archive/c1_market/ G:/backup/
cat F:/zephyr_cold/00_manifest/drawers.jsonl           # 5 行，第 5 行 G: 笔误
grep -n "vhdx" docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md  # 双链 :45
sed -n '1,12p' scripts/backup/backup_ch_vm.ps1          # 排除自覆盖
grep -n "已退役" src/zephyr/data/storage_tiering.py      # 裁定#383
python scripts/ch/archiver.py list | head               # 归档清单（只读）
powershell -NoProfile -Command "Get-ScheduledTask |? {$_.TaskName -match 'Backup|RESTORE'} | ft TaskName,State"
```
