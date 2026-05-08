---
task_id: "TASK-INF-0104"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2 RL-005/009/011/014/015/016/027/030/032/037/039/040/041/043/046 + §5.5"
title: "Phase 2a 韧性安全缺口填补——RL-005/009/011/014~016/027/030/032/037/039~041/043/046"
description: |
  填补 Phase 2a 涉及的 Cross-Layer 缺口——"1人+AI 能不能睡好觉"的分水岭。
  RL-005 健康传导→HealthCheck 三级+故障域隔离（≥5域）+
  RL-009 错误传播链→ErrorTracer W3C trace_id 传递（跨3层完整）+
  RL-011 运行时熔断→ResilienceGuard CircuitBreaker（5次失败→熔断）+
  RL-014 幂等→IdempotencyGuard key 去重（100次=执行1次）+
  RL-015 Secrets→SecretsManager AES-256-GCM（YAML中零明文密钥）+
  RL-016 限流→ResilienceGuard RateLimiter（误差<5%）+
  RL-027 加密归属→ConfigCenter→SecretsManager 强制路由（100%唯一加密路径）+
  RL-030 SLI阈值→CPU>80%→DEGRADED, >95%→DOWN+
  RL-032 TTL分级→关键流ES天然去重/非关键流SQLite24h+
  RL-037 Bulkhead→per-module线程/连接池上限+
  RL-039 重试风暴→RetryBudget全局配额（100/分钟）+
  RL-040 W3C Trace→traceparent header（OTel完全兼容）+
  RL-041 负载脱落→LoadShedder优先级丢弃+
  RL-043 容量预留→L04/L06预分配X%队列+
  RL-046 Flag交互矩阵→pairwise组合测试。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\retry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\fallback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\idempotency.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\secrets.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\bulkhead.py"
    description: "舱壁隔离——per-module Semaphore+连接池上限+ResourcePool"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\load_shedder.py"
    description: "负载脱落——过载>80%按优先级丢弃+LOW拒绝"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\retry_budget.py"
    description: "重试风暴防护——全局配额100/分钟+拒绝重试+jitter"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\secrets_routing.py"
    description: "ConfigCenter加密字段→SecretsManager强制路由"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health\\sli_thresholds.py"
    description: "具体SLI阈值——CPU>80%→DEGRADED, >95%→DOWN; 错误率>5%→DEGRADED"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health\\reconciliation.py"
    description: "ReconciliationLoop——≤30s对账周期+持续自愈"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging\\trace_context.py"
    description: "W3C TraceContext——traceparent header 标准格式"
  - path: "D:\\ZephyrAlpha\\config\\resilience_guard.yaml"
    description: "熔断阈值/限流配额/降级链/Bulkhead配额/LoadShedder阈值/RetryBudget配额"
  - path: "D:\\ZephyrAlpha\\config\\secrets_policy.yaml"
    description: "加密算法/轮转/审计规则/ConfigCenter加密字段路由"
  - path: "D:\\ZephyrAlpha\\config\\health_check.yaml"
    description: "探针定义/SLI阈值/故障域/自愈策略/Reconciliation周期"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\bulkhead.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\load_shedder.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\retry_budget.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\secrets_routing.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health\\sli_thresholds.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health\\reconciliation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging\\trace_context.py"
  - "D:\\ZephyrAlpha\\config\\resilience_guard.yaml"
  - "D:\\ZephyrAlpha\\config\\secrets_policy.yaml"
  - "D:\\ZephyrAlpha\\config\\health_check.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\retry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\fallback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\idempotency.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\secrets.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 Bulkhead/RetryBudget/LoadShedder 代码骨架"
    reason: "舱壁→RetryBudget→LoadShedder 联动实现"
  - module_id: "MOD-INF-002"
    section: "§5.3 W3CTraceContext 代码骨架"
    reason: "traceparent header 格式: 00-{trace_id}-{span_id}-{flags}"
  - module_id: "MOD-INF-002"
    section: "§5.2 设计原则 Fail-Closed"
    reason: "SecretsManager 不可用时拒绝操作"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "本蓝图——§2 RL缺口定义、§5.3 Bulkhead/LoadShedder/RetryBudget/GracefulShutdown/W3CTraceContext 代码骨架"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\circuit_breaker.py"
    reason: "现有 CircuitBreaker 实现——了解扩展点与联动方式"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 32000
timeout_minutes: 90
acceptance_criteria:
  - "CircuitBreaker OPEN→恢复 ≤ 30s（RL-011）"
  - "IdempotencyGuard 100次重复=执行1次（RL-014）"
  - "YAML 中零明文密钥——SecretsManager AES-256-GCM 全覆盖（RL-015）"
  - "RateLimiter 限流误差 < 5%（RL-016）"
  - "ConfigCenter 加密字段 0 次非法路径——强制走 SecretsManager（RL-027）"
  - "健康判定自动化无歧义——具体 SLI 阈值落地（RL-030）"
  - "关键数据 0 TTL 过期风险——ES 天然去重（RL-032）"
  - "Bulkhead: 一模块崩不影响其他（SLO 95%）（RL-037）"
  - "RetryBudget: 0 次配额超额（RL-039）"
  - "traceparent 标准格式 100%——OTel 完全兼容（RL-040）"
  - "LoadShedder: CRITICAL 丢弃率 0%（RL-041）"
rollback_instructions: |
  1. 删除新增 resilience 文件：bulkhead.py / load_shedder.py / retry_budget.py
  2. 删除新增 secrets_routing.py
  3. 删除新增 health 文件：sli_thresholds.py / reconciliation.py
  4. 删除新增 logging/trace_context.py
  5. 删除新增配置文件：resilience_guard.yaml / secrets_policy.yaml / health_check.yaml
  6. 如 shared/ 下现有文件被意外修改→git checkout 还原
depends_on:
  - "TASK-INF-0103"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "security"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
  - "MOD-INF-016"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
