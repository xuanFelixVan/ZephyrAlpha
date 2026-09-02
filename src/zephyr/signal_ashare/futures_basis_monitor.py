# [BLUEPRINT] MOD-SIG-058 | 待统筹登记（blueprint 未建，真源=44号备忘录 §9.8 通道2）
# [MODULE] zephyr.signal_ashare.futures_basis_monitor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] c1_market.futures_kline_qmt（只读）; c1_market.index_quote（只读）; c1_market.kline_futures（只读）; c1_market.kline_index（只读）; c1_market.futures_position（只读）; c1_market.calendar_event（只读）
# [CONSUMERS] （MVP 阶段无——候选消费方：M2 降档触发（贴水急扩）、market_sentiment_analyzer 情绪注解、prediction_log 落库）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只读消费六表不写库；fail-open：任一腿/事件/持仓查询失败不阻塞其余腿，仅 degraded 标注+留痕；两腿皆无→degraded=True 空结果不炸；degraded=True 时结果不可用于 M2 降档决策；输出 dataclass asdict JSON 可序列化（prediction_log 预留）；PIT——所有查询以 ts 为上界
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md §9.8
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/表空/客户端不可用→fail-open 降级（degraded/notes）不抛；ts 格式非法→ValueError（调用方契约违例，fail-closed）
# [TESTS] tests/signal_ashare/test_futures_basis_monitor.py
# [A_module] module_id=MOD-SIG-058 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
MOD-SIG-058 — 期指基差情绪监测器（44号备忘录 §9.8 通道2，M1-⑧/M3-⑥）

第一性原理：期货=机构带杠杆的实时投票机，价格发现领先现货（恐慌时贴水急扩先行）。
消费国内股指期货（IF/IC/IM/IH 主力）与现货指数两腿，输出逐品种基差率/贴水变化率/
贴水急扩告警/持仓确认标志，供 M2 降档触发与情绪注解消费。

品种-现货映射（config 化，默认口径）：
  IF→沪深300(000300) / IC→中证500(000905) / IM→中证1000(000852) / IH→上证50(000016)。
  品种分工注解：IM 对中小盘/题材情绪最敏感（打板策略主看 IM）；IF 主看大盘蓝筹。

数据腿（缺数据优雅降级，逐腿 fail-open）：
  期货分钟腿 = futures_kline_qmt（分钟/tick 采集配置另一代理并行施工中，本模块按表结构
              消费；现表无 timestamp 列，故"30 分钟贴水变化率"暂以前一交易日基差为参照
              的日频代理口径 vel_source="d1_proxy"，分钟采集落地后切换真 30m 参照）；
  现货腿     = index_quote（154k 行实证就绪，3 秒级 timestamp）；
  日频兜底腿 = kline_futures（IF/IC/IM/IH 日频 period='1d'，回补并行施工中）
              + kline_index（现货日收，兼作 σ_20d 历史窗数据源）；
  辅助验证   = futures_position（持仓量同步激增→真对冲确认；平稳→信号打折）；
  交割周     = calendar_event event_type='futures_delivery' 当周→信号降权 0.5
              （贴水自然收敛失真剔除；表空/查询失败 fail-open 不降权+留痕）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 期货分钟腿当日快照（futures_kline_qmt）
