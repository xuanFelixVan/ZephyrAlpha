---
module_id: KE-2123
status: active
title: 3.5 #24: TokenValueAttribution (M-30)
category: module_blueprint
ttl: permanent
---

# 3.5 #24: TokenValueAttribution (M-30)

3.5 #24: TokenValueAttribution (M-30)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\token_value_attribution.py`

实现 `TokenValueAttribution` 类（蓝图 L2507-2584）：
- 按任务类型区分消费：`stable_business` / `experiment` / `debugging` / `unknown`
- `compute_roi(task_type, tokens_consumed, task_success: bool) -> float`
- `generate_monthly_roi_report() -> ROISummary`
- 蓝图 L2519-2585 算法完整实现
