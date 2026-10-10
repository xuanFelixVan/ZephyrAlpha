---
ttl: task_bound
title: L3 挖矿车道台账（entry_flow L4 执行层 + L0/L1 补卡，32 节点）
created: "2026-10-10"
sid: st-nightmine-20261010
lane: L3
family_id: NIGHTMINE-CAMPAIGN
---

# L3 车道台账

真源指针：名册=`00_lane_roster.yaml`（lane=L3 共 32 节点）；判据=`01_mining_brief.md`；
方法论=`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` v1.7.0 §2/§3/§5/§7.5。
本车道产出两类：本台账 + `exam_cards/entry_flow/{L4,L0,L1}/` 新建卡（禁改既有件）。

## 一、实测基线（禁凭记忆，命令原文见各节）

工作目录 `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`；CH 一律经 `scripts/backtest/fexam/ch_data.ch_query_df`（探针形=作业簿 §4，零裸 duckdb）。

### 1.1 数据面实测（命令原文：`SELECT min(trade_date),max(trade_date),count(),uniqExact(symbol) FROM <表>`）

| 表 | 覆盖窗 | 行数 | 标的 | 本车道用途 |
|----|--------|------|------|-----------|
| `c1_market.stk_limit` | 2015-01-05..2026-10-09 | 9,254,772 | 5,831 | 涨跌停价/幅度真源（列：pre_close,limit_up,limit_down,limit_pct,board,st_flag）→ 广度导生的 limit_pct 轴 |
| `c1_market.limit_up_down` | **2026-07-20..2026-10-09** | 5,397 | 54 个交易日 | 既有 7 张广度卡的原绑定表——冻结窗（IS 2019-01-04..2023-12-31 / OOS 2024-01-01..2025-09-09）**零行** ⇒ 平行卡义务成立 |
| `c1_market.kline_daily_hfq` | 1990-12-19..**2026-09-30** | 10,098,785 | 5,916 | 日线 OHLC（后复权）；**实测 `pct_change`/`change` 恒 0**（600519@2024-09-30/2024-10-08 close=14018.96/13818.46 而 change=0）⇒ 涨跌停判据必须用 `close/lag(close)` 比值口径，禁消费 pct_change 列 |
| `c1_market.kline_index` | 1990-12-19..2026-10-09 | 3,104,162 | 1,097 | 000300/000001/399001/399006/000905/000852 实测各 1,843 行覆盖 2018-06-01..2025-12-31 ⇒ 目标面 next_day_index_return 全窗可用 |
| `c1_market.daban_board_event` | 2026-09-01..2026-10-09 | 1,767 | 975 标的 | 打板事件（first_touch_time/close_sealed/seal_bid_volume/is_one_word/consec_limit/open_board_count）→ L4-05 对照卡真绑定 |
| `c1_market.limit_up_pool` | 2026-09-01..2026-10-09 | 1,426 | 789 | first_seal_time/last_seal_time/seal_amount/seal_ratio/open_board_count/turnover_rate → L4-05 封单质量档 |
| `c1_market.tick_data` | 2026-01-05..2026-10-08 | 3,943,831,530 | 11,811 | 逐笔（bid/ask price+volume，market_type 含 stock/etf/index/cb/sector/futures/mkt_index/stock_bj/lof）→ 到达价/滑点/成交仿真主料 |
| `c1_market.tick_depth_5` | 2026-07-24..2026-09-30 | 130,146,982 | 8,720 | 5 档盘口（MatchingLogic.TickSnapshot 口径）→ 限价 vs 市价、部分成交卡 |
| `c1_market.auction_book` | 2026-07-21..2026-09-30 | 3,690,473 | 6,071 | 竞价期盘口（upper_limit/lower_limit/last_price）→ 9:15-9:25 竞价铁律卡 |
| `c1_market.auction_snapshot` | 2026-06-01..2026-09-30 | 288,909 | 6,590 | 竞价成交价/量 → 开盘时点与尾盘竞价对照 |
| `c1_market.kline_etf_1min` | 2021-07-01..2026-10-09 | 292,584,491 | 1,699 | ETF 分钟线（个股无分钟线，仅 tick）→ 盘中时点族可用代理 |
| `c1_market.kline_etf_5min` | 2005-02-23..2026-10-09 | 72,834,407 | 1,699 | 长窗 5 分钟（时点卡长窗替代） |
| `c1_market.option_kline` | 2026-07-30..2026-10-09 | 8,877 | 302 | 期权线（L1-S4 IV 主路径长窗不可得，实测仅 2.5 个月） |
| `c1_market.margin_trading` | 2024-09-02..2026-10-08 | 2,100,709 | 4,933 | 两融（L1-S0 流动性轴长窗缺） |
| `c1_market.crypto_kline_daily` | 2025-08-08..2026-10-08 | 19,801 | 141（含 BTCUSDT） | 币圈 TDM-C-L1/C-L4 唯一数据面；窗 14 个月，统计功效弱如实标 |
| `c1_market.emotion_index` | 1991-06-10..2026-10-09 | 8,661 | version=1 | 情绪指数+stage（辅轴目标面） |
| `c1_backtest.sim_trade_log` | 2026-07-17..2026-10-09 | 84 | — | 模拟成交回报（列 action/price/shares/cost_paid/signal_reason/run_id/strategy_id/mode）→ L4-14 反馈环唯一实测面，样本极小如实标 |

### 1.2 广度导生口径实测验证（本车道平行卡的数据腿）

命令（原文，比例口径避开 `pct_change` 恒 0 事故）：

```sql
SELECT toYear(trade_date) AS y, count() AS days, avg(lu), avg(ld), avg(tu), max(lu), round(1-avg(lu)/avg(tu),4)
FROM (SELECT trade_date,
        countIf(r  >= lim-0.002) AS lu, countIf(r <= -(lim-0.002)) AS ld, countIf(rh >= lim-0.002) AS tu
      FROM (SELECT k.trade_date, k.symbol, k.close/nullIf(prev,0)-1 AS r, k.high/nullIf(prev,0)-1 AS rh,
                   ifNull(l.limit_pct,0.1) AS lim
            FROM (SELECT trade_date,symbol,close,high,
                    lagInFrame(close) OVER (PARTITION BY symbol ORDER BY trade_date ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING) AS prev
                  FROM c1_market.kline_daily_hfq WHERE trade_date BETWEEN '2018-12-01' AND '2025-12-31') k
            LEFT JOIN c1_market.stk_limit AS l FINAL ON k.symbol=l.symbol AND k.trade_date=l.trade_date
            WHERE prev>0) GROUP BY trade_date) GROUP BY y ORDER BY y
```

