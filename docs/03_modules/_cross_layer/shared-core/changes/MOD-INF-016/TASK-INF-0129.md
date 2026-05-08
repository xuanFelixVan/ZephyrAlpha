---
task_id: "TASK-INF-0129"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §5.2 测试文件索引——test_import_chain + test_auto_contract_tester"

title: "§5.2 契约测试维护——test_import_chain.py 更新 + auto_contract_tester 适配 Phase 11-20"
description: |
  维护蓝图 §5.2 中的测试文件索引，适配 Phase 11-20 新增模块。
  test_import_chain.py 当前覆盖 shared/ 基础导入链，但不覆盖 Phase 11-20 的 30+ 新模块。
  要求：
  1. test_import_chain.py 新增 Phase 11-20 所有新 shared/ 模块的 import 测试。
  2. test_auto_contract_tester.py 新增 B26-B56 盲点对应的契约校验用例。
  3. 更新蓝图 §5.2 的测试文件数——从 21 增加到 ≥26（Phase 11-20 新增 5-8 个测试文件）。
  4. 所有新测试文件放在对应的 tests/unit/ 位置，符合文件结构标准。
  专业对标：ZephyrAlpha Test Contract + auto_contract_tester。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
  - "D:\\ZephyrAlpha\\tests\\test_auto_contract_tester.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\tests\contract\test_import_chain.py"
    description: "新增 Phase 11-20 模块 import 测试（cost_budget/context_budget/evals/session_audit/...）"
  - path: "D:\\ZephyrAlpha\\tests\\test_auto_contract_tester.py"
    description: "新增 B26-B56 盲点对应契约校验用例"

allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
  - "D:\\ZephyrAlpha\\tests\\test_auto_contract_tester.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5.1.1"
    reason: "API_INDEX.py——test_import_chain BUG——遗忘了 22 枚举"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §5.2——测试文件索引与维护规则"
  - file_path: "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
    reason: "test_import_chain.py——需要更新以覆盖 Phase 11-20"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 8000
timeout_minutes: 20

acceptance_criteria:
  - "test_import_chain.py: Phase 11-20 的 5 核心模块 import 测试通过"
  - "test_auto_contract_tester.py: B26-B56 盲点对应的契约校验用例通过"
  - "蓝图 §5.2 测试文件数更新 ≥26（从 21）"
  - "pytest tests/test_import_chain.py -v 全部通过"
  - "pytest tests/test_auto_contract_tester.py -v 全部通过"

rollback_instructions: |
  1. git checkout -- tests/test_import_chain.py
  2. git checkout -- tests/test_auto_contract_tester.py

depends_on: ["TASK-INF-0107"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
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
