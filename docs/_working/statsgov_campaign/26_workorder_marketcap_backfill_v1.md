---
ttl: task_bound
completes_when: 数据域按 §1 前置核查签字＋段一验收通过（段二可另行分期）；本班随后按 24 号件 §4 复考协议出阳性对照复考报告
---

# 派工单——市值/价量史回补（批复②：两段合并派数据域、段一先行）

> 规格真源=同目录 `24_positive_control_backfill_spec_v1.md`（缺口实测、字段清单、验收五判据、复考协议）。
> 本单只做**派工动作**：边界、前置核查、分段工单、停机条件。**本班不含取数、不代跑、不自跑**。

## 0. 角色与权限边界

| 项 | 内容 |
|---|---|
| 出单 | 统计合法性班 st-statsgov-20261012（判据与验收口径的 owner） |
| 执行 | **数据域**，按 Owner 四裁（2026-10-12 夜）本单一并与 §1-C 新工作件一并**交数据车道二班 st-datalane2-20261012**（该道已实补 2017-2020 市值，见 27 号件 §1/§4 复测） |
| 本班禁做 | 不碰成绩真源字节、不调 akshare/tushare 取数、不代数据域改它的脚本 |
| 本班必做 | 回补完成后按冻结口径复跑小市值阳性对照并如实出报告（过/不过都说） |
| 呈批 | 段一/段二任一前置核查判"不清"⇒ 本班出阻塞申报，不强跑、不弱化闸 |

## 1. ⚑ 派工前置核查（Owner 令：不清不许跑；批复四裁已**升级为派工硬前置**）

Owner 点名的是核查项 A。本班已用只读口把 A 查到底，并顺出 B/C/D 三条同源缺陷，另有 E/F 两条待测。
**六条全部为硬前置（统筹批复 2026-10-12 夜四裁·第④条尾段）**：任一未清 ⇒ 不许跑，也不许以"跑了再说"代替。
**结论：该脚本的 tushare 腿可用但日期被硬编码在缺口右边界；akshare 腿一跑就会往市值列写 NULL。**
下列每条都附复核命令，数据域须逐条自测签字，不许照抄本单结论。

### A. 名实不符（Owner 点名项）— 本班已核，判：**名不符实，但双腿中有一条是真的**

`scripts/data/backfill_stock_daily_basic.py` 名为 daily_basic（市值/换手/股本），实测两条腿：

| 腿 | 实际调的接口 | 写进 basic 的列 | 判定 |
|---|---|---|---|
| `--source akshare`（**默认**，`:131`） | `ak.stock_zh_a_hist`（`:46`，价量K线接口） | 只 `turnover_rate`，`float_share/circ_mv/total_mv` 三列写 `\N`（`:54-60` to_tsv） | **假 daily_basic**——跑它＝用价量接口冒充市值采集 |
| `--source tushare` | `pro.daily_basic(trade_date=…, fields="ts_code,turnover_rate,float_share,circ_mv,total_mv")`（`:81-91`） | 四列全真值 | **真 daily_basic**，段一就用这条 |

复核命令（只读）：`sed -n '43,60p;81,118p;128,140p' scripts/data/backfill_stock_daily_basic.py`

### B. 默认腿是有害腿 — 判：**须先改默认，再谈跑**

`:131` `--source` 的 `default="akshare"`，而文件头用法示例（`:5-6`）写的是
`… --all`、`… --all --resume-fail`（**都不带 `--source`**）⇒ 照文件头注释照跑的人，默认落进 B 腿。
目标表四列皆 `Nullable(Float64)`（§1-E 实测），`\N` 会真存成 NULL，不是被 DEFAULT 兜掉。
施工建议（判据归数据域，本单不代拍）：去掉默认值改 `required=True`，或让 akshare 腿直接拒写 basic。

### C. 来源标签全表失真 — 判：**本单新查，比 A 更严重，回补前必须先定策**

`INSERT_SQL`（`:31-33`）列清单是 `(trade_date, symbol, turnover_rate, float_share, circ_mv, total_mv)`，
**不含 `data_source`**；而表定义 `data_source LowCardinality(String) DEFAULT 'akshare'`。
⇒ 实测全表 `7,112,965` 行的 `data_source` 一律是 `'akshare'`，但这些行 `total_mv` **零 NULL、零 0**
（min 2,406.0792／max 413,323,876.098，单位万元），形态只可能出自 tushare 腿。
也就是说：**表里"来源=akshare"的标签是列默认值刷出来的假标签，真实来源是 tushare。**
不回补这条也要修——否则 24 号件 §3 第 4 条（"换过源的批次要标注 data_source"）在既有段上无从可验。
复核命令：
`SELECT data_source, count(), countIf(total_mv IS NULL), countIf(total_mv=0), min(total_mv), max(total_mv) FROM c1_market.stock_daily_basic GROUP BY data_source FORMAT TSV`

