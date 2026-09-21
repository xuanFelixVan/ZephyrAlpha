---
ttl: task_bound
---

# 01 挖矿发现 — 备份/冷储自动化方案底料

> 定位：00_master_plan.md 的事实底座。本地挖矿（只读）+ 外部机构实践对照。
> 取数时间：2026-09-20 02:00-03:00（本地 grep/读文件现取，取数命令结果均现场核实；盘位与库内体量引用 2026-09-19 Owner 实测，未重测）。

## 1. 本地挖矿：现有能力 vs 目标能力缺口表

| # | 能力域 | 现有能力（真源位置） | 状态 | 目标能力 | 缺口 |
|---|--------|---------------------|------|---------|------|
| 1 | 数据身份证 | 契约 10 层保留体系：L1 tick≥2 年/L2 分钟≥5 年/L3 日K≥10 年/L4 资金面≥5 年/L6 新闻≥10 年；L5/L7/L9/L10 及 <1GiB 小表永不归档（INV-RET-005）；§2A 派生表滑窗 1min 3 月/5min 1 年/15min 3 年/30min 5 年/60·120min 跟源（`docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml` v1.2.0，PS-CTR-003） | 契约层完整 | 入库即领身份证，机读可查、reconciler 可消费 | 身份证载体已存在但退化：`docs/03_modules/_cross_layer/database/business_data_categories.yaml`（裁定 #ARCH-CH-024 表名/品类唯一真源）114 条品类全有 `lifecycle` 字段，实际取值 206 条 permanent / 2 条 hot_90d / 1 条 hot_1d（2026-09-20 grep 统计），与契约 10 层完全未对齐；`src/zephyr/data/table_registry.py` 只消费 category_id→table 映射，不读 lifecycle |
| 2 | 滚动归档 | `scripts/ch/archiver.py`（875 行）三阶段 export→verify→drop 完整：verify 含行数比对（>100 万行 ±1 容差）+ 随机抽样 100 行字段值多重集比对 + ReplacingMergeTree FINAL 注入防重复幻影行；manifest append-only 含 rows/checksum_md5/compress_ratio；restore 带 checksum 守卫防冷库盘静默腐坏；dry-run、断点续传（跳过已 dropped、重跑 verify 失败）、export-only 纯备份模式齐备 | 手动 CLI（INV-RET-002），2026-08-10 首轮手动归档 1865 分区零事故 | 过线分区自动滚动，无人值守 | 无触发器（见 #8 纸面模块）；无批限量/滞回/熔断/影子模式；ARCHIVE_ROOT 硬编码 E 盘（archiver.py:69），stats() 的 disk_usage 也写死 E:\\（archiver.py:734） |
| 3 | 备份链 | `scripts/backup/`：backup.ps1 六阶段（pre-check/db dump+config sync/code vault/git bundle/offrepo mirror/report）+ working_vault 版本化快照 14 天轮转 + 硬链接去重 + free_floor 60G 空间保险（backup_config.yaml v2.1，2026-09-14 /MIR 误删事故后改版）+ git bundle ≥7 天重建留 2 份（F:\working_vault\git_bundles）+ offrepo_backup /MIR 镜像四目标（trae_memory/qmt_bridge/stash_archive/cold_archive）；触发双保险：计划任务 ZephyrAlpha-DailyBackup 每日 06:00 兜底（backup_daily_trigger.ps1，注释明说"post-commit 只在有 commit 的日子触发，每日任务是保底"）+ backup_reconciler.py post-commit 双条件（重要文件+8h 间隔，INV-08/09/10） | 运行中（production） | 3-2-1-1-0 全覆盖 | ①db_dumps /MIR 覆盖式无版本（backup.ps1:590 注释 "unchanged /MIR, overwrite by design"）——dump 只有一份，dump 时刻坏了无前份可退；②F→G 冷储镜像不存在；③offsite 异地副本不存在；④restore 演练无自动化（archiver restore 有 CLI 无季度巡检） |
| 4 | 冷储入库 | G 盘冷库 SOP（`docs/_working/altdata_line/10_g_drive_cold_storage_sop.md`）：00_manifest drawers.jsonl 先登记后建目录、10_inbox 强制隔离、20_raw/30_corpus/50_archive 归位、三红线（immutable/禁双真源/回测数据家不在冷库） | 人工 SOP（四步） | 新数据自动落箱-登记-归位-清箱 | inbox 无事件钩子；manifest 登记纯手工；90_tmp 30 天 TTL 靠每月人工清；manifest 月度对账靠人工 |
| 5 | CH 冷储仓 | E:\zephyr_cold_archive 117.6G Parquet，asset_inventory OFFREPO-COLD-ARCHIVE（critical/backup:mirror/约 117.6GB），INFRA-STORE-002 已挂册（status: connected） | connected | 迁 F 冷储主库 + G 镜像 | 引用点 7+1 处需同 commit 改（§3 发现 1）；迁移后 E 盘须按 SOP §6 保留 30 天双备份期再清 |
| 6 | 分层决策件 | `src/zephyr/data/storage_tiering.py`（CAND-DAT-006/B1-00584）：Tier HOT→WARM→COLD 单调迁移、TierPolicy、双副本 sha256 校验、RTO/RPO 分级演练（L1~L6）、UFL 追加式事实层，注入式后端设计 | 已建未接线（§3 发现 2） | —— | 声明 CONSUMERS=zephyr.data.scheduler 但 scheduler 零引用；须裁定"接线或退役"（规范预算净零铁律） |
| 7 | 容量监控 | `src/zephyr/data/ch_parts_monitor.py`：system.parts 单表 active>100 告警（阈值真源 THD-HEALTH-005 fail-closed 统读，告警 ALERT-CH-001 飞书触达），防 2026-07-09 parts 爆炸事故重演 | testing | 盘位水位+归档欠账+日志回积监控 | 无 D/E/F/G 四盘水位统一巡检；无"归档落后于增长"的欠账指标（审计触发器） |
| 8 | 自动化载体 | ReconciliationRegistry：`register(ReconcilerSpec(gate_id, trigger, reconcile, priority, file_ops))`，post-commit 事件驱动、异常降级 warn 不阻断其他 reconciler、backup_reconciler 是现成先例（MOD-INF-043） | production | 滚动归档 reconciler 的合法挂载点 | 无——纯增量，符合宪法"事件触发禁 cron/Timer/sleep-loop"红线；注意不新增 schtasks，挂既有备份成功事件链 |
| 9 | CH 系统日志 | 曾合计约 145G（text_log trace 级全量是主因），2026-09-19 Owner TRUNCATE 一次性释放 | 事后救火 | 原生 TTL 按天滚动保留 | config 无 `<ttl>`、text_log level=trace 未调；契约 INV-RET-001~003 管辖的是业务表，系统日志表属运维域不受契约保留义务约束（Altinity 实践：CH 自身不消费这些日志，可激进修剪） |

