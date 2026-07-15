---
module_id: MOD-FEEDBACK_LOOP
title: Feedback Loop Engine Interface / 反馈闭环引擎接口规范
doc_type: architecture_view
status: Active
version: "1.0.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: Claude-Opus-4.7
created_date: "2026-04-24"
last_updated: "2026-05-06"
ttl: permanent
template_source: "vector_memory-service-interface.md v1.2.0 (B-a-1 定稿模板)"
truth_source:
  - "03_modules/_cross_layer/feedback_loop/blueprint.md（MOD-FEEDBACK_LOOP — 详细设计与闭环契约；Phase 5 真源）"
  - "architecture_model/layers/b_feedback_loop.yaml（Feedback Loop YAML SSoT）"
supersedes: []
related_kb:
  - "KBG-0019 Feedback Loop Engine 架构与技术选型（pending B-e）"
integration_points:
  - "Agent Orchestrator (upstream, 任务指标主数据源)"
  - "Context Engine (downstream, 通过 FeedbackAction Protocol 反向调 adjust_strategy)"
  - "Vector Memory Service (upstream stats, 检索命中率等)"
  - "LLM Security Gateway (upstream, 拦截/异常指标)"
  - "Dashboard (downstream, 可视化)"
tags:
  - feedback_loop
  - quality-baseline
  - trend-analysis
  - protocol-coupling
  - vibe-coding-infrastructure
mod_master_blueprint: "MOD-MASTER_BLUEPRINT"
mod_master_contracts:
  - "CT-FLE-ORC-001"
  - "CT-FLE-DB-001"
  - "CT-TELE-FLE-001"
responsibility_domain: D_FEEDBACK_LOOP
design_maturity: design
build_status: planned
---

# Feedback Loop Engine Interface / 反馈闭环引擎接口规范

> **定位**：反馈闭环引擎（FLE）——**接口与真源以 YAML frontmatter `truth_source` 为准**（`MOD-FEEDBACK_LOOP` 蓝图 + `architecture_model/layers/b_feedback_loop.yaml`）。补齐 Generate → Validate → **Analyze → Evolve** 四段的后两段，使系统能从历史数据学会自我调参。演进路线历史上曾以「VG-07 反馈闭环缺口」表述纳入优先级（仅作背景，**非**文档 SSoT）。
>
> **没有 FLE 的问题**：
>
> 1. 任务完成后指标散落（CI 日志 / Agent 日志 / VMS stats）→ 没有统一基线
> 2. 质量波动无量化触发器 → "最近测试通过率下降"靠直觉发现
> 3. Context Engine 权重永远默认 → `lessons` 槽长期无用仍占 10% 预算
> 4. 幻觉事件缺关联分析 → 同类型 hallucination 反复出现无根因

---

## 0. 读者指南

### 0.1 本文档是什么

| 章节 | 内容 | 主要读者 |
|:-:|------|---------|
| §1 | 服务定位与实施策略（Protocol） | 架构师 |
| §2 | 技术选型表 | 架构师 |
| §3 | 核心数据模型（Metric / Baseline / Anomaly / Action） | 开发者 |
| §4 | API 设计（Sink + Analyzer + Dispatcher + Query） | 集成方 |
| §5 | **反馈动作与下游 Protocol 引用**（遗漏 #5 重点章节） | 架构师 |
| §6 | 趋势分析算法 | 开发者 |
| §7 | 前置条件与依赖 | 开发者 |
| §8 | 文件清单与落位 | 开发者 |
| §9 | 集成点 | 架构师 |
| §10 | 渐进路线 | 所有人 |
| §11 | 错误码与降级策略（DEGRADE-001~002） | 集成方 |
| §12 | 性能 SLO（含冷启动） | 运维 |
| §13 | 测试用例（P0） | 开发者、QA |
| §14 | 修订记录 | 所有人 |

### 0.2 本文档**不是**

- ❌ **异常语义判定手册**——FLE 用规则 + 阈值，不承担深度语义判断（LLM 语义分析交给 Agent）
- ❌ **Prometheus 部署指南**——experimental 用 SQLite 时间序列，Prometheus 是 beta+ 升级选项
- ❌ **Context Engine / Orchestrator 实现文档**——见对应 interface.md
- ❌ **报警通道实现**——通知是 Dashboard 职责，FLE 只输出 Anomaly 事件
- ❌ **Dashboard UI 设计**——见 `dashboard-interface-spec.md`（未来另出）
- ❌ **生产部署运维手册**——beta+ 服务化时另出 SRE 文档

