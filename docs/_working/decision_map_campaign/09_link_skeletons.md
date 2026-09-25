---
ttl: task_bound
title: 09 · 交易决策地图按环节走的骨架总表（九环节×八项——挖矿班产出）
created: 2026-09-25
sid: st-mining-20260924（决策地图战役挖矿班）
lane: decision_map_campaign
status: final（只读挖掘+本文件一个交付件；禁 commit；CREATE-GUARD 由总指挥统一登记）
doc_version: v1.0
mining_sources: 见 §0.3 挖矿源清单；挖掘执行日志见 §9
doc_type: log
---

# 09 · 按环节走的骨架总表（九环节 × 八项）

> **一句话**：把仓内已有文档（D/S/G 三册 + TDM 全节点 + battle_map 12 域 + 骨架覆盖审计 +
> 板块/情绪/做T 三线骨架稿 + 考试报告族 + 日循环蓝图族）中的"环节事实"抽干，
> 按九环节各设一节、每环节填八项（①骨架节点 ②数据通道 ③原料清单 ④状态轴
> ⑤概率表覆盖 ⑥四判据 ⑦缺口清单 ⑧下游消费方），尾部给九环节×四判据总勾表与缺口汇总表。
> 全部论断带出处；找不到证据的项目如实写"仓内未见"，禁编造节点号。

## 0. 读法说明

### 0.1 仓内切分 vs 本表九环节的映射（差异如实注）

仓内存在**四套并存的骨架切分**，本表以指挥令的九环节为主轴，逐一套映射：

| 本表环节 | TDM（config/trading_decision_map.yaml，138 节点四流） | 骨架覆盖审计五层（docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md §三） | battle_map 12 域（battle_map/battle_map_*.md） |
|---|---|---|---|
| 1 大盘状态判定 | TDM-E-L1 家族（S0-S5+AGG，yaml:266-544） | SKL1（10 节点，全仓最强层） | BM-SEL-03/07、BM-BUY-02-A-1 |
| 2 大盘情绪 | 无独立层——挂 TDM-E-L1-S3（赚钱效应）/L0-04（明日情绪预测）/TDM-E-L9-V2（状态变量快照·情绪） | 归 SKL1 输入 | BM-SEL-04/23 |
| 3 板块状态与轮动 | TDM-E-L2-01～05（yaml:545-1393） | SKL2（30 节点，零件全套没电） | BM-SEL-08/09/10 |
| 4 板块→个股传导 | TDM-E-L2-06～10 + TDM-E-L3 全家族（yaml:1073-2143） | SKL3（26 节点，只在回测里跑） | BM-SEL-22/24/25 |
| 5 个股做T | TDM-P-P2（yaml:2830-2981）+ P1 体检 | 归 SKL5（审计映射：P2→SKL5） | BM-SELL-08 |
| 6 策略考试与条件共振上岗 | TDM-E-L9-D1/D2/E1/E2（yaml:5138-5226）+ F-C3-02；**TDM 无独立"上岗"层**（state_matrix=配置矩阵非节点） | **五层骨架中无对应层**（机构对照=meta-labeling/pod，06_institutional_benchmark） | BM-BT/BM-MT 域（回测/训练） |
| 7 执行 | TDM-E-L4-01～14（yaml:2169-2567）+ X-S2 离场执行（yaml:3500-3725） | SKL5（28 节点，下半段通电上半段没人下单） | BM-EXE-01～06、BM-SELL-04 |
| 8 风控 | TDM-X-R1（yaml:3156-3297）+ F-C2 约束栈（yaml:3810-3949）+ P1-04 | SKL4 + X1 横切（audit §一.1 映射） | BM-RC-01～12、BM-POS-05 |
| 9 复盘与监控 | TDM-E-L0-02/03（yaml:178-231）+ F-C3 归因（yaml:3780-4172）+ L0 作战室 | ORG 组织者域（5 节点） | BM-REC-02/03 |

**三处切分差异必须知道**：
1. **情绪不是 TDM 的独立层**：TDM 把情绪当 L1 传感器（S3）+L0-04 预测件；"情绪=独立状态变量"
   是 2026-09-22 情绪线新定桩（emotion_index_skeleton_v0.md 头注"独立状态变量——今日场内温度计，
   与大盘明日走势判断是两个变量"）。本表环节 2 按 2026-09-22 定桩走。
2. **板块层升格在途**：22 号 spec 定义"板块=选股输入特征"，2026-09-22 Owner-Max 定桩升格独立层，
   边界冲突待追认（sector_gap_list G9）——环节 3 按"独立层"走，追认未落前属在途定桩。
3. **做T 与执行同层**：五层骨架把 P2（做T）与 L4（执行）同归 SKL5（audit §一.1）；本表按指挥令
   拆为环节 5/6/7 三个环节，骨架证据回指 SKL5。

### 0.2 状态口径用语

- "已接电/覆盖未接电/缺失"三态引自骨架覆盖审计（docs/_working/trading_vision/
  2026-09-16-skeleton-coverage-audit.md §一.4：已接电=实码+生产事件链/消费实证；
  覆盖未接电=实码在盘但无生产日循环触发面）。
- 数据面实测数字（覆盖/行数/起止日）全部直接引自 01_goal_and_architecture.md §三
  （2026-09-24 探针），本表不重测。
- 原料清单的 S 编号=ulib3b_supply_relationship_ledger.md，D 编号=ulib3b_demand_gap_ledger.md，
  板块线 G 编号=sector_gap_list_and_construction_proposal.md，情绪线 G 编号=
  emotion_line/gap_list_and_construction_proposal.md（两线 G 编号独立，引用时注明线别）。
- 本表新发现、三册未收录的缺口以 **LK-xx** 编号登记（§8 汇总表含全部 LK 项）。

### 0.3 挖矿源清单（全部只读）

1. docs/_working/decision_map_campaign/01～08 号文（本战役既有八件）
2. docs/_working/ultimate_library/ulib3b_demand_gap_ledger.md（D1-D36）
3. docs/_working/ultimate_library/ulib3b_supply_relationship_ledger.md（S1-S70）
4. docs/_working/sector_line/sector_gap_list_and_construction_proposal.md（G1-G15）
5. docs/_working/emotion_line/gap_list_and_construction_proposal.md（G1-G13+施工终态 §6）
6. docs/_working/sector_line/sector_layer_skeleton_v0.md；docs/_working/emotion_line/emotion_index_skeleton_v0.md
7. config/trading_decision_map.yaml（节点 ID 全量提取，5674 行）
8. docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/（panorama 统计+各域节点名）
9. docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md / owner-vision-system-mapping.md /
   daily-orchestrator-blueprint.md / blueprint-addendum-warroom-three-tasks.md / data-sufficiency-matrix.md
10. docs/_working/t0_matrix/T0_SCHEME_MATRIX.md；docs/_working/t0_revival/t0_conditional_prereg_card.md
11. docs/_working/sector_line/exam/prereg_exam_report_v1.md；docs/_working/emotion_line/exam_report_v1.md（经缺口单 §6 转引）
12. docs/_working/quant_methodology/（README+01-05 分册+appendix A/B/C）
13. docs/_working/daily_loop_campaign/routing_table_v1_draft.md
14. docs/01_policies_and_standards/sop/mining_sop/skeleton_mining_policy.md（挖掘规范本体）

---

## 环节 1 · 大盘状态判定（regime/六段相位）

### ①骨架节点
- **TDM-E-L1 大盘总闸**（gate，盘前，module=src/zephyr/regime/core/regime_detector.py，
  MOD-REGIME-001，"消费 RegimeSnapshot 的 7 态概率分布当谨慎度系数"，config/trading_decision_map.yaml:266-315）。
- 传感器阵列 7 件：TDM-E-L1-S1 大盘指数传感器（MOD-REGIME-016，yaml:317）/S2 市场内部结构传感器
  （yaml:342）/S3 赚钱效应传感器（yaml:366）/S4 波动率传感器（synthetic_vix，yaml:389）/
  S0 宏观环境传感器（yaml:436）/S0-1 新闻情绪语义分析（yaml:461）/S5 日级市场条件传感器（yaml:488）；
  **TDM-E-L1-AGG 市场状态判定**（yaml:511）。
- 六段相位法定真源：`zephyr.signal_ashare.core.environment_switch` 的 **SIX_STATES** +
  framework_composer.py:153 **REGIME_STATE_TO_ACTIVATION_PHASE 唯一映射位点**（r1/r2 震荡态不路由
  宁漏勿误；r10/r11 可抢占）——02_rulings_and_calibers.md §三。
