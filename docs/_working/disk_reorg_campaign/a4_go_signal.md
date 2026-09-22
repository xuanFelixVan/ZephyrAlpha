---
ttl: task_bound
---

# 【开工令】磁盘重整+冷储备份自动化——六项已签，三队收口当晚即跑
# sid：st-diskreorg-20260921 ｜ 落盘：docs/_working/disk_reorg_campaign/ ｜ 执行=GLM 5.3 Flash 总包+子代理自适应并发，Max 五关卡
# 本文=唯一开工入口；执行本体=a3_safe_construction_checklist.md 阶段 0-8；总令框架=a0_master_order.md

## §0 项目背景（60 秒版）

ZephyrAlpha=Owner 个人量化交易系统，100% AI 开发，仓库 D:\ZephyrAlpha，宪法 AGENTS.md 全程有效（提交网关/热文件 CAS/禁 cron 事件触发/own-scope 等硬规则）。宿主 Windows+HyperV 虚拟机 zephyr-ch 跑 ClickHouse 26.6.1 行情库。五盘定案角色：
- C=NVMe 系统；**D=NVMe 731G=生产**（项目仓 74.7G+CH 虚拟机 data.vhdx 599G，读 1482MB/s 回测主力）；
- E=SATA SSD 931G=软件+热数据（475/437 MB/s）；
- **F=SanDisk 2T USB-SSD（374/340 MB/s）=冷储专项（纯冷库）**：研报语料、Parquet 老分区、原料——回测偶尔读，放快盘；
- **G=东芝 4T USB 机械（写 70 MB/s，小文件 11.5 files/s）=备份总仓（一套完整备份）**：代码快照/db 导出/git 全史/offrepo/冷储夜镜像/CH 双写第二链；
- offsite=Owner 手动月度拿第三块盘离场。**=标准 3-2-1：3 副本（D+G+离场）/2 介质（内置+USB）/1 离场。**
**数据安全第一公理：任何删除前必须有两份验证过的副本；drop 前必须行数 verify；源目录永远最后删且留观 7-30 天。**

## §1 终极目标（一切任务服务于它）

CH 瘦身到位+日志滚动永久自动化+冷储主库落 F+备份总仓落 G+CH 双写+宿主清偿+vhdx 季度压缩机制化。终态验收=五盘容量前后对照表全绿+CH 合规热层约 360G 稳态（VM 内空闲≥200G→压缩后维持≥150G）+冷储/备份全自动无人值守+dashboard 冷储检测绿+恢复演练三次通过+交付报告六要素齐。

## §2 Owner 签字状态（2026-09-21 全签，全按推荐项——施工无需再请示，唯一到场点=压缩窗点头）

1. 契约 INV-RET-002 修订=同意（五重安全阀：备份成功才动手/导出验行数/双副本落地/批限量/熔断 kill switch；滞回 1 月；三步走 shadow→半自动→全自动；ruling_registry 同 commit，INFRA-STORE-002/LOG-OPS-001 同步）
2. 尸体表 35.4G=export Parquet 双副本→行数 verify→DROP（冷库留档）
3. vhdx=恢复压缩（季度+触发式，150G 红线，半自动扳机，Owner 到场窗点头）
4. offsite=Owner 月度手动+新购第三块盘（G 留家不拔走）
5. text_log 级别=information（trace_log/query_log TTL 7 天、其余 system log 14 天、max_size 轮转）
6. db_dumps=14 天版本化（替换单份覆盖式）
7. 排期=三队收口当晚立即开工，通宵连跑阶段 0-4（约 10-17h），次日白天收尾 5/6/8；影子试运行起算=施工完成日
8. 架构=备份总仓 G / 冷储专项 F / CH 第二备份链 / working_vault 迁 G；F:\ch_vm_backup 默认按 B 瘦身。**进度事实（2026-09-21 深夜核）：第二链已由 st-disk-ch-20260921 以 SCSI 热挂双盘双写实现零停机（inc 71G 已入 G 链）**——补挖结论（CH 原生 BACKUP 单命令单目的地；业界=周全量+日增量+链重置）佐证双盘双写与热挂操作合法合规；接手会话禁改动既有双链机制

