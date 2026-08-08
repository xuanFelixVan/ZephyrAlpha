---
module_id: MOD-TRADING-002
title: "盈亏计算器蓝图 — 已实现/未实现盈亏+A股费率"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L03_trading
layer_name: trading
functional_domain: trading
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-TRADING-002 PnL Calculator — 盈亏计算器 蓝图

> **module_id**: MOD-TRADING-002 | **域**: D_TRADING | **层**: L03 交易运营
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-010(盈亏分析)
> **SSoT**: depgraph MOD-TRADING-002 | **设计真源**: D:\临时工作区\依赖图\18-D-TRADING-交易运营域.md §3.2 CTR-TRD-01

## 1. 定位

盈亏计算器——交易后盈亏核算基础设施。从成交回报(Fill)和持仓均价计算已实现盈亏,
从持仓+当前市价计算未实现盈亏, 含A股交易成本(佣金/印花税/过户费)核算。

产出 CTR-TRD-01 费率/PnL数据 → D-REPORTING(C-010)。

属 A 类基础设施(确定性数学计算, 逻辑明确), 费率为 C 类可调参数。
**纯基础设施: 不决定"买什么/何时买", 只负责"算这笔交易赚了多少/花了多少成本"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | Fill (成交回报, CTR-005) | CTR-005 |
| 输入 | OrderSide (买卖方向) | order_enums |
| 输入 | avg_cost (持仓均价, 来自 PositionTracker) | — |
| 输入 | current_price (当前市价, 来自行情) | — |
| 输入 | FeeConfig (费率配置) | C 类参数 |
| 输出 | RealizedPnl / UnrealizedPnl / PortfolioPnl | CTR-TRD-01 |

## 3. 核心规则

### 3.1 已实现盈亏 (Realized PnL)

卖出成交时计算(平均成本法):

```
turnover = fill_price × filled_quantity
gross_pnl = (fill_price - avg_cost) × filled_quantity
fees = commission + stamp_duty + transfer_fee
net_pnl = gross_pnl - fees
```

买入不计已实现盈亏(只更新持仓成本, 由 PositionTracker 负责)。

### 3.2 未实现盈亏 (Unrealized PnL)

```
unrealized_pnl = (current_price - avg_cost) × quantity
```

仅对多头持仓(quantity > 0)计算。空头持仓方向相反。

### 3.3 A股交易成本 (FeeConfig)

| 费项 | 费率 | 方向 | 说明 |
|------|------|------|------|
| 佣金 (commission) | 0.025% | 买入+卖出 | 最低 ¥5/笔 |
| 印花税 (stamp_duty) | 0.05% | 仅卖出 | 2023年减半后0.05% |
| 过户费 (transfer_fee) | 0.001% | 买入+卖出 | 2022年起沪深统一 |

费率全部为 C 类可调参数(FeeConfig), 非硬编码。

### 3.4 费用计算接口 (FeeCalculator port)

```
FeeCalculator (Protocol):
    calculate(turnover: Decimal, side: OrderSide) -> FeeBreakdown

AShareFeeCalculator (默认实现):
    使用 FeeConfig 计算A股标准费用
```

设计为 port + 默认实现, 未来 MOD-TRADING-004(公司行为处理器)可注入更复杂的费率逻辑。

## 4. 关键不变量 (INVARIANTS)

- 所有金额计算使用 Decimal, 禁止 float
- PnLResult / FeeBreakdown 为 frozen dataclass (不可变)
- 已实现盈亏仅在卖出时计算(买入只更新成本)
- 费率参数全部来自 FeeConfig, 禁止硬编码
- 净盈亏 = 毛盈亏 - 总费用 (恒成立)

## 5. 错误契约

- `InvalidPnlInputError` (ZA-TR-0001): 输入数据非法(如负均价/负数量)

## 6. 数据模型

```python
@dataclass(frozen=True)
class FeeConfig:
    commission_rate: Decimal = Decimal("0.00025")   # 0.025%
    commission_min: Decimal = Decimal("5")           # 最低 ¥5
    stamp_duty_rate: Decimal = Decimal("0.0005")     # 0.05% (卖出)
    transfer_fee_rate: Decimal = Decimal("0.00001")  # 0.001%

@dataclass(frozen=True)
class FeeBreakdown:
    commission: Decimal
    stamp_duty: Decimal
    transfer_fee: Decimal
    @property
    def total(self) -> Decimal: ...

@dataclass(frozen=True)
class RealizedPnl:
    symbol: str
    side: OrderSide
    quantity: Decimal
    fill_price: Decimal
    avg_cost: Decimal
    turnover: Decimal
    gross_pnl: Decimal
    fees: FeeBreakdown
    @property
    def net_pnl(self) -> Decimal: ...

@dataclass(frozen=True)
class UnrealizedPnl:
    symbol: str
    quantity: Decimal
    avg_cost: Decimal
    current_price: Decimal
    gross_pnl: Decimal

@dataclass(frozen=True)
class PortfolioPnl:
    realized: list[RealizedPnl]
    unrealized: list[UnrealizedPnl]
    @property
    def total_realized(self) -> Decimal: ...
    @property
    def total_unrealized(self) -> Decimal: ...
    @property
    def total_pnl(self) -> Decimal: ...
    @property
    def total_fees(self) -> Decimal: ...
```

## 7. API

```python
class PnlCalculator:
    def __init__(self, fee_calculator: FeeCalculator | None = None) -> None: ...

    def calculate_realized(
        self, fill: Fill, side: OrderSide, avg_cost: Decimal
    ) -> RealizedPnl: ...

    def calculate_unrealized(
        self, symbol: str, quantity: Decimal, avg_cost: Decimal, current_price: Decimal
    ) -> UnrealizedPnl: ...

    def calculate_portfolio(
        self,
        fills: list[tuple[Fill, OrderSide, Decimal]],  # (fill, side, avg_cost)
        positions: list[tuple[str, Decimal, Decimal, Decimal]],  # (symbol, qty, avg_cost, price)
    ) -> PortfolioPnl: ...
```

## 8. 依赖

- `zephyr.shared.contracts.fill` (Fill, CTR-005)
- `zephyr.shared.contracts.enums.order_enums` (OrderSide)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D-REPORTING(C-010 盈亏分析), D-EX-CORE, D-POSITION
- 设计真源: D-TRADING §3.2 CTR-TRD-01

## 9. 测试

- `tests/trading/test_pnl_calculator.py`
- 覆盖: 已实现盈亏(卖)、未实现盈亏、A股费率(佣金最低¥5/印花税卖出/过户费)、
  组合盈亏汇总、边界值(零持仓/负均价拒绝)、Decimal精度

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-002` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRADING-002` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-002 | MOD-TRADING-002 | ✅ |
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

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/trading/test_pnl_calculator.py` | ✅ 已实现 | |

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
