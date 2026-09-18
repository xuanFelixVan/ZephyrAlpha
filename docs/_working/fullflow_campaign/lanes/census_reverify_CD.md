---
ttl: task_bound
completes_when: 本切片 29 条四态判定全部落判（含显式"未可判"+未跑清单），且成品件已 git add
---

# 普查复测车道 C+D 切片 · 四态判定（`st-ff-rv2-20260918`）

> 任务书=总包 `st-fullflow-20260918` 派工；复测对象=`skeleton/01_break_census.md` **C 族 20 条
> （BRK-027~046）+ D 族 9 条（BRK-047~055）= 29 条**。
> 本车道**只复测与判态，不施工**：未改 `src/**`·`scripts/**`·config·注册表，未建任务条目，未取裁定号。
> 复测时刻=2026-09-18 21:1x~21:5x（本地）；DB 全部只读经 `zephyr.data.ch_reader.query`
> （自动对 ReplacingMergeTree 注 FINAL），未跑任何 ALTER/DELETE/INSERT。
> 表述禁令（#325）：本文件不说"全绿/数据面已干净"。
>
> **切片件数口径说明**：任务书写"BRK-027 ~ BRK-054 区段里的 C/D 两类"，而普查 D 族实为
> BRK-047~**055**（9 条，与任务书"C+D=20+9"一致）。故本切片含 BRK-055，区段上界以族成员为准。
>
> ★ **API 实测坑（防后人重踩，本车道逐条踩过）**
> 1. `DatabaseService` **无 `.query()`**，公开面只有 `create_task / get_clickhouse_conn /
>    get_depgraph_conn / get_governance_conn / health_check / log_rule_enforcement / …`（`dir()` 实测）。
> 2. `get_clickhouse_conn()` 返回的 client **既无 `.cursor()` 也无 `.query()`**。
>    正解=用 `zephyr.data.ch_reader.query(sql)`（返回 TSV 字符串）。
> 3. `ch_reader.query` **失败与"0 结果行"都返回空串**——探针必须自己把空串标成 `CH_ERROR`，
>    否则"查询挂了"会被读成"0 行"，正是本战役要抓的 fail-open 型假象。标量聚合（`count()`/`countIf`）
>    恒返回一行，是区分两者的手段。
> 4. ClickHouse 里 `Date` 列不能与 `0` 比较（`Illegal types (Date, UInt8)`）；判 LEFT JOIN 落空要用
>    `toDate(0)` 或改写 `NOT IN (SELECT …)`。
> 5. 探针件也会无声消失：本车道 `p6_config_tail.py` 写成功后下次调用前即不在盘（同 R-042 形态，
>    只是探针件无损失）。**结论件已按要求即刻 `git add`**。

## 1. 四态计数（总数 29 = C 20 + D 9，无缺件）

| 四态 | 条数 | 条目 |
|---|---|---|
| **仍成立** | **17** | BRK-027 / 028 / 030 / 032 / 037 / 039 / 040 / 041 / 043 / 045 / 049 / 050 / 051 / 052 / 053 / 054 / 055 |
| **已闭合** | **5** | BRK-029 / 034 / **036** / 046 / 047 |
| **口径不符** | **6** | BRK-031 / 033 / 038 / 042 / 044 / 048 |
| **未可判** | **1** | BRK-035（缺"API 原文快照 ↔ 落库行"对账件，见 §2 该条） |
| **归属错** | 0 | —（本切片未发现挂错环节/错族者；环节 ID 均 FF-01/FF-04/FF-16/全局，实测无违） |
| 合计 | **29** | |

> **给总包的分母校正（本车道最实的一条）**：任务书称"只有 5 条被独立复跑过"。实测在 z-verifier3
> 之后、本车道之前，`src/zephyr/data/config/known_data_gaps.yaml` 已被 `st-ff-datagap-20260918`
> 写入 **11 条 `verification_20260918` 字段**（逐条亲验），覆盖本切片 BRK-027/029/034/035/037/038/
> 039/040/041/042/043 共 11 条。⇒ "C 族 20 条全未复测"不成立；真实未复测面应按"是否有
> verification_20260918 + 是否被本类车道亲跑"两轴重算。本车道对 29 条**全部独立重跑**（不复用他车道
> 数字，见逐条"本车道实测"列），可与 datagap 的 11 条互为对拍。

## 2. 逐条明细（普查记载 ↔ 本车道实测 ↔ 四态）

图例：`实测`=本车道亲自复跑；`转报`=引他车道未复跑；`推断`=未取证。

### C 族（20 条）

