---
ttl: task_bound
session: st-xhs-full-20260922
topic: xhs_full_construction_20260922
---

# 幻方十大因子——10 张横截面假设卡入册（工单 #1）

> Owner 工单 #1：按规格卡产 10 张假设卡（逐因子表达式/假设/数据源）入 E1C 挖矿队列逐条过 E4。规格真源=collection_intake/factors/factor_spec_huanfang_ten.md。判定口径：横截面选股因子（非择时指标），不走 tilib 扩批。E4 出证表述遵裁定#325（放行档如实，低放行是常态）。
> DSL=算子白名单 config/factor_mining_whitelist.yaml（v2.1 含 trade_when）；基座字段真源=lane_c_formula_miner.FEATURES（ret_1d/ret_5d/ret_20d/vol_20d/turnover/amt_z20/close_ma20，REG-IND-001）。

## 卡片登记表

### HF-01 短期反转（幻方：A股最重要）｜判定 A 原料
- **表达式**：`neg(rank_cs(ret_5d))`
- **假设**：5 日涨幅截面排名越靠后（跌多）的股票，次 5 日超额收益为正（短期反转效应）；横截面排序做多端=超跌组。
- **数据源**：REG-IND-001 基座（kline_daily 派生 ret_5d），零新增依赖。
- **队列**：已入 lane_c_candidates.csv（CAND-feefa1374102，incr_ic=-0.0219 实算，birth_batch=E1C-20260922-HF）。
- **E4 方案**：横截面 rank IC 分段（2020-2023 IS / 2024-2026 OOS）+ 成本 0/10/30bps 三档换手惩罚；预注册放行判据=OOS IC 均值>0 且两段同号。

### HF-02 中期动量｜判定 A
- **表达式**：`rank_cs(ret_20d)`
- **假设**：20 日动量截面延续（A 股中期动量弱于反转，预期低放行，如实考）。
- **数据源**：基座 ret_20d。
- **队列**：已入 lane_c_candidates.csv（CAND-70df2a6467e7，incr_ic=+0.0048 实算）。
- **E4 方案**：同 HF-01；预注册注意 A 股动量崩溃（momentum crash）尾部——加 max 回撤分段判据。

### HF-03 低波动异象｜判定 A
- **表达式**：`neg(rank_cs(vol_20d))`
- **假设**：20 日波动率越低的股票次期收益越高（低波异象 betting-against-beta 的 A 股形态）。
- **数据源**：基座 vol_20d。
- **队列**：已入 lane_c_candidates.csv（CAND-49fa67062cc5，incr_ic=-0.0222 实算，本窗反低波形态如实）。
- **E4 方案**：同上+分域（大/小盘）稳定性；预注册预期=小盘域更强。

### HF-04 低换手异象｜判定 B（Amihud 指标化立卡见 HF-04b）
- **表达式**：`neg(rank_cs(turnover))`
- **假设**：换手率越低（关注度低/筹码稳）的股票次期收益越高（流动性溢价反向面）。
- **数据源**：基座 turnover（log1p 变换后）。
- **队列**：已入 lane_c_candidates.csv（CAND-1d2a94be819a，incr_ic=-0.0347 实算，本窗反低换手形态如实）。
- **E4 方案**：同上；与 HF-03 相关性检查（低波×低换手天然高相关，入库去重走 clone_guard/因子相关性闸）。

### HF-05 价值（EP 低估）｜判定 B
- **表达式（模板，前置后入队）**：`rank_cs(div(1, pe_ttm))`（=EP 盈利收益率）
- **假设**：盈利收益率截面排序做多端=低估组，次期超额为正。
- **数据源**：c1_market.stock_indicator（PE/PB，2026-08 起）+ **前置=估值历史回补（2026-08 之前缺口，幻方规格卡已披露）**。
- **队列**：前置未齐，暂以模板入册本文件；回补批落地后转 lane_c 队列实体行。
- **E4 方案**：同上；预注册加分域（价值因子拥挤在小盘失效风险）。

