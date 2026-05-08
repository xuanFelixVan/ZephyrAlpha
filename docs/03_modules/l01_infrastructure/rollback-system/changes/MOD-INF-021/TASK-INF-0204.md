---
task_id: "TASK-INF-0204"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 1.4 + §6.2 B16"

title: "RollbackVerifier 实现——G0 门禁 + __pycache__ 清理 + DB 一致性自愈"
description: |
  实现 RollbackVerifier 核心类：
  - G0 门禁验证：文件存在性 + YAML 语法校验
  - __pycache__ 清理：回滚后删除所有 .pyc bytecode 缓存
  - DB 一致性自愈：比较 tasks 表与文件状态，不一致时自动修正
  - differential check：回滚前后逐行比较 tasks/gates/events 表
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_verifier.py"
    description: "回滚验证器——G0 门禁 + __pycache__ 清理 + DB 一致性自愈 + 逐行 differential check"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_verifier.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——所有模型基座"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§2.2 G0 验证流程 + §6.2 B16 cache 一致性问题"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "verify_g0(files) 检查回滚后文件存在性 + YAML 语法"
  - "clear_bytecode_cache() 递归删除所有 __pycache__ 目录"
  - "heal_db_consistency() 比较 tasks 表与文件状态 ← 不一致自动修正"
  - "differential_check(target_sha) 逐行比较回滚前后 DB 表差异"
  - "diff > 3 行 → mark ROLLBACK_PARTIAL + 通知 Owner"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_verifier.py

depends_on:
  - "TASK-INF-0201"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-021"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