## 2. 数据资产清单（需求 5"挖干净"底账：有哪些数据、哪些表、自动化程度）

库内活跃 566.5G（2026-09-19 实测）分解与自动化覆盖：

| 块 | 体量 | 构成（表） | 已自动化 | 未自动化 |
|----|------|-----------|---------|---------|
| 合规热层 | 约 361G | tick_data 141.5G（2025-01 起 21 个月，约 6.7G/月）+ technical_indicator 窗口内 151G + 分钟线族约 66G（kline_1min~60min 及 etf/lof 分钟族）+ 日K/基本面/事件/元数据（小） | 灌入（scheduler+tasks.yaml DAG）、每日备份、parts 爆炸告警 | 身份证（lifecycle 未对齐）、滚动归档、盘位水位 |
| 契约欠账 | 24.9G | TI 窗口外 19.4G + 冷线 5.5G | 无（等清账） | 批次 3 手动清（archiver 现成） |
| 尸体表 | 35.4G | news_corrupt/pre_tz2/各 tz_bak | 无 | Owner 裁定后 export→verify→drop |
| 系统日志 | 145G（已清，从零起步） | text_log/query_log/trace_log/part_log/metric_log/processors_profile_log/asynchronous_metric_log/error_log/background_schedule_pool_log | 无（曾靠 TRUNCATE 救火） | CH 原生 config TTL 滚动 + text_log level 调整 |
| 冷储 Parquet | 117.6G | E:\zephyr_cold_archive（db/table/partition.parquet，archive_manifest.jsonl 1865+ 条） | 每日 F 镜像（offrepo） | 主库迁 F、G 直镜、季度 checksum 抽检 |
| 冷储语料 | 90,243 件 | G:\zephyr_cold\30_corpus\research_reports（F 60,245 + E 29,998 已迁，零失败） | 迁移已完成 | E 侧 29,998 件并入抽屉制统一管理 |
| 备份层 | —— | working_vault（F，14 天）+ db_dumps（F，1 份）+ CH base+inc（D→CH VM 内）+ git bundle（F，2 份）+ offrepo 镜像（F） | 前四者已自动化 | db_dumps 版本化、G 侧镜像、offsite、restore 演练 |

