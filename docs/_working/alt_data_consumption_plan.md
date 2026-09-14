---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（3 条，摘录）**
> - L50: **消费方式**：②③。**强度**：中高。**启动**：立即可做（F7/F4 优先）。**量**：F7=0.5d（已验证）、F4-F6=1d。
> - L86: - F15 恐贪 <20 反弹窗：复用 C4 已验证策略，把信号侧自动化（数据现成）
> - L207: **边界重申**：研报文本/一致预期消费端属 P1-B 研报对话（其 expectations.py 已落地），本方案不越界。
>
> **⚠️ 未完成（3 条，逐条摘录）**
> - L97: ### H. 互动易（第 2 批，未接）
> - L190: - **政策文本→板块映射卡（挂起，来源闸未过）**：policy_expectation_analyzer/policy_theme_mapper 休眠模块 + event_calendar_registry 12 类事件为内部承接件；R12 外部证据搜索全程 429 受阻，按来源可溯闸暂不设计，
> - L204: | R12 | 政策文本映射 | **noise #1**（搜索全程受阻，来源闸未过） | 内部承接件确认，卡挂起 |
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 0 个，其中判废弃 0、路径漂移 0）+ commit 提及 11 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 另类数据消费端施工方案 v1（2026-09-13 · 讨论稿）

> 任务：另类数据"数据层已全绿"之后的消费端设计。每源一张消费设计卡（证据/因子公式/消费方式/启动条件），统一验证纪律复用 C4 资产。
> 前序：[alt-data-handoff](2026-09-12-alt-data-handoff.md) → [第1批施工报告](2026-09-12-alt-data-batch1-construction-report.md) → **本方案**

---

## 0. 总纲：三层消费架构 + 一条排序铁律

**三层架构**：
1. **信号层**：每源产出标准化因子值（横截面）或事件/regime 表（时序），落 `factor_feature_value` 表族 + 事件日历
2. **验证层**：统一考试——C4 粗筛器（IC/分层/换手/衰减）→ OOS 2024-2026 锁窗 → node-verdict 台账（pending→毕业才进决策链）。纪律：**IS 排名不作数，唯一双窗及格才有资格**（恐慌反弹 1.15→0.83 的教训）
3. **消费层**：四种用法——①横截面打分/过滤（选股）②market regime 开关（轮动/仓位）③事件日历（事件窗/风险）④择时窗口（极端值反转）

**排序铁律：按"已有历史深度"排施工序，不按数据重要性。**
- 立即可做（历史满格）：运价（1988~）、生猪（2015~）、宏观、新闻情绪、币圈、天气（195 天）
- 需积累再做：千股千评（09-12 首日！）、人气榜（仅 13 天）——横截面变化率因子需要 ≥20 日，霸榜类需要 ≥60 日

**数据积累批（与消费端并行，本周可做）**：①EODHD 每日最小配额任务（免费层"逐日积累历史"，不跑就真空）②台风表 DDL 先建等 appKey ③北京 key 数据集选型 ④百度 JWT 过期无需动作（第 2 批自动刷新）。

---

## 1. 消费设计卡（按源）

### A. 千股千评 `alt_stock_comment`（横截面日频，09-12 起积累）

