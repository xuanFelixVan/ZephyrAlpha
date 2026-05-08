---
task_id: "DB-025-0072"
namespace: "OPS"
seq: 72
title: "T-DB-006——dead_letter_queue (Phase experimental，P2，2.0h)"
tags: ["fn:db", "ly:cross_layer", "T-DB-006"]
depends_on: ["DB-025-0049"]
upstream_files: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
acceptance_criteria: ["新增 dead_letter_queue() + retry_dlq()", "test_database_manager 覆盖"]
rollback_instructions: "git checkout database_manager.py"
allowed_touch: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
forbidden_touch: []
assigned_pipeline: "B"
pipeline_modules: ["M7","M11"]
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P2"
estimated_context_tokens: 3000
---

# DB-025-0072：T-DB-006——dead_letter_queue

§16.4 T-DB-006: 写入失败入队+重试。新建 dead_letter_queue()/retry_dlq()。
