---
module_id: MOD-EX-003
title: "执行审计器蓝图 — 执行事件哈希链审计日志+报告"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
ttl: permanent
responsibility_domain: 
---

# 执行审计器 (Execution Auditor) — D-EX-CORE-15

> **优先级**: P1 | **成熟度**: production | **建设标记**: ✅可建
> **设计真源**: `D:\临时工作区\依赖图\08-D-EX-CORE-执行核心域.md` §1 D-EX-CORE-15
> **depgraph**: MOD-EX-003 (production/testing/can_build=1)
> **模式复用**: 对齐 MOD-POS-009 PositionAuditLogger（哈希链审计日志同构模式）

## 1. 大白话简介

执行审计器是"交易系统的黑匣子记录仪"——每一笔订单从创建、提交、成交、撤销、被拒、过期，
到幂等性拦截，全部记进一条不可篡改的哈希链日志。任何时刻能查某个订单的完整生命周期，
也能生成审计报告核对链完整性。出问题时（合规检查、故障复盘、纠纷举证），这是唯一可信的证据源。

**为什么需要哈希链？** 普通日志能被悄悄改掉（删一条、改一个数）。哈希链每条记录的 hash 依赖上一条，
改任何一条都会让后续全部 hash 对不上——篡改即被发现。这是 MiFID II / SEC 17a-4 要求的"不可篡改审计 trail"的工程实现。

**与 POS-009 的关系**：POS-009 审计"仓位变更"（D_POSITION 域），EX-15 审计"执行事件"（D_EX_CORE 域）。
两者同构（哈希链 + frozen record + query/report/verify），但事件类型、来源、消费方不同，各自独立。

## 2. 职责（阶段1 scope）

| 职责 | 说明 | 状态 |
|------|------|------|
| 执行事件全记录 | E-EX-01~08 八类事件全部入链，不可跳过 | ✅阶段1 |
| 哈希链防篡改 | SHA-256 链：record_hash 依赖 prev_hash，篡改即断裂 | ✅阶段1 |
| frozen record | ExecutionAuditRecord 不可变，跨层传递安全 | ✅阶段1 |
| 按条件查询 | 按 order_id / symbol / event_type / 时间范围查 | ✅阶段1 |
| 审计报告 | 统计摘要（按事件/标的/来源）+ 链完整性校验 | ✅阶段1 |
| 链完整性校验 | verify_chain() 重算所有 hash，检测断链/篡改 | ✅阶段1 |
| JSONL 持久化 | flush/load 落盘重启恢复（best-effort） | ✅阶段1 |
| listener 异常隔离 | 记录失败不阻断执行主流程（catch + log） | ✅阶段1 |

## 3. 阶段2扩展（本次不实现，记录防遗忘）

| 扩展 | 说明 | 依赖 |
|------|------|------|
| 合规规则引擎 | MiFID II 交易记录 / SEC 17a-4 合规校验 | 合规规则库 |
| 执行质量评分器 | 执行质量打分（成功率/延迟/滑点） | TCA（MOD-EX-012）就绪 |
| 7年保留策略 | 审计日志归档 + 7年保留（合规要求） | 归档存储基础设施 |
| 证据链 DAG | 数据指纹→因子→信号→策略→仓位→订单指纹（TC≥0.997） | 全链路 trace_context |
| SQLite 持久化 | 替代 JSONL，支持高效查询 | SQLite execution_audit 表 |
| 实时告警 | 异常事件（高频拒绝/撤单率飙升）实时告警 | 告警通道 |

> **G6 薄聚合层落地（2026-08-05）**：失败率 + 成交延迟统计已实现为 `compute_operational_risk_stats()`（见 §5），
> 作为 G6 / BM-RC-08-E 操作风险审计的聚合基础。失败率 = ORDER_REJECTED/ORDER_SUBMITTED，
> 延迟 = SUBMITTED→FILLED 时间差（ms），纯派生统计不依赖 TCA。**仍待 TCA**：执行质量/滑点评分；
> **仍待 D_RISK 解释层**：阈值告警/风险解释（battle_map 真源由 MOD-INF-023/029 承载广义操作风险概念）。

