---

skill_id: SKILL-DOM-RBK-001
name: rollback-specialist
description: "Rollback/undo/revert with Git-native + SQLite Checkpoint dual-track infrastructure. Covers four-level rollback (full_revert/partial_revert/discard/hard_reset), failure signal triage, forward-fix, kill switches, forensic audit, adversarial AI safety."
allowed-tools: [Read, Grep, Glob, RunCommand, Write]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Rollback Specialist

## CRITICAL Rules

1. Every write operation MUST create a checkpoint before execution
2. Four-level rollback: full_revert > partial_revert > discard > hard_reset
3. Failure signals triaged as: hard (blocking), soft (advisory), transient (retry)
4. Auto-rollback triggers on post-failure gate verification failure
5. Rollback operations MUST be logged to audit trail (MOD-INF-020)
6. Kill switch MUST be available for runaway rollback chains

## Core Operations

- Git-native checkpoint creation and rollback
- SQLite dump checkpoint management
- Four-level rollback execution (full_revert/partial_revert/discard/hard_reset)
- Failure signal triage and classification
- Forward-fix after soft failures
- Kill switch activation for runaway operations
- Forensic audit of rollback history
- Loop detection for cascading rollbacks

## Unique Constraints

- Dual-track: Git-native + SQLite checkpoint — must maintain consistency between both
- Auto-rollback requires post-rollback gate verification (G0-G9 sequence)
- Agent Cooldown: minimum 30s between consecutive rollbacks
- Loop Detector: max 3 consecutive rollbacks before human escalation
- Rollback audit trail is tamper-evident (append-only)

## Common Error Patterns

- Checkpoint drift: Git state and SQLite checkpoint out of sync
- Partial rollback failure: some files reverted, others stuck
- Cascading rollback: one rollback triggers dependent rollbacks
- Kill switch false positive: triggered on normal recovery operation
- Loop detector threshold exceeded: 3+ consecutive rollbacks

## Checklist

- [ ] Verify checkpoint exists before rollback
- [ ] Determine rollback level (full/partial/discard/hard_reset)
- [ ] Execute rollback with appropriate level
- [ ] Run post-rollback gate verification (G0-G9)
- [ ] Log rollback to audit trail
- [ ] Escalate if loop detector threshold exceeded

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| MAX_CONSECUTIVE_ROLLBACKS | 3 | Loop detector threshold |
| AGENT_COOLDOWN_SECONDS | 30 | Minimum time between rollbacks |
| CHECKPOINT_FRESHNESS_TTL | 3600 | Checkpoint max age in seconds |
| AUTO_ROLLBACK_TRIGGER | post_gate_fail | Triggers on gate failure |

## References (L3, on-demand)

- MOD-INF-021 Rollback System Blueprint
- MOD-INF-020 Audit Trail Integration
- MOD-INF-007 Gate Engine Verification