---
ttl: permanent
doc_type: architecture_view
title: 多策略并发架构
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.6.1"
date: 2026-08-15
topic: multi_strategy_concurrency
scope: 07_trading_decision_architecture
---

## 结案报告（AI-NIGHT-001 复核 2026-08-19）

> **实际开发**：Model A 四模块全部落码——StrategyBook（MOD-POS-020）/FirmRiskAggregator（MOD-POS-021）/BudgetChangeHandler（MOD-POS-022）/RegimeMetaAllocator（MOD-PA-007）。施工分四批：第一批 AI-POS-001（31 号仓位算法+§2.8 漂移再平衡）、第二批 AI-FRA-001（32 号 P0 字段名漂移修复）、第三批 AI-BGT-001（33 号三级升级）、第 4 批 AI-REGIME-001（34 号测试套件重建 55 用例+蓝图对齐）。灾后重建三项（4 测试文件丢失/capability 补登/depgraph maturity 滞后）已分别由 AI-POS/FRA/BGT/REGIME/XCUT-002/REGF-001 批次闭环，depgraph 四节点经 #ARCH-70 通道转 stable+production。
>
> **最终成果**（2026-08-19 代码实证）：`strategy_book.py`（688 行，`VolatilityInfo`+`_is_vol_anomaly` 4 检查链+`SentimentStageSignal`+`rebalance_to_budget`+`size_positions` 三模式，MATURITY=production）；`firm_risk_aggregator.py`（673 行，`pre_kelly_aggregate`/`post_kelly_clip` 两段+`LIQUIDITY_SEVERE_PCT=0.20`/`LIQUIDITY_MODERATE_PCT=0.10` ADV 裁剪，production）；`budget_change_handler.py`（548 行，`TierLevel`+防抖双层+`strategy_type`，production）；`regime_meta_allocator.py`（586 行，`allocate()` 5 步+CRISIS floor 0.09→0.05+water-filling 投影，production）。四测试套件重建（25/60/33/55 用例）均在位。
>
> **未做事项及原因**：
> - `cold_start_ratio` 参数未落码（§6.7 施工指导要求 RegimeMetaAllocator.allocate() 增加该参数+StrategyBook 冷启动状态机）——全 src 零命中；首批策略未上线，冷启动场景尚不存在，属"等触发"设计内延期（未来工程-小型，随首批策略上线装配）。
> - score→weight 显式转换函数未形式化（§2.2 契约③）——按文档裁定"随 `select_stocks` 抽象接口留给策略子类，待首批策略施工时形式化"，属设计内延期（未来工程-小型）。
> - §6.2 策略间相关性验证（correlation drop rule）未施工——承载文档为 [23 号](23_strategy_correlation_validation.md)，依赖首批策略回测/实盘 PnL，属"等数据"（未来工程-小型）。
> - §6.9 并存旧体系退役裁定（MOD-PA-003/PA-002/PA-004/pf_core 5 示例策略）——文档明示"需人裁定，本备忘不擅自定"，等 Owner 裁决。
> - Bayesian Kelly/Conformal Kelly/Water-Filling/no-trade 半带/MPC/Relaxed Risk Parity——文档已裁 Phase 2/3 远期候选并给重评条件，非施工缺口。
> - ~~§2.4 施工状态注记"481 行"漂移~~ ✅ 本次复核补正（遗留 #36 实证项）：实测 548 行，已就地更正。

# 多策略并发架构

> 本备忘记录多策略并发执行架构的选型推理与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。

## 1. 背景

### 1.1 项目处境
- 个人 + 100% AI 开发，迭代速度极快（3-4 个月达到当前规模）
- 部署目标：A 股个人账户（miniQMT 通道），非机构体量
- 多策略并发需求：5 个候选策略（价值反转 / 动量趋势 / 事件驱动 / 打板 / 多因子）
  > **候选清单更新（2026-08-10，[20 §2.1](20_first_batch_strategies.md) 裁定）**：主升龙头并入打板策略内部（BM-SEL-25-C-1 是打板双引擎融合最强决策输出，独立成策略会 alpha 重叠），多因子作为承载主资金的压舱石 sleeve 新增。原"主升龙头"删除。
- 当前处于施工前阶段，架构一旦落地难以回改，故施工前定上限

### 1.2 核心问题
多策略并发有 4 种架构模型（A 独立账本 / B 因子混合 / C 策略之策略 / D 投票融合），选型决定整个系统的复杂度、归因能力、迭代速度。模型选错会导致技术债滚雪球，且 AI-dev 下归因不清=迭代停滞。

