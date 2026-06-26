---
module_id: KE-2892----shadow-va-000
status: active
title: shadow_trust.yaml —— shadow_validator.py 产出
category: module_blueprint
ttl: permanent
---

# shadow_trust.yaml —— shadow_validator.py 产出

shadow_trust.yaml —— shadow_validator.py 产出
shadow_trust:
  last_validated: "2026-05-05T15:00:00Z"
  total_functions_in_manifest: 35
  verified: 33
  hallucinated: 2
  hallucinated_entries:
    - func: "zephyr.shared.data_utils.legacy_migrate"
      reason: "ImportError——data_utils.py 中不存在 legacy_migrate 函数"
      hallucination_source: "推断——v0.6.0 引擎升级时签名漂移导致生成了过期函数的幽灵条目"
  trust_score: 94.3%                      # 94.3% 的函数可信任——良好
  spot_check:
    sample_size: 4
    pass_rate: 100%
  recommendation: "清单可信——2个幻觉函数已自动清除。Trust Score ≥ 90%——可安全注入"
```
