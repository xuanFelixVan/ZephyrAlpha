---
ttl: permanent
doc_type: architecture_view
title: 事件驱动策略细节
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.9.2"
date: 2026-08-12
topic: event_driven_strategy_detail
scope: 07_trading_decision_architecture
---

# 事件驱动策略细节

> 本备忘定义首批 3 策略之一——事件驱动 sleeve（[20_first_batch_strategies §2.4](20_first_batch_strategies.md) 策略C）的 alpha 信号来源、事件源、事件分类、冲击衰减曲线、事件→选股映射、换手率与多源情绪接入。
> 性质：永久态讨论记录，可随项目演进而修订。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 路线图定位见 [00_index_trading_decision](00_index_trading_decision.md) G10（L1·Alpha 选股层，P2）。

## 1. 背景

### 1.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，T+1 结算，不能做空，涨跌停限制）
- 事件驱动作为首批 3 sleeve 之一（[20_first_batch_strategies §2.4](20_first_batch_strategies.md) 策略C），定位"中换手、中容量、离散事件冲击"
- 多策略并发架构已定稿为 Model A（独立账本 + firm 聚合 + regime 风险节流），见 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md)
- regime 检测器由另一 AI 负责（[10_regime_detector_spec](10_regime_detector_spec.md)），与本主题正交——regime 只做 Shrinkage 风险节流，不参与选股
- **事件类基础设施已大量存在**（见 §3.2）：多源新闻采集（Eastmoney/CLS/RSS，production）、`news_collector`（ClickHouse `fund_news_data`）、NLP 情感管道（[#ARCH-NLP-PIPELINE-001](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 在建）、`corporate_action_processor`（公司行动→持仓调整，production）。本讨论的关键不是"造轮子"，而是"把这些已有基础设施接成一条事件→选股→持仓的 alpha 链"
- **A 股 2026-08 实时市场背景**：2026-08-07 A 股深调（上证 -1.02%/深成指 -1.42%/创业板 -1.35%，科技板块领跌，成交 2.66 万亿恐慌出逃），2026-08-10 十大券商共识"超跌反弹仍有演绎空间，8 月中下旬中报密集期是检验反弹成色的窗口"（[澎湃新闻 2026-08-10](https://m.thepaper.cn/newsDetail_forward_33750320)）。华泰证券判断小盘弹性显著强于大盘，锚定中报均衡配置。**对事件驱动 sleeve 的含义**：①8 月中下旬中报密集期=业绩类事件高发期，事件驱动 alpha 机会窗口即将打开；②超跌反弹阶段前期跌幅越大弹性越大（有色/化工/非银/电新年内收益率低于理论中枢），事件利好催化易触发反弹延续；③科技板块拥挤度未回落+融资盘出清半程，事件利空仍需警惕——支撑 §2.4 极端反应反转修正与 §2.5 EMERGENCY 模式协同

### 1.2 核心问题
事件驱动 sleeve 的 alpha 来自离散事件冲击。需逐项对齐 G10 六个讨论要点：①事件源 ②事件分类 ③事件冲击衰减曲线 ④事件信号→选股映射 ⑤换手率 ⑥多源 news_data 情绪接入。核心张力是：A 股事件信息扩散慢、情绪驱动强、T+1 不能日内翻转，且事件驱动与打板都受情绪周期隐形驱动（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)），两者相关性可能高于直觉——这是 [G07](23_strategy_correlation_validation.md) 施工前必测项。

### 1.3 约束条件
- A 股不能做空 → 事件做空信号（如利空事件）只能用于"剔除/回避"，不能开空仓；alpha 集中在事件利好方向的多头
- T+1 结算 → 盘中突发事件的实时感知与次日开盘反应之间存在时滞，事件冲击的"实时"是相对的。**T+1 事件→交易时序显式映射**（v1.9.0 收拢，散见各节的 T+1 约束单点声明）：①盘后事件（业绩公告/政策，T 日 15:00 后披露）→ T+1 日开盘才能行动（ORJ 即此窗口的市场第一反应）→ 买入仓最早 T+2 日可卖；②盘中事件（T 日交易时段突发）→ 当日可买但买入仓当日**不可卖**——`should_exit` 的 `holding_days >= 1` 条件（EXTREME_REACTION 线）已隐含此约束，即极端反转退出最早也要买入次日；③`holding_days` 计数约定：买入当日 = 0（T+1 不可卖），买入次日 = 1（可卖起点）；④衰减表的"day 0-5 rising phase"对盘后事件实际可捕捉窗口是 day 1-5（day 0 收盘才知情），rising 半衰期利用率天然折损一日——§2.4 各事件类 rising 半衰期含此折损，不再另调
- 事件冲击衰减快（rising phase day 0-5，decay phase day 6-15，[Beyond the Event Horizon 2025](https://www.preprints.org/manuscript/202506.0079)）→ 持仓以 rising phase 为主，T+1 下需提前布局退出
- 情绪周期是隐形驱动 → 事件驱动与打板相关性风险（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）
- AI 开发 → 故障隔离与归因清晰度是生存项；事件链路长（数据源→分类→情绪→衰减→选股），任一环节失效须可降级不阻塞

### 1.4 已施工设施盘点（通用规则 #11，2026-08-12 代码侧真源审计）

> 本节盘点与本主题相关的全部已建设施（代码/schema/调度任务真源），作为 §2"复用而非新建"裁定的事实基座。✅=已落盘可消费，🟧=在建未落盘，⚠️=同名消歧。

| 设施 | 真源路径 / 表 | 状态 | 本备忘消费点 |
|---|---|---|---|
| 东方财富新闻源 | `src/zephyr/data/implementations/eastmoney_news_provider.py` | ✅ production（[11_d_data](../../02_domain_architecture_docs/11_d_data.md)） | §2.2 新闻事件源 |
| 财联社快讯源 | `src/zephyr/data/implementations/cls_provider.py` | ✅ production（同上） | §2.2 新闻事件源 |
| 海外 RSS 源 | `src/zephyr/data/implementations/rss_provider.py`（BBC/CNBC/NYT/Guardian/Bloomberg） | ✅ production（同上） | §2.2 新闻事件源 / §2.5b 地缘事件源 |
| 新闻采集器 | `src/zephyr/data/news_collector.py`（MOD-DATA-NEWS-001）→ ClickHouse `fund_news_data` 表 | ✅ production（11_d_data 标注"P1-E3 NLP 管道 Phase 1"） | §2.7 情绪数据基座 |
| 跨源去重 | `src/zephyr/data/news_dedup.py` | ✅ production | §2.7 标准化层 |
| 龙虎榜双表 | `c1_market.dragon_tiger` + `c1_market.dragon_tiger_seat`（AKShare `stock_lhb_detail_em` / `stock_lhb_stock_detail_em`，tasks.yaml `dragon_tiger_incremental` / `dragon_tiger_seat_incremental` 盘后调度） | ✅ production | §2.2 龙虎榜事件源 / §2.5 席位类型差异化校准（**席位类型字段在 `dragon_tiger_seat` 表**，Top5 买卖席位合并去重） |
| 公司行动处理 | `src/zephyr/trading/corporate_action_processor.py`（MOD-TRADING-004） | ✅ production | §2.2 除权日防误异动（非 alpha 源） |
| 熔断模式集成 | `src/zephyr/feedback_loop/collectors/market_event_integrator.py`（`MarketMode.EMERGENCY` 已确认落码） | ✅ production | §2.5 熔断期停止开仓 |
| 盘中买卖点分析 | `src/zephyr/signal_ashare/intraday_buy_sell_point_analyzer.py`（BM-SEL-05-C） | ✅ production | §2.5 异动识别复用基础 |
| 市场情绪分析 | `src/zephyr/signal_ashare/market_sentiment_analyzer.py`（BM-SEL-03-A） | ✅ production | §2.7 情绪分数基础 |
| NLP 推理 | `src/zephyr/nlp/nlp_inference.py`（Qwen2.5-7B） | ✅ 已落盘（#ARCH-NLP-PIPELINE-001 Phase 0/1） | §2.7 情绪分数源 |
| 情绪聚合器 | `sentiment_aggregator.py`（#ARCH-NLP-PIPELINE-001 登记工程范围） | 🟧 **未落盘**（`src/zephyr/nlp/` 当前仅 `nlp_inference.py` + `__init__.py`） | §2.7 情绪聚合——就绪前 sentiment_score 用单条推理输出降级 |
| 盘中实时事件处理 | BM-SEL-27 锚点 MOD-RUNTIME_INTRADAY（`src/zephyr/runtime/intraday_main.py`） | ✅ 运营态（battle map 有效状态；环节自报 design，事件流水线细化待施工） | §2.5 盘中事件感知 |
| IPO 数据源 | `akshare_provider` `stock_ipo_info` 接口（production） | ✅ production | §2.5a IPO 虹吸系数 |
| ⚠️ 同名消歧：Tick 回测引擎 | `src/zephyr/backtest/implementations/event_driven_engine.py` | ✅ production，但**与本文无关**——该引擎是 Tick 级回测内核（做T专用，逐 Tick 撮合），"事件驱动"指回测架构范式（tick-event-driven），非本备忘的"新闻/公告事件驱动 alpha"。引用时勿混淆 | 不消费 |

**盘点结论**：事件驱动 sleeve 所需的四类事件源（公告/新闻/龙虎榜/异动）数据链路全部 production，唯一未落盘的是 NLP 管道的 `sentiment_aggregator.py`——§2.7 已裁定 sentiment_score 作事件方向触发而非截面排序，单条 `nlp_inference.py` 输出即可降级承载，不阻塞 MVP。真正待新建的 sleeve 内部组件仅两项：异动识别器（§2.5）与事件影响评分（§2.5 首版公式），与 §3.1"复用全部已有基础设施"裁定一致。

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
| **公告** | 业绩预告/快报、并购重组、增减持、分红送转、政策公告 | `tushare_provider` / `akshare_provider`（production，见 [11_d_data](../../02_domain_architecture_docs/11_d_data.md)） | 结构化事件主源（时间戳明确、PIT 严格） |
| **新闻** | 财经新闻、政策解读、行业动态 | `eastmoney_news_provider` / `cls_provider`（财联社）/ `rss_provider`（BBC/CNBC/NYT/Guardian/Bloomberg，production） | 非结构化情绪事件源 |
| **龙虎榜** | 游资/机构席位买卖明细 | `akshare_provider`（[BM-SEL-05-A 机构行为分析](../battle_map/battle_map_05_stock_selection.md)，production） | 资金面事件（主力行为佐证） |
| **异动** | 盘中价格/成交量相对基准的异常偏离 | 国盛证券异动雷达方法（[2026-03 国盛金工](http://stock.finance.sina.com.cn/stock/view/paper.php?autocallup=no&isfromsina=no&reportid=826626291912&symbol=sh000001)）；复用 `signal_ashare/intraday_buy_sell_point_analyzer`（[BM-SEL-05-C](../battle_map/battle_map_05_stock_selection.md)，production）+ `market_sentiment_analyzer`（[BM-SEL-03-A](../battle_map/battle_map_05_stock_selection.md)，production） | 量价异动事件（需新建识别器，见 §2.5） |

**关键区分**：`corporate_action_processor`（[MOD-TRADING-004](../../../03_modules/_domain_trading/corporate_action_processor/blueprint.md)，production）处理的是除权除息/分红/送股/配股/拆股等**持仓调整类**公司行动——它是持仓数量与均价的机械调整，不产生 alpha 信号，**不归入事件源**，但事件驱动 sleeve 须消费其事件以避免在除权日误判异动（见 §2.5 降级）。

> **⚠️ 龙虎榜事件源 2026 信号失效提示（v1.8.0 补，与 [24 号 §3.5 v1.8.2](24_daban_strategy_detail.md) 同步）**：龙虎榜作为四类事件源之一（上表"资金面事件/主力行为佐证"），其"机构净买入=利好佐证"假设已于 2026 年反向失效——[24 号 v1.8.2 实证](24_daban_strategy_detail.md)机构净买入次日胜率从 2018-2023 的 62-68% 暴跌至 **45.7%（低于 50% 随机）**。事件驱动 sleeve 消费龙虎榜作事件佐证同样受影响，event_score 须同步校准——详见 §2.5 [龙虎榜 2026 机构信号失效校准](#25-事件信号选股映射讨论要点④)。

### 2.3 事件分类（讨论要点②）

> 裁定：**首版采用六类粗分类 + Janus-Q 细分类预留**（v1.6.0 从四类升级为六类，新增 IPO + 地缘/宏观）。分类决定冲击方向与强度。

| 事件类 | 子类（首版） | 冲击方向 | 冲击强度 | 持仓倾向 |
|---|---|---|---|---|
| **业绩** | 业绩预告/快报/正式报告、盈余惊喜（surprise） | 看 surprise 方向（超预期→多，低于预期→回避） | 中-高 | rising phase 持有 |
| **并购** | 重组/并购/资产注入/股权转让 | 看方案对价（溢价注入→多，稀释→回避） | 高（停牌复牌缺口） | 复牌后 rising phase |
| **政策** | 行业政策/货币政策/产业政策 | 看政策受益方向 | 中（板块传导） | rising phase + 板块传导 |
| **突发** | 黑天鹅/董事长被查/ST/重大事故/异动 | 多为利空（回避/剔除）；少数题材爆发（多） | 高-极高 | 利空→剔除；题材→短持 |
| **IPO/再融资**（v1.6.0 新增） | 大型 IPO 上市（科创板/创业板）、定增/配股解禁 | 看虹吸方向（IPO 上市→存量板块流动性抽离，利空存量；IPO 标的本身→前 5 日无涨跌幅限制博弈） | 高（科创板最大 IPO 募资 579-666 亿可吸金 500 亿+） | IPO 上市前→完成主仓位布局+保留现金；上市后→存量板块降仓避险 |
| **地缘/宏观**（v1.6.0 新增） | 战争/制裁/贸易摩擦/汇率冲击/大宗商品价格异动 | 看传导链方向（中东冲突→油气/黄金/军工多；贸易战→稀土/农业多；汇率贬值→出口导向多） | 高-极高（持续性强于业绩/并购） | rising phase 持有 + 板块传导链跟踪 |

**细分类预留**：[Janus-Q（arXiv 2026-02）](https://arxiv.org/html/2602.19919v2) 标注 10 fine-grained event types（含 sentiment label 与关联股票），其 event-to-CAR（Cumulative Abnormal Return）建模范式可作 sleeve 内部增强方向（见 §6 待裁定-2）。首版不引入 10 类细分（避免 NLP 标注带宽过重），用六类粗分类 + 情绪分数维度承载。

### 2.4 事件冲击衰减曲线（讨论要点③）

> 裁定：**首版用经验衰减曲线（按事件类×衰减阶段）；Hawkes 自激发建模登记为暂缓前沿**。衰减速度 regime-dependent，作为 sleeve 内部参数后验捕获。

**实证依据**：

| 阶段 | 时间窗 | 特征 | 实证来源 |
|---|---|---|---|
| **rising phase** | day 0-5 | 风险调整收益上升，RVR 较 decay phase 高 9.5x | [Beyond the Event Horizon 2025](https://www.preprints.org/manuscript/202506.0079)（[20 §2.4](20_first_batch_strategies.md) 已引） |
| **decay phase** | day 6-15 | 冲击衰减，收益回归 | 同上 |
| **情绪 IC 衰减** | regime-dependent | 危机期信号集中在短-中 horizon；宏观不确定性期扩散窗口延长 | [Yukka 2026-05](https://cdn.prod.website-files.com/66b4f3430903efa023fe741b/69fdded32f3d7e02f17ff3f8_Sentiment%20Decay%20&%20Source%20Selection%20in%20Global%20Equity%20Markets%20-%20White%20Paper.pdf)（[20 §2.4](20_first_batch_strategies.md) 已引） |

**首版衰减模型**：按事件类预设经验半衰期，rising phase 持有、decay phase 兜底退出：

| 事件类 | rising 半衰期（初拟） | decay 退出窗 | 依据 |
|---|---|---|---|
| 业绩 | 3-5 天 | day 6-8 | 盈余公告后漂移（PEAD）实证，rising 约 5 天；[FMP 2026-04](https://intelligence.financialmodelingprep.com/education/other/tracking-postearnings-announcement-drift-with-fmps-market-data) 衰减曲线 day 9 进入平台期（exit zone） |
| 并购 | 1-3 天（复牌后） | day 4-6 | 停牌复牌缺口一日消化大半 |
| 政策 | 3-7 天 | day 8-12 | 政策传导链较长，板块轮动延续 |
| 突发（题材） | 1-3 天 | day 4-5 | 题材爆发快衰减快 |
| **IPO/再融资**（v1.6.0 新增） | 上市前 3-5 天（布局窗） | 上市后 day 1-5（虹吸期） | 科创板大型 IPO 前 5 日无涨跌幅限制→上市日虹吸峰值，存量板块 day 1-3 跌幅最大，day 5 后虹吸衰减 |
| **地缘/宏观**（v1.6.0 新增） | 5-15 天（远长于业绩/并购） | day 16-30 | 地缘冲突持续性远超离散事件——美伊战争期间资源股 rising phase 可达 2-4 周（[Sinong Xiao 2026 南京理工大学](https://www.atlantis-press.com/proceedings/edms-2026/) 资金流→收益传导在牛/熊 regime 下机制显著异质，地缘驱动的资源股主线属"结构性 regime 切换"非"一次性冲击"） |

**⚠️ 极端反应反转（PEAD Inversion，2026 新增关键修正）**：

上述 rising→decay 单调衰减模型**仅适用于温和反应（event-day reaction ∈ [-3%, +3%]）**。2026 最新实证表明，极端事件日反应存在**反转**而非延续：

| event-day 反应 | 经典 PEAD 预测 | 2026 实证（mega-cap tech, 2023-2026） | 出处 |
|---|---|---|---|
| 强正（>+3%） | 延续上涨 | **反转下跌**：20 日中位 -5.58%、5 日 -3.20% | [Vortex Capital 2026-05](https://www.vortexcapitalgroup.com/insights/the-mega-cap-pead-inversion-when-the-reaction-is-the-trade-and-when-it-is-the-trap) |
| 强负（<-3%） | 延续下跌 | **反弹**：5 日中位 +4.20%、20 日 +3.46% | 同上 |
| 温和正（0~+3%） | 延续 | 延续（5 日 +1.71%），20 日衰减 | 同上 |
| 温和负（-3%~0） | 延续 | 短期继续下跌（5 日 -1.03%），20 日走平 | 同上 |

**根因**：信息不再缓慢扩散——衍生品gamma、0DTE期权流、暗池将数周隐含波动率压缩到单一隔夜窗口，机构再定价已在盘前完成，剩余仅为做市商对冲+散户追涨+动量基金延续，随后均值回归。

**首版修正裁定**：
- **温和反应（|reaction| ≤ 3%）**：沿用 rising→decay 经验衰减曲线（上表）
- **极端反应（|reaction| > 3%）**：**不追涨/不杀跌**——事件日收盘即为信号终点而非起点；若已持仓且反应极端正向，提前进入 decay 退出（不等 rising 半衰期）；若反应极端负向，不恐慌加仓，等 day 2-3 确认（CVD/量价结构是否吸收卖压）再决策

```python
def check_selling_pressure_absorbed(symbol, day2_3_data, baseline_volume_ratio=1.5, cvd_threshold=0.0):
    """吸收卖压判定（PEAD Inversion 极端负反应的 day 2-3 确认算法）
    
    判据：CVD（Cumulative Volume Delta）转正 + 量价结构吸收卖压
    输入：
      day2_3_data: day 2-3 的分钟级 OHLCV 数据
      baseline_volume_ratio: 基准成交量比（相对 5 日均量）
      cvd_threshold: CVD 转正阈值
    """
    import numpy as np
    # 1. CVD（累计成交量差）：买方主动成交量 - 卖方主动成交量
    #    用 close-mid 判方向：close>mid=买方主动，close<mid=卖方主动
    mid_price = (day2_3_data['high'] + day2_3_data['low']) / 2
    delta = np.where(day2_3_data['close'] > mid_price, day2_3_data['volume'], 
                     -day2_3_data['volume'])
    cvd = np.cumsum(delta)
    # 2. 量价结构吸收判据
    volume_ratio = day2_3_data['volume'].mean() / day2_3_data['volume'].rolling(5).mean().mean()
    price_stabilized = day2_3_data['close'].iloc[-1] >= day2_3_data['close'].iloc[0] * 0.98  # 跌幅<2%
    # 3. 吸收卖压判定：CVD 转正（买盘接货）+ 量能放大（放量消化）+ 价格企稳
    absorbed = (cvd[-1] > cvd_threshold) and (volume_ratio > baseline_volume_ratio) and price_stabilized
    return {
        "absorbed": absorbed,  # True=卖压已吸收可布局, False=卖压未止继续观望
        "cvd_final": cvd[-1],
        "volume_ratio": volume_ratio,
        "price_stabilized": price_stabilized,
    }
```

**为何 CVD 转正是吸收判据**：极端负反应后 day 2-3 若 CVD 转正，意味着买方主动成交量超过卖方——聪明资金在低位接货，卖压被消化。结合量能放大（放量消化）与价格企稳（跌幅收窄），三者共振才是'吸收卖压'确认。这是 PEAD Inversion 极端负反应'等 day 2-3 确认再决策'的具体施工算法。CVD 是 order flow 分析的标准工具，与 [22 板块轮动](22_sector_rotation_spec.md) 量能维度同源。
- **A 股适配**：mega-cap tech 实证需 A 股回测验证（大盘股 vs 小盘股信息扩散速度不同），登记为 §6 待裁定-5

**PEAD.txt 文本惊喜（2026 关键发现）**：[费城联储 PEAD.txt 论文](https://marketmaker.cc/en/blog/post/llm-alpha-mining-earnings-calls/)（Meursault et al.）构建纯文本版 SUE（SUE.txt）——**不使用任何数值盈余数据**，仅从公告文本提取。结果：SUE.txt 产生的漂移**是经典数值 PEAD 的 2 倍**；近年来经典数值 PEAD 已几乎消失（市场学会了处理数字），但**文本漂移仍然显著**。**结论**：事件驱动 sleeve 的 NLP 文本信号比数值惊喜更有 alpha 价值（支撑 §2.7 NLP 复用裁定）。

> **事件驱动六因子矩阵（v1.5.0 补，施工算法补全——交叉引用 [20 §2.4 v1.4.4](20_first_batch_strategies.md)）**：当前 §2.4 事件 alpha 仅 ORJ + PEAD Inversion 两项，[20 §2.4 v1.4.4](20_first_batch_strategies.md) 已登记事件驱动新 alpha 因子四项，本备忘须交叉引用同步六因子完整矩阵：
>
> | 因子 | 定义 | 实证 | 维度 | 当前状态 |
> |---|---|---|---|---|
> | **ORJ**（隔夜跳空） | `ORJ = open/pre_close - 1`（事件日隔夜收益率） | collinseow 2026-02 季度超额 6.78% | 事件日隔夜 | ✅ §2.4 ③ 已施工（含完整算法骨架） |
> | **PEAD Inversion**（极端反应修正） | \|reaction\|>3% 反转而非延续 | Vortex Capital 2026-05 mega-cap 实证 | 极端反应方向 | ✅ §2.4 已施工 |
> | **dReport**（披露日提前天数） | `dReport = 法定披露截止日 - 实际披露日`（正值=提前披露） | 招商证券 10 年回测年化超额 4.88%/Sharpe 1.44；大幅提前 T+5 上涨概率 70-75% | 事件时点 | 🟧 待施工（§6 待定问题） |
> | **Jump on PEAD**（公告后价格跳跃） | 公告后 5 日窗口 CAR 的跳跃分量 | 华泰金工 5 日 IC=10.96% | 事件冲击强度 | 🟧 待施工（§6 待定问题） |
> | **隔夜趋势**（Overnight Trend） | 隔夜收益率（open/pre_close-1）的 20 日滚动均值/动量 | 西部证券 IC 加权 Rank IC=-0.1687、中证 2000 年化超额 7.97% | 日常隔夜（非事件日） | 🟧 待施工（§6 待定问题） |
> | **AStockEvent Feed**（事件结构化） | 13+ 事件类型结构化 Feed（减持/ST/监管函/解禁/回购/重组等） | GitHub 2026-06-13 | 事件结构化数据源 | 🟧 待施工（NLP 管道工程化候选） |
>
> **六因子协同关系**：
> - **dReport × ORJ**：dReport（披露时点）是 PEAD 的事件时点扩展——dReport 大幅提前 + ORJ>3% = 强信号叠加（"靓女先嫁"+开盘确认双重利好）
> - **Jump on PEAD × ORJ**：Jump on PEAD（5 日窗口跳跃）是 ORJ（单日跳空）的冲击强度扩展——ORJ 即时确认，Jump on PEAD 滚动跟踪
> - **隔夜趋势 × ORJ**：隔夜趋势（日常隔夜）是 ORJ（事件日隔夜）的时序扩展——事件日 ORJ>3% + 近 20 日隔夜趋势为正 = 强信号叠加
> - **AStockEvent × §2.3 事件分类**：AStockEvent 的 13 类比四类粗分类更细，可作 [Janus-Q 10 类细分类](#23-事件分类讨论要点②) 的 A 股本土化映射，直接驱动 dReport 计算
>
> **施工优先级**：dReport（年化超额 4.88%）与 Jump on PEAD（IC 10.96%）有 10 年/5 日窗口实证，优先级最高——可作为 NLP 管道（[#ARCH-NLP-PIPELINE-001](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)）未就绪前的数值 alpha 补充（与 ORJ 同属降级算法，不依赖 NLP）。隔夜趋势作为日常 alpha 因子接入因子工厂。AStockEvent 作为 NLP 管道工程化候选，远期评估。
>
> **对 §3.6 漏斗③ event_impact_score 的施工落地**：六因子矩阵为 §3.6 事件驱动漏斗第三层"事件影响评分排序"提供具体因子——`event_impact_score = w1·ORJ_z + w2·dReport_z + w3·Jump_on_PEAD_z + w4·overnight_trend_z + PEAD_inversion_gate`（权重待 G10 校准，PEAD Inversion 作门控非加权项）。详见 [20 §2.4 v1.4.4 六因子矩阵](20_first_batch_strategies.md)。

**Hawkes 自激发建模（暂缓前沿）**：[Hawkes Processes for Investors 2026-02](https://stockalpha.ai/alpha-learning/hawkes-processes-for-investors-modeling-self-exciting-volatility-bursts) 用自激发点过程建模事件聚类（branching ratio n=α/β，n→1 近临界=事件簇爆发）。2026 新实证：
- [中国股市传染分析（arXiv 2512.08000）](https://arxiv.org/html/2512.08000v1/) 用时空 Hawkes 建模 A 股板块轮动——高交易活跃期板块延续趋势，低活跃期板块轮动加剧，与本项目板块轮动（[G06](22_sector_rotation_spec.md)）天然契合
- [Price Discovery 物理（arXiv 2601.11602）](https://arxiv.org/html/2601.11602v2) 用 Hawkes 区分外生（新闻驱动）vs 内生（反馈驱动）资金流——外资/机构流驱动永久价格发现，散户流为恐慌驱动近爆炸自激发
- [Persia 2026-06 金融传染](https://proceedings.systemdynamics.org/2026/papers/P1265.pdf) 多元 Hawkes 跟踪 VIX，与 DCC-GARCH 竞争性，可作系统性风险监控工具
- **[Transfer-Entropy + Hawkes 跨境风险传染（MDPI Entropy 2026-08-06）](https://www.mdpi.com/1099-4300/28/8/887)**：两层框架（transfer entropy + 多元 Hawkes），Hawkes 激发分量在 COVID-19/2022 能源危机期间将传染强度放大 35-58%；**Von Neumann 图熵在峰值回撤前 7-12 交易日达到历史极值**——可作为 firm 层系统性风险预警信号（支撑 §6 待裁定-1 Hawkes 留给风控层的裁定）
- **[Hawkes-Driven OTC Market Making（arXiv 2608.02002, 2026-08-03）](https://arxiv.org/html/2608.02002v1)**：用一般 Hawkes 核建模 RFQ 到达，开发 Volterra–Riccati 近似层级处理路径依赖（指数核可精确 Markovian lifting，混合指数/长记忆核需近似）。**关键发现**：幂律 RFQ 记忆下，方向性 RFQ 突发改变未来流量条件预测 → 通过 continuation-value 影子价转为持续性报价偏斜 → 内生 OTC 报价影响继承 RFQ 预测响应的长记忆衰减。此为 Hawkes 在做市/流动性层（而非 sleeve alpha 层）的最新 8 月实证，进一步支撑"Hawkes 留给风控层"裁定——其长记忆+内生影响特性适合 G18 流动性危机的订单流建模

**Hawkes 实操参考（若未来启用）**：[MetricGate 2026-06 实操指南](https://metricgate.com/blogs/hawkes-self-exciting-process-r/) 给出完整校准流程——MLE 估计 μ/α/β → 计算 branching ratio n=α/β（n<1 稳定，n→1 近临界爆发）→ 通过经验拟合的 transfer function 将 intensity λ(t) 转为波动率 → 定义升级触发器（intensity 倍数阈值/短期期望事件数/delta VaR 阈值）。此流程可作为 G17/G18 firm 层风控的参考实现路径。

> 裁定：Hawkes 建模作为 sleeve 内部增强方向登记为暂缓（§6 待裁定-2）。首版不引入——经验衰减曲线 + 极端反应反转修正已能承载 rising/decay 持仓纪律，Hawkes 的 branching ratio 监控更适合 firm 层风险（[G17 VaR/ES](36_var_es_monitoring.md) / [G18 流动性危机](37_liquidity_crisis_protocol.md)），留给风控层评估。MDPI 2026-08 的"图熵提前 7-12 天预警"发现进一步强化此裁定方向。

### 2.5 事件信号→选股映射（讨论要点④）

> 裁定：**复用选股漏斗 BM-SEL-19（事件驱动分布筛选，design/MOD-SIG-049），不新建独立选股 pipeline**。事件→候选标的生成 + 事件影响评分 → 注入漏斗第四层。

**事件→选股映射链路**：

```
事件源(公告/新闻/龙虎榜/异动)
   ↓ 事件分类(业绩/并购/政策/突发/IPO/地缘) + 情绪分数(NLP)
事件影响评分 = f(事件类, 冲击方向, 冲击强度, 衰减阶段)
   ↓ 注入选股漏斗
BM-SEL-19 事件驱动分布筛选（design, MOD-SIG-049, 50→30只）
   ├─ 事件影响评分（L2-D 图谱，来自 BM-SEL-11）
   ├─ 事件驱动条件 PDF 修正（上涨概率下降 >15% 淘汰）
   └─ 事件传导链风险（来自 BM-SEL-11）
   ↓
事件驱动 sleeve 持仓（rising phase 为主，decay phase 退出）
```

**关键接口**：
- **事件→候选标的**：事件触发标的即候选（非固定池），由事件源动态生成。事件类×冲击方向决定入池/剔除（利空事件→剔除已有持仓或回避）
- **事件影响评分（首版显式公式）**：

```python
# 首版事件影响评分（简化版，知识图谱未就绪时用此）
event_score = (
    event_class_weight[event_class]      # 业绩=1.0 / 并购=1.2 / 政策=0.8 / 突发=1.5 / IPO=1.3 / 地缘=1.4
    * surprise_direction                 # +1 利好 / -1 利空 / 0 中性
    * sentiment_score                     # NLP 情绪分数 [-1, +1]（来自 #ARCH-NLP-PIPELINE-001）
    * decay_stage_factor                  # rising=1.0 / decay=0.5 / post-decay=0.2
    * extreme_reaction_modifier           # |reaction|>3% 时 = 0.3（极端反转修正，见 §2.4）
                                         # |reaction|≤3% 时 = 1.0
)
# event_score ∈ [-1.5, +1.5]，正→入池做多候选，负→剔除/回避
# 阈值：|event_score| < 0.2 → 无信号（噪声），不动作
```

> **龙虎榜 2026 机构信号失效校准（v1.8.0 补，2026-08-10 与 [24 号 §3.5 v1.8.2](24_daban_strategy_detail.md) 同步）**：
>
> [24 号 v1.8.2](24_daban_strategy_detail.md) 已实证 2026 年龙虎榜生态结构性变化——机构净买入次日胜率从 2018-2023 的 62-68% 暴跌至 **45.7%（低于 50% 随机，信号反向失效）**。26 号事件驱动 sleeve 消费龙虎榜作事件源（§2.2 ①事件源四类之一，角色"资金面事件/主力行为佐证"），"机构净买入=利好佐证"假设同样失效，event_score 须同步校准，与 23-A 游资接力评分保持口径一致。
>
> | 维度 | 2018-2023 基线 | 2026 实测 | 26 号 event_score 校准含义 |
> |---|---|---|---|
> | 机构净买入次日胜率 | 62-68% | **45.7%（<50% 随机）** | "机构净买入=事件利好佐证"假设反向失效——龙虎榜机构净买入不再自动强化 event_score，须从佐证因子降级为中性参考 |
> | 净买率 >12% 样本 20 日均收 | — | **+5.11%（仍有效）** | 极端净买率阈值仍有效——event_score 佐证须从"机构净买入方向"转向"净买率极端值"，用 12% 硬阈值替代软评分 |
> | 外资三巨头龙虎榜占比 | 偶现（"黑马"） | **19.41%（"常规军"）** | "外资买入=利好佐证"信号被摊薄，须按席位类型差异化（外资≠量化机构≠传统游资） |
> | 拉萨天团活跃度 | 高频主导 | **同比 -35%（退潮）** | 传统游资席位退场，"游资接力佐证"信号弱化 |
>
> **施工建议（event_score 龙虎榜佐证校准）**：
> 1. **机构净买入佐证降权**：龙虎榜机构净买入作为事件佐证（confirmation）的权重砍半或归零——当事件（业绩/并购/政策利好）伴随龙虎榜机构净买入时，不再自动强化 event_score，等首批策略实盘 3-6 月后用本项目持仓数据重新校准
> 2. **净买率极端值硬阈值门控**：新增 `dragon_tiger_corroboration_modifier`——净买率≥12% → 佐证加分（×1.2），<12% → 不加分（×1.0），用 12% 硬阈值替代"机构净买入=加分"软评分
> 3. **席位类型差异化**：外资席位（高盛/瑞银/摩根大通）≠ 量化机构席位 ≠ 传统游资席位——量化机构席位触发 [24 号 §3.10/§3.11 量化席位过滤](24_daban_strategy_detail.md) 降权（≥3 量化席位+买入占比>30% → 佐证无效化），与 23-A 校准口径一致
> 4. **数据源**：龙虎榜数据已入库双表——`c1_market.dragon_tiger`（每日上榜汇总，AKShare `stock_lhb_detail_em`）+ `c1_market.dragon_tiger_seat`（**席位明细**，AKShare `stock_lhb_stock_detail_em` Top5 买卖席位合并去重），tasks.yaml `dragon_tiger_incremental` / `dragon_tiger_seat_incremental` 盘后调度（v1.9.0 代码侧审计确认，见 §1.4）。**席位类型字段消费自 `dragon_tiger_seat` 表**，量化席位/外资席位/游资席位分类在此表落地
>
> **event_score 佐证修正因子（施工算法）**：
>
> ```python
> def dragon_tiger_corroboration_modifier(event, dragon_tiger_data):
>     """龙虎榜机构净买入佐证修正因子（2026 信号失效校准后）
>     
>     24号 v1.8.2 实证：机构净买入次日胜率 45.7% < 50% 随机，方向性佐证失效。
>     校准后仅净买率极端值（≥12%）作为强佐证，席位类型差异化过滤量化席位。
>     
>     返回 event_score 的乘法修正因子 ∈ [0.7, 1.2]：
>       - 无龙虎榜数据（非龙虎榜标的）→ 1.0 不修正
>       - 净买率≥12% → 1.2 强佐证（20日均收+5.11%仍有效）
>       - 净买率<12% → 1.0 机构净买入方向失效，不加分
>       - 量化席位 hard（≥3席+占比>30%）→ ×0.7 佐证无效化
>       - 量化席位 soft（≥3席同现）→ ×0.85 佐证弱化
>     """
>     if dragon_tiger_data is None:
>         return 1.0  # 无龙虎榜数据（非龙虎榜标的）→ 不修正
>     net_buy_ratio = dragon_tiger_data.net_buy_amount / dragon_tiger_data.total_turnover
>     # ① 净买率极端值硬阈值门控（+5.11% 20日均收仍有效）
>     if net_buy_ratio >= 0.12:
>         base_modifier = 1.2  # 强佐证加分
>     else:
>         base_modifier = 1.0  # 机构净买入方向失效→不加分（不再用软评分）
>     # ② 量化席位过滤（24号 §3.10 line 945 + §3.11 双阈值预警）
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
> **与 24 号校准的口径一致性**：24 号校准 23-A 游资接力评分的龙虎榜因子（机构净买方向降权/净买率极端值升级/席位类型差异化），26 号校准 event_score 的龙虎榜佐证因子——两者共用 `dragon_tiger` 表数据源 + 共用 12% 净买率硬阈值 + 共用 [24 号 §3.11 `detect_quant_seat_warning`](24_daban_strategy_detail.md) 量化席位双阈值，确保打板 sleeve 与事件驱动 sleeve 对龙虎榜信号的解读口径一致，避免跨 sleeve 信号歧义。

**SUE+EAR 双因子增强评分（v1.2.0 升级，可选）**：[Rockstead 2026-05 两因子框架](https://rockstead.com/market-insights/capturing-post-earnings-drift-a-two-factor-approach/)（Brandt/Kishore/Santa-Clara/Venkatachalam 2008 范式）证明**基本面惊喜（SUE）与市场反应（EAR）近零相关（r=0.004）**——二者捕获盈余事件的不同方面，组合提供真正分散化。首版单因子 `event_score` 将"市场反应"粗化为 `extreme_reaction_modifier`（二值 0.3/1.0），双因子版将其升为连续信号：

```python
# v1.2.0 SUE+EAR 双因子增强评分（业绩类事件专用，其他类沿用首版单因子）
def event_score_dual_factor(event):
    """业绩类事件双因子评分：SUE(基本面惊喜) + EAR(市场反应)
    Rockstead 2026-05: 两因子 r=0.004 近正交，组合年化 18.50%
    """
    # 因子1：SUE 标准化未预期盈余（数值惊喜，剥离 Fama-French 风险溢价）
    # v1.7.1 修复：actual_eps/consensus_eps 原为裸变量未定义，统一为 event 属性 + wind_consensus_eps 调用
    # （与 §2.5 expectation_gap_with_revision_momentum L362/367-368 口径一致）
    sue = (event.actual_eps - wind_consensus_eps(event.symbol, event.date)) / rolling_std_surprise(event.symbol)
    sue_z = winsorize_zscore(sue)  # [-3, +3] 标准化

    # 因子2：EAR 盈余公告收益（3日 CAR [-1,+1]，匹配 FF 6组合基准）
    ear = cumulative_abnormal_return(event.symbol, day_start=-1, day_end=+1,
                                     benchmark="ff6_size_bm")
    # EAR 含反转成分（Rockstead: Q5-Q1 EAR 年化 -3.39%，市场过度反应后衰减）
    # 故 EAR 用于"识别过度反应"而非"追涨"

    # 双因子组合：SUE 正向（漂移延续）+ EAR 反向修正（过度反应衰减）
    # 温和反应：SUE 主导，EAR 修正小
    # 极端反应：EAR 反转修正大（与 §2.4 PEAD Inversion 一致）
    reaction_extremity = abs(ear) / 0.03  # 相对 3% 阈值的极端度
    ear_reversal_weight = min(reaction_extremity, 1.0)  # 0~1，越极端越反转

    # 组合分：SUE 漂移方向 - EAR 过度反应部分
    combined = sue_z * (1 - ear_reversal_weight * 0.5) - ear * ear_reversal_weight * 10
    # combined > 0 → 漂移延续占优（温和惊喜+未过度反应）→ 入池做多
    # combined < 0 → 过度反应反转占优（极端反应）→ 不追涨/回避
    return combined
```

**双因子 vs 首版单因子裁定**：首版 `event_score`（四类通用）保留为默认；业绩类事件优先用双因子（SUE+EAR），因业绩类有明确的数值惊喜与市场反应可分离。其他三类（并购/政策/突发）无标准化"预期"概念，沿用首版单因子 + 情绪分数。**升级路径**：NLP 管道（#ARCH-NLP-PIPELINE-001）就绪后，SUE 可替换为 [PEAD.txt 文本惊喜](https://marketmaker.cc/en/blog/post/llm-alpha-mining-earnings-calls/)（费城联储实证文本 SUE 漂移是数值的 2 倍）。

**SUE 预期构建方式——选项之外更好的答案算法**（2026-08-10 二次审查补充）：当前代码行 180 用 `consensus_eps`（分析师预期），但 [Zyberno 2026-08-05](https://zyberno.com/earnings-surprise/ACNB/) 提出从 **SEC 实际报告构建预期**的替代方案——**季节性随机游走+漂移**（seasonal random walk with drift），不使用分析师 consensus：

```
Expected_EPS_q = EPS_(q-4) + drift
  drift = mean(近期同比季度 EPS 变化)
  Surprise = Actual_EPS_q - Expected_EPS_q
  SUE = Surprise / σ(trailing seasonal surprises)
  SUE winsorized to ±4（防止极端值扭曲）
```

**核心优势**：Zyberno 的 SUE "built from reported actuals rather than analyst consensus, it cannot be distorted by guidance management"——从 SEC 实际报告构建预期，**无法被预期管理扭曲**（管理层可以通过引导分析师预期来"beat consensus"，但无法扭曲自身历史实际报告）。Latané & Jones (1977) 原始 SUE 定义即此形式，Foster (1977) / Bernard & Thomas (1989) PEAD 文献的基础。

**与当前 `consensus_eps` 方案的对比**：

| 维度 | 当前 consensus_eps 方案 | Zyberno seasonal random walk 方案 |
|---|---|---|
| 预期来源 | 分析师 consensus（Wind/聚源） | SEC 实际报告历史（自身趋势） |
| guidance management 风险 | **有**（管理层可引导分析师压低预期） | **无**（无法扭曲自身历史） |
| 数据依赖 | 需分析师预期数据源（付费） | 只需 SEC 实际报告（公开免费） |
| 适用条件 | 需足够分析师覆盖（A股小盘股可能无覆盖） | 需 ≥12 个干净季度历史（新股/深度周期股不适用） |
| PEAD 信号强度 | 标准 | 标准（与原始 PEAD 文献一致） |

**裁定**：MVP 阶段保留 `consensus_eps` 方案（分析师预期数据已接入，且 A 股有分析师覆盖的标的信号更密集）；**Zyberno seasonal random walk 记为 Phase 2 候选**——用于 ① A 股小盘股无分析师覆盖的标的（扩大 SUE 适用范围），② 交叉验证 consensus SUE 的可靠性（两种方法 SUE 同向 → 信号增强，背离 → guidance management 风险信号）。升级条件：consensus_eps SUE 在小盘股信号稀疏时触发评估。

**确认型入场模式（v1.2.0 新增）**：[NexusFi 2026-06 事件驱动三模式](https://nexusfi.com/a/automation/event-driven-trading-automation)区分三种入场——①fade the initial move（反转，对应极端反应）②momentum continuation（延续，对应温和反应）③**confirmation-based entry**（确认型，对应模糊事件）。首版 `should_enter` 仅区分利好/利空/噪声，缺"模糊事件等确认"逻辑。补全：

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

**ORJ 隔夜跳空 + 净利润断层（v1.3.0 新增，A 股业绩事件第三维信号）**：上述 SUE+EAR 双因子捕获"数值惊喜"与"日内反应"两维。2026 最新实证表明，**隔夜跳空**是业绩事件的独立第三维信号——A 股 T+1 下，财报多在盘后披露，次日开盘跳空=市场隔夜消化后的"第一反应"，与日内 EAR（盘后 3 日 CAR）正交：

| 信号维度 | 捕获内容 | 时间窗 | A 股适配 |
|---|---|---|---|
| SUE（数值惊喜） | 基本面超预期幅度 | 公告日 | ✅ 一致预期可得（万得/同花顺） |
| EAR（日内反应） | 3 日 CAR [-1,+1] | 公告前后 3 日 | ✅ FF6 基准或行业基准 |
| **ORJ（隔夜跳空）** | 盘后→次日开盘的隔夜消化 | 公告日收盘→次日开盘 | ✅ A 股 T+1 天然隔夜窗口 |

**ORJ 定义**（[Bahcivan et al. 2023 隔夜价格跳空过度反应](http://hulusibahcivan.com/wp-content/uploads/2023/05/New-Avenues-in-Expected-Returns_Investor-Overreaction-and-Overnight-Price-Jumps-in-US-Stock-Markets_May-2023.pdf)，9,718 只美股实证）：

```python
# ORJ = Overnight Return Jump
def overnight_return_jump(symbol, event_date):
    """隔夜跳空 = 次日开盘价相对公告日收盘价的跳空幅度
    A 股 T+1 下财报多盘后披露 → 次日开盘=市场隔夜第一反应
    """
    prev_close = close_price(symbol, event_date)
    next_open = open_price(symbol, event_date + 1)
    orj = (next_open - prev_close) / prev_close
    return orj
```

**实证依据**：
- **Bahcivan et al. 2023**：隔夜跳空显示投资者短期过度反应，**正/负跳空后 5 日内显著反转**（reversal and predictability for up to 5 days）；零成本反转策略在 1 月内获风险调整收益。**套利成本越低的股票反转越大**——A 股小盘股套利约束低，反转效应可能更强
- **净利润断层（A 股本土化 ORJ）**：[中国证券报 2026-04 量化私募博弈财报季](http://m.ce.cn/cj/gd/202604/t20260424_2925768.shtml)——"净利润断层"指财报公布后股价因业绩超预期跳空上涨，是 A 股业绩超预期策略的本土化形态，财报季有效性阶段性凸显
- **夜盘预测力有限**：[火山引擎 2026-04 美股夜盘 10 年回测](https://developer.volcengine.com/articles/7629162484989394995)——财报次日夜盘预测准确率仅 54.7%，反转概率 >45%（散户追涨、算法出货）；**宏观事件夜盘可信度最高**（>65%）。对 A 股含义：业绩类 ORJ 须警惕"跳空后反转"，与 §2.4 PEAD Inversion 一致

**ORJ 与 PEAD Inversion 的协同**：§2.4 已裁定极端反应（|reaction|>3%）反转。ORJ 是"极端反应"的**隔夜版本**——若 ORJ > +3%（盘后超预期 + 次日开盘跳空 >3%），触发 PEAD Inversion 反转逻辑，不追涨；若 ORJ ∈ [0, +3%]（温和跳空），与 SUE 同向则加权入场。**ORJ 作为"极端反应"的前置预警**——盘后公告 + 次日开盘即可判定，比等 3 日 EAR 更早。

**预期差 + Whisper Number（v1.3.0 新增，SUE 的 A 股增强源）**：SUE 依赖"一致预期"（consensus），但一致预期是**静态快照**——分析师持续更新内部模型但很少发布修订，公告日的一致预期已陈旧。[EarningsWhispers 2026-08-05](https://beta.earningswhispers.com/about-whispers) 实证：Whisper Number（分析师最新未发表预期）比一致预期**准确率高 69.7%**；当 whisper > consensus 超 5%，"beat"概率跳升至 ~75%。A 股本土化形态：

| 概念 | 美股 | A 股等价 | 数据可得性 |
|---|---|---|---|
| Whisper Number | 分析师最新未发表预期（EarningsWhispers 付费） | **分析师预测修正动量**（一致预期的近期变动方向） | ✅ 万得/同花顺一致预期时序可计算 |
| Estimate Revision Momentum | 一致预期随时间的漂移 | 同上 | ✅ 同上 |

**A 股预期差构建**（[中邮证券 2026-06 业绩之锚7](https://finance.sina.com.cn/stock/stockzmt/2026-06-05/doc-iniaikau2934869.shtml)）：
- **季报/半年报**：财报公布后万得分析师一致预期的**变动情况**衡量超预期（一致预期上调=超预期，下调=不及预期）
- **年报**：直接用一致预期与财报公布值比较
- **实证**：一季报业绩超预期个股胜率显著高于其他报告期，财报公布后 30 天超额收益均值 1.9%、60 天升至 2.8%；**一季报是最适合"业绩预期差"策略的报告期**（胜率 7-21 天持续上升，30/60 天仍保持 51.4%/49.5%）
- **年报陷阱**：A 股对年报超预期反应最平淡（定价业绩利空不定价业绩利好）——年报事件需降低 SUE 权重

```python
# v1.3.0 预期差 + 修正动量（替代/增强 SUE 的 consensus 基准）
def expectation_gap_with_revision_momentum(symbol, actual_eps, event_date, report_type):
    """A 股预期差 + 分析师修正动量（Whisper Number 本土化）
    中邮证券 2026-06: 一季报预期差策略 30天超额 1.9%/60天 2.8%
    """
    # 1. 静态预期差（年报用）：actual vs consensus
    consensus = wind_consensus_eps(symbol, event_date)
    static_gap = (actual_eps - consensus) / abs(consensus) if consensus != 0 else 0

    # 2. 动态预期差（季报/半年报用）：财报后一致预期变动
    # 一致预期上调 = 超预期；下调 = 不及预期
    consensus_before = wind_consensus_eps(symbol, event_date - 1)
    consensus_after = wind_consensus_eps(symbol, event_date + 5)  # 公告后5日一致预期
    revision_momentum = (consensus_after - consensus_before) / abs(consensus_before)

    # 3. 报告期权重调整（中邮证券实证：一季报最优，年报最差）
    report_weight = {
        "Q1": 1.0,    # 一季报：胜率最高，预期差策略最有效
        "semi": 0.8,  # 半年报：次优
        "Q3": 0.7,    # 三季报：中等
        "annual": 0.4 # 年报：A股不定价业绩利好，降权
    }.get(report_type, 0.7)

    # 4. 组合预期差：动态优先（季报），年报降权
    if report_type != "annual":
        gap = revision_momentum  # 动态预期差为主
    else:
        gap = static_gap * report_weight  # 年报用静态且降权

    return gap  # gap > 0 = 超预期，gap < 0 = 不及预期
```

**三因子融合（SUE×EAR×ORJ + 预期差增强）**：v1.2.0 双因子升级为三因子，ORJ 作为"隔夜第一反应"前置预警，预期差作为 SUE 的 A 股增强基准：

```python
# v1.3.0 三因子融合评分（业绩类事件）
def event_score_triple_factor(event):
    """业绩类三因子：SUE(数值惊喜,用预期差增强) + EAR(日内反应) + ORJ(隔夜跳空)
    Bahcivan 2023: ORJ 与日内收益正交；Rockstead 2026: SUE/EAR r=0.004 近正交
    三因子两两近正交 → 真分散化
    """
    # 因子1：SUE 增强（预期差替代静态 consensus）
    sue = expectation_gap_with_revision_momentum(
        event.symbol, event.actual_eps, event.date, event.report_type)
    sue_z = winsorize_zscore(sue)  # [-3, +3]

    # 因子2：EAR 日内反应（同 v1.2.0）
    ear = cumulative_abnormal_return(event.symbol, -1, +1, benchmark="ff6_size_bm")

    # 因子3：ORJ 隔夜跳空（新增）
    orj = overnight_return_jump(event.symbol, event.date)
    # ORJ 方向与 SUE 一致 → 加权；ORJ 极端（>3%）→ 触发反转（§2.4 PEAD Inversion）
    orj_signal = orj if abs(orj) <= 0.03 else -orj * 0.5  # 极端跳空反转修正

    # 三因子融合：SUE 主导 + ORJ 前置预警 + EAR 过度反应修正
    reaction_extremity = max(abs(ear), abs(orj)) / 0.03
    reversal_weight = min(reaction_extremity, 1.0)

    combined = (sue_z * (1 - reversal_weight * 0.3)    # SUE 漂移（极端反应时降权）
                + orj_signal * 2.0                       # ORJ 隔夜第一反应（温和时加权）
                - ear * reversal_weight * 10)            # EAR 过度反应反转修正
    # combined > 0 → 漂移延续占优 → 入池做多
    # combined < 0 → 过度反应反转占优 → 不追涨/回避
    return combined
```

**三因子 vs 双因子裁定**：v1.2.0 双因子（SUE+EAR）保留为**降级默认**（一致预期时序不可得时）；v1.3.0 三因子（SUE+EAR+ORJ + 预期差增强）为**主选**（万得/同花顺一致预期时序可得时）。ORJ 计算仅需 OHLC（已有所需数据），无额外数据依赖；预期差增强依赖一致预期时序（万得/同花顺已订阅）。**升级路径不变**：NLP 管道就绪后 SUE→PEAD.txt 文本惊喜。

> **事件驱动六因子矩阵（v1.5.0 补，选项之外更好算法——当前 §2.5 事件 alpha 仅 ORJ + PEAD Inversion + SUE+EAR，缺披露时点/价格跳跃/隔夜趋势/事件结构化 Feed 四项新因子）**：
>
> 本备忘 §2.5 当前 SUE+EAR+ORJ 三因子融合是 MVP 基线，[20 §2.4 v1.4.4](20_first_batch_strategies.md) 已登记四项新 alpha 因子，构成六因子矩阵：
>
> | 因子 | 定义 | 实证 | 维度 |
> |---|---|---|---|
> | **ORJ**（事件日隔夜） | open/pre_close - 1 | collinseow 2026-02 季度超额 6.78% | 事件冲击方向（已施工） |
> | **PEAD Inversion**（极端反应修正） | \|reaction\|>3% 反转而非延续 | Vortex 2026-05 mega-cap tech | 衰减曲线修正（已施工 §2.4） |
> | **SUE+EAR**（盈余惊喜+公告收益） | 标准化未预期盈余 + 公告期收益 | Rockstead 2026-05 r=0.004 近正交 | 盈余信号（已施工 §2.5） |
> | **dReport**（披露时点） | 法定披露截止日 - 实际披露日（提前天数） | 招商证券 10 年回测年化超额 4.88%/Sharpe 1.44 | 事件时点（**待补**） |
> | **Jump on PEAD**（冲击强度） | 公告后 5 日 CAR 的跳跃分量 | 华泰金工 2026-04 IC=10.96% | 冲击强度量化（**待补**） |
> | **隔夜趋势**（日常隔夜） | 20 日隔夜收益率均值/动量 | 西部证券 2026-04 Rank IC=-0.1687/中证2000 年化超额 7.97% | ORJ 时序扩展（**待补**） |
> | **AStockEvent Feed**（事件结构化） | 13+ 类公告结构化事件 Feed | GitHub 2026-06-13 | NLP 管道工程化候选（**待补**） |
>
> **施工优先级**：dReport（年化超额 4.88%）与 Jump on PEAD（IC 10.96%）有 10 年/5 日窗口实证，**优先级最高**，可作为 NLP 管道（[ARCH-NLP-PIPELINE-001](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)）未就绪前的数值 alpha 补充（与 ORJ 同属降级算法）。隔夜趋势与 ORJ 正交可叠加（事件日 ORJ>3% + 近 20 日隔夜趋势为正 = 强信号叠加）。AStockEvent 是 NLP 管道的工程化落地候选，13 类比 §2.3 四类粗分类更细，可作 Janus-Q 10 类细分类的 A 股本土化映射。
>
> **与 §2.4 PEAD 衰退根因的协同**：[20 §2.4 v1.4.3](20_first_batch_strategies.md) 引 Subrahmanyam (UCLA) 2026-03 实证——2000 年后 all-but-microcaps 无 PEAD 证据，主因是"盈余信息含量下降"。六因子矩阵正是对此的应对：① PEAD 聚焦"信息含量高"事件类（并购重组>业绩预告>政策受益）；② SUE.txt 文本惊喜比数值 SUE 更有 alpha（捕捉信息含量而非数字）；③ dReport 提前披露本身是信息含量信号（业绩好才提前披露）。登记为 §6 待裁定（事件类），G10 校准六因子矩阵权重。

- **BM-SEL-11 知识图谱增强（待就绪）**：复用 [BM-SEL-11 知识图谱与因果推演](../battle_map/battle_map_05_stock_selection.md)（design）的传导链 + 因子区分。知识图谱就绪后，可升级为 [LLM 增强动态金融知识图谱（arXiv 2607.10932, 2026-07）](https://arxiv.org/pdf/2607.10932) 范式——LLM 将非结构化文档转为结构化经济状态变化事件 + 提取实体间关系构建动态图谱 + 社区感知信号传播（λ_in > λ_out，事件信号在经济社区内传播强于跨社区）。其 Community Information Surprise（CIS）与 Propagated Information Surprise（PIS）因子在模拟中 rank IC 与 long-short Sharpe 均优于纯情绪/直接事件信号（Fama-MacBeth t-stat ≈ 3.7）。**此为 BM-SEL-11 的 2026 最新对标方向**
- **BM-SEL-19 开通条件**：事件数据源 + 知识图谱 + NLP 就绪（见漏斗 6 件套③）。**未开通则跳过本层，第三层（精筛）直接进第五层**——降级不阻塞，符合 AI 开发故障隔离纪律
- **异动识别器（需新建）**：参考 [国盛证券异动雷达 2026-03](http://stock.finance.sina.com.cn/stock/view/paper.php?autocallup=no&isfromsina=no&reportid=826626291912&symbol=sh000001) 方法——个股与基准指数分钟序列价格/成交量相关系数 <0 触发"异动"，叠加超额收益方向判定上涨/下跌异动。实证（2016-2026 中证800）：异动雷达综合信号通道策略年化超额 7.51%、IR 2.48；叠加负向筛选剔除后 9.77%、IR 2.92。可与其他事件信号（业绩盈余惊喜、量价信号）结合提升触发样本收益

**进出场触发算法（首版）**：

```python
# ── 入场触发 ──
def should_enter(event, current_position):
    """事件触发后是否开仓/加仓"""
    if market_event_integrator.current_mode == MarketMode.EMERGENCY:
        return False  # 熔断期停止开仓（§2.5 降级协同）
    score = compute_event_score(event)  # 上式
    if abs(score) < 0.2:
        return False  # 噪声
    if score > 0 and current_position == 0:
        return True   # 利好事件 + 空仓 → 开多
    if score < 0 and current_position > 0:
        return "EXIT"  # 利空事件 + 有持仓 → 退出信号
    return False

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

**施工算法补全（v1.7.0，2026-08-10 审计 should_enter/should_exit 被调用未定义的辅助函数）**：上述 `should_enter` / `should_exit` / `should_enter_with_confirmation` 调用了 5 项辅助函数/数据结构但未给出定义，补全后进出场触发算法施工闭环：

```python
# ══ 施工算法补全：should_enter/should_exit 调用但未定义的 5 项辅助函数与数据结构 ══

# ── ① event_score 单因子函数化（首版内联公式 §2.5 L215-222 封装为函数）──
def event_score_single_factor(event):
    """首版单因子事件影响评分（并购/政策/突发/IPO/地缘 五类通用）。
    
    知识图谱未就绪时的简化版。event_score ∈ [-1.5, +1.5]，正→入池做多候选，负→剔除/回避。
    阈值 |event_score| < 0.2 → 无信号（噪声），不动作。
    """
    event_class_weight = {
        "earnings": 1.0, "ma": 1.2, "policy": 0.8,
        "surprise": 1.5, "ipo": 1.3, "geopolitical": 1.4,  # §2.5 v1.6.0 补 IPO/地缘权重
    }
    return (
        event_class_weight.get(event.class_, 1.0)
        * event.surprise_direction              # +1 利好 / -1 利空 / 0 中性
        * event.sentiment_score                  # NLP 情绪分数 [-1, +1]（#ARCH-NLP-PIPELINE-001）
        * event.decay_stage_factor               # rising=1.0 / decay=0.5 / post-decay=0.2
        * event.extreme_reaction_modifier        # |reaction|>3% → 0.3（§2.4 PEAD Inversion 极端反转修正）/ 否则 1.0
    )

# ── ② compute_event_score 调度函数（按事件类选择单因子/双因子评分）──
def compute_event_score(event):
    """事件影响评分调度器：业绩类→SUE+EAR 双因子，其他五类→首版单因子。
    
    should_enter / should_enter_with_confirmation 统一调用本函数（不直接调单/双因子），
    便于事件类扩展时单点修改调度逻辑。
    """
    if event.class_ == "earnings":  # 业绩类有标准化"预期"概念，用双因子
        return event_score_dual_factor(event)   # §2.5 v1.2.0 SUE+EAR，r=0.004 近正交
    return event_score_single_factor(event)     # 并购/政策/突发/IPO/地缘 无标准化预期，沿用单因子

# ── ③ decay_exit_window 数据结构（§2.4 衰减曲线表 rising+decay 总长 = 持仓天数上限）──
decay_exit_window: dict[str, int] = {
    "earnings":     10,   # 业绩：rising 5 + decay 5（PEAD 漂移 5-10 日，Foster 1977 / Bernard & Thomas 1989）
    "ma":           15,   # 并购：rising 7 + decay 8（信息消化慢于业绩）
    "policy":       20,   # 政策：rising 10 + decay 10（政策传导链长于并购）
    "surprise":      5,   # 突发：rising 2 + decay 3（快进快出，情绪脉冲）
    "ipo":          15,   # IPO：上市后 day1-5 虹吸期 + day6-15 衰减（§2.5a IPO 虹吸效应）
    "geopolitical": 25,   # 地缘：rising 5-15 远长于业绩/并购（§2.4 衰减曲线表 v1.6.0）
}

# ── ④ has_contradictory_event 反向事件检测（should_exit 第三道线 CONTRADICTION）──
def has_contradictory_event(symbol, current_direction, lookback_days=5):
    """检测近期是否有与当前持仓方向相反的事件（新利空覆盖旧利好 / 新利好覆盖旧利空）。
    
    Args:
        symbol: 标的代码
        current_direction: 当前持仓方向（+1 多；A 股不能做空故恒 +1）
        lookback_days: 回看窗口（默认 5 日，覆盖事件 rising phase 早期）
    Returns:
        bool: 存在反向事件 → True（触发 should_exit "CONTRADICTION"）
    """
    recent_events = event_store.query(
        symbol=symbol, since=trading_days_ago(lookback_days),
    )
    for ev in recent_events:
        # 反向事件：方向非中性且与持仓方向相反
        if ev.surprise_direction != 0 and ev.surprise_direction != current_direction:
            return True
    return False

# ── ⑤ has_volume_confirmation 量能确认（确认型入场 should_enter_with_confirmation 第三分支）──
def has_volume_confirmation(symbol, days=1, min_ratio=1.5):
    """确认型入场的量能确认：事件后成交量是否放大（NexusFi 2026-06 confirmation-based entry 施工化）。
    
    模糊事件（|score|<0.2 且 |reaction|≤3%）等 day1-2 量价确认再入场，避免噪声。
    
    Args:
        symbol: 标的代码
        days: 事件后经过的交易日数（day1/day2 确认窗）
        min_ratio: 最低量比阈值（默认 1.5 倍 20 日均量）
    Returns:
        bool: 量能放大 → True（确认信号有效，可入场）
    """
    recent_vol = volume_series(symbol, days=days)        # 事件后 days 日成交量序列
    baseline_vol = volume_ma(symbol, window=20)          # 20 日均量基线
    if baseline_vol <= 0:
        return False  # 基线缺失（新股/长期停牌）→ 不确认，保守不入场
    return recent_vol.mean() >= min_ratio * baseline_vol
```

> **补全说明**：① `event_score_single_factor` 把 §2.5 首版内联公式封装为函数，供 `compute_event_score` 调度；② `compute_event_score` 是 `should_enter`/`should_enter_with_confirmation` 的统一评分入口，业绩类走双因子、其他五类走单因子；③ `decay_exit_window` 是 §2.4 衰减曲线表的程序化形态，`should_exit` 第一道线 DECAY_TIMEOUT 查表；④ `has_contradictory_event` 查 `event_store` 近 5 日反向事件，支撑第三道线；⑤ `has_volume_confirmation` 是确认型入场第三分支的量能判据。5 项补全后 should_enter/should_exit/should_enter_with_confirmation 三个函数的所有被调用符号均有定义，进出场触发算法施工闭环。
>
> **⚠️ 接口契约精确化（v1.9.0 代码侧审计修正）**：`event_store` / `volume_series` / `volume_ma` / `trading_days_ago` 四者是**接口契约（待落码）而非已建函数**——v1.9.0 全仓扫描确认 `src/zephyr/` 无此四个函数定义（已有 `EventStore` 类在 `gov_audit`/`infrastructure` 域，是治理/系统事件存储，非市场事件存储，勿混用）。落码路径：市场事件存储基于 `fund_news_data` 表 + 事件分类落库（§2.3）实现 `event_store.query(symbol, since)`；`volume_series`/`volume_ma` 基于个股日K 表（pit_query PIT 查询基座，[11_d_data](../../02_domain_architecture_docs/11_d_data.md) production）一行封装；`trading_days_ago` 复用交易日历（hk_trade_calendar 同域日历设施）。**数据基座全部具备，缺的仅是这四个薄封装函数**——登记为事件驱动 sleeve 代码施工时的前置小项（工程量 < 1 天），不阻塞设计闭环

**多层架构对标（2026 最新实践）**：[Closelook Pattern Engine 2026-04](https://closelook.net/reports/post-earnings-drift/) 采用三层递进架构——①regime 层（当前市场态是否支持 drift）→ ②trend 层（个股趋势是否支持延续）→ ③pattern 层（事件惊喜幅度是否足够）。事件驱动 sleeve 的多层协同与此一致：regime 节流（[30 §2.2](30_multi_strategy_concurrency.md) Shrinkage）→ BM-SEL-19 漏斗（trend+pattern）→ event_score（pattern 精度）。Closelook 实证：top quintile earnings surprise 相对 bottom quintile 年化超额 ~13%。

**五层事件驱动架构映射（v1.2.0 新增）**：[NexusFi 2026-06 生产级事件驱动五层架构](https://nexusfi.com/a/automation/event-driven-trading-automation)（摄取→标准化→信号→执行→独立风控）与本系统已有模块一一对应，验证架构完整性：

| NexusFi 五层 | 职责 | 本系统对应模块 | 状态 |
|---|---|---|---|
| ① 事件摄取 | 消费日历/API/新闻流，区分计划事件 vs 突发 | `news_collector` + `eastmoney_news_provider`/`cls_provider`/`rss_provider` + 公告源 | production |
| ② 标准化 | 时间戳归一/去重/实体识别/严重度评分 | `news_dedup` + `corporate_action_processor`（公司行动归一）+ NLP 实体识别（#ARCH-NLP-PIPELINE-001） | production + 在建 |
| ③ 信号生成 | 惊喜分计算/情绪分类/置信度评分 | event_score（§2.5）+ sentiment_score（NLP）+ 异动识别器 | design |
| ④ 执行 | 事件感知订单路由/预挂单/部分成交管理 | [40_execution_broker](40_execution_broker.md) + [41_buy_flow](41_buy_flow.md)/[42_sell_flow](42_sell_flow.md) | active |
| ⑤ 独立风控 | **独立于策略逻辑**——仓位/价差/波动/单事件亏损限额 | FirmRiskAggregator（[MOD-POS-021](../../../03_modules/_domain_position/firm_risk_aggregator/blueprint.md)）+ drawdown Protocol（[G16](35_drawdown_protocol_impl.md)）+ VaR/ES（[G17](36_var_es_monitoring.md)） | active |

**关键纪律**（NexusFi 警告）：风控层须**独立于策略代码路径**——策略与风控共享决策路径时，策略 bug 会禁用本应遏制它的风控。本系统 Model A 的 firm 层独立于 sleeve（[30 §2.1](30_multi_strategy_concurrency.md) 独立账本+firm 聚合），天然满足此纪律。事件驱动 sleeve 的 EMERGENCY 模式停止开仓（§2.5）是 sleeve 读风控层信号，非风控层依赖 sleeve——方向正确。

**与已有模块的降级协同**：
- `corporate_action_processor`（MOD-TRADING-004）的除权除息事件须被事件驱动 sleeve 消费——避免在除权日把机械持仓调整误判为"价格异动"（除权缺口会触发误异动）
- `market_event_integrator`（MOD-FEEDBACK_LOOP，production）处理的是熔断/FOMC/节假日模式切换（FLE 行为），**不产生 alpha**，但事件驱动 sleeve 须读其 EMERGENCY 模式——熔断期停止事件驱动开仓（与 [G18 流动性危机](37_liquidity_crisis_protocol.md) 协同）

```python
def detect_anomaly(symbol, intraday_returns, benchmark_returns, window=20, corr_threshold=0.0, excess_threshold=0.03):
    """异动识别器（国盛证券异动雷达方法施工化）
    
    判据：个股与基准指数分钟序列相关系数<0（脱离同向）+ 超额收益方向显著
    输入：
      intraday_returns: 个股分钟收益率序列
      benchmark_returns: 基准指数分钟收益率序列（如沪深300/中证500）
      window: 滚动窗口（分钟数，默认20=半小时）
      corr_threshold: 相关系数阈值（<0 触发，国盛证券异动雷达方法）
      excess_threshold: 超额收益阈值（3%）
    """
    import numpy as np
    # 1. 滚动相关系数
    rolling_corr = np.array([
        np.corrcoef(intraday_returns[i-window:i], 
                    benchmark_returns[i-window:i])[0, 1]
        for i in range(window, len(intraday_returns))
    ])
    # 2. 超额收益
    excess_return = np.cumprod(1 + intraday_returns) / np.cumprod(1 + benchmark_returns) - 1
    # 3. 异动判定：相关系数<0（脱离同向）+ 超额收益方向显著
    is_anomaly = (rolling_corr[-1] < corr_threshold) and (abs(excess_return[-1]) > excess_threshold)
    anomaly_type = "positive" if excess_return[-1] > 0 else "negative"
    return {
        "is_anomaly": is_anomaly,
        "anomaly_type": anomaly_type,  # positive=异动上涨, negative=异动下跌
        "excess_return": excess_return[-1],
        "rolling_corr": rolling_corr[-1],
    }
```

**为何用相关系数<0 而非固定涨幅阈值**：固定涨幅阈值（如日内>5%）忽略大盘联动——大盘涨 3% 时个股涨 5% 只是跟涨非异动。相关系数<0 判定"个股与基准脱钩"，才是真正的异动信号。国盛证券异动雷达实证此方法在 A 股 2023-2026 样本上捕获了 78% 的重大事件前异动。A 股参数（窗口/阈值/基准选择）需 G23 回测校准，登记 §5 暂缓项 3。

### 2.5a IPO 虹吸效应量化算法（v1.6.0 新增——施工环节算法补全）

> **缺口背景**：final_report_0724 实证 2026-07-27 长鑫科技（688825）科创板上市（募资 579-666 亿，科创板史上最大 IPO），可能吸金 500 亿+，对存量板块短期形成"虹吸效应"→ 07-24~26 是最佳建仓窗口，07-27 前完成主仓位布局+保留 25% 现金。此前 §2.3 事件分类无 IPO 类，§2.5 事件→选股映射无虹吸效应算法，[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) §3.2 日频流动性监控无 IPO 流动性预抽离预警。

**算法 1：IPO 虹吸系数（siphon coefficient）**

```python
def compute_ipo_siphon_coefficient(ipo_event, market_total_volume_20d):
    """计算 IPO 上市日对存量板块的流动性分流系数

    Returns:
        siphon_ratio: float, IPO 募资额 / 全市场 20 日均成交额
        siphon_level: str, "NEGLIGIBLE" / "MODERATE" / "SEVERE" / "EXTREME"
    """
    # 募资规模（亿元）
    raise_amount = ipo_event.raise_amount  # 如长鑫科技 579-666 亿

    # 全市场 20 日均成交额（亿元）
    market_avg_volume = market_total_volume_20d  # 如 A 股日均 ~27000 亿

    # 虹吸系数 = 募资额 / 市场日均成交额
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
    """IPO 虹吸效应驱动的仓位调整

    final_report 实证策略：
    - 上市前 3-5 天：完成主仓位布局（抢在虹吸前建仓）
    - 上市前 1 天：保留 ≥25% 现金作为虹吸期弹药
    - 上市后 day 1-5：存量板块降仓避险（虹吸峰值期）
    - 上市后 day 5+：虹吸衰减，恢复正常仓位
    """
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

**与 [37_liquidity_crisis_protocol §3.2](37_liquidity_crisis_protocol.md) 的联动**：IPO 虹吸是**前瞻性**流动性预警（上市日前已知），不同于 Amihud/spread 的事后检测。37 号 §3.2 日频结构性流动性监控新增"IPO 流动性抽离预警"维度——基于未来 N 日 IPO 募资规模/全市场成交额比值，提前调整仓位上限。两者互补：37 号负责"检测+响应"，26 号负责"alpha 方向+仓位策略"。

**数据源**：IPO 上市日历/募资规模来自 `akshare_provider`（`stock_ipo_info` 接口，production），provider 清单见 [11_d_data](../../02_domain_architecture_docs/11_d_data.md)。前 5 日无涨跌幅限制是科创板/创业板规则硬编码。

**进行时案例（v1.9.0 补，2026-08-11 实盘）**：宇树科技（"人形机器人第一股"）科创板 IPO 申购——[2026-08-10 披露网上中签率 0.018% 创科创板历史新低，978 万户申购、有效申购倍数 8288 倍](https://cbgc.scol.com.cn/news/7840749)；同周创业板新股超纯应材上市首日盘中涨 740%。机器人板块 2026-08-11 午后直线拉升（巨轮智能 1 分钟涨停），印证 IPO 事件对**存量同题材板块**的双向效应：申购期资金分流（虹吸）+ 上市前题材预热（板块异动）——`compute_ipo_siphon_coefficient` 的输入应包含"申购倍数/中签率"作为市场关注度代理变量（募资额固定时，申购热度决定实际资金冻结规模），登记为 §5 暂缓项 8 候选增强

**注意**：虹吸态概念在 [22_sector_rotation_spec §3.1⑤](22_sector_rotation_spec.md) 已存在，但那是**板块间虹吸**（强势板块吸金致其余缺血），非 IPO 驱动的**全市场流动性虹吸**——两者机制不同。IPO 虹吸是**事件型、全局性、可预知的**流动性抽离，板块间虹吸是**持续性、局部性、事后才能检测的**资金迁移。

### 2.5b 地缘/宏观事件→板块受益传导链（v1.6.0 新增——施工环节算法补全）

> **缺口背景**：final_report_0724 核心逻辑"美伊战争→周期资源股（铜/铝/黄金/油气）是主线"这种"地缘事件→特定板块 alpha 方向"的映射算法此前完全缺失。§2.3 事件分类无地缘类，地缘仅在 [32_firm_risk_aggregator](32_firm_risk_aggregator.md)（RMATS 地缘压力测试）和 [10_regime_detector_spec](10_regime_detector_spec.md)（D-SIGNAL-68 overlay）作风控节流，非选股 alpha。

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
    """地缘事件→受益/受害板块映射

    Args:
        event_nlp_tag: NLP 管道产出的事件标签（如 "middle_east_conflict"）
        sentiment_score: 情绪分数 [-1, +1]

    Returns:
        beneficiary_sectors: list[str], 受益板块
        victim_sectors: list[str], 受损板块
        event_score: float, 地缘事件影响评分
    """
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

**与 NLP 管道协同**（§2.7）：地缘事件多来自海外 RSS（BBC/CNBC/NYT/Guardian/Bloomberg 已 production，见 §2.1 事件源表）。NLP 管道（#ARCH-NLP-PIPELINE-001）须产出 `event_nlp_tag`（映射到 `GEOPOLITICAL_SECTOR_MAP` 的 key）+ `sentiment_score`。首版用**规则匹配**（关键词→tag）降级——如 RSS 新闻含"Iran/Israel/Hormuz/红海"→`middle_east_conflict`；含"tariff/export ban/entity list"→`trade_war_escalation`。NLP 管道就绪后升级为语义分类。

**2026 研究支撑**：
- [Sinong Xiao 2026 南京理工大学](https://www.atlantis-press.com/proceedings/edms-2026/)：A 股资金流→收益的**四重并行中介模型**（投资者情绪/市场流动性溢价/信息纳入/股价非同步性），**牛/熊 regime 下传导机制显著异质**——地缘驱动的资源股主线属"结构性 regime 切换"非"一次性冲击"，故 rising phase 远长于离散事件
- [arXiv:2607.27063](https://arxiv.org/abs/2607.27063)（Weng 2026-07-30）：A 股羊群/动量/反转的 agent-based 网络模型，地缘事件下的信息扩散→羊群效应→板块传导链有理论支撑
- [南京大学 2026 regime-dependent 行业轮动](https://doi.org/10.2991/978-94-6239-699-9_51)：4-regime 市场状态分类（20 日波动率×20 日轮动速度）+ regime-dependent risk parity——为地缘事件下板块轮动提供可实施架构

**与风控层的边界**：地缘事件在本 sleeve 作**选股 alpha**（买受益板块、卖受损板块）；在 [32_firm_risk_aggregator](32_firm_risk_aggregator.md) 作**风控压力测试**（RMATS 地缘压力测试，Millennium/Point72 各亏 ~$1.5B 的"diversification illusion"教训）；在 [10_regime_detector_spec](10_regime_detector_spec.md) D-SIGNAL-68 作**regime 节流**（地缘风险→降仓位上限）。三层正交：alpha 层买方向、风控层测压力、regime 层节流。

### 2.6 换手率（讨论要点⑤）

> 裁定：**继承 20/30 号已定值，convergence_window = 2-3 天**。事件触发不定期，持仓以 rising phase（2-5 天）为主，decay phase 兜底退出。

- convergence_window = 2-3 天（[30 §6.4](30_multi_strategy_concurrency.md)，已定；待首批策略实盘后校准）
- BudgetChangeHandler 三级升级（[G14](33_budget_change_handler.md)）：事件驱动属中换手，Tier 1+2 通常 2-3 天自然收敛，Tier 3 兜底防死扛（[30 §2.4](30_multi_strategy_concurrency.md)）
- 持仓周期 2-10 天（视事件类与衰减阶段，见 §2.4 衰减表）

### 2.7 news_data 多源情绪接入（讨论要点⑥）

> 裁定：**复用已建多源 news_data + NLP 管道，不新建情绪源**。情绪分数作为事件信号的一个维度（冲击方向+强度辅助），非独立 alpha。CAND-AISA-001 待四问评估。

**已建多源 news_data（production，非新建）**：

| 数据源 | 模块 | 性质 | 状态 |
|---|---|---|---|
| 东方财富 | `eastmoney_news_provider` | 国内财经新闻 | production |
| 财联社 | `cls_provider` | 国内快讯 | production |
| 海外 RSS | `rss_provider`（BBC/CNBC/NYT/Guardian/Bloomberg） | 海外财经新闻 | production |
| ClickHouse | `news_collector`（MOD-DATA-NEWS-001）→ `fund_news_data` 表 | PIT 严格查询 | production（[11_d_data](../../02_domain_architecture_docs/11_d_data.md)） |
| 去重 | `news_dedup` | 跨源去重 | production |

**NLP 情感管道（在建，复用）**：
- [#ARCH-NLP-PIPELINE-001](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)（2026-08-07）：工程范围 `news_collector.py` / `nlp_inference.py` / `sentiment_aggregator.py`。当前为 regime S2 复苏确认服务（`bad_news_flat ≥ 40` 指标），Phase 0 完成（ml-train 依赖 + Qwen2.5-7B 权重），Phase 1 进行中
- **复用裁定**：事件驱动 sleeve 复用同一 NLP 管道输出——情绪分数作为事件信号维度（事件类×冲击方向×情绪分数→事件影响评分）。NLP 管道为 regime S2 建设的"副产物"天然可服务事件驱动 alpha，避免重复造轮子
- **能力差距（开放问题）**：regime S2 只需 `bad_news_flat`（利空情绪计数），事件驱动需要**事件类型分类 + 情绪方向 + 关联股票**（更接近 [Janus-Q](https://arxiv.org/html/2602.19919v2) 的 10 类 + sentiment label）。此差距是否需扩展 NLP 管道 scope，登记为开放问题（§7-②）

**2026 最新实证支撑 NLP 复用裁定**：
- **PEAD.txt 文本惊喜 > 数值惊喜**（§2.4 已引）：费城联储论文证明纯文本 SUE 产生 2 倍于数值 PEAD 的漂移，且数值 PEAD 已近消失而文本漂移仍在——**NLP 文本信号是事件驱动 alpha 的更优来源**
- **事件感知情绪因子正交性**：[Event-Aware Sentiment Factors（arXiv 2508.07408, 2025-08）](https://arxiv.org/html/2508.07408v1/) 用 LLM 对高情绪强度金融推文做多标签事件分类，对齐 1-7 日 forward returns。发现：某些事件类（如"rumor/speculation"）是**强逆向指标**（Sharpe 低至 -0.38，IC > 0.05，95% 显著），且事件因子预测力**正交于市场 beta**——支撑事件驱动 alpha 与 regime 正交的架构裁定
- **LLM 财报电话会议分析**：[Lopez-Lira & Tang 2026](https://marketmaker.cc/en/blog/post/llm-alpha-mining-earnings-calls/) 证明通用 LLM 对新闻标题的评估可预测次日收益（~90% 方向命中率），尤其对小盘股和负面新闻；[FinCall-Surprise（arXiv 2510.03965）](https://arxiv.org/html/2510.03965v1/) 进一步引入多模态（文本+音频+PPT）——**音频语调揭示管理层信心/不确定性**（纯文本转录丢失此信号）。首版仅用文本（#ARCH-NLP-PIPELINE-001 范围），多模态登记为远期增强
- **LLM 金融预测综述**：[The New Quant（arXiv 2510.05533, 2025-10）](https://arxiv.org/html/2510.05533v1/) 综述 50+ 研究，提出任务分类法：情绪/事件提取→数值推理→多模态→RAG→时序提示→agentic 系统。事件驱动 sleeve 的 NLP 管道（事件分类+情绪方向）对应其"情绪/事件提取"层，未来可沿此分类法演进
- **跨源情绪集成（v1.9.0 补，多源 news_data 的组合方法论）**：[RavenPack × Financial Times 2026-03](https://www.ravenpack.com/research/unlocking-alpha-in-g7-currency-markets-with-financial-times) 跨源情绪集成实证——两独立新闻源（RavenPack Core + FT）平均秩相关仅 10-14%（真正交），经 cross-validated ensemble + tanh 软投票（强化跨源一致信号、压制低置信信号）后 IR 0.48→0.81、年化超额 +108bps、双周价差 ~260bps。**对本项目含义**：东财/财联社/RSS 三源同样异质（国内媒体/快讯/海外），`sentiment_aggregator`（待落盘，§1.4）落码时应采用**跨源一致性投票**而非简单均值——仅当 ≥2 源情绪方向一致时才输出强 sentiment_score，单源孤证降级为弱信号。这是 §2.7"复用多源"裁定的组合层方法论补全
- **情绪分类≠截面 alpha 的又一独立印证（v1.9.0 补）**：[Burchi & Regni, *Cogent Economics & Finance* 2026-07](https://www.tandfonline.com/doi/full/10.1080/23322039.2026.2703376) 用 BERTweet/RoBERTa/FinBERT 对 25 只大盘股推文做情绪→交易信号：**方向准确率接近随机，但信号能捕捉大幅波动**从而改善风险调整收益——"分类指标与经济价值的鸿沟"与 §2.7 QLoRA 负结果（F1 0.88 vs rank IC 0.0143 不显著）互为印证：情绪信号的价值在**事件方向触发+波动捕捉**，不在截面排序

> **⚠️ QLoRA LLM 情绪 OOS 经济性弱警示（v1.5.0 补，2026-08-04 最新负结果——反平衡上述正面实证）**：[QLoRA Benchmark（Luo et al., arXiv:2608.04200, 2026-08-04）](https://arxiv.org/html/2608.04200v1) 在五大金融文本数据集上对比 TF-IDF NB / FinBERT / Financial-RoBERTa / zero-shot Qwen2.5-7B / QLoRA 微调 Qwen2.5-7B·LLaMA3-8B·Mistral-7B。**分类性能强**：Mistral-7B QLoRA 准确率 0.8840、macro-F1 0.8771（QLoRA 将 Qwen2.5 的 F1 从 0.7274 提升至 0.8615）。**但 OOS 经济性弱**：2019 Benzinga S&P 100 样本外评估，所有 7 模型 1 日 rank IC 均为正但极小（最大 FinBERT 0.0143），**28 个模型×期限组合经 False Discovery Rate 多重检验后无统计显著**。
>
> **核心警示**：**语言分类性能 ≠ 收益可预测性**——LLM 情绪分类 F1 高达 0.88，但 OOS 截面选股 rank IC 仅 0.0143 且不显著。这与 [13 号 §2.1 P1-E3 NLP 管道定位调整](13_regime_phase3_engineering_plan.md)（"NLP 信号应定位为 regime/事件输入而非独立 alpha 源"）一致——NLP 情绪信号不应作为独立选股 alpha，应定位为：
> - **事件触发器**（§2.2 事件源）：LLM 识别"事件类型+情绪方向"触发事件驱动 pipeline，而非用情绪分数做截面排序
> - **regime 文本交叉验证器**（[13 号 §2.1 Text-Enhanced Regime](13_regime_phase3_engineering_plan.md)）：HMM 检测 regime shift 候选 → LLM 文本确认/否决，F1=0.82
> - **PEAD.txt 文本惊喜**（§2.4）：文本 SUE 产生 2× 数值 PEAD 漂移——但这是"事件级文本信号"非"情绪分数截面排序"，与 QLoRA 负结果不矛盾（一个是事件触发，一个是截面 alpha）
>
> **对本项目 §2.7 的施工启示**：① NLP 管道（#ARCH-NLP-PIPELINE-001）的 sentiment_score 不应直接进 event_score 截面排序权重（QLoRA 实证 OOS rank IC 0.0143 不显著）；② sentiment_score 应作**事件方向判定**（利好/利空/中性三分类触发）+ **regime 确认**（bad_news_flat 计数），而非截面打分；③ PEAD.txt 文本惊喜（§2.4）是"事件级文本 alpha"，与 QLoRA 负结果正交——前者是事件触发型，后者是截面排序型，本项目应采前者。登记为 §6 待定问题（NLP 信号定位类），与 13 号 P1-E3 NLP 管道定位调整闭合

> **🔧 Hybrid Sentiment "Data Funnel" 双阶段架构（v1.5.2 补，2026-08 最新正面工程化实证——与 QLoRA 负结果互补）**：[Stübinger & Wöhner, *AI* 2026, 7(4):138, "Hybrid Sentiment Analysis in Financial Markets: Multi-Stage LLM Integration for Market-Neutral Alpha Generation"](https://www.mdpi.com/2673-2688/7/4/138) 提出"小模型高吞吐筛选 + 大模型深度验证"双阶段 Data Funnel 架构——**阶段 1 FinBERT 筛选**：900 万数据点经 FinBERT 高吞吐量打分（成本低、覆盖广），仅保留高情绪强度子集；**阶段 2 Gemini 深度验证**：上下文推理+事件级信号提取（成本高、精度高），将"噪声情绪"升级为"事件级 alpha 信号"。
>
> **16 年实证（2010-2025）**：51.02% 年化净收益 / Sharpe 1.06 / Sortino 2.61 / FZ score 0.431 / maxDD 17.29%，多空对冲组合 market-neutral。**关键洞察**：单阶段 LLM（QLoRA 负结果）受"分类性能好 ≠ 收益可预测性"制约，双阶段 Data Funnel 通过"先筛选信号强度、再验证事件语义"两步分离噪声，将 sentiment_score 从"截面排序"重构为"事件级 alpha 触发"——**与本项目 §2.7 NLP 管道定位（事件方向触发+regime 确认，非截面 alpha）高度一致**。
>
> **对本项目 §2.7 的工程化启示**：① #ARCH-NLP-PIPELINE-001 现有 `nlp_inference.py`（Qwen2.5-7B 单阶段）远期可演进为双阶段 Data Funnel——FinBERT/小模型作阶段 1 高吞吐预筛（事件强度评分+方向初判），Qwen2.5-7B 作阶段 2 事件语义验证（事件类型+关联股票+冲击幅度），降低大模型推理成本同时提升信噪比；② 双阶段架构与 §2.4 PEAD.txt 文本惊喜互补——阶段 2 可输出"事件级文本 SUE"作为 PEAD 漂移触发器；③ 登记为远期候选（CAND 待定），MVP 阶段维持单阶段 Qwen2.5-7B，待事件驱动 sleeve 实盘 6-12 月后评估是否升级双阶段。**施工算法完整性结论**：26 号 §2.7 NLP 管道施工流程算法闭环，Data Funnel 是远期工程化增强非 MVP 必需

**CAND-AISA-001 AI 舆情分析器（candidate，待四问评估）**：
- 数据流：新闻/公告/研报 → [AI 舆情分析] → 舆情分数信号
- **开放风险（候选库已登记）**："若 TRAPE AI 可替代则建模块属过度工程"
- **裁定**：首版**不自建独立 AI 舆情模块**——复用 #ARCH-NLP-PIPELINE-001 管道 + `market_sentiment_analyzer`（BM-SEL-03-A，production）。CAND-AISA-001 的四问评估留给 [G28 生命周期](61_lifecycle_multi_ai.md) 统一裁定

## 3. 考虑过的替代方案

### 3.1 自建独立事件数据源与选股 pipeline —— 拒绝
- **拒绝理由**：多源 news_data 已 production（Eastmoney/CLS/RSS）、`news_collector` 已建、NLP 管道在建（#ARCH-NLP-PIPELINE-001）、BM-SEL-19 事件漏斗已 design（MOD-SIG-049）。自建等于重复造轮子，违反"派生产物复用"与 charter 约束五少而精
- **处置**：复用全部已有基础设施，事件驱动 sleeve 只新建"异动识别器"（§2.5）与"事件影响评分"（首版简化版）两个 sleeve 内部组件

### 3.2 首版即引入 Hawkes 自激发建模 —— 拒绝（暂缓）
- **拒绝理由**：Hawkes 建模是研究前沿，参数估计（μ/α/β + branching ratio）需充分事件样本与校准带宽；首版经验衰减曲线已能承载 rising/decay 两阶段持仓纪律。Hawkes 的 branching ratio 监控更适合 firm 层系统性风险（G17/G18），非 sleeve alpha
- **处置**：登记为暂缓前沿（§6 待裁定-2），首版用经验衰减曲线

### 3.3 首版即引入 Janus-Q 10 类细分类 + 端到端 LLM 决策 —— 拒绝（暂缓）
- **拒绝理由**：[Janus-Q](https://arxiv.org/html/2602.19919v2) 将事件从辅助信号升为主决策单元（LLM + 分层门控奖励建模），需 62,400 篇标注语料 + 模型微调。个人+AI 项目无此标注带宽，首版引入属过度工程
- **处置**：首版四类粗分类 + 情绪分数维度承载；Janus-Q 范式登记为 sleeve 内部增强方向（§6 待裁定-2）

### 3.4 事件做空信号开空仓 —— 拒绝（A 股约束）
- **拒绝理由**：A 股不能做空，利空事件（如业绩暴雷、ST）只能用于"剔除已有持仓/回避入池"，不能开空仓
- **处置**：利空事件→剔除/降权；alpha 集中在事件利好方向的多头

## 4. 上限定义

### 4.1 sleeve 规模上限
- 1 个事件驱动 StrategyBook（[MOD-POS-020](../../../03_modules/_domain_position/strategy_book/blueprint.md)），独立 PnL 归因、独立风控参数、独立资金预算
- 容量中等（介于打板小与多因子大之间，具体测算待 G23 回测后校准）
- 与打板、多因子并列，受 firm 层 FirmRiskAggregator（[MOD-POS-021](../../../03_modules/_domain_position/firm_risk_aggregator/blueprint.md)）求和+裁剪

### 4.2 演进路径
- **第一阶段（立即施工）**：复用已建多源 news_data + 经验衰减曲线 + BM-SEL-19 漏斗（待开通）。NLP 管道（#ARCH-NLP-PIPELINE-001）就绪后接入情绪分数维度
- **第二阶段（sleeve 有 3-6 月实盘 PnL 后）**：上叠 RegimeMetaAllocator（[MOD-PA-007](../../../03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md)）按 PerformanceScore × Shrinkage 动态调资金占比（[30 §4.2](30_multi_strategy_concurrency.md)）
- **第三阶段（前沿增强，暂缓）**：Hawkes 自激发建模 / Janus-Q 细分类（见 §6 待裁定-2）

### 4.3 为何这是上限而非妥协
- 事件源四类（公告/新闻/龙虎榜/异动）已覆盖 A 股主要事件维度，多于四类会稀释 NLP 标注带宽
- 复用而非自建——sleeve 边界清晰（事件→候选→评分→注入漏斗），不向数据源层与漏斗层蔓延
- 与打板的相关性风险（情绪隐形驱动）是上限的真实约束——若 G07 实测相关性 >0.6，需重新审视 sleeve 组合（[20 §2.5](20_first_batch_strategies.md)）

> **过度工程审查回执（v1.9.2，2026-08-12 第 5 轮，判定基准=[system_charter §2 硬边界](../04_architecture_principles_decisions/system_charter.md)）**：
> ①**多源 news_data 是否过重（个人项目是否只需 1-2 个源）**——**裁定：不过重**。东财/财联社/RSS 三源是已 production 的存量设施（§1.4 盘点真源确认），复用存量 ≠ 新增负担；RavenPack×FT 2026-03 实证（§2.7）跨源集成 IR 0.48→0.81，多源恰是 alpha 来源而非成本。但**反向边界**：再新增社交源（微博/雪球/股吧）属过重——非结构化社交文本清洗成本高、噪声大，个人项目不扩源
> ②**Hawkes 衰减模型是否过重**——**裁定：当前形态不过重**（§2.4 经验衰减曲线承载，Hawkes 登记 §5 暂缓项 1 留给 firm 层风控）。Hawkes 若首版引入 sleeve alpha 层则过重（参数估计需充分事件样本+校准带宽，单机 64GB RAM 可算但标注/校准人力不足）——本备忘自 v1.0.0 起即拒绝首版引入，持续成立
> ③**其余重机制分布**：Janus-Q 10 类细分类（§5 暂缓项 2，62,400 篇标注带宽）、CNN 可视化盈余（§5 暂缓项 7，GPU 视觉路径）、LLM 动态知识图谱（§5 暂缓项 6）、Data Funnel 双阶段（§2.7 远期候选）——全部显式标注暂缓/远期，按审查规则"远期工程不算过度工程"予以保留

## 5. 待裁定（暂缓）

> 以下项目暂不施工，非永久禁止。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 | 责任方 |
|---|---|---|---|
| 1. Hawkes 自激发事件冲击建模 | 经验衰减曲线+极端反应修正已承载 rising/decay 纪律；Hawkes 参数估计需校准带宽，branching ratio 监控更适合 firm 层风险。MDPI 2026-08 图熵提前 7-12 天预警进一步强化留给风控层 | sleeve 有 3 月 track record + 事件样本充分（>1000 事件）+ firm 层风控（G17/G18）评估认为需要事件聚类监控 | G10 sleeve owner + G17/G18 |
| 2. Janus-Q 10 类细分类 + 端到端 LLM 决策 | 需 62,400 篇标注语料 + 模型微调，个人+AI 项目无此带宽；首版四类粗分类+情绪分数已承载 | NLP 管道（#ARCH-NLP-PIPELINE-001）成熟 + 标注带宽获得（如 TRAPE AI 运行时可自动标注） | G10 sleeve owner + G28 |
| 3. 异动识别器算法定型 | 国盛证券异动雷达方法（相关系数+超额方向）已实证有效，但 A 股参数（窗口/阈值/基准）需 G23 回测校准 | G23 回测框架对接就绪 + 历史异动样本可回测 | G10 + G23 |
| 4. 事件衰减曲线参数按事件类校准 | 初拟半衰期表（§2.4）需实盘/回测验证；衰减速度 regime-dependent 需后验 | sleeve 有 3 月 track record + PerformanceScore 分 regime 校准 | G10 + G07 |
| 5. 极端反应反转（PEAD Inversion）A 股适配 | Vortex 2026-05 实证基于 mega-cap US tech，A 股大盘/小盘信息扩散速度不同需验证；3% 阈值可能 A 股不适配 | G23 回测 + A 股历史事件样本（业绩公告日 reaction 分布）可回测 | G10 + G23 |
| 6. LLM 增强动态知识图谱 + 社区传播 | arXiv 2607.10932（2026-07）CIS/PIS 因子优于纯情绪/直接事件，但需 LLM 事件抽取 + 动态图谱 + 社区检测基础设施，首版无此带宽 | BM-SEL-11 知识图谱就绪 + NLP 管道（#ARCH-NLP-PIPELINE-001）成熟 + 标注带宽 | G10 + G06（BM-SEL-11）|
| 7. CNN 可视化盈余 PEAD 预测（v1.2.0 新增） | [Garfinkel/Hribar/Hsiao 2024](https://www.biz.uiowa.edu/faculty/jgarfinkel/working/CNN.pdf) 将季度盈余转柱状图，CNN 提取漂移预测特征，OOS 显著优于传统 PEAD 预测器（RET[-1,1]）。属深度学习视觉路径，需 GPU 推理+图像化预处理，个人+AI 项目首版过重 | G23 回测框架就绪 + GPU 推理资源 + 双因子（SUE+EAR）已验证基线后评估增量 | G10 + G23 |
| 8. IPO 虹吸系数引入申购热度代理变量（v1.9.0 新增） | §2.5a `compute_ipo_siphon_coefficient` 当前仅用募资额/市场成交额；宇树科技案例（中签率 0.018%/申购 8288 倍）显示申购热度决定实际资金冻结规模，募资额固定时热度才是虹吸强度 proxy。数据源（申购倍数/中签率）需 akshare 新股申购接口验证可得性 | IPO 数据源接口字段核实 + 首个大型 IPO 实盘事件复盘后 | G10 sleeve owner |

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
| **20 号 §2.4 事件分类表述同步（四类→六类）** | 本备忘 §2.3 v1.6.0 已升级为六类（+IPO/再融资+地缘/宏观），但 [20 §2.4](20_first_batch_strategies.md) 仍写"事件分类（业绩/并购/政策/突发）"四类——跨文档版本漂移（v1.9.0 审查发现） | 待 20 号 owner 下次修订时同步为"六类（业绩/并购/政策/突发/IPO/地缘，详见 26 号 §2.3）"。按审查约束不越界改 20 号，登记于此 |
| **`sentiment_aggregator.py` 落盘时序** | §1.4 盘点：`src/zephyr/nlp/` 当前仅 `nlp_inference.py` + `__init__.py`，#ARCH-NLP-PIPELINE-001 登记的 sentiment_aggregator 未落盘 | 待 #ARCH-NLP-PIPELINE-001 Phase 1 完成；就绪前 sentiment_score 用单条推理输出降级（§2.7 已裁定非截面排序用途，不阻塞） |

## 7. 引用

### 7.1 相关设计备忘
- [20_first_batch_strategies.md](20_first_batch_strategies.md) §2.4（事件驱动 sleeve 定义，本讨论的上游裁定）
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md)（多策略并发架构总纲，Model A）
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G10（讨论框架路线图）
- [23_strategy_correlation_validation.md](23_strategy_correlation_validation.md)（G07 相关性验证，施工前必做）
- [22_sector_rotation_spec.md](22_sector_rotation_spec.md)（G06 板块轮动，事件传导链与板块异动映射）
- [33_budget_change_handler.md](33_budget_change_handler.md)（G14 三级升级，convergence_window）
- [36_var_es_monitoring.md](36_var_es_monitoring.md) / [37_liquidity_crisis_protocol.md](37_liquidity_crisis_protocol.md)（G17/G18 风控，Hawkes branching ratio 监控候选消费者）
- [61_lifecycle_multi_ai.md](61_lifecycle_multi_ai.md)（G28，CAND-AISA-001 四问评估归属）

### 7.2 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)（选股阶段）
  - BM-SEL-27：盘中实时事件处理（生产态，事件驱动 sleeve 依赖）
  - BM-SEL-19：事件驱动分布筛选（设计态，MOD-SIG-049，事件漏斗第四层）
  - BM-SEL-11：知识图谱与因果推演（设计态，事件传导链）
  - BM-SEL-05-A：机构行为分析（生产态，龙虎榜数据源）
  - BM-SEL-03-A：市场情绪分析（生产态，情绪分数基础）
  - BM-SEL-05-C：盘中买卖点分析（生产态，异动识别基础）

### 7.3 depgraph 模块与 ARCH/CAND
| 模块/议题 | ID | path / 位置 | 本讨论关系 |
|---|---|---|---|
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | sleeve 载体 |
| NewsCollector | MOD-DATA-NEWS-001 | `src/zephyr/data/news_collector.py` | 新闻数据采集（design→production） |
| CorporateActionProcessor | MOD-TRADING-004 | `src/zephyr/trading/corporate_action_processor.py` | 持仓调整事件（非 alpha，须消费防误判） |
| MarketEventIntegrator | MOD-FEEDBACK_LOOP | `src/zephyr/feedback_loop/collectors/market_event_integrator.py` | 熔断/FOMC 模式切换（EMERGENCY 时停止开仓） |
| NLP 情感管道 | #ARCH-NLP-PIPELINE-001 | `news_collector.py` / `nlp_inference.py` / `sentiment_aggregator.py` | 在建，复用为情绪分数源 |
| AI 舆情分析器（候选） | CAND-AISA-001 | 候选库 | 待四问评估（自建 vs TRAPE AI） |
| 事件漏斗 L4 | MOD-SIG-049 | BM-SEL-19 | 事件影响评分+条件PDF修正+传导链（design） |

> news_data 多源：`rss_provider.py` / `eastmoney_news_provider.py` / `cls_provider.py` / `news_dedup.py` 均为 production（见 [11_d_data](../../02_domain_architecture_docs/11_d_data.md)；v1.9.0 修正：此前误引 09_d_alt_data——该文档仅含 alt_data 域 7 个包入口，provider 真实登记在 11_d_data D_DATA 域）。

### 7.4 开源实证与 2026 行业参考
- [Janus-Q — End-to-End Event-Driven Trading（arXiv 2026-02）](https://arxiv.org/html/2602.19919v2)：LLM + 分层门控奖励建模，10 fine-grained event types + 62,400 篇标注，event-to-CAR 建模。[20 §7.5](20_first_batch_strategies.md) 已引；本讨论 §2.3/§3.3 引为细分类暂缓前沿
- [Yukka — Sentiment Decay & Source Selection（2026-05）](https://cdn.prod.website-files.com/66b4f3430903efa023fe741b/69fdded32f3d7e02f17ff3f8_Sentiment%20Decay%20&%20Source%20Selection%20in%20Global%20Equity%20Markets%20-%20White%20Paper.pdf)：情绪 IC 衰减 regime-dependent。[20 §2.4](20_first_batch_strategies.md) 已引；本讨论 §2.4 衰减曲线依据
- [Hawkes Processes for Investors（2026-02）](https://stockalpha.ai/alpha-learning/hawkes-processes-for-investors-modeling-self-exciting-volatility-bursts)：自激发点过程建模事件聚类。[20 §7.5](20_first_batch_strategies.md) 已引；本讨论 §2.4/§3.2 引为暂缓前沿
- [Beyond the Event Horizon（2025）](https://www.preprints.org/manuscript/202506.0079)：事件后 day 0-5 rising phase RVR 9.5x。[20 §2.4](20_first_batch_strategies.md) 已引；本讨论 §2.4 衰减曲线核心依据
- [国盛证券 — 异动雷达事件簇（2026-03）](http://stock.finance.sina.com.cn/stock/view/paper.php?autocallup=no&isfromsina=no&reportid=826626291912&symbol=sh000001)：A 股异动识别（相关系数+超额方向），2016-2026 中证800 通道策略年化超额 7.51%/IR 2.48，叠加负向筛选 9.77%/2.92。本讨论 §2.5 异动识别器方法来源
- [中国股市传染分析 — Hawkes 视角（arXiv 2512.08000，2025-12）](https://arxiv.org/html/2512.08000v1/)：时空 Hawkes 建模 A 股板块轮动，高活跃期延续趋势/低活跃期轮动加剧。本讨论 §2.4 Hawkes 与板块轮动契合依据（2026 新增）
- [Price Discovery 物理（arXiv 2601.11602，2026-02）](https://arxiv.org/html/2601.11602v2)：Hawkes 区分外生（新闻）vs 内生（反馈）资金流，散户流近爆炸自激发。本讨论 §2.4 事件聚类内生性依据（2026 新增）
- [Persia — Financial Contagion as Self-Exciting Point Process（2026-06）](https://proceedings.systemdynamics.org/2026/papers/P1265.pdf)：多元 Hawkes 跟踪 VIX，GFC vs COVID 不同自激发。本讨论 §2.4 firm 层风险监控候选依据（2026 新增）
- [BlackRock Hedge Fund Outlook Spring 2026](https://alternativefundinsight.com/wp-content/uploads/2026/04/blk-hedge-fund-outlook.pdf)：2026 事件驱动机会集扩大（M&A volume +54% YoY），系统性多策略捕获上升的离散度。本讨论 §1.1 事件驱动 sleeve 时代背景
- **[Vortex Capital — Mega-Cap PEAD Inversion（2026-05）](https://www.vortexcapitalgroup.com/insights/the-mega-cap-pead-inversion-when-the-reaction-is-the-trade-and-when-it-is-the-trap)**：极端事件日反应（>±3%）反转而非延续（+3%→20日-5.58%，-3%→5日+4.20%）。本讨论 §2.4 极端反应反转修正依据（v1.1.0 新增）
- **[费城联储 PEAD.txt（Meursault et al.）](https://marketmaker.cc/en/blog/post/llm-alpha-mining-earnings-calls/)**：纯文本 SUE 产生 2 倍于数值 PEAD 的漂移，数值 PEAD 已近消失而文本漂移仍在。本讨论 §2.4/§2.7 NLP 文本信号优于数值的依据（v1.1.0 新增）
- **[Event-Aware Sentiment Factors（arXiv 2508.07408, 2025-08）](https://arxiv.org/html/2508.07408v1/)**：LLM 多标签事件分类 + forward return 对齐，"rumor/speculation"类为强逆向指标（Sharpe -0.38），事件因子正交于市场 beta。本讨论 §2.7 事件因子正交性依据（v1.1.0 新增）
- **[LLM-Enhanced Dynamic Financial Knowledge Graphs（arXiv 2607.10932, 2026-07）](https://arxiv.org/pdf/2607.10932)**：LLM 事件抽取 + 动态图谱 + 社区感知信号传播，CIS/PIS 因子 t-stat≈3.7 优于纯情绪。本讨论 §2.5 BM-SEL-11 知识图谱 2026 最新对标（v1.1.0 新增）
- **[MDPI Entropy — Transfer-Entropy + Hawkes 跨境传染（2026-08-06）](https://www.mdpi.com/1099-4300/28/8/887)**：两层框架（transfer entropy + 多元 Hawkes），图熵提前 7-12 天预警峰值回撤。本讨论 §2.4 Hawkes 留给风控层最新依据（v1.1.0 新增）
- **[MetricGate — Hawkes 实操指南（2026-06）](https://metricgate.com/blogs/hawkes-self-exciting-process-r/)**：MLE 校准 μ/α/β + branching ratio + intensity→波动率 transfer function + 升级触发器。本讨论 §2.4 Hawkes 实操参考（v1.1.0 新增）
- **[Closelook — PEAD Pattern Engine（2026-04）](https://closelook.net/reports/post-earnings-drift/)**：三层递进架构（regime→trend→pattern），top/bottom quintile 年化超额 ~13%。本讨论 §2.5 多层架构对标（v1.1.0 新增）
- **[FMP — Tracking PEAD（2026-04）](https://intelligence.financialmodelingprep.com/education/other/tracking-postearnings-announcement-drift-with-fmps-market-data)**：PEAD 衰减曲线 day 9 进入平台区（exit zone）。本讨论 §2.4 业绩类衰减窗依据（v1.1.0 新增）
- **[The New Quant — LLM 金融预测综述（arXiv 2510.05533, 2025-10）](https://arxiv.org/html/2510.05533v1/)**：50+ 研究综述，任务分类法（情绪/事件提取→数值推理→多模态→RAG→agentic）。本讨论 §2.7 NLP 管道演进路径（v1.1.0 新增）
- **[FinCall-Surprise — 多模态盈余惊喜（arXiv 2510.03965, 2025-10）](https://arxiv.org/html/2510.03965v1/)**：文本+音频+PPT 多模态盈余惊喜预测，音频语调揭示管理层信心。本讨论 §2.7 多模态远期增强方向（v1.1.0 新增）
- **[Rockstead — Capturing Post-Earnings Drift: A Two-Factor Approach（2026-05）](https://rockstead.com/market-insights/capturing-post-earnings-drift-a-two-factor-approach/)**：SUE+EAR 双因子框架，两因子 r=0.004 近正交，组合 long portfolio 年化 18.50%；EAR 单因子 Q5-Q1 年化 -3.39%（反转）。本讨论 §2.5 SUE+EAR 双因子增强评分依据（v1.2.0 新增）
- **[NexusFi — Event-Driven Trading Automation Five-Layer Architecture（2026-06）](https://nexusfi.com/a/automation/event-driven-trading-automation)**：生产级事件驱动五层架构（摄取→标准化→信号→执行→独立风控），风控须独立于策略逻辑。本讨论 §2.5 五层架构映射+关键纪律依据（v1.2.0 新增）
- **[Hawkes-Driven OTC Market Making（arXiv 2608.02002, 2026-08-03）](https://arxiv.org/html/2608.02002v1)**：Volterra-Riccati 近似处理一般 Hawkes 核路径依赖，幂律 RFQ 记忆+内生 OTC 报价影响。本讨论 §2.4 Hawkes 留给风控层最新 8 月实证（v1.2.0 新增）
- **[Garfinkel/Hribar/Hsiao — Visualizing Earnings to Predict PEAD（2024）](https://www.biz.uiowa.edu/faculty/jgarfinkel/working/CNN.pdf)**：季度盈余转柱状图 CNN 提取漂移预测特征，OOS 优于传统 PEAD 预测器。本讨论 §5 暂缓项 7 CNN 可视化盈余依据（v1.2.0 新增）
- **[Griffin/McInnis/Zhao 2026 — PEAD 衰退根因](https://www.broker-forex.fr/strategie-investissement-PEAD.php)**：PEAD 衰退主因非套利加剧而是盈余"信息性"下降（小盘股盈余波动加大）。支撑 §2.4 PEAD.txt 文本>数值的转向依据（v1.2.0 新增）
- **[澎湃新闻 — 十大券商看后市 A 股超跌反弹（2026-08-10）](https://m.thepaper.cn/newsDetail_forward_33750320)**：2026-08-07 A 股深调后十大券商共识超跌反弹仍有空间，8 月中下旬中报密集期是检验窗口。本讨论 §1.1 A 股实时市场背景依据（v1.2.0 新增）
- **[Bahcivan/Dam/Gonenc — Investor Overreaction and Overnight Price Jumps（2023）](http://hulusibahcivan.com/wp-content/uploads/2023/05/New-Avenues-in-Expected-Returns_Investor-Overreaction-and-Overnight-Price-Jumps-in-US-Stock-Markets_May-2023.pdf)**：9,718 只美股隔夜跳空实证，正/负跳空后 5 日内显著反转，套利成本越低反转越大。本讨论 §2.5 ORJ 隔夜跳空信号依据（v1.3.0 新增）
- **[中国证券报 — 量化私募博弈财报季：从预期差到 AI 穿透（2026-04-24）](http://m.ce.cn/cj/gd/202604/t20260424_2925768.shtml)**：净利润断层（A 股本土化 ORJ）=财报公布后跳空上涨，预期差是核心变量非绝对增速。本讨论 §2.5 净利润断层+预期差 A 股本土化依据（v1.3.0 新增）
- **[中邮证券 — 业绩之锚7：一季报定价中习惯与"甜区"策略（2026-06-05）](https://finance.sina.com.cn/stock/stockzmt/2026-06-05/doc-iniaikau2934869.shtml)**：A 股预期差构建方法（季报用一致预期变动/年报用静态对比），一季报预期差策略 30天超额1.9%/60天2.8%，年报不定价业绩利好。本讨论 §2.5 预期差+报告期权重依据（v1.3.0 新增）
- **[EarningsWhispers — Whisper Number 69.7% 更准确（2026-08-05 更新）](https://beta.earningswhispers.com/about-whispers)**：Whisper Number=分析师最新未发表预期，比一致预期准确率高 69.7%；whisper>consensus 超 5% 时 beat 概率 ~75%。本讨论 §2.5 Whisper Number→修正动量本土化依据（v1.3.0 新增）
- **[火山引擎 — 美股夜盘 10 年回测与实时监控（2026-04-16）](https://developer.volcengine.com/articles/7629162484989394995)**：财报次日夜盘预测准确率仅 54.7%/反转概率>45%，宏观事件夜盘可信度>65%。本讨论 §2.5 ORJ 反转风险+事件类型差异化依据（v1.3.0 新增）

## 8. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G10 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active | G10 六项讨论要点逐项定型：①事件源（复用公告/新闻/龙虎榜/异动四类已建源）②事件分类（四类粗分类+Janus-Q细分类暂缓）③冲击衰减曲线（经验衰减+Hawkes暂缓，2026 新增中国股市Hawkes/Price Discovery/Persia 三实证）④事件→选股映射（复用 BM-SEL-19 漏斗+异动识别器新建）⑤换手率（继承 2-3 天）⑥多源情绪（复用已建 news_data+#ARCH-NLP-PIPELINE-001，CAND-AISA-001 待评估）。过度工程审查：多源 news_data 已 production 非过重，裁定复用不新建。登记 4 项暂缓+6 项开放问题，循环至零 |
| 2026-08-10 | 1.1.0 | 施工算法补全+2026最新实证 | ①§2.4 新增极端反应反转（PEAD Inversion）修正——Vortex 2026-05 实证极端反应(>±3%)反转而非延续，衰减曲线改为双模型（温和延续/极端反转）+ PEAD.txt 文本惊喜>数值惊喜（费城联储）②§2.4 新增 MDPI Entropy 2026-08-06 Hawkes 跨境传染（图熵提前7-12天预警）+ MetricGate 实操指南③§2.5 新增显式事件影响评分公式+进出场触发算法（三道出场线）+ LLM增强动态知识图谱社区传播(arXiv 2607.10932 CIS/PIS因子) + Closelook多层架构对标④§2.7 新增事件感知情绪因子正交性(arXiv 2508.07408)+LLM财报分析+多模态+综述⑤§7.4 新增10条2026参考。登记暂缓项4→6项。持续改进：全网搜索2026-08最新研究，补全施工流程算法缺失 |
| 2026-08-10 | 1.2.0 | 双因子评分+确认型入场+五层架构+8月实证 | ①§2.5 新增 SUE+EAR 双因子增强评分（Rockstead 2026-05 两因子 r=0.004 近正交，组合年化18.50%）——首版单因子 event_score 保留为四类通用默认，业绩类优先用双因子；升级路径 SUE→PEAD.txt 文本惊喜②§2.5 新增确认型入场模式（NexusFi 2026-06 三模式：fade/continuation/confirmation），补全 should_enter 第三分支（模糊事件等 day1-2 量价确认）③§2.5 新增五层事件驱动架构映射（摄取→标准化→信号→执行→独立风控，与已有模块一一对应）+ 风控独立于策略纪律④§2.4 新增 Hawkes-Driven OTC Market Making（arXiv 2608.02002, 2026-08-03）Volterra-Riccati 幂律记忆+内生影响⑤§1.1 新增 A 股 2026-08 实时市场背景（08-07 深调/08-10 超跌反弹共识，中报密集期=业绩事件高发窗口）⑥§5 暂缓项 6→7（新增 CNN 可视化盈余 PEAD 预测）⑦§7.4 新增7条2026-08参考。持续改进：全网搜索2026-08-08最新研究，识别选项之外更好算法（SUE+EAR双因子>单因子），补全施工流程缺失（确认型入场+五层架构映射） |
| 2026-08-10 | 1.3.0 | ORJ隔夜跳空+预期差+三因子融合 | ①§2.5 新增 ORJ（Overnight Return Jump）隔夜跳空信号——Bahcivan 2023 美股9,718只实证隔夜跳空后5日内显著反转；A 股 T+1 天然隔夜窗口，次日开盘=市场隔夜第一反应，与日内 EAR 正交②§2.5 新增净利润断层（A 股本土化 ORJ）——中国证券报 2026-04 量化私募财报季实证，净利润断层=财报后跳空上涨，是 A 股业绩超预期策略本土形态③§2.5 新增预期差+修正动量（Whisper Number 本土化）——EarningsWhispers 2026-08 Whisper 比一致预期准确率高69.7%；中邮证券 2026-06 业绩之锚7：A 股预期差构建方法（季报用一致预期变动/年报用静态对比），一季报预期差策略30天超额1.9%/60天2.8%，年报不定价业绩利好需降权④§2.5 新增三因子融合评分（SUE×EAR×ORJ + 预期差增强）——双因子→三因子，ORJ作隔夜前置预警，预期差作SUE的A股增强基准；三因子两两近正交→真分散化⑤§2.5 ORJ与PEAD Inversion协同——ORJ>3%触发极端反应反转，比等3日EAR更早预警⑥§7.4 新增5条2026参考。持续改进：识别选项之外更好算法（三因子>双因子>单因子），补全施工流程缺失（ORJ隔夜维度+预期差报告期差异化权重） |
| 2026-08-10 | 1.4.0 | SUE 预期构建方式选项之外更好算法 | 用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+持续改进不停。§2.5 新增 Zyberno 2026-08-05 seasonal random walk with drift SUE 算法——从 SEC 实际报告构建预期（Expected_EPS = EPS_(q-4) + drift），不使用分析师 consensus，**无法被 guidance management 扭曲**（管理层可引导分析师预期但无法扭曲自身历史实际报告）。与当前 consensus_eps 方案对比表（5 维度：预期来源/guidance management 风险/数据依赖/适用条件/PEAD 信号强度）。裁定：MVP 保留 consensus_eps（分析师预期数据已接入+A股有覆盖标的信号更密集），Zyberno seasonal random walk 记为 Phase 2 候选——用于小盘股无分析师覆盖+交叉验证 consensus SUE 可靠性（同向→信号增强/背离→guidance management 风险信号） |
| 2026-08-10 | 1.5.0 | 施工算法补全 + 六因子矩阵 + 异动识别器 + 吸收卖压 | §2.5 补六因子矩阵交叉引用（dReport/Jump on PEAD/隔夜趋势/AStockEvent 四项新因子，对齐 20 §2.4 v1.4.4）；§2.5 补异动识别器施工算法（相关系数<0 + 超额收益方向，国盛证券异动雷达方法施工化）；§2.4 补吸收卖压判定算法（CVD 转正 + 量能放大 + 价格企稳，PEAD Inversion 极端负反应 day2-3 确认的施工落地） | 用户要求审查施工环节流程算法缺失、选项之外更好算法 |
| 2026-08-10 | 1.5.1 | QLoRA LLM 情绪 OOS 经济性弱警示 | §2.7 补 2026-08-04 最新负结果反平衡——QLoRA Benchmark（arXiv:2608.04200）：7 模型金融情感分类 F1 高达 0.88 但 OOS 截面选股 rank IC 仅 0.0143，28 组合 FDR 校正后无显著。核心警示"语言分类性能 ≠ 收益可预测性"，NLP sentiment_score 不应直接进 event_score 截面排序，应定位为事件方向触发+regime 文本交叉验证（与 13 号 P1-E3 NLP 管道定位调整闭合） | 用户要求全网搜索 2026-08-08 最新研究+选项之外更好算法。QLoRA 负结果是 LLM 情绪信号定位的关键校准——反平衡 §2.7 既有 4 项正面实证（PEAD.txt/Event-Aware/LLM earnings/New Quant），避免 NLP 管道过拟合"分类性能好=选股 alpha 强"的幻觉 |
| 2026-08-10 | 1.5.2 | Hybrid Sentiment Data Funnel 双阶段架构 | §2.7 补 Stübinger & Wöhner, *AI* 2026, 7(4):138 "Hybrid Sentiment Analysis in Financial Markets: Multi-Stage LLM Integration for Market-Neutral Alpha Generation"——FinBERT 高吞吐筛选（900 万数据点）+ Gemini 深度验证双阶段 Data Funnel 架构，16 年实证 51.02% 年化/Sharpe 1.06/Sortino 2.61。与 QLoRA 负结果互补：单阶段 LLM 受"分类性能 ≠ 收益可预测性"制约，双阶段通过"先筛选信号强度、再验证事件语义"两步分离噪声，将 sentiment_score 从"截面排序"重构为"事件级 alpha 触发"，与本项目 NLP 管道定位（事件方向触发+regime 确认）高度一致。工程化启示：#ARCH-NLP-PIPELINE-001 远期可演进为双阶段（FinBERT 预筛+Qwen2.5-7B 验证），登记为远期候选 | 用户要求持续审查+全网搜索 2026-08 最新研究。Stübinger Data Funnel 是 QLoRA 负结果的正面工程化答案——同一 2026-08 时间窗口，一负一正形成 NLP 管道定位的完整证据链：单阶段截面排序不可行（QLoRA），双阶段事件触发可行（Data Funnel） |
| 2026-08-10 | 1.6.0 | IPO虹吸效应+地缘事件传导链+事件分类四类→六类 | ①§2.3 事件分类从四类→六类，新增 IPO/再融资（第五类）+地缘/宏观（第六类）——final_report_0724 交叉对照发现 IPO 虹吸效应和地缘→板块传导链算法完全缺失；②§2.4 衰减曲线表补 IPO（上市前3-5天布局窗/上市后day1-5虹吸期）和地缘（rising 5-15天远长于业绩/并购）；③§2.5 event_score 公式补 event_class_weight（IPO=1.3/地缘=1.4）；④新增 §2.5a IPO 虹吸效应量化算法（siphon coefficient + 仓位调整策略，与 37 号 §3.2 联动）；⑤新增 §2.5b 地缘事件→板块受益传导链（5 类地缘事件×受益/受害板块静态映射表 + NLP 管道协同 + 三层正交边界）；⑥§2.7 引用 Sinong Xiao 2026 南京理工大学资金流传导四重中介模型（牛/熊 regime 异质）+ arXiv:2607.27063 A 股羊群 agent-based 模型 + 南京大学 regime-dependent 行业轮动 | 用户要求再次审查施工环节流程算法缺失+final_report_0724 交叉对照。后台 agent 确认 26 号缺 IPO 事件类（全文搜索 IPO/虹吸零命中）+缺地缘事件类（地缘仅在 32/10 号作风控非 alpha）。两项均属施工算法缺失非设计未定型 |
| 2026-08-10 | 1.7.0 | 施工算法补全：should_enter/should_exit 被调用未定义的 5 项辅助函数与数据结构 | 用户要求持续改进。审计 §2.5 进出场触发算法发现 should_enter / should_exit / should_enter_with_confirmation 三个函数调用了 5 项辅助函数/数据结构但未给出定义，补全后施工闭环：① event_score_single_factor——首版内联公式（§2.5 L215-222）封装为函数，供 compute_event_score 调度；② compute_event_score——评分调度器，业绩类走 SUE+EAR 双因子（event_score_dual_factor）、其他五类（并购/政策/突发/IPO/地缘）走单因子，should_enter 统一调用本函数；③ decay_exit_window——§2.4 衰减曲线表程序化形态（6 类事件 rising+decay 总长 = 持仓天数上限），should_exit 第一道线 DECAY_TIMEOUT 查表；④ has_contradictory_event——查 event_store 近 5 日反向事件，支撑 should_exit 第三道线 CONTRADICTION；⑤ has_volume_confirmation——确认型入场第三分支量能判据（事件后量比≥1.5 倍 20 日均量），NexusFi 2026-06 confirmation-based entry 施工化。5 项补全后 should_enter/should_exit/should_enter_with_confirmation 所有被调用符号均有定义，event_store/volume_series/volume_ma 复用 D_FEED 域已建接口。施工算法完整性结论：进出场触发算法施工闭环，无新算法缺失 |
| 2026-08-10 | 1.7.1 | event_score_dual_factor 裸变量修复（actual_eps/consensus_eps 未定义） | 第五十五轮审查。审计 v1.7.0 新增 5 项辅助函数内部闭合性时发现 `event_score_dual_factor`（§2.5 v1.2.0 双因子，降级默认）L237 使用裸变量 `actual_eps` / `consensus_eps` 但函数签名 `event_score_dual_factor(event)` 内未定义这两个变量——而同节三因子主选版 `event_score_triple_factor`（L398-399）正确使用 `event.actual_eps` + `expectation_gap_with_revision_momentum(...)`，`expectation_gap_with_revision_momentum`（L362/367-368）正确使用 `wind_consensus_eps(symbol, event_date)`。属 v1.2.0 遗留伪代码精度缺陷，非 v1.7.0 引入。修复：L239 统一为 `sue = (event.actual_eps - wind_consensus_eps(event.symbol, event.date)) / rolling_std_surprise(event.symbol)`，与三因子版 + 预期差函数口径一致。修复后双因子降级默认版与三因子主选版 SUE 分量计算口径统一，代码施工时无双轨歧义 |
| 2026-08-10 | 1.8.0 | **龙虎榜 2026 机构信号失效校准（与 24 号 v1.8.2 同步）** | 用户再次审查要求全网搜索 2026-08-08 最新研究+施工环节算法缺失+持续改进。24 号 v1.8.2 已实证龙虎榜生态 2026 结构性变化（机构净买入次日胜率 62-68%→45.7% < 50% 随机，信号反向失效），并明确要求 26 号 §2.5 event_score 同步校准。本次补：①§2.2 新增龙虎榜事件源 2026 信号失效提示（指向 §2.5 校准）；②§2.5 新增龙虎榜 2026 机构信号失效校准块——4 维度退化表（机构净买胜率/净买率极端值/外资占比/拉萨天团退潮）+ 4 项施工建议（机构净买佐证降权/净买率 12% 硬阈值门控/席位类型差异化/数据源就绪）+ `dragon_tiger_corroboration_modifier()` 施工算法（乘法修正因子 ∈[0.7,1.2]，净买率≥12% 加分/量化席位 hard×0.7 soft×0.85）+ 与 24 号口径一致性说明（共用 dragon_tiger 表+12% 阈值+detect_quant_seat_warning 双阈值）；③§6 新增待定问题（校准参数实盘复核）。确保打板 sleeve（23-A）与事件驱动 sleeve（event_score）对龙虎榜信号解读口径一致，避免跨 sleeve 信号歧义 |
| 2026-08-12 | 1.9.0 | **已施工设施盘点节新增 + 交叉引用真源修正（通用规则 #11 审查）** | 架构审查第 1-2 轮（读现状+代码侧真源审计+回填）：①新增 §1.4「已施工设施盘点」——14 项设施逐项核对代码/schema/tasks.yaml 真源（新闻三源/news_collector/news_dedup/龙虎榜双表/corporate_action_processor/market_event_integrator EMERGENCY 落码确认/intraday_buy_sell_point_analyzer/market_sentiment_analyzer/nlp_inference/IPO stock_ipo_info），盘点结论：四类事件源数据链路全部 production，真正待新建仅异动识别器+事件影响评分两项 sleeve 内部组件；②交叉引用修正：§2.2/§2.5a/§2.7/§7.3 共 4 处误引 09_d_alt_data（该文档仅含 alt_data 域 7 个包入口，无 provider 描述）→ 改引 11_d_data（D_DATA 域，provider 真实登记处）；③§2.5 龙虎榜数据源声明精确化——双表（dragon_tiger 汇总 + dragon_tiger_seat 席位明细），席位类型字段消费自 seat 表；④同名消歧：backtest/event_driven_engine.py 是 Tick 级回测内核（做T专用），与本备忘"新闻/公告事件驱动 alpha"同名不同义，盘点节标注勿混淆；⑤§6 新增 2 项开放问题：20 号 §2.4 事件分类四类→六类跨文档漂移（不越界改 20 号，登记待同步）+ sentiment_aggregator.py 未落盘时序。⚠️ 本轮编辑在主工作区曾两次被并发 session git 操作回滚丢失，改用 session_worktree 物理隔离后重放恢复（#ARCH-GIT-CLEAN-GUARD-FIX 教训实证） |
| 2026-08-12 | 1.9.1 | **缺失环节审查补全 + 2026-08-10/11 最新研究（第 3-4 轮）** | ①§1.3 新增 T+1 事件→交易时序显式映射（盘后事件 T→T+1 开盘行动→T+2 可卖；盘中事件当日买入不可卖，should_exit holding_days>=1 隐含此约束；holding_days 计数约定；rising phase 盘后事件可捕捉窗口折损一日）——收拢散见 §1.3/§2.4/ORJ/should_exit 的 T+1 约束为单点声明；②§2.5 补全说明接口契约精确化——event_store/volume_series/volume_ma/trading_days_ago 全仓扫描确认无已定义函数（已有 EventStore 类在 gov_audit/infrastructure 域是治理事件存储勿混用），修正 v1.7.0"复用 D_FEED 域已建接口"表述为"接口契约待落码"，落码路径明确（fund_news_data+pit_query+交易日历基座全部具备，仅缺薄封装，工程量<1天）；③§2.7 新增跨源情绪集成方法论（RavenPack×FT 2026-03：两源秩相关仅10-14%真正交，tanh 软投票集成 IR 0.48→0.81/+108bps——sentiment_aggregator 落码应采跨源一致性投票非简单均值，≥2 源同向才出强信号）+ Burchi&Regni 2026-07 独立印证（情绪方向准确率近随机但捕捉大幅波动，与 QLoRA 负结果互证"分类性能≠经济价值"）；④§2.5a 新增进行时案例（宇树科技科创板 IPO 中签率 0.018% 历史新低/8288 倍申购，2026-08-11 机器人板块异动）+ §5 暂缓项 8（IPO 虹吸系数引入申购热度代理变量） |
| 2026-08-12 | 1.9.2 | **过度工程审查回执（第 5 轮）** | §4.3 新增过度工程审查回执，逐项对照 charter §2 硬边界判定：①多源 news_data 不过重——东财/财联社/RSS 是 production 存量设施非新增负担，RavenPack 跨源实证多源是 alpha 来源；反向边界明确——再新增社交源（微博/雪球/股吧）属过重不扩源；②Hawkes 当前形态不过重——经验衰减承载 sleeve 层，Hawkes 登记暂缓项 1 留 firm 层风控，若首版引入 sleeve alpha 层则过重（自 v1.0.0 起即拒绝，持续成立）；③Janus-Q/CNN 视觉/LLM 动态图谱/Data Funnel 双阶段全部显式暂缓/远期，按"远期工程不算过度工程"规则保留 |
