---
ttl: task_bound
---

# 财报事实侧数据消费端设计（v1.0，2026-09-12）

> Owner 发起：财报数据齐了，接下来怎么用？哨兵行过滤是什么？要不要先设计模块？
> 定位：与《研报/一致预期消费端设计》（2026-09-12-expectation-consumption-design.md）成姊妹篇——**他消费"预期"（市场认为公司会怎样），本文消费"事实"（公司实际干了什么）**。预期侧 DS-228/229 已建，本文补齐事实侧，两锚合成完整 L2 基本面闭环。
> 数据前提（实测 2026-09-12）：income_statement 344,360 行 / balance_sheet 337,916 / cashflow_statement 308,632 / financial_indicator 383,156（覆盖 5,857~5,891 只，report_period 至 2026-06-30 中报已入，正常行公告至 2026-08-27）；PIT 查询层 pit_query.py 白名单 9 表已建。

---

## 0. 先回答 Owner 两问（大白话）

**问：哨兵行过滤规则是什么意思？**
我们的财报表里，有些行的"公告日"一列填的是假日期 1970-01-01（计算机纪元零点，等于"没填"）。分两种：
1. **整行垃圾**（三大报表各约 2,400 行）：报告期也是 1970，整行都是源头返回的空壳——像贴错标签的空罐头，直接扔掉即可，无害。
2. **危险的一类**（financial_indicator 35,180 行，占 9.2%；disclosure_plan 11%）：**报告期是真的**（比如 2026 中报），但公告日是假的。回测引擎查"3 月 1 日这天我能看到哪些财报"时按公告日过滤——公告日是 1970 = **永远可见**。结果：回测在 3 月就"开天眼"看到 8 月底才公布的中报，成绩虚高，实盘必亏。
**过滤规则** = 消费前加一道安检：公告日 ≤ 1970-01-02 的行，一律视为"公告时间未知"——要么剔除、要么按"最晚可能公告日"保守处理（PIT join 时不让它冒充老早公开）。这就是"哨兵行过滤"，一 条 SQL 条件 + 一层消费约定，成本极低，不做则所有基本面回测的可信度清零。

**问：是不是要先设计模块？消费什么？**
是。菜已齐（数据）、锅已备（回测引擎/评估体系），缺菜谱和厨师。本文就是菜谱。它消费：c3_fundamental 四张核心表（三大报表 + financial_indicator）+ 股东/主营辅助表，产出三层东西：①单季/TTM 派生层（把"累计数"翻译成"单季数"）②基本面因子族（喂回测出证据）③事件信号与否决器升级（喂 signal_fundamental / LLM 三 Agent）。

## 1. 第一性原理：财报数据的本质

财报 = **"公司经营事实"的双时点记录**：报告期（事情发生在哪三个月）× 公告日（市场什么时候能知道）。所有消费价值落在五个事实不变量 + 一个事件脉冲上：

| # | 不变量 | 数据投影 | 经典依据 |
|---|--------|---------|---------|
| ① | **盈利能力**（每单位资产赚多少） | roe_q / GPOA=(营收−成本)/总资产 | Novy-Marx 2013（与价值负相关侧） |
| ② | **成长**（规模在怎么变） | 单季营收/净利 YoY、QoQ 加速度 | 雪球 V4.2 框架实证 |
| ③ | **盈余质量**（利润里有多少真金白银） | 应计=(净利−经营现金流)/总资产 | Sloan 1996；A 股仍有效（剔除亏损股更强，中证1000 最优） |
| ④ | **财务安全**（杠杆与流动性） | 资产负债率/流动比率/商誉占比/Altman Z | Piotroski 2000；国盛多因子 14 |
| ⑤ | **财报信息质量**（报表可不可信） | 应收占比异常/所得税率波动/存货占比 | 国盛"刻画财报信息质量"（附注级项除外） |
| ⑥ | **公告脉冲**（事实落地的那一刻） | 公告日事件 → PEAD 漂移/超预期落差 | Bernard & Thomas 1989（pead_event_model 已在库） |

**一句话**：预期侧告诉我们"市场在想什么"，事实侧告诉我们"公司是什么"——**超预期就是两者的差，这是全项目基本面 alpha 的总闸门**。

## 2. 全网调研结论

