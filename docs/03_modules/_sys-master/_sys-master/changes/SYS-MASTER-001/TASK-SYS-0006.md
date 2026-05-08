---
task_id: "TASK-SYS-0006"
source_blueprint: "SYS-MASTER-001"
source_section: "§6 输出文件位置 + §7 集成目标"

title: "系统输出文件 Manifest + 5大集成目标契约搭建"
description: |
  将 SYS-MASTER-001 §6 的输出文件位置索引与 §7 的集成目标工程化落地。
  §6: 系统生成文件按三类路径追踪——src/zephyr/（生产代码）、tests/（测试）、docs/（文档）。
  每个文件按（module_id | file_path | file_type | version | last_updated）五元组 Manifest 管理。
  §7: 5大集成目标——Integrated Broker Connectivity Service / Model-based Generation Pipeline /
  Event-Driven Market Processing / Outsource Data Provider / Knowledge Management Engine。
  每个目标定义上游输入路径、下游输出路径、接口契约、验收标准。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\output_file_manifest.py"
    description: "§6 file manifest——FileEntry(module_id, file_path, file_type, version, last_updated)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\integration_targets.py"
    description: "§7 5大集成目标——IntegrationTarget Enum + upstream/downstream/contract 定义"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\output_file_manifest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\integration_targets.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§6 文件位置索引 + §7 5大集成目标"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "§6 中文件路径必须符合目录结构标准三类目录(src/tests/docs)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 14000
timeout_minutes: 40

acceptance_criteria:
  - "FileEntry dataclass——module_id / file_path(绝对路径) / file_type(py|md|yaml|sql) / version / last_updated"
  - "IntegrationTarget Enum——IM1~IM5——每成员含 upstream_input / downstream_output / contract / acceptance"
  - "script_manifest.yaml 注册"

rollback_instructions: |
  git rm src/zephyr/governance/output_file_manifest.py integration_targets.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0003"
blocked_by: []
status: "created"
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
