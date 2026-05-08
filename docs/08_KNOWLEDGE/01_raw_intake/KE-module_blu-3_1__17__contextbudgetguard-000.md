---
module_id: KE-module_blu-3_1__17__contextbudgetguard-000
title: 3.1 #17: ContextBudgetGuard
category: module_blueprint
---

# 3.1 #17: ContextBudgetGuard

3.1 #17: ContextBudgetGuard

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\context_budget_guard.py`

实现 `ContextBudgetGuard` 类（蓝图 L2000-2022）：
- `check_watermark(current_pct: float) -> WatermarkLevel`：
  - ≤80% → NORMAL
  - 80%-90% → WARNING (记录告警)
  - 90%-100% → CRITICAL (拒绝更多上下文注入)
- 新增 SLI：`CAP-CTX-001` (context_watermark_breach)
- 蓝图 L2000-2035 YAML 配置完整实现
