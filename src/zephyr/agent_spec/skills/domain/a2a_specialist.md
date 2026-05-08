---
skill_id: SKILL-DOM-A2A-001
name: a2a-protocol
description: "A2A Agent-to-Agent Coordination Protocol (MOD-INF-025)"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: A2A Protocol Specialist

## CRITICAL Rules

1. All A2A communication MUST be traceable — every message, every state transition written to AuditTrail
2. Agent operations MUST NOT cause irreversible system damage (delete, drop_table, rm -rf, mass_update, shutdown)
3. Cross-agent data sharing REQUIRES explicit consent grant — forbidden by default
4. All Tasks MUST have a deadline — timeout triggers auto-escalate, no indefinite blocking
5. Agent failure MUST NOT auto-propagate — CascadeGuard must circuit-break within 3 failures
6. Agent permissions MUST follow least-privilege — no overreach

## Core Operations

- Agent discovery and registration (Layer 1)
- Message routing and state management (Layer 2)
- Coordination: deadlock detection, livelock detection, cascade circuit-break (Layer 3)
- Identity verification (HMAC-SHA256)
- RBAC/Audit/Escalation three-way bridge

## Unique Constraints

- Agent long-term memory capped at 100 items — oldest auto-forgotten
- 9-state task state machine for coordination lifecycle
- Supervisor schedules with conflict detection and resolution
- Phase 2+ auto-activation: no manual trigger needed post-bootstrap

## Common Error Patterns

- Agent registration failed → check identity verifier (HMAC-SHA256)
- Deadlock detected → check resource dependency graph
- Livelock detected → check retry-loop without state change
- Cascade guard tripped → investigate root agent failure (5 Whys)
- Consent denied → cross-agent boundary without explicit grant

## Checklist

- [ ] Verify agent identity before registration
- [ ] Set task deadline (no infinity)
- [ ] Configure CascadeGuard threshold (default: 3)
- [ ] Enable AuditTrail for all A2A messages
- [ ] Set memory cap (default: 100)
- [ ] Verify RBAC/Audit/Escalation bridges active

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| CASCADE_BREAK_THRESHOLD | 3 | Failures before circuit opens |
| MEMORY_CAP | 100 | Max long-term memories per agent |
| TASK_STATES | 9 | State machine states |
| PROTOCOL_LAYERS | 3 | L1 Discovery / L2 Communication / L3 Coordination |

## References (L3, on-demand)

- MOD-INF-025 A2A Protocol blueprint
- Constitution (CONSTITUTION.md) — 7 articles
- G-CT-008 cross-module integration contract
- RBAC bridge (MOD-INF-018)
- Audit bridge
- Escalation bridge (MOD-INF-022)
