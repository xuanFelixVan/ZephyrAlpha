---
ttl: task_bound
---

# 案卷 G — 业务链路机械核验（实测读数，无裁定）

- 核验基准：`git rev-parse HEAD` = `54622bbbf4f9fdbd1e807ec088e4a76be181b353`（分支 dev，2026-09-26 13:42:15 +0800）
- 落地口径：**只认 `git show HEAD:<path>` / `git ls-tree HEAD`**；工作区/索引差异单列"盘面态"，不计入落地。
- 库读口径：ClickHouse / PostgreSQL 一律只 SELECT；使用会抛错的 reader；CH 查询前先探 `system.*` 可达性。
- 本仓盘面警示（实测）：`git status --short` 共 459 条脏项（187 `??` / 143 `D` / 90 `M` / 28 `MM` / 11 `A`/`AM` / 1 `A`），
  索引面与 HEAD 面在 `docs/_working/chain_fullflow_*` 上方向相反（见第 1 条）。
- 本案卷自身盘面态（实测，非本代理操作）：本文件被仓外进程 `git add` 过——索引内快照＝82 行（＝本文件第一版），工作区面＝41,958 字节/338 行；
  `docs/_working/total_command_closeout/` 同窗另有 00_master_skeleton/01_adjudication_master/dossier_A~H 由并行会话写（盘上 mtime 14:36~14:51）。
  本代理未执行任何 `git add`/`commit`。

## 主表

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---------|------|---------|----|
| 1a | 交接书"案卷 16 件在册" | `git ls-tree --name-only HEAD -- docs/_working/chain_fullflow_closeout/ \| wc -l` | **16**（与声称一致） | 相符 |
| 1b | 同上·逐件 | `git ls-tree -l HEAD -- <dir>` | 见下"16 件清单"，合计 297,970 字节 | 相符 |
| 1c | 交接书"旧名 chain_fullflow_20260926 已彻底消失" | `git ls-tree -r --name-only HEAD \| grep -c chain_fullflow_20260926` | HEAD 面 **0 命中**（已消失） | 相符（HEAD 面） |
| 1d | 同上·盘面 | `ls -d docs/_working/*chain_fullflow*` + `git status --short -- <两目录>` | 盘面 **两目录并存**：`chain_fullflow_20260926/` 存盘且 7 件在索引中标 `AM`（新增待提交）；`chain_fullflow_closeout/` 盘面仅 7 件、9 件在索引中标 `D`（暂存删除）。即索引面 = 旧名布局，与 HEAD 面（新名 16 件）方向相反 | 盘面不符（见"新增发现"N1） |

### 16 件清单（HEAD 面，字节数＝blob size）

| 字节 | 文件名 |
|-----:|--------|
| 23421 | business_pipeline_skeleton.md |
| 3278 | lane_pipe_auto_runtime_trading.md |
| 2648 | lane_pipe_consensus_daily.md |
| 2723 | lane_pipe_financial_derived.md |
| 3140 | lane_pipe_llm_backend_ollama.md |
| 3456 | lane_pipe_news_sentiment_score.md |
| 2589 | lane_pipe_pattern_win_rate.md |
| 4462 | lane_pipe_realtime_snapshot.md |
| 4074 | lane_pipe_reconciliation_differences.md |
| 20648 | mine_door_registration_completion.md |
| 15967 | mine_guard_wiring_census.md |
| 20699 | mine_pipe_blockage_substages.md |
| 39804 | mine_pipe_false_green_census.md |
| 23061 | mine_queue_liveness_and_trigger_mass.md |
| 38947 | mine_snapshot_selfconsistency_witness.md |
| 4913 | mining_closeout_and_adjudication.md |

盘面存留（7 件，均在 `chain_fullflow_20260926/`）：`mine_door_registration_completion.md`(20648B) /
`mine_guard_wiring_census.md`(15967B) / `mine_pipe_blockage_substages.md`(20699B) /
`mine_pipe_false_green_census.md`(39804B) / `mine_queue_liveness_and_trigger_mass.md`(23061B) /
`mine_snapshot_selfconsistency_witness.md`(38947B) / `mining_closeout_and_adjudication.md`(4913B)。
另 `chain_fullflow_closeout/` 盘面 7 件同名同字节。HEAD 的 9 件 `lane_pipe_*.md` + `business_pipeline_skeleton.md` 盘面无。

## 第 2 批 · 链路分母与三态（实测复算）

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---------|------|---------|----|
| 2-1 | 交接书"N=62" | `python` 解析 `git show HEAD:docs/_working/chain_fullflow_closeout/business_pipeline_skeleton.md` 表格体，正则 `^\|\s*(\d+)\s*\|` | 编号行 **62** 行，编号 1..62 连续、**无重号无缺号**（unique=62） | 相符 |
| 2-2 | 交接书"通30/半通23/不通9" | 同上，逐行取首个含 ✅/🟡/❌ 单元格为判定列 | 表体实测 **✅29 / 🟡25 / ❌8**（合计 62）；正文 L131-133 宣称 **30/23/9** | **不符**（分布差 1/2/1，见 N2） |
| 2-3 | 骨架 L133"不通 9 条"清单 | 逐条回查表体判定 | #19/#28/#30/#34/#47/#48/#53/#54 = ❌（8 条，行号 60,69,71,75,93,94,109,110）；**#43 表体为 ✅** 且 #43 名称是"决策日报"，全表 62 行**无**名为 pattern_win_rate 的行（该串仅出现在 L133/L134 散文） | **不符**（清单与表体错位一本） |
| 2-4 | 交接书四套分母 122/132/151/62 | `git grep -n` on HEAD | 见下表"四套分母对账" | 口径互异，非同一量纲 |

### 四套分母对账（每套：分母 · 口径 · 出处文件:行号，均 HEAD 面）