| BRK | 普查记载（摘要） | 本车道实测值（时刻 09-18 21:1x~21:5x） | 与记载是否一致 | 四态 | 等级 |
|---|---|---|---|---|---|
| 027 | `edb_data` 0 行，iFind 配额耗尽+源退役，status=accepted | `count() FINAL = 0`；台账 id 在，gap_type=empty_table、status=accepted | **一致** | 仍成立 | 亲验 |
| 028 | `hk_connect_flow` 空表（永久断源），2014-11-17~2024-08-16 完整 4052 行，Owner 门位 | FINAL **4052 行**、`min=2014-11-17 / max=2024-08-16`；两条 gap（empty_table + source_discontinued）均 accepted | 事实一致；**类型标签错**——表非空，被标 `empty_table` | 仍成立（附否证） | 亲验 |
| 029 | `sector_fund_flow` "从未灌入或已清空/疑任务从未上线"的典型假通道 | FINAL **1467 行**，`trade_date 2026-09-15~09-18`（4 个交易日），`data_source=ths`，`max(ingest_ts)=09-18 07:06`；采集器 `scripts/data/collect_sector_fund_flow.py` 在盘；计划任务 `ZephyrAlpha_IntradayFundFlow` 在册、下次 09-19 10:05、状态就绪；哨兵腿 lag=0 breach=false | **不一致**（"从未有一行"已失效） | **已闭合** | 亲验 |
| 030 | `c3_fundamental.dividend` 空表；`dividend_incremental` disabled + source=miniqmt | FINAL **116,334 行**（bdpan 115,351 行/批 2026-07-14 + miniqmt 983 行）；`dividend_incremental` 仍 disabled **但已挂替代任务 `dividend_incremental_akshare`（weekend_calibration 档）**；真病灶=业务日停 `announce_date max=2026-07-01`，哨兵新腿实测 **lag=79d > 30d → breach**；另 **6,749 行 announce_date=1970-01-01**（bdpan 批内 5,766），且**每个 miniqmt 增量批的 `max(announce_date)` 恒为 1970-01-01** | 半不一致：表非空（标签错）；断链事实仍在 | 仍成立（附否证） | 亲验 |
| 031 | `audit_opinion` / `rights_issue` 两表无源、任务 disabled 空挂 | `audit_opinion` FINAL **96,010 行**（bdpan 单批 07-23，`max(announce_date)=2026-05-29`）；`rights_issue` FINAL **80,803 行**（**今日 09-18 由 bdpan 灌入 78,042 行** + 08-29 批，`max(announce_date)=2026-06-30`）；两任务 `audit_opinion_incremental` / `rights_issue_incremental` 实测档期=**daily_event（不是 disabled）**；两表**均已在哨兵在册** | **不一致**（"空挂/disabled"三点全否） | 口径不符 | 亲验 |
| 032 | `l2_tick` 需付费 L2 权限，任务 disabled，**fallback 降级到 get_full_tick 五档快照** | FINAL **0 行**；任务 `l2_tick_snapshot` `extra.disabled=true` ✓，但 **`fallback_sources: []`**（任务描述自述"原 fallback 五档快照降级已于 09-09 清理——循环自引用"）；且 source=miniqmt 而 miniqmt 09-18 已清退 | 主事实一致；**降级那半句已不成立**；修复路径已变（不止权限，还要换源） | 仍成立（附否证） | 亲验 |
| 033 | 北向持仓 3 个 akshare 接口失效 → "该表无有效来源" | 表 FINAL **30,574 行全由 `tushare` 供**（2024-09-30~2026-06-30 季度快照）；任务 `northbound_hold_snapshot_refresh` source=**tushare**、无 akshare fallback；哨兵腿 lag=80 ≤ 120 → ok | **影响判断不一致**（在用主源存在且在供数）；接口本身是否仍返回 NoneType **本车道未做网络实弹** | 口径不符 | 亲验（表侧）/未跑（接口侧） |
| 034 | 同键双行并存（akshare 原始行 + CAPE 回填行），000300 `cape_5y_pct` NULL 5138 行，status=monitoring | FINAL 8,125 行；**(trade_date,symbol) 双行组 = 0**（FINAL 与非 FINAL 各 0）；`data_source` 只剩 `akshare_csindex` 单一源；**cape_5y / cape_5y_pct / pe_pct / erp 四列 100% NULL（0/8125）**；000300 现为 4,062 行（全 NULL）；写入日分布：**2026-09-13 单批重采 8,111 行** | **不一致**（双行症状已消，代之以"回填批整体消失"） | **已闭合**（症状面；闭合方式=被覆盖非被合并，代价是 CAPE 数据丢失） | 亲验 |
| 035 | tushare `hk_hold` 2026-06-30 响应 243 组 ts_code 撞码，"假 code 映射成合法 ts_code → 静默污染" | 库内 **(trade_date, ts_code)→多 name 组数 = 0（全表逐日）**；06-30 实测 4,065 行 / 4,065 distinct ts_code / 4,064 distinct name（仅 1 个 name 对 2 code）；跨日期 337 组 ts_code→多 name，抽 5 组全为**合法更名**（司爾特→ST司特 / 京山輕機→ST京機 / 華夏幸福→*ST華幸 …）非腐败；读码实证 `src/zephyr/data/implementations/northbound_hold_fetcher.py::_resolve_code_collisions`（code 自洽判别救回真主行、失效则整组剔除，commit **8a81919f62** 2026-08-16 已在库，早于普查） | **不可比**——243 是 API 响应侧计数，库内侧因排序键 `(ts_code,trade_date)` 无版本列而"同键后到覆盖"，双行不可观测；污染是否落库既未证实也未证伪 | **未可判**（缺：tushare 原文快照 ↔ 落库行的逐键对账件；另缺 `_resolve_code_collisions` 测试钉——`tests/` 0 命中） | 亲验+推断 |
| 036 | ETF 分钟族 2026-06-30 前按 UTC 墙钟落 `trade_time`（小时∈[1,7]），五表 ~4.12 亿行；**Owner 门位：`--execute` 需低峰窗+批** | ①live 五表抽样月（202603/05/06/07/09）小时域 **∈[9,15]**（30/60min∈[10,15]）；②`kline_etf_1min` **2026-02 全月 4,811,806 行中 hour≤7 命中 0**；③`min(trade_time)=2019-01-02 09:30`（全史北京墙钟）；④**备份五表 `kline_etf_{1,5,15,30,60}min_tz_bak_20260918` 在库**，其 2026-03-16 小时域 **∈[1,7]**（原劈叉态被完整留档=可逆证据）；⑤执行日志 `.runtime/tmp/etf_tzfix_exec2..11.log`（exec11 完成 06:07，`remaining_utc_rows=0`、`after_rows=before_rows`、`EXIT=0`）；⑥落地 commit **`60ed3aa49c`**（09-18 07:22，st-tdchain-20260917 收编工具+终态回写；tdchain 以 `--verify` 只读复验 `remaining_utc=0 ×5`） | **不一致（已转正）** | **已闭合** ★ | 亲验 |
| 037 | mootdx/tdx 板块盘中分钟 2026-09-11 起整体断供；`intraday_sector` 档期 5 任务空转 | tdx 真值最后日 **2026-09-10**（563 code/37,857 行，与普查逐项同）；**09-11/09-15=`synth_sh`、09-14=`synth_eq` 各 139,780 行/580 code**；09-16~18 无任何行（表级 max=09-15）；`intraday_sector` 档期实测在册 **5 件** kline_sector_*min 任务 ✓；哨兵新腿（`row_filter data_source='tdx'` + `min_rows 100000/5d`）今日实测 **lag=8d>5d 且 rows=0<floor 100000 → breach**，而表级腿 lag=3 ≤5 → ok（合成行仍在掩护"表新鲜"） | 一致，且普查**漏记 synth_* 冒充真值仍日更灌入**这一面 | 仍成立 | 亲验 |
| 038 | 议息日历断源；但哨兵仍设 `max_lag_days: 2, past_only: false` ⇒ **"必然天天告警（噪音）"** | 三组数复测：表级 `max(decision_date)=**2025-10-30**` → lag **323d** ✓复现；`bank_code='pboc'` 维 `max=**2019-11-20**` → lag **2494d** ✓复现；"435 行纪元残留(min=1970-01-01)"→ 实测 `decision_date < 1990-01-01` **恰 435 行**（boe 240 / rba 119 / fed 76），但**严格 =1970-01-01 只有 1 行**，且 fed(1982+)/rba(1980+) 的日期形态与真实议息节奏相容 ⇒ "纪元残留"标签对 435 行整体不成立（须按 bank 逐维判）；全表 3,086 行 **ingest_ts 全为 2026-09-18 单批**（akshare 全量幂等重拉，`max(ingest_ts)=09-18 10:04`）；配置历史 `git show` 六版（`d8419af8e6→8a8a3f9290`）该行恒为 `date_col: **ingest_ts**` + `max_lag_days: 2` + 注释自述理由 | **因果方向已否证**：该腿量的是采集心跳（lag=0）⇒ 普查前从未告警，不是"天天噪音" | **口径不符**（缺陷比记载更重：业务停更不可见） | 亲验 |
| 039 | SHFE 仓单归档接口 2025-12 起 404，历史不可回补；2 件 backfill disabled | 库内侧：`CZCE max(trade_date)=2026-09-18`（活）而 `SHFE max=2025-11-17`（**305 天**）且 `max(ingest_ts)=2026-09-18 03:55`（采集活）；哨兵新腿 `row_filter exchange='SHFE'` 实测 **lag=305 > 10 → breach**；两件 backfill 任务仍 disabled ✓ | 一致（404 网络实弹本车道未复跑） | 仍成立 | 亲验（库侧）/未跑（接口侧） |
| 040 | 任务活（`max(ingest_ts)=09-17` 逐日跑）但源停 2026-07-31（lag=49d），7579 万行存量无损 | FINAL `count()=**75,159,520**`（不 FINAL 75,159,520；元数据 75,889,610 含重复 part）；`max(tdate)=2026-07-31`、`max(ingest_ts)=2026-09-18 11:02 UTC` ⇒ **业务滞后 49d / 采集滞后 0d** ✓；`tdate >= 2026-08-01` 行数 **0** ✓；**节奏实测=日频**：202506~202607 逐月 `distinct(tdate)` = 30/31/28/31/30/31/30/31/31/30/31/31/30（每月 28~31 天）；盘上配置 `max_lag_days: 5`（=日频档，非 40 天档） | 普查行文本一致；**"月末快照→40 天档"不成立**——该口径出自 `lanes/datagap_sentinel_yaml_fragment.yaml`（片段推论），已被 z-sentinel 改判 5 天，本车道独立复测支持日频 | 仍成立（档期口径不符，已在他车道修正） | 亲验 |
| 041 | 竞价窗口仅 live 采集产生，2026-06 起共 40 密集日；盘后回补不含盘前=结构性缺口 | FINAL **251,598 行**，`2026-06-01~2026-09-16`，**distinct 交易日 = 47**（普查 40，在途增长）；按月 202606=21 / 202607=7 / 202608=10 / 202609=9；`auction_time` 全落 09 时段（窗口语义正确）；档期 `auction_highfreq` cron `*/10 15-25 9 * * 0-4` ✓在册，其下 2 件任务 | 结构缺口一致；"40 天"→ 现 47 天；近月稀疏（8 月仅 10 日）普查未提 | 仍成立 | 亲验 |
| 042 | `alt_movie_boxoffice` 票房 6 接口全族死，**status=open 未处置** | `system.tables` 全库 `ILIKE '%boxoffice%'` = **0 命中 ⇒ 表根本不存在**；`alt_*` 前缀 26 张表清单内亦无（本车道实跑，与 datagap 同判） | **不一致**：列在"空表/无数据"族并给 `库.表` 路径，实测对象不存在（正确表述=无免费源且未建表） | 口径不符 | 亲验 |
| 043 | 已 closed 缺口**复发**：11h 全量刷新部分写入（只落 4875/5558） | FINAL **259,238 行**（与 z-sentinel 逐位同）；`countIf(close<>0)=0`、`amount<>0=0`、`turnover<>0=0`、`volume<>0=0`，仅 `pe_ttm` 非零 258,796；**跨表全日对拍**：2026-09-15 与 `kline_daily` 配对 **5,548 行，kline 非零 5,548 / dv 非零 0 ⇒ 100% 不一致**（比抽样 20/20 更强）；`data_source` 恒 `local_valuation`（259,238/259,238）；覆盖 2026-08-01~09-17 共 48 个 distinct 日，**其中 14 日是周六/周日**（08-01/02/08/09/15/16/22/23/29/30、09-05/06/12/13，每日 5,534~5,562 行且周六=周日同数；`kline_daily` 同日 0 行，如 09-13=0）；09-16/09-17 各仅 2,000 行=又一次部分写入；哨兵 `column_fill_ratio` 腿实测 **breach：低填充 {close:0.0, amount:0.0, turnover:0.0}（rows=48,489/10d 窗）** | 一致并**升级**：从"缺日"到"错值进闭环"，且新增"非交易日幽灵行"面（普查与本役其他车道均未记） | 仍成立（加重） | 亲验 |
| 044 | 台账 44 条 / 非闭合 33 条 / 14 种 gap_type；`empty_table 4 + source_discontinued 2 + interface_broken 3 = 9 处彻底断源` | 实测 **45 条**（+1，今日新增 `daily_valuation_price_legs_zero_mislabeled` 等）；status: completed 6 / accepted 15 / resolved 6 / monitoring 6 / open 3 / reopened 1 / mitigated 3 / no_source 5 ⇒ **非闭合 = 45−6−6 = 33 条**（数同、组成变：monitoring 7→6、open 2→3、upstream_data_corruption 6→7）；`last_updated: 2026-09-18`；**4 张 `empty_table` 中 3 张实测非空**（edb_data 0 ✓、hk_connect_flow 4,052 ✗、sector_fund_flow 1,467 ✗、dividend 116,334 ✗） | 总量与非闭合数一致；**"9 处彻底断源"的推论口径不符**（3/4 空表标签错） | 口径不符 | 亲验 |
| 045 | 60 件 `bt-*.json` 全量核查：`order_type` 无一非 market、无 `algo_id` 归因字段 | 60 件 ✓；逐件解析 trade 记录 **130,998 条**：`order_type` 取值仅 `{market: 126,545, 键缺失: 4,453}` ⇒ "无一非 market" ✓复现；`algo_id`/`algo` 命中 **0 条 / 0 件** ✓ | 一致；补面=**3.4% 记录连 `order_type` 键都不存在**（普查只说"常量 market"未涵盖此面） | 仍成立 | 亲验 |
| 046 | 哨兵对 `hl_perp_snapshot_daily`/`hl_oi`/`hl_funding`/`hl_liquidation_raw`/`market_china_bond_yield`/`market_fund_flow_daily` 等带 `allow_empty: true` ⇒ 可永远 0 行而不告警 | 配置实测 **51 条目 / 46 表**，带 `allow_empty` 者仅剩 **1** 条（`market_convertible_bond_clause`），且带 `rationale_zh` + `reviewed_at=2026-09-18` + `reviewed_by=st-ff-failopen-20260918` 三前置；普查点名 6 表**均已撤豁免且今日实测有数**（FINAL 234 / 234 / 4,655,619 / **1** / 5,904 / 120 行）；**语义冲突面读码实证**：`allow_empty` 仅在 `_check_date_leg` 里"max(date_col) 查不到任何行/切片为空"时短路，**滞后天数腿、`min_rows_in_window` 地板腿、`column_fill_ratio` 填充率腿各自独立判、不受豁免**；且 `_is_empty_max()` 把 `1970-01-01` 也算"空"（若某表最大业务日是纪元值又配了 allow_empty，会静默） | **不一致（已收口）**；今日实测反证：BRK-043/034 的 fill_ratio 违约照样鸣 ⇒ "有行业务日滞后/关键列全 0"不会被白名单静默 | **已闭合** | 亲验 |

