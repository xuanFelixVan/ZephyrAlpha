---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: 独立信号清单（⑨成绩官每日维护）
---

# 独立信号清单 independent_signals

维护岗=⑨成绩官（每日）；工具=scripts/backtest/fexam/signal_orthogonality.py pool-report 子命令（产出相关矩阵+参与率）。
用途=③④席与点子引擎 prompt 的必读"占领区摘要"（SOP §3-G 三件套之二）；新候选正交准入闸基准（|corr|<=0.3）。

（空册待首班 pool-report 产出后填入：成员表/相关矩阵/独立信号有效数）
## 2026-10-15 首版 ｜ st-qoder-p09-1015-02（⑨成绩官首班·实判非占位）

### 1 pool-report 实测三态：工具可跑、入参无源、池物化面缺位 ⇒ 本班**未能**产出相关矩阵，如实报"闸未开"

- 工具＝可执行：`python scripts/backtest/fexam/signal_orthogonality.py pool-report --help` → rc=0（实测 2026-10-15）。①②班派单把根因从"工具未落地"改判"有工具未跑"；本席复核后**再改判**为"**池物化面缺位**"——工具确可跑，但 `--pool` 在全仓找不到合法入参。
- 入参契约＝目录内 `*.csv`，每档首行须 `date,sig` 两列（signal_orthogonality.py:59-80）。
- 三条独立实测（先立正对照：`SELECT 1`→`[(1,)]`、`SHOW DATABASES`→5 库，读路可用，故空集非读路故障）：
  1. 全仓 `*.csv` 中首行恰为 `date,sig` 者 **0 个**（Grep 正则 `^date,sig$`＋glob `*.csv` → No files found）；
  2. IBT 产物根 `docs/_working/integrated_backtest/`（＝ibt_runner.py:45-47 `ART_ROOT`）**目录不存在**；`.runtime/tmp/ibt_panels/` 仅 `W_POSTD.pkl` 一枚（面板，非信号序列）；
  3. CH 侧候选序列表面在而**零行**：`c1_market.factor_signal`（14 列，含 factor_id/as_of_date/rank_pct/normalized_value）与 `c1_market.factor_feature_value`（9 列，含 factor_id/trade_date/value）的 `SELECT DISTINCT factor_id LIMIT 30` 均返回空集。
- 15 员池真源形制＝**代码不是数据**：`scripts/backtest/ibt/ibt_runner.py:58-74` `MEMBERS`＝15 个 sid → `scripts/backtest/translated/c4_*.py`（5×FACT＋10×CAND）。要出相关矩阵须先执行 15 个信号模块物化 `date,sig`＝跑考试，属 ⑤/⑦⑧席写域，本席不代做（铁律：不改码、不跑考试）。→ 已开单：feedback/to_impl.md 修⑤、feedback/to_datasource.md 缺②。

### 2 成员表（逐字抄自 ibt_runner.py:58-74；"命名面轴"仅按文件名判读，未经内容复核）

| # | sid | 文件名 | 命名面轴 |
|---|---|---|---|
| 1 | FACT-4f749668 | c4_fact_4f749668.py | FACT 编号名，轴不可从文件名判读 |
| 2 | FACT-4228020a | c4_fact_4228020a.py | 同上 |
| 3 | FACT-e293e217 | c4_fact_e293e217.py | 同上 |
| 4 | FACT-e831084c | c4_fact_e831084c.py | 同上 |
| 5 | FACT-4b200528 | c4_fact_4b200528.py | 同上 |
| 6 | CAND-8d000bf3ccc3 | c4_8d000bf3ccc3_pb_poe.py | 估值/基本面（PB·ROE） |
| 7 | CAND-c4ec6332c07f | c4_c4ec6332c07f_trend_score.py | 趋势 |
| 8 | CAND-e3da6fa71af1 | c4_e3da6fa71af1_panic_rebound.py | 反转（恐慌反弹） |
| 9 | CAND-4440d07f973f | c4_4440d07f973f_ultrashort.py | 超短 |
| 10 | CAND-eaddc3f9db4e | c4_eaddc3f9db4e_rsrs_r2.py | 市场状态（RSRS） |
| 11 | CAND-d06cab686cef | c4_d06cab686cef_rsrs_opt.py | 市场状态（RSRS 变体） |
| 12 | CAND-29eb91dbaf60 | c4_29eb91dbaf60_crash_dodge.py | 风控/择时 |
| 13 | CAND-a4543012b464 | c4_a4543012b464_trend5.py | 趋势 |
| 14 | CAND-bd42540f86e4 | c4_bd42540f86e4_pe_pb.py | 估值 |
| 15 | CAND-6a6ec8869ddb | c4_6a6ec8869ddb_momentum62.py | 动量 |

命名面即见重复：趋势×2、RSRS×2、估值×2，与 SOP"成员互为拷贝"叙述方向一致；但**方向一致不等于实测**。

### 3 独立信号有效数

