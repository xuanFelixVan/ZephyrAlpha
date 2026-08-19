---
ttl: permanent
doc_type: architecture_view
title: 首批 3 策略定义
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.3.2"
date: 2026-08-15
topic: first_batch_strategies
scope: 07_trading_decision_architecture
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：三策略 alpha 信号链组件全部 production 实证——打板四引擎（signal_ashare/short_term_stock_selector / youzi_relay_emotion_engine / quant_short_term_strength_engine / dual_engine_fusion_decision_engine）、因子工厂（factor/ 合成/评估/治理全链）、事件底座（news_collector + 新闻三源 + dragon_tiger 双表）；三 sleeve 载体 position/core/{strategy_book, firm_risk_aggregator, budget_change_handler}.py 与 pf_alloc/core/regime_meta_allocator.py 均已成产落码（注：§2.7 所述"budget_change_handler 骨架"与"RegimeMetaAllocator design 骨架"两状态已过时——前者经 33 号批次（AI-BGT-001）落成完整实现，后者经 34 号批次（AI-REGIME-001）落成 v1.0.0 + 55 测试套件）。
>
> **最终成果**：首批 3 策略（打板/多因子/事件驱动）架构定义定稿（active v1.3.2）——差异化矩阵 + 选股池交集处理原则 + intake/incubation 灰度四阶段判据 + charter §3 对齐裁定。
>
> **未做事项及原因**：① 3 个 sleeve 策略类（daban/multifactor/event_driven 组装策略类）未施工——pf_core/strategies/ 实证仅 __init__.py 空壳（仅 DefaultEquityStrategy wrapper），"组件就绪→首批上线"最后一公里未闭环，按 §6 登记待 G08/G09/G10 细节定型后经 G05 标准接口施工；② charter §3 约束二措辞物理修订未做（"按市场状态切换权重"→"按市场状态做风险节流"，§5 待裁定-1，04 域 owner 待认领）；③ convergence_window 校准/容量精确测算/相关性实测为待实盘或归 G07/G08-G10 的依赖项。

# 首批 3 策略定义

> 本备忘定义多策略并发架构（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) Model A）下首批上线的 3 个策略及其特征。
> 性质：永久态讨论记录，可随项目演进而修订。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 路线图定位见 [00_index_trading_decision](00_index_trading_decision.md) G04（L1·Alpha 选股层，⭐推荐起点，P0）。

## 1. 背景

### 1.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT 通道，T+1 结算，不能做空，涨跌停限制）
- 多策略并发架构已定稿为 Model A（独立账本 + firm 聚合 + regime 风险节流），见 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md)
- regime 检测器由另一 AI 负责（[10_regime_detector_spec](10_regime_detector_spec.md)），与本主题正交——regime 只做 Shrinkage 风险节流，不参与选股
- [30_multi_strategy_concurrency §6.1](30_multi_strategy_concurrency.md) 开放问题：5 个候选策略不可能齐平，弱策略拖累归因清晰度，建议首批上 3 个最自信的，跑 3 个月有 track record 后再加第 4、5 个

### 1.2 核心问题
首批上线哪 3 个策略？每个策略的 alpha 信号来源、换手率、容量、选股池、持仓周期、与 regime 的关系如何定义？三策略间如何差异化以为 G07 相关性验证做准备？

### 1.3 约束条件
- A 股不能做空 → 对冲式优化失效，统一框架走"求和+裁剪"而非 MVO（[30_multi_strategy_concurrency §1.3/§3.1](30_multi_strategy_concurrency.md)）
- T+1 结算 → 策略难以日内翻转，独立账本更顺
- 打板容量极小（单票几万~几十万）→ 必须小账本独立运行（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）
- 情绪周期是所有短周期策略的共同隐形驱动 → 策略间相关性可能高于直觉（[30_multi_strategy_concurrency §1.3/§6.2](30_multi_strategy_concurrency.md)）
- AI 开发 → 故障隔离与归因清晰度是生存项（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）

### 1.4 与 charter §3 方法论约束的对齐（关键）

> **本节是本次讨论的关键产出**：澄清 [system_charter §3](../../04_architecture_principles_decisions/system_charter.md) 投资哲学与本批策略定义的关系，消除 charter 与 30_multi_strategy_concurrency 之间的措辞治理债。

**矛盾诊断**：charter §3 约束二明确"不走多策略平台派（Citadel/Millennium 式独立 PM 并行），走统一框架派"；而 30_multi_strategy_concurrency §4.3 写"Citadel/Millennium 的 pod 模型本质就是 A"——字面直接冲突。

