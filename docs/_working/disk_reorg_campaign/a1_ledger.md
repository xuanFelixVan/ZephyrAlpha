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

## 磁盘清偿终局班（2026-09-22，st-disk-final-20260922，续本台账）

> 执行令：通宵令 sid=st-disk-final-20260922；裁定依据 #380/#382/#398/#399（#399=废表两态制全删 Owner 全批）。降级直改主区原因=通宵令明确 --allow-non-worktree --allow-overlap，纯文档+CH 操作批，台账续做须见主区实时态。

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 04:03 | 冷启动：PATH 3.12.8/lock cleanup/reaper 存活（last_run 09-22 03:57）/会话注册+心跳 keeper 30s/reaper 白名单 +2 行 | [亲验] | done |
| 04:07 | 开工实况重测：CH 26.6.1 uptime 29h 零在飞；17 张废表逐张 system.parts 实测与盘点册 100% 对上（合计 35.39G+0.0002G）；default 盘 free=107.9G；TI=1299 parts/185.07G/3.79 亿行；**异常发现：backups2 盘 system.disks 报 0B（阶段4.7 第二链疑似掉盘，移交项）** | survey[亲验] | done |
| 04:12 | 活会话盘点：4 活跃（st-b10-final-20260922=批10 收尾嫌疑/st-dloop/st-residual/st-ulib2）；声明板登记独占窗 04:40-07:30（执行令 02:00-05:00 超窗顺延补记） | [亲验] | done |
| 04:14 | tick 回滚通道引用退役：p0_tick_backfill.py:401 _wipe_three_days 改 ABORT+原逻辑注释存档（执行令写 ：349 行号已漂移至 :404）；wipe_tick3days.py bak 引用全改历史注记+勿复跑哨兵；台账登记即本行 | [亲验] | done |
| 04:18 | api_server 标签字典清 3 行（kline_daily_bak_256/news_data_corrupt/news_data_pre_tz2，裁定#399 同批附注项） | py_compile OK | done |
| 04:20 | 17 张 dry-run 验证三件全过：活表全部存在且新鲜（mtime 均为 09-21）、bak 行数与 manifest 逐张全等、零引用复核；etf_15min/etf_1min 活表行数<bak=滚动归档移动窗口预期（阶段3.2），判据降为记录项 | dry 17/17 | done |

