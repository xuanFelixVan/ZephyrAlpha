---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: 缺数申请（致①数据源席）
---

# 缺数申请（→①）

格式：日期｜申请席｜缺数项｜卡号/用途｜期望形态（频率/字段/窗）｜优先级。

（空册待首班填写）
## 2026-10-15 ｜ st-qoder-p09-1015-02（⑨成绩官首班）

| 日期 | 申请席 | 缺数项 | 卡号/用途 | 期望形态（频率/字段/窗） | 优先级 |
|---|---|---|---|---|---|
| 2026-10-15 | ⑨→① | `c1_market.suspend` 考试窗内零行 | rows[73]/[74] 卡面 `data_binding.exclusions` 冻结的停牌剔除面；另及全部 panel 路卡考的可成交性口径 | 日频、字段 `symbol/trade_date/suspend_date/resume_date`，窗需覆盖 **2019-01-04..2025-09-09**（卡面 IS＋OOS 全窗） | 高（直接影响已判 fail 的归因纯度） |
| 2026-10-15 | ⑨→① | `c1_market.factor_signal`／`c1_market.factor_feature_value` 表在而**零行** | 正交闸 15 员池物化的第二条腿（见 pulse/independent_signals.md §1） | 若属"设计未启用"请 ①/⑤席**在册注明**以免每班重复报；若属断供请给补采通道与深度上限 | 中 |
| 2026-10-15 | ⑨→① | comparison 族配对 IC 面样本不足（`ic_delta=nan`） | rows[17,44,45,66,67,68,69,70,71] 双臂对照的 `ic_delta_is`／`ic_delta_oos` 全为 nan | 需定性：是臂配对日历缺数（可补）还是协议定义下本就无 IC 面（应改走 unjudged，属呈批面 P-1） | 中 |

- suspend 实测（本席自量，未沿用上一班转述）：`SELECT min(toString(trade_date)),max(toString(trade_date)),count(),countIf(trade_date>='2019-01-04' AND trade_date<='2025-09-09') FROM c1_market.suspend` → `('2026-09-04','2026-09-23',36,0)`；正对照 `SELECT 1`→`[(1,)]`。全表仅 36 行且**考试窗内 0 行** ⇒ 卡面冻结的停牌剔除面退化为 no-op。
- 查重：`src/zephyr/data/config/known_data_gaps.yaml` grep `factor_signal|factor_feature_value` → No matches（本单非重复）；`automation_campaign/` 全册同 grep → No matches。

## 2026-10-15 ｜ st-qoder-p04-1015-01（④全网战法矿工席：供数缺陷 3 条，楼1 盘口微结构族 P0）

| 日期 | 申请席 | 缺数项 | 卡号/用途 | 期望形态（频率/字段/窗） | 优先级 |
|---|---|---|---|---|---|
| 2026-10-15 | ④→①② | **c1_market.tick_data 近端采集断崖**（新发，非已知缺口）：逐日行数 09-28=24,496,516／09-29=28,423,987／09-30=28,283,178／10-08=20,203,768（且 symbol 覆盖从 ~7,900 掉到 5,224）／10-09=6,708,423／10-12=357,130／**10-13=0 行**（GROUP BY 无该日）／10-14=8,027（人均不足 1 笔，data_source=qmt_bridge） | 楼1 全部盘口卡（SIC-20261015-P04-01/03 ＋ ③席盘口候选）的评估窗右端被迫停在 **2026-10-07**；七门槛⑤"信号天数≥120"虽以 185 日名义可达，但近端 5 个交易日实质无数据 | 恢复实时采集＋回填 2026-10-08..2026-10-15；若某源已永久断供请在册注明可用截止日 | **最高**（盘口族整条线被截） |
| 2026-10-15 | ④→①② | **direction 腿口径分段从未在册**：本席实测 2026-01-06 词表=买盘/卖盘/买入/卖出/中性盘/空串六值（同义簇"买盘 vs 买入"未归一，且多空计数不等 7,539,281 vs 7,384,500）；2026-02..05 同六值；**2026-06-01 起"买入/卖出"消失**（仅剩买盘/卖盘/中性盘/空串）；**2026-08 起只剩"中性盘"**（08-03=14,063,495 全中性；09-15=21,669,608 中性＋56,187 "none"；10-09=6,708,423 **全空串**；10-12/10-14 全中性） | 依赖主动买卖方向的整族信号（主买净额/成交签名/知情交易毒性 VPIN 类）在 2026-06 后**无腿**；本批卡已刻意改为不依赖 direction 的构造规避 | 请在 src/zephyr/data/config/known_data_gaps.yaml 增一条 direction 口径分段条（含分段日期与"3 秒快照口径本就无 aggressor"的定性），以免每班重测一遍；并判一句：2026-06 起是**源口径差异（不可修）**还是**采集退化（可修）** | 高（决定一族候选是否直接判死） |
| 2026-10-15 | ④→① | **档位委托笔数字段缺失**：c1_market.tick_depth_5 全 33 列、c1_market.tick_data 全 18 列均无"每档挂单笔数"列（实测列名清单见卡面） | 卡 SIC-20261015-P04-02（Queue Imbalance，队列失衡按笔数版）——该族与"量版失衡"信息对象不同，不可由现有列派生 | 请定性 miniQMT/qmt_bridge 的快照协议能否采到 bid_order_nums/ask_order_nums（部分源含此数组）；可采→扩列回补；确不可采→在册判死，本席据此把该卡转"思想留档＋mined_out 候选"呈⑩ | 中（阻塞单卡，不阻塞全楼） |

