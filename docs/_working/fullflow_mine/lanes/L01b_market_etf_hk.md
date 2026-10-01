---
ttl: task_bound
title: "行情ETF转债期权港股族挖矿作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine_20261001
---

# L01b 行情/ETF-LOF/转债/期权/港股/美期族挖矿作业簿

> 方法论：onboarding SOP §9A 六问＋§9B 12 面矩阵（真源=`docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md`）；孤岛判定=census table_residual（`data/runtime/consumption_census_ledger.json` 2026-09-30 读数）；CH 读数=2026-10-01 c1_market 只读实勘（ch_config+clickhouse_driver 只读）。断供阈值=SOP §10（日频>3 天）。

## ① 族读数（已接线/零消费/断供）

| 族 | 实勘 | 已接线 | 零消费 | 断供/异常 |
|---|---|---|---|---|
| K 线主族 15 表 | 1min 14.9 亿行~daily 1,013 万行，max 多为 09-30 | kline_daily/hfq（回测核心）、kline_index（emotion_index_builder）、kline_cb（frontend api_server） | weekly/monthly 非 hfq 版（仅生产者+speed_tester） | kline_weekly/kline_monthly 停 09-15（local_qfq 通道断；hfq 版 09-30 活）；kline_futures 停 09-28 仅 24 主力 |
| ETF/LOF 谱系 18 表 | kline_etf_* 6 表+kline_lof_* 5 表全 09-30 | kline_etf_daily（owner_band_t/owner_regime_switcher/paper_outpost）、kline_etf_1min（plan_engine auction/scenario recorder） | kline_lof_* 全系（speed_tester only）、etf_benchmark、gold_etf_holdings、market_etf_share_snapshot | market_etf_share_snapshot 仅 09-18 单日（任务在管线死）；gold_etf_holdings 停 09-17 且零调度任务；etf_nav 停 09-29（T+1 属正常） |
| 期权族 4 表 | option_kline 8,287 行 302 合约 09-30 | option_kline+option_greeks（signal_ashare/option_sentiment）、option_iv_surface（regime/institutional_regime_scorer+overlay_signals_builder） | option_daily_stats（三零：零消费+任务 disabled+停更） | greeks/iv_surface 停 09-23（miniqmt intraday_realtime 通道断，**伤害现役消费者**）；daily_stats 停 09-22（akshare 无 capability，仅回补脚本） |
| 港股族 5 表 | kline_hk_daily 5,702 只 09-30 fresh | 无（全族零真实消费） | 全族 | hk_kline 停 09-15（193 只）；hk_connect_flow 停 2024-08-16=合法退役（裁定#257，交易所停披露北向实时资金） |
| 美期/全球 5 表 | us_futures_intraday/a50/us_index/kline_us_daily 全 fresh（09-29/30） | us_futures_intraday+a50（plan_engine intraday_l1_tracker）、us_index（foreign_market_coverage） | kline_us_daily（11 只美股龙头，tickflow 单源） | kline_global 半断：CL/GC 活（09-30），HSI/N225/KOSPI 停 08 月下旬（3 任务 disabled 待 provider 封装）、USDCNH 全源失效（4 disabled 子任务实锤） |

- 核心结论：本车道**真正在流血的断供**是 option_greeks/option_iv_surface（消费端 regime 评分器/期权情绪在吃 09-23 旧数）与 kline_global 外盘腿（foreign_market_coverage 读到 08 月底旧数）；其余零消费族属"接而不通"非断供。
- 双表冗余簇（w5_1 必并候选）：hk_kline vs kline_hk_daily（同"港股日K线增量"双表双零，前者 193 只停更、后者 5,702 只 fresh）；convertible_bond_list vs market_convertible_bond_clause（同转债域两表）。

## ② 孤岛 6 表完整矩阵（六问+12 面）

