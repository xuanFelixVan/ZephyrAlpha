---
ttl: task_bound
completes_when: "波 3.1/3.6/3.7 红证全绿并登记需求，案卷经进程外核实"
---

# 数据链案卷 · 波 3.1 / 3.6 / 3.7（车道 st-final-build-20260926 · dev）

## 0. 案卷头部四字段

- **turn_budget**: 名义 12 工具调用 / 实耗 15（调研 6、落盘 9）；单块调研均 ≤6 次，第 8 次调用内已出本册骨架（首版 55 行）。
  超因=3.6 的 "score" 宿主与 3.7 的越界件需多一轮定点定位，未做全仓撒网。
- **verified**（本车道实读/实测，命令原文见 §E）
  - V1 两个 FAILED 崩溃点在 HEAD 面确为裸混型：`consensus_daily_compute.py:146-147/155/157`、
    `financial_derived_compute.py:397/399`（`git show HEAD:…` 原句逐行核，见 §E-5）。
  - V3 `ch_reader` 严格读数通道**已落地**（`src/zephyr/data/ch_reader.py:47` 红线原文
    "判据类读数一律 query_rows / count_strict / ch_probe 三选一"，`:239 def query_rows`），
    故 3.6 的临时探针**不新建**（内收），`_last_trading_day` 直接改道 query_rows。
  - V4 口径尺实测：`[enforced] 命中 0 行` / `[pending 越界] 命中 8 行`（清单见 §3.7）。
  - V5 全部红证：`tests/data/test_wave3_*.py` + 三个邻居尺 = **66 passed / 0 failed**（§E-6，末次跑）。
  - V6 两本 YAML 改后仍可解析（`yaml.safe_load` 双 ok，§E-7）。
  - V7 本包写域足迹（`git status --porcelain`）＝改 5 件 + 新增 6 件，**无越界路径**（§E-8）。
- **assumed**（未实测，禁当结论引用）
  - A1 `reconciliation_differences` "两库皆空"＝G 册第 8/12 条快照，本包**零 CH/DuckDB 实读**，
    故 3.6 的该处只交付"判据件 + 红证"，宿主接线列缺口。
  - A2 "score" 那处真源的宿主文件未定位（G 册/02 册仅列名不指件）→ 不自赋指向。
  - A3 `consensus_daily` 6,797,719 行 / max=2026-09-14 等表读数引自 G 册，未复算。
- **input_set_disjoint_with**: 兄弟包 3.0（CH strict 复测，与本包共用 ch_reader 但改点不同件）、
  3.2/3.3（task_runs/供数守恒）、3.4（Fill 写者）、3.5（空壳表三分）、3.8（HEAD 常红尺）、
  3.9（hfq 独占尺）、3.10（图12）；域外件 `ex_core/`、`backtest/`、`frontend/`、`trading/`、
  `reporting/`、`docs/01_policies_and_standards/**`（全部只读）。
- **evidence_ref.cmd**: §E 全 8 条（可重放，含 PYTHONPATH 前置）；本册所有读数均为命令原文+实抄输出。

> 并发告警（不判因果，只报现象）：本车道工作树在同一次批量执行内出现过
> "同一内容先 1 failed、隔一轮无改动重跑即 66 passed"，且 §E-4 的改前反例跑到的行号内容与
> 当时 Edit 后的文件态不一致——疑似车道内快照/stash 机制在中途回灌（AGENTS §2.8 在册）。
> 处置=末轮以 `git status` + 全文重跑双核（V5/V7），并保留 §D 的改前反例原始 trace 作时间戳证据。

## 3.1 `'str' > 'date'` 入口类型归一（Z-15 / W-34）

**判据（抄波 3.1 原文）**：红证=喂 ISO 字符串与 date 两种入参都必须能跑通且比较结果一致 + 两表回归。

**新件（归一唯一宿主）**：`src/zephyr/data/date_normalize.py`
- `as_iso_day / as_date_obj / iso_window_bound / in_window`；仅 stdlib；**失败必抛**（None/""/非 ISO/非日期类型），
  唯一合法哨兵=None→`""`（沿用两计算核既有"空=不限"口径，不另立第二套）。
