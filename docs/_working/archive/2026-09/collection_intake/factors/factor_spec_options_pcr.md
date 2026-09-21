---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# 期权 PCR 因子族——规格与 P1 数据批立项建议 2026-09-20

> 来源：小红书帖（作者"策略运行日记"，96 评论；配图=PCR 知识卡）。帖主声称据此做夏普 3.95 商品期货策略并自证分段稳定——**按"未复现宣称"对待，只取因子定义不取业绩**。

## 因子规格

- **定义**：PCR（Put-Call Ratio）= 认沽/认购比率。三口径：
  1. 成交量 PCR = 认沽成交量 / 认购成交量；
  2. 成交额 PCR = 认沽成交额 / 认购成交额；
  3. 持仓量 PCR = 认沽未平仓量 / 认购未平仓量。
- **信号口径**（原帖）：PCR>1=恐慌情绪重、做空情绪浓；PCR<1=做多情绪高涨；作用=捕捉日内情绪拐点，适合日内/短波段。
- **用法**：期权信号 → 期货/指数标的交易（信号源与交易标的分离）；指数级择时，不适用个股。

## 内部挖矿 `[亲验]`

- 已有：`src/zephyr/signal_ashare/sentiment/option_sentiment.py`（MOD-SIG-059）**现算成交量 PCR**，主标的 510300，50ETF/500ETF 可 config 扩展。
- 数据面：`c1_market.option_greeks`（3055 行，2026-08 起）/ `option_iv_surface`（3 万行，delta 列全 0）/ `option_kline`（4890 行，2026-07-30 起）——**全部 <2 个月浅历史**；任务在 `src/zephyr/data/config/tasks.yaml`（akshare 新浪源 option_sse_daily_sina）。
- **关键缺口：无任何表含 open_interest → 持仓量 PCR 不可算**；股指期权（IO/MO/HO）未接。

## 外部挖矿 `[外部]`（本次调查最有价值发现）

- **交易所官方每日发布 PCR，免费**：
  - 上交所：官网"股票期权-每日统计"，底层接口 `query.sse.com.cn/commonQuery.do`（sqlId=COMMON_SSE_ZQPZ_YSP_QQ_SJTJ_MRTJ_CX），返回**认沽/认购成交量比（CP_RATE）**+认购/认沽成交量+总成交额；未平仓合约数可自算持仓 PCR。统计页：http://www.sse.com.cn/assortment/options/date/
  - 深交所：`investor.szse.cn/api/report/ShowReport/data`（CATALOGID=ysprdzb&TABKEY=tab1），含**认沽/认购持仓比（rcrpccb）**。
- **最短可行路径**：akshare `option_daily_stats_sse(date)` / `option_daily_stats_szse(date)` 直接返回官方 PCR 字段（免费无 token）；生产化时照抄 akshare 源码端点自建采集器（akshare/option/option_daily_stats_sse_szse.py）。
- tushare：`opt_daily`（doc_id=159）需 2000 积分且 PCR 须按合约自行聚合；`opt_daily_basic` 疑已下线勿依赖。
- 另：上交所 `option_risk_indicator_sse(date)` 提供官方希腊字母+隐波（2015-02-09 起），可顺带升级 option_greeks 的历史深度与质量。

## 判定与立项建议

**C（缺失需立项，P1）**——本项目唯一值得新开的数据批：
1. 新表 `c1_market.option_daily_stats`（建议列：trade_date/exchange/call_vol/put_vol/volume_pcr/call_amt/put_amt/amount_pcr/call_oi/put_oi/oi_pcr；DateTime64(3)+时区按 RULE-SCHEMA-TZ）。
2. 新任务挂 akshare 两接口，日频增量；历史回补深度以接口实际返回为准（上交所期权 2015-02 起，实测确认）。
3. option_sentiment（MOD-SIG-059）升级：从现算成交量 PCR 改读表，扩三口径。
4. 因子假设卡：PCR 三口径对 510300/指数的择时信号 → E4 分段稳定性和容量考试（预注册，原帖夏普 3.95 不作为先验）。
5. 顺带项：`option_risk_indicator_sse` 回补升级 option_greeks 历史。
