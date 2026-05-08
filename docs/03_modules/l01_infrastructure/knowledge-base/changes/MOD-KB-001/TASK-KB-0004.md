---
task_id: "TASK-KB-0004"
source_blueprint: "MOD-KB-001"
source_section: "§3.3 知识条目10状态机"

title: "KE 10状态机验证与增强——验证 kb_repo.py 状态机与蓝图 §3.3 一致性"
description: |
  验证 src/zephyr/kb/kb_repo.py 中 KE 状态机实现与蓝图 §3.3 定义的10状态（DRAFT→SUBMITTED→REVIEWED→ACCEPTED→INDEXED→VERIFIED→DEPRECATED→ARCHIVED / REJECTED / SUPERSEDED）一致性。
  检查要点：(1)所有10态是否均已实现；(2)状态流转矩阵是否与蓝图定义的合法转换一致——如 REVIEWED 只能转 ACCEPTED 或 REJECTED；(3)状态流转日志是否正确写入 kb_state_log 表；(4)终态（REJECTED/ARCHIVED/SUPERSEDED）不可再转出的约束是否被 enforce。
  注意：此任务不修改状态机定义——仅在发现蓝图实现漂移时修正代码以对齐蓝图。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
    description: "修正状态流转逻辑以对齐蓝图 §3.3 定义（如有漂移）"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\state-machine-audit.md"
    description: "状态机审计报告——10态×10态流转矩阵对照表"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\state-machine-audit.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "task_id 编号格式"
  - module_id: "MOD-INF-006"
    section: "§4.2"
    reason: "KE 状态机 vs TaskCard 状态机——两者不混淆"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§3.3 定义了10状态机流转矩阵"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
    reason: "当前实现——需要对照验证"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "kb_repo.py 中 KE_TRANSITIONS 字典覆盖全部10态"
  - "每条合法状态转换在代码中可实现——不允许的状态转换抛出 ValueError"
  - "终态（REJECTED/ARCHIVED/SUPERSEDED）不可再转出"
  - "状态变更时自动写入 kb_state_log 表——from_status+to_status+triggered_by+reason 字段完整"
  - "state-machine-audit.md 输出完整流转矩阵对照表"
  - "现有单元测试 tests/unit/test_kb_repo.py 无 regression"

rollback_instructions: |
  1. git checkout -- src/zephyr/kb/kb_repo.py
  2. 删除 state-machine-audit.md
  3. 运行 pytest tests/unit/test_kb_repo.py 确认恢复

depends_on: ["TASK-KB-0003"]
blocked_by: []
status: "done"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
