---
ttl: permanent
doc_type: architecture_view
title: 密度预测与 QNN 远期愿景
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.4"
date: 2026-08-15
topic: density_prediction
scope: 07_trading_decision_architecture
---

## 结案报告（AI-NIGHT-001 复核 2026-08-19）

> **实际开发**（远期愿景文档——无施工承诺，机制落地状态=维持规划态）：本篇自创建起即定位"远期愿景，待讨论"；90 号 v2.0.0 §10 已裁定"密度预测远期维持，MVP 不建"；v0.1.3 作战地图补丁按 90 号 §10 规划态真源回填 BM-SEL-14/14-A/15 三环节登记（均 design 态，明示"不代表已定稿施工方案"）。
>
> **最终成果**（2026-08-19 代码实证）：仓内现存唯一相关实现为 `feedback_loop/evolution/conformal_prediction.py` 简易 CP 骨架（进化模块自用，非市场密度预测），与 90 号「已施工设施盘点」#10 一致；RWC / LSTM+GMM / MDN / Survival AFT / TCP-RM/DDCI / QNN 全仓零命中——与"远期不施工"裁定一致，无漂移。
>
> **未做事项及原因**：
> - BM-SEL-14 共形预测 Phase 0（slow unweighted rolling conformal + RWC 最优变体）——远期愿景，激活条件=密度预测体系立项；裁定=未来工程-大型（且 conformal 五变体栈收敛范围待 90 号 P-2 用户裁定）。
> - BM-SEL-14-A TCP-RM/DDCI 自适应保形非平稳覆盖——已裁定降级 Phase 2 非平稳增强候选（RWC 优先；RWC 压力期残余 exceedance 显著超名义水平才重评）；裁定=过度工程（当前阶段）。
> - BM-SEL-15 Survival 止盈止损时间预测（AFT 首选，KM 基线/Cox 诊断）——激活条件=密度预测模型验证通过；裁定=未来工程-大型。
> - BM-BUY-02-A-1-c 8 态预测 PDF 积分派生接口——随 90 号 §7 暂缓建设一并冻结（重启三条件未达）；裁定=过度工程（当前阶段）。
> - QNN 量子神经网络——远期愿景待讨论问题（单机 RTX 3090 工程可行性未证）；裁定=过度工程（当前阶段）。

> ## 结案报告回填（2026-08-28 代码实证复核）
> 原"RWC/MDN/Survival AFT/TCP-RM/QNN 全仓零命中"已严重过时，愿景项已被后续批次大量落码：signal_ashare/conditional_density_predictor.py（MOD-SIG-043 production，BLUEPRINT 锚定本文 §1）+survival_time_predictor.py（MOD-SIG-045，AFT+KM）+tcp_rm_conformal.py（MOD-SIG-128，Robbins-Monro+DDCI）+adaptive_conformal_tcp_rm_ddci.py+conformal_predictor.py+event_conditional_density.py；ml_train/implementations/qnn_two_stage.py（MOD-ML-010，注意=分位数 QNN 非量子 QNN）+patchtst_density_encoder.py+kan_density_head.py。
> **仍真实未完工**：量子神经网络（quantum QNN）零命中——与"过度工程不施工"裁定一致；RWC 变体未单独实证；90 号 P-2 conformal 五变体栈收敛待 Owner。本文 draft v0.1.4 与代码现状漂移最大，后续升版时应将状态从"愿景登记"改为"愿景项已部分落码"。

# 密度预测与 QNN 远期愿景

> **状态**：远期愿景，待讨论。源自原《能力定位书》约束十二，当前项目中无代码实现，亦无对应 G01-G28 讨论主题。移入此处待条件成熟后启动讨论。

## 原始内容

- 分阶段实现（参数化→QNN→非参数化）
- 概率校准度偏离对角线<5%才可消费
- 尾部校准（VaR覆盖率误差<2%）为风控消费前提
- CRPS为核心评估指标
- 8态概率Phase4后从PDF积分派生
- 半Kelly为硬上限（0.5×f*）

## 待讨论问题

1. **密度预测是否为当前阶段必需？** 项目当前 regime 检测已定稿12态（10_regime_detector_spec），密度预测是否在 regime 之上还有增量价值？
2. **QNN（量子神经网络）可行性** — 单机 RTX 3090 环境下 QNN 训练/推理的工程可行性？
3. **校准阈值来源** — "5%偏离"、"2%覆盖率误差"这些阈值的依据是什么？需要回测验证。
4. **与现有风控模块的关系** — 30_multi_strategy_concurrency 已定义4级回撤 Protocol 和 FirmRiskAggregator，密度预测如何融入？

