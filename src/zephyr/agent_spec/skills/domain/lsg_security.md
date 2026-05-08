---
skill_id: SKILL-DOM-LSG-001
name: lsg-security
description: "LLM Security Gateway (LSG) — L0-L8 nine-layer defense-in-depth. Covers prompt injection detection, jailbreak defense, PII redaction, agent permission control, cost circuit breaker, observability, continuous validation, multi-agent trust."
allowed-tools: [Read, Grep, Glob, SearchCodebase]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: LSG Security

## CRITICAL Rules

1. Every LLM input MUST pass through L1 (input defense) before reaching model
2. Every LLM output MUST pass through L3 (output security) before reaching user
3. Agent actions MUST be permission-checked via L4 (agent security)
4. Cost circuit breaker (L5) MUST trip on budget threshold exceedance
5. PII MUST be redacted before any external transmission (L3)
6. All security decisions MUST be observable via L6 (observability)

## Core Operations

- L0: Supply chain security — model verification, dependency scanning, MCP validation
- L1: Input defense — prompt injection, jailbreak, encoding bypass detection
- L2: Prompt protection — leak detection, topic boundary control
- L2a: Process sandbox — isolated code execution environment
- L3: Output security — PII redaction, schema validation, hallucination detection
- L4: Agent security — tool permission control, financial compliance, HITL approval
- L5: Resource protection — token budget, rate limiting, cost circuit breaker
- L6: Observability — security event logging, anomaly detection, alerting
- L7: Continuous validation — code integrity, red team regression, provider isolation
- L8: Multi-agent security — cross-agent trust, identity verification, permission model

## Unique Constraints

- L0-L8 layers are sequentially applied — each layer can block or tag
- Blocked requests MUST be logged to security audit trail
- Circuit breaker auto-resets after cooldown period (configurable)
- Multi-agent trust requires signed identity tokens
- PII patterns are configurable via regex allow/deny lists

## Common Error Patterns

- False positive on benign input (prompt injection over-blocking)
- PII redaction misses context-dependent patterns
- Circuit breaker premature trip on burst traffic
- Multi-agent trust handshake timeout
- Security audit log overflow under high throughput

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| MAX_INPUT_TOKENS | 32768 | Max tokens per LLM input |
| CIRCUIT_BREAKER_COOLDOWN_S | 300 | Auto-reset cooldown seconds |
| PII_REDACTION_PLACEHOLDER | "[REDACTED]" | Replacement text |
| MAX_SECURITY_EVENTS_PER_SESSION | 1000 | Audit log cap |
