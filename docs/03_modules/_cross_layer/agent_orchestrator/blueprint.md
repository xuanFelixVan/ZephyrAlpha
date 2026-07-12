---
module_id: MOD-INF-039
submodule_path: src/zephyr/trading/orchestrator
title: "Agent Orchestrator 蓝图 — Agent 全生命周期编排引擎"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
date: "2026-05-19"
valid_from: "2026-05-19"
ttl: permanent
construction_progress: completed
actual_disk_path: "src/zephyr/trading/orchestrator/"
belongs_to: "MOD-INF-035"
generation: 1
functional_domain: operations
summary: "Agent 全生命周期编排：任务队列、Agent调度、沙箱执行、幻觉检测、滚动升级、状态同步、故障恢复、会话管理。遥测跨层支撑层·Vibe Coding 2.0 五大核心服务之一。"
last_updated: "2026-05-19"
last_verified: "2026-05-19"
parent_module: "MOD-INF-035"
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
tags: [agent-orchestrator, task-queue, state-machine, sandbox, hallucination-detection, vibe-coding-infrastructure, lifecycle, session-management, rollback, resilience]
priority: P0
runtime_plane: hot
blueprint_level: module
responsibility_domain: 
  - {target: "MOD-FEEDBACK_LOOP", at: "§2", why: "Feedback Loop——质量数据上报"}
  - {target: "MOD-INF-021", at: "§2", why: "Rollback——操作失败触发回滚"}
references:
  - {id: "MOD-INF-009", at: "§2", why: "Pipeline——管线编排下游消费"}
  - {id: "MOD-INF-018", at: "§2", why: "Agent RBAC——操作权限校验"}
  - {id: "MOD-INF-022", at: "§2", why: "Escalation Protocol——异常升级路径"}
  - {id: "MOD-INF-024", at: "§2", why: "Budget Enforcer——Token/Cost 预算管控"}
  - {id: "MOD-INF-030", at: "§12", why: "Red-Blue Validator——CT-RB-GATE-001 / CT-RB-ESC-002 / CT-RB-KB-003 集成契约"}
  - {id: "AI-ENG-ORC-001", at: "§4", why: "Agent Orchestrator Interface——B轨接口规范"}
ssot_ref: "docs/03_modules/_cross_layer/_b_track_interfaces/agent_orchestrator_interface.md"
design_maturity: design
build_status: planned
---

# Agent Orchestrator 蓝图 — Agent 全生命周期编排引擎

## 概述

本蓝图描述 Agent Orchestrator——ZephyrAlpha Vibe Coding 2.0 五大核心服务中的"任务引擎"。它接管 Agent 任务全生命周期——任务入队、Agent 拉取、沙箱执行、幻觉检测、指标上报、收尾归档。当前规模 55 顶层模块 + 14 子包模块，覆盖 state/ resilience/ core/ 三个子域。上游依赖 AutoRuntime Core（大脑调度 WorkDAG），下游消费 Pipeline 执行结果。

