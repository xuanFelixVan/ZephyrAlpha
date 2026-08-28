---
module_id: MOD-EX-057
title: "下单执行Saga编排器蓝图 — 六步编排+补偿+超时+状态机"
doc_type: blueprint
status: Active
version: "0.1.6"
design_maturity: production
ttl: permanent
responsibility_domain: 
---

# 下单执行 Saga 编排器 (Order Execution Saga) — D-EX-CORE-57

> **优先级**: P0 | **成熟度**: production | **建设标记**: ✅可建
> **设计真源**: `D:\临时工作区\依赖图\08-D-EX-CORE-执行核心域.md` §13 下单执行Saga编排
> **depgraph**: MOD-EX-057 (production/testing/can_build=1)

## 1. 大白话简介

Saga 编排器是"单笔订单的事务经理"——每一笔订单从风控检查到报告生成，走六步标准流程。
任何一步失败，自动执行补偿操作（撤单/回滚），保证系统不会处于"半完成"的不一致状态。
≤5 秒超时硬约束，超时自动撤单。

**为什么需要 Saga？** 普通 execution 直接调 OrderManager 提交订单，如果提交后系统崩溃，
订单可能挂在交易所但本地持仓没更新——数据不一致。Saga 模式把六步封装成一个事务，
失败时按补偿表回滚，保证最终一致。

**与 TradingSession 的关系**：TradingSession 是"盘中会话编排器"（信号→策略→权重→订单批量），
Saga 是"单笔订单事务经理"（风控→提交→成交→持仓→报告+补偿）。TradingSession 可以对每笔
订单调用 Saga.execute() 获得事务保证。粒度不同，互补不替代。

**纯基础设施**：Saga 不决定"买什么/何时买/买多少"——这些由策略域和风控域决定。Saga 只负责
"按顺序执行六步，失败就补偿回滚"。

## 2. 职责（阶段1 scope）

| 职责 | 说明 | 状态 |
|------|------|------|
| 六步编排 | 风控→信号→下单→成交→持仓→报告，严格顺序 | ✅阶段1 |
| 补偿回滚 | 步骤3失败→撤单；步骤5失败→持仓回滚 | ✅阶段1 |
| 超时硬约束 | ≤5s（可配），超时→撤单+标记TIMEOUT | ✅阶段1 |
| 幂等补偿 | 撤单如已成交→忽略；持仓回滚如已更新→覆盖 | ✅阶段1 |
| 状态机追踪 | 每步完成后更新 SagaState，产出 SagaResult | ✅阶段1 |
| 审计集成 | 每步结果记入 ExecutionAuditLogger 哈希链 | ✅阶段1 |
| 线程安全 | 多笔 Saga 可并发执行（每笔独立状态） | ✅阶段1 |

## 3. 阶段2扩展（本次不实现，记录防遗忘）

| 扩展 | 说明 | 依赖 |
|------|------|------|
| Redis Stream 状态持久化 | 每步状态写 Redis Stream，故障恢复断点续传 | Redis 基础设施 |
| 部分成交处理 | 部分 fill → 已成交部分入持仓，未成交部分撤单 | EX-048 fill_handler |
| 跨会话恢复 | 进程重启后从 Redis Stream 恢复未完成 Saga | Redis + 启动钩子 |
| 实时告警 | 超时/补偿/失败实时告警 D-L1 | 告警通道 |
| T+1 不可逆补偿 | 买入腿已成交不可回滚（T+1 约束） | IMM-005 |

## 4. Saga 六步编排（设计真源 §13）

| 步骤 | 操作 | 调用 | 失败补偿 |
|:----:|------|------|---------|
| 1 | 风控检查 | risk_validator.validate_order() | 无需补偿（检查操作） |
| 2 | 信号确认 | signal_confirmer(order)（可选，None=跳过） | 无需补偿（确认操作） |
| 3 | 下单提交 | order_manager.create_order()+submit_order() | 撤单 cancel_order() |
| 4 | 成交确认 | 等待 Fill 回调（Event+timeout） | 无需补偿（被动等待，超时→步骤3补偿） |
| 5 | 持仓更新 | position_tracker.apply_fill(fill, side) | 持仓回滚（反向 apply_fill） |
| 6 | 报告生成 | audit_logger.log_order_filled() 等 | 标记报告待更新（异步，best-effort） |

### 补偿幂等规则

- **撤单幂等**：cancel_order() 如订单已 FILLED → 返回 False（忽略），已 CANCELLED → 返回 False（忽略）
- **持仓回滚幂等**：如持仓已更新 → 用反向 fill 覆盖（买入回滚=卖出同量，卖出回滚=买入同量）

### 超时约束

- 总 Saga 超时 ≤5s（可配 SagaConfig.timeout_seconds）
- 超时后：取消未成交订单 → 标记 TIMEOUT → 如有部分成交则入持仓（阶段2）
- 阶段1：超时 = 无成交，直接撤单

## 5. 依赖关系

| 方向 | 对端 | dep_type | 说明 |
|------|------|----------|------|
| ← 入 | MOD-EX-002 (Execution Engine / OrderManager) | runtime | 订单创建/提交/撤单 |
| ← 入 | RiskValidationPort (risk_validation_bridge) | runtime | 风控检查 |
| ← 入 | MOD-EX-002 (PositionTracker) | runtime | 持仓更新/回滚 |
| ← 入 | MOD-EX-003 (ExecutionAuditLogger) | event | 审计记录 |
| ← 入 | BrokerInterface | runtime | 券商接口（fill 回调） |

**跨域契约**:
- 消费: CTR-004 (Order), CTR-005 (Fill), RiskLimits, RiskViolation
- 产出: E-EX-01~08 (执行事件 → ExecutionAuditLogger)