- 内收声明：吸收两计算核原先各自内联的"字符串窗口裸比"（替代内联写法）；
  **不**并 provider 侧 `_norm_date_str/_norm_date_strict/_norm_date`（对象=源报文列→表列，非窗口比较键）。

**改点（文件:行号，工作树态）**
| 文件 | 行 | 内容 |
|---|---|---|
| `src/zephyr/data/implementations/consensus_daily_compute.py` | 44 | 顶层 `from zephyr.data.date_normalize import as_date_obj, as_iso_day, iso_window_bound` |
| 同上 | 150 | `sorted(trade_dates, key=as_iso_day)`（原 `sorted(trade_dates)` 混型即崩） |
| 同上 | 151-152 | `lo_iso/hi_iso = iso_window_bound(start/end)`（原 `start or ""` 假定全链 str） |
| 同上 | 156-157 | 发布日排序键与 bisect 比较键双双 `as_iso_day`（原裸喂 `r["publish_date"]`） |
| 同上 | 159-163 | `td_iso = as_iso_day(td)` 后再比边界 |
| 同上 | 164-166 | `window_lo` 先 `as_date_obj(td)` 再减窗（原 `td - timedelta` 假定 td 必为 date） |
| 同上 | 194-196 | **出参列** `last_rep` 也归一为 ISO str（禁同列混 date/str 落 CH） |
| 同上 | 338 | `start = min(归一键…, default=None)`（原 `min(r["publish_date"] …)` 混型崩 + 空列表 ValueError） |
| `src/zephyr/data/implementations/financial_derived_compute.py` | 391 | 惰性 import（随本件懒加载口径） |
| 同上 | 394-395 | 边界归一 |
| 同上 | 402-411 | 窗口过滤"两侧同型后比"（替代原 397/399 裸比；无边界时不触碰行值，保留 None 行旧通过语义） |

**before → after**
- before（HEAD 原句，§E-5 取）：`lo_iso = start or ""` / `hi_iso = end or ""` / `td_iso = td.isoformat()` /
  `if hi_iso and td_iso > hi_iso` / `if start and row["announce_date"] < start`。
- after：同位置改为归一键比较；实测两表在 str/date/混型三种入参下行集全等且非空。

**红证**：`tests/data/test_wave3_date_normalize.py`（9 测，§E-3）
① 反例：`"2026-01-08" > date` 与 `date < "2026-01-08"` 必抛 TypeError（改前形态留案，另见 §D 真实 trace）；
② 三载体同键（date / ISO str / `YYYY-MM-DD HH:MM` / `2026/01/05`）+ 六类坏值必抛；
③ **表 1 c3_fundamental.consensus_daily**（纯函数核直测）：同窗 str 边界与 date 边界输出全等且非空；
  发布日混型（同列 date+str 共存）与全 str 同果；
④ **表 2 c3_fundamental.financial_derived**：monkeypatch `load_versions` 造合成三表 store（零 IO），
  `run_compute` 在 str / date / 混型三种边界下 FetchResult 行集全等且非空，窗口外必空（防恒真假绿）。

**缺口**：① 采集/夜间真跑（`build_consensus_daily.py --check`、`build_financial_derived.py --check`）需
`config/.env.clickhouse`，本车道无该件 → 两表"实库回归"未做，仅纯核回归；② `pit_query.py:110` 的
`financial_derived→report_period` 读取面未涉混型（本轮未发现崩点），未改。

## 3.6 三处真源收敛（Z-18 / W-36）

**判据（抄波 3.6 原文）**：双源皆空不得判"空即干净"；红证=一源有一行另一源空 ⇒ 必红。

**新件（判据唯一宿主）**：`src/zephyr/data/dual_source_guard.py`
`pair_status` / `classify_source_pair` + `SOURCE_PAIR_RED={read_unavailable, both_empty, one_sided}`；
三铁律=读失败≠零行 / 双空≠干净 / 单侧空即分裂（禁降级 warn）；不落库不告警不查 DB（不与宿主抢真源）。

