# L3 Reference: Escalation Path Protocol

> Belongs to: architect (SKILL-ROL-ARC-001), governor (SKILL-ROL-GOV-001)
> Dependencies: MOD-INF-022 Escalation Protocol

## Escalation Levels

| Level | Trigger | Action | Owner Response SLA |
|-------|---------|--------|--------------------|
| LIGHT | Minor ambiguity, code style choices | Proceed, log decision | N/A |
| MODERATE | Migration strategy choice, dependency conflict | Pause, await Owner reply | 4h (business hours) |
| CRITICAL | Architecture change, security concern, ABI break | Generate ADR draft, pause, await Owner signature | 2h (any time) |

## Escalation Triggers (from Hyperleap Feb 2026)

1. sentiment: negative response pattern detected
2. low-confidence: confidence < 0.6 on any gate
3. out-of-bounds: output exceeds blueprint-defined boundaries
4. loops: repeated self-correction cycle > 3
5. explicit-request: AI determines human judgment required

## ZephyrAlpha-Specific Triggers

- "factor valid but confidence interval too wide" → MODERATE
- "regulatory interpretation needed (MiFID II / SEC 613)" → CRITICAL
- "data source schema change" → MODERATE
- "cost projection exceeds monthly budget" → CRITICAL

## Escalation Path

```
AI detects trigger → classify level → [LIGHT: proceed+log]
                                    → [MODERATE: suspend→log→notify]
                                    → [CRITICAL: create ADR→suspend→notify urgent]
```

## Notification Channels

1. Session Log marker: `ESCALATION_NEEDED:{level}:{reason}`
2. Feishu notification (if enabled): `python -m zephyr.notify escalations`
3. Audit Trail entry: event_type=`escalation_triggered`
