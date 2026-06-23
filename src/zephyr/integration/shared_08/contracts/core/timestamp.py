# [A_module] module_id=MOD-INT_timestamp | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.core.timestamp
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.core.timestamp
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.core.timestamp
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.core.timestamp import Timestamp, NaiveDatetimeError, ensure_utc, from_unix_ns, to_local, utcnow"
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.core.timestamp。"""
from zephyr.shared.contracts.core.timestamp import *  # noqa: F401,F403