## §3 开跑条件（满足即跑，禁再等人为天数）

1. 三队收口核验：final3 终局交付报告在盘+working C 类终态；tilib a5_delivery_report.md 在盘；dataqa 四报告在盘；主区脏文件<20+队列无新死信
2. 签字状态=§2（已完成）
3. 开工前先读 a1_ledger.md 与本目录既有件——**另一会话已提前按旧方案推进部分阶段**（W1 备料 waste_table_*、影子滚动归档 rolling_archive_plan_shadow.jsonl、vhdx 预检单均在盘）：**接手=对账续做，禁重复施工、禁覆盖其产物**；其已完成的勾选项直接标完成+证据指针

## §4 冷启动（每 shell 必做）

export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"；python --version 须 3.12.x
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status
会话注册+心跳+提交同 shell 链（90s 活性窗，配方=docs/_working/rule_audit_campaign/2026-09-19-construction-handover-prompt.md 坑册）；长批登记 data/runtime/process_reaper_keep.txt

## §5 真源读序（开工前 60 分钟，按序）

1. docs/_working/disk_reorg_campaign/a3_safe_construction_checklist.md——**执行本体**（阶段 0-8 逐勾选+安全施工通则七条+排期定案）
2. docs/_working/disk_reorg_campaign/a0_master_order.md——总令框架（硬事实/避让清单/自裁框架/回执六要素）
3. docs/_working/disk_reorg_campaign/a1_ledger.md——前序会话进度台账（接手对账）
4. docs/_working/disk_reorg_plan_2026_09_19.md——勘察底数 v2（盘位/速度/库内三笔账/引用清单）
5. docs/_working/cold_backup_automation/00_master_plan.md + 01_mining_findings.md——自动化方案 13 章+挖矿报告（身份证机制/reconciler 五重安全阀/3-2-1-1-0/保留与清除总清单 17 行）
6. docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml——10 层保留契约真源
7. scripts/backup/{backup_config.yaml, backup.ps1, backup_reconciler.py, restore.ps1, backup_ch_vm.ps1}——备份链现状
8. scripts/ch/archiver.py——归档唯一通道（export→verify→drop 三阶段）
9. docs/_working/altdata_line/10_g_drive_cold_storage_sop.md——冷库 SOP 三红线
10. docs/_working/dataqa_audit_20260920/ 四报告——R1 表健康基线（执行前后对照物）

## §6 硬事实（2026-09-19/21 实测；执行日重跑探针刷新台账，禁凭记忆）