### D 族（9 条）

| BRK | 普查记载（摘要） | 本车道实测值 | 与记载是否一致 | 四态 | 等级 |
|---|---|---|---|---|---|
| 047 | `src/zephyr/**/*.py` 1405 处 / 215 文件命中 fail-open；"**无统一登记册**可机械区分设计意图与偷懒" | 同口径复跑 = **1406 处 / 216 文件**（+1/+1，战役在途新增）；派生册**已在盘**：`docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml`（250KB，commit **8a8a3f9290**；注意真实路径不是任务书写的 `config/fail_open_register.yaml`——该路径实测不存在），生成器 `scripts/governance/d7_code/generate_fail_open_register.py` 在册；册内 `total_fail_open=1595 / 265 文件`（口径含 `scripts/` + `fail[_-]?open` 全形态），四档分列且 `bucket_counts` 求和自洽（5+176+735+679=1595） | 计数微漂；**"无登记册"已失效** | **已闭合**（登记册面）；聚合数本身**口径不符**（见 §3 量化否证） | 亲验 |
| 048 | "硬编码 `fail_open=True` **5 处**，需逐处判是否应为 fail-closed" | 同命令复跑 = **7**：5 处在 `llm_security/gateway.py`（L123 定义 `FAIL_OPEN_LAYERS={"l6_observability","l7_validation"}` + L307/327/343/364 **四个消费点**），**另 2 处是登记册生成器自身源码里的正则字面量（grep 自伤）**；tokenize 判该 5 处确为真语句（5/5 CODE） | **不一致**：1 个构造被放大成"5 处独立开关"；现数已漂到 7 | 口径不符 | 亲验 |
| 049 | 裸 `except Exception:` **62** 处 / "捕获后 pass" **144** 处 = 最大假象来源 | 同命令复跑：裸 **67**（+5，今日新码）/ 次行 pass **138**（−6，与已落地的 7 处真处置相容）；他口径对照=z-silent AST 分级 **261**（T1 钱路径零痕迹 62 / T2 10 / T3 168 / T4 21），T1 中 7 处已在 commit **8a8a3f9290** 真处置（含头号成果：scheduler CH 探活"先置闩再 notify 丢返回值"改为落盘才置闩），测试钉 `tests/zephyr/data/test_failopen_brk049.py` 11 条 + 变异实测 | 面仍在；**144 这个数不可复现且非完备集**（三口径 62/138/261 互不可比） | 仍成立（部分已治，聚合数口径不符） | 亲验+转报（AST 261 未复跑其分级器） |
| 050 | 262 任务中 **235 未声明 dependencies**（89.7%） | 实测 **264 任务 / 未声明 236（89.4%）**、有依赖 28 | 微漂（战役在途 +2 任务），比例与判据一致 | 仍成立 | 亲验 |
| 051 | 4 件 `schedule: disabled` 死任务空挂 | 实测恰 **4 件**，task_id 与普查逐项同（`dividend_incremental` / `futures_warehouse_receipt_backfill_czce` / `…_shfe` / `road_freight_index_full_refresh`） | **完全一致** | 仍成立 | 亲验 |
| 052 | `flags.alerts`：`auto_escalation=false` + Multi-Window 未实现 ⇒ 告警只评估不升级 | 实测逐字段与普查**字节一致**；`git log -- config/flags.yaml` 最近为 09-12 前的头字段补标批（战役未翻任何 flag ✓ 与 failopen 车道自述相容）。**本车道新证据（加剧后果）**：`Alerter._FAILURE_COOLDOWN_SEC=300` + 同 `task_id` 去重 ⇒ 用 tmp 目录实跑模拟"8 条 breach 逐条 notify"，返回序列 `[True, False×7]`、**落盘仅 1 件**；而 `supply_sentinel._alert_breaches` **不消费 notify 返回值** ⇒ 明晨 8 条违约只有 1 条进 `data/failures/`（仪表盘与 `alert_webhook_dispatch` 均读该目录），余 7 条只活在 log | 一致，且实际后果比记载更重 | 仍成立 | 亲验（冷却/落盘实测）+推断（仪表盘可见性按消费者清单推） |
| 053 | `flags.archive`：enabled=false + `implementation_status: not_started` = 教科书式假通道 | 实测**字节一致** | **完全一致** | 仍成立 | 亲验 |
| 054 | `flags.schema_validation`：`strict_mode=false` + `dlq_enabled=false` + runtime drift 未实现 ⇒ 坏数据无死信可拦（BRK-034/035 能落库的结构性原因） | 实测**字节一致**；三份施工包 `lanes/failopen_BRK-052/053/054_construction_pack.md` 已在盘（commit 8a8a3f9290）**未执行**；本车道今日实测支持其因果：ivd 计算列被后到 None 覆盖归零、dv 14 个周末幽灵行、dv 价格腿全 0 —— 三例都无 strict/无 DLQ 可挡 | **完全一致** | 仍成立 | 亲验 |
| 055 | `COORDINATION_LEDGER §7` 明列"需 Owner 提供凭据（E7 告警推送 webhook 四类凭据）" ⇒ 告警无法外发 | §7 原文仍在册（亲读）；消费者 `src/zephyr/data/alert_webhook_dispatch.py` 在盘 ⇒ 通道代码在、凭据不在 = 半截通道 | **完全一致**（Owner 门位，只登记不催） | 仍成立 | 亲验 |

