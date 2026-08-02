# [BLUEPRINT] MOD-MKT-004 | docs/03_modules/_domain_mkt_data/failover/blueprint.md
# [MODULE] zephyr.market_data.failover
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_registry; zephyr.market_data.vendor_base; zephyr.shared.foundation.errors
# [CONSUMERS] D_EX_SOR
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] FailoverEvent/FailoverConfig frozen; FailoverPolicy/FailoverReason Enum; _active_vendor_id/_history加Lock; 切换原子(先确认目标可用); 同vendor不切自身
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FailoverError(ZA-MKT-0004)
# [TESTS] tests/market_data/failover/test_failover_manager.py
# [TTL] permanent
"""D_MKT_DATA — Failover (故障切换)

多数据源主备切换管理。主数据源健康检查失败时自动切换到备用数据源,
主源恢复后可选自动切回。基于 VendorRegistry 的多 vendor 注册。

属 A 类基础设施(高可用机制), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-004
蓝图: docs/03_modules/_domain_mkt_data/failover/blueprint.md
"""

from zephyr.market_data.failover.manager import (
    FailoverConfig,
    FailoverError,
    FailoverEvent,
    FailoverManager,
    FailoverPolicy,
    FailoverReason,
)

__all__ = [
    "FailoverConfig",
    "FailoverError",
    "FailoverEvent",
    "FailoverManager",
    "FailoverPolicy",
    "FailoverReason",
]
