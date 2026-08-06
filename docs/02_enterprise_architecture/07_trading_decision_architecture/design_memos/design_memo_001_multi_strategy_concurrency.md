---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.3.0"
date: 2026-08-05
topic: multi_strategy_concurrency
scope: 07_trading_decision_architecture
---

# 设计备忘·多策略并发架构

> 本备忘记录多策略并发执行架构的选型推理与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [design_memo_management_spec.md](design_memo_management_spec.md)。

## 1. 背景

### 1.1 项目处境
- 个人 + 100% AI 开发，迭代速度极快（3-4 个月达到当前规模）
- 部署目标：A 股个人账户（miniQMT 通道），非机构体量
- 多策略并发需求：5 个候选策略（价值反转 / 动量趋势 / 事件驱动 / 打板 / 主升龙头）
- 当前处于施工前阶段，架构一旦落地难以回改，故施工前定上限

### 1.2 核心问题
多策略并发有 4 种架构模型（A 独立账本 / B 因子混合 / C 策略之策略 / D 投票融合），选型决定整个系统的复杂度、归因能力、迭代速度。模型选错会导致技术债滚雪球，且 AI-dev 下归因不清=迭代停滞。

### 1.3 约束条件
- A 股几乎不能做空 → 对冲式优化失效
- T+1 结算 → 策略难以日内翻转，独立账本更顺
- 打板策略容量极小（单票可能仅几万到几十万）→ 必须小账本独立运行
- 情绪周期（冰点/反核/主升/疯狂/退潮）是所有短周期策略的共同隐形驱动 → 策略间相关性可能高于直觉
- AI 开发 → 故障隔离与归因清晰度是生存项，不是优化项

## 2. 决策：Model A（独立账本 + firm 风险聚合）

### 2.1 架构定义

每个策略是一个独立 StrategyBook（自带选股+**粗**仓位+风控），firm 层做"求和 + 硬上限裁剪 + **Kelly 精裁决** + regime 风险预算调整"，**没有统一优化器，没有跨策略投票**。

> **分层裁定（2026-08-06，方案A）**：仓位决策分两层——StrategyBook 做"策略层粗仓位"（等权/risk parity，**不用 Kelly**），MOD-POS-001 做"组合层 Kelly 精裁决"。第一性原理：组合级约束（单票上限跨策略叠加）天然在 firm 层；Kelly 需密度预测不宜每策略重复；风险合规与 alpha 解耦防归因纠缠。开源印证：Morwane sleeve(alpha)+risk-parity-throttle(firm) 分层。详见各模块 blueprint（[MOD-POS-020](../../../03_modules/_domain_position/strategy_book/blueprint.md) / [MOD-POS-021](../../../03_modules/_domain_position/firm_risk_aggregator/blueprint.md) / [MOD-PA-007](../../../03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md) / [MOD-POS-022](../../../03_modules/_domain_position/budget_change_handler/blueprint.md)）。

### 2.2 三个核心模块

#### StrategyBook（N 个，N=3~5）
- 输入：策略自己的 alpha 信号
- 内部：自带仓位算法（Kelly / risk parity / 简单等权，**不用 MVO**）
- 输出：target_portfolio（标的+目标仓位）
- 独立 PnL 归因、独立风控参数、独立资金预算

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
- 输出：各 StrategyBook 的**资金预算占比**（不是选股权重，不是仓位权重）
- 分配公式：

  ```
  allocation_i = normalize( Base_i × PerformanceScore_i × Shrinkage_i )
  ```

  > **裁定（2026-08-05）：移除 RegimeScore，regime 仅通过 Shrinkage 做风险节流。**
  > 开源实证：regime-based alpha 择时降低收益（检测器误差被主动重定向放大），regime-based 风险节流改善回撤（防御性，误差容忍）。
  > 误差不对称：alpha 择时判错=主动亏损，风险节流判错=机会成本。RegimeScore 在 meta 层重新引入估计误差放大，与 A 模型"加法替代优化器"哲学矛盾。
  > 策略亲和性由 PerformanceScore（后验 PnL）自然捕获——momentum 在趋势态表现好→滚动 Sharpe 上升→有机获得更多 budget，无需 regime 前瞻下注。

  | 因子 | 含义 | 关键纪律 |
  |---|---|---|
  | Base_i | 先验权重（等权 1/N 或人工先验） | 新策略冷启动只用这个 |
  | PerformanceScore_i | 策略 i 近期滚动风险调整收益（60 日 Sharpe） | 映射 [0.5, 1.5]，防极端；后验 PnL 自然捕获 regime 亲和性 |
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

### 2.5 StrategyBook Drawdown Protocol（账户级回撤风控，2026-08-05）

> **用户裁定（2026-08-05）**：回撤是沉没成本，不参与下一次决策（不进入 RiskSignal），但触发账户级风险节流（减仓/停仓/清仓）。
> **定位**：drawdown protocol 是 StrategyBook 内部风控，不属于 regime 检测器的 RiskSignal。regime 管"市场状态风险"，drawdown protocol 管"账户生存风险"。
> **行业搜索**：LedgerMind Systematic Risk Framework 2026-05、ARKA Global Investments 2026、Sina 量化风控 2026-07、Sina 量化FOF 2026-07、tradingwyckoff Drawdown Guide 2026-01、赢牛资管 VaR-ES 2026-05。

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

