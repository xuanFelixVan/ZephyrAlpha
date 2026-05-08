# L3 Reference: Session Resume Protocol

> Belongs to: architect (SKILL-ROL-ARC-001)
> Implementation: Skill Durable Execution (skill_durable.py)

## Session Resume Chain

```
1. Read session-logs/ directory → find latest session YAML
2. Read _journals/checkpoint_*.json → find interrupt layer
3. Load corresponding blueprint(s) and TaskCards
4. Rebuild SessionContinuity context via zephyr.core.session_continuity
5. Restore Skill execution state from skill_durable snapshot
```

## Checkpoint Format (`_journals/checkpoint_*.json`)

```json
{
  "session_id": "2026-05-08-T3",
  "interrupt_layer": "blueprint",
  "last_phase": "validate",
  "task_cards_inflight": ["TC-042", "TC-043"],
  "skill_states": {
    "SKILL-DOM-DBS-001": {"phase": "construction", "line": 342},
    "SKILL-ROL-IMP-001": {"phase": "implement", "file": "shared/db/migrations.py"}
  },
  "timestamp": "2026-05-08T18:00:00Z"
}
```

## Recovery Priority

1. Restore in-flight TaskCards (TaskRepo PENDING→IN_PROGRESS)
2. Re-load Domain + Role Skills via PipelineSkillBridge
3. Apply Progressive Disclosure: skip L1 frontmatter (already known), load L2 body
4. Continue from interrupt point — do NOT restart from scratch

## Token Budget for Resume Context

- Session metadata: 200 tokens
- Checkpoint state: 150 tokens
- Skill re-load (L2 bodies): 800 tokens max
- Total resume overhead: 1150 tokens
