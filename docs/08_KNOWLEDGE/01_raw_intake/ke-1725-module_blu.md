---
module_id: KE-1635
status: active
title: 2. 到需要做什么（回顾大盘 + 用户原意）
category: module_blueprint
---

# 2. 到需要做什么（回顾大盘 + 用户原意）

2. 到需要做什么（回顾大盘 + 用户原意）

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
| RL-043 | 缺容量预留（关键模块） | RI-05 Reservation：L04/L06预
