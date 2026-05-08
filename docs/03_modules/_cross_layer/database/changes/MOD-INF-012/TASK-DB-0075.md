---
task_id: "DB-025-0075"
namespace: "OPS"
seq: 75
title: "T-DB-009——Prometheus/OpenTelemetry 导出 (Phase experimental，P2，2.0h)"
tags: ["fn:db", "ly:cross_layer", "T-DB-009"]
depends_on: ["DB-025-0065"]
upstream_files: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
acceptance_criteria: ["database_manager 增加 prometheus_export()", "test_database_manager 覆盖"]
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

# DB-025-0075：T-DB-009——Prometheus/OpenTelemetry 导出

§16.4 T-DB-009: database_manager 增加 prometheus_export()。
