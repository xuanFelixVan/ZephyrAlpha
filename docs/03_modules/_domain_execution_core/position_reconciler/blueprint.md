---
module_id: MOD-EX-056
title: "盘中持仓对账器蓝图 — 系统账vs券商账定期比对+差异冻结"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
responsibility_domain: 
---

# 盘中持仓对账器 (Position Reconciler) — D-EX-CORE-56

> **优先级**: P1 | **成熟度**: production | **建设标记**: ✅可建
> **设计真源**: `D:\临时工作区\依赖图\08-D-EX-CORE-执行核心域.md` §1 D-EX-CORE-56
> **depgraph**: MOD-EX-056 (production/testing/can_build=1)

## 1. 大白话简介

持仓对账器是"交易系统的对账员"——定期把"系统自己记的持仓"（PositionTracker，靠成交回报一笔笔累计）
和"券商那边查回来的持仓"（miniQMT / SimulationBroker 的 get_positions）放在一起比对。
两边对得上，说明记账没出错；对不上（差异 > 容差），立刻告警并冻结这只股票的交易，
防止在持仓不明的情况下继续下单。等下次对账两边又一致了，再解冻恢复交易。

**为什么需要它？** 成交回报可能丢、可能重复、券商端可能有人工改动（分红/送股/手工调仓）。
没有对账，系统持仓和真实持仓会悄悄漂移，风控和报告都建立在错误数据上。对账器就是这个"防漂移哨兵"。

## 2. 职责（阶段1 scope）

| 职责 | 说明 | 状态 |
|------|------|------|
| 双源持仓比对 | 比较 PositionTracker（系统账）与 Broker（外部账）的 holdings | ✅阶段1 |
| 差异检测 | 逐标的比较 quantity，diff > tolerance 记为 drift | ✅阶段1 |
| 冻结/解冻管理 | 有 drift 的标的加入冻结集；恢复一致后移出 | ✅阶段1 |
| 告警回调 | on_drift 回调通知调用方（解耦告警通道） | ✅阶段1 |
| 容差配置 | tolerance 可注入（默认 0=精确匹配） | ✅阶段1 |
| 线程安全 | 冻结集读写加锁 | ✅阶段1 |

## 3. 阶段2扩展（本次不实现，记录防遗忘）

| 扩展 | 说明 | 依赖 |
|------|------|------|
| 定时调度 | 每 5 分钟自动触发 reconcile（Timer/APScheduler） | 调度基础设施 |
| miniQMT 实盘源 | broker_source 接 miniQMT get_positions | miniQMT 通道（MOD-EX-058） |
| D-L1 降级 | 恢复后对账仍不一致 → 触发 D-L1 降级（跨域事件） | D-L1 降级机制 |
| 对账历史持久化 | 每次 reconcile 结果落 SQLite，供审计回溯 | SQLite 表 |
| 恢复后强制对账 | 交易恢复前必须先跑一次 reconcile 通过 | 状态机集成 |
| 现金对账 | 除 holdings 外，cash 也参与比对 | 现金对账规则 |

## 4. 依赖关系（depgraph 设计态边）

| 方向 | 对端 | dep_type | 说明 |
|------|------|----------|------|
| ← 入 | MOD-EX-002 (position_tracker) | data | 读取系统账持仓（PositionSource） |
| ← 入 | MOD-EX-003 (simulation_broker / broker adapter) | data | 读取外部账持仓（PositionSource） |

**跨域契约**:
- 消费: CTR-006 (PositionSnapshot) ← D_EXECUTION_CORE（系统账）+ Broker（外部账）
- 产出: ReconcileResult / DriftItem（内部数据结构，非跨域契约）

**PositionSource 协议**（鸭子类型，PositionTracker 和 SimulationBroker 均已满足）:
```python
class PositionSource(Protocol):
    def get_positions(self) -> PositionSnapshot: ...
```

## 5. API 契约

