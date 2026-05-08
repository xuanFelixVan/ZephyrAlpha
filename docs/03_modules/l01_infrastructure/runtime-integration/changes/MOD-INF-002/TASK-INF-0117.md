---
task_id: "TASK-INF-0117"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §8 风险与缓解——27项风险 R001~R027"
title: "27项风险缓解实现——§8全量风险：asyncio.Queue内存暴增/CircuitBreaker误熔断/Secrets主密钥丢失/Cache缓存雪崩/重试风暴等"
description: |
  逐条实现蓝图 §8 的 27 项风险缓解措施。
  R001 asyncio.Queue 内存暴增→QUEUE_MAX_SIZE=10000硬限制+背压+LoadShedder+
  R002 CircuitBreaker 误熔断→HALF_OPEN探测+渐进恢复+TrustDecayTracker+
  R003 IdempotencyGuard 存储膨胀→TTL分级：关键流ES天然去重/非关键流24hTTL+
  R004 IdempotencyGuard TTL过期致重复写入→关键流ES expected_version天然去重+
  R005 SecretsManager 主密钥丢失→主密钥备份+轮转记录+Offline冷存储+
  R006 CacheLayer 缓存穿透→空值缓存+互斥锁防并发+Bulkhead隔离+
  R007 DI 容器循环依赖→BFS检测+启动阻断+
  R008 AutoDiagnostics 误诊→TrustDecayTracker+置信度标记+"请Owner确认"+
  R009 AutoDiagnostics 自反锁→SelfLimiter：同指标修复3次/h→暂停+升级Owner+
  R010 EventStore 日志膨胀→快照策略(每1000事件)+热/冷分层+
  R011 DryRun vs 真实不一致→一致性验证套件(sandbox vs真实双跑diff+共享Protocol)+
  R012 CostTracker 定价表过期→定价表外置 config/llm_pricing.yaml+定时对比官方+
  R013 重试风暴→RetryBudget 每分钟100配额+耗尽拒绝+
  R014 背压传导不及时→BackpressurePropagation 队列>80%立即广播+
  R015 DeadModule 误标→30天DORMANT/60天DEAD/90天归档+
  R016 Schema兼容性→FULL_BACKWARD强制+破坏性变更需2版本共存+
  R017 预热期不足→warmup phase+readiness signal：缓存预热+内部HC全PASS后才READY+
  R018 Crypto-Shredding密钥管理→per-stream密钥=SHA-256(stream_id+master_secret)可复现不存储+
  R019 单节点→SqliteLeaderElection轻量级主选举+
  R020 AI代码无隔离→ModuleSandbox进程隔离+独立子进程+crash永久隔离+
  R021 Token费用无预算→PromptCacheManager+per-sessionTokenBudget+缓存命中+
  R022 AI Session间上下文丢失→AIContextPersistence跨session持久化+
  R023 LLM后端宕机→ModelFallbackChain+3供应商轮流降级+
  R024 Owner决策疲劳→AutoDecideEngine+认知负荷预算模型+
  R025 SQLite Schema变更→expand-contract pattern 在线迁移+
  R026 模块API破坏下游→Pact Contract Testing+CI后向兼容验证+
  R027 弃用螺旋→72h无介入→自动降频+升高自愈阈值。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\config\\resilience_guard.yaml"
    description: "熔断阈值/限流配额/Bulkhead配额/LoadShedder/RetryBudget——R001~R002/R013~R014 缓解落地（与TASK-INF-0104共用）"
  - path: "D:\\ZephyrAlpha\\config\\secrets_policy.yaml"
    description: "主密钥备份/轮转/审计——R005缓解落地（与TASK-INF-0104共用）"
  - path: "D:\\ZephyrAlpha\\config\\health_check.yaml"
    description: "SLI阈值/故障域/自愈策略——R008/R009/R017缓解落地（与TASK-INF-0104共用）"
  - path: "D:\\ZephyrAlpha\\config\\cache_layer.yaml"
    description: "空值缓存+LRU——R006缓解落地"
  - path: "D:\\ZephyrAlpha\\config\\dry_run_policy.yaml"
    description: "一致性验证套件+Loop检测——R011缓解落地（与TASK-INF-0105共用）"
  - path: "D:\\ZephyrAlpha\\config\\llm_pricing.yaml"
    description: "定价表+定时对比——R012缓解落地（与TASK-INF-0105共用）"
  - path: "D:\\ZephyrAlpha\\config\\schema_evolution_policy.yaml"
    description: "FULL_BACKWARD兼容策略——R016缓解落地（与TASK-INF-0103共用）"
allowed_touch:
  - "D:\\ZephyrAlpha\\config\\resilience_guard.yaml"
  - "D:\\ZephyrAlpha\\config\\secrets_policy.yaml"
  - "D:\\ZephyrAlpha\\config\\health_check.yaml"
  - "D:\\ZephyrAlpha\\config\\cache_layer.yaml"
  - "D:\\ZephyrAlpha\\config\\dry_run_policy.yaml"
  - "D:\\ZephyrAlpha\\config\\llm_pricing.yaml"
  - "D:\\ZephyrAlpha\\config\\schema_evolution_policy.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§8"
    reason: "27项风险——逐条标注缓解措施对应的代码文件/配置文件/任务ID"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§8 全量风险表——27项风险×概率×缓解措施×所属RI模块"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 45
acceptance_criteria:
  - "R001~R027: 每项风险有≥1条可验证的缓解措施落地"
  - "R006 缓存雪崩: 空值缓存+互斥锁双重防护已配置"
  - "R008 误诊: TrustDecayTracker 误报>30%→1h内降级的监控告警规则已配置"
  - "R021 Token费用: PromptCacheManager+per-session Budget 已配置月度配额告警"
  - "R024 决策疲劳: AutoDecideEngine 自动决策阈值已可配置且可动态调整"
  - "R026 Schema变更: CI后向兼容检测门禁已集成 Pact 测试"
  - "所有风险缓解措施在对应配置文件中可被追溯"
rollback_instructions: |
  1. 检查上述配置文件是否已有先前任务创建——如有则检查本任务新增条目是否可独立回滚
  2. 如配置文件首次创建→删除该文件
  3. 对其他任务共用的配置文件——仅删除本任务新增的特定条目
depends_on:
  - "TASK-INF-0104"
  - "TASK-INF-0105"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
