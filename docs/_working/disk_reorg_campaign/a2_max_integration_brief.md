---
ttl: task_bound
---

# 【线任务包·磁盘重整+冷储备份自动化】交 Max 总梳理会话——整合入全项目统一施工方案
# 本包=磁盘线一条线的完整输入。接收方=Max 总梳理会话（统筹整合，不直接施工）。

## §0 你的任务（先读）
你是全项目施工方案总梳理会话。当前四条线：
① st-final3 十战线（收尾清零：working 任务书归档+内收+复权链，在飞）
② st-tilib-clear 分包A（指标库 34 指标"代码+测试+注册表"三件套清零，在飞）
③ st-dataqa 分包B（数据质量+测试健康双审计，纯只读四报告 R1-R4，在飞）
④ 本线=磁盘重整+冷储备份自动化（方案与总令已备好，待①②③收口后执行）
**你的产出**：《全项目统一施工方案》（落 docs/_working/unified_campaign/）——把④与①②③的交付物/遗留待办整合排序：全局波次网络（谁先谁后/可并行/必须窗口隔离）、Owner 签字汇总成一张单、每个任务带验收数字与复验命令、断点续班与回执六要素。**只产方案文档，不改代码、不动数据、不搬文件。**其他线若有各自任务包，同格式并入。

## §1 项目背景
ZephyrAlpha=Owner 个人量化交易系统，100% AI 开发，宪法 AGENTS.md 全程有效（硬规则/热文件 CAS/提交网关/禁 cron 事件触发等）。宿主 Windows+HyperV 虚拟机 zephyr-ch 跑 ClickHouse 26.6.1（行情库）。五盘：C=NVMe 系统；D=NVMe 731G（项目仓 D:\ZephyrAlpha 74.7G + CH 虚拟机磁盘 data.vhdx 599G=曾占 D 83%）；E=SATA SSD 931G（软件+热数据）；F=SanDisk 2T USB（实为 SSD，读 374/写 340 MB/s）；G=东芝 4T USB 机械（写 70 MB/s、小文件 11.5 files/s）。Owner 已拍板四盘分工：D=项目+CH 虚拟机、E=软件+热数据、F=冷储主库+working_vault 代码版本库、G=备份兜底+冷储镜像（3-2-1）。**数据安全第一公理：任何删除前必须有两份验证过的副本；drop 前必须行数 verify。**

## §2 硬事实（2026-09-19/20 实测；执行日重跑探针刷新台账，禁凭记忆）
- CH VM 内 /var/lib/clickhouse 631.9G：曾仅剩 6.6G→2026-09-19 晚已 TRUNCATE 全部系统日志释放 145G（现余约 151G）。业务活跃 426.5G=合规热层 361G（tick_data 141.5G=2025-01 起 21 个月、约 6.7G/月唯一增长源；technical_indicator 窗口内 151G；分钟线约 66G；日K/基本面/事件/元数据小）+尸体表 35.4G（news_data_corrupt_20260828 13.0G、news_data_pre_tz2_20260828 12.9G、kline_etf_*_tz_bak 8.1G、kline_1min_tzbak 0.95G 等约 12 张）+契约欠账 24.9G（TI 窗口外 19.4G+冷线 5.5G）。
- 热层有界证明：tick 过 2 年线后（2027 起）热层稳态约 350-400G；150G 冗余≈22 个月纯增长缓冲（Owner 定案按 150G 留，季度压缩巡检）。
- CH 凭据与坑：唯一真源=config/.env.clickhouse；库内仅 default/zephyr_reader/zephyr_writer 三账号，zephyr_writer 无 TRUNCATE system.* 权限（RBAC 设计勿改），系统表操作用 default 超户；>50G 表 TRUNCATE 被 max_table_size_to_drop=50G 保险丝拦——同 ?session_id=xxx 两连发（SET→SELECT 验证→TRUNCATE），禁全局关保险丝；CH 26.6 无 multiquery 参数；CH TSV 分区串带 \' 转义，元组分区解析先 strip 反斜杠；text_log 级别仍是默认 trace（~50G/月回涨，151G 余量约撑 2-3 个月——本线最急项）。
- 冷储现状：G:\zephyr_cold 抽屉库（00_manifest/drawers.jsonl 台账制，研报 90,243 件已入：F 盘 60,245+E 盘 29,998，零失败）；E:\zephyr_cold_archive 117.6G Parquet 冷库（c1_market 115.8+c3_fundamental 1.8）待迁 F；E:\数据下载\研报 84.7G 已复制进 G（2019_bundle 29,998=29,998 对齐），E 侧删除须等 30 天窗（2026-10-18 到期）。
- 代码引用 E:\zephyr_cold_archive 共 7+1 处须同 commit 改齐：scripts/ch/archiver.py:69,732、config/asset_inventory.yaml:139、docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml:200-203、docs/registry_of_logs.yaml:808、src/zephyr/frontend/dashboard/services_registry.py:118-120、scripts/backup/backup_config.yaml:88-89、核对 data_retention_contract.yaml。
- VM 内第二盘 /mnt/chbackup_local（1081G/余698G）物理身份未核实（疑似 F:\ch_backup 映射）——核实前禁动 F 盘任何搬运。
- 保留政策真源=data_retention_contract.yaml：Tick≥2年/分钟·资金面·衍生≥5年/新闻·日K≥10年 手动归档线；<1GiB 研究表永不归档；派生 TI 滑窗 3月/1年/3年/5年（执行极好，全库欠账仅 24.9G）；铁律 INV-RET-002"进冷层必须手动触发"与本线自动化目标冲突，修订路径已在方案 §2/§12。
- 挖矿三发现：①business_data_categories.yaml 114 品类全带 lifecycle 字段但 206 条 permanent 与契约脱节，tasks.yaml retention 字段零命中（身份证载体在、未启用）；②storage_tiering.py 纸面模块（CONSUMERS=scheduler 零引用，接线或退役待裁）；③backup_daily_trigger.ps1（06:00 兜底，post-commit 事件触发）=禁 cron 红线的合法先例，滚动归档挂备份成功事件链即合规。
- 主区状态：三队在飞收尾期，脏文件动态变化；一切提交只走 scripts/git_commit.py --enqueue --files 白名单。

