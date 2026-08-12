---
ttl: permanent
doc_type: architecture_view
title: 密度预测与远期演进路线
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.1"
date: 2026-08-12
topic: density_prediction
scope: 07_trading_decision_architecture
---

# 密度预测与远期演进路线

> **定位**：本文档是密度预测（收益分布预测）能力的讨论真源——记录"是否做/做什么/何时做/不做什么"的完整裁定。源自原《能力定位书》约束十二，当前项目中无代码实现，亦无对应 G01-G28 讨论主题。
>
> **一句话裁定**：密度预测是**高杠杆的中期增强**（非 MVP 必需），走"Conformal 校准 → 轻量 Kelly 收缩 → 分位数回归密度"三步轻量路线；QNN（量子神经网络）从路线图**删除**，降级为理论关注项。

---

## 1. 背景与来源

### 1.1 原始内容（能力定位书约束十二，2026-08-07 移入）

- 分阶段实现（参数化→QNN→非参数化）
- 概率校准度偏离对角线<5%才可消费
- 尾部校准（VaR覆盖率误差<2%）为风控消费前提
- CRPS为核心评估指标
- 8态概率Phase4后从PDF积分派生
- 半Kelly为硬上限（0.5×f*）

### 1.2 历史引用漂移说明（2026-08-12 审查发现）

90_methodology_open_questions §10 修订记录（v0.4.0~v1.17.0）中多处引用"91 号 v0.4.0/v0.5.0/v0.6.0/v1.2.0/v1.3.0/v1.4.0"（如"91 号 Phase 0 RWC 最优变体""91 号 v0.6.0 Information-Entropic DL+GP""见 91 号 v1.2.0 Lévy 家族"）。**经 git 历史核实：91 号自移入以来仅有 45 行骨架（v0.1.1/v0.1.2 两次重排提交），上述版本号内容从未写入本文档**——相关调研结论实际沉淀在 90 号修订记录中。本文档 v1.0.0 起将 90 号修订记录中所有标注"91 号同步/见 91 号"的内容吸收回填，91 号版本号自此与内容同步。90 号文档保持只读不改，其历史引用视为指向本文档 v1.0.0 对应章节。

### 1.3 核心概念界定

**密度预测**（density prediction / probabilistic forecasting）：预测标的次日收益的**完整条件概率分布** P(r|X)，而非点估计 E[r|X]。下游四处消费：

| 消费者 | 消费内容 | 现状 |
|---|---|---|
| 31 号 Kelly 精裁决（MOD-POS-001） | μ/σ²（PDF 前两阶矩积分） | 已定"密度 PDF 主源 + 历史降级"（§2.3.2），代码接口已预留（`win_probability/win_loss_ratio`，None=降级） |
| 36 号 VaR/ES 监控 | 左尾分位数（第三路验证） | 已定参数法+历史模拟取 max + POT/GPD 厚尾（§3.1/§3.2），production |
| 42 号卖出流程止盈位（BM-SELL-03/MOD-SELL-004） | PDF 75% 分位数（止盈位计算） | planned，已定降级路径（密度 PDF 缺失→退化为固定止盈） |
| 8 态走势派生（BM-SEL-04） | PDF 积分派生 8 态概率 | **已随 90 号 #7 裁定暂缓**（A 股预测天花板 52-53% 实证，firsh.me 2026-07） |

> battle_map 登记：BM-SEL-13（收益率条件密度预测，设计态，🟡借鉴）+ BM-SEL-14（共形预测，设计态，含 14-A 自适应非平稳覆盖 TCP-RM/DDCI 🔴自建）——本文档是这两个环节的设计讨论真源。

---

## 2. 已施工设施盘点（通用规则 #11，2026-08-12 全量扫描）

> 先清楚有什么 → 才能知道怎么改 → 才能知道该删除/退役什么。扫描范围：代码/配置/schema/注册表/测试/文档引用。

### 2.1 代码层（与密度预测直接相关）

