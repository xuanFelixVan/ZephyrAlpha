---
module_id: MOD-POS-009
title: "仓位审计记录器蓝图 — 全记录+哈希链+可追溯"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-009 Position Audit Logger — 仓位审计记录器 蓝图

> **module_id**: MOD-POS-009 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P1 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-009 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.3 POS-09

## 1. 定位

仓位审计记录器——D_POSITION 域的**审计基础设施**，监听仓位变更事件
(E-POS-01/02/03/05)，全量记录每笔仓位变更，通过哈希链保证记录不可篡改，
支持按标的/时间/事件类型追溯，定期或按需生成仓位审计报告。

属 **A 类基础设施模块**(事件监听+记录+查询+报告)，不含任何策略决策逻辑。
审计字段格式、哈希链算法、报告模板均为确定性规则。

**边界**: 不决定仓位(决策由 POS-001 承接)；不执行交易(执行由 D-EX-CORE 承接)；
不触发风控(风控由 D-RISK 承接)。本模块是"仓位变更的记录者"，不是"仓位决策的参与者"。

**与 D_GOV_AUDIT 的关系**: 本模块专注 D_POSITION 域内仓位变更审计；
D_GOV_AUDIT (MOD-INF-020) 是跨域审计链基础设施。两者互补不重叠——
POS-009 产出 PositionAuditRecord，可被 D_GOV_AUDIT 审计链引用。

## 2. 输入 / 输出

### 2.1 输入

| 方向 | 内容 | 事件/契约 | 来源 | 就绪 |
|------|------|-----------|------|:----:|
| 事件 | PositionSized(仓位决策完成) | E-POS-01 | POS-001 | ✅stable |
| 事件 | DriftDetected(持仓漂移) | E-POS-02 | POS-003 | ✅stable |
| 事件 | RebalanceTriggered(再平衡指令) | E-POS-03 | POS-004 | ✅stable |
| 事件 | StateChanged(持仓状态变更) | E-POS-05 | POS-002 | ✅stable |
| 公共 | PositionSnapshot(当前持仓快照) | CTR-006 | D-EX-CORE | ⚠️部分 |

### 2.2 输出

| 方向 | 内容 | 去往 |
|------|------|------|
| 记录 | PositionAuditRecord(仓位审计记录) | 内部存储(append-only + hash chain) |
| 报告 | PositionAuditReport(仓位审计报告) | D-REPORTING, D-GOVERNANCE |

### 2.3 事件订阅方式

POS-001 (PositionSizingEngine) 通过 `size()` 方法返回 PositionSizingPlan，
不使用 listener 模式。POS-009 通过 **直接方法调用** 接收:

```python
logger.log_position_sized(plan: PositionSizingPlan)
```

POS-002/003/004 使用 `add_listener(callback)` + `_emit(event)` 模式。
POS-009 通过 **注册 listener** 接收:

```python
state_machine.add_listener(logger.on_state_changed)
drift_monitor.add_listener(logger.on_drift_detected)
rebalance_engine.add_listener(logger.on_rebalance_triggered)
```

## 3. 数据模型

### 3.1 AuditEventType 枚举

| 值 | 对应事件 | 来源模块 |
|----|---------|---------|
| `POSITION_SIZED` | E-POS-01 | POS-001 |
| `DRIFT_DETECTED` | E-POS-02 | POS-003 |
| `REBALANCE_TRIGGERED` | E-POS-03 | POS-004 |
| `STATE_CHANGED` | E-POS-05 | POS-002 |

### 3.2 AuditSource 枚举 (审批链来源)

| 值 | 说明 |
|----|------|
| `AUTO` | 系统自动决策(POS-001 Kelly/约束裁决) |
| `MANUAL` | 人工调仓指令(轨道3) |
| `EMERGENCY` | 应急保命模式(轨道4) |
| `REBALANCE` | 再平衡触发(POS-004) |
| `DRIFT` | 漂移检测触发(POS-003) |

### 3.3 PositionAuditRecord

```python
@dataclass(frozen=True)
class PositionAuditRecord:
    """仓位审计记录——单条不可变记录, 哈希链节点。"""

    record_id: str           # UUID, 唯一标识
    timestamp: datetime      # 记录时间(UTC)
    event_type: AuditEventType  # 事件类型
    symbol: str              # 标的代码(portfolio级事件用 "*")
    source: AuditSource      # 变更来源(审批链)
    detail: dict[str, Any]   # 事件详情(事件特定字段)
    prev_hash: str           # 上一条记录的 hash (首条为 "0"*64)
    record_hash: str         # 本条记录的 hash (SHA-256)
```

**detail 字段按事件类型**:

| event_type | detail 内容 |
|------------|------------|
| POSITION_SIZED | plan_id, strategy_id, total_exposure, symbols, degraded |
| DRIFT_DETECTED | scope, drift_pct, threshold, actual_weight, target_weight |
| REBALANCE_TRIGGERED | trigger, should_rebalance, cost_estimate, benefit_estimate |
| STATE_CHANGED | from_state, to_state, reason |

### 3.4 PositionAuditReport

```python
@dataclass(frozen=True)
class PositionAuditReport:
    """仓位审计报告——定期或按需生成的摘要。"""

    report_id: str            # UUID
    period_start: datetime    # 报告周期起始
    period_end: datetime      # 报告周期结束
    total_records: int        # 总记录数
    by_event_type: dict[str, int]  # 按事件类型统计
    by_symbol: dict[str, int]      # 按标的统计
    by_source: dict[str, int]      # 按来源统计
    chain_valid: bool         # 哈希链完整性校验结果
    chain_break_at: str | None  # 断链位置(None=无断链)
    generated_at: datetime    # 报告生成时间
```

## 4. 核心约束

