---
module_id: MOD-EX-001
title: "部分成交处理器蓝图 — Fill累积+加权均价+状态转换+查询"
doc_type: blueprint
status: Active
version: "0.1.5"
design_maturity: production
ttl: permanent
responsibility_domain: 
---

# 部分成交处理器 (Fill Handler) — D-EX-CORE-48

> **优先级**: P1 | **成熟度**: production | **建设标记**: ✅可建
> **设计真源**: `D:\临时工作区\依赖图\08-D-EX-CORE-执行核心域.md` §1 D-EX-CORE-48
> **depgraph**: MOD-EX-001 (design/planned/can_build=1)

## 1. 大白话简介

部分成交处理器是"成交回报的账房先生"——每次券商回报一笔成交（Fill），它就累加到对应
订单上：更新已成交数量、重新计算加权均价、累计佣金、判断订单是否已全部成交。一笔大单
分3次成交，它就记3笔，最后算总账。任何时刻都能回答"这单成交了多少、还剩多少、均价多少"。

**为什么从 OrderManager 拆出？** 当前成交处理逻辑内嵌在 `OrderManager._on_fill()` 里
（lines 264-296），混在订单生命周期管理中。拆成独立模块后，未来 Fill Processor
（D-EX-CORE-08）可直接复用，不必经过 OrderManager，也便于独立测试成交累积逻辑。

## 2. ID 映射说明

depgraph `blueprint_id=MOD-EX-001` 对应设计文档 `D-EX-CORE-48`（ID 错位：depgraph 前4个
节点使用顺序编号，与设计文档功能编号不一致）。映射表见 §10。

## 3. 职责（阶段1 scope）

| 职责 | 说明 | 状态 |
|------|------|------|
| Fill 累积 | 每笔成交累加到 filled_quantity | ✅阶段1 |
| 加权均价 | new_avg = (old_avg×old_qty + fill_price×fill_qty) / new_qty | ✅阶段1 |
| 佣金累计 | 累加每笔 fill.commission | ✅阶段1 |
| 状态转换 | SUBMITTED→PARTIAL / SUBMITTED→FILLED / PARTIAL→FILLED | ✅阶段1 |
| 剩余量计算 | remaining = total - filled | ✅阶段1 |
| Fill 幂等 | 同一 fill_id 重复处理不重复累积 | ✅阶段1 |
| 成交历史 | 维护 order_id → list[Fill] | ✅阶段1 |
| 成交汇总查询 | FillSummary（总量/已成交量/剩余/均价/笔数/佣金/是否完成） | ✅阶段1 |

## 4. 阶段2扩展（本次不实现，记录防遗忘）

| 扩展 | 说明 | 依赖 |
|------|------|------|
| 成交归因器 | 区分主动成交/被动成交/算法成交 | TCA 基础设施 |
| 费用计算器 | 佣金/印花税/过户费分项计算 | 佣金费率表数据源 |
| T+1 结算合规 | 标记成交结算日，T+1 才可卖出 | A股交易规则引擎 |
| 成交延迟统计 | fill_timestamp - order.submit_timestamp | ExecutionEngine 集成 |

## 5. 依赖关系（depgraph 边）

| 方向 | 对端 | dep_type | 说明 |
|------|------|----------|------|
| ← 入 | MOD-TRADING-002 | import | 交易运营域引用 fill_handler |
| → 出 | shared/contracts/fill.py (CTR-005) | import_depends | 消费 Fill 契约 |
| → 出 | shared/contracts/order.py (CTR-004) | import_depends | 消费 Order 契约 |
| → 出 | shared/contracts/enums/order_enums.py | import_depends | 消费 OrderStatus 枚举 |

**跨域契约**:
- 消费: CTR-005 (Fill) ← D_EXECUTION_CORE
- 消费: CTR-004 (Order) ← D_PORTFOLIO_CORE

## 6. API 契约

```python
@dataclass(frozen=True)
class FillSummary:
    """成交汇总——不可变快照。"""
    order_id: str
    total_quantity: Decimal          # 订单总量
    filled_quantity: Decimal         # 累计成交量
    remaining_quantity: Decimal      # 剩余 = total - filled
    avg_fill_price: Decimal | None   # 加权平均成交价
    fill_count: int                  # 成交笔数
    total_commission: Decimal        # 累计佣金
    is_complete: bool                # filled >= total
    last_fill_timestamp: datetime | None

class FillHandler:
    """部分成交处理器——Fill 累积+加权均价+状态转换+查询。"""

    def process_fill(self, fill: Fill, order: Order) -> FillSummary:
        """处理一笔成交——更新订单成交状态，返回成交汇总。

        幂等: 同一 fill_id 重复调用不会重复累积。
        状态转换: 根据累积量判断 SUBMITTED→PARTIAL / →FILLED。
        """

    def get_summary(self, order_id: str) -> FillSummary | None:
        """获取订单的成交汇总（无成交返回 None）。"""

    def get_fills(self, order_id: str) -> list[Fill]:
        """获取订单的成交历史（按时间顺序）。"""

    def get_remaining(self, order_id: str) -> Decimal | None:
        """获取订单的剩余未成交数量。"""

    def register_callback(
        self, callback: Callable[[Fill, FillSummary], None]
    ) -> None:
        """注册成交回调——每次 process_fill 后同步调用。"""

    @property
    def order_count(self) -> int: ...
    @property
    def total_fill_count(self) -> int: ...
```

## 7. 实现方案（从 OrderManager._on_fill 拆出）

