---
ttl: task_bound
---

# 【收口总令】磁盘重整+冷储备份自动化落地——六波一键施工
# sid 建议：st-diskreorg-202609XX ｜ 落盘：docs/_working/disk_reorg_campaign/ ｜ 执行全程=GLM 5.3 Flash，Max 只守关卡
# 启动条件：st-final3 + st-tilib-clear + st-dataqa 三个施工队全部收口后，Owner 粘贴本令开工

> **⚠️ 2026-09-21 架构定案增补（Owner 拍板）：备份总仓=G（一套完整备份）+ F=冷储专项（纯冷库）+ CH 双写第二链 + offsite=Owner 手动月度拿第三块盘离场（=标准 3-2-1）。本令 W4（备份层）由 `a3_safe_construction_checklist.md` 阶段 4-5 取代；W1/W2/W3/W5-W7 不变并纳入 a3 阶段 1/2/3/6/7/8。执行以 a3 清单为准（含安全施工通则七条与顺序总览）。**

## §0 终极目标（先读，一切任务服务于它）
**一句话**：把磁盘重整的全部动作安全落地——CH 库瘦身到位、日志滚动保留永久自动化、冷储主库迁 F+G 兜底镜像、备份链 3-2-1、宿主垃圾清偿、vhdx 季度压缩机制化。终态=五盘容量对照表全绿 + CH 合规热层约 360G 稳态 + 冷储/备份全自动无人值守 + dashboard 冷储检测绿 + 备份恢复演练通过一次。

**七子目标（每条有唯一验收数字）**：
- S1 CH 库内清偿：尸体表 35.4G 处置完毕 + 契约欠账 24.9G 归档，VM 内部空闲 ≥200G
- S2 日志永久滚动：text_log 级别调低 + 全部 system log 表挂 TTL，重启后 24h 复测膨胀 <1G/天
- S3 冷储主库落 F：E:\zephyr_cold_archive + G:\zephyr_cold 全部迁入 F:\zephyr_cold，代码引用 7+1 处同 commit 改齐，dashboard 冷储检测绿
- S4 备份链 3-2-1：G 盘承接 ch vhdx/db_dumps/offrepo 大镜像 + 新增"F 冷储→G 镜像"条目；backup.ps1 恢复并实跑一轮成功
- S5 宿主清偿：.runtime 清到 <5G、models/ 处置、tmp_db_dumps 轮转、垃圾小目录清零，D 盘剩余 ≥60G
- S6 研报收口：E:\数据下载\研报 对账（执行日 ≥2026-10-18 才删 E 侧）
- S7 vhdx 压缩落地：按 150G 冗余定案执行一次压缩（Owner 在场窗）+ 季度巡检自动化登记

## §0.5 启动前置（缺一不开工）
A. 三队收口验证（读交付物为准，禁凭印象）：
  1. final3：docs/_working/final3_campaign/ 终局交付报告存在 + working C 类计数终态
  2. tilib：docs/_working/tilib_clearance_20260920/a5_delivery_report.md 存在
  3. dataqa：docs/_working/dataqa_audit_20260920/ 四报告（R1-R4）齐
  4. git 主区脏文件 <20 且 commit_queue 无新死信
B. Owner 签字状态：**已全部签署（2026-09-21，全按推荐项）——施工全程无需再请示，唯一到场点=vhdx 压缩停机窗点头**：
  1. 契约 INV-RET-002 修订=同意（五重安全阀+事件触发自动+滞回 1 月+批限量+kill switch；三步走 shadow→半自动→全自动；ruling_registry 同 commit，INFRA-STORE-002/LOG-OPS-001 同步修订）
  2. 尸体表 35.4G=export Parquet 双副本→行数 verify→DROP（冷库留档）
  3. vhdx=恢复压缩（季度+触发式节奏，150G 红线，半自动扳机）
  4. offsite=Owner 月度手动+新购第三块盘专做离场（G 留家值班不拔走）
  5. text_log 级别=information（trace_log/query_log TTL 7 天、其余 14 天）
  6. db_dumps=14 天版本化（替换现"单份覆盖式"）
  7. 排期=三队收口当晚立即开工，通宵连跑阶段 0-4，次日白天收尾 5/6/8；影子试运行起算=施工完成日
  8. 架构定案=备份总仓 G / 冷储专项 F（纯冷库）/ CH 双写第二链 / working_vault 迁 G（原"留 F 例外"作废）；F:\ch_vm_backup 默认按 B 瘦身为配置级轻备份