---

## 1. 服务定位与实施策略

### 1.1 缺口 → 原因 → 解法

**缺口**：系统运行指标有输出（Orchestrator 的 task metrics、VMS 的 search stats、LSG 的拦截事件、Agent 的 token 消耗），但没有统一入口接收、对比基线、触发调参。

**原因**：
1. 老方案把"反馈"当成 Dashboard 职责，但 Dashboard 只展示不决策
2. 没有时间序列基线，每次"感觉变慢了"靠拍脑袋
3. Context Engine 的 slot 权重是启动时配的常量，无法按真实使用情况演化

**解法**：
- 统一 `MetricSink` 接收上游指标（Orchestrator/VMS/LSG/CE 都推）
- SQLite 时间序列表（`metrics_timeseries`）持久化
- 移动平均 + 阈值算法做稳态基线，偏离触发 `Anomaly`
- `Anomaly` 映射到 `Action`（`adjust_slot_weight` / `invalidate_cache` / `quarantine_collection` / `alert_ops`）
- Action 通过 **Protocol 单向引用** 调下游（关键：**不硬编码 CE/Orchestrator 实现**）

### 1.2 职责边界

| Yes | No |
|-----|----|
| ✅ 接收任意上游 `Metric` 事件 | ❌ 产生指标（各服务自己推） |
| ✅ 维护基线 + 趋势分析 + 异常检测 | ❌ LLM 语义级异常判定 |
| ✅ 路由 `Anomaly` → `Action` | ❌ 实际执行动作（调下游 Protocol） |
| ✅ 时间序列持久化与查询 | ❌ 报警通道（UI/Slack/Email） |
| ✅ 记录 Action 效果闭环（效果不佳回滚） | ❌ Action 内部逻辑（下游服务自理） |

### 1.3 实施策略：Protocol + 双实现

```python
# src/zephyr/infrastructure/runtime_integration/a2a_protocol/governance/protocol.py (experimental 产出)

from typing import Protocol

class FeedbackLoopProtocol(Protocol):
    # Sink：接收指标
    async def record_metric(self, metric: Metric) -> None: ...
    async def record_batch(self, metrics: list[Metric]) -> BatchRecordResult: ...

    # Analyze：查询基线 / 异常
    async def get_baseline(self, metric_name: str, window: str = "7d") -> Baseline: ...
    async def detect_anomalies(self, since: datetime | None = None) -> list[Anomaly]: ...

    # Dispatch：触发动作
    async def dispatch_action(self, anomaly: Anomaly) -> ActionResult: ...
    async def list_pending_actions(self) -> list[PendingAction]: ...
    async def acknowledge_action_outcome(self, action_id: str, outcome: ActionOutcome) -> None: ...

    # Query
    async def query_timeseries(self, metric_name: str, since: datetime, until: datetime) -> list[Metric]: ...
    async def stats(self) -> FLEStats: ...

class InProcessFeedbackLoop:
    """SQLite 时间序列 + 规则引擎。"""

class DistributedFeedbackLoop:
    """beta+：InfluxDB + 分布式分析器。"""
```

| Phase | 实施形态 | 运行方式 | 触发升级条件 |
|:-:|---------|---------|-------------|
| **experimental** | **`InProcessFeedbackLoop`（SQLite + 移动平均）** | 进程内异步 | - |
| beta | `DistributedFeedbackLoop`（InfluxDB + SPC 算法） | HTTP 服务 | 数据点 > 100 万 或 误报率 > 20% |
| stable | 强化学习 Evolve | RL Agent | beta 数据充足后 |

**所有 API 均为 `async`**。进程内锁 `asyncio.Lock`，跨进程锁 `filelock.FileLock`。**严禁 `threading.Lock`**。

---

## 2. 技术选型表（真源锁定）

