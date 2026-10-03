---
ttl: task_bound
title: "孤儿指标因子三分法挖矿作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

# L12 孤儿技术指标 115 + 孤儿因子 126 三分法挖矿作业簿

## ① 总读数

- 事实源：`docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml`（143 条）＋`docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（175 条）＋`data/runtime/consumption_census_ledger.json`（2026-09-30 读数 473 岛：indicator 115／factor 126，孤岛名单以 census 为准）。
- 三分法判据（onboarding SOP §9A/§9B/§9C）：A=接线（公式可直接进 factor_mining S0-S7 考试）；B=挂账 defer（有潜在用途、依赖未建消费面，defer_reason+解锁条件必填）；C=候退役登记（仅有名字无式／与库内同义可派生／A 股不适配——只登记不执行，注册表净删=Owner 门位 §5）。
- 判定读数：指标 115 = A 21 + B 77 + C 17；因子 126 = A 15 + B 103 + C 8。合计 A 36 / B 180 / C 25。
- CH 实证（c1_market.technical_indicator，只读 SELECT）：总行数 369,402,056（≈3.69 亿），max(trade_date)=2026-09-30。抽 8 孤岛列全部在表且已算出（非空且非 NaN 口径）：chips_winner 6.39%、scr 6.39%、cyc_5 6.99%、ht_dcperiod 12.97%、zscore_20 9.93%、massi_25 13.79%、correl_30 13.59%、wr_14 98.65%——"算了但没人用"成立；并补上 census value_formula 自述 ch_row_count 读数缺陷的首批实读。
- 消费反查（grep src/zephyr/factor|signal_ashare|strategy_pipeline）：指标输出列 20 例全词零命中（`docs/03_modules/_domain_factor/algo_flow/chips.yaml`、`cycle.yaml` 为生产面自述，非消费）；因子发现 4 例语义消费在途：FCT-SENT-016/017→`src/zephyr/signal_ashare/futures_basis_monitor.py`（basis_rate/basis_vel）、FCT-LIQ-050 北向→`capital_behavior_orchestrator.py`/`crowd_game_simulator.py`、FCT-SENT-020/028→`market_breadth_history_store.py`（breadth_vel/acc）、FCT-SENT-010→`sentiment/sentiment_cycle.py`——census 精确 id 反查漏语义消费，建议复扫治愈 4 岛。

## ② 技术指标 9 族×三态分布（115 孤岛）

| 族 | 孤岛 | A | B | C | 代表例与裁定 |
|---|---|---|---|---|---|
| chips 筹码 | 5 | 5 | 0 | 0 | IND-CHIPS-001 获利盘 chips_winner：A 股特色筹码结构 alpha，CH 已算 6.39%→A |
| statistics 统计 | 9 | 9 | 0 | 0 | IND-STAT-006 slope_14／STAT-009 zscore_20：因子原料直进 S2 宽测→A |
| cycle 循环 | 7 | 7 | 0 | 0 | IND-CYC-005 HT_TRENDMODE：regime 状态轴用法→A |
| volatility 波动 | 11 | 0 | 11 | 0 | IND-VOL-012/013/014 Parkinson/GK/RS：期权/波动率消费面未建→defer |
| volume 量能 | 15 | 0 | 15 | 0 | IND-VOLUME-001 OBV 等：与因子册 LIQ 族同真源，须先语义去重（w5_1 必并）→defer |
| composite 复合 | 1 | 0 | 1 | 0 | IND-COMP-001 一目均衡表 5 列联动语义，单列 IC 无意义→defer |
| trend 趋势 | 33 | 0 | 18 | 15 | 自适应均线重复簇 9 条+PriceTransform 4 条+BBI/GMMA/WMA 可派生→C；ADX/CCI/SAR/VORTEX 等多面适用→B |
| momentum 动量 | 34 | 0 | 32 | 2 | WR/UOS/STOCH/AROON 多面适用→B；APO=PPO 无归一同义、LWR=WR 同真源→C |
| reversal 反转 | 0 | — | — | — | 在册 5 条全部已有消费者，非孤岛（对照读数） |

应用面矩阵（§9B 12 面，按族；工单="接线=被因子表达式消费"）：
- CHIPS→个股（吸筹/出逃状态变量）＋板块（成分股聚合）＋事件驱动（突破×集中度过滤）；大盘/做T/可转债/期货/币圈/宏观/产业链/文本=不适用（缺流通股本换手口径或无 K 线网格）；ETF 面=部分适用（宽基有换手后评）。
- STAT→个股（横截面 zscore/slope）＋大盘（指数位 zscore）＋做T（5/15min 复算）＋期货（beta/correl 对冲比）。
- CYC→大盘择时（HT_TRENDMODE regime 轴）＋板块轮动（主导周期聚类）；个股面=单票周期不稳不适用。
- B 族趋势/动量/量能同 KDJ 例：大盘/板块/个股/做T 天然多面，逐格判定留待接线批（留痕即工单）。

## ③ 因子 13 域×三态分布（126 孤岛；实际 13 域=任务书口径 11 域＋data_asset/risk_rule 散域）

| 域 | 孤岛 | A | B | C | 代表例与裁定 |
|---|---|---|---|---|---|
| liquidity 流动性 | 36 | 2 | 33 | 1 | IRCF/逆势强度比有文献（Kang 2026）＋money_flow 在库→A；tick/L2 类依赖未建面→B；LIQ-041 与 SENT-023 同义簇→C |
| momentum 动量 | 23 | 2 | 21 | 0 | GR-001/002 盈利动量→A；板块轮动/龙头跟随需板块图谱面→B |
| sentiment 情绪 | 21 | 4 | 16 | 1 | 期指基差/PCR/IV_Rank 文献方向明确→A；分钟情绪 16 条等情绪中台接线→B；SENT-014 A 股不适配→C |
| event 事件 | 16 | 0 | 14 | 2 | PEAD/隔夜传导/透支度有式→B；催化分级（域错位）/贝叶斯议程→C |
| technical 技术 | 11 | 0 | 11 | 0 | 缺口 ATR 分级有式有实证、Wyckoff 五事件→B（等接线批） |
| intraday 日内 | 7 | 0 | 7 | 0 | 分时形态依赖 1min 面＋做T 执行面→defer |
| expectations 预期 | 4 | 4 | 0 | 0 | 修正广度/分歧度=分析师预期文献强因子，code 在→A（consensus 数据面先复核） |
| quality 质量 | 2 | 2 | 0 | 0 | F-Score/信息质量代理，DS-230 可算→A |
| knowledge_only | 2 | 0 | 0 | 2 | 纯叙事知识卡（建议迁 capability_cards）→C |
| value 价值 | 1 | 1 | 0 | 0 | FCT-QUAL-002 code-anchored→A |
| volatility（crypto） | 1 | 0 | 1 | 0 | BTC 波动 regime：币圈面未建→defer |
| data_asset | 1 | 0 | 1 | 0 | LIQ-038 五档拆解：依赖 L2 面→defer |
| risk_rule | 1 | 0 | 1 | 0 | TECH-069 缩量阳线规则族：规则域非因子域，建议迁域→defer |

应用面矩阵（A 组域）：SENT-016/017→期货面（IF 主力连续）＋宏观择时；SENT-018/019→ETF/期权面＋大盘择时；EXP/GR/FQ/QUAL→个股横截面；LIQ-046/057→个股＋事件驱动（异动扫描）。

## ④ A 组挖矿候选 top15（建议首个考试轴＋数据面实查）

| # | 候选 | 首考轴（S0-S7） | 数据面实查 |
|---|---|---|---|
| 1 | FCT-SENT-016 期指基差率 | 日频基差率 20d 分位→大盘 regime 状态轴 IC（已半接线：futures_basis_monitor.py） | c1_market 期指行情主力连续 2015→今覆盖实查 |
| 2 | FCT-SENT-017 基差变化率 | basis_vel→开盘 30min 情绪脉冲 IC | 同上；分钟腿缺口期显式标注 |
| 3 | IND-CHIPS-001 chips_winner | 横截面 IC：获利盘×未来 20d 反转（状态变量） | 已算 6.39%，实查个股适用子集内覆盖率 |
| 4 | IND-CHIPS-002/004/005 scr/conc_90/conc_70 | 集中度×突破事件 IC | 同上子集复核 |
| 5 | FCT-EXP-003 修正广度 | 横截面 90d 上调占比 IC（IS 2019-2023 沿 P3 协议） | 先决：consensus 表 2022 后断供复核（P3 教训） |
| 6 | IND-STAT-006 slope_14 | 归一斜率（slope/close）横截面动量 IC | 已算，子集覆盖率复核 |
| 7 | FCT-FQ-006 Piotroski F-Score | F 分位 9 组年化价差 | DS-230 财务衍生表 12q 完整性实查 |
| 8 | FCT-GR-001/002 营收同比+盈利加速度 | SUE/PEAD 20d 漂移分组 | DS-230 rev_q_yoy/np_q_qoq 列在库，实查区间 |
| 9 | FCT-SENT-018 期权 PCR | 成交量口径 PCR 5d 均线历史分位逆向 IC | 50/300ETF 期权三表（无 OI 降级留痕）更新复核 |
| 10 | FCT-SENT-019 IV_Rank | 低波分位 selling premium 择时 IC | IV 序列 min_periods=60 守卫实查 |
| 11 | IND-CYC-005 HT_TRENDMODE | regime 状态轴：trendmode 1/0 分桶复测现有 top 因子（非直接 alpha，regime 条件化必报） | 已算 12.97%，实查连续段分布 |
| 12 | FCT-LIQ-046 IRCF | 机构-散户净流入差市值归一横截面 IC | money_flow 表主力/散户口径字段实查 |
| 13 | FCT-LIQ-057 逆势强度比 | 净流入/市值 IC＋与 IRCF 正交性 | 同上；Kang 2026 信息含量 4.85x 引用核对 |
| 14 | FCT-EXP-005 分歧度 | EPS 分歧度横截面（Diether：高分歧低收益、做空受限市场更显著→A 股适配文献方向） | consensus eps_std 字段实查 |
| 15 | IND-STAT-009 zscore_20 | 20d 标准化价偏离反转 IC | 已算 9.93%，子集复核 |

配套候选（A 组其余 18 条）：EXP-001 一致预期 EP／EXP-004 异常覆盖／FQ-005 信息质量代理／QUAL-002 code-anchored／CHIPS-003 成本均线（支撑阻力轴）；STAT-001/002/003/004/005/007/008 与 CYC-001/002/003/006/007/008 为原料直进 S2 宽测（与动量族正交性检验一并报）。

## ⑤ B/C 组完整名单（compact）

### B 组挂账（180 条=指标 77＋因子 103）

| 族 | 数 | ID 清单 | defer_reason→解锁条件 |
|---|---|---|---|
| IND-VOLATILITY | 11 | VOL-003,005,008,010~014,016~018 | 期权/波动率消费面未建（HV 已年化无消费）；regime 轴先考 CYC→期权链接通或波动率择时立项 |
| IND-VOLUME | 15 | VOLUME-001,003,005~017 | 与因子册 LIQ 36 条同真源语义重叠（w5_1 必并）→LIQ 接线批统一收编后定去留 |
| IND-COMPOSITE | 1 | COMP-001 | 一目 5 列联动信号规则未立→事件型考试立项 |
| IND-TREND | 18 | TREND-002,006~015,017,019,021,033,035~037 | 均线/趋势簇过密：先 S2 对既有 EMA/SMA 基线正交性筛，再逐条立卡→趋势因子批 |
| IND-MOMENTUM | 32 | MOM-003,007,008,010,014~027,029~042 | 摆动族与 SENT/MOM 因子域重叠→A 组建立基线后二批（KDJ 例多面留痕：大盘/板块/个股/做T） |
| FCT-LIQUIDITY | 31 | LIQ-024~035,037,039,042~045,047~056,058,061,062 | tick/L2/五档/两融面未全建；算法拆单致大单类衰减（LIQ-044 实证 7.5%→1%，作为修正算子随 IRCF 收编）→L2 立项或 money_flow 复扫；LIQ-050 北向语义消费在途，复扫治愈优先 |
| FCT-MOMENTUM | 21 | MOM-001,004,006~008,012~014,017~028＋EVENT-013＋CRYPTO-MOM-001/002 | 板块图谱＋连板面未建，与 crowd_game_simulator 语义重叠→板块轮动批；EVENT-013→事件日历批；CRYPTO→币圈交易面立项 |
| FCT-SENTIMENT | 16 | MOM-015＋SENT-006,008,010,011,013,015,020~028 | 分钟情绪中台在建（breadth_vel/情绪温度已算未接线）→情绪中台接线批；SENT-015 NLP 体系→文本面立项 |
| FCT-EVENT | 14 | LIQ-036＋EVENT-001,002,004~007,009~012,014~016 | 事件日历数据面未建（议息/交割日/IPO 可机生但无 sources 登记）→事件日历资产立项；EVENT-014 PEAD 并入 GR-001 考试轴 |
| FCT-TECHNICAL | 11 | TECH-058~060,065,073,074,078~082 | 有式有实证但无消费面；TECH-073 缺口分级可与 IND-VOL-010 TRANGE 联考→接线批 |
| FCT-INTRADAY | 7 | INTRADAY-016,018~020,022,023,026 | 1min 分时面＋做T 执行面未建→做T 立项 |
| FCT 散域 | 3 | CRYPTO-VOL-001、LIQ-038、TECH-069 | 币圈面未建／五档需 L2／TECH-069 属规则域建议迁域→对应面立项 |

### C 组候退役登记（25 条=指标 17＋因子 8；只登记不执行，净删=Owner 门位 §5）

| ID | 判据 |
|---|---|
| IND-TREND-029/030/031/032 | PriceTransform 组：OHL(C) 加权平均，可派生零信息增量 |
| IND-TREND-003/004/022/023/024/025/026/027/028 | 自适应均线重复簇（WMA/DEMA/TEMA/TRIMA/T3/MAMA/VIDYA/FRAMA/JMA 同真源可派生）：收敛唯一建议保留 KAMA/HMA/ZLEMA/SuperSmoother 代表 |
| IND-TREND-018/020 | BBI=4 均线均值、GMMA=12 条 EMA 线性组合，可派生（同真源必并） |
| IND-MOM-028 | APO=PPO 无归一版，同义 |
| IND-MOM-013 | LWR 与 WR 同真源（WR=100−LWR 变换），同义 |
| FCT-MOM-002／FCT-EVENT-008 | knowledge_only 纯叙事知识卡：无式无 inputs 不可回测；建议迁 capability_cards |
| FCT-EVENT-003 | 催化分级=信源采信规则，域错位（情报治理非因子）；建议迁规则册 |
| FCT-EVENT-017 | 事件因果图/贝叶斯网络=研究议程，不可回测不构成因子 |
| FCT-SENT-014 | Utilization/Days-to-Cover：A 股无券源利用率公开数据，不适配 |
| FCT-LIQ-059/060 | 幌骗/对敲监管阈值：监控规则域错位（风控非 alpha）；建议迁 risk_rule/监控册 |
| FCT-LIQ-041 | 与 FCT-SENT-023 guard_ratio 同义簇：收敛唯一（SENT-023 有公式） |

## ⑥ 六向台账（§9A 逐问留痕，查无也是结论）

| 问 | 结论 | 留痕 |
|---|---|---|
| Q1 能产出哪些因子 | CHIPS5+STAT9+CYC7=21 指标即候选因子原料；因子 A15 即 S1 立卡清单 | 本簿②④节 |
| Q2 哪些策略需要 | 未逐卡反查 strategy_registry（留痕=未做非查无）；SENT-016/017 距策略链最近（futures_basis_monitor 已在 signal_ashare 链上） | ⑤ defer 行 |
| Q3 哪些模块需要 | grep 反查完成：指标 20 例零命中；因子 4 例语义消费在途（basis_rate/北向/breadth_vel/情绪温度）→census 复扫治愈建议 | ①总读数 |
| Q4 哪些环节需要 | CHIPS/STAT/CYC=盘后 C 段计算已在（CH 表 fresh 至 09-30）；缺的是消费环节挂载——逐段挂钩 defer 至接线批 | ⑤ |
| Q5 哪些地图需要 | 未逐图扫 TDM/GOMAP（留痕）；algo_flow/chips.yaml+cycle.yaml 生产面域册已在 | ⑤ |
| Q6 还有哪些盲点 | ①"算完就躺"系统级实证：3.69 亿行×8 列零消费；②quantized≠接线（registry 内 used_by_factors 空者 139 条，census 实证孤岛仅 115——24 条有代码消费无因子消费，前者不是孤岛判据）；③census 精确 id 反查漏 4 例语义消费 | 本簿⑦ |

## ⑦ 自审闸三态

| 闸 | 三态 | 依据 |
|---|---|---|
| 数据面实证（S0"可得≠可用"须补质量画像） | 过 | CH 只读 8 列覆盖率＋max(date) 落盘①节 |
| 消费反查（Q3 grep 全词） | 带痕过 | 指标零命中实证；4 例语义消费反证 census 待复扫（未改台账，留痕①节） |
| 计数一致（机算不写死散文） | 过 | 115=21+77+17；126=15+103+8；241 对账 census 473 岛之 indicator/factor 两族 |
| 退役只登记不执行（净删=Owner 门位 §5） | 过 | 未删任何注册条目；C 组仅建议＋判据 |
| 只读勘察＋只写本产出 | 过 | 零既有文件改动、零 git 写、CH 仅 SELECT |
| 路径禁凭记忆 | 带痕过 | 事实源路径来自任务书并经实读核实（yaml/json 解析成功即证在位）；未引未核实新路径 |
| RULE-CAPABILITY-LOOKUP | 带痕过 | 本车道只读挖矿无业务代码施工，未触发施工前双查义务；接线批若采纳本簿工单，施工前 MUST 补 capability_lookup＋library.lookup |
