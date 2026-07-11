---
module_id: MOD-INF-002
submodule_path: src/zephyr/infrastructure/runtime
title: "Runtime Integration 蓝图 — 15核心RI模块跨层协同与运行时基础设施"
doc_type: blueprint
status: Active
version: 6.1.1
layer: L0_infrastructure
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.1
valid_from: 2026-05-01
date: "2026-05-01"
ttl: permanent
construction_progress: completed
actual_disk_path: "src/zephyr/shared/ + src/zephyr/infrastructure/ + src/zephyr/governance/lifecycle_governance/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L2
codification_at: "2026-05-15"
last_verified: "2026-05-15"
last_updated: "2026-05-15"
generation: 7
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
references: []
depends_on:
  - target: MOD-INF-001
    at: §10
    why: 容量保障规则
  - target: MOD-INF-016
    at: §10
    why: Shared Core 承载
priority: P0
runtime_plane: hot
tags:
  - runtime_integration
  - ri-modules
  - event-bus
  - infrastructure
  - shared_core-integration
  - structured-concurrency
  - graceful-shutdown
  - trading-kill-switch
  - module-sandbox
  - auto-decide-engine
  - model-fallback
  - cicd-pipeline
  - vibe-coding
  - owner-cognitive-load
  - trading-mode
  - deterministic-random
  - communication-patterns
  - deprecation-lifecycle
  - pre-trade-risk
summary: >
  15核心RI模块跨层协同+48项设计约束+交易基础设施+模块通信模式+确定性复现+AI施工模式库。v6.1.0模板v3.5/v3.6升级完成。
responsibility_domain: 
design_maturity: prototype
build_status: generated
---

> actual_disk_path: src/zephyr/shared/ (Shared Core 承载) + src/zephyr/infra_ops/ (独立落地) + src/zephyr/lifecycle_manager/ (RI-02)

# Runtime Integration 蓝图 — 15核心RI模块跨层协同与运行时基础设施

