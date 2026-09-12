---
ttl: task_bound
---

# 另类因子数据源补充扫描（2026-09-12）

> 任务：另类因子对话负责。① 盘点与相近因子（社热/情绪/产业垂直/币圈影子）对位的可补充数据；② 全网搜索机构实践与量化社区做法，收集**免费可获取**的另类数据源。
> 前置：本报告基于 [数据分层体检报告](2026-09-12-data-layer-gap-analysis.md) §2.3（L3 ≈15%）与 P2-B 建议（低成本 web 衍生试点）展开，不与财报对话（P1-A）、研报对话（P1-B）的工作范围重叠。

---

## 0. 一页结论

1. **不缺"另类"的空架子，缺的是往 5 条在跑管线里塞同类邻居。** 项目已落地 5 条边缘另类管线（天气/生猪/人气榜/币圈影子/新闻情绪），alt_data 包 15 个模块 DORMANT 但治理件齐全（catalog/connector/compliance/health_manager）。补充策略 = **唤醒 + 复制模板**，不新造轮子。
2. **免费另类数据源里，机构与社区验证最充分、工程成本最低的一批是**：东财股吧/千股千评/雪球热度（散户情绪面）、百度指数（搜索关注度）、互动易/e互动问答（IR 文本）、电影票房/航运运价（产业垂直高频）。全部有免费接口路径，且大多可经 akshare/tushare 直连（两者均已在项目 provider 体系内）。
3. **机构实践印证**：Robeco 把另类获取归纳为"平台代理（Neudata/Eagle Alpha）+ 自采"；paperswithbacktest 把行业另类分 6 子类（web 注意度/社媒情绪/信用卡交易流/地理位置/卫星遥感/爬虫+监管文件衍生）——其中**个人项目可免费做的只有 web 注意度、社媒情绪、监管文件衍生三块**，与体检报告"低成本 web 衍生试点"的裁断一致。
4. **同文案例警钟沿用**：黑石系私募试过卫星停车窥屏后因"合规+成本 vs 阿尔法不成正比"放弃。卫星/电商爬虫/付费另类平台三块**明确不做**。
5. **优先级**：P1 = 社热扩展三源 + 票房/运价两个产业垂直（≤1 天/源，复制 hog_* provider 模板）；P1.5 = 互动易问答（tushare 直连，复用 news_data 管线）；P2 = 百度指数（cookie 治理）、采购/政策爬虫试点（唤醒 web_scraper_engine）、百度迁徙、Google Trends。

---

## 1. 现状基线（谁是"相近因子"）

### 1.1 已在跑的边缘另类管线（5 条）

| 管线 | 数据表/入口 | 形态 |
|------|------------|------|
| 天气 | qweather_provider → weather_data（40 城，免费版每日积累） | 区域面板 |
| 生猪产业链 | hog_futures_core / hog_province_spot / hog_spot_index（akshare） | 行业垂直 |
| 社交热度 | stock_hot_rank（东财人气榜） | 个股情绪 |
| 币圈影子 | crypto_kline_daily + crypto_shadow_gate + 恐贪指数（alternative.me 免费API）+ onchain_provider | 跨市场影子 |
| 新闻情绪 | RSS财联社/东财7x24/tushare新闻 → news_data → news_sentiment_window（夜间窗、PIT规则法、market级） | 文本情绪 |

### 1.2 DORMANT 占位（唤醒即用，不用新写）

alt_data 包 15 模块：social_sentiment_collector、web_scraper_engine、filing_nlp_engine、policy_expectation_analyzer、policy_theme_mapper、concept_factor_mapper、geopolitical_risk_analyzer、research_report_collector + 治理五件（alt_data_catalog / alt_data_connector / alt_data_compliance_reviewer / alt_data_privacy_protector / alt_source_health_manager）+ alt_data_signal_extractor。

### 1.3 已有缺口登记无冲突

known_data_gaps.yaml 现有条目全部是 L1/行情侧问题（tick/港股/美股/北向/审批意见等），**另类侧无已登记缺口**——本报告推荐项不会与存量补数计划重复。

---

## 2. 免费另类数据源候选清单（6 组 12 源）

