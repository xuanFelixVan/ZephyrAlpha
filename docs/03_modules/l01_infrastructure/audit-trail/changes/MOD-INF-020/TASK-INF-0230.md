---
task_id: "TASK-INF-0230"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §8 风险与缓解全部 R1-R42 + §决策记录 D-020-01~57 全覆盖映射"

title: "全面决策与风险覆盖追踪——57 决策 × 42 风险的实现/缓解任务卡映射验证"
description: |
  本任务卡作为审计系统的决策与风险覆盖追踪器（追踪卡——不产生代码，只产生验证报告）。
  验证内容：
  1. 57 条设计决策（D-020-01~D-020-57）每条有 ≥1 张实现/验证任务卡
     - D-020-01~08: TASK-INF-0202/0203/0204/0205/0206/0222/0223/0224 覆盖
     - D-020-09~13: TASK-INF-0206/0226/0226/0226/0227 覆盖
     - D-020-14~19: TASK-INF-0207/0223/0205/0225/0225/0215 覆盖
     - D-020-20~28: TASK-INF-0224/0224/0222/0227/0227/0227/0224/0217/0227 覆盖
     - D-020-29~35: 0222/0211/0220/0231/0231/0227/0231 覆盖（详见本卡映射表）
     - D-020-36~44: 0231/0226/0226/0221/0220/0221/0221/0223/0221 覆盖
     - D-020-45~57: 0231/0220/0220/0224/0212/0230/0230/0230/0230/0230/0230/0230/0221 覆盖
  2. 42 条风险（R1-R42）每条有 ≥1 条缓解任务卡
  3. 生成 decision-risk-card 映射 JSON 报告 → data/audit/coverage-map.json
  4. 缺失项可自动检测——如果任何决策/风险无对应卡 → 输出 gap report
  执行方式：脚本扫描 changes/MOD-INF-020/ 目录下所有 .md → 解析每个 doc 的 description/source_section → 构建覆盖矩阵。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\data\\audit\\coverage-map.json"
    description: "决策/风险/盲点→任务卡映射 JSON——机器可消费"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\verify_blueprint_coverage.py"
    description: "覆盖验证脚本——扫描 changes/ 目录 + 构建映射矩阵"

allowed_touch:
  - "D:\\ZephyrAlpha\\data\\audit\\coverage-map.json"
  - "D:\\ZephyrAlpha\\scripts\\governance\\verify_blueprint_coverage.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "覆盖验证自身也需审计"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§8 全部风险 + 决策记录全表"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 50

acceptance_criteria:
  - "57 条决策每条映射到 ≥1 张实现/验证任务卡——gap report 为空"
  - "42 条风险每条映射到 ≥1 张缓解任务卡——gap report 为空"
  - "coverage-map.json 文件存在——含 decision→cards[] / risk→cards[] 映射"
  - "verify_blueprint_coverage.py 可独立运行——CI 门禁集成"

rollback_instructions: |
  1. 删除 coverage-map.json
  2. 删除 verify_blueprint_coverage.py

depends_on:
  - "TASK-INF-0215"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
