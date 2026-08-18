---
module_id: MOD-REGIME-001
title: "Regime检测器蓝图 — 12态灰度概率+8转换评分+Shrinkage产出（系统最上游·可验证接口）"
doc_type: blueprint
status: Active
version: "0.1.14"
design_maturity: production
build_status: generated
ttl: permanent
layer: L2_domain
layer_name: regime
functional_domain: regime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-06"
last_updated: "2026-08-06"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-REGIME-001 RegimeDetector — 12态Regime检测器 蓝图

> **module_id**: MOD-REGIME-001 | **域**: D_REGIME | **层**: L2 业务域
> **优先级**: P0 | **成熟度**: design | **建设标记**: 🟡 待施工
> **SSoT**: depgraph MOD-REGIME-001 | **spec 真源**: [10_regime_detector_spec.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md) v1.3.1（12态完整 spec）
> **验证真源**: [11_regime_backtest_validation_plan.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md) v1.0.0（回测验证方案，§4 验证需求）
> **消费方**: [RegimeMetaAllocator](../../_domain_portfolio_alloc/regime_meta_allocator/blueprint.md) MOD-PA-007（Shrinkage + 12维概率消费者）

## 1. 定位

12 态 regime 检测器——整个交易决策架构的**最上游**。输出 12 维灰度概率分布 + Shrinkage 风险节流因子，供 RegimeMetaAllocator 做 budget 分配。是 regime 链的源头（regime → Shrinkage → budget → StrategyBook）。

属 **B 类核心业务模块**（HMM 模型 + 规则覆盖层 + 多源融合），HMM 超参数/转换评分门槛为 C 类可调参数。

### 1.1 五子模块分解（11_regime_backtest_validation_plan §8.1）

> **用户裁定（2026-08-06）**：直接实现完整 12 态，回测验证后再基于证据简化。

| 子模块 | 职责 | spec 真源 | 技术选型 |
|---|---|---|---|
| ① HMM 9态 | 9 态 3×3 网格（趋势×波动率），多特征喂入，输出 P(r1)..P(r9) | 10_regime_detector_spec §2.6/§3 | hmmlearn GaussianHMM |
| ② D-SIGNAL-68 覆盖层 | 3 特殊态（CRISIS/RECOVERY/BREAKOUT）规则触发 + 8 转换评分 | 10_regime_detector_spec §2.8/§4 | 规则引擎（动态评分制） |
| ③ ConfidenceSignal | max(P) → 4 档映射 + 稀有态折扣 | 30_multi_strategy_concurrency §2.2 | 公式计算 |
| ④ RiskSignal | 13 参数完整计算 + 聚合公式 | 10_regime_detector_spec §5.3 | 公式计算 |
| ⑤ Shrinkage | ConfidenceSignal × RiskSignal，可开关 | 30_multi_strategy_concurrency §2.2 | 公式计算 |

**数据流**（内部）：
```
市场特征 → ①HMM(P_hmm r1..r9) ──┐
                                 ├──→ 12维合并归一化 ──→ RegimeProbabilities
规则信号 → ②覆盖层(P_overlay r10..r12) ─┘         │
                                                    ├──→ ③ConfidenceSignal ──┐
                                                    │                        ├──→ ⑤Shrinkage
                                                    └──→ ④RiskSignal ────────┘
```

### 1.2 可验证性接口（11_regime_backtest_validation_plan §4 验证需求）

> **关键约束**：接口设计必须满足 11_regime_backtest_validation_plan 的 4 个验证需求，否则代码写完没法验证就返工。

| 验证需求 | 接口设计 | 验证项 |
|---------|---------|--------|
| ① 输出 12 维概率分布 | `RegimeProbabilities`（12 维，Σ=1），**不能只输出硬标签** | B1 校准度 / B2 CRPS |
| ② Shrinkage 可开关 | `shrinkage_enabled` 参数：True→ConfidenceSignal×RiskSignal，False→1.0 | C1 开/关对比（**一票否决**） |
| ③ 8 转换触发可记录 | `TransitionTriggered` 事件（时间戳+转换类型+评分明细） | B4 转换触发准确性 |
| ④ HMM hmmlearn | GaussianHMM，9 态，walk-forward 季度重拟合 | A1/A2/A3 模型质量 |

