---
module_id: "MOD-INF-032"
title: "资源优化引擎蓝图"
doc_type: blueprint
status: Active
version: "1.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-08"
ttl: permanent
construction_progress: phase_1_5_complete
summary: "桌面级自主计算引擎——MAPE-K 循环驱动的资源监控、分析、优化与自愈系统。一个系统包含两个策略引擎：防御引擎（应急保护）和优化引擎（主动提效），共享感知层、执行层和知识层。在保证服务质量的前提下，主动优化 CPU/内存/磁盘 I/O/进程资源使用。"
tags: [autonomic-computing, mape-k, resource-optimization, aiops, process-supervision, observability, circuit-breaker, backpressure, graceful-degradation, self-healing]
priority: P1
belongs_to: "MOD-MASTER-001"
rule_form: structural
scope: global
stability: evolving
verifiability: automated
depends_on:
  - MOD-INF-016  # shared-core (daemon_registry, event_bus, lifecycle)
  - MOD-INF-015  # system-telemetry (metrics, health probes)
  - MOD-INF-009  # pipeline (pipeline_lock, orchestration)
  - MOD-INF-010  # feedback-loop (scheduler, detectors)
  - MOD-INF-007  # gate-engine (gate rules for resource checks)
  - MOD-INF-020  # audit-trail (optimization action audit)
  - MOD-INF-023  # drift-detector (resource config drift)
  - MOD-INF-024  # budget-enforcer (resource cost budget)
  - MOD-INF-019  # agent-spec (skill registration)
  - MOD-INF-013  # mcp-servers (MCP tool exposure)
responsibility_domain: "resource_optimization"
blueprint_level: module
---

# 资源优化引擎 蓝图 + 施工指引

> module_id: MOD-INF-032 | version: 1.1.0 | status: Active | layer: cross_layer

---

## ⚠️ Vibe Coding 蓝图编写铁律

> AI 编写蓝图时**必须**逐条确认已遵守。

| # | 铁律 | 已遵守 |
|---|------|:------:|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | ✅ |
| 2 | 必备链接不可省略 | ✅ |
| 3 | 蓝图必须是最终设计结果 | ✅ |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | ✅ |
| 5 | 涉及文件范围必须明确列出 | ✅ |
| 6 | 容量估算必须写 | ✅ |
| 7 | 迁移/废弃方案必须写 | ✅ |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | ✅ |
| 9 | 蓝图必须自包含 | ✅ |
| 10 | 删除文件必须遵守安全删除协议 | ✅ |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。仅新增文件和修改现有文件。

---

## 必备链接

| # | 链接 | 路径 |
|---|------|------|
| 1 | DaemonRegistry 现有实现 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` |
| 2 | EventBus 现有实现 | `D:\ZephyrAlpha\src\zephyr\shared\event_bus.py` |
| 3 | ContractBus 现有实现 | `D:\ZephyrAlpha\src\zephyr\shared\contract_bus.py` |
| 4 | API_INDEX 现有实现 | `D:\ZephyrAlpha\src\zephyr\shared\API_INDEX.py` |
| 5 | FeedbackLoopScheduler | `D:\ZephyrAlpha\src\zephyr\feedback_loop\scheduler.py` |
| 6 | ResourceGuard | `D:\ZephyrAlpha\src\zephyr\drift_detector\resource_guard.py` |
| 7 | SelfMonitor | `D:\ZephyrAlpha\src\zephyr\audit_trail\self_monitor.py` |
| 8 | AuditWriter | `D:\ZephyrAlpha\src\zephyr\audit_trail\writer.py` |
| 9 | CollectionManager | `D:\ZephyrAlpha\src\zephyr\vector_memory\collection_manager.py` |
| 10 | ContextBudgetTracker | `D:\ZephyrAlpha\src\zephyr\context_engine\context_budget_tracker.py` |
| 11 | HeartbeatServer | `D:\ZephyrAlpha\src\zephyr\shared\heartbeat_server.py` |
| 12 | Lifecycle hooks | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\hooks.py` |
| 13 | MCP Gateway | `D:\ZephyrAlpha\src\zephyr\mcp\gateway_server.py` |
| 14 | 蓝图模板 | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md` |
| 15 | 蓝图架构标准 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\blueprint-architecture-standard.md` |
| 16 | 元数据注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` |
| 17 | 目录结构标准 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` |
| 18 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` |
| 19 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` |
| 20 | 模块注册表 | `D:\ZephyrAlpha\docs\03_modules\module-registry.yaml` |
| 21 | 蓝图路由表 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` |
| 22 | 技能注册表 | `D:\ZephyrAlpha\src\zephyr\agent_spec\skill_registry.yaml` |
| 23 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` |
| 24 | SLI 注册表 | `D:\ZephyrAlpha\config\sli_registry.yaml` |
| 25 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` |
| 26 | 集成闭环总蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master-blueprint\blueprint.md` |
| 27 | 系统总蓝图 | `D:\ZephyrAlpha\docs\03_modules\_sys-master\blueprint.md` |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | ResourceGuard | `D:\ZephyrAlpha\src\zephyr\drift_detector\resource_guard.py` | 磁盘空间监控 + os.walk 扫描 | ResourceGuard 只做磁盘监控和文件扫描，无 CPU/内存/进程池/缓存/调度优化能力，且自身就是资源浪费源（每5秒全量扫描） |
| 2 | DaemonRegistry | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` | 守护线程注册 | DaemonRegistry 只做注册，无压力感知、无自适应调度、无优先级驱动的启停策略。本蓝图升级 DaemonRegistry 而非替换 |
| 3 | ContextBudgetTracker | `D:\ZephyrAlpha\src\zephyr\context_engine\context_budget_tracker.py` | Token 预算管理 | ContextBudgetTracker 只管 Token 预算，不管系统级资源（CPU/内存/磁盘/进程）。两者互补不重叠 |
| 4 | CapacityAssurance (MOD-INF-001) | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\capacity-assurance\blueprint.md` | 容量规划 + 限流 | MOD-INF-001 做容量规划（事前），本蓝图做运行时资源优化（事中+事后）。MOD-INF-001 回答"系统能承载多少"，本蓝图回答"当前资源怎么用得更好" |
| 5 | BudgetEnforcer (MOD-INF-024) | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\budget-enforcer\blueprint.md` | 预算执行 + 降级 | BudgetEnforcer 管 Token/Cost/Time 三维预算，本蓝图管 CPU/Memory/Disk/Process 四维系统资源。BudgetEnforcer 的降级策略可触发本蓝图的自适应调度 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 资源优化引擎主模块 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\resource_optimization_engine.py` | 新建 | 新建 |
| 1a | 数据模型（v1.1.0 拆分） | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\resource_optimization_models.py` | 新建 | 新建 |
| 2 | 守护线程注册表 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` | 读取+修改 | 修改 |
| 3 | I/O 缓存层 | `D:\ZephyrAlpha\src\zephyr\shared\io\io_cache.py` | 新建 | 新建 |
| 4 | 流式读取工具 | `D:\ZephyrAlpha\src\zephyr\shared\io\streaming_reader.py` | 新建 | 新建 |
| 5 | 进程池管理器 | `D:\ZephyrAlpha\src\zephyr\shared\infra\process_pool.py` | 新建 | 新建 |
| 6 | 懒加载器 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\lazy_loader.py` | 新建 | 新建 |
| 7 | 资源优化配置 | `D:\ZephyrAlpha\config\resource_optimization.yaml` | 新建 | 新建 |
| 8 | lifecycle __init__ | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\__init__.py` | 修改 | 修改 |
| 9 | io __init__ | `D:\ZephyrAlpha\src\zephyr\shared\io\__init__.py` | 修改 | 修改 |
| 10 | FLE Scheduler | `D:\ZephyrAlpha\src\zephyr\feedback_loop\scheduler.py` | 修改 | 修改 |
| 11 | LocalModelScheduler | `D:\ZephyrAlpha\src\zephyr\vector_memory\local_model_scheduler.py` | 修改 | 修改 |
| 12 | SelfMonitor | `D:\ZephyrAlpha\src\zephyr\audit_trail\self_monitor.py` | 修改 | 修改 |
| 13 | CircadianScheduler | `D:\ZephyrAlpha\src\zephyr\runtime\circadian_scheduler.py` | 修改 | 修改 |
| 14 | AutoEvolution | `D:\ZephyrAlpha\src\zephyr\feedback_loop\auto_evolution.py` | 修改 | 修改 |
| 15 | infra __init__ | `D:\ZephyrAlpha\src\zephyr\shared\infra\__init__.py` | 修改 | 修改 |
| 16 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 修改 | 修改 |
| 17 | 模块注册表 | `D:\ZephyrAlpha\docs\03_modules\module-registry.yaml` | 修改 | 修改 |
| 18 | 蓝图路由表 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | 修改 | 修改 |
| 19 | 技能注册表 | `D:\ZephyrAlpha\src\zephyr\agent_spec\skill_registry.yaml` | 修改 | 修改 |
| 20 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | 修改 | 修改 |
| 21 | 模块ID注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | 修改 | 修改 |
| 22 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | 修改 | 修改 |
| 23 | SLI 注册表 | `D:\ZephyrAlpha\config\sli_registry.yaml` | 修改 | 修改 |
| 24 | MCP 工具契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool_contracts.yaml` | 修改 | 修改 |
| 25 | 基础设施注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure-registry.yaml` | 修改 | 修改 |
| 26 | 目录注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\directory-registry.yaml` | 修改 | 修改 |
| 27 | 系统路径注册表 | `D:\ZephyrAlpha\docs\03_modules\system-pathway-registry.yaml` | 修改 | 修改 |
| 28 | 单元测试（引擎） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_engine.py` | 新建 | 新建 |
| 29 | 单元测试（缓存） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_io_cache.py` | 新建 | 新建 |
| 30 | 单元测试（流式读取） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_streaming_reader.py` | 新建 | 新建 |
| 31 | 单元测试（进程池） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_process_pool.py` | 新建 | 新建 |
| 32 | 单元测试（懒加载） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_lazy_loader.py` | 新建 | 新建 |
| 33 | 单元测试（自愈闭环） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_self_healing.py` | 新建 | 新建 |
| 34 | 蓝图文档 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\resource-optimization-engine\blueprint.md` | 本文件 | 修改 |

---

## 1. 设计背景与目标

### 背景

2026-05-08 事件：Trae 开启 10 个对话后，系统出现以下问题：
1. **180 个 Python 进程**占用 19.15 GB 内存（每个 MCP 服务器进程 ~115MB）
2. AuditWriter 每次写日志**读全量→写全量→替换文件**，磁盘 I/O 阻塞
3. ResourceGuard 每 5 秒 `os.walk()` 遍历整个项目目录
4. 多个后台守护线程无退出机制、无单例保护、无资源限制
5. 系统卡死 → Trae 报 -2 错误 → 所有对话崩溃

根因：**没有统一的资源优化系统**——各模块各自为政，无全局视角，无主动优化，只有被动降级。

### 目标