| 组件 | 首选 | 备选 | 不推荐 | 选型理由 | 升级触发 | 相关 KB 决策记录 |
|------|----------------|------|-------|---------|---------|----------|
| 时间序列存储 | **SQLite 时间序列表（WAL）** | InfluxDB 2.x | Parquet 文件 | 零外部依赖 + 事务 | 数据点 > 100 万 或跨机查询 | KBG-0019 |
| 趋势分析算法 | **移动平均（EMA）+ 阈值** | SPC（Shewhart 控制图） | 单点阈值（误报高） | 实现简单、可解释 | 误报率 > 20% | KBG-0019 |
| 异常检测 | **规则引擎 + 滑窗阈值** | 轻量 ML（isolation forest） | LLM 语义判（成本高） | 确定性、可审计 | 规则维护成本 > ML 时切换 | KBG-0019 |
| 反馈 → 动作映射 | **静态路由表 + Protocol 调用** | 规则引擎 DSL | 硬编码 | 解耦下游服务 | 动作 > 20 种 | KBG-0019 |
| 下游调用 | **Protocol 注入（`ContextAdjustAction` / `OrchestratorControlAction`）** | 事件总线 | 直接 import | 单向依赖，无循环 | - | KBG-0019 |
| 进程内并发 | **`asyncio.Lock`** | - | `threading.Lock` | 项目全异步栈 | - | - |
| 跨进程并发 | **`filelock.FileLock`** | - | 全局单例 | pytest 并发 | - | - |

---

## 3. 核心数据模型

### 3.1 Metric / Baseline / Anomaly / Action

```python
# src/zephyr/integration/shared/schema/schemas.py (experimental 产出)

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class Metric(BaseModel):
    metric_name: str = Field(..., description="命名空间化，如 'orc.task.duration_ms' / 'vms.search.hit_rate'")
    value: float
    unit: Optional[str] = None
    tags: dict[str, str] = Field(default_factory=dict,
        description="如 {'task_kind':'feature','agent_id':'A-01'}")
    source: Literal["orchestrator", "vms", "context_engine", "lsg", "external"] = "external"
    observed_at: datetime
    correlation_id: Optional[str] = Field(None, description="关联 task_id / request_id，用于根因追溯")

class Baseline(BaseModel):
    metric_name: str
    window: str = Field(description="'7d' / '24h' / '1h'")
    mean: float
    stddev: float
    ema: float = Field(description="指数移动平均")
    ema_alpha: float = Field(default=0.2)
    sample_count: int
    computed_at: datetime

class Anomaly(BaseModel):
    anomaly_id: str
    metric_name: str
    observed_value: float
    baseline_mean: float
    baseline_stddev: float
    deviation_sigma: float = Field(description="|(value-mean)/stddev|")
    severity: Literal["info", "warn", "error", "critical"]
    anomaly_kind: Literal[
        "spike",            # 单点飙升
        "drop",             # 单点跌落
        "trend_up",         # 持续上升
        "trend_down",       # 持续下降
        "flatline",         # 数据停滞（上游挂了？）
        "oscillation",      # 震荡
    ]
    window: str
    first_observed_at: datetime
    last_observed_at: datetime
    correlation_ids: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list,
        description="根据 anomaly_kind 映射建议动作 ID")

class PendingAction(BaseModel):
    action_id: str
    anomaly_id: str
    action_kind: Literal[
        "adjust_context_slot_weight",   # → Context Engine
        "invalidate_context_cache",     # → Context Engine
        "pause_task_kind",              # → Orchestrator
        "quarantine_agent",             # → Orchestrator
        "quarantine_vms_collection",    # → VMS (降权检索)
        "bump_lsg_strictness",          # → LSG
        "alert_ops",                    # → Dashboard / log only
    ]
    target_service: Literal["context_engine", "orchestrator", "vms", "lsg", "ops"]
    payload: dict
    dispatched_at: Optional[datetime] = None
    expires_at: datetime = Field(description="超时未执行自动丢弃")

class ActionOutcome(BaseModel):
    action_id: str
    executed: bool
    effective_observed: bool = Field(description="是否观察到指标改善")
    rollback_required: bool = Field(default=False)
    outcome_measured_at: datetime
    notes: Optional[str] = None
```

### 3.2 Anomaly → Action 静态路由表

