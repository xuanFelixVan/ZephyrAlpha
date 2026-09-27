---
ttl: task_bound
completes_when: 本图封矿（§6 四判据齐）且 fig12 全部作业簿交付后，本件转为施工基准与归档参考
title: 图12 数据供给链图·环节总骨架（外部源→采集→入库→衍生→冷备→对账修复）
owner: st-mapbuild-20260924
---

# 图12 数据供给链图 · 00 环节总骨架

> **一句话域定义**：数据从外部源经采集落到 ClickHouse、经衍生加工到可被交易/因子消费、再经冷备归档与对账修复回到"新鲜且达标"的**全生命周期有多少运营环节**——回答"资产怎么被产出来、被保住、被修回去"，不是"什么时点跑什么"（那是图13）。
> **收敛基准**：本件是图12 唯一收敛基准；`D12-NN` 编号一经定稿即契约，作业簿标题必须引用（`01_<环节名>.md`，见 §5）。
> **状态纪律**（skeleton_mining_policy §5；批次4 落地细化口径，只加不改松）：✅ = **有活跃管线在产数**，三腿齐 =（a）**生产者在册**（tasks.yaml task_id / schedule.yaml 槽 / scheduler 特殊槽 / 进程内写手，四源任一，见 §0 门④★）**+**（b）**触发档期或调用见证留痕**（task_runs 打卡优先，其次 task_progress 台账、档期告警案卷，parts 末写只作代理旁腿）**+**（c）**实查产出新鲜度达标**（业务表 `max(date)`＋近窗计数，UTC 折北京比对）。三缺一只准 🔨/⬜；多腿行任一整腿不 ✅ 则行级不 ✅（状态格写 `分面`）。接口存在/存量存在 ≠ ✅。
> **本会话实查边界（诚实声明，批次4 落地更正）**：task_runs / 案卷 / 外置盘 / schtasks 在主机侧均已实见（§6 🌑 撤二缩一，非"本 worktree 无日志"口径）。CH 读取一律走 `zephyr.infrastructure.database_service.get_clickhouse_conn(role="reader")`（**失败即抛**版通道；`ch_reader/ch_writer.query` 的"失败→空串"返回值不得作为任何证据）；判新鲜度主口径 = **业务表 `max(date)` + 近窗计数**，`system.tables/parts/columns` 枚举面**不可依赖**（09-25 03:55 实测一张坏表可打死全部 system 面，见 §4 批次4），parts 末写只作可选旁腿且失败须记 `probe_failed` 判红。
> **数字一律实测**（§7 命令可复跑）；普查先验（272 任务/27 槽/4 池/7 子命令/15源/76集/75作业）**已漂**，逐条给实测校正值（§4 批次志）。

---

## §0 域定义与四道门实证（裁定#409 一域一图四道门）

### 门① 触发与终点（边界闭合）
- **触发（多源并存，非单一）**：
  - **cron 档期**：`src/zephyr/data/config/schedule.yaml` 实测 **29 个时段槽位**（逐槽 §7-A 可列）。
  - **事件驱动**：盘中 tick/竞价流 `tick_subscriber`→`wal_writer`（`src/zephyr/data/scheduler.py` 无对应 cron，属流式常驻）；`eod_reconciliation` 明确注明"盘中持仓对账走 position 事件入口 R-015"（`schedule.yaml:207`）。
  - **系统级触发（非 APScheduler）**：灾备 `backup.ps1`「daily Task Scheduler (6AM) + post-commit reconciler (8h)」（`scripts/backup/backup.ps1` 头部 Triggers 段）。
  - **手动 CLI**：`python -m zephyr.data {run,rerun-failed,start,speed-test}`（8 子命令，见门④）+ `scripts/ch/archiver.py`（手动归档，INV-RET-002）。
- **终点（批次4 落地改写，WB12-15 P0）**：
  - **可证终点 = 双实锚**：① **归档清单** `archive_manifest.jsonl`（append-only，`scripts/ch/archiver.py:73 MANIFEST_PATH`，由 D12-10b 事件触发器产）；② **任务级对账案卷** `data/failures/<yyyymmdd>_integrity_check_task_reconcile_*.json`（应跑/成功/漏跑/失败四计数，由 D12-20 产）。二者均可指认落盘件与末次时刻 → 终点面可证。
  - **不可达终点（禁冒充）**：「对账 PASS」——`src/zephyr/trading/recon_runner.py:392 run_daily_reconciliation()`（L1 交易级→L2 持仓级→L3 PnL diff→归因三分类→差异落库+告警）设计正确但**未接线三重实证**（15:40 槽无分派分支＋零生产调用方＋`reconciliation_differences` 0 行，本车道 09-25 复跑仍 0 行），故接线前它**不是可达终点**，在图本体以 `red_reason: terminal` 的 gap 节点（DSC-GAP-TERMINUS）显性化，禁标 built、禁以"终点已闭合"散文掩盖。
- **判定**：触发面（cron+事件+系统调度+CLI）可指认真源行；终点面按上条**分可证/不可达两格**——可证面（归档清单+对账案卷）指认到落盘件，不可达面指认到 gap 节点 → 边界闭合（闭合≠全绿：缺口以 gap 节点入图）。

### 门② 跨模块交接（≥2 个 owning 模块）
链路上至少有 5 个不同归属模块在交接：
- `zephyr.data`（采集/入库/衍生/巡检/回补/哨兵，`src/zephyr/data/` 约 90 文件）
- `zephyr.infrastructure.database_service`（PG/SQLite 侧统一通道，MOD-INF-002）
- `zephyr.trading.recon_runner`（日终三账对账，跨到交易域）
- `scripts/ch/archiver.py` + `scripts/backup/backup.ps1`（MOD-INF-043 冷备域，独立于 src）
- `data_asset_registry.yaml`（REG-DATAFLOW-001 资产真源，治理域）
- 消费端外溢：衍生表交 TDM（图/因子）与工厂（图9）——交接点见 §2。
→ 非单模块自治，跨模块交接成立。

### 门③ 不被现有图/文档覆盖（三处实证）
1. **GOMAP 明确排除**：`config/governance_operations_map.yaml:16-22 out_of_scope_refs` 逐字含
   ```
   - name_zh: 数据治理
     ref: docs/01_policies_and_standards/sop/data_ops_sop/data_ops_policy.md
   ```
   GOMAP 边界声明把数据治理划到自家范围外（真源转给 data_ops_policy）→ 本域不在 GOMAP 内。
2. **dataflowgraph = 同资产不同轴（不违一域一图）**：横向 dataflowgraph 真源链 =
   `data_asset_registry.yaml → PG dataflow_* 表 → 生成文档`（`src/zephyr/governance/persistence/dataflowgraph_schema.py:38-43`）。
   其节点=Dataset/Job、边=`dataflow_edges`（`edge_type: push/pull/sync/async/event_driven`，`dataflowgraph_schema.py:181-186`）——表达的是**血缘拓扑"谁喂给谁"**（静态）。
   图12 表达的是**运营流水段+cron 档期+新鲜度+对账修复**（动态生命周期）。两轴差异实证：
   | 维度 | dataflowgraph（横） | 图12（纵） |
   |------|--------------------|------------|
   | 单位 | Dataset/Job 节点 + 边 | 环节（中类完整性检查单元） |
   | 问题 | 数据从哪流到哪（血缘） | 怎么被产出/保住/修回（生命周期） |
   | 触发语义 | 无档期概念 | cron 29 槽 + 事件 + 系统调度 |
   | 状态 | 无边级健康态 | ✅/🔨/⬜（新鲜度实查） |
   | 存储 | PG dataflow_* | tasks.yaml/schedule.yaml/CH/FS |
   → 同资产两轴，不构成覆盖，属**并行轴引用**（挂轴按 module_id 交叉，§3）。