C. 方案真源存在：docs/_working/cold_backup_automation/00_master_plan.md + 01_mining_findings.md（若缺，本班先开波0 按挖矿 SOP 补方案再施工）

## §1 模型路由
Flash 执行全部；Max 只在五关卡介入：破坏性 DB 操作（drop/drop partition）执行前、CH 重启窗、契约修订落地、跨盘搬运启动、每波头条数字复核。禁虚报；未达成如实写原因。

## §2 冷启动（每 shell 必做）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"；python --version 须 3.12.x
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status
会话注册+心跳+提交同 shell 链（90s 活性窗，配方照抄 docs/_working/rule_audit_campaign/2026-09-19-construction-handover-prompt.md 坑册）；长批任务登记 data/runtime/process_reaper_keep.txt。宪法 AGENTS.md 全程有效。

## §3 真源读序（开工前）
1. docs/_working/disk_reorg_plan_2026_09_19.md（勘察底数 v2+引用 7+1 清单）
2. docs/_working/cold_backup_automation/00_master_plan.md + 01_mining_findings.md（自动化方案+挖矿发现）
3. docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml（10 层保留真源）
4. scripts/backup/backup_config.yaml + backup.ps1 + backup_reconciler.py（备份链现状）
5. scripts/ch/archiver.py（归档唯一通道，三阶段 export→verify→drop）
6. docs/_working/altdata_line/10_g_drive_cold_storage_sop.md（冷库 SOP，三红线）
7. dataqa 四报告（R1 表健康基线=本班执行前后对照物）

## §4 硬事实（2026-09-19/20 实测；执行日先重跑探针刷新台账，禁凭记忆）
- 五盘：C=NVMe 系统；D=NVMe 731G（HyperV VM zephyr-ch data.vhdx 599G 占 83%）；E=SATA SSD 931G（软件+热数据）；F=SanDisk 2T USB 实为 SSD（读 374/写 340 MB/s）；G=东芝 4T USB 机械（写 70 MB/s、小文件 11.5 files/s）。速度序 D>E>F>>G。
- CH 26.6.1（VM 内 /var/lib/clickhouse）：系统日志 145G 已清（2026-09-19，5.7→151G）；业务活跃 426.5G=合规热层 361G+尸体表 35.4G（news_corrupt 13.0/news_pre_tz2 12.9/各 tz_bak 约 8+kline_daily_bak 等）+契约欠账 24.9G（TI 窗口外 19.4+冷线 5.5）。text_log 级别未调（~50G/月回涨）——**S2 是时间最急项，151G 余量约撑 2-3 个月**。
- CH 凭据与坑：唯一真源 config/.env.clickhouse；库内仅 default/zephyr_reader/zephyr_writer 三账号，zephyr_writer 无 TRUNCATE system.* 权限（RBAC 设计勿改），系统表操作用 default 超户；>50G 表 TRUNCATE 被 max_table_size_to_drop=50G 保险丝拦——同 `?session_id=xxx` 两连发（SET→SELECT 验证生效→TRUNCATE），禁全局关保险丝；CH 26.6 无 multiquery 参数；CH TSV 分区串带 `\'` 转义，元组分区解析先 strip 反斜杠。
- 冷储现状：G:\zephyr_cold 抽屉库（00_manifest/drawers.jsonl 台账，研报 90,243 件在库）；E:\zephyr_cold_archive 117.6G Parquet（c1_market 115.8+c3_fundamental 1.8）待迁 F；引用 7+1 处=scripts/ch/archiver.py:69,732、config/asset_inventory.yaml:139、infrastructure_registry.yaml:200-203、registry_of_logs.yaml:808、services_registry.py:118-120、backup_config.yaml:88-89、核对 data_retention_contract.yaml。
- VM 内第二盘 /mnt/chbackup_local（1081G/余698G）**身份已破案（2026-09-21 Get-VMHardDiskDrive 实证）**：= 宿主机 `F:\ch_backup_disk.vhdx` 以 SCSI 直挂虚拟机的第三块盘（0:3）——它不是备份副本，是**运行中 VM 的现役备份盘**（CH 每日增量写在这里），**运行期绝不可搬**；W4 修正为：该盘留 F（SSD 当备份盘=最优解），F→G 实际搬运对象=陈旧全拷贝 `F:\ch_vm_backup\data.vhdx`（2026-08-22，635G，已被新备份体系取代，Owner 确认后删或归档）+ offrepo 大镜像。
- 探针脚本：.runtime/tmp/{ch_stats,ch_truncate_logs,bench_disk,parse_wiztree}.py（若已被清按 §3 真源重建）；heredoc 跑 stdin 无 `__file__`，导入项目模块的脚本必须 Write 落文件再跑。
- 主区可能有三队收尾残留脏文件：一切提交只走 --files 白名单，绝不 git add -A/.。