```python
# src/zephyr/observability/feedback_loop/action_router.py

ANOMALY_ACTION_ROUTING = {
    # 指标名 → anomaly_kind → action_kind
    "orc.task.hallucination_rate": {
        "trend_up": ("bump_lsg_strictness", {"delta": 0.1, "ttl_minutes": 60}),
        "spike":    ("pause_task_kind", {"ttl_minutes": 15}),
    },
    "ce.slot.hit_rate.lessons": {
        "trend_down": ("adjust_context_slot_weight", {"slot": "lessons", "delta": -0.03}),
        "drop":       ("adjust_context_slot_weight", {"slot": "lessons", "delta": -0.05}),
    },
    "ce.slot.hit_rate.code_refs": {
        "trend_down": ("adjust_context_slot_weight", {"slot": "code_refs", "delta": -0.03}),
    },
    "vms.search.hit_rate": {
        "trend_down": ("invalidate_context_cache", {}),
        "flatline":   ("alert_ops", {"reason": "vms_search_stopped"}),
    },
    "orc.sandbox.violation_count": {
        "spike":    ("quarantine_agent", {"ttl_minutes": 120}),
        "trend_up": ("bump_lsg_strictness", {"delta": 0.2}),
    },
    "lsg.prompt_injection.bypass_rate": {
        "trend_up": ("bump_lsg_strictness", {"delta": 0.3, "ttl_minutes": 240}),
        "spike":    ("alert_ops", {"severity": "critical"}),
    },
    # ... 其他映射在 feedback_loop_rules.yaml 维护
}
```

---

## 4. API 设计

### 4.1 Python 库 API（experimental 主用）

```python
class InProcessFeedbackLoop:  # implements FeedbackLoopProtocol

    def __init__(
        self,
        config: FLEConfig,
        # 下游 Action Protocol 注入（关键：单向依赖，不硬编码具体实现）
        context_action: "ContextAdjustActionProtocol | None" = None,
        orchestrator_action: "OrchestratorControlActionProtocol | None" = None,
        vms_action: "VMSControlActionProtocol | None" = None,
        lsg_action: "LSGControlActionProtocol | None" = None,
    ) -> None: ...

    # ───── Sink ─────
    async def record_metric(self, metric: Metric) -> None:
        """单条指标入库。批量场景用 record_batch。"""

    async def record_batch(self, metrics: list[Metric]) -> BatchRecordResult:
        """批量入库，事务提交。失败整批回滚。"""

    # ───── Analyze ─────
    async def get_baseline(
        self,
        metric_name: str,
        window: Literal["1h", "24h", "7d", "30d"] = "7d",
    ) -> Baseline: ...

    async def detect_anomalies(
        self,
        since: datetime | None = None,
        metric_filter: list[str] | None = None,
    ) -> list[Anomaly]:
        """
        扫描 since 之后的新指标，运行移动平均 + 阈值规则（§6），输出 anomalies。
        experimental 同步调用（每次 record 后可触发增量检测）。
        """

    # ───── Dispatch ─────
    async def dispatch_action(self, anomaly: Anomaly) -> ActionResult:
        """
        按 ANOMALY_ACTION_ROUTING 生成 PendingAction，调下游 Protocol 执行。
        若对应 Protocol 未注入（None），写 pending_actions.ndjson 待后续补发。
        """

    async def list_pending_actions(
        self,
        include_dispatched: bool = False,
    ) -> list[PendingAction]: ...

    async def acknowledge_action_outcome(
        self,
        action_id: str,
        outcome: ActionOutcome,
    ) -> None:
        """
        下游执行后回调本接口，记录效果。
        若 outcome.rollback_required=True，自动生成反向 Action。
        """

    # ───── Query ─────
    async def query_timeseries(
        self,
        metric_name: str,
        since: datetime,
        until: datetime,
        tag_filters: dict[str, str] | None = None,
        aggregation: Literal["raw", "avg_1m", "avg_5m", "avg_1h"] = "raw",
    ) -> list[Metric]: ...

    async def stats(self) -> FLEStats: ...
```

### 4.2 HTTP API（beta 预留骨架）

| Method + Path | 对应库方法 |
|---------------|-----------|
| `POST /v1/metrics` | `record_metric()` |
| `POST /v1/metrics/batch` | `record_batch()` |
| `GET /v1/baselines/{metric_name}?window=` | `get_baseline()` |
| `POST /v1/anomalies/detect` | `detect_anomalies()` |
| `POST /v1/actions/dispatch` | `dispatch_action()` |
| `GET /v1/actions/pending` | `list_pending_actions()` |
| `POST /v1/actions/{action_id}/outcome` | `acknowledge_action_outcome()` |
| `POST /v1/metrics/query` | `query_timeseries()` |
| `GET /v1/stats` | `stats()` |

---

## 5. 反馈动作与下游 Protocol 引用（遗漏 #5 重点章节）