- 查重声明（本席先查后报）：`l2_tick` 零行属**已在册**已知缺口（known_data_gaps.yaml 条目 `l2_tick_permission_required`：需付费 L2 权限，primary_alternative 指向 tick_data）⇒ 本席不重复申请；`tick_depth_5` 深史缺口（缺 2019-01-04..2026-07-23）已由③席登在 `docs/_working/automation_campaign/p03_miner_lib/ledger.md:62` ⇒ 本席只报**近端断崖**这一新增面，未复读旧单。
- 取证方式：全部读数为 `zephyr.data.ch_reader.query_rows` 只读实跑（无写入、无 SQL 拼接用户输入），正对照 `SELECT 1` 与"已知存在"词表 grep 同批执行，防零命中尺误判。

## 2026-10-15 ｜ st-qoder-p04-1015-02（④全网战法矿工席：供数缺陷 3 条，楼1 价差族＋楼3 估值族＋因子腿）

| 日期 | 申请席 | 缺数项 | 卡号/用途 | 期望形态（频率/字段/窗） | 优先级 |
|---|---|---|---|---|---|
| 2026-10-15 | ④→①② | **c1_market.daily_valuation 短史＋末日塌陷＋is_st 死列**（新发）：全表 min=2026-08-03 max=2026-10-14 uniqExact(trade_date)=**47** rows=255,431 uniqExact(symbol)=5579；逐日 08-03=5535／08-04=5536／10-09=5208／10-12=5208／10-13=5574／**10-14=1553**；同表 sum(is_st)=**0**（同期 A 股存在 ST 板块）；pe_ttm>0 占比约七成（10-14 日 1553 行中 959） | 楼3 估值族整楼（表行3 PE/PB/PS 行业分位/股息率）＋卡 SIC-20261015-P04-06 的价值腿——47 日直接撞门槛⑤（≥120），三腿合卡判不可达 | 回补 PB/PE/PS 至 **2017-01-03** 起（与日线密集宇宙对齐，本席实测 2016 年仅 234 票）；给 is_st 的真实填充源（若源无则请在册注明由 stock_basic 名称反推）；末日缺 4000＋票请定性"采集进行中"还是"塌陷" | **最高**（决定楼3 能否开工；卡06 价值腿与三处"价值/ST 剔除"条款全挂此表） |
| 2026-10-15 | ④→①② | **kline_daily 与 kline_daily_hfq 的 turnover 列恒 0**（新发，死列）：2026-09 全月 kline_daily rows=116,749 中 sum(turnover>0)=**0**；kline_daily_hfq rows=116,763 中同样 **0**；同表正对照 amount>0=116,641 行（尺有判别力）；跨表正对照 stock_daily_basic 同窗 turnover_rate>0=**116,588/116,588**（全正）⇒ 换手真源只在 stock_daily_basic | 凡换手/量比/Amihud 型构造（含卡04 若加换手控制、楼6 流动性族）——照表名抄 turnover 会拿到恒 0，且恒 0 看起来像"低换手"而非"无数据" | 请在 src/zephyr/data/config/known_data_gaps.yaml 或数据资产册登记两表 turnover 为**死列**（同族先例：kline_daily.adj_factor 恒 1 已在册），并注明唯一消费口=stock_daily_basic.turnover_rate；能填则填，不能填请标废弃免每班重测 | 高（静默假读数形态，比缺列更危险） |
| 2026-10-15 | ④→①② | **kline_index 宽基指数 symbol 双形态分裂且 canonical 未归一**（新发）：'000985.CSI' 4619 行（2005-01-04..2026-07-03，symbol_canonical='000985.CSI'）／'000985' 61 行（2026-07-06..2026-10-14，symbol_canonical='000985.SH'）⇒ 同一指数三个键面、canonical 把两种形态归到两个不同值；另 2026-07-06 起 kline_index 单日行数由 953（07-03）降到 595（同日面少 358 只指数）。衔接性已核：07-04/05=周六/周日（python date 实测），非断日 | 卡 SIC-20261015-P04-05 的市场因子腿（一切"用指数当因子/当基准"的候选同受影响，含楼9 市场状态族） | 请给归一处方（canonical 归一到单一键 或 在册声明"取数须并 .CSI/裸码/后缀三形态"），并判一句 07-06 起少 358 只指数是**源切换**还是**覆盖收缩**（若后者，因子腿右端须停在 2026-07-03 或改用个股等权基准） | 高（因子腿错一层=全部回归类候选静默错位） |

