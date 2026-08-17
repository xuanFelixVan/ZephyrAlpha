# [BLUEPRINT] MOD-XS-006 | docs/03_modules/_domain_ex_sor/market_context_provider/blueprint.md
# [MODULE] zephyr.ex_sor.core.market_context_provider
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.ex_sor.core.algo_trading_engine; zephyr.infrastructure.h1_redis_hot.h1_redis_schema; zephyr.market_data.normalized_market_data_producer.producer; zephyr.shared.contracts.market_data
# [CONSUMERS] MOD-L06-001(D_EXECUTION_CORE ExecutionEngine,注入构造 MarketContext 供 generate_plan)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] last_price>0; adv>0(无K线则raise AlgoError); tick缺失时用最近K线close兜底; symbol格式双向兼容(600519/600519.SH/QMT)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlgoError(无ADV/无任何价格源); Redis故障->降级到K线close(不阻断)
# [TESTS] tests/ex_sor/test_market_context_provider.py
# [A_module] module_id=MOD-XS-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

Market Context Provider — 市场上下文提供器 (MOD-XS-006)

D-EX-SOR §2.2 XS-05 配套: 为 AlgoTradingEngine.generate_plan 提供 MarketContext。

治本定位 (2026-08-05 G7 接入):
    原 ExecutionEngine._execute_twap/_execute_vwap 为占位实现——直接 submit_order 整笔订单,
    无切片、无行情。治本方案: 构建 MarketContextProvider 从现有行情基础设施获取真实数据,
    让 generate_plan() 基于真实 last_price/adv/bid/ask 生成切片, 实现执行引擎与算法层解耦。

数据来源 (复用现有基础设施, 不重造):
    - last_price / bid_price / ask_price → Redis tick:{symbol}:latest Hash
      (D-DATA tick_subscriber 双写, tick_redis_cache.tick_to_cache_dict 产出字段)
    - adv (日均成交量) → ClickHouse kline_daily via load_kline
      (近 N 个非停牌交易日的 volume 均值)
    - volume_profile → 默认 §13.2 日内分布 (algo_trading_engine.DEFAULT_VOLUME_PROFILE)

符号格式兼容:
    tick Redis Key 用 QMT 格式 ("000001.SZ"); Order.symbol 可能是 "600519" / "600519.SH"。
    本模块内部 _to_qmt_symbol 推断交易所后缀, 三种格式通吃。

降级策略:
    - Redis tick 缺失 → last_price 用最近 K线 close, bid/ask=None (AlgoError 仅在无任何价格源时抛)
    - Redis 故障 → 同上 (best-effort, 不阻断)
    - load_kline 空 (无K线) → 抛 AlgoError (无 ADV 无法做 §13.1 上限检查)

