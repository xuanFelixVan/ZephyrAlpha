# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.core.base_event
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.core.base_event
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.core.base_event
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.core.base_event import BaseEvent, generate_idempotency_key, validate_idempotency_key"
# [A_module] module_id=MOD-INT_base_event | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.core.base_event。"""
from zephyr.shared.contracts.core.base_event import *  # noqa: F401,F403