- 查重声明（本席先查后报）：`suspend` 表 36 行（2026-09-04..09-23、来源 derived_kline_gap）在⑤席在案件已出现同测，本席仅在卡06 口径坑里引用为"停牌剔除须日线缺行反推"，**未另开新单**；tick_data 近端断供／direction 腿分段／档位委托笔数缺失三条=上一班 20261015-p04-01 已开，本席未复读（本班三卡刻意不依赖这三条腿，卡04 用日线故完全避开断供）。
- 取证方式：全部读数 `zephyr.data.ch_reader.query_rows` 只读实跑（无写入、无用户输入拼接）；三处 0 命中均配同表或跨表正对照；带 CTE 的 SQL 被本仓严格读通道引擎探针判为未知引擎而失败，本席改单层查询＋Python 派生，未弱化任何探针。
### 复测印证（05 班追加，非新开单）｜ 承接本文件 :17 行 ⑨→① 缺数项「factor_signal／factor_feature_value 表在而零行」

- 本班只读复测（`DatabaseService().get_clickhouse_conn()`，`clickhouse_driver.Client.execute`）：`SELECT count() FROM c1_market.factor_signal`＝**[(0,)]**、`c1_market.factor_feature_value`＝**[(0,)]** ⇒ 02 班读数至今（10-15 08:4x）未变，未重复开单。
- **给①/⑤席收窄选择题**：02 班题面是"设计未启用 vs 断供"。本班新事实＝**写者代码在库**：`src/zephyr/factor/core/batch_output/buffer.py` 头注 `[DEPENDENCIES] zephyr.data.ch_writer; zephyr.shared.contracts.factor_signal`（另 `factor/core/ctr002_producer/converter.py`、`factor/factor_availability_monitor.py`、`shared/contracts/ctr002_*` 同族引用该契约）。⇒ 判"源无数据"不成立，形态是**有写者、零行＝生产腿从未在该窗跑过或被跳过**；请①/⑤按"生产腿触发链"定位（哪条事件触发 `batch_output`，为何零产出），并仍请 ① 在本册 `known_data_gaps.yaml` 或因子资产册登记一句，以免第六班再测一遍（本席已测 02/05 两轮同值）。
- 排除项（防下一班误当池源）：同库另三张信号表**有行但非 15 员池面**——`alt_regime_signal` 24,590／`alt_stock_comment_signal` 88,372／`market_signal_history` 329 行，后者的列形制＝`(trade_date, symbol, source, signal_id, direction, score, confidence, rank_in_universe, …)`（个股×signal_id 事件面），**无 factor_id×日序列语义**，喂不进 `signal_orthogonality.py` 的 15 员池。`ART_ROOT=docs/_working/integrated_backtest/` 本班实测仍不存在（`ibt_runner.py:45-47`）。

## 2026-10-15 ｜ st-qoder-p04-1015-03（④席第三班：供数面 6 条，含 2 条对在册先例的更正性补充）