### HF-06 成长（营收/净利同比）｜判定 A 原料
- **表达式（模板）**：`rank_cs(add(rev_q_yoy, np_q_yoy))`
- **假设**：营收与净利同比增速截面排序做多端=高成长组，次期超额为正。
- **数据源**：c3_fundamental.financial_derived（rev_q_yoy/np_q_yoy，PIT 键=(symbol,report_period,announce_date)）。
- **队列**：前置=financial_derived 横截面拼接进基座面板（join 键 PIT 对齐）；模板入册。
- **E4 方案**：同上+公告日漂移检查（PIT 纪律）。

### HF-07 情绪合成｜判定 B
- **表达式**：非公式面——合成面板=_sentiment_panel（恐贪）+ news_sentiment_window + option_sentiment 三口径 PCR（工单#3+#14 已接官方表）。
- **假设**：情绪合成分与次期大盘/情绪敏感股收益负相关（反向）。
- **数据源**：三子源在库（幻方规格卡 §7）。
- **队列**：走情绪注解维度⑨消费面（MOD-SIG-025 权重≤0.10 纪律），不进横截面公式队列；合成器立项另批。
- **E4 方案**：情绪→次 5 日 510300/000852 分位数分组；PCR 官方表 E4 出证独立成卷（见 PCR 假设卡）。

### HF-08 资金流横截面｜判定 A 原料
- **表达式（模板）**：`rank_cs(mf_net_z20)`
- **假设**：20 日净流入标准化排序做多端=资金持续流入组。
- **数据源**：c1_market.money_flow（在产）。
- **队列**：前置=_money_flow 横截面字段进基座（z-score 窗 20）；模板入册。
- **E4 方案**：同上+换手惩罚加重（资金流因子换手陷阱高危，预注册声明）。

### HF-09 板块热点传导｜判定 A（口径同花顺 881）
- **表达式**：非公式面——板块动量→成分股传导（kline_sector_880 2024-10 起）。
- **假设**：板块 5 日涨幅 top 分位的成分股次期超额为正（热点扩散）。
- **数据源**：kline_sector_880+sector_constituent。
- **队列**：板块层骨架在板块线班域（st-chainpile/板块线在飞），本卡挂接不重复施工（写域避让留痕）；传导链归 TDM L2。
- **E4 方案**：板块线班统一考试；本卡仅登记假设与数据源。

### HF-10 盘口买卖压（五档代理）｜判定 B
- **表达式（模板）**：`rank_cs(div(bid_vol_sum, ask_vol_sum))`（bid1-5 量合计/ask1-5 量合计）
- **假设**：买卖压比高（买盘堆积）的股票日内/次日收益为正。
- **数据源**：c1_market.tick_depth_5（五档实时在写）；**深史任何渠道不存在（规格卡披露，known_data_gaps）**——幻方"十档"口径按五档代理定义。
- **队列**：前置=五档日频聚合表立项（压比日面板）；模板入册。
- **E4 方案**：前向积累满 60 交易日后开考（预注册窗口声明，不追考无数据期）。

## E1C 队列入册记录（lane_c_candidates.csv 追加行）

- 4 张基座可表达卡（HF-01/02/03/04）已追加实体行：candidate_id=make_candidate_id(表达式)（CAND- 前缀 md5[:12]），birth_channel=C，birth_batch=E1C-20260922-HF，birth_source=huanfang_ten spec cards（工单#1），hypothesis_zh=各卡假设句；incr_ic 列=真算值（E1C 纯核 rank_ic 增量口径，REG-IND-001 残差化，样本面板=窗内成交额 top50×250 交易日，2026-09-22 实跑）。
- 6 张前置卡（HF-05/06/07/08/09/10）以模板入册本文件，前置（字段扩座/回补批/聚合表/写域避让）逐卡声明；前置齐后转实体行。
- E2 预审/E4 考试沿 FactoryLaneC 周窗自动化消费；本批不入工预审（机制六问在卡内自答，防 LLM 预审排队堵本周窗）。

## 净零声明

本件=工单#1 唯一交付物（10 卡台账）；lane_c_candidates.csv 追加 4 行=队列入册面；无新注册表、无新模块（复用 lane_c 纯核+白名单 v2.1）；与 collection_intake 规格卡跨域不同对象（规格=判定依据，本件=施工卡与队列凭证）不并。