| 设施 | 路径 | 状态 | 与密度预测的关系 |
|---|---|---|---|
| Kelly 仓位裁决 | `src/zephyr/position/core/position_sizing_engine.py`（MOD-POS-001） | production | **已预留密度预测接口**：`win_probability/win_loss_ratio: float \| None`（None=降级等权）；当前实现为二值 Kelly `f*=(bp-q)/b` + 半 Kelly 硬上限 + VaR/CVaR 下调（C4/C5）；偏度/峰度调整（C10）未实现（依赖密度 PDF 高阶矩） |
| Kelly 参数来源标记 | `src/zephyr/position/core/firm_risk_aggregator.py` | production | `kelly_param_source: "density_pdf" / "historical_fallback"` 双源口径已定义 |
| VaR 计算 | `src/zephyr/risk/core/var_calculator.py`（MOD-RK-05） | production | 参数法+历史模拟取 max；36 号 §3.1 真源 |
| ES/尾部风险 | `src/zephyr/risk/core/tail_risk_monitor.py`（MOD-RK-15） | production | 历史模拟 ES + POT/GPD 厚尾拟合（ξ>0.2 厚尾告警，ξ>0.5 FRTB 加价）；**GPD/EVT 已施工，91 号路线图不再重复登记 GPD 阶段** |
| VaR 回测 | `src/zephyr/risk/core/var_backtester.py`（Kupiec/Christoffersen/E-backtesting GREM） | production | 36 号 §3.9 真源；密度预测 VaR 达标判定复用此设施 |
| regime 检测器 | `src/zephyr/regime/core/regime_detector.py` 等 | production | 4 态 HMM + 3 overlay（7 维概率输出）；两阶段概率校准 ECE=4.2% PASS（10 号 §9.3）；**是 Mondrian/RWC regime 分桶的现成输入** |
| ConformalPrediction | `src/zephyr/feedback_loop/evolution/conformal_prediction.py` | production（玩具态） | ⚠️ **与交易密度预测无关**——D_FEEDBACK_LOOP 域 R74 盲点对（anomaly score 置信区间，`predict_interval` 返回 score×0.8/1.2 占位实现）。**不可误当作交易 conformal 基础设施复用** |
| BM-SEL-13 密度预测模块 | battle_map_05 已登记环节（设计态）；MOD-SIG 代码落点规划为 `src/zephyr/signal_ashare/` 平铺（信号域目录约定，无 signals/density 子目录） | **零代码** | 全库扫描确认无实现（`density/conformal/crps` 关键词在 src/ 下无交易域命中） |
| BM-SEL-14 共形预测环节 | battle_map_05 已登记（设计态）；14-A 自适应非平稳覆盖（TCP-RM/DDCI）MOD-SIG-052 planned 路径 `src/zephyr/signal_ashare/adaptive_conformal_tcp_rm_ddci.py` | **零代码** | 本文档 Phase 0 即 BM-SEL-14 的施工路径，落点须对齐 battle_map 登记，禁止另起目录 |

### 2.2 文档/设计层（已定稿的对接契约）

| 设施 | 位置 | 关键约定 |
|---|---|---|
| Kelly 密度主源+降级链 | 31 号 §2.3.2 | 密度 PDF 积分为主源；NaN/方差非正/样本<30/75% 区间覆盖率<60% → 降级历史源；第 5 项降级触发（密度 PDF 连续 20 日下行 miss 超 60 日 miss 率 P95 → Kelly 分数×0.5）已定型 |
| 分布感知调整 | 31 号 §2.3.3 | 偏度/峰度/VaR/CVaR 五路调整（只减不增为主）；当前代码实现 VaR/CVaR 两路 |
| Bayesian Kelly | 31 号 §3.8 | Phase 2 候选；κ=30（swing 级）+ f_max=0.15 上限已定施工参数 |
| Conformal Kelly | 30 号 §2.1 / 31 号 §2.3.2 | Phase 3 远期候选；核心实证"慢而稳 slow unweighted 最优，自适应反损 0.7-5.3pp 年化"；lockbox OOS 增长未保持（校准保持≠盈利保持） |
| RWC（Regime-Weighted Conformal） | 35 号 §4.17 / 36 号 §4.1 / 90 号 v1.12.0 | 暂缓 P2；TWC-first 最小集成路径；复用项目 regime 标签做相似性权重 |
| Conformal 五变体栈收敛（P-2） | 90 号 §待定问题 P-2 | **待用户裁定**：推荐方向②（slow unweighted + EWMA 标准化 + ACI 三层 ~140 行），RWC/COP 作压力期不达标升级 |
| Tail-Aware MDN | 90 号 v1.0.0 | skewed Student-t MDN 与打板"涨停→炸板"动力学原生匹配（mixed causal-noncausal 气泡动力学） |
| Lévy 家族 | 90 号 v1.3.0 | DeepLévy（α-stable+CFM）/ Lévy-Flow（VG/NIG flow，VaR Kupiec p=1.00，ES 低估仅 1.6%） |
| FCVE | 90 号 v1.17.0 / §10 | joint VaR-ES conformal（breach frequency+magnitude），Phase 2 远期候选 |
| 8 态预测暂缓 | 90 号 #7 v0.6.0 | A 股预测天花板 52-53% 实证；突破口在信息源非架构 |
| Conformal Prediction 覆盖保证层 | 10 号 §9.16.6 | B1 校准器数学保证层（mapie 库），Phase 4 待裁定——**与本文档 Phase 0 同源共用基础设施** |
| BM-BT-03-E 密度预测验证 | 11 号 §5 | CRPS/校准度验证框架（设计态），验证 12 维概率分布质量 |

### 2.3 盘点结论