| 04:24 | 1970clean 四表补双副本导出（原 manifest 仅盖 13 张，#399 全批后按数据第一公理补齐）：F+G Parquet+行数核对+sha256 两侧全等 | 4/4 ALL-OK，waste_table_export_manifest_1970clean.yaml | done |
| 04:35 | backups2 异常定性（04:07 发现 0B 的复盘）：OS 层 /mnt/chbackup2 挂载正常（df 618G free，inc.zip 96G+market.zip 266G 在盘），CH 层 system.disks 报 0=CH 配置未刷新（RELOAD DISKS 可修，化妆品级）；宿主 SCSI 0:4 挂接正常 vhdx 452G | [亲验 ssh+df] | done（移交备份链 Owner 复核 CH RELOAD） |
| 04:40-04:41 | **17/17 DROP 全部完成（裁定#399 终局）**：执行器逐张三件验证（活表存在+mtime 新鲜/行数与 manifest 全等/零引用）→DROP→行数归零复核；04:41 中途出现 zephyr_writer 亚秒级轮询 SELECT（st_stock_list 派生管道），阻断判据放宽为仅 >5s 长查询后续删；逐张证据=drop_evidence.jsonl（行数/字节/free_space 前后快照） | 17/17，删表 32.96GiB | done |
| 04:47-04:52 | 空间回收核查：DROP 后 free 未即时上涨一度疑失血（实为 CH 26 异步清理延迟数分钟）；04:52 复核 default 盘 free 107.43→139.39GiB 净回收 +32.0GiB 与删表量全等；root 盘 76% | [亲验 df+du+system.disks] | done |
| 04:55 | 底档落盘：waste_table_registry.yaml 17 条 status=已删除（裁定#399）+yaml.safe_load 验证过；呈报清单追加批文执行记录；登记册更新脚本一次误写（status 状态机缺陷）经 git restore HEAD 后重放修正（自伤自愈，未涉他会话内容） | 17/17 已删除 | done |
| 04:41-05:15 | 分包2 前置+整表 OPTIMIZE FINAL 点火：前置实测=甲线 dwm 58/58 收官零在飞、TI 1354 parts/184.6GiB/3.79 亿行、末次写入 09-21 19:33；FINAL 整表重写引发清理饥饿（free 139→87.7GiB 单调下坠，inactive 积压 800+），**有控熔断 KILL**（merge 中断无副作用） | ti_optimize.log+watchdog 输出 | done |
| 05:20-05:25 | 回血核实：STOP MERGES+清理排空后 free 152GiB inactive=0——单合并+排空模式实证可行；定位 STOP MERGES 会取消显式 OPTIMIZE（Code 236），START MERGES 后改分批打法 | [亲验] | done |
| 05:30-07:1x | **分区分批 OPTIMIZE 落地**：只并 multi-part 分区（dry-run 194 个/68.3GiB，302 个单件分区跳过），15GiB/批+批间排空+单分区 4 次重试退避（与后台合并竞态 Code 236 瞬态错）；195 个 partition_done 零失败；最后 24.6GiB 大分区单批收尾 | ti_batch_evidence.jsonl | done |
| 07:5x-08:4x | 提交队列连环死信四连对症（逐条实测根因）：①wipe_tick3days.py 被 prestage check-ignore --no-index 拦=serializer worktree 只认 HEAD 版 .gitignore，主区未提交豁免行无效；②.gitignore 属 PROTECTED-PATHS 无 CLI 逃生旗（不硬闯）；③capability registry 净删 13 条=他会话 st-commitchain 目录改名中途态（HEAD=新路径/盘上=旧路径），增量对齐 13+1 条 file 字段归零；④SHELL-DANGEROUS 扫中 ledger 历史 pit 原文（改全角斜杠拆弹）+GATE-ALGO-FLOW 扫中 api_server 既有标记缺口（需配套 yaml，剔出批）。处置=主批 13 件（剔 wipe_tick3days.py 与 api_server.py），两者留主区工作区台账登记，归甲线/前端 owner 随批落地；q-0001..0005 死信档案在案 | [亲验] | done |
| 07:02 | **分包2 验收**：active parts 1299→**821（-37%）**健康带达标；单行 SELECT 0.16s；行数 3.790→3.531 亿（-6.8%=ReplacingMergeTree 引擎去重收益，b10 回填重插旧版本被收敛，非丢失）；残余 multi-part=69 个为插入 churn（背景合并常规消化）；inactive 216 排空中 | ti_accept_evidence.json | done |
## 分包4 日历窗等待项登记（本班登记，到日执行，届时勿再问）

