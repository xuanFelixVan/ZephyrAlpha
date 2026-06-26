---
module_id: KE-2553
status: active
title: ai_behavior —— 记录每次模型调用
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# ai_behavior —— 记录每次模型调用

ai_behavior —— 记录每次模型调用
telemetry.ai_behavior.record(
    model_id="gpt-4",
    input_tokens=1200,
    output_tokens=350,
    duration_ms=2500.0,
    cost_usd=0.015,
    prompt_template_id="task_decomposition_v2",
    prompt_version="1.3"
)