- battle_map 侧：BM-SEL-03 市场状态感知、BM-SEL-07 体制转换检测（battle_map_05_stock_selection.md 节点名）；
  BM-BUY-02-A-1 市场状态预测及其四子件：a 3×3 矩阵分类（8 态）/c T+1 次日 8 态预测/d HMM 体制转换
  （battle_map_06_buy_flow.md 节点名；S29/S30 供数证据 battle_map_06_buy_flow.md:553,656）。
- 电态：SKL1=10 节点中 4 已接电/5 覆盖未接电/1 缺失（skeleton-coverage-audit §二矩阵行"L1 大盘/周期"；
  S2/S3/S0/S0-1/S5 均"模块在盘、无日循环触发面"）。

### ②数据通道
- **c1_backtest.regime_snapshot_history**：2019-04-01→2026-09-24，**3,629 日**，7 态概率
  （p_r1-r4+overlay），PIT 语义（01_goal_and_architecture.md §三行 1）。
- c1_backtest.regime_state_anchored（dominant r1~r12，A 态）——sector_layer_skeleton_v0.md §2 输入表。
- 产槽：regime 快照由 pipeline_events 挂 daily_kline SUCCESS **自动产出**（2026-09-16 接自动链；
  消费=pf_alloc 分配链+RSC-2 回测节流，skeleton-coverage-audit §三 TDM-E-L1 行电判依据）。
- 六段相位全史=t0 班物化 CSV（1,816 日/1,054 路由），**在 0033 批待落地**（01_goal §三行 3；
  落地卡点=甲位一句话，05_t0_and_strategy_library.md §一）。

### ③原料清单
- 已供给：**D1**（RegimeSnapshot 7 态概率，供表=c1_backtest.regime_snapshot_history，demand ledger §一）、
  **S29**（大盘指数收益+波动率→BM-BUY-02-A-1-a 8 态）、**S30**（大盘历史序列→HMM 体制转换）、
  **S44**（edb_data/us_index→10_regime_detector_spec 宏观/外盘传导）。
- 缺口：**D2** 部分缺口（涨停/跌停/炸板/连板梯队，连板梯队明细表待 DDL=GAP-F-13）、**D3** 缺口
  （涨停家数/炸板率/晋级率仅 family 级无 FCT-* 条目，yaml:307-311 注释同证）、**D4** 未明（期权 IV 曲面）、
  **D5** 部分缺口（宏观四组，两融已供 DS-098）、**D7** 部分缺口（8 态转移先验/相似日/Brier 三消费点未接线）、
  **D33** 部分缺口（盘中五证据列，kline_index 家数列 07-02 后断供——data-sufficiency-matrix L1 行）。

### ④本环节状态轴
- 输出量=**RegimeSnapshot 7 态概率分布+dominant+confidence_signal+risk_signal+shrinkage**
  （daily-orchestrator-blueprint.md §二 S2 读数清单）；及折算后的**六段相位**（activation phase）。
- 消费方：TDM-E-L1 总闸当日总仓位上限（yaml:273 "今天下不下单/给多少总仓位"）、sector_preference
  偏好映射第一轴（sector_layer_skeleton_v0.md §1 图）、TDM-P-P2-01 做T状态门（"矩阵仅
  accumulation/expansion 段开做T，L1-AGG 直喂"，yaml:2850）、日度编排器 S2 步、TDM-E-L0-04 情绪预测打底先验。

### ⑤概率表覆盖
- **P1-T3 可靠性表（相位转移矩阵）= 本环节专属概率表**：P(相位_t+1|相位_t) 全史+平均停留天数+
  振荡指数，"状态传概率不传点的定量基础"（04_p1_conditional_tables.md §一 T3）。
- P1-T1 主表的 X 轴=六段相位（本环节输出作条件轴），本环节自身被 T3 度量（"状态层自身的可靠性
  必须单独度量"，01_goal §一.1）。
- GPU 搜索**不覆盖**状态层本体（GPU=策略格搜索，03_gpu_campaign.md §一）；8 态转移先验/
  相似日推理为另一族概率件（L0-04 用），三消费点未接线=D7（demand ledger §一）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | ✓ | regime 快照挂 daily_kline SUCCESS 自动产出（skeleton-coverage-audit §三 E-L1 行）；01_goal §三 3,629 日至 09-24 当日 |
| 深史全 | ✓ | 2019-04-01→2026-09-24 共 3,629 日（01_goal §三） |
| 状态真值全史 | ✓ | PIT 语义全史可查（01_goal §三"状态真值全史 ✅"）；六段折算唯一位点法定（02 §三） |
| 概率表可算 | 🟡 | 数据面 09-24 已验、T1/T2/T3 目标 09-25 交付（04 号文 §四）；T3 本环节表在算未交 |

### ⑦缺口清单
D2/D3/D4/D5/D7/D33（上列）；六段分叉两处实现未对齐真源（auto_mount.py:129 R2SIX 法定 vs
daily_decision_orchestrator.py:110 REGIME_TO_SEGMENT 产线占位，修复清单 6 步=quant_methodology/
appendix_C_six_state_truth_chain.md，02 号文 §三）；宏观传感器 S0 与新闻情绪 S0-1 覆盖未接电
（audit §三）；六段全史 CSV 物化待 0033 批（01_goal §三）。

### ⑧下游消费方
TDM-E-L1 总闸（仓位上限）→ F-C1 预算带 → 编排器 S5；sector_preference 第一轴；做T状态门（P2-01）；
L0-04 明日情绪预测先验；RSC-2 回测节流；P1 三张表条件轴；D2 考试卡主判轴之一。

---

## 环节 2 · 大盘情绪（情绪成分/情绪指数）

### ①骨架节点
- **emotion_index 骨架设计稿 v0**（docs/_working/emotion_line/emotion_index_skeleton_v0.md）：
  六成分 **C1 涨停温度/C2 晋级率/C3 广度/C4 量能/C5 杠杆/C6 新闻**（§2），等权合成（§3），
  四 stage 时点 close_final/pre_open/auction/intraday_vN（§4），契约五字段（§5）。
- TDM 挂点：TDM-E-L1-S3 赚钱效应传感器（yaml:366）、TDM-E-L0-04 明日情绪盘中滚动预测
  （8 态转移先验+相似日+Brier 三零件，yaml:232-265）、TDM-E-L9-V2 状态变量快照·情绪（yaml:5069）。
- 存量同域簇：sentiment_cycle（五阶段分类器+compute_sentiment_temperature，production）、
  market_sentiment_analyzer.SentimentPhase、youzi_relay_emotion_engine.EmotionPhase、
  F23_LIMITUP_EMOTION——内收裁定 **#400**"并存分层+内核单源化"（emotion 缺口单 §6 终态表；
  骨架稿 §8.2 存量资产地图）。
- battle_map：BM-SEL-23 游资接力情绪周期、BM-SEL-04 次日 8 态走势预测（battle_map_05 节点名）。

### ②数据通道
- **c1_market.emotion_index**：builder 模块+DDL-as-code+双任务（close_final/pre_open）已接线，
  双 stage 首跑 33 行（emotion 缺口单 §6 S3 行）——**通道在产**。
- 覆盖：**仅 143 交易日（2026-02-26→09-22），成分起点不齐**（01_goal §三行 5，🔴 全史缺）；
  且"emotion_index 真值 2026-09-15 起才有"——D2 考试双轴窗 regime∩emotion 真值仅 **16 日**
  （sector_line/exam/prereg_exam_report_v1.md 卡 D2）。两处数字口径张力=143 日为表内行数
  （含降档成分行），16 日为全成分真值窗——如实并列，不下断言。
- 成分原料通道：daban_board_event（断 09-15→S1 周窗复通完成，事件表 936→1454 行，缺口单 §6）、
  kline_daily+kline_index（通）、margin_trading（滞后 1-2 日）、news_sentiment_window（rule 法单窗）。

### ③原料清单
- 已供给：**S10**-**S21**（情绪线台账全组：kline_daily/margin/dragon_tiger/block_trade/news/stk_limit/
  limit_up_down/auction 双表/research_report/daban 双表，supply ledger §二情绪线）、**S15**（news_sentiment_window→C6）、
  **S18**（limit_up_down→断供期涨停家数替代，C1 权重 0.4 子项）。
- 缺口：情绪线 **G5** 两融史浅（约 40 观测<120 门槛，C5 INSUFFICIENT）、**G6** 新闻全 rule 法单窗、
  **G8** PCR 未建（v0.2 挂载位）、**G12** 竞价原料通未挂载（v0.2）、**G13** 研报评级候选；
  需求侧 **D6** 未明（情绪六段分布周级灰度供给件）、**D28** 缺口（D2 卡双轴 W_map≥120 日，
  INSUFFICIENT 预登记）。