> module_id: MOD-INF-039 | version: 1.0.0 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/orchestrator/ | generation: 1 | construction_progress: completed
> parent_module: MOD-INF-035（AutoRuntime Core）——从 MOD-INF-035 蓝图拆分独立
>
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-039`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | agent_orchestrator.py | §3.1 | Agent 生命周期编排主控 | 已实现 |
| 2 | task_queue.py | §3.1 | 任务队列（SQLite + asyncio.Queue） | 已实现 |
| 3 | trigger_router.py | §3.1 | 触发表路由规则 | 已实现 |
| 4 | wave_generator.py | §3.1 | 批次生成器 | 已实现 |
| 5 | phase_executor.py | §3.1 | Phase 执行器 | 已实现 |
| 6 | batch_orchestrator.py | §3.1 | 批量任务编排 | 已实现 |
| 7 | session_manager.py | §3.1 | 会话管理器 | 已实现 |
| 8 | session_handoff.py | §3.1 | 会话交接 | 已实现 |
| 9 | session_conflict.py | §3.1 | 会话冲突解决 | 已实现 |
| 10 | state_synchronizer.py | §3.1 | 状态同步器 | 已实现 |
| 11 | state_propagation.py | §3.1 | 状态传播 | 已实现 |
| 12 | file_task_mapper.py | §3.1 | 文件-任务映射 | 已实现 |
| 13 | agent_health_monitor.py | §3.1 | Agent 健康监控 | 已实现 |
| 14 | agent_quality.py | §3.1 | Agent 质量评估 | 已实现 |
| 15 | hallucination_detector.py | §3.1 | 幻觉检测器 | 已实现 |
| 16 | failure_matcher.py | §3.1 | 故障模式匹配 | 已实现 |
| 17 | rollback_manager.py | §3.1 | 回滚管理器 | 已实现 |
| 18 | rolling_upgrade.py | §3.1 | 滚动升级 | 已实现 |
| 19 | canary_manager.py | §3.1 | 金丝雀发布管理 | 已实现 |
| 20 | stability_guard.py | §3.1 | 稳定性守卫 | 已实现 |
| 21 | autonomy_guard.py | §3.1 | 自治边界守卫 | 已实现 |
| 22 | bulkhead_manager.py | §3.1 | 隔舱管理器 | 已实现 |
| 23 | degrade_cascade.py | §3.1 | 降级级联 | 已实现 |
| 24 | disk_guard.py | §3.1 | 磁盘守卫 | 已实现 |
| 25 | dlq_manager.py | §3.1 | 死信队列管理器 | 已实现 |
| 26 | deferred_queue.py | §3.1 | 延迟队列 | 已实现 |
| 27 | capacity_budget.py | §3.1 | 容量预算 | 已实现 |
| 28 | config_manager.py | §3.1 | 配置管理器 | 已删除（ARCH-038 P1 空壳退役） |
| 29 | contract_registry.py | §3.1 | 契约注册表 | 已实现 |
| 30 | contract_router.py | §3.1 | 契约路由器 | 已实现 |
| 31 | backup_manager.py | §3.1 | 备份管理器 | 已实现 |
| 32 | data_lifecycle.py | §3.1 | 数据生命周期管理 | 已实现 |
| 33 | housekeeping.py | §3.1 | 日常清理 | 已实现 |
| 34 | startup_sequencer.py | §3.1 | 启动序列器 | 已实现 |
| 35 | teardown_manager.py | §3.1 | 拆卸管理器 | 已实现 |
| 36 | schema_migration.py | §3.1 | Schema 迁移 | 已实现 |
| 37 | version_manifest.py | §3.1 | 版本清单 | 已实现 |
| 38 | model_registry.py | §3.1 | 模型注册表 | 已实现 |
| 39 | dependency_lock.py | §3.1 | 依赖锁 | 已实现 |
| 40 | network_partition.py | §3.1 | 网络分区处理 | 已实现 |
| 41 | system_transfer.py | §3.1 | 系统状态转移 | 已实现 |
| 42 | chaos_engine.py | §3.1 | 混沌工程引擎 | 已实现 |
| 43 | benchmark_runner.py | §3.1 | 基准测试运行器 | 已实现 |
| 44 | blueprint_scorer.py | §3.1 | 蓝图评分 | 已实现 |
| 45 | blueprint_health.py | §3.1 | 蓝图健康检查 | 已实现 |
| 46 | blind_spot_closure.py | §3.1 | 盲点闭合 | 已实现 |
| 47 | construction_guide.py | §3.1 | 施工指导 | 已实现 |
| 48 | design_decisions.py | §3.1 | 设计决策记录 | 已实现 |
| 49 | feature_flag.py | §3.1 | 特性开关 | 已实现 |
| 50 | finding_bridge.py | §3.1 | 发现桥接 | 已实现 |
| 51 | incident_postmortem.py | §3.1 | 事故复盘 | 已实现 |
| 52 | ke_quality.py | §3.1 | 知识条目质量 | 已实现 |
| 53 | knowledge_freshness.py | §3.1 | 知识新鲜度 | 已实现 |
| 54 | lean_scanner.py | §3.1 | 精益扫描器 | 已实现 |
| 55 | path_index.py | §3.1 | 路径索引 | 已实现 |
| 56 | prompt_version.py | §3.1 | Prompt 版本管理 | 已实现 |
| 57 | reconciliation_loop.py | §3.1 | 对账循环 | 已实现 |
| 58 | risk_registry.py | §3.1 | 风险注册表 | 已实现 |
| 59 | core/agent_orchestrator.py | §3.1 (core) | 核心编排器 | 已实现 |
| 60 | core/task_queue.py | §3.1 (core) | 核心任务队列 | 已实现 |
| 61 | core/trigger_router.py | §3.1 (core) | 核心触发表路由 | 已实现 |
| 62 | core/wave_generator.py | §3.1 (core) | 核心批次生成 | 已实现 |
| 63 | resilience/deferred_queue.py | §3.1 (resilience) | 弹性延迟队列 | 已实现 |
| 64 | resilience/failure_matcher.py | §3.1 (resilience) | 弹性故障匹配 | 已实现 |
| 65 | resilience/hallucination_detector.py | §3.1 (resilience) | 弹性幻觉检测 | 已实现 |
| 66 | resilience/rollback_manager.py | §3.1 (resilience) | 弹性回滚管理 | 已实现 |
| 67 | state/agent_health_monitor.py | §3.1 (state) | 状态-健康监控 | 已实现 |
| 68 | state/file_task_mapper.py | §3.1 (state) | 状态-文件任务映射 | 已实现 |
| 69 | state/session_manager.py | §3.1 (state) | 状态-会话管理 | 已实现 |
| 70 | state/state_synchronizer.py | §3.1 (state) | 状态-同步 | 已实现 |
| 71 | __init__.py | — | 包初始化 | 已实现 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/orchestrator/` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" src/zephyr/orchestrator/*.py` | ☐ |
| actual_disk_path 与 §11 产出物路径一致 | 对比 frontmatter 与 §11 | ☐ |

