---
task_id: "TASK-INF-0224"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §5.3 三角闭环反馈（决策 D-020-08）+ §5.4 外部调用链（D-020-20）+ §5.5 间接操作（D-020-21）+ §5.6 反馈自审计（D-020-26）"

title: "实现三角闭环反馈聚合器 + 外部调用链审计 + 间接操作检测 + 反馈自指循环检测"
description: |
  实现 Phase experimental 阶段的四大检测/反馈组件：
  1. `FeedbackAggregator`(§5.3): daily 聚合 top_anomalies/drift_summary/permission_trends/cost_anomalies →
     生成 Markdown policy_evolution_pr_body → 对接 feedback_to_policy.py
  2. `ExternalToolCallAudit`(§5.4): trace_call_chain() 追溯 Agent→MCP→API 调用链,
     detect_call_loop() 无限递归检测, blame_boundary() 故障边界判定
  3. `IndirectOperationDetector`(§5.5): scan_generated_scripts() 可执行脚本检测,
     correlate_write_execute() 写入→执行关联, trace_indirect_path() symlink/cron 路径追踪
  4. `FeedbackSelfAudit`(§5.6): detect_self_reinforcement() Policy 自指检测 0.0~1.0,
     validate_evolution_direction() forward/backward/self_reinforcing 方向判定
  落地 D-020-08/20/21/26。覆盖 R10/R15/R17/R19。覆盖盲点 B25/B26/B34。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\feedback.py"
    description: "FeedbackAggregator——每日审计聚合 + Policy PR 体生成"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\external_call_audit.py"
    description: "ExternalToolCallAudit——外部 MCP/API 调用链审计"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\indirect_op.py"
    description: "IndirectOperationDetector——间接操作路径追踪"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\feedback_self_audit.py"
    description: "FeedbackSelfAudit——自指循环检测"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_feedback.py"
    description: "反馈/外部调用/间接操作/自指检测测试"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_external_call_audit.py"
    description: "外部调用链审计测试"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_indirect_op.py"
    description: "间接操作检测测试"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_feedback_self_audit.py"
    description: "反馈自指检测测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\external_call_audit.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\indirect_op.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\feedback_self_audit.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_feedback*.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_external_call_audit.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_indirect_op.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "反馈推送需记录为审计事件"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§5.3~§5.6——反馈/外部调用/间接操作/自指 + D-020-08/20/21/26"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 14000
timeout_minutes: 90

acceptance_criteria:
  - "FeedbackAggregator.daily_report() → 输出 Markdown（top10 anomalies + drift + trends）"
  - "ExternalToolCallAudit.trace_call_chain() → 完整调用链（Agent → MCP → API）"
  - "ExternalToolCallAudit.detect_call_loop() → 递归链 A→MCP→B→MCP→A → True"
  - "IndirectOperationDetector 检测 symlink 路径 → /tmp/secret → ~/.ssh/id_rsa"
  - "IndirectOperationDetector 检测写入→5s内执行 → 关联度 > 0.8"
  - "FeedbackSelfAudit 检测 Policy 自指 → score > 0.7 → human_gated"

rollback_instructions: |
  1. 删除 feedback.py / external_call_audit.py / indirect_op.py / feedback_self_audit.py
  2. 删除对应测试文件

depends_on:
  - "TASK-INF-0222"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "semi_autonomous"
autonomy_checklist: []
---
