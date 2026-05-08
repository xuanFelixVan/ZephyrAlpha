---
task_id: "TASK-INF-0231"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §9 能力边界声明——盲点 B15-B99 全覆盖策略 + 深度自检审计"

title: "全量盲点管理与闭合追踪——85 盲点 (B15-B99) 的覆盖策略验证与闭合门禁"
description: |
  本任务卡追踪审计系统 85 个已识别盲点的闭合状态。
  Phase scaffold 已覆盖（27 盲点）：
    B20/B22/B30/B38/B43/B46/B50/B54/B61/B66/B67/B72/B79/B83/B87/B92/B95/B98（18盲点）
    加上已通过实现卡间接覆盖的：B17/B31/B44/B78（4盲点）
    加上挂起风险的盲点：B5/B6/B7/B8/B53（5盲点）——本卡标记为"风险缓解中"

  Phase experimental 覆盖策略（27盲点）：
    B15/B16/B18/B23/B24/B25/B26/B27/B32/B33/B34/B39/B45/B53/B57/B58/B64/B68/B71/
    B73/B75/B76/B80/B81/B82/B88/B89/B90/B93/B94/B97/B56  → TASK-INF-0222~0225
    其中 B55 由 TASK-INF-0220 的 prompt injection 净化覆盖
  
  Phase beta 覆盖策略（24盲点）：
    B11/B12/B13/B19/B21/B28/B31/B35/B36/B37/B40/B41/B48/B49/B51/B52/B59/B60/B62/
    B63/B70/B74/B84/B85/B86 → TASK-INF-0226/0227

  v2.0 计划（7盲点）：
    B28(ML基线)/B36/B40/B41/B42/B44/B47/B49/B51/B52/B59/B60/B65/B69/B91/B96/B99
  
  本任务卡输出：盲点覆盖矩阵 YAML + CI 可自动校验。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blind-spot-coverage.yaml"
    description: "盲点覆盖矩阵——每个盲点→phase→闭合任务卡→状态"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blind-spot-coverage.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "盲点管理审计"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§9盲点全量表——B15-B99"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 4000
timeout_minutes: 25

acceptance_criteria:
  - "85 个盲点 (B15-B99) 每个有明确的 phase 归属"
  - "Phase scaffold 27 盲点全部已闭合或标记为风险缓解中——无一遗漏"
  - "Phase experimental 27 盲点均有对应实现任务卡 ID"
  - "Phase beta 24 盲点均有对应实现任务卡 ID"
  - "v2.0 7 盲点有明确的延期声明"
  - "CI 自动校验 blind-spot-coverage.yaml vs §9 声明的一致性"

rollback_instructions: |
  1. 删除 blind-spot-coverage.yaml

depends_on:
  - "TASK-INF-0230"
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