SSoT: depgraph MOD-XS-006
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Redis tick 最新快照 Hash
#   fields: price/bid1/ask1（tick:{symbol}:latest，QMT格式key，repr存储）
#   code: tick_latest_key(symbol) hgetall (market_context_provider.py L193-207)
# - id: I2
#   name: ClickHouse 日K线数据
#   fields: timestamp/volume/close/is_suspended（近35自然日窗口）
#   code: load_kline (market_context_provider.py L222)
# - id: I3
#   name: 默认日内成交量分布
#   fields: §13.2 日内分布 volume_profile 默认配置
#   code: algo_trading_engine.DEFAULT_VOLUME_PROFILE (market_context_provider.py L54-58)
# - id: I4
#   name: 标的代码 symbol
#   fields: 600519/600519.SH/QMT格式三种均可
#   code: get_context(symbol) (market_context_provider.py L154)
# 层: 特征
# - id: F1
#   name_zh: 日均成交量 ADV
#   name_en: adv
#   intro: 近20个非停牌交易日成交量均值，是切片上限检查的流动性基准
#   formula: 拉35自然日日K→按timestamp升序→滤is_suspended且volume>0→取最近20日→adv=Σvolume/20
#   code: market_context_provider.py L230-241
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 符号格式归一化
#   name_en: _to_qmt_symbol
#   intro: 推断交易所后缀把symbol统一成QMT格式，三种写法通吃
#   desc: 已带后缀原样返回；0/3开头→.SZ；6/5/9开头→.SH；无法判定兜底.SH（L79-101）
#   inputs: I4
#   outputs: QMT格式symbol
#   invariant: symbol格式双向兼容
# - id: A2
#   name_zh: ② Redis tick 读取与降级
#   name_en: _read_tick
#   intro: best-effort读tick Hash，故障或QMT key查不到再用原始symbol补查，都不行返回空dict降级K线
#   desc: hgetall(tick_latest_key(qmt))，异常→warning+{}；空且qmt≠原symbol→原key再查一次（L193-207）
#   inputs: I1 A1
#   outputs: tick dict（可空）
# - id: A3
#   name_zh: ③ ADV 与最近收盘价计算
#   name_en: _compute_adv_and_close
#   intro: 从日K算ADV并取最新close，ClickHouse故障降级返回(None,None)不阻断
#   desc: load_kline(近35自然日)→升序排序→滤停牌/零量→最近20日均量=adv，ordered[-1].close=latest_close（L211-242）
#   inputs: I2
#   outputs: (adv, latest_close)（可None）
# - id: A4
#   name_zh: ④ MarketContext 组装
#   name_en: RedisKlineMarketContextProvider.get_context
#   intro: tick优先K线兜底定last_price，校验adv>0，组装出算法交易引擎要的市场上下文
#   desc: last_price=tick.price或K线close，bid/ask仅来自tick；无价格源或无ADV→raise AlgoError（L154-189）
#   inputs: A2 A3 F1 I3 I4
#   outputs: MarketContext
#   invariant: last_price>0；adv>0（无K线raise AlgoError）；tick缺失用最近K线close兜底
# - id: A5
#   name_zh: ⑤ 静态测试提供器
#   name_en: StaticMarketContextProvider
#   intro: 测试用固定上下文，不访问Redis/ClickHouse，symbol不一致时按订单重建
#   desc: 构造注入固定MarketContext；get_context时symbol不同则复制重建对齐订单（L245-289）
#   inputs: I4
#   outputs: MarketContext（固定）
# 层: 输出
# - id: O1
#   name_zh: 市场上下文 MarketContext
#   name_en: MarketContext
#   intro: 含last_price/adv/volume_profile/bid/ask，供generate_plan生成TWAP/VWAP真实切片
#   invariant: last_price>0 且 adv>0
#   downstream: MOD-L06-001 ExecutionEngine（注入构造 MarketContext 供 generate_plan）
# [/ALGO_FLOW]
#
# 边:
# I4 --> A1
# I1 --> A2
# A1 --> A2
# I2 --> A3
# I2 -.->|断点| F1
# F1 --> A4
# A2 --> A4
# A3 --> A4
# I3 --> A4
# I4 --> A4
# I4 --> A5
# A4 --> O1
# A5 --> O1
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from statistics import mean
from typing import TYPE_CHECKING, Final, Protocol

from zephyr.ex_sor.core.algo_trading_engine import (
    DEFAULT_VOLUME_PROFILE,
    AlgoError,
    MarketContext,
)
from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key
from zephyr.market_data.normalized_market_data_producer.producer import load_kline

if TYPE_CHECKING:
    import redis

    from zephyr.shared.contracts.market_data import NormalizedMarketData

__all__: Final = [
    "MarketContextProvider",
    "RedisKlineMarketContextProvider",
    "StaticMarketContextProvider",
]

logger = logging.getLogger(__name__)

# ADV 计算窗口: 拉 adv_window_days 自然日 → 取最近 adv_lookback_days 个非停牌交易日
_DEFAULT_ADV_LOOKBACK_DAYS: Final[int] = 20
_DEFAULT_ADV_WINDOW_DAYS: Final[int] = 35


