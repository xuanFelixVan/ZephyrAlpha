---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "Context Engine 蓝图 — 四阶段上下文注入"
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


# Domain Skill: Context Engine 蓝图 — 四阶段上下文注入

## CRITICAL Rules

### Core Operations
## 7. Anti-Patterns — AI agent 绝对禁止的上下文操作

> 上下文引擎在vibe coding社区是最容易出事的模块——AI往context里乱塞东西。

| # | Anti-Pattern | 违反后果 | 正确做法 |
|---|-------------|---------|---------|
| AP1 | **无LSG审查直接注入** — CE跳过validate阶段 | 恶意prompt进入LLM上下文——不可逆 | 注入前必经CT-CE-LSG-001三层审查 |
| AP2 | **compress丢弃raw_text** — 只保留压缩文本 | LSG需raw_text做注入检测——缺失→安全失效 | compress永远保留raw_text——压缩+原始同时维护 |
| AP3 | **Flat string concat注入** — 所有上下文粘成字符串 | system/rules/knowledge/examples混一起——LLM无法区分层级 | 结构化分层注入: Layer1→4 |
| AP4 | **重复查VMS** — 同一session反复查同一Collection | Token浪费+VMS性能下降+重复注入 | Cache: 同session_id+同query→缓存(TTL=5min) |
| AP5 | **注入不存在文件路径作source** | LLM尝试读不存在文件→幻觉连锁 | VALIDATE-C01: 注入前验证source路径存在 |
| AP6 | **旧KE与新KE权重相同** | 过时知识主导上下文——压制最新经验 | Freshness Decay: created_at越新→权重越高 |
| AP7 | **Token预算耗尽后强行注入** | 模型context溢出→关键信息截断→任务失败 | L3_HARD_STOP=不追加context, 仅保留Always-on |

---

### Unique Constraints
待填写

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