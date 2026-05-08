---
module_id: KE-module_blu-5_3______________policy____d-0-005
title: 5.3 三角闭环——审计反馈回写 Policy（决策 D-020-08）
category: module_blueprint
---

# 5.3 三角闭环——审计反馈回写 Policy（决策 D-020-08）

5.3 三角闭环——审计反馈回写 Policy（决策 D-020-08）

> **决策 D-020-08**（新增）：对接 ADR-0010 §4.4 "Runtime → Policy 反馈"接口。审计 Trail 作为 Runtime 层的"数据生产者"，定期聚合异常/漂移/权限违规数据，通过 `feedback_to_policy.py` 推送至 Policy 层，驱动规则演进。

```yaml
feedback_loop:
  # ADR-0010 §4.4 接口 ④：Runtime → Policy（反馈）
  producer: "audit_trail.aggregator"
  consumer: "feedback_to_policy.py"  # Policy 层 PR 生成器

  aggregation:
    schedule: "daily 00:30 UTC"
    dimensions:
      - top_anomalies: "当日 Top 10 异常事件"
      - drift_summary: "当日蓝图漂移摘要——按模块分组"
      - permission_trends: "本周权限违规趋势"
      - cost_anomalies: "单操作 > $0.50 的高成本事件"

  output:
    format: "Markdown policy_evolution_pr_body"
    target: "GitHub PR → docs/01_policies_and_standards/ 对应规则文件"
    approval: "human_gated——Owner 审批后合并"

  # ADR-0010 激活路径 Sprint 11：L6 OPA Gatekeeper + D2-B 反馈回写闭环
  activation_sprint: "Sprint 11"
```