| 分母 | 对象（口径） | 出处 文件:行号 | 盘上实测复算 |
|-----:|------------|---------------|-------------|
| **62** | "链路"＝一条有独立触发+独立落库面+≥1 消费方+≥1 自检尺的业务流；271 个 data 任务算"腿"不单列 | `docs/_working/chain_fullflow_closeout/business_pipeline_skeleton.md:26`（并集去重结果 N=62）、`:34`（"## 1. 链路总表（62 条）"） | 表体 62 行（2-1）；7 路并集来源表 `:18-26`，其中第 ⑥ 路 depgraph 标注"**未取到**（glob 超时）"＝**7 路实取 6 路** |
| **122** | "环节"（F01–F122，13 段）＝全流通骨架全环节册，非链路 | `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md:13`、`:20`；`00_挖矿分工册.md:3`、`:11`（122 环节→12 深挖组） | `90_crosscheck_link_census.md:99`：**F01–F122 编号无空洞**（2 位 id 去重 99 + 3 位 23 = 122 行），但同句判"**环节集合不完备**" |
| **151** | "环节"扩展建议值（122→~151，＋29，去重落位可缩至 ~140） | `docs/_working/fullflow_mining/00_skeleton/90_crosscheck_link_census.md:99`；`91_chief_command_wave1.md:78`（"122→151 环节扩展…**未开工**"） | 无盘上 151 行产物可数（属提案，`91_chief_command_wave1.md:78` 自陈未开工） |
| **132** | 既非链路亦非环节：TDM `config/trading_decision_map.yaml` 的 **entry 分流节点数**，被 F 册当作"entry 132"引用 | `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md:73`（"182 节点：entry 132/position 18/exit 19/portfolio 13"）；`90_crosscheck_link_census.md:37`（实测分流 **128/18/19/13/4**，判 entry 132＝128＋crypto 4 混计 → "口径漂移 D-1"）；`:161`（"F 册 entry **132 vs 实测 128**"） | 132 与 128+4 之差＝混计 crypto；同句另记 TDM 节点 138 vs 实测 182、ROOR 76 vs 77、F 册顶层包 56 vs 57 共 4 处数值漂移 |

补充：`00_全环节总册.md:13` 还提到 **76 环节**（M0 骨架 `00_skeleton_fullflow.md` 已收卷的 D/T/B/A/G/S/F/X 八段），全部保留并映射入 F 编号 → 实际存在 **76 / 122 / 151(提案) / 62 / 132(TDM entry 混计)** 五套数，非四套。

## 第 3 批 · 270 任务总数（已验），假绿灯 5 件（待库读）

| # | 声称出处 | 命令 | 实测读数 | 态 |
|---|---------|------|---------|----|
| 3-1 | 交接书"270 任务假绿灯普查" | `python` + `yaml.safe_load(git show HEAD:src/zephyr/data/config/tasks.yaml)` | `tasks` 列表长度 **271**；`task_id` 去重后 **270**；重复 id = **`cohort_ledger_daily`**（HEAD 面行号 `:3437` 与 `:3816` 各一次） | 相符（270＝去重值） |
| 3-2 | 骨架"调度器加载 271 任务/29 档/18 源" | 同上 | 271＝列表长度（含 1 条重复），270＝唯一 id → 两数之差**不是**枚举口径差，而是**同 id 重复条目** | **不符**（`mine_pipe_blockage_substages.md:88` R9 与 `:128` L-1 把它记为"枚举口径差 1，已查无"） |
| 3-3 | 普查件是否真 270 行 | `git show HEAD:docs/_working/chain_fullflow_closeout/mine_pipe_false_green_census.md`（`:5`、`:20`"全量清单（270 行）"） | 待复算行数（下批） | 待验 |
| 3-4 | task_runs 真源位置 | 骨架 `:29`"任务运行真态取 SQLite `data/integrator_progress.db`（`mode=ro` 只读）的 `task_runs`" | 真源＝DuckDB 还是 SQLite 需盘上核（下批） | 待验 |

## 探针可信度（前置实测，影响全部库读口径）

- CH 连通：`DatabaseService.get_clickhouse_conn(role="reader")`（`src/zephyr/infrastructure/database_service.py:161`，全仓唯一 Client 构造点）→
  `SELECT 1` OK；`hostName()/version()` = `zephyr-ch` / `26.6.1.1193`；`currentUser()` = `zephyr_reader`，`currentDatabase()` = `c1_market`。
- `system.*` 可达性：**可达**（`system.tables` 总 422 行 = c0_meta 1 / c1_backtest 16 / c1_market 202 / c3_fundamental 34 / system 169；
  `system.columns` c1_market 2848 行；`system.parts WHERE active AND bytes=0` 返回**空集**＝当前无零字节活跃 part）。
  → 本窗口内"全库 system.* 永久失败"已知病**未现**。
- **新增探针病（可复现）**：跨库 `system.tables` 名称模式探测会**静默返回 0 行**，而表实际存在。
  复现（均 reader 抛错型）：`SELECT count() FROM system.tables WHERE name LIKE '%consensus%'` → **0**（重试 3 次同果，ILIKE 同 0）；
  同义带库限 `WHERE database='c3_fundamental' AND name LIKE '%consensus%'` → **2**；直查 `count() FROM c3_fundamental.consensus_daily` → 6,797,719 行。
  对照：`WHERE name LIKE '%daily%'` 跨库 → 25 行（有返回）。口径＝zephyr_reader@zephyr-ch，时间窗 2026-09-26 本地 14:2x~14:4x。
  影响面：普查件里 `NO_TARGET_TABLE(table_missing_in_ch)` 判定若靠跨库名称探测得出，则与本病同型（该案卷 3 例：
  `block_trade_qmt` / `dragon_tiger_qmt` / `margin_trading_qmt`，见 `mine_pipe_false_green_census.md` 行内）。
- 交接书/案卷所用读法分两型（实读原文）：`business_pipeline_skeleton.md:29` 记落库实测走
  `zephyr.data.ch_writer.query`（**该函数异常时 `return ""`**，实测 `src/zephyr/data/ch_writer.py:445/459/483` 三处 return ""）；
  `mine_pipe_false_green_census.md:6` 记走 "DatabaseService reader Client，抛错单列 PROBE_INCONCLUSIVE"。两型读法不同源。

## 第 3 批（续）· 假绿灯 5 件复算

