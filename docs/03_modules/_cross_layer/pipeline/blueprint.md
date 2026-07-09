---
module_id: MOD-INF-009
submodule_path: src/zephyr/integration
title: "Pipeline 蓝图 — 管线编排器·M1-M11门控流水线"
doc_type: blueprint
status: Active
version: "0.39.1"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: design_only
actual_disk_path: "src/zephyr/integration/"
last_updated: "2026-05-14"
last_verified: "2026-05-14"
generation: 2
functional_domain: execution
summary: "Pipeline管线编排器——M1-M11双管线架构(A区生产+B区审计)+三层模型路由+容量升级至1500模块/10K脚本/100AI并发"
tags: [pipeline, m1-m11, dual-pipeline, model-routing, pipeline-orchestrator, backpressure, capacity-upgrade, incremental-scan, circuit-breaker, dead-letter-queue, blind-review, fallback-chain, pipeline-lock, agent-bridge, zone-crossing, artifact-manifest, preemption, lsg, cost-tracking, data-lineage]
priority: P0
runtime_plane: hot
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
rule_form: structural
scope: global
stability: evolving
responsibility_domain: 
depends_on:
  - {target: "MOD-MASTER_BLUEPRINT", at: "§2.7", why: "CT-PIPE-ORC-001 集成契约——Pipeline→Orc路由决策"}
  - {target: "MOD-TASK_SYSTEM", at: "§5", why: "任务系统——M1-M11节点的任务消费方"}
  - {target: "GOV-AI-002", at: "全篇", why: "模型路由策略——Pipeline决策树依据"}
  - {target: "MOD-INF-016", at: "全篇", why: "共享基础设施——LifecycleAware/EventBus/TelemetryEmitter/MetricsRegistry 契约"}
  - {target: "MOD-LLM_SECURITY", at: "全篇", why: "LSG安全闸门——Pipeline L1/L3 输入输出检测"}
  - {target: "MOD-DATABASE", at: "全篇", why: "DeferredQueue——LOCKED任务自动重试"}
  - {target: "MOD-INF-001", at: "§Kill Switch+§Token Budget", why: "Capacity Assurance——Kill Switch前置检查+Token Budget扣减"}
references:
  - {id: "MOD-INF-020", at: "全篇", why: "Decision Log——仅存 references（打破 009↔020↔022 环）"}
  - {id: "MOD-INF-018", at: "全篇", why: "SoD——仅存 references"}
  - {id: "architecture_model/layers/b_pipeline.yaml", at: "全篇", why: "Pipeline YAML SSoT——本蓝图真源"}
design_maturity: design
build_status: planned
---

> module_id: MOD-INF-009 | version: 0.39.1 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/integration/pipeline_orchestrator.py | generation: 2 | construction_progress: partially_implemented

# Pipeline 蓝图 — 管线编排器·M1-M11门控流水线

## 概述