3. **既有采集流文档 = 仅覆盖 1/5 段且未落地**：`scripts/governance/d5_architecture/generators/generate_data_acquisition_flow.py`
   头部实证 `# [INVARIANTS] 只读tasks.yaml;输出到05_dataflow_architecture/`（:8），
   产物 `data_acquisition_flow.md` 仅把 **外部源→ClickHouse 库表** 一段（采集+入库边界）映射成图（`_gen_flow_diagram` 只画 source→db 边，:590-661）。
   **两处关键实证校正普查"采集段已机生"说法**：
   - (a) 覆盖面：只覆盖**段1 采集 + 段2 入库的落库映射**，**段3 衍生/段4 冷备/段5 对账修复完全未生成**（生成器全文无 consensus/resample/archiver/integrity 逻辑）。
   - (b) 落地性：`git check-ignore docs/02_enterprise_architecture/05_dataflow_architecture/data_acquisition_flow.md` **命中=该 .md 是 gitignored 派生物，不在仓**（本 worktree 该目录下仅 `index.md`/`data_acquisition_requirements.yaml`，无此 md）。
   → 本图 = **扩为全链**，并把采集视图**吸收**为图12 子段（处置见 §3）。

### 门④ 机生真源可建性
全部段均有机器可读真源，可生成器直出、零手画：
- 采集/入库：`tasks.yaml`（271 任务）+ `schedule.yaml`（29 槽）+ `scheduler.py` 执行器池。
- 资产：`data_asset_registry.yaml`（18 源/294 集/122 作业）。
- 派生新鲜度：ClickHouse 业务表 `max(date)` + 近窗计数（走 DatabaseService 失败即抛通道；**不依赖 `system.*` 枚举面**，见 ★坑6）。
- 冷备：`scripts/ch/archiver.py` 三段 + `backup_config.yaml` 目标路径。
- 对账：`recon_runner.py` + `integrity_checker/catchup_guard/backfill_checker` + `resource_profile_registry.yaml`（ops_* 维护档期）。
→ 满足"可执行真相源→YAML"机生条件（对齐图9 先例 `generate_governance_map.py` 形态）。

**★ 节点枚举源=四源并存（批次4 硬条款，WB12-35 坐实）**：生成器/校验器的环节枚举必须同时吃 ① `tasks.yaml`（271 任务）**＋② `schedule.yaml` 槽全集（29 槽中 12 枚零任务特殊槽）**＋③ `scheduler.py` 特殊槽分派分支**＋④ 进程内在产写手（工厂/回测/组合域直写 CH，D12-19/20/21 三件的生产者全不在①②③内）。单源或双源都结构性漏段——批次1 只吃①②，批次2/3 各漏出一类（常驻探测器、任务表外派生）。

**四道门结论：全过。图12 独立成立，且明确"扩采集流文档为全链 + 与 dataflowgraph 并行挂轴 + 吸收 GOMAP out_of_scope 数据治理"。**

---

## §1 环节全集（22 个中类 = 完整性检查单元；叶层品种留作业簿）

> **批次4 落地扩行**：18→22（D12-10 拆 a/b、新立 D12-19/D12-20/D12-21），定稿表与逐条三问裁定=12 号提案卷 §1/§2，本表是其骨架正身（六列：编号/环节名/段/状态/真源映射/子环节数）。`D12-NN`（含 `10a/10b` 子契约号）一经定稿即契约。
> **✅ 判定三腿**：（a）生产者在册（tasks.yaml task_id / schedule.yaml 槽 / scheduler 特殊槽 / 进程内写手——**四源任一**，单源必结构性漏段，见 ★坑5）＋（b）触发档期或调用见证留痕 ＋（c）**实查产出新鲜度达标**（UTC 读数一律 +8h 折北京后与档期比对，WB12-30）。接口存在/存量存在 ≠ ✅。
> **状态格机读口径（供图本体 CV-DUAL 消费，禁为凑数改口径）**：状态格**首字符**即行级三态符号（✅/🔨/⬜），括注写限定与子面；多腿行若**任一整腿不 ✅**，首字符写 `分面` 并在同格逐腿标态——该行不得宣 production，图本体须以 `facets` 子结构逐腿挂证据（"行级 ✅ 仅当全腿 ✅"的机生版）。
> **两轴换算（六图终局卷 §3 硬判据）**：`verified_scope: production` 数 **必须 == 本表行级 ✅ 数**（现 **10**），多了算谎、少了算欠，校验器逐节点+计数双判。
> **本表读数时点**：批次4=CH 服务器 `2026-09-24T19:55Z`（12 号卷 L-EXP12）；本车道复跑=`2026-09-25T15:22~15:26Z`（=北京 09-25 23:22~23:26）；两时点各注明、互不覆盖。**09-25 非交易日**（`c1_market.trade_calendar` 末开盘 09-24、下一开盘 09-28），故本轮 T-0=09-24。

