---
task_id: "TASK-KB-0001"
source_blueprint: "MOD-KB-001"
source_section: "§1 概述与模块定位"

title: "MOD-KB-001 模块骨架搭建——蓝图定稿后立即行动清单执行"
description: |
  执行蓝图 §12.1 定义的四项立即行动：(1)更新 b_kb.yaml 架构 YAML SSoT——确认 status=implemented、更新 note 和 modules.description 引用本蓝图；(2)更新 _index.yaml 确认 b_kb.yaml 在 b_track 中正确注册；(3)候选池KB内容清理——逐文件删除已提取的KB专属内容并留痕；(4)创建 knowledge-base/index.md 模块入口索引文件。
  本任务是 knowledge-base 模块正式注册为可施工模块的先决条件。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\b_kb.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\_index.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"

downstream_outputs:
  - path: "D:\ZephyrAlpha\architecture-model\layers\b_kb.yaml"
    description: "更新 note 字段和 modules.description 引用 MOD-KB-001 blueprint.md"
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\_index.yaml"
    description: "确认 b_kb.yaml 在 b_track 中正确注册"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\index.md"
    description: "新建模块入口索引文件——列出蓝图路径、代码路径、KE存放路径、施工Phase状态"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\b_kb.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\_index.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\index.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\**\\*.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "task_id 编号格式 TASK-KB-NNNN"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "新建 index.md 路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§12.1 定义了四步立即行动"
  - file_path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\b_kb.yaml"
    reason: "需要读取当前 status/note 后更新"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "b_kb.yaml status 字段为 implemented"
  - "b_kb.yaml note 字段包含 MOD-KB-001 blueprint.md 引用"
  - "_index.yaml 中 b_kb.yaml 在 b_track 下注册"
  - "knowledge-base/index.md 文件存在——包含蓝图路径、代码路径、KE存放路径、施工Phase状态四项内容"
  - "以上修改不涉及 src/zephyr/kb/ 下任何代码文件"

rollback_instructions: |
  1. git checkout -- docs/02_enterprise_architecture/target-architecture/architecture-model/b_kb.yaml
  2. git checkout -- docs/02_enterprise_architecture/target-architecture/architecture-model/_index.yaml
  3. 删除 D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\knowledge-base\index.md

depends_on: []
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
