# L3 Reference: Governance Scan Guide

> Belongs to: governor (SKILL-ROL-GOV-001)
> Core tool: governance scan workflow

## Scan Command Sequence

```bash
# 1. Environment health check
python scripts/governance/env_check.py

# 2. Full governance scan
python scripts/governance/run_all.py

# 3. Architecture guard scan
python scripts/arch_guard/run_all.py

# 4. Blueprint drift detection
python -m zephyr.drift_detector scan --all

# 5. Gate engine validation (G0-G9)
python -m zephyr.gates validate --all
```

## Scan Result Categories

| Category | Script | What It Checks |
|----------|--------|---------------|
| IMPORT | `import_scanner.py` | All imports resolve, no circular deps |
| STRUCT | `module_structure.py` | `__init__.py` exports match `__all__` |
| BLUEPRINT | `blueprint_drift.py` | Code aligns with blueprint declarations |
| SECURITY | `lsg_scan.py` | No hardcoded secrets, no eval/exec |
| COMPLEXITY | `cyclomatic.py` | Function complexity < 15 |
| COVERAGE | `coverage_gap.py` | Test coverage meets module thresholds |

## Finding Severity Classification

| Level | Criteria | Action |
|-------|---------|--------|
| ERROR | Gate violation, dead import, missing file | BLOCK merge |
| WARN | Freshness < 30, complexity > 10 | Fix before next phase |
| INFO | Style deviation, minor doc gap | Log, fix opportunistically |
