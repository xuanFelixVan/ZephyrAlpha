---
task_id: "TASK-KB-0035"
source_blueprint: "MOD-KB-001"
source_section: "§16 需要更新的相关内容 + 容量约束"

title: "跨模块引用更新清单——AGENTS.md/KB-C4-flow/架构YAML/向量记忆相关文件一致性更新"
description: |
  执行蓝图 §16 定义的跨模块引用更新：(1)蓝图注册表——`blueprint-registry.yaml` 更新版本号+完整度（§16表第1行）；(2)模块ID注册表——`module-id-registry.yaml` 更新KB模块状态（§16表第2行）；(3)CE蓝图——`context-engine/blueprint.md` 更新CT-CE-KB集成状态（§16表第3行）；(4)AGENTS.md KB模块增加引用——确认"你拥有一个底层向量化的知识库"描述已存在→补充 CONTEXT_RULES 内部自动注入知识库；(5)C4→KB flow 下游 pipeline 更新——在 context_assembler 模板中增加 `## 相关记忆 ///3` 段落处延迟<500ms TTL宽放；(6)架构YAML b_kb.yaml modules.description 已在TASK-KB-0001完成——验证引用正确性；(7)向量记忆相关文件——vector_memory.py 中 recall()——原直接 Query ChromaDB 可能需要改为 `unified_memory_api.recall()` 复合；(8)§16 容量约束——`src/zephyr/kb/` 代码文件总量 ≤25个 + 单文件≤500行（新规）——当前实现接近16个；
  若有新文件超出限额→convinence function 合并→进 _helpers.py AB 安全性校验。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\__init__.py"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\b_kb.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\module-id-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\cross-module-reference-update.md"
    description: "新建——逐引用标注更新状态"

allowed_touch:
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\cross-module-reference-update.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§16 定义了需要更新的相关内容清单"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "blueprint-registry.yaml 版本号+完整度已更新（§16表第1行）"
  - "module-id-registry.yaml KB模块状态已更新（§16表第2行）"
  - "CE蓝图 context-engine/blueprint.md CT-CE-KB集成状态已更新（§16表第3行）"
  - "AGENTS.md 已增 KB-RAG 注入描述——CONTEXT_RULES 中明确 `## 相关记忆 ///3` 的触发条件"
  - "cross-module-reference-update.md 包含全部8项引用的更新状态"
  - "src/zephyr/kb/ 文件 count ≤ 25——超出→合并建议"

rollback_instructions: |
  1. git checkout -- AGENTS.md
  2. 删除 cross-module-reference-update.md

depends_on: ["TASK-KB-0001"]
blocked_by: []
status: "created"
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