实测输出（年均涨停家数/跌停家数/触板家数/年内最大涨停家数/炸板率=1-lu/tu）：

| 年 | 交易日 | 均涨停 | 均跌停 | 均触板 | 年内最大涨停 | 炸板率 |
|----|--------|--------|--------|--------|-------------|--------|
| 2019 | 244 | 65.4 | 26.9 | 102.2 | 321 | 0.3603 |
| 2020 | 243 | 81.9 | 40.3 | 124.4 | 267 | 0.3420 |
| 2021 | 243 | 87.9 | 26.7 | 131.2 | 165 | 0.3302 |
| 2022 | 242 | 77.0 | 29.7 | 119.5 | 255 | 0.3555 |
| 2023 | 242 | 44.1 | 14.7 | 69.4 | 117 | 0.3643 |
| 2024 | 242 | 89.2 | 44.8 | 144.0 | **1034** | 0.3807 |
| 2025 | 243 | 77.0 | 31.0 | 116.6 | 177 | 0.3398 |

判读：2024 年峰值 1034 家=2024-09-30 已知行情事件，量级与外部常识一致；炸板率 0.33-0.38 稳定带 ⇒ 导生口径可用，
且 **2019-01-04..2025-09-09 全冻结窗逐年有完整交易日**（242-244 天/年）⇒ 广度平行卡可运行（非 blocked_on_data）。
2018-12 起 19 天为 lag 暖机残段（日均 4.3 家，样本口径不完整）→ 卡内 `buckets.min_obs_per_bucket` 与窗首剔除说明写死。

### 1.3 执行侧基建反查（L4 卡只准绑真实件，命令原文）

`git grep -niE "slippage|fill|execution_cost|vwap" D:/ZephyrAlpha/scripts/backtest` 命中（择要）+ 逐个读件核实存在：

| 基建 | 锚点（实测在件） | 可绑的考法 |
|------|-----------------|-----------|
| 撮合核 | `src/zephyr/backtest/core/matching_logic.py`：`MatchingConfig(commission_rate=万0.854, slippage_bps=None→逐笔按标定真源, stamp_tax_rate, transfer_fee_rate, min_commission=5, lot_size=100, price_limit_pct=0.10)`、`TickSnapshot`(5 档)、`MatchingFill(quantity,price,commission,slippage_cost,filled,filled_quantity,decision_price)` | 成交/滑点/部分成交类对照卡（回测=实盘一致核） |
| 成本标定真源 | `src/zephyr/backtest/core/cost_model_calibration.py`：`liquidity_tier(daily_notional_yuan)`/`slippage_bps_for_notional`/`slippage_bps_universal`/`resolve_slippage_bps`/`n_tiers` | 滑点档开/关对拍、成本门（L4-09） |
| 档位扫描引擎口径 | `scripts/backtest/factory_grid_executor.py`：`exec_caliber=close|next_open|vwap` 透传引擎 + `_vwap_from_amount_volume` + `cost_attribution_row(avg_turnover_1side,days,slippage_bp)`（常量 COMMISSION_BP/SLIPPAGE_BP/STAMP_BP 来自 `_c4_engine`）；INVARIANT「引擎口径唯一=daily_net_returns slippage_bp kwarg，禁二次回测」 | 下单时点/成交价口径对照（L4-02/L4-03/L4） |
| 成本档真源 | `config/exam_scale_cost_gate.yaml`（`tiers_bp`）+ `scripts/backtest/cost_accounting_ruler.py`（R3 档内判据，`EXAM_SLIPPAGE_BP_BASELINE=5.0`）+ `scripts/backtest/calibrate_cost_tier_redblue.py`（同格对拍 run_backtest(slippage_bp=)） | 成本门柱数值取值真源（禁自造 bp） |
| 双臂对照仿真器 | `scripts/backtest/fexam/exit_sim/exit_simulator.py` + 同目录 `prereg_frozen.yaml`（WARM_START 2017-10-01 / WINDOW_RUN 2018-01-02..2026-09-30 / IS 2018-01-02..2025-09-30 / OOS = ch_data.WINDOW_HOLDOUT 2025-10-09..2026-09-30，COMMISSION 取 matching_logic） | 执行规则开/关两档对拍现成装置（含 MaxDD 增益判据先例） |
| 滑点分量归因 | `src/zephyr/ex_sor/services/slippage_analyzer.py`：`SlippageBenchmark{ARRIVAL,VWAP,TWAP,PREV_CLOSE,DECISION}`、`SlippageAttribution`（三因子+残差）、`ImpactModel.predict(coefficient)` | L4-14 实测滑点分量与预估对照 |
| 执行报告 | `src/zephyr/ex_core/execution_report.py`：`build_execution_report`、`_signed_slippage_bps(side,intended_price,avg_fill_price)` | 带符号滑点口径（正=不利） |
| 选型/评分/对账 | `src/zephyr/ex_sor/core/algo_execution_selector.py`、`src/zephyr/ex_sor/services/execution_quality_scorer.py`、`src/zephyr/trading/three_way_reconciliation.py`、`src/zephyr/ex_core/{order_splitter,pricing_policy,daban_execution,local_order_queue,order_manager,fill_handler,pre_execution_checker,price_cage}.py` | 各子环节 module_ref 逐件 `[ -f ]` 实测 18/18 全在（见 §1.4） |
| 盘后质量先验回写 | L4-06 NOTE 实测：`total*(1+0.20*(2q-1))` 调制、q 缺样返 None 走中性（`ScorerBackedQualityPrior`，2026-09-27 闭环） | 反馈环开/关对拍（L4-14/L4-06） |

### 1.4 断言正查留痕（mining_sop §7.5，负存在断言前必跑）

命令 `python -c "import os; [print('OK' if os.path.isfile(f) else 'MISSING', f) for f in [...]]"` 对 18 个 `module_ref` 件逐个核 ⇒ **18/18 OK**（ex_core 8 件 + ex_sor 2 件 + three_way_reconciliation + plan_engine 5 件 + capital_allocator + breakout_failure_detector），故 L4/L0 卡一律有真实件可绑，不虚构接口。

<!-- 后续 `python -m zephyr.library.lookup state` 摘录按节点追加于 §1.5 -->


## 二、逐节点六向台账

