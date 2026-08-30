# [BLUEPRINT] MOD-H1_REDIS_HOT | docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md | §4.3
# [MODULE] zephyr.infrastructure.h1_redis_hot.h1_cqrs_projectors
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.h1_redis_hot.h1_redis_schema
# [CONSUMERS] zephyr.trading; zephyr.signal; zephyr.risk
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 事件→Redis 物化视图投影; Key 通过 h1_redis_schema 构造; 幂等(idempotency_key 去重)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] redis.RedisError(投影失败)->log+不阻断事件流; ProjectorError(致命错误)
# [TESTS] tests/zephyr/infrastructure/h1_redis_hot/test_h1_cqrs_projectors.py
# [A_module] module_id=MOD-H1_REDIS_HOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# M03豁免: AI趋同演化,非复制粘贴（项目内部标注，非 ruff code）

"""
H1CqrsProjectors — 事件→Redis 物化视图投影器。

真源：
    - 蓝图 §4.3（PositionProjector 接口定义）
    - 数据架构.md §12.4.2（CQRS 读端物化视图）
    - 数据架构.md 行3020（投影逻辑真源）

职责：
    监听 EventBus 事件，将事件投影到 Redis Hash 物化视图（CQRS 读端）。
    D-TRADING 的 OrderFilled → position:{symbol}（持仓视图）。
    D-SIGNAL 的 SignalEvent → signal:active（活跃信号视图）。
    D-RISK 的 RiskEvent → risk:status（风控状态视图）。

设计原则（数据架构.md §12.4.2）：
    - 投影器是单向的：事件 → Redis，不反向
    - 幂等：相同 idempotency_key 的事件不重复投影
    - 最终一致：投影延迟 < 事件处理延迟（Redis <5ms 写入）

用法：
    from zephyr.infrastructure.database_service import DatabaseService
    from zephyr.infrastructure.h1_redis_hot.h1_cqrs_projectors import PositionProjector

    ds = DatabaseService()
    projector = PositionProjector(ds.get_redis_conn())
    # EventBus 订阅时：
    # event_bus.subscribe("OrderFilled", projector.handle)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: h1_cqrs_projectors.py
# 层: 算法
# - id: A1
#   name_zh: ① PositionProjector
#   name_en: PositionProjector
#   intro: OrderFilled 事件 → position:{symbol} Hash 物化视图。
#   desc: OrderFilled 事件 → position:{symbol} Hash 物化视图。 蓝图 §4.3 / 数据架构.md §12.4.2 PositionProjector…；公共方法（定义序）: handle；…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② SignalProjector
#   name_en: SignalProjector
#   intro: SignalEvent → signal:active Set 物化视图。
#   desc: SignalEvent → signal:active Set 物化视图。 蓝图 §3.2 活跃信号 Key。D-SIGNAL 产生信号时投影到 signal:active Se…；公共方法（定义序）: handle；…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ RiskProjector
#   name_en: RiskProjector
#   intro: RiskEvent → risk:status Hash 物化视图。
#   desc: RiskEvent → risk:status Hash 物化视图。 蓝图 §3.2 风控状态 Key。D-RISK 风控状态变更时投影到 risk:status。；公共方法（定义序）: handle；源码 L295-…
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ TradeProjector
#   name_en: TradeProjector
#   intro: ExecutionEvent → trade:today:{symbol} List 物化视图。
#   desc: ExecutionEvent → trade:today:{symbol} List 物化视图。 蓝图 §3.2 当日交易 Key。D-TRADING 成交回报时投影到 trad…；公共方法（定义序）: handle；…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A4 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: PositionProjector, SignalProjector, RiskProjector, TradeProjector
#   downstream: zephyr.trading; zephyr.signal; zephyr.risk
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Protocol

from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import (
    account_summary_key,
    position_key,
    risk_status_key,
    signal_active_key,
    trade_today_key,
)

if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)


class EventLike(Protocol):
    """事件协议（鸭子类型，兼容现有 EventBus 事件）。

    蓝图 §4.3 使用 event.event_type + event.payload，本 Protocol 定义最小接口。
    任何具有这两个属性的对象都可作为事件传入。
    """

    event_type: str
    payload: dict[str, Any]


class ProjectorError(RuntimeError):
    """投影器致命错误（非 Redis 异常，如事件格式非法）。"""


class _BaseProjector:
    """投影器基类——提供 Redis 连接 + 幂等去重 + 错误处理。"""

    def __init__(self, redis_conn: redis.Redis):
        """初始化投影器。

        Args:
            redis_conn: redis.Redis 连接实例（来自 DatabaseService.get_redis_conn()）。
        """
        self.conn = redis_conn
        # 幂等去重集合：projector:idempotent:{projector_name}
        # 已处理的 idempotency_key 存入 Redis Set，TTL 1 天（防止 Set 无限增长）
        self._dedup_prefix = "projector:idempotent"
        self._dedup_ttl = 86400  # 1 天

    def _is_duplicate(self, projector_name: str, idempotency_key: str | None) -> bool:
        """检查事件是否已处理过（幂等去重）。

        使用 Redis SADD 的返回值判断：0=已存在（重复），1=新增（首次）。
        """
        if not idempotency_key:
            return False  # 无 idempotency_key 的事件不去重
        key = f"{self._dedup_prefix}:{projector_name}"
        try:
            added = self.conn.sadd(key, idempotency_key)
            if added:
                # 首次添加，设置 TTL 防止 Set 无限增长
                self.conn.expire(key, self._dedup_ttl)
                return False
            return True  # 已存在=重复
        except Exception:  # noqa: BLE001 — 去重失败不阻断投影（宁可重复也不丢事件）
            logger.warning("幂等去重检查失败，放行事件: %s", idempotency_key, exc_info=True)
            return False


class PositionProjector(_BaseProjector):
    """OrderFilled 事件 → position:{symbol} Hash 物化视图。

    蓝图 §4.3 / 数据架构.md §12.4.2 PositionProjector。

    投影逻辑：
        BUY:  HINCRBY amount +qty, HSET avg_price（加权平均）, HSET updated_at
        SELL: HINCRBY amount -qty, HSET updated_at
        （amount 归零时保留 Key，由盘后清理脚本处理）
    """

    _PROJECTOR_NAME = "position"

    def handle(self, event: EventLike) -> None:
        """处理 OrderFilled 事件，投影到 position:{symbol}。

        Args:
            event: 事件对象，需包含 event_type="OrderFilled" 和 payload：
                    - symbol: 标的代码
                    - direction: "BUY" | "SELL"
                    - quantity: 成交数量
                    - price: 成交价格
                    - idempotency_key: 幂等键（可选，用于去重）

        Raises:
            ProjectorError: 事件格式非法（缺必要字段）。
        """
        if event.event_type != "OrderFilled":
            return  # 非目标事件，忽略

        payload = event.payload
        symbol = payload.get("symbol")
        if not symbol:
            raise ProjectorError(f"OrderFilled 事件缺 symbol: {payload}")

        idem_key = payload.get("idempotency_key")
        if self._is_duplicate(self._PROJECTOR_NAME, idem_key):
            logger.debug("PositionProjector 跳过重复事件: %s", idem_key)
            return

        direction = payload.get("direction", "").upper()
        quantity = payload.get("quantity", 0)
        price = payload.get("price", 0.0)

        if direction not in ("BUY", "SELL"):
            raise ProjectorError(f"OrderFilled direction 非法: {direction}")

        try:
            key = position_key(symbol)
            qty_change = quantity if direction == "BUY" else -quantity

            # 使用 pipeline 原子更新（非事务，但减少 RTT）
            pipe = self.conn.pipeline(transaction=False)
            # HINCRBY amount（整数增减）
            pipe.hincrby(key, "amount", qty_change)
            # HSET updated_at（ISO 时间戳）
            from datetime import UTC, datetime

            pipe.hset(
                key,
                mapping={
                    "updated_at": datetime.now(UTC).isoformat(),
                },
            )
            # BUY 时更新 cost/avg_price（加权平均成本）
            if direction == "BUY" and price > 0:
                # 简化：cost = 新增成本, avg_price 在 Reader 侧按需计算
                # 这里存原始成本增量，Reader 读取后计算
                pipe.hincrbyfloat(key, "cost", quantity * price)
            pipe.execute()

            logger.info(
                "PositionProjector: %s %s qty=%d price=%.4f → %s",
                direction,
                symbol,
                quantity,
                price,
                key,
            )
        except Exception as exc:  # noqa: BLE001 — 投影失败不阻断事件流（蓝图§6.3退化矩阵）
            logger.error("PositionProjector 投影失败: symbol=%s, error=%s", symbol, exc)
            # 不 re-raise——投影失败不阻断事件流（蓝图 §6.3 退化矩阵）
            # Reader 会继续读旧值，最终一致由后续事件修复


class SignalProjector(_BaseProjector):
    """SignalEvent → signal:active Set 物化视图。

    蓝图 §3.2 活跃信号 Key。D-SIGNAL 产生信号时投影到 signal:active Set。
    """

    _PROJECTOR_NAME = "signal"

    def handle(self, event: EventLike) -> None:
        """处理 SignalEvent，投影到 signal:active。

        Args:
            event: event_type="SignalEvent", payload={symbol, signal_type, action}
                    action="OPEN" → SADD signal:active
                    action="CLOSE" → SREM signal:active
        """
        if event.event_type != "SignalEvent":
            return

        payload = event.payload
        symbol = payload.get("symbol")
        if not symbol:
            raise ProjectorError(f"SignalEvent 缺 symbol: {payload}")

        idem_key = payload.get("idempotency_key")
        if self._is_duplicate(self._PROJECTOR_NAME, idem_key):
            return

        action = payload.get("action", "OPEN").upper()
        key = signal_active_key()

        try:
            if action == "OPEN":
                self.conn.sadd(key, symbol)
                logger.info("SignalProjector: SADD %s → %s", symbol, key)
            elif action == "CLOSE":
                self.conn.srem(key, symbol)
                logger.info("SignalProjector: SREM %s → %s", symbol, key)
        except Exception as exc:  # noqa: BLE001 — 投影失败不阻断事件流（蓝图§6.3退化矩阵）
            logger.error("SignalProjector 投影失败: symbol=%s, error=%s", symbol, exc)


class RiskProjector(_BaseProjector):
    """RiskEvent → risk:status Hash 物化视图。

    蓝图 §3.2 风控状态 Key。D-RISK 风控状态变更时投影到 risk:status。
    """

    _PROJECTOR_NAME = "risk"

    def handle(self, event: EventLike) -> None:
        """处理 RiskEvent，投影到 risk:status。

        Args:
            event: event_type="RiskEvent", payload={level, rule_id, message?}
                    level: "normal" | "warning" | "critical"
        """
        if event.event_type != "RiskEvent":
            return

        payload = event.payload
        level = payload.get("level", "normal")
        rule_id = payload.get("rule_id", "")

        idem_key = payload.get("idempotency_key")
        if self._is_duplicate(self._PROJECTOR_NAME, idem_key):
            return

        try:
            from datetime import UTC, datetime

            key = risk_status_key()
            self.conn.hset(
                key,
                mapping={
                    "level": level,
                    "rule_id": rule_id,
                    "updated_at": datetime.now(UTC).isoformat(),
                },
            )
            logger.info("RiskProjector: level=%s rule=%s → %s", level, rule_id, key)
        except Exception as exc:  # noqa: BLE001 — 投影失败不阻断事件流（蓝图§6.3退化矩阵）
            logger.error("RiskProjector 投影失败: error=%s", exc)


class TradeProjector(_BaseProjector):
    """ExecutionEvent → trade:today:{symbol} List 物化视图。

    蓝图 §3.2 当日交易 Key。D-TRADING 成交回报时投影到 trade:today:{symbol}。
    盘后清理脚本按 trade 前缀 scan 删除（蓝图 §7.3 生命周期）。
    """

    _PROJECTOR_NAME = "trade"

    def handle(self, event: EventLike) -> None:
        """处理 ExecutionEvent，投影到 trade:today:{symbol}。

        Args:
            event: event_type="ExecutionEvent", payload={symbol, side, price, quantity, ...}
        """
        if event.event_type != "ExecutionEvent":
            return

        payload = event.payload
        symbol = payload.get("symbol")
        if not symbol:
            raise ProjectorError(f"ExecutionEvent 缺 symbol: {payload}")

        idem_key = payload.get("idempotency_key")
        if self._is_duplicate(self._PROJECTOR_NAME, idem_key):
            return

        try:
            import json
            from datetime import UTC, datetime

            key = trade_today_key(symbol)
            record = {
                **payload,
                "projected_at": datetime.now(UTC).isoformat(),
            }
            self.conn.lpush(key, json.dumps(record, ensure_ascii=False))
            logger.debug("TradeProjector: LPUSH → %s", key)
        except Exception as exc:  # noqa: BLE001 — 投影失败不阻断事件流（蓝图§6.3退化矩阵）
            logger.error("TradeProjector 投影失败: symbol=%s, error=%s", symbol, exc)
