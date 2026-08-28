---
ttl: permanent
doc_type: architecture_view
title: 事件驱动策略细节
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.9.8"
date: 2026-08-15
topic: event_driven_strategy_detail
scope: 07_trading_decision_architecture
---
> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：四类事件源数据链路全部 production 实证——新闻三源（eastmoney_news_provider / cls_provider / rss_provider）+ news_collector（MOD-DATA-NEWS-001）+ news_dedup 跨源去重 + dragon_tiger/dragon_tiger_seat 双表（akshare_provider stock_lhb 系）+ corporate_action_processor（MOD-TRADING-004）+ market_event_integrator（EMERGENCY 模式落码）+ intraday_buy_sell_point_analyzer（BM-SEL-05-C）+ market_sentiment_analyzer（BM-SEL-03-A）+ nlp_inference（Qwen2.5-7B）+ ipo_calendar provider（§2.5a 数据源）。
>
> **最终成果**：事件驱动策略细节定稿（active v1.9.7）——六类事件分类 + 经验衰减曲线 + PEAD Inversion 极端反应修正 + event_score 公式族（单/双/三因子）+ 进出场触发算法 + IPO 虹吸 + 地缘传导映射 + 龙虎榜 2026 失效校准。
>
> **未做事项及原因**：① sentiment_aggregator.py 未落盘（src/zephyr/nlp/ 实证仅 nlp_inference.py，§2.7 已裁定单条推理降级不阻塞 MVP）；② sleeve 内部组件全部未落码（grep 实证零命中）——event_score_single_factor / compute_event_score / event_score_dual_factor / event_score_triple_factor / should_enter_with_confirmation / should_exit / 5 辅助函数（has_contradictory_event/has_volume_confirmation 等）/ event_store/volume_series/volume_ma/trading_days_ago 四薄封装 / detect_anomaly 异动识别器 / compute_ipo_siphon_coefficient / map_geopolitical_event_to_sectors / dragon_tiger_corroboration_modifier / expectation_gap_with_revision_momentum / check_selling_pressure_absorbed；③ 六因子矩阵待施工项（dReport/Jump on PEAD/隔夜趋势/AStockEvent Feed）未落码；④ BM-SEL-19 事件驱动分布筛选漏斗（MOD-SIG-049）未施工——依赖知识图谱 BM-SEL-11（design 态）+ NLP 管道 Phase 7；⑤ Hawkes/Janus-Q 细分类/CNN 可视化/LLM 动态图谱/Data Funnel 双阶段为 §5 暂缓项与远期登记；CAND-AISA-001 待 G28 四问评估。

> ## 结案报告回填（2026-08-28 代码实证复核）
> 原"sentiment_aggregator 未落盘/sleeve 组件未落码"已过时：intelligence/event_score.py 全族（single/dual/triple_factor+compute_event_score+should_enter_with_confirmation+expectation_gap+selling_pressure_absorbed）+event_dragon_tiger.py+event_ipo_siphon.py+event_geopolitical_map.py+event_anomaly_detector.py 全在位；nlp/sentiment_aggregator.py 已落盘；pf_core/strategies/event_driven_sleeve_strategy.py 组装类在位。
> **仍真实未完工**：六因子矩阵待施工项（dReport/Jump on PEAD 等外部 Feed）未落；BM-SEL-19/MOD-SIG-049 漏斗零命中；Hawkes/Janus-Q 远期。
>
> ## 施工回填（2026-08-28 AI-WAVE3A-001）
> "BM-SEL-19 漏斗零命中"已施工闭环：`intelligence/event_funnel.py`（MOD-INT_EVENT_FUNNEL，§2.5 事件→选股映射落码）——候选池生成（精筛∪事件触发，`build_candidate_pool`）→ 过滤（复用 `compute_event_score` 全族评分：利空剔除/极端反应>3%/条件PDF下降>15%/传导链>0.7；|score|<0.2 噪声不动作）→ 评分降序 → ~50→~30 容量截断（`run_event_funnel`）；无事件数据源 `skipped` 直通不阻塞。评分真源唯一在 event_score（不重复造公式）；与 21 号侧 `signal_ashare/event_driven_screener.py`（MOD-SIG-049，EventImpactRecord 契约）平行承载 BM-SEL-19 两视角。测试 `tests/intelligence/test_event_funnel.py` 33 用例全绿；depgraph 设计态 node_id=10919338（planned，只登记不流转）。遗留：sleeve 策略接线（当前 event_driven_sleeve_strategy 自承载逐标的评分过滤，漏斗层经 TYPE_CHECKING 声明待接线）。

