---
module_id: MOD-EX-050
title: "执行域仓储接口蓝图 — Order/PositionSnapshot持久化抽象+内存实现"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
ttl: permanent
responsibility_domain: 
---

# 执行域仓储接口 (Repository Interface) — D-EX-CORE-50

> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建
> **设计真源**: `D:\临时工作区\依赖图\08-D-EX-CORE-执行核心域.md` §1 D-EX-CORE-50
> **depgraph**: MOD-EX-050 (design/planned/can_build=1)

## 1. 大白话简介

执行域仓储接口是"订单和持仓的保险柜"——定义一套标准接口，让订单（Order）和持仓快照
（PositionSnapshot）的存取方式与具体存储引擎解耦。现在用内存字典存（开发/测试用），
将来可以换成 SQLite/PostgreSQL，上层代码不用改。就像银行柜员窗口——不管后面保险箱是
铁皮柜还是金库，柜员给你的存取接口都一样。

**为什么需要它？** 当前 OrderManager 用 `self._orders: dict` 存订单，PositionTracker 用
`self._holdings: dict` 存持仓，存储逻辑内嵌在业务模块中。拆出仓储接口后：
- 持久化策略可替换（内存→SQLite→PG）而不改业务代码
- 测试时可注入 mock 仓储
- 符合 DDD Repository 模式，聚合根的持久化由仓储负责

## 2. 职责（阶段1 scope）

| 职责 | 说明 | 状态 |
|------|------|------|
| OrderRepository 抽象 | save/get/get_by_status/get_open_orders/delete/get_all | ✅阶段1 |
| PositionSnapshotRepository 抽象 | save/get_latest/get_all/delete | ✅阶段1 |
| InMemoryOrderRepository | 内存 dict 实现（开发/测试用） | ✅阶段1 |
| InMemoryPositionSnapshotRepository | 内存 dict 实现（开发/测试用） | ✅阶段1 |
| 仓储工厂 | create_order_repository/create_position_repository | ✅阶段1 |

## 4. 阶段2扩展（本次不实现，记录防遗忘）

| 扩展 | 说明 | 依赖 |
|------|------|------|
| SQLiteOrderRepository | 订单落盘持久化 | SQLite execution_audit 表 |
| SQLitePositionSnapshotRepository | 持仓快照落盘 | SQLite positions 表 |
| PostgreSQLRepository | 生产级持久化 | PostgreSQL 基础设施 |
| 快照版本管理 | 按时间戳查询历史快照 | 时间索引 |

## 5. 依赖关系（depgraph 边）

| 方向 | 对端 | dep_type | 说明 |
|------|------|----------|------|
| → 出 | shared/contracts/order.py (CTR-004) | import_depends | Order 聚合根 |
| → 出 | shared/contracts/position.py (CTR-006) | import_depends | PositionSnapshot |
| → 出 | shared/contracts/enums/order_enums.py | import_depends | OrderStatus |
| → 出 | MOD-EX-002 (PositionTracker) | runtime | 仓储可供 PositionTracker 使用 |

## 6. API 契约

```python
class OrderRepository(ABC):
    """订单仓储接口——抽象持久化层。"""
    @abstractmethod
    def save(self, order: Order) -> None: ...
    @abstractmethod
    def get(self, order_id: str) -> Order | None: ...
    @abstractmethod
    def get_by_status(self, status: OrderStatus) -> list[Order]: ...
    @abstractmethod
    def get_open_orders(self) -> list[Order]: ...
    @abstractmethod
    def get_all(self) -> list[Order]: ...
    @abstractmethod
    def delete(self, order_id: str) -> bool: ...
    @abstractmethod
    def count(self) -> int: ...

class PositionSnapshotRepository(ABC):
    """持仓快照仓储接口——抽象持久化层。"""
    @abstractmethod
    def save(self, snapshot: PositionSnapshot) -> None: ...
    @abstractmethod
    def get_latest(self, portfolio_id: str) -> PositionSnapshot | None: ...
    @abstractmethod
    def get_all(self) -> list[PositionSnapshot]: ...
    @abstractmethod
    def delete(self, portfolio_id: str) -> bool: ...
    @abstractmethod
    def count(self) -> int: ...

class InMemoryOrderRepository(OrderRepository):
    """内存订单仓储——开发/测试用。"""
    ...

class InMemoryPositionSnapshotRepository(PositionSnapshotRepository):
    """内存持仓快照仓储——开发/测试用。"""
    ...
```

## 7. 实现方案

**设计原则**:
- 抽象层用 ABC（abstract base class），不依赖任何具体存储引擎
- 内存实现用 dict，线程安全用 threading.Lock（阶段1可选）
- 不做数据转换——直接存取 Order/PositionSnapshot 对象引用
- 仓储不负责业务逻辑（状态转换/校验等），只负责存取

**InMemoryOrderRepository**:
- `_orders: dict[str, Order]` — order_id → Order
- `get_open_orders()` 过滤 PENDING/SUBMITTED/PARTIAL 状态
- `save()` 幂等——相同 order_id 覆盖

**InMemoryPositionSnapshotRepository**:
- `_snapshots: dict[str, list[PositionSnapshot]]` — portfolio_id → 快照列表
- `get_latest()` 返回最新时间戳的快照
- `save()` 追加到列表（支持历史查询）

## 8. 测试计划

| 用例 | 覆盖点 |
|------|--------|
| 订单保存+查询 | save → get 返回同一对象 |
| 订单按状态查询 | get_by_status 过滤正确 |
| 开放订单查询 | get_open_orders 返回 PENDING/SUBMITTED/PARTIAL |
| 订单删除 | delete 后 get 返回 None |
| 订单覆盖保存 | 相同 order_id save 两次，get 返回最新 |
| 持仓快照保存+查询 | save → get_latest 返回最新 |
| 多版本快照 | 多次 save，get_latest 返回时间戳最大的 |
| 快照删除 | delete 后 get_latest 返回 None |
| 空仓储查询 | get/get_latest 返回 None/[] |
| count 统计 | save/delete 后 count 正确 |

## 9. 不变量 (INVARIANTS)

- OrderRepository 和 PositionSnapshotRepository 是 ABC，不可直接实例化
- InMemory 实现不做数据拷贝（存引用），调用方负责不可变性
- Decimal 用于所有金额/数量（由 Order/PositionSnapshot 契约保证）
- 仓储不负责业务校验（状态转换/权限等），只负责存取
- save 操作幂等（相同 ID 重复 save 不报错，覆盖旧值）

## 10. ID 映射表

| depgraph blueprint_id | 设计文档 ID | 功能 |
|----------------------|------------|------|
| MOD-EX-050 | D-EX-CORE-50 | 执行域仓储接口（本模块）|

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-050`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-050` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX-050` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-050 | MOD-EX-050 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

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


