---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "behavioral-auditor"
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

# Domain Skill: behavioral-auditor

## CRITICAL Rules

### Core Operations
## 4. 判定模型——操作 × 许可矩阵 × 安全策略

### Unique Constraints
### 8.1 自身权限约束

- BehavioralAuditor **只读** AuditTrail——不修改任何已记录的日志
- BehavioralAuditor **不执行** Block/Alert/Rollback——只输出 VERDICT，由 Gate/AuditTrail/Rollback 执行
- BehavioralAuditor 的判定结果 MUST 写入 AuditTrail 作为不可变安全事件
- BehavioralAuditor 自身的操作 MUST 通过 AuditTrail 记录（递归自审计）

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
