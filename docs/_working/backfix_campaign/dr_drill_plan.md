---
ttl: task_bound
title: 四类自动恢复演练方案（代码／SQLite／ClickHouse／VM）——备份线 2026-10-13 夜班 P1-A 方案袋（零施工）
session: st-bakdr-20261013
completes_when: Owner 批复后由施工波次 1-5 落地，本册并入 docs/01_policies_and_standards/sop/data_ops_sop/ 的恢复演练真源，随批归档
---

# 四类自动恢复演练方案（代码／SQLite／ClickHouse／VM）

> 本册是**方案袋**：零施工、零改判据、零新建执行体。所有数字为 2026-10-13 22:5x-23:4x 实测（取证命令见 §10）。
> PG 月度演练（`ZEPHYR-RESTORE-DRILL`）覆盖面本册**不动**，只按令另袋修其打分器（见 §9 末段）。

## 0. 大白话＋Owner 只需回的几种话

老底：**备份一直在存，但"能不能拿回来"这句话，只有 PG 一条腿每月真验一次，代码／SQLite／ClickHouse／VM 四条腿一次都没自动验过。**
打比方：仓库每天锁门记账，但从没人拿钥匙试过能不能开门——钥匙断在锁里，要等到真要开门那天才知道。

本方案给每类配一把"试钥匙"的例行动作，分三档：
**L0＝只查清单（几乎免费，天天做）／L1＝真还原一小块到隔离区（分钟级，周或月做）／L2＝大动作（人工＋在场，季度）**。

要 Owner 点头的六件（不点则本班按"只做 L0＋L1 零写面"推进，不越界）：

| # | 事项 | 不点的后果 |
|---|------|-----------|
| O-1 | 新注册 4 支 OS 计划任务（one-shot，跑完即退） | 计划任务注册/变更按在册口径＝Owner 门位，故不点＝演练只能人工点火，等于现状 |
| O-2 | CH 演练走"结构对拍＋分区级表还原（预算 ≤8 GiB）"，全量 444 GiB 档只留人工 | 不点＝CH 恢复性永远只有"备份文件写成功了"这一层自证，没有"读回来对不对" |
| O-3 | SQLite 演练复用既有 `verify_backup()`（它今天**零消费者**） | 不点＝那把已有的尺继续当装饰件，而新写的尺是第二把尺（违 §4 内收） |
| O-4 | VM 月快照走"型 A＝配置面＋VM 定义面"；"型 B＝guest 内 OS+程序文件级镜像（实测 OS 面 du≈13 GiB）"要不要一起开 | 不点＝有整机重建所需的配置，但没有 OS/CH 程序本体，恢复要重装 |
| O-5 | 演练台账落 `data/databases/dr_drill_ledger.json`（与 `backup_state.json` 同性质同区） | 不点＝"演练没跑"与"演练跑了没人看"同形（在册老病），覆盖率无人可读 |
| O-6 | 备份链写侧补两个**只增观测位**（代码快照记 HEAD sha＋条目计数；SQLite 备份副本头 16 字节） | 不点＝代码腿对拍基线只能靠"当场工作区字节"，并行会话脏面会让它天天假红 |

## 1. 现状底账（实测，非叙述）

