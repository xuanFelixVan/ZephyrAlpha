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
# [A_module] module_id=MOD-MKT-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_MKT_DATA — Raw Data Cache (原始数据缓存)

行情数据标准化前的原始数据缓存层。从数据源拉取的原始行情在标准化为
NormalizedMarketData 之前先写入缓存, 支持重放/回放/故障恢复/审计核对。

采用 LRU + TTL 双重淘汰策略, 线程安全, 含内容哈希校验。

属 A 类基础设施(内存缓存), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-006
蓝图: docs/03_modules/_domain_mkt_data/raw_data_cache/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 原始行情字节数据
#   fields: symbol/date/raw_payload(bytes)/source_vendor/可选 ttl_seconds 覆盖
#   code: cache.py put() L194
# - id: I2
#   name: CacheConfig 缓存配置
#   fields: max_size/ttl_seconds/policy(LRU/TTL/LRU_TTL)
#   code: cache.py CacheConfig L106
# 层: 算法
# - id: A1
#   name_zh: ① 写入与内容哈希
#   name_en: RawDataCache.put
#   intro: 原始数据写缓存并算 SHA-256 哈希供审计核对
#   desc: 非空校验（symbol/date/source_vendor，payload 须 bytes）否则 raise CacheError(ZA-MKT-0006)；content_hash=SHA-256 前16字符；同 key 覆盖并调整总字节数
#   inputs: I1
#   outputs: CacheEntry
#   invariant: content_hash 写入时计算
# - id: A2
#   name_zh: ② LRU+TTL 双重淘汰
#   name_en: _evict_lru_locked/is_expired
#   intro: 容量超限踢最久未访问、时间过期惰性清除
#   desc: OrderedDict 末尾=最近访问；容量超 max_size 从首部 popitem 淘汰；expires_at=fetched_at+ttl；TTL 策略仅时间淘汰
#   inputs: A1 I2
#   outputs: 淘汰计数 eviction_count
#   invariant: 条目数≤max_size（LRU 类策略）
# - id: A3
#   name_zh: ③ 读取与范围查询
#   name_en: get/query/exists
#   intro: 命中更新 LRU 顺序，范围查询按日期升序返回
#   desc: get 命中 move_to_end 并 hit_count+1、过期惰性移除记 miss；query 扫描 [start_date,end_date] 区间跳过期、按日期升序、不更新 LRU
#   inputs: A1
#   outputs: CacheEntry 或条目列表
# 层: 输出
# - id: O1
#   name_zh: 缓存条目与统计快照
#   name_en: CacheEntry/CacheStats
#   intro: 标准化前原始行情的可重放缓存及命中率等统计
#   invariant: CacheStats frozen；hit_rate=hit/(hit+miss)
#   downstream: normalized_market_data_producer（#[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# A1 --> A3
# A2 --> O1
# A3 --> O1
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
