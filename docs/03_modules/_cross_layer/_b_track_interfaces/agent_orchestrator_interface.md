---
module_id: MOD-INF-039
title: Agent Orchestrator Interface / Agent 编排器接口规范
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
  - "03_modules/infra_ops/task_system/blueprint.md（MOD-TASK_SYSTEM — Agent Orchestrator / 任务生命周期与状态机真源）"
  - "architecture_model/layers/b_orchestrator.yaml（Orchestrator YAML SSoT）"
supersedes:
  - "archive/reorg-2026-04-24/08_ai_engineering/workflow-interface-contract.md (archived 2026-04-24)"
related_kb:
  - "KBG-0017 Agent Orchestrator 任务队列与状态机（pending B-e）"
  - "KBG-0018 Agent Sandbox（pending B-e）"
integration_points:
  - "Context Engine (upstream, 任务开始前拉上下文)"
  - "LLM Security Gateway (upstream, 入参/出参 Schema 校验)"
  - "Vector Memory Service (upstream writer, 任务完成写 task_history)"
  - "Feedback Loop Engine (downstream signal, 质量数据上报)"
  - "Agent Sandbox (runtime, 文件系统/命令隔离)"
depends_on:
  - target: AI-ENG-CTX-001
    at: "§6"
    why: "Context Engine — 任务开始前拉取上下文"
  - target: AI-ENG-LSG-001
    at: "§4"
    why: "LLM Security Gateway — 入参/出参 Schema 校验"
  - target: AI-ENG-VMS-001
    at: "§4"
    why: "Vector Memory Service — 任务完成写 task_history"
mod_master_blueprint: "MOD-MASTER_BLUEPRINT"
mod_master_contracts:
  - "CT-ORC-SCRIPT-001"
  - "CT-ORC-CE-001"
  - "CT-ORC-VMS-001"
  - "CT-ORC-GATE-001"
tags:
  - agent-orchestrator
  - task-queue
  - state-machine
  - sandbox
  - hallucination-detection
  - vibe-coding-infrastructure
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Agent Orchestrator Interface / Agent 编排器接口规范

> **定位**：Vibe Coding 2.0 五大核心服务中的"任务引擎"。接管任务全生命周期——任务入队、Agent 拉取、沙箱执行、幻觉检测、指标上报、收尾归档。
>

---

## 0. 读者指南

### 0.1 本文档是什么

| 章节 | 内容 | 主要读者 |
|:-:|------|---------|
| §1 | 服务定位与实施策略（Protocol） | 架构师 |
| §2 | 技术选型表 | 架构师、运维 |
| §3 | 核心数据模型（Task / State / Agent / Sandbox） | 开发者 |
| §4 | API 设计（任务/Agent/沙箱三套 API） | 集成方 |
| §5 | 状态机与生命周期 | 开发者 |
| §6 | 沙箱与安全隔离 | 安全 / 开发者 |
| §7 | 前置条件与依赖 | 开发者 |
| §8 | 文件清单与落位 | 开发者 |
| §9 | 集成点 | 架构师 |
| §10 | 渐进路线 | 所有人 |
| §11 | 错误码与降级策略（DEGRADE-001~003） | 集成方 |
| §12 | 性能 SLO（含冷启动） | 运维 |
| §13 | 测试用例（P0） | 开发者、QA |
| §14 | 修订记录 | 所有人 |

### 0.2 本文档**不是**

- ❌ **任务卡 YAML schema**——见 `docs/02_enterprise_architecture/task-card-schema.md`
- ❌ **Context Engine 设计**——见 `context_engine-interface.md`
- ❌ **沙箱内部实现**——本规范定义沙箱接口，具体 Windows ACL / Docker Desktop 实现另出施工图
- ❌ **SQLite 表设计细则**——见 experimental 施工图 `construction-plan-orchestrator-*.md`
- ❌ **幻觉检测规则库**——见 `hallucination_rules.yaml`（experimental 另出）
- ❌ **生产部署运维手册**——beta+ 服务化时另出 SRE 文档

---

## 1. 服务定位与实施策略

### 1.1 缺口 → 原因 → 解法

**缺口**：多 Agent 并行执行任务时，或者乱写源码（沙箱缺位）、或者死循环（幻觉未检测）、或者进度不透明（状态机缺位）、或者历史不可查（任务归档缺位）。

**原因**：
1. 老方案把"任务流程"当作人工操作手册，没有进程态的状态机
2. Agent 获得直接文件系统权限——一旦被劫持或误操作能物理删除整个 repo（SEC-02 根因）
3. LLM 偶发 hallucination 会生成死循环调用链，无硬阻断机制
4. 任务完成后的 `task_history` 散落在 chat log 不可检索

