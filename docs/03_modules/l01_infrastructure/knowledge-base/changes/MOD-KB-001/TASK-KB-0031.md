---
task_id: "TASK-KB-0031"
source_blueprint: "MOD-KB-001"
source_section: "§10 迁移/废弃方案"

title: "KB 旧版迁移方案执行——候选池清理 + Track/KE 目录重建 + ChromaDB冷重启"
description: |
  执行蓝图 §10 定义的三部分迁移方案：(1)清空 docs/03_modules/l01_infrastructure/knowledge-base/candidate-pool/ 目录（全部.md 移入 _archive/ →删除已有KE的 原文件+Git commit"chore:退役候选池"）；(2)重建 docs/08_knowledge/ 目录——遵 §4.2 A 知识数据层三轨18类子目录 + ko/observed|promoting|discarded + kb/active|superseded|retired + _archive/——MKDIR 命令集合+chmod 755 perfs；(3)ChromaDB冷重启——删除 data/chroma/ke_entries/ 子目录→re-init `python -m src.zephyr.kb.chromadb_init --collection ke_entries --reset`——从已迁移的SQLite 重新 push（仅 ACCEPTED+→INDEXED）。
  若旧 KE 在 SQLite 中存在但对应的 ChromaDB embedding 缺失→ push 个别缺失的 (batch size=1)。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\candidate-pool\\_archive\\"
    description: "移入旧候选池 .md 文件 + Git commit 退役记录"
  - path: "D:\\ZephyrAlpha\\docs\\08_knowledge\\track_a_vibe_coding\\"
    description: "Track A 8子目录（a1-a8）+ .gitkeep"
  - path: "D:\\ZephyrAlpha\\docs\\08_knowledge\\track_b_finance\\"
    description: "Track B 7子目录（b1-b7）+ .gitkeep"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\candidate-pool\\"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\"
  - "D:\\ZephyrAlpha\\data\\chroma\\ke_entries\\"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§10 定义了重建三步迁移方案"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "候选池原文件全移出——candidate-pool/ 目录为空"
  - "docs/08_knowledge/track_a_vibe_coding/ 含8子目录"
  - "docs/08_knowledge/track_b_finance/ 含7子目录"
  - "ChromaDB ke_entries reset 后——re-index SQLite 中 ACCEPTED+INDEXED KE"
  - "已有 KE 的向量检索可work——python -c 'from src.zephyr.kb.unified_memory_api import recall; print(len(recall(\"架构\", top_k=5)))'"

rollback_instructions: |
  1. 从 _archive/ 恢复候选池文件到候选池根目录
  2. 删除 docs/08_knowledge/track_* 目录
  3. ChromaDB——从备份恢复 data/chroma/ke_entries/ ——或退回到 0 非 reset 状态

depends_on: ["TASK-KB-0009"]
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
