---
task_id: "DB-025-0077"
namespace: "OPS"
seq: 77
title: "T-DB-011——connection_leak_detector (Phase experimental，P2，1.5h)"
tags: ["fn:db", "ly:cross_layer", "T-DB-011"]
depends_on: ["DB-025-0050"]
upstream_files: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
acceptance_criteria: ["新增 connection_leak_detector()", "test_database_manager 覆盖"]
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

# DB-025-0077：T-DB-011——connection_leak_detector

§16.4 T-DB-011: database_manager 连接超时跟踪+自动回收。
