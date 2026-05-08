---
task_id: "TASK-INF-0121"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §16 AD-002"

title: "AD-002 实现——Shared + Core 合并使用单一蓝图维护：维持 MOD-INF-016 一体化"
description: |
  按 AD-002 决策——Shared 与 Core 保持单一蓝图 MOD-INF-016。
  使用单一蓝图管理 49 文件（Shared 46 + Core 3）而非拆分为两个独立蓝图。
  实现要求：
  1. 蓝图 §2/§3 中的 Shared 和 Core 边界清晰——Core 只负责 models 层，Shared 为全栈公共服务。
  2. 蓝图施工编码规则——Core 模块的代码标记为 archaeon-level（永不删除的核心层），
     Shared 模块标记为 shared-kernel-level（从 8 蓝图均可消费）。
  3. 蓝图版本号统一——版本号变化在 blueprint.md 中只保留一个版本号。
  4. 副 SSoT 清理——b_shared.yaml + b_core.yaml 两个 YAML 与唯一蓝图版本号同步。
  专业对标：DDD Shared Kernel 模式 + Google monorepo-tier documentation。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    description: "版本号统一——只保留一个版本号（同步于 all 副 SSoT）"
  - path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
    description: "SSoT YAML——module_id=MOD-INF-016，同步蓝图 version"
  - path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"
    description: "SSoT YAML——module_id=MOD-INF-016，同步蓝图 version"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5.1.1"
    reason: "module_id唯一性——MOD-INF-016 跨 Shared/Core 两个物理目录"
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "_cross_layer 模块必需同时归属于两个 laye—传入 b_shared.yaml + b_core.yaml"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §16——AD-002 决策上下文与维护规则"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 8000
timeout_minutes: 20

acceptance_criteria:
  - "blueprint.md 版本号（version: v0.14.0）与 b_shared.yaml + b_core.yaml version 一致"
  - "Shared 与 Core 的职责边界在 §2/§3 中明确——无交叉定义"
  - "Core 代码注释中 archaeon-level 标记存在"
  - "Shared 代码注释中 shared-kernel-level 标记存在"
  - "副 SSoT YAML 文件中无 stale version（已从旧 v0.1.x 更新到 v0.14.0）"

rollback_instructions: |
  1. git checkout -- docs/03_modules/_cross_layer/shared-core/blueprint.md
  2. git checkout -- architecture-model/layers/b_shared.yaml
  3. git checkout -- architecture-model/layers/b_core.yaml

depends_on: ["TASK-INF-0116"]
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

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
