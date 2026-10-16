---
ttl: task_bound
---
# SDSC-11 灾备双链备份（CH 增量 + 版本化代码快照 + VM，F→G 镜像）

> 挖矿工程：全链路图12 数据供给链 S4 冷备段 3/4｜真源=config/data_supply_chain_map.yaml#DSC-11｜挖矿时点=2026-10-15（含当日只读复核）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：灾备双链备份（CH 增量+版本化代码快照+VM，F→G 镜像），node_type=stage，build_status=built，verified_scope=production（行级 ✅）。
- 职责一句话：OS 计划任务日备（daily 6AM）+post-commit reconciler（8h 撞闸写 skipped 案卷）；CH 真值口径唯一=system.backup_log（不是 backups 目录、不是 state 文件）；代码快照为 09-14 /MIR 事故后的版本化+硬链接去重形态。存储分工一盘一责：冷库=F:/zephyr_cold（唯一冷储）、备份总仓=G:/backup（INFRA-STORE-003）。
- 决策问句（图原文）：今天真的备份成功了吗？下一次备份会不会把最后一份副本删掉？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-HB→DSC-11（增量备份链）；被保对象=CH 库+代码仓+VM 镜像（D 项目+F 冷库夜镜像+CH 单链+VM 镜像=备份总仓四件） | config/data_supply_chain_map.yaml edges DSC-HB→11；AGENTS.md §7 存储分工行（2026-09-28 Owner 终裁定/INFRA-STORE-003） |
| 输出面 | logs/backup_report_*.json+data/databases/backup_state.json+system.backup_log（服务端真值）；G:/backup/working_vault/<yyyymmdd> 版本化快照（14 天滚动）；本批复核：今日 4 份报告（06:00/14:44/16:19/17:36/19:33 transcript）、working_vault 20261013/14/15 连日、schtasks DailyBackup LastRun=10-15 06:00 Result=0 | logs/backup_report_20261015_*.json；G:/backup/working_vault（本批 ls）；Get-ScheduledTaskInfo ZephyrAlpha-DailyBackup（本批实跑） |
| SSOT 真源 | 备份配置真源=scripts/backup/backup_config.yaml（g_mirror.targets 等）；CH 真值唯一口径=system.backup_log（WB12-29 钦定）；语义层=图12 DSC-11 | scripts/backup/backup_config.yaml；config/data_supply_chain_map.yaml#DSC-11 store_refs |
| 代码模块 | module_id=MOD-INF-043，module_ref=scripts/backup/backup_reconciler.py；执行体 backup.ps1/backup_reconciler.py/backup_config.yaml 全实存 | scripts/backup/backup.ps1；scripts/backup/backup_reconciler.py；scripts/backup/backup_config.yaml（本批 ls） |
| 门禁约束 | skip_not_fail 语义显式化（skip 不算失败）；/MIR 镜像删除退出码 2/3 仍落 status=ok=删除无 fail-loud（residual 在册）；g_mirror ch_vm_backup 目标防护已落地 HEAD（原 P0 治本顺清 2026-10-10，commit 44e4fc50/48bcbd2f/a96c303c 批）；F 侧摘除残留=裁定#445 排窗备案待 Owner 点名 | config/data_supply_chain_map.yaml#DSC-11 fallback+DSC-GAP-MIRROR 节点+edges 注记；scripts/backup/backup.ps1 g_mirror 段 L1057-1164 |
| 自动化触发 | wired_os_task（slot_source=schtasks：ZephyrAlpha-DailyBackup）+post-commit reconciler 8h 闸；本批复核双触发面均在动（06:00 日发+今日 3 份 commit 后报告） | config/data_supply_chain_map.yaml#DSC-11 slot_refs/trigger_facts（alive）；logs/backup_report_20261015_{144433,161927,173601}.json（本批 ls） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 被保对象三件（CH/代码/VM）来源面在册；冷库 F 侧与 G 仓分工合规 |
| 输出面 | pass | 四源互证今日全绿：backup_log 日发+报告 4 份+working_vault 连日+schtasks Result=0；代码快照腿 09-25 一次性失败事件已闭合（10-04 起 ok，10-07 上午 9 连败同日自愈，GAP-CODEBACKUP 留档防再发） |
| SSOT 真源 | pass | backup_config 真源+system.backup_log 唯一口径纪律在册 |
| 代码模块 | pass | 三执行体实存 |
| 门禁约束 | warn | /MIR 删除退出码 2/3 落 ok 分支的 fail-loud 缺陷未修（唯一残留防护缺口面）；F 侧摘除窗（裁定#445）待 Owner 点名——防护面已落地但"删除不报红"的报警盲区仍在 |
| 自动化触发 | pass | 双触发面（schtasks 日发+事件 reconciler）实测今日多次在动 |

## 4. 缺口与建议

1. 【warn 残留】robocopy 删除类退出码（2/3）落 status=ok：建议 g_mirror 段对含删除语义的退出码单列 status=deleted_rows 并告警——"删除无 fail-loud"是仅存的报警盲区（防护闸已落地，此为报警面收尾）。
2. 【warn 在案】F 侧 ch_vm_backup 原件摘除窗：裁定#445 排窗备案待 Owner 点名执行——Owner 门位事项，本图不代答，仅留观察位。
3. 【正向证据】GAP-CODEBACKUP 闭合链完整（09-25 事件→10-04 自愈→10-07 瞬时窗同日自愈→留档防再发），backup_report JSON 族作为事件账本在正常滚动（今日 4 份）。
