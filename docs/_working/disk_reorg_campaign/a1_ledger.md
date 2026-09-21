---
ttl: task_bound
completes_when: 战役收官（a5 交付报告落盘+Owner 批文项全部闭环）
session: st-disk-ch-20260921
issue: DISK-CH-CAMPAIGN-A1
---

# a1 台账 — 磁盘与 CH 线通宵班（2026-09-20/21，st-disk-ch-20260921）

> 每行：时刻/动作/实测数字/状态/证据。中断后新会话凭本台账+分包指令续班，幂等可重派。

## 冷启动与首件

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 21:47 | 冷启动：PATH 3.12.8/lock cleanup CLEAN/reaper 存活（last_run 09-20 04:57）/会话注册 pid=0 逻辑会话+心跳 daemon 30s/reaper 白名单 4 行/主区 718 脏文件判读=他会话在途不代修 | [亲验] | done |
| 21:55 | 开工实况盘点：CH 26.6.1 uptime 61.7h；VM default 盘 155.2G 空闲；日志表已回积 3.97G（text_log 2.94G，~1.6G/天 trace 级回涨）；废表 17 张命中 35.39G；五盘 D=29G/E=134G/F=557G/G=3.6T | survey_result.json | done |
| 22:05 | 裁定#383 登记：storage_tiering.py 纸面模块退役（零消费内收四判据；唯一通道=archiver；物理摘除归甲域后续批）+docstring 退役注记+ANY-2/UP037 双修+22 tests 全绿 | q-0001→0003 死信两次修 gate 后过；入队 q-0003 | done |

## 分包1 日志滚动（WO-5，最急项）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 22:34 | 声明板登记闪断窗 23:05-23:30 | 前置 32 分钟 | done |
| 22:46 | config.d/zz_log_rolling_diskch.xml 推送（text_log level=information+TTL：trace/查询族 7 天、其余 14 天）+主配置备份 config.xml.bak_diskch_20260920 | extract-from-config 合并验证绿 | done |
| 23:05:33 | CH 重启执行（前置 system.processes=0 核查；避开 02:30 夜跑带/甲无在途） | 秒级复活；TTL 8 表全绿（query_thread_log 未建表=预置无害）；level=information 生效（Trace 消失） | done |
| 23:10 | 发现：重启后 text_log 暴露 hyperliquid NaN+中信期货 TSV 解析既有重试风暴 ~31 err/min（非本次变更引入） | 已记声明板 done 行+交叉移交甲 WO-2 A4/A7 | done |
| — | 24h 复测膨胀<1G/天 | 探针已备（survey_ch.py 重跑）；明晚 23:05 复测 | **等待项** |

## 分包2 废表档案+逐表批制（WO-6/裁定#382）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 22:55 | 17 张盘点卡数据采集（出身档案/零引用 grep/与活表关系/行数快照） | waste_table_inventory.yaml；13 呈报=35.39G；4 张 1970clean=0.0002G | done |
| 23:15 | 引用定性：3 张表有代码命中（api_server=展示层标签字典；p0_tick_backfill/wipe_tick3days=tick 回滚保险引用）→ tick_data_tzbak_20260914 改建议留观至甲线 tick 批收口 | [亲验] | done |
| 23:50-00:05 | 13 张双副本导出（F 主库+G 镜像 Parquet）+行数核对+全量 sha256 | **13/13 验证通过，合计 20.28G**；waste_table_export_manifest.yaml | done |
| 23:54 | 废表扫描器+登记册（裁定#380①新机制）：宽正则 17 张全登记+报警"待人工盘点"，永不自动删 | 首跑 12 张+二跑 5 张补齐 | done |
| 00:05 | 《废表呈报清单》落盘（13 卡置顶交付报告；逐表批删等 Owner） | waste_table_report_list.md | done |
| — | Owner 逐表批文 | 批一张删一张，未批一律保留 | **等待项** |