### 2.1 经典学术（公式可直接抄）
- **Sloan (1996)** 应计异象：应计高→盈余持续性差→未来收益低。A 股实证仍有效（百度百科综述：公告期贡献 28% 年超额；农林牧渔/煤炭/家电/明显）。
- **Novy-Marx (2013)** Gross Profitability：(营收−COGS)/资产，"价值另一面"，不受杠杆税务扭曲。
- **Piotroski (2000)** F-Score：9 项 0/1 计数（ROA↑/OCF>0/应计↓/杠杆↓/流动比率↑/无增发/毛利率↑/周转率↑）——**对照我们字段：9 项全部可算**。
- **Fama-French (2015)** 五因子中 RMW（盈利）/CMA（投资）即①④的组合版。

### 2.2 最新机构与社区（2024-2026，A 股口径）
- **国盛多因子系列 14《刻画财报信息质量》**（刘富兵/李林井）：应收款账龄坏账比/折旧摊销政策偏离/所得税率波动率 → 财报信息质量评分；**结论：高质量分域中超预期漂移更强**——信息质量与预期侧（姊妹篇）天然耦合。附注级项（账龄）我们没有，做可得子集。
- **现金流实现率因子（券商量化专题，2026-04）**：指出传统应计"同期对比误判成长股"，改为**时间序列利润→现金流转化效率 + 现金流残差波动率**。RankIC 2.61%→2.93%，沪深300 RankIC 3.85%、多头超额 7.41%。**这是我们 FQ 族的首选改进版公式**。
- **雪球社区 V4.2~V4.5 框架**：单季拆解（Q2=H1−Q1）+ 四重过滤 + 11 因子（SUE_SQ 单季同比惊喜/QoQ_Acc 环比加速度/RevSUE 营收惊喜/GPOA/ΔQuality 三合一）——**社区实证版几乎就是我们 M1+M2 的蓝图**，可直接对照校验。
- **Kim-Muhn-Nikolaev《Financial Statement Analysis with LLMs》**（Chicago Booth, arXiv 2407.17866）：GPT-4+CoT 财报数字预测盈余方向 60.4% vs 分析师 52.7%。**注意：2025 年一作自查数据拟撤稿复核中——引用降级为"方向性证据"**；对我们 llm_fundamental_analysis 三 Agent 的启示不变：结构化数字喂 LLM 有真实增量，最终以我们自有 SOP-B 出证为准。

### 2.3 开源项目（借鉴模式，不引入）
| 项目 | 借鉴 | 不引入原因 |
|------|------|-----------|
| JerBouma/FinanceToolkit（4.9k★） | 500+ 财务公式**全透明可复算**的组织方式 + Piotroski/DuPont 实现 | 美股/FMP 数据源，无 A 股口径 |
| jlancaster7/factor-lab | **acceptedDate 过滤防前视**——与我们 announce_date PIT 同构，印证闸门设计 | 同上 |
| microsoft/qlib Alpha158 | 基本面字段极少 → 印证"财报因子无现成库" | 数据/回测语义不匹配 |

**结论：A股 PIT 财报因子库不存在现成品——公式有公开出处（华泰/国盛/经典文献），数据是我们独有的，自建即价值。**

## 3. 字段可行性（2026-09-12 system.columns 实测）

- income_statement：operating_revenue/operating_cost/**rd_expense**/operating_profit/total_profit/income_tax/net_profit_incl·excl_minority/eps_basic ✅（无"扣非净利润"列——用营业利润/营收口径替代，正好符合"营收比净利难操纵"的社区共识）
- balance_sheet：accounts_receivable/inventory/**goodwill**/total_current_assets·liabilities/total_assets/total_liabilities/short·long_term_loan/retained_earnings ✅ 应计、F-Score、Altman Z、商誉实算全够
- cashflow_statement：**ocf_net**/icf_net/fcff ✅
- financial_indicator（39 列）：**源数据已内置单季列 roe_q/roe_q_excluding/roa_q/ocf_revenue_q** + YoY 族（eps_yoy/net_profit_yoy/revenue_yoy/total_assets_growth）+ gross_margin/net_margin/debt_ratio/ebitda ✅ **M1 工作量大幅下调**——单季盈利指标不用自算，派生层聚焦"三大报表现金科目的单季拆分 + 跨表对齐"

## 4. 模块设计（五个消费模块）