| 编号 | 环节名 | 段 | 状态 | 真源映射（文件:行 / task_id / 命令） | 子环节数估计 |
|------|--------|----|------|--------------------------------------|--------------|
| D12-01 | 盘后批量采集（日K/估值/资金/事件/财务/静态/校准族） | 采集 | ✅（主腿三证齐；子面限定 monthly_static 16/20 表末写不吻合档期→🔨，WB12-08；全仓唯一重复 task_id `cohort_ledger_daily` 双槽点名 WB12-49） | 196/271 任务落六档期；**执行正牌见证**=task_runs `kline_daily_incremental` started=2026-09-24T08:30:00Z=北京 16:30:00 与 cron 秒合（批次4 实查，强于 parts 代理）；本车道复跑 `c1_market.kline_daily` max(trade_date)=**09-24**、10,108,162 行（FINAL 10,108,049——WB12-21 行漂移同源，双版并报 WB12-37） | ~6 时段族 |
| D12-02 | 盘中实时/竞价采集（Tick/L2/Greeks/分钟K/880板块/集合竞价） | 采集 | ✅（叶层点名 l2_tick 0 行🔴、suspend 0 行🔴——本车道复跑双 0 仍在，根因=💰-4 L2 权限；hk/futures 停 09-16 🟡；post_auction 空转槽🔴） | 本车道复跑 `c1_market.tick_data` max(trade_date)=**09-24**、该日 27,766,260 行（批次4 记 27,761,219，持续增长）；`realtime_snapshot` 盘中段零供给待裁（11 卷 N4） | ~4 槽 |
| D12-03 | 事件驱动采集（新闻/宏观/研报/另类/加密；口径=数据源事件） | 采集 | ✅（news/alt/crypto 三族三证；🔴 research_report 停 09-18（`max(publish_date)`，本车道复跑）；🔴 macro 腿分面见右格；36 个 akshare_alt 归属移 D12-01，WB12-20） | `event_driven */3` 实 11 任务；本车道复跑 news 近 6h（`ingest_ts` 口径）**31,831** 行（批次4 记 326 行，列口径未注明，两值不互覆盖）、`alt_fx_rate_ecb` max=**09-24**、`macro_data` max(report_date)=**09-24**/56,314 行、近 30 日 41,593 行——批次4 那次「187×0 字节部件装载失败全链不可读」事故态在本轮**已解除**，按纪律仍留 `probe_failed` 判例（§4 批次4）且其检测口径缺口转 D12-19 挂账；`macro_data_incremental` 当日仍失败（源侧 SSL EOF，`data/failures/20260925_macro_data_incremental_145625.json`） | ~4 槽 |
| D12-04 | ClickHouse 写入通道（两条二级降级） | 入库 | ✅（拓扑更正版 WB12-22；回灌事件无样本🌑限定保留） | `ch_writer.py:8/:429-430/:827-829`；产出见证=D12-01/02 新鲜表（本车道复跑 kline_daily/tick_data 均 T-0） | 3 路径→两链 |
| D12-05 | 实时 WAL 落盘排空（tick 先段落盘→异步 drain 到 CH） | 入库 | ✅（02 簿 14:28 见证；与 D12-04 共 `local_fallback` 汇聚节点，WB12-26） | 本车道复跑 tick 当日 27.77M 行续产；`WalWriter` 仅 tick/depth5 两路，32 攒批任务走 buffered_writer（WB12-23） | ~2 |
| D12-06 | 幂等写与判重（ReplacingMergeTree/FINAL + 判重器） | 入库 | 🔨（判词=机制 ✅/判重器 ❌ 结构性不可用，Code 42 恒红且红被吞成 0，02 簿实测） | `check_tick_duplication.py:125/162-170/230/353`；缺陷节点 DSC-GAP-DUPGUARD | ~2 |
| D12-07 | 技术指标/多周期重采样 | 衍生 | 分面：✅指标腿／🔨重采样腿 | 指标腿三证齐：本车道复跑 `technical_indicator` max=**09-24**（362,215,198 行）+ task_runs 5×SUCCESS（max 09-24T09:32Z）；重采样腿 `kline_sector_intraday` max=**09-22 15:00+08** 本车道复跑未涨 + 该族 5 任务 ≥09-21 零打卡（09-24 案卷列漏跑） | ~2 腿 |
| D12-08 | 财务/一致预期派生 | 衍生 | 分面：🔨财务腿／🔴预期腿 | **本车道新证（财务腿下调）**：`financial_derived_build` 末次 2026-09-24T23:27:35Z(北京) **FAILED**（`'<' not supported between str and datetime.date`）、`financial_derived` max(announce_date)=09-02、09-23/24 案卷均列其为漏跑；`consensus_daily` max=**09-14** 停更持续（本车道复跑 6,797,719 行）、`consensus_daily_build` 末次 09-18 FAILED＋连日漏跑；`financial_parser.py` 已移出真源格（WB12-16） | ~2 腿 |
| D12-09 | 形态/情绪/板块状态衍生 | 衍生 | 分面：✅形态／✅情绪／🟡打板／🔴板块 | 本车道复跑 `market_pattern_event` max(anchor_trade_date)=**09-24**、`emotion_index` max=**09-24**（均 T-0）；`daban_board_event` max=09-22（🟡）；`sector_state` close_final=**09-24**／pre_open=**09-23**（非交易日下 pre_open 落后 1 日，批次4"倒挂消除"读数随日推进，倒挂缺陷未销）；`sector_preference` 全表 **2** 行（批次4 记 1 行）仍近乎空🔴 | 特殊槽两枚 + internal 任务；renko/pnf/kagi 移出（W-4，真身=series_transform 算法叶） |
| D12-10a | 手动 CLI 归档（archiver 五子命令） | 冷备 | 🔨（人工触发、无档期；批量史 08-10/11/16 三日留痕） | `archiver.py:858+` CLI；INV-RET-002 | 5 子命令 |
| D12-10b | 滚动归档事件触发器（backup-success hook） | 冷备 | ✅（三证；限定——skip 原因零留痕🌑-6、state 与 manifest 不自洽本车道复跑仍在：`rolling_archive_state.json` mtime=2026-09-21T07:37Z 而 manifest 末条 09-24T02:07:50Z、`consecutive_failures=1`） | `backup.ps1:887-906`（"Event-triggered only - NO new scheduled task"）+ `rolling_archive_reconciler.py` + 契约 :432-454（`mode: full_auto`/批限量 3/熔断 3）；本车道复跑 manifest **2,515** 行、末条 `kline_etf_30min` 09-24T02:07:50Z | ~3（五重安全阀） |
| D12-11 | 灾备双链备份（CH 增量+版本化代码快照，F→G 镜像） | 冷备 | ✅（CH 腿四源互证；🔴点名——今晨 `code_backup.status=failed`、OS 任务终态未回收、g_mirror P0 随挂） | 本车道复跑 schtasks `\ZephyrAlpha-DailyBackup` LastRun=09-25 06:00:01 **Result=267014（未终态）**；`system.backup_log` 最新 BACKUP_CREATED=2026-09-24T22:03:30Z→22:47:25Z（=北京 09-25 06:03→06:47 成功）；`logs/backup_report_20260925_060007.json` duration=32,796s 且代码快照腿 failed；批次4 读数=09-24 06:00:01/Result=0；终点口径补 backup_state/backup_log（WB12-29） | ~4 阶段 |
| D12-12 | 冷热分层/压缩决策（契约驱动，结构上不可能产数 ✅） | 冷备 | 🔨（改画法——真源换挂契约 §rolling_archive+INV-RET-003/005；storage_tiering 经裁定#383 退役在册（ruling_registry.yaml:5076）、compression_archiver 零调用方） | `data_retention_contract.yaml`；画为 D12-10b 输入节点（OBS-WF-2） | ~2 |
| D12-13 | 完整性巡检 + 新鲜度哨兵（四检核器） | 对账修复 | ✅（台账+告警双证；🔴点名——本车道 09-25 23:2x 复跑当日 23:00 档**无案卷、台账未推进**（末次仍 09-24T15:01:36Z），缺跑嫌疑入 gap） | 本车道复跑 task_progress `integrity_check_daily` last_run=2026-09-24T15:01:36Z=北京 23:01 与 23:00 cron 合、status PARTIAL rows=182；四检核器；catchup_guard 边移交 D12-14（WB12-27） | ~4 检核器 |
| D12-14 | 缺口回补三通道（＋第 4 死通道分面） | 对账修复 | 分面：🔨三活通道／⬜第 4 通道 | ③ catchup_guard 本车道复跑末次 2026-09-25T01:24:20Z=北京 09:24 PARTIAL rows=15（批次4"停 09-21"此后有推进，**但仍未落 05:30 档**⇒自动档期留痕缺）；④ `auto_backfiller` 死结论（re-export+测试，05 簿）→ 改判 ⬜/待退役（WB12-14） | ~4→3 活+1 死 |
| D12-15 | 日终三账对账（回测 vs 模拟盘） | 对账修复 | ⬜（**降级自批次1 的 🔨**——未接线三重实证，本车道复跑 `reconciliation_differences` 仍 **0 行**；§0 门① 终点已按此改写） | `recon_runner.py:392`；15:40 槽无分派分支；gap 节点 DSC-GAP-TERMINUS（`red_reason: terminal`） | ~3 层 diff |
| D12-16 | 坏数据修复与回补器族 | 对账修复 | 🔨（4 回补器 UNTRACKED 在册；c4 路径校正；💰-3 品种点名叶层） | 05 簿 §4.1 逐件表；`scripts/data/repair_kline_degraded_pull.py` + `src/zephyr/data/c4_history_repair.py` | ~8 件 |
| D12-17 | 一致预期双向互验 | 对账修复 | ✅（本车道复跑 `cross_validation_log` 1,601 行、max(check_date)=**2026-09-25**、近 3 日窗 21 行；23:30 cron 精确吻合在册；限定——check_time 恒 epoch、检查族 27→4 未定因 P-7） | `consensus_crosscheck.py` + `c1_market.cross_validation_log`（新鲜度列口径=check_date≠check_time，W-2 注记） | ~1 |
| D12-18 | CH 存储维护 OPTIMIZE / 合并（周度） | 对账修复 | 🔨（判词=已运行 OS 周任务、登记侧滞后、计数不可信） | 本车道独立复跑 schtasks `\ZephyrAlpha-CH-OptimizeMerge-Weekly` LastRun=09-20 03:30:00 Result=0 NextRun=09-27 03:30；假成功病灶 `optimize_merge.py:138-153`；`ops_*` 测量样本仍缺（05 簿在册）；判词更正 `resource_profile_registry.yaml:1098`（WB12-19） | ~1 |
| D12-19 | 破损 part 自愈探测器（CHECKSUM 隔离环） | 对账修复 | 🔨（常驻双锚实见、上线以来零触发、**现役事故不在其检测口径内**→不得 ✅，扩口径施工项挂账） | `scheduler.py:1067`（定义 `_start_corrupted_part_detector`）/:2373（随调度器实调）/:1081（每 5min 查 text_log CHECKSUM_DOESNT_MATCH）/:136（DETACH SQL）/:1096（审计路径）；本车道复跑主区 `data/local_fallback/corrupted_parts_audit.jsonl` **不存在**＝零触发复证；0 字节部件族不在其口径（批次4 红证） | ~2 |
| D12-20 | 任务级对账（档期打卡集合差四计数） | 对账修复 | ✅（案卷按日连产 09-21~24 本车道复跑四件齐；当日 23:00 档未落地随 D12-13 点名） | 09-24 件读数=应跑 183/成功 149/漏跑 19/失败 15（本车道原文复跑）；`task_runs` 本车道复跑 **188,671** 行、max(started_at)=2026-09-25T15:18Z、266 task_id、当日 1,714 runs；生产者=integrity_checker 第 4 检核（独立成行）+ `progress_store` | ~1 |
| D12-21 | 任务表外进程内派生生产（工厂/回测/组合域直写 CH） | 衍生 | 🔨（两表在产但"任务在策/档期留痕"两腿结构性缺位⇒🔨 为状态天花板；C 态 4 表+未接线写器以 gap 挂账） | 写手锚：`src/zephyr/pf_alloc/{allocation_inputs,allocation_orchestrator,crisis_gate}.py`、`src/zephyr/plan_engine/{daily_plan,daily_loop_master_switch}.py`、`src/zephyr/backtest/core/n_trial_ledger.py`、`src/zephyr/pf_alloc/core/strategy_screener_3d.py`；本车道复跑 `c1_backtest.regime_snapshot_history` 3,629 行 max=**09-24**、`strategy_screen` 1,341 行 max=**09-24**；六表在 tasks.yaml 命中数全部 **0**（复跑证实） | ~6 品种起步 |