- 实测值＝**未获得**（§1 三条实测）。
- 在册叙述值＝4.4，出处 `research_production_line_policy.md:274`（原文："15 员池实际仅 4.4 个独立信号（FACT×5 corr=1.000 拷贝、RSRS×2 变体 0.97、2 员纯买入持有）"）与 `:305`。本席 find 全仓**无任何 pool-report 产物**可复现该数 ⇒ 本表标 `4.4＝在册叙述，未复现`，禁当实测引用（防下一班把叙述抄成读数）。
- 旁证（分数册面，独立于池）：卡考 75 行按族实排＝calibration 66＋comparison 9；按节点前缀，单节点 `TDM-E-L1-S2` 占 34 行（45.3%）、`TDM-X-R1-01` 占 8 行（10.7%）⇒ **出分面本身高度集中**。

### 4 占领区摘要（分数册 75 行 card_id 实测口径，供 ③④席与点子引擎防重入）

| 矿楼（pulse/mining_directions.md 楼号） | 分数册 75 行覆盖实测（card_id 语义面） | 对 ③④席的含义 |
|---|---|---|
| 楼4 动量反转 | 已 2 次出分且同判负：rows[73]、rows[74]（20 日动量正向溢价） | 正向动量轴已被双次独立物化否决；反转/残差动量子轴零出分＝空白 |
| 楼5 波动率 | 零"以波动率为信号本体"的出分行；波动率名只作事件触发条件出现在 `TDM-E-L1-S2/calibration/*_ind_vol*_high_event` | 本体空白；把波动率当**条件**的用法已密集占位（34 行） |
| 楼1 盘口 / 楼2 基本面 / 楼3 估值 / 楼6 流动性 / 楼7 资金流 / 楼8 另类 / 楼10 情绪重建 | 分数册 75 行 card_id 无对应本体出分行 | 空白轴；优先按 SOP §3-G 过闸 |
| 楼9 市场状态 | 卡考面无独立出分行；RSRS 两员在池（§2）而未进卡考 | 待开 |

判读面限定：以上按 **card_id 命名语义**归类，本席未逐卡读卡体内容；反证请直接指认行号，本班记为待改判。
## 2026-10-15 日更 ｜ st-qoder-p09-1015-03（⑨成绩官第三班，v1.5.1 每日维护条）

- 复测命令（本班正文原样跑过）：
  - `python scripts/backtest/fexam/signal_orthogonality.py --help` → 子命令 `{gate,pool-report}` 在册，工具**可执行**（三态之"可跑"）。
  - `python scripts/backtest/fexam/signal_orthogonality.py pool-report --help` → `--pool POOL 信号池：glob 或目录（*.csv）`，`--pool` **无默认值**。
  - `python scripts/backtest/fexam/signal_orthogonality.py pool-report --pool 'data/**/*.csv'` → `[SIGNAL-ORTHOGONALITY] ERROR: 信号 CSV 须含 date,sig 两列: …limit_up_down_weekend_rows_20260916_pre_ghostclean.csv 实有 ['trade_date','symbol','name','close',…]`。
  - 全仓 `date,sig` 池实测＝0（`*sig*pool*.csv`／`data/**/signals/*.csv` 候选面皆空）。
- 结论：**有效独立信号数（PR）与相关矩阵今日仍不可产出**，阻塞点与 02 班一致＝15 员池的 `date,sig` CSV 物化腿缺位（在册单＝to_impl.md 修⑤；本席不代做物化，属⑤席写域）。④席/③席在闸未开期间按 02 班口径：候选只入 lane CSV，**不入"过闸"账**。
- 参与率（PR）面本班零读数；占领区摘要无变化（楼4 动量双卡 fail、空白轴六条）。
## 2026-10-15 日更 ｜ st-qoder-p09-1015-04（⑨成绩官第四班：PR 与相关矩阵**首次有机读产出**，占位"零读数"作废）

- 本班把 02/03 班"闸未开、PR 零读数"的结论**改判为可开**：阻塞只是列名契约（工具要 `date,sig`，采集面产 `trade_date,value`）。本班在仓外临时面改名适配后跑通工具（工具与采集面**一字未改**，绕行件＝`.runtime/tmp/st-qoder-p09-1015-04/pool_datesig/`、`pool6/`；正解与附带症状见 to_impl.md「修⑤ 正解改写」）。
- 实测读数（`signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool6`，报告件 `pool6_report.json`）：
  - 池＝agg8 批 6 个序列本体×变换：`lu_count, lu_count_z20, lu_ratio, lu_ratio_z20, avg_abs_ret, avg_abs_ret_z20`；`n_members=6`，`n_common_dates=1855`（2019-02-18..2026-10-12），**`effective_n_signals(PR)=2.1272`**，特征值 `[3.7676, 1.5442, 0.5776, 0.1053, 0.0051, 0.0002]`。
  - 相关矩阵极值（Spearman，逐对全列在 `pool6_report.json`）：`lu_count_z20↔lu_ratio_z20=0.9998`；`lu_count↔lu_ratio=0.9949`；level↔自身 z20＝`lu_count 0.7738／lu_ratio 0.7743／avg_abs_ret 0.7399`；跨本体最低＝`avg_abs_ret_z20↔lu_count_z20=0.2198`（**唯一低于在册 0.3 门的组**）。
