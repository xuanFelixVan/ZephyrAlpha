---
module_id: KE-1875
status: active
title: 2.3 sandbox_policy.yaml
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.3 sandbox_policy.yaml

2.3 sandbox_policy.yaml

创建 `D:\ZephyrAlpha\config\capacity\sandbox_policy.yaml`：

```yaml
version: "2.6.0"
sandbox:
  isolation:
    namespace_pattern: "CAP-SANDBOX-NS-{module}-{agent_id}"
    process_isolation: "subprocess"

  resource_limits:
    cpu:
      max_time_seconds: 300
      max_percent: 50
    memory:
      max_mb: 512
      swap_mb: 0
    disk:
      max_mb: 100
      read_only_paths: ["/system", "/config"]
    network:
      allowed: false

  timeout:
    hard_timeout_seconds: 600
    kill_signal: "SIGKILL"

  policy_lifecycle:
    valid_state_transitions:
      draft: [active]
      active: [deprecated]
      deprecated: [archived]
    states: ["draft", "active", "deprecated", "archived"]

  modes:
    - mode: STRICT
      description: "完全隔离执行"
    - mode: REPORT_ONLY
      description: "执行不隔离，记录行为日志"
```
