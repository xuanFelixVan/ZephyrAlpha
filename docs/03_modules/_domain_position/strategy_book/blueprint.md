---
module_id: MOD-POS-020
title: "独立策略账本蓝图 — 选股+粗仓位+独立风控+budget适配（A模型分层·方案A）"
doc_type: blueprint
status: Active
version: "0.1.2"
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

# MOD-POS-020 StrategyBook — 独立策略账本 蓝图

> **module_id**: MOD-POS-020 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: design | **建设标记**: 🟡 待施工
> **SSoT**: depgraph MOD-POS-020 | **设计真源**: [30_multi_strategy_concurrency.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.2（三个核心模块）、§2.4（权重变动流程）、§2.5（Drawdown Protocol）
> **regime 依赖**: [10_regime_detector_spec.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md) §5（Shrinkage = ConfidenceSignal × RiskSignal，由 RegimeMetaAllocator 施加）

## 1. 定位

独立策略账本——A 模型（[30_multi_strategy_concurrency](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §2.1）的核心实体。每个策略是一个自洽的 StrategyBook，自带选股 + 粗仓位 + 独立风控，输出 `target_portfolio`（标的 + 目标权重）。

属 **B 类核心业务模块**（多源融合 + 策略逻辑 + 风控自洽），策略 alpha 逻辑为 C 类可插拔策略实现。

### 1.1 分层边界（方案 A，2026-08-06 用户裁定）

> **架构决策**：仓位决策分两层——StrategyBook 做"策略层 alpha"（选股 + 粗仓位），MOD-POS-001 做"组合层风险裁决"（Kelly + 13 约束）。
> **第一性原理**：组合级约束（单票上限跨策略叠加）天然在 firm 层，单个 StrategyBook 无法计算；Kelly 需密度预测（重资源），不宜每策略重复嵌入；风险合规与 alpha 解耦防归因纠缠。
> **开源印证**：[Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book) sleeve(alpha) + risk-parity-throttle(firm risk) 分层，OOS Sharpe +1.43。

| 层 | 模块 | 职责 | 输出 |
|---|---|---|---|
| **策略层** | **StrategyBook (本模块)** | 选股 + 粗仓位（等权/risk parity，**不用 Kelly，不用 MVO**） | `target_portfolio`（标的+目标权重） |
| 组合汇总层 | FirmRiskAggregator (MOD-POS-021) | 求和 + 组合级硬裁剪（单票上限 8%/行业上限/总仓位） | `firm_target_portfolio` |
| 组合裁决层 | MOD-POS-001 position_sizing_engine | Kelly + 13 约束 + 市场状态上限 + 四轨融合 | `PositionPlan` → 下单 |

**数据流**：`StrategyBook → FirmRiskAggregator → MOD-POS-001 → 下单`

> ⚠️ **需回写 30_multi_strategy_concurrency §2.2**：原文"StrategyBook 自带仓位算法（Kelly / risk parity / 简单等权）"修正为"自带粗仓位（等权/risk parity），Kelly 精裁决由 firm 层 MOD-POS-001 承担"。本 blueprint 落地后执行回写。

### 1.2 不做什么

- **不做 Kelly 精裁**（由 MOD-POS-001 firm 层做）
- **不做组合级约束**（单票上限跨策略叠加，由 FirmRiskAggregator 做）
- **不做 MVO 协方差优化**（30_multi_strategy_concurrency §3.1 拒绝）
- **不知道市场态**（30_multi_strategy_concurrency §2.2：市场态是 meta 层的事，StrategyBook 只收到 budget 数字）
- **不执行交易**（由 D-EX-CORE 承接）

## 2. 输入 / 输出

### 2.1 输入

| 方向 | 内容 | 契约/事件 | 来源 | 就绪 |
|------|------|-----------|------|:----:|
| 策略 | AlphaSignal（选股信号，策略 specific） | CTR-POS-020-A | 策略实现（继承 StrategyBook） | 🟡 待实现 |
| 资金 | BudgetAllocation（资金预算占比，floor 5%~cap 40%） | CTR-PA-007 | RegimeMetaAllocator (MOD-PA-007) | ❌ 待建（Phase 1 用等权占位） |
| 反馈 | PerformanceScore（自身 60 日滚动 Sharpe，[0.5,1.5]） | CTR-POS-020-P | 自身净值计算 | 🟡 Phase 2 |
| 持仓 | PositionSnapshot（当前持仓快照） | CTR-006 | D-EX-CORE | ⚠️ 部分 |
| 风控 | DrawdownStatus（单策略回撤状态） | CTR-POS-008 | drawdown_controller (POS-008) | ✅ stable |
| 公共 | CapitalCurveLimit（资金曲线缩放） | — | POS-007 | ✅ stable |

### 2.2 输出

| 方向 | 内容 | 契约/事件 | 去往 |
|------|------|-----------|------|
| 输出 | TargetPortfolio（标的+目标权重，**粗仓位未经 Kelly**） | CTR-POS-020 | FirmRiskAggregator (MOD-POS-021) |
| 事件 | StrategyRebalanced（策略再平衡完成） | E-POS-20 | RegimeMetaAllocator（PerformanceScore 反馈） |
| 事件 | StrategyDrawdownAlert（单策略回撤触发） | E-POS-21 | FirmRiskAggregator + Trader |
| 事件 | StrategyKillSwitch（单策略熔断） | E-POS-22 | FirmRiskAggregator（强制隔离） |

### 2.3 TargetPortfolio 定义 (CTR-POS-020)

> **与 MOD-POS-001 PositionPlan 的区别**：TargetPortfolio 是"策略想买什么"（粗仓位，权重和 ≤ budget），PositionPlan 是"组合最终能买什么"（经 Kelly + 13 约束裁决）。两者是粗→精的上下游。

| 字段 | 类型 | 说明 |
|------|------|------|
| strategy_id | str | 策略唯一标识 |
| positions | dict[str, TargetWeight] | {symbol: {target_weight, reason, confidence}} |
| total_weight | float | 权重和（≤ budget，未满部分为现金） |
| budget | float | 当前资金预算占比（来自 RegimeMetaAllocator） |
| cash_ratio | float | 现金比例 = budget − total_weight |
| sizing_method | str | 粗仓位方法（"equal_weight" / "risk_parity" / "custom"） |
| created_at | datetime | 创建时间 |
| idempotency_key | str | `f"{strategy_id}:{trade_date}:{hash(sorted(positions))[:8]}"` |
| schema_version | str | "1.0" |

## 3. 核心规则

### 3.1 选股（策略 specific，可插拔）

StrategyBook 是**容器**，具体选股逻辑由策略实现注入：

```python
class StrategyBook(ABC):
    @abstractmethod
    def generate_alpha_signals(self, snapshot: PositionSnapshot) -> list[AlphaSignal]:
        """策略自己的选股逻辑——返回候选标的+信号强度"""

    @abstractmethod
    def sizing_method(self) -> str:
        """粗仓位方法：equal_weight / risk_parity / custom"""
```

首批 3 个策略候选（30_multi_strategy_concurrency §6.1 待人决策）：打板 / 多因子 / 事件驱动。

### 3.2 粗仓位（不用 Kelly，不用 MVO）

| 方法 | 逻辑 | 适用 |
|------|------|------|
| equal_weight | 每个选中标的等权 `1/N × budget` | 默认，冷启动 |
| risk_parity | 按波动率倒数分配（高波动少配） | 多因子策略 |
| custom | 策略自定义简单比例 | 打板（按连板高度/情绪梯度） |

**硬约束**：
- `total_weight ≤ budget`（不超分配，未满为现金）
- 单标的 `target_weight ≤ 5%`（策略内上限，组合级 8% 由 FirmRiskAggregator 裁剪）
- **不计算 Kelly**（f* 留给 MOD-POS-001）

### 3.3 Budget 适配（30_multi_strategy_concurrency §2.4 三级升级）

budget 是硬约束（来自 meta 层），策略自主权在"怎么适应"，不在"要不要适应"。

```python
def rebalance_to_budget(self, new_budget: float) -> TargetPortfolio:
    """策略必须实现——返回适配新 budget 的 target_portfolio，不能说'我不卖'"""
```

| 级别 | 触发 | 动作 | 性质 |
|------|------|------|------|
| Tier 1 | budget 下调瞬间 | 封锁新仓（现有仓位不动） | 立即，被动 |
| Tier 2 | Tier 1 后 | `rebalance_to_budget`——策略自选砍最不自信的仓位 | 建议，策略自主 |
| Tier 3 | Tier 2 窗口超时 / firm 风险违例 | 按比例强行裁剪所有仓位（dumb but safe） | 强制，firm 层（BudgetChangeHandler MOD-POS-022） |

- convergence_window（30_multi_strategy_concurrency §6.4 待人决策）：打板 1-2 天 / 多因子 3-5 天 / 事件驱动 2-3 天
- budget 上调：直接抬高上限，策略通过买入信号自然部署，现金拖累可接受

### 3.4 独立风控（30_multi_strategy_concurrency §2.5 Drawdown Protocol）

> **用户裁定**（30_multi_strategy_concurrency §2.5）：回撤是沉没成本，不进 regime RiskSignal，但触发账户级风险节流。单策略回撤=策略问题→该策略独立收缩。

**四级回撤阈值**（复用 POS-008 drawdown_controller）：

| 级别 | 回撤阈值 | 动作 |
|------|---------|------|
| Level 1 | > 8% | 降低新仓风险敞口至 75% |
| Level 2 | > 15% | 仓位缩减至 75%，停开新仓 |
| Level 3 | > 20% | 停止所有新开仓，review |
| Level 4 | > 25% | Kill Switch：关闭所有仓位，强制休息 5 天 |

**恢复机制**（ARKA 2026 共识：不自动恢复）：
- 回撤从峰值恢复 50% → 解除停仓，风险敞口仍降 50%
- 创新高 → 恢复正常风险敞口
- Level 4 触发 → 强制休息 5 交易日，需 explicit re-authorization

### 3.5 灰度发布（新策略冷启动）

| 阶段 | budget 占比 | 持续 |
|------|------------|------|
| 观察 | 5% | 5 交易日 |
| 灰度 1 | 20% | 10 交易日 |
| 灰度 2 | 50% | 20 交易日 |
| 全量 | 100% | — |

> 冷启动期 PerformanceScore 不参与 RegimeMetaAllocator 分配（30_multi_strategy_concurrency §2.2：新策略冷启动只用 Base_i）。

## 4. 关键不变量 (INVARIANTS)

- `TargetPortfolio.total_weight ≤ budget`（不超分配）
- 单标的 `target_weight ≤ 5%`（策略内上限）
- `rebalance_to_budget` 必须返回适配新 budget 的组合（**策略不能拒绝**）
- 单策略回撤 > 25% → Kill Switch 强制清仓 + 休息 5 天
- Kill Switch 触发即执行，不允许人工覆盖延迟（30_multi_strategy_concurrency §2.5.5）
- TargetPortfolio **不含 Kelly 裁决结果**（粗仓位，精裁决由 MOD-POS-001 做）
- TargetPortfolio 幂等（idempotency_key 防重复决策）
- 灰度期策略 budget ≤ 灰度阶段上限

## 5. 错误契约

- `InvalidBudgetError` (ZA-POS-0020): budget 越界（<0 或 >1）、budget 突变超 floor/cap 范围
- `StrategyDrawdownKillError` (ZA-POS-0021): 触发 Level 4 Kill Switch，策略强制隔离
- `RebalanceTimeoutError` (ZA-POS-0022): Tier 2 convergence_window 超时，升级 Tier 3
- `AlphaSignalError` (ZA-POS-0023): 选股信号异常（空候选 / 信号强度非法）
- `SizingError` (ZA-POS-0024): 粗仓位计算异常（risk_parity 波动率为零 / custom 逻辑异常）

## 6. 测试规划

### Phase 1 测试 (~30)
- 选股接口：AlphaSignal 生成 / 空候选处理 / 信号强度边界
- 粗仓位：equal_weight 归一 / risk_parity 波动率倒数 / total_weight ≤ budget / 单标的 5% 上限
- budget 适配：rebalance_to_budget 上调/下调 / Tier 1 封锁新仓 / Tier 2 自主砍仓 / Tier 3 强制裁剪
- 独立风控：4 级回撤阈值边界 / Kill Switch 执行 / 恢复机制（50% 回补 / 创新高 / 强制休息）
- 灰度发布：5%→20%→50%→100% 阶段晋升 / 冷启动期 PerformanceScore 不参与分配
- TargetPortfolio 输出：字段完整性 / 幂等性 / sizing_method 标注

### Phase 2 测试 (~15)
- 接入 RegimeMetaAllocator 动态 budget / PerformanceScore 反馈
- 多策略同标的自然叠加（验证粗仓位层不冲突，叠加在 FirmRiskAggregator 做）

## 7. 依赖

### 7.1 已就绪 (Phase 1 可用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `zephyr.position.core.drawdown_controller` (POS-008, DrawdownStatus) — stable
- `zephyr.position.core.capital_curve_manager` (POS-007, CapitalCurveLimit) — stable

### 7.2 待建 (Phase 2 前置)
- RegimeMetaAllocator (MOD-PA-007, BudgetAllocation) — ❌ 待建（Phase 1 用等权占位）
- regime 检测器 (MOD-???, Shrinkage 因子) — ❌ 待建，域未定
- FirmRiskAggregator (MOD-POS-021) — ❌ 待建（本模块输出消费者）
- BudgetChangeHandler (MOD-POS-022) — ❌ 待建（Tier 3 强制裁剪执行者）

### 7.3 消费者
- FirmRiskAggregator (MOD-POS-021)：消费 TargetPortfolio，求和+组合级裁剪
- MOD-POS-001 position_sizing_engine：消费 firm_target_portfolio，Kelly+13 约束精裁决
- RegimeMetaAllocator (MOD-PA-007)：消费 StrategyRebalanced 事件 + PerformanceScore 反馈

### 7.4 降级策略

| 上游缺失 | 降级模式 | 影响 |
|---------|---------|------|
| RegimeMetaAllocator (budget) | 等权分配（1/N），Phase 1 默认 | 跳过 regime 节流 |
| PositionSnapshot | 跳过持仓检查，按全现金假设 | 粗仓位可能不准 |
| drawdown_controller | 跳过回撤风控（标记 degraded） | ⚠️ 风控降级，需告警 |

## 8. 分阶段施工里程碑

### Phase 1: 容器 + 粗仓位 + 独立风控（P0，不依赖未建上游）

**目标**：StrategyBook 容器可运行，等权粗仓位 + 单策略回撤风控 + budget 适配，budget 用等权占位

**范围**：
- StrategyBook 抽象基类 + generate_alpha_signals / sizing_method 接口
- 粗仓位引擎（equal_weight / risk_parity）
- rebalance_to_budget 三级升级（Tier 1 封锁 / Tier 2 自主 / Tier 3 占位）
- 单策略 Drawdown Protocol（4 级阈值 + Kill Switch + 恢复机制）
- 灰度发布状态机（5%→20%→50%→100%）
- TargetPortfolio 输出（CTR-POS-020）
- 降级模式（budget 等权占位）

**不包含**：动态 budget（RegimeMetaAllocator）、PerformanceScore 反馈、多策略联调

**预计**：~400 行代码 + ~30 测试

### Phase 2: 动态 budget + PerformanceScore（依赖 regime 链就绪）

**前置**：RegimeMetaAllocator (MOD-PA-007) + regime 检测器就绪

**范围**：
- 接入 RegimeMetaAllocator 动态 budget（Shrinkage 节流）
- PerformanceScore 计算（60 日滚动 Sharpe，[0.5,1.5] 映射）
- StrategyRebalanced 事件反馈
- 多策略同标的自然叠加验证（在 FirmRiskAggregator 侧）

### Phase 3: 生产化（待 Phase 1/2 验证后）

- 全约束集成测试（与 FirmRiskAggregator + MOD-POS-001 联调）
- 性能 SLA 验证（选股+粗仓位延迟 <50ms P50）
- depgraph build_status → generated, design_maturity → production

## 9. 设计决策记录

| 决策 | 理由 |
|------|------|
| 粗仓位不用 Kelly（方案 A 分层） | 组合级约束跨策略叠加天然在 firm 层；Kelly 需密度预测不宜每策略重复；风险合规与 alpha 解耦防归因纠缠；开源 Morwane 实证分层架构 Sharpe +1.43 |
| StrategyBook 是容器（策略可插拔） | 不同策略 alpha 逻辑差异大（打板/多因子/事件驱动），容器+继承避免 if-else 深渊 |
| budget 是硬约束（策略不能拒绝） | 30_multi_strategy_concurrency §2.4：策略自主权在"怎么适应"不在"要不要适应" |
| 单策略回撤独立收缩（不进 regime RiskSignal） | 30_multi_strategy_concurrency §2.5 用户裁定：回撤是沉没成本属账户风控，单策略回撤=策略问题 |
| 灰度发布 5%→20%→50%→100% | 新策略冷启动防失控，冷启动期 PerformanceScore 不参与分配 |
| TargetPortfolio 不含 Kelly | 与 MOD-POS-001 PositionPlan 粗→精分层，避免双重 Kelly |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-020`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-020` 的 3 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-020` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-020 | MOD-POS-020 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/position/test_cold_start_progression.py` | ✅ 已实现 | |

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


