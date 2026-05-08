---
module_id: KE-module_blu-2_4_canary_deployment__d-019-0-000
title: 2.4 Canary Deployment (D-019-09)
category: module_blueprint
---

# 2.4 Canary Deployment (D-019-09)

2.4 Canary Deployment (D-019-09)

```
Phase 1 — 20%: deploy to 20% sessions, 50 operations minimum
Phase 2 — 50%: if Welch's t-test p<0.05 + no regression, ramp
Phase 3 — 100%: full rollout after 200 operations + gate pass
Auto-rollback: error_rate > baseline × 1.5 → instant revert
```
