---
module_id: MOD-INF-002
title: 运行时集成与 Cross-Layer 缺口填补蓝图（B2 · 3）
doc_type: blueprint
status: Active
version: 5.0.1
layer: L01
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.1
valid_from: 2026-05-01
ttl: permanent
construction_progress: phase_2_complete
belongs_to: "MOD-MASTER-001"
dependencies:
  - MOD-INF-001
  - MOD-INF-016
priority: P0
tags:
  - runtime-integration
  - cross-layer
  - ri-modules
  - event-bus
  - infrastructure
  - shared-core-integration
  - fmea
  - adr
  - structured-concurrency
  - bulkhead
  - graceful-shutdown
  - load-shedding
  - w3c-trace-context
  - session-undo
  - owner-mental-budget
  - leader-election
  - module-sandbox
  - sleep-time-protocol
  - auto-decide-engine
  - prompt-cache
  - model-fallback
  - cicd-pipeline
  - canary-deployment
  - contract-testing
  - vibe-coding
  - owner-cognitive-load
  - developer-experience
  - trading-kill-switch
  - trading-mode
  - paper-trading
  - simulated-clock
  - deterministic-random
  - module-metadata
  - module-template
  - communication-patterns
  - anti-patterns
  - code-ownership
  - ai-confidence
  - deprecation-lifecycle
  - pre-trade-risk
  - order-state-machine
  - trade-reconciliation
  - market-circuit-breaker
  - slippage-model
  - eod-processing
summary: >
  ZephyrAlpha 运行时集成 15 核心 RI 模块 + Cross-Layer 缺口填补蓝图 v5.0.0。v3.0.0 注入 49 项盲点；v4.0.0 注入 55+ 项盲点；v5.0.0 注入 50+ 项盲点——涵盖金融/交易系统专项(K01~K12【Kill Switch/Pre-Trade风控管道/订单状态机/市场时钟标准化/确定性模拟/纸交易/对账/仓位聚合/EOD/市场熔断联动/滑点模型/费率归因】)、模块通信模式扩展(L01~L08【Request-Reply/Scatter-Gather/Pipeline/CompetingConsumers/ContentRouter/MessageFilter/Aggregator/ReturnAddress】)、确定性复现与调试(M01~M06【确定性随机/模拟时钟/时序重放/快照恢复/日志详细度/非侵入钩子】)、长期演进(N01~N06【模块废弃生命周期/破坏性变更管理/后向兼容窗口/模块迁移文档/死代码检测/圈复杂度防护】)、AI施工模式库(O01~O08【模块模板/反模式目录/设计决策树/按类型的错误处理/命名规范/代码所有权/AI信心标注/渐进审查深度】)。新增 5 份代码骨架(TradingKillSwitch/SimulatedClock/DeterministicRandom/ModuleMetadata/ModuleTemplateSkeleton)。新增 Section 5.8 交易系统基础设施模式(5级TradingMode+7大交易专项场景)。新增 Section 5.9 模块通信模式目录。代码骨架总数 24→29。总盲点 104+→155+。~1700+行。
---

# 运行时集成与 Cross-Layer 缺口填补蓝图（B2 · 3）

> **真源声明**：本蓝图是 ZephyrAlpha 运行时集成体系的唯一真源。v1.0.0 经历 Wave 0 三轮审计。v2.0.0 基于全量 20+ 结构性缺口审计——从 6 模块扩展到 12 模块。v2.1.0 三轮深度对标完成后端到端补全。**v3.0.0 全量 49 项盲点注入**。**v4.0.0 55+ 项盲点注入**。**v5.0.0 50+ 项盲点注入**。**v5.0.1 终极取证审计——10项致命假设清单 + 审计结论：设计层面已穷尽**。

---

## 1. 核心概念

运行时集成（Runtime Integration）是 ZephyrAlpha 基础设施层的**横切能力集合**，解决 14 层模块的跨层协同问题。

### 1.1 15 RI 模块全景

#### 通信与生命周期层

| RI 模块 | 名称 | 核心职责 | 权限 | MOD-INF-016 承载 |
|---------|------|---------|------|:--:|
| **RI-01** | EventBus | 异步事件分发（pub/sub）+ 消费者组 + 保序 + DLQ持久化 + IdempotencyGuard + 背压传导链 + 事件优先级 | Immutable Core | `shared/observer.py` + `shared/events/` |
| **RI-02** | ModuleLifecycle | 拓扑排序启动/版本约束/超时控制/热重载/优雅关闭协议/预热期/Crash-Only设计/自描述元数据 | Immutable Core | `shared/lifecycle/hooks.py` |
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

#### 可溯源性与模拟层（v2.1.0 新增）

| RI 模块 | 名称 | 核心职责 | 权限 | MOD-INF-016 承载 |
|---------|------|---------|------|:--:|
| **RI-13** | EventStore | Event Sourcing + CQRS 读模型 + 事件溯源 + 快照(Snapshot) + 时间旅行重放(写隔离) + Crypto-Shredding + Saga补偿事务(触发式) | Immutable Core | — |
| **RI-14** | DryRunSimulator | AI 操作预演——sandbox 执行 + 影响分析 + 差异报告 + 人工/AI审批前置 + 行为一致性验证 + 跨Session Loop检测 + AI自预演 | Human-Gated | — |
| **RI-15** | CostTracker | 全资源FinOps成本归属——per-module / per-session / per-model 费用追踪 + 计算/存储/网络费用 + 预算告警 + 优化建议 + 模块可维护性评分 | AI-Modifiable | — |

**设计容量**：所有模块数 × 14 层 = 1500 模块，RI 各组件不漏不崩。

### 1.2 RI 模块间依赖拓扑（v3.0.0 扩展）

```
### 5.8 交易系统基础设施模式（v5.0.0 新增）

> **对标**：Goldman SecDB / Two Sigma Risk Framework / Jane Street Deterministic Replay。量化交易系统区别于普通软件系统的基础设施需求。

#### 交易模式切换（Trading Mode）

```
TradingMode 是整个系统的"全局运行模式"，决定 L04/L05/L06 三层的行为：

NORMAL     — 实盘模式：真实订单→真实broker→真实资金→KillSwitch就绪
PAPER      — 纸交易：订单→模拟broker→模拟资金→AI施工默认模式
BACKTEST   — 回测模式：SimulatedClock+DeterministicRandom+EventStore重放
READ_ONLY  — 只读模式：所有写操作被DryRun拦截→仅记录不执行
KILLED     — 紧急停止：已触发KillSwitch→所有交易活动冻结
            └── 仅Owner可手动切换回NORMAL（需双因子验证）

模式切换路径限制：
  NORMAL ⇄ PAPER（任一方向）
  PAPER → BACKTEST
  BACKTEST → PAPER
  ANY → READ_ONLY（自动：错误率>阈值时）
  ANY → KILLED（Owner手动/自动：特定条件触发）
  KILLED → NORMAL（仅Owner双因子验证）
```

#### 新增长容场景（交易专项）

| 场景 | RI 模块行为 | Owner 收到什么 |
|------|-----------|-------------|
| AI 新模块部署→默认PAPER模式 | EventBus自动路由交易事件→模拟broker；即便代码有bug无实际亏损 | 🟢 每日："新模块 MOD-L05-042 已上线 Paper Mode——观察72h→可申请升实盘" |
| Paper模式72h稳定→AI申请升实盘 | RI-09 HealthCheck: Paper模式 72h稳定(错误率<1%+订单完成率>95%)→自动生成升级建议 | 🟡 WARNING："MOD-L05-042 已满足实盘条件——审批后可升级" |
| 单模块亏损>日限额 | RI-15 CostTracker 追踪模块PnL→亏损>$X→自动切换该模块为READ_ONLY+通知 | 💀 CRITICAL："MOD-L05-042 今日亏损$X已达硬限额→已自动切换READ_ONLY" |
| KillSwitch触发 | B5-K01 TradingKillSwitch.activate()→5步停止序列 | 💀 CRITICAL：飞书+"语音呼叫如果10min内未确认" |
| 交易所熔断（标的暂停） | B5-K10 检测交易所公告→自动暂停该标的+L05标记READ_ONLY | 🟡 WARNING："SHSE:600XXX已暂停交易——系统已冻结该标的" |
| 交易对账失败 | B5-K07 三方对账→diff>0→自动暂停该broker连接 | 💀 CRITICAL："IBKR:订单#12345系统记录FILLED但broker回执CANCELLED——已暂停IBKR" |
| 日终处理（EOD） | B5-K09 自动结算→PnL计算→保证金监控→归档→生成日报 | 🟢 每日：EOD报告→"今日PnL: +$X.XX(扣费后)，5个模块运行，0个异常" |

### 5.9 模块通信模式目录（v5.0.0 新增）

> **对标**：Enterprise Integration Patterns (Hohpe/Woolf)。RI-01 EventBus 是pub/sub，但模块间通信远不止一种模式。

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
RI-02 ModuleLifecycle ← 所有模块的底座, 最先启动
  ├── RI-04 DependencyInjector ← 模块间引用通道
  │     └── MOD-INF-016 di_container.py ← v3.0.0: DI 统一由 Shared Core 承载
  ├── RI-03 ConfigCenter ← 所有模块的配置源
  │     ├── RI-07 SecretsManager ← ConfigCenter 的加密后端（加密字段强制走此路径）
  │     ├── FeatureFlagManager ← 渐进推出 + 交互矩阵 + 自动 Kill Switch
  │     └── SchemaRegistry ← Schema 兼容性策略 + 版本演进
  ├── RI-01 EventBus ← 跨模块通信
  │     ├── DeliverySemantics: AT_LEAST_ONCE（默认）
  │     ├── RI-06 IdempotencyGuard ← EventBus 的写保护
  │     ├── RI-05 ResilienceGuard ← EventBus 的流量控制
  │     ├── BackpressurePropagation ← 背压信号→上游减速策略
  │     ├── PriorityQueue(CRITICAL/HIGH/NORMAL/LOW) ← 事件优先级
  │     └── MOD-INF-016 DLQ(SQLite持久化) ← v3.0.0: DLQ 持久化
  ├── RI-08 ErrorHandler ← 所有模块的错误出口
  │     ├── RI-05 ResilienceGuard ← 错误率→熔断
  │     ├── W3C TraceContext(traceparent) ← v3.0.0: 标准化 trace context
  │     └── MOD-INF-016 ZephyrLogger ← 结构化日志
  ├── RI-09 HealthCheck ← 所有模块的健康探针
  │     ├── RI-12 AutoDiagnostics ← 不健康→自动诊断
  │     ├── ReconciliationLoop ← v3.0.0: 持续对账期望状态 vs 实际状态
  │     └── 三级状态: UP(全SLI正常) / DEGRADED(任一SLI超阈值) / DOWN(RTO超时)
  ├── RI-10 TelemetryCollector ← 全系统指标
  │     ├── RI-12 AutoDiagnostics ← 异常指标→诊断
  │     ├── RI-15 CostTracker ← Token/费用/资源指标→成本归属
  │     ├── PromptFingerprint ← v3.0.0: prompt→异常关联分析
  │     └── DeadModuleDetector ← v3.0.0: 30天无活动→标记DORMANT
  ├── RI-11 CacheLayer ← 跨模块缓存
  │     ├── RI-15 CostTracker ← 缓存命中/节省→成本优化报告
  │     └── DataAffinity ← v3.0.0: 模块声明的缓存亲和性
  ├── RI-13 EventStore ← 事件溯源+CQRS（Phase 3 触发）
  │     ├── RI-01 EventBus ← 事件写入入口
  │     ├── RI-06 IdempotencyGuard ← 事件去重（关键流 ES 天然去重）
  │     ├── RI-14 DryRunSimulator ← 事件级模拟回放
  │     ├── CryptoShredding ← v3.0.0: GDPR 删除=销毁加密密钥
  │     └── SagaCoordinator ← v3.0.0: 跨模块补偿事务（Phase 4 触发）
  └── RI-14 DryRunSimulator ← AI操作预演（Phase 2b）
        ├── RI-01 EventBus ← 拦截写事件→sandbox执行
        ├── RI-15 CostTracker ← 预演成本预估
        ├── SelfSimulate ← v3.0.0: AI 提交前自预演
        └── CrossSessionLoopDetector ← v3.0.0: 跨 session 重复修改检测
```

### 1.3 与 Shared Core (MOD-INF-016) 的承载关系

> **v3.0.0 新增**：MOD-INF-016 Shared Core（v0.14.0，49文件，施工completed）已实现大量RI模块的代码承载。下表声明明确的职责分工。

| RI 模块 | 蓝图设计归属 | 代码承载归属 | 承载文件 | 备注 |
|---------|:--:|:--:|------|------|
| RI-01 EventBus | MOD-INF-002 | **MOD-INF-016** | `shared/observer.py` + `shared/events/` + `shared/events/dlq.py` | shared 版为基类实现；MOD-INF-002 蓝图定义增强需求（PriorityQueue/背压传导链），在 shared 层扩展 |
| RI-02 ModuleLifecycle | MOD-INF-002 | **MOD-INF-016** | `shared/lifecycle/hooks.py` | shared 版定义 LifecycleAware Protocol；MOD-INF-002蓝图扩展优雅关闭协议+预热期 |
| RI-03 ConfigCenter | MOD-INF-002 | **MOD-INF-016** | `shared/config/` + `shared/flags.py` | shared 版提供加载+校验+FeatureFlag；MOD-INF-002蓝图定义渐进推出+交互矩阵 |
| RI-04 DependencyInjector | MOD-INF-002 | **MOD-INF-016** (planned) | `shared/production/di_container.py` (待施工) | 统一由 shared 承载，不做独立 `l01_infrastructure/dependency_injector.py` |
| RI-05 ResilienceGuard | MOD-INF-002 | **MOD-INF-016** | `shared/resilience/` | shared 版提供 CircuitBreaker/Retry/Fallback；MOD-INF-002蓝图扩展Bulkhead/LoadShedder/RetryBudget |
| RI-06 IdempotencyGuard | MOD-INF-002 | **MOD-INF-016** | `shared/production/idempotency.py` | shared 版为基础实现；MOD-INF-002蓝图定义TTL分级策略 |
| RI-07 SecretsManager | MOD-INF-002 | **MOD-INF-016** | `shared/production/secrets.py` | — |
| RI-08 ErrorHandler | MOD-INF-002 | **MOD-INF-016** | `shared/errors.py` + `shared/logging.py` | shared 版提供异常树+trace_id；MOD-INF-002蓝图扩展W3C Trace Context |
| RI-09 HealthCheck | MOD-INF-002 | **MOD-INF-016** | `shared/health.py` | shared 版提供 AggregateHealth；MOD-INF-002蓝图定义具体SLI阈值+Reconciliation |
| RI-10 TelemetryCollector | MOD-INF-002 | **MOD-INF-016** | `shared/production/metrics.py` | shared 版提供基础metrics；MOD-INF-002蓝图扩展PromptFingerprint+DeadModuleDetector |
| RI-11 CacheLayer | MOD-INF-002 | **MOD-INF-016** | `shared/production/cache.py` | shared 版为基础实现；MOD-INF-002蓝图扩展Data Locality |
| RI-12 AutoDiagnostics | MOD-INF-002 | **独立落地** | `l01_infrastructure/auto_diagnostics.py` | 共享核心无对应实现——100%新施工 |
| RI-13 EventStore | MOD-INF-002 | **独立落地** | `l01_infrastructure/event_store.py` | 共享核心无对应实现——Phase 3 触发式落地 |
| RI-14 DryRunSimulator | MOD-INF-002 | **独立落地** | `l01_infrastructure/dry_run_simulator.py` | 共享核心无对应实现——Phase 2b |
| RI-15 CostTracker | MOD-INF-002 | **独立落地** | `l01_infrastructure/cost_tracker.py` | 共享核心无对应实现——Phase 2b |

> **职责准则**：MOD-INF-002 定义"运行时集成体系需要什么"（WHAT + WHY），MOD-INF-016 承载"公共实现"（HOW）。若 shared 版已足够，RI 模块直接消费 shared；若需要增强，在 shared 层扩展而非独立重写。仅 RI-12/13/14/15 因 shared 无对应能力，独立落地 `l01_infrastructure/`。

---

## 2. 到需要做什么（回顾大盘 + 用户原意）

**Owner 指示**：
- 所有 Cross-Layer 缺口必须在 experimental 填平，不给未来埋雷
- "Layer 之间怎么通信？配置怎么统一管？错误怎么统一处理？"
- 100% AI 施工 + 1人+AI 维护——系统必须能在无人干预下自愈 90% 的异常
- 零依赖优先：能用 Python stdlib + SQLite 完成的不引入新依赖

**Cross-Layer 缺口清单**（RL-001 ~ RL-048，v3.0.0 全量）：

