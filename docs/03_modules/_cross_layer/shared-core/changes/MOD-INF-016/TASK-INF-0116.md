---
task_id: "TASK-INF-0116"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §8 需要更新的相关内容"

title: "§8 注册表更新——蓝图注册表 + models.py + b_shared.yaml/b_core.yaml 全链路同步"
description: |
  按蓝图 §8 要求，更新 4 项注册表：
  1. metadata-registry.md 模块注册表→新增 MOD-INF-016 条目（module_id / path / version / 职责）。
  2. b_shared.yaml SSoT→同步 frontmatter（module_id / description / consumer 索引）。
  3. b_core.yaml SSoT→同步 Core 子模块职责声明。
  4. API_INDEX.py→新增 Phase 11-20 新增的 shared/ 公共 API 导出。
  此外，蓝图 §8 提到 models.py 需要更新 TaskCard schema_version /= 1.0.0。
  所有 entry 必须在首次 release 前更新完毕。
  专业对标：Backstage API Docs + Google BUILD workspace rules。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\API_INDEX.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    description: "追加 MOD-INF-016 entry——module_id / path / version / 职责描述"
  - path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
    description: "同步 MOD-INF-016 frontmatter——Shared 层 SSoT"
  - path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"
    description: "同步 Core 子模块职责——Core 层 SSoT"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\API_INDEX.py"
    description: "新增 Phase 11-20 的公共 API 导出（cost_budget / evals / ... etc.）"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
    description: "更新 TaskCard schema_version 到 RELEASE-0.1.0"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\API_INDEX.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5.1"
    reason: "API_INDEX.py——公共 API 合约载体，不能有未生声明导入"
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "_cross_layer/ 模块只同时修改 b_shared.yaml + b_core.yaml 两个 SSoT"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §8——需要更新内容的明确清单"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    reason: "元数据注册表——MOD-INF-016 必须在此注册"
  - file_path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_shared.yaml"
    reason: "Shared SSoT——验证 frontmatter 声明与 blueprint.md 一致"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 12000
timeout_minutes: 30

acceptance_criteria:
  - "metadata-registry.md 中含有 MOD-INF-016 条目，module_id / path / version 字段齐全"
  - "b_shared.yaml frontmatter 中 module_id=MOD-INF-016 且 consumer 索引声明了 task-system"
  - "b_core.yaml 同步 Core 子模块职责与 §3 声明一致"
  - "API_INDEX.py 新增 Phase 11-20 公共 API 导出且通过 import 验证"
  - "models.py schema_version 更新为 RELEASE-0.1.0（从 draft 提升）"
  - "pytest tests/unit/test_schemas.py -v 全部通过"

rollback_instructions: |
  1. git checkout -- docs/01_policies_and_standards/meta/metadata-registry.md
  2. git checkout -- architecture-model/layers/b_shared.yaml
  3. git checkout -- architecture-model/layers/b_core.yaml
  4. git checkout -- src/zephyr/shared/API_INDEX.py
  5. git checkout -- src/zephyr/core/models.py

depends_on: ["TASK-INF-0102"]
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