1. **接口已预留、实现为零**：Kelly 链路（31 号）从设计到代码都为密度预测留好了位置（主源/降级双轨），密度预测模块本身（BM-SEL-13）零代码——**建设密度预测不是新增架构，是填充已设计空位**。
2. **风控侧已自足**：VaR（参数法+HS 取 max）+ ES（HS+POT/GPD）+ 回测（Kupiec/Christoffersen/GREM）已是业界正确姿势且 production——密度预测对风控是**第三路验证增强**，非补短板。
3. **regime 分桶输入现成**：4 态 HMM + ECE=4.2% 校准器是 Mondrian/RWC conformal 的天然 regime 权重来源。
4. **唯一需防误用**：`feedback_loop/evolution/conformal_prediction.py` 是运维域占位玩具，交易 conformal 须新建，禁止复用。

---

## 3. 第一性原理分析

### 3.1 密度预测的本质

交易决策的数学本质是**在不确定性下分配资本**。点估计 E[r] 只回答"期望赚多少"，分布 P(r) 额外回答"不确定性多大、尾部多厚、偏度方向"。下游四个消费者分别需要分布的不同切片：Kelly 要前两阶矩（μ/σ²），VaR/ES 要左尾分位数，止盈位要 75% 分位数，8 态派生要全分布积分。**一个条件分布层一次建模、多处复用**——这是密度预测的杠杆率所在。

### 3.2 为什么个人+100%AI 项目需要（或不需要）

**需要的理由（增量价值）**：
- 31 号已定密度 PDF 为 Kelly 主源——二值点估计（胜率 p/盈亏比 b）是降级方案，历史窗口在 regime 切换时滞后（浙商证券 2026-07 A 股实证建议 10-30 日短窗口）；分布层能捕捉偏度/峰度/厚尾，31 号 §2.3.3 分布感知调整（C10 偏度/峰度）只有密度 PDF 就绪后才能实现
- 2026 年范式证据：学术研究正从点预测转向分布预测（FutureQuant/Utility-Weighted Calibration）；TMMDN（多元 t-MDN）OOS Sharpe 统计显著优于 DCC-GARCH；清华高斯混合在中国市场 CRPS 胜 GARCH
- conformal 校准层（Phase 0）给"经验 ECE"升级为"有限样本覆盖保证"，与 10 号 §9.16.6 待裁定项同源

**不需要的理由（为何非必需）**：
- 现有组合（校准后 regime + 半 Kelly 硬上限 + VaR 取 max + POT/GPD + 四级回撤 Protocol）已是散户级前 1% 水平，四层独立防御栈在尾部场景下有效仓位已远低于半 Kelly 名义值（31 号 §2.3.1 Taleb 论点回应）
- 90 号 #7 已裁定 A 股次日方向预测天花板 52-53%——密度预测不改变方向预测的信息上限，只改变不确定性的表达质量；最激进消费场景（8 态派生）已暂缓
- 量化社区主流（qlib/Numerai/WorldQuant）2026 年仍以点预测为绝对核心，密度预测是"自己加模块"的差异化投入，不是行业标配补课

**结论**：密度预测对该项目是"从 80 分到 90 分"的高杠杆中期增强——值得做，但不阻塞任何现有闭环，启动时机由触发条件控制（§5.2）。

### 3.3 与 regime 12 态的关系（裁定问题 1 的第一性原理）

两者**正交**，维度不同：

| 维度 | regime 检测器（10 号） | 密度预测（本文档） |
|---|---|---|
| 回答的问题 | 市场处于什么状态（多谨慎） | 这只票明天收益分布长什么样（下多大注） |
| 输出空间 | 状态概率分布 P(r₁..r₄)（4 态+3 overlay） | 收益连续分布 P(r\|X) |
| 消费者 | 34 号 Shrinkage 风险节流 | 31 号 Kelly / 36 号 VaR / 42 号止盈 / 8 态派生 |
| 项目宪法分工 | 市场级风险节流（§3 约束三生死线） | 标的级参数供给（sleeve 内） |

regime 之上密度预测**有增量**（不同维度），但不是 regime 的替代品或升级版；反之 regime 概率校准（ECE=4.2%）不构成密度预测——一个是状态分类概率，一个是收益连续分布。

### 3.4 长远期战略（3 年视角）

- **工具链趋势**：conformal（MAPIE）已开箱即用；分位数回归/MDN 半天可搭（PyTorch/LightGBM）；扩散/Lévy-Flow 级生成密度预计 2027-2028 才有成熟库——**轻量路线现在做不过时，重型路线等工具链成熟再评估不迟**
- **需求趋势**：LLM 被实证系统性压缩尾部（Narrow Consensus），显式分布建模在 2026→2029 是差异化 alpha 来源而非标配——早建轻量层有复利价值
- **3 年后回看本决策**：轻量三步路线（conformal → Bayesian Kelly → 分位数密度）的每一步都是经典统计/ML，不因 AI 技术革命贬值；QNN 删除决策由 IBM 路线图自身（ML 应用 2033+）背书，3 年内大概率仍正确

---

## 4. 待讨论问题裁定

### 4.1 密度预测是否为当前阶段必需？——**非必需，定为中期增强（触发式启动）**

