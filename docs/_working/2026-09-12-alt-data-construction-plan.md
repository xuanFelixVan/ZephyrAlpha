---
ttl: task_bound
---

# 另类数据施工图 v2：可持续性审计 + 裁定复核 + 政府/国际宏观数据接入（2026-09-12）

> 任务：回答 Owner 四个问题——① 五条另类管线是否可持续更新；② 电商爬虫不碰的裁定原因；③ "web 注意度/社媒情绪/监管文件衍生"三块具体怎么做；④ 政府数据要不要采购、国际宏观（FRED 等）能否免费获取；并给出完整施工图与注册 URL 清单。

---

## 0. 一页结论

1. **五条另类管线全部有持续调度任务，不是一次性导数。** 生猪三表在 tasks.yaml 是 daily_event 日度任务（akshare 增量/幂等），其余四条各有专属 task。风险不在"有没有源"，在 akshare 上游网页改版——用 alt_source_health_manager + known_data_gaps 机制兜底（先例：北向三接口断 → tushare 替代）。
2. **电商爬虫不碰的四条理由**（此前只写了裁定没写原因）：反爬工程量（登录/验证码/代理池+页面改版维护）＞ 收益；平台条款合规深水区；有免费合法替代品（海关进出口月度、统计局社零）；同等"消费景气"信号可由已接的宏观数据覆盖。
3. **三块可做（web 注意度 / 社媒情绪 / 监管文件衍生）全部有具体施工路径**：见 §2，每块标注了复用哪个 DORMANT 模块、落哪张表、加哪个 task。
4. **政府数据不需要采购。** 国家统计局/部委公示/采购公告全免费；243+ 省市级开放平台免费（部分数据集需注册账号下载）；唯一小额可选采购是 textdata.cn 互动问答历史集（一次性买断，非订阅）。
5. **国际宏观免费的已经接了一半**：FRED（22 序列，event_driven 增量）+ 世界银行（免 key）+ EIA 能源已在跑（tasks.yaml 实证）；本轮新增建议 = IMF、OECD（免费 API）+ GDELT（免注册、15 分钟全球新闻事件）+ SEC EDGAR EFTS（免注册 JSON 全文检索）。
6. **施工批次**：第 1 批（免注册直连）→ 第 2 批（注册类，URL 清单 §4）→ 第 3 批（爬虫试点）→ 第 4 批（海外源）。

---

## 1. 五条管线可持续性审计（代码实证）

审计口径：tasks.yaml（src/zephyr/data/config/tasks.yaml）是否有 live 调度任务 + 增量/幂等模式 + 源可访问性。

| 管线 | task_id | schedule | 模式 | 源 | 判定 |
|------|---------|----------|------|----|------|
| 生猪期货 | hog_futures_core_refresh | **daily_event** | 增量 | akshare futures_hog_core（东财期货源） | ✅ 可持续 |
| 生猪分省现货 | hog_province_spot_refresh | **daily_event** | 全量快照幂等 | akshare spot_hog_soozhu（搜猪 28 省价差） | ✅ 可持续 |
| 生猪现货指数 | hog_spot_index_refresh | **daily_event** | 周度数据日度拉取幂等去重 | akshare index_hog_spot_price | ✅ 可持续 |
| 天气 | qweather_now/forecast_incremental | 日度 | 增量 | 和风天气免费 API（QWEATHER_API_KEY，免费注册） | ✅ 可持续（免费版无历史→每日积累） |
| 社交热度 | stock_hot_rank_incremental | **daily_capital** | 增量 | akshare 东财人气榜 | ✅ 可持续 |
| 币圈影子 | crypto_kline_daily_incremental + 恐贪指数 | 日度 | 增量 | OKX + alternative.me 免费免 key API | ✅ 可持续 |
| 新闻情绪 | news_cls_incremental / eastmoney_news / tushare 新闻 | 持续 | 增量 | 财联社电报/东财 7x24/tushare | ✅ 可持续 |

