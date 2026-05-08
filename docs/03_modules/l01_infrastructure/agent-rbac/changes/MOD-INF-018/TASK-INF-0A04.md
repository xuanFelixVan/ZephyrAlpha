---
task_id: "TASK-INF-0A04"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.3 L0 — Engine 降级策略 + D-018-06"

title: "实现L0 EngineDegradation — 权限引擎降级策略与降级攻击防护"
description: |
  实现PermissionEngine的降级策略。核心原则：崩=blocked(安全检查失败→默认拒绝)。
  降级攻击检测：同一Agent触发的降级→立即BLOCKED(D-018-17联动)。
  Partial failure持续>1小时→自动升级为P0告警。
  实施D-018-06：负面偏好——权限系统故障时安全优先于便利。
  对标Perplexity cascading failures + NVIDIA多Agent健康检测。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\kill_switch.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\engine_degradation.py"
    description: "EngineDegradationManager——降级状态机/降级源检测/PartialFailure监控/恢复策略"

  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_engine_degradation.py"
    description: "测试——验证崩=blocked/降级攻击检测/PartialFailure升级/恢复流程"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\engine_degradation.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_engine_degradation.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.3降级策略+D-018-06决策+降级攻击检测逻辑"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "Engine异常时所有check()返回PERMISSION_BLOCKED"
  - "降级源检测:同一Agent触发>=2次降级→该Agent立即BLOCKED"
  - "PartialFailure持续>3600s→自动升级为P0告警"
  - "Engine恢复后运行完整性验证再恢复ALLOW"
  - "Owner可手动将降级状态恢复到正常模式"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\engine_degradation.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_engine_degradation.py

depends_on:
  - "TASK-INF-0A02"
  - "TASK-INF-0A03"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
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
