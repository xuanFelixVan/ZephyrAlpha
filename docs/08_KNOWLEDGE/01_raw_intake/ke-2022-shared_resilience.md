---
module_id: KE-1931
status: active
title: 2.6 shared-resilience（韧性基座）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.6 shared-resilience（韧性基座）

2.6 shared-resilience（韧性基座）

> **盲点 B6/B9/B15 修复**——统一重试/熔断/降级策略，零依赖基类。
> 与 gates/circuit_breaker.py 互补——本模块纯内存，gates 版 SQLite 持久化 + 门禁集成。

| 文件 | 职责 |
|------|------|
| `resilience/retry.py` | **async_retry 装饰器**——指数退避 + jitter + 异常白名单/黑名单 |
| `resilience/circuit_breaker.py` | **CircuitBreaker 状态机**——CLOSED/OPEN/HALF_OPEN 三态，线程安全，零持久化 |
| `resilience/fallback.py` | **FallbackChain 降级链**——按序尝试 fallback 函数，全部失败抛 FallbackExhaustedError |