**解法**：
- **SQLite + asyncio.Queue 队列**：零外部依赖、轻量、持久化
- **Python enum + dataclass 状态机**：状态变迁强校验，非法转移即抛
- **Windows ACL + 只读挂载沙箱**：Agent 写操作必经沙箱代理
- **规则引擎 + 阈值幻觉检测**：同一文件 N 次无进展编辑即终止
- **任务完成自动写 VMS `task_history`**：后续任务可通过 VMS `multi_search` 检索"类似任务如何完成"

### 1.2 职责边界

| Yes | No |
|-----|----|
| ✅ 任务排队、优先级、依赖调度 | ❌ 决定"任务内容"（上游 planner/任务卡） |
| ✅ Agent 生命周期（拉取/执行/终止/清理） | ❌ Agent 内部的 LLM 调用（Agent 自己的事） |
| ✅ 沙箱创建/挂载/销毁 | ❌ 沙箱内部文件系统细节（Windows ACL/Docker） |
| ✅ 状态机强校验 | ❌ 任务的业务执行（Agent 实现） |
| ✅ 幻觉循环检测与终止 | ❌ 幻觉语义判定（FLE 处理） |
| ✅ 任务历史归档到 VMS | ❌ 任务检索（调 VMS）|
| ✅ 质量指标上报 FLE | ❌ 异常分析（FLE）|

### 1.3 实施策略：Protocol + 双实现

```python
# src/zephyr/infrastructure/runtime_integration/a2a_protocol/governance/protocol.py (experimental 产出)

from typing import Protocol

class OrchestratorProtocol(Protocol):
    # 任务
    async def submit_task(self, task: TaskSubmit) -> TaskHandle: ...
    async def get_task(self, task_id: str) -> Task | None: ...
    async def list_tasks(self, filters: TaskFilters | None = None) -> list[Task]: ...
    async def cancel_task(self, task_id: str, reason: str) -> CancelResult: ...

    # Agent
    async def register_agent(self, spec: AgentSpec) -> AgentHandle: ...
    async def claim_task(self, agent_id: str, capabilities: list[str]) -> Task | None: ...
    async def report_progress(self, agent_id: str, task_id: str, progress: AgentProgress) -> None: ...
    async def complete_task(self, agent_id: str, task_id: str, result: TaskResult) -> CompleteResult: ...
    async def fail_task(self, agent_id: str, task_id: str, failure: TaskFailure) -> None: ...

    # 沙箱
    async def provision_sandbox(self, task_id: str, policy: SandboxPolicy) -> Sandbox: ...
    async def destroy_sandbox(self, sandbox_id: str) -> None: ...

    # 健康与统计
    async def stats(self) -> OrchestratorStats: ...

class InProcessOrchestrator:
    """experimental（当前目标）：SQLite + asyncio.Queue，单进程。"""

class DistributedOrchestrator:
    """beta+：ARQ + Redis，多 worker。"""
```

| Phase | 实施形态 | 运行方式 | 触发升级条件 |
|:-:|---------|---------|-------------|
| **experimental** | **`InProcessOrchestrator`（SQLite + asyncio.Queue）** | 单进程，多 Agent 协程 | - |
| beta | `DistributedOrchestrator`（ARQ + Redis） | 多 worker 进程 | 任务量 > 100/天 或并发 Agent > 10 |
| stable | NATS JetStream | 分布式 | 跨机 Agent / 实时通信 < 1s 需要 |

**所有 API 均为 `async`**。进程内锁用 `asyncio.Lock`，跨进程锁用 `filelock.FileLock`。SQLite 使用 WAL 模式支持多协程并发读。**严禁 `threading.Lock`**。

---

## 2. 技术选型表（真源锁定）