## 4. 依赖关系（depgraph 设计态边）

| 方向 | 对端 | dep_type | 说明 |
|------|------|----------|------|
| ← 入 | MOD-EX-001 (fill_handler / order_manager) | event | 订单生命周期事件（E-EX-01/02/03/05/06/07） |
| ← 入 | MOD-EX-004 (redis_idempotency) | event | 幂等性拦截事件（E-EX-08） |

**跨域契约**:
- 消费: ExecutionEvent（E-EX-01~08，域内事件）
- 产出: ExecutionAuditReport → D_REPORTING（审计报告）/ D_GOVERNANCE（合规消费）

## 5. API 契约

```python
class ExecutionAuditEventType(str, Enum):
    """执行审计事件类型（对应 E-EX-01~08）。"""
    ORDER_CREATED = "ORDER_CREATED"            # E-EX-01
    ORDER_SUBMITTED = "ORDER_SUBMITTED"        # E-EX-02
    ORDER_FILLED = "ORDER_FILLED"              # E-EX-03
    FILL_RECEIVED = "FILL_RECEIVED"            # E-EX-04
    ORDER_CANCELLED = "ORDER_CANCELLED"        # E-EX-05
    ORDER_REJECTED = "ORDER_REJECTED"          # E-EX-06
    ORDER_EXPIRED = "ORDER_EXPIRED"            # E-EX-07
    IDEMPOTENCY_BLOCKED = "IDEMPOTENCY_BLOCKED"  # E-EX-08

class AuditSource(str, Enum):
    """执行事件来源（审批链）。"""
    AUTO = "AUTO"              # 系统自动执行
    SIMULATION = "SIMULATION"  # 模拟盘
    LIVE = "LIVE"              # 实盘
    MANUAL = "MANUAL"          # 人工干预

@dataclass(frozen=True)
class ExecutionAuditRecord:
    """单条执行审计记录（哈希链节点，不可变）。"""
    record_id: str
    timestamp: datetime
    event_type: ExecutionAuditEventType
    order_id: str
    symbol: str
    source: AuditSource
    detail: dict[str, Any]
    prev_hash: str
    record_hash: str

@dataclass(frozen=True)
class ExecutionAuditReport:
    """执行审计报告（统计摘要 + 链完整性）。"""
    report_id: str
    period_start: datetime
    period_end: datetime
    total_records: int
    by_event_type: dict[str, int]
    by_symbol: dict[str, int]
    by_source: dict[str, int]
    chain_valid: bool
    chain_break_at: str | None
    generated_at: datetime

@dataclass(frozen=True)
class OperationalRiskStats:
    """操作风险统计——失败率 + 成交延迟聚合（G6 / BM-RC-08-E 薄聚合层，纯派生统计）。"""
    period_start: datetime
    period_end: datetime
    submission_count: int
    rejection_count: int
    filled_count: int
    failure_rate: float          # rejection/submission ∈ [0,1]，无提交=0.0
    fill_rate: float             # filled/submission ∈ [0,1]
    latency_count: int           # 成功配对 SUBMITTED→FILLED 的订单数
    latency_p50_ms: float
    latency_p95_ms: float
    latency_max_ms: float
    latency_mean_ms: float
    generated_at: datetime

class ExecutionAuditLogger:
    """执行审计记录器 — 全记录 + 哈希链防篡改 + 查询/报告。"""

    def __init__(self, persist_path: Path | str | None = None) -> None: ...

    # 通用记录入口
    def log(self, event_type, order_id, symbol, source, detail, timestamp=None) -> ExecutionAuditRecord: ...

    # 便捷方法（每类事件一个）
    def log_order_created(self, order_id, symbol, detail, source=AuditSource.AUTO): ...
    def log_order_submitted(self, order_id, symbol, detail, source=AuditSource.AUTO): ...
    def log_order_filled(self, order_id, symbol, detail, source=AuditSource.AUTO): ...
    def log_fill_received(self, order_id, symbol, detail, source=AuditSource.AUTO): ...
    def log_order_cancelled(self, order_id, symbol, detail, source=AuditSource.AUTO): ...
    def log_order_rejected(self, order_id, symbol, detail, source=AuditSource.AUTO): ...
    def log_order_expired(self, order_id, symbol, detail, source=AuditSource.AUTO): ...
    def log_idempotency_blocked(self, order_id, symbol, detail, source=AuditSource.AUTO): ...

    # 查询 / 报告 / 校验 / 持久化
    def query(self, order_id=None, symbol=None, event_type=None, start=None, end=None) -> list[ExecutionAuditRecord]: ...
    def generate_report(self, period_start, period_end) -> ExecutionAuditReport: ...
    def compute_operational_risk_stats(self, period_start, period_end) -> OperationalRiskStats: ...
    def verify_chain(self) -> tuple[bool, str | None]: ...
    def flush(self) -> None: ...
    def load(self) -> None: ...
```

