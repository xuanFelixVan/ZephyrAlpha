---
module_id: MOD-INF-016
submodule_path: src/zephyr/shared
title: "Shared+Core 蓝图"
doc_type: blueprint
status: Active
version: "0.19.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
last_updated: "2026-06-23"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: design_only
actual_disk_path: "src/zephyr/shared/"
belongs_to: "MOD-MASTER_BLUEPRINT"
summary: "跨层共享基础设施，115+已跟踪文件，Shared 59 + Core 60 .py + ProcessLifecycleGateway (已实现) + F20 监控系统恢复(16文件: health/longevity/metrics/observability/quality/sla/contracts) + F21 自动化集成(EventBus合并+自动启动+事件订阅+分钟级监控+Finalizer自动关闭)"
tags: [shared, core, cross-layer, contracts, ssot-guard, event-bus, blueprint-decomposer, infrastructure, v0.20.0, f21-automation]
priority: P0
runtime_plane: hot
codification_level: L2
last_verified: "2026-05-14"
codification_at: "2026-05-15"
generation: 2
functional_domain: operations
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
references: []
depends_on:
  - {target: "architecture_model/layers/b_shared.yaml", at: "全篇", why: "Shared YAML SSoT"}
  - {target: "architecture_model/layers/b_core.yaml", at: "全篇", why: "Core YAML SSoT"}
  - {target: "MOD-CONTEXT_ENGINE", at: "blueprint.md", why: "Context Engine 消费 Shared 模型"}
  - {target: "MOD-INF-003", at: "blueprint.md", why: "Script System 消费 Shared ProcessPoolManager"}
  - {target: "MOD-GATE_ENGINE", at: "blueprint.md", why: "Gate Engine 消费 Shared AsyncObserver"}
  - {target: "MOD-INF-009", at: "blueprint.md", why: "Pipeline 消费 Shared 分层限流+PriorityLock"}
---

# Shared Core 蓝图 — 跨层共享基础设施：事件总线/配置/缓存/限流/契约

> module_id: MOD-INF-016 | version: 0.18.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/shared/ + src/zephyr/core/ | generation: 2 | construction_progress: completed
>
> **SSoT 声明**: Shared canon SSoT 为 [b_shared.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_shared.yaml)；Core canon SSoT 为 [b_core.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_core.yaml)。Shared + Core 合并为单一蓝图（均为跨层基础设施，体积较小）。

**负向责任**：不涉及应用层业务逻辑 / GUI 渲染 / 外部 API 集成 / 数据库 Schema 设计（→ MOD-DATABASE）。

**触发**：EventBus 集成 → §2.2；配置管理 → §2.6；缓存策略 → Phase 8；限流配置 → Phase 8；契约定义 → §2.1。

## 概述

本蓝图描述 Shared Core——ZephyrAlpha 跨层共享基础设施层，为所有模块提供 EventBus、配置中心、缓存层、限流器、幂等守卫、契约总线等 18 项基础组件。通过 daemon_registry 统一管理守护线程生命周期。当前 115+ 文件覆盖 shared/ 和 core/ 两目录，目标支撑 1,500 模块规模。被 AutoRuntime Core（MOD-INF-035）和资源优化引擎（MOD-RESOURCE_OPTIMIZATION_ENGINE）等上游消费。

> **标准锚点**：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md) | [压缩工作流标准](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml) | [code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)

---

## §0 代码对齐验证

> ⚠️ 防止 construction_progress 与实际代码不符。
> 每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§15）。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> 列出蓝图描述的**所有代码文件**。此清单 = 代码目录下的实际文件列表。
> AI 施工者按此清单创建文件，审计者按此清单验证对齐。
> **存在性状态受控词表**：`未实现` / `已实现` / `已阻塞` / `已废弃`
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-016`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:---:|-------------------|
| 1 | (215 files) | §2 | 跨层共享基础设施 | 已实现 | |
| 2 | core/ (60 files) | §3 | 核心模块 | 已实现 | |
| 3 | infra/process_lifecycle_gateway.py | §2.10 | 进程生命周期统一入口网关 | 已实现 | |
| 4 | health.py + healthcheck_service.py | §2.7 | 健康监控服务(F20恢复) | 已实现 | |
| 5 | longevity_monitor.py | §2.7 | 长寿监控(F20恢复) | 已实现 | |
| 6 | metrics.py | §2.8 | 指标收集(F20恢复) | 已实现 | |
| 7 | health_discovery.py + tracing.py + cli_summary.py | §2.7 | 可观测性辅助(F20恢复,原observability_02/归位shared/根) | 已实现 | |
| 8 | (原shared_services/observability_02/ 已删除-stale路径) | §2.7 | — | 已废弃 | |
| 9 | quality/quality_monitor.py | §2.7 | 质量监控代理(F20恢复) | 已实现 | |
| 10 | sla/sla_monitor.py | §2.7 | SLA监控代理(F20恢复) | 已实现 | |
| 11 | maintenance/autonomy_monitor.py | §2.7 | 自治监控(F20恢复) | 已实现 | |
| 12 | contracts/telemetry_emitter.py | §2.1 | 遥测契约(CTR-P1-013 codegen) | 已实现 | |
| 13 | contracts/market/factor_monitor_report.py | §2.1 | 因子监控报告契约(F20恢复) | 已实现 | |
| 14 | contracts/risk/ (risk_dashboard_snapshot/risk_metrics) | §2.1 | 风险监控契约(F20恢复) | 已实现 | |

### §0.2 对齐验证矩阵

> 每次蓝图版本升级后填写。验证 construction_progress 是否与代码实际状态一致。

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/shared/ src/zephyr/core/` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| actual_disk_path 与 §11 产出物路径一致 | 路径核对 | ☐ |

### §0.3 版本-代码映射

> 记录蓝图版本与代码实现的对应关系。

| 蓝图版本 | 代码覆盖范围 | 状态 |
|---------|------------|:---:|
| v0.17.0 | 115 已跟踪文件 + 109 shared子目录 + 53 core子目录 | ✅ |
| v0.19.0 | F20 监控系统恢复: 16个shared/监控文件补全11字段头部 + shim目标路径修复 | ✅ |

---

## §1 设计背景与目标

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-016 |
| 涵盖 | Shared (`src/zephyr/shared/`) + Core (`src/zephyr/core/`) |
| 文件数 | Shared 49 文件(Phase 0-10 已审计) + 10 early-bird(Phase 11-14) + Core 2 文件 = 61 已跟踪文件（另有 ~43 orphan 待分类） |
| 核心职责 | 提供所有系统共用的数据模型、基础设施、工具函数 |

### 运行场景约束

| 约束 | 影响 |
|------|------|
| 单机部署：i7-12700KF（12C20T）/ 64GB RAM / RTX 3090 24GB / 1TB NVMe SSD | 所有容量设计基于单机，不支持水平扩展 |
| Python 3.12+ + Pydantic V2 | 所有数据模型必须继承 BaseModel，禁止 dataclass |
| SQLite 单写者锁 | 写入串行化，需 WriteBatcher 批量合并（暂缓待 L 级 5000+脚本） |
| 100 AI 并发稳态 | 共享组件必须支持 100 并发读写 |
| 1,500 模块 / 10,000 脚本目标容量 | 注册表和索引必须支持 O(1) 或 O(log N) 查询 |

---

## 2. Shared 模块（9 子模块, 59 文件——49 Phase 0-10 + 10 Phase 11-14 early-bird）

## §2 子模块与职责

| 序号 | 子模块 | 职责 | 文件数 |
|------|--------|------|--------|
| §2.1 | 数据契约（contracts） | 跨层 Pydantic models SSoT + 输入/输出契约装饰器 | 5 |
| §2.2 | 事件总线（events） | 异步 Observer Pub/Sub + 事件体 schema + 死信队列(DLQ) | 6 |
| §2.3 | 核心能力（core） | Task核心模型 (31字段基座) + BlueprintDecomposer | 2 |
| §2.4 | 韧性组件（resilience） | CircuitBreaker + Retry + FallbackChain | 4 |
| §2.5 | 生命周期（lifecycle） | 模块 start/stop/health_check 钩子 + 优雅关闭 | 3 |
| §2.6 | 配置管理（config） | YAML 配置加载 + 校验 | 3 |
| §2.7 | 通用工具（utilities） | 类型别名 + diff/patch + 文件操作 + 常量 + FeatureFlag + 能力 + API索引 + 错误层次 + 枚举 + 日志 + shared_quickref + 测试夹具 + Schema迁移 + 废弃策略 + 版本协商 + 健康聚合 | 24 |
| §2.8 | 生产基础设施（production） | 序列化 + API Client + Secrets + 缓存 + 速率限制 + 幂等性 + 上下文 + Metrics + 分页 + 时间工具 + 环境检测 + 分布式锁 + Outbox + Schema Registry | 14 |
| §2.9 | AI 专属基础设施（planned） | AI 成本预算与熔断 + Token/上下文预算管理 + Evals 框架 + Durable Execution + 后处理管道 + Session 审计轨迹 + Multi-Agent 编排 + Skill/Prompt 注册表 + Model Provider 抽象 + 上下文压缩 + 输出质量评分 + 宪法自更新 + DI 容器 + 代码沙箱 + 配置覆盖链 | 0（待施工） |
| §2.10 | 进程生命周期网关（shared-infra） | ProcessLifecycleGateway — 统一进程创建入口 + idle_timeout 空闲回收 + DaemonRegistry 自动注册 + Gate 防绕过 | 2（已实现） |

### 2.1 shared-contracts（跨层数据契约）

> → 详见 **MOD-013** `contracts_blueprint.md`（跨层数据契约 SSoT——11 子域 64 文件，含 instrument/money/timestamp/runtime_plane_tag 等）

### 2.2 shared-infra（共享基础设施）

> → 详见 **MOD-015** `shared_infra_blueprint.md`（跨层共享基础设施——14 子目录 ~115 文件，含 schemas/ssot_guard/observer/capability/paths/logging/health 等）

### 2.3 shared-errors（统一错误层次）

> **补全 ssot_guard.py:L103 标记的「尚未完成的 ZephyrBaseError 体系」。**
> 与 contracts/errors/ 的区别：contracts/errors/ 是 dataclass 值对象（跨层结构化错误传递），
> 本子模块是 Python Exception 继承树（throw/catch 统一入口）。

> → 详见 **MOD-015** `shared_infra_blueprint.md`（shared/errors.py — ZephyrBaseError + 12 子类错误层次）

### 2.4 shared-constants（集中 re-export）

> **修复散落枚举问题**——此前 AI 需要到 instrument.py / order.py / observer.py / schemas.py 四处找枚举。

> → 详见 **MOD-015** `shared_infra_blueprint.md`（shared/constants.py — 共享枚举集中 re-export）

### 2.5 shared-events（事件体 Schema）