### ④本环节状态轴
- 输出量=**emotion_index ∈[0,1] 灰度分位**（"今日场内温度计"，与大盘明日走势判断是两个变量，
  emotion_index_skeleton_v0.md 头注）+components 六成分明细（逐成分 status）+version。
- 消费方：sector_preference 第二轴（现状 D 态 mock，sector_layer_skeleton_v0.md §2）、
  排班/仓位节流（骨架稿 §8.3 差异化定位）、sentiment_cycle 策略条件化（离散五阶段，§8.3）、
  D2 板块地图考试卡第二轴、L0-04 情绪预测（8 态族，另一轴）。

### ⑤概率表覆盖
- **无情绪专属概率表**。最接近件=TDM-E-L0-04 的 8 态转移先验（next_day_8state_forecast）+
  Brier 校准闭环——三消费点未接线=D7（demand ledger §一；audit §三 L0-04 行"覆盖未接电"）。
- P1 三张表不含情绪轴（04_p1_conditional_tables.md §一：T1 维度=板块×六段相位）；
  情绪轴入概率表的前提=D28 重考窗（真值≥120 日，约 2027-03 自动满足，prereg_exam_report_v1 卡 D2）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | 🟡 | 表+双任务在产（缺口单 §6），但 C1/C2 依赖 daban 复通后实际产出、C5 降档（骨架稿 §6 v0.1.0） |
| 深史全 | ✗ | 仅 143 交易日、成分起点不齐（01_goal §三 🔴）；两融需新建外部 API 通道补史（02 号文 §七） |
| 状态真值全史 | ✗ | 全成分真值窗仅 16 日（prereg_exam_report_v1 卡 D2）；补史=GPU 后第一批（02 号文 §七） |
| 概率表可算 | ✗ | D28 主判 INSUFFICIENT 预登记兑现；情绪轴无概率表（本节⑤） |

### ⑦缺口清单
情绪线 G5/G6/G8/G12/G13；D6/D28；**LK-01**（本表新登）情绪成分 IC 加权二期限定于考试通过后
（骨架稿 §3），当前等权+降档为最终口径；**LK-02** 内收裁定 #400 的"两枚举收敛"移交治理班
未落（缺口单 §6 G9/G10 行）。

### ⑧下游消费方
sector_preference 第二轴（板块线）；sentiment_cycle/策略条件化；编排器与排班（仓位节流）；
L0-04 明日情绪预测；D2 考试卡；板块线 D 态集成夜换真值约定（sector 骨架 §8.5）。

---

## 环节 3 · 板块状态与轮动（sector_state/资金流/轮动序列）

### ①骨架节点
- **板块层骨架设计稿 v0**（docs/_working/sector_line/sector_layer_skeleton_v0.md §3）：
  五成分 **momentum_pct（q3/q5/q20 加权动量分位）/rrg_quadrant（DualEma 10/26 四象限）/
  strength（涨停比 40%+梯队 30%+趋势 30%）/net_inflow_pct/rotation_state（市场级 5 状态）**，
  另 sector_preference 大盘×情绪→板块偏好表（§4：情绪三档×大盘三档→5 档偏好标签+tilt+banned_quadrant）。
  算法真源=22_sector_rotation_spec.md v1.9.8（骨架稿头注"公式级真源，本稿只做集成编排"）。
- TDM：TDM-E-L2-01 板块强度综合（+5 子件，yaml:572-1251）/L2-02 轮动序列追踪（RRG+单板块预警）/
  L2-03 调整周期进度/L2-04 板块级市场状态（五分类+虹吸）/L2-05 水温响应（档推导+响应三件套）。
- battle_map：BM-SEL-08 板块轮动序列追踪、BM-SEL-09 调整周期追踪、BM-SEL-10 行情生命周期阶段
  （battle_map_05 节点名；S23/S24 供数证据 battle_map_05_stock_selection.md:825,863,900）。
- 电态：SKL2=30 节点中 **1 已接电/28 覆盖未接电**（audit §二矩阵行 L2——"零件全套、没电"）。

### ②数据通道
- c1_market.**kline_sector_880**：2020-03-17→今 45.7 万行、469 码、1,584 交易日，近 3 日在产满量
  （01_goal §三行 2；sector 骨架 §2；S8 供给实证 sector_internal_inventory.md:185-190）。
- c1_market.**sector_state**：**985 日回放 425,787 行 ✅**（01_goal §三行 4）——回放已有、
  close_final/pre_open 两 stage 上线走施工批 2（sector 缺口单 §2 批次切分）。
- 辅通道：sector_snapshot（实时截面，A 态）、sector_constituent（SCD-2，595 板块→6,179 股）、
  money_flow（A）、sector_fund_flow（C 态仅 6 天史，G7 改判"在产+短史"）、
  limit_up_pool/daban_board_event（断 09-15=G3，与情绪班共用修复）（sector 骨架 §2 输入清单）。

### ③原料清单
- 已供给：**S8**（kline_sector_880/kline_sector/sector_snapshot/sector_fund_flow 板块层主供）、
  **D8**（板块日 K 深史）、**D9**（实时截面）、**D10**（成分股映射 SCD-2）、
  **D17**（拥挤度+景气+资金三标尺原料在库：S7 stock_daily_basic 7.1M/S5 analyst_forecast/
  S1 dragon_tiger_seat 618k 4.5 年——G14 待接线）、**S66**（sector_state+sector_preference→
  daily_gate_snapshot._collect_l2，L2 门三原料供料实证 batch2_consumer_wiring_patch.md:22-47）、
  **S67**（板块信号→pf_alloc/batched_position_builder+boundary_revision_engine+
  sector_rotation_score_mapping）。
- 缺口：**D11** 部分缺口（涨停原料 daban 断 09-15=G3）、**D12** 缺口（行业净流入分位，
  sector_fund_flow 仅 6 天=G7）、**D15** 缺口（L2 门三原料，gate 恒 not_evaluated——S66 已补料但
  接线在途）、**D16** 缺口（三级门槛阈值全 proposed=G8）、**D18** 缺口（板块坐标系裁定 G5/
  概念成分时戳快照 G12）。

### ④本环节状态轴
- 输出量=**sector_state 每板块每日五行**（momentum_pct/rrg_quadrant/strength/net_inflow_pct/
  rotation_state，观察列 capital_score/watch_score）+ **sector_preference**（preference_label 5 档+
  tilt 0.8~1.2+banned_quadrant）（sector 骨架 §3/§4/§5 DDL 草案）。
- 消费方：L2 板块门三原料 top/retained_sectors/score（G4 会合点，缺口单 §1 P0）、
  G05/sector_rotation_score_mapping 选股链（S67）、ETF 载体执行组（G13）、编排器 S3 门快照
  （daily-orchestrator-blueprint §二 S3"L2 放行档"）、P1-T1 主表被条件轴。

### ⑤概率表覆盖
- **P1-T1 主表 P(板块收益|大盘相位) 就是本环节的概率表**（板块×六段相位，四元组行
  raw/n/Wilson LB/区间宽，MIN_OBS=30 地板）；**P1-T2 辅表=板块相对排名条件表**（top quintile
  持续性/换手率，"用途=BM-SEL-08 板块轮动序列、22_sector_rotation_spec 的查询原料"）
  （04_p1_conditional_tables.md §一 T1/T2）。
- GPU 输入包含板块条件轴（grid_gpu_sectorcond 四通道，04 号文 §三.5 一致性抽查项）；
  数据面 09-24 已验，交付目标 09-25（04 §四）。
- **有效性证据缺口**：S10 考试卡判 **NO_EDGE**（q20 动量分位对 T+1 收益区分力不成立，
  W_full Q5−Q1=−0.2717%、分年符号一致率 0.20）——"按 momentum_pct 排 Top-N 当强势板块"
  的消费口径未获考试支持（prereg_exam_report_v1.md 卡 S10）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | ✓ | kline_sector_880 近 3 日在产满量（S8）；sector_state 回放 985 日在库（01_goal §三） |
| 深史全 | 🟡 | 日 K 六年深史 ✅；例外：kline_sector_intraday 断供 7 天（G2）、sector_fund_flow 仅 6 天（G7）、daban 断供（G3，已复通） |
| 状态真值全史 | 🟡 | sector_state 回放 985 日<880 全史 1,584 日；preference 情绪轴开发期 mock（骨架 §8.5） |
| 概率表可算 | 🟡 | P1-T1/T2 数据面已验、09-25 交付中（04 §四）；T2 即轮动查询原料；S10 动量标尺有效性 NO_EDGE |

