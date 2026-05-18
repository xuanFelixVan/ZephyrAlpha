---
blueprint_id: MOD-INF-019
---

# L3 Reference: Compliance Checklist

> Belongs to: governor (SKILL-ROL-GOV-001)
> Standards: EU AI Act, MiFID II, SEC Rule 613, GDPR

## Pre-Construction Compliance Gates

- [ ] G-CT-001: Agent RBAC permissions defined for this module
- [ ] G-CT-002: Audit trail consumer registered (MOD-INF-020)
- [ ] G-CT-003: Budget Enforcer limits set (MOD-INF-024)
- [ ] G-CT-004: Skill KYA protocol acknowledged (MOD-INF-019 skill_kya)

## Data Handling (GDPR / MiFID II)

- [ ] No PII in Skill frontmatter or L2 body
- [ ] No hardcoded API keys, tokens, or passwords
- [ ] No raw financial data in Skill descriptions
- [ ] Data zone classification declared (CN / US / EU / GLOBAL)
- [ ] Geo-Fence compliance: Skill only accesses data in its declared zone

## AI Safety (EU AI Act Alignment)

- [ ] Skill has defined failure modes (see postmortem template)
- [ ] Skill has kill switch registered (skill_kill_switch.py)
- [ ] Skill has freshness decay model active (720h to zero)
- [ ] Skill has sandbox preview capability (skill_sandbox.py)
- [ ] Skill output is LSG-sanitized before persistence

## SEC Rule 613 (Consolidated Audit Trail)

- [ ] All Skill actions produce audit events
- [ ] Audit events include: timestamp, agent_id, session_id, event_type
- [ ] Audit chain is tamper-evident (HMAC-SHA256)
- [ ] Audit retention period: 7 years minimum for financial modules

## Post-Execution Verification

- [ ] Run `python scripts/governance/compliance_check.py`
- [ ] Verify no G6 violations in audit report
- [ ] Verify skill_freshness > 30.0 for all active skills
- [ ] Verify no drift between skill_registry.yaml and filesystem
- [ ] Submit compliance report to `docs/09_audit/reports/`

## Quarterly Review Items

- [ ] Deprecation review: any skills > 180 days since last validated?
- [ ] Model compatibility: all skills tested against current model roster?
- [ ] Cost audit: token consumption vs budget projections?
- [ ] Access review: RBAC permissions still appropriate?
