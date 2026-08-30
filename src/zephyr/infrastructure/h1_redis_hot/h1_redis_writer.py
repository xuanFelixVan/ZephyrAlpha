# [BLUEPRINT] MOD-H1_REDIS_HOT | docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md | §4.1
# [MODULE] zephyr.infrastructure.h1_redis_hot.h1_redis_writer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.h1_redis_hot.h1_redis_schema
# [CONSUMERS] zephyr.factor.engine; zephyr.data.ch_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIPELINE 批量写入; Key 通过 h1_redis_schema 构造; 因子值 float→str 序列化
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] redis.RedisError(连接异常)->记录失败批次+重试; H1WriteBatchFailed(批量写入失败)
# [TESTS] tests/zephyr/infrastructure/h1_redis_hot/test_h1_redis_writer.py
# [A_module] module_id=MOD-H1_REDIS_HOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# M03豁免: AI趋同演化,非复制粘贴（项目内部标注，非 ruff code）

"""
H1RedisWriter — D-FACTOR Engine 每 3 秒截面写入 Redis（PIPELINE 模式）。

真源：
    - 蓝图 §4.1（H1RedisWriter 接口定义）
    - 数据架构.md §11.1.2（在线存储 Online Store）
    - 数据架构.md §7.2（容量估算 ~50MB 因子截面）

职责：
    D-FACTOR Engine 每 3 秒计算一批因子截面（5000只×200因子≈1M字段），
    通过 redis-py PIPELINE 批量写入 Redis Hash（feature:{symbol}）。

性能：
    - PIPELINE 模式：单次 RTT 批量发送 5000 条 HSET，避免逐条往返
    - 因子值 float→str：Redis Hash value 为 str，业务侧 Reader 反序列化
    - 写入频率：每 3 秒/批（miniQMT Tick=3秒，蓝图 §5.1 约束 2）

用法：
    from zephyr.infrastructure.database_service import DatabaseService
    from zephyr.infrastructure.h1_redis_hot.h1_redis_writer import H1RedisWriter

    ds = DatabaseService()
    writer = H1RedisWriter(ds.get_redis_conn())
    writer.write_factor_cross_section({
        "000001.SZ": {"momentum_20d": 0.0234, "close": 12.50},
        "600000.SH": {"momentum_20d": -0.0156, "close": 8.32},
    })

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: redis_conn 参数
#   fields: 参数 redis_conn（无注解）
#   code: h1_redis_writer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① H1RedisWriter
#   name_en: H1RedisWriter
#   intro: D-FACTOR Engine 每 3 秒截面写入 Redis（PIPELINE 模式）。
#   desc: D-FACTOR Engine 每 3 秒截面写入 Redis（PIPELINE 模式）。 蓝图 §4.1 接口实现。；公共方法（定义序）: write_factor_cross_section, write_tick…
#   inputs: redis_conn
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: H1RedisWriter
#   downstream: zephyr.factor.engine; zephyr.data.ch_writer
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import (
    MAXMEMORY_EXPANSION_TRIGGER_RATIO,
    factor_field,
    feature_key,
    feature_updated_at_field,
)

if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)

# 默认因子版本（窄表理念 DD-P3-01：Field 含因子名+版本）
_DEFAULT_FACTOR_VERSION = "v1"


class H1WriteBatchFailed(RuntimeError):
    """批量写入失败（蓝图 §6.1 异常场景 3）。"""


class H1RedisWriter:
    """D-FACTOR Engine 每 3 秒截面写入 Redis（PIPELINE 模式）。

    蓝图 §4.1 接口实现。
    """

    def __init__(self, redis_conn: redis.Redis):
        """初始化 Writer。

        Args:
            redis_conn: redis.Redis 连接实例（来自 DatabaseService.get_redis_conn()）。
                        要求 decode_responses=True（业务代码直接拿 str）。
        """
        self.conn = redis_conn

    def write_factor_cross_section(
        self,
        cross_section: dict[str, dict[str, float]],
        factor_version: str = _DEFAULT_FACTOR_VERSION,
    ) -> int:
        """批量写入因子截面（PIPELINE 模式）。

        蓝图 §4.1 / §5.1 约束 3：5000只×200因子≈1M字段/3秒，PIPELINE 单次 RTT。

        Args:
            cross_section: {symbol: {factor_name: factor_value}}。
                           例：{"000001.SZ": {"momentum_20d": 0.0234, "close": 12.50}}
            factor_version: 因子版本号（窄表 DD-P3-01，默认 v1）。
                            版本升级时新版本 Field 并存，不改 Key 结构。

        Returns:
            写入的 symbol 数量。

        Raises:
            H1WriteBatchFailed: PIPELINE 批量执行失败（记录失败批次，调用方可重试）。
        """
        if not cross_section:
            return 0

        start = time.perf_counter()
        pipe = self.conn.pipeline(transaction=False)  # 非原子，性能优先
        written = 0

        # CP-02 过期检测（治本，2026-08-03 实地演练发现）：
        # 整批截面共享同一写入时戳——同一 3 秒周期内所有 symbol 的 updated_at 一致，
        # 消费者读 time.time() - updated_at 判定新鲜度（>阈值标 expired → 降级）。
        # 用 epoch 秒（repr(float)）便于消费者直接 float() 做差值，无 ISO 解析开销。
        updated_at = repr(time.time())
        updated_at_field = feature_updated_at_field()

        for symbol, factors in cross_section.items():
            if not factors:
                continue
            key = feature_key(symbol)
            # 构造 {factor_name:ver: str(value), _updated_at: epoch} mapping
            # _updated_at 与因子 Field（name:ver）前缀区分，不会冲突
            mapping = {factor_field(name, factor_version): repr(val) for name, val in factors.items()}
            mapping[updated_at_field] = updated_at
            pipe.hset(key, mapping=mapping)
            written += 1

        try:
            pipe.execute()
        except Exception as exc:
            elapsed = time.perf_counter() - start
            logger.error(
                "H1RedisWriter 批量写入失败: %d symbols, %.3fs, error=%s",
                written,
                elapsed,
                exc,
            )
            raise H1WriteBatchFailed(f"因子截面批量写入失败（{written} symbols, {elapsed:.3f}s）: {exc}") from exc

        elapsed_ms = (time.perf_counter() - start) * 1000
        # 蓝图 §6.2 可观测性：h1_write_cross_section_seconds
        if elapsed_ms > 3000:
            logger.warning(
                "H1RedisWriter 写入耗时 %.1fms 超过 3s 阈值（%d symbols）",
                elapsed_ms,
                written,
            )
        else:
            logger.debug(
                "H1RedisWriter 写入 %d symbols, %.1fms",
                written,
                elapsed_ms,
            )

        # 容量监控（蓝图 §6.2：h1_maxmemory_usage_ratio > 70% 告警）
        self._check_memory_pressure()

        return written

    def write_tick_latest(self, symbol: str, tick_data: dict[str, float | int | str]) -> None:
        """写入盘中最新 tick（tick:{symbol}:latest）。

        蓝图 §3.3 Tick 缓存 Key。D-DATA (miniQMT) 盘中 tick 缓存，
        决策引擎快速取最新价。

        Args:
            symbol: 标的代码（如 "000001.SZ"）。
            tick_data: {price: 12.50, volume: 100000, bid1: 12.49, ask1: 12.51, ...}
        """
        from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key

        key = tick_latest_key(symbol)
        # 值转 str（Redis Hash value 统一 str）
        mapping = {k: repr(v) for k, v in tick_data.items()}
        self.conn.hset(key, mapping=mapping)

    def _check_memory_pressure(self) -> None:
        """检查 maxmemory 使用率（蓝图 §6.2：> 70% 告警 P2）。"""
        try:
            info = self.conn.info("memory")
            used = info.get("used_memory", 0)
            maxmem = info.get("maxmemory", 0)
            if maxmem > 0:
                ratio = used / maxmem
                if ratio > MAXMEMORY_EXPANSION_TRIGGER_RATIO:
                    logger.warning(
                        "Redis maxmemory 使用率 %.1f%% > %.0f%% 阈值 （used=%s, max=%s）—— 触发扩展评估",
                        ratio * 100,
                        MAXMEMORY_EXPANSION_TRIGGER_RATIO * 100,
                        info.get("used_memory_human", "?"),
                        f"{maxmem // 1024 // 1024}MB",
                    )
        except Exception:  # noqa: BLE001 — 监控不阻断写入
            logger.debug("maxmemory 检查跳过（info 不可用）", exc_info=True)
