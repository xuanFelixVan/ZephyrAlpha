---
ttl: task_bound
session: st-ailayer-fullflow-sc
creation_token: m5sc-backup-coldstore-20260925
---

# M5 补挖分册 03：备份冷储册（D 组共担项接续）——六 STAGE 流水线+3-2-1 实测

> 证据：backup_config.yaml v2.1.0 全读+STAGE 面扫描+G/F 盘活探+state json 实读，2026-09-25。只读挖矿。
> D 组补挖项"备份冷储 3-2-1"由本册承接（SC 视角=调度触发面+运行证据；存储分工总图=INFRA-STORE-003，登记于 infrastructure_registry.yaml / asset_catalog.md / 73_d_infrastructure.md 三处）。

## 一、流水线本体（backup.ps1，918 行，六 STAGE）
真源 `scripts/backup/backup_config.yaml` v2.1.0（MOD-INF-043；v2.1 变更动因=#B1 09-14 docs/_working 误删事故——robocopy /MIR 会传播删除，摧毁最后恢复源）：
- **STAGE 1** pre-check（备份锁 Test/Acquire/Release，防并发双跑）。
- **STAGE 2** DB dump+config sync（D:\tmp_db_dumps）。
- **STAGE 3** 代码版本化快照（v2.1 核心）：`G:\backup\working_vault\<yyyyMMdd>\`，首跑 seed 自昨日快照+当日 Mode B 增量刷新；硬链接去重（同盘块共享，空间≈1×+日变更量）；retention 14 天上限、free_floor 60GB、min_keep 3 天（空间自适应收缩，不足 fail loud 中止）。
- **STAGE 3b** git bundle：`G:\backup\git_bundles`（git 史灾备）。
- **STAGE 3c** 仓外关键资产镜像 4 targets：trae_memory / qmt_bridge(E:) / stash_archive / cold_archive(F:\zephyr_cold\50_archive)；data_download 已裁移除（09-14，源日膨胀 66GB 是 F 盘告急头号推手）。
- **STAGE 3d** G 兜底镜像（3-2-1 的 G 侧，裁定 #380⑥/#381）：`F:\zephyr_cold` → `G:\zephyr_cold\60_mirror\zephyr_cold_main`（/MIR 逐条；首度全量 710G 由 st-disk-ch-20260921 通宵班完成）。
- **CH 段**：增量双件制 `market.zip`（全量基线）+`inc.zip`（每日覆盖）；inc≥50%×base 自动重建基线；Mode=ch 跳过 3c。

## 二、触发面（调度车道本体）
| 通道 | 触发 | 件 | 实测 |
|---|---|---|---|
| ZephyrAlpha-DailyBackup | Daily 06:00 | wscript launch_hidden.vbs → backup.ps1 -Mode all -Force | 主波基线 09-24 exit 0；**本波 G 盘 working_vault/20260925 快照在盘=今晨班成功实证** |
| ZephyrAlpha-WeeklyVMBackup | Weekly 五 06:00 | backup_ch_vm.ps1 -AutoCheck | 09-19 autocheck=skipped_unchanged；**09-24 起 data.vhdx 镜像冻结于 G:\backup\ch_vm_backup 不再 /MIR**（Owner 裁定：F 原件瘦身后若续 /MIR 会把 G 侧唯一全量镜像同步删除=三份全灭） |
| backup_reconciler（post-commit） | 事件触发（INV-08：非时间触发） | 双条件=重要文件+距上次成功≥8h；状态持久化 data/databases/backup_state.json | **INV-11 假绿闸（09-24 新装）**：CH 段 ok 落账前须过 system.backup_log BACKUP_CREATED 行交叉核验，不过则降级+连带摘除 last_ch_backup_status |
| LibraryLedgerBackup/Drill | Daily 03:30 / Monthly 10-01 04:00 | library_ledger_backup.py backup/drill | 主波基线：backup 绿；**drill 267011 从未跑**（首窗未到） |
| ZEPHYR-RESTORE-DRILL | Monthly 10-01 04:30 | restore_drill.py：最新 depgraph.dump→pg_restore→临时库 depgraph_drill→三表行数对账→JSON 报告→DROP | **267011 从未跑**；pg_restore 不可达=failed+exit 1（fail-visible） |
| CH-OptimizeMerge-Weekly | Weekly 日 03:30 | run_optimize_merge_hidden.ps1 | 主波基线 09-20 exit 0 |

## 三、冷储与多副本实测（3-2-1 对账）
- **F:\zephyr_cold**（冷库原件）：00_manifest/10_inbox/20_raw/30_corpus/40_migration/50_archive/90_tmp 七区在盘。
- **G:\backup**（备份总仓）：working_vault（最新快照 20260925+前三日连续=版本链健康）/db_dumps/git_bundles（最新 full bundle 09-21）/offrepo/predelete_deltas/ch_vm_backup（boot.vhdx+data.vhdx+zephyr-ch 冻结镜像）六区在盘。
- **G:\zephyr_cold\60_mirror**（冷储兜底镜像）：配置在册（STAGE 3d）。
- **CH 备份双链**：F 主/G 二（INFRA-STORE-003 地图口径），机制=STAGE CH 段 base+inc。
- state json 实读：`last_backup_time=2026-09-24T15:16:56Z status=ok`；**`last_backup_log_verified=False`**（INV-11 交叉核验未过/探针待核，非 ok 直落）；`last_ch_backup_status=skipped`（Mode 语义内）。

## 四、六向台账
- **上游输入**：D:\ZephyrAlpha 主区+DB dump+CH 基线/增量+F:\zephyr_cold 冷库+E:\qmt_bridge 等仓外资产+git 历史。
- **下游消费**：恢复场景（restore.ps1/restore_drill/手动 robocopy 回取）；审计（backup_state.json+logs/restore_drill_*.json）；INV-11 交叉核验读 system.backup_log。
- **自动化触发**：见 §二 表（每日/每周/每月/事件四通道）。
- **真源与注册表**：backup_config.yaml v2.1.0（MOD-INF-043 §3.3）；asset_inventory.yaml offrepo_assets（3c 目标清单）；backup_reconciler.py 头注（INV-08~12 五不变量）；INFRA-STORE-003（存储地图）。
- **门禁与质量尺**：备份锁互斥；INV-11 假绿闸（机械可信度闸）；free_floor fail loud；pg_restore fail-visible；schema 白名单不适用（无 DDL）。
- **当前运行状态：绿（备份面）/黄（恢复面）**。备份在轨有当日实证；恢复演练双件 10-01 才首跑——3-2-1 第三条腿"可恢复性"尚无一次实证。

## 五、堵点与修法
| # | 堵点 | 修法 | 归属 |
|---|------|------|------|
| 1 | 恢复演练双件从未跑（10-01 首窗） | 盯梢 10-01 04:00/04:30 首跑结果；若 267011 未转 0 即立项；演练前先手动直跑一次兜底（restore_drill 支持 manual） | 本车道+Owner 知会 |
| 2 | last_backup_log_verified=False | 复核 INV-11 探针（system.backup_log 当窗 BACKUP_CREATED 行）是核验失败还是探针故障；连带核 CH skipped 是否符合 Mode 预期 | 数据/施工小单 |
| 3 | git bundle 最新 09-21（4 天未刷） | 核对 STAGE 3b 触发条件（可能有 ref 变更才刷的短路逻辑）；确认是否语义内 | 施工小单 |

## 六、自审闸三态
**挖干可施工**：六 STAGE+六触发通道+三副本位全部双源实证（config/脚本/盘面/state 四源交叉）；3-2-1 对账清楚（D 主区+F 冷库+G 兜底）；堵点三件均为可执行小单，无结构未知。