| 组件 | 首选 | 备选 | 不推荐 | 选型理由 | 升级触发 | 相关 KB 决策记录 |
|------|----------------|------|-------|---------|---------|----------|
| 任务队列 | **SQLite (WAL) + asyncio.Queue** | Redis + arq | Celery（重）/ Airflow（重） | 零外部依赖，Windows 原生 | 任务量 > 100/天 或并发 > 10 | KBG-0017 |
| 状态机 | **Python enum + dataclass** | `transitions` 库 | FSM 框架 | 最小依赖，静态类型可校验 | 状态数 > 20 | KBG-0017 |
| 任务存储 | **SQLite（WAL）** | PostgreSQL | Markdown 文件 | 事务、崩溃恢复、易备份 | 数据 > 5GB | KBG-0017 |
| Agent 通信 | **SQLite 共享状态表 + asyncio.Event** | NATS JetStream | 文件锁 | 零外部依赖 | 跨进程/跨机通信 | KBG-0017 |
| 沙箱（Windows 首选） | **Windows ACL + 只读挂载** | Docker Desktop（升级） | gVisor（Windows 兼容差）| 当前平台 Windows，轻量 | 需要完整容器隔离 | KBG-0018 |
| 沙箱（Linux/CI） | Docker Desktop | Firejail | - | 一致性 | - | KBG-0018 |
| 幻觉检测 | **规则引擎 + 阈值（N 次无进展即终止）** | 轻量 ML 分类器 | LLM 自己判（成本高）| 确定性，可审计 | 误报率 > 30% | KBG-0017 |
| 健康监控 | **内存指标 + SQLite** | Prometheus | 外部 APM | 零外部依赖 | 跨机部署 | KBG-0017 |
| 进程内并发 | **`asyncio.Lock`** | - | `threading.Lock`（阻塞事件循环） | 项目全异步栈 | 服务化后废除 | - |
| 跨进程并发 | **`filelock.FileLock`** | SQLite 事务 | 全局单例 | pytest 并发 + 多 Agent | 服务化后废除 | - |

---

## 3. 核心数据模型

### 3.1 Task 状态机

```python
# src/zephyr/orchestration/runtime_core/orchestrator/state.py (experimental 产出)

from enum import Enum

class TaskState(str, Enum):
    DRAFT      = "draft"       # 已创建未提交
    QUEUED     = "queued"      # 已入队等待 Agent 认领
    ASSIGNED   = "assigned"    # 被 Agent claim 未开始
    RUNNING    = "running"     # 执行中
    BLOCKED    = "blocked"     # 被依赖阻塞
    REVIEWING  = "reviewing"   # 等待 LSG 审查输出
    COMPLETED  = "completed"   # 成功完成
    FAILED     = "failed"      # 失败
    CANCELLED  = "cancelled"   # 主动取消
    HALLUCINATING = "hallucinating"  # 幻觉检测触发，隔离待清理

# 合法状态转移（非法转移直接抛 IllegalStateTransitionError）
ALLOWED_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.DRAFT:      {TaskState.QUEUED, TaskState.CANCELLED},
    TaskState.QUEUED:     {TaskState.ASSIGNED, TaskState.CANCELLED},
    TaskState.ASSIGNED:   {TaskState.RUNNING, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.RUNNING:    {TaskState.REVIEWING, TaskState.BLOCKED, TaskState.FAILED,
                           TaskState.HALLUCINATING, TaskState.CANCELLED},
    TaskState.BLOCKED:    {TaskState.RUNNING, TaskState.CANCELLED, TaskState.FAILED},
    TaskState.REVIEWING:  {TaskState.COMPLETED, TaskState.FAILED, TaskState.RUNNING},  # review 挂后退回 RUNNING 允许重试
    TaskState.HALLUCINATING: {TaskState.CANCELLED, TaskState.FAILED},
    TaskState.COMPLETED:  set(),  # 终态
    TaskState.FAILED:     set(),  # 终态
    TaskState.CANCELLED:  set(),  # 终态
}
```

### 3.2 Pydantic Schemas