**候选方案**：① 立即建设；② 永不建设（regime+Kelly 标量已够）；③ 触发式中期建设。

**裁定：③**。理由见 §3.2/§3.3——有正交增量价值但非补短板；31 号架构已预留主源位置，建设=填空非新增。**启动触发条件**（全部满足）：
1. 首批策略 ≥50 trades track record（Kelly 参数校准样本量，31 号 §2.3.2 样本门控同源）
2. Phase 0 conformal 基础设施就绪（§5.1）
3. 36 号 VaR/ES 回测发现压力期失准证据（Kupiec/Christoffersen FAIL 记录）——无失准则密度第三路验证无痛点驱动

### 4.2 QNN 可行性——**从路线图删除，降级为理论关注项**

**候选方案**：① 保留为远期愿景阶段；② 降级为理论关注（移出路线图，登记重评触发条件）；③ 彻底删除。

**裁定：②**（2026-08 全网调研，证据如下）：

| 判据 | 证据 |
|---|---|
| **原理性判据（最重）** | 项目无量子硬件，只能经典模拟 QNN；经典模拟的 QNN = 带 2ⁿ 指数开销的经典模型——同样的 RTX 3090 算力投给经典密度模型（MDN/flow/分位数回归）**严格占优**。LANL 2026-04（Nature Comms+PRX Quantum）证明结构性两难：**可训练的 QNN 架构必然经典可模拟；经典不可模拟的必然 barren plateau 训练不动**——"不存在中间地带" |
| **时间线判据** | IBM 路线图（2026-01）把 ML 通用应用排在 Blue Jay 时代（2033+，2000 逻辑比特）；高盛 2026-04 测算实用金融应用需 800 万逻辑比特后**解散量子团队**；JPMorgan 维持研究但全部 PoC（225 资产 qReduMIS 仍是量子采样引导经典求解） |
| **证据判据** | 2026 年 QNN 未在任何实际 ML 任务证明经典优势；15+ 银行量子项目无一生产部署；学生团队 QNN 组合跑输等权基准；QCBM/QGAN 密度建模困于 10-20 比特单变量 toy 设定+mode collapse |
| **单机极限** | RTX 3090 24GB 实用上限 ~28-30 qubit state vector（2³⁰×16B≈17GB）；2026 消费级 GPU QML 研究典型规模 20 qubit/6 万参数/20 分钟每 epoch——该规模经典模型（LightGBM/小型 NN）秒级完成且效果更好 |

**为何不选③**：QML 是高投入学术方向，容错硬件有明确里程碑（IBM Starling 2029，200 逻辑比特），保留零成本关注项覆盖小概率突变。**重评触发条件**（任一满足，预计不早于 2030）：(a) ≥1000 逻辑比特容错机云可用；(b) 同行评审证据证明 QNN/QCBM 在真实金融数据上稳定优于强经典基线；(c) 出现打破 LANL 两难的架构（无 barren plateau 且经典不可模拟）。

**路线图逻辑修正**：原"参数化→QNN→非参数化"混淆两个正交维度——参数化/非参数化是**模型表达能力轴**，经典/量子是**计算基底轴**。QNN 不是非参数化方法的前身，嵌在递进链里是概念错误，应删非顺延。

### 4.3 校准阈值来源——**合理化修正后保留，验证方法明确**

| 原始阈值 | 裁定 | 依据 |
|---|---|---|
| 概率校准度偏离对角线<5% | **保留，口径明确为 ECE≤5%** | 与 10 号 B1 校准器门槛一致（两阶段校准后 ECE=4.2% PASS 已实证可达）；ECE 是分桶校准曲线对角的加权偏离，口径等价 |
| VaR 覆盖率误差<2%（风控消费前提） | **保留，验证设施现成** | 对齐 Basel 交通灯框架精神；36 号 §3.9 Kupiec（覆盖率）+Christoffersen（独立性）回测已 production——密度 VaR 直接复用，无需新建判定设施。补注：A 股涨跌停±10%/±20% 使尾部离散化，覆盖率评估须区分"连续体部分"与"涨跌停质量点"（§6.3 施工方案） |
| CRPS 为核心评估指标 | **保留，补双辅助指标** | CRPS 是概率预测标准严格评分规则（能源领域 GEFCom 2014 起主流化，股票领域 2024-2026 跟进）；但 CRPS 数值不直观——补**分桶覆盖率**（75%/90% 区间实际命中率，对齐 Conformal Kelly 74.8% vs 75% 口径）与 **Pinball loss**（分位数回归原生损失）作辅助。判定基线：CRPS 须优于 climatology 基准（长期经验分布，对齐 11 号 BM-BT-03-E B2 判定法） |
| 8 态概率 Phase4 后从 PDF 积分派生 | **降级为远期可选项** | 90 号 #7 已裁定 8 态预测暂缓（A 股方向预测天花板 52-53%）；PDF→8 态积分路径保留为"8 态若重启时的派生方式"，不构成密度预测的建设理由 |
| 半 Kelly 为硬上限（0.5×f*） | **真源在 31 号，本文档不重复** | 31 号 §2.3.1 已定稿（含 Taleb 胖尾批判的四层防御栈回应）；密度预测改变的是 μ/σ² 来源，不改变 0.5× 硬上限本身 |