- **占领区摘要（当日增量，供③④席 prompt）**：agg8 批名义 8 卡、实占 **2 轴**——涨跌停广度轴（`lu_count`＝`lu_ratio`，两变换共 4 卡）＋已实现绝对收益轴（`avg_abs_ret` 4 卡）。凡新候选落这两轴者按重复件计量，不计入产量。
- 空白轴地图**维持**（02 班六条：波动率/流动性/资金面/基本面/估值/盘口 本体零出分；本班 8 行 card_id 语义未落入六轴任一本体）。判读面限定沿用 02 班声明：按 card_id 命名语义归类，未逐卡读卡体。
- 15 员池（CONDAXIS 整装）PR 面本班**未产出**：整池 `date,sig` 物化仍缺（⑤席写域），且 13 员直跑触发"共同日期不足 0<3"（见修⑤附带症状）。
## 2026-10-15 日更 ｜ st-qoder-p09-1015-05（⑨成绩官第五班：15 员池 PR 复测＝仍无源，根因收窄为"有写者零行"）

- 复跑命令与读数（本班正文原样跑）：
  - `DatabaseService().get_clickhouse_conn()` → `SELECT count() FROM c1_market.factor_signal`＝`[(0,)]`；`c1_market.factor_feature_value`＝`[(0,)]`（同批非读路故障：同连接 `system.tables` 查询正常返回）。
  - 池物化腿另一支：`ls docs/_working/integrated_backtest/` → **No such file or directory**（`ART_ROOT` 定义在 `scripts/backtest/ibt/ibt_runner.py:45-47`）。
  - 15 员成员表＝`ibt_runner.py:58-74` `MEMBERS`（FACT×5＋CAND×10，本班逐字复读，与 02 班 §2 表一致，无增删）。
- **有效独立信号数（PR）今日状态**：15 员池＝**仍未获得**（物化属⑤席写域，本席不跑考试）；在册唯一机读产出＝agg8 六员池 **PR=2.1272**（04 班，`.runtime/tmp/st-qoder-p09-1015-04/pool6_report.json`），本班**未推翻、未新增**。
- 在册叙述值 4.4（`research_production_line_policy.md:274`）继续标"**未复现**"——本席累计五班无任何 pool-report 产物可再现该数，禁当实测引用。
- 占领区摘要**维持** 04 班面（涨跌停广度轴＋已实现绝对收益轴；空白轴六条）。本班增量 0 行考试 ⇒ 无新轴入占。
- 空白轴地图判读面限定沿用：按 card_id 命名语义归类，本席未逐卡读卡体。

## 2026-10-15 日更 ｜ st-qoder-p09-1015-06（⑨成绩官第六班：**全册"独立通过轴"首份账**＋15 员池 PR 第三度复测同值）

- **独立通过轴数＝1（不是 2）**：磁盘面 83 行中 `verdict: pass` 仅 **2 行**＝rows[76] `TDM-E-L1-S2/calibration/41_agg_lu_count_z20_fwd10` 与 rows[78] `…43_agg_lu_ratio_z20_fwd10`，而 04 班正交实测（`pool6_report.json`）给出 `lu_count_z20↔lu_ratio_z20=0.9998` ⇒ 两 pass 落**同一根轴**。按 SOP v1.4.0"产量按轴计量"，本生产线至今**出分 83 次／64 个对象／独立通过轴 1 根**，且该轴尚未升 verified（两腿未过：`ic_ir_min` 柱无面＋净/成本全 NaN，见 04 班 §3 与在册修⑥/修⑨）。⚠ 引用本册时禁把"2 个 pass"叙述成"2 个独立信号"。
- 15 员池（CONDAXIS 整装）PR：本班**第三度**复测，读数与 02/05 班逐位同——`DatabaseService().get_clickhouse_conn()` → `SELECT count() FROM c1_market.factor_signal`＝`[(0,)]`、`c1_market.factor_feature_value`＝`[(0,)]`；`docs/_working/integrated_backtest/` 目录本班实测仍不存在。**状态维持"仍未获得"**，根因仍为 05 班在册的"有写者、零行＝生产腿未跑"。本班未再烧物化腿（⑤席写域），亦未第三次开缺数单（该题 02 班 :17 已在册，①席"在册注明以免每班重复报"的欠账仍在）。
- 占领区摘要**无变化**（本班增量 0 行考试 ⇒ 无新轴入占）：涨跌停广度轴（`lu_count`≡`lu_ratio`）＋已实现绝对收益轴，两 pass 同落第一轴。
- 在册叙述值 4.4（`research_production_line_policy.md:274`）继续标"**未复现**"（本席累计六班无任何产物可再现该数）。
- 空白轴地图判读面限定沿用：按 card_id 命名语义归类，本席未逐卡读卡体。
## 2026-10-15 日更 ｜ st-qoder-p09-1015-08（⑨成绩官第八班：**独立命题分母首份更正＝59，非 65**）