**实质裁定**：Model A **不是** Citadel pod 式，是 Morwane 式"统一风险框架（firm 求和+裁剪+Kelly）+ 独立 alpha sleeve + regime 风险节流"——它正是 charter 约束二"统一框架派"的正确实现。Citadel pod = 几十个互不相关独立 PM + 被动风险聚合 + PM 间不共享不协同；Model A = 统一 firm 层 + 统一 StrategyBook 接口 + 统一信号工厂（G05）+ 少而精（3-5 个）差异化 sleeve。30_multi_strategy_concurrency §4.3 的 pod 类比是误标，已由其 v1.4.0 修正（§5 待裁定-2 已落地）。

**charter §3 约束逐条对齐**：

| charter 约束 | 要求 | 本批3策略如何满足 |
|---|---|---|
| 约束二·统一框架派 | 统一框架 + 少而精，非几十个互不相关独立 PM | 统一 firm 风险框架下 3 个差异化 sleeve；非 pod 式（见上裁定） |
| 约束三·regime 生死线 | regime 准确识别是前提 | 三策略选股**不读** regime 输出；regime 只做 Shrinkage 风险节流（非 alpha 择时/权重切换）。regime 准确性由另一 AI 负责（G02/G03），与本主题正交 |
| 约束四·三维度解耦 | 策略=选股信号×组合权重×执行方式，独立优化 | 本讨论**只定义选股信号维度**（what）；组合权重（how much）在 G12，执行方式（how）在 G19/G20，不越界 |
| 约束五·少而精+差异性 | 新增策略须论证差异性（信号源/持仓周期/市场状态适配） | §2.5 按 charter 三维论证三策略差异性 |

> **charter §3 约束二"按市场状态切换权重"已 Morwane 实证否决**（[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md)：regime 做 alpha 择时 Sharpe 1.04→0.87，做风险节流 Sharpe 1.43 + MaxDD -14.2%→-10.3%）。charter 措辞待修订为"按市场状态做风险节流"（见 §5 待裁定-1）。

## 2. 决策：首批3策略 = 打板 + 多因子 + 事件驱动

### 2.1 候选清单澄清

[30_multi_strategy_concurrency §1.1](30_multi_strategy_concurrency.md) 原列 5 候选：价值反转 / 动量趋势 / 事件驱动 / 打板 / 主升龙头。但 §6.1 首批候选组合用"打板+多因子+事件驱动"，其中"多因子"不在 5 候选清单。

**裁定（选项 c）**：
- **主升龙头并入打板策略内部**——主升龙头（[battle_map_05](../battle_map/battle_map_05_stock_selection.md) BM-SEL-25-C-1 主升龙头决策类）本质是打板双引擎融合链的最强决策输出，与打板高度重叠，作为独立策略会产生 alpha 重叠（违反 charter 约束五）
- **多因子作为独立横截面选股 sleeve 补入候选清单**——承担"承载主资金 + 低换手 + 大容量"的压舱石角色，是统一框架不可或缺的低频基石
- 5 候选清单更新为：**价值反转 / 动量趋势 / 事件驱动 / 打板 / 多因子**（去掉主升龙头，新增多因子）

首批 = 打板 + 多因子 + 事件驱动。价值反转/动量趋势留 G11 第二批次（首批 track record 后）。

### 2.2 策略A：打板（daban）

> 定位：高换手、小容量、情绪驱动的短线 sleeve。必须小账本独立运行（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）。

| 维度 | 定义 |
|---|---|
| **alpha 信号来源** | 游资接力情绪 + 连板梯队结构 + 双引擎融合。复用已建打板链 [battle_map_05](../battle_map/battle_map_05_stock_selection.md) BM-SEL-22（短线评分卡7维）/ BM-SEL-23（游资接力6因子+情绪周期4+1阶段）/ BM-SEL-24（量化强度6维）/ BM-SEL-25（双引擎融合6类决策，定位为打板策略内部融合，[30_multi_strategy_concurrency §7.3](30_multi_strategy_concurrency.md)） |
| **换手率特征** | 高。convergence_window = 1-2 天（[30_multi_strategy_concurrency §6.4](30_multi_strategy_concurrency.md)）。Tier 1+2 通常 1-2 天自然收敛，Tier 3 不触发（[30_multi_strategy_concurrency §2.4](30_multi_strategy_concurrency.md)） |
| **容量上限** | 极小。单票几万~几十万（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）。sleeve 整体容量小，必须小账本独立运行，不可承载主资金 |
| **选股池范围** | 连板梯队标的（主板 + 创业板涨停标的）。排除 ST / *ST / 退市风险警示 / 涨跌停流动性失效标的。具体池生成规则在 G08 打板细节讨论 |
| **持仓周期** | 1-3 天。T+1 约束下以打板次日卖出为主，连板晋级者持有至分歧/破板 |
| **与 regime 关系** | 选股**不读** regime 输出，只收 budget 数字。打板内部的"情绪周期4+1阶段定位"（BM-SEL-23-B：冰点/反核/主升/疯狂/退潮）是 **sleeve 内 alpha 择时信号**，决定买卖什么；与 regime 灰度概率分布**正交**（regime 决定多谨慎，不决定买卖什么）。边界已定型：[28_sentiment_cycle_trading §3.1/§3.4](28_sentiment_cycle_trading.md) |