> **核心设计约束**：FLE 调 Context Engine / Orchestrator 的 `adjust_*` 接口时，**严禁直接 import** 其实现类。必须定义本地 Protocol，调用方在 wiring 层注入。
>
> **原因**：
> 1. 避免循环依赖（CE 未来可能订阅 FLE 的 `runtime_state` 作为 slot 输入）
> 2. 测试时能用 Mock Protocol 脱钩真实服务
> 3. beta+ 服务化后只需换注入实现（HTTP Client / Remote Proxy），FLE 本体零改动

### 5.1 FLE 侧定义的下游 Protocol

```python
# src/zephyr/observability/feedback_loop/action_protocols.py (FLE 侧定义)

from typing import Protocol

class ContextAdjustActionProtocol(Protocol):
    """对应 Context Engine 的 adjust_strategy 接口。"""
    async def adjust_strategy(self, task_id: str, signal: "FeedbackSignal") -> "AdjustResult": ...

class OrchestratorControlActionProtocol(Protocol):
    """对应 Orchestrator 的控制动作。"""
    async def pause_task_kind(self, task_kind: str, ttl_minutes: int, reason: str) -> None: ...
    async def quarantine_agent(self, agent_id: str, ttl_minutes: int, reason: str) -> None: ...

class VMSControlActionProtocol(Protocol):
    """对应 VMS 的临时降权检索。"""
    async def quarantine_collection(self, collection: str, ttl_minutes: int, reason: str) -> None: ...

class LSGControlActionProtocol(Protocol):
    """对应 LSG 的严格度调整。"""
    async def bump_strictness(self, delta: float, ttl_minutes: int, reason: str) -> None: ...
```

### 5.2 Wiring 示例（experimental，单进程）

```python
# src/zephyr/data/knowledge_management/kb/bootstrap.py

async def build_services():
    vm = get_vm()
    ce = InProcessContextEngine(config=..., vm=vm, entity_graph_path=...)
    orc = InProcessOrchestrator(config=...)
    lsg = InProcessLLMSecurityGateway(config=...)

    # FLE 注入下游 Protocol 适配器
    fle = InProcessFeedbackLoop(
        config=...,
        context_action=CEAdjustAdapter(ce),      # 适配器：把 FLE FeedbackSignal 转 CE FeedbackSignal
        orchestrator_action=OrcControlAdapter(orc),
        vms_action=VMSControlAdapter(vm),
        lsg_action=LSGControlAdapter(lsg),
    )

    # Orchestrator 反向注入 FLE 作为 FeedbackSinkProtocol
    orc.set_feedback_sink(FLEMetricSinkAdapter(fle))
    # CE 反向注入同理
    ce.set_feedback_sink(FLEMetricSinkAdapter(fle))

    return vm, ce, orc, lsg, fle
```

### 5.3 FeedbackSignal 适配（与 CE §3.3 对齐）

```python
# src/zephyr/infrastructure/shared_services/context_engine.py

class CEAdjustAdapter:
    """FLE 侧 Anomaly → CE 侧 FeedbackSignal 的适配器。"""

    def __init__(self, ce: ContextEngineProtocol) -> None:
        self._ce = ce

    async def adjust_strategy(self, task_id: str, signal_fle: "FLESignal") -> AdjustResult:
        # 把 FLE 内部 anomaly kind 映射到 CE 的 FeedbackSignal.anomaly_type
        signal_ce = FeedbackSignal(
            task_id=task_id,
            anomaly_type=_map_anomaly_kind(signal_fle.anomaly_kind),
            confidence=min(1.0, signal_fle.deviation_sigma / 3.0),
            suggested_action=_map_action(signal_fle.suggested_action),
            target_slot=signal_fle.payload.get("slot"),
            adjustment_magnitude=signal_fle.payload.get("delta", 0.1),
            observed_at=signal_fle.last_observed_at,
        )
        return await self._ce.adjust_strategy(task_id, signal_ce)
```

### 5.4 依赖方向图

```
  Orchestrator --[push metrics via FeedbackSinkProtocol]--> FLE
  Context Engine --[push metrics]--> FLE
  VMS --[push metrics]--> FLE
  LSG --[push metrics]--> FLE

  FLE --[via ContextAdjustActionProtocol adapter]--> Context Engine.adjust_strategy()
  FLE --[via OrchestratorControlActionProtocol adapter]--> Orchestrator.pause_task_kind() 等
  FLE --[via VMSControlActionProtocol adapter]--> VMS.quarantine_collection()
  FLE --[via LSGControlActionProtocol adapter]--> LSG.bump_strictness()
```

**没有循环依赖**：FLE 永远是中心，上游推、下游拉。所有跨服务调用通过 Protocol 解耦。