## 3. 抽样人工判读（聚合数能不能当判据 —— 任务书点名题）

### 3.1 结论先给

**不能。** 三条聚合型条目（BRK-047/048/049）的**数字**在 12 小时内就各自漂了（1405→1406、5→7、144→138），
且漂的方向不可解释为"变好/变坏"；更要命的是**分母里绝大多数不是代码**。量化否证：

- 对登记册**条目化的 860 点**做 tokenize 真身分类（脚本
  `.runtime/tmp/st-ff-rv2-20260918/p5_ast_classify.py`）：

| 登记册档位 | 条目数 | 真语句 CODE | 注释 COMMENT | docstring | 行号已漂移 |
|---|---|---|---|---|---|
| `hardcoded_default_permit` | 5 | **5（100%）** | 0 | 0 | 0 |
| `money_path_no_trace` | 176 | **12（6.8%）** | 84（47.7%） | 80（45.5%） | 0 |
| `undeclared_needs_review` | 679 | **49（7.2%）** | 241（35.5%） | 378（55.7%） | 11（1.6%） |

⇒ "176 处在钱路径且零痕迹"里有 **164 处只是散文里出现了 fail-open 这个词**。聚合数能做的只有一件事：
**当漂移监控的尺子**（生成器 `--check` 就是干这个的，本车道实跑 **`DRIFT…exit=1`** 见 §4）。

