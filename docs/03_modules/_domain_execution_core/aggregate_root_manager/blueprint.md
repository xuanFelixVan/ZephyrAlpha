---
module_id: MOD-EX-049
title: "执行域聚合根管理器蓝图 — Order/Position生命周期协调层"
doc_type: blueprint
status: Active
version: "0.1.7"
design_maturity: production
ttl: permanent
responsibility_domain: 
---

# 执行域聚合根管理器 (Aggregate Root Manager) — D-EX-CORE-49

> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建
> **设计真源**: `D:\临时工作区\依赖图\08-D-EX-CORE-执行核心域.md` §1 D-EX-CORE-49
> **depgraph**: MOD-EX-049 (design/planned/can_build=1)

## 1. 大白话简介

聚合根管理器是"执行域的总调度台"——把订单仓储、成交处理、持仓跟踪三个独立组件拧成一股绳。
上层（Saga编排器/Fill处理器）只需调一个方法，它就自动完成"更新订单状态→记录成交→更新持仓→
持久化"的全链路操作。就像餐厅的领班——你只管点菜（发指令），领班负责协调后厨各岗位（订单/
成交/持仓）协同出餐，不用你分别跑去找每个岗位。

**为什么不重复造轮子？** 它不替代 FillHandler/PositionTracker/Repository 的任何逻辑，
而是作为 Facade（门面模式）协调三者：FillHandler 算成交累积，PositionTracker 更新持仓，
Repository 存到仓储。聚合根管理器只负责"调用顺序+事务边界"，不包含业务计算。

## 3. 职责（阶段1 scope）

| 职责 | 说明 | 状态 |
|------|------|------|
| 订单创建+持久化 | create_order → 构造Order → save to repo | ✅阶段1 |
| 成交全链路处理 | process_fill → FillHandler + PositionTracker + repo.save | ✅阶段1 |
| 订单状态查询 | get_order_state → order + fill_summary | ✅阶段1 |
| 持仓快照查询 | get_position_snapshot → PositionTracker.get_positions | ✅阶段1 |
| 开放订单查询 | get_open_orders → repo.get_open_orders | ✅阶段1 |
| 持仓快照持久化 | save_position_snapshot → position_repo.save | ✅阶段1 |

## 5. 依赖关系

| 方向 | 对端 | dep_type | 说明 |
|------|------|----------|------|
| → 出 | MOD-EX-001 (FillHandler) | runtime | 成交处理委托 |
| → 出 | MOD-EX-002 (PositionTracker) | runtime | 持仓跟踪委托 |
| → 出 | MOD-EX-050 (Repository) | runtime | 持久化委托 |
| → 出 | CTR-004 (Order) | import_depends | Order 聚合根 |
| → 出 | CTR-005 (Fill) | import_depends | Fill 成交回报 |

## 6. API 契约

```python
@dataclass(frozen=True)
class OrderState:
    """订单完整状态——不可变。"""
    order: Order
    fill_summary: FillSummary | None

class ExecutionAggregateManager:
    """执行域聚合根管理器——协调 Order/Position 生命周期。"""

    def __init__(
        self,
        order_repo: OrderRepository,
        position_tracker: PositionTracker,
        fill_handler: FillHandler | None = None,
        position_snapshot_repo: PositionSnapshotRepository | None = None,
    ) -> None: ...

    def create_order(
        self, symbol: str, strategy_id: str, side: OrderSide,
        order_type: OrderType, quantity: Decimal,
        limit_price: Decimal | None = None,
    ) -> Order:
        """创建订单并持久化到仓储。"""

    def process_fill(self, fill: Fill, order: Order) -> FillSummary:
        """成交全链路：FillHandler→PositionTracker→repo.save。"""

    def get_order_state(self, order_id: str) -> OrderState | None:
        """获取订单+成交汇总。"""

    def get_position_snapshot(self) -> PositionSnapshot:
        """获取当前持仓快照。"""

    def save_position_snapshot(self) -> PositionSnapshot:
        """持久化当前持仓快照（如配有 position_snapshot_repo）。"""

    def get_open_orders(self) -> list[Order]:
        """查询所有开放订单。"""

    def get_order(self, order_id: str) -> Order | None: ...
```

## 8. 测试计划

| 用例 | 覆盖点 |
|------|--------|
| 创建订单+持久化 | create_order → repo.get 返回同一订单 |
| 成交全链路 | process_fill → order状态更新 + position更新 + repo持久化 |
| 多笔成交累积 | 3笔fill → order FILLED + position 正确 |
| 订单状态查询 | get_order_state 返回 order + fill_summary |
| 持仓快照查询 | get_position_snapshot 返回正确 holdings/cash |
| 持仓快照持久化 | save_position_snapshot → position_repo 有记录 |
| 开放订单查询 | get_open_orders 过滤正确 |
| 未知订单查询 | get_order_state 返回 None |

## 9. 不变量

- 聚合根管理器是 Facade，不包含业务计算逻辑（委托给 FillHandler/PositionTracker）
- process_fill 调用顺序固定：FillHandler→PositionTracker→repo.save
- OrderState 是 frozen dataclass
- 依赖注入：所有组件通过构造函数注入，可替换为 mock

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-049`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-049` 的 11 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX-049` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-049 | MOD-EX-049 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 11 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/ex_core/test_aggregate_root_manager.py` | ✅ 已实现 | |
| `tests/ex_core/test_daban_execution.py` | ✅ 已实现 | |
| `tests/ex_core/test_daban_exit_decision.py` | ✅ 已实现 | |
| `tests/ex_core/test_daban_instant_circuit_breaker.py` | ✅ 已实现 | |
| `tests/ex_core/test_daban_monitors.py` | ✅ 已实现 | |
| `tests/ex_core/test_daban_named_functions.py` | ✅ 已实现 | |
| `tests/ex_core/test_daban_pit_safety.py` | ✅ 已实现 | |
| `tests/ex_core/test_daban_signal_decision.py` | ✅ 已实现 | |
| `tests/ex_core/test_operational_risk_stats.py` | ✅ 已实现 | |
| `tests/ex_core/test_position_tracker.py` | ✅ 已实现 | |

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


