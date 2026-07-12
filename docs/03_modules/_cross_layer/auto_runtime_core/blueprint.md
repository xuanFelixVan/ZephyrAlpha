---
module_id: MOD-INF-035
submodule_path: src/zephyr/trading/autopilot
title: "AutoRuntime Core 蓝图 — 系统大脑·三层运行时运营中心"
doc_type: blueprint
template_for: blueprint
status: Active
version: "6.0.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-10"
valid_from: "2026-05-10"
ttl: permanent
construction_progress: completed
actual_disk_path: "src/zephyr/trading/"
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
runtime_plane: hot
blueprint_level: module
responsibility_domain: 
  - {target: "MOD-INF-016", at: "全篇", why: "Shared Core——事件总线/生命周期/日志/沙箱等公共基座"}
  - {target: "MOD-INF-009", at: "全篇", why: "Pipeline——大脑调度管线任务"}
  - {target: "MOD-INF-034", at: "全篇", why: "Model Profiler——大脑消费 benchmark 结果做模型路由"}
  - {target: "MOD-GATE_ENGINE", at: "§2", why: "Gate Engine——大脑执行结果需过门禁验证"}
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——大脑操作写入审计日志"}
  - {target: "MOD-FEEDBACK_LOOP", at: "§2", why: "Feedback Loop——大脑异常上报反馈闭环"}
references:
  - {id: "MOD-INF-019", at: "§2", why: "Agent Spec——大脑通过 Skill 注册发现新能力"}
  - {id: "MOD-INF-013", at: "§2", why: "MCP Servers——大脑能力通过 MCP 暴露"}
  - {id: "MOD-INF-023", at: "§2", why: "Drift Detector——大脑配置漂移检测联动"}
  - {id: "MOD-INF-021", at: "§2", why: "Rollback——大脑操作失败触发回滚"}
  - {id: "MOD-INF-024", at: "§2", why: "Budget Enforcer——大脑 Token/Cost 预算管控"}
  - {id: "MOD-INF-018", at: "§2", why: "Agent RBAC——大脑操作权限校验"}
  - {id: "MOD-KB-001", at: "§4", why: "Knowledge Base——大脑 Dream Cycle 知识固化目标"}
  - {id: "MOD-INF-011", at: "§2", why: "Vector Memory——大脑检索向量知识"}
  - {id: "MOD-CONTEXT_ENGINE", at: "§2", why: "Context Engine——大脑消费上下文注入"}
  - {id: "MOD-LLM_SECURITY", at: "§2", why: "LLM Security——大脑 LLM 调用的安全闸门"}
  - {id: "MOD-INF-022", at: "§2", why: "Escalation Protocol——大脑异常升级路径"}
design_maturity: prototype
build_status: generated
---

# AutoRuntime Core 蓝图 — 系统大脑·三层运行时运营中心

## 概述

本蓝图描述 AutoRuntime Core——ZephyrAlpha 的系统大脑。它解决了 1500 模块/10000 脚本/100 AI 并发下的全局运行时编排问题。核心职责包括：三层运行时编排、MAPE-K 调和循环、节律调度、健康监控、工作编排、自动接入。当前规模 51 模块/268 脚本/0 AI 并发，目标容量 1500 模块/10000 脚本/100 AI 并发。上游依赖 Pipeline/Gate Engine/Audit Trail，下游被所有模块消费。

