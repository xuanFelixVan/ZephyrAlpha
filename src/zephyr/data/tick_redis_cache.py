# [BLUEPRINT] MOD-H1_REDIS_HOT | docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md | §3.3
# [MODULE] zephyr.data.tick_redis_cache
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.h1_redis_hot.h1_redis_schema
# [CONSUMERS] zephyr.data.tick_subscriber
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIPELINE 批量写入 tick:{symbol}:latest; best-effort(Redis故障不阻断WAL主路径); Key 通过 h1_redis_schema 构造
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] redis.RedisError->log+返回0(不raise,不阻断WAL); 空tick->skip
# [TESTS] tests/zephyr/data/test_tick_redis_cache.py
# [A_module] module_id=MOD-H1_REDIS_HOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



tick → Redis tick:{symbol}:latest 双写器（D-DATA → H1 集成适配器）。

真源：
    - H1 蓝图 §3.3 Tick 缓存（tick:{symbol}:latest Hash）
    - H1 蓝图 §9 集成点：D-DATA (miniQMT) → H1，盘中 tick
    - 数据架构.md §8.2 流式路径 + CP-01（Tick→Redis ≤3秒）

职责：
    tick_subscriber._drain_batch 批量出队时，将 QMT tick dict 转换为
    Redis tick:{symbol}:latest Hash 格式，PIPELINE 批量写入。

    与 WAL 路径的关系：双写（WAL→ClickHouse 是持久化主路径，
    Redis 是热读取加速层）。Redis 故障时 best-effort 降级——
    log+返回0，不阻断 WAL 主路径（CP-02 降级：信号端用上一批因子值）。

性能：
    - PIPELINE 模式：500 条 tick 单次 RTT 批量 HSET
    - 写入频率：每 drain_batch 一次（~500条/批，tick_subscriber 3秒周期）
    - 延迟：<10ms（CP-01 SLO）

用法::

    from zephyr.data.tick_redis_cache import TickRedisCache
    cache = TickRedisCache(redis_conn)
    cache.write_batch([("000001.SZ", tick_dict), ("600000.SH", tick_dict2)])

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: tick 参数
#   fields: 参数 tick，类型注解 dict
#   code: tick_redis_cache.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① tick_to_cache_dict
#   name_en: tick_to_cache_dict
#   intro: QMT tick dict → Redis tick:{symbol}:latest Hash fields。
#   desc: QMT tick dict → Redis tick:{symbol}:latest Hash fields。 输出字段（H1 蓝图 §3.3：price/volume/bid1…；源码 L119-L163
#   inputs: tick
#   outputs: dict[str, float | int] | None
# - id: A2
#   name_zh: ② TickRedisCache
#   name_en: TickRedisCache
#   intro: tick → Redis tick:{symbol}:latest PIPELINE 批量双写器。
#   desc: tick → Redis tick:{symbol}:latest PIPELINE 批量双写器。 蓝图 §3.3 Tick 缓存 + §9 D-DATA→H1 集成点实现。 设…；公共方法（定义序）: write_b…
#   inputs: redis_conn
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: dict[str, float | int] | None
#   name_en: dict[str, float | int] | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.tick_subscriber
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key

if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)

# Tick 缓存 Hash 字段数上限（5档 bid/ask + price/volume/amount/timestamp = 23 字段）
_MAX_LEVELS = 5


def _safe_float(val: object) -> float:
    """安全转换为 float，失败返回 0.0。"""
    if val is None:
        return 0.0
    try:
        f = float(val)
        return f if f == f else 0.0  # NaN check
    except (TypeError, ValueError):
        return 0.0


