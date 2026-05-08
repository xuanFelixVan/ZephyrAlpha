---
task_id: "TASK-MST-0012"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十三 端到端场景走查——8步完整OPS修复全流程"

title: "实现端到端场景走查验证器——8步OPS修复全流程集成测试"
description: |
  实现 §十三 端到端场景走查的自动化验证器：
  走查从 Finding→TaskCard 创建→上下文构建→管线选路→AI 执行→Script System 判定→门禁→FLE，
  完整覆盖 11/13 条 CT-* 合同。
  核心功能：(1)自动化重跑 8 步完整流程并验证每一步的 CT-* 契约执行正确；
  (2)验证 CE build→compress→validate→inject 四阶段正确性；
  (3)验证 exit code 0→GATE PASS 路径；
  (4)验证 MEDIUM Finding→KE 自动入库→VMS embedding 生成路径；
  (5)生成端到端 trace report——包含每步耗时、涉及的 CT-*、门禁结果。

priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_router.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\e2e_walkthrough.py"
    description: "端到端场景走查验证器——8步OPS修复全流程自动化验证"
  - path: "D:\\ZephyrAlpha\\tests\\integration\\test_e2e_walkthrough.py"
    description: "端到端场景走查集成测试——验证 11/13 CT-* 合同协同"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\e2e_walkthrough.py"
  - "D:\\ZephyrAlpha\\tests\\integration\\test_e2e_walkthrough.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§十三——8步完整OPS修复全流程 + 涉及的CT-*合同(11/13)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M5"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "e2e_walkthrough.py 自动化重跑 8 步完整 OPS 修复流程"
  - "每一步验证对应 CT-* 契约执行正确（Orc→CE→Pipeline→AI Agent→Script System→Gates→FLE）"
  - "生成 trace report——包含每步耗时、CT-* 编号、门禁结果"
  - "模拟 Finding(severity=MEDIUM, type=BUG_FIX)→自动走完全流程"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\e2e_walkthrough.py
  2. 删除 D:\ZephyrAlpha\tests\integration\test_e2e_walkthrough.py

depends_on: ["TASK-MST-0004"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