```python
# src/zephyr/integration/shared/schema/schemas.py

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class TaskSubmit(BaseModel):
    task_card_path: str = Field(description="任务卡 YAML 文件路径")
    priority: int = Field(default=5, ge=1, le=10)
    depends_on: list[str] = Field(default_factory=list, description="前置任务 task_id")
    required_capabilities: list[str] = Field(default_factory=list,
        description="Agent 必备能力，如 ['python', 'pandas', 'backtest']")
    timeout_seconds: int = Field(default=3600, ge=60, le=86400)
    sandbox_policy: Optional["SandboxPolicy"] = None

class Task(BaseModel):
    task_id: str
    state: TaskState
    submitted_at: datetime
    task_card_path: str
    task_card_hash: str
    priority: int
    depends_on: list[str]
    required_capabilities: list[str]
    claimed_by: Optional[str] = None
    sandbox_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_seconds: int
    retry_count: int = 0
    last_progress_at: Optional[datetime] = None
    metrics: dict = Field(default_factory=dict)

class AgentSpec(BaseModel):
    agent_id: str
    agent_kind: Literal["implementer", "reviewer", "tester", "planner", "generic"]
    capabilities: list[str]
    max_concurrent_tasks: int = Field(default=1, ge=1, le=10)
    heartbeat_interval_seconds: int = Field(default=30)

class AgentProgress(BaseModel):
    task_id: str
    agent_id: str
    stage: Literal["planning", "coding", "testing", "reviewing"]
    files_touched: list[str]
    tokens_consumed: int
    tools_invoked: list[str]
    observation_hash: str = Field(description="本次进度观测指纹，用于幻觉循环检测")
    timestamp: datetime

class TaskResult(BaseModel):
    task_id: str
    output_files: list[str]
    test_passed: bool
    test_report_path: Optional[str] = None
    metrics: dict
    summary: str = Field(description="自然语言摘要，入 VMS task_history")

class TaskFailure(BaseModel):
    task_id: str
    failure_kind: Literal[
        "timeout",
        "exception",
        "test_failed",
        "review_rejected",
        "hallucination_detected",
        "sandbox_violation",
        "dependency_failed",
    ]
    message: str
    retryable: bool
    stack_trace: Optional[str] = None

class SandboxPolicy(BaseModel):
    writable_paths: list[str] = Field(description="白名单可写路径（相对 repo root）")
    readable_paths: list[str] = Field(default_factory=list,
        description="白名单可读路径，默认整个 repo 只读")
    network_access: Literal["none", "local_only", "full"] = "none"
    max_memory_mb: int = Field(default=2048)
    max_cpu_seconds: int = Field(default=3600)
    allowed_commands: list[str] = Field(default_factory=list,
        description="白名单可执行命令，为空=拒绝所有命令执行")

class Sandbox(BaseModel):
    sandbox_id: str
    task_id: str
    kind: Literal["windows_acl", "docker", "none"]
    mount_root: str = Field(description="Agent 感知的根目录，Agent 所有路径必经此前缀")
    policy: SandboxPolicy
    created_at: datetime
    expires_at: datetime
```

### 3.3 幻觉循环检测规则

```python
# src/zephyr/orchestration/runtime_core/orchestrator/hallucination.py (experimental 产出)

# 基础规则：Agent 连续 N 次 AgentProgress.observation_hash 相同 → 陷入循环
HALLUCINATION_RULES = {
    "loop_same_observation": {
        "threshold_count": 3,
        "window_seconds": 120,
        "action": "transition_to_hallucinating",
    },
    "no_progress_timeout": {
        "threshold_seconds": 300,  # 5 分钟无 progress 上报
        "action": "transition_to_hallucinating",
    },
    "token_budget_exceeded": {
        "threshold_multiplier": 3.0,  # 超预算 3 倍
        "action": "transition_to_hallucinating",
    },
    "repeated_same_file_edit": {
        "threshold_count": 10,  # 同一文件 10 次编辑
        "window_seconds": 600,
        "action": "transition_to_hallucinating",
    },
    "tool_call_explosion": {
        "threshold_count_per_minute": 50,
        "action": "transition_to_hallucinating",
    },
}

# 触发动作：transition_to_hallucinating → 上报 FLE（signal=hallucination_spike）→ 销毁沙箱 → 任务转 FAILED
```

---

## 4. API 设计

### 4.1 任务 API

```python
class InProcessOrchestrator:

    async def submit_task(self, submit: TaskSubmit) -> TaskHandle:
        """
        提交任务。校验任务卡存在、依赖存在、capabilities 描述合法。
        状态：DRAFT → QUEUED（自动）。
        返回 handle，供调用方 await 终态。
        """

    async def get_task(self, task_id: str) -> Task | None: ...

    async def list_tasks(
        self,
        state: TaskState | list[TaskState] | None = None,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[Task]: ...

    async def cancel_task(self, task_id: str, reason: str) -> CancelResult:
        """状态转 CANCELLED，若 RUNNING 则先销毁沙箱与通知 Agent。"""
```

### 4.2 Agent API