```python
@dataclass(frozen=True)
class DriftItem:
    """单个标的的差异记录。"""
    symbol: str
    system_qty: Decimal    # PositionTracker 的数量
    broker_qty: Decimal    # Broker 的数量
    diff: Decimal          # system_qty - broker_qty

@dataclass(frozen=True)
class ReconcileResult:
    """一次对账的结果。"""
    timestamp: datetime
    matched: bool                    # True=完全一致
    drifts: tuple[DriftItem, ...]    # 差异项（空 tuple = 一致）
    frozen_symbols: frozenset[str]   # 对账后仍冻结的标的
    newly_frozen: frozenset[str]     # 本次新增冻结
    newly_unfrozen: frozenset[str]   # 本次解冻

class PositionReconciler:
    """盘中持仓对账器 — 定期比对系统账与券商账，差异→告警+冻结。"""

    def __init__(
        self,
        system_source: PositionSource,      # 通常 = PositionTracker
        broker_source: PositionSource,      # 通常 = SimulationBroker / miniQMT
        tolerance: Decimal = Decimal("0"),
        on_drift: Callable[[ReconcileResult], None] | None = None,
    ) -> None: ...

    def reconcile(self) -> ReconcileResult:
        """执行一次对账：比较两源 holdings，更新冻结集，返回结果。
        matched=False 时触发 on_drift 回调。"""

    def is_frozen(self, symbol: str) -> bool: ...
    @property
    def frozen_symbols(self) -> frozenset[str]: ...
    def unfreeze(self, symbol: str) -> None:
        """手动解冻（人工干预或恢复后强制）。"""
```

## 6. 实现方案

**比对算法**:
1. `system_snap = system_source.get_positions()`，`broker_snap = broker_source.get_positions()`
2. 取两源 holdings 的 symbol 并集
3. 逐标的：`diff = system_qty - broker_qty`，`abs(diff) > tolerance` → 记 DriftItem
4. 冻结集更新：`new_frozen = drift_symbols - old_frozen`，`new_unfrozen = old_frozen - drift_symbols`
5. 冻结集 = 当前 drift_symbols（有差异即冻结，无差异即解冻）
6. matched = (drifts 为空)；不 matched → 触发 on_drift

**冻结语义**:
- 冻结集是"当前对账有差异的标的"——每次 reconcile 全量重算（不是累加）
- is_frozen(symbol) 供 ExecutionEngine 下单前检查（阶段2集成）
- 解冻=下次对账该标的 diff ≤ tolerance，自动移出冻结集

**阶段1 broker_source**:
- 模拟盘：SimulationBroker.get_positions()（与 PositionTracker 共享同一 Fill 流，正常情况应一致）
- 实盘（阶段2）：miniQMT 查询接口

## 7. 测试计划

| 用例 | 覆盖点 |
|------|--------|
| 两源完全一致 | matched=True，drifts 空，无冻结 |
| 系统多记 | system_qty > broker_qty → drift，冻结该标的 |
| 系统少记 | system_qty < broker_qty → drift，冻结 |
| 标的仅在一源 | 一源有另一源无 → drift（缺方按 0） |
| 容差非零 | diff ≤ tolerance 不算 drift |
| 冻结→解冻 | 第一次 drift 冻结，修正后第二次 reconcile 解冻 |
| newly_frozen/unfrozen | 增量正确 |
| on_drift 回调 | matched=False 时被调用，True 时不调用 |
| 多标的混合 | 部分一致部分漂移 |
| 线程安全 | 并发 reconcile + is_frozen 不出错 |
| PositionTracker/SimulationBroker 集成 | 用真实对象作 source 验证 |

## 8. 不变量 (INVARIANTS)

- DriftItem / ReconcileResult 是 frozen dataclass，跨层传递不可变
- Decimal 用于所有数量比较，禁止 float
- 冻结集每次 reconcile 全量重算（非累加），保证与最新对账结果一致
- on_drift 回调异常不阻断 reconcile（catch + log，避免告警通道故障影响对账主流程）
- reconcile() 不修改任一 source 的状态（纯读比对）

## 9. ID 映射

depgraph `blueprint_id=MOD-EX-056` 与设计文档 `D-EX-CORE-56` 编号一致（从 008 起对齐，见 EX-04 蓝图 §10）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-056`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-056` 的 5 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX-056` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-056 | MOD-EX-056 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 5 文件 | N/A | — |

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
| `tests/ex_core/test_fill_handler.py` | ✅ 已实现 | |
| `tests/ex_core/test_multi_contract_adapter.py` | ✅ 已实现 | |
| `tests/ex_core/test_position_reconciler.py` | ✅ 已实现 | |
| `tests/ex_core/test_repository_interface.py` | ✅ 已实现 | |

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
