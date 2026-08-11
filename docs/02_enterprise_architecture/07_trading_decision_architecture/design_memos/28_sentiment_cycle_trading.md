---
ttl: permanent
doc_type: architecture_view
title: 情绪周期×交易决策
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-12
topic: sentiment_cycle_trading
scope: 07_trading_decision_architecture
depends_on:
  - 10_regime_detector_spec
  - 20_first_batch_strategies
  - 30_multi_strategy_concurrency
related_modules:
  - src/zephyr/signal_ashare/youzi_relay_emotion_engine.py
  - src/zephyr/signal_ashare/dual_engine_fusion_decision_engine.py
  - src/zephyr/position/core/strategy_book.py
---

# 情绪周期×交易决策

> 本备忘定义游资情绪周期（4+1 阶段）在交易决策中的角色与边界：**情绪周期 = sleeve 内 alpha 择时信号（决定买卖什么、几成仓）；regime = 市场级风险节流（决定多谨慎）；两者正交**。
> 性质：永久态讨论记录，可随项目演进而修订。管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。
> 路线图定位见 [00_index_trading_decision](00_index_trading_decision.md) G21。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G21 情绪周期×交易决策 |
| 所属 | 跨作战地图 05/06/07/09 |
| 依赖 | G04（[20_first_batch_strategies](20_first_batch_strategies.md)）、G08（[24_daban_strategy_detail](24_daban_strategy_detail.md)，打板最依赖情绪周期） |
| 对标 | 游资情绪周期体系 / 龙虎榜情绪 / 涨跌停情绪温度 |
| 正交性 | ✅ 已裁定：与 regime 正交（§3.1/§3.4）——情绪周期=sleeve 内 alpha 择时，regime=市场级风险节流 |
| 优先级 | P2（打板策略前置） |
| 状态 | **已定型（v1.0.0）**——G04/G08 依赖闭合；2026-08-11 git clean 灾难丢失后按引用方（30 号 v1.4.0 / 24 号 v1.9.x / strategy_book.py）锚点重建 |

## 2. 背景

### 2.1 项目处境

- 打板链已 production：[battle_map_05](../battle_map/battle_map_05_stock_selection.md) BM-SEL-22（短线评分卡）/ BM-SEL-23（游资接力情绪周期）/ BM-SEL-24（量化短线强度）/ BM-SEL-25（双引擎融合），对应代码 `src/zephyr/signal_ashare/` 四引擎
- 情绪周期 4+1 阶段定位器（BM-SEL-23-B）是打板链内建组件，已 production（`youzi_relay_emotion_engine.py`）
- [30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md) 裁定：情绪周期是所有短周期策略的**共同隐形驱动**，打板×事件驱动相关性可能高于直觉
- [10_regime_detector_spec](10_regime_detector_spec.md) C-prime 裁定：情绪周期探测器**保留不动、降级为情绪轴软输入**（经映射表软调 regime 概率分布），不新建独立检测器模块，不直接被 Shrinkage 消费

### 2.2 核心问题

情绪周期如何服务交易决策：①5 阶段（冰点/反核/主升/疯狂/退潮）各阶段的买卖纪律是什么？②定位器准确率如何保障？③与 regime 的分工边界在哪？④各策略在不同情绪阶段如何部署？⑤作为"隐形驱动"，它对策略间相关性意味着什么？

### 2.3 约束条件

- T+1、不能做空、涨跌停限制 → 退潮期无法对冲，**只能空仓/降仓**，纪律必须是硬性的
- 打板容量极小（单票几万~几十万）→ 情绪周期仓位上限是 sleeve 级风控第一层
- 涨停端 alpha 衰减（2026 年炸板率 ~68%、打板隔日溢价 ~1.7%，见 §8.3）→ 情绪阶段误判的代价比历史上任何时候都高
- 单人 + 100% AI 开发 → 阶段定位规则必须简单可审计（阈值法优先于黑盒模型）

## 3. 决策

### 3.1 分工边界：情绪周期 vs regime（核心裁定）