**界内接线**：`src/zephyr/data/consensus_crosscheck.py`
- `:140` import；`:160-173` 族 1 双源前置判据，红态 `_classify(..., ok=False, warn=False)` 并带点名 detail；
- `:177` `from scipy import stats` 下移到真要算秩相关处（红路径免重依赖，也让无 scipy 环境可跑红证）；
- `:122-128` `_last_trading_day` 由 `ch_reader.query()` + `rows[0][0][:10]` 直取（W-180 点名禁法）
  改 `ch_reader.query_rows()` 严格通道 + 读空必抛 RuntimeError（禁"读空当无缺口"）。

**before → after**：改前两源同为 0 行与"query 返回 None（读失败）"在 `n<30` 分支里都只按 `warn=n>=100`
分类，detail 仅"共同键仅 0"；`raw=None` 被 `_load_tsv_rows(raw or "")` 静默吞成零行 ⇒ 假绿面。
改后三形态各出点名 detail、一律 fail。

**红证**：`tests/data/test_wave3_dual_source_guard.py`（8 测，monkeypatch `ch_reader.query`，零真库）
判据件：双空⇒`both_empty`+`clean is False`+detail 含"空≠干净"；**一源 1 行一源 0 行⇒`one_sided` ∈ SOURCE_PAIR_RED**；
`raw=None`⇒`read_unavailable`（"读数通道失败"点名）；皆有行⇒`ok`/clean。
宿主集成：正向/反向单侧空⇒`status=="fail"`；双空⇒fail 且 detail 点名"空≠干净"；双读失败⇒fail；
双源有行⇒不误红（`agg` 无 `pair_status`）。

**缺口（越界/未定位，禁越界改）**
1. `reconciliation_differences`：宿主在 `src/zephyr/trading/recon_runner.py:381`（`if not rows:`）与
   `src/zephyr/reporting/reconciliation_schema.py:42`（表 DDL），**均在本包写域外**；
   建议其对 governance.db 与 CH `c1_market.reconciliation_differences` 两侧读数调 `classify_source_pair`。
2. "score" 第三处：宿主未定位（A2），不自赋路径。
3. `consensus_crosscheck` 其余检查族（族 2 `check_freshness` 起）仍存 `query()` 下标直取，需按 W-180 逐条迁 `query_rows`。

## 3.7 miniQMT 口径四件 + 回退哨兵尺（Z-19 / W-37）

**在册正确口径**（尺内常量 `CALIBER_TRUE`＝表述唯一真源，文档引用它不各抄一遍）：
`miniQMT 仅实盘通道退役；模拟盘的分钟/tick 唯一源仍是在用状态`。

**现读四件当前写法（工作树实读，§E-4）**：G 册点名的四件 HEAD/工作树**仍全在旧口径**
（印证 00 册 W-37 状态"🔨被回退"），尺实测 8 行命中：
`ex_core/miniqmt_channel_manager.py:58,59`（"通道退役冻结"／"XtMiniQmt.exe 全面清退"）、
`backtest/implementations/ch_tick_replay.py:19`（"miniQMT 退役后断供"）、
`frontend/dashboard/web/features/bridge/br-page.js:54,63`（"miniQMT 已退役"）、
`frontend/dashboard/web/pages/bridge.html:3`（"券商全面清退"）、
`docs/_working/automation/campaign/HANDOFF_20260921_ab_league.md:16,38`（"下线"变体）。
**五件全在本包写域外 → 只交点清单，未改一字。**

**界内改点（把旧口径改对，同时不触任何阈值/状态字段）**
- `src/zephyr/data/config/known_data_gaps.yaml:19-21` 原"9/18 miniQMT 清退后…"→
  "9/18 miniQMT 仅实盘通道退役（在册正确口径：模拟盘的分钟/tick 唯一源仍是在用状态）；本 API 经大QMT 沙箱可用…"，
  并把续行"miniQMT 清退后的已验证替代"→"实盘退役后的已验证替代"；