| # | 目标 | 衡量标准 |
|---|------|---------|
| G1 | **进程资源池化**——MCP 服务器进程跨对话共享，而非每对话独立启动 | 10 对话时 Python 进程数从 180 降至 ≤20 |
| G2 | **I/O 零拷贝优化**——消除"读全量→写全量"模式 | AuditWriter 单次写入延迟从 O(n) 降至 O(1) |
| G3 | **智能调度**——后台守护线程按需启动、按优先级调度 | FLE-Scheduler 空闲时段 CPU 占用从 30% 降至 <5% |
| G4 | **内存水位管理**——主动监控+提前优化，而非等内存满了再降级 | 内存使用率超过 75% 时自动触发优化，95% 前完成 |
| G5 | **缓存复用**——YAML/JSONL 解析结果缓存，避免重复 I/O | 同一 YAML 文件 30 秒内重复读取命中缓存率 ≥90% |
| G6 | **流式处理**——大文件读取改为流式/尾部读取 | _load_events_raw(limit=100) 内存占用从 O(n) 降至 O(limit) |
| G7 | **自愈闭环**——资源异常自动检测→诊断→优化→验证 | 资源异常从检测到恢复 ≤60 秒，无需人工干预 |
| G8 | **AI 可发现**——任何新 AI session 都能自动定位并使用资源优化能力 | 通过蓝图路由+技能注册+MCP工具三重发现，0 次人工指引 |

### 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | GPU 监控与优化 | 当前系统不使用 GPU |
| 2 | 网络带宽优化 | 桌面环境非瓶颈 |
| 3 | 容器化/虚拟化资源隔离 | 超出桌面级范围 |
| 4 | 业务算法优化 | 不改变算法正确性，只优化资源使用方式 |
| 5 | 安全策略执行 | 不做权限控制，归属 MOD-INF-018 |

---

## 2. 模块边界

### 职责范围

| # | 职责 | 描述 |
|---|------|------|
| 1 | 资源快照采集 | 定期采集 CPU/内存/磁盘/进程/线程指标 |
| 2 | 压力分级 | 将资源状态分为 NORMAL/WARNING/CRITICAL/EMERGENCY 四级 |
| 3 | **防御策略引擎** | 应急保护：EMERGENCY/CRITICAL 时停止非必要服务、释放内存、保护核心功能 |
| 4 | **优化策略引擎** | 主动提效：NORMAL/WARNING 时进程池复用、缓存预热、批量 I/O、自适应调度 |
| 5 | 优化策略执行 | 根据压力等级执行对应的优化策略（非降级——是更聪明的资源使用） |
| 6 | 守护线程注册表 | 统一注册、启停、优先级管理所有后台守护线程 |
| 7 | I/O 优化 | 缓存层 + 流式读取 + append-only 写入 + 批量合并 |
| 8 | 进程池管理 | MCP 服务器进程跨对话共享，限制最大进程数 |
| 9 | 优化历史 | 记录优化动作和效果，供 MAPE-K Knowledge 使用 |
| 10 | 压力状态机 | 管理压力等级转换，含滞后机制防抖动 |
| 11 | 优雅降级矩阵 | 定义每个压力等级下各子系统的行为变化 |
| 12 | 断路器 | 优化动作失败时自动熔断，防止级联故障 |
| 13 | 背压机制 | 优化速度跟不上资源恶化速度时，向上游施加背压 |
| 14 | 自愈闭环 | 资源异常自动检测→诊断→优化→验证的完整闭环 |
| 15 | 配置管理 | 资源阈值、策略参数、调度频率等可配置化 |

#### 架构决策：一个系统，两个策略引擎

> **决策**：防御（Defensive）和优化（Offensive）合为一个系统，内部包含两个策略引擎。
>
> **理由**：
> 1. 共享同一组传感器（ResourceSnapshot），拆分则数据冗余
> 2. 防御和优化需要协调——EMERGENCY 时不能同时做缓存预热（优化）和停止服务（防御）
> 3. 防御和优化是同一频谱的两端，WARNING 时两者都参与，需要统一调度
> 4. 知识库（Knowledge）需要同时看到防御和优化历史，才能做出更好的决策
> 5. 类比：人体自主神经系统（交感+副交感）是一个系统两个控制器，而非两个独立系统
>
> **隔离措施**：两个策略引擎在代码层面独立（不同策略列表、不同触发条件），但共享执行层和知识层
>
> **对标**：IBM Autonomic Computing MAPE-K 架构、Kubernetes HPA+Descheduler 双引擎、Google SRE 自动修复+容量规划双循环

#### 架构决策：1,500 模块容量三大转变

> 当前 47 模块已产生 180 进程 / 19 GB 内存的问题。扩展到 1,500 模块时（×32），
> 如果不进行架构级转变，系统将完全不可用（预估 150,000 进程 / 200 GB 内存）。
> 以下三个转变是支撑 1,500 模块的必要条件。

**转变 1：从"每模块独立进程"到"进程池共享"**

```
现在:  1,500 模块 × 10 对话 × 10 MCP = 150,000 进程  → 不可行
优化后: 10 对话 × 3 共享 MCP 网关 = 30 进程          → 可行
```

> **决策**：MCP 服务器进程不按"对话×模块"维度创建，而是按"服务器类型"维度共享。
> 所有对话共享同一组 MCP 服务器进程，通过请求级隔离（而非进程级隔离）保证状态安全。
>
> **理由**：
> 1. MCP 服务器本质是无状态路由层，进程级隔离是不必要的资源浪费
> 2. 进程池模式在 Kubernetes HPA、数据库连接池中已被广泛验证
> 3. 请求级隔离通过 `request_id` + `session_id` 前缀实现，成本远低于进程级隔离
>
> **风险与缓解**：状态泄漏风险 → 每次 MCP 调用前重置上下文 + 请求级沙箱

**转变 2：从"全量加载"到"按需加载"**

```
现在:  import 1,500 个模块 → 启动时间 5 分钟，内存 200 GB  → 不可行
优化后: 懒加载 + importlib → 只加载当前对话需要的 10 个模块 → 可行
```

> **决策**：模块采用懒加载策略，仅在首次被调用时通过 `importlib.import_module()` 动态导入。
> 系统启动时只加载核心框架（~20 个模块），其余 1,480 个模块按需加载。
>
> **理由**：
> 1. 任何一次对话只需要 5-15 个模块，加载全部 1,500 个是浪费
> 2. Python 的 `importlib` 已原生支持动态导入，无额外依赖
> 3. IDE 的 LSP 服务器也采用同样的懒加载策略（如 Pylance 的 lazy import）
>
> **风险与缓解**：首次调用延迟 → 预热缓存（CACHE_WARM 策略）+ import 预判

**转变 3：从"各自轮询"到"统一调度"**

```
现在:  300 个守护线程各自 while True + sleep  → CPU 碎片化、调度不可控
优化后: 1 个调度器统一管理 300 个任务         → 批量执行、智能排程
```

> **决策**：所有后台守护线程注册到 DaemonRegistry，由统一的 ResourceOptimizationEngine
> 调度器按优先级和时间窗口统一调度。不再允许各模块自行创建 `while True` 循环。
>
> **理由**：
> 1. 300 个独立线程的上下文切换开销约为 300 × 8KB 栈 = 2.4MB，加上调度器内核开销
> 2. 统一调度器可以批量执行（一次 tick 执行多个任务），减少上下文切换
> 3. 统一调度器可以根据压力等级动态调整频率（自适应调度），各自轮询做不到
> 4. 类比：Kubernetes 的 kube-scheduler 统一调度所有 Pod，而非每个 Pod 自行调度
>
> **风险与缓解**：调度器单点故障 → 调度器自身无状态 + 崩溃自动重启 + 守护线程仍为 daemon

### 不包含的职责

| # | 不包含 | 原因 | 归属 |
|---|--------|------|------|
| 1 | 业务逻辑优化 | 不改变算法正确性 | 各业务模块 |
| 2 | 安全策略执行 | 不做权限控制 | MOD-INF-018 (agent-rbac) |
| 3 | 日志审计记录 | 不做审计记录存储 | MOD-INF-015 (telemetry) |
| 4 | 错误恢复/重试 | 不做业务级重试 | MOD-INF-009 (pipeline) |
| 5 | 容量规划 | 不做事前容量规划 | MOD-INF-001 (capacity-assurance) |
| 6 | Token/Cost 预算 | 不做 LLM 调用预算 | MOD-INF-024 (budget-enforcer) |
| 7 | 漂移检测 | 不做配置漂移检测 | MOD-INF-023 (drift-detector) |
| 8 | 回滚执行 | 不做代码级回滚 | MOD-INF-021 (rollback-system) |

---

## 3. 接口契约

### 3.1 公共 API

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Callable
from datetime import datetime

class ResourceOptimizationEngine:
    """资源优化引擎主类——MAPE-K 循环驱动的资源监控、分析、优化与自愈"""

    _instance: Optional["ResourceOptimizationEngine"] = None

    def __new__(cls) -> "ResourceOptimizationEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def snapshot(self) -> "ResourceSnapshot":
        """
        采集当前资源快照

        输入：无
        输出：ResourceSnapshot 包含 CPU/内存/磁盘/进程/线程指标
        核心逻辑：psutil 采集 → 缺失字段降级 Windows API → 填充默认值 0
        """

    def optimize(self, strategy: "OptimizationStrategy", context: Optional[dict] = None) -> "OptimizationResult":
        """
        执行指定优化策略

        输入：strategy 枚举值 + context 可选上下文
        输出：OptimizationResult 包含执行结果和资源变化
        核心逻辑：断路器检查 → 策略执行 → 结果记录 → 知识层更新
        """

    def register_daemon(self, name: str, start_fn: Callable, stop_fn: Callable, priority: int = 5) -> None:
        """
        注册守护线程到统一调度器

        输入：name 全局唯一标识 + start_fn/stop_fn + priority 0-10（0最高）
        输出：无
        核心逻辑：名称唯一性校验 → DaemonRegistry 注册 → 按优先级排序
        """

    def start_daemon(self, name: str) -> bool:
        """启动指定守护线程。输出：是否成功启动"""

    def stop_daemon(self, name: str) -> bool:
        """停止指定守护线程（幂等）。输出：是否成功停止"""

    def get_cache_stats(self) -> "CacheStats":
        """获取 I/O 缓存统计。输出：CacheStats"""

    def get_process_pool_stats(self) -> "ProcessPoolStats":
        """获取进程池统计。输出：ProcessPoolStats"""

    def get_optimization_history(self, limit: int = 100) -> list["OptimizationRecord"]:
        """获取优化历史记录。输出：最近的 limit 条记录"""

    def on_pressure(self, callback: Callable[["PressureLevel", "ResourceSnapshot"], None]) -> None:
        """注册压力变化回调。回调异常不中断主循环"""

    def health_check(self) -> "HealthCheckResult":
        """健康检查端点。输出：引擎运行状态 + 各子系统状态"""

    def get_pressure_state(self) -> "PressureState":
        """获取当前压力状态机状态。输出：PressureState 含当前级别 + 转换历史"""

    def force_pressure(self, level: "PressureLevel", reason: str) -> None:
        """强制设置压力级别（仅用于测试和紧急人工干预）。需 Owner 审批"""

    def get_degradation_matrix(self) -> "DegradationMatrix":
        """获取当前降级矩阵。输出：各子系统在各压力级别下的行为"""

    def get_circuit_breaker_status(self) -> dict[str, "CircuitBreakerState"]:
        """获取所有断路器状态。输出：策略名 → 断路器状态映射"""

    def get_file_cache(self) -> "FileCache":
        """获取文件缓存实例。输出：FileCache 单例——v1.1.0 新增"""

    def get_process_pool(self) -> "MCPProcessPool":
        """获取进程池实例。输出：MCPProcessPool 单例——v1.1.0 新增"""

    def get_lazy_loader(self) -> "LazyModuleRegistry":
        """获取懒加载注册表实例。输出：LazyModuleRegistry 单例——v1.1.0 新增"""
