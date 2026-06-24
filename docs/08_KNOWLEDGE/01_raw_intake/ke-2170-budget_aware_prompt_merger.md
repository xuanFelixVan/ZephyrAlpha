---
module_id: KE-2078
status: active
title: 3.2 #40: BudgetAwarePromptMerger (M-37)
category: module_blueprint
---

# 3.2 #40: BudgetAwarePromptMerger (M-37)

3.2 #40: BudgetAwarePromptMerger (M-37)

文件：`D:\ZephyrAlpha\src\zephyr\shared\budget_aware_prompt.py`

实现 `BudgetAwarePromptMerger` 类：
- `full_build` 模式（Token Budget > 70% + Error Budget healthy）
- `essential_only` 模式（Token Budget 30%~70% + warning）
- `minimal_viable` 模式（Token Budget < 30% + critical/emergency）
- `merge(task, budget_status)`: 根据预算选择施工模式