- 同件 `:928`（dividend_incremental root_cause）"9/18 miniqmt 清退同款病…源退役后任务空挂"→
  "仅实盘退役同款病（模拟盘分钟/tick 供数仍在用）…源实盘退役后任务空挂"；
- 同件 `:1309` "miniQMT 实盘端 2026-09-18 券商清退"→
  "miniQMT 仅实盘端 2026-09-18 券商清退（模拟盘分钟/tick 唯一源仍是在用状态；穿透式监管，93 号备忘）"；
- `src/zephyr/data/config/data_supply_sentinel.yaml:12-13` "股东户数表 2026-07 断供两月无人知（miniqmt 清退后任务空挂）"→
  "停更两月无人知（miniqmt 仅实盘退役、模拟盘分钟/tick 仍在用时该任务空挂）"；
- 同件 `:597-598` "miniQMT 09-18 清退后**无在跑供给通道**"→
  "miniQMT 仅实盘通道 09-18 退役（模拟盘分钟/tick 唯一源仍是在用状态），故实盘侧 tick_data 无在跑供给通道"。

**哨兵尺**：`src/zephyr/data/miniqmt_caliber_sentinel.py`
行级三条件才开火：①同行点 miniQMT 主题（`miniqmt|mini qmt|xtmini`）②出现旧口径词
（`全面清退|已退役|清退|退役冻结|断供|无在跑供给通道|退役后转历史|通道退役冻结|下线`）
③无范围限定词（`仅实盘|模拟盘|实盘…退役|实盘通道`）——禁扩全文模糊匹配（误报会逼后人放宽尺）。
分级：`ENFORCED_FILES`（界内 2 件，硬零容忍）/ `PENDING_HANDOFF_FILES`（写域外 5 件，只报现状不判红，防连坐），
`python -m …` CLI 在 enforced 非零时 exit 1。

**红证**：`tests/data/test_wave3_miniqmt_caliber.py`（7 测）——四条旧口径⇒四行开火；两种正确写法⇒零开火；
非 miniQMT 主题的"断供"不误伤；**tmp_path 临时件喂旧口径 ⇒ `len(findings)==1` 且 lineno/原行相符，
补上范围限定词 ⇒ `==[]`（回退即红的自证）**；`enforced_findings()==[]`；pending 清单不指空路径；尺自述不被自家尺开火。

**缺口**：① 越界五件文案待兄弟道落地，落地后须删 `PENDING_HANDOFF_FILES` 对应条（防清单腐烂成第二真源）；
② `br-page.js:63` 原行含全角引号，本册转写与磁盘字节可能有字符级差，复核以 `scan_file` 输出为准；
③ 界内两件之外的 `src/zephyr/data/**` 文案面（如 `backfill_checker.py:681` "miniqmt 近期持续拒连"）
经判据判定为"通道现状描述"非口径断言，未纳尺、未改。

## D. 改前反例原 trace（3.1 案卷硬证据，§E-4 同批跑）

```
src/zephyr/data/implementations/financial_derived_compute.py:399: in run_compute
    if start and row["announce_date"] < start:
E   TypeError: '<' not supported between instances of 'str' and 'datetime.date'
src/zephyr/data/implementations/consensus_daily_compute.py:155: in build_consensus_rows
    if hi_iso and td_iso > hi_iso:
E   TypeError: '>' not supported between instances of 'str' and 'datetime.date'
```
（与 G 册第 7 条记的两条 task_runs FAILED 消息**逐字同型**：`consensus_daily_build` FAILED@2026-09-18T22:30:20Z `'>'…`、
`financial_derived_build` FAILED@2026-09-25T21:32:12Z `'<'…`。）

## E. 证据命令原文（可重放）

