---
task_id: "TASK-INF-0118"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §9 R2 风险——CirDep-INF-021"

title: "§9 R2 缓解——循环依赖防护验证：CircularImportGuard + contract interception circuit breaker"
description: |
  缓解蓝图 §9 R2 风险——CirDep-INF-021 循环依赖未被所有可能的 import 路径覆盖。
  shared/ 包含 46 文件，彼此间存在无形依赖——简图 CirDep-INF-021 记录的循环尚不在现有 CT 测试中。
  需实现：
  1. 扩展 test_import_chain.py——添加 CirDep-INF-021 记录的 3 条 import 路径验证。
  2. 实现 CircularImportGuard——AST 级 import 路径追溯，在 CI pipeline 中断熔断。
  3. 集成 contract interception circuit breaker——3 次 fail 后 mark 为 DEP-INF-021 并告警。
  专业对标：Python import-linter + ZephyrAlpha auto_contract_tester + Ruff AST。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ssot_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cir_dep_guard.py"
    description: "CircularImportGuard——AST 进口路径追溯 + CI 熔断"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_cir_dep_guard.py"
    description: "单元测试——验证 3 条 CirDep-INF-021 路径检测"
  - path: "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
    description: "新增 CirDep-INF-021 3 条 import 路径测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cir_dep_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_cir_dep_guard.py"
  - "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ssot_guard.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5.1"
    reason: "API_INDEX.py——共享包合法性清单——CirDep-INF-021 是已知未合法单元"
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——cir_dep_guard 被 ≥2 个 L01 模块消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §9——R2 CirDep-INF-021 详情与缓解策略"
  - file_path: "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
    reason: "test_import_chain.py——需要新增 3 条 CirDep-INF-021 import 路径测试"

assigned_model: "claude-sonnet-4.6"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 40

acceptance_criteria:
  - "cir_dep_guard.py: analyze_imports(module_path)——返回 ImportGraph"
  - "cir_dep_guard.py: detect_circular()——检测 CirDep-INF-021 中 3 条循环路径"
  - "cir_dep_guard.py: ContractInterceptionCB——3 次 fail 后标记为 DEP-INF-021"
  - "test_import_chain.py 新增 3 条 CirDep-INF-021 import 路径测试"
  - "pytest tests/unit/test_cir_dep_guard.py -v 全部通过"
  - "CI/CD 中 cir_dep_guard 集成成功——python shared/cir_dep_guard.py check-all"
  - "SHARED-QUICKREF.yml 更新——新增 cir_dep_guard 入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\cir_dep_guard.py
  2. 删除 D:\ZephyrAlpha\tests\unit\test_cir_dep_guard.py
  3. git checkout -- tests/test_import_chain.py
  4. 还原 __init__.py 对应导出
  5. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0101"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-sonnet-4.6"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
