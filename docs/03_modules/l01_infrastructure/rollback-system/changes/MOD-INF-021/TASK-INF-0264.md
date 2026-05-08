---
task_id: "TASK-INF-0264"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 8.1-8.5 + §6.14 B98-B102 + 决策 D-021-22 + D-021-27~29"
title: "取证基础设施——Shell注入审计 + git hash-object 完整性 + NTP 证明 + Bit Rot + TOCTOU"
description: |
  实现 Phase 8 Part 1 取证基础设施，覆盖 B98-B102：
  B98 Shell 注入审计——回滚前 check 所有 trigger/message 是否嵌入 shell 命令
  B99 git hash-object 完整性——回滚前后每个文件的 git hash 存证
  B100 NTP 时钟证明——取证事件时间戳从 NTP 池获取，不可篡改
  B101 Bit Rot 检测——定期检查归档文件未受损
  B102 TOCTOU Race 防护——文件读写间内 locks/flocks 防御竞争条件
  涵盖 R31-R36 取证完整性与不可抵赖性风险。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\forensic.py"
    description: "取证引擎——Shell注入/hash存证/NTP时间戳/Bit Rot/TOCTOU 防护"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\forensic.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.14 B98-B102 取证核心 + D-021-22/27/28/29"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 12000
timeout_minutes: 45
acceptance_criteria:
  - "回滚 trigger/message Shell 命令嵌入扫描"
  - "回滚前后每个文件 git hash-object 独立存证"
  - "NTP 时间戳——无法回改取证事件时间"
  - "Bit Rot 定期检查 —— >90天归档文件验证"
  - "TOCTOU —— file locks (fcntl.flock + msvcrt.locking)"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\forensic.py
depends_on:
  - "TASK-INF-0263"
blocked_by: []
status: "done"
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