> **修复 B6/B10 盲点**——observer.py 的 emit() 接受裸 dict，消费者不知道 payload 结构。

> → 详见 **MOD-015** `shared_infra_blueprint.md`（shared/events/event_schemas.py — 事件体 Schema）

### 2.6 shared-resilience（韧性基座）

> **盲点 B6/B9/B15 修复**——统一重试/熔断/降级策略，零依赖基类。
> 与 gates/circuit_breaker.py 互补——本模块纯内存，gates 版 SQLite 持久化 + 门禁集成。

> → 详见 **MOD-015** `shared_infra_blueprint.md`（shared/resilience/ — retry/circuit_breaker/fallback 韧性基座）

### 2.7 shared-lifecycle（模块生命周期）

> **盲点 B8 修复**——统一模块初始化/启动/关闭/健康检查契约。

> → 详见 **MOD-015** `shared_infra_blueprint.md`（shared/lifecycle/hooks.py — 模块生命周期钩子）

### 2.8 shared-feature-flags（功能开关）

> **盲点 B7/B10 修复**——100% AI 施工下的 AI 行为开关，配置驱动。

> → 详见 **MOD-015** `shared_infra_blueprint.md`（shared/flags.py — FeatureFlag 功能开关系统）

### 2.9 shared-utilities（通用工具层）

> **盲点 #5/#14/#15/#3 修复**——类型安全 + diff/patch + 安全I/O + 配置加载四大缺口。

> → 详见 **MOD-015** `shared_infra_blueprint.md`（shared/utils/ — types/diff_utils/file_utils/config 通用工具层）

### 2.10 shared-process-lifecycle（进程生命周期网关）

