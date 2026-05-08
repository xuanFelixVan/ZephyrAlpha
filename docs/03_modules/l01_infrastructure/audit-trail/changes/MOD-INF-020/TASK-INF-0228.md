---
task_id: "TASK-INF-0228"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 DOM-GOV-001 集成契约锚点——G-CT-001/002/007"

title: "实现 DOM-GOV-001 集成契约——G-CT-001（RBAC 判定消费）/G-CT-002（异常→Rollback）/G-CT-007（Spec 执行审计）"
description: |
  实现 audit_trail 与 DOM-GOV-001 三条集成契约的运行时代码：
  - G-CT-001(MOD-INF-018 RBAC): audit_trail 作为消费方——记录每次 RBAC 判定事实
    (Agent X 请求 权限 Y → Gate Engine 判定 PASS/FAIL → audit entry TYPE=PERMISSION_VIOLATION if fail)
  - G-CT-002(MOD-INF-021 Rollback): audit_trail 作为产出方——
    anomaly_score > 0.9 或 drift_severity=critical → 触发 rollback 信号 → 
    Rollback Engine 接收并启动撤销流程
  - G-CT-007(MOD-INF-019 Agent Spec): audit_trail 作为消费方——
    Agent Spec 执行记录 → 蓝图预期 vs 实际操作对比 → drift detection 输入
  功能层级：Phase scaffold G-CT-001 基础消费, Phase experimental G-CT-002/G-CT-007 全量。
  落地 3 条集成契约。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\integrations.py"
    description: "DOM-GOV-001 集成契约运行时实现——3 条契约"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_integrations.py"
    description: "集成契约测试——RBAC事件消费/Rollback信号发射/Spec漂移检测"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\integrations.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_integrations.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rbac\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "集成操作审计留痕"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "DOM-GOV-001 契约表——G-CT-001/002/007"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rbac\\blueprint.md"
    reason: "MOD-INF-018——RBAC 判定接口"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback\\blueprint.md"
    reason: "MOD-INF-021——Rollback 信号接收"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 50

acceptance_criteria:
  - "G-CT-001: RBAC PERMISSION_VIOLATION → audit entry written with rule_violated"
  - "G-CT-002: anomaly_score > 0.9 → rollback_signal emitted to MOD-INF-021"
  - "G-CT-007: Agent Spec execution → blueprint vs actual comparison → drift report"
  - "3/3 契约双向集成测试通过"
  - "集成失败 → 不影响审计系统主流程（degraded gracefully）"

rollback_instructions: |
  1. 删除 integrations.py 内容
  2. 删除 test_integrations.py
  3. 确认 RBAC/Rollback 模块无对 audit_trail.integrations 的残留引用

depends_on:
  - "TASK-INF-0222"
  - "TASK-INF-0223"
blocked_by: []

status: "done"

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
