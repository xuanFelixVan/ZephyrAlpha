---
module_id: KE-2879
status: active
title: sandbox_policy.yaml
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# sandbox_policy.yaml

sandbox_policy.yaml
sandbox_rules:
  - operation: "file_delete"
    sandbox: true
    dry_run: true
    require_confirmation: true
  - operation: "config_modify"
    sandbox: true
    diff_before_apply: true
  - operation: "external_api_call"
    sandbox: false
    cost_limit: 1.00
```

---