> **真源声明**：本蓝图是 ZephyrAlpha 运行时集成体系的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 运行时集成体系——它解决了 14 层模块的跨层协同问题。核心职责包括：异步事件分发(EventBus)、模块生命周期管理、韧性保障(熔断/限流/降级)、安全审计、可观测性、可溯源性与模拟。当前规模 15 个 RI 模块，目标容量 1,500 模块 × 14 层。上游依赖 MOD-INF-016 Shared Core 承载层，下游被所有 D_FACTOR-实验 层模块消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> 防止 construction_progress 与实际代码不符。
> 每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§14）。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> 路径约定：相对于 `src/zephyr/`。标注"Shared Core 承载"的文件归属 MOD-INF-016，[BLUEPRINT] 应标注 MOD-INF-016。
> 顶层 re-export wrapper（如 `shared/observer.py`→`shared/infra/observer.py`）不在本表逐一列出，见下方"Re-export Wrapper 清单"。
> **存在性状态受控词表**：`未实现` / `已实现` / `已阻塞` / `已废弃`
> - `已实现`：代码已存在且通过验证 → 蓝图不再重复代码内容，接口签名见 §4
> - `已阻塞`：因外部依赖未就绪无法实现 → MUST 注明阻塞原因
> - `已废弃`：设计变更后不再需要 → MUST 在 §5.3 迁移方案中说明
> - 此列是**当前事实**（永久时态），不是施工进度追踪（临时时态）

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-002`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） | 承载 |
|---|--------|------------|------|:-----:|-------------------|------|
| 1 | shared/infra/observer.py | §1 RI-01 | EventBus Pub/Sub 基类 | 已实现 | — | Shared Core |
| 2 | shared/event_bus.py | §1 RI-01 | EventBus 背压控制+DomainEvent | 已实现 | — | Shared Core |
| 3 | shared/events/event_schemas.py | §1 RI-01 | 事件体 Pydantic V2 Schema | 已实现 | — | Shared Core |
| 4 | shared/events/dlq.py | §1 RI-01 | DLQ SQLite 持久化 | 已实现 | — | Shared Core |
| 5 | shared/events/dlq_bridge.py | §1 RI-01 | DLQ→Observer 集成桥 | 已实现 | — | Shared Core |
| 6 | lifecycle_manager/hooks.py | §1 RI-02 | ModuleLifecycle LifecycleAware | 已实现 | — | Shared Core |
| 7 | shared/config/loader.py | §1 RI-03 | YAML 配置加载+Pydantic 校验 | ❌ ARCH-038 已退役 | 虚假统一空壳(0消费者) | Shared Core |
| 8 | shared/foundation/flags.py | §1 RI-03 | FeatureFlag 三态+灰度 | 已实现 | — | Shared Core |
| 10 | shared/resilience/circuit_breaker.py | §1 RI-05 | 熔断器状态机 | 已实现 | — | Shared Core |
| 11 | shared/resilience/retry.py | §1 RI-05 | 统一重试策略 | 已实现 | — | Shared Core |
| 12 | shared/resilience/fallback.py | §1 RI-05 | 降级策略模式 | 已实现 | — | Shared Core |
| 13 | shared/infra/limiter.py | §1 RI-05 | 速率限制器 Token Bucket | 已实现 | — | Shared Core |
| 14 | shared/infra/idempotency.py | §1 RI-06 | 幂等性存储/检查 | 已实现 | — | Shared Core |
| 15 | shared/security/secrets.py | §1 RI-07 | Secrets 管理抽象 | 已实现 | — | Shared Core |
| 16 | shared/foundation/errors.py | §1 RI-08 | 统一错误层次 | 已实现 | — | Shared Core |
| 17 | shared/observability/logging.py | §1 RI-08 | 结构化日志+trace_id 传播 | 已实现 | — | Shared Core |
| 18 | shared/observability/tracing.py | §1 RI-08 | 分布式追踪 OTLP | 已实现 | — | Shared Core |
| 19 | shared/observability/health.py | §1 RI-09 | 聚合健康检查三级状态 | 已实现 | — | Shared Core |
| 20 | shared/observability/health_discovery.py | §1 RI-09 | 健康发现注册 | 已实现 | — | Shared Core |
| 21 | shared/observability/metrics.py | §1 RI-10 | Metrics 收集基础设施 | 已实现 | — | Shared Core |
| 22 | shared/infra/cache.py | §1 RI-11 | 统一缓存抽象 | 已实现 | — | Shared Core |
| 24 | infra_ops/auto_diagnostics.py | §1 RI-12 | AutoDiagnostics 自动诊断（含诊断反转验证：深挖后回溯初始诊断） | 已实现 | — | 独立落地 |
| 25 | infra_ops/event_store.py | §1 RI-13 | EventStore 事件存储 | 已实现 | — | 独立落地 |
| 26 | infra_ops/dry_run_simulator.py | §1 RI-14 | DryRunSimulator 干运行模拟 | 已实现 | — | 独立落地 |
| 27 | infra_ops/cost_tracker.py | §1 RI-15 | CostTracker 成本追踪 | 已实现 | — | 独立落地 |
| 28 | infra_ops/kill_switch_sim.py | §3 B5-K01 | KillSwitch 硬件模拟器 | 已实现 | — | 独立落地 |

**Re-export Wrapper 清单**（顶层别名→canonical，仅 re-export，不包含独立逻辑）：

| wrapper | canonical |
|--------|-----------|
| shared/observer.py | shared/infra/observer.py |
| shared/flags.py | shared/foundation/flags.py |
| shared/errors.py | shared/foundation/errors.py |
| shared/logging.py | shared/observability/logging.py |
| shared/health.py | shared/observability/health.py |
| shared/idempotency.py | shared/infra/idempotency.py |
| shared/secrets.py | shared/security/secrets.py |
| shared/cache.py | shared/infra/cache.py |
| shared/metrics.py | shared/observability/metrics.py |

**路径修正记录**：

| 旧路径（蓝图 v5/v6） | 新路径（实际） | 原因 |
|---------------------|-------------|------|
| shared/production/idempotency.py | shared/infra/idempotency.py | `shared/production/` 目录不存在 |
| shared/production/secrets.py | shared/security/secrets.py | `shared/production/` 目录不存在 |
| shared/production/metrics.py | shared/observability/metrics.py | `shared/production/` 目录不存在 |
| shared/production/cache.py | shared/infra/cache.py | `shared/production/` 目录不存在 |
| shared/config/（目录） | ❌ ARCH-038 已删除 | 虚假统一空壳，目录已移除 |
| shared/resilience/（目录） | shared/resilience/circuit_breaker.py 等 | 展开为具体文件 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| §0.1 清单中 27/28 文件存在（#9 未实现） | `ls src/zephyr/shared/infra/observer.py` 等逐文件核对 | ☑ |
| RI-12/13/14/15 独立落地文件已存在 | `ls src/zephyr/infrastructure/runtime_integration/auto_diagnostics.py` 等 | ☑ |
| shared/production/ 路径已修正为实际路径 | §0.1 路径修正记录 | ☑ |
| Shared Core 承载文件与 MOD-INF-016 蓝图一致 | 交叉验证 MOD-INF-016 §0 | ☑ |
| re-export wrapper 指向正确的 canonical 文件 | 逐文件读取 wrapper 头部 | ☑ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v5.0.1 (基线) | 15 RI 模块 + 29 代码骨架 + 48 RL 约束 | — | — |
| v6.0.0 (模板v3.3重构) | 同 v5.0.1 + 新增§3.2数据流+§6错误处理+§9测试策略+§12集成目标+§14风险+§16施工指引+§18决策记录 | — | 结构重组，无功能变更 |
| v6.1.0 (模板v3.5/v3.6升级) | 同 v6.0.0 + §0前移+§7/§15删除+§14增加类型列+§10拆分+铁律#13~#15 | — | 模板合规升级，无功能变更 |

---

## §1 设计背景与目标

### 1.1 背景

运行时集成（Runtime Integration）是 ZephyrAlpha 基础设施层的**横切能力集合**，解决 14 层模块的跨层协同问题。

#### 通信与生命周期层

| RI 模块 | 名称 | 核心职责 | 权限 | MOD-INF-016 承载 |
|---------|------|---------|------|:--:|
| **RI-01** | EventBus | 异步事件分发（pub/sub）+ 消费者组 + 保序 + DLQ持久化 + IdempotencyGuard + 背压传导链 + 事件优先级 | Immutable Core | `shared/observer.py` + `shared/events/` |
| **RI-02** | ModuleLifecycle | 拓扑排序启动/版本约束/超时控制/热重载/优雅关闭协议/预热期/Crash-Only设计/自描述元数据 | Immutable Core | `lifecycle_manager/hooks.py` |
| **RI-03** | ConfigCenter | 分层配置 + 热重载 + Feature Flags（渐进推出+交互矩阵+Kill Switch）+ 写入校验 + Schema兼容性策略 + 配置审计 + 回滚 | Human-Gated | `shared/config/` |
| **RI-04** | DependencyInjector | 模块间引用获取的统一入口——构造注入 + 接口绑定 + 循环依赖检测 | Immutable Core | `shared/production/di_container.py` (planned) |

#### 韧性与可靠性层

| RI 模块 | 名称 | 核心职责 | 权限 | MOD-INF-016 承载 |
|---------|------|---------|------|:--:|
| **RI-05** | ResilienceGuard | 运行时熔断器(CircuitBreaker) + 限流器(RateLimiter) + 降级链(GracefulDegradation) + 超时传播(TimeoutContext) + Bulkhead舱壁隔离 + 负载脱落(LoadShedder) + 重试风暴防护(RetryBudget) + 自适应并发限制 | Immutable Core | `shared/resilience/` |
| **RI-06** | IdempotencyGuard | 写操作去重——idempotency_key 驱动 + TTL分级(关键流ES天然去重/非关键流SQLite TTL) + 乐观并发控制 | Immutable Core | `shared/production/idempotency.py` |

#### 安全与审计层

| RI 模块 | 名称 | 核心职责 | 权限 | MOD-INF-016 承载 |
|---------|------|---------|------|:--:|
| **RI-07** | SecretsManager | API Key/密码加密存储 + 轮转提醒 + 访问审计 + 泄露检测 + AI 注入隔离。ConfigCenter加密字段强制走本模块 | Human-Gated | `shared/production/secrets.py` |
| **RI-08** | ErrorHandler | SRE 对齐错误分类 + 聚合 + W3C Trace Context传播 + Retry Policy 联动 + CircuitBreaker 联动 + trace_id 跨进程传播 | Immutable Core | `shared/errors.py` + `shared/logging.py` |

#### 可观测性与自治层

| RI 模块 | 名称 | 核心职责 | 权限 | MOD-INF-016 承载 |
|---------|------|---------|------|:--:|
| **RI-09** | HealthCheck | 三级健康(UP/DEGRADED/DOWN) + 具体SLI阈值 + 容量健康 + 合成事务 + 故障域隔离 + 自愈触发 + Reconciliation Loop持续对账 | Human-Gated | `shared/health.py` |
| **RI-10** | TelemetryCollector | 多 Plane 指标聚合 + 基数限制(per-module 500) + 直方图 + Exemplar + 多维聚合 + 推送降级 + AI 行为特化 + Prompt Fingerprint + 死模块检测 | AI-Modifiable | `shared/production/metrics.py` |
| **RI-11** | CacheLayer | 统一缓存——LRU 本地 + 语义缓存(VMS) + TTL 分层 + 缓存一致性协议 + Data Locality/Affinity | AI-Modifiable | `shared/production/cache.py` |
| **RI-12** | AutoDiagnostics | 异常→自动诊断报告 + Runbook 匹配 + AI 修复建议 + 修复后自动补充知识库 + 信任衰减曲线 + 自限反馈 + Owner 异步通知 | AI-Modifiable | — |

#### 可溯源性与模拟层

| RI 模块 | 名称 | 核心职责 | 权限 | MOD-INF-016 承载 |
|---------|------|---------|------|:--:|
| **RI-13** | EventStore | Event Sourcing + CQRS 读模型 + 事件溯源 + 快照(Snapshot) + 时间旅行重放(写隔离) + Crypto-Shredding + Saga补偿事务(触发式) | Immutable Core | — |
| **RI-14** | DryRunSimulator | AI 操作预演——sandbox 执行 + 影响分析 + 差异报告 + 人工/AI审批前置 + 行为一致性验证 + 跨Session Loop检测 + AI自预演 | Human-Gated | — |
| **RI-15** | CostTracker | 全资源FinOps成本归属——per-module / per-session / per-model 费用追踪 + 计算/存储/网络费用 + 预算告警 + 优化建议 + 模块可维护性评分 | AI-Modifiable | — |

**设计容量**：所有模块数 × 14 层 = 1500 模块，RI 各组件不漏不崩。

#### 与 Shared Core (MOD-INF-016) 的承载关系

> MOD-INF-016 Shared Core（v0.14.0，49文件，施工completed）已实现大量RI模块的代码承载。下表声明明确的职责分工。

| RI 模块 | 蓝图设计归属 | 代码承载归属 | 承载文件 | 备注 |
|---------|:--:|:--:|------|------|
| RI-01 EventBus | MOD-INF-002 | **MOD-INF-016** | `shared/observer.py` + `shared/events/` + `shared/events/dlq.py` | shared 版为基类实现；MOD-INF-002 蓝图定义增强需求（PriorityQueue/背压传导链），在 shared 层扩展 |
| RI-02 ModuleLifecycle | MOD-INF-002 | **MOD-INF-016** | `lifecycle_manager/hooks.py` | shared 版定义 LifecycleAware Protocol；MOD-INF-002蓝图扩展优雅关闭协议+预热期 |
| RI-03 ConfigCenter | MOD-INF-002 | **MOD-INF-016** | `shared/config/` + `shared/flags.py` | shared 版提供加载+校验+FeatureFlag；MOD-INF-002蓝图定义渐进推出+交互矩阵 |
| RI-04 DependencyInjector | MOD-INF-002 | **MOD-INF-016** (planned) | `shared/production/di_container.py` (待施工) | 统一由 shared 承载，不做独立 `infra_ops/dependency_injector.py` |
| RI-05 ResilienceGuard | MOD-INF-002 | **MOD-INF-016** | `shared/resilience/` | shared 版提供 CircuitBreaker/Retry/Fallback；MOD-INF-002蓝图扩展Bulkhead/LoadShedder/RetryBudget |
| RI-06 IdempotencyGuard | MOD-INF-002 | **MOD-INF-016** | `shared/production/idempotency.py` | shared 版为基础实现；MOD-INF-002蓝图定义TTL分级策略 |
| RI-07 SecretsManager | MOD-INF-002 | **MOD-INF-016** | `shared/production/secrets.py` | — |
| RI-08 ErrorHandler | MOD-INF-002 | **MOD-INF-016** | `shared/errors.py` + `shared/logging.py` | shared 版提供异常树+trace_id；MOD-INF-002蓝图扩展W3C Trace Context |
| RI-09 HealthCheck | MOD-INF-002 | **MOD-INF-016** | `shared/health.py` | shared 版提供 AggregateHealth；MOD-INF-002蓝图定义具体SLI阈值+Reconciliation |
| RI-10 TelemetryCollector | MOD-INF-002 | **MOD-INF-016** | `shared/production/metrics.py` | shared 版提供基础metrics；MOD-INF-002蓝图扩展PromptFingerprint+DeadModuleDetector |
| RI-11 CacheLayer | MOD-INF-002 | **MOD-INF-016** | `shared/production/cache.py` | shared 版为基础实现；MOD-INF-002蓝图扩展Data Locality |
| RI-12 AutoDiagnostics | MOD-INF-002 | **独立落地** | `infra_ops/auto_diagnostics.py` | 共享核心无对应实现——100%新施工 |
| RI-13 EventStore | MOD-INF-002 | **独立落地** | `infra_ops/event_store.py` | 共享核心无对应实现——Phase 3 触发式落地 |
| RI-14 DryRunSimulator | MOD-INF-002 | **独立落地** | `infra_ops/dry_run_simulator.py` | 共享核心无对应实现——Phase 2b |
| RI-15 CostTracker | MOD-INF-002 | **独立落地** | `infra_ops/cost_tracker.py` | 共享核心无对应实现——Phase 2b |

> **职责准则**：MOD-INF-002 定义"运行时集成体系需要什么"（WHAT + WHY），MOD-INF-016 承载"公共实现"（HOW）。若 shared 版已足够，RI 模块直接消费 shared；若需要增强，在 shared 层扩展而非独立重写。仅 RI-12/13/14/15 因 shared 无对应能力，独立落地 `infra_ops/`。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 跨层通信统一 | 14层模块通过EventBus通信，P99延迟≤100ms |
| 2 | 模块生命周期管理 | 500模块拓扑排序≤50ms，优雅关闭0数据丢失 |
| 3 | 韧性保障 | 熔断/限流/降级/隔离四重防护，CRITICAL事件丢弃率0% |
| 4 | 1人+AI自愈 | 90%异常自动修复，Owner日均告警≤10条 |
| 5 | 全资源FinOps | per-module费用归属100%覆盖，LLM月费≤$50 |
| 6 | 零依赖优先 | Python stdlib + SQLite完成核心功能，外部依赖最小化 |
| 7 | 确定性复现 | 固定种子→同输入同输出，回测可复现 |
| 8 | 交易安全 | KillSwitch 5步停止序列，Paper模式AI施工默认 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | AI 审计守卫实现 | → MOD-INF-001 |
| 2 | 安全网关实现 | → MOD-LLM_SECURITY |
| 3 | 因子计算逻辑 | → D_FACTOR-D_SIGNAL 业务层 |
| 4 | 审计追踪链存储 | → MOD-INF-020 |
| 5 | 回滚执行 | → MOD-INF-021 |
| 6 | 任务门禁 | → MOD-GATE_ENGINE |
| 7 | Shared Core 实现细节 | → MOD-INF-016 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Windows 单机部署 | 无分布式协调需求，SQLite WAL 足够 |
| 1人+AI 运维 | 系统必须90%异常自愈，Owner告警预算≤10条/日 |
| 15 个 RI 模块 | 设计容量1500模块×14层，当前规模验证 |
| 零依赖优先 | 能用 Python stdlib + SQLite 完成的不引入新依赖 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | RI-01 ~ RI-15 模块设计+实现 | 15个RI模块的完整设计、代码骨架、落地方案 |
| 2 | Cross-Layer 设计约束落地 | RL-001 ~ RL-048 + B4/B5 系列约束 |
| 3 | 失败模式+降级路径 | 所有 RI 模块的 FMEA + 降级链 |
| 4 | 自愈能力设计 | 1人+AI 运维语境下的自动诊断/修复/升级 |
| 5 | Shared Core 承载关系 | 与 MOD-INF-016 的职责边界与代码承载映射 |
| 6 | 五视图体系 | 静态拓扑/动态行为/故障传播/容量伸缩/Owner感知 |
| 7 | KB 决策记录 架构决策记录 | 关键设计决策的依据和替代方案 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | AI 审计守卫 | MOD-INF-001（capacity_assurance） |
| 2 | 安全网关（LSG） | MOD-LLM_SECURITY（llm_security） |
| 3 | 因子计算逻辑 | D_FACTOR-D_SIGNAL 业务层 |
| 4 | 审计追踪链存储 | MOD-INF-020（audit-trail），RI-13 EventStore 提供事件级溯源 |
| 5 | 回滚执行 | MOD-INF-021（rollback-system），RI-13 事件重放可配合回滚 |
| 6 | 任务门禁（G0-G7） | MOD-GATE_ENGINE（gate_engine） |
| 7 | Shared Core 实现细节 | MOD-INF-016（shared_core）——本蓝图定义需求，MOD-INF-016 承载实现 |

---

## §3 架构设计

### 3.1 组件架构

| 组件 | 层级 | 核心类/协议 | 依赖 | 状态 |
|------|------|-----------|------|------|
| RI-01 EventBus | 通信与生命周期 | `EventBus`, `EventConsumer`, `BackpressurePropagator` | RI-06, RI-05 | ✅ MOD-INF-016 承载 |
| RI-02 ModuleLifecycle | 通信与生命周期 | `LifecycleAware`, `GracefulShutdown` | — | ✅ MOD-INF-016 承载 |
| RI-03 ConfigCenter | 通信与生命周期 | `ConfigCenter`, `FeatureFlagManager` | RI-07 | ✅ MOD-INF-016 承载 |
| RI-04 DependencyInjector | 通信与生命周期 | `DIContainer` | RI-02 | ❌ planned |
| RI-05 ResilienceGuard | 韧性与可靠性 | `CircuitBreaker`, `Bulkhead`, `LoadShedder`, `RetryBudget` | — | ✅ MOD-INF-016 承载 |
| RI-06 IdempotencyGuard | 韧性与可靠性 | `IdempotencyGuard` | — | ✅ MOD-INF-016 承载 |
| RI-07 SecretsManager | 安全与审计 | `SecretsManager` | — | ✅ MOD-INF-016 承载 |
| RI-08 ErrorHandler | 安全与审计 | `ErrorHandler`, `W3CTraceContext` | RI-05 | ✅ MOD-INF-016 承载 |
| RI-09 HealthCheck | 可观测性与自治 | `HealthCheck`, `ReconciliationLoop` | RI-12 | ✅ MOD-INF-016 承载 |
| RI-10 TelemetryCollector | 可观测性与自治 | `TelemetryCollector`, `PromptFingerprint` | RI-12, RI-15 | ✅ MOD-INF-016 承载 |
| RI-11 CacheLayer | 可观测性与自治 | `CacheLayer` | RI-15 | ✅ MOD-INF-016 承载 |
| RI-12 AutoDiagnostics | 可观测性与自治 | `AutoDiagnostics`, `TrustDecayTracker` | RI-09 | ✅ 独立落地 |
| RI-13 EventStore | 可溯源性与模拟 | `EventStore`, `CryptoShredding`, `SagaCoordinator` | RI-01, RI-06 | ✅ 独立落地 |
| RI-14 DryRunSimulator | 可溯源性与模拟 | `DryRunSimulator`, `CrossSessionLoopDetector` | RI-01, RI-15 | ✅ 独立落地 |
| RI-15 CostTracker | 可溯源性与模拟 | `CostTracker`, `MaintainabilityScore` | — | ✅ 独立落地 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_FACTOR-实验 业务模块 | EventBus publish → PriorityQueue → consumer group dispatch | RI 消费者 | Pydantic Event |
| 2 | EventBus DLQ | 失败事件 → SQLite持久化 → 指数退避重试 | 原消费者 | DLQEntry |
| 3 | HealthCheck 探针 | async check → SLI阈值比对 → 三级状态判定 | AutoDiagnostics / Owner | HealthStatus |
| 4 | ConfigCenter 变更 | YAML reload → Pydantic校验 → FeatureFlag评估 → 事件通知 | 所有订阅模块 | ConfigEvent |
| 5 | AI 写操作 | DryRunSimulator sandbox → diff报告 → 审批门 → 执行 | 目标模块 | SimulationResult |
| 6 | LLM API 调用 | CostTracker 拦截 → token计数 → 美元换算 → 预算检查 | Owner日报 | CostEntry |

### 3.3 状态生命周期

| 状态 | 含义 | 转换条件 |
|------|------|---------|
| PLANNED | 设计完成，未施工 | → SCAFFOLDED: scaffold.py 创建文件 |
| SCAFFOLDED | 文件已创建，代码骨架就绪 | → IMPLEMENTED: 核心逻辑实现完成 |
| IMPLEMENTED | 核心逻辑完成，测试通过 | → INTEGRATED: 与其他 RI 模块联调通过 |
| INTEGRATED | 联调通过，Phase 验收完成 | → PRODUCTION: 生产环境部署 |
| PRODUCTION | 生产运行 | → DEPRECATED: 标记废弃 |
| DEPRECATED | 标记废弃，仍可用 | → ARCHIVED: 迁移完成后归档 |
| ARCHIVED | 归档，只读 | — 终态 |

### 蓝图特有：终选技术栈

| 组件 | 终选 |
|------|------|
| RI-01 EventBus | **asyncio.PriorityQueue（四级优先级）+ Pydantic 类型化事件 + DLQ SQLite持久化 + 背压信号 + DeliverySemantics: AT_LEAST_ONCE** |
| RI-02 ModuleLifecycle | **ABC + 拓扑排序(BFS) + register/unregister + 版本范围约束 + 优雅关闭协议(drain→timeout→force_kill) + Crash-Only设计** |
| RI-03 ConfigCenter | **YAML + os.environ 覆盖 + Pydantic 校验 + watchdog 热重载 + Feature Flags（渐进推出+交互矩阵+Kill Switch）** |
| RI-04 DependencyInjector | **由 MOD-INF-016 `shared/production/di_container.py` 统一承载——构造注入 + ABC 接口绑定 + 循环检测** |
| RI-05 ResilienceGuard | **CircuitBreaker(三态) + TokenBucket(限流) + TimeoutContext + 降级链 YAML + Bulkhead(per-module线程/连接池上限) + LoadShedder(优先级丢弃) + RetryBudget(全局配额)** |
| RI-06 IdempotencyGuard | **分级策略：关键流(风控/交易/仓位)走 ES expected_version 天然去重；非关键流 SHA-256 + SQLite TTL** |
| RI-07 SecretsManager | **AES-256-GCM 本地加密 + .env 自动加解密 + 访问审计发射** |
| RI-08 ErrorHandler | **Enum(SRE分类) + Structlog 结构化 + W3C traceparent header + trace_id跨进程传播 + 聚合窗口** |
| RI-09 HealthCheck | **async 探针 + 依赖传导 + 三级状态 + 具体SLI阈值(CPU>80%→DEGRADED,>95%→DOWN;错误率>5%→DEGRADED,>10%→DOWN) + Reconciliation Loop持续对账** |
| RI-10 TelemetryCollector | **structlog 聚合 + per-module基数限制(500) + 超限LRU淘汰+告警 + 直方图 + Exemplar + 10s 推送 + PromptFingerprint + DeadModuleDetector** |
| RI-11 CacheLayer | **LRU dict + VMS 语义缓存 + TTL 分层(Hot/Warm/Cold) + DataAffinity hints** |
| RI-12 AutoDiagnostics | **HealthCheck 触发 + Runbook YAML 匹配 + 诊断报告 Markdown生成 + 修复后→KB自动补充 + TrustDecayTracker + SelfLimiter** |
| RI-13 EventStore | **SQLite append-only event_log 表 + 快照表(每1000事件) + CQRS读模型(SQLite View) + Crypto-Shredding + SagaCoordinator(Phase 4触发)** |
| RI-14 DryRunSimulator | **sandbox=True 标志位 + 拦截写操作→日志输出 + diff报告生成 + approval gate + 一致性验证套件 + CrossSessionLoopDetector + SelfSimulate** |
| RI-15 CostTracker | **LLM调用拦截→token计数→美元换算 + CPU/内存/IO记录 + per-module/session tag归属 + 模块可维护性评分 + 飞书日报** |

### 蓝图特有：设计原则

| 原则 | 内容 |
|------|------|
| Crash-Only | 系统不依赖"优雅关闭"——每次停止=crash，每次恢复=重启。所有状态持久化，重启后自动从SQLite重建内存状态 |
| Structured Concurrency | 使用 `asyncio.TaskGroup` 管理1500+模块的并发生命周期——子任务全部完成或全部取消，无孤儿协程 |
| Fail-Closed | 安全组件（SecretsManager/ErrorHandler）不可用时拒绝操作而非放行 |
| Immutable Events | RI-13 EventStore 事件一旦写入不可修改/不可删除——审计完整性不可妥协 |
| Progressive Disclosure | 容量模型和告警按 Owner 注意力预算分级——实时仅推送CRITICAL，其余汇总 |

### 蓝图特有：关键代码骨架（29个）

#### DeliverySemantics（消息传递语义）

```python
from enum import Enum

class DeliverySemantics(Enum):
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"

class EventPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
```

#### BackpressurePropagation（背压传导）

```python
@dataclass
class BackpressureSignal:
    source_module: str
    queue_usage_pct: float
    severity: str
    affected_upstream: list[str]