> ProcessLifecycleGateway — 统一进程创建入口 + idle_timeout 空闲回收 + DaemonRegistry 自动注册 + Gate 防绕过。
> 设计根因: 裸 Popen/Process 绕过 MCPProcessPool 导致进程泄漏。
> 依赖图: [DEP-GRAPH-process-lifecycle-001](file:///D:/ZephyrAlpha/data/asset_index/archive/DEP-GRAPH-process-lifecycle-001.yaml)

> → 详见 **MOD-015** `shared_infra_blueprint.md`（shared/infra/process_lifecycle_gateway.py + gates 门禁 — 进程生命周期网关）

**ProcessPool 增强** (modify existing `process_pool.py`):

| 新增功能 | 说明 |
|---------|------|
| `idle_timeout_s` (默认 600s) | 空闲超时自动回收——自上次 get_or_create 后无复用超时则 terminate |
| DaemonRegistry 集成 | 每个池化进程启动/回收时自动注册/注销到 DaemonRegistry |
| `launch_daemon()` | 新增接口——启动 daemon 进程并注册到 DaemonRegistry |

**不变量**:
- 所有子进程创建必须经过 ProcessLifecycleGateway（Gate 门禁校验）
- 所有池化进程 idle_timeout_s 后必须被回收
- 所有池化进程必须在 DaemonRegistry 中注册
- Gateway 本身不持有业务逻辑——只做路由和生命周期管理

**消费者**: AutoRuntimeCore (ollama serve 启动) / MCPLauncher (MCP Server DAG 启动)

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | shared/contracts | 跨层数据契约 SSoT | — | 同步调用 |
| 2 | shared/events | 异步事件总线 | contracts | 发布/订阅 |
| 3 | shared/resilience | 韧性基座（重试/熔断/降级） | — | 同步调用 |
| 4 | shared/infra | 生产基础设施（缓存/限流/锁/Outbox/Metrics） | contracts, events | 同步调用 + 事件 |
| 5 | core/blueprint_decomposer | 蓝图分解器 | contracts | 同步调用 |
| 6 | core/event_bus | 核心事件总线 | events | 发布/订阅 |
| 7 | core/models | Task 核心模型 | contracts | 同步调用 |
| 8 | shared/infra/process_lifecycle_gateway | 进程生命周期统一入口 | ProcessPool, DaemonRegistry | 同步调用 + 注册 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | 业务模块 | Task 创建/状态变更 | shared/schemas → SQLite | Task Pydantic Model |
| 2 | 业务模块 | 事件发布 | shared/observer → outbox → 消费者 | EventSchema Pydantic Model |
| 3 | AI Session | 缓存查询 | shared/cache (L1→L2→DB) | pickle / dict |
| 4 | AI Session | 限流请求 | shared/limiter → cost_budget | TokenBucket 状态 |
| 5 | 所有模块 | 日志写入 | shared/logging → JSONL 文件 | JSON 日志 |
| 6 | AutoRuntimeCore/MCPLauncher | 进程启动请求 | ProcessLifecycleGateway → ProcessPool → subprocess | 进程句柄 + pid |
| 7 | ProcessPool | 空闲超时回收 | ProcessLifecycleGateway → DaemonRegistry 注销 | 进程终止信号 |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| CircuitBreaker CLOSED | 失败率 > 阈值 | OPEN | 失败计数 ≥ min_requests |
| CircuitBreaker OPEN | 超时到期 | HALF_OPEN | timeout 已过 |
| CircuitBreaker HALF_OPEN | 探测成功 | CLOSED | 成功计数 ≥ success_threshold |
| CircuitBreaker HALF_OPEN | 探测失败 | OPEN | 失败计数 ≥ 1 |
| Task PENDING | 调度器分配 | RUNNING | 资源可用 |
| Task RUNNING | 执行完成 | COMPLETED | 结果非空 |
| Task RUNNING | 执行失败 | FAILED | 异常非空 |
| IdempotencyKey IN_PROGRESS | 超时 30min | ABANDONED | 超过 max_execution_time |

---

## 3. Core 模块（16 子目录, 60 文件）

> actual_disk_path: `src/zephyr/core/`（60 个 .py 文件：7 根目录 + 53 子目录）
> construction_progress: 60/60 文件已落盘（根目录 7 文件 phase_0_14_complete，子目录 36 功能文件 early-bird，16 __init__.py 自动生成）

### 3.1 core/ 文件蓝图归属表

> → 详见 **MOD-014** `governance_core_blueprint.md`（core/ 16 子目录 60 文件——blueprint_decomposer/models/context_engine/event_bus/lifecycle 等）

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | 全部 29 文件已实现 | ✅ implemented |
| experimental | models.py 升级到 v0.3.0（继承 schemas.py Task 31字段）| ✅ completed |
| phase_4 | 可观测 & 契约安全——结构化日志 + 契约测试 + AI 快速参考 | ✅ completed |
| phase_5 | 演化安全——测试夹具/工厂 + Schema 迁移 + 废弃策略 | ✅ completed |
| phase_6 | 韧性增强——死信队列 + 版本协商 + 健康聚合 | ✅ completed |
| phase_7 | 生产基础 1——序列化 + API Client + Secrets 管理 | ✅ completed |
| phase_8 | 生产基础 2——缓存 + 速率限制 + 幂等性 + 上下文传播 | ✅ completed |
| phase_9 | 可观测增强 —— Metrics + 分页 + 时间工具 + 环境检测 + SemVer | ✅ completed |
| phase_10 | 进阶架构 —— 分布式锁 + Outbox 模式 + Schema Registry | ✅ completed |
| phase_11 | AI 成本可控 —— 成本预算熔断 + 上下文预算管理（B26, B28） | ✨ early-bird（cost_budget 208行3类9函 + context_budget 259行4类17函，已落盘已导入，缺单元测试） |
| phase_12 | AI 质量可控 —— Evals 框架 + Session 审计轨迹（B29, B32） | ✨ early-bird（evals 258行7类14函 + session_audit 315行8类19函，已落盘已导入，缺单元测试） |
| phase_13 | AI 流程可控 —— Durable Execution + 后处理管道（B30, B31） | ✨ early-bird（durable_execution 335行6类19函 + post_process 289行5类9函，已落盘已导入，缺单元测试） |
| phase_14 | AI 团队可控 —— 宪法自愈 + Multi-Agent 编排 + Skill 注册表（B27, B33, B34）+ 版本协商 | ✨ early-bird（constitutional_update 225行3类7函 + multi_agent 272行7类13函 + skill-registry 194行6类2函 + version_negotiation 174行6类8函，已落盘已导入，缺单元测试） |
| phase_15 | AI 架构可控 —— Provider 抽象 + 上下文压缩 + 输出评分 + DI 容器 + 沙箱 + 配置链（B35-B40） | ⬜ planned |
| phase_16 | AI 溯源可控 —— AIBOM 物料清单 + Memory Bank 持久记忆（B41, B42） | ⬜ planned |
| phase_17 | AI 安全可控 —— DSPy 声明式优化 + Structured Concurrency + Dry-run 模式（B43, B44, B45） | ⬜ planned |
| phase_18 | AI 韧性可控 —— Backpressure + Quota 配额 + Degradation Matrix + KG 接口 + Drift 检测（B46-B50） | ⬜ planned |
| phase_19 | AI 安全纵深 —— Prompt 注入防御 + 结构化输出强制保障 + LLM API 专属限流（B51-B53） | ⬜ planned |
| phase_20 | AI 校验护盾 —— 工具调用参数护栏 + Prompt 缓存策略 + 多 Provider 语义降级（B54-B56） | ⬜ planned |

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 共享+核心——115 已跟踪文件（67 Phase 0-14 + 41 原 orphan 归类 + 7 core 根目录）已落盘 + 109 shared 子目录文件（§5.1a）+ 53 core 子目录文件（§5.1a-core）= 215 shared/ + 60 core/ .py 文件全覆盖

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/shared/API_INDEX.py` | ✅ 已实现 | |
| `src/zephyr/shared/capability.py` | ✅ 已实现 | |
| `src/zephyr/shared/content_fingerprint.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/market/instrument.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/portfolio/money.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/core/runtime_plane_tag.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/core/timestamp.py` | ✅ 已实现 | |
| `src/zephyr/shared/api/dos_launcher.py` | ✅ 已实现 | |
| `src/zephyr/shared/frontmatter_utils.py` | ✅ 已实现 | |
| `src/zephyr/shared/observer.py` | ✅ 已实现 | |
| `src/zephyr/shared/paths.py` | ✅ 已实现 | |
| `src/zephyr/shared/schemas.py` | ✅ 已实现 | |
| `src/zephyr/shared/ssot_guard.py` | ✅ 已实现 | |
| `src/zephyr/shared/time_utils.py` | ✅ 已实现 | |
| `src/zephyr/shared/token_utils.py` | ✅ 已实现 | |
| `src/zephyr/shared/constants.py` | ✅ 已实现 | Phase 1 新增：共享枚举集中 re-export |
| `src/zephyr/shared/errors.py` | ✅ 已实现 | Phase 1 新增：ZephyrBaseError + 12 子类 |
| `src/zephyr/shared/events/event_schemas.py` | ✅ 已实现 | Phase 1 新增：Observer 事件体 Pydantic Schema |
| `src/zephyr/shared/resilience/retry.py` | ✅ 已实现 | Phase 2 新增：async_retry 重试装饰器 |
| `src/zephyr/shared/resilience/circuit_breaker.py` | ✅ 已实现 | Phase 2 新增：轻量熔断器三态状态机 |
| `src/zephyr/shared/resilience/fallback.py` | ✅ 已实现 | Phase 2 新增：FallbackChain 降级策略链 |
| `src/zephyr/infrastructure/shared_services/lifecycle/hooks.py` | ✅ 已实现 | Phase 2 新增：模块生命周期钩子 + 健康检查 |
| `src/zephyr/shared/flags.py` | ✅ 已实现 | Phase 2 新增：FeatureFlag 功能开关系统 |
| `src/zephyr/shared/types.py` | ✅ 已实现 | Phase 3 新增：13 个语义化 NewType |
| `src/zephyr/shared/diff_utils.py` | ✅ 已实现 | Phase 3 新增：diff/patch 统一工具 |
| `src/zephyr/shared/io/file_utils.py` | ✅ 已实现 | Phase 3 新增：原子写/备份/rollback |
| `src/zephyr/shared/config/loader.py` | ❌ ARCH-038 已退役 | 虚假统一空壳（0消费者），配置加载回归 infrastructure/config/load_config() |
| `src/zephyr/shared/logging.py` | ✅ 已实现 | Phase 4 新增：结构化日志 ZephyrLogger + trace_id 传播 |
| `src/zephyr/shared/api/shared_quickref.yaml` | ✅ 已实现 | Phase 4 新增：AI 零歧义快速参考 canonical YAML |
| `src/zephyr/shared/testing.py` | ✅ 已实现 | Phase 5 新增：测试夹具/工厂——7个工厂函数 |
| `src/zephyr/shared/migration.py` | ✅ 已实现 | Phase 5 新增：版本化 Schema 迁移系统 |
| `src/zephyr/shared/deprecation.py` | ✅ 已实现 | Phase 5 新增：@deprecated 装饰器 + 三模式 |
| `src/zephyr/shared/events/dlq.py` | ✅ 已实现 | Phase 6 新增：死信队列——SQLite 持久化 + 定时重试 |
| `src/zephyr/shared/__version__.py` | ✅ 已实现 | Phase 6 新增：PEP 440 版本常量 + 运行时校验 |
| `src/zephyr/shared/health.py` | ✅ 已实现 | Phase 6 新增：聚合健康检查 + JSON 可序列化 |
| `src/zephyr/shared/io/serialization.py` | ✅ 已实现 | Phase 7 新增：统一序列化——Decimal/str, datetime→ISO 8601 |
| `src/zephyr/shared/api_client.py` | ✅ 已实现 | Phase 7 新增：统一 API Client 基类——超时/重试/熔断/metrics |
| `src/zephyr/shared/secrets.py` | ✅ 已实现 | Phase 7 新增：Secrets 管理——Env/DotEnv Provider + sanitize |
| `src/zephyr/shared/infra/cache.py` | ✅ 已实现 | Phase 8 新增：缓存抽象——TTL + LRU 驱逐 + 最大容量 |
| `src/zephyr/shared/limiter.py` | ✅ 已实现 | Phase 8 新增：Token Bucket 速率限制器 |
| `src/zephyr/shared/idempotency.py` | ✅ 已实现 | Phase 8 新增：幂等性 infrastructure——Stripe 24h TTL 对齐 |
| `src/zephyr/shared/context.py` | ✅ 已实现 | Phase 8 新增：结构化 RequestContext——trace_id/span_id/tenant/agent |
| `src/zephyr/shared/metrics.py` | ✅ 已实现 | Phase 9 新增：Metrics Registry——Counter/Gauge/Histogram + Prometheus text |
| `src/zephyr/shared/utils/pagination.py` | ✅ 已实现 | Phase 9 新增：统一分页工具——Page[T]/CursorPage[T] |
| `src/zephyr/shared/time_utils.py` | ✅ 已实现 | Phase 9 新增：时间工具——now_utc/freeze_time/parse_iso |
| `src/zephyr/shared/env.py` | ✅ 已实现 | Phase 9 新增：环境检测——is_dev/is_prod/is_test |
| `src/zephyr/shared/lock.py` | ✅ 已实现 | Phase 10 新增：分布式锁抽象——MemoryLock + async context manager |
| `src/zephyr/shared/outbox.py` | ✅ 已实现 | Phase 10 新增：事务性 Outbox——polling publisher + at-least-once |
| `src/zephyr/shared/schema_registry.py` | ✅ 已实现 | Phase 10 新增：Schema Registry——集中式版本编目 + 兼容性查询 |
| `src/zephyr/infrastructure/shared_services/blueprint_decomposer.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/models.py` | ✅ 已实现 | v0.3.0 — 继承Task 31字段全链路贯通 |
| `src/zephyr/infrastructure/shared_services/__init__.py` | ✅ 已实现 | 包初始化 |
| `src/zephyr/infrastructure/shared_services/blueprint_code_sync.py` | ✅ 已实现 | 蓝图-代码同步 |
| `src/zephyr/infrastructure/shared_services/context_engine.py` | ✅ 已实现 | 上下文引擎 |
| `src/zephyr/infrastructure/shared_services/healthcheck_service.py` | ✅ 已实现 | 健康检查服务 |
| `src/zephyr/infrastructure/shared_services/session_continuity.py` | ✅ 已实现 | 会话连续性（根目录副本） |
| `src/zephyr/shared/tracing.py` | ✅ 已实现 | Phase 6 新增：OpenTelemetry 兼容 tracing context |
| `src/zephyr/resilience/budget_enforcement/cost_budget.py` | ✨ early-bird | Phase 11 (B26)：AI 成本预算熔断——208行 3类 9函 |
| `src/zephyr/orchestration/context_management/context_budget.py` | ✨ early-bird | Phase 11 (B28)：上下文预算管理——259行 4类 17函 |
| `src/zephyr/shared/evals.py` | ✨ early-bird | Phase 12 (B29)：Evals 评估框架——258行 7类 14函 |
| `src/zephyr/shared/session_audit.py` | ✨ early-bird | Phase 12 (B32)：Session 审计轨迹——315行 8类 19函 |
| `src/zephyr/shared/durable_execution.py` | ✨ early-bird | Phase 13 (B30)：Durable Execution——335行 6类 19函 |
| `src/zephyr/governance/behavioral-admission/post_process.py` | ✨ early-bird | Phase 13 (B31)：后处理管道——289行 5类 9函 |
| `src/zephyr/governance/constitutional_update/constitutional_update.py` | ✨ early-bird | Phase 14 (B27)：宪法自更新——225行 3类 7函 |
| `src/zephyr/infrastructure/runtime_integration/a2a_protocol/multi_agent.py` | ✨ early-bird | Phase 14 (B33)：Multi-Agent 编排——272行 7类 13函 |
| `src/zephyr/orchestration/agent_lifecycle/skill-registry.py` | ✨ early-bird | Phase 14 (B34)：Skill/Prompt 注册表——194行 6类 2函 |
| `src/zephyr/shared/version_negotiation.py` | ✨ early-bird | Phase 14：版本协商——174行 6类 8函 |
| `src/zephyr/governance/architecture_governance/path_resolver.py` | ✅ 已实现 | Phase 10 补注册：路径解析器——261行2类7函。消费者：mcp/task_manager_server.py |
| `src/zephyr/shared/contract_bus.py` | ✅ 已实现 | Phase 10 补注册：契约总线——140行6类14函。消费者：contract_tester.py |
| `src/zephyr/shared/event_bus.py` | ✅ 已实现 | Phase 10 补注册：共享事件总线——124行3类7函（与core/events/event_bus独立） |
| `src/zephyr/shared/__init__.py` | ✅ 已实现 | 包初始化 |
| `src/zephyr/shared/blueprint_scorer.py` | ✅ 已实现 | 蓝图路由评分 |
| `src/zephyr/shared/kg_interface.py` | ✅ 已实现 | 知识图谱接口 |
| `src/zephyr/shared/adaptive_sampler.py` | ✅ 已实现 | 原 orphan 归类：自适应采样 |
| `src/zephyr/shared/ai_audit_guard.py` | ✅ 已实现 | 原 orphan 归类：AI修改审计守卫 |
| `src/zephyr/shared/ai_understandability_constraint.py` | ✅ 已实现 | 原 orphan 归类：AI可理解性约束 |
| `src/zephyr/shared/alert_escalation.py` | ✅ 已实现 | 原 orphan 归类：告警升级 |
| `src/zephyr/shared/alert_manager.py` | ✅ 已实现 | 原 orphan 归类：告警收敛管理 |
| `src/zephyr/shared/alert_precision_tracker.py` | ✅ 已实现 | 原 orphan 归类：告警精度追踪 |
| `src/zephyr/shared/blueprint_code_auditor.py` | ✅ 已实现 | 原 orphan 归类：蓝图-代码一致性审计 |
| `src/zephyr/shared/budget_aware_prompt.py` | ✅ 已实现 | 原 orphan 归类：预算感知提示 |
| `src/zephyr/shared/capacity_calibrator.py` | ✅ 已实现 | 原 orphan 归类：容量校准器 |
| `src/zephyr/shared/capacity_digital_twin.py` | ✅ 已实现 | 原 orphan 归类：容量数字孪生 |
| `src/zephyr/shared/capacity_fingerprint.py` | ✅ 已实现 | 原 orphan 归类：容量指纹 |
| `src/zephyr/shared/capacity_governance_loop.py` | ✅ 已实现 | 原 orphan 归类：容量治理闭环 |
| `src/zephyr/shared/capacity_runbook_generator.py` | ✅ 已实现 | 原 orphan 归类：容量Runbook生成 |
| `src/zephyr/shared/code_economy_analyzer.py` | ✅ 已实现 | 原 orphan 归类：代码经济效益分析 |
| `src/zephyr/shared/combinatorial_gate.py` | ✅ 已实现 | 原 orphan 归类：组合门禁 |
| `src/zephyr/infrastructure/runtime_integration/config_validator.py` | ✅ 已实现 | 原 orphan 归类：配置校验器 |
| `src/zephyr/shared/contract_tester.py` | ✅ 已实现 | 原 orphan 归类：契约合规测试 |
| `src/zephyr/shared/core_integrity_guard.py` | ✅ 已实现 | 原 orphan 归类：核心完整性守卫 |
| `src/zephyr/shared/cost_estimator.py` | ✅ 已实现 | 原 orphan 归类：成本估算器 |
| `src/zephyr/shared/degradation_chain.py` | ✅ 已实现 | 原 orphan 归类：退化链追踪 |
| `src/zephyr/shared/dependency_capacity_guard.py` | ✅ 已实现 | 原 orphan 归类：依赖容量守卫 |
| `src/zephyr/shared/dual_channel_alert.py` | ✅ 已实现 | 原 orphan 归类：双通道告警 |
| `src/zephyr/shared/error_budget_tracker.py` | ✅ 已实现 | 原 orphan 归类：错误预算追踪器 |
| `src/zephyr/shared/events/event_bus_upgrade.py` | ✅ 已实现 | 原 orphan 归类：事件总线升级 |
| `src/zephyr/shared/fault_isolator.py` | ✅ 已实现 | 原 orphan 归类：故障隔离器 |
| `src/zephyr/shared/heartbeat_server.py` | ✅ 已实现 | 原 orphan 归类：心跳服务器 |
| `src/zephyr/infrastructure/runtime_integration/rollback/kill_switch.py` | ✅ 已实现 | 原 orphan 归类：Kill Switch |
| `src/zephyr/shared/longevity_monitor.py` | ✅ 已实现 | 原 orphan 归类：长时运行监控 |
| `src/zephyr/shared/model_capacity_probe.py` | ✅ 已实现 | 原 orphan 归类：模型容量探针 |
| `src/zephyr/shared/module_birth_registry.py` | ✅ 已实现 | 原 orphan 归类：模块出生注册表 |
| `src/zephyr/shared/owner_trust_gauge.py` | ✅ 已实现 | 原 orphan 归类：信任度量 |
| `src/zephyr/infrastructure/runtime_integration/pydantic_v2_migrator.py` | ✅ 已实现 | 原 orphan 归类：Pydantic迁移助手 |
| `src/zephyr/shared/reasoning_spans.py` | ✅ 已实现 | 原 orphan 归类：推理跨度追踪 |
| `src/zephyr/shared/sandbox_executor.py` | ✅ 已实现 | 原 orphan 归类：沙箱执行器 |
| `src/zephyr/resilience/budget_enforcement/semantic_cache.py` | ✅ 已实现 | 原 orphan 归类：语义缓存 |
| `src/zephyr/shared/slo_review_assistant.py` | ✅ 已实现 | 原 orphan 归类：SLO审查助手 |
| `src/zephyr/shared/task_heartbeat.py` | ✅ 已实现 | 原 orphan 归类：任务心跳 |
| `src/zephyr/shared/ttl_cleanup_engine.py` | ✅ 已实现 | 原 orphan 归类：TTL清理引擎 |
| `src/zephyr/shared/vibe_experiment_tracker.py` | ✅ 已实现 | 原 orphan 归类：实验追踪 |
| `src/zephyr/infrastructure/runtime_integration/warm_hot_gate.py` | ✅ 已实现 | 原 orphan 归类：冷热路径门禁 |
| `src/zephyr/shared/zephyr_logger.py` | ✅ 已实现 | 原 orphan 归类：ZephyrLogger日志 |

### 5.1a 子目录文件索引（109 文件）

> TD-SHARED-001 重组：34对发散副本已全部解决为 re-export wrapper。★=独立实现，其余为 re-export wrapper。
> 已在 §5.1 跟踪的文件标注(§5.1)，不重复计入。

| 子目录 | 文件数 | 文件列表 |
|--------|--------|---------|
| api/ | 4 | `__init__`, `api_client`★, `api_index`★, `dos_launcher`★ |
| config/ | 2 | `__init__`, `loader`(§5.1) |
| contracts/backpressure/ | 4 | `__init__`, `pause`★, `resume`★, `throttle`★ |
| contracts/core/ | 10 | `__init__`, `base_event`★, `enforcer`★, `factories`★, `gate_types`★, `registry`★, `runtime_plane_tag`(§5.1), `system_configuration`★, `timestamp`(§5.1), `trace_context`★ |
| contracts/errors/ | 7 | `__init__`, `contract_violation_error`★, `data_quality_error`★, `execution_rejection_error`★, `factor_computation_error`★, `risk_limit_violation_error`★, `signal_degradation_warning`★ |
| contracts/execution/ | 6 | `__init__`, `capital_allocation_result`★, `execution_report`★, `fill`★, `model_serving_request`★, `order`★ |
| contracts/experiment/ | 3 | `__init__`, `experiment_result`★, `model_serving_response`★ |
| contracts/external/ | 5 | `__init__`, `ext_001`★, `ext_002`★, `ext_003`★, `ext_004`★ |
| contracts/market/ | 7 | `__init__`, `factor_monitor_report`★, `factor_signal`★, `instrument`(§5.1), `macro_factor_signal`★, `market_data`★, `synthesized_signal`★ |
| contracts/portfolio/ | 5 | `__init__`, `money`(§5.1), `performance_attribution_report`★, `position`★, `strategy_lifecycle_event`★ |
| contracts/risk/ | 5 | `__init__`, `compliance_rule`★, `risk_dashboard_snapshot`★, `risk_limits`★, `risk_metrics`★ |
| events/ | 3 | `__init__`, `dlq`(§5.1), `dlq_bridge`★ |
| foundation/ | 7 | `__init__`, `constants`, `deprecation`, `env`, `errors`, `flags`, `types` |
| infra/ | 8 | `__init__`, `cache`, `idempotency`, `limiter`, `lock`, `observer`, `outbox`, `process_pool`★ |
| io/ | 8 | `__init__`, `content_fingerprint`, `file_utils`, `frontmatter_utils`, `io_cache`★, `paths`, `serialization`, `streaming_reader`★ |
| lifecycle/ | 6 | `__init__`, `daemon_registry`★, `hooks`(§5.1), `lazy_loader`★, `resource_optimization_engine`★, `resource_optimization_models`★ |
| observability/ | 7 | `__init__`, `health`★, `health_discovery`★, `logging`, `metrics`, `token_utils`, `tracing` |
| resilience/ | 4 | `__init__`, `circuit_breaker`(§5.1), `fallback`(§5.1), `retry`(§5.1) |
| schema/ | 3 | `__init__`, `schema_registry`, `schemas` |
| security/ | 4 | `__init__`, `capability`, `secrets`, `ssot_guard` |
| utils/ | 9 | `__init__`, `blueprint_scorer`★, `context`, `db_utils`★, `diff_utils`, `migration`, `pagination`, `testing`, `time_utils` |

### 5.1a-core Core 子目录文件索引（53 文件）

> core/ 目录共 60 个 .py 文件。§5.1 已跟踪 7 个根目录文件。本节列出子目录文件。

| 子目录 | 文件数 | 文件列表 |
|--------|--------|---------|
| adaptation/ | 3 | `__init__`, `execution_tuner`★, `prompt_version_manager`★ |
| compensation/ | 2 | `__init__`, `saga_compensator`★ |
| dependency/ | 2 | `__init__`, `dependency_graph`★ |
| draft/ | 2 | `__init__`, `draft_assistant`★ |
| events/ | 5 | `__init__`, `event_bus`★, `event_reactor`★, `event_store`★, `hook_dispatcher`★ |
| impact/ | 3 | `__init__`, `impact_propagator`★, `llm_impact_analyzer`★ |
| knowledge/ | 4 | `__init__`, `ke_linker`★, `ke_structurer`★, `kms_interface`★ |
| lifecycle/ | 3 | `__init__`, `scope_guard`★, `task_lifecycle_manager`★ |
| maintenance/ | 5 | `__init__`, `autonomy_monitor`★, `dogfooding`★, `handbook`★, `zero_config`★ |
| observability/ | 6 | `__init__`, `cli_summary`★, `cost_tracker`★, `failure_matcher`★, `notifier`★, `trace_decorator`★ |
| quality/ | 2 | `__init__`, `quality_monitor`★ |
| queue/ | 3 | `__init__`, `task_queue`★, `task_scheduler`★ |
| reliability/ | 5 | `__init__`, `circuit_breaker`★, `context_guard`★, `diff_planner`★, `retry_handler`★ |
| session/ | 3 | `__init__`, `session_boundary`★, `session_continuity`★ |
| sla/ | 2 | `__init__`, `sla_monitor`★ |
| sync/ | 2 | `__init__`, `blueprint_code_sync`★ |

### 5.1b 待集成文件

> **状态更新（2026-05-10）**：原 41 项 orphan 已全部归类至 §5.1（根目录文件）或 §5.1a（子目录文件）。本节保留空表作为未来新 orphan 的登记位置。

| 文件 | 集群 | 规模 | 用途 |
|------|------|------|------|
| *(空——所有 orphan 已归类)* | | | |

### 5.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/test_schemas.py` | ✅ 已实现 | |
| `tests/test_ssot_guard.py` | ✅ 已实现 | |
| `tests/test_capability.py` | ✅ 已实现 | |
| `tests/test_money.py` | ✅ 已实现 | |
| `tests/test_instrument.py` | ✅ 已实现 | |
| `tests/contract/test_import_chain.py` | ✅ 已实现 | Phase 10：8 直接消费者导入链路契约验证（Phase 4 初始 6 → Phase 10 扩展至 8，移除 4 间接消费者） |
| `tests/contract/test_schema_stability.py` | ✅ 已实现 | Phase 4 新增：Task 31字段快照 + TaskCard继承 + 错误层次 + 类型别名 |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 6. 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` | 本文件 |
| Shared 代码 | `D:\ZephyrAlpha\src\zephyr\shared\` | 跨层共享模型/工具 |
| Core 代码 | `D:\ZephyrAlpha\src\zephyr\core\` | 核心基础设施 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\test_shared.py` + `test_core.py` | 单元测试 |
| 契约基础框架 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\core\base_event.py` + `enforcer.py` + `factories.py` + `registry.py` + `system_configuration.py` | 契约基类/执行器/工厂/注册表/系统配置（5个核心契约，★标记于§5.1a-core） |
| 外部集成契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\external\ext_001.py` ~ `ext_004.py` | 4个外部系统集成契约（★标记于§5.1a） |

---

## 7. 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| 所有基础设施域模块 | shared 模型引用 | `from zephyr.shared.models import ...` | 所有模块可 import shared 模型 |
| Agent RBAC (MOD-INF-018) | AgentIdentity 模型 | `shared/models.py` → `AgentIdentity` | RBAC 可使用 AgentIdentity |
| Audit Trail (MOD-INF-020) | AuditEvent 模型 | `shared/models.py` → `AuditEvent` | Audit Trail 可使用 AuditEvent |
| Event Bus | 事件总线 | `core/event_bus.py` | 模块间事件通信 |

### 7.1 反向依赖索引 —— 谁依赖 Shared+Core

> 本节是 **AI 施工安全护栏**。修改 shared/core 任一文件前，AI MUST 对照此表确认影响范围。
> 每次新增模块依赖 shared/core 时，MUST 更新此表。

| 消费方 module_id | 消费方名称 | 导入的 shared/core 文件 | 导入量 | 关键依赖点 |
|------|------|------|:---:|------|
| MOD-DATABASE | Database | `schemas.py` (Task/TaskStatus), `paths.py` (DB_PATH/REPO_ROOT) | 2 文件 | SQLite CRUD 继承 Task 模型；DB 路径从 paths SSoT 获取 |
| MOD-CONTEXT_ENGINE | Context Engine | `schemas.py`, `paths.py`, `token_utils.py`, `time_utils.py`, `frontmatter_utils.py` | 9 文件 | 上下文装配、Token 预算、时间戳、frontmatter 解析全链路依赖 |
| MOD-INF-009 | Pipeline | `schemas.py`, `paths.py`, `time_utils.py` | 2 文件 | 管线调度器依赖 Task 状态模型 + 路由模型 |
| MOD-GATE_ENGINE | Gate Engine | `schemas.py`, `paths.py`, `time_utils.py`, `frontmatter_utils.py` | 3 文件 | 门禁判决依赖 TaskStatus/CheckResult；熔断器依赖配置路径 |
| MOD-FEEDBACK_LOOP | Feedback Loop | `schemas.py`, `paths.py`, `time_utils.py`, `observer.py` | 3 文件 | 自进化引擎依赖事件总线 + 指标采集模型 |
| MOD-KB-001 | Knowledge Base | `schemas.py` (KnowledgeEntry/KeCategory), `paths.py`, `content_fingerprint.py`, `frontmatter_utils.py` | 10 文件 | KE 生命周期全链路——ingest/extract/activate/analyze 全部依赖 shared 模型 |
| MOD-INF-013 | MCP Servers | `schemas.py`, `paths.py`, `time_utils.py` | 3 文件 | task_manager/doc_guard/gate_engine 三个 MCP Server 均对接 shared 模型 |
| MOD-LLM_SECURITY | LLM Security | `schemas.py`, `paths.py`, `time_utils.py` | 1 文件 | 安全审计日志依赖 AuditEvent 模型 |
| MOD-INF-002 | Runtime Integration | `schemas.py`, `paths.py`, `observer.py`, `capability.py`, `dos_launcher.py` | 5 文件 | 跨层集成——事件总线、能力管控、指令加载、任务调度全链路 |
| MOD-INF-017 | Code Dedup Engine | `paths.py`, `content_fingerprint.py`, `frontmatter_utils.py` | — | 蓝图声明 `depends_on: MOD-INF-016` |
| MOD-INF-019 | Agent Spec | `schemas.py`, `frontmatter_utils.py` | — | Skill 加载器依赖蓝图 frontmatter 解析 |
| — | shared/contracts/ 扩展文件 | `schemas.py`, `paths.py`, `time_utils.py`, `portfolio/money.py`, `market/instrument.py` | 20+ 文件 | backpressure/errors/enforcer/registry 等 20+ 契约文件全部 import shared 基础设施 |

> **AI 安全规则**：修改 `schemas.py` 的 Task 类 → 影响 **至少 10 个消费者模块**（全部 基础设施层）。
> 修改 `paths.py` 的路径常量 → 影响 **所有 src/zephyr/ 下代码**。
> 修改 `errors.py` 的异常层次 → 影响 **所有模块的异常处理链**（新增子类安全，修改已有子类谨慎）。
> 修改 `event_schemas.py` 的 Schema → 影响 **所有 observer.emit() 调用点的 payload 结构**。
> 修改 `resilience/retry.py` 的 RetryConfig → 影响 **所有使用 @async_retry 的调用点**。
> 修改 `lifecycle/hooks.py` 的 LifecycleAware Protocol → 影响 **所有实现该 Protocol 的模块**。
> 修改 `flags.py` 的 FeatureFlag 状态 → **AI 不可修改**——运维手动操作 config/。
> 修改 `types.py` 的 NewType → 影响 **所有使用这些别名的函数签名**（mypy 会报错）。
> 修改 `config/loader.py` 的加载逻辑 → 影响 **所有模块的配置加载链路**。
> 修改 `logging.py` 的 ZephyrLogger 接口 → 影响 **所有使用 get_logger() 的模块**。新增日志方法安全，修改/删除已有方法谨慎。
> 修改 `shared_quickref.yaml` → **AI 可自由更新**——本文件是 AI 导航用的派生文件，无消费者依赖。
> 修改 `testing.py` 工厂函数签名 → 影响 **所有使用工厂函数的测试**。新增参数需向后兼容（keyword-only + 默认值）。
> 修改 `migration.py` 迁移路径 → 影响 **所有依赖 migrate_task() 的模块**。必须注册双向迁移 + 更新 latest_schema_version。
> 修改 `deprecation.py` 的 DeprecatedAPIError → 异常层次变更，影响 **所有 catch 该异常的地方**。
> 修改 `events/dlq.py` 的 DeadLetter 结构 → 影响 **所有依赖 DLQ 的模块**。新增字段安全，修改/删除字段谨慎。
> 修改 `__version__.py` → 影响 **所有调用 check_shared_version() 的模块**。版本号递增安全，格式变更谨慎。
> 修改 `health.py` 的 HealthStatus 枚举 → 影响 **所有 health check consumer**。新增状态值安全，删除/重命名谨慎。

**漂移防护**：修改 Shared Core 接口 MUST 同步更新所有消费者蓝图的 depends_on（§7.1 表）；新增 shared/ 模块 MUST 更新 API_INDEX.py + shared_quickref.yaml + §5 文件清单；修改 schemas.py Task 31字段 MUST 更新 test_schema_stability.py 快照。

---

## 8. 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 版本号+完整度 | 蓝图补全后更新 |
| 2 | models.py | `D:\ZephyrAlpha\src\zephyr\shared\models.py` | 新增 AgentIdentity/AuditEvent 模型 | MOD-INF-018/020 实现后需新增模型 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | SQLite 写入拥塞（SQLITE_BUSY） | busy_timeout > 5s | WriteBatcher 批量合并（暂缓待 L 级）+ 降级为内存队列 | 所有持久化操作 |
| 2 | CircuitBreaker 熔断触发 | 失败率 > 阈值 | FallbackChain 降级 + 半开探测 | 依赖该外部服务的所有 Session |
| 3 | Cache L2 命中率 < 50% | 监控指标 | 降级为仅 L1 + 关键查询走 DB 直连 | 上下文注入、蓝图查询 |
| 4 | PriorityLock 死锁 | 等待 > 60s | DeadWorkerReaper 强制释放 + TTL 30min | 所有持锁操作 |
| 5 | Outbox 积压 > 5,000 | pending 队列监控 | 背压拒绝新 append + fire-and-forget 降级 | 事件通知延迟 |
| 6 | Worker 进程崩溃 | 心跳超时 30s | Controller 重启 Worker + 清理共享状态 | 该 Worker 上的所有任务 |
| 7 | IdempotencyKey IN_PROGRESS 超时 | 超过 max_execution_time 30min | IdempotencyJanitor 标记 ABANDONED | 相同 idempotency_key 的后续请求 |
| 8 | LLM API Rate Limit (429) | HTTP 状态码 | limiter.py 分区限流 + 指数退避重试 | 所有 LLM API 调用 |

---

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | API Key 泄露 | 高 | secrets.py 环境变量/DotEnv Provider + sanitize 脱敏 | `scan_secret_leak.py` 扫描 |
| 2 | SQL 注入 | 高 | Pydantic V2 参数化 + ORM 模式，禁止字符串拼接 | 代码审计 + 静态分析 |
| 3 | 路径遍历 | 中 | paths.py SSoT 路径常量 + file_utils 路径校验 | 边界测试 |
| 4 | 竞态条件（锁/幂等性） | 中 | PriorityLock TTL + IdempotencyKey 超时清理 | 并发压力测试 |
| 5 | 日志敏感数据泄露 | 中 | ZephyrLogger 自动脱敏 + secrets.py sanitize | 日志审计 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | shared/ 所有公开类和函数 | Task 31字段创建/校验、Cache CRUD、Limiter 限流、Lock acquire/release、Idempotency start/complete | 覆盖率 > 80% |
| 2 | 契约测试 | 跨模块 import 链 | 6 消费者导入验证 + Schema 稳定性快照 | 29/29 通过 |
| 3 | 性能测试 | cache/limiter/serializer | P50/P95/P99 延迟对比基线 | 退化 < 10% |
| 4 | 并发测试 | lock/observer/outbox/idempotency | 100 并发读写压力测试 | 无死锁、无数据丢失 |
| 5 | 集成测试 | shared ↔ core ↔ 业务模块 | 端到端 Task 生命周期 | 全链路通过 |

---

## §10 依赖关系

### 10.1 依赖声明

> 详细消费者依赖索引见 [§7.1 反向依赖索引](#71-反向依赖索引--谁依赖-sharedcore)——12 消费者模块全部 traced。
> 关键依赖：MOD-CONTEXT_ENGINE(Context Engine), MOD-INF-009(Pipeline), MOD-GATE_ENGINE(Gate Engine), MOD-DATABASE(Database), MOD-INF-002(Runtime Integration)。

### 10.2 依赖图对齐声明

> 蓝图 §10.1 声明的依赖 MUST 与全局依赖图一致。

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-016` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

> 全局依赖图只覆盖模块级，不覆盖脚本级。本节补充蓝图内部脚本/模块间的执行顺序和数据流依赖。

#### 执行顺序依赖

> 如无内部依赖，填写"无内部依赖"。

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| — | — | — | — |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| shared/contracts | shared/schemas | Pydantic 数据模型 | 直接 import |
| shared/events | core/events/event_bus | EventSchema | 发布/订阅 |
| ProcessLifecycleGateway | ProcessPool | dict[str, PooledProcess] | 直接 import + 复合 |
| ProcessPool | DaemonRegistry | ProcessLifecycle 注册事件 | 方法调用 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 否 | 消费者固定，手动维护即可 |
| 2 | 依赖对齐自动验证 | 是 | 12个消费者，需 CI 门禁 |
| 3 | 临时时态内容自动清理 | 否 | 施工已完成 |
| 4 | 施工步骤完成度自动检测 | 否 | 施工已完成 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 2 | 依赖对齐自动验证 | CI门禁 | `validate_path_alignment.py` | 无 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:---:|:---:|---------|------|
| R1 | models.py 膨胀——所有模块的共享模型集中在一个文件 | 高 | 中 | 按域拆分：models_rbac.py / models_audit.py / models_task.py | 风险 |
| R2 | 循环依赖——shared ↔ core ↔ 业务模块 | 中 | 高 | 依赖方向严格单向：业务 → shared → core | 风险 |
| R3 | ~~models.py v0.3.0 破坏性变更——影响所有模块~~ | ~~中~~ | ~~高~~ | ✅ 已解决——v0.4.0 TaskCard 继承 Task 31字段全链路贯通，零破坏 | 风险 |
| R4 | shared 模块成为依赖瓶颈——修改 models.py 影响所有模块；循环依赖风险；models.py 破坏性变更全项目适配成本 | 高 | 高 | §7.1 反向依赖索引 + §17.4 版本兼容性策略 + 消费者通知机制 | 负面后果 |
| R5 | ProcessLifecycleGateway 单点故障——Gateway 故障导致所有进程无法启动 | 低 | 高 | Gateway 本身轻薄（无业务逻辑，纯路由）+ 启动失败时 fallback 到裸 Popen（带告警日志）+ DaemonRegistry 独立存活 | 风险 |

---

## 11. 施工指引

### 11.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 2 个 Phase（Phase 0 + experimental 已完成） |
| 施工模式 | 扩展（已有 shared + core 基础设施） |
| 核心风险 | ✅ 已消除——models.py v0.3.0 升级完成，零破坏 |

### 11.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | shared/models.py 已实现 | hard | ✅ | ✅ |
| 2 | core/event_bus.py 已实现 | hard | ✅ | ✅ |
| 3 | MOD-INF-018 AgentIdentity 模型定义 | soft | ☐ | ☐ |

### 11.3 实施步骤

#### 步骤 1：✅ models.py v0.3.0 升级（已完成）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3 Core 模块 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\core\models.py` |
| 验收标准 | TaskCard 继承 schemas.py Task（31字段：28业务+3 DB追踪）全链路贯通 |
| G7 检查项 | ✅ 所有现有模块 import 不受影响（17/17 测试通过） |

#### 步骤 2：按域拆分 models

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 R1 缓解 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\shared\models_rbac.py` 等 |
| 验收标准 | models.py 仅做 re-export，实际定义在域文件中 |
| G7 检查项 | 所有现有 import 路径不受影响？ |

### 11.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| ~~1~~ | ~~models.py v0.3.0 破坏现有模块~~ | ✅ 已完成，无需回滚——17/17 测试通过，零破坏 |
| 2 | 域拆分导致 import 失败 | 回退到单文件 models.py |

### 11.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 |
|---|--------|---------------|:---:|:---:|
| 1 | ~~models.py v0.3.0~~ | `D:\ZephyrAlpha\src\zephyr\core\models.py` | ✅ | ✅ |
| 2 | models_rbac.py | `D:\ZephyrAlpha\src\zephyr\shared\models_rbac.py` | ☐ | ☐ |
| 3 | models_audit.py | `D:\ZephyrAlpha\src\zephyr\shared\models_audit.py` | ☐ | ☐ |

---

## 12. 已发现未修复盲点（第四轮审计 | 2026-05-05）

> **审计基线**: v0.10.0（48 文件，221 导出）
> **审计语境**: 100% AI 施工 + 1人 + AI 维护 | 依赖氛围编程
> **新增研究来源**: PydanticAI、AgentBudget、LLMCore、Azure AI Agent Server、Boris Cherny 工作流、2026 多智能体编程全景

### 12.1 盲点总览（15 项，4 个优先级）

| 优先级 | 盲点 ID | 缺失能力 | 对应 Phase |
|:---:|:---:|------|:---:|
| 🔴 | B26 | **AI 成本预算与强制熔断**——LLM API 调用无硬性成本限制。Agent 异常循环可在 10 分钟内刷光 $200 配额 | 11 |
| 🔴 | B27 | **AI 上下文文件自更新基础设施**——AGENTS.md 是静态的，AI 无法把"犯错-学到"写回宪法 | 14 |
| 🔴 | B28 | **Token 计数与上下文预算管理**——`token_utils.py` 已存在于 shared/ 但未被 `__init__.py` 导出 | 11 |
| 🟠 | B29 | **Evals 框架**——有 contract tests（代码正确性），缺 Agent 输出质量系统评估 | 12 |
| 🟠 | B30 | **Durable Execution（断点续跑）**——长流程 AI task 可能运行数小时。进程崩溃后从头重跑 | 13 |
| 🟠 | B31 | **AI 输出后处理管道**——AI 生成代码后自动跑 lint/format/typecheck | 13 |
| 🟠 | B32 | **AI Session 完整审计轨迹**——每次 AI session 的记录（prompts、decisions、tool calls、costs、errors、outcomes） | 12 |
| 🟡 | B33 | **Multi-Agent 团队编排基座**——Agent role 定义 + task dispatch + result merge | 14 |
| 🟡 | B34 | **Agent Skill/Prompt 注册表（共享层）**——`prompt_registry.py` 在 `context_engine/` 而非 shared/ | 14 |
| 🟡 | B35 | **Model Provider 抽象层**——`api_client.py` 有 HTTP 层统一 client，缺模型语义层 | 15 |
| 🟡 | B36 | **上下文窗口压缩/截断策略**——当上下文接近模型上限时，需智能压缩 | 15 |
| 🔵 | B37 | **结构化 Agent 输出质量评分**——Relevance/Accuracy/Completeness 三维评分 + 自动回归 | 15 |
| 🔵 | B38 | **配置覆盖链（环境 > YAML > 默认）**——1人+AI 维护时需要清晰的配置优先级 | 15 |
| 🔵 | B39 | **依赖注入容器**——AI agent 组件化：constructor injection → 组件可替换 → 测试可隔离 | 15 |
| 🔵 | B40 | **AI 代码生成沙箱（共享层统一接口）**——`process_sandbox.py` 在 `llm_security/`，shared/ 应有沙箱接口抽象 | 15 |

---

## 13. 已发现未修复盲点（第五轮审计 | 2026-05-05）

> **审计基线**: v0.11.0（49 文件，223 导出）
> **审计语境**: 100% AI 施工 + 1人 + AI 维护 | 依赖氛围编程
> **新增研究来源**: Cisco AIBOM、Trusera ai-bom、DSPy 3.0、Mem0/Memori Memory Bank、Claude Code auto-memory、Azure Multi-Agent Patterns、LangSmith/Galileo LLMOps

### 13.1 盲点总览（10 项）

| 优先级 | 盲点 ID | 缺失能力 | 对应 Phase |
|:---:|:---:|------|:---:|
| 🔴 | B41 | **AIBOM — AI 物料清单与代码溯源** | 16 |
| 🔴 | B42 | **Memory Bank — Agent 跨会话持久记忆** | 16 |
| 🟠 | B43 | **DSPy 风格声明式 Prompt 优化** | 17 |
| 🟠 | B44 | **Structured Concurrency — 结构化并发** | 17 |
| 🟠 | B45 | **Dry-run / Simulation Mode** | 17 |
| 🟡 | B46 | **Backpressure Protocol** | 18 |
| 🟡 | B47 | **Quota Management — 资源配额** | 18 |
| 🟡 | B48 | **Graceful Degradation Matrix** | 18 |
| 🟡 | B49 | **Knowledge Graph Interface** | 18 |
| 🟡 | B50 | **Data Drift Detection** | 18 |

---

## 14. 已发现未修复盲点（第六轮审计 | 2026-05-05）

> **审计基线**: v0.12.0（49 文件，223 导出）
> **审计方法**: AI 安全纵深防御 / LLM 结构化输出强制保障 / LLM API 专属基础设施

### 14.1 盲点总览（6 项）

| 优先级 | 盲点 ID | 缺失能力 | 对应 Phase |
|:---:|:---:|------|:---:|
| 🔴 | B51 | **Prompt Injection Defense — 标签式信任传播** | 19 |
| 🔴 | B52 | **Structured Output Guarantee — LLM 输出强制校验+自动重试** | 19 |
| 🟠 | B53 | **LLM API 专属速率限制 + Provider 降级** | 19 |
| 🟠 | B54 | **Tool Call Parameter Validation — 工具调用参数护栏** | 20 |
| 🟡 | B55 | **Prompt Caching Strategy — 上下文缓存策略** | 20 |
| 🟡 | B56 | **Multi-Provider Semantic Equivalence Fallback** | 20 |



### 14.3 Shared 层准入边界规则

> 为防止 shared/ 膨胀为垃圾场，新增模块进入 shared/ 必须同时满足：
> 1. 被 ≥2 个基础设施域模块消费（或预期会被消费）
> 2. 不绑定任何特定业务域
> 3. 接口粒度 ≤ Protocol/dataclass/Enum（不包含重量级实现）

---



## 16. KB 决策记录 — 架构决策记录（Architecture Decision Records）

> 本节记录 Shared+Core 的关键架构决策及其 trade-off。AD 格式参照 adr.github.io。

### AD-001: Pydantic V2 作为跨层数据契约基座

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | 所有跨层数据模型使用 Pydantic V2 BaseModel，不用 Python dataclasses 或 raw dict |
| **原因** | ① 自动序列化/反序列化（to_dict/from_dict 由 serialization.py 统一；Decimal→str 自动处理）② 运行时类型校验（避免 dict key typo 在生产崩掉）③ 与 FastAPI/ShieldLM/PydanticAI 生态正交兼容 ④ AI 施工友好——Pydantic schema 即文档，AI 不需要额外查字段含义 |
| **代价** | ① Pydantic V2 导入约增加 50ms 冷启动 ② 跨模块模型耦合（改 Task 影响 10+ 消费者——已由 §7.1 反向依赖索引缓解）③ Pydantic 版本升级可能 BREAKING——由 `check_shared_version()` 运行时版本协商兜底 |
| **替代方案** | Python dataclasses（缺自动校验 / JSON 序列化需手写）；TypedDict（缺校验 / 工具链支持弱）；Protocol Buffers（过度工程 / 无生产需求） |

### AD-002: Shared + Core 合并为单一蓝图

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | MOD-INF-016 同时涵盖 `src/zephyr/shared/` 和 `src/zephyr/core/`，不拆分为两个独立蓝图 |
| **原因** | ① 两者体积均较小（shared 46 文件 + core 3 文件 = 49 文件——独立蓝图的最低门槛是 30+ 文件）② 强耦合——core/models.py 继承 shared/schemas.py，拆分后 AI 需同时读两份蓝图做 cross-reference ③ 两者均为跨层基础设施，功能域一致 |
| **拆分触发条件** | shared 文件数 >80 或 core 模块独立形成 3+ 个子系统——届时拆分 |
| **替代方案** | 独立两个蓝图（当前体积下 over-engineering——AI session 冷启动需多读一份 blueprint.md + 多维护一份 registry entry） |

### AD-003: Resilience 组件使用纯内存（非 SQLite 持久化）

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | `shared/resilience/` 的 CircuitBreaker/Retry/FallbackChain 全部纯内存，不持久化 |
| **原因** | ① 持久化版在 `gates/circuit_breaker.py`——SQLite + 门禁集成。两版分工：shared 版给 AI agent 内部重试（零依赖、快速恢复），gates 版给生产请求门禁（持久化、可审计）② 纯内存避免依赖 SQLite——shared 是最底层，不应有 DB 依赖 ③ 熔断状态半衰期短（30s）——持久化收益低 |
| **代价** | 进程重启 → 熔断状态丢失 → burst 期间可能重复请求已熔断的服务（由 retry + timeout 兜底） |

### AD-004: Prompt/Skill 注册表不在 shared/ 而在 context_engine/

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | B34 标记的 Skill/Prompt 注册表缺在 shared/——但当前 `prompt_registry.py` 放在 `context_engine/` 是合理的设计决策，非盲点 |
| **原因** | ① Prompt 模板与业务语义紧耦合（"为 Task 生成执行计划" vs "为 KB entry 生成摘要"）——不适合作为 shared/ 通用抽象 ② Skill 注册与 Agent Identity 强绑定——归属 agent-rbac 或 context_engine ③ shared/ 只提供通用 PromplTemplate/Skill Schema（Pydantic 模型），具体注册表由业务模块承载 |
| **shared/ 职责** | 当 context_engine 和 agent-rbac 和 feedback_loop 三个模块都需要 `PromptTemplate` / `SkillDefinition` 数据模型时，将其提升到 shared/ |

### AD-005: shared_quickref.yaml 是 AI 派生文件（非 SSoT）

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | `shared_quickref.yaml` 是从 `__init__.py` `__all__` 派生出的 AI 快速导航文件，无消费者依赖 |
| **原因** | ① AI session 冷启动时读 QUICKREF 比 grep `__all__` 快 ② 包含 anti_patterns / entry_point 等 AI 专属信息——`__all__` 不承载 ③ 是 blueprint.md 的速览版本——AI 读完 blueprint 后对照 QUICKREF 快速定位 |
| **更新策略** | 每次新增 shared/ 模块 → `__init__.py` `__all__` → QUICKREF（两步更新）。QUICKREF 落后 `__all__` ≤1 个 session 可接受（AI 查 QUICKREF 后仍会 verify `__init__.py`） |

---

## 17. Consumer Onboarding Guide — 新模块接入指南

> **面向**: 下一个 AI session 冷启动 + 新基础设施域模块接入 shared/

### 17.1 最小接入（3 行 import 即用）

```python
from zephyr.shared.schemas import Task, TaskStatus       # 所有模块都需要
from zephyr.shared.paths import REPO_ROOT, DB_PATH       # 路径从 SSoT 获取
from zephyr.shared.logging import get_logger             # 结构化日志 + trace_id 传播

logger = get_logger(__name__)
```

### 17.2 shared/ 按消费场景的分层

| 层级 | 模块 | 适用场景 | 示例 |
|:---:|------|------|------|
| L0 必选 | schemas, paths, logging | 所有模块 | `from zephyr.shared.schemas import Task` |
| L1 常用 | time_utils, token_utils, frontmatter_utils, errors, types | 需要时间/Token/Frontmatter/异常/类型安全的模块 | `from zephyr.shared.time_utils import now_utc` |
| L2 生产 | serialization, api_client, secrets, cache, limiter, idempotency, context, metrics, pagination, env, lock, outbox, schema_registry | 对外 API / 持久化 / 性能敏感的模块 | `from zephyr.shared.cache import MemoryCache` |
| L3 韧性 | resilience/*, lifecycle/* | 需要重试/熔断/生命周期管理的模块 | `from zephyr.shared.resilience.retry import async_retry` |
| L4 AI 专属 | （Phase 11-20 施工完成后） | AI agent 模块 | `from zephyr.shared.cost_budget import CostBudget` |
| facade | contracts/* | 需要跨层结构化数据交换的模块 | `from zephyr.shared.contracts.market.instrument import Instrument` |

### 17.3 不做什么（Anti-patterns）

| ❌ 不要 | ✅ 应该 |
|------|------|
| `from zephyr.shared import *` | 显式 import 需要的符号——AI session 和 mypy 都需要知道 "这个模块用了 shared 的哪些" |
| 直接修改 `task.status = TaskStatus.DONE` | 用 `task.mark_completed()` 等语义化方法——由 models.py v0.4.0 提供 |
| `datetime.utcnow()` 裸用 | `from zephyr.shared.time_utils import now_utc`——唯一 UTC 入口，可测试 |
| 在模块中定义自己的路径常量 | `from zephyr.shared.paths import REPO_ROOT, DB_PATH`——paths.py 是 SSoT |
| 在模块中自己写 `logger = logging.getLogger()` | `from zephyr.shared.logging import get_logger`——trace_id 自动传播 |

### 17.4 版本兼容性策略

| shared/ 版本变更类型 | 影响 | 消费者需做什么 |
|------|------|------|
| PATCH (0.14.X) | 新增文件/新增导出/修复 bug——完全向后兼容 | 无需操作 |
| MINOR (0.X.0) | 新增文件≥5 / 新增子模块——向后兼容，新增可选符号 | AI session 可选择性采用新模块 |
| MAJOR (X.0.0) | 破坏 Task 31字段 / 删除导出 / 重命名模块 | 全部基础设施域模块 MUST 同步升级——check_shared_version() 运行时阻断不兼容版本 |

---

## 18. Blueprint Quality Self-Assessment — 蓝图质量自评

> **评估标准**: 蓝图作为 AI 独立施工规格说明书的质量。100% AI 施工 + 1人+AI 维护语境。

### 18.1 可实施性评分（每个 planned phase）

| Phase | 盲点 | 蓝图细节完备度 | AI 独立施工评分 | 缺口 |
|:---:|------|:---:|:---:|------|
| 11 | B26, B28 | 🟢 详细 | 8/10 | B28 token_utils.py 已存在——施工复杂度低。B26 成本预算需明确 provider 定价数据来源 |
| 12 | B29, B32 | 🟢 详细 | 8/10 | B29 Evals 框架需定义 eval 用例格式。B32 Session audit 需明确 JSONL 格式 |
| 13 | B30, B31 | 🟡 中等 | 7/10 | B30 Durable Execution 需明确 Worker/Activity 抽象层。B31 后处理管道需 hook 点设计 |
| 14 | B27, B33, B34 | 🟡 中等 | 6/10 | B33 Multi-Agent 编排最复杂——需在蓝图补充 AgentCard / TaskDispatch / ResultMerge 三个 Protocol |
| 15 | B35-B40 | 🟡 中等 | 7/10 | 6 项规模适中，但 B39 DI 容器需 explicit constructor injection 约定 |
| 16 | B41, B42 | 🟢 详细 | 8/10 | AIBOM/Memory Bank 均为接口定义级——200-300 行 Protocol + dataclass |
| 17 | B43-B45 | 🟡 中等 | 7/10 | B43 DSPy 声明式优化——声明式 Signature 语法设计是关键决策 |
| 18 | B46-B50 | 🟡 中等 | 7/10 | 5 项但 KG 接口 + Drift 检测可能不满足 shared/ 准入规则——需再判断 |
| 19 | B51-B53 | 🟡 中等 | 7/10 | B51 Prompt 注入防御——IFC 标签系统需 Microsoft FIDES 参考实现 |
| 20 | B54-B56 | 🟢 详细 | 8/10 | 3 项均为薄封装（100-200 行接口定义）|

### 18.2 蓝图漂移风险自评

| 风险 | 当前评分 | 缓解 |
|------|:---:|------|
| 蓝图声称的 49 文件 vs 磁盘实际 | 🟢 低 | §5 文件清单 49 文件全 ✅，IC1/IC2 已修复 |
| `__all__` 导出数 vs QUICKREF | 🟢 低 | 当前 223 导出——Phase 11-20 新增后需同步更新 |
| Phase 0-10 代码 vs Phase 11-20 planned | N/A | planned phases 无磁盘代码——零漂移风险 |
| blueprint.md vs SSoT YAML (b_shared.yaml/b_core.yaml) | 🟡 中 | blueprint.md 是真源派生的施工文档——YAML 是 canon。两者版本号应同步 |

### 18.3 蓝图完整度矩阵

| 维度 | 状态 | 评分 |
|------|:---:|:---:|
| 文件清单（§5） | ✅ 49 文件全部 indexed | 10/10 |
| 盲点覆盖（§12-§14） | ✅ 56 盲点，25 已实现 (Phase 0-10)，31 planned (Phase 11-20) | 10/10 |
| 施工阶段（§4） | ✅ Phase 0-20 全部 planned | 10/10 |
| 依赖追踪（§7.1） | ✅ 12 消费者模块全部 traced | 9/10 |
| AI 安全护栏（§7.1 底部） | ✅ 按文件/子模块粒度 | 10/10 |
| 架构决策（§16 KB 决策记录） | 🟢 新增——5项 AD | 7/10 ← 尚缺 |
| 消费者指南（§17 Onboarding） | 🟢 新增 | 7/10 ← 尚缺 |
| 蓝图质量自评（§18 本节） | 🟢 新增 | 6/10 ← 需每个 Phase 施工后更新 |
| 测试策略（§19 待施工） | 🟡 待补充 | — |

---

## 19. Shared Layer Testing Strategy — 共享层测试策略

> **目标**: shared/ 作为全系统基础设施，其测试覆盖直接影响所有基础设施域模块的施工信心。

### 19.1 测试分层

| 层 | 范围 | 目标覆盖率 | 当前状态 |
|:---:|------|:---:|:---:|
| **单元测试** | 每个 shared/*.py 的纯函数/类——不依赖外部（无 DB、无 HTTP、无文件系统） | ≥90% | 7 文件已测试（schemas/ssot_guard/capability/money/instrument + contract tests）——**缺 42 文件** |
| **集成测试** | shared/ 子模块间的交互——e.g., `context.py` + `logging.py` trace_id 传播 → 日志输出包含 trace_id | ≥70% | 未开始 |
| **契约测试** | 6 消费者模块 import shared → 所有符号可成功 import + Task 31字段稳定性快照 | 100% | ✅ 29/29 通过（§5.2）。每次新增 shared 符号 MUST 更新 `test_import_chain.py` |
| **性能回归测试** | cache/limiter/serializer 的操作耗时基准——e.g., `MemoryCache.put()` < 10µs、`to_json()` 100KB < 50ms | P95 不退化 | 未开始 |
| **漂移检测** | 蓝图 §5 声称的 49 文件 vs 磁盘实际 vs `__init__.py` `__all__` | 三者一致 | ✅ 本轮修复 IC1/IC2 后一致 |

### 19.2 单元测试优先级（TOP 10 缺测试文件）

> 按"被消费者引用次数"×"修改频率"排序

| 优先级 | 文件 | 被引用次数 | 建议第一个测试 |
|:---:|------|:---:|------|
| 1 | `cache.py` | — | `test_cache_ttl_expiry()` |
| 2 | `limiter.py` | — | `test_token_bucket_consume()` |
| 3 | `serialization.py` | — | `test_to_dict_decimal_handling()` |
| 4 | `idempotency.py` | — | `test_idempotency_key_determinism()` |
| 5 | `context.py` | — | `test_contextvars_propagation()` |
| 6 | `metrics.py` | — | `test_counter_thread_safety()` |
| 7 | `api_client.py` | — | `test_timeout_retry_composition()` |
| 8 | `pagination.py` | — | `test_cursor_pagination()` |
| 9 | `lock.py` | — | `test_memory_lock_lease_expiry()` |
| 10 | `outbox.py` | — | `test_outbox_polling_publisher()` |

### 19.3 性能回归基准（建议值）

| 操作 | P50 | P95 | P99 |
|------|-----|-----|-----|
| `MemoryCache.put()` | <5µs | <10µs | <20µs |
| `TokenBucketLimiter.consume()` | <1µs | <5µs | <10µs |
| `to_json(obj, 100KB)` | <10ms | <50ms | <100ms |
| `IdempotencyStore.start(key)` | <5µs | <10µs | <15µs |
| `MetricsRegistry.get_or_create_counter()` | <1µs | <3µs | <5µs |

### 19.4 测试维护策略

| 触发事件 | 操作 |
|------|------|
| 新增共享模块 | 新增单元测试 + 更新 `test_import_chain.py` + 更新 QUICKREF |
| 修改已有模块签名 | MUST 运行 `test_import_chain.py`（跨模块 import）+ `test_schema_stability.py`（Task 31字段快照） |
| 性能敏感模块变更（cache/limiter/serializer） | MUST 运行性能回归 + 比较 P50/P95 |
| 蓝图 Phase 11-20 每完成一个 | MUST 新增对应测试 + 更新 §19.2 优先级表 + 更新蓝图完整度矩阵（§18.3）

---

## §17 容量升级

### 17.1 当前容量基线

| 资源 | 设计目标 | 测量方式 |
|------|---------|---------|
| 模块数 | 1,500 | blueprint_registry.yaml |
| 脚本数 | 10,000 | script-manifest.yaml |
| AI 并发 | 100 Session | 运行时监控 |
| 内存 | 64GB（单机 i7-12700KF） | psutil |
| GPU | RTX 3090 24GB VRAM | nvidia-smi |

### 17.2 扩展触发条件

| 触发条件 | 组件 | 动作 |
|---------|------|------|
| 并发写入 > 10/s | SQLite | WriteBatcher 批量合并（暂缓待 L 级） |
| AI Session > 100 | MemoryCache | per-session L1 + shared L2 双层 |
| 模块 > 1,500 | Metrics | Label 白名单 + Lock-Free Counter |
| 并发 API 调用 > 20 | HTTP Client | per-provider 独立连接池 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-INF016-06 | ThreadPoolExecutor 替代串行 subprocess | ThreadPool / multiprocessing / serial | ThreadPool | I/O密集型+GIL无影响+轻量 | 2026-05-07 |
| 2 | AD-001 | 跨层数据契约基座 | Pydantic V2 / dataclasses / TypedDict / Protocol Buffers | Pydantic V2 | 自动校验/序列化/AI友好 | 2026-05-05 |
| 3 | AD-002 | Shared+Core 蓝图合并 vs 拆分 | 合并 / 拆分独立蓝图 | 合并 | 体积均<80文件+强耦合 | 2026-05-05 |
| 4 | AD-003 | Resilience 持久化策略 | 纯内存 / SQLite持久化 | 纯内存 | 零DB依赖+gates已有持久化版 | 2026-05-05 |
| 5 | AD-005 | shared_quickref 派生文件定位 | AI派生文件 / SSoT | AI派生文件 | 从__all__派生，无消费者依赖 | 2026-05-05 |
| 6 | AD-004 | Skill/Prompt注册表归属 | shared/ / context_engine/ | context_engine | Prompt模板与业务语义紧耦合 | 2026-05-05 |

> AD-001~AD-005 详细决策记录 → [§16 KB 决策记录](#16-adr--架构决策记录architecture-decision-records)

---

## 已知技术债务（2026-05-08 审计 · Session-20260508-001）

### TD-SHARED-001: 37文件发散副本（Phase 11 待修）

| 维度 | 内容 |
|------|------|
| 问题 | 37 模块同时存在于顶层目录和子目录，内容是非 byte-identical 发散副本，非 re-export wrapper |
| 风险 | 修改不同步 → 行为不一致；路径混乱 → AI 认知错误；典型案例 `shared/cache.py`(5595B) ≠ `shared/infra/cache.py`(5560B) |

**规范路径策略（Phase 11 施行）**:
| 顶层文件 | 规范子目录路径 | 处置 |
|----------|--------------|------|
| `cache.py` | `infra/cache.py` | 顶层改为 re-export wrapper |
| `metrics.py` | `observability/metrics.py` | 顶层改为 re-export wrapper |
| `logging.py` | `observability/logging.py` | 顶层改为 re-export wrapper |
| `health.py` | `observability/health.py` | 顶层改为 re-export wrapper |
| `token_utils.py` | `observability/token_utils.py` | 顶层改为 re-export wrapper |
| `tracing.py` | `observability/tracing.py` | 顶层改为 re-export wrapper |
| `idempotency.py` | `infra/idempotency.py` | 顶层改为 re-export wrapper |
| `limiter.py` | `infra/limiter.py` | 顶层改为 re-export wrapper |
| `lock.py` | `infra/lock.py` | 顶层改为 re-export wrapper |
| `observer.py` | `infra/observer.py` | 顶层改为 re-export wrapper |
| `outbox.py` | `infra/outbox.py` | 顶层改为 re-export wrapper |
| `serialization.py` | `io/serialization.py` | 顶层改为 re-export wrapper |
| `content_fingerprint.py` | `io/content_fingerprint.py` | 顶层改为 re-export wrapper |
| `file_utils.py` | `io/file_utils.py` | 顶层改为 re-export wrapper |
| `frontmatter_utils.py` | `io/frontmatter_utils.py` | 顶层改为 re-export wrapper |
| `paths.py` | `io/paths.py` | 顶层改为 re-export wrapper |
| `errors.py` | `foundation/errors.py` | 顶层改为 re-export wrapper |
| `constants.py` | `foundation/constants.py` | 顶层改为 re-export wrapper |
| `flags.py` | `foundation/flags.py` | 顶层改为 re-export wrapper |
| `types.py` | `foundation/types.py` | 顶层改为 re-export wrapper |
| `deprecation.py` | `foundation/deprecation.py` | 顶层改为 re-export wrapper |
| `env.py` | `foundation/env.py` | 顶层改为 re-export wrapper |
| `secrets.py` | `security/secrets.py` | 顶层改为 re-export wrapper |
| `capability.py` | `security/capability.py` | 顶层改为 re-export wrapper |
| `ssot_guard.py` | `security/ssot_guard.py` | 顶层改为 re-export wrapper |
| `migration.py` | `utils/migration.py` | 顶层改为 re-export wrapper |
| `pagination.py` | `utils/pagination.py` | 顶层改为 re-export wrapper |
| `time_utils.py` | `utils/time_utils.py` | 顶层改为 re-export wrapper |
| `context.py` | `utils/context.py` | 顶层改为 re-export wrapper |
| `testing.py` | `utils/testing.py` | 顶层改为 re-export wrapper |
| `diff_utils.py` | `utils/diff_utils.py` | 顶层改为 re-export wrapper |
| `blueprint_scorer.py` | `utils/blueprint_scorer.py` | 顶层改为 re-export wrapper |
| `schemas.py` | `schema/schemas.py` | 顶层改为 re-export wrapper |
| `schema_registry.py` | `schema/schema_registry.py` | 顶层改为 re-export wrapper |
| `api_client.py` | `api/api_client.py` | 顶层改为 re-export wrapper |
| `dos_launcher.py` | `api/dos_launcher.py` | 顶层改为 re-export wrapper |

**施行方法**: 每个顶层文件替换为 `from zephyr.shared.<subdir>.<module> import *` wrapper。
**不影响消费者**: 316 处现有引用全部保持兼容。

### TD-SHARED-002: `__init__.py` 导入路径不一致（已部分修复）

`__init__.py` 中 ~33 个 import 使用顶层路径（`from zephyr.shared.cache import`），
~16 个使用规范子目录路径（`from zephyr.shared.api.api_client import`）。
TD-SHARED-001 修复完成后，统一改为子目录路径。

## ⚠️ Vibe Coding 蓝图编写铁律

> 以下铁律来自实战经验。违反任何一条都可能导致后续 AI 施工时出现幻觉、路径漂移、执行失败。
> 本蓝图已合并蓝图（设计）和施工指引（实施）。
> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | 蓝图必须是最终设计结果——不记录决策过程 | 蓝图过厚，关键信息被噪音淹没 |
| 3 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移——AI 自行决定，可能选错 |
| 4 | 蓝图必须自包含——关键信息不能只写"详见XX" | 信息缺失——AI 缺少关键上下文 |
| 5 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 6 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 7 | 容量估算必须写 | AI 不知道系统能容纳多少，可能设计出无法扩展的方案 |
| 8 | 迁移/废弃方案必须写 | AI 不知道旧东西怎么处理，可能直接删除或保留 |
| 9 | 必备链接不可省略——即使与前序文档重复也必须完整列出 | AI 每次新 session 是零记忆，不记得前序文档写了什么 |
| 10 | 产出物路径必须与 GOV-DOC-002 一致 | AI 不知道项目目录规范，会自行创建路径 |
| 11 | 涉及文件范围必须明确列出 | AI 不知道边界在哪，会越界修改 |
| 12 | 删除文件必须遵守安全删除协议——禁止直接删除任何文件 | 没有git备份，删除不可逆 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 代码文件是 SSoT，蓝图复制代码=双源漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

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

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| 本蓝图已达 1100+ 行，Shared + Core 均为跨层基础设施 | **原地** | 服务对象相同（所有基础设施-实验模块）+ 变更频率同步 + 依赖关系完全重叠 |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。

## 必备链接

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表、frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射、边界判据 |
| 3 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 4 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 5 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 6 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

## 项目中已有类似功能

无。

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | shared/ | `D:\ZephyrAlpha\src\zephyr\shared\` | 修改/扩展 | 容量升级 + 新增模块 |
| 2 | core/ | `D:\ZephyrAlpha\src\zephyr\core\` | 修改/扩展 | 容量升级 + 新增模块 |
| 3 | shared/infra/process_lifecycle_gateway.py | `D:\ZephyrAlpha\src\zephyr\shared\infra\process_lifecycle_gateway.py` | 新增 | ProcessLifecycleGateway 统一入口 |
| 4 | gates/invariants/en_process_lifecycle_gateway.py | `D:\ZephyrAlpha\src\zephyr\gates\invariants\en_process_lifecycle_gateway.py` | 新增 | 进程创建入口校验门禁 |
| 5 | 测试 | `D:\ZephyrAlpha\tests\` | 新增 | 对应新模块的单元测试 |