| node_id | 六向结论(每向一句) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---------|-------------------|--------|--------|-----------|-------------|
| TDM-E-L1-S2 | ①上游=data_refs DS-082/DS-108（limit_up_down/limit_up_pool/daban_board_event）实测冻结窗零行，长窗唯一口径=stk_limit(2015-01-05 起/9.25M 行)+日线导生，已入卡；②下游=`git grep -ln TDM-E-L1-S2` 消费方=L1-AGG 情绪六段轴与 emotion_index components（C1_limitup_temp 实测 source='daban_board_event'），广度卡该考"喂给 AGG 的状态判定掉多少"→归 AGG 消融卡不重复立；③算法=母卡 02-08 同族先例七张，机构三件套沿用响应曲线/IC 地板/牛熊同号（外部 URL 待复挖批，本轮未取到合格引文=受阻非查无）；④后端=module_ref `src/zephyr/signal_ashare/limit_up/limit_up_followthrough.py` 实测存在（`[ -f ]` OK），ALGO_FLOW 已出仓至 `_domain_signal/algo_flow/limit_up_followthrough.yaml`；⑤呈现=只登记（作战室广度面板已有件，不施工）；⑥数据=逐年实测 244/243/243/242/242/242/243 交易日完整，join 0 unmatched/7,590,928，`pct_change` 列恒 0 事故已写入各卡 derivation 禁消费条款 | 7 | calibration×7（09-15 全为母卡 02-08 的导生口径平行卡） | 否——六向中③外部机构对照向为"受阻未查无"，长尾留跨源验证 | 无（母卡 7 张为 blocked_on_data 性质，本车道以平行卡解，不改母卡） |
| TDM-E-L1-S3 | ①上游=DS-082/DS-107 涨停集合与溢价需"昨涨停今表现"截面，导生口径成立；②下游=晋级率喂 emotion_index components C2_promotion（实测 components 含 C1_limitup_temp/C2_promotion 命名）+L4-05 打板接力；③算法=母卡 02/03/04 先例，先锋四态母卡 04 需"昨日最高连板股今日开盘状态"，导生可做但需 streak 串+开盘价双条件，本轮列为长尾；④后端=`src/zephyr/signal_ashare/limit_up/lhb_premium_analyzer.py` 在 TDM 记为 module_ref（件存在性见 §1.4 核 18/18 未含此件，另核于本行末：存在性=待核，卡未绑该件只绑数据口径）；⑤呈现=只登记；⑥数据=溢价/晋级率导生全窗可得（实测涨停家数年均 44-89 只，截面规模充足），情绪指数辅轴逐年 242-244 天完整 | 2 | calibration×2（S3/05 溢价、S3/06 晋级率） | 否——先锋四态平行卡（S3/07）与 lhb 件存在性核对列长尾 | 无 |
| TDM-E-L4 | ①上游=本节点 data_refs 空但 module_mounts 5 件（MOD-EX-049/050/055/EXE-AGENTS/TRIG-001），执行层该收的"信息"=成交价口径与成本档而非新数据源，已入卡；②下游=节点为"全流终端"之一（TDM-E-FLOW 上游），执行结果该喂 L4-14 成本反馈环，已在 L4-14 卡立；③算法=同族先例=exit_simulator 双臂（Sharpe+MaxDD）与 calibrate_cost_tier_redblue 五档扫描，外部锚 Almgren-Chriss 2000 在 TDM L4-14 algo_note 已带年份，本仓裁定"Almgren-Chriss 不采纳进 MVP"（90_methodology_open_questions.md L259 实测摘录）⇒ 卡内影响模型口径按平方根律+档位锚，不吹新模型；④后端=引擎 `daily_net_returns(weights,px_close,gate_limits,slippage_bp,*,exec_caliber,px_exec)` 实测三档口径全可切（_c4_engine L770-780/L627-631）；⑤呈现=只登记；⑥数据=日线 1990..2026-09-30/10.1M 行长窗齐，ETF 5min 2005 起 72.8M 行，个股分钟缺（实测无个股 1min 表）已写进臂定义降级条款 | 1 | comparison×1 | 否——长尾=execution_caliber 与规模维（participation_rate）联合扫描的 2D 版卡、币圈代理口径 | blocked_on_impl=comparison 族卡驱动执行器（1 件，全族共用） |
| TDM-E-L4-01 | ①上游=DS-150 日线；分批的输入=置信度档（A/B/C 回踩为调节因子，L3 族产出）；②下游=喂 L4-06 算法选型与 L4-08 失败降级（首仓失败不加仓），已在两卡中显式引用；③算法=同族先例 exit_simulator 双臂 + 换手成本式（cost=turnover*(COMMISSION_BP*2+STAMP_BP+slip*2)/1e4 实测 L702）；④后端=`src/zephyr/ex_core/order_splitter.py` 实测存在（§1.4 18/18）；⑤呈现=只登记；⑥数据=日线全窗齐；"站稳分时均线"确认腿在个股长窗无分钟线（实测），卡内先验写死为日线 4 点近似并标退化 | 1 | comparison×1 | 否——长尾=首批比例与置信度档联动（而非固定三档）版 | blocked_on_impl=comparison 执行器（共用） |
| TDM-E-L4-02 | ①上游=DS-150 + 竞价面（auction_snapshot/auction_book 实测）；②下游=下单时点直接决定 L4-06 算法窗口与 L4-03 限价锚，两卡互相引用；③算法=尾盘效应外部文献本轮未取得合格 URL（受阻非查无，入长尾）；④后端=`src/zephyr/plan_engine/closing_session_decision.py`（TDM module_ref，实测存在）+ `batched_position_builder`（TDM 记名，未单独核）；⑤呈现=只登记；⑥数据=时点四臂长窗受限于"个股无分钟线"（实测结论），竞价臂仅 2026-06-01..09-30 可用 ⇒ 长窗版降为三臂并如实标 blocked_on_data | 1 | comparison×1 | 否——竞价铁律（9:15-9:20 可撤假象/9:20-9:25 只挂不撤）单独立卡列长尾，数据面 auction_book 已在册 | blocked_on_data=个股盘中分钟线历史段（2019-01-04..2025-09-09 缺）；blocked_on_impl=comparison 执行器 |
| TDM-E-L4-03 | ①上游=盘口 5 档（tick_depth_5 实测 2026-07-24 起 130M 行）；②下游=成交价直接进 L4-14 实测滑点账与 L4-09 成本门；③算法=撮合核 matching_logic（TickSnapshot/MatchingFill 实测在件，列名与 tick_depth_5 一一对应），无外部新法；④后端=`src/zephyr/ex_core/pricing_policy.py` 实测存在；⑤呈现=只登记；⑥数据=窗仅 35+11 交易日（数据上限，卡内先验把主判据定为排序方向非显著性） | 1 | comparison×1 | 否——长尾=价格笼子（申报价±2%）与限价偏移的交互臂，件在（price_cage.py）数据在（stk_limit） | blocked_on_impl=tick 级三臂撮合驱动器（1 件）+ comparison 执行器 |
| TDM-E-L4-05 | ①上游=daban_board_event(1,767 行/975 标的)+limit_up_pool(1,426 行)+tick_depth_5，三表列实测齐（first_touch_time/open_board_count/close_sealed/seal_bid_volume/seal_ratio/turnover_rate/float_market_cap）；②下游=打板成交结果喂 L4-14 分量归因与 L3-06 环境开关；③算法=内部先例=limit_up_followthrough ALGO_FLOW（已出仓至 _domain_signal/algo_flow/）；成本分档锚取本仓裁定（高流动 0.05-0.1%、打板/事件 0.15-0.3% 并乘成交概率折减，90_methodology_open_questions.md L259 实测摘录），禁凭模型记忆造外部数；④后端=`src/zephyr/ex_core/daban_execution.py` 实测存在；⑤呈现=只登记；⑥数据=事件明细仅 2026-09-01 起 ⇒ 卡整体受限于单月窗，历史段 blocked_on_data 明列 | 1 | comparison×1 | 否——长尾=撤单纪律（封单骤减 20% 立即撤）的盘中逐笔版（需 tick 级队列模型） | blocked_on_data=打板事件历史回填（2015-01-05..2026-08-31 缺）；blocked_on_impl=comparison 执行器 |
| TDM-E-L4-08 | ①上游=DS-150 日线（入场价/10 日低）+ stk_limit 跌停不可成交约束；②下游=降级信号喂 L4-01 批次控制与卖出决策族（P 流），本卡三臂设计含"只暂停不加仓"分离臂即为归因下游；③算法=同族先例 exit_simulator ATR 双臂（STOP_MULT/ATR_N 冻结件先例，窗口口径直接借用其 IS/OOS 切法）；④后端=`src/zephyr/sell_decision/core/breakout_failure_detector.py` 实测存在（§1.4）；⑤呈现=只登记；⑥数据=长窗全齐（日线 10.1M 行 + stk_limit 9.25M 行 + join 0 unmatched），本车道最"能跑"的一张 L4 卡 | 1 | comparison×1 | 否——六向全部入卡或已查无（③外部文献向与⑤呈现为登记性结论），本节点判 mined_out 证据充分后再封 | blocked_on_impl=comparison 执行器（数据/引擎零缺口） |
| TDM-E-L4-09 | ①上游=DS-082（涨跌停）+ 成交额（ADV，规模维 participation_rate 输入，实测 scale_gate 已在冻结册声明）；②下游=硬约束结论供全部 L4 卡做口径折扣；③算法=冻结成本门件即本仓考尺（exam_scale_cost_gate.yaml 全文实读，含 Owner 2026-09-30 批复 B 案 v2.0.0 块），未引外部新法；④后端=`src/zephyr/ex_core/price_cage.py` 实测存在；引擎形参 `gate_limits` 实测可切（L770-780）；⑤呈现=只登记；⑥数据=长窗全齐，触板规模实测（日均数十只被闸挡下，非边缘情形） | 1 | comparison×1 | 否——长尾=T+1 约束单独臂（当日买入不可卖）与持仓限额臂的独立量化卡 | blocked_on_impl=comparison 执行器 + 逐票预期收益比较器（拒单集合需 1 件，实测不存在不虚构） |
| TDM-E-L4-04 | ①上游=清单+可用资金（组合内生），无新数据源；②下游=分配结果喂 L4-06 算法选型与 L4-01 分批，本卡臂间只动次序以隔离贡献；③算法=外部"资金分配排序"文献本轮未取回合格 URL（受阻非查无）；④后端=`src/zephyr/signal_fundamental/capital/capital_allocator.py` 实测存在（§1.4 18/18）；⑤呈现=只登记；⑥数据=价格面全窗齐，生产"置信度"在册表实测缺位 ⇒ 卡内以截面秩代理并显式标注，禁冒充 | 1 | comparison×1 | 否 | blocked_on_impl=置信度入参面 + comparison 执行器 |
| TDM-E-L4-06 | ①上游=六件算法（EXA-TWAP/VWAP/ICEBERG/IS/POV/ALT，TDM algo_refs 实记）+参与率纪律；②下游=选型结果被 L4-14 反馈环回写（2026-09-27 闭环在 TDM 原文实测记载，含 `total*(1+0.20*(2q-1))` 公式），两卡互绑；③算法=内部先例=selector 件 + 安慰剂臂自反设计（外部 Almgren-Chriss 在本仓被裁定"不采纳进 MVP"，见 90_methodology_open_questions.md L259 摘录，禁当外部权威引用）；④后端=`algo_execution_selector.py`+`execution_quality_scorer.py` 均实测存在；⑤呈现=只登记；⑥数据=tick_data 3.9B 行可做参与率，实测成交仅 84 笔 ⇒ 主判据面功效弱已先验声明 | 1 | comparison×1 | 否 | blocked_on_impl=tick 重放成交账 + comparison 执行器；blocked_on_data=成交明细历史（2026-07-17 前缺） |
| TDM-E-L4-07 | ①上游=四类触发器（价格/时间/指标/风控）；②下游=队列输出直接决定 L4-10/L4-11 的入单序；③算法=同族消融先例=骨架 `TDM-E-L4-07__ablation.yaml`（族已定 ablation，本卡照族）；④后端=`local_order_queue.py` 实测存在 + MOD-TRIG-001；⑤呈现=只登记；⑥数据=tick 面齐但**触发事件流水无表**（实测 system.tables 检索零命中）⇒ 事件计数面必须靠注入器 | 1 | ablation×1 | 否 | blocked_on_impl=触发事件流水入库 + tick 重放器 + comparison/ablation 执行器 |
| TDM-E-L4-10 | ①上游=订单状态事件（实测无表，仅 sim_* 族 26-331 行小账）；②下游=状态机喂 L4-11/L4-13；③算法=九态与超时策略取 algo_note+实现件常量，未引外部；④后端=`order_manager.py` 实测存在，五闸链（F62 P0-10，2026-09-28）在 TDM 原文实记；⑤呈现=只登记；⑥数据=sim_trade_log 84 行 + 无中间态列（实测列集 12 项已核）⇒ 窗最短、功效最弱，卡内先验禁显著性宣称 | 1 | comparison×1 | 否 | blocked_on_data=委托回报与中间态时序；blocked_on_impl=comparison 执行器 |
| TDM-E-L4-11 | ①上游=tick_depth_5 剩余量可成交性；②下游=成交结果进 L4-14 滑点账；③算法=撮合核 matching_logic 实测（MatchingFill 含 filled/filled_quantity 两字段，正是本卡原料）；④后端=`fill_handler.py` 实测存在；⑤呈现=只登记；⑥数据=tick_depth_5 仅 2026-07-24..09-30（实测 130M 行/8,720 标的）⇒ 窗 35+11 天，竞态柱因无券商时序标 blocked 不硬判 | 1 | comparison×1 | 否 | blocked_on_impl=tick 重放驱动器 + comparison 执行器；blocked_on_data=撤改回报时序 |
| TDM-E-L4-12 | ①上游=五查各自输入（ST=stk_limit.st_flag 实测列、笼子价=pre_close/limit_up 实测列、资金/限额/熔断=组合内生）；②下游=拒单集合喂 L4-09 成本门与治理冗余门审计；③算法=逐条消融设计（六臂），无外部引用需求；④后端=`pre_execution_checker.py`+`price_cage.py` 实测存在；⑤呈现=只登记；⑥数据=长窗全齐（日线 10.1M + stk_limit 9.25M + join 0 unmatched）⇒ 本车道 L4 段第二可跑卡 | 1 | comparison×1 | 否 | blocked_on_impl=comparison 执行器（数据/引擎零缺口） |
| TDM-E-L4-13 | ①上游=三方账（本地 sim_trade_log 实测有、委托侧与成交确认侧实测无表）；②下游=对账结果约束次日开盘可否交易；③算法=无外部法（工程正确性验收）；④后端=`three_way_reconciliation.py` 实测存在（MOD-EX-002/003/056/RK-19 挂载记名）；⑤呈现=只登记；⑥数据=两份账缺 ⇒ 只能以故障注入仿真落地，卡内先验标注 injection=simulated | 1 | comparison×1 | 否 | blocked_on_data=券商委托回报+成交确认两份流水；blocked_on_impl=故障注入驱动器 + comparison 执行器 |
| TDM-E-L4-14 | ①上游=DS-008 成交回报 + 预估两档（一口价/流动性分层，件内实测函数）；②下游=回写 q 先验进 L4-06 选型（同战役跨卡对账点）；③算法=三分量归因取件内 SlippageAttribution 口径，外部锚（分策略滑点档）取本仓裁定 L259 摘录；④后端=`execution_quality_scorer.py`/`slippage_analyzer.py`/`execution_report.py`/`cost_model_calibration.py` 四件均实测在；⑤呈现=只登记；⑥数据=sim_trade_log 84 行 + tick 3.9B 行（可重放补足）⇒ 主判据改"方向一致率"，卡内先验禁显著性 | 1 | comparison×1 | 否 | blocked_on_data=实测成交样本；blocked_on_impl=order_id→算法归因账 + comparison 执行器 |
| TDM-C-L4 | ①上游=币圈日线（crypto_kline_daily 实测 2025-08-08..2026-10-08/141 标的）；②下游=进场决策喂币圈风控族（未施工）；③算法=ATR 口径直接复用 exit_simulator.wilder_atr_one（实测函数，复用禁重造）；④后端=TDM 节点 module_ref=null（实测）⇒ 无件可绑，卡为"先有可考口径再施工"的准入材料；⑤呈现=只登记；⑥数据=日频齐、分钟缺（实测无币圈分钟表），止损触发只能收盘检查并标注 | 1 | comparison×1 | 否 | blocked_on_impl=币圈执行件（节点空壳）+ comparison 执行器 |
| TDM-E-FLOW | ①上游=L0 计划 + L2/L3 选股 + L4 执行三段（节点为终端聚合）；②下游=无（终点，TDM 原文"下游无"实测照录）；③算法=全链消融先例=骨架卡 family=comparison + L1-AGG 消融设计同构；④后端=module_ref=null、module_mounts=['MOD-SIG-087']（实测名册），件存在性未逐一核（记待核，不虚构）；⑤呈现=只登记；⑥数据=三段各自数据面均实测齐 ⇒ 卡可跑（除执行器件） | 1 | comparison×1 | 否 | blocked_on_impl=comparison 执行器 |
| TDM-E-L0 | ①上游=C3-01 归因/C3-04 校准/L1-AGG 宏观态（TDM 原文实记）；②下游=计划喂 L3-06 环境开关/L4 执行/X 离场；③算法=计划开/关四臂对照含"禁做清单三源"可核两源，人工政策源实测无结构化历史 ⇒ 明标 blocked；④后端=`daily_warroom_pipeline.py` 等 plan_engine 5 件实测存在（§1.4）；⑤呈现=只登记（作战室卡已有件）；⑥数据=闸输入 regime_state_anchored 2017-07-11 起 4,488 行实测齐，计划实录仅 judgment_* 12/24/6 行 ⇒ 以规则重放臂落地 | 1 | comparison×1 | 否 | blocked_on_data=盘前计划逐日流水；blocked_on_impl=comparison 执行器 |
| TDM-E-L0-01 | ①上游=DAL-SCEN-PROB（MOD-PLAN-017）九格情景概率；②下游=立场档喂 L0 总仓位与 L4-01 首批比例；③算法=事件研究/概率定档属仓内既有链，外部无新增需求；④后端=`daily_trade_plan.py`+`scenario_probability_model.py`+`similar_day_inference.py` 三件实测存在；⑤呈现=只登记；⑥数据=指数日线 1,843 行（000300）暖机足；情景概率逐日落库实测无表 ⇒ 重放臂 + 反向臂（防方向错） | 1 | comparison×1 | 否 | blocked_on_impl=当日情景概率实录账 + comparison 执行器 |
| TDM-E-L0-02 | ①上游=当日计划边界 + 盘中实际；②下游=修订结果反喂当日执行与归因；③算法=含 REV_LEAK_TEST 构造违例臂（专测 premarket_constraint_loader 过期拒发），属自反设计非外部法；④后端=`plan_deviation_monitor.py`+`premarket_constraint_loader.py` 实测存在；`boundary_revision_engine` 件名仅在 TDM 记名，本车道未定位到同名文件 ⇒ 卡内标注"待逐件核"不写死路径；⑤呈现=只登记；⑥数据=盘中代理 kline_etf_1min（2021-07-01 起，实测）钉死窗起点 | 1 | comparison×1 | 否 | blocked_on_impl=修订逐日流水 + comparison 执行器；blocked_on_data=2021-07-01 前盘中面 |
| TDM-E-L0-03 | ①上游=closing_session_decision→brier_calibration→tomorrow_boundary_planner 三链（TDM 原文实记）；②下游=明日边界喂次日 L3-06/L4/X 离场；③算法=Brier/可靠性曲线属标准概率学验收，仓内件既有口径优先（禁自造校准法）；④后端=三件实测存在（find 核）；⑤呈现=只登记；⑥数据=真值面 emotion_index 逐年 242-244 天完整（实测）+ 四档 dominant 第二套真值；概率逐日实录缺 ⇒ 重放臂 + 双真值交叉 | 1 | comparison×1 | 否 | blocked_on_data=八态概率与边界逐日实录（2019-2026 无表）；blocked_on_impl=comparison 执行器 |
| TDM-E-L0-04 | ①上游=DS-150/DS-082/DS-107 + DAL-8STATE-FCST（TDM 实记 data_refs）；②下游=降档预警喂偏离监控（L0-02）与三处反哺 D123-①②③；③算法=外部文献（Lou-Poli-Gao / Renault JBF 2017 / SSRN 5599654）仅 TDM 记题，本车道未取回 URL+发布方+年份全文核对 ⇒ 记"受阻非查无"入长尾；④后端=`intraday_tomorrow_forecast.py`（纯函数核零 IO，TDM 原文）实测存在；⑤呈现=只登记；⑥数据=盘中四时点用 ETF 1min 代理（实测 2021-07-01 起 292M 行）+ tick 短窗复核版；情绪真值 2026 实测 186 天 | 1 | comparison×1 | 否 | blocked_on_data=2021-07-01 前盘中面；blocked_on_impl=comparison 执行器 |
| TDM-E-L1 | ①上游=RegimeSnapshot 7 态概率（regime_snapshot_history 实测 3,635 行）+ 六段预算带；②下游=总仓位上限喂 L0 与全流；③算法=凯利简版/波动率目标化取仓内件（vol_target_allocator MOD-BT-082 记名），裁定#304 HMM 锚定与 R-055a fail-closed 数值口径逐字照录为臂参数；④后端=`regime_detector.py` 实测存在（名册 confidence=verified，本节点是全车道唯一已验收节点，判据须与其实测账对账）；⑤呈现=只登记；⑤数据=anchored 表 2017-07-11 起长窗齐 ⇒ 闸类最可跑卡 | 1 | comparison×1 | 否 | blocked_on_impl=comparison 执行器 |
| TDM-E-L1-AGG | ①上游=DS-098 宏观四档 × 情绪六段（两表实测覆盖齐）；②下游=三件套（预算带/六段态/策略路由）broadcast 全图，消融必须看全链掉幅而非单环；③算法=消融四档替换（随机/固定/旁路×2）先验冻结，防"常数测试"漏判；④后端=`anchored_state_machine.py` 实测存在；回滚开关 anchored_cap.disabled 机制 TDM 原文实记（回滚窗至 2026-10-23）；⑤呈现=只登记；⑥数据=regime_state_anchored 4,488 行 + emotion_index 全窗 ⇒ 数据腿齐 | 1 | ablation×1 | 否 | blocked_on_impl=状态输入注入器（消融必需）+ comparison/ablation 执行器 |
| TDM-E-L1-S0 | ①上游=四维（货币/流动性/海外/政策）逐轴核 CH：货币=M1/M2 月度实测 1,166 行（1978-2026-08），流动性=两融实测 2.1M 行但仅 2024-09-02 起，海外=kline_global 实测仅 CL/GC/HSI/KOSPI/N225/USDCNH 六标的（**无纳指/标普**），政策=rate_decision_calendar 实测含 1970-01-01 脏哨兵；②下游=宏观支撑/压制分喂 L1-AGG；③算法=事件研究法（母卡已用），本车道补状态型序列；④后端=`policy_expectation_analyzer.py`（TDM module_ref）；⑤呈现=只登记；⑥数据=两轴入卡，海外轴 blocked_on_data（缺美股指数）、政策轴 blocked_on_data（人工录入无结构史+脏日期） | 2 | calibration×2 | 否——海外轴/政策轴解 blocked 后各需一卡（列长尾） | blocked_on_data=隔夜美股指数（kline_global 无 NDX/SPX）+ 政策人工录入结构化历史 |
| TDM-E-L1-S0-1 | ①上游=news_sentiment_window（scope='market' 实测 2019-01-04..2026-10-08/2,622 行，单标的）+ 上游明细 news_sentiment_score 7.9M 行；②下游=市场级+板块级读数喂 L1-S0 与 L2-09 事件链（TDM 原文）；③算法=均值型之外补"分歧度"正交面（本车道新命题，非母卡重复）；④后端=`news_sentiment_analyzer.py` 实测存在；⑤呈现=只登记；⑥数据=2019-2024 全年覆盖、2025 起变稀（实测 243/201 行/年）⇒ OOS 段功效风险已写进 calendar_coverage_guard | 1 | calibration×1 | 否——板块级 scope 与逐条打分口径跨版本对齐列长尾 | 无（2025 后稀疏为已知风险，标柱不标卡） |
| TDM-E-L1-S1 | ①上游=DS-150 指数 OHLC（实测 000300 1,843 行 2018-06-01..2025-12-31）；②下游=指数趋势分(-2~+2)喂 L1-AGG 宏观轴；③算法=MA 排列/距高点（DAL-MA-ALIGN 记名）与母卡 02 同题——**母卡 02 数据腿实测成立，无需平行卡**（本行即"已查无可补"结论）；④后端=`regime/features/index_sensor.py`（TDM module_ref，未逐件 find，记待核）；⑤呈现=只登记；⑥数据=母卡 03（黄白线交叉）需盘中分时——实测个股/指数分钟面无长窗（ETF 1min 自 2021-07-01），黄白线本身是指数分时概念 ⇒ 母卡 03 属 blocked_on_data，本车道未为其造代理（代理=换命题，禁） | 0 | — | 否——长尾=黄白线代理是否等价（需先定代理合法性再立卡） | 未立卡原因：唯一可判面已被母卡 02 覆盖，代理口径会改变命题（诚实优先，不凑数） |
| TDM-E-L1-S4 | ①上游=DS-150 close（后备路径"仅依赖 close"，TDM 原文）+ 期权面 option_kline（实测 2026-07-30 起/8,877 行）；②下游=vix_pct 喂 L1 波动目标化与 L1-AGG 熔断 cap 公式；③算法=合成 VIX/下行半偏差/CBOE 简化 VIX 三式均在 algo_note 内写明，件锚 MOD-REGIME-011/013；④后端=`regime/features/synthetic_vix.py` 实测存在；⑤呈现=只登记；⑥数据=主路径母卡 02 blocked_on_data（期权历史缺）+ SVX-1-P0 delta 恒 0 事故实记 ⇒ 本车道立后备路径长窗卡（04） | 1 | calibration×1 | 否——主路径 IV 曲面解 blocked 后需回填卡（长尾）；已把"主备切换逻辑"列第二长尾 | blocked_on_data（母卡侧）=期权 IV 曲面 2026-07-30 前历史；本卡不受阻 |
| TDM-E-L1-S5 | ①上游=DS-082/DS-059/DS-150（11 信号原料）；②下游=S0-S4 五档水温是 L1-AGG 唯一盘中可变输入；③算法=环比 z 分数合成（母卡同题），本车道取 11 项中日线可导生 7 项做长窗版并先验声明覆盖度 7/11；④后端=`signal_ashare/core/daily_condition_sensor.py`（TDM module_ref）；⑤呈现=只登记；⑥数据=盘中精确版受"个股分钟线缺"限制（实测），日频导生子集全窗齐 | 1 | calibration×1 | 否——剩余 4 项（盘中炸板走向等）解 blocked 后另卡（长尾） | blocked_on_data（母卡侧）=盘中 9:35 首算历史；本卡为日频子集版 |
| TDM-C-L1 | ①上游=BTC 日线 + ALT/BTC 汇率（crypto_kline_daily 实测 141 标的含 BTCUSDT）；②下游=趋势档/进攻档喂币圈总仓位与 C-L4；③算法=200 日线+斜率、山寨季宽度（内部无先例件，属新立）；④后端=节点 module_ref=null、confidence=untested（实测）⇒ 空壳，卡为准入材料；⑤呈现=只登记；⑥数据=MA200 有效窗实测从 2026-03-02 起（表起点 2025-08-08 加 200 交易日暖机），OOS 仅 27 交易日 ⇒ 先验禁显著性 | 1 | comparison×1 | 否 | blocked_on_impl=币圈仓位闸实现（节点空壳）+ comparison 执行器；blocked_on_data=币圈历史深度 |