---

## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha 需要一个 Agent 全生命周期编排引擎来管理 AI Agent 的任务队列、调度、沙箱执行和质量评估。原属于 MOD-INF-035 AutoRuntime Core 蓝图管辖，但 `orchestrator/` 包（55+ 顶层文件 + 3 子包）具有独立的职责域——Agent 任务生命周期管理，与大脑的 MAPE-K 调和循环职责完全不同。根据蓝图拆分判定标准（铁律#15），已触发拆分条件。

### §1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | Agent 任务全生命周期管理 | 状态机 10 状态覆盖 DRAFT→COMPLETED 全部路径 |
| 2 | 任务队列公平调度 | 无饥饿任务、P2 最大等待合规 |
| 3 | 沙箱安全执行 | 沙箱创建失败→拒绝无沙箱运行 |
| 4 | 幻觉检测与纠正 | HALLUCINATING 状态分支触发→自动回滚 |
| 5 | 滚动升级与金丝雀发布 | 零停机升级 |

### §1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | MAPE-K 调和循环 | MOD-INF-035 AutoRuntime Core 负责 |
| 2 | 节律调度与 DreamCycle | MOD-INF-035 AutoRuntime Core 负责 |
| 3 | 能力注册 CapabilityRegistry | MOD-INF-035 AutoRuntime Core 负责 |
| 4 | 模块自动接入与孤儿检测 | MOD-INF-035 AutoRuntime Core 负责 |
| 5 | Pipeline 管线执行 | MOD-INF-009 Pipeline 负责 |

---

## §2 模块边界

### §2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | Agent 任务生命周期 | DRAFT→QUEUED→ASSIGNED→RUNNING→REVIEWING→COMPLETED 状态机 |
| 2 | 任务队列管理 | SQLite + asyncio.Queue 双队列架构 |
| 3 | Agent 调度 | Agent 拉取任务 / 公平调度 / WIP 限制 |
| 4 | 沙箱执行 | Windows ACL + 只读挂载 / 拒绝无沙箱运行 |
| 5 | 幻觉检测 | 输出质量检测 / HALLUCINATING 状态分支 |
| 6 | 会话管理 | Session 创建/交接/冲突解决/状态持久化 |
| 7 | 状态同步 | 跨组件状态传播与同步 |
| 8 | 版本升级 | 滚动升级 / 金丝雀发布 / Schema 迁移 |
| 9 | 故障恢复 | 回滚管理 / 死信队列 / 降级级联 / 隔舱 |
| 10 | 质量评估 | Agent 质量评分 / 蓝图健康检查 / 知识新鲜度 |
| 11 | 日常运维 | 备份管理 / 数据生命周期 / 配置管理 |