| 任务名 | task_runs 最近一次（SQLite `data/integrator_progress.db` mode=ro，全表 190,390 行，distinct task_id=266） | 目标表 | 目标表 count()（CH reader 实读，2026-09-26 14:3x） | 最新数据日 | 与声称 |
|--------|---|---|---|---|---|
| realtime_snapshot_incremental | SUCCESS@2026-09-24T07:40:06+00:00，runs=797，fetched=5568/written=5568 | c1_market.realtime_snapshot | **0** | —（表空） | 相符（SUCCESS+written 5568 而表 0 行） |
| etf_benchmark_refresh | SUCCESS@2026-09-**25**T21:30:03+00:00，runs=19，fetched=0/written=0 | c1_market.etf_benchmark | **0** | — | 表 0 行相符；**账本最近态与案卷不同**（案卷行记 SUCCESS@2026-09-24T21:30:10） |
| suspend_status_premarket | SUCCESS@2026-09-24T00:34:00+00:00，runs=24，fetched=0/written=0 | c1_market.suspend | **36**（非 0！） | max(trade_date)=**2026-09-23** | **不符**（案卷记 0 行） |
| suspend_status_postclose | SUCCESS@2026-09-24T10:12:48+00:00，runs=25，fetched=0/written=0 | c1_market.suspend | **36** | 2026-09-23 | **不符**（同上） |
| suspend_status_derive_weekend | SUCCESS@2026-09-**25**T21:30:10+00:00，runs=21，fetched=**36**/written=**36** | c1_market.suspend | **36** | 2026-09-23 | **不符**：既不 0 行，也不满足该案卷"不可分辨集合"自设判据（要求 fetched=0 且 written=0） |

- 时间窗解释（实测）：`suspend` 的 36 行与 `suspend_status_derive_weekend` 2026-09-25T21:30:10Z（＝本地 09-26 05:30）那次 written=36 同量；
  案卷件盘上时间戳 09-26 02:44~03:02（本地），**早于该次写入** → 读数为"案卷快照时点"与"本窗口时点"之差，非同一时刻复算。
- 案卷内部算术：`mine_pipe_false_green_census.md` 表体复算＝**270 行、task_id 唯一 270**（与"全量清单 270 行"相符）；
  判定列自数：GREEN_WITH_DATA 226／NOT_GREEN 合计 25（STALE 13+FAILED 8+RUNNING 3+DEFERRED_PERSISTENCE 1）／
  NEVER_RUN 10／FALSE_GREEN 5／NO_TARGET_TABLE 4（table_missing_in_ch 3 + no_table_declared 1）＝ **270**，与文中分布逐档吻合。
- 另一班声称的"不可分辨集合＝4"：案卷列 etf_benchmark_refresh + suspend 三腿；本窗口实测其中 **3 腿目标表已非 0 行**、
  1 腿（derive_weekend）账本 fetched/written 非 0 → 4 件里按案卷自设判据本窗口**仅 1 件（etf_benchmark_refresh）成立**。

## 第 6 条 · 空壳表 10 张（CH 实读 + 在册核对）

真源点名的 10 张＝`business_pipeline_skeleton.md:150`（"并集去重后另有 10 张 count()=0"）：
edb_data / realtime_snapshot / index_valuation_daily_v2 / ipo_schedule / margin_target_adjustment / market_index_meta /
msci_adjustment / reconciliation_differences / stock_candidate_pool / stock_valuation。
`mine_pipe_blockage_substages.md:121` 另称"**空壳表 9 张**"并列 6 张未登记者 + `suspend` + `etf_benchmark`（**列名实为 8 张**）。

| 表 | 所在库（`system.tables` 带库限实读） | count()（CH reader） | 备注 |
|----|---|---:|---|
| c1_market.edb_data | c1_market | **0** | 声称已登记（accepted·iFind 退役） |
| c1_market.realtime_snapshot | c1_market | **0** | 链路 #19 ❌ |
| c1_market.index_valuation_daily_v2 | c1_market | **0** | 未登记 |
| c1_market.ipo_schedule | c1_market | **0** | 未登记 |
| c1_market.margin_target_adjustment | c1_market | **0** | 未登记 |
| c1_market.market_index_meta | c1_market | **0** | 未登记 |
| c1_market.msci_adjustment | c1_market | **0** | 未登记 |
| c1_market.reconciliation_differences | c1_market | **0** | 声称"真源在 governance.db"（见第 8 条） |
| c1_market.stock_candidate_pool | c1_market | **0** | 未登记 |
| c1_market.stock_valuation | **c1_market 唯一**（全库 `%stock_valuation%` 带库限复扫＝c1_market 1 张，c3_fundamental 34 表内无此名） | **0** | 跨库重名声称：本窗口实读**不存在第二个同名表** |
| c1_market.suspend | c1_market | **36**（非空，max trade_date 2026-09-23） | 案卷快照时点为 0 → 时点差 |
| c1_market.etf_benchmark | c1_market | **0** | |

10 张中 9 张 count()=0 复核成立（edb_data 亦 0），`suspend`/`etf_benchmark` 两张里仅 etf_benchmark 仍 0。

## 第 7 条 · hfq 表族与 adj_factor（实读）

- `system.columns`（带库限）`name='lineage_version' AND table LIKE '%hfq%'` → 仅 **1 行：`kline_daily_hfq.lineage_version`**；
  `kline_weekly_hfq`、`kline_monthly_hfq` **无该列** → 交接书声称的"weekly/monthly 缺 lineage_version"**相符**。
- 族内表盘点（`system.tables WHERE database='c1_market' AND name LIKE '%hfq%'`）＝**11 张**：
  `kline_daily_hfq`、`kline_weekly_hfq`、`kline_monthly_hfq` + 迁移残留 8 张
  （`kline_daily_hfq_legacy_20260924` / `_preversion_20260925` / `_quarantine_20260925` / `_recalc`、
  `kline_monthly_hfq_legacy_20260924` / `kline_monthly_hfq_legacy_r1_20260924`、
  `kline_weekly_hfq_legacy_20260924` / `kline_weekly_hfq_legacy_r1_20260924`）——与骨架 `:161` 所列吻合（该句未列 monthly_legacy_r1，实读为 11 张）。
- `kline_daily.adj_factor` 恒 1 死列声称：`SELECT count(DISTINCT adj_factor), min, max FROM c1_market.kline_daily`
  → **(1, Decimal('1'), Decimal('1'))** ＝ distinct 只有 1 个值、恒 1 → **相符**。

## 第 9 条 · sector 881/8803 深度与 sector_constituent（实读）