### 1.3 不做什么

- **不做 budget 分配**（归 RegimeMetaAllocator MOD-PA-007）
- **不做选股 / 仓位**（归 StrategyBook / MOD-POS-001）
- **不做回测**（归 BM-BT 框架，本模块只提供可验证接口）
- **不做宏观 regime**（现有 [gov_drift/regime_detector.py](../../../../src/zephyr/gov_drift/detector_core/regime_detector.py) 是宏观 4 态，与本模块无关）

## 2. 输入 / 输出

### 2.1 输入

| 方向 | 内容 | 契约/事件 | 来源 | 就绪 |
|------|------|-----------|------|:----:|
| HMM 特征 | RegimeFeatures（波动率分位/趋势斜率/相关性矩阵/涨跌家数/量能异动） | CTR-SIG-001-F | ClickHouse 特征工程 | 🟡 待建（§8.2 步骤1） |
| 覆盖层信号 | OverlaySignals（Capitulation/Wyckoff/VIX/政策底/利空钝化/资金承接/筹码/估值等） | CTR-SIG-001-O | 10_regime_detector_spec §4 各转换数据源 | ❌ 待建 |
| RiskSignal 输入 | RiskSignalInputs（13 参数市场风险输入） | CTR-SIG-013 | 10_regime_detector_spec §5.3 数据源 | ❌ 待建 |
| 配置 | shrinkage_enabled（验证开关，默认 True） | config | 配置文件 | ✅ config |
| 配置 | hmm_params（n_states=9, covariance_type, n_iter） | config | 配置文件 | ✅ config |

### 2.2 输出

| 方向 | 内容 | 契约/事件 | 去往 |
|------|------|-----------|------|
| 核心 | RegimeProbabilities（12 维灰度概率，Σ=1） | CTR-SIG-012 | RegimeMetaAllocator (MOD-PA-007) + BM-BT-03-E 验证 |
| 核心 | Shrinkage（ConfidenceSignal × RiskSignal 或 1.0） | CTR-SIG-014 | RegimeMetaAllocator (MOD-PA-007) |
| 事件 | TransitionTriggered（8 转换触发，含评分明细） | E-SIG-01 | RegimeMetaAllocator + BM-BT 验证（B4） |
| 归因 | RegimeSnapshot（当前态+概率+Shrinkage 计算明细） | E-SIG-02 | Trader + 归因系统 |

### 2.3 RegimeProbabilities 定义 (CTR-SIG-012)

> **12 维灰度概率**，供 B1 校准度 / B2 CRPS 验证。**不能只输出硬标签**。

| 字段 | 类型 | 说明 |
|------|------|------|
| probabilities | dict[str, float] | {r1..r12: P(ri)}，Σ=1.0 |
| hmm_probabilities | dict[str, float] | {r1..r9: P_hmm(ri)}（HMM 原始输出，归因用） |
| overlay_probabilities | dict[str, float] | {r10..r12: P_overlay(ri)}（覆盖层输出，归因用） |
| dominant_regime | str | max(P) 对应的态 |
| dominant_frequency | float | dominant_regime 的历史频率（稀有态判断用） |
| confidence | float | max(P) 值 |
| timestamp | datetime | |
| schema_version | str | "1.0" |

**12 态清单**（10_regime_detector_spec §3，D-SIGNAL-04）：

| 编号 | 态 | 来源 | 驱动 |
|------|-----|------|------|
| r1-r9 | 9 基础态（趋势×波动率 3×3 网格） | HMM | hmmlearn GaussianHMM |
| r10 | CRISIS（危机） | D-SIGNAL-68 覆盖层 | 规则触发（S2 参数 §4.12） |
| r11 | RECOVERY（复苏） | D-SIGNAL-68 覆盖层 | 规则触发（S2 参数 §4.12） |
| r12 | BREAKOUT（突破） | D-SIGNAL-68 覆盖层 | 规则触发（S1 参数 §4.10） |

