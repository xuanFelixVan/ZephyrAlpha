---
module_id: MOD-EX-002
title: "持仓跟踪器蓝图 — Fill回调驱动+平均成本+PositionSnapshot产出"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
ttl: permanent
responsibility_domain: 
---

# 持仓跟踪器 (Position Tracker) — D-EX-CORE-04

> **优先级**: P0 | **成熟度**: production | **建设标记**: ✅可建
> **设计真源**: `D:\临时工作区\依赖图\08-D-EX-CORE-执行核心域.md` §1 D-EX-CORE-04
> **depgraph**: MOD-EX-002 (production/testing/can_build=1)

## 1. 大白话简介

持仓跟踪器是"交易系统的账本"——每笔成交（Fill）进来，它就更新对应股票的持仓数量和平均成本，
同时扣减/增加现金。任何时刻都能拍一张"持仓快照"（PositionSnapshot）给风控、组合、报告域用。

**为什么从 SimulationBroker 拆出？** 当前持仓逻辑内嵌在 SimulationBroker 里（`_positions`/`_avg_cost`/
`_update_positions`/`get_positions`），实盘券商（MiniQmtBroker）也有类似需求。拆成独立模块后，
回测/模拟/实盘三个场景共用同一套持仓跟踪逻辑，消除三态不一致风险。

## 2. ID 映射说明

depgraph `blueprint_id=MOD-EX-002` 对应设计文档 `D-EX-CORE-04`（ID 错位：depgraph 顺序编号 ≠
设计文档功能编号）。映射表见 §10。

## 3. 职责（阶段1 scope）

| 职责 | 说明 | 状态 |
|------|------|------|
| 持仓数量维护 | symbol → quantity（买入加、卖出减） | ✅阶段1 |
| 平均成本计算 | 买入：加权平均；卖出：成本不变（已实现部分在现金端） | ✅阶段1 |
| 现金跟踪 | 买入扣现金（价×量+佣金）；卖出加现金（价×量-佣金） | ✅阶段1 |
| PositionSnapshot 产出 | CTR-006 快照（holdings/market_values/cash/total_market_value） | ✅阶段1 |
| Fill 回调集成 | `apply_fill(fill, side)` 更新持仓 | ✅阶段1 |
| market_value 计算 | qty × avg_cost（阶段1）；阶段2改为 qty × 实时价 | ✅阶段1 |

## 4. 阶段2扩展（本次不实现，记录防遗忘）

| 扩展 | 说明 | 依赖 |
|------|------|------|
| SQLite 持久化 | 持仓状态落盘，重启恢复 | SQLite execution_audit 表 |
| Redis 实时更新 | 每笔成交后写 Redis，供 D-RISK 实时监控 | Redis 基础设施 |
| T+1 锁定约束 | A股买入当天不可卖（查 available_quantity） | miniQMT 持仓查询 |
| FIFO/LIFO 成本法 | 替代平均成本的可选成本核算 | 设计文档"扩展"段 |
| 保证金追踪 | 融资融券保证金计算 | 保证金数据源 |
| unrealized_pnl | 需实时价格 → 浮动盈亏 | PriceProvider 注入 |
| 方案C: D-RISK 指令 | D-RISK 发调仓指令，PositionTracker 执行写入 | D-RISK 域就绪 |

## 5. 依赖关系（depgraph 设计态边）

| 方向 | 对端 | dep_type | 说明 |
|------|------|----------|------|
| ← 入 | MOD-EX-001 (fill_handler) | runtime | 成交处理器将 Fill 传入 |
| ← 入 | MOD-EX-050 (repository_interface) | runtime | 仓储接口提供持久化（阶段2） |
| ← 入 | MOD-EX-056 (position_reconciler) | data | 对账器读取持仓数据 |
| → 出 | MOD-EX-008 (fill_processor) | runtime | 依赖成交处理器（注:双向，depgraph仅记单向防环） |
| → 出 | MOD-EX-003 (audit_journal) | event | 持仓变更事件送审计 |

**跨域契约**:
- 消费: CTR-005 (Fill) ← D_EXECUTION_CORE
- 产出: CTR-006 (PositionSnapshot) → D_RISK / D_PORTFOLIO / D_REPORTING / D_ML_TRAIN
- 产出: E-EX-04 (FillReceived 事件) → D_RISK / D_PORTFOLIO / D_REPORTING

