---
task_id: "TASK-INF-0113"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §5.1 终选技术栈——15 RI 模块架构决策（DD-001~DD-015）"
title: "15 RI 模块架构决策实现——§5.1 终选技术栈全量落地：EventBus/ModuleLifecycle/ConfigCenter/DependencyInjector/ResilienceGuard 等"
description: |
  实现蓝图 §5.1 的 15 项终选技术栈决策（DD-001~DD-015），每条决策1项实现任务。
  DD-001 RI-01 EventBus→asyncio.PriorityQueue(四级优先级)+Pydantic类型化+DLQ SQLite持久化+背压信号+AT_LEAST_ONCE+
  DD-002 RI-02 ModuleLifecycle→ABC+拓扑排序BFS+version range constraint+优雅关闭+Crash-Only+
  DD-003 RI-03 ConfigCenter→YAML+os.environ覆盖+Pydantic校验+watchdog热重载+Feature Flags(渐进推出+交互矩阵+Kill Switch)+
  DD-004 RI-04 DependencyInjector→MOD-INF-016 di_container.py 承载——构造注入+ABC接口绑定+循环检测+
  DD-005 RI-05 ResilienceGuard→CircuitBreaker(三态)+TokenBucket(限流)+TimeoutContext+降级链YAML+Bulkhead+LoadShedder+RetryBudget+
  DD-006 RI-06 IdempotencyGuard→分级策略：关键流ES expected_version天然去重/非关键流SHA-256+SQLite TTL+
  DD-007 RI-07 SecretsManager→AES-256-GCM本地加密+.env自动加解密+访问审计发射+
  DD-008 RI-08 ErrorHandler→Enum(SRE分类)+Structlog结构化+W3C traceparent header+
  DD-009 RI-09 HealthCheck→async探针+依赖传导+三级状态+具体SLI阈值+ReconciliationLoop+
  DD-010 RI-10 TelemetryCollector→structlog聚合+per-module基数限制500+超限LRU+PromptFingerprint+DeadModuleDetector+
  DD-011 RI-11 CacheLayer→LRU dict+VMS语义缓存+TTL分层+DataAffinity hints+
  DD-012 RI-12 AutoDiagnostics→HealthCheck触发+Runbook YAML匹配+诊断报告Markdown+KB补充+
  DD-013 RI-13 EventStore→SQLite append-only event_log+快照(每1000事件)+CQRS读模型+Crypto-Shredding+
  DD-014 RI-14 DryRunSimulator→sandbox标志位+拦截写操作+diff报告+审批门+一致性验证套件+CrossSessionLoopDetector+
  DD-015 RI-15 CostTracker→LLM调用拦截→token计数→美元换算+CPU/内存/IO记录+per-module归属+飞书日报。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\observer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\idempotency.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\secrets.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\errors.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\metrics.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cache.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\config\\telemetry_collector.yaml"
    description: "聚合/基数限制per-module/PromptFingerprint开关/DeadModuleDetector阈值"
  - path: "D:\\ZephyrAlpha\\config\\cache_layer.yaml"
    description: "TTL分层/LRU/语义缓存/DataAffinity hints"
  - path: "D:\\ZephyrAlpha\\config\\flag_interaction_matrix.yaml"
    description: "Feature Flag pairwise组合测试用例"
  - path: "D:\\ZephyrAlpha\\config\\schema_evolution_policy.yaml"
    description: "Schema兼容性策略"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\flags\\rollout.py"
    description: "FeatureFlag渐进推出——1%→10%→50%→100%+自动Kill Switch+SchemaRegistry"
allowed_touch:
  - "D:\\ZephyrAlpha\\config\\telemetry_collector.yaml"
  - "D:\\ZephyrAlpha\\config\\cache_layer.yaml"
  - "D:\\ZephyrAlpha\\config\\flag_interaction_matrix.yaml"
  - "D:\\ZephyrAlpha\\config\\schema_evolution_policy.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\flags\\rollout.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\observer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.1"
    reason: "15 项终选技术栈决策——每条决策核对已有MOD-INF-016实现覆盖度"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§5.1 15项终选技术栈决策清单——逐条核对10个shared/已有实现"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 60
acceptance_criteria:
  - "DD-001: EventBus PriorityQueue 四级优先级——CRITICAL(0)/HIGH(1)/NORMAL(2)/LOW(3)"
  - "DD-002: ModuleLifecycle 拓扑排序BFS——500模块≤50ms"
  - "DD-003: ConfigCenter Feature Flags 渐进推出——1%→10%→50%→100%+自动Kill Switch"
  - "DD-004: DependencyInjector 由MOD-INF-016统一承载——单DI容器入口"
  - "DD-005: ResilienceGuard 七合一——熔断+限流+降级+Bulkhead+LoadShedder+RetryBudget+自适应并发"
  - "DD-007: SecretsManager AES-256-GCM——零明文密钥落盘"
  - "DD-009: HealthCheck SLI阈值具体化——CPU>80%→DEGRADED"
  - "DD-012: AutoDiagnostics 闭环——诊断→修复→KB沉淀"
  - "DD-015: CostTracker 全资源FinOps——per-module+session_id粒度"
  - "全部15条决策有对应的已实现/待落地文件追踪"
rollback_instructions: |
  1. 删除新增配置文件：telemetry_collector.yaml / cache_layer.yaml / flag_interaction_matrix.yaml / schema_evolution_policy.yaml
  2. 删除 shared/flags/rollout.py
  3. 如 shared/flags/ 目录变为空→删除目录
depends_on:
  - "TASK-INF-0101"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
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