def _to_qmt_symbol(symbol: str) -> str:
    """推断 QMT 格式交易所后缀 (tick Redis Key 用 QMT 格式)。

    6/5/9 开头 → .SH (沪市/沪基金/科创板); 0/3 开头 → .SZ (深市/创业板);
    已带后缀 → 原样返回; 无法判定 → .SH 兜底。

    Args:
        symbol: "600519" / "600519.SH" / "000001.SZ" 均可

    Returns:
        QMT 格式 symbol ("600519.SH")
    """
    s = symbol.strip()
    if "." in s:
        return s.upper()
    if not s:
        return s
    head = s[0]
    if head in ("0", "3"):
        return f"{s}.SZ"
    if head in ("6", "5", "9"):
        return f"{s}.SH"
    return f"{s}.SH"


def _parse_decimal(val: object) -> Decimal | None:
    """安全解析 Redis Hash 值 (repr 存储) 为 Decimal, 失败/非正返回 None。"""
    if val is None:
        return None
    try:
        d = Decimal(str(val))
    except Exception:  # noqa: BLE001 — 防御性解析
        return None
    return d if d > 0 else None


class MarketContextProvider(Protocol):
    """市场上下文提供器接口——供 ExecutionEngine 依赖注入 (解耦)。"""

    def get_context(self, symbol: str) -> MarketContext:
        """构造指定标的的 MarketContext 快照。

        Args:
            symbol: 标的代码 (接受 "600519" / "600519.SH" / "000001.SZ")

        Returns:
            MarketContext (last_price>0, adv>0)

        Raises:
            AlgoError: 无任何价格源 / 无 ADV (K线缺失)
        """