```

### 3.2 数据模型

> **v1.1.0 变更**：数据模型从 `resource_optimization_engine.py` 拆分到独立文件 `resource_optimization_models.py`，解决 `io_cache.py` ↔ `resource_optimization_engine.py` 循环导入问题。
>
> 依赖链：`models.py` ← `io_cache.py` ← `resource_optimization_engine.py`（无循环）

```python
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional
from datetime import datetime

class PressureLevel(str, Enum):
    """压力等级枚举——四级分级体系"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class OptimizationStrategy(str, Enum):
    """优化策略枚举——7 种策略"""
    CACHE_WARM = "cache_warm"
    IO_BATCH = "io_batch"
    PROCESS_POOL = "process_pool"
    LAZY_INIT = "lazy_init"
    STREAMING_READ = "streaming_read"
    SCHEDULE_ADAPT = "schedule_adapt"
    MEMORY_COMPACT = "memory_compact"

class DefensiveStrategy(str, Enum):
    """防御策略枚举——4 种策略"""
    STOP_LOW_PRIORITY = "stop_low_priority"
    RELEASE_MEMORY = "release_memory"
    REDUCE_FREQUENCY = "reduce_frequency"
    EMERGENCY_GC = "emergency_gc"

class CircuitBreakerState(str, Enum):
    """断路器状态"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class ResourceSnapshot(BaseModel):
    """资源快照——某一时刻的系统资源状态"""
    timestamp: float = Field(..., description="采集时间戳（Unix epoch）")
    cpu_percent: float = Field(default=0.0, description="CPU 使用率（0-100）")
    memory_percent: float = Field(default=0.0, description="内存使用率（0-100）")
    memory_used_gb: float = Field(default=0.0, description="已用内存（GB）")
    memory_total_gb: float = Field(default=0.0, description="总内存（GB）")
    process_count: int = Field(default=0, description="进程数")
    thread_count: int = Field(default=0, description="线程数")
    disk_io_read_mb_s: float = Field(default=0.0, description="磁盘读取速率（MB/s）")
    disk_io_write_mb_s: float = Field(default=0.0, description="磁盘写入速率（MB/s）")
    disk_free_gb: float = Field(default=0.0, description="磁盘剩余空间（GB）")
    pressure: PressureLevel = Field(default=PressureLevel.NORMAL, description="压力等级")

    @field_validator("cpu_percent", "memory_percent")
    @classmethod
    def validate_percent(cls, v: float) -> float:
        return max(0.0, min(100.0, v))

class OptimizationRecord(BaseModel):
    """优化记录——一次优化动作的完整记录"""
    timestamp: float = Field(..., description="执行时间戳")
    trigger: PressureLevel = Field(..., description="触发压力等级")
    strategy: OptimizationStrategy = Field(..., description="执行的策略")
    actions_taken: list[str] = Field(default_factory=list, description="执行的动作列表")
    memory_before_gb: float = Field(..., description="优化前内存（GB）")
    memory_after_gb: float = Field(..., description="优化后内存（GB）")
    process_count_before: int = Field(..., description="优化前进程数")
    process_count_after: int = Field(..., description="优化后进程数")
    quality_preserved: bool = Field(default=True, description="业务质量是否保持")
    duration_ms: int = Field(default=0, description="执行耗时（毫秒）")
    success: bool = Field(default=True, description="是否成功")

class OptimizationResult(BaseModel):
    """优化执行结果"""
    strategy: OptimizationStrategy = Field(..., description="执行的策略")
    success: bool = Field(..., description="是否成功")
    actions_taken: list[str] = Field(default_factory=list, description="执行的动作")
    snapshot_before: ResourceSnapshot = Field(..., description="优化前快照")
    snapshot_after: Optional[ResourceSnapshot] = Field(default=None, description="优化后快照")
    quality_preserved: bool = Field(default=True, description="业务质量是否保持")
    error_message: Optional[str] = Field(default=None, description="错误信息")

class CacheStats(BaseModel):
    """缓存统计"""
    total_entries: int = Field(default=0, description="缓存条目总数")
    hit_count: int = Field(default=0, description="命中次数")
    miss_count: int = Field(default=0, description="未命中次数")
    hit_rate: float = Field(default=0.0, description="命中率（0-1）")
    memory_usage_mb: float = Field(default=0.0, description="缓存内存占用（MB）")
    evictions: int = Field(default=0, description="淘汰次数")

class ProcessPoolStats(BaseModel):
    """进程池统计"""
    active_processes: int = Field(default=0, description="活跃进程数")
    max_processes: int = Field(default=30, description="最大进程数")
    reuse_count: int = Field(default=0, description="复用次数")
    zombie_count: int = Field(default=0, description="僵尸进程数")

class PressureState(BaseModel):
    """压力状态机状态"""
    current_level: PressureLevel = Field(default=PressureLevel.NORMAL, description="当前压力级别")
    previous_level: Optional[PressureLevel] = Field(default=None, description="前一个压力级别")
    entered_at: datetime = Field(default_factory=datetime.now, description="进入当前级别的时间")
    transition_count: int = Field(default=0, description="状态转换次数")
    cooldown_remaining_s: float = Field(default=0.0, description="冷却期剩余秒数")

class HealthCheckResult(BaseModel):
    """健康检查结果"""
    engine_running: bool = Field(..., description="引擎是否运行")
    monitor_loop_alive: bool = Field(..., description="监控循环是否存活")
    last_snapshot_age_s: float = Field(..., description="上次快照距今秒数")
    pressure_level: PressureLevel = Field(..., description="当前压力级别")
    daemon_count: int = Field(default=0, description="注册守护线程数")
    cache_healthy: bool = Field(default=True, description="缓存是否健康")
    process_pool_healthy: bool = Field(default=True, description="进程池是否健康")

class DegradationMatrix(BaseModel):
    """降级矩阵——每个压力级别下各子系统的行为"""
    normal: dict[str, str] = Field(default_factory=dict, description="NORMAL 级别各子系统行为")
    warning: dict[str, str] = Field(default_factory=dict, description="WARNING 级别各子系统行为")
    critical: dict[str, str] = Field(default_factory=dict, description="CRITICAL 级别各子系统行为")
    emergency: dict[str, str] = Field(default_factory=dict, description="EMERGENCY 级别各子系统行为")