## 6. 实现方案（对齐 POS-009 同构模式）

**哈希链算法**（与 POS-009 一致）:
```
record_hash = SHA-256(record_id | timestamp | event_type | order_id | symbol | source | detail_json | prev_hash)
```
首条 prev_hash = ZERO_HASH ("0"*64)。

**记录流程**:
1. log() 调用 → 取 last_hash 作为 prev_hash
2. 计算 record_hash（SHA-256，JSON canonical 序列化）
3. 构造 ExecutionAuditRecord（frozen）追加到链尾
4. 返回 record

**链校验**:
- 遍历所有记录，检查 prev_hash 链接连续
- 重算每条 record_hash，比对存储值（检测篡改）
- 断链返回 (False, record_id)

**与 POS-009 的差异**:
- 事件类型：E-EX-01~08（执行事件）vs E-POS-01/02/03/05（仓位事件）
- 关联键：order_id（执行域主键）vs symbol（仓位域主键）
- 来源枚举：AUTO/SIMULATION/LIVE/MANUAL vs AUTO/MANUAL/EMERGENCY/REBALANCE/DRIFT
- 哈希算法、链结构、query/report/verify/flush 完全同构

## 7. 测试计划

| 用例 | 覆盖点 |
|------|--------|
| 单条记录 | hash 正确，prev_hash=ZERO_HASH |
| 多条链式 | 每条 prev_hash = 上一条 record_hash |
| 链完整性 | verify_chain() 通过 |
| 篡改检测 | 改 detail 后 verify_chain() 返回 False + 断点 |
| 八类事件 | 每类事件便捷方法各记一条 |
| 查询 order_id | 按 order_id 过滤 |
| 查询 symbol/event_type/时间 | 组合过滤 |
| 报告统计 | by_event_type/by_symbol/by_source 计数正确 |
| frozen 不可变 | setattr 抛异常 |
| 持久化 round-trip | flush→load 后链完整、hash 一致 |
| listener 异常隔离 | log 内部异常不抛出（catch+log） |

## 8. 不变量 (INVARIANTS)

- ExecutionAuditRecord / ExecutionAuditReport 是 frozen dataclass，不可变
- 哈希链连续：每条 prev_hash = 上一条 record_hash（首条 = ZERO_HASH）
- 全记录不可跳过：所有 E-EX 事件 MUST 入链（调用方责任）
- detail 用 dict[str, Any]（事件特定字段，JSON 可序列化）
- Decimal/timestamp 在 hash 计算时用 default=str 序列化（保证 canonical）
- flush/load 是 best-effort（失败 log 不抛异常）
- log() 内部异常不阻断执行主流程（catch + log）

## 9. ID 映射

depgraph `blueprint_id=MOD-EX-003` 对应设计文档 `D-EX-CORE-15`（ID 错位：depgraph 顺序编号 ≠ 设计文档功能编号，见 EX-04 蓝图 §10）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-003` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX-003` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-003 | MOD-EX-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | N/A | — |
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
| `src/zephyr/ex_core/audit_journal/__init__.py` | ✅ 已实现 | |

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