> 本节回应 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) v1.4.0 待裁定-4（"打板情绪周期4+1 与 regime 边界"），已定型。

| 维度 | 情绪周期 4+1 | regime（4 HMM 基态 + 3 overlay） |
|---|---|---|
| **回答的问题** | 买卖什么、几成仓（alpha 择时） | 该多谨慎（风险节流程度） |
| **作用层** | sleeve 内部（打板最强、事件驱动次之、多因子最弱） | firm 层（Shrinkage → budget 数字） |
| **时间尺度** | 天级微观（连板梯队、炸板率、晋级率） | 周/月级宏观（趋势×波动率结构） |
| **消费方** | 打板 sleeve（双引擎权重、仓位上限）、事件驱动 sleeve（衰减参数、退潮加权） | RegimeMetaAllocator / FirmRiskAggregator |
| **接口关系** | 不读 regime 输出，只收 budget 数字 | 不读情绪阶段标签；情绪仅经 [10 §3.3](10_regime_detector_spec.md) 映射表**软调**概率分布 |

**实证依据**：
- Morwane 实证（[30 §7.4](30_multi_strategy_concurrency.md)）：regime 做 alpha 择时 Sharpe 1.04→0.87，做风险节流 Sharpe 1.43 + MaxDD -14.2%→-10.3%——**状态信号用于进攻（择时）有害，用于防守（节流）有益**。情绪周期允许做 sleeve 内择时是因为其输入（连板梯队/封单/晋级率）与打板 alpha 同源同尺度，不是 regime 那种宏观外生信号
- 10 号 Phase 2 验证：12 态过拟合降为 4 态——状态颗粒度越细越不可信，情绪周期 4+1 阶段同理（§3.3 准确率回测为施工前必做）

### 3.2 5 阶段买卖纪律

> 本节是 [24_daban_strategy_detail](24_daban_strategy_detail.md) 引用锚点（[28 §3.2]）。纪律与代码 `youzi_relay_emotion_engine.py` 的 `StrategyAction` 枚举逐一对应。

| 阶段 | 市场特征 | 买卖纪律（代码动作） | sleeve 仓位上限 |
|---|---|---|---|
| 冰点 | 连板断层、涨停稀少、跌停潮后 | **空仓/埋伏**（WAIT）——不追，等反转信号 | 0 ~ 极轻 |
| 反核 | 首板密集出现、核按钮修复 | **小仓试错**（SMALL_TRIAL）——轻仓试新题材 | ≤2-3 成 |
| 主升 | 龙头加速、梯队完整、晋级率高 | **核心仓做龙头**（CORE_POSITION）——主攻最高板/主线最强 | 3-5 成 |
| 疯狂 | 高位接力、一致性亢奋 | **只做龙头**（LEADER_ONLY）——减仓非核心，拒做中位股 | 2-3 成（减仓） |
| 退潮 | 断板潮、炸板率飙升、核按钮批量 | **空仓等冰点**（CLEAR_WAIT）——强制空仓 | ≤1 成（清仓） |

**退潮期强制空仓是打板 sleeve 存活的核心机制**（[24 §2](24_daban_strategy_detail.md)）：2026 年炸板率 ~68% 环境下，退潮期任何操作（打板/追高/低吸）期望为负。仓位上限表同时是打板四层风控的第一层（sleeve 内情绪周期仓位上限，[24 §3.7](24_daban_strategy_detail.md)）。

**社区实证**（2026 年，§8.3）：A 股短线社区主流划分为 4 阶段（启动/主升/分歧/退潮）或 6 阶段（启动/确认/分歧/断板/高潮/退潮），仓位映射与本裁定一致——退潮空仓、冰点轻仓试错、主升重仓、高潮/疯狂减仓。本项目 4+1 划分处于社区主流颗粒度区间内。

### 3.3 情绪周期定位器（BM-SEL-23-B，production）

**裁定：复用不新建**（[10_regime_detector_spec §2.2](10_regime_detector_spec.md) C-prime）——不新建独立检测器模块，情绪周期定位由打板链内建的 23-B 承担。

