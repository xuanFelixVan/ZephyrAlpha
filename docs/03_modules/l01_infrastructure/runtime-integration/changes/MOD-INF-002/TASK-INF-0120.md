---
task_id: "TASK-INF-0120"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §12 施工指引——Phase 1a~Phase ∞ 全量施工步骤 + 施工前检查"
title: "§12 施工指引执行——从施工前检查到 Phase ∞ 维护期切换全部 27 个施工步骤"
description: |
  执行蓝图 §12 的全部施工步骤——将设计转化为实施计划。
  施工前检查：验证 MOD-INF-016 shared/ 下10个已实现文件→决定跳过独立文件创建还是扩展。
  Phase 1a 底座上线（步骤1~5）：
  步骤1 验证 shared/lifecycle/hooks.py→扩展 graceful shutdown+warmup
  步骤2 shared/production/di_container.py 新文件落地
  步骤3 验证 shared/config/→扩展渐进推出+交互矩阵+SchemaRegistry+KillSwitch
  步骤4 验证 shared/errors.py+logging.py→扩展W3C TraceContext
  步骤5 四模块联调(RI-02+03+04+08)+结构化并发验证
  Phase 1b 通信就绪（步骤6~9）：
  步骤6 验证 shared/observer.py→扩展PriorityQueue+DeliverySemantics+Backpressure+Schema兼容
  步骤7 验证 shared/idempotency.py→扩展TTL分级策略
  步骤8 验证 shared/metrics.py→扩展PromptFingerprint+DeadModuleDetector
  步骤9 集成测试+背压传导链压测+基数限制超限测试
  Phase 2a 韧性安全（步骤10~14）：
  步骤10 验证 shared/resilience→扩展Bulkhead+LoadShedder+RetryBudget+自适应并发
  步骤11 验证 shared/secrets.py→ConfigCenter加密字段路由
  步骤12 验证 shared/health.py→扩展SLI阈值+Reconciliation+TrustDecayTracker
  步骤13 验证 shared/cache.py→扩展DataAffinity hints+穿透防护
  步骤14 全链路韧性测试——混沌实验
  Phase 2b 自治闭环（步骤15~19）：
  步骤15 RI-12 AutoDiagnostics独立落地+Runbooks+TrustDecay
  步骤16 RI-14 DryRunSimulator独立落地+一致性+LoopDetector+SelfSimulate
  步骤17 RI-15 CostTracker独立落地+飞书日报
  步骤18 ModuleGraph D3.js可视化+拓扑图实时渲染+死模块标红
  步骤19 ProgressiveDelivery 预留 Protocol
  Phase 3 溯源增强（步骤20~22）触发式
  Phase 4 补偿增强（步骤23~24）触发式
  Phase ∞ 维护期切换（步骤25~27）
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\construction_phase_tracker.md"
    description: "28项施工步骤进度追踪表——每步骤标注Phase/步骤号/任务/产出物/承载归属/当前状态"
  - path: "D:\\ZephyrAlpha\\config\\maintenance_mode.yaml"
    description: "Phase ∞ 维护期配置——SLO收紧阈值/DryRunSimulator降频/CostTracker保留全精度/AutoDiagnostics保留实时"
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\construction_phase_tracker.md"
  - "D:\\ZephyrAlpha\\config\\maintenance_mode.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§12"
    reason: "施工前检查规则——先验证 shared/ ✅实现→再决定扩展或独立落地"
  - module_id: "MOD-INF-002"
    section: "§6.1"
    reason: "Phase∞维护期SLO收紧——DryRun仅对新写操作100%覆盖+部分RI降频运行"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§12 施工指引完整施工表——Phase 1a~Phase ∞ 全部27步骤"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45
acceptance_criteria:
  - "施工前检查: 逐条核对 shared/ 下10个已实现文件——标注已满足/需扩展/不满足"
  - "Phase 1a: 5步骤完成——RI-02/03/04/08四模块联调+结构化并发验证"
  - "Phase 1b: 4步骤完成——EventBus/IdempotencyGuard/Telemetry集成测试+背压压测"
  - "Phase 2a: 5步骤完成——七合一韧性+Secrets+Health+Cache全链路混沌实验"
  - "Phase 2b: 5步骤完成——AutoDiagnostics/DryRunSimulator/CostTracker独立落地+可视化"
  - "Phase 3: 3步骤触发式——EventStore→L04/L05/L06切ES→Crypto-Shredding验证"
  - "Phase 4: 2步骤触发式——SagaCoordinator→补偿验证"
  - "Phase ∞: 3步骤——SLO收紧+降频配置+维护期确认"
rollback_instructions: |
  1. 删除 construction_phase_tracker.md
  2. 删除 config/maintenance_mode.yaml
depends_on: []
blocked_by: []
status: "created"
tags_fn:
  - "infra"
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