### M0 质量闸门 `financial_data_quality`（一切消费的前置，最优先）
- **哨兵过滤规则**（成文为消费约定，所有基本面查询强制）：`announce_date <= 1970-01-02` 的行 → 三大报表按"整行垃圾"剔除（report_period 同为 1970）；financial_indicator/disclosure_plan 按"公告时间未知"处理——回测 PIT join 中视为**最晚公告**（保守可见性），日常查询直接剔除。
- 落地形态：①pit_query.py 白名单查询内嵌过滤子句（一处改，全消费方受益）②独立纯函数校验器（回测 data_handler 复核用，双保险）③覆盖率监控挂前端数据监管页（每股年报缺口=披露计划 vs 实际报表比对）。
- **为什么 M0 是 M1~M5 的前置**：9.2% 假公告日不处理，后面所有因子回测全部作废重跑。

#### M0 根因实测补充（2026-09-12 晚六探针，结论改写）
- **来源结构**：三大报表+financial_indicator 的正常行几乎全部来自 **bdpan 百度云归档**（data_source=bdpan，带真实公告日，供至 2026Q1，ingest 07-14~07-23）。**2026-08-27~09-08 一次 akshare 批量回填**把 fin_indicator 2025Q1~2026Q2 六期以无公告日方式重灌（该 akshare 接口本身无公告日期列）→ 与 bdpan 好版本构成**同键双写**。
- **风险重估**：2025Q1~2026Q1 五期双写哨兵（~27.5K 行）被同键 bdpan 好版本压住（LIMIT 1 BY announce_date DESC）→ **PIT 天然免疫，无害死重**，清理降级低优先。**唯一真风险 = 2026-06-30 中报 fin_indicator 4,874 行**（无好版本，PIT 永远可见=前视）；连带三大表中报仅 akshare 1,000 只入库（bdpan 中报归档未到）。
- **修复双源**：①bdpan 中报归档（是否已出待云盘确认）②akshare stock_yjbb_em 按期全市场（实测 20260630 期 11,449 行含"最新公告日期"，六期六次调用即可补日；该列为修正后口径=偏保守，PIT 安全）。
- **M0 哨兵过滤升级为 P0 前置**：修复落地前，中报 fin_indicator 消费"宁缺毋错"。

#### M0 云盘实勘 + 来源口径修正（2026-09-12 晚，BaiduPCS-Go 实勘 + ingest 批次探针）
- **口径修正**：`data_source='bdpan'` 是建表 DDL 的 DEFAULT 值（apply_market_tables_ddl.py L74），**不代表真来自百度云**。ingest 批次实探：正常行 = **2026-07-14 单日全历史重灌**（IS 340,959 / FI 347,976 行，report_period 1988~2026Q1）——与云盘"季报_CSV 每报告期一个文件（1989~2026Q1）"形状吻合，真源高度指向云盘季报 CSV 批（施工时以导入脚本/日志复核为准）。
- **云盘实勘**（/apps/bdpan/量化交易数据/上市公司财务信息/）：季报_CSV（每期一个全市场 CSV，1989~20260331）+ 季报_XLSX + 每日更新（2026-01~07 月度目录，最后文件 20260703.csv）+ 17 个单表 zip（利润表/资产负债表/现金流量表/财务指标/股东/质押/解禁/审计/预告/快报等）。**整盘自动同步 2026-07-03 16:24 停更（与 tick 归档同一时刻）→ 中报（2026-06-30 期）不在云盘**。
- **修复路线修正**：路 A（云盘中报归档）**排除**——无货；路 A'（新）= miniQMT download_financial_data2 三表+指标中报下载（**9/18 退役前窗口，先小样验证是否带公告日**）；路 B（akshare stock_yjbb_em 六期补日，已实测可用）为主力；路 C（pit_query 哨兵过滤）立即生效。另：**云盘同步线 7/3 停更影响全线（tick/分钟/财务/复权因子/新闻），需 Owner 决定是否重启同步器并登记 known_data_gaps**。