**段计数（22）**：采集 3（01-03）｜入库 3（04-06）｜衍生 4（07-09+21）｜冷备 4（10a/10b/11/12）｜对账修复 8（13-20）。
**状态占比（行级，与图本体 machine.skeleton_status.by_symbol 同源）**：✅ **10**（01/02/03/04/05/10b/11/13/17/20）｜分面 **4**（07/08/09/14，各含 ✅ 腿与 🔨/🔴/⬜ 腿，行级不 ✅）｜🔨 **7**（06/10a/12/16/18/19/21）｜⬜ **1**（15）。
**两轴对照**：production=**10**（图本体 `verified_scope: production` 与本表 ✅ 集一一对应，校验器 CV-DUAL 逐节点+计数双判）；其余 12 行（4 分面 + 7 🔨 + 1 ⬜）为 structure。

---

## §2 五段分层与交接点（段间谁交给谁 / 失败如何降级；批次4 落地改画法四条已并入）

```
[外部源 23 家]
   │ D12-01/02/03 采集（provider 归一行为 normalized rows）
   │   失败降级①：主源失败→fallback_sources 顺序切副源（tasks.yaml 39 任务配；不可恢复错立即切、可恢复重试用尽才切）
   │   失败降级②：source_circuit_breaker 熔断（纯内存无持久＝🌑-4）；CLI `pause <source>` 名义化坐实（三处断链，WB12-25）——
   │                可用停摆开关实为 schedule:disabled / extra.disabled / data/runtime/*.disabled 三类
   ▼
[D12-04/05/06 入库：CH 写通道 —— 画成两条二级降级链 + 一个汇聚节点，禁串成"三级"]
   读/DDL 链 TCP(9000)→HTTP(8123)；批量写链 HTTP(8123)→本地 TSV 落盘（写链从不过 TCP，WB12-22）
   D12-04 与 D12-05 **共 `local_fallback` 汇聚节点**（同目录/同 _manifest.jsonl/同回灌器，两条入边，WB12-26）
   实时 tick：wal_writer 段文件→90% 容量**硬阻断拒收**→异步 drain；攒批 32 任务走 buffered_writer（与 WAL 同形不同物）
   幂等：ReplacingMergeTree 直接 INSERT / MergeTree 写前 DELETE；判重 check_tick_duplication（**准入闸半假绿在册**）
   D12-19（破损 part 自愈探测器）在此段挂"入库自愈腿"边注：常驻 DETACH 隔离环，不产数、只兜底
   ▼ （交接：原始库表 c0_meta/c1_market/c3_fundamental 就绪）
[D12-07/08/09/21 衍生加工：internal DAG 任务 + 任务表外进程内写手]
   输入=上段原始表；输出=派生表（technical_indicator/consensus/pattern/sector_state）
   依赖真源=tasks.yaml dependencies（**跨槽全 advisory**，悬空 task_id 亦判已满足，WB12-36）；档期倒挂只由 manual 件检测
   D12-21＝工厂/回测/组合进程内直写 CH 的产出面（无 task 行、无档期可打卡⇒两腿结构性缺位）
   失败降级：integrity/backfill 缺口检测回补
   ▼ （交接 A：派生表→消费端 TDM 因子/工厂——出图12 域，交图13/图9）
   ▼ （交接 B：主库热数据→冷备）
[D12-10a/10b/11/12 冷备：决策→执行→灾备（D12-12 是输入节点，不与执行体并列）]
   D12-12（契约分层线/批限量/excluded_tables）──输入──▶ D12-10b 滚动归档事件触发器
   D12-10b：backup.ps1 STAGE 4b 成功事件钩子 → rolling_archive_reconciler（五重安全阀+契约限量 3）→ 三段器
   D12-10a：人工 CLI 归档（同一执行体 export→verify→drop，两行不同生产者/不同验证口径，故拆）
   三段器：export(CH→Parquet, 注 FINAL)→verify(行数+抽样逐位)→drop；verify 不等则**不进 drop**；manifest append-only
   D12-11：CH 增量真值口径唯一=system.backup_log（非 backups 目录/非 state 文件）；F→G 镜像 + 版本化 code vault
   ▼ （交接 C：冷库/备份件→恢复演练 restore.ps1/restore_drill.py——演练任务从未运行在册）
[D12-13..20 对账修复：新鲜度/达标/缺口/污染/三账/维护/自愈 反馈环]
   检测：integrity_check(23:00) + supply_sentinel(06:50) + calendar_coverage(07:10)（detection_only，告警不回补）
   任务级：D12-20 档期打卡集合差四计数（应跑/成功/漏跑/失败）→ 输出 overdue 清单交 D12-14（catchup_guard 归此，禁两行重复挂载）
   回补：daily_backfill(17:00)/weekend_backfill/catchup_guard(05:30)；第 4 通道 auto_backfiller ⬜ 未接线
   修复：repair_kline_degraded_pull/c4_history_repair + 勿物理删走 valid_to/fact_close 通道；D12-19 DETACH 隔离环
   互验：consensus_crosscheck(23:30)→cross_validation_log（✅）；recon eod_reconciliation(15:40)→**未接线，不可达终点**
   维护：OPTIMIZE 合并（OS 周任务在跑、登记侧滞后、"失败 0"不可信）
   ▲ 修复结论回写 known_data_gaps.yaml（三渠道实证不可恢复→转 accepted）；反馈到采集段回补
```

**关键降级铁律**（data_ops_policy §1/§4）：三步验证（必要/真实/可逆）后动手；不可逆（删行/物理删表）升 Owner 门位；删冗余/重建后 OPTIMIZE FINAL 逐位比对；CH query 失败不抛→DDL 后必探针核实。

---

## §3 重叠判定（旁轴逐条处置：吸收/融合/扩展/废弃/引用）

