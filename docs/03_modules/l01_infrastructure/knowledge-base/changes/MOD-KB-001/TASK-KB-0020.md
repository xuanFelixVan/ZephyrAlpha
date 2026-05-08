---
task_id: "TASK-KB-0020"
source_blueprint: "MOD-KB-001"
source_section: "§6.4 脚本系统接收 KB 成果 + §6 已实现代码索引"

title: "脚本系统 C4→G1 自动化集成——Makefile/Justfile 接收KB检索成果 + 已实现代码索引验证"
description: |
  实现蓝图 §6.4 定义的脚本系统与 KB 检索集成：(1)在 Makefile/Justfile 的目标中嵌入 kb_recall 自动注入——`context: kb_recall + run`——在 AI session begin→context_assembler 模板中自动插入最近 3 条 `## 相关记忆 ///3`；(2)默认 C4→G1 flow——AI session结束→context_engine agent→压缩摘要→KE G1+G5→效应：质量用于反馈回路；(3)已实现代码索引验证——对照蓝图 SKILL_MAP 重新扫描 src/zephyr/kb/ 目录——确认15个已实现模块（ingest/triage/analyze/activate/extract/unified_memory_api/kb_repo/chromadb_init/batch_ingest/_sentinels/...）在磁盘上存在且 import 路径正确。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\Makefile"
  - "D:\\ZephyrAlpha\\justfile"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\Makefile"
    description: "在 context 目标中嵌入 kb_recall 自动注入"
  - path: "D:\\ZephyrAlpha\\justfile"
    description: "在 context 目标中嵌入 kb_recall 自动注入"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\__init__.py"
    description: "追加 kb_recall_quick 便捷函数导入"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\code-index-verification.md"
    description: "新建——实现代码索引验证报告——逐模块标注磁盘状态+import路径"

allowed_touch:
  - "D:\\ZephyrAlpha\\Makefile"
  - "D:\\ZephyrAlpha\\justfile"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\__init__.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\code-index-verification.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§6.4 定义C4→G1 flow + §6 末尾 SKILL_MAP 完整代码索引"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "Makefile context 目标中 kb_recall_quick 自动注入 `## 相关记忆 ///3` 块到 context 模板"
  - "justfile context 目标中同逻辑嵌入"
  - "C4→G1 flow 的 kb context→context_assembler→session 开始自动推送 last 3 KE"
  - "code-index-verification.md 包含全部15个 SKILL_MAP 模块的磁盘验证结果——存在/缺失/路径错误"
  - "缺失模块→if has IMPL tag: →WARNING 并生成补全建议"

rollback_instructions: |
  1. git checkout -- Makefile justfile
  2. git checkout -- src/zephyr/kb/__init__.py
  3. 删除 code-index-verification.md

depends_on: ["TASK-KB-0018"]
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
