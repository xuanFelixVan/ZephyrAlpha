﻿﻿﻿﻿﻿﻿﻿﻿---
module_id: "MOD-INF-035"
title: "AutoRuntime Core 蓝图 — 系统大脑·三层运行时运营中心"
doc_type: blueprint
template_for: blueprint
status: Active
version: "6.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-10"
valid_from: "2026-05-10"
ttl: permanent
construction_progress: completed
actual_disk_path: "src/zephyr/runtime/"
belongs_to: "SYS-MASTER-001"
generation: 2
functional_domain: operations
summary: "系统大脑：三层运行时编排+MAPE-K调和循环+节律调度+健康监控+工作编排+自动接入"
last_updated: "2026-05-14"
last_verified: "2026-05-13"
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: "ZephyrAlpha 系统大脑——三层运行时编排、节律调度、健康监控、审计日志、工作编排、自动接入。五层同心圆架构，24子组件，85+文件。终极目标：孤儿率→0%。"
tags: [auto-runtime, brain, core, orchestrator, mape-k, circadian, dream-cycle, health-monitor, work-orchestrator, auto-integrator, orphan-detector, capability-registry, cross-layer, system-brain]
priority: P0
blueprint_level: module
responsibility_domain: "auto_runtime_core"
depends_on:
  - {target: "SYS-MASTER-001", at: "全篇", why: "系统总蓝图——大脑是三级金字塔 Level 1 节点"}
  - {target: "MOD-INF-002", at: "全篇", why: "Runtime Integration——RI EventStore/DryRun/CostTracker 运行时桥接"}
  - {target: "MOD-INF-016", at: "全篇", why: "Shared Core——事件总线/生命周期/日志/沙箱等公共基座"}
  - {target: "MOD-INF-009", at: "全篇", why: "Pipeline——大脑调度管线任务"}
  - {target: "MOD-INF-034", at: "全篇", why: "Model Profiler——大脑消费 benchmark 结果做模型路由"}
  - {target: "MOD-INF-007", at: "§2", why: "Gate Engine——大脑执行结果需过门禁验证"}
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——大脑操作写入审计日志"}
  - {target: "MOD-INF-010", at: "§2", why: "Feedback Loop——大脑异常上报反馈闭环"}
references:
  - {id: "MOD-INF-019", at: "§2", why: "Agent Spec——大脑通过 Skill 注册发现新能力"}
  - {id: "MOD-INF-013", at: "§2", why: "MCP Servers——大脑能力通过 MCP 暴露"}
  - {id: "MOD-INF-023", at: "§2", why: "Drift Detector——大脑配置漂移检测联动"}
  - {id: "MOD-INF-021", at: "§2", why: "Rollback——大脑操作失败触发回滚"}
  - {id: "MOD-INF-024", at: "§2", why: "Budget Enforcer——大脑 Token/Cost 预算管控"}
  - {id: "MOD-INF-018", at: "§2", why: "Agent RBAC——大脑操作权限校验"}
  - {id: "MOD-KB-001", at: "§4", why: "Knowledge Base——大脑 Dream Cycle 知识固化目标"}
  - {id: "MOD-INF-011", at: "§2", why: "Vector Memory——大脑检索向量知识"}
  - {id: "MOD-INF-008", at: "§2", why: "Context Engine——大脑消费上下文注入"}
  - {id: "MOD-INF-014", at: "§2", why: "LLM Security——大脑 LLM 调用的安全闸门"}
  - {id: "MOD-INF-022", at: "§2", why: "Escalation Protocol——大脑异常升级路径"}
ssot_ref: "specs/auto-runtime-core/spec.md"
---

# AutoRuntime Core 蓝图 — 系统大脑·三层运行时运营中心

## 概述

本蓝图描述 AutoRuntime Core——ZephyrAlpha 的系统大脑。它解决了 1500 模块/10000 脚本/100 AI 并发下的全局运行时编排问题。核心职责包括：三层运行时编排、MAPE-K 调和循环、节律调度、健康监控、工作编排、自动接入。当前规模 51 模块/268 脚本/0 AI 并发，目标容量 1500 模块/10000 脚本/100 AI 并发。上游依赖 Pipeline/Gate Engine/Audit Trail，下游被所有模块消费。