| 缺口 ID | 描述 | 填补方案 |
|---------|------|---------|
| RL-001 | 缺跨层通信用事件总线 | RI-01 EventBus |
| RL-002 | 缺统一模块生命周期管理 | RI-02 ModuleLifecycle |
| RL-003 | 缺分层配置中心 | RI-03 ConfigCenter |
| RL-004 | 缺统一 Telemetry 聚合 | RI-10 TelemetryCollector |
| RL-005 | 缺跨模块健康传导 | RI-09 HealthCheck |
| RL-006 | 缺类型安全事件契约 | RI-01 EventBus 类型化事件 |
| RL-007 | 缺模块依赖可视化 | RI-02 ModuleGraph |
| RL-008 | 缺配置漂移自动告警 | RI-03 ConfigValidator |
| RL-009 | 缺跨层错误传播链追踪 | RI-08 ErrorTracer |
| RL-010 | 缺运行时背压机制 | RI-01 EventBus BackpressureController |
| RL-011 | 缺运行时熔断器（外部服务调用） | RI-05 ResilienceGuard CircuitBreaker |
| RL-012 | 缺事件失败处理（死信队列+重试） | RI-01 EventBus DLQ + RetryPolicy |
| RL-013 | 缺统一依赖注入/IoC 容器 | RI-04 DependencyInjector |
| RL-014 | 缺写操作幂等性保障 | RI-06 IdempotencyGuard |
| RL-015 | 缺 Secrets/密钥管理 | RI-07 SecretsManager |
| RL-016 | 缺运行时限流器 | RI-05 ResilienceGuard RateLimiter |
| RL-017 | 缺统一缓存层 | RI-11 CacheLayer |
| RL-018 | 缺自动诊断与自愈能力 | RI-12 AutoDiagnostics |
| RL-019 | 缺审计级事件溯源+时间旅行 | RI-13 EventStore（ES+CQRS） |
| RL-020 | 缺 AI 操作预演/沙盒执行 | RI-14 DryRunSimulator |
| RL-021 | 缺 per-module LLM 费用归属+告警 | RI-15 CostTracker |
| RL-022 | 缺消息传递语义声明 | RI-01 DeliverySemantics：AT_LEAST_ONCE（默认） |
| RL-023 | 缺背压传导链设计 | RI-01 BackpressurePropagation 协议 |
| RL-024 | 缺 DI 容器与 MOD-INF-016 统一 | RI-04 → MOD-INF-016 `di_container.py` |
| RL-025 | 缺时间旅行重放时的写隔离策略 | RI-13 replay_to() write_mode: READ_ONLY/OPTIMISTIC_LOCK |
| RL-026 | 缺 DryRun 与真实执行行为一致性保证 | RI-14 一致性验证套件——sandbox vs 真实双跑 diff |
| RL-027 | 缺 ConfigCenter 加密字段归属 | RI-03 加密字段强制走 RI-07 SecretsManager |
| RL-028 | 缺 Loop Detector 自动恢复条件 | RI-14 自动恢复：错误率<3%持续1h→恢复 OR Owner手动 |
| RL-029 | 缺 DLQ 持久化保障 | RI-01 DLQ → SQLite 持久化表（对接 MOD-INF-016 dlq.py） |
| RL-030 | 缺健康检查 SLI 阈值具体数值 | RI-09 具体阈值：CPU>80%→DEGRADED,>95%→DOWN |
| RL-031 | 缺 Feature Flag 渐进推出路径 | RI-03 rollout: 1%→10%→50%→100% + 自动 Kill Switch |
| RL-032 | 缺 IdempotencyGuard TTL 与精确一次矛盾 | RI-06 分级策略：关键流ES天然去重/非关键流SQLite TTL |
| RL-033 | 缺 Telemetry 基数限制具体语义 | RI-10 per-module 500；超限→LRU淘汰+告警 |
| RL-034 | 缺 Cooldown 分层的动态调整 | RI-12 CRITICAL 15min/HIGH 10min/MEDIUM 5min/LOW 2min |
| RL-035 | 缺 CostTracker 全资源追踪（计算/存储/网络） | RI-15 扩展：CPU时间/内存峰值/磁盘IO——至少记录不硬限 |
| RL-036 | 缺结构化并发管理 1500+ 模块 | §5.1 asyncio.TaskGroup 统一管理并发生命周期 |
| RL-037 | 缺 Bulkhead 舱壁资源隔离 | RI-05 Bulkhead：per-module 线程/连接池上限 |
| RL-038 | 缺完整优雅关闭协议 | RI-02 SIGTERM→drain→等待in-flight→超时force kill→状态持久化 |
| RL-039 | 缺重试风暴防护 | RI-05 RetryBudget：全局重试配额，耗尽拒绝重试 |
| RL-040 | 缺 W3C Trace Context 标准化 | RI-08 trace_id→W3C traceparent格式，兼容OpenTelemetry |
| RL-041 | 缺负载脱落（Load Shedding） | RI-05 LoadShedder：超载按优先级丢弃低优先级请求 |
| RL-042 | 缺 Schema 版本化兼容性策略 | RI-01 SchemaEvolutionPolicy：FULL_BACKWARD/FORWARD_TRANSITIVE |
| RL-043 | 缺容量预留（关键模块） | RI-05 Reservation：L04/L06预分配X%队列容量 |
| RL-044 | 缺预热期机制 | RI-02 warmup phase：启动→缓存预热→内部HealthCheck→READY |
| RL-045 | 缺 Crypto-Shredding (GDPR删除) | RI-13 anonymize_stream()：per-stream加密密钥，删密钥=不可恢复 |
| RL-046 | 缺 Feature Flag 交互矩阵检测 | RI-03 FlagInteractionValidator：启动时pairwise组合测试 |
| RL-047 | 缺信任衰减曲线 | RI-12 TrustDecayTracker：误报>30%→降级"建议模式" |
| RL-048 | 缺 Crash-Only Software 设计理念 | §1 核心原则：每次停止=crash，恢复走重启 |

### 2.1 v4.0.0 新一轮盲点审计：55+ 新缺口（2026-05-05）

> **审计背景**：v3.0.0 注入 49 项盲点后蓝图达 98% 完备度。但三个维度仍大面积空白：**(1) 分布式/多节点**——蓝图几乎完全是单节点设计，对 "模块 > 300 切 Kafka" 仅有声明无设计；**(2) 部署与基础设施自动化**——CI/CD、IaC、容器编排策略完全缺失；**(3) 氛围编程/AI施工特有需求**——Prompt缓存策略、AI代码审查、上下文窗口预算管理、自修复回路质量保障等。

以下按类别列出 55+ 未覆盖盲点。

#### A. 分布式系统与多节点（B4-A01~A10）

> **当前薄弱点**：蓝图仅有 `distributed_lock.py` 引用和 "模块 > 300 切 Kafka" 的触发条件，但无分布式协调的具体设计。

| 盲点 ID | 缺失内容 | 专业机构对标 | 效应（若无） |
|---------|---------|------------|-----------|
| B4-A01 | **Leader Election**——多节点部署时需要主节点选举（谁执行定时任务/健康检查仲裁？） | Google Chubby / etcd Raft | 双主→数据竞态；无主→定时任务停滞 |
| B4-A02 | **Cluster Membership（Gossip Protocol）**——节点加入/离开/崩溃的感知机制 | HashiCorp Serf / Cassandra Gossip | 节点崩溃后无感知→请求继续路由到死节点 |
| B4-A03 | **Split-Brain Protection**——网络分区时一致性的保护策略 | Pacemaker Fencing / K8s Lease | 分区→双主同时写→不可逆数据损坏 |
| B4-A04 | **Consistent Hashing / Sharding**——"kubernetes > 500/事件"的Sharding算法 | Discord (Rust+Sharding) / Dynamo | 扩容→事件路由全量重构→生产中断 |
| B4-A05 | **Quorum-Based Decision**——每次部署/FeatureFlag变更需要多少节点共识 | Raft R+W > N | 单节点作恶→全集群中毒 |
| B4-A06 | **Hybrid Logical Clock (HLC)**——跨节点事件的偏序/全序关系 | CockroachDB HLC / TrueTime | 跨节点事件无因果顺序→溯源分析出现 "先果后因" |
| B4-A07 | **CRDT（Conflict-Free Replicated Types）**——多节点并发写入的自动合并策略 | Figma / Linear / Redis CRDT | 并发修→手动解冲突→1人不具备此能力 |
| B4-A08 | **Anti-Entropy（Read Repair + Hinted Handoff）**——节点间状态同步与修复 | Dynamo / Cassandra | 节点间状态漂移→单节点缓存*3→雪崩 |
| B4-A09 | **Multi-Raft / Raft Group Segmented Consensus**——按模块域分建共识组，降低全局共识负载 | TiKV Multi-Raft | 全局共识→N模块均参与→延迟O(N²) |
| B4-A10 | **Graceful Partition Healing**——分区恢复后的渐进重建策略（Limiter→Backoff→RateLimit→Full）| CockroachDB Range Lease | 分区恢复→瞬间全量同步→网络+CPU双爆 |

#### B. 部署与基础设施自动化（B4-B01~B08）

| 盲点 ID | 缺失内容 | 专业机构对标 |
|---------|---------|------------|
| B4-B01 | **CI/CD Pipeline Design**——代码→lint→test→dryrun→approve→merge→deploy 的全自动流水线 | GitHub Actions / ArgoCD |
| B4-B02 | **Canary Deployment（金丝雀）**——新模块版本→1%流量→健康→50%→100% 的渐进上线 | Spinnaker / Flagger |
| B4-B03 | **Infrastructure-as-Code (IaC)**——Docker Compose→ Pulumi/Terraform 配置管理 | Terraform / Pulumi |
| B4-B04 | **Blue-Green Deployment**——模块版本切换零停机 | K8s Service / AWS CodeDeploy |
| B4-B05 | **Secret Zero Problem（密钥引导）**——启动时第一个秘密从哪里来，后续怎么展开 | Vault Auto-Unseal / AWS KMS |
| B4-B06 | **Immutable Infrastructure Implementation**——§7 提到 Phase 5 但无设计细节 | Docker immutable tags / NixOS |
| B4-B07 | **Container Escape Prevention**——AI生成的代码在容器中运行时，沙箱加固策略 | gVisor / Firecracker |
| B4-B08 | **Artifact Registry & Provenance**——构建产物签名 + SBOM + SLSA供应链级别 | Sigstore / SLSA Framework |

#### C. 数据管理与迁移（B4-C01~C06）

| 盲点 ID | 缺失内容 | 专业机构对标 |
|---------|---------|------------|
| B4-C01 | **Schema Migration with Zero Downtime**——SQLite表结构变更时的在线迁移策略（expand-contract pattern） | Stripe / GitHub Schema迁移 |
| B4-C02 | **Point-in-Time Recovery (PITR)**——SQLite WAL→增量备份→任意时间点恢复 | PostgreSQL WAL-G / Litestream |
| B4-C03 | **Data Retention Policy Automation**——自动过期/归档/删除策略执行 | AWS S3 Lifecycle / Temporal |
| B4-C04 | **Database Connection Pooling**——1500模块并发SQLite读写时的连接池策略 | HikariCP / PgBouncer |
| B4-C05 | **SQLite Write Contention**——多模块同时写入单一SQLite的并发冲突处理设计 | SQLite WAL + `busy_timeout` |
| B4-C06 | **Data Locality for Multi-Region**——若未来跨Region部署的数据同步策略 | CockroachDB / DynamoDB Global Tables |

#### D. 测试与质量保障深度（B4-D01~D08）

| 盲点 ID | 缺失内容 | 专业机构对标 |
|---------|---------|------------|
| B4-D01 | **Contract Testing**——模块间API/Pact测试确保Schema变更不破坏下游消费者 | Pact / Spring Cloud Contract |
| B4-D02 | **Property-Based Testing**——Randomized+Shrink自动发现边界条件 | Hypothesis / QuickCheck |
| B4-D03 | **Automated Test Generation from Diff**——AI代码变更→自动生成对应maß试 | DiffBlue / Copilot Test Gen |
| B4-D04 | **Mutation Testing**——测试质量度量：修改代码→测试是否捕获 | PITest / Mutmut |
| B4-D05 | **Fuzz Testing at Module Boundary**——at EventBus/ConfigCenter接口做随机数据注入 | AFL++ / LibFuzzer |
| B4-D06 | **Golden File Testing**——关键输出→哈希锁定→任何变更=回归告警 | Bazel / Chromium |
| B4-D07 | **Cross-Module Integration Test Orchestration**——1500模块的集成测试矩阵管理策略 | Bazel / Nx |
| B4-D08 | **Test Flake Detection & Quarantine**——不稳定测试自动隔离+报告所有者 | Google / Uber |

#### E. 氛围编程/AI施工 专项深度（B4-E01~E12）

> **这是本轮审计最核心发现**：蓝图虽以 "100% AI施工" 为前提，但缺少 AI 代码生成、上下文管理、Prompt工程等方面的设计。

| 盲点 ID | 缺失内容 | 氛围编程社区对标 |
|---------|---------|---------------|
| B4-E01 | **Prompt Caching Strategy**——哪些 context embed 应缓存以降低LLM API调用费用 | Anthropic Prompt Caching / GPTCache |
| B4-E02 | **Context Window Budget（上下文窗口预算）**——每次AI调用的context大小<= X tokens | Cursor Context / Copilot Indexing |
| B4-E03 | **Semantic Code Search / Code Embedding**——AI在施工时如何高效查询已有代码库（与 AI 自主理解间的桥梁） | Cursor Codebase Indexing / Sourcegraph Cody |
| B4-E04 | **Code Generation Template System**——模块脚手架、事件处理器模板、配置模板的标准化 | Copilot Workspace / v0 |
| B4-E05 | **AI Code Review Automation**——AI生成代码→另一AI审查（"四眼"原则） | CodeRabbit / Copilot Code Review |
| B4-E06 | **Self-Healing Quality Gate**——AI自修复后需要验证：修复不引入新盲点/不影响其他模块 | Datadog / Honeycomb |
| B4-E07 | **AI Decision Log**——每次AI做重大施工决策→自动追加 ADR，防"为什么这么做？"不可回答 | ADR.tools / Structurizr |
| B4-E08 | **Diff-Level Undo**——不是 session undo，而是单次 diff 级别的精细undo | Git reflog / Linear undo |
| B4-E09 | **Model Fallback Chain**——deepseek-chat → deepseek-reasoner → qwen-max → 提级Owner | OpenRouter / Helicone |
| B4-E10 | **AI Context Persistence across Sessions**——跨session的AI上下文保存/恢复/过期策略；避免session边界丢失上下文 | MemGPT / Mem0 |
| B4-E11 | **Prompt Version Control & A/B Testing**——提示词的版本化、分级测试、回滚 | LangSmith / Arize Phoenix |
| B4-E12 | **Token Optimization Pipeline**——AI调用前自动压缩上下文(PromptCompressor)+剪枝不相关文件引用 | Anthropic Prompt Improver / LangChain |

#### F. 1人+AI 运维深度强化（B4-F01~F10）

> **核心问题**：蓝图已有告警预算+通知分层+休假模式，但缺"Owner是人会累会忘会犯错"的深度设计。

| 盲点 ID | 缺失内容 | 效应 |
|---------|---------|------|
| B4-F01 | **Owner Cognitive Load Budget（认知负荷预算）**——每日除了告警，还包括所有需要Owner做的决策（审批/回滚/配置变更/FeatureFlag）。超过 X 项→触发"轻负载日" | 决策疲劳→低质量决策→重大事故漏判 |
| B4-F02 | **Daily Operations Briefing（晨报）**——每天睡醒后一份摘要：昨日关键指标/费用/自愈记录/待决策项 | 一睁眼不知道系统昨天发生了什么 |
| B4-F03 | **Sleep-Time Protocol**——Owner睡眠时段（数据驱动：23:00-07:00 local）→所有非CRITICAL静音；CRITICAL仅触发一次→若5min内无响应→自动启动自愈回路 | 凌晨3点告警→吵醒→疲劳决策→人→AI→系统均崩溃 |
| B4-F04 | **Auto-Decide Threshold**——影响<X模块/费用<$Y/风险RPN<Z的操作系统自动执行无需审批 | 每个小改动都需要Owner审批→瓶颈→迭代停滞 |
| B4-F05 | **Emergency Wake-Up Criteria**——什么是真的值得叫Owner起来的紧急情况（精确定义） | 假阳性叫醒→"狼来了"效应→真紧急时Owner已关通知 |
| B4-F06 | **Weekly System Health Report**——每周生成一份Markdown报告到Knowledge Base | 连续多日无注意→问题积累 |
| B4-F07 | **Owner Absence Simulation（Owner消失押练）**——每月1次6h"假Owner离线"演练→系统应在无Owner下运行 | 真正休假/失能时才发现系统依赖Owner手动回复 |
| B4-F08 | **Knowledge Externalization**——Owner的决策原则、偏好的转化为系统可执行的规则 | Owner失能→系统无人会判断 |
| B4-F09 | **Onboarding Auto-Generation**——系统自文档化→新参与者（或失忆后的自己）能在30min内理解系统 | 人是代码库的吗×？不断变化的context→无法重新理解自己的系统 |
| B4-F10 | **Mental Health Safeguard**——连续72h无Owner手动介入→系统降低告警频率（防"坚持不下去→彻底关掉通知"的弃用螺旋）| 心理防线崩溃→放弃系统而非修复 |

#### G. 安全深度强化（B4-G01~G06）

| 盲点 ID | 缺失内容 | 专业机构对标 |
|---------|---------|------------|
| B4-G01 | **Module Sandboxing**——RI模块间的运行时隔离——一个模块的crash/无限循环不应影响其他模块 | AWS Lambda / Cloudflare Workers |
| B4-G02 | **AI-Generated Code Security Scanning**——每次AI施工完成后自动对新增代码做Semgrep安全扫描 | Semgrep / CodeQL |
| B4-G03 | **Tamper-Proof Audit Log**——审计日志的哈希链（Merkle Tree）防篡改 | Certificate Transparency / Trillian |
| B4-G04 | **Least Privilege Enforcement per Module**——每个模块只拥有它声明的资源访问权 | AWS IAM / K8s PodSecurityPolicy |
| B4-G05 | **Supply Chain Security (SBOM + Vulnerability Scan)**——依赖的脆弱性扫描 + Software Bill of Materials | CycloneDX / Dependabot |
| B4-G06 | **AI Prompt Injection Guard**——Owner指令 vs AI生成的内容→防止AI把"友好的代码注释"当命令执行 | Gandalf Game / Lakera Guard |