## 三、正查留痕（mining_sop §7.5 负存在断言三源正查，命令与输出摘录）

1. `python -m zephyr.library.lookup state "对照卡执行器"` →
   `source-1 馆索引: -- no hits -- / source-2 git log(90d): -- no hits -- / source-3 工棚+挂账面: -- no hits --`，
   `sources-with-hits: 0/3`（快照 2026-10-10T07:23:57+08:00）。
   ⇒ 支撑本车道全部 L4/L0/L1 闸卡的 `blocked_on_impl=comparison 族卡驱动执行器` 断言（0/3 源命中=未做，非凭记忆）。
2. `python -m zephyr.library.lookup state "comparison 族 执行器"` → source-1 命中件仅为**骨架卡文件本身**
   （`exam_cards/entry_flow/L0/TDM-E-L0-0{1,2,3,4}__comparison.yaml` 等 generated 件），无执行器件
   ⇒ 与结论 1 一致：族卡在册、驱动器缺位。
3. `python -m zephyr.library.lookup state "滑点 仿真 撮合"` → source-1 命中
   `TBL:ch:c1_backtest.sim_daily_report 仿真日报`、`TBL:ch:c1_backtest.sim_trade_log 仿真成交流水`；
   source-2 git log 命中 T3a/考试卡战役等提交 ⇒ 撮合/仿真面**存在但为日频小账**，
   据此追加实测（见 §3.4）并修正表述：本车道断言不是"无仿真"，而是"无 tick 级三臂撮合驱动器/无订单中间态流水"。
