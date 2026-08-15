---
ttl: permanent
doc_type: architecture_view
title: RegimeMetaAllocator 参数
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.8.5"
date: 2026-08-15
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
- regime 检测器（[10_regime_detector_spec](10_regime_detector_spec.md)）已实现并验证：4 态 HMM + D-SIGNAL-68 overlay + Shrinkage 二维公式。**C1 验证已通过**（[11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §0.5.4，2026-08-08）：Shrinkage 节流有效（MaxDD 改善 +7.36pp，Calmar +27%），核心假设成立

### 2.2 核心问题

regime 信号如何用于多策略资金分配？两种用法有根本差异：

| 用法 | 性质 | 误差后果 | 实证 |
|---|---|---|---|
| **alpha 择时**（regime 重定向资金到"表现好的策略"） | 进攻性 | 判错 = 主动亏损 | Morwane：Sharpe 1.43→0.87（**降**） |
| **风险节流**（regime 只收缩总暴露，不重定向） | 防御性 | 判错 = 机会成本（少赚） | Morwane：Sharpe 1.43→1.43（不变），MaxDD −14.2%→−10.3%（**改善**） |

**已裁定（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2，2026-08-05）**：移除 RegimeScore，regime 仅通过 Shrinkage 做风险节流。regime 只回答"现在该多谨慎"，不回答"现在该偏向哪个策略"——后者由 PerformanceScore 后验 PnL 自然捕获。

### 2.3 约束条件

- **A 股不能做空** → 对冲式优化失效；**策略 PnL 未就绪** → PerformanceScore 无法计算，当前只能用 Base 先验（等权 1/N）
- **C1 已通过但参数阈值待校准** → 四档阈值（60/80/95%）的 D1 ±20% 敏感性网格未跑（[11号](11_regime_backtest_validation_plan.md) §0.5.7）
- **实际 4 态非 12 态**（[11号](11_regime_backtest_validation_plan.md) §0.5.2）：r1 低波 27.6% / r2 中波 37.4% / r3 牛市 14.9% / r4 熊市 20.2%——**无 <1% 稀有态**，稀有态机制在 4 态下基本不触发

## 3. 决策：三因子乘法分配（Base × PerformanceScore × Shrinkage）

### 3.1 分配公式

```
allocation_i = normalize( Base_i × PerformanceScore_i × Shrinkage_i )

  硬约束：floor ≥ 5%（防饿死），cap ≤ 40%（防集中），Σ allocation_i = 1.0
```

✅ **已施工 production**：[regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) MOD-PA-007（**v1.0.0 production**，MATURITY=production，commit 81c7687540）——`allocate()` 5 步流程 + `_compute_shrinkage()`（含 CRISIS floor 降级 0.09→0.05）+ `_normalize_and_clip()`（water-filling 投影）+ `compute_performance_score()` 静态方法（Sortino→[0.5,1.5]）全部落地，`FLOOR=0.05` / `CAP=0.40`。✅ **测试套件已重建**（2026-08-15，AI-REGIME-001）：[test_regime_meta_allocator.py](../../../../tests/pf_alloc/test_regime_meta_allocator.py) 55 用例按 §3.4 施工要点 16 条 + 代码本体回建（原 2026-08-11 git 灾难丢失，从未提交不可恢复），两轮 55/55 全绿，重建后立即 git 提交闭环（灾难教训：未提交=无保护）。

**两个层次**（[BudgetAllocation](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) dataclass）：

| 层次 | 字段 | 回答的问题 | 范围 |
|---|---|---|---|
| 相对占比 | `allocations`（Σ=1.0） | "偏向哪个策略" | floor 5% ~ cap 40% |
| 总暴露因子 | `global_shrinkage` | "现在该多谨慎" | 0.21 ~ 1.0 |
| 实收预算 | `effective_budgets = allocation_i × global_shrinkage` | 策略实际可用 budget | — |

> **关键区分**：allocation_i（相对占比）由 Base×PerformanceScore 主导；global_shrinkage（总暴露）由 regime 主导。两者解耦——regime 不重定向资金，只缩放总暴露。**实现注记**：代码当前 Shrinkage 是**全局**的（所有策略共用），归一化时约掉——**allocation_i 实际由 Base×PerformanceScore 决定，Shrinkage 只通过 `effective_budget = allocation_i × global_shrinkage` 缩放总暴露**。公式保留 Shrinkage_i 下标是为未来每策略差异化 Shrinkage 预留。

### 3.2 讨论要点逐项对齐

#### ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` → §3.1

**决策**：三因子乘法 + 归一化 + floor/cap 裁剪。已定型于 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2。乘法而非加法/优化器：O(N) 复杂度，无协方差估计，归因清晰（"加法替代优化器"哲学 [30号](30_multi_strategy_concurrency.md) §2.3 的 meta 层延伸）。

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

##### Sharpe → Sortino 的选型理由

| 维度 | Sharpe | Sortino | 对我们的影响 |
|---|---|---|---|
| 风险定义 | 总标准差（上下行都算"风险"） | 仅下行偏差（只惩罚亏损） | 我们 PerformanceScore 的目的是"识别亏损策略"做风险节流，不是"识别波动策略"——Sortino 的 downside-focus 与目的对齐 |
| 对 upside volatility | **惩罚**（涨停板 = "风险"） | **不惩罚**（涨停板 = 好事） | A 股打板策略有大量涨停板 upside 波动，Sharpe 会**低估**打板策略的 PerformanceScore → budget 分配偏差；事件驱动策略二元结果同理 |
| 2026 行业共识 | 通用标准，适合对称分布 | **非对称/偏态分布首选**（advisingalpha/equiscale/portfoliogenius/moneylume/fastercapital 2026 一致） | A 股策略收益分布普遍右偏 → 非对称 → Sortino 更合适 |
| Sortino ≥ Sharpe | 恒成立 | — | Sortino >> Sharpe 的 gap = "friendly asymmetry"（上行波动为主），是好策略的标志而非噪声 |

**结论**：切换到 Sortino 作为 PerformanceScore 的 primary 指标。Sharpe 保留为**对照指标**（监控 Sortino/Sharpe gap，gap 大 = 策略上行偏态强 = 友好；gap 小 = 对称波动 = 中性）。✅ 代码侧已施工（`compute_performance_score()` 静态方法，见 §3.5），映射区间 [0.5,1.5] / 60 日窗口 / floor-cap 兜底均不变。

##### 无风险利率 Rf 定义

| 参数 | 取值 | 来源 | 更新频率 |
|---|---|---|---|
| Rf（年化） | ~2.0%（2026 货币基金均值） | 货币基金 7 日年化收益率（如余额宝/天弘） | 月频（波动小，月频取均值足够） |
| Rf（日频） | Rf_年化 / 252 | — | 每日由年化换算 |
| R_target（Sortino 分子用） | = Rf | 同 Sharpe 分子，保持两指标可比 | — |

- **为什么用货币基金而非国债**：A 股个人账户的"无风险替代"是货币基金（T+0 可取、零信用风险），1 年期国债需锁仓不符 T+1 流动性需求；货币基金年化 ~2% 与 1 年期国债 ~1.8% 量级一致。**简化路径**：若数据管线未接货币基金收益率，可暂用固定 Rf=2.0%（2026 均值），首批策略 PnL 校准时再接实时数据——Rf 误差对 Sortino 排序影响极小（所有策略用同一 Rf，只平移不分流）

##### MAR 选型理由（0% / Rf / target 三选一）

Sortino 公式 `Sortino = (R_p − MAR) / σ_d` 中的 **MAR（Minimum Acceptable Return）** 有三种主流取值——0% / 无风险利率 Rf / 自定义目标收益率 target，实质影响 Sortino 结果（fortraders 2026-04 引 IBKR Quant）。

| MAR 取值 | 适用场景 | 对我们的影响 | 2026 实证来源 |
|---|---|---|---|
| **0%** | 资本保全 / 最小化回撤 | **过于宽松**——任何正收益日都不计入下行偏差，σ_d 偏小 → Sortino 偏高 → PerformanceScore 系统性高估，放大 downside 样本少时的 inflated values 风险 | fortraders 2026-04-30 表 / wallible 2026-03 |
| **Rf（~2%，我们的选择）** | 跑赢无风险被动投资；**机构默认** | **正合适**——"策略必须跑赢货币基金才算合格"，下行偏差只统计"跑输无风险利率"的日子。这是 Sortino 原始论文（Frank Sortino 1980s）的意图 | icalculators 2026-06 / portfolioslab 2026-03 / schwab 2024 |
| **target（如 9% 利润目标）** | 跟踪特定业绩目标（prop firm 挑战赛） | **不适用**——个人量化系统无外部利润目标，target 选值无客观依据（5%? 10%? 15%?），引入主观偏差 | fortraders 2026-04-30 表 |

**决策：MAR = Rf（~2%）**。理由：① **Sortino 原始意图**——MAR 是"策略的被要求收益率"（Schwab 2024 引 Frank Sortino 原始论文），对个人量化系统 = 至少跑赢 cash 替代（货币基金）；② **与 Sharpe 分子一致**——两指标纯差异在分母（总 σ vs 下行 σ_d），gap 干净反映上行偏态强度（MAR≠Rf 则 gap 混入"MAR 选择差异"噪声，gap 监控失效）；③ **避免 0% 的 inflated values 放大**——Rf MAR 把"跑输 cash"的日子也算下行，σ_d 更稳健；④ **避免 target 主观偏差**——Rf 有市场数据客观可查；⑤ **机构默认**——icalculators 2026-06"MAR often set to Rf for pensions"。✅ 代码侧已实现（`MAR_ANNUAL=0.02`），**禁止**用 0% 或硬编码 target 作为 MAR。

##### 熊市最低总暴露（global_shrinkage floor）

- **当前 floor**：`global_shrinkage ≥ ConfidenceSignal_min(0.3) × RiskSignal_min(0.30) = 0.09`（9%）——极端熊市（max(P)<60% + 13 参数全亮红灯）时，总暴露最低保留 9%
- **为什么 9% 而非 0**：A 股不能做空、个人账户无债券/黄金防御资产，**cash 就是防御资产**。极端熊市保留 9% 暴露用于捕捉反弹（熊市反弹往往暴力，如 2024-09 政策底单日 +8%），完全空仓 = 错过反弹 + 无法恢复 PerformanceScore。9% 是"最低侦察兵暴露"，91% cash 是防御
- **2026 资本保全研究的对照**：recessionistpro 2026-02 / brimindinvest 2026-06 / protraderdaily 2026-08 建议衰退期保留 20-35% 防御资产——但那是**多资产组合**；A 股单市场个人账户无此 sleeve，9% 暴露 ≈ 91% cash 防御，对应多资产组合的"极端防御"档位。**不需要提高 floor**：A 股熊市特征是阴跌+急反弹，低暴露高 cash 是正确防御姿态；提高 floor（如 ≥30%）反而在熊市被迫持有过多暴露，与风险节流目的矛盾

##### ⚠️ 危机态（CRISIS）覆盖说明（解决 9% floor vs 5% crisis cap 冲突）

**冲突**：本节 global_shrinkage floor = 9%（极端熊市最低暴露），而 [31号](31_position_sizing.md) §2.4.3 定义 CRISIS（⑩特殊态）总仓位上限 = 5%（9% > 5% 表面矛盾）。**决议：firm 层 5% crisis cap 优先于 meta 层 9% floor——两者不矛盾，适用于不同 regime 态：**

| 层次 | 机制 | 适用 regime 态 | 数值 | 性质 |
|---|---|---|---|---|
| **meta 层（本备忘 34号）** | `global_shrinkage floor = 0.09` | **r4 熊市**（4 态 HMM 中最差的常规态，max(P)<60% + ConfidenceSignal=0.3） | 9% | **目标值下限**（meta 层输出的 effective_budget 目标 ≥9%，策略可自然低于目标） |
| **firm 层（[31号](31_position_sizing.md) §2.4.3）** | `MARKET_REGIME_CAPS[CRISIS] = 0.05` | **⑩ CRISIS 特殊态**（D-SIGNAL-68 overlay 触发的系统性危机，非 4 态 HMM 之一） | 5% | **硬上限**（firm 层 FirmRiskAggregator 强制裁剪，不可突破） |

**关键区分**：
1. **r4 熊市 ≠ ⑩ CRISIS**：r4 是 4 态 HMM 的常规熊市态（占样本 20.2%，[11号](11_regime_backtest_validation_plan.md) §0.5.2）；⑩ CRISIS 是 D-SIGNAL-68 overlay 触发的**特殊危机态**（如 2015 股灾/2024-02 雪球敲入），频率远低于 r4。9% floor 管 r4，5% cap 管 ⑩
2. **floor 是目标下限非硬约束**：9% floor 意味着 meta 层在 r4 熊市**输出目标 ≥9%**，但策略实际暴露可低于目标（未部署完/止损离场）。floor 防"meta 层把目标压到 0 导致策略无 budget 可用"，不强制策略必须持有 9%
3. **cap 是硬上限**：5% crisis cap 是 firm 层 FirmRiskAggregator 的**强制裁剪**——当 ⑩ CRISIS 触发时，无论 meta 层 effective_budget 目标多少，firm 层总仓位 ≤5%
4. **当 r4 熊市 + ⑩ CRISIS 同时触发**：⑩ CRISIS overlay 优先级高于 r4 HMM 基态（[10号](10_regime_detector_spec.md) D-SIGNAL-68 overlay 设计），此时 firm 层 5% cap 为 binding constraint，meta 层 9% floor **自动悬空**。CRISIS 态下 `global_shrinkage` 不受 0.09 floor 约束（可降至 0.05 对齐 crisis cap），由 firm 层硬裁剪兜底

> **施工注记**：✅ 代码 `_compute_shrinkage()` 已实现 CRISIS 态分支——`is_crisis=True`（D-SIGNAL-68 overlay 触发）时 floor 从 0.09 降至 0.05（对齐 [31号](31_position_sizing.md) crisis cap），`effective_budget` 目标值 ≤0.05。非 CRISIS 态的 9% floor 逻辑不受影响。

##### 其他设计要点（保留）

- **为什么 60 日**：覆盖 ~3 个月，足以过滤单月噪声，又不至于太滞后（A 股情绪周期 2-3 个月）；**为什么 [0.5, 1.5] 而非 [0, 2]**：防极端——差策略不至于被归零（floor 5% 防饿死），好策略不至于被无限放大（cap 40% 防集中）
- **后验捕获 regime 亲和性**：momentum 在趋势态表现好→滚动 Sortino 上升→有机获得更多 budget，无需 regime 前瞻下注（[30号](30_multi_strategy_concurrency.md) §2.2 裁定）；**walk-forward 天然无前视**：60 日滚动窗口只用过去数据，与 [11号](11_regime_backtest_validation_plan.md) C1 验证的 walk-forward 协议一致
- **冷启动过渡**：策略上线 0-60 日内 PerformanceScore 无法算完整 60 日 Sortino → 过渡期用已有天数算部分 Sortino（≥30 日起算，见下方样本量要求），不足 30 日则 PerformanceScore=1.0 中性（同 §3.2.1 冷启动逻辑）
- **⚠️ Sortino 样本量要求**：Sortino 的下行偏差只统计 `R_daily < R_target` 的日子，A 股 60 交易日中下跌日约 40% ≈ 24 日。ecassets 2026-05 / foliolab 2026 警告：**下行样本不足时 Sortino 系统性偏高（inflated values）**，高估策略表现。防护四件套：
  1. **最小 downside 样本门槛**：downside 观测数 <15 时 PerformanceScore 强制 =1.0 中性（不参与 Sortino 映射）——A 股约需 38 交易日（15÷0.4）积累足够 downside 样本，冷启动过渡门槛据此从 20 日上调到 30 日（留余量）
  2. **PerformanceScore floor 兜底**：即便 Sortino 算出 ≥2.0（映射 1.5），也受 §3.2.4 cap 40% 约束
  3. **Sortino/Sharpe gap 监控**：若某策略 Sortino >> Sharpe（gap 异常大），标记为"疑似 inflated"，复核后决定是否降权
  4. **待校准**：首批策略 PnL 后，实测 downside 样本数与 PerformanceScore 稳定性，必要时上调窗口到 90 日（downside 样本 ~36 日，更稳）
- **⚠️ 60 日 vs Sortino 36 个月机构标准（重大修正）**：两个不同来源的"36 个月"须区分——
  - **来源 A：Sortino 自身的机构标准**。forex-basics 2026-05-28（evergreen verified）/ financefriend24 2026 / superglobalcalculator 2026 / getzenquery 2026：**Sortino 机构标准 = 36 个月（~540 交易日）= 我们 60 日的 9 倍**——我们 60 日远低于机构标准，是已知妥协
  - **来源 B：BestFolio walk-forward 优化器窗口**（36 个月，~780 交易日）：为 max Sharpe **优化器**稳协方差矩阵，与我们用 Sortino 做简单映射不同
  - **我们 60 日的特殊理由（A 股 + 个人系统）**：① A 股情绪周期 2-3 个月，策略 alpha 衰减快，需快速响应；② 我们用 Sortino 做 [0.5,1.5] 线性映射 + floor/cap 裁剪，**不是优化器**，短窗口噪声被裁剪缓冲；③ 个人系统策略数少（3-5 个），不需要机构级的统计稳健性；④ 60 日 downside 样本 ~24 日，配合防护四件套可控制 inflated values 风险。**已知风险**：60 日窗口 Sortino 估计误差大于机构标准——连胜期（少下跌日）Sortino 偏高 → allocation 偏大，连亏期相反；**floor/cap 是第一道防线，gap 监控是第二道防线**
  - **实盘校准触发条件**：首批策略 3-6 个月 PnL 后，若实测发现——① PerformanceScore 月度变动 >0.3（映射区间 [0.5,1.5] 的 30%）频繁出现；② 同一策略 Sortino 月度排名波动大（如本月第 1 下月第 3）；③ Sortino/Sharpe gap 监控频繁触发"疑似 inflated"——则上调窗口到 90 日（downside ~36 日）或 120 日（downside ~48 日），代价是响应变慢。**远期演进**：若 90/120 日仍不稳定，可考虑**月频 Sortino + 36 个月窗口**（完全对齐机构标准），但需策略实盘 3 年后才有足够数据——MVP 先用 60 日 + 防护四件套
- **⚠️ 加权方式决策（等权 vs EMA）**：

  | 加权方式 | 机制 | 优点 | 缺点 | 2026 实证 |
  |---|---|---|---|---|
  | **等权（MVP 选择）** | 60 日简单滚动平均，每日权重 1/60 | 简单 + walk-forward 天然无前视 + 所有日子等权无偏 | 对"近强远弱"alpha 衰减响应慢 | — |
  | **指数加权 EMA（远期候选）** | 半衰期 20-30 日，近期权重指数衰减更高 | 对 alpha 衰减响应快 | 需验证无前视（EMA 递归实现易引入前视）+ 半衰期选值主观 | volity 2026-06 EMA 趋势市 55-60% 胜率 + ctrl-trade 2026-06 EMA-50 filter 20 年回测 Sharpe 0.93 |

  **决策：MVP 用等权，EMA 列远期候选**。理由：① **walk-forward 无前视优先**——等权窗口只用过去 60 日数据，天然 walk-forward；EMA 递归实现易引入前视（初始化用全样本均值、α 选值用未来数据优化）；② **floor/cap 缓冲短窗口噪声**——不需要 EMA 的"近期权重"快速响应；③ **EMA 不是"更好"而是"不同"**——volity 2026-06 实证 EMA 趋势市 55-60% 胜率但 SMA 震荡市更稳，A 股 regime 切换频繁，EMA 可能过度响应 regime 噪声。**EMA 升级触发条件**：首批策略 PnL 后若发现——① 策略表现有"近强远弱"衰减特征；② PerformanceScore 月度变动 >0.3 频繁但等权响应滞后——则升级到 EMA（半衰期 20-30 日，选值用 walk-forward CV 优化，禁止全样本优化防前视）。

- **⚠️ 多策略 PerformanceScore 同向变动说明**：当 regime 切换（如 r3 牛市→r4 熊市）时，**所有策略的 Sortino 可能同时下降** → 所有 PerformanceScore 同时降低 → normalize 后 allocation 比例可能几乎不变。**这是 feature 不是 bug**：① PerformanceScore 的设计意图就是"后验捕获 regime 亲和性"——所有策略同向变动说明 regime 影响是"市场级"而非"策略级"，此时 allocation 比例稳定是正确的（市场级切换不重定向资金，RegimeScore alpha 择时已被 §2.2 裁定拒绝）；② **"多谨慎"由 global_shrinkage 回答**——regime 切换时 global_shrinkage 降低 → effective_budget = allocation × global_shrinkage 整体同比例收缩，正是 allocation/global_shrinkage 解耦设计的体现；③ **floor/cap 防同向极端**仍生效；④ 打板策略 Sortino 波动远大于多因子，**实际同向变动不会完全同步**（完全同步只在"所有策略对 regime 同等敏感"时发生，实际不会）。

- **待校准**：映射区间 [0.5, 1.5] 和窗口 60 日待首批策略 PnL 后验证；可能需按策略类型差异化窗口（打板用 30 日，多因子用 90 日）；Sortino vs Sharpe 的实测 gap 待首批 PnL 后复核选型；**冷启动贝叶斯收缩（远期候选）**——MRC（arXiv:2605.24490, 2026-05-23）用贝叶斯自适应混合 `score = w_prior × 1.0 + w_data × Sortino_score`，权重 `w_data ∝ 样本量` 随数据积累渐变（而非硬切换），比我们 30 日阈值切换更平滑。MVP 不采纳（30 日阈值 + floor/cap 兜底已足够，贝叶斯收缩增加先验分布假设复杂度），待首批 PnL 证明冷启动期权重跳变成问题后再评估

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
- **shrinkage_enabled 开关**：代码已有，C1 验证一票否决机制——若 Shrinkage 无效则 `shrinkage_enabled=False`，`global_shrinkage=1.0` 回退等权。**待校准**：四档阈值 60/80/95% 的 D1 ±20% 敏感性网格未跑（[11号](11_regime_backtest_validation_plan.md) §0.5.7），当前值是 [30号](30_multi_strategy_concurrency.md) §2.2 启发式设定
- **60% 阈值的外部印证**：1uptick 2026-06 机构方案明确"when no single regime probability exceeds **60%**—automatically reduce position sizes by 30-50%"——与我们 max(P)<60%→强收缩的阈值**完全一致**，60% 是行业共识的"regime 不确定"临界点。**我们 0.3 更激进的理由**：1uptick 减的是"position sizes"（可日内调整），我们 0.3 减的是"global_shrinkage"（总暴露）——A 股 T+1 不能日内快速止损，不确定时需更保守的预防性收缩；且实际 Shrinkage = 0.3 × RiskSignal（不确定时也 <1.0），叠加后更保守
- **Shrinkage 更新频率**：ConfidenceSignal 随 regime 检测日频更新（HMM 日频推理，[10号](10_regime_detector_spec.md)）；RiskSignal 13 参数中 realized_vol/量价等日频、新闻情绪盘内更新。global_shrinkage 日频重算，盘中 regime 突变（如 D-SIGNAL-68 overlay 触发）可盘中重算
- **Quarter Kelly 与 Shrinkage 节流的同构印证**：pooyagolchian 2026-04《Portfolio Risk Management》实证 fractional Kelly 的风险预算折扣收益（2026 年真实数据）——

  | 策略 | 风险预算折扣 | CAGR | MaxDD | 与 Full Kelly 比 |
  |---|---|---|---|---|
  | Full Kelly | 1.0× | 18.2% | −62% | 基准 |
  | Half Kelly | 0.5× | 14.1% | −38% | 77% 增长 / 61% 回撤 |
  | **Quarter Kelly** | 0.25× | 10.8% | −22% | **59% 增长 / 35% 回撤** |
  | Risk Parity 基线 | — | 9.2% | −18% | 50% 增长 / 29% 回撤 |

  核心结论："Quarter Kelly delivers 85% of full Kelly's growth with only 35% of the drawdown"。这与我们的 Shrinkage 节流**同构**——Shrinkage 把总暴露从 1.0 缩到 0.21-1.0，本质就是 regime 驱动的 fractional 风险预算折扣。区别：Kelly fraction 基于胜率/赔率（收益端估计），Shrinkage 基于 regime 置信度+风险参数（风险端推断，不依赖收益预测，规避了 Kelly 对估计误差极敏感的缺陷，见 §4.5）。两者共享同一规律：**适度收缩风险预算 → 以小得多的回撤代价获得大部分增长**——这是 §2.2 "regime 做风险节流而非 alpha 择时"裁定的实证支撑。我们的 9% 熊市 floor（§3.2.2）对应"不低于 Quarter Kelly 量级的最低风险敞口"

#### ⑤ floor≥5% / cap≤40% → §3.2.4

**决策**：归一化后硬约束，floor 5% 防饿死 + cap 40% 防集中。

| 约束 | 值 | 防什么 | 代码 |
|---|---|---|---|
| floor | ≥5% | 单策略被 PerformanceScore×Shrinkage 压到 0（饿死）→ 永远无法翻身 | `FLOOR=0.05` |
| cap | ≤40% | 单策略霸占 budget（集中）→ 多策略分散化失效 | `CAP=0.40` |

- 实现：✅ 代码 `_normalize_and_clip()` 用 **water-filling 投影**（固定越界值 + 按比例重分配未越界部分，避免被裁剪值在再归一化时拉回越界区间——比原"裁剪+全局再归一化"伪代码更稳，见 §9 v2.7.0）。**⚠️ floor/cap 无解兜底**：floor+cap 约束在策略数 N 较小时可能**数学无解**——如 N=2 + floor=5% + cap=40%：两策略都 ≥5% 且 ≤40%，Σ=1.0 → 一个 ≥60% 必然违 cap。无解场景的兜底（参考 AIMS Mathematics 2026, 11(2):3647 Lkhagvasuren et al. feasibility restoration 思想——当约束无解时找"最近可行解"）：
  1. **检测无解**：迭代 5 次仍未收敛（仍有策略越界）→ 判定 floor/cap 在当前 N 下无解
  2. **优先保 floor 降 cap**：floor 是"防饿死"的生存线（不可降），cap 是"防集中"的优化线（可降）→ 自动放宽 cap 到 `1 − (N-1)×floor`（如 N=2 + floor=5% → cap 放宽到 95%）
  3. **日志告警**：无解兜底触发时 log WARNING + 上报 firm 层 [32号](32_firm_risk_aggregator.md)，标记"策略数过少导致分散化失效"，提示人工评估加策略或调 floor
  4. **N≥3 时基本不触发**：N=3 + floor=5% + cap=40% → 最小 Σ=15%、最大 Σ=120%，Σ=1.0 必有解。**无解兜底主要为 N=2 边缘情况设计**，MVP 首批 3 策略不触发
- **cap 40% 的外部印证**：BestFolio 2026-04 walk-forward 明确用 "Max weight per strategy: **40%**"——与我们 CAP=0.40 **完全一致**；**GATE-WPCA-PI**（AIMS Mathematics 2026, 11(2):3647-3702）"entropy floor"+"sleeve caps" 与我们 floor 5%/cap 40% 同构，2026 年学术级印证。**待校准**：5%/40% 是行业经验值（多策略基金单策略通常 5-30%），首批策略数确定后校准（3 策略时 cap 可放到 40%；5 策略时 cap 可降到 30%）

#### ⑥ 稀有态差异化收缩 → §3.2.5

**决策**：按态频率差异化收缩（[30号](30_multi_strategy_concurrency.md) §2.2）：常见态 >5% 轻收缩 / 中等态 1-5% 中度收缩 / 稀有态 <1% 重收缩——稀有态检测置信度天然低。

- **4 态下的实际情况**：r1=27.6% / r2=37.4% / r3=14.9% / r4=20.2%——**全部是常见态（>5%），无 <1% 稀有态**。**结论**：稀有态机制在当前 4 态下基本不触发，是为原 12 态设计的向前兼容机制
- **保留理由**：若未来基于证据加态（如 [11号](11_regime_backtest_validation_plan.md) §0.6.9 层次 HMM 升级路径），稀有态机制自动生效，无需重写。**不是过度工程**：该机制是 Shrinkage 计算内的一个条件分支，代码量极轻，保留无成本

##### 12 态→4 态退化映射

> **问题背景**：Shrinkage 的 ConfidenceSignal 四档、稀有态差异化收缩最初按"12 态 regime"设计；但 [11号](11_regime_backtest_validation_plan.md) §0.5.2 C1 验证实测 HMM 按 BIC/AIC 信息准则选优后**稳定收敛到 4 态**，原 12 态的多数子态未被区分。必须明确 4 态如何吸收原 12 态语义，否则"按态收缩"会因态数不匹配而悬空。

**退化映射的 why（设计原则，非精确查表）**：

| 退化原则 | 说明 | 为什么 |
|---|---|---|
| **按波动族合并** | 原设计的高/中/低波动子态 → 合并到 r1（低波）/r2（中波） | 波动是 regime 检测的一阶特征，细分子态在日频上不可靠区分（A 股情绪周期 2-3 个月，子态持续时间 <1 个月易被噪声淹没） |
| **按趋势方向合并** | 原设计的上涨/下跌主趋势 → 合并到 r3（牛市）/r4（熊市） | 趋势方向是 regime 的二阶特征，4 态已覆盖"牛/熊/低波/中波"四象限，进一步细分对 Shrinkage 收缩系数的差异化无统计意义 |
| **稀有态机制冻结** | 原 12 态中 <1% 的"危机闪崩态"等 → 当前 4 态无对应（全部 >5%），稀有态分支**不激活但不删除** | 冻结而非删除是为层次 HMM 加态（[11号](11_regime_backtest_validation_plan.md) §0.6.9）时自动复用；删除则未来加态需重写 Shrinkage 查表逻辑 |

**当前实现行为**：4 态全部走"常见态 >5% 轻收缩"分支，稀有态分支死代码（保留但不执行）。ConfidenceSignal 四档阈值（60/80/95%）作用于 max(P），与态数无关——**退化不影响 ConfidenceSignal 计算**，只影响"按态频率差异化收缩"这一子分支。**施工注记**：12 态→4 态的**精确状态 ID 映射表**归 [10号](10_regime_detector_spec.md) regime 检测器文档定义（那里管 HMM 状态语义），本备忘只管"Shrinkage 如何消费 4 态输出"；精确查表待 [10号] 校准（见 §6 待裁定）。

#### ⑦ 第二阶段上线时机 → §3.2.6

**决策**：[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §4.2 演进路径——**各策略有 3-6 个月实盘 PnL 后**上加 RegimeMetaAllocator。

| 门槛 | 状态 | 说明 |
|---|---|---|
| C1 验证（Shrinkage 有效性） | ✅ 已通过（commit 852457e9） | 核心假设成立，Shrinkage 节流有效 |
| 首批策略 PnL（PerformanceScore 输入） | ❌ 未就绪 | 策略未实盘，无 60 日 Sortino |
| 四档阈值 D1 敏感性校准 | ❌ 未跑 | [11号](11_regime_backtest_validation_plan.md) §0.5.7 待完成项 |

- **第一阶段（当前）**：纯 A 模型，各策略等权或先验比例 budget 固定不变，FirmRiskAggregator 只做求和+裁剪（[30号](30_multi_strategy_concurrency.md) §4.2）；**第二阶段（策略 3-6 个月 PnL 后）**：上加 RegimeMetaAllocator，按 PerformanceScore 动态调占比 + Shrinkage 节流
- **过渡方案**：在 PnL 积累期内，可用 `Base × Shrinkage`（PerformanceScore=1.0 中性）先跑——regime 节流已验证有效，只是没有后验分配

#### ⑧ 外部信号交叉验证（5 档水温 + 板块轮动状态）→ §3.2.7

> **为什么需要交叉验证**：HMM regime 检测基于收益+波动统计量，是"后验状态推断"——不直接告诉你"市场结构性水温"。Wyckoff-Analysis 实证（[YoungCan-Wang/Wyckoff-Analysis](https://github.com/YoungCan-Wang/Wyckoff-Analysis) v2.1.x，2026-04）提供两个**独立于 HMM 的外部信号**——大盘水温（5 档）与板块轮动状态（5 分类）——可与 HMM 4 态交叉验证，作为 Shrinkage 的辅助印证而非主信号。

**信号 A：大盘水温 5 档仓位（Wyckoff-Analysis 2026-04 实证）**：NEUTRAL（均线健康，正常市况）100% / RISK_ON（短线过热）50% / PANIC_REPAIR（暴跌后修复，方向未确认）50% / RISK_OFF（均线破位）30% / CRASH（系统性危机）0%；实测 NEUTRAL **+1.17%（唯一正收益）** / RISK_ON −1.54% / CRASH −3.2%。

**信号 B：板块轮动状态 5 分类（WyckoffTradingAgent 2026-04 实证）**：CONSENSUS_CLIMAX（共识高潮，多板块同时暴涨）watch_score −0.15 警惕见顶 / DISAGREEMENT_PULLBACK（分歧回调）+0.01 / HEALTHY_MAINLINE（健康主线）+0.03 / DISTRIBUTION_RISK（派发风险，领涨板块高位放量滞涨）−0.10 **最危险状态** / NEUTRAL_MIXED（中性混沌）0；实证：共识高潮后 3 日下跌 >2% 概率达 29.8%，派发风险扣分有据可依。

**交叉验证的定位（远期候选，不进 MVP 主链路）**：

| 维度 | 当前 MVP（4 态 HMM Shrinkage） | 远期（外部信号交叉验证） |
|---|---|---|
| 主信号 | HMM 4 态 + RiskSignal 13 参数 | 不变（HMM 仍是主信号） |
| 辅助信号 | 无 | 5 档水温 + 板块轮动状态作为 Shrinkage 的**印证/校验**，不替换 |
| 作用方式 | — | 当 HMM 判 r3（牛市）但水温=RISK_ON + 板块=CONSENSUS_CLIMAX → 信号冲突 → 触发 ConfidenceSignal 降档；当两者一致 → 增强 ConfidenceSignal |
| 为什么不进 MVP | C1 已证明纯 HMM Shrinkage 有效（MaxDD 改善 7.36pp），无需叠加外部信号增加复杂度 | 外部信号的数据管线未接入；冲突仲裁规则需实盘验证后才能定 |

> **与 RMATS 的解耦思想印证**：RMATS（arXiv:2605.25311, 2026-05-25）的 Risk Agent 独立于策略 agent——我们的 regime Shrinkage 同样是独立于策略层的风险节流层，外部信号可作为**风险层的多源输入**，但**不引入 RMATS 的多 agent 递归架构**（见 §4.4）。**过度工程审查**：定位为"远期辅助印证"——只在 HMM 与外部信号冲突时触发 ConfidenceSignal 降档（保守化），一致时不增强（避免过度乐观）。是否启用待首批策略实盘后校准（见 §6 待裁定）。

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
- **下游**：BudgetAllocation 发给 StrategyBook；budget 下调时触发 [BudgetChangeHandler](33_budget_change_handler.md)（33号）三级升级（33号 §3.2；✅ 33号 已于 2026-08-12 重建为 active v1.0.0——commit 6a4f5392，依 MOD-POS-022 production 代码回建）
- **正交性**：本模块只管"budget 怎么算 + 怎么分配"，不管"budget 下调怎么落地"（归 33号）、"单策略内仓位怎么算"（归 [31_position_sizing](31_position_sizing.md)）、"firm 层求和裁剪"（归 [32_firm_risk_aggregator](32_firm_risk_aggregator.md)）
- **effective_budget 是目标值非强制值**：RegimeMetaAllocator 产出 `effective_budget = allocation_i × global_shrinkage` 是**目标预算**，StrategyBook 的实际暴露可能 ≠ 目标（未部署完/已超配）。实际暴露低于目标→策略可自然加仓；实际暴露高于目标→budget 下调，触发 [33号](33_budget_change_handler.md) 三级升级收敛。两者差异是常态，不是 bug
- **更新频率**：effective_budget 日频重算（PerformanceScore 60 日滚动日频更新 + Shrinkage 日频更新）；盘中 regime 突变（D-SIGNAL-68 overlay 触发）时盘中重算 Shrinkage → effective_budget。日频更新意味着 budget 可能日频变动，这正是 [33号](33_budget_change_handler.md) §3.3 防抖双层的必要性来源

### 3.4 施工算法实现（allocate 完整伪代码）

✅ **已施工 production**：完整施工算法已落地于 [regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py) MOD-PA-007（v1.0.0）——`allocate()` 主入口 5 步流程（PerformanceScore → global_shrinkage → raw_allocation → normalize+clip → effective_budget）、`_compute_sortino_and_sharpe()`（MAR=Rf + downside 样本量门槛 + gap 监控）、`_compute_confidence_signal()`（max(P) 四档）、`_compute_risk_signal()`（13 参数占位，逻辑归 [10号]）、`_normalize_and_clip()`（**water-filling 投影**，施工中将原"裁剪+全局再归一化"伪代码升级为固定越界值+按比例重分配未越界部分，避免 N=2/cap 受限场景收敛扭曲）。`BudgetAllocation` dataclass 含 allocations / global_shrinkage / effective_budgets / confidence_signal / risk_signal / perf_scores / sortino_sharpe_gaps 审计字段。

**施工要点（已随代码落地的口径裁定，代码本体为真源）**：
1. **MAR=Rf 硬约束**：`MAR = Rf = 0.02`（货币基金年化），确保 Sortino 与 Sharpe 分子一致，gap 干净反映上行偏态强度。
2. **downside 样本量门槛**：`downside_count < 15` 时 PerformanceScore 强制 1.0 中性。
3. **gap 监控两级阈值**：gap > 1.8 → 疑似 inflated 警告；gap > 2.25 → 严重 inflated 强制降权复核。
4. **global_shrinkage 与 allocation 解耦**：`raw_allocation = Base × PerformanceScore`（不含 Shrinkage）——全局 Shrinkage 归一化时约掉，只在 `effective_budget = allocation × global_shrinkage` 层缩放总暴露。
5. **floor/cap N=2 无解兜底**：迭代 5 次仍未收敛 → 优先保 floor 降 cap 到 `1-(N-1)×floor`（§3.2.4）。N≥3 时基本不触发。
6. **冷启动过渡**：上线 <30 交易日 → PerformanceScore=1.0 中性；≥30 日且有足够 downside 样本 → 起算部分 Sortino；60 日完整窗口 → 正常 Sortino 映射。
7. **RiskSignal 13 参数归 [10号]**：`_compute_risk_signal()` 是占位接口，本备忘只管消费（clamp[0.30, ..., 1.00] + 与 ConfidenceSignal 乘法）。
8. **ConfidenceSignal 四档阈值待 D1 校准**：当前 60/80/95% 是启发式设定，D1 ±20% 敏感性网格未跑（[11号] §0.5.7）。若 D1 显示某档边界是悬崖型，需调整阈值。
9. **days_live 交易日口径**：用 `trading_days_live = len(returns)`（交易日数），与 COLD_START_MIN_DAYS=30 交易日口径一致——自然日口径（30 自然日 ≈ 20-22 交易日）会导致冷启动过早脱离。
10. **ddof 一致性**：Sortino downside deviation 与 Sharpe total deviation 均用 ddof=1（样本估计），确保 gap 监控 apples-to-apples。本项目 gap 监控要求 Sortino/Sharpe 同 ddof 才可比。
11. **gap 常量语义**：`GAP_NORMAL_CEILING=1.5` 是"正常 gap 上限"，乘子 1.2/1.5 是"超出正常范围的严重程度分级"。
12. **CRISIS 态分支**：`is_crisis=True` 时 floor 从 0.09 降至 0.05，否则 meta 层目标值虚高（9% vs firm 层实际 5%）导致 [33号] BudgetChangeHandler 收敛异常。✅ 已实现。
13. **⚠️ Sortino 下行偏差分母修复（CRITICAL bug 修复）**：下行偏差分母用 `max(n-1, 1)`（**总样本量** n-1，ddof=1 与 Sharpe 一致），**非** `n_downside-1`（仅下行观测数）——后者是常见实现错误（CFA Institute 2026 共识 + arXiv:2510.12725 引证 + quantt.co.uk 2026-04 独立验证"divide by the total number of observations (N), not just the number of below-target ones"），人为抬高 Sortino（例：n=60, n_downside=24 → Sortino 虚高 √(59/23)≈1.6x）。分子仍只对 `R < MAR` 的日子求和。
14. **⚠️ Bootstrap CI 远期候选（CRITICAL 修正：BCa → stationary block bootstrap）**：当前防护四件套是**点估计 + 规则防护**。arXiv:2510.12725（Oliveira et al. 2025-10）提出非参数 bootstrap 鲁棒优化——用 bootstrap 重采样构造 Sortino 的 95% 置信区间。**升级路径**：若首批策略 PnL 后发现 PerformanceScore 月度变动 >0.3 频繁（§3.2.2 实盘校准触发条件），将 PerformanceScore 从"点估计映射"升级为"bootstrap 5% 下分位（保守估计）映射"。**不进 MVP**（~100ms 计算开销 + 复杂度），作为四件套防护的升级路径登记。**正确方案：stationary block bootstrap（Politis-Romano 自动块长），非 BCa**——Soloviov 2026-06 6000 次受控实验证明 BCa 仅在 iid 下有效（覆盖率 0.954），AR(1) φ=0.3 自相关下失效（0.838 vs 名义 0.95）；block bootstrap 保留序列内依赖结构，AR(1) 下覆盖率恢复 0.946。BCa 保留为 ≥252 日窗口且收益近似 iid 时的长窗口选项。**CI_TOO_WIDE 守卫**（Pancake Engine 2026-05 / Ding & Martin 2017）：当 `(ci_high - ci_low) / |point_estimate| > 5.0` 时该 PerformanceScore 不可信，触发更强 Shrinkage。
15. **⚠️ PerformanceScore 选择偏差收缩远期候选（James-Stein 估计器）**：PerformanceScore 的实际用途是策略间相对排序+差异化分配（构成"选择"操作）。Pav《Post-Selection Estimation of Sharpe Ratios》(arXiv:2606.01650v1, 2026-06-02) 系统测试 5 种修正估计器，**结论：James-Stein 估计器在多数现实参数下最优**（紧随其后是 GMLEB 经验贝叶斯），收缩因子 `s = (1 - (k-2)·σ²/||ζ̂||²)₊`（positive-part，k=策略数≥3 时生效），把每个策略的 Sortino 往横截面均值收缩——离群高 Sortino 被拉回最多。与 34号 的关联：① N=3-5 策略满足 k≥3；② 四件套是**单策略绝对值防护**，James-Stein 是**多策略相对值防护**，两者正交互补；③ 实现成本极低（~20 行），不换框架。**不进 MVP**（收缩因子需实盘数据校准），若实盘后发现"上月 Sortino 最高的策略本月虚高→次月反转"（选择偏差表征），James-Stein 收缩是第一修正路径。
16. **⚠️ Block-wild Bootstrap 评估·过度工程纠偏**：**评估结论：不采纳，登记为已评估的过度工程**。依据 Soloviov 2026-06 受控实验：**"GARCH 与 regime 波动率对 Sharpe 覆盖率损害很小"**——stationary block bootstrap 在 GARCH(1,1) 和 Markov regime-switching 下覆盖率接近 nominal（无需 wild 权重修正），仅 AR(1) 自相关是主要损害源且 stationary block bootstrap 已修复（0.838→0.946）。block-wild 的异方差修正收益边际、实现复杂度增加，**不符合 MVP 简洁原则**。保留为"若未来发现 bootstrap CI 在 GARCH 区间系统性偏窄"时的备选升级路径，但不预施工。

### 3.5 已施工设施盘点（通用规则 #11）

> 扫描基线：2026-08-12 工作树 + git 历史取证。

| 设施 | 路径 / 标识 | 状态 | 备注 |
|---|---|---|---|
| **主模块代码** | [regime_meta_allocator.py](../../../../src/zephyr/pf_alloc/core/regime_meta_allocator.py)（MOD-PA-007） | ✅ production v1.0.0（MATURITY=production，commit 81c7687540 已提交） | `allocate()` 5 步流程 + `_compute_shrinkage()`（含 CRISIS floor 降级 0.09→0.05）+ `_normalize_and_clip()`（water-filling 投影）+ `compute_performance_score()` 静态方法（Sortino→[0.5,1.5]）全部落地 |
| **模块蓝图** | [blueprint.md](../../../../docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md) | ✅ 存在 | MODIFY-GUARD 锚点 |
| **测试套件** | [test_regime_meta_allocator.py](../../../../tests/pf_alloc/test_regime_meta_allocator.py) | ✅ **已重建**（2026-08-15，AI-REGIME-001，两轮 55/55 全绿） | 原 55 用例 2026-08-11 git 灾难丢失（从未提交、`git clean -fd` 删除、不可恢复）；按 §3.4 伪代码 16 条施工要点 + 代码本体回建，组织保持原结构 8 类 55 用例（TestConfidenceSignal 8 / TestRiskSignal 4 / TestShrinkage 7 / TestNormalizeAndClip 8 / TestRawAllocation 3 / TestAllocate 9 / TestComputePerformanceScore 8 / TestEdgeCases 8），重建后立即提交 git 闭环 |
| **错误契约** | AllocationError（ZA-PA-0007）/ ShrinkageDisabled（ZA-PA-0008） | ✅ 已在代码定义 | `shrinkage_enabled=False` 时 `global_shrinkage=1.0` 回退等权（C1 一票否决机制） |
| **上游·regime 检测器** | [regime_detector.py](../../../../src/zephyr/regime/core/regime_detector.py)（MOD-REGIME-001）+ [risk_signal_builder.py](../../../../src/zephyr/regime/risk_signal_builder.py) | ✅ 已施工（commit 191a17432f） | 产出 7 维概率（4 HMM 基态 + 3 overlay 特殊态）+ RiskSignal 13 参数 |
| **上游·C1 验证资产** | `logs/c1_repro/c1_repro_report.md` + `c1_metrics.json` | ✅ 已产出（commit 852457e9） | C1 四项全通过：Sharpe 0.3678→0.3474 / MaxDD 0.2221→0.1485 / Calmar +27% / Turnover ≤2×（[11号](11_regime_backtest_validation_plan.md) §0.5.4） |
| **下游·StrategyBook** | [strategy_book.py](../../../../src/zephyr/position/core/strategy_book.py)（MOD-POS-020） | ✅ production（70 测试，[30号](30_multi_strategy_concurrency.md) §2.2） | 消费 BudgetAllocation |
| **下游·FirmRiskAggregator** | [firm_risk_aggregator.py](../../../../src/zephyr/position/core/firm_risk_aggregator.py)（MOD-POS-021） | ✅ production（54 测试） | firm 层求和裁剪；⑩CRISIS 5% 硬 cap 兜底（[31号](31_position_sizing.md) §2.4.3） |
| **下游·BudgetChangeHandler** | [budget_change_handler.py](../../../../src/zephyr/position/core/budget_change_handler.py)（MOD-POS-022） | ✅ production（47 测试）；✅ 设计文档 33号 已重建（active v1.0.0，2026-08-12 commit 6a4f5392，含 §3.2 三级升级 + §3.3 防抖双层 + §3.7 已施工设施盘点） | 收 BudgetChanged 事件，三级升级落地 |
| **同域配套模块** | [multi_strategy_capital_allocator.py](../../../../src/zephyr/pf_alloc/core/multi_strategy_capital_allocator.py)（MOD-PA-003）/ strategy_correlation_gate.py / signal_synthesis_combiner.py | ✅ production（各有测试套件幸存） | MOD-PA-003 是权重规整层（容量截断/MaxDD 减仓/冷启动缩放），与本模块正交——本模块产出"目标 budget 占比"，MOD-PA-003 做权重规整，不重复 |
| **depgraph 登记** | MOD-PA-007 | ✅ 已登记（代码头 SSoT 声明） | stability=evolving / safety=M / ai_autonomy=ai_modifiable |

**盘点结论**：代码链路（上游 regime → 本模块 → 下游 position 三模块）完整且全部 production；测试套件缺口已于 2026-08-15 重建闭环（AI-REGIME-001，55 用例两轮全绿）。无需退役/删除的设施——同域 3 个配套模块功能边界清晰不重叠。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-20-B | 多策略资金分配 | §3 三因子乘法分配（§3.1 分配公式 / §3.4 allocate 伪代码 / §3.5 已施工设施） | production 已建 |

## 4. 考虑过的替代方案（拒绝理由）

### 4.1 RegimeScore（regime 做 alpha 择时，重定向资金）—— 拒绝

- **拒绝理由**：Morwane 实证 Sharpe 1.43→0.87（**降**）。regime 择时判错 = 主动亏损；且 RegimeScore 在 meta 层重新引入估计误差放大，与 A 模型"加法替代优化器"哲学矛盾。详见 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2 裁定 + §7.4 Morwane 实证

### 4.2 MVO 统一优化器（协方差矩阵分配）—— 拒绝

- **拒绝理由**：协方差估计是研究课题（5000×5000 矩阵），A 股情绪周期切换时相关性飙升到 0.8+，优化器放大输入噪声。详见 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §3.1

### 4.3 等权固定不调（无 RegimeMetaAllocator）—— 第一阶段方案，非拒绝

- **定位**：第一阶段（当前）就用这个——各策略等权或先验比例，budget 固定不变。**不升级的理由不成立**：C1 已证明 Shrinkage 节流有效（MaxDD 改善 7.36pp），第二阶段有 PnL 后升级到 RegimeMetaAllocator 有明确收益

### 4.4 复杂 RL/动态优化分配器 —— 拒绝

- **拒绝理由**：过度工程。三因子乘法 + floor/cap 是最简方案，O(N) 复杂度。RL 分配器需训练、调参、监控，且黑箱不可解释。misango 2026-03 实证：简单方案（60/40）在交易成本后优于复杂 ML 方案

### 4.5 Kelly Criterion / Black-Litterman —— 拒绝

- **Kelly Criterion**：按胜率/赔率最优下注。拒绝理由——A 股策略胜率/赔率估计误差大（情绪市波动剧烈），Kelly 对估计误差极敏感（稍有偏差即过度集中或过度保守），需 Kelly fraction（如 1/4 Kelly）打折扣到与三因子乘法无本质差异
- **⚠️ Conformal Kelly 远期精炼（不推翻 Kelly 拒绝但登记精炼路径）**：Ryan《Conformal Kelly》(arXiv:2608.01494v1, 2026-08-02) 提出**用保形预测区间宽度作为 fractional Kelly 的 σ**（`f* ≈ μ/σ²`，σ 取自 75% 保形区间半宽）——区间变宽→缩仓，区间变窄→加仓。开发窗口（2016-2021）年化净对数增长 28.5%、Sharpe 1.34、MaxDD 27.7%；风险控制层 MaxDD 27.7%→20.3%。**关键设计原则**：最简单的"慢、无权重、逐资产 rolling 保形分位数"胜过所有快速自适应方案。**但样本外增长未保持**（2022+ 校准保持 0.745 vs 0.750 目标，但增长仅 8.5%/7.0% 低于被动基准），警示"开发窗口过拟合到特定 regime"风险。与 34号 的关联：① Conformal Kelly 直击"Kelly 对估计误差敏感"这一拒绝理由（保形区间提供有限样本分布无关的覆盖率保证）；② 是**单策略仓位尺寸**（属 [31号] PositionSizing scope），非 meta 层多策略分配。**结论**：不推翻 Kelly 拒绝（仍是 Kelly 族，σ 敏感本质未变），登记为 [31号] Phase 4+ 单策略仓位尺寸远期精炼路径——**触发条件**：首批策略实盘后若 [31号] fractional Kelly 出现"σ 估计不稳致仓位抖动"且保形区间能提供更稳定宽度则评估。
- **Black-Litterman**：先验市场均衡 + 后验观点融合。arxiv 2410.14841 用 BL+regime 信号 IR 0.05→0.4，但 BL 需协方差矩阵（A 股情绪周期相关性飙升问题未解决，见 [30号](30_multi_strategy_concurrency.md) §3.1）+ 观点矩阵（需人工设定"观点"，个人系统无人值守无观点来源）。三因子乘法的 Base×PerformanceScore 已实现"先验+后验融合"且无协方差依赖，是 BL 的轻量替代

## 5. 上限定义（Ceiling）

### 5.1 系统上限

三因子乘法（Base × PerformanceScore × Shrinkage）+ floor/cap 是 meta 层分配的上限。不堆优化器（MVO/RL）、不堆因子（RegimeScore 已移除）、不堆档位（四档足够，见 §6 过度工程审查）。

### 5.2 演进路径

- **第一阶段（当前）**：纯 A 模型，等权/先验固定 budget，FirmRiskAggregator 求和裁剪
- **第二阶段（策略 3-6 个月 PnL 后）**：上加 RegimeMetaAllocator，PerformanceScore 动态调占比 + Shrinkage 节流
- **远期（可选）**：状态条件协方差 RARP（[11号](11_regime_backtest_validation_plan.md) §0.6.7 华安证券 RARP）——从"缩放 budget"升级到"按状态重估风险结构"。但本项目定位是"风险节流器"（防御性），RARP 是组合优化器（进攻性），当前不在 scope
- **远期（可选）·MPC 多期预测路径**：Nystrup/Boyd/Lindström/Madsen《Multi-period portfolio selection with drawdown control》（Annals of Operations Research 2019）——Model Predictive Control 动态优化，基于多变量 HMM 的多期收益均值/协方差预测，**根据已实现回撤调整风险厌恶系数**（realized drawdown → γ 动态）。核心机制：每个时点求解开环约束优化，只执行首步控制动作，新观测到达后重算（receding horizon）。实证：以小或无 mean-variance 效率牺牲控制回撤。

  | 维度 | 当前 Shrinkage（MVP） | MPC 多期预测（远期） |
  |---|---|---|
  | 优化方式 | 单期缩放（global_shrinkage × allocation） | 多期滚动优化（预测 H 期，执行 1 期） |
  | 回撤控制 | 静态四档 ConfidenceSignal（max(P) 映射） | 动态风险厌恶（realized drawdown → γ 自适应） |
  | 预测输入 | HMM 当前态概率（max(P)） | HMM 多期均值/协方差预测（forward prediction） |
  | 复杂度 | O(N)，无协方差 | 需多变量 HMM 多期预测 + 凸优化求解器 |
  | 为什么不进 MVP | C1 已证明静态 Shrinkage 有效 | MPC 需 HMM 多期预测管线（未建）+ 凸优化求解器 + 多期协方差估计（A 股情绪周期相关性飙升问题未解，见 [30号](30_multi_strategy_concurrency.md) §3.1）；机构级方法，当前规模不需要 |

  **MPC 对 Shrinkage 的启发（可先吸收思想不换架构）**："根据已实现回撤动态调整风险厌恶"可作为四档 ConfidenceSignal 的**未来增强**——不是静态 max(P) 映射，而是叠加 realized drawdown 反馈（如当前回撤已 >10%，即使 max(P) 高也强制降档）。可在不引入完整 MPC 框架的前提下，作为 §3.2.7 外部信号交叉验证的"回撤通道"实现。完整 MPC 框架待 [11号] §0.6 层次 HMM 升级 + 协方差估计问题解决后评估

- **远期（可选）·Statistical Jump Model（JM）路径**：Shu-Yu-Mulvey《Downside risk reduction using regime-switching signals: a statistical jump model approach》（Journal of Asset Management 25(5):493-507, 2024；arXiv:2402.05272）提出 **Statistical Jump Model（统计跳跃模型，JM）**——与传统 Markov-switching HMM 的根本区别是**显式跳跃惩罚（jump penalty）λ**：每次状态转换付出 λ 代价，从而**增强 regime 持续性**（persistence），抑制 HMM 高频状态抖动。JM 用动态规划 + 坐标下降交替迭代特征质心与状态路径，**特征集仅需收益序列衍生指标**（DD_10 + Sortino_20 + Sortino_60 三维），无需协方差矩阵。实证：US/Germany/Japan 1990-2023 含交易成本+执行延迟，JM-guided 策略在波动率、MaxDD、Sharpe 上**全面优于 HMM-guided 与 buy-and-hold**。

  | 维度 | 当前 HMM 4 态（MVP） | Statistical Jump Model（远期） |
  |---|---|---|
  | regime 持续性 | HMM 转移概率隐式决定（无显式约束） | **显式 jump penalty λ 控制转换频率**——λ 越大 regime 越持久，直接对抗 HMM 高频抖动 |
  | 特征集 | 收益+波动统计量（HMM 输入） | DD_10 + Sortino_20 + Sortino_60（**与我们 PerformanceScore 的 Sortino 同源**——JM 直接消费 Sortino 特征做 regime 推断） |
  | 协方差需求 | 无（Shrinkage 只用 max(P) + RiskSignal） | 无（JM 仅用单资产收益衍生特征，不估协方差） |
  | 状态数 | 4 态（BIC 选优，[11号](11_regime_backtest_validation_plan.md) §0.5.2） | 2 态（Bull/Bear，JM 原始）/ 3 态（Cortese-Kolm-Lindström 2026 信息准则选优 MSCI）/ 4 态（Snow-Ouyang 2026 stress-aware） |
  | 复杂度 | HMM EM 训练 + 前向推理 | 动态规划 + 坐标下降（O(T·K)，T=样本长度，K=状态数） |
  | 为什么不进 MVP | C1 已证明 HMM 4 态 Shrinkage 有效（MaxDD 改善 7.36pp） | JM 需重写 regime 检测器（[10号](10_regime_detector_spec.md)），C1 验证基于 HMM 须重跑 |

  **JM 对 Shrinkage 的三个关键启发（可先吸收思想不换架构）**：① **regime 持续性是回撤的一阶决定因素**（arXiv:2603.04441《Explainable Regime-Aware Investing》实证"regime inference stability—particularly identity preservation—is a first-order determinant of portfolio drawdown"）——我们的 HMM 4 态无显式持续性约束，可在 [10号](10_regime_detector_spec.md) 加"最小 regime 持续期"约束（如最少 5 个交易日才允许状态切换），等价于离散版 jump penalty，无需换 JM 框架；② **Sortino 特征双重用途**——JM 用 Sortino_20/Sortino_60 做 regime 推断输入特征，与我们 §3.2.2 PerformanceScore 的 60 日 Sortino 同源（中金 CICC 2026-06 实证 JM + Sortino 特征使三资产风险平价 MaxDD -7.07%→-3.23%、卡玛比率 0.77→1.59），印证"Sortino 既能做 regime 检测又能做 PerformanceScore"的双重价值；③ **JM-MPC 混合框架**（Li et al. 2025《Regime-Switching Asset Allocation Using a Framework Combining a Jump Model and Model Predictive Control》, Mathematics 13(17):2837）——JM 识别 regime + MPC 滚动优化，是"换 regime 检测器 + 换优化器"的双重远期升级路径。

  **中金 CICC 2026-06 A 股实证的关键启示**：跳跃惩罚 λ：权益/黄金=50，债券=25；强制避险持续**至少 60 个交易日**（与我们 Sortino 60 日窗口巧合一致）；增强信号（须债券同步看空才确认系统性风险）——**"多资产确认 + 强制持续期"是降低 false positive 的有效机制**。我们单市场（A 股）无"债券看空"交叉确认维度，但 §3.2.7 外部信号交叉验证可起类似"多源确认"作用

##### 第十六条远期候选：Sticky HMM with Dirichlet Self-Transition Prior

> **来源**：Staures & Kabašinskas《Identifiable Regime Detection in Pension Fund Networks via Sticky Hidden Markov Models》(preprints.org 2026-06-02, DOI:10.20944/preprints202606.0111.v1；同行评审版 Mathematics 2026, 14(14):2463)。

**核心机制**：Bayesian sticky 转移先验 `π_k ~ Dirichlet(α·1 + κ·e_k)`，其中 κ 控制自转移持续性——期望自转移概率 `E[π_kk] = (α+κ)/(K·α+κ)`。κ 越大 regime 越持久（直接对抗 HMM 高频抖动）。论文识别 3 个潜态，高风险期 cluster 跟踪误差放大 1.09×-1.23×。

| 维度 | 当前 HMM 4 态（MVP） | Sticky HMM（远期） | JM（远期） | Hybrid HMM Poisson（远期） |
|---|---|---|---|---|
| 持续性机制 | HMM 转移概率隐式（无约束） | **Dirichlet 先验 κ 参数**显式控制自转移 | 显式 jump penalty λ | **Poisson jump-duration** 强制尾部态驻留 |
| 实现侵入性 | — | **极低**（转移矩阵估计加 1 行先验） | 高（重写检测器） | **低**（直接转移计数替代 EM，无后处理层） |
| 参数估计 | Baum-Welch EM | 贝叶斯推断（κ 由 CV 选择） | 动态规划 + 坐标下降 | **直接转移计数（绕过 Baum-Welch EM）** |
| 状态划分 | BIC + 收益/波动统计量 | 同当前 HMM | DD_10 + Sortino_20/60 | **Laplace 分位数定义状态**（非聚类） |
| 统计规范性 | 标准 | **最规范**（贝叶斯先验是"状态持续性"的统计标准方法） | 工程化（非贝叶斯） | 半参数（频率派 + Poisson 驻留约束） |

**与 JM / Hybrid HMM Poisson 的关系**：四条路径共享"增强 regime 持续性"目标但机制不同——Sticky HMM 是**先验约束**，JM 是**转换成本**，Hybrid HMM Poisson 是**停留时间约束**。Sticky HMM **实现侵入性最低**（转移矩阵估计加 1 行先验，不重写 forward-backward）且**统计上最规范**；Hybrid HMM Poisson 的独特优势是**参数估计比当前 HMM 更简单**（直接转移计数绕过 EM），可与 Sticky HMM 叠加。**为什么不进 MVP**：C1 已证明 HMM 4 态 Shrinkage 有效（MaxDD 改善 7.36pp）；κ 需 CV 选择（增加调参成本）。若 HMM 实盘后发现状态高频抖动（月内切换 >2 次），Sticky HMM 是比 JM 更轻量的第一升级路径——不换检测器只加先验。归 [10号](10_regime_detector_spec.md) regime 检测器实现。

##### A 股本土对标：中邮证券 LSTM-GHMM 5 态方案

> **来源**：黄子崟《市场脉搏（2）：基于 LSTM~HMM 混合方案的量化择时与动态仓位管理》(中邮证券研报, 2026-07-09, SAC S1340523090002)。

**核心架构**：LSTM 自编码器（90 日 × 25 维 → 10 维压缩）+ 高斯 HMM（GHMM）**5 态**（1 个低自维持过渡态 + 4 个高自维持稳态）。关键设计：**状态切换经"过渡态"完成而非稳态间直接跳跃**——减少稳态间高频切换（与 JM / Sticky HMM / Poisson 持续期的"增强持续性"目标一致，但用"过渡态"结构实现而非先验/惩罚/约束）。

**关键实证**：2021 年以来多指数回测控制回撤并积累超额；**2026 年 K 型极端分化行情适应性偏弱**——超额损失精准锁定于特定状态（执行层问题，非识别层问题）。

**与 34号 的关联**：① **5 态结构（4 稳态 + 1 过渡态）**是第四条 regime 持续性增强路径——机制是"结构性过渡态"，其 K 型分化失效场景印证我们需要 Shrinkage 因子保护；② **轻量级干预规则修正凯利公式均值回归偏差**与我们的 Shrinkage × PerformanceScore 乘法哲学一致——regime 识别后做风险节流而非 alpha 择时；③ **2026 K 型分化失效**是 A 股本土最新实证——2026H1 量化超额从 14.17% 降至 3.11%（[新浪财经 2026-07-11](https://finance.sina.com.cn/jjxw/2026-07-11/doc-inihmkxc5002361.shtml)），K 型行情+因子失效+策略同质化使 alpha 择时难度飙升，印证"风险节流不做 alpha 择时"裁定。

##### 第十七条远期候选：Hybrid HMM with Poisson Jump-Duration

> **来源**：Alswaidan & Varner《Hybrid Hidden Markov Model for Modeling Equity Excess Growth Rate Dynamics: A Discrete-State Approach with Jump-Diffusion》(arXiv:2603.10202v2, Cornell University, 2026-03-10 提交, 2026-04-02 修订)。

**核心架构**：① **Laplace 分位数定义状态**（非聚类，用 Laplace CDF 将连续超额增长率离散化为分位数状态）；② **Poisson jump-duration 机制**强制高波动尾部态驻留经验现实时长（λ 控制跳频率、dwell time 约束强制尾部态持久）；③ **直接转移计数估计参数，绕过 Baum-Welch EM**（直接从观测序列数转移次数估转移矩阵，无 EM 迭代）。

**关键实证**：SPY 10 年日频数据，1000 条模拟路径——KS 检验通过率 >97%（样本内）/ 94%（样本外 2025 全年）；AD 检验 >91%。**标准 HMM 无 jump 通过更多分布检验但无法生成波动率聚类**，Hybrid HMM Poisson 在分布保真 + 时序结构 + 尾部覆盖三维度上联合质量最优。

**与其他持续性路径的关键差异**：

| 维度 | Hybrid HMM Poisson 的独特价值 |
|---|---|
| **参数估计比当前 HMM 更简单** | 直接转移计数（O(T·K) 数转移次数）vs 当前 HMM Baum-Welch EM（迭代 forward-backward）——**升级反而降低实现复杂度** |
| **Laplace 分位数状态划分** | 非聚类方法，对重尾分布（A 股收益率尖峰厚尾）比 Gaussian HMM 聚类更贴合 |
| **Poisson jump-duration 是后验约束** | 不是先验（Sticky HMM）也不是转换成本（JM），而是**显式驻留时间约束**——直接控制"尾部态至少停留 N 天" |
| **与 JM 的 Sortino 同源** | JM 用 DD_10 + Sortino_20/60 做特征；Hybrid HMM Poisson 用超额增长率分位数——两者都消费收益衍生指标，可复用我们 §3.2.2 的 Sortino 管线 |

**为什么是 JM 的轻量替代**：JM 需动态规划 + 坐标下降交替迭代（重写检测器）；Hybrid HMM Poisson 的直接转移计数**比当前 HMM 的 Baum-Welch EM 还简单**（无迭代），同时通过 Poisson jump-duration 获得与 JM jump penalty 同等的持续性增强。代价是 Laplace 分位数状态划分可能不如 BIC 聚类贴合 A 股 4 态语义——需校验 Laplace 分位数与现有 4 态的对应关系。

**A 股适用性评估**：① **Laplace 分布**（kurtosis=3）比 Gaussian 更贴合 A 股收益率尖峰特性（kurtosis >3），但极端尾部可能需 Student-t 或 EVT 补充；② **Poisson 驻留约束**可设尾部态（r4 熊市）最少驻留 ~20-40 交易日（与中金 CICC JM"强制避险持续至少 60 交易日"同量级）；③ **直接转移计数**无 EM 迭代 → walk-forward 重训练更快（C1 [11号] §0.5.7 D1 敏感性网格可更快跑完）。

**为什么不进 MVP**：C1 已证明 HMM 4 态 Shrinkage 有效。**实际侵入性仍需重写 [10号](10_regime_detector_spec.md) regime 检测器**（Laplace 分位数状态划分 + Poisson jump-duration 后处理），不是纯增量。若 HMM 实盘后发现状态抖动 + Baum-Welch EM 重训练耗时成为瓶颈，Hybrid HMM Poisson 是同时解决两个问题的路径——比 Sticky HMM（只解决持续性）更全面，但侵入性更高。归 [10号](10_regime_detector_spec.md) regime 检测器实现。

（远期演进路径排序见第十八条末——含全部条目，为当前权威版本）

##### 第十八条远期候选：CHMM-t（Student-t 发射的连续 HMM）—— 重尾发射优先于持续性机制（**最高优先级选项外更好算法**）

> **来源**：Alswaidan, Jin & Varner《Continuous Hidden Markov Models for Equity Returns: Heavy-Tail Emission Families and Regime-Conditional Value-at-Risk》(arXiv:2606.23492, 2026-06, West Virginia University)。

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

**关键论据**：① **arXiv:2606.23492 的颠覆性结论**——"重尾发射比 jump-duration 机制更重要"，直接挑战第十七条的前提，CHMM-t 用更低成本（~50 行 emission 替换）解决更根本的分布性问题；② **与 Soloviov 2026-07 一致**（§8.1 已引：Student-t innovations 修复几乎所有 VaR 覆盖误差，99% VaR 违规率 1.58%→1.03%，尾形效应比不对称效应大一个数量级）——同一原理在 HMM emission 层的应用；③ **项目记忆已认定非过度工程**，优先 Phase 4 鲁棒性阶段实施；④ **hmmlearn 可直接实现**（`GaussianHMM`→自定义 t-emission 或 `pomegranate` t-emission），无需重写 forward-backward/Viterbi——**实现成本所有远期候选中最低**；⑤ **regime-conditional VaR 副产品**可反哺 [36号] VaR 计算器的 regime-aware 增强。

**A 股适用性评估**：① Gaussian emission 系统性低估 A 股尖峰厚尾（kurtosis >3）→ r4 极端日概率被低估 → ConfidenceSignal 极端日可能误判高确信度，Student-t 的自由度 ν 估计能捕捉厚尾；② **ν 校准**：Soloviov 2026-07 建议 ν=5（GJR-GARCH Student-t innovations），可用 MLE + walk-forward 校准——首批策略实盘后用 A 股数据估 ν；③ **与 4 态语义兼容**——只改 emission 不改状态划分，r1/r2/r3/r4 语义不变，C1 可复用，是侵入性最低的"增强"而非"替换"。

**为什么不进 MVP**：C1 已证明 Gaussian HMM 4 态 Shrinkage 有效。CHMM-t 是**鲁棒性增强**（Phase 4 目标），非 MVP 功能缺口。但**若首批策略实盘后发现**：① 极端日 ConfidenceSignal 误判（r4 熊市极端日仍高确信度）；② regime-conditional VaR 与实际尾部不匹配；③ Sortino/Sharpe gap 监控频繁触发疑似分布性问题——则 CHMM-t 是**第一升级路径**（比 Sticky HMM 更优先，因为解决更根本的分布性问题且实现成本同样低）。

**远期演进路径排序更新（CHMM-t 提升为第一优先级）**：
- **① 近期**（不换架构）：HMM 4 态 + 加最小持续期约束 + §3.2.7 外部信号交叉验证
- **①.4 近期**（不换架构，**最高优先级**）：**CHMM-t（Student-t emission）**——仅改 emission 分布 ~50 行，解决分布性问题，**优先于 Sticky HMM**
- **①.5 近期**（不换架构，最低侵入性）：**Sticky HMM Dirichlet 先验**——转移矩阵加 1 行先验，κ 由 CV 选择
- **② 中期**（换检测器不换优化器）：HMM→JM/SJM 替换，C1 重跑验证
- **②.5 中期**（加态不换检测器）：**5 态结构（4 稳态 + 1 过渡态）**——参考中邮证券 A 股本土实证
- **②.6 中期**（换检测器，参数估计更简）：**Hybrid HMM Poisson**——Laplace 分位数状态 + Poisson jump-duration + 直接转移计数（绕过 EM），比 JM 实现更轻但需校验 Laplace 分位数与 A 股 4 态语义对应
- **③ 远期**（换检测器+换优化器）：JM-MPC 混合（Li 2025），需协方差估计问题先解决

> **过度工程审查更新**：CHMM-t 是所有远期候选中**实现成本最低**（~50 行 emission 替换，不换检测器/不换状态划分/不重写 C1）且**证据最颠覆**的路径。**升级优先级更新**：CHMM-t（分布性，最高优先级）> Sticky HMM（时间性-先验）> 5 态结构（时间性-过渡态）> Hybrid HMM Poisson（时间性-持续期+绕过 EM）> JM（时间性-完全重写）。所有远期候选均登记非施工算法缺失，MVP 用 Gaussian HMM 4 态（C1 已验证有效）。

##### 第十九条远期候选：HSMM（显式持续期半马尔可夫）+ HMM-GAS（score-driven 时变转移）+ BOCPD（贝叶斯在线变点）三条并行路径

> **来源**：① HSMM——libhmm issue #50（2026-07-04，正式列为架构增强）+ Pohle et al. PHSMM R 包（arXiv:2101.09197，penalized MLE 无分布假设 dwell-time 估计）+ Vedant-Choudhari/hsmm-regime-model；② HMM-GAS——André Lucas 厦门大学讲座（2026-04-21）+ R 包 gasmodel v0.6.2（2026-05-17）；③ BOCPD——Fast-BOCPD 库（pip install fast-bocpd，14000-43000 obs/sec，含 Student-t outlier-robust 模型）+ 朱映秋等《统计研究》2025 第 1 期自适应 BOCPD（上证综指验证，CSSCI/北大核心）。

**三条路径的共同定位**：均为"选项之外"的 regime 检测增强路径，与第 1-18 条远期候选正交（不重叠），登记为远期候选池的并行选项，MVP 不采纳。

| 路径 | 核心思想 | 与现有候选的差异 | 2026 证据 | 实现成本 |
|---|---|---|---|---|
| **HSMM（显式持续期）** | HMM 隐含几何分布 dwell time（无记忆），HSMM 显式建模每个状态的 duration distribution（Poisson/Negative Binomial/Gamma/非参数）突破此限制 | Hybrid HMM Poisson（第17条）是 HSMM 的特化（Poisson 持续期 + Laplace 分位数）；HSMM 是通用框架，可用 Negative Binomial 处理过离散停留时间（A 股熊市停留时间方差 > 均值时 Poisson 不够） | libhmm 2026-07 架构增强 + Politecnico Milano 硕士论文 S&P 500 对比 HSMM>HMM + PHSMM 无分布假设 | 中（truncated forward-backward O(TN²D_max)，有 Python 实现） |
| **HMM-GAS（score-driven 时变转移）** | 转移概率不固定，由观测驱动的 GAS 方程演化 `p_{jj,t}=exp(f_{j,t})/(1+exp(f_{j,t}))`，`f_{j,t+1}=ω+A·s+B·f`（s 是条件似然 scaled score） | 观测驱动无需 MCMC，自然适应 regime 不稳定性——是 HMM 与 HSMM 之间的"第三条路"（持续性不靠先验/持续期，靠转移概率随观测自适应） | André Lucas 2026-04 讲座 + gasmodel R 包 v0.6.2 | 中（GAS 方程 + gasmodel 库） |
| **BOCPD（贝叶斯在线变点）** | 维护 run-length（距上次变点时间）后验分布，每步更新——问题从"我们在哪个状态"转为"刚发生了变化吗" | 产出概率而非二元信号，可按比例调仓（与 ConfidenceSignal 软映射同构）；天然处理不确定性；online 友好。**《统计研究》上证综指验证**（A 股本土实证） | Fast-BOCPD 库（含 Student-t）+ 朱映秋 2025 上证综指自适应 BOCPD | 低（pip install，~100 行集成） |

**为什么三条均不进 MVP 但登记**：① C1 已验证 HMM 4 态有效，三条路径均为"换检测器/换范式"的远期升级；② HSMM 是 Hybrid HMM Poisson 的通用版（已登记第17条），登记通用版为的是若 Poisson 持续期不足以拟合 A 股过离散停留时间可升级到 Negative Binomial；③ HMM-GAS 的"观测驱动时变转移"是独特范式（非先验/非持续期/非重尾），与 arXiv:2606.06190（§8.1 已引）"日频 TVTP 不必要"结论有张力——但 GAS 是连续时变而非离散 TVTP；④ BOCPD 的"变点检测"范式与 HMM 的"状态分类"正交，CUSUM+BOCPD+HMM 三信号集成（mathandmarkets 2026-01-30）是 ensemble 思路，可作 Phase 4+ 鲁棒性增强。三条均归 [10号](10_regime_detector_spec.md) regime 检测器远期实现。

### 5.3 为何这是上限而非妥协

- Morwane 实证：regime 做 risk-throttle Sharpe 不变（1.43）、MaxDD 改善 3.9pp、Calmar +38%——**同一个 regime 信号，用于进攻有害，用于防守有益**。三因子乘法是 Morwane risk-throttle 模式的直接工程化，无自创方法
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
| **Sticky HMM Dirichlet 先验（不换架构，最低侵入性）** | 机制/出处见 §5.2 第十六条远期候选——Bayesian sticky 转移先验 `π_k ~ Dir(α+κ·e_k)`，κ 控制自转移持续性；实现侵入性极低（转移矩阵加 1 行先验），统计上最规范，归 [10号](10_regime_detector_spec.md) regime 检测器实现 | HMM 实盘后若发现状态高频抖动，Sticky HMM 是比 JM 更轻量的第一升级路径（不换检测器只加先验） |
| **5 态结构（4 稳态 + 1 过渡态）** | 机制/出处见 §5.2 A 股本土对标——中邮证券 2026-07 LSTM-GHMM 5 态（1 过渡态 + 4 稳态），状态切换经过渡态完成减少稳态间直接跳跃；2026 K 型分化下适应性偏弱。归 [10号](10_regime_detector_spec.md) regime 检测器实现 | HMM 实盘后若发现稳态间直接跳跃导致 PerformanceScore 跳变则评估加过渡态 |
| **3 态 vs 4 态 ablation** | CSDN 2026-05 A 股 HMM 实战指出"A 股 60%+ 时间震荡，3 态是过拟合与表达力的折中（2 态太粗、4 态过拟合）"——直接质疑 4 态选择。[11号](11_regime_backtest_validation_plan.md) C1 验证 BIC 选优稳定收敛到 4 态，但未做 3 态样本外稳定性对比 | 首批策略 A 股数据上对比 3 态 vs 4 态样本外稳定性；若 3 态显著更稳则降级 |
| **Hybrid HMM Poisson jump-duration（换检测器，参数估计更简）** | 机制/出处见 §5.2 第十七条远期候选——Laplace 分位数状态划分 + Poisson jump-duration 强制尾部态驻留 + **直接转移计数绕过 Baum-Welch EM**；比 JM 实现更轻（无动态规划），比当前 HMM 参数估计更简（无 EM 迭代）。归 [10号](10_regime_detector_spec.md) regime 检测器实现 | HMM 实盘后若发现状态抖动 + Baum-Welch EM 重训练耗时成为双重瓶颈，则评估 Hybrid HMM Poisson（同时解决持续性和计算成本）；需先校验 Laplace 分位数与 A 股 4 态语义对应关系 |
| **3 态 sweet spot 佐证** | kooexperience 2026-03 HMM 教程实证"stock returns naturally cluster into roughly three volatility regimes—two feels too coarse, four or more starts overfitting noise, three is the sweet spot"——与 CSDN 2026-05 A 股实证同向质疑 4 态。但 [11号] C1 BIC 选优稳定收敛到 4 态（非过拟合），且 4 态有语义基础（r1-r4），待 ablation 定论 | 同 3 态 vs 4 态 ablation 条件 |
| ~~测试套件重建（P0 缺口）~~ **✅ 已解决（2026-08-15）** | ~~55 用例丢失待重建~~ → **已重建闭环**：AI-REGIME-001 按 §3.4 伪代码 16 条施工要点 + 代码本体（water-filling 投影/CRISIS floor 降级/gap 两级阈值）回建 [test_regime_meta_allocator.py](../../../../tests/pf_alloc/test_regime_meta_allocator.py) 55 用例（8 类组织保持原结构），两轮 55/55 全绿；重建后立即 git 提交闭环（git 灾难教训：未提交=无保护，已执行） | ✅ 已解决（2026-08-15，用户裁定 AI-REGIME-001 施工） |
| **33号 文档重建依赖（✅ 已解决）** | ~~[33号](33_budget_change_handler.md) 设计文档在 2026-08-11 git 灾难中丢失（骨架 v0.1.0）~~ → **2026-08-12 已重建为 active v1.0.0**（commit 6a4f5392，依 MOD-POS-022 production 代码回建，47 测试幸存）；§3.3 两处引用锚点已恢复精确指向（三级升级→33号 §3.2，budget 变动防抖→33号 §3.3 防抖双层） | ✅ 已解决（2026-08-12） |
| **conf_k 连续置信收缩（远期候选）** | marketmaker.cc 2026-06-28 受控实验（600 种子、已知 ground truth）：`conf_k = n/(n+k)` 交易数收缩因子 + exposure floor 组合的连续收缩可追平全时间线 Sharpe（OOS 1.70）且退化率仅 0.2%——是比 ConfidenceSignal 四档阶梯（0.3/0.6/0.85/1.0）更有理论形状依据的**连续置信收缩函数**。MVP 不采纳（四档已经 C1 验证 + 1uptick 60% 阈值外部印证 + 语义可解释），登记为四档的连续化远期替代——若 D1 敏感性网格显示四档边界是悬崖型（±20% 扰动效果骤变），conf_k 连续函数是首选替代形状 | D1 网格显示四档悬崖型 / 实盘后 ConfidenceSignal 档位跳变频繁 |

### 6.1 过度工程审查：四档 Shrinkage 是否过细？

**结论：四档不过细，保留。**

| 对比 | 评估 |
|---|---|
| 2 档（如 0.5/1.0） | 太粗——<60% 和 60-95% 用同一档，丢失"中度确信"区分，过度保守 |
| 3 档（如 0.3/0.7/1.0） | 可行，但 80-95% 轻度收缩（0.85）和 >95% 满部署（1.0）的区分有意义（C1 验证中贡献了 MaxDD 改善） |
| **4 档（当前 0.3/0.6/0.85/1.0）** | **合理**——对应四个认知状态（不确定/有方向/较确信/高确信），有语义基础 |
| 5 档+ | 过细——max(P) 的估计误差本身就 >5%，分太细是伪精确 |

**关键论据**：① 四档只是 ConfidenceSignal 部分，真正的 Shrinkage = ConfidenceSignal × RiskSignal（13 参数连续值 0.3-1.0），整体是"离散×连续"=准连续，粒度足够细，**不需要在 ConfidenceSignal 上再加分档**；② C1 已通过，证明四档在历史数据上有效（MaxDD 改善 7.36pp）；③ 四档阈值（60/80/95%）待 D1 敏感性网格校准——悬崖型（±20% 扰动效果骤变）则调整，稳健则确认。

## 7. 待定问题（讨论要点）

> 以下来自 [00_index_trading_decision](00_index_trading_decision.md) §3 G15 讨论要点，已逐项对齐落入 §3 决策。

- [x] ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` → §3.1；② Base_i 先验权重 → §3.2.1；③ PerformanceScore 60 日 Sortino 映射 [0.5,1.5] → §3.2.2；④ Shrinkage 置信度→风险节流映射（四档）→ §3.2.3
- [x] ⑤ floor≥5% / cap≤40% → §3.2.4；⑥ 稀有态差异化收缩 → §3.2.5；⑦ 第二阶段上线时机 → §3.2.6；⑧ 外部信号交叉验证（5 档水温 + 板块轮动状态）→ §3.2.7（审查补充，非原始 G15 要点；远期辅助印证定位，不进 MVP 主链路）

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
| Invesco+清华《Dynamic global asset allocation》(2026-04) + I-am-Uchenna/regime-allocation-strategy (2026-01) + donarduka/regime-switching-portfolio (2026) | regime 动态分配实证：Invesco"higher returns, better risk-adjusted performance, shallower drawdowns"；I-am-Uchenna Sharpe 1.220/MaxDD -19.54% vs 等权 0.660/-23.45%；donarduka MaxDD 改善 5.5pp（与 C1 的 7.36pp 同量级，独立印证 regime 节流） |
| arxiv 2410.14841《Dynamic Factor Allocation Leveraging Regime-Switching Signals》 + 华安证券《基于状态切换信号的动态因子配置》(2025-10-21, SJM+BL) | regime analysis ≠ factor timing；BL+regime 信号 IR 0.05→0.4（华安 SJM 特征加权 IR 同量级 8 倍提升，双重印证）——支撑"regime 用于风险节流不用于择时"；BL 已拒绝（§4.5），SJM 特征选择思想可吸收到 RiskSignal 13 参数权重优化 |
| misango《Regime-Based Portfolio Strategies》(2026-03) + preprints.org《When to Route? Regime-Adaptive Meta-Policies》(2026-05) + loic-mmt/quant-portfolio (2026-08-07) | misango：60/40 成本后优于复杂 ML 方案——支撑三因子乘法而非 RL/优化器（§4.4）；preprints：低信号时直接部署比路由更安全；loic-mmt："不预测未来，只检测状态+调整暴露"——与"只做风险节流不做择时"裁定一致 |
| BestFolio《Walk-Forward Portfolios》(2026-04) | walk-forward max Sharpe 优化器：36 个月 lookback + **cap 40%** + 月频重平衡。cap 40% 与我们 CAP=0.40 完全一致（§3.2.4 印证）；36 个月 vs 我们 60 日的窗口差异在 §3.2.2 讨论 |
| 1uptick.com《Regime-Adaptive Risk Framework》(2026-06) | 机构跨资产方案：regime transition 时 max(P)<**60%** 减仓 30-50% + 60-120 天校准窗口。60% 阈值与我们 ConfidenceSignal 四档完全一致（§3.2.3 印证） |
| stockalpha.ai《AI for Portfolio Optimization》(2026-01) + arxiv MM-ARC 2509.05080v3 (2026-07-27) + arxiv 2510.14986《RegimeFolio》(2026-10) | stockalpha：改善协方差/收益估计收益大于调优化器——我们用 PerformanceScore 后验代替协方差估计（该建议的轻量替代）；MM-ARC/RegimeFolio（Ledoit-Wolf+regime MVO，Sharpe 1.17、MaxDD 改善 12%）——MVO 已拒绝（§4.2），"regime 分割+分别建模"思想与 Shrinkage 一致 |
| arxiv 2603.04441《Explainable Regime-Aware Investing》(2026-02) + arXiv:2507.19824《Regime-Switching Induced Stock Price Jumps》(2025-07) + arXiv:2602.16952 HyRA(2026-02-18)+ewinnington(2025-04-16) | 2603.04441：核心论断"**regime inference stability—particularly identity preservation—is a first-order determinant of portfolio drawdown**"（Sharpe 2.18 vs SPX 1.18）——印证 Shrinkage 路径，记 10 号 Phase 3 增强候选；2507.19824：制度切换时股价本身发生跳跃（如 2024-09 政策底单日 +8%）——印证 §3.3 日频更新 + D-SIGNAL-68 盘中重算设计；HyRA/ewinnington：加 floor/关系约束时迭代 water-filling 失效→MIQP——当前 `_normalize_and_clip` 对 N=3-5 有效，MIQP 记远期升级路径 |
| advisingalpha.com《Sharpe vs Sortino》(2026-05) + fastercapital.com(2026-05) + moneylume.com(2026) | 三源一致：Sortino 只惩罚下行波动，适合非对称/偏态收益分布（moneylume：options/杠杆 ETF/crypto 应选 Sortino——A 股打板/事件驱动收益分布类似 options payoff）——支撑 §3.2.2 Sortino 切换 |
| equiscale.ai《Sharpe vs Sortino》(2026) + portfoliogenius.ai《Sortino Ratio》(2026) + fxroboteasy.com(2026-08-04) | equiscale：高波动策略的 good volatility 不应拉低评分（A 股打板涨停板直接支撑 Sortino 选型）；portfoliogenius：Sortino 解读区间（<0 失败/0.5-1.0 适中/1.0-2.0 很好/>2.0 卓越）支撑 §3.2.2 映射区间 [0.5,1.5] 语义；fxroboteasy：trend-followers/breakout systems 首选 Sortino |
| recessionistpro.com《Capital Preservation》(2026-02) + protraderdaily.com《Recession Portfolio 2026》(2026-08-09) | recessionistpro："先定回撤上限"——支撑 §3.2.2 熊市最低总暴露设计（A 股 cash=防御资产，9% floor）；protraderdaily：防御组合 MaxDD -8.2% vs growth -23.7%——多资产对照，A 股单市场用高 cash（低 global_shrinkage）等效防御 |
| ecassets.com《Sortino Ratio》(2026-05-28) + foliolab.ai《Sortino Ratio》(2026) | **关键警示**：下行样本少→Sortino 系统性偏高（inflated values）——直接支撑 §3.2.2 样本量门槛（downside<15 强制中性）+ 防护三件套（样本门槛+cap 兜底+gap 监控） |
| Oliveira et al.《Tactical asset allocation with macroeconomic regime detection》(Quantitative Finance 2026-06-11, Oxford-Man Institute) + Pei et al.《Market Regime Council for Dynamic Credit Assignment》(arXiv:2605.24490, 2026-05-23) | Oliveira：FRED-MD 宏观数据集+modified k-means+预测 regime 分布→仓位映射（优于 equal-weight）——记 10 号前沿演进候选（宏观特征补充）；Pei（MRC）：贝叶斯自适应混合冷启动（权重随样本量渐变）比我们 30 日阈值切换更平滑——§3.2.2 冷启动远期候选（MVP 不采纳）；Shapley credits O(2^N) 过重不采纳 |
| forex-basics.com《Sortino Ratio Basics》(2026-05-17, verified 2026-05-28) + financefriend24.com《Sortino Ratio Explained》(2026) | **关键机构标准**：Sortino 机构标准=最低 36 个月；<36 个月对单个坏月高度敏感——直接支撑 §3.2.2 重大修正（60 日远低于标准是已知妥协，需防护四件套+实盘校准触发条件） |
| superglobalcalculator.com《Sortino Ratio Calculator》(2026) + getzenquery.com(2026) | "Need ≥ 30 periods for stability"——支撑 §3.2.2 downside 样本量门槛（我们 60 日 downside ~24 日接近 30 阈值，需防护） |
| Alkhudaydi & Althobaity《GATE-WPCA-PI》(AIMS Mathematics 2026, 11(2):3647-3702) + Lkhagvasuren et al.(JIMO 2026, 22(4):1672-1692) | GATE-WPCA-PI：entropy floor+sleeve caps 与我们 floor 5%/cap 40% 同构（§3.2.4 学术级印证）；Lkhagvasuren：feasibility restoration（约束无解时找最近可行解）——直接支撑 §3.2.4 无解兜底（N=2 优先保 floor 降 cap） |
| AI Finance Labs / Lopez-Lira《Claude AI-Managed Portfolio》(2026-03 至 2026-08) + sooktrading/whalesbook《KOSPI Collapse 2026》(2026-08-03/05) | Claude AI 管 $50K 5 个月 19.04% vs S&P 12.24%，最大持仓=0-3 月国债 ETF——**AI 无人值守系统天然倾向防御**，印证低 global_shrinkage floor 9% 设计；KOSPI 2026-07 六周 -40%（杠杆 ETF+集中 >50% 权重崩塌、32 万账户强平）——印证 cap 40% 防集中+禁杠杆必要性 |
| Yang et al.《RMATS: Recursive Multi-Agent Trading System》(arXiv:2605.25311, 2026-05-25, APAM 2026) | 4 agents+recursive Manager，MaxDD 9.62%（vs MVO 15.49%），**Risk Agent 独立于策略 agent**——印证 regime 层应独立于策略层解耦；**不采纳多 agent 递归架构**（§4.4/§3.2.7）；其 adaptive circuit breaker 与四档+外部信号冲突降档思想一致 |
| [YoungCan-Wang/Wyckoff-Analysis](https://github.com/YoungCan-Wang/Wyckoff-Analysis) v2.1.x（2026-04 实证） | A 股大盘水温 5 档仓位（NEUTRAL 100%/RISK_ON 50%/PANIC_REPAIR 50%/RISK_OFF 30%/CRASH 0%），实测 NEUTRAL +1.17%（唯一正收益）——直接支撑 §3.2.7 5 档水温作 HMM 4 态外部交叉验证信号 |
| [YoungCan-Wang/WyckoffTradingAgent](https://github.com/YoungCan-Wang/WyckoffTradingAgent) Wiki《04_Finance_Sector_Rotation_Regime》（2026-04 实证） | 板块轮动 5 分类+watch_score；共识高潮后 3 日下跌 >2% 概率 29.8%；DISTRIBUTION_RISK 最危险状态与 HMM r4 交叉印证——支撑 §3.2.7 板块状态辅助信号 |
| pooyagolchian《Portfolio Risk Management: VaR, CVaR, and Kelly Criterion for 2026》(2026-04-13) | Fractional Kelly 实证：Quarter Kelly 10.8%/−22%（85% 增长/35% 回撤）——直接支撑 §3.2.3 Shrinkage 节流与 Quarter Kelly 同构（"适度收缩风险预算→以小得多回撤代价获大部分增长"是 §2.2 裁定的实证依据） |
| Nystrup/Boyd/Lindström/Madsen《Multi-period portfolio selection with drawdown control》(Annals of Operations Research 282(2):1-27, 2019) | MPC 动态优化+多变量 HMM 多期预测+**按已实现回撤调风险厌恶系数**——§5.2 远期候选；完整框架需协方差+凸优化求解器，"realized drawdown→γ 动态"思想可先吸收为 ConfidenceSignal 回撤通道增强（§6 待裁定），不换架构 |
| Grube Martín-Lunas et al.《From Regime Detection to Decision Rules》(MDPI Economies 14(7):268, 2026-07-09) + Verma/Putri/Lesupi(arXiv:2605.27848, 2026-05-27) + youcanbuildthings.com(2026-05-06) | Grube：naive regime-conditional CVaR 年换手 ~226%，"**bottleneck is not regime detection but transparent, stable, cost-aware decision-rule design**"——支撑 Shrinkage 只缩放总暴露（低换手）而非 regime-MVO（§4.2）；Verma：one-day execution lag 避前视（与 T+1 一致），RL 不采纳（§4.4）；youcanbuildthings：90 天 correlation drop rule+circuit breaker（15% half/25% zero）——[30号] 策略独立性可借鉴的量化判定 |
| Shu/Yu/Mulvey《Downside risk reduction using regime-switching signals: a statistical jump model approach》(Journal of Asset Management 25(5):493-507, 2024；arXiv:2402.05272) | **JM 原始论文**——显式 jump penalty λ 增强 regime 持续性；特征集 DD_10+Sortino_20/60（**与我们 PerformanceScore Sortino 同源**）；1990-2023 三国实证全面优于 HMM 与 buy-and-hold——直接支撑 §5.2 JM 远期候选 |
| 中金公司《量化配置模型系列（2）：基于统计跳跃的系统性风险预警模型》(2026-06-24, finance.sina.com.cn 报道) | **JM 应用于 A 股（股-债-金八资产）**——λ：权益/黄金=50、债券=25；强制避险≥60 交易日（与我们 Sortino 60 日窗口巧合一致）；三资产风险平价 MaxDD -7.07%→-3.23%、卡玛 0.77→1.59；"多资产确认+强制持续期"降 false positive（我们单市场用 §3.2.7 外部信号起类似作用）——支撑 §5.2 JM + §3.2.2 60 日窗口 |
| Cortese/Kolm/Lindström《Generalized information criteria for high-dimensional sparse statistical jump models》(AStA 2026-06) + Li/Chen/Tao/Ji《JM+MPC》(Mathematics 13(17):2837, 2025) | Cortese：**JM 超参数选择学术标准**（广义信息准则，MSCI 3 态最优与我们 4 态 BIC 同量级）；Li：**JM-MPC 混合框架**——支撑 §5.2 远期演进路径排序③；MVP 均不采纳（需协方差估计问题先解决） |
| dataloopr《Regime-Aware Portfolio Strategies》(2026-03-09) + Soloviov《Asymmetry, Fat Tails, and the Cost of the Wrong Innovation》(2026-07, marketmaker.cc) + Park/Kim《Deep Generative AI for Portfolio Management》(Columbia, 2025) | RiskSignal 波动建模远期参考：GARCH+Student-t 是 realized_vol 分位数进阶建模；Soloviov 受控实验：**Student-t innovations 修复几乎所有 VaR 覆盖误差（99% VaR 违规率 1.58%→1.03%），尾形效应比不对称效应大一个数量级**——RiskSignal 升级 GARCH 时 Student-t 必选，ν 估计是关键参数；Park/Kim 深度生成模型 CVaR 优化——Phase 5+ 不采纳（训练成本+黑箱） |
| 汇安基金柳预才《大小盘动态量化新框架》(2026-08-07, cnfol.com 报道) | **A 股本土双层动态量化**——顶层风格判别（20+ 因子）≈我们 regime+Shrinkage（但汇安做大小盘 alpha 择时，我们 §4.1 拒绝）；双独立选股池≈StrategyBook sleeve；切换阈值过滤噪音≈四档；底仓对冲误判≈floor≥5%。2026H1 量化超额 14.17%→3.11%（[新浪财经 2026-07-11](https://finance.sina.com.cn/jjxw/2026-07-11/doc-inihmkxc5002361.shtml)）印证"风险节流不做 alpha 择时"裁定 |
| firestrand/marketregimeml《Model Comparison》(2025-09, GitHub) | **regime 检测模型对比基准**——SVM 集成 RQI 83.6-86.9 vs HMM 67.8-76.6 vs LSTM 49.1-64.9；**10 个优化特征胜过 35+ 特征**，n_regimes>3 过拟合——HMM 非最优但 C1 已证明有效 MVP 不换；SVM 集成为 §6 HMM→JM 替换提供更轻量替代路径；10 特征原则印证 6 因子 HMM 输入精简设计 |
| quantt.co.uk《Sortino Ratio Explained》(2026-04) + CFA Institute《The Sortino Ratio》(Deborah Kidd, CFA, rpc.cfainstitute.org) | quantt：**Sortino ≈ 1.3-1.5×Sharpe 正常范围基准**（支撑 §3.2.2 gap 监控阈值校准）+ **下行偏差分母用总样本量 N（非下行观测数）的独立验证**（支撑施工要点 #13 分母修复）；CFA Institute：Sortino 权威原始定义 + Sortino-Forsey 1996 bootstrap 方法——为施工要点 #14 bootstrap 远期候选提供理论溯源 |
| RPubs《Market Regime Detection using HMM Walk-Forward》(2026-04) | **HMM walk-forward 三策略对比**——expanding window+hard switch **失败**（crisis-scarred 训练数据致过度保守）；rolling 3yr+hard switch 纠正；**soft allocation（概率加权敞口）最优 MaxDD -30.5%（vs hard expanding -52.4%）**——直接验证 ConfidenceSignal 四档软映射设计（软映射优于硬切换量化证据）；expanding 失败警示：HMM refit 须 rolling 非 expanding（归 [10号] 设计约束） |
| GARCH-ARJI《Jump Persistence in Financial Markets》(Int J Forecasting 42(3):833-852, 2026) + M-ROLL《AI-Markov Hybrid Portfolio Framework》(IJFMR 2026-03/04) | GARCH-ARJI：**跳跃强度时变持续性**——RiskSignal realized_vol 升级 GARCH 建模**须纳入 ARJI 跳跃强度**（常数跳跃强度低估尾部风险）；M-ROLL：Markov+PSO 散度最小化（Sharpe 1.87 较等权 +260%，MaxDD 44.2%→28.1%）——不换检测器换优化器的第三条远期路径，MVP 不采纳 |
| Acanto 8A《Momentum + Risk Parity White Paper》(2026-02) + arXiv:2606.09478《Volatility Forecasting under Market Regimes: High-Frequency Chinese Equity Data》(2026-06) | Acanto 8A：动量+风险平价 2008-2026 Sharpe 1.19、**Sortino 1.21**、MaxDD -7.6%——Sortino 1.21 是机构级基准（首批策略实盘后 Sortino 达 1.0-1.5 是合理预期）；arXiv:2606.09478：**A 股高频实证** regime-augmented HARQ+MS-GJR-GARCH 波动率预测持续优于 baseline——支撑 RiskSignal 升级 regime-augmented GARCH 远期候选的 A 股适用性，MVP 不换 |
| arXiv:2604.09060《Taming the Black Swan: A Momentum-Gated Hierarchical Optimisation Framework for Asymmetric Alpha Generation》(2026-04, Chakraborty & Singh) | **AEGIS 框架：动量门控+minimax 相关+SLSQP 直接优化 Sortino**，20 年 walk-forward——**直接优化 Sortino** 印证我们 PerformanceScore 选型正确；minimax 相关强制分散与 floor 5%/cap 40% 同构；SLSQP 需协方差估计 MVP 不采纳，记远期候选 |
| arXiv:2603.10202《Hybrid Hidden Markov Model for Modeling Equity Excess Growth Rate Dynamics: A Discrete-State Approach with Jump-Diffusion》(v2 2026-04-02, Alswaidan & Varner, Cornell) | **直接支撑 §5.2 第十七条远期候选**——Laplace 分位数状态+Poisson jump-duration+直接转移计数绕过 Baum-Welch EM（参数估计比当前 HMM 更简单）；SPY 10 年 KS/AD >97%/91%（样本内）、>94%（样本外）；MVP 不换（C1 已验证 HMM 4 态有效） |
| Oliveira/Guzman/Firooziye《(Non-Parametric) Bootstrap Robust Optimization for Portfolios and Trading Strategies》(arXiv:2510.12725, 2025-10-14, USP/UCL) | **非参数 bootstrap 鲁棒优化**——直接支撑施工要点 #14 bootstrap CI 远期候选（点估计映射→bootstrap 下分位映射）；CFA Institute 2026 共识：downside deviation 分母必须用全部 n——直接支撑施工要点 #13 CRITICAL bug 修复 |
| quarcc.com《Endogenous Regime-Switching with Duration Dependence》(2026-03-08) + arXiv:2604.27991《Stochastic Inertia in Regime-Switching Models》(2026-04-30) | quarcc：**negative-binomial hazard duration dependence**——比 Poisson 更灵活处理过离散停留时间（A 股熊市停留方差>均值时 Poisson 不够），远期候选池第五条路径；Stochastic Inertia：噪声反而增强 regime 寿命——regime 持续性增强的理论基础（最轻量路径：仅在转移概率上加噪声），MVP 不采纳 |
| Soloviov《Do Bootstrap Confidence Intervals for Backtest Statistics Cover? A Controlled Study Under Serial Dependence》(bootstrap.marketmaker.cc, 2026-06-10, arXiv-ready; [GitHub](https://github.com/suenot/bootstrap-coverage)) | **Bootstrap CI 覆盖率受控实验**（6000 次）——BCa 仅 iid 有效（0.954），AR(1) φ=0.3 下失效（0.838 vs 名义 0.95）；GARCH/regime 波动率损害小；**最大回撤分位数全部乐观偏差**；实践配方=自动块长 block bootstrap 或 Lo HAC SE——**直接支撑施工要点 #14 CRITICAL 修正**（stationary block bootstrap，AR(1) 下恢复 0.946） |
| Staures & Kabašinskas《Identifiable Regime Detection in Pension Fund Networks via Sticky Hidden Markov Models》(preprints.org 2026-06-02, DOI:10.20944/preprints202606.0111.v1; Mathematics 2026, 14(14):2463) | **直接支撑 §5.2 第十六条远期候选**——Sticky HMM Dirichlet 自转移先验（识别 3 潜态，高风险期 cluster 跟踪误差放大 1.09×-1.23×）；实现侵入性极低（转移矩阵加 1 行先验），统计上最规范；MVP 不采纳，HMM 实盘状态高频抖动时的第一轻量升级路径 |
| usepancake/batter《Pancake Engine Bootstrap CI + Permutation Test》(GitHub math-audit-0.4.md, 2026-05-26) | **直接支撑施工要点 #14 CI_TOO_WIDE 守卫**——percentile bootstrap（10000 次重采样）+ 5× 阈值（Ding & Martin 2017 对 Sharpe 的校准）；PerformanceScore 的 bootstrap CI 触发 CI_TOO_WIDE 时须更强 Shrinkage 或强制中性 |
| 中邮证券/黄子崟《市场脉搏（2）：基于 LSTM~HMM 混合方案的量化择时与动态仓位管理》(2026-07-09, SAC S1340523090002) | **直接支撑 §5.2 A 股本土对标 + §6 待裁定 5 态结构**——LSTM 自编码器（90 日×25 维→10 维）+ GHMM 5 态（1 过渡态+4 稳态）；2026 K 型极端分化适应性偏弱（超额 14.17%→3.11%）印证"风险节流不做 alpha 择时"裁定；MVP 不采纳 |
| 华安证券/严佳炜、钱静闲《自适应市场状态的强化学习在资产配置中的应用》(2026-05-01) + 湘财证券/仇华《2026年8月大类资产配置展望》(2026-07-26) | 华安 RL：KMeans/GMM/HMM 三机制+Transformer PPO（Sharpe 1.43/Sortino 1.59）——**奖励裁剪是关键**（可嵌入 PerformanceScore 防极端），**机制信号互信息 0.1020** 可作 HMM 信号强度基准（首批实盘后对照）；MVP 不采纳 RL（§4.4）。湘财：A 股波动率锚定风险平价三档（≤4%/8-10%/15-18%）——可作 Base 因子 A 股校准基准（MVP 等权 1/N，远期可升级 inverse-vol/risk parity） |
| CSDN/mokamo《A股市场状态识别：HMM + Optuna 超参优化》(2026-05-16) + arXiv:2606.06190《Multi-Scale MS-GARCH EUR/USD》(2026-06-04) | CSDN：A 股 3 态 GaussianHMM 实战（年化波动 20-30%、60%+ 时间震荡，**3 态是过拟合与表达力折中**）——直接质疑 4 态，记 §6"3 态 vs 4 态 ablation"项；arXiv:2606.06190：4H/1H 上 TVTP 受支持，**1D 日频上静态转移概率更优**——支撑我们 HMM 静态转移概率选择，MVP 不采纳多尺度 |
| arXiv:2512.03777《iHMM 初始化策略对比》(2026-06-12 v2, Cortese & Rossini) + kooexperience.com《HMM Regime Detection》(2026-03) | iHMM：**distance-based clustering（KMeans++）初始化一致优于 model-based/uniform**——归 [10号] HMM EM 训练初始化策略；iHMM 自动推断状态数成本高 MVP 不采纳。kooexperience：3 态教程实证"three is the sweet spot"——与 CSDN 同向质疑 4 态，支撑 §6"3 态 sweet spot 佐证"项；C1 BIC 稳定收敛 4 态且有语义基础（r1-r4），待 ablation 定论 |
| susanpotter.net《Bootstrap Methods for Strategy Robustness》(2026-05-23) + metricgate.com《Choosing a Resampling Scheme for Dependent Time Series》(2026-06) | susanpotter：naive i.i.d. bootstrap 金融时序三重失效（破坏自相关/波动率聚类/截面相关），block bootstrap（Künsch/Liu-Singh/Politis-Romano）保留块内依赖；metricgate：**AR(1) φ=0.7 下 naive i.i.d. 标准误仅为真实值 ~40%（灾难性低估）**，stationary bootstrap 对块长选择不敏感更鲁棒——**直接支撑施工要点 #14 stationary block bootstrap 选择** |
| Alswaidan, Jin & Varner《Continuous Hidden Markov Models for Equity Returns: Heavy-Tail Emission Families and Regime-Conditional Value-at-Risk》(arXiv:2606.23492, 2026-06, West Virginia University) | **直接支撑 §5.2 第十八条远期候选（第一优先级）**——颠覆性发现："HMM 无法复现收益率绝对值自相关慢衰减"是**分布性**问题非时间性——重尾 emission（Student-t）而非 jump-duration/HSMM 弥合大部分拟合差距，无需调超参数；产出 regime-conditional VaR 过 Christoffersen 检验；~50 行 emission 替换；MVP 不换，实盘发现分布性问题则 CHMM-t 是第一升级路径 |
| Pav《Post-Selection Estimation of Sharpe Ratios》(arXiv:2606.01650v1, 2026-06-02) | **直接支撑施工要点 #15 选择偏差收缩远期候选**——James-Stein 估计器多数现实参数下最优（GMLEB 次之），收缩因子 `s = (1 - (k-2)·σ²/‖ζ̂‖²)₊`（k≥3 生效）；多策略相对值防护与四件套绝对值防护正交；MVP 不进，实盘发现"Sortino 最高策略次月反转"则启用 |
| Ryan《Conformal Kelly: Conformal Prediction Intervals as the Scale in Fractional Kelly Position Sizing》(arXiv:2608.01494v1, 2026-08-02, ACS Athens) | **直接支撑 §4.5 Conformal Kelly 远期精炼登记**——保形区间宽度作 fractional Kelly 的 σ；最简慢/无权重/逐资产 rolling 保形分位数胜过所有快速自适应；**样本外警示**：校准保持（0.745 vs 0.750）但增长未保持——不推翻 Kelly 拒绝，[31号] Phase 4+ 单策略仓位远期路径 |
| marketmaker.cc《Objective-Function Design: The Metric You Optimize Secretly Picks Your Strategy》(2026-06-28，含配套论文+开源代码） | **目标函数口径受控实验**（600 种子）——全时间线 Sharpe 永不退化（OOS 1.71），per-trade 口径 57% 概率选出退化策略——**印证 PerformanceScore 全时间线口径纪律**（60 日 Sortino 按每日收益序列计算，含未持仓日 0）；`conf_k = n/(n+k)` 支撑 §6 conf_k 远期候选 |
| Whelan《Kelly Strategies and the Return on Capital Deployed》(UCD, 2026-05) | **fractional Kelly 单位资本回报新证**——full Kelly 单位投放资本回报仅约均值一半，半 Kelly 3µ/4、1/4 Kelly 7µ/8——为 Shrinkage ≤1.0 只减不增的折扣哲学提供 2026 学术背书（与 §3.2.3 Quarter Kelly 同构印证互补） |
| arXiv:2603.21330《FinRL-X》(2026-03-22) + Candriam Alternative Multi-Strategies 转型（AOF/Boursorama 2026-03-23 + 官网 Q&A 2026-04-16） | FinRL-X：组合级**风险覆盖层独立于信号层**做成可组合管道——印证 regime Shrinkage 正是独立于策略层的风险覆盖层（§3.1 解耦设计），RL 分配器不采纳（§4.4）；Candriam：机构级多策略基金按 risk-on/off regime 动态调整策略权重+单一交易账簿——行业侧印证"regime 驱动策略间资金再分配"是 2026 机构在用范式，我们用三因子乘法 O(N) 实现同目标 |
| cluttmann/multi_strategy_portfolio（GitHub 个人实盘，2026-05~08 持续提交） | **反例弱证据（诚实登记）**——个人 7-sleeve 组合固定目标权重+月度再平衡，2026-05 退役其 "Regime World" 策略（无业绩归因披露）。不据此改 MVP：① 无业绩对比无法判断 regime 失效还是实现问题；② C1 已实证 Shrinkage 有效（MaxDD 改善 7.36pp）；③ 第一阶段本就是固定 budget（§4.3），RegimeMetaAllocator 是第二阶段可选增强。登记为"regime 模块个人系统适配性"持续观察项 |

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
| 2026-08-12 | 2.8.0 | **二十次审查（AI-12 任务驱动：34/00号 双文档架构审查 + 2026-08-12 全网搜索）**——5 项核心改动：① **§3.5 新增「已施工设施盘点」**（通用规则 #11）——全面扫描代码/蓝图/测试/上下游/depgraph 11 项设施，结论：代码链路完整全部 production，**唯一缺口 = 测试套件丢失**；② **测试丢失事件取证与标注**——`tests/pf_alloc/test_regime_meta_allocator.py`（55 用例）经 git 取证确认**从未提交**（`git log --all` 无记录），2026-08-11 被 `git clean -fd` 删除不可恢复，§3.1 代码映射"55 测试用例全绿"修正为"曾全绿+待重建"，§6 待裁定新增 P0 重建项（重建依据 §3.4 伪代码 + 代码本体）；③ **33号 幻影引用修复**——33号 设计文档实为骨架 v0.1.0（git 灾难丢失/从未提交高版本内容），§3.3 两处引用（三级升级 + budget 变动防抖 §6）标注临时真源（30号 §2.4 + MOD-POS-022 production 代码），§6 待裁定新增重建依赖项；④ **§8.1 新增 5 条 2026-08-12 搜索引用**——marketmaker.cc 目标函数口径受控实验（印证 PerformanceScore 全时间线口径 + conf_k=n/(n+k) 连续收缩登记为四档远期替代）/ Whelan fractional Kelly 单位资本回报（Shrinkage 折扣哲学学术背书）/ FinRL-X 风险覆盖层独立（架构印证）/ Candriam 机构 regime 动态分配（行业印证）/ cluttmann 个人系统退役 regime 模块（**反例弱证据诚实登记**，不据此改 MVP）；⑤ **§6 待裁定新增 3 项**（测试套件重建 P0 / 33号 重建依赖 / conf_k 连续置信收缩远期候选）。**审查结论**：C1 回填与 7 项讨论要点在前 19 轮已完成；分配公式参数设计完整（公式/Base/PerformanceScore/Shrinkage 四档/floor·cap/稀有态/第二阶段时机 + §3.4 完整伪代码）；四档 Shrinkage 与 60 日 Sortino 经过度工程复审**维持不过度**（C1 实证 + 1uptick 60% 阈值 + BestFolio cap 40% 外部印证）；本轮搜索未发现需更换 MVP 基线的证据。frontmatter v2.7.0→v2.8.0 | 用户任务驱动审查发现：① 测试套件丢失是 08-11 git 灾难在本模块的遗留创伤（代码幸存但无回归防护网）；② 33号 引用指向已丢失内容；③ 已施工设施从未系统盘点（通用规则 #11 要求）；④ 2026-08-12 最新研究 5 条均印证现有设计，conf_k 连续收缩是唯一值得登记的增量备选 |
| 2026-08-12 | 2.8.1 | **二十一次审查·33号重建联动修正**——① §3.3 两处标注更新：33号 已于 2026-08-12 重建为 **active v1.0.0**（commit 6a4f5392，另一 AI 依 MOD-POS-022 production 代码回建，含 §3.2 三级升级 + §3.3 防抖双层 + §3.7 已施工设施盘点），原"骨架待重建"临时真源标注改为精确锚点引用（三级升级→33号 §3.2 / budget 变动防抖→33号 §3.3）；② §3.5 盘点表 33号 行同步更新；③ §6 待裁定"33号 文档重建依赖"标记 ✅ 已解决。**遗留未变**：测试套件重建（P0）仍为开放缺口——33号 重建只解决了文档侧，tests/pf_alloc/test_regime_meta_allocator.py（55 用例）仍丢失待重建。frontmatter v2.8.0→v2.8.1 | 二十次审查完成后，另一 AI 会话于 04:32 提交 6a4f5392 重建 7 篇骨架文档（含 33号），本备忘对 33号 的"骨架"引用随之过时，本轮联动修正保持交叉引用准确性（循环审查第 2 轮新发现修复） |
| 2026-08-12 | 2.8.2 | 作战地图环节映射补强——锚定 BM-SEL-20-B | §3.5 末尾补映射块，环节级可追溯 |
| 2026-08-14 | 2.8.3 | 压缩精简：噪音去除+施工细节梳理，零信息丢失审查通过（AI-DOCS-001） | §3.4 伪代码折叠为参数常量表+16 条施工要点（代码本体 production 为真源）；§9 修订记录全量保留；参数表/接口契约/触发条件零丢失 |
| 2026-08-15 | 2.8.4 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-10） | 过程性标签清理（"N 次审查新增/修复/补充"等审查轮次注记，修订记录已承载审查史）；§6 待裁定表机制描述改指 §5.2 真源（Sticky 行"第六条"笔误修正为第十六条）；§8.1 引用表"关系"列散文压缩为定位+指针（来源/链接/关键数据/支撑关系逐项保留）；参数表/G04 校准触发/裁定/跨文档链接零丢失 |
| 2026-08-15 | 2.8.5 | 测试套件重建闭环（AI-REGIME-001 施工）：§3.1 丢失标注→✅ 已重建；§3.5 盘点表测试套件行 ❌→✅ + 盘点结论"唯一缺口"表述清除；§6 待裁定 P0 行标 ✅ 已解决 | 原 55 用例 2026-08-11 git 灾难丢失（从未提交不可恢复），按 §3.4 伪代码 16 条施工要点 + 代码本体回建（8 类 55 用例，两轮 55/55 全绿），重建后立即提交 git 闭环灾难教训；文档同步反映防护网恢复 |