### ⑦缺口清单
G2/G3（断供，G3 已复通）、G4（L2 门供料接线）、G5（板块坐标系裁定，469/596/90/499 四口径未辨析）、
G7（资金流深史双轨选项）、G8（阈值全 proposed）、G9（升格边界追认，唯一硬呈报项）、G12（概念轴前视
硬 gate）、G14（三标尺升维）；D11/D12/D15/D16/D18；**LK-03**（本表新登）S10 NO_EDGE 后动量成分
权重修订须走下轮预注册新卡（prereg_exam_report_v1 卡 S10 预承诺 S10-6.2），当前"状态轴有效成分集"
未定。

### ⑧下游消费方
L2 门/G05 选股链；sector_rotation_score_mapping；ETF 组执行（G13，待 S10/D2 出档后议——缺口单 §1 P2）；
编排器门快照；P1 表；D2/S10 考试卡；daily_gate_snapshot（S66）。

---

## 环节 4 · 板块→个股传导（选股/成分映射/因子）

### ①骨架节点
- 传导段：**TDM-E-L2-06 板块个股传导**（"只传板块强度调节分+龙头定位两字段，个股层不得直接引用
  板块买卖结论——层级隔离防越权"，强度调节分乘数封闭 10→+15%/6→+5%/<6→−10%，yaml:1073-1100）、
  L2-06-1 三级放行门槛（①板块强度>6②个股强度>5③日成交>2 亿，yaml:1101-1129）、L2-06-2 龙头识别、
  L2-06-3 强度加权传导、L2-07 回踩质量分级、L2-09 催化剂识别、L2-10 同源补涨比价。
- 个股段：TDM-E-L3 全家族 15 节点——L3-01 Universe 构建与剔除/L3-02 九阶段选票主链/L3-03 双池评分
  （短线池/波段池 5 分制+合流体检）/L3-04 负面否决器（一票否决七清单，yaml:1595-1631）/
  L3-05 顺位排序/L3-06 环境开关/L3-07 策略专属链（打板/多因子/其余 sleeve）/
  L3-08 候选池输出/L3-09 股票池分层维护/L3-10 可交易性预检/L3-11 日内动态选股（竞价+涨速）/
  L3-12 个股多维验证（资金面/龙虎榜/筹码/形态）（节点名全表见 config/trading_decision_map.yaml:1394-2143）。
- battle_map：BM-SEL-22 短线选股评分卡、BM-SEL-24 量化短线强度评级、BM-SEL-25 双引擎融合决策、
  BM-SEL-05 主力行为感知、BM-SEL-16 分级指标过滤、BM-SEL-23-B 情绪周期定位、BM-SEL-24-A-4 资金维度
  （battle_map_05 节点名；S22/S25/S26/S27/S28 供数证据 battle_map_05_stock_selection.md:714,1408,3094,2434,3259）。
- 电态：SKL3=26 节点 **0 已接电/25 覆盖未接电/1 缺失**（audit §二矩阵行 L3——"链条活着，但只在
  回测里跑，生产日循环无挂点"）。

### ②数据通道
- 成分映射：c1_market.sector_constituent（SCD-2，595 板块→6,179 股，**D10 已供给**，stockq：骨架 §2）。
- 原料表：dragon_tiger_seat 4.5 年 618k 行（**D20 已供给**）、stock_daily_basic 7.1M、daily_valuation、
  money_flow 五层净流入、limit_up_pool、auction_snapshot/auction_book——均在产（S1/S4/S7/S26/
  emotion 缺口单 §8.1）。
- 决策链产槽：**无生产日循环挂点**——L3 主链消费面=回测整装（audit §三 L3 行族"tasks.yaml 仅数据
  任务，无决策日循环触发面"；owner-vision-system-mapping §三"L3 个股/策略：建成，队员未毕业"）。

### ③原料清单
- 已供给：D10/D20、S22（龙虎榜/资金流/大宗→BM-SEL-05）、S25（涨跌停/停牌/ST→BM-SEL-16）、
  S26（竞价涨幅/量比→BM-SEL-23-A-5 竞价强度因子）、S27（连板断层→BM-SEL-23-B）、
  S28（主力净流入+大单占比→BM-SEL-24-A-4）、S52/S54（概念分类→22/26 号 spec）。
- 缺口：**D19** 部分缺口（Universe 剔除字段组，limit_up_down 历史仅 2026-08-03 起）、
  **D21** 缺口（流通股本数据工程，裁定 #257④ 挂起——获利盘/单峰密集度）、
  **D22** 缺口（池成员持久化载体，M-41 待登记）。

### ④本环节状态轴
- 输出量=**候选池输出+个股强度分+板块传导调节分**（L2-06 两字段封闭乘数）+双池 5 分制评分+
  顺位排序表。**注意：该状态轴无全史物化表**——池成员持久化载体缺口=D22/M-41（demand ledger §三），
  本表判"仓内未见个股层状态轴真值全史"。
- 消费方：TDM-E-L4 买卖执行链、TDM-P-P2-02 做T调度标的、TDM-P-P1 持仓体检、battle_map
  BM-BUY-03 决策编排。

### ⑤概率表覆盖
- **个股层无条件概率表**（仓内未见立项）。GPU 搜索覆盖策略层"什么条件下什么策略赚钱"
  （03 号文 §一），不覆盖"板块→个股传导收益分布"；P1-T2 板块排名持续性是选股的间接原料
  （04 §一 T2）。S10 NO_EDGE 直接削弱"强势板块名单"喂个股层的输入有效性（prereg_exam_report_v1 卡 S10）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | 🟡 | 原料表全在产；但 L3 决策链生产日循环无挂点、可交易预检调用方为零（audit §三） |
| 深史全 | 🟡 | 龙虎榜 4.5 年/日线深史在；limit_up_down 仅 2026-08-03 起（D19） |
| 状态真值全史 | ✗ | 候选池/评分/传导分无全史物化载体（D22=M-41；本表④） |
| 概率表可算 | ✗ | 个股层条件概率表仓内未立项（本表⑤） |

### ⑦缺口清单
D19/D21/D22；**LK-04**（本表新登）L3 生产挂点缺失=五层骨架中"只在回测里跑"层的通电工程
（audit §二 L3 行）；**LK-05** 个股层状态轴物化与概率表空白（本表④⑤）；板块线 G6（能力反查面
板块资产零在编，16 模块名单移交图书馆班）。

### ⑧下游消费方
TDM-E-L4 买卖执行；P2-02 做T调度；P1 持仓体检；BM-BUY-03 决策编排；整装回测（S11 框架，
owner-vision-system-mapping §三"整装/模拟盘：框架在，未跑真队员"）。

---

## 环节 5 · 个股做T（日内/条件化矩阵）

### ①骨架节点
- TDM：**TDM-P-P2 做T与加减仓**四件——P2-01 做T资格与成本前置（三道门：状态门/振幅门/成本门；
  D58 五道门枚举+D111 绝对金额制成本门+时段准入矩阵+量能闸门+T量盘口匹配，yaml:2830-2866）、
  P2-02 做T策略调度（三策略并发：intraday-surge-fall/orderbook-imbalance/vwap-reversion，
  单次≤底仓 30%，身份=proposed 假说，yaml:2867-2907）、P2-03 做T闭环与成功判定
  （14:50 未闭环无条件平；成功=股数不变+总成本降；喂 C3 归因，yaml:2908-2944）、
  P2-04 减仓与再平衡；上游 TDM-P-P1 持仓体检六件（yaml:2568-2829）。
- battle_map：BM-SELL-08 做T日内套利（battle_map_07_sell_flow.md 节点名；S32 分时因子供数证据
  battle_map_07_sell_flow.md:487）。
- 条件化矩阵两件本体：**T0-CONDITIONAL 预注册假设卡**（frozen，状态选择性做T：宏观门
  vol_pct(T-1)>0.700 或 dominant∈{r3,r12}；情绪门∈{ignition,expansion,euphoria}；双门 AND，
  t0_revival/t0_conditional_prereg_card.md §2）+ **T0-SCHEME-MATRIX 34 法三态矩阵**
  （7 可考/13 待料/8 阻断/6 执行层，t0_matrix/T0_SCHEME_MATRIX.md §一）。

### ②数据通道
- **kline_1min：14.83 亿行 / 2021-09→2026-09 / 5,853 只**（裁定 #413④ 立法：信号/考试=分钟，
  01_goal §三行 6、02 号文 §一.4）——材料线开闸 Owner 已批"肯定要用"（05 号文 §一）。
