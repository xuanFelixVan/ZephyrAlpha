---
task_id: "TASK-INF-0232"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 depends_on + references——模块依赖验证 + Phase scaffold 全量集成测试"

title: "依赖验证与全量集成测试——depends_on 5 模块 + references 7 模块 + Phase scaffold E2E"
description: |
  验证蓝图声明的所有 depends_on 和 references 模块的集成：
  depends_on 验证：
  - MOD-INF-012(Database)→SQLite 派生查询索引可用性
  - MOD-INF-007(Gate Engine)→门禁决策审计记录读取
  - MOD-INF-002(Runtime)→RI-13/14/15 联动
  - MOD-INF-016(Shared Core)→EventType+Task Schema+韧性基座
  - GOV-CMP-002(审计策略)→AUD-001~004 合规
  - GOV-CMP-003(治理审计协议)→12 维度对齐
  
  references 验证：
  - MOD-INF-023(漂移检测)/015(遥测)/010(FLE)/ADR-0010/KB-001/022(Escalation)
  
  全量 Phase scaffold E2E 集成测试：
  1. 端到端流程——Agent操作→AuditWriter→JSONL→IntegrityVerifier→CLI→ExternalVerifier
  2. 性能基准：1000 条 < 5s 写入, 10000 条完整性校验 < 5s
  3. 并发测试：3 IDE 同时写入 100 条——无冲突无丢数据
  4. 故障恢复：JSONL 中断 → 自动回退 → 索引重建
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\gate-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\compliance\\audit-trail-policy.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_integration.py"
    description: "全量集成测试——E2E流程+性能基准+并发"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_dependency_check.py"
    description: "依赖模块存在性验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_integration.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_dependency_check.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "集成测试需审计记录"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "depends_on + references 全表"

assigned_model: "deepseek"
assigned_pipeline: "B"
pipeline_modules:
  - "M1"
  - "M3"
  - "M7"
estimated_tokens: 10000
timeout_minutes: 60

acceptance_criteria:
  - "depends_on 6 模块全部存在且接口可调用——无 ImportError"
  - "references 7 模块的 module_id 存在于注册表"
  - "E2E: Agent操作→写入→查询→校验→CLI 全链路 < 5s"
  - "并发 3 IDE × 100 条 = 300 条目——零丢失"
  - "故障注入：删除中间条目 → integrity_failure 事件触发 → P0 告警"
  - "5/5 集成测试通过"

rollback_instructions: |
  1. 删除 test_integration.py / test_dependency_check.py
  2. 清理测试数据

depends_on:
  - "TASK-INF-0209"
  - "TASK-INF-0210"
  - "TASK-INF-0211"
  - "TASK-INF-0213"
  - "TASK-INF-0214"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
