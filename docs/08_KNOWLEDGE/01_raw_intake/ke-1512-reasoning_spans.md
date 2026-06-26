---
module_id: KE-1422
status: active
title: 12.1 Reasoning Spans
category: module_blueprint
ttl: permanent
---

# 12.1 Reasoning Spans

12.1 Reasoning Spans

Agent 推理步骤追踪，遵循 OTel GenAI Span 定义：

```python
from opentelemetry import trace

tracer = trace.get_tracer("zephyr.capacity-assurance")

async def trace_reasoning(agent_name: str, task: str, steps: list[str]):
    with tracer.start_as_current_span("agent.reasoning") as span:
        span.set_attribute("gen_ai.system", "zephyr")
        span.set_attribute("gen_ai.request.model", agent_name)
        span.set_attribute("agent.task", task)
        span.set_attribute("agent.steps.count", len(steps))
        for i, step in enumerate(steps):
            span.add_event(f"reasoning.step.{i}", {"description": step})
```