### 2.3 策略B：多因子（multifactor）

> 定位：低换手、大容量、横截面选股的压舱石 sleeve。承载主资金。

| 维度 | 定义 |
|---|---|
| **alpha 信号来源** | 横截面因子打分。复用已建因子工厂 [battle_map_05](../battle_map/battle_map_05_stock_selection.md) BM-SEL-02（因子计算/注册表/IC-IR评估/衰减监控/多因子合成/治理生命周期）。因子覆盖基本面 + 技术面 + 资金面三维。具体因子组合方式（打分/IC加权/正交化）在 G09 多因子细节讨论 |
| **换手率特征** | 低。convergence_window = 3-5 天（[30_multi_strategy_concurrency §6.4](30_multi_strategy_concurrency.md)）。Tier 1+2 给时间，Tier 3 兜底防死扛（[30_multi_strategy_concurrency §2.4](30_multi_strategy_concurrency.md)） |
| **容量上限** | 较大。可承载主资金，是统一框架的低频基石。具体容量测算在 G09 |
| **选股池范围** | 全市场沪深 A 股。排除 ST / *ST / 次新（上市 <60 天）/ 日均成交额低于流动性阈值的标的。具体过滤规则在 G09 |
| **持仓周期** | 5-20 天（中周期）。按因子衰减周期调仓 |
| **与 regime 关系** | 选股**不读** regime 输出，只收 budget 数字。纯横截面选股，不依赖 regime 做择时。"市场状态适配"由 PerformanceScore 后验捕获（[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md)：多因子在趋势态表现好→滚动 Sharpe 上升→有机获得更多 budget，无需 regime 前瞻下注） |

### 2.4 策略C：事件驱动（event_driven）

> 定位：中换手、中容量、离散事件冲击的 sleeve。