| 读数 | 命令/口径 | 实测 |
|------|----------|------|
| 881 深史上限 | `c1_market.kline_sector_880`（761,860 行、uniqExact(sector_code)=729、min 2020-03-17、max 2026-09-24）按 `sector_code LIKE '881%'` | 159,198 行 / **128 个去重标的** / **min(trade_date)=2021-08-02** / max 2026-09-24 → **相符** |
| 881 各段起点 | 同上按前 4 位分组 | 8810:23 只、8811:25、8812:30、8813:26、8814:24（合计 128），四段 min 均 2021-08-02 |
| 8803 段 | 同上 `8803` 前缀 | 61 只 / 76,250 行 / min 2021-08-02 / max 2026-09-24 |
| 名册侧同证 | `data/registers/metaq_sector_name/sector_code_name_registry.csv`（HEAD 面，表头 11 列，数据 **729 行**，sector_code 去重 729 无重号；coverage_status：named 719 / unresolved 10） | 881 族 128 行中 first_trade_date=2021-08-02 者 **127**，另 1 行 2026-06-29；8803 族 61 行 first_trade_date **全部** 2021-08-02 |
| "469→728" 声称 | HEAD 面 `docs/_working/chain_fullflow_closeout/` 与 `fullflow_mining/` 内 grep `469`/`728` | **未找到该声称的出处件**（chain 案卷内 469/728 零命中，仅 `kline_60min` 行数 24637280 含"728"子串）；盘上现值＝**729**（CH uniqExact 与 CSV 行数同值） |
| sector_constituent 实存非空 | `c1_market.sector_constituent` | **236,836 行** / uniqExact(sector_code)=**595** / uniqExact(stock_code)=**6179** / max(update_date)=**2026-09-03**（较 09-24 滞 21 天）；列集含 valid_from/valid_to/data_source |

## 第 4 条 · 'str > date' 崩溃（代码点实测 + 账本原文 + 是否已修）

账本原文（SQLite `data/integrator_progress.db` mode=ro，表 `task_runs`，列 run_id/task_id/started_at/finished_at/status/rows_fetched/rows_written/error_msg）：

| task_id | 在册运行次数 | 最近一次 started_at | status | error_msg 原文 |
|---------|-------------:|--------------------|--------|----------------|
| consensus_daily_build | **1** | 2026-09-18T22:30:20+00:00 | FAILED | `'>' not supported between instances of 'str' and 'datetime.date'` |
| financial_derived_build | 5 | 2026-09-25T21:32:12+00:00 | FAILED | `'<' not supported between instances of 'str' and 'datetime.date'` |

- 案卷声称 `financial_derived` 最近 FAILED@2026-09-24T23:26:42Z（`lane_pipe_financial_derived.md:23`）；
  本窗口按 `ORDER BY started_at DESC` 实读最近为 **2026-09-25T21:32:12Z**（同错，另一实例）→ 案卷快照时点早于 09-25 那次。
- consensus_daily 表读数复算（CH reader）：`c3_fundamental.consensus_daily` = **6,797,719 行 / max(trade_date)=2026-09-14**；
  `c3_fundamental.consensus_daily_repaired` = **1,655,363 行 / max=2026-09-15** → 与 `lane_pipe_consensus_daily.md` 所记两值**逐位相符**。
  `c3_fundamental.financial_derived` 存在（34 表清单内），但该表**无 `trade_date` 列**（直查报 Code:47 Unknown identifier），案卷记其口径为 `report_period`（max 2026-06-30，本窗口未复算该列）。

代码注记 vs 消费点（均 HEAD 面，文件:行号）：

| 位置 | 原文/摘录 | 实读类型判定 |
|------|----------|-------------|
| `src/zephyr/data/provider_base.py:71-73` | `start: datetime.date` / `end: datetime.date`（`@dataclass class FetchPayload`，定义起 `:58`） | 注记＝**datetime.date**（与声称"注记 datetime.date"相符） |
| `src/zephyr/data/implementations/internal_compute_provider.py:615-622` | `if payload.table == "c3_fundamental.financial_derived": yield from self._fetch_financial_derived(payload)`；`...consensus_daily` → `_fetch_fund_consensus_daily(payload)` | 调度侧路由（tasks.yaml `:634-637` consensus_daily_build source=internal；`:661-664` financial_derived_build source=internal） |
| `internal_compute_provider.py:680-683`、`:699`、`:710` | `yield from run_compute(... end=payload.end ...)`；`run_compute_repaired(symbols=..., start=payload.start, end=payload.end)`；`run_compute(symbols=payload.symbols, start=payload.start, end=payload.end)` | **注入点＝payload 的 date 对象直传**（对照 `:664` 一处 `run_compute()` 无参全量分支） |
| `src/zephyr/data/implementations/financial_derived_compute.py:374-376` | `def run_compute(symbols=None, start: str \| None = None, end: str \| None = None)`；docstring `:384`"start/end: 衍生公告日窗口（含，**iso str**）" | 形参声明＝**str**，与注入侧 date 相互矛盾 |
| `financial_derived_compute.py:397`、`:399` | `if start and row["announce_date"] < start:` / `if end and row["announce_date"] > end:` | **崩溃点**：`row["announce_date"]` 是 str（由 `:261` `"announce_date": a.isoformat()` 产出）→ str `<` date ＝账本 `'<' not supported between instances of 'str' and 'datetime.date'` |
| `src/zephyr/data/implementations/consensus_daily_compute.py:120-121/308-309` | `start: str \| None = None, end: str \| None = None`（docstring `:130/:317`"iso str"） | 同上声明 str |
| `consensus_daily_compute.py:146-147` | `lo_iso = start or ""` / `hi_iso = end or ""` | date 对象真值非空 → `hi_iso` 仍为 **date**，无归一 |
| `consensus_daily_compute.py:155`、`:157` | `if hi_iso and td_iso > hi_iso:` / `if lo_iso and td_iso < lo_iso:` | **崩溃点**：`td_iso = td.isoformat()`（`:154`，str）→ str `>` date ＝账本 `'>' not supported ...` |

