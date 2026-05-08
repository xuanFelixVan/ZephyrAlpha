---
task_id: "TASK-INF-0A10"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.9 L6 — Observability 可观测性 + D-018-11"

title: "实现L6 Observability — OpenTelemetry指标上报与行为异常检测规则"
description: |
  实现observability.py。OpenTelemetry指标上报：d2.authz.decision.*指标(按agent_id/permission_level/decision分组)、
  延迟histogram、告警信噪比监控(noise_to_signal_ratio)、指标完整性校验(上报代码哈希比对+自身受L0保护)。
  行为异常检测规则(anomaly_detection)：操作密度突增/非工作时间批量操作/Maturity不合理升级行为。
  实施D-018-11：权限系统自身必须可观测——OpenTelemetry标准。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\observability.py"
    description: "ObservabilityReporter——OTEL exporter/metrics/anomaly_detection/signal_noise_monitor/metric_integrity"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_observability.py"
    description: "测试——指标上报验证/信噪比监控/异常检测触发/完整性自检"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\observability.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_observability.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.9 L6 Observability+OpenTelemetry标准+信噪比监控+异常检测+指标完整性+决策D-018-11"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "OpenTelemetry Exporter正确上报d2.authz.decision.*指标"
  - "decision_counter{agent,level,decision}按时序采集"
  - "signal_noise_ratio:噪音>10:1持续5分钟→触发P1告警"
  - "anomaly_detection:凌晨3点批量删除→标记异常→AUTO_GUARD"
  - "metric_integrity:上报代码哈希与预期不一致→标记TAMPERED"
  - "L6自身上报代码纳入L0 protected_paths"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\observability.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_observability.py
  3. 移除OpenTelemetry导出配置(如在config中)

depends_on:
  - "TASK-INF-0A02"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
  - "observability"
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