> module_id: MOD-INF-035 | version: 6.0.0 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/trading/ | generation: 2 | construction_progress: completed
>
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-030`

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
| 10 | health-monitor.py | §3.1 | 健康监控+自愈 | 已实现 |
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
| `boot_cron_jobs.py` | § — | — | 已实现 | | 本模块 |
| `boot_hooks.py` | § — | — | 已实现 | | 本模块 |
| `capability_sync.py` | § — | — | 已实现 | | 本模块 |
| `resource_optimization.py` | § — | — | 已实现 | | 本模块 |
| `staging_area.py` | §RULE-ZERO | — | 已实现 | CP-1010~1014 多AI并发草稿写入+提交+冲突检测 | 本模块 |
| `__main__.py` | § — | — | 已实现 | | 本模块 |
| `__main__.py` | § — | — | 已实现 | | 本模块 |
| `gpu_monitor.py` | § — | — | 已实现 | | 本模块 |
| `ide_health_daemon.py` | § — | — | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/trading/` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" src/zephyr/trading/autopilot.py` | ☐ |
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
| 5 | SQLite 批量缓冲 | SYS-MASTER §〇 #10 (KBG-0038) 负责 |
| 6 | 跨进程锁协议 | SYS-MASTER §〇 #11 (KBG-0037) 负责 |
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
| 3 | 门禁规则执行 | MOD-GATE_ENGINE Gate Engine |
| 4 | 审计日志持久化优化 | SYS-MASTER §〇 #10 KBG-0038 |
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
| 2 | AutoTaskGenerator | L2 | 自动扫描生成推理任务送 GPU（L2 本地推理队列任务，非 TaskCard/TaskRepository 任务卡。任务卡唯一合法入口 = MOD-TASK_SYSTEM BlueprintDecomposer） | AutoRuntimeCore | 事件 |
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
| 审计日志写入 | ~50 条/天 | 5,000 条/天 | SQLite 批量缓冲 | ✅ 已覆盖 | SYS-MASTER KBG-0038 |
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
| MOD-INF-002 (RI) | 必须 | EventStore/DryRun/CostTracker | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\runtime_integration\blueprint.md` |
| MOD-INF-016 (Shared) | 必须 | 事件总线/生命周期/日志/沙箱 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\shared_core\blueprint.md` |
| MOD-INF-009 (Pipeline) | 必须 | 管线任务调度与状态 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\pipeline\blueprint.md` |
| MOD-INF-034 (ModelProfiler) | 可选 | benchmark 结果用于路由决策 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\model-profiler\blueprint.md` |
| MOD-GATE_ENGINE (Gate) | 必须 | 执行结果门禁验证 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md` |
| MOD-INF-020 (AuditTrail) | 必须 | 操作审计日志写入 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-FEEDBACK_LOOP (FLE) | 必须 | 异常上报与反馈闭环 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\feedback_loop-engine\blueprint.md` |
| MOD-INF-019 (AgentSpec) | 可选 | Skill 注册发现 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-spec\blueprint.md` |
| MOD-KB-001 (KB) | 可选 | DreamCycle 知识固化目标 | — | `D:\ZephyrAlpha\docs\03_modules\l03_intelligence\knowledge_base\blueprint.md` |
| MOD-INF-011 (VMS) | 可选 | 向量知识检索 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\vector_memory\blueprint.md` |
| SYS-MASTER-001 | 必须 | 系统总蓝图 | — | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` |

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
| 容量配置 | `D:\ZephyrAlpha\config\capacity_params.yaml` | 容量预算参数 |
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

> 权威定义见 [`../../_domain_governance/blueprint.md`](../../_domain_governance/blueprint.md) §3。

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-035-01 | 治理域 | 调度方（大脑→管线任务分发） | MOD-INF-009 | 修改分发接口必须同步更新 Pipeline 蓝图 |
| G-CT-035-02 | 治理域 | 消费方（benchmark→路由决策） | MOD-INF-034 | 修改路由逻辑必须同步更新 ModelProfiler 蓝图 |
| G-CT-035-03 | 治理域 | 产出方（操作→审计日志） | MOD-INF-020 | 修改审计格式必须同步更新 AuditTrail 蓝图 |
| G-CT-035-04 | 治理域 | 消费方（异常→反馈闭环） | MOD-FEEDBACK_LOOP | 修改反馈协议必须同步更新 FLE 蓝图 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\architecture_model\module_id_registry.yaml` | 确认 MOD-INF-035 v6.0.0 | 版本升级 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 更新版本+generation+codification_level | 规格化完成 |
| 3 | spec.md | 见本蓝图附录A | 追加容量需求章节 | spec 未含容量设计 |
| 4 | capacity_params.yaml | `D:\ZephyrAlpha\config\capacity_params.yaml` | 追加 brain_dream_cycle_memory_mb / boot_timeout_ms / recovery_timeout_ms | 容量升级参数 |

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
| 3 | SYS-MASTER §〇 #10 KBG-0038 SQLite 批量缓冲已设计 | hard | ✅ | ☐ |
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
| health-monitor.py | 分层检查频率 + 异常触发深检 |
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
| 3 | health-monitor.py | `D:\ZephyrAlpha\src\zephyr\runtime\health-monitor.py` | ☐ | ☐ | ☐ |
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
| HealthMonitor 分层检查 | GAP-001 | health-monitor.py | T1 | 待施工 |
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
| SQLite 写入批量缓冲 | SYS-MASTER-001 | §〇 #10 KBG-0038 | ✅ 已设计 |
| 拥塞控制 / 扫描请求合并 | SYS-MASTER-001 | §〇 #6 | ✅ 已设计 |
| 共享基础组件并发安全 | MOD-INF-016 | §〇-B 18 项压力测试 | ✅ 已设计 |
| 硬件感知调度 | SYS-MASTER-001 | §〇 #5 | ✅ 已设计 |
| 知识库存储 | MOD-KB-001 | 知识库蓝图 | ⬜ 待确认 |
| 跨进程 ZephyrLock | SYS-MASTER-001 | §〇 #11 KBG-0037 | ✅ 已设计 |

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
  - blueprint_registry.yaml 同步更新
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
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表、frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 详细规范 | — | `D:\ZephyrAlpha\specs\auto_runtime_core\spec.md` | SSoT 施工依据 |
| 10 | 容量参数 | — | `D:\ZephyrAlpha\config\capacity_params.yaml` | 容量预算配置 |

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
| 4 | 容量配置 | `D:\ZephyrAlpha\config\capacity_params.yaml` | 修改 | 新增容量参数 |
| 5 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` | 修改 | 本文件 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 大脑核心架构设计 | **本文档 §1-§10** | 已取代的旧蓝图 |
| 大脑施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 大脑接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| 详细规范 | 见本蓝图附录A | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-009 Pipeline 蓝图 | §4 接口契约、§12.1 域契约 |
| Tier 1 | MOD-INF-019 Agent Spec 蓝图 | §17 容量升级缺口 |
| Tier 1 | SYS-MASTER-001 系统总蓝图 | §3 架构设计、§10 依赖关系 |
| Tier 2 | MOD-INF-020 AuditTrail | §4.1 AiAuditLogger 接口 |
| Tier 2 | MOD-GATE_ENGINE GateEngine | §4.1 TaskGate 接口 |
| Tier 2 | MOD-INF-013 MCP Servers | §4.5 MCP 接口 |
| Tier 3 | src/zephyr/trading/autopilot.py | §4 数据模型、§11 产出物路径 |

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
| 2026-05-13 | 6.0.0 | 规格化 Layer 1（蓝图模板 v3.2 合规）+ Layer 2（砍对标/散文/设计过程）；新增 §0-§18 全部必需章节；容量升级内容映射到 §17；MOD-GOVERNANCE 映射到 §12.1；frontmatter 新增 generation/functional_domain/codification_level |
| 2026-05-12 | 5.2.0 | 容量补缺 7 项（GPU调度/RAM/I-O/自监控/冷启动/交互矩阵/降级链） |
| 2026-05-10 | 5.1.0 | 容量升级方案 12 项压力测试 + 四拐点矩阵 + 下游接口衔接 |
| 2026-05-10 | 5.0.0 | 基线蓝图——24 子组件完整实现 |

---

## 蓝图特有章节

### 蓝图特有：容量设计交叉覆盖矩阵

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：跨蓝图容量完整性评估是大脑独有的顶层视角
> 不可砍理由：砍掉 = 丢失跨蓝图接口缺口信息，下一个 AI 不知道 Agent Spec 容量设计是零覆盖

| 容量维度 | AutoRuntime Core | Agent Spec | SYS-MASTER | Pipeline | Shared | capacity_assurance | 综合等级 |
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

---

### 蓝图特有：强制物理隔离层（Forced Physical Isolation Layer, FP-ISO）

> 来源：2026-07-01 治本方案设计——解决多 AI 并发执行时"做着做着全部丢失"的元问题
> 仅本蓝图需要：worktree 物理隔离是 AutoRuntime Core 独有的并发安全基础设施
> 不可砍理由：砍掉 = 多 AI 并发覆盖修改的根因永远无法消除，held_files "仅预警不阻断" 设计缺陷永久存在

#### FP-ISO.1 章节定位

本章节定义 ZephyrAlpha 多 AI 并发执行的**强制物理隔离层**。这是对 [parallel_session_coordination_policy.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md) §5.2「不新增阻断层」设计的**治本修订**——现有"仅预警不阻断"无法防止编辑期文件覆盖，必须新增物理隔离作为最强阻断。

#### FP-ISO.2 现有功能盘点（已实现基础设施）

| # | 组件 | 完整绝对路径 | 现有能力 | 缺口 |
|---|------|------------|---------|------|
| 1 | WorktreeManager | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\worktree_manager.py` | create/merge/cleanup/get_current session worktree | **未强制启用**——能力存在但 AI 可绕过 |
| 2 | GitCommitGateway | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\git_commit_gateway.py` | 全局跨进程串行锁 + PID 僵尸检测 + TTL 1800s | 主目录裸 commit 仅 logger.info「建议」，**未硬阻断** |
| 3 | HeldOverlapGate | `D:\ZephyrAlpha\src\zephyr\governance\commit_gates\held_overlap_gate.py` | commit 时检测搭便车（目标文件被其他 session 持有）| **仅 commit 时检测**，编辑期无防护 |
| 4 | SessionRegistry | `D:\ZephyrAlpha\src\zephyr\security\access_control\session_concurrency.py` | session 注册/心跳/claim_file/release_file | held_files 是「预警不阻断」（policy §3.2 明确） |
| 5 | SessionHandoff | `D:\ZephyrAlpha\src\zephyr\security\access_control\session_concurrency.py` | 跨 session 状态交接包 `.runtime/handoffs/` | 已落地，不涉及隔离 |
| 6 | parallel_session_coordination_policy | `D:\ZephyrAlpha\docs\01_policies_and_standards\policies\parallel_session_coordination_policy.md` | §5.2「不新增阻断层」+ §7「最外层可见性」 | **设计缺陷**：把阻断责任推给 GitCommitGateway，但全局锁只串行化 commit 不防编辑覆盖 |

**关键洞察**：项目已具备完整治本基础设施（WorktreeManager 全功能实现），致命缺口是**「能力存在但未强制启用」**——GitCommitGateway 第331-341行检测到不在 worktree 时只 `logger.info` 然后向后兼容直接 commit。

#### FP-ISO.3 病根分析（L4 元问题）

| 层级 | 问题 | 证据 |
|------|------|------|
| L1 现象 | P0/P1 修改被并发 AI 覆盖丢失 | session_manager.py _db_path 死字段、session_lifecycle.py trust-score 4处、session_state_machine.yaml 路径断裂反复出现 |
| L2 直接原因 | 多 AI 在主工作目录 `D:\ZephyrAlpha` 裸跑，编辑期无隔离 | 10-20 个 AI 共享同一工作区，行级覆盖无声丢失 |
| L3 设计原因 | held_files 协议是「预警不阻断」（policy §3.2/§5.2/§7） | GitCommitGateway 全局锁只串行化 commit，AI A 编辑 → AI B 编辑 → AI B commit → AI A 工作区基线已变 |
| L4 元问题 | **WorktreeManager 物理隔离能力已实现但未强制启用** | git_commit_gateway.py 第336-341行 `wt_session is None` 时 `logger.info("建议使用")` + 向后兼容直接 commit |

**治本原则**：把「可选」变「强制」。Anthropic 16-agent C 编译器案例证明 worktree 物理隔离 + git push 协调足以支撑 16 个 AI 并行产出 10 万行代码，前提是**强制启用**而非「建议」。

#### FP-ISO.3.5 工作模式适配（关键决策点）

> 本节定义两种并发工作模式，**当前 ZephyrAlpha 采用模式B**。

| 模式 | 触发方式 | 工作目录 | worktree 物理隔离 | 当前采用 |
|------|---------|---------|:---:|:---:|
| **模式A：命令行编排** | `spawn_agent.ps1` 启动独立 AI 进程 | 每个 AI 独立 worktree | ✅ 强制可用 | ❌ |
| **模式B：Trae IDE 对话并发** | Trae IDE 内开多个 AI 对话 | **共享 `D:\ZephyrAlpha`** | ❌ 无法直接用 | ✅ 当前 |

**模式B 的核心约束**（决定方案差异）：
1. Trae IDE 工作目录固定为 `D:\ZephyrAlpha`，所有 AI 对话共享同一工作区
2. AI 用 Trae 的 Edit/Write 工具直接改主目录文件，**编辑瞬间系统无法拦截**
3. 多个 AI 对话在同一个 Trae 进程内，无法用 spawn_agent.ps1 切换目录
4. 硬阻断主目录 commit = 所有 AI 都不能 commit = 项目停摆

**模式B 治本策略**：「软编辑 + 硬提交」——编辑期靠 AI 自觉 claim（系统提供冲突可见性），提交期靠 GitCommitGateway 硬校验（未 claim / 冲突文件拒绝提交）。无法 100% 防止编辑期覆盖，但能 100% 防止覆盖被提交——覆盖即使发生，commit 时被拒绝，迫使 AI 重新基于最新基线编辑。

#### FP-ISO.4 治本三件套设计（模式A：命令行编排——不适用于当前 Trae 工作流）

> ⚠️ 本节方案适用于模式A（命令行启动独立 AI 进程）。**当前 ZephyrAlpha 采用模式B（Trae IDE 对话），本节方案不适用，保留作为模式A 参考与未来切换储备。实际采用方案见 [FP-ISO.4B](#fp-iso4b-治本三件套设计模式btrae-ide-适配当前采用)。**

##### 件1：GitCommitGateway 硬阻断主目录 commit（核心改动）

| 项目 | 内容 |
|------|------|
| 变更文件 | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\git_commit_gateway.py` |
| 变更位置 | 第326-341行 worktree 检测分支 |
| 变更内容 | `wt_session is None` 时返回 `CommitStatus.MAIN_BRANCH_VIOLATION`（不再向后兼容） |
| 新增参数 | `commit(..., allow_main_branch: bool = False)`——逃生通道，对标现有 `allow_overlap` |
| 新增枚举 | `CommitStatus.MAIN_BRANCH_VIOLATION` |
| 阻断逻辑 | `if wt_session is None and not allow_main_branch: return CommitResult(status=MAIN_BRANCH_VIOLATION, message="主工作目录禁止裸 commit，必须先 create_session_worktree() 物理隔离")` |
| 逃生通道 | `commit(allow_main_branch=True)` 仍可在主目录 commit（向后兼容紧急场景） |
| 验收 | 主目录裸 commit 返回 MAIN_BRANCH_VIOLATION；`allow_main_branch=True` 通过；worktree 内 commit 通过 |

##### 件2：spawn_agent.ps1 全自动编排脚本

| 项目 | 内容 |
|------|------|
| 新建文件 | `D:\ZephyrAlpha\scripts\governance\spawn_agent.ps1` |
| 职责 | 串联「分配 session_id → 创建 worktree → 切目录 → 启动 AI → 退出 merge/cleanup」全自动流程 |
| 复用组件 | WorktreeManager.create_session_worktree / merge_session_worktree / cleanup_session_worktree |
| 参数 | `-Task <任务描述>` `-AiTool <trae/cursor/codex>` `-MergeOnExit <switch>` |
| session_id 规则 | `sess-{PID}-{yyyyMMddHHmmss}` 全局唯一 |
| 退出处理 | AI 退出后自动 merge_session_worktree（冲突时保留 worktree 供人工解决）或 cleanup_session_worktree |
| 验收 | 脚本启动后 AI 在独立 worktree 工作；退出后 worktree 自动 merge 或清理；无 worktree 泄漏 |