本蓝图描述 Pipeline 管线编排器——它解决了"AI 任务如何从创建到审计全链路受控执行"的核心问题。核心职责包括：M1-M11 双管线调度（A 区生产 + B 区审计）、三层模型路由（DeepSeek/GLM/Claude + Fallback 链）、并发锁与优先级抢占、容量升级至 1500 模块/10K 脚本/100 AI 并发。当前规模 51 模块/268 脚本/0 AI 并发，目标容量 1500/10000/100。上游依赖 Orchestrator（CT-PIPE-ORC-001）和 Task System（MOD-TASK_SYSTEM），下游被 Gate Engine、Feedback Loop、Audit Trail 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> 防止 construction_progress 与实际代码不符。
> 每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§15）。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-009`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §3 | 模块导出——30+ 公开符号 | 已实现 | |
| 2 | `models.py` | §4 | Pydantic V2 数据模型（全部 30+ 类） | 已实现 | |
| 3 | `pipeline_orchestrator.py` | §4.1 | 管线协调器——dispatch/route/fallback/blind_review/preempt/lock | 已实现 | |
| 4 | `ct_pipe_routing.py` | §3 | CT-PIPE-ORC-001 路由解析 | 已实现 | |
| 5 | `routing_plugins.py` | §3 | K8s Filter→Score→Bind 插件架构 + PipelineRouter | 已实现 | |
| 6 | `pipeline_lock.py` | §3 | 并发文件锁——MemoryLockBackend + FileLockBackend | 已实现 | |
| 7 | `pipeline_agent_bridge.py` | §3 | Pipeline→AgentOrchestrator 桥接 | 已实现 | |
| 8 | `pipeline_roadmap.py` | §16 | 路线图骨架 + ConstructionPhaseTracker | 已实现 | |
| 9 | `backpressure_manager.py` | §3 | 背压三级响应 | 已实现 | |
| 10 | `circuit_breaker_manager.py` | §3 | 熔断器三态机 | 已实现 | |
| 11 | `cost_tracker.py` | §3 | per-call 成本追踪 | 已实现 | |
| 12 | `dead_letter_queue.py` | §3 | 死信队列 + replay | 已实现 | |
| 13 | `layer_consumer_registry.py` | §3 | 层级消费者注册 | 已实现 | |
| 14 | `layer_router.py` | §3 | 层级路由 | 已实现 | |
| 15 | `model_router.py` | §3 | 模型路由 + 版本锁定 + 限流 | 已实现 | |
| 16 | `preemption_manager.py` | §3 | 优先级抢占 + resume | 已实现 | |
| 17 | `routemanifest.yaml` | §3 | 路由清单 | 已实现 | |
| 18 | `model_profiler/` | §3 | 已提升为顶层包 `src/zephyr/model-profiler/`，详见 MOD-INF-034 蓝图 | 已迁移 | |
| 19 | `model_profiler/benchmark_suite.py` | §3 | 已迁移至 `zephyr.model_profiler.benchmark_suite` | 已迁移 | |
| 20 | `model_profiler/cli.py` | §3 | 已迁移至 `zephyr.model_profiler.cli` | 已迁移 | |
| 21 | `model_profiler/deepseek_v4_chat.py` | §3 | 已迁移至 `zephyr.model_profiler.deepseek_v4_chat` | 已迁移 | |
| 22 | `model_profiler/model_discovery.py` | §3 | 已迁移至 `zephyr.model_profiler.model_discovery` | 已迁移 | |
| 23 | `model_profiler/profiler.py` | §3 | 已迁移至 `zephyr.model_profiler.profiler` | 已迁移 | |
| 24 | `model_profiler/results_writer.py` | §3 | 已迁移至 `zephyr.model_profiler.results_writer` | 已迁移 | |
| 25 | `model_profiler/task_model_learner.py` | §3 | 已迁移至 `zephyr.model_profiler.task_model_learner` | 已迁移 | |
| `backpressure_types.py` | § — | — | 已实现 | | 本模块 |
| `llm_gateway.py` | § — | — | 已实现 | | 本模块 |
| `model_profiler/capability_passport.py` | § — | — | 已实现 | | 本模块 |
| `model_profiler/exam_orchestrator.py` | § — | — | 已实现 | | 本模块 |
| `model_profiler/exam_test_cases.py` | § — | — | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按 §0.1 清单核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| actual_disk_path = §11 业务代码路径 | `ls D:\ZephyrAlpha\src\zephyr\pipeline\` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.37.0 (基线) | dispatch/route/fallback/lock/blind_review/telemetry/lifecycle/zone_crossing/lsg/lineage/circuit_breaker/cost_tracking/dead_letter | — | — |
| v0.38.0 (容量升级) | backpressure_manager/circuit_breaker_manager/cost_tracker/dead_letter_queue/model_router/layer_router/preemption_manager/model-profiler/ | IncrementalScanOrchestrator, ScriptImpactMap, ShardRouter 4→16, CapacityCalibrator | 待施工（Phase B/C） |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 的 AI 任务需要从创建到审计全链路受控执行。当前 Pipeline 串行调度 M1-M11，并发参数硬编码为小数值（max_concurrent=1, max_parallel=2），无增量扫描能力，无设计容量声明。系统面临 30× 模块增长（51→1500）和 37× 脚本增长（268→10000）的规模压力。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | M1-M11 双管线调度 | A 区 M1-M5 串行生产 + B 区 M6-M11 审计（M8/M9 可并行） |
| 2 | 三层模型路由 + Fallback | DeepSeek→GLM→Claude 降级链 + M3/M7 双盲审查 |
| 3 | 容量升级至 1500/10K/100 | 增量扫描 <1min / 全量周检 <3h / 48 并发 worker |
| 4 | 并发安全 | 背压三级响应 + per-session 公平调度 + 跨进程锁 |
| 5 | 可观测性 | 6 项 CapacityWatermark 指标 + Prometheus 端点 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 金融交易执行（FIX 协议/交易所连接） | 业务层→地基阶段暂不开发 |
| 2 | 多资产多市场组合管理 | 纯业务层→留待业务层任务卡 |
| 3 | Paper Trading 验证 | 业务层→地基阶段暂不开发 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Windows 11 笔记本（i7-12700KF 12C/20T, 64GB, NVMe, RTX 3090） | 并发上限受 CPU 核数约束→48 ProcessPoolExecutor |
| 单 Owner + AI 24/7 运行 | 无风控官兜底→Pipeline 自身必须具备完整安全防线 |
| 多 IDE 共存（Trae + Cursor + Claude Code） | 跨进程文件锁必须用 os.mkdir 原子操作 |
| Windows Update 强制重启 | 无 SIGTERM→atexit + save_state 必须可靠 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | M1-M11 双管线调度 | A 区生产（M1-M5）+ B 区审计（M6-M11）+ DAG 拓扑排序 |
| 2 | 模型路由决策 | CT-PIPE-ORC-001 路由解析 + Filter→Score→Bind 插件架构 |
| 3 | 三层模型策略 | DeepSeek 主力 + GLM 审查 + Claude 特种救援 + Fallback 链 |
| 4 | 并发控制 | 文件级+层级锁 + 优先级抢占 + 背压管理 |
| 5 | 容量管理 | capacity_params.yaml SSoT + 增量扫描 + 水平分片 |
| 6 | 安全防线 | LSG 闸门 + Zone Crossing + 双盲审查 + SoD 检查 |
| 7 | 可观测性 | Telemetry 3 metrics + 3 trace spans + EventBus + LifecycleAware |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 任务创建与状态机 | MOD-TASK_SYSTEM Task System |
| 2 | 门禁规则评估 | MOD-GATE_ENGINE Gate Engine |
| 3 | 上下文装配 | MOD-CONTEXT_ENGINE Context Engine |
| 4 | 反馈闭环 | MOD-FEEDBACK_LOOP Feedback Loop |
| 5 | Kill Switch / Token Budget | MOD-INF-001 Capacity Assurance |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | PipelineOrchestrator | 管线协调器——dispatch/route/fallback/blind_review/preempt/lock | models.py, ct_pipe_routing.py | 同步调用 |
| 2 | PipelineRouter | K8s Filter→Score→Bind 路由插件 | routing_plugins.py | 同步调用 |
| 3 | PipelineLock | 并发文件锁——MemoryLockBackend + FileLockBackend | pipeline_lock.py | 同步调用 |
| 4 | PipelineAgentBridge | Pipeline→AgentOrchestrator 桥接 | pipeline_agent_bridge.py | 同步调用 |
| 5 | BackpressureManager | 背压三级响应（L1正常/L2警告/L3拒绝） | backpressure_manager.py | 事件 |
| 6 | CircuitBreakerManager | 熔断器三态机 CLOSED→OPEN→HALF_OPEN | circuit_breaker_manager.py | 同步调用 |
| 7 | CostTracker | per-call 成本追踪 + per-model CostRecord | cost_tracker.py | 同步调用 |
| 8 | DeadLetterQueue | 死信队列 + replay | dead_letter_queue.py | 队列 |
| 9 | ModelRouter | 模型路由 + 版本锁定 + 限流 | model_router.py | 同步调用 |
| 10 | LayerRouter | 层级路由 + 消费者注册 | layer_router.py, layer_consumer_registry.py | 同步调用 |
| 11 | PreemptionManager | 优先级抢占 + resume | preemption_manager.py | 同步调用 |
| 12 | ModelProfiler | 模型性能评测 + 基准套件 | model-profiler/ 子模块 | 异步 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | Orchestrator.create_task() | dispatch(task_card) → 路由决策 → M1-M11 执行 → PipelineResult | EventBus / DeferredQueue | TaskCard → PipelineResult |
| 2 | git diff (增量扫描) | IncrementalScanOrchestrator → ScriptImpactMap → BulkheadExecutor | 治理脚本执行 | ScanResult |
| 3 | M3(DeepSeek) + M7(GLM) | 双盲审查 → 共识比较 | M11 门禁裁决 | verdict_A, verdict_B |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| PENDING | dispatch() 调用 | IN_PROGRESS | 锁获取成功 + Kill Switch 未触发 |
| IN_PROGRESS | 模块执行完成 | COMPLETED | 所有 M 节点通过 |
| IN_PROGRESS | 模块执行失败 | FAILED | Fallback 链耗尽 |
| IN_PROGRESS | 锁冲突 | LOCKED | PipelineLock.acquire() 返回冲突 |
| LOCKED | 锁释放 | PENDING | DeferredQueue auto-retry |
| IN_PROGRESS | P0 抢占 | PAUSED | PreemptionManager 触发 |
| PAUSED | P0 完成 | IN_PROGRESS | resume_preempted() |
| IN_PROGRESS | Emergency 触发 | PREEMPTED | SEV1/Kill Switch 事件 |

---

## §4 接口契约

### 4.1 公共 API

```python
class PipelineOrchestrator:
    """管线协调器——M1-M11 双管线调度核心"""

    def dispatch(self, task_card: "TaskCard", dry_run: bool = False) -> "PipelineResult":
        """
        调度任务通过 M1-M11 管线

        输入：task_card 含 task_type/priority/target_layer/estimated_complexity
        输出：PipelineResult 含 status/artifacts/module_results/cost_usd
        核心逻辑：路由决策→锁获取→逐模块执行→Fallback→双盲审查→门禁裁决
        """

    def save_state(self, path: str) -> None:
        """持久化当前状态（锁/成本/熔断器/缓存）→ 原子写入"""

    def load_state(self, path: str) -> None:
        """从持久化恢复状态→ checksum 校验"""
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class PipelineStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    LOCKED = "locked"
    PAUSED = "paused"
    PREEMPTED = "preempted"

