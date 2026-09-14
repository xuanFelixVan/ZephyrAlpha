---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（10 条，摘录）**
> - L16: 另类因子对话（本对话）已完成：① 免费另类数据源全网扫描（v1 清单 12 源 6 组）；② 可持续性审计 + 裁定复核 + 政府/国际宏观接入（施工图 v2，四批施工）；③ Owner 逐平台申请 API 后的密钥入库（本轮完成，见 §3）。
> - L22: ## 2. Owner 已申请到的 API 与密钥状态（本轮已入库）
> - L26: | Alpha Vantage | `R0EI5AGNMTSABYE5`（明文完整） | ✅ 已入库 | .env `ALPHAVANTAGE_API_KEY`（registry 原有条目，本轮补值） |
> - L27: | EODHD | `6aa56e7c5d6d83.56448068`（明文完整） | ✅ 已入库 | .env `EODHD_API_KEY` + registry 新条目（免费层每日请求逐日积累，无历史回补） |
> - L28: | 百度指数·数据开放平台 Access-Token | JWT（**约 24h 过期**，exp≈2026-09-13） | ✅ 已入库（短时） | .env `BAIDU_INDEX_TOKEN`；appKey=69ba9d46fec452d84d661da1bdf50898；平台账号 uid=
> - L29: | 北京市开放平台 key | `1789224430654`（明文完整） | ✅ 已入库 | .env `BJ_DATA_OPEN_KEY`；**个人 token 有效期 3 个月**，cron 续期提醒已建（见 §5） |
> - （另有 4 条完成信号，见正文）
>
> **⚠️ 未完成（2 条，逐条摘录）**
> - L7: > 本文件是新对话的**第一输入**。任务背景、密钥状态、平台 API 入口、待办事项、全部文件路径都在这里。
> - L79: ## 8. 交接后新对话的待办（按序）
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 0、路径漂移 0）+ commit 提及 4 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 另类数据工作交接指令（2026-09-12 深夜 · 另类因子对话 → 新对话）

> 本文件是新对话的**第一输入**。任务背景、密钥状态、平台 API 入口、待办事项、全部文件路径都在这里。
> 姊妹文件：`2026-09-12-data-layer-gap-analysis.md`（体检）→ `2026-09-12-alt-data-supplement-scan.md`（v1 清单）→ `2026-09-12-alt-data-construction-plan.md`（施工图 v2）→ 本文件（交接）。

---

## 1. 任务背景（完整版）

Owner 运营 ZephyrAlpha 个人量化系统（主仓 `D:\ZephyrAlpha`）。数据分层体检报告判定 L3 另类层 ≈15%：alt_data 包 15 个模块 DORMANT 占位但治理件齐全，在跑的边缘另类管线 5 条（天气/生猪/人气榜/币圈影子/新闻情绪，全部有 tasks.yaml 常驻调度任务，可持续更新——已用代码实证，生猪三表 = hog_futures_core/hog_province_spot/hog_spot_index 三个 daily_event 任务）。

另类因子对话（本对话）已完成：① 免费另类数据源全网扫描（v1 清单 12 源 6 组）；② 可持续性审计 + 裁定复核 + 政府/国际宏观接入（施工图 v2，四批施工）；③ Owner 逐平台申请 API 后的密钥入库（本轮完成，见 §3）。

**明确排除项（已裁定，勿推翻）**：卫星遥感/停车窥屏（黑石同文案例：合规+成本 vs 阿尔法不成正比）、电商价格爬虫（反爬重+条款灰色+有免费替代品：海关月度/统计局社零）、付费另类平台订阅（Neudata/Eagle Alpha/Wind/Choice；iFind 已于 2026-08-14 退归）。唯一付费例外保留：分析师一致预期历史（P1-C，财报对话范围）。