```

### 3.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `snapshot()` | 无 | — | — |
| `optimize()` | `strategy` | ✅ | 必须是 OptimizationStrategy 枚举值 |
| `optimize()` | `context` | ❌ | dict，最大 10 个键 |
| `register_daemon()` | `name` | ✅ | 全局唯一，最大 64 字符，`[a-z][a-z0-9_-]+` |
| `register_daemon()` | `start_fn` | ✅ | Callable，无参数，返回 None |
| `register_daemon()` | `stop_fn` | ✅ | Callable，无参数，返回 None，必须幂等 |
| `register_daemon()` | `priority` | ❌ | 0-10 整数，默认 5，0 最高优先级 |
| `on_pressure()` | `callback` | ✅ | Callable[[PressureLevel, ResourceSnapshot], None] |
| `force_pressure()` | `level` | ✅ | PressureLevel 枚举值 |
| `force_pressure()` | `reason` | ✅ | 非空字符串，最大 256 字符 |
| `get_optimization_history()` | `limit` | ❌ | 1-10000 整数，默认 100 |

### 3.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `snapshot()` | `ResourceSnapshot`：所有字段非 None（缺失时为 0） | 不抛异常，降级到默认值 |
| `optimize()` | `OptimizationResult`：actions_taken 非空列表 | `OptimizationResult(success=False, error_message=...)` |
| `register_daemon()` | None | `ValueError("Daemon '{name}' already registered")` |
| `start_daemon()` | `True` | `False`（守护线程不存在或已运行） |
| `stop_daemon()` | `True` | `False`（守护线程不存在或已停止，幂等） |
| `health_check()` | `HealthCheckResult` | 不抛异常，降级到 `engine_running=False` |
| `force_pressure()` | None | `PermissionError("Owner approval required")` |

### 3.5 MCP 接口

**Tools**：

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `resource_snapshot` | `snapshot()` | `{}` | `ResourceSnapshot` JSON |
| `resource_optimize` | `optimize()` | `{strategy: str, context?: dict}` | `OptimizationResult` JSON |
| `resource_health` | `health_check()` | `{}` | `HealthCheckResult` JSON |
| `resource_pressure` | `get_pressure_state()` | `{}` | `PressureState` JSON |
| `resource_daemon_list` | `DaemonRegistry.list()` | `{}` | `list[DaemonInfo]` JSON |
| `resource_cache_stats` | `get_cache_stats()` | `{}` | `CacheStats` JSON |

**错误码**：
- `ROE_001(400)` — 无效策略名
- `ROE_002(403)` — 权限不足（force_pressure 需 Owner）
- `ROE_003(404)` — 守护线程不存在
- `ROE_004(409)` — 守护线程名称冲突
- `ROE_005(503)` — 引擎未运行

### 3.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增优化策略（OptimizationStrategy 枚举值） | ✅ 向后兼容 | 不影响已有消费者 |
| 新增防御策略（DefensiveStrategy 枚举值） | ✅ 向后兼容 | 不影响已有消费者 |
| 新增 MCP Tool | ✅ 向后兼容 | 不影响已有消费者 |
| 修改 ResourceSnapshot 字段 | ⚠️ 需通知 | 消费者需更新解析逻辑 |
| 修改压力阈值 | ✅ 向后兼容 | 配置变更，非接口变更 |
| 删除/重命名 API 方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 修改 MCP Tool 输入 Schema | ⚠️ 需通知 | 消费者需更新参数 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## 4. 约束条件

### 技术约束

| # | 约束 | 原因 |
|---|------|------|
| 1 | psutil 为可选依赖 | 桌面环境可能未安装，需降级到 Windows API |
| 2 | 不修改 Trae 进程管理 | Trae 的 MCP 进程启动逻辑不在我们控制范围 |
| 3 | 优化动作不得影响业务正确性 | quality_preserved = True 是硬约束 |
| 4 | 守护线程停止操作必须是幂等的 | 重复调用 stop() 不报错 |
| 5 | 所有优化动作必须可回滚 | 优化失败时能恢复到优化前状态 |
| 6 | 监控循环自身资源占用 < 1% CPU | 监控者不能成为被监控的问题源 |
| 7 | 配置变更热加载无需重启 | 运行时修改阈值不中断监控循环 |
| 8 | 单例模式——全局唯一引擎实例 | 防止多实例导致资源竞争和策略冲突 |

### 容量估算

#### 当前规模（2026-05-08）

| 指标 | 当前值 |
|------|--------|
| 蓝图注册数 | 47 |
| Python 源文件数 | 1,714 |
| 子目录数 | 192 |
| 后台守护线程 | ~10 |
| MCP 服务器进程（10 对话） | 180 |
| 总内存占用 | 19.15 GB |

#### 1,500 模块目标规模

| 指标 | 1,500 模块时估算 | 依据 |
|------|--------|------|
| Python 源文件数 | ~54,000 | 1,714 × (1500/47) ≈ 54,680 |
| 后台守护线程 | ~300 | 每模块平均 0.2 个守护线程 |
| 蓝图文档 | 1,500 份 | 每模块一份 |
| YAML 配置文件 | ~15,000 | 每模块平均 10 个配置 |
| JSONL 日志文件 | ~3,000 | 每模块平均 2 个日志 |
| 单次全量扫描耗时 | ~30 分钟 | os.walk 54K 文件 + 逐文件 stat |
| 内存占用（无优化） | ~200 GB | 300 守护线程 × 115MB + 缓存 + 数据 |
| 内存占用（有优化） | ~8 GB | 进程池复用 + 懒加载 + 流式读取 |

#### 1,500 模块下的关键瓶颈与对策

| 瓶颈 | 无优化时 | 优化后 | 对策 |
|------|---------|--------|------|
| **进程数爆炸** | 1,500 × 10 对话 × 10 MCP = 150,000 进程 | ≤ 30 进程 | MCP 进程池跨对话共享 |
| **守护线程爆炸** | 300 线程各自轮询 | ≤ 20 线程 | 单例 + 按需启动 + 自适应频率 |
| **磁盘 I/O** | 300 线程 × 每分钟 1 次全量扫描 | 缓存命中率 90%+ | FileCache + mtime 校验 |
| **JSONL 全量读取** | 3,000 文件 × 每次 O(n) | O(limit) | tail_jsonl + 偏移量索引 |
| **YAML 解析** | 15,000 文件 × 每分钟重复解析 | 缓存命中 0 次解析 | FileCache + LRU |
| **内存泄漏** | 300 模块 × 各自累积 | 统一 GC + TTL 清理 | DaemonRegistry + purge_expired |
| **蓝图路由** | 1,500 条规则线性匹配 | O(log n) 分层路由 | 层级索引 + 关键字倒排 |
| **import 链** | 1,500 模块全部 import | 按需 import | 懒加载 + importlib 动态导入 |

#### 1,500 模块容量验证清单

| # | 检查项 | 通过标准 | 验证方法 |
|---|--------|---------|---------|
| C1 | 1,500 个蓝图注册表加载时间 | < 2 秒 | 基准测试 |
| C2 | 蓝图路由匹配时间 | < 50ms | 基准测试 |
| C3 | 10 对话时 Python 进程数 | ≤ 30 | 进程计数 |
| C4 | 10 对话时内存占用 | ≤ 8 GB | psutil 采样 |
| C5 | FileCache 命中率 | ≥ 90% | 缓存统计 |
| C6 | tail_jsonl(limit=100) 内存 | < 1 MB | 内存分析 |
| C7 | 300 守护线程注册 + 启动时间 | < 10 秒 | 基准测试 |
| C8 | EMERGENCY 压力下恢复时间 | < 60 秒 | 压力测试 |
| C9 | 优化历史查询 10,000 条 | < 100ms | 数据库查询 |
| C10 | 全量资源快照采集时间 | < 500ms | 基准测试 |
| C11 | 监控循环自身 CPU 占用 | < 1% | psutil 采样 |
| C12 | 压力状态转换抖动次数（1小时内） | ≤ 3 次 | 日志分析 |
| C13 | 断路器从 OPEN 到 HALF_OPEN 时间 | 30 秒 | 计时 |
| C14 | 配置热加载延迟 | < 5 秒 | 计时 |

### 迁移/废弃方案

| 迁移项 | 来源 | 目标 | 方式 |
|--------|------|------|------|
| DaemonRegistry | `daemon_registry.py` | `resource_optimization_engine.py` 内含 | 旧文件保留为 re-export 兼容层 |
| guard_loop | `resource_guard.py` | 注册到 DaemonRegistry | 旧函数保留为兼容入口 |

---

## 5. 依赖关系

| 依赖模块 | 类型 | 内容 | 版本 |
|----------|------|------|------|
| MOD-INF-016 (shared-core) | 必须 | daemon_registry, event_bus, lifecycle, contract_bus, API_INDEX | ≥0.14.0 |
| MOD-INF-015 (system-telemetry) | 必须 | metrics, health_probes, SLI 上报 | ≥0.9.0 |
| MOD-INF-009 (pipeline) | 必须 | pipeline_lock, orchestration | ≥0.36.0 |
| MOD-INF-010 (feedback-loop) | 必须 | scheduler (注册为守护线程), detectors | ≥0.32.0 |
| MOD-INF-007 (gate-engine) | 可选 | 资源检查门禁规则 | ≥0.5.0 |
| MOD-INF-020 (audit-trail) | 可选 | 优化动作审计记录 | ≥1.4.0 |
| MOD-INF-023 (drift-detector) | 可选 | 资源配置漂移检测 | ≥1.0.1 |
| MOD-INF-024 (budget-enforcer) | 可选 | 资源成本预算集成 | ≥0.7.0 |
| MOD-INF-019 (agent-spec) | 可选 | 技能注册 | ≥0.17.0 |
| MOD-INF-013 (mcp-servers) | 可选 | MCP 工具暴露 | ≥0.3.41 |
| psutil | pip (可选) | 系统指标采集 | ≥5.9.0 |

---

## 6. 产出物存放目录

| 产出物 | 绝对路径 |
|--------|---------|
| 资源优化引擎主模块 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\resource_optimization_engine.py` |
| 守护线程注册表（升级版） | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` |
| I/O 缓存层 | `D:\ZephyrAlpha\src\zephyr\shared\io\io_cache.py` |
| 流式读取工具 | `D:\ZephyrAlpha\src\zephyr\shared\io\streaming_reader.py` |
| 进程池管理器 | `D:\ZephyrAlpha\src\zephyr\shared\infra\process_pool.py` |
| 懒加载器 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\lazy_loader.py` |
| 资源优化配置 | `D:\ZephyrAlpha\config\resource_optimization.yaml` |
| 单元测试 | `D:\ZephyrAlpha\tests\unit\shared\test_resource_optimization.py` |
| 容量测试 | `D:\ZephyrAlpha\tests\capacity\test_1500_module_capacity.py` |
| 蓝图文档 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\resource-optimization-engine\blueprint.md` |

---

## 7. 集成目标

### 7.1 核心集成（Tier 1）

| 集成目标 | 方式 | 集成点 | 验证方法 |
|----------|------|--------|---------|
| FeedbackLoopScheduler | 注册为 priority=5 守护线程 | `scheduler.py` start() | 启动 10 对话后仅 1 个 FLE 实例运行 |
| ResourceGuard | 注册为 priority=3 守护线程 + shutil.disk_usage | `resource_guard.py` guard_loop() | guard_loop CPU 占用 < 0.1% |
| SelfMonitor | 注册为 priority=7 守护线程 + 流式读取 | `self_monitor.py` start_scheduler() | check() 内存占用 < 1MB |
| AuditWriter | 使用 io_cache 缓存 + append 写入 | `writer.py` _write() | 写入延迟 < 1ms（不随文件大小增长） |
| HeartbeatServer | 注册为 priority=8 守护线程 + 单例保护 | `heartbeat_server.py` start() | 端口冲突时不崩溃 |
| CollectionManager | 定期调用 purge_expired() | `collection_manager.py` | ChromaDB 存储增长率 < 1MB/天 |
| MCP Gateway | 进程池复用 | `gateway_server.py` | 10 对话时 Python 进程数 ≤ 20 |

### 7.2 系统集成（Tier 2）

| 集成目标 | 方式 | 集成点 | 验证方法 |
|----------|------|--------|---------|
| EventBus | 发布资源压力事件 | `event_bus.py` emit() | 压力变化时事件正确发布 |
| ContractBus | 注册资源优化契约 | `contract_bus.py` register() | 契约校验通过 |
| API_INDEX | 注册资源优化 API | `API_INDEX.py` register() | API 可被检索 |
| Gate Engine | 新增 G-RES 资源检查门禁 | `gates/_registry.yaml` | 资源不足时门禁阻断 |
| System Telemetry | 上报资源 SLI 指标 | `config/sli_registry.yaml` | 指标可查询 |
| Audit Trail | 记录优化动作审计 | `audit_trail/writer.py` | 优化动作可追溯 |
| Drift Detector | 资源配置漂移检测 | `drift_detector/drift_engine.py` | 阈值被篡改时检测到 |
| Budget Enforcer | 资源成本预算联动 | `budget_enforcer/budget_engine.py` | 资源超支时触发预算降级 |
| Rollback System | 优化动作回滚支持 | `rollback/rollback_executor.py` | 优化失败时可回滚 |

### 7.3 AI 可发现性集成（Tier 3）

| 集成目标 | 方式 | 集成点 | 验证方法 |
|----------|------|--------|---------|
| Agent Spec | 注册 SKILL-DOM-ROE-001 技能 | `skill_registry.yaml` | AI 通过技能名发现资源优化能力 |
| MCP Servers | 暴露 6 个资源优化 MCP 工具 | `mcp/gateway_server.py` | AI 通过 MCP 调用资源优化功能 |
| Blueprint Routing | 新增 R030 路由规则 | `config/blueprint_routing.yaml` | AI 通过关键字自动定位到本蓝图 |
| Trigger Routing | 新增 task_keywords 映射 | `src/zephyr/agent_spec/skill_registry.yaml` | AI 通过触发词路由到资源优化技能 |
| Blueprint Registry | 新增 MOD-INF-032 条目 | `docs/03_modules/blueprint-registry.yaml` | 蓝图可被蓝图搜索 MCP 发现 |
| Module Registry | 新增 MOD-INF-032 条目 | `docs/03_modules/module-registry.yaml` | 模块可被模块索引发现 |
| Cross-Module Dependency | 新增依赖关系 | `cross-module-dependency-registry.yaml` | 依赖链可追溯 |
| Module ID Registry | 新增 MOD-INF-032 ID | `module-id-registry.yaml` | ID 不冲突 |
| AGENTS.md | 新增资源优化冷启动步骤 | `AGENTS.md` | 新 AI session 知道资源优化引擎存在 |
| project_rules.md | 新增 STEP 引用 | `.trae/rules/project_rules.md` | Trae 自动加载规则中包含资源优化 |

---

## 8. 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | lifecycle __init__ | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\__init__.py` | 导出 ResourceOptimizationEngine | 模块可导入 |
| 2 | io __init__ | `D:\ZephyrAlpha\src\zephyr\shared\io\__init__.py` | 导出 io_cache, streaming_reader | 模块可导入 |
| 3 | FLE Scheduler | `D:\ZephyrAlpha\src\zephyr\feedback_loop\scheduler.py` | 使用 DaemonRegistry.register() 注册 | 统一调度 |
| 4 | ResourceGuard | `D:\ZephyrAlpha\src\zephyr\drift_detector\resource_guard.py` | 使用 DaemonRegistry.register() 注册 | 统一调度 |
| 5 | SelfMonitor | `D:\ZephyrAlpha\src\zephyr\audit_trail\self_monitor.py` | 使用 DaemonRegistry.register() 注册 | 统一调度 |
| 6 | HeartbeatServer | `D:\ZephyrAlpha\src\zephyr\shared\heartbeat_server.py` | 使用 DaemonRegistry.register() 注册 | 统一调度 |
| 7 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 新增 MOD-INF-032 条目 | 蓝图可发现 |
| 8 | 模块注册表 | `D:\ZephyrAlpha\docs\03_modules\module-registry.yaml` | 新增 MOD-INF-032 条目 | 模块可发现 |
| 9 | 蓝图路由表 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | 新增 R030 路由规则 | AI 可路由 |
| 10 | 技能注册表 | `D:\ZephyrAlpha\src\zephyr\agent_spec\skill_registry.yaml` | 新增 SKILL-DOM-ROE-001 + task_keywords | AI 可发现技能 |
| 11 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | 新增 MOD-INF-032 依赖关系 | 依赖链可追溯 |
| 12 | 模块ID注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | 新增 MOD-INF-032 ID | ID 唯一性 |
| 13 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | 新增 G-RES 资源检查门禁 | 资源不足时门禁阻断 |
| 14 | SLI 注册表 | `D:\ZephyrAlpha\config\sli_registry.yaml` | 新增资源优化 SLI 指标 | 可观测性 |
| 15 | MCP 工具契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool_contracts.yaml` | 新增 6 个资源优化工具契约 | MCP 可调用 |
| 16 | 集成闭环总蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master-blueprint\blueprint.md` | 新增 CT-ROE 集成契约 | 跨系统集成 |
| 17 | requirements.txt | `D:\ZephyrAlpha\requirements.txt` | 新增 psutil>=5.9.0 (可选) | 依赖声明 |