已施工机制（`youzi_relay_emotion_engine.py`，production）：

1. **6 因子评分**（0-100）：连板高度 25 + 封单质量 20 + 涨停时间 15 + 开板次数 15 + 竞价强度 10 + 助攻梯队 15
2. **阈值映射定阶段**：≤20 冰点 / 20-40 反核 / 40-65 主升 / 65-85 疯狂 / >85 疯狂（超高危）
3. **退潮条件触发（"+1"）**：高分但市场广度下降（涨停家数萎缩、断板率上升）→ 退潮。退潮不由分数区间直接给出，是条件触发的特殊阶段——疯狂后必退潮
4. **置信度输出**：`phase_confidence` 随阶段一并输出，供下游降级判断

**演进方向（未施工，见 §6）**：
- **灰度概率输出**：[10 §2.5.4](10_regime_detector_spec.md) 用户裁定——探测器输出应为 5 维概率分布 P(冰点)...P(退潮)、Σ=1，与 regime 探测器输出逻辑一致。当前代码为硬标签+置信度，存在差距
- **BOCPD/CUSUM 变点检测**：阶段转换（尤其疯狂→退潮）的统计变点预警，`strategy_book.py` 注释已预留此锚点（"28号定义 5 阶段情绪周期 + BOCPD/CUSUM 检测"）
- **准确率回测**：施工前必做（[30 §6.3](30_multi_strategy_concurrency.md) / [24 §6](24_daban_strategy_detail.md)）——production 在跑但无历史准确率评估

### 3.4 与 regime 的正交性

> 本节是 [24_daban_strategy_detail](24_daban_strategy_detail.md) 引用锚点（[28 §3.4]）。

- **打板读情绪周期、不读 regime**：打板 sleeve 的选股与仓位由 4+1 阶段驱动；regime 对打板的唯一作用通道是 firm 层 budget 数字（Shrinkage 节流结果）
- **情绪周期对 regime 的唯一作用通道**：[10 §3.3](10_regime_detector_spec.md) 映射表软输入——情绪阶段软调 regime 概率分布，不作为第 13 态硬叠加，不直接被 Shrinkage 消费
- **防双重惩罚**：当 regime 已触发 ⑧加速下跌信号时，`strategy_book.py` 的退潮加权回退为 1.0（§3.5）——同一风险不重复计价

### 3.5 情绪周期作为隐形驱动与退潮加权机制

> 本节是 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) v1.4.0 与 `strategy_book.py` 的引用锚点（[28 §3.5]）。

**问题**（[30 §1.3](30_multi_strategy_concurrency.md)）：情绪周期是所有短周期策略的共同隐形驱动——打板与事件驱动在退潮期**同时**亏损，策略间相关性在尾部飙升（A 股版"分散化幻觉"，与 bayes-group 2026-03 对 pod 平台 March 2026 事件的观察同构）。

**已施工机制**（`strategy_book.py`，production）：**退潮加权系数**——

- 退潮阶段（`stage="退潮"`）：StrategyBook 内部卖出信号权重 × `retreat_weight`，按策略类型差异化：**打板 1.5 / 事件驱动 1.3 / 多因子 1.2**（打板对情绪退潮最敏感）
- 非退潮阶段：`retreat_weight = 1.0`（无加权）
- regime ⑧加速下跌信号激活时：回退 1.0（风险已由 Shrinkage 计价，不重复加权）

**相关性验证是 G07 施工前必测项**：若实测各阶段打板×事件驱动相关性 >0.6，"多策略实为情绪 beta 穿多件衣服"，需重新审视策略组合（[30 §6.2](30_multi_strategy_concurrency.md) / [20 §2.5](20_first_batch_strategies.md)）。

### 3.6 各策略在不同情绪阶段的部署