### 2.4 TransitionTriggered 事件定义 (E-SIG-01)

> 供 B4 转换触发准确性验证（标注历史事件时点，±5 交易日吻合 ≥6/8）。

| 字段 | 类型 | 说明 |
|------|------|------|
| transition_id | str | T1-T6 / S1 / S2 |
| transition_name | str | 如"CRISIS→RECOVERY" |
| stage | str | "trigger" / "confirm" / "fail" / "strong_confirm" |
| score | int | 动态评分总分 |
| score_breakdown | dict | 各维度分值明细（如 {capitulation: 65, vix: 45, ...}） |
| threshold | int | 触发门槛（如 trigger=140, confirm=190） |
| timestamp | datetime | 触发时间戳 |
| schema_version | str | "1.0" |

## 3. 核心规则

### 3.1 子模块①：HMM 9态（10_regime_detector_spec §2.6/§3）

> **技术选型（§10 已决策）**：hmmlearn GaussianHMM，9 态 3×3 网格，walk-forward 季度重拟合。

| 配置 | 值 | 说明 |
|------|-----|------|
| n_states | 9 | 3×3 网格（趋势上/平/下 × 波动率高/中/低） |
| covariance_type | "full" | 多特征协方差 |
| n_iter | 100 | EM 迭代 |
| 重拟合频率 | 季度 | walk-forward（对照 Morwane） |
| 解码方式 | 因果 Viterbi | 防前视（§9 行业对照：Morwane causal Viterbi） |

**9 态 3×3 网格**（10_regime_detector_spec §3）：

| | 低波动 | 中波动 | 高波动 |
|---|---|---|---|
| **上升趋势** | r1 Bull-Low | r2 Bull-Mid | r3 Bull-High |
| **横盘** | r4 Neutral-Low | r5 Neutral-Mid | r6 Neutral-High |
| **下降趋势** | r7 Bear-Low | r8 Bear-Mid | r9 Bear-High |

**输出**：`P_hmm(r1)..P_hmm(r9)`，Σ=1.0（GaussianHMM predict_proba）

**特征工程**（§8.2 步骤1，来自 ClickHouse）：
- 波动率分位（20日 HV 分位）
- 趋势斜率（线性回归斜率）
- 相关性矩阵（跨资产/跨行业）
- 涨跌家数比
- 量能异动

### 3.2 子模块②：D-SIGNAL-68 覆盖层（10_regime_detector_spec §2.8/§4）

> 3 特殊态规则触发 + 8 转换评分。规则引擎，非 HMM。

**3 特殊态触发**：
- **CRISIS (r10)**：10_regime_detector_spec §4.12 S2 参数（Capitulation投降+Wyckoff吸筹+VIX见顶+政策底+估值极端+利空钝化+资金承接+底部筹码，8维度评分）
- **RECOVERY (r11)**：10_regime_detector_spec §4.12 S2 确认标准
- **BREAKOUT (r12)**：10_regime_detector_spec §4.10 S1 参数（复苏→突破）

**8 转换评分**（动态评分制，10_regime_detector_spec §4.1 总览表）：

| 转换 | 路径 | 评分维度 | spec 真源 |
|------|------|---------|---------|
| T1 | Bull-Low→Bull-High | 量能扩张+趋势加速+波动率上升 | §4.6 |
| T2 | Bear-Low→Bull-Low | 均值回归+价值投资+底部框架 | §4.7 |
| T3 | Bull-High→Bear-High | 动量衰竭+泡沫破裂 | §4.8 |
| T4 | Bull-High→Bear-Low | 泡沫崩塌（Minsky+Shiller CAPE） | §4.8 |
| T5 | Bull-High→Neutral-High | Wyckoff派发+情绪退潮 | §4.11 |
| T6 | Bear-High→Bear-Low | 恐慌抛售结束+波动率回落 | §4.7 |
| S1 | RECOVERY→BREAKOUT | 突破确认（量价+主线+情绪） | §4.10 |
| S2 | CRISIS→RECOVERY | 见底检测（8维度见底） | §4.12 |