```python
    async def register_agent(self, spec: AgentSpec) -> AgentHandle:
        """Agent 启动时调用。失败场景：agent_id 重复。"""

    async def claim_task(
        self,
        agent_id: str,
        capabilities: list[str],
    ) -> Task | None:
        """
        拉取一个 QUEUED 任务，要求：依赖全 COMPLETED + capabilities 覆盖任务需求。
        原子性由 SQLite 事务保证，避免两 Agent 拿到同一任务。
        状态：QUEUED → ASSIGNED。
        """

    async def report_progress(
        self,
        agent_id: str,
        task_id: str,
        progress: AgentProgress,
    ) -> None:
        """
        Agent 执行中周期上报（心跳）。
        内部动作：
          1. 更新 last_progress_at
          2. 运行 §3.3 幻觉检测规则
          3. 若命中 → 状态转 HALLUCINATING，销毁沙箱，上报 FLE
        首次 report_progress 时：ASSIGNED → RUNNING。
        """

    async def complete_task(
        self,
        agent_id: str,
        task_id: str,
        result: TaskResult,
    ) -> CompleteResult:
        """
        Agent 声明完成。
        内部流程：
          1. 状态 RUNNING → REVIEWING
          2. 调用 LSG 审查输出 schema（若 LSG 启用）
          3. 若 result.test_passed=False → 转 FAILED
          4. 审查通过 → REVIEWING → COMPLETED
          5. 写 VMS task_history（软失败，不阻塞）
          6. 销毁沙箱
          7. 上报 FLE 完成指标
        """

    async def fail_task(
        self,
        agent_id: str,
        task_id: str,
        failure: TaskFailure,
    ) -> None:
        """
        Agent 主动声明失败。
        状态：* → FAILED（或 retryable 且 retry_count < max_retry 则 → QUEUED）。
        """

    async def heartbeat(self, agent_id: str) -> None: ...
```

### 4.3 沙箱 API

```python
    async def provision_sandbox(
        self,
        task_id: str,
        policy: SandboxPolicy,
    ) -> Sandbox:
        """
        为任务创建沙箱。
        Windows 默认：
          - repo 整体只读挂载
          - writable_paths 白名单创建可写 overlay 目录
          - network_access='none' 通过防火墙规则隔离
        超时自动销毁（配 expires_at）。
        """

    async def destroy_sandbox(self, sandbox_id: str) -> None: ...

    async def verify_sandbox_violation(
        self,
        sandbox_id: str,
    ) -> list[SandboxViolation]:
        """
        检查沙箱自创建以来的越界行为（试图写白名单外路径 / 发起外部网络 等）。
        任一违规 → 任务转 HALLUCINATING，上报 FLE（signal 类型 sandbox_violation 扩展）。
        """
```

### 4.4 HTTP API（beta 预留骨架）

| Method + Path | 对应库方法 |
|---------------|-----------|
| `POST /v1/tasks` | `submit_task()` |
| `GET /v1/tasks/{task_id}` | `get_task()` |
| `GET /v1/tasks?state=&agent=` | `list_tasks()` |
| `POST /v1/tasks/{task_id}/cancel` | `cancel_task()` |
| `POST /v1/agents` | `register_agent()` |
| `POST /v1/agents/{agent_id}/claim` | `claim_task()` |
| `POST /v1/tasks/{task_id}/progress` | `report_progress()` |
| `POST /v1/tasks/{task_id}/complete` | `complete_task()` |
| `POST /v1/tasks/{task_id}/fail` | `fail_task()` |
| `POST /v1/sandboxes` | `provision_sandbox()` |
| `DELETE /v1/sandboxes/{sandbox_id}` | `destroy_sandbox()` |
| `GET /v1/stats` | `stats()` |

---

## 5. 状态机与生命周期

### 5.1 典型生命周期

```
[Caller] submit_task(task_card)
  DRAFT → QUEUED
[Orchestrator] 扫描依赖，满足条件的任务暴露给 claim_task
[Agent A] claim_task(agent_id, capabilities)
  QUEUED → ASSIGNED
[Orchestrator] provision_sandbox(policy) → Sandbox
[Agent A] 执行循环：
  report_progress() 第一次：ASSIGNED → RUNNING
  report_progress() 周期上报（幻觉检测运行）
  complete_task(result)
    RUNNING → REVIEWING
    → LSG schema 校验 → VMS 写 task_history → destroy_sandbox
    REVIEWING → COMPLETED
```

### 5.2 异常路径

```
幻觉触发 → HALLUCINATING → 销毁沙箱 → 上报 FLE → CANCELLED/FAILED
沙箱越界 → 同上
依赖失败 → 所有依赖该任务的任务 → BLOCKED → FAILED
超时 → FAILED（retryable 则 → QUEUED，retry_count+1）
review 拒绝 → REVIEWING → RUNNING 或 FAILED（看 retryable）
```

---

## 6. 沙箱与安全隔离

### 6.1 Windows ACL 沙箱实现要点（experimental 默认）

- repo 根目录整体 ACL 只读给 Agent 进程用户
- `writable_paths` 每项创建 overlay 目录，softlink 到 `.runtime/sandboxes/<sid>/writable/<path>/`
- Agent 进程以独立受限用户运行（避免继承调用者权限）
- 网络隔离通过 Windows Defender Firewall 规则在沙箱期间禁用出站（`network_access='none'`）
- `allowed_commands` 通过 AppLocker 策略或自建命令白名单 wrapper