非库内大对象：data.vhdx 599G（D 盘，动态盘）；E:\数据下载（Owner 2026-09-14 裁定不备份，源在 E 可随时重镜像）。

## 3. 意外发现（挖出来的）

1. **"7+1 引用点"逐一核实成立，行号对准**：scripts/ch/archiver.py:69（ARCHIVE_ROOT）与 :732-735（stats 的 `shutil.disk_usage("E:\\")`）、config/asset_inventory.yaml:139（OFFREPO-COLD-ARCHIVE path）、docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml:197-211（INFRA-STORE-002 的 host/access_method 含"禁接 scheduler"字样）、同目录 registry_of_logs.yaml:805-812（LOG-OPS-001 路径+retention: permanent）、src/zephyr/frontend/dashboard/services_registry.py:118-120（cold_archive 探测器 dir+manifest）、scripts/backup/backup_config.yaml:88-89（offrepo cold_archive 源）；"+1"=data_retention_contract.yaml 内 E 盘字样（:61/:396/:401/:406）需随裁定一并改口径。另挖出第 8 处：`src/zephyr/data/config/known_data_gaps.yaml` 也引用 zephyr_cold_archive——迁移批核对清单应含它。
2. **契约声明的消费者是空头支票**：data_retention_contract.yaml 头部写"消费者：tasks.yaml（每个任务的 retention 字段从本契约查表）"，但 `src/zephyr/data/config/tasks.yaml`（3704 行）grep retention/ttl/layer 零命中——身份证在任务层从未落地（文档-实现漂移，宪法 §4.3 定义为事故级）。方案改挂品类真源，该声明随契约 v1.3.0 删除。
3. **storage_tiering.py 是纸面模块**：头部声明 CONSUMERS=zephyr.data.scheduler，但 scheduler.py 全文零引用（2026-09-20 grep 证实）；仅 `__init__.py` re-export 与 factor/offline_store.py 注释级语义引用。好消息：滚动归档不缺决策逻辑现成件；坏消息：又一个"声明-实现漂移"样本，须裁定接线或退役。
4. **offrepo_backup 仍是 /MIR**：v2.1 把代码备份改成版本化正是因为 /MIR 传播删除（2026-09-14 docs/_working 误删事故），但 offrepo 四目标至今 /MIR；对 cold_archive 这类 immutable 源风险可控，且已有 data_download 膨胀教训注释（backup_config.yaml:90-92）。冷库迁 F 后此节目标须同步改源，是现成的复核点。
5. **每日 06:00 计划任务与"禁 cron"红线并存的合法先例**：backup_daily_trigger.ps1 是 schtasks，属 Owner 已批准的备份兜底层（"有 commit 才备份"的补洞，注释含 WHY 段）；宪法禁的是永久系统 reconciler 用 cron/Timer/sleep-loop。滚动归档自动化应挂事件链（备份成功事件），不新增任何计划任务——这是方案合规性的关键先例。
6. **容量账的巧合红利**：热层稳态约 350-400G + 150G 冗余 ≈ 530-580G，恰好落在现有 data.vhdx 599G 之内——滚动归档建立后**无需扩容 vhdx**，压缩后也不会反复膨胀（增长有界）。
7. **契约内部同信息双处维护**：契约的 layers[].cold_policy 与 §5 storage_matrix 两处各自描述同一保留政策（如 news_data 在两处都写了"E盘 Parquet 手动触发"）——v1.3.0 修订时必须两处同步改，否则修了 layers 漏了 storage_matrix 又是一处文档矛盾；建议修订时给 §5 加"由 layers 生成"注记或声明 layers 为唯一真源。
8. **archiver 的 export-only 模式就是现成的"备份先行"原语**：`archiver export`（export+verify 不 DROP，manifest 记 verified/未 dropped）可直接用作滚动归档第 4 阀"第二副本"之外的预置份——方案最终选 G 镜像做第二副本（独立介质），export-only 留作演练与应急全量备份工具。

