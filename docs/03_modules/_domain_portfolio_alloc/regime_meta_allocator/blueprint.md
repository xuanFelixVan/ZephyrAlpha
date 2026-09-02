---
module_id: MOD-PA-007
title: "Regime元分配器蓝图 — Shrinkage风险节流+PerformanceScore后验分配（A模型·meta层）"
doc_type: blueprint
status: Active
version: "0.1.6"
design_maturity: production
build_status: production
ttl: permanent
layer: L02_pf_alloc
layer_name: pf_alloc
functional_domain: pf_alloc
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-06"
last_updated: "2026-08-06"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-PA-007 RegimeMetaAllocator — Regime元分配器 蓝图

> **module_id**: MOD-PA-007 | **域**: D_PF_ALLOC | **层**: L02 组合分配
> **优先级**: P0 | **成熟度**: design | **建设标记**: 🟡 待施工（第二阶段上，30_multi_strategy_concurrency §4.2）
> **SSoT**: depgraph MOD-PA-007 | **设计真源**: [30_multi_strategy_concurrency.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.2（RegimeMetaAllocator + 分配公式 + 置信度映射 + 稀有态处理）
> **Shrinkage 真源**: [10_regime_detector_spec.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md) §5（Shrinkage = ConfidenceSignal × RiskSignal，二维公式 + 13 参数阈值 + 聚合公式）
> **开源实证**: [Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book) — regime 做 risk-throttle Sharpe +1.43 / MaxDD −10.3%，regime 做 alpha-timing Sharpe +0.87（降）

## 1. 定位

Regime 元分配器——A 模型（[30_multi_strategy_concurrency](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.2）的 meta 层。消费 regime 检测器的 12 维灰度概率分布 + 各策略 PerformanceScore，通过 **Shrinkage 风险节流**（只减不增）+ **PerformanceScore 后验分配**，产出各 StrategyBook 的资金预算占比。

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
| regime 源 | regime 检测器 (MOD-REGIME-001) | 输出 12 维灰度概率 P(r1)..P(r12) |
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
| 核心 | RegimeProbabilities（12 维灰度概率，Σ=1） | CTR-SIG-012 | regime 检测器 (MOD-REGIME-001, D_REGIME) | 🟡 骨架 |
| 核心 | PerformanceScore[]（各策略 60 日滚动 Sharpe，[0.5,1.5]） | CTR-PA-007-P | StrategyBook 反馈 / 净值计算 | ❌ 待建 |
| 核心 | RiskSignalInputs（13 参数市场风险输入） | CTR-SIG-013 | 10_regime_detector_spec §5.3 数据源 | ❌ 待建 |
| 配置 | Base[]（先验权重，等权 1/N 或人工先验） | config | 配置文件 | ✅ config |
| 配置 | StrategySampleDays[]（各策略样本天数，<30 额外收缩） | CTR-PA-007-S | StrategyBook 注册 | ❌ 待建 |
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
| global_shrinkage | float | 全局风险节流因子（0.21~1.0），控制总暴露 |
| effective_budgets | dict[str, float] | {strategy_id: allocation_i × global_shrinkage}，StrategyBook 实收 |
| shrinkage_detail | ShrinkageDetail | Shrinkage 计算明细（归因用） |
| rebalance_allowed | bool | 当日是否允许再平衡（频率控制 ≤1次/日） |
| created_at | datetime | 创建时间 |
| idempotency_key | str | `f"alloc:{trade_date}:{hash(allocations)[:8]}"` |
| schema_version | str | "1.0" |

**ShrinkageDetail 子结构**（归因用）：

| 字段 | 类型 | 说明 |
|------|------|------|
| confidence_signal | float | ConfidenceSignal 值 |
| confidence_breakdown | dict | {max_p, base_confidence, rarity_discount, dominant_regime} |
| risk_signal | float | RiskSignal 值 |
| risk_breakdown | dict | {risk_base, anomaly_count, resonance_penalty, opportunity_recovery} |
| sample_shrinkage | dict[str, float] | {strategy_id: SampleShrinkage_i} |

## 3. 核心规则

### 3.1 分配公式（30_multi_strategy_concurrency §2.2）

```
allocation_i = normalize( Base_i × PerformanceScore_i × SampleShrinkage_i )
effective_budget_i = allocation_i × global_shrinkage

其中:
  global_shrinkage = ConfidenceSignal × RiskSignal          # 全局风险节流（regime 驱动）
  SampleShrinkage_i = f(StrategySampleDays_i)                # 策略级样本量收缩
```

> **关键设计**：`global_shrinkage` 是全局的（所有策略共享），在 `normalize` **外部**控制总暴露；`SampleShrinkage_i` 是策略级的，在 `normalize` **内部**影响相对分配。这精确实现了 30_multi_strategy_concurrency §2.2 的裁定——"regime 只回答多谨慎（global_shrinkage），不回答偏向谁（normalize 内由 PerformanceScore 决定）"。

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

**稀有态额外折扣**（30_multi_strategy_concurrency §2.2 稀有态处理）：

| 态频率 | rarity_discount | 说明 |
|--------|:---------------:|------|
| 常见态 > 5% | 1.0 | 置信度天然高 |
| 中等态 1-5% | 0.85 | 中度收缩 |
| 稀有态 < 1% | 0.7 | 稀有态检测置信度天然低，重收缩 |

```
ConfidenceSignal = base_confidence(max(P)) × rarity_discount(dominant_regime_frequency)
# 最低可能: 0.3 × 0.7 = 0.21（稀有态 + 低置信度）
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
| 危机（max(P)<60% + RiskSignal=0.3） | 0.3 × 0.3 = **0.09** | 9% |
| 稀有态 + 低置信 + 极端风险 | 0.21 × 0.3 = **0.063** | 6.3% |

### 3.3 PerformanceScore（后验分配，30_multi_strategy_concurrency §2.2）

> **策略亲和性由后验 PnL 自然捕获**——无需 regime 前瞻下注。

| 步骤 | 逻辑 |
|------|------|
| 1. 计算 | 60 日滚动 Sharpe Ratio（风险调整收益） |
| 2. 映射 | `PerformanceScore = clamp(Sharpe × scale + offset, 0.5, 1.5)` |
| 3. 防极端 | clip 到 [0.5, 1.5]（差策略不会被清零，好策略不会被独占） |
| 4. 冷启动 | 灰度发布期 / 样本<30 天 → PerformanceScore=1.0（不参与后验分配，只用 Base） |

**映射示例**（初始值，待回测校准）：

| 60日 Sharpe | PerformanceScore | 语义 |
|-------------|:----------------:|------|
| < 0 | 0.5 | 差策略，budget 减半 |
| 0 ~ 1.0 | 0.5 ~ 1.0 | 正常 |
| 1.0 ~ 2.0 | 1.0 ~ 1.5 | 好策略，budget 加成 |
| > 2.0 | 1.5 | 优秀，但封顶防独占 |

> **为何不直接用 Sharpe 而要映射**：原始 Sharpe 可能负值或极端，直接乘会破坏归一化。映射到 [0.5,1.5] 保证差策略不被清零（floor 0.5）、好策略不独占（cap 1.5）。

### 3.4 SampleShrinkage（样本量收缩，30_multi_strategy_concurrency §2.2）

| 样本天数 | SampleShrinkage | 说明 |
|---------|:---------------:|------|
| ≥ 30 天 | 1.0 | 正常 |
| 1-30 天 | 线性插值 0.5→1.0 | 新策略样本不足，额外收缩 |
| 0 天（冷启动） | 0.5 | 强制收缩，配合灰度发布 |

```
SampleShrinkage_i = clamp(0.5 + 0.5 × min(sample_days_i / 30, 1), 0.5, 1.0)
```

### 3.5 归一化 + floor/cap 硬约束（30_multi_strategy_concurrency §2.2）

```
raw_i = Base_i × PerformanceScore_i × SampleShrinkage_i
allocation_i = raw_i / Σ(raw)                              # 归一化，Σ=1.0
allocation_i = clamp(allocation_i, floor=5%, cap=40%)       # 硬约束
# clamp 后可能 Σ≠1.0，需二次归一化
allocation_i = allocation_i / Σ(clamped_allocation)         # 二次归一化
```

| 约束 | 值 | 目的 |
|------|:--:|------|
| floor | ≥ 5% | 防饿死（新策略至少有最小 budget 验证） |
| cap | ≤ 40% | 防集中（单策略不超过 40%，即使 PerformanceScore 极高） |

### 3.6 再平衡频率控制

| 规则 | 说明 |
|------|------|
| ≤ 1 次/交易日 | 防过度交易（30_multi_strategy_concurrency 引用 MOD-PA-003 §3.4） |
| 当日已再平衡 → rebalance_allowed=False | 沿用上次 BudgetAllocation |
| 触发例外 | regime 突变（max(P) 跨越置信度档位）+ Kill Switch 事件 → 允许紧急再平衡 |

## 4. 关键不变量 (INVARIANTS)

- `Σ allocation_i = 1.0`（归一化，二次归一化后严格成立）
- `allocation_i ∈ [5%, 40%]`（floor/cap 硬约束）
- `global_shrinkage ∈ [0.063, 1.0]`（ConfidenceSignal × RiskSignal，最低稀有态+极端风险）
- `Σ effective_budget_i = global_shrinkage`（总暴露 = 全局收缩因子）
- `effective_budget_i = allocation_i × global_shrinkage`（StrategyBook 实收）
- Shrinkage **只减不增**（≤1.0，风险节流非加杠杆）
- 再平衡频率 ≤ 1 次/交易日（紧急例外除外）
- 冷启动策略 PerformanceScore=1.0（不参与后验分配）
- BudgetAllocation 幂等（idempotency_key 防重复分配）

## 5. 错误契约

- `InvalidRegimeInputError` (ZA-PA-0007): 灰度概率 Σ≠1、含负值/NaN、维度≠12
- `InvalidPerformanceScoreError` (ZA-PA-0008): PerformanceScore 越界 [0.5,1.5]、策略 ID 不匹配
- `AllocationNormalizationError` (ZA-PA-0009): 归一化失败（raw 全零 / 二次归一化不收敛）
- `ShrinkageCalculationError` (ZA-PA-0010): ConfidenceSignal/RiskSignal 计算异常

## 6. 测试规划

### Phase 1 测试 (~20)
- Shrinkage：ConfidenceSignal 四档映射 / 稀有态折扣 / RiskSignal 消费（mock 输入）/ 上下界
- PerformanceScore：Sharpe→[0.5,1.5] 映射 / clip 边界 / 冷启动=1.0
- SampleShrinkage：30天边界 / 线性插值 / 0天=0.5
- 分配公式：normalize / floor 5% / cap 40% / 二次归一化
- 再平衡频率：当日已再平衡阻断 / regime 突变紧急例外
- BudgetAllocation 输出：effective_budget = allocation × shrinkage / 幂等性

### Phase 2 测试 (~15)
- 接入 regime 检测器真实灰度概率 / 13 参数 RiskSignal
- PerformanceScore 反馈联调（StrategyRebalanced 事件 → Sharpe 更新 → allocation 调整）
- 归因联调（ShrinkageDetail 完整链）
- 7 月案例验证（10_regime_detector_spec §5.3.4 五个时间点 Shrinkage 值吻合）

## 7. 依赖

### 7.1 已就绪 (Phase 1 可用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- Base 权重配置（config 驱动）

### 7.2 待建 (前置)
- regime 检测器 (MOD-REGIME-001, D_REGIME 域, RegimeProbabilities + RiskSignal) — 🟡 骨架已建（本模块核心上游）
- StrategyBook (MOD-POS-020, PerformanceScore + StrategySampleDays 反馈) — ❌ 待建（blueprint 已完成）
- BudgetChangeHandler (MOD-POS-022, BudgetChanged 事件消费) — ❌ 待建

### 7.3 消费者
- StrategyBook (MOD-POS-020)：消费 effective_budget_i
- BudgetChangeHandler (MOD-POS-022)：消费 BudgetChanged 事件（触发三级升级）
- Trader + 归因系统：消费 ShrinkageDetail（Shrinkage 归因）

### 7.4 与 MOD-PA-003 的关系（待协调）

| MOD-PA-003 功能 | A 模型下的归属 | 状态 |
|----------------|---------------|------|
| 容量约束 | MOD-PA-007 cap 40% 部分覆盖 + FirmRiskAggregator 组合级裁剪 | 部分替代 |
| MaxDD 减仓 | StrategyBook Drawdown Protocol（单策略级，§2.5）+ MOD-PA-007 Shrinkage（组合级） | 已被覆盖 |
| 冷启动缩放 | StrategyBook 灰度发布（5%→100%）+ MOD-PA-007 SampleShrinkage | 已被覆盖 |
| 再平衡频率 | MOD-PA-007 §3.6（≤1次/日） | 已被覆盖 |

> **初步判断**：MOD-PA-003 大部分功能被 A 模型其他模块覆盖，可能降级/重构。但 MOD-PA-003 有活跃生产依赖，具体处置待 MOD-PA-003 blueprint 范围内决定（参考 30_multi_strategy_concurrency §7.3 MOD-PF-002 暂缓弃用先例）。

### 7.5 降级策略

| 上游缺失 | 降级模式 | 影响 |
|---------|---------|------|
| regime 检测器 | ConfidenceSignal=0.3（强收缩默认）+ RiskSignal=1.0（无风险信号） | Phase 1 默认，保守部署 |
| PerformanceScore | 全部=1.0（等权，纯 Base 分配） | 跳过后验分配 |
| RiskSignal 13 参数 | RiskSignal=1.0（无市场风险信号） | Shrinkage 仅由 ConfidenceSignal 驱动 |

## 8. 分阶段施工里程碑

### Phase 1: Shrinkage 框架 + 等权分配（P0，regime 降级模式）

**目标**：Shrinkage 计算框架 + 等权 Base 分配 + floor/cap，regime 用降级默认

**范围**：
- ConfidenceSignal 计算（base_confidence 四档 + rarity_discount，regime 输入用 mock/降级）
- RiskSignal 消费接口（Phase 1 mock=1.0，Phase 2 接入真实 13 参数）
- global_shrinkage = ConfidenceSignal × RiskSignal
- PerformanceScore 映射框架（Phase 1 全=1.0 等权）
- SampleShrinkage 计算
- 分配公式 normalize + floor/cap + 二次归一化
- 再平衡频率控制（≤1次/日 + 紧急例外）
- BudgetAllocation 输出（CTR-PA-007）
- 降级模式（regime 缺失时 ConfidenceSignal=0.3）

**不包含**：真实 regime 灰度概率、13 参数 RiskSignal、PerformanceScore 反馈联调

**预计**：~400 行代码 + ~20 测试

### Phase 2: 接入 regime 链 + PerformanceScore 反馈（依赖 regime 检测器）

**前置**：regime 检测器 + StrategyBook 就绪

**范围**：
- 接入 regime 检测器 12 维灰度概率（真实 ConfidenceSignal）
- 接入 13 参数 RiskSignal（真实 RiskSignal 聚合）
- PerformanceScore 真实计算（60 日滚动 Sharpe，StrategyRebalanced 事件反馈）
- 7 月案例验证（10_regime_detector_spec §5.3.4 五时间点）
- 归因联调（ShrinkageDetail 完整链）

### Phase 3: 生产化（待 Phase 1/2 验证后）

- 与 StrategyBook + BudgetChangeHandler 联调
- 性能 SLA 验证（分配计算延迟 <30ms P50，N≤5 策略）
- depgraph build_status → generated, design_maturity → production

## 9. 设计决策记录

| 决策 | 理由 |
|------|------|
| 移除 RegimeScore（regime 不做 alpha 择时） | 30_multi_strategy_concurrency §2.2 裁定 + Morwane 开源实证：择时降 Sharpe 1.43→0.87，节流降 MaxDD；误差不对称（择时判错=亏损，节流判错=机会成本） |
| global_shrinkage 在 normalize 外部（控制总暴露） | 精确实现"regime 回答多谨慎"：全局因子不改变相对分配，只控制总暴露 |
| SampleShrinkage 在 normalize 内部（影响相对分配） | 新策略样本不足时相对分配更保守，与 PerformanceScore 同层 |
| PerformanceScore 映射 [0.5,1.5] | 差策略不被清零（floor 0.5 验证机会）、好策略不独占（cap 1.5 防集中） |
| PerformanceScore 后验捕获策略亲和性 | momentum 趋势态表现好→Sharpe 上升→有机获更多 budget，无需 regime 前瞻下注（避免估计误差放大） |
| 稀有态 rarity_discount | 稀有态检测置信度天然低，额外收缩（30_multi_strategy_concurrency §2.2） |
| floor 5% / cap 40% | 防饿死 + 防集中（30_multi_strategy_concurrency §2.2 硬约束） |
| 再平衡 ≤1次/日 + 紧急例外 | 防过度交易；regime 突变/Kill Switch 允许紧急再平衡 |
| RiskSignal 由 regime 检测器侧计算 | 13 参数是市场风险指标，属于 regime 检测范畴；本模块是消费者，职责单一 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PA-007`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PA-007` 的 5 个 file 节点 | production | `extract_depgraph.py --modules MOD-PA-007` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PA-007 | MOD-PA-007 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 5 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/pf_alloc/test_correlation_persistence.py` | ✅ 已实现 | |
| `tests/pf_alloc/test_multi_strategy_capital_allocator.py` | ✅ 已实现 | |
| `tests/pf_alloc/test_regime_meta_allocator.py` | ✅ 已实现 | |
| `tests/pf_alloc/test_strategy_correlation_gate.py` | ✅ 已实现 | |

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