**输出**：`P_overlay(r10), P_overlay(r11), P_overlay(r12)` + `TransitionTriggered` 事件

### 3.3 12 维概率合并归一化

```
# HMM 9 态输出
P_hmm = {r1..r9: predict_proba}          # Σ=1.0

# 覆盖层 3 特殊态输出
P_overlay = {r10, r11, r12: rule_score}   # 各 [0,1]，独立

# 合并：覆盖层概率压缩 HMM 概率质量
overlay_mass = Σ P_overlay                 # 覆盖层总概率
hmm_scale = 1 − overlay_mass              # HMM 被压缩

P(r1..r9) = P_hmm(r_i) × hmm_scale
P(r10..r12) = P_overlay(r_i)

# 归一化（防浮点误差）
P = normalize(P(r1..r12))                 # Σ=1.0
```

> **设计理由**：特殊态触发时，覆盖层"覆盖"HMM 的判断——CRISIS 触发时 P(r10) 上升，P(r1..r9) 等比压缩。无特殊态时 overlay_mass=0，P(r1..r9)=P_hmm，退化为纯 HMM。

### 3.4 子模块③：ConfidenceSignal（30_multi_strategy_concurrency §2.2）

> **直接引用 RegimeMetaAllocator blueprint §3.2.1**——计算逻辑在本模块（regime 检测器侧），消费在 RegimeMetaAllocator。

```
ConfidenceSignal = base_confidence(max(P)) × rarity_discount(dominant_frequency)

base_confidence:
  max(P) < 60% → 0.3    (强收缩)
  max(P) 60-80% → 0.6   (中度收缩)
  max(P) 80-95% → 0.85  (轻度收缩)
  max(P) > 95% → 1.0    (满部署)

rarity_discount:
  常见态 >5% → 1.0
  中等态 1-5% → 0.85
  稀有态 <1% → 0.7
```

### 3.5 子模块④：RiskSignal（10_regime_detector_spec §5.3）

> **直接引用 10_regime_detector_spec §5.3.3 聚合公式 + RegimeMetaAllocator blueprint §3.2.2**——13 参数计算在本模块，消费在 RegimeMetaAllocator。

```
RiskSignal = clamp[ 0.30,  RiskBase × 共振惩罚 + 机会恢复,  1.00 ]

  RiskBase   = min( 参数#1-10, #12 的系数 )            # 11 风险参数取最严
  共振惩罚   = 1 − 0.05 × max(0, 异常参数数 − 1)         # 下限 ×0.80
  机会恢复   = #11 鬼故事抵消 + #13 利空不跌抵消          # 上限 +0.25
```

13 参数清单见 10_regime_detector_spec §5.3.1-§5.3.2。

### 3.6 子模块⑤：Shrinkage（可开关，11_regime_backtest_validation_plan C1 验证）

```
if shrinkage_enabled:
    Shrinkage = ConfidenceSignal × RiskSignal       # 正常模式
else:
    Shrinkage = 1.0                                  # 验证模式（C1 开/关对比基准组）
```

> **可开关设计**：11_regime_backtest_validation_plan C1 是一票否决验证——对比"Shrinkage=1.0（关）"vs"Shrinkage=ConfidenceSignal×RiskSignal（开）"。开关由 config 控制，回测框架切换。

## 4. 关键不变量 (INVARIANTS)

- `RegimeProbabilities.probabilities` 中 Σ P(ri) = 1.0（12 维归一化）
- `Shrinkage ∈ [0.063, 1.0]`（ConfidenceSignal × RiskSignal，最低 0.3×0.7×0.3=0.063）
- `shrinkage_enabled=False` 时 Shrinkage **恒等于 1.0**（C1 验证基准组）
- 8 转换触发**必须**输出 `TransitionTriggered` 事件（含评分明细，供 B4 验证）
- HMM 解码用**因果 Viterbi**（防前视，§9 行业对照）
- HMM **walk-forward 季度重拟合**（防模型老化，对照 Morwane）
- `P_overlay` 各值 ∈ [0, 1]，`overlay_mass` ≤ 1.0
- 无特殊态触发时 `overlay_mass=0`，退化为纯 HMM（P(r1..r9)=P_hmm）

