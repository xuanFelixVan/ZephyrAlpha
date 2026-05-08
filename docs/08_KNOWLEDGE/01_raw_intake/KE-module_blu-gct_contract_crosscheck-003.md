---
module_id: KE-module_blu-gct_contract_crosscheck-003
title: GCT Contract Crosscheck
category: module_blueprint
---

# GCT Contract Crosscheck

GCT Contract Crosscheck

| GCT | Source Module | Target Module | Source File | Target File | Bridge OK |
|-----|--------------|---------------|-------------|-------------|-----------|
| G-CT-001 | agent_rbac | audit_trail | contracts.py | contracts.py | ✅ |
| G-CT-002 | audit_trail | rollback | anomaly.py | contracts.py | ✅ |
| G-CT-003 | rollback | escalation | result_types.py | contracts.py | ✅ |
| G-CT-004 | escalation | agent_rbac | approval.py | approver_check.py | ✅ |
| G-CT-005 | drift_detector | rollback | events.py | drift_fix.py | ✅ |
| G-CT-006 | budget_enforcer | escalation | alerts.py | budget_handler.py | ✅ |
| G-CT-007 | agent_spec | audit_trail | registry.py | spec_auditor.py | ✅ |
| G-CT-008 | a2a | agent_rbac | protocol.py | a2a_check.py | ✅ |
