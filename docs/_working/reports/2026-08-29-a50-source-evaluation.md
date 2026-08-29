---
ttl: task_bound
---

# A50（富时中国A50期货，新交所SGX）数据源评估与落地结论

> **用途**：A22 施工项（44号备忘 §9.6 通道1 / M3-①d 盘前 gap_adj w3=A50夜盘）的数据源评估落盘。
> 评估方式=2026-08-29（周六，冻结行情态）本机实证探测（HTTP 状态/字段/历史深度逐项实测），非文献转述。
> 范围纪律：日韩通道已裁定砍（44号 §11 裁定三 + 路线图 A22 注记），本评估不含日韩源。

## 一、候选源实证结论表

| 源 | 接口/通道 | 口径 | 历史深度 | 实证结果（2026-08-29） | 结论 |
|---|---|---|---|---|---|
| 新浪 hf 裸调 | `hq.sinajs.cn?list=hf_CHA50CFD`（须带 Referer，GBK） | 实时快照：最新价/买/卖/今开/最高/最低/昨结/持仓量/行情日期时间 | 无历史（仅最新快照） | ✅ HTTP 200，字段全（last=14662.52，prev_settle=14706，oi=781522） | **主源（盘中/盘前实时腿）**——已在位（us_futures_intraday_snapshot 默认品种表含 CHA50CFD） |
| akshare 封装 | `futures_foreign_commodity_realtime("CHA50CFD")` | 同新浪 hf | 无 | ❌ KeyError——akshare 品种表硬编码 30 个商品代码，不含 CHA50CFD（与 92号 §7.2 评估一致复证） | 不可用（封装层缺口，故主源走裸调） |
| 新浪历史 | `akshare.futures_foreign_hist(symbol="CHA50CFD")` | 日K：date/open/high/low/close/volume/position（持仓）；无成交额 | **约 10 年（2016-08-29 起，2594 行）** | ✅ 实证 2594 行，最新行 2026-08-28 | **选定（日频历史腿）**——本批落地为 a50_futures_daily 通道 |
| 东财 | `futures_global_spot_em`（CN00Y 行） | 快照：最新价/涨跌/今开/最高/最低/昨结/成交量/买盘量/卖盘量/持仓量；**无行情时间戳** | 无 | ✅ CN00Y="A50期指当月连续" 行在位 | 保留为盘中兜底（degraded=1，已在位） |
| 东财历史 | `futures_global_hist_em(symbol="CN00Y")` | 日K（push2his kline） | 理论多年 | ❌ 本环境 ProxyError（push2his 需特定网络路径），且无免费稳定性承诺 | 不采用 |
| 新浪分钟历史 | `GlobalFuturesService.getGlobalFuturesMiniKLine5m` | 分钟K | — | ❌ "Service not found"（接口已下线） | 不采用（A50 无免费分钟历史源；盘前场景日频+实时快照足够） |
| tushare | pro.fut_daily 等 | 期货日K | 国内所 | ❌ 口径不符：tushare 期货仅国内六大所（CFFEX/SHFE/DCE/CZCE/GFEX/INE），无 SGX 外盘品种 | 排除 |
| SGX 官方 | sgx.com 数据服务 | 官方全量 | 全量 | ❌ 付费/需注册，超免费通道约束 | 排除 |

## 二、落地配置（本批已施工）

| 通道 | 任务（tasks.yaml） | 表 | 源 | 状态 |
|---|---|---|---|---|
| 盘中/盘前实时快照 | `us_futures_intraday_snapshot`（intraday_realtime 每5分钟） | `c1_market.us_futures_intraday` | 新浪 hf 裸调主源 + 东财快照兜底 | **既有在位**（92号 §7.2，2026-08-22 已落），A50=CHA50CFD 在默认品种表 |
| 日频历史 | `a50_futures_daily_incremental`（pre_market 08:30，夜盘 ~05:15 已收） | `c1_market.a50_futures_daily`（新表，本批 DDL+建表+回填） | akshare futures_foreign_hist（新浪源） | **本批新落**（2026-08-29） |

- 新表 DDL 真源：`schemas/categories/market_a50_futures_daily.py`（ReplacingMergeTree，ORDER BY (symbol, trade_date)，无 amount 列——源无成交额字段）；
- 初始回填：一次性全窗口执行，**2594 行（2016-08-29 ~ 2026-08-28）已落库**（quality_gate 标记 183 行 OHLC 形态告警=源早期年份 volume/position=0 的平值行，写入未阻断，留痕待消费端按需过滤）；
- fallback_sources 显式置空：评估结论无免费稳定等价源（东财历史接口不可用、tushare 无品种、SGX 官方付费）。

## 三、遗留风险

1. **A50 日K的交易日历口径**：futures_foreign_hist 的 date 列为 SGX 交易日（含夜盘归属约定未明文），与 A 股 trade_date 对齐时边界日（如周一行含上周五夜盘）可能有 ±1 日归属差——盘前 gap_adj 消费时以"最近一根已完成日K"取用即可吸收。
2. **新浪 hf/历史接口无 SLA**：免费通道政策变化不可控；hf 通道已有东财快照兜底，历史腿断供影响仅为校准数据停更（不阻塞盘前链路）。
3. **早期数据质量**：2016-2018 段 volume/position 多为 0（源侧缺失），价格字段完整；质量标记告警已留痕。
