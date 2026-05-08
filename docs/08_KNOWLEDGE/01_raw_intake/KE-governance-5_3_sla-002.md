---
module_id: KE-governance-5_3_sla-002
title: 5.3 SLA 与格式要求
category: governance_rule
---

# 5.3 SLA 与格式要求

5.3 SLA 与格式要求

```yaml
sla:
  max_delay_hours: 24
  escalation: block_further_work
  reminder_after_hours: 12
format_requirements:
  - Owner 在 Session Log 的 confirmation_section 签字
  - Git commit message 必须包含 "Confirmed-By: Owner"
warning_review:
  - 每次 commit 前必须展示 WARNING 清单，强制 AI 阅读并确认
  - Owner 必须在 Session Log 中确认已审阅，作为 DoD 的一部分
  - WARNING 累计超过 5 条则禁止 commit
```

---
