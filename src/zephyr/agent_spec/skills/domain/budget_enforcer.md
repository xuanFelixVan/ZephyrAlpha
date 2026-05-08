---
skill_id: SKILL-DOM-BGT-001
name: budget-enforcer
description: "Budget Enforcer (MOD-INF-024) — 三维预算强制执行 + 七级预算体系 + Trust Ring"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 60
token_budget_l2: 600
author: factory-agent
---

# Domain Skill: Budget Enforcer Specialist

## CRITICAL Rules

1. All AI operations MUST pass `BudgetEngine.pre_flight_check` before execution
2. Budget dimensions: TOKEN / COST / TIME — all three MUST be checked
3. Degradation chain (NORMAL→NOTIFY→WARNING→MODEL_SWITCH→COMPRESS→MINIMAL→HALT) MUST be followed strictly
4. Trust Ring verification MUST be active for cross-agent budget operations
5. IPI Defense MUST block instruction-injection attacks on budget parameters
6. All budget decisions MUST be written to Tamper-Evident Log (audit chain)

## Core Operations

- `BudgetEngine.pre_flight_check(operation, estimated_tokens, estimated_cost) → GateDecision`
- `BudgetTracker.track(session_id, tokens_used, cost_used, time_elapsed) → TrackerSummary`
- `DegradationManager.degrade(current_level, budget_remaining) → DegradationAction`
- `TrustRingManager.verify(agent_id, operation, budget_claim) → TrustSignature`
- `BurnRateMonitor.check_rate(session_id) → BurnRateAlert`
- `PreFlightGate.evaluate(operation, budget_profile) → PreFlightDecision`

## Unique Constraints

- Seven-tier budget hierarchy: SYSTEM → ORGANIZATION → PROJECT → MODULE → SESSION → OPERATION → MODEL
- Six-level degradation chain with HALT as final guard
- Trust Ring requires 2-of-3 agent signatures for budget overrides
- Tamper-Evident Log uses SHA-256 chain hash linking (MOD-INF-020)
- Poison cascade detection (3 consecutive budget failures → auto-freeze)

## Common Error Patterns

- Budget exceeded → check DegradationManager for auto-degrade path
- Pre-flight gate blocked → verify `PreFlightGate.evaluate()` decision + budget profile
- Trust ring broken → rebuild ring with 2-of-3 valid signatures
- IPI attack detected → block operation, escalate to MOD-INF-022
- Burn rate spike → `BurnRateMonitor.check_rate()` returns alert → apply rate limit

## Checklist

- [ ] Verify BudgetEngine.pre_flight_check returned ALLOW
- [ ] Check all three dimensions (TOKEN, COST, TIME)
- [ ] Verify Trust Ring for cross-agent operations
- [ ] Enable IPI Defense on budget-critical paths
- [ ] Write all decisions to Tamper-Evident Log
- [ ] Monitor BurnRateMonitor at session and module levels

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| BUDGET_DIMENSIONS | 3 | TOKEN, COST, TIME |
| BUDGET_TIERS | 7 | System→Organization→Project→Module→Session→Operation→Model |
| DEGRADE_LEVELS | 6 | NORMAL→NOTIFY→WARNING→MODEL_SWITCH→COMPRESS→MINIMAL→HALT |
| TRUST_RING_SIGNATURES | 2-of-3 | Minimum signatures for override |
| POISON_CASCADE_THRESHOLD | 3 | Failures before auto-freeze |

## References (L3, on-demand)

- MOD-INF-024 Budget Enforcer blueprint
- MOD-INF-020 Audit Trail (Tamper-Evident Log)
- MOD-INF-022 Escalation Protocol (IPI cascade)
- MOD-INF-014 Trust Ring Manager
- PreFlightGate, BurnRateMonitor, DegradationManager