**证据**：Da-Engelberg-Gao《In Search of Attention》（JF 2011，搜索量→短期价格压力→反转，[原文](https://academicweb.nd.edu/~zda/Google.pdf)）；A股百度指数复制系（ASV=log SVI − 前 8 周均值，[复现配方](https://zhuanlan.zhihu.com/p/593205002)，[Baidu index predictability](https://d-nb.info/1129927857/34)）；[《金融研究》关注度与概念股](http://www.jryj.org.cn/CN/abstract/abstract616.shtml)；华创《机构情绪与个人情绪》(2023)。东财关注指数=股吧流量代理，与 ASV 同族。

**因子**：
- F1 关注度异动：attention_index 横截面 zscore → Δ5d（激增=散户涌入→价格压力，**定位为反向信号/过滤器**比正向更稳——DEG 结论是压力后反转）
- F2 综合得分×机构参与度动量：composite_score 5 日变化 × org_participation → 机构一致性（正向，弱信号）
- F3 排名跃迁事件：current_rank 单日升幅 top5% → 热点扩散事件流（喂 chain_impact_stream）

**消费方式**：横截面（①）。**强度**：高（DEG 系最扎实）。**启动**：≥20 交易日（约 10 月中）。**量**：1.5 天。

### B. 航运运价 `alt_shipping_index`（1988~，历史满格）

**证据**：BDI=全球干散货景气领先指标（BCI 40%+BPI 30%+BSI 30%，[MacroMicro](https://sc.macromicro.me/charts/893/commodity-bdi)）；[华创 2026 航运供需缺口逻辑](https://www.cls.cn/detail/2219254)；BDI 与金砖股市共整合实证；**校准**：BDI=铁矿石/煤炭/谷物（上游资源+航运股），中国出口看集装箱 SCFI/CCFI——"出口链"叙事收敛为"资源/航运链"。

**因子**：
- F4 BDI 动量 regime：20 日 zscore 越阈 → 周期/资源 regime 开关（market 级）
- F5 船型结构：BCI/BPI 比值动量 → 铁矿石 vs 谷物航线景气切换
- F6 油轮系：BDTI/BCTI 20 日动量 → 能源运输景气（地缘事件放大器）
- F7 台风事件日历：**已实弹验证**（11 事件，后 10 日均值 +8.86%、9/11 上涨，含反例）→ 事件窗因子 + 风险日历

**消费方式**：②③。**强度**：中高。**启动**：立即可做（F7/F4 优先）。**量**：F7=0.5d（已验证）、F4-F6=1d。

### C. 天气 `weather_data`（40 城，195 天）

**证据**：[Cao-Wei 温度异常（JBF 2005，879 引）](https://www.sciencedirect.com/science/article/abs/pii/S0378426604001293)；Hirshleifer-Shumway 阳光效应 (2003)；稳健性有反例（[Andrikopoulos 2020](https://hull-repository.worktribe.com/OutputFile/1571292)）→ **情绪通道降权，供需通道为主**：温度距平→用电负荷→日耗煤（卖方成熟框架）。

**因子**：
- F8 温度距平 regime：40 城均温 vs 季节基准距平 → 迎峰度夏/冬 → 煤炭/电力轮动
- F9 极端天气日历：高温日数/降水极值 → 农产品/保险事件流

**消费方式**：②③。**强度**：中。**启动**：立即可做（需先建 40 城季节基准，accumulate 195 天够初版）。**量**：1.5d。

### D. 生猪三表（2015~）

**证据**：猪周期产业框架（能繁→出栏 ~10 个月领先）；卖方养殖右侧信号体系；自研表自带 4/6/12 月均线。

**因子**：
- F10 期现价差：hog_futures_core − spot_index 标准化 → 近端供需紧张度
- F11 周期相位：spot_index / ma_12m 相位（0-1）→ 养殖股右侧信号
- F12 分省价差离散度：province_spot 横截面 std → 调运受阻事件（疫情/台风交叉验证）

**消费方式**：②③。**强度**：中高。**启动**：立即可做。**量**：1d。

### E. 人气榜 `stock_hot_rank`（仅 13 天）

**证据**：散户注意力透支/拥挤度（华创 2023）；[东财官方已推"股吧情绪指数"](https://guba.eastmoney.com/)；[股吧情绪学术研究](https://pdf.hanspub.org/aam20221100000_79882519.pdf)。

**因子**：F13 霸榜持续度（连续 N 日 Top50）→ **拥挤度过滤器**（剔除/降权，不做正向）。
**消费方式**：①过滤。**强度**：中。**启动**：≥60 日（11 月）。**量**：0.5d（与 A 共用框架）。

### F. 币圈影子（17,698 行 + 恐贪）

**证据**：BTC=全球流动性/风险偏好代理；**自有 OOS 证据**：C4 恐慌反弹策略为唯一双窗及格（1.15→0.83，年衰减 11%）。

**因子**：
- F14 BTC 30d 动量 → risk-on/off regime（成长股/A50 输入）
- F15 恐贪 <20 反弹窗：复用 C4 已验证策略，把信号侧自动化（数据现成）

**消费方式**：②④。**强度**：中（自有 OOS）。**启动**：立即可做。**量**：0.5-1d。

### G. 新闻情绪窗 `news_sentiment_window`（已有消费，升级算法）

**证据**：[Lopez-Lira & Tang（SSRN 4412788，8600 引，JFE 正式发表）](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4412788)：LLM 头条情绪分预测次日收益优于传统词典；2025 反思：[清华 Chen et al.](https://www.pbcsf.tsinghua.edu.cn/__local/9/CA/40/43E4F9DF1FABF236323CFACED4E_13568904_12C59E.pdf) LLM 过外推历史 → **必带验收集**（与 AI 自动发现 E2 结论一致）。

**因子**：F16 LLM 情绪分替代规则法（经 LSG 网关，仅增量头条日约百条，控成本）；F17 情绪动量/衰减结构。
**消费方式**：④（开盘 gap/日内）。**强度**：高（OOS 自带验收集）。**启动**：立即可做。**量**：1.5d。

### H. 互动易（第 2 批，未接）

**证据**：[《金融研究》互动易 DID 信息效率](http://www.jryj.org.cn/CN/abstract/abstract241.shtml)；[《会计研究》董秘回复信息含量](http://sfi.cuhk.edu.cn/zh-hans/node/7065)；[《财贸研究》互动放大异质性风险](https://html.rhhz.net/CJYJ/html/17794c14-b22d-4e71-b91b-053fc480a45a.htm)；央财 NLP 定价效率。

**因子**：F18 提问量激增（关注度前兆，与 F1 同族）；F19 回复含糊度/情感（LLM）；F20 主题聚类（政策概念传导）。
**消费方式**：①③。**强度**：中高（国内学术最厚的另类之一）。**启动**：irm_qa 积分核对后。**量**：2d（含文本管线）。

### I-K. 待接入层（简）

- **I 台风/灾害**（等 appKey）：F7 扩展灾损评估（风圈×省份农业/港口权重）；DDL 可先建
- **J GDELT/SEC/IMF**（第 4 批）：GDELT tone=英文事件流（港美股/币圈）；SEC EFTS=美股文本；IMF=全球 regime 交叉验证。低优先
- **K EODHD/AV**（第 4 批）：常规美股深度，非另类；**仅配额积累任务先行**（0.5d）

---

## 2. 施工排序（消费端批次）

| 批次 | 内容 | 量 | 启动条件 |
|------|------|-----|---------|
| C-1（本周） | F7 台风事件日历 + F14/F15 币圈 regime + F4 BDI regime | 2.5d | 无（数据现成） |
| C-2（下周） | F10-F12 生猪 + F8 温度距平 + F16 LLM 情绪试点 | 4d | 无 |
| C-3（10 月中） | F1-F3 千股千评 + F13 人气榜 | 2d | 积累 ≥20/60 日 |
| C-4（第 2 批后） | F18-F20 互动易 | 2d | irm_qa 积分核对 |
| 积累批（并行） | EODHD 配额任务 + 台风 DDL 先建 + 北京选型 | 1d | appKey/选型 |

## 3. 统一考试（每个因子必过）

1. C4 粗筛器：IC 均值/IR、分层单调性、换手、衰减半衰期
2. OOS 2024-2026 锁窗，双窗及格制（IS 不作数）
3. node-verdict 台账：pending → 毕业；毕业因子落 factor_feature_value + 接决策链白名单
4. PIT 三公理不变：as_of/embargo/survivorship

## 4. 遗留判定（本方案不做的）

- 蝴蝶/桦加沙类反例的深挖（台风 vs 全球供需混杂）→ F7 落地后用全样本台风数据回答
- GDELT/IMF 消费设计 → 第 4 批数据落地时另卡
- 生活指数类（露营/游泳/观星）→ 永不做

---

## 5. 挖矿增补（2026-09-13 病菌寻路 R1-R9，SOP=trading_decision_map_pathfinding_sop）

按六向寻路跑 9 轮（每向内部反查+全网搜索），**未触发"连续两轮噪音"终止条件**——R4 与 R8 各出现单轮噪音但均被后续信号打断；本批按 SOP 时间盒封矿（新候选 9 项 > 单批 3 个上限），长尾矿脉排下批。

### 5.1 新增因子候选

- **F21 市场级复合情绪指数**（CICSI/Baker-Wurgler 中国版，易志高&茅宁 2009 方法系）：PCA 合成。**组件可得性已验证（R6 内部反查）**：两融 `macro_china_market_margin_sh/sz` ✓、新增开户 `stock_account_statistics_em` ✓、IPO `stock_ipo_summary_cninfo` ✓、换手率=L1 已有 ✓；封基折价→传统封基已消亡**需改造**（LOF 折价替代或删项）；消费者信心→**GAP**（akshare 无 A 股版）。证据：[北大国发院 CICSI](https://www.nsd.pku.edu.cn/xzyj/kyfb/zsfb/zgtzzqxzs/250262.htm)、[情绪指数择时策略](https://pdf.hanspub.org/ecl2024133_4132310986.pdf)
- **F22 情绪调节动量**：市场情绪状态作为动量/反转切换开关（情绪高涨→动量失效切反转）。证据：[运筹与管理：情绪×时间序列动量](http://www.jorms.net/CN/article/downloadArticleFile.do?attachType=PDF&id=12010)；[北大刘玉珍：A股动量弱=散户机制](https://www.gsm.pku.edu.cn/finance/info/1008/3538.htm)；[BigQuant：A股动量负 IC/skip=1 减弱](https://bigquant.com/wiki/doc/vmpoW4sE1e)。与 F1/F14/F21 联动
- **F7 增强**：台风"灾损强度特征"=风圈半径×产区停留时间 → 菜价/猪价事件预测（[台北市台风-菜价实证：产区雨量与停留时间为关键变量]；[21财经：极端天气 CPI 测算](https://m.21jingji.com/article/20220622/936f344a6ae4a1db92e1bb097569e42d.html)）——与台风数据集 22 字段精确匹配、与 F12 调运受阻交叉
- **席位跟随（待验证，不入图）**：高胜率游资席位未来 5 日超额 +2.8%（[CSDN 实测](https://blog.csdn.net/IG507/article/details/163804132)，单来源+衰减警告[证券时报](https://www.stcn.com/article/detail/3613485.html)）；数据已在库（dragon_tiger 双表）

### 5.2 既有因子增强

- **F4 增强（下游路径+校准）**：库存周期择时——上游原材料策略年化超额 12.2%/胜率 58.8%/IR 0.79（[BigQuant 库存周期](https://bigquant.com/wiki/doc/jYcc7PcRmi)）；**校准警告**：BDI 同比跟踪出口方向正确率仅 ~54%（[信达宏观高频观测方法论](https://pdf.dfcfw.com/pdf/H3_AP202209011577932019_1.pdf)）——F4 定位=干散货/资源链，禁外推到出口链
- **F16 增强（成本路线定案）**：双层方案=本地 FinBERT 开源批量（[valuesimplex/FinBERT2，中文金融语料，分类任务超 GPT-4 系](https://github.com/valuesimplex/FinBERT)，实测 85%+ 准确）+ LSG LLM 抽样校验——纯 API 路线成本不必要
- **F9 增强**：DATA-GAP 落到可执行——港口铁矿石库存周报官方免费（[大商所交割库库存周报](http://www.dce.com.cn/dalianshangpin/sspz/487477/kczb/index.html)，周五更新可追溯）+ 冬季补库季节性（[华泰期货](https://htfc.com/wz_upload/png_upload/20241224/1735045878949957363.pdf)）；注意 Mysteel 口径争议

### 5.3 验证层增补（硬改造项）

1. **衰减先验**：McLean & Pontiff (2016 JF)——因子发表后可预测性衰减 ~26%、整体（含样本内过拟合）~58% → 所有因子毕业预期按此打折；这也是 OOS 锁窗纪律的文献根据
2. **A股回测四规则**（缺一即回测虚高）：①信号次日成交（T+1）②涨跌停日视为无法成交 ③停牌剔除 ④成本+冲击。核对 C4 粗筛器是否显式实现
3. **DSR 现成**：`backtest/regime_validation/c4_deflated_sharpe_runner` + E2 平稳 bootstrap/E3 参数敏感性/E4 成本敏感性已存在——统一考试直接调用，无需新建

### 5.4 消费基建接线点改写（R1 内部反查）

`src/zephyr/regime/` 整包已存在：F4/F14/F21/F22 的 regime 输出**接线目标=index_regime_panel / institutional_regime_scorer / risk_signal_builder / overlay_signals_builder**，不新造管道；regime_cycle_analyzer 供 F11 周期相位复用。

### 5.5 挖矿日志与下批长尾

| 轮 | 矿脉 | 判定 | 关键产出 |
|----|------|------|---------|
| R1 | 衰减/失效 + 情绪复合指数 | signal | 衰减先验、F21、regime 接线点、DSR 现成 |
| R2 | 台风灾损下游 + 港口库存上游 | signal | F7 增强、54% 校准、库存周期路径、大商所源 |
| R3 | 情绪×动量 + regime 模型 | signal | F22；R3-B（HMM 通识）=noise |
| R4 | 龙虎榜席位 + 两融 | **noise #1** | 席位因子=单来源待验证；两融搜索受阻 |
| R5 | 港口库存 DATA-GAP | signal | 大商所周报、补库季节性 |
| R6 | CICSI 组件可得性（内部） | signal | F21 组件 4/6 现成 |
| R7 | FinBERT 开源路线 | signal | F16 双层方案 |
| R8 | 日耗煤/信心补源（内部） | **noise #1** | daily_energy 待字段核验，无新发现 |
| R9 | A股适配闸 | signal | 回测四规则、反转佐证 |

**下批长尾矿脉（未挖）**：CICSI 消费者信心补源（统计局月度网页通道）；日耗煤替代源字段核验（macro_china_daily_energy）；龙虎榜席位因子多来源验证；GDELT/IMF 消费卡（第 4 批后）；台风灾损权重矩阵设计（等 appKey）。

---

## 6. 挖矿增补 Batch 2（2026-09-14，R10-R13：已在库未消费数据的另类用法）

Owner 追问"还能继续挖吗"——上批为时间盒封矿非枯竭。Batch 2 瞄准**库里有表/有数据但从未进消费方案**的矿：涨停板情绪、期权/期货衍生品情绪、政策文本。

### 6.1 新增因子候选

- **F23 涨停板情绪周期**（市场级日频情绪温度计，**数据已在库**：limit_up_down 3,474 行日更；limit_up_pool/daban 空表待任务激活）：连板高度/晋级率/炸板率三指标 → 六阶段状态机（启动→发酵→加速→分歧→回调→整固）。量化阈值（社区共识，多源交叉）：晋级率 >60%=高潮 / 40-60%=复苏 / <30%=退潮冰点；炸板率 >40%=预警。证据：[情绪周期六阶段模型](https://zhuanlan.zhihu.com/p/1925272125087917966)、[晋级率量化阈值](https://zhuanlan.zhihu.com/p/2032128108367721739)、[三大要素判断法](https://xueqiu.com/9137623309/155903269)、财联社每日快评实战口径。消费：market regime 输入（与 F21 月度 CICSI 互补=高频层）+ 短线风险日历。量：1d
- **F24 期权 PCR + 股指期货基差组合情绪**（机构情绪温度计；**数据空库=先补**：option_iv/futures_term 表在但基本无数据）：持仓量 PCR 顶底择时（[华福证券：2022 两个中期底部均提示](http://wt.microbell.com/data/2673057c43456dfa2f71aabb3a444881.html)；[华泰：持仓量 PCR 显著优于成交量 PCR](https://www.163.com/dy/article/L5NO35JO05568W0A.html)）；期权指标→期指多空年化 18.86%（[东证期货](https://www.fxbaogao.com/detail/4072506)）；基差分析 IH<IF<IC<IM 格局+合成期货升贴水剔分红（[东证基差框架](https://www.fxbaogao.com/detail/5065517)）。**口径共识**：PCR 剔除保险对冲干扰、与 IV/基差组合使用。DATA-GAP：option_iv/futures_term 数据源任务优先激活。量：补数据 1d + 因子 1d
- **政策文本→板块映射卡（挂起，来源闸未过）**：policy_expectation_analyzer/policy_theme_mapper 休眠模块 + event_calendar_registry 12 类事件为内部承接件；R12 外部证据搜索全程 429 受阻，按来源可溯闸暂不设计，下批补搜

### 6.2 后端实现路线（R13）

- **Qlib**（microsoft/qlib，数万 star）：数据→挖因子→训模型→回测全链路，事实标准；Alpha158 因子集已被 vnpy 集成——因子验证管线的参考架构
- **FinGPT**：开源金融 LLM，情绪分析可单卡（RTX 3090）跑——F16 与 FinBERT 并列的开源候选，选型时对比
- **QuantsPlaybook**（hugo2046）：100+ 券商金工研报复现（含情绪/关注度因子）——F1/F13/F16 的直接参考实现库（[GitHub](https://github.com/hugo2046/QuantsPlaybook)）

### 6.3 Batch 2 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|----|------|------|---------|
| R10 | 涨停板情绪周期（内部反查+搜索） | signal | F23 三指标状态机、阈值体系、limit_up_down 3474 行可算 |
| R11 | 期权 PCR/基差 | signal | F24 组合口径、华福/华泰/东证三源、空库 DATA-GAP |
| R12 | 政策文本映射 | **noise #1**（搜索全程受阻，来源闸未过） | 内部承接件确认，卡挂起 |
| R13 | 开源实现 | signal | Qlib/FinGPT/QuantsPlaybook 三路线 |

**边界重申**：研报文本/一致预期消费端属 P1-B 研报对话（其 expectations.py 已落地），本方案不越界。

**Batch 3 长尾（未挖）**：政策文本卡补源重挖；PCR/基差数据补源任务；Qlib/FinGPT 选型深挖（license/成熟度/维护度）；ETF 份额变动情绪（etf 表在库）；跌停家数/涨跌停比自建 A 股恐惧指标（与 F15 恐贪对齐）。

---

## 7. 挖矿增补 Batch 3（2026-09-14，R14-R20：长尾矿脉全开，**双噪音触发正式封矿**）

Owner 令"把矿挖干为止"。本批 7 轮（signal 5 / 连续 noise 2），**R19+R20 连续两轮噪音触发终止条件，挖矿正式结束**。

### 7.1 新增因子候选

- **F25 转债转股溢价率分位**（风险偏好 regime）：溢价率中位数=转债市场情绪核心温度计（中位数 50%+ =情绪偏乐观；低分位=股性占优）。证据：[证券时报：转债估值回落市场情绪依然偏乐观]、[万柏基金：价格/溢价率中位数分位判断]；应用三路径=分位择时/低溢价选券因子（[方正测算有效](http://pdf.dfcfw.com/pdf/H3_AP201903051302967135_1.pdf)）/负溢价套利。**组件已验证**：`bond_cb_jsl`（集思录，含溢价率）+ 库内 convertible_bond_list 1,051 行。量：0.5d
- **F26 宽基 ETF 份额变动反转**（长周期反向择时）：份额变动模块"反转效应突出、长周期择时显著"（[研报精选 2025 第 7 期](https://finance.sina.cn/2025-06-02/detail-ineyuazm1615798.d.html)）；东吴提示资金流与价格负相关（中小盘更明显）=逆指标；**分层纪律：宽基含国家队高抛低吸、主题 ETF 才是市场化情绪**（[财联社：宽基 16 周净赎回后重新净流入信号](https://www.cls.cn/detail/2395076)）。组件：`fund_etf_fund_daily_em`。需建份额日度积累任务。量：补任务 0.5d + 因子 0.5d
- **F27 政策文本→板块映射**（解挂）：[LLM 经济金融文本分析综述（2024）](https://cjoe.cjoe.ac.cn/CN/10.12012/CJoE2024-0208)+[中大林建浩团队多源 LLM 交易实证](https://dedsl.sysu.edu.cn/article/149)+[AI 产业政策文本量化（政策工具分类法）]三源支撑；内部承接=policy_expectation_analyzer/policy_theme_mapper/event_calendar_registry。量：2d（第 2 批后）
- **F8 补源确认**：`macro_china_daily_energy`=**沿海六大电库存日度数据（2016 至今，金十源）**——迎峰度夏/冬用电通道的核心上游数据缺口补上，待字段级核验

### 7.2 Batch 3 挖矿日志与封矿判定

| 轮 | 矿脉 | 判定 | 产出 |
|----|------|------|------|
| R14-15 | 恐惧/ETF/转债/商品/日耗煤组件（内部） | signal | F25/F26 组件、F8 补源 |
| R16 | 转债溢价率证据链 | signal | F25 闭合 |
| R17 | 政策文本重挖 | signal | F27 解挂 |
| R18 | ETF 份额择时 | signal | F26 闭合、宽基/主题分层 |
| R19 | 隔夜美股→A股联动 | **noise #1**（限流受阻，仅泛化共整文献） | 无新引文 |
| R20 | attention 反转窗口 | **noise #2**（限流受阻） | 无新引文 |

**封矿声明**：三批合计 20 轮（signal 15 / noise 4 / 其中 2 轮噪音系搜索通道限流所致）。因子位定稿 **F1-F27**。诚实备注：R19/R20 的噪音是搜索通道限流所致而非矿脉真空，换新鲜配额可复验——但这两条属"参数级打磨"（隔夜缺口、持有期窗口），不影响框架完整性。剩余不可挖项=永久禁区（卫星/电商/生活指数）+ 施工细节（字段核验类，施工时顺手做）。

### 7.3 最终施工排序（消费端定稿）

| 批次 | 内容 | 量 | 启动条件 |
|------|------|-----|---------|
| C-1（立即） | F7 台风日历 + F14/F15 币圈 + F4 BDI regime + F23 涨停情绪（数据全现成） | 3.5d | 无 |
| C-2（次周） | F10-F12 生猪 + F8 温度距平（含六大电核验）+ F16 FinBERT 试点 + F25 转债溢价率 | 4.5d | 无 |
| C-3（10 月中） | F1-F3 千股千评 + F13 人气榜 + F22 情绪调节动量 | 2.5d | 积累达标 |
| C-4（第 2 批后） | F18-F20 互动易 + F27 政策文本 | 4d | irm_qa 核对 |
| C-5（数据补齐后） | F24 期权 PCR/基差 + F26 ETF 份额反转 | 3d | 空库数据源激活 |
| 并行积累批 | EODHD 配额任务 + 台风 DDL + F26 份额积累任务 | 1d | 无 |