| 维度 | 定义 |
|---|---|
| **alpha 信号来源** | 离散事件冲击。事件源：公告 / 新闻 / 龙虎榜 / 盘中异动。复用 [battle_map_05](../battle_map/battle_map_05_stock_selection.md) BM-SEL-27（盘中实时事件处理）。事件分类（业绩/并购/政策/突发）与冲击衰减曲线在 G10 事件驱动细节讨论。news_data 多源情绪接入在 G10 |
| **换手率特征** | 中。convergence_window = 2-3 天（[30_multi_strategy_concurrency §6.4](30_multi_strategy_concurrency.md)） |
| **容量上限** | 中等。介于打板（小）与多因子（大）之间。具体测算在 G10 |
| **选股池范围** | 事件触发标的（非固定池）。由事件源动态生成候选，排除 ST / 流动性失效标的。具体事件→选股映射在 G10 |
| **持仓周期** | 2-10 天（视事件类型与冲击衰减曲线）。实证依据：事件后 day 0-5 为风险调整收益 rising phase（RVR 较 decay phase 高 9.5x），day 6-15 进入衰减——故持仓以 rising phase 为主，decay phase 兜底退出（[Beyond the Event Horizon 2025](https://www.preprints.org/manuscript/202506.0079)） |
| **与 regime 关系** | 选股**不读** regime 输出，只收 budget 数字。事件触发逻辑不依赖 regime（正交成立）；但事件冲击的**衰减速度**是 regime-dependent 的（危机期信号集中在短-中 horizon，宏观不确定性期扩散窗口延长，[Yukka 2026](https://cdn.prod.website-files.com/66b4f3430903efa023fe741b/69fdded32f3d7e02f17ff3f8_Sentiment%20Decay%20&%20Source%20Selection%20in%20Global%20Equity%20Markets%20-%20White%20Paper.pdf)），此衰减速度作为 sleeve 内部参数由 PerformanceScore 后验捕获，不破坏正交。需警惕：事件驱动与打板都受情绪周期隐形驱动（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)），两者相关性可能高于直觉，留给 G07 实测验证 |

### 2.5 三策略差异化矩阵（charter 约束五差异性论证）

> 按 charter §3 约束五要求的"信号源 / 持仓周期 / 市场状态适配"三维论证。本矩阵是 G07 相关性验证（[30_multi_strategy_concurrency §6.2](30_multi_strategy_concurrency.md)，施工前必做）的输入。

| 维度 | 打板 | 多因子 | 事件驱动 |
|---|---|---|---|
| **信号源** | 游资接力情绪 / 连板结构 | 横截面因子打分 | 离散事件冲击 |
| **信号频率** | 盘中实时 | 盘后日频 | 事件触发不定期 |
| **持仓周期** | 1-3 天（短） | 5-20 天（中） | 2-10 天（中短） |
| **换手率** | 高（1-2天收敛） | 低（3-5天收敛） | 中（2-3天收敛） |
| **容量** | 小（几万~几十万） | 大（承载主资金） | 中 |
| **选股池** | 连板梯队（窄） | 全市场（宽） | 事件标的（动态） |
| **市场状态适配** | 主升/疯狂态强；退潮态弱（情绪周期驱动） | 趋态势强；震荡态弱（后验 PerformanceScore 捕获） | 视事件类型，与 regime 弱相关 |
| **相关性预期** | 与多因子低；与事件驱动**可能偏高**（情绪隐形驱动） | 与两者低 | 与打板**可能偏高** |

**差异化结论**：三策略在信号源/持仓周期/换手率/容量/选股池五维均不同，alpha 来源正交。**唯一风险点**：打板与事件驱动都受情绪周期隐形驱动（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)），相关性可能高于直觉——这是 G07 施工前必测项。若 G07 实测各阶段相关性 >0.6，"多策略实为情绪 beta 穿多件衣服"，需重新审视策略组合（[30_multi_strategy_concurrency §6.2](30_multi_strategy_concurrency.md)）。

### 2.6 三策略选股池交集与冲突标的处理（接口指引）

> 三策略选股池有天然交集可能（多因子=全市场，打板=连板梯队窄池，事件=动态事件池）。本节声明交集处理原则，具体规则留给 G13 FirmRiskAggregator。

- **低交集设计**：打板=连板梯队窄池（高换手、容量小）；多因子=全市场（打板标的可在多因子池中存在，但受容量约束与因子打分自然边缘化，不构成主力持仓）；事件=动态事件池（事件触发即生即灭）。三者主力持仓域天然分离
- **冲突场景**：同一标的同时被多策略选中（如某连板股既进打板池又因事件进事件池）。处理原则：**按 sleeve 独立账本叠加，不强制去重**——每个 sleeve 独立下自己的单，由 firm 层（[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md) MOD-POS-021）裁剪控总风险敞口。具体冲突标的净额/优先级规则在 G13
- **此低交集设计是 G07 相关性验证的前置假设**：若 G07 实测选股池交集率过高（如三策略持仓重合 >20%），需重新审视差异化是否成立

### 2.7 已施工设施盘点（通用规则 #11）

> 全面扫描三策略 alpha 信号链的已建设施（2026-08-12 核验），明确"哪些已能用、哪些是缺口"，作为回填 why 与施工排序的依据。

| 链 | 环节 | 设施 | 状态 |
|---|---|---|---|
| 打板 | BM-SEL-22 短线评分卡（7维+强庄股） | `signal_ashare/short_term_stock_selector.py` + `institutional_behavior_analyzer.py` | ✅ production |
| 打板 | BM-SEL-23 游资接力情绪周期（6因子+4+1阶段） | `signal_ashare/youzi_relay_emotion_engine.py` | ✅ production |
| 打板 | BM-SEL-24 量化短线强度（6维+A~E评级） | `signal_ashare/quant_short_term_strength_engine.py` | ✅ production |
| 打板 | BM-SEL-25 双引擎融合（60/40基准+情绪自适应+6类决策） | `signal_ashare/dual_engine_fusion_decision_engine.py` | ✅ production |
| 多因子 | BM-SEL-02 因子工厂（计算/注册表/IC-IR/衰减/合成/治理） | `factor/`（ic_ir_calc、multifactor_synthesis、factor_optimization、momentum/value_factor、alpha_signal_pipeline、governance/） | ✅ production |
| 事件驱动 | BM-SEL-27 盘中实时事件处理 | `signal_ashare/intraday_buy_sell_point_analyzer.py` 等 | ✅ production（news_data 多源接入未完成，G10） |
| 三 sleeve 载体 | StrategyBook / FirmRiskAggregator / BudgetChangeHandler | `position/core/`（MOD-POS-020/021/022） | ✅ production（[30 §7.2](30_multi_strategy_concurrency.md)：54/47 测试） |
| firm 资金分配 | RegimeMetaAllocator | `pf_alloc/core/regime_meta_allocator.py` | ⚠️ design 骨架（C1 验证已通过，参数待首批 3-6 月 PnL 校准，第二阶段上线） |
| **3 策略 sleeve 策略类** | daban / multifactor / event_driven 组装策略类 | `pf_core/strategies/` | ❌ **缺口：目录为 re-export 空壳**（仅 DefaultEquityStrategy wrapper），3 个 sleeve 策略类未施工 |

**关键缺口与 why**：三策略的"信号链组件"（打板四引擎 / 因子工厂 / 事件处理）均 production，但把组件组装为 StrategyBook sleeve 的**策略类代码**未落地——这是从"组件就绪"到"首批上线"的最后一公里。组装依赖 G08/G09/G10 细节讨论定型与 G05 选股引擎标准接口（21 号），在此之前本文档的 3 策略定义停留在"架构定义已闭环、代码实例未闭环"状态。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-21-A | 策略引擎 | §2 首批 3 策略 sleeve 定义（§2.2-§2.4 策略 A/B/C + §2.7 已施工设施） | production 已建 |
| BM-SEL-21-F | 量化策略集 | §2 策略集成员与权重定义 + §4.4 intake/incubation 灰度门禁（ABS001 上线门禁 `abs001_gate.py` 由 25 号承载） | production 已建 |

## 3. 考虑过的替代方案

### 3.1 主升龙头作为独立策略 —— 拒绝
- **拒绝理由**：主升龙头（BM-SEL-25-C-1）本质是打板双引擎融合链的最强决策输出，与打板高度重叠。作为独立策略会产生 alpha 重叠，违反 charter §3 约束五"禁止堆砌相似策略制造多策略假象"
- **处置**：并入打板策略内部，作为打板 sleeve 的最高优先级决策类（P0）

### 3.2 价值反转 / 动量趋势进首批 —— 拒绝（暂缓）
- **拒绝理由**：首批应上"最自信"的 3 个（[30_multi_strategy_concurrency §6.1](30_multi_strategy_concurrency.md)）。打板链已建（BM-SEL-22~25 production）、因子工厂已建（BM-SEL-02 production）、事件处理已建（BM-SEL-27 production），三者均有作战地图支撑，置信度最高。价值反转/动量趋势需额外研究带宽，且与多因子同属横截面选股，首批同上会稀释归因清晰度
- **处置**：留 G11 第二批次，首批 3 策略跑 3 个月有 track record 后再讨论（[30_multi_strategy_concurrency §6.1](30_multi_strategy_concurrency.md)）

### 3.3 首批只上 1-2 个策略 —— 拒绝
- **拒绝理由**：单策略无分散，违反 Model A 多 sleeve 自然叠加的架构价值（[30_multi_strategy_concurrency §2.3](30_multi_strategy_concurrency.md)）。2 策略分散不足。3 策略是少而精与分散化的平衡点，且覆盖高/低/中三档换手率与容量，为 firm 层风险聚合提供差异化 sleeve

### 3.4 "多因子统指价值反转+动量趋势"（选项 b） —— 拒绝
- **拒绝理由**：价值反转与动量趋势是两种不同 alpha（价值=反转均值回归，动量=趋势延续），合并为单一"多因子"会丢失归因粒度。多因子应是独立的横截面因子合成 sleeve，价值/动量作为其因子族成员或作为 G11 独立策略，不应混淆

## 4. 上限定义

### 4.1 首批规模上限
- 首批 3 个 sleeve：打板 + 多因子 + 事件驱动
- 各 sleeve 独立 StrategyBook（[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md) MOD-POS-020），独立 PnL 归因、独立风控参数、独立资金预算
- 打板 sleeve 受容量硬约束（小账本），多因子 sleeve 承载主资金，事件驱动 sleeve 中等

### 4.2 演进路径
- **第一阶段（立即施工）**：3 个 sleeve 等额或先验比例资金分配，固定不变。FirmRiskAggregator（MOD-POS-021）只做求和+裁剪（[30_multi_strategy_concurrency §4.2](30_multi_strategy_concurrency.md)）
- **第二阶段（各 sleeve 有 3-6 个月实盘 PnL 后）**：上加 RegimeMetaAllocator（MOD-PA-007），按 PerformanceScore × Shrinkage 动态调资金占比
- **第三阶段（首批 track record 后）**：上加第 4、5 策略（价值反转/动量趋势，G11）

### 4.3 为何这是上限而非妥协
- 3 个差异化 sleeve 已覆盖高/低/中换手率 + 小/大/中容量 + 情绪/横截面/事件三类 alpha 来源，是少而精的完整组合
- 多于 3 个会稀释研究带宽（charter §3 约束五：单人+AI+资金小，少而精是唯一可行路径）
- 少于 3 个会丧失 Model A 自然叠加的分散价值（[30_multi_strategy_concurrency §2.3](30_multi_strategy_concurrency.md)）

### 4.4 首批3策略 intake/incubation 灰度（接口指引）

> 多策略运营纪律是生死线（业界经验：80% 写作在研究、50% 实际时间在运营，[quanthedgeai 2026-07](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)）。本节声明首批3策略的灰度上线指引，具体 schedule 与执行在 G24 模拟实盘验证路径。

- **统一灰度流程**（对齐 [charter §4.2 B-007](../../04_architecture_principles_decisions/system_charter.md) 策略工厂上线流程 + quanthedgeai intake 四阶段；v1.2.0 起**判据驱动**，不设日历硬下限）：
  1. **回测验证**（G23 回测框架）：honest split（in-sample / out-of-sample / true OOS），composite score 达标
  2. **模拟盘**（paper portfolio）：累计 ≥30 笔有效交易且 PnL 偏离回测预期 ≤30% 即达标；偏离 >30% 则调查后再推进
  3. **小资金实盘**（half-sized live）：rolling DSR（Deflated Sharpe Ratio）确认信号稳定（DSR>0 且滚动窗口不破）即达标
  4. **全资金实盘**（full size）：持续监控，触发回撤 Protocol 即降级

  > **为何判据驱动而非"≥6 月"日历硬锁**：单人小资金项目按月硬性等待会无谓推迟上线，且与 [30 §6.1](30_multi_strategy_concurrency.md) "3 个月 track record"矛盾；样本量（trade-count）与统计显著性（DSR）才是推进依据（AlphaFactory 2026-05 小项目权衡）。日历时长仅作参考下限（~2 月），不作推进门禁。
- **上线顺序建议**（各 sleeve 独立灰度，不强制同步）：
  - 打板：容量小、风控参数独立、BM-SEL-22~25 已 production → 可最先灰度
  - 多因子：承载主资金、需充分模拟盘验证因子衰减 → 排第二
  - 事件驱动：依赖 news_data 多源接入进度（G10）→ 视数据就绪排后
- **再平衡纪律**（参考 quanthedgeai）：25% no-trade band（当前权重偏离目标 >25% 才再平衡），每周最多一次， sleeve 增减后强制再平衡。具体在 G19/G20 执行

## 5. 待裁定

> 以下项目暂不施工，非永久禁止。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 | 责任方 |
|---|---|---|---|
| 1. charter §3 约束二/三措辞修订 | charter 写"按市场状态切换权重"已被 Morwane 实证否决，应修订为"按市场状态做风险节流"；并补充"统一框架=统一firm风险框架+少而精差异化sleeve，非Citadel pod"澄清 | 本讨论已裁定，待物理修订（2026-08-12 核验：charter §3 约束二仍写"按市场状态切换权重"，未修订） | 04 域 owner 待认领 |

> 已闭合 3 项（30 号 §4.3 pod 误标修正、30 号 §1.1 5 候选清单同步、打板情绪周期 4+1 与 regime 12 态边界定型）——闭合事实与出处见 §8 修订记录 v1.3.0 ③。

## 6. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| convergence_window 按换手率校准（打板1-2/多因子3-5/事件2-3天） | [30_multi_strategy_concurrency §6.4](30_multi_strategy_concurrency.md) / G14 | 待首批策略实盘后校准 |
| 三策略相关性实测（施工前必做） | [30_multi_strategy_concurrency §6.2](30_multi_strategy_concurrency.md) / G07 | 待 G07 执行 |
| 各策略容量精确测算 | 本讨论 §2.2-2.4 | 待 G08/G09/G10 细节讨论 |
| 事件驱动事件源接入（news_data 多源） | 本讨论 §2.4 / G10 | 待 G10 讨论 |
| 打板情绪周期定位器准确率评估 | [30_multi_strategy_concurrency §6.3](30_multi_strategy_concurrency.md) / G21 | 待评估（G21 已由 [28](28_sentiment_cycle_trading.md) v1.0.0 定型，回测待 G07） |
| 3 策略 sleeve 策略类施工（信号链组件→StrategyBook 组装） | 本讨论 §2.7 | 待 G08/G09/G10 细节定型后经 G05 标准接口（21 号）施工 |

## 7. 引用

### 7.1 相关设计备忘
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md)（多策略并发架构总纲，Model A）
- [00_index_trading_decision.md](00_index_trading_decision.md)（讨论框架路线图，G04 定位）
- [10_regime_detector_spec.md](10_regime_detector_spec.md)（regime spec，正交边界依据）
- [28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md)（G21 情绪周期×交易决策，v1.0.0 已定型）
- [system_charter.md §3](../../04_architecture_principles_decisions/system_charter.md)（投资哲学，§1.4 对齐）