#### M0 执行记录（2026-09-12 深夜，D1 裁定三路落地）
- **路 B 数据修复（已完成）**：目标=无好版本的哨兵键 **5,020** 个（中报 4,874 + 其他期散布 146），yjbb 六期日期映射 **100% 命中**，INSERT 修正版本行 5,020 行（`data_source='akshare_yjbb_repair'`，只插不改零破坏，可逆=按 data_source 一键 DELETE）；复验**残余无好版本哨兵键=0**；公告日分布 08-22~08-28（中报季末）合理；与 baostock pubDate 交叉验证一致（600000=08-28 / 000001=08-15 / 300750=07-25）。踩坑三枚：①`exchange`/`symbol_canonical` 是 MATERIALIZED 列禁显式插入（TRAE-082 存量债——写入须用 system.columns 动态可插入列清单）②`ch_writer.query` 对 INSERT 返回空串≠失败（client.execute 返回 []）③ch_reader inject_final 与表别名冲突——SQL 自带显式 FINAL 即跳过注入。
- **路 C 代码落地（已 staged，网关提交中）**：pit_query.py `_SQL_AS_OF`/`_SQL_LATEST` 模板加 `AND {anchor_col} > toDate('1970-01-02')` 哨兵守卫（公告时间未知=PIT 不可见，宁缺毋错）；+2 守卫测试锁定；顺带修正白名单计数断言 9→10（research_report 扩表遗留）。tests/data/test_pit_query.py **49/49 全绿**。**PIT 语义实测印证两路缺一不可**：只插修正版时，8/1 时点查询仍会选中哨兵行（1970 永远满足 <=）——守卫是第二道必需防线。
- **巨潮裁定（Owner 委托）**：**不建全自动爬取/分类/入库管线**——一手源价值在对账校验非主供（主供双源已实测：akshare yjbb + baostock）；公告原文 PDF 非结构化，自动分类进库=另造文档解析管线，成本远超收益；真正需要原文=C4 文本管线（LLM 提取），届时一次投入两处收益。登记为**按需校验源**（对账探针抽查用，不常驻不爬全量）。
- **免费源实测（22:03）**：baostock 0.9.30 环境已装——季频四表（profit/balance/cash_flow/growth）带 **pubDate 真公告日，2026 中报已更新**（浦发 08-28/平安 08-15/宁德 07-25）；限制=比率+核心值非全科目、逐股查询。tushare 三表带 ann_date（积分门槛未核）。**退役后长期增量=baostock 披露季跑批 + yjbb 修日，免费闭环**。
- **待办移交**：①三大表中报全科目缺口（~4,500 只）→ miniQMT 9/18 前冲刺或 akshare 东财逐股（F1 批）②disclosure_plan 哨兵 11% 同法修复（低优先）③三表 1970 整行垃圾 + 五期双写死重清理（带备份 DELETE 批，F1）④云盘同步线停更登记 ⑤stock_indicator 估值回补立项（D4）。

### M1 派生层 `financial_derived`（statement 粒度，DS-230）
- **粒度**：(symbol, report_period, announce_date)——**不做每日物化**：5000 股×1200 日×全字段=行数爆炸且每日展开是回测引擎（pit_manager as_of join）本来就在干的事，不重复建设。
- **内容**：①跨表对齐宽表（income+cashflow+balance 按 (symbol, report_period) 对齐，只取公告日齐三方可见版本）②单季拆分：单季营收/净利/OCF = 本期累计 − 上年同期累计（同比口径）与 − 上季累计（环比口径，Q1 特判）③TTM 滚动四季 ④派生比率：应计/GPOA/单季毛利率/所得税率。
- **PIT 铁律**：派生只用 announce_date 已知的行；ReplacingMergeTree 修正公告 → 同键新版本派生行重算（sort key 含 announce_date，与源表同构）。
- 实现：DDL-as-Code（照 fundamental_research_report.py 先例）+ 夜间批（nightly_financial 后）+ 历史全量回补一次。

### M2 事实侧因子族（首批 8 个，逐个走 SOP-B，登记 factor_registry）
| 因子 | 构造（列名已核实） | 依据 |
|------|------|------|
| FQ-01 应计 | (net_profit_incl_minority − ocf_net) / total_assets（TTM） | Sloan 1996；A 股实证强 |
| FQ-02 现金流实现率 | 利润→OCF 时间序列转化效率 + 残差波动率 | 2026-04 券商专题（改进应计） |
| FQ-03 GPOA | (operating_revenue − operating_cost) / total_assets | Novy-Marx 2013 |
| FQ-04 单季盈利变化 | roe_q 同比差（ΔROEq） | 雪球 V4.x 实证 |
| GR-01 单季营收成长 | 单季 operating_revenue YoY | RevSUE 口径（营收难操纵） |
| GR-02 盈利加速度 | 单季净利 QoQ 变化率 | 雪球 QoQ_Acc |
| FQ-05 信息质量代理 | 应收/营收占比异常 + 所得税率波动（可得子集） | 国盛 14（附注项除外） |
| FQ-06 F-Score 计数 | Piotroski 9 项 0/1 求和 | Piotroski 2000 |
- 登记口径：factor_registry 现有 10 类中落 **quality/value** 两类（不新增类）；准入五要素齐全（出处/公式可复算/分类/PIT 声明/词表标签）；晋级门槛按 2026-09-12 成文判据（IS 2019-2023 |IC|≥0.02 + t p<0.05 + 覆盖 60%）。**value_factor（简易 PE proxy）作为在库条目做去马甲对照**（秩相关≥0.85 则挂 variant_of）。

