---
ttl: task_bound
rule_form: data
verifiability: manual
title: 通宵战役 Owner 汇编包（st-bizmine-op-20260919，W2.5）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: 完成（纯合成与引用，零新计算；全部数字注明出处报告路径）
session: st-bizmine-op-20260919
parent_context: bizmine_general_order.md §6 W2.5 + bizmine_campaign_ledger.md（全部车道索引）
note: 下文出处路径均相对 docs/_working/bizmine_night/；「红蓝」=redblue_report.md。本包不含部署结论；全部日线结论=暂定（kline_daily.adj_factor 恒 1，待复权链修复后复核）。
---

# 业务层 Alpha 挖掘通宵战 · Owner 汇编包

## 1. 一页纸总结

### 1.1 今晚干了什么（一句话/车道）

| 车道 | 一句话 | 出处 |
|---|---|---|
| R 灰度轴 | 17 幸存者×vol_pct 灰度桶条件化重算：POOLED LOW 1.12/MID 0.21/**HIGH 2.48**，收益集中高波桶（红蓝勘误后 HIGH 最优 **13/17**、MID 最差 **12/17**），边界 ±0.05 方向稳 | regime_axis/survivor_regime_report.md §2/§5 |
| T 做T | 主观做T方法库（12+4 手法三路来源）+条件化窄测官方判定 **TERMINATE**（G1 挂：uplift 1.284<1.5）+币圈研究报告 | t0_regime/t0_regime_narrow_test_results.md 等 |
| F 因子 | 因子挖掘 SOP v0.1+缺口报告 G1-G10；IC 大海选 126 值得考→38 可映射全量入册→top-20 待考池；F3 五面板 21 因子探针 | factor_sop_screen/{factor_mining_sop_v0_1.md,screen_report.md,altdata_probe_report.md} |
| L1 量能 | 18 档→15 组全考：**2 PASS**（CORREL/BETA，risk_off 防守形态）/13 RED；E4 正考双不通过→转条件化窄测池 | volume_family_l1/exam_report.md |
| S 板块 | 442 清洗板块 8 信号 IC+周频轮动：S8 唯一双期同号；轮动指数口径 1.0-1.25 坍缩至 ETF 口径 0.13-0.54=**可实现性未证实** | sector_family/d_sector_family_report.md |
| P 图形 | 78 值得考→103 cell 全事件研究（1580 万事件）：塔形底 +3.60%/双底 +2.23%/塔形顶 -3.67% 最稳双向 | pattern_events/report.md |
| PATX 图形窄考 | 6 事件正式判定：**3 PASS**（塔形底 2.89/双底 1.42/塔形顶 2.37 统计口径）+3 RED | pattern_narrow_exam/narrow_exam_report.md |
| PATD 定义审计 | 62 行对标：**material-wrong 43**，规范重考翻案 5 形态——「引擎错不是形态死」；11 条引擎工单 | pattern_definition_audit/pattern_definition_audit_report.md |
| PB 图形补扫 | 159 条「缺数据」三分归因：23 预审误判已覆盖+5 可补扫+32 数据债+96 待查（引擎缺检测器） | pattern_backfill/pattern_backfill_inventory.md |
| E ETF | 510300 择时 60 行零候选+ETF 轮动 42 行：G_BDION 门改善 MDD（-40.0%→-11.4%）、G_HIGH 减值（数字以 csv 为准，见勘误） | etf_family/etf_lane_report.md §7 |
| ETFT0 高波做T | 三宇宙全 GREEN_LANDS：A 6绿4黄/B 13绿25黄62红（簇条件化）/C 17绿3黄零红——Owner「不外推」裁定成立 | etf_t0_retest/etft0_screen_report.md |
| CRY 币圈 | 双卡双 RED：VWAP 回归（毛边际 -0.73bp）+funding carry（OOS 净年化 4.09%<5%）；费率作废条款触发 | crypto_probe/{vwap_revert_results.md,funding_carry_results.md} |
| B1 传感器 | 三件批算：S1 指数 **valid**（rho=0.800）/S0-1 情绪 h20 **valid**（标题降级口径）/S0 宏观不可判（四腿缺三） | sensors_b1/sensor_monotonicity_b1_exam.md |
| IND-A/B/C 指标 | TI 宽表 **163 列三切片全筛完**（1320 行/片全量入册）：50/54/53 列负向短反转主调；top-10×3 待考池 | indicators_sweep_{a,b,c}/report.md |
| ALT-B 另类 | 四面板 24 信号全量入册：**0 项达提名线**，8 项待扩样本观察档；宏观 naïve 开关全面劣于买入持有 | altdata_probes_b/altdata_b_report.md |
| MID 洼地 | 38 候选按 vol_pct MID 桶二筛 top-10；**「总体平庸但 MID 显著」=0 条**——MID 荒漠在日频截面因子层无免费解 | mid_valley/mid_valley_report.md |
| TICK tick执行 | 三模型×三标的 9 官方格全 FAIL：执行改善上限 2.4bp、穿越触发中位移动为负——#304 第四环 | tick_t0/tick_t0_results.md |
| TICKM tick矩阵 | 72 格基线全落：54 ok+18 insufficient，**0 亮点**（BH q 全 1.0，p50 -6.39bp=成本线） | tick_matrix/tick_matrix_report.md |
| ALGO 算法 | 全网 16 组检索：**否决全粒度全组合矩阵、改有界矩阵 ≤36 格/波**；top3 伪码级设计段就绪 | algo_mining/{algo_mining_digest.md,matrix_necessity_verdict.md} |
| 红蓝对抗 | 12 车道四向攻击+蓝队复核：**10 PASS/2 ISSUE-已修，零头条被攻倒**；计数勘误 13/17、12/17 | redblue_report.md §0/§8 |

（**销账批 W2.6 已落地**（本包初稿落盘后 1 分钟内）：①backtest_backlog 写回 19 条——BT-P1-032 勘测销账（#304 四环关闭）+B1 三传感器（001 valid/006 valid/005 pending）+B0 15 条 exec_quality valid+BT-P0-003 pending（commit 0cd61d2b2f）；②known_data_gaps.yaml 批量登记 8 条目数据缺口（commit 421b9dc2e7，销账会话=st-bizmine-co-20260919）——§7 数据债的注册表正门归宿已落。）

### 1.2 三个最大发现

1. **灰度状态轴（Owner 主纲）跨车道成立，且有明确边界**：策略层收益集中 HIGH 桶（POOLED 2.48 vs MID 0.21，极差 2.27；regime_axis/survivor_regime_report.md）；因子层「状态一换，因子选择整个换血」——趋势族 risk_on 失效/risk_off 强负（factor_sop_screen/screen_report.md §3）、价值/小盘只活 risk_off（factor_sop_screen/altdata_probe_report.md §3）、量能防守族超额集中 risk_off（volume_family_l1/exam_report.md §四）。边界：4 条反例策略反向、MID 是 U 形洼地、「HIGH 桶增益」在 IND 车道 OOS 衰减（indicators_sweep_c/report.md §2）、板块横截面无稳定桶模式（sector_family §4）。
2. **做T 四环证据链闭合，但死因从「成本」前移到「缺信号」**：#304 成本数学→真实信号 RED→条件化仍 TERMINATE→tick 执行全灭（改善上限 2.4bp vs 缺口 12-17bp）；Owner「低波样本不外推」裁定被证实——高波宇宙振幅 108.8bp（池化）进绿区带，栖息地真实存在（etf_t0_retest/etft0_screen_report.md §4）。
3. **图形「引擎错不是形态死」坐实**：62 行对标 material-wrong 43，5 形态翻案（上吊线/塔形顶方向翻转、晨星从无效变 +0.93% 真信号、流星线/Hikkake 反向是伪影）——P 报告 RED 名单 majority 应改判「实现错」；任何图形考试必须先过定义审计再定罪（pattern_definition_audit/pattern_definition_audit_report.md §7.2）。

### 1.3 做T 终局裁定（一段）

A股 ETF 15min 级做T 建议终结（#304 维持关闭，四环证据独立同向）：①无条件成本数学不可行（S2 裁定书，承 T 卡）；②真实信号逐笔 RED（T.md +0.88bp/边）；③行情条件化后仍不可行——高波桶 uplift 1.284<1.5 门，所需捕获率 35.5% 仍为可持续带（5-15%）的 2-3 倍（t0_regime/t0_regime_narrow_test_results.md §3）；④tick 执行侧无救援——被动执行改善中位 0.0-2.4bp，穿越型触发在零执行成本世界的中位移动本身为负（-8.7/-27.0/-30.5bp，tick_t0/tick_t0_results.md §3-4；tick_matrix 72 格 0 亮点合流）。但终局不是「日终局」：振幅确实存在且随灰度上行（L<M<H 单调），执行不是瓶颈（上限 2.4bp），**缺的是正毛信号**；Owner 裁定「510300 判定不外推高波宇宙」成立，三宇宙 GREEN_LANDS 把做T 经济学从 hopeless 移到 borderline（绿区≠净边际为正，最优仍需捕获 14-24%）。剩余正门=信号侧新卡（预注册）+港股通簇真日内回转，见 §4。

### 1.4 到组合 Sharpe 2.0 的路线图（一段）

基线：现状池净 0.307→毛清账 1.204→alpha 缺口 0.796→低相关组队后现可达 **1.541**→距 2.0 剩 0.46（组合层，regime_axis/teaming_regime_brief.md §3）。弹药账两笔：零相关物理下限=1 条 @H2 OOS Sharpe 1.28 或 4 条 @0.64；按实测相关结构（新成员对账本 ρ≤0.2）**≈4 条 @H2 OOS Sharpe ≥1.4**（或 ≈8 条 @1.3），折算≈再打 1-2 场 80+ 候选全流程战役且头部质量不衰减。结构上 **HIGH 桶不缺弹药（13/17 挤在 HIGH），MID/LOW 最缺**：MID 荒漠（POOLED 0.21）在日频截面因子层无免费解（MID 车道「总体平庸但 MID 显著」=0 条，mid_valley/mid_valley_report.md §2）——**MID 靠组合层条件化（降仓/降换手）不靠换因子**；仅存的因子窄门=三条相对独立 MID 候选（缺口ATR ρ0.149/二进三 ρ0.468/UTAD ρ0.666）+非日频结构数据（资金流/龙虎榜/日内）。

## 2. 全库覆盖度矩阵

状态：✅全测完 ｜ ◐筛完待考（升考试须预注册卡）｜ ⛔数据缺。

| 库/数据面 | 状态 | 覆盖与结论（出处） |
|---|---|---|
| 图形库·值得考 78 条→103 cell | ✅ | 全事件研究（1580 万事件/639 万股日基线/2021-09..2026-09）：塔形底/双底/塔形顶最稳双向，经典教材形态系统性反向（pattern_events/report.md） |
| 图形库·窄考 6 事件 | ✅ | PASS 3/RED 3，双档 Bonferroni+T+1 开盘 PIT 口径（pattern_narrow_exam/narrow_exam_report.md） |
| 图形库·「必死」50 条 | ✅（抽样 18） | 判死与实现无关成立；但 12/18「无机械口径」理由过强（fib/谐波/圆弧有公开算法）；1 条事实错误（CBS 实已物化 32 条）（pattern_definition_audit/pattern_definition_audit_report.md §5） |
| 图形库·「缺数据」159 条 | ✅归因/◐可补扫 | 23 预审误判已覆盖+3 部分+5 可补扫（周线反转等，历史未跑）+32 数据债⛔+96 待查（引擎缺检测器，含 8 DL 套件）（pattern_backfill/pattern_backfill_inventory.md §2）；PATD 另证 17 条「缺数据」实已物化+双顶已物化 59 万事件（pattern_definition_audit/pattern_definition_audit_report.md §5） |
| 指标库 technical_indicator 163 列 | ✅筛完/◐待考 | 三切片 55/54/54 全测（每片 1320 行全量入册，IS 2021-01 起/OOS 至 09-18）：负向短反转主调，top-10×3 待考池（indicators_sweep_a/report.md、indicators_sweep_b/screen_report.md、indicators_sweep_c/report.md） |
| factor 库 126 值得考 | ✅筛完/◐待考 | 38 可映射全量入册（114 行）+top-20 待考池；88 skip（板块分类/资金流/日内/事件族等五类）（factor_sop_screen/screen_report.md §1） |
| 另类 9 面板 | ✅探完/◐观察档 | F3 五面板 21 因子（252 组：价值/小盘、龙虎榜席位、分歧度有真信号；计数类零结果）+ALT-B 四面板 24 信号（101 行：0 提名，8 观察档）（factor_sop_screen/altdata_probe_report.md；altdata_probes_b/altdata_b_report.md） |
| 币圈 | ✅两卡全考/⛔多处缺 | funding 小时级 466 万行 ✅双卡双 RED；行情仅日线 13 个月◐；清算流空表（1 行）⛔；现/永双腿行情缺=basis 不可测⛔（t0_regime/t0_crypto_research.md §1；crypto_probe/funding_carry_results.md §5） |
| 传感器三件 | ✅/⛔ | S1 指数 valid（rho=+0.800 全 8 格，+2 档结构性不可达=规格发现）；S0-1 情绪 h20 valid（标题-only 降级口径，持久化窗全落 holdout 故重算）；S0 宏观不可判（Shibor 76 行/两融 2 月/政策无表=四腿缺三，仅海外腿探针）（sensors_b1/sensor_monotonicity_b1_exam.md §2-4） |
| 板块族 880 | ✅/⛔ | 469 板块（清洗 442）8 信号 IC+轮动+灰度条件版全测：S8 唯一双期同号；ETF 口径可实现性未证实；涨停占比信号数据双缺口⛔；成分快照仅 2 天⛔（sector_family/d_sector_family_report.md §1/§3-5） |
| ETF 宇宙 | ✅ | 510300 择时 12 规则×5 变体 60 行零候选+轮动 4×5×2 42 行（etf_family/etf_lane_report.md）；ETFT0 三宇宙 130 标的 532+532 判定位全披露（etf_t0_retest/etft0_screen_report.md） |
| tick | ✅/⛔ | tick_data 88.57 亿行/2025-01 起 21 个月（个股深样本）：TICK 三模型全 FAIL+TICKM 72 格基线 0 亮点；tick_depth_5 仅 40 日⛔（M3 降级披露）；auction_book 22 天/17 全快照⛔；2022-2024 tick 不在库⛔；bdpan 时代 L1 bid/ask 100% NULL⛔（tick_inventory_total.md；tick_t0/tick_t0_results.md §7；tick_matrix/tick_matrix_report.md §10） |
| 分钟线 | ✅在库/⛔冷归档 | kline_1min 4.7 年+kline_etf_1min 至 09-18（T3/E/ALGO 已消费）；E 盘冷归档 2000-2021 分钟线（1min 255 月/ETF 1min 2005-2018）未挂回=已登记数据债（tick_inventory_total.md；台账 06:0x E 盘盘点行） |

## 3. 考试结果册

### 3.1 PASS 名单

| 对象 | 读数 | 限定条件 | 出处 |
|---|---|---|---|
| 塔形底/向上 | 年化超额 Sharpe 2.89，NW t 8.42，+30.7bp/日成本后，6/6 年，4733 检验严格档+常规档双存活 | **PATD 规范版对照**：引擎 +3.6% 大部分是松规则（长下影+两根不跌）超跌反弹 alpha，规范塔形底（跌≥8%+平台+站上 5% 确认）+0.81% 仍真活但语义错位；PATX 考的仍是引擎事件集，建议补规范版对照（→§6②） | pattern_narrow_exam/narrow_exam_report.md §1；pattern_definition_audit/pattern_definition_audit_report.md §7.1 |
| 双底/向上 | Sharpe 1.42，NW t 4.15，6/6 年，双档存活 | 20 日窗衰减（NW 1.77<2），有效性集中 5-10 日；规范双底（颈线确认）+1.27% 同向（事件数 1/64） | 同上两处 |
| 塔形顶/向下 | **PASS（统计口径）**：Sharpe 2.37，NW t 3.54，全 10 桶两轴同号=唯一真全天候 | ⚠融券可执行性未证（费率 8-10%/年+券源未建模）；复权敏感度高（红蓝 §3：修复后幅度将缩）；PATD 规范版方向翻转（+0.60% 反教材）——统计 PASS 基于引擎松规则事件集 | pattern_narrow_exam §1/§5；redblue_report.md §3 |
| ETFT0 宇宙 A 行业/主题 ETF | 6 绿 4 黄零红；双窗绿=588200 科创芯片（req 0.185/OOS 0.134）、512480 半导体、512170 医疗、512010 300 医药 | 589090 仅 3 日 INSUFFICIENT；绿区≠净边际为正（诚实条款） | etf_t0_retest/etft0_screen_report.md §3 |
| ETFT0 宇宙 B T+0 类 | 绿区簇 13 只=全部港股通/恒生科技/创新药：513330 恒生互联网（0.195/0.227 双窗绿）、513130/513180 恒生科技、159792、513060 等 | 债券 37+黄金 5+美日欧宽基 62 全红；池化 RED——簇条件化披露；**B 簇=唯一真日内回转+经济学达标** | 同上 |
| ETFT0 宇宙 C 高波个股 | 17 绿 3 黄零红（最强宇宙）；top=300561 汇金科技（req 0.141/OOS 0.196 双窗绿）、300469 信息发展、300781 因赛集团、300757 罗博特科等 | T+1 底仓T 上界读数；OOS H 桶 8 绿 12 黄零红 | 同上 |
| L1 CORREL（risk_off 防守） | 沙箱三关 PASS：OOS 毛超额 +9.88bp/日，DSR 0.6223 | **E4 正考不通过**（IS 参考段净 sharpe -0.606，不可跳级语义）→转 risk_off 条件化窄测池（risk_off 桶 +30.0bp/日形态已量化，新卡另预注册） | volume_family_l1/exam_report.md §三/§五 |
| L1 BETA（risk_off 防守） | +8.40bp/日，DSR 0.6348 | 同上（risk_off 桶 +25.4bp/日） | 同上 |
| S8_rank_chg20/h20 板块轮动强度 | 唯一 IS/OOS 双期 \|t\|≥2 同号（+0.11/+0.11） | 边缘显著，复权复核后可能掉线（redblue §3 中敏感）；筛≠考 | sector_family/d_sector_family_report.md §3；redblue_report.md §0-S |
| R 三档观察档（组队备料） | 稳健 1.815/均衡 1.838/进攻 1.470（整窗实测） | 全部「观察档」硬约束：成员全带 E4 存疑 verdict；B-15 待 Owner，禁部署 | regime_axis/teaming_regime_brief.md §1 |

### 3.2 RED 名单（含死因一句话）

| 对象 | 死因一句话 | 出处 |
|---|---|---|
| Marubozu/向上（PATX④） | T+1 开盘入场吃掉隔夜跳空翻负：成本后 -1.37，拥挤信号日系统性更差 | pattern_narrow_exam/narrow_exam_report.md §1 |
| 流星线/向下反向（PATX⑤） | 0/6 年方向不符；PATD 判定其反向是无前提定义的伪影（规范版无任何方向） | 同上；pattern_definition_audit §7.1 |
| 一字涨停板/向上（PATX⑥） | 双口径挂：逐笔中位 -7.31% 长尾伪影+拥挤季 -25.2bp/d+次日开盘常不可成交（回测口径本身乐观） | pattern_narrow_exam §1 |
| L1 量能族 12 组+ROLLVAR | 毛超额不足或 DSR≤0.5：ADOSC +11.6 过关①但 DSR 0.115 拦下；FORCE_INDEX -16.82 全表最差 | volume_family_l1/exam_report.md §二 |
| E 车道 510300 择时 | 零候选：无任何版本过「净 Sharpe>1 且 MDD<15%」双门；regime 门对 510300 不加值 | etf_family/etf_lane_report.md §2（数字以 csv+勘误为准） |
| S 轮动 ETF 口径 | 指数口径 1.0-1.25 坍缩至 ETF 口径 0.13-0.54 且跑不赢自身等权=不可交易溢价（AI 板指数 +100% vs ETF +38%） | sector_family/d_sector_family_report.md §5 |
| CRY T0-PRERG-01 VWAP 回归 | 毛边际 -0.73bp<12bp 门，对照差 -2.04bp（p=0.908）=对无条件出手无增量 | crypto_probe/vwap_revert_results.md §3 |
| CRY T0-PRERG-02 funding carry | OOS 净年化 +4.09%<5% 门；动用率 1.70/5 槽为瓶颈；HL 真实费率下 ≈3.0% 更红（RED 对费率修正稳健） | crypto_probe/funding_carry_results.md §3-4 |
| TICK 三模型×三标的 | 9 官方格全 FAIL：穿越型触发中位移动为负（-8.7/-27.0/-30.5bp）=零执行成本世界仍亏；M2 被动改善仅 0.0-2.4bp 且出场腿 86% 超时转吃单 | tick_t0/tick_t0_results.md §3-4 |
| TICKM 72 格 | 0 亮点：54 ok 格最小 p=0.166、BH q 全 1.0；全格 p50 -6.39bp=Q5 成本线（中位毛捕获≈0） | tick_matrix/tick_matrix_report.md §5/§6 |
| ALT-B 宏观择时面 | naïve BDI/BDTI 开关全面劣于买入持有（IS Sharpe -0.004/-0.291 vs BH +0.234） | altdata_probes_b/altdata_b_report.md §4 |
| 经典教材形态（P 层） | Hammer/Hikkake/一阳穿多线系统性反向——PATD 改判：majority=实现错非形态死（一阳穿多线规范版补要件后 6/6 年仍反向=真形态死） | pattern_events/report.md；pattern_definition_audit §7.2 |
| F3 零结果面 | consensus 计数类 IC≈0（1094 日）；money_flow（44 日）/margin（35 日）功效不足非证据 | factor_sop_screen/altdata_probe_report.md §2/§4 |

### 3.3 全部待考池汇总（筛≠考，升考试须预注册卡+沙箱+E4）

| 池 | 条目 | 出处 |
|---|---|---|
| P 图形待考池 | 14 cell（升池不判 PASS） | pattern_events/report.md（台账 03:1x 行） |
| IND-A top10 | adosc(-0.97)/ar_26/boll_bw/bull_power_13/atr_14/fi_13/boll_breakout/fractal_high/correl_30/apo（十列三桶全同号，OOS 全存活） | indicators_sweep_a/report.md §4 |
| IND-B top10 | kc_lower(+0.67)/histvol_20(-0.67)/natr_14(-0.66)/md_14(+0.45)/ma_60/gmma_l60/kst(-0.43)/gmma_l50/gmma_l45/gmma_l40（实为超卖反弹+低波+反转三家族，建议按族抽代表 kc_lower+histvol+kst+md_14） | indicators_sweep_b/screen_report.md §1 |
| IND-C top10 | parkinson_20(-0.641)/yang_zhang_20/rogers_satchell_20/pvi/pvt/trange/var_20≡stddev_20/rsi_24/wvad_24（低波/波动率估计器族横扫；升考须与 L1 15 组归并去重） | indicators_sweep_c/report.md §1 |
| F top20 | 历史天量 -0.76IR/二进三断板/地量 +0.60/ATR14/布林收口/下方缺口/缺口ATR/底部量能节奏/UTAD/假突破/MACD零轴（risk_on 失效型）/RS/立桩量/高位振幅/20日均线趋势/乖离率/均线排列/月线支撑/红多绿少/放量突破（头部=低波+量能反转异象族；状态反号证据=§5 方法论节） | factor_sop_screen/screen_report.md §2 |
| MID top10 | 历史天量/二进三断板/地量/ATR14/假突破/下方缺口/布林收口/缺口ATR/UTAD/MA20斜率（三档全同号；相对独立仅缺口ATR 0.149/二进三 0.468/UTAD 0.666；10 卡 frozen：G1 MID 条件化窄测 Sharpe≥1.4+uplift≥1.5） | mid_valley/mid_valley_report.md §2；prereg_card_mid_valley_top10.md |
| ALT-B 观察档 8 | auc_gap-eod -0.173（94% 同号）/auc_vratio-t1 -0.079/auc_imb-eod +0.038（未达 0.05 保留观察）/news_sent-intra **+0.262**（90%）/news_buzz +0.063/hot_rankchg +0.093/lianban_up +0.078（连板高度单调）等——均 n=17-92 天 2026 高波单 regime，扩样本后重筛 | altdata_probes_b/altdata_b_report.md §6 |
| L1 条件化池 | CORREL/BETA risk_off 条件化窄测（E4 未过的唯一后路） | volume_family_l1/exam_report.md §五 |
| F3 提名建议 | 龙虎榜席位净买（h5 +0.079/h10 +0.054）+分歧度（净段 +0.0275）升预注册卡候选 | factor_sop_screen/altdata_probe_report.md §2/§7 |
| S 双期同号 | S8_rank_chg20/h20（+0.11/+0.11，边缘） | sector_family/d_sector_family_report.md §3 |

## 4. 做T 终局专节

**四环证据链**（各自独立、同向，前三环=t0_regime/t0_regime_narrow_test_results.md §5，第四环=tick_t0/tick_t0_results.md §5.3）：

1. **#304 第一环·成本数学**：510300 15min 中位 bar 振幅 26bp vs Q5 往返 8.4bp→需捕获 32%（S2 裁定书，承 T 卡）。
2. **第二环·真实信号**：真实信号逐笔考试 RED（T.md +0.88bp/边）。
3. **第三环·行情条件化**：T3 官方 TERMINATE——高波桶 uplift 1.284<1.5 门；req_cap 从 45.6% 压到 35.5%，仍为可持续带 2-3 倍；考试段（2026-06..09 高波期 69.4%）同判（t0_regime/t0_regime_narrow_test_results.md §3）。
4. **第四环·tick 执行**：9 官方格全 FAIL；同触发配对 M2-M1 改善中位 0.0bp（报价 era +2.39bp=执行改善全部实测上限）；决定性事实=穿越触发的 trigger-to-trigger 中位移动为负；TICKM 72 格 0 亮点、累计 N 账 +54 格 +0 亮点（tick_matrix/tick_matrix_report.md §8）。

**结论**：振幅在（高波宇宙池化 H 桶 108.8bp，行业 ETF 61.1bp，510300 仅 33.8bp）、执行上限 2.4bp（比 12-17bp 净门槛低一个数量级）、**缺的是信号**——分钟级问题是「振幅够但要捕获 35%+」，tick 级穿越触发连正毛移动都中位不存在（tick_t0/tick_t0_results.md §3）。

**信号侧前沿**（下一班可立卡的原料，均须新预注册卡）：
- ALGO 实现队列 top3（伪码级设计段已就绪，algo_mining/algo_mining_digest.md §6）：OFI 成交签名代理（tick 21 个月，分桶后每桶≈120 日踩功效门）；A股开盘半小时日内动量（Gao JFE 2018/Chu 2019，1min 4.7 年直接可考）；VWAP 偏离条件化做T（衔接 W3 绿区簇，k 在 IS 期预注册禁 OOS 调）。
- ALT-B 隔夜情绪：news_sent→当日日内 IC **+0.262**（t=12.2，n=92 天，90% 同号）——做T 语义可用、持仓语义不可用（5 日反转 -0.033 并存=注意力驱动结构）；功效警示 n=92 天单 regime（altdata_probes_b/altdata_b_report.md §2a）。

**栖息地名单**（etf_t0_retest/etft0_screen_report.md §3-4）：
- 588200 科创芯片/512480 半导体/512170 医疗/512010 300 医药（宇宙 A 双窗绿，T+1 底仓T 上界读数）；
- 513330 恒生互联网/513130/513180 恒生科技/159792 港股通互联网/513060 等 13 只港股簇（宇宙 B 绿区簇=**唯一真日内回转+经济学达标**，最先具备逐笔考试资格）；
- 300561 汇金科技/300469 信息发展/300757 罗博特科等 17 只高波个股簇（宇宙 C 最强，底仓T 执行模型须写死）。
- 诚实底线：绿区=清 1.43 倍安全门槛需捕获 <25%，最优仍需 14-24%，处可持续带上沿或以上——净边际正须逐笔卡出证。

## 5. 方法论发现节

### 5.1 Owner 论点（灰度选因子）证据面

- **成立**：策略层 POOLED HIGH 2.48 vs MID 0.21（regime_axis/survivor_regime_report.md §2.1）；因子层四路独立证据——趋势/技术确认类 risk_on 集体失效、risk_off 强负（factor_sop_screen/screen_report.md §3.1）；基本面族仅 risk_on 有效且反号（ROE 同比差 risk_on IR 0.81 vs risk_off -0.05，screen_report.md §3.2）；价值/小盘只活 risk_off（ep risk_off IR 0.40 vs risk_on 0.06，altdata_probe_report.md §3）；量能防守族超额集中 risk_off、15 档最优桶 risk_on=0（volume_family_l1/exam_report.md §四）。「79 严选只活 1 条的病根=考试不看行情状态」方向被证实。
- **边界（如实）**：4 条反例策略反向（高波桶通吃不是全员性质）；收益 U 形分布（MID 最弱）；「HIGH 桶增益」在 IND 切片 OOS 衰减=IS 现象（indicators_sweep_c/report.md §2.1）；板块横截面无稳定桶模式、轮动绝对收益集中 HIGH 是 beta 不是 alpha（sector_family §4）；ETF 轮动 G_HIGH 门减值=R 结论不迁移（etf_family §3）；幸存者选择与考试窗同源，POOLED HIGH 偏乐观（redblue_report.md §11.3）。定级=「存在集中性证据，待下窗复考」，不升规律。

### 5.2 图形定义审计：「引擎错不是形态死」

62 行对标=material-wrong 43（趋势上下文缺失最大族群：TA-Lib 全家源码注释自认不查趋势；双底无颈线确认 57 万事件；塔形顶底与 Bulkowski 三段完全不同；地天板方向标签 bug 一行修）/minor 13/equivalent 6（pattern_definition_audit/pattern_definition_audit_report.md §4）。规范重实现重考 12 cell：**5 翻案**（上吊线 CANON-FLIP、塔形顶方向翻转、晨星从无效变 +0.93% 真信号、流星线/Hikkake 反向是伪影）、2 形态死坐实（一阳穿多线补要件后 6/6 年仍反向、锤子线弱反向）、2 真活但语义错位（塔形底 +0.81%/双底 +1.27%）、黄昏星=方向依赖定义（结论可随定义翻转）、三只乌鸦规范 n=0 功效不足（§7）。11 条引擎修复工单移交图形库线（T1 上下文过滤/T2 塔形重写/T6 地天板一行修等，§6）。

### 5.3 红蓝/多重检验纪律实战案例

- **F 车道 v1 作废**：除权掩膜 pandas iloc 笛卡尔块赋值 bug→首版 532f9f7b98 IC 数值作废，numpy 成对花式索引修复全量重跑，v2 supersedes 入册；红蓝专项核验「修复彻底，v2 为唯一有效数值」成立（redblue_report.md §2.1；factor_sop_screen/screen_report.md §6）。
- **PATX 严格档**：P 全研 4733 检验 Bonferroni 阈值下 3 个 PASS 全部存活（p²<1/500 分辨率）+常规档 α/103 双档并报；bootstrap=锚日聚类 500 次（pattern_narrow_exam §3）。
- **R 计数勘误**：红队边界 ±0.05 重跑方向稳，但坐实两处计数错（14/17→13/17、15/17→12/17），勘误节追加原 csv 零改动；乘法位置量化 p≈0.002-0.045 维持「待下窗复考」（redblue_report.md §1.1）。
- **蓝队 frozen 一致性**：12 车道 mtime 链卡先于结果全 OK、未发现任何跑后改参（redblue_report.md §5）；TICK run1 bdpan 时间戳 UTC 错标、TICKM run2 amount 单位 1/100——均为「崩溃/判缺陷于统计前、参数零改动重跑」的先例执行（tick_t0/tick_matrix 报告 §1）。
- **假阳性量化示范**：ALGO 引 HLZ t>3.0/DSR/PBO 论证「全矩阵=噪声收割」（10³ 格期望假阳 1.3 个/轮 vs 真实功效 <30%）（algo_mining/matrix_necessity_verdict.md §2.2）；MID 车道 114 组 |t|>3.29 观测 74 vs 期望 0.11=名义 t 无区分度的实证（mid_valley_report.md §3①）。

## 6. 下一班施工队列（优先级）

1. **PATD 11 条引擎工单移交图形库线**：T1 CDL 全家趋势上下文过滤/T2 塔形三段重写/T4 Hikkake 分档/T6 地天板方向一行修为高优先；修后图形库 103 cell 重扫重考（pattern_definition_audit/pattern_definition_audit_report.md §6）。
2. **PATX PASS 卡补规范版对照**：塔形底/双底/塔形顶三卡补规范实现对照腿（规范版参数已在 canonical_patterns.py 钉死可复用），并排期复权链修复后复核（红蓝 §3 复核清单第一位）。
3. **ALGO top3 落地**：OFI 代理→开盘半小时日内动量→VWAP 条件化做T（衔接 W3 绿区簇），伪码级设计段与功效门已备（algo_mining/algo_mining_digest.md §6；algo_mining/implementation_queue.csv）。
4. **E4 收口（W2.3）**：MID 三独立卡（缺口ATR/二进三/UTAD，G1 MID 条件化窄测 Sharpe≥1.4+uplift≥1.5→G2 E4→G3 DSR N_eff≈4）+L1 CORREL/BETA risk_off 条件化池新卡；f06 import 验证 OK 但 intake 目录禁碰约束下走注册表正门（mid_valley_report.md §4.3；volume_family_l1/exam_report.md §五）。
5. **红蓝指出的修复**：计数勘误下游修订（mid_valley 两件/teaming brief/总包令引用面按 13/17、12/17 更正）；E 车道敏感档数字来源确认；L1 成本口径命名二义（25bp/换手 vs 引擎现行）给两套土规正式命名；L1「反向参考」列改名（redblue_report.md §7）。
6. **有界矩阵第一波**（按 ALGO 规格 v1 经 Owner 批准后，见 §8-6）：≤36 判定格/波，5 粒度轴（秒不设信号档）×4 数据轴×≤8 信号族，BH q=0.10+跨轮累计 N 账+功效门 120 日/桶（algo_mining/matrix_necessity_verdict.md §3）。

## 7. 数据债清单

> 销账批 W2.6 已落地（st-bizmine-co-20260919，commit 0cd61d2b2f=backtest_backlog 写回 19 条；421b9dc2e7=known_data_gaps.yaml 登记 8 条目：consensus PIT 坏/kline_etf_daily 过浅/TI 429 万重复/tick 覆盖缺口/清算流空表/weather 31 日/研报 hot_value 全空等）——**数据债的注册表正门归宿=src/zephyr/data/config/known_data_gaps.yaml（销账批②），下表为车道报告原始出处索引**。

| # | 债项 | 影响 | 出处 |
|---|---|---|---|
| 1 | **复权链 adj_factor 恒 1**（全局债） | 一切日线结论=暂定；复核清单排序：PATX③→PATX/P①②幅度→R HIGH 幅度→S8→ETFT0 C rv20→F/MID 池排名 | redblue_report.md §3 |
| 2 | TI daily 429 万重复 (date,symbol) 须 ingest_ts 去重；md_14 源含 inf；2026 值真异键 61,617（6.5%） | 指标库一切消费方 | indicators_sweep_b/screen_report.md §4；indicators_sweep_a/report.md §2 |
| 3 | consensus_daily plain 值类 PIT 坏（平推快照）；repaired 净段 2022+ 断供 | 一致预期值类因子只能用 2019-2021 | factor_sop_screen/altdata_probe_report.md §1 |
| 4 | tick_depth_5 仅 40 日（逐标的 4-8 日）；auction_book 22 天/17 全快照；2022-2024 tick 不在库；2026-06 tick 全月空窗；bdpan L1 bid/ask 100% NULL | M3/S3/S4 降级、M2 长窗缺 L1 | tick_t0/tick_t0_results.md §7；tick_matrix/tick_matrix_report.md §10 |
| 5 | bdpan 上游缺陷：timestamp UTC 错标 +08、amount 单位 1/100（车道已机械修复，属源数据债） | tick 消费方必须自归一 | tick_matrix/tick_matrix_report.md §1-2 |
| 6 | hot_value/rating_change 全空列；limit_up_down 无封单/炸板维度；weather 31 日；research_report 全文 20GB 未搬 | 热度绝对值/评级调向/天气/文本情绪信号不可构造 | altdata_probes_b/altdata_b_report.md §5 |
| 7 | money_flow 3.5 月/margin 2 月功效不足（≥1 年再探） | 资金流/两融因子挂长尾 | factor_sop_screen/altdata_probe_report.md §4 |
| 8 | S0 宏观腿：Shibor 76 行/两融 2 月/政策腿无表 | S0 传感器不可判 | sensors_b1/sensor_monotonicity_b1_exam.md §4 |
| 9 | E 盘冷归档（E:/zephyr_cold_archive：1min 2000-2021 255 月/ETF 1min 2005-2018/5-60min/无 tick）未挂回 | 有界矩阵功效最大单点杠杆；可救 kline_etf_daily 过浅 | 台账 06:0x E 盘盘点行；tick_inventory_total.md |
| 10 | 板块成分快照仅 2 天；880 板块名称映射缺失；涨停占比数据双缺口 | 板内广度/成员因子、涨停信号不可考 | sector_family/d_sector_family_report.md §1/§6 |
| 11 | kline_etf_daily 过浅（96k 行）；2 只 ETF 无名（159908J/510680J）；589090 次新 IS 仅 3 日 | ETF 日线口径弃用（E 车道改 1min 聚合）；ETFT0 缺行 | etf_family/etf_lane_report.md §1；etft0_screen_report.md §2 |
| 12 | dragon_tiger_seat 断供 2024-02 后待核；图形 32 条 intraday/盘口数据债+96 条缺检测器 | 席位因子增量；图形库 183 条未物化 | algo_mining/algo_mining_digest.md §3；pattern_backfill/pattern_backfill_inventory.md §5-6 |

## 8. 待 Owner 裁定清单（逐条带选项与建议）

| # | 事项 | 选项 | 建议 |
|---|---|---|---|
| 1 | **B-15 组队评审**：三档观察档（稳健 1.815/均衡 1.838/进攻 1.470，全带 E4 存疑 verdict） | a) 进 E8 纸面 sleeve 赛马（MOD-PA-004 相关性闸+MOD-PA-003 分配器）；b) 封存待 E4 收口后再评；另附：「按桶切换」假设是否立项 | a)+切换立项走预注册卡+2025-09..2026-09 前向窗窄测（数据在库）；弹药账口径采信闭式外推账（≈4 条 @1.4）作下阶段 KPI（regime_axis/teaming_regime_brief.md §4） |
| 2 | **塔形顶做空可交易性**：统计 PASS（2.37）但融券费率 8-10%/年+券源未建模；复权修复后幅度将缩（红蓝高敏感第一位） | a) 单独立卡建模融券成本后重判；b) 维持「统计口径」封存不做交易解读 | b) 先封存，排 a) 于复权链修复后同批（红蓝 §3 复核清单第一位） |
| 3 | **CRY 费率作废条款**：HL 公开档 perp 4.5bp/spot 7bp vs 占位 2bp，差>1bp 条款已触发 | a) T0-PRERG-02 按真实费率重判一次后封卡；b) 直接维持 RED 封卡 | a)（重判成本极低、封卡证据更硬；真实费率下 ≈3.0% 更红，crypto_probe/funding_carry_results.md §4） |
| 4 | **图形引擎工单排期归属**：11 条工单（T1/T2/T4/T6 高优）+补扫 5 条历史回填 | a) 归图形库线（PATD 移交对象）；b) 归数据线捆 JOB-108 | a) 工单归图形库线；5 条补扫历史回填归数据线 pattern_event_backfill.py 正门（JOB-108 幂等已验证） |
| 5 | **SOP v0.1 转正**：factor_mining_sop_v0_1（八段缝合册+regime 条件化条款）+G1-G10 缺口归宿 | a) 转正升 sop/（G4 并 factor_mining_sop、G3+G5+G6+G8 合并一本 exam_policy）；b) 维持工作稿再用一战 | a)，按净零原则新立册仅 exam_policy 一本候选（factor_sop_screen/strategy_sop_gap_report.md §3） |
| 6 | **有界矩阵规格批准**：ALGO 规格 v1（≤36 格/波、5 粒度轴、4 数据轴、BH q=0.10、功效门 120 日、跨轮累计 N、滚动前向） | a) 批准开第一波（top3 格先行）；b) 修规格后再批 | a)，第一波=ALGO top3+功效门自查；矩阵只产候选卡不出 PASS（algo_mining/matrix_necessity_verdict.md §3） |
| 7 | **E 盘归档挂回工单**：E:/zephyr_cold_archive 分钟线 2000-2021（255 月）挂回数据线正门 | a) 立工单排期（今晚只登记）；b) 不挂 | a)——有界矩阵与分钟级信号的最大单点历史深度杠杆（台账 06:0x 行） |
| 8 | 红蓝登记附带项：B1 方向语义冻结（S1/S0-1 valid 全依赖正向读法，冻结反向则全改判 noise）；E 敏感档来源确认；L1 成本口径命名 | 各自 a/b 见 redblue_report.md §7 | 归维护班批处理，B1 语义冻结建议随下次决策点一并定 |

---

*汇编代理：st-bizmine-op-20260919。纯合成零新计算；未纳入项与他会话在途件清单见最终交付消息。台账行已随批追加（锁忙则登记代追加）。*
