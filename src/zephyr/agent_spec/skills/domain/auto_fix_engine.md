---
skill_id: SKILL-DOM-AFX-001
name: auto-fix-engine
description: "Auto-Fix Engine (MOD-CROSS-001) — 九层修复器(L1规则引擎+L2 LLM桥接+L3 Agent OODA自愈), 七道安全防线, WAL原子修复, 16类修复器(ZombieCleaner/AllCompleter/DedupExtractor/ScaffoldRegistrar/AlignmentSyncer/DriftFixer/DepVersionFixer/ImportFixer/ConfigFixer/LLM修复/Agent自愈), Shadow Workspace预演, 修复模式学习, 级联熔断, 灰度发布, 修复预算控制, 跨Session并发协调."
allowed-tools: [Read, Grep, Glob, SearchCodebase, Write, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: Auto-Fix Engine

## CRITICAL Rules

1. Every fix MUST use atomic WAL-style write (temp file → atomic rename)
2. Seven security defenses MUST be checked before applying any fix
3. Shadow Workspace rehearsal MUST pass before production fix
4. Cascade circuit breaker MUST trip on 3 consecutive fix failures
5. Fix budget MUST be checked before each operation — no overspend
6. Cross-session concurrency MUST be coordinated via lock protocol
7. Gray-release fraction MUST be respected during rollout

## Core Operations

- L1 Rule Engine: pattern-based automatic repair
- L2 LLM Bridge: LLM-powered fix generation with prompt templates
- L3 Agent OODA Self-Heal: observe→orient→decide→act fix loop
- Sixteen fixer types (ZombieCleaner, AllCompleter, DedupExtractor, ScaffoldRegistrar, AlignmentSyncer, DriftFixer, DepVersionFixer, ImportFixer, ConfigFixer, LLM Fix, Agent Self-Heal, +5 reserved)
- WAL-style atomic fix with rollback capability
- Shadow Workspace rehearsal and diff validation
- Fix pattern learning and cataloging
- Cascade circuit breaker with escalation
- Gray-release percentage-based rollout

## Unique Constraints

- Seven security defenses are non-skippable and applied in order
- Cascade circuit breaker after 3 consecutive failures → human escalation
- Fix budget is per-session and per-module (dual limits)
- Shadow Workspace rehearsal must complete within 30s timeout
- Gray-release respects max_fraction (default 0.1 for new fixers)
- Cross-session locks are mandatory for files under concurrent fix

## Common Error Patterns

- WAL log fragmentation under high fix frequency
- Shadow Workspace timeout on large codebases
- Cascade circuit breaker false positive on unrelated failures
- Gray-release fraction drift after session restart
- Cross-session lock contention on hot files

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| CASCADE_BREAKER_THRESHOLD | 3 | Consecutive failures before escalation |
| SHADOW_TIMEOUT_SECONDS | 30 | Max rehearsal time |
| GRAY_RELEASE_DEFAULT_FRACTION | 0.1 | Default rollout fraction |
| BUDGET_DEFAULT_PER_SESSION | 50 | Max fixes per session |
| WAL_RETENTION_DAYS | 7 | WAL log retention period |

## References (L3, on-demand)

- CT-FIX-001 through CT-FIX-006 Auto-Fix Contracts
- MOD-INF-022 Escalation Protocol
- MOD-INF-023 Drift Detector
- MOD-INF-028 Script System