- **tick_data：89.5 亿行 / 2025-01→2026-09 全市场（L1 3s）**；l2_tick 0 行禁用；tick 独立信号判死
  （62bp 成本绞肉机实证）（01_goal §三行 7、05 号文 §一）。
- 六段相位全史 CSV（1,816 日/1,054 路由）=条件化矩阵的 X 轴材料，0033 批待落地（01_goal §三行 3）。

### ③原料清单
- 已供给：**D23**（大盘段位直喂+20 日振幅+成本模型，供表 DS-150+CST-T0-001）、
  34 法数据门实测（kline_1min 1,227 日 ✅、六段相位 ✅、vol_pct ✅——T0_SCHEME_MATRIX §二逐法）。
- 缺口：**D24** 部分缺口（封单 tick 买一档量代理，MFE/MAE 台账字段欠账）、
  **D26** 部分缺口（kline_etf_60min 缺约 9.0 万 bar，四段结构缺口，etf_1min 合成可救 ~95%——
  data-sufficiency-matrix §S-OWNER-001）、**D36** 缺口（tick_depth_5 五档深度差约 17 交易日
  walkforward）、**LK-06**（本表新登）转债分钟 bar 缺失——"真 T+0 品种一个都没进可考：
  本仓没有转债分钟 bar，转债逐笔在 tick_data（163 只）需先分钟重采样=最优先施工指向"
  （T0_SCHEME_MATRIX §一读法+§四）。

### ④本环节状态轴
- 输出量=**做T资格三态**（状态门×振幅门×成本门过/不过）+ **做T闭环成功判定**
  （成功/失败/损耗统计，喂 C3 归因——"做T是降成本工具不是独立盈利来源"，yaml P2-03）。
- 消费方：TDM-F-C3 绩效归因（做T贡献拆账 D50：交易盈亏/持仓盈亏二分+底仓/做T/加仓腿分离，
  yaml:3798-3803 注释）、TDM-P-P1-05 组合级体检、P2-04 减仓再平衡。

### ⑤概率表覆盖
- **T0-CONDITIONAL E4 考试=条件化概率表的做T版**（状态门命中 vs 非命中净价差比较）——
  已考 verdict=`STATE_GATE_NEVER_TRIGGERED`：材料只有 **26 对同体往返<30 门槛**且与宏观门互斥
  （T0_SCHEME_MATRIX §二 F4.4 行；05 号文"核心卡点=做T考试样本 26 对<30"）。
- 34 法矩阵=可考性概率表前身（每法三态+样本量缺口登记）；六段相位×做T方法=条件化矩阵骨架，
  GPU 搜索**不含做T**（grid=策略格，03 §一；"GPU 输入包全毕"指做T方法矿，05 §一）。
- 解锁路径：kline_1min 材料线开闸→考试样本量达标（05 §一"现状与解锁"）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | ✓ | kline_1min/tick 在库且在产（01_goal §三）；材料线开闸已批（05 §一） |
| 深史全 | ✓ | 分钟 5 年/tick 21 个月（裁定 #413④）；例外=D26 小时线缺口、D36 五档差 17 日 |
| 状态真值全史 | 🟡 | 六段全史 1,816 日已物化但 0033 批待落地（甲位卡点）；regime_state_anchored 在库可替代轴源 |
| 概率表可算 | 🟡 | E4 卡 frozen、判据齐（前置命中率≥0.30 等，卡 §3）；卡在样本 26<30，材料线开闸后即可重考 |

### ⑦缺口清单
样本 26<30（材料线解锁在途）；甲位一句话（auto_mount.py 写回准否，07 号文 §C 门位表）；
D24/D26/D36；LK-06 转债分钟重采样；**LK-07**（本表新登）三策略（surge-fall/orderbook-imbalance/
vwap-reversion）confidence=proposed、回测验证通过前不生效（yaml P2-02 注释 D111），做T策略层
至今无一条 verified。

### ⑧下游消费方
C3 归因（做T贡献拆账）；P1-05 组合体检；执行层（tick 盘口失衡=执行增强 v2，05 §一）；
X-S1-02 止损族（做T价差+时间止损挂 P2-02，yaml X-R1 注释 m-11）。

---

## 环节 6 · 策略考试与条件共振上岗（GPU 成绩单→选策略规则）

### ①骨架节点
- TDM：TDM-E-L9-D1 决策假设·因子组合挖掘/D2 登记与考试方案/E1 验证·一问一考考试链/
  E2 结论回传与修正（yaml:5138-5226）；TDM-F-C3-02 升降级管线与退役评审（yaml:3950-3988）；
  **state_matrix 配置矩阵**（策略×状态挂载格，TDM-E-L1 strategy_mounts 实例：capitulation→
  [STR-VREV-025/027]、accumulation→[STR-VREV-026/027]、expansion→[STR-MOMTREND-033]，
  yaml:296-307；ignition/euphoria/distribution=空格 pending-owner-adoption——routing_table_v1_draft.md §2）。
- **TDM 无独立"上岗规则"层**（本表 §0.1 差异 3）：条件共振上岗规则 v1 未立——切换摩擦三零件
  （滞回带/最短任职期 20 日/冷却 60 日）为新提案待采纳（06_methodology_index.md 冷水⑤行）。
- 考试制资产族（骨架=卡族+引擎+台账）：预注册卡（search_space_prereg.yaml、sector S10/D2 卡
  frozen、emotion 卡 A/B、T0-CONDITIONAL、etft0 母本）；C4 考试引擎+DSR+OOS+台账
  （"考试咽喉（C4 引擎+DSR+OOS+年衰减率）✅ 已建实战"，2026-09-13-strategy-factory-pipeline-discussion.md
  结案摘录 L58）；GPU 网格执行器 factory_grid_executor（03 §一）；e7_defense（DSR 浮动门槛，
  N_eff 口径裁定 #306，03 §二.6）。
- battle_map：BM-BT 域（回测验证 6 文件头）、BM-MT-01 训练流水线（design 态）——
  battle_map/index.md 与 panorama（MT-01 design 态，panorama mermaid 块）。

### ②数据通道
- config/strategy_registry.yaml（REG-STR-001）：**161=19 active+139 candidate+3 deprecated**；
  factor_registry 175 条（02 号文 §四）。
- GPU 战役通道：data/strategy_intake/grid_20260924-213246/（T1 3,700 格跑批中→T2 900 格自动晋级，
  闭卷窗 2019-01-04→2025-09-09；03 §一表）。
- 退役三账本：聚宽漏斗 c4_deferrals.csv（322 行机读）/潘潘并入宿主 159 条/git 全量重建；
  strategy_archive/ 机制已建零触发（05 §二；appendix_A）。
- 模拟盘四件+成绩台账：sim_trade_log/sim_pocket_daily/sim_platform_journal/strategy_screen（S37）。

### ③原料清单
- 已供给：**S35**（miniQMT tick+CH 日线→BM-BT-02-B 回测多源）、**S37**（模拟盘四件）、
  退役三账本（appendix_A "三账本均可重考"）、GPU 成绩单口径（cost_adjusted_sharpe 主目标+
  毛夏普仅观察+DSR 门槛，03 §二.6）。
- 缺口：**D30** 缺口（state_matrix 六空格 pending-owner-adoption——Owner 资金分配门位未填，
  yaml:4461-4475 时点注）、**D31** 缺口（预算带/过渡带数值 proposed→confirmed 待 Owner 批）、
  **LK-08**（本表新登）PBO+CPCV 未接入考试验收链（06_methodology 冷水①"补=PBO+CPCV 进下轮
  考试制"；B2 排期"本轮成绩单出来即用"）、**LK-09** 退役重考未开（排 GPU 第一轮条件骨架后=下周，
  05 §二排期）。

### ④本环节状态轴
- 输出量=**每策略"什么条件下胜率/期望最高"成绩单**（GPU 格级 cost_adjusted_sharpe+DSR 判档）+
  **策略×状态挂载格 verified 状态**（state_matrix 格，C3-02 评审升级——yaml F-C3"矩阵格 verified
  升级=系统自我进化闭环"）。
- 消费方：条件共振上岗（"当日实际天气与成绩单条件对上=条件共振→对路策略上岗；多策略并发"，
  01_goal §一.5）；编排器 S4 策略包选择（daily-orchestrator-blueprint §二 S4）；C3-03 sleeve 调权；
  退役评审 C3-02。

### ⑤概率表覆盖
- **GPU 成绩单=条件化概率表的策略层版本**（在册策略×条件格×五档成本门）；P1 三张表=资产层
  （T1 板块/T2 排名/T3 转移）。两层互补："GPU 成绩单+P1 概率表=条件共振选策略的原料"
  （05 §二 长期愿景）。
