---
ttl: task_bound
---

# 业务层 Alpha 挖掘通宵战 · 战役台账（st-bizmine-20260919）

> 真源总令=bizmine_general_order.md（v2）。本台账只追加不回改；每行一个事件，带产物路径或 commit。

| 时刻 | 车道 | 事件 | 产物 / commit |
|---|---|---|---|
| 01:41 | 总包 | v1 总包令落盘（L1/L2/L3 初版） | d33b3ada93 |
| 02:0x | 总包 | v2 修订：灰度状态轴升第一主纲；做T行情条件化复活轴；因子SOP补链；另类数据入挖 | q-20260919-st-bizmine-20260919-0002 |
| 02:0x | R | 发车 st-bizmine-r：灰度×因子条件化考试（17幸存者×状态桶） | - |
| 02:0x | T | 发车 st-bizmine-t0：主观做T方法库挖矿+行情条件化窄测+币圈研究 | - |
| 02:0x | F | 发车 st-bizmine-f：因子SOP v0.1+IC大海选+另类数据探针 | - |
| 02:3x | L1 | 发车 st-bizmine-l1：量能族 14 档（同源预检+去重+预注册+沙箱考） | - |
| 02:3x | S | 发车 st-bizmine-sec：板块族首批（强度/轮动信号 IC+周频轮动快测） | - |
| 02:3x | P | 发车 st-bizmine-pat：图形库 78 条值得考事件研究 | - |
| 02:3x | E | 发车 st-bizmine-etf：ETF 波段择时+横截面轮动（Owner 愿景对齐） | - |
| 待 | 预备 | B1 三传感器批计算（BT-P1-001/005/006）、BT-P1-029/054 晋升登记（车位空出递补） | - |
| 待 | W2 | 红蓝对抗+销账（BT-P1-032/B0 15条）+起床报告 | - |
| 02:3x | R | R1 灰度现状一页纸（三套状态资产/PIT 口径/条件化选列=regime_state_anchored.vol_pct；#ARCH-344 只引用） | docs/_working/bizmine_night/regime_axis/regime_status_assessment.md @ 6fa8fd2cc7 |
| 02:3x | R | R2 预注册卡（IS 三分位 0.3200/0.7040，T-1 PIT）+17 幸存者×状态桶矩阵+报告：POOLED LOW 1.12/MID 0.21/HIGH 2.48，14/17 最优桶=HIGH，收益集中于高波灰度桶（暂定，复权链未修复） | docs/_working/bizmine_night/regime_axis/{prereg_card_survivor_regime_buckets.md,survivor_regime_matrix.csv,survivor_regime_report.md} @ 6fa8fd2cc7 |
| 02:5x | R | R3 组队备料 regime 版：三档观察档（稳健 1.815/均衡 1.838/进攻 1.470）+按桶切换示意+弹药三笔账（≈4 条 @H2 Sharpe≥1.4 或 1-2 场 80+ 候选战役；MID 洼地最缺弹药）；B-15 待 Owner | docs/_working/bizmine_night/regime_axis/teaming_regime_brief.md（本批落） |
| 02:5x | R | R4 板块灰度层 v0 设计段（只设计不实现）：880 表实测 469 板块/2022 起成熟 4.5 年；成分快照仅 2 天=历史广度缺口；strength∈[0,1] 定义+三假设方向 | docs/_working/bizmine_night/regime_axis/sector_regime_design.md（本批落） |
| 03:5x | T | T车道四件全落：主观做T方法库(12+4手法三路来源)/转换表+2预注册卡/行情条件化窄测**TERMINATE**(G1挂:uplift 1.284<1.5;H桶req_cap 0.355,净@10%捕获-5bp,304证据链第三环闭合)/币圈研究报告(funding小时级466万行,BTC年化均值14%,清算流空表,C1卡勘误) | docs/_working/bizmine_night/t0_regime/ (commit 本批) |
| 02:57 | F | F1+F2 两件全落：因子挖掘SOP v0.1缝合册(八段流程+regime条件化条款+预注册模板,转正待Owner)+挖策略SOP缺口报告(G1-G10)；IC大海选 126值得考→38可映射全量入册(114行,IS 2019-2023,前瞻5/10/20,F4_BDI T-1分桶)：top-20待考池头部=历史天量-0.94IR/地量+0.79/ATR低波-0.79/布林收口+0.65，状态反号证据=MACD零轴·均线排列·趋势斜率 risk_on失效/risk_off强负，基本面族仅risk_on有效(净利yoy IR 1.11 vs 0.13)；筛≠考,复权暂定 | docs/_working/bizmine_night/factor_sop_screen/{factor_mining_sop_v0_1.md,strategy_sop_gap_report.md,screen_results.csv,screen_report.md}(本批commit) |
| 03:5x | B1 | B1 三传感器批计算全落（BT-P1-001/005/006）：S1 指数传感器 **valid**（rho=+0.800 全 8 格，N=1/5/10/20×lag0/1，n=8428，主读法=趋势跟随；+2 档结构性不可达=规格发现）；S0-1 新闻情绪批量重算（759.5 万标题规则法、3518 交易日、持久化窗 0 落考试窗全 holdout）：h=20 **valid**/短中窗 pending（rho 0.5-0.8），情绪延续语义全格正向；S0 宏观 **整体不可判**（四腿缺三：Shibor 76 行/两融 2 月/政策无表），仅海外腿探针（纳指隔夜跌>2% n=559：1 日压制-0.04%、20 日反强+0.90%）；方向双读法并报（反向读法全 noise，冻结待决策点）；标题-only 降级口径暂定 |
| 03:5x | B1 | 交付：docs/_working/bizmine_night/sensors_b1/（考试报告 md+5 csv；批算脚本 .runtime/tmp 不提交，转正另走正门） | docs/_working/bizmine_night/sensors_b1/sensor_monotonicity_b1_exam.md 等 6 件（本批 commit） |
| 04:5x | E | E车道四件全落：510300择时预注册12规则x5变体60行(真源=kline_etf_1min聚合日线,仅1只≥250日的kline_etf_daily弃用)+全量筛查：top=RSI反转h10净Sharpe 0.796/MDD-8.6%，零候选(Sharpe>1&MDD<15%双门未过)；regime门对510300不加值(0.796→0.69)；轮动mom20_top10超额+5.1pp/年但换手48x净Sharpe 0.46，G_BDION门加值(0.58/MDD-12%)，G_HIGH门减值(R车道高波桶结论不迁移)；0候选；伪影403观测量化+gate bug修复重跑登记 | docs/_working/bizmine_night/etf_family/ (commit 本批) |