## 6. API 契约

```python
class SagaState(str, Enum):
    """Saga 状态机。"""
    INIT = "INIT"
    RISK_PASSED = "RISK_PASSED"
    SIGNAL_CONFIRMED = "SIGNAL_CONFIRMED"
    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    FILL_RECEIVED = "FILL_RECEIVED"
    POSITION_UPDATED = "POSITION_UPDATED"
    COMPLETED = "COMPLETED"
    # 失败/补偿状态
    RISK_REJECTED = "RISK_REJECTED"
    SIGNAL_INVALID = "SIGNAL_INVALID"
    ORDER_REJECTED = "ORDER_REJECTED"
    TIMEOUT = "TIMEOUT"
    COMPENSATED = "COMPENSATED"

@dataclass(frozen=True)
class SagaResult:
    """单笔 Saga 执行结果（不可变）。"""
    saga_id: str
    order_id: str
    symbol: str
    side: str
    state: SagaState
    steps_completed: tuple[str, ...]
    fill: Fill | None
    error: str | None
    compensated: bool
    started_at: datetime
    completed_at: datetime
    duration_ms: float

@dataclass
class SagaConfig:
    """Saga 配置。"""
    timeout_seconds: float = 5.0
    fill_poll_interval: float = 0.05

class OrderExecutionSaga:
    """下单执行 Saga 编排器 — 六步编排 + 补偿 + 超时。"""

    def __init__(
        self,
        order_manager: OrderManager,
        risk_validator: RiskValidationPort,
        position_tracker: PositionTracker,
        audit_logger: ExecutionAuditLogger,
        broker: BrokerInterface,
        broker_id: str = "simulation",
        risk_limits: RiskLimits | None = None,
        config: SagaConfig | None = None,
        signal_confirmer: Callable[[Order], bool] | None = None,
    ) -> None: ...

    def execute(self, order: Order, side: OrderSide) -> SagaResult:
        """执行单笔订单的 Saga 六步流程（同步，阻塞至完成或超时）。"""
        ...
```

## 7. 实现方案

### Fill 等待机制

使用 `_FillCollector` 内部类（线程安全 Event + 一次性回调）：
1. 注册 fill callback（捕获指定 order_id 的 fill）
2. 提交订单（SimulationBroker 同步触发 fill；实盘异步）
3. Event.wait(remaining_timeout) 等待 fill
4. 收到 fill → 步骤5；超时 → 补偿撤单

### 补偿执行

```python
def _compensate_order(self, order, ctx):
    """步骤3补偿：撤单（幂等）。"""
    if order.status in {OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL}:
        self._order_manager.cancel_order(order.order_id)
        self._audit.log_order_cancelled(order.order_id, order.symbol, {"reason": "saga_compensate"})

def _compensate_position(self, fill, side, ctx):
    """步骤5补偿：持仓回滚（反向 apply_fill，幂等）。"""
    reverse_fill = _make_reverse_fill(fill)  # 同价同量，反方向
    reverse_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
    self._position_tracker.apply_fill(reverse_fill, reverse_side)
```

### 状态机流转

```
INIT
  ↓ step1: risk_check
RISK_PASSED ──(fail)──→ RISK_REJECTED (终止)
  ↓ step2: signal_confirm
SIGNAL_CONFIRMED ──(fail)──→ SIGNAL_INVALID (终止)
  ↓ step3: order_submit
ORDER_SUBMITTED ──(fail)──→ ORDER_REJECTED (终止)
  ↓ step4: fill_confirm (timeout)
FILL_RECEIVED ──(timeout)──→ TIMEOUT → compensate → COMPENSATED
  ↓ step5: position_update
POSITION_UPDATED ──(fail)──→ compensate_position → COMPENSATED
  ↓ step6: report
COMPLETED
```

## 8. 测试计划

| 用例 | 覆盖点 |
|------|--------|
| 完整成功流程 | 六步全过，state=COMPLETED，fill 非 None |
| 风控拒绝 | step1 fail，state=RISK_REJECTED，无下单 |
| 信号失效 | step2 fail，state=SIGNAL_INVALID，无下单 |
| 下单被拒 | step3 fail，state=ORDER_REJECTED |
| 成交超时 | step4 timeout，state=TIMEOUT+COMPENSATED，撤单 |
| 持仓更新失败 | step5 fail，state=COMPENSATED，持仓回滚 |
| 补偿撤单幂等 | 已成交订单撤单返回 False（忽略） |
| 补偿持仓回滚 | 反向 fill 恢复持仓 |
| 超时配置 | custom timeout 生效 |
| 审计记录 | 每步事件记入 ExecutionAuditLogger |
| 并发安全 | 多笔 Saga 并发执行 |
| SagaResult 不可变 | frozen dataclass 验证 |
| 信号确认跳过 | signal_confirmer=None 时跳过 step2 |

## 9. 不变量 (INVARIANTS)

- SagaResult 是 frozen dataclass，跨层传递不可变
- ≤5s 超时硬约束（可配但不超过交易所限制）
- 补偿操作幂等：重复执行不产生副作用
- 每笔 Saga 独立状态，互不影响（无共享可变状态）
- 审计记录不可跳过：每个状态转换 MUST 记入 ExecutionAuditLogger
- execute() 是同步阻塞调用，调用方需自行异步化（如 ThreadPoolExecutor）

## 10. ID 映射

depgraph `blueprint_id=MOD-EX-057` 对应设计文档 `D-EX-CORE-57`（编号一致）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-057`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-057` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX-057` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-057 | MOD-EX-057 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 11. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 11.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/ex_core/test_saga_timeout_recovery.py` | ✅ 已实现 | |

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