- 本班增量 0 行（磁盘面 sha `4f986ec7143a690f…`／84 行／mtime 09:38:34，与 07 班终报锚点逐位同）⇒ **占领区摘要无新轴入占**；15 员池 PR 状态**维持 05/06 班在册"仍未获得"**，本班按 07 班在册禁烧面条款**未复测** `factor_signal`／`factor_feature_value`（三度同值）与 `ART_ROOT`。
- ⚑ **本班新面（对照基准更新，④席生成端与正交闸必读）**：分数册 84 行＝**65 个 distinct card_id**，其中 **6 对（12 行）是"母卡 ↔ `*_derived` 平行卡"逐字节同读数**——`rows[2,10]`（涨停家数）、`rows[3,11]`（跌停家数）、`rows[4,12]`（炸板率）、`rows[5,13]`（封板率）、`rows[6,14]`（连板最高高度）、`rows[7,16]`（净广度），全部挂在 `TDM-E-L1-S2` 一个节点上。机制＝`scripts/backtest/fexam/card_binding.py:364` 的 `*_derived` 回落分支把平行卡送回母卡同一枚本地 CSV ⇒ **相关系数 1.0 由码面构造保证，不是实测巧合**。
- ⇒ 独立信号清单分母更正：**独立经济命题＝65 − 6＝59**；在册 04 班"agg8 批 8 卡实占 2.13 轴"与本条**不可混用**（前者是不同卡之间的高相关，本条是同一枚序列被两卡读取）。按轴计量时，L1-S2 节点的涨跌停/广度族在"母卡＋平行卡＋level＋z20"四层里能提供的独立轴仍是 04 班在册的那 2.13 个，不因平行卡而增加。
- 在册 pass 面维持 06 班读数（全册 pass 仅 rows[76]/[78]，同落一根 `lu_count_z20` 轴，`corr=0.9998`）⇒ **独立通过轴仍＝1**，本班未升级任何行（铁律：fail 不升级；pass 两腿未过，见 04 班 §3 与在册修⑥/修⑨）。
- 空白轴地图判读面限定沿用：按 card_id 命名语义归类，本席未逐卡读卡体。
- 复跑尺＝`python .runtime/tmp/st-qoder-p09-1015-08/dup8_metrics_identity.py`（正对照 rows[2]≡rows[10]、负对照 rows[83] 独占；并把 06 班在册"同卡复跑"5 组单列为 `修④` 形，不与本条混计）。

## 2026-10-15 日更 ｜ st-qoder-p09-1015-09（⑨成绩官第九班：**独立命题分母 59→64；新 6 行零新轴入占；镜像簇首份点名 1 行**）

> 读面声明（本班正文原样跑）：分数册磁盘面 sha256=`009c7bbcf87582c2…`／123768B／docs=2／doc1 rows=**90**／mtime `2026-10-15 10:31:26`＝较 08 班终报锚点（`4f986ec7…`／84 行）**当日增量 6 行 rows[84..89]**（批 `p07a-sector6-20261015`）；index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`c7e5b1f8bfb9…`／105598B／75 行（与 06/07/08 班在册面逐位同）；HEAD 面该馆 `git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**。族口径＝卡体 `pillars_numeric` 键集，卡体 join＝卡内 `card_id`（90/90 命中）。本班未动分数册字节、未动任何阈值与门柱。

- **占领区摘要（本班新 6 行）**：市场级日频情绪指数（rows[85]）、RRG 象限迁移（rows[86]）、板块候选池边际/ablation（rows[87]）、业绩预增催化剂（rows[88]）、合成 z 分数 shock 面板（rows[89]）、四档风险分层（rows[84]）⇒ **全部落在已占轴，零新轴入占**。未占/稀薄轴维持 04 班在册方向（波动率期限结构、流动性/冲击成本、资金面分户、另类数据）——正交闸与 ③④ 席请优先去无人占的轴。
- **产量口径**：`90 行＝70 distinct card_id＝64 个独立经济命题`（扣 08 班在册 6 对逐字节同读数平行卡）。⚠ 08 班在册 59＝84 行面（65−6），本班 64＝90 行面（70−6），两数皆真、差＝本班 5 个新对象，引用者勿混面。
- **15 员池 PR（参与率/相关矩阵）**：**维持"仍未获得"**。本班按 07/08 班在册禁烧面条款**未复测** `factor_signal`/`factor_feature_value`（三度同值＝各 0 行）与 `ART_ROOT`；正交闸列名契约适配面与 PR 复跑配方仍在册（04 班 `to_impl.md` 修⑤ 正解改写＋`.runtime/tmp/st-qoder-p09-1015-04/pool6/`）。
- **本席位的新对照基准（④席生成端必读）**：分数册现值第一次出现**净/成本口径行**——rows[84..89] 六行的 `net_bucket_medians` 全负、`round_trip_cost_bp=25.0`，而**全册 90 行无任何一桶为正**（has_pos=0，尺＝`.runtime/tmp/st-qoder-p09-1015-09/probe9_net_and_rerun.py`）。⇒ 正交闸若开始用"扣费后可实现性"作筛选，现值面是**六行样本**、不是全册；存量 84 行是毛口径（NaN 净面）。跨代比较必须分账（详见 `to_impl.md` 修⑨ 追加面）。
- **镜像簇点名（呈批 P-6 的人工替代面）**：`mono_spearman ≤ −0.6 且 regime/oos 同号` 在全册命中 **1 行＝rows[87]**。若 P-6 裁"不加列"，此清单即每班唯一检索面。


## 2026-10-15 日更 ｜ st-qoder-p09-1015-10（⑨成绩官第十班：**对照基准新面＝comparison 族 OOS 配对面 10/10 无读数**；独立命题分母 64→65；零新轴入占）

> **读面声明（本班正文原样跑）**：判卷锚点＝快照 `.runtime/tmp/st-qoder-p09-1015-10/score_snapshot.yaml`（磁盘面 sha256 `d8a6fd8d52f749cecf73c8f02e931d936df020702bfc548bfb97778476cbf949`／129267B／docs=2／doc1 rows=**93**／mtime `2026-10-15 15:13:49`，较 09 班终报锚点 `009c7bbcf87582c2…`／123768B／90 行＝增量 3 行 rows[90..92]）。**本班写作期间册又长**：现值 `b0c9a370fcfc5b080c0b4171…`／130320B／rows=**94**／mtime `15:41:28`（第二快照 `score_snapshot_1542.yaml`）⇒ 本班追加判 rows[93]，**实判 4 行**。index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`009c7bbcf87582c2…`／rows=**90**（09 班磁盘终面已被吸收入 index）；HEAD 面该馆 `git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**。本班未动分数册任何字节、未动任何阈值与门柱。