### 6.2 Docker Desktop 沙箱（升级路径）

触发条件：需要完整 syscall 隔离 / CI 环境 / 不信任的第三方 Agent

- 挂载 repo 为只读 bind mount
- `writable_paths` 作为可写 tmpfs overlay
- `--network=none` 默认
- 资源限制：`--memory`, `--cpus`, `--pids-limit`

### 6.3 沙箱违规检测

```
文件系统审计 → Windows 审计策略 + FileSystemWatcher 监听 writable_paths 外写操作
命令执行审计 → 进程创建事件监听
网络违规     → Firewall 日志扫描
```

---

## 7. 前置条件与依赖

| 前置项 | 状态 |
|-------|:----:|
| `src/zephyr/orchestrator/` 包创建 | ⏳ 待建 |
| SQLite schema 脚本 | ⏳ experimental T-1-XX |
| Context Engine（上游，拉任务上下文） | ⏳ B-a-2 产出 + experimental 实现 |
| LSG Protocol（审查 complete 结果 schema） | ⏳ B-a-5 产出 + beta 实现 |
| VMS（任务完成写 task_history） | ⏳ B-a-1 产出 + experimental 实现 |
| KBG-0017 / KBG-0018 批准 | ⏳ pending B-e |

**Python 依赖**：

```toml
[project.optional-dependencies]
orchestrator = [
    "aiosqlite>=0.19",
    "filelock>=3.13",
    "pydantic>=2.5,<3.0",
    "psutil>=5.9",  # 资源监控
]
```

---

## 8. 文件清单与落位（不留 placeholder）

```

├── src/zephyr/
│   ├── orchestrator/                               # ⏳ experimental 新建
│   │   ├── __init__.py                             # 导出 get_orc()
│   │   ├── protocol.py                             # OrchestratorProtocol
│   │   ├── in_process.py                           # experimental 实现
│   │   ├── distributed.py                          # beta+ 占位
│   │   ├── schemas.py                              # Pydantic schemas
│   │   ├── state.py                                # TaskState + ALLOWED_TRANSITIONS
│   │   ├── queue.py                                # SQLite + asyncio.Queue
│   │   ├── agent_registry.py                       # Agent 管理
│   │   ├── hallucination.py                        # 幻觉规则引擎
│   │   ├── sandbox/
│   │   │   ├── base.py                             # SandboxProtocol
│   │   │   ├── windows_acl.py                      # experimental 默认
│   │   │   ├── docker_desktop.py                   # beta 升级
│   │   │   └── noop.py                             # 测试/本地开发
│   │   ├── db.py                                   # SQLite WAL schema
│   │   └── config.py                               # OrchestratorConfig
│   └── config/
│       ├── orchestrator.yaml
│       └── hallucination_rules.yaml                # §3.3 规则外置
│
├── .runtime/
│   ├── orchestrator/
│   │   ├── data/databases/governance.db                                # SQLite WAL
│   │   ├── data/databases/governance.db-wal
│   │   └── data/databases/governance.db-shm
│   ├── sandboxes/
│   │   └── <sandbox_id>/                           # 各任务独立沙箱
│   │       └── writable/                           # overlay 可写目录
│   └── logs/
│       ├── orchestrator.log
│       ├── hallucination_events.log
│       └── sandbox_violations.log
│
├── tests/
│   ├── test_state_machine.py                       # 合法/非法转移全覆盖
│   ├── test_submit_and_claim.py
│   ├── test_concurrent_claim.py                    # 多 Agent 抢锁
│   ├── test_progress_and_hallucination.py
│   ├── test_complete_and_archive.py                # 写 VMS 路径
│   ├── test_sandbox_windows_acl.py
│   ├── test_sandbox_violation_detection.py
│   ├── test_cold_start.py
│   └── test_degrade_paths.py
│
└── .gitignore                                      # 已追加 .runtime/
```

---

## 9. 集成点

### 9.1 上游依赖

| 上游 | 关系 | 调用 |
|------|------|------|
| 任务卡文件系统 | 必须 | submit_task 读 YAML |
| **Context Engine**（必须） | 必须 | Agent claim 后调 `ce.build(ctx_request)` |
| **LSG**（可选） | 可选 | complete 时调 `lsg.validate_output(result)` |
| **VMS**（必须） | 必须 | 完成时 `vm.ingest(task_history_doc)` |

### 9.2 下游消费者

| 下游 | 关系 | 调用姿态 |
|------|------|---------|
| **Feedback Loop Engine** | 必须 | Orchestrator push 指标（task_completed / failed / hallucinated / duration / cost） |
| Dashboard `task_overview.py` | 可选 | `await orc.list_tasks() / stats()` |
| CI/CD | 可选 | submit_task 触发验收任务 |