```bash
# 前置（每个新 shell）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926
export PYTHONPATH="D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src;D:/ZephyrAlpha/.aidrafts/st-final-build-20260926"
python --version            # 3.12.8

# 1 本包三测 + 邻居尺（consensus 纯核 / financial_derived 纯核 / supply_sentinel 消费方）
python -m pytest tests/data/test_wave3_date_normalize.py tests/data/test_wave3_dual_source_guard.py \
  tests/data/test_wave3_miniqmt_caliber.py tests/scripts/test_build_consensus_daily.py \
  tests/zephyr/data/test_financial_derived_compute.py tests/zephyr/data/test_supply_sentinel.py -q
#   末次实测：66 passed in 2.54s
# 2 全 data 测试目录连带回归
python -m pytest tests/data -q      # 实测：612 passed / 1 failed / 1 skipped in 35.43s
#   唯一红件=tests/data/test_internal_compute_provider_cohort_daily.py::test_route_builds_per_trading_day_and_aligns_columns
#   根因日志：CLICKHOUSE_HOST 未配置 + cohort_daily_writer CH 写入失败 fail-open（alt_data 域，本包零触碰，见 §G）
# 3 本包三测单独跑（24 测：9 + 8 + 7）
python -m pytest tests/data/test_wave3_date_normalize.py tests/data/test_wave3_dual_source_guard.py \
  tests/data/test_wave3_miniqmt_caliber.py -q                       # 实测：24 passed
# 4 改前反例（同一批 pytest 抓到 §D 两条 TypeError）+ 口径尺
python -m zephyr.data.miniqmt_caliber_sentinel        # 实测：[enforced] 命中 0 行；[pending 越界] 命中 8 行
# 5 HEAD 面 before 态锚点
git show HEAD:src/zephyr/data/implementations/consensus_daily_compute.py   # :146/147/154/155/157/159 裸 str 比
git show HEAD:src/zephyr/data/implementations/financial_derived_compute.py # :397/399 裸混型比
# 6/7 绿态与 YAML 可解析性：同 §E-1 输出 + yaml.safe_load 双 ok
# 8 写域足迹
git status --porcelain src/zephyr/data tests/data docs/_working/total_command_closeout/wave3
#   M ch_reader.py / ch_writer.py（**他会话在途件，本包零触碰**）
#   M config/data_supply_sentinel.yaml / config/known_data_gaps.yaml / consensus_crosscheck.py
#   M implementations/consensus_daily_compute.py / implementations/financial_derived_compute.py
#   ?? wave3/ ?? date_normalize.py ?? dual_source_guard.py ?? miniqmt_caliber_sentinel.py
#   ?? tests/data/test_wave3_{date_normalize,dual_source_guard,miniqmt_caliber}.py
```

## F. 会话收尾状态

未 commit / 未 add / 未 enqueue（本包硬禁）；全部改动留在车道工作树。
DB 侧：零写、零 DDL、零 DELETE/UPDATE、零 mv/DETACH/RELOAD；判据类读数不走 `query()` 字符串下标直取
（族 1 走显式 raw 存活判据，`_last_trading_day` 改 `query_rows`）。

## G. 环境红件（非本包因果，未动）

`tests/data/test_internal_compute_provider_cohort_daily.py::test_route_builds_per_trading_day_and_aligns_columns`
红因日志原文＝`CLICKHOUSE_HOST 未配置…` + `cohort_daily_writer[...] CH 写入失败 fail-open`，
属 `alt_data/cohort_daily` 域（本包零触碰）的 CH 配置依赖红。本包未改它、未 skip、未放宽任何断言。

## H. 本包登记需求（逐件）

> **路径冲突处置（重要，禁第二真源）**：`docs/_working/total_command_closeout/wave3/registration_needs.yaml`
> 实测已是**兄弟道（波 3.2/3.3）生成器在管件**——`generated_by: scripts/governance/data_supply/gen_registration_needs.py`、
> `note_zh: 现读现出，禁手工增删条目`（`generated_at_utc 2026-09-26T13:01:25Z`，且其内容已把本包登记需求
> 指向自身）。本包一度按任务书直写该路径，随即被其生成器重跑覆盖＝**该件真源归生成器**，
> 故本包不再覆写它，改随本册 §H 递交登记需求，请登记面/生成器宿主吸收（下节逐件字段与任务书要求一一对齐）。

