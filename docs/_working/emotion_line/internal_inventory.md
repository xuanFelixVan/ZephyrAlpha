---
ttl: task_bound
title: 情绪线内部盘点册——成分断点四态判定与 DB 实证
created: 2026-09-22
sid: st-emomine-20260922
lane: emotion_line
status: active
doc_version: v1.0
---

# 内部盘点册——情绪指数候选成分 × 仓内现状四态判定

> 性质=只挖不建。本册逐项回答"建 emotion_index 的每一味原料，仓内现在有没有、通不通、断在哪"。
> 四态定义：**通**=日频连续且近端新鲜（≤2 交易日）；**半通**=有数据但历史浅/近端滞后/采样稀疏；
> **断**=曾产出但近端停摆；**缺件**=目标表/任务不存在。
> 证据分级：**[亲验]**=本会话只读探针实测（CH reader 连接，2026-09-22）；**[代码]**=源码直读；
> **[注册表]**=注册表/调度真源直读。

## §0 探针方法（可复现）

- 探针脚本：`.runtime/tmp/st-emomine-20260922/probe_emotion_tables.py`（只读 SELECT，经
  `DatabaseService.get_clickhouse_conn('reader')`，全仓唯一 Client 构造点，零写入）。
- 结果快照：`.runtime/tmp/st-emomine-20260922/probe_result.json`（659 行全量 JSON）。
- 探针时点：2026-09-22 18:00-18:40（Asia/Shanghai）。下文所有行数/日期均为该时点实测。

## §1 四态总表

| # | 成分族 | 真源表（CH） | 行数 | 覆窗 | 近端 | 四态 |
|---|--------|--------------|------|------|------|------|
| 1 | 涨停/连板/炸板/晋级（daban 链） | c1_market.daban_board_event | 936 | 09-01→09-15 | 断 5 交易日 | **断** |
| 2 | 打板四引擎负载 | c1_market.daban_engine_load | 936 | 09-01→09-15 | 断 5 交易日 | **断** |
| 3 | 涨跌家数比/大盘涨幅 | c1_market.kline_daily + kline_index | 10,096,973 / 3,100,016 | 1990→09-22 | 当日 | **通** |
| 4 | 成交额分位/换手分位 | c1_market.kline_daily（amount/turnover/volume 列在） | 同上 | 同上 | 当日 | **通** |
| 5 | 两融温度 | c1_market.margin_trading | 188,494 | 07-20→09-18 | 滞后 1-2 交易日 | **半通** |
| 6 | 龙虎榜（游资温度） | c1_market.dragon_tiger / dragon_tiger_seat | 2,122 / 617,864 | 08-07→09-22 / 2022-01-04→09-21 | 当日 / T-1 | **通** |
| 7 | 大宗交易 | c1_market.block_trade / block_trade_detail | 1,433 / 1,565 | 08-07→09-22 / 08-03→09-22 | 当日 | **通**（史浅） |
| 8 | 币圈情绪面板（异轴） | c1_market.sentiment_panel | 25 | 09-01→09-21 | T-1 | **半通**（疑点证实，见 §3） |
| 9 | 新闻原文 | c3_fundamental.news_data | 8,231,242 | 2010-01-02→09-22 22:00 | 当日 | **通** |
| 10 | 新闻情绪窗 | c1_market.news_sentiment_window | 19,818 | 02-25→09-22（每日 1 市场行） | 当日 08:00 | **半通**（见 §4） |
| 11 | 期权族（PCR 原料） | c1_market.option_iv_surface / option_kline / option_greeks | 30,259 / 7,458 / 4,602 | 01-29→09-21 等 | T-1 | **半通** |
| 12 | 盘口宽度快照 | c1_market.market_breadth_snapshot | 139 | 08-24→09-22（3-8 行/日） | 当日 | **半通**（极浅） |
| 13 | cohort 投资者画像 | c1_backtest.cohort_daily_ledger | —（表未建） | — | — | **缺件** |
| 14 | 涨停价真源（daban 前置） | c1_market.stk_limit | 9,215,394 | →09-22 | 当日 | **通** |
| 15 | 散户资金流（cohort 原料） | c1_market.money_flow | 522,466 | →09-22 | 当日 | **通** |
| 16 | 个股关注度（cohort 原料） | c1_market.alt_stock_comment | 36,380 | →09-21 | T-1 | **通** |

**汇总：通 9 / 半通 4 / 断 2 / 缺件 1。** 情绪指数 v0 最小聚合版的原料基本齐——真正卡脖子的是
daban 链断供（成分 1/2）与 cohort 缺件；其余皆为"能聚合但要带缺陷标注"。

## §2 逐项判定与断点定性

### 2.1 daban 链（涨停家数/连板高度/炸板率/晋级率）——**断**