**结论**：五条管线 = 7 组任务全部在调度清单上，持续更新成立。**残余风险与对策**：
- akshare 上游网页改版（先例：北向 stock_hsgt_* 三接口 2026-08 断裂 → tushare hk_hold 替代，全程 known_data_gaps 登记）。对策：alt_source_health_manager 健康探针 + 缺口登记表，断供时换源而非弃线。
- 和风免费版无历史：只能每日积累，今天不跑明天就少一天。对策：保持任务常开即可。

## 1.5 裁定复核（用户问"为什么"）

| 裁定 | 原因 | 免费合法替代品 |
|------|------|---------------|
| 卫星遥感/停车窥屏：不碰 | 黑石系私募实测后因"合规+成本 vs 阿尔法不成正比"放弃（体检报告 §1.3 同文案例） | 无需替代 |
| 电商价格爬虫：不碰 | ① 反爬重：登录态/验证码/代理池+页面改版持续维护，工程量远超个人项目预算；② 平台服务条款与数据权属灰色，合规深水区；③ RQData 把电商数据做成标准目录项恰恰说明这是授权商用生意，不是白嫖生意 | 海关进出口月度（akshare 宏观区）、统计局社零总额、电商行业月报数据（统计局/商务部免费） |
| 付费另类平台（Neudata/Eagle Alpha/Wind/Choice）：不买 | 订阅成本与个人项目阿尔法不成比例；iFind 已于 2026-08-14 主动退归（#ARCH-DATA-IFIND-RETIRE-001） | 唯一例外保留在 P1-C：分析师一致预期**历史**若免费源拿不到，这是唯一值得重新花钱的点（财报对话范围） |

---

## 2. 三块可做的施工图

### 2.1 Web 注意度（搜索/浏览热度）

| 项 | 内容 |
|----|------|
| 源 | 百度指数（index.baidu.com，免费需登录 cookie）；akshare 百度指数移动版接口 |
| 施工 | 概念关键词池治理（≈200 词起步：行业词+政策热词+龙头简称）→ 每日拉取 → 落 c1_market.search_attention → concept_factor_mapper 做概念→个股映射 |
| 唤醒模块 | concept_factor_mapper（DORMANT） |
| 风险 | cookie 过期 → alt_source_health_manager 监控 + 告警 |
| PIT | 指数即所得，无前视 |

### 2.2 社媒情绪

| 项 | 内容 |
|----|------|
| 源 | A1 股吧个股吧发帖量/阅读热度（akshare data center 系）；A2 千股千评日频关注度/评分（东财数据中心）；A3 雪球关注/讨论（非官方 API） |
| 施工 | 唤醒 social_sentiment_collector → 三源统一 (metric, trade_date, value, source) 行格式 → 落 stock_hot_rank 邻位表族 → 与 news_sentiment_window 情绪指数在消费端合成 |
| 证据 | 华创《机构情绪与个人情绪》（2023）；雪球情绪指数长回测（知乎 2023-01） |
| 风险 | 接口漂移 → health manager；非官方接口限频 → 降级拉取 |

### 2.3 监管文件衍生

| 项 | 内容 |
|----|------|
| 源（境内） | 互动易+e互动问答（tushare irm_qa，已有 token）；历史回补 textdata.cn 536 万条（2011–2024.12，一次性小额买断可选）；巨潮公告文本（akshare 公告接口已部分覆盖） |
| 源（海外） | SEC EDGAR EFTS 全文检索（efts.sec.gov，免注册 JSON API，需声明 User-Agent）；QuantsPlaybook 社区已验证此类文本因子工程 |
| 施工 | filing_nlp_engine 唤醒 → 问答/公告文本入 news_data 同款管线 → 结构化（提问量/回复情感/含糊度/主题）→ 消费端与研报链（P1-B）共享 intelligence 域 |
| PIT | 公告/问答发布时间即所得，embargo 走既有三公理 |

---

## 3. 政府数据：不需要采购，免费路径清单