**与并行对话的边界**：财报对话负责 P1-A（财报因子消费端）、研报对话负责 P1-B（研报链路 MVP）——另类对话不做这两块，但互动易文本/百度指数可作研报观点交叉验证源。

## 2. Owner 已申请到的 API 与密钥状态（本轮已入库）

| 平台 | key 值摘要 | 状态 | 位置 |
|------|-----------|------|------|
| Alpha Vantage | `R0EI5AGNMTSABYE5`（明文完整） | ✅ 已入库 | .env `ALPHAVANTAGE_API_KEY`（registry 原有条目，本轮补值） |
| EODHD | `6aa56e7c5d6d83.56448068`（明文完整） | ✅ 已入库 | .env `EODHD_API_KEY` + registry 新条目（免费层每日请求逐日积累，无历史回补） |
| 百度指数·数据开放平台 Access-Token | JWT（**约 24h 过期**，exp≈2026-09-13） | ✅ 已入库（短时） | .env `BAIDU_INDEX_TOKEN`；appKey=69ba9d46fec452d84d661da1bdf50898；平台账号 uid=90557200 |
| 北京市开放平台 key | `1789224430654`（明文完整） | ✅ 已入库 | .env `BJ_DATA_OPEN_KEY`；**个人 token 有效期 3 个月**，cron 续期提醒已建（见 §5） |
| 上海市开放平台 | 未申请到 API（占位） | ⏳ 待按话术申请 | .env `SH_OPEN_DATA_TOKEN=`（注释占位）+ registry 占位条目 |
| Tushare | `f42ada…c6bb`（原有） | ✅ 原已在库（2000 积分） | .env `TUSHARE_TOKEN`；irm_qa 互动易接口积分门槛需在 tushare.pro 核对 |
| FRED / 和风 / EIA / OKX | 原有 | ✅ 原已在库 | .env 对应条目 |

登记纪律：值只进 `D:\ZephyrAlpha\.env`（gitignore 保护），`config/secret_registry.yaml` 只登记元数据（本轮 4 条新增 + AlphaVantage 补值说明，YAML 校验通过，total_keys 100→104）。

## 3. 各平台 API 入口核实结果（Owner 问"准确 API 获取网址"）