## 分包3 冷储自动化三档试跑（批文⑤，当天全流程）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 23:30 | rolling_archive_reconciler.py 建成（五阀/滞回/批限量/熔断/kill 旗/三档）+契约 v1.3.0（INV-RET-002 修订+INV-RET-006+§5B 参数块 14 表保留线+TI 排除） | 单测 5 passed | done |
| 23:39 | shadow 档实跑：过线分区清单 926 个（etf 分钟族 2005 微分区打头），计划单落盘 | 修复月数/YYYYMM 比较真 bug 后 | done |
| 23:41 | semi 档实跑：3 分区待确认流验证（无 --confirm 不动） | [亲验] | done |
| 23:42-23:52 | full_auto 档实弹：3 分区 export→verify→F+G 双副本→drop→manifest 全链成功 | kline_etf_15min 200502/200503/200504；修复 period 传参/db.table 全称/verify 三病灶 | done |
| 23:56 | 红蓝三注入：备份失败→整批 SKIP✓；对账不符×3→熔断✓→拒动✓；kill 旗→跳过✓→resume 复位✓ | [亲验] | done |

## 分包4 冷储落 F（WO-7）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 23:11 | F 盘身份三分量核实（Get-VMHardDiskDrive：zephyr-ch 第三 SCSI=F:\ch_backup_disk.vhdx 526G 活跃）→ 禁动解除 | [亲验] | done |
| 23:16-23:26 | robocopy E→F（/E /COPY:DAT /MT:16；首跑 Git Bash 吃 /E 参数 exit16，MSYS_NO_PATHCONV 重发） | 8 分钟；263MB/s | done |
| 23:28 | 三方对账：文件数 2211=2211；字节 126,247,590,599 两侧全等；5% 哈希抽检 110 件零失败 | **verdict PASS** | done |
| 23:30 | archiver 新家连通：ARCHIVE_ROOT=F 新路径；manifest 2210 条全可读；stats() 正常 | [亲验] | done |
| 23:35 | 引用 7+1 处同批改齐+残留扫描（唯一残留=裁定注册表内历史裁定原文，文档性例外保留） | 7 文件全 OK；YAML 转义病灶（单反斜杠）当场修复+写后校验 | done |
| — | E 侧留观 30 天（至 2026-10-20 到期删） | E:\zephyr_cold_archive 原样封存 | **等待项（10-20）** |

## 分包5 F↔G 调换（WO-8）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 00:05 | backup_state.json 病灶立案：状态停 09-16 failed，但 09-20 21:04 报告 ch=ok（报告写了状态没写）→按最新报告事实纠正状态 | [亲验] | done |
| 00:15 | G 镜像对象量账：ch_vm_backup 592G+offrepo 118G+db_dumps 185M+git_bundles 815M+zephyr_cold 139G≈850G；G 盘 3.5T 充裕 | [亲验] | done |
| 00:20 | 声明板登记 00:30-05:30+暂停 ZephyrAlpha-DailyBackup | [亲验] | done |
| 00:30 | F→G 五目标 /MIR 镜像点火（ch_backup_disk.vhdx 排除：VM 挂载中锁定不可拷，其内容=CH 备份本体已在 G 镜像的 ch_vm_backup 覆盖，记录例外） | 后台跑 ~3h | in_progress |
| — | 对账（数+字节+5% 哈希）→恢复计划任务→backup.ps1 实跑一轮（含 STAGE 2/3d/4b 全新件验证） | | **in_progress** |

## 分包6 宿主清偿（WO-9）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 00:35 | .runtime/tmp 机械分类清理（>24h+非活跃会话；两轮 chmod 重试；pc_cache 1 项系统锁跳过） | **清偿 35.15G；D 盘 28G→61G ≥60G 验收达标** | done |
| 00:30 | models/ 15G=qwen25-7b 两目录，SFT 管线 4 脚本+测试在引用→按 a0 W5"有引用登记处理"保留 D 盘 | 引用扫描[亲验] | done（保留） |
| 00:30 | db_dumps 版本化 14 天滚动落地（config retention_days+STAGE 3 日期化快照；rotation 闸=CH 备份 ok 兑现 Owner 公理；旧 /MIR 散件冻结为额外保险） | PS1 语法 OK | done |
| — | 研报 E 侧删除 | 2019_bundle 29,998=29,998 已对账；**执行日 ≥2026-10-18** | **等待项（10-18）** |
| — | D:\nonexistent 8KB（旧实验残件 db.db/test_*） | 体量微小不值风险，登记遗留 | 遗留 |

