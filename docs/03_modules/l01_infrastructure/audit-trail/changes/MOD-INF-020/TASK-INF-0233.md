---
task_id: "TASK-INF-0233"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §3.2 文件组成全量表 + §7 施工文件对照"

title: "模块注册与蓝图索引更新——script_manifest.yaml / blueprint-registry.yaml / module_index 同步"
description: |
  将 audit_trail 模块注册到项目治理基础设施：
  1. 更新 `docs/03_modules/blueprint-registry.yaml`——追加 MOD-INF-020 条目
  2. 更新 `docs/01_policies_and_standards/_registry/catalogs/script-manifest.yaml`——注册 audits 所有 Python 文件
  3. 更新 `docs/03_modules/l01_infrastructure/index.md`——追加 audit-trail 模块导航
  4. 运行 `python scripts/governance/d3_metadata/generate_rule_catalog.py` 重新生成元数据索引
  5. 验证所有 registered 路径在磁盘上存在
  落地 AGENTS.md §6.5 脚本入库规则。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\script-manifest.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\index.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
    description: "追加 MOD-INF-020 条目"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\script-manifest.yaml"
    description: "注册 audit_trail/ 下所有 .py 文件"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\index.md"
    description: "追加 audit-trail 模块导航条目"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\script-manifest.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\index.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\**\\*.md"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "注册表路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§3.2——全量文件注册清单"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
    reason: "需追加 MOD-INF-020"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 3000
timeout_minutes: 20

acceptance_criteria:
  - "blueprint-registry.yaml 含 MOD-INF-020: status=active, path=正确"
  - "script-manifest.yaml 含 audit_trail/ 下所有 .py 文件注册"
  - "index.md 含 audit-trail 导航→blueprint.md 链接"
  - "generate_rule_catalog.py 运行成功——无 ERROR"

rollback_instructions: |
  1. 从 blueprint-registry.yaml 中移除 MOD-INF-020 条目
  2. 从 script-manifest.yaml 中移除 audit_trail entries
  3. 从 index.md 中移除 audit-trail 导航

depends_on:
  - "TASK-INF-0200"
blocked_by: []

status: "done"

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