- **占领区摘要（本班 4 行）**：rows[90]/[91]/[92] 全落**同一张已占卡**（五级熔断状态机 vs 二值全清＝风控阶梯轴，09 班在册已计）；rows[93]＝减仓参与率对次日价格路径＝已占价量/成交压力轴 ⇒ **零新轴入占**。未占/稀薄轴维持在册方向＝波动率期限结构、流动性与冲击成本、资金面分户、另类数据。
- **产量口径**：`94 行＝71 distinct card_id＝65 个独立经济命题`（扣在册 6 对逐字节同读数平行卡）。⚠ 09 班在册 64＝90 行面（70−6）、本班 65＝94 行面（71−6），差＝rows[93] 一个真新对象，两数皆真、引用者勿混面。
- **④席生成端与正交闸必读的新对照基准（本班首份账）**：分数册**对照/消融族的 OOS 侧从未有过读数**——10 行双臂行（rows[17]/[44]/[45]/[66]/[67]/[68]/[69]/[70]/[71]/[92]）`ic_delta_oos` **10/10 全 NaN**，7 行的唯一败根即此。⇒ 任何"该风控命题 OOS 已验/OOS 不稳"的叙述都**无册面依据**；正交闸若按"OOS 通过"筛轴，comparison 族贡献应为 **0 根已验轴**，不是 12 行。尺＝`python .runtime/tmp/st-qoder-p09-1015-10/replay10_dualarm.py 0 92`（PROBLEMS 0）。
- **15 员池 PR（参与率/相关矩阵）**：**维持"仍未获得"**。本班按 07/08/09 班在册禁烧面条款**未复测** `factor_signal`/`factor_feature_value`（三度同值＝各 0 行）与 `ART_ROOT`；04 班列名契约适配面与 PR 复跑配方仍在册。
- **在册叙述值 4.4**（`research_production_line_policy.md:274`）继续标"**未复现**"（本席累计七班无任何产物可再现该数）。
- **镜像簇点名（P-6 人工替代面续条）**：本班新行无镜像形（rows[93] `mono_spearman` 无面），全册命中仍＝**1 行 rows[87]**。
- 空白轴地图判读面限定沿用：按 card_id 命名语义归类，本席未逐卡读卡体（本班例外＝卡 07 与 02_dualwindow 两张读过卡体全文）。

## 2026-10-15 16:5x ｜ st-qoder-p09-1015-11（⑨成绩官第十一班·每日维护行）