| 情绪阶段 | 打板 sleeve | 事件驱动 sleeve | 多因子 sleeve |
|---|---|---|---|
| 冰点 | 空仓/埋伏；双引擎权重 → 量化 70% | 事件稀少期，衰减参数保守 | 正常横截面选股（不读阶段） |
| 反核 | 小仓试错；双引擎 50:50 | 试错性参与（首板题材催化） | 正常 |
| 主升 | 核心仓做龙头；游资 70% | 主升期事件溢价放大，积极参与 | 正常 |
| 疯狂 | 只做龙头、减仓；游资 80% | 警惕利好兑现型事件 | 正常 |
| 退潮 | **强制空仓**；量化 60%；retreat_weight=1.5 | 降仓；retreat_weight=1.3 | 正常；retreat_weight=1.2 |

双引擎自适应权重已 production（`dual_engine_fusion_decision_engine.py`：基准游资 60/量化 40，冰点→量化 70 / 反核→50:50 / 主升→游资 70 / 疯狂→游资 80 / 退潮→量化 60）。多因子 sleeve 纯横截面选股，不读情绪阶段标签，仅经退潮加权弱耦合。

## 4. 考虑过的替代方案

### 4.1 3 阶段（冰点/主升/退潮）—— 拒绝
粒度不够：反核（试错）与主升（重仓）仓位差 2 倍以上，疯狂（减仓）与主升操作相反，合并会丢失关键操作差异。[24 §4.3](24_daban_strategy_detail.md) 已裁定。

### 4.2 6+ 阶段（社区流派：启动/确认/分歧/断板/高潮/退潮）—— 拒绝
过拟合风险：阶段越多，阶段内样本越少，定位器准确率越不可信（10 号 12 态→4 态的同构教训）。社区 6 阶段划分可作为 4+1 阶段内的子状态参考，不升级为独立阶段。[24 §4.3](24_daban_strategy_detail.md) 已裁定。

### 4.3 新建独立情绪检测器模块 —— 拒绝
[10 §2.2](10_regime_detector_spec.md) C-prime 已裁定：情绪周期探测器（23-B）保留不动、降级为情绪轴软输入，不新建独立模块。不拆旧可用资产是标准工程实践。

### 4.4 情绪周期升级为 regime 级权重切换信号 —— 拒绝
Morwane 实证：状态信号做 alpha 择时摧毁价值（Sharpe 1.04→0.87）。情绪周期只允许 sleeve 内择时（输入与 alpha 同源同尺度），不得越界到 firm 层 budget 决策——firm 层只看 regime Shrinkage 与 PerformanceScore 后验。

## 5. 上限定义

### 5.1 系统上限

- **阶段数上限 4+1**：不随社区流派细化而增加
- **作用域上限 sleeve 内**：情绪周期信号不进入 firm 层资金分配公式（budget 只由 PerformanceScore × Shrinkage 决定）
- **仓位上限表即硬约束**：§3.2 各阶段仓位上限由 sleeve 内风控强制执行，退潮期强制空仓不可覆盖（kill-switch 级除外的人工干预走 40 号执行层流程）

### 5.2 演进路径

1. **当前（production）**：阈值法硬标签 + 置信度 + 退潮条件触发
2. **下一步**：准确率回测（G07 前置）→ 灰度概率输出（10 号 §2.5.4 裁定方向）
3. **远期**：BOCPD/CUSUM 变点检测做疯狂→退潮转换预警；社区细分阶段作为阶段内子状态参考

### 5.3 为何是上限而非妥协

4+1 阶段已覆盖全部操作差异（空仓/试错/重仓/减仓/清仓五档动作与仓位一一对应）；作用域限制在 sleeve 内是 Morwane 实证与 Model A 架构的直接推论；更多阶段或更大作用域带来的不是收益而是过拟合与相关性幻觉。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| 灰度概率输出升级（硬标签→5 维概率分布） | 10 号 §2.5.4 已定方向，但需准确率回测先证明硬标签基线可靠 | 准确率回测完成后 |
| BOCPD/CUSUM 变点检测 | 阈值法已 production，变点检测是增强非替代；需历史数据验证预警提前量 | 回测数据积累后 |
| 情绪周期定位器准确率回测 | production 在跑但无历史准确率评估 | G07 + [30 §6.3](30_multi_strategy_concurrency.md) 施工前必做 |
| 打板×事件驱动退潮期相关性实测 | §3.5 理论推断，待实测 | G07 施工前必做 |