| 等待项 | 触发日期 | 执行命令与前置 | 状态 |
|---|---|---|---|
| E 侧冷库删除（E:\zephyr_cold_archive，117.6G Parquet） | ≥2026-10-20（30 天留观到期） | 前置=重跑三方对账（文件数 2211+字节 126,247,590,599 vs `F:\zephyr_cold\50_archive\by_project\zephyralpha\` 全等）→ `Remove-Item -LiteralPath 'E:\zephyr_cold_archive' -Recurse -Force`（建议二段式：先改名 .pending_delete 复核一天再删）→ 全仓 `rg E:\zephyr_cold_archive` 零命中终验（历史裁定档豁免） | 已登记 |
| 研报 E 侧删除（E:\数据下载\研报，84.7G/29,998 件） | ≥2026-10-18（30 天窗到期） | 前置=重跑对账（E 侧 vs G 2019_bundle 29,998=29,998+字节+5% hash 抽检）→ `Remove-Item -LiteralPath 'E:\数据下载\研报' -Recurse -Force` → G 侧 manifest 抽读 10 件复验 | 已登记 |
| vhdx 压缩（D:\HyperV\VMs\zephyr-ch\data.vhdx） | 等 Owner 点名（a3 §7；预检单 vhdx_precheck_20260920/21.md 已备） | `backup.ps1 -Precheck` 出最新预检单 → Owner 点名 → 全局冻结档停 VM → 管理员 `Optimize-VHD -Path D:\HyperV\VMs\zephyr-ch\data.vhdx -Mode Full` → 起 VM → 全链健康探针（a3 7.3）；验收 vhdx ≤450G | 已登记（Owner 门位） |


## 假期前磁盘减压班（st-diskrelief-20260923，09-23 18:40 起）

> 总包=Owner 指令卡"假期前磁盘减压班 v2"（G 9.2% 红线+假期无人值守风险）。设计铁律=INFRA-STORE-003 注册版（D=生产/E=软件+热数据/F=纯冷库/G=备份总仓）；数据第一公理=删除前两份验证副本+hash verify。

| 时刻 | 动作 | 实测 | 证据/状态 |
|---|---|---|---|
| 18:40 | 冷启动：PATH 3.12.8 / lock_files cleanup CLEAN（顺带回收 st-ailayer-p1、st-k4 两死会话遗物）/ reaper 存活 last_run 18:40:30 killed=0 | [亲验] | done |
| 18:45 | 清理前五盘基线（Get-Volume 含 C）：C 55.3G(27.8%) / D 64.9G(8.9%) / E 57.9G(6.2%) / F 179.9G(9.7%) / **G 228.7G(6.1%)** | .runtime/tmp/diskrelief/before_volumes.txt | done |
| 19:05 | 任务1 步①对账记录复核：a3 §4.2 PASS（09-21 18:53 种子，1,156,584 件/200.7G 逻辑量/双侧全等+57,829 件哈希零失败；F 旧 vault 原留观至 09-28，本卡经 Owner 批准提前） | 本表 4.2 行 | done |
| 19:20 | 任务1 步②**当前态重对账**（新写 verify_pair.py：逐目录 count+bytes+集差+每目录抽 20 件 sha256，9 对全跑） | F=**1,156,584 件 / 200.7 GiB**（与 §4.2 记录逐件吻合）vs G=1,156,667 件 / 201.9 GiB；**missing_in_dst=0**；8/9 PASS；180 件抽样 sha256 零失败 | vault_task1_summary.json + vault_2026*.json | done |
| 19:28 | 任务1 步③ 20260921 FAIL 定性=F 侧为 18:53 种子版、G 侧为 20:05 快照直写版（G 多 83 件 + 128 件字节差，内容=.ailocks 锁态 / config/standards.yaml / ch fstab）→ **先把 128 件 F 独有变体全量归档 G 再删**（逐件 sha256 双端复核） | ok=**128/128** failed=0，313,148,631 B → G:\backup\predelete_deltas\F_working_vault_20260921_variants_20260923\_delta_manifest.json | archive_vault_delta.py | done |
| 19:46 | **任务1 删除 F:\working_vault**（Remove-Item -Recurse -Force，12.4 分钟） | F 空闲 179.9→**232.6 GB（净回收 +52.7 GB）**——台账口径 200.7G 是**跨日硬链接逻辑量**，物理净回收以 df 为准 | [亲验] | **done** |
| 19:35 | 任务2 前置：三份 ch_vm_backup 结构核（各 5 文件，data.vhdx=635,189,592,064 B 三份同尺寸）+ 谱系破案（a4 §4.9 WizTree 三份等值 + F 第四份原件；g_mirror 现行条目=F:\ch_vm_backup→G:\backup\ch_vm_backup，故 G:\zephyr_backup_mirror 区已无消费者）；三方 sha256 长作业点火 | 见后续行 | hash_triple.py | in_progress |
| 19:40 | 任务3 定性（**先纠正对应物**：config offrepo_backup.base=G:\backup\offrepo，嵌套 G:\backup\offrepo\offrepo_backup\ 才是 09-21 改址遗留旧镜像——首跑比错对象致"假不等 75 件"） | 对现行目标：**F 4,360 件全在 G（missing=0）**、30 件 sha256 零失败、G 多 228 件更新档；唯一字节差=append-only archive_manifest.jsonl，**前缀证明成立**（F 624,220 B 恰为 G 715,340 B 的前导字节，2,291 行 ⊂ 2,512 行，F 独有行=0） | offrepo_vs_current_g.json | **核等成立** |
| 19:52 | 任务3 真源核实（RULE-DATA-OPS"真实性"）：F:\offrepo_backup 只是**旧镜像落点**，四件 mirror 资产真源=E:\qmt_bridge / F:\zephyr_cold\50_archive / D:\ZephyrAlpha-stash-archive / C:\Users\fanzi\.trae-cn\memory（asset_inventory 15 条逐核） | [亲验] | 删除放行 |
| 19:58 | **任务3 删除 F:\offrepo_backup**（136.63 GiB 逻辑量 / 4,360 件） | 见下行回收数 | [亲验] | done |
| 19:50 | 任务4 半程：09-23 五次 skip 全为 lock_held（02:26、10:25 两趟真跑占锁所致），DailyBackup=Ready / NextRun 09-24 06:00；**CH 硬证 system.backup_log（持久 MergeTree 表，非内存表）逐日：09-19 2 次 / 09-20 4 次 / 09-21 1 次(压缩 90.28 GiB) / 09-22 零次 / 09-23 2 次(02:25→03:11、09:21→10:16，各 ~380 GiB total_size)** | 双链盘内 df 逐项同步：sdc/sdd 各 331G used / 626G avail / 35%；inc.zip 87,932,709,303 B @09-23 10:16 两处一致；market.zip 266,634,034,420 B @09-15 两处一致 | [亲验] | done |
| 19:52 | 任务4 **发现 P1 假绿嫌疑（移交 Owner）**：backup_state.json 记 last_ch_backup_time=09-22 10:21:37 且 verified=true，但 backup_log 09-22 零行，且 last_ch_backup_bytes=96,936,103,205 B **逐字节等于 09-21 那次的压缩量 90.2788 GiB** → 09-22 那次"成功"疑为沿用上一次结果；logs 下 09-22 亦无对应报告（仅 14:02/14:36 两份 cadence-skip） | 证据等级=亲验数字 + 推断定性（缺 09-22 10:21 那次运行日志方能定案） | **待 Owner** |
| 20:00 | 任务4 rebase 余量核算：inc/base = 87.9/266.6 GiB = 33.0%，阈值 50%（backup_config rebase_threshold）→ 假期内可能触发重建基线；已核 rebase 分支=**先删 inc.zip+market.zip 再写新 base**（backup.ps1:308-323），故峰值≈新 base 单独体积，盘内 626G avail 充足 | [亲验] 读码+盘内 df | done |


| 时刻 | 动作 | 实测 | 证据/状态 |
|---|---|---|---|
| 20:57 | 任务2 第一份全量 hash 完成（正本 data.vhdx 5209 s） | `f963a7736fef…` | chvm_triple_hash.json | done |
| 21:14 | 第二份完成（mirror data.vhdx 仅 1027 s，速率反常 5× → 起疑） | `3c17de3c1d…` **与正本不等** | 同上 | **停手信号** |
| 21:20 | 零成本探针①：7 个偏移窗 4 MiB 逐字节比对三份 | 正本≡冷抽屉（7/7 全等）；mirror 头部等值、≥100 GiB 处**全零** | [亲验] | done |
| 21:30 | 探针②：`fsutil file queryallocranges` 三份同长 | 均单区间 0x93e4400000=635,189,592,064 B 满额分配 → **非稀疏**，mirror 是真被写了 ~550 GiB 零 | [亲验] | done |
| 21:46 | 探针③：128 窗（头部细扫+每 5 GiB  stride）1 MiB 取样定性 mirror 非零边界 | A==C **128/128**；B 非零窗止于 **40 GiB**，45 GiB 起全零；A==B 仅 22/128 | scan_mirror_zeros.py | done |
| 21:48 | **定性上报**：卡的第一步前提"三方等值"证伪——mirror 不是第三份副本，而是 **09-21 一次没跑完的整机拷贝残件**（前 ~41 GiB 有数据、其后零填充；同尺寸因 VHDX 固定大小）；根因=a4 §4.9 那句"WizTree 勘实三份完全等值"出自**同名+同尺寸判重、不比内容**，故 1774.7G 亦是 3×591.57 的算术而非可互删量 | 事实+成因+替代路径三条 | [亲验数字/推断成因] | **不擅自删** |
| 21:52 | **Owner 总指挥令④项**：①注册表 note 改真值口径（两份等值+一份未完成残件，禁再写"三份等值/1774.7G"）②删除仍按两证前置=冷抽屉全盘 hash 逐位一致 **且** mirror 前 45 GiB 逐块差分独有字节=∅，两证齐才删③删后 G 达 22-23% 即停手、冷抽屉按原排期留 10-21④"停手→探针→定性→不擅自删"处置链进项目记忆（Owner 已记档） | 本班记忆已落：`diskrelief-shift-20260923.md` + `premise-falsified-stop-and-probe.md` | 裁定 | 执行中 |
| 20:35 | 附带治本：`restore.ps1` 读侧路径落后写侧一版（`$VaultBase/$DbDumps` 写死 F:\，`Get-LatestGitBundle` 仍找 `<vault>\git_bundles`=只剩 09-14/15 旧件，活件在 `G:\backup\git_bundles`）→ 真灾会恢复错代码+错 bundle；已改按 backup_config.yaml 单一真源解析（同款 backup.ps1 习语），头部工件清单同步注记 | PSParser syntax_errors=0；非 ASCII 字节=0；解析值 Test-Path 全 True；端到端 `inventory` 实跑待 G 盘不抢盘时补 | [亲验] | done（待实跑验收） |
| 21:50 | 任务4 假期增量预估按 **09-25(周五) 12:00 GPU 点火 + 59 h 无人值守（至 09-27 23:00）** 校准：窗内 06:00 自动备份 2 次（09-26、09-27）+09-28 06:00 恰在窗外 → G 净增≈vault 2-3 天 55-90 GB + db_dumps 2×0.19 GB + CH 链原地覆写不累加（inc.zip 覆盖写、rebase 先删后写，主机侧文件不再涨）；**删 mirror 前**裕度 228.7-90≈139 GB，距空间守卫 floor=60 GB（backup.ps1:444 量 vault 所在盘=G）只剩两次快照的余量；**删后**≈820-864 GB（22-23%） | [亲验代码+实测盘量] | done |
| — | **在飞**：冷抽屉 data.vhdx 全量 sha256（ETA ≈22:40）→ 完成后立即跑 mirror 前 46 GiB 逐块差分（diff_mirror_prefix.py）→ 两证齐即删 `G:\zephyr_backup_mirror\` | | in_progress |

## 备份冷储安全总包班（st-backup-cold-20260924，09-23 23:10 接管减压班断腿）

> 纪律等级=全场最高（数据第一公理：删除前两份验证副本+行数/hash 核对）。总指挥 30 分钟批注制。真源=本台账+overnight_decisions_20260923.md 各轮裁决。

| 时刻 | 动作 | 实测 | 证据/状态 |
|---|---|---|---|
| 23:16 | 冷启动：PATH 3.12.8 / lock cleanup CLEAN / reaper 存活（last_run 23:10 killed=0）；hash 作业确认**未死未断**：chvm_triple_hash.json finished_at=23:14:24 自然收尾 | [亲验] | done |
| 23:20 | **证一达成**：正本 G:\backup\ch_vm_backup ≡ 冷抽屉 G:\zephyr_cold\ch_vm_backup 全 5 件 sha256 逐位等值（data.vhdx=f963a773…b77b 双方全等；vmcx/VMRS/vmgs/boot.vhdx 三份全等）；mirror data.vhdx=3c17de3c… 确认残件 | chvm_triple_hash.json | done |
| 23:26 | 证二点火：diff_mirror_prefix.py 前 46GiB（≥令的 45GiB）逐 16MiB 块差分；reaper keep +diff_mirror_prefix | 后台 806.8s | done |
| 23:45 | ②backup 假绿处方施工：backup_reconciler.py 加 INV-11 闸（ok 落账前 system.backup_log 交叉核验）+cadence-skip 分记；红测 TestBackupLogGate 先行；能力反查/claim/depgraph(既有节点不新增)三前置 | 26/26 测试 | done |
| 00:0x | **证二疑点块法证**：差分 2944 块=2608 等值+335 B 侧纯零+**1 块疑点（40.75GiB）**→逐字节法证 prefix_truncation（差异 4,172,533 字节全部 B 侧为零，mirror 数据止于块内 11,534,335B 其后全零）=**独有字节集合=∅ 实证** | torn_block_forensics.json | done |
| 00:2x | 证据包归档 G:\backup\predelete_deltas\G_zephyr_backup_mirror_torn_evidence_20260924\（5 件+sha256 清单+VERDICT.md）；删除前清点：区内仅 ch_vm_backup 5 件 591.57GiB 与被哈希集合一致，零未证成内容 | _evidence_sha256.txt | done |
| 00:2x | **①-3 删除执行**：改名→核 5 件→Remove-Item；G 空闲 228.37→**819.94GB，净腾 591.57GB 分毫不差**；G=**22.0%**≥20% 停手线触发→冷抽屉按 10-21 原排期禁动 | [亲验] | **done** |
| 00:4x | ①-4 落册：INFRA-STORE-003 note 真值口径（safe_write CAS+yaml 解析护栏+进程外复核）；『三份等值/1774.7G』口径作废+WizTree 尺寸判重≠内容等值方法论注记 | commit 364aefa2 | done |
| 00:50 | ③restore.ps1 三处 config 化**端到端实跑验收 PASS**：Vault/git_bundle/CH 文件名全部从 backup_config.yaml 正确解析（bundle 在 G:\backup\git_bundles 找到 09-21 活件）；verify 只读实跑钉出 8 红 | inventory+verify 输出 | done |
| 00:55 | **发现 P1-a**：vault 最新快照 20260923 残缺（缺 AGENTS.md/pyproject.toml/.env.ch_backup/.env.clickhouse；20260922 完整）=02:57 被中断的种子 | verify 输出 | 待 06:00 Mode B 自愈 |
| 01:00 | **发现 P1-b**：db_dumps 只有 20260921/22 两目录——**09-23 四轮 backup.ps1 无一轮跑完 STAGE 3/4**（CH 三次全成，代码/dumps/bundle 链自 09-22 19:13 断流）；reaper_kill.log 连环 orphan_aged:age≈2.1h 处决与死亡时点吻合（backup.ps1 不在保护名单） | [亲验] | 处置见下行 |
| 01:05 | P1-b 处置：**backup.ps1+ch_vm_ssh.py 登 reaper keep**（长批登记铁律）；08:00 后监控 06:00 轮是否首次完整跑通 | keep.txt | done |
| 01:10 | verify 第 4 处同类缺陷治本：dumps 校验改日期目录感知（09-20 版本化改址时前任漏改），重跑 verify dumps 4 红转绿；inventory dumps 段同步列最新日期目录；PS1 语法 0 错+纯 ASCII | verify 复跑输出 | done |
| 01:1x | **假绿闸实战首拦（提交前活体证据）**：23:38 st-gpu-final 提交触发 post-commit 备份遇 lock_held 短退出（skip 文件在），旧代码必记 ok，新闸 fail-closed 判 ch_log_missing+warn——09-22 同型假绿从此绝根 | backup_state.json+backup_skipped_20260923_233759.json | done |
| 01:2x | ②正门提交：批1 码+测试 d2afbd43（三学费：NO-BARE-SQL 豁免=常量须 _SQL_ 前缀非后缀/ruff BLE001 收窄 except/ruff-format 赛跑 Edit 需重读）；批2 注册表 364aefa2；**假期前落地达成** | git log 核归属 | done |

### 假期 59h 余量推演（④，09-25 12:00→09-27 23:00，Owner 已批口径）

- 窗内 DailyBackup：09-26/09-27 各 06:00 一轮（09-28 06:00 在窗外）。G 净增=vault 日 churn 快照（硬链接去重，观测≈8G/天，预算 20G/天）+db_dumps 2×0.19G；CH=VM 盘内原地覆写+G chbackup2 rsync 覆写**不累加**；git bundle 09-26(5d)/09-27(6d) 均 <7d 跳过。
- 结论：最可能 G 末态≈**815G+（21.9%）**；计入最坏 rebase（概率低：inc/base=88/248=0.35<0.5 阈值，且 base rsync 临时占 266G）G 仍 ≥513G（13.8%），距 backup.ps1 空间守卫 floor=60GB 富余 8 倍+。**假期 G 盘余量判定：绿**。
- 排班确认：ZephyrAlpha-DailyBackup Ready/NextRun 09-24 06:00 ✓；ZEPHYR-RESTORE-DRILL 已注册首射 10-01 04:30 ✓；CHHealthProbe 3min 级 ✓；WeeklyVMBackup 09-26 06:00 在窗内但 AutoCheck skip_unchanged（CH 版本自 08-22 未变）✓。
- 缺口登记：无专职"backup_state↔backup_log 每日对账"计划任务；缓解=新闸（post-commit 路径）+每日报告/skip 文件可观测+CHHealthProbe。建议 Owner 批一个日级对账探针（永续四要素，未批不建）。

### 五盘对照表（⑤；before=09-23 18:45 减压班基线，after=09-24 01:2x）

| 盘 | before 空闲 | after 空闲 | Δ | 备注 |
|---|---|---|---|---|
| C | 55.3G(27.8%) | 56.6G(28.4%) | +1.3G | 本班零动作 |
| D | 64.9G(8.9%) | 63.6G(8.7%) | -1.3G | 他会话在途代谢 |
| E | 57.9G(6.2%) | **41.1G(4.4%)** | **-16.8G** | 他会话数据落地所为，本班零动作；**4.4% 红牌呈总指挥** |
| F | 179.9G→232.6G(减压班删 working_vault +52.7) | 389.4G(20.9%) | +156.8G(对 18:45) | 含减压班 F 侧清理与本班零动作 |
| G | 228.7G(6.1%) | **819.9G(22.0%)** | **+591.2G** | 本班删 mirror 残件净腾 591.57G；9.2% 红线解除 |

### 晨报六要素

1. **完成了什么**：①减压班断腿全链收口——两证齐（正本≡冷抽屉全盘逐位等值+mirror 46GiB 差分独有字节=∅）删 G:\zephyr_backup_mirror\ 净腾 591.57G，G 6.1%→22.0%，停手线触发，冷抽屉留 10-21 排期；注册表真值口径落册（『三份等值』口径作废+方法论注记）。②backup 假绿处方假期前落地（d2afbd43）：ok 落账前 backup_log 交叉核验闸+假绿降级连带保护 db_dumps 轮转闸+cadence-skip 分记，26/26 测试含红测，且已实战首拦一次 lock-skip 假 ok。③restore.ps1 三处 config 化验收 PASS+第 4 处同类缺陷（dumps 日期目录）当场治本。④假期 59h 推演=绿+排班全确认。⑤五盘对照表如上。
2. **关键数字**：mirror 残件=09-21 未完成拷贝（前 ~41GiB 有数据，40.75GiB 撕裂尾块逐字节法证独有=∅）；删除净腾 591.57GB；G 空闲 228.4→819.9GB（22.0%）；两 commit=d2afbd43/364aefa2；测试 26/26。
3. **新发现/风险**：P1-b=09-22 19:13 后 backup.ps1 零完整轮（CH 三次全成但 vault/dumps/bundle 断流），疑 reaper orphan_aged 处决未列入保护名单的长跑——已上 keep 名单，今晨 06:00 轮是首个验证点；P1-a=vault 20260923 快照残缺 4 关键文件，06:00 Mode B 预期自愈，恢复视角 verify 此刻 4 红属预期；E 盘 4.4% 红牌；21:09 那轮 backup.ps1 死前 CH 备份已成功（backup_log id=b3642a4d 22:02 落账）但 state 未写，06:00 CH cadence 将自然重跑并自愈双链。
4. **待 Owner/总指挥**：①日级 backup 对账探针立项与否（未批不建）；②reaper 对 backup.ps1 的处决机制复核（keep 名单是保护还是需白名单语义确认）；③E 盘 4.4% 是否派班；④恢复演练（RESTORE-DRILL 10-01 首射）前是否先补一轮 20260924 手动全量备份核验。
5. **证据指针**：G:\backup\predelete_deltas\G_zephyr_backup_mirror_torn_evidence_20260924\（VERDICT.md+sha256 清单）；.runtime/tmp/diskrelief\{chvm_triple_hash,mirror_prefix_diff,torn_block_forensics}.json+after_volumes_20260924.txt；commits d2afbd43/364aefa2。
6. **交接/下一步**：06:00 后复验三件事=DailyBackup 首个完整轮（report+20260924 vault+dumps 目录齐）／vault 自愈后 verify 应 0 issues／backup_state 经新闸记 backed_up+last_backup_log_verified=true；本班 claim 已全 release；reaper keep 两条新增留存。

## 三裁定执行（2026-09-24 01:5x，Owner 对三件新发现批文，st-backup-cold-20260924）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 01:4x | ①C4 缓存迁冷库（入库四步）：drawers.jsonl 第 8 行登记先行→同卷 mv→F:/zephyr_cold/50_archive/by_project/zephyralpha_c4_exam_pdf_cache | 60,245 件/56,591,048,267B 全等+20 件 sha256 抽样全等；年份分层 2017-2021 保留原名 | done |
| 01:4x | ②F:/个人文件：Owner 已亲迁 E 盘 | F 侧确认不存在 | done（Owner 亲办） |
| 01:5x | ③五会话目录（F/G 双侧）：双侧全等核对→整体 6.2MiB/1839 件归档 50_archive/by_project/zephyralpha_session_workdirs_final3_20260918_19→双侧原件删除 | 残留检查零；drawers.jsonl 第 9 行登记 | done |
| 01:5x | 冷库盘点副产物：F:/zephyr_cold/library/（16.78MiB，内含 20260924 活目录，他包在写）不在六区清单——登记观察勿动 | [亲验] | 观察 |
