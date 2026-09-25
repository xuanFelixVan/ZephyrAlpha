# G/F 盘 备份+冷库 全景审计 SOP（v1.0，2026-09-24 立法，源自 st-backup-cold-20260924 全夜实战）

> 执行者：任意 AI 会话（按本 SOP 机械执行，无需上下文）。频率：日检 5 分钟/周检 30 分钟/月检 2 小时/季检半天。
> 真源指针：保留契约=docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml；四盘地图=INFRA-STORE-003；备份消费真源=scripts/backup/backup_config.yaml；冷库台账=F:\zephyr_cold\00_manifest\drawers.jsonl。
> 硬红线：全程只读+台账追加；任何删除需 Owner 批文+两份验证副本；实盘四禁。

## 一、日检（每天 07:30，5 分钟）

1. 四盘容量：powershell Get-Volume C/D/E/F/G——判据：F≥700G、G≥500G、D≥50G、E≥50G free，任一破线标红。
2. 昨夜备份报告存在：ls -t logs/backup_report_日期*.json——无报告→查 backup_skipped_日期*（lock-skip=可观测跳过，健康）+reaper_kill.log 当日行（出现 backup/powershell 击杀=标红，处理：确认 data/runtime/process_reaper_keep.txt 含 backup.ps1/ch_vm_ssh.py）。
3. state 真源核验：data/databases/backup_state.json——last_backup_status=ok 且 last_ch_backup_status∈{ok,skipped}；backup_log 交叉：curl CH "SELECT count() FROM system.backup_log WHERE status='BACKUP_CREATED' AND event_time>=now()-INTERVAL 26 HOUR" 应≥1（CH today()=UTC 日切陷阱，用 26h 窗）。
4. 第二链日检：ch_vm_ssh --cmd "stat -c '%s %Y' /mnt/chbackup2/inc.zip"——字节数≥最新 backup total_size×0.15 且 mtime 距今≤26h（台账【第二链日检】行）。
5. 三哨兵（防蒸发）：git show HEAD 逐查 LEDGER 0600-VERIFY-PASS、registry 口径注记、backup.ps1 B2 标记——任一消失=蒸发复发，从工作树重落并标红。

## 二、周检（每周一 09:00，30 分钟）

1. F/G 顶层对账：对照本 SOP §四期望清单逐项 du——多出的顶层条目=未登记杂物（查来源，归档或报 Owner）；缺失项=排查。
2. 60_mirror 新鲜度：G:\zephyr_cold\60_mirror\zephyr_cold_main 顶层 mtime 应≤48h（每夜 STAGE 3d 同步）。
3. offrepo 源↔镜像对照：backup_config offrepo.targets 逐条 robocopy /L 对账（G⑥ 翻倍疑点年度复核）。
4. vault 快照健康：最新日期目录含 AGENTS.md/pyproject.toml/config\.env.*——缺=自愈失败标红。
5. dumps 链：最新日期目录四件齐（depgraph.dump/pg_globals/两 SQLite）。
6. git_bundles：最新≤7 天且≥2 份。
7. 冷库 drawers.jsonl：逐行 json.loads 合法+path 在盘上存在。
8. E 盘复扫：顶层无新增数据目录（只允许软件/个人/qmt_bridge/qmt_bridge_sim/ZephyrAlpha 日志）。

## 三、月检（每月 1 日，2 小时）

1. 灾备演练四级（非破坏性）：git bundle 实 clone 到 F 临时区核 commits；SQLite 恢复+PRAGMA integrity_check；PG dump pg_restore 进临时库核 89 表+抽样行数后 DROP；CH 验证层（verified=True+backup_log 交叉）。
2. CH 全量 RESTORE 演练（破坏性，需 Owner 点名停机窗）：按 ZEPHYR-RESTORE-DRILL 任务。
3. archive_manifest.jsonl 全量核对：逐行 path 存在+bytes 相等。
4. 60_mirror 与 F:\zephyr_cold 全量 robocopy /L 对账（应零独有）。
5. predelete_deltas 证据包 sha256 清单全验。

## 四、季检（半年，半天）

- 全文件级审计（本 SOP 挖矿全集）：F/G 每顶层目录逐件清点、重复副本扫描、路径幻觉扫描（断链/死链）、冷库不可持续获取数据集复查（是否值得转 Parquet 查询层）、INFRA-STORE-003 与实盘差异修订。

## 五、已known 盲点（挖矿清单，逐届复核）

1. backup.ps1 运行 9.1h 病理（09-25 实测）——B8 拆分方案未落地前的已知慢点。
2. 周六 06:00 backup_ch_vm 与 DailyBackup 撞车（V1）。
3. reaper 对 backup.ps1 的 keep 匹配语义未与维护班确认（09-25 06:00 轮仍被杀）。
4. CH today()=UTC 日切——所有"当日"判据必须用 26h 窗或本地时区换算。
5. 60_mirror 对 C4 52.7G 的追赶（09-25 夜应完成，周检核）。
6. g_mirror 摘除 ch_vm_backup 后 backup\ch_vm_backup 冻结档无自动更新（CH 升级时手动重做）。

## 六、处置分级

绿=记录；黄=标红台账+下轮复查；红=立即取证（只读）+报 Owner；任何删除=Owner 批文+两份验证副本+台账留痕。