### 9.3 FLE 单向依赖（Protocol 引用）

```python
# src/zephyr/orchestration/runtime_core/orchestrator/feedback_sink.py

from typing import Protocol

class FeedbackSinkProtocol(Protocol):
    """Orchestrator 只知道这个 Protocol，不 import FLE 具体实现。"""
    async def record_task_metrics(self, metrics: TaskMetrics) -> None: ...
    async def record_hallucination_event(self, event: HallucinationEvent) -> None: ...

# 注入：
#   orc = InProcessOrchestrator(feedback_sink=get_fle(), ...)
#   没注入 FLE 时，使用 NoopFeedbackSink 不阻塞
```

---

## 10. 渐进路线

| Phase | 范围 | 验收标准 |
|:-:|------|---------|
| **scaffold**（当前） | 接口规范 + KBG-0017/0018 | status=Active |
| **experimental** | `InProcessOrchestrator` + Windows ACL sandbox + 幻觉基础规则 | ① §13 P0 用例通过<br>② 单进程 5 Agent 并发不死锁<br>③ 沙箱越界检测无漏报 |
| **beta** | LSG 接入 + FLE 反馈通道接入 + VMS task_history 归档 | 完整闭环；Docker Desktop 沙箱可选启用 |
| **beta** | `DistributedOrchestrator`（ARQ + Redis） | 任务量 > 100/天 触发；兼容单进程 API |
| **stable** | NATS JetStream + 跨机 Agent | 跨机实时协调 |

---

## 11. 错误码与降级策略

### 11.1 异常层级

```python
class OrcError(Exception): ...
class OrcConfigError(OrcError): ...
class OrcQueueError(OrcError): ...                   # SQLite 读写失败
class IllegalStateTransitionError(OrcError): ...     # 非法状态转移
class SandboxProvisionError(OrcError): ...           # 沙箱创建失败
class SandboxViolationError(OrcError): ...           # 沙箱越界
class HallucinationDetectedError(OrcError): ...      # 幻觉终止
class DependencyFailedError(OrcError): ...
```

### 11.2 P0 级降级条款

> **核心原则**：Orchestrator 是"任务中枢"——核心功能挂了无人接任务，**允许降级到无 FLE/无 VMS 的最小闭环，但严禁降级沙箱（安全不可退让）**。

**DEGRADE-001：FLE 不可用时降级为日志记录**

触发场景：FLE 进程挂 / `record_task_metrics` 抛异常

降级动作：
```python
try:
    await self._feedback_sink.record_task_metrics(metrics)
except Exception as e:
    log_structured("orc_degrade", code="DEGRADE-001", task_id=tid, reason=str(e))
    # 写入 .runtime/orchestrator/pending_metrics.ndjson 待 FLE 恢复后回放
```
**上游契约**：FLE 恢复时应调 `orc.replay_pending_metrics()` 消费积压。

**DEGRADE-002：VMS 写 task_history 失败时转本地归档**

触发场景：任务 COMPLETED 后 `vm.ingest` 失败（VMS 降级中）

降级动作：
```python
try:
    await vm.ingest(task_history_doc)
except VMError:
    # 保持写 .runtime/orchestrator/pending_task_history/<task_id>.yaml
    # 任务仍标记 COMPLETED（不因归档失败而失败）
    log_structured("orc_degrade", code="DEGRADE-002", task_id=tid)
```
**上游契约**：VMS 恢复时 `orc.replay_pending_task_history()` 回放。

**DEGRADE-003：沙箱创建失败绝不降级**

触发场景：Windows ACL 配置失败 / Docker Desktop 未启动

**不降级**：`provision_sandbox` 失败 → 任务状态转 FAILED，`failure_kind='sandbox_violation'`。

**上游契约**：安全红线，沙箱是 SEC-02 修复的核心手段，宁可任务全挂也不能让 Agent 裸跑。

### 11.3 降级条件速查表

| 触发条件 | 降级动作 | 上游感知 |
|---------|---------|---------|
| FLE 不可用 | 写 pending_metrics.ndjson | DEGRADE-001 |
| VMS 写 task_history 失败 | 写 pending_task_history | DEGRADE-002 |
| Context Engine build 失败 | 任务转 FAILED，retryable=True | 日志告警 |
| LSG 审查失败 | 任务转 FAILED，不重试 | 日志告警 |
| **沙箱创建失败** | **不降级**，任务 FAILED | **DEGRADE-003**（红线） |
| SQLite WAL 读失败 | 抛 OrcQueueError，不降级（基础设施） | 日志告警 |
| 单 Agent 心跳超时 | Agent 标记 dead，任务超时重排 | 日志 |