| 撞车面 | 同职责内容 | 差异 | 处置 |
|--------|-----------|------|------|
| `data_asset_registry.yaml`（REG-DATAFLOW-001） | 都登记 sources/datasets/jobs | 注册表=**资产清单真源**（有什么）；图12=**运营流水**（怎么产/保/修）。且注册表静态清单已漂移：`entry_counts` 声明 datasets=293 而实际列表 **294**（+1 漂移，违反"清单必机生"），prose 头仍写"15源/76集/75作业"（严重滞后实测 18/294/122） | **引用**：图12 引注册表为资产真源，不复制条目（INV-1 同款）；漂移计数校正列为总包收口请求（§5 末） |
| `generate_data_acquisition_flow.py` | 都画"源→表"采集流 | 生成器只覆盖 采集+入库落库映射（段1-2），无衍生/冷备/对账；其 .md 产物 gitignored 未落地 | **吸收**：图12 生成器并入采集视图逻辑并扩为全链；原 .md 降为图12 子段（登记替代=净零，符合 #ARCH-310 R4） |
| 横向 `dataflowgraph`（dataflow_* PG 表） | 同为"数据流"字样 | 血缘轴（Dataset→Job→Dataset 边，静态"谁喂谁"）vs 生命周期轴（cron+新鲜度+对账，动态"怎么产/保/修"）；dataflow_runs 表记 per-Job 执行，与图12"调度档期"仅弱重叠 | **并行轴·引用**：不合并；图12 节点经 module_id 挂总线与 dataflowgraph 交叉（对齐 §3 挂轴）。dataflow_runs 作为可选第三腿证据引用 |
| **图13 交易日循环图** | **同一批 `schedule.yaml` 29 cron 槽** | 图12=**数据资产怎么流动/被产/被保住**（供给链视角：某槽产出哪张表、新鲜度、失败降级）；图13=**什么时点跑什么**（时序视角：16:30 daily_kline→16:45 dloop→17:00 backfill 的时间编排与交易节拍） | **共享·分界引用**：两图各自引用 schedule.yaml 但**读不同语义**（资产产出 vs 时点编排）。分界规则见下 |
| GOMAP `out_of_scope_refs`「数据治理」 | — | GOMAP 明确排除 | **吸收**：图12 承接该 out_of_scope 域（真源路径挂载 data_ops_policy.md，不复制内容） |

### ★ 图12 与图13 的分界（供总包裁两图边界）
**判据一句话**：**看这条边"是不是关于数据本身的产出/新鲜/保全/修复"**。
- 是 → **图12**（例：daily_kline 槽**产出** `kline_daily` 表、ch_writer 写失败降级、integrity_check 判其达标、catchup_guard 补其缺口、archiver 冷备其分区）。
- 否、只是"这个时点在交易日节拍里轮到它跑" → **图13**（例：把 daily_kline/dloop_post/eod_reconciliation 排进 08:34→…→16:45→15:40 的当日时序、盘前/盘中/盘后/夜窗分层）。
- **同一 task_id/槽位可两图都出现，但节点语义不同**：图12 的节点是"资产供给环节（D12-NN）"、边是数据流；图13 的节点是"时点活动"、边是时间先后。二者以 schedule.yaml 为**共享真源锚**交叉引用，互不吞并。
- **dloop_post(16:45)/eod_reconciliation(15:40) 归属仲裁**：数据供给链里"日终对账 PASS 作为终点"曾属图12 段5 终产物（D12-15）；而"16:45 总扳手把预案/盘中/收盘/结算/拍板串成日循环"属图13 时序编排。**建议总包**：D12-15 只画"对账作为数据质量终点产出 PASS"，dloop 十环节整体（MOD-PLAN-033）归图13，图12 以引用锚衔接、不复制其环节。**批次4 落地补充**：该"PASS 终点"今天不可达（D12-15 未接线），§0 门① 已按双实锚改写，本条仲裁不因此失效也不被代答。

---

## §4 批次志（四类批次跑没跑 + 实测增量 + 三扫收敛判定）

> **本件 = 批次1（图12 骨架首挖·结构扫描批）**。普查先验视为"批次0 外部输入"，实测校正如下（校正≠新增环节，而是把漂的先验对齐到机生真源）。

**普查先验 vs 本会话实测（全部 §7 命令可复跑）**：
| 度量 | 普查/文件先验 | 本会话实测 | 差 | 备注 |
|------|--------------|-----------|----|------|
| tasks.yaml 任务数 | 272 | **271** | -1 | `HAS_TASK_ID`=271 一致，无空 id |
| 不同数据源 | 23 | **23** | 0 | 见 §7-B 逐源计数 |
| 唯一目标表 | — | **192** | 新测 | tasks.yaml table 去重 |
| incremental=true 任务 | — | **163** | 新测 | |
| 配 fallback_sources 任务 | — | **39** | 新测 | 韧性三层覆盖 14.4% |
| schedule='disabled' 任务 | — | **4** | 新测 | 停摆任务，非删除 |
| schedule.yaml 槽位 | 27 | **29** | +2 | 新增 sector_close_final/sector_pre_open 等 |
| 执行器池数 | 4 | **5** | +1 | `scheduler.py:2394-2398` default/heavy/realtime/intraday_minute/intraday_sector（schedule.yaml 头注仍写 4，滞后） |
| CLI 子命令 | 7 | **8** | +1 | `cli.py` handlers：status/list/run/rerun-failed/pause/resume/start/speed-test（AGENTS"7"滞后） |
| 注册表 sources | 15(prose) | **18** | +3 | entry_counts 亦=18，prose 头滞后 |
| 注册表 datasets | 76(prose) | **294**(declared 293) | +218 | declared 与实际差 1=静态清单漂移 |
| 注册表 jobs | 75(prose) | **122** | +47 | trigger_type: scheduled 57/event_driven 39/manual 26 |
| CH 业务表 | — | **221** | 新测 | c0_meta 1/c1_market 187/c3_fundamental 33（live 实查） |

**四类批次执行状态**：
1. **三重扫描批（本批=批次1）**：① 按生产者逐家过——23 源全枚举（§7-B）✔；② 按形态/资产类别逐类过——5 段 + CH 三库分类 ✔；③ 按消费者文献——识别交接边界（→TDM/因子/工厂）✔。**三扫均跑一轮**，但第③扫（消费端反查缺口）**仅到边界、未挖至品种**，故尚不判收敛。
2. **需求批**：未独立开批（消费端缺口反向将在 D12-15/17 作业簿按需触发）。
3. **案例批**：本批借两个真实事故作锚——(a) 股东户数断供两月误标 ✅（skeleton §2.2 实证）→ 催生 supply_sentinel 段（D12-13）；(b) 9/1 调度器宕机错过 monthly_static 空 32h → 催生 catchup_guard（D12-14）。案例已转节点。
4. **考古批**：本批发现两处"考古级"陈旧——(a) iFinD 源 2026-08-14 已退役、akshare 转正（tasks.yaml:82 注）；(b) dataflowgraph 旧文件 `dataflow_graph_registry.yaml` 物理保留中（S6 改名过渡态）。旧实现登记，活性待作业簿清。

**增量计数曲线**：批次0（普查 272/27/4/7/15/76/75）→ 批次1（实测 271/29/5/8/18/294/122）。**注意**：这是"先验校正"不是"新环节增长"；中类层新增 = 从普查粗描 5 段细化到 **18 个可检核中类**。

### 批次 2~4 执行与曲线（批次4 落地时补记；条线真源=90 溢出账 / 11 消费端卷 / 12 提案卷）