class BackpressurePropagator:
    _thresholds: dict = {
        "warning": 0.80,
        "critical": 0.95,
    }

    async def propagate(self, signal: BackpressureSignal) -> None:
        for upstream_id in signal.affected_upstream:
            throttle_factor = self._calc_throttle(signal.queue_usage_pct)
            await EventBus.publish(BackpressureEvent(
                target_module=upstream_id,
                throttle_factor=throttle_factor
            ))
```

#### Bulkhead（舱壁隔离）

```python
class Bulkhead:
    _pools: dict[str, "ResourcePool"] = {}

    class ResourcePool:
        max_concurrent: int
        semaphore: asyncio.Semaphore

    def configure(self, module_id: str,
                  max_concurrent: int = 10,
                  max_db_connections: int = 5) -> None: ...

    async def acquire(self, module_id: str) -> AsyncContextManager:
        ...
```

#### LoadShedder（负载脱落）

```python
class LoadShedder:
    _overload_threshold: float = 0.80

    async def admit(self, request: "Request") -> bool:
        global_load = await self._measure_global_load()
        if global_load < self._overload_threshold:
            return True
        return request.priority <= EventPriority.HIGH
```

#### RetryBudget（重试配额）

```python
class RetryBudget:
    _budget_per_window: int = 100
    _used_this_window: int = 0
    _window_start: float = 0.0

    async def can_retry(self) -> bool:
        if time.monotonic() - self._window_start > 60.0:
            self._used_this_window = 0
            self._window_start = time.monotonic()
        return self._used_this_window < self._budget_per_window
```

#### 优雅关闭协议

```python
class GracefulShutdown:
    drain_timeout: float = 30.0
    force_kill_timeout: float = 5.0

    async def shutdown(self) -> ShutdownResult:
        EventBus.stop_accepting()
        in_flight = EventBus.drain(self.drain_timeout)
        if in_flight.timeout:
            EventBus.force_kill(self.force_kill_timeout)
        HealthCheck.persist_current_state()
        return ShutdownResult(pending_events=in_flight.remaining)
```

#### W3C TraceContext

```python
class W3CTraceContext:
    trace_id: str
    span_id: str
    trace_flags: int

    def to_traceparent(self) -> str:
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags:02x}"

    @classmethod
    def from_traceparent(cls, header: str) -> "W3CTraceContext": ...
```

#### Crypto-Shredding

```python
class CryptoShredding:
    _stream_keys: dict[str, bytes] = {}

    async def anonymize_stream(self, stream_id: str) -> None:
        del self._stream_keys[stream_id]
        audit.record(f"CRYPTO_SHRED: stream={stream_id}")
```

#### Saga Coordinator（触发式）

```python
class SagaCoordinator:
    _active_sagas: dict[str, "SagaInstance"] = {}

    async def start(self, saga_id: str,
                    steps: list["SagaStep"]) -> SagaResult: ...

    async def compensate(self, saga_id: str,
                         failed_step: int) -> CompensateResult:
        ...
```

#### Speculative Execution

```python
class SpeculativeExecutor:
    async def emit_with_hedge(self, event: Event,
                              replicas: int = 2) -> EventResult:
        tasks = [consumer.handle(event) for consumer in self._replicas[:replicas]]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        return done.pop().result()
```

#### Leader Election via SQLite Lease

```python
class SqliteLeaderElection:
    _lease_table = "leader_lease"
    _lease_id = "global_leader"
    _lease_ttl: float = 30.0
    _renew_interval: float = 10.0

    async def try_become_leader(self) -> bool:
        now = time.time()
        result = await self.db.execute(
            f"""INSERT OR REPLACE INTO {self._lease_table}
                (lease_id, node_id, acquired_at, expires_at)
                VALUES (?, ?, ?, ?)
                WHERE NOT EXISTS (
                    SELECT 1 FROM {self._lease_table}
                    WHERE lease_id = ? AND expires_at > ?
                )""",
            (self._lease_id, self.node_id, now, now + self._lease_ttl,
             self._lease_id, now)
        )
        return result.rowcount > 0

    async def is_leader(self) -> bool:
        row = await self.db.fetchone(
            f"SELECT node_id FROM {self._lease_table} "
            f"WHERE lease_id = ? AND expires_at > ?",
            (self._lease_id, time.time())
        )
        return row is not None and row[0] == self.node_id

    async def step_down(self) -> None:
        await self.db.execute(
            f"DELETE FROM {self._lease_table} WHERE node_id = ?",
            (self.node_id,)
        )
```

#### Module Sandbox（模块级进程隔离）

```python
class ModuleSandbox:
    _module_procs: dict[str, asyncio.subprocess.Process] = {}
    _crash_counter: dict[str, int] = {}

    async fn spawn_module(self, module_id: str,
                           entrypoint: str) -> None:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", f"zephyr.{module_id}",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        self._module_procs[module_id] = proc

    async def restart_if_crashed(self, module_id: str) -> bool:
        proc = self._module_procs.get(module_id)
        if proc and proc.returncode is not None:
            self._crash_counter[module_id] = self._crash_counter.get(module_id, 0) + 1
            if self._crash_counter[module_id] >= 5:
                await self.notify_owner(
                    f"💀 {module_id} 已连续crash 5次→已隔离，需Owner手动恢复"
                )
                return False
            await self.spawn_module(module_id, proc.entrypoint)
            return True
        return True
```

#### Sleep-Time Protocol（睡眠时段协议）

```python
class SleepTimeProtocol:
    _sleep_start: int = 23
    _sleep_end: int = 7
    _critical_suppressed: int = 0

    def is_sleep_time(self) -> bool:
        hour = datetime.now(tz=self._owner_tz).hour
        return hour >= self._sleep_start or hour < self._sleep_end

    async def handle_alert(self, alert: Alert) -> AlertDecision:
        if not self.is_sleep_time():
            return AlertDecision.SEND_NORMAL
        if alert.level == AlertLevel.CRITICAL:
            if self._critical_suppressed >= 1:
                return AlertDecision.AUTO_HEAL
            self._critical_suppressed += 1
            return AlertDecision.SEND_SINGLE
        return AlertDecision.QUEUE_FOR_MORNING
```

#### Auto-Decide Engine（自动决策引擎）

```python
class AutoDecideEngine:
    _thresholds: dict = {
        "impacted_modules": 3,
        "cost_impact_usd": 0.10,
        "risk_rpn": 50,
    }

    async fn decide(self, operation: "Operation") -> DecideResult:
        impact = await self._assess_impact(operation)
        if (impact.modules <= self._thresholds["impacted_modules"] and
            impact.cost <= self._thresholds["cost_impact_usd"] and
            impact.rpn <= self._thresholds["risk_rpn"]):
            log.info(f"🤖 {operation.id}: 自动执行——影响范围足够小无需Owner审批")
            return DecideResult(auto_approved=True)
        return DecideResult(needs_approval=True, reason=impact.summary())
