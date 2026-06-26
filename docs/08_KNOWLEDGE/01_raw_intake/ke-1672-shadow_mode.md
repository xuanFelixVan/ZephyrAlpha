---
module_id: KE-1582
status: active
title: 18.1 Shadow Mode 三级激活体系
category: module_blueprint
ttl: permanent
---

# 18.1 Shadow Mode 三级激活体系

18.1 Shadow Mode 三级激活体系

```yaml
gate_activation_stages:
  - stage: shadow
    description: "门禁评估→记录结果→不阻断任务"
    duration: "≥50次评估 且 ≥7天"
    exit_criteria: "误报率<5% 且 P0漏检率<1%"
  - stage: beta_enforce
    description: "门禁评估→P0阻断→P1/P2仅告警"
    duration: "≥100次评估 且 ≥14天"
    exit_criteria: "P0误报率<1% 且 override次数<3"
  - stage: full_enforce
    description: "门禁评估→P0/P1阻断→P2告警"
    exit_criteria: "连续30天无override"

activation_lifecycle: shadow → beta_enforce → full_enforce
