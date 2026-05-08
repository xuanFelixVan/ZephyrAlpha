---
task_id: "TASK-KB-0009"
source_blueprint: "MOD-KB-001"
source_section: "§4.1 代码层目录 + §4.2 知识数据层目录 + §4.3 ChromaDB持久化层 + §4.4 4 Collection体系"

title: "目录结构与物理布局验证——代码层/知识数据层/ChromaDB层一致性检查 + 4 Collection初始化确认"
description: |
  验证蓝图 §4 定义的目录结构与磁盘实际状态一致性：(1)§4.1 代码层——确认 src/zephyr/kb/ 下12个已实现模块（✅标注）是否存在 + _future/ 目录下6个预留模块是否有 __init__.py stub；(2)§4.2 知识数据层——确认 docs/08_knowledge/ 目录结构按 §3.8 三轨18类体系组织（track_a_vibe_coding 8子目录 + track_b_finance 7子目录 + ko/observed|promoting|discarded + kb/active|superseded|retired + _archive/）；(3)§4.3 ChromaDB持久化层——确认 data/chroma/ 目录存在且 chroma.sqlite3 + 4个 Collection 子目录完整；(4)§4.4 4 Collection——确认 ke_entries/vibe_rules/blueprints/failure_patterns 四个 Collection 存在且向量维度384d。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\directory-layout-audit.md"
    description: "目录审查报告——逐文件标注状态（存在/缺失/与蓝图不符）"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\directory-layout-audit.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\**\\*.md"
  - "D:\\ZephyrAlpha\\data\\chroma\\**"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规检查"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§4 定义了完整目录结构——需要逐项对照磁盘"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "directory-layout-audit.md 逐文件列出状态——存在✅/缺失❌/路径不符⚠️"
  - "src/zephyr/kb/ 下12个✅模块100%存在于磁盘"
  - "docs/08_knowledge/ 目录结构至少包含 track_a_vibe_coding 和 track_b_finance 顶层目录"
  - "ChromaDB 4 Collection 可被 chromadb_init.py query 到"
  - "缺失项已生成修复建议列表"

rollback_instructions: |
  1. 删除 directory-layout-audit.md
  2. 无代码修改——纯审计报告，回滚仅需删除输出文件

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
