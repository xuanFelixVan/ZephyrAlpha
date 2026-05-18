---

skill_id: SKILL-DOM-BLU-001
name: master-blueprint
description: "Master blueprint interpretation"
allowed-tools: [Read, Grep, Glob, Task(search)]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Master Blueprint

## CRITICAL Rules

1. SYS-MASTER-001 is the apex of the three-tier blueprint pyramid
2. Read §0 dispatch table first (~400 tokens) to locate subsystem
3. Conflict resolution chain: PS-STD-005 > SYS-MASTER-001 > MOD-MASTER-001 > module blueprint
4. Never generate code from blueprints directly—blueprints define boundaries, not implementations
5. All construction MUST pass G0-G7 gates (§2), no exceptions

## Core Operations

- Cold-start navigation via §0 dispatch table
- Blueprint tier navigation: Level 0 → Level 1 → Level 2
- Cross-module integration via MOD-MASTER-001 contracts
- Blueprint version validation and drift detection
- ADR (Architecture Decision Record) creation

## Unique Constraints

- 102 chapters covering full system topology
- §0 ≈ 400 tokens for rapid cold-start
- BlueprintUpdate v1.0.0 contract for version tracking
- New modules MUST register in blueprint-registry.yaml

## Common Error Patterns

- Reading full blueprint instead of §0 dispatch → token waste
- Bypassing MOD-MASTER-001 for cross-module changes → integration break
- Using outdated blueprint version → code-design drift
- Skipping gate validation → rejected merge

## Checklist

- [ ] Read §0 dispatch table for subsystem routing
- [ ] Navigate to target module blueprint via tier chain
- [ ] Check MOD-MASTER-001 for cross-module contracts
- [ ] Validate blueprint version freshness
- [ ] Record architectural decisions as ADR

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| BLUEPRINT_TIERS | 3 | Level 0 (system) → Level 1 (domain) → Level 2 (module) |
| DISPATCH_TOKENS | 400 | §0 cold-start reading size |
| TOTAL_CHAPTERS | 102 | Full SYS-MASTER-001 coverage |

## References (L3, on-demand)

- SYS-MASTER-001 blueprint
- MOD-MASTER-001 integration contracts
- blueprint-registry.yaml