4. 追加实测（命令 `SELECT database,name,total_rows FROM system.tables WHERE name ILIKE 'sim%'`）：
   `sim_attribution_daily 88`、`sim_daily_report 264`、`sim_platform_journal 26`、`sim_pocket_daily 331`、`sim_trade_log 84`；
   `sim_daily_report` 列实测 19 项（含 target_position/actual_position 于 payload、realized_scenario、eval_score、synthetic 标记）
   ⇒ 位置类实测账存在但样本 <350 行且带 `synthetic` 位，不能充当 L4-10/13 所需的状态机事件流水（断言按此收窄，未夸大）。
5. 宏观/新闻轴正查（命令 `SELECT ... FROM system.tables WHERE name ILIKE '%rate%'/'%macro%'/'%news%'/'%sentiment%'`）
   → `market_china_bond_yield 10,416（2025-09-23 起）`、`rate_decision_calendar 6,172（1970-01-01 脏哨兵..2025-10-30，11 央行）`、
   `macro_credit_money 1,166（1978-01-31..2026-08-31）`、`news_sentiment_window 22,257`、
   `c3_fundamental.news_sentiment_score 7,947,739`、`kline_global 13,133（仅 CL/GC/HSI/KOSPI/N225/USDCNH）`
   ⇒ 支撑"海外轴隔夜美股 blocked_on_data"与"货币 M1/M2 长窗可用、流动性两融短窗可用"两条结论。
