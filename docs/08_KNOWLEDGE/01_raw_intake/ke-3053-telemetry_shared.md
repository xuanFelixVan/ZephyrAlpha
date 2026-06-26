---
module_id: KE-2952------shared-002
title: 复用清单（Telemetry 基于这些 shared 组件构建，不复写）
category: module_blueprint
ttl: permanent
---

# 复用清单（Telemetry 基于这些 shared 组件构建，不复写）

复用清单（Telemetry 基于这些 shared 组件构建，不复写）

| shared 组件 | 绝对路径 | 提供的能力 | Telemetry 使用方式 | AI 施工约束 |
|------------|---------|-----------|-------------------|-----------|
| **TraceContext**（contextvars） | `shared/logging.py` | trace_id / span_id / session_id 跨调用链自动传播 | §5 logs + §6 traces 的上下文来源 | **MUST 使用 shared.logging 的 `TraceContext`**，禁止定义第二个 TraceContext |
| **CTR-TRACE-001** | `shared/contracts/trace_context.py` | trace_id / span_id / parent_span_id / service_name 数据契约 | §6 Span 字段必须兼容此契约 | Span.trace_id/span_id/parent_span_id 格式与 CTR-TRACE-001 一致 |
| **get_logger + JSON Formatter** | `shared/logging.py` | 结构化 JSON 日志（_StructuredFormatter）+ 人类可读控制台（_HumanFormatter） | §5 logs 子系统不做独立日志系统——它是 shared.logging 的消费端和增强端 | 各模块的 log 统一经 shared.logging → Telemetry logs 子系统持久化，不双写 |
| **LifecycleAware + ModuleHealth** | `shared/lifecycle/hooks.py` | 模块生命周期协议 + `health_check() → ModuleHealth` | §10 health 子系统定时轮询所有已注册模块的 `health_check()` | 健康检查数据来源是各模块的 LifecycleAware 协议实现，不是 Telemetry 自行探测 |
| **BackpressureThrottle/Pause/Resume** | `shared/contracts/backpressure/` | CTR-BP-001 PAUSE / CTR-BP-002 THROTTLE / CTR-BP-003 RESUME | §4 ring buffer 80%/95% 填满时发出 backpressure 信号 | 禁止静默丢数据——必须先发 THROTTLE → 再发 PAUSE → 最后丢弃 |
| **FeatureFlag**（三态） | `shared/flags.py` | FlagState.ALWAYS_ON / CONDITIONAL / ALWAYS_OFF | 控制 profiling 开关、采样率、日志级别、成本阈值 | 所有实验性 Telemetry 功能 MUST 由 FeatureFlag 守护（默认 OFF） |
| **EventBus**（pub/sub） | `shared/observer.py` | 线程安全的订阅/发布/取消 | Telemetry 内部事件分发（archive TTL 触发、告警状态变更、schema 变更通知） | 内部事件走 observer.EventBus，不做自定义事件系统 |
| **TelemetryEmitter 契约** | `shared/contracts/telemetry_emitter.py` | CTR-P1-013 遥测发射器接口 | MetricPoint / AIBehaviorEvent / HealthReport 等是实现此契约的具体数据类 | §3 所有新数据类 MUST 实现或兼容 TelemetryEmitter 接口 |