### 7.2 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)（选股阶段）
  - BM-SEL-22~25：打板链（短线评分卡 / 游资接力情绪周期 / 量化短线强度评级 / 双引擎融合）
  - BM-SEL-02：因子计算与信号生成（多因子 sleeve 依赖）
  - BM-SEL-27：盘中实时事件处理（事件驱动 sleeve 依赖）
  - BM-SEL-08/09：板块轮动序列追踪 / 调整周期追踪（G06 板块轮动输入）

### 7.3 depgraph 模块（引用稳定 path / blueprint_id）
| 模块 | blueprint_id | path | 本讨论关系 |
|---|---|---|---|
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | 3 个 sleeve 的载体 |
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | 统一风险框架（求和+裁剪） |
| RegimeMetaAllocator | MOD-PA-007 | `src/zephyr/pf_alloc/core/regime_meta_allocator.py` | regime 风险节流消费者（第二阶段） |
| BudgetChangeHandler | MOD-POS-022 | `src/zephyr/position/core/budget_change_handler.py` | convergence_window 三级升级执行 |

### 7.4 下游交接（本讨论是以下主题组的前置依赖）
- G05 选股引擎架构（`21_stock_selection_engine`）：3 sleeve 的选股 pipeline 标准接口
- G07 策略间相关性验证（`23_strategy_correlation_validation`）：§2.5 差异化矩阵为输入
- G08 打板细节（`24_daban_strategy_detail`）：§2.2 打板 sleeve 定义
- G09 多因子细节（`25_multifactor_strategy_detail`）：§2.3 多因子 sleeve 定义
- G10 事件驱动细节（`26_event_driven_strategy_detail`）：§2.4 事件驱动 sleeve 定义

