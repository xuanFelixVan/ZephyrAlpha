---
task_id: "TASK-MST-0005"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §三 共享Schemas——TaskCard/Finding/KE + CTR-VER-001 版本协商"

title: "实现共享 Schema 版本协商机制(CTR-VER-001)并嵌入 schema_version 字段"
description: |
  为 §三 的 3 个共享 Schema(TaskCard/Finding/KE)嵌入 schema_version 字段和 version_negotiation 规则。
  核心：(1) 新增字段遵循 forward-compat——双版本过渡期机制；
  (2) 删除字段遵循 deprecation 流程——标记 @deprecated → 2 MAJOR 版本后移除；
  (3) 类型变更 → BREAKING → 2 版本过渡期；
  (4) 每个 Schema 在运行时协商版本——消费者声明 max_supported_version，生产者按 min(producer, consumer) 降级返回。
  使 TaskCard 28 字段模型与 metadata-registry.md §7.1 保持一致。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\version_negotiation.py"
    description: "版本协商器——CTR-VER-001——Schema版本升级/降级/过渡期管理"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_version_negotiation.py"
    description: "版本协商单元测试——forward-compat + deprecation 流程验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\version_negotiation.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_version_negotiation.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

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
    reason: "§三——3个共享Schema + CTR-VER-001 版本协商规则定义"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    reason: "§7.1——TaskCard 28字段真源定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "version_negotiation.py 实现 CTR-VER-001 的 forward-compat(新增可选字段)和 backward-compat(2版本过渡期)"
  - "Schema version negotiation: 消费者声明 max_supported_version，生产者返回 min(producer, consumer)"
  - "BREAKING 变更（字段删除/类型修改）→ 自动标记 @deprecated → 2 MAJOR 版本后移除"
  - "运行时 Schema 版本不匹配 → 降级处理 → 创建 DOC_INCONSISTENCY Finding"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\version_negotiation.py
  2. 删除 D:\ZephyrAlpha\tests\unit\test_version_negotiation.py

depends_on: []
blocked_by: []

status: "done"

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