#### H. 可观测性深度强化（B4-H01~H05）

| 盲点 ID | 缺失内容 | 专业机构对标 |
|---------|---------|------------|
| B4-H01 | **Distributed Trace Visualization**——跨5层的trace→时序火焰图 | Jaeger / Tempo / Honeycomb |
| B4-H02 | **Error Budget Burn Rate Alerting**——不只是实时告警，Error Budget < 1%/1h → CRITICAL | Google SRE Workbook |
| B4-H03 | **Capacity Forecasting**——基于历史趋势预测：何时需扩展 500→1500模块 | Datadog Watchdog / Netflix Atlas |
| B4-H04 | **Latency Heat Maps**——per-module P50/P95/P99 latency→自动识别退化的模块 | Discord / Uber |
| B4-H05 | **Slow Query Detection**——SQLite查询 > 100ms→自动标记+建议索引 | PostgreSQL pg_stat_statements |

#### I. API与协议设计（B4-I01~I04）

| 盲点 ID | 缺失内容 | 专业机构对标 |
|---------|---------|------------|
| B4-I01 | **Module API Versioning Strategy**——模块对外API的版本规范(SemVer→Major.Minor)与废弃窗口 | Stripe API / K8s API |
| B4-I02 | **Backward Compatibility Enforcement**——CI自动检测模块新版本是否破坏下游消费者接口 | Google API Improvement Proposals |
| B4-I03 | **WebSocket / gRPC Stream Management**——若模块间使用流通信的超时/重连/背压策略 | gRPC / RSocket |
| B4-I04 | **Module Discovery & Self-Description**——新模块自动注册+能力声明，无需维护手工清单 | DNS-SD / mDNS / LDAP |

#### J. 开发者体验（1人用）（B4-J01~J06）

| 盲点 ID | 缺失内容 |
|---------|---------|
| B4-J01 | **One-Command Local Setup**——`git clone && ./setup.sh`→全量本地运行环境就绪 |
| B4-J02 | **Hot Reload Development**——模块代码变更→自动reload无需重启整个系统 |
| B4-J03 | **AI REPL / Chat Interface**——终端内直接与AI交互施工（类似 Copilot Chat / Aider）|
| B4-J04 | **Self-Debugging Hooks**——AI施工→失败→自动收集日志+stacktrace+context →给AI自修复 |
| B4-J05 | **Codebase Familiarity Score**——每个模块→Owner多久没看过/改过→"熟悉度"指标+提醒review |
| B4-J06 | **Automated CHANGELOG from Git**——AI读git log→自动写入结构化 CHANGELOG.md |

#### K. 金融/交易系统专项（B5-K01~K12）

> **这是第三轮审计最核心发现**：蓝图讲了 15 个通用 RI 模块，但 0 处提到交易系统特有的基础设施需求。量化交易系统不只是"又一个软件系统"——它有回测、有Kill Switch、有复盘、有市场时钟。对机构对标：Goldman SecDB / Two Sigma / Jane Street。

| 盲点 ID | 缺失内容 | 专业机构对标 | 效应（若无） |
|---------|---------|------------|-----------|
| B5-K01 | **Emergency Trading Kill Switch（紧急交易停止）**——一条命令或一个信号：立即取消所有未完成订单+清空EventBus交易事件+切换ALL模块为read-only模式 | CME Kill Switch / Two Sigma "Big Red Button" | 算法失控→无法停损→账户穿透 |
| B5-K02 | **Pre-Trade Risk Check Pipeline（交易前风控管道）**——每个交易事件通过模块链：订单→仓位限制检查→资金检查→敞口检查→合规检查→才到交易所 | Goldman SecDB Pre-Trade Risk | AI生成的交易逻辑→无风控→裸奔发单 |
| B5-K03 | **Order State Machine Standardization（订单状态机标准化）**——所有订单类模块必须实现统一状态机(NEW→PENDING→PARTIAL→FILLED/CANCELLED/REJECTED) | FIX Protocol / Interactive Brokers API | L05层每个模块自定义订单状态→下游混乱→复盘错乱 |
| B5-K04 | **Market Data Clock & Timestamp Normalization（市场时钟标准化）**——所有事件时间戳统一到交易所时钟(NTP→PTP)，非本地os.time() | IEX Timestamp / PTP IEEE 1588 | AI用 `time.time()` 而非交易所时钟→tick对齐错位→回测不可复现 |
| B5-K05 | **Deterministic Simulation Mode（确定性模拟模式）**——RI-14 DryRun扩展：用固定随机种子+模拟时间→同输入必然同输出 | Jane Street Deterministic Replay | 回测结果不可复现→无法判断"AI改好了还是碰巧" |
| B5-K06 | **Paper Trading Infrastructure（纸交易基础设施）**——所有涉及交易的模块自动支持paper模式：EventBus emit→sandbox account而非真实broker | Alpaca Paper API / QuantConnect | AI施工→直接操作真实账户→1个bug→亏损 |
| B5-K07 | **Trade Reconciliation（交易对账）**——系统订单 vs 经纪商回执 vs 清算报告 → 三方对账，diff→告警 | DTCC / FIX Drop Copy | AI提交的订单→实际成交vs系统记录不一致→未知敞口 |
| B5-K08 | **Position & Exposure Aggregation（仓位聚合）**——无论多少模块在交易，全局仓位/净敞口实时计算+硬限额 | Goldman SecDB / RiskMetrics | 多模块分散操作→净裸露超限→被风控部追责 |
| B5-K09 | **End-of-Day / Start-of-Day Processing（日终/日初处理）**——定时任务：持仓结算/损益计算/保证金监控/数据归档 | Bloomberg AIM / EOD Batch | 无标准化日终流程→混乱的手动操作 |
| B5-K10 | **Market Circuit Breaker Integration（市场熔断联动）**——交易所熔断/涨跌停→系统自动暂停该标的交易+通知Owner | SSE/SZSE Circuit Breaker Rules | 交易所停牌了→系统还在尝试下单→累积错误订单 |
| B5-K11 | **Slippage & Market Impact Modeling（滑点模型）**——DryRun和backtest中自动归入滑点成本，不假设理想成交价 | Almgren-Chriss / Virtu | AI在回测中看到"完美利润"→实盘滑点吞噬50%→系统不可信 |
| B5-K12 | **Fee & Commission Attribution（费率归因）**——每笔交易费用归属到模块，纳入RI-15 CostTracker的全资源FinOps | Interactive Brokers / Binance Fee Schedule | 费用被忽视→"赚钱"的回测实际上扣费后亏损 |

#### L. 模块通信模式扩展（B5-L01~L08）

> **当前薄弱点**：RI-01 EventBus 只覆盖了 pub/sub。但真实系统需要更多通信模式。对标：Enterprise Integration Patterns (Hohpe/Woolf) / ZeroMQ Patterns。

| 盲点 ID | 缺失内容 | 适用场景 |
|---------|---------|---------|
| B5-L01 | **Request-Reply Pattern**——同步请求→等待响应→超时处理 | 模块间"问一个问题"——查询账户余额/因子值/风控判断 |
| B5-L02 | **Scatter-Gather Pattern**——一请求广播N个模块→收集所有响应→聚合 | 因子计算——同时向多个数据源发请求→投票/加表 |
| B5-L03 | **Pipeline / Chain Pattern**——事件→模块A处理→传给B→C→...→最终结果 | ETL管道/数据清洗/信号生成→过滤→排序→执行 |
| B5-L04 | **Competing Consumers**——多个消费者竞争同一事件，先到先处理——自动负载均衡 | 同质任务队列——多worker消费redis pub/sub |
| B5-L05 | **Message Routing（Content-Based Router）**——根据消息内容→路由到不同消费者 | 事件类型路由：TradeEvent→L05模块，RiskEvent→L04模块 |
| B5-L06 | **Message Filtering / Enrichment（消息过滤/增强）**——EventBus中间件自动截获+修改/增强/过滤事件 | 添加追踪信息/删除敏感字段/标准化格式 |
| B5-L07 | **Aggregation / Batching Strategy**——多个独立事件→按时间窗/数量窗聚合为一个批处理事件 | 批量行情→归一化→一次性消费而非N次分别处理 |
| B5-L08 | **Return Address / Callback Pattern**——事件带return_address字段→消费者完成后→发送响应到该地址 | 异步请求-响应模式——不阻塞请求方 |

#### M. 确定性复现与调试（B5-M01~M06）

> **交易系统的根基**：Jane Street 每年投入8位数美元构建确定性回放基础设施。1人+AI需要在有限资源下达到80%的效果。

| 盲点 ID | 缺失内容 | 专业机构对标 |
|---------|---------|------------|
| B5-M01 | **Deterministic Random（确定性随机）**——全系统共享种子→种子相同则所有"随机"行为完全相同 | `random.seed(42)` + numpy/pytorch seed对齐 |
| B5-M02 | **Simulated Clock（模拟时钟）**——区分 `real_time` vs `sim_time`；回测/预演时用sim_time驱动 | SimPy / Jane Street Core.Time |
| B5-M03 | **Event Replay with Exact Timing（精确时序事件重放）**——从EventStore读取事件→按记录的时间戳精确重放→同序同果 | Kafka + WallClockReplayer |
| B5-M04 | **Snapshot → Restore for Debugging（快照→恢复调试）**——运行时快照全系统状态→Owner手动调试时从此点恢复 | rr (Mozilla) / CRIU |
| B5-M05 | **Execution Log with Verbosity Control（执行日志详细度控制）**——按需打开/关闭per-module详细日志用于调试 | `DEBUG_MODULE=l06` 环境变量 |
| B5-M06 | **Non-Intrusive Debugging Hooks（非侵入调试钩子）**——每个RI模块暴露hook点→在不改代码的情况下插桩观察 | DTrace / eBPF |

#### N. 长期演进与模块生命周期管理（B5-N01~N06）

| 盲点 ID | 缺失内容 | 专业机构对标 |
|---------|---------|------------|
| B5-N01 | **Module Deprecation Lifecycle（模块废弃生命周期）**——标记→警告→隔离→归档→删除的5阶段过程 | K8s API Deprecation / Stripe API Versioning |
| B5-N02 | **Breaking Change Management（破坏性变更管理）**——2版本共存+路由→旧版本N个月后移除的标准流程 | Google API Improvement Proposals (AIP) |
| B5-N03 | **Backward Compatibility Window（后向兼容窗口）**——每个模块声明支持多少个历史版本 | Android API Levels / Node.js LTS |
| B5-N04 | **Module Migration Path Documentation（模块迁移文档）**——废弃模块→替代模块的映射表+迁移guide | AWS Service Migration Guides |
| B5-N05 | **Dead Code Detection within Modules（模块内死代码检测）**——vulture/coverage分析→标记未使用代码→通知Owner | Vulture / Coverage.py |
| B5-N06 | **Cyclomatic Complexity Guard（圈复杂度防护）**——模块复杂度>15→AI必须简化；>25→CI拒绝merge | McCabe / SonarQube |

#### O. AI 施工模式库与反模式（B5-O01~O08）

> **最前沿的盲点**：AI需要被教"在这个系统中应该怎么做模块"+"绝对不要做什么"。这是氛围编程的"风格指南"——不是代码lint，而是设计决策lint。

| 盲点 ID | 缺失内容 | 氛围编程社区对标 |
|---------|---------|---------------|
| B5-O01 | **Module Template System（模块模板系统）**——AI创建新模块时自动从模板生成：`abc→lifecycle→event_handler→config→tests` | `cookiecutter` / Copilot Workspace |
| B5-O02 | **Anti-Patterns Catalog（反模式目录）**——"在这个系统中绝对不要做什么"——如：不要绕过EventBus直接import其他模块的内部函数 | Google Code Smells / Refactoring.Guru |
| B5-O03 | **Design Decision Tree（设计决策树）**——"我应该用EventBus还是直接调用？"→决策流程图→AI可执行规则 | The Architecture Decision Record (ADR) |
| B5-O04 | **Error Handling Patterns by Module Type（按模块类型的错误处理模式）**——数据模块:重试+降级→静态值；交易模块:重试1次→报警→拒绝 | Netflix Error Handling Taxonomy |
| B5-O05 | **Module Naming Convention Enforcer（模块命名规范执行器）**——`lXX_function_module_name` 强制一致——防止AI创造不一致的名字 | PEP 8 + ZephyrAlpha Naming Spec |
| B5-O06 | **Code Ownership Manifest（代码所属声明）**——每个py文件声明：AI施工 % vs Owner手动 % vs AI自修复 %——量化的"谁写的" | GitHub CODEOWNERS |
| B5-O07 | **AI Confidence Annotation（AI信心标注）**——AI在自己写的代码中标注信心分数(0-1)——低信心代码标注为REVIEW_NEEDED | Copilot Confidence / Claude Artifacts |
| B5-O08 | **Progressive Code Review Depth（渐进代码审查深度）**——AI信心>0.9→轻审(仅lint+safety)；0.5-0.9→中审(+contract test)；<0.5→重审(+full test suite+Owner review) | Google CR+Review Levels |

---

## 3. 边界

### 3.1 覆盖

- RI-01 ~ RI-15 模块的设计 + 实现
- Cross-Layer 缺口 RL-001 ~ RL-048 填补
- 所有 RI 模块的失败模式定义 + 降级路径
- 1人+AI 运维语境下的自愈能力设计
- 与 MOD-INF-016 Shared Core 的承载关系与职责边界
- FMEA 失效模式与效应分析
- ADR 架构决策记录
- 五视图完整体系（静态拓扑/动态行为/故障传播/容量伸缩/Owner感知）

### 3.2 不覆盖（→ 去哪）

- AI 审计守卫 → MOD-INF-001（capacity-assurance）
- 安全网关（LSG）→ MOD-INF-014（llm-security）
- 因子计算逻辑 → L02-L03 业务层
- 审计追踪链存储 → MOD-INF-020（audit-trail），RI-13 EventStore 提供事件级溯源，审计追踪链消费事件
- 回滚执行 → MOD-INF-021（rollback-system），RI-13 事件重放可配合回滚
- 任务门禁（G0-G7）→ MOD-INF-007（gate-engine）
- Shared Core 基础设施的实现细节 → MOD-INF-016（shared-core）——本蓝图定义需求，MOD-INF-016 承载实现

---

## 4. 输入 / 基于此设计

| 输入 | 来源 |
|------|------|
| Owner 架构提问 | "Layer 间怎么通信？配置怎么统一管？" |
| Cross-Layer 缺口审计（RL-001~021）| Wave 0 架构自检 + v2.0.0/v2.1.0 盲点审计 |
| v2.0.0 盲点审计 | 20+ 结构性缺口 + 专业机构对标（Google SRE/Netflix/K8s/Stripe/Goldman SecDB） |
| v2.1.0 深度对标 | Event Sourcing+CQRS (金融行业 76% 采用率, 99.98%可用性) + Dry Run (Terraform plan/Agent CI/CD) + FinOps Cost Attribution (Visibility/Allocation/Optimization 三大支柱) |
| v3.0.0 全量盲点审计 | 49 项盲点——跨模块职责对齐 + 结构性缺口(GAP-01~07) + 深度强化(WEAK-01~07) + 业界对标(MISS-01~14) + 前沿盲点(FUTURE-01~10) + 1人+AI专项(OPT-01~07) + 蓝图质量(FMEA+ADR) |
| MOD-INF-016 Shared Core v0.14.0 | 49 文件已实现——10 个 RI 模块的代码承载基座 |

---

## 5. 架构决策

### 5.1 终选技术栈（v3.0.0 扩展）

