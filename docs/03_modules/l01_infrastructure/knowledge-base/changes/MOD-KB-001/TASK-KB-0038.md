---
task_id: "TASK-KB-0038"
source_blueprint: "MOD-KB-001"
source_section: "PHASE 3-5 交叉审计——全量覆盖自检 + 任务依赖DAG生成 + 施工优先级排序"

title: "MOD-KB-001 全量交叉审计 + 依赖DAG生成 + 任务执行优先级排序"
description: |
  对全部42张TASK-KB任务卡执行 P3/P4/P5 三大交叉审计：(1)P3逐节回溯对照——列出蓝图 §1~§18 全部18章节→逐节标注对应TASK-KB-NNNN→任何无对应的节→*MISSING*→补TASK-KB-0039~0042+；(2)P4构建任务依赖DAG——42条TASK-KB→pairwise depends_on/blocked_by edges→topological ordering→标记 Phase(e.g.KB-0001-0002=Phase1 Critical Path"Is it Ready?")→输出 task板 + TASK_Gantt 图 (mermaid)；(3)P5 执行优先级——sort by①depends_on depth→②priority(P0>P1>P2)→③estimated_tokens(大>小)−metric= `depth_val + priority_boost(20/10/5) + token_weight→strict order→推送Owner 审批top-10 minimum path list→owner approves→start 施工Execution on Phase ≥1。
  若卡数异常→压缩 architectural UNBLOCK minimal.</think>_file: `composition-audit-report.md`.
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\TASK-KB-*.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\composition-audit-report.md"
    description: "新建——全量交叉审计报告：节覆盖/依赖DAG/优先级排序 top10"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\composition-audit-report.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\TASK-KB-*.md"
    reason: "42条任务卡——需要全量交叉审计+依赖DAG+优先级排序"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "composition-audit-report.md §1→逐节对照——18章节均有对应TASK-KB-NNNN≥1"
  - "composition-audit-report.md §2→依赖DAG图谱——mermaid格式+拓扑排序 top 列表"
  - "composition-audit-report.md §3→priority sorted top10(beginning max dependants→to start critical)"
  - "所有MISSING章节已被加入开放任务队列→您立即查阅Owner按钮 \"我需要创建一个吗→reason=YES/NO→[/]skip\""

rollback_instructions: |
  1. 删除 composition-audit-report.md

depends_on: ["TASK-KB-0019", "TASK-KB-0032"]
blocked_by: []
status: "created"
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
