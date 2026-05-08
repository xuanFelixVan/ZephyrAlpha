---
task_id: "TASK-INF-0A13"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.14 Permission Guard 七层+六横切面运行时检查核心API"

title: "实现PermissionGuard核心编排器——七层+六横切面运行时check()入口"
description: |
  实现permission_guard.py——七层纵深防御+六横切面的统一编排。
  check(action, agent)→遍历L0→L1→L2→L3→L4→L5→L6→L7
  →各层返回(ALLOW|AUTO_GUARD|BLOCKED)→按优先级合并→
  →Hook系统注入(pre/post/on_blocked/on_kill_switch)→
  →结果写入审计日志(Audit Trail)→返回最终判定。
  单次check() < 1.8ms总预算(含全链检查)。
  对齐§2.0的总览模型 + §2.14的完整执行流。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\kill_switch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\engine_degradation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\rbac_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\abac_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\input_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\sequence_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\output_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\observability.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\dry_run.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"
    description: "PermissionGuard统一编排器——check()入口/七层遍历/Hook注入/审计写入"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_permission_guard.py"
    description: "PermissionGuard端到端测试——全链check()/延迟<1.8ms/Hook编排/审计日志"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_permission_guard.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.0七层总览+§2.14执行流+L0→L7编排+横切面A/B/C/D/E/F集成点"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "check(action, agent)→遍历L0→L7→返回PermissionResult"
  - "L0(ImmutableCore+KillSwitch+Degradation)→L1(RBAC)→L2(ABAC)→L3→L4→L5→L6→L7顺序执行"
  - "单次check()平均延迟 < 1.8ms (pytest基准测试)"
  - "各层全PASS→PermissionResult.ALLOW"
  - "任一层BLOCKED→短路返回BLOCKED+拒绝原因(ruled_id,layer)"
  - "AUTO_GUARD→执行→post_action_verifier验证→失败记录"
  - "每个判定写入审计日志(MOD-INF-020)"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\permission_guard.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_permission_guard.py

depends_on:
  - "TASK-INF-0A02"
  - "TASK-INF-0A03"
  - "TASK-INF-0A04"
  - "TASK-INF-0A05"
  - "TASK-INF-0A06"
  - "TASK-INF-0A07"
  - "TASK-INF-0A08"
  - "TASK-INF-0A09"
  - "TASK-INF-0A10"
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