| 层 | 源 | 获取方式 | 注册需求 | 用途 |
|----|----|---------|---------|------|
| 全国 | 国家统计局 data.stats.gov.cn | 免费，akshare 宏观区已包装（macro_data 291K 行已在跑） | 免注册 | CPI/PPI/PMI/GDP/社零/工业增加值 |
| 全国 | 部委公示原文（发改委/工信部/商务部/农业农村部） | gov.cn 免费 | 免注册 | policy_expectation_analyzer 喂料、政策主题传导 |
| 全国 | 中国政府采购网 ccgp.gov.cn 中标公告 | 免费公开 | 免注册 | 爬虫试点（体检报告 P2-B 点名）：中标额→企业订单前瞻 |
| 全国 | 国家公共数据资源登记平台/国家数据局 nda.gov.cn | 免费目录检索 | 目录检索免注册 | 发现各地开放数据集的全国入口 |
| 地方 | 上海 data.sh.gov.cn / 浙江 data.zjzwfw.gov.cn / 北京及 243+ 省市平台 | 免费开放 | 部分数据集需注册实名账号 | 区域经济面板（与 weather 40 城同构）、地方产业数据 |
| 采购判断 | —— | **0 元为主**；唯一可选小额 = textdata.cn 历史问答集（买断） | —— | 不订阅任何政府数据付费服务 |

**关键澄清**：政府数据的问题从来不是"贵"，是"散"——243 个平台各有一套目录。施工上只按需接 2-3 个（上海+浙江+采购网试点），不做全域扫描。

## 3.5 国际宏观（FRED 等）：免费的已接一半

| 源 | 项目现状 | 免费性 | 本轮动作 |
|----|---------|--------|---------|
| FRED 美联储 | **已在跑**：fred_provider + macro_fred_incremental（event_driven，22 序列：美 GDP/CPI/失业率/国债收益率/美元/WTI/黄金/VIX） | 免费 API key | 确认 owner 级 FRED_API_KEY 配置在位（注册见 §4） |
| 世界银行 | **已在跑**：macro_worldbank_full_refresh（免 key） | 完全免费 | 无需动作 |
| EIA 能源 | **已在跑**：eia_provider | 免费 key | 无需动作 |
| IMF | 未接 | 免费数据门户 | 新增：接入 IMF WEO/IFS 精选序列（汇率/外储/全球通胀），落 macro_data 共表（indicator_name 前缀区分，复用 FRED 模式） |
| OECD | 未接 | 免费 SDMX API | 低优先：部分指标与 FRED/世行重叠 |
| GDELT | 未接 | 100% 免费免注册，15 分钟更新 | 新增：全球新闻事件/GKG 情绪 → 港美股+币圈影子增强（与 news_sentiment_window 同构，英文事件流） |
| SEC EDGAR EFTS | 未接 | 免注册 JSON API | 新增：美股申报全文（配合已知缺口"美股深度"） |
| pytrends/Google Trends | 未接 | 免费（pytrends 已归档，脆弱） | P2：美股/加密辅助关键词 |
| Alpha Vantage/EODHD/FMP/Finnhub 免费层 | 未接 | 免费配额层 | P2：仅用于美股深度补缺（kline_us_daily 源上限已知缺口），配额内做增量 |

**VPN 澄清**：本轮海外源核验走的是服务端检索；本地接入时 FRED/WorldBank/EIA 既有代码已处理代理（读 HTTPS_PROXY），GDELT/EFTS 同理可直接复用。

---

## 4. 施工批次与注册 URL 清单

### 批次规划

| 批次 | 内容 | 前置 | 工程量 |
|------|------|------|--------|
| **第 1 批：免注册直连** | A1 股吧/A2 千股千评、D7 票房、D8 运价（akshare 直连，照抄 hog_* 模板落 alt_* 表族） | 无 | 每源 ≤1 天 |
| **第 2 批：注册类** | A3 雪球、B4 百度指数（账号+cookie）、C6 互动易（tushare 已有 token，核对 irm_qa 积分门槛）、地方开放平台账号（上海/浙江 各注册一个） | **Owner 注册动作（下表）** | 每源 0.5-1 天 |
| **第 3 批：爬虫试点** | E10 政府采购网中标公告（唤醒 web_scraper_engine + compliance_reviewer）；textdata.cn 历史问答集（可选小额采购） | 第 2 批账号 | 2-3 天 |
| **第 4 批：海外源** | GDELT 15 分钟事件流 → 英文情绪窗口；SEC EFTS 美股申报文本；IMF 序列接入 | VPN 常态在线 | 2-3 天 |