class RedisKlineMarketContextProvider:
    """Redis tick + ClickHouse 日K → MarketContext (生产实现)。

    用法::

        from zephyr.infrastructure.database_service import DatabaseService
        ds = DatabaseService(...)
        provider = RedisKlineMarketContextProvider(redis_conn=ds.get_redis_conn())
        ctx = provider.get_context("600519")
        plan = algo_engine.generate_plan(order, params, ctx)
    """

    def __init__(
        self,
        redis_conn: redis.Redis,
        adv_lookback_days: int = _DEFAULT_ADV_LOOKBACK_DAYS,
        adv_window_days: int = _DEFAULT_ADV_WINDOW_DAYS,
    ) -> None:
        self._redis = redis_conn
        self._adv_lookback = max(1, adv_lookback_days)
        self._adv_window = max(self._adv_lookback, adv_window_days)

    def get_context(self, symbol: str) -> MarketContext:
        if not symbol or not symbol.strip():
            raise AlgoError("symbol 不能为空", details={"field": "symbol"})

        tick = self._read_tick(symbol)
        adv, latest_close = self._compute_adv_and_close(symbol)

        # last_price: tick 优先, 缺失用最近 K线 close 兜底
        last_price = _parse_decimal(tick.get("price")) or latest_close
        if last_price is None or last_price <= 0:
            raise AlgoError(
                f"无法获取 {symbol} 的 last_price (tick 与 K线均缺失)",
                details={"symbol": symbol, "tick": bool(tick), "kline_close": str(latest_close)},
            )

        bid_price = _parse_decimal(tick.get("bid1"))
        ask_price = _parse_decimal(tick.get("ask1"))

        if adv is None or adv <= 0:
            raise AlgoError(
                f"无法计算 {symbol} 的 ADV (K线缺失或全停牌)",
                details={"symbol": symbol, "lookback": self._adv_lookback},
            )

        logger.info(
            "MarketContext: symbol=%s last=%s adv=%s bid=%s ask=%s (tick=%s)",
            symbol, last_price, adv, bid_price, ask_price, bool(tick),
        )
        return MarketContext(
            symbol=symbol,
            last_price=last_price,
            adv=adv,
            volume_profile=dict(DEFAULT_VOLUME_PROFILE),
            bid_price=bid_price,
            ask_price=ask_price,
        )

    # ── 内部: Redis tick 读取 ──

    def _read_tick(self, symbol: str) -> dict[str, str]:
        """读 Redis tick:{symbol}:latest Hash, best-effort (故障返回空 dict)。"""
        qmt = _to_qmt_symbol(symbol)
        try:
            data = self._redis.hgetall(tick_latest_key(qmt))
        except Exception as exc:  # noqa: BLE001 — best-effort, 降级到 K线
            logger.warning("Redis tick 读取失败 symbol=%s: %s (降级到 K线 close)", symbol, exc)
            return {}
        # 兜底: QMT 格式查不到, 用原始 symbol 再查一次
        if not data and qmt != symbol:
            try:
                data = self._redis.hgetall(tick_latest_key(symbol))
            except Exception:  # noqa: BLE001
                data = {}
        return data or {}

    # ── 内部: ADV + 最近 close ──

    def _compute_adv_and_close(
        self, symbol: str
    ) -> tuple[Decimal | None, Decimal | None]:
        """从 ClickHouse 日K计算 ADV (近 N 个非停牌交易日 volume 均值) + 最近 close。

        Returns:
            (adv, latest_close) — 无数据时对应位为 None
        """
        end = datetime.now(UTC).date()
        start = end - timedelta(days=self._adv_window)
        try:
            records = load_kline([symbol], start.isoformat(), end.isoformat())
        except Exception as exc:  # noqa: BLE001 — ClickHouse 故障降级
            logger.warning("load_kline 失败 symbol=%s: %s", symbol, exc)
            return None, None

        if not records:
            return None, None

        # 按 timestamp 升序, 取最近 N 个非停牌交易日
        ordered = sorted(records, key=lambda r: r.timestamp)
        active = [r for r in ordered if not r.is_suspended and r.volume > 0]
        if not active:
            return None, ordered[-1].close

        recent = active[-self._adv_lookback:]
        adv = Decimal(str(mean(float(r.volume) for r in recent)))
        # Decimal 均值更精确: 用 sum/len
        total = sum((r.volume for r in recent), Decimal("0"))
        adv = total / Decimal(len(recent))
        latest_close = ordered[-1].close
        return adv, latest_close


class StaticMarketContextProvider:
    """测试用静态提供器——返回固定 MarketContext (不访问 Redis/ClickHouse)。

    用法::

        provider = StaticMarketContextProvider(ctx)
        # 或便捷构造
        provider = StaticMarketContextProvider.from_values(
            symbol="600519", last_price=100, adv=100000, bid=99.9, ask=100.1)
    """

    def __init__(self, ctx: MarketContext) -> None:
        self._ctx = ctx

    def get_context(self, symbol: str) -> MarketContext:
        # symbol 不一致时重建一个 (保持 ctx 其余字段), 确保 symbol 与订单对齐
        if symbol and symbol != self._ctx.symbol:
            return MarketContext(
                symbol=symbol,
                last_price=self._ctx.last_price,
                adv=self._ctx.adv,
                volume_profile=dict(self._ctx.volume_profile),
                bid_price=self._ctx.bid_price,
                ask_price=self._ctx.ask_price,
            )
        return self._ctx

    @classmethod
    def from_values(
        cls,
        symbol: str,
        last_price: Decimal | float | str,
        adv: Decimal | float | str,
        bid_price: Decimal | float | str | None = None,
        ask_price: Decimal | float | str | None = None,
    ) -> StaticMarketContextProvider:
        """便捷构造: 接受 Decimal/float/str (内部转 Decimal)。"""
        ctx = MarketContext(
            symbol=symbol,
            last_price=Decimal(str(last_price)),
            adv=Decimal(str(adv)),
            bid_price=Decimal(str(bid_price)) if bid_price is not None else None,
            ask_price=Decimal(str(ask_price)) if ask_price is not None else None,
        )
        return cls(ctx)