| 平台 | 免费/付费 | 准确 API 入口 | 说明 |
|------|----------|--------------|------|
| 百度指数·数据开放平台 | **免费层**：关键词热度查询有日配额；付费 = 提升配额 | 控制台 <https://console.bce.baidu.com> → 数据开放平台/百度指数应用管理；token 刷新也在应用管理 | 你给的 JWT 是**短时 token（≈24h）**，免费层不等于永久 token——接入时写自动刷新或每日重取逻辑；收藏夹里充值页只是付费加速入口，不充值也能用免费配额 |
| 上海市开放平台 | 免费 | 官网 <https://data.sh.gov.cn> → 「互动交流/数据申请」栏目 → 选"有待开放的数据"或"未开放"数据集提交申请；**接口调用指南 V2025 PDF**：官网资产页 `data.sh.gov.cn/assets/data/接口调用指南V2025.pdf` | 你截图里的页面（数据申请表单：选择资源→申请理由→验证码→提交申请）就是正确入口；API 权限在申请获批后随数据集下发 |
| 深圳市开放平台 | 免费 | <https://opendata.sz.gov.cn> 首页「数据申请」→ 提交数据申请（436/539 页表单） | 你已亲测；申请话术模板见 §4，直接粘贴 |
| 北京市开放平台 | 免费 | <https://data.beijing.gov.cn> → 接口页（你已拿到 key） | **每 90 天手动续期**，cron 已建 |
| 浙江数据开放 | 免费 | <https://data.zjzwfw.gov.cn>（你给的 zjservice-fe 链接是政务服务门户，不是数据 API 入口） | 数据 API 在开放平台站的「数据目录/接口」分区；优先级低，可放最后 |
| 国家数据局 | 免费 | <https://www.nda.gov.cn/sjj/index_pc.html>（国家公共数据资源登记平台·国家数据集） | **定位是全国公共数据资源的目录登记入口**，不是数据 API 网关——查到目标数据集后跳转到对应地方平台/部门平台获取。没有统一 API 是设计如此，不是你没找到 |
| Tushare | 已有 2000 积分 | <https://tushare.pro> → 个人主页 → 接口 TOKEN；irm_qa（互动易）等接口按积分分级 | 积分不够的接口需升级（付费或贡献），先核对 irm_qa 门槛再决定 |
| FRED | 免费 | <https://fred.stlouisfed.org/docs/api/api_key.html>；**项目已有 key 在用**（.env FRED_API_KEY），你贴的示例 URL 里的 abc... 是文档示例不是真 key | 无需动作 |
| IMF | 免费 | **SDMX 2.1**：<https://api.imf.org/external/sdmx/2.1/...>；**SDMX 3.0**：<https://api.imf.org/external/sdmx/3.0/...>；API 门户：<https://portal.api.imf.org/apis> | 2.1 vs 3.0 区别见 §6；**建议接 2.1**（稳定、教程多、SDMX 库兼容） |
| GDELT | 免费 | 正确入口：<https://www.gdeltproject.org/data.html>（DOC 2.0/2.1 事件库、GKG、TV API）；你贴的 ngrams 文章是过渡期**非消费级**数据集（只有四词词频直方图，无全文，≠常规事件 API） | 接入路径：每日拉 lastupdate.txt → 解析 CSV.zip → 事件/GKG 入库，无需注册 |
| SEC | 免费 | 数据 API：<https://www.sec.gov/edgar/search>（EFTS 全文检索）+ <https://www.sec.gov/cgi-bin/browse-edgar> 等；你发的 federalregister.gov 是**申报机构（filer）管理规则**，不是数据 API 申请；`sec.gov/submit-filings` 是**公司提交申报文件**的入口，与数据获取无关 | 数据获取无需申请 API，只需请求头带合法 User-Agent + 遵守限频（≤10 req/s） |
| Alpha Vantage | 免费层 ~25 req/天 | <https://www.alphavantage.co/support/#api-key> | key 已入库 |
| EODHD | 免费层（每日请求逐日积累） | <https://eodhd.com/register> | key 已入库 |

## 4. SH / SZ 数据申请话术模板（复制即用）

**深圳 opendata.sz.gov.cn（数据申请页 436/539 字段）：**

> 本人系个人量化研究者，需批量、周期性获取贵平台发布的【宏观经济/区域经济统计】类数据集（如地区生产总值、规模以上工业、社会消费品零售总额等可开放统计表），用于个人学术研究与数据分析。申请通过接口或批量下载方式获取上述**已经开放**的数据集，不做转售、不做二次分发，仅用于本人研究。恳请批准，谢谢。

**上海 data.sh.gov.cn（申请理由 ≤255 字）：**

> 个人量化研究者，申请获取【已开放的经济统计类数据集】的接口调用/批量下载权限，用于个人数据分析与研究，承诺不转售、不二次分发、遵守平台使用条款。恳请批准。

（要点：强调"已开放数据集 + 个人研究 + 不转售不分发"，通过率高；若申请"有条件开放"数据集，平台可能要求补充用途说明或实名核验。）

## 5. 已建自动化

- **cron 任务**（AutoClaw「定时」面板可见）：`北京开放平台Token续期提醒-每90天`（id c638e057-4930-43be-984c-bf85017f1e5d）——首次触发 2026-12-12 10:00（token 到期日），此后每 90 天；提醒文案含 .env 路径与更新步骤，并会顺带检查 SH_OPEN_DATA_TOKEN 是否已申请到。
- 百度指数 token ≈24h 过期：**不设 cron**（接入层处理——provider 每日运行时刷新/重取 token，失败则告警），避免主会话每日被噪音唤醒。

