---
module_id: KE-2326
status: active
title: §5 Circular Dependency Ruling
category: module_blueprint
---

# §5 Circular Dependency Ruling

§5 Circular Dependency Ruling

- **Ruling:** RBAC → Audit (单向调用，Audit 不 import RBAC)
- **Enforcement:** check_audit_rbac_isolation.py static analysis
- **Status:** COMPLIANT ✅
