# [A_module] module_id=MOD-SEM_semantic_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""Re-export wrapper: semantic-auditor has migrated to zephyr.governance.semantic_auditor"""

from zephyr.governance.semantic_auditor import *  # noqa: F403

__all__ = ["*"]