## §3 本线资产与真源路径（全部已落盘+git add）
1. docs/_working/disk_reorg_plan_2026_09_19.md——勘察底数 v2（盘位/速度/库内三笔账/D/E 逐目录清单/软件不迁裁定/引用清单）
2. docs/_working/cold_backup_automation/00_master_plan.md——自动化方案 13 章（身份证机制/滚动归档 reconciler 五重安全阀/3-2-1-1-0 备份映射/vhdx 150G 专章/保留与清除总清单 17 行表/执行批 0-8/风险回滚/拍板清单）
3. docs/_working/cold_backup_automation/01_mining_findings.md——挖矿报告（9 行缺口表/数据资产清单/8 条意外发现/外部实践对照/20 条引用）
4. docs/_working/disk_reorg_campaign/a0_master_order.md——收口六波总令（三队收口后可粘贴直接执行：W1-W7 全文+验收数字+避让清单+自裁框架）
5. docs/_working/altdata_line/10_g_drive_cold_storage_sop.md——冷库 SOP（抽屉制+三红线 immutable/禁双真源/回测数据家不在冷库）
6. docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml——10 层保留契约真源
7. scripts/backup/backup_config.yaml+backup.ps1+backup_reconciler.py——备份链现状（working_vault 14 天轮转/db_dumps 覆盖式缺口/ch 增量/offrepo 镜像）
8. scripts/ch/archiver.py——归档唯一通道（三阶段 export→verify→drop）
9. 探针脚本 .runtime/tmp/{ch_stats,ch_truncate_logs,bench_disk,parse_wiztree}.py（可能已被 TTL 清，可按 §3 真源重建）

## §4 本线已完成（勿重做）
1. CH 系统日志 9 表 TRUNCATE，释放 145G（5.7→151G），业务零触碰零停机（2026-09-19）
2. 研报 90,243 件迁移 G 抽屉库完成并抽样验证（另一会话执行）
3. 全套勘察+方案+总令落盘（§3 的 1-4 号文档）；D/E 盘软件不迁裁定成立（软件合计仅 16G，注册表手术不值）