- 判"是否已修"口径（HEAD 现码该行）：`:397/:399` 与 `:146-147/:155/:157` **均无 isoformat/fromisoformat 归一**，与崩溃原文一致 → HEAD 面**未见归一**。
- 声称方向核对：交接书称"注记 datetime.date 而消费端拿 ISO 字符串直比"——实测为**同一处矛盾的两个面**（注入端 date、计算核行值 ISO str），
  但方向相反于表述：计算核形参自己声明 `str`，被注入的才是 `date`；行值（`announce_date`/`td_iso`）恒为 str。
- 日志侧证据：本窗口在 `logs/` 未做定向 grep（列入"缺口"）。

## 第 5 条 · Fill 写者（HEAD 面逐符号计数）

- 定义：`src/zephyr/shared/contracts/fill.py:50`（`@dataclass(frozen=True) class Fill`，`:49` 装饰行）。
- `git grep -n "Fill("` HEAD -- src/zephyr/ 实测构造点（Python 侧，剔除 JS 同名 `infoFill(`）：

| 文件:行号 | 符号 | 备注 |
|-----------|------|------|
| `src/zephyr/ex_core/adapters/miniqmt_broker.py:742` | `Fill(` | 于 `fills: list[Fill]`（`:725`）累积、`:757` 排序、`:764` 返回（内存对象，非落库） |
| `src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:306` | `fill = Fill(` | 文件桥 broker |
| `src/zephyr/ex_core/fill_handler.py:116` | `Fill(` | JSON dict → Fill 逆变换（`:93` 正向 `_fill_to_json_dict`） |
| `src/zephyr/ex_core/order_execution_saga.py:804`、`:860` | `ctx.fill = Fill(` / `reverse_fill = Fill(` | saga 正向/回滚 |
| `src/zephyr/backtest/core/matching_logic.py:341/406/502/585` | `MatchingFill(` | 非 Fill（注释 `:219-221` 说明三方解耦：MatchingFill→BacktestFill / →Fill） |
| `src/zephyr/backtest/core/matching_engine.py:955` | `BacktestFill(` | 回测专用 |

- 成交落库面实测（CH reader，带库限探测）：`system.tables` 中 `%fill%` 命名表 → **0 张**（c1_market/c0_meta/c1_backtest）；
  `c1_market.fills` 直查 → ServerException Code:60 `Unknown table expression identifier`（表不存在，抛错型确认）。
- 唯一相近落库表：`c1_market.execution_report`（`%execution%` 命中 1 张），实测 **count() = 1 行**。
- "已接入单一写者"逐符号验真：实现符号存在＝`src/zephyr/ex_core/execution_report_producer.py:152 class ExecutionReportProducer`（＋`src/zephyr/ex_core/async_fill_dispatcher.py` 在册）；
  接线点计数＝`qmt_file_bridge_broker.py:427 def attach_execution_report_producer`（方法定义）＋
  **唯一外部调用** `src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py:160 broker.attach_execution_report_producer(producer)`（producer 于 `:153` 构造，`:97/:122` 持有/暴露）；
  测试面 `tests/ex_core/test_execution_report_producer.py`、`tests/ex_core/test_async_fill_dispatcher.py` 在册；
  算法流册 `docs/03_modules/_domain_execution_core/algo_flow/async_fill_dispatcher.yaml` 在册。
  broker 侧注释自陈未接线语义＝`qmt_file_bridge_broker.py:8` 与 `:420`"（None=未接线，行为与历史一致）"。
- F57 定义处＝`docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md:102`
  （"F57 结算对账与三方核对 … src/zephyr/trading/settlement_reconciliation.py、three_way_reconciliation.py；ex_core/eod_reconciliation.py | built"）。
  本窗口未在该行或 chain 案卷内检索到"Fill 无生产写者"字样原文（列入缺口）。

## 第 8 条 · 供数先于接核对器（reconciliation_differences 双源）

| 项 | 实测读数（口径） |
|----|------------------|
| 双源之一＝DuckDB 治理库 | 文件 `data/databases/governance.db`（盘上 203,563,008 字节，mtime 2026-09-26 14:40）；`duckdb.connect(read_only=True)` 列 `%recon%` 表 → `reconcile_execution_log`、`reconciliation_differences`；`SELECT count(), max(detected_at) FROM reconciliation_differences` → **(0, None)** |
| 双源之二＝ClickHouse | `c1_market.reconciliation_differences`（`system.tables` 带库限实读唯一命中）→ **count()=0** |
| 两库皆空复算 | **成立**（两读数各由抛错型客户端取得，非空串静默） |
| 写入方在册 | `src/zephyr/trading/recon_runner.py`（`:22` 注释声明差异落 governance.db append-only；`L117 INSERT INTO reconciliation_differences`；DDL `src/zephyr/reporting/reconciliation_schema.py:42`）——锚点取自 `lane_pipe_reconciliation_differences.md:14-16`，本窗口复核两文件均在 HEAD |
| 读点 | `api_server.py:1484` 映射展示项"对账差异"（案卷所记锚点，本窗口未逐行复验） |
| 关联证据 | `c1_market.execution_report` 实测 **count()=1**（案卷记"仅 1 行 · 2026-09-18"同量级） |

触发方式（只给读数，判据＝是否 cron/Timer/sleep-loop）：

- `src/zephyr/data/config/schedule.yaml:209-210` → `eod_reconciliation:` + `cron: "40 15 * * 0-4"`（该文件 cron 槽位共 **29** 个）。
- 同文件 `:202-208` 注释自陈：唯一入口＝`src/zephyr/trading/recon_runner.py:392 run_daily_reconciliation`，
  并自陈"日终核对批，**非自愈 reconciler 环路**——§9.3 约束的是自愈环，本槽位是定时事实核对，与 L11 integrity_check 同性质；盘中持仓对账走 position 事件入口（R-015）"。
- `git grep "Timer|time.sleep|AsyncIOScheduler|add_job"` on `src/zephyr/trading/recon_runner.py`、`src/zephyr/data/ch_parts_monitor.py` → **零命中**。
- 事件面符号 `PositionReconciler.handle_execution_report` 仅见于 schedule.yaml:207-208 注释（"属 z-land 实现面，本车道只排班+哨兵"）——实现行号未定位（列缺口）。

## 第 10 条 · miniQMT 口径（HEAD 面 grep，行号＋原句）