---

## 9. 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解措施 |
|---|------|:----:|:----:|---------|
| R1 | psutil 未安装导致指标缺失 | 中 | 低 | 降级到 Windows GlobalMemoryStatusEx API |
| R2 | 进程池复用导致状态泄漏 | 低 | 高 | 每次使用前重置 MCP 服务器状态 + 请求级沙箱 |
| R3 | 缓存一致性——YAML 文件被外部修改 | 中 | 中 | 缓存条目带 mtime 校验，变化时失效 |
| R4 | 优化动作误判——停止了必要的服务 | 低 | 高 | 优先级系统 + quality_preserved 硬约束 + 人类确认回调 |
| R5 | 监控线程自身成为 CPU 瓶颈 | 低 | 中 | 30 秒间隔 + psutil.cpu_percent(interval=0) 非阻塞 |
| R6 | 压力等级抖动——频繁在 WARNING/NORMAL 间切换 | 中 | 中 | 滞后机制（上升阈值 75% / 下降阈值 65%）+ 冷却期 60 秒 |
| R7 | 断路器误开——偶发失败导致策略被熔断 | 低 | 高 | HALF_OPEN 探测机制 + 失败计数阈值 ≥3 + 自动恢复 30 秒 |
| R8 | 背压传播——优化速度跟不上恶化速度 | 低 | 高 | EMERGENCY 级别直接停止所有非核心服务 + 人类告警 |
| R9 | 配置热加载导致运行中策略参数突变 | 中 | 中 | 配置变更在下一个监控周期生效 + 当前正在执行的策略不受影响 |
| R10 | 优化器自身资源泄漏 | 低 | 高 | 优化历史使用 SQLite 存储（非内存）+ 定期 self_health_check + 自动重启 |
| R11 | 懒加载首次调用延迟过高 | 中 | 低 | CACHE_WARM 策略预判热点模块 + import 预加载 |
| R12 | 单例模式在多进程环境下失效 | 低 | 中 | 文件锁保证跨进程单例 + 进程池内共享实例 |

---

## 10. 后果（Consequences）

### 正面后果

1. **系统稳定性提升**——内存耗尽前自动优化，避免 -2 错误
2. **资源利用率提升**——进程池复用减少 80%+ 内存占用
3. **I/O 性能提升**——缓存 + 流式读取 + append 写入消除 I/O 瓶颈
4. **可观测性提升**——全局资源快照 + 优化历史 + 压力分级 + SLI 指标
5. **MAPE-K 知识积累**——优化历史为未来决策提供依据
6. **自愈能力**——资源异常自动检测→诊断→优化→验证闭环
7. **AI 可发现**——三重发现机制（蓝图路由+技能注册+MCP工具）确保新 AI 知道使用
8. **1,500 模块可扩展**——三大架构转变为规模扩展奠定基础

### 负面后果

1. **新增 psutil 可选依赖**——需在 requirements.txt 中添加
2. **守护线程注册为必须步骤**——现有模块需改造接入
3. **缓存层增加内存开销**——约 10-50MB（取决于缓存文件数量）
4. **进程池引入状态管理复杂度**——需确保 MCP 服务器状态隔离
5. **优化器自身需被监控**——"谁监控监控者"问题，需 self_health_check
6. **降级矩阵增加运维认知负担**——需通过 MCP 工具和仪表盘降低理解成本

---

## 11. 施工指引

### 施工策略

分 7 个 Phase，对应三大架构转变 + I/O 优化 + 自愈闭环 + AI 可发现性 + 容量验证：

### Phase 1: 统一调度引擎（对应转变 3：从各自轮询到统一调度）✅ COMPLETED

**前置条件**：DaemonRegistry 已存在

**实施步骤**：

1. **读**：阅读 `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` 现有实现
2. **做**：创建 `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\resource_optimization_engine.py`
   - 实现 `ResourceOptimizationEngine` 类（单例）
   - 实现 `snapshot_resources()` 采集 CPU/内存/进程/磁盘 I/O
   - 实现 `_classify_pressure()` 压力分级（NORMAL/WARNING/CRITICAL/EMERGENCY）
   - 实现 `_monitor_loop()` 30 秒循环
   - 实现防御策略引擎：EMERGENCY 时停止低优先级守护线程，CRITICAL 时降低频率
   - 实现优化策略引擎：NORMAL 时缓存预热/批量 I/O，WARNING 时流式读取/延迟初始化
   - 实现 `optimize()` 统一调度两个策略引擎
   - 实现 `OptimizationStrategy` 枚举和对应执行逻辑
   - 实现压力状态机（含滞后机制和冷却期）
   - 实现断路器模式（CLOSED/OPEN/HALF_OPEN）
   - 实现 `health_check()` 自检端点
3. **产**：`resource_optimization_engine.py` + 单元测试
4. **检**：运行测试，验证压力分级逻辑正确

**完成标准**：
- `snapshot_resources()` 在 Windows 上正常采集内存指标
- 压力分级逻辑覆盖所有 4 个级别
- 防御策略和优化策略各自独立触发、互不干扰
- 监控循环可启停
- 压力状态机滞后机制防止抖动
- 断路器在 3 次失败后熔断

### Phase 2: I/O 优化层 ✅ COMPLETED

**前置条件**：Phase 1 完成

**实施步骤**：

1. **读**：阅读 `D:\ZephyrAlpha\src\zephyr\shared\io\__init__.py` 和 `file_utils.py`
2. **做**：
   - 创建 `D:\ZephyrAlpha\src\zephyr\shared\io\io_cache.py`
     - `FileCache` 类：基于 mtime 的 YAML/JSON 文件缓存
     - 缓存键 = 文件路径 + mtime，值 = 解析后的 dict
     - 最大缓存 1000 条目，LRU 淘汰
   - 创建 `D:\ZephyrAlpha\src\zephyr\shared\io\streaming_reader.py`
     - `tail_jsonl()` 函数：读取 JSONL 文件最后 N 行（seek 到文件末尾附近）
     - `stream_jsonl()` 函数：生成器模式逐行读取，不全部加载
3. **产**：`io_cache.py` + `streaming_reader.py` + 单元测试
4. **检**：验证缓存命中率 ≥90%（重复读取场景）

**完成标准**：
- `FileCache` 缓存命中时 0 次 I/O
- `tail_jsonl(path, 100)` 内存占用 < 100KB
- 缓存条目在文件修改后自动失效

### Phase 3: 守护线程统一接入（对应转变 3：消除各自轮询）✅ COMPLETED

**前置条件**：Phase 1 完成

**实施步骤**：

1. **读**：阅读所有需要接入的守护线程模块
2. **做**：
   - 修改 `scheduler.py`：在 `start()` 中调用 `DaemonRegistry.register("fle-scheduler", self.start, self.stop, priority=5)`
   - 修改 `resource_guard.py`：在 `guard_loop()` 启动时注册
   - 修改 `self_monitor.py`：在 `start_scheduler()` 中注册
   - 修改 `heartbeat_server.py`：在 `start()` 中注册
   - 修改 `auto_evolution.py`：在 `start()` 中注册
   - 修改 `task_queue.py`：在 `start()` 中注册
3. **产**：修改后的 6 个文件 + 集成测试
4. **检**：启动所有守护线程后 `DaemonRegistry.status()` 显示全部 RUNNING

**完成标准**：
- 所有守护线程通过 DaemonRegistry 注册
- `stop_low_priority()` 能按优先级停止守护线程
- EMERGENCY 压力时自动停止低优先级守护线程

### Phase 4: 进程池 + 懒加载（对应转变 1 + 转变 2）✅ COMPLETED

**前置条件**：Phase 2 + Phase 3 完成

**实施步骤**：

1. **读**：阅读 `D:\ZephyrAlpha\src\zephyr\mcp\gateway_server.py` 进程管理逻辑
2. **做**：
   - 创建 `D:\ZephyrAlpha\src\zephyr\shared\infra\process_pool.py`
     - `MCPProcessPool` 类：管理 MCP 服务器进程的生命周期
     - 最大进程数限制（默认 30）
     - 进程复用：同一 MCP 服务器跨对话共享
     - 僵尸进程检测和回收
   - 创建 `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\lazy_loader.py`
     - `LazyModuleRegistry` 类：按需加载模块
     - `importlib.import_module()` 动态导入
     - 热点模块预判 + 预加载
   - 实现自适应调度：
     - FLE-Scheduler 在 NORMAL 压力时 30 秒轮询
     - WARNING 压力时延长到 60 秒
     - CRITICAL 压力时延长到 120 秒
     - EMERGENCY 压力时暂停（stop + 后续恢复）
3. **产**：`process_pool.py` + `lazy_loader.py` + 集成测试
4. **检**：10 对话场景下进程数 ≤ 20，内存 < 8GB

**完成标准**：
- 进程池最大进程数可配置
- 懒加载：启动时仅加载核心框架（~20 模块），其余按需加载
- 自适应调度根据压力自动调整轮询频率
- 10 对话场景下系统不卡顿、不报 -2 错误

### Phase 5: 自愈闭环 + 配置管理 ✅ COMPLETED

**前置条件**：Phase 1-4 完成

**实施步骤**：

1. **做**：
   - 创建 `D:\ZephyrAlpha\config\resource_optimization.yaml` 配置文件
     - 压力阈值：memory_warning=75, memory_critical=85, memory_emergency=95
     - 调度频率：normal=30s, warning=60s, critical=120s, emergency=暂停
     - 缓存参数：max_entries=1000, ttl=300s
     - 进程池参数：max_processes=30, zombie_check_interval=60s
     - 断路器参数：failure_threshold=3, recovery_timeout=30s
     - 滞后参数：hysteresis_percent=10, cooldown_seconds=60
   - 实现配置热加载（文件 mtime 监控 + 下一个监控周期生效）
   - 实现自愈闭环：检测→诊断→优化→验证
   - 实现背压机制：优化速度跟不上恶化速度时触发 EMERGENCY
   - 集成 EventBus 发布资源压力事件
   - 集成 Audit Trail 记录优化动作