## 作战地图环节登记（v0.1.3 作战地图全覆盖补丁，按 90 号 §10 规划态真源回填）

> 以下来自作战地图 stock_selection 流程的 3 个 design 态环节在本稿登记。90 号 v2.0.0 §10 已裁定"密度预测远期维持，MVP 不建"，并警示：90 号各版本引用的"91 号 v0.4.0~v1.4.0"内容（四阶段路线/RWC/Lévy/Exformer）均未落盘到本稿，属**规划态提案（真源在 90 号）**。本节按 90 号 §10 规划态真源回填环节级登记，不代表已定稿施工方案。

### 1. BM-SEL-14 共形预测（L2A，design，MOD-SIG-044）

- **定位**：密度预测 PDF（BM-SEL-13）输出后叠加共形区间层——目标覆盖率 95%，产出"覆盖率保证区间"，下游 BM-EXE-01 共形 VaR / 信号置信区间。触发=密度预测输出后；降级=共形预测未就绪时区间无数学覆盖率保证。
- **裁定（按 90 号 §10 规划态回填）**：**Phase 0 基线 = slow unweighted rolling conformal**（90 号 §10 裁定注记③，Conformal Kelly 实证"慢而稳 conformal 胜过快而自适应"），**变体路线 RWC（Regime-Weighted Conformal，Oxford 2026-08-03，arXiv:2602.03903v3）为 Phase 0 最优变体**（90 号 v0.6.0 登记——复用项目 regime 检测器提供 regime 相似度权重，比 TCP 架构原生匹配；压力期自动收紧）。conformal 五变体栈（slow→EWMA→RWC→ACI→COP）的最终收敛范围**待 90 号待定问题 P-2 用户裁定**（建议方向② slow unweighted+EWMA+ACI 三层，RWC/COP 作压力期不达标时升级）。
- **契约/参数**：输入=收益率条件密度 PDF；输出=95% 名义覆盖率区间（分布无关有限样本边际覆盖保证）；区间层设计=PDF 分位数（2.5%/97.5%）外裹 conformal 安全缓冲（历史预测误差滚动窗口分位数）；消费前提=概率校准度偏离对角线<5%、尾部 VaR 覆盖率误差<2%（原始内容既有阈值）。
- **重评条件**：36 号 VaR/ES 压力期失准复盘确认需要 joint breach frequency+magnitude 控制时，评估 FCVE（90 号 v1.6.0 登记，Phase 2 远期）。

### 2. BM-SEL-14-A 自适应保形非平稳覆盖（TCP-RM/DDCI，L2A，design，MOD-SIG-052 planned）

- **定位**：非平稳市场环境（体制漂移/分布迁移）下的自适应保形覆盖——TCP-RM（自适应保形滚动/regime 模型覆盖半径）+ DDCI（非平稳分布无关动态保形推断），目标覆盖率 95%。消费=BM-SEL-13 密度 PDF + BM-SEL-07 体制转换标签；下游=BM-SEL-04 8 态预测 / BM-BUY-02 信号置信度。
- **与 RWC 的取舍裁定**：**RWC 优先，TCP-RM/DDCI 降级为非平稳增强候选（Phase 2）**。依据=90 号 §10 引用"RWC 为 Phase 0 最优变体"——RWC 的指数时间衰减+regime 相似性权重已覆盖"平滑 regime 漂移"场景（含覆盖率上下界推导，不假设加权可交换性），且复用项目 regime 检测器零额外建模；TCP-RM/DDCI 面向更激进的非平稳/突变场景，复杂度更高（~200 行+），在 RWC 压力期覆盖率不达标前不引入。降级路径=自适应变体失效回退 BM-SEL-14 静态共形预测。
- **重评条件**：RWC 实跑后压力期残余 exceedance 显著超名义水平（90 号 v0.7.0 登记 RWC 关键告诫：压力期残余 2.29% exceedance）时，评估 TCP-RM/DDCI 或 ACI 补层。

### 3. BM-SEL-15 Survival 止盈止损时间预测（L2C，design，MOD-SIG-045）