---

## 6. 趋势分析算法

### 6.1 EMA（指数移动平均）

```
EMA_t = α · value_t + (1-α) · EMA_{t-1}
其中 α ∈ [0.1, 0.3]（experimental 默认 0.2）
```

新值偏离 EMA 超过 `k·stddev`（experimental 默认 k=2）即标记 `spike`/`drop`。

### 6.2 滑窗趋势检测

```
窗口 w=10 个采样点
取 w 内线性拟合斜率 slope
|slope / baseline_mean| > threshold（experimental 默认 0.1）持续 3 个窗口 → trend_up/down
```

### 6.3 Flatline 检测

```
连续 N 个窗口（experimental 默认 5）无新数据点 → flatline
（上游服务挂的早期信号）
```

### 6.4 规则外置

所有阈值 / 窗口 / 映射表外置到 `config/feedback_loop_rules.yaml`，便于无代码变更调参。

---

## 7. 前置条件与依赖

| 前置项 | 状态 |
|-------|:----:|
| `src/zephyr/feedback_loop/` 包创建 | ⏳ 待建 |
| SQLite 时间序列 schema | ⏳ experimental T-1-XX |
| 上游 metrics sink 接线（Orchestrator/VMS/LSG/CE 都要调 FLE） | ⏳ beta 接入 |
| 下游 Action Protocol 适配器实现 | ⏳ beta 接入 |
| KBG-0019 批准 | ⏳ pending B-e |

**Python 依赖**：

```toml
[project.optional-dependencies]
feedback_loop = [
    "aiosqlite>=0.19",
    "numpy>=1.26,<2.0",     # EMA / 线性拟合
    "filelock>=3.13",
    "pydantic>=2.5,<3.0",
]
```

---

## 8. 文件清单与落位（不留 placeholder）

```

├── src/zephyr/
│   ├── feedback_loop/                              # ⏳ experimental 新建
│   │   ├── __init__.py                             # 导出 get_fle()
│   │   ├── protocol.py                             # FeedbackLoopProtocol
│   │   ├── action_protocols.py                     # §5.1 下游 Protocol 定义
│   │   ├── in_process.py                           # experimental 实现
│   │   ├── distributed.py                          # beta+ 占位
│   │   ├── schemas.py                              # Metric / Baseline / Anomaly / Action
│   │   ├── sink.py                                 # record_metric / record_batch
│   │   ├── analyzer/
│   │   │   ├── ema.py                              # EMA 实现
│   │   │   ├── trend.py                            # 滑窗斜率
│   │   │   └── flatline.py
│   │   ├── action_router.py                        # §3.2 ANOMALY_ACTION_ROUTING
│   │   ├── dispatcher.py                           # dispatch_action 逻辑
│   │   ├── adapters/
│   │   │   ├── context_engine.py                   # CEAdjustAdapter
│   │   │   ├── orchestrator.py                     # OrcControlAdapter
│   │   │   ├── vms.py                              # VMSControlAdapter
│   │   │   └── lsg.py                              # LSGControlAdapter
│   │   ├── db.py                                   # SQLite schema
│   │   └── config.py
│   └── config/
│       ├── feedback_loop.yaml
│       └── feedback_loop_rules.yaml                # 阈值外置
│
├── .runtime/
│   ├── feedback_loop/
│   │   ├── metrics.db                              # SQLite WAL
│   │   ├── pending_actions.ndjson                  # 下游未注入时的缓冲
│   │   └── baseline_cache.json
│   └── logs/
│       ├── fle_degrade.log
│       └── fle_action_audit.log                    # 所有 Action 审计
│
├── tests/
│   ├── test_sink.py
│   ├── test_ema.py
│   ├── test_trend_detection.py
│   ├── test_flatline.py
│   ├── test_action_routing.py
│   ├── test_dispatch_with_mock_protocol.py         # 关键：用 Mock 验证 Protocol 解耦
│   ├── test_action_outcome_rollback.py
│   ├── test_cold_start.py
│   └── test_degrade_paths.py
│
└── .gitignore                                      # 已追加 .runtime/
```

---

## 9. 集成点

### 9.1 上游 Metric Sources