### A 组：散户情绪/关注度扩展（对位 stock_hot_rank + news_sentiment_window）

| 源 | 内容 | 免费获取路径 | 因子逻辑 | 证据 |
|----|------|-------------|---------|------|
| A1 东方财富股吧 | 个股吧发帖量/阅读热度 | 网页接口/akshare data center 系（接口名随版本变动，落地时以现版为准） | 股吧热度激增 → 散户涌入 → 短期动量/反转 | 华创证券《量化选股系列：机构情绪与个人情绪》（2023-09）；多篇学术 VAR 研究 |
| A2 千股千评（东财数据中心） | 综合关注度/评分，日频 | 免费接口 | 关注度分位变化因子 | 同上研报系 |
| A3 雪球 | 关注人数/讨论量 | 非官方 API（免费） | 社区情绪面，与股吧互补 | 社区"雪球情绪指数"回测文（知乎 2023-01）宣称熊市期仍有显著超额 |

工程量：小。唤醒 social_sentiment_collector；表族挂 stock_hot_rank 邻位；接口漂移风险用 alt_source_health_manager 监控（akshare 北向接口失效有先例）。

### B 组：搜索关注度（全网实践最久的免费另类）

| 源 | 内容 | 免费获取路径 | 因子逻辑 | 证据 |
|----|------|-------------|---------|------|
| B4 百度指数 | 关键词搜索指数（PC+移动） | 免费，需登录 cookie；akshare 有移动版接口 | 搜索爆发 → 关注度 → 短期量价反应；概念关键词池映射个股池 | 百度指数官方平台；2019 年起学术文献多篇；华创等券商研报 |
| B5 Google Trends | 英文关键词热度 | pytrends（免费，已归档但可用、脆弱） | 美股/加密辅助信号 | 社区常用工具 |

工程量：中（关键词池治理是主要成本）。唤醒 concept_factor_mapper 做概念→个股映射；PIT 安全（指数即所得，无前视）。

### C 组：互动平台文本（IR 问答 → 文本另类）

| 源 | 内容 | 免费获取路径 | 因子逻辑 | 证据 |
|----|------|-------------|---------|------|
| C6 互动易 + 上证e互动 | 投资者问答原文、公司回复 | tushare irm_qa 接口（项目已有 token，积分门槛以 tushare 官网为准）；**历史回补**：textdata.cn 536 万条问答数据集（2011–2024.12，一次性低成本） | 提问量激增=关注度前兆；回复含糊度/情感=信披质量；主题聚类=政策概念传导 | 上财期刊等学术应用多篇；cnopendata/textdata 数据集描述 |

工程量：中小。文本入库复用 news_data 同款管线 + filing_nlp_engine 唤醒；NLP 消费端可与研报链（P1-B）共享 intelligence 域基建。

### D 组：产业垂直高频价格（复制 hog_* 模式，akshare 直连）

| 源 | 内容 | 免费获取路径 | 因子逻辑 | 证据 |
|----|------|-------------|---------|------|
| D7 电影票房 | 日票房/影片/影院 | akshare 艺恩系接口（如 movie_boxoffice_cinema_daily） | 传媒/影视/院线基本面高频前瞻 | akshare 官方另类数据专区 |
| D8 航运运价 | BDI/CBFI/SCFI 等运价指数 | akshare 航运系/新浪源 | 出口链/航运板块景气前瞻 | 与产业链 ig_* 事件传导打通 |
| D9 水泥/钢材现货价 | 建材高频价格 | 生意社/数字水泥网源（akshare 部分覆盖） | 地产链景气高频代理 | 与 hog_* 同构 |

工程量：小。每源照抄 hog provider 模板（fetch → BufferedWriter → c1_market.alt_* 表族），登记 data_asset_registry。

### E 组：政策/监管/公共采购文本（唤醒 policy_* 与 web_scraper_engine）

