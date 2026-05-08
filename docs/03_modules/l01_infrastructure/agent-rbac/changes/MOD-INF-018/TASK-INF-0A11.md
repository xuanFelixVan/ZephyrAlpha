---
task_id: "TASK-INF-0A11"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.10 L7 — Testing & Dry-Run + D-018-12"

title: "实现L7 TestingFramework — 权限影响分析/Dry-Run/自动化测试/对抗性测试"
description: |
  实现dry_run.py和test_permissions.py。权限影响分析：新增/修改权限后自动分析影响哪些Agent/操作。
  Dry-Run模式：模拟执行操作→返回"如果现在执行会是什么判定"而不实际执行。
  自动化测试框架：test_permissions.py含120+攻击向量验证、跨模型一致性测试、
  权限冲突编排、边缘用例枚举(95+用例)。
  对抗性测试：一个专用Agent尝试绕过所有七层+六横切面防护。
  Canary权限灰度(D-018-33)：新权限先测试1%流量→观察24h→自动全量→失败自动回滚。
  实施D-018-12：权限配置=可测试代码——必须自动化验证。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\dry_run.py"
    description: "DryRunSimulator——simulate()/impact_analysis()/DryRunResult"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_permissions.py"
    description: "权限自动化测试框架——120+攻击向量/跨模型一致性/对抗性测试/边缘用例"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_dry_run.py"
    description: "Dry-Run模式测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\dry_run.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_permissions.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_dry_run.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.10 L7 Testing+攻击向量清单+边缘用例+Canary灰度+决策D-018-12/D-018-33"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 14000
timeout_minutes: 60

acceptance_criteria:
  - "dry_run.simulate()返回(decision, blocked_layer, rule_id, correction_suggestion)"
  - "impact_analysis()分析结果含affected_agents/affected_operations/risk_score"
  - "test_permissions.py覆盖>=120个攻击向量"
  - "对抗性测试:专用Agent攻击100次→0次成功绕过"
  - "跨模型一致性:DeepSeek/GLM/Claude对同一规则判定一致率>=95%"
  - "Canary:新权限1%采样+24h观察+P0异常自动回滚"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\dry_run.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_permissions.py
  3. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_dry_run.py

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