### 4.4 与现有风控模块的关系——**前瞻分布层，正交叠加不替代**

密度预测融入四层防御栈的方式（全部"增强"非"替代"）：

| 模块 | 融入方式 | 性质 |
|---|---|---|
| 31 号 Kelly（MOD-POS-001） | 密度 PDF 积分 μ/σ² 替代历史降级源；`kelly_param_source` 切换 `historical_fallback→density_pdf`；四检查链降级逻辑不变 | 参数源升级 |
| 36 号 VaR/ES | 密度左尾分位数作**第三路**（与参数法/历史模拟三路取 max）；POT/GPD 尾部模块不动 | 增加一路验证 |
| 35 号回撤 Protocol | 密度区间下行 miss 率作 **drawdown dial 软预警**（Conformal Kelly 实证 MaxDD 27.7%→20.3%），与四级硬触发互补——软预警不等回撤实际发生 | 事前软预警补充 |
| 42 号卖出流程 | PDF 75% 分位数供止盈位计算（BM-SELL-03→MOD-SELL-004 planned）；已定降级（缺失→固定止盈），密度就绪后升级 | 参数源升级 |
| 30 号 FirmRiskAggregator | 无感（Kelly 参数来源变化对聚合器透明） | 不变 |
| 34 号 RegimeMetaAllocator | 无感（regime Shrinkage 与密度预测正交，§3.3） | 不变 |

---

## 5. 路线图裁定（六阶段审查 → 新三步路线）

### 5.1 原六阶段逐项裁定

90 号修订记录累积形成的路线（Phase 0 五变体栈 → Phase 0.5 轻量 Kelly → Phase 1 Tail-Aware MDN → Phase 1.5 Info-Entropic DL+GP → Phase 2 FCVE/Lévy-Flow/扩散 → QNN）逐项裁定：

| 原阶段 | 内容 | 裁定 | 理由（第一性原理+证据） |
|---|---|---|---|
| Phase 0 | Conformal 五变体栈（slow unweighted→EWMA→RWC→ACI→COP） | **采纳但收敛**——推荐 90 号 P-2 方向②（slow unweighted+EWMA 标准化+ACI 三层 ~140 行），**待用户裁定** | Conformal Kelly 实证"slow unweighted 最优，每加快自适应反损 0.7-5.3pp 年化"；EWMA 标准化把条件覆盖差距 0.134→0.040；ACI 修复 regime break 后欠覆盖（0.562→0.70-0.875，宽度代价仅 1.12-1.14×）——A 股政策市 regime break 频繁，ACI 有痛点驱动。RWC/COP 降级为压力期不达标时的升级（复用 regime 标签）。工程上 mapie 库离线计算，不占交易时段资源 |
| Phase 0.5 | Bayesian Kelly / RMSE Kelly | **采纳，Phase 2 触发** | 31 号 §3.8 已定（κ=30 swing 级+f_max=0.15；n_eff=κ 时精确等价半 Kelly，样本自适应）；闭式 ~20 行；Sukhov Monte Carlo：Bayesian Kelly 破产率 0.8% vs Half Kelly 4.2% |
| Phase 1 | LSTM+GMM → Tail-Aware MDN | **替换主路径，MDN 降为备选增强** | 主路径替换为**分位数回归轻量路径**（LightGBM quantile 7-9 分位数+样条插值 CDF，§6.3）——无 MDN 分量塌陷坑、与现有因子栈兼容、CPU 可训。Tail-Aware MDN（skewed Student-t，打板气泡动力学原生匹配）保留为 Phase 1 备选增强——当分位数路径 CRPS 不达标或需要完整 PDF 解析形式（8 态派生重启）时启用 |
| Phase 1.5 | Info-Entropic DL+GP（微分熵→Kelly，CNN-Transformer+GP 全栈） | **删除** | 重方案无实证背书：需 CNN-Transformer+GP 全栈（Exformer/QFCQT backbone 随删），而 Phase 0.5 轻量方案（Bayesian/RMSE Kelly）已覆盖其"不确定性→Kelly 收缩"核心价值（~20 行 vs 全栈）。90 号 v0.8.0 自己亦定位 Phase 0.5 为其轻量替代。复杂度超出硬边界收益比 |
| Phase 2 | FCVE / GPD / Lévy-Flow / 扩散 | **拆分**：GPD 移出（已施工）；FCVE/Lévy-Flow/扩散保留远期标注 | GPD/POT 已在 36 号 ES production（§2.1），重复登记删除。FCVE 保留 Phase 2 远期（36 号需 joint breach frequency+magnitude 控制时启用）。Lévy-Flow 保留远期（VG-flow VaR Kupiec p=1.00 证据强，但 NF-GARCH 作者自评"效应量温和 vs 实现成本"——等工具链成熟）。扩散模型保留远期（CUHK 2026-04 A 股因子条件扩散已验证，但无产品化工具链，且其增量价值主要在多资产联合尾部——单账户日频场景边际收益低；2027-2028 重评）。Bayesian GP 尾部外推保留 Phase 3+（90 号 v1.11.0） |
| QNN | 量子神经网络 | **删除**（§4.2） | 原理性严格劣势+IBM 路线图 ML 应用 2033+ |