6. 订单/委托回报侧负断言正查：`SELECT database,name FROM system.tables WHERE name ILIKE '%order%' OR '%report%' OR '%recon%' OR '%broker%'`
   （限 c1_market/c1_backtest）→ 实测零命中 ⇒ 支撑 L4-10/L4-11/L4-13 的 blocked_on_data 表述。
7. 件存在性正查（非负断言，但仍留痕）：`find src/zephyr -iname "*<module_name>*"` 对 9 个记名件
   （scenario_probability_model/brier_calibration/similar_day_inference/next_day_8state_forecast/
   batched_position_builder/premarket_constraint_loader/closing_session_decision/breakout_failure_detector/anchored_state_machine）
   → 9/9 命中真实路径；唯一未定位=`boundary_revision_engine`（仅在 TDM algo_note 记名）⇒ 相关卡内标注"待逐件核"，不写死路径。

## 四、车道收尾（32 节点）

- **本车道节点总数**：32（名册 `lane=L3` 权威名单，与任务书逐一对齐：TDM-E-L4+L4-01..14+TDM-C-L4=16；TDM-E-FLOW+L0+L0-01..04=6；L1 层 10 个）。
- **已挖数**：32/32（每节点六向全部留痕，见 §二各行；无未开工节点）。
- **新卡总数**：39 张（YAML 逐件 parse 校验通过，必填面与 `data_binding` 五子项、`pillars_numeric` 五子项零缺失；
  校验命令见本车道临时件记录，全部 `preregistered_by: st-nightmine-20261010-L3`；
  机核结果：cards=39 / bad=0 / families={comparison:23, calibration:14, ablation:2} / 有卡节点=31（第 32 节点 TDM-E-L1-S1 为"已查无可补，不凑数立卡"，见 §二该行与 §四诚实申报）。
