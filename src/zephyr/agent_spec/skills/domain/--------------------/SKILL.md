---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "孤儿判定子系统蓝图 — 资产生死判决引擎"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: 孤儿判定子系统蓝图 — 资产生死判决引擎

## CRITICAL Rules

### Core Operations
待填写

### Unique Constraints
### 7.4 性能约束

| 指标 | 目标 | 实现 |
|------|------|------|
| 图构建时间 | < 10s（全项目） | 增量构建 + 缓存 |
| 单文件可达性查询 | < 100ms | reverse_index 预计算 |
| 图内存占用 | < 200MB | 只存签名不存内容 |
| 增量更新 | < 2s（单文件变更） | 受影响子图重算 |

---

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