- 登记册覆盖率实测（任务书"有册≠登记全"一问）：
  - 需人审的三档（5 + 176 + 679 = 860）**100% 条目化**；有意降级留痕档 735 条**只给 count 不给条目**
    （册内自述"逐条清单由 `--full` 模式按需再生成"）⇒ **全量面条目化覆盖 = 860/1595 = 53.9%**；
  - 盘上派生册 vs 现扫：**现扫 1601 / 267 文件**（盘上 1595 / 265），盘上缺 45 条、多 40 条
    ⇒ 盘上对现扫覆盖 **94.8%**，即 2 小时内 8.5% churn；`--check` 已红（exit=1）。
  - ⇒ 结论：**册已存在且分档可用（BRK-047 机制面判已闭合）**，但"登记全"要到 100% 需
    `--full` 展开 + 门禁把 `--check` 接进 CI；当前它是**待审清单生成器**，不是**严重度尺子**。

### 3.2 fail-open 抽样 5 处（取自登记册 CODE 档，非注释档）

| # | 位置 | 实测形态 | 人工判读 |
|---|---|---|---|
| 1 | `src/zephyr/security/llm_defense/llm_security/gateway.py:123`（+307/327/343/364 消费） | `FAIL_OPEN_LAYERS = {"l6_observability","l7_validation"}`，仅观测/校验层降级，L1-L5 本就 fail-closed | **设计意图**（显式命名+分层）。但有张力点待裁：契约 `orchestrator/contracts/design_decisions.py` **DD-3** 明文"fail-closed 优先于 availability，替代方案 fail-open → 安全风险"，LSG 对 L7 校验放行是否违 DD-3，本车道不裁 |
| 2 | `src/zephyr/orchestrator/contracts/design_decisions.py:80/81` | 命中的是 DD-3 契约条目的 `content` / `alternatives` **文本字面量** | **登记册分类误报**——契约里写"不要用 fail-open"被登记成"一处 fail-open 点"。此例足以否证"按命中数排严重度" |
| 3 | `src/zephyr/plan_engine/overnight_boundary_reviser.py:303` | `reasons.append("外盘通道无数据，跳过（fail-open）")`，同函数上文有 `trace["channels"][...] = "skipped:no_data"` | **设计意图且留痕**；但登记册把它记为 `has_trace=false` ⇒ **五轴里的"有无痕迹"轴不可靠**（只看本行，不看上下文） |
| 4 | `src/zephyr/signal_ashare/core/candidate_pool_aggregator.py:380` | 候选来源全空 → 返回空池 + notes 记录 + 否决清单照常透出 | **设计意图**，且降级方向是保守（不出手=不亏钱），非放行 |
| 5 | `scripts/governance/reconcile_generators.py:192` | `except OSError as e: LOGGER.warning(...) ; return True, "no_lock"` | **设计意图（有 WARNING 留痕）**，代价=并发重生成可互踩派生册；可接受，但属"锁 fail-open"家族，宜进 §5 建议册 |

⇒ 抽样判定：**5 处全部 = 设计意图降级（其中 1 处是登记册误报）**，未在这 5 处发现"偷懒 fail-open"。
真正的偷懒风险不在 `fail-open` 关键字命中的地方，而在 §3.3 那种**不提该关键字**的静默 `pass`。
⇒ 由此推论：BRK-047 的 1405/1406 命中面**指错了对象**，按关键字扫 fail-open 天然是低召回+高误报。

### 3.3 吞异常（BRK-049）抽样 5 处

