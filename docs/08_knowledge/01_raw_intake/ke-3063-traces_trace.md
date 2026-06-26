---
module_id: KE-2962------------------trace--000
status: active
title: traces —— 上下文管理器风格，自动注入 trace_id
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# traces —— 上下文管理器风格，自动注入 trace_id

traces —— 上下文管理器风格，自动注入 trace_id
with telemetry.traces.span("pipeline_execute") as span:
    span.set_metadata(task_id="T-001")
    # ... 业务逻辑 ...
    # 退出时自动记录 span end_time + status
