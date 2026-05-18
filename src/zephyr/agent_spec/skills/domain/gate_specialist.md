---

skill_id: SKILL-DOM-GAT-001
name: gate-specialist
description: "Gate engine rule and policy management"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Gate Specialist

## CRITICAL Rules

1. G0-G9 gate sequence MUST be executed in order
2. Any gate failure = HALT, no bypass allowed
3. Gate results MUST be written to GateCheckResult v1.0.0 contract
4. Skipped gates = rejected merge (SYS-MASTER-001 §2)
5. Gate configuration changes require ADR

## Core Operations

- Gate engine initialization and configuration
- Sequential gate execution (G0 → G9)
- Gate result collection and aggregation
- Pass/fail decision and halt enforcement
- Gate registry synchronization

## Unique Constraints

- Gates execute in strict sequence: cannot skip G3 to run G4
- Each gate has defined execution plane (pre-commit/CI/runtime)
- Gate timeout: 60s per gate
- Failed gates auto-escalate to MOD-INF-022

## Common Error Patterns

- Gate timeout → check rule complexity, optimize
- False positive → rule too strict, tune threshold
- Gate registry drift → gate file not synced with registry
- Circular dependency → gate references itself

## Checklist

- [ ] Verify gate sequence order
- [ ] Check all gates have timeout configured
- [ ] Validate GateCheckResult schema
- [ ] Sync gate registry with actual files
- [ ] Document any gate configuration changes in ADR

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| GATE_COUNT | 10 | G0 through G9 |
| GATE_TIMEOUT | 60 | Max seconds per gate |
| EXECUTION_PLANES | 3 | pre-commit, CI, runtime |

## References (L3, on-demand)

- G0-G9 gate specifications
- GateCheckResult v1.0.0 contract
- gate registry (_registry.yaml)