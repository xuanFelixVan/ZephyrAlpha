---
task_id: "TASK-MST-0029"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §三十三 死代码与孤儿文件清理——CT-LEAN-001 + §三十四 蓝图自健康诊断——CT-BLUEPRINT-HEALTH-001"

title: "实现死代码/孤儿文件/僵尸引用三扫描 + 蓝图自身健康度自检"
description: |
  实现 §三十三 CT-LEAN-001 的三层扫描 + §三十四 CT-BLUEPRINT-HEALTH-001 蓝图自健康诊断(orphan_section_scan/secnum_audit/blind_spot_audit)。
  死代码清理：(1)Layer1 dead code——ast walk unreachable code→生成 audit report；
  (2)Layer2 orphaned files——未在 blueprint.md/blueprints.yml 路径表中→WARN；
  (3)Layer3 zombie references——引用文件/dir已不存在→FLE→Orc→生成TaskCard清除。
  .trash/ 机制：move to .trash/ → 30天 not referenced→永久删除。
  蓝图健康：(1)orphan_section_scan——docs/ 文件NONE归属 0→报告→Orc通知；
  (2)secnum_duplicate_audit——§编号重复→Agent hallucination→AGENTS.md声明："若发现重复§→先验证唯一性再继续"；
  (3)GATE-* 一致性——蓝图声明的GATE与实际构成的GATE对齐→GATE-BLUEPRINT-1。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\deadcode_scanner.py"
    description: "死代码扫描器——CT-LEAN-001——3层扫描(L1死代码+L2孤儿+L3僵尸)+.trash/"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\blueprint_health.py"
    description: "蓝图健康检查器——CT-BLUEPRINT-HEALTH-001——orphan_section_scan+secnum_audit+GATE一致性"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_deadcode_scanner.py"
    description: "死代码扫描器单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_blueprint_health.py"
    description: "蓝图健康检查器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\deadcode_scanner.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\blueprint_health.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_deadcode_scanner.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_blueprint_health.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

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
    reason: "§三十三——CT-LEAN-001 + §三十四——CT-BLUEPRINT-HEALTH-001 蓝图自健康诊断完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "deadcode_scanner.py 实现 Layer1(ast walk unreachable)/Layer2(路径表对比)/Layer3(zombie reference) 三层扫描"
  - ".trash/ 目录 recovery→移回原处；30天未引用→DELETE_PERMANENTLY"
  - "blueprint_health.py 实现 orphan_section_scan——docs/ 文件 NONE 归属→WARN"
  - "secnum_duplicate_audit——检测 §编号重复→AGENTS.md 声明验证"
  - "GATE-BLUEPRINT-1——蓝图声明GATE与实际gate构成一致性→GATE mismatch→block deployment"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\deadcode_scanner.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\blueprint_health.py
  3. 删除新增的测试文件
  4. 如有创建 .trash/ 测试文件 → 清理

depends_on: []
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