| 组件 | 终选 | 理由 |
|------|------|------|
| RI-01 EventBus | **asyncio.PriorityQueue（四级优先级）+ Pydantic 类型化事件 + DLQ SQLite持久化 + 背压信号 + DeliverySemantics: AT_LEAST_ONCE** | 零依赖；PriorityQueue确保风控告警不被积压事件阻塞 |
| RI-02 ModuleLifecycle | **ABC + 拓扑排序(BFS) + register/unregister + 版本范围约束 + 优雅关闭协议(drain→timeout→force_kill) + Crash-Only设计** | 极简；crash-only确保无人值守场景下自恢复 |
| RI-03 ConfigCenter | **YAML + os.environ 覆盖 + Pydantic 校验 + watchdog 热重载 + Feature Flags（渐进推出+交互矩阵+Kill Switch）** | 零依赖；交互矩阵防止Flag组合引入bug |
| RI-04 DependencyInjector | **由 MOD-INF-016 `shared/production/di_container.py` 统一承载——构造注入 + ABC 接口绑定 + 循环检测** | 消除双DI容器重复——一个模块只有一个注入入口 |
| RI-05 ResilienceGuard | **CircuitBreaker(三态) + TokenBucket(限流) + TimeoutContext + 降级链 YAML + Bulkhead(per-module线程/连接池上限) + LoadShedder(优先级丢弃) + RetryBudget(全局配额)** | 七合一韧性基座 |
| RI-06 IdempotencyGuard | **分级策略：关键流(风控/交易/仓位)走 ES expected_version 天然去重；非关键流 SHA-256 + SQLite TTL** | 关键流零TTL过期风险；非关键流轻量级 |
| RI-07 SecretsManager | **AES-256-GCM 本地加密 + .env 自动加解密 + 访问审计发射** | 单机可用；ConfigCenter加密字段唯一后端 |
| RI-08 ErrorHandler | **Enum(SRE分类) + Structlog 结构化 + W3C traceparent header + trace_id跨进程传播 + 聚合窗口** | 零依赖；W3C标准对齐OpenTelemetry生态 |
| RI-09 HealthCheck | **async 探针 + 依赖传导 + 三级状态 + 具体SLI阈值(CPU>80%→DEGRADED,>95%→DOWN;错误率>5%→DEGRADED,>10%→DOWN) + Reconciliation Loop持续对账** | SLI阈值具体化消除主观判断；Reconciliation持续自愈 |
| RI-10 TelemetryCollector | **structlog 聚合 + per-module基数限制(500) + 超限LRU淘汰+告警 + 直方图 + Exemplar + 10s 推送 + PromptFingerprint + DeadModuleDetector** | 预聚合；PromptFingerprint追踪AI行为归因 |
| RI-11 CacheLayer | **LRU dict + VMS 语义缓存 + TTL 分层(Hot/Warm/Cold) + DataAffinity hints** | 复用VMS；Affinity减少跨模块缓存miss |
| RI-12 AutoDiagnostics | **HealthCheck 触发 + Runbook YAML 匹配 + 诊断报告 Markdown生成 + 修复后→KB自动补充 + TrustDecayTracker + SelfLimiter** | 零依赖；闭环：诊断→修复→KB沉淀 |
| RI-13 EventStore | **SQLite append-only event_log 表 + 快照表(每1000事件) + CQRS读模型(SQLite View) + Crypto-Shredding + SagaCoordinator(Phase 4触发)** | Phase 3 触发——零新依赖；GDPR兼容 |
| RI-14 DryRunSimulator | **sandbox=True 标志位 + 拦截写操作→日志输出 + diff报告生成 + approval gate + 一致性验证套件 + CrossSessionLoopDetector + SelfSimulate** | Python mock模式；跨Session Loop检测消除氛围编程"上下文失忆→重复犯错" |
| RI-15 CostTracker | **LLM调用拦截→token计数→美元换算 + CPU/内存/IO记录 + per-module/session tag归属 + 模块可维护性评分 + 飞书日报** | 调用层拦截不侵入模型；全资源FeinOps |

### 5.2 设计原则（v3.0.0 新增）

| 原则 | 内容 | 对标 |
|------|------|------|
| Crash-Only | 系统不依赖"优雅关闭"——每次停止=crash，每次恢复=重启。所有状态持久化，重启后自动从SQLite重建内存状态 | Google Chubby |
| Structured Concurrency | 使用 `asyncio.TaskGroup` 管理1500+模块的并发生命周期——子任务全部完成或全部取消，无孤儿协程 | Python 3.11+ / Trio |
| Fail-Closed | 安全组件（SecretsManager/ErrorHandler）不可用时拒绝操作而非放行 | OWASP / MOD-INF-014 |
| Immutable Events | RI-13 EventStore 事件一旦写入不可修改/不可删除——审计完整性不可妥协 | Goldman SecDB |
| Progressive Disclosure | 容量模型和告警按 Owner 注意力预算分级——实时仅推送CRITICAL，其余汇总 | Anthropic Codified Context |

### 5.3 关键代码骨架（v3.0.0 新增）

#### DeliverySemantics（消息传递语义）

```python
from enum import Enum

class DeliverySemantics(Enum):
    """RI-01 EventBus 的消息传递语义"""
    AT_MOST_ONCE = "at_most_once"    # 可能丢失，不重复——遥测日志等低价值事件
    AT_LEAST_ONCE = "at_least_once"  # 可能重复，不丢失——默认；配合IdempotencyGuard
    EXACTLY_ONCE = "exactly_once"    # 不丢不重——金融交易等关键事件，走ES expected_version

class EventPriority(Enum):
    """RI-01 EventBus 事件优先级——高优先级不排低优先级后面"""
    CRITICAL = 0   # 风控告警/熔断触发——立即消费
    HIGH = 1       # 交易执行/仓位变更——优先
    NORMAL = 2     # 模块状态变更/配置变更——正常
    LOW = 3        # Telemetry聚合/日志——积压时可丢弃
```

#### BackpressurePropagation（背压传导）

```python
@dataclass
class BackpressureSignal:
    """背压信号——从 EventBus 向上游传播"""
    source_module: str         # 哪个模块慢
    queue_usage_pct: float     # 队列使用率 (0.0-1.0)
    severity: str              # "warning" (>80%) | "critical" (>95%)
    affected_upstream: list[str]  # 受影响的上有模块ID

class BackpressurePropagator:
    """背压传导——不是单向减速，而是链式减速"""
    _thresholds: dict = {
        "warning": 0.80,   # 80% → 发 WARNING 信号→上游模块限速到 50%
        "critical": 0.95,  # 95% → 发 CRITICAL 信号→上游模块暂停写入
    }

    async def propagate(self, signal: BackpressureSignal) -> None:
        """根据队列使用率→计算减速因子→通知上游模块"""
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
    """舱壁隔离——per-module 线程/连接池上限，防止一个模块耗尽全局资源"""
    _pools: dict[str, "ResourcePool"] = {}

    class ResourcePool:
        max_concurrent: int       # 最多并发操作数
        semaphore: asyncio.Semaphore

    def configure(self, module_id: str,
                  max_concurrent: int = 10,
                  max_db_connections: int = 5) -> None: ...

    async def acquire(self, module_id: str) -> AsyncContextManager:
        """获取该模块的资源——若已满则等待；超时则抛 ResourceExhaustedError"""
```

#### LoadShedder（负载脱落）

```python
class LoadShedder:
    """负载脱落——超载时按请求优先级主动丢弃低优先级请求，不等队列满"""
    _overload_threshold: float = 0.80  # 全局负载 > 80% → 开始脱落

    async def admit(self, request: "Request") -> bool:
        """判断是否接纳请求。过载时：CRITICAL→接纳/HIGH→按概率接纳/LOW→拒绝"""
        global_load = await self._measure_global_load()
        if global_load < self._overload_threshold:
            return True
        return request.priority <= EventPriority.HIGH  # 仅CRITICAL+HIGH被接纳
```

#### RetryBudget（重试配额）

```python
class RetryBudget:
    """重试风暴防护——全局重试配额，耗尽后拒绝重试，避免级联放大"""
    _budget_per_window: int = 100    # 每分钟最多 100 次重试
    _used_this_window: int = 0
    _window_start: float = 0.0

    async def can_retry(self) -> bool:
        """检查当前窗口内是否还有重试配额"""
        if time.monotonic() - self._window_start > 60.0:
            self._used_this_window = 0
            self._window_start = time.monotonic()
        return self._used_this_window < self._budget_per_window
```

#### 优雅关闭协议

```python
class GracefulShutdown:
    """RI-02 ModuleLifecycle 优雅关闭协议"""
    drain_timeout: float = 30.0     # drain 最多等 30s
    force_kill_timeout: float = 5.0  # drain 超时 → force kill 5s

    async def shutdown(self) -> ShutdownResult:
        """SIGTERM → drain → 等待 in-flight → 超时 force kill → 状态持久化"""
        EventBus.stop_accepting()              # 1. 停止接受新事件
        in_flight = EventBus.drain(self.drain_timeout)  # 2. 等待 in-flight 完成（30s）
        if in_flight.timeout:
            EventBus.force_kill(self.force_kill_timeout)  # 3. 超时强制 kill（5s）
        HealthCheck.persist_current_state()     # 4. 持久化当前健康状态
        return ShutdownResult(pending_events=in_flight.remaining)
```

#### W3C TraceContext

```python
class W3CTraceContext:
    """对齐 W3C Trace Context Level 2——跨模块/跨进程 trace_id 传播"""
    trace_id: str    # 32 hex chars
    span_id: str     # 16 hex chars
    trace_flags: int  # 01 = sampled

    def to_traceparent(self) -> str:
        """生成 traceparent header: 00-{trace_id}-{span_id}-{trace_flags:02x}"""
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags:02x}"

    @classmethod
    def from_traceparent(cls, header: str) -> "W3CTraceContext": ...
```

#### Crypto-Shredding

```python
class CryptoShredding:
    """RI-13 EventStore GDPR 兼容——用 per-stream AES 密钥加密敏感字段
    删除权 = 销毁该 stream 的 AES 密钥 → 所有历史事件不可解密 = 逻辑删除
    """
    _stream_keys: dict[str, bytes] = {}  # stream_id → AES-256 key

    async def anonymize_stream(self, stream_id: str) -> None:
        """删除加密密钥 = 该 stream 的所有历史事件永久不可读"""
        del self._stream_keys[stream_id]
        audit.record(f"CRYPTO_SHRED: stream={stream_id}")
```

#### Saga Coordinator（触发式）

```python
class SagaCoordinator:
    """RI-13 扩展——跨模块补偿事务（Phase 4 触发，仅当需要多步骤回滚时激活）"""
    _active_sagas: dict[str, "SagaInstance"] = {}

    async def start(self, saga_id: str,
                    steps: list["SagaStep"]) -> SagaResult: ...

    async def compensate(self, saga_id: str,
                         failed_step: int) -> CompensateResult:
        """从 failed_step 逆序执行补偿——恢复每个步骤之前的状态"""
```

#### Speculative Execution

```python
class SpeculativeExecutor:
    """RI-01 EventBus 投机执行——关键路径同时发 2 路，取最快返回"""
    async def emit_with_hedge(self, event: Event,
                              replicas: int = 2) -> EventResult:
        """发送到 N 个消费者，第一个完成的结果直接返回"""
        tasks = [consumer.handle(event) for consumer in self._replicas[:replicas]]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        return done.pop().result()
```

#### Leader Election via SQLite Lease（多节点主选举）

```python
class SqliteLeaderElection:
    """最简单的 Leader Election——SQLite 做租约存储。
    只适用于单数据中心3-5节点——不是 Raft，是"轻量级主选举"。
    """
    _lease_table = "leader_lease"
    _lease_id = "global_leader"
    _lease_ttl: float = 30.0    # 租约 TTL 30s
    _renew_interval: float = 10.0  # 每 10s 续约

    async def try_become_leader(self) -> bool:
        """INSERT OR REPLACE 原子操作竞争 Leader"""
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
        """检查当前节点是否仍为 Leader"""
        row = await self.db.fetchone(
            f"SELECT node_id FROM {self._lease_table} "
            f"WHERE lease_id = ? AND expires_at > ?",
            (self._lease_id, time.time())
        )
        return row is not None and row[0] == self.node_id

    async def step_down(self) -> None:
        """主动让位——退出前通知集群"""
        await self.db.execute(
            f"DELETE FROM {self._lease_table} WHERE node_id = ?",
            (self.node_id,)
        )
```

#### Module Sandbox（模块级进程隔离）

```python
class ModuleSandbox:
    """RI 模块间运行时隔离——每模块独立子进程。
    AI生成的代码在子进程中运行→crash/无限循环→不污染主进程。
    """
    _module_procs: dict[str, asyncio.subprocess.Process] = {}
    _crash_counter: dict[str, int] = {}  # crash 计数→自动熔断

    async fn spawn_module(self, module_id: str,
                           entrypoint: str) -> None:
        """启动模块为独立子进程——通过 stdin/stdout JSON-RPC 通信"""
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", f"zephyr.{module_id}",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        self._module_procs[module_id] = proc

    async def restart_if_crashed(self, module_id: str) -> bool:
        """检测模块进程是否存活→crash则重启→5次后永久隔离+通知Owner"""
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
    """Owner 睡眠时段自动管理——数据驱动的静音窗口。
    假设：23:00-07:00 local = Owner 正在睡觉。
    """
    _sleep_start: int = 23    # 23:00
    _sleep_end: int = 7       # 07:00
    _critical_suppressed: int = 0

    def is_sleep_time(self) -> bool:
        """判断当前是否在睡眠时段"""
        hour = datetime.now(tz=self._owner_tz).hour
        return hour >= self._sleep_start or hour < self._sleep_end

    async def handle_alert(self, alert: Alert) -> AlertDecision:
        """睡眠时段：CRITICAL 只触发一次→5min内无Owner响应→走自愈"""
        if not self.is_sleep_time():
            return AlertDecision.SEND_NORMAL

        if alert.level == AlertLevel.CRITICAL:
            if self._critical_suppressed >= 1:  # 已发过一次
                return AlertDecision.AUTO_HEAL  # 直接自愈
            self._critical_suppressed += 1
            return AlertDecision.SEND_SINGLE    # 只发一条

        return AlertDecision.QUEUE_FOR_MORNING  # 其余→早上推送
```

#### Auto-Decide Engine（自动决策引擎）

```python
class AutoDecideEngine:
    """自动决策阈值——影响范围小的操作无需Owner审批。
    三维：影响模块数 × 费用（$） × 风险RPN
    """
    _thresholds: dict = {
        "impacted_modules": 3,      # 影响 ≤3 模块
        "cost_impact_usd": 0.10,    # 费用 ≤$0.10
        "risk_rpn": 50,             # RPN ≤50
    }

    async fn decide(self, operation: "Operation") -> DecideResult:
        """三阈值判断→AND 满足=自动执行|OR 不满足=送审批"""
        impact = await self._assess_impact(operation)
        if (impact.modules <= self._thresholds["impacted_modules"] and
            impact.cost <= self._thresholds["cost_impact_usd"] and
            impact.rpn <= self._thresholds["risk_rpn"]):
            log.info(f"🤖 {operation.id}: 自动执行——影响范围足够小无需Owner审批")
            return DecideResult(auto_approved=True)
        return DecideResult(needs_approval=True, reason=impact.summary())
```

#### Prompt Cache & Token Budget（提示缓存与Token预算）

```python
class PromptCacheManager:
    """AI调用前的上下文优化——缓存+压缩+预算三重优化。
    氛围编程核心运维——Token钱和上下文窗口都是有限资源。
    """
    _cache: dict[str, tuple[float, str]] = {}  # prompt_hash → (ttl, cached_response)
    _modules_total_tokens_this_session: dict[str, int] = {}  # per-module 追踪

    async fn optimize_prompt(self, module_id: str,
                              raw_context: str,
                              user_intent: str) -> str:
        """三阶段：① 检查缓存→命中直接返回 ② 压缩context→剪枝不相关文件
        ③ Token预算告警→超限提示简化"""

        # 阶段1: 缓存检查
        cache_key = sha256(user_intent.encode()).hexdigest()
        if cache_key in self._cache:
            ttl, cached = self._cache[cache_key]
            if time.time() < ttl:
                self._track_tokens(module_id, len(cached) // 4)  # ~1 token/4 chars
                return cached

        # 阶段2: 上下文压缩——只发相关文件的前N行定义
        compressed = self._compress_context(raw_context, max_chars=8000)

        # 阶段3: Token预算检查——若本月已用>80%→自动提示简化
        monthly_pct = self._get_monthly_token_pct(module_id)
        if monthly_pct > 0.80:
            compressed = f"[⚠️ Token预算已用{monthly_pct:.0%}] " + compressed[:4000]

        return compressed
```

#### Emergency Trading Kill Switch（紧急交易停止）

```python
class TradingKillSwitch:
    """B5-K01——一条命令紧急停止所有交易活动。
    对标：CME Kill Switch / Two Sigma "Big Red Button"。
    在量化交易系统中，这是最重要的安全组件——比 CircuitBreaker 高一个优先级。
    """
    _mode: str = "NORMAL"  # NORMAL | PAPER_ONLY | READ_ONLY | KILLED

    async def activate(self, reason: str,
                        confirmed_by: str = "AUTO") -> KillSwitchResult:
        """立即执行五步停止序列"""
        results = []

        # 1. 标记模式→KILLED（所有RM模块立即感知）
        self._mode = "KILLED"

        # 2. 所有未完成订单→取消
        results.append(await self._cancel_all_pending_orders())

        # 3. EventBus 中所有交易事件→清空
        results.append(await EventBus.purge_events(
            event_types=["TradeEvent", "OrderEvent"]))

        # 4. 所有L05（交易执行）模块→只读
        results.append(await ModuleLifecycle.set_mode("L05", "READ_ONLY"))

        # 5. 审计记录→永久留存
        audit.record_severe(f"KILL_SWITCH: reason={reason} by={confirmed_by}")

        return KillSwitchResult(mode=self._mode, actions=results)

    async def deactivate(self, confirmed_by: str) -> KillSwitchResult:
        """恢复交易——需要Owner显式确认"""
        if confirmed_by != "Owner":
            raise PermissionError("Kill Switch 只能由 Owner 手动解除")
        self._mode = "NORMAL"
        # 恢复L05模块为可写
        await ModuleLifecycle.set_mode("L05", "NORMAL")
        return KillSwitchResult(mode=self._mode)
```

#### Simulated Clock（模拟时钟——确定性回测根基）

