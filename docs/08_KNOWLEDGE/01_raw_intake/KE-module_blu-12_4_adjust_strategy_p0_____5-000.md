---
module_id: KE-module_blu-12_4_adjust_strategy_p0_____5-000
title: 12.4 Adjust Strategy P0（遗漏 #5）
category: module_blueprint
---

# 12.4 Adjust Strategy P0（遗漏 #5）

12.4 Adjust Strategy P0（遗漏 #5）

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-A1 | downweight_slot 生效 | 默认权重 lessons=0.1 | adjust(signal downweight lessons magnitude 0.05) | 新权重 lessons=0.05，ttl 60min |
| P0-A2 | ttl 到期回默认 | 上一步后 | sleep(ttl+1)，再 build | lessons 权重回 0.1 |
| P0-A3 | 总预算守恒 | 任意 signal | adjust | Σ slot_budgets = 1.0 ±0.001（其他 slot 按比例吸收） |
| P0-A4 | 审计日志落盘 | 任意 adjust | 检查 `logs/ce_feedback.log` | 含 task_id/signal/effective_from/new_budgets |