## §5 本线待执行任务清单（大目标 S1-S7→波次 W1-W7；全文见 a0_master_order.md，此处浓缩）
**大目标**：CH 瘦身到位+日志滚动永久自动化+冷储主库迁 F+G 镜像+备份 3-2-1+宿主清偿+vhdx 季度压缩机制化；终态=五盘容量对照表全绿+热层约 360G 稳态+全自动无人值守+dashboard 冷储检测绿+恢复演练通过。
- W1 CH 库内清偿（S1）：12 张尸体表逐表 export Parquet 双副本（F+G）→行数 verify→凭批文 drop【M】；欠账 24.9G 走 archiver archive-range；验收=内部空闲≥200G+尸体清零。
- W2 日志滚动永久化（S2，最急）：text_log level 调低+各 system log 表原生 TTL（trace_log/query_log 7 天、其余 14 天）+max_size 轮转→低峰重启 CH【M】→24h 复测膨胀<1G/天。
- W3 冷储主库落 F（S3）：E:\zephyr_cold_archive→F:\zephyr_cold\50_archive\by_project\zephyralpha\（robocopy+文件数/字节/5% hash 对账）→引用 7+1 处同 commit 改齐【M】→dashboard 探针绿→E 侧留观 30 天；G:\zephyr_cold 整体迁 F 同配方。
- W4 F↔G 调换（S4）：首查 /mnt/chbackup_local 身份→暂停 backup.ps1→ch_backup_disk.vhdx 526G/db_dumps/offrepo 大镜像 F→G 对账→backup_config offrepo targets 更新+新增 F 冷储→G 镜像条目→恢复 backup.ps1 实跑成功。
- W5 宿主清偿（S5+S6）：.runtime 45G 走 classify_workspace_wip 流程；models/ 14.3G 先 rg 引用再处置；tmp_db_dumps 轮转；D:\nonexistent 等小目录三层验证后清；研报对账（≥2026-10-18 才删 E 侧）；验收=D 剩余≥60G。
- W6 vhdx 压缩（S7，Owner 在场窗）：F 新鲜备份前置→停 VM→Optimize-VHD Full→起 VM→全链健康探针→季度巡检自动化登记；验收=vhdx≤450G+内部空闲维持≥150G。
- W7 终验红蓝：五盘对照表+引用残留 rg 扫描+搬运抽 hash 复测+备份恢复演练两次（G vhdx 分区+F 冷储 parquet 分区）→交付报告。
- 依赖约束（供你排序）：W1 需 dataqa R1 基线先落（作前后对照）；W2 时间最急（2-3 个月窗）；W3 引用改齐宜在 final3 working 清零后（热文件竞争小）；W4 须夜间无备份触发窗；W6 须 Owner 在场；研报删除挂 10-18 日历窗。

## §6 冲突与窗口（整合时必须遵守）
三队在飞期本线全线禁动：drop/CH 重启/跨盘搬运/清 .runtime 全部延后。具体撞点：dataqa 给全库每表量行数（中途删表毁其 R1）；tilib 明文 technical_indicator 宽表白天禁写入（archiver 扫 TI 撞它）；final3 挖矿狂查 CH（重启=打断）；三队高频 commit 触发 backup.ps1（搬运被打断）；三队 staging/claim/心跳全在 .runtime（清理=拆台）。唯一例外已执行：09-19 晚日志 TRUNCATE（秒级/无中断/保护性排雷）。

## §7 Owner 签字清单（6 项，请汇总进统一签字单）
①契约 INV-RET-002 修订（三步走 shadow→半自动→全自动，ruling_registry 同 commit，INFRA-STORE-002/LOG-OPS-001 同步）；②尸体表处置（推荐 export→verify→DROP）；③vhdx 压缩复决+150G 定案；④offsite 异地副本形式（月度拔盘 vs 小体量上云）；⑤db_dumps 版本化保留天数（建议 14 天）；⑥批次排期（收口后批 0-3 是否连做+shadow 起算日）。

## §8 纪律
禁 cron/sleep-loop（事件触发，backup 成功事件链为合法先例）；数据第一公理（删除前两份验证副本）；热文件 safe_write_text+CAS；.md 带 ttl frontmatter 字母开头 snake_case；提交唯一正门 git_commit.py --enqueue --files 白名单；避让清单=ruling_registry/gate_registry/capability_registry/tasks.yaml/AGENTS.md/docs/03_modules/**/data/strategy_intake/**/data/crypto/**/data_handler.py/akshare_provider.py/apply_market_tables_ddl.py 本体+三队目录只读；回执六要素+证据等级[亲验]/[转报]/[推断]；禁虚报，做不到如实写原因。