- **本班工具实跑**（非引用在册）＝`python scripts/backtest/fexam/signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool6 --out .runtime/tmp/st-qoder-p09-1015-11/pool6_report_11.json` → `n_members=6 n_common_dates=1855 effective_n_signals(PR)=2.1272`，rc=0。⇒ **PR 与 04 班在册逐位同＝同池同人同值的复现确认，不是新增读数**；本班未新建池面。相关矩阵已落 `.runtime/tmp/st-qoder-p09-1015-11/pool6_report_11.json`（键面：`correlation_matrix`/`effective_n_signals`/`eigenvalues`/`kind`/`members`/`n_common_dates`/`n_members`）。
- **正交闸准入基准沿用**：`|corr|<=0.3`（工具契约在册）。本班从 `pool6_report_11.json` 直读一例：`avg_abs_ret` ↔ `avg_abs_ret_z20` corr=**0.7399**（>0.3 ⇒ 同轴变体不占独立名额）；`avg_abs_ret` ↔ `lu_count_z20` corr=**0.1331**（<=0.3 ⇒ 可视为独立候选）。⚠ 这仍是**6 员适配池**，不是 ①②班派单所指的 **15 员池**。
- **15 员池缺席如实注明（未重烧）**：`c1_market.factor_signal`/`factor_feature_value` 各 **0 行**（三度同值禁烧面，本班未测第四次）；`ART_ROOT=docs/_working/integrated_backtest/` 按 05 班在册为不存在目录，本班未复查。⇒ 本表对 ④ 席生成端的对照基准**仍只能覆盖 6 员适配池面**，15 员池 PR 无源；在册叙述值 4.4（`research_production_line_policy.md:274`）继续标"**未复现**"。
- **本班新增对照事实（供 ④ 席，属分面非池面）**：分数册新行 rows[94] 所在节点 `TDM-P-P2-04`（盘口/仓位族）与 rows[95] 所在 `TDM-E-L9-A01`（动量截面轴）**均不在 `pool6` 六员之内** ⇒ 正交闸对本班两行对象**无从对照**，如实报"闸对该两对象未开"，勿把"未触发"读成"已判独立"。


## 2026-10-15 ｜ st-qoder-p09-1015-12（⑨成绩官第十二班·每日维护行：增量 0 行＝零新轴入占；pool-report 复现＋首份"族×verdict"分账）

> 读面声明（本班正文原样跑）：磁盘面 sha256 `d77773545f5b4cc7c8c64686a8aab8e2c672a540740e843da953f4e3186d0c9c`／132248B／docs=2／doc1 rows=**96**／mtime `2026-10-15 16:28:53`＝与 11 班终报锚点**逐位同** ⇒ **本班增量 0 行**；index `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`009c7bbcf87582c2…`／123768B／**90 行**（落后磁盘 6 行／8480B，自 11 班起未动）；HEAD 该馆 **0 件**。本班未动分数册任何字节、未动任何阈值与门柱。族口径＝卡体 `pillars_numeric` 键集，join＝卡内 `card_id`（96/96）。

- **本班工具实跑**（非引用在册）＝`python scripts/backtest/fexam/signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool6` → `n_members=6 n_common_dates=1855 effective_n_signals(PR)=2.1272`（rc=0），落 `.runtime/tmp/st-qoder-p09-1015-12/pool6_report_12.json`。pool6 六枚 CSV mtime 皆 `07:30` 未变 ⇒ **PR 与 04/11 班逐位同＝同池同人同值复现确认，非新增读数**；本班未新建池面。
- **占领区摘要**：本班增量 0 行 ⇒ **零新轴入占**；未占/稀薄轴维持 04/09 班在册方向（波动率期限结构、流动性与冲击成本、资金面分户、另类数据）。
- **首份"族×verdict"分账（④席生成端与正交闸必读，本班 `measure12.py` 直测、非派生）**：96 行按卡体 `pillars_numeric` 键集分族＝**校准 61／事件 23／对照 11／maxdd_min 变体 1**；交叉 verdict＝校准 `{fail 59, pass 2}`、事件 `{fail 23}`、对照 `{fail 9, blocked 2}`、变体 `{fail 1}`。⇒ **全册唯二 pass（rows[76]/[78]）全落校准族同一根 `lu_count_z20` 轴（corr=0.9998），事件族 23 行 0 pass、对照族 11 行 0 pass**：除校准这一根涨跌停广度轴外，生产线至今**没有任何族产出过一个通过对象**。此为家族级矿位成熟度信号；本班增量 0 ⇒ 零新开单，仅入分账供 ④ 席判"事件族是否近 mined_out"。
- **15 员池 PR 缺席如实注明（未重烧）**：`c1_market.factor_signal`/`factor_feature_value` 各 0 行（三度同值，本班未第四次重烧）；`ART_ROOT=docs/_working/integrated_backtest/` 未复查；在册叙述值 4.4（`research_production_line_policy.md:274`）继续标"**未复现**"（本席累计八班无产物可再现该数）。
- 空白轴地图判读面限定沿用：按 card_id 命名语义归类，本班未逐卡读卡体（例外＝轮一抽的 rows[0]/[44]/[46] 三张回过卡体）。


## 2026-10-15 ｜ st-qoder-p09-1015-13（⑨成绩官第十三班·每日维护行：增量 0 行＝零新轴入占；pool-report 复现＋**事件族 OOS 确认柱可达性首份账**）

> 读面声明（本班正文原样跑，终报前重测）：磁盘面 sha256=d77773545f5b4cc7c8c64686a8aab8e2c672a540740e843da953f4e3186d0c9c／132248B／docs=2／rows=96／mtime `2026-10-15 16:28:53`＝与 12 班终报锚点**逐位同** ⇒ **本班增量 0 行**；index `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`009c7bbcf87582c2…`／123768B／**90 行**（落后磁盘 6 行，自 11 班起未动）；HEAD 该馆 **0 件**。本班未动分数册任何字节、未动任何阈值与门柱。族口径＝卡体 `pillars_numeric` 键集（逐字复用 12 班在册 `measure12.py` 的 `family_of`），join＝卡内 `card_id`（96/96）。