class RoutingDecision(BaseModel):
    task_id: str = Field(..., description="任务ID")
    node_id: str = Field(..., description="M节点ID")
    execution_model: str = Field(..., description="执行模型")
    sandbox_profile: str = Field(..., description="沙箱配置")
    gate_profile: str = Field(..., description="门禁配置")

class ModuleResult(BaseModel):
    module_id: str = Field(..., description="M节点ID")
    status: str = Field(..., description="pass/fail/skip")
    artifacts: list = Field(default_factory=list)
    tokens_used: int = Field(default=0)
    cost_usd: float = Field(default=0.0)

class PipelineResult(BaseModel):
    task_id: str
    status: PipelineStatus
    module_results: list[ModuleResult] = Field(default_factory=list)
    artifacts: list = Field(default_factory=list)
    cost_usd: float = Field(default=0.0)
    is_dry_run: bool = Field(default=False)

class ArtifactClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `dispatch()` | `task_card` | ✅ | TaskCard 实例，含 task_type/priority |
| `dispatch()` | `dry_run` | ❌ | bool，默认 False |
| `save_state()` | `path` | ✅ | 绝对路径，目录必须存在 |
| `load_state()` | `path` | ✅ | 绝对路径，文件必须存在 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `dispatch()` | `PipelineResult(status=COMPLETED)` | `LOCKED` / `FAILED` / `PREEMPTED` |
| `save_state()` | 文件写入成功 | `PermissionError` / `OSError` |
| `load_state()` | 状态恢复成功 | `FileNotFoundError` / `ValueError`(checksum 不匹配) |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 PipelineStatus 枚举值 | ✅ 向后兼容 | PREEMPTED 新增 |
| 新增 ModuleResult 字段 | ✅ 向后兼容 | 有默认值 |
| 删除/重命名 PipelineResult 字段 | ❌ 破坏性 | 需 Owner 审批 |
| dispatch() 新增参数 | ✅ 向后兼容 | 有默认值 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 3.12+ + Pydantic V2 | KBG-0040 |
| 2 | Windows NTFS 原子写入 | os.replace() |
| 3 | 跨进程锁用 os.makedirs(exist_ok=False) | 多 IDE 共存 |
| 4 | ProcessPoolExecutor 替代 ThreadPoolExecutor | subprocess I/O 释放 GIL |
| 5 | MAX_PATH 260 字符限制 | 260 字符 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 模块数 | 51 | 1,500 | 1,500 | ✅ | capacity_params.yaml SSoT |
| 脚本数 | 268 | 10,000 | 10,000 | ✅ | 增量扫描 + ScriptImpactMap |
| AI 并发 | 0 | 100 session | 100 | ✅ | 背压三级 + per-session 公平 |
| 并发 worker | 24 | 48 | 48 | ✅ | 16 分片 × 3 ProcessPool |
| 全量扫描耗时 | 3.5h | <3h | 3h | ✅ | 并行优化 |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | route-manifest.yaml | `D:\ZephyrAlpha\src\zephyr\pipeline\route-manifest.yaml` | `D:\ZephyrAlpha\src\zephyr\pipeline\routemanifest.yaml` | 重复文件→保留 snake_case 版本 | Grep 全项目引用并更新 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | DeepSeek API 失败 | HTTP 429/5xx/超时 | Fallback 链：DeepSeek→GLM→Claude | 当前 dispatch |
| 2 | 锁冲突 | PipelineLock.acquire() 返回冲突 | 状态→LOCKED→DeferredQueue auto-retry | 当前 dispatch |
| 3 | 熔断器触发 | 连续 3 次失败（窗口 60s） | CLOSED→OPEN→HALF_OPEN（冷却 30s） | 同模型所有 dispatch |
| 4 | 死信 | 重试耗尽 | DeadLetterQueue + replay + Owner 通知 | 当前 dispatch |
| 5 | Emergency 模式 | SEV1/Kill Switch | P0 bypass / P1 等待 30s→SIGKILL / P2 立即 SIGKILL | 所有运行中 dispatch |
| 6 | 背压过载 | 队列深度 >90% | HTTP 429 + exponential backoff | 新入队 dispatch |
| 7 | Windows Update 重启 | 无 SIGTERM | save_state 原子写入 + atexit handler | 所有 in-flight dispatch |
| 8 | Dispatch Stuttering | 相同 input 失败 >2 次 | STUTTER_DETECTED→停止自动重试→Owner review | 当前 dispatch |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | M3/M7 同模型审查（双盲退化） | 高 | mandatoryAntiAffinity: M3≠M7 模型 | _verify_model_diversity Jaccard 检测 |
| 2 | A 区产出物绕过 M6 直通 B 区 | 高 | Zone Crossing 防线 + _validate_zone_crossing | 单元测试 |
| 3 | LLM 输入/输出注入 | 中 | LSG L1+L3 安全闸门（懒加载 MOD-LLM_SECURITY） | _call_model 检测 |
| 4 | 跨进程锁竞争 | 中 | FileLockBackend os.mkdir 原子锁 + stale PID 清理 | 多 IDE 并发测试 |
| 5 | 数据血缘篡改 | 高 | PipelineLineageChain HMAC-SHA256 不可篡改链 | checksum 校验 |
| 6 | Artifact 越权访问 | 中 | ArtifactClassification 四级标签 | 访问控制检查 |
| 7 | Token 预算超支 | 中 | _check_token_budget 200K 限额 80% 告警 | 预算追踪测试 |
| 8 | SoD 违规（author==reviewer） | 中 | _check_separation_of_duties 检测 | 单元测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | PipelineOrchestrator 全方法 | dispatch/route/fallback/blind_review/preempt/lock | 31 tests PASS |
| 2 | 集成测试 | Pipeline→Orchestrator 桥接 | CT-PIPE-ORC-001 集成 | 端到端通过 |
| 3 | 安全测试 | LSG/Zone Crossing/SoD | L1+L3 检测 + 跨区阻断 | 阻断生效 |
| 4 | 容量测试 | 100 AI 并发模拟 | 增量扫描 <1min | P95 <60s |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-TASK_SYSTEM | 必须 | TaskCard → dispatch() → PipelineResult | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\task_system\blueprint.md` |
| MOD-INF-003 | 必须 | Orc.create_task() → Pipeline.dispatch() | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\orchestrator\blueprint.md` |
| MOD-INF-016 | 必须 | LifecycleAware/EventBus/TelemetryEmitter/MetricsRegistry | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\shared_infrastructure\blueprint.md` |
| MOD-LLM_SECURITY | 必须 | LSG L1+L3 输入输出检测 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\llm_security_gateway\blueprint.md` |
| MOD-GATE_ENGINE | 可选 | G6 检查——AI 是否已读蓝图 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md` |
| MOD-DATABASE | 可选 | DeferredQueue LOCKED→auto-retry | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\deferred_queue\blueprint.md` |
| GOV-AI-002 | 必须 | 模型路由策略决策树 | v2.0.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\policies\ai-model-routing-policy.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-009` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| pipeline_orchestrator.py | pipeline_agent_bridge.py | PipelineOrchestrator 实例是桥接的前置条件 | 检查 PipelineOrchestrator 初始化 |
| model_router.py | model-profiler/profiler.py | ModelRouter 使用 ModelProfiler 的评测结果 | 检查 profiler 产出物 |
| backpressure_manager.py | circuit_breaker_manager.py | 背压 L3 触发熔断器 | 检查熔断器状态 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| pipeline_orchestrator.py | dead_letter_queue.py | 失败的 PipelineResult | 队列 |
| cost_tracker.py | pipeline_orchestrator.py | CostRecord | 函数调用 |
| model-profiler/profiler.py | model_router.py | ModelBenchmark | YAML 文件 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 脚本数>10 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖 |
| 3 | 临时时态内容自动清理 | 是 | 有迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | asset-inventory/dependency.py | 不覆盖scripts/目录 |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\pipeline\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\pipeline\` | Python 源码（18 .py + 2 .yaml + model-profiler/ 子模块 8 文件） |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\test_pipeline_orchestrator.py` | 单元测试 |
| 配置文件 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | 19 条蓝图路由表 |
| 容量参数 | `D:\ZephyrAlpha\config\capacity_params.yaml` | 并发/容量参数 SSoT |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Orchestrator (MOD-INF-003) | CT-PIPE-ORC-001 契约 | Pipeline.dispatch() | 端到端集成测试 |
| Task System (MOD-TASK_SYSTEM) | runtime_call | TaskCard 读取 + PipelineResult 写回 | 单元测试 |
| Gate Engine (MOD-GATE_ENGINE) | pre_check | dispatch() 前 G6 检查 | beta session_simulator |
| LSG (MOD-LLM_SECURITY) | pre_check | _call_model L1+L3 检测 | 安全测试 |
| Shared Infra (MOD-INF-016) | contract_consume | LifecycleAware + EventBus + Telemetry | 集成测试 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 版本→0.39.0 + status→Active | 蓝图升级 |
| 2 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | construction_progress 更新 | 代码状态变更 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 版本更新 | 蓝图升级 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 100 AI 并发时背压不足→队列爆满 | 中 | 高 | 三级背压 L1/L2/L3 + exponential backoff | 风险 |
| 2 | 增量扫描 ScriptImpactMap 精度不足 | 中 | 中 | AI 辅助标记 + Owner 审核 + 回退链 | 风险 |
| 3 | LLM API 速率限制雪崩 | 中 | 高 | Per-Provider TokenBucket + Fallback 链 | 风险 |
| 4 | Emergency 模式与运行中 dispatch 冲突 | 低 | 高 | P0 bypass / P1 等待→SIGKILL / PREEMPTED 状态 | 风险 |
| 5 | Artifact 互相覆盖 | 中 | 高 | per-dispatch 目录隔离 + PipelineArtifactManifest | 风险 |
| 6 | Windows Update 强制重启无 SIGTERM | 低 | 高 | save_state 原子写入 + atexit handler | 风险 |
| 7 | 双管线增加延迟（A+B 全链路） | 中 | 中 | M8/M9 并行 + Conditional Execution 跳过无变更模块 | 负面后果 |
| 8 | 多模型调用增加 Token 成本 | 中 | 中 | CostTracker per-call 追踪 + 80% 告警 | 负面后果 |
| 9 | 容量升级需分片和增量扫描等新组件施工投入 | 高 | 中 | 分 Phase 施工（A→B→C） | 负面后果 |
| 10 | 100 AI 并发场景下行为需压力测试验证 | 中 | 高 | Phase D 压力测试验收 | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取 GOV-AI-002 模型路由策略 | 打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 5 个 Phase（Phase A~D + Phase 0 蓝图补全） |
| 施工模式 | 扩展 |
| 核心风险 | 100 AI 并发下背压和公平调度未经验证 |
| 目标 generation | 2 — 本次施工将蓝图从 generation 1 升级到 generation 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-016 LifecycleAware/EventBus 契约 | hard | ✅ | ☐ |
| 2 | MOD-LLM_SECURITY LSG 安全闸门 | hard | ✅ | ☐ |
| 3 | GOV-AI-002 v2.0.0 模型路由策略 | hard | ✅ | ☐ |
| 4 | capacity_params.yaml 已创建 | soft | ✅ | ☐ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：核心瓶颈——并发参数调优

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5.2 容量估算 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py` |
| 验收标准 | max_concurrent=100, max_parallel=11, enable_parallel_modules=True |
| 验证命令 | `python -m pytest tests/test_pipeline_orchestrator.py -k test_concurrency -v` |
| G7 检查项 | capacity_params.yaml 参数与代码一致 |

#### 步骤 2：增量扫描调度器

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §17 容量升级 GAP-02 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pipeline\incremental_scan_orchestrator.py` |
| 验收标准 | git diff→ScriptImpactMap→15-30 脚本→<1min |
| 验证命令 | `python -m pytest tests/test_incremental_scan.py -v` |
| G7 检查项 | ScriptImpactMap 双向索引完整性 |