## §5 组织形态与自适应并发
1. 本会话=总包：派波/验收/裁定登记/收口；细节施工派子代理。
2. 自适应爬坡：起步 3 并发→完成一波+1 探测→任一死亡/超时降 1 档稳态→每小时重探；额度跨会话共享，浮动是常态。worker≤20 红线。
3. 机械扫描/对账/探针一律 Python 直跑，不占子代理额度。
4. 性能哨兵：每 30 分钟把 RAM 可用/worker 数写进 a1 台账；RAM<8G 或触顶即降档。
5. 每波自审循环：①验收命令实测数字 ②抽样复验≥3 项 ③出问题即修→复检，连续两轮 0 问题才开下一波。

## §6 波次（线内先挖后干、线间并行流水；【M】=Max 关卡；【O】=Owner 在场窗）
- **W1 CH 库内清偿（S1）**：尸体表 12 张逐表：export Parquet 双副本（F 冷储+G 镜像落点）→行数 verify→凭 §0.5-B2 批文 drop【M 前置】→欠账 24.9G 走 archiver archive-range（落点=W3 完成后的 F 冷储路径，若 W3 未完先落 E 原路径）→验收：system.parts 复查内部空闲 ≥200G+尸体表清零。
- **W2 日志滚动永久化（S2，最急）**：改 CH server config：text_log level=information（按 Owner 签项）+ 各 system log 表 TTL（trace_log/query_log 7 天、其余 14 天）+ max_size 轮转→低峰重启 CH【M：重启步骤复验】→24h 后复测膨胀 <1G/天→验收=S2。
- **W3 冷储主库落 F（S3）**：E:\zephyr_cold_archive→F:\zephyr_cold\50_archive\by_project\zephyralpha\（robocopy /E /COPY:DAT /MT:16）→文件数+字节+5% hash 对账→引用 7+1 处同 commit 改齐【M：引用复核】→dashboard services_registry 探针绿→archiver list/stats 试跑→E 侧改 .migrating 留观 30 天登记到期删。G:\zephyr_cold 整体迁 F:\zephyr_cold 同配方（G 侧只读保留 30 天）。验收=S3。
- **W4 F↔G 调换（S4，2026-09-21 修正）**：~~ch_backup_disk.vhdx 搬 G~~ **该盘经查是虚拟机 SCSI 直挂的现役备份盘（F:\ch_backup_disk.vhdx 0:3），运行期禁搬，永久留 F**。~~635G 陈旧全拷贝~~ **F:\ch_vm_backup 经查是设计内组件（backup_ch_vm.ps1 MOD-INF-043 §3.6 智能周备：AutoCheck 校验 CH 版本+配置哈希，未变则跳过——08-22 时间戳=系统按设计在跳过，非陈旧垃圾）**，其唯一价值=OS+CH 程序+配置（数据部分与增量备份冗余）；处置三选一待 Owner 裁定：A 保留现状 / B 瘦身为配置级轻备份（删 555G 数据部分，收口后改 backup_ch_vm.ps1）/ C 整机制退役（删目录+退 backup_ch_vm.ps1+restore.ps1 vm 模式+config 条目三处同步）。offrepo 大镜像 F→G robocopy+对账→backup_config offrepo targets 更新（cold_archive 源改 F 新家；新增 F 冷储→G 镜像条目）→恢复 backup.ps1 实跑一轮成功→验收=S4。
- **W5 宿主清偿（S5+S6）**：.runtime 走 classify_workspace_wip 流程清（禁肉眼判罚）→models/ 14.3G 先 rg 全仓引用（Ollama/训练/测试消费方），无引用迁 E:\ai_models\zephyr 有引用登记处理→tmp_db_dumps 轮转→D:\nonexistent 等小目录三层验证后清→研报对账（E:\数据下载\研报 vs G 2019_bundle 文件数+字节+5% hash）；执行日 ≥2026-10-18 才删 E 侧，否则登记到期提醒→验收：D 剩余 ≥60G。
- **W6 vhdx 压缩（S7，【O】Owner 在场窗）**：前置=F 新鲜备份+VM 内空闲核对→停 VM→管理员 Optimize-VHD -Path D:\HyperV\VMs\zephyr-ch\data.vhdx -Mode Full→起 VM→CH 全链健康探针（表 count 抽查+dashboard+tick 查询一条）→季度巡检自动化登记（季初自动生成压缩预检单：内部空闲/垃圾量/备份新鲜度三指标）→验收：vhdx 文件 ≤450G、D 盘剩余显著回升、VM 内空闲维持 ≥150G。
- **W7 终验红蓝（全部波后）**：五盘容量前后对照表+CH 热层体量对账+working 无新增烂账；红蓝一轮（红队攻击=对账假绿/搬运丢文件抽 hash 复测/引用改漏（rg "E:\zephyr_cold_archive" 残留扫全仓）/backup.ps1 首跑失败隐瞒/TTL 配置写错导致日志提前全丢）；备份恢复演练两次（G vhdx 副本恢复一分区+F 冷储 parquet 恢复一分区）→临时件清→交付报告（终极目标逐条对账+前后对照表+Owner 待签项归零情况）。