def _safe_int(val: object) -> int:
    """安全转换为 int，失败返回 0。"""
    if val is None:
        return 0
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def tick_to_cache_dict(tick: dict) -> dict[str, float | int] | None:
    """QMT tick dict → Redis tick:{symbol}:latest Hash fields。

    输出字段（H1 蓝图 §3.3：price/volume/bid1-5/ask1-5 + 扩展）：
        - timestamp: tick 时间戳（毫秒，int）
        - price: 最新价（float）
        - volume: 累计成交量（int）
        - amount: 累计成交额（float）
        - bid1~bid5: 五档买价（float）
        - ask1~ask5: 五档卖价（float）
        - bid_vol1~bid_vol5: 五档买量（int）
        - ask_vol1~ask_vol5: 五档卖量（int）

    Args:
        tick: xtdata 回调的 tick dict（含 time/lastPrice/volume/bidPrice/askPrice/bidVol/askVol）

    Returns:
        {field: value} mapping，或 None（空 tick / 无 time 字段）
    """
    if not tick or not tick.get("time"):
        return None

    result: dict[str, float | int] = {
        "timestamp": _safe_int(tick.get("time")),
        "price": _safe_float(tick.get("lastPrice")),
        "volume": _safe_int(tick.get("volume")),
        "amount": _safe_float(tick.get("amount")),
    }

    bid_prices = tick.get("bidPrice") or []
    ask_prices = tick.get("askPrice") or []
    bid_vols = tick.get("bidVol") or []
    ask_vols = tick.get("askVol") or []

    for i in range(_MAX_LEVELS):
        if i < len(bid_prices):
            result[f"bid{i + 1}"] = _safe_float(bid_prices[i])
        if i < len(ask_prices):
            result[f"ask{i + 1}"] = _safe_float(ask_prices[i])
        if i < len(bid_vols):
            result[f"bid_vol{i + 1}"] = _safe_int(bid_vols[i])
        if i < len(ask_vols):
            result[f"ask_vol{i + 1}"] = _safe_int(ask_vols[i])

    return result


class TickRedisCache:
    """tick → Redis tick:{symbol}:latest PIPELINE 批量双写器。

    蓝图 §3.3 Tick 缓存 + §9 D-DATA→H1 集成点实现。

    设计原则：
        - best-effort：Redis 故障时 log+返回0，不 raise（WAL 是主路径）
        - PIPELINE 批量：500 条 tick 单次 RTT，非逐条 HSET
        - Key 通过 h1_redis_schema.tick_latest_key 构造（禁止手拼 f-string）
    """

    def __init__(self, redis_conn: redis.Redis):
        """初始化 tick 缓存写入器。

        Args:
            redis_conn: redis.Redis 连接实例（来自 DatabaseService.get_redis_conn()）。
                        要求 decode_responses=True。
        """
        self.conn = redis_conn

    def write_batch(self, ticks: list[tuple[str, dict]]) -> int:
        """PIPELINE 批量写入 tick 到 Redis tick:{symbol}:latest。

        Args:
            ticks: [(stock_code, tick_dict), ...]
                   stock_code: QMT 格式（如 "000001.SZ"），直接作为 Redis Key 的 symbol

        Returns:
            成功写入的 tick 数量（0=空批次或 Redis 故障）
        """
        if not ticks:
            return 0

        start = time.perf_counter()
        pipe = self.conn.pipeline(transaction=False)  # 非原子，性能优先
        queued = 0

        for stock_code, tick in ticks:
            cache_dict = tick_to_cache_dict(tick)
            if cache_dict is None:
                continue
            key = tick_latest_key(stock_code)
            # 值转 str（Redis Hash value 统一 str，与 H1RedisWriter 一致）
            mapping = {k: repr(v) for k, v in cache_dict.items()}
            pipe.hset(key, mapping=mapping)
            queued += 1

        if queued == 0:
            return 0

        try:
            pipe.execute()
        except Exception as exc:  # noqa: BLE001 — best-effort，不阻断 WAL
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.warning(
                "TickRedisCache 批量写入失败: %d ticks, %.1fms, error=%s",
                queued,
                elapsed_ms,
                exc,
            )
            return 0

        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > 100:
            logger.warning(
                "TickRedisCache 写入耗时 %.1fms 超过 100ms 阈值（%d ticks）",
                elapsed_ms,
                queued,
            )
        else:
            logger.debug(
                "TickRedisCache 写入 %d ticks, %.1fms",
                queued,
                elapsed_ms,
            )
        return queued