### T1 etf_nav（95,267 行｜1,701 只｜2021-07-29→09-29｜tushare fund_nav 主源，任务在岗）
- 六问：Q1 溢价率=kline_etf_daily 收盘/nav、跟踪误差（nav 收益 vs etf_benchmark）、净值动量/波动、nav×份额=规模流；Q2 ETF 轮动/申赎套利/折溢价回归/L05_t0 成本池；Q3 零消费实证，候选挂 strategy_factory owner_*（现只吃 kline_etf_daily，差 nav 一腿）；Q4 C 盘后（nav 晚间发布，溢价率 T 日可算）；Q5 TDM ETF 节点+S6 流动性监控（折溢价=流动性变量）；Q6 盲点=T+1 滞后无人盯、溢价率因子三原料表全零消费互不知。
- 12 面：大盘✓宽基 nav 情绪｜板块△行业 ETF 净值流｜个股✗｜做T✓折溢价（工单）｜转债✗｜ETF/LOF✓主面｜期货✗｜币圈✗｜宏观✗｜产业链✗｜事件✓巨额申赎｜文本✗

### T2 convertible_bond_iv（11,481 行｜322 只｜2026-08-07→09-30｜miniqmt intraday_realtime）
- 六问：Q1 CB 隐波分位（期权价值高估/低估轴）、IV-历史波价差；Q2 双低/条款博弈策略的期权价值轴；Q3 零（producer only）；Q4 B 盘中；Q5 无挂图；Q6 盲点=历史仅 1.8 月，S0-S7 IC 考试样本不足——先回补再挖。
- 12 面：转债✓主面｜做T△日内 IV 脉冲｜其余 10 面✗（A 股个股/大盘/期货无映射）

### T3 convertible_bond_list（1,059 行｜2007-07→09-29｜akshare refresh 任务在岗）
- 六问：Q1 静态因子（余额/评级/YTM）+条款日期轴（强赎/回售/下修倒计时）；Q2 双低轮动+条款博弈（强赎临期避坑）；Q3 零（frontend api_server 有字符串命中，census §3.4 不计——复扫时复核）；Q4 A 盘前（持仓强赎过滤）；Q5 无；Q6 盲点=与 market_convertible_bond_clause 同域双表，须先语义去重再接线。
- 12 面：转债✓主面｜个股✓正股联动/强赎回溯正股（工单）｜事件✓条款事件｜板块△转债余额行业聚集｜其余✗

### T4 futures_term_structure（3,665 行｜295 合约｜2026-08-03→09-29｜miniqmt+tushare）
- 六问：Q1 期限结构因子（近远月斜率/卷斜率 roll yield/contango-back 状态）；Q2 商品 CTA 展期收益+对冲腿近远月选择；Q3 零；Q4 C 盘后（结算价斜率）；Q5 产业链传导图（BOM 叶挂价辅助定价）；Q6 盲点=历史仅 2 月，且与 kline_futures（8,278 行 24 主力 2017→）分工未声明（全合约 vs 主连）。
- 12 面：期货/商品✓主面｜宏观/择时✓商品通胀信号｜产业链✓BOM 定价辅助｜大盘△（弱）｜其余✗

### T5 hk_kline（6,107 行｜193 只｜2026-08-03→09-15 停更｜miniqmt 专属、fallback 已知假移除）
- 六问：Q1-Q5 全查无（零消费+停更）；Q6 盲点本体=与 kline_hk_daily 同域双表双零——w5_1 判"同域重复簇→收敛唯一"：并表到 kline_hk_daily 后本表出退役证明，六问按 kline_hk_daily 重跑。
- 12 面：全 12 面✗（先并表再判——零消费小停更表无独立价值面）

### T6 kline_hk_daily（221,794 行｜5,702 只｜2026-08-03→09-30 fresh｜miniqmt 主+akshare 备，任务在岗）
- 六问：Q1 AH 溢价因子（对 kline_daily 同名 A 股）、港股通标的动量/波动；Q2 AH 轮动+跨市场分散（TDM 十职能"新市场"）；Q3 零消费者（fresh 但无人查="接而不通"现行案例）；Q4 C 盘后（16:10 港收后增量）；Q5 TDM 新市场节点+产业链图（港股上市产业链公司）；Q6 盲点=历史仅 2 月、指数腿在 kline_global.HSI（停 08-28）。
- 12 面：大盘✓港股通聚合指数面｜个股✓港股通标的（工单）｜宏观/择时✓AH 联动｜产业链✓｜板块△｜事件△｜做T✗（无分钟表）｜转债/ETF/期货/币圈/文本✗

