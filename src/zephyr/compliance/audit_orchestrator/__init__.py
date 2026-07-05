# [A_module] module_id=MOD-CMP_audit_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: audit-orchestrator has migrated to zephyr.governance.audit_trail"""

from zephyr.governance.audit_trail import *  # noqa: F403