### 5.2 新路线图（裁定后）

```
Phase 0   Conformal 校准层（slow unweighted + EWMA 标准化 + ACI，~140 行，mapie）
          触发：10 号 §9.16.6 Phase 4 评估时同源建设   【待用户裁定：90 号 P-2 方向②】
          ↓
Phase 0.5 Bayesian Kelly（κ=30 闭式收缩，~20 行）+ RMSE Kelly
          触发：首批策略 ≥50 trades（31 号 §3.8 Phase 2 候选已定）
          ↓
Phase 1   分位数回归密度（LightGBM quantile 9 分位数 + 样条 CDF + 涨跌停质量点）
          触发：§4.1 三条件全满足
          备选增强：Tail-Aware MDN（打板气泡动力学/完整 PDF 需求重启时）
          ↓
Phase 2+  远期标注（不施工）：FCVE joint VaR-ES / Lévy-Flow / 扩散模型 / Bayesian GP
          重评：工具链成熟或 36 号痛点驱动时逐项评估
          
已删除：Phase 1.5 Info-Entropic DL+GP（轻量方案已覆盖）/ QNN（§4.2）/ GPD 阶段（36 号已施工）
```

### 5.3 路线图合理性论证（为何三步够用）

第一性原理：下游消费者需要的分布信息精度有上限——Kelly 要前两阶矩（对分布形状不敏感），VaR 要左尾两个分位数（1%/5%），止盈位要 75% 分位数，8 态已暂缓。**9 个分位数+conformal 校准已覆盖全部现存消费需求**；更重的生成式模型（MDN 全解析 PDF/flow/扩散）服务的场景（8 态重启/多资产联合尾部/奇异期权定价）在本项目要么已暂缓、要么不存在。路线收敛到三步是"需求驱动删法"，非能力不足妥协。

---

## 6. 采纳项施工方案（设计态，触发后施工）

> 三项均为远期触发式建设，当前不落码。本节定义触发条件、文件位置、集成点、验证方法。

### 6.1 Phase 0：Conformal 校准层【待用户裁定 90 号 P-2】

- **触发条件**：90 号 P-2 用户裁定方向② + 10 号 §9.16.6 Phase 4 评估窗口（两者同源共用基础设施）
- **施工内容**（~140 行 + 测试）：
  1. 新建 `src/zephyr/signal_ashare/adaptive_conformal_tcp_rm_ddci.py`（**对齐 battle_map BM-SEL-14-A / MOD-SIG-052 已登记 planned 路径**，信号域平铺约定；交易域 conformal，**禁止复用** `feedback_loop/evolution/conformal_prediction.py` 运维玩具，亦禁止另起 regime/calibration 目录）
  2. 三层栈：slow unweighted rolling 分位数（窗 252 交易日）→ EWMA 标准化 conformity score（修复 conditional coverage）→ ACI（自适应 γ，regime break 后欠覆盖修复）；与 BM-SEL-14-A 已登记的 TCP-RM/DDCI 方向同族（自适应非平稳覆盖），施工时以 ACI 为 baseline、TCP-RM/DDCI 为增强评估
  3. 与 10 号 B1 两阶段校准器叠加（非替代）：Stage 1+2 概率校准，Stage 3 conformal 集合/区间保证
- **集成点**：10 号 regime 概率输出（集合保证）；31 号 §2.3.2 第 4/5 项降级检查（75% 区间覆盖率、下行 miss 率的统计来源）
- **验证**：walk-forward 覆盖率（边际 ≥90% 名义 + 高波动桶条件覆盖差距 <0.05）+ 区间宽度对比高斯基线（文献基准：窄 11.4%）+ regime break 后 60 步覆盖恢复（ACI ≥0.70）
- **风险与缓解**：校准集样本不足（<100 预测误差）→ 积累期只报告不消费；A 股涨跌停使 score 离散化 → 分桶评估区分连续体/涨跌停样本

### 6.2 Phase 0.5：Bayesian Kelly