## 4. 外部实践对照表

| 议题 | 业界实践 | 对本项目的启示 |
|------|---------|---------------|
| CH 冷热分层 | 官方 TTL ... TO DISK/TO VOLUME 多盘分层（storage policy 定义 hot/cold volumes）；TTL move 由后台 merge 概率性驱动，`ALTER TABLE ... MOVE PARTITION TO DISK` 手动迁移才是确定性操作；社区已知坑：TTL 重评估把整表搬错盘（ClickHouse GitHub issue #66272）、改 TTL 后冷盘数据不自动回迁 | 契约 INV-RET-003 禁业务表 TTL 是对的——分区级确定性迁移+先验证再删（archiver 三阶段）比 merge 概率 move 更符合"数据不能坏"；CH 原生 TTL 只用于系统日志表（运维域，非契约管辖） |
| 机构 tick 保留 | kdb+ tick 标准三层：RDB 内存热层→tickerplant `.u.end` 当日 historicise 落盘→HDB 全史冷层，按日期分区跨存储介质分层（NVMe→SAN/对象→磁带）；监管惯例 MiFID II 约 5-7 年；常见节奏：热天级→温月级→约 1 年后冷→约 7 年后归档或法定删除 | 我方 L1 2 年/L2 5 年/L3 10 年分档与机构惯例同量级；kdb+"按日期分区天然就是归档单元"正是本方案以月分区为滚动粒度的依据；证监会 ≥7 年合规要求契约头部已对标 |
| lakehouse 保留 | Iceberg 默认永久留快照、需定期 expire_snapshots（官方 Maintenance 指南）；Delta VACUUM 默认 7 天保护期才物理删除；两者共同点：逻辑删除与物理删除解耦，保留窗=时间旅行深度 | archiver 的 export→verify→drop 就是同构"两阶段+宽限"设计；drop 前第二副本落 G 镜像相当于把保护期拉长为一个镜像周期，比业界默认更保守一档 |
| 备份工程 | 3-2-1 已进化为 3-2-1-1-0（Veeam 提法）：+1 份 immutable/离线副本、0 恢复错误；Opti9 引用 89% 勒索攻击先打备份——备份可达性即攻击面 | F 主库+G 兜底+git bundle 已近 3-2-1；缺"1 offline"（建议月度拔盘轮换）与"0 错误"（季度 restore 演练自动化）；research_reports 20 区 immutable 是现成的 WORM 思想先例 |
| 数据契约 | 数据契约=机器可查的保留/治理元数据（OpenMetadata DataContract 实体提案、Confluent Schema Registry 契约校验、Monte Carlo/Soda 实践），目录驱动生命周期自动化是共识方向 | "身份证"不是自创概念：契约 10 层落到 business_data_categories.yaml 的 lifecycle 字段+table_registry 消费+gate 校验，就是 metadata-driven retention 的最小实现，且复用裁定 #ARCH-CH-024 既有真源地位 |

## 5. 引用链接

