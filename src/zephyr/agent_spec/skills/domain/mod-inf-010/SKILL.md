---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "MOD-INF-010"
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


# Domain Skill: MOD-INF-010

## CRITICAL Rules

### Core Operations
### 47.3 Owner多因子验证（高风险操作）

| Factor | 类型 | 实现 |
|:---|:---|------|
| Knowledge | Owner预设安全短语（Agent不可知） | 审批时附带 |
| Possession | Owner飞书/手机App推送一次性验证码 | 通道不经过Agent |
| Inherence | 行为生物识别——语言风格/决策速度/消息结构 | 被动检测 |
| Temporal | 审批请求→响应的时间间隔（AI毫秒级→人类数秒） | 时间模式检测 |

### Unique Constraints
### 11.2 核心约束

- **CWD 白名单**：只在 `src/zephyr/` / `scripts/` / `docs/` 下执行
- **ENV 白名单**：只继承明确列出的环境变量
- **timeout 强制**：默认60s，超时终止进程树
- **shell=True 禁止**：命令必须以 list[str] 形式传入

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