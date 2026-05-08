---
task_id: "TASK-INF-0207"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 2.2 + §6.2 B6/B8 + 决策 D-021-10 + AP3/AP6"

title: "Loop Detector + Agent Cooldown 实现——回滚震荡防护"
description: |
  实现 rollback_loop_detector.py——同一 (task_id, gate_id) 组合触发回滚 >3 次/h → 暂停 agent 自动回滚权限 + DEFER_TO_HUMAN。
  实现 agent_cooldown.py——回滚后 5min 禁止修改被回滚文件，cooldown 状态绑定到 Agent Identity session token。
  rollback_quarantine.db 记录 (agent_session, file_path, until_iso)。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_loop_detector.py"
    description: "循环检测器——同一(task, gate)组合 >3次/h → 暂停 + 升级"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\agent_cooldown.py"
    description: "Agent 隔离器——回滚后 5min 禁止修改被回滚文件"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_loop_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\agent_cooldown.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.2 B6/B8 盲点 + §8 AP3/AP6 Anti-Patterns + D-021-10 回滚预算决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "loop_detector 维护 (task_id, gate_id, timestamps) 滑动窗口记录"
  - "同一组合 >3 次/h → 暂停该 agent 自动回滚权限 → DEFER_TO_HUMAN → 通知 Owner"
  - "agent_cooldown 回滚后自动施加 5min 冷却期"
  - "cooldown 状态绑定 Agent Identity session token——跨 IDE 追踪（B28）"
  - "auto_rollback_trigger 执行前校验 cooldown 状态"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_loop_detector.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\rollback\agent_cooldown.py

depends_on:
  - "TASK-INF-0205"
blocked_by: []
status: "done"

tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-021"]

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
