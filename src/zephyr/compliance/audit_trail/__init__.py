# [A_module] module_id=MOD-CMP_audit_trail | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: audit-trail has migrated to zephyr.governance.audit_trail"""

# 5.93.6 修复：import * → 显式导入
from zephyr.governance.audit_trail import bridges

__all__ = ["bridges"]