- 真源：`c1_market.daban_board_event`（936 行）+ `c1_market.daban_engine_load`（936 行），
  两表均 **2026-09-01→09-15**，09-16 起连续 5 个交易日（09-16/17/18/21/22）零新增 **[亲验]**。
  9 月逐日行数 57~120 行/日（=当日触板事件数，量级健康）**[亲验]**。
- 派生产权：触板/封住/一字/首触/开板次数/封单代理/连板（三级涨停价解析链 88445 样本 100% 验证）
  **[调度]** tasks.yaml task `daban_board_event_derive`（source=internal，deps=kline_daily+stk_limit）。
- 断因定性：schedule=`weekend_calibration`（分钟/tick 富化重，周窗重放幂等）**[调度]**；
  前置 `kline_daily`（→09-22）与 `stk_limit`（→09-22）都活着 **[亲验]**——即**上游通、派生停**，
  断点在周窗重放任务本身（09-19/20 周末窗未跑或跑了未落），不在数据源。
- 消费影响：涨停家数/连板高度/炸板率/晋级率四个情绪核心成分全部停 09-15；四引擎负载宽表同断
  （板块线同样受害——非本线独有）。
- 四引擎负载（`ex_core/daban_load_producer.py::run_daily_batch`）同天断，与事件表同根因 **[代码]**。

### 2.2 涨跌家数比 / 大盘涨幅——**通**

- `kline_daily` 10,096,973 行、`pct_change` 列在，→09-22（当日 5,554 只）**[亲验]**；
  `kline_index` 3,100,016 行、1990-12-19 起、每日 ~595 个指数代码，→09-22 **[亲验]**。
- 涨跌家数比=当日 kline_daily 按 pct_change>0 计数比；大盘涨幅=000300 日收益。零新依赖。

### 2.3 成交额分位 / 换手率分位——**通**

- `kline_daily` 列清单实测含 `volume/amount/turnover/amplitude/pct_change/adj_factor` **[亲验]**。
- 注意：`stock_indicator`（1167 万行）实测**无** turnover/amount 列（列=pe/pb/ps/pcf/dividend_yield/
  total_mv/circ_mv）**[亲验]**——分位原料必须走 kline_daily，勿引错表。

### 2.4 两融——**半通**

- `margin_trading` 188,494 行，**2026-07-20 起**，max=09-18 **[亲验]**。
- 两个缺陷：①覆盖仅 ~2 个月（分位窗口严重不足）；②近端滞后 1-2 交易日（交易所 T+1 发布节奏，
  akshare stock_margin_detail_sse/szse）**[调度]** task `margin_trading_incremental`。
- 处置口径（设计稿承接）：两融成分 as-of 对齐用"最近可得日"，且考试时窗内该成分 INSUFFICIENT
  风险预登记（见考试卡草案）。

### 2.5 龙虎榜 / 大宗——**通**

- `dragon_tiger` 2,122 行（08-07→09-22，当日盘后）、`dragon_tiger_seat` 617,864 行
  （**2022-01-04 起**，→09-21）**[亲验]**——席位级深历史是现成资产，游资温度与龙头封开板
  代理可直接起量。
- `block_trade` 1,433 行 + `block_trade_detail` 1,565 行（08-03→09-22）**[亲验]**——
  折价率均值（JOIN kline_daily close）是机构情绪代理（cohort inst_config 同款算法 **[代码]**）。

### 2.6 期权族（PCR 原料）——**半通，互依赖标注**

- `option_iv_surface` 30,259 行（01-29→09-21）、`option_kline` 7,458 行（07-30→09-22，
  50ETF/300ETF 新浪源）、`option_greeks` 4,602 行（08-03→09-21）**[亲验]**。
- **PCR 衍生指标未建**：小红书班第 3 件在建（写域不在本线）——本班**只标注互依赖，不施工、
  不重复建**（总包 §3 硬边界）。骨架设计稿为 PCR 预留 v0.2 挂载位（见设计稿 §5）。

### 2.7 盘口宽度快照——**半通**

- `market_breadth_snapshot` 仅 139 行（08-24 起，每日 3-8 行分钟快照）**[亲验]**。
- 定性：任务 `market_breadth_snapshot_minute` 活着但保留稀疏、史极浅——**情绪指数不建议依赖
  此表**；宽度成分改由 kline_daily 派生（涨停跌停家数比/上涨占比），该表只作盘中辅助。

## §3 sentiment_panel 疑点专章（总包点名实证项）

**疑点"无持久化历史"——证实。** [亲验] 实测全表仅 **25 行**，构成如下：