四件（HEAD 面原句仍含"全面清退/已退役/断供"）：

| 文件 | 行号 | 原句（截取） |
|------|-----:|-------------|
| `src/zephyr/ex_core/miniqmt_channel_manager.py` | 58/59/61/63 | "miniQMT 通道退役冻结…"；"券商 2026-09-18 关停 miniQMT 通道（XtMiniQmt.exe **全面清退**）…"；"但退役日起禁真连（fail-closed）"；"退役不是删功能，是关阀门" |
| `src/zephyr/backtest/implementations/ch_tick_replay.py` | 19 | "（xtquant 本地缓存）读回测 tick——9/18 miniQMT 退役后**断供**。本 adapter 读…" |
| `src/zephyr/frontend/dashboard/web/features/bridge/br-page.js` | 54/58/63/65/66 | `cd.textContent = 'miniQMT **已退役**（' + st.retire_date + '）'`；"退役倒计时"；`:63` 注释"miniqmt 存活信号 9/18 退役…显示'已退役'占位，非'已停'"；`var miniState = miniRetired ? '**已退役**' : …`；"退役后转历史基线" |
| `src/zephyr/frontend/dashboard/web/pages/bridge.html` | 3/26 | "miniQMT 2026-09-18 券商**全面清退**，QMT HTTP 桥（EXEC v16.4 沙箱内 18901）接班…"；"miniQMT 退役后其列转为历史基线（灰显）" |

另三件（声称应已为"仅实盘退役"口径）：

| 文件（HEAD 真实路径） | "仅实盘"命中 | HEAD 面现口径 |
|----------------------|-------------:|---------------|
| `src/zephyr/data/config/known_data_gaps.yaml` | **0** | `:19-20`"9/18 miniQMT **清退**后：本 API 经大QMT 沙箱可用（ZEPHYR_HIST_PROBE 2026-08-26 实证…）"；`:109`"新浪/miniqmt 均不进料"；`:216`"Level-2 逐笔…（miniQMT get_l2_quote）" |
| `src/zephyr/data/config/data_supply_sentinel.yaml` | **0** | `:12`"股东户数表 2026-07 断供两月无人知（miniqmt **清退**后任务空挂）"；`:596`"tick 三秒快照主表：miniQMT 09-18 清退后**无在跑供给通道**" |
| `docs/_working/automation/campaign/HANDOFF_20260921_ab_league.md` | **0** | `:16`"**MiniQMT 09-18 下线**——一切走大 QMT 文件桥（MOD-L06-001-QMTFB），禁拉 XtMiniQmt" |

路径核对：交接书所写 `config/data_supply_sentinel.yaml` 真身＝`src/zephyr/data/config/data_supply_sentinel.yaml`；
`HANDOFF_20260921_ab_league.md` 真身＝`docs/_working/automation/campaign/`，非 `docs/_working/` 直下。

## 第 11 条 · TDM/ALGO_FLOW 同步欠账（抽样＋门进程内自测）

抽样口径＝`git log -20 -- src/zephyr/data/ src/zephyr/trading/ src/zephyr/ex_core/` 内前 5 个含实现 .py（非 tests）的 commit，`git show --name-only` 取同批文件：

| commit | 日期 | 实现 .py 数 | 同批 algo_flow/decision_map yaml |
|--------|-----:|-----------:|--------------------------------|
| `ef9e118ae7` | 2026-09-26 | 15 | **13**（含 `docs/03_modules/_domain_data/algo_flow/data/macro_vintage.yaml` 等） |
| `dc1c66e651` | 2026-09-26 | 1（process_reaper.py） | **0** |
| `bce9d7a80a` | 2026-09-26 | 1（process_reaper.py） | **0** |
| `30505c93f6` | 2026-09-26 | 78 | **38** |
| `d070dd4270` | 2026-09-25 | 1（tqcenter_provider.py） | **0** |

门判据与自测（只读；纯核 `check_algo_note_sync` 不触 git、不写审计文件）：

- 门件＝`src/zephyr/gov_enforcement/commit_gates/algo_note_sync_gate.py`；注册＝`gate_registry.yaml:638`（`- gate_id: ALGO-NOTE-SYNC`）、
  `in_process_gate_registry.yaml:342-344`（module_path＋`factory_function: make_algo_note_sync_gate`）；
  判据函数 `check_algo_note_sync` 定义 `:200`、失败消息 `:247`、工厂 `:287`、`GateSpec(gate_id="ALGO-NOTE-SYNC", check=_check, priority=62)` `:322`。
  该门同时列名 `fail_open_register.yaml:2354`（stage FF-14、line 44、on_money_path=false、has_trace=false）与 `:5997`（count: 6）。
  门自陈 fail-open 面＝`:8` INVARIANTS"地图缺失/解析失败/git 异常 fail-open（passed=True）"。
- 地图真源实读：`config/trading_decision_map.yaml` → 节点 **182**，带 `module_ref` **121**（全为 .py 路径），无 module_ref **61**（红节点豁免）。
- 自测 A（**改代码未改 yaml**）：`files=["src/zephyr/plan_engine/daily_warroom_pipeline.py"]`（节点 `TDM-E-L0` 的 module_ref），`diff_text=""`、`old_text=new_text=HEAD 面地图全文`
  → **blocked=True**，消息原文含"ALGO-NOTE-SYNC：1 个节点的实现代码在本 commit 被触碰，但其大白话算法说明未同步——算法改了大白话必须跟着改…algo_note_zh 未同 commit 修订"。
- 自测 B（代码不在地图）：`src/zephyr/trading/process_reaper.py`、`src/zephyr/data/implementations/tqcenter_provider.py` 的地图 module_ref 命中节点数 **0**；
  以未在册路径调用 → **blocked=False**。即上表三个"零 yaml"样本文件均落在该门**作用域之外**（门仅覆盖 121 个 module_ref，非全仓 .py）。
- 模块级 `docs/03_modules/**/algo_flow/*.yaml` 的同步义务不属该门判据：`ch_parts_monitor.yaml`、`process_reaper.yaml` 均在 HEAD 在册（同第 12 条表），
  逐模块"是否同批修订"本窗口未做（列缺口）。

## 第 12 条 · 环节自动化五件（在册/最后改动/消费者计数，不判性质）

