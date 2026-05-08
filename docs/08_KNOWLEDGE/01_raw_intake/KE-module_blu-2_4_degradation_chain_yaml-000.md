---
module_id: KE-module_blu-2_4_degradation_chain_yaml-000
title: 2.4 degradation_chain.yaml
category: module_blueprint
---

# 2.4 degradation_chain.yaml

2.4 degradation_chain.yaml

创建 `D:\ZephyrAlpha\config\capacity\degradation_chain.yaml`：

```yaml
version: "2.6.0"
degradation:
  chain:
    - level: 0 (PRIMARY)
      model: "GLM-5.1"
      provider: "zhipu"
      
    - level: 1 (FALLBACK_A)
      model: "GLM-4-Flash"
      provider: "zhipu"
      trigger: "连续 2 个窗口异常 (OR)"
      
    - level: 2 (FALLBACK_B)
      model: "DeepSeek-V4-Pro"
      provider: "deepseek"
      trigger: "L2 fallback 同样异常"
      
    - level: 3 (LOCAL)
      model: "quantized-7B-gguf"
      provider: "local"
      trigger: "远程均不可用"

  bidirectional_switch:
    degrade_trigger:
      condition: "连续 2 个窗口异常 (OR 逻辑)"
      metric: "error_rate / latency / availability"
    restore_trigger:
      condition: "连续 3 个窗口正常 (AND 逻辑)"
      metric: "全部指标合格"

  output_truncation:
    max_tokens: 2048
    truncation_strategy: "intelligent (段落边界)"
    
  progressive_switch:
    enabled: true
    default_rate_pct_per_second: 5
    max_switch_duration_seconds: 60
```