| metric | 行数 | 覆窗 | 定性 |
|--------|------|------|------|
| fear_greed_index | 21 | 09-01→09-21 | alternative.me 币圈恐贪指数，日频 1 行，**仅 21 天** |
| cb_conversion_premium_median | 4 | 09-16→09-21 | 转债转股溢价率中位数（akshare F25 风险偏好温度计，任务 cb_premium_median_daily） |
| btc_dominance / etf_flow / usdt_premium | 0 | — | provider 骨架能力，源未接入，零行 |

- **t0 复活班 E4 考试 unevaluable 判定的物证**：21 天恐贪 + 4 天转债溢价，任何滚动分位/考试
  窗都不够格。t0 考试时点该表甚至只有 2 行（09-12/09-13，注册表 evidence 留痕 **[注册表]**）。
- **词表漂移注记**：DDL 注释声明 metric 词表=fear_greed_index/btc_dominance/etf_flow/usdt_premium
  **[代码]** schemas/categories/market/market_sentiment_panel.py，但实库已出现第五个 metric
  （cb_conversion_premium_median，A 股转债系）——词表注释与实库已漂移，归属=数据治理另案，
  本班只登记不修。
- **红线重申**（总包 §2）：fear_greed 是币圈异轴，**禁**顶替 A 股情绪成分（t0 考试判例）。
  它在本线唯一合法位置=v0.2+ 的"跨市场辅助确认"可选成分，且必须带异轴标注。

## §4 新闻线专章

- **原文层通**：`news_data` 8,231,242 行（2010→2026-09-22 22:00），近 7 日每日 700~2,400 条
  **[亲验]**；四源（财新快讯/cls/东财/rss）同表写入+标题 MD5 去重 **[调度]**。
- **打分层半通**：`news_sentiment_window` 19,818 行 = market 183 行（02-25 起**每日 1 行**，
  →09-22 08:00）+ symbol 19,635 行 **[亲验]**。三个断点：
  ①打分全走 `data_source='rule'` 规则法，LLM/llm_fallback 分支无实证落库 **[亲验]**；
  ②无独立调度任务（注册表 produced_by_job=null，挂靠夜间批/盘前流程调用 **[注册表]**），
  写入器=`src/zephyr/intelligence/nightly_sentiment_window.py`（夜间窗=前日 18:00→当日 08:00）；
  ③无盘中窗、symbol 级覆盖非全市场（19,635 行 vs 全市场 5,565 只/日）。
- 消费口径：市场级 sentiment_index（[-1,1]）+正/负/中性计数+top_events_json 可直接作情绪成分
  C6；只取 scope='market' 日窗行，symbol 级留二期。

## §5 cohort 投资者画像——**缺件（代码就绪、落地闸未合）**

- 代码面**就绪** **[代码]**：`src/zephyr/alt_data/cohort_daily_ledger.py`（五人群日频聚合器：
  retail 散户/leverage 杠杆/hot_money 游资/inst_config 机构/industry 留位；纯计算禁写库）
  + `cohort_daily_writer.py`（写通道，strict+ReplacingMergeTree 同键幂等）。
  模块头声明"CH insert 已接线（Owner 批 2026-09-21），调度任务 cohort_ledger_daily deps=
  [money_flow, margin_trading, dragon_tiger, block_trade]"。
- 落地面**未合** **[亲验]**：①`c1_backtest.cohort_daily_ledger` **表不存在**（system.tables
  全库扫描零命中，DDL 真源 schemas/categories/cohort_daily_ledger.py 已在）；②tasks.yaml
  **无** cohort_ledger_daily 任务条目。
- **矛盾定性**：代码注释"已接线"与调度真源/实库现状不符——接线声明至少部分未落地
  （表建了吗？任务登记了吗？），归属施工班核对，本班如实登记为缺件。
- 原料侧全通 **[亲验]**：money_flow 522,466 行→09-22、alt_stock_comment 36,380 行→09-21、
  margin_trading/dragon_tiger/block_trade 均在库（§2）。

## §6 与接口契约 v0.1 的对接点（Max 定稿只读引用）

- 契约要求 components 数组必带成分明细（name/raw_value/percentile/weight）——本册四态表即
  components 候选全集：v0 可入 6 成分（C1 涨停温度/C2 晋级率/C3 广度/C4 量能/C5 杠杆/C6 新闻），
  PCR 与 cohort 画像留 v0.2 挂载位。
- 契约要求 stage 四态（pre_open/auction/intraday_vN/close_final）——原料近端新鲜度实测
  （两融 T+1、龙虎榜 seat T-1、新闻窗 08:00）直接决定各 stage 能聚合哪些成分，映射见设计稿 §4。

## §7 证据分级自查

- 全部行数/日期/列清单=本会话亲验探针（可复现脚本+JSON 快照在案）；
- 代码定性=模块头/DDL 真源直读；调度定性=tasks.yaml HEAD 版直读；
- 未做任何写操作（探针只读；写域=本战役文件夹）。