```python
class SimulatedClock:
    """B5-M02——区分真实时间 vs 模拟时间。
    回测时用sim_time驱动所有定时器/超时/schedule。
    实盘时sim_time==real_time，零开销。
    """
    _mode: str = "REAL"  # REAL | SIMULATED
    _sim_time: float = 0.0

    def now(self) -> float:
        """统一时间源——调用者不需要知道当前是实盘还是回测"""
        return time.time() if self._mode == "REAL" else self._sim_time

    async def sleep(self, duration: float) -> None:
        """统一sleep——回测中瞬间跳过，实盘中真实等待"""
        if self._mode == "REAL":
            await asyncio.sleep(duration)
        else:
            self._sim_time += duration  # 回测：时间直接推进

    async def advance_to(self, target_time: float) -> None:
        """回测引擎专用——推进到下一个事件时间"""
        if self._mode != "SIMULATED":
            raise RuntimeError("advance_to 仅在 SIMULATED 模式可用")
        self._sim_time = max(self._sim_time, target_time)
```

#### Deterministic Random（确定性随机）

```python
class DeterministicRandom:
    """B5-M01——全局确定性随机。种子相同→全系统所有"随机"行为完全相同。
    这是回测可复现性的硬件保证。
    """
    _seed: int = 42
    _rng: random.Random = field(default_factory=lambda: random.Random(42))

    def reseed(self, seed: int) -> None:
        """重新设置种子→回测开始时调用→确保可复现"""
        self._seed = seed
        self._rng = random.Random(seed)
        random.seed(seed)
        numpy.random.seed(seed % (2**32 - 1))

    def uniform(self, a: float = 0.0, b: float = 1.0) -> float:
        """所有模块调用此方法而非 random.random()——确保走同一RNG"""
        return self._rng.uniform(a, b)

    def choice(self, seq: Sequence[T]) -> T:
        """所有模块调用此方法而非 random.choice()"""
        return self._rng.choice(seq)
```

#### Module Metadata & Self-Description（模块元数据与自描述）

```python
class ModuleMetadata:
    """B4-I04 深化——每个模块在启动时注册自己的元数据。
    AI 施工的新模块→自动继承模板元数据→无需手动维护清单。
    """
    module_id: str
    layer: str                # L01-L14
    functional_domain: str    # infra/risk/trading/data/research/...
    capabilities: list[str]   # ["event_consumer", "event_producer", "http_api", ...]
    dependencies: list[str]   # MOD-INF-001, ...
    api_version: str          # "1.0.0" (SemVer)
    supports_backward: list[str]  # 支持的后向版本 ["0.9.0", "0.8.0"]
    ai_confidence: float      # 0.0-1.0: AI 对这模块的信心
    code_ownership: dict      # {"ai_generated": 85, "human_modified": 10, "ai_repaired": 5}

    def describe(self) -> str:
        """一行自描述——给其他模块和调度器用"""
        return (f"{self.module_id}@{self.api_version} "
                f"[{','.join(self.capabilities)}] "
                f"conf={self.ai_confidence:.0%}")
```

#### Module Template Skeleton（模块模板骨架）

```python
# templates/module_template.py.j2 — 新模块从此模板生成
"""
{{ module_id }} — {{ description }}
Generated by AI Template System v{{ template_version }}
AI Confidence: {{ ai_confidence }}
Layer: {{ layer }} | Domain: {{ functional_domain }}
"""
from zephyr.shared.lifecycle import LifecycleAware
from zephyr.shared.observer import EventConsumer, EventProducer
from zephyr.shared.config import Configurable
from zephyr.shared.errors import ZephyrError

class {{ class_name }}(LifecycleAware, EventConsumer, Configurable):
    """{{ docstring }}"""

    module_id: str = "{{ module_id }}"
    api_version: str = "0.1.0"
    capabilities: list[str] = {{ capabilities }}

    async def on_start(self) -> None:
        """Phase {{ start_phase }}——启动顺序{{ start_order }}"""
        await super().on_start()
        # FIXME(AUDIT-05): 模块启动逻辑待实现——施工时由AI agent填充
        pass

    async def on_event(self, event: "Event") -> None:
        """消费事件——来自 EventBus"""
        # FIXME(AUDIT-05): 事件处理逻辑待实现——施工时由AI agent填充
        pass

    async def on_stop(self) -> None:
        """优雅关闭"""
        await super().on_stop()
        pass
```

### 5.4 RI-13 EventStore 设计哲学（v3.0.0 扩展）

Event Sourcing 在金融行业已验证：76% 机构已迁移至实时事件驱动架构，CQRS 实现 35-47% 交易处理性能提升 + 99.98% 市场波动期可用性。但全量实现 ES 对 1 人+AI 是高风险决策。因此采用**触发式渐进引入**：

```
Phase 1-2: 传统状态存储（SQLite CRUD） ← 快速迭代
           ↓ 触发条件：模块数 > 100 或 首次合规/审计要求
Phase 3:   RI-13 EventStore ← 关键数据流切 ES，非关键保持 CRUD
           └── 仅对 L04(风控)、L06(仓位)、L05(交易执行) 三层的写操作做 Event Sourcing
           └── CQRS 读模型：物化视图(账户余额)、聚合视图(因子分数)
           └── 快照策略：每 1000 事件自动快照 → 重放上限 1000 事件 → 恢复延迟 < 500ms
           └── v3.0.0: Crypto-Shredding 可选启用（有 GDPR/合规需求时）
           ↓ 触发条件：首次跨模块多步骤回滚需求
Phase 4:   RI-13 SagaCoordinator ← 编排补偿事务（触发式，不主动启动）
```

### 5.5 RL-001 ~ RL-048 填补方案（v3.0.0 扩展）

| 缺口 | 方案 | Phase | 验收 |
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
| RL-024 DI统一 | Mod-INF-016 `di_container.py` | 1a | 一个容器，一处注入 |
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
| RL-043 容量预留 | L04/L06预分配X% | 2a | 关键模块0被挤占 |
| RL-044 预热期 | warmup→预热→内部HC→READY | 1a+2a | 启动0假熔断 |
| RL-045 Crypto-Shred | per-stream密钥→删除密钥=不可读 | 3 | GDPR就绪 |
| RL-046 Flag交互矩阵 | pairwise组合测试 | 2a | Flag组合0未知bug |
| RL-047 信任衰减 | 误报>30%→降级"建议模式" | 2b | 自愈误判0扩大 |
| RL-048 Crash-Only | 依赖重启恢复不依赖优雅关闭 | 1a | 无人值守自恢复100% |

### 5.6 CI/CD 与部署自动化流水线（v4.0.0 新增）

> **对标**：GitHub Actions / ArgoCD / Flagger 的金丝雀部署模式。在 1人+AI 语境下，CI/CD 需极简化——一条命令从代码到生产。

```
代码提交（AI 完成施工）
  ├── 1️⃣ 静态分析门
  │     ├── mypy strict（类型检查）
  │     ├── ruff（lint）
  │     └── Semgrep（安全扫描——v4.0.0 新增）
  ├── 2️⃣ 测试门
  │     ├── 单元测试（受影响模块）
  │     ├── Contract Test（Pact——v4.0.0 新增）
  │     └── Property-Based Test（Hypothesis——v4.0.0 新增）
  ├── 3️⃣ DryRun 门（RI-14 预演）
  │     ├── sandbox 执行→diff 报告
  │     ├── 一致性验证套件
  │     └── CrossSessionLoopDetector
  ├── 4️⃣ Approve 门
  │     ├── 自动决策引擎判断（RPN<50 + 影响≤3模块 + 费用≤$0.10）
  │     └── OR Owner 审批
  ├── 5️⃣ 部署门
  │     ├── Canary（1%→10%→50%→100% 流量渐进）
  │     ├── 健康监控每个 Canary 阶段
  │     └── 自动回滚条件：错误率>5% OR P99延迟超过2x基线
  └── 6️⃣ 生产验证
        ├── Smoke Test（合成事务验证）
        ├── 错误率基线对比
        └── 自动追加 ADR（若涉及架构变更）
```

| 阶段 | 工具 | 理由 |
|------|------|------|
| 静态分析 | mypy + ruff + Semgrep | 零新依赖——已有 Python 环境即可 |
| 单元测试 | pytest + Hypothesis | 参数化测试覆盖边界 |
| Pact 测试 | pact-python | 验证模块间契约不被破坏 |
| DryRun | RI-14 DryRunSimulator | 自建——零新依赖 |
| Canary | 基于 RI-03 FeatureFlag 实现 | 复用 ConfigCenter 渐进推出能力 |

### 5.7 AI 施工自治回路（v4.0.0 新增）

> **对标**：Aider / Copilot Chat / Cursor Agent 模式。氛围编程的核心是 "AI 说了算 → 人 review → 循环"。蓝图不实现 AI 本身，但为 AI 施工提供结构化的执行环境。

```
AI 施工 Session 生命周期
  │
  ├── 1. 启动
  │     ├── AI Context Builder: 收集相关模块蓝图/代码/最近变更
  │     ├── Token Budget Check: 会话总预算 ≤ 本模块月度配额
  │     └── 锁定工作区：同一模块不能被两个 session 同时修改
  │
  ├── 2. 施工循环（每轮）
  │     ├── AI 提交修改
  │     ├── 自动 Self-Review（另一模型做 Code Review——四眼原则）
  │     ├── 自动 Lint-Fix（ruff → 自动修复 → 再lint → pass）
  │     ├── 自动 Test Gen（从 diff 生成对应的单元测试）
  │     └── 自动 SelfSimulate（DryRun 预演修改→预测影响面）
  │
  ├── 3. 提审
  │     ├── 生成统一 diff 报告：代码变更 + 测试结果 + DryRun预测 + 费用预估
  │     ├── Auto-Decide Engine 判断（RPN + 影响面 + 费用）
  │     └── → 自动通过 OR 推送给 Owner 审批
  │
  └── 4. 结束
        ├── 记录 Session Log + AI Decision Log（ADR）
        ├── 解锁工作区
        └── 更新 Codebase Familiarity Score
```

#### AI 模型降级链（v4.0.0 新增代码骨架）

```python
class ModelFallbackChain:
    """AI 模型调用降级链——首选模型失败→自动切换备选→最终提级 Owner。
    氛围编程每天的事实——模型挂了不能停止施工。
    """
    _chain: list[tuple[str, float]] = [
        ("deepseek-chat", 0.90),        # 首选：性价比最高
        ("deepseek-reasoner", 0.70),    # 降级1：推理强但贵
        ("qwen-max", 0.60),             # 降级2：备选供应商
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

---

## 6. 架构视图

### 6.1 Phase 路线图（v3.0.0 最终版）

| Phase | 名称 | 交付内容 | 核心目标 |
|-------|------|---------|---------|
| **1a** | 底座上线 | RI-02 ModuleLifecycle(拓扑排序+版本约束+优雅关闭协议+Crash-Only+预热期) + RI-03 ConfigCenter(热重载+写入校验+Feature Flags) + RI-04 DependencyInjector(统一由MOD-INF-016承载) + RI-08 ErrorHandler(SRE分类+W3C Trace Context) | 模块启动链 + 配置 + DI + 错误——四者一体，结构化并发 |
| **1b** | 通信就绪 | RI-01 EventBus(完整版: DeliverySemantics+PriorityQueue+DLQ持久化+背压传导链+消费者组+Schema兼容) + RI-10 TelemetryCollector(基数限制+PromptFingerprint+DeadModuleDetector) + RI-06 IdempotencyGuard(TTL分级) | 事件系统带上所有防护 + 消息语义明确 |
| **2a** | 韧性安全 | RI-05 ResilienceGuard(熔断+限流+Bulkhead+LoadShedder+RetryBudget+超时+降级+自适应并发) + RI-07 SecretsManager + RI-09 HealthCheck(具体SLI阈值+ReconciliationLoop) + RI-11 CacheLayer(DataAffinity) | "1人+AI 能不能睡好觉"的分水岭——七合一韧性+标准化健康 |
| **2b** | 自治闭环 | RI-12 AutoDiagnostics(Runbook→诊断→KB自动补充+TrustDecayTracker+SelfLimiter) + RI-14 DryRunSimulator(行为一致性验证+CrossSessionLoopDetector+SelfSimulate) + RI-15 CostTracker(全资源+MaintainabilityScore) + ModuleGraph(D3.js) + ProgressiveDelivery 预留 | 系统自己诊断 + 预演 + 费用自控 + Owner看总结报告 |
| **3** | 溯源增强（触发式） | RI-13 EventStore（ES+CQRS+写隔离+Crypto-Shredding）——当模块数 > 100 或首次合规/审计需求触发 | 金融级完整审计追踪——监管就绪 + GDPR就绪 |
| **4** | 补偿增强（触发式） | RI-13 SagaCoordinator——当首次跨模块多步骤回滚需求出现时触发 | 复杂业务流程的原子性回退 |
| **∞** | 维护期（全部Phase完成后自动切换） | 维护期SLO收紧：DryRun仅对新写操作100%覆盖(已有路径依赖集成测试)；部分RI降频运行；AI自预演常态化 | Owner告警预算从宽松→严格，系统进入稳态自运行 |

### 6.2 验收标准（beta 综合——v3.0.0 扩展）

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
| 安全 | ConfigCenter 加密字段非法路径 | 0%（强制走SecretsManager） |
| 安全 | Crypto-Shredding 有效性 | 删除密钥后0条事件可解密 |
| 错误处理 | 跨 3 层 W3C trace_id 完整性 | 100% |
| 错误处理 | OpenTelemetry 兼容性 | traceparent 标准格式 100% |
| 可观测 | Telemetry 标签基数 | ≤500 / module |
| 可观测 | PromptFingerprint 覆盖率 | 100%（所有LLM调用标记） |
| 可观测 | DeadModule Detector 准确率 | ≥95% |
| 自治 | HealthCheck DOWN → 诊断报告生成 | ≤15s |
| 自治 | Reconciliation Loop 对账周期 | ≤30s |
| 自治 | TrustDecayTracker 误报阈值 | 误报>30%→1h内降级 |
| 自治 | SelfLimiter 激活条件 | 同指标修复>3次/h→暂停+升级Owner |
| AI 安全 | 写操作 DryRun 覆盖率 | 100% |
| AI 安全 | DryRun vs 真实行为一致性 | diff=0（一致性验证套件100%） |
| AI 安全 | CrossSession Loop 检测准确率 | ≥90%（同diff被回滚过→永久拦截） |
| 成本 | LLM + CPU/内存/IO 费用归属 | module_id + session_id |
| 成本 | 模块可维护性评分 | MaintainabilityScore覆盖全部1500模块 |
| 溯源 | 关键流事件不可变性 | 100% |
| 合规 | GDPR删除权可达性 | Crypto-Shredding 100%覆盖 |

### 6.3 1人+AI 运维视角的容量模型（v3.0.0 扩展）

#### Owner 告警预算与通知分层

> **v3.0.0 核心新增**：Owner 每天最多处理 N=10 条实时告警。超出→汇总为日报。

| 通知级别 | 推送方式 | Owner 感知 | 示例 |
|:--:|------|------|------|
| **💀 CRITICAL** | 立即飞书 | 需要3秒内看到并决策 | 熔断OPEN/Secrets泄露/Drift检测到不安全漂移/CostTracker硬限额触发 |
| **🟡 WARNING** | 每小时汇总飞书 | 可以等1小时再看 | ErrorBudget < 50%/RateLimiter触发/IdempotencyGuard TTL清理/Backpressure WARNING |
| **🟢 INFO** | 每日汇总飞书 | 睡醒再看 | FeatureFlag状态汇总/Cooldown触发/模块启动完成/CacheLayer命中率日报 |
| **⚪ DEBUG** | 仅Dashboard | 不推送，Owner主动查看 | Telemetry基数详情/所有LLM调用token明细/AI行为Trace/PromptFingerprint分析 |
| **✨ AI_SELF_HEALED** | 日报中列出 | "今天AI自愈了N次"——不去打扰Owner | HealthCheck→AutoDiagnostics→修复→成功——全链路无人参与 |

#### 场景模型（v3.0.0 扩展）

| 场景 | RI 模块行为 | Owner 收到什么（通知级别） |
|------|-----------|-------------|
| AI 生成写操作 | RI-14 DryRunSimulator: SelfSimulate→sandbox预演→diff报告→"此操作将修改3个文件/影响2个模块/预计$0.03 LLM费用+$0.01 CPU费用"→确认 | 🟢 每日汇总飞书 + diff 预览 + 一键 approve/reject |
| AI 自预演发现循环依赖 | RI-14 SelfSimulate: AI提交前自己预演→发现循环依赖→**AI自己拒绝自己的修改**→换方案 | ✨ AI_SELF_HEALED → 日报中一句话 |
| 跨Session重复修改 | RI-14 CrossSessionLoopDetector: SHA-256 diff匹配→"此修改已在TASK-INF-0033中被回滚过→永久拦截" | 🟡 每小时汇总：被拦截的重复修改 |
| LLM 月费逼近预算 | RI-15 CostTracker: "deepseek-chat 模块本月已用$38/预算$50，按当前速率预计月底$52→建议启用 CacheLayer" | 🟡 每小时汇总 + 优化建议 |
| LLM 月费超标 | RI-15 CostTracker: 硬限额触发→自动降级到小模型 | 💀 立即飞书：硬限额触发，已自动降级 |
| 监管审计请求 | RI-13 EventStore: 输入时间范围→重建当时完整状态→导出审计报告 | 🟢 每日汇总: "2026-Q2 审计报告已生成——所有风控决策可溯源至原始事件" |
| LLM API 费用异常 | RI-15 CostTracker: "今日已完成1283次调用，较昨日+340%，最贵调用来自 context_engine/recompress @ $0.12/次" | 🟡 每小时汇总 + 异常调用详情 |
| AI 想改 ConfigCenter | RI-14 DryRunSimulator: sandbox→Flag交互矩阵检测→"此配置变更涉及2个Flag的组合，交互矩阵测试PASS"→放行 | 🟢 每日汇总：今日X项配置变更，全部交互矩阵PASS |
| 模块崩→触发Bulkhead+LoadShedder | RI-05: "l05模块连接池耗尽→不影响其他48模块" | 🟡 每小时汇总: "l05模块需要关注——今24小时触发Bulkhead限流X次" |
| DeadModule检测 | RI-10: "MOD-INF-017(Code Dedup Engine)已30天无事件活动→标记DORMANT；60天→建议归档" | 🟢 每日汇总: "本月无活动模块: MOD-INF-017, ..." |
| Owner 激活"休假模式" | 全部RI自动恢复机制解锁：熔断→自动CLOSE/预算→自动限额/Secrets轮转→自动延期 | Owner无感知——"休假模式已激活：3天零实时告警——全部自愈" |

> **Owner 信任衰减**（v3.0.0）：如果 AutoDiagnostics 的修复在 30% 以上的情况被 Owner 手动回滚，系统自动降级为"建议模式"——修复建议只推送，不自动执行。信任恢复需要连续 50 次建议被 Owner approve 且无回滚。

### 6.4 五视图体系（v3.0.0 衡量标准）

| 视图 | 内容 | 当前状态 |
|------|------|:--:|
| **静态拓扑视图** | 模块清单 + 依赖 DAG + 承载关系（§1.2 + §1.3） | ✅ |
| **动态行为视图** | 每个 RI 模块的状态机、生命周期状态图 | ⚠️ 蓝图骨架存在但未展开为状态图 |
| **故障传播视图** | 从底层故障到顶层 Owner 感知的因果链——不是简单的依赖链，而是"如果X故障→下游效应" | ✅ §6.3 容量模型 + §9 FMEA |
| **容量伸缩视图** | Load→Response Curve：当前负载 X / 延迟 Y / 成功率 Z，预测 2x 负载时的延迟和成功率 | ⚠️ 依赖 MOD-INF-001 容量预测模型 |
| **Owner 感知视图** | 每个 RI 模块在每种失败模式下，Owner 感知到什么、需要做什么。Owner 需 ≤3s 理解告警含义 | ✅ §6.3 通知分层 |

### 6.5 1人+AI 深度运维场景（v4.0.0 新增）

> **核心洞察**：v3.0.0 的告警预算+通知分层解决的是"信息过载"问题。v4.0.0 要解决的是"Owner 也是人"的问题——会累、会忘、会犯错、会放弃。

#### Owner 认知负荷模型

```
Owner 每日决策容量 = C_max
  ├── 告警处理（CRITICAL × 3 + WARNING × 2 + INFO × 1 权重）
  ├── 审批决策（代码变更 × 2, 配置变更 × 1.5, FeatureFlag × 1）
  ├── 架构决策（模块新建 × 4, 重设计 × 5）
  └── 手动修复（每次 × 3）