#   fields: trade_date/symbol/close/volume（主力=成交量最大合约）
# - id: I2
#   name: 现货实时腿（index_quote）
#   fields: timestamp/price（≤ts 最新一笔）
# - id: I3
#   name: 期货日频历史（kline_futures period='1d'）
#   fields: trade_date/symbol/close/volume（主力按日成交量最大）
# - id: I4
#   name: 现货日频历史（kline_index）
#   fields: trade_date/close
# - id: I5
#   name: 持仓量（futures_position）
#   fields: trade_date/long_position/short_position（品种跨合约合计）
# - id: I6
#   name: 交割周日历（calendar_event futures_delivery）
#   fields: event_date
# 层: 特征
# - id: F1
#   name_zh: 基差率
#   formula: basis_rate = (F_主力 - S_现货) / S_现货
# - id: F2
#   name_zh: 贴水变化率（30 分钟口径，当前 d1_proxy）
#   formula: basis_vel_30m = basis_rate(t) - basis_rate(t-30min)  # 分钟腿未落地前=今日-前一交易日基差
# - id: F3
#   name_zh: 基差日变化 20 日 σ
#   formula: σ_20d = stdev(diff(daily_basis_series), 近20个差分)  # 样本<5 不定性
# - id: F4
#   name_zh: 持仓激增率
#   formula: pos_surge = (最新日总持仓 - 前5日均值) / 前5日均值  # >10% 激增
# 层: 算法
# - id: A1
#   name_zh: 贴水急扩告警
#   desc: F2 < -1.5×F3 → discount_alert=True（机构对冲避险急增，M2 降档触发输出之一）
# - id: A2
#   name_zh: 交割周降权
#   desc: ts 所在 ISO 周存在 futures_delivery 事件 → applied_weight=0.5；查询失败 fail-open 不降权+留痕
# - id: A3
#   name_zh: 持仓确认
#   desc: 告警且 F4>10% → confirm_flag=True（真对冲）；告警且持仓平稳 → confirm_flag=False，signal_weight×0.5（或为期指单边投机）；持仓数据不可用 → confirm_flag=None 不打折（fail-open）
# - id: A4
#   name_zh: 降级链
#   desc: 分钟腿缺→日频腿+degraded 标注；单腿缺→该品种跳过留痕；两腿皆无→snapshot degraded=True 空结果
# 层: 输出
# - id: O1
#   name_zh: FuturesBasisSnapshot
#   intro: ts/trade_date/per_symbol{basis_rate,basis_vel_30m,discount_alert,confirm_flag,...}/delivery_week/applied_weight/degraded/notes；frozen dataclass JSON 可序列化（prediction_log 预留）
# [/ALGO_FLOW]
#
# 边:
# I1,I2,I3,I4 --> F1,F2,F3
# F2,F3 --> A1
# I6 --> A2
# I5,F4,A1 --> A3
# I1,I2,I3,I4 --> A4
# A1,A2,A3,A4 --> O1
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Final
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

__all__: Final = [
    "FuturesBasisConfig",
    "FuturesBasisSnapshot",
    "FuturesBasisSymbol",
    "FuturesProduct",
    "compute_futures_basis",
]

_TZ_SHANGHAI: Final = ZoneInfo("Asia/Shanghai")

# SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值
SQL_SPOT_LATEST: Final = """
SELECT timestamp, price
FROM c1_market.index_quote
WHERE symbol = %(spot_symbol)s AND trade_date = %(trade_date)s AND timestamp <= %(ts)s
ORDER BY timestamp DESC
LIMIT 1
"""

SQL_FUTURES_QMT_INTRADAY: Final = """
SELECT symbol, close, volume
FROM c1_market.futures_kline_qmt
WHERE trade_date = %(trade_date)s AND symbol LIKE %(prefix)s
"""

SQL_FUTURES_DAILY: Final = """
SELECT trade_date, symbol, close, volume
FROM c1_market.kline_futures
WHERE period = '1d' AND symbol LIKE %(prefix)s AND trade_date <= %(trade_date)s
ORDER BY trade_date DESC
LIMIT %(limit)s
"""

SQL_SPOT_DAILY: Final = """
SELECT trade_date, close
FROM c1_market.kline_index
WHERE symbol IN %(symbols)s AND trade_date <= %(trade_date)s
ORDER BY trade_date DESC
LIMIT %(limit)s
"""

SQL_POSITION_RECENT: Final = """
SELECT trade_date, symbol, long_position, short_position
FROM c1_market.futures_position
WHERE symbol LIKE %(prefix)s AND trade_date <= %(trade_date)s
ORDER BY trade_date DESC
LIMIT %(limit)s
"""

SQL_DELIVERY_EVENTS: Final = """
SELECT event_date
FROM c1_market.calendar_event
WHERE event_type = %(event_type)s AND event_date BETWEEN %(week_start)s AND %(week_end)s
"""


