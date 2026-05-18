---

skill_id: SKILL-ROL-GOV-001
name: governor
description: "Audit scanning, drift fixing, compliance enforcement"
allowed-tools: [Read, Grep, Glob, RunCommand, mcp_Excel]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 300
author: factory-agent
blueprint_id: MOD-INF-019
---


# Role Skill: Governor

## CRITICAL Rules

1. Never modify business code
2. Run governance scans before each audit
3. Report drift findings to escalation module
4. Validate against blueprint SSoT

## Governance Scan Workflow

1. Run `python scripts/governance/run_all.py`
2. Run `python scripts/arch_guard/run_all.py`
3. Analyze findings
4. Generate audit report
5. Submit to drift-detector

## References (L3, on-demand)

- governance_scan_guide.md
- drift_fix_protocol.md
- compliance_checklist.md