# Rollback Protocol (L3 Cold Memory)

## Overview
Rollback protocol defines the step-by-step procedure for safely reverting system changes across file systems, databases, and configuration layers.

## Trigger Conditions
- Test failure rate exceeds 20% after deployment
- Critical service degradation detected by telemetry
- Governance gate (G5+) blocks progression
- Drift detection flags > 5 files in divergence

## Rollback Levels

### L1: Atomic File Revert
- Scope: Single file
- Mechanism: Git checkout HEAD~1 <file>
- Validation: Lint + typecheck on reverted file
- Duration target: < 5 seconds

### L2: Partial Module Revert
- Scope: All files in a module directory
- Mechanism: Git reset --soft HEAD~1 + selective checkout
- Validation: Module-level test suite pass
- Duration target: < 30 seconds

### L3: Full System Revert
- Scope: Entire repository
- Mechanism: Git reset --hard to last known-good commit
- Validation: Full CI pipeline pass
- Duration target: < 5 minutes

### L4: Data Layer Rollback
- Scope: SQLite + ChromaDB
- Mechanism: WAL checkpoint restore from pre-change snapshot
- Validation: Data integrity checksum verification
- Duration target: < 60 seconds

## Safety Gates
1. Pre-rollback verification: Ensure rollback target exists
2. Dry-run simulation: Shadow workspace test before actual rollback
3. Incremental commit: Each rollback step is independently reversible
4. Audit trail: Every rollback logged with timestamp, trigger, and result
5. Automatic forward-fix attempt before rollback (if safe)

## Post-Rollback
1. System health check (all integration points)
2. Root cause analysis automatic trigger
3. Skill freshness score adjustment
4. Notification to governance channel