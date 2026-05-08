---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "可执行 Agent Spec 蓝图 — 蓝图→Skill 升级引擎"
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

# Domain Skill: 可执行 Agent Spec 蓝图 — 蓝图→Skill 升级引擎

## CRITICAL Rules

### Core Operations
待填写

### Unique Constraints
### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 多 IDE 并发（TRAE/Cursor/RooCode） | Skill 加载机制必须跨 IDE 统一——AGENTS.md 是唯一所有 IDE 都读的文件；Skill 格式遵循 agentskills.io 开放标准确保跨工具兼容 |
| 10+ 并发对话 | 不能加载全部 Skill——Progressive Disclosure 三层递进，按需加载 |
| 1 人 + AI 施工 + AI 维护 | Domain Skill 按模块创建（来一个模块配一个 Skill），Role Skill 固定 3 个角色模式 |
| 14 层 × 多模块扩展 | 新模块创建时同步创建其 Domain Skill——框架支持 100+ 模块的渐进扩展 |
| 跨 AI 模型（DeepSeek/GLM/Kimi/Qwen/Claude） | Skill 格式必须对多模型友好——结构化表格 + 代码块 > 长篇散文 |

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