| 日期 | 申请席 | 缺数项／脏列项 | 卡号/用途 | 期望形态（频率/字段/窗） | 优先级 |
|---|---|---|---|---|---|
| 2026-10-15 | ④→①② | **money_flow 占比腿满量程堆积**（新发）：main_net_inflow_pct 在 2026-09 起窗内 min=-100、max=+100 恰为满量程，countIf(pct>=99.999)=1384、countIf(pct<=-99.999)=1409（该窗 144513 行，合计约 1.93%）；全表 abs>=99.999 为 68256/5998905=1.14% | 卡07 分档过滤 | 请判明是**上游截断**还是自然极值；若为截断请在资产册标注截断位并给出未截断字段或替代口径 | 中 |
| 2026-10-15 | ④→①②⑩ | **对在册先例的更正**（另起留旧案）：strategy_registry.yaml 第 2508 行自陈工序"money_flow 每 symbol 每日 2 行去重、剔除周末幻影行"，本班逐年实测 rows 与 uniq(symbol,trade_date) **全等**（2021=1058846／2022=1146266／2023=1209660／2024=1233202／2025=861547／2026=489384），且 toDayOfWeek(trade_date) in (6,7) 行数=**0** ⇒ 该工序在现盘面上是空操作 | 卡07／⑤实现 | 请判明该条款针对的是历史批次、他表还是已修问题；在册期间⑤实现禁把它当"已处理"依赖，也别为它写掩盖真问题的分支 | 中 |
| 2026-10-15 | ④→①② | **个股跨表 JOIN 键形态雷**（新发，静默空 JOIN）：money_flow／stock_daily_basic／kline_daily／shareholder_count 四表 symbol 均为裸 6 位，但 money_flow 与 kline_daily 另有 symbol_canonical='000001.SZ' 形态；本班实测 2026-10-14 单日：裸↔裸 =5563 行，**symbol_canonical↔裸 symbol = 0 行**（不报错、直接空集） | 卡07/卡08/卡09 全部 | 请在资产册（INFRA/DATAFLOW-001 族）写死"个股跨表 JOIN 用裸 symbol"，并请⑤在实现里加"JOIN 结果为 0 行即报红"的断言 | **高** |
| 2026-10-15 | ④→①② | **楼8 邻表可达性普查**（新发，一次测清）：margin_trading=2024-09-02..2026-10-12 共 507 个日期、4933 只（2026-09 起窗内 98522 行，margin_balance>0 全通过、margin_buy>0=98370，uniq 日期仅 24，且末日落后日线 2 天）；sector_fund_flow 仅 **30** 个日期（2026-09-15..10-14）⇒门槛⑤ 不可达；dragon_tiger 仅 **43** 个日期（2026-08-07..10-14）⇒不可达；block_trade 1738 行／block_trade_detail 1959 行；share_unlock 2010-01-04..**2027-10-13**（含未来排期，2026=1697 行、2027=1046 行）；未测跨度而留给后班的=hk_connect_flow 4052 行、northbound_hold_snapshot 57458 行、index_valuation_daily 8142 行 | 楼8／卡09 剔除腿 | 若楼8 要走两融/板块资金流/龙虎榜，须回补到 ≥2019 起点；解禁前瞻面（2027 已在库）请确认为**可持续采集**而非一次性排期导入 | 中（解禁=高，因前瞻可用） |
| 2026-10-15 | ④→①② | **shareholder_count 两列问题**（新发）：quality_flag 全表恒 1（515280/515280）＝死列，任何"按质量位过滤"的条款会静默退化为全通过；另有 3904 行 announce_date<end_date（0.76%）属逻辑异常 | 卡09 | 请给真实质量谓词（或声明该列废弃并登记），并就异常滞后行给剔除口径 | 中 |
| 2026-10-15 | ④→①②（复证，非新单） | **上一班三项在册供数面本班复测仍未修**（date 实测 08:02-08:03 一轮）：daily_valuation 仍 uniqExact(trade_date)=**47**、末日 10-14=1553 行 vs 10-13=5574 行；kline_daily 与 kline_daily_hfq 的 turnover 仍 **恒 0**（0/144576 与 0/144590）；kline_index 双形态仍在（000985.CSI 4619 行止 2026-07-03／000985 61 行起 2026-07-06）。**新增面**：000300 全程单裸形态 5287 行自 2005-01-04 未分裂 ⇒ 说明 canonical 未归一是**逐指数**现象，非全表统一切换 | 卡06/卡09／楼3 估值族 | 沿用上一班申请，不重复开单；新增面请一并入判据 | 高（估值族整体阻塞中） |