| 批次 | 车道·件 | 中类层新增 | 溢出/发现 | 备注 |
|------|---------|-----------|-----------|------|
| 批次2 | L-WB12（01~05 五本作业簿 + 90 溢出账） | **+3**（WB12-01/02/03：拆行候选、探测器、任务级对账） | 53 条入册（WB12-01..53） | 五簿逐环节三腿复测，改判 6 处 |
| 批次3 | L-CONS12（11 消费端需求反查卷） | **+1**（N1 任务表外进程内派生簇） | C 态 5 表 + 1 幽灵引用 + 🌑 撤 2 缩 1 | 分母 174 消费点/40 被引表实扫 |
| 批次4 | L-EXP12（12 扩行提案与封顶重宣卷） | **+0**（四候选裁定毕、另驳回 6 项不加行） | 新中类候选 0；🌑/💰 逐条独立复验 | 相邻批 +3→+1→**0**，中类增量曲线拉平 |
| 批次4 落地 | **L-REGEN12（本批：骨架回写 + 图本体同步）** | 18→**22** 入骨架正身 | 见下"本批复跑增量" | 骨架回写权经总包让渡（本图骨架单张授权），批次号即本节 |

**本批（L-REGEN12，2026-09-25T15:22~15:26Z 只读复跑）相对 12 号卷的读数变动（各自注明时点，不互相覆盖）**：
1. **解除项**：`c1_market.macro_data` 本时可读（max(report_date)=09-24、近 30 日 41,593 行），`system.tables/parts/columns` 枚举面本时活（c1_market 202 表 / 23,186 parts）——批次4 那次"187×0 字节部件致全 system 面被打死"的**事故态已解除**；但 `probe_failed 必判红、禁把查不到写成无问题` 与 `禁依赖 system.* 判新鲜度` 两条口径**保留为常设纪律**（判例在册，不因本时可读而撤销）。
2. **推进项**：catchup_guard 台账由"停 09-21T09:25Z"推进到 09-25T01:24:20Z（PARTIAL rows=15），**仍未落 05:30 档**⇒D12-14 的③腿红项改判词不减等。
3. **新增红项（本批实见，图本体已入 gap）**：① `financial_derived_build` 末次 2026-09-24T23:27:35Z(北京) **FAILED**（`'<' not supported between str and datetime.date`）——D12-08 财务腿由"案卷列漏跑"升级为"跑必失败"；② `\ZephyrAlpha-DailyBackup` 09-25 06:00:01 次 **Result=267014（未终态，OS 侧 17h 未回收）**、当日报告 `code_backup.status=failed`、duration 32,796s（CH 腿本身 BACKUP_CREATED 成功）；③ 23:00 巡检档在本批复跑时刻（slot 后 ~25min）**无当日案卷且台账未推进**（末次仍 09-24T15:01:36Z）——D12-13/D12-20 的"按日连产"因此带当日缺跑疑点；④ 探测器审计件 `data/local_fallback/corrupted_parts_audit.jsonl` 主区仍不存在（零触发复证）。
4. **在册投影缺口（收口请求，本车道无写权）**：`path_ownership_map.yaml`（depgraph 派生在册投影）对 `scripts/ch/rolling_archive_reconciler.py` / `src/zephyr/data/supply_sentinel.py` / `calendar_coverage_checker.py` / `sector_state_pipeline.py` 无 claim（其中 sector_state_pipeline 在 depgraph 侧 blueprint_id 写作 `MOD-SIG-026 supplement`，含空格非 MOD-* 形态）⇒图本体 module_ref 一律改挂**在册可解析的代表路径**，禁止自造号，上述缺口以 gap 节点/条目留账。

**封矿判定（§6 四判据）**：**中类层已封矿**（§6.3 批次4 重宣正文，四判据逐条判齐；🌑/💰 清点毕、增量曲线 +3→+1→0 拉平）。**未封的部分**：叶层品种（sector 族谱、契约→实体映射、任务级对账逐月全量）与新事故触发的批次 5 重开条款——封矿≠图完成，图本体三件验收（22 环节再生 / terminal_gap 真指向 / gap_refs+幽灵全落）随本批施工面核验。

---

## §5 待挖清单（历史＝五本作业簿 + 11/12 两卷已交付；本节现值=叶层未尽项）

**批次2~4 已履行的挖矿件**（文件名以实交付名为准，与批次1 建议名不同）：`01_采集三段与源熔断.md`(D12-01/02/03) · `02_入库单通道与幂等判重.md`(04/05/06+D19 前身) · `03_衍生加工三族.md`(07/08/09) · `04_冷备灾备与分层.md`(10a/10b/11/12) · `05_对账修复六环.md`(13-18+D20 前身) · `11_消费端需求反查.md`（三扫第③扫，D21 出身）· `12_扩行提案与封顶重宣.md`（批次4 定稿表）。**中类层已无待挖**（§6.3 封顶）。

**叶层未尽项（不占中类枝，禁以"环节"名义增枝）**：
1. **sector 族谱**（WB12-48）——三张板块 K 线并存、生产者各异（tqcenter/tdx/miniqmt/akshare/特殊槽），消费端选错表的风险账在 D12-07/09 叶层。
2. **契约→实体表映射 13 项**（11 卷 N2）——TDM 13 个 `physical_type=契约/模块路径` 的 DS 引用无法按表名机械验供，归 `data_asset_registry` 收口。
3. **任务级对账逐月全量**——现证仅按日案卷 09-21~24 四日；历史全量在 `data/failures/` 与 `task_runs`，属 D12-20 叶层扩样。
4. **`option` 族与图13 语义互认**（12 卷 §5-2 末行）——互认前不判红，挂 `—待裁`。
5. **`redundant_source/` 六件 + sqlite_fallback 考古**（01/02 簿点名未裁）——活路径未证，禁以猜测入中类。
6. **D12-19 检测口径扩至 0 字节部件族**（施工项，非环节）——现口径只查 `CHECKSUM_DOESNT_MATCH`，抓不到装载期 "Suspiciously many 0-byte parts"。

**总包收口请求（本车道不直写共享面，登记诉求）**：
- (a) `data_asset_registry.yaml` `entry_counts.datasets` 声明 293 vs 实际 294 的 +1 漂移 → 建议生成器重刷 entry_counts（静态清单禁手维，宪章 §9.5）。
- (b) schedule.yaml 头注"16 槽位"、scheduler.py 头注"4 执行器池"、AGENTS"7 子命令" 三处 prose 滞后 → 建议改字段化或机生（§4 已实测为 29/5/8）。
- (c) 图12/图13 dloop_post+eod_reconciliation 归属仲裁（依 §3★ 建议）。
- (d) 蓝图 §4 图12 终局数 **21→22**（12 卷 §1 净账，本骨架已按 22 定稿）；`reconcile_execution_log` 假绿坑与"名字近亲须按列集双向核对"入本图坑册（★坑7）。
- (e) `path_ownership_map.yaml` 派生投影对四个在用执行体无 claim（§4 批次4 第 4 条）→ 建议生成器重刷投影；图本体已按"在册代表路径"挂号，未自造。
- (f) g_mirror `ch_vm_backup` 目标复活 P0（WB12-44）仍系 Owner 门位，不由施工件代答。

---

## §6 封顶声明与 🌑/💰 点名（skeleton §6 第3条：做不了的必全点名）

### 6.1 🌑 不可得点名（批次4 逐条独立复验：撤 2 缩 1 新 3）

