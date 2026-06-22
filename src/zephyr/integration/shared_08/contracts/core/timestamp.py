# [A_module] module_id=MOD-INT_timestamp | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-166 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.core.timestamp
# [INVARIANTS] Timestamp真源在zephyr.integration.shared_08.timestamp_utils;本文件仅作向后兼容re-export
# [MODIFY-GUARD] zephyr.integration.shared_08.timestamp_utils
# [CONSUMERS] zephyr.integration.shared_08.contracts;zephyr.integration.shared_08._contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError on missing timestamp_utils module
# [TESTS]

from zephyr.integration.shared_08.timestamp_utils import (
    NaiveDatetimeError,
    Timestamp,
    ensure_utc,
    from_unix_ns,
    to_local,
    utcnow,
)

__all__ = ["NaiveDatetimeError", "Timestamp", "ensure_utc", "from_unix_ns", "to_local", "utcnow"]