| # | 位置 | 形态 | 人工判读 |
|---|---|---|---|
| 1 | `src/zephyr/data/ch_reader.py:130` | `count()` 判引擎是否 ReplacingMergeTree 失败 → `except Exception: pass` → 退化为**不 FINAL 计数** | **偷懒型（真缺陷）**：无日志、方向上把重复 part 多计 ⇒ "行数达标"被虚假满足，正好掩盖 BRK-040/043 那类"任务活着零产出"。这是普查 144 想指的东西，但按次行 grep 抓不到它（下一行不是 pass） |
| 2 | `src/zephyr/pf_alloc/core/sector_distribution_comparator.py:77` | 逐日 `QuantileRegressor.fit/predict` 失败 → `pass`；末尾 `if not rows: return 空表` | **偷懒型（真缺陷）**：拟合失败逐行丢弃后仍返回"看起来有数"的表；全失败也返回空 DataFrame 而非报错 ⇒ 下游分位边界研究无感 |
| 3 | `src/zephyr/risk/paper_hedge_leg.py:553` | 内层 `Alerter().notify` 失败 → `pass`，但外层 `log.error(exc_info=True)` + 返回 `{"action":"error"}` | **设计意图可接受**（钱路径钩子不反噬调度器，且失败已出声）；不是 failopen 车道修的"先置闩"同型 |
| 4 | `src/zephyr/data/consensus_crosscheck.py:322 / 330` | 告警通道自身故障 → `pass`，**无二次留痕** | **"告警自身被吞"同族候选**（与 BRK-049 头号成果同型），本车道未改，转报 z-silent/failopen 车道定级 |
| 5 | `src/zephyr/gov_enforcement/commit_gates/foreign_change_gate.py:136` | 注释自述 `except Exception:  # fail-open` | **需复核**：门禁检测器自身故障即放行提交，与裁定#321"门禁只许加严"存在张力（本车道只登记观察，不判违规） |

⇒ 5 处站点结果：**2 真偷懒 / 1 设计意图可接受 / 1 "告警自身被吞"同族候选 / 1 需复核**。
⇒ **聚合数不能定级，必须"分档 + 抽样"双轨**；建议普查后续把这类条目的判据从"grep 计数"改为
"分档器计数 + 每档固定抽样种子"。

## 4. 修正建议（**不改 `01_break_census.md` 原件**，交总包落笔）

按"改台账一行"的可执行粒度给：

1. **BRK-036 → 改判已闭合（P0，本切片最重要的一条）**。台账 `etf_minute_tz_split_pre_202607` 仍
   `status=monitoring` + "--execute **等 Owner 批准**"，`COORDINATION_LEDGER §7` 仍列作待批 Owner 门位，
   `lanes/datagap_source_triage.md:48` 仍写"需低峰窗+Owner 批"——而盘上事实是：五表已影子换名、
   `remaining_utc=0×5`、备份五表 `*_tz_bak_20260918` 留档、执行日志 11 份、终态回写 commit `60ed3aa49c`。
   ⇒ 这是 **R-026 第 8 类"自愈仍挂账"的活体实例**，且严重度高于 BRK-022 原例（涉资金破坏性门位）。
   建议：①台账与 §7 同步改态并挂 commit；②`*_tz_bak_20260918` 五表的物理删除时机仍留 Owner（正确，勿动）；
   ③**转报 Owner 核实执行授权链**——本车道在 `docs/_working/**` 与 `.runtime/tmp` 范围内未检索到低峰窗批准的
   书面记录（instL=分包12 T 项、脚本独占；执行时刻本地 09-18 05:34~06:07）。**这是"未见记录"不是"确认违规"**。
2. **BRK-038 → 撤"噪音"定性，改记因果**。普查"哨兵必然天天告警（噪音）"方向相反（该腿 `date_col=ingest_ts`
   永不告警）；台账 `verification_20260918` 已更正，建议普查同步。并把本车道对"435 行纪元残留"的
   精判写进去：`<1990-01-01` 共 435 行（boe 240/rba 119/fed 76），其中**恰为 1970-01-01 者仅 1 行**，
   "纪元残留"标签不可整批套用。
3. **BRK-043 → 结论改写并加两条新面**：①"缺日"已被"错值进闭环"取代（FINAL 259,238 行价格/量四列
   全 0；2026-09-15 全日 5,548/5,548 与 `kline_daily` 不一致）；②**新面 A：14 个周六/周日被写成有数日**
   （每日 5,534~5,562 行，且成对同数），任何按日期连接的下游会把假日当交易日；③**新面 B：09-16/09-17
   各仅 2,000 行=又一次部分写入**。④建议给哨兵补一条**"业务日必须 ∈ 交易日历"判据腿**（现四腿全兜不住
   幽灵假日行）。
4. **BRK-044 → 分类标签校正**：`gap_type=empty_table` 的 4 条里 3 条实测非空（hk_connect_flow 4,052 /
   sector_fund_flow 1,467 / dividend 116,334）⇒ "9 处彻底断源"应改为"1 处真空表（edb_data）+ 8 处源停/接口死"。
   总数 44→45、monitoring 7→6、open 2→3 需按台账再生成（勿手改）。
5. **BRK-029/031/042 → 从"空表"族迁出**：029 通道已建成（判闭合，残余=历史永久不可得 + 通道未入
   `tasks.yaml`/`schedule.yaml` 正门，`catchup_guard` 不覆盖，建议另立新条）；031 两表非空且任务在
   `daily_event` 槽（真正残余=`audit_opinion` 业务日停 2026-05-29，滞后 112 天）；042 是"未建表"不是"空表"。
6. **BRK-032 → 补记修复路径已变**：miniqmt 已清退 + fallback 已于 09-09 清空 ⇒ 本条不再是"开通权限即可"，
   需与 BRK-030 同配方换源；Owner 门位仍成立。
7. **BRK-034 → 记"闭合方式存疑"**：双行消失的原因是 09-13 单批全量重采把计算列覆盖为 NULL（现四列
   100% 空），属"以更糟方式闭合"；新面已由 datagap 立条（`index_valuation_daily_erp_not_computed` 等），
   本车道实测支持其 fill_ratio=0，且哨兵腿今日能鸣 ⇒ 建议普查正文把该条拆"双行(闭合)/派生列归零(新)"。
8. **BRK-035 → 改判据**：普查的"243 组"与"静默污染"跨了两个面（API 响应 vs 库内落库）。建议改写为
   "上游 tushare 撞码缺陷仍在（外部无修复路径）；我方写前判别 `_resolve_code_collisions` 在位
   （commit 8a81919f62），库内同日同键 0 组；**缺该判别的测试钉**（`tests/` 0 命中）⇒ 建议补钉"。