## 7. 待定问题

| 原讨论要点（00_index G21） | 状态 | 落点 |
|---|---|---|
| ① 5 阶段各阶段买卖纪律 | ✅ 已裁定 | §3.2 |
| ② 定位器准确率评估 | ⏳ 待回测 | §3.3 / §6 |
| ③ 情绪周期与 regime 映射关系 | ✅ 已裁定 | §3.1 / §3.4（+ [10 §3.3](10_regime_detector_spec.md) 软输入映射表） |
| ④ 各策略不同情绪阶段部署 | ✅ 已裁定 | §3.6 |
| ⑤ 情绪周期=隐形驱动→策略间相关性来源 | ✅ 机制已施工，实测待 G07 | §3.5 |

## 8. 引用

### 8.1 相关设计备忘
- [10_regime_detector_spec](10_regime_detector_spec.md)（C-prime：情绪周期软输入；§2.5.4 灰度概率裁定；§3.3 映射表）
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04：打板/多因子/事件驱动三 sleeve 定义）
- [24_daban_strategy_detail](24_daban_strategy_detail.md)（G08：情绪周期主要消费方；§3.7 四层风控第一层；§4.3 阶段数裁定）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md)（Model A；§1.3 隐形驱动；§6.3 准确率回测；v1.4.0 待裁定-4 由本文 §3.1 定型）

### 8.2 相关作战地图与代码
- [battle_map_05_stock_selection](../battle_map/battle_map_05_stock_selection.md)：BM-SEL-23-B（4+1 阶段定位）/ BM-SEL-23-C（阶段→策略映射）/ BM-SEL-25-B（情绪周期自适应权重）
- `src/zephyr/signal_ashare/youzi_relay_emotion_engine.py`（production：EmotionPhase / StrategyAction / 阈值 20-40-65-85 / 退潮条件触发）
- `src/zephyr/signal_ashare/dual_engine_fusion_decision_engine.py`（production：情绪周期自适应权重）
- `src/zephyr/position/core/strategy_book.py`（production：退潮加权系数 retreat_weight）

### 8.3 外部实证（2026 年）
- A 股情绪周期社区主流划分（4 阶段：启动/主升/分歧/退潮；6 阶段：+断板/高潮）与仓位映射（退潮空仓/冰点轻仓/主升重仓/高潮减仓）——与 §3.2 裁定一致，支撑 4+1 颗粒度处于行业主流区间
- 2026-08 游资生态：炸板率 ~68%（2023 年 ~40%）、打板隔日溢价 ~1.7%（2023 年 ~4.2%）——涨停端 alpha 衰减背景下，退潮期强制空仓（§3.2）是 sleeve 存活前提
- [Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book)：状态信号择时有害/节流有益——§3.1/§4.4 分工边界的核心实证

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G21 讨论要点占位，待讨论填空 |
| 2026-08-12 | 1.0.0 | 骨架→active 定型回填 | 2026-08-11 git clean 灾难丢失原内容后，按引用方锚点（30 号 v1.4.0 待裁定-4 引用 §3.1、24 号 v1.9.x 引用 §3.2/§3.4/§3.5、strategy_book.py 注释引用 §3.5 + BOCPD/CUSUM）重建并定型：§3.1 分工边界（情绪周期=sleeve 内 alpha 择时 vs regime=市场级风险节流）、§3.2 五阶段买卖纪律与仓位上限、§3.3 定位器现状与演进（灰度概率/变点检测待裁定）、§3.4 正交性、§3.5 退潮加权机制（production）、§3.6 三策略部署矩阵；§4 替代方案（3 阶段/6+阶段/独立检测器/regime 级切换均拒绝）；2026 社区实证（4-6 阶段划分、炸板率 68%）入 §8.3。5 个 G21 讨论要点 4 个已裁定、1 个待回测（2026-08-12 三次并发回滚后重建） |
