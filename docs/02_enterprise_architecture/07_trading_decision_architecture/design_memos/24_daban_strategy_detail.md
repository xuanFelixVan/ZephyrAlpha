---
ttl: permanent
doc_type: architecture_view
title: 打板策略细节
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.10.6"
date: 2026-08-15
topic: daban_strategy_detail
scope: 07_trading_decision_architecture
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：打板信号链四引擎 + 支撑设施全部 production 实证——short_term_stock_selector（7 维评分卡）/ youzi_relay_emotion_engine（6 因子+情绪周期 4+1）/ quant_short_term_strength_engine（6 维 A~E 评级）/ dual_engine_fusion_decision_engine（60/40 基准+自适应 5 档+6 类决策），均有测试；支撑设施 cash_manager（T+1 结算）/ position_sizing_engine（C12）/ drawdown_controller + kill_switch 系 / cancel_rate_guard + price_cage（2026 程序化新规，40 号 v2.6.0 已闭合）/ ex_core 执行层全 production。注：§3.6 所述"budget_change_handler.py 骨架待填充"已过时——MOD-POS-022 经 33 号批次（AI-BGT-001）落成完整实现（TierLevel/FreezeNewPositions/RebalanceRequest/ForcedTrim/BudgetChangeHandler 实证）。
>
> **最终成果**：打板策略细节定稿（active v1.10.6）——8 项讨论要点 + §3.13/§3.14 十二项施工算法形式化 + 8 具名函数设计，覆盖信号→定位→入场→封板→出场→风控→容量全流程。
>
> **未做事项及原因**：12 项形式化算法 + 8 具名函数全部未落码（grep 实证零命中）——§3.13 七项（NextDayExitDecision 含 classify_position_status / DabanInstantCircuitBreaker / classify_decision_v192 第 7 类 REFLUSH_DIVE / DabanExecutionAlgorithm / get_dragon_tiger_pit PIT 断言 / SignalDecayMonitor / reflush_next_day_exit_decision）+ §3.14 五项（pre_validate_daban_signal / HoldingPeriodMicrostructureMonitor / DabanPITBacktestFramework / DabanTimingDecision / DynamicCapacityCalculator）+ 8 具名函数（classify_echelon_health / score_consecutive_height_with_death_pool / score_auction_3d / detect_auction_paper_tiger / score_seal_structure / forecast_next_day_premium / classify_reflush_board / detect_quant_seat_warning）；按 §6 登记排期——#1/#2/#5/#8/#9 首批实盘前必做、#10 首批回测前必做、#6 实盘后即需、#3/#7 Phase 5、#4/#11/#12 Phase 3；两层分类法统一裁定（§6）与 C9 换手率分层校准待首批回测。Phase 5 ML 栈（CatBoost 破板预测/Siamese LOB/QFCQT/Hawkes/速度签名/Du 混合模型）为远期登记。

# 打板策略细节