# 事件驱动策略细节
> 本备忘定义首批 3 策略之一——事件驱动 sleeve（[20_first_batch_strategies §2.4](20_first_batch_strategies.md) 策略C）的 alpha 信号来源、事件源、事件分类、冲击衰减曲线、事件→选股映射、换手率与多源情绪接入。性质：永久态讨论记录。管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)；路线图定位见 [00_index_trading_decision](00_index_trading_decision.md) G10（L1·Alpha 选股层，P2）。
## 1. 背景
### 1.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，T+1 结算，不能做空，涨跌停限制）；事件驱动为首批 3 sleeve 之一（[20 §2.4](20_first_batch_strategies.md) 策略C），定位"中换手、中容量、离散事件冲击"；多策略并发架构 Model A 定稿（[30](30_multi_strategy_concurrency.md)），regime 只做 Shrinkage 风险节流不参与选股（[10](10_regime_detector_spec.md)）
- 事件类基础设施已大量存在（§1.4）：多源新闻采集、`news_collector`、NLP 情感管道（[#ARCH-NLP-PIPELINE-001](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 在建）、`corporate_action_processor`。关键不是"造轮子"，而是"把已有基础设施接成事件→选股→持仓的 alpha 链"
- **A 股 2026-08 市场背景**：08-07 深调后十大券商共识"超跌反弹仍有演绎空间，8 月中下旬中报密集期是检验窗口"（[澎湃 2026-08-10](https://m.thepaper.cn/newsDetail_forward_33750320)）。含义：①中报密集期=业绩类事件高发窗口；②超跌反弹阶段事件利好催化易触发反弹延续；③科技拥挤度未回落，事件利空仍需警惕——支撑 §2.4 极端反应反转修正与 §2.5 EMERGENCY 协同
### 1.2 核心问题
alpha 来自离散事件冲击，需对齐 G10 六要点：①事件源 ②事件分类 ③冲击衰减曲线 ④信号→选股映射 ⑤换手率 ⑥多源情绪接入。核心张力：A 股信息扩散慢、情绪驱动强、T+1 不能日内翻转；事件驱动与打板同受情绪周期隐形驱动（[30 §1.3](30_multi_strategy_concurrency.md)），相关性可能高于直觉——[G07](23_strategy_correlation_validation.md) 施工前必测。
### 1.3 约束条件
- 不能做空 → 利空事件信号只能"剔除/回避"，alpha 集中在事件利好方向的多头
- **T+1 事件→交易时序显式映射**（v1.9.0 收拢单点声明）：①盘后事件（T 日 15:00 后披露）→ T+1 日开盘才能行动（ORJ 即此窗口第一反应）→ 买入仓最早 T+2 可卖；②盘中事件 → 当日可买但**不可卖**——`should_exit` 的 `holding_days >= 1`（EXTREME_REACTION 线）已隐含此约束；③`holding_days` 计数：买入当日=0（不可卖），次日=1（可卖起点）；④盘后事件 rising 可捕捉窗口实为 day 1-5（day 0 收盘才知情），半衰期折损一日已含于 §2.4 各事件类 rising 半衰期，不另调
- 事件冲击衰减快（rising day 0-5，decay day 6-15，[Beyond the Event Horizon 2025](https://www.preprints.org/manuscript/202506.0079)）→ 持仓以 rising phase 为主，T+1 下需提前布局退出
- 情绪周期隐形驱动 → 与打板相关性风险（[30 §1.3](30_multi_strategy_concurrency.md)）；事件链路长（数据源→分类→情绪→衰减→选股），任一环节失效须可降级不阻塞
### 1.4 已施工设施盘点（通用规则 #11，2026-08-12 代码侧真源审计）
> ✅=已落盘可消费，🟧=在建未落盘，⚠️=同名消歧。本盘点为 §2"复用而非新建"裁定的事实基座（真源路径经代码/schema/tasks.yaml 审计，provider 登记见 [11_d_data](../../02_domain_architecture_docs/11_d_data.md)）。

- ✅ 新闻三源 `eastmoney_news_provider.py`/`cls_provider.py`/`rss_provider.py`（BBC/CNBC/NYT/Guardian/Bloomberg，production）→ §2.2 新闻事件源/§2.5b 地缘事件源
- ✅ `news_collector.py`（MOD-DATA-NEWS-001）→ ClickHouse `fund_news_data` + `news_dedup.py` 跨源去重（production）→ §2.7 情绪数据基座/标准化层
- ✅ 龙虎榜双表 `c1_market.dragon_tiger` + `c1_market.dragon_tiger_seat`（AKShare `stock_lhb_detail_em`/`stock_lhb_stock_detail_em`，tasks.yaml 盘后调度，production）→ §2.2 龙虎榜事件源/§2.5 席位类型校准（**席位类型字段在 `dragon_tiger_seat` 表**）
- ✅ `corporate_action_processor.py`（MOD-TRADING-004）→ §2.2 除权日防误异动（非 alpha 源）；✅ `market_event_integrator.py`（`MarketMode.EMERGENCY` 已落码）→ §2.5 熔断期停止开仓
- ✅ `intraday_buy_sell_point_analyzer.py`（BM-SEL-05-C）→ §2.5 异动识别复用基础；✅ `market_sentiment_analyzer.py`（BM-SEL-03-A）→ §2.7 情绪分数基础
- ✅ `nlp_inference.py`（Qwen2.5-7B，#ARCH-NLP-PIPELINE-001 Phase 0/1 已落盘）→ §2.7 情绪分数源；🟧 `sentiment_aggregator.py` **未落盘**（`src/zephyr/nlp/` 仅 `nlp_inference.py`）→ 就绪前用单条推理输出降级
- ✅ BM-SEL-27 锚点 MOD-RUNTIME_INTRADAY（`runtime/intraday_main.py`，运营态）→ §2.5 盘中事件感知；✅ `akshare_provider` `stock_ipo_info`（production）→ §2.5a IPO 虹吸系数
- ⚠️ 同名消歧：`backtest/implementations/event_driven_engine.py` 是 Tick 级回测内核（tick-event-driven 架构范式，做T专用），**与本文"新闻/公告事件驱动 alpha"无关**，引用勿混淆

**盘点结论**：四类事件源（公告/新闻/龙虎榜/异动）数据链路全部 production；唯一未落盘为 `sentiment_aggregator.py`——§2.7 已裁定 sentiment_score 作事件方向触发而非截面排序，单条 `nlp_inference.py` 输出可降级承载，不阻塞 MVP。真正待新建的 sleeve 内部组件仅两项：异动识别器（§2.5）与事件影响评分（§2.5 首版公式）。
## 2. 决策：事件驱动 sleeve 定义
> 本节是对 [20_first_batch_strategies §2.4](20_first_batch_strategies.md) 策略C"事件驱动"的细化展开，逐项对齐 G10 六个讨论要点。
### 2.1 策略定位（继承 20 号，不重复裁定）
| 维度 | 定义 | 出处 |
|---|---|---|
| alpha 信号来源 | 离散事件冲击 | [20 §2.4](20_first_batch_strategies.md) |
| 换手率特征 | 中。convergence_window = 2-3 天 | [20 §2.4](20_first_batch_strategies.md) / [30 §6.4](30_multi_strategy_concurrency.md) |
| 容量上限 | 中等（介于打板小与多因子大之间） | [20 §2.4](20_first_batch_strategies.md) |
| 选股池范围 | 事件触发标的（非固定池，动态生成） | [20 §2.4](20_first_batch_strategies.md) |
| 持仓周期 | 2-10 天（视事件类型与冲击衰减曲线） | [20 §2.4](20_first_batch_strategies.md) |
| 与 regime 关系 | 选股**不读** regime 输出，只收 budget 数字；事件冲击衰减速度 regime-dependent，作为 sleeve 内部参数由 PerformanceScore 后验捕获 | [20 §2.4](20_first_batch_strategies.md) |
### 2.2 事件源（讨论要点①）
> 裁定：**复用已建多源事件基础设施，不新建数据源**。四类事件源对应已有生产态模块。

| 事件源 | 数据内容 | 已建模块（状态） | 角色 |
|---|---|---|---|
| **公告** | 业绩预告/快报、并购重组、增减持、分红送转、政策公告 | `tushare_provider` / `akshare_provider`（production，[11_d_data](../../02_domain_architecture_docs/11_d_data.md)） | 结构化事件主源（时间戳明确、PIT 严格） |
| **新闻** | 财经新闻、政策解读、行业动态 | `eastmoney_news_provider` / `cls_provider` / `rss_provider`（production） | 非结构化情绪事件源 |
| **龙虎榜** | 游资/机构席位买卖明细 | `akshare_provider`（[BM-SEL-05-A](../battle_map/battle_map_05_stock_selection.md)，production） | 资金面事件（主力行为佐证） |
| **异动** | 盘中价格/成交量相对基准的异常偏离 | 国盛证券异动雷达方法（[2026-03 国盛金工](http://stock.finance.sina.com.cn/stock/view/paper.php?autocallup=no&isfromsina=no&reportid=826626291912&symbol=sh000001)）；复用 `intraday_buy_sell_point_analyzer`（BM-SEL-05-C）+ `market_sentiment_analyzer`（BM-SEL-03-A，均 production） | 量价异动事件（需新建识别器，见 §2.5） |
**关键区分**：`corporate_action_processor`（[MOD-TRADING-004](../../../03_modules/_domain_trading/corporate_action_processor/blueprint.md)）处理除权除息/分红/送股等**持仓调整类**公司行动——机械调整不产生 alpha，**不归入事件源**，但 sleeve 须消费其事件避免除权日误判异动（§2.5 降级）。
> **⚠️ 龙虎榜 2026 信号失效提示（v1.8.0）**：[24 号 v1.8.2 实证](24_daban_strategy_detail.md)机构净买入次日胜率从 62-68% 暴跌至 **45.7%（低于随机）**，"机构净买入=利好佐证"假设反向失效。event_score 须同步校准——见 §2.5"龙虎榜 2026 机构信号失效校准"块。
### 2.3 事件分类（讨论要点②）
> 裁定：**首版六类粗分类 + Janus-Q 细分类预留**（v1.6.0 四类→六类，新增 IPO + 地缘/宏观）。分类决定冲击方向与强度。

| 事件类 | 子类（首版） | 冲击方向 | 冲击强度 | 持仓倾向 |
|---|---|---|---|---|
| **业绩** | 业绩预告/快报/正式报告、盈余惊喜（surprise） | 看 surprise 方向（超预期→多，低于预期→回避） | 中-高 | rising phase 持有 |
| **并购** | 重组/并购/资产注入/股权转让 | 看方案对价（溢价注入→多，稀释→回避） | 高（停牌复牌缺口） | 复牌后 rising phase |
| **政策** | 行业政策/货币政策/产业政策 | 看政策受益方向 | 中（板块传导） | rising phase + 板块传导 |
| **突发** | 黑天鹅/董事长被查/ST/重大事故/异动 | 多为利空（回避/剔除）；少数题材爆发（多） | 高-极高 | 利空→剔除；题材→短持 |
| **IPO/再融资**（v1.6.0） | 大型 IPO 上市（科创板/创业板）、定增/配股解禁 | 看虹吸方向（IPO→存量板块流动性抽离利空存量；IPO 标的前 5 日无涨跌幅限制博弈） | 高（科创板最大 IPO 募资 579-666 亿可吸金 500 亿+） | 上市前→完成主仓布局+保留现金；上市后→存量板块降仓避险 |
| **地缘/宏观**（v1.6.0） | 战争/制裁/贸易摩擦/汇率冲击/大宗商品价格异动 | 看传导链方向（中东冲突→油气/黄金/军工多；贸易战→稀土/农业多；汇率贬值→出口导向多） | 高-极高（持续性强于业绩/并购） | rising phase 持有 + 板块传导链跟踪 |
**细分类预留**：[Janus-Q（arXiv 2026-02）](https://arxiv.org/html/2602.19919v2) 标注 10 fine-grained event types（含 sentiment label 与关联股票），event-to-CAR 建模范式可作增强方向（§5 待裁定-2）。首版不引入（避免 NLP 标注带宽过重），用六类粗分类 + 情绪分数承载。
### 2.4 事件冲击衰减曲线（讨论要点③）
> 裁定：**首版用经验衰减曲线（按事件类×衰减阶段）；Hawkes 自激发建模登记为暂缓前沿**。衰减速度 regime-dependent，作 sleeve 内部参数后验捕获。

**实证依据**（[20 §2.4](20_first_batch_strategies.md) 已引）：rising phase（day 0-5）风险调整收益上升、RVR 较 decay phase 高 9.5x，decay phase（day 6-15）冲击衰减收益回归（[Beyond the Event Horizon 2025](https://www.preprints.org/manuscript/202506.0079)）；情绪 IC 衰减 regime-dependent——危机期集中短-中 horizon、宏观不确定期扩散窗口延长（[Yukka 2026-05](https://cdn.prod.website-files.com/66b4f3430903efa023fe741b/69fdded32f3d7e02f17ff3f8_Sentiment%20Decay%20&%20Source%20Selection%20in%20Global%20Equity%20Markets%20-%20White%20Paper.pdf)）。

**首版衰减模型**：按事件类预设经验半衰期，rising phase 持有、decay phase 兜底退出：

| 事件类 | rising 半衰期（初拟） | decay 退出窗 | 依据 |
|---|---|---|---|
| 业绩 | 3-5 天 | day 6-8 | PEAD 实证 rising 约 5 天；[FMP 2026-04](https://intelligence.financialmodelingprep.com/education/other/tracking-postearnings-announcement-drift-with-fmps-market-data) 衰减曲线 day 9 进入平台期（exit zone） |
| 并购 | 1-3 天（复牌后） | day 4-6 | 停牌复牌缺口一日消化大半 |
| 政策 | 3-7 天 | day 8-12 | 政策传导链较长，板块轮动延续 |
| 突发（题材） | 1-3 天 | day 4-5 | 题材爆发快衰减快 |
| **IPO/再融资**（v1.6.0） | 上市前 3-5 天（布局窗） | 上市后 day 1-5（虹吸期） | 科创板大型 IPO 前 5 日无涨跌幅限制→上市日虹吸峰值，存量板块 day 1-3 跌幅最大，day 5 后虹吸衰减 |
| **地缘/宏观**（v1.6.0） | 5-15 天（远长于业绩/并购） | day 16-30 | 美伊战争期间资源股 rising 可达 2-4 周（[Sinong Xiao 2026](https://www.atlantis-press.com/proceedings/edms-2026/)：资金流→收益传导牛/熊 regime 异质，地缘主线属"结构性 regime 切换"非一次性冲击） |
**⚠️ 极端反应反转（PEAD Inversion，2026 新增关键修正）**：rising→decay 单调衰减模型**仅适用于温和反应（event-day reaction ∈ [-3%, +3%]）**。极端事件日反应存在**反转**而非延续（[Vortex Capital 2026-05](https://www.vortexcapitalgroup.com/insights/the-mega-cap-pead-inversion-when-the-reaction-is-the-trade-and-when-it-is-the-trap)，mega-cap tech 2023-2026）：

| event-day 反应 | 经典 PEAD 预测 | 2026 实证 | 数值 |
|---|---|---|---|
| 强正（>+3%） | 延续上涨 | **反转下跌** | 20 日中位 -5.58%、5 日 -3.20% |
| 强负（<-3%） | 延续下跌 | **反弹** | 5 日中位 +4.20%、20 日 +3.46% |
| 温和正（0~+3%） | 延续 | 延续后衰减 | 5 日 +1.71%，20 日衰减 |
| 温和负（-3%~0） | 延续 | 短跌后走平 | 5 日 -1.03%，20 日走平 |
**根因**：衍生品 gamma、0DTE 期权流、暗池将数周隐含波动率压缩到单一隔夜窗口，机构再定价盘前完成，剩余为做市商对冲+散户追涨，随后均值回归。
**首版修正裁定**：
- **温和反应（|reaction| ≤ 3%）**：沿用 rising→decay 经验衰减曲线（上表）
- **极端反应（|reaction| > 3%）**：**不追涨/不杀跌**——事件日收盘即信号终点；已持仓且极端正向→提前进入 decay 退出（不等 rising 半衰期）；极端负向→不恐慌加仓，等 day 2-3 确认（CVD/量价结构是否吸收卖压）再决策

```python
def check_selling_pressure_absorbed(symbol, day2_3_data, baseline_volume_ratio=1.5, cvd_threshold=0.0):
    """吸收卖压判定（PEAD Inversion 极端负反应 day 2-3 确认）。day2_3_data: day 2-3 分钟级 OHLCV"""
    import numpy as np
    # CVD（累计成交量差）：close>mid=买方主动，close<mid=卖方主动
    mid_price = (day2_3_data['high'] + day2_3_data['low']) / 2
    delta = np.where(day2_3_data['close'] > mid_price, day2_3_data['volume'],
                     -day2_3_data['volume'])
    cvd = np.cumsum(delta)
    volume_ratio = day2_3_data['volume'].mean() / day2_3_data['volume'].rolling(5).mean().mean()
    price_stabilized = day2_3_data['close'].iloc[-1] >= day2_3_data['close'].iloc[0] * 0.98  # 跌幅<2%
    # 吸收卖压判定：CVD 转正（买盘接货）+ 量能放大（放量消化）+ 价格企稳
    absorbed = (cvd[-1] > cvd_threshold) and (volume_ratio > baseline_volume_ratio) and price_stabilized
    return {
        "absorbed": absorbed,  # True=卖压已吸收可布局, False=卖压未止继续观望
        "cvd_final": cvd[-1],
        "volume_ratio": volume_ratio,
        "price_stabilized": price_stabilized,
    }
```
CVD 转正因为买方主动成交量超过卖方=聪明资金低位接货；三者共振才确认"吸收卖压"。CVD 与 [22 板块轮动](22_sector_rotation_spec.md) 量能维度同源。**A 股适配**：mega-cap 实证需 A 股回测验证（大小盘信息扩散速度不同），登记 §5 待裁定-5。

**PEAD.txt 文本惊喜（2026 关键发现）**：[费城联储 PEAD.txt 论文（Meursault et al.）](https://marketmaker.cc/en/blog/post/llm-alpha-mining-earnings-calls/)构建纯文本 SUE（SUE.txt，不用数值盈余数据）——文本漂移**是经典数值 PEAD 的 2 倍**，数值 PEAD 已近消失而文本漂移仍显著。**结论**：NLP 文本信号比数值惊喜更有 alpha 价值（支撑 §2.7 NLP 复用裁定）。

> **事件驱动六因子矩阵（v1.5.0，交叉引用 [20 §2.4 v1.4.4](20_first_batch_strategies.md)）**：
>
> | 因子 | 定义 | 实证 | 维度 | 当前状态 |
> |---|---|---|---|---|
> | **ORJ**（隔夜跳空） | `ORJ = open/pre_close - 1`（事件日隔夜收益率） | collinseow 2026-02 季度超额 6.78% | 事件日隔夜 | ✅ §2.4/§2.5 已施工 |
> | **PEAD Inversion**（极端反应修正） | \|reaction\|>3% 反转而非延续 | Vortex Capital 2026-05 | 极端反应方向 | ✅ §2.4 已施工 |
> | **dReport**（披露日提前天数） | `dReport = 法定披露截止日 - 实际披露日`（正值=提前） | 招商证券 10 年回测年化超额 4.88%/Sharpe 1.44；大幅提前 T+5 上涨概率 70-75% | 事件时点 | 🟧 待施工（§6 待定问题） |
> | **Jump on PEAD**（公告后价格跳跃） | 公告后 5 日窗口 CAR 的跳跃分量 | 华泰金工 5 日 IC=10.96% | 事件冲击强度 | 🟧 待施工 |
> | **隔夜趋势** | 隔夜收益率 20 日滚动均值/动量 | 西部证券 Rank IC=-0.1687、中证 2000 年化超额 7.97% | 日常隔夜（非事件日） | 🟧 待施工 |
> | **AStockEvent Feed** | 13+ 事件类型结构化 Feed（减持/ST/监管函/解禁/回购/重组等） | GitHub 2026-06-13 | 事件结构化数据源 | 🟧 待施工（NLP 管道工程化候选） |
>
> **协同关系**：dReport（披露时点）是 PEAD 事件时点扩展——dReport 大幅提前 + ORJ>3% = 强信号叠加；Jump on PEAD（5 日跳跃）是 ORJ（单日跳空）强度扩展——ORJ 即时确认、Jump 滚动跟踪；隔夜趋势是 ORJ 时序扩展——事件日 ORJ>3% + 20 日隔夜趋势为正 = 强信号叠加；AStockEvent 13 类可作 Janus-Q 10 类细分类的 A 股本土化映射，直接驱动 dReport 计算。
>
> **施工优先级**：dReport（4.88%）与 Jump on PEAD（IC 10.96%）有实证窗口，优先级最高——可作 NLP 管道未就绪前的数值 alpha 补充（与 ORJ 同属降级算法，不依赖 NLP）；隔夜趋势接入因子工厂；AStockEvent 远期评估。
>
> **对 [21 号 §3.6](21_stock_selection_engine.md) 漏斗③ event_impact_score 的落地**：`event_impact_score = w1·ORJ_z + w2·dReport_z + w3·Jump_on_PEAD_z + w4·overnight_trend_z + PEAD_inversion_gate`（权重待 G10 校准，PEAD Inversion 作门控非加权项）。

**Hawkes 自激发建模（暂缓前沿）**：[Hawkes Processes for Investors 2026-02](https://stockalpha.ai/alpha-learning/hawkes-processes-for-investors-modeling-self-exciting-volatility-bursts) 用自激发点过程建模事件聚类（branching ratio n=α/β，n→1 近临界=事件簇爆发）。2026 实证：[中国股市传染（arXiv 2512.08000）](https://arxiv.org/html/2512.08000v1/)时空 Hawkes 建模 A 股板块轮动（与 [G06](22_sector_rotation_spec.md) 契合）；[Price Discovery 物理（arXiv 2601.11602）](https://arxiv.org/html/2601.11602v2)区分外生（新闻）vs 内生（反馈）资金流；[Persia 2026-06](https://proceedings.systemdynamics.org/2026/papers/P1265.pdf)多元 Hawkes 跟踪 VIX；[MDPI Entropy 2026-08-06](https://www.mdpi.com/1099-4300/28/8/887)图熵在峰值回撤前 7-12 交易日达历史极值→firm 层系统性风险预警；[Hawkes-Driven OTC（arXiv 2608.02002）](https://arxiv.org/html/2608.02002v1)幂律 RFQ 记忆+内生报价影响（做市/流动性层）。实操参考 [MetricGate 2026-06](https://metricgate.com/blogs/hawkes-self-exciting-process-r/)（MLE 估 μ/α/β→n=α/β→intensity→波动率 transfer function→升级触发器）。
> 裁定：Hawkes 登记暂缓（§5 待裁定-1）——经验衰减曲线+极端反应修正已承载 rising/decay 纪律，branching ratio 监控更适合 firm 层风险（[G17](36_var_es_monitoring.md)/[G18](37_liquidity_crisis_protocol.md)），留给风控层评估。
### 2.5 事件信号→选股映射（讨论要点④）
> 裁定：**复用选股漏斗 BM-SEL-19（事件驱动分布筛选，design/MOD-SIG-049），不新建独立选股 pipeline**。事件→候选标的生成 + 事件影响评分 → 注入漏斗第四层。

**事件→选股映射链路**：事件源（公告/新闻/龙虎榜/异动）→ 事件分类（六类）+ 情绪分数（NLP）→ 事件影响评分 = f（事件类， 冲击方向， 冲击强度， 衰减阶段） → 注入选股漏斗 **BM-SEL-19** 事件驱动分布筛选（design，MOD-SIG-049，50→30只：事件影响评分 L2-D 图谱来自 BM-SEL-11 + 事件驱动条件 PDF 修正[上涨概率下降 >15% 淘汰] + 事件传导链风险[BM-SEL-11]）→ sleeve 持仓（rising phase 为主，decay phase 退出）。

**关键接口**：
- **事件→候选标的**：事件触发标的即候选（非固定池），事件类×冲击方向决定入池/剔除（利空→剔除持仓或回避）
- **事件影响评分（首版显式公式）**：`event_score = event_class_weight[event_class]（业绩=1.0/并购=1.2/政策=0.8/突发=1.5/IPO=1.3/地缘=1.4）× surprise_direction（+1 利好/-1 利空/0 中性）× sentiment_score（NLP [-1,+1]，#ARCH-NLP-PIPELINE-001）× decay_stage_factor（rising=1.0/decay=0.5/post-decay=0.2）× extreme_reaction_modifier（|reaction|>3% → 0.3，§2.4 极端反转修正；|reaction|≤3% → 1.0）`。event_score ∈ [-1.5, +1.5]，正→入池做多候选，负→剔除/回避；**|event_score| < 0.2 → 无信号（噪声），不动作**。函数化封装见下方辅助函数① `event_score_single_factor`。

> **龙虎榜 2026 机构信号失效校准（v1.8.0，与 [24 号 §3.5 v1.8.2](24_daban_strategy_detail.md) 同步）**：机构净买入次日胜率 62-68%→**45.7%（<50% 随机，反向失效）**，event_score 龙虎榜佐证须校准，与 23-A 游资接力评分口径一致。
>
> | 维度 | 2018-2023 基线 | 2026 实测 | event_score 校准含义 |
> |---|---|---|---|
> | 机构净买入次日胜率 | 62-68% | **45.7%（<50% 随机）** | 方向性佐证失效——机构净买入不再自动强化 event_score，降级为中性参考 |
> | 净买率 >12% 样本 20 日均收 | — | **+5.11%（仍有效）** | 佐证转向"净买率极端值"，用 12% 硬阈值替代软评分 |
> | 外资三巨头龙虎榜占比 | 偶现 | **19.41%（常规军）** | "外资买入=利好"被摊薄，须按席位类型差异化（外资≠量化机构≠传统游资） |
> | 拉萨天团活跃度 | 高频主导 | **同比 -35%（退潮）** | 传统游资退场，"游资接力佐证"弱化 |
>
> **施工建议**：①机构净买入佐证权重砍半或归零，实盘 3-6 月后重新校准；②新增 `dragon_tiger_corroboration_modifier`——净买率≥12% → ×1.2，<12% → ×1.0；③席位类型差异化——量化席位触发 [24 号 §3.10/§3.11 过滤](24_daban_strategy_detail.md)（≥3 量化席位+买入占比>30% → 佐证无效化）；④数据源：双表 `dragon_tiger`（汇总）+ `dragon_tiger_seat`（**席位明细**，Top5 买卖席位合并去重，tasks.yaml 盘后调度），席位类型字段消费自 `dragon_tiger_seat`。
>
> ```python
> def dragon_tiger_corroboration_modifier(event, dragon_tiger_data):
>     """龙虎榜佐证修正因子（2026 失效校准）。返回乘法因子 ∈ [0.7, 1.2]：无数据→1.0；净买率≥12%→1.2；<12%→1.0；量化 hard（≥3席+占比>30%）→×0.7；soft（≥3席）→×0.85"""
>     if dragon_tiger_data is None:
>         return 1.0  # 非龙虎榜标的 → 不修正
>     net_buy_ratio = dragon_tiger_data.net_buy_amount / dragon_tiger_data.total_turnover
>     # ① 净买率极端值硬阈值门控（+5.11% 20日均收仍有效）
>     if net_buy_ratio >= 0.12:
>         base_modifier = 1.2  # 强佐证加分
>     else:
>         base_modifier = 1.0  # 机构净买入方向失效→不加分
>     # ② 量化席位过滤（24号 §3.10 + §3.11 双阈值预警）
>     quant_seats = [s for s in dragon_tiger_data.buyer_seats if s.type == "quant_inst"]
>     quant_count = len(quant_seats)
>     quant_buy_ratio = (sum(s.buy_amount for s in quant_seats)
>                        / dragon_tiger_data.total_buy) if dragon_tiger_data.total_buy > 0 else 0.0
>     if quant_count >= 3 and quant_buy_ratio > 0.30:
>         base_modifier *= 0.7   # hard: 量化主导→佐证无效化（次日高开低走概率70%）
>     elif quant_count >= 3:
>         base_modifier *= 0.85  # soft: 量化席位同现→佐证弱化（后续3日下跌概率58%）
>     return base_modifier
>
> # event_score_final = event_score * dragon_tiger_corroboration_modifier(event, dt_data)
> # 仅当事件源含龙虎榜佐证时调用；无龙虎榜数据时 modifier=1.0 不影响原 event_score
> ```
>
> **与 24 号口径一致性**：共用 `dragon_tiger` 表 + 12% 净买率硬阈值 + [24 号 §3.11 `detect_quant_seat_warning`](24_daban_strategy_detail.md) 量化席位双阈值，确保两 sleeve 对龙虎榜信号解读一致，避免跨 sleeve 歧义。

**SUE+EAR 双因子增强评分（v1.2.0 升级，可选）**：[Rockstead 2026-05 两因子框架](https://rockstead.com/market-insights/capturing-post-earnings-drift-a-two-factor-approach/)证明**SUE 与 EAR 近零相关（r=0.004）**，组合提供真分散化。首版单因子将"市场反应"粗化为 `extreme_reaction_modifier`（二值 0.3/1.0），双因子版升为连续信号：
```python
# v1.2.0 SUE+EAR 双因子增强评分（业绩类事件专用，其他类沿用首版单因子）
def event_score_dual_factor(event):
    """业绩类双因子：SUE(基本面惊喜) + EAR(市场反应)。Rockstead 2026-05: r=0.004 近正交，组合年化 18.50%"""
    # 因子1：SUE 标准化未预期盈余（v1.7.1 修复：统一 event 属性 + wind_consensus_eps 调用）
    sue = (event.actual_eps - wind_consensus_eps(event.symbol, event.date)) / rolling_std_surprise(event.symbol)
    sue_z = winsorize_zscore(sue)  # [-3, +3]
    # 因子2：EAR 盈余公告收益（3日 CAR [-1,+1]，FF 6组合基准）
    # EAR 含反转成分（Q5-Q1 EAR 年化 -3.39%），用于"识别过度反应"而非"追涨"
    ear = cumulative_abnormal_return(event.symbol, day_start=-1, day_end=+1,
                                     benchmark="ff6_size_bm")
    reaction_extremity = abs(ear) / 0.03  # 相对 3% 阈值的极端度
    ear_reversal_weight = min(reaction_extremity, 1.0)  # 0~1，越极端越反转
    # 组合分：SUE 漂移方向 - EAR 过度反应部分
    combined = sue_z * (1 - ear_reversal_weight * 0.5) - ear * ear_reversal_weight * 10
    # combined > 0 → 漂移延续占优 → 入池做多；< 0 → 过度反应反转占优 → 不追涨/回避
    return combined
```
**双因子 vs 单因子裁定**：首版 `event_score` 保留为默认；业绩类优先双因子（有明确数值惊喜与市场反应可分离），其他五类无标准化"预期"沿用单因子+情绪分数。**升级路径**：NLP 管道就绪后 SUE 可替换为 PEAD.txt 文本惊喜（漂移 2 倍）。
**SUE 预期构建——Zyberno seasonal random walk 备选（2026-08-10 补）**：[Zyberno 2026-08-05](https://zyberno.com/earnings-surprise/ACNB/) 从 **SEC 实际报告构建预期**（不用分析师 consensus）：`Expected_EPS_q = EPS_(q-4) + drift`（drift = 近期同比季度 EPS 变化均值），`SUE = (Actual_EPS_q - Expected_EPS_q) / σ(trailing seasonal surprises)`，winsorized ±4。

**核心优势**：从实际报告构建预期**无法被 guidance management 扭曲**（管理层可引导分析师预期，无法扭曲自身历史实际报告）；Latané & Jones (1977) 原始 SUE 即此形式。对比 consensus_eps 方案：无 guidance management 风险、数据免费公开，但需 ≥12 个干净季度历史（新股/深度周期股不适用）。**裁定**：MVP 保留 `consensus_eps`（分析师预期已接入、A 股覆盖标的信号密集）；Zyberno 记为 Phase 2 候选——用于小盘股无覆盖标的 + 交叉验证 consensus SUE（同向→增强，背离→guidance management 风险信号）。

**确认型入场模式（v1.2.0 新增）**：[NexusFi 2026-06 三模式](https://nexusfi.com/a/automation/event-driven-trading-automation)——①fade the initial move（极端反应）②momentum continuation（温和反应）③confirmation-based entry（模糊事件）。首版 `should_enter` 缺第三分支，补全：
```python
# 确认型入场（v1.2.0 补全 should_enter 的第三分支）
def should_enter_with_confirmation(event, current_position, day0_reaction):
    """事件触发后入场决策（含确认型）"""
    if market_event_integrator.current_mode == MarketMode.EMERGENCY:
        return False  # 熔断期停止开仓
    score = compute_event_score(event)

    # 1. 极端反应（|reaction|>3%）：不入场（§2.4 PEAD Inversion，反转风险）
    if abs(day0_reaction) > 0.03:
        return ("WAIT_CONFIRM", 2)  # 等 day 2 确认是否反转
    # 2. 温和反应且有明确信号（|score|≥0.2）：立即入场（momentum continuation）
    if abs(score) >= 0.2:
        if score > 0 and current_position == 0:
            return True
        if score < 0 and current_position > 0:
            return "EXIT"
    # 3. 模糊事件（|score|<0.2 且 |reaction|≤3%）：确认型入场
    # 等 day 1-2 量价确认（成交量放大+方向一致）再入场，避免噪声
    if 0 < day0_reaction <= 0.03 and has_volume_confirmation(event.symbol, days=1):
        return True  # 温和正反应 + 次日量价确认 → 入场
    return False
```
**ORJ 隔夜跳空 + 净利润断层（v1.3.0，A 股业绩事件第三维信号）**：SUE+EAR 捕获"数值惊喜"与"日内反应"两维，**隔夜跳空**是独立第三维——A 股 T+1 下财报多盘后披露，次日开盘跳空=市场隔夜消化后"第一反应"，与日内 EAR 正交：

| 信号维度 | 捕获内容 | 时间窗 | A 股适配 |
|---|---|---|---|
| SUE（数值惊喜） | 基本面超预期幅度 | 公告日 | ✅ 一致预期可得（万得/同花顺） |
| EAR（日内反应） | 3 日 CAR [-1,+1] | 公告前后 3 日 | ✅ FF6 基准或行业基准 |
| **ORJ（隔夜跳空）** | 盘后→次日开盘的隔夜消化 | 公告日收盘→次日开盘 | ✅ A 股 T+1 天然隔夜窗口 |
**ORJ 定义**（[Bahcivan et al. 2023](http://hulusibahcivan.com/wp-content/uploads/2023/05/New-Avenues-in-Expected-Returns_Investor-Overreaction-and-Overnight-Price-Jumps-in-US-Stock-Markets_May-2023.pdf)，9,718 只美股实证）：隔夜跳空 = 次日开盘价相对公告日收盘价的幅度（A 股 T+1 下财报多盘后披露 → 次日开盘=市场隔夜第一反应）。仅需 OHLC 数据。单行实现：`def overnight_return_jump(symbol, event_date): return open_price(symbol, event_date + 1) / close_price(symbol, event_date) - 1`（三因子融合 `event_score_triple_factor` 调用此函数）。

**实证**：Bahcivan 2023——正/负跳空后 5 日内显著反转，套利成本越低反转越大（A 股小盘股套利约束低，反转或更强）；净利润断层（A 股本土化 ORJ，[中国证券报 2026-04](http://m.ce.cn/cj/gd/202604/t20260424_2925768.shtml)）=财报后跳空上涨，财报季有效性阶段性凸显；[火山引擎 2026-04 夜盘回测](https://developer.volcengine.com/articles/7629162484989394995)——财报次日夜盘预测准确率仅 54.7%/反转概率>45%，宏观事件夜盘可信度>65%——业绩类 ORJ 须警惕"跳空后反转"，与 §2.4 PEAD Inversion 一致。**ORJ 与 PEAD Inversion 协同**：ORJ>+3% 触发反转逻辑不追涨；ORJ ∈ [0,+3%] 与 SUE 同向则加权入场。ORJ 是极端反应的**前置预警**（盘后公告+次日开盘即判定，比等 3 日 EAR 更早）。
**预期差 + Whisper Number（v1.3.0，SUE 的 A 股增强源）**：一致预期是静态快照（公告日已陈旧）。[EarningsWhispers 2026-08-05](https://beta.earningswhispers.com/about-whispers)：Whisper Number 比一致预期**准确率高 69.7%**，whisper>consensus 超 5% 时 beat 概率 ~75%。A 股等价物=**分析师预测修正动量**（一致预期近期变动方向，万得/同花顺时序可计算）。**A 股预期差构建**（[中邮证券 2026-06 业绩之锚7](https://finance.sina.com.cn/stock/stockzmt/2026-06-05/doc-iniaikau2934869.shtml)）：季报/半年报用财报后一致预期**变动**衡量超预期；年报用一致预期与公布值静态比较；一季报预期差策略 30 天超额 1.9%/60 天 2.8%（胜率最高报告期）；**年报陷阱**——A 股不定价业绩利好，年报事件降 SUE 权重。
```python
# v1.3.0 预期差 + 修正动量（替代/增强 SUE 的 consensus 基准）
def expectation_gap_with_revision_momentum(symbol, actual_eps, event_date, report_type):
    """A 股预期差 + 分析师修正动量（Whisper Number 本土化）。中邮证券 2026-06: 一季报 30天超额 1.9%/60天 2.8%"""
    # 1. 静态预期差（年报用）：actual vs consensus
    consensus = wind_consensus_eps(symbol, event_date)
    static_gap = (actual_eps - consensus) / abs(consensus) if consensus != 0 else 0
    # 2. 动态预期差（季报/半年报用）：财报后一致预期变动（上调=超预期）
    consensus_before = wind_consensus_eps(symbol, event_date - 1)
    consensus_after = wind_consensus_eps(symbol, event_date + 5)  # 公告后5日一致预期
    revision_momentum = (consensus_after - consensus_before) / abs(consensus_before)
    # 3. 报告期权重调整（中邮证券实证：一季报最优，年报最差）
    report_weight = {
        "Q1": 1.0,    # 一季报：胜率最高
        "semi": 0.8,  # 半年报：次优
        "Q3": 0.7,    # 三季报：中等
        "annual": 0.4 # 年报：A股不定价业绩利好，降权
    }.get(report_type, 0.7)
    # 4. 组合预期差：动态优先（季报），年报用静态且降权
    if report_type != "annual":
        gap = revision_momentum
    else:
        gap = static_gap * report_weight
    return gap  # gap > 0 = 超预期，gap < 0 = 不及预期
```
**三因子融合（SUE×EAR×ORJ + 预期差增强）**：
```python
# v1.3.0 三因子融合评分（业绩类事件）
def event_score_triple_factor(event):
    """SUE(预期差增强) + EAR(日内反应) + ORJ(隔夜跳空)。三因子两两近正交 → 真分散化"""
    # 因子1：SUE 增强（预期差替代静态 consensus）
    sue = expectation_gap_with_revision_momentum(
        event.symbol, event.actual_eps, event.date, event.report_type)
    sue_z = winsorize_zscore(sue)  # [-3, +3]
    # 因子2：EAR 日内反应（同 v1.2.0）
    ear = cumulative_abnormal_return(event.symbol, -1, +1, benchmark="ff6_size_bm")
    # 因子3：ORJ 隔夜跳空。方向与 SUE 一致→加权；极端（>3%）→触发反转（§2.4）
    orj = overnight_return_jump(event.symbol, event.date)
    orj_signal = orj if abs(orj) <= 0.03 else -orj * 0.5  # 极端跳空反转修正
    # 三因子融合：SUE 主导 + ORJ 前置预警 + EAR 过度反应修正
    reaction_extremity = max(abs(ear), abs(orj)) / 0.03
    reversal_weight = min(reaction_extremity, 1.0)
    combined = (sue_z * (1 - reversal_weight * 0.3)    # SUE 漂移（极端反应时降权）
                + orj_signal * 2.0                       # ORJ 隔夜第一反应（温和时加权）
                - ear * reversal_weight * 10)            # EAR 过度反应反转修正
    # combined > 0 → 入池做多；< 0 → 不追涨/回避
    return combined
```
**三因子 vs 双因子裁定**：v1.2.0 双因子保留为**降级默认**（一致预期时序不可得时）；v1.3.0 三因子为**主选**（万得/同花顺时序可得时）。ORJ 仅需 OHLC 无额外数据依赖；预期差依赖一致预期时序（已订阅）。**升级路径不变**：NLP 管道就绪后 SUE→PEAD.txt 文本惊喜。
> **六因子矩阵交叉引用**：完整六因子矩阵（ORJ/PEAD Inversion/SUE+EAR/dReport/Jump on PEAD/隔夜趋势/AStockEvent Feed）、协同关系、施工优先级与 §2.4 PEAD 衰退根因协同，见 §2.4"事件驱动六因子矩阵"块（v1.5.0，对齐 [20 §2.4 v1.4.4](20_first_batch_strategies.md)），本处不重复登记。

- **BM-SEL-11 知识图谱增强（待就绪）**：复用 [BM-SEL-11](../battle_map/battle_map_05_stock_selection.md)（design）传导链+因子区分。就绪后可升级为 [LLM 增强动态金融知识图谱（arXiv 2607.10932, 2026-07）](https://arxiv.org/pdf/2607.10932)——CIS/PIS 因子 rank IC 与 long-short Sharpe 优于纯情绪/直接事件信号（Fama-MacBeth t-stat ≈ 3.7），为 BM-SEL-11 的 2026 对标方向
- **BM-SEL-19 开通条件**：事件数据源 + 知识图谱 + NLP 就绪。**未开通则跳过本层，第三层（精筛）直接进第五层**——降级不阻塞
- **异动识别器（需新建）**：[国盛证券异动雷达 2026-03](http://stock.finance.sina.com.cn/stock/view/paper.php?autocallup=no&isfromsina=no&reportid=826626291912&symbol=sh000001)——个股与基准分钟序列价格/成交量相关系数<0 触发"异动"，叠加超额收益方向判定。实证（2016-2026 中证800）：通道策略年化超额 7.51%/IR 2.48；叠加负向筛选 9.77%/IR 2.92

**进出场触发算法（首版）**：入场触发首版 `should_enter(event, current_position)` 为四分支——EMERGENCY 熔断停开仓 → `compute_event_score(event)` 评分 → |score|<0.2 噪声不动作 → score>0 且空仓开多 / score<0 且有持仓返回 "EXIT"；该逻辑已并入上方 `should_enter_with_confirmation` 分支 1-2（v1.2.0 确认型为完整版，不重复列码）。出场触发三道线：
```python
# ── 出场触发（三道线）──
def should_exit(event, position, holding_days):
    """持仓后何时退出"""
    # 1. decay phase 兜底退出（按事件类衰减表，§2.4）
    if holding_days > decay_exit_window[event.class_]:
        return "DECAY_TIMEOUT"
    # 2. 极端反应提前退出（§2.4 PEAD Inversion）
    if abs(event.day0_reaction) > 0.03 and holding_days >= 1:
        return "EXTREME_REACTION"  # 不等 rising 半衰期
    # 3. 反向事件触发（新利空覆盖旧利好）
    if has_contradictory_event(event.symbol, event.direction):
        return "CONTRADICTION"
    return False
```
**施工算法补全（v1.7.0）**：上述 `should_enter`/`should_exit`/`should_enter_with_confirmation` 调用的 5 项辅助函数/数据结构定义如下，补全后进出场触发算法施工闭环：
```python
# ══ 施工算法补全：5 项辅助函数与数据结构 ══

# ── ① event_score 单因子函数化（§2.5 首版内联公式封装）──
def event_score_single_factor(event):
    """首版单因子评分（并购/政策/突发/IPO/地缘五类通用）。∈ [-1.5,+1.5]，正→入池/负→剔除，|score|<0.2→噪声不动作。"""
    event_class_weight = {
        "earnings": 1.0, "ma": 1.2, "policy": 0.8,
        "surprise": 1.5, "ipo": 1.3, "geopolitical": 1.4,  # §2.5 v1.6.0 补 IPO/地缘权重
    }
    return (
        event_class_weight.get(event.class_, 1.0)
        * event.surprise_direction              # +1 利好 / -1 利空 / 0 中性
        * event.sentiment_score                  # NLP 情绪分数 [-1, +1]
        * event.decay_stage_factor               # rising=1.0 / decay=0.5 / post-decay=0.2
        * event.extreme_reaction_modifier        # |reaction|>3% → 0.3（§2.4）/ 否则 1.0
    )

# ── ② compute_event_score 调度函数（按事件类选择单/双因子）──
def compute_event_score(event):
    """评分调度器：业绩类→SUE+EAR 双因子，其他五类→首版单因子。should_enter 系列统一调用，扩展单点修改。"""
    if event.class_ == "earnings":  # 业绩类有标准化"预期"概念，用双因子
        return event_score_dual_factor(event)   # §2.5 v1.2.0
    return event_score_single_factor(event)

# ── ③ decay_exit_window 数据结构（§2.4 衰减表 rising+decay 总长 = 持仓天数上限）──
decay_exit_window: dict[str, int] = {
    "earnings":     10,   # 业绩：rising 5 + decay 5（PEAD 漂移 5-10 日）
    "ma":           15,   # 并购：rising 7 + decay 8（信息消化慢于业绩）
    "policy":       20,   # 政策：rising 10 + decay 10（政策传导链长于并购）
    "surprise":      5,   # 突发：rising 2 + decay 3（快进快出，情绪脉冲）
    "ipo":          15,   # IPO：上市后 day1-5 虹吸期 + day6-15 衰减（§2.5a）
    "geopolitical": 25,   # 地缘：rising 5-15 远长于业绩/并购（§2.4 v1.6.0）
}

# ── ④ has_contradictory_event 反向事件检测（should_exit 第三道线）──
def has_contradictory_event(symbol, current_direction, lookback_days=5):
    """检测近期是否有与持仓方向相反的事件。current_direction 恒 +1（A 股不能做空）。"""
    recent_events = event_store.query(
        symbol=symbol, since=trading_days_ago(lookback_days),
    )
    for ev in recent_events:
        if ev.surprise_direction != 0 and ev.surprise_direction != current_direction:
            return True
    return False

# ── ⑤ has_volume_confirmation 量能确认（确认型入场第三分支）──
def has_volume_confirmation(symbol, days=1, min_ratio=1.5):
    """事件后成交量是否放大。min_ratio: 最低量比阈值（默认 1.5 倍 20 日均量）。"""
    recent_vol = volume_series(symbol, days=days)        # 事件后 days 日成交量序列
    baseline_vol = volume_ma(symbol, window=20)          # 20 日均量基线
    if baseline_vol <= 0:
        return False  # 基线缺失（新股/长期停牌）→ 保守不入场
    return recent_vol.mean() >= min_ratio * baseline_vol
```
> **⚠️ 接口契约精确化（v1.9.0 代码侧审计）**：`event_store`/`volume_series`/`volume_ma`/`trading_days_ago` 是**接口契约（待落码）而非已建函数**——全仓扫描确认 `src/zephyr/` 无此四者定义（已有 `EventStore` 类在 `gov_audit`/`infrastructure` 域，是治理/系统事件存储，勿混用）。落码路径：市场事件存储基于 `fund_news_data` 表+事件分类落库实现 `event_store.query(symbol, since)`；`volume_series`/`volume_ma` 基于个股日K 表（pit_query PIT 查询基座，[11_d_data](../../02_domain_architecture_docs/11_d_data.md) production）薄封装；`trading_days_ago` 复用交易日历。**数据基座全部具备，仅缺四个薄封装函数**（工程量 < 1 天），不阻塞设计闭环。

**五层事件驱动架构映射（v1.2.0）**：[NexusFi 2026-06 五层架构](https://nexusfi.com/a/automation/event-driven-trading-automation)与本系统模块一一对应（[Closelook 2026-04](https://closelook.net/reports/post-earnings-drift/) 三层递进 regime→trend→pattern 同构，top/bottom quintile 年化超额 ~13%）：

| NexusFi 五层 | 职责 | 本系统对应模块 | 状态 |
|---|---|---|---|
| ① 事件摄取 | 消费日历/API/新闻流，区分计划 vs 突发 | `news_collector` + 新闻三源 + 公告源 | production |
| ② 标准化 | 时间戳归一/去重/实体识别/严重度评分 | `news_dedup` + `corporate_action_processor` + NLP 实体识别（#ARCH-NLP-PIPELINE-001） | production + 在建 |
| ③ 信号生成 | 惊喜分/情绪分类/置信度评分 | event_score（§2.5）+ sentiment_score + 异动识别器 | design |
| ④ 执行 | 事件感知订单路由/预挂单/部分成交 | [40_execution_broker](40_execution_broker.md) + [41_buy_flow](41_buy_flow.md)/[42_sell_flow](42_sell_flow.md) | active |
| ⑤ 独立风控 | **独立于策略逻辑**——仓位/价差/波动/单事件亏损限额 | FirmRiskAggregator（[MOD-POS-021](../../../03_modules/_domain_position/firm_risk_aggregator/blueprint.md)）+ drawdown Protocol（[G16](35_drawdown_protocol_impl.md)）+ VaR/ES（[G17](36_var_es_monitoring.md)） | active |
**关键纪律**（NexusFi）：风控层须**独立于策略代码路径**（策略与风控共享路径时策略 bug 会禁用风控）。Model A firm 层独立于 sleeve（[30 §2.1](30_multi_strategy_concurrency.md)）天然满足；sleeve 读 EMERGENCY 停止开仓是 sleeve 读风控信号，方向正确。

**与已有模块的降级协同**：`corporate_action_processor` 除权除息事件须被 sleeve 消费——避免除权日把机械持仓调整误判为"价格异动"；`market_event_integrator`（MOD-FEEDBACK_LOOP，production）处理熔断/FOMC/节假日模式切换（不产生 alpha），sleeve 须读其 EMERGENCY 模式——熔断期停止开仓（与 [G18](37_liquidity_crisis_protocol.md) 协同）。

```python
def detect_anomaly(symbol, intraday_returns, benchmark_returns, window=20, corr_threshold=0.0, excess_threshold=0.03):
    """异动识别器（国盛异动雷达施工化）：相关系数<0（脱离同向）+ 超额收益方向显著。window 默认 20 分钟=半小时。"""
    import numpy as np
    # 1. 滚动相关系数
    rolling_corr = np.array([
        np.corrcoef(intraday_returns[i-window:i],
                    benchmark_returns[i-window:i])[0, 1]
        for i in range(window, len(intraday_returns))
    ])
    # 2. 超额收益
    excess_return = np.cumprod(1 + intraday_returns) / np.cumprod(1 + benchmark_returns) - 1
    # 3. 异动判定：相关系数<0 + 超额收益方向显著
    is_anomaly = (rolling_corr[-1] < corr_threshold) and (abs(excess_return[-1]) > excess_threshold)
    anomaly_type = "positive" if excess_return[-1] > 0 else "negative"
    return {
        "is_anomaly": is_anomaly,
        "anomaly_type": anomaly_type,  # positive=异动上涨, negative=异动下跌
        "excess_return": excess_return[-1],
        "rolling_corr": rolling_corr[-1],
    }
```
相关系数<0 判定"个股与基准脱钩"才是真异动（固定涨幅阈值会把大盘联动误判为异动）；国盛实证此方法捕获 78% 重大事件前异动。A 股参数（窗口/阈值/基准）需 G23 回测校准，登记 §5 暂缓项 3。
### 2.5a IPO 虹吸效应量化算法（v1.6.0 新增——施工环节算法补全）
> **缺口背景**：final_report_0724 实证长鑫科技（688825）科创板上市（募资 579-666 亿，科创板史上最大 IPO）可吸金 500 亿+，对存量板块形成"虹吸效应"→上市前完成主仓布局+保留 25% 现金。此前事件分类无 IPO 类、映射无虹吸算法、[37 §3.2](37_liquidity_crisis_protocol.md) 无 IPO 流动性预抽离预警。
**算法 1：IPO 虹吸系数（siphon coefficient）**
```python
def compute_ipo_siphon_coefficient(ipo_event, market_total_volume_20d):
    """IPO 上市日对存量板块的流动性分流系数。Returns: siphon_ratio（募资额/全市场20日均成交额）, siphon_level"""
    raise_amount = ipo_event.raise_amount  # 如长鑫科技 579-666 亿
    market_avg_volume = market_total_volume_20d  # 如 A 股日均 ~27000 亿
    siphon_ratio = raise_amount / market_avg_volume
    # 分级（基于 final_report 实证 + A 股历史 IPO 虹吸案例校准）
    if siphon_ratio < 0.01:
        siphon_level = "NEGLIGIBLE"    # <1% 日均成交额，影响可忽略
    elif siphon_ratio < 0.02:
        siphon_level = "MODERATE"      # 1-2%，局部板块有扰动
    elif siphon_ratio < 0.03:
        siphon_level = "SEVERE"        # 2-3%，全市场流动性显著抽离（长鑫 666/27000≈2.5%）
    else:
        siphon_level = "EXTREME"       # >3%，极端虹吸（历史罕见）
    return siphon_ratio, siphon_level
```
**算法 2：IPO 上市日前后的仓位调整策略**
```python
def ipo_siphon_position_adjustment(ipo_event, current_positions, siphon_level):
    """IPO 虹吸效应驱动的仓位调整（final_report 实证策略）"""
    days_to_listing = (ipo_event.listing_date - today).days

    if siphon_level in ("SEVERE", "EXTREME"):
        if 3 <= days_to_listing <= 5:
            # 上市前 3-5 天：加速建仓窗口
            return ("ACCELERATE_ENTRY", "上市前布局窗口，优先完成主仓位")
        elif 0 < days_to_listing < 3:
            # 上市前 1-2 天：保留现金
            return ("HOLD_CASH", f"保留≥25%现金，{ipo_event.name}上市虹吸备用")
        elif -5 <= days_to_listing <= 0:
            # 上市后 day 0-5：虹吸峰值，存量板块降仓
            return ("REDUCE_EXISTING", "存量板块降仓避险，虹吸峰值期")
        else:
            return ("NORMAL", "虹吸期外，正常操作")
    else:
        return ("NORMAL", "虹吸影响可忽略")
```
**与 [37_liquidity_crisis_protocol §3.2](37_liquidity_crisis_protocol.md) 联动**：IPO 虹吸是**前瞻性**流动性预警（上市日前已知），37 号 §3.2 日频监控新增"IPO 流动性抽离预警"维度（未来 N 日 IPO 募资/成交额比值→提前调仓位上限）。分工：37 号"检测+响应"，26 号"alpha 方向+仓位策略"。
**数据源**：IPO 日历/募资规模来自 `akshare_provider`（`stock_ipo_info`，production，[11_d_data](../../02_domain_architecture_docs/11_d_data.md)）；前 5 日无涨跌幅限制为科创板/创业板规则硬编码。

**进行时案例（v1.9.0，2026-08-11 实盘）**：宇树科技科创板 IPO [网上中签率 0.018% 创历史新低、有效申购 8288 倍](https://cbgc.scol.com.cn/news/7840749)；同周创业板新股上市首日盘中涨 740%；机器人板块 08-11 午后异动——印证 IPO 对存量同题材板块的双向效应（申购期分流+上市前题材预热）。`compute_ipo_siphon_coefficient` 应引入"申购倍数/中签率"作市场关注度代理（募资额固定时申购热度决定实际资金冻结规模），登记 §5 暂缓项 8。
**注意**：虹吸态概念在 [22_sector_rotation_spec §3.1⑤](22_sector_rotation_spec.md) 已存在，但那是**板块间虹吸**（持续性、局部、事后检测）；IPO 虹吸是**事件型、全局性、可预知的**流动性抽离——机制不同。
### 2.5b 地缘/宏观事件→板块受益传导链（v1.6.0 新增——施工环节算法补全）
> **缺口背景**：final_report_0724 核心逻辑"美伊战争→周期资源股（铜/铝/黄金/油气）"的"地缘事件→板块 alpha 方向"映射算法此前缺失；地缘此前仅在 [32](32_firm_risk_aggregator.md)（RMATS 压力测试）和 [10](10_regime_detector_spec.md)（D-SIGNAL-68）作风控节流，非选股 alpha。
**算法：地缘事件→A 股板块受益映射表**
```python
# 地缘事件→受益板块静态映射表（MVP 简单映射，Phase 2 演进为 NLP 动态识别）
GEOPOLITICAL_SECTOR_MAP = {
    "middle_east_conflict": {        # 中东冲突（美伊战争/霍尔木兹海峡/红海危机）
        "beneficiary_sectors": ["油气开采", "油气炼化", "黄金", "军工", "船舶"],
        "victim_sectors": ["航空", "化工(原油成本)", "纺织(原油成本)"],
        "transmission_logic": "地缘冲突→原油/黄金避险溢价→上游资源股受益",
        "rising_half_life_days": "5-15",  # 远长于业绩/并购（见 §2.4 衰减表）
        "empirical_basis": "final_report_0724: 电气设备3日+123亿/有色+144亿断层领先",
    },
    "trade_war_escalation": {         # 贸易战升级（关税/出口管制/实体清单）
        "beneficiary_sectors": ["稀土", "农业(大豆替代)", "半导体(国产替代)", "软件(信创)"],
        "victim_sectors": ["出口导向(家电/纺服)", "苹果产业链"],
        "transmission_logic": "贸易摩擦→国产替代加速+战略资源溢价→自主可控受益",
        "rising_half_life_days": "5-10",
    },
    "currency_depreciation": {        # 人民币贬值
        "beneficiary_sectors": ["出口导向(纺织/家电/机械)", "黄金"],
        "victim_sectors": ["进口导向(航空/造纸)"],
        "transmission_logic": "汇率贬值→出口竞争力提升+外币资产升值",
        "rising_half_life_days": "3-7",
    },
    "commodity_price_surge": {        # 大宗商品价格异动（铜/锂/稀土）
        "beneficiary_sectors": ["有色(对应金属)", "采掘"],
        "victim_sectors": ["下游制造(成本端)"],
        "transmission_logic": "大宗涨价→上游资源股直接受益+下游成本承压",
        "rising_half_life_days": "5-15",
    },
    "tech_sanctions": {               # 科技制裁（芯片/EDA/设备出口限制）
        "beneficiary_sectors": ["半导体(国产替代)", "软件(信创)", "军工"],
        "victim_sectors": ["被制裁企业", "依赖进口技术的企业"],
        "transmission_logic": "技术制裁→国产替代加速+自主可控战略强化",
        "rising_half_life_days": "10-20",  # 国产替代是长期逻辑，持续性最长
    },
}

def map_geopolitical_event_to_sectors(event_nlp_tag, sentiment_score):
    """地缘事件→受益/受害板块映射。event_nlp_tag: NLP 产出的事件标签；sentiment_score ∈ [-1,+1]"""
    mapping = GEOPOLITICAL_SECTOR_MAP.get(event_nlp_tag, {})
    if not mapping:
        return [], [], 0.0
    beneficiary = mapping["beneficiary_sectors"]
    victim = mapping["victim_sectors"]
    rising_hl = int(mapping["rising_half_life_days"].split("-")[0])
    # event_score 用 §2.5 首版公式
    event_score = (
        1.4  # 地缘 event_class_weight
        * (1 if beneficiary else -1)  # surprise_direction: 有受益板块=利好
        * sentiment_score
        * (1.0 if days_since_event <= rising_hl else 0.5)  # decay_stage_factor
        * 1.0  # 地缘事件通常 |reaction|≤3%，extreme_reaction_modifier=1.0
    )
    return beneficiary, victim, event_score
```
**与 NLP 管道协同**（§2.7）：地缘事件多来自海外 RSS（已 production）。NLP 管道须产出 `event_nlp_tag`（映射到 map 的 key）+ `sentiment_score`。首版用**规则匹配**降级（如含"Iran/Israel/Hormuz/红海"→`middle_east_conflict`；"tariff/export ban/entity list"→`trade_war_escalation`），NLP 就绪后升级语义分类。
**2026 研究支撑**：[Sinong Xiao 2026](https://www.atlantis-press.com/proceedings/edms-2026/) A 股资金流→收益四重并行中介模型，牛/熊 regime 传导异质——地缘主线属"结构性 regime 切换"故 rising 远长于离散事件；[arXiv:2607.27063](https://arxiv.org/abs/2607.27063) A 股羊群/动量/反转 agent-based 模型支撑信息扩散→板块传导链；[南京大学 2026 regime-dependent 行业轮动](https://doi.org/10.2991/978-94-6239-699-9_51) 4-regime 分类+regime-dependent risk parity 提供可实施架构。

**与风控层的边界**：地缘事件在本 sleeve 作**选股 alpha**（买受益/卖受损）；在 [32](32_firm_risk_aggregator.md) 作**风控压力测试**（RMATS）；在 [10](10_regime_detector_spec.md) D-SIGNAL-68 作 **regime 节流**。三层正交：alpha 层买方向、风控层测压力、regime 层节流。
### 2.6 换手率（讨论要点⑤）
> 裁定：**继承 20/30 号已定值，convergence_window = 2-3 天**。事件触发不定期，持仓以 rising phase（2-5 天）为主，decay phase 兜底退出。
- convergence_window = 2-3 天（[30 §6.4](30_multi_strategy_concurrency.md)，已定；待首批策略实盘后校准）；BudgetChangeHandler 三级升级（[G14](33_budget_change_handler.md)）：中换手 Tier 1+2 通常 2-3 天自然收敛，Tier 3 兜底防死扛（[30 §2.4](30_multi_strategy_concurrency.md)）；持仓周期 2-10 天（视事件类与衰减阶段，§2.4 衰减表）
### 2.7 news_data 多源情绪接入（讨论要点⑥）
> 裁定：**复用已建多源 news_data + NLP 管道，不新建情绪源**。情绪分数作事件信号的一个维度（冲击方向+强度辅助），非独立 alpha。CAND-AISA-001 待四问评估。

**已建多源 news_data**：东财/财联社/海外 RSS 三源 + `news_collector`→`fund_news_data`（PIT 严格查询）+ `news_dedup` 跨源去重，全部 production（§1.4 盘点，[11_d_data](../../02_domain_architecture_docs/11_d_data.md)）。
**NLP 情感管道（在建，复用）**：
- [#ARCH-NLP-PIPELINE-001](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)：工程范围 `news_collector.py`/`nlp_inference.py`/`sentiment_aggregator.py`，当前为 regime S2 服务（`bad_news_flat ≥ 40`），Phase 0 完成、Phase 1 进行中。**复用裁定**：sleeve 复用同一管道输出——情绪分数作事件信号维度，regime S2 建设"副产物"天然服务事件驱动 alpha，避免重复造轮子
- **能力差距（开放问题）**：regime S2 只需 `bad_news_flat`，事件驱动需**事件类型分类+情绪方向+关联股票**（接近 [Janus-Q](https://arxiv.org/html/2602.19919v2) 10 类+sentiment label）。是否扩展 NLP scope 登记为开放问题（§6-②）

**2026 实证支撑 NLP 复用裁定**：
- **PEAD.txt 文本>数值**（§2.4 已引）：文本 SUE 漂移 2 倍于数值 PEAD——NLP 文本信号是更优 alpha 来源
- **事件感知情绪因子正交性**：[Event-Aware Sentiment Factors（arXiv 2508.07408）](https://arxiv.org/html/2508.07408v1/)——"rumor/speculation"类是强逆向指标（Sharpe -0.38，IC>0.05），事件因子预测力正交于市场 beta
- **LLM 财报分析+综述**：[Lopez-Lira & Tang 2026](https://marketmaker.cc/en/blog/post/llm-alpha-mining-earnings-calls/) 通用 LLM 评估新闻标题可预测次日收益（~90% 方向命中率，小盘股/负面新闻尤甚）；[FinCall-Surprise（arXiv 2510.03965）](https://arxiv.org/html/2510.03965v1/) 多模态音频语调揭示管理层信心（首版仅文本，多模态远期）；[The New Quant（arXiv 2510.05533）](https://arxiv.org/html/2510.05533v1/) 任务分类法，本管道对应"情绪/事件提取"层
- **跨源情绪集成（v1.9.0）**：[RavenPack × FT 2026-03](https://www.ravenpack.com/research/unlocking-alpha-in-g7-currency-markets-with-financial-times)——两独立新闻源秩相关仅 10-14%（真正交），cross-validated ensemble+tanh 软投票后 IR 0.48→0.81、年化超额 +108bps。**含义**：东财/财联社/RSS 三源异质，`sentiment_aggregator` 落码应采用**跨源一致性投票**而非简单均值——≥2 源同向才输出强 sentiment_score，单源孤证降级弱信号
- **情绪分类≠截面 alpha 独立印证（v1.9.0）**：[Burchi & Regni 2026-07](https://www.tandfonline.com/doi/full/10.1080/23322039.2026.2703376)——情绪方向准确率近随机但捕捉大幅波动改善风险调整收益，与 QLoRA 负结果互证：情绪信号价值在**事件方向触发+波动捕捉**，不在截面排序

> **⚠️ QLoRA LLM 情绪 OOS 经济性弱警示（v1.5.0，反平衡）**：[QLoRA Benchmark（arXiv:2608.04200, 2026-08-04）](https://arxiv.org/html/2608.04200v1)——QLoRA 微调分类 F1 高达 0.88，但 OOS 截面选股 rank IC 最大仅 0.0143，28 组合 FDR 校正后**无统计显著**。**核心警示**：语言分类性能 ≠ 收益可预测性，与 [13 号 §2.1 P1-E3 NLP 定位调整](13_regime_phase3_engineering_plan.md)一致——sentiment_score 定位为：①事件触发器（事件类型+方向三分类）②regime 文本交叉验证器（HMM 候选→LLM 确认，F1=0.82）③PEAD.txt 文本惊喜（事件级文本信号，与截面排序负结果正交）。**施工启示**：sentiment_score 不进 event_score 截面排序权重，作事件方向判定+regime 确认。登记 §6 待定问题（NLP 信号定位类）。
> **🔧 Hybrid Sentiment "Data Funnel" 双阶段架构（v1.5.2，远期候选）**：[Stübinger & Wöhner, *AI* 2026, 7(4):138](https://www.mdpi.com/2673-2688/7/4/138)——阶段 1 FinBERT 高吞吐筛选（900 万数据点）+ 阶段 2 Gemini 深度验证（事件级信号提取），16 年实证 51.02% 年化/Sharpe 1.06/Sortino 2.61/maxDD 17.29%。双阶段通过"先筛选信号强度、再验证事件语义"分离噪声，将 sentiment_score 从"截面排序"重构为"事件级 alpha 触发"——与本项目 NLP 定位一致。**工程化启示**：#ARCH-NLP-PIPELINE-001 远期可演进双阶段（FinBERT 预筛+Qwen2.5-7B 验证），阶段 2 可输出"事件级文本 SUE"作 PEAD 触发器。登记远期候选，MVP 维持单阶段，实盘 6-12 月后评估。

**CAND-AISA-001 AI 舆情分析器（candidate，待四问评估）**：数据流 新闻/公告/研报→AI 舆情分析→舆情分数信号；开放风险"若 TRAPE AI 可替代则建模块属过度工程"。**裁定**：首版**不自建独立 AI 舆情模块**——复用 #ARCH-NLP-PIPELINE-001 + `market_sentiment_analyzer`（BM-SEL-03-A）。四问评估留 [G28](61_lifecycle_multi_ai.md) 统一裁定。

> **设计注记：情绪信号非对称使用口径（2026-08 机构实证）**：负面情绪是下跌强预警（→风险预警/减仓规避），正面情绪与上涨关系弱——不构建多头信号；sleeve 内择时边界不变。出处：东吴金工 2026-01《AI 重塑量化》（调研纪要情绪因子空头端年化超额 8.26%，与量价/基本面低相关）；华泰 LLM-FADT 同向。
## 3. 考虑过的替代方案
### 3.1 自建独立事件数据源与选股 pipeline —— 拒绝
多源 news_data 已 production、`news_collector` 已建、NLP 管道在建、BM-SEL-19 已 design——自建=重复造轮子，违反"派生产物复用"与 charter 约束五少而精。**处置**：复用全部已有基础设施，只新建"异动识别器"（§2.5）与"事件影响评分"（首版简化版）两个 sleeve 内部组件。
### 3.2 首版即引入 Hawkes 自激发建模 —— 拒绝（暂缓）
参数估计（μ/α/β+branching ratio）需充分事件样本与校准带宽；经验衰减曲线已承载 rising/decay 纪律；branching ratio 监控更适合 firm 层（G17/G18）非 sleeve alpha。**处置**：登记暂缓前沿（§5 待裁定-1），首版用经验衰减曲线。
### 3.3 首版即引入 Janus-Q 10 类细分类 + 端到端 LLM 决策 —— 拒绝（暂缓）
[Janus-Q](https://arxiv.org/html/2602.19919v2) 需 62,400 篇标注语料+模型微调，个人+AI 项目无此带宽，首版引入属过度工程。**处置**：六类粗分类+情绪分数承载；Janus-Q 范式登记增强方向（§5 待裁定-2）。
### 3.4 事件做空信号开空仓 —— 拒绝（A 股约束）
A 股不能做空，利空事件（业绩暴雷/ST）只能"剔除已有持仓/回避入池"。**处置**：利空事件→剔除/降权；alpha 集中在事件利好方向的多头。
## 4. 上限定义
### 4.1 sleeve 规模上限
- 1 个事件驱动 StrategyBook（[MOD-POS-020](../../../03_modules/_domain_position/strategy_book/blueprint.md)），独立 PnL 归因/风控参数/资金预算；容量中等（介于打板小与多因子大之间，具体测算待 G23 回测校准）
- 与打板、多因子并列，受 firm 层 FirmRiskAggregator（[MOD-POS-021](../../../03_modules/_domain_position/firm_risk_aggregator/blueprint.md)）求和+裁剪
### 4.2 演进路径
- **第一阶段（立即施工）**：复用已建多源 news_data + 经验衰减曲线 + BM-SEL-19 漏斗（待开通）。NLP 管道就绪后接入情绪分数维度
- **第二阶段（3-6 月实盘 PnL 后）**：上叠 RegimeMetaAllocator（[MOD-PA-007](../../../03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md)）按 PerformanceScore × Shrinkage 动态调资金占比（[30 §4.2](30_multi_strategy_concurrency.md)）
- **第三阶段（前沿增强，暂缓）**：Hawkes / Janus-Q 细分类（§5 待裁定-1/2）
### 4.3 为何这是上限而非妥协
- 事件源四类已覆盖 A 股主要事件维度，多于四类稀释 NLP 标注带宽；复用而非自建——sleeve 边界清晰（事件→候选→评分→注入漏斗），不向数据源层与漏斗层蔓延
- 与打板相关性风险是真实约束——若 G07 实测相关性 >0.6，需重审 sleeve 组合（[20 §2.5](20_first_batch_strategies.md)）

> **过度工程审查回执（v1.9.2，判定基准=[system_charter §2](../04_architecture_principles_decisions/system_charter.md)）**：✅ 已施工审查通过——①多源 news_data 不过重（三源为 production 存量设施，RavenPack 实证跨源集成 IR 0.48→0.81，多源是 alpha 来源；反向边界：再新增社交源微博/雪球/股吧属过重不扩源）；②Hawkes 当前形态不过重（经验衰减承载 sleeve 层，Hawkes 留 firm 层风控；首版引入 sleeve alpha 层则过重，自 v1.0.0 起拒绝持续成立）；③Janus-Q/CNN 视觉/LLM 动态图谱/Data Funnel 全部显式暂缓/远期，按"远期工程不算过度工程"规则保留。
## 5. 待裁定（暂缓）
> 以下项目暂不施工，非永久禁止。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 | 责任方 |
|---|---|---|---|
| 1. Hawkes 自激发事件冲击建模 | 经验衰减+极端反应修正已承载 rising/decay 纪律；参数估计需校准带宽，branching ratio 监控更适合 firm 层。MDPI 2026-08 图熵提前 7-12 天预警强化留给风控层 | sleeve 有 3 月 track record + 事件样本充分（>1000）+ G17/G18 评估需要事件聚类监控 | G10 sleeve owner + G17/G18 |
| 2. Janus-Q 10 类细分类 + 端到端 LLM 决策 | 需 62,400 篇标注语料+微调，无此带宽；首版六类粗分类+情绪分数已承载 | NLP 管道成熟 + 标注带宽获得（如 TRAPE AI 运行时自动标注） | G10 sleeve owner + G28 |
| 3. 异动识别器算法定型 | 国盛异动雷达方法已实证有效，A 股参数（窗口/阈值/基准）需 G23 回测校准 | G23 回测框架对接就绪 + 历史异动样本可回测 | G10 + G23 |
| 4. 事件衰减曲线参数按事件类校准 | 初拟半衰期表（§2.4）需实盘/回测验证；衰减速度 regime-dependent 需后验 | sleeve 有 3 月 track record + PerformanceScore 分 regime 校准 | G10 + G07 |
| 5. 极端反应反转（PEAD Inversion）A 股适配 | Vortex 2026-05 基于 mega-cap US tech，A 股大小盘信息扩散不同需验证；3% 阈值可能不适配 | G23 回测 + A 股历史事件样本（业绩公告日 reaction 分布）可回测 | G10 + G23 |
| 6. LLM 增强动态知识图谱 + 社区传播 | arXiv 2607.10932 CIS/PIS 因子优于纯情绪/直接事件，但需 LLM 事件抽取+动态图谱+社区检测基础设施，首版无此带宽 | BM-SEL-11 就绪 + NLP 管道成熟 + 标注带宽 | G10 + G06（BM-SEL-11）|
| 7. CNN 可视化盈余 PEAD 预测 | [Garfinkel/Hribar/Hsiao 2024](https://www.biz.uiowa.edu/faculty/jgarfinkel/working/CNN.pdf) 盈余转柱状图 CNN 提取漂移特征，OOS 优于传统 PEAD 预测器；需 GPU 推理+图像化预处理，首版过重 | G23 就绪 + GPU 资源 + 双因子基线验证后评估增量 | G10 + G23 |
| 8. IPO 虹吸系数引入申购热度代理变量（v1.9.0） | §2.5a 当前仅用募资额/成交额；宇树案例（中签率 0.018%/申购 8288 倍）显示申购热度决定实际资金冻结规模。数据源（申购倍数/中签率）需 akshare 新股申购接口验证可得性 | IPO 数据接口字段核实 + 首个大型 IPO 实盘复盘后 | G10 sleeve owner |
## 6. 待定问题
| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| 事件驱动与打板相关性实测（施工前必做） | [20 §2.5](20_first_batch_strategies.md) / [30 §6.2](30_multi_strategy_concurrency.md) / [G07](23_strategy_correlation_validation.md) | 待 G07 执行；若 >0.6 需重审 sleeve 组合 |
| NLP 管道 scope 扩展（regime S2 `bad_news_flat` → 事件类型分类+情绪方向+关联股票） | 本讨论 §2.7 | 待 #ARCH-NLP-PIPELINE-001 Phase 1 完成后评估；若需扩展可登记新 ARCH |
| CAND-AISA-001 四问评估（自建 AI 舆情模块 vs 依赖 TRAPE AI 运行时） | 候选库 CAND-AISA-001 | 待 [G28](61_lifecycle_multi_ai.md) 统一裁定 |
| BM-SEL-19 开通条件就绪时序（事件数据源+知识图谱+NLP） | 漏斗 6 件套③（[battle_map_05](../battle_map/battle_map_05_stock_selection.md)） | 待 #ARCH-NLP-PIPELINE-001 + [G06 知识图谱/因果推演](22_sector_rotation_spec.md)（BM-SEL-11）就绪 |
| 事件驱动容量精确测算 | [20 §2.4](20_first_batch_strategies.md) | 待 G23 回测后校准 |
| convergence_window 实盘校准（事件 2-3 天） | [30 §6.4](30_multi_strategy_concurrency.md) / [G14](33_budget_change_handler.md) | 待首批策略实盘后校准 |
| 事件驱动六因子矩阵权重校准（dReport/Jump on PEAD/隔夜趋势接入） | §2.4 | 待 G10 校准，dReport 与 Jump on PEAD 优先级最高（有 10 年/5 日实证） |
| 龙虎榜 2026 机构信号失效校准参数实盘复核 | §2.2/§2.5（v1.8.0 与 24 号 v1.8.2 同步） | 待首批策略实盘 3-6 月后用本项目持仓数据重新校准——机构净买入佐证降权系数/净买率 12% 硬阈值/量化席位双阈值，与 23-A 校准口径一致 |
| **20 号 §2.4 事件分类表述同步（四类→六类）** | 本备忘 §2.3 v1.6.0 已升级为六类（+IPO/再融资+地缘/宏观），但 [20 §2.4](20_first_batch_strategies.md) 仍写四类——跨文档版本漂移（v1.9.0 审查发现） | 待 20 号 owner 下次修订时同步为"六类（业绩/并购/政策/突发/IPO/地缘，详见 26 号 §2.3）"。按审查约束不越界改 20 号，登记于此 |
| **`sentiment_aggregator.py` 落盘时序** | §1.4 盘点：`src/zephyr/nlp/` 当前仅 `nlp_inference.py` + `__init__.py` | 待 #ARCH-NLP-PIPELINE-001 Phase 1 完成；就绪前 sentiment_score 用单条推理输出降级（§2.7 已裁定非截面排序用途，不阻塞） |
| **30 号 §2.4 引 "[20 §6.4]" 为失效锚点** | v1.9.2 第 6 轮一致性审查发现：[30_multi_strategy_concurrency §2.4](30_multi_strategy_concurrency.md) L227 引"打板高换手 1-2 天自然收敛，[20 §6.4]"，但 20 号无 §6.4 节（convergence_window 真源在 20 号 §2.2-2.4 各节"换手率特征"行 + 30 号 §6.4 自身） | 待 30 号 owner 修正锚点（建议改引 20 号 §2.2 或自引 §6.4）。按审查约束不越界改 30 号，登记于此 |
## 7. 引用
### 7.1 相关设计备忘
- [20_first_batch_strategies.md](20_first_batch_strategies.md) §2.4（事件驱动 sleeve 定义，上游裁定）/ [00_index_trading_decision.md](00_index_trading_decision.md) §3 G10（路线图）
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md)（Model A 总纲）/ [23_strategy_correlation_validation.md](23_strategy_correlation_validation.md)（G07 相关性验证，施工前必做）
- [22_sector_rotation_spec.md](22_sector_rotation_spec.md)（G06 板块轮动，事件传导链映射）/ [33_budget_change_handler.md](33_budget_change_handler.md)（G14 三级升级，convergence_window）
- [36_var_es_monitoring.md](36_var_es_monitoring.md) / [37_liquidity_crisis_protocol.md](37_liquidity_crisis_protocol.md)（G17/G18 风控，Hawkes branching ratio 监控候选消费者）/ [61_lifecycle_multi_ai.md](61_lifecycle_multi_ai.md)（G28，CAND-AISA-001 归属）
### 7.2 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)（选股阶段）——BM-SEL-27 盘中实时事件处理（生产态，sleeve 依赖）；BM-SEL-19 事件驱动分布筛选（设计态，MOD-SIG-049，漏斗第四层）；BM-SEL-11 知识图谱与因果推演（设计态，传导链）
- 同图生产态复用件：BM-SEL-05-A 机构行为分析（龙虎榜数据源）；BM-SEL-03-A 市场情绪分析（情绪分数基础）；BM-SEL-05-C 盘中买卖点分析（异动识别基础）
### 7.3 depgraph 模块与 ARCH/CAND
| 模块/议题 | ID | path / 位置 | 本讨论关系 |
|---|---|---|---|
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | sleeve 载体 |
| NewsCollector | MOD-DATA-NEWS-001 | `src/zephyr/data/news_collector.py` | 新闻数据采集（production） |
| CorporateActionProcessor | MOD-TRADING-004 | `src/zephyr/trading/corporate_action_processor.py` | 持仓调整事件（非 alpha，须消费防误判） |
| MarketEventIntegrator | MOD-FEEDBACK_LOOP | `src/zephyr/feedback_loop/collectors/market_event_integrator.py` | 熔断/FOMC 模式切换（EMERGENCY 时停止开仓） |
| NLP 情感管道 | #ARCH-NLP-PIPELINE-001 | `news_collector.py` / `nlp_inference.py` / `sentiment_aggregator.py` | 在建，复用为情绪分数源 |
| AI 舆情分析器（候选） | CAND-AISA-001 | 候选库 | 待四问评估（自建 vs TRAPE AI） |
| 事件漏斗 L4 | MOD-SIG-049 | BM-SEL-19 | 事件影响评分+条件PDF修正+传导链（design） |
> news_data 多源：`rss_provider.py`/`eastmoney_news_provider.py`/`cls_provider.py`/`news_dedup.py` 均 production（[11_d_data](../../02_domain_architecture_docs/11_d_data.md)；v1.9.0 修正：provider 真实登记在 11_d_data D_DATA 域，非 09_d_alt_data）。
### 7.4 开源实证与 2026 行业参考
- 事件分类/衰减：[Janus-Q（arXiv 2026-02）](https://arxiv.org/html/2602.19919v2)（10 类+62,400 篇标注，§2.3/§3.3）；[Yukka 情绪衰减（2026-05）](https://cdn.prod.website-files.com/66b4f3430903efa023fe741b/69fdded32f3d7e02f17ff3f8_Sentiment%20Decay%20&%20Source%20Selection%20in%20Global%20Equity%20Markets%20-%20White%20Paper.pdf)（§2.4）；[Beyond the Event Horizon 2025](https://www.preprints.org/manuscript/202506.0079)（rising RVR 9.5x，§2.4）；[FMP Tracking PEAD（2026-04）](https://intelligence.financialmodelingprep.com/education/other/tracking-postearnings-announcement-drift-with-fmps-market-data)（day 9 平台期，§2.4 业绩衰减窗）
- PEAD Inversion/文本惊喜：[Vortex Capital（2026-05）](https://www.vortexcapitalgroup.com/insights/the-mega-cap-pead-inversion-when-the-reaction-is-the-trade-and-when-it-is-the-trap)（>±3% 反转，§2.4）；[费城联储 PEAD.txt](https://marketmaker.cc/en/blog/post/llm-alpha-mining-earnings-calls/)（文本 SUE 漂移 2 倍，§2.4/§2.7）；[Griffin/McInnis/Zhao 2026 PEAD 衰退根因](https://www.broker-forex.fr/strategie-investissement-PEAD.php)（盈余信息性下降，§2.4）
- Hawkes 簇：[Hawkes for Investors（2026-02）](https://stockalpha.ai/alpha-learning/hawkes-processes-for-investors-modeling-self-exciting-volatility-bursts)；[中国股市传染（arXiv 2512.08000）](https://arxiv.org/html/2512.08000v1/)；[Price Discovery 物理（arXiv 2601.11602）](https://arxiv.org/html/2601.11602v2)；[Persia 金融传染（2026-06）](https://proceedings.systemdynamics.org/2026/papers/P1265.pdf)；[MDPI Entropy 跨境传染（2026-08-06）](https://www.mdpi.com/1099-4300/28/8/887)（图熵提前 7-12 天预警）；[MetricGate 实操指南（2026-06）](https://metricgate.com/blogs/hawkes-self-exciting-process-r/)；[Hawkes-Driven OTC（arXiv 2608.02002）](https://arxiv.org/html/2608.02002v1)（均 §2.4）
- 异动/双因子/架构：[国盛证券异动雷达（2026-03）](http://stock.finance.sina.com.cn/stock/view/paper.php?autocallup=no&isfromsina=no&reportid=826626291912&symbol=sh000001)（年化超额 7.51%/IR 2.48，叠加负向筛选 9.77%/2.92，§2.5）；[Rockstead SUE+EAR 双因子（2026-05）](https://rockstead.com/market-insights/capturing-post-earnings-drift-a-two-factor-approach/)（r=0.004，组合年化 18.50%，EAR Q5-Q1 年化 -3.39%，§2.5）；[NexusFi 五层架构（2026-06）](https://nexusfi.com/a/automation/event-driven-trading-automation)（风控独立于策略，§2.5）；[Closelook Pattern Engine（2026-04）](https://closelook.net/reports/post-earnings-drift/)（三层递进，top/bottom quintile 年化 ~13%，§2.5）
- 知识图谱/NLP：[LLM 动态金融知识图谱（arXiv 2607.10932）](https://arxiv.org/pdf/2607.10932)（CIS/PIS t-stat≈3.7，§2.5）；[Event-Aware Sentiment Factors（arXiv 2508.07408）](https://arxiv.org/html/2508.07408v1/)（rumor 类 Sharpe -0.38，§2.7）；[The New Quant 综述（arXiv 2510.05533）](https://arxiv.org/html/2510.05533v1/)（§2.7）；[FinCall-Surprise 多模态（arXiv 2510.03965）](https://arxiv.org/html/2510.03965v1/)（§2.7 远期）；[QLoRA Benchmark（arXiv:2608.04200）](https://arxiv.org/html/2608.04200v1)（F1 0.88 vs rank IC 0.0143 不显著，§2.7 警示）；[Stübinger & Wöhner Data Funnel（*AI* 2026, 7(4):138）](https://www.mdpi.com/2673-2688/7/4/138)（双阶段 51.02% 年化/Sharpe 1.06，§2.7 远期候选）
- ORJ/预期差：[Bahcivan et al. 2023 隔夜跳空](http://hulusibahcivan.com/wp-content/uploads/2023/05/New-Avenues-in-Expected-Returns_Investor-Overreaction-and-Overnight-Price-Jumps-in-US-Stock-Markets_May-2023.pdf)（9,718 只美股，跳空后 5 日反转，§2.5）；[中国证券报 净利润断层（2026-04-24）](http://m.ce.cn/cj/gd/202604/t20260424_2925768.shtml)（§2.5）；[中邮证券 业绩之锚7（2026-06-05）](https://finance.sina.com.cn/stock/stockzmt/2026-06-05/doc-iniaikau2934869.shtml)（一季报 30 天超额 1.9%/60 天 2.8%，年报不定价利好，§2.5）；[EarningsWhispers Whisper Number（2026-08-05）](https://beta.earningswhispers.com/about-whispers)（准确率 +69.7%，whisper>consensus 5% 时 beat 概率 ~75%，§2.5）；[火山引擎 夜盘回测（2026-04-16）](https://developer.volcengine.com/articles/7629162484989394995)（准确率 54.7%/反转>45%，宏观事件 >65%，§2.5）
- 其他：[Garfinkel/Hribar/Hsiao CNN 可视化盈余（2024）](https://www.biz.uiowa.edu/faculty/jgarfinkel/working/CNN.pdf)（§5 暂缓项 7）；[BlackRock Hedge Fund Outlook Spring 2026](https://alternativefundinsight.com/wp-content/uploads/2026/04/blk-hedge-fund-outlook.pdf)（M&A volume +54% YoY，§1.1 时代背景）；[澎湃新闻 十大券商看后市（2026-08-10）](https://m.thepaper.cn/newsDetail_forward_33750320)（§1.1 市场背景）
## 8. 修订记录
| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G10 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active | G10 六项讨论要点逐项定型：①事件源（复用公告/新闻/龙虎榜/异动四类已建源）②事件分类（四类粗分类+Janus-Q细分类暂缓）③冲击衰减曲线（经验衰减+Hawkes暂缓）④事件→选股映射（复用 BM-SEL-19 漏斗+异动识别器新建）⑤换手率（继承 2-3 天）⑥多源情绪（复用已建 news_data+#ARCH-NLP-PIPELINE-001，CAND-AISA-001 待评估）。登记 4 项暂缓+6 项开放问题 |
| 2026-08-10 | 1.1.0 | 施工算法补全+2026最新实证 | ①§2.4 新增极端反应反转（PEAD Inversion）修正（Vortex 2026-05）+衰减曲线双模型（温和延续/极端反转）+PEAD.txt 文本惊喜（费城联储）②§2.4 新增 MDPI Hawkes 跨境传染+MetricGate 实操③§2.5 新增显式事件影响评分公式+进出场触发算法（三道出场线）+LLM动态知识图谱（arXiv 2607.10932）+Closelook对标④§2.7 新增事件感知情绪因子正交性+LLM财报分析+多模态+综述⑤§7.4 新增10条参考。暂缓项4→6项 |
| 2026-08-10 | 1.2.0 | 双因子评分+确认型入场+五层架构+8月实证 | ①§2.5 SUE+EAR 双因子（Rockstead r=0.004，年化18.50%）——单因子保留默认，业绩类优先双因子；升级路径 SUE→PEAD.txt②确认型入场（NexusFi 三模式）补 should_enter 第三分支③五层架构映射+风控独立纪律④§2.4 Hawkes-Driven OTC（arXiv 2608.02002）⑤§1.1 A股2026-08市场背景⑥§5 暂缓项6→7（CNN可视化盈余）⑦§7.4 新增7条参考 |
| 2026-08-10 | 1.3.0 | ORJ隔夜跳空+预期差+三因子融合 | ①§2.5 ORJ（Bahcivan 2023，9,718只美股跳空后5日反转）；A股T+1天然隔夜窗口，与日内EAR正交②净利润断层（A股本土化ORJ，中国证券报2026-04）③预期差+修正动量（Whisper Number本土化：EarningsWhispers准确率+69.7%；中邮证券业绩之锚7：一季报30天超额1.9%/60天2.8%，年报降权）④三因子融合（SUE×EAR×ORJ+预期差增强）⑤ORJ与PEAD Inversion协同（ORJ>3%触发反转，比3日EAR更早）⑥§7.4 新增5条参考 |
| 2026-08-10 | 1.4.0 | SUE 预期构建方式选项之外更好算法 | §2.5 新增 Zyberno 2026-08-05 seasonal random walk with drift SUE——从 SEC 实际报告构建预期，无法被 guidance management 扭曲。与 consensus_eps 五维对比。裁定：MVP 保留 consensus_eps，Zyberno 记 Phase 2 候选（小盘无覆盖标的+交叉验证：同向→增强/背离→guidance management 风险信号） |
| 2026-08-10 | 1.5.0 | 施工算法补全 + 六因子矩阵 + 异动识别器 + 吸收卖压 | §2.5 补六因子矩阵交叉引用（dReport/Jump on PEAD/隔夜趋势/AStockEvent，对齐 20 §2.4 v1.4.4）；§2.5 补异动识别器施工算法（相关系数<0+超额方向，国盛异动雷达施工化）；§2.4 补吸收卖压判定算法（CVD转正+量能放大+价格企稳，PEAD Inversion 极端负反应 day2-3 确认施工落地） |
| 2026-08-10 | 1.5.1 | QLoRA LLM 情绪 OOS 经济性弱警示 | §2.7 补 QLoRA Benchmark（arXiv:2608.04200）：分类 F1 0.88 但 OOS rank IC 仅 0.0143 不显著。"语言分类性能≠收益可预测性"，sentiment_score 定位为事件方向触发+regime 文本交叉验证（与 13 号 P1-E3 定位调整闭合） |
| 2026-08-10 | 1.5.2 | Hybrid Sentiment Data Funnel 双阶段架构 | §2.7 补 Stübinger & Wöhner（*AI* 2026, 7(4):138）——FinBERT 筛选+Gemini 验证双阶段，16 年实证 51.02% 年化/Sharpe 1.06。与 QLoRA 负结果互补：双阶段"先筛选信号强度、再验证事件语义"分离噪声，将 sentiment_score 重构为"事件级 alpha 触发"。登记远期候选 |
| 2026-08-10 | 1.6.0 | IPO虹吸效应+地缘事件传导链+事件分类四类→六类 | ①§2.3 四类→六类（+IPO/再融资+地缘/宏观）——final_report_0724 交叉对照发现算法缺失；②§2.4 衰减表补 IPO（上市前3-5天布局/上市后day1-5虹吸）和地缘（rising 5-15天）；③§2.5 event_class_weight 补 IPO=1.3/地缘=1.4；④新增 §2.5a IPO 虹吸量化算法（siphon coefficient+仓位调整，与 37 §3.2 联动）；⑤新增 §2.5b 地缘→板块传导链（5类地缘事件映射表+NLP协同+三层正交边界）；⑥§2.7 引 Sinong Xiao 2026+arXiv:2607.27063+南京大学 regime-dependent 轮动 |
| 2026-08-10 | 1.7.0 | 施工算法补全：should_enter/should_exit 被调用未定义的 5 项辅助函数与数据结构 | 审计发现三个进出场函数调用 5 项辅助函数/数据结构未定义，补全后施工闭环：①event_score_single_factor（首版内联公式封装）②compute_event_score（调度器：业绩类双因子/其他五类单因子）③decay_exit_window（§2.4 衰减表程序化，6类 rising+decay 总长）④has_contradictory_event（event_store 近5日反向事件）⑤has_volume_confirmation（量比≥1.5倍20日均量，NexusFi confirmation 施工化）。补全后所有被调用符号均有定义 |
| 2026-08-10 | 1.7.1 | event_score_dual_factor 裸变量修复 | 第五十五轮审查。`event_score_dual_factor` L237 裸变量 `actual_eps`/`consensus_eps` 未在函数签名内定义（v1.2.0 遗留伪代码精度缺陷），统一为 `event.actual_eps` + `wind_consensus_eps(event.symbol, event.date)`，与三因子版+预期差函数口径一致，消除双轨歧义 |
| 2026-08-10 | 1.8.0 | **龙虎榜 2026 机构信号失效校准（与 24 号 v1.8.2 同步）** | 24 号 v1.8.2 实证机构净买入次日胜率 62-68%→45.7%（<50%随机，反向失效），要求 26 号 event_score 同步校准。补：①§2.2 失效提示；②§2.5 校准块——4维退化表+4项施工建议（佐证降权/净买率12%硬阈值/席位类型差异化/数据源）+`dragon_tiger_corroboration_modifier()`（∈[0.7,1.2]，净买率≥12%加分/量化席位 hard×0.7 soft×0.85）+与24号口径一致性（共用 dragon_tiger 表+12%阈值+detect_quant_seat_warning）；③§6 新增待定问题（校准参数实盘复核） |
| 2026-08-12 | 1.9.0 | **已施工设施盘点节新增 + 交叉引用真源修正（通用规则 #11 审查）** | 架构审查第1-2轮：①新增 §1.4 已施工设施盘点——14项设施逐项核对代码/schema/tasks.yaml 真源，结论：四类事件源数据链路全部 production，待新建仅异动识别器+事件影响评分两项；②交叉引用修正：§2.2/§2.5a/§2.7/§7.3 共4处误引 09_d_alt_data→改引 11_d_data；③§2.5 龙虎榜数据源精确化（双表，席位类型字段在 seat 表）；④同名消歧：backtest/event_driven_engine.py 是 Tick 级回测内核（做T专用）勿混淆；⑤§6 新增2项开放问题（20号四类→六类漂移+sentiment_aggregator 未落盘） |
| 2026-08-12 | 1.9.1 | **缺失环节审查补全 + 2026-08-10/11 最新研究（第 3-4 轮）** | ①§1.3 T+1 事件→交易时序显式映射（盘后事件T→T+1开盘→T+2可卖；盘中事件当日买入不可卖；holding_days 计数约定；rising 窗口折损一日）收拢为单点声明；②§2.5 接口契约精确化——event_store/volume_series/volume_ma/trading_days_ago 全仓扫描无已定义函数（gov_audit EventStore 勿混用），落码路径明确（fund_news_data+pit_query+交易日历，工程量<1天）；③§2.7 跨源情绪集成（RavenPack×FT：秩相关10-14%，tanh软投票 IR 0.48→0.81——≥2源同向才出强信号）+Burchi&Regni 2026-07 独立印证；④§2.5a 宇树科技案例（中签率0.018%/8288倍）+§5 暂缓项8（申购热度代理变量） |
| 2026-08-12 | 1.9.2 | **过度工程审查回执（第 5 轮）** | §4.3 新增审查回执：①多源 news_data 不过重（production 存量非新增负担，RavenPack 实证多源是 alpha 来源；反向边界：社交源不扩）；②Hawkes 当前形态不过重（经验衰减承载，留 firm 层风控）；③Janus-Q/CNN/LLM图谱/Data Funnel 全部显式暂缓/远期，按规则保留 |
| 2026-08-12 | 1.9.3 | **一致性与交叉引用审查 + 文档质量复核（第 6-7 轮）** | 第6轮：与20号（§2.1六维对齐✅，四类→六类漂移已登记）、30号（convergence_window锚点✅，反引"[20 §6.4]"失效已登记）、23号G07闭环✅、62号（strategy_registry 6类含event_driven✅、UNI-RULE-002引本备忘✅）、§7.3 blueprint链接逐一验证✅。第7轮：frontmatter受控词表✅、八段齐全✅、硬约束✅、交叉引用全稳定相对path✅ |
| 2026-08-12 | 1.9.4 | **确认轮内部锚点审计修复** | 循环自检发现3类内部引用失效并修复：①"§6 待裁定-N"×7处误指——暂缓项真源在 §5，§6 为待定问题，replace_all 修正；②"§3.6 漏斗③"裸写悬空——真源为21号§3.6，补全链接；③v1.6.0 四类→六类升级三处残留统一为六类 |
| 2026-08-12 | 1.9.5 | **确认轮 C：页内锚点加固** | 零发现确认轮中2处渲染器脆弱页内锚点（#23-...② / #25-...④，GitHub/CommonMark 剥离特殊字符致失效）改为稳健文字引用（"§2.3 细分类预留"/"§2.5 龙虎榜 2026 机构信号失效校准块"）；校正 §2.4 六因子块版本标注（v1.9.3→v1.9.4 修正） |
| 2026-08-14 | 1.9.6 | 压缩精简：噪音去除+施工细节梳理，零信息丢失审查通过（AI-DOCS-001） | 文档压缩：折叠过程性叙述/研发过程/重复解释——§2.5 六因子矩阵重复块改交叉引用 §2.4、§2.7 数据源表改引 §1.4、§7.4 参考按主题合并分组、代码 docstring 去冗（全部逻辑/参数/阈值保留）、Hawkes 实证簇与 2026 研究支撑压缩。策略定义/事件分类/参数表全部数值/信号规则/进出场算法/风控约束零丢失，章节编号与锚点不变 |
| 2026-08-15 | 1.9.7 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-06） | 通读两轮零发现——第一轮压缩后本文已收敛：event_class_weight 1.0/1.2/0.8/1.5/1.3/1.4、衰减半衰期表、PEAD Inversion 阈值、进出场算法、待裁定/待定问题全保留，正文零变更 |
| 2026-08-22 | 1.9.8 | §2.7 补设计注记：情绪信号非对称使用口径 | 92 号清单波 1（ALG-04）文档注记——负面情绪是下跌强预警（→风险预警/减仓规避），正面情绪与上涨关系弱，不构建多头信号；sleeve 内择时边界不变。出处：东吴金工 2026-01《AI 重塑量化》（调研纪要情绪因子空头端年化超额 8.26%，与量价/基本面低相关）；华泰 LLM-FADT 同向。与 28 号 v1.2.4 §3.4 同款注记同步，无算法变更 |

---

## 附录：数据资产消费登记（63 号审查批次 B+C，2026-08-20 登记）

> 来源：[63_data_utilization_audit](63_data_utilization_audit.md) §6.2 批次 B（事件驱动/策略模块）+ 批次 C（概念分类行）/ §7.2 第二波——消费层文档覆盖缺口施工。登记口径：每表 3-5 行（表名/内容/潜在消费场景/当前状态）；按收缩方案合并为本节表格汇总。当前状态统一为**未消费登记**（unconsumed registration）：数据已落库、代码层或有引用，但本消费方文档尚未将其作为显式数据源描述；后续实际消费接线后，按 63 号 §7.0.1 六字段模板改写为正文小节并更新状态。引用计数为 2026-08-20 工作区复扫（src/zephyr *.py，词边界匹配）。

| 表名 | 内容 | 潜在消费场景 | 当前状态 |
|---|---|---|---|
| `convertible_bond_iv`（可转债隐含波动率，63 号简写 `cb_iv`） | 可转债 IV（implied volatility，隐含波动率）曲面/点位 | 可转债事件 sleeve 定价参考：IV 低位+正股事件催化→转债弹性机会（90 号 §18 可转债 P1 待验证） | **未消费登记**（2026-08-20 实证：src/zephyr 引用 3 次（miniqmt_provider.py，按实际表名复扫），代码活跃；消费语义未落本文档） |
| `convertible_bond_list`（可转债标的池） | 存量可转债清单（代码/正股/转股价/到期日） | 可转债事件 sleeve 标的池基础表：正股事件→转债映射查询 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 6 次，代码活跃；消费语义未落本文档） |
| `calendar_event`（事件日历） | 市场级事件日历（议息/宏观发布/重要日期） | 事件驱动时间轴锚点：事件前后窗口的进出场规则（§2.4 衰减表事件日对齐）；与 10 号 regime 事件日历消费语义互补 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 18 次（manual_calendar_events/internal_compute_provider/regime_cycle_analyzer），代码活跃；消费语义未落本文档） |
| `index_adjustment`（指数调仓） | 指数成分调整事件（调入/调出/生效日） | 指数调仓事件 sleeve：调入股被动买入/调出股被动卖出的事件套利窗口 | **未消费登记·待 Q8 裁定**（2026-08-20 实证：src/zephyr 零命中，与 63 号 §10.2 Q8"代码零引用但规划已登记"口径一致；仅 schemas DDL/采集配置在位；Q8 裁定 dormant 则转"待启用"） |
| `ipo_schedule`（IPO 日程） | 新股发行日程（申购日/上市日/募资额） | IPO 事件 sleeve + 流动性抽离预警联动（37 号 §3.2a 已建 ipo_calendar 管道，本表为日程维度补充） | **未消费登记·待 Q8 裁定**（同上一行口径：src/zephyr 零命中，Q8 待裁定） |
| `share_change`（股本变动） | 个股股本变动记录（增发/送转/拆并股） | 股本变动事件：送转填权/增发摊薄事件驱动信号（akshare_provider 已有采集引用） | **未消费登记**（2026-08-20 实证：src/zephyr 引用 5 次（akshare_provider.py），代码活跃；消费语义未落本文档） |
| `rights_issue`（配股） | 配股公告与配股方案明细 | 配股事件：配股除权前后的价格压制/填权行情事件信号 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 4 次（akshare_provider.py），代码活跃；消费语义未落本文档） |
| `equity_pledge_detail`（股权质押明细） | 股东股权质押逐笔明细（质押方/比例/预警线） | 质押风险事件：高质押比例+股价临预警线→强平抛压事件预警 | **未消费登记·待 Q8 裁定**（2026-08-20 实证：src/zephyr 零命中；known_data_gaps.yaml/tasks.yaml/schemas DDL 在位——采集配置已声明缺口，消费代码未见，标**待实证**） |
| `margin_target_adjustment`（融资融券标的调整） | 两融标的调入/调出事件 | 两融标的调整事件：调入→杠杆资金可达性提升，调出→强制降杠杆抛压；63 号 §6.2 批次 B 表指派 25 号、§7.2 步骤 1 指派本篇——本篇按事件流语义登记，25 号侧不重复登记（口径差异标**待实证**，随 63 号下一轮统一） | **未消费登记·待 Q8 裁定**（2026-08-20 实证：src/zephyr 零命中，Q8 待裁定） |
| `concept_board`（概念板块） | 概念板块清单（板块代码/名称） | 概念分类事件映射基础表：概念利好事件→成分股筛选（与 `concept_board_constituent` 配对，63 号 §7.0.3 拓扑：被依赖表先补） | **未消费登记**（2026-08-20 实证：src/zephyr 引用 5 次，代码活跃；消费语义未落本文档） |
| `concept_board_constituent`（概念板块成分） | 概念板块—成分股映射 | 概念事件→受益个股落地：概念利好事件驱动 sleeve 的成分股池生成 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 1 次，代码弱活跃（路由映射级）；消费语义未落本文档） |