> module_id: MOD-INF-035 | version: 6.0.0 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/runtime/ | generation: 2 | construction_progress: completed
>
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[compression-workflow-standard.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/document/compression-workflow-standard.md)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[system-dependency-map.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/system-dependency-map.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | auto_runtime_core.py | §3.1 | MAPE-K 调和循环主控 | 已实现 |
| 2 | auto_task_generator.py | §3.1 | 自动扫描项目文件生成推理任务 | 已实现 |
| 3 | auto_integrator.py | §3.1 | 自动接入新模块 | 已实现 |
| 4 | module_onboarding_scanner.py | §3.1 | 模块接入扫描器 | 已实现 |
| 5 | orphan_detector.py | §3.1 | 孤儿检测器 | 已实现 |
| 6 | work_orchestrator.py | §3.1 | DAG 驱动任务调度 | 已实现 |
| 7 | work_dag.py | §3.1 | DAG 数据模型 | 已实现 |
| 8 | circadian_scheduler.py | §3.1 | 日间/夜间/周末节律调度 | 已实现 |
| 9 | dream_cycle.py | §3.1 | 夜间知识固化 | 已实现 |
| 10 | health_monitor.py | §3.1 | 健康监控+自愈 | 已实现 |
| 11 | feedback_loop.py | §3.1 | 反馈闭环 | 已实现 |
| 12 | capability_registry.py | §3.1 | 能力注册中心 | 已实现 |
| 13 | capability_card.py | §3.1 | 能力卡片数据模型 | 已实现 |
| 14 | status_dashboard.py | §3.1 | 实时状态面板 | 已实现 |
| 15 | night_shift_queue.py | §3.1 | 夜班登记表 | 已实现 |
| 16 | ai_audit_logger.py | §3.1 | AI 行为审计日志 | 已实现 |
| 17 | integration_registry.py | §3.1 | 集成注册表 | 已实现 |
| 18 | runtime_config.py | §3.1 | 配置模型 | 已实现 |
| 19 | stop_gate.py | §3.1 | 质量闸门 | 已实现 |
| 20 | finalizer.py | §3.1 | 优雅清理 | 已实现 |
| 21 | lifecycle_manager.py | §3.1 | 启动/停止/健康检查序列 | 已实现 |
| 22 | action_dispatcher.py | §3.1 | 动作分派器 | 已实现 |
| 23 | task_gate.py | §3.1 | 任务门禁 | 已实现 |
| 24 | windows_service.py | §3.1 | Windows Service 包装器 | 已实现 |
| 25 | __init__.py | — | 包初始化 | 已实现 |
| 26 | __main__.py | — | 入口点 | 已实现 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/runtime/` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" src/zephyr/runtime/*.py` | ☐ |
| actual_disk_path 与 §11 产出物路径一致 | 对比 frontmatter 与 §11 | ☐ |
| §17 容量升级组件代码覆盖 | 按升级组件清单核对 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v5.0.0 (基线) | 24/24 子组件已落盘 | — | — |
| v6.0.0 (容量升级) | 基线组件全部存在 | BrainAdmissionController / GPU调度 / 语义路由 | 待施工——§17 T0-T3 渐进落地 |

---

---

## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha 需要一个系统大脑统一编排所有模块的运行时行为。当前规模 ~51 模块 / ~268 脚本 / 0 AI 并发，目标规模 1,500 模块 / 10,000 脚本 / 100 AI 并发。大脑从"巡几十个模块"变为"巡 1,500 个模块"，需要容量升级设计。

### §1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 接入项目所有模块，孤儿率 → 0% | 孤儿率 = 未接入模块数 / 总模块数 |
| 2 | 三层运行时编排（L1 Trae / L2 Local / L3 API） | 三层 AI 任务正确路由率 100% |
| 3 | MAPE-K 调和循环稳态延迟 <500ms（1,500 模块） | P50 loop latency |
| 4 | 100 AI 并发下调度公平性 | 无饥饿任务（P2 最大等待 <N 秒） |
| 5 | 增量扫描 <1 分钟（15-30 脚本），全量周检 <75 分钟 | 扫描耗时 |

### §1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 脚本执行引擎 | Pipeline (MOD-INF-009) 负责 |
| 2 | 多进程 Worker Pool | SYS-MASTER §〇 #1 负责 |
| 3 | 硬件感知调度 | SYS-MASTER §〇 #5 负责 |
| 4 | 拥塞控制/背压算法 | SYS-MASTER §〇 #6 负责 |
| 5 | SQLite 批量缓冲 | SYS-MASTER §〇 #10 (ADR-0038) 负责 |
| 6 | 跨进程锁协议 | SYS-MASTER §〇 #11 (ADR-0037) 负责 |
| 7 | SLI/SLO/Kill Switch 定义 | Capacity Assurance (MOD-INF-001) 负责 |

### §1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 单机部署：i7-12700KF 12C20T / 64GB / RTX 3090 24GB | 大脑进程预留 8GB RAM / 4GB VRAM，不可超限 |
| Windows Service 运行 | L0 自举层需 Windows Service 包装器 |
| Python GIL 限制 | I/O 密集型用 ThreadPoolExecutor，CPU 密集型需多进程 |
| GPU 白天 Worker Pool / 夜间 DreamCycle 共享 | MUST GPU 时间分片+VRAM 硬分区 |
| 无 git 备份 | 删除操作不可逆——MUST 遵守安全删除协议 |

---

## §2 模块边界

### §2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 三层运行时编排 | L1 Trae(IDE) / L2 Local(Ollama) / L3 API(DeepSeek/Claude) 任务路由 |
| 2 | MAPE-K 调和循环 | Monitor→Analyze→Plan→Execute 水平触发式对账 |
| 3 | 节律调度 | CircadianScheduler 日间/夜间/周末三周期 + DreamCycle 知识固化 |
| 4 | 健康监控 | HealthMonitor 分层检查 + 自愈触发 |
| 5 | 工作编排 | WorkOrchestrator DAG 驱动 + WIP 池 + 公平调度 |
| 6 | 自动接入 | ModuleOnboardingScanner + AutoIntegrator + OrphanDetector |
| 7 | 能力注册 | CapabilityRegistry + CapabilityCard |
| 8 | 审计日志 | AiAuditLogger AI 行为审计 |
| 9 | 状态面板 | StatusDashboard 实时聚合视图 |

### §2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 脚本执行 | MOD-INF-009 Pipeline |
| 2 | 进程池管理 | SYS-MASTER §〇 Worker Pool |
| 3 | 门禁规则执行 | MOD-INF-007 Gate Engine |
| 4 | 审计日志持久化优化 | SYS-MASTER §〇 #10 ADR-0038 |
| 5 | 拥塞控制算法 | SYS-MASTER §〇 #6 |
| 6 | 知识库存储 | MOD-KB-001 |
| 7 | 向量检索引擎 | MOD-INF-011 Vector Memory |

---

## §3 架构设计

### §3.1 组件架构

**五层同心圆架构**：L0 自举层 → L1 调和层 → L2 执行层 → L3 知识层 → L4 编排层

| # | 组件 | 层级 | 职责 | 依赖 | 交互方式 |
|---|------|:---:|------|------|---------|
| 1 | AutoRuntimeCore | L1 | MAPE-K 调和循环主控 | HealthMonitor, CapabilityRegistry | 同步调用 |
| 2 | AutoTaskGenerator | L2 | 自动扫描生成推理任务送 GPU（L2 本地推理队列任务，非 TaskCard/TaskRepository 任务卡。任务卡唯一合法入口 = MOD-INF-006 BlueprintDecomposer） | AutoRuntimeCore | 事件 |
| 3 | AutoIntegrator | L2 | 自动接入新模块 | ModuleOnboardingScanner | 同步调用 |
| 4 | ModuleOnboardingScanner | L2 | 发现未接入模块 | IntegrationRegistry | 同步调用 |
| 5 | OrphanDetector | L2 | 检测未被大脑管的模块 | IntegrationRegistry | 同步调用 |
| 6 | WorkOrchestrator | L4 | DAG 驱动任务调度 | CapabilityRegistry, Pipeline | 队列 |
| 7 | WorkDAG | L4 | DAG 数据模型 | WorkOrchestrator | 同步调用 |
| 8 | CircadianScheduler | L1 | 日间/夜间/周末节律调度 | DreamCycle, NightShiftQueue | 事件 |
| 9 | DreamCycle | L3 | 夜间知识固化 | KnowledgeBase, VectorMemory | 队列 |
| 10 | HealthMonitor | L1 | 健康监控+自愈 | AutoRuntimeCore | 事件 |
| 11 | FeedbackLoop | L1 | 反馈闭环 | AutoRuntimeCore | 事件 |
| 12 | CapabilityRegistry | L2 | 能力注册中心 | CapabilityCard | 同步调用 |
| 13 | CapabilityCard | L2 | 能力卡片数据模型 | — | — |
| 14 | StatusDashboard | L1 | 实时状态面板 | HealthMonitor, WorkOrchestrator | 共享存储 |
| 15 | NightShiftQueue | L3 | 夜班登记表 | CircadianScheduler | 队列 |
| 16 | AiAuditLogger | L2 | AI 行为审计日志 | — | 队列 |
| 17 | IntegrationRegistry | L2 | 集成注册表 | — | 同步调用 |
| 18 | RuntimeConfig | L0 | 配置模型 | — | — |
| 19 | StopGate | L1 | 质量闸门 | AutoRuntimeCore | 同步调用 |
| 20 | Finalizer | L1 | 优雅清理 | StopGate | 同步调用 |
| 21 | LifecycleManager | L0 | 启动/停止/健康检查序列 | AutoRuntimeCore | 同步调用 |
| 22 | ActionDispatcher | L2 | 动作分派器 | WorkOrchestrator | 同步调用 |
| 23 | TaskGate | L1 | 任务门禁 | AutoRuntimeCore | 同步调用 |
| 24 | WindowsService | L0 | Windows Service 包装器 | LifecycleManager | 同步调用 |

**三层 AI 工作分类**：

| 层级 | 名称 | 模型 | 用途 |
|------|------|------|------|
| L1 | Trae 层 | Claude/GPT-4 | IDE 内联操作——实时代码生成/审查 |
| L2 | Local 层 | DeepSeek/Ollama | 本地批量操作——脚本执行/审计扫描 |
| L3 | API 层 | GLM/Qwen | 远程推理——深度分析/策略生成 |

### §3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | 文件系统事件 / git log | MAPE-K Monitor 检测变更 | Analyze→Plan→Execute | HealthSnapshot |
| 2 | AI Session 请求 | WorkOrchestrator DAG 调度 | Pipeline 执行 | WorkDAG |
| 3 | 模块注册 | CapabilityRegistry 写入+缓存 | 路由决策 | CapabilityCard |
| 4 | 日间知识积累 | DreamCycle 夜间固化 | KnowledgeBase | KE 条目 |
| 5 | 健康检查 | HealthMonitor 分层检查 | 自愈/升级 | HealthSnapshot |

### §3.3 状态生命周期

**MAPE-K 调和循环状态**：

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| Idle | 文件变更事件 / 定时轮询 | Monitoring | 事件队列非空 |
| Monitoring | 收集完成 | Analyzing | HealthSnapshot 已生成 |
| Analyzing | 异常检测完成 | Planning | 需要修复 |
| Analyzing | 无异常 | Idle | — |
| Planning | 方案生成完成 | Executing | Plan 非空 |
| Executing | 执行完成 | Monitoring | 验证修复效果 |

**大脑降级状态**：

| 当前状态 | 触发条件 | 动作 |
|---------|---------|------|
| Lv0 Normal | CPU<75% & MEM<70% | 全功能运行 |
| Lv1 Throttle | CPU>75% 或 MEM>70% | StatusDashboard 降采样 / OrphanDetector 暂停 / DreamCycle 推迟 |
| Lv2 Shed | CPU>85% 或 MEM>80% | ModuleOnboardingScanner 纯增量 / MAPE-K 降频30s / AiAuditLogger 环形缓冲 |
| Lv3 Critical | CPU>95% 或 MEM>90% | 拒绝非P0 DAG / HealthMonitor 仅心跳 / 通知Owner / 5min未恢复→Kill Switch |

---

## §4 接口契约

### §4.1 公共 API

```python
class AutoRuntimeCore:
    """大脑主控——MAPE-K 调和循环"""

    def boot(self) -> "None":
        """启动大脑——加载所有组件，启动调和循环。输入：RuntimeConfig。输出：无。核心逻辑：LifecycleManager 初始化序列。"""

    def shutdown(self) -> "None":
        """优雅关闭——StopGate 判定 + Finalizer 清理。输入：无。输出：无。核心逻辑：等待活跃任务完成或超时。"""

    def submit_work(self, dag: "WorkDAG", priority: "int" = 1) -> "str":
        """提交工作 DAG。输入：WorkDAG + 优先级。输出：dag_id。核心逻辑：WorkOrchestrator 入队+公平调度。"""

class CapabilityRegistry:
    """能力注册中心"""

    def register(self, card: "CapabilityCard") -> "None":
        """注册能力卡片。输入：CapabilityCard。输出：无。核心逻辑：写穿更新内存+持久化。"""

    def find_by_tags(self, tags: "list[str]") -> "list[CapabilityCard]":
        """按标签查询能力。输入：标签列表。输出：匹配的能力卡片列表。核心逻辑：内存缓存 O(1) 查询。"""

class HealthMonitor:
    """健康监控+自愈"""

    def check_health(self, module_id: "str", depth: "str" = 'shallow') -> "HealthSnapshot":
        """检查模块健康。输入：module_id + 深度(shallow/deep)。输出：HealthSnapshot。核心逻辑：分层检查频率。"""
```

### §4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class DegradationLevel(str, Enum):
    NORMAL = "lv0_normal"
    THROTTLE = "lv1_throttle"
    SHED = "lv2_shed"
    CRITICAL = "lv3_critical"

class HealthSnapshot(BaseModel):
    module_id: str = Field(..., description="模块ID")
    status: str = Field(..., description="健康状态: healthy/degraded/failed")
    latency_ms: float = Field(..., description="检查耗时毫秒")
    checks: dict = Field(default_factory=dict, description="各检查项结果")

class WorkDAG(BaseModel):
    dag_id: str = Field(..., description="DAG唯一标识")
    session_id: str = Field(..., description="提交session")
    priority: int = Field(default=1, description="优先级 0=P0 1=P1 2=P2")
    tasks: list = Field(default_factory=list, description="任务节点列表")
    dependencies: dict = Field(default_factory=dict, description="任务依赖关系")
```

### §4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `submit_work()` | `dag` | ✅ | WorkDAG 实例，dag_id 唯一 |
| `submit_work()` | `priority` | ❌ | 0-2，默认1 |
| `register()` | `card` | ✅ | CapabilityCard 实例，module_id 唯一 |
| `check_health()` | `module_id` | ✅ | 已注册的模块ID |
| `check_health()` | `depth` | ❌ | shallow/deep，默认shallow |

### §4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `boot()` | 无（组件全部启动） | `BOOT_TIMEOUT` / `COMPONENT_INIT_FAILED` |
| `submit_work()` | `dag_id: str` | `WIP_POOL_FULL` / `INVALID_DAG` |
| `register()` | 无 | `DUPLICATE_MODULE` / `INVALID_CARD` |
| `find_by_tags()` | `list[CapabilityCard]` | 空列表（无匹配） |
| `check_health()` | `HealthSnapshot` | `MODULE_NOT_FOUND` / `CHECK_TIMEOUT` |

### §4.5 MCP 接口

本模块通过 MCP 暴露以下 Tools：

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `brain_status` | `StatusDashboard.get_status()` | `{section: str}` | `{health: dict, wip: int, degradation: str}` |
| `submit_task` | `WorkOrchestrator.submit_work()` | `{dag: WorkDAG, priority: int}` | `{dag_id: str}` |
| `query_capability` | `CapabilityRegistry.find_by_tags()` | `{tags: list[str]}` | `{cards: list[dict]}` |

**错误码**：`WIP_POOL_FULL(429)` — WIP池满 / `MODULE_NOT_FOUND(404)` — 模块未注册 / `DEGRADED(503)` — 大脑降级中

### §4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/方法 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名字段/方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |
| MCP 输入 Schema 修改 | ⚠️ 需通知 | 消费者需更新参数 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 原因 |
|---|------|------|
| 1 | Python 3.12+ / Pydantic V2 | 项目统一技术栈 |
| 2 | 单进程架构（大脑自身） | 大脑瓶颈在数据结构效率，不在 raw compute |
| 3 | GIL 限制下 I/O 密集用 ThreadPoolExecutor | GIL 对 I/O 无影响 |
| 4 | Windows Service 运行 | L0 自举层需 Windows 兼容 |
| 5 | 文件写入 MUST 原子操作（temp-file + os.replace） | Windows Defender + NTFS 锁竞争 |
| 6 | 禁止 open(path, "w") 省略 encoding="utf-8" | 编码一致性 |

### §5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 被管理模块数 | ~51 | 1,500 | MAPE-K 单轮 <200ms | ❌ 需事件驱动 | §17 T1 事件驱动增量对账 |
| AI 并发 Session | 0 | 100 | WorkOrchestrator WIP ≤100 | ❌ 需公平调度 | §17 T2 WIP 池+公平调度 |
| 治理脚本数 | ~268 | 10,000 | DreamCycle 夜间 4h 窗口 | ❌ 需轮转固化 | §17 T3 分层固化优先级 |
| CapabilityCard 内存 | ~51 条 | 1,500 条 | ~4.5MB 结构化 + overhead | ✅ 需缓存 | §17 T0 内存缓存 |
| 审计日志写入 | ~50 条/天 | 5,000 条/天 | SQLite 批量缓冲 | ✅ 已覆盖 | SYS-MASTER ADR-0038 |
| 大脑 RAM 预算 | ~50MB | 80-250MB 稳态 | 2GB 上限 | ✅ | RuntimeConfig max_brain_memory_mb: 2048 |
| GPU VRAM | 4GB 大脑独占 | 白天 Worker+夜间 DreamCycle | 24GB 总量 | ❌ 需调度 | §17 T1 GPU 时间分片 |

### §5.3 迁移/废弃方案

> ⚠️ 临时时态：迁移方案执行完毕后从蓝图删除。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| — | 无 | — | — | 本蓝图不涉及文件废弃或迁移，容量升级为增量式 | — |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | MAPE-K 调和循环超时(>5s) | 连续3轮 >5s | 暂停后台任务 + 降级Monitor粒度 + 通知Owner | 全局调度延迟 |
| 2 | WorkOrchestrator WIP 池满 | WIP > max_active_dag | 拒绝非P0 DAG submit | 新任务排队 |
| 3 | CapabilityRegistry 缓存命中率 <95% | 监控指标 | 检查缓存失效原因 + 扩大缓存 | 路由决策延迟 |
| 4 | DreamCycle 夜间窗口溢出 | 凌晨5:30未完成 | 提前截断 + 标记未完成模块下次优先 | 知识固化延迟 |
| 5 | 大脑进程崩溃 | 进程监控 | 重启读 schedule_state.json + SQLite 恢复DAG状态 | 全部AI Session 暂停 |
| 6 | GPU VRAM 不足(<4GB) | VRAM 监控 | DreamCycle 跳过重计算环节，次日补跑 | 知识固化降级 |
| 7 | 100 Session 并发审计写入 | 文件锁排队 | 切换环形内存缓冲+批量flush | 审计日志延迟 |
| 8 | 冷启动超时(>10s) | boot_timeout_ms | CapabilityCard 预索引批量加载 | 启动延迟 |

---


## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | AI Session 越权操作 | 高 | Agent RBAC (MOD-INF-018) 权限校验 | RBAC 单元测试 |
| 2 | 审计日志篡改 | 高 | AiAuditLogger append-only + 文件权限 | 日志完整性检查 |
| 3 | 大脑配置漂移 | 中 | Drift Detector (MOD-INF-023) 联动 | 漂移检测脚本 |
| 4 | GPU 资源争抢导致拒绝服务 | 中 | GPU 时间分片 + VRAM 硬分区 | GPU 监控指标 |
| 5 | 敏感数据泄露到日志 | 中 | AiAuditLogger 脱敏过滤 | 日志扫描 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 24 子组件核心方法 | MAPE-K 循环 / DAG 调度 / 能力注册 / 健康检查 | 覆盖率 >80% |
| 2 | 集成测试 | 大脑↔Pipeline / 大脑↔CapabilityRegistry / 大脑↔HealthMonitor | 端到端任务提交→执行→审计 | 端到端通过 |
| 3 | 容量测试 | 1,500 模块 / 100 AI 并发 | MAPE-K 循环延迟 / WIP 池公平性 / 内存预算 | P50 <500ms / 无饥饿 / <2GB |
| 4 | 降级测试 | Lv0→Lv1→Lv2→Lv3 降级链 | CPU/MEM 超限触发降级 | 降级动作正确执行 |
| 5 | 冷启动测试 | boot() 全流程 | 1,500 CapabilityCard 加载耗时 | P99 <10s |

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-002 (RI) | 必须 | EventStore/DryRun/CostTracker | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\runtime-integration\blueprint.md` |
| MOD-INF-016 (Shared) | 必须 | 事件总线/生命周期/日志/沙箱 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\shared-core\blueprint.md` |
| MOD-INF-009 (Pipeline) | 必须 | 管线任务调度与状态 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\pipeline\blueprint.md` |
| MOD-INF-034 (ModelProfiler) | 可选 | benchmark 结果用于路由决策 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\model-profiler\blueprint.md` |
| MOD-INF-007 (Gate) | 必须 | 执行结果门禁验证 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\gate-engine\blueprint.md` |
| MOD-INF-020 (AuditTrail) | 必须 | 操作审计日志写入 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\audit-trail\blueprint.md` |
| MOD-INF-010 (FLE) | 必须 | 异常上报与反馈闭环 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\feedback-loop-engine\blueprint.md` |
| MOD-INF-019 (AgentSpec) | 可选 | Skill 注册发现 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\agent-spec\blueprint.md` |
| MOD-KB-001 (KB) | 可选 | DreamCycle 知识固化目标 | — | `D:\ZephyrAlpha\docs\03_modules\l03_intelligence\knowledge-base\blueprint.md` |
| MOD-INF-011 (VMS) | 可选 | 向量知识检索 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vector-memory\blueprint.md` |
| SYS-MASTER-001 | 必须 | 系统总蓝图 | — | `D:\ZephyrAlpha\docs\03_modules\_sys-master\blueprint.md` |

---

### §10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-035` |

### §10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| 无内部脚本依赖 | — | — | — |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| 无内部数据流依赖 | — | — | — |

### §10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 模块数>10 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖 |


## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\runtime\` | 24 子组件 Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\runtime\` | 测试用例 |
| 启动脚本 | `D:\ZephyrAlpha\scripts\construction\start_brain.py` | 大脑启动入口 |
| 容量配置 | `D:\ZephyrAlpha\configs\capacity_params.yaml` | 容量预算参数 |
| 审计日志 | `D:\ZephyrAlpha\data\audit_logs\` | AI 行为审计 JSONL |
| 能力卡片 | `D:\ZephyrAlpha\data\capability_cards\` | CapabilityCard YAML |
| 工作 DAG | `D:\ZephyrAlpha\data\work_dags\` | WorkDAG 定义 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Pipeline (MOD-INF-009) | 新增接口 | WorkOrchestrator → Pipeline submit | 端到端任务执行 |
| CapabilityRegistry | 事件订阅 | 模块注册 → 大脑感知 | 新模块自动接入 |
| HealthMonitor | 定时轮询 | 分层健康检查 | 异常触发自愈 |
| AiAuditLogger | 写入接口 | 所有 AI 操作审计 | 日志完整性 |
| MCP Servers (MOD-INF-013) | MCP Tool 暴露 | brain_status / submit_task / query_capability | MCP 客户端调用 |

### §12.1 域契约锚点

> 权威定义见 [`../../_domain-governance/blueprint.md`](../../_domain-governance/blueprint.md) §3。

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-035-01 | 治理域 | 调度方（大脑→管线任务分发） | MOD-INF-009 | 修改分发接口必须同步更新 Pipeline 蓝图 |
| G-CT-035-02 | 治理域 | 消费方（benchmark→路由决策） | MOD-INF-034 | 修改路由逻辑必须同步更新 ModelProfiler 蓝图 |
| G-CT-035-03 | 治理域 | 产出方（操作→审计日志） | MOD-INF-020 | 修改审计格式必须同步更新 AuditTrail 蓝图 |
| G-CT-035-04 | 治理域 | 消费方（异常→反馈闭环） | MOD-INF-010 | 修改反馈协议必须同步更新 FLE 蓝图 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | 确认 MOD-INF-035 v6.0.0 | 版本升级 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 更新版本+generation+codification_level | 规格化完成 |
| 3 | spec.md | `D:\ZephyrAlpha\specs\auto-runtime-core\spec.md` | 追加容量需求章节 | spec 未含容量设计 |
| 4 | capacity_params.yaml | `D:\ZephyrAlpha\configs\capacity_params.yaml` | 追加 brain_dream_cycle_memory_mb / boot_timeout_ms / recovery_timeout_ms | 容量升级参数 |

---

## §14 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解策略 | 类型 |
|---|------|------|------|---------|
| 1 | MAPE-K 循环 O(1500) 退化 | 高 | 高 | 事件驱动增量对账 + 分层Monitor粒度 | 风险 |
| 2 | WorkOrchestrator 公平调度缺失 | 高 | 高 | WIP 池 + session 配额 + 饥饿防护 | 风险 |
| 3 | GPU Worker Pool 与 DreamCycle 踩踏 | 中 | 高 | GPU 时间分片 + VRAM 硬分区 | 风险 |
| 4 | 大脑自监控盲区 | 中 | 高 | MAPE-K 自观测 SLI + 自愈触发器 | 风险 |
| 5 | Agent Spec 语义路由缺失 | 中 | 中 | 向量检索替代关键词匹配（MOD-INF-019 承接） | 风险 |
| 6 | 冷启动 1,500 CapabilityCard 超时 | 低 | 中 | 预索引批量加载 + boot_timeout_ms: 10000 | 风险 |
| 7 | 100 Session 并发审计写入锁竞争 | 中 | 中 | 环形内存缓冲 + 批量flush | 风险 |


| N1 | 大脑成为单点——崩溃影响全部 AI Session | 高 | 高 | HealthMonitor 自愈 + 降级链 | 负面后果 |
| N2 | 容量升级需渐进落地（T0-T3 四个拐点） | 高 | 中 | §17 容量升级附录 | 负面后果 |
| N3 | GPU 调度增加运维复杂度 | 中 | 中 | GPU 时间分片 + VRAM 硬分区 | 负面后果 |



## §16 施工指引

### AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（§0-§18） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | capacity_params.yaml 已读取 | 确认容量参数 | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4 Phase（T0-T3 渐进落地） |
| 施工模式 | 扩展（在现有组件上追加规模适配） |
| 核心风险 | MAPE-K O(1500) 退化 + WorkOrchestrator 公平调度 |
| 目标 generation | 2 — 容量升级版 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | SYS-MASTER §〇 Worker Pool 已设计 | hard | ✅ | ☐ |
| 2 | Pipeline §0 IncrementalScanOrchestrator 已设计 | hard | ✅ | ☐ |
| 3 | SYS-MASTER §〇 #10 ADR-0038 SQLite 批量缓冲已设计 | hard | ✅ | ☐ |
| 4 | spec.md 容量章节已追加 | soft | ❌ | ☐ |

### 16.3 实施步骤

#### 步骤 1：T0 拐点（51→200 模块 / 1→5 AI）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 / §17 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\runtime\` |
| 验收标准 | CapabilityRegistry 内存缓存命中率 >95%；StatusDashboard 聚合视图可用；StopGate 预算生效 |
| 验证命令 | `python -m pytest tests/runtime/test_capability_registry.py tests/runtime/test_status_dashboard.py -v` |
| G7 检查项 | 缓存失效策略已定义？聚合维度已列出？StopGate 预算参数已配置？ |

**变更文件清单**：

| 文件 | 变更 |
|------|------|
| capability_registry.py | 追加内存缓存 + 读写锁 |
| status_dashboard.py | 追加聚合视图 + 下钻 |
| stop_gate.py | 追加 session 预算参数 |

#### 步骤 2：T1 拐点（200→500 模块 / 5→20 AI）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 / §17 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\runtime\` |
| 验收标准 | ModuleOnboardingScanner 增量 diff <3s；HealthMonitor 分层检查核心模块 30s/其他 5min；MAPE-K 事件驱动生效 |
| 验证命令 | `python -m pytest tests/runtime/test_onboarding_scanner.py tests/runtime/test_health_monitor.py tests/runtime/test_mape_k.py -v` |
| G7 检查项 | 增量 diff 算法已选？分层检查频率已配置？事件驱动+兜底轮询已实现？ |

**变更文件清单**：

| 文件 | 变更 |
|------|------|
| module_onboarding_scanner.py | 增量 diff 模式 + 自动注册 API |
| health_monitor.py | 分层检查频率 + 异常触发深检 |
| auto_runtime_core.py | 事件驱动 Monitor + 兜底轮询 |
| runtime_config.py | 追加 GPU 调度参数 + MAPE-K 自观测 SLI |

#### 步骤 3：T2 拐点（500→1,000 模块 / 20→50 AI）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 / §17 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\runtime\` |
| 验收标准 | WorkOrchestrator WIP 池 + 公平调度；CircadianScheduler 轮转策略生效；无饥饿任务 |
| 验证命令 | `python -m pytest tests/runtime/test_work_orchestrator.py tests/runtime/test_circadian_scheduler.py -v` |
| G7 检查项 | WIP 池深度已定？公平调度算法已选？饥饿防护超时已配置？ |

**变更文件清单**：

| 文件 | 变更 |
|------|------|
| work_orchestrator.py | WIP 池 + session 配额 + 饥饿防护 |
| circadian_scheduler.py | DreamCycle 轮转策略 + 窗口溢出截断 |

#### 步骤 4：T3 拐点（1,000→1,500 模块 / 50→100 AI）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 / §17 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\runtime\` |
| 验收标准 | DreamCycle 分层固化优先级生效；全量参数调优对齐 1,500；增量扫描 <1min / 全量周检 <75min |
| 验证命令 | `python -m pytest tests/runtime/test_dream_cycle.py tests/runtime/ -v --capacity` |
| G7 检查项 | 固化优先级已定义？知识老化策略已配置？全量参数已对齐？ |

**变更文件清单**：

| 文件 | 变更 |
|------|------|
| dream_cycle.py | 分层固化优先级 + 知识老化 + 去重 |
| runtime_config.py | 全量参数调优 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 缓存命中率不达标 | 禁用内存缓存，回退到直接查询 |
| 2 | 增量 diff 漏检 | 回退到全量扫描模式 |
| 3 | 公平调度死锁 | 禁用 WIP 限制，回退到无限制提交 |
| 4 | DreamCycle 固化失败 | 推迟到次日窗口，标记未完成 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | capability_registry.py | `D:\ZephyrAlpha\src\zephyr\runtime\capability_registry.py` | ☐ | ☐ | ☐ |
| 2 | work_orchestrator.py | `D:\ZephyrAlpha\src\zephyr\runtime\work_orchestrator.py` | ☐ | ☐ | ☐ |
| 3 | health_monitor.py | `D:\ZephyrAlpha\src\zephyr\runtime\health_monitor.py` | ☐ | ☐ | ☐ |
| 4 | dream_cycle.py | `D:\ZephyrAlpha\src\zephyr\runtime\dream_cycle.py` | ☐ | ☐ | ☐ |
| 5 | 测试套件 | `D:\ZephyrAlpha\tests\runtime\` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed (基线) / in_progress (容量升级) | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

---

## §17 容量升级附录

> generation=2 蓝图 MUST 填写此附录。增量式——只写新增/变更部分。

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 被管理模块数 | ~51 | IntegrationRegistry count |
| AI 并发 Session | 0 | WorkOrchestrator active DAG count |
| 治理脚本数 | ~268 | Pipeline script count |
| 大脑 RAM 稳态 | ~50MB | psutil.Process.memory_info().rss |
| GPU VRAM 大脑占用 | ~2GB | nvidia-smi |
| MAPE-K 单轮延迟 | ~50ms | mape_k_loop_latency_ms |
| 冷启动时间 | ~2s | boot() 耗时 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | MAPE-K 全量轮询 O(n) | 事件驱动增量对账 + 分层Monitor | 模块数 >200 |
| GAP-002 | WorkOrchestrator 无 WIP 限制 | WIP 池 + 跨Session公平调度 | 活跃 DAG >50 |
| GAP-003 | ModuleOnboardingScanner 全量扫描 | 增量 diff + 自动注册 | 全量扫描 >3s |
| GAP-004 | GPU 无调度模型 | 时间分片 + VRAM 硬分区 | AI 并发 >20 |
| GAP-005 | 大脑无自监控 | MAPE-K 自观测 SLI + 自愈触发器 | 始终需要 |
| GAP-006 | RAM 无预算 | max_brain_memory_mb + DreamCycle 分批 | 始终需要 |
| GAP-007 | 磁盘 I/O 无路径分析 | JSONL 环形缓冲 + 批量flush | AI 并发 >50 |
| GAP-008 | 组件交互无组合态分析 | BrainAdmissionController 全局准入 | AI 并发 >50 |
| GAP-009 | 无降级优先级链 | 四级降级链 Lv0-Lv3 | CPU>75% 或 MEM>70% |
| GAP-010 | 冷启动/崩溃恢复无 SLA | boot_timeout_ms + recovery_timeout_ms | 始终需要 |
| GAP-011 | Agent Spec 语义路由缺失 | 向量检索替代关键词匹配 | Skill 数 >500 |
| GAP-012 | AGENTS.md 触发表膨胀 | L0 分层索引 + L1 二级索引 | 模块数 >500 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v5.0.0 | 1 | 基线 | 24 子组件完整实现 | ✅ |
| v5.2.0-capacity-v2 | 2 | 容量升级设计 | 12 项压力测试 + 7 项补缺 + 四拐点矩阵 | ⚠️ 设计完成，代码待施工 |
| v6.0.0 | 2 | 规格化+容量升级 | 蓝图模板 v3.2 合规 + 规格化砍削 | ⚠️ 同上 |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-001 | MAPE-K 事件驱动增量对账 | P1 | v6.1.0 (T1) | 待施工 |
| GAP-002 | WorkOrchestrator WIP 公平调度 | P0 | v6.2.0 (T2) | 待施工 |
| GAP-003 | ModuleOnboardingScanner 增量 diff | P1 | v6.1.0 (T1) | 待施工 |
| GAP-004 | GPU 时间分片+VRAM硬分区 | P1 | v6.1.0 (T1) | 待施工 |
| GAP-005 | MAPE-K 自观测 SLI | P0 | v6.1.0 (T1) | 待施工 |
| GAP-006 | 大脑 RAM 预算 | P2 | v6.0.0 (T0) | 待施工 |
| GAP-007 | 磁盘 I/O 环形缓冲 | P2 | v6.2.0 (T2) | 待施工 |
| GAP-008 | BrainAdmissionController | P2 | v6.2.0 (T2) | 待施工 |
| GAP-009 | 四级降级链 | P1 | v6.0.0 (T0) | 待施工 |
| GAP-010 | 冷启动/崩溃恢复 SLA | P2 | v6.0.0 (T0) | 待施工 |
| GAP-011 | Agent Spec 语义路由 | P1 | v6.3.0 (T3) | 待施工(MOD-INF-019承接) |
| GAP-012 | AGENTS.md 分层索引 | P1 | v6.3.0 (T3) | 待施工(MOD-INF-019承接) |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| CapabilityRegistry 内存缓存 | GAP-006 | capability_registry.py | T0 | 待施工 |
| StatusDashboard 聚合视图 | — | status_dashboard.py | T0 | 待施工 |
| StopGate 预算 | — | stop_gate.py | T0 | 待施工 |
| MAPE-K 事件驱动 | GAP-001 | auto_runtime_core.py | T1 | 待施工 |
| HealthMonitor 分层检查 | GAP-001 | health_monitor.py | T1 | 待施工 |
| ModuleOnboardingScanner 增量 | GAP-003 | module_onboarding_scanner.py | T1 | 待施工 |
| GPU 调度模型 | GAP-004 | runtime_config.py | T1 | 待施工 |
| MAPE-K 自观测 SLI | GAP-005 | auto_runtime_core.py | T1 | 待施工 |
| WorkOrchestrator WIP 池 | GAP-002 | work_orchestrator.py | T2 | 待施工 |
| CircadianScheduler 轮转 | — | circadian_scheduler.py | T2 | 待施工 |
| BrainAdmissionController | GAP-008 | 新建 brain_admission_controller.py | T2 | 待施工 |
| DreamCycle 分层固化 | — | dream_cycle.py | T3 | 待施工 |

### 渐进式扩展触发矩阵

| 拐点 | 模块数 | AI 并发 | 触发条件 | 切换动作 |
|:---:|:---:|:---:|------|------|
| T0 | 51→200 | 1→5 | 当前到近期 | ① CapabilityRegistry 内存缓存 ② StatusDashboard 聚合视图 ③ StopGate 预算 ④ 降级链 ⑤ RAM 预算 ⑥ 冷启动 SLA |
| T1 | 200→500 | 5→20 | ModuleOnboardingScanner 全量扫 >3s | ⑦ 增量 diff ⑧ HealthMonitor 分层检查 ⑨ MAPE-K 事件驱动 ⑩ GPU 调度 ⑪ 自观测 SLI |
| T2 | 500→1,000 | 20→50 | WorkOrchestrator WIP >50 活跃 DAG | ⑫ WIP 池+公平调度 ⑬ CircadianScheduler 轮转 ⑭ BrainAdmissionController ⑮ 磁盘 I/O 环形缓冲 |
| T3 | 1,000→1,500 | 50→100 | DreamCycle 夜间窗口溢出 | ⑯ DreamCycle 分层固化 ⑰ 全量参数调优 ⑱ Agent Spec 语义路由(MOD-INF-019) ⑲ AGENTS.md 分层索引(MOD-INF-019) |

### 下游蓝图接口衔接

| 大脑需要的能力 | 下游承接蓝图 | 承接章节 | 状态 |
|------|------|------|:---:|
| 脚本并发执行 40-50 Worker | SYS-MASTER-001 | §〇-C Worker Pool | ✅ 已设计 |
| 增量扫描调度 + ScriptImpactMap | MOD-INF-009 | §0.3 IncrementalScanOrchestrator | ✅ 已设计 |
| SQLite 写入批量缓冲 | SYS-MASTER-001 | §〇 #10 ADR-0038 | ✅ 已设计 |
| 拥塞控制 / 扫描请求合并 | SYS-MASTER-001 | §〇 #6 | ✅ 已设计 |
| 共享基础组件并发安全 | MOD-INF-016 | §〇-B 18 项压力测试 | ✅ 已设计 |
| 硬件感知调度 | SYS-MASTER-001 | §〇 #5 | ✅ 已设计 |
| 知识库存储 | MOD-KB-001 | 知识库蓝图 | ⬜ 待确认 |
| 跨进程 ZephyrLock | SYS-MASTER-001 | §〇 #11 ADR-0037 | ✅ 已设计 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-INF035-01 | 大脑采用单进程架构 | A:单进程 B:多进程 | A | 大脑瓶颈在 I/O 不在 CPU，ThreadPoolExecutor 足够 | 2026-05-10 |
| 2 | D-INF035-02 | MAPE-K 采用事件驱动+兜底轮询 | A:纯轮询 B:纯事件 C:事件+兜底 | C | 纯轮询 O(1500) 不可接受；纯事件可能漏检 | 2026-05-10 |
| 3 | D-INF035-03 | 容量升级采用渐进式四拐点 | A:一次性 B:渐进式 | B | 模型渐进加入，不需要一次落地 | 2026-05-10 |
| 4 | D-INF035-04 | GPU 采用时间分片+VRAM硬分区 | A:无调度 B:时间分片 C:硬分区 D:B+C | D | 白天Worker+夜间DreamCycle 必须隔离 | 2026-05-10 |
| 5 | D-INF035-05 | 降级链采用四级(Lv0-Lv3) | A:三级 B:四级 | B | 需要 Throttle/Shed/Critical 三级降级 + Normal 基线 | 2026-05-10 |
| 6 | D-INF035-06 | Skill 路由采用语义向量检索 | A:关键词 B:语义向量 | B | 1500 Skill 下关键词冲突率不可接受 | 2026-05-10 |
| 7 | D-INF035-07 | AiAuditLogger 采用环形缓冲+批量flush | A:直接JSONL B:环形缓冲+flush | B | 100 Session 并发 append 文件锁排队 | 2026-05-10 |
| 8 | D-INF035-08 | 大脑 RAM 上限 2GB | A:1GB B:2GB C:4GB | B | 结构化数据 ~15MB + Python overhead ×3-5 = 80-250MB 稳态 | 2026-05-10 |
| 9 | D-INF035-09 | 冷启动 SLA P99 <10s | A:5s B:10s C:30s | B | 1500 CapabilityCard 批量加载 + 预索引 | 2026-05-10 |
| 10 | D-INF035-10 | Agent Spec 容量缺口由 MOD-INF-019 承接 | A:大脑设计 B:Agent Spec设计 | B | 大脑只消费接口，不设计 Skill 体系内部 | 2026-05-10 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | **必备链接不可省略**——即使与前序文档重复也必须完整列出 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程、不保存未选方案 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | 执行漂移——AI 自行决定，可能选错 |
| 9 | **蓝图必须自包含**——关键信息不能只写"详见XX" | 信息缺失——AI 缺少关键上下文 |
| 10 | **删除文件必须遵守安全删除协议**——禁止直接删除任何文件 | 永久丢失——无法恢复 |
| 11 | **construction_progress 必须与代码实际状态一致** | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4） | 代码文件是 SSoT，蓝图复制代码=双源漂移 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史 | 蓝图是当前设计文档，不是历史记录 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级 | 职责不同的内容强行塞一个蓝图=职责不清 | AI 不知道该读哪个蓝图 |

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
      a) 有独立的 module_id 前缀
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint-registry.yaml 同步更新
```

## ⚠️ 安全删除协议

### 蓝图中的删除决策清单

> 本蓝图不涉及文件废弃/迁移/删除。

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持1个Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | 编号规则、doc_type词表、frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\governance-methodology-standard.md` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\file-naming-standard.md` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai-autonomy-authority-registry.md` | AI 操作权限 |
| 9 | 详细规范 | — | `D:\ZephyrAlpha\specs\auto-runtime-core\spec.md` | SSoT 施工依据 |
| 10 | 容量参数 | — | `D:\ZephyrAlpha\configs\capacity_params.yaml` | 容量预算配置 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | PipelineOrchestrator | `D:\ZephyrAlpha\src\zephyr\pipeline\` | 任务调度 | Pipeline 管管线执行，大脑管全局调度——层级不同 |
| 2 | TaskRepository | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | 任务状态管理 | TaskRepository 是数据层，大脑是调度层 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | runtime 包 | `D:\ZephyrAlpha\src\zephyr\runtime\` | 修改 | 容量升级组件新增 |
| 2 | 测试目录 | `D:\ZephyrAlpha\tests\runtime\` | 修改 | 新增容量升级测试 |
| 3 | 启动脚本 | `D:\ZephyrAlpha\scripts\construction\start_brain.py` | 读取 | 启动入口 |
| 4 | 容量配置 | `D:\ZephyrAlpha\configs\capacity_params.yaml` | 修改 | 新增容量参数 |
| 5 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` | 修改 | 本文件 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 大脑核心架构设计 | **本文档 §1-§10** | 已取代的旧蓝图 |
| 大脑施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 大脑接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint-registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| 详细规范 | [spec.md](file:///D:/ZephyrAlpha/specs/auto-runtime-core/spec.md) | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-009 Pipeline 蓝图 | §4 接口契约、§12.1 域契约 |
| Tier 1 | MOD-INF-019 Agent Spec 蓝图 | §17 容量升级缺口 |
| Tier 1 | SYS-MASTER-001 系统总蓝图 | §3 架构设计、§10 依赖关系 |
| Tier 2 | MOD-INF-020 AuditTrail | §4.1 AiAuditLogger 接口 |
| Tier 2 | MOD-INF-007 GateEngine | §4.1 TaskGate 接口 |
| Tier 2 | MOD-INF-013 MCP Servers | §4.5 MCP 接口 |
| Tier 3 | src/zephyr/runtime/*.py | §4 数据模型、§11 产出物路径 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 |
| 修改 construction_progress | 下游更新依赖状态 | 更新集成测试 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-14 | 6.1.0 | v3.5模板升级：§0前移至概述后；§7备选方案删除；§15后果删除（负面合并到§14）；§0.1新增存在性列；§5.3标注临时时态；§10拆为4子节；§14新增类型列；铁律#13-#15；蓝图拆分判定标准；压缩工作流执行 |
| 2026-05-14 | 6.1.0 | 蓝图模板 v3.5 合规重构：新增概述段；章节重排（§0 移至 §15 后，规则参考段移至 §18 后）；frontmatter 新增 template_for、移除 codification_level/codification_at；§5.3 表格格式更新 |
| 2026-05-13 | 6.0.0 | 规格化 Layer 1（蓝图模板 v3.2 合规）+ Layer 2（砍对标/散文/设计过程）；新增 §0-§18 全部必需章节；容量升级内容映射到 §17；DOM-GOV-001 映射到 §12.1；frontmatter 新增 generation/functional_domain/codification_level |
| 2026-05-12 | 5.2.0 | 容量补缺 7 项（GPU调度/RAM/I-O/自监控/冷启动/交互矩阵/降级链） |
| 2026-05-10 | 5.1.0 | 容量升级方案 12 项压力测试 + 四拐点矩阵 + 下游接口衔接 |
| 2026-05-10 | 5.0.0 | 基线蓝图——24 子组件完整实现 |

---

## 蓝图特有章节

### 蓝图特有：容量设计交叉覆盖矩阵

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：跨蓝图容量完整性评估是大脑独有的顶层视角
> 不可砍理由：砍掉 = 丢失跨蓝图接口缺口信息，下一个 AI 不知道 Agent Spec 容量设计是零覆盖

| 容量维度 | AutoRuntime Core | Agent Spec | SYS-MASTER | Pipeline | Shared | Capacity-Assurance | 综合等级 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 并发 Session 管理 | 🟡 | ❌ 缺 | 🟡 | — | — | — | 🟡 有设计待落地 |
| 脚本并发执行 | 🟢 依赖下游 | — | 🟢 | 🟢 | — | — | 🟢 已设计 |
| 增量扫描调度 | 🟢 依赖 Pipeline | — | — | 🟢 | — | — | 🟢 已设计 |
| GPU VRAM 预算 | 🟡 GAP-004 | ❌ 缺 | 🟡 | — | — | — | 🟡 有设计/缺 Agent 视角 |
| RAM 内存预算 | 🟡 GAP-006 | ❌ 缺 | 🟢 | — | — | — | 🟢 有设计需细化 |
| 磁盘 I/O 路径 | 🟡 GAP-007 | ❌ 缺 | 🟡 | — | — | — | 🟡 有设计/分析 |
| 大脑自监控 | 🔴 GAP-005 | ❌ 缺 | — | — | — | — | 🔴 零覆盖→已识别 |
| 冷启动/崩溃恢复 | 🟡 GAP-010 | ❌ 缺 | — | — | — | — | 🟡 已识别 |
| Skill 加载机制 | — | 🔴 零覆盖 | — | — | 🟡 | — | 🔴 核心缺失 |
| Agent Spec 触发路由 | — | 🔴 零覆盖 | — | — | — | — | 🔴 核心缺失 |
| Skill 语义路由 | ❌ 缺接口 | 🔴 零覆盖 | — | — | — | — | 🔴 核心缺失 |
| SLI/SLO/Kill Switch | 🟢 依赖下游 | ❌ 缺 | 🟢 | — | — | 🟢 | 🟢 已设计 |

### 蓝图特有：大脑 12 组件压力测试审查

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：12 项审查是大脑独有的组件级容量分析
> 不可砍理由：砍掉 = 丢失每个组件的 O(n)→O(log n) 退化路径和设计决策

| # | 审查项 | 级别 | 需要新设计？ | 依赖下游？ |
|:--:|------|:--:|:--:|:--:|
| 1 | MAPE-K Monitor：全量轮询→事件驱动增量对账 | 🟡 | 是 | 否 |
| 2 | WorkOrchestrator：WIP 池+跨 Session 公平调度 | 🔴 | 是 | SYS-MASTER §〇 #2 |
| 3 | ModuleOnboardingScanner：全量扫→增量 diff | 🟡 | 是 | 否 |
| 4 | OrphanDetector：规模适应性 | 🟢 | 否 | — |
| 5 | CapabilityRegistry：并发读缓存 | 🟡 | 是 | MOD-INF-016 §〇 #1 |
| 6 | CircadianScheduler：夜间窗口容量规划 | 🟡 | 是 | 否 |
| 7 | DreamCycle：分层固化优先级 | 🟡 | 是 | MOD-KB-001 |
| 8 | HealthMonitor：分层检查频率 | 🟡 | 是 | 否 |
| 9 | AiAuditLogger：并发写入 | 🟢 已覆盖 | 否 | SYS-MASTER §〇 #10 |
| 10 | StatusDashboard：信息聚合视图 | 🟡 | 是 | 否 |
| 11 | IntegrationRegistry：引用完整性 | 🟢 | 否 | — |
| 12 | StopGate/Finalizer：高并发竞态 | 🟡 | 是 | 否 |

### 蓝图特有：组件并发交互矩阵

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：5×5 交互热度矩阵是大脑独有的组合态分析
> 不可砍理由：砍掉 = 丢失 WorkOrchestrator↔CapabilityRegistry 🔴高热度交互信息

|  | MAPE-K Monitor | WorkOrchestrator | CapabilityRegistry | HealthMonitor | AiAuditLogger |
|:--|:--:|:--:|:--:|:--:|:--:|
| MAPE-K Monitor | — | 🟢 低 | 🟡 中 | 🟡 中 | 🟢 低 |
| WorkOrchestrator | 🟡 中 | — | 🔴 高 | 🟢 低 | 🟡 中 |
| CapabilityRegistry | 🟡 中 | 🔴 高 | — | 🟢 低 | 🟢 低 |
| HealthMonitor | 🟡 中 | 🟢 低 | 🟢 低 | — | 🟢 低 |
| AiAuditLogger | 🟢 低 | 🟡 中 | 🟢 低 | 🟢 低 | — |

🔴 **热度极高交互**：WorkOrchestrator ↔ CapabilityRegistry——每次 resolve_layer() 查能力 → 100 AI × 每个 DAG 数个 task → 高 QPS。CapabilityRegistry 内存缓存 + 读写锁是关键防线。缓存命中率 <95% → 全局瓶颈。

### 蓝图特有：Agent Spec 容量缺口（MOD-INF-019 承接）

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：大脑与 Agent Spec 的接口缺口是跨蓝图协作关键
> 不可砍理由：砍掉 = 下一个 AI 不知道 Agent Spec 容量设计是零覆盖，不会推动 MOD-INF-019 补设计

| 大脑需要的能力 | Agent Spec 当前支持 | 目标状态 | 缺口级别 |
|------|:--:|:--:|:--:|
| "AI 在改模块 A"→ 加载 Skill A | 关键词触发表 O(N) | 语义向量路由 O(log N) | 🔴 |
| "新模块创建"→ 自动生成 Skill | 无 | AI 模板 + Owner 审核 | 🔴 |
| "蓝图变更"→ Skill FreshnessScore 批量重算 | 手动逐个 | 周检批量重算 | 🟡 |
| "100 AI 并发加载 Skill"→ 读缓存 | 无 | 对接 VectorMemory + Shared 缓存 | 🟡 |
| "1,500 个 Skill 的注册/发现"→ 目录索引 | 无 | CapabilityRegistry 扩展 | 🟡 |

**施工建议**：MOD-INF-019 Agent Spec 蓝图应在自身 §〇 中承接上述缺口。大脑只负责：① 感知新模块→通知 Agent Spec 生成 Skill；② 感知蓝图变更→触发 FreshnessScore 重算；③ 任务分配时从 Agent Spec 获取匹配 Domain Skill。

### 蓝图特有：撤回项澄清

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：防止 AI 误判"大脑缺了某设计"而重复造轮子
> 不可砍理由：砍掉 = AI 可能重新设计已有下游方案

| 已完成的独立设计 | 责任蓝图 | 大脑的消费边界 |
|------|------|------|
| Multi-Process Worker Pool | SYS-MASTER §〇 #1 | 大脑 submit task → Pool 执行 |
| 硬件感知调度 | SYS-MASTER §〇 #5 | 大脑声明 task 优先级 |
| IncrementalScanOrchestrator | Pipeline §0.3 | 大脑触发扫描 → Pipeline 执行 |
| ScriptImpactMap | Pipeline §0.3 | 消费结果 |
| ShardRouter 16 片 | Pipeline §0.5 | 消费路由结果 |
| 并发参数集中化 | Pipeline §0.6 | 消费 capacity_params.yaml |
| SQLite 批量缓冲 | SYS-MASTER §〇 #10 | AiAuditLogger 接入 |
| ZephyrLock 跨进程升级 | SYS-MASTER §〇 #11 | 大脑消费锁 |
| 拥塞控制 + 背压 | SYS-MASTER §〇 #6 | 大脑感知拥塞 |
| 18 项基础组件压力测试 | Shared §〇-B | 大脑消费 |
| SLI/SLO/Kill Switch 重校准 | MOD-INF-001 | 大脑消费 |

### 蓝图特有：容量升级施工总入口

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：跨 Phase 施工入口是大脑容量升级的执行路线图
> 不可砍理由：砍掉 = AI 不知道施工顺序和依赖关系

**Phase 0（蓝图先行——立即、不写代码）**:
1. MOD-INF-019 Agent Spec：创建 §〇 容量章节——承接 Agent Spec 容量缺口
2. AutoRuntime Core：将 MAPE-K Monitor 的"文件系统事件监控"修改为 `git-log polling`
3. 确认 Vector Memory (MOD-INF-011) 对 Skill embedding 索引的支持范围

**Phase 1（T0-T1 拐点）**:
4. GPU VRAM 监控 + 水位线
5. Session 生命周期状态机 + MAPE-K 自监控 SLI
6. CapabilityRegistry 内存缓存 + 读写锁
7. 大脑降级优先级链实现

**Phase 2（T2-T3 拐点）**:
8. Domain Skill 语义路由落地（MOD-INF-019 施工阶段）
9. 增量扫描假阴性三层防御
10. 全量分层抽样扫描 + DreamCycle 轮转固化

**完成标准**：1,500 模块、10,000 脚本、100 AI 并发 → 增量扫描 <1 分钟、全量周检 <75 分钟、CPU <80%、RAM <70%、VRAM <85%。

### 蓝图特有：蓝图增量变更计划

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：现有 §1-§7 的增量追加计划
> 不可砍理由：砍掉 = AI 不知道哪些章节需要追加规模适配子节

| 原章节 | 追加子节 | 内容 |
|------|------|------|
| §3.1 MAPE-K 调和循环 | §3.1.6 规模适配：事件驱动增量对账 | Monitor 阶段从全量轮询→事件驱动+兜底轮询；分层 Monitor 粒度 |
| §3.1 核心子组件表 | 追加 WorkOrchestrator 的 WIP 池参数行 | max_active_dag / session_fairness / starvation_timeout |
| §3.1 自动接入子系统 | §3.1.5 规模适配：增量检测 | ModuleOnboardingScanner 增量 diff 设计；自动注册 API |
| §3.1 节律调度 | §3.1.5 规模适配：轮转策略 | DreamCycle 按日轮转~215 模块；夜间窗口溢出截断 |
| §3.1 健康监控与自愈 | §3.1.5 规模适配：分层检查 | 核心模块 30s / 其他模块 5min；异常触发深检 |