- **本班工具实跑**（非引用在册）＝`python scripts/backtest/fexam/signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool6 --out .runtime/tmp/st-qoder-p09-1015-13/pool6_report_13.json` → `n_members=6 n_common_dates=1855 effective_n_signals(PR)=2.1272`（rc=0）；pool6 六枚 CSV mtime 皆 `07:30` 未变 ⇒ **PR 与 04/11/12 班逐位同＝同池同人同值复现确认，非新增读数**。
- **占领区摘要**：本班增量 0 行 ⇒ **零新轴入占**；未占/稀薄轴维持 04/09 班在册方向（波动率期限结构、流动性与冲击成本、资金面分户、另类数据）。
- ⚑ **给 ③④ 席与正交闸的新事实（原因层，本班直测、尺＝`python .runtime/tmp/st-qoder-p09-1015-13/measure13d.py`）**：**事件族 23 行的"OOS 同号确认"柱在当前冻结窗下数学不可达**＝卡面 OOS 窗逐字相同（23/23＝`2024-01-01..2025-09-09`，实测面总日数 **410**），而族内下限把"≥200 事件日"同时套在**被用来确认的那一窗**（`scripts/backtest/fexam/calibration_exam.py:843`、`:873-875`），⇒ 需要事件密度 **≥48.8%**；实测该族 OOS 事件日 79–165（密度 19.3%–40.2%）、IS 侧 239–363（**23/23 过线**）。⇒ 12 班在册"事件族 23 行 0 pass"的**原因不是信号弱，而是门槛×窗长的可达性**：同一枚 200 下限套在 IS 窗 1212 日只需 16.5% 密度、套在 OOS 窗 410 日需 48.8%。**对新卡的可执行含义**＝若沿用该 410 日 OOS 窗＋稀疏事件定义（<50% 覆盖），此柱必拦、该卡不可能 pass；本席不动门柱，题面已按呈批 **P-9** 交裁（选项与代价见 `to_impl.md` 本班节）。
- **15 员池 PR 缺席如实注明（未重烧）**：`c1_market.factor_signal`/`factor_feature_value` 各 0 行（三度同值，本席未第四次重烧）；`ART_ROOT=docs/_working/integrated_backtest/` 未复查；在册叙述值 4.4（`research_production_line_policy.md:274`）继续标"**未复现**"（本席累计九班无产物可再现该数）。
- 空白轴地图判读面限定沿用：按 card_id 命名语义归类，本班未逐卡读卡体（例外＝轮一抽的 rows[48]/[55]/[60] 三张事件卡读过卡体 `pillars_numeric` 与 `window`）。


## 2026-10-15 ｜ st-qoder-p09-1015-14（⑨成绩官第十四班·每日维护行：增量 0 行＝零新轴入占；pool-report 复现＋**断链"面积 vs 阻断"分面首份账**）

> 读面声明（本班正文原样跑，终报前重测）：磁盘面 sha256 `d77773545f5b4cc7c8c64686a8aab8e2c672a540740e843da953f4e3186d0c9c`／132248B／docs=2／doc1 rows=**96**／mtime `2026-10-15 16:28:53`＝与 13 班终报锚点**逐位同** ⇒ **本班增量 0 行**；卡池按卡内 `card_id` 字段 join＝**552**（=卡文件数 552），96 行 join **96/96** 零缺失；index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 与 HEAD 该馆面沿 13 班在册（本班未复查，避免与他席在途袋对撞）。本班未动分数册任何字节、未动任何阈值与门柱。

