---
module_id: KE-module_blu-5_circular_dependency_ruling-000
title: §5 Circular Dependency Ruling
category: module_blueprint
---

# §5 Circular Dependency Ruling

§5 Circular Dependency Ruling

- **Ruling:** RBAC → Audit (单向调用，Audit 不 import RBAC)
- **Enforcement:** check_audit_rbac_isolation.py static analysis
- **Status:** COMPLIANT ✅