### M3 事件族填坑（事实侧 × 预期侧的交汇点）★
- `event_factor_matrix` 的 EarningsFactorData（consensus_before/after/ear 已预留）→ **actual 供给方=本文**：业绩快报/正式报表的 eps_basic 按公告日供 actual；consensus 供方=姊妹篇 DS-229 consensus_daily。
- `pead_event_model`（MOD-SIG-110，production）已是 SUE 五档+20 日漂移的完整判定核（纯内存 DI 注入）——**只差装配批把实际 EPS（c3 财务表）和一致预期（DS-229）注进去**，不用新写判定逻辑。
- 业绩预告→正式报表"落差检测"（预告水分）：earnings_forecast（预告，1998 起）vs income_statement（实际）同键比对，输出 surprise_direction 事件流，negative_veto 可消费。

### M4 LLM 财报深读（Phase 2）
- llm_fundamental_analysis 三 Agent（testing）的 FundamentalInputBundle：financial_report 槽从"文本"升级为"结构化数字快照"（M1 派生宽表按 PIT 取当期可见版本渲染成表）+ M2 因子分位，LLM 做"数字体检报告"。
- 时机：等 C2/C3 因子出证 + P0 收口（GPT 财报论文撤稿风波提示：此路线有价值但必须自有证据背书）。

### M5 信号层挂接（SOP-C C5 解冻后）
- negative_veto 升级：goodwill_impairment_risk 从"上游模型判定"改为**实算**（goodwill/equity_incl_minority 比率 + 业绩预告亏损联动）——negative_veto 本来就是财报消费者，这是给它的弹药。
- 事实侧因子分位并入 FundamentalInputBundle 的 quantitative_score（0.6/0.4 权重槽已有）。

## 5. 与现有体系的咬合（已逐文件核实）

1. **pit_query.py**：白名单 9 表已含四张财报表；M0 过滤子句 + M1 派生表登记白名单（period_col=report_period 照现有模式）。姊妹篇 D3 的"时间锚列参数化"一并处理。
2. **factor_registry**：准入五要素/生命周期五态/晋级门槛 2026-09-12 刚成文——FQ/GR 因子是这套新判据的第一批考生。
3. **backtest_backlog.yaml**：SOP-A 产物、预注册禁挪——**注意：因子级回测对象走 experiment_registry（factor_eval 类型，schema 已支持）+ backlog 因子条目**，与姊妹篇同规矩。
4. **回测引擎现成**：multifactor_pit_backtest（5 层 PIT 断言）+ layered_backtest + ic_ir_calc = SOP-B ④⑤⑥ 的 L0 引擎，零新建。
5. **数据工程债（M2 依赖）**：①stock_indicator 仅 2026-08/09 两月——**估值倍数历史回补（约 5000 股×1200 日）需 DataScheduler 立项**，C3 翻译试点同款欠账，估值类因子（VL 族扩展）等它；②daily_valuation 整表黑名单勿用。
6. **边界声明**：`factor/expectations.py`（姊妹篇 C2 预备件）= 预期侧六因子；本文 M2 事实侧因子独立成文件（建议 `factor/fundamentals.py`），互不侵入；M3 是两边的汇合点，actual/consensus 各供一半。

## 6. 分期施工

| 期 | 内容 | 依赖 | 量级 |
|----|------|------|------|
| **F1** | M0 哨兵闸门（pit_query 过滤+校验器+监控面板）+ M1 派生表（DDL+回补+DS/品类登记） | 无（数据已在库），不占回测通道，**可立即动工** | 2-3 天 |
| **F2** | M2 首批 8 因子：登记→SOP-B ④⑤⑥→experiment_registry 台账 | F1 + **回测通道空闲（排队 P0 后）** | 每因子 0.5-1 天 |
| **F3** | M3 事件族：pead 装配批 + EarningsFactorData 填坑 + 预告落差检测 | F1 + 姊妹篇 DS-229 | 2-3 天 |
| **F4** | M4 LLM 结构化快照喂三 Agent | F2/F3 出证 + P0 收口 | 2-3 天 |
| **F5** | M5 信号挂接（negative_veto 商誉实算 + bundle） | SOP-C C5 解冻 | 1-2 天 |
| 并行债 | stock_indicator 估值历史回补立项（数据工程） | Owner 批 | 独立排期 |

