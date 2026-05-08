---
module_id: KE-module_blu-degradation_chain_yaml-000
title: degradation_chain.yaml
category: module_blueprint
---

# degradation_chain.yaml

degradation_chain.yaml
chains:
  - trigger: "cost_per_day > 5.00"
    fallback:
      - model: "deepseek-chat"
        max_tokens: 2000
        temperature: 0.3
      - model: "qwen2.5-3b-onnx"
        max_tokens: 1000
        temperature: 0.1
  - trigger: "latency_p99 > 10000"
    fallback:
      - model: "deepseek-chat"
        timeout: 5000
      - model: "qwen2.5-3b-onnx"
        timeout: 2000
```