- CH VM 内 /var/lib/clickhouse 631.9G：系统日志 145G 已清（09-19，5.7→151G 余）；业务活跃 426.5G=合规热层 361G（tick 141.5G=2025-01 起、约 6.7G/月唯一增长源+TI 窗口内 151G+分钟线 66G+小表）+尸体表 35.4G（约 12 张 news_corrupt/pre_tz2/各 tz_bak）+契约欠账 24.9G（TI 窗口外 19.4+冷线 5.5）。**text_log 仍 trace 级 ~50G/月回涨，151G 余量约撑 2-3 个月——阶段 2 最急，最迟 2026-11 前完成**。
- CH 凭据与坑：唯一真源=config/.env.clickhouse；仅 default/zephyr_reader/zephyr_writer 三账号，系统表操作用 default 超户（zephyr_writer 无 TRUNCATE 权限=RBAC 设计勿改）；>50G 表 TRUNCATE 被 max_table_size_to_drop=50G 保险丝拦→同 ?session_id=xxx 两连发（SET→SELECT 验证→TRUNCATE），禁全局关保险丝；CH 26.6 无 multiquery；TSV 分区串带 \' 转义先 strip 反斜杠。
- **F:\ch_backup_disk.vhdx=虚拟机 SCSI 直挂的现役备份盘（0:3），运行期禁搬，阶段 4.7 双写落地稳定 14 天前不动它**；F:\ch_vm_backup=设计内智能周备（AutoCheck 跳过未变周），默认 B 瘦身。
- 冷储现状：G:\zephyr_cold 抽屉库（drawers.jsonl 台账，研报 90,243 件）+E:\zephyr_cold_archive 117.6G Parquet 待迁 F；E:\数据下载\研报 84.7G 已复制进 G（2019_bundle 29,998=29,998），E 侧删除须 ≥2026-10-18。
- 引用 E:\zephyr_cold_archive 共 7+1 处须同 commit 改齐：scripts/ch/archiver.py:69,732、config/asset_inventory.yaml:139、infrastructure_registry.yaml:200-203、registry_of_logs.yaml:808、services_registry.py:118-120、backup_config.yaml:88-89、核对 data_retention_contract.yaml。
- 探针脚本 .runtime/tmp/{ch_stats,ch_truncate_logs,bench_disk,parse_wiztree}.py（可能被 TTL 清，按 §5 真源重建；heredoc 跑 stdin 无 __file__，导项目模块的脚本必须 Write 落文件再跑）。
- 挖矿三发现：①business_data_categories.yaml 114 品类 lifecycle 字段未启用（身份证载体在）；②storage_tiering.py 纸面模块待裁定接线/退役；③backup_daily_trigger.ps1=禁 cron 合法先例，滚动归档挂备份成功事件链即合规。

## §7 执行本体：阶段 0-8（逐勾选以 a3 为准；一屏版）

> **进度速览（2026-09-21 深夜核，权威=a3 勾选+session st-disk-ch-20260921）**——已完成：阶段 0 全、阶段 1 全（95,188 件/137.6G 迁 F 对账 PASS、引用 7/8 齐 commit 6684ba5d83）、2.1-2.2（config+闪断窗重启）、3.1 导出半（13/13 双副本+sha256 全等）+3.2 滚动归档 24 轮、4.1/4.7（G 骨架+双链热挂零停机 inc 71G）、6.1-6.6（.runtime 清 35.15G/D=61G 达标/offsite 手册落档）、7.4 预检自动化。**待办**：2.3 复测、3.1 drop（等 Owner 逐表批 `waste_table_report_list.md`，裁定 #382 逐表批制）、3.3、4.2-4.6（working_vault 迁 G 等）、4.8、5.1-5.2、7.1-7.3/7.5（Owner 到场压缩）、8 全部（终验红蓝+演练）。
> **增补阶段 4.9 镜像去重批（2026-09-22 WizTree 勘实，并入阶段 5 执行）**：G 盘 ch_vm_backup（8-22 旧整机拷贝 591.57G）存在**三份完全等值副本**——`G:\backup\ch_vm_backup`、`G:\zephyr_backup_mirror\ch_vm_backup`、`G:\zephyr_cold\ch_vm_backup`，合计 1774.7G 冗余（多夜镜像改址叠加；F 盘另有原件第 4 份）。处置：三方 hash 确认等值后删二留一或三份全删（F 原件在盘佐证），`G:\zephyr_cold\zephyr_cold` 嵌套 274.49G 对照 manifest 解析归位；预期 G 剩余 342G→2100G+（9.2% 红线解除）。F 盘 10-05 阶段 5 后回约 1300G。
> **增补清理项（2026-09-22 补录）**：F 盘过渡旧件三笔——①`F:\working_vault` 旧副本 200.7G（留观至 **09-28**，G 总仓已对账 PASS）②`F:\offrepo_backup` 旧镜像 136.6G（G:\backup\offrepo 273.62G 已接管，核等后删）③`F:\db_dumps` 0.36G 旧件（G 版本化已接管）——并入阶段 5/去重批同批核等清理；**F 盘最终只保留：冷储主库 + CH 主链盘（ch_backup_disk.vhdx，活挂载设计内例外）+ 个人文件 + pdf 缓存**。
> **阶段 9 知识固化（2026-09-22 本会话执行 3/4）**：①INFRA-STORE-003"四盘分工与存储地图"条目=已立（infrastructure_registry.yaml，YAML 解析验证绿）②MOD-INF-043 蓝图 2.0.5→3.0.0（v3.0 纪要：G 总仓/双链/冷储专项/滚动归档/vhdx 排班化）③宪法 §7 DatabaseService 行增存储分工指针（行数 140 不变=等长替换合规；**待 Max/Owner 复验**）④capability 关键词登记+ROOR 挂接+permanent 手册提炼+图书馆卡=**余留给执行会话**（capability 册 tilib 在飞竞写避让，token 同批走）。

