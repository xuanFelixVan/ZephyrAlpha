---
skill_id: SKILL-DOM-TEL-001
name: system-telemetry
description: "System-wide observability — 9 subsystems (metrics/logs/traces/ai_behavior/archive/profiles/health/alerts/schema) via unified Telemetry facade. Three closed loops (AI dev/ops/governance). Aligned with OTel GenAI semantic conventions."
allowed-tools: [Read, Grep, Glob]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: System Telemetry

## CRITICAL Rules

1. ALL subsystem metrics MUST flow through Telemetry facade — no direct writes
2. Three closed loops (dev/ops/governance) MUST each have their own aggregation pipeline
3. OTel semantic conventions MUST be followed for all GenAI spans
4. Telemetry data MUST NOT contain PII or secrets
5. Health checks MUST run on a minimum 30s interval
6. Alerts MUST have a defined threshold and escalation path

## Core Operations

- Unified metric collection via Telemetry facade (9 subsystems)
- AI behavior tracing with OTel GenAI semantic convention alignment
- Health check execution with configurable intervals
- Alert generation with threshold and escalation rules
- Archive rotation and retention policy enforcement
- Performance profile snapshot and comparison
- Schema version management for telemetry data

## Unique Constraints

- Facade is single entry point — no direct subsystem access
- Three closed loops never cross-contaminate data
- PII scrubber runs before any telemetry export
- Alert escalation requires human acknowledgement within TTL
- Archive retention minimum 90 days for compliance

## Common Error Patterns

- Metric naming collision across subsystems
- OTel span parent-child relationship mismatch
- Alert storm under high load (suppression missing)
- PII leak through custom dimension tags
- Archive write failure under retention pressure

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| HEALTH_CHECK_INTERVAL_S | 30 | Minimum seconds between health checks |
| ARCHIVE_RETENTION_DAYS | 90 | Minimum archive retention |
| ALERT_ESCALATION_TTL_S | 300 | Alert acknowledgement timeout |
| MAX_TELEMETRY_BATCH | 1000 | Max events per export batch |
