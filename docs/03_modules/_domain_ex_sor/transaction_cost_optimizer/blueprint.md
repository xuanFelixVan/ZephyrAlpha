---
module_id: MOD-EX_SOR_EXT-003
submodule_path: src/zephyr/ex_sor/services/transaction_cost_optimizer.py
title: "交易成本优化器蓝图 — A股全成本分解+优化建议"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
build_status: stable
ttl: permanent
layer: L2_domain
layer_name: execution_routing
functional_domain: execution
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P2
blueprint_level: module
responsibility_domain: 
---

# MOD-EX_SOR_EXT-003 Transaction Cost Optimizer — 交易成本优化器 蓝图

> **module_id**: MOD-EX_SOR_EXT-003 | **域**: D_EX_SOR | **层**: L2 执行路由
> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建(①) | **设计标签**: XS-EXT-03
> **SSoT**: depgraph MOD-EX_SOR_EXT-003 | **设计真源**: D:\临时工作区\依赖图\09-D-EX-SOR-执行路由域.md §2.1 XS-EXT-03 + §13.3 成本模型
> **代码**: src/zephyr/ex_sor/services/transaction_cost_optimizer.py | **测试**: tests/ex_sor/test_transaction_cost_optimizer.py

## 1. 定位

交易成本优化器——计算 A 股交易的全成本（显性 + 隐性），分解到六项组件，并给出优化建议。

大白话：每次买卖股票，除了看得见的佣金和印花税，还有看不见的"隐性成本"——比如你的大单把价格打跑了（冲击成本）、或者没成交的部分错过了行情（机会成本）。本模块把所有成本算清楚，告诉你哪项最贵、怎么省。

属 D-EX-SOR §2.1 补充子模块，P2 优先级，①可建。纯计算模块，Decimal 守恒。A 股费率真源遵循 2023-08-28 印花税降后标准。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 订单元信息 + 成交数量/均价 + 可选(decision_price 冲击基准 / unfilled_quantity 机会成本 / adv / volatility) |
| 输出 | TransactionCostResult（显性+隐性+总成本(bps) + 六项明细 breakdown）+ OptimizationAdvice |

## 3. 核心设计

### 3.1 A 股成本结构（FeeSchedule，可配置）

**显性成本（Explicit）——费率单位 bps（万分之一）：**

| 组件 | CostComponent | 收费方 | 默认费率 | 说明 |
|------|--------------|--------|---------|------|
| 佣金 | COMMISSION | 券商 | 3bps (0.03%) | 双边，最低 5 元 |
| 印花税 | STAMP_DUTY | 国税 | 5bps (0.05%) | **卖方单边**（2023-08-28 由 0.1% 降至 0.05%） |
| 过户费 | TRANSFER_FEE | 中登 | 0.1bps (0.001%) | 双边（2022-04-29 由 0.002% 降至 0.001%） |
| 监管费 | REGULATORY_FEE | 证监会 | 0.2bps (0.002%) | 双边 |

**隐性成本（Implicit）：**

| 组件 | CostComponent | 计算方式 |
|------|--------------|---------|
| 冲击成本 | IMPACT | 优先：`(成交价 - 决策价) × 数量`（BUY）/ `(决策价 - 成交价) × 数量`（SELL）；无决策价时用估计器 |
| 机会成本 | OPPORTUNITY | `未成交数量 × 决策价 × 0.001`（未成交部分错失收益估计） |

不变量：`总成本 = 显性 + 隐性`；`成本非负`（有利执行不算成本，impact<0 归零）。

### 3.2 冲击成本估计器（ImpactCostEstimator）

当无 decision_price 时，用线性冲击模型估计：

```
impact_bps = coeff × participation_rate × volatility_bps
impact_amount = notional × impact_bps / 10000
```

`LinearImpactEstimator`（coefficient=5.0 经验值：1% 参与率 × 2% 波动率 → ~10bps 冲击），理论对标 Kyle's lambda 简化版。
`ImpactCostEstimator` 为 Protocol 接口，可替换为平方根模型等。

### 3.3 优化建议（advise）

找最大成本驱动项，按组件给建议：

| 驱动项 | 建议 | action | 预估节省比 |
|--------|------|--------|-----------|
| COMMISSION | 与券商协商费率/增大交易量获取阶梯优惠 | negotiate_rate | 30% |
| STAMP_DUTY | 法定税率不可调，减少卖出频率（降换手率） | reduce_turnover | 0% |
| IMPACT | 使用 TWAP/VWAP 拆单或降低参与率 | use_algo_split | 40% |
| OPPORTUNITY | 提高成交率（放宽限价/更激进算法） | increase_fill_rate | 50% |
| TRANSFER_FEE/REGULATORY_FEE | 占比低，优化空间有限 | none | 0% |

`estimated_saving_bps = total_cost_bps × saving_ratio`

## 4. 数据结构