@dataclass(frozen=True, slots=True)
class FuturesProduct:
    """品种-现货映射（config 化；44号 §9.8 品种分工注解随映射携带）。"""

    product: str  # 期指品种码 IF/IC/IM/IH
    spot_name: str  # 现货指数中文名
    quote_symbol: str  # index_quote 写法（QMT 带后缀，如 000300.SH）
    kline_symbols: tuple[str, ...]  # kline_index 候选写法（裸码/带后缀并存兼容）
    sensitivity: str  # 品种分工注解


DEFAULT_PRODUCTS: Final = (
    FuturesProduct("IF", "沪深300", "000300.SH", ("000300", "000300.SH"), "IF 主看大盘蓝筹"),
    FuturesProduct("IC", "中证500", "000905.SH", ("000905", "000905.SH"), "IC 看中盘"),
    FuturesProduct("IM", "中证1000", "000852.SH", ("000852", "000852.SH"), "IM 对中小盘/题材情绪最敏感，打板策略主看"),
    FuturesProduct("IH", "上证50", "000016.SH", ("000016", "000016.SH"), "IH 看超大盘蓝筹"),
)


@dataclass(frozen=True, slots=True)
class FuturesBasisConfig:
    """阈值配置——默认值取自 44号备忘录 §9.8 通道2。"""

    products: tuple[FuturesProduct, ...] = DEFAULT_PRODUCTS
    vel_sigma_threshold: float = 1.5  # 贴水急扩：basis_vel < -1.5σ_20d
    sigma_window_days: int = 20  # σ 窗口（日频基差差分个数）
    sigma_min_samples: int = 5  # σ 最小样本（噪声护栏，不足不定性）
    delivery_week_weight: float = 0.5  # 交割周信号降权
    position_confirm_pct: float = 0.10  # 持仓激增确认阈值（对前5日均值）
    position_lookback_days: int = 5  # 持仓均值参照窗（交易日）
    unconfirmed_discount: float = 0.5  # 告警未被持仓确认时的信号打折系数
    daily_lookback_limit: int = 60  # 日频历史查询行数上限（覆盖 σ 窗口+兜底）


@dataclass(frozen=True, slots=True)
class FuturesBasisSymbol:
    """单品种基差明细。"""

    product: str
    spot_name: str
    basis_rate: float | None  # F1 基差率
    basis_vel_30m: float | None  # F2 贴水变化率（vel_source 标明口径）
    vel_source: str  # "d1_proxy"（分钟腿未落地前）/ 未来 "intraday_30m"
    discount_alert: bool  # A1 贴水急扩告警
    confirm_flag: bool | None  # A3 持仓确认；None=持仓数据不可用（fail-open）
    signal_weight: float  # 品种级信号权重（未确认告警打折 0.5）
    futures_price: float | None
    spot_price: float | None
    futures_leg: str  # futures_kline_qmt / kline_futures_daily
    spot_leg: str  # index_quote_intraday / kline_index_daily
    sigma_20d: float | None
    position_surge_pct: float | None
    sensitivity: str  # 品种分工注解
    degraded: bool  # 任一斑降级日频/数据不全即 True
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class FuturesBasisSnapshot:
    """期指基差情绪输出契约（盘中实时计算，M2 降档/情绪注解消费）。"""

    ts: str  # 计算时点 YYYY-MM-DD HH:MM:SS（Asia/Shanghai）
    trade_date: str  # 数据日 YYYY-MM-DD
    per_symbol: dict[str, FuturesBasisSymbol] = field(default_factory=dict)
    delivery_week: bool = False  # ts 所在周为股指期货交割周
    applied_weight: float = 1.0  # 快照级权重（交割周 0.5）
    degraded: bool = False  # 两腿皆无/客户端不可用时 True，结果不可用于决策
    notes: list[str] = field(default_factory=list)  # 降级原因等留痕


def _normalize_ts(ts: datetime | date | str | None) -> datetime:
    """归一化计算时点（None→当前 Asia/Shanghai；非法格式抛 ValueError）。"""
    if ts is None:
        return datetime.now(_TZ_SHANGHAI).replace(tzinfo=None)
    if isinstance(ts, datetime):
        return ts.replace(tzinfo=None)
    if isinstance(ts, date):
        return datetime(ts.year, ts.month, ts.day)
    s = str(ts)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"ts 格式非法（须 YYYY-MM-DD[ HH:MM:SS]）: {ts!r}")


