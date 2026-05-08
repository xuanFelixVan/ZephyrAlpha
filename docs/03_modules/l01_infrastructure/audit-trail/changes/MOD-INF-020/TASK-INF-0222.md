---
task_id: "TASK-INF-0222"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §5.1 AI 行为异常签名——13 种异常检测（决策 D-020-07）"

title: "实现异常检测引擎——13 种 AI 行为异常签名全量检测 + 告警发射"
description: |
  实现 `src/zephyr/audit_trail/anomaly.py` 中的 `AnomalyDetector` 异常检测引擎。
  实现全部 13 种异常签名（ANM-001 ~ ANM-013）：
  ANM-001 越权操作 / ANM-002 批量删除(>5) / ANM-003 门禁跳过 / ANM-004 非工作时间(UTC 22-06, >20/h) /
  ANM-005 高频操作(>100/min) / ANM-006 跨Agent冲突(同文件5min内3+Agent) / ANM-007 审计日志异常(哈希链/HMAC/Ed25519) /
  ANM-008 Agent冒充 / ANM-009 委托链异常 / ANM-010 协同规避 / ANM-011 间接操作规避 /
  ANM-012 信任趋势恶化 / ANM-013 Dry-Run差异异常。
  检测逻辑：每条 AuditEntryV1 写入后触发——各签名检测器独立运行 → anomaly_score 聚合 →
  >0.7 P1 告警 / >0.9 P0 阻断 → 写入 anomaly_detected 事件。
  落地决策 D-020-07。覆盖风险 R7/R13/R14/R15/R16/R17。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\anomaly.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\governance\audit_trail\anomaly.py"
    description: "AnomalyDetector 类——13 种异常签名 + score 聚合 + 告警发射"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_anomaly.py"
    description: "13种异常模拟→检测→告警→全量测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\anomaly.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_anomaly.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-002"
    reason: "异常检测告警规则"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§5.1——13 签名表 + D-020-07"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 75

acceptance_criteria:
  - "13 个检测器可独立启用/禁用（feature flags）"
  - "ANM-001 越权检测：Agent X 操作 Y 文件但 Y 在 forbidden_touch → anomaly_score=0.95"
  - "ANM-002 批量删除：单 task >5 文件删除 → P0"
  - "ANM-006 冲突检测：同文件 5min 内 3+ Agent 写 → auto-lock"
  - "ANM-007 完整性：哈希链断裂 → 立即 P0"
  - "ANM-010 协同：3 Agent 各删 4 文件（总计12>5）→ 检测协同规避"
  - "anomaly_score > 0.7 → P1 alert / > 0.9 → P0 block"
  - "13/13 异常测试通过——每种签名至少 1 个正向 + 1 个负向测试"

rollback_instructions: |
  1. 删除 anomaly.py 内容
  2. 删除 test_anomaly.py

depends_on:
  - "TASK-INF-0209"
  - "TASK-INF-0205"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
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