### 7.5 开源实证参考
- [Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book)：2 个弱相关 alpha sleeve + risk-parity + regime 风险节流，OOS 2013-2026 Sharpe 1.43 / MaxDD -10.3%。本架构 Model A 的直接范式来源，印证"统一风险框架 + sleeve + regime 风险节流"优于"regime alpha 择时"
- 2026 最新实践综述（regime-aware / systematic multi-strategy vs pod）支撑 §1.4 charter 对齐裁定，详见本讨论配套审查报告
- [quanthedgeai — Implementing a Multi-Strategy Portfolio End-to-End (2026-07)](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)：端到端施工流程（Step 0-7）+ intake 四阶段 + 25% no-trade band。§4.4 灰度指引与 G24 直接参考
- [Janus-Q — End-to-End Event-Driven Trading (arXiv 2026-02)](https://arxiv.org/html/2602.19919v2)：LLM + 分层门控奖励建模，事件从辅助信号升为主决策单元。G10 事件驱动 sleeve 内部增强方向
- [Yukka — Sentiment Decay & Source Selection (2026-05)](https://cdn.prod.website-files.com/66b4f3430903efa023fe741b/69fdded32f3d7e02f17ff3f8_Sentiment%20Decay%20&%20Source%20Selection%20in%20Global%20Equity%20Markets%20-%20White%20Paper.pdf)：情绪 IC 衰减曲线 regime-dependent。§2.4 事件衰减边界细化依据
- [Hawkes Processes for Investors (2026-02)](https://stockalpha.ai/alpha-learning/hawkes-processes-for-investors-modeling-self-exciting-volatility-bursts)：自激发点过程建模事件聚类。G10 事件冲击建模先进方法
- [Beyond the Event Horizon (2025)](https://www.preprints.org/manuscript/202506.0079)：事件后 day 0-5 rising phase RVR 9.5x on decay phase。§2.4 持仓周期实证依据
- 2026-08 A 股游资生态（东方财富社区）：炸板率 ~68%（2023 年 ~40%）、打板隔日溢价 ~1.7%（2023 年 ~4.2%）、量化成交占比 >35%——涨停端 alpha 衰减实证，支撑 §2.2 打板"小容量+情绪周期纪律"定位（详见 [28 §8.3](28_sentiment_cycle_trading.md)）
- J.P. Morgan Factor Views 3Q26（2026-08-07）：动量因子持续强势、价值/质量历史估值低位、建议跨因子分散——多因子 sleeve 因子族配置的宏观参考
- LVS Event-Driven 实证（2026Q1）：事件驱动组合在 S&P -8.9% 季度仅 -0.2%——事件驱动收益流与大盘低相关的下行保护属性，支撑 §2.4 事件驱动 sleeve 的分散价值
- quant67 另类数据综述（2026-05）：新闻情绪信号指数衰减、短线半衰期 30 分钟~数小时——§2.4 事件衰减曲线（rising phase 后快速衰减）的工程参数参考

## 8. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-08 | 1.0.0 | 初稿 | G04 首批3策略定义定型：打板+多因子+事件驱动；澄清"多因子"来源（主升龙头并入打板，多因子新增）；§1.4 对齐 charter §3（裁定 Model A 非 Citadel pod，是 Morwane 式统一风险框架）；登记 charter/30_multi_strategy_concurrency 措辞治理债待裁定 |
| 2026-08-08 | 1.1.0 | 施工流程补充 | 补 §2.4 事件持仓周期实证（rising phase 9.5x）+ 衰减 regime-dependent 边界细化；新增 §2.6 选股池交集与冲突标的处理原则；新增 §4.4 intake/incubation 灰度指引（对齐 charter B-007 + quanthedgeai 四阶段）；§7.5 补 Janus-Q/Yukka/Hawkes/quanthedgeai 开源参考。2026 最新实践审查确认无替代架构，前沿算法登记为各 sleeve/firm 层演进方向 |
| 2026-08-08 | 1.2.0 | §4.4 灰度去过度工程 | 回应"§4.4 vs §6.4 收敛窗口"过度检查：加正交声明（生命周期月级 vs 单次收敛天级，勿混淆）；§4.4 从硬性"≥6月"改为判据驱动（trade-count + DSR，对齐 AlphaFactory 2026-05 小项目权衡），消除与 §6.1"3月 track record"的矛盾，符合 charter 约束五少而精 |
| 2026-08-09 | 1.2.1 | 文件名 discussion_003_first_batch_strategies.md → 20_first_batch_strategies.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 1.2.2 | §7 前向引用旧名（design_memo_003/discussion_005-008）更新为段位名（21_stock_selection_engine/23-26） | 文档体系重排补遗：前向引用未随 1.2.1 改名同步更新 |
| 2026-08-09 | 1.2.3 | §1 管理规范链接 `design_memo_management_spec.md`→`01_design_memo_management_spec.md` | 改名工程遗留断链修复（全量断链扫描发现） |
| 2026-08-09 | 1.2.4 | 文档头统一：frontmatter 补 title/owner/language，H1 去"讨论·"前缀与 title 对齐；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-12 | 1.3.0 | ①新增 §2.7 已施工设施盘点（通用规则 #11）：打板四引擎/因子工厂/事件处理/position 三件套均 production，pf_core/strategies 空壳=3 策略 sleeve 策略类未施工（缺口登记 §6）；②§4.4 修正内部矛盾——正文"≥6 月"硬性表述改判据驱动（trade-count≥30 + PnL 偏离≤30% + rolling DSR），对齐 v1.2.0 修订记录声称；③§5 待裁定落地状态更新：2/3 号已由 30 号 v1.4.0 落地、4 号已由 28 号 v1.0.0 定型、1 号（charter 措辞）2026-08-12 核验仍未修订保持开放；④§7.5 补 2026-08 实证（炸板率 68% 游资生态 / JPM Factor Views 3Q26 / LVS 事件驱动下行保护 / quant67 情绪衰减）；⑤§7.1 补 28 号引用 | 多轮审查回填：设施盘点先行明确缺口、消除正文与修订记录矛盾、待裁定状态与引用方同步、最新实证入库（2026-08-12 三次并发回滚后重建并即时提交锁定） |
| 2026-08-12 | 1.3.1 | 作战地图环节映射补强——锚定 BM-SEL-21-A、BM-SEL-21-F | §2.7 末尾补映射块，环节级可追溯 |
| 2026-08-15 | 1.3.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-06） | §5 移除 3 行删除线已闭合待裁定（pod 误标/5 候选清单/情绪周期边界——闭合事实 v1.3.0 ③ 已载，表末补指针注记）；其余通读零发现。3 策略定义/差异化矩阵/设施盘点/灰度四阶段判据/引用链接零丢失 |