- ClickHouse 官方 TTL 分层指南（Manage data with TTL，TO DISK/TO VOLUME）: https://clickhouse.com/docs/guides/developer/ttl
- ClickHouse 博客·系统表内幕（系统日志表 MergeTree 持久化）: https://clickhouse.com/blog/a-window-into-clickhouse-internals
- Altinity KB·System tables ate my disk（系统日志可激进修剪）: https://kb.altinity.com
- 系统日志 TTL 配置（config `<ttl>` 与 MODIFY TTL）: https://github.com/ClickHouse/clickhouse-docs/issues/1241
- TTL 分层搬错盘坑: https://github.com/ClickHouse/ClickHouse/issues/66272
- ChistaDATA·Storage Tiering Best Practices: https://chistadata.com
- kdb+ 架构（RDB/HDB/tickerplant）: https://code.kx.com/q/architecture
- kdb+ tick 数据存储教程: https://www.timestored.com/kdb-guides/kdb-tick-data-store
- Data Intellect·Supporting kdb+tick（historicise 机制）: https://dataintellect.com/news/supporting-kdb-tick
- Dell PowerScale·kdb+ tick architecture（跨介质分层参考架构）: https://infohub.delltechnologies.com
- Veeam·3-2-1 Backup Rule Explained（3-2-1-1-0）: https://www.veeam.com/blog/321-backup-rule.html
- Opti9·3-2-1-1-0 Backup Strategy（89% 勒索先打备份）: https://opti9tech.com
- Object First·3-2-1 for Unbreakable Protection（immutable）: https://objectfirst.com
- Datto·What Is the 3-2-1-1-0 Backup Rule: https://www.datto.com
- Apache Iceberg·Maintenance（expire_snapshots）: https://iceberg.apache.org/docs/latest/maintenance/
- Delta Lake·VACUUM（默认 7 天保护期）: https://docs.delta.io/latest/delta-utility.html
- Databricks·VACUUM 与时间旅行: https://docs.databricks.com/en/sql/language-manual/delta-vacuum.html
- Confluent·Data Contracts for Schema Registry: https://docs.confluent.io/platform/current/schema-registry/data-contracts.html
- OpenMetadata·DataContract 实体提案: https://github.com/open-metadata/OpenMetadata
- Monte Carlo·How Data Contracts Work: https://www.montecarlodata.com/blog-data-contracts/

## 6. 本地挖矿读取文件清单（可复现）

| 文件 | 挖到什么 |
|------|---------|
| docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml | 10 层保留真源、INV-RET-001~005、§2A 滑窗、§5 storage_matrix、changelog |
| scripts/ch/archiver.py | 三阶段实现、manifest/checksum/restore/dry-run/断点续传、ARCHIVE_ROOT 硬编码位置 |
| scripts/backup/backup_config.yaml（v2.1） | working_vault/db_dumps/ch_backup/offrepo 全参数、/MIR 教训注释 |
| scripts/backup/backup.ps1 | 六阶段结构、db_dumps /MIR 位置（:590）、git bundle 策略 |
| scripts/backup/backup_reconciler.py | post-commit 双条件触发、ReconcilerSpec 模式、状态持久化 |
| scripts/backup/backup_daily_trigger.ps1 | 每日 06:00 计划任务、与禁 cron 红线并存的合法先例注释 |
| docs/03_modules/_cross_layer/database/business_data_categories.yaml | lifecycle 字段存在但退化（206 permanent/2 hot_90d/1 hot_1d） |
| src/zephyr/data/table_registry.py | 只消费 category_id→table，不读 lifecycle |
| src/zephyr/data/storage_tiering.py | 纸面模块证据（声明 CONSUMERS vs scheduler 零引用） |
| src/zephyr/data/ch_parts_monitor.py | parts>100 告警链路（THD-HEALTH-005/ALERT-CH-001） |
| src/zephyr/governance/audit/reconciliation_registry.py | ReconcilerSpec 注册/执行/异常降级机制 |
| src/zephyr/data/config/tasks.yaml | retention/ttl/layer 字段零命中（空头支票证据） |
| config/asset_inventory.yaml | OFFREPO-COLD-ARCHIVE 登记（critical/mirror/117.6GB） |
| docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml | INFRA-STORE-002 全条目（含"禁接 scheduler"字样） |
| docs/01_policies_and_standards/_registry/catalogs/registry_of_logs.yaml | LOG-OPS-001（:805-812，retention: permanent） |
| docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | 归档相关裁定检索（无 INV-RET-002 专项条目，契约本体即裁定记录） |
| src/zephyr/frontend/dashboard/services_registry.py | cold_archive 探测器（:118-120） |
| docs/_working/altdata_line/10_g_drive_cold_storage_sop.md | 抽屉制/四步入库/三红线/容量巡检 |
| src/zephyr/data/config/known_data_gaps.yaml | 第 8 处 zephyr_cold_archive 引用（新发现） |
| zephyr_cold_archive 全仓引用 grep（py/yaml/ps1） | 7+1 引用点行号逐一核实 |