- 上岗层概率表：**尚未立法**——静态查表 v1（滞回带提案）→contextual bandit v2（07 号文 §B2
  排期"静态表+上岗规则 v1 验证一个交易日循环后"）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | ✓ | GPU T1 跑批中（grid_20260924-213246，21:32 发车）；C4 引擎已建实战（03 §一；factory 结案 L58） |
| 深史全 | ✓ | 闭卷窗 2019-01-04→2025-09-09 全档成本门真跑（03 §一命令行） |
| 状态真值全史 | ✓ | 条件轴=regime PIT 3,629 日（本表环节 1⑥）；六段折算唯一位点（02 §三） |
| 概率表可算 | 🟡 | 成绩单预计周六出（03 §一）；上岗规则 v1 未立（LK-10）、D30 六空格未填 |

### ⑦缺口清单
D30/D31；LK-08（PBO/CPCV）；LK-09（退役重考未开）；**LK-10**（本表新登）条件共振上岗规则 v1
未立法（滞回带+任职期=提案，06 冷水⑤；routing_table_v1_draft §3 落地三步全部待 Owner 批）；
**LK-11** T1 轻档成本路径代码缺失（方案①升级案=代码新建+考规修订双活，03 §三清单 1-2）。

### ⑧下游消费方
编排器 S4（PackageDecision）；多策略并发 pod（01_goal §一.5"单判错不致命"）；C3 归因调权与退役
评审；模拟盘试用通道（重考纪律 3：机制门槛+试用期，05 §二）。

---

## 环节 7 · 执行（下单/滑点/盘口）

### ①骨架节点
- TDM-E-L4 买卖点与执行 14 件：L4-01 分批建仓/L4-02 买入时序/L4-03 价格锚定/L4-04 资金分配多标的/
  L4-05 打板执行专项/L4-06 执行算法/L4-07 条件触发队列/L4-08 突破失败降级/L4-09 执行硬约束/
  L4-10 订单生命周期状态机/L4-11 部分成交与撤改处理/L4-12 订单级预检/L4-13 执行容灾对账/
  **L4-14 执行成本反馈与选型回写**（节点名全表 yaml:2169-2567）。
- 离场执行：TDM-X-S2 六件（执行方式路由/T+1 与涨跌停约束/执行时段路由/本地条件单管理/
  分批止盈执行/卖出闭环与退出效率，yaml:3500-3725）。
- battle_map：BM-EXE-01 自适应风控审批/02 交易执行/03 执行质量 TCA/04 Pre-Trade 合规检查/
  05 智能订单路由与拆单/06 成交回报处理与持仓更新（battle_map_10_execution.md 节点名）；
  BM-SELL-04 止盈止损族（A 止盈/B 止损/C 策略止损/D 猎杀防护/E 分批退出，battle_map_07 节点名）。
- 电态：SKL5=28 节点 **0 已接电/27 覆盖未接电/1 缺失**——"下半段通电（委托管线/价格笼子/订单预检/
  熔断减抄全是 production 件且路径通）、上半段没人下单（无日循环产生委托，策略模板缺 BT-P2-055）"
  （audit §二 L5 行+§大白话摘要）。

### ②数据通道
- **QMT 桥**：100 股端到端实测过（data-sufficiency-matrix §五层矩阵 L5 行；qmt bridge 迁移台账
  docs/_working/2026-09-08-qmt-bridge-migration-ledger.md 在案）。
- **tick L1 3s**：执行优化与盘口信号法定通道（裁定 #413④，89.5 亿行）；**tick_depth_5** 五档深度
  1,883 万行、日增 1,220 万，距全市场 20 日 walkforward 差约 17 交易日（D36；data-sufficiency L5 行）。
- 成本模型注册表：CST-T0-001（做T 31.2bp 固定口径）/CST-ASTOCK-001（真实费率核算）
  （t0 卡 §3；yaml P2-01 注释）。

### ③原料清单
- 已供给：**S31**（压力位→BM-SELL-01 突破成败）、**S32**（分时因子量比/CVD/VPIN→BM-SELL-08）、
  **S68**（实时 tick→BM-SIM-08 封板队列撮合）、S36（成交量+持仓→BM-RC-04-E 流动性监控）。
- 缺口：**D34** 缺口（L4-14 执行成本反馈闭环——"三零件在、选择器不消费=断链实证"，
  TDM:2529-2540）、**D36**（上列）、**LK-12**（本表新登）逐笔 TCA 滑点归因欠账（D50③：
  "decision price→fill price 滑点归因，A 股隐性成本可达佣金 5-10 倍"，yaml:3802-3803 注释）。

### ④本环节状态轴
- 输出量=**订单生命周期状态**（L4-10 状态机）+ **执行质量 TCA**（滑点/成交质量，BM-EXE-03）+
  委托与回转单（L5 判定物："委托与回转单（滑点最小化）"，owner-vision-system-mapping §一 L5 行）。
- 消费方：L4-14 选型回写（断链=D34）；C3-01 多维归因（逐笔 TCA）；TDM-P-P1-01 持仓对账；
  BM-REC-02-A TCA 执行质量分析。

### ⑤概率表覆盖
- **执行层无概率表**（如实：执行语义=成本最小化非概率推断）。最接近件=盘口失衡执行信号
  （tick 盘口失衡=做T执行增强 v2，排 GPU 后——07 号文 §B2 末行）；tick 独立信号已判死
  （62bp 实证，appendix_B）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | 🟡 | QMT 桥实测通、委托管线 production；但无日循环产生委托——BT-P2-055 模板缺（audit §摘要 L5） |
| 深史全 | 🟡 | tick 21 个月在库；tick_depth_5 差 17 交易日（D36）；板块分钟K真值源未定（synth 合成顶着，02 §七） |
| 状态真值全史 | ✗ | 执行质量/滑点全史台账未见——L4-14 断链实证（D34）、逐笔 TCA 欠账（LK-12） |
| 概率表可算 | ✗ | 执行层无概率表（本表⑤，如实注：非本层语义） |

### ⑦缺口清单
D34/D36；BT-P2-055 底仓+日内回转执行模板（owner-vision-system-mapping §五挂单）；
LK-12（逐笔 TCA）；盘口失衡执行信号 v2（排 GPU 后）；M-55 人工干预入口（paper 升档前增设，
yaml X-R1 注释 D117——与环节 8 共享）。

### ⑧下游消费方
成交回报→持仓更新（BM-EXE-06）；C3-01 归因；P1-01 持仓对账；BM-REC-01 结算对账（design 态）；
X-S2 卖出闭环。

---

## 环节 8 · 风控（组合/回撤/熔断）

### ①骨架节点
- TDM：**TDM-X-R1 应急保命**（kill_switch 常驻任何档位不可移除；组合回撤 25% 或单日 −6%→无条件
  全清仓+冻结开仓通道，仅 Owner 手动解除，yaml:3156-3192）+ 熔断五级状态机三件——
  R1-01 熔断分级判定（L0 正常/L1 警戒日亏≥2%/L2 禁开仓≥4%/L3 减仓≥6%/L4 保命回撤≥25%，
  迟滞解除"当日无新低+修复 50% 才降一级，禁 V 型回满"，MOD-RK-049
  drawdown_state_machine.py，yaml:3193-3227）、R1-02 熔断期减仓（重亏仓→高波动仓→压舱石，
  MOD-RK-050，yaml:3228-3258）、R1-03 护盘白名单（proposed 假说）；**TDM-P-P1-04 风险否决体检**；
  **TDM-F-C2-02 组合约束栈/C2-03 相关性聚类与 cluster 上限**（yaml:3850-3949）。
- battle_map：BM-RC-01 风控策略与限额管理（9 种限额，production）/02 盘前风控检查/
  03 Kill Switch 熔断/04 盘中持仓风控监控（VaR/回撤/因子暴露/流动性）/06 系统性风险五信号+
  尾部 EVT（S33/S34 供数证据 battle_map_09_risk_control.md:1214,1247）/09 AI-Agent 风险治理/
  10 风险否决权（design 态）/11 独立风险数据管道/12 极端事件与黑天鹅（battle_map_09 节点名）。
- 组合侧：BM-POS-05 资金曲线回撤缩放、BM-POS-02 Kelly、BM-POS-08 资金曲线自诊断
  （S70 供数证据 battle_map_08_position_management.md:263-271,481-489）。
- 四层止损作用域（m-11）：单票连续价（X-S1-02）/做T价差+时间（P2-02）/sleeve 月度净值
  （F-C3-02：5% 减半·7.5% 冻结）/组合日度+回撤（X-R1）（yaml X-R1 注释）。