### 需 Owner 注册的免费源（网址清单）

| # | 平台 | 网址 | 注册类型 | 用途 |
|---|------|------|---------|------|
| 1 | 百度指数 | <https://index.baidu.com> | 百度账号+登录 cookie | Web 注意度 |
| 2 | FRED API | <https://fred.stlouisfed.org/docs/api/api_key.html> | 免费 API key（32 位） | 国际宏观（已在用，确认 key 在位） |
| 3 | 和风天气 | <https://dev.qweather.com> | 免费 key（已在用） | 天气管线续命 |
| 4 | tushare | <https://tushare.pro> | 已有 token，核对 irm_qa 积分 | 互动易问答 |
| 5 | 上海市公共数据开放平台 | <https://data.sh.gov.cn> | 实名账号（部分数据集） | 区域面板 |
| 6 | 浙江·数据开放 | <https://data.zjzwfw.gov.cn> | 实名账号（部分数据集） | 区域面板 |
| 7 | 国家公共数据资源登记平台（入口：国家数据局） | <https://www.nda.gov.cn> | 目录免注册 | 全国开放数据集发现 |
| 8 | 国家统计局 | <https://data.stats.gov.cn> | 免注册 | 宏观（akshare 已包装） |
| 9 | GDELT | <https://www.gdeltproject.org> | 免注册 | 全球新闻事件流 |
| 10 | SEC EDGAR EFTS | <https://efts.sec.gov/LATEST/search-index?q=%22test%22> （查询端点，文档见 sec.gov/edgar） | 免注册（需 User-Agent） | 美股申报文本 |
| 11 | IMF Data | <https://data.imf.org> | 免注册 | 国际宏观补充 |
| 12 | Alpha Vantage（P2 备选） | <https://www.alphavantage.co> | 免费 key | 美股深度 |
| 13 | EODHD（P2 备选） | <https://eodhd.com> | 免费层 | 美股深度 |
| 14 | textdata.cn 问答历史集 | <https://textdata.cn> | 数据集商品（可选买断） | 互动易历史回补 |
| 15 | pytrends | <https://github.com/GeneralMills/pytrends> | 开源库 | Google Trends 免费接口 |

---

## 5. 治理闭环（与 v1 报告 §4 一致，不重复展开）

新源全部过：alt_data_catalog 登记 → alt_data_compliance_reviewer（license_type/latency_profile）→ alt_source_health_manager 探针 → known_data_gaps.yaml 断供登记。PIT 三公理不变。

## 6. 证据清单

- tasks.yaml 调度实证：hog_* 三任务 daily_event（D:\ZephyrAlpha\src\zephyr\data\config\tasks.yaml）；qweather/stock_hot_rank/crypto_kline/news_cls/macro_fred/macro_worldbank 各任务行号见正文引用
- FRED API key 说明：<https://fred.stlouisfed.org/docs/api/api_key.html>；世界银行公开数据：<https://data.worldbank.org>（中文站 data.worldbank.org.cn）；IMF：<https://data.imf.org> / <https://www.imf.org/en/data>
- GDELT 100% 免费开放、15 分钟更新：<https://www.gdeltproject.org>；ONS 对 GDELT 两大库（Event/GKG）说明
- SEC EDGAR 免费全文检索（EFTS，2001 至今）：<https://efts.sec.gov> 与 <https://www.sec.gov/edgar>；EDGAR API 总览 sec.gov
- 政府数据：上海平台 <https://data.sh.gov.cn>（沪府令21号办法）；浙江 <https://data.zjzwfw.gov.cn>；开放林指数报告 ifopendata.cn（51.33% 城市已上线平台）；人民网/国家数据局 nda.gov.cn 公共数据资源三文件与开放量增长数据
- 电商数据商用化参照：米筐 RQData 目录含电商数据（第一轮扫描）
- 免费层行情 API 对比（免费层普遍限 1 年历史）：<https://eodhd.com> scorecard、stackademic 2026-06 对比文
- 生猪三表 akshare 接口名（futures_hog_core/spot_hog_soozhu/index_hog_spot_price）：tasks.yaml extra.description 原文