```

#### Prompt Cache & Token Budget

```python
class PromptCacheManager:
    _cache: dict[str, tuple[float, str]] = {}
    _modules_total_tokens_this_session: dict[str, int] = {}

    async fn optimize_prompt(self, module_id: str,
                              raw_context: str,
                              user_intent: str) -> str:
        cache_key = sha256(user_intent.encode()).hexdigest()
        if cache_key in self._cache:
            ttl, cached = self._cache[cache_key]
            if time.time() < ttl:
                self._track_tokens(module_id, len(cached) // 4)
                return cached
        compressed = self._compress_context(raw_context, max_chars=8000)
        monthly_pct = self._get_monthly_token_pct(module_id)
        if monthly_pct > 0.80:
            compressed = f"[⚠️ Token预算已用{monthly_pct:.0%}] " + compressed[:4000]
        return compressed
```

#### Emergency Trading Kill Switch

```python
class TradingKillSwitch:
    _mode: str = "NORMAL"

    async def activate(self, reason: str,
                        confirmed_by: str = "AUTO") -> KillSwitchResult:
        results = []
        self._mode = "KILLED"
        results.append(await self._cancel_all_pending_orders())
        results.append(await EventBus.purge_events(
            event_types=["TradeEvent", "OrderEvent"]))
        results.append(await ModuleLifecycle.set_mode("D_PORTFOLIO_CORE", "READ_ONLY"))
        audit.record_severe(f"KILL_SWITCH: reason={reason} by={confirmed_by}")
        return KillSwitchResult(mode=self._mode, actions=results)

    async def deactivate(self, confirmed_by: str) -> KillSwitchResult:
        if confirmed_by != "Owner":
            raise PermissionError("Kill Switch 只能由 Owner 手动解除")
        self._mode = "NORMAL"
        await ModuleLifecycle.set_mode("D_PORTFOLIO_CORE", "NORMAL")
        return KillSwitchResult(mode=self._mode)
```

#### Simulated Clock

```python
class SimulatedClock:
    _mode: str = "REAL"
    _sim_time: float = 0.0

    def now(self) -> float:
        return time.time() if self._mode == "REAL" else self._sim_time

    async def sleep(self, duration: float) -> None:
        if self._mode == "REAL":
            await asyncio.sleep(duration)
        else:
            self._sim_time += duration

    async def advance_to(self, target_time: float) -> None:
        if self._mode != "SIMULATED":
            raise RuntimeError("advance_to 仅在 SIMULATED 模式可用")
        self._sim_time = max(self._sim_time, target_time)
```

#### Deterministic Random

```python
class DeterministicRandom:
    _seed: int = 42
    _rng: random.Random = field(default_factory=lambda: random.Random(42))

    def reseed(self, seed: int) -> None:
        self._seed = seed
        self._rng = random.Random(seed)
        random.seed(seed)
        numpy.random.seed(seed % (2**32 - 1))

    def uniform(self, a: float = 0.0, b: float = 1.0) -> float:
        return self._rng.uniform(a, b)

    def choice(self, seq: Sequence[T]) -> T:
        return self._rng.choice(seq)
```

#### Module Metadata & Self-Description

```python
class ModuleMetadata:
    module_id: str
    layer: str
    functional_domain: str
    capabilities: list[str]
    dependencies: list[str]
    api_version: str
    supports_backward: list[str]
    ai_confidence: float
    code_ownership: dict

    def describe(self) -> str:
        return (f"{self.module_id}@{self.api_version} "
                f"[{','.join(self.capabilities)}] "
                f"conf={self.ai_confidence:.0%}")
```

#### Module Template Skeleton

```python
from zephyr.shared.lifecycle import LifecycleAware
from zephyr.shared.observer import EventConsumer, EventProducer
# from zephyr.shared.config import Configurable  # ARCH-038: loader.py 已退役，配置加载用 infrastructure/config/load_config()
from zephyr.shared.errors import ZephyrError

class {{ class_name }}(LifecycleAware, EventConsumer, Configurable):
    module_id: str = "{{ module_id }}"
    api_version: str = "0.1.0"
    capabilities: list[str] = {{ capabilities }}

    async def on_start(self) -> None:
        await super().on_start()

    async def on_event(self, event: "Event") -> None:
        ...

    async def on_stop(self) -> None:
        await super().on_stop()
```

#### Model Fallback Chain

```python
class ModelFallbackChain:
    _chain: list[tuple[str, float]] = [
        ("deepseek-chat", 0.90),
        ("deepseek-reasoner", 0.70),
        ("qwen-max", 0.60),
    ]

    async def call_with_fallback(self, prompt: str) -> "AIResponse":
        last_error = None
        for model_id, confidence in self._chain:
            try:
                result = await self._call_model(model_id, prompt)
                return result
            except Exception as e:
                last_error = e
                log.warn(f"{model_id}→failed→trying next")
                continue
        raise AIBackendExhaustedError(
            f"All {len(self._chain)} models failed. Last error: {last_error}"
        )
```

### 蓝图特有：RI-13 EventStore 设计哲学

全量实现 ES 对 1 人+AI 是高风险决策。采用**触发式渐进引入**：

```
Phase 1-2: 传统状态存储（SQLite CRUD）
           ↓ 触发条件：模块数 > 100 或 首次合规/审计要求
Phase 3:   RI-13 EventStore ← 关键数据流切 ES，非关键保持 CRUD
           └── 仅对 D_RISK(风控)、D_EXECUTION_CORE(仓位)、D_PORTFOLIO_CORE(交易执行) 三层的写操作做 Event Sourcing
           └── CQRS 读模型：物化视图(账户余额)、聚合视图(因子分数)
           └── 快照策略：每 1000 事件自动快照 → 重放上限 1000 事件 → 恢复延迟 < 500ms
           └── Crypto-Shredding 可选启用（有 GDPR/合规需求时）
           ↓ 触发条件：首次跨模块多步骤回滚需求
Phase 4:   RI-13 SagaCoordinator ← 编排补偿事务（触发式，不主动启动）
```

### 蓝图特有：RL-001 ~ RL-048 落地方案

| 约束 | 方案 | Phase | 验收 |
|------|------|-------|------|
| RL-001 跨层通信 | EventBus pub/sub + consumer group | 1b | 跨层消息延迟 P99 < 100ms |
| RL-002 模块管理 | ModuleLifecycle 拓扑排序启动 | 1a | 500 模块拓扑排序 < 50ms |
| RL-003 配置分层 | ConfigCenter YAML+env + 热重载 | 1a | 配置变更→reload < 3s |
| RL-004 Telemetry | structlog 聚合 + 基数限制 | 1b | 标签基数 ≤ 500 per-module |
| RL-005 健康传导 | HealthCheck 三级 + 故障域隔离 | 2a | 故障域隔离 ≥5 域 |
| RL-006 事件类型 | Pydantic 类型化 + Schema 兼容校验 | 1b | mypy 100% |
| RL-007 依赖可视化 | ModuleGraph JSON + D3.js | 2b | 拓扑图实时渲染 |
| RL-008 配置漂移 | ConfigValidator 定时比对 | 1b | 漂移告警 < 30s |
| RL-009 错误传播链 | ErrorTracer W3C trace_id 传递 | 2a | 跨 3 层 trace_id 完整 |
| RL-010 背压 | EventBus BackpressureController | 1b | 队列 > 80%→背压 |
| RL-011 运行时熔断 | ResilienceGuard CircuitBreaker | 2a | 5 次失败→熔断 |
| RL-012 死信队列 | EventBus DLQ(SQLite持久化) + 指数退避重试 | 1b | 持久化存活，24h内可重放 |
| RL-013 依赖注入 | DependencyInjector 构造注入 | 1a | 只能通过 injector.get() |
| RL-014 幂等 | IdempotencyGuard key 去重 | 2a | 100 次=执行 1 次 |
| RL-015 Secrets | SecretsManager AES-256-GCM | 2a | YAML 中零明文密钥 |
| RL-016 限流 | ResilienceGuard RateLimiter | 2a | 误差 < 5% |
| RL-017 缓存 | CacheLayer LRU+VMS语义 | 2b | 命中率 ≥ 30% |
| RL-018 自诊 | AutoDiagnostics 异常→诊断 | 2b | 诊断报告 < 15s |
| RL-019 事件溯源 | EventStore ES+CQRS | 3 | 事件不可变 + 快照 < 500ms |
| RL-020 操作预演 | DryRunSimulator sandbox | 2b | 写操作 100% 可预演 |
| RL-021 费用归属 | CostTracker per-module | 2b | 费用归属粒度 = module_id |
| RL-022 消息语义 | EventBus DeliverySemantics: AT_LEAST_ONCE(默认) | 1b | 所有消费者按此语义设计 |
| RL-023 背压传导 | BackpressurePropagation 协议 | 1b | 下游队列>80%→上游减速 |
| RL-024 DI统一 | MOD-INF-016 `di_container.py` | 1a | 一个容器，一处注入 |
| RL-025 时间旅行隔离 | replay_to() write_mode: READ_ONLY | 3 | 重放期间0写入冲突 |
| RL-026 行为一致性 | sandbox vs 真实 双跑diff套件 | 2b | diff=0 → 行为一致 |
| RL-027 加密归属 | ConfigCenter→SecretsManager强制路由 | 2a | 唯一加密路径100% |
| RL-028 Loop恢复 | 错误率<3%持续1h→自动恢复OR手动 | 2b | Loop检测0误触发恢复 |
| RL-029 DLQ持久化 | SQLite持久化表 | 1b | 进程重启DLQ不丢 |
| RL-030 SLI阈值 | CPU>80%→DEGRADED,>95%→DOWN | 2a | 健康判定自动化无歧义 |
| RL-031 Flag推出 | 1%→10%→50%→100%+自动KillSwitch | 2a | Flag发布0事故 |
| RL-032 TTL分级 | 关键流ES天然去重/非关键流SQLite24h | 2a | 关键数据0TTL过期风险 |
| RL-033 基数语义 | per-module 500；超限→LRU淘汰+告警 | 1b | 高基数可控 |
| RL-034 Cooldown分层 | CRITICAL 15m/HIGH 10m/MEDIUM 5m/LOW 2m | 2b | 不同失败不同冷却 |
| RL-035 全资源追踪 | CostTracker覆盖CPU/内存/IO | 2b | 全资源FeinOps可见 |
| RL-036 结构化并发 | asyncio.TaskGroup | 1a | 0孤儿协程 |
| RL-037 Bulkhead | per-module线程/连接池上限 | 2a | 一模块崩不拖全系统 |
| RL-038 优雅关闭 | drain→等待→超时→ForceKill→持久化 | 1a | 关闭0数据丢失 |
| RL-039 重试风暴 | RetryBudget全局配额 | 2a | 重试放大器被抑制 |
| RL-040 W3C Trace | traceparent header | 2a | OTel生态完全兼容 |
| RL-041 负载脱落 | LoadShedder优先级丢弃 | 2a | CRITICAL事件从不被丢 |
| RL-042 Schema兼容 | FULL_BACKWARD / FORWARD_TRANSITIVE | 1b | Schema变更零爆炸 |
| RL-043 容量预留 | D_RISK/D_EXECUTION_CORE预分配X% | 2a | 关键模块0被挤占 |
| RL-044 预热期 | warmup→预热→内部HC→READY | 1a+2a | 启动0假熔断 |
| RL-045 Crypto-Shred | per-stream密钥→删除密钥=不可读 | 3 | GDPR就绪 |
| RL-046 Flag交互矩阵 | pairwise组合测试 | 2a | Flag组合0未知bug |
| RL-047 信任衰减 | 误报>30%→降级"建议模式" | 2b | 自愈误判0扩大 |
| RL-048 Crash-Only | 依赖重启恢复不依赖优雅关闭 | 1a | 无人值守自恢复100% |

### 蓝图特有：扩展设计约束（B4/B5 系列）

#### A. 分布式系统与多节点（B4-A01~A10）

| 约束 ID | 约束内容 | 验证方式 |
|---------|---------|---------|
| B4-A01 | Leader Election——多节点部署时主节点选举 | 双主检测=0；无主时定时任务停滞=0 |
| B4-A02 | Cluster Membership（Gossip Protocol）——节点加入/离开/崩溃感知 | 节点崩溃后请求路由到死节点=0 |
| B4-A03 | Split-Brain Protection——网络分区时一致性保护 | 分区期间双主同时写=0 |
| B4-A04 | Consistent Hashing / Sharding——模块>500/事件的Sharding算法 | 扩容后事件路由无需全量重构 |
| B4-A05 | Quorum-Based Decision——部署/FeatureFlag变更的节点共识数 | 单节点作恶→全集群中毒=0 |
| B4-A06 | Hybrid Logical Clock (HLC)——跨节点事件偏序/全序 | 跨节点溯源无"先果后因" |
| B4-A07 | CRDT——多节点并发写入自动合并 | 并发修改无需手动解冲突 |
| B4-A08 | Anti-Entropy（Read Repair + Hinted Handoff）——节点间状态同步修复 | 节点间状态漂移=0 |
| B4-A09 | Multi-Raft / Raft Group Segmented Consensus——按模块域分建共识组 | 全局共识延迟≠O(N²) |
| B4-A10 | Graceful Partition Healing——分区恢复后渐进重建 | 分区恢复后无网络+CPU双爆 |

#### B. 部署与基础设施自动化（B4-B01~B08）

| 约束 ID | 约束内容 |
|---------|---------|
| B4-B01 | CI/CD Pipeline Design——代码→lint→test→dryrun→approve→merge→deploy 全自动流水线 |
| B4-B02 | Canary Deployment——新模块版本→1%→50%→100% 渐进上线 |
| B4-B03 | Infrastructure-as-Code (IaC)——Docker Compose→ Pulumi/Terraform 配置管理 |
| B4-B04 | Blue-Green Deployment——模块版本切换零停机 |
| B4-B05 | Secret Zero Problem——启动时第一个秘密来源与后续展开 |
| B4-B06 | Immutable Infrastructure Implementation——模块不可变部署设计细节 |
| B4-B07 | Container Escape Prevention——AI代码在容器中运行的沙箱加固策略 |
| B4-B08 | Artifact Registry & Provenance——构建产物签名 + SBOM + SLSA供应链级别 |

#### C. 数据管理与迁移（B4-C01~C06）

| 约束 ID | 约束内容 |
|---------|---------|
| B4-C01 | Schema Migration with Zero Downtime——SQLite表结构变更在线迁移（expand-contract pattern） |
| B4-C02 | Point-in-Time Recovery (PITR)——SQLite WAL→增量备份→任意时间点恢复 |
| B4-C03 | Data Retention Policy Automation——自动过期/归档/删除策略执行 |
| B4-C04 | Database Connection Pooling——1500模块并发SQLite读写连接池策略 |
| B4-C05 | SQLite Write Contention——多模块同时写入单一SQLite的并发冲突处理 |
| B4-C06 | Data Locality for Multi-Region——跨Region部署的数据同步策略 |

#### D. 测试与质量保障深度（B4-D01~D08）

| 约束 ID | 约束内容 |
|---------|---------|
| B4-D01 | Contract Testing——模块间API/Pact测试确保Schema变更不破坏下游 |
| B4-D02 | Property-Based Testing——Randomized+Shrink自动发现边界条件 |
| B4-D03 | Automated Test Generation from Diff——AI代码变更→自动生成对应测试 |
| B4-D04 | Mutation Testing——修改代码→测试是否捕获 |
| B4-D05 | Fuzz Testing at Module Boundary——EventBus/ConfigCenter接口随机数据注入 |
| B4-D06 | Golden File Testing——关键输出哈希锁定→变更=回归告警 |
| B4-D07 | Cross-Module Integration Test Orchestration——1500模块集成测试矩阵管理 |
| B4-D08 | Test Flake Detection & Quarantine——不稳定测试自动隔离+报告所有者 |

#### E. AI施工 专项深度（B4-E01~E12）

| 约束 ID | 约束内容 |
|---------|---------|
| B4-E01 | Prompt Caching Strategy——context embed缓存降低LLM API调用费用 |
| B4-E02 | Context Window Budget——每次AI调用的context大小≤X tokens |
| B4-E03 | Semantic Code Search / Code Embedding——AI施工时高效查询已有代码库 |
| B4-E04 | Code Generation Template System——模块脚手架/事件处理器/配置模板标准化 |
| B4-E05 | AI Code Review Automation——AI生成代码→另一AI审查（四眼原则） |
| B4-E06 | Self-Healing Quality Gate——AI自修复后验证：不引入新问题/不影响其他模块 |
| B4-E07 | AI Decision Log——每次AI重大施工决策→自动追加 KB 决策记录 |
| B4-E08 | Diff-Level Undo——单次 diff 级别精细undo |
| B4-E09 | Model Fallback Chain——deepseek-chat → deepseek-reasoner → qwen-max → 提级Owner |
| B4-E10 | AI Context Persistence across Sessions——跨session上下文保存/恢复/过期策略 |
| B4-E11 | Prompt Version Control & A/B Testing——提示词版本化、分级测试、回滚 |
| B4-E12 | Token Optimization Pipeline——AI调用前自动压缩上下文+剪枝不相关文件引用 |

#### F. 1人+AI 运维深度强化（B4-F01~F10）

| 约束 ID | 约束内容 | 验证方式 |
|---------|---------|---------|
| B4-F01 | Owner Cognitive Load Budget——每日决策容量上限，超限→"轻负载日" | 决策疲劳→重大事故漏判=0 |
| B4-F02 | Daily Operations Briefing——每日摘要：关键指标/费用/自愈记录/待决策项 | Owner每日首览≤3min理解系统状态 |
| B4-F03 | Sleep-Time Protocol——23:00-07:00 非CRITICAL静音；CRITICAL仅1次→5min无响应→自愈 | 凌晨告警吵醒≤1次/夜 |
| B4-F04 | Auto-Decide Threshold——影响<X模块/费用<$Y/风险RPN<Z→自动执行无需审批 | 低风险操作审批瓶颈=0 |
| B4-F05 | Emergency Wake-Up Criteria——精确定义值得叫醒Owner的紧急情况 | 假阳性叫醒=0 |
| B4-F06 | Weekly System Health Report——每周Markdown报告到Knowledge Base | 连续多日无注意→问题积累=0 |
| B4-F07 | Owner Absence Simulation——每月1次6h"假Owner离线"演练 | 真正休假时系统依赖Owner手动=0 |
| B4-F08 | Knowledge Externalization——Owner决策原则转化为系统可执行规则 | Owner失能→系统无人判断=0 |
| B4-F09 | Onboarding Auto-Generation——新参与者30min内理解系统 | 新人上手时间≤30min |
| B4-F10 | Mental Health Safeguard——连续72h无Owner手动介入→降低告警频率 | 弃用螺旋=0 |

#### G. 安全深度强化（B4-G01~G06）

| 约束 ID | 约束内容 |
|---------|---------|
| B4-G01 | Module Sandboxing——RI模块间运行时隔离——一个模块crash/无限循环不影响其他模块 |
| B4-G02 | AI-Generated Code Security Scanning——AI施工完成后自动Semgrep安全扫描 |
| B4-G03 | Tamper-Proof Audit Log——审计日志哈希链（Merkle Tree）防篡改 |
| B4-G04 | Least Privilege Enforcement per Module——每个模块只拥有声明的资源访问权 |
| B4-G05 | Supply Chain Security (SBOM + Vulnerability Scan)——依赖脆弱性扫描 + Software Bill of Materials |
| B4-G06 | AI Prompt Injection Guard——Owner指令 vs AI内容分离 |

#### H. 可观测性深度强化（B4-H01~H05）

| 约束 ID | 约束内容 |
|---------|---------|
| B4-H01 | Distributed Trace Visualization——跨5层trace→时序火焰图 |
| B4-H02 | Error Budget Burn Rate Alerting——Error Budget < 1%/1h → CRITICAL |
| B4-H03 | Capacity Forecasting——基于历史趋势预测扩展时机 |
| B4-H04 | Latency Heat Maps——per-module P50/P95/P99 latency→自动识别退化模块 |
| B4-H05 | Slow Query Detection——SQLite查询 > 100ms→自动标记+建议索引 |

#### I. API与协议设计（B4-I01~I04）

| 约束 ID | 约束内容 |
|---------|---------|
| B4-I01 | Module API Versioning Strategy——模块对外API版本规范(SemVer)与废弃窗口 |
| B4-I02 | Backward Compatibility Enforcement——CI自动检测模块新版本是否破坏下游接口 |
| B4-I03 | WebSocket / gRPC Stream Management——流通信的超时/重连/背压策略 |
| B4-I04 | Module Discovery & Self-Description——新模块自动注册+能力声明 |

#### J. 开发者体验（B4-J01~J06）

| 约束 ID | 约束内容 |
|---------|---------|
| B4-J01 | One-Command Local Setup——`git clone && ./setup.sh`→全量本地运行环境就绪 |
| B4-J02 | Hot Reload Development——模块代码变更→自动reload无需重启 |
| B4-J03 | AI REPL / Chat Interface——终端内直接与AI交互施工 |
| B4-J04 | Self-Debugging Hooks——AI施工→失败→自动收集日志+stacktrace→AI自修复 |
| B4-J05 | Codebase Familiarity Score——per-module熟悉度指标+提醒review |
| B4-J06 | Automated CHANGELOG from Git——AI读git log→结构化 CHANGELOG |

#### K. 金融/交易系统专项（B5-K01~K12）

| 约束 ID | 约束内容 | 验证方式 |
|---------|---------|---------|
| B5-K01 | Emergency Trading Kill Switch——一条命令：取消所有未完成订单+清空EventBus交易事件+切换ALL模块read-only | 算法失控→无法停损=0 |
| B5-K02 | Pre-Trade Risk Check Pipeline——订单→仓位限制→资金检查→敞口检查→合规检查→交易所 | AI交易逻辑无风控发单=0 |
| B5-K03 | Order State Machine Standardization——统一状态机(NEW→PENDING→PARTIAL→FILLED/CANCELLED/REJECTED) | 下游订单状态混乱=0 |
| B5-K04 | Market Data Clock & Timestamp Normalization——统一到交易所时钟(NTP→PTP) | tick对齐错位=0 |
| B5-K05 | Deterministic Simulation Mode——固定随机种子+模拟时间→同输入同输出 | 回测不可复现=0 |
| B5-K06 | Paper Trading Infrastructure——所有交易模块自动支持paper模式 | AI施工→直接操作真实账户=0 |
| B5-K07 | Trade Reconciliation——系统订单 vs 经纪商回执 vs 清算报告三方对账 | 系统记录与实际不一致=0 |
| B5-K08 | Position & Exposure Aggregation——全局仓位/净敞口实时计算+硬限额 | 净裸露超限=0 |
| B5-K09 | End-of-Day / Start-of-Day Processing——持仓结算/损益计算/保证金监控/数据归档 | 无标准化日终流程=0 |
| B5-K10 | Market Circuit Breaker Integration——交易所熔断→系统自动暂停该标的交易 | 交易所停牌后继续下单=0 |
| B5-K11 | Slippage & Market Impact Modeling——DryRun和backtest自动归入滑点成本 | 回测"完美利润"≠实盘=0 |
| B5-K12 | Fee & Commission Attribution——每笔交易费用归属到模块，纳入RI-15 FinOps | 费用被忽视→虚假盈利=0 |

#### L. 模块通信模式扩展（B5-L01~L08）

| 约束 ID | 约束内容 | 适用场景 |
|---------|---------|---------|
| B5-L01 | Request-Reply Pattern——同步请求→等待响应→超时处理 | 查询账户余额/因子值/风控判断 |
| B5-L02 | Scatter-Gather Pattern——一请求广播N个模块→收集响应→聚合 | 因子计算——多数据源请求→投票/加表 |
| B5-L03 | Pipeline / Chain Pattern——事件→A处理→B→C→最终结果 | ETL管道/数据清洗/信号生成→过滤→排序→执行 |
| B5-L04 | Competing Consumers——多消费者竞争同一事件，先到先处理 | 同质任务队列——多worker消费 |
| B5-L05 | Content-Based Router——根据消息内容路由到不同消费者 | TradeEvent→D_PORTFOLIO_CORE，RiskEvent→D_RISK |
| B5-L06 | Message Filtering / Enrichment——EventBus中间件截获+修改/增强/过滤事件 | 添加追踪信息/删除敏感字段 |
| B5-L07 | Aggregation / Batching Strategy——按时间窗/数量窗聚合为批处理事件 | 批量行情→归一化→一次性消费 |
| B5-L08 | Return Address / Callback Pattern——事件带return_address→完成后响应 | 异步请求-响应模式 |

#### M. 确定性复现与调试（B5-M01~M06）

| 约束 ID | 约束内容 |
|---------|---------|
| B5-M01 | Deterministic Random——全系统共享种子→种子相同→所有随机行为完全相同 |
| B5-M02 | Simulated Clock——区分 real_time vs sim_time；回测/预演时用sim_time驱动 |
| B5-M03 | Event Replay with Exact Timing——从EventStore按记录时间戳精确重放→同序同果 |
| B5-M04 | Snapshot → Restore for Debugging——运行时快照全系统状态→从此点恢复调试 |
| B5-M05 | Execution Log with Verbosity Control——按需打开/关闭per-module详细日志 |
| B5-M06 | Non-Intrusive Debugging Hooks——每个RI模块暴露hook点→不改代码插桩观察 |

#### N. 长期演进与模块生命周期管理（B5-N01~N06）

| 约束 ID | 约束内容 |
|---------|---------|
| B5-N01 | Module Deprecation Lifecycle——标记→警告→隔离→归档→删除5阶段 |
| B5-N02 | Breaking Change Management——2版本共存+路由→旧版本N个月后移除 |
| B5-N03 | Backward Compatibility Window——每个模块声明支持的历史版本数 |
| B5-N04 | Module Migration Path Documentation——废弃模块→替代模块映射表+迁移guide |
| B5-N05 | Dead Code Detection within Modules——vulture/coverage分析→标记未使用代码 |
| B5-N06 | Cyclomatic Complexity Guard——复杂度>15→AI简化；>25→CI拒绝merge |

#### O. AI 施工模式库与反模式（B5-O01~O08）

| 约束 ID | 约束内容 |
|---------|---------|
| B5-O01 | Module Template System——AI创建新模块时自动从模板生成 |
| B5-O02 | Anti-Patterns Catalog——"在这个系统中绝对不要做什么" |
| B5-O03 | Design Decision Tree——"用EventBus还是直接调用？"→AI可执行决策规则 |
| B5-O04 | Error Handling Patterns by Module Type——数据模块:重试+降级→静态值；交易模块:重试1次→报警→拒绝 |
| B5-O05 | Module Naming Convention Enforcer——`lXX_function_module_name` 强制一致 |
| B5-O06 | Code Ownership Manifest——每个py文件声明：AI施工% vs Owner手动% vs AI自修复% |
| B5-O07 | AI Confidence Annotation——AI在代码中标注信心分数(0-1)——低信心=REVIEW_NEEDED |
| B5-O08 | Progressive Code Review Depth——信心>0.9→轻审；0.5-0.9→中审；<0.5→重审+Owner review |

### 蓝图特有：交易系统基础设施模式

#### 交易模式切换（Trading Mode）

TradingMode 是整个系统的"全局运行模式"，决定 D_RISK/D_PORTFOLIO_CORE/D_EXECUTION_CORE 三层的行为：

| 模式 | 说明 |
|------|------|
| NORMAL | 实盘模式：真实订单→真实broker→真实资金→KillSwitch就绪 |
| PAPER | 纸交易：订单→模拟broker→模拟资金→AI施工默认模式 |
| BACKTEST | 回测模式：SimulatedClock+DeterministicRandom+EventStore重放 |
| READ_ONLY | 只读模式：所有写操作被DryRun拦截→仅记录不执行 |
| KILLED | 紧急停止：已触发KillSwitch→所有交易活动冻结，仅Owner可手动切换回NORMAL（需双因子验证） |

模式切换路径限制：
- NORMAL ⇄ PAPER（任一方向）
- PAPER → BACKTEST / BACKTEST → PAPER
- ANY → READ_ONLY（自动：错误率>阈值时）
- ANY → KILLED（Owner手动/自动：特定条件触发）
- KILLED → NORMAL（仅Owner双因子验证）

#### 新增长容场景（交易专项）

| 场景 | RI 模块行为 | Owner 收到什么 |
|------|-----------|-------------|
| AI 新模块部署→默认PAPER模式 | EventBus自动路由交易事件→模拟broker | 🟢 每日："新模块已上线 Paper Mode——观察72h→可申请升实盘" |
| Paper模式72h稳定→AI申请升实盘 | RI-09 HealthCheck: 72h稳定(错误率<1%+订单完成率>95%)→自动生成升级建议 | 🟡 WARNING："已满足实盘条件——审批后可升级" |
| 单模块亏损>日限额 | RI-15 CostTracker 追踪模块PnL→亏损>$X→自动切换该模块为READ_ONLY+通知 | 💀 CRITICAL："今日亏损已达硬限额→已自动切换READ_ONLY" |
| KillSwitch触发 | B5-K01 TradingKillSwitch.activate()→5步停止序列 | 💀 CRITICAL：飞书+"语音呼叫如果10min内未确认" |
| 交易所熔断（标的暂停） | B5-K10 检测交易所公告→自动暂停该标的+D_PORTFOLIO_CORE标记READ_ONLY | 🟡 WARNING："标的已暂停交易——系统已冻结" |
| 交易对账失败 | B5-K07 三方对账→diff>0→自动暂停该broker连接 | 💀 CRITICAL："系统记录与broker回执不一致——已暂停" |
| 日终处理（EOD） | B5-K09 自动结算→PnL计算→保证金监控→归档→生成日报 | 🟢 每日：EOD报告 |

### 蓝图特有：模块通信模式目录

| 模式 | EventBus 支持程度 | 当前实现 | 施工建议 |
|------|:--:|------|------|
| **Pub/Sub**（发布/订阅） | ✅ 完整 | `shared/observer.py` | 已就绪 |
| **Request/Reply**（请求/响应） | ⚠️ 部分 | 无内建支持 | Phase 1b 扩展：`@request_response(timeout=5.0)` 装饰器 |
| **Scatter/Gather**（分散/聚合） | ❌ 无 | — | Phase 2b 扩展：`ScatterGatherRouter` |
| **Pipeline/Chain**（管道/链） | ❌ 无 | — | 通过事件类型路由实现 |
| **Competing Consumers**（竞争消费者） | ⚠️ 部分 | Consumer Group | 已就绪 |
| **Content-Based Router**（内容路由） | ❌ 无 | — | Phase 1b：`EventRouter` 按event.type路由 |
| **Message Filter**（消息过滤） | ❌ 无 | — | Phase 1b：`EventFilter` 中间件 |
| **Aggregator**（聚合器） | ❌ 无 | — | Phase 2b：`EventAggregator` 时间窗/数量窗 |
| **Return Address**（回调地址） | ❌ 无 | — | Phase 2b：Event.return_address 字段 |

### 蓝图特有：CI/CD 与部署自动化流水线

| 阶段 | 工具 | 门禁内容 |
|------|------|---------|
| 1️⃣ 静态分析 | mypy + ruff + Semgrep | mypy strict + ruff + Semgrep |
| 2️⃣ 测试 | pytest + Hypothesis + pact-python | 单元测试 + Contract Test(Pact) + Property-Based Test(Hypothesis) |
| 3️⃣ DryRun | RI-14 DryRunSimulator | sandbox执行→diff报告 + 一致性验证 + CrossSessionLoopDetector |
| 4️⃣ Approve | Auto-Decide Engine | RPN<50+影响≤3模块+费用≤$0.10 → 自动通过；否则 Owner审批 |
| 5️⃣ 部署 | 基于 RI-03 FeatureFlag | Canary(1%→10%→50%→100%) + 健康监控 + 自动回滚(错误率>5% OR P99延迟>2x基线) |
| 6️⃣ 生产验证 | — | Smoke Test + 错误率基线对比 + 自动追加KB 决策记录 |

### 蓝图特有：AI 施工自治回路

| 阶段 | 内容 |
|------|------|
| 1. 启动 | AI Context Builder + Token Budget Check + 锁定工作区 |
| 2. 施工循环（每轮） | AI提交→Self-Review(四眼原则)→Lint-Fix→Test Gen→SelfSimulate |
| 3. 提审 | 统一diff报告 + Auto-Decide Engine → 自动通过 OR Owner审批 |
| 4. 结束 | Session Log + KB 决策记录 + 解锁工作区 + 更新Familiarity Score |

### 蓝图特有：1人+AI 运维视角的容量模型

#### Owner 告警预算与通知分层

| 通知级别 | 推送方式 | Owner 感知 | 示例 |
|:--:|------|------|------|
| **💀 CRITICAL** | 立即飞书 | 需要3秒内看到并决策 | 熔断OPEN/Secrets泄露/Drift检测/CostTracker硬限额触发 |
| **🟡 WARNING** | 每小时汇总飞书 | 可以等1小时再看 | ErrorBudget < 50%/RateLimiter触发/Backpressure WARNING |
| **🟢 INFO** | 每日汇总飞书 | 睡醒再看 | FeatureFlag状态汇总/Cooldown触发/CacheLayer命中率日报 |
| **⚪ DEBUG** | 仅Dashboard | 不推送，Owner主动查看 | Telemetry基数详情/LLM调用token明细/AI行为Trace |
| **✨ AI_SELF_HEALED** | 日报中列出 | "今天AI自愈了N次" | HealthCheck→AutoDiagnostics→修复→成功——全链路无人参与 |

#### 五视图体系

| 视图 | 内容 | 当前状态 |
|------|------|:--:|
| **静态拓扑视图** | 模块清单 + 依赖 DAG + 承载关系 | ✅ |
| **动态行为视图** | 每个 RI 模块的状态机、生命周期状态图 | ⚠️ 蓝图骨架存在但未展开 |
| **故障传播视图** | 从底层故障到顶层 Owner 感知的因果链 | ✅ |
| **容量伸缩视图** | Load→Response Curve | ⚠️ 依赖 MOD-INF-001 容量预测模型 |
| **Owner 感知视图** | 每个 RI 模块在每种失败模式下，Owner 感知到什么 | ✅ |

#### 深度运维场景

| 场景 | 触发条件 | 系统行为 | Owner 感知 |
|------|---------|---------|-----------|
| 🛌 **睡眠保护** | 23:00-07:00 local | CRITICAL 仅触发1次→5min无响应→自愈 | "今日7小时睡眠窗口——系统自行处理了2个WARNING" |
| ☕ **晨报推送** | 07:00-08:00 | Daily Briefing: 昨日关键指标+费用+自愈记录+待决策项 | 飞书："昨日3个AI自愈/月费$1.42/1项待审批" |
| 🧠 **决策疲劳防护** | C_today > 0.8×C_max | Auto-Decide Engine激活 | "今日已做X项自动决策——节省了Y次审批" |
| 🚨 **紧急唤醒判定** | 夜间+核心回路DOWN+3次自愈失败 | CRITICAL飞书：原因+已尝试自愈+建议动作 | 明确告知为何唤醒 |
| 🏝️ **Owner消失演练** | 每月1次（6h） | 系统进入"Owner Absent Mode" | 演练结束后报告 |
| 📝 **知识外化** | Owner每次做决策后 | 记录决策原则→转化为系统规则 | "已自动学习到你的12条决策偏好" |
| 💔 **弃用螺旋防护** | 连续72h无Owner手动介入 | 降低告警频率30%+升高自愈阈值 | "注意：已3天无手动操作" |
| 🔄 **自我解释** | Owner 说 "why?" | ≤3s可理解的因果解释 | "EventBus熔断因为：l06消费速率<10/s" |
| 📊 **周报** | 每周日 | Weekly Report：SLO/费用/健康/AI施工统计 | Markdown→飞书→KB |

#### 开发者体验设计

| 体验目标 | 设计 | 实现方式 |
|---------|------|---------|
| **一键启动** | `git clone && ./tools/setup.sh` | 自动创建venv、安装依赖、初始化SQLite、启动EventBus |
| **热重载** | 模块代码变更→自动reload | watchdog监控→受影响模块restart（复用RI-02热重载） |
| **AI Chat 集成** | 终端内 `/z` 命令→AI施工 | `$ /z fix module l06` → AI对话→代码变更→DryRun→审批 |
| **自调试钩子** | AI施工→失败→自动收集上下文 | 自动捕获trace_id+stacktrace+最近commit→发送给AI自修复 |
| **代码熟悉度** | per-module可视化熟悉度 | f(最后修改天数, Owner修改次数, 最近AI修改次数)→低熟悉度→提醒review |
| **自动 CHANGELOG** | AI读写git log→结构化CHANGELOG | 与RI-15 CostTracker共用AI Decision Log管道 |

---

## §4 接口契约

### 4.1 公共 API

| RI 模块 | 核心类 | 关键方法签名 |
|---------|--------|-------------|
| RI-01 | EventBus | `async publish(event: Event) -> None`, `async subscribe(topic: str, handler: Callable) -> str`, `async drain(timeout: float) -> DrainResult` |
| RI-02 | ModuleLifecycle | `async register(module: LifecycleAware) -> None`, `async startup_all() -> StartupReport`, `async shutdown() -> ShutdownResult` |
| RI-03 | ConfigCenter | `get(key: str, default: Any) -> Any`, `async reload() -> None`, `get_feature_flag(name: str) -> FlagState` |
| RI-05 | ResilienceGuard | `async call_with_circuit(name: str, fn: Callable) -> Any`, `async acquire_rate(name: str) -> bool` |
| RI-07 | SecretsManager | `encrypt(plaintext: str) -> str`, `decrypt(ciphertext: str) -> str`, `rotate(key_id: str) -> None` |
| RI-09 | HealthCheck | `async check(module_id: str) -> HealthStatus`, `async check_all() -> AggregateHealth` |
| RI-14 | DryRunSimulator | `async simulate(operation: Operation) -> SimulationResult`, `async approve(operation_id: str) -> None` |

### 4.2 数据模型

| 模型 | 基类 | 核心字段 |
|------|------|---------|
| Event | Pydantic BaseModel | `event_type: str`, `payload: dict`, `priority: EventPriority`, `trace_id: str` |
| HealthStatus | Pydantic BaseModel | `module_id: str`, `status: Literal["UP","DEGRADED","DOWN"]`, `sli_values: dict[str,float]` |
| CircuitState | Enum | `CLOSED`, `OPEN`, `HALF_OPEN` |
| FlagState | Enum | `OFF`, `CANARY`, `ON` |
| DeliverySemantics | Enum | `AT_MOST_ONCE`, `AT_LEAST_ONCE`, `EXACTLY_ONCE` |
| EventPriority | Enum | `CRITICAL=0`, `HIGH=1`, `NORMAL=2`, `LOW=3` |

### 4.3 输入契约

| 约束 | 适用模块 | 值 |
|------|---------|-----|
| 事件体必须 Pydantic 验证 | RI-01 | `isinstance(event, BaseModel)` |
| 模块必须实现 LifecycleAware | RI-02 | `hasattr(module, 'on_start')` |
| 配置 key 必须在 schema 中声明 | RI-03 | `key in schema` |
| 幂等 key 非空 | RI-06 | `len(idempotency_key) > 0` |
| 加密字段走 SecretsManager | RI-03→RI-07 | `field.encrypted == True → SecretsManager.decrypt()` |

### 4.4 输出契约

| 约束 | 适用模块 | 值 |
|------|---------|-----|
| 事件投递语义 | RI-01 | `AT_LEAST_ONCE`（默认）；关键流 `EXACTLY_ONCE` |
| 健康状态枚举 | RI-09 | 仅 `UP`/`DEGRADED`/`DOWN` |
| trace_id 格式 | RI-08 | W3C traceparent: `00-{32hex}-{16hex}-{02x}` |
| 诊断报告格式 | RI-12 | Markdown，≤500 字 |
| 费用归属粒度 | RI-15 | `module_id` + `session_id` |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约 | 版本 | 兼容性策略 |
|------|------|-----------|
| Event schema | 1.0.0 | FULL_BACKWARD |
| HealthStatus | 1.0.0 | FULL_BACKWARD |
| DeliverySemantics | 1.0.0 | FORWARD_TRANSITIVE |
| FlagState | 1.0.0 | FULL_BACKWARD |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 版本 | 3.12+ |
| 2 | 操作系统 | Windows 单机 |
| 3 | 并发模型 | asyncio |
| 4 | 数据库 | SQLite WAL |
| 5 | 序列化 | Pydantic V2 |
| 6 | 外部依赖 | 最小化 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 模块总数 | 15 | 300 | 1500 | ✅ | 模块 > 300 → EventBus 切 Kafka |
| 事件消费者 | — | 500/事件 | — | ✅ | 消费者 > 500 → EventBus Sharding |
| 并发写入 | — | 150 (10% 模块) | — | ✅ | SQLite busy_timeout + WAL |
| 告警预算 | — | 10 条/日 | — | ✅ | 超出 → 降级为日报汇总 |
| LLM 月费 | — | $50 | — | ✅ | 超出 → 预算硬限额 + 自动降级 |
| Telemetry 基数 | — | 500/module | — | ✅ | 超限 → LRU 淘汰 + 告警 |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

本蓝图不涉及迁移。

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | EventBus 队列满→背压信号延迟→上游持续写入→队列溢出丢事件 | BackpressurePropagation 80%立即广播 + QueueSize监控 | 背压传导+LoadShedder优先级丢弃 | 关键事件丢失→风控/交易状态不一致 |
| 2 | CircuitBreaker 误熔断→关键下游不可用→全链降级 | HALF_OPEN探测 + TrustDecayTracker | 渐进恢复+信任衰减监控 | 风控检查失败→交易被拒→PnL偏离 |
| 3 | DryRun sandbox产出与真实执行不一致 | 一致性验证套件（双跑diff）+ SelfSimulate | 修复sandbox→重新验证 | Owner确认的操作上线后触发LoopDetector |
| 4 | HealthCheck SLI阈值模糊→DEGRADED判定歧义→自愈触发延迟 | 具体SLI阈值+Reconciliation Loop | 阈值具体化+持续对账 | 系统DEGRADED→30s延迟→雪崩为DOWN |
| 5 | IdempotencyGuard TTL过期→同key重复写入 | 关键流ES expected_version天然去重 | 分级策略：关键流零TTL风险 | 风控限额double-count |
| 6 | AutoDiagnostics连续误诊3次→SelfLimiter激活 | TrustDecayTracker逆过程 | 暂停后Owner修复→信任恢复 | 模块DOWN但自愈回路暂停 |
| 7 | SecretsManager主密钥丢失→所有加密配置不可读 | 主密钥备份+Offline冷存储+轮转记录 | 从冷备恢复密钥 | 全系统瘫痪 |
| 8 | DeadModule检测误标→活跃模块被标记DORMANT | 30天阈值保守+标记前人工确认 | 误标恢复 | 模块被误归档→上游崩 |
| 9 | Crypto-Shredding去密钥→冷备份中仍有点密钥 | Shred操作→同时删除主+冷备双份密钥+3路审计确认 | 双份密钥同步删除 | GDPR不合规 |
| 10 | RetryBudget耗尽→关键消费者重试被拒 | RetryBudget按事件优先级分配：CRITICAL自带保底配额 | CRITICAL保底配额 | 关键操作被DLQ滞留 |
| 11 | AI代码在EventLoop中无限循环→阻塞所有RI模块 | ModuleSandbox进程隔离 | 独立子进程+5次crash永久隔离 | 全系统DOWN |
| 12 | SQLite schema迁移锁表→所有模块阻塞 | expand-contract online migration | 兼容性检查门禁+双写过渡期 | 全量生产停机 |
| 13 | 模块A升级破坏模块B的API契约→级联故障 | Pact Contract Testing + CI Backward Compatibility Check | 2版本共存+路由 | 一模块升级→炸上下游 |

---

## §8 安全考量

### 安全机制

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 密钥管理风险 | 高 | RI-07 SecretsManager: AES-256-GCM 加密 + 轮转提醒 + 访问审计 + 泄露检测 + AI 注入隔离 | YAML中零明文密钥 |
| 2 | 访问控制绕过 | 高 | RI-07: ConfigCenter 加密字段强制走 SecretsManager | 唯一加密路径100% |
| 3 | 审计日志篡改 | 中 | RI-13 EventStore: 事件不可变 + Crypto-Shredding | 删除密钥后0条事件可解密 |
| 4 | AI代码无隔离 | 高 | ModuleSandbox: AI代码独立子进程 + 5次crash永久隔离 | 一模块crash不影响其他 |
| 5 | 安全组件不可用 | 高 | RI-07, RI-08: Fail-Closed——安全组件不可用时拒绝操作 | 拒绝操作而非放行 |
| 6 | 交易系统失控 | 高 | TradingKillSwitch: 5步停止序列 + 仅Owner双因子解除 | 算法失控→无法停损=0 |
| 7 | Prompt注入 | 中 | RI-14: Owner指令 vs AI内容分离 | 注入攻击被拦截 |
| 8 | 供应链攻击 | 中 | CI/CD: Semgrep扫描 + SBOM + SLSA | CVE自动评估+告警 |

### 致命假设清单

| # | 致命假设 | 假设不成立的后果 | 缓解可能性 | 缓解措施 |
|:--:|---------|---------------|:--:|------|
| H1 | SQLite单写者瓶颈对1500模块并发写入可接受 | 六类写入同时排队→系统不可用级别延迟 | 🟡 中 | BackpressurePropagation + 写争用缓解(busy_timeout) |
| H2 | AI自测试+AI自审查能发现AI自生成的缺陷 | 同架构不同模型共享训练数据盲区→漏掉同一边界条件 | 🔴 低 | "四眼原则"(不同模型审查)。但盲区重叠率未测量 |
| H3 | AI施工工具生态3年内不会剧变 | deepseek停服/被封/价格×10→施工管道断裂 | 🟡 中 | ModelFallbackChain(3供应商) |
| H4 | SQLite WAL/DB永不被逻辑性损坏 | 逻辑错误写入SQLite→持久化为"正确"数据 | 🔴 低 | expand-contract + 三方对账。逻辑损坏检测需应用层checksum |
| H5 | 1500模块的模块ID不发生碰撞 | 两个session各自生成相同ID→后创建覆盖前一个 | 🟢 高 | 代码索引表。但无原子ID分配器 |
| H6 | Python asyncio.TaskGroup 在未来5年内保持向后兼容 | Python变更TaskGroup语义→1500模块需全部review | 🟢 高 | 无直接缓解。Python生态假设 |
| H7 | Owner具备在紧急情况下的有效决策能力 | 凌晨3点被唤醒→睡眠惯性+决策疲劳 | 🟡 中 | 紧急唤醒判定+通知分层 |
| H8 | 系统能在Owner永久失能后继续运作或安全停止 | 交易系统有账户/仓位/资金——法律上需要人类负责人 | 🔴 低 | 无设计。建议：Dead Man's Switch |
| H9 | 全量集成测试的可行替代方案足够有效 | 1500模块组合爆炸→三模块交互时序bug | 🟡 中 | Cross-Module Integration Test + Canary |
| H10 | 蓝图的Text-to-Code转换能忠实执行设计意图 | 蓝图说"Crash-Only"但AI生成了`try: ... except: pass` | 🟡 中 | AI施工自治回路+CI/CD六门流水线 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 所有RI模块核心类 | EventBus publish/subscribe/drain; CircuitBreaker三态转换; IdempotencyGuard去重; SecretsManager加解密 | 覆盖率≥80% |
| 2 | 集成测试 | RI模块间交互 | RI-02+03+04+08四模块联调; 背压传导链压测; 基数限制超限测试 | 端到端通过 |
| 3 | 韧性测试 | 混沌实验 | 熔断+Bulkhead+LoadShedding+RetryBudget联动; 全链路韧性测试 | SLO达标 |
| 4 | Contract测试 | 模块间API | Pact测试确保Schema变更不破坏下游 | 0契约破坏 |
| 5 | 一致性验证 | DryRun vs 真实 | sandbox vs 真实双跑diff | diff=0 |
| 6 | 性能测试 | 容量边界 | 500模块拓扑排序≤50ms; 跨层消息延迟P99≤100ms; 投机执行降低尾延迟≥30% | 性能指标达标 |

### 验收标准

| 维度 | 指标 | 目标 |
|------|------|------|
| 性能 | 500 模块拓扑排序时间 | ≤50ms |
| 性能 | 跨层消息延迟 P99 | ≤100ms |
| 性能 | 投机执行降低尾延迟 | ≥30%（CRITICAL事件P99.9） |
| 韧性 | CircuitBreaker OPEN 后恢复时间 | ≤30s |
| 韧性 | RateLimiter 限流精度 | 误差 < 5% |
| 韧性 | Bulkhead 隔离有效性 | 一模块崩不影响其他模块（SLO 95%） |
| 韧性 | RetryBudget 重试配额精度 | 0 次配额超额 |
| 韧性 | LoadShedder 保护有效性 | CRITICAL 丢弃率 0% |
| 可靠性 | IdempotencyGuard 去重准确率 | 100% |
| 可靠性 | 关键数据流 TTL 过期风险 | 0%（ES天然去重） |
| 安全 | Secrets 明文落盘 | 0 |
| 安全 | ConfigCenter 加密字段非法路径 | 0% |
| 安全 | Crypto-Shredding 有效性 | 删除密钥后0条事件可解密 |
| 错误处理 | 跨 3 层 W3C trace_id 完整性 | 100% |
| 可观测 | Telemetry 标签基数 | ≤500 / module |
| 可观测 | PromptFingerprint 覆盖率 | 100% |
| 自治 | HealthCheck DOWN → 诊断报告生成 | ≤15s |
| 自治 | TrustDecayTracker 误报阈值 | 误报>30%→1h内降级 |
| AI 安全 | 写操作 DryRun 覆盖率 | 100% |
| AI 安全 | DryRun vs 真实行为一致性 | diff=0 |
| 成本 | LLM + CPU/内存/IO 费用归属 | module_id + session_id |
| 溯源 | 关键流事件不可变性 | 100% |
| 合规 | GDPR删除权可达性 | Crypto-Shredding 100%覆盖 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-016 Shared Core | 必须 | 10 个 RI 模块的代码承载基座 | v0.14.0 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` |
| MOD-INF-001 Capacity Assurance | 必须 | 容量 SLO + Error Budget | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\capacity_assurance\blueprint.md` |
| MOD-GATE_ENGINE Gate Engine | 可选 | 任务门禁 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md` |
| MOD-INF-020 Audit Trail | 可选 | 审计追踪链 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-INF-021 Rollback System | 可选 | 回滚系统 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\rollback-system\blueprint.md` |
| MOD-INF-023 Drift Detector | 可选 | 漂移检测 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\drift-detector\blueprint.md` |
| MOD-LLM_SECURITY LLM Security | 可选 | LLM 安全网关 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\llm_security\blueprint.md` |
| MOD-INF-018 Agent RBAC | 可选 | Agent RBAC | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-INF-025 A2A Protocol | 可选 | Agent-to-Agent 协议 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\a2a-protocol\blueprint.md` |
| MOD-KB-001 Knowledge Base | 可选 | AutoDiagnostics→修复成功→自动补充知识库 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\knowledge_base\blueprint.md` |
| MOD-INF-022 Escalation Protocol | 可选 | 自治权限升降级 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-protocol\blueprint.md` |
| MOD-INF-024 Budget Enforcer | 可选 | 预算强制执行 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\budget-enforcer\blueprint.md` |

### 10.2 依赖图对齐声明

> 蓝图 §10.1 声明的依赖 MUST 与全局依赖图一致。不一致 = 漂移。
> 全局依赖图 SSoT：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> 机器 SSoT：[cross-module-dependency-registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml)

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-002` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| shared/infra/observer.py | shared/events/dlq.py | EventBus 基类是 DLQ 的前置条件 | 检查 observer.py 存在 |
| shared/resilience/circuit_breaker.py | shared/resilience/retry.py | 熔断状态影响重试策略 | 检查 circuit_breaker.py 存在 |
| lifecycle_manager/hooks.py | infra_ops/auto_diagnostics.py | LifecycleAware 是 AutoDiagnostics 注册前置 | 检查 hooks.py 存在 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| shared/infra/observer.py | shared/events/dlq.py | Event | 函数调用 |
| shared/observability/health.py | infra_ops/auto_diagnostics.py | HealthStatus | 事件总线 |
| shared/observability/metrics.py | infra_ops/cost_tracker.py | TokenUsage | 函数调用 |
| infra_ops/dry_run_simulator.py | shared/kill_switch.py | SimulationResult | 事件总线 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 蓝图依赖12个外部模块+28个内部文件 |
| 2 | 依赖对齐自动验证 | 是 | 有12个外部依赖需对齐 |
| 3 | 临时时态内容自动清理 | 否 | 无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 否 | 已施工完成 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | asset-inventory/dependency.py | 不覆盖scripts/目录 |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |

---

## §11 产出物存放目录

### 源码文件

> ✅ = 已实现（含 MOD-INF-016 Shared Core 承载的实现）；❌ = 待施工
> 逐文件清单见 §0.1 代码文件清单

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\runtime_integration\blueprint.md` | 本文件 |
| 业务代码（Shared Core承载） | `D:\ZephyrAlpha\src\zephyr\shared\` | RI-01~RI-11 共享核心承载 |
| 业务代码（独立落地） | `D:\ZephyrAlpha\src\zephyr\infra_ops\` | RI-12~RI-15 独立落地 |
| 测试代码 | `D:\ZephyrAlpha\tests\infra_ops\` | 测试用例 |
| 配置文件 | `D:\ZephyrAlpha\config\` | RI模块配置YAML |

### 配置文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `config/event_bus.yaml` | ❌ | 事件类型/Schema/DLQ策略/DeliverySemantics/Priority配置 |
| `config/resilience_guard.yaml` | ❌ | 熔断阈值/限流配额/降级链/Bulkhead per-module配额/LoadShedder阈值/RetryBudget配额 |
| `config/secrets_policy.yaml` | ❌ | 加密算法/轮转/审计规则/ConfigCenter加密字段路由 |
| `config/health_check.yaml` | ❌ | 探针定义/SLI具体阈值/故障域/自愈策略/Reconciliation周期 |
| `config/telemetry_collector.yaml` | ❌ | 聚合/基数限制per-module/PromptFingerprint开关/DeadModuleDetector阈值 |
| `config/cache_layer.yaml` | ❌ | TTL分层/LRU/语义缓存/DataAffinity hints |
| `config/runbooks/` | ❌ | 常见故障 SOP YAML——AutoDiagnostics消费 |
| `config/llm_pricing.yaml` | ❌ | LLM 定价表——CostTracker 消费 + 定时对比 |
| `config/dry_run_policy.yaml` | ❌ | 哪些操作自动审批/必须人工/一致性验证套件开关/CrossSessionLoop检测开关 |
| `config/flag_interaction_matrix.yaml` | ❌ | Feature Flag pairwise组合测试用例——CI自动消费 |
| `config/schema_evolution_policy.yaml` | ❌ | Schema兼容性策略：FULL_BACKWARD/FORWARD_TRANSITIVE |
| `config/owner_notification_tiers.yaml` | ❌ | Owner告警预算N=10、通知分层规则、休假模式激活码 |
| `config/trust_decay_policy.yaml` | ❌ | TrustDecayTracker恢复窗口+trust阈值+逆过程 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-INF-016 Shared Core | 代码承载 | `shared/` 目录下所有RI模块基类 | 验证Shared Core实现满足蓝图增强需求 |
| MOD-INF-001 Capacity Assurance | 事件订阅 | HealthCheck→容量SLO→ErrorBudget | 容量约束事件正确传播 |
| MOD-INF-020 Audit Trail | 事件生产 | RI-13 EventStore→审计追踪链消费 | 事件级溯源→审计报告导出 |
| MOD-INF-021 Rollback System | 事件生产 | RI-13 事件重放→配合回滚 | 事件重放→状态恢复 |
| MOD-LLM_SECURITY LLM Security | Fail-Closed对齐 | RI-07/RI-08安全组件→LLM安全网关 | 安全组件不可用时拒绝操作 |
| MOD-KB-001 Knowledge Base | 知识写入 | AutoDiagnostics→修复成功→KB自动补充 | 修复后KB条目新增 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | RI 模块注册 | 新增 RI-13~RI-15 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 蓝图元数据 | 版本更新 |
| 3 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 依赖关系 | RI 模块依赖 |

---

## §14 已知风险与缓解

> 本节同时承接原 §15 后果中的**负面后果**——设计决策带来的已知代价。
> 正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | asyncio.Queue 在 500 模块下内存暴增 | 低 | 高 | QUEUE_MAX_SIZE = 10000 硬限制 + 背压 + LoadShedder | 风险 |
| 2 | CircuitBreaker 误熔断 | 中 | 高 | HALF_OPEN 探测 + 渐进恢复 + 信任衰减监控 | 风险 |
| 3 | IdempotencyGuard 存储膨胀 | 中 | 中 | TTL分级：关键流ES天然去重零存储/非关键流24hTTL定时清理 | 风险 |
| 4 | SecretsManager 主密钥丢失 | 低 | 高 | 主密钥备份 + 轮转记录 | 风险 |
| 5 | CacheLayer 缓存穿透（雪崩） | 中 | 中 | 空值缓存 + 互斥锁防并发重建 + Bulkhead隔离 | 风险 |
| 6 | AutoDiagnostics 误诊 | 中 | 中 | 标记置信度 + TrustDecayTracker + "请 Owner 确认" | 风险 |
| 7 | EventStore 事件日志膨胀 | 中 | 中 | 快照策略（每 1000 事件）+ 热/冷分层存储 | 风险 |
| 8 | DryRun 与真实执行行为不一致 | 中 | 中 | 一致性验证套件——sandbox vs 真实双跑 diff | 风险 |
| 9 | 重试风暴——500消费者同时重试 | 中 | 高 | RetryBudget：全局每分钟配额100——耗尽拒绝重试 + jitter | 风险 |
| 10 | Token费用无预算→月底账单超预期 | 高 | 高 | PromptCacheManager + per-session Token Budget | 风险 |
| 11 | Owner决策疲劳→低质量审批→事故 | 高 | 高 | Auto-Decide Engine + 认知负荷预算 | 风险 |
| 12 | 单节点设计——多节点部署时无Leader | 中 | 中 | SqliteLeaderElection——SQLite租约实现轻量级主选举 | 风险 |
| 13 | Schema兼容性策略缺失→模块升级炸下游 | 中 | 高 | SchemaEvolutionPolicy：强制FULL_BACKWARD兼容 | 风险 |
| 14 | 弃用螺旋——Owner长时间不使用系统 | 中 | 中 | 弃用螺旋防护——72h无介入→自动降频+增高自愈阈值 | 风险 |
| 15 | 15个RI模块完整实现工作量巨大 | 高 | 高 | 5个Phase渐进交付 | 负面后果 |
| 16 | Shared Core承载关系增加MOD-INF-016修改频率 | 中 | 中 | RI增强需求在shared层扩展 | 负面后果 |
| 17 | AutoDiagnostics误诊的信任衰减需要时间积累 | 中 | 中 | TrustDecayTracker渐进恢复 | 负面后果 |
| 18 | 触发式模块（RI-13/14/15）在触发前无代码验证 | 中 | 中 | 定期设计review | 负面后果 |
| 19 | 零依赖优先限制技术选型——模块>300时需迁移 | 中 | 高 | Protocol抽象层无缝切换 | 负面后果 |

---

## §16 施工指引

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §0 对齐 + §1-§14 架构 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 4 | GOV-DOC-002 防幻觉路径映射已理解 | 能回答"某类文件该放哪" | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 5 个 Phase（1a/1b/2a/2b/3）+ 2 个触发式Phase（4/∞） |
| 施工模式 | 扩展为主（Shared Core承载层扩展）+ 独立落地（RI-12/13/14/15） |
| 核心风险 | Shared Core扩展可能影响已有功能；触发式Phase设计可能过时 |
| 目标 generation | 7 — 本次从 generation 6 升级到 generation 7（模板v3.5/v3.6升级） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-016 Shared Core v0.14.0 已施工completed | hard | ✅ | ✅ |
| 2 | Python 3.12+ 环境就绪 | hard | ✅ | ✅ |
| 3 | SQLite WAL 可用 | hard | ✅ | ✅ |

### 16.3 实施步骤

> **⚠️ 施工前检查**：检查 MOD-INF-016 Shared Core v0.14.0 已有对应实现的状态。若 `shared/` 下文件已是 ✅，RI 模块从设计→到交付→到测试的流程应**跳过独立文件创建**，改为：
> 1. 验证 Shared Core 实现是否满足本蓝图的增强需求
> 2. 若不足：在 `shared/` 目录下扩展（不创建 `infra_ops/` 独立文件）
> 3. 若完全满足：直接标记为 ✅，记录验收时间

#### Phase 1a: 底座上线

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 1 | RI-02 ModuleLifecycle——验证 `lifecycle_manager/hooks.py`；扩展优雅关闭协议+Crash-Only设计+预热期 | `lifecycle_manager/shutdown.py` + `lifecycle_manager/warmup.py` | MOD-INF-016 扩展 |
| 2 | RI-04 DependencyInjector——在 `shared/production/di_container.py` 落地构造注入+接口绑定+循环检测 | `shared/production/di_container.py` + 测试 | **MOD-INF-016 新文件** |
| 3 | RI-03 ConfigCenter——验证 `shared/config/`；扩展渐进推出+交互矩阵+SchemaRegistry+FeatureFlag Kill Switch | `shared/flags/rollout.py` + `config/flag_interaction_matrix.yaml` | MOD-INF-016 扩展 |
| 4 | RI-08 ErrorHandler——验证 `shared/errors.py` + `shared/logging.py`；扩展W3C Trace Context | `shared/logging/trace_context.py` | MOD-INF-016 扩展 |
| 5 | 集成测试——RI-02+03+04+08 四模块联调（结构化并发 TaskGroup 验证） | 4 模块联调 + 结构化并发验证 | — |

#### Phase 1b: 通信就绪

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 6 | RI-01 EventBus——验证 `shared/observer.py`；扩展PriorityQueue+DeliverySemantics+BackpressurePropagation+Schema兼容性策略 | `shared/events/priority_queue.py` + `config/event_bus.yaml` + `config/schema_evolution_policy.yaml` | MOD-INF-016 扩展 |
| 7 | RI-06 IdempotencyGuard——验证 `shared/production/idempotency.py`；扩展 TTL 分级策略 | `shared/production/idempotency_policy.yaml` | MOD-INF-016 扩展 |
| 8 | RI-10 TelemetryCollector——验证 `shared/production/metrics.py`；扩展PromptFingerprint+DeadModuleDetector+基数超限LRU策略 | `shared/production/prompt_fingerprint.py` + `shared/production/dead_module_detector.py` | MOD-INF-016 扩展 |
| 9 | 集成测试 + 背压传导链压测 + 基数限制超限测试 | — | — |

#### Phase 2a: 韧性安全

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 10 | RI-05 ResilienceGuard——验证 `shared/resilience/`；扩展Bulkhead+LoadShedder+RetryBudget+自适应并发限制 | `shared/resilience/bulkhead.py` + `shared/resilience/load_shedder.py` + `shared/resilience/retry_budget.py` + `config/resilience_guard.yaml` | MOD-INF-016 扩展 |
| 11 | RI-07 SecretsManager——验证 `shared/production/secrets.py`；ConfigCenter 加密字段路由 | `shared/production/secrets_routing.py` | MOD-INF-016 扩展 |
| 12 | RI-09 HealthCheck——验证 `shared/health.py`；扩展具体SLI阈值+ReconciliationLoop+TrustDecayTracker | `shared/health/sli_thresholds.py` + `shared/health/reconciliation.py` + `config/health_check.yaml` | MOD-INF-016 扩展 |
| 13 | RI-11 CacheLayer——验证 `shared/production/cache.py`；扩展 DataAffinity hints + 穿透/LRU 策略 | `shared/production/cache_affinity.py` | MOD-INF-016 扩展 |
| 14 | 全链路韧性测试——混沌实验（熔断+Bulkhead+LoadShedding+RetryBudget联动） | — | — |

#### Phase 2b: 自治闭环

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 15 | **RI-12 AutoDiagnostics**——HealthCheck触发→Runbook匹配→诊断报告Markdown→修复成功→KB自动补充→SelfLimiter | `auto_diagnostics.py` + `config/runbooks/` + `config/trust_decay_policy.yaml` | MOD-INF-002 独立 |
| 16 | **RI-14 DryRunSimulator**——sandbox预演+diff报告+审批门+一致性验证套件+CrossSessionLoopDetector+SelfSimulate | `dry_run_simulator.py` + `config/dry_run_policy.yaml` | MOD-INF-002 独立 |
| 17 | **RI-15 CostTracker**——LLM+CPU+内存+IO调用拦截+全资源per-module费用归属+MaintainabilityScore+预算告警+飞书日报 | `cost_tracker.py` + `config/llm_pricing.yaml` + `config/owner_notification_tiers.yaml` | MOD-INF-002 独立 |
| 18 | ModuleGraph——D3.js可视化 + 依赖拓扑实时渲染 + 死模块标红 | 前端 + API | — |
| 19 | ProgressiveDelivery 预留 | Protocol | — |

#### Phase 3: 溯源增强（触发式）

> **不主动启动。** 当模块数 > 100 或 Owner 发出"需要合规审计"指令时触发。

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 20 | **RI-13 EventStore**——append-only event_log + 快照 + CQRS读模型 + replay_to写隔离 + Crypto-Shredding | `event_store.py` | MOD-INF-002 独立 |
| 21 | D_RISK(风控)/D_PORTFOLIO_CORE(交易)/D_EXECUTION_CORE(仓位) 三层写操作切 Event Sourcing | 迁移脚本 + 验证 | — |
| 22 | 事件重放验证 + 审计报告导出 + Crypto-Shredding GDPR验证 | 审计报告 + Shred验证 | — |

#### Phase 4: 补偿增强（触发式）

> **不主动启动。** 当首次跨模块多步骤回滚需求出现时触发。

| 步骤 | 任务 | 产出物 |
|:--:|------|--------|
| 23 | RI-13 SagaCoordinator——跨模块补偿事务编排 | `event_store/saga_coordinator.py` |
| 24 | 补偿事务验证——多步骤回滚→逆序执行补偿→所有步骤恢复 | 补偿验证报告 |

#### Phase ∞: 维护期切换

| 步骤 | 任务 | 产出物 |
|:--:|------|--------|
| 25 | Phase ∞ 切换检查——全部 Phase 验收标准达标 | 切换确认 |
| 26 | SLO 收紧——维护期容忍度从宽松→严格 | 维护期 SLO 阈值表 |
| 27 | RI 模块降频配置——DryRunSimulator降频 + CostTracker保留全精度 + AutoDiagnostics保留实时 | `config/maintenance_mode.yaml` |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| Phase 1a | Shared Core扩展破坏已有功能 | git revert shared/ 目录变更；独立文件直接删除 |
| Phase 1b | EventBus扩展导致消息丢失 | 回退到基类observer.py；DLQ SQLite表可保留 |
| Phase 2a | 韧性组件误熔断 | 禁用新组件配置YAML；回退到shared/resilience/基类 |
| Phase 2b | AutoDiagnostics误诊 | 禁用auto_diagnostics.py；降级为手动诊断 |
| Phase 3 | EventStore性能不达标 | 停止ES写入；回退到CRUD模式 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | Shared Core 扩展文件 | `D:\ZephyrAlpha\src\zephyr\shared\` | ☐ | ☐ | ☐ |
| 2 | 独立落地文件 | `D:\ZephyrAlpha\src\zephyr\infra_ops\` | ☐ | ☐ | ☐ |
| 3 | 配置文件 | `D:\ZephyrAlpha\config\` | ☐ | ☐ | ☐ |
| 4 | 测试文件 | `D:\ZephyrAlpha\tests\infra_ops\` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者 |
| verification_status | passed | 审计者 |
| code_alignment_verified | yes | 审计者 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 模块总数 | 15 | `ls src/zephyr/` 递归统计 |
| 事件消费者 | <100/事件 | EventBus consumer group 统计 |
| 并发写入 | <50 | SQLite WAL 写入计数 |
| LLM 月费 | $0 (未启用) | CostTracker 统计 |
| Telemetry 基数 | <100/module | metrics 标签统计 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | asyncio.Queue 单进程限制 | EventBus 切 Kafka/RabbitMQ（Protocol 抽象层无缝切换） | 模块 > 300 |
| GAP-002 | 单消费者组限制 | EventBus Sharding（Consistent Hashing） | 消费者 > 500/事件 |
| GAP-003 | SQLite 单写者 | 连接池 + busy_timeout + 写队列批处理 | 并发写入 > 150 |
| GAP-004 | 本地 AES-256-GCM | SecretsManager 升级到 Vault（Protocol 抽象层） | 首次安全事故 |
| GAP-005 | 单节点 | SqliteLeaderElection → etcd Raft | 多节点部署需求 |
| GAP-006 | 单进程 | ModuleSandbox 进程隔离 | AI 代码隔离需求 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v5.0.1 | 5 | 基线 | 15 RI模块 + 29代码骨架 + 48 RL约束 | ✅ |
| v6.0.0 | 6 | 模板v3.3重构 | 章节重排+新增§3.2/§6/§9/§12/§14/§15/§16/§18 | ✅ |
| v6.1.0 | 7 | 模板v3.5/v3.6升级 | §0前移+§7/§15删除+§14增加类型列+§10拆分+铁律#13~#15+蓝图拆分判定标准 | ✅ |

### 触发条件与扩展路径

| 条件 | 动作 |
|------|------|
| 模块 > 300 | RI-01 切 Kafka/RabbitMQ（Protocol 抽象层无缝切换） |
| pub/sub 消费者 > 500/事件 | 触发 EventBus Sharding |
| 模块 > 100 或 首次合规要求 | **触发 RI-13 EventStore**（ES+CQRS） |
| 首次跨模块多步骤回滚需求 | **触发 RI-13 SagaCoordinator**（Phase 4） |
| LLM API 月费 > $50 | RI-15 CostTracker 启用预算硬限额 + 自动降级到小模型 |
| LLM API 月费 > $500 | CacheLayer 启用全量语义缓存 + 查询重写 + prompt 自动压缩 |
| 总LLM月费 > $1000 | RI-15 全资源FinOps面板自动生成 |
| 外部依赖 > 10 个 | ResilienceGuard 降级链独立为 YAML 配置 |
| 首次安全事故 | SecretsManager 升级到 Vault（Protocol 抽象层） |
| AI 写操作错误率 > 5% | DryRunSimulator 审查级别升级——所有写操作必须人工 approve |
| AI 写操作错误率 < 3% 持续 1h | DryRunSimulator 审查级别自动降级——恢复自动审批模式 |
| AutoDiagnostics 误报率 > 30% | TrustDecayTracker → 自动降级为"建议模式" |
| 同指标修复触发 > 3 次/小时 | SelfLimiter → 暂停该指标的自动修复回路→升级 Owner |
| 模块 > 500 且 发现不可变部署需求 | Phase 5: RI 模块不可变部署 |
| 全部 Phase 完成 | 自动切换 Phase ∞（维护期） |
| Owner 激活"休假模式" | 熔断恢复/预算限额/轮转延期全自动 |
| Owner 每日告警 > N=10 | 超出告警自动降级为"日报汇总" |
| Owner 认知负荷 C_today > 0.8×C_max | 激活"轻负载日" |
| 进入睡眠时段（23:00-07:00） | 激活 Sleep-Time Protocol |
| 睡眠时段+核心回路DOWN+3次自愈失败 | 紧急唤醒 Owner |
| 连续72h无Owner手动介入 | 弃用螺旋防护 |
| 每月固定时间 | Owner 消失演练（6h） |
| 模型 > 3 次 API 调用失败 | ModelFallbackChain 自动切换备选模型 |
| 全部模型调用失败 | AIBackendExhaustedError——暂停AI施工+升级Owner |
| 单模块连续crash ≥ 5次 | ModuleSandbox 永久隔离该模块+通知Owner |
| 单次部署错误率>5% | Canary自动回滚 |
| Dependabot/SBOM报告新CVE | 自动评估影响面——HIGH/CRITICAL→立即飞书 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-INF002-01 | EventBus 实现 | asyncio.Queue / Kafka / Redis Streams | asyncio.Queue | 零依赖；模块<300不需要Kafka | 2026-05-01 |
| 2 | D-INF002-02 | 幂等策略 | ES天然去重 / SQLite TTL / 双写 | 分级：关键流ES+非关键流SQLite | 关键流零TTL过期风险 | 2026-05-01 |
| 3 | D-INF002-03 | DI容器归属 | 独立l01文件 / MOD-INF-016承载 | MOD-INF-016承载 | 消除双DI容器重复 | 2026-05-01 |
| 4 | D-INF002-04 | EventStore引入时机 | 立即实现 / 触发式渐进 | 触发式渐进 | 1人+AI高风险决策；76%金融机构已验证ES | 2026-05-01 |
| 5 | D-INF002-05 | 并发模型 | asyncio / multiprocessing | asyncio | I/O密集型GIL无影响；线程更轻量 | 2026-05-01 |
| 6 | D-INF002-06 | 密钥管理 | 本地AES-256-GCM / Vault | 本地AES-256-GCM | 单机足够；Phase 5触发时迁移Vault | 2026-05-01 |
| 7 | D-INF002-07 | Crash-Only设计 | 优雅关闭优先 / Crash-Only | Crash-Only | 无人值守场景下自恢复100% | 2026-05-01 |
| 8 | D-INF002-08 | 交易模式默认 | NORMAL / PAPER | PAPER | AI施工→直接操作真实账户=0 | 2026-05-01 |
| 9 | D-INF002-09 | AI自治权限 | 全自动 / 信任衰减 | 信任衰减 | 误报>30%→降级"建议模式" | 2026-05-01 |
| 10 | D-INF002-10 | 模板v3.3重构 | 保持旧结构 / 按新模板重构 | 按新模板重构 | REQUIRED_SECTIONS合规；AI阅读顺序优化 | 2026-05-14 |
| 11 | D-INF002-11 | 模板v3.5/v3.6升级 | 保持v3.3 / 升级到v3.5/v3.6 | 升级到v3.5/v3.6 | §0前移提升AI阅读效率；§7/§15删除减少噪音；§10拆分增加依赖可追溯性 | 2026-05-14 |
| 12 | D-INF002-12 | EventBus优先级队列 | 无优先级 / PriorityQueue四级 | PriorityQueue四级 | 风控告警不被积压事件阻塞 | 2026-05-01 |
| 13 | D-INF002-13 | ConfigCenter交互矩阵 | 无 / pairwise组合测试 | pairwise组合测试 | 防止Flag组合引入bug | 2026-05-01 |
| 14 | D-INF002-14 | ResilienceGuard七合一 | 独立组件 / 统一基座 | 统一基座 | 熔断+限流+降级+隔离+脱落+重试配额+自适应并发联动 | 2026-05-01 |
| 15 | D-INF002-15 | HealthCheck SLI阈值具体化 | 主观判定 / 数值阈值 | 数值阈值 | 消除DEGRADED判定歧义 | 2026-05-01 |
| 16 | D-INF002-16 | TelemetryCollector PromptFingerprint | 无 / 追踪AI行为归因 | 追踪AI行为归因 | AI行为可追溯 | 2026-05-01 |
| 17 | D-INF002-17 | CacheLayer DataAffinity | 无 / Affinity hints | Affinity hints | 减少跨模块缓存miss | 2026-05-01 |
| 18 | D-INF002-18 | DryRunSimulator CrossSessionLoop | 无 / Loop检测 | Loop检测 | 消除氛围编程"上下文失忆→重复犯错" | 2026-05-01 |
| 19 | D-INF002-19 | CostTracker全资源FinOps | 仅LLM / 全资源 | 全资源 | CPU+内存+IO+LLM全覆盖 | 2026-05-01 |
| 20 | D-INF002-20 | 终选技术栈"理由"列删除 | 保留 / 删除并补充到§18 | 删除并补充到§18 | 理由属于决策记录（§18），不属于技术选型表 | 2026-05-15 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径 | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链或垃圾积累 |
| 8 | 禁止模糊词 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

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
| Runtime Integration 蓝图中"EventBus 分片策略" | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| Runtime Integration 蓝图中"AI Backend 模型降级链" | **原地** | 模型降级是 RI 核心能力，不是独立子系统 |
| Runtime Integration 蓝图中"独立 Phase 5 不可变部署" | **拆分** | 独立 Phase 路线图 + 与主体 depends_on 交集<30% + 内容>100行 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

> ⚠️ 如果本蓝图会导致文件被废弃/迁移/删除，**必须**在此列出。

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| 1 | 无 | — | — | — | — |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | 给足缓冲期，deprecated 至少保持1个Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表、frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 蓝图模板 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md` | 蓝图结构合规 |
| 10 | 代码构建标准 | GOV-ENG-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` | 十五字段头部标准 |
| 11 | Shared Core 蓝图 | MOD-INF-016 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\shared_core\blueprint.md` | DI容器+共享模块 |
| 12 | 容量保障蓝图 | MOD-INF-001 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\capacity_assurance\blueprint.md` | 容量规则 |

---

## 项目中已有类似功能

> ⚠️ 防重复检查：编写蓝图前**必须**确认项目中是否已有类似功能。

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | EventBus (shared) | `D:\ZephyrAlpha\src\zephyr\shared\event_bus.py` | 事件发布/订阅 | RI-01 EventBus 是此文件的蓝图设计，不是重复 |
| 2 | DIContainer (shared) | `D:\ZephyrAlpha\src\zephyr\shared\di_container.py` | 依赖注入 | RI-02 DIContainer 是此文件的蓝图设计，不是重复 |
| 3 | GracefulShutdown (shared) | `D:\ZephyrAlpha\src\zephyr\shared\graceful_shutdown.py` | 优雅关闭 | RI-04 是此文件的蓝图设计，不是重复 |

---

## 涉及的文件范围

> ⚠️ 防范围漂移：本蓝图涉及的文件范围。AI 编写和施工时**不得**超出此范围。

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | shared/ | `D:\ZephyrAlpha\src\zephyr\shared\` | 读取/修改 | RI-01~RI-11 代码实现 |
| 2 | infra_ops/ | `D:\ZephyrAlpha\src\zephyr\infra_ops\` | 读取/修改 | RI-12~RI-15 独立落地 |
| 3 | lifecycle_manager/ | `D:\ZephyrAlpha\src\zephyr\lifecycle_manager\` | 读取/修改 | hooks.py 启动钩子 |
| 4 | blueprint.md | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\runtime_integration\blueprint.md` | 修改 | 蓝图自身 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| RI 模块架构设计 | **本文档 §1-§10** | 旧版蓝图 |
| RI 施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| RI 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\shared_core\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\capacity_assurance\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 2 | `D:\ZephyrAlpha\src\zephyr\shared\` | §12 集成点 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\infra_ops\` | §4 数据模型、§11 产出物路径 |

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

## 1. 已实现代码完整路径索引

> **蓝图-代码同步强制约定（见 AGENTS.md §7 代码规范）**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 运行时集成——orchestrator 9文件已实现

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/orchestration/runtime_core/orchestrator/agent_health_monitor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/agent_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/agent_quality.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/autonomy_guard.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/backup_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/batch_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/benchmark_runner.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/blind_spot_closure.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/blueprint_health.py` | ⚠️ 骨架 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/bulkhead_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/canary_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/capacity_budget.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/chaos_engine.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/config_manager.py` | ❌ 已删除（ARCH-038 P1 空壳退役） | |
| `src/zephyr/orchestration/runtime_core/orchestrator/construction_guide.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/contract_registry.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/contract_router.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/core/agent_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/core/task_queue.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/core/wave_generator.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/data_lifecycle.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/deferred_queue.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/degrade_cascade.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/dependency_lock.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/design_decisions.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/disk_guard.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/dlq_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/failure_matcher.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/feature_flag.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/file_task_mapper.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/finding_bridge.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/hallucination_detector.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/housekeeping.py` | ⚠️ 骨架 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/incident_postmortem.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/ke_quality.py` | ⚠️ 骨架 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/knowledge_freshness.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/lean_scanner.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/model_registry.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/network_partition.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/path_index.py` | ⚠️ 骨架 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/phase_executor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/prompt_version.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/reconciliation_loop.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/resilience/deferred_queue.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/resilience/failure_matcher.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/resilience/hallucination_detector.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/resilience/rollback_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/risk_registry.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/rollback_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/rolling_upgrade.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/schema_migration.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/session_conflict.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/session_handoff.py` | ⚠️ 骨架 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/session_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/stability_guard.py` | ⚠️ 骨架 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/startup_sequencer.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/state/agent_health_monitor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/state/file_task_mapper.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/state/session_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/state/state_synchronizer.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/state_propagation.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/state_synchronizer.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/system_transfer.py` | ⚠️ 骨架 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/task_queue.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/teardown_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/trigger_router.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/version_manifest.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/runtime_core/orchestrator/wave_generator.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/test_agent_orchestrator.py` | ✅ 已实现 | |
| `tests/test_agent_health_monitor.py` | ✅ 已实现 | |
| `tests/test_hallucination_detector.py` | ✅ 已实现 | |
| `tests/test_rollback_manager.py` | ✅ 已实现 | |
| `tests/test_state_synchronizer.py` | ✅ 已实现 | |
| `tests/test_trigger_router.py` | ✅ 已实现 | |
| `tests/test_file_task_mapper.py` | ✅ 已实现 | |
| `tests/test_wave_generator.py` | ✅ 已实现 | |
| `tests/test_deferred_queue.py` | ❌ 未实现 | |
| `tests/integration/test_agent_e2e.py` | ✅ 已实现 | |

### 1.3 配置文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `config/trigger_router.yaml` | ✅ 已实现 | |
| `config/capabilities.yaml` | ✅ 已实现 | |
| `config/session_state_machine.yaml` | ✅ 已实现 | |

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

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-15 | 6.1.0 | 压缩工作流：终选技术栈"理由"列删除（补充到§18 D-INF002-12~20）；CI/CD表"理由"列删除；§3.1 RI-12~15状态❌→✅对齐§0.1；frontmatter日期更新2026-05-15 |
| 2026-05-14 | 6.1.0 | v3.5/v3.6升级：§0前移至概述后；§7备选方案删除（信息由§18决策记录覆盖）；§15后果删除（正面与§1重复，负面合并到§14风险）；§14增加"类型"列；§0.1增加"存在性"+"阻塞原因"列；§5.1去掉"原因"列；§5.3标注临时时态属性+执行状态列；§10拆为§10.1-§10.4；铁律新增#13~#15；新增蓝图拆分判定标准；§16.3施工步骤时态属性；尾部施工声明标注时态属性；frontmatter version=6.1.0/generation=7/last_updated=2026-05-14 |
| 2026-05-14 | 6.0.0 | v3.3重构：章节重排+新增§3.2/§6/§9/§12/§14/§15/§16/§18 |
| 2026-05-01 | 5.0.1 | 基线：15 RI模块 + 29代码骨架 + 48 RL约束 | �

## Consumers
- zephyr.runtime_integration (internal)
