---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "集成闭环总蓝图 — 任务系统·脚本系统·知识库及全部基础设施系统"
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

# Domain Skill: 集成闭环总蓝图 — 任务系统·脚本系统·知识库及全部基础设施系统

## CRITICAL Rules

### Core Operations
待填写

### Unique Constraints
### 19.4 AI施工KISS约束 (CT-KISS-001)

```yaml
contract: CT-KISS-001
title: "AI agent施工约束——Keep It Simple"
principle: "100%AI施工最大风险=过度工程化。本契约是AI的刹车。"

constraints:
  - "每个CT-*的实现不超过3个类（Protocol+Impl+Factory）"
  - "每个方法不超过30行——超过→拆分"
  - "不使用超过2级的继承层次"
  - "不使用元编程/metaclass除非§九DD表特批"
  - "adapter/wrapper只能有1层——不做'adapter pattern over an adapter'"
  - "抛出异常前先检查是否可以degrade而非crash"

ai_self_check:
  question: "这个实现能否删掉一半代码仍然功能完整？"
  if_yes: "删掉那一半"
```

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
