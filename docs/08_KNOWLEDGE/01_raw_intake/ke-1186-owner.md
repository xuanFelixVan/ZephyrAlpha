---
module_id: KE-1100--------owner-002
status: active
title: COND-001：限额例外必须 Owner 审批
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# COND-001：限额例外必须 Owner 审批

COND-001：限额例外必须 Owner 审批

任何策略需要超出默认限额时，必须满足以下**全部条件**：

1. 提交书面申请，说明超限原因和预期收益
2. 设置比默认更严格的止损线（超限比例的 50%）
3. Owner 明确批准
4. 例外有效期 ≤ 30 天，到期自动恢复默认限额
5. 同一策略 90 天内例外申请次数 ≥ 3 次 → 标记为 `limit_inadequate`，强制重新评估该策略的限额合理性