## 5. 错误契约

- `HMMFittingError` (ZA-SIG-0001): HMM 拟合失败（特征缺失/NaN/不收敛）
- `InvalidFeatureError` (ZA-SIG-0002): RegimeFeatures 格式非法/缺失必需字段
- `OverlayRuleError` (ZA-SIG-0003): 覆盖层规则计算异常（评分维度缺失/阈值非法）
- `ShrinkageCalculationError` (ZA-SIG-0004): ConfidenceSignal/RiskSignal 计算异常
- `ProbabilityNormalizationError` (ZA-SIG-0005): 12 维归一化失败（Σ≠1 / 含 NaN）

## 6. 测试规划

### Phase 1 测试 (~30)
- HMM 9态：拟合/predict_proba 输出 9 维/Σ=1/因果 Viterbi 防前视
- 覆盖层：3 特殊态触发/不触发/8 转换评分计算
- 12 维合并：无覆盖层退化为纯 HMM/覆盖层压缩 HMM 概率/归一化
- ConfidenceSignal：4 档映射/稀有态折扣/边界值
- RiskSignal：13 参数聚合/最严主导/共振惩罚/机会恢复（mock 输入）
- Shrinkage：开/关切换/shrinkage_enabled=False 恒=1.0/上下界
- TransitionTriggered 事件：8 转换各触发一次/评分明细完整
- RegimeProbabilities 输出：12 维/Σ=1/字段完整性

### Phase 2 测试 (~15)
- walk-forward 季度重拟合/模型老化检测
- 7 月案例验证（10_regime_detector_spec §5.3.4 五时间点 Shrinkage 值吻合）
- 历史事件验证（11_regime_backtest_validation_plan B4：2008/2015/2020/2024 转换触发时点 ±5 交易日）

## 7. 依赖

### 7.1 已就绪 (Phase 1 可用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `hmmlearn` 库（GaussianHMM）
- config（shrinkage_enabled / hmm_params）

### 7.2 待建 (前置)
- RegimeFeatures 特征工程（ClickHouse → 波动率分位/趋势斜率/相关性/涨跌家数/量能）— §8.2 步骤1
- OverlaySignals 数据源（10_regime_detector_spec §4 各转换的 Capitulation/Wyckoff/VIX 等信号）— ❌ 待建
- RiskSignalInputs 13 参数数据源 — ❌ 待建

### 7.3 消费者
- RegimeMetaAllocator (MOD-PA-007)：消费 RegimeProbabilities + Shrinkage（核心消费者）
- BM-BT-03-E 验证：消费 RegimeProbabilities（B1 校准度 / B2 CRPS）
- BM-BT 验证：消费 TransitionTriggered 事件（B4 转换触发准确性）
- MOD-POS-001 position_sizing_engine：消费 dominant_regime（市场状态→仓位上限映射，§5.2）

### 7.4 降级策略

| 上游缺失 | 降级模式 | 影响 |
|---------|---------|------|
| RegimeFeatures | HMM 无法运行 → 输出均匀分布 P=1/12 | ConfidenceSignal=0.3（强收缩） |
| OverlaySignals | 覆盖层不触发 → 退化为纯 HMM 9 态 | 无特殊态检测（CRISIS/RECOVERY/BREAKOUT） |
| RiskSignalInputs | RiskSignal=1.0（无市场风险信号） | Shrinkage 仅由 ConfidenceSignal 驱动 |
| hmmlearn 拟合失败 | 沿用上次模型 / 均匀分布 | 标记 degraded |

## 8. 分阶段施工里程碑

### Phase 1: HMM 9态 + 覆盖层 + Shrinkage 框架（P0）