- **本班工具实跑**（非引用在册）＝`python scripts/backtest/fexam/signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool6 --out .runtime/tmp/st-qoder-p09-1015-14/pool6_report_14.json` → `n_members=6 n_common_dates=1855 effective_n_signals(PR)=2.1272`（rc=0）；pool6 六枚 CSV mtime 皆 `2026-10-15 07:30` 未变（本班 `stat` 直读）⇒ **PR 与 04/11/12/13 班逐位同＝同池同人同值复现确认，非新增读数**；本班未新建池面。
- **占领区摘要**：本班增量 0 行 ⇒ **零新轴入占**；未占/稀薄轴维持 04/09 班在册方向（波动率期限结构、流动性与冲击成本、资金面分户、另类数据）。
- **15 员池 PR 缺席如实注明（未重烧）**：`c1_market.factor_signal`/`factor_feature_value` 各 0 行（三度同值，本席未第四次重烧）；`ART_ROOT` 未复查；在册叙述值 4.4（`research_production_line_policy.md:274`）继续标"**未复现**"（本席累计十班无产物可再现该数）。
- ⚑ **给 ④ 席生成端与正交闸的新对照基准（原因层，本班直测）＝断链的"面积"与"阻断"差 39 倍，勿按引用数开单**：552 卡中 **84 卡（15.2%）** 卡体含指向已删 `docs/_working/**` 的路径、覆盖分数册 **39/96 行（40.6%）**，但键级分面显示引用几乎全落在溯源字段（`status_reason 60／mother_score_row 28／data_window_evidence 18／same_family_precedent 18／basis_casefile 16／paper_trail 10`），**机器字段命中仅 3 卡**；全册**执行阻断仍只有 rows[90] 一枚**（双臂 book_channel 经 `card_binding.py:1761` → `exit_simulator.py:122 load_indicator` → 旧址 `SCORES_YAML`）。⇒ 正交闸与生成端据此须知：**这 39 行的读数是有效的**（断的是证据回溯，不是输入），而"对照族 11 行 0 pass"里那 2 行 blocked **与信号有效性无关**（本版对照族说明）。尺＝`.runtime/tmp/st-qoder-p09-1015-14/measure14b_cards.py`＋`measure14c_keyface.py`（只读、内置三对照）。
- **在册事实续供下一班（勿重查）**：`comparison_exam.py`（OD-1 执行器，`book_channel:` 文案唯一发射点＝`:270/:274/:277`）三面＝**HEAD 无／index 无／磁盘 `??` 未跟踪**；`signal_orthogonality.py`＝HEAD 无／index 有（`AM`）⇒ 本班能跑的是**磁盘面**，任何从 HEAD 起跑的车道这两个工具都**不存在**。
- 空白轴地图判读面限定沿用：按 card_id 命名语义归类，本班未逐卡读卡体（例外＝轮一抽的 rows[76]/[78]/[66] 三张回过卡体 `pillars_numeric`）。


## 10-15 19:30 ｜ st-qoder-p09-1015-15（⑨成绩官第十五班·独立信号清单）

- 工具实跑＝`python scripts/backtest/fexam/signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool6` → `n_members=6 n_common_dates=1855 effective_n_signals(PR)=2.1272`（rc=0）＝**在册同值复现，非新读数**（04 班首测，11/12/13/14 班复现）。
- ⚠ 本班对"对照基准"的一条实质更正：分数册新增四张对照卡（rows[96..99]）**不构成 4 条独立信号**＝四卡只产出 **2 个读数面**（rows[96]≡rows[97] 整块 metrics 相等；rows[98]/[99] 差 8.5e−5），且两枚 target 腿卡读数落在对侧血统量级（尺与证据＝to_impl.md 修㉑）。⇒ 给 ④ 席生成端与正交闸的口径＝**独立信号分母不因这批 +4，最多 +0**。
- 在册尺面计数更新（本班直测）＝跨卡同读数簇 **7**（08 班尺原样跑现值面）；同号负向簇 **17 行／14 卡**。
- 15 员池物化面＝在册禁烧面（`c1_market.factor_signal`／`factor_feature_value` 各 0 行，03–11 班三度同值），本班**未重烧**。


## 10-15 20:08 ｜ st-qoder-p09-1015-16（⑨成绩官第十六班·独立信号清单）

- 工具实跑＝`python scripts/backtest/fexam/signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool6` → `n_members=6 n_common_dates=1855 effective_n_signals(PR)=2.1272`（rc=0）＝**在册同值复现，非新读数**（04 班首测，11–15 班复现）。本班未新建池面；15 员池物化面＝在册禁烧面（`c1_market.factor_signal`／`factor_feature_value` 各 0 行），本班**未重烧**。
- 本班增量 0 行 ⇒ **零新轴入占、独立信号分母不变**（在册口径：分母只随"新对象首轮＋读数面可区分"增长；15 班已定 rows[96..99] 四卡只 2 面 ⇒ 那批 +0，本班不重复计）。
- ⚑ **给 ④ 席生成端与正交闸的本班直测（原因层）＝"某柱从未被评估"要先算方向性再谈独立面**：全册冻 `ic_ir_min` 的 **69** 行里机判过 **14（20.3%）**、无面 **55**；但无面行的其余四柱**逐一有面**（`face_when_noface={4: 55}`），而缺一根否决柱**只可能放宽、不可能加严**⇒ 真正受影响的判语面＝**唯二 pass 行 rows[76]/[78]**。生成端据此知：**这 55 行的 IC 读数面本身有效**（mono/regime/oos/ic_mean 四脚齐），不必把它们当"废分"重挖。
- 尺与对照（可复跑）＝`.runtime/tmp/st-qoder-p09-1015-16/measure16_icir_coverage.py`（只读）；负对照 `ic_ir_min_typo`→`rows_with_pillar=0`，正对照 `mono_spearman_min`→`69 行／机判 55（79.7%）／无面 14`（与 ic_ir 的 14 显著不同＝尺有判别力）。
- 三面可用性提示（给从 HEAD 起跑的车道）＝`calibration_exam.py` 与 `comparison_exam.py` 在 **HEAD/index/磁盘** 三面各缺一条腿（详见本席 ledger 16 班 §4/§5＋两条 [BLOCKER]）；`signal_orthogonality.py` 本班跑的是**磁盘面**。
