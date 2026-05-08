---
task_id: "TASK-INF-0A27"
source_blueprint: "MOD-INF-018"
source_section: "蓝图全量 数据完整性自回归验证"

title: "实现agent-rbac模块数据完整性自回归验证——all integrity self-verification"
description: |
  实现integrity_self_check.py——对agent-rbac模块所有产出物进行完整性自回归验证。
  验证内容：
  1. 代码文件完整性：所有.py文件sha256与预期基线对比
  2. 配置文件完整性：所有YAML配置文件无未签名变更
  3. 测试覆盖率完整性：test_permissions.py攻击向量覆盖+盲点测试覆盖
  4. 决策-实现映射完整性：94项决策均有实现代码
  5. 契约合规性：4项契约(G-CT-001/004/007/008)自动验证
  6. 文件路径索引完整性：蓝图§2中的文件路径索引全部在磁盘存在
  7. Agent Identity Model完整性：5级Maturity/4 IDE source/5 Roles全部有效
  8. Phase门禁完整性：每Phase进入下一Phase前验证前Phase产出完整性
  生成integrity_report.json。
priority: "P3"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\decision_registry.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\integrity_self_check.py"
    description: "IntegritySelfCheck——全模块完整性自回归验证+integrity_report.json生成"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_integrity.py"
    description: "完整性测试——自回归验证+基线对比+CI门禁集成"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\integrity_self_check.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_integrity.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "蓝图全量——数据完整性验证覆盖所有蓝图定义的产出物+决策+契约+盲点+风险+代码块"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "run_all_checks()→返回integrity_report含全部8项验证结果"
  - "code_integrity:所有源文件sha256匹配基线→TAMPERED检测"
  - "decision_coverage:94/94→100%"
  - "blind_spot_coverage:209/209→100%"
  - "contract_compliance:4/4契约验证通过"
  - "file_path_validity:66个文件路径索引全部在磁盘存在"
  - "phase_gate_integrity:上一Phase产出完整性验证通过→允许进入下一Phase"
  - "CI集成:integrity_self_check.py的运行作为CI必过门禁"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\integrity_self_check.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_integrity.py

depends_on:
  - "TASK-INF-0A13"
  - "TASK-INF-0A25"
  - "TASK-INF-0A26"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "quality"
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
