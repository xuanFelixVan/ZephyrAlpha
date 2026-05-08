---
task_id: "TASK-KB-0019"
source_blueprint: "MOD-KB-001"
source_section: "§6.2 KB 施工任务追踪 + §6.3 状态机区分 + §3.5 KMS三级漏斗流程"

title: "KB 施工任务追踪板实现 + KE状态机vsTaskCard状态机区分机制"
description: |
  实现蓝图 §6.2 定义的 KB 施工任务追踪板 + §3.5 KMS 三级漏斗流程图落地：(1)在 knowledge-base/ 目录下建立施工跟踪：task-board.md（任务进度汇总图谱）→动态显示施工任务卡状态分布+E2E测试覆盖率+缺口→产出自愈建议；(2)task-repo.py 实现施工任务仓储——创建 TASK-KB-NNNN 元数据关联；(3)§6.3 KE(10态) vs TaskCard(created/done) 状态机区分——提供两个独立的 Python Enum: KeStatus(9_current+1_future=10态) vs TaskCardStatus(created/done) + 映射函数 ke_to_taskcard_trigger()；(4)TaskCard的状态变更触发 KE 状态同步——TaskCard completed→触发 KE AUDIT→STATE_SYNC_CHECK→确认 KE 是否升级。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-lifecycle-standard.md"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\db\task_repo.py"
    description: "新建——KB施工任务仓储——TASK-KB-NNNN 注册+状态查询+依赖关系"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\task_board.py"
    description: "新建——task-board 生成器——动态统计施工任务卡状态分布→产出自愈建议"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\task-board.md"
    description: "新建——KB施工任务追踪板（蓝图任务进度汇总图谱——动态更新）"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\task_board.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\task-board.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"
  - module_id: "PS-STD-001"
    section: "§6.12"
    reason: ".py 注册到脚本注册表"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§6.2 定义施工任务追踪 + §6.3 定义状态机区分 + §3.5 KMS三级漏斗流程图（rust学习版）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "KeStatus 枚举 10 态(DRAFT/SUBMITTED/REVIEWED/ACCEPTED/INDEXED/VERIFIED/DEPRECATED/ARCHIVED/REJECTED/SUPERSEDED)"
  - "TaskCardStatus 枚举 2 态(created/done)"
  - "ke_to_taskcard_trigger()——返回任务卡状态变更应触发的 KE 同步动作"
  - "task_repo.py 提供 register_task_card(task_id, depends_on, status)→bool 四函数"
  - "task_board.py 扫描 changes/MOD-KB-001/ 目录→按status分组动态汇总→产出自愈建议"
  - "task-board.md 初始为空——施工任务追踪板列表——动态更新"

rollback_instructions: |
  1. 删除 src/zephyr/kb/task_repo.py, task_board.py
  2. 删除 task-board.md
  3. 若 track_task_card_in_kb() 已修改 gorvernance files→git checkout --

depends_on: ["TASK-KB-0004", "TASK-KB-0001"]
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
