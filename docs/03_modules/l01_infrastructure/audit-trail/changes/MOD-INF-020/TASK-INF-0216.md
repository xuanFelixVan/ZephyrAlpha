---
task_id: "TASK-INF-0216"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.2 consistency_check——rebuild_script + §3.2 rebuild_index.py"

title: "实现 SQLite 索引重建脚本——rebuild_audit_index.py（JSONL → SQLite 派生索引）"
description: |
  实现 `scripts/governance/rebuild_audit_index.py` 索引重建脚本。
  功能：
  - 扫描 data/audit/ 目录下的所有 JSONL 文件 → 解析每行 JSON → 提取查询关键字段
  - 创建/重建 SQLite 索引表：task_summaries / file_details / entries / anomalies / drifts
  - 完整性预校验：重建前验证 JSONL 哈希链连续性（快速模式）
  - 增量重建：读取上一次重建的 lamport_clock checkpoint → 仅处理新条目
  - 写入元审计事件：log_index_rebuild(trigger, entries_count)
  - CLI 入口：python rebuild_audit_index.py [--full|--incremental]
  落地决策 D-020-02。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\rebuild_audit_index.py"
    description: "索引重建脚本——JSONL→SQLite + 增量 + checkpoint"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_rebuild_audit_index.py"
    description: "重建脚本测试——全量/增量一致性 + checkpoint 机制"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\rebuild_audit_index.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_rebuild_audit_index.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\data\\audit\\**\\*.jsonl"
  - "D:\\ZephyrAlpha\\data\\audit\\**\\*.db"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "脚本路径 scripts/governance/ 合规"
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "索引重建需记录为元审计事件"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.2——consistency_check + rebuild_script + D-020-02"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 7000
timeout_minutes: 45

acceptance_criteria:
  - "全量重建 10000 行 JSONL → SQLite 索引 10000 条记录"
  - "增量重建仅处理新条目 → 现有条目不受影响"
  - "checkpoint lamport_clock 保存正确 → 断点续传有效"
  - "重建后 SQLite 行数 == JSONL 行数"
  - "重建完成自动写入 log_index_rebuild 元审计事件"

rollback_instructions: |
  1. 删除 rebuild_audit_index.py
  2. 删除 test_rebuild_audit_index.py
  3. 删除测试期间产生的 checkpoint.json 文件

depends_on:
  - "TASK-INF-0209"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "data"
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