### §2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | MAPE-K 调和循环 | MOD-INF-035 AutoRuntime Core |
| 2 | 节律调度 | MOD-INF-035 CircadianScheduler |
| 3 | 能力注册 | MOD-INF-035 CapabilityRegistry |
| 4 | 管线执行 | MOD-INF-009 Pipeline |
| 5 | 门禁规则执行 | MOD-GATE_ENGINE Gate Engine |
| 6 | 审计日志持久化 | MOD-INF-020 Audit Trail |
| 7 | LLM 安全网关 | MOD-LLM_SECURITY LLM Security |

---

## §3 架构设计

### §3.1 组件架构

**三子域架构**：core 核心调度层 → resilience 弹性层 → state 状态层

| # | 组件 | 子域 | 职责 | 依赖 | 交互方式 |
|---|------|:---:|------|------|---------|
| 1 | AgentOrchestrator | core | 主控——Agent 生命周期编排 | TaskQueue, TriggerRouter | 同步调用 |
| 2 | TaskQueue | core | 任务队列 SQLite + asyncio.Queue | — | 队列 |
| 3 | TriggerRouter | core | 触发条件→任务路由 | — | 同步调用 |
| 4 | WaveGenerator | core | 批次任务生成 | TaskQueue | 同步调用 |
| 5 | PhaseExecutor | — | Phase 执行引擎 | AgentOrchestrator | 同步调用 |
| 6 | BatchOrchestrator | — | 批量任务编排 | TaskQueue, PhaseExecutor | 同步调用 |
| 7 | SessionManager | state | 会话生命周期 | — | 同步调用 |
| 8 | SessionHandoff | state | 会话交接 | SessionManager | 同步调用 |
| 9 | SessionConflict | state | 冲突解决 | SessionManager | 同步调用 |
| 10 | StateSynchronizer | state | 跨组件状态同步 | SessionManager | 事件 |
| 11 | StatePropagation | state | 状态传播 | StateSynchronizer | 事件 |
| 12 | FileTaskMapper | state | 文件↔任务映射 | — | 同步调用 |
| 13 | AgentHealthMonitor | state | Agent 健康监控 | — | 事件 |
| 14 | AgentQuality | — | Agent 质量评估 | AgentHealthMonitor | 同步调用 |
| 15 | HallucinationDetector | resilience | 输出幻觉检测 | FailureMatcher | 同步调用 |
| 16 | FailureMatcher | resilience | 故障模式匹配 | RollbackManager | 同步调用 |
| 17 | RollbackManager | resilience | 回滚执行 | — | 同步调用 |
| 18 | RollingUpgrade | — | 滚动升级 | CanaryManager, StabilityGuard | 同步调用 |
| 19 | CanaryManager | — | 金丝雀发布 | StabilityGuard | 同步调用 |
| 20 | StabilityGuard | — | 稳定性守卫 | AutonomyGuard | 同步调用 |
| 21 | AutonomyGuard | — | 自治边界守卫 | — | 同步调用 |
| 22 | BulkheadManager | — | 隔舱隔离 | — | 同步调用 |
| 23 | DegradeCascade | — | 降级级联链 | BulkheadManager | 同步调用 |
| 24 | DiskGuard | — | 磁盘空间守卫 | — | 事件 |
| 25 | DLQManager | — | 死信队列管理 | TaskQueue | 同步调用 |
| 26 | DeferredQueue | — | 延迟队列 | TaskQueue | 队列 |
| 27 | CapacityBudget | — | 容量预算管控 | — | 同步调用 |
| 28 | ConfigManager | — | 配置中心 | — | 同步调用 |
| 29 | ContractRegistry | — | 契约注册表 | ContractRouter | 同步调用 |
| 30 | ContractRouter | — | 契约路由 | ContractRegistry | 同步调用 |
| 31 | BackupManager | — | 备份管理 | DataLifecycle | 同步调用 |
| 32 | DataLifecycle | — | 数据生命周期 | Housekeeping | 同步调用 |
| 33 | Housekeeping | — | 日常清理 | — | 定时 |
| 34 | StartupSequencer | — | 启动序列 | TeardownManager | 同步调用 |
| 35 | TeardownManager | — | 拆卸序列 | — | 同步调用 |
| 36 | SchemaMigration | — | Schema 迁移 | VersionManifest | 同步调用 |
| 37 | VersionManifest | — | 版本清单 | — | 同步调用 |
| 38 | ModelRegistry | — | 模型注册 | — | 同步调用 |
| 39 | DependencyLock | — | 依赖锁管理 | — | 同步调用 |
| 40 | NetworkPartition | — | 网络分区处理 | — | 事件 |
| 41 | SystemTransfer | — | 系统状态转移 | — | 同步调用 |
| 42 | ChaosEngine | — | 混沌工程 | — | 同步调用 |
| 43 | BenchmarkRunner | — | 基准测试 | — | 同步调用 |
| 44 | BlueprintScorer | — | 蓝图评分 | BlueprintHealth | 同步调用 |
| 45 | BlueprintHealth | — | 蓝图健康 | — | 同步调用 |
| 46 | BlindSpotClosure | — | 盲点闭合 | FindingBridge | 同步调用 |
| 47 | ConstructionGuide | — | 施工指导 | — | 同步调用 |
| 48 | DesignDecisions | — | 设计决策 | — | 同步调用 |
| 49 | FeatureFlag | — | 特性开关 | — | 同步调用 |
| 50 | FindingBridge | — | 发现桥接 | — | 同步调用 |
| 51 | IncidentPostmortem | — | 事故复盘 | — | 同步调用 |
| 52 | KEQuality | — | KE 质量评估 | — | 同步调用 |
| 53 | KnowledgeFreshness | — | 知识新鲜度 | — | 同步调用 |
| 54 | LeanScanner | — | 精益扫描 | — | 同步调用 |
| 55 | PathIndex | — | 路径索引 | — | 同步调用 |
| 56 | PromptVersion | — | Prompt 版本 | — | 同步调用 |
| 57 | ReconciliationLoop | — | 对账循环 | — | 定时 |
| 58 | RiskRegistry | — | 风险注册 | — | 同步调用 |