- **定位**：预测止盈/止损发生时间的分布——消费市场状态（BM-SEL-03），产出止盈止损时间分布，下游 BM-POS-01 仓位时间预算 / 止盈止损时点。降级=Survival 未就绪时止盈止损用固定规则（现状）。
- **激活条件**：**密度预测模型验证通过**（与 [21_stock_selection_engine §6](21_stock_selection_engine.md) 登记一致——"Survival/密度预测：止盈止损时间预测、T+1 次日 8 态属远期愿景，激活条件=密度预测模型验证通过"）。
- **生存分析选型裁定（三选一）**：**首选 AFT（Accelerated Failure Time，参数生存模型）**——① 直接建模"事件发生时间"本身的对数线性回归，输出是可解释的持有期分布参数，与"仓位时间预算"直接对接（Cox 输出风险比而非时间）；② 不依赖 Cox 的比例风险假设（市场状态切换下 PH 假设大概率不成立）；③ 参数少（Weibull/log-logistic 两参族），个人系统样本量可估。**Kaplan-Meier 作非参数基线**（分层 KM 曲线校准 AFT 拟合优度），**Cox 作协变量显著性诊断工具**（筛选哪些市场状态变量显著影响止盈止损时间，喂回 AFT 特征集）。复杂度升级路径（时变协变量/竞争风险）列 Phase 3+。
- **重评条件**：密度预测 Phase 0（本节第 1 条）校准达标（5%/2% 阈值）后启动本环节详细设计。

### 4. 衔接：BM-BUY-02-A-1-c 八态预测的远期接口

BM-BUY-02-A-1-c（T+1 次日 8 态走势预测，L2C，design）的远期接口=**"PDF 积分派生"**（8 态概率从密度预测 PDF 对各区间的积分派生，非独立分类模型）——与 90 号 §7 暂缓裁定呼应：8 态预测已降级远期候选，"Phase 4 后从 PDF 积分派生"随 §7 暂缓建设一并冻结；重启以 90 号 §7 三条件（系统稳定盈利 / 目标收窄为开盘 30 分钟走势 / 概率仅接入仓位微调）全部满足为前提，届时本稿密度 PDF 是其唯一输入源，不另建 8 态专用模型。

## 关联

- 00_index_trading_decision G16-G18（风控落地）
- 10_regime_detector_spec（regime detector spec，12态）
- 30_multi_strategy_concurrency（多策略并发，仓位/风控框架）

## 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.1 | 文件名 discussion_021_density_prediction.md → 91_density_prediction.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 0.1.2 | 文档头统一：title/H1 去"讨论稿："前缀，scope 归一为 07_trading_decision_architecture；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-12 | 0.1.3 | 作战地图全覆盖补丁——BM-SEL-14 / BM-SEL-14-A / BM-SEL-15（+BM-BUY-02-A-1-c 衔接）。新增「作战地图环节登记」节，按 90 号 §10 规划态真源回填 3 环节：① BM-SEL-14 共形预测——Phase 0 基线=slow unweighted rolling conformal，RWC 为 Phase 0 最优变体（复用 regime 检测器），栈收敛范围待 90 号 P-2 用户裁定；密度 PDF→95% 覆盖率区间层（PDF 分位数外裹 conformal 安全缓冲），消费前提=校准偏离<5%/尾部覆盖率误差<2%；② BM-SEL-14-A TCP-RM/DDCI——与 RWC 取舍裁定：RWC 优先，TCP-RM/DDCI 降级 Phase 2 非平稳增强候选（RWC 压力期残余 2.29% exceedance 为触发重评）；③ BM-SEL-15 Survival 止盈止损时间预测——选型三选一裁定首选 AFT（直接建模事件发生时间、无 PH 假设、参数少），KM 基线校准、Cox 协变量诊断；激活条件=密度预测模型验证通过（与 21 号 §6 登记一致）；④ 衔接 BM-BUY-02-A-1-c 八态预测远期接口="PDF 积分派生"，与 90 号 §7 暂缓裁定重启条件呼应，不另建 8 态专用模型 | 作战地图 14 环节全覆盖施工：闭合 stock_selection 流程 3 个 design 态环节在本稿的登记缺口；90 号 v2.0.0 §10 警示"91 号实际仅 v0.1.2 骨架，引用内容均未落盘"，本版按规划态真源回填 |
| 2026-08-15 | 0.1.4 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-06） | 通读零发现——规划态登记已按定位→裁定→契约→重评条件四要素最简（BM-SEL-14/14-A/15 三环节+衔接段），正文零变更 |
