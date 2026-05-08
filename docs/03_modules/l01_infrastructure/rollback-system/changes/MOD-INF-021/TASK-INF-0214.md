---
task_id: "TASK-INF-0214"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 3.5 + §6.2 B19 + §8 Anti-Patterns"
title: "Anti-Patterns 落地——AP1~AP44 防护实现（跨Phase分发）"
description: |
  将蓝图 §8 中 44 条 Anti-Patterns 逐条实现防护机制。
  AP1-AP44 的防护逻辑已分发到各 Phase 对应任务卡中：
  - AP1/AP2/AP3/AP4/AP5/AP6/AP7 → scaffold/experimental 阶段（TASK-INF-0203/0204/0206/0207/0209）
  - AP8-AP13 → resilience 阶段
  - AP14-AP20 → sovereign 阶段
  - AP21-AP27 → metacognitive 阶段
  - AP28-AP32 → forensic 阶段
  - AP33-AP38 → governance 阶段
  - AP39-AP44 → adversarial 阶段
  本任务卡负责：创建 §8 Anti-Patterns 文档引用索引，确保每条 AP 的检查逻辑在对应模块中落地。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\_anti_patterns_.py"
    description: "Anti-Pattern 索引——44条 AP 编号 → 对应防护代码文件映射表"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\_anti_patterns_.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§8 Anti-Patterns 全部 44 条"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 4000
timeout_minutes: 19
acceptance_criteria:
  - "_anti_patterns_.py 含全部 44 条 AP 的 ID→实现文件映射"
  - "每条 AP 在映射表中指向至少一个实现文件"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\_anti_patterns_.py
depends_on:
  - "TASK-INF-0203"
blocked_by: []
status: "created"
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-021"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
