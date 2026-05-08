---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "MOD-INF-005"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: MOD-INF-005

## CRITICAL Rules

### Core Operations
### 94.3 硬件故障应急操作

```
SSD 濒死 (SMART warning):
  1) 即时全量备份 (§59.1) → 外部硬盘+云存储
  2) 非必要进程停止——只保留实时监控
  3) 下单备用 SSD → 到货后 dd clone 或 重建环境(§69.2)
  4) Owner 收到物理行动指令: "买新SSD——型号: Samsung 990 Pro 2TB"
```

---

### Unique Constraints
### 56.2 杠杆约束

| 约束 | 上限 |
|------|:--:|
| 单一资产: Max | 25% of AUM/Notional |
| Sector 上限 | 40% (AUM) |
| Cash reserve | ≥5% of AUM |

### Common Error Patterns
待填写

## Checklist

- [ ] Verify blueprint before implementation
- [ ] Check upstream dependencies
- [ ] Validate against acceptance criteria
- [ ] Run gate engine checks (G0-G9)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_TIMEOUT | 30 | Default operation timeout (seconds) |

## References (L3, on-demand)

- module_blueprint.md
- integration_guide.md
- troubleshooting.md
