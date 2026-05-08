---
task_id: "TASK-SYS-0002"
source_blueprint: "SYS-MASTER-001"
source_section: "§0 AI Agent 冷启动分发"

title: "AI Agent 冷启动分发系统搭建——导航表 + 三级Token预算"
description: |
  实现 AI Agent 进入会话后的导航分发基础设施。
  §0.1: ai_role_instruction 读取 frontmatter 76条 rules 注入 AI 上下文。
  §0.2: 任务域导航表——约55行，4列矩阵：任务域 | 先读 | 再读 | Token预算。
  任务域涵盖门禁/断路器→行情数据管线的全部子领域，每个域映射到其依赖文档和预算。
  §0.3: 三级 Token Budget 分配——Hot Memory (~800 tokens 实时门禁状态)、
  Domain Triggers (~2000 tokens 当前任务域依赖)、Cold Memory (~8000 tokens 全量背景被动检索)。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_dispatch.py"
    description: "§0.2 导航表实现——约55域名→4列矩阵(任务域|先读|再读|Token预算)的 dispatch resolver"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\token_budget.py"
    description: "§0.3 三级 Token Budget——Hot(~800)/Domain(~2000)/Cold(~8000) 分配与溢出管理"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_dispatch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\token_budget.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-005"
    section: "§5"
    reason: "governance/ 路径合法性 + script_manifest.yaml 注册"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§0.1/§0.2/§0.3——ai_role_instruction/nav table 4列/三级 budget"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 55

acceptance_criteria:
  - "agent_dispatch.py 实现 dispatch_table——dict 映射约55个 domain→{pre_read, re_read, token_budget} 三元组"
  - "dispatch resolver 返回当前最佳匹配 domain 的依赖文档清单和 budget 上限"
  - "token_budget.py 实现 TokenManager——三级池 Hot(800)/Domain(2000)/Cold(8000)——分配时检查溢出"
  - "hat 中的 rules 76条可被 agent_dispatch.py 读取注入 context"

rollback_instructions: |
  git rm src/zephyr/governance/agent_dispatch.py token_budget.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0001"
blocked_by: []
status: "done"
tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