#### 步骤 3：水平分片扩展

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §17 容量升级 GAP-05 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pipeline\shard_router.py` |
| 验收标准 | ShardRouter 4→16 片 + 独立 SQLite per shard |
| 验证命令 | `python -m pytest tests/test_shard_router.py -v` |
| G7 检查项 | 一致性哈希迁移正确性 |

#### 步骤 4：背压与公平调度

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §17 容量升级 缺口 #1/#3 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pipeline\backpressure_manager.py` |
| 验收标准 | 三级背压 L1/L2/L3 + per-session 公平调度 |
| 验证命令 | `python -m pytest tests/test_backpressure.py -v` |
| G7 检查项 | 100 并发下无饥饿 |

#### 步骤 5：压力测试验收

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5.2 容量估算 |
| 产出位置 | `D:\ZephyrAlpha\tests\integration\test_pipeline_capacity.py` |
| 验收标准 | 100 AI 并发模拟→增量扫描 <1min / 全量 <3h |
| 验证命令 | `python -m pytest tests/integration/test_pipeline_capacity.py -v` |
| G7 检查项 | 所有容量指标达标 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 并发参数导致不稳定 | 恢复 capacity_params.yaml 原值 |
| 2 | 增量扫描结果不准确 | 回退到全量扫描模式 |
| 3 | 分片迁移数据丢失 | 从备份 SQLite 恢复 |
| 4 | 背压误拒绝 | 调整阈值参数 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | 并发参数调优 | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py` | ☐ | ☐ | ☐ |
| 2 | 增量扫描调度器 | `D:\ZephyrAlpha\src\zephyr\pipeline\incremental_scan_orchestrator.py` | ☐ | ☐ | ☐ |
| 3 | 水平分片 | `D:\ZephyrAlpha\src\zephyr\pipeline\shard_router.py` | ☐ | ☐ | ☐ |
| 4 | 背压管理 | `D:\ZephyrAlpha\src\zephyr\pipeline\backpressure_manager.py` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 模块数 | 51 | module_id_registry.yaml |
| 脚本数 | 268 | script-manifest.yaml |
| AI 并发 | 0 | AISessionPool |
| 并发 worker | 24 (BulkheadExecutor 四池) | 代码硬编码 |
| 全量扫描耗时 | ~3.5h | 实测 |
| 分片数 | 4 | ShardRouter 硬编码 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-01 | 设计容量从未声明 | capacity_params.yaml design_capacity 声明 | — |
| GAP-02 | 无增量扫描调度器 | IncrementalScanOrchestrator + ScriptImpactMap | 脚本 >500 |
| GAP-03 | 无模块-脚本关联元数据 | ModuleScriptMapping + ModuleScriptRegistry | 模块 >100 |
| GAP-04 | 并发参数散落 5 个文件 | capacity_params.yaml SSoT | — |
| GAP-05 | ShardRouter 硬编码 4 片 | 4→16 分片 + 独立 SQLite | 模块 >200 |
| GAP-06 | CapacityBudget 静态 64 | CapacityCalibrator 动态调整 | 模块 >100 |
| GAP-07 | 无 Pipeline 级背压 | BackpressureManager 三级响应 | AI 并发 >10 |
| GAP-08 | 无 per-session 公平调度 | Dispatch Fairness 三层隔离 | AI 并发 >20 |
| GAP-09 | 无 LLM API 速率协调 | Per-Provider TokenBucket | dispatch >50/min |
| GAP-10 | 无 Emergency 冲突解决 | PREEMPTED 状态 + 自动重入队 | SEV1 事件 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.37.0 | 1 | 基线 | M1-M11 双管线 + 路由 + 安全防线 + 韧性 | ✅ |
| v0.38.0 | 2 | 容量升级 | 背压/公平调度/增量扫描/分片/参数化 | ⚠️ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-01 | 设计容量从未声明 | P0 | v0.38.0 | 已完成 |
| GAP-02 | 无增量扫描调度器 | P0 | v0.38.0 | 待施工 |
| GAP-03 | 无模块-脚本关联 | P0 | v0.38.0 | 待施工 |
| GAP-04 | 并发参数散落 | P0 | v0.38.0 | 已完成 |
| GAP-05 | 分片数硬编码 | P1 | v0.38.0 | 待施工 |
| GAP-06 | 容量预算静态 | P1 | v0.38.0 | 待施工 |
| GAP-07 | 无背压机制 | P0 | v0.38.0 | 已完成 |
| GAP-08 | 无公平调度 | P1 | v0.38.0 | 待施工 |
| GAP-09 | 无 API 速率协调 | P1 | v0.38.0 | 待施工 |
| GAP-10 | 无 Emergency 冲突解决 | P0 | v0.38.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| BackpressureManager | GAP-07 | backpressure_manager.py | Phase A2 | 已存在 |
| CircuitBreakerManager | GAP-07 | circuit_breaker_manager.py | Phase A2 | 已存在 |
| CostTracker | GAP-04 | cost_tracker.py | Phase A | 已存在 |
| DeadLetterQueue | GAP-07 | dead_letter_queue.py | Phase A2 | 已存在 |
| ModelRouter | GAP-09 | model_router.py | Phase A2 | 已存在 |
| PreemptionManager | GAP-08 | preemption_manager.py | Phase A2 | 已存在 |
| IncrementalScanOrchestrator | GAP-02 | incremental_scan_orchestrator.py | Phase B | 待施工 |
| ModuleScriptRegistry | GAP-03 | module_script_registry.py | Phase B | 待施工 |
| ShardRouter 4→16 | GAP-05 | shard_router.py | Phase C | 待施工 |
| CapacityCalibrator | GAP-06 | capacity_calibrator.py | Phase C | 待施工 |

### 蓝图特有：M1-M11 双管线架构

> 来源：规格化内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：M1-M11 门控流水线是 Pipeline 独有的架构模式
> 不可砍理由：砍掉 = Pipeline 核心设计丢失

#### A 区：生产管线（M1-M5）

| 节点 | 职责 | 模型 | Sandbox | Gate |
|:---:|------|------|:---:|:---:|
| **M1** | 任务卡解析→结构化执行计划 | DeepSeek V4 Pro | full | full_g0_g7 |
| **M2** | 上下文装配→调用 context_engine | DeepSeek V4 Pro | standard | pre_commit_only |
| **M3** | 代码/文档生成——核心生产 | DeepSeek V4 Pro | full | full_g0_g7 |
| **M4** | 格式校验 | DeepSeek V4 Pro | standard | pre_commit_only |
| **M5** | 产物打包 | GLM-5.1 | standard | post_exec_only |

#### B 区：审计管线（M6-M11）

| 节点 | 职责 | 模型 | Sandbox | Gate |
|:---:|------|------|:---:|:---:|
| **M6** | 差异检测——产出 vs 期望（AP2边界标记） | DeepSeek V4 Pro | standard | pre_commit_only |
| **M7** | 深度审查——逐个文件逻辑/合规 | GLM-5.1 | audit | full_g0_g7 |
| **M8** | 标准合规——PS/GOV/KB 决策记录 | DeepSeek V4 Pro | standard | post_exec_only |
| **M9** | 风险评估——OWASP LLM Top 10 | DeepSeek V4 Pro | standard | post_exec_only |
| **M10** | 审计报告→Finding 格式 | DeepSeek V4 Pro | standard | post_exec_only |
| **M11** | 门禁裁决——G5/G6 | DeepSeek V4 Pro | restricted | none |

#### 三层模型策略

```
DeepSeek V4 Pro → 主力生产（M1-M4 + M6/M8/M9/M10/M11）
GLM-5.1        → 深度审查（M7 + M5）
Claude Opus 4.7 → 特种救援（DeepSeek失败3次 / GLM驳回2次 / security标签）
```

#### 模型降级 Fallback 链

```
DeepSeek 失败 → GLM → Claude
GLM 失败      → DeepSeek → Claude
Claude 失败   → 无降级（终点）
```

#### Affinity / Anti-Affinity 约束矩阵

| 约束类型 | 约束项 | 节点A | 节点B | 权重 | 说明 |
|:---:|------|:---:|:---:|:---:|------|
| mandatoryAntiAffinity | model | M3 | M7 | hard | 双盲审查必须用不同模型 |
| preferredAntiAffinity | model | M8 | M9 | soft | 建议合规+风险用不同模型 |
| mandatoryAffinity | sandbox | M1~M4 | — | hard | A 区必须在 full/standard sandbox |
| mandatoryAffinity | pipeline | A 区全部 | — | hard | A 区产出物必须经 M5→M6 |

#### Pipeline DAG 拓扑

```
A_DAG: M1 → M2 → M3 → M4 → M5（串行）