2. **产**：配置文件 + 自愈逻辑 + 集成测试
3. **检**：模拟内存泄漏场景，验证自愈闭环在 60 秒内恢复

**完成标准**：
- 配置文件存在且所有参数有明确默认值
- 配置变更在 5 秒内生效
- 自愈闭环：内存泄漏→检测→优化→验证 ≤60 秒
- EventBus 事件正确发布
- 优化动作可审计追溯

### Phase 6: AI 可发现性 + 注册

**前置条件**：Phase 1 完成

**实施步骤**：

1. **做**：
   - 更新 `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml`：新增 MOD-INF-032 条目
   - 更新 `D:\ZephyrAlpha\docs\03_modules\module-registry.yaml`：新增 MOD-INF-032 条目
   - 更新 `D:\ZephyrAlpha\config\blueprint_routing.yaml`：新增 R030 路由规则
   - 更新 `D:\ZephyrAlpha\src\zephyr\agent_spec\skill_registry.yaml`：新增 SKILL-DOM-ROE-001 + task_keywords
   - 更新 `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml`：新增依赖
   - 更新 `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml`：新增 ID
   - 更新 `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml`：新增 G-RES 门禁
   - 更新 `D:\ZephyrAlpha\config\sli_registry.yaml`：新增资源 SLI
   - 更新 `D:\ZephyrAlpha\src\zephyr\mcp\tool_contracts.yaml`：新增 6 个工具契约
   - 创建 `D:\ZephyrAlpha\src\zephyr\agent_spec\skills\domain\resource_optimization.md`：技能描述文件
2. **产**：10+ 个注册表更新 + 1 个技能描述文件
3. **检**：通过 blueprint_search MCP 可搜索到 MOD-INF-032

**完成标准**：
- 所有注册表包含 MOD-INF-032 条目
- 蓝图路由 R030 匹配关键字"资源优化"/"resource"/"内存"/"CPU"
- 技能注册表包含 SKILL-DOM-ROE-001
- MCP 工具契约包含 6 个资源优化工具

### Phase 7: 1,500 模块容量验证

**前置条件**：Phase 1-6 全部完成

**实施步骤**：

1. **读**：阅读 §4 中"1,500 模块容量验证清单"
2. **做**：
   - 创建容量基准测试脚本 `D:\ZephyrAlpha\tests\capacity\test_1500_module_capacity.py`
   - 模拟 1,500 模块注册（使用轻量级 mock 模块）
   - 逐一验证 C1-C14 容量检查项
   - 记录基准数据到 `D:\ZephyrAlpha\tests\capacity\baseline_1500.yaml`
3. **产**：容量测试 + 基准数据
4. **检**：所有 C1-C14 检查项通过

**完成标准**：
- C1-C14 全部通过
- 基准数据记录完整，可供后续回归对比

### 回滚方案

每个 Phase 独立，可单独回滚：
- Phase 1 回滚：删除 `resource_optimization_engine.py`，恢复 `daemon_registry.py` 旧版
- Phase 2 回滚：删除 `io_cache.py` 和 `streaming_reader.py`
- Phase 3 回滚：恢复 6 个守护线程模块的原始启动逻辑
- Phase 4 回滚：删除 `process_pool.py` 和 `lazy_loader.py`，恢复原始调度频率
- Phase 5 回滚：删除 `resource_optimization.yaml`，移除 EventBus/Audit 集成代码
- Phase 6 回滚：恢复所有注册表到更新前状态
- Phase 7 回滚：删除容量测试脚本

### 施工状态

| Phase | 对应转变 | 状态 | 完成日期 |
|:-----:|:-------:|:----:|:--------:|
| 1 | 转变 3（统一调度） | not_started | - |
| 2 | I/O 优化 | not_started | - |
| 3 | 转变 3（统一接入） | not_started | - |
| 4 | 转变 1（进程池）+ 转变 2（懒加载） | not_started | - |
| 5 | 自愈闭环 + 配置管理 | not_started | - |
| 6 | AI 可发现性 + 注册 | not_started | - |
| 7 | 1,500 模块容量验证 | not_started | - |

---

## 12. MAPE-K 详细设计

> 对标 IBM Autonomic Computing Architecture、Kubernetes Control Plane、Google SRE Automation

### 12.1 Monitor（监控层）

| 组件 | 职责 | 采集频率 | 降级策略 |
|------|------|---------|---------|
| CpuMonitor | cpu_percent, cpu_count, load_avg | 30s | psutil 缺失时跳过 |
| MemoryMonitor | memory_percent, memory_used_gb, memory_total_gb | 30s | 降级到 Windows GlobalMemoryStatusEx |
| DiskMonitor | disk_io_read_mb_s, disk_io_write_mb_s, disk_free_gb | 30s | 降级到 shutil.disk_usage |
| ProcessMonitor | process_count, thread_count, zombie_count | 30s | 降级到 os.getpid() + psutil.Process |
| DaemonMonitor | 各守护线程运行状态 | 60s | 仅检查 DaemonRegistry 状态 |

### 12.2 Analyze（分析层）

| 分析器 | 职责 | 输入 | 输出 |
|--------|------|------|------|
| PressureClassifier | 压力分级 | ResourceSnapshot | PressureLevel |
| TrendAnalyzer | 资源趋势分析 | 最近 10 个 ResourceSnapshot | 趋势方向（上升/平稳/下降） |
| AnomalyDetector | 异常检测 | ResourceSnapshot + 历史基线 | 是否异常 + 置信度 |
| RootCauseAnalyzer | 根因分析 | 异常 + 守护线程状态 + 进程列表 | 最可能原因 |

### 12.3 Plan（计划层）

| 规划器 | 职责 | 触发条件 | 输出 |
|--------|------|---------|------|
| DefensivePlanner | 防御策略规划 | CRITICAL/EMERGENCY | DefensiveStrategy 列表 |
| OffensivePlanner | 优化策略规划 | NORMAL/WARNING | OptimizationStrategy 列表 |
| ConflictResolver | 策略冲突解决 | 防御和优化策略同时触发 | 优先执行防御策略 |
| RollbackPlanner | 回滚计划 | 优化失败 | 回滚步骤列表 |

### 12.4 Execute（执行层）

| 执行器 | 职责 | 安全保障 |
|--------|------|---------|
| StrategyExecutor | 执行优化/防御策略 | 断路器保护 + quality_preserved 校验 |
| DaemonController | 守护线程启停控制 | 幂等操作 + 优先级排序 |
| CacheManager | 缓存管理 | mtime 校验 + TTL 过期 |
| ProcessPoolManager | 进程池管理 | 最大进程数限制 + 僵尸回收 |

### 12.5 Knowledge（知识层）

| 知识类型 | 存储 | 用途 |
|---------|------|------|
| 优化历史 | SQLite `resource_optimization.db` | 策略效果分析 + 趋势预测 |
| 压力转换历史 | 内存（最近 1000 次） | 抖动检测 + 滞后校准 |
| 策略成功率 | 内存（LRU 100 条） | 策略选择优先级 |
| 资源基线 | SQLite | 异常检测基线 |
| 配置快照 | SQLite | 配置漂移检测 |

---

## 13. 压力状态机

### 13.1 状态转换图

```
                    memory > 95%
    ┌──────────┐ ──────────────→ ┌───────────┐
    │  NORMAL  │                  │ EMERGENCY │
    │          │ ←────────────── │           │
    └────┬─────┘  memory < 85%   └─────┬─────┘
         │        (滞后 10%)            │
         │ memory > 75%                 │ memory < 90%
         ↓                              │ (滞后 5%)
    ┌──────────┐                  ┌─────┴─────┐
    │ WARNING  │ ──────────────→ │ CRITICAL  │
    │          │ ←────────────── │           │
    └──────────┘  memory < 65%   └───────────┘
                 (滞后 10%)
```

### 13.2 转换规则

| 从 → 到 | 触发条件 | 滞后机制 | 冷却期 |
|---------|---------|---------|--------|
| NORMAL → WARNING | memory > 75% 或 cpu > 80% 或 process_count > 50 | 无 | 60s |
| WARNING → NORMAL | memory < 65% 且 cpu < 70% 且 process_count < 40 | 滞后 10% | 60s |
| WARNING → CRITICAL | memory > 85% 或 cpu > 90% | 无 | 60s |
| CRITICAL → WARNING | memory < 75% 且 cpu < 80% | 滞后 10% | 60s |
| CRITICAL → EMERGENCY | memory > 95% 或 cpu > 98% | 无 | 30s |
| EMERGENCY → CRITICAL | memory < 90% | 滞后 5% | 30s |

### 13.3 防抖动机制

- **滞后（Hysteresis）**：上升阈值和下降阈值之间保持 10% 差距，防止在阈值附近频繁切换
- **冷却期（Cooldown）**：状态转换后 60 秒内不再转换（EMERGENCY 除外，30 秒）
- **确认计数**：连续 2 次采样满足条件才触发转换，单次异常不触发
- **抖动检测**：1 小时内转换超过 3 次则记录告警，自动加宽滞后区间

---

## 14. 优雅降级矩阵

| 子系统 | NORMAL | WARNING | CRITICAL | EMERGENCY |
|--------|--------|---------|----------|-----------|
| FLE-Scheduler | 30s 轮询 | 60s 轮询 | 120s 轮询 | 暂停 |
| ResourceGuard | 5s 扫描 | 30s 扫描 | 60s 扫描 | 暂停 |
| SelfMonitor | 正常检查 | 流式读取 | 减少检查项 | 仅心跳 |
| HeartbeatServer | 正常心跳 | 降低频率 | 最低频率 | 仅保持端口 |
| AuditWriter | 正常写入 | 批量写入 | 仅 append | 缓冲到内存 |
| CollectionManager | 正常 purge | 延长 purge 间隔 | 暂停 purge | 暂停 |
| MCP 进程池 | 正常复用 | 限制新进程 | 不创建新进程 | 释放非核心进程 |
| FileCache | 正常缓存 | 限制新缓存条目 | 冻结缓存 | 清理低优先级缓存 |
| 懒加载 | 正常按需加载 | 仅加载核心模块 | 仅加载必要模块 | 禁止加载 |
| EventBus | 正常发布 | 批量发布 | 仅发布关键事件 | 仅发布 EMERGENCY 事件 |

---

## 15. 全系统集成契约

### 15.1 EventBus 事件类型

| 事件名 | 触发条件 | 数据 |
|--------|---------|------|
| `resource.pressure.changed` | 压力等级变化 | `{old_level, new_level, snapshot}` |
| `resource.optimization.executed` | 优化策略执行完成 | `{strategy, result, snapshot_before, snapshot_after}` |
| `resource.optimization.failed` | 优化策略执行失败 | `{strategy, error, snapshot}` |
| `resource.daemon.stopped` | 守护线程被停止 | `{daemon_name, reason, pressure_level}` |
| `resource.circuit_breaker.opened` | 断路器打开 | `{strategy, failure_count}` |
| `resource.circuit_breaker.closed` | 断路器关闭 | `{strategy}` |
| `resource.emergency.entered` | 进入 EMERGENCY | `{snapshot, root_cause}` |
| `resource.emergency.recovered` | 从 EMERGENCY 恢复 | `{snapshot, recovery_time_s}` |