## 6. API 契约

```python
class PositionTracker:
    """持仓跟踪器 — Fill 回调驱动，产出 PositionSnapshot (CTR-006)。"""

    def __init__(self, initial_cash: Decimal = Decimal("1000000")) -> None: ...

    def apply_fill(self, fill: Fill, side: OrderSide) -> None:
        """应用成交——更新持仓数量、平均成本、现金。
        Args:
            fill: 成交回报（CTR-005，不可变）
            side: 买卖方向（Fill 契约无 side 字段，需调用方传入）
        """

    def get_positions(self) -> PositionSnapshot:
        """产出持仓快照（CTR-006），不可变。"""

    @property
    def cash(self) -> Decimal: ...
    @property
    def holdings(self) -> dict[str, Decimal]: ...
    @property
    def avg_costs(self) -> dict[str, Decimal]: ...
```

## 7. 实现方案（从 SimulationBroker 拆出）

**提取逻辑**（SimulationBroker → PositionTracker）:
- `_positions: dict[str, Decimal]` → `tracker._holdings`
- `_avg_cost: dict[str, Decimal]` → `tracker._avg_costs`
- `_cash: Decimal` → `tracker._cash`
- `_update_positions(order, fill_price, commission)` → `tracker.apply_fill(fill, side)`
- `get_positions()` → `tracker.get_positions()`

**SimulationBroker 改造**（保持外部 API 不变）:
- `__init__` 创建 `self._position_tracker = PositionTracker(initial_cash)`
- `_update_positions` 改为 `self._position_tracker.apply_fill(fill, order.side)`
- `get_positions` 改为 `return self._position_tracker.get_positions()`

**平均成本算法**（与 SimulationBroker 现有逻辑一致）:
- 买入: `new_avg = (old_avg × old_qty + fill_price × fill_qty) / new_qty`
- 卖出: avg_cost 不变（成本已锁定），现金端实现盈亏

## 8. 测试计划

| 用例 | 覆盖点 |
|------|--------|
| 买入更新持仓 | quantity 增加、avg_cost 加权、cash 扣减 |
| 卖出更新持仓 | quantity 减少、avg_cost 不变、cash 增加 |
| 多次买入同标的 | avg_cost 递进更新 |
| 卖出到零持仓 | quantity=0、avg_cost 清零 |
| PositionSnapshot 不可变 | frozen dataclass 验证 |
| cash 不足场景 | 边界检查（阶段1不阻断，记录负值由风控处理） |
| SimulationBroker 集成 | 拆出后 get_positions 结果一致 |

## 9. 不变量 (INVARIANTS)

- PositionSnapshot 是 frozen dataclass，跨层传递时不可变
- Decimal 用于所有金额/数量计算，禁止 float
- apply_fill 幂等性：同一 fill_id 重复调用不重复更新（阶段2，阶段1由调用方保证）
- cash 可为负（融资场景），由 D-RISK 风控拦截，PositionTracker 不阻断

## 10. ID 映射表 (MOD-EX-XXX ↔ D-EX-CORE-XX)

depgraph 前4个节点使用顺序编号，与设计文档功能编号错位：

| depgraph blueprint_id | 设计文档 ID | 功能 | 说明 |
|----------------------|------------|------|------|
| MOD-EX-001 | D-EX-CORE-48 | 部分成交处理 (fill_handler) | 顺序编号≠功能编号 |
| **MOD-EX-002** | **D-EX-CORE-04** | **Position Tracker** | **本模块** |
| MOD-EX-003 | D-EX-CORE-15 | Execution Auditor (audit_journal) | 顺序编号≠功能编号 |
| MOD-EX-004 | INV-007 | Redis 幂等性 (redis_idempotency) | 跨模块基础设施 |
| MOD-EX-008+ | D-EX-CORE-08+ | 对齐 | 从008起编号一致 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-002` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX-002` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-002 | MOD-EX-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 11. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 11.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/ex_core/position_tracker/__init__.py` | ⚠️ 骨架 | |
| `src/zephyr/ex_core/position_tracker/tracker.py` | ✅ 已实现 | |

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


