---
skill_id: SKILL-DOM-FBL-001
name: feedback-specialist
description: "Feedback loop and evolution engine"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: Feedback Specialist

## CRITICAL Rules

1. Every skill execution MUST complete the five-stage feedback loop
2. Predict → Detect → Diagnose → Act → Verify (PDDAV cycle)
3. Anomaly detection triggers MUST escalate to MOD-INF-022
4. Feedback events MUST be written to Audit Trail (MOD-INF-020)
5. Loop failure = skill execution failure = rollback

## Core Operations

- Five-stage feedback loop orchestration
- Anomaly prediction and detection
- Root cause diagnosis
- Corrective action execution
- Fix verification and loop closure

## Unique Constraints

- All 5 stages must complete before skill exits
- Stage timeout: 30s per stage
- Escalation on stage 3+ failure
- Results feed into SkillFreshness scoring

## Common Error Patterns

- Loop timeout → stage took longer than 30s
- Diagnosis inconclusive → escalate to human
- Fix verification failed → rollback + re-diagnose
- Missing audit trail → feedback event not recorded

## Checklist

- [ ] Execute Predict stage
- [ ] Execute Detect stage
- [ ] Execute Diagnose stage
- [ ] Execute Act stage
- [ ] Execute Verify stage
- [ ] Write feedback summary to audit trail

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| STAGE_TIMEOUT | 30 | Max seconds per feedback stage |
| MAX_RETRY | 3 | Max retry attempts for fix |
| LOOP_STAGES | 5 | Predict-Detect-Diagnose-Act-Verify |

## References (L3, on-demand)

- PDDAV loop specification
- escalation protocol (MOD-INF-022)
- anomaly detection patterns
