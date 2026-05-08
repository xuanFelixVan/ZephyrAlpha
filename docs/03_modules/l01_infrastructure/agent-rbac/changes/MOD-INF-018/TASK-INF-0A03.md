---
task_id: "TASK-INF-0A03"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.2 L0 — Kill Switch 全局熔断 + D-018-05"

title: "实现L0 KillSwitch — 全局熔断机制"
description: |
  实现kill_switch.py。全局熔断机制：>=9种自动触发器(rapid_file_deletion/unauthorized_protected_write/
  multi_session_anomaly/signal_noise_attack/sensitivity_label_blitz/agent_spawn_storm/
  rollback_storm/clock_tampering/credential_scan_blast)。
  熔断源隔离策略：单Agent触发仅阻断该Agent，多Agent触发才全局熔断。
  触发阈值可配置，auto_cooldown机制，Owner可手动解除。
  实施D-018-05：运营中断系统对标交易系统熔断+CISA ATF Incident Response。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\kill_switch.py"
    description: "KillSwitch类——auto_triggers注册/触发检测/cooldown/Owner手动解除"

  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_kill_switch.py"
    description: "测试——验证所有触发器/熔断源隔离/cooldown/手动解除"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\kill_switch.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_kill_switch.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.2 Kill Switch完整定义+9种auto_triggers+熔断源隔离策略+决策D-018-05"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "KillSwitch注册的auto_triggers数量>=9种"
  - "rapid_file_deletion触发器在1分钟内>20次删除触发熔断"
  - "signal_noise_attack触发器在噪音比>10:1时触发"
  - "单Agent触发仅阻断该Agent(非全局)"
  - "多Agent(>=3)同时触发才全局熔断"
  - "cooldown默认300s后自动尝试解除"
  - "Owner可手动解除全局熔断"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\kill_switch.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_kill_switch.py
  3. 如immutable_core.py引用了KillSwitch——移除引用并恢复原始版本

depends_on:
  - "TASK-INF-0A02"
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
