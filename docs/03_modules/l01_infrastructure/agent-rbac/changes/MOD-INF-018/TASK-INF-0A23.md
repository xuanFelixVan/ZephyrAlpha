---
task_id: "TASK-INF-0A23"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §5 — 施工 Phase 规划（21个Phase）"

title: "执行agent-rbac施工Phase规划——scaffold到polish全生命周期21个阶段"
description: |
  执行蓝图§5表格定义的完整施工Phase规划（严格按蓝图原文）：
  - scaffold L0 ImmutableCore: protected_paths+always_blocked+Engine降级→immutable_core.py (P0)
  - scaffold L1 RBAC: GOV-AI-001→rbac_roles.yaml派生+AgentIdentity(MaturityLevel)+PermissionGuard骨架→identity.py+rbac_guard.py+derive_rbac_roles.py (P0)
  - scaffold L4 SequenceGuard: 会话级序列追踪+forbidden_sequences基础规则集→sequence_guard.py (P0)
  - experimental: 完整三层权限执行(L1 always_allow/auto_guard/blocked)+L4序列阻断+Gate Engine集成+Kill Switch→permission_guard.py编排L0→L4 (P0)
  - experimental L2 ABAC: 意图感知+Agent Maturity四级信任+时间窗口(off_hours降级)→abac_guard.py (P1)
  - experimental L3 InputGuard: 参数schema白名单+危险模式检测+路径白名单→input_guard.py (P1)
  - beta: 多IDE统一身份+MCP权限检查+权限漂移检测→全链路集成 (P2)
  - beta L6 Observability: OpenTelemetry指标+行为异常检测规则→observability.py (P2)
  - beta L7 Testing: 权限影响分析+Dry-Run+自动化测试框架→dry_run.py+test_permissions.py (P2)
  - stable L5 OutputGuard: PII脱敏+凭证检测+大小截断→output_guard.py (P3)
  - enhance D-018-13: SessionToken签名校验+AgentIdentityVerifier+跨Session伪造检测→identity.py扩展+cross_session_detector.py (P0)
  - enhance D-018-14: startup_lock+maintenance_mode+校验序列→immutable_core.py扩展 (P0)
  - enhance D-018-15: 四类钩子注册表+预置9个钩子(H01-H09)→permission_hooks.py+permission_hooks.yaml (P0)
  - enhance D-018-16: creation_policy+遗传衰减+生命周期管理→agent_creation_policy.yaml+rbac_guard.py扩展 (P1)
  - enhance D-018-17: 推送驱动缓存失效+降级攻击防护→cache_invalidation.py+cache_policy.yaml (P1)
  - enhance D-018-18: JIT越权+Owner CLI+一次性Token→emergency_override.py (P1)
  - polish D-018-19: 规则效果评估+僵尸规则检测+复杂度预算+Owner仪表盘→auto_maintenance.yaml+health_dashboard.yaml (P2)
  - polish Owner缺席策略: 超时审阅→保守模式→ownership_absence_policy.yaml (P2)
  - polish 跨模型一致性测试: DeepSeek/GLM/Claude对同权限规则判定一致性→L7扩展 (P2)
  - polish 对抗性测试: 一个专用Agent尝试绕过所有七层+六横切面→L7扩展 (P2)
  - polish 定期审计报告: 每周自动生成+交付→cronjob+report template (P2)
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-lifecycle-standard.md"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\phase_executor.py"
    description: "Phase执行编排器——21个Phase顺序/依赖/门禁/关键交付物/优先级"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\phase_executor.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"
  - module_id: "TLC-STD-002"
    section: "§4"
    reason: "任务生命周期门禁——每Phase通过门禁才能进入下一Phase"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§5 施工Phase规划表——21个Phase+6个施工等级+交付物+优先级"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 16000
timeout_minutes: 60

acceptance_criteria:
  - "phase_executor注册全部21个Phase——严格按蓝图§5表格"
  - "每Phase定义:施工等级(scaffold/experimental/beta/stable/enhance/polish)/任务描述(蓝图原文)/关键交付物/优先级"
  - "Phase执行顺序:scaffold→experimental→beta→stable→enhance→polish不可跳跃"
  - "scaffold 3个Phase→L0 ImmutableCore(immutable_core.py)+L1 RBAC(identity+rbac_guard+derive_rbac)+L4 SequenceGuard(sequence_guard.py)"
  - "experimental 3个Phase→PermissionGuard编排(permission_guard.py)+L2 ABAC(abac_guard.py)+L3 InputGuard(input_guard.py)"
  - "beta 3个Phase→多IDE集成+L6 Observability(observability.py)+L7 Testing(dry_run+test_permissions)"
  - "stable 1个Phase→L5 OutputGuard(output_guard.py)"
  - "enhance 6个Phase→D-018-13/14/15/28/17/18"
  - "polish 5个Phase→D-018-19+缺席策略+一致性测试+对抗测试+定期报告"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\phase_executor.py
  2. 如有Phase执行状态持久化数据——删除

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "planning"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-018"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