B_DAG: M6 → M7 → M8 ∥ M9 → M10 → M11
       （M8/M9 可并行，parallel_group=audit_mid）
```

#### 路由决策树

```yaml
routing_decision_tree:
  input: "TaskCard { task_type, priority, target_layer, estimated_complexity }"
  output: "PipelineNode { node_id, execution_model, sandbox_profile, gate_profile }"
  rules:
    - condition: "task_type == MODEL_BUILD AND estimated_complexity == HIGH"
      route: "M1 (DeepSeek V4 Pro + full sandbox + full_g0_g7)"
    - condition: "task_type == AUDIT AND priority == P0"
      route: "M3 (DeepSeek V4 Pro 复审 + audit sandbox + full_g0_g7)"
    - condition: "task_type ∈ {DOC_WRITE, REFACTOR} AND target_layer ∈ {D_DATA,基础设施,D_COMPLIANCE}"
      route: "M5 (GLM-5.1 + standard sandbox + post_exec_only)"
```

#### Scheduling Profiles

| Profile | 适用任务 | 路由策略 | 延迟要求 |
|------|------|------|:---:|
| `audit_strict` | P0 审计 | 全链 A+B，双盲审查，必须共识 | < 300s |
| `doc_fast` | 文档写作/重构 | 单管线 M6，跳过审计 | < 60s |
| `batch_low` | P3 批量任务 | Batch API 模式，攒批执行 | < 3600s |

#### Pipeline → Agent 桥接

| M 节点 | Agent 角色 | 域 |
|:---:|------|:---:|
| M1/M2 | ARCHITECT | D0 |
| M3 | IMPLEMENTER | D1 |
| M4/M6/M7/M10 | REVIEWER | D2 |
| M8/M9/M11 | GOVERNOR | D3 |
| M5 | OPERATOR | D5 |

#### Artifact 传递

```
M3.generate() → PipelineArtifact(key="M3_generated_code", type=code)
    → Manifest.artifacts.append(artifact)
    → M6.diff() → manifest.get("M3_generated_code") → 差异对比