- **触发条件**：首批策略 ≥50 trades track record（31 号 §3.8 已定 Phase 2 候选）
- **施工内容**（~20 行 + 测试）：`position_sizing_engine.py` 新增 `_compute_bayesian_kelly_fraction(p̄, b, n_eff, κ=30)`，收缩因子 `n_eff/(n_eff+κ)`，`f_max=0.15` 上限与 §2.4.1 单票 8% 取最小；Beta 后验随每笔交易更新（α+=win, β+=loss）
- **集成点**：替换/并存 `_compute_kelly_fraction` 的固定 0.5× 系数（A/B 对比后择一）；输出 `kelly_adjustments` 增记 `shrinkage_factor=n_eff/(n_eff+κ)` 供归因
- **验证**：OOS 增长+回撤+破产率 Monte Carlo（对齐 Sukhov 基准：破产率 0.8% vs Half Kelly 4.2%）；A/B 期间固定半 Kelly 为对照组
- **风险与缓解**：胜率估计本身含噪声（A 股 52-53% 天花板）→ κ=30 先验强度已按 swing 级标定；连续亏损期后验深收缩是自然行为非 bug

### 6.3 Phase 1：分位数回归密度（轻量主路径）

- **触发条件**：§4.1 三条件全满足（50+ trades / Phase 0 就绪 / 36 号压力期失准证据）
- **施工内容**（设计要点）：
  1. 新建 `src/zephyr/signal_ashare/quantile_density_model.py`（**BM-SEL-13 落位**，对齐信号域 `signal_ashare/` 平铺约定；登记 capability_canonical_file_registry + module_translation_registry + ARCH 条目）
  2. LightGBM quantile，9 分位数 {1%,5%,10%,25%,50%,75%,90%,95%,99%}，pinball loss；输入复用 L1 因子工厂特征（21 号 §3.3 分布特征工程：滞后项/交互项/滚动统计量/Signature）
  3. 样条插值 9 分位数→CDF（单调性约束）
  4. **A 股涨跌停 censored-mixture 改造（文献空白，自建）**：CDF 在 ±10%/±20%（按板块/ST 状态）加离散质量点，质量=该股历史涨跌停条件频率；T+1 隔夜跳空不可对冲 → 左尾质量对仓位权重上调
  5. 输出接口：`predict_cdf(symbol, X) → {quantiles, cdf_spline, limit_up_mass, limit_down_mass}`；μ/σ² 数值积分供 31 号（切换 `kelly_param_source=density_pdf`）；1%/5% 分位数供 36 号第三路取 max
- **集成点**：31 号 §2.3.2 主源切换（四检查链降级保留）；36 号 VaR 第三路；11 号 BM-BT-03-E CRPS 验证框架
- **验证**：CRPS < climatology 基准（11 号 B2 判定法）+ 分桶覆盖率（75%/90%）+ ECE≤5%（§4.3）+ Kupiec/Christoffersen 复用 36 号设施 + walk-forward OOS
- **风险与缓解**：① 方向预测天花板 52-53%——密度预测不承诺超越信息上限，只改善不确定性表达，验证标准对准"校准质量"非"方向准确率"；② 涨跌停质量点频率估计在小样本不稳 → 个股历史<3 次涨跌停时用板块先验收缩；③ LightGBM 分位数交叉（非单调）→ 插值前强制排序+单调样条

### 6.4 远期标注项（不施工，仅登记重评条件）

| 项 | 重评条件 |
|---|---|
| Tail-Aware MDN（Phase 1 备选增强） | 分位数路径 CRPS 不达标 / 8 态派生重启需解析 PDF |
| FCVE（joint VaR-ES） | 36 号需 joint breach frequency+magnitude 控制（Basel 式联合回测 FAIL 时） |
| Lévy-Flow（VG/NIG flow） | flow 工具链产品化成熟 + VaR Kupiec/ES 低估痛点驱动 |
| 扩散模型（A 股条件扩散） | 2027-2028 工具链成熟后重评；CUHK 论文为锚点 |
| Bayesian GP 尾部外推 | 90 号 v1.11.0 登记，Phase 3+ |
| QNN | 已删（§4.2 三触发条件，预计不早于 2030） |

---

## 7. 过度工程审查（判定基准：system_charter §2 硬边界 + 1 人多 AI 并发）

| 项 | 判定 | 理由 |
|---|---|---|
| Phase 0 conformal 三层栈（~140 行） | ✅ 不过度 | wrapper 模式+mapie 库；离线盘后计算不占交易时段资源；与 10 号 §9.16.6 同源共用不重复建设；有明确痛点（经验 ECE→数学覆盖保证） |
| Phase 0.5 Bayesian Kelly（~20 行） | ✅ 不过度 | 闭式 O(1)；替代固定系数非新增架构；κ=30 已标定 |
| Phase 1 分位数回归密度 | ✅ 不过度 | LightGBM CPU 可训（无 GPU 显存压力，远低于约束二 21.6GB 上限）；单模型非栈；9 分位数覆盖全部现存消费需求（§5.3） |
| Tail-Aware MDN 备选 | ✅ 远期标注保留 | 显式标注 Phase 1 备选增强，非当前施工 |
| Phase 2+（FCVE/Lévy-Flow/扩散/Bayesian GP） | ✅ 远期标注保留 | 全部显式标注远期+重评条件，符合"已显式标注远期愿景不算过度工程"规则 |
| ~~Phase 1.5 Info-Entropic DL+GP~~ | ❌ 已删除 | CNN-Transformer+GP 全栈超出 1 人维护带宽，核心价值被 Phase 0.5 覆盖（§5.1） |
| ~~QNN~~ | ❌ 已删除 | 经典模拟严格劣于同算力经典模型，任何时点都更差（§4.2） |
| ~~GPD 阶段~~ | ❌ 已移除 | 36 号已施工，重复登记 |

