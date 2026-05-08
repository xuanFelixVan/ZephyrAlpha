---
task_id: "TASK-INF-0A06"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.5 L2 — ABAC 属性权限 + D-018-07"

title: "实现L2 ABACGuard — 五维属性权限(intent/maturity/temporal/sensitivity/tlb)"
description: |
  实现abac_guard.py。五维ABAC判定：意图感知(intent)、Agent Maturity四级信任、
  时间窗口(off_hours降级+lunch_peak限制)、资源敏感性(label)、per-Agent TLB限流。
  Maturity四级信任对应不同操作带宽。
  敏感标签篡改检测——sensitivity_label_blitz熔断+标签变更审计+自动还原。
  实施D-018-07：意图感知+时间窗口+成熟度+敏感性四维——从"谁"升级到"什么上下文"。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\rbac_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\abac_guard.py"
    description: "ABACGuard——intent_aware/temporal_window/maturity_based/sensitivity_aware/tlb_limiter五维判定"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_abac_guard.py"
    description: "测试五维判定——off_hours自动切换/TLB限流/sensitivity降级"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\abac_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_abac_guard.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.5 ABAC+D-018-07完整规范——五维ABAC+TLB+Maturity+资源敏感性+sensitivity_label_blitz防护"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 14000
timeout_minutes: 60

acceptance_criteria:
  - "ABAC维度>=5(intent/temporal/maturity/sensitivity/tlb)"
  - "off_hours(22:00-08:00+weekend)自动将auto_guard降级为blocked"
  - "Maturity L0_INTERN在off_hours完全blocked"
  - "per-Agent TLB默认：L1=100/L2=500/L3=2000/L4=10000"
  - "sensitivity_label_blitz检测：1分钟内>5次标签变更触发Kill Switch"
  - "资源敏感性从frontmatter读取——high_sensitivity文件仅L3+可写"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\abac_guard.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_abac_guard.py

depends_on:
  - "TASK-INF-0A05"
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