**状态机**：
```
DRAFT → QUEUED → ASSIGNED → RUNNING → REVIEWING → COMPLETED
  ↓        ↓         ↓          ↓           ↓
CANCELLED BLOCKED   —     HALLUCINATING  FAILED
```

### §3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | AutoRuntime Core WorkDAG | TaskQueue 入队→Agent 拉取 | Pipeline 执行 | WorkDAG |
| 2 | Agent 执行输出 | HallucinationDetector 检测 | RollbackManager | QualityReport |
| 3 | Session 事件 | SessionManager 生命周期 | StateSynchronizer | SessionState |
| 4 | 版本变更 | RollingUpgrade→CanaryManager | StabilityGuard | VersionManifest |

---

## §4 接口契约

### §4.1 公共 API

```python
class AgentOrchestrator:
    """Agent 生命周期编排主控"""

    def submit_task(self, dag: "WorkDAG", priority: int = 1) -> str:
        """提交任务到队列。输入：WorkDAG + 优先级。输出：task_id。"""

    def assign_task(self, agent_id: str) -> "Task | None":
        """Agent 拉取任务。输入：agent_id。输出：Task 或 None。"""

    def complete_task(self, task_id: str, output: dict) -> None:
        """标记任务完成。输入：task_id + 输出。输出：无。"""

    def fail_task(self, task_id: str, reason: str) -> None:
        """标记任务失败。输入：task_id + 失败原因。输出：无。"""

class HallucinationDetector:
    """幻觉检测器"""

    def detect(self, task_output: dict) -> "DetectionResult":
        """检测输出中的幻觉。输入：任务输出。输出：DetectionResult。"""

class RollbackManager:
    """回滚管理器"""

    def rollback(self, task_id: str, to_state: str) -> bool:
        """回滚任务到指定状态。输入：task_id + 目标状态。输出：成功/失败。"""
```