**审查结论**：采纳三步均为轻量经典方法（合计 ~200 行+LightGBM 模型），无 GPU 硬边界冲突，无 1 人维护带宽冲突；重型项全部远期标注或删除。

---

## 8. 关联

- [00_index_trading_decision](00_index_trading_decision.md) G16-G18（风控落地）
- [10_regime_detector_spec](10_regime_detector_spec.md)（regime 检测器，§9.16.6 Conformal 覆盖保证层同源）
- [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md)（BM-BT-03-E CRPS 验证框架）
- [21_stock_selection_engine](21_stock_selection_engine.md)（L1 分布特征工程输入；L2-C Survival/密度预测远期位）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md)（Conformal Kelly Phase 3 远期候选；四层防御栈）
- [31_position_sizing](31_position_sizing.md)（Kelly 密度主源+降级链 §2.3.2；Bayesian Kelly §3.8）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（§4.17 RWC；drawdown dial 软预警对接）
- [36_var_es_monitoring](36_var_es_monitoring.md)（VaR/ES 现状+§4.1 CRC 远期登记；POT/GPD 已施工）
- [42_sell_flow](42_sell_flow.md)（止盈位消费 PDF 75% 分位数，BM-SELL-03/MOD-SELL-004）
- [90_methodology_open_questions](90_methodology_open_questions.md)（§10 密度预测历史调研沉淀；P-2 conformal 变体收敛待用户裁定）

---

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.1 | 文件名 discussion_021_density_prediction.md → 91_density_prediction.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 0.1.2 | 文档头统一：title/H1 去"讨论稿："前缀，scope 归一为 07_trading_decision_architecture；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-12 | 1.0.0 | 骨架（45 行）→ 完整讨论文档并升级 active：① §2 已施工设施盘点（通用规则 #11：Kelly 接口已预留/BM-SEL-13 零代码/feedback_loop conformal 玩具防误用）；② §3 第一性原理（密度预测=标的级分布层，与 regime 市场级状态正交；四消费者一次建模多处复用）；③ §4 四问题裁定（非必需但中期增强触发式启动 / **QNN 从路线图删除降级理论关注**——经典模拟严格劣势+LANL 两难+IBM ML 2033+ / 校准阈值合理化保留 / 前瞻分布层正交叠加不替代）；④ §5 六阶段裁定→新三步路线（Phase 0 conformal 收敛待用户裁定 90 号 P-2 / Phase 0.5 Bayesian Kelly / Phase 1 分位数回归轻量路径；删除 Phase 1.5 Info-Entropic DL+GP 与 QNN，GPD 阶段移除因 36 号已施工）；⑤ §6 施工方案（三采纳项触发条件/文件位置/集成点/验证/风险）；⑥ §7 过度工程审查全过；⑦ 吸收 90 号 v0.4.0-v1.17.0 全部"91 号同步"悬空引用内容（§1.2 历史漂移说明） | 架构审查：第一性原理 + 2026-08 全网调研（密度预测=高杠杆中期增强走轻量路线；QNN 单机严格劣势删除）+ 90 号修订记录悬空引用回填（91 号版本号自此与内容同步）。title 去 QNN 更名"密度预测与远期演进路线"（00_index §3/§10 描述行待同步） |
| 2026-08-12 | 1.0.1 | 第二轮交叉引用对齐修正：① §1.3 消费者补第四处——42 号卖出流程止盈位消费 PDF 75% 分位数（BM-SELL-03/MOD-SELL-004 planned，降级=固定止盈，battle_map_07 登记）；② §2.1 盘点补 BM-SEL-13/BM-SEL-14 battle_map_05 登记状态（含 MOD-SIG-052 planned 路径）；③ §6.1 Phase 0 落点改 `src/zephyr/signal_ashare/adaptive_conformal_tcp_rm_ddci.py`（对齐 BM-SEL-14-A/MOD-SIG-052 登记，禁另起 regime/calibration 目录）；④ §6.3 Phase 1 落点改 `src/zephyr/signal_ashare/quantile_density_model.py`（信号域平铺约定，原规划 signals/density 目录不存在）；⑤ §4.4 融入表补 42 号行；⑥ var_backtester.py 补全路径 | 复审发现：battle_map_05/07 已登记 BM-SEL-13/14 环节与 MOD-SIG-052 planned 路径，施工方案落点须对齐 battle_map 真源而非另拟目录；卖出流程是密度 PDF 已登记消费者不可遗漏 |