- **族分布**：comparison 23、calibration 14、ablation 2（calibration 全数落在 L1 传感器/广度补卡；ablation=L1-AGG 聚合环 + L4-07 队列环，两节点 node_type 均为 aggregation，符合"聚合环节走消融"立法；机核命令见本节末注）。
- **mined_out 名单（严格 §3 结构判据）**：**空**。理由逐条：全部 32 节点的③算法/机制向在本战役内均处于两种状态之一——
  已入卡（可判）或外部检索未取得"URL+发布方+年份"合格引文（=受阻，非查无，§3 明定受阻不算查无、不算封矿依据）；
  另有 §4.6 列出的长尾未挖项。禁以"挖了两轮/时间不够/节点太多"降格封矿，故本车道一律不标 mined_out。
  近枯竭（六向仅剩外部文献一向未闭）：TDM-E-L4-08、TDM-E-L4-09、TDM-E-L4-12、TDM-E-L1、TDM-E-L1-AGG、TDM-E-L1-S2。
- **blocked 名单与原因**：
  - 共用件（全车道唯一硬阻塞）：`comparison/ablation 族卡驱动执行器`缺位（0/3 源正查，§3.1）。
    受影响卡=23 张 comparison + 2 张 ablation（calibration 14 张可由既有 `calibration_exam.run_card` 直接考，不受阻）。
  - blocked_on_data（逐卡写明缺哪表哪段）：L4-02（个股盘中分钟线 2019-2025 缺）、L4-05（打板事件 2015-01-05..2026-08-31 缺）、
    L4-06/L4-14（实测成交回报 2026-07-17 前缺，仅 84 笔）、L4-10/L4-11/L4-13（委托回报/中间态/成交确认三份流水缺）、
    L0/L0-01/L0-02/L0-03/L0-04（计划·概率·边界逐日流水缺，仅 judgment_* 12/24/6 行）、L1-S0 海外轴（kline_global 无 NDX/SPX）、
    L1-S0 政策轴（人工录入无结构史 + rate_decision_calendar 1970 脏哨兵）、L1-S5 母卡盘中版（9:35 首算历史缺）、
    C-L1/C-L4（币圈 MA200 有效窗仅 2026-03 起 + 无币圈分钟/费率实测面）。
  - blocked_on_impl（除共用执行器外的额外缺件）：tick 级三臂撮合重放器（L4-03/06/07/11）、
    下单前逐票预期收益比较器（L4-09）、触发事件流水入库（L4-07）、订单九态事件入库（L4-10）、
    三方账故障注入器（L4-13）、状态输入注入器（L1-AGG）、置信度入参面（L4-04）、币圈执行件（C-L1/C-L4，节点空壳）。