| 点名 | 结论（批次4 裁定 + 本车道 09-25 复跑） | 实测锚 |
|------|----------------------------------------|--------|
| 🌑-1 调度执行日志/task_runs 不可得 | **收缩**（不再整条不可得）——残余两点：①**槽级 firing 日志**（scheduler 档期开火留痕，两侧均无；catchup_guard 05:30 自动档无留痕即其后果）②**`ops_*` 资源测量样本**（主区 `resource_samples/` 12 件无 ops_，D12-18 假成功病灶）；正牌落点名 `resource_samples/<task_id>.jsonl`（01 簿溢-7 口径） | 本车道复跑 `data/integrator_progress.db`（只读 URI）`task_runs` **188,671** 行、max(started_at)=2026-09-25T15:18Z、266 task_id、当日 1,714 runs |
| 🌑-2 schtasks 无权枚举 | **全撤**（本主机形态可实见，非不可得） | 本车道独立实跑 `Get-ScheduledTaskInfo`：DailyBackup LastRun=09-25 06:00:01、CH-OptimizeMerge-Weekly LastRun=09-20 03:30:00 Result=0、ZEPHYR-RESTORE-DRILL Result=267011（从未运行） |
| 🌑-3 冷/备盘挂载（F:/G:）不可见 | **全撤**（残余转环节判定，不再算"不可得"） | 本车道直读 `F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl` 2,515 行；04 簿盘侧四读数在册 |
| 🌑-4 **熔断器历史熔断状态不可考古**（新立） | 不可得成立——`source_circuit_breaker` 纯内存无持久，"熔过没有"事后不可得 | 01 簿内-5（INVARIANTS 逐字）；撤无可撤 |
| 🌑-5 **WAL 积压量与 90% 背压历史触发面**（新立） | 不可得成立——埋点全在内存 registry，无落盘留痕 | 02 簿 §2"欠"项 |
| 🌑-6 **滚动归档 skip 原因留痕**（新立） | 不可得成立——4b 段 stdout 仅 Write-Host 不落档、audit-trail 无 rolling 件；**亦是 D12-10b ✅ 的限定条件** | 04 簿 P-1；本车道复跑 `rolling_archive_state.json` mtime=09-21T07:37Z vs manifest 末条 09-24T02:07:50Z（不自洽仍在） |

**非 🌑 声明（禁把可修问题洗成不可得）**：`c1_market.macro_data` 的 0 字节部件装载失败**不列 🌑**——可经 DETACH/重导路径修复，属**运行事故红项**，走 gap 节点 `red_reason: broken_supply`（批次4 于 09-25 03:55 实录 187×0 字节部件致该表与全部 `system.*` 枚举面查询失败；本车道 09-25 23:2x 复跑该表已可读＝事故态解除，但 `probe_failed` 判例与 D12-19 检测口径缺口照挂，不因"现在能读"而消失）。

### 6.2 💰 花钱可解点名（批次4 复验：保 3 增 1）

| 点名 | 结论 | 锚 |
|------|------|----|
| 💰-1 tushare 额度 | **保留**（价格=谈判获取，无本机可得口径） | token 走 secrets，`cli.py:_load_dotenv` |
| 💰-2 iFinD 已退役 | **保留**（考古登记语义） | `tasks.yaml:82` 注 |
| 💰-3 bdpan 网盘 tick / 采购包 | **保留**（外部采购=💰，品种叶层点名于 D12-16） | `scripts/data/import_bdpan_tick_zip.py` 在库 |
| 💰-4 **miniQMT L2 行情权限**（新增） | 花钱可解——l2_tick 断供根因="需 L2 行情权限"且降级腿已清理，属💰非🌑 | 01 簿 D12-02 任务描述逐字；本车道复跑 `l2_tick`/`suspend` 仍双 0 行 |

`internal`(24)/`backfill`/`rss`/`akshare*`/`miniqmt`(本地 QMT 客户端) 等非付费，不入💰。

### 6.3 封顶声明（批次4 重宣，2026-09-25，由 12 号提案卷 L-EXP12 出料、L-REGEN12 回写）

> 图12 环节**封顶在中类层 22 个可检核单元**（采集 3｜入库 3｜衍生 4｜冷备 4｜对账修复 8；编号 D12-01~09、10a、10b、11~21）。四判据对账——**①三扫各跑一轮**（生产者扫含"调度器进程内常驻探测器"与"任务表外进程内派生"两补类；消费端扫含 174 点/40 表批与扩行版零新增验证轮；诚实注：分母层全量 174 点重跑未做，判据以"中类层零新增"达成，命令在 11 卷 §0 可复跑）；**②中类增量曲线 +3→+1→+0 拉平**；**③🌑 撤二缩一并新点三、💰 保三增一**，清点毕（§6.1/§6.2 逐条带实测锚）；**④本声明即封顶重宣**。
> 此后增长=叶→数据集/品种的实现（tasks.yaml 任务全集、特殊槽、data_asset_registry 数据集、CH 被引表等机生真源自然给全），**不再增枝**；增枝须过停止判据三问并**点名所补生产者类别** + 留批次号。其中 **D12-21 设专款防腐条款**——新表入 D12-21 必过三问，"应挂任务表/档期而未挂"者不得入格、一律走 gap 红项，防垃圾桶化。环节退役资格按内收判据（零触发零消费→退役）季度随并审执行——**D12-14 第 4 通道（⬜ 未接线）为下一审计首检对象**。
> **封矿 ≠ 图完成 ≠ 死亡**：新事故/新考古可触发批次 5 重开（触发即须引用本声明并过三问）；蓝图 §4 图12 终局验收三件（图本体再生 / terminal_gap 真指向 / gap_refs+幽灵落全）属施工活，随本批落地并在图本体侧核验。**本声明的可得性边界**：中类层判据不担保叶层完备（sector 族谱、契约→实体映射 13 项、任务级对账逐月全量等均在叶层/册面，不占中类枝）。

---

## §7 实查命令附录（全部可复跑核验；禁抄数字，跑出来的为准）

> 环境前置（RULE-ENV）：`export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"`（python 3.12.8），cwd=worktree 根。

### A. 数 tasks.yaml 任务 / 源 / 表 / 槽位
```bash
python -c "import yaml,collections as c;\
t=yaml.safe_load(open('src/zephyr/data/config/tasks.yaml',encoding='utf-8'))['tasks'];\
print('TOTAL_TASKS',len(t));\
print('DISTINCT_SOURCES',len({x.get('source') for x in t}));\
print('DISTINCT_TABLES',len({x.get('table') for x in t if x.get('table')}));\
print('INCREMENTAL_TRUE',sum(1 for x in t if x.get('incremental') is True));\
print('HAS_FALLBACK',sum(1 for x in t if x.get('fallback_sources')));\
print('SCHEDULE_DISABLED',sum(1 for x in t if x.get('schedule')=='disabled'))"
# 实测: 271 / 23 / 192 / 163 / 39 / 4
```
```bash
python -c "import yaml;s=yaml.safe_load(open('src/zephyr/data/config/schedule.yaml',encoding='utf-8'))['schedules'];\
import collections as c;print('TOTAL_SLOTS',len(s));\
print('EXECUTORS',dict(c.Counter(v.get('executor') for v in s.values())))"
# 实测: TOTAL_SLOTS=29; EXECUTORS default20/heavy5/realtime2/intraday_minute1/intraday_sector1
```
```bash
python -c "import yaml;t=yaml.safe_load(open('src/zephyr/data/config/tasks.yaml',encoding='utf-8'))['tasks'];\
import collections as c;print(dict(c.Counter(x.get('source') for x in t).most_common()))"
# 23 源逐计: akshare100 miniqmt56 akshare_alt36 internal24 tushare13 tqcenter5 tdx5 tickflow4 hyperliquid4 baostock3 fred3 rss2 crypto_binance2 eia2 qmt_bridge2 irm2 qweather2 cls1 eastmoney_news1 backfill1 crypto_sentiment_panel1 alt_regime_signal1 alt_fx_ecb1
```

### B. 执行器池（数 scheduler.py 注册处，勿信头注）
```bash
grep -nE "ThreadPoolExecutor\(" src/zephyr/data/scheduler.py | sed -n '2,6p'
# 实测 :2394-2398 共 5 池 default(8)/heavy(2)/realtime(4)/intraday_minute(4)/intraday_sector(2)
```