| 上游 | 推送什么 | 频率 |
|------|---------|------|
| **Orchestrator** | `orc.task.duration_ms` / `orc.task.hallucination_rate` / `orc.sandbox.violation_count` / `orc.agent.throughput` | 每任务完成时 + 每分钟聚合 |
| **VMS** | `vms.search.hit_rate` / `vms.search.latency_ms` / `vms.ingest.count` / `vms.degrade_events` | 每查询 + 每分钟聚合 |
| **Context Engine** | `ce.slot.hit_rate.<slot>` / `ce.build.latency_ms` / `ce.compress.ratio` / `ce.degrade_events` | 每 build 完成 |
| **LSG** | `lsg.prompt_injection.bypass_rate` / `lsg.output_schema.reject_rate` / `lsg.secret_leak.events` | 每拦截事件 |

### 9.2 下游 Action Targets（Protocol 调用）

见 §5.1 + §5.4 依赖方向图。

### 9.3 Dashboard

```
Dashboard --[query_timeseries / get_baseline / list_pending_actions]--> FLE
```

只读消费，不反向写入。

---

## 10. 渐进路线

| Phase | 范围 | 验收标准 |
|:-:|------|---------|
| **scaffold**（当前） | 接口规范 + KBG-0019 | status=Active |
| **experimental** | `InProcessFeedbackLoop` + SQLite 时间序列 + EMA/趋势 + ACTION_ROUTING 静态表 | ① §13 P0 用例通过<br>② Sink 吞吐 ≥ 1000 metric/s<br>③ 异常检测 P95 延迟 ≤ 200ms |
| **beta** | 上游接线（4 服务均推指标）+ 下游 Protocol 适配器全启 | 闭环：hallucination 尖峰 → quarantine_agent 自动生效 |
| **beta** | `DistributedFeedbackLoop`（InfluxDB + SPC） | 数据点 > 100 万触发 |
| **stable** | 强化学习 Evolve（slot 权重自动收敛） | beta 数据充足 |

---

## 11. 错误码与降级策略

### 11.1 异常层级

```python
class FLEError(Exception): ...
class FLEConfigError(FLEError): ...
class FLESinkError(FLEError): ...                     # record_metric 写入失败
class FLEAnalyzerError(FLEError): ...                 # 基线计算失败
class FLEActionDispatchError(FLEError): ...           # 下游 Protocol 调用失败
```

### 11.2 P0 级降级条款（2 条）

> **核心原则**：FLE 是"观察 + 调参"角色，**自己挂了系统仍要能跑**，宁可不调参也不能反过来拖垮核心链路。

**DEGRADE-001：FLE 自己挂了不影响上游 metric 产出**

触发场景：
- SQLite WAL 损坏 / 磁盘满
- FLE 进程 OOM

**上游契约**（所有 metric 产出方必须遵守）：

```python
# 调 FLE 的 record_metric 必须 try/except，不抛到业务层
try:
    await fle_sink.record_metric(metric)
except Exception as e:
    # 不阻塞业务，本地缓冲待恢复
    local_buffer.append(metric)
    log_structured("fle_push_degrade", reason=str(e))
```

**FLE 恢复后**：暴露 `replay_buffer(metrics)` 接口给上游回放。

**DEGRADE-002：下游 Action Protocol 未注入或调用失败时缓冲**

触发场景：
- Wiring 阶段某下游 Protocol 未注入（例如 experimental 暂不接 LSG）
- 下游服务挂
- 下游超时

降级动作：

```python
try:
    await self._context_action.adjust_strategy(task_id, signal)
except Exception as e:
    # 写 pending_actions.ndjson
    await self._buffer_pending_action(action, reason=str(e))
    log_structured("fle_dispatch_degrade", code="DEGRADE-002", action_id=aid, reason=str(e))
```

**恢复策略**：暴露 `replay_pending_actions()` 接口，下游恢复后主动调。action 超 `expires_at` 自动丢弃避免陈旧动作生效。

**对 ACTION 产出的硬约束**：每个 Action 的生效**必须记录 `effective_from` + `ttl`**，超 ttl 自动回滚默认，**FLE 挂了也不会留下永久错误配置**。

### 11.3 降级条件速查表

| 触发条件 | 降级动作 | 上游感知 |
|---------|---------|---------|
| FLE 自己挂 | 上游本地缓冲 metrics | DEGRADE-001 |
| 下游 Protocol 未注入 | pending_actions.ndjson 缓冲 | DEGRADE-002 |
| 下游调用失败 | 同上 | DEGRADE-002 |
| SQLite 读失败 | 基线返回 None，不触发 anomaly | 日志告警 |
| Action TTL 到期 | 自动回滚默认值 | 透明 |

