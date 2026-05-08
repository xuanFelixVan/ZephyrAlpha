---
module_id: KE-module_blu-4_6_v0_9_0___8-000
title: §4.6 v0.9.0 新增8类
category: module_blueprint
---

# §4.6 v0.9.0 新增8类

§4.6 v0.9.0 新增8类

- **CircuitBreakerState**(Enum): CLOSED/OPEN/HALF_OPEN
- **ModelVersionInfo**: model_name/version/context_limit/cost_per_1k
- **ModelConfidence**: source(logprob/self_eval/ensemble)/score(0.0-1.0)/rationale
- **AIImpactAssessment**: task_id/risk_tier/human_review/rationale/nist_rmf_category
- **CostRecord**: model/module_id/input_tokens/output_tokens/cost_usd/timestamp
- **DeadLetterEntry**: task_id/reason/failure_count/last_error/timestamp
- **EmergencyFallbackPlan**: triggered/models_called/results/best_model/action
- **ABExperimentRoute**: experiment_id/task_id/variant(ExpVariant)/rationale