⚑ **本班 23:5x 复测：失真面已从 711.3 万涨到 10,506,415 行**（数据车道二班的两条回补腿同样没带 `data_source`，
全表仍 100% `'akshare'`）。⇒ 按 Owner 四裁（2026-10-12 夜）第④条尾段，本条**越出回补范围，登记为数据域新工作件**：

| 工作件 | 内容 |
|---|---|
| 名称 | 存量来源标签完整性核查（`stock_daily_basic.data_source` 全表 1,050.6 万行与真源不符） |
| 归属 | 数据域（与本班 26 号派工单一并交**数据车道二班**） |
| 判据 | 逐段核真源（四列实值 vs NULL 形态、`circ_mv=close×float_share/10⁴` 精确性、批次 `ingest_ts` 分层），产出"标签—真源"对账册 |
| 门位 | **改标属 Owner**（判据面数值）；核查与对账属 AI；读侧即刻起**不得以 `data_source` 作源判据** |
| 已证事实 | 2021 前段四列全实值且单位自洽 ⇒ 出自 tushare 腿；2020-09-18 有 90 行四列全 NULL（见 27 号件 §1 附行） |

### D. tushare 腿日期枚举硬编码在缺口右边界 — 判：**不改就跑不到目标年份**

`:136-138` 交易日取自
`SELECT DISTINCT toYYYYMMDD(trade_date) FROM c1_market.kline_daily WHERE trade_date >= '2021-01-01'`
⇒ 默认只覆盖 2021+，恰好是既有数据段的左边界。段一（2019-2020）与段二（2017-2018）**必须先把日期窗口参数化**，
否则跑完报"成功"而 2019-2020 仍 0 行（这正是"表面完成、账面零增量"的假绿形态）。

### E. 引擎与版本列未知 ⇒ 覆盖风险未定性 — 判：**UNPROBED，数据域补测后才能定"追加还是覆盖"**

`DESCRIBE TABLE` 可读；`system.tables`/`SHOW CREATE` 在本机现况下取不到建表全文（HTTP 404＋TCP 报错，
`SHOW CREATE` 返回空串——按在册纪律，空＝探测失败，**不得**读成"表不存在"）。已确知：
`engine = ReplacingMergeTree`，`ingest_ts DateTime64(3,'UTC') DEFAULT now()`。
未知且必须补测的两点：① `ORDER BY` 键；② 建表是否声明 `VERSION`（若未声明 version 列，
后写入的 NULL 行在 merge 后会**静默顶掉**同键的真值行＝B 腿的危害被放大成不可逆）。
复核命令（任选可用面，取不到要如实报 UNPROBED）：
`SELECT create_table_query FROM system.tables WHERE database='c1_market' AND name='stock_daily_basic' FORMAT TSV`

### F. 源权限与单位 — 判：**待测**

`tushare.pro_daily` 历史段（2017-2020）通常吃积分档位；`TUSHARE_TOKEN` 走 `secrets`（勿裸取环境变量）。
若权限够不到目标年份 ⇒ 判 `blocked_on_data` 并上报，**不得**用 `float_share × close` 之类推算值冒充采集值；
确要用推算，必须新批次显式标 method 并在验收件里单列一栏（推算≠回补）。

## 2. 段一（先行，便宜）——stock_daily_basic 2019-01-01..2020-12-31

| 项 | 内容 |
|---|---|
| 目标表 | `c1_market.stock_daily_basic`（列名勿改：`trade_date, symbol, turnover_rate, float_share, circ_mv, total_mv, data_source, ingest_ts`） |
| 入口 | 现成件 `scripts/data/backfill_stock_daily_basic.py`，**`--source tushare` 腿**，先完成 §1-D 的日期窗口参数化 |
| 基线（本班实测，完工要能对拍） | 全表 `7,112,965` 行，覆盖 `2021-01-04..2026-10-12`，`uniqExact(symbol)=5,785`；2019-2020 段 **0 行**（`count() WHERE trade_date<'2021-01-01'` = `0`，真零非探测失败） |
| 价量侧 | **无需回补**：2019=890,251 行 / 2020=969,967 行，票面 2019=3,771、2020=4,366（24 号件 §1 实测）⇒ 只缺市值/股本/换手 |
| 目标行量（估） | ≈ 487 交易日 × 当年票面 ⇒ **约 198 万行**（24 号件 §2） |
| 两列都要 | `circ_mv` 与 `total_mv` 都补：本班实测小市值构造 total_mv 基显著优于 circ_mv 基（1.24 vs 0.50），验收要两列齐，不许只挑一列 |
| 完工定义 | §4 验收三条全绿 ⇒ 段一 done；段二可另开期 |
| **现状（本班 23:5x 复测）** | **已补齐**：2019=885,332／2020=946,540 行（合 1,831,872，与车道二班在册数逐位吻合），2019=244／2020=243 交易日与 `kline_daily` 同集 ⇒ **缺日率 0**。本班已按 §4 出验收核账：**追1 PASS／追2 FAIL（见 §1-C）／追3 未闭合**，明细与复核命令=`27_segment2_channel_probe_and_acceptance_v1.md` §1 |