### 4.3 为何这是上限而非妥协
- Citadel/Millennium 的 pod 模型本质就是 A（独立账本 + firm 风险聚合），**没有统一 MVO**
- 5 个策略的 MVO 收益 < 5 个策略独立加总收益，因为协方差估计误差 > MVO 理论增益
- 真正的上限 = 在 A 框架内把每个 StrategyBook 做到极致，而不是在 firm 层堆优化器
- 差异化 alpha 在 A 股打板/游资/连板领域深度（BM-SEL-22~25），统一优化器不是护城河

## 5. 待裁定（暂缓）

> 以下项目暂不施工，**非永久禁止**。待项目演进到一定程度，部分项可能自然不再成立，部分项可能重新需要。届时回看本节，重新裁定。每项附"重评条件"——满足时可重新讨论。

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| firm 层统一 MVO 优化器 | 协方差估计是研究课题；放大噪声；归因纠缠 | 协方差估计方案成熟（如因子模型+shrinkage 验证有效） |
| firm 层跨策略选股投票 | A 的自然叠加已等价实现；O(N²) 冲突是技术债 | 策略数显著增加（>8）且自然叠加不足 |
| 数字孪生 / 世界模型 DreamerV3 / TD-MPC2 | 研究前沿，非生产工具；投入产出比对个人系统极低 | 算力充裕（GPU≥48GB）且模型成熟度达到生产级 |
| LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索 | 研究议题，作战地图之外；AI 写 AI 的失控风险高 | 可控性方案（沙箱+审批+回滚）验证可靠 |
| 60 个活跃因子 / 150 设计容量 | 个人系统 8-15 个因子足够；多了是过拟合温床 | AUM 增长到需要更多因子分散 |
| 56 条硬边界一视同仁 | 砍到 10 条真红线（Fail-Closed）+ 其余降为指导原则 | 团队扩大或合规要求升级 |

## 6. 待定问题

### 6.1 首批上线的 3 个策略（需人决策）
5 个候选策略不可能齐平，弱策略拖累归因清晰度。建议首批上 3 个最自信的，跑 3 个月有 track record 后再加第 4、5 个。

候选组合（待确认）：打板 + 多因子 + 事件驱动

### 6.2 策略间相关性验证（施工前必做）
用历史数据算 5 个策略两两相关矩阵，按情绪周期分层看。若各阶段相关性都 >0.6，"多策略"实为"情绪 beta 穿多件衣服"，需重新审视策略组合。

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
讨论文档：[discussion_001_regime_detector_spec.md](discussion_001_regime_detector_spec.md)

## 7. 引用

### 7.1 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)（选股阶段，双引擎融合等机制在此阶段内部保留）
- [battle_map_12_cross_cutting.md](../battle_map/battle_map_12_cross_cutting.md)（§16 冲突矩阵大部分将因 A 架构而消失）
- [battle_map_10_execution.md](../battle_map/battle_map_10_execution.md)（执行阶段，FirmRiskAggregator 输出在此下单）

### 7.2 depgraph 模块（已登记 2026-08-05）
以下模块已登记到 depgraph 设计态（build_status=planned, design_maturity=design）：

| 模块 | blueprint_id | path | domain_id | 说明 |
|---|---|---|---|---|
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | D_POSITION | 独立策略账本，自带选股+仓位+风控 |
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | D_POSITION | firm 层求和+硬上限裁剪，不做 MVO |
| RegimeMetaAllocator | MOD-PA-007 | `src/zephyr/pf_alloc/core/regime_meta_allocator.py` | D_PF_ALLOC | regime 灰度概率→Shrinkage 风险节流，第二阶段上 |
| BudgetChangeHandler | MOD-POS-022 | `src/zephyr/position/core/budget_change_handler.py` | D_POSITION | 三级升级（封锁→自平衡→强裁），执行 budget 变动 |

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

## 8. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-05 | 1.0.0 | 初稿 | 多策略并发架构选型定型，施工前记录推理防飘移 |
| 2026-08-05 | 1.1.0 | 补充分配公式+权重变动三级升级+灰度 regime+置信度→仓位映射；关闭 §6.5；新增 §6.6 | 策略权重分配与 budget 变动操作流程讨论定型 |
| 2026-08-05 | 1.2.0 | 移除 RegimeScore，分配公式改为 Base×Performance×Shrinkage；置信度映射改为风险节流语义；regime 仅用于 Shrinkage | 开源实证：regime alpha 择时降收益、风险节流改善回撤；与 A 模型"加法替代优化器"哲学对齐 |
| 2026-08-05 | 1.3.0 | §2.5 StrategyBook Drawdown Protocol（四级回撤阈值 8/15/20/25%+恢复机制+分层风控+VaR/ES+Kill Switch） | 用户确认"回撤是沉没成本属账户风控不属市场状态"+2026-08-05 行业搜索（LedgerMind/ARKA/Sina量化FOF/tradingwyckoff/赢牛资管） |