| # | 约束 | 说明 | 阶段 |
|---|------|------|:----:|
| C1 | 全记录 | 每笔仓位变更事件 MUST 记录, 不可跳过 | 阶段1 |
| C2 | 哈希链 | record_hash = SHA-256(record_id + timestamp + event_type + symbol + source + detail + prev_hash), 防篡改 | 阶段1 |
| C3 | 链完整性 | 首条 prev_hash = "0"*64; 后续 prev_hash = 上一条 record_hash | 阶段1 |
| C4 | 不可变 | PositionAuditRecord 为 frozen dataclass, 建立后不可修改 | 阶段1 |
| C5 | 异常不阻断 | listener 异常仅记录日志, 不阻断事件发布方主流程 | 阶段1 |
| C6 | 审批链追溯 | 每条记录 MUST 标注 source(来源), 支持按来源过滤 | 阶段1 |
| C7 | 按需查询 | 支持按 symbol / event_type / time_range 查询历史记录 | 阶段1 |
| C8 | 报告生成 | 支持 generate_report(period_start, period_end) 生成审计报告 | 阶段1 |

## 5. 哈希链算法

```
record_hash = SHA-256(
    record_id      |  # UUID
    timestamp      |  # ISO 8601 UTC
    event_type     |  # 枚举值
    symbol         |  # 标的代码
    source         |  # 来源枚举值
    detail_json    |  # detail 字段的 canonical JSON (sort_keys=True)
    prev_hash        # 上一条 record_hash
)
```

**链完整性校验**:
1. 首条记录 prev_hash == "0"*64
2. 每条 record_hash == 重算结果
3. 每条 prev_hash == 上一条 record_hash
4. 任一条件不满足 → chain_valid=False, chain_break_at=该记录 record_id

## 6. 降级模式

| 场景 | 降级行为 |
|------|---------|
| 存储写入失败 | 记录保留在内存, 标记 `persist_failed=True`, 告警 |
| 哈希计算异常 | 使用 fallback hash (record_id 本身), 标记 `hash_degraded=True` |
| listener 异常 | 仅记录日志, 不阻断事件发布方 (C5) |

降级记录在报告中单独标注, 不混入正常记录统计。

## 7. 接口定义

### 7.1 PositionAuditLogger 类

```python
class PositionAuditLogger:
    """仓位审计记录器——监听事件 + 全记录 + 哈希链 + 报告。"""

    def __init__(self, persist_path: Path | None = None) -> None: ...

    # ── 事件接收 (listener 接口) ──
    def on_state_changed(self, event: StateChangedEvent) -> None: ...
    def on_drift_detected(self, event: DriftDetectedEvent) -> None: ...
    def on_rebalance_triggered(self, event: RebalanceTriggeredEvent) -> None: ...

    # ── 直接调用 (POS-001 不用 listener) ──
    def log_position_sized(self, plan: PositionSizingPlan) -> None: ...

    # ── 查询 ──
    def query(
        self,
        symbol: str | None = None,
        event_type: AuditEventType | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[PositionAuditRecord]: ...

    # ── 报告 ──
    def generate_report(
        self, period_start: datetime, period_end: datetime
    ) -> PositionAuditReport: ...

    # ── 哈希链校验 ──
    def verify_chain(self) -> tuple[bool, str | None]: ...

    # ── 持久化 ──
    def flush(self) -> None: ...  # 写入 JSON 文件 (可选)
```

### 7.2 注册方式

```python
# 在编排层注册 POS-009 为各模块的 listener
logger = PositionAuditLogger(persist_path=Path("data/audit/position_audit.jsonl"))

state_machine.add_listener(logger.on_state_changed)
drift_monitor.add_listener(logger.on_drift_detected)
rebalance_engine.add_listener(logger.on_rebalance_triggered)

# POS-001 直接调用 (在 size() 返回后)
plan = sizing_engine.size(inp)
logger.log_position_sized(plan)
```

## 8. 阶段规划

| 阶段 | 内容 | 阶段2(排除) |
|------|------|------------|
| 阶段1 | 内存 append-only + 哈希链 + 查询 + 报告 + JSONL 持久化 | — |
| 阶段2 | 接入 D_GOV_AUDIT 审计链; SQLite 持久化; 实时告警 | 显式排除 |

## 9. 依赖关系

| 依赖 | 类型 | 就绪 |
|------|------|:----:|
| POS-001 PositionSizingPlan | 直接调用 | ✅ |
| POS-002 StateChangedEvent | listener | ✅ |
| POS-003 DriftDetectedEvent | listener | ✅ |
| POS-004 RebalanceTriggeredEvent | listener | ✅ |
| zephyr.shared.foundation.errors | import | ✅ |

## 10. 测试策略

| 测试 | 内容 |
|------|------|
| test_log_position_sized | 记录 PositionSized 事件, 验证字段完整性 |
| test_log_state_changed | 记录 StateChanged 事件, 验证 listener 接口 |
| test_log_drift_detected | 记录 DriftDetected 事件 |
| test_log_rebalance_triggered | 记录 RebalanceTriggered 事件 |
| test_hash_chain | 验证哈希链连续性 + 篡改检测 |
| test_verify_chain | 验证链完整性校验(正常 + 断链) |
| test_query_filter | 验证按 symbol/event_type/time 过滤查询 |
| test_generate_report | 验证报告统计正确性 |
| test_listener_exception | 验证 listener 异常不阻断主流程 (C5) |
| test_persist_jsonl | 验证 JSONL 持久化 + 加载 |
| test_frozen_record | 验证 PositionAuditRecord 不可变 (C4) |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-009`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-009` 的 9 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-009` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-009 | MOD-POS-009 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 9 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 11. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 11.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/position/test_position_state_machine.py` | ✅ 已实现 | |

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