### 12 面汇总矩阵（✓=适用留工单｜△=弱适用｜✗=不适用留痕）

| 表 | 大盘 | 板块 | 个股 | 做T | 转债 | ETF/LOF | 期货 | 币圈 | 宏观 | 产业链 | 事件 | 文本 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| etf_nav | ✓ | △ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| cb_iv | ✗ | ✗ | ✗ | △ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| cb_list | ✗ | △ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| futs_term | △ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ |
| hk_kline | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| kline_hk_daily | ✓ | △ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | △ | ✗ |

## ③ 族级粗矩阵（已接线判定+盲点一句话）

| 族/表 | 判定 | 盲点一句话 |
|---|---|---|
| kline_1min~60min | 已接线核心（回测/做T 原料） | 5min 表 8,706 symbol＞1min 5,858——universe 口径漂移未声明 |
| kline_daily/hfq | 已接线核心 | hfq 三张 legacy/quarantine 残表（0924/0925 后缀）待净零清理 |
| kline_weekly/monthly(非hfq) | 零消费+停更 09-15 | hfq 版已 fresh 接管，本两版疑可退役（先核 10,431 vs 5,911 universe 差异） |
| kline_index/index_calc | 已接线/内部 compute | index_calc 仅 1 symbol 1,963 行，用途未声明 |
| kline_cb | 已接线（frontend） | 转债因子面（双低/IV）全未建——cb 两孤岛表无消费即此因 |
| kline_futures | 弱接线 | 停 09-28+仅 24 主力，与 futs_term/期货仓单族分工未声明 |
| kline_etf_* | 已接线（策略面） | 分钟族仅 1min 有真实消费，5-60min 疑冗余（复核后收敛） |
| kline_lof_* | 零消费 | 全系 speed_tester only；LOF 策略面从未立项——挖或退役二选一 |
| etf_list/lof_list | 元数据 fresh | 清单表随主面接线自然被消费，暂无罪 |
| etf_benchmark | 零消费 | 是 etf_nav 跟踪误差因子的必需腿——两零消费表互为接线件 |
| market_etf_share_snapshot | 零消费+断供 | 快照积累制 09-18 首日即停=差分基线永缺，任务在管线死（§8 反例现行） |
| gold_etf_holdings | 零消费+断供 | 无调度任务（tasks.yaml 零条目），2004→2026-09-17 长史白躺 |
| option_kline | 已接线 | 唯一活腿；50/300ETF 302 合约面够 PCR/IV_Rank 因子起步 |
| option_greeks/iv_surface | 已接线但断供 | intraday miniqmt 通道停 09-23——regime/情绪消费端在吃旧数 |
| option_daily_stats | 三零 | C 出口候选（零消费+任务 disabled+停 09-22）；PCR 量比因子若有需先复活它 |
| hk_stock_list/hk_trade_calendar | 元数据零消费 | calendar 有一行 2027 前瞻属正常；清单表随港股面接线被消费 |
| hk_connect_flow | 合法退役 | 裁定#257 留痕完备，regime 消费端 fillna(0) 降级在岗——非事故 |
| us_futures_intraday/a50/us_index | 已接线 | 三表覆盖隔夜锚已闭环；us_index 停 09-29 属 T+1 正常 |
| kline_us_daily | 零消费 | 11 只龙头 07-20 起浅史、tickflow 单源无备（§6 fallback 铁律贴线） |
| kline_global | 半断供 | HSI/N225/KOSPI disabled 待 provider 封装（首采已落库）；USDCNH 五源全灭登记在案 |

## ④ 接线工单（按止血优先序）

