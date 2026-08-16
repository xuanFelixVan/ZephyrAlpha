---
module_id: MOD-PA-007
title: "Regime元分配器蓝图 — Shrinkage风险节流+PerformanceScore后验分配（A模型·meta层）"
doc_type: blueprint
status: Active
version: "0.2.0"
design_maturity: production
build_status: stable
ttl: permanent
layer: L02_pf_alloc
layer_name: pf_alloc
functional_domain: pf_alloc
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-06"
last_updated: "2026-08-15"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-PA-007 RegimeMetaAllocator — Regime元分配器 蓝图

> **module_id**: MOD-PA-007 | **域**: D_PF_ALLOC | **层**: L02 组合分配
> **优先级**: P0 | **成熟度**: production | **建设标记**: ✅ v1.0.0 production（commit 81c7687540，55 用例防护网 2026-08-15 重建；启用时机归 30号 §4.2 第二阶段）
> **SSoT**: depgraph MOD-PA-007 | **设计真源**: [30_multi_strategy_concurrency.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.2（RegimeMetaAllocator + 分配公式 + 置信度映射 + 稀有态处理）
> **Shrinkage 真源**: [10_regime_detector_spec.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md) §5（Shrinkage = ConfidenceSignal × RiskSignal，二维公式 + 13 参数阈值 + 聚合公式）
> **开源实证**: [Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book) — regime 做 risk-throttle Sharpe +1.43 / MaxDD −10.3%，regime 做 alpha-timing Sharpe +0.87（降）

## 1. 定位

Regime 元分配器——A 模型（[30_multi_strategy_concurrency](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.2）的 meta 层。消费 regime 检测器的 **7 维灰度概率分布**（4 HMM 基态 + 3 overlay 特殊态，取 max(P)）+ 各策略 PerformanceScore（60 日 Sortino 映射），通过 **Shrinkage 风险节流**（只减不增）+ **PerformanceScore 后验分配**，产出各 StrategyBook 的资金预算占比。

属 **B 类核心业务模块**（多源融合 + 风险节流 + 动态分配），Shrinkage 阈值/PerformanceScore 映射为 C 类可调参数。

### 1.1 核心裁定（30_multi_strategy_concurrency §2.2，2026-08-05）

> **移除 RegimeScore，regime 仅通过 Shrinkage 做风险节流。**
> - regime **不做 alpha 择时**（开源实证 Morwane：择时降 Sharpe 1.43→0.87，节流降 MaxDD −14.2%→−10.3%）
> - 误差不对称：alpha 择时判错=主动亏损，风险节流判错=机会成本
> - 策略亲和性由 **PerformanceScore（后验 PnL）自然捕获**——momentum 在趋势态表现好→滚动 Sharpe 上升→有机获得更多 budget，无需 regime 前瞻下注
> - **regime 只回答"现在该多谨慎"，不回答"现在该偏向哪个策略"**

### 1.2 分层边界

| 层 | 模块 | 职责 |
|---|---|---|
| regime 源 | regime 检测器 (MOD-REGIME-001) | 输出 7 维灰度概率（4 HMM 基态 + 3 overlay 特殊态） |
| **meta 分配** | **RegimeMetaAllocator (本模块)** | **Shrinkage 节流 + PerformanceScore 后验分配 → budget 占比** |
| 策略层 | StrategyBook (MOD-POS-020) | 收到 budget 数字，选股+粗仓位（不知道市场态） |

**数据流**：`regime检测器(灰度P) → RegimeMetaAllocator(Shrinkage+Performance) → budget_i → StrategyBook_i`

> **关键纪律**（30_multi_strategy_concurrency §2.2）：市场态是 meta 层的事，StrategyBook 本身不知道市场态，只收到 budget 数字。

### 1.3 不做什么

- **不做 alpha 择时**（移除 RegimeScore，30_multi_strategy_concurrency §2.2 裁定）
- **不重定向资金到"regime 友好"策略**（PerformanceScore 后验捕获，无需前瞻下注）
- **不做 MVO / 协方差估计**（30_multi_strategy_concurrency §3.1 拒绝）
- **不做选股 / 仓位裁决**（归 StrategyBook / MOD-POS-001）
- **不执行交易**（归 D-EX-CORE）

## 2. 输入 / 输出

### 2.1 输入

| 方向 | 内容 | 契约/事件 | 来源 | 就绪 |
|------|------|-----------|------|:----:|
| 核心 | RegimeProbabilities（7 维灰度概率：4 HMM 基态 + 3 overlay 特殊态，取 max(P)） | CTR-SIG-012 | regime 检测器 (MOD-REGIME-001, D_REGIME) | ✅ production |
| 核心 | PerformanceScore[]（各策略 60 日滚动 **Sortino** 映射 [0.5,1.5]，MAR=Rf=2%） | CTR-PA-007-P | `compute_performance_score()` 静态方法已落地（本模块）；策略 PnL 数据源待首批实盘 | ⚠️ 待 PnL |
| 核心 | RiskSignalInputs（13 参数市场风险输入，本模块消费 risk_base/resonance_penalty/opportunity_recovery 三键） | CTR-SIG-013 | 10_regime_detector_spec §5.3 数据源（13 参数聚合逻辑归 10号） | ✅ production |
| 配置 | Base[]（先验权重，等权 1/N 或人工先验） | config | 配置文件 | ✅ config |
| 配置 | StrategySampleDays[]（各策略上线交易日数，<30 冷启动强制 PerformanceScore=1.0 中性） | CTR-PA-007-S | StrategyBook 注册 | ⚠️ 待 PnL |
| 事件 | StrategyRebalanced（策略再平衡完成，触发再平衡频率控制） | E-POS-20 | StrategyBook | ❌ 待建 |

### 2.2 输出

| 方向 | 内容 | 契约/事件 | 去往 |
|------|------|-----------|------|
| 输出 | BudgetAllocation（各策略 budget 占比 + 全局 Shrinkage） | CTR-PA-007 | StrategyBook (MOD-POS-020) |
| 事件 | BudgetChanged（budget 变动，触发三级升级） | E-PA-07 | BudgetChangeHandler (MOD-POS-022) |
| 事件 | ShrinkageDetail（Shrinkage 计算明细，归因用） | E-PA-08 | Trader + 归因系统 |

### 2.3 BudgetAllocation 定义 (CTR-PA-007)

> **两个层次**：`allocation_i`（相对占比，Σ=1.0）回答"偏向哪个策略"；`global_shrinkage`（总暴露因子）回答"现在该多谨慎"。StrategyBook 收到的 **effective_budget = allocation_i × global_shrinkage**。

| 字段 | 类型 | 说明 |
|------|------|------|
| allocations | dict[str, float] | {strategy_id: 相对占比}，Σ=1.0，floor 5%~cap 40% |
| global_shrinkage | float | 全局风险节流因子（0.05~1.0；常规 floor 0.09，CRISIS 态降级 0.05），控制总暴露 |
| effective_budgets | dict[str, float] | {strategy_id: allocation_i × global_shrinkage}，StrategyBook 实收 |
| shrinkage_detail | ShrinkageDetail | Shrinkage 计算明细（归因用） |
| perf_scores | dict[str, float] | 各策略 PerformanceScore 回显（审计用，冷启动强制后值） |
| sortino_sharpe_gaps | dict[str, float] | Sortino/Sharpe gap 监控（四件套 #3，默认空 dict 待 PnL 管线） |
| rebalance_allowed | bool | 当日是否允许再平衡（字段已落地默认 True；频率控制逻辑待 StrategyRebalanced 事件管线） |
| created_at | datetime | 创建时间 |
| schema_version | str | "1.0" |

**ShrinkageDetail 子结构**（归因用，与代码 dataclass 一致）：

| 字段 | 类型 | 说明 |
|------|------|------|
| confidence_signal | float | max(P) 四档映射值 ∈{0.3,0.6,0.85,1.0} |
| risk_signal | float | RiskSignal 值 ∈[0.30,1.00]（clamp 后） |
| raw_shrinkage | float | confidence × risk（floor 裁剪前） |
| final_shrinkage | float | ≥ floor（裁剪后，即 global_shrinkage） |
| shrinkage_enabled | bool | C1 验证开关（False → 全 1.0 回退等权） |
| is_crisis | bool | D-SIGNAL-68 overlay 是否触发 CRISIS 态（floor 0.09→0.05） |

## 3. 核心规则

### 3.1 分配公式（30_multi_strategy_concurrency §2.2）

```
allocation_i = normalize( Base_i × PerformanceScore_i )      # global_shrinkage 是全局的，归一化时约掉
effective_budget_i = allocation_i × global_shrinkage

其中:
  global_shrinkage = ConfidenceSignal × RiskSignal          # 全局风险节流（regime 驱动）
  冷启动: 上线 <30 交易日 → PerformanceScore_i 强制 1.0 中性  # v1.0.0 施工裁定，替代原 SampleShrinkage 连续收缩
```

> **关键设计**（30_multi_strategy_concurrency §2.2 + 34号 §3.1 实现注记）：`global_shrinkage` 是全局的（所有策略共享），在 `normalize` **外部**控制总暴露；冷启动中性在 `normalize` **内部**影响相对分配（PerformanceScore=1.0 时该策略退回纯 Base 先验）。这精确实现了裁定——"regime 只回答多谨慎（global_shrinkage），不回答偏向谁（normalize 内由 Base×PerformanceScore 决定）"。

### 3.2 Shrinkage 二维公式（10_regime_detector_spec §5）

```
global_shrinkage = ConfidenceSignal × RiskSignal
```

#### 3.2.1 ConfidenceSignal（置信度→风险节流，10_regime_detector_spec §5.1）

> max(P) 为当前最高态概率，来自 regime 检测器灰度输出。

**base_confidence 映射**（30_multi_strategy_concurrency §2.2）：

| max(P) | base_confidence | 语义 |
|--------|:---------------:|------|
| < 60% | 0.3 | 强收缩，回退等权/指数（"不确定时别赌方向"） |
| 60-80% | 0.6 | 中度收缩，整体保守部署 |
| 80-95% | 0.85 | 轻度收缩，正常部署 |
| > 95% | 1.0 | 接近无收缩，满部署 |

**稀有态额外折扣**（30_multi_strategy_concurrency §2.2 稀有态处理）——⚠️ **当前冻结未激活**：实测 4 态频率 r1 27.6%/r2 37.4%/r3 14.9%/r4 20.2% 全部 >5% 常见态（11号 §0.5.2），稀有态分支不触发，v1.0.0 代码未实现 rarity_discount（34号 §3.2.5：为原 12 态设计的向前兼容机制，加态时自动生效无需重写）。设计值备查：

| 态频率 | rarity_discount | 说明 |
|--------|:---------------:|------|
| 常见态 > 5% | 1.0 | 置信度天然高 |
| 中等态 1-5% | 0.85 | 中度收缩 |
| 稀有态 < 1% | 0.7 | 稀有态检测置信度天然低，重收缩 |

```
ConfidenceSignal = base_confidence(max(P))              # 当前实现（4 态全常见，无 rarity 项）
# 加态后设计: ConfidenceSignal = base_confidence(max(P)) × rarity_discount(dominant_regime_frequency)
```

#### 3.2.2 RiskSignal（13 参数市场风险，10_regime_detector_spec §5.3）

> **直接引用 10_regime_detector_spec §5.3.3 聚合公式**，本模块是 RiskSignal 的消费者，不是计算者。RiskSignal 由 regime 检测器侧的 13 参数聚合产出。

```
RiskSignal = clamp[ 0.30,  RiskBase × 共振惩罚 + 机会恢复,  1.00 ]

  RiskBase   = min( 参数#1-10, #12 的系数 )            # 11 风险参数取最严
  共振惩罚   = 1 − 0.05 × max(0, 异常参数数 − 1)         # 每多一个异常再扣 5%，下限 ×0.80
  机会恢复   = #11 鬼故事抵消 + #13 利空不跌抵消          # 上限 +0.25
```

| 信号 | 含义 | 来源 |
|------|------|------|
| #1-10, #12 | 11 个风险下调参数（波动率/量能/形态/时间/空间/相关性/涨跌家数/虹吸/背离/斜率/筹码）四档 1.0/0.85/0.6/0.3 | 10_regime_detector_spec §5.3.1 |
| #11 | 新闻情绪反向（双向：鬼故事抵消 / 利好出货下调 / 天灾避险下调） | 10_regime_detector_spec §5.3.2 |
| #13 | 利空不跌验证（纯机会：低开拉回+0.10 / 平开高开+0.15 / 连续钝化+0.20） | 10_regime_detector_spec §5.3.2 |

> 本模块消费 `RiskSignal`（标量）+ `RiskSignalInputs`（13 参数明细，归因用）。计算逻辑在 regime 检测器侧，本模块只做 `global_shrinkage = ConfidenceSignal × RiskSignal`。

#### 3.2.3 Shrinkage 上下界

| 场景 | Shrinkage 值 | 总暴露 |
|------|:-----------:|:------:|
| 满部署（max(P)>95% + 无风险异常） | 1.0 × 1.0 = **1.0** | 100% |
| 正常部署（max(P) 80-95% + 轻度异常） | 0.85 × 0.85 ≈ **0.72** | 72% |
| r4 熊市极端（max(P)<60% + RiskSignal=0.3） | 0.3 × 0.3 = **0.09**（SHRINKAGE_FLOOR 兜底） | 9% |
| ⑩ CRISIS 特殊态（D-SIGNAL-68 overlay 触发） | floor 降级 **0.05**（对齐 31号 §2.4.3 crisis cap，firm 层硬裁剪兜底） | ≤5% |

### 3.3 PerformanceScore（后验分配，30_multi_strategy_concurrency §2.2 + 34号 §3.2.2 Sortino 选型）

> **策略亲和性由后验 PnL 自然捕获**——无需 regime 前瞻下注。

| 步骤 | 逻辑 |
|------|------|
| 1. 计算 | 60 日滚动 **Sortino**（非 Sharpe）：`Sortino = (R_p − MAR) / σ_d`，MAR=Rf=2% 年化（货币基金），下行偏差 σ_d 只统计 `R_daily < MAR` 的日子、**分母用总样本量 n-1**（ddof=1，CFA 2026 共识，非 n_downside-1） |
| 2. 映射 | Sortino [0, 2.0] 线性映射到 [0.5, 1.5]（Sortino≤0→0.5；=1.0→1.0；≥2.0→1.5） |
| 3. 防极端 | clip 到 [0.5, 1.5]（差策略不会被清零，好策略不会被独占）+ 分配层 floor 5%/cap 40% 双兜底 |
| 4. 样本防护 | downside 观测 <15 → 强制 1.0 中性（四件套 #1，防小样本 inflated values）；Sortino/Sharpe gap 两级监控（>1.8 警告 / >2.25 严重复核，四件套 #3） |
| 5. 冷启动 | 上线 <30 交易日 → PerformanceScore=1.0 中性（`_apply_cold_start_neutral` 强制，防上游误传非中性值） |

> **为何 Sortino 而非 Sharpe**（34号 §3.2.2 裁定）：PerformanceScore 目的是"识别亏损策略"做节流，Sortino 只惩罚下行波动与目的对齐；A 股打板策略涨停板 upside 波动在 Sharpe 下被误罚 → Sortino 不低估；Sharpe 保留为对照指标（gap 监控）。

**映射示例**（初始值，待首批策略 PnL 校准）：

| 60日 Sortino | PerformanceScore | 语义 |
|-------------|:----------------:|------|
| ≤ 0 | 0.5 | 差策略，budget 减半（floor 5% 兜底防饿死） |
| 1.0 | 1.0 | 中性，不调整 |
| ≥ 2.0 | 1.5 | 优秀，budget ×1.5（cap 40% 兜底防集中） |

> **为何不直接用原始 Sortino 而要映射**：原始 Sortino 可能负值或极端，直接乘会破坏归一化。映射到 [0.5,1.5] 保证差策略不被清零（floor 0.5 留验证机会）、好策略不独占（cap 1.5 防集中）。

### 3.4 冷启动中性（v1.0.0 施工裁定，替代原 SampleShrinkage 连续收缩设计）

| 上线交易日数 | PerformanceScore | 说明 |
|---------|:---------------:|------|
| < 30 交易日 | **强制 1.0 中性** | `_apply_cold_start_neutral`：即使上游误传非中性值也强制覆写（log warning），样本不足不参与后验分配 |
| ≥ 30 且 downside ≥15 | 正常 Sortino 映射 | 30 日门槛留余量（A 股约 38 交易日积累 15 个 downside 样本） |

> **为何从连续收缩（0.5→1.0 线性插值）改为硬切换中性**：downside 样本 <15 时 Sortino 系统性偏高（ecassets/foliolab 2026 警告 inflated values），连续插值会把"虚假精确的 Sortino"引入分配；硬切换 + floor/cap 兜底更简单且可解释（34号 §3.2.2 防护四件套 #1）。贝叶斯收缩（MRC arXiv:2605.24490 权重随样本量渐变）登记为远期候选，MVP 不采纳。

### 3.5 归一化 + floor/cap 硬约束（30_multi_strategy_concurrency §2.2 + 34号 §3.2.4）

```
raw_i = Base_i × PerformanceScore_i                       # Shrinkage 全局，归一化时约掉不参与
allocation_i = raw_i / Σ(raw)                              # 归一化，Σ=1.0
allocation_i = water_filling_project(allocation_i)         # floor 5% / cap 40% 投影（≤5 轮迭代）
# 越界策略固定到 floor/cap，剩余 budget 按比例只重分给未越界策略（防再归一化拉回越界）
# 无解兜底：N × cap < 1.0 → 放宽 cap 到 1-(N-1)×floor（优先保 floor 防饿死，log WARNING 上报）
```

| 约束 | 值 | 目的 |
|------|:--:|------|
| floor | ≥ 5% | 防饿死（新策略至少有最小 budget 验证） |
| cap | ≤ 40% | 防集中（单策略不超过 40%，即使 PerformanceScore 极高） |

### 3.6 再平衡频率控制（契约预留）

| 规则 | 说明 |
|------|------|
| ≤ 1 次/交易日 | 防过度交易（30_multi_strategy_concurrency 引用 MOD-PA-003 §3.4） |
| 当日已再平衡 → rebalance_allowed=False | 沿用上次 BudgetAllocation |
| 触发例外 | regime 突变（max(P) 跨越置信度档位）+ Kill Switch 事件 → 允许紧急再平衡 |

> **落地状态**：`rebalance_allowed` 字段已随 v1.0.0 落地（默认 True）；当日阻断/例外触发逻辑依赖 StrategyRebalanced 事件管线（E-POS-20），待首批策略实盘联调时实现。

## 4. 关键不变量 (INVARIANTS)

- `Σ allocation_i = 1.0`（归一化 + water-filling 投影后成立；⚠️ 退化输入例外：全部策略同时越界且无 free 策略可重分时，floor/cap 硬约束优先于 Σ=1.0，见 34号 §3.2.4）
- `allocation_i ∈ [5%, 40%]`（floor/cap 硬约束）
- `global_shrinkage ∈ [0.05, 1.0]`（常规 floor 0.09 = 0.3×0.30；CRISIS 态降级 0.05 对齐 31号 §2.4.3 crisis cap）
- `Σ effective_budget_i = global_shrinkage`（总暴露 = 全局收缩因子）
- `effective_budget_i = allocation_i × global_shrinkage`（StrategyBook 实收）
- Shrinkage **只减不增**（≤1.0，风险节流非加杠杆）
- 再平衡频率 ≤ 1 次/交易日（紧急例外除外）——契约预留，字段已落地逻辑待事件管线
- 冷启动策略 PerformanceScore=1.0（<30 交易日强制中性，防上游误传）

## 5. 错误契约

- `AllocationError` (ZA-PA-0007): 策略列表为空 / base_weights 无法确定（✅ 代码已定义，`allocate()` 入口抛出）
- `ShrinkageDisabled` (ZA-PA-0008): 头部 [ERROR_CONTRACT] 声明预留，⚠️ 代码未实例化（2026-08-15 漂移取证）——当前 `shrinkage_enabled=False` 走 `global_shrinkage=1.0` 回退等权不抛错（C1 一票否决机制）
- 原设计稿的 `InvalidRegimeInputError`/`InvalidPerformanceScoreError`/`AllocationNormalizationError`/`ShrinkageCalculationError`（ZA-PA-0007~0010 旧编号）未随 v1.0.0 实现，移除防误导

## 6. 测试规划

### ✅ 已落地（2026-08-15 重建，tests/pf_alloc/test_regime_meta_allocator.py，55 用例两轮全绿）

- **TestConfidenceSignal(8)**：四档映射 + 0.60/0.80/0.95 边界 + list/ndarray 输入
- **TestRiskSignal(4)**：缺省=1.0 / 正常聚合 / clamp 0.30 下界 / clamp 1.00 上界
- **TestShrinkage(7)**：开关回退全 1.0 / 双因子乘法 / 只减不增 / 0.09 floor 角点 / CRISIS floor 降级 0.05（monkeypatch 参数域白盒）/ 审计字段 / crisis 标志透传
- **TestNormalizeAndClip(8)**：比例透传 / 归一化 / floor 强制 / cap 强制 / water-filling 保 free 比例 / N=2 无解兜底放宽 cap / 全零回退等权 / 多越界收敛
- **TestRawAllocation(3)**：Base×Perf 精确乘法 / 缺失 base 等权补齐 / allocations 对 Shrinkage 开关不变（解耦证明）
- **TestAllocate(9)**：三策略 happy path / Σ=1.0 不变量 / effective=alloc×shrinkage 恒等 / 空策略 AllocationError / 开关禁用 / 冷启动强制中性 / CRISIS 透传 / 审计字段 / 人工先验保留
- **TestComputePerformanceScore(8)**：冷启动中性 / 空收益 / downside<15 强制中性 / 负 Sortino→0.5 / 高 Sortino→1.5 / 线性映射中点 / **下行偏差分母 n-1 CRITICAL 回归** / upside 波动 Sortino>Sharpe
- **TestEdgeCases(8)**：N=1 / N=2 / list 输入 / 4 态实测向量 / 7 态 overlay 向量 / 缺省风险键 / 全冷启动保先验 / 退化全越界

### Phase 2 联调（待首批策略实盘）

- 接入 regime 检测器真实 7 维灰度概率 + 13 参数 RiskSignal 聚合输出
- PerformanceScore PnL 反馈联调（StrategyRebalanced 事件 → Sortino 更新 → allocation 调整）
- 归因联调（ShrinkageDetail 完整链）
- 7 月案例验证（10_regime_detector_spec §5.3.4 五个时间点 Shrinkage 值吻合）

## 7. 依赖

### 7.1 已就绪 (Phase 1 可用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- Base 权重配置（config 驱动）

### 7.2 依赖状态（2026-08-15 盘点）
- regime 检测器 (MOD-REGIME-001, D_REGIME 域, RegimeProbabilities + RiskSignal) — ✅ production（commit 191a17432f，7 维概率 + risk_signal_builder）
- StrategyBook (MOD-POS-020, PerformanceScore + StrategySampleDays 反馈) — ✅ production（70 测试）；PnL 反馈管线待首批策略实盘
- BudgetChangeHandler (MOD-POS-022, BudgetChanged 事件消费) — ✅ production（47 测试；33号 设计文档 2026-08-12 重建 active v1.0.0）

### 7.3 消费者
- StrategyBook (MOD-POS-020)：消费 effective_budget_i
- BudgetChangeHandler (MOD-POS-022)：消费 BudgetChanged 事件（触发三级升级）
- Trader + 归因系统：消费 ShrinkageDetail（Shrinkage 归因）

### 7.4 与 MOD-PA-003 的关系（待协调）

| MOD-PA-003 功能 | A 模型下的归属 | 状态 |
|----------------|---------------|------|
| 容量约束 | MOD-PA-007 cap 40% 部分覆盖 + FirmRiskAggregator 组合级裁剪 | 部分替代 |
| MaxDD 减仓 | StrategyBook Drawdown Protocol（单策略级，§2.5）+ MOD-PA-007 Shrinkage（组合级） | 已被覆盖 |
| 冷启动缩放 | StrategyBook 灰度发布（5%→100%）+ MOD-PA-007 冷启动中性（<30 交易日 PerformanceScore=1.0） | 已被覆盖 |
| 再平衡频率 | MOD-PA-007 §3.6（≤1次/日） | 已被覆盖 |

> **初步判断**：MOD-PA-003 大部分功能被 A 模型其他模块覆盖，可能降级/重构。但 MOD-PA-003 有活跃生产依赖，具体处置待 MOD-PA-003 blueprint 范围内决定（参考 30_multi_strategy_concurrency §7.3 MOD-PF-002 暂缓弃用先例）。

### 7.5 降级策略

> 当前已实现的降级路径 = `shrinkage_enabled=False`（global_shrinkage=1.0 回退等权，C1 一票否决机制）。下表为设计意图，输入缺失自动降级逻辑未随 v1.0.0 实现（allocate 要求显式入参）。

| 上游缺失 | 降级模式 | 影响 |
|---------|---------|------|
| regime 检测器 | ConfidenceSignal=0.3（强收缩默认）+ RiskSignal=1.0（无风险信号） | 保守部署（设计意图，未实现自动触发） |
| PerformanceScore | 全部=1.0（等权，纯 Base 分配） | 跳过后验分配 |
| RiskSignal 13 参数 | RiskSignal=1.0（缺省三键默认，已实现） | Shrinkage 仅由 ConfidenceSignal 驱动 |

## 8. 分阶段施工里程碑

### Phase 1: Shrinkage 框架 + 等权分配 —— ✅ 已落地（v1.0.0，commit 81c7687540）

**已交付**：ConfidenceSignal 四档映射 / RiskSignal 消费接口（三键聚合 + clamp）/ global_shrinkage 二维公式（含 CRISIS floor 降级）/ PerformanceScore Sortino 映射框架 / 冷启动中性（替代 SampleShrinkage）/ water-filling 归一化裁剪（含 N=2 无解兜底）/ BudgetAllocation 输出（CTR-PA-007）/ shrinkage_enabled 降级开关。

**实测**：~540 行代码 + 55 测试（2026-08-15 重建，两轮全绿）。

### Phase 2: 接入实盘反馈链 —— ⚠️ 部分落地（待首批策略 PnL）

**已就绪**：regime 检测器 7 维概率 + RiskSignal 均 production；`compute_performance_score()` 静态方法落地可算 60 日 Sortino。
**待实盘**：策略 PnL 数据源（60 日 Sortino 实算输入）/ StrategyRebalanced 事件反馈环 / 7 月案例验证 / 归因联调。

### Phase 3: 生产化 —— ✅ 主体达成

- depgraph build_status=generated, design_maturity=production ✅
- 55 用例回归防护网 ✅（2026-08-15 重建闭环）
- 与 StrategyBook + BudgetChangeHandler 联调、性能 SLA 验证（<30ms P50，N≤5）——待首批策略实盘联调时验证

## 9. 设计决策记录

| 决策 | 理由 |
|------|------|
| 移除 RegimeScore（regime 不做 alpha 择时） | 30_multi_strategy_concurrency §2.2 裁定 + Morwane 开源实证：择时降 Sharpe 1.43→0.87，节流降 MaxDD；误差不对称（择时判错=亏损，节流判错=机会成本） |
| global_shrinkage 在 normalize 外部（控制总暴露） | 精确实现"regime 回答多谨慎"：全局因子不改变相对分配，只控制总暴露 |
| 冷启动中性替代 SampleShrinkage 连续收缩（v1.0.0 施工裁定） | downside 样本 <15 时 Sortino 系统性偏高（inflated values），连续插值引入虚假精确；<30 交易日硬切 1.0 中性 + floor/cap 兜底更简单可解释（34号 §3.2.2 防护四件套 #1） |
| PerformanceScore 用 Sortino 非 Sharpe，映射 [0.5,1.5] | 只惩罚下行波动与"识别亏损策略"目的对齐；A 股打板涨停板 upside 波动在 Sharpe 下被误罚（34号 §3.2.2）；MAR=Rf=2% 保持与 Sharpe 分子一致，gap 干净反映上行偏态 |
| PerformanceScore 后验捕获策略亲和性 | momentum 趋势态表现好→Sortino 上升→有机获更多 budget，无需 regime 前瞻下注（避免估计误差放大） |
| water-filling 投影替代"裁剪+全局再归一化"（v1.0.0 施工改进） | 原伪代码在 N=2/cap 受限场景收敛失败（被裁剪值再归一化时拉回越界）；固定越界值+只按比例重分未越界部分（34号 §9 v2.7.0） |
| CRISIS 态 floor 降级 0.09→0.05 | ⑩CRISIS 特殊态 firm 层 5% 硬 cap 优先于 meta 层 9% 目标 floor，不对齐会导致 33号 收敛异常（34号 §3.2.2 危机态覆盖说明） |
| 稀有态 rarity_discount 冻结未激活 | 当前 4 态全 >5% 常见态（11号 §0.5.2），机制不触发；保留设计为加态向前兼容（34号 §3.2.5） |
| floor 5% / cap 40% | 防饿死 + 防集中（30_multi_strategy_concurrency §2.2 硬约束；BestFolio 2026-04 cap 40% 外部印证） |
| 再平衡 ≤1次/日 + 紧急例外（契约预留） | 防过度交易；regime 突变/Kill Switch 允许紧急再平衡；字段已落地，逻辑待 StrategyRebalanced 事件管线 |
| RiskSignal 由 regime 检测器侧计算 | 13 参数是市场风险指标，属于 regime 检测范畴；本模块是消费者，职责单一 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PA-007`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PA-007` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-PA-007` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PA-007 | MOD-PA-007 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/pf_alloc/core/regime_meta_allocator.py` | ✅ 已实现 | |

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