| 源 | 内容 | 免费获取路径 | 因子逻辑 | 证据 |
|----|------|-------------|---------|------|
| E10 政府采购/招投标公告 | 中标金额/采购人 | 中国政府采购网公开（需爬虫） | 中标额 → 企业订单前瞻；与体检报告 P2-B 点名项一致 | 体检报告 P2-B |
| E11 部委政策文件 | 发改委/工信部/央行等公示原文 | gov.cn 免费 | policy_expectation_analyzer 喂料；政策主题→板块传导 | 政策事件日历已有 12 类（REG-EVT-001） |

工程量：中。爬虫+解析+合规审查走 alt_data_compliance_reviewer。

### F 组：迁徙/区域活动

| 源 | 内容 | 免费获取路径 | 因子逻辑 | 证据 |
|----|------|-------------|---------|------|
| F12 百度迁徙 | 城市迁入迁出规模指数 | akshare 百度地图慧眼接口（免费） | 出行/消费/区域主题传导 | akshare 官方（事件数据-人口迁徙） |

工程量：小；映射链长 → P2。

---

## 3. 优先级矩阵

| 级别 | 项 | 理由 |
|------|----|------|
| **P1** | A1/A2/A3（社热扩展）+ D7/D8（票房/运价） | 免费、接口成熟、模板现成（hog_* 照抄）、与在跑管线同构 |
| **P1.5** | C6（互动易/e互动） | tushare 直连成本低；需文本管线但复用 news 管线；历史回补一次性投入 |
| **P2** | B4（百度指数）、E10/E11（爬虫试点）、F12（迁徙）、B5（Trends） | 有 cookie/爬虫/治理成本，或映射链长；试点定位 |
| **不做** | 卫星遥感/停车窥屏、电商价格爬虫、付费另类平台（Neudata/Eagle Alpha） | 黑石同文案例（合规+成本 vs 阿尔法）；反爬重+合规深水区；定位不符 |

## 4. 落地路线（4 步）

1. **复制模板**：以 hog_* provider 为模板，新增 票房/运价/股吧热度 三个 fetcher → c1_market.alt_* 表族 → data_asset_registry v1.6.x 登记（source_type=alt）。每源 ≤1 天。
2. **唤醒模块**：social_sentiment_collector（股吧/雪球）+ filing_nlp_engine（互动易问答）→ 并入 news_data 管线，PIT 打点走既有 as_of/embargo 三公理。
3. **关键词池试点**：百度指数概念关键词池 → concept_factor_mapper 概念→个股映射；cookie 健康监控接 alt_source_health_manager。
4. **治理闭环**：新源全部过 alt_data_catalog 登记（source_id/类型/质量分/配额/FTS）+ alt_data_compliance_reviewer 审查（license_type/latency_profile），与 §2.4 数据治理轴对齐。

## 5. 与另两条对话的关系

- 财报对话（P1-A 消费端）、研报对话（P1-B 链路）范围不变；本清单 B/C 组（互动易文本、百度指数）可作研报观点的**交叉验证源**；D 组产业垂直与产业链 ig_* 事件传导（chain_impact_stream）天然打通。

## 6. 证据清单

- AKShare 另类数据文档（影院票房/百度迁徙等接口）：https://akshare.akfamily.xyz
- 百度指数平台：https://index.baidu.com
- tushare 深证互动易接口：https://tushare.pro
- textdata.cn「上证e互动、深证互动易」问答记录 536 万条（2011–2024.12）：https://textdata.cn
- QuantsPlaybook 券商金工研报复现库（光大/华泰/招商/国信/开源/东吴等 100+ 策略）：https://github.com/hugo2046/QuantsPlaybook
- 华创证券《量化选股系列：机构情绪与个人情绪》（2023-09-05，发现报告平台）：https://www.fxbaogao.com
- 雪球情绪指数完整历史回测（知乎专栏 2023-01-29）
- Robeco《科普贴：有关量化投资的另类数据》（2022-10-11，Neudata/Eagle Alpha 平台路径）：https://www.robeco.com
- paperswithbacktest 另类数据分类（web 注意度/社媒情绪/信用卡交易流/地理位置/卫星遥感/爬虫+监管文件衍生）：https://paperswithbacktest.com
- 黑石系私募卫星/停车数据弃用案例：见 [数据分层体检报告](2026-09-12-data-layer-gap-analysis.md) §1.3
