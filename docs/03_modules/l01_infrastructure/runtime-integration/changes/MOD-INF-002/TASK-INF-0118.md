---
task_id: "TASK-INF-0118"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §9 FMEA——17项失效模式与效应分析 FMEA-001~FMEA-017"
title: "17项FMEA失效模式缓解实现——EventBus溢出/误熔断/DryRun不一致/SLI阈值模糊/AutoDiagnostics误诊等"
description: |
  逐条实现蓝图 §9 的 17 项 FMEA 失效模式缓解（AIAG 标准：S×O×D=RPN）。
  FMEA-001 EventBus队列满→RPN 120 (S8×O3×D5)——BackpressurePropagation 80%立即广播+QueueSize监控+
  FMEA-002 CircuitBreaker误熔断→RPN 112 (S7×O4×D4)——HALF_OPEN探测+TrustDecayTracker+自适应并发限制+
  FMEA-003 DryRun sandbox与真实不一致→RPN 140 (S7×O4×D5)——一致性验证套件(双跑diff)+SelfSimulate+
  FMEA-004 SLI阈值模糊→RPN 180 (S6×O5×D6)——具体SLI阈值+ReconciliationLoop+
  FMEA-005 IdempotencyGuard TTL过期→RPN 72 (S9×O2×D4)——关键流ES expected_version天然去重+
  FMEA-006 AutoDiagnostics连续误诊→RPN 48 (S8×O2×D3)——TrustDecay逆过程+暂停后Owner修复→信任恢复+
  FMEA-007 SecretsManager主密钥→RPN 20 (S10×O1×D2)——主密钥备份+Offline冷存储+轮转记录+
  FMEA-008 DeadModule误标→RPN 70 (S5×O2×D7)——30天阈值保守+标记前人工确认弹窗+
  FMEA-009 Crypto-Shredding不彻底→RPN 108 (S9×O2×D6)——Shred同时删主+冷备双份密钥+3路审计确认+
  FMEA-010 RetryBudget耗尽→RPN 84 (S7×O3×D4)——按事件优先级分配：CRITICAL自带保底配额+
  FMEA-011 休假模式泄露→RPN 36 (S6×O2×D3)——泄露→自动轮转+沙箱隔离+日报保留为头条+
  FMEA-012 Phase∞维护期CostTracker降频漏费→RPN 64 (S4×O4×D4)——CostTracker全资源追踪保留全精度10s采样+
  FMEA-013 AI代码无限循环→RPN 81 (S9×O3×D3)——ModuleSandbox进程隔离+
  FMEA-014 Token配额耗尽→RPN 140 (S7×O4×D5)——PromptCacheManager+ModelFallbackChain+per-session Budget+
  FMEA-015 睡眠中被叫醒→RPN 120 (S6×O4×D5)——SleepTimeProtocol CRITICAL仅1次+5min→自愈+
  FMEA-016 SQLite schema迁移锁表→RPN 80 (S8×O2×D5)——expand-contract online migration+
  FMEA-017 模块API破坏下游→RPN 96 (S8×O3×D4)——Pact Contract Testing+CI后向兼容验证。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\config\\fmea_mitigation_monitoring.yaml"
    description: "17项FMEA缓解措施监控配置——每项标注RPN值+SOD维度+监控指标+告警阈值"
allowed_touch:
  - "D:\\ZephyrAlpha\\config\\fmea_mitigation_monitoring.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§9"
    reason: "FMEA AIAG 标准——17项失效模式×(S×O×D=RPN)——RPN>200强化缓解 RPN>100需监控"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§9 FMEA全量表——17项失效模式×Severity/Occurrence/Detection/RPN×效应×检测手段"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 45
acceptance_criteria:
  - "FMEA-001 (RPN 120): BackpressurePropagation监控告警——queue_usage>80%→WARNING触发"
  - "FMEA-003 (RPN 140): 一致性验证套件——sandbox vs 真实双跑 diff=0 确认"
  - "FMEA-004 (RPN 180): SLI阈值具体化——CPU>80%→DEGRADED >95%→DOWN 无主观判断"
  - "FMEA-009 (RPN 108): Crypto-Shredding 3路审计确认——删主+冷备+审计确认三同步"
  - "FMEA-013 (RPN 81): ModuleSandbox 进程隔离验证——子进程crash不污染主进程"
  - "FMEA-014 (RPN 140): Token配额告警+ModelFallbackChain+PromptCacheManager三重防护"
  - "全部17项FMEA条目有对应的监控配置"
rollback_instructions: |
  1. 删除 config/fmea_mitigation_monitoring.yaml
depends_on:
  - "TASK-INF-0117"
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
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