所有降级写 `logs/orchestrator_degrade.log`（结构化 JSON）。

---

## 12. 性能 SLO

### 12.1 稳态 SLO

| 指标 | 目标 | 条件 |
|------|------|------|
| `submit_task()` p50 | ≤ 20 ms | - |
| `claim_task()` p95 | ≤ 50 ms | 5 Agent 并发 |
| `report_progress()` p95 | ≤ 15 ms | 含幻觉规则运行 |
| `complete_task()` p95 | ≤ 500 ms | 含 LSG 审查 + VMS 写入 |
| `provision_sandbox()` Windows ACL p95 | ≤ 800 ms | - |
| `provision_sandbox()` Docker p95 | ≤ 3000 ms | - |
| 幻觉检测实时性 | ≤ 1 心跳周期内触发 | - |
| 最大并发 Task | 10 | 单进程 |

### 12.2 冷启动 SLO

| 指标 | 目标 | 说明 |
|------|------|------|
| 进程 import | ≤ 1.5 s | 仅 import orchestrator |
| SQLite schema check + 连接 | ≤ 500 ms | WAL 启用 |
| Agent registry 加载 | ≤ 300 ms | 从 DB 恢复 |
| Pending tasks 重排（崩溃恢复） | ≤ 2 s | 扫描 ASSIGNED/RUNNING 状态任务标记超时或重排 |
| 首次 `submit_task()` | ≤ 100 ms | 含首次 DB 写入 |
| **总冷启动到可用** | **≤ 5 s** | - |

---

## 13. 测试用例（P0）

### 13.1 状态机 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-S1 | DRAFT → QUEUED 合法 | 通过 |
| P0-S2 | COMPLETED → RUNNING 非法 | 抛 IllegalStateTransitionError |
| P0-S3 | 所有合法转移路径全覆盖 | 全部通过 |
| P0-S4 | 并发 claim 原子性 | 两 Agent 同时 claim 同一 task，只有一个成功 |

### 13.2 任务流 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-T1 | 完整 happy path（submit→claim→progress→complete） | 状态全正确，task_history 入 VMS |
| P0-T2 | 依赖链（A→B→C） | B 等 A 完成才 QUEUED |
| P0-T3 | 超时自动 FAILED | timeout_seconds=60，不 report_progress 后 FAILED |
| P0-T4 | retryable 失败重排 | retry_count +1, 回 QUEUED |

### 13.3 幻觉检测 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-H1 | 连续 3 次相同 observation_hash | 状态转 HALLUCINATING，沙箱销毁，FLE 事件上报 |
| P0-H2 | 5 分钟无 progress | 同上 |
| P0-H3 | 同一文件 10 次编辑 | 同上 |
| P0-H4 | token 预算超 3 倍 | 同上 |

### 13.4 沙箱 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-B1 | Windows ACL 基本隔离 | Agent 写白名单外路径失败 |
| P0-B2 | 越界检测 | 写非 writable_paths 路径被记录并转 HALLUCINATING |
| P0-B3 | 销毁后无残留 | writable overlay 目录全清 |
| P0-B4 | 沙箱创建失败任务 FAILED（**DEGRADE-003 红线**） | 不降级，任务 failure_kind='sandbox_violation' |

### 13.5 降级 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-D1 | FLE 挂 | complete 仍成功，pending_metrics 落盘，DEGRADE-001 日志 |
| P0-D2 | VMS 写失败 | 任务仍 COMPLETED，pending_task_history 落盘，DEGRADE-002 日志 |
| P0-D3 | 沙箱创建失败 | **不降级**，任务 FAILED |

### 13.6 冷启动 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-C1 | 崩溃后启动恢复 | ASSIGNED/RUNNING 任务全部超时重排为 QUEUED |
| P0-C2 | 冷启动总耗时 ≤ 5s | - |

---

## 14. 修订记录

| 日期 | 版本 | 说明 |
|------|:-:|------|
| 2026-04-24 | 1.0.0 | 初版（B-a-3）。基于 VMS v1.2 模板 + KBG-0017/0018。重点：① 完整 TaskState 状态机强校验；② §3.3 幻觉检测规则引擎；③ §6 Windows ACL 沙箱+ Docker Desktop 升级；④ §11.2 DEGRADE-003 沙箱创建失败不降级（安全红线）；⑤ FLE/VMS 单向 Protocol 依赖，挂了可降级不阻塞。 |
