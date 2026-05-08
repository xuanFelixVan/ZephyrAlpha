---
task_id: "TASK-SYS-0022"
source_blueprint: "SYS-MASTER-001"
source_section: "§30 知识管理 + §78 Bus Factor + §82 代码考古"

title: "知识管理引擎(索引→搜索→关联) + Bus Factor≤2(Onboarding/ADR Log/Runbook) + AI代码考古(doc auto-gen/blame/evolution)体系"
description: |
  将 SYS-MASTER-001 §30 知识管理 + §78 知识连续性(Bus Factor) + §82 AI代码考古三合一落地。
  §30: 知识管理引擎——索引→搜索→关联三组件。全文检索 elastic/app search。
  §78: Bus Factor 防御——knowledge_bus_factor≤2（任何关键模块至少2人/Agent理解）/
  onboarding material<15min可理解（README+diagram+key_functions）/decision_log ADR格式
  （problem/options/decision/rationale/review_date）/runbook 每个关键模块 ops runbook自动生成。
  §82: Code Archaeology——auto-generate module doc+ code_blame 追溯代码起源(agent_id/session_id/task_id)+code_evolution_graph(commit→release→dependency 时间线)。
  本卡搭建 knowledge_engine.py + bus_factor_defense.py + code_archaeology.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\knowledge_engine.py"
    description: "§30 KM引擎——索引→搜索→关联 三组件+全文检索"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\bus_factor_defense.py"
    description: "§78 BusFactor≤2 check+Onboarding<15min+ADR Decision Log+Ops Runbook auto-gen"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\code_archaeology.py"
    description: "§82 代码考古——module doc auto-gen+code blame(agent→session→task)+evolution graph"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\knowledge_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\bus_factor_defense.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\code_archaeology.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§30 KM(索引→搜索→关联)+§78 BusFactor≤2(Onboarding/ADR/Runbook)+§82 Archaeology(auto doc/blame/evolution)"

assigned_model: "deepseek"
assigned_pipeline: "A/B hybrid"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 22000
timeout_minutes: 60

acceptance_criteria:
  - "KM: Index(自动索引 docs/ 内容)→Search(elastic full-text)→Association( semantic 关联)"
  - "bus_factor: Score(module)→owner_count≥2 Tool. onboarding→README+diagram+key_funcs <15min可理解. decision_log→ADR format. runbook auto-gen per module"
  - "archaeology: blame(file,line)→agent_id/session_id/task_id traced from __provenance__. evolution→git log→DiGraph→export timeline"

rollback_instructions: |
  git rm src/zephyr/governance/knowledge_engine.py bus_factor_defense.py code_archaeology.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0010"
blocked_by: []
status: "done"
tags_fn:
  - "docs"
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
