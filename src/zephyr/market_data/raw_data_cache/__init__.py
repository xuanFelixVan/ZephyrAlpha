# [BLUEPRINT] MOD-MKT-006 | docs/03_modules/_domain_mkt_data/raw_data_cache/blueprint.md
# [MODULE] zephyr.market_data.raw_data_cache
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.market_data.normalized_market_data_producer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CacheEntry/CacheConfig/CacheKey/CacheStats frozen不可变; 读写加threading.Lock; LRU+TTL双重淘汰; content_hash写入时计算
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CacheError(ZA-MKT-0006)
# [TESTS] tests/market_data/raw_data_cache/test_raw_data_cache.py
# [TTL] permanent
"""D_MKT_DATA — Raw Data Cache (原始数据缓存)

行情数据标准化前的原始数据缓存层。从数据源拉取的原始行情在标准化为
NormalizedMarketData 之前先写入缓存, 支持重放/回放/故障恢复/审计核对。

采用 LRU + TTL 双重淘汰策略, 线程安全, 含内容哈希校验。

属 A 类基础设施(内存缓存), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-006
蓝图: docs/03_modules/_domain_mkt_data/raw_data_cache/blueprint.md
"""

from zephyr.market_data.raw_data_cache.cache import (
    CacheConfig,
    CacheEntry,
    CacheError,
    CacheKey,
    CacheStats,
    EvictionPolicy,
    RawDataCache,
)

__all__ = [
    "CacheConfig",
    "CacheEntry",
    "CacheError",
    "CacheKey",
    "CacheStats",
    "EvictionPolicy",
    "RawDataCache",
]