### 15.2 ContractBus 契约

| 契约 ID | 方向 | 内容 |
|---------|------|------|
| CT-ROE-001 | ROE → EventBus | 压力变化事件发布契约 |
| CT-ROE-002 | ROE → AuditTrail | 优化动作审计记录契约 |
| CT-ROE-003 | BudgetEnforcer → ROE | 预算降级触发资源优化契约 |
| CT-ROE-004 | ROE → GateEngine | 资源不足门禁阻断契约 |
| CT-ROE-005 | FeedbackLoop → ROE | 资源异常检测器注册契约 |
| CT-ROE-006 | DriftDetector → ROE | 资源配置漂移通知契约 |

### 15.3 API_INDEX 注册

| API 名 | 模块 | 方法 | 描述 |
|--------|------|------|------|
| `resource_snapshot` | ResourceOptimizationEngine | snapshot() | 获取当前资源快照 |
| `resource_optimize` | ResourceOptimizationEngine | optimize() | 执行优化策略 |
| `resource_health` | ResourceOptimizationEngine | health_check() | 健康检查 |
| `resource_pressure` | ResourceOptimizationEngine | get_pressure_state() | 获取压力状态 |
| `resource_cache_stats` | ResourceOptimizationEngine | get_cache_stats() | 缓存统计 |
| `resource_daemon_list` | DaemonRegistry | list() | 守护线程列表 |

### 15.4 Gate 门禁规则

| Gate ID | 类型 | 触发条件 | 动作 |
|---------|------|---------|------|
| G-RES-001 | pre_check | memory_percent > 90% | 阻断非必要操作，提示"系统资源不足" |
| G-RES-002 | pre_check | process_count > 100 | 阻断新进程创建 |
| G-RES-003 | post_check | 优化后 memory 未降低 | 告警 + 升级到 EMERGENCY |

### 15.5 SLI 指标

| SLI 名 | 类型 | 目标 | 测量方法 |
|--------|------|------|---------|
| `resource_optimization_success_rate` | 成功率 | ≥ 95% | 成功次数 / 总执行次数 |
| `resource_pressure_recovery_time_s` | 恢复时间 | ≤ 60s | EMERGENCY 进入到恢复的时间 |
| `resource_cache_hit_rate` | 缓存命中率 | ≥ 90% | 命中次数 / 总访问次数 |
| `resource_process_pool_reuse_rate` | 进程复用率 | ≥ 80% | 复用次数 / 总请求次数 |
| `resource_monitor_cpu_overhead_percent` | 监控开销 | ≤ 1% | 监控循环 CPU 占用 |

---

## 16. AI 可发现性设计

> **核心原则**：在 100% AI 开发 + 一人维护的语境下，任何新 AI session 必须能在 0 次人工指引下
> 自动发现并使用资源优化功能。三重发现机制确保不成为孤儿功能。

### 16.1 发现路径 1：蓝图路由

AI 通过 `config/blueprint_routing.yaml` R030 规则自动定位：

```yaml
- route_id: "R030"
  blueprint_id: "MOD-INF-032"
  blueprint_level: module
  path_patterns:
    - "src/zephyr/shared/lifecycle/resource_optimization_engine.py"
    - "src/zephyr/shared/io/io_cache.py"
    - "src/zephyr/shared/io/streaming_reader.py"
    - "src/zephyr/shared/infra/process_pool.py"
    - "src/zephyr/shared/lifecycle/lazy_loader.py"
    - "config/resource_optimization.yaml"
  task_keywords:
    - "资源优化"
    - "resource optimization"
    - "内存"
    - "memory"
    - "CPU"
    - "进程池"
    - "process pool"
    - "缓存"
    - "cache"
    - "守护线程"
    - "daemon"
    - "压力"
    - "pressure"
    - "降级"
    - "degradation"
    - "懒加载"
    - "lazy load"
    - "流式读取"
    - "streaming"
    - "自愈"
    - "self-healing"
    - "MAPE-K"
    - "断路器"
    - "circuit breaker"
    - "背压"
    - "backpressure"
  scope: pre_change
  safety: "H"
  priority: 91
  description: "资源优化引擎 — MAPE-K 循环驱动的资源监控、分析、优化与自愈系统"
```

### 16.2 发现路径 2：Agent Skill

AI 通过 `skill_registry.yaml` SKILL-DOM-ROE-001 技能发现：

```yaml
SKILL-DOM-ROE-001:
  name: resource-optimization
  description: "Resource Optimization Engine (MOD-INF-032) MAPE-K 循环驱动的资源监控/分析/优化/自愈。双策略引擎（防御+优化），压力状态机（NORMAL/WARNING/CRITICAL/EMERGENCY），断路器，背压，优雅降级矩阵，进程池复用，I/O 缓存，流式读取，懒加载，自适应调度。入口 ResourceOptimizationEngine.snapshot()/optimize()/health_check()"
  skill_type: domain
  tier: L1
  path: resource_optimization.md
  references:
    - MOD-INF-032
    - MOD-INF-016
    - MOD-INF-015
```

触发路由 task_keywords 新增：

```yaml
resource: resource-optimization
资源优化: resource-optimization
内存优化: resource-optimization
memory: resource-optimization
cpu: resource-optimization
进程池: resource-optimization
process_pool: resource-optimization
daemon: resource-optimization
守护线程: resource-optimization
pressure: resource-optimization
压力: resource-optimization
degradation: resource-optimization
降级: resource-optimization
cache: resource-optimization
缓存: resource-optimization
lazy: resource-optimization
懒加载: resource-optimization
self-healing: resource-optimization
自愈: resource-optimization
circuit_breaker: resource-optimization
断路器: resource-optimization
```

### 16.3 发现路径 3：MCP 工具

AI 通过 MCP 工具直接调用资源优化功能（见 §3.5）。

### 16.4 冷启动集成

新 AI session 冷启动时，通过以下路径发现资源优化引擎：

```
AGENTS.md → PS-STD-005 §7 → MOD-MASTER-001 → MOD-INF-032
                                                     ↓
                              blueprint_routing.yaml R030（关键字匹配）
                                                     ↓
                              skill_registry.yaml SKILL-DOM-ROE-001
                                                     ↓
                              MCP 工具 resource_snapshot/health_check
```

### 16.5 需登记的注册表完整清单

| # | 注册表 | 路径 | 登记内容 |
|---|--------|------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | MOD-INF-032 条目 |
| 2 | 模块注册表 | `D:\ZephyrAlpha\docs\03_modules\module-registry.yaml` | MOD-INF-032 条目 |
| 3 | 蓝图路由表 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | R030 路由规则 |
| 4 | 技能注册表 | `D:\ZephyrAlpha\src\zephyr\agent_spec\skill_registry.yaml` | SKILL-DOM-ROE-001 + keywords |
| 5 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | MOD-INF-032 依赖 |
| 6 | 模块ID注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | MOD-INF-032 ID |
| 7 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | G-RES-001~003 |
| 8 | SLI 注册表 | `D:\ZephyrAlpha\config\sli_registry.yaml` | 5 个资源 SLI |
| 9 | MCP 工具契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool_contracts.yaml` | 6 个工具契约 |
| 10 | 基础设施注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure-registry.yaml` | MOD-INF-032 基础设施条目 |
| 11 | 文档元数据索引 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index.yaml` | 蓝图文档元数据 |
| 12 | 目录注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\directory-registry.yaml` | 新增目录条目 |
| 13 | 系统路径注册表 | `D:\ZephyrAlpha\docs\03_modules\system-pathway-registry.yaml` | 资源优化路径 |

---

## 17. 自动化运维设计

> 在一人开发+AI维护、一人使用、100%氛围编程AI开发的语境下，尽量全自动化。

### 17.1 自愈闭环

```
检测（Monitor）→ 分析（Analyze）→ 计划（Plan）→ 执行（Execute）→ 验证（Verify）
     ↑                                                    │
     └──────────── 验证失败则回滚并升级 ←───────────────────┘
```

| 阶段 | 自动化程度 | 人工介入 |
|------|:---------:|---------|
| 检测 | 100% 自动 | 无 |
| 分析 | 100% 自动 | 无 |
| 计划 | 95% 自动 | EMERGENCY 级别需人类确认（可配置跳过） |
| 执行 | 100% 自动 | 无 |
| 验证 | 100% 自动 | 无 |
| 回滚 | 100% 自动 | 无 |

### 17.2 混沌工程（压力测试）

| 测试场景 | 触发方式 | 预期行为 | 验证方法 |
|---------|---------|---------|---------|
| 内存泄漏模拟 | 分配大量对象不释放 | WARNING → CRITICAL → 自动 GC → 恢复 | 内存恢复到 NORMAL |
| 进程数爆炸 | 启动大量子进程 | 进程池限制 + 僵尸回收 | 进程数 ≤ max_processes |
| 磁盘 I/O 阻塞 | 模拟大量文件写入 | IO_BATCH 策略 + append 写入 | I/O 延迟 < 阈值 |
| 守护线程死锁 | 模拟线程阻塞 | 超时检测 + 自动重启 | 线程恢复运行 |
| 配置漂移 | 修改阈值配置 | 漂移检测 + 告警 | 漂移被检测到 |

### 17.3 Runbook（运维手册）

| 场景 | 自动处理 | 人工操作 |
|------|---------|---------|
| 内存 > 90% | 自动触发 CRITICAL 策略 | 无需操作 |
| 内存 > 95% | 自动触发 EMERGENCY + 停止低优先级服务 | 检查是否有异常进程 |
| 优化策略连续失败 3 次 | 断路器打开 + 告警 | 检查失败原因 |
| 压力状态 1 小时抖动 > 3 次 | 自动加宽滞后区间 | 检查是否有周期性负载 |
| 监控循环自身崩溃 | 自动重启（daemon 线程） | 检查崩溃原因 |
| 进程池僵尸进程 > 5 | 自动回收 | 检查是否有进程泄漏 |

### 17.4 自动化优化策略

| 策略 | 触发条件 | 自动执行 | 可配置参数 |
|------|---------|---------|-----------|
| CACHE_WARM | NORMAL + 空闲时段 | 预热最近访问的 YAML 文件 | 预热文件数、预热间隔 |
| IO_BATCH | WARNING + 多个小 I/O | 合并为批量操作 | 批量大小、合并窗口 |
| PROCESS_POOL | 任何级别 | 复用 MCP 进程 | 最大进程数、超时时间 |
| LAZY_INIT | WARNING + 内存 > 70% | 延迟加载非核心模块 | 核心模块列表 |
| STREAMING_READ | WARNING + 大文件读取 | 切换为流式读取 | 文件大小阈值 |
| SCHEDULE_ADAPT | 任何级别 | 调整守护线程频率 | 各级别频率 |
| MEMORY_COMPACT | CRITICAL + 内存 > 85% | GC + 对象池化 | GC 触发阈值 |

---

## 18. 配置管理

