---
ttl: permanent
doc_type: architecture_view
title: RegimeMetaAllocator 参数
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.7.0"
date: 2026-08-10
topic: regime_meta_allocator
scope: 07_trading_decision_architecture
---

# RegimeMetaAllocator 参数

> 本备忘记录 regime 元分配器的选型推理、参数框架与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> **⚠️ 参数状态**：框架（why + 公式 + 三因子语义）已定 active；具体参数值（Base 权重 / PerformanceScore 映射系数 / 四档阈值 / floor·cap）**待首批策略 3-6 个月实盘 PnL 后校准**（见 §6 待裁定）。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G15 RegimeMetaAllocator 参数 |
| 所属 | 作战地图 08 + [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2 |
| 依赖 | ✅ [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) C1 验证已通过（commit 852457e9，四项全通过）；⚠️ G04 PerformanceScore 需首批策略 PnL（未就绪） |
| 对标 | Morwane risk-throttle / RegimeScore 移除裁定（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2） |
| 正交性 | ⚠️ 本身是 regime 节流的消费者；C1 已通过，参数待策略 track record 后校准 |
| 优先级 | P3（第二阶段，等策略 track record） |
| 状态 | 框架已定·active（C1 已通过，框架 why 成立；参数待首批策略 PnL 后校准） |

## 2. 背景

### 2.1 项目处境

- A 模型（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.1）已裁定：3-5 个 StrategyBook 独立账本 + firm 层求和裁剪 + **可选 RegimeMetaAllocator 动态 budget**
- regime 检测器（[10_regime_detector_spec](10_regime_detector_spec.md)）已实现并验证：4 态 HMM + D-SIGNAL-68 overlay + Shrinkage 二维公式
- **C1 验证已通过**（[11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §0.5.4，2026-08-08）：Shrinkage 节流有效（MaxDD 改善 +7.36pp，Calmar +27%），核心假设成立

### 2.2 核心问题

regime 信号如何用于多策略资金分配？两种用法有根本差异：

| 用法 | 性质 | 误差后果 | 实证 |
|---|---|---|---|
| **alpha 择时**（regime 重定向资金到"表现好的策略"） | 进攻性 | 判错 = 主动亏损 | Morwane：Sharpe 1.43→0.87（**降**） |
| **风险节流**（regime 只收缩总暴露，不重定向） | 防御性 | 判错 = 机会成本（少赚） | Morwane：Sharpe 1.43→1.43（不变），MaxDD −14.2%→−10.3%（**改善**） |

**已裁定（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2，2026-08-05）**：移除 RegimeScore，regime 仅通过 Shrinkage 做风险节流。regime 只回答"现在该多谨慎"，不回答"现在该偏向哪个策略"——后者由 PerformanceScore 后验 PnL 自然捕获。

### 2.3 约束条件

- **A 股不能做空** → 对冲式优化失效
- **策略 PnL 未就绪** → PerformanceScore 无法计算，当前只能用 Base 先验（等权 1/N）
- **C1 已通过但参数阈值待校准** → 四档阈值（60/80/95%）的 D1 ±20% 敏感性网格未跑（[11号](11_regime_backtest_validation_plan.md) §0.5.7）
- **实际 4 态非 12 态**（[11号](11_regime_backtest_validation_plan.md) §0.5.2）：r1 低波 27.6% / r2 中波 37.4% / r3 牛市 14.9% / r4 熊市 20.2%——**无 <1% 稀有态**，稀有态机制在 4 态下基本不触发

## 3. 决策：三因子乘法分配（Base × PerformanceScore × Shrinkage）

### 3.1 分配公式

```
allocation_i = normalize( Base_i × PerformanceScore_i × Shrinkage_i )

  硬约束：floor ≥ 5%（防饿死），cap ≤ 40%（防集中），Σ allocation_i = 1.0
```

> 代码映射：[regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) MOD-PA-007（**v1.0.0 production**，MATURITY=production），`FLOOR=0.05` / `CAP=0.40`，`allocate()` / `_compute_shrinkage()` / `_compute_confidence_signal()` / `_compute_risk_signal()` / `_compute_raw_allocation()` / `_normalize_and_clip()` / `compute_performance_score()`（静态方法，供上游计算 Sortino→[0.5,1.5]）。55 测试用例全绿。

**两个层次**（[BudgetAllocation](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) dataclass）：

| 层次 | 字段 | 回答的问题 | 范围 |
|---|---|---|---|
| 相对占比 | `allocations`（Σ=1.0） | "偏向哪个策略" | floor 5% ~ cap 40% |
| 总暴露因子 | `global_shrinkage` | "现在该多谨慎" | 0.21 ~ 1.0 |
| 实收预算 | `effective_budgets = allocation_i × global_shrinkage` | 策略实际可用 budget | — |

> **关键区分**：allocation_i（相对占比）由 Base×PerformanceScore 主导（回答"偏向谁"）；global_shrinkage（总暴露）由 regime 主导（回答"多谨慎"）。两者解耦——regime 不重定向资金，只缩放总暴露。
>
> **实现注记**：代码当前 Shrinkage 是**全局**的（一个 regime 状态→一个 global_shrinkage，所有策略共用），非每策略差异化。数学上 `normalize(Base_i × PerformanceScore_i × global_shrinkage) = normalize(Base_i × PerformanceScore_i)`——全局 Shrinkage 在归一化时约掉，**allocation_i 实际由 Base×PerformanceScore 决定，Shrinkage 只通过 `effective_budget = allocation_i × global_shrinkage` 缩放总暴露**。公式保留 Shrinkage_i 下标是为未来每策略差异化 Shrinkage 预留（如不同策略对 regime 敏感度不同），当前实现 = 全局。

### 3.2 讨论要点逐项对齐

#### ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` → §3.1

**决策**：三因子乘法 + 归一化 + floor/cap 裁剪。已定型于 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2。

- 为什么乘法而非加法/优化器：乘法是"加法替代优化器"哲学（[30号](30_multi_strategy_concurrency.md) §2.3）的 meta 层延伸——O(N) 复杂度，无协方差估计，归因清晰
- 为什么三因子：Base（先验）× PerformanceScore（后验）× Shrinkage（节流）——分别回答"初始怎么分""跑出来后怎么调""现在多谨慎"

#### ② Base_i 先验权重 → §3.2.1

**决策**：Base_i 是先验权重，新策略冷启动只用这个（无 PnL 时 PerformanceScore=1.0 中性）。

| 场景 | Base_i 取值 | 理由 |
|---|---|---|
| 冷启动（无任何 PnL） | 等权 1/N | 无信息先验，不偏袒 |
| 人工有先验信念 | 人工设定（如打板 0.3/多因子 0.4/事件 0.3） | 策略容量差异（打板容量小，不应等权） |
| 第二阶段（有 PnL） | 仍用先验，PerformanceScore 做后验调整 | Base 是锚，PerformanceScore 是调整，防 PnL 噪声导致权重剧烈跳动 |

- **待校准**：首批策略确定后，按策略容量差异设定人工先验（[30号](30_multi_strategy_concurrency.md) §6.1 首批 3 策略待确认）

#### ③ PerformanceScore 60 日 Sortino 映射 [0.5,1.5] → §3.2.2

**决策**：PerformanceScore_i = 60 日滚动 **Sortino**（非 Sharpe）线性映射到 [0.5, 1.5]，防极端。

| 60 日 Sortino | PerformanceScore | 含义 |
|---|---|---|
| ≤ 0 | 0.5 | 最差，权重砍半（但不饿死，floor 5% 兜底） |
| 1.0（中性） | 1.0 | 中性，不调整 |
| ≥ 2.0 | 1.5 | 最好，权重 ×1.5（但不集中，cap 40% 兜底） |

> **公式**：`Sortino = (R_p − R_target) / σ_d`
> - `R_p` = 60 日策略日均收益率 × 252（年化）
> - `R_target` = 无风险利率 Rf（见下），同 Sharpe 分子
> - `σ_d` = **下行偏差**（downside deviation）：只对 `R_daily < R_target` 的日子算偏差，上行波动不计入

##### Sharpe → Sortino 的选型理由（2026-08 三次审查更新）

| 维度 | Sharpe | Sortino | 对我们的影响 |
|---|---|---|---|
| 风险定义 | 总标准差（上下行都算"风险"） | 仅下行偏差（只惩罚亏损） | 我们 PerformanceScore 的目的是"识别亏损策略"做风险节流，不是"识别波动策略"——Sortino 的 downside-focus 与目的对齐 |
| 对 upside volatility | **惩罚**（涨停板 = "风险"） | **不惩罚**（涨停板 = 好事） | A 股打板策略有大量涨停板 upside 波动，Sharpe 会**低估**打板策略的 PerformanceScore → budget 分配偏差；事件驱动策略二元结果（兑现大涨/不兑现小亏）同理 |
| 2026 行业共识 | 通用标准，适合对称分布 | **非对称/偏态分布首选**（advisingalpha/equiscale/portfoliogenius/moneylume/fastercapital 2026 一致） | A 股策略收益分布普遍右偏（涨停板截断上行、跌停板+止损截断下行）→ 非对称 → Sortino 更合适 |
| Sortino ≥ Sharpe | 恒成立 | — | Sortino >> Sharpe 的 gap = "friendly asymmetry"（上行波动为主），是好策略的标志而非噪声 |

**结论**：切换到 Sortino 作为 PerformanceScore 的 primary 指标。Sharpe 保留为**对照指标**（监控 Sortino/Sharpe gap，gap 大 = 策略上行偏态强 = 友好；gap 小 = 对称波动 = 中性）。

> **施工注记**：[regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) 当前 `_compute_performance_score()` 用 Sharpe（`_sharpe()`）。切换到 Sortino 需新增 `_downside_deviation()` 函数 + 改 `_compute_performance_score()` 调用 + 新增 **downside 样本量门槛检查**（downside 观测数 <15 时返回 1.0 中性，防 inflated values，见 §3.2.2 样本量要求）。属施工层改动，不影响本备忘的 why 决策（映射区间 [0.5,1.5] / 60 日窗口 / floor-cap 兜底均不变）。

##### 无风险利率 Rf 定义

| 参数 | 取值 | 来源 | 更新频率 |
|---|---|---|---|
| Rf（年化） | ~2.0%（2026 货币基金均值） | 货币基金 7 日年化收益率（如余额宝/天弘） | 月频（波动小，月频取均值足够） |
| Rf（日频） | Rf_年化 / 252 | — | 每日由年化换算 |
| R_target（Sortino 分子用） | = Rf | 同 Sharpe 分子，保持两指标可比 | — |

- **为什么用货币基金而非国债**：A 股个人账户的"无风险替代"是货币基金（T+0 可取、零信用风险），1 年期国债需锁仓不符 T+1 流动性需求。货币基金年化 ~2% 与 1 年期国债 ~1.8% 量级一致
- **简化路径**：若数据管线未接货币基金收益率，可暂用固定 Rf=2.0%（2026 均值），首批策略 PnL 校准时再接实时数据。Rf 的误差对 Sortino 排序影响极小（所有策略用同一 Rf，只平移不分流）

##### MAR 选型理由（0% / Rf / target 三选一，2026-08 八次审查补充）

> **问题背景**：Sortino 公式 `Sortino = (R_p − MAR) / σ_d` 中的 **MAR（Minimum Acceptable Return，最小可接受收益）** 有三种主流取值——0% / 无风险利率 Rf / 自定义目标收益率 target。MAR 选择**实质影响 Sortino 结果**（fortraders 2026-04 引 IBKR Quant："The choice of the MAR can significantly influence the Sortino Ratio"），须明确选型理由。

| MAR 取值 | 适用场景 | 对我们的影响 | 2026 实证来源 |
|---|---|---|---|
| **0%** | 资本保全 / 最小化回撤（fortraders 表"Best For: Preserving capital and minimizing drawdowns"） | **过于宽松**——任何正收益日（R_daily>0）都不计入下行偏差，σ_d 偏小 → Sortino 偏高 → PerformanceScore 系统性高估。A 股策略连涨期 downside 样本本就少（§3.2.2 已警告 inflated values 风险），0% MAR 会放大此风险 | fortraders 2026-04-30 表 / wallible 2026-03"MAR souvent 0%" |
| **Rf（~2%，我们的选择）** | 跑赢无风险被动投资（fortraders 表"Best For: Outperforming passive, low-risk investments"）；**机构默认** | **正合适**——MAR=Rf 意味着"策略必须跑赢货币基金才算合格"，下行偏差只统计"跑输无风险利率"的日子。这是 Sortino 原始论文（Frank Sortino 1980s）的意图：MAR 是"策略的被要求收益率"，对个人量化系统而言"被要求"= 至少跑赢 cash | icalculators 2026-06"MAR often set to Rf (4.2–4.6%) or policy hurdle (5–7%) for pensions" / portfolioslab 2026-03"MAR can be set to the risk-free rate, zero, or a personal target return" / schwab 2024"Frank Sortino's original formula used a MAR—a required rate of return—in place of the risk-free rate" |
| **target（如 9% 利润目标）** | 跟踪特定业绩目标（fortraders 表"Best For: Achieving profit requirements"） | **不适用**——个人量化系统无外部利润目标（不像 prop firm 挑战赛要求 9% 才分成）。设 target 会人为抬高 MAR → 更多日子被判为"下行" → σ_d 偏大 → Sortino 偏低 → PerformanceScore 系统性低估。且 target 选值无客观依据（5%? 10%? 15%?），引入主观偏差 | fortraders 2026-04-30 表（For Traders 挑战赛 9% 目标场景） |

**决策：MAR = Rf（~2%）**。理由汇总：

1. **Sortino 原始意图**：MAR 是"策略的被要求收益率"（Schwab 2024 引 Frank Sortino 原始论文），对个人量化系统 = 至少跑赢 cash 替代（货币基金）。Rf 是 MAR 的"被要求"语义最忠实体现
2. **与 Sharpe 分子一致**：MAR=Rf → Sortino 与 Sharpe 分子相同（都是 R_p − Rf），两指标**纯差异在分母**（总 σ vs 下行 σ_d）→ Sortino/Sharpe gap 干净反映"上行偏态强度"（§3.2.2 gap 监控的基础）。若 MAR≠Rf，gap 会混入"MAR 选择差异"噪声，gap 监控失效
3. **避免 0% 的 inflated values 放大**：§3.2.2 已警告 60 日 downside 样本 ~24 日的 inflated values 风险，0% MAR 会进一步压低 σ_d（更多日子不算下行）放大此风险；Rf MAR 把"跑输 cash"的日子也算下行，σ_d 更稳健
4. **避免 target 的主观偏差**：个人系统无人值守无外部目标，target 选值无客观依据；Rf 有市场数据（货币基金 7 日年化）客观可查
5. **机构默认**：icalculators 2026-06 明确"MAR often set to Rf for pensions"——Rf 是机构默认 MAR，与我们"对标机构实践"偏好一致

> **施工注记**：代码 `_compute_performance_score()` 实现 Sortino 时，`MAR = Rf`（同 §3.2.2 Rf 定义，货币基金 ~2% 年化 / 252 日频）。**禁止**用 0% 或硬编码 target 作为 MAR——前者放大 inflated values 风险，后者引入主观偏差。Rf 数据源同 §3.2.2 Rf 定义（货币基金 7 日年化月频取均值，或简化路径固定 2.0%）。

##### 熊市最低总暴露（global_shrinkage floor）

- **当前 floor**：`global_shrinkage ≥ ConfidenceSignal_min(0.3) × RiskSignal_min(0.30) = 0.09`（9%）——极端熊市（max(P)<60% + 13 参数全亮红灯）时，总暴露最低保留 9%
- **为什么 9% 而非 0**：A 股不能做空、个人账户无债券/黄金防御资产，**cash 就是防御资产**。极端熊市保留 9% 暴露用于捕捉反弹（熊市反弹往往暴力，如 2024-09 政策底单日 +8%），完全空仓 = 错过反弹 + 无法恢复 PerformanceScore。9% 是"最低侦察兵暴露"，91% cash 是防御
- **2026 资本保全研究的对照**：recessionistpro 2026-02 / brimindinvest 2026-06 / protraderdaily 2026-08 建议衰退期保留 20-35% 防御资产——但那是**多资产组合**（债券/黄金作为 defensive sleeve）。A 股单市场个人账户无此 sleeve，cash 比例 = 1 − global_shrinkage，所以低 global_shrinkage（高 cash）= 高防御，与多资产"高防御资产占比"等价。9% 暴露 ≈ 91% cash 防御，对应多资产组合的"极端防御"档位
- **不需要提高 floor**：A 股熊市特征是阴跌+急反弹，低暴露高 cash 是正确的防御姿态。若提高 floor（如 ≥30%）反而在熊市被迫持有过多暴露，与风险节流目的矛盾

##### ⚠️ 危机态（CRISIS）覆盖说明（2026-08-10 九次审查补充——解决 9% floor vs 5% crisis cap 冲突）

> **冲突描述**：本节 global_shrinkage floor = 9%（极端熊市最低保留 9% 暴露），而 [31号](31_position_sizing.md) §2.4.3 定义 CRISIS（⑩特殊态）总仓位上限 = 5%。9% > 5%，表面矛盾。

**决议：firm 层 5% crisis cap 优先于 meta 层 9% floor。两者不矛盾，因为适用于不同的 regime 态：**

| 层次 | 机制 | 适用 regime 态 | 数值 | 性质 |
|---|---|---|---|---|
| **meta 层（本备忘 34号）** | `global_shrinkage floor = 0.09` | **r4 熊市**（4 态 HMM 中最差的常规态，max(P)<60% + ConfidenceSignal=0.3） | 9% | **目标值下限**（meta 层输出的 effective_budget 目标 ≥9%，策略可自然低于目标） |
| **firm 层（[31号](31_position_sizing.md) §2.4.3）** | `MARKET_REGIME_CAPS[CRISIS] = 0.05` | **⑩ CRISIS 特殊态**（D-SIGNAL-68 overlay 触发的系统性危机，非 4 态 HMM 之一） | 5% | **硬上限**（firm 层 FirmRiskAggregator 强制裁剪，不可突破） |

**关键区分**：
1. **r4 熊市 ≠ ⑩ CRISIS**：r4 是 4 态 HMM 的常规熊市态（占样本 20.2%，[11号](11_regime_backtest_validation_plan.md) §0.5.2），阴跌为主但非系统性崩盘；⑩ CRISIS 是 D-SIGNAL-68 overlay 触发的**特殊危机态**（如 2015 股灾/2024-02 雪球敲入），频率远低于 r4。两者是不同的 regime 态，9% floor 管 r4，5% cap 管 ⑩
2. **floor 是目标下限非硬约束**：§3.1 已明确"effective_budget 是目标值非强制值"——9% floor 意味着 meta 层在 r4 熊市**输出目标 ≥9%**，但策略实际暴露可低于目标（未部署完/已止损）。floor 防"meta 层把目标压到 0 导致策略无 budget 可用"，不强制策略必须持有 9%
3. **cap 是硬上限**：5% crisis cap 是 firm 层 FirmRiskAggregator 的**强制裁剪**——当 ⑩ CRISIS 触发时，无论 meta 层 effective_budget 目标多少，firm 层总仓位 ≤5%。这是风险红线的最后防线
4. **当 r4 熊市 + ⑩ CRISIS 同时触发**：⑩ CRISIS overlay 优先级高于 r4 HMM 基态（[10号](10_regime_detector_spec.md) D-SIGNAL-68 overlay 设计），此时 firm 层 5% cap 为 binding constraint，meta 层 9% floor **自动悬空**（floor 只在非 CRISIS 态生效）。代码实现须在 `_compute_shrinkage()` 中检查 `is_crisis` flag，CRISIS 态下 `global_shrinkage` 不受 0.09 floor 约束（可降至 0.05 对齐 crisis cap），由 firm 层硬裁剪兜底

**施工注记**：[regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) `_compute_shrinkage()` 须新增 CRISIS 态分支——当 regime detector 输出 `is_crisis=True`（D-SIGNAL-68 overlay 触发）时，`global_shrinkage` floor 从 0.09 降至 0.05（对齐 [31号](31_position_sizing.md) crisis cap），且 `effective_budget` 目标值 ≤0.05。此改动不影响非 CRISIS 态的 9% floor 逻辑。若代码暂未实现此分支，firm 层 FirmRiskAggregator 的 5% 硬裁剪仍能保证安全（cap 优先于 floor），但 meta 层输出的目标值会虚高（9% vs 实际 5%），导致 [33号](33_budget_change_handler.md) 收敛行为异常（目标 9% → 实际被裁到 5%，触发不必要的收敛动作）。**须在首批策略上线前实现此分支**

##### 其他设计要点（保留）

- **为什么 60 日**：覆盖 ~3 个月，足以过滤单月噪声，又不至于太滞后（A 股情绪周期 2-3 个月）
- **为什么 [0.5, 1.5] 而非 [0, 2]**：防极端——差策略不至于被归零（floor 5% 防饿死），好策略不至于被无限放大（cap 40% 防集中）
- **后验捕获 regime 亲和性**：momentum 在趋势态表现好→滚动 Sortino 上升→有机获得更多 budget，无需 regime 前瞻下注（[30号](30_multi_strategy_concurrency.md) §2.2 裁定）
- **walk-forward 天然无前视**：60 日滚动窗口只用过去数据，天然 walk-forward，无前视偏差（与 [11号](11_regime_backtest_validation_plan.md) C1 验证的 walk-forward 协议一致）
- **冷启动过渡**：策略上线 0-60 日内，PerformanceScore 无法算完整 60 日 Sortino → 过渡期用已有天数算部分 Sortino（≥30 日起算，见下方样本量要求），不足 30 日则 PerformanceScore=1.0 中性（同 §3.2.1 冷启动逻辑）
- **⚠️ Sortino 样本量要求（2026-08 四次审查补充）**：Sortino 的下行偏差只统计 `R_daily < R_target` 的日子，A 股 60 交易日中下跌日约 40% ≈ 24 日。ecassets 2026-05 / foliolab 2026 明确警告：**"downside sample is small → statistically unreliable"** + **"inflated values for strategies with few downside observations"**——下行样本不足时 Sortino 会系统性偏高（少几个下跌日就使分母骤降→Sortino 飙升），高估策略表现。防护措施：
  1. **最小 downside 样本门槛**：downside 观测数 <15 时 PerformanceScore 强制 =1.0 中性（不参与 Sortino 映射）——A 股约需 38 交易日（15÷0.4）积累足够 downside 样本，冷启动过渡门槛据此从 20 日上调到 30 日（留余量）
  2. **PerformanceScore floor 兜底**：即便 Sortino 算出 ≥2.0（映射 1.5），也受 §3.2.4 cap 40% 约束——Sortino inflated values 不会导致单策略霸占 budget
  3. **Sortino/Sharpe gap 监控**：若某策略 Sortino >> Sharpe（gap 异常大），标记为"疑似 inflated"——可能是 downside 样本太少或连胜期未遇回撤，复核后决定是否降权
  4. **待校准**：首批策略 PnL 后，实测 downside 样本数与 PerformanceScore 稳定性，必要时上调窗口到 90 日（downside 样本 ~36 日，更稳）
- **⚠️ 60 日 vs Sortino 36 个月机构标准（2026-08 六次审查重大修正）**：这是两个不同来源的"36 个月"，须区分——
  - **来源 A：Sortino 自身的机构标准**。forex-basics 2026-05-28（evergreen verified）明确："The institutional standard is a minimum of thirty-six months" + "With only twelve months of data it is easy to land in a situation where the strategy enjoyed a lucky run without deeper drawdowns, and the downside deviation came out artificially low"；financefriend24 2026："With fewer than 36 monthly observations (3 years), the result is highly sensitive to individual bad months. With 60+ monthly observations (5 years), the estimate becomes more reliable"；superglobalcalculator 2026："Need ≥ 30 periods for stability"；getzenquery 2026："For more reliable results, consider using 20-30+ return periods"。**Sortino 机构标准 = 36 个月（~540 交易日）= 我们 60 日的 9 倍**——我们 60 日远低于机构标准，是已知妥协
  - **来源 B：BestFolio walk-forward 优化器窗口**。BestFolio 2026-04 用 36 个月（~780 交易日）lookback，但那是为 max Sharpe **优化器**（需长窗口稳协方差矩阵），与我们用 Sortino 做简单映射不同
  - **我们 60 日的特殊理由（A 股 + 个人系统）**：① A 股情绪周期 2-3 个月（短于美股市场周期），策略 alpha 衰减快，需快速响应；② 我们用 Sortino 做 [0.5,1.5] 线性映射 + floor/cap 裁剪，**不是优化器**，短窗口噪声被裁剪缓冲（映射后 0.5-1.5 的变动对 allocation 的影响被 floor 5%/cap 40% 限制）；③ 个人系统策略数少（3-5 个），不需要机构级的统计稳健性；④ 60 日 downside 样本 ~24 日，配合 §3.2.2 四件套防护（downside<15 强制中性 + cap 兜底 + gap 监控 + 待校准）可控制 inflated values 风险
  - **已知风险**：60 日窗口下 Sortino 估计误差大于机构标准，具体表现——策略连胜期（少下跌日）Sortino 偏高 → PerformanceScore 偏高 → allocation 偏大；策略连亏期相反。**floor/cap 是第一道防线**（极端值被裁剪），**gap 监控是第二道防线**（Sortino/Sharpe gap 异常触发复核）
  - **实盘校准触发条件**：首批策略 3-6 个月 PnL 后，若实测发现——① PerformanceScore 月度变动 >0.3（映射区间 [0.5,1.5] 的 30%）频繁出现；② 同一策略 Sortino 月度排名波动大（如本月第 1 下月第 3）；③ Sortino/Sharpe gap 监控频繁触发"疑似 inflated"——则上调窗口到 90 日（downside ~36 日，接近机构标准的月频等价）或 120 日（downside ~48 日），代价是响应变慢
  - **远期演进**：若 90/120 日仍不稳定，可考虑**月频 Sortino + 36 个月窗口**（完全对齐机构标准），但需策略实盘 3 年后才有足够数据——这是第二阶段之后的远期校准项，MVP 先用 60 日 + 防护四件套
- **⚠️ 加权方式决策（等权 vs EMA，2026-08 八次审查补充）**：PerformanceScore 的 60 日 Sortino 窗口有两种加权方式——
  | 加权方式 | 机制 | 优点 | 缺点 | 2026 实证 |
  |---|---|---|---|---|
  | **等权（MVP 选择）** | 60 日简单滚动平均，每日权重 1/60 | 简单 + walk-forward 天然无前视 + 所有日子等权无偏 | 对"近强远弱"alpha 衰减响应慢（60 日前的高 Sortino 与今日同等权重） | — |
  | **指数加权 EMA（远期候选）** | 半衰期 20-30 日，近期权重指数衰减更高 | 对 alpha 衰减响应快（近期 Sortino 权重高，旧 alpha 失效快速反映） | 需验证无前视（EMA 递归用历史 EMA，理论上 walk-forward 但实现易引入前视）+ 半衰期选值主观 | volity 2026-06 EMA 系统趋势市 55-60% 胜率（响应速度 ~2x SMA）+ ctrl-trade 2026-06 EMA-50 filter 20 年回测 Sharpe 0.93（最高，vs 100% SPY 0.58）|

  **决策：MVP 用等权，EMA 列远期候选**。理由：
  1. **walk-forward 无前视优先**：等权窗口只用过去 60 日数据，天然 walk-forward；EMA 递归公式 `EMA_t = α × R_t + (1−α) × EMA_{t-1}` 理论上无前视但实现时易引入（如初始化用全样本均值、α 选值用未来数据优化）
  2. **floor/cap 缓冲短窗口噪声**：§3.2.4 floor 5%/cap 40% 已裁剪 PerformanceScore 极端值，等权 60 日的噪声被裁剪缓冲，不需要 EMA 的"近期权重"来快速响应
  3. **EMA 升级触发条件**：首批策略 PnL 后，若实测发现——① 策略表现有"近强远弱"衰减特征（如 regime 切换后旧 alpha 失效，60 日前的高 Sortino 与当前表现不符）；② PerformanceScore 月度变动 >0.3 频繁但等权响应滞后——则升级到 EMA（半衰期 20-30 日）。半衰期选值用 walk-forward CV（cross-validation）优化，禁止用全样本优化（防前视）
  4. **EMA 不是"更好"而是"不同"**：volity 2026-06 实证 EMA 在趋势市 55-60% 胜率，但 SMA 在震荡市更稳（EMA 对噪声过敏）。A 股 regime 切换频繁（4 态 HMM），EMA 可能过度响应 regime 噪声——需首批 PnL 验证 alpha 衰减特征后再决定

- **⚠️ 多策略 PerformanceScore 同向变动说明（2026-08 八次审查补充）**：当 regime 切换（如 r3 牛市→r4 熊市）时，**所有策略的 Sortino 可能同时下降**（因为它们都经历同一熊市 regime）→ 所有 PerformanceScore 同时降低 → normalize(Base × PerformanceScore) 后 allocation 比例可能几乎不变（因为所有策略同比例下降）。**这是 feature 不是 bug**：
  1. **PerformanceScore 的设计意图就是"后验捕获 regime 亲和性"**（§3.2.2"后验捕获 regime 亲和性"）——momentum 在趋势态表现好→Sortino 上升→有机获得更多 budget。当所有策略同向变动时，说明 regime 影响是"市场级"而非"策略级"——此时 allocation 比例稳定是正确的（不该在市场级 regime 切换时还重定向资金，那是 RegimeScore alpha 择时已被 §2.2 裁定拒绝）
  2. **真正的"多谨慎"由 global_shrinkage 回答**：regime 切换时 global_shrinkage 降低（ConfidenceSignal 降档 + RiskSignal 升高）→ effective_budget = allocation × global_shrinkage 整体降低 → 所有策略 budget 同比例收缩。这正是 §3.1 "allocation 回答偏向谁 / global_shrinkage 回答多谨慎"解耦设计的体现——regime 切换影响 global_shrinkage（总暴露），不影响 allocation（相对占比）
  3. **floor/cap 防同向极端**：即便所有策略 PerformanceScore 同向变动，floor 5% 防饿死 + cap 40% 防集中仍生效——不会因同向变动导致某策略被归零或霸占
  4. **不同策略对 regime 敏感度不同**：打板策略在 r3 牛市 Sortino 高、r4 熊市 Sortino 低（趋势跟随）；多因子策略各 regime Sortino 差异小（市场中性）；事件驱动策略与 regime 弱相关（事件独立）。**实际同向变动不会完全同步**——打板 Sortino 波动远大于多因子，normalize 后打板在牛市 allocation 上升、熊市下降，这正是 PerformanceScore 的价值。完全同步只在"所有策略对 regime 同等敏感"时发生，实际不会

- **待校准**：映射区间 [0.5, 1.5] 和窗口 60 日待首批策略 PnL 后验证；可能需按策略类型差异化窗口（打板用 30 日，多因子用 90 日）；Sortino vs Sharpe 的实测 gap 待首批 PnL 后复核选型；**冷启动贝叶斯收缩（远期候选）**——当前冷启动 <30 日直接 PerformanceScore=1.0 中性，MRC（arXiv:2605.24490, 2026-05-23）用贝叶斯自适应混合 `score = w_prior × 1.0 + w_data × Sortino_score`，权重 `w_data ∝ 样本量` 随数据积累从 0→1 渐变（而非硬切换），比我们的阈值切换更平滑。MVP 不采纳——我们的 30 日阈值 + floor/cap 兜底已足够防极端，贝叶斯收缩增加先验分布假设的复杂度，待首批 PnL 证明冷启动期权重跳变成问题后再评估

#### ④ Shrinkage 置信度→风险节流映射（四档）→ §3.2.3

**决策**：Shrinkage 是二维公式（[10_regime_detector_spec](10_regime_detector_spec.md) §5.2.2），ConfidenceSignal 四档 × RiskSignal 13 参数连续值。

```
Shrinkage = ConfidenceSignal × RiskSignal

  ConfidenceSignal = f(max(P))           # HMM 置信度映射，四档 0.3-1.0
  RiskSignal = g(实时市场风险参数)          # 13 参数连续值 0.3-1.0，只减不增
```

**ConfidenceSignal 四档**（[10号](10_regime_detector_spec.md) §5.1）：

| max(P) | ConfidenceSignal | 风险节流行为 | 说明 |
|---|---|---|---|
| <60% | 0.3 | 强收缩，回退等权/指数 | 不确定时别赌方向 |
| 60-80% | 0.6 | 中度收缩，整体保守部署 | 有方向感但不确信 |
| 80-95% | 0.85 | 轻度收缩，正常部署 | 方向较确信 |
| >95% | 1.0 | 接近无收缩，满部署 | 高确信度 |

**RiskSignal**（[10号](10_regime_detector_spec.md) §5.3.3）：`clamp[0.30, RiskBase × 共振惩罚 + 机会恢复, 1.00]`，13 参数（realized_vol 分位/量价时空/跨市场相关性/虹吸态/技术背离/新闻情绪/筹码结构等），#1 门控（危机期 #1<1.0 才激活附加参数）。

- **C1 验证已通过**（[11号](11_regime_backtest_validation_plan.md) §0.5.4）：Shrinkage 开 vs 关，Sharpe 0.3678→0.3474（不显著伤害 ✅）/ MaxDD 0.2221→0.1485（改善 +0.0736 ✅）/ Calmar 0.2918→0.3694（+27% ✅）/ Turnover 2.27→2.55（≤2×✅）
- **shrinkage_enabled 开关**：代码已有，C1 验证一票否决机制——若 Shrinkage 无效则 `shrinkage_enabled=False`，`global_shrinkage=1.0` 回退等权
- **待校准**：四档阈值 60/80/95% 的 D1 ±20% 敏感性网格未跑（[11号](11_regime_backtest_validation_plan.md) §0.5.7），当前值是 [30号](30_multi_strategy_concurrency.md) §2.2 启发式设定
- **60% 阈值的外部印证**：1uptick 2026-06 机构方案明确"when no single regime probability exceeds **60%**—automatically reduce position sizes by 30-50%"——与我们 ConfidenceSignal max(P)<60%→强收缩的阈值**完全一致**，60% 是行业共识的"regime 不确定"临界点
- **我们 0.3 vs 1uptick 30-50% 更激进的理由**：1uptick 减的是"position sizes"（可日内调整），我们 0.3 减的是"global_shrinkage"（总暴露）。A 股 T+1 不能日内快速止损，不确定时需要更保守的预防性收缩——宁可少赚不可多亏。且 0.3 是 ConfidenceSignal 部分，实际 Shrinkage = 0.3 × RiskSignal，RiskSignal 在不确定时也 <1.0，叠加后更保守
- **Shrinkage 更新频率**：ConfidenceSignal 随 regime 检测日频更新（HMM 日频推理，[10号](10_regime_detector_spec.md)）；RiskSignal 13 参数中 realized_vol/量价等日频、新闻情绪盘内更新。global_shrinkage 日频重算，盘中 regime 突变（如 D-SIGNAL-68 overlay 触发）可盘中重算
- **Quarter Kelly 与 Shrinkage 节流的同构印证（2026-08 六次审查补充）**：pooyagolchian 2026-04《Portfolio Risk Management》实证 fractional Kelly 的风险预算折扣收益（2026 年真实数据）——

  | 策略 | 风险预算折扣 | CAGR | MaxDD | 与 Full Kelly 比 |
  |---|---|---|---|---|
  | Full Kelly | 1.0× | 18.2% | −62% | 基准 |
  | Half Kelly | 0.5× | 14.1% | −38% | 77% 增长 / 61% 回撤 |
  | **Quarter Kelly** | 0.25× | 10.8% | −22% | **59% 增长 / 35% 回撤** |
  | Risk Parity 基线 | — | 9.2% | −18% | 50% 增长 / 29% 回撤 |

  核心结论："Quarter Kelly delivers 85% of full Kelly's growth with only 35% of the drawdown"。这与我们的 Shrinkage 节流**同构**——Shrinkage 把总暴露从 1.0 缩到 0.21-1.0，本质就是 regime 驱动的 fractional 风险预算折扣。区别：Kelly fraction 基于胜率/赔率（收益端估计），Shrinkage 基于 regime 置信度+风险参数（风险端推断，不依赖收益预测，规避了 Kelly 对估计误差极敏感的缺陷，见 §4.5）。但两者共享同一规律：**适度收缩风险预算 → 以小得多的回撤代价获得大部分增长**——这是 §2.2 "regime 做风险节流而非 alpha 择时"裁定的实证支撑。我们的 9% 熊市 floor（§3.2.2）对应"不低于 Quarter Kelly 量级的最低风险敞口"

#### ⑤ floor≥5% / cap≤40% → §3.2.4

**决策**：归一化后硬约束，floor 5% 防饿死 + cap 40% 防集中。

| 约束 | 值 | 防什么 | 代码 |
|---|---|---|---|
| floor | ≥5% | 单策略被 PerformanceScore×Shrinkage 压到 0（饿死）→ 永远无法翻身 | `FLOOR=0.05` |
| cap | ≤40% | 单策略霸占 budget（集中）→ 多策略分散化失效 | `CAP=0.40` |

- 实现：归一化 → 低于 floor 抬到 floor / 高于 cap 压到 cap → 再归一化（[regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) `_normalize_and_clip`）。再归一化可能使个别策略再次越界，**迭代 2-3 次即可收敛**（floor/cap 是有界投影，非等比例缩放，数学上有限步收敛）
- **⚠️ floor/cap 无解兜底（2026-08 六次审查补充）**：floor+cap 约束在策略数 N 较小时可能**数学无解**——如 N=2 + floor=5% + cap=40%：两策略都 ≥5% 且 ≤40%，Σ=1.0 → 一个 ≥60% 必然违 cap。无解场景的兜底（参考 AIMS Mathematics 2026, 11(2):3647 Lkhagvasuren et al.《Convex and sphere packing approaches to portfolio optimization》的 feasibility restoration 思想——当约束无解时找"最近可行解"）：
  1. **检测无解**：迭代 5 次仍未收敛（仍有策略越界）→ 判定 floor/cap 在当前 N 下无解
  2. **优先保 floor 降 cap**：floor 是"防饿死"的生存线（不可降），cap 是"防集中"的优化线（可降）→ 自动放宽 cap 到 `1 − (N-1)×floor`（如 N=2 + floor=5% → cap 放宽到 95%）。这保证所有策略 ≥floor，代价是单策略可能超原 cap
  3. **日志告警**：无解兜底触发时 log WARNING + 上报 firm 层 [32号](32_firm_risk_aggregator.md)，标记"策略数过少导致分散化失效"，提示人工评估加策略或调 floor
  4. **N≥3 时基本不触发**：N=3 + floor=5% + cap=40% → 最小 Σ=15%、最大 Σ=120%，Σ=1.0 必有解（如 33%/33%/34%）；N=5 + floor=5% + cap=40% → 最小 Σ=25%、最大 Σ=200%，同样有解。**无解兜底主要为 N=2 边缘情况设计**，MVP 首批 3 策略不触发
- **cap 40% 的外部印证**：BestFolio 2026-04 walk-forward 明确用 "Max weight per strategy: **40%**. Forces real diversification. Stops the optimizer from collapsing onto whichever single strategy looked best"——与我们 CAP=0.40 **完全一致**，40% 是多策略分散化的行业共识上限。**GATE-WPCA-PI**（AIMS Mathematics 2026, 11(2):3647-3702）也用 "entropy floor" 防集中 + "sleeve caps" 限制单资产——与我们 floor 5%/cap 40% 同构，2026 年学术级印证
- **待校准**：5%/40% 是行业经验值（多策略基金单策略通常 5-30%），首批策略数确定后校准（3 策略时 cap 可放到 40%；5 策略时 cap 可降到 30%）

#### ⑥ 稀有态差异化收缩 → §3.2.5

**决策**：按态频率差异化收缩（[30号](30_multi_strategy_concurrency.md) §2.2）：常见态 >5% 轻收缩 / 中等态 1-5% 中度收缩 / 稀有态 <1% 重收缩——稀有态检测置信度天然低。

- **4 态下的实际情况**：r1=27.6% / r2=37.4% / r3=14.9% / r4=20.2%——**全部是常见态（>5%），无 <1% 稀有态**
- **结论**：稀有态机制在当前 4 态下基本不触发，是为原 12 态设计的向前兼容机制
- **保留理由**：若未来基于证据加态（如 [11号](11_regime_backtest_validation_plan.md) §0.6.9 层次 HMM 升级路径），稀有态机制自动生效，无需重写
- **不是过度工程**：该机制是 Shrinkage 计算内的一个条件分支（按态频率查表收缩系数），代码量极轻，保留无成本

##### 12 态→4 态退化映射（2026-08 六次审查补充）

> **问题背景**：Shrinkage 的 ConfidenceSignal 四档、稀有态差异化收缩最初按"12 态 regime"设计；但 [11号](11_regime_backtest_validation_plan.md) §0.5.2 C1 验证实测 HMM 按 BIC/AIC 信息准则选优后**稳定收敛到 4 态**（r1 低波/r2 中波/r3 牛市/r4 熊市），原 12 态的多数子态在样本期内未被区分。这产生了"设计的 12 态 vs 实际的 4 态"之间的退化映射问题——必须明确 4 态如何吸收原 12 态语义，否则 Shrinkage 的"按态收缩"会因态数不匹配而悬空。

**退化映射的 why（设计原则，非精确查表）**：

| 退化原则 | 说明 | 为什么 |
|---|---|---|
| **按波动族合并** | 原设计的高/中/低波动子态 → 合并到 r1（低波）/r2（中波） | 波动是 regime 检测的一阶特征，细分子态在日频上不可靠区分（A 股情绪周期 2-3 个月，子态持续时间 <1 个月易被噪声淹没） |
| **按趋势方向合并** | 原设计的上涨/下跌主趋势 → 合并到 r3（牛市）/r4（熊市） | 趋势方向是 regime 的二阶特征，4 态已覆盖"牛/熊/低波/中波"四象限，进一步细分（如"温和牛"/"急牛"）对 Shrinkage 收缩系数的差异化无统计意义 |
| **稀有态机制冻结** | 原 12 态中 <1% 的"危机闪崩态"等 → 当前 4 态无对应（全部 >5%），稀有态分支**不激活但不删除** | 冻结而非删除是为层次 HMM 加态（[11号](11_regime_backtest_validation_plan.md) §0.6.9）时自动复用；删除则未来加态需重写 Shrinkage 查表逻辑 |

**当前实现行为**：4 态全部走"常见态 >5% 轻收缩"分支，稀有态分支死代码（保留但不执行）。ConfidenceSignal 四档阈值（60/80/95%）作用于 max(P)（HMM 输出的最大状态概率），与态数无关——无论 4 态还是 12 态，max(P) 的语义都是"当前最可能态的确信度"，所以**退化不影响 ConfidenceSignal 计算**，只影响"按态频率差异化收缩"这一子分支。

> **施工注记**：12 态→4 态的**精确状态 ID 映射表**（如"原态 0,1,2 → r1；原态 3,4 → r2"）归 [10号](10_regime_detector_spec.md) regime 检测器文档定义（那里管 HMM 状态语义），本备忘只管"Shrinkage 如何消费 4 态输出"。退化映射的精确查表待 [10号] 校准（见 §6 待裁定）。MPC 多期预测路径下（见 §5.2 远期候选）若引入层次 HMM，退化映射需重新校准——届时 12 态可能不再全部退化到 4 态。

#### ⑦ 第二阶段上线时机 → §3.2.6

**决策**：[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §4.2 演进路径——**各策略有 3-6 个月实盘 PnL 后**上加 RegimeMetaAllocator。

| 门槛 | 状态 | 说明 |
|---|---|---|
| C1 验证（Shrinkage 有效性） | ✅ 已通过（commit 852457e9） | 核心假设成立，Shrinkage 节流有效 |
| 首批策略 PnL（PerformanceScore 输入） | ❌ 未就绪 | 策略未实盘，无 60 日 Sortino |
| 四档阈值 D1 敏感性校准 | ❌ 未跑 | [11号](11_regime_backtest_validation_plan.md) §0.5.7 待完成项 |

- **第一阶段（当前）**：纯 A 模型，各策略等权或先验比例 budget 固定不变，FirmRiskAggregator 只做求和+裁剪（[30号](30_multi_strategy_concurrency.md) §4.2）
- **第二阶段（策略 3-6 个月 PnL 后）**：上加 RegimeMetaAllocator，按 PerformanceScore 动态调占比 + Shrinkage 节流
- **过渡方案**：在 PnL 积累期内，可用 `Base × Shrinkage`（PerformanceScore=1.0 中性）先跑——regime 节流已验证有效，只是没有后验分配

#### ⑧ 外部信号交叉验证（5 档水温 + 板块轮动状态）→ §3.2.7

> **为什么需要交叉验证**：HMM regime 检测基于收益+波动统计量，是"后验状态推断"——它告诉你"市场现在处于哪种统计态"，但不直接告诉你"市场结构性水温"。A 股的 Wyckoff-Analysis 实证（[YoungCan-Wang/Wyckoff-Analysis](https://github.com/YoungCan-Wang/Wyckoff-Analysis) v2.1.x，2026-04）提供了两个**独立于 HMM 的外部信号**——大盘水温（5 档）与板块轮动状态（5 分类）——可与 HMM 4 态交叉验证，作为 Shrinkage 的辅助印证而非主信号。

**信号 A：大盘水温 5 档仓位（Wyckoff-Analysis 实证）**

| 水温 | 含义 | 建议仓位 | 实测收益（2026-04 实证） |
|---|---|---|---|
| NEUTRAL | 均线健康，正常市况 | 100% | **+1.17%（唯一正收益）** |
| RISK_ON | 短线过热 | 50% | −1.54% |
| PANIC_REPAIR | 暴跌后修复，方向未确认 | 50% | — |
| RISK_OFF | 均线破位 | 30% | — |
| CRASH | 系统性危机 | 0% | −3.2% |

核心实证结论："选股选得好不如市场选得对，水温仓控是性价比最高的风控手段"——与我们的 Shrinkage 风险节流哲学一致（regime 只回答"现在该多谨慎"）。

**信号 B：板块轮动状态 5 分类（WyckoffTradingAgent 实证）**

| 状态 | 特征 | watch_score 调整 | 系统反应 |
|---|---|---|---|
| CONSENSUS_CLIMAX（共识高潮） | 多板块同时暴涨，市场亢奋 | −0.15 | 警惕见顶 |
| DISAGREEMENT_PULLBACK（分歧回调） | 涨跌严重分化，领涨回调 | +0.01 | 微加分 |
| HEALTHY_MAINLINE（健康主线） | 一条明确主线持续领涨 | +0.03 | 加分 |
| DISTRIBUTION_RISK（派发风险） | 领涨板块高位放量滞涨 | −0.10 | **最危险状态** |
| NEUTRAL_MIXED（中性混沌） | 涨跌互现，无序 | 0 | 不加不减 |

实证验证：共识高潮后 3 日下跌 >2% 概率达 29.8%，派发风险扣分有据可依。

**交叉验证的定位（远期候选，不进 MVP 主链路）**：

| 维度 | 当前 MVP（4 态 HMM Shrinkage） | 远期（外部信号交叉验证） |
|---|---|---|
| 主信号 | HMM 4 态 + RiskSignal 13 参数 | 不变（HMM 仍是主信号） |
| 辅助信号 | 无 | 5 档水温 + 板块轮动状态作为 Shrinkage 的**印证/校验**，不替换 |
| 作用方式 | — | 当 HMM 判 r3（牛市）但水温=RISK_ON + 板块=CONSENSUS_CLIMAX → 信号冲突 → 触发 ConfidenceSignal 降档（max(P) 视为不确定，走 <60% 强收缩分支）；当两者一致 → 增强 ConfidenceSignal |
| 为什么不进 MVP | C1 已证明纯 HMM Shrinkage 有效（MaxDD 改善 7.36pp），无需叠加外部信号增加复杂度 | 外部信号的数据管线（水温/板块状态）未接入；交叉验证的冲突仲裁规则需实盘验证后才能定 |

> **与 RMATS 的解耦思想印证**：RMATS（arXiv:2605.25311, 2026-05-25）的 Risk Agent 独立于策略 agent——risk 层与策略层解耦。我们的 regime Shrinkage 同样是独立于策略层的风险节流层（regime 只收缩总暴露，不重定向资金）。5 档水温/板块轮动状态可作为**风险层的多源输入**（类似 RMATS Risk Agent 的 geopolitical stress 输入），但**不引入 RMATS 的多 agent 递归架构**——个人项目过度工程审查明确拒绝复杂多 agent 系统（见 §4.4）。外部信号以"辅助印证"身份进入风险层，而非新立 agent。
>
> **过度工程审查**：5 档水温 + 板块轮动状态若作为"主信号"会引入两条独立 regime 检测链路（HMM + 水温），增加维护成本与信号冲突仲裁复杂度。定位为"远期辅助印证"——只在 HMM 与外部信号冲突时触发 ConfidenceSignal 降档（保守化），一致时不增强（避免过度乐观），是性价比最高的接入方式。是否启用待首批策略实盘后校准（见 §6 待裁定）。

### 3.3 与上下游的关系

```
regime_detector(10号, MOD-REGIME-001) → 7维概率 + RiskSignal 13参数
    ↓
RegimeMetaAllocator(本模块, MOD-PA-007)
    ├─ ConfidenceSignal = f(max(P))  四档
    ├─ RiskSignal = g(13参数)         连续
    ├─ Shrinkage = ConfidenceSignal × RiskSignal
    ├─ allocation_i = normalize(Base × PerformanceScore × Shrinkage)
    └─ BudgetAllocation → StrategyBook(MOD-POS-020) 消费
                          ↓ budget 下调
                          BudgetChangeHandler(MOD-POS-022, 33号) 三级升级落地
```

- **上游**：regime 检测器产出 7 维概率 + RiskSignal 13 参数（[10号](10_regime_detector_spec.md) §5）
- **下游**：BudgetAllocation 发给 StrategyBook；budget 下调时触发 [BudgetChangeHandler](33_budget_change_handler.md)（33号）三级升级
- **正交性**：本模块只管"budget 怎么算 + 怎么分配"，不管"budget 下调怎么落地"（归 33号）、"单策略内仓位怎么算"（归 [31_position_sizing](31_position_sizing.md)）、"firm 层求和裁剪"（归 [32_firm_risk_aggregator](32_firm_risk_aggregator.md)）
- **effective_budget 是目标值非强制值**：RegimeMetaAllocator 产出 `effective_budget = allocation_i × global_shrinkage` 是**目标预算**，StrategyBook 的实际暴露可能 ≠ 目标（未部署完/已超配）。实际暴露低于目标→策略可自然加仓；实际暴露高于目标→budget 下调，触发 [33号](33_budget_change_handler.md) 三级升级收敛。两者差异是常态，不是 bug
- **更新频率**：effective_budget 日频重算（PerformanceScore 60 日滚动日频更新 + Shrinkage 日频更新）；盘中 regime 突变（D-SIGNAL-68 overlay 触发）时盘中重算 Shrinkage → effective_budget。日频更新意味着 budget 可能日频变动，这正是 [33号](33_budget_change_handler.md) §6 budget 变动防抖的必要性来源

### 3.4 施工算法实现（allocate 完整伪代码）

> **2026-08-10 九次审查补全**：§3.1-§3.3 定义了三因子乘法的逻辑规则与上下游关系，但缺乏统一编排入口的施工算法。以下伪代码将 Sortino 计算（§3.2.2 含 MAR=Rf + downside 样本量门槛 + gap 监控）、Shrinkage 计算（§3.2.3 四档 ConfidenceSignal × 13 参数 RiskSignal）、归一化裁剪（§3.2.4 floor/cap + N=2 无解兜底）、global_shrinkage 与 allocation 解耦（§3.1 实现注记）整合为单一 `allocate` 函数，供 [regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) MOD-PA-007 施工参考。

```python
from dataclasses import dataclass, field
import numpy as np
from collections import deque

# ── 常量定义（§3.2.2 / §3.2.3 / §3.2.4）──
FLOOR = 0.05                        # 单策略最低占比 5%（防饿死，§3.2.4）
CAP = 0.40                          # 单策略最高占比 40%（防集中，§3.2.4）
PERF_SCORE_MIN = 0.5                # PerformanceScore 映射下限（§3.2.2）
PERF_SCORE_MAX = 1.5                # PerformanceScore 映射上限（§3.2.2）
SORTINO_NEUTRAL = 1.0               # Sortino=1.0 → PerformanceScore=1.0（中性）
SORTINO_FLOOR = 0.0                 # Sortino≤0 → PerformanceScore=0.5（砍半）
SORTINO_CEILING = 2.0               # Sortino≥2.0 → PerformanceScore=1.5（×1.5）
DOWNSIDE_MIN_OBSERVATIONS = 15      # downside 样本量门槛（§3.2.2 四件套防护）
COLD_START_MIN_DAYS = 30            # 冷启动过渡门槛（≥30 日起算部分 Sortino）
GAP_NORMAL_CEILING = 1.5            # Sortino/Sharpe gap 正常上限（quantt.co.uk 2026-04 实证 1.3-1.5，施工要点 #11）
MAR_ANNUAL = 0.02                   # MAR = Rf ≈ 2%（货币基金年化，§3.2.2 MAR 选型）
TRADING_DAYS = 252

# ── ConfidenceSignal 四档（§3.2.3，[10号] §5.1）──
CONFIDENCE_THRESHOLDS = [
    (0.60, 0.30),   # max(P) < 60% → 0.3（强收缩）
    (0.80, 0.60),   # 60% ≤ max(P) < 80% → 0.6（中度收缩）
    (0.95, 0.85),   # 80% ≤ max(P) < 95% → 0.85（轻度收缩）
    (1.01, 1.00),   # max(P) ≥ 95% → 1.0（满部署）
]

# ── Shrinkage floor（§3.2.2 熊市最低总暴露 + §3.2.2 危机态覆盖说明）──
SHRINKAGE_FLOOR = 0.09          # = ConfidenceSignal_min(0.3) × RiskSignal_min(0.30) = 9%（r4 熊市常规态）
CRISIS_SHRINKAGE_FLOOR = 0.05   # CRISIS 态 floor 降至 5%（对齐 [31号] §2.4.3 ⑩CRISIS cap=5%，施工要点 #12）


@dataclass
class BudgetAllocation:
    """RegimeMetaAllocator 产出物（§3.1 两个层次）。

    allocation_i（相对占比）回答"偏向哪个策略"，global_shrinkage（总暴露因子）
    回答"现在该多谨慎"，effective_budgets = allocation × global_shrinkage 是策略实收预算。
    """
    allocations: dict[str, float]      # {strategy_id: weight}，Σ=1.0，floor≤w≤cap
    global_shrinkage: float            # 总暴露因子 0.09~1.0
    effective_budgets: dict[str, float]  # {strategy_id: allocation × global_shrinkage}
    confidence_signal: float           # ConfidenceSignal 值（审计用）
    risk_signal: float                 # RiskSignal 值（审计用）
    perf_scores: dict[str, float]      # 各策略 PerformanceScore（审计用）
    sortino_sharpe_gaps: dict[str, float]  # 各策略 Sortino/Sharpe gap（§3.2.2 gap 监控）


def allocate(
    strategies: list[str],
    base_weights: dict[str, float],
    daily_returns: dict[str, deque],   # {strategy_id: deque of 60-day daily returns}
    regime_probs: np.ndarray,          # HMM 7 维概率向量（[10号] 输出）
    risk_signal_params: dict,          # RiskSignal 13 参数（[10号] §5.3.3 输出）
    current_date,                      # 当前交易日（冷启动判定用）
    strategy_start_dates: dict[str, date],  # {strategy_id: 上线日期}（冷启动判定用）
    is_crisis: bool = False,           # D-SIGNAL-68 overlay 是否触发 CRISIS 态（§3.2.2 危机态覆盖，施工要点 #12）
) -> BudgetAllocation:
    """RegimeMetaAllocator 主入口：三因子乘法分配 + floor/cap 裁剪 + Shrinkage 节流。

    流程：
      1. 计算 PerformanceScore_i（60 日 Sortino + MAR=Rf + downside 样本量门槛）
      2. 计算 global_shrinkage（ConfidenceSignal 四档 × RiskSignal 13 参数）
      3. 三因子乘法 raw_allocation_i = Base_i × PerformanceScore_i
         （Shrinkage 是全局的，归一化时约掉，只在 effective_budget 层缩放，§3.1 实现注记）
      4. 归一化 + floor/cap 迭代裁剪（含 N=2 无解兜底，§3.2.4）
      5. effective_budget_i = allocation_i × global_shrinkage

    Args:
        strategies: 策略 ID 列表（3-5 个）
        base_weights: 人工先验权重 {strategy_id: weight}（§3.2.1，冷启动等权 1/N）
        daily_returns: 各策略 60 日日频收益率序列
        regime_probs: HMM 输出的 regime 概率向量
        risk_signal_params: RiskSignal 13 参数（realized_vol 分位/量价/跨市场/虹吸/技术/新闻/筹码等）
        current_date: 当前交易日
        strategy_start_dates: 各策略上线日期（冷启动 <30 交易日 PerformanceScore=1.0 中性）
        is_crisis: bool，D-SIGNAL-68 overlay 是否触发 CRISIS 态（§3.2.2 危机态覆盖说明）

    Returns: BudgetAllocation（allocations + global_shrinkage + effective_budgets）
    """
    N = len(strategies)

    # ── Step 1: 计算各策略 PerformanceScore（§3.2.2）──
    perf_scores: dict[str, float] = {}
    sortino_sharpe_gaps: dict[str, float] = {}

    for sid in strategies:
        returns = daily_returns.get(sid, deque())
        # ⚠️ 口径：用 len(returns)（交易日数）而非 calendar days（§3.4 施工要点 #9）
        trading_days_live = len(returns)

        # 冷启动过渡（§3.2.2）：上线 <30 交易日 → PerformanceScore=1.0 中性
        if trading_days_live < COLD_START_MIN_DAYS:
            perf_scores[sid] = 1.0  # 无信息先验，不偏袒
            sortino_sharpe_gaps[sid] = 0.0
            continue

        sortino, sharpe = _compute_sortino_and_sharpe(returns)
        downside_count = sum(1 for r in returns if r < MAR_ANNUAL / TRADING_DAYS)

        # downside 样本量门槛（§3.2.2 四件套防护 #1）
        if downside_count < DOWNSIDE_MIN_OBSERVATIONS:
            # downside 样本不足 → Sortino 统计不可靠 → 强制中性
            perf_scores[sid] = 1.0
            sortino_sharpe_gaps[sid] = 0.0
            audit_log.log_warning(sid,
                f"downside 样本 {downside_count} < {DOWNSIDE_MIN_OBSERVATIONS}，"
                f"Sortino 统计不可靠，PerformanceScore 强制中性 1.0")
            continue

        # PerformanceScore 线性映射 [0,2] → [0.5,1.5]（§3.2.2）
        if sortino <= SORTINO_FLOOR:
            perf_scores[sid] = PERF_SCORE_MIN  # 0.5
        elif sortino >= SORTINO_CEILING:
            perf_scores[sid] = PERF_SCORE_MAX  # 1.5
        else:
            # 线性插值：Sortino 0→0.5, 1→1.0, 2→1.5
            perf_scores[sid] = PERF_SCORE_MIN + (sortino - SORTINO_FLOOR) / (
                SORTINO_CEILING - SORTINO_FLOOR) * (PERF_SCORE_MAX - PERF_SCORE_MIN)

        # gap 监控（§3.2.2 四件套防护 #3）：Sortino/Sharpe gap 异常大 → 疑似 inflated
        # 2026-08 搜索实证：Sortino ≈ 1.3-1.5 × Sharpe 为正常范围（quantt.co.uk 2026-04）
        # ⚠️ gap 常量语义（§3.4 施工要点 #11）：GAP_NORMAL_CEILING=1.5（正常上限）
        #    gap > GAP_NORMAL_CEILING × 1.2 = 1.8 → 疑似 inflated 警告
        #    gap > GAP_NORMAL_CEILING × 1.5 = 2.25 → 严重 inflated 强制降权复核
        gap = sortino / sharpe if sharpe > 0 else float('inf')
        sortino_sharpe_gaps[sid] = gap
        if gap > GAP_NORMAL_CEILING * 1.2:  # gap > 1.8 → 疑似 inflated
            audit_log.log_warning(sid,
                f"Sortino/Sharpe gap={gap:.2f} 异常大（正常 1.3-1.5），疑似 inflated values，"
                f"标记复核——可能 downside 样本太少或连胜期未遇回撤")

    # ── Step 2: 计算 global_shrinkage（§3.2.3 ConfidenceSignal × RiskSignal）──
    confidence_signal = _compute_confidence_signal(regime_probs)
    risk_signal = _compute_risk_signal(risk_signal_params)
    # ⚠️ CRISIS 态 floor 降级（§3.2.2 危机态覆盖说明 + 施工要点 #12）：
    #    is_crisis=True（D-SIGNAL-68 overlay）时 floor 从 0.09 降至 0.05 对齐 31号 crisis cap
    effective_floor = CRISIS_SHRINKAGE_FLOOR if is_crisis else SHRINKAGE_FLOOR  # 0.05 / 0.09
    global_shrinkage = max(effective_floor, confidence_signal * risk_signal)

    # ── Step 3: 三因子乘法 raw_allocation（§3.1 实现注记）──
    #    Shrinkage 是全局的（所有策略共用 global_shrinkage），归一化时约掉：
    #    normalize(Base_i × PerfScore_i × global_shrinkage) = normalize(Base_i × PerfScore_i)
    #    所以 raw_allocation 不含 Shrinkage，Shrinkage 只在 effective_budget 层缩放
    raw_allocation = {}
    for sid in strategies:
        raw_allocation[sid] = base_weights[sid] * perf_scores[sid]

    # ── Step 4: 归一化 + floor/cap 迭代裁剪（§3.2.4）──
    allocations = _normalize_and_clip(raw_allocation, FLOOR, CAP, strategies)

    # ── Step 5: effective_budget = allocation × global_shrinkage（§3.1 两层）──
    effective_budgets = {sid: allocations[sid] * global_shrinkage for sid in strategies}

    return BudgetAllocation(
        allocations=allocations,
        global_shrinkage=global_shrinkage,
        effective_budgets=effective_budgets,
        confidence_signal=confidence_signal,
        risk_signal=risk_signal,
        perf_scores=perf_scores,
        sortino_sharpe_gaps=sortino_sharpe_gaps,
    )


def _compute_sortino_and_sharpe(returns: deque) -> tuple[float, float]:
    """计算 60 日 Sortino + Sharpe（§3.2.2，MAR=Rf，等权滚动窗口）。

    Sortino = (R_p − MAR) / σ_d
    Sharpe  = (R_p − Rf) / σ_total
    MAR = Rf = 货币基金 ~2% 年化（§3.2.2 MAR 选型决策）

    Returns: (sortino, sharpe) 年化值
    """
    returns_arr = np.array(returns)
    n = len(returns_arr)
    if n == 0:
        return (SORTINO_NEUTRAL, SORTINO_NEUTRAL)

    # 年化收益（日均 × 252）
    r_p_annual = np.mean(returns_arr) * TRADING_DAYS
    mar_daily = MAR_ANNUAL / TRADING_DAYS
    rf_daily = MAR_ANNUAL / TRADING_DAYS  # MAR = Rf（§3.2.2 决策）

    # ── Sortino：下行偏差只统计 R_daily < MAR 的日子（§3.2.2）──
    # ⚠️ ddof 一致性：downside deviation 与 Sharpe total deviation 均用 ddof=1（样本估计），
    #    确保 gap 监控 apples-to-apples（§3.4 施工要点 #10）
    downside_returns = returns_arr[returns_arr < mar_daily]
    n_downside = len(downside_returns)
    if n_downside == 0:
        # 无下行日 → Sortino 无穷大，但实际是"连胜期 inflated"风险
        # 返回 SORTINO_CEILING（映射 1.5），由 gap 监控标记复核
        sortino = SORTINO_CEILING
    else:
        # 标准 Sortino 下行偏差（CFA Institute 2026 共识 + arXiv:2510.12725 引证）：
        # 分母用总样本量 n-1（ddof=1，与 Sharpe np.std(ddof=1) 一致），
        # 而非 n_downside-1（仅下行观测数）——后者是常见实现错误，会人为抬高 Sortino
        # （分母更小 → σ_d 更小 → Sortino 更大 → PerformanceScore 系统性高估 → budget 分配偏差）。
        # 例：n=60, n_downside=24 → n_downside-1=23 vs n-1=59 → Sortino 虚高 √(59/23)≈1.6x
        downside_deviation = np.sqrt(np.sum((downside_returns - mar_daily) ** 2) / max(n - 1, 1))
        daily_downside_dev = downside_deviation
        annual_downside_dev = daily_downside_dev * np.sqrt(TRADING_DAYS)
        sortino = (r_p_annual - MAR_ANNUAL) / annual_downside_dev if annual_downside_dev > 0 else SORTINO_CEILING

    # ── Sharpe：总标准差（对照指标，§3.2.2 gap 监控用）──
    total_deviation = np.std(returns_arr, ddof=1) if n > 1 else 0
    annual_total_dev = total_deviation * np.sqrt(TRADING_DAYS)
    sharpe = (r_p_annual - MAR_ANNUAL) / annual_total_dev if annual_total_dev > 0 else 0.0

    return (sortino, sharpe)


def _compute_confidence_signal(regime_probs: np.ndarray) -> float:
    """ConfidenceSignal 四档映射（§3.2.3，[10号] §5.1）。

    regime_probs 是 HMM 输出的状态概率向量（如 7 维），取 max(P) 映射四档：
      max(P) < 60%  → 0.30（强收缩，不确定时别赌方向）
      60% ≤ max(P) < 80% → 0.60（中度收缩）
      80% ≤ max(P) < 95% → 0.85（轻度收缩）
      max(P) ≥ 95% → 1.00（满部署，高确信度）

    60% 阈值的外部印证：1uptick 2026-06 机构方案"max(P)<60% 减仓 30-50%"完全一致。
    """
    max_p = float(np.max(regime_probs))
    for threshold, signal in CONFIDENCE_THRESHOLDS:
        if max_p < threshold:
            return signal
    return CONFIDENCE_THRESHOLDS[-1][1]  # 默认 1.0


def _compute_risk_signal(params: dict) -> float:
    """RiskSignal 13 参数连续值（§3.2.3，[10号] §5.3.3）。

    RiskSignal = clamp[0.30, RiskBase × 共振惩罚 + 机会恢复, 1.00]
    13 参数：realized_vol 分位 / 量价时空 / 跨市场相关性 / 虹吸态 /
             技术背离 / 新闻情绪 / 筹码结构等。
    #1 门控：危机期 #1<1.0 才激活附加参数。

    本函数是占位接口——实际 13 参数聚合逻辑归 [10号](10_regime_detector_spec.md)
    §5.3.3 regime 检测器实现，本备忘只管"如何消费 RiskSignal 值"。
    """
    risk_base = params.get("risk_base", 1.0)
    resonance_penalty = params.get("resonance_penalty", 0.0)
    opportunity_recovery = params.get("opportunity_recovery", 0.0)
    raw = risk_base * resonance_penalty + opportunity_recovery
    return max(0.30, min(1.00, raw))


def _normalize_and_clip(
    raw: dict[str, float],
    floor: float,
    cap: float,
    strategies: list[str],
) -> dict[str, float]:
    """归一化 + floor/cap 迭代裁剪（§3.2.4，含 N=2 无解兜底）。

    算法：
      1. 归一化 raw 使 Σ=1.0
      2. 迭代裁剪：低于 floor 抬到 floor / 高于 cap 压到 cap → 再归一化
      3. 重复 2-3 次直到收敛（无策略越界）或达到最大迭代次数
      4. 若 N=2 且 floor+cap 无解 → 优先保 floor 降 cap（§3.2.4 无解兜底）

    floor/cap 有界投影数学上有限步收敛（通常 2-3 次迭代）。
    """
    N = len(strategies)

    # Step 1: 归一化
    total = sum(raw[sid] for sid in strategies)
    if total <= 0:
        # 全零 → 等权兜底
        return {sid: 1.0 / N for sid in strategies}
    alloc = {sid: raw[sid] / total for sid in strategies}

    # Step 2: 迭代 floor/cap 裁剪
    effective_cap = cap
    for iteration in range(5):  # 最多 5 次迭代
        violated = False
        # 裁剪到 [floor, effective_cap]
        for sid in strategies:
            if alloc[sid] < floor:
                alloc[sid] = floor
                violated = True
            elif alloc[sid] > effective_cap:
                alloc[sid] = effective_cap
                violated = True

        if not violated:
            break  # 收敛

        # 再归一化
        total = sum(alloc[sid] for sid in strategies)
        if total > 0:
            alloc = {sid: alloc[sid] / total for sid in strategies}

    # Step 3: 检查是否仍越界（N=2 无解场景，§3.2.4 兜底）
    still_violated = any(alloc[sid] < floor - 1e-6 or alloc[sid] > effective_cap + 1e-6
                         for sid in strategies)
    if still_violated:
        # N=2 + floor=5% + cap=40% → 数学无解（两策略都 ≤40% → Σ ≤80% ≠100%）
        # 兜底：优先保 floor（防饿死生存线不可降），放宽 cap 到 1-(N-1)×floor
        relaxed_cap = 1.0 - (N - 1) * floor
        audit_log.log_warning(
            f"floor/cap 无解兜底触发：N={N}, floor={floor}, cap={effective_cap} → "
            f"放宽 cap 到 {relaxed_cap:.2f}（优先保 floor 防饿死，§3.2.4）")
        effective_cap = relaxed_cap

        # 重新裁剪 + 归一化
        for sid in strategies:
            alloc[sid] = max(floor, min(effective_cap, alloc[sid]))
        total = sum(alloc[sid] for sid in strategies)
        if total > 0:
            alloc = {sid: alloc[sid] / total for sid in strategies}

    return alloc
```

> **施工要点**：
> 1. **MAR=Rf 硬约束**：`_compute_sortino_and_sharpe()` 中 `MAR = Rf = 0.02`（货币基金年化），**禁止**用 0% 或硬编码 target（§3.2.2 MAR 选型决策）。MAR=Rf 确保 Sortino 与 Sharpe 分子一致，gap 干净反映上行偏态强度。
> 2. **downside 样本量门槛**：`downside_count < 15` 时 PerformanceScore 强制 1.0 中性（§3.2.2 四件套防护 #1）。A 股 60 交易日 downside 样本 ~24 日，接近风险区，须防护。
> 3. **gap 监控阈值**：正常 Sortino/Sharpe gap ≈ 1.3-1.5（quantt.co.uk 2026-04 实证）；gap > 1.6 触发"疑似 inflated"警告（§3.2.2 四件套防护 #3）。
> 4. **global_shrinkage 与 allocation 解耦**：`raw_allocation = Base × PerformanceScore`（不含 Shrinkage），因为 Shrinkage 是全局的，归一化时约掉（§3.1 实现注记）。Shrinkage 只在 `effective_budget = allocation × global_shrinkage` 层缩放总暴露。**代码骨架 BUG 提醒**：若 `regime_meta_allocator.py` 当前 `_compute_raw_allocation()` 在乘法中包含 `Shrinkage_i`，应移除——全局 Shrinkage 在归一化时约掉，包含它是冗余且可能误导（暗示每策略差异化 Shrinkage，实际当前实现是全局）。
> 5. **floor/cap N=2 无解兜底**：`_normalize_and_clip()` 迭代 5 次仍未收敛 → 优先保 floor 降 cap 到 `1-(N-1)×floor`（§3.2.4 无解兜底）。N≥3 时基本不触发（数学上有解）。
> 6. **冷启动过渡**：上线 <30 日 → PerformanceScore=1.0 中性（§3.2.2）。≥30 日且有足够 downside 样本 → 起算部分 Sortino。60 日完整窗口 → 正常 Sortino 映射。
> 7. **RiskSignal 13 参数归 [10号]**：`_compute_risk_signal()` 是占位接口，实际 13 参数聚合逻辑归 [10号](10_regime_detector_spec.md) §5.3.3 regime 检测器实现。本备忘只管"如何消费 RiskSignal 值"（clamp[0.30, ..., 1.00] + 与 ConfidenceSignal 乘法）。
> 8. **ConfidenceSignal 四档阈值待 D1 校准**：当前 60/80/95% 是启发式设定（[30号] §2.2），D1 ±20% 敏感性网格未跑（[11号] §0.5.7 待完成项）。若 D1 显示某档边界是悬崖型（±20% 扰动效果骤变），需调整阈值。
> 9. **⚠️ days_live 交易日口径（十三次审查修复）**：原伪代码 `days_live = (current_date - strategy_start_dates[sid]).days` 用**自然日**（calendar days），但 `COLD_START_MIN_DAYS=30` 是**交易日**口径（§3.2.2"A 股约需 38 交易日"）。30 自然日 ≈ 20-22 交易日，会导致策略过早脱离冷启动（少 ~8-10 交易日）。**已修复**：改用 `trading_days_live = len(returns)`（returns 是日频交易日序列，len 即交易日数），口径与 COLD_START_MIN_DAYS 一致。同时移除冗余的 `or len(returns) < COLD_START_MIN_DAYS` 条件（trading_days_live 已包含此检查）。
> 10. **⚠️ ddof 一致性（十三次审查修复）**：原伪代码 Sortino downside deviation 用 `np.mean(...)`（ddof=0 总体估计），Sharpe total deviation 用 `np.std(ddof=1)`（样本估计）——**ddof 不一致导致 gap 监控 apples-to-oranges**（Sortino 系统性偏小因分母含 N 而非 N-1，gap 偏大触发误报）。**已修复**：Sortino downside deviation 改用 `np.sum(...) / max(n_downside - 1, 1)`（ddof=1 样本估计），与 Sharpe `np.std(ddof=1)` 一致。**注**：标准 Sortino 论文用 ddof=0（总体），但本项目 gap 监控要求 Sortino/Sharpe 同 ddof 才可比，选 ddof=1（样本估计是统计最佳实践，且 Sharpe 已用 ddof=1）。若需对齐原始 Sortino 论文，须两处同时改 ddof=0（gap 监控仍一致），但 ddof=1 更保守（σ 更大 → Sortino/Sharpe 更小 → gap 监控更不易误报 inflated）。
> 11. **⚠️ gap 常量语义（十三次审查修复）**：原伪代码 `gap > SORTINO_SHARPE_GAP_THRESHOLD * 2` 语义模糊——`SORTINO_SHARPE_GAP_THRESHOLD` 是什么？gap 本身？还是 delta？注释"gap > 1.6"暗示 threshold=0.8 但无定义。**已修复**：重命名常量为 `GAP_NORMAL_CEILING=1.5`（正常 gap 上限，quantt.co.uk 2026-04 实证 1.3-1.5 正常范围的上界），两级阈值：① gap > `GAP_NORMAL_CEILING × 1.2` = 1.8 → 疑似 inflated 警告（log_warning + 标记复核）；② gap > `GAP_NORMAL_CEILING × 1.5` = 2.25 → 严重 inflated 强制降权复核（施工时须实现两级，伪代码仅展示第一级）。常量语义清晰：GAP_NORMAL_CEILING 是"正常 gap 上限"，乘子 1.2/1.5 是"超出正常范围的严重程度分级"。
> 12. **⚠️ CRISIS 态分支（十三次审查新增，§3.2.2 危机态覆盖说明）**：`allocate()` Step 2 `global_shrinkage = max(SHRINKAGE_FLOOR, confidence_signal * risk_signal)` 须新增 CRISIS 态检查——当 `is_crisis=True`（D-SIGNAL-68 overlay 触发）时，`SHRINKAGE_FLOOR` 从 0.09 降至 0.05（对齐 [31号] §2.4.3 ⑩CRISIS cap=5%），否则 meta 层目标值虚高（9% vs firm 层实际 5%）导致 [33号] BudgetChangeHandler 收敛异常。施工实现：`effective_floor = CRISIS_SHRINKAGE_FLOOR if is_crisis else SHRINKAGE_FLOOR`，须首批策略上线前实现。
> 13. **⚠️ Sortino 下行偏差分母修复（十四次审查 CRITICAL bug 修复）**：原伪代码 `downside_deviation = sqrt(Σ(...) / max(n_downside - 1, 1))` 分母用 `n_downside-1`（仅下行观测数）——这是**常见实现错误**（CFA Institute 2026 共识 + arXiv:2510.12725 引证），会人为抬高 Sortino（分母更小 → σ_d 更小 → Sortino 更大 → PerformanceScore 系统性高估 → budget 分配偏差）。例：n=60, n_downside=24 → n_downside-1=23 vs 正确的 n-1=59 → Sortino 虚高 √(59/23)≈1.6x。**已修复**：分母改用 `max(n - 1, 1)`（总样本量 n-1，ddof=1 与 Sharpe 一致），分子仍只对 `R < MAR` 的日子求和（above-MAR 日子贡献 0）。这是比 ddof 不一致（施工要点 #10）更严重的统计正确性 bug——ddof 影响量级 ~3%，分母用 n_downside 影响量级 ~60%。
> 14. **⚠️ Bootstrap CI 远期候选（十四次审查新增，十六次审查 CRITICAL 修正：BCa → block bootstrap）**：当前 Sortino 防护四件套（downside<15 强制中性 + cap 兜底 + gap 监控 + 待校准）是**点估计 + 规则防护**——给出 Sortino 的一个值 + 规则裁剪极端值。arXiv:2510.12725（Oliveira et al. 2025-10, USP/UCL）提出**非参数 bootstrap 鲁棒优化**——把 Sortino 当作带置信区间的随机量而非点估计，用 bootstrap 重采样构造 Sortino 的 95% 置信区间。**升级路径**：若首批策略 PnL 后发现 PerformanceScore 月度变动 >0.3 频繁（§3.2.2 实盘校准触发条件），可将 PerformanceScore 从"点估计 Sortino 线性映射"升级为"bootstrap 下分位 Sortino 映射"——用 5% 下分位（保守估计）而非点估计做映射，天然处理小样本偏差。**不进 MVP**（bootstrap 重采样增加 ~100ms 计算开销 + 实现复杂度），但作为四件套防护的升级路径登记。
>
>    **⚠️ 十六次审查 CRITICAL 修正（Soloviov 2026-06 实证）**：原方案用 **BCa（Bias-Corrected and accelerated）bootstrap**，但 Soloviov《Do Bootstrap Confidence Intervals for Backtest Statistics Cover?》(bootstrap.marketmaker.cc, 2026-06-10, arXiv-ready) 的 6000 次受控实验证明：**BCa 仅在 iid 下有效（覆盖率 0.954），在 AR(1) φ=0.3 自相关下 BCa 救不了**（覆盖率 0.838 vs 名义 0.95）——"失败的是 resampling scheme 而非区间公式"。A 股日频收益率存在自相关（情绪周期/趋势惯性），60 日短窗口 + regime switching 是最坏组合。**正确升级路径：stationary block bootstrap（Politis-Romano 自动块长）替代 BCa**——block bootstrap 保留序列内依赖结构，在 AR(1) 下覆盖率恢复到 0.946。实践配方：① 绝不要按 bar 重采样依赖 PnL（iid bootstrap 在自相关下系统性低估方差）；② 默认用自动块长的 stationary block bootstrap 或 Lo HAC 标准误；③ 把 bootstrap 回撤分位数当下界（最大回撤分位数在所有场景下都乐观偏差：iid 0.08-0.10 / regime 0.13-0.17 / AR(1) 0.23）。BCa 保留为 ≥252 日窗口且收益近似 iid 时的长窗口选项（二阶精确、transformation-respecting）。**CI_TOO_WIDE 守卫**（Pancake Engine 2026-05 / Ding & Martin 2017）：当 `(ci_high - ci_low) / |point_estimate| > 5.0` 时该 PerformanceScore 不可信，触发更强 Shrinkage——5× 阈值来自 Sharpe ratio 校准，工程上简单有效。
> 15. **⚠️ PerformanceScore 选择偏差收缩远期候选（十八次审查新增，James-Stein 估计器）**：当前 PerformanceScore 把每个策略的 Sortino **独立**映射到 [0.5,1.5]——但本项目是多策略系统（[30号] 首批 3-5 策略），PerformanceScore 的**实际用途是策略间相对排序+差异化分配**，这构成"选择"操作（给高 Sortino 策略更多 budget）。Pav《Post-Selection Estimation of Sharpe Ratios》(arXiv:2606.01650v1, 2026-06-02) 系统测试 5 种"选中最高 in-sample Sharpe 策略后估计其真实 Sharpe"的修正估计器（polyhedral lemma / James-Stein 收缩 / debias max Sharpe / thresholding / empirical Bayes），**结论：James-Stein 估计器在多数现实参数下最优**（紧随其后是 GMLEB 经验贝叶斯），且对资产收益相关性鲁棒。James-Stein 收缩因子 `s = (1 - (k-2)·σ²/||ζ̂||²)₊`（positive-part，k=策略数≥3 时生效），把每个策略的 Sortino 往横截面均值收缩——**离群高 Sortino 被拉回最多**（正是选择偏差膨胀的方向）。与 34号 的关联：① N=3-5 策略满足 James-Stein 适用条件（k≥3）；② 当前四件套防护（downside<15 中性 + cap 1.5 + gap 监控 + 待校准）是**单策略绝对值防护**，James-Stein 是**多策略相对值防护**（防止"选了表现最好的策略→其 Sortino 被选择膨胀→过度分配"），两者正交互补；③ 实现成本极低（~20 行：算横截面 Sortino 均值 + 收缩因子 + 修正后映射），不换框架。**不进 MVP**（首批策略数与 track record 未定，收缩因子需实盘数据校准），但作为 PerformanceScore 多策略选择偏差防护的远期升级路径登记——若首批策略实盘后发现"上月 Sortino 最高的策略本月 PerformanceScore 虚高→次月反转"（选择偏差表征），James-Stein 收缩是第一修正路径。
> 16. **⚠️ Block-wild Bootstrap 评估·过度工程纠偏（十八次审查新增）**：待办任务曾登记"评估 Block-wild Bootstrap 作为 stationary block bootstrap 的异方差增强"。Block-wild bootstrap = block 重采样（保留自相关）× wild 随机权重（保留异方差/GARCH），理论上同时处理 AR(1) + GARCH。**评估结论：不采纳，登记为已评估的过度工程**。依据 Soloviov 2026-06 受控实验（§8.1 已引）的明确发现：**"GARCH 与 regime 波动率对 Sharpe 覆盖率损害很小"**——stationary block bootstrap 在 GARCH(1,1) 和 Markov regime-switching 下覆盖率接近 nominal（无需 wild 权重修正），仅 AR(1) 自相关是主要损害源且 stationary block bootstrap 已修复（覆盖率 0.838→0.946）。A 股日频收益率虽有波动率聚类（GARCH 特征），但 Soloviov 证据表明 Sharpe 覆盖率对 GARCH 不敏感→block-wild 的异方差修正收益边际、实现复杂度增加（wild 权重 Rademacher/Mammen 分布选择 + 与 block 重采样的耦合），**不符合 MVP 简洁原则**。延续过度工程纠偏纪律：stationary block bootstrap（v2.4.0 已定）是 A 股 60 日短窗口 Sortino CI 的充分方案，block-wild bootstrap 保留为"若未来发现 PerformanceScore bootstrap CI 在 GARCH 区间系统性偏窄"时的备选升级路径，但不预施工。

## 4. 考虑过的替代方案（拒绝理由）

### 4.1 RegimeScore（regime 做 alpha 择时，重定向资金）—— 拒绝

- **拒绝理由**：Morwane 实证 Sharpe 1.43→0.87（**降**）。regime 择时判错 = 主动亏损；且 RegimeScore 在 meta 层重新引入估计误差放大，与 A 模型"加法替代优化器"哲学矛盾
- 详见 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2 裁定 + §7.4 Morwane 实证

### 4.2 MVO 统一优化器（协方差矩阵分配）—— 拒绝

- **拒绝理由**：协方差估计是研究课题（5000×5000 矩阵），A 股情绪周期切换时相关性飙升到 0.8+，优化器放大输入噪声。详见 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §3.1

### 4.3 等权固定不调（无 RegimeMetaAllocator）—— 第一阶段方案，非拒绝

- **定位**：第一阶段（当前）就用这个——各策略等权或先验比例，budget 固定不变
- **不升级的理由不成立**：C1 已证明 Shrinkage 节流有效（MaxDD 改善 7.36pp），第二阶段有 PnL 后升级到 RegimeMetaAllocator 有明确收益

### 4.4 复杂 RL/动态优化分配器 —— 拒绝

- **拒绝理由**：过度工程。三因子乘法 + floor/cap 是最简方案，O(N) 复杂度。RL 分配器需训练、调参、监控，且黑箱不可解释。misango 2026-03 实证：简单方案（60/40）在交易成本后优于复杂 ML 方案

### 4.5 Kelly Criterion / Black-Litterman —— 拒绝

- **Kelly Criterion**：按胜率/赔率最优下注。拒绝理由——A 股策略胜率/赔率估计误差大（情绪市波动剧烈），Kelly 对估计误差极敏感（稍有偏差即过度集中或过度保守），需 Kelly fraction（如 1/4 Kelly）打折扣到与三因子乘法无本质差异
- **⚠️ Conformal Kelly 远期精炼（十八次审查新增，不推翻 Kelly 拒绝但登记精炼路径）**：Ryan《Conformal Kelly: Conformal Prediction Intervals as the Scale in Fractional Kelly Position Sizing》(arXiv:2608.01494v1, 2026-08-02) 提出**用保形预测区间宽度作为 fractional Kelly 的 σ**（`f* ≈ μ/σ²`，σ 取自 75% 保形区间半宽）——区间变宽→缩仓，区间变窄→加仓。开发窗口（2016-2021，含交易成本+1日执行滞后+杠杆上限）年化净对数增长 28.5%、Sharpe 1.34、MaxDD 27.7%；**风险控制层**：保形区间在下行方向 miss 率超历史率→判定模型失效→砍杠杆，MaxDD 27.7%→20.3%。**关键设计原则（反直觉）**：最简单的"慢、无权重、逐资产 rolling 保形分位数"胜过所有快速自适应方案（每个自适应调整代价 0.7-5.3pp 年增长）——"仓位尺寸需要宽度的稳定性而非局部尖锐性"。与 34号 的关联：① Conformal Kelly 直击"Kelly 对估计误差敏感"这一拒绝理由——保形区间提供**有限样本分布无关的覆盖率保证**（非渐近），理论上比经验 σ 更鲁棒；② **但样本外增长未保持**（2022+ 校准保持 0.745 vs 0.750 目标，但增长仅 8.5%/7.0% 低于被动基准）——作者预注册如实报告，警示"开发窗口过拟合到特定 regime"风险；③ 与三因子乘法的关系：Conformal Kelly 是**单策略仓位尺寸**（属 [31号] PositionSizing scope），非 meta 层多策略分配——34号 消费 PerformanceScore 做 budget 分配，[31号] 做单策略仓位，Conformal Kelly 若采纳应归 [31号] 单策略仓位层（替代或增强 fractional Kelly），非 34号。**结论**：不推翻 §4.5 Kelly 拒绝（Conformal Kelly 仍是 Kelly 族，对 σ 估计敏感的本质未变，仅用保形区间替代经验 σ），但登记为 [31号] Phase 4+ 单策略仓位尺寸远期精炼路径——**触发条件**：首批策略实盘后若 [31号] fractional Kelly 出现"σ 估计不稳致仓位抖动"且保形区间能提供更稳定宽度则评估。
- **Black-Litterman**：先验市场均衡 + 后验观点融合。arxiv 2410.14841 用 BL+regime 信号 IR 0.05→0.4，但 BL 需协方差矩阵（A 股情绪周期相关性飙升问题未解决，见 [30号](30_multi_strategy_concurrency.md) §3.1）+ 观点矩阵（需人工设定"观点"，个人系统无人值守无观点来源）。三因子乘法的 Base×PerformanceScore 已实现"先验+后验融合"且无协方差依赖，是 BL 的轻量替代

## 5. 上限定义（Ceiling）

### 5.1 系统上限

三因子乘法（Base × PerformanceScore × Shrinkage）+ floor/cap 是 meta 层分配的上限。不堆优化器（MVO/RL）、不堆因子（RegimeScore 已移除）、不堆档位（四档足够，见 §6 过度工程审查）。

### 5.2 演进路径

- **第一阶段（当前）**：纯 A 模型，等权/先验固定 budget，FirmRiskAggregator 求和裁剪
- **第二阶段（策略 3-6 个月 PnL 后）**：上加 RegimeMetaAllocator，PerformanceScore 动态调占比 + Shrinkage 节流
- **远期（可选）**：状态条件协方差 RARP（[11号](11_regime_backtest_validation_plan.md) §0.6.7 华安证券 RARP）——从"缩放 budget"升级到"按状态重估风险结构"。但本项目定位是"风险节流器"（防御性），RARP 是组合优化器（进攻性），当前不在 scope
- **远期（可选）·MPC 多期预测路径**：Nystrup/Boyd/Lindström/Madsen《Multi-period portfolio selection with drawdown control》（Annals of Operations Research 2019，2026 多篇引用复现）——Model Predictive Control 动态优化，基于多变量 HMM 的多期收益均值/协方差预测，**根据已实现回撤调整风险厌恶系数**（realized drawdown → γ 动态）。核心机制：每个时点求解开环约束优化，只执行首步控制动作，新观测到达后重算（receding horizon）。实证：以小或无 mean-variance 效率牺牲控制回撤，加杠杆可进一步提升收益不增 MaxDD。

  | 维度 | 当前 Shrinkage（MVP） | MPC 多期预测（远期） |
  |---|---|---|
  | 优化方式 | 单期缩放（global_shrinkage × allocation） | 多期滚动优化（预测 H 期，执行 1 期） |
  | 回撤控制 | 静态四档 ConfidenceSignal（max(P) 映射） | 动态风险厌恶（realized drawdown → γ 自适应） |
  | 预测输入 | HMM 当前态概率（max(P)） | HMM 多期均值/协方差预测（forward prediction） |
  | 复杂度 | O(N)，无协方差 | 需多变量 HMM 多期预测 + 凸优化求解器 |
  | 为什么不进 MVP | C1 已证明静态 Shrinkage 有效 | MPC 需 HMM 多期预测管线（未建）+ 凸优化求解器（CVXPY 依赖）+ 多期协方差估计（A 股情绪周期相关性飙升问题未解，见 [30号](30_multi_strategy_concurrency.md) §3.1）；个人项目过度工程审查：MPC 是机构级方法，当前规模不需要 |

  **MPC 对 Shrinkage 的启发（可先吸收思想不换架构）**：MPC 的"根据已实现回撤动态调整风险厌恶"思想，可作为当前四档 ConfidenceSignal 的**未来增强**——不是静态 max(P) 映射，而是叠加 realized drawdown 反馈（如当前回撤已 >10%，即使 max(P) 高也强制降档）。这个增强可在不引入完整 MPC 框架的前提下，作为 §3.2.7 外部信号交叉验证的"回撤通道"实现。完整 MPC 框架待 [11号] §0.6 层次 HMM 升级 + 协方差估计问题解决后评估

- **远期（可选）·Statistical Jump Model（JM）路径**：Shu-Yu-Mulvey《Downside risk reduction using regime-switching signals: a statistical jump model approach》（Journal of Asset Management 25(5):493-507, 2024；arXiv:2402.05272）提出 **Statistical Jump Model（统计跳跃模型，JM）**——与传统 Markov-switching HMM 的根本区别是**显式跳跃惩罚（jump penalty）λ**：每次状态转换付出 λ 代价，从而**增强 regime 持续性**（persistence），抑制 HMM 高频状态抖动。JM 用动态规划 + 坐标下降交替迭代特征质心与状态路径，**特征集仅需收益序列衍生指标**（DD_10 + Sortino_20 + Sortino_60 三维），无需协方差矩阵。实证：US/Germany/Japan 1990-2023 含交易成本+执行延迟，JM-guided 策略在波动率、MaxDD、Sharpe 上**全面优于 HMM-guided 与 buy-and-hold**。

  | 维度 | 当前 HMM 4 态（MVP） | Statistical Jump Model（远期） |
  |---|---|---|
  | regime 持续性 | HMM 转移概率隐式决定（无显式约束） | **显式 jump penalty λ 控制转换频率**——λ 越大 regime 越持久，直接对抗 HMM 高频抖动 |
  | 特征集 | 收益+波动统计量（HMM 输入） | DD_10 + Sortino_20 + Sortino_60（**与我们 PerformanceScore 的 Sortino 同源**——JM 直接消费 Sortino 特征做 regime 推断） |
  | 协方差需求 | 无（Shrinkage 只用 max(P) + RiskSignal） | 无（JM 仅用单资产收益衍生特征，不估协方差） |
  | 状态数 | 4 态（BIC 选优，[11号](11_regime_backtest_validation_plan.md) §0.5.2） | 2 态（Bull/Bear，JM 原始）/ 3 态（Cortese-Kolm-Lindström 2026 信息准则选优 MSCI）/ 4 态（Snow-Ouyang 2026 stress-aware） |
  | 复杂度 | HMM EM 训练 + 前向推理 | 动态规划 + 坐标下降（O(T·K)，T=样本长度，K=状态数） |
  | 为什么不进 MVP | C1 已证明 HMM 4 态 Shrinkage 有效（MaxDD 改善 7.36pp） | JM 需重写 regime 检测器（[10号](10_regime_detector_spec.md)），C1 验证基于 HMM 须重跑；个人项目过度工程审查：MVP 先用 HMM，JM 列第二阶段后远期候选 |

  **JM 对 Shrinkage 的三个关键启发（可先吸收思想不换架构）**：

  1. **regime 持续性是回撤的一阶决定因素**：arXiv:2603.04441《Explainable Regime-Aware Investing》实证"regime inference stability—particularly identity preservation—is a first-order determinant of portfolio drawdown"——JM 的 jump penalty 正是"identity preservation"的显式机制。**我们的 HMM 4 态无显式持续性约束**，可吸收此思想：在 [10号](10_regime_detector_spec.md) regime 检测器加"最小 regime 持续期"约束（如最少 5 个交易日才允许状态切换），等价于离散版 jump penalty，无需换 JM 框架
  2. **Sortino 特征双重用途**：JM 用 Sortino_20/Sortino_60 作为 regime 推断输入特征，**与我们 §3.2.2 PerformanceScore 用 60 日 Sortino 做后验分配同源**——中金 CICC 2026-06 实证（股-债-金八资产）JM + Sortino 特征使三资产风险平价 MaxDD -7.07%→-3.23%、卡玛比率 0.77→1.59。这印证"Sortino 既能做 regime 检测又能做 PerformanceScore"的双重价值，我们的 60 日 Sortino 选择有 JM 实证支撑
  3. **JM-MPC 混合框架**：Li et al. 2025《Regime-Switching Asset Allocation Using a Framework Combining a Jump Model and Model Predictive Control》（Mathematics 13(17):2837）——JM 识别 regime + MPC 滚动优化，在高波动期显著降低回撤。这是上述 MPC 远期候选与 JM 远期候选的**融合路径**：JM 替换 HMM 做 regime 检测（持续性更强）+ MPC 做多期优化（回撤动态控制），是"换 regime 检测器 + 换优化器"的双重远期升级路径

  **中金 CICC 2026-06 A 股实证的关键启示**：中金将 JM 应用于中国股-债-金市场，**设跳跃惩罚 λ：权益/黄金=50，债券=25**（债券更稳定需更小 penalty 区分微弱状态变化）；强制避险持续**至少 60 个交易日**（与我们 Sortino 60 日窗口巧合一致）；增强信号（须债券同步看空才确认系统性风险）使预警天数大降但避险效果同等或更好——**"多资产确认 + 强制持续期"是降低 false positive 的有效机制**。我们单市场（A 股）无"债券看空"交叉确认维度，但 §3.2.7 外部信号交叉验证（5 档水温 + 板块轮动）可起类似"多源确认"作用。

  **远期演进路径排序**：① **近期**（不换架构）：HMM 4 态 + 加最小持续期约束（吸收 JM 持续性思想）+ §3.2.7 外部信号交叉验证；② **中期**（换检测器不换优化器）：HMM→JM/SJM 替换，C1 重跑验证；③ **远期**（换检测器+换优化器）：JM-MPC 混合（Li 2025），需协方差估计问题先解决。MVP 不采纳 JM——C1 已证明 HMM Shrinkage 有效，JM 的持续性优势需首批策略实盘后若发现 HMM 状态抖动导致 PerformanceScore 跳变频繁时再评估升级

##### 第十六条远期候选：Sticky HMM with Dirichlet Self-Transition Prior（2026-08-10 十六次审查新增）

> **来源**：Staures & Kabašinskas《Identifiable Regime Detection in Pension Fund Networks via Sticky Hidden Markov Models》(preprints.org 2026-06-02, DOI:10.20944/preprints202606.0111.v1；同行评审版 Mathematics 2026, 14(14):2463)。

**核心机制**：Bayesian sticky 转移先验 `π_k ~ Dirichlet(α·1 + κ·e_k)`，其中 κ 控制自转移持续性——期望自转移概率 `E[π_kk] = (α+κ)/(K·α+κ)`。κ 越大 regime 越持久（直接对抗 HMM 高频抖动）。论文识别 3 个潜态，高风险期 cluster 跟踪误差放大 1.09×-1.23×，与 PCA absorption ratio + DTW 层次聚类组合。

| 维度 | 当前 HMM 4 态（MVP） | Sticky HMM（远期） | JM（远期） | Hybrid HMM Poisson（远期） |
|---|---|---|---|---|
| 持续性机制 | HMM 转移概率隐式（无约束） | **Dirichlet 先验 κ 参数**显式控制自转移 | 显式 jump penalty λ | **Poisson jump-duration** 强制尾部态驻留 |
| 实现侵入性 | — | **极低**（转移矩阵估计加 1 行先验） | 高（重写检测器） | **低**（直接转移计数替代 EM，无后处理层） |
| 参数估计 | Baum-Welch EM | 贝叶斯推断（κ 由 CV 选择） | 动态规划 + 坐标下降 | **直接转移计数（绕过 Baum-Welch EM）** |
| 状态划分 | BIC + 收益/波动统计量 | 同当前 HMM | DD_10 + Sortino_20/60 | **Laplace 分位数定义状态**（非聚类） |
| 统计规范性 | 标准 | **最规范**（贝叶斯先验是"状态持续性"的统计标准方法） | 工程化（非贝叶斯） | 半参数（频率派 + Poisson 驻留约束） |

**与 JM / Hybrid HMM Poisson 的关系**：四条路径共享"增强 regime 持续性"目标但机制不同——Sticky HMM 是**先验约束**（训练时偏置自转移），JM 是**转换成本**（每次切换付 λ 代价），Hybrid HMM Poisson 是**停留时间约束**（Poisson jump-duration 强制尾部态 dwell time）。Sticky HMM 是四者中**实现侵入性最低**的（仅需在转移矩阵估计加 Dirichlet 先验，不重写 forward-backward），且**统计上最规范**（贝叶斯先验是"状态持续性"的教科书方法）。Hybrid HMM Poisson 的独特优势是**参数估计比当前 HMM 更简单**（直接转移计数绕过 Baum-Welch EM），可与 Sticky HMM 叠加使用（先验 + 显式驻留双重约束）。

**为什么不进 MVP**：C1 已证明 HMM 4 态 Shrinkage 有效（MaxDD 改善 7.36pp），无显式持续性约束已足够。Sticky HMM 的 κ 参数需交叉验证选择（增加调参成本），且贝叶斯推断比 EM 略复杂。若 HMM 实盘后发现状态高频抖动（月内切换 >2 次），Sticky HMM 是比 JM 更轻量的第一升级路径——不换检测器只加先验。归 [10号](10_regime_detector_spec.md) regime 检测器实现。

##### A 股本土对标：中邮证券 LSTM-GHMM 5 态方案（2026-08-10 十六次审查新增）

> **来源**：黄子崟《市场脉搏（2）：基于 LSTM~HMM 混合方案的量化择时与动态仓位管理》(中邮证券研报, 2026-07-09, SAC S1340523090002)。

**核心架构**：LSTM 自编码器（90 日 × 25 维 → 10 维压缩）+ 高斯 HMM（GHMM）**5 态**（1 个低自维持过渡态 + 4 个高自维持稳态）。关键设计：**状态切换经"过渡态"完成而非稳态间直接跳跃**——这减少了稳态间高频切换（与我们 §5.2 JM / Sticky HMM / Poisson 持续期的"增强持续性"目标一致，但用"过渡态"结构实现而非先验/惩罚/约束）。

**关键实证**：2021 年以来多指数回测控制回撤并积累超额；**2026 年 K 型极端分化行情适应性偏弱**——超额损失精准锁定于特定状态（执行层问题，非识别层问题）。

**与 34号 的关联**：
1. **5 态结构（4 稳态 + 1 过渡态）**是第四条 regime 持续性增强路径——与 JM / Sticky HMM / Hybrid HMM Poisson 并列，但机制是"结构性过渡态"而非"先验/惩罚/约束"。A 股 2026 K 型分化下的失效场景印证我们需要 Shrinkage 因子保护
2. **轻量级干预规则修正凯利公式均值回归偏差**与我们的 Shrinkage × PerformanceScore 乘法哲学一致——都是在 regime 识别后做风险节流而非 alpha 择时
3. **2026 K 型分化失效**是 A 股本土最新实证——2026H1 量化超额从 14.17% 降至 3.11%（[新浪财经 2026-07-11](https://finance.sina.com.cn/jjxw/2026-07-11/doc-inihmkxc5002361.shtml)），K 型行情+因子失效+策略同质化使 alpha 择时难度飙升，印证我们"风险节流不做 alpha 择时"裁定

##### 第十七条远期候选：Hybrid HMM with Poisson Jump-Duration（2026-08-10 十七次审查新增）

> **来源**：Alswaidan & Varner《Hybrid Hidden Markov Model for Modeling Equity Excess Growth Rate Dynamics: A Discrete-State Approach with Jump-Diffusion》(arXiv:2603.10202v2, Cornell University, 2026-03-10 提交, 2026-04-02 修订)。

**核心架构**：三个创新组件组合——① **Laplace 分位数定义状态**（非聚类，用 Laplace CDF 将连续超额增长率离散化为分位数状态）；② **Poisson jump-duration 机制**强制高波动尾部态驻留经验现实时长（两参数：λ 控制跳频率、dwell time 约束强制尾部态持久）；③ **直接转移计数估计参数，绕过 Baum-Welch EM**（直接从观测序列数转移次数估转移矩阵，无 EM 迭代）。

**关键实证**：SPY 10 年日频数据，1000 条模拟路径——KS 检验通过率 >97%（样本内）/ 94%（样本外 2025 全年）；AD 检验 >91%。**标准 HMM 无 jump 通过更多分布检验但无法生成波动率聚类**（volatility clustering），Hybrid HMM Poisson 在分布保真 + 时序结构 + 尾部覆盖三维度上联合质量最优。可扩展至 424 资产管线（copula 依赖模型保持各资产边际 HMM 分布）。

**与其他持续性路径的关键差异**：

| 维度 | Hybrid HMM Poisson 的独特价值 |
|---|---|
| **参数估计比当前 HMM 更简单** | 直接转移计数（O(T·K) 数转移次数）vs 当前 HMM Baum-Welch EM（迭代 forward-backward）——**升级反而降低实现复杂度** |
| **Laplace 分位数状态划分** | 非聚类方法，用 Laplace CDF 定义状态边界——对重尾分布（A 股收益率尖峰厚尾）比 Gaussian HMM 聚类更贴合 |
| **Poisson jump-duration 是后验约束** | 不是先验（Sticky HMM）也不是转换成本（JM），而是**显式驻留时间约束**——直接控制"尾部态至少停留 N 天" |
| **与 JM 的 Sortino 同源** | JM 用 DD_10 + Sortino_20/60 做特征；Hybrid HMM Poisson 用超额增长率分位数——两者都消费收益衍生指标，可复用我们 §3.2.2 的 Sortino 管线 |

**为什么是 JM 的轻量替代**：JM 需动态规划 + 坐标下降交替迭代（重写检测器 + 算法复杂度高）；Hybrid HMM Poisson 的直接转移计数**比当前 HMM 的 Baum-Welch EM 还简单**（无迭代），同时通过 Poisson jump-duration 获得与 JM jump penalty 同等的持续性增强。代价是 Laplace 分位数状态划分可能不如 BIC 聚类贴合 A 股 4 态语义（r1 低波/r2 中波/r3 牛市/r4 熊市）——需校验 Laplace 分位数与现有 4 态的对应关系。

**A 股适用性评估**：
1. **Laplace 分布与 A 股收益率**：A 股日频收益率尖峰厚尾（kurtosis >3），Laplace 分布（kurtosis=3）比 Gaussian（kurtosis=3）更贴合尖峰特性——但 A 股极端尾部（如 2015 股灾、2026 K 型分化）可能需 Student-t 或 EVT 补充
2. **Poisson jump-duration 与 A 股情绪周期**：A 股情绪周期 2-3 个月，Poisson 驻留约束可设尾部态（r4 熊市）最少驻留 ~20-40 交易日（与中金 CICC JM 的"强制避险持续至少 60 交易日"同量级）
3. **直接转移计数与 walk-forward**：无 EM 迭代 → walk-forward 重训练更快（C1 验证 [11号] §0.5.7 的 D1 敏感性网格可更快跑完）

**为什么不进 MVP**：C1 已证明 HMM 4 态 Shrinkage 有效（MaxDD 改善 7.36pp），当前 HMM + Baum-Welch EM 已工作。Hybrid HMM Poisson 的"直接转移计数比 EM 更简单"是理论优势，但**实际侵入性仍需重写 [10号](10_regime_detector_spec.md) regime 检测器**（Laplace 分位数状态划分 + Poisson jump-duration 后处理），不是纯增量。若 HMM 实盘后发现状态抖动 + Baum-Welch EM 重训练耗时成为瓶颈，Hybrid HMM Poisson 是同时解决两个问题的路径——比 Sticky HMM（只解决持续性，不解决 EM 计算成本）更全面，但比 Sticky HMM 侵入性高（需重写状态划分逻辑）。归 [10号](10_regime_detector_spec.md) regime 检测器实现。

**远期演进路径排序更新（十七次审查）**：
- **① 近期**（不换架构）：HMM 4 态 + 加最小持续期约束 + §3.2.7 外部信号交叉验证
- **①.5 近期**（不换架构，最低侵入性）：**Sticky HMM Dirichlet 先验**——转移矩阵加 1 行先验，κ 由 CV 选择
- **② 中期**（换检测器不换优化器）：HMM→JM/SJM 替换，C1 重跑验证
- **②.5 中期**（加态不换检测器）：**5 态结构（4 稳态 + 1 过渡态）**——参考中邮证券 A 股本土实证
- **②.6 中期**（换检测器，参数估计更简）：**Hybrid HMM Poisson**——Laplace 分位数状态 + Poisson jump-duration + 直接转移计数（绕过 EM），比 JM 实现更轻但需校验 Laplace 分位数与 A 股 4 态语义对应
- **③ 远期**（换检测器+换优化器）：JM-MPC 混合（Li 2025），需协方差估计问题先解决

> **过度工程审查**：Sticky HMM、5 态结构、Hybrid HMM Poisson 均不进 MVP——C1 已验证 HMM 4 态有效，上述路径为首批策略实盘后若发现状态抖动问题的升级阶梯。升级优先级：Sticky HMM（侵入性最低，只加先验）> 5 态结构（加过渡态）> Hybrid HMM Poisson（换状态划分 + 绕过 EM，同时解决持续性和计算成本）> JM（完全重写检测器）。所有远期候选均登记非施工算法缺失

##### 第十八条远期候选：CHMM-t（Student-t 发射的连续 HMM）—— 重尾发射优先于持续性机制（2026-08-10 十八次审查新增，**最高优先级选项外更好算法**）

> **来源**：Alswaidan, Jin & Varner《Continuous Hidden Markov Models for Equity Returns: Heavy-Tail Emission Families and Regime-Conditional Value-at-Risk》(arXiv:2606.23492, 2026-06, West Virginia University)。KDD '26（2026-08-09~13, 济州岛）Concept Drift Detection 横评（arXiv:2606.07789, Cerqueira et al.）同期印证 regime/drift 检测方法学活跃度。

**核心发现（颠覆性）**：长期以来认为"HMM 无法复现收益率绝对值自相关的慢衰减"是**时间性**问题（→ 解法是放弃 HMM 转 HSMM/jump-duration）。本文用 **CHMM-t（Student-t 发射的连续 HMM）** 重新审视该问题，证明：**原始失败是分布性的，不是时间性的**——重尾边际分布（Student-t）而非更多 decay modes（jump-duration/HSMM）弥合了大部分拟合差距，**无需调超参数**。在 SPY walk-forward、30 只股票面板、CRSP 跨年代、6 资产篮子上验证；该模型还产出 regime-conditional VaR，通过 Christoffersen 条件覆盖检验。

**为什么这是"选项外更好的算法"且优先级最高**：

| 维度 | CHMM-t（Student-t 发射） | Sticky HMM（先验） | Hybrid HMM Poisson（持续期） | JM（jump penalty） |
|---|---|---|---|---|
| **解决的问题** | **分布性**：收益率尖峰厚尾 → Gaussian 发射低估尾部 → regime 概率估计失真 | **时间性**：状态高频抖动 → 转移概率无持续性约束 | **时间性**：尾态驻留不足 + EM 计算成本 | **时间性**：状态高频抖动 |
| **实现侵入性** | **极低**——仅改 emission 分布（hmmlearn `GaussianHMM`→自定义 t-emission，~50 行） | 低——转移矩阵加 1 行 Dirichlet 先验 | 中——重写状态划分（Laplace 分位数）+ Poisson 后处理 | 高——重写检测器（动态规划+坐标下降） |
| **2026 证据强度** | **arXiv:2606.23492 证明分布性修复 > 时间性修复**（颠覆 HSMM/jump-duration 路径的前提） | Staures 2026-06 贝叶斯先验（标准方法） | Alswaidan 2026-03 KS/AD >94% | Shu 2024 + 中金 CICC 2026 A 股实证 |
| **与 A 股契合度** | **A 股收益率尖峰厚尾显著**（kurtosis >3，Soloviov 2026-07 实证 Student-t innovations 必选） | 通用，非 A 股特定 | Laplace 分位数对尖峰有贴合但 kurtosis=3 不足 | DD_10+Sortino 特征 A 股可用 |
| **是否换检测器** | **否**（只换 emission，[10号] HMM 架构不变） | 否（加先验） | 是（换状态划分） | 是（完全重写） |
| **C1 验证影响** | **最小**——emission 换 t 后重跑 C1 即可，4 态语义不变 | 小——加先验后重跑 C1 | 中——Laplace 分位数需校验与 4 态对应 | 大——重写检测器 + C1 重跑 |

**关键论据**：
1. **arXiv:2606.23492 的颠覆性结论**："重尾发射比 jump-duration 机制更重要"——直接挑战第十七条 Hybrid HMM Poisson 的前提（Poisson jump-duration 解决的是时间性，但问题根源可能是分布性）。CHMM-t 用更低的实现成本（~50 行 emission 替换 vs 重写状态划分+Poisson 后处理）解决更根本的问题（分布性）
2. **与 Soloviov 2026-07 一致**：34号 §8.1 已引 Soloviov 受控实验——"Student-t innovations 修复几乎所有 VaR 覆盖误差（99% VaR 违规率 1.58%→1.03%），尾形效应比不对称效应大一个数量级"。CHMM-t 是同一原理在 HMM emission 层的应用（Soloviov 是 GARCH innovation 层）
3. **项目记忆已认定非过度工程**：Student-t HMM 被评估为非过度工程，优先在 Phase 4 鲁棒性阶段实施——本条是对该项目记忆决策的文档化落地
4. **hmmlearn 可直接实现**：`hmmlearn.GaussianHMM` 的 emission 可替换为 Student-t（需自定义 emission 类或用 `pomegranate` 库的 t-emission），无需重写 forward-backward/Viterbi——**实现成本是所有远期候选中最低的**
5. **regime-conditional VaR 副产品**：CHMM-t 自然产出每个 regime 态的 VaR，可反哺 [36号] VaR 计算器的 regime-aware 增强（当前 [36号] VaR 是静态的，远期可升级为 regime-conditional）

**A 股适用性评估**：
1. **A 股收益率尖峰厚尾**：A 股日频收益率 kurtosis 显著 >3（Soloviov 2026-07 实证），Gaussian HMM 的 emission 系统性低估尾部 → r4 熊市态的极端日（如 -8% 跌停潮）概率被低估 → ConfidenceSignal 在极端日仍可能给出高确信度（误判）。Student-t emission 的自由度 ν 估计能捕捉这种厚尾
2. **ν 自由度的 A 股校准**：Soloviov 2026-07 建议 ν=5（GJR-GARCH Student-t innovations），CHMM-t 的 ν 可用 MLE 估计 + walk-forward 校准——首批策略实盘后用 A 股数据估 ν
3. **与 4 态语义兼容**：CHMM-t 只改 emission 不改状态划分，r1/r2/r3/r4 语义不变，C1 验证可复用——是侵入性最低的"增强"而非"替换"

**为什么不进 MVP**：C1 已证明 Gaussian HMM 4 态 Shrinkage 有效（MaxDD 改善 7.36pp），当前 Gaussian emission 已工作。CHMM-t 的"重尾发射修复分布性"是**鲁棒性增强**（Phase 4 目标），非 MVP 功能缺口。但**若首批策略实盘后发现**：① 极端日 ConfidenceSignal 误判（r4 熊市极端日仍高确信度）；② regime-conditional VaR 与实际尾部不匹配；③ Sortino/Sharpe gap 监控频繁触发疑似分布性问题——则 CHMM-t 是**第一升级路径**（比 Sticky HMM 更优先，因为解决更根本的分布性问题且实现成本同样低）。

**远期演进路径排序更新（十八次审查，CHMM-t 提升为第一优先级）**：
- **① 近期**（不换架构）：HMM 4 态 + 加最小持续期约束 + §3.2.7 外部信号交叉验证
- **①.4 近期**（不换架构，**最高优先级**，十八次审查新增）：**CHMM-t（Student-t emission）**——仅改 emission 分布 ~50 行，解决分布性问题（arXiv:2606.23492 证明比时间性修复更根本），项目记忆已认定非过度工程，**优先于 Sticky HMM**
- **①.5 近期**（不换架构，最低侵入性）：**Sticky HMM Dirichlet 先验**——转移矩阵加 1 行先验，κ 由 CV 选择
- **② 中期**（换检测器不换优化器）：HMM→JM/SJM 替换，C1 重跑验证
- **②.5 中期**（加态不换检测器）：**5 态结构（4 稳态 + 1 过渡态）**——参考中邮证券 A 股本土实证
- **②.6 中期**（换检测器，参数估计更简）：**Hybrid HMM Poisson**——Laplace 分位数状态 + Poisson jump-duration + 直接转移计数（绕过 EM），比 JM 实现更轻但需校验 Laplace 分位数与 A 股 4 态语义对应
- **③ 远期**（换检测器+换优化器）：JM-MPC 混合（Li 2025），需协方差估计问题先解决

> **过度工程审查更新（十八次审查）**：CHMM-t（Student-t emission）是所有远期候选中**实现成本最低**（~50 行 emission 替换，不换检测器/不换状态划分/不重写 C1）且**证据最颠覆**（arXiv:2606.23492 证明分布性修复优先于时间性修复，直接挑战 HSMM/jump-duration 路径前提）的路径。项目记忆已认定 Student-t HMM 非过度工程优先在 Phase 4 实施——本条是该决策的文档化落地。**升级优先级更新**：CHMM-t（分布性，~50 行，最高优先级）> Sticky HMM（时间性-先验，1 行先验）> 5 态结构（时间性-过渡态）> Hybrid HMM Poisson（时间性-持续期+绕过 EM）> JM（时间性-完全重写）。所有远期候选均登记非施工算法缺失，MVP 用 Gaussian HMM 4 态（C1 已验证有效）。

##### 第十九条远期候选：HSMM（显式持续期半马尔可夫）+ HMM-GAS（score-driven 时变转移）+ BOCPD（贝叶斯在线变点）三条并行路径（2026-08-10 十八次审查新增）

> **来源**：① HSMM——libhmm issue #50（2026-07-04 开启，正式列为架构增强）+ Pohle et al. PHSMM R 包（arXiv:2101.09197，penalized MLE 无分布假设 dwell-time 估计）+ Vedant-Choudhari/hsmm-regime-model（Python 实现）；② HMM-GAS——André Lucas 厦门大学讲座（2026-04-21，score-driven 模型综述）+ R 包 gasmodel v0.6.2（2026-05-17）；③ BOCPD——Fast-BOCPD 库（pip install fast-bocpd，14000-43000 obs/sec，含 Student-t outlier-robust 模型）+ 朱映秋等《统计研究》2025 第 1 期自适应 BOCPD（上证综指验证，CSSCI/北大核心）。

**三条路径的共同定位**：均为"选项之外"的 regime 检测增强路径，与第 1-18 条远期候选正交（不重叠），登记为远期候选池的并行选项，MVP 不采纳。

| 路径 | 核心思想 | 与现有候选的差异 | 2026 证据 | 实现成本 |
|---|---|---|---|---|
| **HSMM（显式持续期）** | HMM 隐含几何分布 dwell time（无记忆），HSMM 显式建模每个状态的 duration distribution（Poisson/Negative Binomial/Gamma/非参数）突破此限制 | Hybrid HMM Poisson（第17条）是 HSMM 的特化（Poisson 持续期 + Laplace 分位数）；HSMM 是通用框架，可用 Negative Binomial 处理过离散停留时间（A 股熊市停留时间方差 > 均值时 Poisson 不够） | libhmm 2026-07 架构增强 + Politecnico Milano 硕士论文 S&P 500 对比 HSMM>HMM + PHSMM 无分布假设 | 中（truncated forward-backward O(TN²D_max)，有 Python 实现） |
| **HMM-GAS（score-driven 时变转移）** | 转移概率不固定，由观测驱动的 GAS 方程演化 `p_{jj,t}=exp(f_{j,t})/(1+exp(f_{j,t}))`，`f_{j,t+1}=ω+A·s+B·f`（s 是条件似然 scaled score） | 观测驱动（observation-driven）无需 MCMC，自然适应 regime 不稳定性——是 HMM 与 HSMM 之间的"第三条路"（持续性不靠先验/持续期，靠转移概率随观测自适应） | André Lucas 2026-04 讲座 + gasmodel R 包 v0.6.2 | 中（GAS 方程 + gasmodel 库） |
| **BOCPD（贝叶斯在线变点）** | 维护 run-length（距上次变点时间）后验分布，每步更新——问题从"我们在哪个状态"转为"刚发生了变化吗" | 产出概率而非二元信号，可按比例调仓（与 ConfidenceSignal 软映射同构）；天然处理不确定性；online 友好。**《统计研究》上证综指验证**（A 股本土实证） | Fast-BOCPD 库（含 Student-t）+ 朱映秋 2025 上证综指自适应 BOCPD | 低（pip install，~100 行集成） |

**为什么三条均不进 MVP 但登记**：① C1 已验证 HMM 4 态有效，三条路径均为"换检测器/换范式"的远期升级；② HSMM 是 Hybrid HMM Poisson 的通用版（已登记第17条），登记通用版为的是若 Poisson 持续期不足以拟合 A 股过离散停留时间可升级到 Negative Binomial；③ HMM-GAS 的"观测驱动时变转移"是独特范式（非先验/非持续期/非重尾），与 arXiv:2606.06190（34号 §8.1 已引）"日频 TVTP 不必要"结论有张力——但 GAS 是连续时变而非离散 TVTP，可能更适合 regime 不稳定性；④ BOCPD 的"变点检测"范式与 HMM 的"状态分类"正交，CUSUM+BOCPD+HMM 三信号集成（mathandmarkets 2026-01-30）是 ensemble 思路，可作 Phase 4+ 鲁棒性增强。三条均归 [10号](10_regime_detector_spec.md) regime 检测器远期实现。

### 5.3 为何这是上限而非妥协

- Morwane 实证：regime 做 risk-throttle Sharpe 不变（1.43）、MaxDD 改善 3.9pp、Calmar +38%——**同一个 regime 信号，用于进攻有害，用于防守有益**
- 三因子乘法是 Morwane risk-throttle 模式的直接工程化，无自创方法
- Invesco+清华 2026-04 + I-am-Uchenna 2026-01 + arxiv 2410.14841 三源一致：regime-based 动态分配改善回撤和风险调整收益

## 6. 待裁定（暂缓）

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| Base_i 人工先验权重 | 首批策略未确定（[30号](30_multi_strategy_concurrency.md) §6.1 待确认 3 策略） | 首批策略上线 |
| PerformanceScore 指标选型（Sortino primary / Sharpe 对照）+ 映射区间 [0.5,1.5] + 60 日窗口 + Rf 取值 + MAR=Rf 选型 + downside 样本量门槛 + **60 日 vs 36 个月机构标准差距** + 加权方式（等权 vs EMA） | 无策略 PnL 验证；Sortino vs Sharpe 实测 gap 待复核；60 日 downside 样本 ~24 日，样本量充足性待实测（ecassets/foliolab 警告小样本 inflated values 风险）；**60 日远低于 Sortino 36 个月机构标准（forex-basics/financefriend24 2026），估计误差大于机构级，需实盘校准触发条件判定是否上调窗口到 90/120 日**；MAR=Rf 选型已定（§3.2.2），target/0% 排除；EMA 列远期候选，需 walk-forward CV 验证半衰期无前视 | 首批策略 3-6 个月 PnL + PerformanceScore 月度变动 >0.3 频繁 / Sortino 月度排名波动大 / gap 监控频繁触发 / 发现"近强远弱"alpha 衰减特征则评估 EMA 升级 |
| ConfidenceSignal 四档阈值 60/80/95% | D1 ±20% 敏感性网格未跑（[11号](11_regime_backtest_validation_plan.md) §0.5.7） | D1 验证完成 |
| floor 5% / cap 40% 精确值 | 策略数未定（3 策略 vs 5 策略 cap 不同） | 首批策略数确定 |
| 稀有态机制在 4 态下的触发 | 当前 4 态全 >5%，机制不触发；待未来加态生效 | 基于证据加态（如层次 HMM） |
| **12 态→4 态退化映射精确查表** | §3.2.5 已定退化原则（按波动族/趋势方向合并 + 稀有态冻结），但精确状态 ID 映射表归 [10号](10_regime_detector_spec.md) regime 检测器文档定义，未校准 | [10号] regime 检测器 HMM 状态语义校准完成 |
| **外部信号交叉验证（5 档水温 + 板块轮动状态）是否启用** | §3.2.7 定位为远期辅助印证，HMM 与外部信号冲突时的 ConfidenceSignal 降档规则未定；数据管线（水温/板块状态）未接入 | 首批策略实盘 + 水温/板块状态数据管线接入；若纯 HMM Shrinkage 实盘 MaxDD 改善不达 C1 量级（7.36pp）则考虑启用 |
| **MPC 回撤通道增强（不换架构）** | §5.2 远期候选——在 ConfidenceSignal 叠加 realized drawdown 反馈（回撤 >阈值强制降档），无需完整 MPC 框架 | 纯 max(P) 四档实盘后若回撤控制不足（如某次回撤超 firm 层 drawdown protocol 阈值）则评估 |
| **最小 regime 持续期约束（吸收 JM 持续性思想，不换架构）** | §5.2 JM 远期候选启发——HMM 4 态无显式持续性约束，可加"最少 N 个交易日才允许状态切换"约束（离散版 jump penalty），归 [10号](10_regime_detector_spec.md) regime 检测器实现；arXiv:2603.04441 实证 regime identity preservation 是 drawdown 一阶决定因素 | HMM 实盘后若发现 regime 状态高频抖动导致 PerformanceScore/ConfidenceSignal 跳变频繁（如月内状态切换 >2 次）则评估 |
| **HMM→JM/SJM 替换（换检测器，远期）** | §5.2 远期候选——Statistical Jump Model（Shu-Yu-Mulvey 2024）显式 jump penalty 增强 regime 持续性，全面优于 HMM；中金 CICC 2026-06 A 股实证 MaxDD -7.07%→-3.23%。需重写 [10号](10_regime_detector_spec.md) regime 检测器 + C1 验证重跑 | 首批策略实盘后若 HMM 状态抖动问题持续（即便加了最小持续期约束）则评估升级到 JM |
| **Sticky HMM Dirichlet 先验（不换架构，最低侵入性，十六次审查新增）** | §5.2 第六条远期候选——Staures & Kabašinskas 2026-06（Mathematics 14(14):2463）Bayesian sticky 转移先验 `π_k ~ Dir(α+κ·e_k)`，κ 控制自转移持续性。实现侵入性极低（转移矩阵加 1 行先验），统计上最规范，归 [10号](10_regime_detector_spec.md) regime 检测器实现 | HMM 实盘后若发现状态高频抖动，Sticky HMM 是比 JM 更轻量的第一升级路径（不换检测器只加先验） |
| **5 态结构（4 稳态 + 1 过渡态，十六次审查新增）** | §5.2 A 股本土对标——中邮证券 2026-07 LSTM-GHMM 5 态（1 过渡态 + 4 稳态），状态切换经过渡态完成减少稳态间直接跳跃；2026 K 型分化下适应性偏弱。归 [10号](10_regime_detector_spec.md) regime 检测器实现 | HMM 实盘后若发现稳态间直接跳跃导致 PerformanceScore 跳变则评估加过渡态 |
| **3 态 vs 4 态 ablation（十六次审查新增）** | CSDN 2026-05 A 股 HMM 实战指出"A 股 60%+ 时间震荡，3 态是过拟合与表达力的折中（2 态太粗、4 态过拟合）"——直接质疑 4 态选择。[11号](11_regime_backtest_validation_plan.md) C1 验证 BIC 选优稳定收敛到 4 态，但未做 3 态样本外稳定性对比 | 首批策略 A 股数据上对比 3 态 vs 4 态样本外稳定性；若 3 态显著更稳则降级 |
| **Hybrid HMM Poisson jump-duration（换检测器，参数估计更简，十七次审查新增）** | §5.2 第十七条远期候选——Alswaidan & Varner 2026-03（arXiv:2603.10202, Cornell）Hybrid HMM：Laplace 分位数状态划分 + Poisson jump-duration 强制尾部态驻留 + **直接转移计数绕过 Baum-Welch EM**。KS/AD 通过率 >97%/91%（样本内），94%（样本外）。比 JM 实现更轻（无动态规划），比当前 HMM 参数估计更简（无 EM 迭代）。归 [10号](10_regime_detector_spec.md) regime 检测器实现 | HMM 实盘后若发现状态抖动 + Baum-Welch EM 重训练耗时成为双重瓶颈，则评估 Hybrid HMM Poisson（同时解决持续性和计算成本）；需先校验 Laplace 分位数与 A 股 4 态语义对应关系 |
| **3 态 sweet spot 佐证（十七次审查新增）** | kooexperience 2026-03 HMM 教程实证"stock returns naturally cluster into roughly three volatility regimes—two feels too coarse, four or more starts overfitting noise, three is the sweet spot"——与 CSDN 2026-05 A 股实证同向质疑 4 态。但 [11号] C1 BIC 选优稳定收敛到 4 态（非过拟合），且 4 态有语义基础（r1-r4），待 ablation 定论 | 同 3 态 vs 4 态 ablation 条件 |

### 6.1 过度工程审查：四档 Shrinkage 是否过细？

**结论：四档不过细，保留。**

| 对比 | 评估 |
|---|---|
| 2 档（如 0.5/1.0） | 太粗——<60% 和 60-95% 用同一档，丢失"中度确信"区分，过度保守 |
| 3 档（如 0.3/0.7/1.0） | 可行，但 80-95% 轻度收缩（0.85）和 >95% 满部署（1.0）的区分有意义（C1 验证中贡献了 MaxDD 改善） |
| **4 档（当前 0.3/0.6/0.85/1.0）** | **合理**——对应四个认知状态（不确定/有方向/较确信/高确信），有语义基础 |
| 5 档+ | 过细——max(P) 的估计误差本身就 >5%，分太细是伪精确 |

**关键论据**：
1. 四档只是 ConfidenceSignal 部分，真正的 Shrinkage = ConfidenceSignal × RiskSignal，RiskSignal 是 13 参数连续值（0.3-1.0）。整体 Shrinkage 是"离散×连续"=准连续，粒度足够细，**不需要在 ConfidenceSignal 上再加分档**
2. C1 已通过，证明四档在历史数据上有效（MaxDD 改善 7.36pp）
3. 四档阈值（60/80/95%）待 D1 敏感性网格校准——若 D1 显示某档边界是悬崖型（±20% 扰动效果骤变），则需调整；若稳健则确认

## 7. 待定问题（讨论要点）

> 以下来自 [00_index_trading_decision](00_index_trading_decision.md) §3 G15 讨论要点，已逐项对齐落入 §3 决策。

- [x] ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` → §3.1
- [x] ② Base_i 先验权重 → §3.2.1
- [x] ③ PerformanceScore 60 日 Sortino 映射 [0.5,1.5] → §3.2.2
- [x] ④ Shrinkage 置信度→风险节流映射（四档）→ §3.2.3
- [x] ⑤ floor≥5% / cap≤40% → §3.2.4
- [x] ⑥ 稀有态差异化收缩 → §3.2.5
- [x] ⑦ 第二阶段上线时机 → §3.2.6
- [x] ⑧ 外部信号交叉验证（5 档水温 + 板块轮动状态）→ §3.2.7（审查补充，非原始 G15 要点；远期辅助印证定位，不进 MVP 主链路）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G15
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2（分配公式 + RegimeScore 移除裁定）/ §4.2（第二阶段演进路径）
- [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md)（C1 验证，§0.5.4 四项全通过；§0.5.7 待完成项 D1）
- [10_regime_detector_spec](10_regime_detector_spec.md) §5（Shrinkage 产出方，§5.1 四档 + §5.2.2 二维公式 + §5.3.3 RiskSignal 聚合）
- [31_position_sizing](31_position_sizing.md)（G12，单策略仓位算法）
- [32_firm_risk_aggregator](32_firm_risk_aggregator.md)（G13，firm 层求和裁剪）
- [33_budget_change_handler](33_budget_change_handler.md)（G14，budget 下调三级升级落地）
- [battle_map_08_position_management](../battle_map/battle_map_08_position_management.md)（当前状态快照）
- [regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py)（MOD-PA-007 代码骨架）

### 8.1 2026 行业搜索参考

| 来源 | 与本备忘的关系 |
|---|---|
| Morwane/multi-strategy-alpha-book（[30号](30_multi_strategy_concurrency.md) §7.4 已引） | 核心实证：regime risk-throttle Sharpe 不变 + MaxDD 改善 3.9pp + Calmar +38%；regime alpha-timing Sharpe 降。直接支撑"Shrinkage 节流 vs RegimeScore 择时"裁定 |
| Invesco+清华《Dynamic global asset allocation》(2026-04) | Markov Regime-Switching 动态分配：higher returns, better risk-adjusted performance, shallower drawdowns。印证 regime-based 动态分配改善回撤 |
| I-am-Uchenna/regime-allocation-strategy (2026-01) | Regime Strategy Sharpe 1.220 / MaxDD -19.54% vs Equal Weight Sharpe 0.660 / MaxDD -23.45%——regime 分配显著优于等权（Sharpe 近翻倍，MaxDD 改善 4pp） |
| arxiv 2410.14841《Dynamic Factor Allocation Leveraging Regime-Switching Signals》 | regime analysis ≠ factor timing（不预测何时切换）；Black-Litterman + regime 信号 IR 0.05→0.4。支撑"regime 用于风险节流/分配调整，不用于择时" |
| misango《Regime-Based Portfolio Strategies》(2026-03) | 60/40 在交易成本后优于复杂 ML 方案；simple often outperforms complex。警示过度复杂化，支撑"三因子乘法"而非 RL/优化器 |
| preprints.org《When to Route? Regime-Adaptive Meta-Policies》(2026-05) | 层次化决策系统：direct optimization safer in low-signal。印证"低信号时直接部署（Shrinkage 节流）比试图路由（alpha 择时）更安全" |
| BestFolio《Walk-Forward Portfolios》(2026-04) | walk-forward max Sharpe 优化器：36 个月 lookback + **cap 40%** + 月频重平衡。cap 40% 与我们 CAP=0.40 完全一致（§3.2.4 印证）；36 个月 vs 我们 60 日的窗口差异在 §3.2.2 讨论（他们需长窗口稳协方差，我们用 Sortino 不需要） |
| 1uptick.com《Regime-Adaptive Risk Framework》(2026-06) | 机构跨资产方案：regime transition 时 max(P)<**60%** 减仓 30-50% + 60-120 天校准窗口。60% 阈值与我们 ConfidenceSignal 四档完全一致（§3.2.3 印证）；60-120 天校准窗口与我们 regime 检测器训练窗口一致 |
| loic-mmt/quant-portfolio (2026-08-07) | regime-aware portfolio，哲学"不预测未来，只检测状态+调整暴露"——与我们"regime 只做风险节流不做择时"完全一致。8 月最新同类项目，印证架构方向 |
| donarduka/regime-switching-portfolio (2026) | regime 动态分配实证：Sharpe +0.026、MaxDD 改善 5.5pp。与我们 C1 验证（MaxDD 改善 7.36pp）同量级，独立印证 regime 节流效果 |
| stockalpha.ai《AI for Portfolio Optimization》(2026-01) | 总结：improving covariance/return estimates yields outsized benefits vs tuning optimizer knobs。但我们选择不估计协方差（A 模型哲学），用 PerformanceScore 后验代替——是这条建议的轻量替代路径 |
| arxiv MM-ARC 2509.05080v3 (2026-07-27) | Multimodal Adaptive Routing of Capital + RABO 鲁棒性审计。比三因子乘法复杂得多（多模态+贝叶斯优化），但核心"regime-conditioned strategy pools"与我们 regime→Shrinkage 一致。misango 2026-03 警示简单方案更优，我们不选 RABO |
| arxiv 2603.04441《Explainable Regime-Aware Investing》(2026-02) | Wasserstein HMM：严格因果滚动 Gaussian HMM + 模板身份追踪。核心论断"**regime inference stability—particularly identity preservation—is a first-order determinant of portfolio drawdown**"——印证我们用 Shrinkage（regime prob 直接缩放暴露，不做不稳定 re-routing）的正确性，Sharpe 2.18 vs SPX 1.18。已记为 10 号 Phase 3 增强候选（身份保持机制） |
| arxiv 2510.14986《RegimeFolio》(2026-10) | regime-aware + sector-specialized MVO，Sharpe 1.17、MaxDD 改善 12%。用 Ledoit-Wolf shrinkage 协方差 + regime-conditioned MVO——我们 A 模型明确拒绝 MVO（协方差估计问题，[30号](30_multi_strategy_concurrency.md) §3.1），但"regime 分割+分别建模"思想与 Shrinkage 节流一致 |
| advisingalpha.com《Sharpe vs Sortino》(2026-05) | "Sortino is a better measure of risk-adjusted return for most individual investors because it only penalizes downside variability"。支撑 §3.2.2 PerformanceScore 从 Sharpe 切换到 Sortino |
| equiscale.ai《Sharpe vs Sortino》(2026) | "Use Sortino for high-volatility strategies or growth stocks—assets have massive good volatility that would unfairly lower a Sharpe score"。A 股打板涨停板 = massive good volatility，直接支撑 Sortino 选型 |
| portfoliogenius.ai《Sortino Ratio》(2026) | Sortino 公式 + 解读区间（<0 失败 / 0-0.5 低于平均 / 0.5-1.0 适中 / 1.0-2.0 很好 / >2.0 卓越）。支撑 §3.2.2 映射区间 [0.5,1.5] 的语义（0.5=适中偏弱砍半 / 1.0=中性 / 1.5=很好接近卓越） |
| fastercapital.com《Sortino Ratio》(2026-05) | "Traditional risk-adjusted metrics treat upside/downside symmetrically. However, investors often care more about avoiding losses than maximizing gains"。支撑 PerformanceScore 的 downside-focus 与风险节流目的对齐 |
| moneylume.com《Sharpe Ratio in 2026》(2026) | "Not ideal for: options, leveraged ETFs, or crypto—use Sortino ratio instead"。A 股打板/事件驱动的非对称收益分布类似 options 的 payoff 结构，适用 Sortino |
| recessionistpro.com《Capital Preservation》(2026-02) | "Define your drawdown limit first—5%/10%/15% determines everything"。支撑 §3.2.2 熊市最低总暴露设计——先定 drawdown 上限再定 exposure floor。A 股 cash=防御资产，9% floor 对应"极端防御"档位 |
| protraderdaily.com《Recession Portfolio 2026》(2026-08-09) | 60% bonds/25% dividend/15% alts 组合 MaxDD -8.2% vs growth -23.7%。多资产防御组合对照——A 股单市场无此 sleeve，用高 cash（低 global_shrinkage）等效防御 |
| ecassets.com《Sortino Ratio》(2026-05-28) | **关键警示**："downside sample is small → statistically unreliable" + "inflated values for strategies with few downside observations"。直接支撑 §3.2.2 Sortino 样本量门槛（downside<15 强制中性）——60 日窗口 downside 样本 ~24 日接近风险区，需防护 |
| foliolab.ai《Sortino Ratio》(2026) | **关键警示**："Requires more data than Sharpe for stable estimates, since only below-target observations contribute to denominator" + "Can produce very high values for strategies with few downside observations, potentially overstating risk-adjusted performance"。支撑 §3.2.2 inflated values 防护三件套（样本门槛 + cap 兜底 + gap 监控） |
| fxroboteasy.com《Sortino Ratio》(2026-08-04) | "When Sortino is preferred: trend-followers, breakout systems, options-style strategies, and any system that targets large wins relative to small losses"。A 股打板=breakout system，直接支撑 Sortino 选型；实用区间 1.0-1.5 good / >2.5 excellent 与我们 [0.5,1.5] 映射语义一致 |
| Oliveira et al.《Tactical asset allocation with macroeconomic regime detection》(Quantitative Finance 2026-06-11, Oxford-Man Institute) | FRED-MD 宏观数据集 + modified k-means regime 检测 + 预测 regime 分布 + 仓位映射。优于 equal-weight/buy-and-hold/random regime。与本项目 HMM 路径不同（k-means vs HMM），但"regime 预测分布→仓位映射"思想与 Shrinkage 节流一致；记为 10 号 regime 检测器前沿演进候选（宏观特征补充） |
| Pei et al.《Market Regime Council for Dynamic Credit Assignment》(arXiv:2605.24490, 2026-05-23) | 多 agent LLM 决策系统用 **Shapley credits** 在线加权 + **贝叶斯自适应混合**稳定早期冷启动 + regime-dependent multipliers。Sharpe 1.51 / CR 440.1%。与 34号 的关联：贝叶斯冷启动（`w_prior×1.0 + w_data×Sortino`，权重随样本量渐变）比我们 30 日阈值硬切换更平滑，记为 §3.2.2 冷启动远期候选（MVP 不采纳，复杂度 vs 收益不划算）；Shapley credits 需 O(2^N) coalition 评估，N=5 策略下过重，不采纳（我们的 Base×Sortino×Shrinkage 乘法是 O(N) 替代） |
| forex-basics.com《Sortino Ratio Basics》(2026-05-17, verified 2026-05-28) | **关键机构标准**："The institutional standard is a minimum of thirty-six months" + "With only twelve months of data it is easy to land in a situation where the strategy enjoyed a lucky run without deeper drawdowns, and the downside deviation came out artificially low"。直接支撑 §3.2.2 重大修正——Sortino 自身有 36 个月机构标准，我们 60 日（~3 个月）远低于标准，是已知妥协，需防护四件套 + 实盘校准触发条件 |
| financefriend24.com《Sortino Ratio Explained》(2026) | **关键样本量标准**："With fewer than 36 monthly observations (3 years), the result is highly sensitive to individual bad months. With 60+ monthly observations (5 years), the estimate becomes more reliable" + "Short-period Sortino Ratios — particularly from strategies that rarely lose money — should be treated with caution"。支撑 §3.2.2 60 日 vs 36 个月机构标准的差距分析 + 实盘校准触发条件设计 |
| superglobalcalculator.com《Sortino Ratio Calculator》(2026) | "Need ≥ 30 periods for stability" + "Few data points: Need ≥ 30 periods for stability"。支撑 §3.2.2 downside 样本量门槛（我们 60 日 downside ~24 日接近 30 阈值，需防护） |
| getzenquery.com《Sortino Ratio Calculator》(2026) | "For more reliable results, consider using 20-30+ return periods" + "Limited data (16 periods). For more reliable results, consider using 20-30+ return periods"。支撑 §3.2.2 样本量门槛设计 |
| Alkhudaydi & Althobaity《GATE-WPCA-PI》(AIMS Mathematics 2026, 11(2):3647-3702, doi:10.3934/math.2026149) | Graph-aware adaptive tracking-error optimization：mean-variance surrogate + **entropy floor**（防集中）+ **sleeve caps**（限制单资产）+ PI 控制器控制 tracking error 在可行带内。与 34号 的关联：entropy floor/sleeve caps 与我们 floor 5%/cap 40% 同构（§3.2.4 学术级印证）；PI 控制器是 PerformanceScore 调整的进阶版（我们用滚动 Sortino，他们用 PI 控制器 steering TE），记为远期候选（MVP 不采纳，PI 控制器增加复杂度） |
| Lkhagvasuren et al.《Convex and sphere packing approaches to portfolio optimization》(JIMO 2026, 22(4):1672-1692, doi:10.3934/jimo.2026062) | feasibility restoration——当约束无解时找"最近可行解"（convex QP 计算 closest allocation to reference portfolio preserving quadratic structure）。直接支撑 §3.2.4 floor/cap 无解兜底设计——N=2 时 floor+cap 可能数学无解，用"优先保 floor 降 cap"的最近可行解策略 |
| AI Finance Labs / Lopez-Lira《Claude AI-Managed Portfolio》(2026-03 至 2026-08, forexclub 报道) | Claude AI 管理 $50K 组合，5 个月回报 19.04% vs S&P 12.24%；Claude 最大持仓 = iShares 0-3 月国债 ETF（最防御），策略倾向防御性平衡基金管理。与 34号 的关联：**AI 无人值守系统天然倾向防御**——印证我们"风险优先 + cash 防御 + 低 global_shrinkage floor 9%"设计的正确性。无人值守 AI 无"追涨"情绪，低暴露高 cash 是自然选择，与机构 GPIF 机械再平衡异曲同工 |
| sooktrading/whalesbook《KOSPI Collapse 2026》(2026-08-03/05) | 2026-07 KOSPI 6 周跌 40%、蒸发 $2 万亿、多次熔断；杠杆 ETF + 集中三星/SK海力士（>50% 指数权重）= 多米诺崩塌；32 万账户强平。政府措施：暂停新杠杆 ETF、三倍保证金。与 34号 的关联：印证 cap 40% 防集中 + 禁杠杆 + circuit breaker 的必要性——A 股虽无杠杆 ETF，但打板策略天然高集中，cap 40% 是防"KOSPI 式集中崩塌"的硬约束 |
| Yang et al.《RMATS: Recursive Multi-Agent Trading System》(arXiv:2605.25311, 2026-05-25, APAM 2026) | 4 specialized agents（Sentiment/Report/Analysis/Risk）+ recursive Manager + 收敛保证。MaxDD 9.62%（vs MVO 15.49%）。**Risk Agent 独立于策略 agent**（CVaR + geopolitical stress + adaptive circuit breaker）。与 34号 的关联：印证 regime 层应独立于策略层解耦（我们的 Shrinkage 是独立风险节流层），但**不采纳多 agent 递归架构**（个人项目过度工程审查，见 §4.4/§3.2.7）；RMATS 的 adaptive circuit breaker 与我们 ConfidenceSignal 四档 + §3.2.7 外部信号冲突降档思想一致 |
| [YoungCan-Wang/Wyckoff-Analysis](https://github.com/YoungCan-Wang/Wyckoff-Analysis) v2.1.x（2026-04 实证） | A 股大盘水温 5 档仓位控制：NEUTRAL 100% / RISK_ON 50% / PANIC_REPAIR 50% / RISK_OFF 30% / CRASH 0%。实测：NEUTRAL +1.17%（唯一正收益）/ RISK_ON −1.54% / CRASH −3.2%。核心结论"选股选得好不如市场选得对，水温仓控是性价比最高的风控手段"。直接支撑 §3.2.7 5 档水温作为 HMM 4 态的外部交叉验证信号——水温与 Shrinkage 风险节流哲学一致 |
| [YoungCan-Wang/WyckoffTradingAgent](https://github.com/YoungCan-Wang/WyckoffTradingAgent) Wiki《04_Finance_Sector_Rotation_Regime》（2026-04 实证） | 板块轮动状态 5 分类：CONSENSUS_CLIMAX / DISAGREEMENT_PULLBACK / HEALTHY_MAINLINE / DISTRIBUTION_RISK / NEUTRAL_MIXED + watch_score 加减分机制。实测：共识高潮后 3 日下跌 >2% 概率 29.8%。支撑 §3.2.7 板块轮动状态作为 regime 检测的辅助信号——DISTRIBUTION_RISK 是"最危险状态"，与 HMM r4（熊市）形成交叉印证 |
| pooyagolchian《Portfolio Risk Management: VaR, CVaR, and Kelly Criterion for 2026》(2026-04-13) | Fractional Kelly 实证（2026 真实数据）：Full Kelly CAGR 18.2%/MaxDD −62% / Half Kelly 14.1%/−38% / **Quarter Kelly 10.8%/−22%**（85% 增长 / 35% 回撤）/ Risk Parity 9.2%/−18%。直接支撑 §3.2.3 Shrinkage 节流与 Quarter Kelly 同构——"适度收缩风险预算 → 以小得多的回撤代价获大部分增长"是 §2.2 regime 风险节流裁定的实证依据 |
| Nystrup/Boyd/Lindström/Madsen《Multi-period portfolio selection with drawdown control》(Annals of Operations Research 282(2):1-27, 2019；2026 多篇引用复现) | MPC（Model Predictive Control）动态优化 + 多变量 HMM 多期均值/协方差预测 + **根据已实现回撤调整风险厌恶系数**。实证：以小或无 mean-variance 效率牺牲控制回撤。记为 §5.2 远期候选——完整 MPC 框架需协方差估计（A 股情绪周期相关性飙升问题未解）+ 凸优化求解器，个人项目过度工程；但"realized drawdown → γ 动态"思想可先吸收为 ConfidenceSignal 的回撤通道增强（§3.2.7/§6 待裁定），不换架构 |
| Grube Martín-Lunas et al.《From Regime Detection to Decision Rules: A Data-Driven Macro-Financial CVaR Framework》(MDPI Economies 14(7):268, 2026-07-09) | 4-state Gaussian HMM + CVaR 优化 + 严格 walk-forward（expanding window，4 周重估）。**关键发现**：naive regime-conditional CVaR 年换手 ~226%（侵蚀净收益至基准之下），regime-constrained weight bands 才是关键（net Sharpe within 0.009 of static benchmark at ~29% turnover）。结论"**bottleneck is not regime detection but transparent, stable, cost-aware decision-rule design**"。支撑我们的方向：Shrinkage 只缩放总暴露（低换手）而非 regime-conditional MVO（高换手），印证 §4.2 MVO 拒绝；也印证 [33号](33_budget_change_handler.md) §6 budget 防抖/turnover 控制的必要性 |
| Verma/Putri/Lesupi《Regime-Based Portfolio Allocation Using HMM and RL》(arXiv:2605.27848, 2026-05-27) | 3-state Gaussian HMM（BIC 选优）+ RL 动态分配 SPY/TLT/GLD。RL policy 最高 Sharpe + 显著低 drawdown，fully interpretable。**one-day execution lag 避免 look-ahead bias**。支撑：execution lag 与我们 T+1 结算窗口设计一致（[33号](33_budget_change_handler.md) §3.2.4）；3-state 与我们 4-state 同量级，HMM+RL 是远期候选但 MVP 不采纳 RL（黑箱+训练成本，见 §4.4） |
| youcanbuildthings.com《Multi Strategy Trading Bot Python: Risk Parity Allocator》(2026-05-06) | risk-parity capital sizing（inverse-vol）+ **90-day correlation drop rule**（两策略 90 日滚动相关 >0.70 持续 30 天 → 剔除其一）+ per-strategy drawdown circuit breaker（15% half / 25% zero）+ intent netting before broker。与我们多策略架构高度相似：inverse-vol 是 risk parity 简化版（我们用 Base 先验 + PerformanceScore 后验替代）；correlation drop rule 是 [30号](30_multi_strategy_concurrency.md) 策略独立性可借鉴的量化判定；per-strategy circuit breaker 印证 [33号](33_budget_change_handler.md) per-strategy TierState 设计 |
| Shu/Yu/Mulvey《Downside risk reduction using regime-switching signals: a statistical jump model approach》(Journal of Asset Management 25(5):493-507, 2024；arXiv:2402.05272) | **Statistical Jump Model（JM）原始论文**——显式 jump penalty λ 增强 regime 持续性，抑制 HMM 高频抖动；特征集 DD_10+Sortino_20+Sortino_60（**与我们 PerformanceScore Sortino 同源**）；US/Germany/Japan 1990-2023 含交易成本+执行延迟，JM-guided 在波动率/MaxDD/Sharpe 全面优于 HMM 与 buy-and-hold。直接支撑 §5.2 JM 远期候选——JM 是 HMM 的 regime 持续性增强替代，Sortino 特征双重用途（regime 检测 + PerformanceScore）印证我们 60 日 Sortino 选择 |
| 中金公司《量化配置模型系列（2）：基于统计跳跃的系统性风险预警模型》(2026-06-24, finance.sina.com.cn 报道) | **JM 应用于 A 股（股-债-金八资产）的关键实证**——借鉴 Shu et al. (2024) JM，DD_10+Sortino_20+Sortino_60 三维特征；跳跃惩罚 λ：权益/黄金=50，债券=25；强制避险持续≥60 交易日；增强信号（须债券同步看空才确认系统性风险）。实证：三资产风险平价 MaxDD -7.07%→-3.23%、卡玛比率 0.77→1.59；八资产均值-方差 MaxDD -35.18%→-21.96%。**关键启示**：① JM 在中国市场有效（非仅美股）；② 60 交易日持续期与我们 Sortino 60 日窗口巧合一致；③ "多资产确认+强制持续期"降低 false positive——我们单市场用 §3.2.7 外部信号交叉验证起类似多源确认作用。支撑 §5.2 JM 远期候选 + §3.2.2 60 日窗口选择 |
| Cortese/Kolm/Lindström《Generalized information criteria for high-dimensional sparse statistical jump models》(AStA Advances in Statistical Analysis 110(2):289-317, 2026-06, doi:10.1007/s10182-026-00554-9) | **JM 超参数选择的学术标准**——将广义信息准则框架扩展到高维稀疏 JM，推导模型拟合度与复杂度表达式构造信息准则用于 jump penalty λ 选优；模拟研究显示高概率选中正确超参数；MSCI 发达/新兴市场实证 3 态模型最优。支撑 §5.2 JM 远期候选——若升级到 JM，λ 选优有学术级信息准则（非启发式），且 3 态与我们 4 态（BIC 选优）同量级，JM 不强制减少状态数 |
| Li/Chen/Tao/Ji《Regime-Switching Asset Allocation Using a Framework Combining a Jump Model and Model Predictive Control》(Mathematics 13(17):2837, 2025, doi:10.3390/math13172837) | **JM-MPC 混合框架**——JM 识别 regime + 滚动预测机制估计多期时变收益/协方差 + MPC 优化资产配置。实证：JM-MPC 全面优于等权组合，高波动期显著降低回撤，风险调整收益更优。支撑 §5.2 远期演进路径排序③——JM 替换 HMM（持续性更强）+ MPC 多期优化（回撤动态控制）是"换检测器+换优化器"的双重远期升级路径；MVP 不采纳（需协方差估计问题先解决） |
| dataloopr《Regime-Aware Portfolio Strategies for Changing Market Conditions》(2026-03-09) | **集成 regime-aware 框架**——GARCH(1,1) 波动聚类 + Student-t 肥尾 + Markov regime switching + regime-switching Monte Carlo + 动态波动率目标仓位。与我们架构对照：GARCH+Student-t 是 RiskSignal 13 参数中 realized_vol 的进阶建模（我们用分位数，他们用 GARCH 条件方差）；regime-switching MC 是 §5.2 MPC 多期预测的简化版（MC 采样 vs 凸优化）；动态波动率目标与我们 Shrinkage 节流同构。记为 RiskSignal 波动建模的远期增强候选（GARCH 替代分位数） |
| Soloviov《Asymmetry, Fat Tails, and the Cost of the Wrong Innovation: A Controlled GARCH Tail-Risk Study》(2026-07, marketmaker.cc) | **GARCH 尾部风险的受控实验**——GJR-GARCH(1,1) + Student-t(ν=5) innovations 的已知 ground truth DGP，拟合 5 族竞争模型 120 seeds×4 样本量。**关键发现**：① 切换 innovation 到 Student-t 修复几乎所有 VaR 覆盖误差（99% VaR 违规率 1.58%→1.03%，ES bias -23.0%→+0.9%）；② 尾形效应（Normal→t）在 ES bias 上**比不对称效应（GARCH→GJR）大一个数量级**；③ 近对称近高斯控制 DGP 下额外结构不再获益（BIC 仅 1.7% 选不对称重尾模型）。支撑：若 RiskSignal 升级到 GARCH 建模，**Student-t innovations 是必选**（Normal GARCH 在尾部乐观危险）；A 股收益肥尾显著，t innovations 的 ν 估计是关键参数 |
| Park/Kim《Deep Generative AI for Portfolio Management》(Columbia University Engineering Poster, 2025) | **深度生成模型做 CVaR 优化**——Student-t Glow（Normalizing Flow）+ Flow Matching + Score-Based Model 学习灵活收益分布，替代高斯假设做 CVaR 组合优化。Gaussian 分布无法捕捉肥尾和极端风险，深度生成模型更好建模尾部行为。支撑：远期（Phase 5+）若 CVaR 优化需要更精确尾部建模，深度生成模型是前沿路径；MVP 不采纳（神经网络训练成本+黑箱，与 A 模型简单哲学矛盾） |
| 华安证券《基于状态切换信号的动态因子配置》(2025-10-21, finance.sina.com.cn) | **稀疏跳跃模型（SJM）+ Black-Litterman 因子配置**——SJM（Nystrup 2021）在 JM 基础上加特征加权挑选，识别单因子牛熊态，整合到 BL 模型动态调整 7 指数（市场+6 风格因子）配置。实证：IR 0.05→0.4（8 倍提升）+ Sharpe/MaxDD 绝对改善。支撑：① SJM 是 JM 的高维扩展（特征选择），若我们未来加宏观特征做 regime 检测可参考；② BL+regime 信号 IR 0.4 与 arxiv 2410.14841 一致（§4.5 已引），双重印证 regime 信号对 BL 增益量级稳定；③ 我们拒绝 BL（需协方差+观点矩阵，§4.5），但 SJM 的特征选择思想可吸收到 RiskSignal 13 参数权重优化 |
| 汇安基金柳预才《大小盘动态量化新框架》(2026-08-07, cnfol.com 报道) | **A 股本土双层动态量化实证**——顶层市值风格判别模型（整合宏观流动性/市场估值/资金动量/交易拥挤度等 **20+ 量化因子**，每日更新风格倾向结论）+ 底层双独立选股池（大盘：中证800 盈利质量/持续分红/价值因子；小盘：中证1000 景气反转/量价波动/alpha 因子）+ **切换阈值过滤日间噪音**避免频繁调仓 + **底仓对冲误判风险**。与 34号 的关联：① 顶层风格判别 ≈ 我们的 regime 检测器 + RegimeMetaAllocator Shrinkage（"现在该多谨慎"），但汇安做的是**大小盘 alpha 择时**（"现在偏向谁"），我们明确拒绝 RegimeScore 择时（§4.1，Morwane 实证降 Sharpe）；② 双独立选股池 ≈ 我们的 StrategyBook 独立 sleeve（[30号](30_multi_strategy_concurrency.md) Model A）；③ **切换阈值过滤噪音**与我们的 ConfidenceSignal 四档（max(P)<60% 强收缩）同构——都是"不确定时别赌方向"；④ **底仓对冲误判**与我们的 floor≥5%（§3.2.4 防饿死）同构——都防"判错时全盘皆输"。**关键差异**：汇安做 alpha 择时（风格轮动），我们做风险节流（Shrinkage）——A 股 2026 上半年量化超额从 14.17% 降至 3.11%（[新浪财经 2026-07-11](https://finance.sina.com.cn/jjxw/2026-07-11/doc-inihmkxc5002361.shtml)），K 型行情+因子失效+策略同质化使 alpha 择时难度飙升，印证我们"风险节流不做 alpha 择时"裁定的正确性 |
| firestrand/marketregimeml《Model Comparison》(2025-09, GitHub) | **regime 检测模型对比基准**（100% 真实市场数据）——快速 SVM 集成（RBF+Linear）RQI 83.6-86.9 vs HMM 67.8-76.6 vs LSTM 49.1-64.9（最差，不推荐）。**10 个优化特征胜过 35+ 特征**（特征过多反而过拟合），n_regimes>3 过拟合。与 34号 的关联：① HMM 非最优但 C1 已证明 HMM 4 态 Shrinkage 有效（MaxDD 改善 7.36pp），MVP 不换；② SVM 集成优于 HMM 的基准为 §5.2 JM 远期候选 / §6 HMM→JM 替换提供额外证据——若 HMM 实盘后发现状态抖动/检测精度不足，SVM 集成是比 JM 更轻量的替代路径（无需 jump penalty 调参，仅需 RBF+Linear kernel 组合）；③ **10 特征原则**印证我们 6 因子 HMM 输入的精简设计正确——特征过多过拟合 |
| quantt.co.uk《Sortino Ratio Explained》(2026-04) | **Sortino ≈ 1.3-1.5 × Sharpe 正常范围基准** + **下行偏差分母用总样本量 N（非下行观测数）的独立验证**——文章 Step 5 明确写道"divide by the total number of observations (N), not just the number of below-target ones"，并标注"This is a common source of confusion"。若 Sortino 远高于 Sharpe 说明策略不对称波动（小亏损+大盈利）；若接近说明上下行对称。系统性交易策略优先 Sortino（刻意追求上行波动，Sharpe 会惩罚）。与 34号 的关联：① 直接支撑 §3.2.2 gap 监控阈值校准——`_compute_sortino_and_sharpe()` 中 gap > 1.6（=1.3-1.5 正常上限的 ~1.1 倍）触发"疑似 inflated"警告；② **独立验证 v2.2.0 施工要点 #13 的 Sortino 分母修复**（n_downside-1→n-1）——quantt.co.uk 2026-04 明确指出分母用 N（总样本量）是正确做法，n_downside 是"common source of confusion"的常见错误。MAR 选择影响巨大（常用无风险利率，但更高 MAR 如 5% 标准更严格）——印证 §3.2.2 MAR=Rf 决策的合理性 |
| CFA Institute《The Sortino Ratio: Is Downside Risk the Only Risk that Matters?》(Deborah Kidd, CFA, rpc.cfainstitute.org) | **Sortino 比率的权威原始定义来源**——CFA Institute 官方出版物，明确 downside deviation 的分母争议："the proper calculation of downside deviation" 存在多种变体，"which one an investor uses matters a great deal"。引用 Sortino and Forsey (1996) 建议"fitting a continuous curve to a bootstrapped distribution"——即 bootstrap 方法处理 Sortino 的不确定性，与 v2.2.0 施工要点 #14 的 BCa bootstrap 远期候选同源。与 34号 的关联：① 作为 Sortino 下行偏差分母共识（v2.2.0 施工要点 #13 引用的"CFA Institute 2026 共识"）的权威出处——CFA Institute 确认分母变体是"easy to understand but also easy to miscalculate"的常见陷阱；② Sortino-Forsey 1996 bootstrap 引用为 BCa bootstrap 远期候选（施工要点 #14）提供原始理论溯源——CFA Institute 早在 2012 文件中就引用了 Sortino-Forsey 的 bootstrap 方法，我们 v2.2.0 的 BCa bootstrap 升级路径（点估计→5% 下分位保守估计）是对这一原始建议的现代化实现 |
| RPubs《Market Regime Detection using HMM Walk-Forward》(2026-04) | **HMM walk-forward 三策略对比实证**——① Strategy A（expanding window + hard switch）**失败**：out-of-sample 仅 ~20% 时间持仓（crisis-scarred 训练数据导致 HMM 过度保守）；② Strategy B（rolling 3yr + hard switch）纠正 regime 持续性不匹配；③ **Strategy C（soft allocation，概率加权敞口）最优**：用后验概率作为连续仓位尺寸，消除 abrupt switches，MaxDD -30.5%（vs hard expanding -52.4%）。与 34号 的关联：① **直接验证 ConfidenceSignal 四档软映射设计**——我们用 max(P) 映射到 4 档 Shrinkage（非 binary bull/bear 开关）正是 Strategy C 的"soft allocation"思路，rpubs 实证 MaxDD 改善 22pp（-52.4%→-30.5%）为软映射优于硬切换提供量化证据；② **expanding window 失败警示**——HMM 训练窗口应用 rolling 而非 expanding（crisis-scarred 数据导致过度保守），此为 [10号](10_regime_detector_spec.md) HMM refit 策略的设计约束，34号 消费 10号 输出的 regime_probs 须确认 10号 用 rolling refit |
| GARCH-ARJI《Jump Persistence in Financial Markets》(International Journal of Forecasting 42(3):833-852, 2026) | **跳跃强度的时变持续性**——GARCH-ARJI 模型实证跳跃强度具有持续性，时变跳跃强度对尾部风险预测至关重要。短期偏度急剧下降、超额峰度上升（初始跳跃强度高时）；长期时间分散化效应使偏度和峰度缓慢趋零。S&P 500/FTSE 100/DAX 30 样本外回测确认。与 34号 的关联：① RiskSignal 13 参数中 realized_vol 若升级到 GARCH 建模（dataloaderoop 远期候选），**须纳入 ARJI 跳跃强度**（常数跳跃强度的 GARCH 低估尾部风险）；② A 股牛熊转换常伴随跳跃（政策突变/黑天鹅），时变跳跃强度比 HMM 转移概率更能捕捉"跳跃聚集"现象——为 §5.2 JM 远期候选提供跳跃持续性理论支撑 |
| M-ROLL《AI-Markov Hybrid Portfolio Framework》(IJFMR 2026-03/04) | **离散时间 Markov 链 + 粒子群优化（PSO）自适应权重**——PSO 最小化经验与目标分布散度（评估 10 种散度指标：KL/Jensen-Shannon/Hellinger/Wasserstein 等）。5 个美国行业测试：Sharpe 1.87（较等权提升 260%），MaxDD 44.2%→28.1%。卡方检验验证 Markov 平稳性和无记忆性。与 34号 的关联：M-ROLL 是 HMM→JM 之外的**第三条远期路径**——不换检测器（仍用 Markov），但换优化器（PSO 替代我们的三因子乘法）。MVP 不采纳（PSO 增加复杂度且三因子乘法 C1 已验证有效），但若首批策略实盘后发现三因子乘法分配效果不足（如 PerformanceScore 对 alpha 衰减响应太慢），M-ROLL 的散度最小化是替代优化路径 |
| arXiv:2507.19824《Regime-Switching Induced Stock Price Jumps》(2025-07) | **制度切换时股价本身发生跳跃**——不仅市场参数（利率/升值率/波动率/跳跃强度）依赖制度，还允许制度切换时股价本身发生跳跃（除常规微观跳跃外）。动机：牛市转熊市时股价常急剧下跌，反之亦然。用 complete-of-squares 技术推导最优组合和有效前沿。与 34号 的关联：A 股牛熊转换常伴随跳跃（如 2024-09 政策底单日 +8%、2026-07 KOSPI 6 周跌 40%），**制度切换诱导的股价跳跃**意味着 ConfidenceSignal 四档映射（max(P) 映射）在 regime 切换瞬间可能来不及反应——Shrinkage 日频更新 + D-SIGNAL-68 overlay 盘中突变重算是必要的，印证 §3.3 更新频率设计的合理性 |
| Acanto 8A《Momentum + Risk Parity White Paper》(2026-02) | **21 资产类别 + 月度再平衡 + 双动量 + 风险平价加权**——2008-2026 回测（含 GFC/COVID/2022 通胀冲击）：Sharpe 1.19、**Sortino 1.21**、最大回撤仅 -7.6%。4228 参数组合网格搜索确认当前配置位于 99 分位。**关键启示**：2022 年 60/40 组合失效（股债同跌）证明静态相关性假设危险，自适应配置必要。与 34号 的关联：① Sortino 1.21 是动量+风险平价组合的**机构级基准**，与我们 PerformanceScore 用 Sortino 做后验分配的目标一致——首批策略实盘后 Sortino 达 1.0-1.5 区间是合理预期；② -7.6% MaxDD 是多资产风险平价的回撤基准，A 股单市场 + Shrinkage 节流的目标 MaxDD 改善量级（C1 已验证 22.2%→14.9%）与此同向；③ **双动量框架**（绝对动量+相对动量）与我们的 Base 先验 + PerformanceScore 后验同构——先验锚 + 后验调整 |
| arXiv:2606.09478《Volatility Forecasting and Return Prediction under Market Regimes: Evidence from High-Frequency Chinese Equity Data》(2026-06) | **A 股高频 regime-aware 波动率预测实证**——两阶段框架：① regime-augmented HARQ（heterogeneous autoregressive realized volatility with quarticity）+ Markov-switching GJR-GARCH 过滤捕捉长记忆/不对称/结构性 regime；② regime 指标 + 波动率预测 + 收益预测因子输入 XGBoost 严格 walk-forward out-of-sample。**核心发现**：regime-aware 波动率预测持续优于 baseline HARQ 模型。与 34号 的关联：① **A 股本土实证**（非美股泛化）——regime-augmented 波动率建模在 A 股高频数据上有效，支撑 RiskSignal 13 参数中 realized_vol 若升级到 GARCH 建模（§5.2 远期候选 dataloopr GARCH+Student-t）的 A 股适用性；② Markov-switching GJR-GARCH 是我们 HMM 4 态 + GARCH 条件方差的融合路径——当前 RiskSignal 用 realized_vol 分位数（简单），远期可升级到 regime-augmented GARCH（捕捉波动聚类+不对称+regime 切换）；③ 严格 walk-forward 与我们 C1 验证的 walk-forward 协议一致。MVP 不换（C1 已验证分位数有效），记为 RiskSignal 波动建模远期候选的 A 股实证支撑 |
| arXiv:2604.09060《Taming the Black Swan: A Momentum-Gated Hierarchical Optimisation Framework for Asymmetric Alpha Generation》(2026-04, Chakraborty & Singh) | **AEGIS 框架：动量门控 + 最小最大化相关 + SLSQP 直接优化 Sortino**——波动率调整动量过滤器识别趋势强度 + minimax 相关算法强制结构分散 + 序贯最小二乘规划（SLSQP）优化资本分配以最大化 Sortino ratio。20 年 walk-forward 回测（2006-2025 含 GFC）：熊市降低崩盘强度（解耦相关风险），牛市保留不对称上行参与。与 34号 的关联：① **直接优化 Sortino** 与我们 PerformanceScore 用 Sortino 做后验映射目标一致——AEGIS 用凸优化器直接最大化 Sortino，我们用 Sortino 线性映射 [0.5,1.5] + floor/cap 裁剪（更简单，A 模型哲学）；② minimax 相关强制分散与我们的 floor 5%/cap 40% 防集中同构（但 AEGIS 用相关矩阵，我们用简单 cap）；③ MVP 不采纳 SLSQP 优化器（§4.2 已拒绝 MVO，SLSQP 是 MVO 的变体同样需协方差估计），但"直接优化 Sortino"思想印证我们 PerformanceScore 选 Sortino 的正确性——如果 Sortino 不是好的优化目标，AEGIS 不会选它做目标函数。记为远期候选：若三因子乘法分配效果不足，SLSQP Sortino 优化是替代路径（需解决协方差估计问题） |
| arXiv:2603.10202《Hybrid Hidden Markov Model for Modeling Equity Excess Growth Rate Dynamics: A Discrete-State Approach with Jump-Diffusion》(v2 2026-04-02, Alswaidan & Varner, Cornell) | **混合 HMM + Poisson 驱动跳跃持续期机制**——将连续超额增长率离散化为 Laplace 分位数定义的市场状态 + 用 Poisson 驱动的跳跃持续期机制增强 regime-switching 过程以强制 realistic 尾部状态停留时间。参数通过直接转移计数估计（完全避免 Baum-Welch EM）。SPY 10 年数据 1000 条模拟路径：KS/AD 拟合优度 pass rate >97%/91%（样本内）、>94%（样本外 2025 全年）。标准 HMM 无 jump 通过更多分布检验但无法生成波动率聚类。与 34号 的关联：**直接支撑 §5.2 第十七条远期候选**——Hybrid HMM Poisson 是 regime 持续性增强的第五条路径（与 JM jump penalty / Sticky HMM Dirichlet / 5 态过渡态 / negative-binomial hazard 并列），独特优势是**参数估计比当前 HMM 更简单**（直接转移计数绕过 Baum-Welch EM 迭代），同时通过 Poisson jump-duration 获得与 JM jump penalty 同等的持续性增强。MVP 不换（C1 已验证 HMM 4 态有效），若 HMM 实盘后发现状态抖动 + EM 重训练耗时成为双重瓶颈，Hybrid HMM Poisson 同时解决两个问题 |
| Oliveira/Guzman/Firooziye《(Non-Parametric) Bootstrap Robust Optimization for Portfolios and Trading Strategies》(arXiv:2510.12725, 2025-10-14, USP/UCL) | **非参数 bootstrap 鲁棒优化**——把效用当作随机变量做百分位优化，非参数 bootstrap 重采样构造数据驱动的置信区间（不假设特定分布形式）。实证：在组合与 time-series momentum 上比传统鲁棒优化（参数化/椭球不确定集）更平滑更稳定。与 34号 的关联：① Sortino 小样本偏差本质是 downside deviation 估计不稳，bootstrap 重采样可量化该不确定性并给出 Sortino 置信区间而非点估计——直接支撑施工要点 #14 BCa bootstrap 远期候选（PerformanceScore 从"点估计映射"升级为"BCa 下分位映射"）；② **CFA Institute 2026 共识**：downside deviation 分母必须用全部 n（非 n_downside）——常见实现错误人为抬高 Sortino，直接支撑施工要点 #13 的 CRITICAL bug 修复（原伪代码用 n_downside-1 分母虚高 ~60%）；③ BCa（Bias-Corrected and accelerated）是小样本偏差校正金标准（二阶精度，同时处理 bias 与 skewness），优于 percentile/normal 法（一阶）。MVP 不进（~100ms 计算开销），作为四件套防护升级路径登记 |
| quarcc.com《Endogenous Regime-Switching with Duration Dependence》(2026-03-08) | **3 态内生 regime-switching + negative-binomial hazard duration dependence**——用 negative-binomial 分布（而非 Poisson）引入 duration dependence，比 Poisson 更灵活（能处理过离散的停留时间），softmax 时变转移矩阵，GJR-GARCH 状态条件发射，skewed-t 分布。"前向转移赔率"作为可交易信号。与 34号 的关联：① **第四条 regime 持续性增强路径**（与 JM jump penalty / Poisson 持续期 / stochastic inertia 并列）——negative-binomial hazard 比 Poisson 更灵活处理过离散停留时间（A 股熊市停留时间方差 > 均值时 Poisson 不够），但复杂度更高；② skewed-t 分布印证 Soloviov 2026-07 的"Student-t innovations 必选"结论（§8.1 已引）；③ 适合个股级 regime 检测（我们做市场级），MVP 不换，记为 §5.2 远期候选池第五条路径 |
| arXiv:2604.27991《Stochastic Inertia in Regime-Switching Models》(2026-04-30, Schoeller et al.) | **随机惯性理论**——噪声反而能增强 regime 寿命，小噪声下系统比确定性对应物停留更久。为"在 HMM 转移中加少量噪声可提升持续性"提供理论依据。与 34号 的关联：① **regime 持续性增强的理论基础**——JM jump penalty（转换成本）/ Poisson 持续期（停留约束）/ stochastic inertia（噪声增强）三条路径共享"增强 regime 持续性"目标但机制不同，stochastic inertia 是最轻量的（仅在转移概率上加噪声）；② MVP 不采纳（理论支撑而非工程实现），但为 §5.2 远期候选池提供"为什么 regime 持续性增强有多种实现路径"的理论解释 |
| arXiv:2602.16952《HyRA: Hyperition RAN Allocation with Dual-Layer Water-Filling》(2026-02-18, Waterloo, Zangooei et al.) + ewinnington《Water-Filling to MIQP》(2025-04-16) | **双层 water-filling + KKT 闭式解 / water-filling → MIQP 转换**——HyRA 外层定预算 + 内层新颖 water-filling 调度，通过 KKT + Big-M 转为可解 MIP；ewinnington 指出当加入最小值约束（floor）或分配间关系约束时，迭代 water-filling 失效，应改用混合整数二次规划（MIQP）。与 34号 的关联：① 当前 `_normalize_and_clip()` 用迭代裁剪 + N=2 无解兜底（§3.2.4），对于 N=3-5 策略 + floor 5%/cap 40% 约束基本不触发无解（数学上有解）；② 若未来 floor/cap 约束更复杂（如策略间关系约束/动态 floor），迭代 water-filling 可能收敛慢或不收敛，MIQP 是更鲁棒的替代——但 MIQP 需求解器（scipy.optimize.milp 或 CVXPY），MVP 不采纳（当前迭代法有效）；③ POCS（Projection Onto Convex Sets）交替投影是可行性恢复的轻量替代。记为 §5.2 `_normalize_and_clip` 远期升级路径 |
| Soloviov《Do Bootstrap Confidence Intervals for Backtest Statistics Cover? A Controlled Study Under Serial Dependence》(bootstrap.marketmaker.cc, 2026-06-10, arXiv-ready; [GitHub](https://github.com/suenot/bootstrap-coverage)) | **Bootstrap CI 覆盖率受控实验**——5 种已知真实 Sharpe 的 DGP（iid Gaussian / iid Student-t / AR(1) / GARCH(1,1) / Markov regime-switching）× 3 种样本长度（250/1000/4000 日）× 14 种区间方法（Lo iid/HAC SE、percentile/basic/BCa bootstrap、trade-level、stationary/circular block bootstrap 自动块长），共 6000 次实验。**关键发现**：① **BCa 仅在 iid 下有效**（覆盖率 0.954），AR(1) φ=0.3 下 BCa 救不了（覆盖率 0.838 vs 名义 0.95）——"失败的是 resampling scheme 而非区间公式"；② GARCH 与 regime 波动率对 Sharpe 覆盖率损害很小；③ **最大回撤分位数全部乐观偏差**：iid 0.08-0.10 / regime 0.13-0.17 / AR(1) 0.23；④ 实践配方：绝不要按 bar 重采样依赖 PnL，默认用自动块长 block bootstrap 或 Lo HAC SE，把 bootstrap 回撤分位数当下界。**直接支撑施工要点 #14 十六次审查 CRITICAL 修正**——原 BCa bootstrap 远期候选在 A 股自相关下失效，须升级为 stationary block bootstrap（Politis-Romano 自动块长），block bootstrap 在 AR(1) 下覆盖率恢复到 0.946。BCa 保留为 ≥252 日 iid 近似场景的长窗口选项 |
| Staures & Kabašinskas《Identifiable Regime Detection in Pension Fund Networks via Sticky Hidden Markov Models》(preprints.org 2026-06-02, DOI:10.20944/preprints202606.0111.v1; Mathematics 2026, 14(14):2463) | **Sticky HMM Dirichlet 自转移先验**——Bayesian sticky 转移先验 `π_k ~ Dirichlet(α·1 + κ·e_k)`，κ 控制自转移持续性（期望自转移概率 `E[π_kk] = (α+κ)/(K·α+κ)`）；与 PCA absorption ratio + DTW 层次聚类组合。识别 3 个潜态，高风险期 cluster 跟踪误差放大 1.09×-1.23×。**直接支撑 §5.2 第六条远期候选**——Sticky HMM 是 regime 持续性增强的**第六条路径**（与 JM jump penalty / Poisson 持续期 / negative-binomial hazard / stochastic inertia / 5 态过渡态并列），实现侵入性极低（转移矩阵加 1 行先验），统计上最规范（贝叶斯先验是"状态持续性"教科书方法）。MVP 不采纳（C1 已验证 HMM 有效），若 HMM 实盘后发现状态高频抖动，Sticky HMM 是比 JM 更轻量的第一升级路径 |
| usepancake/batter《Pancake Engine Bootstrap CI + Permutation Test》(GitHub math-audit-0.4.md, 2026-05-26) | **Percentile bootstrap CI 工程实现 + CI_TOO_WIDE 守卫**——percentile bootstrap（10000 次重采样）+ `CI_TOO_WIDE` 守卫（阈值 5×：当 `(ci_high - ci_low)/|point_estimate| > 5.0` 时该指标不可信）；BCa 显式推迟到未来版本（O(N²) jackknife 开销）；Sharpe/Sortino/CAGR CI 同时输出。**直接支撑施工要点 #14 CI_TOO_WIDE 守卫**——5× 阈值来自 Ding & Martin (2017) 对 Sharpe ratio 的校准（年化 CI 宽度超 ~4× 点估计对应 p-value > 0.25），工程上简单有效。当 PerformanceScore 的 bootstrap CI 触发 CI_TOO_WIDE 时，应触发更强 Shrinkage 或强制中性 |
| 中邮证券/黄子崟《市场脉搏（2）：基于 LSTM~HMM 混合方案的量化择时与动态仓位管理》(2026-07-09, SAC S1340523090002) | **A 股本土 LSTM 自编码器 + GHMM 5 态方案**——LSTM 自编码器（90 日 × 25 维 → 10 维压缩）+ 高斯 HMM 5 态（1 个低自维持过渡态 + 4 个高自维持稳态），状态切换经过渡态完成减少稳态间直接跳跃；轻量级干预规则修正凯利公式均值回归偏差。2021 年以来多指数回测控制回撤并积累超额；**2026 年 K 型极端分化行情适应性偏弱**（超额损失锁定于特定状态，执行层问题非识别层问题）。**直接支撑 §5.2 A 股本土对标 + §6 待裁定 5 态结构**——5 态（4 稳态 + 1 过渡态）是第四条 regime 持续性增强路径（结构性过渡态），2026 K 型分化失效（2026H1 量化超额 14.17%→3.11%）印证"风险节流不做 alpha 择时"裁定。MVP 不采纳（C1 已验证 4 态有效），若 HMM 实盘后稳态间直接跳跃导致 PerformanceScore 跳变则评估加过渡态 |
| 华安证券/严佳炜、钱静闲《自适应市场状态的强化学习在资产配置中的应用》(2026-05-01) | **A 股本土 RL + KMeans/GMM/HMM 三机制**——KMeans + GMM + HMM 从波动率/回撤/利差提取 3 机制（稳定/中性/危机）；RL 环境（连续权重 + Sharpe 奖励 + ±3% 裁剪 + 每 30 步资本重置 + 每 25 步 -5% 冲击）；Transformer PPO Sharpe 1.43、Sortino 1.59；**奖励裁剪是关键**（移除后 Sharpe 1.07→0.83）；机制信号互信息 0.1020。与 34号 的关联：① 3 机制（稳定/中性/危机）可作为 4 态 HMM 的简化对照；② 奖励裁剪思路可嵌入 PerformanceScore 计算（±3% 裁剪 = 防极端 PerformanceScore）；③ **机制信号互信息 0.1020** 是可量化的信号强度基准——首批策略实盘后可测 HMM regime 信号与策略 PnL 的互信息做对照。MVP 不采纳 RL（§4.4 已拒绝），记为 A 股本土 RL 对照参考 |
| 湘财证券/仇华《2026年8月大类资产配置展望》(2026-07-26, 新浪财经转载) | **A 股本土波动率锚定风险平价实证**——以波动率、风险贡献度为核心锚的风险平价均衡模型；按风险偏好分保守/稳健/进取三档（目标年化波动 ≤4% / 8-10% / 15-18%）。2026 年 8 月建议进取型配置：权益 61%、债券 27%、商品 12%、货币 0%。与 34号 的关联：① **A 股本土风险平价实证**验证波动率锚定方法在中国市场可行性；② 三档风险偏好与个人账户可调参数契合——可参考作为 Base 因子的 A 股校准基准（当前 MVP 用等权 1/N，远期可升级到 inverse-volatility 或 risk parity）；③ 进取型权益 61% 与我们 cap 40% 单策略上限形成对照（多资产组合 vs 单市场多策略，性质不同）。记为 Base 因子 A 股校准参考 |
| CSDN/mokamo《A股市场状态识别：HMM + Optuna 超参优化的量化实战》(2026-05-16) | **A 股 3 态 GaussianHMM 实战**——3 态（BULL/SIDEWAYS/BEAR）+ Optuna 超参优化 + Walk-Forward Validation + Tushare 数据。**关键论据**：A 股年化波动率 20-30%（远高于标普 500 的 15%）；A 股 60%+ 时间处于震荡；3 态是"过拟合与表达力"的折中（2 态太粗、4 态过拟合）。与 34号 的关联：**直接质疑 4 态选择**——A 股个人账户小样本下 3 态可能比 4 态更稳健。记为 §6 待裁定"3 态 vs 4 态 ablation"项——首批策略 A 股数据上对比 3 态 vs 4 态样本外稳定性，若 3 态显著更稳则降级。[11号](11_regime_backtest_validation_plan.md) C1 验证 BIC 选优稳定收敛到 4 态，但未做 3 态样本外稳定性对比 |
| arXiv:2606.06190《Multi-Scale Markov-Switching GARCH: Volatility Regime Detection in EUR/USD》(2026-06-04, Chaudhary) | **多尺度 MS-GARCH + TVTP**——三层（1D/4H/1H）AR(1)-MS-GARCH + 时变转移概率（TVTP）+ skewed Student-t emissions；27 维联合概率张量 + Mixture-of-Experts。DM 检验显著优于 GARCH(1,1)（DM=+4.70, p=1.28e-6）。**关键结论**：4H/1H 上 TVTP 强烈受支持（ΔAIC=+690.7, +499.9），**1D（日频）上静态转移概率更优**——"semi-Markov models where transition probabilities depend on regime age"为未来方向。与 34号 的关联：**日频上 TVTP 不必要**的结论支撑我们 HMM 4 态用静态转移概率（非 TVTP）的选择——A 股日频 regime 检测无需时变转移概率，简化模型。MVP 不采纳多尺度（外汇 + 27 个 RidgeCV 对 A 股个人账户过重），但其日频 TVTP 不必要的结论对我们 HMM 配置有参考价值 |
| arXiv:2512.03777《A comparison between initialization strategies for the infinite hidden Markov model》(2026-06-12 v2, Cortese & Rossini, University of Milan) | **iHMM 初始化策略对比**——HDP 先验的 iHMM，beam sampler 推断；系统比较初始化策略。**关键发现**：distance-based clustering（KMeans++）初始化一致优于 model-based 和 uniform（后者是文献默认）。与 34号 的关联：iHMM 自动推断状态数可解决"4 态是否最优"的元问题，但贝叶斯非参推断成本高 MVP 不采纳；**其初始化结论（用 KMeans++ 而非均匀初始化）对当前 HMM 训练直接有用**——归 [10号](10_regime_detector_spec.md) regime 检测器 HMM EM 训练初始化策略：应用 KMeans++ 而非均匀初始化，提升收敛质量。记为 10 号 HMM 训练优化参考 |
| kooexperience.com《What Mood Is the Market In? HMM Regime Detection》(2026-03, Trader Koo) | **3 态 HMM 教程实证"three is the sweet spot"**——"Research shows that stock returns naturally cluster into roughly three volatility regimes. Two feels too coarse (you miss the 'normal' middle). Four or more starts overfitting noise. Three is the sweet spot." 与 34号 的关联：**直接支撑 §6 待裁定"3 态 vs 4 态 ablation"+"3 态 sweet spot 佐证"项**——与 CSDN 2026-05 A 股实证同向质疑 4 态选择。但 [11号] C1 BIC 选优稳定收敛到 4 态（非过拟合），且 4 态有语义基础（r1-r4），待 ablation 定论。tied covariance（所有状态共享协方差矩阵）是该教程的实现细节，归 [10号](10_regime_detector_spec.md) HMM 配置参考 |
| susanpotter.net《Bootstrap Methods for Strategy Robustness: Resampling When You Can't Get More Data》(2026-05-23) | **金融时序 bootstrap 方法论综述**——naive i.i.d. bootstrap 在金融时序上三重失效：① 破坏自相关（momentum/mean-reversion 模式消失）；② 破坏波动率聚类（GARCH-like 行为被打散）；③ 破坏截面相关（pairs trading 对冲关系断裂）。block bootstrap（Künsch 1989 moving block / Liu-Singh 1992 / Politis-Romano stationary）通过保留块内依赖结构解决。与 34号 的关联：**直接支撑施工要点 #14 十六次审查 CRITICAL 修正**——BCa bootstrap 在自相关下失效的机理：BCa 假设 resampling scheme 有效，但 i.i.d. resampling 在 AR(1) 下破坏自相关 → 方差估计失效 → CI 覆盖率崩塌。stationary block bootstrap（Politis-Romano 几何分布随机块长）保留序列内依赖结构，是 A 股日频收益率（情绪周期/趋势惯性导致自相关）的正确 bootstrap 方案 |
| metricgate.com《Choosing a Resampling Scheme for Dependent Time Series》(2026-06) | **四种依赖时序 bootstrap 方案对比决策框架**——block bootstrap（固定块长）/ stationary bootstrap（Politis-Romano 几何分布随机块长，保证重采样序列平稳）/ sieve bootstrap（AR 模型残差重采样）/ dependent wild bootstrap（相关随机权重）。**关键量化**：AR(1) φ=0.7 下 naive i.i.d. bootstrap 标准误仅为真实值的 ~40%（灾难性低估），block/stationary bootstrap 恢复大部分方差。与 34号 的关联：**直接支撑施工要点 #14 stationary block bootstrap 选择**——stationary bootstrap 比固定块长 block bootstrap 更鲁棒（对单一块长选择不敏感），是 A 股 60 日短窗口 Sortino CI 的最佳 resampling scheme。sieve bootstrap（AR 残差）是替代选项但需指定 AR 阶数 |
| Alswaidan, Jin & Varner《Continuous Hidden Markov Models for Equity Returns: Heavy-Tail Emission Families and Regime-Conditional Value-at-Risk》(arXiv:2606.23492, 2026-06, West Virginia University) | **CHMM-t（Student-t 发射的连续 HMM）颠覆性发现**——长期认为"HMM 无法复现收益率绝对值自相关的慢衰减"是时间性问题（→解法是 HSMM/jump-duration），本文用 CHMM-t 重新审视证明：**原始失败是分布性的，不是时间性的**——重尾边际分布（Student-t）而非更多 decay modes 弥合了大部分拟合差距，**无需调超参数**。在 SPY walk-forward、30 只股票面板、CRSP 跨年代、6 资产篮子上验证；模型还产出 regime-conditional VaR，通过 Christoffersen 条件覆盖检验。**直接支撑 §5.2 第十八条远期候选**——CHMM-t 是所有远期候选中实现成本最低（~50 行 emission 替换，不换检测器/不换状态划分/不重写 C1）且证据最颠覆（分布性修复优先于时间性修复，直接挑战 HSMM/jump-duration 路径前提）的路径。与 Soloviov 2026-07（§8.1 已引 Student-t innovations 修复 VaR 覆盖误差）一致——CHMM-t 是同一原理在 HMM emission 层的应用（Soloviov 在 GARCH innovation 层）。MVP 不换（C1 已验证 Gaussian HMM 4 态有效），若首批策略实盘后发现分布性问题（极端日 ConfidenceSignal 误判 / regime-conditional VaR 与尾部不匹配 / Sortino-Sharpe gap 频繁触发）则 CHMM-t 是第一升级路径 |
| Pav《Post-Selection Estimation of Sharpe Ratios》(arXiv:2606.01650v1, 2026-06-02) | **选中最高 in-sample Sharpe 策略后的真实 Sharpe 估计**——考虑"从 k 个策略中选 in-sample Sharpe 最高者后估计其真实 signal-noise ratio"问题，系统测试 5 种修正估计器（polyhedral lemma / James-Stein 收缩 / debias expected max Sharpe / thresholding / empirical Bayes GMLEB）。**关键发现**：James-Stein 估计器在多数现实参数（样本量/策略数/Sharpe 分布形态）下最优，紧随其后是 GMLEB 经验贝叶斯，且对资产收益相关性鲁棒。James-Stein 收缩因子 `s = (1 - (k-2)·σ²/‖ζ̂‖²)₊`（positive-part，k≥3 生效），把每个估计往横截面均值收缩，离群高值被拉回最多。**直接支撑施工要点 #15 PerformanceScore 选择偏差收缩远期候选**——本项目 PerformanceScore 用于多策略相对排序+差异化分配（构成"选择"操作），高 Sortino 策略的 Sortino 被选择膨胀→过度分配，James-Stein 收缩是正交于四件套绝对值防护的多策略相对值防护。N=3-5 策略满足 k≥3 适用条件，实现成本极低（~20 行）。MVP 不进（首批策略数与 track record 未定），若实盘后发现"上月 Sortino 最高策略次月反转"则 James-Stein 是第一修正路径 |
| Ryan《Conformal Kelly: Conformal Prediction Intervals as the Scale in Fractional Kelly Position Sizing》(arXiv:2608.01494v1, 2026-08-02, ACS Athens) | **保形预测区间宽度作为 fractional Kelly 的 σ**——`f* ≈ μ/σ²` 中 σ 取自 75% 保形区间半宽，区间变宽→缩仓、变窄→加仓。开发窗口（2016-2021，含交易成本+1日执行滞后+杠杆上限）年化净对数增长 28.5%、Sharpe 1.34、MaxDD 27.7%；风险控制层（保形区间下行 miss 率超历史率→砍杠杆）MaxDD 27.7%→20.3%。**关键设计原则（反直觉）**：最简单的慢/无权重/逐资产 rolling 保形分位数胜过所有快速自适应方案（每个自适应代价 0.7-5.3pp 年增长）——"仓位尺寸需要宽度稳定性而非局部尖锐性"；保形宽度比教科书标准差在匹配杠杆下多 2.1pp/年增长。**样本外警示**：2022+ 校准保持（0.745 vs 0.750 目标）但增长未保持（8.5%/7.0% 低于被动基准），作者预注册如实报告。**直接支撑 §4.5 Conformal Kelly 远期精炼登记**——直击"Kelly 对估计误差敏感"拒绝理由（保形区间提供有限样本分布无关覆盖率保证），但样本外增长未保持+仍是 Kelly 族（σ 敏感本质未变），不推翻 §4.5 Kelly 拒绝，登记为 [31号] Phase 4+ 单策略仓位尺寸远期精炼路径（归 [31号] 非 34号，因 Conformal Kelly 是单策略仓位非 meta 层多策略分配） |

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G15 讨论要点占位，参数等 C1 验证后校准 |
| 2026-08-10 | 1.0.0 | 回填分配框架（§2 背景 + §3 决策含 7 讨论要点逐项对齐 + §4 替代方案 + §5 上限 + §6 待裁定 + 过度工程审查）；C1 验证已通过引用（§0.5.4 四项全通过）；参数标"待策略 track record 后校准"；2026 行业搜索（Invesco/I-am-Uchenna/arxiv/misango/preprints）；status→active（框架已定，参数待校准） | C1 已通过（commit 852457e9）框架 why 成立；7 讨论要点逐项对齐；四档 Shrinkage 过度工程审查结论为不过细 |
| 2026-08-10 | 1.1.0 | 施工流程缺失补充：§3.2.2 冷启动过渡（≥20 日起算部分 Sharpe）+ walk-forward 无前视 + 60日 vs BestFolio 36个月对比；§3.2.3 Shrinkage 更新频率（日频+盘中突变重算）+ 1uptick 60%阈值印证 + 0.3 更激进理由；§3.2.4 裁剪迭代收敛性 + BestFolio cap 40% 印证；§3.3 effective_budget 目标值语义；§4.5 Kelly/BL 替代方案拒绝；§8.1 补 BestFolio/1uptick/loic-mmt(8月7日)/donarduka/stockalpha/MM-ARC 参考 | 二次审查发现施工环节流程缺失（冷启动/更新频率/目标值语义），2026-08 最新行业研究印证 60% 阈值与 cap 40% 参数选择 |
| 2026-08-10 | 1.2.0 | §3.2.2 PerformanceScore 从 Sharpe 切换到 **Sortino**（primary）+ Sharpe 保留为对照指标；补 Sharpe→Sortino 选型理由表（5 维度对比，A 股打板 upside volatility 论据）；补**无风险利率 Rf 定义**（货币基金 ~2%，月频更新）；补**熊市最低总暴露**（global_shrinkage floor 9% 设计，cash=防御资产，对照 2026 资本保全研究）；§6 待裁定补 Sortino 选型项；§8.1 补 Wasserstein HMM/RegimeFolio/advisingalpha/equiscale/portfoliogenius/fastercapital/moneylume/recessionistpro/protraderdaily 参考 | 三次审查发现 PerformanceScore 算法缺失（Sharpe 惩罚 A 股打板涨停板 upside volatility 导致低估），2026-08 最新行业研究 5 源一致推荐 Sortino 用于非对称收益分布；Wasserstein HMM 印证 regime inference stability 是 drawdown 一阶决定因素支撑 Shrinkage 路径 |
| 2026-08-10 | 1.3.0 | §3.2.2 修正 **Sortino 样本量隐患**（60 日窗口 downside 样本 ~24 日，ecassets/foliolab 2026 警告"statistically unreliable"+"inflated values"）→ 补 inflated values 防护三件套（downside<15 强制中性门槛 + cap 兜底 + Sortino/Sharpe gap 监控）+ 冷启动过渡门槛从 20 日上调到 30 日；施工注记补 downside 样本量门槛检查；§6 待裁定补样本量校准项；§8.1 补 ecassets/foliolab/fxroboteasy（Sortino 样本量与选型）+ Oxford Quantitative Finance 2026（FRED-MD 宏观 regime 检测，10 号前沿演进候选）参考 | 四次审查发现 Sortino 样本量施工算法缺失（小 downside 样本导致 Sortino 系统性偏高，原"24 日足够"论断与 2026 研究矛盾），全网搜索 2026-08-08 最新研究补充样本量防护 + 宏观 regime 检测前沿 |
| 2026-08-10 | 1.4.0 | §3.2.2 待校准补**冷启动贝叶斯收缩远期候选**（MRC arXiv:2605.24490 贝叶斯自适应混合 `w_prior×1.0 + w_data×Sortino` 权重随样本量渐变 vs 我们 30 日阈值硬切换，MVP 不采纳）；§8.1 补 MRC 参考（Shapley credits O(2^N) 过重不采纳 + 贝叶斯冷启动记为远期候选） | 五次审查全网搜索 2026-08-08 最新研究，发现 MRC（arXiv:2605.24490, 2026-05-23）贝叶斯冷启动方法比我们阈值切换更平滑，评估后记为远期候选不采纳（复杂度 vs 收益不划算，30 日阈值+floor/cap 已足够防极端）；Shapley credits O(2^N) 在 N=5 策略下过重，我们的 O(N) 乘法是正确替代 |
| 2026-08-10 | 1.5.0 | §3.2.2 **重大修正**：60 日 vs 36 个月——区分两来源（A: Sortino 自身机构标准 forex-basics/financefriend24/superglobalcalculator/getzenquery 2026 一致"36 个月最低"，我们 60 日=1/9 远低于标准；B: BestFolio 优化器窗口，不同性质）+ 补 60 日特殊理由（A 股情绪周期/非优化器/策略数少/四件套防护）+ 已知风险（连胜期 Sortino 偏高）+ 实盘校准触发条件（PerformanceScore 月度变动>0.3/排名波动/gap 频繁→上调 90/120 日）+ 远期演进（月频 Sortino+36 月对齐机构标准）；§3.2.4 补**floor/cap 无解兜底**（N=2 时数学无解，参考 JIMO 2026 Lkhagvasuren feasibility restoration：迭代 5 次未收敛→优先保 floor 降 cap 到 1-(N-1)×floor + 日志告警；N≥3 不触发）；§3.2.4 补 GATE-WPCA-PI（AIMS Mathematics 2026）entropy floor/sleeve caps 学术级印证；§6 待裁定补"60 日 vs 36 个月机构标准差距"校准项；§8.1 补 forex-basics/financefriend24/superglobalcalculator/getzenquery（Sortino 36 月机构标准）+ GATE-WPCA-PI + JIMO Lkhagvasuren + Claude AI 防御性组合 + KOSPI 2026 集中崩塌 参考 | 六次审查发现重大认知盲区：原"60 日 vs 36 个月"对比只引 BestFolio 优化器窗口，未识别 Sortino 自身有 36 个月机构标准（forex-basics 2026-05-28 evergreen verified 明确"institutional standard is a minimum of thirty-six months"），我们 60 日远低于标准是已知妥协需明确风险+校准触发条件；同时发现 floor/cap 在 N=2 时数学无解的施工算法缺失（JIMO 2026 feasibility restoration 支撑兜底设计）；GATE-WPCA-PI entropy floor 学术级印证 cap 40%；Claude AI 无人值守天然防御倾向印证低 global_shrinkage floor；KOSPI 2026 集中崩塌印证 cap 40% 防集中必要性 |
| 2026-08-10 | 1.6.0 | §3.2.5 补**12 态→4 态退化映射**（退化原则三表：按波动族合并/按趋势方向合并/稀有态冻结 + 当前实现行为 + ConfidenceSignal 不受退化影响 + 精确 ID 映射归 10 号待校准）；§3.2.3 补 **Quarter Kelly 与 Shrinkage 同构印证**（pooyagolchian 2026-04 fractional Kelly 实证表：Quarter Kelly 85% 增长/35% 回撤，与 Shrinkage 节流"适度收缩风险预算→小回撤代价获大部分增长"同构）；§3.2.7 新增**外部信号交叉验证**（5 档水温 Wyckoff-Analysis 实证 + 板块轮动状态 5 分类 WyckoffTradingAgent 实证 + 远期辅助印证定位 + RMATS 风险层解耦思想印证 + 过度工程审查不引入多 agent）；§5.2 补 **MPC 多期预测远期候选**（Nystrup/Boyd MPC + realized drawdown→γ 动态，完整框架过度工程但回撤通道思想可先吸收不换架构）；§6 待裁定补 3 项（退化映射精确查表/外部信号交叉验证启用/MPC 回撤通道增强）；§8.1 补 8 条新研究（RMATS/Wyckoff 水温/Wyckoff 板块轮动/pooyagolchian Kelly/Nystrup MPC/MDPI CVaR turnover/arXiv HMM+RL/youcanbuildthings risk parity） | 七次审查发现施工算法缺失：12 态→4 态退化映射无明确原则（Shrinkage 按态收缩会因态数不匹配悬空）；外部信号交叉验证机制缺失（HMM 4 态无独立水温/板块印证）；2026 最新研究整合——RMATS MaxDD 9.62% 印证风险层独立解耦 + 5 档水温实证（NEUTRAL 唯一正收益）+ Quarter Kelly 同构 + MPC 回撤通道思想；过度工程审查：5 档水温/板块轮动定位远期辅助印证不进 MVP，RMATS 多 agent 递归架构明确拒绝（个人项目） |
| 2026-08-10 | 1.7.0 | §3.2.2 补 **MAR 选型理由**（0%/Rf/target 三选一对比表 + 5 条决策理由：Sortino 原始意图/与 Sharpe 分子一致/避免 0% inflated values 放大/避免 target 主观偏差/机构默认 → 决策 MAR=Rf ~2%）；§3.2.2 补 **PerformanceScore 加权方式决策**（等权 vs EMA 对比表：MVP 用等权 walk-forward 无前视，EMA 半衰期 20-30 日列远期候选 + 升级触发条件 + volity 2026-06 EMA 趋势市实证）；§3.2.2 补**多策略 PerformanceScore 同向变动说明**（regime 切换时所有策略 Sortino 同降是 feature 非 bug——allocation 回答偏向谁/global_shrinkage 回答多谨慎解耦 + floor/cap 防同向极端 + 不同策略 regime 敏感度不同实际不同步）；§3.1 补**global_shrinkage 与 allocation 解耦实现注记**（Shrinkage 当前全局非每策略差异化，归一化约掉全局 Shrinkage，allocation 实际由 Base×PerformanceScore 决定，公式保留下标为未来每策略差异化预留）；§5.2 新增 **Statistical Jump Model（JM）远期候选**（Shu-Yu-Mulvey 2024 JM 显式 jump penalty 增强 regime 持续性 + 特征集 Sortino 同源 + 6 维对比表 + 三个关键启发：regime 持续性是 drawdown 一阶决定因素/Sortino 特征双重用途/JM-MPC 混合 + 中金 CICC A 股实证 + 远期演进路径排序三阶段）；§6 待裁定补 2 项（最小 regime 持续期约束/HMM→JM 替换）+ PerformanceScore 行补 MAR=Rf+EMA；§8.1 补 8 条新研究（Shu-Yu-Mulvey JM/中金 CICC JM/Cortese-Kolm-Lindström JM 信息准则/Li JM-MPC/dataloopr GARCH+Student-t/Soloviov GARCH 尾部受控实验/Park-Kim 深度生成模型/华安证券 SJM+BL） | 八次审查全网搜索 2026-08 最新研究：发现 Statistical Jump Model（Shu-Yu-Mulvey 2024，中金 CICC 2026-06 A 股实证）显式 jump penalty 增强 regime 持续性全面优于 HMM，且特征集 DD_10+Sortino_20+Sortino_60 与我们 PerformanceScore Sortino 同源——是 HMM 的远期增强替代候选（MVP 不采纳，C1 已证明 HMM 有效）；JM-MPC 混合（Li 2025）是"换检测器+换优化器"双重远期路径；MAR 选型缺失（Sortino 公式 MAR 有 0%/Rf/target 三选一实质影响结果）+ EMA 加权远期候选 + 多策略同向变动说明 + global_shrinkage 解耦实现注记 均为施工算法缺失补充；GARCH+Student-t 尾部建模（Soloviov 2026 受控实验：Student-t 修复 VaR 覆盖误差，尾形效应比不对称效应大一个数量级）记为 RiskSignal 波动建模远期增强 |
| 2026-08-10 | 1.8.0 | frontmatter 版本号追赶 v1.6.0→v1.8.0（v1.7.0 修订记录已存在但 frontmatter 滞后）+ §8.1 补 **汇安基金双层动态量化 A 股本土印证**（2026-08-07 cnfol 报道：顶层市值风格判别 20+ 因子 + 双独立选股池 + 切换阈值过滤噪音 + 底仓对冲误判；与本项目架构同构对照：顶层判别≈regime Shrinkage 但汇安做 alpha 择时我们做风险节流，双选股池≈StrategyBook sleeve，切换阈值≈ConfidenceSignal 四档，底仓对冲≈floor≥5%；A 股 2026H1 量化超额 14.17%→3.11% 印证"风险节流不做 alpha 择时"裁定正确性） | 九次审查全网搜索 2026-08-08 最新研究，发现汇安基金双层动态量化框架是 A 股本土 2026-08-07 最新实证，与本项目 regime+StrategyBook 架构高度同构，且 2026H1 量化超额衰减数据印证"alpha 择时难度飙升→风险节流更稳健"的裁定；同时修复 frontmatter 版本号漂移（v1.7.0 修订记录已存在但 frontmatter 滞后在 v1.6.0） |
| 2026-08-10 | 1.9.0 | §3.4 新增 **allocate 完整施工算法伪代码**（重大施工算法缺失补全）：BudgetAllocation dataclass（allocations + global_shrinkage + effective_budgets + 审计字段）+ `allocate()` 主入口 5 步流程（PerformanceScore 计算 → global_shrinkage 计算 → 三因子乘法 raw_allocation → 归一化+floor/cap 迭代裁剪 → effective_budget 缩放）+ `_compute_sortino_and_sharpe()`（MAR=Rf 硬约束 + downside 样本量检查 + 年化换算 + Sharpe 对照）+ `_compute_confidence_signal()`（max(P) 四档映射 + 1uptick 60% 阈值印证）+ `_compute_risk_signal()`（占位接口，13 参数归 [10号]）+ `_normalize_and_clip()`（迭代 5 次裁剪 + N=2 无解兜底优先保 floor 降 cap）+ 8 条施工要点（MAR=Rf 硬约束/downside 样本量门槛/gap 监控 1.3-1.5 基准/global_shrinkage 解耦 + 代码骨架 BUG 提醒/floor/cap N=2 兜底/冷启动过渡/RiskSignal 归 10 号/ConfidenceSignal 待 D1 校准）。§8.1 补 7 条新研究：firestrand SVM>HMM 基准（RQI 83.6-86.9 vs HMM 67.8-76.6，为 JM 远期候选提供额外证据 + 10 特征原则印证 6 因子精简）+ quantt Sortino 1.3-1.5×Sharpe 正常基准（gap 监控阈值校准实证）+ GARCH-ARJI 跳跃持续性（Int J Forecasting 2026，RiskSignal GARCH 升级须含 ARJI）+ M-ROLL AI-Markov 混合（IJFMR 2026-03/04，第三条远期路径 PSO 替代三因子乘法）+ regime-switching 股价跳跃（arXiv:2507.19824，regime 切换瞬间 max(P) 来不及反应印证 D-SIGNAL-68 盘中重算必要性）+ Acanto 8A 动量+风险平价（Sortino 1.21/MaxDD -7.6%，机构级基准印证 PerformanceScore Sortino 目标 1.0-1.5 合理）。frontmatter v1.8.0→v1.9.0 | 十次审查全网搜索 2026-08-10 最新研究，发现**重大施工算法缺失**：§3.1-§3.3 定义了三因子乘法逻辑规则但缺统一编排入口的施工算法伪代码（33号已有 §3.4 handle_budget_change 完整伪代码，34号缺对等的 allocate 伪代码）。补全后 Sortino 计算（MAR=Rf + downside 门槛 + gap 监控）/ Shrinkage 计算（四档×13 参数）/ 归一化裁剪（迭代+N=2 兜底）/ global_shrinkage 解耦 全部整合为单一 allocate 函数。同时发现 firestrand 2025-09 基准显示 SVM 集成优于 HMM（RQI 83.6-86.9 vs 67.8-76.6），为 JM 远期候选提供"不换 JM 也可换 SVM"的更轻量替代路径；quantt 2026-04 Sortino 1.3-1.5×Sharpe 正常范围为 gap 监控阈值提供实证校准；GARCH-ARJI 2026 跳跃持续性为 RiskSignal GARCH 升级须含 ARJI 提供理论支撑 |
| 2026-08-10 | 2.0.0 | §8.1 补 3 条 2026 最新研究（十二次审查全网搜索 2026-08-08~10）：① **arXiv:2606.09478 A 股高频 regime-aware 波动率预测实证**（regime-augmented HARQ + Markov-switching GJR-GARCH + XGBoost 严格 walk-forward，regime-aware 波动率预测持续优于 baseline HARQ）——**A 股本土实证**支撑 RiskSignal realized_vol 升级到 regime-augmented GARCH 的远期候选适用性（当前用分位数，C1 已验证有效 MVP 不换）；② **arXiv:2604.09060 AEGIS 框架**（动量门控 + minimax 相关 + SLSQP 直接优化 Sortino，20 年 walk-forward）——"直接优化 Sortino"印证我们 PerformanceScore 选 Sortino 的正确性（若 Sortino 非好优化目标 AEGIS 不会选它做目标函数），SLSQP 优化器记为远期候选（§4.2 已拒绝 MVO，SLSQP 是 MVO 变体同样需协方差估计 MVP 不采纳）；③ **arXiv:2603.10202 Hybrid HMM + Poisson 跳跃持续期机制**（强制尾态停留时间 + 避免 Baum-Welch EM 直接转移计数估计，SPY 10 年 KS/AD pass rate >94%）——**第三条 regime 持续性增强路径**（与 JM jump penalty 并列），若 HMM 实盘后发现尾态停留时间不足，Poisson 持续期机制是比 JM 更轻量的增强路径（不换检测器只加停留约束），记为 §5.2 JM 远期候选的并行替代路径。施工算法完整性结论：§3.4 allocate 完整伪代码已覆盖 PerformanceScore/Shrinkage/归一化裁剪/global_shrinkage 解耦全场景，本轮无施工算法缺失（仅远期候选证据补充）。frontmatter v1.9.0→v2.0.0 | 十二次审查全网搜索 2026-08-08~10 最新研究，评估施工算法完整性 + 更好算法。结论：① 施工算法无缺失——§3.4 allocate 完整伪代码已覆盖全场景（与 33号 §3.4 handle_budget_change 对等）；② 3 条新研究均为远期候选证据非 MVP 变更——A 股 regime-augmented GARCH 是 RiskSignal 升级路径（C1 已验证分位数有效）/ AEGIS SLSQP Sortino 优化印证 Sortino 选型正确但优化器需协方差估计 MVP 不换 / Hybrid HMM Poisson 持续期是 JM 的并行替代路径（HMM 有效不换）；③ 选项之外更好的算法评估：当前 HMM 4 态 + Shrinkage + Sortino 三因子乘法经 C1 验证有效（MaxDD 改善 7.36pp），3 条新研究均不构成"更好到需更换 MVP"的证据，远期候选池已有 JM/SVM/GARCH-ARJI/M-ROLL 四条路径，本轮新增 Poisson 持续期为第五条 |
| 2026-08-10 | 2.1.0 | §3.2.2 新增 **⚠️ 危机态（CRISIS）覆盖说明**（解决 9% floor vs 5% crisis cap 冲突）：明确 firm 层 5% crisis cap（[31号] §2.4.3 ⑩CRISIS 特殊态）优先于 meta 层 9% global_shrinkage floor——两者不矛盾因为适用不同 regime 态（9% floor 管 r4 熊市常规态，5% cap 管 ⑩CRISIS 特殊态，D-SIGNAL-68 overlay 触发）；4 条关键区分（r4≠⑩ / floor 是目标下限非硬约束 / cap 是硬上限 / r4+⑩同时触发时⑩优先9%floor悬空）+ 施工注记（`_compute_shrinkage()` 须新增 CRISIS 态分支，is_crisis=True 时 floor 从 0.09 降至 0.05 对齐 crisis cap，须首批策略上线前实现否则 33号收敛行为异常）。§3.4 伪代码 3 项高优先级缺口修复：① **days_live 交易日口径**（原用 calendar days `.days` 与 COLD_START_MIN_DAYS=30 交易日口径不一致，30 自然日≈20-22 交易日致冷启动过早脱离，改用 `trading_days_live=len(returns)`）；② **ddof 一致性**（原 Sortino downside 用 np.mean ddof=0 / Sharpe 用 np.std ddof=1 不一致致 gap 监控 apples-to-oranges，统一改 ddof=1 样本估计）；③ **gap 常量语义**（原 `SORTINO_SHARPE_GAP_THRESHOLD*2` 语义模糊，重命名 `GAP_NORMAL_CEILING=1.5` + 两级阈值 1.8/2.25）；④ allocate() 函数签名新增 is_crisis 参数 + Step 2 CRISIS floor 降级分支。施工要点补 #9-#12（days_live 口径/ddof 一致/gap 常量/CRISIS 分支）。frontmatter v1.9.0→v2.1.0（追赶 v2.0.0 修订记录+本次升级） | 十三次审查发现 **CRITICAL 冲突** + 3 项施工算法口径 bug：① §3.2.2 global_shrinkage floor=9% 与 [31号] §2.4.3 CRISIS cap=5% 表面矛盾（9%>5%），分析后确认两者适用不同 regime 态不矛盾，但须显式声明优先级层次（firm 层硬 cap > meta 层目标 floor）+ 施工算法须新增 CRISIS 分支；② days_live 自然日 vs 交易日口径 bug 致冷启动过早脱离；③ ddof 不一致致 gap 监控误报；④ gap 常量命名模糊。均为风险红线级/统计正确性问题，须首批策略上线前闭环 |
| 2026-08-10 | 2.2.0 | §3.4 伪代码补 **Sortino 下行偏差分母 CRITICAL bug 修复**（十四次审查）：原 `downside_deviation = sqrt(Σ(...) / max(n_downside - 1, 1))` 分母用 `n_downside-1`（仅下行观测数）——CFA Institute 2026 共识 + arXiv:2510.12725（Oliveira et al. 2025-10 USP/UCL）引证：**常见实现错误**，会人为抬高 Sortino（分母更小 → σ_d 更小 → Sortino 更大 → PerformanceScore 系统性高估 → budget 分配偏差）。例：n=60, n_downside=24 → n_downside-1=23 vs 正确的 n-1=59 → Sortino 虚高 √(59/23)≈1.6x。**已修复**：分母改用 `max(n - 1, 1)`（总样本量 n-1，ddof=1 与 Sharpe 一致），分子仍只对 `R < MAR` 的日子求和（above-MAR 日子贡献 0）。这是比施工要点 #10（ddof 不一致，影响 ~3%）更严重的统计正确性 bug（影响 ~60%）。施工要点补 #13（Sortino 下行偏差分母修复 + CFA Institute 2026 共识 + arXiv:2510.12725 引证）+ #14（**BCa bootstrap 远期候选**：arXiv:2510.12725 非参数 bootstrap 鲁棒优化把 Sortino 当带置信区间的随机量，BCa 二阶精度同时处理 bias+skewness 优于 percentile/normal 法一阶，升级路径为 PerformanceScore 从"点估计映射"→"BCa 下分位映射"用 5% 下分位保守估计天然处理小样本偏差，不进 MVP ~100ms 开销作为四件套防护升级路径登记）。§8.1 补 arXiv:2510.12725（Oliveira BCa bootstrap + CFA Institute downside deviation 分母共识）。frontmatter v2.1.0→v2.2.0 | 十四次审查发现 **CRITICAL 统计正确性 bug**：Sortino 下行偏差分母用 `n_downside-1` 是常见实现错误（CFA Institute 2026 共识），人为抬高 Sortino ~60%（n=60, n_downside=24 场景），导致 PerformanceScore 系统性高估 + budget 分配偏差。修复分母为 `n-1`（与 Sharpe ddof=1 一致）。同时登记 BCa bootstrap（arXiv:2510.12725）作为四件套防护升级路径——把 Sortino 从点估计升级为带 95% 置信区间的随机量，用 5% 下分位保守估计天然处理小样本偏差，MVP 不进（~100ms 开销+复杂度）但作为远期升级路径 |
| 2026-08-10 | 2.3.0 | §8.1 补 **3 条 Sortino 分母修复 + soft allocation 设计验证引用**（十五次审查全网搜索 2026-08-08~10）：① **quantt.co.uk 引用更新**——补 Step 5 明确原文"divide by the total number of observations (N), not just the number of below-target ones"+ "This is a common source of confusion"，独立验证 v2.2.0 施工要点 #13 的 n_downside-1→n-1 修复正确；② **CFA Institute 新增引用**（rpc.cfainstitute.org, Deborah Kidd CFA）——Sortino 比率权威原始定义来源，明确 downside deviation 分母争议"easy to understand but also easy to miscalculate"+ 引用 Sortino-Forsey 1996 bootstrap 方法为 BCa bootstrap 远期候选（施工要点 #14）提供原始理论溯源；③ **RPubs HMM walk-forward 新增引用**（2026-04）——三策略对比实证：expanding window+hard switch 失败（仅 ~20% 持仓 crisis-scarred）vs **soft allocation（概率加权敞口）最优 MaxDD -30.5% vs hard -52.4%**，直接验证 ConfidenceSignal 四档软映射设计（非 binary bull/bear 开关）+ expanding window 失败警示（10号 HMM refit 须用 rolling 非 expanding）。frontmatter v2.2.0→v2.3.0 | 十五次审查全网搜索 2026-08-08~10 最新研究，为 v2.2.0 Sortino 分母修复 + ConfidenceSignal 软映射设计补充独立验证引用。quantt.co.uk 2026-04 Step 5 原文 + CFA Institute 权威定义 + RPubs soft allocation 实证三重验证 v2.2.0 修复正确性。CFA Institute Sortino-Forsey 1996 bootstrap 引用为 BCa bootstrap 远期候选提供原始理论溯源。RPubs expanding window 失败警示为 10号 HMM refit 策略提供设计约束（须 rolling 非 expanding） |
| 2026-08-10 | 2.4.0 | **十六次审查（全网搜索 2026-06~08-10 最新研究）**——3 项核心改动：① **施工要点 #14 CRITICAL 修正：BCa → block bootstrap**——Soloviov《Do Bootstrap Confidence Intervals Cover?》(bootstrap.marketmaker.cc, 2026-06-10) 6000 次受控实验证明 BCa 仅在 iid 下有效（覆盖率 0.954），AR(1) φ=0.3 自相关下 BCa 救不了（覆盖率 0.838 vs 名义 0.95），A 股日频收益率有自相关 → 须升级为 stationary block bootstrap（Politis-Romano 自动块长，AR(1) 下覆盖率恢复 0.946）+ CI_TOO_WIDE 守卫（5× 阈值，Pancake Engine 2026-05 / Ding & Martin 2017）；② **§5.2 新增第十六条远期候选：Sticky HMM Dirichlet 先验**——Staures & Kabašinskas（Mathematics 2026, 14(14):2463）Bayesian sticky 转移先验 `π_k ~ Dir(α+κ·e_k)`，实现侵入性极低（转移矩阵加 1 行先验），统计上最规范，是比 JM 更轻量的第一升级路径 + **A 股本土对标：中邮证券 LSTM-GHMM 5 态**（2026-07-09）4 稳态+1 过渡态减少稳态间直接跳跃，2026 K 型分化失效印证风险节流哲学 + 远期演进路径排序更新（①.5 Sticky HMM / ②.5 5 态结构）；③ **§6 待裁定新增 3 项**（Sticky HMM Dirichlet 先验 / 5 态结构 / 3 态 vs 4 态 ablation）+ **§8.1 新增 8 条 2026 研究**（Soloviov bootstrap 覆盖率 / Staures Sticky HMM / Pancake Engine CI_TOO_WIDE / 中邮证券 LSTM-GHMM 5 态 / 华安证券 RL+HMM 三机制 / 湘财证券风险平价 / CSDN 3 态 vs 4 态 / arXiv:2606.06190 日频 TVTP 不必要 / arXiv:2512.03777 iHMM KMeans++ 初始化）。施工算法完整性结论：§3.4 allocate 完整伪代码已覆盖全场景，本轮无施工算法缺失（施工要点 #14 是远期候选修正非 MVP 变更，BCa 从未进 MVP）。frontmatter v2.3.0→v2.4.0 | 十六次审查全网搜索 2026-06~08-10 最新研究（后台 agent 返回 4 领域 20+ 篇研究），发现 1 项 CRITICAL 远期候选修正 + 2 项高价值远期候选登记。① Soloviov 2026-06 受控实验证明 BCa 在自相关下失效——原 v2.2.0 施工要点 #14 登记的 BCa bootstrap 远期候选在 A 股自相关下会给出虚假置信区间，须修正为 stationary block bootstrap，这是远期候选路径修正非 MVP 变更（BCa 从未进 MVP）；② Sticky HMM Dirichlet 先验是 regime 持续性增强的第六条路径，实现侵入性最低（1 行先验），若 HMM 实盘后发现状态抖动是比 JM 更轻量的第一升级路径；③ 中邮证券 5 态方案是 A 股本土最新对标（2026-07-09），2026 K 型分化失效（量化超额 14.17%→3.11%）印证"风险节流不做 alpha 择时"裁定。延续过度工程纠偏：所有新发现均远期候选登记非 MVP baseline |
| 2026-08-10 | 2.5.0 | **十七次审查（全网搜索 2026-08-08~10 最新研究）**——3 项核心改动：① **§5.2 新增第十七条远期候选：Hybrid HMM with Poisson Jump-Duration**——Alswaidan & Varner（arXiv:2603.10202v2, Cornell, 2026-03-10/04-02）三组件创新：Laplace 分位数状态划分（非聚类）+ Poisson jump-duration 强制尾部态驻留 + **直接转移计数绕过 Baum-Welch EM**（比当前 HMM 参数估计更简单）。SPY 10 年 KS/AD >97%/91%（样本内）、94%（样本外）。标准 HMM 无 jump 通过更多分布检验但无法生成波动率聚类。**是 JM 的轻量替代**（JM 需动态规划+坐标下降，Hybrid HMM 直接计数无迭代），独特优势是同时解决 regime 持续性 + EM 计算成本两个问题。升级优先级排序：Sticky HMM（最低侵入）> 5 态结构 > Hybrid HMM Poisson（换状态划分+绕过 EM）> JM（完全重写）。远期演进路径排序新增 ②.6 档；② **§6 待裁定新增 2 项**（Hybrid HMM Poisson jump-duration / 3 态 sweet spot 佐证）——kooexperience 2026-03 实证"three is the sweet spot"与 CSDN 2026-05 A 股实证同向质疑 4 态，但 C1 BIC 选优稳定收敛到 4 态待 ablation 定论；③ **§8.1 新增 3 条 2026 研究**（kooexperience 3 态 sweet spot / susanpotter block bootstrap 方法论 / metricgate 四种 bootstrap 方案对比）+ arXiv:2603.10202 引用更新（v1→v2 修订日期 + 第十七条远期候选对齐 + 标准无 jump HMM 局限性补充）。比较表"Poisson 持续期"列升级为"Hybrid HMM Poisson"（补状态划分维度 + 直接转移计数实现侵入性修正）。施工算法完整性结论：§3.4 allocate 完整伪代码已覆盖全场景，本轮无施工算法缺失（第十七条远期候选是远期登记非 MVP 变更）。frontmatter v2.4.0→v2.5.0 | 十七次审查全网搜索 2026-08-08~10 最新研究，完成待办任务"评估 Hybrid HMM Poisson jump-duration 作为 JM 轻量替代"。关键发现：Cornell arXiv:2603.10202 的 Hybrid HMM Poisson **不是 JM 的简化版而是独立路径**——其"直接转移计数绕过 Baum-Welch EM"使参数估计比当前 HMM 更简单（理论升级反而降低实现复杂度），同时 Poisson jump-duration 获得与 JM jump penalty 同等的持续性增强。文档结构审查：§5.2 远期候选组织合理（JM→Sticky HMM→中邮 5 态→Hybrid HMM Poisson 按"换不换检测器"递进），§6 待裁定按"侵入性递增"排序，§8.1 引用按"regime 持续性→bootstrap 方法论→A 股本土"分组。block bootstrap 方法论（susanpotter/metricgate）独立验证 v2.4.0 BCa→stationary block bootstrap 修正正确性 |
| 2026-08-10 | 2.6.0 | **十八次审查（全网搜索 2026-06~08-10 最新研究）**——5 项核心改动：① **§5.2 新增第十八条远期候选：CHMM-t（Student-t 发射的连续 HMM）——最高优先级选项外更好算法**——Alswaidan, Jin & Varner（arXiv:2606.23492, 2026-06, West Virginia University）颠覆性证明"HMM 无法复现收益率绝对值自相关的慢衰减"是**分布性**问题而非**时间性**问题——重尾边际分布（Student-t emission）而非更多 decay modes（jump-duration/HSMM）弥合大部分拟合差距，无需调超参数。CHMM-t 实现成本最低（~50 行 emission 替换，不换检测器/不换状态划分/不重写 C1），证据最颠覆（直接挑战 HSMM/jump-duration 路径前提）。升级优先级更新：CHMM-t（分布性，最高优先级）> Sticky HMM（时间性-先验）> 5 态结构 > Hybrid HMM Poisson > JM；② **§5.2 新增第十九条远期候选：HSMM + HMM-GAS + BOCPD 三条并行路径**——HSMM（显式持续期半马尔可夫，Hybrid HMM Poisson 的通用版）/ HMM-GAS（score-driven 时变转移，观测驱动无需 MCMC）/ BOCPD（贝叶斯在线变点，Fast-BOCPD 库 + 朱映秋《统计研究》上证综指 A 股本土实证）；③ **施工要点 #15 新增：PerformanceScore 选择偏差收缩（James-Stein 估计器）**——Pav（arXiv:2606.01650v1, 2026-06-02）证明 James-Stein 估计器在多数现实参数下最优，收缩因子 `s=(1-(k-2)σ²/‖ζ̂‖²)₊`，N=3-5 策略满足 k≥3 适用条件，是正交于四件套绝对值防护的多策略相对值防护（~20 行），MVP 不进登记远期；④ **施工要点 #16 新增：Block-wild Bootstrap 评估·过度工程纠偏**——评估结论不采纳，依据 Soloviov 2026-06"GARCH 与 regime 波动率对 Sharpe 覆盖率损害很小"，stationary block bootstrap 已充分，block-wild 异方差修正收益边际不符合 MVP 简洁原则；⑤ **§4.5 新增 Conformal Kelly 远期精炼登记**——Ryan（arXiv:2608.01494v1, 2026-08-02）保形预测区间宽度作 fractional Kelly 的 σ，开发窗口 MaxDD 27.7%→20.3% 但样本外增长未保持，不推翻 Kelly 拒绝，登记为 [31号] Phase 4+ 单策略仓位远期精炼（归 [31号] 非 34号）；⑥ **§8.1 新增 3 条 2026 研究**（CHMM-t arXiv:2606.23492 / James-Stein Sharpe arXiv:2606.01650 / Conformal Kelly arXiv:2608.01494）。施工算法完整性结论：§3.4 allocate 完整伪代码已覆盖全场景，本轮无施工算法缺失（第十八/十九条远期候选 + 施工要点 #15/#16 + Conformal Kelly 均为远期登记非 MVP 变更）。frontmatter v2.5.0→v2.6.0 | 十八次审查全网搜索 2026-06~08-10 最新研究，完成 3 项待办任务（Block-wild Bootstrap 评估→过度工程纠偏不采纳 / Conformal Kelly 评估→[31号] 远期精炼登记 / James-Stein 评估→施工要点 #15 登记）。关键发现：① CHMM-t（arXiv:2606.23492）的"分布性修复优先于时间性修复"是颠覆性结论，直接挑战第十七条 Hybrid HMM Poisson + HSMM 路径的前提——重尾 emission（Student-t）比 jump-duration/HSMM 用更低成本解决更根本问题，提升为远期演进第一优先级；② James-Stein 收缩（arXiv:2606.01650）填补 PerformanceScore 多策略选择偏差防护空白（四件套是单策略绝对值防护，James-Stein 是多策略相对值防护，两者正交互补）；③ Block-wild Bootstrap 评估为过度工程（Soloviov 证据表明 GARCH 对 Sharpe 覆盖率损害小，stationary block bootstrap 已充分）；④ Conformal Kelly 样本外增长未保持警示 Kelly 族即使加保形区间仍有过拟合风险，不推翻 §4.5 拒绝。延续过度工程纠偏纪律：所有新发现均远期候选登记非 MVP baseline |
| 2026-08-10 | 2.7.0 | **十九次审查·代码施工完成**——[regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) MOD-PA-007 从骨架（MATURITY=design, v0.1.0）升级到 **production（v1.0.0）**。**施工内容**：① `allocate()` 主入口 5 步流程（PerformanceScore → global_shrinkage → raw_allocation → normalize+clip → effective_budget）完整实现；② `_compute_shrinkage()` 含 ConfidenceSignal 四档 × RiskSignal + CRISIS 态 floor 降级（0.09→0.05，§3.4 施工要点 #12）；③ `_compute_confidence_signal()` max(P) 四档映射；④ `_compute_risk_signal()` 13 参数占位接口（实际逻辑归 [10号]）；⑤ `_compute_raw_allocation()` Base×PerformanceScore（不含全局 Shrinkage，§3.4 施工要点 #4）；⑥ `_normalize_and_clip()` **water-filling 投影算法**（原伪代码"裁剪+全局再归一化"在 N=2/cap 受限场景收敛失败，升级为固定越界值+按比例重分配未越界部分，避免被裁剪值在再归一化时拉回越界区间）；⑦ `compute_performance_score()` 静态方法（60 日 Sortino + MAR=Rf + downside 样本量门槛 + gap 监控，供上游计算）；⑧ `_apply_cold_start_neutral()` 冷启动校验（<30 交易日强制中性，防上游误传）。**55 测试用例全绿**（0.75s）：TestConfidenceSignal(8) + TestRiskSignal(4) + TestShrinkage(7) + TestNormalizeAndClip(8) + TestRawAllocation(3) + TestAllocate(9) + TestComputePerformanceScore(8) + TestEdgeCases(8)。AllocationError(ZA-PA-0007) 自定义异常已实现。§3.1 代码映射更新为 v1.0.0 production。frontmatter v2.6.0→v2.7.0 | 价值增长点转向代码施工——文档审查 18 轮后边际价值极低，§3.4 伪代码已覆盖全场景。本轮完成 RegimeMetaAllocator 代码施工，是 MOD-PA-007 从设计到 production 的里程碑。water-filling 算法是施工中发现的伪代码改进——原"裁剪+全局再归一化"在 N=2 + cap=40% 无解场景迭代 5 次后 alloc 被扭曲到 0.5/0.5（应在放宽 cap 后恢复 0.75/0.25），water-filling 通过固定越界值+只重分配未越界部分避免此问题。CRISIS 态 floor 降级（施工要点 #12）已实现。冷启动校验防上游误传非中性值。 |