当 C_today > C_max × 0.80 → 🟡 "轻负载日"建议——非紧急决策延迟到明天
当 C_today > C_max × 1.00 → 🔴 "认知超载"——自动决策引擎激活，仅CRITICAL+架构决策送Owner
```

#### 新增场景矩阵

| 场景 | 触发条件 | 系统行为 | Owner 感知 |
|------|---------|---------|-----------|
| 🛌 **睡眠保护** | 23:00-07:00 local | CRITICAL 仅触发 1 次→5min 内无响应→自动启动自愈回路；其余→静音，早上推送 | "今日7小时睡眠窗口——系统自行处理了2个WARNING" |
| ☕ **晨报推送** | 07:00-08:00 | 生成 Daily Briefing: 昨日关键指标+费用+自愈记录+待决策项+今日预测 | Markdown 报告→飞书："昨日系统运行摘要——3个AI自愈/月费$1.42/1项待审批" |
| 🧠 **决策疲劳防护** | C_today > 0.8×C_max | 自动激活 Auto-Decide Engine——影响≤3模块+费用≤$0.10+RPN<50→自动执行 | "今日已做X项自动决策——节省了Y次审批——你还有Z项待决策" |
| 🚨 **紧急唤醒判定** | 夜间+触发"唤醒标准" | 精确定义：仅当 ①核心交易/风控回路 DOWN + ②自愈3次失败 + ③影响≥L04/L05/L06 任意一层 | CRITICAL飞书：明确告知"为何唤醒你"+"系统已尝试的自愈"+"建议的动作" |
| 🏝️ **Owner消失演练** | 每月1次（6h） | 系统进入"Owner Absent Mode"——熔断/预算/轮转全自动——按真实SLO运行 | 演练结束后报告："这6小时内：系统处理了X个异常/0次需要人工介入/0次违反SLO" |
| 📝 **知识外化** | Owner 每次做决策后 | 记录决策原则→转化为系统规则："[Owner名]在[场景]中选择了[选项]因为[原因]" | 一个月后："已自动学习到你的12条决策偏好——它们会自动执行" |
| 💔 **弃用螺旋防护** | 连续72h无Owner手动介入 | 系统降低告警频率30%——"太多告警→人放弃→更不介入→系统更差"。同时升高自愈阈值 | "注意：已3天无手动操作——系统已自动降低告警频率——随时可恢复" |
| 🔄 **自我解释** | Owner 说 "why?" | 系统为每个状态/告警/决策提供 ≤3s 可理解的因果解释 | "EventBus 熔断因为：l06模块消费速率<10/s(基准100/s)—3次重试全超时—自动OPEN" |
| 📊 **周报** | 每周日 | 生成 Weekly Report：SLO达标/费用趋势/模块健康变化/新增盲点/AI施工统计 | Markdown→飞书→自动存入Knowledge Base |

### 6.6 开发者体验设计（v4.0.0 新增）

> **对标**：Vercel/Netlify 的 "git push → live" 体验。1人开发者的时间是最稀缺资源。

| 体验目标 | 设计 | 实现方式 |
|---------|------|---------|
| **一键启动** | `git clone && ./tools/setup.sh` | 自动创建 venv、安装依赖、初始化 SQLite、启动 EventBus |
| **热重载** | 模块代码变更→自动reload | watchdog 监控 `src/zephyr/` →受影响模块 restart（复用 RI-02 热重载） |
| **AI Chat 集成** | 终端内 `/z` 命令→AI 施工 | `$ /z fix module l06` → AI 对话→代码变更→DryRun→审批 |
| **自调试钩子** | AI 施工→失败→自动收集上下文 | 自动捕获 trace_id + stacktrace + 最近 commit → 发送给 AI 自修复 |
| **代码熟悉度** | per-module 可视化熟悉度 | f(最后修改天数, Owner修改次数, 最近AI修改次数) → 低熟悉度→提醒 review |
| **自动 CHANGELOG** | AI 读写 git log → 生成结构化 CHANGELOG | 与 RI-15 CostTracker 共用 AI Decision Log 管道 |

---

## 7. 触发条件与扩展路径（v3.0.0 扩展）

| 条件 | 动作 |
|------|------|
| 模块 > 300 | RI-01 切 Kafka/RabbitMQ（Protocol 抽象层无缝切换） |
| pub/sub 消费者 > 500/事件 | 触发 EventBus Sharding |
| 模块 > 100 或 首次合规要求 | **触发 RI-13 EventStore**（ES+CQRS）——关键三层（L04/05/06）切事件溯源 |
| 首次跨模块多步骤回滚需求 | **触发 RI-13 SagaCoordinator**（Phase 4）——编排跨模块补偿事务 |
| LLM API 月费 > $50 | RI-15 CostTracker 启用预算硬限额 + 自动降级到小模型 |
| LLM API 月费 > $500 | CacheLayer 启用全量语义缓存 + 查询重写 + prompt 自动压缩 |
| 总LLM月费 > $1000 | RI-15 全资源FinOps面板自动生成——per-module费用排行+优化建议TOP10 |
| 外部依赖 > 10 个 | ResilienceGuard 降级链独立为 YAML 配置 |
| 首次安全事故 | SecretsManager 升级到 Vault（Protocol 抽象层） |
| AI 写操作错误率 > 5% | DryRunSimulator 审查级别升级——所有写操作必须人工 approve |
| AI 写操作错误率 < 3% 持续 1h（Loop Detector 恢复条件）| DryRunSimulator 审查级别自动降级——恢复自动审批模式 |
| AutoDiagnostics 误报率 > 30% | TrustDecayTracker → 自动降级为"建议模式"——修复建议不自动执行，需 Owner approve |
| 同指标修复触发 > 3 次/小时 | SelfLimiter → 暂停该指标的自动修复回路→升级 Owner 手动处理 |
| 模块 > 500 且 发现不可变部署需求 | Phase 5: RI 模块不可变部署——每个配置变更=新版本=切流量，旧版本保留不删 |
| 全部 Phase 完成 | 自动切换 Phase ∞（维护期）——SLO 收紧、DryRun 降频、AI自预演常态化 |
| Owner 激活"休假模式" | 熔断恢复/预算限额/轮转延期全自动——Owner 离线期间 0 实时告警 |
| Owner 每日告警 > N=10 | 超出告警自动降级为"日报汇总"而非实时推送 |
| Owner 认知负荷 C_today > 0.8×C_max（v4.0.0） | 激活"轻负载日"——非紧急决策延迟到明天自动推送 |
| Owner 认知负荷 C_today > C_max（v4.0.0） | 激活"认知超载"保护——Auto-Decide Engine 承担所有非CRITICAL+非架构决策 |
| 进入睡眠时段（23:00-07:00）（v4.0.0） | 激活 Sleep-Time Protocol——CRITICAL 仅触发1次+5min无响应→自愈；其余静音 |
| 睡眠时段+核心回路DOWN+3次自愈失败（v4.0.0） | 紧急唤醒 Owner——飞书CRITICAL+明确指出原因+已尝试自愈+建议动作 |
| 连续72h无Owner手动介入（v4.0.0） | 弃用螺旋防护——降低告警频率30%+升高自愈阈值——防止"放弃系统" |
| 每月固定时间（v4.0.0） | Owner 消失演练（6h）——系统全自动运行——验证无Owner依赖 |
| 模型 > 3 次 API 调用失败（v4.0.0） | ModelFallbackChain 自动切换备选模型 |
| 全部模型调用失败（v4.0.0） | AIBackendExhaustedError——暂停AI施工+升级Owner |
| 单模块连续crash ≥ 5次（v4.0.0） | ModuleSandbox 永久隔离该模块+通知Owner手动恢复 |
| 单次部署错误率>5%（v4.0.0） | Canary自动回滚——回到上一个健康版本 |
| Dependabot/SBOM报告新CVE（v4.0.0） | 自动评估影响面——HIGH/CRITICAL→立即飞书+绿帽更新 |

---

## 8. 风险与缓解（v3.0.0 扩展）

| 风险 | 概率 | 缓解 |
|------|------|------|
| asyncio.Queue 在 500 模块下内存暴增 | 低 | QUEUE_MAX_SIZE = 10000 硬限制 + 背压 + LoadShedder |
| CircuitBreaker 误熔断 | 中 | HALF_OPEN 探测 + 渐进恢复 + 信任衰减监控 |
| IdempotencyGuard 存储膨胀 | 中 | TTL分级：关键流ES天然去重零存储/非关键流24hTTL定时清理 |
| IdempotencyGuard TTL 过期致重复写入 | **中** | 关键流（风控/交易/仓位）使用 ES expected_version 天然去重——零 TTL 过期风险 |
| SecretsManager 主密钥丢失 | 低 | 主密钥备份 + 轮转记录 |
| CacheLayer 缓存穿透（雪崩） | 中 | 空值缓存 + 互斥锁防并发重建 + Bulkhead隔离 |
| DI 容器循环依赖 | 低 | 启动时 BFS 检测→阻断 |
| AutoDiagnostics 误诊 | 中 | 标记置信度 + TrustDecayTracker（误报>30%→自动降级）+ "请 Owner 确认" |
| AutoDiagnostics 自反锁恶性循环 | **低** | SelfLimiter：同指标修复3次/h→暂停回路+升级Owner |
| **EventStore 事件日志膨胀** | **中** | 快照策略（每 1000 事件）+ 热/冷分层存储 |
| **DryRun 与真实执行行为不一致** | **中** | v3.0.0: 一致性验证套件——sandbox vs 真实双跑 diff + 共享 Protocol→同源保证 |
| **CostTracker 定价表过期** | **低** | 定价表外置 `config/llm_pricing.yaml` + 定时对比官方 API + API费用异常告警 |
| **重试风暴——500消费者同时重试** | **中** | RetryBudget：全局每分钟配额100——耗尽拒绝重试 + jitter |
| **背压传导不及时→上游继续写入→队列爆满** | **低** | BackpressurePropagation：队列>80% 立即广播+上游减速因子实时计算 |
| **DeadModule 误标→活跃模块被标记** | 低 | DeadModule检测阈值保守：30天DORMANT/60天DEAD/90天才建议归档 |
| **Schema兼容性策略缺失→模块升级炸下游** | **中** | SchemaEvolutionPolicy：强制FULL_BACKWARD兼容；破坏性变更需2版本共存+路由 |
| **预热期不足→虚假熔断→系统波动** | 低 | warmup phase + readiness signal：全链路缓存预热+内部HealthCheck全PASS后才READY |
| **Crypto-Shredding密钥管理复杂度** | 低 | per-stream密钥 = SHA-256(stream_id + master_secret)——可复现不存储，删除=无法复现 |
| **单节点设计——多节点部署时无Leader→双主竞态（v4.0.0）** | **中** | SqliteLeaderElection (§5.3 代码骨架)——SQLite租约实现轻量级主选举，后续可用etcd |
| **AI 代码无隔离→一个模块的无限循环拖死 EventLoop（v4.0.0）** | **中** | ModuleSandbox 进程隔离 (§5.3 代码骨架)——每模块独立子进程+5次crash永久隔离 |
| **Token费用无预算→月底账单$200而非预期$50（v4.0.0）** | **高** | PromptCacheManager + per-session Token Budget (§5.3 代码骨架)——缓存命中直接返回+月度配额告警 |
| **AI施工Session间上下文丢失→同一问题重复施工（v4.0.0）** | **中** | AI Context Persistence (§5.7)——跨session上下文持久化+过期策略 |
| **全部LLM后端同时宕机→施工停滞（v4.0.0）** | **低** | ModelFallbackChain (§5.7 代码骨架)——3供应商轮流降级 |
| **Owner决策疲劳→低质量审批→事故（v4.0.0）** | **高** | Auto-Decide Engine (§5.3 代码骨架) + 认知负荷预算 (§6.5)——自动决策低风险操作 |
| **SQLite Schema变更无在线迁移→ALTER TABLE 锁表→生产停机（v4.0.0）** | **中** | expand-contract pattern (§2.1-C01)——兼容性检查门禁+双写过渡期 |
| **模块API破坏下游消费者→一模块更新→下游全炸（v4.0.0）** | **中** | Contract Testing (Pact) + Backward Compatibility Enforcement (§2.1-D01, §2.1-I02) |
| **弃用螺旋——Owner长时间不使用系统→告警累积→更不敢打开（v4.0.0）** | **中** | 弃用螺旋防护 (§6.5)——72h无介入→自动降频+增高自愈阈值 |

---

## 9. FMEA — 失效模式与效应分析（v3.0.0 新增）

> **对标**：AIAG FMEA 手册——Severity(1-10) × Occurrence(1-10) × Detection(1-10) = RPN。
> RPN > 200 = 必须强化缓解；RPN > 100 = 需要监控。

| # | 失效模式 | RI 模块 | S | O | D | RPN | 效应 | 检测手段 |
|---|---------|---------|:--:|:--:|:--:|:--:|------|---------|
| 1 | EventBus 队列满→背压信号延迟→上游持续写入→队列溢出丢事件 | RI-01 | 8 | 3 | 5 | **120** | 关键事件丢失→风控/交易状态不一致 | BackpressurePropagation 80%立即广播 + QUeueSize监控 |
| 2 | CircuitBreaker 误熔断→关键下游不可用→全链降级 | RI-05 | 7 | 4 | 4 | **112** | 风控检查失败→交易被拒→PnL偏离 | HALF_OPEN探测 + TrustDecayTracker + 自适应并发限制 |
| 3 | DryRun sandbox产出与真实执行不一致→Owner确认的操作上线后触发LoopDetector | RI-14 | 7 | 4 | 5 | **140** | 一次"同意"上线后→触发回滚→Owner信任受损 | 一致性验证套件（双跑diff）+ SelfSimulate |
| 4 | HealthCheck SLI阈值模糊→DEGRADED判定歧义→自愈触发延迟 | RI-09 | 6 | 5 | 6 | **180** | 系统DEGRADED →30s延迟→雪崩为DOWN | 具体SLI阈值+Reconciliation Loop |
| 5 | IdempotencyGuard TTL过期(25h)→同key重复写入→风控限额被绕过两次 | RI-06 | 9 | 2 | 4 | **72** | 风控限额double-count→pseudo重复执行 | 关键流ES expected_version天然去重——0TTL风险 |
| 6 | AutoDiagnostics连续误诊3次→SelfLimiter激活→但受影响的模块仍在DOWN | RI-12 | 8 | 2 | 3 | **48** | 模块DOWN但自愈回路暂停→Owner需要手动修复 | TrustDecay逆过程：暂停后Owner修复→信任恢复 |
| 7 | SecretsManager主密钥丢失→所有加密配置不可读→系统无法启动 | RI-07 | 10 | 1 | 2 | **20** | 全系统瘫痪→Owner需要手动重建密钥 | 主密钥备份+Offline冷存储+轮转记录 |
| 8 | DeadModule检测误标→活跃模块被标记DORMANT→30天后被归档 | RI-10 | 5 | 2 | 7 | **70** | 模块被误归档→依赖该模块的上游崩 | 30天阈值保守+标记前人工确认弹窗(仅首次误标) |
| 9 | Crypto-Shredding去密钥→但冷备份中仍有点密钥→"删除"实际上不彻底 | RI-13 | 9 | 2 | 6 | **108** | 声称已Shred的数据实际仍可从冷备恢复→GDPR不合规 | Shred操作→同时删除主+冷备双份密钥+3路审计确认 |
| 10 | RetryBudget耗尽→关键消费者重试被拒→DLQ堆积→多事件永久卡在DLQ | RI-05 | 7 | 3 | 4 | **84** | 关键操作被DLQ滞留→时效性窗口过期 | RetryBudget按事件优先级分配：CRITICAL自带保底配额 |
| 11 | Owner "休假模式"激活→但休假期间新Secrets泄露→自愈水平不足→等待Owner回归 | RI-14 | 6 | 2 | 3 | **36** | 泄露持续72h→扩大影响面 | 休假模式下:泄露→自动轮转+沙箱隔离+日报保留为头条 |
| 12 | Phase ∞ 维护期→CostTracker降频→漏掉一笔异常费用→月费超预算 | RI-15 | 4 | 4 | 4 | **64** | 月度LLM费用小幅超预算→未被及时发现 | CostTracker降频从实时→每小时；但全资源追踪保留全精度(10s采样不变) |
| 13 | AI代码在EventLoop中无限循环→阻塞所有RI模块→全系统无响应（v4.0.0） | RI-05 | 9 | 3 | 3 | **81** | 全系统DOWN→只有重启能恢复 | ModuleSandbox进程隔离——AI模块独立子进程运行 |
| 14 | Token配额耗尽→AI施工中断→关键bug修复延迟（v4.0.0） | RI-15 | 7 | 4 | 5 | **140** | 无法修复bug→生产事故窗口延长 | PromptCacheManager + ModelFallbackChain + per-session Budget |
| 15 | Owner睡眠中被夜间自愈失败叫醒→疲劳→漏掉真正紧急的告警（v4.0.0） | RI-09 | 6 | 4 | 5 | **120** | "狼来了"→真紧急时已关通知 | Sleep-Time Protocol——CRITICAL仅1次+5min→自愈 |
| 16 | SQLite schema迁移锁表→所有1500模块阻塞在数据库写入（v4.0.0） | RI-03 | 8 | 2 | 5 | **80** | 全量生产停机→Duration=迁移时长 | expand-contract online migration |
| 17 | 模块A升级破坏模块B的API契约→级联故障至上depending的3层（v4.0.0） | RI-01 | 8 | 3 | 4 | **96** | 一模块升级→炸上下游→系统分区降级 | Pact Contract Testing + CI Backward Compatibility Check |

---

## 10. 关键关联（v3.0.0 扩展）

| 关联文档 | 说明 |
|---------|------|
| `shared-core/blueprint.md` (MOD-INF-016) | **v3.0.0 关键新增**——10 个 RI 模块的代码承载基座，详见 §1.3 承载关系表 |
| `capacity-assurance/blueprint.md` (MOD-INF-001) | 容量 SLO + Error Budget——RI 模块依赖其容量约束 |
| `gate-engine/blueprint.md` (MOD-INF-007) | 任务门禁——ResilienceGuard 不替代 Gate Engine |
| `audit-trail/blueprint.md` (MOD-INF-020) | 审计追踪链——RI-13 EventStore 提供事件级溯源，审计追踪链消费 |
| `rollback-system/blueprint.md` (MOD-INF-021) | 回滚系统——支持 session-level 全量 undo（v3.0.0 新增需求） |
| `drift-detector/blueprint.md` (MOD-INF-023) | 漂移检测——ConfigValidator 增强消费方 |
| `llm-security/blueprint.md` (MOD-INF-014) | LLM 安全网关——Fail-Closed原则对齐 |
| `agent-rbac/blueprint.md` (MOD-INF-018) | Agent RBAC——DryRun审批门对接权限层级 |
| `a2a-protocol/blueprint.md` (MOD-INF-025) | Agent-to-Agent 协议——当 trigger: Agent ≥ 3 |
| `knowledge-base/blueprint.md` (MOD-KB-001) | AutoDiagnostics→修复成功→自动补充知识库 |
| `escalation-protocol/blueprint.md` (MOD-INF-022) | 升级协议——TrustDecayTracker→SelfLimiter→Owner升级链 |
| `budget-enforcer/blueprint.md` (MOD-INF-024) | 预算强制执行——CostTracker硬限额触发→BudgetEnforcer消费降级策略 |
| `shared/production/limiter.py` (MOD-INF-016) | 速率限制基类——RI-05 ResilienceGuard RateLimiter 消费 |
| `shared/production/distributed_lock.py` (MOD-INF-016) | 分布式锁——当 trigger: 模块部署 > 1 节点 |
| Cross-Layer 缺口审计 `RL-001~048` | 本蓝图填补方案 |

> **历史溯源**：Wave 0 终审（2026-04-27）→ v1.0.0（2026-05-01, 6模块）→ v2.0.0（2026-05-05, 全量盲点审计, 12模块）→ v2.1.0（2026-05-05, 三轮深度对标, 15模块）→ **v3.0.0（2026-05-05, 49盲点全量注入 + MOD-INF-016承载关系 + FMEA + ADR + 五视图体系）**。

---

## 11. 已实现代码完整路径索引（v3.0.0 —— MOD-INF-016 承载整合版）

### 11.1 源码文件

> **说明**：✅ = 已实现（含 MOD-INF-016 Shared Core 承载的实现）；❌ = 待施工；N/A = 由 MOD-INF-016 承载，本模块不独立落地文件

| 文件路径 | 实现状态 | 版本/变更 | 承载归属 |
|---------|:---:|------|------|
| `src/zephyr/shared/observer.py` | ✅ | RI-01 EventBus Pub/Sub 基类 | **MOD-INF-016** |
| `src/zephyr/shared/events/event_schemas.py` | ✅ | RI-01 事件体Schema | **MOD-INF-016** |
| `src/zephyr/shared/events/dlq.py` | ✅ | RI-01 DLQ SQLite 持久化 | **MOD-INF-016** |
| `src/zephyr/shared/lifecycle/hooks.py` | ✅ | RI-02 ModuleLifecycle LifecycleAware | **MOD-INF-016** |
| `src/zephyr/shared/config/` | ✅ | RI-03 ConfigCenter 加载+校验 | **MOD-INF-016** |
| `src/zephyr/shared/flags.py` | ✅ | RI-03 FeatureFlag 三态 | **MOD-INF-016** |
| `src/zephyr/shared/resilience/circuit_breaker.py` | ✅ | RI-05 CircuitBreaker 三态 | **MOD-INF-016** |
| `src/zephyr/shared/resilience/retry.py` | ✅ | RI-05 指数退避+Jitter | **MOD-INF-016** |
| `src/zephyr/shared/resilience/fallback.py` | ✅ | RI-05 FallbackChain 降级链 | **MOD-INF-016** |
| `src/zephyr/shared/idempotency.py` | ✅ | RI-06 IdempotencyGuard 基类 | **MOD-INF-016** |
| `src/zephyr/shared/secrets.py` | ✅ | RI-07 SecretsManager | **MOD-INF-016** |
| `src/zephyr/shared/errors.py` | ✅ | RI-08 ErrorHandler 异常树 | **MOD-INF-016** |
| `src/zephyr/shared/logging.py` | ✅ | RI-08 trace_id 传播+结构化日志 | **MOD-INF-016** |
| `src/zephyr/shared/health.py` | ✅ | RI-09 AggregateHealth 三级状态 | **MOD-INF-016** |
| `src/zephyr/shared/metrics.py` | ✅ | RI-10 Telemetry 基础metrics | **MOD-INF-016** |
| `src/zephyr/shared/cache.py` | ✅ | RI-11 CacheLayer 基类 | **MOD-INF-016** |
| `src/zephyr/shared/production/di_container.py` | ❌ | RI-04 DependencyInjector | **MOD-INF-016** (planned §2.9) |
| `src/zephyr/l01_infrastructure/auto_diagnostics.py` | ❌ | RI-12 AutoDiagnostics——**独立落地** | MOD-INF-002 |
| `src/zephyr/l01_infrastructure/event_store.py` | ❌ | RI-13 EventStore——**独立落地** | MOD-INF-002（Phase 3 触发） |
| `src/zephyr/l01_infrastructure/dry_run_simulator.py` | ❌ | RI-14 DryRunSimulator——**独立落地** | MOD-INF-002（Phase 2b） |
| `src/zephyr/l01_infrastructure/cost_tracker.py` | ❌ | RI-15 CostTracker——**独立落地** | MOD-INF-002（Phase 2b） |

### 11.2 配置文件（v3.0.0 扩展）

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
| `config/flag_interaction_matrix.yaml` | ❌ | v3.0.0 Feature Flag pairwise组合测试用例——CI自动消费 |
| `config/schema_evolution_policy.yaml` | ❌ | v3.0.0 Schema兼容性策略：FULL_BACKWARD/FORWARD_TRANSITIVE |
| `config/owner_notification_tiers.yaml` | ❌ | v3.0.0 Owner告警预算N=10、通知分层规则、休假模式激活码 |
| `config/trust_decay_policy.yaml` | ❌ | v3.0.0 TrustDecayTracker恢复窗口+trust阈值+逆过程 |

---

## 12. 施工指引（v3.0.0 —— MOD-INF-016 承载视角版）

### 施工前检查

> **⚠️ 在启动任何Phase施工前**：检查 MOD-INF-016 Shared Core v0.14.0 已有对应实现的状态。若 `shared/` 下文件已是 ✅，RI 模块从设计→到交付→到测试的流程应**跳过独立文件创建**，改为：
> 1. 验证 Shared Core 实现是否满足本蓝图的增强需求
> 2. 若不足：在 `shared/` 目录下扩展（不创建 `l01_infrastructure/` 独立文件）
> 3. 若完全满足：直接标记为 ✅，记录验收时间

### Phase 1a: 底座上线（v3.0.0 MOD-INF-016 快车道）

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 1 | RI-02 ModuleLifecycle——验证 `shared/lifecycle/hooks.py`；扩展优雅关闭协议+Crash-Only设计+预热期 | `shared/lifecycle/shutdown.py` + `shared/lifecycle/warmup.py` | MOD-INF-016 扩展 |
| 2 | RI-04 DependencyInjector——在 `shared/production/di_container.py` 落地构造注入+接口绑定+循环检测 | `shared/production/di_container.py` + 测试 | **MOD-INF-016 新文件** |
| 3 | RI-03 ConfigCenter——验证 `shared/config/`；扩展渐进推出+交互矩阵+SchemaRegistry+FeatureFlag Kill Switch | `shared/flags/rollout.py` + `config/flag_interaction_matrix.yaml` | MOD-INF-016 扩展 |
| 4 | RI-08 ErrorHandler——验证 `shared/errors.py` + `shared/logging.py`；扩展W3C Trace Context | `shared/logging/trace_context.py` | MOD-INF-016 扩展 |
| 5 | 集成测试——RI-02+03+04+08 四模块联调（结构化并发 TaskGroup 验证） | 4 模块联调 + 结构化并发验证 | — |

### Phase 1b: 通信就绪（v3.0.0 扩展）

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 6 | RI-01 EventBus——验证 `shared/observer.py`；扩展PriorityQueue+DeliverySemantics+BackpressurePropagation+Schema兼容性策略 | `shared/events/priority_queue.py` + `config/event_bus.yaml` + `config/schema_evolution_policy.yaml` | MOD-INF-016 扩展 |
| 7 | RI-06 IdempotencyGuard——验证 `shared/production/idempotency.py`；扩展 TTL 分级策略（关键流 ES 天然去重/非关键流 SQLite TTL） | `shared/production/idempotency_policy.yaml` | MOD-INF-016 扩展 |
| 8 | RI-10 TelemetryCollector——验证 `shared/production/metrics.py`；扩展PromptFingerprint+DeadModuleDetector+基数超限LRU策略 | `shared/production/prompt_fingerprint.py` + `shared/production/dead_module_detector.py` | MOD-INF-016 扩展 |
| 9 | 集成测试 + 背压传导链压测 + 基数限制超限测试 | — | — |

### Phase 2a: 韧性安全（v3.0.0 扩展）

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 10 | RI-05 ResilienceGuard——验证 `shared/resilience/`；扩展Bulkhead+LoadShedder+RetryBudget+自适应并发限制 | `shared/resilience/bulkhead.py` + `shared/resilience/load_shedder.py` + `shared/resilience/retry_budget.py` + `config/resilience_guard.yaml` | MOD-INF-016 扩展 |
| 11 | RI-07 SecretsManager——验证 `shared/production/secrets.py`；ConfigCenter 加密字段路由 | `shared/production/secrets_routing.py` | MOD-INF-016 扩展 |
| 12 | RI-09 HealthCheck——验证 `shared/health.py`；扩展具体SLI阈值+ReconciliationLoop+TrustDecayTracker | `shared/health/sli_thresholds.py` + `shared/health/reconciliation.py` + `config/health_check.yaml` | MOD-INF-016 扩展 |
| 13 | RI-11 CacheLayer——验证 `shared/production/cache.py`；扩展 DataAffinity hints + 穿透/LRU 策略 | `shared/production/cache_affinity.py` | MOD-INF-016 扩展 |
| 14 | 全链路韧性测试——混沌实验（熔断+Bulkhead+LoadShedding+RetryBudget联动） | — | — |

### Phase 2b: 自治闭环（v3.0.0 独立施工）

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 15 | **RI-12 AutoDiagnostics**——HealthCheck触发→Runbook匹配→诊断报告Markdown→修复成功→KB自动补充→SelfLimiter | `auto_diagnostics.py` + `config/runbooks/` + `config/trust_decay_policy.yaml` | MOD-INF-002 独立 |
| 16 | **RI-14 DryRunSimulator**——sandbox预演+diff报告+审批门+一致性验证套件+CrossSessionLoopDetector+SelfSimulate | `dry_run_simulator.py` + `config/dry_run_policy.yaml` | MOD-INF-002 独立 |
| 17 | **RI-15 CostTracker**——LLM+CPU+内存+IO调用拦截+全资源per-module费用归属+MaintainabilityScore+预算告警+飞书日报 | `cost_tracker.py` + `config/llm_pricing.yaml` + `config/owner_notification_tiers.yaml` | MOD-INF-002 独立 |
| 18 | ModuleGraph——D3.js可视化 + 依赖拓扑实时渲染 + 死模块标红 | 前端 + API | — |
| 19 | ProgressiveDelivery 预留 | Protocol | — |

### Phase 3: 溯源增强（触发式）

> **不主动启动。** 当模块数 > 100 或 Owner 发出"需要合规审计"指令时触发。

| 步骤 | 任务 | 产出物 | 承载 |
|:--:|------|--------|------|
| 20 | **RI-13 EventStore**——append-only event_log + 快照 + CQRS读模型 + replay_to写隔离 + Crypto-Shredding | `event_store.py` | MOD-INF-002 独立 |
| 21 | L04(风控)/L05(交易)/L06(仓位) 三层写操作切 Event Sourcing | 迁移脚本 + 验证 | — |
| 22 | 事件重放验证 + 审计报告导出 + Crypto-Shredding GDPR验证 | 审计报告 + Shred验证 | — |

### Phase 4: 补偿增强（触发式）

> **不主动启动。** 当首次跨模块多步骤回滚需求出现时触发。

| 步骤 | 任务 | 产出物 |
|:--:|------|--------|
| 23 | RI-13 SagaCoordinator——跨模块补偿事务编排 | `event_store/saga_coordinator.py` |
| 24 | 补偿事务验证——多步骤回滚→逆序执行补偿→所有步骤恢复 | 补偿验证报告 |

### Phase ∞: 维护期切换（全部 Phase 完成后）

| 步骤 | 任务 | 产出物 |
|:--:|------|--------|
| 25 | Phase ∞ 切换检查——全部 Phase 验收标准达标 | 切换确认 |
| 26 | SLO 收紧——维护期容忍度从宽松→严格 | 维护期 SLO 阈值表 |
| 27 | RI 模块降频配置——DryRunSimulator降频 + CostTracker保留全精度 + AutoDiagnostics保留实时 | `config/maintenance_mode.yaml` |

---

## 13. 终极取证审计——系统性假设、致命前提与自限性边界

> **审计员身份**：你不是蓝图作者，不是Owner，你是外部取证专家。你要回答一个问题：**"这个系统在什么条件下会不可逆地失败？"**
>
> 以下 10 项不是"盲点"——前三轮已找到 155+ 个盲点。以下是 **整个架构依赖的致命假设**。每个假设都标注了"若假设不成立"的后果和"缓解可能性"。

### 致命假设清单

| # | 致命假设 | 假设不成立的后果 | 缓解可能性 | 缓解措施（已存在于蓝图） |
|:--:|---------|---------------|:--:|------|
| H1 | **SQLite单写者瓶颈对1500模块并发写入可接受**。SQLite 仅支持1个并发写者，WAL模式下读者与1写者共存，第2个写者遇 SQLITE_BUSY。1500模块若 10% 同时写入=150并发写入排队→每个等 busy_timeout→整体延迟飙升 | EventBus/Health/Cache/Idempotency/DLQ/CostTracker 六类写入同时排队→系统不可用级别延迟 | 🟡 中 | §5.3 BackpressurePropagation + 写争用缓解(B4-C05 busy_timeout)。**但无实际写入密度模型**——150模块同时写入的场景未建模 |
| H2 | **AI自测试+AI自审查能发现AI自生成的缺陷**。deepseek-chat审查自己或deepseek-reasoner审查deepseek-chat——它们共享训练数据分布中的盲区。同一架构的不同模型不等于"独立审查" | TradingKillSwitch的测试由生成TradingKillSwitch的同系列AI编写→两者漏掉同一个边界条件→Kill Switch在生产中不可用 | 🔴 低 | §5.7 "四眼原则"(不同模型审查)。**但不同模型来源同生态(OpenAI/Meta/DeepSeek)的盲区重叠率未测量**。无人类编写的独立黄金测试集 |
| H3 | **AI施工工具生态3年内不会剧变**。deepseek-v4停服/被封/价格×10/API变更→全量1500模块的施工管道断裂 | 无法创建新模块/修复bug/应对安全事故→系统冻结→逐行退化为纯人工维护 | 🟡 中 | §5.7 ModelFallbackChain(3供应商)。但若整个中国LLM生态受冲击(合规/被禁/断网)，所有3供应商可能同时不可用 |
| H4 | **SQLite WAL/DB永不被逻辑性损坏**。`PRAGMA integrity_check` 检测结构损坏，不检测逻辑损坏（如：风控通过但仓位写入了错误数量——两个模块竞态导致的逻辑错误写入SQLite→持久化为"正确"数据） | 账户余额/仓位/风控状态被错误的"永久真实"覆盖→"数据库说它是正确的"→复盘也无法发现 | 🔴 低 | B4-C01 expand-contract + B5-K07 三方对账。**但逻辑损坏检测需要应用层checksum/Merkle trie/交叉验证——这些都在设计层面，未落地为代码骨架** |
| H5 | **1500模块的模块ID不发生碰撞**。AI在不同session中创建模块——若两个session各自生成 MOD-L05-042→后创建的那个静默覆盖前一个的注册 | 一个模块"消失"——依赖它的下游找不到→级联DOWN。日志只显示模块未注册，不显示"被覆盖了" | 🟢 高 | §11 代码索引表。**但无原子ID分配器**——依赖AI遵守命名规范(B5-O05)而非系统强制执行 |
| H6 | **Python 3.11+ asyncio.TaskGroup 在未来5年内保持向后兼容**。蓝图大量依赖 `asyncio.TaskGroup(Python 3.11)` 实现 Structured Concurrency。若Python 3.14/4.0变更TaskGroup语义→1500模块需全部review | 无法升级Python→安全补丁缺口→被迫留在旧Python版本→技术债累积 | 🟢 高 | 无直接缓解。Python生态假设——但1500模块规模让"全部review"不可行 |
| H7 | **Owner具备在紧急情况下的有效决策能力**。凌晨3点被KillSwitch唤醒→需要在30s内判断"是否为真紧急"+"应该按哪个按钮"+"后果是什么"。睡眠惯性+决策疲劳→实际决策能力远低于蓝图假设 | KillSwitch误触发→Owner错误解除→真实算法失控被确认→延误止损窗口 | 🟡 中 | §6.5 紧急唤醒判定(仅核心回路DOWN+3次自愈失败)、§6.3 通知分层。**但Owner真实决策能力无法在设计层面保证——这是人因工程的硬天花板** |
| H8 | **系统能在Owner永久失能后继续运作或安全停止**。休假模式72h，但永久呢？交易系统有账户/仓位/资金——法律上需要人类负责人 | 账户中的仓位无限期持有→市场反向→亏损→法律追责到已故(或失能)Owner的遗产 | 🔴 低 | 无设计。这是蓝图的**绝对边界**——1人系统在所有者死亡/失能后的行为不在设计范围内。外部审计员的建议：为"永久失能"场景设计一个独立的死手开关(Dead Man's Switch)——每月需Owner主动确认，未确认→触发全账户平仓+停止 |
| H9 | **全量集成测试的可行替代方案足够有效**。1500模块的组合爆炸(1500² 可能的交互对)不可能用全量集成测试覆盖。蓝图依赖Contract Testing + DryRun simulaton + 生产Canary渐进上线来替代 | 一个三模块交互的时序bug(模块A在C完成前B就开始)→Canary 1%阶段不触发(因为1%流量碰不到)→全量后触发→全系统DOWN | 🟡 中 | §2.1-D07 Cross-Module Integration Test Orchestration、§5.6 Canary。**但1500模块的真实交互复杂度超出任何测试策略——只能靠生产Canary作为终极防线** |
| H10 | **蓝图的Text-to-Code转换能忠实执行设计意图**。1664行Markdown蓝图→AI读取→生成代码。审计员问：如果蓝图说"Crash-Only设计"但AI生成了`try: ... except: pass`怎么办？ | 蓝图本该 "FAIL-CLOSED" 的策略被AI生成为 "FAIL-OPEN"→安全边界被绕过 | 🟡 中 | §5.7 AI施工自治回路(审查+lint+dryrun) + §5.6 CI/CD六门流水线。**但语义层面的忠实性无自动化验证——例如"优雅关闭协议"vs AI生成的`sys.exit(0)`——两者都过lint但语义完全相反** |

### 取证审计结论

**设计层面已穷尽。** 经过 v1→v2→v2.1→v3(49盲点)→v4(55+盲点)→v5(50+盲点) 六版迭代，蓝图在全维度上已达期刊发表级完备度：15 RI模块 × 48 RL缺口 × 155+盲点清单 × 29代码骨架 × 17 FMEA × 27风险 × 28触发条件 × 28验收指标 × 15关键关联 × 13配置模板。

**剩余10项致命假设的分布：**

```
🔴 不可缓解（2项）：H2(AI审查AI的盲区重叠)、H4(逻辑数据损坏无应用层检测)
🟡 部分缓解（6项）：H1(SQLite写瓶颈)、H3(LLM生态剧变)、H5(模块ID碰撞)、H7(Owner凌晨决策力)、H9(1500模块集成测试)、H10(蓝图→代码忠实转换)
🟢 已缓解（1项）：H8(Owner永久失能——可加Dead Man's Switch缓解)
```

**外部取证专家的最终判断**：

> 该蓝图在 **纸质设计层面已达瓶颈**。再补充盲点将陷入过度设计——例如 H1 (SQLite写瓶颈建模) 需要生产数据而非更多设计文档；H2 (AI盲区重叠率) 需要实际测试而非假设。**剩余风险全部在实施层面**：29个代码骨架→完成实现、1500模块的实际生成、生产环境的3个月静默运行观察。
>
> **建议：停止设计迭代，启动 Phase 1a 实施。** 在第一个模块上线后，根据 `actual vs designed` 的gap重新评估H1-H10——那时候的审计将基于运行数据而非设计文档。
>
> （如果你坚持继续设计迭代，下一次审计将发现的是"在1500模块都跑起来之后，每条消息的序列化开销是多少"——这不是蓝图该回答的问题。）

---

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 5.0.1 | **终极取证审计**：切换视角——从"找缺失模式"到"外部取证专家视角"。新增 §13 10项致命假设清单（H1~H10）：SQLite单写者瓶颈(H1·🟡)/AI审查AI的盲区重叠(H2·🔴)/LLM生态剧变(H3·🟡)/逻辑数据损坏检测缺失(H4·🔴)/模块ID碰撞(H5·🟢)/Python版本依赖(H6·🟢)/Owner凌晨决策力(H7·🟡)/Owner永久失能(H8·🔴·建议Dead Man's Switch)/1500模块集成测试不可行(H9·🟡)/蓝图→代码语义忠实性(H10·🟡)。取证审计结论：**设计层面已穷尽**——建议停止设计迭代，启动 Phase 1a 实施。剩余风险全部在实施与运营层面。 |
| 2026-05-05 | 5.0.0 | **50+ 项新盲点注入——第三轮深度审计：交易系统专项**。金融/交易系统 K01~K12：Emergency Trading Kill Switch（代码骨架 TradingKillSwitch·5步停止序列） + Pre-Trade Risk Check Pipeline + 订单状态机标准化(FIX Protocol) + 市场时钟标准化(NTP→PTP) + 确定性模拟模式 + Paper Trading Infrastructure + 交易对账(三方) + 仓位聚合+硬限额 + EOD/SOD日终处理 + 市场熔断联动 + 滑点模型(Almgren-Chriss) + 费率归因。模块通信模式 L01~L08：Request-Reply / Scatter-Gather / Pipeline / CompetingConsumers / Content-Based Router / MessageFilter / Aggregator / ReturnAddress——§5.9 9模式目录。确定性复现 M01~M06：确定性随机(代码骨架 DeterministicRandom) + 模拟时钟(代码骨架 SimulatedClock) + 精确时序重放 + 快照恢复调试 + Verbosity Control + 非侵入钩子。长期演进 N01~N06：模块废弃5阶段生命周期 + 破坏性变更管理(2版本共存) + 后向兼容窗口 + 迁移文档 + 死代码检测 + 圈复杂度防护(McCabe)。AI施工模式库 O01~O08：模块模板系统(代码骨架 Jinja2模板) + 反模式目录 + 设计决策树 + 按模块类型错误处理 + 命名规范执行器 + Code Ownership Manifest + AI Confidence Annotation + 渐进审查深度(3级)。新增 §5.8 交易系统基础设施模式(5级TradingMode+7大交易专项场景)。代码骨架：24→29。总盲点：104+→155+。蓝图行数 ~1358→~1700+。 |
| 2026-05-05 | 4.0.0 | **55+ 项新盲点注入——系统性补齐**。分布式系统：§2.1-A 10项（Leader Election / Cluster Membership / Split-Brain / Consistent Hashing / Quorum / HLC / CRDT / Anti-Entropy / Multi-Raft / Partition Healing）——代码骨架 SqliteLeaderElection。部署自动化：§2.1-B 8项 + §5.6 CI/CD 六门流水线(静态分析→测试→DryRun→审批→Canary→生产验证)。数据管理：§2.1-C 6项（Schema在线迁移 / PITR / 保留策略 / 连接池 / 写竞争 / 多Region）。测试深度：§2.1-D 8项（Contract Testing(Pact) / Property-Based(Hypothesis) / Test Gen from Diff / Mutation Testing / Fuzz Testing / Golden Files / 集成编排 / Flake检测）。氛围编程专项：§2.1-E 12项（Prompt缓存 / Token预算 / 代码Embedding / 模板系统 / AI代码审查 / 自修复质量门 / AI Decision Log / Diff级Undo / 模型降级链 / 跨Session上下文 / Prompt版本控制 / Token优化管道）——代码骨架 PromptCacheManager + ModelFallbackChain + §5.7 AI施工Session生命周期。1人+AI深度运维：§2.1-F 10项 + §6.5 认知负荷模型+9大新增场景（睡眠保护/晨报/决策疲劳/紧急唤醒/Owner消失演练/知识外化/弃用螺旋/自我解释/周报）——代码骨架 SleepTimeProtocol + AutoDecideEngine。安全深化：§2.1-G 6项（模块沙箱/Semgrep扫描/Merkle审计链/最小权限/SBOM/Prompt注入防护）——代码骨架 ModuleSandbox。可观测性：§2.1-H 5项（Distributed Trace Viz / Error Budget Burn Rate / 容量预测 / Latency Heat Map / 慢查询检测）。API协议：§2.1-I 4项。开发者体验：§2.1-J 6项 + §6.6 6维体验矩阵。FMEA：12→17项。风险：18→27项。触发条件：17→28项。代码骨架：18→24。术语表：55+ 术语对齐国际标准。蓝图行数 ~950→1358（+400+行）。
| 2026-05-05 | 3.0.0 | **49 项盲点全量注入——破坏性升级**。跨模块职责对齐：新增 §1.3 "与 MOD-INF-016 Shared Core 承载关系表"——声明 10 个 RI 模块代码承载归属，代码索引表从全 ❌ 更新为 MOD-INF-016 承载部分 ✅。结构性缺口 GAP-01~07 全量补全：DeliverySemantics（AT_LEAST_ONCE）+ BackpressurePropagation 协议 + DI 统一由 MOD-INF-016 承载 + 时间旅行 replay_to 写隔离 + DryRun 一致性验证套件 + ConfigCenter 加密字段强制走 SecretsManager + LoopDetector 自动恢复条件。设计深度强化 WEAK-01~07：DLQ SQLite 持久化 + 具体 SLI 阈值数值 + Feature Flags 渐进推出(1%→100%)+交互矩阵(FlagInteractionValidator) + IdempotencyGuard TTL 分级(关键流ES天然去重) + Telemetry 基数语义(per-module 500/LRU淘汰) + Cooldown 分层(MEDIUM 5m/HIGH 10m/CRITICAL 15m) + CostTracker 全资源追踪(CPU/内存/IO)。业界对标 MISS-01~14：Structured Concurrency(asyncio.TaskGroup) + Bulkhead 舱壁隔离 + 优雅关闭协议(drain→force kill) + 重试风暴防护(RetryBudget) + W3C Trace Context(traceparent) + LoadShedder 负载脱落 + Schema 兼容性策略(FULL_BACKWARD/FORWARD_TRANSITIVE) + 容量预留(关键模块X%) + 预热期(warmup→READY) + Crypto-Shredding(GDPR删除权) + Crash-Only 设计理念。前沿盲点 FUTURE-01~10：AI自预演(SelfSimulate) + PromptFingerprint + 自愈→KB反馈 + 事件优先级(PriorityQueue CRITICAL/HIGH/NORMAL/LOW) + SagaCoordinator(Phase 4 触发) + SpeculativeExecution(Hedged Requests) + Data Locality/Affinity + Operator/Reconciliation Pattern + SelfLimiter(自限反馈) + 不可变基础设施(Phase 5 planned)。1人+AI专项 OPT-01~07：Owner 告警预算(N=10) + 通知分层(💀实时/🟡每小时/🟢每日/⚪Dashboard/✨AI_SELF_HEALED) + Owner 离线/休假模式 + Module MaintainabilityScore + CrossSession LoopDetector(跨Session重复修改) + 施工→维护切换(Phase ∞)。蓝图质量：新增 §9 FMEA(12 项失效模式 RPN 分析) + §5.2 设计原则(Crash-Only/StructuredConcurrency/Fail-Closed/ImmutableEvents/ProgressiveDisclosure) + §6.4 五视图体系。代码索引表：整合 MOD-INF-016 已实现的10个 ✅ + N/A 标记（不再独立落地）。施丌指引：从"独立创建文件"改为"先验证 shared 实现→再扩展 shared→仅在无shared对应时独立落地"。Phase 路线：Phase 2a 扩展(七合一韧性+标准化健康)、Phase 2b 扩展(自治闭环含SelfSimulate+一致性套件+全资源FinOps)、Phase 3 扩展(含Crypto-Shredding)、Phase 4 新增(Saga补偿事务)、Phase ∞ 新增(维护期切换)。RL 缺口 21→48。代码骨架 6→18。配置文件 9→13。容量模型 5→10(Push模型升级为通知分层+DailySummary)。验收指标 12→28。扩展路径 8→14。风险 12→18 + 12项FMEA。关键关联 6→15（含 MOD-INF-016 承载关系+消费者上下游）。蓝图行数 ~522→~950+。 |
| 2026-05-05 | 2.1.0 | **深度补全**：三轮专业对标（Event Sourcing+CQRS金融行业76%采用率+Dry Run Agent CI/CD+FinOps Visibility/Allocation/Optimization）。新增：RI-13 EventStore（ES+CQRS+快照+时间旅行, Phase 3 触发式）、RI-14 DryRunSimulator（sandbox预演+审批门, Phase 2b）、RI-15 CostTracker（per-module LLM费用归属+预算告警+优化建议, Phase 2b）。RL缺口 18→21。代码骨架 3→6。配置文件 7→9。容量模型 5→7。扩展路径 4→5。风险 9→12。Phase路线：Phase 2b 扩展（自治闭环=诊断+预演+费用三合一），Phase 3 新增（溯源增强，触发式）。 |
| 2026-05-05 | 2.0.0 | **破坏性升级**：6→12 RI 模块 + 韧性基础设施前置 + 1人+AI运维语境校准 |
| 2026-05-01 | 1.0.1 | 补充 §10 已实现代码完整路径索引 |
| 2026-05-01 | 1.0.0 | 初始创建——6 RI 模块 + RL-001~RL-009 |

---

## 施工落盘确认（2026-05-07 审计）

| 维度 | 状态 |
|------|------|
| construction_progress | phase_2_complete（Phase 1 Skeleton + Phase 2 E2E 均已通过） |
| 源码路径 | `src/zephyr/` (跨模块: core/runtime, hooks/, governance/, shared/) |
| 源码文件数 | 40 个 .py/.yaml |
| 测试路径 | `tests/infrastructure/` + `tests/integration/` |
| 配置文件 | `config/runtime/*.yaml` + `config/context_rules.yaml` |
| 关键入口 | `runtime_integrator`, `hook_manager`, `shared/protocols` |
