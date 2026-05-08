---
task_id: "TASK-SYS-0004"
source_blueprint: "SYS-MASTER-001"
source_section: "§2 架构原则 + §3 关键ADR索引"

title: "5条不可变核心原则 + 11条ADR索引(ADR-0001~R90)体系落地"
description: |
  将 SYS-MASTER-001 §2 的架构原则与 §3 的 ADR（Architecture Decision Record）索引体系工程化落地。
  §2.1 5条不可变核心原则：
  P1-SSoT（ADR-0001）：YAML=真源，MD=衍生视图。
  P2-YAML Schema（ADR-0002）：单Schema，Phased Required Fields（Phase 0→Phase 5）。
  P3-Dual AI（ADR-0003）：DeepSeek 主建设 + GLM-4.7 主审查。
  P4-OCP（ADR-0004）：Open-Closed Principle——对扩展开放，对修改封闭。
  P5-Blueprint First（G6）：先读蓝图→后写代码。
  §2.2 蓝图体系铁律5条。
  §3 11条 ADR 索引：ADR-0001~ADR-0011，每条含 date/status/source 字段。
  内容包括 Canonical SSoT → 三级金字塔 → Wasmtime沙箱 → XML中间表示等。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\architecture_principles.py"
    description: "5条核心原则 P1-P5 枚举 + 蓝图铁律5条枚举 + principled_check decorator"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\adr_registry.py"
    description: "11条 ADR 索引——adr_id/date/status/source 持久化查询"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\architecture_principles.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\adr_registry.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§2.1 P1-P5 / §2.2 铁律 / §3 ADR-0001~R90 11条"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 16000
timeout_minutes: 45

acceptance_criteria:
  - "ArchPrinciple 枚举 5 成员——P1_SSOT / P2_YAML_SCHEMA / P3_DUAL_AI / P4_OCP / P5_BLUEPRINT_FIRST"
  - "BlueprintIronLaw 枚举 5 成员"
  - "ADRRecord 含 adr_id / date / status(Proposed/Accepted/Deprecated/Superseded) / source 四字段"
  - "ADR_REGISTRY list 长度 == 11——从 ADR-0001 到 R90"
  - "script_manifest.yaml 注册"

rollback_instructions: |
  git rm src/zephyr/governance/architecture_principles.py adr_registry.py
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