```

#### Zone Crossing 防线

A 区(M1-M5)产出物不得直接流入 B 区(M6-M11)——必须经过 M6 边界标记。`_validate_zone_crossing()` 在模块切换时校验。

#### 双盲审查

M3(DeepSeek) + M7(GLM) → 共识比较 → 一致→PASS / 不一致→可升级 Claude 仲裁。

#### 背压三级响应

| 级别 | 队列深度 | 行为 |
|:---:|:---:|------|
| L1 正常 | <70% | 所有 dispatch 正常入队 |
| L2 警告 | 70%-90% | 返回 "X-Pipeline-Load: HIGH"，低优先级延后 |
| L3 拒绝 | >90% | HTTP 429，仅 P0_EMERGENCY bypass |

#### 执行模式策略

| 模式 | 触发条件 | 行为 |
|------|---------|------|
| 增量扫描（默认） | AI 改代码后自动触发 | git diff→ScriptImpactMap→15-30 脚本→<1min |
| 全量扫描（周检） | 每周日凌晨 2:00 或手动 | 跑全部 10K 脚本→2-3h |
| 部分扫描（回退） | 增量失败时自动降级 | 按模块分组→跑关联脚本池 |
| 紧急全量（兜底） | SEV1/Kill Switch | 跳过队列→全量扫描 |

---

## §18 决策记录

> 记录蓝图中的关键设计决策。
> 与变更记录不同——变更记录记"改了什么"，决策记录记"为什么这样设计"。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。
> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-PIPE-01 | M3/M7 必须用不同模型 | A:同模型/B:不同模型/C:可选 | B | 双盲审查独立性——同模型=单盲退化 | 2026-05-04 |
| 2 | D-PIPE-02 | Fallback 链顺序 | A:DeepSeek→Claude→GLM/B:DeepSeek→GLM→Claude | B | GLM 免费→先尝试低成本方案 | 2026-05-04 |
| 3 | D-PIPE-03 | 并发执行器选择 | A:ThreadPoolExecutor/B:ProcessPoolExecutor | B | subprocess I/O 释放 GIL | 2026-05-05 |
| 4 | D-PIPE-04 | 分片策略 | A:4片保持/B:16片扩展/C:32片 | B | 1500/16=94模块/片→SQLite 写锁可接受 | 2026-05-10 |
| 5 | D-PIPE-05 | 增量扫描为默认模式 | A:全量默认/B:增量默认 | B | 10K 脚本全量=不可行 | 2026-05-10 |
| 6 | D-PIPE-06 | 背压拒绝策略 | A:静默丢弃/B:返回429+C:无限排队 | B | 429 让调用方感知并退避 | 2026-05-10 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | AI 零记忆，不知道相对路径的基准在哪 | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 每次新 session 是零记忆 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程 | 决策过程是草稿的事 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | AI 不知道项目目录规范 | 路径幻觉 |
| 5 | **涉及文件范围必须明确列出** | AI 不知道边界在哪 | 范围漂移 |
| 6 | **容量估算必须写** | AI 不知道系统能容纳多少 | 容量瓶颈 |
| 7 | **迁移/废弃方案必须写** | AI 不知道旧东西怎么处理 | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | AI 无法处理模糊指令 | 执行漂移 |
| 9 | **蓝图必须自包含** | AI 可能不读引用的文件 | 信息缺失 |
| 10 | **删除文件必须遵守安全删除协议** | 没有git备份，删除不可逆 | 永久丢失 |
| 11 | **construction_progress 必须与代码实际状态一致** | 标completed但代码不存在=虚假进度 | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 路径不一致=AI找不到代码 | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 代码文件是 SSoT，蓝图复制代码=双源漂移 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容（架构/接口/约束/当前状态） | 蓝图是当前设计文档，不是历史记录 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责不同的内容强行塞一个蓝图=职责不清 | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀（如 CAP-G vs CAP）
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| Pipeline 蓝图中"ModelProfiler 子模块"（8 文件+独立 CLI） | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| Pipeline 蓝图中"容量升级 GAP-02~GAP-10" | **原地** | 容量升级是 Pipeline 核心能力，不是独立子系统 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 安全删除方案 |
|---|---------------|------------|---------|------------|
| 1 | route-manifest.yaml（重复） | `D:\ZephyrAlpha\src\zephyr\pipeline\route-manifest.yaml` | 废弃型 | 保留 routemanifest.yaml→交叉验证→标记 deprecated→物理删除 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持 1 个 Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type 词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | Orchestrator (MOD-INF-003) | `D:\ZephyrAlpha\src\zephyr\orchestrator\` | 任务调度 | Orchestrator 是上层调度→Pipeline 是下层管线执行，职责不同 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | Pipeline 源码 | `D:\ZephyrAlpha\src\zephyr\pipeline\` | 修改 | 容量升级参数调整 |
| 2 | Pipeline 测试 | `D:\ZephyrAlpha\tests\unit\test_pipeline_orchestrator.py` | 修改 | 新增并发/背压测试 |
| 3 | 容量参数 | `D:\ZephyrAlpha\config\capacity_params.yaml` | 修改 | 参数更新 |
| 4 | 路由配置 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | 读取 | 路由表引用 |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 任务管线——pipeline_orchestrator+models骨架完成

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/infrastructure/runtime_integration/pipeline/backpressure_manager.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/circuit_breaker_manager.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/cost_tracker.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/ct_pipe_routing.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/dead_letter_queue.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/layer_consumer_registry.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/layer_router.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/llm_gateway.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/benchmark_suite.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/capability_passport.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/cli.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/deepseek_v4_chat.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/exam_orchestrator.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/exam_test_cases.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/model_discovery.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/profiler.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/results_writer.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/task_model_learner.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/model_router.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/models.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_agent_bridge.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_lock.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_roadmap.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/preemption_manager.py` | ✅ 已实现 | |
| `src/zephyr/integration/route-manifest.yaml` | ✅ 已实现 | |
| `src/zephyr/integration/routemanifest.yaml` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/routing_plugins.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/test_pipeline_orchestrator.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| M1-M11 双管线架构设计 | **本文档 §17 蓝图特有** | b_pipeline.yaml（派生） |
| 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | — |
| 施工步骤 | **本文档 §16** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-003 Orchestrator | §4 接口契约、CT-PIPE-ORC-001 |
| Tier 2 | MOD-GATE_ENGINE Gate Engine | §4 PipelineResult |
| Tier 3 | `src/zephyr/integration/pipeline_orchestrator.py` | §4 数据模型、§11 产出物路径 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改 construction_progress | 下游更新依赖状态 | 更新集成测试 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调 | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |

