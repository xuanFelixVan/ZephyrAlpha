---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "漂移运行时检测蓝图 — Git-native Drift Detection + AI 施工专项"
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


# Domain Skill: 漂移运行时检测蓝图 — Git-native Drift Detection + AI 施工专项

## CRITICAL Rules

### Core Operations
待填写

### Unique Constraints
### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 先干后验模式 | 漂移检测是后验的核心组件——AI 先干，drift detector 后验 |
| 80+ 现有治理脚本 | 不重写，整合为运行时检测的检测器 |
| 能自动绝不人工 | 可自动修复的漂移自动修，不可自动修复的生成修复建议 |
| 100% AI 施工 | 需覆盖 AI 特有的漂移模式：幻觉引用、跨 session 不一致、死码积累、知识污染 |
| 1人+AI 维护 | 检测器必须自己能发现自己的问题（自漂移检测），Owner 只看摘要 |

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