| 类型 | 角色 | 关键字段 |
|------|------|---------|
| `CostComponent` | 成本组件枚举 | COMMISSION/STAMP_DUTY/TRANSFER_FEE/REGULATORY_FEE/IMPACT/OPPORTUNITY |
| `FeeSchedule` | A 股费率表（frozen，可配置） | commission_rate_bps, commission_min, stamp_duty_rate_bps, transfer_fee_rate_bps, regulatory_fee_rate_bps |
| `TransactionCostBreakdown` | 单项成本明细 | component, amount, rate_bps, description |
| `TransactionCostResult` | 成本分析结果（frozen） | order_id, symbol, side, quantity, avg_price, notional, explicit_cost, implicit_cost, total_cost, total_cost_bps, breakdown[]; `.explicit_cost_bps`/`.implicit_cost_bps`/`.breakdown_for(comp)` |
| `OptimizationAdvice` | 优化建议 | primary_driver, recommendation, estimated_saving_bps, action |

## 5. 公开 API

```python
class TransactionCostOptimizer:
    def __init__(self, fee_schedule: FeeSchedule | None = None,
                 impact_estimator: ImpactCostEstimator | None = None) -> None
    def calculate(self, order_id, symbol, side, quantity, avg_price, *,
                  decision_price=None, unfilled_quantity=_ZERO,
                  adv=None, volatility=None, now=None) -> TransactionCostResult
    def advise(self, result: TransactionCostResult) -> OptimizationAdvice
    def get_history(self, symbol: str | None = None) -> list[TransactionCostResult]
    def clear_history(self) -> None
    @property
    def history(self) -> list[TransactionCostResult]
    @property
    def fee_schedule(self) -> FeeSchedule
```

## 6. 不变量与约束

| # | 不变量 | 来源 |
|---|--------|------|
| 1 | 成本非负（有利执行 impact<0 归零） | `[INVARIANTS]` |
| 2 | 显性 = 佣金+印花税+过户费+监管费 | `[INVARIANTS]` |
| 3 | 隐性 = 冲击+机会 | `[INVARIANTS]` |
| 4 | 总 = 显性 + 隐性 | `[INVARIANTS]` |
| 5 | 印花税仅卖方征收 | `[INVARIANTS]` + A 股规则 |
| 6 | 佣金有最低收费（默认 5 元） | FeeSchedule |
| 7 | 费率非负（FeeSchedule.__post_init__ 校验） | 输入校验 |
| 8 | Decimal 全程精度 | 项目铁律 |

## 7. 错误契约

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| `TransactionCostError` | ZA-XS-EXT-0003 | 通用基类 |
| `InvalidFeeScheduleError` | ZA-XS-EXT-0003-FS | 费率为负或最低佣金为负 |
| `InvalidCostInputError` | ZA-XS-EXT-0003-CI | 数量/价格≤0、未成交数量<0 |

## 8. 依赖关系

| 依赖模块 | 依赖类型 | 依赖内容 |
|---------|---------|---------|
| `zephyr.shared.contracts.enums.order_enums` | 必须 | OrderSide |
| `zephyr.shared.foundation.errors` | 必须 | ZephyrBaseError 基类 |

无外部服务依赖（纯计算）。

## 9. 消费者

| 消费者 | 消费方式 | 契约 |
|--------|---------|------|
| MOD-EX_SOR_EXT-002 (ExecutionQualityScorer) | 消费 TransactionCostResult → cost 维度评分 | EXT-002 `score_from_results` |
| MOD-EX-CORE (成本报告) | 消费成本明细生成 TCA 报告 | D-EX-CORE §13.3 |

## 10. 已实现代码路径

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/ex_sor/services/transaction_cost_optimizer.py` | ✅ 已实现 | 687 行，build_status=stable |
| `tests/ex_sor/test_transaction_cost_optimizer.py` | ✅ 已实现 | 40 用例，全过 |

## 11. 设计真源映射

| 设计文档条目 | 本模块实现 |
|-------------|-----------|
| §2.1 XS-EXT-03 佣金费率 | FeeSchedule.commission_rate_bps + 最低收费 |
| §2.1 XS-EXT-03 印花税 | FeeSchedule.stamp_duty_rate_bps（卖方单边） |
| §2.1 XS-EXT-03 冲击成本 | IMPACT 组件 + LinearImpactEstimator |
| §2.1 XS-EXT-03 机会成本 | OPPORTUNITY 组件（未成交部分） |
| §13.3 成本模型 | 显性+隐性六项分解 |
| §521 滑点成本 | IMPACT 估计器对齐固定+动态滑点模型 |

## 12. 变更记录

| 日期 | 版本 | 变更摘要 |
|------|------|---------|
| 2026-08-02 | 0.1.0 | 初版落地：显性(佣金+印花税+过户费+监管费)+隐性(冲击+机会)六项分解+优化建议；类名由 CostBreakdown 改为 TransactionCostBreakdown 解决冲突；module_id 由非法 MOD-XS-EXT-003 改为派生轨 MOD-EX_SOR_EXT-003 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX_SOR_EXT-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX_SOR_EXT-003` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX_SOR_EXT-003` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX_SOR_EXT-003 | MOD-EX_SOR_EXT-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 13. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 13.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/ex_sor/test_transaction_cost_optimizer.py` | ✅ 已实现 | |

### 13.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §13（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
