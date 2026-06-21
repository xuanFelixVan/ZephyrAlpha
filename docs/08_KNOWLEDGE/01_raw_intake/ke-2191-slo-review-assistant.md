---
module_id: KE-2098
status: active
title: 3.3 #5: SLOReviewAssistant
category: module_blueprint
---

# 3.3 #5: SLOReviewAssistant

3.3 #5: SLOReviewAssistant

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\slo_review_assistant.py`

实现 `SLOReviewAssistant` 类：
- `generate_quarterly_review() -> SLOReviewReport`：
  - 实际 p99 < target × 0.3 → 建议 tighten
  - 实际 p99 > target × 1.2 → 建议 relax
  - error_budget_remaining > 0.95 → 建议 retire（考虑退役此 SLI）
- `auto_retire_stale_slis(staleness_days=90)`：自动标记>90天预算消耗<5%的SLI为"待退役审查"
- 蓝图 L1299-1317 完整实现
