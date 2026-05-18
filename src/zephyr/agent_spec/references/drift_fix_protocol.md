---
blueprint_id: MOD-INF-019
---

# L3 Reference: Drift Fix Protocol

> Belongs to: governor (SKILL-ROL-GOV-001)
> Dependencies: MOD-INF-023 Drift Detector

## Drift Detection Triggers

1. Blueprint version updated → code must re-align
2. New module added → must have Domain Skill + blueprint registration
3. Repository structure change → AGENTS.md topology must update
4. Skill registry entry has no corresponding .md file
5. .md file exists but not in skill_registry.yaml

## Auto-Fix Categories

| Drift Type | Auto-Fix? | Fix Method |
|-----------|-----------|-----------|
| blueprint_registry drift | YES | Run `python -m zephyr.drift_detector sync` |
| skill_registry file missing | YES | Mark ORPHANED in registry, notify |
| AGENTS.md topology stale | SEMI | Generate diff PR, await Owner review |
| Code ≠ blueprint contract | NO | Create Finding → escalate to implementer |
| Security policy bypass | NO | CRITICAL escalation immediately |

## Fix Protocol Steps

```yaml
step_1_detect:
  tool: "drift_detector.scan()"
  output: "DriftReport {type, severity, source, target}"

step_2_classify:
  auto_fixable: [registry_drift, file_missing, stale_reference]
  semi_auto: [topology_update, freshness_boost]
  manual_required: [contract_violation, security_bypass]

step_3_apply:
  auto: "drift_detector.auto_fix() → verify via blueprint_diff"
  semi: "generate diff → create PR → await Owner review"
  manual: "create Escalation → log Finding → notify Owner"

step_4_verify:
  tool: "blueprint_diff" (skill vs code state comparison)
  gate: "G6 (drift check)"
```

## Rollback Safety

Every auto-fix creates a checkpoint before applying:
```python
from zephyr.agent_spec.rollback_specialist import RollbackCheckpoint
checkpoint = RollbackCheckpoint.create("drift_fix_{timestamp}")
```
If verification fails → `checkpoint.rollback()`
