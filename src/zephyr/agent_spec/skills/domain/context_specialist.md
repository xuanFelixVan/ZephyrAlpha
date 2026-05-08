---
skill_id: SKILL-DOM-CTX-001
name: context-specialist
description: "Context engine and pipeline operations"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: Context Specialist

## CRITICAL Rules

1. Context assembly MUST follow Progressive Disclosure protocol
2. Token budget MUST be checked before assembly (max 800 tokens for L2 combined)
3. Context injection MUST use ContextPipeline v2.0.0 contract
4. Never inject stale context (freshness_score < 70 requires refresh)
5. Cold memory retrieval is on-demand only (L3)

## Core Operations

- Context assembly from blueprint + task card + session log
- Progressive Disclosure: L1(metadata) → L2(body) → L3(references)
- Token budget enforcement and downgrade
- Context injection into AI session workspace
- Dispatch table routing for subsystem navigation

## Unique Constraints

- Max combined L2 tokens: 800
- L0 Constitution always loaded (~800 tokens)
- L3 references max: 8000 tokens
- Context must be re-assembled on session switch

## Common Error Patterns

- Token budget overflow → trigger downgrade to L1-only
- Stale context injection → check freshness_score threshold
- Missing dispatch route → fallback to default (implementer)
- Context collision → two sessions loading same skill simultaneously

## Checklist

- [ ] Check token budget before assembly
- [ ] Verify freshness_score >= 70
- [ ] Route through dispatch table
- [ ] Inject context via pipeline

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| L2_COMBINED_BUDGET | 800 | Max combined L2 tokens |
| L3_MAX_BUDGET | 8000 | Max L3 reference tokens |
| FRESHNESS_THRESHOLD | 70 | Minimum freshness for injection |
| L0_CONSTITUTION_TOKENS | 800 | Always-loaded constitution size |

## References (L3, on-demand)

- ContextPipeline v2.0.0 contract
- dispatch_table specification
- session_continuity protocol
