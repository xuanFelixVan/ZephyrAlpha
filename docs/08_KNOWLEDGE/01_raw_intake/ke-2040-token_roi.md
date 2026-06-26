---
module_id: KE-1949
status: active
title: 2.8 Token ROI 模型
category: module_blueprint
ttl: permanent
---

# 2.8 Token ROI 模型

2.8 Token ROI 模型

```yaml
token_roi:
  description: "不只算花了多少 token——算这些 token 产出了什么。Token 价值归因是 FinOps for AI 的核心。"
  outcome_metrics:
    - metric: "lines_of_code_per_1k_tokens"
      description: "每 1000 token 产出的代码行数"
      baseline_week_1: null     # Week 1 建立基线

    - metric: "files_completed_per_1k_tokens"
      description: "每 1000 token 完成的文件数"

    - metric: "blueprint_sections_per_1k_tokens"
      description: "每 1000 token 产出的蓝图章节数"

    - metric: "debug_rounds_per_task"
      description: "每任务的 debug 轮次——越高说明首次生成质量越差"

  trend_alert:
    roi_drop_30_percent: "ROI 下降 30% 以上 → 告警 Owner '施工效率下降，建议检查 Prompt 质量'"

  integration: "与 Session Log（docs/09_audit/session_logs/）联动，自动计算"
```