9. **BRK-046 → 已闭合，转两条新登记**：①`blind_spots` 只统计"只有心跳腿的表"（今日 heartbeat_blind=0），
   兜不到"**整表不配任何条目**"的静默面——实测 `edb_data / hk_connect_flow / l2_tick / kline_etf_* /
   alt_movie_boxoffice` 均 NOT_MONITORED（后者本就无表）⇒ 建议新增"应监测未监测"判据；
   ②`_is_empty_max()` 把 `1970-01-01` 当空，若某表配了 `allow_empty` 且最大业务日是纪元值则静默 ⇒ 建议
   该情形单独出声（现无测试覆盖）。
10. **BRK-047/048/049 → 三条合并改判据（R-026 第 2 类同型）**：主数从"grep 命中数"改为登记册
    `bucket_counts`，并把 §3.1 的 tokenize 比例（真语句 6.8%/7.2%/100%）写为册的伴随指标；同时把
    **`generate_fail_open_register.py --check` 接进 CI/门禁**（本车道实跑：`DRIFT…exit=1`，盘上册已过期
    8.5%，这就是它该被门禁盯住的直接证据）。
11. **BRK-052 → 补记"告警只落 1/8"新证据**（§2 表 052 行的冷却实测），建议与 BRK-055 合并为
    "告警最后一米"族：`auto_escalation=false` + 四类凭据缺 + 同 task_id 300s 去重，三件事叠加后
    "哨兵鸣了"与"人知道了"之间仍有断点。
12. **BRK-050 → 数字改生成器口径**：264/236（89.4%）随战役漂移，建议改为"按 `dependencies` 字段
    生成+入 `--check`"，散文只引用字段不写死数字（宪法 §4.3）。

## 5. 未跑条目与原因（不把未跑算成"仍成立"）

| 项 | 未跑内容 | 原因 | 若跑需要什么 |
|---|---|---|---|
| BRK-033 | 三个 akshare hsgt 接口今日是否仍返回 NoneType | 任务书禁"以静态推断替代实弹"，本车道不做未标网络实弹 | 授权一次对外只读网络调用（akshare 1.18.75，约 30s×3） |
| BRK-042 | endata 票房接口是否仍"没有权限 -1" | 同上（对外网络实弹） | 同上 |
| BRK-039 | `ak.futures_shfe_warehouse_receipt` 是否仍 404 | 同上；库内侧（SHFE 停 2025-11-17 + 哨兵违约）已亲验 | 同上 |
| BRK-035 | 撞码污染是否落库 | **判"未可判"**：缺 tushare 响应原文快照（写前件），且表排序键使同键覆盖不可观测 | 需 tushare 原文留痕件或重放一次响应做逐键对账（涉 API 配额） |
| BRK-036 | 备份五表的 bak↔live 逐表双向对照 | 只对 1min 做了 bak 侧∈[1,7] 对照，其余 4 表只验 live 侧归一（省读成本） | 4 条 `toStartOfHour` 分组查询（各 ~10s） |
| BRK-049 | z-silent AST 分级器的 261 口径 | 属他车道件，本车道只转报不重算（避免撞车） | 跑其分级器（只读 AST） |
| BRK-046 | "空表会响"的注入测试件 | 未跑生产告警面（`data/failures/` 是生产路径，禁探针写）；只读码 + tmp 目录模拟冷却 | 由 failopen 车道在其测试件内跑（已自称 11 条+变异） |
| 排班事实 | 今日 06:50 哨兵生产排班是否确实执行 | 未取调度日志；本车道用"新配置 commit 时刻 20:54 晚于 06:50"反推生产首鸣=09-19 06:50 | 取 scheduler 运行日志一次 |

## 6. 给任务书三个重点问题的直接回答

1. **BRK-038 三组数**：表级 323 天 ✓、pboc 维 2494 天 ✓ 均复现；"435 行纪元残留"= `<1990-01-01` 共 435 行
   （其中恰 1970-01-01 仅 1 行，标签需按 bank 拆分）。普查因果方向**已否证**。
   **哨兵今天是否已能告警：判据面"已能"——本车道以只读 `check_tables(today=2026-09-18)` 实跑得
   checked=51 / breached=8 / heartbeat_blind=0，其中本表两条新腿（业务决议日 323>75、pboc 维 2494>90）
   均判 breach；但生产面"尚未鸣过"——新配置 commit `85ef0962d0` 落地 20:54，排班 cron 是每日 06:50，
   ⇒ 首条生产告警要等 09-19 06:50。旁证：`data/failures/` 里 `data_supply_sentinel` 只有 3 件、时间戳
   09-17T21:01/21:19/21:47Z（本地 09-18 05:0x/05:4x），其一条即"lag=323d > **20d**"，而 **20 天阈值在已提交
   配置链任何版本中都不存在**（`git show` 六版亲验）⇒ 属车道开发期实跑产物，不能当生产告警证据。
2. **BRK-040**：日频结论成立（每月 28~31 个 distinct tdate；`tdate>=08-01` 行数 0；业务滞后 49d /
   采集 0d）⇒ "月末快照→40 天档"（出自 z-datagap 片段）不成立；盘上配置已是 `max_lag_days: 5`。
3. **BRK-043**：FINAL 259,238 ✓、`countIf(close<>0)=0` ✓、跨表对拍 **5,548/5,548 不一致**（强于 20/20）
   ⇒ 新态 = **仍成立且加重**；另发现普查与所有在册车道均未记的 **14 个周末幽灵交易日**。

## 7. R-018 高风险判断表（等级 / 若我错了会怎样 / Max 验真命令）

