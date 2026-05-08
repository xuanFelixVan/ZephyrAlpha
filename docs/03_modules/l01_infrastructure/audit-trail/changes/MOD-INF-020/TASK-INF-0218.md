---
task_id: "TASK-INF-0218"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §7 Phase scaffold 验收标准——测试要求 + §3.2 tests/ 目录"

title: "搭建测试基础设施——tests/audit_trail/ 目录 + conftest + fixtures + test data"
description: |
  创建 `tests/audit_trail/` 测试目录及测试基础设施：
  - `conftest.py`: 共享 fixtures——sample entries/临时 JSONL 文件/sandbox writer & query
  - `fixtures.py`: 预定义测试数据——合法的 AuditEntryV1 样本（覆盖 31 种事件类型）
  - `data/`: 测试用 JSONL 样本文件
  - 所有测试文件 skeleton：test_models.py / test_writer.py / test_query.py / test_integrity.py / test_agent_signer.py / test_lamport.py / test_self_monitor.py / test_cli.py / test_meta_audit.py
  - 注册到 script_manifest.yaml（按 AGENTS.md §6.5）
  对标蓝图 §7 Phase scaffold 验收标准 #5——5/5 单元测试通过。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\tests\\conftest.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\scripts\__init__.py"
    description: "测试包入口"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\conftest.py"
    description: "共享 fixtures——临时文件/写入器实例/示例条目"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\fixtures.py"
    description: "预定义测试数据——覆盖 31 事件类型"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\data\\"
    description: "测试 JSONL 样本数据目录"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_models.py"
    description: "模型单元测试骨架"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_writer.py"
    description: "写入器单元测试骨架"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_query.py"
    description: "查询接口单元测试骨架"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_integrity.py"
    description: "完整性验证单元测试骨架"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_agent_signer.py"
    description: "Agent 签名单元测试骨架"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_lamport.py"
    description: "Lamport 时钟单元测试骨架"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_self_monitor.py"
    description: "自监控单元测试骨架"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_cli.py"
    description: "CLI 集成测试骨架"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_meta_audit.py"
    description: "元审计单元测试骨架"

allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\**\\*.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\data\\**\\*"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\data\\audit\\**\\*"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "测试路径 tests/audit_trail/ 合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§3.2——tests/ 目录结构 + §7 scaffold 验收标准 #5"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 5000
timeout_minutes: 30

acceptance_criteria:
  - "tests/audit_trail/ 含 __init__.py + conftest.py + fixtures.py + data/ 目录"
  - "conftest.py 含 sample_entry fixture——生成合法 AuditEntryV1"
  - "fixtures.py 含 31 种事件类型各一条样本数据"
  - "10 个 test_*.py 骨架文件存在——可被 pytest 发现"
  - "pytest tests/audit_trail/ --collect-only 成功发现所有测试文件"

rollback_instructions: |
  1. 删除 tests/audit_trail/ 目录及所有子文件

depends_on:
  - "TASK-INF-0200"
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