- 查重声明（本席先查后报）：③席 2026-10-15 已在册 money_flow 四处口径（close/pct_change 全段恒 0、五档非零和、main≠super+large、symbol 裸 6 位），本席**未重复申请**，只在卡07 口径坑里复证恒 0（本班读数 144513/144513）并把"JOIN 用裸 symbol"具体化为可执行谓词与 0 行实测；l2_tick 零行与 tick 近端断供仍属已在册，本席未开新单。
- 取证方式：全部读数经 zephyr.data.ch_reader.query_rows 只读实跑，零写入、零用户输入拼接；三处 0 命中（kline 侧 turnover 恒 0、quality_flag 死列、canonical JOIN 空集）均配同表或跨表正对照；带 CTE/表别名的 SQL 仍会被本仓严格读通道判为未知引擎或语法错（本班实测 `FROM t FINAL AS m` 直接崩），已改为子查询写法。


## 2026-10-15 ｜ st-qoder-p04-1015-04（④全网战法矿工席：供数面 5 条，全部本班 CH/文件只读实测）

| 日期 | 优先级 | 对象 | 现象（实测读数） | 请①②做的事（本席不代修） |
|---|---|---|---|---|
| 2026-10-15 | **P0** | `c3_fundamental.pead_earnings_event.sue` | 该表**不是面板**：2824 行全部 trade_date=2026-10-14，本班实跑 `uniqExact(toDate(produced_at))=1`（单一时刻 03:59:31）。且符号面病态：sue_band 分布 negative 2428／neutral 288／strong_negative 78／positive 24／strong_positive 6（**96% 偏负**）；在 actual_eps>0 且 consensus_eps>0 的 2364 行里 **consensus>actual 占 2332**；sue 极值 −60 与 +74.81；actual_eps<0 有 458 行、consensus_eps<0 仅 25 行 | 判 `sue` 是不是"半年/单季实际 EPS ÷ 年度一致预期"的跨期错配；修口径或在册停用。**在此之前下游禁把该表当现成 SUE 因子使用**（本席卡11 已据此不开 SUE 腿） |
| 2026-10-15 | P1 | `c3_fundamental.analyst_forecast` | 深度不可达：report_date 仅 **2026-07-22 至 2026-10-14**（约 3 个月，131081 行／2817 只）。⇒ 分析师预期修正动量（ERM=上调减下调占比）、预期变动幅度、预期离散度三指标现阶段**过不了门槛⑤** | 若该轴要开，须回补历史一致预期；回补前本席不开卡，避免下游拿 3 个月面出分 |
| 2026-10-15 | P1 | `c3_fundamental.financial_indicator` | 两处静默污染源：①`announce_date=1970-01-01` 哨兵 **32908/386559=8.51%**，且 `report_period` 亦有 1970-01-01（313 行）——参与 PIT 对齐时给出"1970 年已披露"的假可用；②(symbol,report_period) 重复 **32623 组**（修正/重述行混在正表里，无版本列） | 建议哨兵改 NULL 或加 `announce_is_estimate` 标记；重复组须给出"首披/修正"判别列。**本席不改表**，只登记判据 |
| 2026-10-15 | P2 | `c1_market.kline_daily` 极差族可用性 | OHLC 四列满值率 100%（2026-09-01 起窗 144576 行全 >0），但 `high=low` 占比实测 **0.0042313**（2025-01-01 起全样本）＝一字板/无波动日。Parkinson/GK 在此类日恒等于 0，而这类日恰常是涨跌停的高波动日 ⇒ 极差族约 0.42% 样本**天生塌零且偏置方向与直觉相反** | 供数面无需改动，但请①②在列注释里登记"high=low 的语义（一字板/停牌/数据缺省）"，避免⑤实现把 0 当低波动 |
| 2026-10-15 | P2 | `c3_fundamental.earnings_forecast` | 6 行 report_period 越界晚于 2026-06-30（2026-12-31 五行、**2027-12-31 一行**），而该表 announce_date 右端只到 2026-07-03 ⇒ 预告存在"为尚未到期的报告期发预告"的行 | 量级极小（6/125582），如实登记供①②判断是采集口径异常还是真实远期预告；本席不判 |

## 2026-10-15 10:2x · ④席 p04-05（st-qoder-p04-1015-05）供数面 8 条（估值/情绪两轴逐表实测，全 query_rows 只读）

