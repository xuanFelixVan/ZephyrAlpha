---
module_id: MOD-POS-022
title: "Budget变动处理器蓝图 — 三级升级落地+convergence_window+超时强裁（A模型·执行层）"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
build_status: stable
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-06"
last_updated: "2026-08-06"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-022 BudgetChangeHandler — Budget变动处理器 蓝图

> **module_id**: MOD-POS-022 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: design | **建设标记**: 🟡 待施工
> **SSoT**: depgraph MOD-POS-022 | **设计真源**: [30_multi_strategy_concurrency.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.4（权重变动操作流程·三级升级）
> **上游触发**: [RegimeMetaAllocator blueprint](../_domain_portfolio_alloc/regime_meta_allocator/blueprint.md) MOD-PA-007 §2.2 BudgetChanged 事件 (E-PA-07)
> **执行目标**: [StrategyBook blueprint](../strategy_book/blueprint.md) MOD-POS-020 §3.3 rebalance_to_budget 接口

## 1. 定位

Budget 变动处理器——A 模型（[30_multi_strategy_concurrency](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.4）的执行层。当 RegimeMetaAllocator 产出新 `BudgetAllocation` 导致某策略 budget 变动时，本模块负责**把 budget 变动落地到 StrategyBook**——三级升级（Tier 1 封锁 → Tier 2 自主 → Tier 3 强裁），确保策略适配新 budget，策略不能说"我不卖"。

属 **A 类基础设施**（事件驱动 + 状态机 + 超时升级，逻辑明确），convergence_window / 超时阈值为 C 类可调参数。

### 1.1 核心原则（30_multi_strategy_concurrency §2.4）

> **budget 是硬约束**（来自 meta 层），策略的自主权在"怎么适应 budget"，不在"要不要适应"。策略必须实现 `rebalance_to_budget(new_budget)` 接口——**策略不能说"我不卖"**。

> **三级升级而非直接强砍**：尊重策略自主权（决定砍哪个）+ 避免随机时刻强制卖出的高成本。

### 1.2 分层边界

| 层 | 模块 | 职责 |
|---|---|---|
| meta 分配 | RegimeMetaAllocator (MOD-PA-007) | 产出 BudgetAllocation，budget 变动时发 BudgetChanged 事件 |
| **执行层** | **BudgetChangeHandler (本模块)** | **接收 BudgetChanged → 三级升级落地 → 确保 StrategyBook 适配** |
| 策略层 | StrategyBook (MOD-POS-020) | 接收 rebalance 指令，自主选砍哪些仓位 |

**数据流**：
```
RegimeMetaAllocator ──BudgetChanged事件──→ BudgetChangeHandler
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    ▼                           ▼                           ▼
              Tier 1: 封锁新仓            Tier 2: 策略自主             Tier 3: 强制裁剪
              (立即，被动)               (rebalance_to_budget)         (dumb but safe)
                    │                           │                           │
                    └───────────────────────────┴───────────────────────────┘
                                                │
                                                ▼
                                         StrategyBook 适配新 budget
```

### 1.3 不做什么

- **不做 budget 计算**（归 RegimeMetaAllocator）
- **不做选股 / 仓位裁决**（归 StrategyBook / MOD-POS-001）
- **不决定砍哪个仓位**（Tier 2 由策略自主决定；Tier 3 按比例 dumb 裁剪）
- **不执行交易**（归 D-EX-CORE；本模块只产出 rebalance 指令）
- **不处理 budget 上调**（上调简单，StrategyBook 直接抬高上限自然部署，30_multi_strategy_concurrency §2.4）

## 2. 输入 / 输出

### 2.1 输入

| 方向 | 内容 | 契约/事件 | 来源 | 就绪 |
|------|------|-----------|------|:----:|
| 触发 | BudgetAllocation（新分配方案） | CTR-PA-007 | RegimeMetaAllocator (MOD-PA-007) | ❌ 待建 |
| 事件 | BudgetChanged（budget 变动事件，含 old/new 对比） | E-PA-07 | RegimeMetaAllocator | ❌ 待建 |
| 配置 | ConvergenceWindows（各策略 convergence_window，按换手率差异化） | config | 配置文件 | 🟡 待校准（30_multi_strategy_concurrency §6.4） |
| 持仓 | PositionSnapshot（当前持仓，Tier 3 强裁计算用） | CTR-006 | D-EX-CORE | ⚠️ 部分 |
| 反馈 | StrategyRebalanced（策略 rebalance 完成反馈） | E-POS-20 | StrategyBook | ❌ 待建 |

### 2.2 输出

| 方向 | 内容 | 契约/事件 | 去往 |
|------|------|-----------|------|
| 指令 | FreezeNewPositions（Tier 1 封锁新仓指令） | CTR-POS-022-F | StrategyBook (MOD-POS-020) |
| 指令 | RebalanceRequest（Tier 2 rebalance 请求，含 new_budget） | CTR-POS-022-R | StrategyBook (MOD-POS-020) |
| 指令 | ForcedTrim（Tier 3 强制裁剪指令，含裁剪比例） | CTR-POS-022-T | FirmRiskAggregator (MOD-POS-021) / D-EX-CORE |
| 事件 | BudgetChangeHandled（变动处理完成） | E-POS-40 | RegimeMetaAllocator + Trader（归因用） |
| 事件 | TierEscalation（升级事件，记录 Tier 1→2→3 流转） | E-POS-41 | Trader + 归因系统 |

## 3. 核心规则：三级升级（30_multi_strategy_concurrency §2.4）

### 3.1 触发判定

```
收到 BudgetChanged 事件:
    对每个 strategy_i:
        old_budget = 旧 allocation_i × old_global_shrinkage
        new_budget = 新 allocation_i × new_global_shrinkage
        delta = new_budget − old_budget

        if delta ≥ 0:  budget 上调 → 不处理（StrategyBook 自然部署，§3.5）
        if delta < 0:  budget 下调 → 启动三级升级（§3.2-3.4）
```

> **只处理下调**：上调简单（抬高上限 + 买入信号自然部署），不需要 Handler 介入（30_multi_strategy_concurrency §2.4）。

### 3.2 Tier 1：封锁新仓（立即，被动）

| 属性 | 值 |
|------|-----|
| 触发时机 | budget 下调瞬间 |
| 性质 | 立即，被动 |
| 动作 | StrategyBook 不允许开任何新仓，现有仓位不动 |

```
对 strategy_i 发送 FreezeNewPositions(strategy_id, frozen=True):
    StrategyBook 标记 frozen=True
    后续 generate_alpha_signals 产出的新标的被拒绝（不开仓）
    现有持仓不强制变动
```

> **设计理由**：budget 下调第一时间止血——封锁新仓防止策略用旧 budget 的惯性继续开仓。现有仓位给策略时间自主处理（Tier 2）。

### 3.3 Tier 2：策略自主 rebalance（建议，策略自主）

| 属性 | 值 |
|------|-----|
| 触发时机 | Tier 1 后立即 |
| 性质 | 建议，策略自主 |
| 动作 | 发送 rebalance_to_budget 请求，策略自选砍哪些仓位（砍最不自信的） |
| 窗口 | convergence_window_i（按换手率差异化，§3.6） |

```
对 strategy_i 发送 RebalanceRequest(strategy_id, new_budget, deadline):
    StrategyBook 调用 rebalance_to_budget(new_budget)
    策略自主决定:
        - 砍哪些仓位（按 confidence 最低 / 持仓时间最短 / 收益最差排序）
        - 砍多少（使 total_weight ≤ new_budget）
        - 返回新的 TargetPortfolio
    完成后发送 StrategyRebalanced 事件

if 在 convergence_window 内收到 StrategyRebalanced:
    Tier 2 成功 → 关闭 FreezeNewPositions（frozen=False）→ 流程结束
if convergence_window 超时未收到:
    升级 Tier 3
```

> **设计理由**：尊重策略自主权——策略最清楚自己哪个仓位最不自信。避免随机时刻强制卖出（高冲击成本 + 可能砍掉即将盈利的仓位）。

### 3.4 Tier 3：强制裁剪（强制，firm 层）

| 属性 | 值 |
|------|-----|
| 触发时机 | Tier 2 窗口超时 / firm 风险违例 |
| 性质 | 强制，firm 层（绕过策略自主权） |
| 动作 | 按比例强行裁剪所有仓位（dumb but safe） |

```
触发条件:
    (a) convergence_window 超时，策略未完成 rebalance
    (b) firm 风控违例（FirmRiskAggregator 报告组合级硬约束被破坏）

执行 ForcedTrim(strategy_id, cut_ratio):
    cut_ratio = new_budget / current_total_weight    # 等比裁剪至新 budget
    对 strategy_i 的每个持仓:
        target_qty *= cut_ratio
    直接生成裁剪指令 → FirmRiskAggregator / D-EX-CORE 执行
    不经过 StrategyBook 的 rebalance_to_budget（绕过策略自主权）

Tier 3 完成后:
    关闭 FreezeNewPositions
    记录 TierEscalation 事件（Tier 2 超时 → Tier 3 强裁）
    标记 strategy_i 为 "forced_trimmed"（归因用）
```

> **设计理由**：dumb but safe——策略死扛不卖时，firm 层兜底。按比例等比裁剪（不挑仓位），保证 budget 约束被满足。宁可错杀不可漏放（与 Kill Switch 原则一致，30_multi_strategy_concurrency §2.5.5）。

### 3.5 Budget 上调处理（不经过三级升级）

```
if delta ≥ 0 (budget 上调):
    直接更新 strategy_i 的 budget 上限
    关闭 FreezeNewPositions（如之前被冻结）
    StrategyBook 通过自己的买入信号自然部署新资金
    不需要强制动作；现金拖累可接受（现金也是一种仓位）
    唯一约束：新买入后总暴露 ≤ 新 budget
```

> 上调无需 Handler 介入——StrategyBook 直接收到新 budget 上限，自然部署。Handler 只记录 BudgetChangeHandled 事件（归因用）。

### 3.6 ConvergenceWindow（按换手率差异化，30_multi_strategy_concurrency §6.4 待校准）

| 策略类型 | convergence_window | 理由 |
|---------|:------------------:|------|
| 打板（高换手） | 1-2 交易日 | 持仓周期短，自然快速收敛 |
| 事件驱动（中换手） | 2-3 交易日 | 事件发酵有节奏，给中等时间 |
| 多因子（低换手） | 3-5 交易日 | 持仓周期长，给充足时间自主调仓 |

> **初始值待校准**（30_multi_strategy_concurrency §6.4 需人决策）：首批 3 策略确定后，用历史换手率数据校准。config 可调，支持 per-strategy 配置。

### 3.7 高换手 vs 低换手策略的收敛特征（30_multi_strategy_concurrency §2.4）

| 策略类型 | Tier 1+2 收敛 | Tier 3 触发频率 |
|---------|:-------------:|:---------------:|
| 高换手（打板） | 1-2 天自然收敛 | 极低（持仓本就短命） |
| 低换手（多因子） | 3-5 天给时间 | 偶发（策略死扛时兜底） |

> **设计意图**：高换手策略 Tier 1+2 通常自然收敛（持仓本就 1-2 天到期），Tier 3 几乎不触发；低换手策略 Tier 1+2 给充足时间，Tier 3 兜底防死扛。每级是独立事件，可 log 可复盘。

## 4. 状态机（Tier 升级流转）

```
                    BudgetChanged (delta<0)
                           │
                           ▼
                    ┌─────────────┐
                    │   PENDING   │  收到下调事件，待处理
                    └──────┬──────┘
                           │ 发送 FreezeNewPositions
                           ▼
                    ┌─────────────┐
                    │  TIER1_FROZEN│  封锁新仓，现有仓位不动
                    └──────┬──────┘
                           │ 发送 RebalanceRequest
                           ▼
                    ┌─────────────┐
            ┌───────│  TIER2_REBAL │  策略自主 rebalance（convergence_window 内）
            │       └──────┬──────┘
            │              │
     ┌──────┴──────┐       └──────┬──────┐
     │             │               │      │
     ▼             ▼               ▼      ▼
 StrategyRebalanced           超时/违例
 (成功)                       │
     │                        ▼
     │                  ┌───────────┐
     │                  │ TIER3_TRIM│  强制裁剪（dumb but safe）
     │                  └──────┬────┘
     │                         │
     └────────────┬────────────┘
                  ▼
           ┌─────────────┐
           │   COMPLETED  │  BudgetChangeHandled 事件
           └─────────────┘
```

> **状态持久化**：Tier 升级状态持久化（防重启丢失），支持跨交易日恢复（低换手策略 convergence_window 可能跨日）。

## 5. 关键不变量 (INVARIANTS)

- budget 下调**必经三级升级**（Tier 1 → Tier 2 → Tier 3），不跳级（除 firm 风险违例直接 Tier 3）
- Tier 1 触发后 StrategyBook **不得开任何新仓**（frozen=True 期间）
- Tier 2 策略返回的 TargetPortfolio **total_weight ≤ new_budget**（策略不能说"我不卖"）
- Tier 3 裁剪后 strategy_i 的 total_weight **= new_budget**（强制达标）
- Tier 3 **绕过策略自主权**（直接生成裁剪指令，不经 rebalance_to_budget）
- budget 上调**不经三级升级**（直接抬高上限，自然部署）
- convergence_window 超时**必须升级 Tier 3**（不允许无限等待）
- 每级升级是**独立事件**，可 log 可复盘（TierEscalation 事件链）
- Tier 状态持久化（跨交易日可恢复）
- 现金拖累在上调时**可接受**（现金也是一种仓位）

## 6. 错误契约

- `BudgetChangeError` (ZA-POS-0040): BudgetChanged 事件格式非法 / old_budget 缺失 / strategy_id 不匹配
- `FreezeFailedError` (ZA-POS-0041): Tier 1 封锁指令下发失败（StrategyBook 未响应 frozen 确认）
- `RebalanceTimeoutError` (ZA-POS-0042): Tier 2 convergence_window 超时（升级 Tier 3 的触发条件，非致命）
- `ForcedTrimError` (ZA-POS-0043): Tier 3 强裁失败（PositionSnapshot 缺失 / cut_ratio 计算异常 / 执行层拒绝）
- `StateRecoveryError` (ZA-POS-0044): 跨日恢复状态机异常（持久化数据损坏 / 状态不一致）

## 7. 测试规划

### Phase 1 测试 (~28)
- 触发判定：上调不处理 / 下调启动三级 / delta=0 边界
- Tier 1：FreezeNewPositions 下发 / frozen 期间新仓被拒 / 现有仓位不动
- Tier 2：RebalanceRequest 下发 / 策略自主砍仓 / convergence_window 内完成 / 返回 total_weight ≤ new_budget
- Tier 3：超时升级 / firm 风险违例直接 Tier 3 / 等比裁剪 cut_ratio 计算 / 绕过策略自主权
- 状态机：PENDING→TIER1→TIER2→COMPLETED / TIER2→TIER3→COMPLETED 全路径
- convergence_window：打板 1-2天 / 事件驱动 2-3天 / 多因子 3-5天 边界
- budget 上调：直接抬高上限 / 解冻 / 现金拖累可接受
- 事件链：TierEscalation 完整记录 / BudgetChangeHandled 归因
- 降级：PositionSnapshot 缺失时 Tier 3 用估算

### Phase 2 测试 (~12)
- 跨日恢复：状态持久化 / 重启后恢复 TIER2_REBAL / 超时跨日计算
- 多策略并发：多个 BudgetChanged 并发处理 / 策略间隔离
- 联调：与 RegimeMetaAllocator + StrategyBook + FirmRiskAggregator 全链路

## 8. 依赖

### 8.1 已就绪 (Phase 1 可用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- ConvergenceWindows 配置（config 驱动，per-strategy）

### 8.2 待建 (前置)
- RegimeMetaAllocator (MOD-PA-007, BudgetChanged 事件) — ❌ 待建（blueprint 已完成）
- StrategyBook (MOD-POS-020, rebalance_to_budget 接口 + StrategyRebalanced 事件) — ❌ 待建（blueprint 已完成）
- FirmRiskAggregator (MOD-POS-021, Tier 3 强裁执行 + 风险违例反馈) — ❌ 待建（blueprint 已完成）

### 8.3 消费者
- StrategyBook (MOD-POS-020)：接收 FreezeNewPositions / RebalanceRequest 指令
- FirmRiskAggregator (MOD-POS-021) / D-EX-CORE：接收 ForcedTrim 强裁指令
- RegimeMetaAllocator (MOD-PA-007)：接收 BudgetChangeHandled 反馈
- Trader + 归因系统：接收 TierEscalation 事件链

### 8.4 降级策略

| 上游缺失 | 降级模式 | 影响 |
|---------|---------|------|
| PositionSnapshot (Tier 3) | 用上次已知持仓估算 cut_ratio | 强裁精度降级 |
| StrategyBook rebalance 反馈 | Tier 2 无法确认完成 → 直接超时升级 Tier 3 | 跳过策略自主权 |
| 状态持久化 | 内存状态，重启丢失 → 全部策略重新 Tier 1 | 跨日恢复失效 |

## 9. 分阶段施工里程碑

### Phase 1: 三级升级 + 状态机（P0）

**目标**：budget 下调三级升级完整落地 + 状态机 + 事件链

**范围**：
- 触发判定（上调不处理 / 下调启动三级）
- Tier 1 封锁新仓（FreezeNewPositions）
- Tier 2 策略自主 rebalance（RebalanceRequest + convergence_window 超时）
- Tier 3 强制裁剪（ForcedTrim 等比裁剪 + 绕过策略自主权）
- 状态机（PENDING→TIER1→TIER2→COMPLETED / TIER2→TIER3→COMPLETED）
- budget 上调处理（直接抬高 + 解冻）
- 事件链（TierEscalation + BudgetChangeHandled）
- 降级模式（PositionSnapshot 缺失估算）

**不包含**：跨日恢复、多策略并发优化

**预计**：~350 行代码 + ~28 测试

### Phase 2: 跨日恢复 + 多策略并发（依赖上游联调）

**前置**：RegimeMetaAllocator + StrategyBook + FirmRiskAggregator 就绪

**范围**：
- 状态持久化（跨交易日恢复）
- 多策略并发 BudgetChanged 处理（策略间隔离）
- 全链路联调（RegimeMetaAllocator → Handler → StrategyBook → FirmRiskAggregator）
- convergence_window 校准（首批策略换手率数据，30_multi_strategy_concurrency §6.4）

### Phase 3: 生产化（待 Phase 1/2 验证后）

- 性能 SLA 验证（Tier 1 响应 <100ms / Tier 3 裁剪指令 <500ms）
- depgraph build_status → generated, design_maturity → production

## 10. 设计决策记录

| 决策 | 理由 |
|------|------|
| 三级升级而非直接强砍 | 30_multi_strategy_concurrency §2.4：尊重策略自主权 + 避免随机时刻强制卖出高成本 |
| Tier 1 立即封锁新仓 | budget 下调第一时间止血，防策略用旧 budget 惯性继续开仓 |
| Tier 2 策略自主选砍哪些 | 策略最清楚自己哪个仓位最不自信；避免错砍即将盈利的仓位 |
| Tier 3 等比裁剪（dumb but safe） | 策略死扛时 firm 层兜底；按比例不挑仓位，保证 budget 约束达标 |
| Tier 3 绕过策略自主权 | 策略不能说"我不卖"——budget 是硬约束（30_multi_strategy_concurrency §2.4） |
| 只处理下调（上调不介入） | 上调简单（抬高上限+自然部署），现金拖累可接受 |
| convergence_window 按换手率差异化 | 高换手自然快收敛，低换手给充足时间；30_multi_strategy_concurrency §6.4 |
| 状态持久化（跨日恢复） | 低换手策略 convergence_window 可能跨日，防重启丢失状态 |
| 每级独立事件可 log 可复盘 | 归因清晰：能追溯"哪个策略何时被冻结/自主/强裁" |
| firm 风险违例直接 Tier 3 | 风控违例不等 convergence_window，立即强裁（保命优先） |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-022`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-022` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-022` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-022 | MOD-POS-022 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 11. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 11.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 11.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §11（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


