---
module_id: KE-4359
title: GCT Contract Crosscheck
category: module_blueprint
ttl: permanent
---

# GCT Contract Crosscheck

GCT Contract Crosscheck

| GCT | Source Module | Target Module | Source File | Target File | Bridge OK |
|-----|--------------|---------------|-------------|-------------|-----------|
| G-CT-001 | agent-rbac | audit-trail | contracts.py | contracts.py | ✅ |
| G-CT-002 | audit-trail | rollback | anomaly.py | contracts.py | ✅ |
| G-CT-003 | rollback | escalation | result_types.py | contracts.py | ✅ |
| G-CT-004 | escalation | agent-rbac | approval.py | approver_check.py | ✅ |
| G-CT-005 | drift-detector | rollback | events.py | drift_fix.py | ✅ |
| G-CT-006 | budget-enforcer | escalation | alerts.py | budget_handler.py | ✅ |
| G-CT-007 | agent-spec | audit-trail | registry.py | spec_auditor.py | ✅ |
| G-CT-008 | a2a | agent-rbac | protocol.py | a2a_check.py | ✅ |