**目标**：12 维概率输出 + Shrinkage 计算（可开关）+ 转换触发事件，特征用 mock/降级

**范围**（§8.2 实现步骤）：
1. 特征工程框架（ClickHouse → RegimeFeatures，Phase 1 可用 mock）
2. HMM 9态训练（hmmlearn GaussianHMM，predict_proba 输出 9 维）
3. D-SIGNAL-68 覆盖层（3 特殊态规则触发 + 8 转换评分）
4. 12 维概率合并归一化
5. ConfidenceSignal 计算（4 档 + 稀有态折扣）
6. RiskSignal 计算框架（13 参数聚合，Phase 1 部分参数可 mock）
7. Shrinkage 计算（可开关，shrinkage_enabled）
8. RegimeProbabilities + TransitionTriggered 输出
9. 降级模式

**不包含**：walk-forward 重拟合、真实特征工程、全部 13 参数接入

**预计**：~600 行代码 + ~30 测试

### Phase 2: 真实特征 + walk-forward + 验证接入（依赖数据就绪）

**前置**：ClickHouse 特征工程 + OverlaySignals 数据源就绪

**范围**：
- 真实 RegimeFeatures（波动率分位/趋势斜率/相关性/涨跌家数/量能）
- walk-forward 季度重拟合
- 真实 13 参数 RiskSignal
- 7 月案例验证 + 历史事件验证（11_regime_backtest_validation_plan B4）
- 接入 BM-BT-03-E 验证（B1/B2）

### Phase 3: 回测验证 + 生产化（11_regime_backtest_validation_plan 全流程）

**范围**：
- 11_regime_backtest_validation_plan Phase 1-5 回测验证（C1 开/关对比是一票否决）
- 验证通过 → depgraph build_status → generated, design_maturity → production
- 验证失败 → regime 不部署，回退静态等权（11_regime_backtest_validation_plan §10）

## 9. 设计决策记录

| 决策 | 理由 |
|------|------|
| 完整 12 态（非先简化） | 11_regime_backtest_validation_plan §10 已决策：直接实现完整 12 态，验证后基于证据简化，避免重复工作 |
| hmmlearn GaussianHMM | 11_regime_backtest_validation_plan §10 已决策：行业主流（Morwane/fibalgo 均用），与开源生态一致 |
| 因果 Viterbi 解码 | 防前视（§9 行业对照：Morwane causal Viterbi），回测不能用未来信息 |
| walk-forward 季度重拟合 | 防模型老化，对照 Morwane，11_regime_backtest_validation_plan E1 鲁棒性验证 |
| Shrinkage 可开关 | 11_regime_backtest_validation_plan C1 一票否决验证：对比开/关，不通过则 regime 不部署 |
| 12 维概率输出（非硬标签） | 11_regime_backtest_validation_plan B1/B2 验证需要概率分布（CRPS/校准度），硬标签无法验证概率质量 |
| 转换触发事件记录 | 11_regime_backtest_validation_plan B4 验证：8 转换触发时点 ±5 交易日吻合 ≥6/8 |
| 覆盖层压缩 HMM 概率 | 特殊态触发时覆盖 HMM 判断，无触发时退化为纯 HMM，平滑兼容 |
| RiskSignal 在本模块计算 | 13 参数是市场风险指标，属于 regime 检测范畴；RegimeMetaAllocator 是消费者 |
| 不做宏观 regime | 现有 gov_drift/regime_detector.py 是宏观 4 态（经济周期），与本模块（交易 12 态）无关 |

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/regime/__init__.py` | ⚠️ 骨架 | |
| `src/zephyr/regime/core/__init__.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/regime/test_chip_distribution_engine.py` | ✅ 已实现 | |
| `tests/regime/test_regime_detector.py` | ✅ 已实现 | |
| `tests/regime/test_trend_features.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-REGIME-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-REGIME-001` 的 6 个 file 节点 | production | `extract_depgraph.py --modules MOD-REGIME-001` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-REGIME-001 | MOD-REGIME-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 6 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