- **未挖长尾清单（明列，非停止判据）**：
  1. 各 L4/L0 comparison 卡的"外部机构对照文献向"（需 URL+发布方+年份+年份核验，本轮 429/受阻）。
  2. L4-03 价格笼子（申报价±2%）与限价偏移的交互臂（件 price_cage.py 在、数据 stk_limit 在，未立卡）。
  3. L4-02 竞价铁律单独卡（9:15-9:20 可撤假象 / 9:20-9:25 只挂不撤；auction_book 实测 3,690,473 行可用）。
  4. L4-01 首批比例与置信度档联动版（非固定三档）。
  5. L4-07 优先级抢占在真实触发事件流水上的复算（待事件入库件）。
  6. L4-05 撤单纪律"封单骤减 20% 立即撤"的 tick 级队列模型版。
  7. L1-S3 情绪先锋四态平行卡（母卡 04 的导生版，需 streak 串 + 开盘价双条件）。
  8. L1-S2 连板家数"分布形状"（母卡 07 的完整分布形态，本车道只落一阶摘要 streak>=2 家数）。
  9. L1-S2 净广度比值型变体（本卡固定差分）。
  10. L1-S4 主路径期权 IV 曲面长窗回填卡（解 blocked 后）。
  11. L1-S4/L1-AGG 主备路径切换逻辑考核卡（本车道明言"未考切换"）。
  12. L1-S5 11 信号剩余 4 项（盘中炸板走向等）的短窗 tick 版（tick_depth_5 实测窗内）。
  13. L1-S0 板块级新闻情绪 scope 与 news_sentiment_score 跨 caliber_version 口径对齐卡。
  14. L1-S0 政策事件轴（结构化录入链建成后可立卡）。
  15. L1-S1 黄白线代理合法性判定（代理=换命题，需先裁定代理口径再立卡）。
  16. L0-03 八态概率双真值（emotion vs anchored dominant）分歧时的第三真值选择。
  17. L0 禁做清单第三源（人工政策/事件）结构化后补卡。
  18. L4-09 T+1 约束单独臂与持仓限额臂的独立量化卡（本卡合并处理）。
  19. L4-06 参与率纪律 10-20% 的经验分布建档（tick 面可算，本卡只设柱未跑）。
  20. C-L1/C-L4 币圈真实费率/滑点实测面与跨所口径（Binance/OKX 分表）建设后复考。
  21. 广度导生口径与事件表口径（2026-09 重叠段）的等价性实证卡（rho>=0.9 判据已写入卡 09 的 caliber_equivalence，未跑）。
  22. `data/strategy_intake/grid_*` 参考 run 的实际 manifest 行数/窗口首跑建档（本车道只核目录存在）。
- **建议交叉复挖 20% 名单（6-7 个节点，交他道或复挖批）**：
  TDM-E-L4（与 L2/L3 选股道交叉：口径差值对 alpha 的侵蚀归属）、TDM-E-L4-09（与治理道交叉：门的冗余判据）、
  TDM-E-L4-12（与治理道交叉：五查逐条冗余→净零候选）、TDM-E-L1-AGG（与 L1 道/风控道交叉：状态环是否≈常数）、
  TDM-E-L1-S2（与数据道交叉：daban_board_event/limit_up_pool 历史回填可行性=7 张母卡的解锁条件）、
  TDM-E-L0-03（与 P 流/归因道交叉：Brier 校准链复用面）、TDM-C-L4（与基础设施道交叉：币圈数据深度与费率实测）。
- **诚实申报的负结果与不立卡决定**：TDM-E-L1-S1 未立卡（唯一可判长窗面已被母卡 02 覆盖，代理会改命题）；
  7 张 L4 卡的"倒 U / 符号为负属预期"条款（跌停家数、连板高度、失败态 IC、q 先验 IC 等）
  均按 `calibration_exam.judge` 原样判 fail 入册，未改符号口径造过门（G4-5）。
