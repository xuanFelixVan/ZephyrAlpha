# [BLUEPRINT] MOD-H1_REDIS_HOT | docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md | §4.2
# [MODULE] zephyr.infrastructure.h1_redis_hot.h1_redis_reader
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.h1_redis_hot.h1_redis_schema
# [CONSUMERS] zephyr.signal; zephyr.risk; zephyr.position; zephyr.decision_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 读取延迟<5ms; Key 通过 h1_redis_schema 构造; 失败抛 H1RedisUnavailable(降级信号)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] H1RedisUnavailable(Redis 不可用->调用方降级为上一批次+标记过期 CP-02); redis.RedisError(连接异常)
# [TESTS] tests/zephyr/infrastructure/h1_redis_hot/test_h1_redis_reader.py
# [A_module] module_id=MOD-H1_REDIS_HOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# M03豁免: AI趋同演化,非复制粘贴（项目内部标注，非 ruff code）

"""
H1RedisReader — 决策引擎 <5ms 在线特征查询。

真源：
    - 蓝图 §4.2（H1RedisReader 接口定义）
    - 数据架构.md §11.1.2（在线存储 Online Store）
    - 蓝图 §6.3 退化矩阵：Redis 不可用时降级为上一批次因子值 + 标记 expired（CP-02）

职责：
    为 D-SIGNAL / D-RISK / D-POSITION / 决策引擎提供 <5ms 的在线特征查询。
    读取 Redis Hash（feature/position/risk Key），反序列化为 Python dict。

降级策略（蓝图 §6.3）：
    Redis 不可用时抛 H1RedisUnavailable，调用方捕获后：
    1. 使用进程内 L1 缓存的上一批次因子值
    2. 标记数据 expired（CP-02 因子值→信号≤5秒容忍过期）
    3. 限制下单（降级期不开新仓）

用法：
    from zephyr.infrastructure.database_service import DatabaseService
    from zephyr.infrastructure.h1_redis_hot.h1_redis_reader import H1RedisReader, H1RedisUnavailable

    ds = DatabaseService()
    reader = H1RedisReader(ds.get_redis_conn())
    try:
        features = reader.get_online_features("000001.SZ", ["momentum_20d", "close"])
    except H1RedisUnavailable:
        # 降级：使用上一批次因子值 + 标记 expired
        ...

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: redis_conn 参数
#   fields: 参数 redis_conn（无注解）
#   code: h1_redis_reader.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① H1RedisReader
#   name_en: H1RedisReader
#   intro: 决策引擎 <5ms 在线特征查询。
#   desc: 决策引擎 <5ms 在线特征查询。 蓝图 §4.2 接口实现。；公共方法（定义序）: get_online_features, get_feature_updated_at, get_position, get_ris…
#   inputs: redis_conn
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: H1RedisReader
#   downstream: zephyr.signal; zephyr.risk; zephyr.position; zephyr.decision_engine
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)

# 延迟告警阈值（蓝图 §6.2：h1_read_latency_seconds P95>5ms → P1 告警）
_READ_LATENCY_WARN_MS = 5.0


class H1RedisUnavailable(RuntimeError):
    """Redis 不可用——调用方降级为上一批次因子值 + 标记 expired（CP-02）。

    蓝图 §6.1 异常场景 1 / §6.3 退化矩阵。
    """


def _parse_float(value: str | None) -> float | None:
    """将 Redis Hash value（str）反序列化为 float。

    Writer 用 repr(val) 写入，这里用 float() 反序列化。
    None 或空值返回 None（因子缺失）。
    """
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning("因子值反序列化失败: %r", value)
        return None


class H1RedisReader:
    """决策引擎 <5ms 在线特征查询。

    蓝图 §4.2 接口实现。
    """

    def __init__(self, redis_conn: redis.Redis):
        """初始化 Reader。

        Args:
            redis_conn: redis.Redis 连接实例（来自 DatabaseService.get_redis_conn()）。
                        要求 decode_responses=True。
        """
        self.conn = redis_conn

    def get_online_features(
        self,
        symbol: str,
        feature_names: list[str],
        factor_version: str = "v1",
    ) -> dict[str, float]:
        """读取单标的因子截面，<5ms（蓝图 §4.2 / DD-11-01）。

        使用 HMGET 批量读取指定因子字段，避免 HGETALL 拉全量。

        Args:
            symbol: 标的代码（如 "000001.SZ"）。
            feature_names: 需要的因子名列表（如 ["momentum_20d", "close"]）。
            factor_version: 因子版本号（默认 v1，与 Writer 对齐）。

        Returns:
            {factor_name: factor_value}，缺失因子不包含在结果中。

        Raises:
            H1RedisUnavailable: Redis 连接失败或超时——调用方降级（CP-02）。
        """
        from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import factor_field, feature_key

        start = time.perf_counter()
        try:
            key = feature_key(symbol)
            fields = [factor_field(name, factor_version) for name in feature_names]
            values = self.conn.hmget(key, fields)
        except Exception as exc:
            logger.error("H1RedisReader get_online_features 失败: symbol=%s, error=%s", symbol, exc)
            raise H1RedisUnavailable(f"Redis 因子截面读取失败（symbol={symbol}）: {exc}") from exc

        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > _READ_LATENCY_WARN_MS:
            logger.warning(
                "H1RedisReader 读取延迟 %.2fms > %.0fms 阈值（symbol=%s, %d factors）",
                elapsed_ms,
                _READ_LATENCY_WARN_MS,
                symbol,
                len(feature_names),
            )

        result: dict[str, float] = {}
        for name, raw in zip(feature_names, values, strict=True):
            val = _parse_float(raw)
            if val is not None:
                result[name] = val

        return result

    def get_feature_updated_at(self, symbol: str) -> float | None:
        """读取标的因子截面的 updated_at 时间戳（CP-02 时效判定）。

        读取 feature:{symbol} Hash 的 _updated_at Field（由 H1RedisWriter 写入）。
        消费者用 time.time() - updated_at 判定数据新鲜度，超阈值则标记 expired
        触发 CP-02 降级（上一批次兜底 + 限制开仓）。

        典型用法::

            updated_at = reader.get_feature_updated_at("000001.SZ")
            if updated_at is not None and (time.time() - updated_at) > 10.0:
                # 数据已过期（>10s 未刷新），标记 expired 触发降级
                ...

        Args:
            symbol: 标的代码（如 "000001.SZ"）。

        Returns:
            updated_at epoch 秒（float）；无数据/未写入返回 None。

        Raises:
            H1RedisUnavailable: Redis 连接失败或超时——调用方降级（CP-02）。
        """
        from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import (
            feature_key,
            feature_updated_at_field,
        )

        try:
            key = feature_key(symbol)
            raw = self.conn.hget(key, feature_updated_at_field())
        except Exception as exc:
            logger.error(
                "H1RedisReader get_feature_updated_at 失败: symbol=%s, error=%s",
                symbol,
                exc,
            )
            raise H1RedisUnavailable(f"Redis updated_at 读取失败（symbol={symbol}）: {exc}") from exc

        return _parse_float(raw)

    def get_position(self, symbol: str) -> dict[str, Any]:
        """读取当前持仓，<5ms（蓝图 §4.2）。

        读取 position:{symbol} Hash（amount/cost/avg_price/updated_at）。
        由 PositionProjector 在 OrderFilled 事件时更新。

        Args:
            symbol: 标的代码。

        Returns:
            持仓字典（空仓返回 {}）。字段：amount(int)/cost(float)/avg_price(float)/updated_at(str)。

        Raises:
            H1RedisUnavailable: Redis 不可用。
        """
        from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import position_key

        start = time.perf_counter()
        try:
            key = position_key(symbol)
            raw = self.conn.hgetall(key)
        except Exception as exc:
            logger.error("H1RedisReader get_position 失败: symbol=%s, error=%s", symbol, exc)
            raise H1RedisUnavailable(f"Redis 持仓读取失败（symbol={symbol}）: {exc}") from exc

        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > _READ_LATENCY_WARN_MS:
            logger.warning("H1RedisReader 持仓读取延迟 %.2fms（symbol=%s）", elapsed_ms, symbol)

        if not raw:
            return {}

        # 反序列化数值字段
        result: dict[str, Any] = dict(raw)
        if "amount" in result:
            try:
                result["amount"] = int(float(result["amount"]))
            except (ValueError, TypeError):
                pass
        for num_field in ("cost", "avg_price"):
            if num_field in result:
                val = _parse_float(result[num_field])
                if val is not None:
                    result[num_field] = val
        return result

    def get_risk_status(self) -> dict[str, Any]:
        """读取风控状态，<5ms（蓝图 §4.2）。

        读取 risk:status Hash（level/rule_id/updated_at）。
        由 RiskProjector 在 RiskEvent 时更新。

        Returns:
            风控状态字典（无数据返回 {}）。字段：level(str)/rule_id(str)/updated_at(str)。

        Raises:
            H1RedisUnavailable: Redis 不可用。
        """
        from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import risk_status_key

        start = time.perf_counter()
        try:
            key = risk_status_key()
            raw = self.conn.hgetall(key)
        except Exception as exc:
            logger.error("H1RedisReader get_risk_status 失败: error=%s", exc)
            raise H1RedisUnavailable(f"Redis 风控状态读取失败: {exc}") from exc

        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > _READ_LATENCY_WARN_MS:
            logger.warning("H1RedisReader 风控读取延迟 %.2fms", elapsed_ms)

        return dict(raw) if raw else {}

    def get_account_summary(self) -> dict[str, Any]:
        """读取账户状态（蓝图 §3.2 account:summary）。

        Returns:
            账户字典（total_asset/cash/available/updated_at），无数据返回 {}。

        Raises:
            H1RedisUnavailable: Redis 不可用。
        """
        from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import account_summary_key

        try:
            key = account_summary_key()
            raw = self.conn.hgetall(key)
        except Exception as exc:
            raise H1RedisUnavailable(f"Redis 账户状态读取失败: {exc}") from exc

        if not raw:
            return {}

        result: dict[str, Any] = dict(raw)
        for num_field in ("total_asset", "cash", "available"):
            if num_field in result:
                val = _parse_float(result[num_field])
                if val is not None:
                    result[num_field] = val
        return result