| # | 工单 | 对象 | 动作 | 验收 |
|---|---|---|---|---|
| W1 | 期权实时断供止血 | option_greeks/iv_surface | 查 miniqmt intraday 通道 09-23 起失败留痕（§8 failures/），修源或降级 akshare 逐合约自算 | max(trade_date) 回到 T-1，institutional_regime_scorer 读到新数 |
| W2 | ETF 份额快照复活 | market_etf_share_snapshot | 查 daily_capital 槽 09-18 后静默失败；重跑建连续基线 | 连续 ≥5 交易日快照，差分=净申赎可算 |
| W3 | etf_nav 溢价率因子接线 | etf_nav+etf_benchmark+kline_etf_daily | 三零表组合=溢价率/跟踪误差因子族：factor_registry 候选卡+strategy_factory data_refs 补挂 | 溢价率因子 ≥1 消费者实查到数（§9 铁律） |
| W4 | 港股双表收敛+接线 | hk_kline→kline_hk_daily | hk_kline 出退役证明（Owner 门位）；kline_hk_daily 挂 AH 溢价因子候选 | census 复扫 hk_kline 记 retired；AH 因子卡入册 |
| W5 | kline_global 外盘腿复活 | HSI/N225/KOSPI 3 disabled 任务 | provider 封装 global_index_daily capability（USDCNH 另案五源重挖） | foreign_market_coverage 读到 T-1 外盘 |
| W6 | 转债域收敛+条款因子 | cb_list×clause 双表去重 | 语义去重后 cb_list 挂条款日期轴因子候选（先决：cb_iv 回补史） | 去重结论入账+条款因子卡 |
| W7 | 期限结构因子 | futures_term_structure | 回补历史（现仅 2 月）→roll yield 因子候选 | S0 IC 考试样本 ≥2 年 |
| W8 | 周月线非 hfq 版复核 | kline_weekly/monthly | 查 local_qfq 通道停更因；核 universe 差异后定接线或退役 | 三态出口留痕 |

## ⑤ 六向台账（§9A 入账口映射，6 孤岛表汇总）

- Q1 因子：候选 8 条（溢价率/跟踪误差/净值动量、CB IV 分位、转债条款倒计时、roll yield、AH 溢价、港股通动量）→ 全部待开 factor_registry candidate 卡，无一在册。
- Q2 策略：owner_band_t/owner_regime_switcher（ETF 轮动缺 nav 腿）、双低/条款博弈（转债域策略面未立项）、AH 轮动（TDM 新市场职能）→ 策略卡 data_refs 零挂载。
- Q3 模块：consumed_by_jobs 回填=etf_nav→etf_nav_refresh（生产自环）；6 表真实业务消费=0（census 实证一致）。
- Q4 环节：C 盘后=etf_nav/cb_list/futs_term/kline_hk_daily 四表增量汇合点（daily_kline 系）；B 盘中=cb_iv/miniqmt 实时族（当前断）。
- Q5 地图：TDM（ETF 节点/新市场节点）、L05_t0 成本池、S6 流动性监控、产业链 BOM（futs_term 辅助）→ 图谱挂链全空。
- Q6 盲点：三处状态无人汇总在案（census zero/wiring unwired/factor 无卡三本账互不知）；wiring_registry 待总筹落 unwired 后 90 天门起算。

## ⑥ 自审闸三态（§9C 出口）

| 三态 | 表 | 依据 |
|---|---|---|
| 接线（A） | etf_nav、kline_hk_daily、convertible_bond_list、futures_term_structure | 因子方向明确+消费端可指名（W3/W4/W6/W7） |
| 挂账（B） | convertible_bond_iv | defer_reason=历史仅 1.8 月不足以 S0-S7 IC 考试；解锁条件=回补 ≥2 年（90 天门照计龄） |
| 退役评审（C，只登记不执行） | hk_kline | 被 kline_hk_daily 全覆盖（同域/更小 universe/已停更）；注册表净删=Owner 门位 §5 |
| 附注 | option_daily_stats、gold_etf_holdings、kline_lof_*、kline_weekly/monthly 非 hfq | 族级粗判 C 候选，留 W8 与后续批次复核；hk_connect_flow=合法退役非本批对象 |

- 自审：①全程只读 CH（ch_config reader）+零改既有文件+零 git 写；②所有读数 2026-10-01 可复算（表名/行数/max(date) 均直查 system.tables+count）；③census 判定权威采纳，本簿仅补 CH 实证与接线方向；④净零：本簿=批次产物一册，未新增独立台账（汇总视图=census/wiring 机生链，§9B-3）。
