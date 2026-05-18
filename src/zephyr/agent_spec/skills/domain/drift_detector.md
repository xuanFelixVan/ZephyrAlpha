---

skill_id: SKILL-DOM-DRF-001
name: drift-detector
description: "Drift detection, budget enforcement, auto-reconciliation, and trend analysis"
allowed-tools: [Read, Grep, Glob, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "1.0.1"
token_budget_l1: 80
token_budget_l2: 600
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Drift Detector (MOD-INF-023) — v1.0.1 battle_tested

> 蓝图: docs/03_modules/l01_infrastructure/drift-detector/blueprint.md
> 源码: src/zephyr/drift_detector/ (47 files: 45 .py + 2 .yaml)
> MCP: governance.drift_scan / governance.drift_report / governance.drift_budget
> Gate: drift_budget check_type (#19 in GateEngine)

## CRITICAL Rules

1. Cold-start STEP 4.9 auto-activates drift detector on every session entry
2. Drift detection runs on three scan levels: LIGHT (post-commit <5s), STANDARD (periodic 30min), DEEP (on-demand/phase-gate <5min)
3. Detected drift persists to SQLite drift_events (WAL mode, append-only via TRIGGER)
4. 39 detectors registered: 18 existing governance scripts + 13 new + 6 AI-engineering + 2 infra
5. Auto-fixable drift auto-repairs with pre-fix snapshot → rollback on failure; non-fixable generates structured runbook
6. Drift budget per module tier (P0=3/mo, P1=8/mo, P2=15/mo) — exhaustion blocks new construction via Gate Engine
7. Drift state machine: DETECTED → TRIAGED → ACKNOWLEDGED → RESOLVING → RESOLVED → VERIFIED (DEAD_LETTER after 24h TTL)
8. Self-check via self_check.py (pure stdlib, zero zephyr deps) — validates core files + registry parsability

## Core Operations

- **Scan**: `governance.drift_scan --level LIGHT|STANDARD|DEEP` via MCP or `scan()` in drift_engine.py
- **Budget check**: `check_budget_for_gate(module_id)` → returns allowed + remaining
- **Report**: `governance.drift_report` → current drift status + trend summary
- **AI detectors**: AIConstructionDetectors — hallucination_import, dead_code, broken_logic, duplicate_functionality, session_style_drift, knowledge_pollution
- **Reconciliation**: reconciler.py — auto-fix with optimistic concurrency (mtime guard)
- **Trend analysis**: trend_analyzer.py — velocity, resolution_rate, MTTR over 90-day windows

## Unique Constraints

- 100% AI construction + 1 human maintainer → absence mode (LENIENT/SURVIVAL) for owner offline periods
- Storm mode triggers at >50 drifts/scan → batch aggregation, pause auto-fix
- Hotfix bypass: [HOTFIX] commits auto-suppressed for 72h, then re-evaluated
- Credibility scoring per detector (fp_rate × precision × recency) → modulates alert routing
- Cascade detection: 3 fix→new-drift cycles in 30min locks auto-fix, alerts owner
- Baseline poisoning guard: cross-validation vs git + multi-baseline voting + hash chain

## Common Error Patterns

- False positive drift → mark FALSE_POSITIVE → auto-learning suppresses after 3 repeated patterns
- Stale detector → detector config outdated, update _detector_registry.yaml
- Cascading drift → cascade_detector.py interrupts repair loops
- Silent drift → self_check.py detects detector degradation (48h zero-drift = anomaly)
- Hallucination import → ai_hallucination_import uses importlib.util.find_spec() full resolution

## Checklist

- [ ] Verify STEP 4.9 cold-start activated (bootstrap + budget check)
- [ ] Run MCP governance.drift_scan (LIGHT for quick check)
- [ ] Check drift budget status for target module
- [ ] Classify and score all findings (ROI priority engine)
- [ ] Execute auto-fix for minor drifts (with pre-fix snapshot)
- [ ] Escalate critical/unfixable drifts to owner
- [ ] Run self-check (self_check.py or SelfTestVerifier)
- [ ] Update freshness scores

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DRIFT_BUDGET_P0 | 3/mo | Zero tolerance — exhaustion blocks new construction |
| DRIFT_BUDGET_P1 | 8/mo | New tasks downgraded to P3 on exhaustion |
| DRIFT_BUDGET_P2 | 15/mo | Warning only on exhaustion |
| STORM_THRESHOLD | 50 | Drifts/scan to trigger storm mode |
| DEAD_LETTER_TTL | 24h | Unhandled drift auto-escalation |
| HOTFIX_TTL | 72h | Hotfix bypass before re-evaluation |
| BASELINE_RETENTION | 10 | Snapshots retained per module |

## References (L3, on-demand)

- [blueprint.md v1.0.1](file:///d:/ZephyrAlpha/docs/03_modules/l01_infrastructure/drift-detector/blueprint.md)
- [_detector_registry.yaml](file:///d:/ZephyrAlpha/src/zephyr/drift_detector/_detector_registry.yaml)
- [E2E tests](file:///d:/ZephyrAlpha/tests/infrastructure/test_drift_e2e_pipeline.py) — 6/6 PASSED
- [Red-Blue adversarial](file:///d:/ZephyrAlpha/tests/infrastructure/test_drift_red_blue_adversarial.py) — 4/4 100% detection
- escalation protocol (MOD-INF-022)
- Gate Engine (drift_budget check_type #19)