| 件 | 在 HEAD | 最后改动 commit（`git log -1 -- <path>`） | 消费者 grep 读数（HEAD 面 `git grep -c`） |
|----|---------|------------------------------------------|----------------------------------------|
| `src/zephyr/data/scheduler.py` | 是 | `20885a28f2` 2026-09-24「[st-pipeline-final-20260924][secbuild·板块线批0-3终版代投] 19 件」 | 命中多件：`scripts/start_scheduler.ps1:2`、`scripts/governance/apply_resource_plan.py:1`、`scripts/governance/generators/generate_resource_profile_registry.py:4`、`src/zephyr/data/alerter.py:1`、`src/zephyr/alt_data/alt_regime_signals.py:1` 等（>8 件） |
| `src/zephyr/trading/process_reaper.py` | 是 | `dc1c66e651` 2026-09-26「[P-19 续] 根因坐实：_kill_pid_tree 遇 AccessDenied 不再连坐整轮收割」 | `scripts/register_process_reaper_task.ps1:6`、`src/zephyr/governance/resilience_governance/emergency_track_guardian.py:2`、`src/zephyr/infrastructure/capacity_assurance/host_resource_governor.py:2`、`src/zephyr/orchestrator/global_state_aggregator.py:2`、`generate_resource_profile_registry.py:1` 等（>6 件） |
| `scripts/backup/backup_reconciler.py` | 是 | `c359d642dc` 2026-09-26「fix(backup): P-7 备份裁决载体改脱离进程＋假绿分支去重降复杂度」 | `scripts/backup/backup.ps1:2`、`scripts/backup/README.md:2`、`config/governance_operations_map.yaml:2`、`capability_canonical_file_registry.yaml:2`、`fail_open_register.yaml:2`、`module_translation_registry.yaml:1` 等（>6 件） |
| `src/zephyr/data/ch_parts_monitor.py` | 是 | `8bb5da3b95` 2026-09-16「chore(algo-flow): P2-1 死块清偿+语料图修复落地 02（90 件）」 | 代码侧外部命中**仅 1 件**＝`src/zephyr/data/scheduler.py:2`；其余为文档命中（`scripts/governance/oneoff/data_domain_audit_report_db.md:4`）；自身 1 |
| `scripts/governance/fullflow/generate_fullflow_crosscheck.py` | **否（HEAD 无此件）** | 无（`git log --` 空输出） | 工作区亦无该目录（`ls scripts/governance/fullflow/` → No such file）；唯一命中＝`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml:52534-52538`（`token: fullflow-closure-wave2-generate-fullflow-crosscheck-20260925`、`created_by: st-ailayer-final-20260924`、`capability: fullflow_closure_wave2`）；同批 `scripts/governance/fullflow/__init__.py`（`:52529`）亦 HEAD 无该文件 |

## 新增发现（本窗口实测，交接书未列）

| # | 读数 | 证据锚点 |
|---|------|---------|
| N1 | **索引面与 HEAD 面反向**：索引中 `chain_fullflow_closeout/` 的 9 件（`business_pipeline_skeleton.md` + 8 件 `lane_pipe_*.md`）标 `D`（暂存删除），同时旧名目录 `chain_fullflow_20260926/` 的 7 件标 `AM`（新增）；`git stash list` **空**、`.runtime/workspace_alerts/` 仅 `claim_release_request_gpu.json`（**无 stash_notice.json**）。工作区全仓脏项 459（`?? 187 / D 143 / M 90 / MM 28 / AM 10 / A 1`） | `git status --short -- docs/_working/chain_fullflow_closeout docs/_working/chain_fullflow_20260926`、`git stash list` |
| N2 | **三态分布正文与表体不自洽**：正文 `:131-133` 记 30/23/9，表体逐行判定实数 ✅29/🟡25/❌8（合计 62） | `business_pipeline_skeleton.md` HEAD 面 python 复算 |
| N3 | **"不通 9 条"清单里 #43 指向错行**：表体 #43＝"决策日报"判定 ✅；62 行内无名为 `pattern_win_rate` 的行 | 同上 `:89` vs `:133` |
| N4 | **270 与 271 之差有确定原因**：`tasks.yaml` 列表 271 条，`task_id` 唯一 270，重复项＝`cohort_ledger_daily`（HEAD 面 `:3437`、`:3816`）。案卷把该差记为"枚举口径差，已查无" | `src/zephyr/data/config/tasks.yaml`、`mine_pipe_blockage_substages.md:88/:128` |
| N5 | **账本维是第三套分母**：`task_runs` distinct task_id＝**266**；与 tasks.yaml(270) 双向差集：账本有而配置无 6 个（`cb_kline_incremental`/`edb_data_incremental`/`emotion_index_auction`/`kline_daily_bj_incremental`/`kline_futures_qmt_incremental`/`sector_kline_incremental`），配置有而账本无 **10** 个（`factor_decay_monitor_weekly`、`global_hsi/kospi/nikkei/usdcnh_daily_incremental`、`ir_activity_record_refresh`、`irm_interactive_qa_refresh`、`kline_5min_history_backfill`、`kline_us_daily_qmt_incremental`、`tick_backfill_weekly`）——与案卷 NEVER_RUN=10 同数 | `data/integrator_progress.db` mode=ro |
| N6 | **跨库 system.tables 名称探测会静默返回 0**（详见"探针可信度"节）：`LIKE '%consensus%'` 三次复测均 0，带 `database=` 限同义查询＝2，直查该表 6,797,719 行 | `.runtime/tmp/dossierG/ch_recheck*.py` |
| N7 | **`suspend` 现非 0 行**（36 行，max trade_date 2026-09-23）：假绿灯 5 件里的 suspend 三腿本窗口不再满足"表 0 行"；`suspend_status_derive_weekend` 账本 fetched/written＝36/36 亦不满足该案"不可分辨集合"的自设判据（fetched=0 且 written=0）→ 4 件集合本窗口按同判据仅 1 件成立 | CH reader + `task_runs` |
| N8 | **D 队骨架的落库读数用 `ch_writer.query`**，该函数异常时 `return ""`（`src/zephyr/data/ch_writer.py:445/459/483`）→ 骨架面"0 行/无数据"类读数与本窗口抛错型读数是两套可信度 | `business_pipeline_skeleton.md:29` |
| N9 | **空壳表张数三处不一致**：骨架 `:150`＝10 张（点名 10）；`mine_pipe_blockage_substages.md:121`＝"9 张"但点名 8 张；本窗口实读点名 12 张中 **11 张 count()=0**，唯一非 0 是 `suspend`。`stock_valuation` 全库唯一在 `c1_market`（无跨库重名表） | CH reader `system.tables`（带库限）+ `count()` |
| N10 | **consensus_daily 账本仅 1 条运行记录**（ledger_runs=1，2026-09-18 FAILED），非"每晚推进后停更"的形态；`market_pattern_win_rate` 在 `task_runs` **0 条记录** | `task_runs` |
| N11 | `'str' and 'datetime.date'` 崩溃原文在 `logs/`（`*.log`/`*.txt`，depth≤2，533 个文件）内**零命中**；唯一在册载体＝`task_runs.error_msg`（两腿各一条原文，见第 4 条表）→ "最近 3 条时间戳"无法从日志给出 | `grep -rl` on logs/ |
| N12 | **ALGO-NOTE-SYNC 门作用域读数**：地图 182 节点中仅 121 有 `module_ref`；抽样 5 commit 里 3 个"零同批 yaml"的 .py（process_reaper×2、tqcenter_provider）都不在 module_ref 集合内 → 门对该类文件结构性不触发（自测 B blocked=False） | `gate 件 :200/:322`、`config/trading_decision_map.yaml` |
| N13 | 该门同时是 **fail-open 登记件**（`fail_open_register.yaml:2354` stage FF-14/line 44、`:5997` count 6；门 `:8` 自陈"地图缺失/解析失败/git 异常 fail-open（passed=True）"） | 同左 |
| N14 | 注册表指向**不存在**的生成器：`capability_canonical_file_registry.yaml:52534` 登记 `scripts/governance/fullflow/generate_fullflow_crosscheck.py`，HEAD 面与工作区面均无该文件/目录（同 `__init__.py`） | 第 12 条表末行 |
| N15 | `system.parts WHERE active AND bytes=0` 本窗口返回空集 → 已知"零字节破损件致 system.* 永久失败"病在该窗口**未现**（不代表已治） | CH reader |