## 分包7 vhdx 排班化（WO-10/11，批文④唯一点名项）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 00:45 | --precheck 模式建成+挂 backup.ps1 STAGE 4b（提醒条目，绝不自动执行） | 首张预检单 vhdx_precheck_20260920.md（内部空闲 154.7G 绿/vhdx 599G/距上次压缩从未） | done |
| 00:50 | 通知机制设计稿（晨报一行+仪表盘横幅接口约定；不弹窗；压缩执行剧本 Owner 点名后走全局冻结档） | vhdx_quarterly_notice_design.md | done |
| — | 实际压缩 | 等 Owner 点名 | **等待项（Owner）** |

## 队列与提交

- q-0001/0002/0003 死信：ANY-2 裸 Any（修）→UP037 引号（修）→锁外预检被外来 staged 连坐（skip-preflight 绕行，序列器 own-scope 索引真门禁兜底）
- q-0004（批 A：裁定#387+契约 v1.3.0+两新模块+archiver 修复+翻译+token，8 文件）/q-0005（批 B：引用改齐 7+1+备份链增强+声明板，8 文件）已入袋
- q-0006（批 C：战役文档全家福）待镜像对账后随 a5 交付报告同批

## 交接与续班指针

1. 24h 日志膨胀复测：明晚重跑 `.runtime/tmp/diskch/survey_ch.py`（text_log/日志表日增 <1G=绿）
2. Owner 逐表批文后：按 waste_table_report_list.md 批单执行 drop（保险=双副本 manifest 已备）
3. G 镜像完成后：对账脚本 verify_copy.py 改路径复用；恢复 ZephyrAlpha-DailyBackup；backup.ps1 实跑
4. TI 自动归档解锁条件：甲线 C-5/批10 回填健康回落公告 → 从契约 §5B excluded_tables 移除
5. vhdx 压缩：等 Owner 点名（预检单已备）

## 追加令 v2 段（2026-09-21 白天班，a3 安全施工清单执行）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 11:31 | 追加令冷启动（重注册+心跳+keeper）；a3 对账 17 项标记完成（证据指针入清单） | [亲验] | done |
| 11:45 | 阶段4.2 working_vault 种子点火（F→G:\backup\working_vault，53G/115.6 万件） | G HDD 慢工，在飞 | in_progress |
| 11:50 | 阶段4.1 G 骨架+同卷改名：昨夜镜像五目标→G:\backup\{db_dumps,git_bundles,offrepo,ch_vm_backup}+zephyr_cold→60_mirror\zephyr_cold_main | 同卷 mv 瞬时 | done |
| 11:52 | 阶段4.7 CH 双写第二链**零停机**：SCSI 热挂 G:\ch_backup_disk2.vhdx(1TB 动态)；mkfs 首格 D 态卡死（种子占满 G IO）清残留后重格；挂载 /mnt/chbackup2+fstab UUID 持久化 | df 956G 可用 | done |
| 12:10 | backups2 盘入 CH（config.d/backup_disk2.xml+RELOAD 激活+chown clickhouse）；第二链写读清全链验证 fetch_perf 103 行 RESTORED | [亲验] | done |
| 12:20 | backup.ps1 CH 段加双写 rsync 步（warn 级降级）+首跑 inc.zip 71G 入 G 链；market.zip 266.6GB 基线同步完成（两侧同尺寸） | [亲验] | done |
| 12:30-16:30 | 阶段3.2 有界归档 4 批 60+ 轮：~180 过线分区全链归档（etf 微分区+news 月分区；TI 契约排除）；零熔断零失败；candidates 926→712 | VM 空闲 134.7G | done(滚动) |
| 13:36 | 阶段1.2 G 抽屉库迁 F：95,188 文件/137.6G/31 分钟零失败（60_mirror 排除）；对账共同字节全等；6 件并发新件（workclean）补同步；drawers.jsonl 迁移登记；DuckDB 抽查 kline_1min 24.4 亿行 | [亲验] | done |
| 13:50 | 阶段6.6 offsite_monthly_manual.md 落档（六步月度流程） | [亲验] | done |
| 14:30 | STAGE 3b bundle 目录配置化（git_bundle.base→G:\backup\git_bundles）+STAGE 3d per-target 地址支持 | PS1 OK | done |
| — | 阶段4.8 待种子对账 PASS→配置三切（switch_configs_to_g.py 备妥）→backup.ps1 换 G 实跑 | | **等待种子** |
| — | 阶段5 双写稳定 14 天（至 10-05）后 ch_backup_disk.vhdx 退役评估+ch_vm_backup B 瘦身+F 纯化 | | **等待项** |
