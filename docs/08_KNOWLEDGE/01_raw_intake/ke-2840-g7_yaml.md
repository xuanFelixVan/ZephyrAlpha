---
module_id: KE-2742
status: active
title: G7 YAML 规则
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# G7 YAML 规则

G7 YAML 规则

```yaml
gate_name: "Task-G7: Delivery Gate"
gate_level: "G7"
required_context: ["acceptance_criteria", "zalp_errors", "task_card_md", "task_repo_mm"]
check_method: "verify_delivery_completeness"
checks:
  step1_ac_pass: "所有AC status=passed"
  step2_zalp_clean: "zalp_error_count==0"
  step3_dual_track: "task_repo与.md字段一致"
```