### ②数据通道
- 阈值/限额注册：RLM-KILLSW-003/005、RLM-KILL-SWITCH-004/005/006、THD-DRAWDOWN-001/002/003
  （yaml X-R1 threshold_refs/risk_limit_refs）。
- 组合净值/回撤序列：BM-POS-08 消费"组合净值历史"（S70）——产槽为纸面/模拟盘净值链
  （alloc_budget_daily/adjudication 凭证链，daily-orchestrator-blueprint §六）。
- **kill_switch 本体**：src/zephyr/security/access_control/kill_switch.py（MOD-INF-018）production，
  宪法 §7 速查表在册；心跳失联→默认降级安全态（I-06/M-60，yaml X-R1 注释）。

### ③原料清单
- 已供给：**S33**（融资余额+流动性+政策新闻+外围指数→BM-RC-06-A 系统性风险五信号）、
  **S34**（尾部数据+跳跃检测→BM-RC-06-B EVT/POT）、**S36**（成交量+持仓+行情→BM-RC-04-E）、
  **S41**（restricted_shares/share_unlock→35_drawdown_protocol 解禁压力减仓）、
  **S43/S45**（etf_nav/kline_futures→37_liquidity_crisis_protocol 对冲池）、
  **S69**（历史极端事件库 2008/2015/2020→BM-SIM-05 压力测试）、**S70**（组合净值历史→BM-POS-08）。
- 缺口：**D31**（预算带数值 proposed→confirmed）；**LK-13**（本表新登）组合净值全史依赖模拟盘
  积累（"整装回测尚无正收益记录"，owner-vision-system-mapping §三）——回撤状态机的全史输入
  在实盘前只有模拟盘长度。

### ④本环节状态轴
- 输出量=**熔断级别 L0-L4**（R1-01 离散状态机）+ 组合回撤/日盈亏双轴读数 + 谨慎度 risk_signal
  （L1 侧，环节 1 产出）+ 风险否决结论（P1-04）。
- 消费方：X-S2 离场执行；P3-01 加仓资格门④（"熔断禁加期=R1-01 状态机 L1 及以上持续期间"，
  yaml R1-01 注释 M-36）；全系统开仓通道冻结；编排器 no_trade 三源之一（kill_switch active，
  blueprint §二 S5）；Owner（L4 人工接管）。

### ⑤概率表覆盖
- **风控层无概率表**（阈值/状态机语义，非概率推断——如实注）。间接件：P1-T3 相位转移矩阵
  服务"下游置信度加权"（04 §一 T3）；UP-5 尾部对冲信号=组合预测 CVaR(5%) 破 −3% 阈值→
  生成对冲建议（信号非指令，D107 回测验证前休眠，yaml X-R1 UP-5 注释）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | ✓ | kill_switch production 常驻、横切独立于编排器运行（blueprint §一.5"编排器缺席不阻塞保命"） |
| 深史全 | 🟡 | 阈值注册在册；组合净值全史=模拟盘长度（LK-13） |
| 状态真值全史 | 🟡 | 熔断级别流转全史台账仓内未见物化表（R1-01 输出落库面未见——本表如实注） |
| 概率表可算 | ✗ | 风控无概率表（阈值语义；CVaR 信号在库休眠） |

### ⑦缺口清单
D31；LK-13；M-55（Owner 手动接管正式入口节点，paper 升档前）；BM-RC-10 风险否决权/RC-11
独立管道=design 态（battle_map_09 节点名；panorama 设计态计数）；**LK-14** R1-03 护盘白名单
proposed 未回测生效（yaml X-R1-03）。

### ⑧下游消费方
X 流全链（S1-06 强制清仓绕过通道）；P3-01 加仓资格门；编排器 no_trade 合成；F-C2 组合聚合
（预算变动三级升级 C2-04）；Owner 门位（L4 解除/复位）。

---

## 环节 9 · 复盘与监控（日循环/warroom/归因）

### ①骨架节点
- TDM：**TDM-E-L0 盘前作战计划**四件——L0-01 计划生成/L0-02 偏离监控与修订（plan_deviation_monitor
  production，yaml:178-202）/L0-03 收盘复盘与明日边界（tomorrow_boundary_planner production；
  closing_session_decision→brier_calibration 回填→明日边界，yaml:203-231）/L0-04 明日情绪盘中
  滚动预测（yaml:232-265）；**TDM-F-C3 绩效归因反馈**五件——C3-01 多维归因引擎/C3-02 升降级管线
  与退役评审/C3-03 sleeve 权重调权/C3-04 参数校准闭环/C3-05 可靠度养成与信号健康
  （yaml:3780-4172，"系统自我进化的发动机"）。
- 作战室（warroom）：MOD-PLAN-018 daily_warroom_pipeline（testing，**仓库内零调用方**——
  audit §三 TDM-E-L0 行）；作战室三任务产品需求（盘中实时走势分析/明日走势概率/验证昨日计划，
  blueprint-addendum-warroom-three-tasks.md 三任务节；判定台账标准三表
  trading_vision/2026-09-16-judgment-ledger-standard.md）。
- 日度编排器（日循环心脏）：**BT-P1-031 蓝图已立、本体不存在**（daily-orchestrator-blueprint.md
  §一"持有今日不交易权"；owner-vision-system-mapping §三"无日度编排闭环……编排器不存在"）。
- battle_map：BM-REC-02 报告复盘（TCA/绩效归因/A 股交易复盘/风险报告）/BM-REC-03 闭环优化反馈
  （因子/信号/模型层反馈+元级迭代）（battle_map_11_reconciliation.md 节点名）。
- 电态：ORG 域 5 节点 2 已接电（L0-02/L0-03）/3 覆盖未接电（audit §三 ORG 行族；
  "组织者两件：都不存在"=周期切换器+日度编排器，audit §大白话摘要末行）。

### ②数据通道
- **decision_daily**（日度决策快照表）：蓝图 schema 已定（§4.1 DDL 草案，c1_backtest 库）；
  "decision_daily 表已建（v1 安全态）"（data-sufficiency-matrix §五层矩阵 L4 行）。
- 判定台账三表：judgment_intraday_market_state/judgment_next_day_forecast/scenario_hits
  （warroom 三任务，addendum 三任务节）。
- 归因输入：sim_trade_log 等模拟盘四件（S37）+ L4-14 执行成本反馈（断链 D34）+ C3 基准
  BMK-INDEX-003/BMK-ABSOLUTE-001（yaml F-C3 benchmark_refs）。
- 触发链：daily_kline SUCCESS 唤醒→regime 快照→pf_alloc→编排器（第三棒）（blueprint §三.2）。

### ③原料清单
- 已供给：**S37**（模拟盘四件+成绩台账）；L0-02/L0-03 production 件（audit 电判）。
- 缺口：**D29** 部分缺口（S2 regime 快照滞后阈值治本——供给闸 3 日 vs 消费阈 1 日，"已补印未治本"，
  demand ledger §四）、**D34**（执行成本反馈断链，归因输入缺一条腿）、
  **D7**（Brier 校准三消费点未接线）、**LK-15**（本表新登）归因三欠账未清（D50：交易/持仓盈亏
  二分+策略级 P&L Explain+逐笔 TCA，yaml F-C3 注释"三项已由 C3-01 承接落位"但输入面
  L4-14/S37 均在途）。

### ④本环节状态轴
- 输出量=**一行可审计的日度决策快照**（decision_daily：market_state/position_cap/package_set/
  no_trade+reason 枚举/degraded 轨迹，blueprint §4.1 列清单）+ **归因拆账**（L1/L3/L5 各层贡献，
  "整条链赚钱≠每层有用……不赚钱的层砍掉"，owner-vision-system-mapping §二.3）+
  Brier 校准分（预测 vs 实际回填打分）。
- 消费方：次日 L0-01 计划生成；C3-02 退役评审（升降级）；C3-03 调权；Owner 晨报/仪表盘
  warroom 组件（audit L0-03 行"仪表盘 warroom 组件消费（人工面）"）。

### ⑤概率表覆盖
- Brier 校准闭环=本环节概率件（预测概率的日常打分）——三零件（8 态/相似日/校准）全在、
  消费未接线（D7；L0-04 覆盖未接电）。
- P1 表重估节奏与漂移降权挂点（Shrinkage provider）=05_drift_reestimation.md（冷水⑥消费路径，
  06_methodology 冷水⑥行）。

