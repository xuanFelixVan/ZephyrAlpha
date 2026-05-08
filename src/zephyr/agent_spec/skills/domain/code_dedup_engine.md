---
skill_id: SKILL-DOM-DED-001
name: code-dedup-engine
description: "Code deduplication engine — Monoculture immunity (BRS 0-100), atomic WAL-style fix, 25-dimension closed loop, 66 modules across 3 waves. Covers lexical/AST/semantic detection, auto-fix with safety gates, cross-boundary clone awareness, decision audit trail."
allowed-tools: [Read, Grep, Glob, SearchCodebase]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: Code Dedup Engine

## CRITICAL Rules

1. Every fix MUST use atomic WAL-style write (temp file → atomic rename)
2. Monoculture immunity check (BRS) MUST run before each dedup sweep
3. 25-dimension closed loop MUST complete before marking a dedup done
4. Safety gates MUST pass before auto-fix is applied
5. Cross-boundary clones MUST be detected across module boundaries
6. All dedup decisions MUST be logged in audit trail

## Core Operations

- Lexical similarity detection (token-level)
- AST structural similarity detection (tree-level)
- Semantic similarity detection (embedding-level)
- WAL-style atomic fix execution
- Monoculture immunity score (BRS 0-100) calculation and check
- 25-dimension quality check (correctness, performance, maintainability, security, style × 5)
- Cross-boundary clone awareness across module boundaries
- Decision audit trail with rollback capability

## Unique Constraints

- BRS must be >= 70 before auto-fix can proceed
- WAL writes are append-only until fix is committed
- 25-dimension check is non-skippable — all 25 must pass
- Cross-boundary clones require module owner sign-off
- Rollback of a dedup fix restores original with full audit trail

## Common Error Patterns

- False positive dedup (similar code with different semantics)
- BRS threshold too low causing monoculture vulnerability
- WAL log corruption on concurrent access
- Cross-boundary clone missed due to import alias differences
- 25-dimension check false failure on edge cases

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| BRS_MIN_THRESHOLD | 70 | Minimum monoculture immunity score |
| WAL_LOG_RETENTION | 30 | Days to retain WAL logs |
| 25D_CHECK_COUNT | 25 | Number of quality dimensions |
| WAVES_TOTAL | 3 | Total dedup waves (lexical/AST/semantic) |
| MODULES_COVERED | 66 | Modules in scope across 3 waves |