##### 件3：git pre-commit hook OS 层兜底

| 项目 | 内容 |
|------|------|
| 新建文件 | `D:\ZephyrAlpha\.git\hooks\pre-commit` |
| 职责 | 检测当前是否在 session worktree 内，不在则拒绝 commit（防 AI 绕过 GitCommitGateway 裸调 git） |
| 检测逻辑 | `git rev-parse --git-dir` vs `git rev-parse --git-common-dir`，相等即主工作目录 |
| 逃生通道 | 环境变量 `ZEPHYR_ALLOW_MAIN_BRANCH=1` |
| 验收 | 主目录 `git commit` 被拒；worktree 内 `git commit` 通过；`ZEPHYR_ALLOW_MAIN_BRANCH=1 git commit` 通过 |

#### FP-ISO.4B 治本三件套设计（模式B：Trae IDE 适配——P2 防搭便车提交）【已废弃，superseded by FP-ISO.4C】

> 🟡 **本节降级为 P2 方案**（2026-07-01 更新）。41 个并发丢失案例分析表明，FP-ISO.4B 的「软编辑+硬提交」只能防 Mode C（搭便车 commit，7%），无法防 Mode A（git stash/reset 冲掉工作区，51%）和 Mode B（直接编辑覆盖，17%）。治本方案已升级为 [FP-ISO.4C worktree 物理隔离](#fp-iso4c-治本方案worktree-物理隔离当前采用)。FP-ISO.4B 保留为 P2——SessionRequiredGate/ClaimRequiredGate/HeldOverlapGate 防主工作目录直接 commit 的搭便车场景。
>
> ⚠️ **session_claim API 已废弃**（2026-07-04 更新）。`session_claim_start`/`add`/`check`/`heartbeat`/`end` 零实际调用方（死代码），claim 语义已被 `session_worktree_commit` 的 `HELD-OVERLAP` 硬阻断完全替代且更强。`generate_session_id` 保留（被 `session_worktree.py` 调用）。AI 对话启动请改用 `session_worktree_start`（FP-ISO.4C）。

##### 件1改：GitCommitGateway commit 时强校验 claim（核心改动）

| 项目 | 内容 |
|------|------|
| 变更文件 | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\git_commit_gateway.py` |
| 变更位置 | commit 流程中 HeldOverlapGate 调用处 |
| 变更内容 | HeldOverlapGate 从「warning 不阻断」升级为「reject 阻断」——commit 时对所有 staged 文件做三元校验 |
| 校验规则 | ① 文件在当前 session 的 claim 列表 → ✅ 通过；② 文件被其他活跃 session claim → ❌ 拒绝（防搭便车覆盖）；③ 文件未 claim → ❌ 拒绝（强制 AI 先声明） |
| 新增参数 | `commit(..., allow_unclaimed: bool = False)`——逃生通道（对标现有 `allow_overlap`），用于紧急修复未 claim 文件 |
| 新增状态 | `CommitStatus.CLAIM_VIOLATION`（文件被他人 claim）、`CommitStatus.UNCLAIMED_VIOLATION`（文件未 claim） |
| 复用组件 | 现有 SessionRegistry.claim_file / other_held_files + HeldOverlapGate 扩展 |
| 验收 | ① 两个 AI claim 同一文件，后到者 commit 被拒返回 CLAIM_VIOLATION；② 未 claim 文件 commit 被拒返回 UNCLAIMED_VIOLATION；③ `allow_unclaimed=True` 通过；④ claim 内文件 commit 通过 |

##### 件2改：SessionClaim helper（AI 启动必调）

| 项目 | 内容 |
|------|------|
| 新建文件 | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\session_claim.py` |
| 职责 | 提供 AI 对话启动时的 session 注册 + 文件 claim + 冲突检测一体化接口 |
| 核心 API | `session_claim_start(session_id, files=[])` 启动并声明；`session_claim_add(session_id, file)` 追加声明；`session_claim_check(file, session_id)` 写前检测；`session_claim_end(session_id)` 结束释放 |
| session_id 生成 | `sess-{PID}-{yyyyMMddHHmmss}`（Trae 对话无内置 session_id，用 PID+时间戳；同一 Trae 进程内多对话用对话索引区分） |
| 冲突语义 | `session_claim_add` 返回 `{"conflict": True, "owner": "sess-xxx"}` 时 AI 须等待或换文件（软约束，AGENTS.md 规定 AI 必须遵守） |
| 复用组件 | 现有 SessionRegistry（扩展 claim 为阻断语义）+ SessionHandoff |
| AGENTS.md 规则 | 新增「AI 对话启动第一步：调用 session_claim_start 声明 session 与将修改文件；改新文件前调用 session_claim_add；冲突时必须等待或换文件」 |
| 验收 | AI 启动调用 session_claim_start 后，SessionRegistry 有记录；claim 冲突时返回 conflict=True；AI 结束调用 session_claim_end 后 claim 释放 |

##### 件3改：可选 worktree 隔离（高风险任务专用，非强制）

| 项目 | 内容 |
|------|------|
| 复用文件 | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\worktree_manager.py`（已实现，无改动） |
| 职责 | 对改契约文件/大范围重构等高风险任务，AI 可选择 `WorktreeManager.create_session_worktree()` 创建 worktree，在 worktree 内操作后 merge 回主目录 |
| 使用场景 | ① 修改 GitCommitGateway/WorktreeManager 等契约文件本身；② 大范围重构（>10 文件）；③ 实验性改动（不确定是否保留） |
| 非强制原因 | Trae 模式下 AI 默认在主目录用 Trae 工具操作，强制 worktree 会破坏 IDE 工作流；worktree 内 AI 需手动用完整路径，增加认知负担 |
| 与件1/件2关系 | ~~worktree 内 AI 仍须 session_claim_start~~（**已废弃 2026-07-04**：session_claim_start 零调用方，claim 语义已被 session_worktree_commit 的 HELD-OVERLAP 硬阻断替代）；worktree commit 时 GitCommitGateway 仍校验 claim |
| 验收 | `WorktreeManager.create_session_worktree()` 返回 worktree 路径；AI 在 worktree 内 commit 通过；merge 回主目录成功 |

#### FP-ISO.4C 治本方案：worktree 物理隔离（当前采用）

> ✅ **本节为当前治本方案**（2026-07-01 采用）。基于 41 个并发丢失案例分析，worktree 物理隔离是唯一同时覆盖 Mode A（51%）+ Mode B（17%）+ Mode D（7%）= 75%+ 丢失场景的方案。

##### 病根数据（41 案例分析）

从 Trae memory 文件挖掘 41 个并发丢失案例，按失败模式分类：

| 模式 | 占比 | 描述 | FP-ISO.4B 能否防 |
|------|:---:|------|:---:|
| **Mode A** | **51%** | git stash/reset/checkout 冲掉工作区（THE #1 KILLER） | ❌ |
| **Mode B** | **17%** | 直接编辑同一文件覆盖 | ❌ |
| Mode C | 7% | 搭便车/幽灵 commit（他人文件混入） | ✅ 唯一能防 |
| Mode D | 7% | 未 commit 被回收（永久丢失，损害最高） | ❌ |
| 其他 | 18% | 混合/不明 | — |

**结论**：FP-ISO.4B 只能防 7%（Mode C），worktree 物理隔离能防 75%+（A+B+D）。

##### 核心设计：每 AI 对话独占一个 git worktree

```
主工作目录 (D:\ZephyrAlpha)
├── .aidrafts/
│   ├── sess-12345-20260701223518/    ← AI 对话 A 的独立 worktree
│   │   └── (独立 git index，A 的修改不进入主工作区)
│   └── sess-67890-20260701223519/    ← AI 对话 B 的独立 worktree
│       └── (独立 git index，B 的修改不进入主工作区)
└── (主分支，merge 后才出现 A/B 的改动)
```

**为什么 worktree 能治 A+B+D**：
- **Mode A（stash/reset 冲掉）**：worktree 有独立 index，AI 在自己 worktree 内的 git 操作不影响其他 worktree 和主工作区
- **Mode B（编辑覆盖）**：各 AI 在物理隔离的目录操作，不存在"同一文件"问题
- **Mode D（未 commit 丢失）**：worktree 内的修改持久存在于 `.aidrafts/{sid}/`，不会被主工作区的 git 操作回收

##### 实现组件

| 组件 | 文件 | 职责 |
|------|------|------|
| **session_worktree.py**（新建）| `src/zephyr/governance/rule_bridge/session_worktree.py` | AI 对话 worktree 生命周期 helper（5 函数：start/commit/merge/abort/status）|
| **worktree_manager.py**（现有+修复）| `src/zephyr/governance/rule_bridge/worktree_manager.py` | 底层 worktree 引擎（create/merge/cleanup/list）；修复 `_worktree_exists` 路径标准化 bug（Windows `\` vs `/`）|
| **GATE-COMMIT-GW**（现有+扩展）| `scripts/governance/d11_compliance/validate_commit_gateway.py` | 新增 `_is_session_worktree_commit()` 放行 worktree 内 commit（FP-ISO.4C 授权绕过 GitCommitGateway）|

##### AI 对话工作流（AGENTS.md 规定，君子协定模式 2026-07-02）

```
1. 对话启动 → session_worktree_start(session_id) → 返回 worktree_path
2. AI 用 Edit/Write 正常编辑文件（写项目根，IDE 限制无法改 cwd）
3. 提交 → session_worktree_commit(session_id, files, message)
   → 自动 shutil.copy2 同步 files 从项目根到 worktree（解决 Edit/Write 写项目根的问题）
   → worktree 内 git add + commit（独立 index，无需 GitCommitGateway）
   （worktree 内 commit 用 --no-verify 绕过 pre-commit hooks，与 GitCommitGateway 一致；
    GATE-COMMIT-GW 检测 worktree 上下文自动放行）
4. 任务完成 → session_worktree_merge(session_id) → merge 回主分支 + 清理 worktree
5. 放弃任务 → session_worktree_abort(session_id) → 丢弃修改 + 清理 worktree
```

> **君子协定测试状态（2026-07-02）**：Trae IDE 不支持自动触发 worktree（无启动 hook、IDE 不可 hook、AI 不可改 cwd），当前走君子协定——AI 自觉调 start/commit/merge，对标 AI 自觉查锁。文件同步已实现（`session_worktree_commit` 内 `shutil.copy2` 项目根→worktree），AI 无需手动同步。判定标准：连续 5 轮 AI 自觉遵守→转正式规则；AI 绕过→切 selective add（删 stash、按 claimed 文件 `git add`、串行锁）。自动触发条件：Trae 原生支持 worktree（对标 VS Code 1.107）后激活。

##### 关键设计决策

1. **worktree 内 commit 绕过 GitCommitGateway**：worktree 有独立 git index，session 独占整个 worktree，不存在共享冲突，无需 GitCommitGateway 的全局串行锁和门禁
2. **worktree 内 commit 用 `--no-verify`**：与 GitCommitGateway 自身行为一致（GitCommitGateway 也用 `--no-verify` 绕过 pre-commit hooks）；worktree commit 是隔离的中间工作，最终校验在 merge 回主分支时生效
3. **GATE-COMMIT-GW worktree 上下文放行**：检测 cwd 含 `.aidrafts/sess-` 时放行（纵深防御——即使 AI 不用 `--no-verify`，gate 也不阻断 worktree commit）
4. **文件同步（君子协定模式，2026-07-02）**：AI 的 Edit/Write 写到项目根（IDE 限制，无法改），worktree 内文件是创建时的旧版本。`session_worktree_commit` 在 `git add` 前自动 `shutil.copy2` 将 files 从项目根同步到 worktree，确保 stage 的是最新内容。AI 无需手动同步
5. **适用场景**：≥2 个并发 AI 对话时 MUST 走 worktree 模式；单 AI 对话可选
6. **claim/overlap 门禁保留为 P2**：主工作目录直接 commit 路径仍走 GitCommitGateway + SessionRequiredGate/ClaimRequiredGate/HeldOverlapGate（防搭便车提交）

##### 验收（已通过 2026-07-01 端到端测试）

- ✅ 两 session 各建 worktree，路径不同且目录存在
- ✅ session A 在 worktree 内 commit，主工作区无 A 的文件（物理隔离生效）
- ✅ session B 在 worktree 内 commit，A/B worktree 互不干扰
- ✅ merge session A 回主分支，主工作区出现 A 的文件
- ✅ abort session B，worktree 已清理，B 的修改被丢弃
- ✅ 主工作区最终只有 A 的改动（B 被丢弃）

#### FP-ISO.5 阻断层次重设计（修订 parallel_session_coordination_policy）

现有 policy §5.2「不新增阻断层」需修订为**四层阻断**：

| 层级 | 机制 | 模式A 强度 | 模式B 强度（当前） | 职责 | 状态 |
|------|------|:---:|:---:|------|:---:|
| **L0 物理隔离** | **session_worktree + WorktreeManager** | **最强** | **最强（治本，FP-ISO.4C）** | 从根本上让多 AI 不在同一工作区 | ✅ **已落地**（2026-07-01） |
| L1 编辑期声明 | SessionClaim + AGENTS.md 规则 | 不需要 | 软（AI 自觉）| 编辑前声明 claim，冲突可见 | ✅ 已落地（P2） |
| L2 提交期校验 | GitCommitGateway + SessionRequiredGate/ClaimRequiredGate/HeldOverlapGate | 不需要 | 硬（commit 拒绝）| 未 claim / 冲突文件拒绝提交 | ✅ 已落地（P2，主目录 commit 路径） |
| L3 串行化 | GitCommitGateway 全局锁 | 中 | 中 | commit 顺序化，后到者等锁 | ✅ 已落地 |
| L4 文件锁 | RULE-ZERO lock_files.py | 强 | 强 | LOCKED 后禁止写 | ✅ 已落地 |

**模式B 关键变更**（2026-07-01 FP-ISO.4C 更新）：原 FP-ISO.4B 设计把阻断责任推给 L1+L2（编辑期声明+提交期校验），但 41 案例分析表明这只覆盖 Mode C（7%）。FP-ISO.4C 将 L0（worktree 物理隔离）升级为**治本方案**——每 AI 对话独占 worktree，从根本上消除共享工作区冲突，覆盖 Mode A+B+D（75%+）。L1/L2 保留为 P2，防主工作目录直接 commit 的搭便车场景。

#### FP-ISO.6 未考虑到的问题讨论（治本方案完整性审查）

> 本节系统性讨论治本三件套可能引入的新问题，确保方案「非常治本」而非「治标换标」。

| # | 潜在问题 | 风险等级 | 缓解方案 | 责任组件 |
|---|---------|:---:|---------|---------|
| Q1 | **session_id 如何全局唯一分配**——多个并发 AI 如何获得不冲突的 session_id | 高 | spawn_agent.ps1 用 `sess-{PID}-{yyyyMMddHHmmss}` 生成；PID + 秒级时间戳在单机内唯一；WorktreeManager.create_session_worktree 内部检测重名则追加 `-{N}` 后缀 | spawn_agent.ps1 + WorktreeManager |
| Q2 | **worktree 泄漏**——AI 进程崩溃未 cleanup，worktree 残留占磁盘 | 高 | ① WorktreeManager 启动时扫描 `git worktree list --porcelain` 检测无主 worktree；② 超过 TTL（默认 24h）的 session worktree 自动 cleanup；③ spawn_agent.ps1 的 `finally` 块保证退出时清理；④ 新增 `worktree_gc.py` 守护进程定期回收 | WorktreeManager + worktree_gc.py（新增） |
| Q3 | **merge 冲突如何处理**——多 worktree 改了同一文件，merge 回主分支冲突 | 高 | ① merge_session_worktree 检测冲突时**不强制 merge**，保留 worktree 供人工解决；② 在 `.runtime/worktree_conflicts/{session_id}.json` 记录冲突文件清单；③ spawn_agent.ps1 输出冲突提示，AI 自行决定重试或人工介入；④ 不自动 abort，避免丢失工作 | WorktreeManager.merge_session_worktree |
| Q4 | **基础设施文件被多 worktree 同时依赖**——GitCommitGateway 本身、AGENTS.md、配置文件被所有 AI 读取，若某个 AI 在 worktree 内修改了它们再 merge，会污染其他 AI | 高 | ① 定义 `infrastructure_contracts.yaml` 列出契约文件（GitCommitGateway/WorktreeManager/AGENTS.md/configs/）；② 契约文件在 worktree 内**只读**，修改必须走主分支 + Owner 审批；③ pre-commit hook 检测契约文件被修改则拒绝；④ 这正是「[蓝图特有:撤回项澄清](#蓝图特有撤回项澄清)」中 ZephyrLock 跨进程升级的延伸应用 | infrastructure_contracts.yaml（新增）+ pre-commit hook |
| Q5 | **Windows 文件锁兼容性**——NTFS 锁 vs Unix advisory lock，pre-commit hook 在 Windows 是否生效 | 中 | ① git hooks 在 Windows 通过 `sh.exe` 执行，bash 语法兼容；② 文件锁用 `os.open(O_CREAT\|O_EXCL)` 原子创建，跨平台；③ 不依赖 fcntl（Unix only），改用原子文件创建；④ 已在 GitCommitGateway `_GlobalCommitLock` 验证 Windows 可行 | pre-commit hook + 现有 _GlobalCommitLock |
| Q6 | **worktree 数量上限与磁盘空间**——20 个并发 AI = 20 个 worktree，每个含完整工作树，磁盘占用 | 中 | ① git worktree 共享 `.git` 对象库，只增量存工作树文件，单 worktree 约 200-500MB；② 20 worktree ≈ 4-10GB，单机 64GB RAM + SSD 可承受；③ WorktreeManager 配置 `max_concurrent_worktrees=30` 硬上限；④ 超限时新 AI 排队等待 | WorktreeManager |
| Q7 | **与 StagingArea（§RULE-ZERO）的关系**——StagingArea 已支持「≥2 AI 并发提交草稿」，与 worktree 隔离是否重复 | 中 | ① StagingArea 是**提交层**隔离（草稿 → 正式 commit），worktree 是**工作区层**隔离（编辑期）；② 二者互补：worktree 防编辑覆盖，StagingArea 防提交冲突；③ worktree 内的 AI 仍可用 StagingArea 提交草稿；④ 不废弃 StagingArea | StagingArea + WorktreeManager 协同 |
| Q8 | **逃生通道被滥用**——`allow_main_branch=True` 和 `ZEPHYR_ALLOW_MAIN_BRANCH=1` 被频繁使用，回到裸跑状态 | 中 | ① GitCommitGateway 记录每次 `allow_main_branch=True` 的调用到审计日志；② 周报统计逃生通道使用次数，>5 次/周触发 Owner 审查；③ pre-commit hook 在逃生通道触发时输出醒目警告；④ 不硬禁用（保留灵活性），但可观测 | GitCommitGateway 审计 + AiAuditLogger |
| Q9 | **AI 不知道自己在 worktree 内**——AI 启动时未感知工作目录已切换，仍按主目录逻辑操作 | 中 | ① spawn_agent.ps1 在 worktree 创建后输出 `[session_id] worktree=<path>` 醒目标识；② AGENTS.md 新增「AI 启动时必读 worktree 标识」规则；③ WorktreeManager.get_current_worktree() 供 AI 主动查询；④ GitCommitGateway commit 时在 message 自动追加 `[session=<id>]` 前缀 | spawn_agent.ps1 + AGENTS.md |
| Q10 | **跨 worktree 的共享状态同步**——多个 AI 在各自 worktree 修改 depgraph (PostgreSQL) 等共享真源，如何避免数据库层冲突 | 高 | ① depgraph 修改必须通过 `apply_depgraph.py`（现有硬约束），该工具内部用 PostgreSQL 事务锁；② worktree 隔离的是文件系统，不是数据库；③ 共享真源（depgraph/YAML 规则）的并发由数据库事务保证，不依赖 worktree；④ worktree 内 AI 调 apply_depgraph.py 时走数据库串行，与文件隔离正交 | apply_depgraph.py（现有）+ PostgreSQL 事务 |
| Q11 | **蓝图/文档并发修改**——多 AI 同时改蓝图 YAML，merge 时冲突 | 中 | ① 蓝图修改属于「契约文件」（Q4），worktree 内只读；② 蓝图修改走主分支 + Owner 审批；③ 若必须并发改不同蓝图，按蓝图路径分区，每个 AI 只改分配的蓝图 | infrastructure_contracts.yaml + 路径分区 |
| Q12 | **回滚兼容性**——如果硬阻断导致 AI 无法工作，如何快速回滚 | 中 | ① 件1/件2/件3 都有逃生通道（allow_main_branch / ZEPHYR_ALLOW_MAIN_BRANCH）；② 回滚件1：GitCommitGateway 临时设 `allow_main_branch=True` 默认值；③ 回滚件3：删除 .git/hooks/pre-commit 即恢复；④ 回滚件2：直接在主目录启动 AI（不经过 spawn_agent.ps1） | 各组件逃生通道 |

**模式B（Trae IDE 适配）特有问题**：

| # | 潜在问题 | 风险等级 | 缓解方案 | 责任组件 |
|---|---------|:---:|---------|---------|
| Q13 | **AI 忘记 claim 就编辑**——软约束失守，AI 用 Trae Edit 工具直接改文件未先 session_claim_start | 高 | ① AGENTS.md 铁律「AI 对话第一步必调 session_claim_start」；② GitCommitGateway commit 时校验（件1改）——未 claim 文件 commit 被拒，AI 被迫补 claim 或放弃；③ SessionClaim helper 提供 `session_claim_add` 补充声明；④ 即使编辑期覆盖发生，commit 时也会被拦截，覆盖无法落地 | SessionClaim + GitCommitGateway + AGENTS.md |
| Q14 | **Trae 对话无内置 session_id**——如何区分同一 Trae 进程内的多个并发对话 | 高 | ① session_id = `sess-{trae_pid}-{dialog_index}-{timestamp}`，dialog_index 由 AI 自报（对话启动时 AI 自己计数）；② 备选：session_id = `sess-{uuid4}`，AI 启动时生成；③ SessionRegistry 检测重名则追加后缀；④ session_id 写入 `.runtime/sessions/{session_id}.json` 供其他 AI 可见 | SessionClaim helper |
| Q15 | **claim 列表预估错误**——AI 启动时无法预知所有要改的文件，导致改了未 claim 的文件 | 高 | ① session_claim_add 支持运行时追加声明，AI 改新文件前先 add；② GitCommitGateway commit 时若发现未 claim 文件，返回 UNCLAIMED_VIOLATION 并列出文件清单，AI 补 claim 后重试；③ AGENTS.md 规则「改新文件前必先 session_claim_add」；④ 提供 `session_claim_auto_add_from_diff` 工具，commit 前自动从 git diff 提取文件并补充 claim | SessionClaim + GitCommitGateway |
| Q16 | **长对话 claim 过期/会话切换**——AI 对话持续数小时，claim 一直持有导致其他 AI 阻塞 | 中 | ① SessionClaim 的 claim 设 TTL（默认 2h），超时自动释放；② AI 每次操作前调用 `session_claim_heartbeat` 续期；③ 对话结束（AI 主动声明完成）调用 `session_claim_end` 释放；④ TTL 过期后其他 AI 可 force_acquire（强制抢占），原 AI commit 时被拒并提示重新 claim | SessionClaim |
| Q17 | **编辑期两个 AI 同时改同文件**——覆盖已发生但未 commit，如何恢复 | 高 | ① GitCommitGateway commit 时校验 claim——后到者 commit 被拒（CLAIM_VIOLATION）；② 后到者须 `git checkout <冲突文件>` 丢弃自己的覆盖，重新基于最新基线编辑；③ SessionClaim 检测到冲突时提示「文件 X 被 session Y 持有，请等待或 git checkout 丢弃本地修改」；④ 这是模式B 的固有局限——编辑期覆盖无法 100% 防止，但 commit 校验保证覆盖不落地 | GitCommitGateway + SessionClaim |
| Q18 | **claim 粒度问题**——claim 单文件 vs 整个目录，粒度过细 AI 负担重，过粗阻塞多 | 中 | ① 默认单文件粒度（精确，不误伤）；② 支持 glob 模式 `session_claim_add("src/zephyr/governance/**/*.py")` 批量 claim；③ 契约文件（GitCommitGateway/WorktreeManager/AGENTS.md）强制单文件 claim + Owner 审批；④ 普通文件支持 glob 批量 claim 降低 AI 负担 | SessionClaim |

**结论**：18 个潜在问题均有缓解方案，无致命阻断。模式A（Q1-Q12）最高风险 Q1/Q2/Q3/Q4/Q10；模式B（Q13-Q18）最高风险 Q13/Q14/Q15/Q17——核心风险是「AI 不自觉 claim」（Q13）和「编辑期覆盖已发生」（Q17），均通过 GitCommitGateway commit 时硬校验兜底，保证覆盖无法落地。治本三件套（模式B）可行。

#### FP-ISO.7 实施计划与验收

> 模式A（命令行编排）实施计划见原表，当前不执行。**模式B（Trae 适配，当前采用）实施计划如下**：

| Phase | 件 | 变更文件 | 验收命令 | 状态 |
|-------|---|---------|---------|:---:|
| Phase 1 | 件1改 | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\git_commit_gateway.py` + `D:\ZephyrAlpha\src\zephyr\governance\commit_gates\held_overlap_gate.py` | `python -m pytest tests/governance/test_git_commit_gateway.py::test_claim_violation tests/governance/test_git_commit_gateway.py::test_unclaimed_violation -v` | 待施工 |
| Phase 1 | 件2改 | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\session_claim.py`（新建） | `python -m pytest tests/governance/test_session_claim.py -v` | 待施工 |
| Phase 2 | 件3改 | `D:\ZephyrAlpha\src\zephyr\governance\rule_bridge\worktree_manager.py`（复用，无改动） | `python -m pytest tests/governance/test_worktree_manager.py -v` | ✅ 已实现 |
| Phase 2 | — | `D:\ZephyrAlpha\AGENTS.md` | 新增「AI 对话启动第一步：session_claim_start」规则 | 待施工 |
| Phase 3 | Q4 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure_contracts.yaml`（新建）| 契约文件清单完整，claim 强制单文件 + Owner 审批 | 待施工 |
| Phase 3 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\policies\parallel_session_coordination_policy.md` | §3.2/§5.2 修订：held_files 从「预警不阻断」升级为「commit 时硬校验」 | 待施工 |

**模式B 完成标准**：
1. 两个并发 AI 对话 claim 同一文件，后到者 commit 返回 CLAIM_VIOLATION
2. AI 改未 claim 文件，commit 返回 UNCLAIMED_VIOLATION，列出文件清单
3. AI 调用 session_claim_start 后，SessionRegistry 有记录，其他 AI 可见
4. claim TTL 2h 过期后自动释放，其他 AI 可 force_acquire
5. 契约文件（GitCommitGateway/AGENTS.md 等）被 worktree 内 AI 修改时 commit 被拒
6. 逃生通道 `allow_unclaimed=True` 可观测，周报统计使用次数

#### FP-ISO.8 与业界实践对标

| 业界实践 | 来源 | ZephyrAlpha 对应 | 状态 |
|---------|------|----------------|:---:|
| Git Worktree 并行 Agent | GitHub Copilot App / Anthropic Agent Teams / Block | WorktreeManager（已实现）+ spawn_agent.ps1（待施工） | 🟡 能力有/未强制 |
| current_tasks/ 锁 + git push 拒绝 | Anthropic 16-agent C 编译器案例 | GitCommitGateway 全局锁（已实现）+ 硬阻断（待施工） | 🟡 锁有/未阻断主目录 |
| Write-time 状态校验 | STORM（arXiv:2605.20563, 2026-05）| HeldOverlapGate（已实现，commit 时检测）| 🟢 已落地（commit 级） |
| Contract Files 不可触碰 | Autonomous Agentic Research Swarm | infrastructure_contracts.yaml（待施工，Q4） | 🔴 待施工 |
| Resource Warden 文件锁 | HiveMind MCP | SessionRegistry held_files（已实现，仅预警）| 🟡 预警有/未阻断 |

---

## 附录 A：详细设计规范（从 specifications/auto_runtime_core/spec.md 迁移，2026-07-01）

> 以下内容原存于 specifications/auto_runtime_core/spec.md（MOD-SPEC-002），已收敛至本蓝图。
> 系统级全局清单（26包/31蓝图/三层AI工作分类）属于 SYS-MASTER 范畴，不在此重复。
> 系统级全局清单（§2 26包清单、§3 三层AI工作分类、§7 26包集成点）属于 SYS-MASTER 范畴，已省略。

### A.1 责任地图（原 §0.1：AutoRuntime Core 与其他编排器的职责边界）

#### Q0.1: AutoRuntime Core 是不是系统中唯一一个？有没有功能唯一责？

**是的。** AutoRuntime Core 是整个 ZephyrAlpha 项目中**唯一承担"系统大脑"职责的组件**。

```
ZephyrAlpha 责任地图：
┌──────────────────────────────────────────────────────┐
│ AutoRuntime Core ← 唯一的系统大脑                      │
│   职责：三层运行时编排、节律调度、健康监控、审计日志       │
│   职责：工作编排（WorkOrchestrator）                    │
│   职责：自动接入（ModuleOnboardingScanner）             │
│                                                      │
│ PipelineOrchestrator ← 管线内部编排（M1-M11）          │
│   职责：单条管线的阶段流转                              │
│                                                      │
│ AgentOrchestrator ← Agent 生命周期                    │
│   职责：单个 Agent 的创建/运行/销毁                     │
│                                                      │
│ DaemonRegistry ← 守护进程注册                          │
│   职责：进程级资源监控                                 │
│                                                      │
│ Gate Engine ← 安全闸门                                │
│   职责：策略准入                                       │
│                                                      │
│ TaskRepository ← 任务状态机（10状态）                   │
│   职责：任务 CRUD + 状态流转审计                        │
│                                                      │
│ WorkOrchestrator ← 工作编排（AutoRuntime 子系统）      │
│   职责：决定什么工作、什么时候、用什么模型、什么顺序       │
└──────────────────────────────────────────────────────┘
```

### A.2 业界实践对标表（原 §0.2：13项业界实践→ARC对应表）

#### Q0.2: 专业机构和氛围编程社区是怎么做的？

| 业界实践 | 来源 | 核心思想 | ARC 对应 |
|----------|------|----------|----------|
| **Agent Card + 能力发现** | Google A2A Protocol | AgentCard 声明能力、技能、端点 URL；自动发现 | CapabilityRegistry + CapabilityCard |
| **Orchestrator-Ledger** | Microsoft Magentic-One | 单一 Orchestrator 制定计划→分派→跟踪→反思 | AutoRuntimeCore + NightShiftQueue |
| **Supervisor Pattern** | LangGraph (LangChain) | 中央主管路由，Worker 子图隔离 | MAPE-K 调和循环 |
| **Level-Triggered Reconciliation** | K8s Controller Pattern | 只看"spec vs actual 的差距"；Idempotent | HealthMonitor + MAPE-K Loop |
| **Stop Gate** | Claude Code 45天实验 | 被动质量闸门——阻止 AI 什么都不做就退出 | StopGate |
| **Dream Cycle** | Claude Code 自主实验 | 归档→提取模式→遗忘细节→语义索引→commit | CircadianScheduler 夜间归档 |
| **Filesystem as Memory** | Claude Code / Vibe Coding | 认知外化到文件系统 | AiAuditLogger JSONL + NightShiftQueue |
| **Cursor Rules / AGENTS.md** | Cursor IDE 社区 | 持久化上下文给每次 AI 会话 | AGENTS.md + CapabilityRegistry |
| **MCP Tools/Resources/Prompts** | Anthropic MCP | 三类原语：Tools/Resources/Prompts | CapabilityCard.input/output_schema |
| **Finalizer** | K8s Operator Pattern | CR 删除前拦截，做清理工作 | Finalizer |
| **Self-Improving Agent** | 45天 Claude Code 实验 | 自我反思→学习教训→编码改进→提交→部署 | Feedback Loop |
| **Work Graph / DAG** | Airflow / Prefect / Temporal | 工作编排为 DAG，依赖管理+并行+重试 | WorkOrchestrator |
| **Solo Operator AIOS** | inonx.com 中央内核架构 | Agent 层 + Memory 层 + Governance 层 | AutoRuntime Core 整体 |

### A.3 WorkOrchestrator 完整代码骨架（原 §4）

#### 4.1 为什么需要工作编排？

300+ 文件、26 个包、上百个可自动化工作。如果没有编排系统：
- 工作之间有依赖（先入库→再分析→再激活），没有编排会乱序
- 同类工作可以并行（5 个嵌入任务同时跑），没有编排会串行
- 优先级不同（P0 合规检查 > P2 代码去重），没有编排会抢资源
- 工作量波动（夜班多、白天少），没有编排会浪费或过载

#### 4.2 设计理念

借鉴 **Airflow DAG** + **Temporal Workflow** + **K8s Job** 三种模式：

| 模式 | 来源 | 核心思想 | ARC 采用 |
|------|------|----------|----------|
| DAG 依赖图 | Airflow / Prefect | 工作定义为 DAG，节点=任务，边=依赖 | WorkDAG |
| 持久化执行 | Temporal | 工作流状态持久化，崩溃后可恢复 | TaskRepository 10 状态机 |
| 优先级抢占 | K8s Pod PriorityClass | P0 抢占 P2 资源 | PriorityPreemption |
| 并行槽位 | K8s Parallelism | 控制同时运行的任务数 | ConcurrencySlot |
| 工作窃取 | Go Work Stealing | 空闲层窃取其他层的任务 | LayerWorkStealing |

#### 4.3 WorkOrchestrator 架构

```python
class WorkOrchestrator:
    """工作编排子系统——决定什么工作、什么时候、用什么模型、什么顺序。

    借鉴:
      - Airflow: DAG 依赖图
      - Temporal: 持久化工作流
      - K8s Job: 优先级抢占 + 并行控制
    """

    def __init__(self, task_repo: TaskRepository, capability_registry: CapabilityRegistry)

    # ---- DAG 管理 ----
    def register_dag(self, dag: WorkDAG) -> None
    def get_dag(self, dag_id: str) -> WorkDAG | None
    def list_dags(self) -> list[WorkDAG]

    # ---- 执行 ----
    def submit(self, work: WorkItem) -> str              # 返回 task_id
    def submit_dag(self, dag_id: str, params: dict) -> str
    def cancel(self, task_id: str) -> bool

    # ---- 调度 ----
    def schedule_next(self) -> list[WorkItem]             # 返回可执行的任务
    def resolve_layer(self, work: WorkItem) -> str        # 决定跑在哪一层
    def resolve_priority(self, work: WorkItem) -> str     # P0/P1/P2

    # ---- 并行控制 ----
    def acquire_slot(self, layer: str) -> bool            # 获取执行槽位
    def release_slot(self, layer: str) -> None            # 释放槽位
    def available_slots(self, layer: str) -> int

    # ---- 状态 ----
    def status(self, task_id: str) -> TaskStatus
    def pending_count(self) -> dict[str, int]             # 按层统计
    def running_count(self) -> dict[str, int]
```

```python
class WorkDAG(BaseModel):
    """工作 DAG——定义工作之间的依赖关系。"""
    dag_id: str
    name: str
    description: str
    nodes: list[WorkNode]
    edges: list[WorkEdge]
    default_layer: str                    # trae / local / api
    default_priority: str                 # P0 / P1 / P2
    max_parallelism: int = 3
    retry_on_failure: int = 2
    timeout_minutes: int = 60

class WorkNode(BaseModel):
    """DAG 节点——一个可执行的工作单元。"""
    node_id: str
    capability_id: str                    # 对应 CapabilityCard.capability_id
    work_type: str                        # embedding / inference / search / ...
    params: dict                          # 输入参数
    layer_override: str | None = None     # 强制指定层
    priority_override: str | None = None  # 强制指定优先级

class WorkEdge(BaseModel):
    """DAG 边——节点间依赖。"""
    from_node: str
    to_node: str
    condition: str = "success"            # success / failure / always
```

```python
class WorkItem(BaseModel):
    """工作项——提交到编排系统的最小单元。"""
    item_id: str
    dag_id: str | None                    # 所属 DAG（独立任务为 None）
    node_id: str | None                   # 所属节点
    capability_id: str
    work_type: str
    params: dict
    layer: str                            # trae / local / api
    priority: str                         # P0 / P1 / P2
    status: str                           # PENDING / READY / RUNNING / COMPLETED / FAILED / ...
    depends_on: list[str]                 # 依赖的 item_id 列表
    created_at: str
    scheduled_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    result: dict | None = None
    error: str | None = None
```

#### 4.4 与现有 TaskRepository / TaskQueue / TaskScheduler 的衔接

```
                    WorkOrchestrator
                    （工作编排子系统）
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    submit()       schedule_next()   resolve_layer()
          │              │              │
          ▼              ▼              ▼
    TaskRepository   TaskScheduler   _resolve_execution_mode()
    (10状态机)       (定时调度)       (三层决策)
          │              │              │
          └──────┬───────┘              │
                 ▼                      │
            TaskQueue                   │
            (后台轮询自动分发)            │
                 │                      │
          ┌──────┴──────┐               │
          ▼             ▼               ▼
     L1(Trae)     L2(Local)       L3(API)
```

**边界清晰**：

| 组件 | 职责 | 不做什么 |
|------|------|----------|
| **WorkOrchestrator** | 决定什么工作、什么顺序、什么层、什么优先级 | 不管理任务状态机 |
| **TaskRepository** | 管理 10 状态机（PENDING→IN_PROGRESS→COMPLETED→VERIFIED） | 不决定跑哪层 |
| **TaskQueue** | 后台轮询 READY 任务，自动 dispatch | 不决定优先级 |
| **TaskScheduler** | 定时调度（assigned_model/assigned_pipeline） | 不管理依赖 |
| **CircadianScheduler** | 生物钟定时触发 | 不管理工作依赖图 |

**衔接流程**：
```
1. WorkOrchestrator.submit(work_item)
   → 写入 TaskRepository.create()（状态=PENDING）
   → 解析依赖，依赖满足 → 状态=READY

2. TaskQueue 后台轮询 READY 任务
   → WorkOrchestrator.resolve_layer() 决定跑哪层
   → WorkOrchestrator.acquire_slot() 获取槽位
   → dispatch 到对应层执行

3. 执行完成
   → TaskRepository.update(status=COMPLETED)
   → WorkOrchestrator 检查下游依赖是否满足
   → 满足 → 下游任务状态→READY

4. CircadianScheduler 定时触发
   → WorkOrchestrator.submit_dag() 注入预定义 DAG
   → 例如 00:00 注入 "daily-dream-cycle" DAG
```

#### 4.5 预定义工作 DAG

| DAG ID | 触发方式 | 节点 | 层级 |
|--------|----------|------|------|
| `daily_dream_cycle` | Circadian 00:00 | archive→extract→forget→index→commit | L2→L3→L2→L2→L2 |
| `daily_health_check` | Circadian 07:00 | probe_all→reconcile→report | L2→L2→L2 |
| `daily_code_dedup` | Circadian 02:00 | scan→match→prioritize→merge | L2→L2→L2→L2 |
| `daily_kb_maintenance` | Circadian 04:00 | integrity→verify→freeze→dedup | L2→L2→L2→L2 |
| `daily_compliance` | Circadian 22:00 | matrix_check→sbom→supply_chain | L3→L3→L3 |
| `daily_feedback_loop` | Circadian 03:00 | analyze_pending→generate_proposals→apply | L2→L2→L2 |
| `pipeline_full_run` | 手动/事件 | M1→M2→M3→...→M11 | L1+L2+L3 |
| `kb_ingest_pipeline` | 事件（新数据） | triage→extract→analyze→ingest→activate | L2→L2→L2→L2→L2 |
| `security_scan` | 事件（新代码） | injection_check→red_team→sandbox→report | L2→L3→L2→L2 |
| `model_drift_check` | Circadian 12:00 | collect_metrics→compare_baseline→alert_if_drift | L2→L2→L2 |

#### 4.6 并行控制

```
并行槽位（按层分配）：
┌──────────────────────────────────────────┐
│ L1 (Trae)  │ 槽位: 1（人在环，串行）      │
│ L2 (Local) │ 槽位: 3（Ollama 可并行3推理） │
│ L3 (API)   │ 槽位: 2（成本控制，最多2并发） │
└──────────────────────────────────────────┘

优先级抢占：
  P0（合规/安全）→ 抢占 P2 槽位
  P1（运维）     → 正常排队
  P2（优化/清理） → 空闲时执行

层间工作窃取：
  L2 空闲 + L3 排队 → L2 尝试处理（如果能力匹配）
  L3 空闲 + L2 排队 → 不窃取（成本原因）
```

### A.4 自动接入子系统代码骨架（原 §5）

#### 5.1 为什么需要自动接入？

当前设计是"被动等注册"——模块启动时 self-register。但问题是：
- **新模块创建时**，开发者/AI 可能忘记注册到 CapabilityRegistry → 变成孤儿
- **现有模块**中，大量模块还没接入大脑 → 孤儿率很高
- **大脑不知道自己不知道什么**——没有主动扫描，就不知道遗漏了什么

需要一套**主动扫描+自动判断+自动接入**的子系统。

#### 5.2 设计理念

借鉴 **K8s Controller Manager**（主动调和）+ **Claude Code Self-Improving Agent**（自我发现+自我完善）：

| 模式 | 来源 | 核心思想 | ARC 采用 |
|------|------|----------|----------|
| 主动扫描 | K8s Controller Manager | 不等事件，定期全量扫描 | ModuleOnboardingScanner |
| 智能判断 | Claude Code Self-Improving | 临时启动高级模型分析 | AutoIntegrator (L3 临时激活) |
| 孤儿检测 | K8s Orphan Pod Detection | 发现不在管理范围内的资源 | OrphanDetector |
| 自动注册 | K8s Auto-Registration | 发现即注册 | AutoIntegrator.generate_card() |
| 终极目标驱动 | Self-Improving Agent | 知道自己的目标，主动向目标靠近 | reconcile() 检查孤儿率 |

#### 5.3 三组件架构

```
┌─────────────────────────────────────────────────────────────┐
│                 自动接入子系统                                 │
│                                                             │
│  ┌──────────────────────┐                                   │
│  │ ModuleOnboardingScanner │ ← 主动扫描：发现新模块/蓝图     │
│  │   scan_filesystem()    │                                 │
│  │   scan_blueprints()    │                                 │
│  │   diff_registered()    │ ← 对比 CapabilityRegistry       │
│  └──────────┬───────────┘                                   │
│             │ 发现未注册模块                                  │
│             ▼                                               │
│  ┌──────────────────────┐                                   │
│  │   AutoIntegrator       │ ← 智能判断：临时启动 L3 分析     │
│  │   analyze_module()     │   "这个模块要不要接入？"         │
│  │   should_integrate()   │   "接入哪一层？"                 │
│  │   generate_card()      │   "怎么接入？"                   │
│  │   assign_work_type()   │   "分配什么工作类型？"            │
│  └──────────┬───────────┘                                   │
│             │ 生成 CapabilityCard + IntegrationPoint          │
│             ▼                                               │
│  ┌──────────────────────┐                                   │
│  │   OrphanDetector       │ ← 孤儿检测：持续监控孤儿率        │
│  │   compute_orphan_rate()│                                 │
│  │   find_orphans()       │ ← 找出所有未接入模块             │
│  │   prioritize_orphans() │ ← 按优先级排序                   │
│  │   report()             │ ← 生成孤儿报告                   │
│  └──────────────────────┘                                   │
└─────────────────────────────────────────────────────────────┘
```

#### 5.4 ModuleOnboardingScanner

```python
class ModuleOnboardingScanner:
    """模块接入扫描器——主动发现未注册模块。

    借鉴:
      - K8s Controller Manager: 主动调和，不等事件
      - K8s Discovery: 自动发现集群中的资源
    """

    def scan_filesystem(self) -> list[ModuleDiscovery]
    def scan_blueprints(self) -> list[BlueprintDiscovery]
    def diff_registered(self) -> list[UnregisteredModule]
    def watch_for_changes(self) -> None              # 文件系统 watcher

@dataclass
class ModuleDiscovery:
    """发现的模块。"""
    module_path: str               # src/zephyr/governance/cost_router.py
    module_name: str               # cost_router
    package: str                   # governance
    has_class: bool                # 是否定义了类
    class_names: list[str]         # 类名列表
    has_public_functions: bool     # 是否有公开函数
    function_names: list[str]      # 函数名列表
    has_blueprint: bool            # 对应蓝图是否存在
    blueprint_path: str | None     # 蓝图路径
    docstring: str | None          # 模块 docstring
    imports: list[str]             # 依赖的其他模块

@dataclass
class UnregisteredModule:
    """未注册的模块——孤儿。"""
    discovery: ModuleDiscovery
    reason: str                    # 为什么没注册（新创建/遗漏/不支持）
    priority: str                  # P0/P1/P2 接入优先级
    suggested_layer: str           # 建议接入哪一层
```

**扫描策略**：
```
1. 全量扫描（CircadianScheduler 04:00 触发）
   - 遍历 src/zephyr/ 下所有 .py 文件
   - 遍历 architecture_model/ 下所有 .yaml 文件
   - 对比 CapabilityRegistry.list_all()
   - 输出 UnregisteredModule 列表

2. 增量扫描（文件系统 watcher 实时触发）
   - 监听 src/zephyr/ 目录的 create/modify 事件
   - 新文件 → 立即触发 ModuleOnboardingScanner
   - 输出单个 UnregisteredModule

3. 蓝图扫描（CircadianScheduler 07:00 触发）
   - 遍历 architecture_model/ 下所有 .yaml
   - 检查蓝图定义的模块是否都有对应 CapabilityCard
   - 输出蓝图→代码→注册的三方对齐报告
```

#### 5.5 AutoIntegrator

```python
class AutoIntegrator:
    """自动接入器——临时启动高级模型分析是否接入。

    借鉴:
      - Claude Code Self-Improving: 临时启动强推理分析
      - K8s Admission Controller: 接入前审查
    """

    def analyze_module(self, module: UnregisteredModule) -> IntegrationAnalysis
    def should_integrate(self, analysis: IntegrationAnalysis) -> bool
    def generate_card(self, analysis: IntegrationAnalysis) -> CapabilityCard
    def assign_work_type(self, analysis: IntegrationAnalysis) -> str
    def auto_register(self, card: CapabilityCard) -> bool

@dataclass
class IntegrationAnalysis:
    """接入分析结果。"""
    module_path: str
    should_integrate: bool          # 是否应该接入
    reason: str                     # 为什么（不）接入
    suggested_layer: str            # trae / local / api
    suggested_priority: str         # P0 / P1 / P2
    suggested_work_types: list[str] # 建议的工作类型
    suggested_capability_card: CapabilityCard | None
    confidence: float               # 分析置信度 0.0-1.0
    model_used: str                 # 分析使用的模型（通常是 L3 API）
```

**接入决策流程**：
```
1. 发现未注册模块 → AutoIntegrator.analyze_module()

2. 临时启动 L3 高级模型（DeepSeek V4 Pro / Claude）分析：
   - 读取模块源码 + docstring + imports
   - 读取对应蓝图 YAML（如果有）
   - 判断：
     a. 这个模块是否应该接入大脑？（纯工具函数可能不需要）
     b. 接入哪一层？（Trae/Local/API）
     c. 分配什么工作类型？
     d. 生成 CapabilityCard 草稿

3. 如果 confidence >= 0.8 → 自动注册到 CapabilityRegistry
4. 如果 confidence < 0.8 → 写入 NightShiftQueue，等人类裁定
5. 无论哪种结果 → AiAuditLogger 记录分析过程
```

**关键设计：临时启动 L3**

```
正常情况：L3 只在夜班运行（省钱）
接入分析时：临时启动 L3 API 做一次深度推理
           ↓
  分析完毕后 L3 回到待机状态
           ↓
  成本控制：每天最多 10 次临时 L3 激活（可配置）
```

#### 5.6 OrphanDetector

```python
class OrphanDetector:
    """孤儿检测器——持续监控孤儿率，驱动大脑向终极目标靠近。

    借鉴:
      - K8s Orphan Pod Detection
      - Self-Improving Agent: 知道目标，主动靠近
    """

    def compute_orphan_rate(self) -> float          # 0.0-1.0，目标=0.0
    def find_orphans(self) -> list[UnregisteredModule]
    def prioritize_orphans(self, orphans: list) -> list  # 按优先级排序
    def report(self) -> OrphanReport
    def is_goal_met(self) -> bool                   # 孤儿率 == 0.0?

@dataclass
class OrphanReport:
    """孤儿报告。"""
    total_modules: int
    registered_modules: int
    orphan_modules: int
    orphan_rate: float
    orphans_by_priority: dict[str, int]             # P0: 3, P1: 12, P2: 45
    orphans_by_package: dict[str, int]              # governance: 30, shared: 15, ...
    top_priority_orphans: list[UnregisteredModule]  # 最应该先接入的
    goal_gap: float                                 # 1.0 - orphan_rate，距离目标的差距
```

**与调和循环的衔接**：
```
HealthMonitor.reconcile() 每次调和时：
  ① 原有：probe 所有已注册组件 → spec vs actual
  ② 新增：OrphanDetector.compute_orphan_rate()
  ③ 新增：如果孤儿率 > 0 → 触发 ModuleOnboardingScanner.scan_filesystem()
  ④ 新增：发现孤儿 → AutoIntegrator.analyze_module()
  ⑤ 新增：分析结果 → 自动注册 或 登记表
  ⑥ 新增：ReconciliationReport 包含孤儿率指标
```

#### 5.7 新模块创建时的自动接入

**当任何 AI 或人类创建新模块时**，自动触发接入流程：

```
新 .py 文件创建
  │
  ├─ 方式1: 文件系统 watcher 检测到新文件
  │         → ModuleOnboardingScanner.scan_filesystem()
  │         → 发现 UnregisteredModule
  │         → AutoIntegrator.analyze_module()
  │
  ├─ 方式2: 新蓝图 YAML 创建
  │         → ModuleOnboardingScanner.scan_blueprints()
  │         → 发现蓝图定义的模块未注册
  │         → AutoIntegrator.analyze_module()
  │
  └─ 方式3: AGENTS.md 中写明规则
            "所有新模块必须注册到 CapabilityRegistry"
            → AI 创建新模块时，读到这条规则，主动 register()
```

#### 5.8 扫描现存所有模块的遗漏

**首次全量扫描**（Boot 时 + CircadianScheduler 04:00 定期）：

```
1. 遍历 src/zephyr/ 下所有 .py 文件 → 300+ 个文件
2. 遍历 architecture_model/ 下所有 .yaml → 31 个蓝图
3. 对比 CapabilityRegistry.list_all() → 当前注册数
4. 差集 = 未注册模块 = 孤儿
5. 按 priority 排序：
   - P0: 有蓝图定义但未注册的（蓝图说应该有，但没有）
   - P1: 有公开 API 的模块（class + public functions）
   - P2: 纯内部工具函数（可能不需要注册）
6. P0 立即触发 AutoIntegrator
7. P1 排队等待
8. P2 标记为"可选接入"
```

### A.5 AutoRuntimeCore 类完整方法签名 + 20步 Boot Sequence（原 §6.2-6.3）

#### 6.2 AutoRuntime Core（`auto_runtime_core.py`）

```python
class AutoRuntimeCore:
    """三层运行时运营中心——ZephyrAlpha 系统大脑。"""

    def __init__(self, config: RuntimeConfig)

    # ---- 生命周期 ----
    def boot(self) -> BootReport
    def shutdown(self) -> None

    # ---- 调和 ----
    def reconcile(self) -> ReconciliationReport
    def health(self) -> HealthSnapshot

    # ---- 状态 ----
    def status_panel(self) -> str
    def status_json(self) -> dict

    # ---- 任务 ----
    def dispatch_task(self, task: TaskCard) -> DispatchResult
    def get_night_shift_queue(self) -> list[NightShiftAmbiguityLogEntry]
    def resolve_night_shift(self, entry_id: str, decision: str, notes: str) -> None

    # ---- 工作编排 ----
    @property
    def work_orchestrator(self) -> WorkOrchestrator
    def submit_work(self, work: WorkItem) -> str
    def submit_dag(self, dag_id: str, params: dict) -> str

    # ---- 注册 ----
    @property
    def capability_registry(self) -> CapabilityRegistry
    @property
    def integration_registry(self) -> IntegrationRegistry

    # ---- 闸门 ----
    @property
    def stop_gate(self) -> StopGate
    def can_stop(self) -> bool
```

#### 6.3 Lifecycle Manager

Boot Sequence（20步，含 WorkOrchestrator 初始化）：
```
01-13. 同 v3.0.0（配置→审计→注册→模型预热→调度器）
14. WorkOrchestrator.initialize(task_repo, capability_registry)  ← 新增
15. WorkOrchestrator.load_dags(data/work_dags/)                  ← 新增
16. CircadianScheduler().start()
17. HealthMonitor().start()
18. StatusDashboard().start()
19. IntegrationRegistry.validate_all()
20. 输出 BootReport → 进入主调和循环
```

### A.6 防孤儿机制（9处注册清单 + 零孤儿保证）（原 §8）

#### 8.1 注册清单（全部 9 处）

| 注册位置 | 内容 | 触发时机 |
|----------|------|----------|
| **AGENTS.md** | 项目宪法 | 手动维护 |
| CapabilityRegistry | CapabilityCard | 组件启动时自动 |
| IntegrationRegistry | IntegrationPoint | 系统 boot 时 |
| DaemonRegistry | Daemon 心跳 | 持续 |
| AiAuditLogger | 每次 AI 行为 | 每次调用 |
| NightShiftQueue | 不确定登记 | 遇到时追加 |
| ContractRegistry | 接口契约 CT-* | 启动时 |
| **WorkOrchestrator** | **WorkDAG** | **boot 时加载** |
| **OrphanDetector** | **OrphanReport** | **调和时自动** |

#### 8.2 零孤儿保证

- **不注册 = 不存在**
- **不编排 = 不执行**（WorkOrchestrator 只执行注册过的 DAG）
- **不扫描 = 不发现**（ModuleOnboardingScanner 主动扫描，不等注册）
- CapabilityCard 校验拒绝错误注册
- HealthMonitor 持续 probe
- AiAuditLogger 全量记录
- AGENTS.md 第一入口

### A.7 全自动优化8阶表（原 §9）

同 v4.0.0 §8，新增：

| 阶 | 优化项 | 实现组件 | 受益 |
|----|--------|----------|------|
| 一阶 | **自动扫描** | ModuleOnboardingScanner | 主动发现新模块 |
| 二阶 | **智能接入** | AutoIntegrator (L3 临时激活) | 自动判断+自动注册 |
| 二阶 | **孤儿检测** | OrphanDetector | 持续监控孤儿率 |
| 三阶 | **终极目标驱动** | reconcile() 检查孤儿率 | 大脑主动向目标靠近 |

| 阶 | 优化项 | 实现组件 | 受益 |
|----|--------|----------|------|
| 一阶 | **工作编排** | WorkOrchestrator | 自动决定什么工作、什么顺序、什么层 |
| 一阶 | **DAG 依赖管理** | WorkDAG | 工作间依赖自动解析 |
| 一阶 | **并行控制** | ConcurrencySlot | 同层多任务并行 |
| 二阶 | **优先级抢占** | PriorityPreemption | P0 抢占 P2 |
| 三阶 | **层间工作窃取** | LayerWorkStealing | L2 空闲时帮 L3 |

### A.8 验收标准（22条）（原 §10）

| # | 标准 |
|---|------|
| 1 | `python -m zephyr.runtime` 一键启动，自动 warmup 全部组件 |
| 2 | 开机自启：Windows Service 注册成功 |
| 3 | 启动后 TUI 面板实时显示三层状态 + 组件 + 节律 + 工作编排状态 |
| 4 | 内置节律运行：时间到了自动切换层级、触发任务 |
| 5 | DEMO 7 任务 + tasks/ JSON 投递任务全部自动分派 |
| 6 | 所有 AI 行为写入 `data/audit_logs/` JSONL |
| 7 | CapabilityRegistry 中注册了所有已实现组件 |
| 8 | IntegrationRegistry 验证全部 26 包集成点 |
| 9 | Ctrl+C → Finalizer → Stop Gate → 优雅关闭 |
| 10 | 资源 > 80% 自动降级 |
| 11 | Dream Cycle 每天至少触发一次 |
| 12 | Stop Gate 阻止空转退出 |
| 13 | 与 b_execution_model.yaml 100% 对齐 |
| 14 | `ruff check --select F` 零新增 |
| 15 | AGENTS.md 存在且完整 |
| 16 | Feedback Loop 生成至少一个进化提案 |
| 17 | **WorkOrchestrator 加载 10 个预定义 DAG** |
| 18 | **DAG 依赖自动解析：上游完成→下游 READY** |
| 19 | **并行控制：L2 同时跑 3 个嵌入任务** |
| 20 | **优先级抢占：P0 任务抢占 P2 槽位** |
| 21 | **ModuleOnboardingScanner 全量扫描发现孤儿** |
| 22 | **AutoIntegrator 临时启动 L3 分析后自动注册或登记** |

### A.9 与现有蓝图对应表（16个ARC组件→蓝图YAML映射）（原 §11）

| ARC 组件 | 对应蓝图 YAML | 关系 |
|----------|---------------|------|
| AutoRuntimeCore | `b_execution_model.yaml` | 运行时实现 |
| CircadianScheduler | `b_execution_model.yaml` runtime_schedule | 作息落地 |
| CapabilityRegistry | 新建（桥接 to `b_bridge.yaml`） | 能力注册 |
| IntegrationRegistry | 新建（桥接 to 所有 b_*.yaml） | 集成注册 |
| AiAuditLogger | 新建 | 审计日志 |
| HealthMonitor | `DaemonRegistry` 扩展 | 自愈 |
| StopGate | 新建 | 质量闸门 |
| DreamCycle | 新建 | 知识固化 |
| FeedbackLoop | `b_feedback_loop.yaml` | 自演化 |
| Finalizer | 新建 | 优雅清理 |
| AGENTS.md | 新建 | 项目宪法 |
| **WorkOrchestrator** | **新建** | **工作编排** |
| **WorkDAG** | **新建** | **DAG 依赖图** |
| **ModuleOnboardingScanner** | **新建** | **自动扫描** |
| **AutoIntegrator** | **新建** | **自动接入** |
| **OrphanDetector** | **新建** | **孤儿检测** |