**提取逻辑**（OrderManager._on_fill → FillHandler.process_fill）:

| OrderManager._on_fill | FillHandler.process_fill |
|----------------------|------------------------|
| `self._fills[order_id].append(fill)` | `self._fills[order_id].append(fill)` |
| `order.filled_quantity += fill.filled_quantity` | 同左 |
| `order.avg_fill_price = weighted_avg(...)` | 同左（提取为 `_compute_avg_price`） |
| `order.updated_at = now()` | 同左 |
| `if filled >= qty: →FILLED` | 同左 + 幂等检查 |
| `elif filled > 0: →PARTIAL` | 同左 |
| `for cb in self._fill_callbacks: cb(fill)` | `cb(fill, summary)` — 传 FillSummary |

**新增能力**（OrderManager._on_fill 没有的）:
- `fill_id` 幂等检查（防重复处理同一笔成交）
- `remaining_quantity` 计算
- `total_commission` 累计
- `FillSummary` 不可变快照
- `fill_count` 统计
- `last_fill_timestamp` 追踪

**不改动 OrderManager**: 本阶段 FillHandler 作为独立模块存在，OrderManager 保持不变。
后续 Fill Processor（D-EX-CORE-08）可直接使用 FillHandler。

**加权均价算法**:
```
new_avg = (old_avg × old_filled_qty + fill_price × fill_qty) / new_filled_qty
```
使用 Decimal 全程计算，禁止 float。

## 8. 测试计划

| 用例 | 覆盖点 |
|------|--------|
| 单笔全部成交 | filled=total, status→FILLED, avg=fill_price |
| 单笔部分成交 | filled<total, status→PARTIAL, remaining>0 |
| 多笔累积成交 | 3笔累积, avg 加权正确, fill_count=3 |
| 多笔后全部成交 | 最后1笔补齐, status→FILLED |
| 幂等：重复 fill_id | 第2次调用不累积, summary 不变 |
| 佣金累计 | total_commission = sum(各笔 commission) |
| 剩余量计算 | remaining = total - filled |
| 成交历史查询 | get_fills 返回按顺序的 Fill 列表 |
| 汇总查询 | get_summary 返回正确的 FillSummary |
| 回调通知 | register_callback 后每次 process_fill 触发 |
| 零数量成交 | raise ValueError |
| 未知订单 | process_fill 对 order_id 不匹配的 fill raise |
| over-fill | filled > total → 标记 is_complete=True + 日志警告 |

## 9. 不变量 (INVARIANTS)

- FillSummary 是 frozen dataclass，跨层传递时不可变
- Decimal 用于所有金额/数量计算，禁止 float
- fill_id 全局唯一，重复 process_fill 幂等（不重复累积）
- filled_quantity 单调递增（只增不减）
- 状态转换遵循 OrderManager.VALID_TRANSITIONS 规则
- Order 对象就地更新（Order 是 frozen=false 的可变 dataclass）

## 10. ID 映射表 (MOD-EX-XXX ↔ D-EX-CORE-XX)

depgraph 前4个节点使用顺序编号，与设计文档功能编号错位：

| depgraph blueprint_id | 设计文档 ID | 功能 | 说明 |
|----------------------|------------|------|------|
| **MOD-EX-001** | **D-EX-CORE-48** | **部分成交处理 (fill_handler)** | **本模块** |
| MOD-EX-002 | D-EX-CORE-04 | Position Tracker | 顺序编号≠功能编号 |
| MOD-EX-003 | D-EX-CORE-15 | Execution Auditor (audit_journal) | 顺序编号≠功能编号 |
| MOD-EX-004 | INV-007 | Redis 幂等性 (redis_idempotency) | 跨模块基础设施 |
| MOD-EX-008+ | D-EX-CORE-08+ | 对齐 | 从008起编号一致 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-001` 的 16 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX-001` |
| 数据流图 (dataflow) | 1 个 Dataset / 2 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-001 | MOD-EX-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 16 文件 | N/A | — |

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
| `src/zephyr/ex_core/daban_exit_decision.py` | ✅ 已实现 | |
| `src/zephyr/ex_core/daban_instant_circuit_breaker.py` | ✅ 已实现 | |
| `src/zephyr/ex_core/daban_monitors.py` | ✅ 已实现 | |
| `src/zephyr/ex_core/daban_named_functions.py` | ✅ 已实现 | |
| `src/zephyr/ex_core/daban_pit_safety.py` | ✅ 已实现 | |
| `src/zephyr/ex_core/daban_signal_decision.py` | ✅ 已实现 | |
| `src/zephyr/ex_core/fill_handler.py` | ✅ 已实现 | |

### 11.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/ex_core/test_async_fill_dispatcher.py` | ✅ 已实现 | |
| `tests/ex_core/test_corporate_action_adjuster.py` | ✅ 已实现 | |
| `tests/ex_core/test_execution_auditor.py` | ✅ 已实现 | |
| `tests/ex_core/test_fill_id_dedup_persistence.py` | ✅ 已实现 | |
| `tests/ex_core/test_open_order_resolver.py` | ✅ 已实现 | |
| `tests/ex_core/test_order_execution_saga.py` | ✅ 已实现 | |
| `tests/ex_core/test_pricing_policy.py` | ✅ 已实现 | |
| `tests/ex_core/test_programmatic_trading_guard.py` | ✅ 已实现 | |
| `tests/ex_core/test_trading_halt_resolver.py` | ✅ 已实现 | |

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