### 18.1 配置文件结构

`D:\ZephyrAlpha\config\resource_optimization.yaml`：

```yaml
version: "1.0.0"
pressure_thresholds:
  memory_warning_percent: 75
  memory_critical_percent: 85
  memory_emergency_percent: 95
  cpu_warning_percent: 80
  cpu_critical_percent: 90
  cpu_emergency_percent: 98
  process_warning_count: 50
  process_critical_count: 100
hysteresis:
  percent: 10
  cooldown_seconds: 60
  confirmation_count: 2
  oscillation_threshold_per_hour: 3
schedule:
  normal_interval_s: 30
  warning_interval_s: 60
  critical_interval_s: 120
  emergency_action: pause
cache:
  max_entries: 1000
  ttl_seconds: 300
  lru_enabled: true
process_pool:
  max_processes: 30
  zombie_check_interval_s: 60
  reuse_enabled: true
circuit_breaker:
  failure_threshold: 3
  recovery_timeout_s: 30
  half_open_max_calls: 1
audit:
  enabled: true
  max_history_records: 10000
  storage: sqlite
self_healing:
  enabled: true
  max_recovery_time_s: 60
  emergency_human_confirm: false
```

### 18.2 热加载机制

- 配置文件 mtime 监控：每 30 秒检查一次
- 变更检测：mtime 变化 → 重新加载配置
- 生效策略：下一个监控周期开始时使用新配置
- 当前正在执行的策略不受影响（避免中途变更导致不一致）

---

## 19. 可观测性集成

### 19.1 指标上报

| 指标 | 类型 | 上报目标 | 频率 |
|------|------|---------|------|
| resource_cpu_percent | gauge | System Telemetry | 30s |
| resource_memory_percent | gauge | System Telemetry | 30s |
| resource_process_count | gauge | System Telemetry | 30s |
| resource_pressure_level | gauge(0-3) | System Telemetry | 30s |
| resource_optimization_total | counter | System Telemetry | 事件驱动 |
| resource_optimization_success | counter | System Telemetry | 事件驱动 |
| resource_optimization_duration_ms | histogram | System Telemetry | 事件驱动 |
| resource_cache_hit_rate | gauge | System Telemetry | 60s |

### 19.2 审计集成

每个优化动作记录到 Audit Trail：

```python
audit_entry = {
    "actor": "ResourceOptimizationEngine",
    "action": "optimize",
    "strategy": strategy.value,
    "pressure_before": snapshot_before.pressure.value,
    "pressure_after": snapshot_after.pressure.value,
    "memory_before_gb": snapshot_before.memory_used_gb,
    "memory_after_gb": snapshot_after.memory_used_gb,
    "quality_preserved": result.quality_preserved,
    "duration_ms": result.duration_ms,
    "timestamp": datetime.now().isoformat(),
}
```

### 19.3 健康检查端点

`health_check()` 返回的 `HealthCheckResult` 可被：
- HeartbeatServer 采集并上报
- MCP 工具 `resource_health` 暴露给 AI
- System Telemetry 的 health probe 定期检查

---

## 20. 高阶衍生项

> 以下是从本蓝图衍生出的二阶~N阶效应和补充设计，确保蓝图自洽性和完整性。

### 20.1 二阶效应：优化器自身的资源消耗

**问题**：优化器自身消耗 CPU（监控循环）+ 内存（缓存+历史记录），成为被优化对象的一部分。

**解决方案**：
- 监控循环 CPU 开销 < 1%（C11 验证项）
- 优化历史使用 SQLite 存储（非内存），单条记录 < 1KB
- 缓存内存开销有上限（max_entries=1000 × 平均 50KB = ~50MB）
- `self_health_check()` 每 5 分钟检查自身资源占用，超过阈值时自动降级监控频率

### 20.2 二阶效应：优化策略之间的冲突

**问题**：CACHE_WARM（预热缓存）和 MEMORY_COMPACT（释放内存）可能同时触发。

**解决方案**：
- ConflictResolver：WARNING 时 CACHE_WARM 优先，CRITICAL 时 MEMORY_COMPACT 优先
- 策略互斥表：每种策略声明 `excludes: [策略列表]`，执行前检查
- 同一监控周期内只执行一种策略（避免叠加效应）

### 20.3 二阶效应：优化动作的副作用

**问题**：停止守护线程可能影响依赖该线程的其他模块。

**解决方案**：
- 依赖图：DaemonRegistry 维护守护线程间的依赖关系
- 停止顺序：先停被依赖方，再停依赖方
- 恢复顺序：先启依赖方，再启被依赖方
- quality_preserved 硬约束：任何优化动作不得导致业务质量下降

### 20.4 三阶效应：优化历史的知识积累

**问题**：长期运行后，优化历史数据量增长。

**解决方案**：
- SQLite 存储：单表 + 时间分区索引
- 自动清理：超过 30 天的记录自动归档到 JSONL
- 查询优化：最近 1000 条常驻内存，其余按需查询
- 知识提取：每周自动分析优化历史，更新策略成功率排名

### 20.5 三阶效应：跨 Session 优化知识传递

**问题**：AI session 结束后，优化知识如何传递给下一个 session。

**解决方案**：
- 优化历史持久化到 SQLite（跨 session 保留）
- Session 交接时，SelfMonitor 写入当前资源状态到 session-logs
- 新 session 冷启动时，ResourceOptimizationEngine 自动加载最近优化历史
- 知识库集成：高价值优化案例自动写入 KE（Knowledge Entry）

### 20.6 四阶效应：优化策略的进化

**问题**：固定的优化策略可能不适应未来新的资源瓶颈。

**解决方案**：
- 策略注册表：OptimizationStrategy 枚举可扩展（§3.6 契约版本保证向后兼容）
- 策略效果评分：每次执行后记录效果（内存降低量、CPU 降低量）
- 策略淘汰：连续 10 次效果为负的策略自动降级（降低优先级）
- Feedback Loop 集成：资源异常模式可注册为新的 Feedback Loop detector

### 20.7 四阶效应：1,500 模块下的优化器可扩展性

**问题**：1,500 模块时，优化器自身需要管理 300 个守护线程 + 30 个进程 + 1000 个缓存条目。

**解决方案**：
- 守护线程分组：按功能域分组调度（每组一个调度批次）
- 进程池分层：核心进程池（10 个）+ 扩展进程池（20 个，按需创建）
- 缓存分层：热缓存（最近 100 条，常驻内存）+ 温缓存（101-1000 条，LRU）+ 冷缓存（SQLite）
- 监控分层：核心指标（CPU/内存）30s + 扩展指标（磁盘/进程）60s + 详细指标（线程/缓存）120s

### 20.8 五阶效应：元优化——优化优化过程本身

**问题**：优化策略的参数（阈值、频率、批量大小）是否最优？

**解决方案**：
- 参数自调优：基于优化历史，自动调整参数（如 WARNING 阈值从 75% 调整到 72%）
- A/B 测试：对相同压力场景，交替使用不同参数，比较效果
- 安全边界：参数调整范围有上下限（如 WARNING 阈值只能在 60%-85% 之间）
- 人类审批：参数调整超过 5% 需 Owner 确认

### 20.9 五阶效应：优化器的安全防护

**问题**：恶意 AI 或配置篡改可能导致优化器执行危险操作。

**解决方案**：
- Agent RBAC 集成：优化操作需要 `resource:optimize` 权限
- 操作白名单：只允许执行 OptimizationStrategy 枚举中定义的策略
- 审计追踪：每个优化动作记录到 Audit Trail（不可篡改）
- 紧急停止：`force_pressure(EMERGENCY)` 需要 Owner 审批
- LLM Security 集成：优化指令经过 LSG 扫描，防止注入攻击

### 20.10 六阶效应：优化器与系统重组的协同

**问题**：GOV-RSTR-001 系统重组总蓝图可能拆分/合并模块，影响优化器的守护线程注册表。

**解决方案**：
- 模块诞生注册表集成：新模块创建时自动注册到 DaemonRegistry
- 模块废弃通知：模块废弃时自动从 DaemonRegistry 注销
- 蓝图-代码同步器集成：蓝图变更时自动更新优化策略配置
- Orphan Judge 集成：孤儿守护线程自动检测和清理

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 资源优化引擎架构设计 | **本文档 §1-§10** | — |
| 资源优化引擎施工步骤 | **本文档 §11** | — |
| 资源优化引擎接口契约 | **本文档 §3** | — |
| MAPE-K 详细设计 | **本文档 §12** | — |
| 压力状态机设计 | **本文档 §13** | — |
| 降级矩阵 | **本文档 §14** | — |
| AI 可发现性设计 | **本文档 §16** | — |
| 高阶衍生项 | **本文档 §20** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 使用方式 |
|:----:|--------|---------|
| 1 | FeedbackLoopScheduler | 注册为守护线程 + 自适应调度 |
| 1 | ResourceGuard | 注册为守护线程 + 优化 I/O |
| 1 | SelfMonitor | 注册为守护线程 + 流式读取 |
| 1 | AuditWriter | 使用 io_cache + append 写入 |
| 1 | HeartbeatServer | 注册为守护线程 + 单例保护 |
| 2 | CollectionManager | 定期 purge_expired() |
| 2 | MCP Gateway | 进程池复用 |
| 2 | EventBus | 压力变化事件消费 |
| 2 | System Telemetry | SLI 指标上报 |
| 2 | Audit Trail | 优化动作审计 |
| 2 | Gate Engine | 资源检查门禁 |
| 2 | Budget Enforcer | 预算降级联动 |
| 2 | Drift Detector | 配置漂移检测 |
| 3 | Agent Spec | 技能注册 + 发现 |
| 3 | MCP Servers | 工具暴露 |
| 3 | Blueprint Routing | 路由发现 |
| 3 | 所有新 AI session | 通过三重发现机制使用 |

### 变更同步规则

| 变更类型 | Tier 1（直接消费者） | Tier 2（系统集成） | Tier 3（AI 可发现性） |
|---------|------------------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 | 更新 MCP 工具契约 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 | 更新技能描述 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 | 更新蓝图路由关键字 |
| 新增优化策略 | 无影响 | 更新降级矩阵 | 更新技能描述 + MCP 工具 |
| 修改压力阈值 | 无影响 | 更新 SLI 指标 | 无影响 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§3） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| 新增优化策略 | AI 可自主 + 更新 §3 枚举 + 通知 Tier 2 |
| 修改压力阈值 | AI 可自主 + 更新 §4 + 通知 Tier 2 |
| 施工步骤微调 | AI 可自主修改 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 |
| force_pressure() 调用 | 需 Owner 审批 |

### 变更记录

| 版本 | 日期 | 作者 | 变更 |
|------|------|------|------|
| 1.0.0 | 2026-05-08 | human_plus_agent | 全面升级：Pydantic V2 数据模型、MCP 接口、契约版本、压力状态机、MAPE-K 详细设计、降级矩阵、断路器、背压、自愈闭环、配置管理、AI 可发现性三重机制、全系统集成契约（EventBus/ContractBus/API_INDEX/Gate/SLI/Audit）、高阶衍生项（二阶~六阶）、注册表登记完整清单（13 个注册表）、7 Phase 施工指引 |
| 0.1.0 | 2026-05-08 | human_plus_agent | 初始创建 |