def _to_date(v: Any) -> date:
    """CH Date 列返回值归一（date 或 'YYYY-MM-DD' 字符串）。"""
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    return datetime.strptime(str(v), "%Y-%m-%d").date()


def _default_client():
    """延迟加载默认 CH 客户端（不可用时返回 None，由主入口转 degraded）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，期指基差监测降级", exc_info=True)
        return None


def _query(client: Any, sql: str, params: dict, notes: list[str], label: str) -> list[tuple]:
    """fail-open 查询包装：异常→空结果+留痕，不阻塞其余腿。"""
    try:
        return client.execute(sql, params)
    except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
        logger.warning("%s 查询失败(fail-open): %r", label, e)
        notes.append(f"{label} 查询失败(fail-open): {e!r}")
        return []


def _pick_main_by_volume(rows: list[tuple], close_idx: int, vol_idx: int) -> float | None:
    """主力合约=成交量最大行（快照腿当日多合约并存时）。"""
    best_price: float | None = None
    best_vol = -1.0
    for r in rows:
        close = float(r[close_idx] or 0.0)
        vol = float(r[vol_idx] or 0.0)
        if close <= 0:
            continue
        if vol > best_vol:
            best_vol = vol
            best_price = close
    return best_price


def _daily_main_series(rows: list[tuple]) -> dict[date, float]:
    """期货日频历史→{trade_date: 主力收盘}（逐日成交量最大合约）。"""
    best: dict[date, tuple[float, float]] = {}
    for r in rows:
        td = _to_date(r[0])
        close = float(r[2] or 0.0)
        vol = float(r[3] or 0.0)
        if close <= 0:
            continue
        cur = best.get(td)
        if cur is None or vol > cur[0]:
            best[td] = (vol, close)
    return {td: close for td, (_, close) in best.items()}


def _daily_spot_series(rows: list[tuple]) -> dict[date, float]:
    """现货日频历史→{trade_date: 收盘}（DESC 序首见优先，兼容裸码/带后缀双写法）。"""
    series: dict[date, float] = {}
    for r in rows:
        td = _to_date(r[0])
        close = float(r[1] or 0.0)
        if close > 0 and td not in series:
            series[td] = close
    return series


def _basis_series(fut: dict[date, float], spot: dict[date, float]) -> list[tuple[date, float]]:
    """日频基差序列（两腿日期交集，升序）。"""
    return [(td, (fut[td] - spot[td]) / spot[td]) for td in sorted(set(fut) & set(spot)) if spot[td] > 0]


def _sigma_20d(series: list[tuple[date, float]], cfg: FuturesBasisConfig) -> float | None:
    """基差日差分 σ（样本不足→None 不定性，不出告警）。"""
    diffs = [series[i][1] - series[i - 1][1] for i in range(1, len(series))]
    window = diffs[-cfg.sigma_window_days :]
    if len(window) < cfg.sigma_min_samples:
        return None
    return statistics.stdev(window)


def _position_surge(rows: list[tuple], cfg: FuturesBasisConfig) -> tuple[bool | None, float | None]:
    """持仓确认：最新日总持仓对前 N 日均值激增 → True（真对冲）；平稳 → False；无数据 → None。"""
    by_date: dict[date, float] = {}
    for r in rows:
        td = _to_date(r[0])
        by_date[td] = by_date.get(td, 0.0) + float(r[2] or 0.0) + float(r[3] or 0.0)
    days = sorted(by_date, reverse=True)
    if not days:
        return None, None
    latest = by_date[days[0]]
    ref = [by_date[d] for d in days[1 : 1 + cfg.position_lookback_days]]
    if not ref:
        return None, None
    mean = sum(ref) / len(ref)
    if mean <= 0:
        return None, None
    surge = (latest - mean) / mean
    return surge > cfg.position_confirm_pct, surge


def _compute_product(
    client: Any,
    product: FuturesProduct,
    d: date,
    ts_str: str,
    cfg: FuturesBasisConfig,
) -> FuturesBasisSymbol | None:
    """单品种基差计算；两腿皆缺→None（由主入口汇总判定 snapshot 级 degraded）。"""
    notes: list[str] = []
    prefix = f"{product.product}%"

    # ---- 现货腿：index_quote 盘中最新（≤ts）→ kline_index 日收兜底 ----
    spot_rows = _query(
        client,
        SQL_SPOT_LATEST,
        {"spot_symbol": product.quote_symbol, "trade_date": d, "ts": ts_str},
        notes,
        f"{product.product} 现货实时腿(index_quote)",
    )
    spot_daily_rows = _query(
        client,
        SQL_SPOT_DAILY,
        {"symbols": product.kline_symbols, "trade_date": d, "limit": cfg.daily_lookback_limit},
        notes,
        f"{product.product} 现货日频(kline_index)",
    )
    spot_daily = _daily_spot_series(spot_daily_rows)
    spot_price: float | None = None
    spot_leg = ""
    degraded = False
    if spot_rows and float(spot_rows[0][1] or 0.0) > 0:
        spot_price = float(spot_rows[0][1])
        spot_leg = "index_quote_intraday"
    elif spot_daily:
        spot_price = spot_daily[max(spot_daily)]
        spot_leg = "kline_index_daily"
        degraded = True
        notes.append("现货盘中腿缺失，降级日频收盘(kline_index)")
    else:
        notes.append("现货两腿皆缺")

    # ---- 期货腿：futures_kline_qmt 当日 → kline_futures 日频兜底 ----
    fut_qmt_rows = _query(
        client,
        SQL_FUTURES_QMT_INTRADAY,
        {"trade_date": d, "prefix": prefix},
        notes,
        f"{product.product} 期货分钟腿(futures_kline_qmt)",
    )
    fut_daily_rows = _query(
        client,
        SQL_FUTURES_DAILY,
        {"prefix": prefix, "trade_date": d, "limit": cfg.daily_lookback_limit},
        notes,
        f"{product.product} 期货日频(kline_futures)",
    )
    fut_daily = _daily_main_series(fut_daily_rows)
    futures_price = _pick_main_by_volume(fut_qmt_rows, close_idx=1, vol_idx=2)
    futures_leg = ""
    if futures_price is not None:
        futures_leg = "futures_kline_qmt"
    elif fut_daily:
        futures_price = fut_daily[max(fut_daily)]
        futures_leg = "kline_futures_daily"
        degraded = True
        notes.append("期货分钟腿缺失，降级日频腿(kline_futures)")
    else:
        notes.append("期货两腿皆缺")

    if futures_price is None or spot_price is None:
        logger.warning("%s 基差单腿缺失跳过: %s", product.product, "; ".join(notes))
        return None

    # ---- F1 基差率 / F2 贴水变化率（d1_proxy）/ F3 σ_20d ----
    basis_rate = (futures_price - spot_price) / spot_price
    history = _basis_series(fut_daily, spot_daily)
    sigma = _sigma_20d(history, cfg)
    prev = [b for td, b in history if td < d]
    basis_vel: float | None = None
    if prev:
        basis_vel = basis_rate - prev[-1]
    else:
        notes.append("无前一日基差参照，贴水变化率缺省")
    if sigma is None:
        notes.append(f"σ_20d 样本不足(<{cfg.sigma_min_samples})，不出贴水急扩告警")

    # ---- A1 贴水急扩告警 ----
    alert = basis_vel is not None and sigma is not None and basis_vel < -cfg.vel_sigma_threshold * sigma

    # ---- A3 持仓确认（fail-open：无数据/查询失败→confirm_flag=None 不打折）----
    pos_rows = _query(
        client,
        SQL_POSITION_RECENT,
        {"prefix": prefix, "trade_date": d, "limit": (cfg.position_lookback_days + 1) * 10},  # 单日多合约行预留
        notes,
        f"{product.product} 持仓(futures_position)",
    )
    confirm, surge_pct = _position_surge(pos_rows, cfg)
    signal_weight = 1.0
    if alert:
        if confirm is True:
            notes.append(f"持仓同步激增{surge_pct:.1%} → 真对冲确认")
        elif confirm is False:
            signal_weight = cfg.unconfirmed_discount
            notes.append(
                f"持仓平稳(激增率{surge_pct:.1%}≤{cfg.position_confirm_pct:.0%}) → 信号打折×{cfg.unconfirmed_discount}（或为期指单边投机）"
            )
        else:
            notes.append("持仓数据不可用，告警不打折(fail-open)")

    return FuturesBasisSymbol(
        product=product.product,
        spot_name=product.spot_name,
        basis_rate=basis_rate,
        basis_vel_30m=basis_vel,
        vel_source="d1_proxy",
        discount_alert=alert,
        confirm_flag=confirm,
        signal_weight=signal_weight,
        futures_price=futures_price,
        spot_price=spot_price,
        futures_leg=futures_leg,
        spot_leg=spot_leg,
        sigma_20d=sigma,
        position_surge_pct=surge_pct,
        sensitivity=product.sensitivity,
        degraded=degraded,
        notes=notes,
    )


def compute_futures_basis(
    ts: datetime | date | str | None = None,
    ch_client: Any | None = None,
    config: FuturesBasisConfig | None = None,
) -> FuturesBasisSnapshot:
    """主入口：国内期指基差情绪快照（44号 §9.8 通道2，M1-⑧/M3-⑥）。

    Args:
        ts: 计算时点（None→当前 Asia/Shanghai；PIT 上界，仅消费 ≤ts 数据）。
        ch_client: clickhouse-driver 鸭子类型（execute(sql, params) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client，不可得→degraded。
        config: 阈值/映射配置（None 用默认 44号 §9.8 口径）。

    Returns:
        FuturesBasisSnapshot；两腿皆无/查询异常 → degraded=True 空结果不炸
        （对齐 MOD-SIG-056/057 降级范式）。
    """
    cfg = config or FuturesBasisConfig()
    t = _normalize_ts(ts)
    d = t.date()
    ts_str = t.strftime("%Y-%m-%d %H:%M:%S")
    notes: list[str] = []

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        logger.warning("期指基差监测降级: ch_client 未注入且默认客户端不可用")
        return FuturesBasisSnapshot(
            ts=ts_str, trade_date=d.isoformat(), degraded=True, notes=["ch_client 未注入且默认客户端不可用"]
        )

    # ---- A2 交割周判定（fail-open：表空/查询失败→不降权+留痕）----
    week_start = d - timedelta(days=d.weekday())
    week_end = week_start + timedelta(days=6)
    delivery_week = False
    event_rows = _query(
        client,
        SQL_DELIVERY_EVENTS,
        {"event_type": "futures_delivery", "week_start": week_start, "week_end": week_end},
        notes,
        "交割周日历(calendar_event)",
    )
    if event_rows:
        delivery_week = True
        notes.append(
            f"{week_start.isoformat()}~{week_end.isoformat()} 为股指期货交割周，贴水自然收敛失真剔除 → 信号降权×{cfg.delivery_week_weight}"
        )
    applied_weight = cfg.delivery_week_weight if delivery_week else 1.0

    per_symbol: dict[str, FuturesBasisSymbol] = {}
    for product in cfg.products:
        result = _compute_product(client, product, d, ts_str, cfg)
        if result is not None:
            per_symbol[product.product] = result

    if not per_symbol:
        notes.append("全部品种两腿皆无（期货+现货数据缺口）")
        logger.warning("期指基差监测降级: %s", notes[-1])
        return FuturesBasisSnapshot(
            ts=ts_str,
            trade_date=d.isoformat(),
            delivery_week=delivery_week,
            applied_weight=applied_weight,
            degraded=True,
            notes=notes,
        )

    return FuturesBasisSnapshot(
        ts=ts_str,
        trade_date=d.isoformat(),
        per_symbol=per_symbol,
        delivery_week=delivery_week,
        applied_weight=applied_weight,
        degraded=False,
        notes=notes,
    )