### C. CLI 子命令（数 handlers dict）
```bash
grep -nE '"(status|list|run|rerun-failed|pause|resume|start|speed-test)":' src/zephyr/data/cli.py
python -c "import ast;s=open('src/zephyr/data/cli.py').read();print('SUBCOMMANDS',s.count('sub.add_parser'))"
# 实测 8 个子命令（census/AGENTS 说 7，滞后）
```

### D. 数 data_asset_registry 资产（对比 declared vs 实际，抓漂移）
```bash
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml',encoding='utf-8'));\
print('DECLARED',d['entry_counts']);\
print('ACTUAL',{'sources':len(d['sources']),'datasets':len(d['datasets']),'jobs':len(d['jobs'])})"
# 实测 DECLARED {18,293,122} vs ACTUAL {18,294,122} → datasets 漂移 +1
```

### E. ClickHouse 新鲜度实查（**批次4 改口径：走 DatabaseService 失败即抛通道，禁 system.\* 枚举面**）
```bash
export PYTHONPATH="$PWD/src"    # 锁 worktree 包（否则 import 到主区代码，判据不同源）
python -c "import os;zephyr_check=__import__('zephyr');assert '.aidrafts' in zephyr_check.__file__,zephyr_check.__file__;\
from zephyr.infrastructure.database_service import get_db_service as g;\
c=g().get_clickhouse_conn(role='reader');\   # 失败即抛版通道：空串永不可能是返回值
print('SERVER',c.execute('SELECT now(), today(), timezone()'));\\
print('kline_daily',c.execute('SELECT max(trade_date),count() FROM c1_market.kline_daily'));\\
print('kline_daily_FINAL',c.execute('SELECT max(trade_date),count() FROM c1_market.kline_daily FINAL'));\\
print('tick',c.execute(\"SELECT max(trade_date),count() FROM c1_market.tick_data WHERE trade_date='2026-09-24'\"));\\
print('news_6h',c.execute('SELECT count(),max(publish_time) FROM c3_fundamental.news_data WHERE ingest_ts>=now()-INTERVAL 6 HOUR'));\\
print('crossval',c.execute('SELECT max(check_date),count() FROM c1_market.cross_validation_log'))"
# 本车道实测（2026-09-25T15:2xZ，服务器 tz=Etc/UTC，09-25 非交易日⇒T-0=09-24）：
#   kline_daily max=2026-09-24 行=10,108,162（FINAL 10,108,049）；tick 09-24 行=27,766,260；
#   news 近 6h=31,831 行；cross_validation_log max(check_date)=2026-09-25 行=1,601
```
```bash
# 执行腿正门（优先于 parts 末写代理）：task_runs / task_progress 只读 URI 实查
python -c "import sqlite3;c=sqlite3.connect('file:D:/ZephyrAlpha/data/integrator_progress.db?mode=ro',uri=True);\
print(c.execute('select count(*),max(started_at),count(distinct task_id) from task_runs').fetchall());\
print(c.execute(\"select task_id,last_run_at,last_status,rows_total from task_progress where task_id in ('integrity_check_daily','kline_daily_incremental','catchup_guard','consensus_daily_build','financial_derived_build')\").fetchall())"
# 实测：task_runs 188,702 行 / max=2026-09-25T15:39Z / 266 task_id；
#       kline_daily_incremental started=2026-09-24T08:30:00Z（=北京 16:30:00，与 cron 秒合）；
#       integrity_check_daily last_run=2026-09-24T15:01:36Z PARTIAL rows=182；
#       financial_derived_build / consensus_daily_build 均 last_status=FAILED（本车道新证）
```
```powershell
# OS 调度腿（schtasks 已可得，🌑-2 全撤）
powershell -NoProfile -Command "Get-ScheduledTaskInfo -TaskName ZephyrAlpha-DailyBackup,ZephyrAlpha-CH-OptimizeMerge-Weekly,ZEPHYR-RESTORE-DRILL | Select TaskName,LastRunTime,LastTaskResult,NextRunTime"
# 实测：DailyBackup 09-25 06:00:01 Result=267014（未终态，本车道新红）；OptimizeMerge 09-20 03:30 Result=0 Next 09-27；RESTORE-DRILL 267011（从未运行）
```

### ★ 已知坑（写进骨架避免后人重踩；1~4 批次1 亲测，5~8 批次2~4 亲测）
1. **静默失败陷阱（最高危）**：`ch_writer.query` [ERROR_CONTRACT] 明写 **"query失败->返回空字符串"**。本会话实测两次触发——
   - `SELECT max(toDateTime(timestamp/1000)) FROM c1_market.tick_data` → 返回 `''`（实为 **HTTP 500** 隐藏，非"无数据"）；
   - `SELECT max(toDate(created_at)) FROM c1_market.cross_validation_log` → 返回 `''`（实为 **HTTP 404**，列/查询不成立）。
   **纪律**：标 ✅ 前，空串**必须**换正确列名/SQL 复跑排除假读，不能把 `''` 读成"该表无数据/断供"；图本体证据通道只认 `DatabaseService.get_clickhouse_conn(role="reader")`（校验器 `CV-DUAL` 已把空串语义通道列为不合格证据）。
2. **ReplacingMergeTree 须 `FINAL`**：查去重后真值（尤其 max/计数/判重）须加 `FINAL`，否则合并前多版本干扰读数。且 **ch_reader 自动注 FINAL、DatabaseService 原生连接不注**（WB12-37 不对称在册）⇒ 同一 SQL 两通道结果可不同，`freshness_evidence.final_variant` 必须记双版。
3. **prose 计数必漂**：schedule.yaml 头注(16 槽)/scheduler 头注(4 池)/AGENTS(7 子命令)/registry prose(15/76/75) 全部滞后于机生实测(29/5/8/18/294/122)——**计数只信跑出来的，§9.5 静态清单禁手维**。
4. **采集流 .md 未落地**：`data_acquisition_flow.md` 是 **gitignored** 派生物，"采集段已机生"仅指生成器在仓、产物不在仓。
5. **枚举源单源必漏段（批次4 三案例坐实）**：只以 `tasks.yaml` 为生产者枚举源，会结构性漏掉三类现役环节——schedule.yaml 零任务**特殊槽**（12 枚，走 `_run_special_schedule` 硬编码白名单）、**调度器进程内常驻探测器**（D12-19）、**任务表外进程内写手**（D12-21）。⇒ 节点枚举必须四源并存（§0 门④★），生成器已机生 `machine.sources.process_in_product`。
6. **`system.*` 枚举面可被一张坏表整体打死（批次4 红证）**：09-25 03:55 实测 `c1_market.macro_data` 因 187 个 0 字节部件装载失败（Code 231→695/696→722），连锁令 `system.tables/parts/columns` 全库枚举面与该表直查同时失败，仅 `system.one/text_log/backup_log` 与 `DESCRIBE TABLE` 存活。**纪律**：判新鲜度用业务表 `max(date)`＋近窗计数；`system.parts.modification_time` 只作可选旁腿且必须 try-catch；**探测失败一律记 `probe_failed` 判红，禁把"查不到"写成"无问题"**（本条即本役判例，写进 laws 与校验器 CV-FRESH）。
7. **近亲名台账必须按列集双向核对（OBS-WF-14）**：`reconcile_execution_log`（图11 提交自愈环台账，实测 89,115 行且当天仍在写）与图12 的 `reconciliation_differences`（三账差异表，实测 **0 行**）名字近亲、语义无关。凡"按名字相似认领执行证据"必假绿——核对方向=①列集比对 ②写入方 grep ③行数/末次时刻一致性，三者同过才算同一张表。
8. **UTC 直读判档期必差 8 小时（WB12-30）**：服务器 `timezone()='Etc/UTC'` 而列类型多为 `DateTime64(3,'UTC')`、部分列为 `+08` 语义（news/sector 类）。凡以 max 时刻判"是否落在档期窗内"，必须先折北京再比 cron，否则会把 T-1 读成 T-0 或反之。
