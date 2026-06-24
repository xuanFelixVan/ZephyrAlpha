---
module_id: KE-2419
title: 7. 深度硬规则（蓝图隐含约束）
category: module_blueprint
---

# 7. 深度硬规则（蓝图隐含约束）

7. 深度硬规则（蓝图隐含约束）

| # | 硬规则 | 来源 |
|---|--------|------|
| 1 | **AI 不可知全阈值**: BlueprintAccessFilter 强制移除敏感数值，AI 知晓所有阈值 = 潜在越狱风险 | §24.9 #62 |
| 2 | **IMMUTABLE_CORE 清单**: kill_switch.py / error_budget_tracker.py / circuit_breaker.py / token_budget_tracker.py / graceful_shutdown.py / startup_guard.py —— 上述文件被 AI 修改 → BLOCK + Owner 双签 | §23.4 #52 |
| 3 | **出生即注册**: 任何 .py 文件被创建时必须调用 ModuleBirthRegistry.register_birth()，否则一周后被孤儿扫描标记 | §23.5 #54 |
| 4 | **蓝图-代码一致**: 代码中的关键阈值必须与蓝图 §23 中定义一致，不一致 → P0 | §24.3 #56 |
| 5 | **Owner 信任防漂移**: alert_dismissal_rate > 30% → CRITICALLY_LOW → 升级所有告警为 L3 | §24.11 #64 |