> **性质**：已定型（active）。由 [00_index_trading_decision](00_index_trading_decision.md) G08 主题组派生，8 项讨论要点已逐项对齐落入 §3 决策。
> **施工图纪律**：本文档定型后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。
> **v1.9.2~v1.9.7 七轮审查整合**：§3.13 七项 + §3.14 五项施工算法补全（含 §3.13#1 classify_position_status 字段填充断裂点修复、§3.13#4 passive impact/SaR 升级、§3.13#6 two-type classification 升级）+ 2026-08 arXiv 研究背书（liquidation cascade / Public Trader Identity / 北大打板理性预期 / 价格笼子实证 / Siamese LOB / Du 开盘信号混合模型 / QFCQT 混沌门控 / Hawkes 长记忆核 / QLoRA 情感因子负面警示 / 速度域签名 / 扩散价格动力学悖论）——12 项施工算法完整覆盖信号→定位→入场→封板→出场→风控→容量全流程，逐轮明细见 §9 修订记录。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G08 打板策略细节 |
| 所属 | 作战地图 05（BM-SEL-25 打板 sleeve） |
| 依赖 | G04（[20_first_batch_strategies](20_first_batch_strategies.md) §2.2 打板 sleeve）、G05（信号工坊）、G21（[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 情绪周期）、G22（40_execution_broker 执行层） |
| 对标 | 雪球炸板率统计 2026-07 / 华安证券涨停板 Alpha 2026-03 / caifuhao 连板复盘 2026-08 / IG507 涨停统计分析 2026-08 / legulegu 首封时间线性映射 2026-07 |
| 正交 | ✅ 与 regime 正交（[28 §3.4](28_sentiment_cycle_trading.md) 与 regime 的正交性 + [20 §2.2](20_first_batch_strategies.md) 打板 sleeve 表）：打板读情绪周期不读 regime，情绪周期=sleeve 内 alpha 择时，regime=市场级风险节流，两者正交 |
| 优先级 | P1（高换手、小容量、高频 alpha） |
| 状态 | active 1.10.6（8 项讨论要点已对齐 §3.1-§3.8 + 12 项施工算法 §3.13/§3.14 覆盖信号→定位→入场→封板→出场→风控→容量全流程 + 设施盘点 §1.1 + Phase 5 ML 增强栈 §5.2——逐项明细见文首块引用与 §9 修订记录） |

### 1.1 已施工设施盘点（通用规则 #11，2026-08-12 代码侧真源审计）

> 本节盘点打板 sleeve 相关的全部已建设施（代码/测试真源，grep 级核实），作为 §3 各裁定"复用而非新建"的事实基座。✅=已落码 production，🟧=骨架/文档态未落码，⚠️=术语或分类法消歧。

**① 打板信号链四引擎（`src/zephyr/signal_ashare/`，全部 production 且有测试）**

| 设施 | 真源路径 | 状态 | 本文档消费点 |
|---|---|---|---|
| 短线选股评分卡 7 维（BM-SEL-22） | `short_term_stock_selector.py`（`score_limitup_potential`：连板高度/封单强度/板块效应/分歧程度/市值流动性/封板时间/催化强度 7 维 100 分）+ `tests/signal_ashare/test_short_term_stock_selector.py` | ✅ production | §3.1 连板梯队评分基座 / §3.4 容量约束输入 |
| 游资接力情绪引擎 6 因子+情绪周期 4+1（BM-SEL-23） | `youzi_relay_emotion_engine.py`（`YouziRelayEmotionEngine`：`score_consecutive_height`/`score_seal_quality`/`score_seal_time`/`score_open_board`/`score_auction_strength`/`score_assist_echelon` 6 因子 + `determine_emotion_phase` 阶段定位 + `map_strategy` 策略映射）+ 对应测试 | ✅ production | §3.2 情绪周期定位器（why：6 因子权重 25/20/15/15/10/10 sum=95，阶段阈值 20/40/65/85——§3.8 已裁定源码为真源） |
| 量化短线强度引擎 6 维（BM-SEL-24） | `quant_short_term_strength_engine.py`（价格动量 Z-score/行业强度/相对强度/资金/技术/风险 6 维 + A~E 五级评级 + `StockCategory` 分类）+ 对应测试 | ✅ production | §3.3 主升龙头识别的量化引擎输入 |
| 双引擎融合决策（BM-SEL-25） | `dual_engine_fusion_decision_engine.py`（`DualEngineFusionDecisionEngine`：`determine_adaptive_weights` 情绪周期自适应权重 5 档 + `classify_decision` + `extract_pdf_signal` 4 维 PDF 信号）+ 对应测试 | ✅ production | §3.5 双引擎融合——⚠️ production 输出为 **6 类标的分类**（主升龙头/二进三/跟风/复苏/伪强/地天反包 + NEUTRAL 兜底），基准权重**游资 60%/量化 40%**，与 battle_map BM-SEL-25 一致；见下方消歧④ |

> **作战地图子环节契约补注（v1.10.1 补，BM-SEL-22-A/22-B/25-D 闭合）**：上表两个引擎的作战地图子环节——BM-SEL-22-A 机构选股评分器（`short_term_stock_selector.py`，MOD-SIG-023 内一支）、BM-SEL-22-B 强庄股识别器（同模块内一支）、BM-SEL-25-D PDF 分布信号提取（`extract_pdf_signal`，MOD-SIG-035 内一支）——此前仅登记级提及，契约描述已补全于 **§3.5 后附段**（3 支均为 ✅ production 有测试，本次为文档补记，无代码变更）。

**② 打板支撑设施（执行/资金/风控/合规）**

| 设施 | 真源路径 | 状态 | 本文档消费点 |
|---|---|---|---|
| T+1 现金结算 | `src/zephyr/position/core/cash_manager.py`（POS-06：`available_cash = total_cash - pending_settlement`，卖出 T+1 结算次日释放） | ✅ production | §3.7 T+1 时序（why：T+1 结算是打板"次日才能卖"的资金面硬约束实现） |
| 单票仓位上限 | `src/zephyr/position/core/position_sizing_engine.py`（C12 ≤5% NAV） | ✅ production | §2.3 约束条件 / §5.1 系统上限 |
| 账户级回撤 Protocol | `src/zephyr/position/core/drawdown_controller.py` + `src/zephyr/risk/core/drawdown_tracker.py` / `var_calculator.py` + kill_switch 系列 | ✅ production（[30 §2.5]） | §3.6 第二层风控（why：打板波动远大于多因子，账户级四级回撤+Kill Switch 是生存红线） |
| firm 层 budget 裁剪 | `src/zephyr/position/core/budget_change_handler.py`（MOD-POS-022） | 🟧 骨架待填充（§6 已登记） | §3.6 第三层风控 |
| 程序化交易合规 | `src/zephyr/ex_core/cancel_rate_guard.py`（撤单率滚动监控 ≤15%）+ `price_cage.py`（价格笼子） | ✅ production（[40号](40_execution_broker.md) v2.6.0 已闭合） | §3.7 2026 程序化新规约束 |
| 执行层（G22） | `src/zephyr/ex_core/execution_engine.py` / `order_execution_saga.py` / `fill_handler.py` 等 | ✅ production | §3.13#4 分笔建仓依赖 / §3.14#11 打板时点决策落地层 |
| 板块/资金/机构行为分析 | `sector_analyzer.py` / `capital_flow_pattern_analyzer.py` / `institutional_behavior_analyzer.py` / `market_sentiment_analyzer.py` / `intraday_buy_sell_point_analyzer.py`（均 signal_ashare/） | ✅ production | §3.1 梯队板块共振 / §3.3 资金引擎 / §3.14#8 前置质量评估的数据源 |

**③ 文档态形式化算法（🟧 全部未落码——2026-08-12 grep 全 `src/` 零命中，属"文档已定型、代码待施工"）**

| 算法 | 文档位置 | 施工时点 |
|---|---|---|
| §3.13 七项：NextDayExitDecision（含 classify_position_status）/ DabanInstantCircuitBreaker / classify_decision_v192（第7类 REFLUSH_DIVE）/ DabanExecutionAlgorithm / get_dragon_tiger_pit / SignalDecayMonitor / reflush_next_day_exit_decision | §3.13 | 首批实盘前必做（#1/#2/#5）/ Phase 3-5（其余） |
| §3.14 五项：pre_validate_daban_signal / HoldingPeriodMicrostructureMonitor / DabanPITBacktestFramework / DabanTimingDecision / DynamicCapacityCalculator | §3.14 | 首批实盘/回测前必做（#8/#9/#10）/ Phase 3（#11/#12） |
| v1.5.0~v1.9.0 增补具名函数：classify_echelon_health / score_consecutive_height_with_death_pool / score_auction_3d / detect_auction_paper_tiger / score_seal_structure / forecast_next_day_premium / classify_reflush_board / detect_quant_seat_warning | §3.1/§3.9/§3.11 | 同上——§6 待裁定表"已补"指**文档算法补全**，非代码已 production，阅读时勿误读 |

**④ ⚠️ 术语与分类法消歧**

1. **引擎命名**：本文 §3.5 原表述"情绪引擎/技术引擎"= battle_map 与源码的"**游资情绪引擎**（BM-SEL-23）/**量化强度引擎**（BM-SEL-24）"。v1.10.0 起正文统一用 battle_map canonical 名。
2. **决策分类法两层架构**：battle_map BM-SEL-25 与 production `classify_decision` 输出 **6 类标的分类**（主升龙头/二进三/跟风/复苏/伪强/地天反包）；本文 §3.5 表的 7 类（BOARD/CONTINUE/INVERSE_BOARD/REFLUSH_DIVE/WATCH/REJECT/WAIT）是**交易动作层**分类法（标的分类→买卖动作的映射），其中第 7 类 REFLUSH_DIVE 为 v1.9.2 设计态新增、代码未落。v1.8.2 修订记录中"伪代码修正为多维条件版匹配 production `classify_decision`"的表述**不准确**——两者分类语义不同层，不存在逐行匹配关系；v1.10.0 已修正 §3.5 表述。两层映射的最终统一裁定见 §6 待裁定新增条目。
3. **正交引用**：[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) 已于 2026-08-12 填充定型（active 1.0.0，commit `0db887c9e7`，按引用方锚点重建），本文 `[28 §x.x]` 前向引用已全部落地——§3.2 5 阶段买卖纪律 / §3.4 与 regime 的正交性 / §3.5 退潮加权机制（§6 待裁定对应行已核销）。

**盘点结论**：打板 sleeve 的信号识别链（BM-SEL-22→23→24→25）四引擎与支撑设施（T+1 结算/仓位上限/回撤 Protocol/程序化合规/执行层）**全部 production 且有测试**，这是 §3.1-3.7 各裁定"复用已建打板链"的事实基座。未落码的是 v1.9.2/v1.9.3 两轮施工算法审查补全的 12 项形式化算法 + 8 个具名函数——它们是从"信号→定位→入场→封板→出场→风控→容量"全流程的断裂点补全，施工时点已在 §6 逐条登记（首批实盘前/Phase 3/Phase 5）。**先清楚有什么 → 才能知道怎么改 → 才知道该退役什么**：当前无需退役项。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-22-C | 连板潜力评分卡 | §1.1①（`score_limitup_potential` 7 维 100 分表行）/ §3.1（裁定复用 22-C-1，连板梯队评分基座+中位股死亡池） | production已建 |
| BM-SEL-22-C-1 / BM-SEL-22-C-2 / BM-SEL-22-C-3 / BM-SEL-22-C-4 / BM-SEL-22-C-5 / BM-SEL-22-C-6 / BM-SEL-22-C-7 | 七维度（连板高度/封单强度/板块效应/分歧程度/市值流动性/封板时间/催化强度） | §1.1①（评分卡 7 维逐维列出）/ §3.1（梯队分档与健康度四档判定消费） | production已建 |
| BM-SEL-22-D | 连板分歧程度评估器 | §1.1①（评分卡"分歧程度"维）/ §3.13 缺失#1（`soft_exit_divergence` 分歧度>0.5→软退出） | production已建 |
| BM-SEL-23-A | 6因子游资接力评分 | §1.1①（游资接力情绪引擎 6 因子行）/ §3.2（情绪周期定位器评分输入）/ §3.8（6 因子权重 25/20/15/15/10/10 sum=95 源码真源裁定） | production已建 |
| BM-SEL-23-A-1 / BM-SEL-23-A-2 / BM-SEL-23-A-3 / BM-SEL-23-A-4 / BM-SEL-23-A-5 / BM-SEL-23-A-6 | 六因子（连板高度/封单质量/涨停时间/开板次数/竞价强度/助攻梯队） | §1.1①（6 因子函数逐支列名）/ §3.8（助攻梯队因子权重真源裁定；battle_map A-6 分值修正登记 §6） | production已建 |
| BM-SEL-24-A | 6维度量化强度评分 | §1.1①（量化短线强度引擎 6 维行）/ §3.3（主升龙头识别的量化引擎输入）；架构定位与 6 维权重校准归 [21_stock_selection_engine](21_stock_selection_engine.md) §3.4——分工：21 号管三层选股架构中"量化引擎输入"的定位/边界/权重校准方法，本篇管打板 sleeve 内逐维构成与消费点 | production已建 |
| BM-SEL-24-A-1 / BM-SEL-24-A-2 / BM-SEL-24-A-3 / BM-SEL-24-A-4 / BM-SEL-24-A-5 / BM-SEL-24-A-6 | 六维度（价格动量Z-score/行业强度/相对强度/资金/技术/风险） | §1.1①（6 维逐维列出）；维度权重 20/15/20/15/20/10 与 IC 加权/SHAP 校准路径见 21 号 §3.4 | production已建 |
| BM-SEL-24-B | A~E五级评级 | §1.1①（强度引擎行：A~E 五级评级 + `StockCategory` 分类） | production已建 |

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是个人 + 100% AI 开发的 A 股量化交易系统。首手 3 策略（打板/多因子/事件驱动）已在 [20 §2.2-2.4] 定义为差异化 sleeve。打板 sleeve 定位为"高换手、小容量、打板首板/连板的突击 sleeve"，承载小资金高 alpha。

**2026 打板效益崩塌硬数据**（caifuhao 2026-08-03 游资换打法 + caifuhao 2026-08-02 复盘1200只连板）：
- 次日溢价：4.2%→1.7%（腰斩）
- 炸板率：68%（2026 vs 2023 的 ~30%）
- 量化占比：35%（2026 vs 2023 的 <10%）
- 涨停时间分层炸板率：早盘<20% / 尾盘>50%

打板 sleeve 仍在存活的原因：情绪周期定位器在退潮期强制空仓（[28 §3.2]），规避大部分炸板风险；主升/疯狂期打板次日高开溢价概率仍高。但效益崩塌要求更精细的信号识别和风控。

### 2.2 核心问题

1. **连板梯队如何识别**——连板股按高度分梯队，梯队健康度决定打板安全性。
2. **情绪周期如何定位**——4+1 阶段（冰点/反核/主升/疯狂/退潮），退潮为条件触发。
3. **主升龙头如何识别**——三引擎共振（情绪+技术+资金）。
4. **打板容量极小**——单票几万~几十万，13 项约束链常触发。
5. **双引擎融合在此策略内部**——60/40 基准+情绪周期自适应，7 类决策。
6. **打板专用风控参数**——三层风控+第四层瞬时风控。
7. **T+1 约束下的打板时序**——T日打板→T+1日卖出，2026程序化新规额外约束。
8. **助攻梯队权重真源裁定**——解决 [28 §6] 口径漂移。

### 2.3 约束条件

- **单票仓位**：≤5% NAV（C12），实际受 C6/C11 制约远小于此
- **sleeve 容量**：单票几万~几十万，sleeve 整体 50-200 万（待实盘校准）
- **持仓周期**：1-3 天（T+1 约束 + 情绪周期）
- **并发持仓数**：≤10 只（小账本约束）
- **PIT 铁律**：INV-004——龙虎榜数据 T 日盘后公布，T 日盘中决策只能用 T-1 日及之前龙虎榜（§3.13 缺失#5 PIT 处理补全）
- **T+1 结算**：买入当日扣减可用，卖出 T+1 结算，资金周转 2 天起
- **程序化新规**：内部限频 ≤15 笔/秒（安全垫，远低于法定 300 笔/秒）+ 撤单率 ≤15% 硬限

## 3. 决策

### 3.1 讨论要点①：连板梯队识别

**裁定**：复用 22-C-1 + 23-A-1 + 25-C-3，不单独建模块。连板梯队按高度分档，梯队健康度四档判定。

**连板梯队分档**：

| 梯队 | 高度 | 特征 | 打板安全性 |
|---|---|---|---|
| 首板 | 1 板 | 试探性涨停，次日溢价方差最大 | 中（需三引擎共振确认） |
| 2 板 | 2 板 | 确认性涨停，晋级率 ~50% | 高（主升期最佳打板标的） |
| 3 板+ | 3 板以上 | 龙头确认，但炸板率随高度递增 | 中（需梯队健康度确认） |
| 孤板 | 1 板无梯队 | 无跟风、无板块效应 | 低（炸板率 58%） |

**梯队健康度四档判定**（`classify_echelon_health`，v1.5.0 补施工算法）：PERFECT（梯队完整）/ FRACTURE（断层）/ LONE_DRAGON（孤龙）/ COLLAPSE（崩塌）。退潮预警条件③④新增——中位断层/畸形孤龙时强制降仓。

**炸板率板块地位分层**（v1.9.0 补）：龙头 8% / 跟风 32% / 孤板 58%（7 倍差距，caifuhao 2026-08-02 复盘1200只）。修正系数：龙头 ×1.2/跟风 ×1.0/孤板 ×0.5。

> **独立印证（v1.10.0 补）**：雪球 2026-02-25《A股打板开板率深度量化分析》（2021-2025 全市场回测）给出**完全相同的三层数字**——龙头 8%/跟风 32%/孤板 58%，并补板型分层：一字缩量板 8%（散户买不到，买到即炸板节点，当日回撤普遍>10%）/ 6板+ 12% / 3-5板中位 18% / 2板 21% / 首板 26% / 尾盘偷袭板（14:30后）52%；炸板口径区分"临时开板（回封不计入）vs 有效开板（未回封才计入）"。两套独立数据源同值互证，§3.1 分层可信。另：一字龙"零换手买不到"特性已被 §3.4 C9 换手率 3-15% 隐式拒入（一字板换手≈0），无需新增板型。

**分级梯队晋级率**（v1.7.0 补）：1进2 ~50% / 2进3 ~30% / 3进4 ~15% / 4进5 ~0%（退潮前兆）。

**中位股死亡池**（`score_consecutive_height_with_death_pool`，v1.5.0 补）：梯队断层/孤龙时 3-4 板扣 40/30 分，完美梯队维持原评分。

### 3.2 讨论要点②：情绪周期定位器

**裁定**：复用 23-B（情绪周期定位器），4+1 阶段，退潮为条件触发。准确率回测施工前必做（[30 §6.3]）。

**4+1 阶段**：

| 阶段 | 评分阈值 | 仓位上限 | 特征 |
|---|---|---|---|
| 冰点 | ≤20 | 0~极轻 | 跌停>涨停，连板≤3 |
| 反核 | 20-40 | ≤2-3 成 | 跌停板反抽出现 |
| 主升 | 40-65 | 3-5 成 | 涨停>跌停，晋级率>50% |
| 疯狂 | 65-85 | 2-3 成（减仓） | 连板≥20，首封时间<10:00 |
| 退潮 | 条件触发 | ≤1 成（清仓） | 4进5=0% / 中位断层 / 龙头炸板 |

**退潮条件触发**：①4进5晋级率=0%；②中位股断层；③龙头首次炸板；④连板数骤降。四条件任一触发。

**机理层理论背书**（v1.8.0+v1.9.2+v1.9.3 补）：
- **羊群 agent-based "超调→反转"微观机理**（[arXiv:2607.27063](https://arxiv.org/abs/2607.27063)）：信息扩散+社会强化分离机制解释情绪周期超调与反转。31 页 16 图 7 表，A 股实证，Johnson SU 变换尾部羊群指标。
- **Liquidation cascade 炸板级联机理**（[arXiv:2608.03616](https://arxiv.org/abs/2608.03616) 2026-08-05 Seuma）：清算级联亚临界分支——封单崩塌时持有者止损触发更多止损，形成局部级联。88% 级联卖出在 30 分钟内完成，63% 被做市商吸收。解释§3.10 三次炸板回封级联机理，与§3.13 缺失#2 瞬时风控直接相关。
- **打板理性预期模型（v1.9.3 补，北大 Jiang & Li）**：动态理性预期模型证明涨跌停规则通过阻碍信息完全纳入诱发涨停后跳空——知情交易者将价格推至涨停，未知情交易者推断信息未完全纳入→次日开盘推高。实证：封死涨停平均隔夜收益 +2.43%（打板者利润），打开涨停平均回撤 -5.25%（亏损为利润 2 倍+）。2020 创业板改革（±10%→±20%）自然实验提供因果证据：放宽涨跌停缓解投机扭曲。**这是 24 号文档的理论根基**——解释为何打板 alpha 存在（信息未完全纳入）+ 为何炸板亏损>涨停利润（回撤不对称性），为 §3.4 13 约束链 + §3.13#1 NextDayExitDecision 提供理论背书。

**准确率兜底**（[28 §3.2]）：置信度<60% 保守降仓，<40% 强制空仓。

### 3.3 讨论要点③：主升龙头识别

**裁定**：复用 25-C-1 三引擎共振打分。

**三引擎共振**：情绪引擎 40%（连板梯队健康度+晋级率+情绪周期阶段）+ 技术引擎 30%（量价突破+MA排列+换手率）+ 资金引擎 30%（主力净流入+龙虎榜游资席位+封单质量）。三引擎均≥70 分且情绪周期在主升/疯狂期→打板信号确认。

### 3.4 讨论要点④：打板容量极小

**裁定**：13 项约束链（C1-C13），C6/C11 常触发。小账本（单票几万~几十万），sleeve 整体 50-200 万。

**关键约束**：C6 封单量（封单≥流通盘 0.5%）/ C11 封成比（>10）/ C9 换手率（3%-15%）/ C8 涨停时间（首封≤10:00）/ C10 连板高度（≤5 板）。C6/C11 是最高频触发约束——封流比<0.5% 或封成比<10 时直接否决打板信号。

### 3.5 讨论要点⑤：双引擎融合在此策略内部

**裁定**：60/40 基准（**游资情绪引擎 60% + 量化强度引擎 40%**，即 BM-SEL-23/BM-SEL-24 双引擎）+ 情绪周期自适应（冰点量化 70% / 主升游资 70% / 退潮量化 60% 等 5 档，`determine_adaptive_weights`）。`dual_engine_fusion_decision_engine.py`（BM-SEL-25）已 production。

**两层分类法架构（v1.10.0 澄清，修正 v1.8.2 不实同步声明）**：

- **第一层：6 类标的分类（production 已实现）**——`classify_decision` 输出 主升龙头/二进三/跟风/复苏/伪强/地天反包（+NEUTRAL 兜底），与 battle_map BM-SEL-25-C 一致。这是"标的角色"判定。
- **第二层：7 类交易动作（本文档设计态，代码未落）**——下表 BOARD/CONTINUE/INVERSE_BOARD/REFLUSH_DIVE/WATCH/REJECT/WAIT 是"标的角色→打板 sleeve 买卖动作"的 sleeve 内映射层，其中第 7 类 REFLUSH_DIVE 为 v1.9.2 新增（§3.13 缺失#3）。
- **v1.8.2 声明修正**：v1.8.2 修订记录称"伪代码修正为多维条件版匹配 production `classify_decision`"——经 2026-08-12 代码侧审计，两者分类语义不同层（标的分类 vs 交易动作），不存在逐行匹配关系，该声明不准确。两层映射的统一裁定（动作层是否吸收进 production 引擎）见 §6 待裁定新增条目。

**7 类交易动作决策**（v1.9.2 补第7类，设计态伪代码见 §3.13 缺失#3 `classify_decision_v192`）：

| 决策 | 条件（游资=游资情绪引擎分，量化=量化强度引擎分） | 动作 |
|---|---|---|
| BOARD | 游资≥阈值+量化≥60（主升/疯狂） | 打板买入 |
| CONTINUE | 游资≥阈值×0.8+量化≥70 | 持仓续板 |
| INVERSE_BOARD | 游资≥60+量化≥75 | 地天反包（非反核） |
| REFLUSH_DIVE | 冰点/反核+跌停板反抽+游资≥40+量化≥60 | **反核入场**（v1.9.2 补） |
| WATCH | 游资≥40+量化≥50 | 观望 |
| REJECT | 默认 | 否决 |
| WAIT | 游资<20 | 冰点等待 |

> **§3.13 缺失#3 补充**：第7类 REFLUSH_DIVE + 情绪周期门控切换——主升/疯狂→打板路径，冰点/反核→反核路径。

> **作战地图子环节契约补全（v1.10.1 补，BM-SEL-22-A/22-B/25-D 闭合——3 支均 production，本文档补记契约，无代码变更）**：
>
> **① BM-SEL-22-A 机构选股评分器（production，MOD-SIG-023 `short_term_stock_selector.py` 内一支）**：短线选股评分卡（BM-SEL-22）内的机构视角评分维度，盘前全量+盘中增量触发，输出机构选股评分（0-100）汇入 BM-SEL-22 评分卡汇总。**裁定**：契约以作战地图 indicators 为真源定型——**4 维加权 100 分：目标价空间 40%（消费 L1/L2 基本面）+ 基本面评分 30%（L1/L2 财务）+ 技术趋势 20%（L2-A 因子）+ 流动性 10%（L0 行情）**；降级=基本面数据缺失→跳过机构评分维度，仅技术面。**重评条件**：首批策略回测时按 A 股实际数据校准 4 维权重（40/30/20/10 为经验设定）。
>
> **② BM-SEL-22-B 强庄股识别器（production，MOD-SIG-023 同模块内一支）**：短线选股评分卡的强庄股加分维度，盘前全量+盘中增量触发，输出强庄股标签+置信度喂 BM-SEL-22 评分卡加分。**裁定**：三特征识别规则定型——**走势独立性**（与大盘相关性低于独立性阈值，走势独立=有庄控盘）+ **换手率异常**（换手率偏离常态倍数超阈）+ **盘口神秘大单**（L0 盘口大单识别规则命中），**三特征同时命中**→强庄股标签成立；降级=盘口数据缺失→跳过强庄维度。**重评条件**：独立性阈值/换手率偏离倍数/大单识别规则三项参数待首批策略回测校准。
>
> **③ BM-SEL-25-D PDF 分布信号提取（production，MOD-SIG-035 `extract_pdf_signal`）**：双引擎融合决策（BM-SEL-25）内的分布信号出口——消费条件 PDF（L2-A 密度预测）+ 融合决策分数（BM-SEL-25-A），产出 4 维 PDF 分布信号喂 BM-SEL-21 组合优化。**裁定**：`extract_pdf_signal` 4 维语义定型——**方向**（分布均值/众数给出的多空方向）+ **置信度**（分布集中度/峰度换算的置信水平）+ **尾部风险**（分布左尾分位数，前瞻 VaR 语义）+ **相对价值**（当前价格相对分布中枢的偏离度）；降级=密度预测未就绪→跳过 PDF 信号（当前 [91_density_prediction](91_density_prediction.md) 属远期，本支以融合分数为主输入运行）。**重评条件**：密度预测模型（[91号](91_density_prediction.md)）验证通过后，校准 4 维信号的分布口径与尾部风险阈值。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-23-C | 情绪周期策略映射 | §3.5（情绪周期门控切换：主升/疯狂→打板路径，冰点/反核→反核路径）/ §3.6（第一层 sleeve 内情绪周期仓位上限 5 档规则：冰点 0~极轻/反核 ≤2-3 成/主升 3-5 成/疯狂 2-3 成/退潮 ≤1 成）；阶段→操作规则完整体系见 [28_sentiment_cycle_trading §3.2](28_sentiment_cycle_trading.md) 5 阶段买卖纪律 | production已建 |
| BM-SEL-24-C | 双引擎基准权重配置 | §3.5（基准权重 60/40 游资 60%+量化 40%，5 档情绪周期自适应权重裁定） | production已建 |
| BM-SEL-25-B | 情绪周期自适应权重 | §3.5（裁定：60/40 基准 + 情绪周期自适应 5 档 `determine_adaptive_weights`——冰点量化 70%/主升游资 70%/退潮量化 60% 等） | production已建 |
| BM-SEL-25-C | 6类决策输出 | §3.5（第一层 `classify_decision` 6 类标的分类：主升龙头/二进三/跟风/复苏/伪强/地天反包） | production已建 |
| BM-SEL-25-C-1 / BM-SEL-25-C-2 / BM-SEL-25-C-3 / BM-SEL-25-C-4 / BM-SEL-25-C-5 / BM-SEL-25-C-6 | 六决策类（主升龙头/二进三/跟风/复苏/伪强/地天反包） | §3.5（`classify_decision` 6 类标的分类逐类展开；消歧④区分标的角色 vs 交易动作 7 类映射层） | production已建 |

### 3.6 讨论要点⑥：打板专用风控参数

**裁定**：打板 sleeve 风控分四层——sleeve 内情绪周期仓位上限 + StrategyBook 账户级回撤 Protocol + firm 层 budget 裁剪 + **打板专用瞬时风控**（v1.9.2 补第四层，见 §3.13 缺失#2）。

**第一层：sleeve 内情绪周期仓位上限**：冰点 0~极轻 / 反核 ≤2-3 成 / 主升 3-5 成 / 疯狂 2-3 成（减仓）/ 退潮 ≤1 成（清仓）。

**第二层：StrategyBook 账户级回撤 Protocol**（[30 §2.5]，已 production）：Level 1 警告（回撤>8%，单笔风险降至1.5%）/ Level 2 减仓（>15%，仓位缩至75%）/ Level 3 停仓（>20%）/ Level 4 清仓（>25%）/ 日度熔断（单日亏损>4%）/ 单策略熔断（>5%）/ Kill Switch（单日>6%/回撤>25%/连5亏/流动性危机）。

**第三层：firm 层 budget 三级裁剪**（[30 §2.4]）：Tier 1 封锁新仓 / Tier 2 策略自选砍仓（1-2天收敛）/ Tier 3 按比例裁剪。

**第四层：打板专用瞬时风控**（§3.13 缺失#2，v1.9.2 补）：`DabanInstantCircuitBreaker`——三触发器（封单崩塌30%/梯队断层/量化席位hard 70%）→ 瞬时熔断卖出。与 Kill Switch 并列但优先级更高——Kill Switch 是日度熔断，DabanInstantCircuitBreaker 是盘中瞬时熔断。

**施工状态**：`budget_change_handler.py`（MOD-POS-022）骨架待填充。回撤 Protocol 相关模块（drawdown_controller/tracker/var_calculator/kill_switch）已 production。

### 3.7 讨论要点⑦：T+1 约束下的打板时序

**裁定**：T+1 结算由 `cash_manager.py` 真实实现，打板时序以"打板次日卖出为主，连板晋级者持有至分歧/破板"为核心。

**T+1 结算机制**（`cash_manager.py` POS-06）：买入当日扣减可用；卖出 T+1 结算进 `pending_settlement`，次日释放。`available_cash = total_cash - pending_settlement`。

**打板时序**：T日盘中打板买入→T日收盘持仓不可卖→T+1日开盘竞价观察（高开溢价→卖出；低开闷杀→止损）→T+1日盘中连板晋级者持有→T+2日资金可用。

> **§3.13 缺失#1 补充**：T+1日开盘行仅有定性描述，v1.9.2 补 `next_day_exit_decision()` 完整函数（见 §3.13）。

**2026 程序化交易新规约束**：官方高频认定 ≥300笔/秒 OR ≥20000笔/日（中基协2026-07权威确认）。"15笔/秒"是市场误传。本项目内部限频 ≤15笔/秒（安全垫）+ 撤单率 ≤15% 硬限。`ProgramTradingComplianceGuard` 令牌桶限流+撤单率滚动监控。

**施工状态**：✅ [40号](40_execution_broker.md) v2.6.0 已实现 CancelRateGuard+ProgrammaticTradingGuard。

### 3.8 助攻梯队权重真源裁定（解决 [28 §6] 待裁定项）

**裁定**：**源码 10 分/sum 95 为真源**，battle_map 待修正。6 因子助攻梯队评分：连板梯队健康度 20 + 晋级率 15 + 封单质量 15 + 龙虎榜游资席位 15 + 首封时间 15 + 换手率 15 = 95（差额 5 分为情绪周期阶段加减分）。

### 3.9 竞价三维 100 分打分体系 + 执行纪律（v1.6.0 新增）

**裁定**：集合竞价三维 100 分——大盘 30 分+板块 30 分+个股 40 分。`score_auction_3d` 9:25 集合竞价定格后调用。总分≥80 打板确认，60-80 观望，<60 否决。纸老虎识别 `detect_auction_paper_tiger`（竞价涨幅 7-8% 但匹配量<总量 3%=主力演戏，一票否决，IC 胜率 95%+）。

### 3.10 量化 vs 游资博弈新格局——三次炸板回封模型（v1.7.0 新增）

**裁定**：2026 量化占比 35%，量化 vs 游资博弈新格局需要三次炸板回封模型。第一次炸板→回封（量化止损/游资吸筹，中）；第二次（量化继续出货/游资加仓，低）；第三次（量化大量出货/游资力竭，极低=承接崩塌前兆）。

**Public Trader Identity 量游博弈理论背书**（[arXiv:2608.04373](https://arxiv.org/abs/2608.04373) 2026-08-06 Zhai）：公开交易者身份本身具有信号价值——量化席位占比升高=逆向选择风险升高=收益可预测性下降。为§3.11 `detect_quant_seat_warning` 提供理论背书。

**退潮检测三信号**：①龙头滞涨；②龙虎榜量化席位占比异常升高+知名游资减少；③跟风股无差别破位下跌。

### 3.11 封单结构双指标 + 次日溢价三维预测 + 回封生死线决策 + 量化席位双阈值预警（v1.8.0 新增）

**裁定**：4 个施工算法补全封板质量评估。

**①封单结构双指标**（`score_seal_structure`）：封流比≥5%稳定/<2%薄弱 + 封成比>10稳定/<1不牢。

**②次日溢价三维预测**（`forecast_next_day_premium`）：封板时间×量能×封单→预期溢价区间+操作建议。> **§3.13 缺失#1 补充**：只输出预测不做决策，v1.9.2 补 `next_day_exit_decision()`。

**③回封生死线决策**（`classify_reflush_board`）：15分钟内回封+封单递增=良性；20-30分钟无法回封=承接崩塌。

**④龙虎榜量化席位双阈值预警**（`detect_quant_seat_warning`）：hard 70%降权30%+预警 / soft 58%降权15%。> **§3.13 缺失#5 补充**：无PIT处理边界，v1.9.2 补 `get_dragon_tiger_pit()` as_of_date断言。

### 3.12 跌停板反抽/反核策略（v1.9.0 新增）

**裁定**：涨停端 alpha 衰减背景下跌停端反抽成为辅助 alpha。复用 `dual_engine_fusion` + 23-B 情绪周期门控，纯增量 ~60 行。入场=跌停板打开+冰点/反核阶段+主力净流入转正。止损 3-5%，时间止盈 2-5 日，仓位 ≤2 成。

> **§3.13 缺失#3/#7 补充**：v1.9.2 补第7类 REFLUSH_DIVE 切换门控 + `reflush_next_day_exit_decision()` 二次出场决策。

### 3.13 施工算法 7 项缺失补全（v1.9.2 新增，施工算法完整性深度审查）

> 2026-08-10 施工算法完整性深度审查识别出 7 项缺失（3 高+3 中+1 低）。本节集中补全形式化施工算法，填补"信号识别→情绪定位→打板入场→封板判断→次日出场→风控熔断→容量管理"七大环节断裂点。

#### 缺失#1：次日出场完整决策算法（高优先级，T+1 闭环断裂修复）

```python
@dataclass
class NextDayExitDecision:
    """次日出场完整决策（v1.9.2 补，整合 forecast_next_day_premium + 20号三档退出）"""
    hard_exit_premium_low: float = -0.05    # 低开≥5%→硬止损全卖（核按钮闷杀）
    hard_exit_consecutive_loss: int = 3      # 连续3板未晋级→硬退出
    soft_exit_divergence: float = 0.5        # 分歧度>0.5→软退出
    take_profit_tier1: float = 0.03          # 高开≥3%→竞价卖50%
    take_profit_tier2: float = 0.05          # 高开≥5%→全卖
    max_holding_days: int = 3                # 持仓≥3天未晋级→硬退出

    def decide(self, position: dict, auction_data: dict, forecast: dict, holding_days: int) -> dict:
        open_premium = auction_data['open_price'] / position['cost_basis'] - 1
        if open_premium <= self.hard_exit_premium_low:  # 硬退出①：低开闷杀
            return {'action': 'STOP_LOSS', 'qty_ratio': 1.0, 'reason': f'核按钮闷杀 open={open_premium:.1%}'}
        if holding_days >= self.max_holding_days and not position.get('consecutive_board', False):  # 硬退出②：持仓超时
            return {'action': 'SELL_ALL', 'qty_ratio': 1.0, 'reason': f'持仓{holding_days}天未晋级→时间退出'}
        if position.get('exploded', False) and forecast.get('phase') == '退潮':  # 硬退出③：炸板+退潮
            return {'action': 'SELL_ALL', 'qty_ratio': 1.0, 'reason': '炸板+退潮→硬退出'}
        if open_premium >= self.take_profit_tier2:  # 高开止盈：分批
            return {'action': 'SELL_ALL', 'qty_ratio': 1.0, 'reason': f'高开{open_premium:.1%}≥5%→全卖'}
        if open_premium >= self.take_profit_tier1:
            return {'action': 'SELL_HALF', 'qty_ratio': 0.5, 'reason': f'高开{open_premium:.1%}≥3%→竞价卖50%'}
        if forecast.get('divergence', 0) > self.soft_exit_divergence:  # 软退出：分歧度高
            return {'action': 'SELL_HALF', 'qty_ratio': 0.5, 'reason': f'分歧度>0.5→分批退'}
        if position.get('consecutive_board', False) and open_premium > 0:  # 连板晋级者持有
            return {'action': 'HOLD', 'qty_ratio': 0.0, 'reason': '连板晋级+高开→持有'}
        return {'action': 'HOLD', 'qty_ratio': 0.0, 'reason': '等盘中确认'}

    @staticmethod
    def classify_position_status(position: dict, t1_data: dict, echelon_status: str) -> dict:
        """持仓状态分类（v1.9.6 补，填充 consecutive_board/exploded 字段——decide() 依赖此两字段，此前无填充算法，本方法补全断裂点）。
        连板晋级判断：T+1日涨停收盘+封单存在+梯队非孤板（与 §3.1 classify_echelon_health 联动）；炸板判断：T日封板后 T+1日盘中打开（封单崩塌或价格跌破涨停价，与 §3.13#2 DabanInstantCircuitBreaker 联动——炸板触发瞬时风控）。"""
        t1_close = t1_data.get('close', 0)
        t1_high = t1_data.get('high', 0)
        limit_up_price = t1_data.get('limit_up_price', 0)
        t1_seal_ratio = t1_data.get('seal_ratio', 0)  # T+1日封流比（0=无封单）
        # ① 连板晋级：T+1日收盘涨停 + 封单存在 + 梯队非孤板
        is_limit_up_close = (limit_up_price > 0 and abs(t1_close - limit_up_price) < 0.01)
        has_seal = t1_seal_ratio > 0.001  # 封流比>0.1%
        is_in_echelon = echelon_status not in ('LONE_DRAGON', 'COLLAPSE')
        consecutive_board = is_limit_up_close and has_seal and is_in_echelon
        # ② 炸板：T日封板后 T+1日盘中触及涨停但未封住（最高价=涨停价但收盘<涨停价）或 T+1日封单崩塌（DabanInstantCircuitBreaker 触发后标记）
        touched_limit = (limit_up_price > 0 and t1_high >= limit_up_price * 0.999)
        not_sealed_close = not is_limit_up_close
        exploded = touched_limit and not_sealed_close
        position['consecutive_board'] = consecutive_board
        position['exploded'] = exploded
        return {'consecutive_board': consecutive_board, 'exploded': exploded,
                'reason': (f'连板晋级={consecutive_board}（涨停收盘={is_limit_up_close}+封单={has_seal}+梯队={is_in_echelon}），'
                           f'炸板={exploded}（触涨停={touched_limit}+未封收={not_sealed_close}）')}
```

#### 缺失#2：打板专用瞬时风控（高优先级，盘中瞬时熔断缺失）

```python
@dataclass
class DabanInstantCircuitBreaker:
    """打板专用瞬时风控（v1.9.2 补，三触发器→瞬时熔断卖出）。与 §3.6 Kill Switch 并列——Kill Switch 是账户级日度熔断，本类是 sleeve 级盘中瞬时熔断。
    理论背书：arXiv:2608.03616 liquidation cascade 亚临界分支——封单崩塌时止损触发更多止损，需在级联扩散前卖出。"""
    seal_collapse_threshold: float = 0.30    # 封单瞬间消失30%即熔断
    echelon_fracture_actions = {'FRACTURE', 'LONE_DRAGON', 'COLLAPSE'}
    quant_seat_hard_threshold: float = 0.70  # 量化席位买入占比>70%

    def check_instant_break(self, position: dict, live_data: dict, echelon_status: str, quant_seat_ratio: float) -> dict:
        seal_ratio = live_data.get('current_seal', 0) / max(live_data.get('initial_seal', 1), 1)
        if seal_ratio < (1 - self.seal_collapse_threshold):  # 触发器①：封单崩塌
            return {'trigger': 'SEAL_COLLAPSE', 'action': 'INSTANT_SELL', 'qty_ratio': 1.0, 'reason': f'封单崩塌{(1-seal_ratio):.0%}≥30%→瞬时熔断'}
        if echelon_status in self.echelon_fracture_actions:  # 触发器②：梯队断层
            return {'trigger': 'ECHELON_FRACTURE', 'action': 'INSTANT_SELL', 'qty_ratio': 1.0, 'reason': f'梯队{echelon_status}→瞬时熔断清仓'}
        if quant_seat_ratio > self.quant_seat_hard_threshold:  # 触发器③：量化席位hard预警
            return {'trigger': 'QUANT_SEAT_HARD', 'action': 'INSTANT_SELL', 'qty_ratio': 1.0, 'reason': f'量化席位{quant_seat_ratio:.0%}>70%→瞬时熔断'}
        return {'trigger': None, 'action': 'MONITOR'}
```

#### 缺失#3：打板 vs 反核切换门控（中优先级，第7类决策）

```python
def classify_decision_v192(emotion_score: float, tech_score: float, phase: str, is_limit_down_rebound: bool = False) -> str:
    """双引擎融合 7 类决策（v1.9.2 补第7类 REFLUSH_DIVE + 情绪周期门控切换）——§3.5 INVERSE_BOARD 是"地天反包"非"反核"，§3.12 反核无显式切换逻辑，本函数补全"""
    if phase in ('冰点', '反核') and is_limit_down_rebound:  # 情绪周期门控：冰点/反核→反核路径
        if emotion_score >= 40 and tech_score >= 60:
            return 'REFLUSH_DIVE'  # 反核入场
        return 'WAIT'
    # 打板路径（主升/疯狂期，原6类不变）
    threshold = PHASE_THRESHOLDS[phase]
    if emotion_score >= threshold and tech_score >= 60:
        return 'BOARD' if phase in ('主升', '疯狂') else 'WATCH'
    elif emotion_score >= threshold * 0.8 and tech_score >= 70:
        return 'CONTINUE'
    elif emotion_score >= 60 and tech_score >= 75:
        return 'INVERSE_BOARD'
    elif emotion_score >= 40 and tech_score >= 50:
        return 'WATCH'
    elif emotion_score < 20:
        return 'WAIT'
    else:
        return 'REJECT'
```

#### 缺失#4：分笔建仓算法（中优先级，容量管理执行层）

**v1.9.3 理论升级**：原 v1.9.2 用启发式 queue_decay_rate=0.15，v1.9.3 接入 [arXiv:2607.28323](https://arxiv.org/abs/2607.28323)（Barzykin 2026-07-30 Passive Market Impact）的理论框架——限价单填充概率随距 midprice 距离指数衰减 `λ(d)=λ₀·exp(-κd)`，价格对订单流不平衡的短期响应线性 `ΔP = η·OFI`。该框架在 NASDAQ+FX 实证校准，A 股涨停板场景可直接套用（涨停板=极限距 midprice 场景）。同时整合 [arXiv:2603.09164](https://arxiv.org/abs/2603.09164)（SaR Slippage-at-Risk）的前瞻性流动性风险度量——在分笔建仓前先用 SaR 评估当前订单簿可承受的冲击量。

```python
@dataclass
class DabanExecutionAlgorithm:
    """打板分笔建仓（v1.9.2 补，v1.9.3 升级 passive impact 理论背书，v1.9.5 补 Hawkes 长记忆核，v1.9.7 补扩散价格动力学悖论）。依赖 G22 执行层。
    理论背书：arXiv:2608.00885 微结构均值回归最优执行（v1.9.2 原引）/ arXiv:2607.28323 Passive Market Impact 指数填充概率衰减（v1.9.3）/ arXiv:2603.09164 SaR 前瞻性流动性风险（v1.9.3）/ arXiv:2608.02002 Hawkes 长记忆核 Volterra-Riccati 近似——封单增减是自激励点过程（封单吸引更多封单），一般 Hawkes 核建模封单队列爆发与衰减，补充指数核的长记忆衰减（v1.9.5）/ arXiv:2608.00988 扩散价格动力学悖论精确可解模型——平方根冲击律+Lévy-walk 框架，严格证明可预测订单流下价格仍扩散（拆单不泄露信息），为批量入场拆单提供理论依据（v1.9.7）"""
    # v1.9.3 升级：从启发式 0.15 改为理论校准的指数衰减率
    fill_decay_kappa: float = 0.20       # 填充概率指数衰减率（被动 impact 校准）
    fill_base_lambda: float = 1.0        # 基础填充强度（涨停板=封单强，基础高）
    price_impact_eta: float = 0.001      # 线性响应系数（OFI→ΔP）
    sar_alpha: float = 0.95              # SaR 分位数（95% 滑点风险）
    first_batch_ratio: float = 0.6       # 封板瞬间首批60%
    reflush_batch_ratio: float = 0.3     # 回封补量30%
    cancel_timeout_sec: int = 30         # 30秒未成交考虑撤单

    def estimate_fill_probability(self, queue_position: int, seal_volume: int, order_volume: int, distance_to_mid: float = 0.0) -> float:
        """v1.9.3 升级：指数填充概率衰减（passive impact 理论）"""
        base_prob = min(seal_volume / max(order_volume * 10, 1), 1.0)  # 基础填充强度（封单量/订单量比）
        distance_decay = math.exp(-self.fill_decay_kappa * distance_to_mid)  # v1.9.3: 距 midprice 指数衰减（涨停板 distance_to_mid≈涨停幅度）
        position_decay = (1 - 0.15) ** queue_position  # 队列位置衰减（保留 v1.9.2 启发式，作为补充）
        return base_prob * distance_decay * position_decay

    def estimate_sar(self, order_book: dict, order_volume: int) -> float:
        """v1.9.3 新增：Slippage-at-Risk 前瞻性滑点评估——SaR(α)=模拟订单簿吸收 order_volume 的滑点分位数；简化版用订单簿深度+集中度估算，集中度高→脆弱流动性→SaR 大"""
        depth = sum(level['volume'] for level in order_book.get('bid_levels', [])[:5])
        concentration = max(level['volume'] for level in order_book.get('bid_levels', [])) / max(depth, 1)
        return (order_volume / max(depth, 1)) * (1 + concentration) * self.price_impact_eta

    def build_execution_plan(self, target_volume: int, seal_volume: int, queue_position: int, order_book: dict = None) -> list[dict]:
        plan = []
        if order_book:  # v1.9.3: 前置 SaR 检查——若 SaR 超阈值则削减 target_volume
            sar = self.estimate_sar(order_book, target_volume)
            if sar > 0.02:  # 滑点>2% 削减
                target_volume = int(target_volume * 0.7)
                plan.append({'batch': 'SAR_TRIM', 'qty': target_volume, 'reason': f'SaR={sar:.3f}>2%→削30%'})
        first_qty = int(target_volume * self.first_batch_ratio)
        plan.append({'batch': 'FIRST', 'qty': first_qty, 'timing': 'SEAL_INSTANT',
                     'fill_prob': self.estimate_fill_probability(queue_position, seal_volume, first_qty)})
        reflush_qty = int(target_volume * self.reflush_batch_ratio)
        plan.append({'batch': 'REFLUSH', 'qty': reflush_qty, 'timing': 'RESEAL',
                     'fill_prob': self.estimate_fill_probability(queue_position + 5, seal_volume, reflush_qty)})
        reserve_qty = target_volume - first_qty - reflush_qty
        plan.append({'batch': 'RESERVE', 'qty': reserve_qty, 'timing': 'OPPORTUNISTIC', 'fill_prob': 0.3})
        return plan
```

#### 缺失#5：龙虎榜 PIT 处理（高优先级，未来函数致命缺陷修复）

```python
def get_dragon_tiger_pit(symbol: str, as_of_date: date, db_session) -> list[dict]:
    """龙虎榜PIT安全查询（v1.9.2 补，as_of_date 边界断言）——龙虎榜盘后17:00公布，T日盘中决策若用T日龙虎榜=未来函数=回测虚高+实盘失效，只能用T-1日及之前龙虎榜"""
    latest_available = as_of_date - timedelta(days=1)
    rows = db_session.execute(
        "SELECT * FROM dragon_tiger WHERE symbol = :symbol AND trade_date <= :latest "
        "ORDER BY trade_date DESC LIMIT 5",
        {'symbol': symbol, 'latest': latest_available}
    ).fetchall()
    for row in rows:  # PIT断言
        assert row.trade_date < as_of_date, \
            f"PIT VIOLATION: dragon_tiger trade_date={row.trade_date} >= as_of_date={as_of_date}"
    return [dict(row) for row in rows]
```

**施工建议**：在 `youzi_relay_emotion_engine.py` 的 `score_youzi_relay` 和 `detect_quant_seat_warning` 增加 `as_of_date` 参数+PIT断言。**首批策略实盘前必须修复**。

#### 缺失#6：CUSUM 信号失效监控（中优先级，信号质量持续监控）

**v1.9.3 理论升级**：原 v1.9.2 用 CUSUM+PSI 双检测器，但 [arXiv:2607.27070](https://arxiv.org/abs/2607.27070)（Seuma 2026-07-29 7-event cascade study）证明 critical slowing down 仅在 5/7 内生级联有效，2/7 外生冲击（政策/新闻）无前置信号——**单一指标无法跨所有事件预警**。唯一跨 6/7 事件的规律：级联前 taker buy/sell ratio 方差压缩（"安静的市场订单波动"）。v1.9.3 据此新增方差压缩检测器+two-type classification（内生 vs 外生），CUSUM 保留用于内生型，方差压缩用于外生型兜底。同时整合 [arXiv:2604.20949](https://arxiv.org/abs/2604.20949)（Hiremath 2026-04 Latent Microstructure Regime）的 trigger-based detector——三态因果 DGP（stable→latent build-up→stress）+ MAX 聚合 + rising-edge + 自适应阈值，平均领先 +18.6 步且 precision=1.0。

```python
@dataclass
class SignalDecayMonitor:
    """打板信号失效监控（v1.9.2 补 CUSUM+PSI，v1.9.3 升级 two-type classification+方差压缩+latent regime）。分级响应：OK→REDUCE→STOP。
    参考：mathandmarkets 2026-02 CUSUM（k=0.5σ/h=4σ）——内生型级联 / stockalpha.ai 2026-02 Concept Drift（分级响应）/ arXiv:2607.27070 7-event cascade：critical slowing down 仅 5/7 有效，方差压缩跨 6/7（v1.9.3）/ arXiv:2604.20949 latent microstructure regime：三态 DGP+trigger detector，领先 +18.6 步（v1.9.3）"""
    cusum_k: float = 0.5       # 偏移容差（0.5σ）——内生型
    cusum_h: float = 4.0       # 触发阈值（4σ）
    cusum_S: float = 0.0       # 累积和
    psi_alert: float = 0.1     # 轻微漂移
    psi_critical: float = 0.25 # 严重漂移
    variance_compression_threshold: float = 0.6  # v1.9.3 新增：方差压缩至历史 60% 触发预警（外生型兜底）
    variance_window: deque = field(default_factory=lambda: deque(maxlen=60))
    baseline_window: deque = field(default_factory=lambda: deque(maxlen=30))
    cascade_type: str = 'UNKNOWN'  # v1.9.3 新增：two-type classification——ENDOGENOUS / EXOGENOUS / UNKNOWN

    def update(self, win: bool, premium: float, taker_bs_ratio_var: float = None) -> dict:
        self.baseline_window.append(premium)
        mu, sigma = 0.55, 0.5
        self.cusum_S = max(0, self.cusum_S + ((1.0 if win else 0.0) - mu - self.cusum_k * sigma))  # CUSUM：监控胜率累积偏移（内生型）
        if self.cusum_S > self.cusum_h * sigma:
            self.cascade_type = 'ENDOGENOUS'
            return {'level': 'REDUCE', 'type': 'ENDOGENOUS', 'reason': f'CUSUM={self.cusum_S/sigma:.1f}σ>4σ→仓位减半'}
        if taker_bs_ratio_var is not None and len(self.variance_window) >= 30:  # v1.9.3 新增：方差压缩检测器（外生型兜底，跨 6/7 事件）
            self.variance_window.append(taker_bs_ratio_var)
            hist_var = np.var(list(self.variance_window)[:-10])
            curr_var = np.var(list(self.variance_window)[-10:])
            if curr_var < hist_var * self.variance_compression_threshold:
                self.cascade_type = 'EXOGENOUS'
                return {'level': 'REDUCE', 'type': 'EXOGENOUS', 'reason': f'方差压缩{curr_var/hist_var:.0%}<60%→外生冲击预警+仓位减半'}
        if len(self.baseline_window) >= 30:  # PSI：监控次日溢价分布漂移
            psi = self._compute_psi()
            if psi > self.psi_critical:
                return {'level': 'STOP', 'reason': f'PSI={psi:.2f}>0.25→停止打板+重新校准'}
            elif psi > self.psi_alert:
                return {'level': 'REDUCE', 'reason': f'PSI={psi:.2f}>0.1→仓位减半'}
        return {'level': 'OK', 'reason': '信号质量正常'}
```

#### 缺失#7：反核二次出场决策算法（低优先级，Phase 5 候选）

```python
def reflush_next_day_exit_decision(position: dict, auction_data: dict, holding_days: int) -> dict:
    """反核二次出场决策（v1.9.2 补，Phase 5 候选）——§3.12 有静态出场参数但缺反核后次日不同走势的分别出场决策，本函数补全"""
    open_premium = auction_data['open_price'] / position['cost_basis'] - 1
    if open_premium >= 0.05:
        return {'action': 'SELL_ALL', 'qty_ratio': 1.0, 'reason': f'反核后高开≥5%→止盈'}
    if -0.03 < open_premium < 0.05:
        if holding_days >= 5:
            return {'action': 'SELL_ALL', 'qty_ratio': 1.0, 'reason': '反核持有5天→时间止盈'}
        return {'action': 'HOLD', 'qty_ratio': 0.0, 'reason': '低开>-3%→观察等反抽'}
    if open_premium <= -0.03:
        return {'action': 'STOP_LOSS', 'qty_ratio': 1.0, 'reason': f'低开≤-3%→止损'}
    if auction_data.get('is_limit_down', False):
        return {'action': 'HOLD', 'qty_ratio': 0.0, 'reason': '继续跌停→持有等反抽'}
    return {'action': 'HOLD', 'qty_ratio': 0.0, 'reason': '观察'}
```

### 3.14 施工算法第三轮深度审查补全（v1.9.3 新增，5 项缺口）

> 2026-08-10 第三轮施工算法深度审查 + 8 月 8-10 日 arXiv 最新研究整合。v1.9.2 的 7 项补全覆盖了"信号识别→情绪定位→打板入场→封板判断→次日出场→风控熔断→容量管理"七大环节的**显式断裂点**，但第三轮审查发现七环节之间仍存在 5 项**隐式断裂点**——前置质量评估、持仓期间监控、回测 PIT 框架、打板时点决策、容量动态测算。本节集中补全。

#### 缺失#8：打板信号前置质量评估算法（高优先级，信号识别→情绪定位断裂点）

**断裂点**：§3.1 连板梯队识别后直接跳到 §3.2 情绪周期定位，缺少"当前连板梯队是否值得打板"的前置质量评估门控——低质量梯队（孤板/断层）即使情绪周期在主升期也不应打板。

```python
def pre_validate_daban_signal(echelon_health: str, echelon_height: int, sector_resonance: float, follow_count: int) -> dict:
    """打板信号前置质量评估（v1.9.3 补，梯队质量→yes/no门控），在 §3.2 情绪周期定位器之前调用。
    理论背书：arXiv:2607.27063 羊群 agent-based 模型——信息扩散+社会强化分离机制下，无梯队跟风的孤板属于"信息扩散不充分"，超调反转概率高。"""
    score = 0
    reasons = []
    health_scores = {'PERFECT': 40, 'FRACTURE': 15, 'LONE_DRAGON': 5, 'COLLAPSE': 0}  # 梯队健康度权重 40
    score += health_scores.get(echelon_health, 0)
    if echelon_health in ('LONE_DRAGON', 'COLLAPSE'):
        reasons.append(f'梯队{echelon_health}→质量极低')
    # 连板高度权重 20（2板最优，>5板风险递增）
    if echelon_height == 2:
        score += 20
    elif echelon_height == 1:
        score += 10
    elif 3 <= echelon_height <= 4:
        score += 15
    else:
        score += 5
        reasons.append(f'{echelon_height}板高度风险')
    score += int(sector_resonance * 20)  # 板块共振权重 20（板块跟风度）
    if sector_resonance < 0.3:
        reasons.append('板块共振不足→孤板风险')
    score += min(follow_count * 4, 20)  # 跟风股数量权重 20
    if follow_count < 3:
        reasons.append(f'跟风股{follow_count}只<3→梯队单薄')
    # 门控决策
    if score >= 70:
        return {'pass': True, 'score': score, 'reason': '梯队质量合格→进入情绪周期定位'}
    elif score >= 50:
        return {'pass': 'CONDITIONAL', 'score': score, 'reason': f'梯队质量中等({";".join(reasons)})→降仓50%'}
    else:
        return {'pass': False, 'score': score, 'reason': f'梯队质量不合格({";".join(reasons)})→否决打板'}
```

#### 缺失#9：持仓期间微结构监控算法（高优先级，封板判断→次日出场断裂点）

**断裂点**：§3.11 封板判断在 T 日盘中封板瞬间，§3.13#1 NextDayExitDecision 在 T+1 日开盘，中间 T 日封板后到收盘的持仓期间持续监控缺失（§3.13#2 是瞬时熔断，非持续监控）。

```python
@dataclass
class HoldingPeriodMicrostructureMonitor:
    """持仓期间微结构监控（v1.9.3 补，封板后→收盘持续监控）。与 §3.13#2 DabanInstantCircuitBreaker 互补——后者是瞬时熔断，本类是持续监控+渐进降仓。
    理论背书：arXiv:2604.20949 latent regime 三态 DGP（stable→latent build-up→stress）+trigger detector 领先 +18.6 步 / arXiv:2603.09164 SaR 前瞻性滑点——封板后订单簿微结构变化可提前预警封单崩塌。"""
    sar_threshold_alert: float = 0.01    # SaR>1% 预警
    sar_threshold_reduce: float = 0.02   # SaR>2% 降仓
    ofi_window: deque = field(default_factory=lambda: deque(maxlen=20))
    latent_buildup_detected: bool = False

    def monitor(self, position: dict, order_book: dict, seal_data: dict) -> dict:
        depth = sum(l['volume'] for l in order_book.get('bid_levels', [])[:5])  # ① SaR 前瞻性滑点评估
        concentration = max(l['volume'] for l in order_book.get('bid_levels', [])) / max(depth, 1)
        sar = (position['qty'] / max(depth, 1)) * (1 + concentration) * 0.001
        ofi = order_book.get('ofi', 0)  # ② 订单流不平衡（OFI）latent build-up 检测
        self.ofi_window.append(ofi)
        if len(self.ofi_window) >= 10:
            ofi_trend = np.mean(list(self.ofi_window)[-5:]) - np.mean(list(self.ofi_window)[:-5])
            if ofi_trend < -0.3:  # OFI 持续下降=latent build-up
                self.latent_buildup_detected = True
        seal_ratio = seal_data.get('current', 0) / max(seal_data.get('initial', 1), 1)  # ③ 封单持续监控
        if sar > self.sar_threshold_reduce or (self.latent_buildup_detected and seal_ratio < 0.5):  # 分级响应
            return {'action': 'REDUCE_50', 'reason': f'SaR={sar:.3f}>2%或latent+封单<50%→降仓50%'}
        if sar > self.sar_threshold_alert or self.latent_buildup_detected:
            return {'action': 'ALERT', 'reason': f'SaR={sar:.3f}>1%或latent build-up→预警'}
        if seal_ratio < 0.7:
            return {'action': 'ALERT', 'reason': f'封单剩余{seal_ratio:.0%}<70%→监控'}
        return {'action': 'MONITOR', 'reason': '持仓微结构正常'}
```

#### 缺失#10：PIT 安全回测框架算法（高优先级，回测验证基础设施）

**断裂点**：§3.13#5 仅处理龙虎榜 PIT，情绪周期评分、连板梯队、封单数据等其他数据源的 PIT 安全回测框架缺失。

```python
class DabanPITBacktestFramework:
    """打板 PIT 安全回测框架（v1.9.3 补，全数据源 PIT 断言，扩展 §3.13#5 龙虎榜 PIT 到全数据源）。
    理论背书：北大 Jiang & Li 理性预期模型——打板 alpha 来自信息未完全纳入，回测必须严格 PIT 否则虚高（PIT 违规=虚高 alpha）。"""
    PIT_RULES = {
        'dragon_tiger': {'publish_time': 'T日17:00', 'available_for': 'T+1日盘中'},  # §3.13#5
        'emotion_cycle_score': {'publish_time': '实时计算', 'available_for': 'T日盘中'},  # 当日实时可用
        'echelon_data': {'publish_time': '实时', 'available_for': 'T日盘中'},  # 连板梯队实时
        'seal_data': {'publish_time': '实时', 'available_for': 'T日盘中'},  # 封单实时
        'next_day_auction': {'publish_time': 'T+1日9:25', 'available_for': 'T+1日9:25后'},  # 次日竞价
        'news_sentiment': {'publish_time': '实时', 'available_for': 'T日盘中'},  # 新闻实时
    }

    @staticmethod
    def assert_pit(data_source: str, data_date: date, decision_date: date) -> None:
        """PIT 断言（v1.9.3 补，全数据源）"""
        rule = DabanPITBacktestFramework.PIT_RULES.get(data_source)
        if not rule:
            return
        if data_source == 'dragon_tiger':  # 龙虎榜：决策日只能用 T-1 日及之前
            assert data_date < decision_date, \
                f"PIT VIOLATION: dragon_tiger {data_date} >= decision {decision_date}"
        if data_source == 'next_day_auction':  # 次日竞价：决策日 T+1 只能用 T+1 日 9:25 后数据
            assert data_date <= decision_date, \
                f"PIT VIOLATION: next_day_auction {data_date} > decision {decision_date}"

    def run_backtest(self, strategy_config: dict, start: date, end: date) -> dict:
        """PIT 安全回测主循环（v1.9.3 补）"""
        results = []
        for decision_date in self._trading_days(start, end):
            dragon_tiger = self._load('dragon_tiger', decision_date)  # ① 数据加载+PIT 断言
            self.assert_pit('dragon_tiger', dragon_tiger['date'], decision_date)
            emotion = self._load('emotion_cycle_score', decision_date)
            echelon = self._load('echelon_data', decision_date)
            pre_val = pre_validate_daban_signal(  # ② 前置质量评估（§3.14 缺失#8）
                echelon['health'], echelon['height'], echelon['sector_resonance'], echelon['follow_count'])
            if not pre_val['pass']:
                continue
            phase = emotion['phase']  # ③ 情绪周期定位（§3.2）
            if phase in ('退潮',) and not pre_val['pass'] == True:
                continue
            decision = classify_decision_v192(emotion['score'], echelon['tech_score'], phase)  # ④ 双引擎决策（§3.5）
            if decision not in ('BOARD', 'CONTINUE'):
                continue
            next_day = self._next_trading_day(decision_date)  # ⑤ 次日出场（§3.13#1）
            auction = self._load('next_day_auction', next_day)
            self.assert_pit('next_day_auction', auction['date'], next_day)
            exit_dec = NextDayExitDecision().decide(
                {'cost_basis': echelon['price']}, auction, emotion, holding_days=1)
            results.append({'date': decision_date, 'decision': decision, 'exit': exit_dec})
        return self._summarize(results)
```

#### 缺失#11：打板时点决策算法（中优先级，入场→封板判断断裂点）

**断裂点**：§3.5 双引擎决策输出 BOARD 后的具体下单时点缺失——封板瞬间追板（aggressive）vs 板前埋伏（passive）；§3.9 竞价三维只管 9:25 集合竞价。

```python
@dataclass
class DabanTimingDecision:
    """打板时点决策（v1.9.3 补，追板 vs 埋伏权衡）。理论背书：arXiv:2607.28323 passive impact——涨停板=极限距 midprice，追板=市价单确定性高但冲击大，埋伏=限价单成本低但填充概率低，需在"追板成交概率"vs"板前埋伏等待时间"间权衡。"""
    chase_threshold: float = 0.85       # 封板概率>85%→追板（市价单）
    ambush_threshold: float = 0.50      # 封板概率50-85%→板前埋伏（限价单）
    max_ambush_wait_sec: int = 120      # 埋伏最长等待120秒
    seal_strength_required: float = 0.05  # 封流比>5%才追板

    def decide_timing(self, near_limit: bool, seal_strength: float, volume_surge: float, time_to_close_min: int) -> dict:
        """打板时点决策（v1.9.3 补）"""
        seal_prob = self._estimate_seal_probability(near_limit, seal_strength, volume_surge)  # 封板概率估算
        if seal_prob >= self.chase_threshold and seal_strength >= self.seal_strength_required:
            return {'action': 'CHASE', 'order_type': 'MARKET',
                    'reason': f'封板概率{seal_prob:.0%}>85%+封流比{seal_strength:.1%}>5%→追板'}
        if seal_prob >= self.ambush_threshold:
            return {'action': 'AMBUSH', 'order_type': 'LIMIT', 'limit_price': '涨停价-0.01',
                    'max_wait': self.max_ambush_wait_sec,
                    'reason': f'封板概率{seal_prob:.0%}50-85%→板前埋伏'}
        if time_to_close_min < 30 and seal_prob < self.ambush_threshold:
            return {'action': 'WAIT', 'reason': f'封板概率{seal_prob:.0%}<50%+临近收盘→观望'}
        return {'action': 'WAIT', 'reason': f'封板概率{seal_prob:.0%}<50%→观望'}

    def _estimate_seal_probability(self, near_limit, seal_strength, volume_surge):
        # 简化概率模型
        prob = 0.5
        if near_limit: prob += 0.2
        prob += min(seal_strength * 5, 0.2)
        prob += min(volume_surge * 0.1, 0.15)
        return min(prob, 0.95)
```

#### 缺失#12：容量动态测算算法（中优先级，容量管理执行层）

**断裂点**：§3.4 13 约束链都是静态阈值，缺少基于实时流动性（封单量、委买队列、换手率）动态测算可下仓量的算法（§3.13#4 分笔建仓的前置"可下多少仓"测算）。

```python
@dataclass
class DynamicCapacityCalculator:
    """打板容量动态测算（v1.9.3 补，实时流动性→可下仓量）。理论背书：arXiv:2603.09164 SaR——SaR 直接映射容量上限。与 §3.4 13 约束链（静态阈值）互补——本类提供动态测算。"""
    max_sar_tolerance: float = 0.015        # SaR 容忍度 1.5%
    max_seal_ratio: float = 0.10            # 单票不超过封单量 10%
    max_float_turnover: float = 0.02        # 单票不超过流通盘 2%
    nav_ratio_cap: float = 0.05             # C12 单票 ≤5% NAV

    def calculate(self, nav: float, seal_volume: int, float_shares: int, order_book: dict, price: float) -> dict:
        """动态测算可下仓量（v1.9.3 补）"""
        # ① SaR 约束——滑点风险反推容量：SaR(q) = (q/depth)*(1+concentration)*eta <= max_sar_tolerance → q <= max_sar_tolerance*depth / ((1+concentration)*eta)
        depth = sum(l['volume'] for l in order_book.get('bid_levels', [])[:5])
        concentration = max(l['volume'] for l in order_book.get('bid_levels', [])) / max(depth, 1)
        eta = 0.001
        sar_capacity = int(self.max_sar_tolerance * depth / max((1 + concentration) * eta, 0.001))
        seal_capacity = int(seal_volume * self.max_seal_ratio)  # ② 封单量约束
        float_capacity = int(float_shares * self.max_float_turnover)  # ③ 流通盘约束
        nav_capacity = int(nav * self.nav_ratio_cap / price)  # ④ NAV 约束（C12）
        capacities = {'sar': sar_capacity, 'seal': seal_capacity, 'float': float_capacity, 'nav': nav_capacity}  # 取最小值
        binding = min(capacities, key=capacities.get)
        return {'max_qty': capacities[binding], 'binding_constraint': binding, 'all_constraints': capacities,
                'reason': f'binding={binding}({capacities[binding]})→可下{capacities[binding]}股'}
```

## 4. 考虑过的替代方案

### 4.1 过度工程审查：7 维评分卡 + 6 因子 + 6 维强度是否维度过多

**裁定**：不过度工程。19 维通过三引擎共振 AND 逻辑降维，非加法堆叠。**辛普森悖论警示**（华安证券 2026-03，32,615 样本，年化 18.21%）：单因子有效≠多因子组合有效。首批策略回测时做多因子联合检验。

### 4.2 替代方案：单引擎 vs 双引擎

| 方案 | 结论 |
|---|---|
| 单引擎（纯情绪） | 不采用——情绪信号噪声大 |
| **双引擎（情绪+技术）** | **采用**——互验降噪 |
| 三引擎（+资金） | §3.3 三引擎共振用于龙头识别，非全量打板 |

### 4.3 替代方案：情绪周期阶段数

**采用 4+1 阶段**（冰点捕捉+退潮条件触发），3 阶段粒度不够，6+阶段过拟合风险。

## 5. 上限定义

### 5.1 系统上限

| 维度 | 上限 | 依据 |
|---|---|---|
| 单票仓位 | ≤5% NAV（C12） | `position_sizing_engine.py` |
| sleeve 容量 | 50-200 万（待校准） | [20 §2.2] + 流动性约束 |
| 持仓周期 | 1-3 天 | T+1 约束 + 情绪周期 |
| 并发持仓数 | ≤10 只 | 小账本约束 |
| 回撤上限 | 25% 清仓（Level 4） | [30 §2.5] |
| 单日亏损上限 | 4% 组合 / 5% 单策略 / 6% Kill Switch | [30 §2.5] |

### 5.2 演进路径

- **Phase 1（当前，production）**：7 维评分卡 + 6 因子情绪 + 6 维强度 + 双引擎融合
- **Phase 2（回测微调+合规增强）**：情绪周期准确率回测 + 助攻梯队权重修正 + 涨停时间分层 + 换手率黄金标准 + ✅程序化新规合规层（40号v2.6.0已闭合）+ 中位股死亡池 + 梯队健康度四档 + 量化接力阈值矩阵
- **Phase 3（容量校准+分笔建仓）**：sleeve 容量校准 + convergence_window 实测 + 分笔建仓算法（§3.13 缺失#4，依赖G22）+ 容量动态测算（§3.14 缺失#12，SaR 反推容量上限）
- **Phase 4（最终升级）**：模型学权重（参考 fibalgo 47 特征路线）
- **Phase 5（跌停端反抽+ML破板预测+量游共振协同）**：跌停板反抽/反核（§3.12+§3.13缺失#3/#7）+ CatBoost Tick 级破板预测 ML + 量游共振协同视角 + Level2 订单簿不平衡封单分析（§3.11 封单双指标升级路径）+ **v1.9.4 补**：Siamese LOB 架构（[arXiv:2505.22678](https://arxiv.org/abs/2505.22678) Yang et al. 2025，A 股 14 军工股实证，利用 ask-bid 对称性+MHA-LSTM，超 75% 基线提升）+ Du 开盘信号分布混合模型（[arXiv:2506.06356](https://arxiv.org/abs/2506.06356) Du 2026 USTC，A 股 5 模块框架 15.2% 年化/Sharpe 1.87，开盘竞价 mixture model 识别套利+市值流动性动态仓位+grid-search 止盈止损）+ **v1.9.5 补**：QFCQT 混沌门控 Quantformer（[arXiv:2608.07363](https://arxiv.org/abs/2608.07363) Lin et al. 2026-08-07，Lee 振荡器激活模块+平滑-混沌门控融合，8 族 Lee 振荡器软叠加，A 股股指直接测试，高波动场景 ETTh2 MSE 相对 HAT 提升 43.9%，适合情绪周期冰点→主升→退潮突变检测，远期 ML 架构候选）+ **v1.9.7 补**：速度域签名封板真伪判断（[arXiv:2608.05373](https://arxiv.org/abs/2608.05373) Chen & Hybinette 2026-08-05，速度而非水平域检测 pump-and-crash 模式，price velocity 签名区分"真封板"vs"诱多封"，HMM regime 条件检测+SHAP 可解释归因，印度 BANKNIFTY 10/10 操纵日恢复+AUC=0.91。A 股连板炸板率 70% 环境下速度签名比传统封单量/换手率水平指标更鲁棒，填补"盘中封板质量实时评估"缺口。负面结果启示：HMM regime 用于条件检测是用召回率换精确率，单纯状态划分不够需结合速度签名条件触发）
- **Phase 6（v1.9.3 新增：施工算法深度补全+微结构升级）**：打板信号前置质量评估（§3.14 缺失#8）+ 持仓期间微结构监控（§3.14 缺失#9，latent regime+SaR）+ PIT 安全回测框架（§3.14 缺失#10）+ 打板时点决策（§3.14 缺失#11，追板vs埋伏）+ §3.13#4 DabanExecution 升级 passive impact 指数填充概率 + §3.13#6 SignalDecayMonitor 升级 two-type classification+方差压缩检测器

### 5.3 为何是上限

打板容量上限由 A 股连板标的流动性决定（大资金进场即冲击成本爆炸）。持仓周期上限由 T+1 + 情绪周期退潮检测决定。回撤上限取行业基准下限因打板波动远大于多因子。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| 情绪周期定位器准确率回测 | production 跑但未做历史准确率评估 | G07 + [30 §6.3] 施工前必做 |
| 打板×事件驱动相关性实测 | 退潮期相关性可能飙升 | G07 施工前必做（[28 §3.5]） |
| sleeve 容量精确测算 | 当前为估算值 | 首批策略实盘后校准 |
| 助攻梯队权重 battle_map 修正 | 源码10分/battle_map 15分 | reconciler fix-in-place |
| `budget_change_handler.py` 填充 | 骨架待填充 | 首批 pipeline 就绪后施工 |
| 涨停时间分层量化 | 22-C 封板时间未按时段分层 | 首批策略回测后实施 |
| 换手率黄金标准 | 22-C 未含换手率维度 | 首批策略回测后实施 |
| 量化接力阈值矩阵 | 无市场情绪绝对阈值前置门控 | 首批策略回测后校准 |
| 2026-07-06交易新规阈值更新 | ±12%→±20% | G22 执行层施工时同步 |
| legulegu 六指标情绪评分 | 首封时间线性映射 | 远期参考 |
| 跌停板反抽/反核策略 | §3.12+§3.13缺失#3/#7 | Phase 5 候选 |
| 辛普森悖论多因子联合检验 | §4.1 补 | 首批策略回测时做 |
| CatBoost Tick 级破板预测 | Phase 5 候选 | 需 Tick 数据基础设施 |
| 量游共振退潮三信号 | Phase 5 候选 | 首批策略回测验证 |
| 分笔建仓算法 | §3.13缺失#4 v1.9.2补 | 依赖G22，Phase 3 |
| Liquidation cascade 机理 | §3.2 v1.9.2补 arXiv:2608.03616 | 远期理论参考 |
| Public Trader Identity | §3.10 v1.9.2补 arXiv:2608.04373 | 与量化席位预警联动 |
| 微结构均值回归执行 | §3.13缺失#4 v1.9.2补 arXiv:2608.00885 | 与分笔建仓联动 |
| 打板时点决策 | §3.14#11 v1.9.3补 | Phase 3 |
| 容量动态测算 | §3.14#12 v1.9.3补 | Phase 3 |
| A股价格笼子政策实证 | §3.7 v1.9.3补 Frontiers Physics 2025 | 与40号价格笼子联动 |
| 双引擎两层分类法统一裁定 | §3.5 v1.10.0 澄清：production 6 类标的分类 vs 本文档 7 类交易动作不同层 | 首批实盘前裁定——动作层是否吸收进 `dual_engine_fusion_decision_engine.py`（落码 REFLUSH_DIVE 时一并处理） |
| 42 号时间止损口径校准 | [42 §3.2] 打板时间止损 1-2 天 vs 本文 §3.13#1 `max_holding_days=3`（§2.3 持仓周期 1-3 天） | 首批策略回测时统一（42 号侧亦标"待 G04 校准"，属跨文档校准项，不擅自改） |
| battle_map BM-SEL-23-A-6 修正 | §3.8 已裁定源码 10 分/sum 95 为真源，battle_map 仍写 15 分 | reconciler fix-in-place（他文档，不越界改） |
| C9 换手率按流通盘分层校准 | §3.4 C9 当前单一区间 3%-15%；雪球 2026-02-25 给出分层最优：50亿下 8-15%（炸板率12%）/ 50-200亿 5-10%（10%）/ 200亿上 3-6%（8%），且缩量加速板（<前日50%换手）炸板率翻倍 | 首批策略回测时用项目自有数据验证分层区间后修订 C9 |
| ✅ 文档算法已补·首批实盘前必做施工 | §3.13#1 次日出场完整决策 / §3.13#2 打板专用瞬时风控 / §3.13#5 龙虎榜PIT处理（**必须修复**） / §3.14#8 打板信号前置质量评估 / §3.14#9 持仓期间微结构监控 | 首批实盘前落码 |
| ✅ 文档算法已补·首批回测前必做 | §3.14#10 PIT 安全回测框架 | 首批回测前落码 |
| ✅ 文档算法已补·首批实盘后即需 | §3.13#6 CUSUM 信号失效监控 | 首批实盘后落码 |
| ✅ 文档算法已补·首批回测校准/验证 | 中位股死亡池（v1.5.0）/ 梯队健康度四档判定（v1.5.0，准确率回测时评估）/ 龙虎榜量化席位过滤（v1.7.0）/ 纸老虎识别（v1.7.0）/ 分级梯队晋级率（v1.7.0，准确率回测时评估）/ 封单结构双指标（v1.8.0）/ 次日溢价三维预测（v1.8.0）/ 回封生死线决策（v1.8.0）/ 龙虎榜量化席位双阈值（v1.8.0）/ 炸板率板块地位分层（v1.9.0） | 首批策略回测后校准/验证 |
| ✅ 文档算法已补·Phase 5 | 打板vs反核切换（§3.13#3）/ 反核二次出场（§3.13#7） | Phase 5 落码 |
| ✅ 理论背书已登记 | 打板理性预期理论根基（§3.2 北大Jiang&Li，远期理论参考）/ Passive impact 指数填充概率（§3.13#4 arXiv:2607.28323，与分笔建仓联动）/ SaR 前瞻性滑点风险（§3.13#4+§3.14#9/#12 arXiv:2603.09164，与持仓监控+容量测算联动）/ Two-type classification 级联（§3.13#6 arXiv:2607.27070，与CUSUM联动）/ Latent microstructure regime（§3.14#9 arXiv:2604.20949，与持仓监控联动）/ 7-event cascade 异质性（§3.13#6 arXiv:2607.27070，与方差压缩检测器联动）/ QFCQT 混沌门控 Quantformer（§5.2 Phase 5 arXiv:2608.07363，远期ML架构候选，A股股指测试）/ Hawkes 长记忆核封单动力学（§3.13#4 arXiv:2608.02002，与Passive Impact联动）/ QLoRA 情感因子负面结果警示（arXiv:2608.04200，情感因子需经济验证非语言学指标）/ 速度域签名封板真伪判断（§5.2 Phase 5 arXiv:2608.05373，速度域优于水平域，填补盘中封板质量评估缺口）/ 扩散价格动力学悖论（§3.13#4 arXiv:2608.00988，拆单不泄露信息的精确理论依据） | 远期理论参考/对应算法联动 |

## 7. 待定问题（讨论要点）

- [x] 8 项讨论要点全部闭合：① 连板梯队识别 → §3.1；② 情绪周期定位器 → §3.2；③ 主升龙头识别 → §3.3；④ 打板容量极小 → §3.4；⑤ 双引擎融合 → §3.5（7 类决策）；⑥ 打板专用风控 → §3.6（四层风控+§3.13#2 瞬时风控）；⑦ T+1 时序 → §3.7（+§3.13#1 完整出场决策）；⑧ 助攻梯队权重 → §3.8

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G08
- [20_first_batch_strategies](20_first_batch_strategies.md) §2.2 打板 sleeve
- [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) §3.1-3.4/§5.2/§6
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.4/§2.5/§6.3/§7.3
- [40_execution_broker](40_execution_broker.md) §决策⑫（v2.6.0）
- [41_buy_flow](41_buy_flow.md) §5.2 / [42_sell_flow](42_sell_flow.md) §3.8
- [15_data_feature_layer_spec](15_data_feature_layer_spec.md)
- battle_map_05_stock_selection（BM-SEL-22~25）
- **arXiv**：2607.27063 羊群agent-based / 2608.03616 liquidation cascade / 2608.04373 Public Trader Identity / 2608.00885 微结构均值回归 / 2607.05141 Square-Root Impact / 2607.28323 Passive Market Impact（v1.9.3补）/ 2603.09164 SaR Slippage-at-Risk（v1.9.3补）/ 2607.27070 7-event cascade two-type（v1.9.3补）/ 2604.20949 Latent Microstructure Regime（v1.9.3补）/ 1503.03548 A股价格限制统计性质（v1.9.3补）/ 2505.22678 Siamese LOB A股实证（v1.9.4补）/ 2506.06356 Du A股5模块框架15.2%年化（v1.9.4补）/ 2608.07363 QFCQT 混沌门控 Quantformer A股股指测试（v1.9.5补）/ 2608.02002 Hawkes 长记忆核 Volterra-Riccati 封单动力学（v1.9.5补）/ 2608.04200 QLoRA 情感因子负面结果 28组合无一显著（v1.9.5补）/ **2608.05373 速度域签名封板真伪判断 AUC=0.91（v1.9.7补）/ 2608.00988 扩散价格动力学悖论 Lévy-walk 精确可解（v1.9.7补）**
- **券商/社区**：雪球炸板率2026-07 / 华安涨停板Alpha2026-03 / caifuhao连板复盘2026-08 / 头条量化vs游资2026-08 / CSDN集合竞价2026-08 / 叩富问财封单避坑2026-07 / legulegu情绪评分2026-07 / mathandmarkets CUSUM2026-02 / stockalpha.ai Concept Drift2026-02 / quant67执行算法2026-05 / **国泰海通高频选股因子周报2026-08-10（v1.9.4补，开盘后买入意愿强度因子2026多空16.29%+尾盘成交占比13.58%，打板竞价+尾盘时段行为因子实证背书）**
- **学术期刊**：北大Jiang&Li打板理性预期模型（v1.9.3补）/ Frontiers in Physics 2025-07 A股价格笼子政策实证（v1.9.3补）/ Journal of Forecasting 2025-03 A股价格限制可预测性 ML 66%（v1.9.3补）

## 9. 修订记录

| 日期 | 版本 | 变更摘要 |
|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 |
| 2026-08-10 | 1.0.0 | 8 项讨论要点全部对齐落定，status→active |
| 2026-08-10 | 1.5.0 | §3.1 classify_echelon_health 四档 + score_consecutive_height_with_death_pool |
| 2026-08-10 | 1.6.0 | §3.9 竞价三维100分 |
| 2026-08-10 | 1.7.0 | §3.10 量化vs游资三次炸板回封+纸老虎+分级晋级率 |
| 2026-08-10 | 1.8.0 | §3.2 羊群agent-based机理 + §3.5 v1.8.2 伪代码同步 + §3.11 封单双指标+预测+回封+席位预警 |
| 2026-08-10 | 1.9.0 | §2.1 效益崩塌硬数据 + §3.1 炸板率分层 + §3.12 反核策略 + §4.1 辛普森悖论 + §5.2 Phase 5 |
| 2026-08-10 | 1.9.1 | 状态行版本同步 + §6 程序化新规交叉引用（40号v2.6.0已闭合） |
| 2026-08-10 | 1.9.2 | **施工算法完整性深度审查——7项缺失补全**：§3.13 新增①next_day_exit_decision() ②DabanInstantCircuitBreaker ③classify_decision_v192 第7类REFLUSH_DIVE ④DabanExecutionAlgorithm ⑤get_dragon_tiger_pit() PIT断言 ⑥SignalDecayMonitor CUSUM+PSI ⑦reflush_next_day_exit_decision()。§3.2补liquidation cascade(arXiv:2608.03616)。§3.10补Public Trader Identity(arXiv:2608.04373)。§3.13缺失#4补微结构均值回归(arXiv:2608.00885)。全网搜索8月3-10日92篇arXiv q-fin：无A股涨停板专门新论文。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.9.3 | **第三轮施工算法深度审查——5项缺口补全+2项算法升级+理论背书补**：§3.14 新增⑧pre_validate_daban_signal 前置质量评估 ⑨HoldingPeriodMicrostructureMonitor 持仓期间微结构监控 ⑩DabanPITBacktestFramework 全数据源PIT回测框架 ⑪DabanTimingDecision 打板时点决策（追板vs埋伏）⑫DynamicCapacityCalculator 容量动态测算。§3.13#4 DabanExecution 升级 passive impact 指数填充概率(arXiv:2607.28323)+SaR(arXiv:2603.09164)。§3.13#6 SignalDecayMonitor 升级 two-type classification(arXiv:2607.27070)+方差压缩检测器+latent regime(arXiv:2604.20949)。§3.2补北大Jiang&Li打板理性预期理论根基+liquidation cascade 88%/30min/63%实证细节。全网搜索8月8-10日arXiv q-fin+学术期刊：新增5篇arXiv+3篇学术期刊。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.9.4 | **第四轮最新研究整合——Phase 5 ML增强+A股行为因子实证背书**：§5.2 Phase 5 补 Siamese LOB 架构（arXiv:2505.22678 A股14军工股 ask-bid 对称性+MHA-LSTM 超75%基线提升）+ Du 开盘信号分布混合模型（arXiv:2506.06356 A股5模块框架 15.2%年化/Sharpe 1.87，开盘竞价mixture model+市值流动性动态仓位+grid-search止盈止损）。§8 引用补国泰海通高频因子周报2026-08-10（开盘后买入意愿强度因子2026多空16.29%+尾盘成交占比13.58%，打板竞价+尾盘时段行为因子实证背书）。12项施工算法已完整覆盖信号→定位→入场→封板→出场→风控→容量全流程，本轮无新施工算法缺口。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.9.5 | **第五轮最新研究整合——Phase 5 ML架构+封单动力学+情感因子警示**：§5.2 Phase 5 补 QFCQT 混沌门控 Quantformer（arXiv:2608.07363 A股股指直接测试，Lee振荡器+平滑-混沌门控融合，高波动场景MSE相对HAT提升43.9%，适合情绪周期突变检测，远期ML架构候选）。§3.13#4 DabanExecution 理论背书补 Hawkes 长记忆核（arXiv:2608.02002 Volterra-Riccati近似，封单Hawkes动力学一般核建模，与arXiv:2607.28323 Passive Impact同作者，补充长记忆衰减）。§6 待裁定补 QLoRA情感因子负面结果警示（arXiv:2608.04200：28个模型-期限组合Newey-West+FDR校正后无一显著，情感分类准≠可交易，A股情感因子需经济验证非语言学指标）。12项施工算法仍完整，本轮无新施工算法缺口。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.9.6 | **第六轮字段填充断裂点审查——§3.13#1 NextDayExitDecision 补 classify_position_status() 方法**：decide() 依赖 consecutive_board（连板晋级）和 exploded（炸板）两字段但此前无填充算法。本方法形式化：①连板晋级判断=T+1日涨停收盘+封单存在(封流比>0.1%)+梯队非孤板(LONE_DRAGON/COLLAPSE排除) ②炸板判断=T+1日盘中触及涨停(最高价≥涨停价×0.999)但未封住(收盘<涨停价)。与§3.1 classify_echelon_health联动(梯队健康度影响晋级有效性)+§3.13#2 DabanInstantCircuitBreaker联动(炸板触发瞬时风控)。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.9.7 | **第七轮最新研究整合——速度域签名封板真伪判断+扩散价格动力学悖论**：§5.2 Phase 5 补速度域签名封板真伪判断（arXiv:2608.05373 Chen&Hybinette 2026-08-05，速度而非水平域检测pump-and-crash，price velocity签名区分"真封板"vs"诱多封"，HMM regime条件检测+SHAP可解释归因，印度BANKNIFTY 10/10操纵日恢复+AUC=0.91，A股连板炸板率70%环境下速度签名比传统封单量/换手率水平指标更鲁棒，填补"盘中封板质量实时评估"缺口。负面结果启示：HMM regime用于条件检测是用召回率换精确率，单纯状态划分不够需结合速度签名条件触发）。§3.13#4 DabanExecution理论背书补扩散价格动力学悖论（arXiv:2608.00988 Sato et al. 2026-08-02，平方根冲击律+Lévy-walk框架精确可解，严格证明可预测订单流下价格仍扩散=拆单不泄露信息，为批量入场拆单提供理论依据）。12项施工算法仍完整，本轮无新施工算法缺口。延续轻量优先+不替换已定决策原则 |
| 2026-08-12 | 1.10.0 | **第八轮架构审查（通用规则#11 设施盘点+文档-代码一致性修正+2026-08 最新研究对照）**：①新增 §1.1「已施工设施盘点」——grep 级代码侧真源审计：打板信号链四引擎（short_term_stock_selector/youzi_relay_emotion_engine/quant_short_term_strength_engine/dual_engine_fusion_decision_engine）+支撑设施（cash_manager/position_sizing_engine/drawdown_controller/cancel_rate_guard/price_cage/ex_core）全部 production 且有测试；明确 §3.13/§3.14 十二项形式化算法与 v1.5.0~v1.9.0 八个具名函数（classify_echelon_health/score_auction_3d 等）**全部未落码**（文档已定型、代码待施工），消除"已补=已 production"误读。②§3.5 修正——术语对齐 battle_map canonical 名（游资情绪引擎/量化强度引擎，替换情绪/技术引擎）；澄清两层分类法架构（production 6 类标的分类 vs 本文 7 类交易动作映射层）；**修正 v1.8.2"伪代码匹配 production classify_decision"不实声明**（两者分类语义不同层）。③§1 正交行引用修正——审查时 [28 §3.4] 悬空（28 号骨架），先改指 [20 §2.2] 真源；审查期间 28 号填充定型（active 1.0.0），最终恢复 [28 §3.4] 为主引用 + [20 §2.2] 互证。④§3.1 炸板率分层补雪球 2026-02-25 独立印证（龙头8%/跟风32%/孤板58% 两源同值互证 + 板型分层 + 一字龙已被 C9 隐式拒入）。⑤§6 待裁定新增 5 条：两层分类法统一裁定/28 号前向引用回填/42 号时间止损口径（1-2天 vs max_holding_days=3）校准/battle_map BM-SEL-23-A-6 15分修正/C9 换手率按流通盘分层校准（雪球分层最优区间，首批回测验证后修订）。⑥28 号同步——28 号 2026-08-12 已填充定型（active 1.0.0），§1 正交行恢复 [28 §3.4] 为主引用 + §6 对应待裁定行核销。延续轻量优先+不替换已定决策原则 |
| 2026-08-12 | 1.10.1 | **作战地图全覆盖补丁——闭合 BM-SEL-22-A / BM-SEL-22-B / BM-SEL-25-D（3 环节）**：① §1.1 设施表 ① 补「作战地图子环节契约补注」（3 支 production 子环节此前仅登记级提及，指针到 §3.5 后附段）；② §3.5 补「作战地图子环节契约补全」后附段——BM-SEL-22-A 机构选股评分器 4 维加权契约（目标价空间 40%/基本面 30%/技术趋势 20%/流动性 10%，以作战地图 indicators 为真源核对）；BM-SEL-22-B 强庄股识别器三特征识别规则（走势独立性/换手率异常倍数/盘口神秘大单，三特征同时命中）；BM-SEL-25-D PDF 分布信号提取 `extract_pdf_signal` 4 维语义展开（方向/置信度/尾部风险/相对价值）。3 支均 ✅ production 有测试，本次为文档契约补记（定位→裁定→契约→重评条件四要素），无代码变更。延续轻量优先+不替换已定决策原则 |
| 2026-08-12 | 1.10.2 | 作战地图环节映射补强——锚定 BM-SEL-22-C（+22-C-1~7）/22-D、BM-SEL-23-A（+23-A-1~6）、BM-SEL-24-A（+24-A-1~6）/24-B（§1.1 末映射块）、BM-SEL-24-C、BM-SEL-25-C（+25-C-1~6）（§3.5 末映射块）；24-A 行注明与 21 号 §3.4 分工（21 号管量化引擎输入定位与权重校准，本篇管打板 sleeve 逐维构成与消费点）：语义已覆盖但正文未显式编号的环节锚定到承载小节，实现环节级可追溯；不改既有正文 |
| 2026-08-12 | 1.10.3 | 作战地图环节映射补强②——子维度编号全枚举：§1.1/§3.5 映射块中 4 行区间记法（22-C-1~7 / 23-A-1~6 / 24-A-1~6 / 25-C-1~6）展开为逐编号显式列出（BM-SEL-22-C-1...C-7 / BM-SEL-23-A-1...A-6 / BM-SEL-24-A-1...A-6 / BM-SEL-25-C-1...C-6），修复编号级可追溯性扫描漏匹配；不改既有正文 |
| 2026-08-12 | 1.10.4 | 作战地图环节映射补强③——补锚 BM-SEL-23-C（情绪周期策略映射→§3.5 门控切换 + §3.6 仓位上限 5 档，体系深锚 28号 §3.2）与 BM-SEL-25-B（情绪周期自适应权重→§3.5 `determine_adaptive_weights` 5 档）：PG `battle_map_steps` 全量核对（340 环节/19 deprecated/321 活跃）发现 3 个活跃环节未显式锚定，其中 2 个属本篇（另 1 个 BM-SIM-08 归 53号）；语义早已覆盖（§3.5/§3.6 既有正文），仅补编号级锚定，不改既有正文 |
| 2026-08-14 | 1.10.5 | 压缩精简：噪音去除+施工细节梳理，零信息丢失审查通过（AI-DOCS-001） |
| 2026-08-15 | 1.10.6 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-06）——§1 状态行内容清单墙去重（真源=文首块引用+§9 修订记录）；§7 八项已闭合讨论要点压缩为一行映射；§6 删「已闭合·交叉引用」行（40 号 v2.6.0 闭合见 §3.7 施工状态+v1.9.1 修订记录，28 号前向引用落地见 §1.1④+v1.10.0 修订记录）。炸板率 8/32/58、晋级率 50/30/15/0、13 约束链、7 类决策、12 项算法参数/裁定/链接零丢失 |