## 6. IMF SDMX 2.1 vs 3.0（一句话版）

2.1 = 老标准，GET 查询格式成熟、社区代码与 pandasdmx/pysdmx 兼容最好，数据全；3.0 = 新标准（2025+），元数据模型更严谨、支持新查询能力，但库支持还在追赶。**数据本身两版一致，选 2.1 省事**；IMF 自己也说 3.0 是"new features and changes"。接入用 2.1 endpoint：`https://api.imf.org/external/sdmx/2.1/data/{flowRef}/{key}/{providerRef}`。

## 7. 你提到的"某平台免费开放全量数据下载"新闻

两轮定向搜索（免费开放金融数据 3/6 个月 + 量化平台免费开放公告）**未命中该新闻**，不编造。检索到的最接近事实：麦蕊智数 2026-08-29 更新日志称"量化因子数据接口正式开放：19 个因子接口/68 字段/完整历史因子序列（逐股自上市日起算）"（https://www.mairuiapi.com/updatelog）——它是免费试用+付费模式，与你记忆的"免费 3-6 个月全量"不完全吻合。若你回忆起更多线索（平台名/发布渠道），告诉我再搜；该信息不影响主线施工。

## 8. 交接后新对话的待办（按序）

1. **第 1 批施工（免注册直连，可立即开工）**：股吧/千股千评/票房/运价 akshare 直连，照抄 hog_* provider 模板 → c1_market.alt_* 表族 → data_asset_registry 登记；每源 ≤1 天。
2. **第 2 批（注册类）**：百度指数接入（BAIDU_INDEX_TOKEN + 每日刷新逻辑 + concept_factor_mapper 唤醒）；雪球；互动易 irm_qa（先核对 2000 积分是否够）；SH/SZ 开放平台等申请获批后接入。
3. **第 3 批（爬虫试点）**：政府采购网中标公告（唤醒 web_scraper_engine + compliance_reviewer）；textdata.cn 历史问答集（可选小额买断）。
4. **第 4 批（海外）**：GDELT 日频拉取（gdeltproject.org/data.html 路径）；SEC EFTS（User-Agent+限频）；IMF SDMX 2.1 精选序列落 macro_data 共表（indicator_name 前缀 IMF_，复用 FRED 模式）；Alpha Vantage/EODHD 免费层做美股深度补缺（EODHD 每日请求逐日积累，先跑起来）。
5. 治理闭环每批都做：alt_data_catalog 登记 → compliance_reviewer → alt_source_health_manager 探针 → known_data_gaps.yaml；PIT 三公理不变。

## 9. 关键文件路径总表

| 文件 | 路径 |
|------|------|
| 主仓 | `D:\ZephyrAlpha` |
| 密钥真源 | `D:\ZephyrAlpha\.env`（值）+ `D:\ZephyrAlpha\config\secret_registry.yaml`（元数据，total_keys=104） |
| 调度清单 | `D:\ZephyrAlpha\src\zephyr\data\config\tasks.yaml` |
| 缺口登记 | `D:\ZephyrAlpha\src\zephyr\data\config\known_data_gaps.yaml` |
| 另类模块包 | `D:\ZephyrAlpha\src\zephyr\alt_data\`（15 模块 DORMANT） |
| provider 模板 | `D:\ZephyrAlpha\src\zephyr\data\implementations\`（hog 模板：tasks.yaml 三个 hog_* 任务 + akshare_provider） |
| 资产登记 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\data_asset_registry.yaml` |
| 本系列报告 | `D:\ZephyrAlpha\docs\_working\2026-09-12-data-layer-gap-analysis.md` · `2026-09-12-alt-data-supplement-scan.md/html` · `2026-09-12-alt-data-construction-plan.md/html` · `2026-09-12-alt-data-handoff.md`（本文件） |
| cron 任务 | 「定时」面板：北京开放平台Token续期提醒-每90天 |
