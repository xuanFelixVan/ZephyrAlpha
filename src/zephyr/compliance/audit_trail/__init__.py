# [A_module] module_id=MOD-CMP-audit_trail | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


Re-export wrapper: audit-trail has migrated to zephyr.gov_audit

# [ALGO_FLOW] external: docs/03_modules/_domain_compliance/algo_flow/audit_trail__init__.yaml
"""

# 5.93.6 修复：import * → 显式导入
from zephyr.gov_audit import bridges

__all__ = ["bridges"]