| 判断 | 等级 | 若错会怎样 | Max 验真命令 |
|---|---|---|---|
| BRK-036 ETF 时区劈叉已闭合（4.12 亿行转正），台账与 §7 的 Owner 门位记载已过期 | **亲验** | 若实际未修：分钟级回测/日内信号时间轴仍错，且"已闭合"会让总包停掉这条施工项→缺陷固化在生产数据里 | `python -c "from zephyr.data import ch_reader as r;print(r.query(\"SELECT toStartOfHour(trade_time),count() FROM c1_market.kline_etf_1min WHERE trade_date='2026-03-16' GROUP BY 1 ORDER BY 1\"))"` 与同 SQL 打 `kline_etf_1min_tz_bak_20260918`（前者 9..15、后者 1..7）；再 `git show 60ed3aa49c --stat` |
| BRK-036 的执行授权链我**未找到书面记录**（不等于违规） | 亲验（执行证据）+ **推断**（"未见"仅覆盖我搜过的 docs/_working 与 .runtime 局部） | 若其实有批文：我的转报会平白质疑一次合规；若无批文：资金破坏性操作绕过 Owner 门位，是本役最重的流程事故之一 | `grep -rn "tz_bak_20260918\|低峰\|--execute" docs/_working/ ruling_registry.yaml` + 问 instL（`st-ff-instL-20260918` 分包12）是否持有窗口批准 |
| BRK-043 新增"14 个周末幽灵交易日" | **亲验** | 若 kline_daily 自身缺这些日（如调休补市），则我把正常交易日误判为幽灵行，虚报一条新断点 | `python -c "from zephyr.data import ch_reader as r;print(r.query(\"SELECT trade_date,dayOfWeek(trade_date),count() FROM c1_market.daily_valuation FINAL WHERE trade_date NOT IN (SELECT DISTINCT trade_date FROM c1_market.kline_daily FINAL WHERE trade_date>='2026-07-01') GROUP BY 1,2 ORDER BY 1\")))"` + 与 `market_calendar` 对拍调休 |
| BRK-046 allow_empty 不再豁免"滞后/填充率"，白名单面已收口 | 亲验（读码+配置+今日 8 条 breach 反证） | 若 allow_empty 还在别处短路第二/三腿，则"空表会响"仍是纸面承诺，BRK-029 型风险复发 | 读 `src/zephyr/data/supply_sentinel.py:308-415`；跑 `python -c "from zephyr.data.supply_sentinel import check_tables;import datetime;s=check_tables(today=datetime.date(2026,9,18));print(s['checked'],s['breached'],s['blind_spots'])"`（只读） |
| BRK-047/048/049 聚合数不能当判据（真语句仅 6.8%/7.2%，144→138→261 三口径互不可比） | **亲验**（tokenize 分类可重跑） | 若分类器误判（docstring 边界），我可能把"真缺陷点"说成"散文"，导致总包放松对这 66 处真语句的跟进 | `python .runtime/tmp/st-ff-rv2-20260918/p5_ast_classify.py`（探针件，纯只读）；再 `python scripts/governance/d7_code/generate_fail_open_register.py --check`（现应 exit=1） |
| BRK-035 判"未可判"（不猜"仍成立"，也不判闭合） | 亲验（库内 0 组）+ 推断（污染不可观测的机理） | 若污染确曾落库：我给"未可判"会让总包误以为无风险而漏掉一次历史清创；若未落库：判闭合反而更激进，故选保守态 | 补 `_resolve_code_collisions` 测试钉 + 对 tushare `hk_hold(20260630)` 做一次响应留痕，与 `SELECT ts_code,name FROM c1_market.northbound_hold_snapshot WHERE trade_date='2026-06-30'` 逐键对账 |
| "告警 8 条只落 1 件 failures/ 文件"（同 task_id 300s 冷却 + `_alert_breaches` 不读 notify 返回值） | 亲验（tmp 目录实跑模拟，**未写生产告警面**）+ 推断（对仪表盘可见性的影响，按 `data/failures` 消费者清单推） | 若仪表盘另有日志侧汇聚或冷却被上游绕过，则我虚报一条"最后一米仍断"的新缺陷 | `python -c "from zephyr.data.alerter import Alerter,LEVEL_ERROR;import tempfile;a=Alerter(failures_dir=tempfile.mkdtemp());print([a.notify('t','m'+str(i),level=LEVEL_ERROR) for i in range(8)])"`（期望 `[True,False×7]`）；`sed -n '487,515p' src/zephyr/data/supply_sentinel.py` |
| BRK-052/053/054 flag 未翻、施工包未执行（三态仍成立） | **亲验** | 若别车道在我读后翻了 flag：我把已闭合误报为仍成立（次生：重复派工） | `python -c "import yaml,json;f=yaml.safe_load(open('config/flags.yaml',encoding='utf-8'))['flags'];print(json.dumps({k:f[k] for k in ('alerts','archive','schema_validation')},ensure_ascii=False))"` + `git log -1 -- config/flags.yaml` |
| 切片外推：本切片 29 条"全部独立重跑" ⇒ C+D 族可信分母已恢复 | **推断**（只覆盖 29/85；A/B/E~I 族共 56 条仍可能未复测） | 若总包据此宣布"普查可信度问题已解决"，A/B/E 族的同类"自愈仍挂账"会继续误导派工 | 对本切片用同一探针复跑；对其余 56 条另开车道（本件只声明 C+D 覆盖） |

## 8. 复现件清单（本车道临时件，全部只读；`.runtime/tmp/st-ff-rv2-20260918/`）

| 件 | 作用 |
|---|---|
| `p1_tables.py` | 29 条相关表存在性/引擎/元数据行数（含 `alt_movie_boxoffice` 不存在的确证） |
| `p2_c_fact.py` / `p2_out.txt` | C 族逐表事实（FINAL 行数/日期跨度/双行组/撞码/纪元残行/源分布） |
| `p3_more.py` / `p3_out.txt` | dv N-1、竞价、ETF 小时域、白名单表、多表纪元残行 |
| `p4_timeline.py` / `p4_out.txt` | 写入侧时间线（dv 对拍、bdpan 批次、synth 冒充、reservoir 日频） |
| `p5_ast_classify.py` | 登记册 860 条目 tokenize 真身分类（§3.1 表） |
| `p7_alert_cooldown.py` | 告警冷却面实测（8 条→1 件，写 tmp 不写生产） |
| `p8_tail.py` / `p9_fix.py` | 台账标签↔实测对照、dv 非交易日 NOT IN 判定、dividend/audit/rights 时间线 |
| `sentinel_run.txt` | 只读 `check_tables(today=2026-09-18)` 全量输出（checked=51/breached=8） |
| `fo_fresh.yaml` | `generate_fail_open_register.py --stdout` 现扫结果（用于覆盖率对照，未落盘派生册） |

> 一处过程留痕：`p6_config_tail.py` 写成功后下次调用前从盘上消失（未跟踪件被无声抹掉的 R-042 同型，
> 只是探针件无实质损失）。本件所列结论均可由上表其余探针复现。
