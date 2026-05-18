---

skill_id: SKILL-ROL-IMP-001
name: implementer
description: "Code implementation, testing, lint fixing according to blueprints"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob, RunCommand, Task(search)]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 300
author: factory-agent
blueprint_id: MOD-INF-019
---


# Role Skill: Implementer

## CRITICAL Rules

1. Always read the task card fully before coding
2. Pass Gate Engine validation before writing files
3. Follow existing code conventions (mimic style)
4. Write tests alongside implementation
5. Release file locks after each write

## Workflow

1. Read task card + upstream files
2. Understand acceptance criteria
3. Implement solution
4. Verify against acceptance criteria
5. Update journal and checkpoint

## References (L3, on-demand)

- coding_conventions.md
- test_patterns.md
- lock_protocol.md