---

## 蓝图特有章节

### 蓝图特有：Descheduler 任务重平衡

> 来源：规格化内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：Pipeline 独有的后台扫描策略
> 不可砍理由：砍掉 = STALE/MISROUTED 任务永久卡住

```yaml
descheduler:
  scan_interval_s: 300
  strategies:
    - name: "stale_task_eviction"
      trigger: "IN_PROGRESS > 30min"
      action: "mark STALE → FAILED → release_lock → re-enqueue"
    - name: "misrouted_rebalance"
      trigger: "estimated_complexity changed by FLE feedback"
      action: "re-evaluate routing → cancel + re-dispatch"
    - name: "claude_stuck_recovery"
      trigger: "CLAUDE_RESCUE > 60min"
      action: "downgrade to partial_result mode"
```

### 蓝图特有：Conditional Execution + Saga + Decision Log

> 来源：规格化内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：Pipeline 独有的执行控制模式
> 不可砍理由：砍掉 = Token 浪费 + 部分失败不可恢复

| 机制 | 触发条件 | 行为 |
|------|---------|------|
| Conditional Execution | M6.diff() → has_changes==false | 跳过 M7/M8/M9→直达 M11 |
| Dispatch Cancellation | 运行时中断信号 | cancel / modify_priority / switch_model |
| Saga Rollback | 部分模块失败 | 补偿回滚→delete artifacts + restore files |
| Decision Log | 每次路由决策 | audit-trail 持久化（含 policy_version + affinity_violations） |
| Policy Testing | 路由策略变更 | 断言路由 + affinity 约束 |