所有降级写 `logs/fle_degrade.log`。

---

## 12. 性能 SLO

### 12.1 稳态 SLO

| 指标 | 目标 | 条件 |
|------|------|------|
| `record_metric()` p50 | ≤ 3 ms | 单条 |
| `record_batch(100)` p95 | ≤ 50 ms | - |
| `detect_anomalies()` p95 | ≤ 200 ms | 单指标 7 天窗口 |
| `get_baseline()` p50 | ≤ 30 ms | 缓存命中 |
| `dispatch_action()` p95 | ≤ 500 ms | 含下游 Protocol 调用 |
| `query_timeseries(1h raw)` p95 | ≤ 100 ms | - |
| 最大吞吐（record） | ≥ 1000 metric/s | WAL 批提 |

### 12.2 冷启动 SLO

| 指标 | 目标 | 说明 |
|------|------|------|
| 进程 import | ≤ 1 s | 仅 import feedback_loop |
| SQLite 连接 + schema check | ≤ 300 ms | WAL |
| 基线缓存加载 | ≤ 500 ms | 从 baseline_cache.json |
| pending_actions.ndjson 回放 | ≤ 1 s | < 1000 条 |
| 首次 `record_metric()` | ≤ 50 ms | - |
| **总冷启动到可用** | **≤ 3 s** | - |

---

## 13. 测试用例（P0）

### 13.1 Sink P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-S1 | record_metric 单条写入 | 可 query_timeseries 查到 |
| P0-S2 | record_batch 原子性 | 批内一条失败整批回滚 |
| P0-S3 | 吞吐 ≥ 1000 metric/s | WAL 批提，连续 10 秒压测 |

### 13.2 分析 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-A1 | EMA 收敛 | 100 点常量数据后 ema ≈ 该常量 |
| P0-A2 | spike 检测 | 偏离 3σ 单点 → anomaly_kind=spike |
| P0-A3 | trend_up 检测 | 滑窗 3 次斜率 > 阈值 → trend_up |
| P0-A4 | flatline 检测 | 连续 5 窗口无数据 → flatline |

### 13.3 动作路由 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-R1 | hallucination_rate trend_up → bump_lsg_strictness | 路由表命中，生成 PendingAction |
| P0-R2 | lessons hit_rate drop → adjust_context_slot_weight | 同上 |
| P0-R3 | 未匹配规则 → alert_ops | 兜底路由 |

### 13.4 Protocol 解耦 P0（关键，遗漏 #5 对应）

| # | 用例 | 预期 |
|:-:|------|------|
| P0-P1 | 用 Mock ContextAdjustActionProtocol 验证调用 | FLE 不 import CE 实现类 |
| P0-P2 | 下游未注入时缓冲 | context_action=None 时写 pending_actions.ndjson |
| P0-P3 | 下游调用失败时缓冲 | 抛异常后同上 |
| P0-P4 | replay_pending_actions 回放成功 | expires_at 内的 action 全派发 |
| P0-P5 | expires_at 过期丢弃 | 过期 action 不派发 |

### 13.5 Outcome 闭环 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-O1 | rollback_required=True 自动生成反向 Action | 校验反向动作 payload |
| P0-O2 | TTL 到期自动回滚 | ttl_minutes 后指标观察回默认 |

### 13.6 降级 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-D1 | FLE sink 写失败上游缓冲 | 模拟 SQLite 写异常，上游本地缓冲不丢 |
| P0-D2 | 下游 Protocol 挂 | pending_actions.ndjson 写入，DEGRADE-002 日志 |

### 13.7 冷启动 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-C1 | 冷启动 ≤ 3s | - |
| P0-C2 | pending_actions 回放 | 启动后 replay 历史动作 |

---

## 14. 修订记录

| 日期 | 版本 | 说明 |
|------|:-:|------|
| 2026-04-24 | 1.0.0 | 初版（B-a-4）。基于 VMS v1.2 模板 + KBG-0019。重点：① §5 下游 Protocol 单向引用（`ContextAdjustActionProtocol` 等）解决遗漏 #5 耦合风险；② §3.2 ANOMALY_ACTION_ROUTING 静态路由表；③ §6 EMA + 滑窗斜率 + Flatline 三算法；④ §11.2 DEGRADE-001/002 + 所有 Action TTL 强制（FLE 挂也不会留下永久错误配置）；⑤ §5.4 无循环依赖图。 |