## 3. 段二（决定成败）——kline_daily(＋_hfq) 与 basic 2017-01-01..2018-12-31

| 项 | 内容 |
|---|---|
| 为什么要 | 阳性对照要过 DSR 门槛需 T≥**1,651** 交易日（693×(3.104/2.010)²）；只补 2019-2020 得 T≈1,180 ⇒ t≈2.62 仍差一档。**这段不做，阳性对照就还是考不成** |
| 现状（实测） | `kline_daily` 2016=56,648／2017=57,190／2018=57,158 行——按 24 号件票面即 234/240/237 只，**是 stub 不是薄采**（`kline_daily_hfq` 同形态 232/238/235，两表互证非取数姿势问题） |
| 目标 | 票面回到"当年实际上市数 ×0.95"（2017≈3,560、2018≈3,580），价量 ≈173 万行＋同段 basic ≈173 万行 |
| 表族义务 | 后复权是 daily/weekly/monthly 表族：改 `kline_daily` 须族内对拍，勿只补日线让周/月线与 `adj_factor` 脱基（在档前科：WO-004 日线改后周线仍跟旧基座，72% 矛盾） |
| 停机判据 | 通道实测后仍取不到 2017-2018 全市场价量 ⇒ **如实报 `blocked_on_data`**，不得用 240 票 stub 面冒充全市场面板复考（那会把阳性对照做成假绿）。⚑ 更正：本行前版曾引"881/8803 深史真实上限 2021-08-02"作前科，那是**板块指数**通道的结论，转域到个股日线不成立，已按本班实测的三条个股通道替换（见 27 号件 §2） |
| **现状（本班 23:5x 复测）** | **市值半边已到**：2017=743,941／2018=817,637 行（合 1,561,578，与在册吻合），票面 3,468/3,611；**价量半边未到**：`kline_daily` 2017=240／2018=237 票仍是 stub ⇒ 决定成败的那一半**还没做**，可用通道只有 baostock（须先补窗口化在册语义），详见 27 号件 §2-§3 |

## 4. 验收判据（不达标不算完成，别用行数糊）

24 号件 §3 五条照用（逐年票面 ≥ 当年上市数×0.95／逐日与 kline 对账缺日率<0.5%／20票×40日手工对拍且
`total_mv>0` 无负无 NaN／与既有段同单位口径且标 `data_source`／PIT 一律上月末市值，附"用当日值＝未来函数"反例被拒）。
本单因 §1 新查而**追加三条**：

1. **既有段零改动证明**：回补前后各跑一次
   `SELECT count(), countIf(total_mv IS NULL), countIf(total_mv=0), min(trade_date), max(trade_date) FROM c1_market.stock_daily_basic`
   ⇒ `>= '2021-01-01'` 段的行数与三态计数必须逐位不变（ReplacingMergeTree 下"没变"要按 FINAL 复核）。
2. **标签真实**：新批次 `data_source` 必须由 INSERT 显式写入且与实际接口一致；
   若同时修 §1-C，要给出既有段的重标方案（改判据面数值属 Owner 门位，AI 不得自行刷）。
3. **默认腿危害复现测试**：改完后必须存在一条"照 `--all` 裸跑会落到哪条腿"的显式断言或被拒的测试；
   即：**验收要证明 B 腿现在跑不起来**，而不是证明"我们不会误跑它"。

## 5. 回退与纪律（数据域执行时照本单走）

- RULE-DATA-OPS：只 INSERT 新日期段；**禁** `ALTER TABLE … DELETE`、禁 UPDATE 覆盖既有行；
  判重用 `check_tick_duplication.py`，禁聚合计数判重。回退＝按 `ingest_ts`/`data_source` 批次界删除新段（先测可逆性再动）。
- 长批任务先登记 `data/runtime/process_reaper_keep.txt`（每行一个 cmdline 子串），否则 reaper 会把回补进程当游离核心杀掉。
- 进度/失败清单现落 `.runtime/tmp/tilib-clear/b9_*`（`:28-29`）——那是别的战役的目录名，
  数据域施工时建议改到自己会话的 staging 面；禁向 `.runtime` 根直写。
- 单位与探测失败一律出声：CH 读口出错返回空串而不抛，空串≠"没有数据"（真零的签名是 `0`）。

## 6. 本班后续（不在本单交付面内）

段一验收通过 ⇒ 本班按 24 号件 §4 冻结口径复跑小市值阳性对照（同 8 配置面、同成本档 17.5bp×双边、
同判官 DSR=`MOD-SIM-024`/PBO=`cpcv`，禁新造数学），复考报告与判读**先预登记后测量**。
段二未到 ⇒ 阳性对照继续判"待数据"，**不得**以改月频 t 口径替代回补（批复三已判：留档不采）。
