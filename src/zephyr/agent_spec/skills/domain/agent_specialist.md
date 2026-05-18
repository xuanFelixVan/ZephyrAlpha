---

skill_id: SKILL-DOM-AGT-001
name: agent-specialist
description: "Agent RBAC permission management"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Agent Specialist

## CRITICAL Rules

1. Every AI agent MUST have a defined permission level (READ_ONLY/CODE_MODIFY/ADMIN)
2. Permission checks MUST run before every file write operation
3. RBAC changes require asymmetric audit (dual-confirmation)
4. Blind spot tracking MUST be active for all agent operations
5. Adversarial resilience checks run on session boundary

## Core Operations

- Agent permission level assignment
- RBAC policy definition and enforcement
- Audit log guard monitoring
- Blind spot detection and tracking
- Adversarial resilience validation

## Unique Constraints

- READ_ONLY: no file writes, query only
- CODE_MODIFY: file writes with gate validation
- ADMIN: full access, requires asymmetric audit
- Permission escalation requires human approval

## Common Error Patterns

- Permission denied on write → check agent permission level
- Audit log gap → blind spot tracker missed an event
- RBAC bypass attempt → adversarial resilience triggered
- Asymmetric audit failure → second reviewer did not confirm

## Checklist

- [ ] Assign correct permission level per agent role
- [ ] Enable blind spot tracker
- [ ] Configure adversarial resilience
- [ ] Set up asymmetric audit for ADMIN operations
- [ ] Verify audit log guard is active

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| PERMISSION_LEVELS | 3 | READ_ONLY, CODE_MODIFY, ADMIN |
| AUDIT_REVIEWERS | 2 | Required for asymmetric audit |
| BLIND_SPOT_SCAN_INTERVAL | 300 | Scan every 5 minutes |

## References (L3, on-demand)

- RBAC policy specification (MOD-INF-018)
- asymmetric audit protocol
- adversarial resilience patterns