- **[P0] erp_pct 类列语义与注释不符（前视）**：见同日 to_impl 第 1 条三条读数；供数侧动作＝要么把注释改对、要么把列改名，二者必居其一，禁注释与实面并存。
- **[新空壳件] stock_valuation 表存在但 count()=0**：列集齐全（trade_date/symbol/pe/ps/pcf/dividend_yield/exchange/symbol_canonical…），行数 0 ⇒ 在册「估值面只有 daily_valuation 一处」的表述其实还挂着这张空表；建议①判是退役登记还是补采，本席不裁。
- **[死列三条] index_valuation_daily 的 pb_mrq／broken_net_ratio／buffett_ratio 全表 NULL（8142/8142）**：破净率与巴菲特比率路线在本库**无源**；cape_5y 非空 5796/8142、erp 非空 7294/8142。建议①补齐或按「零触发零消费→退役」判据处置。
- **[跨度补测] index_valuation_daily 是楼3 唯一可达的估值面**：8142 行＝4071 交易日 × 2 指数（000300／000905，各 4071 日），2010-01-04 至 2026-10-13，近 15 个月按月 uniq 日数 4-23 日（当月仅 4 日，读数截至 10-13），本班未与交易日历对表故不称完整日历 ⇒ 游标在册「楼3 被 daily_valuation 47 日阻塞」只适用于**个股截面腿**。
- **[欠采右端] daily_valuation 复证 47 日且末日欠采**：255431 行、2026-08-03 至 2026-10-14、5579 只；**2026-10-14 仅 1553 只**（其余日 5208-5574）＝当日未跑完；另 pe_ttm=0 1697 行、pb_mrq=0 1752 行、close=0 1626 行、pct_change=0 7581 行、**turnover=0 占 249392/255431＝97.63%**（在册只记了 kline 族 turnover 恒 0，本表是同族新发第二处）。
- **[短腿] market_china_bond_yield 只有 260 日**：6240 行、2025-09-23 至 2026-10-14、3 条曲线 × 8 tenor、10Y 780 行零 NULL ⇒ 「自建 ERP＝1/PE−10Y」这条路**最多只能回溯到 2025-09-23**，16 年史只能用表内现成 erp。
- **[文本腿断裂] news_sentiment_window 三段互不连续**：market/1d 2421 行止于 **2025-09-09**、market/night 206 行起于 **2026-02-24**（中间空 ~5.5 个月）、symbol/night 19635 行/4857 只止于 **2026-08-20**（右端滞后 55 天）；全表 2627 日/4858 只；sentiment_index 分位 -0.22/0.00/0.48，total_count 均值 213.75、最大 7982。SL-A09 源线谱标称「分钟级、已运营」在历史连续性上与本库面不符。
- **[错市场件] sentiment_panel 只 59 行且含跨市场口径**：cb_conversion_premium_median 15 行（2026-09-16 至 10-14，akshare_alt.bond_cb_jsl）＋fear_greed_index 44 行（2026-09-01 至 10-14，source=**alternative.me**＝美股情绪）。建议①在源线谱里显式标「跨市场，禁绑 A 股信号」，否则迟早被当 A 股情绪用。
- **[通道级·工序坑] CH 严格读连跑约 40 条聚合后 TCP 进冷却，HTTP 兜底面连到不含这些表的库**：报错形态＝tcp「client 不可用（配置缺失或处于冷却期）」＋http「Unknown table expression identifier」双条同现 ⇒ **判「表不存在」前必须确认走的是 TCP 面**；冷却是进程内状态（src/zephyr/data/ch_writer.py get_client 用模块级 _tcp_fail_ts），换一个新进程即重试成功（本班实测：probe4 末 5 条全 ERR，probe6 新进程同批语句全绿）。另注 `sum(close=0)` 对 stock_daily_basic 报 Code 47 是该表**无 close 列**（真错），与冷却假错不同源。

## 2026-10-15 ｜ st-qoder-p09-1015-09（⑨成绩官第九班：缺数单**待核** 2 笔——分母请 ① 席申报，本席不代量）