### 1.3 约束条件
- A 股几乎不能做空 → 对冲式优化失效
- T+1 结算 → 策略难以日内翻转，独立账本更顺
- 打板策略容量极小（单票可能仅几万到几十万）→ 必须小账本独立运行
- 情绪周期（冰点/反核/主升/疯狂/退潮）是所有短周期策略的共同隐形驱动 → 策略间相关性可能高于直觉（详见 [28 情绪周期×交易决策](28_sentiment_cycle_trading.md) §3.5：情绪周期领先指数约 14 天，退潮期打板×事件驱动相关性飙升；2026 实证 [bayes-group March Shock](https://www.bayes-group.com/insights/march-shock-multistrat-resilience)：pod shops 因"分散化幻觉"尾部相关性飙升集体亏损 $1-1.5B）
- AI 开发 → 故障隔离与归因清晰度是生存项，不是优化项

## 2. 决策：Model A（独立账本 + firm 风险聚合）

### 2.1 架构定义

每个策略是一个独立 StrategyBook（自带选股+**粗**仓位+风控），firm 层做"求和 + 硬上限裁剪 + **Kelly 精裁决** + regime 风险预算调整"，**没有统一优化器，没有跨策略投票**。

> **分层裁定（2026-08-06，方案A）**：仓位决策分两层——StrategyBook 做"策略层粗仓位"（等权/risk parity，**不用 Kelly**），MOD-POS-001 做"组合层 Kelly 精裁决"。第一性原理：组合级约束（单票上限跨策略叠加）天然在 firm 层；Kelly 需密度预测不宜每策略重复；风险合规与 alpha 解耦防归因纠缠。开源印证：Morwane sleeve(alpha)+risk-parity-throttle(firm) 分层。详见各模块 blueprint（[MOD-POS-020](../../../03_modules/_domain_position/strategy_book/blueprint.md) / [MOD-POS-021](../../../03_modules/_domain_position/firm_risk_aggregator/blueprint.md) / [MOD-PA-007](../../../03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md) / [MOD-POS-022](../../../03_modules/_domain_position/budget_change_handler/blueprint.md)）。
>
> **Fractional Kelly 比例（2026-08-10 行业共识补充）**：firm 层 Kelly 精裁决使用 **Fractional Kelly（25-50% Kelly）**，非 Full Kelly。三源一致：① tradingengineeringlab 2026-06——Full Kelly 假设"精确知道 edge"，实际 edge 是噪声估计，Full Kelly 容忍 50%+ 回撤；② metatronics 2026-03——2% 单笔风险规则 ≈ Fractional Kelly，10 连败@2%=18.3% 回撤（可恢复），@Full Kelly=65.1%（近乎毁灭）；③ astuteinvestorscalculus 2026-06——Fractional Kelly 25-50%，最大仓位 12-15%、多数 5-8%。**A 股适配**：T+1+涨跌停限制使日内损失有界，但隔夜跳空风险大（无隔夜对冲），Fractional Kelly 保守端（25-30%）+ §2.5 四级回撤硬阈值 = 双保险。具体 fraction 值待 [31 仓位算法](31_position_sizing.md) G12 讨论标定。
>
> **选项外更优算法：Bayesian Kelly Criterion（2026-08-10 算法审查补充）**：固定 Fractional Kelly 25-50% 是"一刀切"收缩——大样本过度保守，小样本仍嫌激进。Sukhov 2026-06 提出 **Bayesian Kelly with Parameter Uncertainty**：后验加权替代 plug-in Kelly 分数，收缩系数随有效样本量自适应——
>
> ```
> f* = (p̄ − (1−p̄)/b) · n_eff/(n_eff + κ)
> ```
>
> p̄=α/(α+β) 为 Beta 共轭先验后验均值（胜率），n_eff=α+β 为有效样本量，κ 为正则化强度。**关键性质**：n_eff 小→自动深收缩；n_eff 大→自动放宽到 Full Kelly。
>
> | 方案 | 收缩机制 | 样本自适应 | 实现复杂度 | 推荐 |
> |---|---|---|---|---|
> | **固定 Fractional Kelly 25-50%** | 固定比例 | ❌ | 最简 | Phase 1（当前，[31 号](31_position_sizing.md) 已用半 Kelly 硬上限） |
> | **Bayesian Kelly** | n_eff/(n_eff+κ) 后验收缩 | ✅ | 中（需维护 Beta 先验+后验更新） | **Phase 2 演进**（首批策略 3-6 月 PnL 后标定 κ） |
>
> **定位**：Bayesian Kelly 是 Fractional Kelly 的**自适应演进**（非替代），两者都遵循"风险优先"。详见 [31 仓位算法](31_position_sizing.md) G12 讨论。
>
> **选项外更优算法：Conformal Kelly（2026-08-10 四次算法审查补充）**：Bayesian Kelly 仍依赖"胜率 p + 赔率 b"点估计（虽用后验收缩），Conformal Kelly 直接从**预测区间宽度**推导缩放因子——绕过 p/b 估计。[arXiv:2608.01494v1（Ryan 2026-08-02）](https://arxiv.org/html/2608.01494v1)用 Conformal Prediction 75% 区间宽度作 Fractional Kelly 的 scale：区间宽→收缩，窄→放大。
>
> ```
> f_conformal = f_kelly × (w_ref / w_t)   # w_t=当前区间宽度，w_ref=基准宽度（如历史中位数）
> ```
>
> **核心实证**：6 年窗口（2016-2021，含成本+1 日延迟+杠杆上限）年化净 log 增长 28.5%、Sharpe 1.34、MaxDD 27.7%（vs S&P 500 15.9%、同杠杆被动 21-22%）；区间命中率 74.8%（目标 75%）。
>
> **反直觉发现（印证 §2.2 regime 哲学）**：让区间更快适应 regime 的每次调整损失 0.7-5.3pp 年增长——最优是最简单的 slow/unweighted/per-asset rolling conformal quantiles，**稳定性比局部锐度更重要**。
>
> **回撤控制集成（drawdown dial）**：conformal 区间下行 miss 率远超历史→判模型失效→削杠杆，MaxDD 27.7%→20.3% 且 Sharpe 提升，timing 击败全部 40 个 placebo（rank-based p=1/41≈0.024）——与 §2.5 四级回撤 Protocol 同源（回撤驱动风险节流），但用连续 miss 率替代离散阈值。
>
> **诚实性披露**：Lockbox（2022+ OOS）calibration 保持（0.745 vs 0.750 目标）但**增长未保持**（8.5%/7.0% 每年，低于被动基准）——方法对开发窗口敏感，实盘需谨慎。
>
> | 方案 | 缩放机制 | 依赖估计 | 回撤集成 | OOS 诚实性 | 推荐 |
> |---|---|---|---|---|---|
> | **固定 Fractional Kelly 25-50%** | 固定比例 | 胜率/赔率 | ❌ | — | Phase 1（当前） |
> | **Bayesian Kelly** | n_eff/(n_eff+κ) 后验收缩 | Beta 先验+胜率 | ❌ | — | Phase 2 演进 |
> | **Conformal Kelly** | conformal 区间宽度比 | 预测模型（不需 p/b） | ✅ drawdown dial | ✅ Lockbox 披露 | **Phase 3 远期候选** |
>
> **为何远期而非 Phase 2**：① 需可靠预测模型产出 return 区间（当前 alpha 信号输出仓位/target_portfolio 非 return 分布）；② Lockbox OOS 增长未保持，需充分验证；③ Bayesian Kelly 已解决"样本自适应"核心问题，Conformal Kelly 边际收益在"绕过 p/b+回撤集成"。**重评条件**：Phase 2 Bayesian Kelly 跑 6+ 月后若 p/b 估计噪声致 Kelly 分数不稳定，评估 Conformal Kelly 替代。详见 [31 仓位算法](31_position_sizing.md) G12 讨论。

### 2.2 三个核心模块

> **施工状态（2026-08-12 核对源码）**：**四模块全部 production**——StrategyBook（MOD-POS-020，680 行）+ FirmRiskAggregator（MOD-POS-021，651 行）+ BudgetChangeHandler（MOD-POS-022，572 行）+ RegimeMetaAllocator（MOD-PA-007，594 行）。先定接口后填实现：A 模型落地难回改，接口契约是 sleeve/firm/meta 三层协作边界，先冻结边界防归因纠缠。
> - A 模型核心数据流 StrategyBook→FirmRiskAggregator→MOD-POS-001 已贯通（三模块 v2.3.0~v2.4.0 施工完成）
> - RegimeMetaAllocator：`allocate()`/`_compute_shrinkage()`/`_normalize_and_clip()`/`compute_performance_score()` 全实现，FLOOR=5%/CAP=40% 硬约束在位；**C1 验证已通过**（commit 852457e9，Shrinkage 节流有效：MaxDD 改善 +7.36pp，Calmar +27%）。**"代码 production"≠"上线"**：参数（Base 权重/PerformanceScore 映射/四档阈值）待首批策略 3-6 月 PnL 校准，上线仍第二阶段（P3）
> - §2.5 回撤 Protocol 相关模块（drawdown_controller 603 行 / drawdown_tracker 332 行 / var_calculator 394 行 / kill_switch 归 D-RISK）**已先于三模块施工至 production**（见 §2.5 why 补全）
> - ⚠️ **测试文件丢失（2026-08-11 git clean 灾难，#ARCH-GIT-CLEAN-GUARD-FIX）**：4 个测试文件（70/54/47/55 共 226 测试）2026-08-10 创建后未 `git add`，2026-08-11 `git clean -fd` 被删且 git 历史无记录——"171+55 测试全绿"当前工作区无法复现，重建登记 §6.8。教训：新建文件必须立即 `git add`

#### StrategyBook（N 个，N=3~5）
- 输入：策略自己的 alpha 信号 + 情绪周期阶段信号（[28号](28_sentiment_cycle_trading.md) §3.5，见下方接口契约）
- 内部：自带仓位算法（Kelly / risk parity / 简单等权，**不用 MVO**）
- 输出：target_portfolio（标的+目标仓位，权重口径=相对 strategy_budget 占比，见下方声明）
- 独立 PnL 归因、独立风控参数、独立资金预算

> **StrategyBook 输入/输出接口契约（v2.2.0 补，跨文档算法交接完整性审查——链路 2/6 缺口修复）**：
>
> **① 情绪周期阶段信号接口**（[28号](28_sentiment_cycle_trading.md) → 30号 StrategyBook，链路 2 缺口修复）：28号定义 5 阶段情绪周期（冰点/反核/主升/疯狂/退潮）+ BOCPD/CUSUM 检测，退潮阶段触发卖出信号加权。StrategyBook 通过以下数据结构接收情绪周期阶段信号：
> ```
> SentimentStageSignal:
>   stage: str             # 当前情绪阶段 ∈ {冰点, 反核, 主升, 疯狂, 退潮}
>   confidence: float      # BOCPD 后验概率 [0,1]，<0.6 触发降级（见下方降级路径）
>   retreat_weight: float  # 退潮加权系数，仅退潮阶段非 1.0（默认 1.5，见下方说明）
>   timestamp: datetime
> ```
> - **退潮加权系数**：退潮阶段（`stage="退潮"`）时，StrategyBook 内部卖出信号权重 × `retreat_weight`（默认 1.5，可按策略类型差异化：打板 1.5 / 事件驱动 1.3 / 多因子 1.2——打板对情绪退潮最敏感）。非退潮阶段 `retreat_weight=1.0`（无加权）。28号 §3.5 已定义退潮期打板×事件驱动相关性飙升，此系数是 sleeve 内 alpha 择时的实现机制
> - **降级路径**：28号未就绪或 `confidence<0.6` 时，StrategyBook 降级为 regime ⑧加速下跌信号（§3.5 已定义降级路径），`retreat_weight` 回退为 1.0（不加权）。此降级路径完整，不影响 firm 层统一风险框架
> - **与 regime 的正交性**：情绪周期是 sleeve 内 alpha 择时（买卖什么），regime 是市场级风险节流（多谨慎），两者正交（[28号](28_sentiment_cycle_trading.md) §3.1 + §3.5 已定型）。情绪周期信号不直接被 Shrinkage 消费（[10号](10_regime_detector_spec.md) §2.5.3）
>
> **② target_portfolio 权重口径声明**（[32号](32_firm_risk_aggregator.md) → 30号 交接，链路 6 缺口 1 修复）：`target_portfolio` 中每个 `TargetPosition.target_weight` 是**相对各自 strategy_budget 的占比**（非相对总资金的绝对权重）。[32号](32_firm_risk_aggregator.md) §2.2 据此做 budget 口径归一化：`account_weight = tp_weight × budget_used / total_budget`。若 StrategyBook 实现者误输出绝对权重（相对总资金），将导致 32号 budget 口径统一 double-count。**施工注记**：`strategy_book.py`（MOD-POS-020）施工时须在 `target_portfolio` 输出注释中显式声明此口径
>
> **⚠️ 字段名三方漂移（2026-08-12 代码核对，v2.6.0 补）**：代码真源 `TargetPortfolio` dataclass（strategy_book.py）字段为 **`positions: dict[str, TargetWeight]` + `budget`**（非本文档伪代码的 `target_portfolio` / `budget_used`，且 `positions` 值是 `TargetWeight` 对象非裸 float）；`firm_risk_aggregator.py` 的 `_sum_by_symbol()` 按 `target_portfolio`/`budget_used` duck-typing 取值——**直接传入 TargetPortfolio 对象会静默取空默认值得出全现金组合**（断裂不报错）。权重口径声明本身已在代码落实（`TargetWeight` docstring 明示"相对 strategy_budget 的占比"），但字段名对齐属 P0 接口修复项，登记 [32号 §6](32_firm_risk_aggregator.md) 开放问题
>
> **③ score→weight 转换接口**（[25号](25_multifactor_strategy_detail.md) IC 加权合成 → [21号](21_stock_selection_engine.md) 选股 → 30号 StrategyBook 仓位算法，链路 6 缺口 2 文档化）：25号 IC 加权合成产出复合因子评分（[21号 §3.3](21_stock_selection_engine.md) 归一化[-3,3]），非 target_portfolio 权重。评分→权重转换在 StrategyBook 内部完成（三维度解耦：选股=评分排序 top-N / 仓位=Kelly·risk_parity·等权 / 风控=独立参数）。`size_positions()` 已实现 equal_weight/risk_parity/custom，但 score→weight 的**显式转换函数**（composite_score[-3,3]→仓位权重映射）随 `select_stocks` 抽象接口留给策略子类，待首批策略施工时形式化，登记为 §6.7 冷启动执行比例的配套施工项

#### FirmRiskAggregator（1 个，O(N) 复杂度）
- 输入：所有 StrategyBook 的 target_portfolio
- 处理：
  1. 按标的求和
  2. 单票硬上限裁剪（如 >8% 按比例削）
  3. 行业/总仓位硬约束
  4. 冲突标的处理（一策略买一策略卖 → 按净额或按优先级）
- 输出：firm_target_portfolio → 下单
- **不做 MVO，不做协方差估计**，只做求和+裁剪

#### RegimeMetaAllocator（1 个，第二阶段上）
- 输入：市场状态**灰度概率分布**（12 维，非硬标签）→ **仅用于 Shrinkage 风险节流** + 各策略近期滚动收益（PerformanceScore）
  > **设计与实现口径（2026-08-10）**：12 态是 [10_regime_detector_spec](10_regime_detector_spec.md) 的设计真源（9 基础 3×3 + 3 特殊覆盖层）；C1 验证实际跑的是 **4 态 HMM**（[34 §2.3](34_regime_meta_allocator.md)：r1低波27.6%/r2中波37.4%/r3牛市14.9%/r4熊市20.2%，无<1%稀有态）。12 态=设计目标，4 态=当前已验证实现。本节"12 维"按设计真源表述，实际接入以 10号/11号/34号 实现态为准。
- 输出：各 StrategyBook 的**资金预算占比**（不是选股权重，不是仓位权重）
- 分配公式：

  ```
  allocation_i = normalize( Base_i × PerformanceScore_i × Shrinkage_i )
  ```

  > **裁定（2026-08-05）：移除 RegimeScore，regime 仅通过 Shrinkage 做风险节流。**
  > 开源实证：regime-based alpha 择时降低收益（检测器误差被主动重定向放大），regime-based 风险节流改善回撤（防御性，误差容忍）。
  > 误差不对称：alpha 择时判错=主动亏损，风险节流判错=机会成本。RegimeScore 在 meta 层重新引入估计误差放大，与 A 模型"加法替代优化器"哲学矛盾。
  > 策略亲和性由 PerformanceScore（后验 PnL）自然捕获——momentum 在趋势态表现好→滚动 Sortino 上升→有机获得更多 budget，无需 regime 前瞻下注。

  | 因子 | 含义 | 关键纪律 |
  |---|---|---|
  | Base_i | 先验权重（等权 1/N 或人工先验） | 新策略冷启动只用这个 |
  | PerformanceScore_i | 策略 i 近期滚动风险调整收益（60 日 **Sortino**，非 Sharpe——Sortino 只惩罚下行波动，符合"上行波动是好的"直觉） | 映射 [0.5, 1.5]，防极端；后验 PnL 自然捕获 regime 亲和性。**口径对齐 [34 §3.1](34_regime_meta_allocator.md)**：34 号 RegimeMetaAllocator 真源用 Sortino，本备忘原写 Sharpe 已修正 |
  | Shrinkage_i | regime 置信度 + 信号可靠性综合收缩，**≤1.0（只减不增）** | regime 唯一入口；见下方置信度→风险节流映射；样本<30 天额外收缩 |

- 硬约束：floor ≥ 5%（防饿死），cap ≤ 40%（防集中）
- **置信度→风险节流映射**（max(P) 为当前最高态概率，来自 regime 检测器灰度输出；仅控制 Shrinkage，**不重定向资金**）：
  - max(P) < 60% → 强收缩（Shrinkage→0.3），回退等权/指数（"不确定时别赌方向"）
  - max(P) 60-80% → 中度收缩（Shrinkage→0.6），整体保守部署
  - max(P) 80-95% → 轻度收缩（Shrinkage→0.85），正常部署
  - max(P) > 95% → 接近无收缩（Shrinkage→1.0），满部署
- 稀有态处理：按态频率差异化收缩（常见态>5%轻收缩，中等态1-5%中度收缩，稀有态<1%重收缩——稀有态检测置信度天然低）
- **市场态是 meta 层的事，策略本身不知道市场态，只收到 budget 数字**
- **regime 只回答"现在该多谨慎"，不回答"现在该偏向哪个策略"——后者由 PerformanceScore 后验决定**

### 2.3 关键特性：自然叠加
多策略选到同一只票时，仓位自然叠加（S1 给 5% + S2 给 5% = 10%）。这等价于一个永远稳定的等权 risk-budget 优化器，无需调投票权重，无需估协方差。这是 A 模型最被低估的优点——用加法替代优化器，O(N) 替代 O(N²)。

> **多策略组合预期 Sharpe 基准（2026-08-10 行业实证补充，出处见 §7.4 vzeman）**：cross-sectional momentum (12-1) gross Sharpe ~0.85 / net ~0.65（volatility-scaled 风险调整收益翻倍）；time-series/dual momentum net Sharpe 0.6-0.8；学术回测 headline 实盘打 20-50% 折扣。
>
> **校准意义**：Model A 多策略组合（打板/多因子/事件驱动）预期 net Sharpe 基准 **0.6-0.85**——"加法替代优化器"不引入协方差估计误差的合理上限。A 股 T+1+涨跌停+不能做空使预期略低于美股全景，但 volatility-scaled（§2.1 Fractional Kelly + §2.2 Shrinkage）的"风险调整收益翻倍"效应仍适用。实盘 net Sharpe <0.5 提示策略间相关性过高（§6.2 必做验证）或单策略 alpha 不足；>1.0 需警惕过拟合。对照 [Morwane OOS 2013-2026](§7.4) risk-throttle Sharpe 1.43（两 sleeve 弱相关 ρ=+0.03）——弱相关 sleeve 组合可达 Sharpe >1，但需 sleeve 更多且相关性极低，本项目 3 策略起步以 0.6-0.85 为合理预期。

> **A 股 2026 上半年量化超额衰减警示（2026-08-10 市场环境校准补充）**：[新浪财经 2026-07-11](https://finance.sina.com.cn/jjxw/2026-07-11/doc-inihmkxc5002361.shtml)——2026H1 A 股量化多头平均收益 16.25%（与 2025 同期持平），但**平均超额从 14.17% 骤降至 3.11%**（中证 500 指增超额仅 0.85%）——收益主要来自 Beta。
> - **三根因**：① K 型行情——4-5 成成交额集中前 5% 热门科技股，分散持仓的非热点中小盘滞涨；② 因子失效+策略同质化——机构共用相似价量因子框架，超额被摊薄；③ 风格错配——资金偏好科技成长/动量，低估值低波因子弱势
> - **校准意义**：A 股 2026 纯横截面多因子 alpha 获取难度飙升，印证 [34 §4.1](34_regime_meta_allocator.md) "regime 做 alpha 择时降 Sharpe"。Model A"风险节流不做 alpha 择时"+ §6.2 相关性验证 + [28 情绪周期](28_sentiment_cycle_trading.md) sleeve 内择时的组合更稳健：多因子 sleeve 超额预期从 0.6-0.85 **下调**，打板 sleeve 情绪周期择时（与横截面 alpha 正交）连板回暖期仍可获超额
> - **实盘预期管理**：首批 3 策略实盘 6 月后若组合 net Sharpe <0.3（低于基准一半），优先排查策略间相关性（§6.2）而非单策略 alpha——K 型行情下"相关性飙升"比"alpha 不足"更可能是根因

> **叠加超限裁剪算法（2026-08-10 补充）**：自然叠加后若超过 firm 层单票硬上限（如 8%），须裁剪。裁剪算法（FirmRiskAggregator `MOD-POS-021` 已施工）：
>
> | 裁剪方式 | 算法 | 优点 | 缺点 | 适用场景 |
> |---|---|---|---|---|
> | **A: 按比例缩放（pro-rata）** | `adj_i = raw_i × (cap / Σraw)`，所有策略同比例缩减 | 最简，O(N)；不偏袒任何策略 | 高信心策略被同等缩减，信号失真 | **首选**（A 模型"加法替代优化器"哲学延伸——不做优先级判断） |
> | **B: 按 PerformanceScore 优先级** | 低 PerformanceScore 策略先砍，保高 score 策略仓位 | 保留"好策略"完整仓位 | 引入优先级=引入优化器特征；归因纠缠 | 不采用（违背 A 模型哲学） |
> | **C: 按策略类型优先级** | 打板 > 事件驱动 > 多因子（或自定义优先级） | 人工可控 | 人工优先级=技术债 | 不采用 |
>
> **裁定**：选 **A（按比例缩放）**。理由：A 模型核心是"加法替代优化器"——叠加超限时做优先级裁剪（B/C）等于在 firm 层引入优化器特征，破坏归因清晰度。pro-rata 是唯一与 A 哲学一致的裁剪方式，O(N) 且不偏袒。裁剪日志须记录各策略原始仓位→裁剪后仓位，供归因复盘。
>
> **行业印证**：Morwane risk-parity 用 inverse-vol 权重（非优先级），叠加超限时按 vol 比例缩放——本质是 pro-rata 的变体。Citadel pod 模型中 PM 间仓位冲突由 risk desk 按固定规则（非优先级）裁剪，非"谁好谁优先"。
>
> **选项外更优算法：Clipped Water-Filling（2026-08-10 算法审查补充）**：pro-rata"同比例缩减"在 minimax 意义下非最优。arXiv:2603.26893（2026-03）证明 **Water-Filling 在在线可分资源分配中普遍 minimax 最优**（对任何 Schur-单调目标函数）；arXiv:2603.15963（2026-03）多资产交叉保证金场景 Clipped Water-Filling 实证优于 pro-rata。直觉：把预算"注"到各策略直到水位齐平（max-min fairness），而非按比例削。
>
> | 裁剪方式 | minimax 最优性 | 与 A 模型哲学一致性 | 复杂度 | 裁定 |
> |---|---|---|---|---|
> | **pro-rata 按比例缩放** | 次优 | ✅ 完全一致（不偏袒） | O(N) | **Phase 1 首选**（当前裁定） |
> | **Clipped Water-Filling** | ✅ minimax 最优 | ⚠️ 部分——"填平"隐含小仓位优先 | O(N log N) | **Phase 2 候选**（若 pro-rata 显示信号失真） |
>
> **为何 Phase 1 仍选 pro-rata**：A 模型叠加超限是"轻微超限"（如 8% 上限超出 1-2%），此时两者差异极小；且 pro-rata 与"不偏袒"哲学完全一致。**重评条件**：实盘若 pro-rata 裁剪致高信心策略被过度缩减、归因显示"裁剪失真"，升级到 Water-Filling。

### 2.4 权重变动操作流程

**核心原则**：budget 是硬约束（来自 meta 层），策略的自主权在"怎么适应 budget"，不在"要不要适应"。策略必须实现 `rebalance_to_budget(new_budget)` 接口，返回适配新 budget 的 target_portfolio——策略不能说"我不卖"。

#### Budget 增加（策略 i 预算上调）—— 简单
- 直接抬高 budget 上限
- 策略通过自己的买入信号自然部署新资金
- 不需要强制动作；现金拖累可接受（现金也是一种仓位）
- 唯一约束：新买入后总暴露 ≤ 新 budget

#### Budget 减少（策略 i 预算下调）—— 三级升级

| 级别 | 动作 | 触发时机 | 性质 |
|---|---|---|---|
| Tier 1 | 封锁新仓（StrategyBook 不允许开任何新仓，现有仓位不动） | budget 下调瞬间 | 立即，被动 |
| Tier 2 | 发送 rebalance_to_budget 信号，策略自选砍哪些仓位（砍最不自信的） | Tier 1 后立即 | 建议，策略自主 |
| Tier 3 | 按比例强行裁剪所有仓位（dumb but safe） | Tier 2 窗口超时 / firm 风险违例 | 强制，firm 层 |

- 高换手策略（打板）：Tier 1+2 通常 1-2 天自然收敛，Tier 3 不触发
- 低换手策略（多因子）：Tier 1+2 给时间，Tier 3 兜底防死扛
- 每级是独立事件，可 log 可复盘
- 三级升级而非直接强砍：尊重策略自主权（决定砍哪个）+ 避免随机时刻强制卖出的高成本

> **施工状态（2026-08-10 核对源码）**：✅ `budget_change_handler.py`（MOD-POS-022）**已施工 production**——`TierLevel` 枚举 + `FreezeNewPositions`/`RebalanceRequest`/`ForcedTrim` 三指令 dataclass + `TierState` 状态机 + `handle_budget_change`/`check_convergence` 及三级指令生成方法全部实现（548 行，0 处 NotImplementedError；2026-08-19 复核实测，原注"481 行"为 2026-08-10 旧值）。`convergence_windows` 默认值已按 [20 §6.4](20_first_batch_strategies.md) 预置（打板 2 天 / 多因子 4 天 / 事件驱动 3 天）。**为何三级而非直接强砍**：直接强砍=随机时刻卖出高成本+剥夺策略归因；三级让策略在窗口内自选砍哪个（保留归因），超时 firm 层 dumb-but-safe 兜底（保生存）。依赖 StrategyBook 的 `rebalance_to_budget` 接口（已 production）。⚠️ **33 号骨架化（2026-08-12 核对）**：33 号在 2026-08-11 git 灾难中内容丢失回退至骨架 v0.1.0，G14 设计真源待重建；当前三级升级接口契约以 `budget_change_handler.py` 头部 docstring（INVARIANTS/TierLevel/收敛检测三条件）为临时真源，重建登记 §6.8。
>
> **Tier 2→Tier 3 收敛检测算法（2026-08-10 补充）**：`check_convergence()` 须定义"策略是否在窗口内收敛"的判定标准。算法：
>
> ```
> 收敛条件（同时满足）：
>   ① 仓位差收敛：|实际总仓位 - target_budget| / target_budget < ε_pos（建议 ε_pos=5%）
>   ② 持续性：上述条件连续维持 ε_days 日（建议 ε_days=1，即 1 个交易日）
>   ③ 无新违例：窗口内无新的 firm 层风险违例（如单票超限未纠正）
>
> 超时触发 Tier 3：convergence_window 内未满足收敛条件 → ForcedTrim 按比例强裁
> ```
>
> **为何 ε_pos=5%**：A 股 T+1 无法当日即时调仓，5% 容差给 1-2 日自然调仓空间（打板高换手 1-2 天自然收敛，[20 §6.4](20_first_batch_strategies.md)）。太小（1%）→ Tier 3 频繁误触发；太大（15%）→ budget 下调形同虚设。5% 是"T+1 自然收敛"与"budget 约束有效"的平衡点，待实盘校准。
>
> **选项外更优算法：最优 no-trade 半带公式（2026-08-10 算法审查补充）**：固定 ε_pos=5% 是经验值，无理论根基。stockalpha.ai 2026-02 给出基于布朗运动首达时间的闭式解——
>
> ```
> b* = [3·c·σ² / (2·λ)]^(1/3)
> ```
>
> 其中 c=往返交易成本（A 股约 0.15%：佣金 0.025%×2 + 印花税 0.05% + 滑点 0.05%），σ=年化波动率（A 股个股 ~30-40%），λ=跟踪误差惩罚。也可从目标 TE 反推：**b = TE_target · √3**（若目标 TE=3%，则 b≈5.2%，与经验值 5% 吻合）。比固定 ε 的优势：①交易成本与波动率显式纳入；②立方根缩放对参数误指稳健（σ 估错 2× → b 仅变 1.26×）；③各策略可按自身 σ 差异化（打板 σ 高→带宽宽，多因子 σ 低→带宽窄）。
>
> **裁定**：Phase 1 用固定 ε_pos=5%（简单，且与 TE·√3 经验吻合）；Phase 2 实盘后有各策略 σ 数据后，升级为 b*=[3cσ²/(2λ)]^(1/3) 按策略差异化。详见 [33 BudgetChangeHandler](33_budget_change_handler.md)。

### 2.5 StrategyBook Drawdown Protocol（账户级回撤风控，2026-08-05）

> **用户裁定（2026-08-05）**：回撤是沉没成本，不参与下一次决策（不进入 RiskSignal），但触发账户级风险节流（减仓/停仓/清仓）。
> **定位**：drawdown protocol 是 StrategyBook 内部风控，不属于 regime 检测器的 RiskSignal。regime 管"市场状态风险"，drawdown protocol 管"账户生存风险"。
> **行业搜索**：LedgerMind Systematic Risk Framework 2026-05、ARKA Global Investments 2026、Sina 量化风控 2026-07、Sina 量化FOF 2026-07、tradingwyckoff Drawdown Guide 2026-01、赢牛资管 VaR-ES 2026-05。

> **施工状态与 why 补全（2026-08-10 核对源码）**：本 Protocol 相关模块**已先于 §2.2/§2.4 三模块施工至 production**——`drawdown_controller.py`（MOD-POS-008，488 行）、`drawdown_tracker.py`、`var_calculator.py`、`kill_switch.py`（均 production）。**为何回撤风控先于 alpha 账本**：用户原则"风险优先于收益"——生存底线是 alpha 迭代的前提；且回撤风控不依赖选股逻辑，可独立先建。**为何四级硬阈值而非软优化**：硬阈值=fail-closed 生存底线，软优化=fail-open 风险（优化器可能"优化"掉保护）；四级 8/15/20/25% 是行业基准（LedgerMind/ARKA/Sina FOF 2026 共识），非自创。
>
> **⚠️ 文档与实现口径漂移（待核对）**：本文 §2.5.1 定义的"四级回撤阈值 8/15/20/25%"是**交易决策层视角**的账户净值回撤阶梯；源码 `drawdown_controller.py` 实现的是**仓位域视角**的"5 级系统性风险 GREEN/YELLOW/ORANGE/RED/BLACK（VaR<2%/2-4%/4-6%/>6%/CVaR>10% 驱动）+ 策略级止损 Soft(单策略回撤>5%)/Hard(>10%) + 7 黑天鹅模式 BS-001~BS-007"。两者是同一 Protocol 的不同层级表达（交易决策层=净值回撤阶梯；仓位域=VaR 驱动的响应级别），但颗粒度与触发量纲不同，须在 G13 FirmRiskAggregator / G14 风控细节讨论中明确两视角的映射关系，防止"四级"与"五级"并存导致执行歧义。drawdown_controller 消费组合回撤+VaR/CVaR 产出分级响应，定位为**组合级**（MOD-POS-001 仓位上限调整的消费者），非纯 StrategyBook 内部——与本文 §2.5.3"单策略 vs 组合层面分层"一致。

#### 2.5.1 四级回撤阈值（行业基准）

> **行业基准**（LedgerMind 2026-05 / ARKA 2026 / Sina 量化FOF 2026-07）：

| 级别 | 回撤阈值 | 动作 | 行业来源 |
|---|---|---|---|
| **Level 1: 警告** | 回撤 > 8% | 降低新仓风险敞口至 75%（单笔风险从 2% 降至 1.5%） | Sina 量化FOF 2026-07：8% 减仓启动线 |
| **Level 2: 减仓** | 回撤 > 15% | 仓位缩减至 75%，停开新仓（仅允许平仓和调仓） | LedgerMind 2026-05：15% reduce to 75% |
| **Level 3: 停仓** | 回撤 > 20% | 停止所有新开仓，review framework | LedgerMind 2026-05：20% halt new positions |
| **Level 4: 清仓** | 回撤 > 25% | 关闭所有仓位，强制休息 | LedgerMind 2026-05：25% close all, mandatory break |

> **日度熔断**（补充）：
> - 组合单日亏损 > 4% → 暂停开仓 1 天（Eastmoney 2026-07：组合熔断）
> - 单策略单日亏损 > 5% → 该策略暂停 1 天

> **回撤恢复不对称数学（2026-08-10 补充，支撑阈值合理性）**：回撤与恢复非对称——损失在当前资本上发生，恢复须在更小余额上赚取。恢复所需收益 `Recovery = D / (1 - D)`：
>
> | 回撤 D | 剩余 | 恢复所需 | 本项目对应级别 |
> |---|---|---|---|
> | 8% | 92% | +8.7% | Level 1 警告（可恢复） |
> | 15% | 85% | +17.6% | Level 2 减仓（尚可恢复） |
> | 20% | 80% | +25.0% | Level 3 停仓（需 review） |
> | 25% | 75% | +33.3% | Level 4 清仓（强制休息） |
> | 50% | 50% | +100% | （不可承受——需翻倍） |
>
> 来源：tradingengineeringlab 2026-06 / astuteinvestorscalculus 2026-06 / metatronics 2026-03 三源一致。**为何阈值定在 25% 而非 30%/40%**：25% 需 +33% 恢复（按 10% 年化约 3 年）尚可承受；30% 需 +43%，50% 需 +100%——恢复成本凸性增长，25% 是"恢复尚可行"与"防灾难性损失"的临界点。Level 4 后强制休息 5 天给"恢复 +33%"留心理空间，避免情绪化加码。

#### 2.5.2 恢复机制（Recovery Protocol）

> **行业共识**（ARKA 2026）：Recovery requires explicit re-authorization. 不能自动恢复。

| 阶段 | 条件 | 动作 |
|---|---|---|
| **回撤企稳** | 回撤从峰值恢复 50%（如从 -20% 回到 -10%） | 解除停仓，允许新仓但风险敞口仍降 50% |
| **完全恢复** | 创新高（回撤归零） | 恢复正常风险敞口 |
| **强制休息期** | Level 4 触发后 | 强制休息 5 个交易日，期间不允许任何交易 |

#### 2.5.3 单策略 vs 组合层面（分层风控）

> **用户洞察**："回撤深了是因为上一次交易没交易好，是策略的问题，不是市场的问题。"
> → 单策略回撤 = 策略问题 → 该策略独立收缩
> → 组合回撤 = 系统性问题 → 全局收缩

| 层面 | 回撤基准 | 触发动作 |
|---|---|---|
| **单策略层面** | 各 StrategyBook 自身净值回撤 | 该策略独立减仓/停仓，不影响其他策略 |
| **组合层面** | firm 层总净值回撤 | 所有策略同步收缩（通过 Shrinkage 额外下调） |

#### 2.5.4 VaR/ES 辅助监控（前沿补充）

> **来源**：Sina 量化风控 2026-07 / 赢牛资管 2026-05

| 指标 | 定义 | 触发 |
|---|---|---|
| **VaR_95** | 95% 置信下日度最大预期损失 | VaR > 1.2×入场 VaR → 减仓 20% |
| **ES_95** | 超过 VaR 时的预期平均损失 | ES > 1.3×入场 ES → 再减仓 20% |
| **波动率调整** | 30 日波动率 | 每增 10% → 仓位减 20%（LedgerMind 2026-05） |

#### 2.5.5 Kill Switch（紧急熔断）

> **来源**：tradingwyckoff 2026-01 Kill Switch Protocol

| 触发条件 | 动作 |
|---|---|
| 单日亏损 > 6% | 立即平仓所有持仓，暂停交易 3 天 |
| 回撤 > 25% | 清仓 + 强制休息 5 天 + 人工 review |
| 连续 5 天亏损 | 降仓至 50%，review 策略有效性 |
| 流动性危机（买卖价差 > 正常 5x） | 立即停止开仓，仅允许平仓 |

> **Kill Switch 原则**：宁可错杀不可漏放。触发即执行，不允许人工覆盖延迟。

#### 2.5.6 过度工程审查：VaR/ES 与 Kill Switch 对个人项目是否过重（2026-08-10）

> **结论：Kill Switch 保留（生存底线，mandatory）；VaR/ES 5 级 + 7 黑天鹅模式建议分级降级——保留计算与监控，但活跃节流层级精简。**

**审查对象**：源码 `var_calculator.py`（production，323 行）、`kill_switch.py`（production，264 行）、`drawdown_controller.py`（production，488 行，含 5 级系统性风险 + 7 黑天鹅模式 BS-001~BS-007）。

| 组件 | 对个人项目是否过重 | 裁定 | 理由 |
|---|---|---|---|
| **Kill Switch**（单日>6%/回撤>25%/连5亏/流动性危机） | ❌ 不过重 | **保留为 mandatory 生存底线** | 单账户无机构的多层对冲缓冲，Kill Switch 是 fail-closed 最后一道闸；tradingwyckoff 2026-01 行业共识；触发即执行不可覆盖=防 AI-dev 下"再等等"的人性弱点 |
| **四级回撤阈值 8/15/20/25%** | ❌ 不过重 | **保留** | 行业基准（LedgerMind/ARKA/Sina FOF 2026），非自创；硬阈值=fail-closed，软优化=fail-open 风险 |
| **VaR/ES 计算**（var_calculator） | ⚠️ 边界 | **保留计算+监控，活跃节流层级精简** | VaR/ES 作为"监控仪表盘"对个人项目有价值（看见风险浓度）；但作为 5 级活跃节流触发器（GREEN/YELLOW/ORANGE/RED/BLACK 自动调仓位上限）对个人 A 股小账户偏重——A 股 T+1+涨跌停已天然限制日内损失，5 级 VaR 节流的边际收益低于维护成本。建议：保留 VaR/ES 计算与告警，活跃节流以四级回撤为主，VaR 5 级作为"辅助参考"而非主节流轴 |
| **7 黑天鹅模式 BS-001~BS-007** | ⚠️ 偏重 | **保留框架，模式数等实盘验证后裁剪** | 7 模式覆盖跨市场暴跌/流动性枯竭/政策黑天鹅等，框架合理；但个人 A 股账户能遇到的极端模式有限（无衍生品、无跨境、T+1），7 模式中部分可能永不触发。建议：先保留框架与日志，实盘跑 6-12 月后看哪些模式真正触发过，未触发的降级为"监控"而非"自动响应" |

**总体裁定**：回撤风控先于 alpha 账本施工至 production，方向正确（生存优先），但 production≠定稿——5 级 VaR 节流 + 7 黑天鹅模式是从机构级框架继承的完整集，对个人项目存在"建了未必用"的过度风险。遵循 charter 约束五"少而精"原则，G13/G14 风控细节讨论按两层处置：① Kill Switch + 四级回撤 = 真红线（mandatory）；② VaR 5 级 + 7 黑天鹅 = 监控层（先全建+全 log，实盘验证后裁剪未触发项）。这与 [Trium Capital 2026-06](https://wealthdfm.com/viewpoint-not-all-multi-strategy-funds-are-built-the-same/) 的"止损是 review 信号"形成对照——个人系统取 pod 的硬纪律（防 AI-dev 软弱），但用"监控 vs 红线"分层避免机构级全量自动化的维护负担。

#### 2.5.7 回撤度量补充与 EVT 尾部层（2026-08-10 算法审查补充）

> **本节定位**：§2.5.6 过度工程审查后，补充两个"度量层"增强——不替代四级硬阈值触发器（生存红线），而是提供更平滑的**离线度量**与**数据驱动尾部检测**。

**① CDaR（Conditional Drawdown-at-Risk）——回撤路径度量补充**

固定四级阈值 8/15/20/25% 是"单点 maxDD"触发器——只看回撤峰值，不看回撤路径。CDaR（Chekhlov-Uryasev-Zabarankin 2003，2026 仍主流）对回撤序列的最差 α% 尾部取平均：α→0 收敛于 maxDD，α→1 收敛于平均回撤（pain index）。

| 度量 | 定义 | 优势 | 适用层 |
|---|---|---|---|
| maxDD（当前） | 历史最大回撤峰值 | 简单，生存防线 | **实时触发器**（四级阈值基于此） |
| CDaR_α=0.05 | 最差 5% 回撤均值 | 考虑整条路径而非单点；tail 平均比单点更稳定；凸可线性规划求解 | **离线度量+优化目标**（非实时触发器） |

> **定位**：CDaR 不替代四级阈值触发器（后者是 fail-closed 生存底线），而是作为**离线组合优化的目标函数**与**回撤健康度仪表盘**。PyPortfolioOpt 已实现 `EfficientCDaR`（α=0.05），个人项目开箱即用。价值：回测时用 CDaR 评估"四级阈值是否设在合理水位"——若 CDaR_0.05 显著高于 Level 1 阈值（8%），说明回撤尾部浓度高，四级阈值可能偏松。
>
> 来源：[metricgate 2026-06](https://metricgate.com/docs/conditional-drawdown-at-risk/) / [stockalpha.ai 2026-02](https://stockalpha.ai/alpha-learning/drawdown-constrained-optimization-cdar-and-path-dependent-risk-limits) / [pfolio.io 2026-03](https://www.pfolio.io/academy/conditional-drawdown-at-risk)

**② EVT（极值理论）——7 黑天鹅模式的数据驱动补充层**

7 黑天鹅模式 BS-001~BS-007 是**人工枚举**（跨市场暴跌/流动性枯竭/政策黑天鹅等），无法捕获未知模式。EVT（极值理论）提供**数据驱动**的尾部建模框架：

| 方法 | 算法 | 优势 | 适用条件 |
|---|---|---|---|
| **POT-GPD**（Peaks Over Threshold + 广义帕累托分布） | 对超阈值残差拟合 GPD，形状参数 ξ 决定尾厚（ξ>0 重尾/Fréchet，ξ=0 指数/Gumbel） | 给出尾部**概率**而非二元标志；数学根基强；可外推到历史未观测的极端分位 | 需足够样本（A 股黑天鹅稀少，需 5+ 年日频数据） |
| **Autoencoder 残差 + POT** | 正常数据训练 autoencoder，黑天鹅事件 reconstruction error 飙升；对残差用 POT-GPD 建模 | 数据驱动捕获**未知**异常模式；比人工枚举更全 | 需训练 autoencoder（中等复杂度） |

> **定位**：EVT 不替代 7 模式枚举（后者是已知的、可解释的、即时响应的），而是作为**补充层**——POT-GPD 给出"当前尾部概率"，autoencoder 残差检测"未知异常"。两者输出作为 [32 FirmRiskAggregator](32_firm_risk_aggregator.md) 的**监控信号**（全 log），不直接触发 Kill Switch（Kill Switch 仍由四级阈值+人工模式驱动）。**实盘 6-12 月后**看哪些黑天鹅模式真正触发过，未触发的降级为监控——与 §2.5.6 过度工程审查裁定一致。
>
> 来源：[BlackSwan-Flag-EVT-residuals (GitHub 2025-10)](https://github.com/utsimul/BlackSwan-Flag-EVT-residuals) / [CSDN EVT 金融风控 2026-07](https://blog.csdn.net/weixin_27298377/article/details/160431033) / [frmquizbank 尾部风险 2026-08](https://frmquizbank.com/blog/tail-risk-black-swan-events)

**③ Kill Switch 行业标准印证**

2026-08 算法审查补充：Kill Switch 是 SEC Rule 15c3-5 / MiFID II **强制要求**（非可选），四级响应阶梯 Throttle → Cancel-all → Block new → Flatten。Knight Capital（2012，45 分钟亏 $4.4 亿）是教科书案例。本项目 Kill Switch + requires_manual_reset 设计与行业标准一致。来源：[hftradingbook 2026-06](https://hftradingbook.com/risk/kill-switches) / [algotradingdesk 2026-03](https://algotradingdesk.com/kill-switch-mechanisms-hft-risk-control/)

## 3. 考虑过的替代方案（拒绝理由）

### 3.1 Model B（因子混合 + 统一 MVO 优化器）—— 拒绝
- **拒绝理由**：统一 MVO 需要协方差矩阵（5000×5000），这是研究课题不是工程任务
- 协方差估计在 A 股情绪周期切换时全错（冰点期相关性飙升到 0.8+）
- 优化器放大输入噪声：小幅协方差扰动 → 权重大幅跳动
- 归因纠缠：亏钱时无法区分"策略 alpha 错"还是"优化器权重错"还是"协方差估错"
- AI 能写对优化器代码，但写不出"准确的协方差矩阵"——那是数据+研究问题

### 3.2 Model D（加权投票选股）—— 拒绝
- **拒绝理由**：A 的自然叠加已等价实现"多策略共识→大仓位"，无需投票
- D 的投票权重是 meta-参数，需要回测/调参/衰减监控，是技术债
- D 的跨策略冲突仲裁是 O(N²) 乃至 O(2^N) 复杂度，A 是 O(N)
- D 的"加权投票"在拥挤交易上反而放大风险（多策略同选的票往往是 alpha 已被套利的拥挤票）

### 3.3 C+D+B+meta 混合 —— 拒绝
- **拒绝理由**：过度设计。D 和 B 在 firm 层无增益（A 的自然叠加替代 D，风险预算聚合替代 B）
- 该方案是"既要又要"的 hedge，不是清晰决策
- 多一层隔离对 AI-builder 更易实现，但 D/B 这两层本身不该建

### 3.4 Model C（策略之策略，纯 meta 分配）—— 部分采纳
- C 的"独立账本+meta 资金分配"思路被采纳为 RegimeMetaAllocator
- 但 C 不单独使用，因为 C 不定义 firm 层风险聚合，需要 A 的 FirmRiskAggregator 补足

## 4. 上限定义（Ceiling）

### 4.1 系统上限
3-5 个独立 StrategyBook + 1 个 FirmRiskAggregator + 1 个可选 RegimeMetaAllocator。

### 4.2 演进路径
- **第一阶段（立即施工）**：纯 A，各策略等额或先验比例资金分配，固定不变。FirmRiskAggregator 只做求和+裁剪。
- **第二阶段（各策略有 3-6 个月实盘 PnL 后）**：上加 RegimeMetaAllocator，按风险调整后收益（IR/Sharpe）动态调资金占比。
  > **前置进展（2026-08-10）**：[11 C1 验证](11_regime_backtest_validation_plan.md) 已通过（commit 852457e9，Shrinkage 节流有效），[34](34_regime_meta_allocator.md) 框架已 active v1.0.0。第二阶段上线门槛仅剩"首批策略 PnL 就绪（PerformanceScore 输入）+ 四档阈值 D1 敏感性校准"。过渡期可用 `Base × Shrinkage`（PerformanceScore=1.0 中性）先跑。
- **远期（可选，非当前 scope）**：Relaxed Risk Parity——从三因子乘法升级到松弛风险预算。
  > **2026 新实证**（出处见 §7.4）：[ericxuzhesheng/Relaxed-Risk-Parity-Research](https://github.com/ericxuzhesheng/Relaxed-Risk-Parity-Research)（2026-08-07 更新，410 commits）——松弛风险预算 + 凸自适应重构 + CVaR 约束 + Turnover penalty。是"三因子乘法（当前）→ MVO（已否决）"的中间态：比三因子乘法精细（考虑策略间协方差结构），比 MVO 稳定（不直接反转协方差矩阵）。
  >
  > **为何远期而非第二阶段**：① 三因子乘法 O(N) 已满足 3-5 策略需求，策略数少时边际收益有限；② 需引入 cvxpy 求解器依赖；③ CVaR 约束需策略 PnL 尾部分布估计（更长 track record）。**重评条件**：策略数 >5 且三因子乘法显示"等权 risk contribution 假设不成立"（如某策略波动率显著高于其他但 PerformanceScore 未充分调整）。
  >
  > **远期演进选项 B：MPC 多期预测（2026-08-10 算法审查补充，出处见 §7.4）**：Nystrup-Boyd-Lindström-Madsen（Annals of OR 282(1):245-271, 2019）MPC + 多变量 HMM 多期预测——**根据已实现回撤动态调整风险厌恶**，控制回撤且几乎不牺牲 mean-variance efficiency。
  >
  > **与 Model A 哲学一致性**：MPC 核心"根据已实现回撤调整风险厌恶"与 §2.5 Drawdown Protocol **同源**（回撤驱动风险节流）；差别在 MPC 用连续优化器（需协方差预测），Model A 用离散硬阈值（O(N) 加法）。MPC 是 Model A"有可靠多期预测"时的连续化演进——与 §2.5.7 CDaR、Relaxed Risk Parity 同属"加法替代优化器的精细化演进谱系"。
  >
  > **为何远期而非第二阶段**：① 需多变量 HMM 多期均值/协方差预测（[10号](10_regime_detector_spec.md) 当前 4 态 HMM 仅做 regime 识别）；② 连续优化器引入协方差估计（§3.1 否决 MVO 的理由），需先验证 HMM 预测稳定性；③ 离散硬阈值 + Shrinkage 已满足当前需求。**重评条件**：[10号] 升级到多期预测 + 首批策略 PnL 验证四级阈值有效性后，评估 MPC 连续化演进。

### 4.3 为何这是上限而非妥协
- Model A **不是** Citadel pod 式，是 **Morwane 式"统一风险框架（firm 求和+裁剪+Kelly）+ 独立 alpha sleeve + regime 风险节流"**（2026-08-10 [20 §1.4/§5 待裁定-2](20_first_batch_strategies.md) 裁定修正误标）。Citadel pod = 几十个互不相关独立 PM + 被动风险聚合 + PM 间不共享不协同；Model A = 统一 firm 层 + 统一 StrategyBook 接口 + 统一信号工厂（G05）+ 少而精（3-5 个）差异化 sleeve——与 charter §3 约束二"统一框架派"一致。
  > **2026 实证支撑**（完整出处见 §7.4）：resonanzcapital 2026-04 区分 systematic multi-strategy（统一风险框架）vs discretionary pod（各自为政），Model A 属前者；Trium Capital 2026-06 区分 pod 平台（风险主导+止损即砍仓）与传统多策略（止损是 review 信号），Model A 属后者谱系；algoalpha 2026-06 个人可借鉴 pod 的**过程**（先定风险再定仓位）非规模；RMATS（arXiv:2605.25311）独立 Risk Agent（CVaR+压力测试+断路器）印证 FirmRiskAggregator"风险从 alpha 解耦为独立层"——MaxDD 9.62% < MVO 15.49%；个人项目不采用多 agent 递归协调（§5 暂缓项），A 模型用更简方式（firm 求和+裁剪+硬阈值）实现同等风险解耦。
- 5 个策略的 MVO 收益 < 5 个策略独立加总收益，因为协方差估计误差 > MVO 理论增益
- 真正的上限 = 在 A 框架内把每个 StrategyBook 做到极致，而不是在 firm 层堆优化器
- 差异化 alpha 在 A 股打板/游资/连板领域深度（BM-SEL-22~25），统一优化器不是护城河

## 5. 待裁定（暂缓）

> 以下项目暂不施工，**非永久禁止**。待项目演进到一定程度，部分项可能自然不再成立，部分项可能重新需要。届时回看本节，重新裁定。每项附"重评条件"——满足时可重新讨论。
>
> **v1.4.0 处置说明**：[20 §5](20_first_batch_strategies.md) 登记的 4 项相关待裁定已处置（详见修订记录 1.4.0：pod 误标 ✅/候选清单同步 ✅/情绪周期边界 ✅/charter 措辞 ⏳ 属 04 域）。下方 6 项为本备忘原生暂缓项，状态未变。

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| firm 层统一 MVO 优化器 | 协方差估计是研究课题；放大噪声；归因纠缠 | 协方差估计方案成熟（如因子模型+shrinkage 验证有效） |
| firm 层跨策略选股投票 | A 的自然叠加已等价实现；O(N²) 冲突是技术债 | 策略数显著增加（>8）且自然叠加不足 |
| 数字孪生 / 世界模型 DreamerV3 / TD-MPC2 —— **已裁定裁剪（#ARCH-OE-010，decided 2026-08-11 用户确认）** | 裁定：BM-SIM-05 降级为"依赖图快照"（保留拓扑可视化去推演）；世界模型推演裁剪（**远期不采纳**，solo 硬件 GPU 24GB 不满足 ≥48GB 门槛） | 不重评（远期不采纳已定性） |
| LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索 | 研究议题，作战地图之外；AI 写 AI 的失控风险高 | 可控性方案（沙箱+审批+回滚）验证可靠。**关联裁定**：CC-14 投票优先多 Agent 协作已 decided 降级为可选模式（#ARCH-OE-011，2026-08-11）——solo 单 session 主导用单 Agent 决策+red_blue_validator 承接 |
| 60 个活跃因子 / 150 设计容量 | 个人系统 8-15 个因子足够；多了是过拟合温床 | AUM 增长到需要更多因子分散 |
| 56 条硬边界一视同仁 | 砍到 10 条真红线（Fail-Closed）+ 其余降为指导原则 | 团队扩大或合规要求升级 |

## 6. 待定问题

### 6.1 首批上线的 3 个策略（需人决策）
5 个候选策略不可能齐平，弱策略拖累归因清晰度。建议首批上 3 个最自信的，跑 3 个月有 track record 后再加第 4、5 个。

候选组合（待确认）：打板 + 多因子 + 事件驱动

### 6.2 策略间相关性验证（施工前必做）
用历史数据算 5 个策略两两相关矩阵，按情绪周期分层看。若各阶段相关性都 >0.6，"多策略"实为"情绪 beta 穿多件衣服"，需重新审视策略组合。

> **施工算法补充（2026-08-10 五次算法审查）**：[youcanbuildthings 2026-05](https://youcanbuildthings.com/articles/multi-strategy-trading-bot-python)给出具体的 correlation drop rule——90 天滚动相关性 >0.70 持续 30 天 → drop 低 Sharpe 策略。算法：
>
> ```python
> def correlation_drop(returns_df, threshold=0.70, persistence_days=30):
>     """90天滚动相关性>threshold持续persistence_days→drop低Sharpe策略"""
>     rolling_corr = returns_df.rolling(90).corr()
>     # 检测每对策略相关性>threshold持续persistence_days
>     # 持续超限→保留高Sharpe，drop低Sharpe
> ```
>
> **A 股适配**：① 阈值 0.70→0.60（A 股情绪退潮期相关性飙升，[28 §3.5](28_sentiment_cycle_trading.md) bayes-group March Shock 尾部相关性案例，0.70 太松）；② 按情绪周期分层看（冰点/退潮期相关性天然高，不触发 drop，而是触发"退潮期空仓"纪律）；③ drop 不是永久退役，而是"暂停部署+归因复查"（相关性回落 <0.5 后可恢复）。**与上文">0.6 需重新审视"的关系**：0.6 是"审视"阈值（施工前必做验证），0.6-0.7 是"监控+归因"区间，>0.7 持续 30 天是"暂停部署"阈值——形成三级响应。详见 [23 策略相关性验证](23_strategy_correlation_validation.md)。

### 6.3 情绪周期定位器准确率（施工前必做）
BM-SEL-23-B 情绪周期 4+1 阶段定位器的历史准确率需评估。错判代价大（主升判成冰点→该进攻时防守），且 RegimeMetaAllocator 依赖此信号。需有"置信度<60%→默认保守"的兜底。

### 6.4 convergence_window 按策略换手率怎么定（需人决策）
Tier 2 的 rebalance 窗口需按策略换手率差异化设置。初拟：打板 1-2 天，多因子 3-5 天，事件驱动 2-3 天。需首批策略确定后校准。

### 6.5 ~~12 态×N 策略的样本量问题~~ → 已决策（2026-08-05）
**决策：不合并 12 态，用灰度概率分布 + 软分配 + 按频率差异化收缩。**
- 灰度天然解决过渡平滑（替代了合并的过渡功能）
- 软分配让每个态获得更多有效样本（过渡期天按 P 比例贡献给多个态）
- 按态频率差异化收缩处理稀有态（常见态用自身估计，稀有态收缩向均值）
- 比一刀切合并更优雅：保留 12 态精细度，数据不足处自动降级

### 6.6 regime 检测器业务规则 spec（需人定义，讨论中）
regime 检测器须输出 12 维灰度概率分布（非硬标签）。业务规则（各态转换路径、触发/确认信号、置信度更新规则、主线识别）需人定义——这是主观交易经验的系统化编码。
讨论文档：[10_regime_detector_spec.md](10_regime_detector_spec.md)

### 6.7 策略级冷启动执行比例（MVP 基线已定，待 C1 实盘校准）

新 StrategyBook 上线初始执行比例（§2.2 仅提"冷启动只用 Base_i"，未定义执行比例）——v2.1.0 裁定定型。**行业标准**（[quanthedgeai 2026-07](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)）：research candidate → paper portfolio（6 月，PnL 偏离回测预期 >30% 则调查）→ half-sized live（6 月，rolling DSR 确认）→ full size，即"先纸面、再半仓、后满仓"三段式。

**MVP 基线（v2.1.0 裁定采纳）**：
| 阶段 | 执行比例 | 持续时间 | 晋升条件 |
|---|---|---|---|
| 冷启动 | ×30% | 1 个月 | 无 firm 风险违例 + PnL 不偏离回测预期 >30% |
| 半仓 | ×60% | 1 个月 | PerformanceScore 初步稳定 + rolling Sortino > 0 |
| 满仓 | ×100% | — | PerformanceScore 稳定（60 日窗口有效观测≥40） |

**裁定要点**：
1. **与 53 号模拟实盘迁移路径 PARALLEL→SHADOW→GRAY_RAMP 同构**——冷启动是策略级灰度迁移，53 号是系统级灰度迁移，共用"渐进放大"哲学。×30% 起步是"单策略故障不致命 + PnL 信号可观测"的平衡点（冷启动期无 track record、PerformanceScore 无效，是新策略最脆弱阶段）
2. **参数待 C1 校准**：×30%/×60%/×100% 为基线，按实盘 PnL 校准（Sharpe >1.5 且 MaxDD <5% 可加速 ×50%→×100% 两段式；Sharpe <0.8 延长冷启动至 2 月）
3. **与 §2.4 BudgetChangeHandler 联动**：冷启动期 budget 上调用 Tier 1+2（自平衡），不触发 Tier 3 强裁——budget 预算本身已按 ×30%/×60% 缩放，Tier 3 门槛相应缩放
4. **与 25 号因子治理灰度正交**：因子级灰度（10%→30%→100%）是单因子权重渐进暴露（周期短，IC 稳定快）；策略级冷启动是整个 StrategyBook 资金预算渐进放大（周期长，策略 PnL 波动远大于因子 IC）——不冲突
5. **风险红线**：冷启动期 Kill Switch 仍全效（系统级非策略级，不受缩放影响），新策略故障在 30% 暴露度下即可被截断

> **施工指导**：RegimeMetaAllocator.allocate() 须增加 `cold_start_ratio` 参数（默认 1.0=满仓，冷启动期设 0.3/0.6），在 allocate 伪代码的"effective_budget 缩放"步骤后乘以 cold_start_ratio。cold_start_ratio 由 StrategyBook 维护，按上线天数自动晋升（1 月→0.3→0.6，2 月→1.0），PerformanceScore 稳定后锁定 1.0。

### 6.8 灾后重建事项（2026-08-11 git clean 灾难，#ARCH-GIT-CLEAN-GUARD-FIX）

> 以下 4 项均为 2026-08-11 git 灾难（`git clean -fd` 等内置命令绕过 git_guard.py alias 拦截）造成的资产丢失/治理缺口，**属"需重建/补登记"事实记录，非架构决策**。重建施工不属于本备忘范围，登记于此供治理调度。

| 事项 | 现状 | 丢失/缺口内容 | 重建建议 |
|---|---|---|---|
| **4 个测试文件丢失** | `tests/position/test_strategy_book.py`（70 测试）/ `test_firm_risk_aggregator.py`（54）/ `test_budget_change_handler.py`（47）/ `tests/pf_alloc/test_regime_meta_allocator.py`（55）于 2026-08-10 创建未 `git add`，2026-08-11 被 `git clean -fd` 删除，git 历史无记录 | 226 个测试用例（4 模块代码均 production 在位，仅测试丢失） | 按各模块 blueprint + 代码头部 [TESTS] 声明重建；重建后立即 `git add`（防护规则①） |
| **33 号 BudgetChangeHandler 设计文档骨架化** | 当前工作区 33 号=骨架 v0.1.0（draft，2026-08-09）；2026-08-10 全天升级的 v2.10.0 定稿内容在 git 历史中无记录，彻底丢失 | G14 三级升级设计真源（§3.4 handle_budget_change 伪代码 / §3.2.6 TierState / 防抖 5 规则等） | 以 `budget_change_handler.py`（production，572 行）头部 docstring + 本备忘 §2.4 + 32 号 §2.1 degraded 契约为临时真源重建 33 号；重建后 30/32 号交叉引用版本号需回填 |
| **capability_canonical_file_registry 未登记** | MOD-POS-020/021/022 + MOD-PA-007 均未在 `capability_canonical_file_registry.yaml` 登记（该 registry 仅有 MOD-POS-009 一条 D_POSITION 记录） | 硬约束"模块创建必须生成 creation_token 并登记"违例 | 补 4 条登记（creation_token 追溯生成或按补救流程登记） |
| **depgraph maturity 滞后** | depgraph（PostgreSQL）中 4 模块仍 design——[64_d_position.md](../../02_domain_architecture_docs/64_d_position.md)（自动生成）将 MOD-POS-020/021/022 标"设计态" | 自动生成文档与代码状态脱节 | depgraph DB 更新 maturity=production 后重新生成 64 号文档；battle_map_08 锚点状态联动核对 |

### 6.9 并存旧体系与 Model A 的关系裁定（需人决策）

> 全量设施盘点（§7.5）发现 pf_alloc / pf_core 存在与 Model A 功能重叠的已施工旧体系模块，**谁是真源、是否退役需人裁定**，本备忘不擅自定。

| 旧体系模块 | 状态 | 与 Model A 的重叠点 | 待裁定 |
|---|---|---|---|
| MOD-PA-003 multi_strategy_capital_allocator（`pf_alloc/core/`，production v0.1.0） | 已施工 | 容量截断 + MaxDD>15% 全线减仓 50% + 冷启动 ×30% + 再平衡 ≤1 次/日——与 RegimeMetaAllocator（MOD-PA-007）的"Base×PerformanceScore×Shrinkage + floor/cap"功能部分重叠（都是策略级资金分配+缩放）；冷启动 ×30% 与 §6.7 策略级冷启动三段式（×30%→×60%→×100%）重叠 | PA-003 是否降级为 MOD-PA-007 的内部组件，或标记 deprecated |
| MOD-PA-002 signal_synthesis_combiner / MOD-PA-004 strategy_correlation_gate（`pf_alloc/core/`，均 production） | 已施工 | BM-SEL-20-A（信号合成）/ BM-SEL-20-C（相关性门禁）旧投票体系残留——Model A §3.2 已否决跨策略投票，§7.3 已将 BM-SEL-20 标记 rejected | 两模块是否随 BM-SEL-20 rejected 同步退役，或保留为策略内部机制（§7.3 对 BM-SEL-02-K 的降级先例） |
| pf_core 旧体系 5 示例策略 + portfolio_optimizer / constraint_solver / rebalance_scheduler / performance_attribution_engine / strategy_engine | 均 production | §7.3 已记录 MOD-PF-002 暂缓弃用（rebalance_scheduler 有活跃依赖）；5 示例策略（default_equity / topn_momentum / vwap_reversion / intraday_surge_fall / orderbook_imbalance）与 StrategyBook 体系的关系未定义 | 首批 3 策略（20 号）上线时，示例策略是迁入 StrategyBook 还是退役 |

## 7. 引用

### 7.1 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)（选股阶段，双引擎融合等机制在此阶段内部保留）
- [battle_map_12_cross_cutting.md](../battle_map/battle_map_12_cross_cutting.md)（§16 冲突矩阵大部分将因 A 架构而消失）
- [battle_map_10_execution.md](../battle_map/battle_map_10_execution.md)（执行阶段，FirmRiskAggregator 输出在此下单）

### 7.2 depgraph 模块（已登记 2026-08-05，2026-08-12 状态更新）
**四模块全部已施工 `MATURITY=production`**（2026-08-12 核对源码）；⚠️ 4 个测试文件在 2026-08-11 git clean 灾难中丢失（§2.2 ⚠️ + §6.8），depgraph（PostgreSQL）中 4 模块 maturity 仍 design（64_d_position.md 自动生成滞后），治理缺口登记 §6.8：

| 模块 | blueprint_id | path | domain_id | 说明 | 当前状态（2026-08-12 核对源码） |
|---|---|---|---|---|---|
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | D_POSITION | 独立策略账本，自带选股+仓位+风控 | ✅ production（v1.0.0，680 行）⚠️ 测试丢失（70） |
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | D_POSITION | firm 层求和+硬上限裁剪，不做 MVO | ✅ production（v1.0.0，651 行）⚠️ 测试丢失（54） |
| RegimeMetaAllocator | MOD-PA-007 | `src/zephyr/pf_alloc/core/regime_meta_allocator.py` | D_PF_ALLOC | regime 灰度概率→Shrinkage 风险节流，第二阶段上 | ✅ production（v1.0.0，594 行）⚠️ 测试丢失（55）；参数待 PnL 校准，上线仍 P3 |
| BudgetChangeHandler | MOD-POS-022 | `src/zephyr/position/core/budget_change_handler.py` | D_POSITION | 三级升级（封锁→自平衡→强裁），执行 budget 变动 | ✅ production（v1.0.0，572 行）⚠️ 测试丢失（47）+ 33 号文档骨架化 |

> Soft-Assignment Performance Tracker：RegimeScore 移除后降级为归因可选工具（非分配器依赖），暂缓登记。

### 7.3 需降级/重构的现有设计
- BM-SEL-20 多策略投票（CAND-HARVEST-3225）→ 候选已标记 **rejected**（2026-08-05），A 的自然叠加替代
- BM-SEL-02-K 多策略投票加权 → 降级为策略内部机制（非跨策略层）
- §16 的 31 条跨策略冲突仲裁 → 大部分消失（A 无跨策略冲突），仅留 firm-level 硬上限
- BM-SEL-25 双引擎融合 → 保留，定位为"打板策略内部"融合，非跨策略层
- MOD-PF-002 portfolio_optimizer.py → MVO 方式被 A 模型否决（§3.1），但当前有活跃生产依赖（rebalance_scheduler.py），**暂缓弃用**；待 StrategyBook 施工后评估重构/移除

### 7.4 开源实证参考

> 以下开源项目为本备忘录的架构选型和 §1.2.0 RegimeScore 裁定提供实证支撑。

#### [Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book) — 核心实证

**直接验证了"regime 做风险节流 vs regime 做 alpha 择时"的对比**。两个弱相关 alpha sleeve（ρ=+0.03）经 inverse-vol risk parity 组合，上叠 3 态 Gaussian HMM（calm/normal/stress），walk-forward 季度重拟合，因果 Viterbi 解码。

OOS 2013-2026（扣除 2bps/turnover）：

| 策略 | Sharpe | Max DD | Calmar | Turnover/yr |
|---|---|---|---|---|
| Risk-parity（基准） | +1.43 | −14.2% | +1.04 | — |
| Regime 做 alpha 择时（naive） | +1.04 | −16.6% | +0.63 | 40.4 |
| Regime 做 alpha 择时（disciplined） | +0.87 | −15.2% | +0.56 | 4.3 |
| **Regime 做风险节流** | **+1.43** | **−10.3%** | **+1.43** | 1.7 |

**两条发现，一个教训**：
1. Regime 做收益择时信号**摧毁价值**——naive 和 disciplined（置信度门控+迟滞+定期再平衡）均跑输静态 risk parity。切换滞后（persistence trap）+ 破坏分散化组合的代价 > 择时收益。
2. Regime 做风险节流**增加价值**——保持已验证的 risk-parity 组合始终运行，仅用 regime 在确认 stress 时削减总暴露。Sharpe 不变（1.43），Max DD 从 −14.2% 缩至 −10.3%，Calmar +38%，turnover 仅 1.7×/yr。

**教训**："HMM regime detection is a risk-management tool, not a return-timing signal — exactly what a desk would conclude."

**鲁棒性**：block-bootstrap 2000×（21-day blocks），risk-throttle Sharpe 90% CI [+1.01, +1.87]，P(Sharpe > 0) = 100%。交易成本不敏感（0-50bps Sharpe 不变，因 turnover 极低）。

> **与本备忘录的关系**：此项目是 §1.2.0 移除 RegimeScore 裁定的**直接实证依据**。其"risk-throttle"模式 = 本备忘录的 Shrinkage 因子；其"alpha-timing"模式 = 被移除的 RegimeScore 因子。数据完美印证：同一个 regime 信号，用于进攻（择时）有害，用于防守（节流）有益。

#### [shprite21/Regime-Aware-Systematic-Equities-Trading-Platform](https://github.com/shprite21/Regime-Aware-Systematic-Equities-Trading-Platform)

机构级 regime-aware 系统股权交易平台，将 regime detection + alpha generation + portfolio optimization + risk management + 回测 + 分析整合为统一 research-to-execution pipeline。设计目标对标机构系统股权研究基础设施。与本备忘录的参考价值：验证 regime detection → alpha → portfolio → risk 的分层架构是行业主流范式。

#### [ItsSawhill/market-regime-detection](https://github.com/ItsSawhill/market-regime-detection)

多资产市场 regime 检测框架，同时使用 KMeans（静态聚类）和 HMM（时序依赖），walk-forward 滚动重训练。特征工程覆盖 price/volatility/momentum/volume/macro signals，使用 VIX/Treasury yields/USD index 作为宏观代理。多策略基准对比（regime-based vs momentum vs trend-following vs buy-and-hold）。与本备忘录的参考价值：HMM + walk-forward 是 regime 检测的工程标准做法。

#### [ridash2005/Multi-Regime-Algorithmic-Trading-System](https://github.com/ridash2005/Multi-Regime-Algorithmic-Trading-System)

3-regime 波动率分类系统（low σ<15% → mean reversion / medium 15-30% → hybrid / high >30% → breakout）。Quant Games 2026 提交，Portfolio Sharpe 2.276。与本备忘录的参考价值：验证波动率分层是 regime 分类的实用维度（与本项目 12 态中趋势×波动率 3×3 网格一致）。

#### 2026 多策略架构实证补充（v1.4.0 新增）

> 以下 2026 实证为 §4.3 pod 误标修正与 §1.3 情绪周期隐形驱动提供支撑。

- [resonanzcapital — Systematic Multi-Strategy vs Discretionary Pod Platforms (2026-04)](https://resonanzcapital.com/insights/systematic-multi-strategy-vs.-discretionary-pod-platforms-different-engines-different-risk)：明确区分两类架构——systematic multi-strategy（中央设计信号库+统一风险框架，判断内嵌系统，仓位与回撤控制连续内嵌执行逻辑）vs discretionary pod（独立 PM 各自为政，风险聚合反应式：突破→检测→行动）。March 2026 伊朗事件中 systematic 持稳、pod 集体回撤。**Model A 属 systematic 谱系**，直接支撑 §4.3 修正。
- [bayes-group — After the March Shock (2026-03)](https://www.bayes-group.com/insights/march-shock-multistrat-resilience)：March 2026 事件 Millennium/Citadel/Point72/Balyasny 各亏 $1-1.5B，暴露"分散化幻觉"——尾部相关性在宏观冲击下飙升，看似独立的 pod 同时同向亏损。**支撑 §1.3 情绪周期作为 A 股版尾部相关性飙升事件**，与 [28 §3.5](28_sentiment_cycle_trading.md) 呼应。
- [Trium Capital / WealthDFM — Not all multi-strategy funds are built the same (2026-06)](https://wealthdfm.com/viewpoint-not-all-multi-strategy-funds-are-built-the-same/)：pod 平台=风险主导+止损即自动砍仓+回撤中砍仓；传统多策略=收益主导+止损是 review 信号+回撤中可加仓。**Model A 的"统一框架+少而精+硬阈值回撤节流"** 取 pod 的风险纪律（硬阈值）但弃 pod 的组织复杂度，是两谱系的工程折中。
- [algoalpha — Multi-Strategy Hedge Funds and the Pod Model, Explained (2026-06)](https://www.algoalpha.co/join/blog/multi-strategy-pod-shops-explained)：个人投资者可借鉴 pod 模型的**过程**（分散下注、先定风险再定仓位、保持系统化），**非规模**。**支撑 Model A 在个人系统上的合理性**——借 pod 风险纪律，不上 pod 组织复杂度。

#### 2026 仓位/风控算法实证补充（v1.5.0 新增）

> 以下 2026 实证为 §2.1 Fractional Kelly、§2.3 叠加裁剪、§2.5.1 回撤恢复数学、§4.2 Relaxed Risk Parity 提供支撑。

- [tradingengineeringlab — Risk Management: The Math of Survival (2026-06)](https://www.tradingengineeringlab.com/es/risk-management-trading-math-of-survival/)：连败概率精确 Markov 链计算（常见近似公式误差 2×）；回撤恢复不对称 `Recovery = D/(1-D)`（30% 回撤需 +43%）；Full Kelly 容忍 50%+ 回撤。**支撑 §2.1 Fractional Kelly + §2.5.1 回撤恢复数学**
- [metatronics — Position Sizing: The One Number (2026-03)](https://metatronics.com/position-sizing-math)：2% 单笔风险规则 ≈ Fractional Kelly；10 连败@2%=18.3% 回撤（可恢复），@10%=65.1%（毁灭）。**支撑 §2.5.1 四级阈值的回撤容差设计**
- [astuteinvestorscalculus — Managing Drawdowns (2026-06)](https://astuteinvestorscalculus.com/portfolio-drawdown-management/)：Fractional Kelly 25-50%；最大仓位 12-15%、多数 5-8%；预定义规则（drawdown 前制定，非 drawdown 中制定）。**支撑 §2.1 Fractional Kelly 比例 + §2.5 回撤 Protocol "触发即执行"原则**
- [ericxuzhesheng/Relaxed-Risk-Parity-Research (2026-08-07)](https://github.com/ericxuzhesheng/Relaxed-Risk-Parity-Research)：松弛风险预算 + 凸自适应重构 + CVaR 约束 + Turnover penalty。410 commits，持续维护。**支撑 §4.2 远期演进路径**——三因子乘法→MVO 之间的中间态
- [marketmaker.cc — 12 Portfolio Optimization Algorithms Compared (2026-05)](https://marketmaker.cc/en/blog/post/portfolio-optimization-algorithms-compared)：对比 HRP/HERC/GHRP/MHRP/Black-Litterman/NCO 等 12 种优化算法。HRP（López de Prado 2016）不反转协方差矩阵，比 MVO 更稳定 OOS。**支撑 §3.1 否决 MVO 的合理性**——即便用 HRP 替代 MVO，仍引入优化器复杂度，A 模型加法更简
- [proinvesting — Detect Market Regime Shifts Before Price Moves (2026-04)](https://proinvesting.co/es/how-to-detect-market-regime-shifts-before-price-moves/)：Bayesian uncertainty regime detection——模型不确定性 `Σ*(t) = rolling_std(|P(t) - smoothed_P(t)|) + α·vol(t)` 本身就是信号（"当模型不知道时，那就是信号"）。**支撑 [10号](10_regime_detector_spec.md) `max(P)<60% 强收缩`机制**——不仅看 max(P)，模型不确定性也是风险信号。属 10 号 regime 检测器范围，本备忘交叉引用

#### 2026 年 8 月算法审查实证补充（v1.6.0 新增）

> 以下 2026 实证为 §2.1 Bayesian Kelly、§2.3 Water-Filling、§2.4 no-trade 带宽、§2.5.7 CDaR/EVT 提供算法支撑。

- [Sukhov — Bayesian Kelly Criterion with Parameter Uncertainty (2026-06)](https://github.com/sergeisukhovmkt/Bayesian-Kelly-Criterion-with-Parameter-Uncertainty)：后验加权 Kelly `f* = (p̄ − (1−p̄)/b) · n_eff/(n_eff + κ)`，收缩系数随有效样本量自适应。**支撑 §2.1 Bayesian Kelly 为固定 Fractional Kelly 的自适应演进**
- [Water-Filling is Universally Minimax Optimal (arXiv:2603.26893, 2026-03)](https://arxiv.org/html/2603.26893v1)：注水算法在在线可分资源分配中普遍 minimax 最优（对任何 Schur-单调目标函数）。[Risk-Based Auto-Deleveraging Clipped Water-Filling (arXiv:2603.15963, 2026-03)](https://arxiv.org/html/2603.15963v1)：多资产交叉保证金场景实证优于 pro-rata。**支撑 §2.3 Water-Filling 为 pro-rata 的 Phase 2 候选**
- [stockalpha.ai — Optimal Rebalancing Bands Under Transaction Costs (2026-02)](https://stockalpha.ai/alpha-learning/no-trade-regions-optimal-rebalancing-bands-under-transaction-costs)：最优 no-trade 半带 `b* = [3·c·σ²/(2·λ)]^(1/3)`，基于布朗运动首达时间闭式解；可从 TE 反推 `b = TE_target·√3`。**支撑 §2.4 no-trade 带宽公式为固定 ε_pos 的理论增强**
- [metricgate — Conditional Drawdown-at-Risk (2026-06)](https://metricgate.com/docs/conditional-drawdown-at-risk/) / [stockalpha.ai — Drawdown Constrained Optimization (2026-02)](https://stockalpha.ai/alpha-learning/drawdown-constrained-optimization-cdar-and-path-dependent-risk-limits)：CDaR 是相干回撤风险测度，凸可线性规划求解，PyPortfolioOpt 已实现 `EfficientCDaR`。**支撑 §2.5.7 CDaR 作为离线度量补充**
- [BlackSwan-Flag-EVT-residuals (GitHub 2025-10)](https://github.com/utsimul/BlackSwan-Flag-EVT-residuals) / [CSDN EVT 金融风控 (2026-07)](https://blog.csdn.net/weixin_27298377/article/details/160431033)：POT-GPD 极值理论 + autoencoder 残差检测，数据驱动尾部建模。**支撑 §2.5.7 EVT 作为 7 黑天鹅模式的数据驱动补充层**
- [hftradingbook — Kill Switches (2026-06)](https://hftradingbook.com/risk/kill-switches) / [algotradingdesk — Kill Switch Mechanisms (2026-03)](https://algotradingdesk.com/kill-switch-mechanisms-hft-risk-control/)：Kill Switch 是 SEC Rule 15c3-5 / MiFID II 强制要求，四级响应阶梯 Throttle→Cancel-all→Block new→Flatten；Knight Capital 教科书案例。**印证 §2.5.5 Kill Switch 设计与行业标准一致**
- [firestrand — marketregimeml 模型对比 (2026)](https://github.com/firestrand/marketregimeml)：真实数据 RQI 基准——HMM 67.8-76.6（可解释性高），LSTM 49-64（不推荐）；**n_regimes>3 过拟合，10 个优化特征胜过 35+**。**印证本项目 C1 实跑 4 态 HMM 合理性**；交叉引用 [10号](10_regime_detector_spec.md) 12 态设计需审视合并

#### 2026 年 8 月最新研究整合（v1.7.0 新增）

> 以下 2026 实证为 §2.3 多策略 Sharpe 基准、§4.2 MPC 远期演进、§4.3 RMATS 独立 Risk Agent 印证、§6.7 冷启动执行比例行业标准提供支撑。

- [vzeman/trading-autoresearch — Systematic Equity Trading: What Works in 2026 (2026-05)](https://github.com/vzeman/trading-autoresearch/blob/main/systematic_equity_trading_research.md)：综合 ~40 篇一手来源（Jegadeesh & Titman / Hou-Xue-Zhang / Frazzini-Israel-Moskowitz / AQR / Two Sigma / Man AHL / Carver / López de Prado 等）的 2026 equity systematic trading 全景。cross-sectional momentum (12-1) gross Sharpe ~0.85 / net ~0.65（月度换手 ~140%/yr），volatility-scaled 风险调整收益翻倍；time-series/dual momentum net Sharpe 0.6-0.8；学术回测 headline 实盘打 20-50% 折扣。**支撑 §2.3 多策略组合预期 Sharpe 基准 0.6-0.85**
- [Nystrup-Boyd-Lindström-Madsen — Multi-Period Portfolio Selection with Drawdown Control (Annals of Operations Research 282(1):245-271, 2019; [Stanford Boyd page 2026-06 维护](https://stanford.edu/~boyd/papers/multiperiod_portfolio_drawdown.html))]：MPC + 多变量 HMM 多期预测，根据已实现回撤动态调整风险厌恶，控制回撤且几乎不牺牲 mean-variance efficiency。**支撑 §4.2 MPC 远期演进——与 Model A 回撤驱动风险节流（§2.5）同源**
- [Yang et al. — RMATS: Recursive Multi-Agent Trading System (arXiv:2605.25311, 2026-05, APAM 2026)](https://arxiv.org/pdf/2605.25311)：4 agent（Sentiment/Report/Analysis/Risk）+ 递归 Manager，Risk Agent 用 CVaR + 地缘压力测试 + 自适应断路器。561 交易日/24 资产实证 MaxDD 9.62% < MVO 15.49% < FinBERT 15.28%，消融实验确认各组件贡献。**支撑 §4.3 FirmRiskAggregator 独立分层设计正确性（独立 Risk Agent 印证）**
- [quanthedgeai — Implementing a Multi-Strategy Portfolio End-to-End (2026-07)](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)：多策略组合端到端实施框架——strategy intake 四阶段（research candidate → paper portfolio 6 月 → half-sized live 6 月 → full size），risk parity allocation，max risk contribution per strategy 25-30% / per risk-driver cluster 40-50%，vol target 10-15% annualized。**支撑 §6.7 策略级冷启动执行比例行业标准（先纸面→半仓→满仓三段式渐进上线）**

#### 2026 年 8 月四次算法审查实证补充（v1.8.0 新增）

> 以下 2026 实证为 §2.1 Conformal Kelly 选项外更优算法、§2.5.1 五级 drawdown sizing 行业对照提供支撑。

- [Conformal Kelly: Conformal Prediction Intervals as the Scale in Fractional Kelly Position Sizing (arXiv:2608.01494v1, 2026-08-02)](https://arxiv.org/html/2608.01494v1)：conformal 75% 区间宽度作 Fractional Kelly 缩放因子。完整实证数据（Sharpe 1.34/MaxDD 27.7%→20.3% drawdown dial/Lockbox 披露）见 §2.1。**支撑 §2.1 Conformal Kelly 为 Phase 3 远期候选**
- [vzeman/trading-autoresearch — Drawdown-Based Dynamic Sizing (2026-05)](https://github.com/vzeman/trading-autoresearch/blob/main/systematic_equity_trading_research.md)：5 级 drawdown sizing（0-5% Full / 5-10% 75% / 10-15% 50% / 15-20% 25% / >20% Halt），比本项目四级（8/15/20/25%）更激进（5% 即开始减仓）。**对照意义**：本项目四级阈值 8% 起步更保守（给 A 股 T+1+涨跌停更多容错），vzeman 5 级更细但 5% 起步适合可日内调仓的美股。印证 §2.5.1 四级阈值行业基准合理性，同时提供"5 级 vs 4 级"对照——本项目 4 级是"足够粗让 T+1 不误触、足够细让风控有效"的平衡
- [Morwane/multi-strategy-alpha-book — Sleeve-Addition Study + Robustness Suite (2026-06-10)](https://github.com/Morwane/multi-strategy-alpha-book)：新增 13 市场跨资产趋势 sleeve 测试 + 成本敏感性/bootstrap CI/相关性压力测试 robustness suite。HMM regime overlay 作风险管理工具（非择时信号）Sharpe 1.43 保持、MaxDD -14.2%→-10.3%、Calmar +38%、换手 1.7×/yr。**印证 §2.2 regime→Shrinkage 风险节流哲学 + §7.4 sleeve-addition 可扩展性**

#### 2026 年 8 月五次算法审查实证补充（v1.9.0 新增）

> 以下 2026 实证为 §6.2 G07 相关性验证施工算法、§4.2 演进路径"何时升级"评估框架提供支撑。

- [youcanbuildthings — Multi Strategy Trading Bot Python: Risk Parity Allocator (2026-05)](https://youcanbuildthings.com/articles/multi-strategy-trading-bot-python)：多策略 bot 4 大机制——risk-parity capital sizing（60 日 inverse-vol）+ 90 天滚动相关性 drop rule（>0.70 持续 30 天→drop 低 Sharpe）+ per-strategy drawdown circuit breaker（15% half / 25% zero）+ intent netting before broker。$98K 总资金 6 策略分配示例。**支撑 §6.2 G07 相关性验证施工算法**（correlation drop rule 具体 Python 实现 + 三级响应阈值 0.6 审视/0.6-0.7 监控/>0.7 暂停部署）+ **印证 §2.5 四级回撤 Protocol**（15% half / 25% zero 与本项目 15% 减仓 / 25% 清仓一致）
- [Regime-Adaptive Meta-Policies for Hierarchical Portfolio Agents (Kou et al. 2026-05, preprints 202605.0517)](https://www.preprints.org/manuscript/202605.0517)：三操作点架构（direct optimizer / routed consensus / alpha-augmented optimizer），rolling adaptive meta-policy 按近期表现选模式。**关键发现**："routing helps when dispersion/decorrelation is high；direct optimization is safer in low-signal settings"——**印证 Model A 在 A 股低信号环境的适用性**，并为 §4.2 演进路径提供"何时升级"评估框架（策略数 >8 且分散度高时重新评估 routing）。**不采纳为当前方案**（§3.2 已拒绝 Model D 投票/consensus）

#### 2026 年 8 月六次审查实证补充（v2.6.0 新增）

> 以下 2026-08-12 全网搜索新获 2 条机构实证，为 §1.1"3-5 策略少而精"与 §4.3"Model A=统一风险框架+独立 sleeve"提供支撑。

- [Paloma Partners 重组（Bloomberg via Hedgeweek 2026-07-17）](https://www.hedgeweek.com/paloma-overhauls-multi-strategy-platform-with-fewer-teams-and-renewed-focus-on-arbitrage/)：Paloma（1981 年创立）砍 PM 团队**一半至 ~10 个**，聚焦固收套利+系统化策略——"underperforming teams offset gains"+量化策略拥挤市场超额存疑（AUM $4B→$1.1B）。**印证 §1.1"少而精 3-5 策略"与 charter §3 约束五**：多策略鼻祖级平台也在 2026 拥挤化环境收敛到高确信少数策略；§2.3 超额衰减是全球性现象。
- [Candriam L Alternative Multi-Strategies（CAMS，The Hedge Fund Journal Issue 178，2026-06-25）](https://thehedgefundjournal.com/candriam-l-alternative-multi-strategies-cams/)：欧洲 UCITS 版内部多策略（4 主观+4 量化），**"all strategies are aggregated into a single trading book"**，成本集中管理，按 risk-on/transitory/risk-off 三态 regime 动态再配置。**印证 §4.3 Model A 定位**（统一风险框架+单一账本聚合+非 pod 组织，与 Morwane/resonanzcapital 同谱系）；三态 regime 比 12 态简洁——间接支持 [10号](10_regime_detector_spec.md)"状态数宜少"方向（与 §7.4 firestrand "n_regimes>3 过拟合"呼应）。

### 7.5 已施工设施盘点（2026-08-12 全量核对，通用规则 #11）

> 盘点范围：position / pf_alloc / pf_core / risk 四域中与本备忘主题（多策略并发 + firm 风险聚合 + 回撤 Protocol）相关的全部已施工设施。**先清楚有什么 → 才知道怎么改 → 才知道该删除/退役什么**。发现的重叠/缺口已分别登记 §6.8（灾后重建）与 §6.9（旧体系裁定）。

#### A. Model A 核心链（§2.2 三模块 + meta 层，均 production）

| 模块 | path | 行数 | 测试 | 备注 |
|---|---|---|---|---|
| MOD-POS-020 StrategyBook | `src/zephyr/position/core/strategy_book.py` | 680 | ⚠️ 丢失（70） | `select_stocks` 为子类抽象接口（2 处 NotImplementedError 属模板方法正常设计，非骨架） |
| MOD-POS-021 FirmRiskAggregator | `src/zephyr/position/core/firm_risk_aggregator.py` | 651 | ⚠️ 丢失（54） | 两段拆分 pre_kelly_aggregate/post_kelly_clip 已实现，0 处 NotImplementedError |
| MOD-POS-022 BudgetChangeHandler | `src/zephyr/position/core/budget_change_handler.py` | 572 | ⚠️ 丢失（47） | 0 处 NotImplementedError；33 号设计文档骨架化（§6.8） |
| MOD-PA-007 RegimeMetaAllocator | `src/zephyr/pf_alloc/core/regime_meta_allocator.py` | 594 | ⚠️ 丢失（55） | 0 处 NotImplementedError；参数待 PnL 校准，上线仍第二阶段 |

#### B. 回撤 Protocol 链（§2.5，均 production 且测试在位）

| 模块 | path | 行数 | 测试 |
|---|---|---|---|
| MOD-POS-008 drawdown_controller（5 级 VaR 风险 + Soft/Hard 策略止损 + 7 黑天鹅 BS-001~007） | `src/zephyr/position/core/drawdown_controller.py` | 603 | ✅ `tests/position/test_drawdown_controller.py` |
| drawdown_tracker | `src/zephyr/risk/core/drawdown_tracker.py` | 332 | ✅ `tests/risk/test_drawdown_tracker.py` |
| MOD-RK-05 var_calculator（Phase 1 参数法+历史模拟取 max） | `src/zephyr/risk/core/var_calculator.py` | 394 | ✅ `tests/risk/test_var_calculator.py` |
| Kill Switch 执行 | 归 D-RISK 域（drawdown_controller 仅产出 `kill_switch_advised` 建议，KS-L4 由 stop_loss 触发执行——代码 INVARIANTS 明示边界） | — | ✅ |

#### C. 仓位域其余已施工（与本备忘数据流直接相关，均 production 且测试在位）

- MOD-POS-001 `position_sizing_engine.py`（881 行，Kelly 精裁决层——§2.1 分层裁定步骤③的消费者，`tests/position/test_position_sizing_engine.py` 在位）
- MOD-POS-010 `position_limit_enforcer.py`（5% NAV 最终硬限兜底，32 号 §2.4 三层口径之一）
- `position_state_machine` / `position_drift_monitor` / `rebalance_engine` / `cash_manager` / `capital_curve_manager` / `calendar_position_constraint` / `sell_position_link` / `position_audit_logger` / `position_reconciler`——均 production，测试在位

#### D. 并存旧体系（功能重叠，裁定登记 §6.9）

- MOD-PA-003 `multi_strategy_capital_allocator.py`（production）——与 MOD-PA-007 功能重叠
- MOD-PA-002 `signal_synthesis_combiner.py` / MOD-PA-004 `strategy_correlation_gate.py`（均 production）——BM-SEL-20-A/C 旧投票体系残留
- pf_core 旧体系：`portfolio_optimizer` / `constraint_solver` / `rebalance_scheduler` / `performance_attribution_engine` / `strategy_engine` + 5 示例策略（均 production）——§7.3 已记 MOD-PF-002 暂缓弃用

#### E. 治理/文档设施缺口（登记 §6.8）

- `capability_canonical_file_registry.yaml`：4 模块未登记（仅 MOD-POS-009 一条 D_POSITION 记录）
- depgraph（PostgreSQL）：4 模块 maturity 仍 design → [64_d_position.md](../../02_domain_architecture_docs/64_d_position.md)（自动生成）标"设计态"滞后
- 测试：4 个测试文件丢失（见上表 ⚠️）

## 8. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-05 | 1.0.0 | 初稿 | 多策略并发架构选型定型，施工前记录推理防飘移 |
| 2026-08-05 | 1.1.0 | 补充分配公式+权重变动三级升级+灰度 regime+置信度→仓位映射；关闭 §6.5；新增 §6.6 | 策略权重分配与 budget 变动操作流程讨论定型 |
| 2026-08-05 | 1.2.0 | 移除 RegimeScore，分配公式改为 Base×Performance×Shrinkage；置信度映射改为风险节流语义；regime 仅用于 Shrinkage | 开源实证：regime alpha 择时降收益、风险节流改善回撤；与 A 模型"加法替代优化器"哲学对齐 |
| 2026-08-05 | 1.3.0 | §2.5 StrategyBook Drawdown Protocol（四级回撤阈值 8/15/20/25%+恢复机制+分层风控+VaR/ES+Kill Switch） | 用户确认"回撤是沉没成本属账户风控不属市场状态"+2026-08-05 行业搜索（LedgerMind/ARKA/Sina量化FOF/tradingwyckoff/赢牛资管） |
| 2026-08-09 | 1.3.1 | 文件名 design_memo_001_multi_strategy_concurrency.md → 30_multi_strategy_concurrency.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 1.3.2 | §1 管理规范链接 `design_memo_management_spec.md`→`01_design_memo_management_spec.md` | 改名工程遗留断链修复（全量断链扫描发现） |
| 2026-08-09 | 1.3.3 | 文档头统一：frontmatter 补 title/owner/language，H1 去"设计备忘·"前缀与 title 对齐；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-10 | 1.4.0 | 落实 [20 §5](20_first_batch_strategies.md) 待裁定-2/3 + why 补全 + 过度工程审查：① §4.3 pod 误标修正（Model A = Morwane 式统一风险框架，非 Citadel pod，附 resonanzcapital/Trium/algoalpha 2026 实证）；② §1.1 5 候选清单同步（主升龙头并入打板，多因子新增）；③ §1.3 情绪周期隐形驱动补 bayes-group March Shock 实证 + 交叉引用 28；④ §2.2/§2.4/§2.5 已施工部分 why 补全（核对源码：三模块骨架 design，回撤 Protocol 已 production）；⑤ §2.5.6 过度工程审查（Kill Switch/四级回撤保留为真红线，VaR 5 级+7 黑天鹅降级为监控层）；⑥ §2.5 口径漂移标注（四级回撤 vs 源码 5 级 VaR+7 黑天鹅）；⑦ §5 v1.4.0 处置说明；⑧ §7.4 补 2026 多策略架构实证 4 项；⑨ §2.2/§4.2 同步 [34](34_regime_meta_allocator.md) v1.0.0 并发升级（C1 验证已通过 commit 852457e9，框架 active；标注 12 态设计 vs 4 态已验证实现口径） | 20 §5 待裁定处置 + 源码施工状态核对 + 2026 行业实证补充；与 28 情绪周期×交易决策 active 1.0.0 同步定型；34 号同期升级 active，本版同步引用 |
| 2026-08-10 | 1.5.0 | 施工算法完整性审查 + 2026 算法实证补充：① §2.1 补 Fractional Kelly 比例（25-50%，三源共识 tradingengineeringlab/metatronics/astuteinvestorscalculus）；② §2.3 补叠加超限裁剪算法（裁定 pro-rata 按比例缩放，否决优先级裁剪，A 哲学延伸）；③ §2.4 补 Tier 2→Tier 3 收敛检测算法（ε_pos=5%+ε_days=1+无新违例，A 股 T+1 适配）；④ §2.5.1 补回撤恢复不对称数学（Recovery=D/(1-D)，25%需+33%恢复，支撑阈值合理性）；⑤ §4.2 补远期演进选项 Relaxed Risk Parity（ericxuzhesheng 2026-08-07，三因子→MVO 中间态）；⑥ §7.4 补 6 条 2026 仓位/风控算法实证（Fractional Kelly 共识/回撤恢复数学/Relaxed Risk Parity/HRP 12 算法对比/Bayesian uncertainty regime） | 施工环节流程算法缺失补全 + 2026 年 8 月最新研究实践算法搜索；与 28 号 v1.1.0 同步（28 补情绪周期迟滞/灰度/连板冰点，30 补 Kelly/裁剪/收敛/回撤数学/Relaxed RP） |
| 2026-08-10 | 1.6.0 | 选项外更优算法 + 2026-08 最新研究 + 口径修正：① §2.1 补 Bayesian Kelly Criterion（Sukhov 2026-06，f*=(p̄−(1−p̄)/b)·n_eff/(n_eff+κ) 样本自适应收缩，作为固定 Fractional Kelly 的 Phase 2 演进）；② §2.2 修正 PerformanceScore 口径 Sharpe→Sortino（对齐 34 号真源）；③ §2.3 补 Clipped Water-Filling（arXiv:2603.26893/15963 2026-03，minimax 最优，作为 pro-rata 的 Phase 2 候选，附 A 哲学一致性分析）；④ §2.4 补最优 no-trade 半带公式 b*=[3cσ²/(2λ)]^(1/3)（stockalpha 2026-02，布朗运动首达时间闭式解，TE·√3 反推）；⑤ §2.5.7 新增回撤度量补充与 EVT 尾部层（CDaR 离线度量 + POT-GPD/autoencoder 数据驱动黑天鹅补充 + Kill Switch SEC 标准印证）；⑥ §7.4 补 7 条 2026-08 算法实证 | 全网搜索 2026-08-08 最新研究，发现 3 个选项外更优算法（Bayesian Kelly/Water-Filling/no-trade 带宽）+ 2 个度量补充（CDaR/EVT）；修正 Sharpe→Sortino 口径漂移；与 28 号 v1.2.0 同步（28 补计数式迟滞/BOCPD，30 补 Bayesian Kelly/Water-Filling/no-trade/CDaR/EVT） |
| 2026-08-10 | 1.7.0 | 2026-08 最新研究整合 + 施工算法缺失审查：① §2.3 补多策略组合预期 Sharpe 基准（vzeman/trading-autoresearch 2026-05，cross-sectional momentum net Sharpe ~0.65，volatility-scaled 翻倍，综合 ~40 篇一手来源）；② §4.2 远期演进补 MPC 多期预测（Nystrup-Boyd 2019 Annals of OR，HMM 多期预测+回撤驱动风险厌恶，与 Model A 回撤节流同源，列为远期选项 B）；③ §4.3 补 RMATS 独立 Risk Agent 印证（arXiv:2605.25311 2026-05 APAM，MaxDD 9.62%<MVO 15.49%，独立 Risk Agent CVaR+stress test+circuit breaker 验证 FirmRiskAggregator 分层设计正确性；个人项目不采用多 agent 递归协调但取其风险解耦架构）；④ §6.7 新增策略级冷启动执行比例待定问题（施工算法缺失——§2.2 仅提 Base_i 未定义初始执行比例，行业标准 quanthedgeai 2026-07 research→paper→half-sized→full 三段式，初拟 ×30%→×60%→×100%）；⑤ §7.4 补 4 条 2026 实证（vzeman/Nystrup-Boyd/RMATS/quanthedgeai） | 全网搜索 2026-08 最新研究，发现 3 项需整合（RMATS 独立 Risk Agent 印证/Systematic Equity Sharpe 基准/MPC Boyd 远期演进）+ 1 项施工算法缺失（策略级冷启动执行比例）。个人项目不采用 RMATS 多 agent 递归协调（§5 暂缓——AI 写 AI 失控风险+投入产出比低），但取其"独立 Risk Agent"架构印证 Model A FirmRiskAggregator 分层设计正确性 |
| 2026-08-10 | 1.8.0 | 四次算法审查 + 选项外更优算法 + 2026-08-08 最新研究：① **§2.1 补 Conformal Kelly**（arXiv:2608.01494v1 2026-08-02，用 conformal prediction 75% 区间宽度作为 Fractional Kelly 缩放因子，绕过 p/b 估计；6 年开发窗口 Sharpe 1.34/MaxDD 27.7%；反直觉发现"区间快速适应 regime 损失 0.7-5.3pp 年增长"印证 §2.2 regime 哲学；drawdown dial 集成 MaxDD 27.7%→20.3%；Lockbox OOS 增长未保持需谨慎；列为 Phase 3 远期候选）；② §7.4 补 3 条 2026-08 四次审查实证（Conformal Kelly/vzeman 5 级 drawdown sizing 行业对照/Morwane 2026-06-10 sleeve-addition+robustness 更新）；③ vzeman 5 级 drawdown sizing（0-5% Full/5-10% 75%/10-15% 50%/15-20% 25%/>20% Halt）作为 §2.5.1 四级阈值行业对照——本项目 4 级 8% 起步更保守（A 股 T+1 容错），vzeman 5 级 5% 起步适合美股日内调仓 | 全网搜索 2026-08-08 最新研究实践算法，发现 1 个选项外更优算法（Conformal Kelly——比 Bayesian Kelly 更前沿，绕过 p/b 估计+回撤集成+OOS 诚实性，但 Lockbox 增长未保持故列远期）+ 1 项行业对照（vzeman 5 级 drawdown sizing 印证四级阈值合理性）；Conformal Kelly 的反直觉发现"稳定性比局部锐度更重要"直接印证 §2.2 regime→Shrinkage 风险节流哲学 |
| 2026-08-10 | 1.9.0 | 五次算法审查 + 施工算法缺失填补 + 选项外更优算法：① **§6.2 G07 相关性验证补 correlation drop rule 施工算法**（youcanbuildthings 2026-05，90 天滚动相关性 >0.70 持续 30 天→drop 低 Sharpe；A 股适配阈值 0.70→0.60+按情绪周期分层+三级响应 0.6 审视/0.6-0.7 监控/>0.7 暂停部署）；② §7.4 补 2 条 2026-08 五次审查实证（youcanbuildthings correlation drop rule + Regime-Adaptive Meta-Policies 三操作点架构评估）；③ Regime-Adaptive Meta-Policies（Kou 2026-05）"direct optimization is safer in low-signal settings"印证 Model A 在 A 股低信号环境适用性，提供"何时升级到 routing"评估条件（策略数 >8 且分散度高时） | 用户要求再次审查施工环节流程算法缺失+选项外更优算法+2026-08-08 最新研究+持续改进不停。**G07 施工算法缺失填补**：§6.2"施工前必做"但无具体算法→补 correlation drop rule（Python 实现+三级响应阈值+A 股适配）。**选项外更优算法**：Regime-Adaptive Meta-Policies 提供"何时 Model A 需要升级"的 regime-conditional 评估框架，但当前不采纳（Model A 已裁定不做 routing/consensus） |
| 2026-08-10 | 2.0.0 | §2.3 补 **A 股 2026 上半年量化超额衰减市场环境校准**（新浪财经 2026-07-11：1236 只量化多头平均收益 16.25% 但超额从 14.17%骤降至 3.11%，K 型行情+因子失效+策略同质化三根因；中证 500 指增超额仅 0.85%；校准意义：多因子 sleeve 超额预期下调，打板 sleeve 情绪周期择时与横截面 alpha 正交仍可获超额，实盘 Sharpe<0.3 优先排查相关性而非 alpha 不足） | 六次审查全网搜索 2026-08-08 最新研究，发现 A 股 2026H1 量化超额骤降数据（14.17%→3.11%）对项目预期管理有实质校准价值——印证"风险节流不做 alpha 择时"在 alpha 衰减期更稳健，且为实盘 Sharpe 基准 0.6-0.85 提供"K 型行情下需下调"的现实约束。版本号跳 v1.9.0→v2.0.0 标记市场环境校准是里程碑级更新（影响首批策略预期管理） |
| 2026-08-10 | 2.1.0 | §6.7 策略级冷启动执行比例从"待裁定"升级为"MVP 基线已定，待 C1 实盘校准" | 三十七轮施工算法完整性审查发现 30 号文档唯一"设计待定"项——§6.7 策略级冷启动执行比例（初拟方案 ×30%→×60%→×100% 三段式但标注"待裁定"）。经审查初拟方案已有完整三段式+晋升条件+行业标准支撑（quanthedgeai 2026-07 paper→half→full 三段式）+与 BudgetChangeHandler 联动设计，符合风险优先原则。裁定：①MVP 基线采纳三段式（与 53 号 PARALLEL→SHADOW→GRAY_RAMP 同构）；②参数待 C1 校准（Sharpe>1.5 可加速两段式，<0.8 延长冷启动期）；③冷启动期 budget 上调用 Tier 1+2 不触发 Tier 3 强裁；④与 25 号因子治理灰度正交；⑤Kill Switch 系统级全效不受冷启动缩放影响。新增施工指导：allocate() 增 cold_start_ratio 参数。§6.7 是 30 号唯一设计待定项，本次裁定后 30 号施工算法完整性闭环 |
| 2026-08-10 | 2.2.0 | §2.2 StrategyBook 输入/输出接口契约补全（跨文档算法交接完整性审查——链路 2/6 缺口修复）：① **情绪周期阶段信号接口**（链路 2：28号→30号）——补 `SentimentStageSignal(stage, confidence, retreat_weight, timestamp)` 数据结构 + 退潮加权系数（默认 1.5，打板 1.5/事件 1.3/多因子 1.2 差异化）+ 降级路径（confidence<0.6 降级为 regime ⑧）+ 与 regime 正交性声明；② **target_portfolio 权重口径声明**（链路 6 缺口 1：32号→30号）——显式声明 `target_weight` 是相对 strategy_budget 占比非绝对权重，32号 §2.2 据此做 budget 归一化 `account_weight = tp_weight × budget_used / total_budget`，施工注记要求 strategy_book.py 输出注释声明此口径；③ **score→weight 转换接口**（链路 6 缺口 2：25号→21号→30号）——文档化 25号 IC 加权合成评分[-3,3]→StrategyBook 内部三维度解耦（选股 top-N / 仓位 Kelly·RP·等权 / 风控独立）的转换路径，当前骨架态待首批策略施工形式化 | 跨文档算法交接完整性审查（后台 agent 6 链路审查）：链路 2（28→30 情绪周期→多策略）缺口=情绪阶段→StrategyBook 接口未定义；链路 6（25→32 多因子→firm）缺口 1=30号口径未显式声明，缺口 2=score→weight 转换未文档化。均为"接口契约未显式文档化"非"算法逻辑断裂"，严重性中等。本次补全后 4 条有缺口链路中的 2 条（链路 2/6）闭环 |
| 2026-08-10 | 2.3.0 | **StrategyBook（MOD-POS-020）代码施工完成**：`strategy_book.py` 从骨架（MATURITY=design, v0.1.0）升级到 production（v1.0.0）。实现内容：① `build_target_portfolio()` 主入口——选股+粗仓位+budget裁剪+回撤Protocol+情绪周期信号缓存+cash_ratio 计算；② `rebalance_to_budget()` budget 适配——上调保留仓位现金拖累可接受/下调按 confidence 降序砍最不自信仓位（§2.4 Tier 2）；③ `compute_performance_score()` 60 日滚动 Sortino→[0.5,1.5] 映射（§2.2 口径对齐 34号 §3.1）；④ `size_positions()` equal_weight/risk_parity（inverse-vol，Morwane 实证）/custom 降级等权；⑤ 回撤 Protocol 四级（Level 1 8%/Level 2 15%/Level 3 20%/Level 4 25%+强制休息 5 天，§2.5.1 行业基准）；⑥ `SentimentStageSignal` 接口（28号→30号 链路2，退潮加权打板1.5/事件1.3/多因子1.2+降级路径 confidence<0.6 回退1.0）。测试 70 个用例全绿（0.15s）。同步：§2.2 施工状态从"三模块骨架"更新为"StrategyBook+FirmRiskAggregator 已 production，BudgetChangeHandler 待施工" | 代码施工路径规划推荐 32号 FirmRiskAggregator 后转 30号 StrategyBook（32号 DEPENDENCIES 上游）。StrategyBook 是 A 模型核心实体——每个策略自洽选股+粗仓位+独立风控，输出 target_portfolio 交 FirmRiskAggregator。施工完成填补策略层代码真空，与已完成的 FirmRiskAggregator（54 测试）形成完整数据流：StrategyBook→FirmRiskAggregator→MOD-POS-001。三模块中仅剩 BudgetChangeHandler（MOD-POS-022）待施工 |
| 2026-08-10 | 2.4.0 | **BudgetChangeHandler（MOD-POS-022）代码施工完成 + 三模块全部 production 里程碑**：`budget_change_handler.py` 从骨架（MATURITY=design, v0.1.0）升级到 production（v1.0.0）。实现内容：① `handle_budget_change()` 主入口——5 规则优先级（上调不防抖/收敛中re-target/<5%防抖/≥5%触发/累计>10%强制触发）+ 三级升级编排（Tier1封锁→Tier2 rebalance→Tier3超时强裁）；② `check_convergence()` 收敛检测——ε_pos=5%+ε_days=1+超时升级Tier3（trim_ratio=(exposure-target)/exposure）；③ `_retarget_in_convergence()` 收敛中再变动——上调停止Tier3强裁/下调更新target重置窗口；④ 防抖机制——日内<5%忽略+日间累计>10%强制+新交易日重置；⑤ 三级指令生成（FreezeNewPositions/RebalanceRequest/ForcedTrim）——纯逻辑层不直接调用broker，调用者负责执行。测试 47 用例全绿（0.12s）。**三模块全部施工完成里程碑**：StrategyBook(70)+FirmRiskAggregator(54)+BudgetChangeHandler(47) = 171 测试全绿，A 模型核心数据流 StrategyBook→FirmRiskAggregator→MOD-POS-001 完全贯通。设计决策：circuit breaker/大宗交易/TWAP 等执行层交互作为可选 hook 不在本模块实现（归 D-EX-CORE 执行层），本模块只生成指令保持纯逻辑可单元测试 | 三模块最后一个骨架 BudgetChangeHandler 施工完成。设计文档 §3.4 伪代码含完整 circuit breaker/大宗交易/TWAP/2026-07-07 A股新规等执行层细节，但代码实现聚焦核心三级升级状态机（可纯单元测试），执行层交互归 D-EX-CORE。三模块全部 production 标志 A 模型仓位管理 sleeve 层→firm 层→budget 变动处理层完整贯通 |
| 2026-08-10 | 2.5.0 | **文档-代码一致性修复**（六十五轮）：§2.4 施工状态行 L214（"budget_change_handler.py 当前骨架 MATURITY=design"）+§7.2 depgraph 模块登记表（"已登记到 depgraph 设计态 build_status=planned, design_maturity=design"）2 处描述滞后修复——对照实际源码 budget_change_handler.py / strategy_book.py / firm_risk_aggregator.py 全部 `MATURITY=production`，仅 regime_meta_allocator.py 仍 design。§7.2 模块登记表新增"当前状态（2026-08-10 核对源码）"列明示每个模块 production/design 状态，与 [33号 v2.10.0](33_budget_change_handler.md) + [32号 v1.0.20](32_firm_risk_aggregator.md) 文档-代码一致性审查结论对齐 | 六十五轮文档-代码一致性深度审查扩展到 30号——发现 30号 §2.4 L214（v2.3.0 之前描述，v2.4.0 修订记录已说明施工完成但 L214 漏改）+§7.2 模块登记表（v1.0.0 时期历史登记）两处描述滞后。**方法论价值**：本轮证明即使文档自身已在修订记录正确登记施工里程碑，正文描述行仍可能滞后未同步——"修订记录正确≠正文描述正确"，是文档-代码一致性审查的次要新角度（应同时核验"正文状态描述行"与"修订记录条目"） |
| 2026-08-12 | 2.6.0 | **灾后全量设施盘点 + 文档-代码-测试三方一致性修复**：① §2.2 施工状态修正——RegimeMetaAllocator 实际已 production（MOD-PA-007 v1.0.0，594 行，0 处 NotImplementedError，34 号 v2.7.0 先行确认），v2.5.0"代码仍骨架 design 态"误记修正；"代码 production≠上线"（参数待 PnL 校准仍 P3）；② ⚠️ 披露 2026-08-11 git clean 灾难（#ARCH-GIT-CLEAN-GUARD-FIX）测试丢失——4 个测试文件（70/54/47/55 共 226 测试）创建未 `git add` 被删且 git 历史无记录，此前"171+55 测试全绿"当前无法复现；③ §2.4 对 [33号 v2.10.0](33_budget_change_handler.md) 引用修正——33 号内容丢失回退骨架 v0.1.0，G14 真源待重建（临时真源=代码 docstring）；④ §5 待裁定更新——数字孪生/世界模型行改为 #ARCH-OE-010 已 decided 裁剪（2026-08-11 用户确认，远期不采纳），LLM 多 Agent 行补 #ARCH-OE-011 关联裁定（CC-14 降级可选）；⑤ §6.8 新增灾后重建事项 4 项（测试重建/33 号重建/capability registry 补登记/depgraph maturity 滞后）；⑥ §6.9 新增并存旧体系裁定 3 项（MOD-PA-003 与 PA-007 功能重叠/MOD-PA-002+PA-004 旧投票体系残留/pf_core 5 示例策略关系未定）；⑦ §7.2 表四模块全 production 更新+测试丢失标注；⑧ §7.5 新增已施工设施盘点（规则 #11：position/pf_alloc/pf_core/risk 四域全量）；⑨ §2.2 接口契约②补字段名三方漂移 P0 标注（TargetPortfolio.positions/budget vs 伪代码 target_portfolio/budget_used，直接传对象会静默产出全现金组合）+ ③骨架态措辞修正 | 架构审查任务（30/32 号）第 1-3 轮：读现状+全量基础设施盘点发现 7 类问题（RegimeMetaAllocator 状态滞后/33 号骨架化引用悬空/测试丢失/registry 未登记/depgraph 滞后/PA-003 重叠/§5 与 ARCH-OE decided 不一致），第 3 轮算法审查新发现 StrategyBook→FirmRiskAggregator 接口字段名三方漂移 P0 断裂风险。按"事实性漂移修复 + 决策类登记开放问题不擅自定"原则处置。**施工方式**：worktree 隔离（主区并发会话持续回退致修改 3 次丢失，用户裁定改 worktree 施工）。**第 4-6 轮续**：④ 第 4 轮 2026-08-12 全网搜索——§7.4 新增"六次审查实证补充"2 条（Paloma 2026-07-17 砍半数 PM 团队聚焦高确信策略=机构级"少而精"印证+量化拥挤超额衰减全球现象；Candriam CAMS 2026-06-25 单一交易账本聚合+三态 regime 动态再配置=Model A 同构机构案例）；⑤ 第 5 轮过度工程审查**零新发现**——§2.5.6（VaR/ES+Kill Switch 分级降级）与 32 号 §4.4（行业/总仓位硬约束必需非过重）既有裁定充分，三模块+三级升级已施工代码量适度（651/680/572 行）无过度；⑥ 第 6 轮一致性审查**零新修复**——与 31 号接口一致/33 号骨架化已处置/34 号 RegimeMetaAllocator 已对齐/35 号口径分裂双向承认（映射归 35 号 §3.2）/54 号引用正确 |
| 2026-08-15 | 2.6.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-07） | §2.1/§2.3/§4.2 实证与 §7.4 重复出处指针化；§2.2/§2.4/§2.5 施工状态过程叙述→当前态结论；§2.3 超额衰减长散文要点化；§4.3/§5 strikethrough 清理（当前态陈述）；§6.7 审查过程叙述→裁定要点；§7.2/§7.4 长条目瘦身。标题编号/关键数值（四级回撤 8/15/20/25%、FLOOR 5%/CAP 40%、ε_pos=5%、冷启动 ×30/60/100%、Sharpe 基准 0.6-0.85、熔断 4%/6%）/裁定/开放问题/BM-XXX/#ARCH-XXX/跨文档链接零丢失 |