## 无法判定 / 缺口

1. `git ls-tree` 只给 HEAD 面；本窗口**未做**逐文件 `git show HEAD:<path>` 与盘上内容的一致性 diff（除第 1 条字节数与 `AM`/`D` 状态），故"16 件内容=案卷宣称内容"未验。
2. 交接书"consensus_daily 与 financial_derived 同崩 'str > date'"的代码级归因已给（`:397/:399`、`:155/:157` + 注入点 `:680-683/:699/:710`），
   但**未定位**调度器把 `payload.start`（date）灌入声明为 str 形参的路径上是否存在 `isoformat()` 归一被旁路的具体调用栈（未运行该腿，运行会写库，越只读红线）。
3. `api_server.py:1484` 对账差异读点、`recon_runner.py:117/:392`、`miniqmt_channel_manager` 之外是否有别的 miniQMT 口径件——未逐行复验，仅按锚点存在性读数。
4. `PositionReconciler.handle_execution_report` 实现行号未定位（事件触发声称的可执行证据缺口）。
5. 模块级 `algo_flow/*.yaml` 与 `algo_note_zh` 的"逐模块同批修订率"未机算（需生成器，本窗口禁写仓库文件，故只给 5 commit 抽样）。
6. `"Fill 无生产写者"`字样：HEAD 面 `chain_fullflow_closeout/` 与 `fullflow_mining/00_skeleton/` 内未 grep 到该原句；F57 行原文只到"built"。声称出处未定位 → 该项**只验了符号计数**，未验"总根"表述本身。
7. `sector 881 深史上限`已双面复算相符；**"469→728"未找到出处件**（HEAD 面 chain/fullflow 目录 grep 469、728 无相关命中），盘上现值 729（CH uniqExact 与 CSV 行数同）→ 469 的口径（表？名册？时点？）无从对照。
8. 假绿灯 5 件的"目标表行数"本窗口读数与案卷快照时点不同（suspend 族），**无法在同一时点复现案卷原读数**（案卷运行时刻≈09-26 02:44~03:02 本地）。
9. `chain_fullflow_closeout/` 的 9 件盘上缺失是否会被后续提交落地为删除（索引态），本窗口不提交、不判定。
10. 未引用任何裁定号（`ruling_registry` 未查，因本案卷无需引裁定）。

## 收尾：与交接书不符处 Top 5（≤400 字）

1. **三态分布**：交接书 30/23/9；HEAD 案卷表体逐行实数 **29/25/8**（N=62 与"不通清单第 9 项 #43"均错位，#43 表体为 ✅ 且 62 行无 pattern_win_rate 行）。
2. **假绿灯 5 件现势**：`suspend` 三腿目标表本窗口＝**36 行 / max 2026-09-23**（非 0）；`suspend_status_derive_weekend` 账本 fetched/written＝36/36 → "不可分辨集合 4"按同判据本窗口仅 **1 件**成立；另 2 件（realtime_snapshot、etf_benchmark）0 行复核成立。
3. **空壳表张数**：交接书"9~10 张 + 6 张未登记"；点名口径三处互异（10／9 但列 8／本窗口实读 11 张 count=0，唯 `suspend` 非 0）；`stock_valuation` 全库唯一在 **c1_market**，无跨库重名表。
4. **270/271**：270＝`task_id` 去重值，真因＝`cohort_ledger_daily` 在 `tasks.yaml:3437/:3816` **重复**，非案卷所记"枚举口径差 1（已查无）"；账本维另有第三分母 **266**。
5. **未落地/失踪项**：miniQMT 口径四件 HEAD 面仍含"全面清退/已退役/断供"，另三件"仅实盘"命中 **0**（未改成）；`generate_fullflow_crosscheck.py` HEAD 与工作区**均不存在**却仍被 canonical registry `:52534` 登记；`'str>date'` 两崩溃点 HEAD **无归一**，`financial_derived_build` 最近 FAILED 2026-09-25T21:32:12Z（案卷所记 09-24 那次已被更新实例覆盖）。