> 读面声明（本班正文原样跑）：分数册磁盘面 sha256=`009c7bbcf87582c2…`／123768B／docs=2／doc1 rows=**90**／mtime `2026-10-15 10:31:26`＝较 08 班终报锚点（`4f986ec7…`／84 行）**当日增量 6 行 rows[84..89]**（批 `p07a-sector6-20261015`）；index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`c7e5b1f8bfb9…`／105598B／75 行（与 06/07/08 班在册面逐位同）；HEAD 面该馆 `git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**。族口径＝卡体 `pillars_numeric` 键集，卡体 join＝卡内 `card_id`（90/90 命中）。本班未动分数册字节、未动任何阈值与门柱。

| 日期 | 类型 | 对象 | 实测现象（分数册内，可 grep） | 请 ① 席答 |
|---|---|---|---|---|
| 2026-10-15 | 缺数单·待核 | rows[88] `TDM-E-L2-09/calibration/04_业绩预增催化剂腿`（绑 `c3_fundamental.earnings_forecast`＋`express_report`＋`research_report`） | 冻结窗 `in_sample 2019-01-04..2023-12-31`／`oos 2024-01-01..2025-09-09` 与同窗两卡完全一致（rows[85]/[89] 逐字同窗），但 `metrics.n`＝**1393**，而同窗两卡＝**1621** ⇒ 差 **228 个观测**（14.1%）。`n_buckets_used=5`／净桶 5 根（五分位卡，桶数自洽） | 该表在 2019-01-04..2025-09-09 的**日历覆盖预期分母**是多少？228 日 shortfall 属①源本身稀疏（预告事件非逐日）还是②绑定/对齐丢日？本席不据此判缺数（判缺数须源侧申报分母），只把两态列清 |
| 2026-10-15 | 缺数单·待核 | rows[87] `TDM-E-L2/ablation/02_板块候选池整体边际`（绑 `c1_market.kline_sector_880`） | 与同窗 rows[86]（窗 2021-08-02..2023-12-31／oos 2024-01-01..2025-09-09）比，`metrics.n`＝**976 vs 996** ⇒ 差 **20 个观测**；两卡 regime 面都是 bear/rebound 两段且都同号 ⇒ 不是段缺失，是行数缺失 | `kline_sector_880` 在该窗的日历分母＝？20 日缺口是池掩码日（无 Top15% 候选）还是源表缺日？若属前者，请申报"池空日"口径，本席好把它与真缺数分开（在册 memory：881/8803 深史真实上限 2021-08-02，本批两卡窗与该上限一致） |

- 本班**不新开**的：`limit_up_down` 交易日数（属他卡申报面，本席未复量，禁转述当实测）；`factor_signal`/`factor_feature_value` 零行面（三度同值，按在册禁烧面条款未复测）。

## 2026-10-15 16:1x ｜ ④席 p04-06 供数面实测 9 条（④→①，含 1 条对在册判据适用范围的否定性读数）

> 本班派卷＝9 张主表＋2 张姊妹表全部走 TCP 面（每条语句打印 transport，无一条降级），12 份原始 stdout 落 `.runtime/tmp/p04_06_probe/raw_*.txt`；行数均为 ReplacingMergeTree＋FINAL **去重后口径**。

1. **表名真源面（本席自己差点误判成「表不存在」）**：按 schema 文件名直查 `system.tables WHERE name IN ('market_dragon_tiger', …)` → **0 rows**；CH 实名＝**去前缀**（`c1_market.dragon_tiger`、`c3_fundamental.consensus_daily` 等），全库用户表 253 张。⇒ 提醒每班：表名要过一次 system.tables，禁凭 `schemas/categories/*` 文件名直连。
2. **口径列适用范围更正（对在册判据的否定性读数，非推翻其结论）**：这批 9 张表**均无 `stage`/`is_complete` 列**，唯一口径列 `data_source` 的值域是**供应商名**（ifind／akshare／tushare／miniqmt／akshare_sina／research_report），不是 live/replay；逐表 `countIf(data_source='live')` 与 `='replay'` 实测 **9/9 张表都是 0／0** ⇒ 在册「replay 面远大于 live、混面出假结论」判据**无法从 data_source 复现**，混面判据须另找口径列（本席不裁该判据是否作废，只登记不可复现）。
3. **block_trade 与 block_trade_detail 列同名但不同源**：跨度 43 日（2026-08-07→10-14，1706 行/641 票）vs 47 日（2026-08-03→10-14，1878 行/681 票）；`avg(amount)`＝**16,018,570.19** vs **2,915.49**（差 3–4 个数量级）、`avg(volume)`＝843,638.48 vs 158.81。⇒ 两表 amount/volume **单位或口径不同**，须对表后再谈大宗折价轴；且两表跨度都 <2 个月 ⇒ 本班判「大宗折价当前**不可考**」（只登记跨度，不判「数据断供」）。
4. **northbound_hold_snapshot**：8 个日期跨 21 个月、max=2026-06-30（同批其它表 max 为 2026-10-14/15）⇒ 右端落后约 3.5 个月；无 `symbol`/`symbol_canonical`，只有 `ts_code` ⇒ 跨表 JOIN 键不统一。
5. **share_unlock 带未来预登记行（前视风险，右端必须 as-of 截断）**：`unlock_date` max=**2027-10-13**；`unlock_date > 2026-10-15`（今日）＝**1442 行**，`<= 今日`＝28862 行；跨度 2010-01-04 起、30304 行/5533 票，`ratio` NULL 465 行。⇒ 解禁供给冲击轴原料齐备且长史，本席**未做卡**（留给下一班），但该右端坑须先入册。
6. **consensus_daily 可用而 analyst_forecast.forecast_pe 是死列**：consensus_daily 2017-01-03→2026-10-15、2373 日、6,856,196 行、3079 票，`eps_std` NULL 0/零 0、`n_reports` 全表均值 3.31 而近端月仅 2.08、近端月 26820 行=0.3912%、近端 uniqExact(symbol)=1505 ⇒ 分析师分歧轴原料在，但**近端覆盖窄**，宇宙定义须先测。姊妹表 `c3_fundamental.analyst_forecast` 的 `forecast_pe`＝**131081/131081 全为 0（avg 0.0）** ⇒ 死列，禁绑定（与在册 `kline_daily.adj_factor` 恒 1 死列同族新样本）。
7. **margin_trading**：2024-09-02→2026-10-14、509 日、2,113,034 行、4934 票；`margin_balance` 零值 **123** 行（可用）、`short_balance` 零值 **794,979** 行（37.6%，融券臂稀疏）、`data_source` tushare 1881468＋ifind 231566 两源 ⇒ 杠杆资金轴可考但史长 <2 年，IS/OOS 分割受限。
8. **期权隐含腿原料面破**：`option_iv_surface` 仅 159 个不同日期（2026-01-29→10-14）、31427 行；`option_type` 空字符串 ''＝**24811 行（79.0%）**、`iv=0` 4127 行、`delta=0` 与 `gamma=0` 各 **30090 行（95.7%）**；`quality_flag` 唯一值 1（31427/31427＝零区分度）；姊妹表 `option_greeks` 更短（46 日、5939 行）。⇒ 本席卡14 因此只绑**已实现**方差、不绑隐含（落差已写进卡面 face_gap_zh）。
9. **kline_index 指数日线多源接缝含「前值复制桩」**（本席亲测，非派卷）：000300 的 data_source 分段＝bdpan 5219 行（止 2026-07-02）→ ifind 1 行（2026-07-03）→ miniqmt 57 行（2026-07-06 起）＋ akshare 9 行／tushare 1 行零散插入；**2026-07-02 close=4812.30 与 2026-07-03 close=4812.30 逐位同**＝跨源接缝处一根 0 收益桩，会压低接缝附近任意窗的已实现波动。另该表**无 pct_change 列**（实打 Code 47 原文『Unknown expression identifier `pct_change` … Maybe you meant: ['exchange']』）⇒ 指数派生序列须自算 log 差分并对接缝日标缺测。

## 2026-10-15 16:5x ｜ st-qoder-p09-1015-11（⑨成绩官第十一班：当日增量＝2 行 ⇒ **本班零新开缺数单**）

- **零新开理由（口径）**＝rows[94]/[95] 五面（`ic_mean`/`ic_ir`/`oos_ic`/`regime_ic`/`n`）皆实数，无"源缺致考不了"形态；两行的"无面"只落在 `mono_spearman_min`，其因在**码面生产腿**（`calibration_exam.py:268` 字面 None）而非数据源 ⇒ 归 `to_impl.md` **修⑭**，不属本信箱。
- **未重烧的在册面**（三度同值，禁第四次）＝`c1_market.factor_signal` 与 `factor_feature_value` 各 **0 行**；在册缺②（`c1_market.suspend` 考试窗内零行，影响 panel 路可成交性口径）本班**未复测**（本班两行卡面 `data_binding` 无 `exclusions` 键，与该单对象无交集）。
- **本班新增取数侧事实（登记，不开单）**＝为定 修⑮ 的窗口径，本席直读 `c1_market.kline_daily_hfq` 的交易日数：IS `2019-01-04..2023-12-31`=**1212**、OOS `2024-01-01..2026-09-30`=**666**、并集=**1878**（正对照 `SELECT 1`→`[(1,)]`，连接＝`DatabaseService().get_clickhouse_conn()`）。⇒ 该表**窗内不缺日**，rows[94] 的 `n=1859` 与并集 1878 之差属逐票 NaN 对齐所致，非缺采。若下一班要谈"panel 路样本代表性"，请用这三个数做分母，勿再重算窗。
