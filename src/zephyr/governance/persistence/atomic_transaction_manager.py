# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.persistence.atomic_transaction_manager
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.atomic_transaction_manager
# [CONSUMERS] tests.unit.test_atomic_transaction_manager_unit; tests.unit.db.test_atomic_transaction_manager_db
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# 代理模块：将 zephyr.governance.persistence.atomic_transaction_manager 重定向到 zephyr.governance.atomic_transaction_manager
from zephyr.governance.atomic_transaction_manager import (
    AtomicTransactionManager,
    TransactionError,
    _new_tx_id,
    _utf8_lf_bytes,
)

__all__ = ["AtomicTransactionManager", "TransactionError", "_new_tx_id", "_utf8_lf_bytes"]
