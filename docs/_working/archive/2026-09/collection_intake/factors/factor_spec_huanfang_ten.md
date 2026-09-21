---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# 幻方《量化投资十八问》十大因子——规格卡与内外判定 2026-09-20

> 来源：小红书帖（作者"毅見Alpha"，Gemini 图解版），原文定性=公众号科普+公关口径，**无官方稳定直链** `[外部]`——可作因子清单速查表，不可作方法论真源。
> 用法：以下每因子给"幻方定义 → 项目内部数据/指标现状 → 判定"。判定口径见 README。

## 总判定

**B（部分有需补齐）**：十因子中 6 个的数据与指标原料已在库（A 级原料），2 个历史偏浅需回补，1 个缺指标化（流动性），1 个依赖盘口深史。全部按"横截面因子假设卡"走 E1C 立项 + E4 重考，不走 tilib 时序指标扩批（幻方口径是选股因子非择时指标）。

## 逐因子规格卡

### 1. 反转因子（幻方：A 股最重要）
- 定义：涨多了要跌、跌多了要涨（短期反转）。
- 内部 `[亲验]`：指标库 reversal 类已设taxonomy；ROC/MTM/CMO/BIAS/RSI/WR/KDJ 等超买超卖反转族在产（technical_indicator_registry.yaml，138 条）。
- 判定：**A**（时序指标齐）；横截面反转组合口径（多空排序）未做 → E1C 假设卡。

### 2. 价值因子（PE/市净率/现金流）
- 内部 `[亲验]`：`c1_market.stock_indicator` 有 PE/PB/PS/PCF/股息率（akshare 源，**2026-08 起，历史浅**）；`stock_daily_basic` 只有换手率/股本/市值（无 PE/PB）；现金流原料在 `c3_fundamental.cashflow_statement`。
- 判定：**B**——缺口=估值历史回补（2026-08 之前）。

### 3. 成长因子（三年净利润/营收 CAGR）
- 内部 `[亲验]`：`c3_fundamental.income_statement`（34 万行）+ `financial_derived`（rev_q_yoy/np_q_yoy/各 TTM，PIT 键=(symbol, report_period, announce_date)）齐备。
- 判定：**A**（原料齐，CAGR 自算）；注意三表源=miniqmt（9/18 退役）→ **切 akshare 是在途风险**（裁定 #339 主线）。

### 4. 动量因子（T 期加权涨幅）
- 内部 `[亲验]`：ROC/MTM/TSI/SMI/RMI/Inertia/PFE/COPPOCK 等 in stock。
- 判定：**A**。

### 5. 波动率因子（低波异象）
- 内部 `[亲验]`：ATR/NATR/HistVol/Parkinson/Garman-Klass/Rogers-Satchell/Yang-Zhang/STDDEV/ROLLVAR/Ulcer 全在库。
- 判定：**A**；低波横截面组合口径 → E1C 假设卡。

### 6. 流动性因子（低换手异象）
- 内部 `[亲验]`：换手率=原始字段（`stock_daily_basic.turnover_rate`，批 9 落地，000852 自 2021 起 100% 覆盖），**指标库无 turnover/Amihud 条目**；量比全库未见。
- 判定：**B**——立 Amihud 非流动性+换手率横截面因子条目（数据已就绪，纯指标化工作）。

### 7. 情绪因子
- 内部 `[亲验]`：`event.news_sentiment_window`（夜间窗，status=testing）、`c1_market.sentiment_panel`（恐贪 ingest active）、option_sentiment（MOD-SIG-059，成交量 PCR 现算）。
- 判定：**B**——三个子源都在，缺"合成情绪面板"；PCR 三口径升级见 factor_spec_options_pcr.md。

### 8. 资金流因子
- 内部 `[亲验]`：`c1_market.money_flow`（个股）+ `market_fund_flow_daily`（大盘）+ `sector_fund_flow`（板块 881 体系）三表在产；北向=裁定退役停采留表。
- 判定：**A**。

### 9. 板块因子
- 内部 `[亲验]`：industry_class（申万）+ kline_sector/kline_sector_880（同花顺 881，2024-10 起）+ concept_board 族 + sector_constituent 全在；申万日线正式表仍 candidate。
- 判定：**A**（同花顺口径可用）；热点传导类因子 → E1C。

### 10. 盘口因子（十档买卖压）
- 内部 `[亲验]`：`c1_market.tick_depth_5` **五档**（bid/ask price+volume 1-5，20 列），tick_subscriber 桥自 9/18 实时写入；**历史五档任何渠道不存在**（近期可走大 QMT download_history_data，服务器留 ~1 月）；幻方说"十档"，我们只有五档——买卖压代理口径按五档定义。
- 判定：**B**——前向数据已接，因子定义按五档落地；深史缺口记录在案（known_data_gaps）。

## 附：原帖方法论侧记

- 帖主用 Gemini（Nano Banana Pro）"原文+手绘 prompt"直出图解；坑=A股红涨绿跌需 prompt 指定（见 tools/tool_gemini_chart_recipe.md）。
- 评论区补一条：**Barra**（风险模型体系）——内部无 Barra 类风险模型，判定 D P2（组合归因参照系）。