| 腿 | 真源工件（实测在位） | 体量实测 | 今天的可恢复性证据 |
|----|---------------------|---------|-------------------|
| 代码 | `G:\backup\working_vault\20261013\`（硬链接去重日快照，保留 14 天、min_keep 3、60 GB 地板）；`G:\backup\git_bundles\zephyralpha_full_{20261003,20261011}.bundle` | bundle 497,991,197 B／523,166,936 B；另有嵌套 `git_bundles\git_bundles\` 两支 09-14/09-15 陈旧件 853 MB | 2026-09-15 一次**人工**演练（63,691 件 sha256 抽检全匹配），所用脚本**未入库** |
| SQLite | `G:\backup\db_dumps\<date>\governance_backup.db`＋`session_backup.db`（源＝`data/databases/governance.db` 253,448,192 B、`session_continuity.db` 12,288 B） | 副本 253,444,096 B／12,288 B（20261013 轮） | 09-15 人工 PASS；此后**零自动** |
| ClickHouse | VM 内 `/mnt/chbackup_local`（＝`G:\ch_backup_disk2.vhdx`）的 `market.zip`＋`inc.zip`；每轮产 `report.databases.clickhouse.manifest`（226 条 `database/name/total_rows`） | base 298,968,010,737 B／inc 83,072,030,247 B；库内 4 个库 247 表（231 张有 active parts）、339.19 GiB、7,135,146,008 行 | `verified=True` 只是 `backup.ps1` 自检＋INV-11 的 `system.backup_log` 独立核验；**库级/表级 RESTORE 自 2026-07-28 未做** |
| VM | `D:\HyperV\VMs\zephyr-ch\{boot.vhdx,data.vhdx}`＋`zephyr-ch\Virtual Machines\*.vmcx/vmgs/vmrs` | **boot.vhdx FileSize＝4,194,304 B（空盘，虚拟 80 GiB）**；data.vhdx 604,755,722,240 B；vmcx 77,824 B、vmgs 4,194,816 B、vmrs 10,339,016,704 B | `G:\backup\ch_vm_backup` 已不存在（`infrastructure_registry.yaml:229` 记"已退役 2026-10-04 Owner 批"），`backup_ch_vm.ps1:153-154` 无条件 `exit 0` 密封，周任务 Disabled ⇒ **重建路径从未演练** |
| （PG，不动） | `G:\backup\db_dumps\<date>\depgraph.dump` 256,398,630 B＋`pg_globals.sql` 206 B | 月度 1 次四条件对账 | 唯一有自动演练的一腿，判据骨架本册直接沿用 |

## 2. 四腿共同骨架（不新造第二把尺）

PG 演练已裁的骨架＝`judge_drill()` 四条件合取（C1 表集合全等 ∧ C2 行数**方向性** drill≤live ∧ C3 老数据内容指纹 ∧ C4 子进程返回码分类）＋失败支八键契约（`pass/criteria/failed_criteria/rows/criteria_version/criteria_change_note/legacy_judge_note/status`，`rows={}` 取 dict 同型）。
**本方案把它当作四腿的裁决外形**，每腿只填自己的采集手段；三对判据一律按这三列写：

| 列 | 含义 | 不许有的形态 |
|----|------|-------------|
| 指纹 | 不可变内容的聚合哈希（文件 sha256／CH cityHash64 有界样本／DDL 规范化文本 sha256） | "存在即绿"（在册铁律：存在性≠内容判据） |
| 行数 | 条目数／表数／行数，一律**方向性**（drill≤live）或全等，按各腿是否可变决定 | 精确相等当恒尺（dump 是历史时点，PG P-3R1 已为此翻过一次车） |
| 关键字段 | 该对象"没坏"的最小语义证据（列集合／主键区间／引擎计数／版本串／文件头魔数） | 空集合当通过（0 命中必须带正对照，否则是假绿尺） |

## 3. 四腿明细

### 3.1 代码腿

**工件对拍基线必须钉在"抓取时刻的 HEAD"**——实测 `backup.ps1` 全文零处 `git rev-parse`，且工作区在多会话并发期是脏面（本班进场即见 `AGENTS.md`／`gate_registry.yaml`／`config/flags.yaml` 均 MM），拿"当前工作区字节"当尺＝天天假红。⇒ 写侧补两条只增观测位（O-6）：`working_vault/<date>/_manifest.head_sha`＋`_manifest.file_count`；写不进（无 HEAD 可取）＝备份腿自己报红，不许静默缺位。

| 档 | 频率 | 抽查面 | 三对判据 | 成本实测/预估 |
|----|------|--------|---------|--------------|
| L0 | 每轮备份收尾（已错峰在 Stage 4 后） | 日目录存在 ∧ `_manifest` 两键 ∧ bundle 最新份新鲜度 ≤8 天 | 行数：`is_file()` 谓词分层计数==manifest；关键字段：head_sha==当日 dev HEAD；指纹：manifest 自身的 sha 入账 | 秒级（**禁全树枚举**——52m45s 黑洞同族，见 O-6 的记账位设计） |
| L1 | 日频 | 从 HEAD 树抽 200 件（seed 写进报告）＋12 件在册关键件（AGENTS.md、backup.ps1、restore.ps1、backup_config.yaml、restore_drill.py、gate_registry.yaml、infrastructure_registry.yaml、startup_vocabulary.yaml、trae_060_*.yaml、module_translation_registry.yaml、config/flags.yaml、r5_digit_suffix_gate.py）；**现场 `git status --porcelain` 列出的脏件从抽样集剔除并计数披露** | 指纹：逐件 sha256(vault)==sha256(`git show HEAD:<path>`)；行数：剔除后候选 ≥100（不足＝不可判＝红，不是"少测点"）；关键字段：12 件白名单全在且非零字节 | 200 次小文件读（USB G:）≈10-30 秒 |
| L2 | 周频 | ①`git bundle verify` ∧ 从 bundle 克隆到隔离 scratch ∧ `git rev-parse` 回读；②从 vault robocopy 恢复 `scripts/backup/`＋`config/` 两目录全件到隔离区，逐件 sha256 对拍 | 指纹：两目录逐件全等；行数：恢复件数==源件数；关键字段：克隆仓库 HEAD==bundle 记录的 sha；`git fsck` 零错 | bundle 523 MB 克隆≈1-3 分钟；两目录件数少，秒级 |
| L3 | 人工，季度，禁自动 | 整仓恢复到备用盘并跑 `pytest --collect-only` 计数 | — | >2 小时；**与 L2 同形**（同一条恢复链的放大版），故只作在场演练，不排自动 |

### 3.2 SQLite 腿

现状病：`DatabaseManager.verify_backup()`（T-DB-005，`database_manager.py:832`）已实现 `PRAGMA integrity_check`＋表名遍历＋逐表行数，**但全仓零调用者**＝又一装饰护栏。方案＝让它有第一位消费者（演练腿），不新写第二把尺（O-3）。
⚠ 一个必须显形的坑：`verify_backup()` 内部执行 `PRAGMA journal_mode = WAL`＝**它会写被验证的库**。演练绝不允许改备份件 ⇒ 演练一律对**副本**跑（复制到隔离区后验），并在施工时给 `verify_backup()` 加一个 `read_only=True` 形参（跳过 journal_mode 与 integrity 之外的写副作用）。这条属"改判据面"吗？不——它改的是**副作用**，不改正向断言；仍列施工项供复核。

| 档 | 频率 | 抽查面 | 三对判据 | 成本预估 |
|----|------|--------|---------|---------|
| L0 | 日频 | 备份副本文件头 16 字节==`SQLite format 3\0` ∧ 尺寸 ≥ 源库 90%（防零字节/破损件被接受——PG 腿 `_find_latest_dump` 只验存在性，同族病已显形在册） | 关键字段：魔数；行数：size 比值读数；指纹：副本 sha256 入账（不判等，供追溯） | 秒级 |
| L1 | 日频 | 只读打开副本：`integrity_check`／表名集合⊇**从 `sqlite_schema.py` DDL 派生的必需表集**（禁手写清单，§9.5 静态清单禁手工）／逐表行数 vs 源库同窗读数 | 指纹：integrity_check=='ok'；行数：drill≤live 逐表成立 ∧ 缺口比 ≤ 阈值；关键字段：必需表集合全等（缺任一即红） | governance.db 241 MiB，USB 上 integrity_check ≈1-3 分钟 |
| L2 | 周频 | 副本进隔离区，用**生产读路径**（`DatabaseService.get_governance_connection`，禁裸 `sqlite3.connect`）跑 3 条真业务查询：`fle_alerts` 计数、`rule_catalog` 行数、`module_translation_registry` 对应表列集合 | 同三对＋"读得通生产代码"这一层证据 | 分钟级 |

### 3.3 ClickHouse 腿（Owner 定的分级：结构还原＋表指纹比对 vs 全量）

结构基线**已在册**：每轮备份产 `report.databases.clickhouse.manifest`（226 条 `database/name/total_rows`，取 `system.tables` 非 View）⇒ 演练不必另造 schema 快照，缺的只是"还原侧的配对读数"。

| 档 | 频率 | 抽查面 | 三对判据 | 成本实测/预估 |
|----|------|--------|---------|--------------|
| L0 | 日频 | VM 内经既有单口 `ch_vm_ssh.py --stat-backup {market,inc}.zip --json` 取 size/mtime，与 `backup_state.json` 的 `last_ch_backup_{bytes,full_bytes}` 逐位对拍；＋INV-11 的 `system.backup_log` BACKUP_CREATED 核验（已有单口 `query_backup_log_created`，不重写） | 关键字段：两条链 file/bytes 全等；行数：size_ratio 读数；指纹：backup_log 事件 id | 秒级，零还原，零停机 |
| L1 | 月频（结构面） | 一次性库 `drill_ch_<ts>`：把备份轮 manifest 里的**表名集合**与活库 `system.tables` 现值对拍 ∧ 逐表 `create_table_query` 规范化文本的聚合 sha256；View 表单独列"依赖齐备性"读数（View 不可 RESTORE，诚实标注不冒充） | 指纹：DDL 聚合 sha256 全等；行数：表数==226（口径注明"非 View"，禁跨 family 混分母）∧ 引擎计数（ReplacingMergeTree 228／MergeTree 15／View 4 现值）；关键字段：逐表 total_rows 方向性 drill≤live | 只读元数据，秒-分钟级，零数据搬运 |
| L2 | 周频（分区级真还原，**本方案的核心新增证据**） | 按 `system.parts` 体量选**分区级** RESTORE：`tick_data`（66.49 GiB 全表）取 1 日分区、`kline_1min`（34.94 GiB）取 1 日、`technical_indicator`（195.16 GiB）取 1 月、`news_data`（12.22 GiB）取 1 日、`adj_factor`（21,055,072 行）全表、`c0_meta` 任一维度表——**预算硬闸 ≤8 GiB**；一次性库建成后 `DROP ... SYNC`＋`DROP DATABASE`，finally 双通道清理（照抄 PG 演练骨架） | 指纹：每表有界样本 cityHash64 聚合（只比两侧共有主键，PG C3 同构）；行数：`count() FINAL`（**ReplacingMergeTree 228 张，不 FINAL 的行数不可比**，在册坑）；关键字段：`min/max` 事件日期 ∧ 抽样列校验和 | 8 GiB 量级 RESTORE 从 sdc（G: vhdx）读，预估 10-30 分钟；**须实测首演才给准数** |
| L3 | 季度，人工，须窗 | 库级全量 RESTORE（444 GiB 备份盘） | — | 未实测（从未做过）⇒ 本方案**不给它自动触发**，只登记为人工档；首演要另立时间预算 |

风险与硬前置（写进判据，不写在散文里）：
1. **容量闸**：演练前读 `system.disks` 的 `default` 盘 free（实测 190.77 GiB）∧ 宿主 `D:` free（实测 60.2 GiB，data.vhdx 动态增长会吃它）；任一 < 预算×2 ⇒ 拒跑并报警（宁可不跑不跑爆——在册事故：压缩中途没空间＝虚拟盘半完成威胁数据库本体）。
2. **与备份腿互斥**：RESTORE 读的是 CH 备份盘，与 `backup.ps1` 的 CH 增量腿抢同一设备；演练点火须走既有互斥闸（`ch_backup_config.yaml:63` 的 `vm_name` 真源＋`backup_reconciler.ch_guest_vm_running`），且避开 06:00 窗。
3. **软失败**：CH 查询出错会返空串而不抛（在册 `ch-query-fails-soft-trap`）⇒ 演练读侧一律"rc＋空值＋非空断言"三检，采不到数＝红，禁当"无数据"。

### 3.4 VM 腿（**前提被实测证伪，必须先报窗**）

令卡写的是"内容＝系统盘+配置面（不含数据盘）"。实测两面证据：
- 宿主侧：`Get-VHD boot.vhdx` ⇒ `FileSize=4,194,304 B`／虚拟 80 GiB／Dynamic＝**一张没装过东西的空盘**；`data.vhdx` 604,755,722,240 B。
- 客户机侧：`lsblk` ⇒ `sda`(=boot.vhdx) 80 G **无分区无文件系统**；`sdb`(=data.vhdx) 600 G 分 `sdb1` 1 G vfat `/boot/efi`＋`sdb2` 598.9 G ext4 **挂在 `/`**；`clickhouse-client` 的 `system.disks.default`＝`/var/lib/clickhouse/` 就在 `sdb2` 上。

⇒ **这台 VM 没有"独立系统盘"这个物理对象**：操作系统＋CH 程序＋CH 数据同在 `data.vhdx` 的同一个分区里。"不含数据盘的盘级月镜像"在物理上不存在；真要盘级就必然含 563 GiB 数据。照原令去拍，只会拍回一张 4 MiB 空盘——那是最漂亮的一种假绿。

可达形态（本册据此设计，落法见 P1-B 施工段）：

| 型 | 内容 | 体量 | 成本 | 恢复语义 |
|----|------|------|------|---------|
| **A（本班落地）** | VM 定义面：vmcx＋vmgs 原字节 ∧ `Get-VM/Get-VMHardDiskDrive/Get-VMNetworkAdapter/Get-VMFirmware/Get-VMProcessor/Get-VMMemory/Get-VMSecurity/Get-VMIntegrationService` 全字段 JSON 快照 ∧ `Get-VHD` 三盘台账；guest 配置面：`/etc`（实测 7.0 MB：`config.xml`/`users.xml`/`config.d`/`users.d` 及 `.bak`/`.old` 变体）＋`/etc/fstab`＋systemd 单元＋CH 版本串（26.6.1.1193）＋dpkg 包清单（4 个） | MB 级 | 零停机、秒-分级 | 定义能重建、配置能原样贴回；OS/CH 程序仍需重装（＝在册"重建式"那句） |
| **B（要 Owner 点头，O-4）** | 在型 A 之上加 guest 内 **OS+程序文件级镜像**：tar 排除 `/var/lib/clickhouse` 与 `/mnt/*`（实测 OS 面 `du -x` ≈13 GiB，压缩预估 5-8 GiB） | 每月 5-8 GiB，≥2 份 ⇒ G: 月增 ≤16 GiB（G 现余 2,471.4 GiB） | 零停机，预估 10-30 分钟 | 重装即回当日 OS＋CH 程序，不必 apt 拉包（外网不可用时也回得来） |
| **C（令卡已排除）** | 盘级 `data.vhdx` 全镜像 | 563 GiB/份，≥2 份＝1.13 TiB | 需停机或 Save-VM 态复制，历史实测 30-90 分钟 | 整机快恢；**与"不含数据盘"的令面冲突，故本册不自行开** |

回滚验证的"双证"定义（型 A，本班即做）：
- **证 1 内容级**：镜像内逐件 sha256 ↔ 活体同刻双读对拍（不是"文件在不在"，是"字节等不等"）；CH 版本串/dpkg 清单/`fstab` UUID 三项逐字段核。
- **证 2 可回滚级**：用镜像里的 VM 定义在 Hyper-V 里 `New-VM` 一台**隔离临时机**（不挂任何生产 vhdx、不连外部交换机），读回 vCPU=12／内存／固件 SecureBoot=Off／启动序／SCSI 控制器位置三附件路径，逐项与 spec 对拍，然后 `Remove-VM` 删除。全程零触碰生产 VM 与三张 vhdx。
（型 C 的开机级回滚验证不属本袋，因为它要先解决 C 档是否开。）

## 4. 自动触发腿怎么落（与"禁 cron"红线的相容论证）

红线原文真源＝`docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml:119-133`（§3 事件驱动全自动），逐字是"**时间触发(cron/Timer/sleep-loop/periodic/进程内调度器)等于要人指令触发，没达成自动，禁止**"，同段 L132 给出例外口径："CI schedule 属**进程外**托管层级、非进程内 Timer、不占运行时 ⇒ 允许"。
适用面也写死在规范里：L127 的归类表明该禁只约束 **C 类永久系统**（reconciler/scheduler/watchdog/boot_hooks），"跑完即退"的一次性脚本不是常驻系统。
词表侧：`_registry/vocabularies/startup_vocabulary.yaml:23-27` v1.1.0（2026-09-05 总管裁定）增设 **`scheduled_task`** 值（:64 起为正式枚举），边界在 :27"仅限守护类 one-shot（执行完即退出）；进程内 Timer/轮询守护仍禁"；同文件 :20-22 明确被禁的是 `scheduled`（进程内定时）。
既有先例：`scripts/backup/restore_drill.py:17` 就是这条红线的合法豁免写法——`# noqa: m11-perm-manual-legitimate  M11豁免: … 由 ZEPHYR-RESTORE-DRILL schtasks 月度事件触发，人工直跑为兜底形态，非常驻`，执法面是 `src/zephyr/gov_enforcement/commit_gates/manual_only_permanent_gate.py` 与同件 PERM-TRIGGER。

⇒ **结论（可写进施工令的说法）**：备份演练天然日历型，与红线的相容方式＝**OS 托管计划任务 one-shot**（`[STARTUP] scheduled_task`，执行体跑完即退，禁任何进程内 Timer/常驻/`Start-Sleep` 轮询），不是新发明，是沿用词表 v1.1.0 与月度演练已裁先例。红线要防的是"进程里养一个定时器"，不是"日历到点跑一个批"。

注册纪律（一支新任务必须齐的六面，缺一面就是下一班的雷）：
1. 注册脚本落 `scripts/tasks/register/register_*.ps1`——`scripts/governance/scheduled_task_reconcile.py:8` 把"期望清单唯一真源"定在 register 脚本的字面声明，**没有注册脚本的任务对账器根本看不见**（现状实例：`ZEPHYR-RESTORE-DRILL` 全库 grep 只在脚本自身命中，无 ps1＝在册缺口，本方案建议顺带补一支纯登记面脚本，触发器与执行体一字不改）。
2. `config/resource_profile_registry.yaml` 种子同步（机生册，改 `scripts/governance/generators/generate_resource_profile_registry.py` 的种子再重生成，禁手改）。
3. `data/runtime/process_reaper_keep.txt` 登记 cmdline 子串（RULE-GUARDIAN，否则 reaper 误杀在飞的演练）。
4. 脚本头 `[TTL] permanent`＋`[STARTUP] scheduled_task`＋`[CONSUMERS]` 声明；新建 .py 走 `add_module_translation.py`（TRANSLATION-COVERAGE gate 拦）。
5. 错峰表（实测窗）：主备份 06:00 计划任务＋夜间多道点火器；CH 六跑完后至次日 16:3x 调度器静默；建议 **L0 每轮收尾随链走／L1 代码＋SQLite 日频 09:30／L2 代码＋SQLite＋CH 分区还原 周日 10:30／CH 结构面＋VM 配置面 每月 5 日 10:00**，全部避开 05:30-08:00 与 16:00-19:00。
6. **注册/变更计划任务＝Owner 门位**（在册口径 ruling_registry 明写"计划任务注册/变更类＝Owner 门位"；另有 P2 裁定门＋P1 资源画像双前置的既有裁定），⇒ 本册 §0 O-1 就是那一点头。

## 5. 失败告警面（不新建通道）

在册边界：裁定 **RULING 255**（`ruling_registry.yaml:1162-1172`）通知唯一出口＝前端 promotion 页，飞书/SMTP 通道彻底删除；同册 F74 条（:3369-3371）"通知通道＝晨报承接，不复活 SMTP/飞书、不加推送组件"。⇒ 演练失败**不开新通道**，走三条既有出口：

| 出口 | 单口 | 写什么 | 谁读 |
|------|------|--------|------|
| OpsAlertFeed | `src/zephyr/infrastructure/system_telemetry/alerts/ops_alert_feed.py`（`publish`，落 `.runtime/ops_notifications/notifications.jsonl`，safe_write_text CAS） | 每腿每次演练的红/缺跑事件，带 `leg/tier/verdict/report_path/stale_days` | 仪表盘 `/api/ops-notifications`＋promotion 页（既有消费面） |
| 报告件 | `logs/dr_drill_<leg>_<ts>.json`（沿用 PG 演练命名面与八键契约） | 三对判据逐条读数＋采集面分母（缺分母＝尺无牙，当场红） | 人工阅＋台账聚合器 |
| 计划任务原生 | `LastTaskResult` | 退出码（`0 if pass else 1`） | schtasks／巡检现读 |

**最要紧的一条不是"红了报"，是"没跑要报"**：在册教训——`backup_daily_trigger.ps1` 当年只查 `last_ch_backup_status` 不查 `last_backup_status`，导致主链失败 12 天无人知；`dr_resilience_metrics.py` 的 `pass_rate()` 历史为空时返 **1.0**、`days_since_last_drill()` 返 `inf`＝降级态与"未触发"同形。⇒ 台账每腿必带 `last_attempt_at`／`last_pass_at`／`consecutive_failures`，新鲜度闸＝超过 2× 频率 WARN、超过 4× CRITICAL，**且"从没跑过"必须显式 CRITICAL，不得由 inf 冒充"很好"**。

## 6. 台账与装饰件内收（§4 全资产净零）

- 台账：`data/databases/dr_drill_ledger.json`（与 `backup_state.json` 同区同性质＝运行数据，非规则数据；按 RULE-SSOT 架构/运行数据直写不建表，不新建 DB 表 ⇒ 零迁移面）。键：每腿每档一行 `{leg, tier, schedule, last_attempt_at, last_pass_at, consecutive_failures, last_report}`。
- **在册 PG 口径的处置**：`restore_drill.py` 文档串明写"Owner 裁定＝drill 结果不入账，人工阅"。本方案不改它的**裁决与覆盖面**，但四腿新台账需要一个统一读面；两条口径如何在 PG 那条并轨（入账 or 保持人工阅）＝**呈批项 O-5**，本班不自裁。
- 装饰件转真件（这就是净零的"合并/替代"面）：
  | 对象 | 现状 | 方案处置 |
  |------|------|---------|
  | `DatabaseManager.verify_backup()` | 全仓零调用者 | SQLite L1 的第一位真消费者（替代"另写一把 SQLite 尺"） |
  | `src/zephyr/feedback_loop/diagnosers/health/dr_resilience_metrics.py` | R231-R234 四指标**零生产者**（除自家测试），空历史即返满分 | 台账成为其唯一喂入；若 Owner 不接（O-5）则按"零触发零消费→退役"报退役申请，不留在岗装绿 |
  | `scripts/ops/r6_restore_via_vm.py`／`r6_restore_check.py` | 一次性手工件（建临时库→RESTORE TABLE AS→行数＋前 5 行→DROP） | CH L1/L2 的实现基座，**收编不新建** |
  | 2026-09-15 人工演练的 sha256 抽检逻辑 | **未入库**（只在 `logs/dr_drill_20260915.json` 留结论） | 代码腿 L1 的实现基座；那份人工件退役为台账历史行＋指针 |
  | `ZEPHYR-RESTORE-DRILL` 无注册脚本 | 对账器看不见的手工件 | 补纯登记面脚本（触发器/执行体零改动） |
  | `G:\backup\git_bundles\git_bundles\`（0914/0915 两支 853 MB） | 嵌套双真源嫌疑 | 代码腿 L0 的清单自洽项显形它；物理删除属 Owner 门位，本班不删 |
  | 新建文件数 | — | 本册 1 份（方案袋）＋施工波次预计 4 支执行体＋4 支注册脚本；每支均声明其替代/合并的旧条目，无声明即不建 |

## 7. 施工波次（Owner 批复后才动，逐波可回退）

| 波 | 内容 | 面 | 预估 | 回退 |
|----|------|----|------|------|
| 1 | 裁决外形（沿用八键契约）＋台账单口＋代码腿 L0/L1＋SQLite L0/L1（含 `verify_backup(read_only=True)` 形参） | 只读＋隔离区写 | 半天 | 每波独立 commit，`git revert` 即净 |
| 2 | CH L0/L1（结构对拍，零数据搬运） | 只读元数据 | 半天 | 同上 |
| 3 | VM 型 A 通道（＝P1-B 本班已落地面）＋回滚验证证 1/证 2 | Hyper-V 只读＋临时 VM | 半天 | 临时 VM `Remove-VM`，镜像目录删除属本班自造物 |
| 4 | CH L2 分区级真还原（含容量硬闸与 finally 双通道清理）＋代码/SQLite L2 | **会在 VM 内建一次性库** | 1 天（含首演取实测时长） | `DROP DATABASE drill_ch_<ts>`；不动备份盘 |
| 5 | 4 支计划任务注册（O-1 批后）＋资源画像种子＋reaper keep＋告警接线＋每腿"必然红"变异用例（证尺有牙） | 注册面 | 半天 | `schtasks /delete` 逐一注销（本班留逐字命令） |

红线：任何一波都不改既有判据的阈值/口径；新尺一律先"能红"再"能绿"（在册铁律：判绿的尺须先证明能红），变异用例与正对照件同批落地。

## 8. 本方案的自证边界（不许被引用成"DR 已验证"）

1. 自包含测试证的是**契约与裁决逻辑**，不是"这份备份真能恢复回来"——能恢复只由真演练证，月度真跑不得因测试绿而撤（件头在册）。
2. 本册所有成本列的"预估"字样＝未实测项，施工波次 4 首演后必须回填实测数字，回填前不得当战果引用。
3. L3/型 C 档**没有**任何实测时长（从未做过），本册因此不排自动触发；若 Owner 要开，须另立带时间预算的人工演练袋。
4. 代码腿在并行会话脏面期的"剔除件数"是判据的一部分：**剔除数过大＝尺失效**，不当作通过。

## 9. P1-A2（顺手修 PG 演练打分器中文乱码）——本班按令另袋，摘要先行

10-01 那轮判红的病因，今日已用**真实字节回放**复现并定位（复现脚本 `D:/ZephyrAlpha/.runtime/tmp/bakdr_20261013/repro_c4_locale3.py`，创建/删除两个 scratch 库，未触 `depgraph` 与 `depgraph_drill`）：
- 病形：`pg_restore` 在**没有 `LC_ALL/LANG/LANGUAGE` 环境变量的进程环境**里，会把自己那两句框架 token 本地化**并按系统 ANSI 代码页（本机 ACP=936）写进 stderr**，而服务端错误正文走 UTF-8（本机 `PYTHONUTF8=1`）。实测原始字节：
  `b'pg_restore: \xb4\xed\xce\xf3: could not execute query: \xe9\x94\x99\xe8\xaf\xaf:  \xe5\x85\xb3\xe7\xb3\xbb "t_repro2" \xe5\xb7\xb2\xe7\xbb\x8f\xe5\xad\x98\xe5\x9c\xa8'`
  ＝ `错误:` 是 GBK 字节、服务端消息是 UTF-8 字节，**一条流两种编码**。结果 `_RE_RESTORE_ERROR_LINE`/`_RE_RESTORE_COMMAND_LINE` 双双 0 命中 ⇒ `error_count=0` ⇒ `unknown` ⇒ `pass=False`，而同轮 C1/C2/C3 全绿。与 10-01 报告 `pg_restore_error_unclassified` 逐字同形。
- 正对照（同脚本同数据，钉 `LC_ALL=C LANG=C LANGUAGE=C`）：`pg_restore: error: … 错误:  关系 … 已经存在 / Command was: CREATE TABLE …`，两把正则各 **2/2 命中**。
- 修法方向（**改喂给闸的输入指向，不改闸**）：在 `restore_drill.py:652` 那一个 env 构造点把三个 locale 变量钉成 `C`，并对喂给 C4 的子进程调用显式 `encoding="utf-8"`（防未来 `PYTHONUTF8` 被撤后服务端 UTF-8 正文又被 cp936 解码——那会让良性规则里的中文分支一起失效）。**不扩良性错误白名单、不动 `_C4_PASSING_VERDICTS`、不动退出码语义**；乱码流照旧判红（fail-visible 不弱化），只是从此不该再产生乱码流。
- 待 Owner 复核的两条自问：①10-07 的 IN1-32b（显式 `DROP SCHEMA public`＋`--no-privileges`）已把当年那三条良性错误**从源头消掉**（10-09 五连跑 rc=0/clean/passed 为证），所以"11-01 会不会又红"的诚实回答是**大概率不会因同一因红**；本修法买的是"下一种良性错误出现时不再假红"，属保险，不是救火。②10-01 那次为何拿到 GBK 流＝计划任务环境的 locale 变量面与交互终端不同；本班已按计划任务原环境点火一次真跑取证（`Start-ScheduledTask ZEPHYR-RESTORE-DRILL`，23:33 起跑），读数写进班账，不在此预支结论。

## 10. 本册取证清单（复核命令＋期望值）

```
# (1) VM 无独立系统盘（双面）
powershell -NoProfile -Command "Get-VHD -Path D:\HyperV\VMs\zephyr-ch\boot.vhdx | Select FileSize,Size,VHDType"
#   期望 FileSize=4194304  Size=85899345920  VhdType=Dynamic（输出列名是 VhdType）
python scripts/backup/ch_vm_ssh.py --cmd 'lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT'
#   期望 sda 80G 无 FSTYPE 无挂载点；sdb2 598.9G ext4 挂 /

# (2) CH 库面分母
python scripts/backup/ch_vm_ssh.py --cmd "clickhouse-client -q \"SELECT database,count() FROM system.tables WHERE database NOT IN ('system','INFORMATION_SCHEMA','information_schema') GROUP BY database\""
#   期望 c1_market 196 / c3_fundamental 34 / c1_backtest 16 / c0_meta 1

# (3) 结构基线已在册（不必另造）
python -c "import json;d=json.load(open('logs/backup_report_20261013_003608.json',encoding='utf-8',errors='replace'));m=d['databases']['clickhouse']['manifest'];print(len(m),m[0][:80])"
#   期望 226 与首条 {"database":"c1_market","name":"a50_futures_daily","total_rows":2625}

# (4) verify_backup 是装饰件
grep -rn "verify_backup" src/ scripts/ tests/ | grep -v "def verify_backup"
#   期望 仅 2 处注释/日志命中，零调用者

# (5) 备份链不记 HEAD（代码腿对拍基线缺口）
grep -n "rev-parse" scripts/backup/backup.ps1
#   期望 0 命中

# (6) 乱码复现（建删两个 scratch 库，不触生产库）
python D:/ZephyrAlpha/.runtime/tmp/bakdr_20261013/repro_c4_locale3.py
#   期望 "no LC_*" 行 match errline(utf8)=0；"LC_ALL=C…" 行 match errline=utf8 2／commandline 2
```

署名：adjudicator=st-bakdr-20261013（备份线夜班总包；本册＝P1-A 方案袋，零施工；§9 修法与 P1-B/P2 各自成袋）。