### §4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum

class TaskState(str, Enum):
    DRAFT = "DRAFT"
    QUEUED = "QUEUED"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    REVIEWING = "REVIEWING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    HALLUCINATING = "HALLUCINATING"

class Task(BaseModel):
    task_id: str
    state: TaskState = TaskState.DRAFT
    agent_id: str | None = None
    session_id: str | None = None
    priority: int = 1

class DetectionResult(BaseModel):
    is_hallucination: bool
    confidence: float
    reason: str | None = None
```

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 原因 |
|---|------|------|
| 1 | Python 3.12+ / Pydantic V2 | 项目统一技术栈 |
| 2 | 任务队列：SQLite + asyncio.Queue（双队列） | 持久化 + 低延迟 |
| 3 | 沙箱：Windows ACL + 只读挂载 | 无 Docker 环境 |
| 4 | P0 降级红线：沙箱创建失败→拒绝无沙箱运行 | 安全优于可用性 |
| 5 | 文件写入 MUST 原子操作（temp-file + os.replace） | NTFS 锁竞争 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 任务队列满 | WIP > max_active | 拒绝非P0任务入队 | 新任务排队 |
| 2 | 幻觉检测触发 | HallucinationDetector | 任务→HALLUCINATING→回滚 | 单任务 |
| 3 | 沙箱创建失败 | Sandbox 初始化异常 | 拒绝运行→任务 FAIL | 单任务 |
| 4 | Session 冲突 | SessionConflict 检测 | 冲突解决→通知 | 单 Session |
| 5 | 滚动升级失败 | CanaryManager 检测 | 自动回滚→上一版本 | 全局 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | Agent 越权操作 | 高 | Agent RBAC (MOD-INF-018) | RBAC 单元测试 |
| 2 | 沙箱逃逸 | 高 | Windows ACL + 只读挂载 | 沙箱安全测试 |
| 3 | 任务输出注入 | 中 | LLM Security Gateway 校验 | 注入测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 55 子组件核心方法 | 状态机 / 队列 / 幻觉检测 / 回滚 | 覆盖率 >80% |
| 2 | 集成测试 | Orchestrator↔Pipeline / Orchestrator↔Gate | 端到端任务提交→执行→审计 | 端到端通过 |

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-035 (AutoRuntime) | 必须 | WorkDAG 调度入口 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-INF-016 (Shared) | 必须 | 事件总线/生命周期/日志 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` |
| MOD-CONTEXT_ENGINE (Context) | 必须 | 上下文注入 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\context_engine\blueprint.md` |
| MOD-LLM_SECURITY (LLM Security) | 必须 | 入参/出参校验 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\llm_security\blueprint.md` |
| MOD-INF-011 (VMS) | 必须 | task_history 写入 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\vector_memory\blueprint.md` |
| MOD-GATE_ENGINE (Gate) | 必须 | TaskGate 门禁 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-INF-020 (Audit) | 必须 | 审计日志 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-FEEDBACK_LOOP (FLE) | 必须 | 质量数据上报 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback_loop\blueprint.md` |
| MOD-INF-021 (Rollback) | 必须 | 回滚触发 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\rollback-system\blueprint.md` |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\agent-orchestrator\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\orchestrator\` | 55+14 子组件 Python 源码 |
| 核心子包 | `D:\ZephyrAlpha\src\zephyr\orchestrator\core\` | 核心调度层 |
| 弹性子包 | `D:\ZephyrAlpha\src\zephyr\orchestrator\resilience\` | 弹性容错层 |
| 状态子包 | `D:\ZephyrAlpha\src\zephyr\orchestrator\state\` | 状态管理层 |
| 测试代码 | `D:\ZephyrAlpha\tests\orchestrator\` | 测试用例 |
| B轨接口 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\_b_track_interfaces\agent_orchestrator_interface.md` | 接口规范 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| AutoRuntime Core (MOD-INF-035) | 输入接口 | WorkDAG 提交→Orchestrator.submit_task() | 端到端任务执行 |
| Pipeline (MOD-INF-009) | 输出接口 | Orchestrator→Pipeline 任务执行 | 管线调度 |
| Gate Engine (MOD-GATE_ENGINE) | 门禁调用 | TaskGate 门禁验证 | 门禁通过率 |
| Context Engine (MOD-CONTEXT_ENGINE) | 上游调用 | 任务开始前拉上下文 | 上下文注入验证 |
| LLM Security (MOD-LLM_SECURITY) | 上游调用 | 入参/出参 Schema 校验 | 安全测试 |
| Vector Memory (MOD-INF-011) | 写入接口 | 任务完成写 task_history | 数据完整性 |
| Rollback (MOD-INF-021) | 联动调用 | 失败触发回滚 | 回滚成功 |

