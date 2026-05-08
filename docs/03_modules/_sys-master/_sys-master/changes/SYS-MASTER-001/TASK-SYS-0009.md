---
task_id: "TASK-SYS-0009"
source_blueprint: "SYS-MASTER-001"
source_section: "§13 数据安全与分级 + §14 启动/停机拓扑顺序"

title: "L1-L4 数据分级治理 + 6阶段(Secrets+DB→Dashboard)启动/停机拓扑骨架"
description: |
  将 SYS-MASTER-001 §13 数据安全与分级 + §14 系统启动/停机顺序工程化落地。
  §13: L1-L4 数据分级——L1 Public/L2 Internal/L3 Confidential/L4 Restricted，
  每级定义加密要求/访问控制/审计日志/保留天数。
  §14: 系统启动 6 Phase 按顺序——
  P1-Secrets+DB / P2-Context+Gate / P3-Market Data / P4-Factor+Signal / P5-OMS+Risk / P6-Dashboard+Telemetry。
  停机逆序——P6→P1。Phase 间 DAG 依赖，前一步健康检查通过→下一步。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_classification.py"
    description: "§13 DataLevel Enum——L1_PUBLIC/L2_INTERNAL/L3_CONFIDENTIAL/L4_RESTRICTED + 每级属性"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\startup_shutdown.py"
    description: "§14 StartupPhase 枚举——P1_SECRETS_DB→P6_DASHBOARD_TELEMETRY + DAG依赖+健康检查门"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\startup_shutdown_cli.py"
    description: "§14 CLI——zephyr-start / zephyr-stop 命令"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_classification.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\startup_shutdown.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\startup_shutdown_cli.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§13 L1-L4 分级 + §14 P1-P6 启动拓扑、DAG依赖、逆序停机"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 16000
timeout_minutes: 45

acceptance_criteria:
  - "DataLevel 枚举 4 成员——每级含 encryption_required/bool+access_control/list+audit_log/bool+retention_days/int"
  - "StartupPhase 枚举 6 成员——P1_SECRETS_DB→P6_DASHBOARD_TELEMETRY——有向 DAG 依赖"
  - "StartupOrchestrator.run() 遍历 DAG→每阶段健康检查通过→下一阶段"
  - "ShutdownOrchestrator.run() 逆序——P6→P1"
  - "CLI argparse: zephyr-start --phases 1-6 / zephyr-stop"

rollback_instructions: |
  git rm src/zephyr/governance/data_classification.py startup_shutdown.py startup_shutdown_cli.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0003"
blocked_by: []
status: "done"
tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
