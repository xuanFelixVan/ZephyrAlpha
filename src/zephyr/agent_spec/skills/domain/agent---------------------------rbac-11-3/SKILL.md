---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "Agent 身份与权限系统蓝图 — 七层纵深防御 + 六横切面 RBAC 11.3"
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

# Domain Skill: Agent 身份与权限系统蓝图 — 七层纵深防御 + 六横切面 RBAC 11.3

## CRITICAL Rules

### Core Operations
# H02: Git状态一致性——write操作前确认git status clean

### Unique Constraints
### 1.3 运行场景约束（决策输入）

| 约束 | 影响 |
|------|------|
| 100% AI 开发，多 IDE 并发（TRAE / Cursor / RooCode） | 权限系统必须跨 IDE 统一，不能依赖单一 IDE 的审批机制 |
| 同时开启 10+ 对话 | 阻塞式审批 = 10 个对话全卡死——绝对不可接受 |
| 1 人 + AI，99% AI 维护 | 人工审批是最稀缺资源——必须最小化，能自动绝不人工 |
| 决策围绕原则/目标驱动 | 权限判定应该是规则驱动的自动决策，不是人工审批 |
| 100% AI 施工 = 权限系统自身也是 AI 写的 | **权限层核心必须不可变**——AI 不能修改自己的护栏 |
| **Owner 可能缺席（出差/休假/离线）** | **系统必须具备 Owner 缺席时的自治保守模式**——Owner超时未审阅→自动降权，防止无人值守时裸奔 |
| **Vibe Coding AI 零记忆重启（§5.1）** | **权限规则必须自解释**——每个规则旁边写清"为什么、谁定的、什么时间定的"，AI读完即可执行，不依赖跨session记忆 |

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