---

## §14 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解策略 | 类型 |
|---|------|------|------|---------|------|
| 1 | 任务队列满导致饥饿 | 中 | 高 | WIP 池 + 公平调度 | 风险 |
| 2 | 幻觉检测误判 | 低 | 中 | 多模型交叉验证 | 风险 |
| 3 | 滚动升级中途崩溃 | 低 | 高 | CanaryManager 自动回滚 | 风险 |
| | N1 | 沙箱失败→拒绝运行导致任务 FAIL | 中 | 中 | 安全优于可用性（P0 降级红线） | 负面后果 |

---

## §16 施工指引

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工模式 | 维护（基线已完成，按需扩展） |
| 核心风险 | 任务队列扩展 / 幻觉检测精度 |
| 目标 generation | 1 — 基线版 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | agent_orchestrator.py | `D:\ZephyrAlpha\src\zephyr\orchestrator\agent_orchestrator.py` | ☐ | ☐ | ☐ |
| 2 | task_queue.py | `D:\ZephyrAlpha\src\zephyr\orchestrator\task_queue.py` | ☐ | ☐ | ☐ |
| 3 | hallucination_detector.py | `D:\ZephyrAlpha\src\zephyr\orchestrator\hallucination_detector.py` | ☐ | ☐ | ☐ |
| 4 | rollback_manager.py | `D:\ZephyrAlpha\src\zephyr\orchestrator\rollback_manager.py` | ☐ | ☐ | ☐ |
| 5 | 测试套件 | `D:\ZephyrAlpha\tests\orchestrator\` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | agent |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-ORC-001 | 从 MOD-INF-035 拆分独立蓝图 | A:保留 B:拆分 | B | orchestrator 有独立职责域，满足拆分判定全部4条件 | 2026-05-19 |
| 2 | D-ORC-002 | 任务队列双架构 | A:SQLite B:asyncio C:A+B | C | 持久化+低延迟 | 遗留 |

---

## 必备链接

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | B轨接口规范 | AI-ENG-ORC-001 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\_b_track_interfaces\agent_orchestrator_interface.md` | 接口定义 |
| 4 | AutoRuntime Core | MOD-INF-035 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` | 父模块蓝图 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | AutoRuntime WorkOrchestrator | `D:\ZephyrAlpha\src\zephyr\runtime\work_orchestrator.py` | DAG 调度 | WorkOrchestrator 管全局 DAG 编排，Orchestrator 管 Agent 粒度任务执行——层级不同 |
| 2 | Pipeline TaskLifecycleManager | `D:\ZephyrAlpha\src\zephyr\pipeline\` | 任务状态 | Pipeline 管管线执行状态，Orchestrator 管 Agent 工作状态——责任域不同 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | orchestrator 包 | `D:\ZephyrAlpha\src\zephyr\orchestrator\` | 本模块代码 | 不变（[BLUEPRINT] 头部更新） |
| 2 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\agent-orchestrator\blueprint.md` | 本文件 | 新建 |
| 3 | AutoRuntime Core 蓝图 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` | 父模块 | 修改（拆分后更新） |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| Agent Orchestrator 架构设计 | **本文档 §1-§10** | MOD-INF-035 蓝图（已拆分） |
| Agent Orchestrator 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| B轨接口规范 | [agent_orchestrator_interface.md](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/_b_track_interfaces/agent_orchestrator_interface.md) | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-19 | 1.0.0 | 从 MOD-INF-035 拆分独立蓝图——Agent Orchestrator 全生命周期编排引擎首次独立登记 |
