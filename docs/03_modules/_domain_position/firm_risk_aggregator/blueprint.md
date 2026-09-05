---
module_id: MOD-POS-021
title: "Firm层风险聚合器蓝图 — 求和+硬上限裁剪+冲突净额（A模型·组合汇总层）"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
build_status: production
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

# MOD-POS-021 FirmRiskAggregator — Firm层风险聚合器 蓝图

> **module_id**: MOD-POS-021 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: design | **建设标记**: 🟡 待施工
> **SSoT**: depgraph MOD-POS-021 | **设计真源**: [30_multi_strategy_concurrency.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.2（FirmRiskAggregator）、§2.3（自然叠加）、§3.1（拒绝 MVO）
> **上游契约**: [StrategyBook blueprint](../strategy_book/blueprint.md) MOD-POS-020 §2.3 TargetPortfolio (CTR-POS-020)

## 1. 定位

Firm 层风险聚合器——A 模型（[30_multi_strategy_concurrency](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.2）的组合汇总层。消费所有 StrategyBook 的 `TargetPortfolio`，**按标的求和（自然叠加）+ 组合级硬上限裁剪 + 冲突净额处理**，产出 `FirmTargetPortfolio` 交由 MOD-POS-001 精裁决。

属 **A 类基础设施**（求和+裁剪+净额，逻辑明确无优化），O(N) 复杂度（N=策略数×标的数），**不做 MVO，不做协方差估计**。

### 1.1 分层边界（方案 A，承接 StrategyBook §1.1）

| 层 | 模块 | 职责 | 输出 |
|---|---|---|---|
| 策略层 | StrategyBook (MOD-POS-020) | 选股 + 粗仓位 | `TargetPortfolio`（单策略，粗仓位） |
| **组合汇总层** | **FirmRiskAggregator (本模块)** | **求和 + 组合级硬裁剪 + 冲突净额** | **`FirmTargetPortfolio`（汇总+裁剪，仍粗仓位）** |
| 组合裁决层 | MOD-POS-001 position_sizing_engine | Kelly + 13 约束 + 市场状态上限 | `PositionPlan` → 下单 |

**数据流**：`StrategyBook(×N) → FirmRiskAggregator → MOD-POS-001 → 下单`

> 本模块是"粗→精"分层的中转站：上游各策略粗仓位自然叠加，本模块做组合级硬裁剪（防多策略叠加集中），下游 MOD-POS-001 做 Kelly 精裁决。两层裁剪不冗余——本模块管"跨策略叠加集中"，MOD-POS-001 管"标的级 Kelly 合规"。

### 1.2 核心哲学：用加法替代优化器（30_multi_strategy_concurrency §2.3）

> **自然叠加**：多策略选到同一只票时，仓位自然叠加（S1 给 3% + S2 给 5% = 8%）。这等价于一个永远稳定的等权 risk-budget 优化器，无需调投票权重，无需估协方差。这是 A 模型最被低估的优点——**用加法替代优化器，O(N) 替代 O(N²)**。

### 1.3 不做什么

- **不做 MVO / 协方差估计**（30_multi_strategy_concurrency §3.1 拒绝：协方差估计是研究课题，放大噪声，归因纠缠）
- **不做 Kelly**（方案 A，Kelly 归 MOD-POS-001）
- **不做选股**（选股在 StrategyBook）
- **不做标的级精裁**（VaR/参与率/退出时间归 MOD-POS-001）
- **不做跨策略投票/优先级仲裁**（30_multi_strategy_concurrency §3.2 拒绝 Model D；A 模型下自然叠加替代投票）

## 2. 输入 / 输出

### 2.1 输入

| 方向 | 内容 | 契约/事件 | 来源 | 就绪 |
|------|------|-----------|------|:----:|
| 核心输入 | TargetPortfolio[]（各策略粗仓位组合，N 个） | CTR-POS-020 | StrategyBook (MOD-POS-020) | ❌ 待建 |
| 硬约束 | FirmRiskLimits（单票/行业/总仓位上限） | CTR-POS-021-L | 配置 + D-RISK | ✅ config |
| 持仓 | PositionSnapshot（当前持仓，冲突净额计算用） | CTR-006 | D-EX-CORE | ⚠️ 部分 |
| 事件 | StrategyKillSwitch（某策略熔断，排除其贡献） | E-POS-22 | StrategyBook | ❌ 待建 |

### 2.2 输出

| 方向 | 内容 | 契约/事件 | 去往 |
|------|------|-----------|------|
| 输出 | FirmTargetPortfolio（汇总+裁剪后组合） | CTR-POS-021 | MOD-POS-001 position_sizing_engine |
| 事件 | FirmAggregated（聚合完成） | E-POS-30 | MOD-POS-001 + Trader（归因用） |
| 事件 | FirmConstraintHit（硬上限触发裁剪） | E-POS-31 | Trader + RegimeMetaAllocator（风控反馈） |

### 2.3 FirmTargetPortfolio 定义 (CTR-POS-021)

> **与 TargetPortfolio 的区别**：TargetPortfolio 是单策略粗仓位；FirmTargetPortfolio 是所有策略汇总+裁剪后的组合级粗仓位，携带各策略贡献明细（归因用）。两者都未经 Kelly，交由 MOD-POS-001 精裁决。

| 字段 | 类型 | 说明 |
|------|------|------|
| firm_positions | dict[str, FirmTarget] | {symbol: {target_weight, contributions, cut_ratio}} |
| total_exposure | float | 总暴露（所有标的 target_weight 之和） |
| total_budget | float | 所有策略 budget 之和（组合资金上限） |
| cash_ratio | float | 现金比例 = total_budget − total_exposure |
| constraint_checks | dict | 各硬约束检查结果（单票/行业/总仓位，含是否触发裁剪） |
| conflicts_resolved | list[ConflictRecord] | 冲突标的净额处理记录（归因用） |
| degraded | bool | 是否降级模式 |
| created_at | datetime | 创建时间 |
| idempotency_key | str | `f"firm:{trade_date}:{hash(sorted(firm_positions))[:8]}"` |
| schema_version | str | "1.0" |

**FirmTarget 子结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| target_weight | float | 合并+裁剪后权重 |
| contributions | dict[str, float] | {strategy_id: 原始贡献权重}（归因用，裁剪前） |
| cut_ratio | float | 裁剪比例（1.0=未裁剪，0.8=削了20%） |
| conflict_type | str \| None | "none" / "buy_sell" / "overlap_overflow" |

## 3. 核心规则

### 3.1 求和（自然叠加，30_multi_strategy_concurrency §2.3）

按标的合并所有 StrategyBook 的 TargetPortfolio：

```
对每个 symbol s:
    firm_positions[s].target_weight = Σ_i TargetPortfolio_i.positions[s].target_weight
    firm_positions[s].contributions = { strategy_i: TargetPortfolio_i.positions[s].target_weight }
```

**关键**：这是**加法**，不是投票。S1 给 3% + S2 给 5% = 8%，不需要投票权重或优先级仲裁。多策略共识→大仓位是自然涌现的，无需 meta-参数。

### 3.2 组合级硬上限裁剪（三类，30_multi_strategy_concurrency §2.2 步骤 2-3）

> **与 MOD-POS-001 裁剪的区别**：本模块管"跨策略叠加集中"（组合级），MOD-POS-001 管"标的级 Kelly 合规"。本模块裁剪在 Kelly 前，MOD-POS-001 裁剪在 Kelly 后。

#### 3.2.1 单票硬上限裁剪（防多策略叠加集中）

| 约束 | 触发 | 动作 | 默认阈值 |
|------|------|------|---------|
| 单票上限 | symbol 叠加后 > 8% | **等比削减**各策略贡献 | 8%（config 可调） |

**等比削减逻辑**（默认，O(N) 简单）：
```
cut_ratio = 单票上限 / 叠加后权重
对每个 strategy_i: contributions[i] *= cut_ratio
target_weight = 单票上限
```

> **为何等比而非优先级**：30_multi_strategy_concurrency §3.2 拒绝 Model D 投票权重（meta-参数是技术债）。等比削减无需优先级配置，O(N) 简单可审计。如未来需优先级，config 可切换 `cut_mode: "pro_rata" | "priority"`。

#### 3.2.2 行业/板块硬约束

| 约束 | 触发 | 动作 | 默认阈值 |
|------|------|------|---------|
| 单行业上限 | 行业占比 > 30% | 等比削减该行业内所有标的 | 30%（config 可调） |
| 行业分散度 | 持仓行业数 < 3 | 预警（不强制裁剪） | 3 |

#### 3.2.3 总仓位硬约束

| 约束 | 触发 | 动作 | 默认阈值 |
|------|------|------|---------|
| 总暴露上限 | total_exposure > total_budget | 等比削减所有标的 | total_budget |
| 总暴露上限 | total_exposure > 市场状态上限 | 等比削减至市场状态上限 | 来自 regime（Phase 2） |

> Phase 1 市场状态上限用降级默认（30_multi_strategy_concurrency §2.2 置信度<60%→0.3）；Phase 2 接入 regime 检测器的灰度概率。

### 3.3 冲突标的净额处理（30_multi_strategy_concurrency §2.2 步骤 4）

> **A 模型下冲突罕见**（30_multi_strategy_concurrency §7.3：§16 的 31 条跨策略冲突仲裁大部分消失），但仍需处理同标的一买一卖的净额。

| 冲突类型 | 场景 | 处理 | 记录 |
|---------|------|------|------|
| buy_sell | S1 买入 symbol A，S2 卖出 symbol A（减仓） | 按净额：net = buy_weight − sell_weight | ConflictRecord |
| overlap_overflow | 多策略同向叠加超限 | §3.2.1 等比削减 | cut_ratio |

**净额计算**：
```
net_weight = Σ(买入贡献) − Σ(卖出贡献)
if net_weight > 0: 保留为 target_weight（买入净额）
if net_weight ≤ 0: 标记为清仓/减仓（target_weight=0 或负值转卖出）
```

> A 股不能做空，net_weight ≤ 0 时 target_weight=0（清仓），不产生空头。

### 3.4 裁剪执行顺序

```
[1] 求和（自然叠加）→ 得到原始 firm_positions
    │
[2] 冲突净额处理（buy_sell 净额）→ 更新 firm_positions
    │
[3] 单票硬上限裁剪（>8% 等比削减）→ 更新 contributions + cut_ratio
    │
[4] 行业硬约束裁剪（>30% 等比削减）→ 可能触发连锁（行业裁剪后单票又超限？否，只减不增）
    │
[5] 总仓位硬约束裁剪（>total_budget 等比削减）→ 最终 firm_positions
    │
[6] 输出 FirmTargetPortfolio（携带 contributions + constraint_checks + conflicts_resolved）
```

> **裁剪只减不增**：每步裁剪只会降低权重，不会升高，因此无需迭代收敛——单次顺序执行即可。这是 O(N) 复杂度的关键。

## 4. 关键不变量 (INVARIANTS)

- `FirmTargetPortfolio.firm_positions` 中每个 symbol 的 `target_weight ≤ 单票硬上限（8%）`
- `total_exposure ≤ total_budget`（不超总资金预算）
- 单行业占比 ≤ 行业上限（30%）
- **裁剪只减不增**（单次顺序执行，无需迭代收敛）
- **不做 Kelly**（粗仓位层，精裁决归 MOD-POS-001）
- **不做 MVO**（30_multi_strategy_concurrency §3.1 拒绝）
- O(N) 复杂度（N=策略数×标的数，无 O(N²) 协方差计算）
- FirmTargetPortfolio 幂等（idempotency_key 防重复聚合）
- Kill Switch 策略的贡献被排除（不参与求和）
- `contributions` 记录裁剪前原始贡献（归因可追溯）

## 5. 错误契约

- `InvalidAggregationInputError` (ZA-POS-0030): TargetPortfolio 列表为空、strategy_id 重复、权重非法（负值/NaN）
- `ConstraintViolationError` (ZA-POS-0031): 裁剪后仍超限（不变量被破坏，需告警——理论上不应发生，因裁剪只减不增）
- `ConflictResolutionError` (ZA-POS-0032): 冲突标的净额计算异常（贡献明细缺失/符号矛盾）
- `FirmRiskLimitError` (ZA-POS-0033): FirmRiskLimits 配置非法（上限≤0/单票>总仓位）

## 6. 测试规划

### Phase 1 测试 (~25)
- 求和：单策略/多策略同标的叠加/不同标的不交叉
- 单票裁剪：8% 边界/等比削减比例/多策略贡献裁剪后归因
- 总仓位裁剪：total_budget 边界/等比削减
- 冲突净额：buy_sell 净额/同向叠加/净额≤0 清仓
- 裁剪顺序：单票→行业→总仓位 链式/只减不增验证
- Kill Switch 排除：熔断策略贡献不参与求和
- FirmTargetPortfolio 输出：字段完整性/contributions 归因/幂等性
- 降级模式：PositionSnapshot 缺失时冲突处理降级

### Phase 2 测试 (~12)
- 行业约束：30% 边界/行业裁剪/行业分散度预警
- 市场状态上限：接入 regime 灰度概率后的总仓位裁剪
- 归因联调：contributions + cut_ratio + conflicts_resolved 完整归因链

## 7. 依赖

### 7.1 已就绪 (Phase 1 可用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- FirmRiskLimits 配置（config 驱动，单票/行业/总仓位阈值）

### 7.2 待建 (前置)
- StrategyBook (MOD-POS-020, TargetPortfolio) — ❌ 待建（本模块核心输入，blueprint 已完成）
- MOD-POS-001 position_sizing_engine 接口适配 — ⚠️ 需调整输入契约（从 D-PF-CORE TargetPortfolio → FirmTargetPortfolio）

### 7.3 消费者
- MOD-POS-001 position_sizing_engine：消费 FirmTargetPortfolio，Kelly + 13 约束精裁决
- RegimeMetaAllocator (MOD-PA-007)：消费 FirmConstraintHit 事件（风控反馈）
- Trader/归因系统：消费 FirmAggregated 事件 + contributions 归因

### 7.4 降级策略

| 上游缺失 | 降级模式 | 影响 |
|---------|---------|------|
| 部分 StrategyBook 缺失 | 仅聚合可用策略，标记 degraded | 组合不完整 |
| PositionSnapshot | 冲突净额按目标权重计算（不扣除已有持仓） | 冲突处理精度降级 |
| FirmRiskLimits 配置 | 使用硬编码默认（8%/30%/total_budget） | 无法动态调参 |

## 8. 分阶段施工里程碑

### Phase 1: 求和 + 单票/总仓位裁剪 + 冲突净额（P0）

**目标**：多策略 TargetPortfolio 求和 + 硬裁剪 + 冲突净额，输出 FirmTargetPortfolio

**范围**：
- 求和（自然叠加，§3.1）
- 单票硬上限裁剪（等比削减，§3.2.1）
- 总仓位硬约束裁剪（§3.2.3，市场状态用降级默认）
- 冲突标的净额处理（§3.3）
- 裁剪执行顺序（§3.4，只减不增单次执行）
- Kill Switch 策略排除
- FirmTargetPortfolio 输出（CTR-POS-021，含 contributions 归因）
- 降级模式

**不包含**：行业约束、市场状态动态上限、优先级裁剪模式

**预计**：~350 行代码 + ~25 测试

### Phase 2: 行业约束 + 市场状态动态上限（依赖 regime 链）

**前置**：regime 检测器 + RegimeMetaAllocator 就绪

**范围**：
- 行业/板块硬约束裁剪（§3.2.2）
- 市场状态动态上限（接入 regime 灰度概率，替代降级默认）
- 行业分散度预警
- 归因联调（contributions + cut_ratio + conflicts_resolved 完整链）

### Phase 3: 生产化（待 Phase 1/2 验证后）

- 与 MOD-POS-001 接口适配联调（FirmTargetPortfolio → PositionPlan）
- 性能 SLA 验证（聚合延迟 <20ms P50，N≤5 策略×≤30 标的）
- depgraph build_status → generated, design_maturity → production

## 9. 设计决策记录

| 决策 | 理由 |
|------|------|
| 用加法替代优化器（自然叠加） | 30_multi_strategy_concurrency §2.3：等价等权 risk-budget 优化器，O(N) 替代 O(N²)，无需协方差估计 |
| 等比削减（非优先级） | 30_multi_strategy_concurrency §3.2 拒绝 Model D 投票权重（meta-参数是技术债）；等比 O(N) 简单可审计；config 预留 priority 模式 |
| 裁剪只减不增（单次执行） | 每步裁剪只降权重不升，无需迭代收敛，保证 O(N) |
| 不做 Kelly（方案 A 分层） | Kelly 归 MOD-POS-001；本模块管"跨策略叠加集中"，MOD-POS-001 管"标的级 Kelly 合规"，两层不冗余 |
| 单票上限 8%（>MOD-POS-001 的 5%） | 本模块防"多策略叠加极端集中"（Kelly 前），MOD-POS-001 做"最终合规"（Kelly 后 5%）；8%>5% 合理，粗裁→精裁 |
| 冲突净额而非仲裁 | 30_multi_strategy_concurrency §7.3：A 模型下跨策略冲突大部分消失，简单净额即可，无需 31 条仲裁规则 |
| contributions 记录裁剪前原始贡献 | 归因可追溯：亏钱时能区分"哪个策略贡献了这只票""裁剪削了多少" |
| 不做 MVO/协方差 | 30_multi_strategy_concurrency §3.1：协方差估计是研究课题，A 股情绪周期切换时全错，归因纠缠 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-021`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-021` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-021` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-021 | MOD-POS-021 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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


