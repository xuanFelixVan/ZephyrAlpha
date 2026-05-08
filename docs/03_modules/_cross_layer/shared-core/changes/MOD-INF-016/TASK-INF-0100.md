---
task_id: "TASK-INF-0100"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §1 概述"

title: "§1 模块骨架搭建与定位验证——Shared+Core 跨层基础设施概述完整性审计"
description: |
  验证 MOD-INF-016 Shared+Core 模块概述（§1）的蓝图声明与实际状态一致。
  涵盖：module_id 确认、Shared（src/zephyr/shared/）与 Core（src/zephyr/core/）合并范围、
  文件数声明（Shared 46 + Core 3 = 49 文件）的磁盘一致性、核心职责定义。
  锚定真源声明 SSoT——b_shared.yaml + b_core.yaml。
  对标 Google Monorepo shared/ 模式 + DDD Shared Kernel 跨限界上下文共享领域模型。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0100.md"
    description: "本任务卡——§1 概述审计任务的执行记录"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0100.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§1.4"
    reason: "SSoT 声明——SSoT YAML 与 blueprint.md 版本号必须同步"
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "_cross_layer/ 模块准入规则——核心职责横跨 >=2 个 C 轨层"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图——验证 §1 概述声明"
  - file_path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
    reason: "Shared YAML SSoT——验证 module_id/frontmatter 一致性"
  - file_path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"
    reason: "Core YAML SSoT——验证 module_id/frontmatter 一致性"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 3000
timeout_minutes: 15

acceptance_criteria:
  - "blueprint.md §1 module_id = MOD-INF-016 且 b_shared.yaml/b_core.yaml 中 module_id 一致"
  - "Shared 目录 (D:\\ZephyrAlpha\\src\\zephyr\\shared\\) 下文件数 = 46（含子目录递归）"
  - "Core 目录 (D:\\ZephyrAlpha\\src\\zephyr\\core\\) 下文件数 = 3"
  - "总文件数 = 49"
  - "core/modules.py 继承 shared/schemas.py Task 的 import 链路可成功执行"

rollback_instructions: |
  本任务为只读审计——不做文件修改。如发现不一致，记录到 TASK-INF-0100.md 正文中作为审计发现，
  创建后续修复任务卡。无操作需要回滚。

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings:
  - id: "F-TASK-INF-0100-001"
    severity: "high"
    finding: "b_core.yaml module_id = MOD-INF-006，但 blueprint.md 和 b_shared.yaml 均为 MOD-INF-016。module_id 不一致。"
    evidence: "b_core.yaml:L11: module_id: MOD-INF-006"
  - id: "F-TASK-INF-0100-002"
    severity: "high"
    finding: "Shared 目录实际 .py 文件数=150（含子目录递归），与蓝图声明 46 不一致。目录已重组为 api/foundation/infra/io/observability/schema/security/utils 等子模块，且存在大量顶层与子目录重复文件。"
    evidence: "Glob **/*.py count = 150"
  - id: "F-TASK-INF-0100-003"
    severity: "medium"
    finding: "Core 目录实际 .py 文件数=4（含 session_continuity.py + __init__.py），与蓝图声明 3 不一致。"
    evidence: "Glob **/*.py count = 4 (models.py, blueprint_decomposer.py, session_continuity.py, __init__.py)"
  - id: "F-TASK-INF-0100-004"
    severity: "medium"
    finding: "总文件数实际=154，与蓝图声明 49 不一致。"
    evidence: "共享150 + Core4 = 154"
  - id: "F-TASK-INF-0100-005"
    severity: "info"
    finding: "import 链路验证通过：from zephyr.core.models import TaskCard 成功。"
    evidence: "python -c import test passed"

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
