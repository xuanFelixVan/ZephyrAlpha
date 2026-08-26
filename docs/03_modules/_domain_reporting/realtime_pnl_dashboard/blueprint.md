---
module_id: MOD-RPT-004
title: "实时盈亏仪表盘蓝图 — PnL/持仓/风控状态聚合(3s刷新)"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
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

# MOD-RPT-004 Real-time P&L Dashboard — 实时盈亏仪表盘 蓝图

> **module_id**: MOD-RPT-004 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-010(盈亏分析)
> **SSoT**: depgraph MOD-RPT-004 | **设计真源**: D:\临时工作区\依赖图\10-D-REPORTING-报告域.md §1.2 D-REPORTING-04, §2.4 Phase 1
> **激活阶段**: Phase 1 (前提: D-EX-CORE就绪 CTR-005/006 + D-DATA可访问)

## 1. 定位

实时盈亏仪表盘——盘中实时聚合 PnL/持仓/订单/风控状态, 产出 DashboardSnapshot
供 D-FRONTEND 渲染（本模块只产出数据, 不渲染 UI）。3s 刷新由消费者定时调用
refresh() 实现, 设计不内置定时器（解耦, 便于测试）。

直接消费 MOD-TRADING-002 PnL 计算器(CTR-TRD-01) + MOD-EX-002 PositionTracker,
闭环价值链: 成交→持仓→PnL→仪表盘。

属 A 类基础设施(确定性数据聚合), 纯消费层不发布领域事件(D-RPT-D01)。
**纯基础设施: 不决定"买什么/何时买", 只负责"实时算出当前盈亏/持仓/风控状态"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | Fill (成交回报, CTR-005) | CTR-005 |
| 输入 | PositionSnapshot (持仓快照, CTR-006) via PositionTracker | CTR-006 |
| 输入 | market_prices (当前市价, 来自行情) | — |
| 输入 | RiskDashboardSnapshot (风控状态, CTR-P1-008, 可选) | CTR-P1-008 |
| 输入 | PnL 计算结果 (来自 PnlCalculator, CTR-TRD-01) | CTR-TRD-01 |
| 输出 | DashboardSnapshot (实时仪表盘快照) | → D-FRONTEND |

## 3. 核心规则

### 3.1 已实现盈亏累计

每次 record_fill(fill, side) 调用:
- 从 PositionTracker 读取 avg_cost (卖出不改变 avg_cost, 可安全读取)
- 调用 PnlCalculator.calculate_realized 计算 net_pnl + fees
- 累加到 session 级 realized_pnl_total / fees_total / fill_count
- 保留最近 N 笔成交 (recent_fills, 默认 N=20)

### 3.2 未实现盈亏实时计算

refresh(market_prices) 调用:
- 从 PositionTracker.get_positions() 读取当前持仓
- 对每个标的: avg_cost 来自 tracker, current_price 来自 market_prices (缺失则回退 avg_cost)
- 调用 PnlCalculator.calculate_unrealized 计算 gross_pnl
- 汇总 unrealized_pnl_total

### 3.3 组合总盈亏

```
total_pnl = realized_pnl_total + unrealized_pnl_total
total_assets = cash + total_market_value
return_pct = total_pnl / initial_capital × 100%
```

### 3.4 风控状态 (可选, 降级模式)

- update_risk(risk_snapshot): 注入 RiskDashboardSnapshot (CTR-P1-008)
- 无风控数据时 risk_snapshot=None (降级: 仪表盘不显示风控状态, PnL/持仓不受影响)
- 设计真源 D-RPT-D08: 降级策略——上游未就绪时核心功能仍可用

### 3.5 3s 刷新机制

- 本模块不内置定时器 (解耦: 消费者 TradingSession/D-FRONTEND 定时调 refresh)
- refresh() 为纯函数式: 输入 market_prices → 输出 DashboardSnapshot (并缓存最近一次)
- 线程安全: 内部加 Lock 保护累计状态 (record_fill 与 refresh 可能并发)

## 4. 关键不变量 (INVARIANTS)

- 所有金额计算使用 Decimal, 禁止 float (return_pct 除外, 百分比展示用 float)
- DashboardSnapshot / PositionPnlEntry 为 frozen dataclass (不可变)
- realized_pnl_total 单调累加 (仅 record_fill 修改, refresh 只读)
- total_pnl = realized_pnl_total + unrealized_pnl_total 恒成立 (refresh 时)
- 纯消费层: 不发布领域事件, 不修改持仓状态 (持仓由 PositionTracker 管理)

## 5. 错误契约

- `InvalidDashboardInputError` (ZA-RPT-0001): 市价为负/initial_capital 非正

## 6. 数据模型

```python
@dataclass(frozen=True)
class PositionPnlEntry:
    symbol: str
    quantity: Decimal
    avg_cost: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_pct: float  # (current-avg)/avg × 100, avg=0时为0

@dataclass(frozen=True)
class DashboardSnapshot:
    timestamp: datetime
    portfolio_id: str
    total_pnl: Decimal          # realized + unrealized
    realized_pnl: Decimal       # 累计净已实现
    unrealized_pnl: Decimal     # 当前浮盈亏
    total_fees: Decimal         # 累计费用
    cash: Decimal
    total_market_value: Decimal
    total_assets: Decimal       # cash + market_value
    return_pct: float           # total_pnl / initial_capital × 100
    positions: list[PositionPnlEntry]
    risk_snapshot: Optional[RiskDashboardSnapshot]
    fill_count: int
    schema_version: str = "1.0"
```

## 7. API

```python
class RealtimePnlDashboard:
    def __init__(
        self,
        position_tracker: PositionTracker,
        pnl_calculator: PnlCalculator | None = None,
        portfolio_id: str = "realtime_dashboard",
        initial_capital: Decimal = Decimal("1000000"),
        recent_fills_limit: int = 20,
    ) -> None: ...

    def record_fill(
        self, fill: Fill, side: OrderSide, avg_cost: Decimal | None = None
    ) -> RealizedPnl: ...

    def update_risk(self, risk_snapshot: RiskDashboardSnapshot) -> None: ...

    def refresh(self, market_prices: dict[str, Decimal]) -> DashboardSnapshot: ...

    def get_snapshot(self) -> DashboardSnapshot | None: ...
```

## 8. 依赖

- `zephyr.ex_core.position_tracker.tracker` (PositionTracker, MOD-EX-002)
- `zephyr.trading.pnl_calculator` (PnlCalculator, MOD-TRADING-002)
- `zephyr.shared.contracts.fill` (Fill, CTR-005)
- `zephyr.shared.contracts.position` (PositionSnapshot, CTR-006)
- `zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot` (RiskDashboardSnapshot, CTR-P1-008)
- `zephyr.shared.contracts.enums.order_enums` (OrderSide)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D-FRONTEND (Dashboard 渲染)
- 设计真源: D-REPORTING §1.2 D-REPORTING-04, §2.4 Phase 1, §3 D-RPT-D01/D08

## 9. 测试

- `tests/reporting/test_realtime_pnl_dashboard.py`
- 覆盖: 已实现盈亏累计(多笔)、未实现盈亏实时计算、组合总盈亏、return_pct、
  风控状态注入/降级、持仓明细(多空/零)、3s刷新幂等、Decimal精度、frozen不可变、
  边界值(空持仓/负市价拒绝/initial_capital非正)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RPT-004`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RPT-004` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RPT-004` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RPT-004 | MOD-RPT-004 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

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
| `src/zephyr/reporting/realtime_pnl_dashboard.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_realtime_pnl_dashboard.py` | ✅ 已实现 | |

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


