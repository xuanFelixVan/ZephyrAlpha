---
task_id: "TASK-INF-0113"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §5 已实现代码完整路径索引"

title: "§5 代码路径索引维护——蓝图-源码路径同步与一致性验证"
description: |
  维护 blueprint.md §5 中 49 文件路径索引与磁盘文件的一致性。
  §5.1 源码文件——Shared 46 + Core 2（models.py / blueprint_decomposer.py）= 48 个 .py 文件路径。
  §5.2 测试文件——17 个 unit + 2 个 integration + 1 个 contract + 1 个 emergency = 21 测试文件。
  §5.5 路径索引使用指南——搜索-阅读-修改三步工作流。
  每次蓝图版本号变更后 MUST 更新代码路径索引。
  专业对标：Google Build file OWNERS + ZephyrAlpha auto_contract_tester。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\sync_code_index.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\sync_code_index.py"
    description: "脚本——自动扫描 shared/ + core/ 目录，生成路径索引并同步到 blueprint.md §5"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\sync_code_index.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5.1.1"
    reason: "API_INDEX.py——§5.1 中 API_INDEX.py 路径必须始终最新"
  - module_id: "GOV-DOC-002"
    section: "§7"
    reason: "目录结构标准——scripts/governance/ 为管控脚本合法目录"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §5——需要同步的路径索引目标"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 10000
timeout_minutes: 30

acceptance_criteria:
  - "sync_code_index.py 可执行——python scripts/governance/sync_code_index.py 不报错退出"
  - "共享层源码 48 文件路径与磁盘一致（Shared 46 + Core 2）"
  - "测试文件 21 路径与磁盘一致"
  - "walk_source_path 有最大深度限制（避免无限递归）"
  - "路径索引不存在的文件自动标记 [MISSING] 并 fail"
  - "SHARED-QUICKREF.yml 引用路径与实际磁盘路径一致"

rollback_instructions: |
  如果 sync_code_index.py 损坏了 blueprint.md §5：
  1. git checkout -- docs/03_modules/_cross_layer/shared-core/blueprint.md
  如为新脚本本身的 bug：
  1. git revert <commit>

depends_on: ["TASK-INF-0100"]
blocked_by: []

status: "created"

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
