---
task_id: "TASK-KB-0007"
source_blueprint: "MOD-KB-001"
source_section: "§3.8 三轨18类知识分类体系"

title: "KeCategory 枚举重构——从旧6分类升级为三轨18类 + 向后兼容迁移逻辑"
description: |
  执行蓝图 §3.8 定义的分类体系升级：(1)废弃原有金融域6类枚举（blueprint_decision/best_practice/factor/failure_pattern/guardrail/architecture_decision）；(2)新增三轨18类——Track A Vibe Coding施工知识8类(A1-A8) + Track B 金融领域知识7类(B1-B7) + Track C Owner决策画像3类(C1-C3) + Track D AI协作知识预留桩3类(D1-D3)；(3)实现向后兼容迁移逻辑：old_category→new_category 映射表 + SQLite ALTER 而非 DROP；(4)extract.py EXTRACTION_TEMPLATES 扩展——从5→15模板（覆盖Track A全部8类+Track B全部7类source_type）。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    description: "KeCategory 枚举重构——18枚举值 三轨18类注解"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
    description: "EXTRACTION_TEMPLATES 从5模板扩展至15模板——覆盖Track A/B全15类source_type"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
    description: "分类逻辑更新——对接新18类枚举 + 向后兼容映射"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_category_migration.py"
    description: "新建——old_category→new_category 映射表 + SQLite 迁移脚本"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_category_migration.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "新建文件路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§3.8 定义了三轨18类 + §5.11 定义了15类EXTRACTION_TEMPLATES"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "schemas.py 中 KeCategory 枚举定义18个值——A1-A8/B1-B7/C1-C3"
  - "triage.py 的 _assign_category() 能处理18类分类逻辑"
  - "extract.py EXTRACTION_TEMPLATES 包含15个模板字典（session_log/adr/governance_document/precommit_failure/dependency_migration/academic_paper/market_data_experience/regulatory_document/trading_experience 等）"
  - "_category_migration.py 提供完整的 old→new 映射表"
  - "SQLite 中已有 KE 的 category 字段可通过 migration 脚本一键更新"
  - "旧6类查询仍可用——映射表保证向后兼容"

rollback_instructions: |
  1. git checkout -- src/zephyr/shared/schemas.py
  2. git checkout -- src/zephyr/kb/extract.py
  3. git checkout -- src/zephyr/kb/triage.py
  4. 删除 src/zephyr/kb/_category_migration.py
  5. SQLite: 若已执行 migration——用备份的 kb_state.db 覆盖 data/sqlite/kb_state.db

depends_on: ["TASK-KB-0003"]
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