## §7 施工纪律（违反必炸）
提交唯一正门 scripts/git_commit.py --enqueue --files 白名单；commit 后 git log -1 --name-only 核归属；改前 lock_files.py acquire claim；失败重试带 --adopt-prior-work；新文件 CREATE-GUARD token 同批；.md 带 ttl frontmatter、字母开头纯 snake_case；热文件 safe_write_text+CAS 禁 yaml.dump 整写；数据库操作一律既有通道（archiver/DatabaseService/CH HTTP+config/.env.clickhouse）；**任何 drop 前必须双验证副本+行数 verify——数据不能坏是第一公理**；跨盘搬运一律先对账后动源，源侧留观 30 天；Git Bash 无 pgrep、heredoc 吞字符——多行 python 一律 Write 落文件再跑。
避让清单（撞锁等 5 分钟禁硬闯）：三队目录 final3_campaign/tilib_clearance_20260920/dataqa_audit_20260920（只读禁改）、ruling_registry/gate_registry/capability_registry/tasks.yaml/AGENTS.md/docs/03_modules/**/data/strategy_intake/**/data/crypto/**/data_handler.py/akshare_provider.py/apply_market_tables_ddl.py 本体。

## §8 自裁框架（通宵无人打断）
遇分歧按此裁："作为客观专业架构师，从第一性原理出发，长远期战略考虑，项目 100% AI 开发现实，参照专业机构实践/量化社区惯例/GitHub 开源实现，给出分析过程+裁定结果"。真无法裁定=登记 docs/_working/disk_reorg_campaign/o_pending_owner.md+跳过继续。**破坏性操作（drop/CH 重启/搬运启动/vhdx 压缩）永不自裁，必须 §0.5 批文或 Owner/Max 关卡放行。**

## §9 断点续班+回执+收官
进度全落 docs/_working/disk_reorg_campaign/a1_ledger.md（每行：波次/动作/commit/实测数字/状态/证据指针）——中断后新会话凭本令+读 a1 即续，幂等可重派。
每波回执六要素：①改动文件+commit hash（核归属）②验收实测数字（禁引旧数）③复验命令④停手/关卡项⑤证据等级[亲验]/[转报]/[推断]⑥未完成+原因。
收官：连续两轮 0 问题→红蓝一轮→GitCommitGateway 全落地→临时件清（.runtime/tmp 自建目录删）→终局交付报告 a5_delivery_report.md（终极目标逐条对账+五盘容量/CH 体量/备份链前后对照表）。做不到的逐条写"未达成+原因"，禁虚报。
