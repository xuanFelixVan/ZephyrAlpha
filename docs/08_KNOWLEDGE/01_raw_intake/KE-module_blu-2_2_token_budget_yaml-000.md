---
module_id: KE-module_blu-2_2_token_budget_yaml-000
title: 2.2 token_budget.yaml
category: module_blueprint
---

# 2.2 token_budget.yaml

2.2 token_budget.yaml

创建 `D:\ZephyrAlpha\config\capacity\token_budget.yaml`：

```yaml
version: "2.6.0"
token_budget:
  levels:
    - level: L0 (GLOBAL)
      budget_id: "global_total"
      tokens_per_window: 10000000
      window_size_seconds: 86400
      algorithm: "token_bucket"
      burst_ratio: 1.5
    
    - level: L1 (MODULE)
      budget_id_pattern: "module_{module_id}"
      tokens_per_window: 1000000
      window_size_seconds: 86400
      algorithm: "token_bucket"
    
    - level: L2 (AGENT)
      budget_id_pattern: "agent_{agent_id}"
      tokens_per_window: 100000
      window_size_seconds: 3600
      algorithm: "sliding_window"
    
    - level: L3 (MODEL)
      budget_id_pattern: "model_{model_name}"
      tokens_per_window: 500000
      window_size_seconds: 3600
      algorithm: "token_bucket"
      cost_tracking: true

  preflight_estimation:
    enabled: true
    algorithm: "heuristic + linear_regression"
    calibration_window: 1000

  cycle_reset:
    modes: ["sliding_window", "natural_cycle"]
    natural_cycles: ["hour", "day", "week"]
```
