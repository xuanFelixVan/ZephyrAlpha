---
task_id: "DB-025-0076"
namespace: "OPS"
seq: 76
title: "T-DB-010——FTS5 全文搜索 (Phase experimental，P2，3.0h)"
tags: ["fn:db", "ly:cross_layer", "T-DB-010"]
depends_on: ["DB-025-0016"]
upstream_files: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"]
acceptance_criteria: ["task_repo 增加 search(query) 使用 FTS5", "test_task_repo 覆盖"]
rollback_instructions: "git checkout task_repo.py"
allowed_touch: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"]
forbidden_touch: []
assigned_pipeline: "B"
pipeline_modules: ["M7","M11"]
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P2"
estimated_context_tokens: 3000
---

# DB-025-0076：T-DB-010——FTS5 全文搜索

§16.4 T-DB-010: task_repo FTS5虚拟表+search()。