| file | kind | creation_token 建议 capability | 翻译 name-zh / plain-zh（≥8 字） | depgraph module_id + 域 | ALGO-NOTE-SYNC 同批 | 克隆风险 |
|---|---|---|---|---|---|---|
| `src/zephyr/data/date_normalize.py` | source | `date_window_type_normalization` | 日期窗口比较键归一 / 把写成字符串的日期和真日期先折成同一天再比大小，避免程序在比较时当场崩 | `zephyr.data.date_normalize` / `_domain_data`（两计算核新增依赖边，须 `--force` 重建） | 不需要（未挂 TDM module_ref；挂则代码与 algo_note_zh 同批） | 近似件已点名不并：`akshare_provider.py:1660/3190`、`akshare_alt_provider.py:379`（入站报文归一）、`signal_ashare/core/analysis_utils.py:42`、`exam_plan.py:349`（跨域无窗口语义）；请 clone_guard 标 acknowledged |
| `src/zephyr/data/dual_source_guard.py` | source | `dual_source_pair_verdict` | 双源判据收敛件 / 两源互核时读不到、两边都空、只有一边有货，三种情况一律算红不许当没问题 | `zephyr.data.dual_source_guard` / `_domain_data` | 不需要（纯判据，不在资金链路） | 低：`source_health_check.py:204`（对象=探针存活）、`recon_runner.py` L2（零容差资金面，越界）；跨域不同对象→不并 |
| `src/zephyr/data/miniqmt_caliber_sentinel.py` | source | `miniqmt_caliber_text_guard` | miniQMT 口径回退哨兵 / 扫描提到 miniQMT 的句子，说它全面退役断供却没写仅实盘的逐行点名报红 | `zephyr.data.miniqmt_caliber_sentinel` / `_domain_data` | 不需要（文本尺，无算法口径变更） | 中：commit_gates 文案族判"溯源标注存在性"、`align_all.py` 判图文对齐，均非"按行禁词+范围限定放行"；若他道已有同职尺则以本件为合并目标并退役副本 |
| `tests/data/test_wave3_date_normalize.py` | test | n-a（CREATE-GUARD tests/ 豁免） | 测试件不入翻译册 | `tests.data.test_wave3_date_normalize` / tests | 不需要 | 低（邻居 `tests/scripts/test_build_consensus_daily.py` 只测聚合口径，本件只测混型入参） |
| `tests/data/test_wave3_dual_source_guard.py` | test | n-a | 同上 | `tests.data.test_wave3_dual_source_guard` / tests | 不需要 | 低（`consensus_crosscheck.py:21` 自陈其测从未入库＝本件为该模块第一份在册测） |
| `tests/data/test_wave3_miniqmt_caliber.py` | test | n-a | 同上 | `tests.data.test_wave3_miniqmt_caliber` / tests | 不需要 | 低（无同题尺测） |

**改件登记面**（5 件，无 token 义务）：`consensus_daily_compute.py`（行 44/150-166/194-196/338，
**出参列 last_report_date 由原样带出改 ISO str＝列类型口径变更 → ALGO-NOTE-SYNC 需 review 同批**，
其是否挂 TDM module_ref 本包未核）；`financial_derived_compute.py`（391/394-395/402-411，零改阈值）；
`consensus_crosscheck.py`（122-128/140/160-177，**声明在途依赖**：`ch_reader.query_rows` 属波 3.0 在管件，
本包只消费不复制，若其回退则本包 `_last_trading_day` 须改回声明式临时探针）；
`known_data_gaps.yaml`（19-21/928/1309）与 `data_supply_sentinel.yaml`（12-13/597-598）仅文案、零改 gap_id 与阈值。

**未落地登记面（诚实清单）**：① 未自赋任何裁定号（未先 grep ruling_registry 确认可查 → 案卷全用文字描述）；
② 三件新 .py 的 `add_module_translation.py` 登记、creation_token 登记、depgraph 登记**均未执行**（本包禁改热册，
且工具预算内未跑登记面）；③ 越界五件 miniQMT 文案与 `recon_runner.py:381` / 未定位的 "score" 宿主
→ 交兄弟道接 `dual_source_guard`，落地后须删 `miniqmt_caliber_sentinel.PENDING_HANDOFF_FILES` 对应条（防清单腐烂成第二真源）。