## 7. 裁定结果（Owner 委托，2026-09-12 晚裁定；施工落地时按 RULE-RULING 登记 ruling_registry）

| # | 裁定 | 分析过程（第一性原理 → 证据 → 结论） |
|---|------|--------------------------------------|
| D1 | **哨兵三层防御**：①立即落 pit_query 哨兵过滤（防前视兜底）②9/18 前 miniQMT 拉中报三表+指标（先小样验证带不带公告日）③失败则 stock_yjbb_em 六期补日（UPDATE 前备份）。残余不可修键登记 known_data_gaps+按"最晚可见"；双写死重低优先清理；**云盘同步线 7/3 停更单独登记并请 Owner 决定是否重启** | PIT 的本质=可见性时钟，不确定性必须往保守方向用（1970=永远可见是把不确定当最乐观）；六探针+云盘实勘钉死根因与无货，修复只剩 QMT/akshare 两路 |
| D2 | **statement 粒度**（每股×报告期×公告版本），不做每日物化 | 事实的真源粒度=披露事件；"某天可见什么"是查询语义非存储语义。预物化=制造第二真源→双写漂移（本次乱象即活教材）。机构（qlib/聚宽/米筐）全部 PIT API 现查现展开；100% AI 开发下维护物化管道是最易烂的长期负债，AI 强在写查询弱在养管道 |
| D3 | **双登记，串行对照**：FQ-01 应计先跑出证 → FQ-02 现金流实现率作对照，IC 显著优才转正否则挂 variant_of | 去马甲机制现成（秩相关≥0.85）；两公式纯函数成本≈零；稀缺的是回测通道不是函数——先登记不亏，双跑浪费 |
| D4 | **立项回补 stock_indicator 估值历史**（~5000 股×1200 日），与 D1 修复同批，走"9/18 退役前窗口冲刺" | 估值因子族全灭+C3 翻译试点被卡（数据地雷②）；CH 量级无压力；估值分位是 regime/估值带的地基（S2 已在用指数级估值，个股缺位）；miniQMT 退役是硬 deadline，所有依赖它的采集集中窗口内 |
| D5 | **首发顺序：FQ-01 应计 → GR-01 单季营收 → FQ-03 GPOA → FQ-06 F-Score** | 文献强度（Sloan A股实证+公告期 28% 超额）×字段就绪（三表现成）×与预期侧联动（RevSUE 为超预期事件打底）；F-Score 是复合计数，依赖前三单项先验证 |
| D6 | **F1（闸门+派生层+哨兵修复）立即并行不占回测通道；F2 因子回测一律排队 P0 之后；D1/D4 数据修复归"退役前窗口冲刺"最高优先** | P0=生死线（9/12 已拍板优先级）；数据工程与回测不抢通道；9/18 硬 deadline 决定冲刺顺序 |

## 8. 出证与引用清单

- 学术：Sloan 1996（The Accounting Review）；Novy-Marx 2013（JFE）；Piotroski 2000（JAR）；Fama-French 2015；Bernard & Thomas 1989；Kim-Muhn-Nikolaev arXiv 2407.17866（2025 撤稿复核中，降级引用）
- 机构：国盛量化多因子系列 14《刻画财报信息质量》；现金流实现率因子专题（2026-04，腾讯证券转载券商研报）
- 社区：雪球 V4.2~V4.5 单季拆解 11 因子框架；应计异象 A 股实证综述（百度百科学术引用链）
- 开源：JerBouma/FinanceToolkit；jlancaster7/factor-lab（acceptedDate 防前视）；microsoft/qlib
- 项目内契约：pit_query.py（白名单+LIMIT 1 BY）；factor_registry.yaml 准入判据头（2026-09-12）；negative_veto.py L46-111；pead_event_model.py（MOD-SIG-110，SUE/漂移核）；event_factor_matrix.py EarningsFactorData；factor/expectations.py（预期侧分工边界）；value_factor.py（去马甲对照）；multifactor_pit_backtest / layered_backtest（评估引擎）
- 实测探针：c3_fundamental 四核心表行数/覆盖/哨兵行画像（2026-09-12 本会话，system.columns + countIf）