### ⑥四判据
| 判据 | 勾 | 证据 |
|---|---|---|
| 通道在线 | ✗ | 日度编排器本体不存在（BT-P1-031 蓝图待批开工）；warroom pipeline 零调用（audit §摘要"这就是 Owner'感觉没运作'的机械解释"） |
| 深史全 | 🟡 | decision_daily 刚建 v1 安全态（data-sufficiency L4）；决策快照历史=0 |
| 状态真值全史 | ✗ | 计划 vs 实际核对全史未见（postmarket_reconcile 仅签名占位，blueprint §二 T4 行） |
| 概率表可算 | ✗ | Brier 闭环三零件在未接线（D7）；归因拆账输入面在途（LK-15） |

### ⑦缺口清单
BT-P1-031 编排器施工（蓝图待 Owner 批）；warroom 三任务（表与结算器先行，addendum 施工挂点）；
D7/D29/D34；LK-15；**LK-16**（本表新登）六段↔五态映射未落地（routing_table_v1_draft §1
"全仓无映射定义"——盘中五态行与六段编排器接口对不上）。

### ⑧下游消费方
Owner（晨报/门位）；次日计划链 L0-01→L0-04；C3 归因→退役评审→调权（环节 6 上游回灌）；
仪表盘（src/zephyr/frontend/dashboard/app_panel.py，宪法 §7）；drift 重估循环（05 分册）。

---

## §8 总勾表与缺口汇总

### 8.1 九环节 × 四判据总勾表

| 环节 | ①通道在线 | ②深史全 | ③状态真值全史 | ④概率表可算 | 一句话 |
|---|---|---|---|---|---|
| 1 大盘状态判定 | ✓ | ✓ | ✓ | 🟡（T3 在算） | 全仓最强层，唯概率表在交 |
| 2 大盘情绪 | 🟡 | ✗（143 日） | ✗（真值 16 日） | ✗（D28 INSUFFICIENT） | 温度计已装、历史最短 |
| 3 板块状态与轮动 | ✓ | 🟡（三处断/短史） | 🟡（回放 985/1584 日） | 🟡（T1/T2 在交；S10 NO_EDGE） | 数据厚、有效性标尺刚证伪一轴 |
| 4 板块→个股传导 | 🟡 | 🟡 | ✗（无池载体） | ✗ | 只在回测里跑 |
| 5 个股做T | ✓ | ✓ | 🟡（六段 CSV 待落地） | 🟡（26 对<30 待材料线） | 材料全、考试差样本 |
| 6 策略考试与上岗 | ✓ | ✓ | ✓ | 🟡（成绩单在途、上岗规则未立） | 考试机器实战、上岗规则缺位 |
| 7 执行 | 🟡 | 🟡 | ✗（TCA 无台账） | ✗ | 桥通、无人下单、反馈断链 |
| 8 风控 | ✓ | 🟡 | 🟡 | ✗（阈值语义） | 保命件常驻、净值史浅 |
| 9 复盘与监控 | ✗ | 🟡 | ✗ | ✗ | 骨架最弱层——心脏未装 |

（✓/🟡/✗ 判据逐项证据见各环节⑥；本表为导航，不替代逐条出处。）

### 8.2 缺口编号汇总表（按环节排序）

| 环节 | 沿用册编号（D=demand / S线G=sector / E线G=emotion） | 本表新登 LK |
|---|---|---|
| 1 大盘状态判定 | D2/D3/D4/D5/D7/D33；六段分叉 6 步（appendix_C） | — |
| 2 大盘情绪 | E线 G5/G6/G8/G12/G13；D6/D28 | LK-01（IC 加权二期未启）；LK-02（#400 枚举收敛未落） |
| 3 板块状态与轮动 | S线 G2/G4/G5/G7/G8/G9/G12/G14；D11/D12/D15/D16/D18（G3 已复通销口） | LK-03（S10 后动量成分集未定） |
| 4 板块→个股传导 | D19/D21/D22；S线 G6 | LK-04（L3 生产挂点）；LK-05（个股状态轴+概率表空白） |
| 5 个股做T | D24/D26/D36；甲位门位（07 号文 §C） | LK-06（转债分钟 bar）；LK-07（三策略全 proposed） |
| 6 策略考试与上岗 | D30/D31 | LK-08（PBO/CPCV 未接）；LK-09（退役重考未开）；LK-10（上岗规则 v1 未立）；LK-11（T1 轻档代码缺） |
| 7 执行 | D34/D36；BT-P2-055 挂单 | LK-12（逐笔 TCA 欠账） |
| 8 风控 | D31 | LK-13（组合净值全史浅）；LK-14（R1-03 未回测生效） |
| 9 复盘与监控 | D7/D29/D34；BT-P1-031 蓝图 | LK-15（归因三欠账输入面）；LK-16（六段↔五态映射未落） |

### 8.3 骨架空洞清单（仓内连骨架定义都缺或仅设计稿的部位）

1. **上岗规则层**（环节 6）：考试机器与成绩单全套在，但"条件共振→选策略"的骨架节点在 TDM
   无对应 node（state_matrix=配置矩阵），唯一形态=设计稿（routing_table_v1_draft.md，Owner 批前
   零 config）+切换摩擦提案（04_switch_friction）。
2. **日度编排器本体**（环节 9）：蓝图 170 行级细节齐备（blueprint S1-S7/一库一闸/降级矩阵），
   本体不存在、warroom 零调用——ORG 域"两件组织者一件零调用、一件不存在"（audit §摘要）。
3. **个股层状态轴物化**（环节 4）：候选池/评分/传导分有 TDM 节点定义但无持久化载体（D22=M-41）、
   无概率表、无生产挂点——骨架定义在、状态轴与概率面双空洞。
4. **执行层反馈面**（环节 7）：L4-14 节点在图、三零件在库、选择器不消费（D34"断链实证"）——
   反馈闭环有骨架无名分（节点无消费边）。
5. **情绪概率面**（环节 2）：情绪指数本体+成分骨架齐，但情绪轴入概率表的卡（D28 重考）要等
   2027-03 真值窗——概率面空洞为时间性空洞而非定义性空洞。

---

## §9 挖掘执行日志（mining_sop/skeleton_mining_policy.md §7 纪律）

| 批 | 矿脉 | 证据源（路径） | 判定 |
|---|---|---|---|
| B1 | 战役八件全读 | decision_map_campaign/README+01～08 | signal（数据面实测表直引 01 §三） |
| B2 | 需求侧 D1-D36 / 供给侧 S1-S70 | ultimate_library/ulib3b_demand_gap_ledger.md / ulib3b_supply_relationship_ledger.md | signal |
| B3 | 板块线缺口+骨架 v0 / 情绪线缺口+骨架 v0 | sector_line/sector_gap_list_and_construction_proposal.md、sector_layer_skeleton_v0.md；emotion_line/两件 | signal |
| B4 | TDM 全节点提取（138 节点名+关键 algo_note） | config/trading_decision_map.yaml（awk 提取 node_id×name_zh 全表；精读 L0/L1/L2-06/L3-04/P2/X-R1/F-C3 段） | signal |
| B5 | battle_map 域节点名+panorama 统计 | battle_map/index.md、battle_map_panorama.md 头、08 域文件标题扫描 | signal（341 环节/151 production/157 design） |
| B6 | 五层骨架覆盖审计+Owner 愿景映射+蓝图族 | trading_vision/ 三件+skeleton-coverage-audit 全节点落格表 | signal（SKL1-L5 电态矩阵为环节⑥勾的重要证据源） |
| B7 | 做T矩阵+条件卡+考试报告 | t0_matrix/T0_SCHEME_MATRIX.md、t0_revival/t0_conditional_prereg_card.md、sector_line/exam/prereg_exam_report_v1.md | signal（S10 NO_EDGE/D2 INSUFFICIENT/26 对卡点） |
| B8 | 方法论十册+策略工厂+日循环路由 | quant_methodology/README.md、2026-09-13-strategy-factory-pipeline-discussion.md、daily_loop_campaign/routing_table_v1_draft.md | signal |
| B9 | 挖矿 SOP 对表 | mining_sop/skeleton_mining_policy.md（三扫收敛/状态标记/日志纪律） | 本日志按其 §7 落 |

**三扫收敛声明**：B1-B9 九批后，九环节×八项每格均有出处或"仓内未见"明示；未做第四批
（外部方法论文档 sector_external_methodology.md 等属算法源非骨架源，不入骨架证据）。
**封矿声明**：本表为骨架导航件，节点号/状态轴/缺口以各真源为准，本表禁作为新增节点号的出处
（防第二真源漂移——skeleton_mining_policy §2"骨架外新条目须先回写真源骨架"）。
