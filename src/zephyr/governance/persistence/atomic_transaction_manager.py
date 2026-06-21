# 代理模块：将 zephyr.governance.persistence.atomic_transaction_manager 重定向到 zephyr.governance.atomic_transaction_manager
from zephyr.governance.atomic_transaction_manager import (
    AtomicTransactionManager,
    TransactionError,
    _new_tx_id,
)

__all__ = ["AtomicTransactionManager", "TransactionError", "_new_tx_id"]
