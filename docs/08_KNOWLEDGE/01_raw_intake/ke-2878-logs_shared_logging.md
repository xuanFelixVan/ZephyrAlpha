---
module_id: KE-2778-------shared-logging-000
status: active
title: logs —— 复用 shared.logging，增加便捷方法
category: module_blueprint
---

# logs —— 复用 shared.logging，增加便捷方法

logs —— 复用 shared.logging，增加便捷方法
telemetry.logs.info("task dispatched", task_id="T-001")
telemetry.logs.warning("rate limit approaching", current_rate=95)
telemetry.logs.error("pipeline failed", trace_id=trace_id)