```
三队收口当晚即开
 阶段0 基线取证+冻结 backup.ps1（0.5h，不动数据）
 阶段1 冷储主库落 F（E 117.6G+G 抽屉库迁入；对账三件套+引用 7+1 同 commit；E 侧留观 30 天）→ 2-4h
 阶段2 CH 日志 TTL 永久化（最急！改 config+重启窗）→ 0.5h
 阶段3 CH 库内清偿（尸体表双副本验证后删+欠账归档；内部空闲≥200G）→ 1-2h
 阶段4 备份总仓落 G【核心】working_vault 迁 G(种子过夜)→db_dumps/git/offrepo 迁 G
        →F 冷储→G 夜镜像上线→CH 双写第二链(唯一 VM 窗)→backup.ps1 换 G 实跑全绿 → 5-9h
 阶段5 CH 旧备份盘处置+F 纯化（双写稳定 14 天后摘旧盘；ch_vm_backup 按 B 瘦身）
 阶段6 宿主清偿(.runtime 45G/models 14.3G 查引用/研报对账)+offsite 手册落档；D≥60G
 阶段7 vhdx 压缩（Owner 到场窗）：停 VM→Optimize-VHD Full→健康探针→季度巡检登记；vhdx≤450G
 阶段8 终验红蓝+恢复演练三次（CH 增量/冷储 Parquet/代码快照）→终局交付报告
```

## §8 施工纪律与避让

提交唯一正门 scripts/git_commit.py --enqueue --files 白名单；commit 后 git log -1 --name-only 核归属；改前 lock_files.py acquire claim；失败带 --adopt-prior-work；新件 CREATE-GUARD token 同批；.md 带 ttl frontmatter 字母开头 snake_case；热文件 safe_write_text+CAS；禁 git add -A/.；多行 python 一律 Write 落文件再跑（heredoc 吞字符）。
避让（撞锁等 5 分钟）：三队目录 final3_campaign/tilib_clearance_20260920/dataqa_audit_20260920 只读禁改；ruling_registry/gate_registry/capability_registry/tasks.yaml/AGENTS.md/docs/03_modules/**/data/strategy_intake/**/data/crypto/**/data_handler.py/akshare_provider.py/apply_market_tables_ddl.py 本体。
自适应并发：起步 3→+1 探测→死亡降档；worker≤20；机械扫描走 Python 不占额度；性能哨兵 30 分钟记台账。

## §9 自裁框架+回执+收官

自裁："作为客观专业架构师，从第一性原理出发，长远期战略考虑，项目 100% AI 开发现实，参照专业机构实践/量化社区惯例/GitHub 开源实现，给出分析过程+裁定结果"。无法裁定=登记 o_pending_owner.md+跳过。**破坏性操作（drop/重启/搬运启动/压缩）永不自裁——签字已给到 §2 对应项，按项执行即可；超出 §2 清单的破坏性动作一律停手上报。**
每阶段自审循环：连续两轮 0 问题才进下一阶段。回执六要素：①文件+commit 核归属②验收实测数字（禁引旧数）③复验命令④停手/关卡项⑤证据等级[亲验]/[转报]/[推断]⑥未完成+原因。
收官：GitCommitGateway 全落地→临时件清→终局交付报告（终极目标逐条对账+五盘容量/CH 体量/备份链前后对照表+Owner 待办归零情况）。禁虚报，做不到如实写原因。
