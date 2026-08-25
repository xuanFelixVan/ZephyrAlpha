# [BLUEPRINT] MOD-MKT-007 | docs/03_modules/_domain_mkt_data/auction_data_manager/blueprint.md | §
# [MODULE] zephyr.market_data.auction_data_manager
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SIG-089 auction_microstructure_analyzer（快照注入面）；MOD-PLAN-015 auction_hit_recorder（命中率回放供数面）；调度器（运行时装配批挂接）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 记录构造即 Fail-Closed（价>0/量≥0/撤单≤申报/PIT 当日/session 匹配）; (symbol,ts) 批内去重保首条; fetcher/sink/loader 异常不炸调度（status/notes 留痕）; 回放输出按 (symbol,ts) 排序、同标的 ts 严格递增; 不直连行情源/DB（三面全注入）
# [MODIFY-GUARD] 双 D-DATA-32 撞名裁定（canonical=CAND-MKTDATA-003/B10-02234，CAND-MKTDATA-004/B13-04251 REVIEW 归并本模块）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AuctionDataManagerError(ZA-MKT-0010，用法 Fail-Closed); InvalidAuctionTickError(ZA-MKT-0011，逐条校验)
# [TESTS] tests/market_data/test_auction_data_manager.py
# [A_module] module_id=MOD-MKT-007 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-DATA-32 A股集合竞价数据管理器（B10-02234 canonical + B13-04251 归并 → MOD-MKT-007）。

数据管理面（与信号分析面 MOD-SIG-089 正交）：

1. **竞价时段判定**：开盘集合竞价 09:15-09:25（逐 3 秒快照节奏声明）+
   收盘集合竞价 14:57-15:00；session_of(ts) 边界含端点。
2. **采集编排**：fetcher 注入（miniQMT/通达信/tushare/akshare 源无关 callable）
   → 逐条字段校验（竞价量价/虚拟撮合价量：价>0、量≥0、撤单≤申报、PIT 当日、
   session 窗口匹配）→ 规范化 AuctionSnapshotRecord → 批内 (symbol,ts) 去重
   保首条 → sink 委托落账（CH auction_snapshot / Parquet 写入 callable）。
   fetcher/sink 异常 → status 留痕不抛（调度不炸）。
3. **命中率回放供数**：loader 注入读库存 → 轻校验 + PIT 过滤 + (symbol,ts)
   排序去重 → 供 MOD-PLAN-015（命中回放）与 MOD-SIG-089（微结构分析，要求
   同标的 ts 严格递增）消费。

不做什么：不做行为分类/方向预测（MOD-SIG-089 职责）、不做命中判定
（MOD-PLAN-015 职责）、不直连行情源/DB（fetcher/loader/sink 全注入）、
不重复 miniqmt_provider 原始采集函数（本模块为其上的校验/编排/供数管理面）。

依据: D-DATA-32 §30.3.1（B10-02234）+ A3数据架构 §17.1（B13-04251）；
construction_backlog_dig.tsv 双 D-DATA-32 撞名裁定。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final, Iterable, Mapping, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

__all__: Final = [
    "OPEN_SNAPSHOT_CADENCE_SEC",
    "SESSION_WINDOWS",
    "AuctionDataManager",
    "AuctionDataManagerError",
    "AuctionSession",
    "AuctionSnapshotRecord",
    "CollectReport",
    "InvalidAuctionTickError",
    "ReplayReport",
    "TickRejection",
    "session_of",
    "validate_tick",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class AuctionDataManagerError(ZephyrBaseError):
    """管理器用法非法（占位错误码，纪律⑦留对账批）。"""

    error_code = "ZA-MKT-0010"


class InvalidAuctionTickError(ZephyrBaseError):
    """单条竞价快照校验失败（占位错误码，纪律⑦留对账批）。"""

    error_code = "ZA-MKT-0011"


# ──────────────────────────────────────────────────────────────────────────────
# 竞价时段
# ──────────────────────────────────────────────────────────────────────────────


class AuctionSession(str, Enum):
    """竞价时段（封闭集）。"""

    OPEN_CALL = "open_call"  # 开盘集合竞价 09:15-09:25
    CLOSE_CALL = "close_call"  # 收盘集合竞价 14:57-15:00


#: 时段窗口（HH:MM 含端点）
SESSION_WINDOWS: Final[Mapping[AuctionSession, tuple[str, str]]] = {
    AuctionSession.OPEN_CALL: ("09:15", "09:25"),
    AuctionSession.CLOSE_CALL: ("14:57", "15:00"),
}

#: 开盘竞价快照节奏（逐 3 秒，B13-04251 spec 声明）
OPEN_SNAPSHOT_CADENCE_SEC: Final = 3


def _hhmm_to_time(hhmm: str) -> datetime.time:
    hh, mm = hhmm.split(":")
    return datetime.time(int(hh), int(mm))


def session_of(ts: datetime.datetime) -> AuctionSession | None:
    """判定时间戳所属竞价时段（含端点），窗口外返回 None。"""
    t = ts.time()
    for session, (start, end) in SESSION_WINDOWS.items():
        if _hhmm_to_time(start) <= t <= _hhmm_to_time(end):
            return session
    return None


# ──────────────────────────────────────────────────────────────────────────────
# 快照记录（规范化产物）
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class AuctionSnapshotRecord:
    """单时点竞价快照规范化记录（placed/canceled 为当日累计口径）。

    字段名对齐 MOD-SIG-089 AuctionSnapshot（indicative_price/indicative_volume/
    buy1_volume/placed_volume/canceled_volume），接线零映射成本。
    """

    symbol: str
    trade_date: datetime.date
    ts: datetime.datetime
    session: AuctionSession
    indicative_price: float  # 虚拟撮合价
    indicative_volume: float  # 虚拟撮合量（累计）
    auction_amount: float = 0.0  # 竞价成交额
    buy1_volume: float | None = None  # 买一档封单量
    placed_volume: float | None = None  # 累计申报量
    canceled_volume: float | None = None  # 累计撤单量
    data_source: str = ""
    quality_flag: int = 1  # 1=正常 0=异常（对齐 CH auction_snapshot 列口径）

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise InvalidAuctionTickError(f"symbol 非法: {self.symbol!r}")
        if not isinstance(self.indicative_price, (int, float)) or self.indicative_price <= 0:
            raise InvalidAuctionTickError(f"indicative_price 须>0: {self.indicative_price!r}")
        for name in ("indicative_volume", "auction_amount"):
            v = getattr(self, name)
            if not isinstance(v, (int, float)) or v < 0:
                raise InvalidAuctionTickError(f"{name} 须≥0: {v!r}")
        for name in ("buy1_volume", "placed_volume", "canceled_volume"):
            v = getattr(self, name)
            if v is not None and (not isinstance(v, (int, float)) or v < 0):
                raise InvalidAuctionTickError(f"{name} 须≥0: {v!r}")
        if (
            self.placed_volume is not None
            and self.canceled_volume is not None
            and self.canceled_volume > self.placed_volume
        ):
            raise InvalidAuctionTickError(
                f"撤单量({self.canceled_volume}) 不得大于申报量({self.placed_volume})"
            )
        if self.quality_flag not in (0, 1):
            raise InvalidAuctionTickError(f"quality_flag 须∈(0,1): {self.quality_flag!r}")
        if not isinstance(self.ts, datetime.datetime):
            raise InvalidAuctionTickError(f"ts 须为 datetime: {type(self.ts).__name__}")
        if self.ts.date() != self.trade_date:
            raise InvalidAuctionTickError(
                f"PIT违规: ts 日期 {self.ts.date()} != trade_date {self.trade_date}"
            )
        if session_of(self.ts) != self.session:
            raise InvalidAuctionTickError(
                f"ts {self.ts.time()} 不在声明时段 {self.session.value} 窗口内"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 报告
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TickRejection:
    """逐条拒收留痕。"""

    index: int
    reason: str


@dataclass(frozen=True)
class CollectReport:
    """采集编排报告。"""

    trade_date: datetime.date
    session: AuctionSession
    fetched: int = 0
    accepted: int = 0
    rejected: int = 0
    duplicates: int = 0
    persisted: int = 0
    status: str = "ok"  # ok | empty | all_rejected | fetch_error | sink_error
    rejections: tuple[TickRejection, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReplayReport:
    """回放供数报告（records 按 (symbol,ts) 排序，同标的 ts 严格递增）。"""

    trade_date: datetime.date
    records: tuple[AuctionSnapshotRecord, ...] = ()
    skipped: int = 0
    notes: tuple[str, ...] = ()


# ──────────────────────────────────────────────────────────────────────────────
# tick 规范化
# ──────────────────────────────────────────────────────────────────────────────

_REQUIRED_KEYS: Final = ("symbol", "ts", "indicative_price", "indicative_volume")
_OPTIONAL_NUMERIC: Final = ("auction_amount", "buy1_volume", "placed_volume", "canceled_volume")


def _parse_ts(raw: Any) -> datetime.datetime:
    if isinstance(raw, datetime.datetime):
        return raw
    if isinstance(raw, str):
        text = raw.strip()
        try:
            return datetime.datetime.fromisoformat(text)
        except ValueError:
            pass
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.datetime.strptime(text, fmt)
            except ValueError:
                continue
    raise InvalidAuctionTickError(f"ts 非法: {raw!r}")


def _to_number(name: str, raw: Any) -> float:
    if isinstance(raw, bool):
        raise InvalidAuctionTickError(f"{name} 不得为 bool: {raw!r}")
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        try:
            return float(raw.strip())
        except ValueError as exc:
            raise InvalidAuctionTickError(f"{name} 数值非法: {raw!r}") from exc
    raise InvalidAuctionTickError(f"{name} 类型非法: {type(raw).__name__}")


def validate_tick(
    raw: Mapping[str, Any],
    *,
    trade_date: datetime.date,
    session: AuctionSession | None,
    data_source: str = "",
) -> AuctionSnapshotRecord:
    """把原始 tick 规范化为 AuctionSnapshotRecord（Fail-Closed）。

    Args:
        raw: 原始 tick（fetcher/loader 产出的 Mapping）。
        trade_date: 交易日（PIT 校验基准）。
        session: 声明时段；None 时按 ts 推导（回放路径），窗口外拒收。
        data_source: 数据源标记（miniQMT/通达信/tushare/akshare...）。

    Raises:
        InvalidAuctionTickError: 缺必填键/类型非法/取值域越界/PIT/session 不匹配。
    """
    if not isinstance(raw, Mapping):
        raise InvalidAuctionTickError(f"tick 须为 Mapping: {type(raw).__name__}")
    for key in _REQUIRED_KEYS:
        if key not in raw:
            raise InvalidAuctionTickError(f"缺必填键: {key}")
    ts = _parse_ts(raw["ts"])
    actual_session = session if session is not None else session_of(ts)
    if actual_session is None:
        raise InvalidAuctionTickError(f"ts {ts.time()} 不在任何竞价时段窗口内")
    kwargs: dict[str, Any] = {
        "symbol": raw["symbol"],
        "trade_date": trade_date,
        "ts": ts,
        "session": actual_session,
        "indicative_price": _to_number("indicative_price", raw["indicative_price"]),
        "indicative_volume": _to_number("indicative_volume", raw["indicative_volume"]),
        "data_source": data_source or str(raw.get("data_source", "")),
    }
    for name in _OPTIONAL_NUMERIC:
        if name in raw and raw[name] is not None:
            kwargs[name] = _to_number(name, raw[name])
    if "quality_flag" in raw and raw["quality_flag"] is not None:
        qf = raw["quality_flag"]
        if not isinstance(qf, int) or isinstance(qf, bool):
            raise InvalidAuctionTickError(f"quality_flag 类型非法: {qf!r}")
        kwargs["quality_flag"] = qf
    return AuctionSnapshotRecord(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 数据管理器
# ──────────────────────────────────────────────────────────────────────────────


class AuctionDataManager:
    """A股集合竞价数据管理器（采集编排 + 回放供数，三面全注入无 IO）。"""

    # ── 采集编排 ──────────────────────────────────────────────────────

    def collect_session(
        self,
        *,
        trade_date: datetime.date,
        session: AuctionSession,
        fetcher: Callable[..., Iterable[Mapping[str, Any]]],
        sink: Callable[[tuple[AuctionSnapshotRecord, ...]], Any],
        data_source: str = "",
    ) -> CollectReport:
        """竞价时段采集编排：fetcher → 校验规范化 → 去重 → sink 落账。

        Args:
            trade_date: 交易日。
            session: 采集时段。
            fetcher: ``fetcher(trade_date=..., session=...) -> Iterable[Mapping]``。
            sink: ``sink(records) -> None``（CH/Parquet 写入委托）。
            data_source: 数据源标记。

        Returns:
            CollectReport（fetcher/sink 异常 → status 留痕不抛）。

        Raises:
            AuctionDataManagerError: 用法非法（fetcher/sink 不可调用、trade_date 非 date）。
        """
        if not isinstance(trade_date, datetime.date):
            raise AuctionDataManagerError(f"trade_date 须为 date: {type(trade_date).__name__}")
        if not isinstance(session, AuctionSession):
            raise AuctionDataManagerError(f"session 须为 AuctionSession: {session!r}")
        if not callable(fetcher):
            raise AuctionDataManagerError("fetcher 必须为可调用对象")
        if not callable(sink):
            raise AuctionDataManagerError("sink 必须为可调用对象")

        try:
            raw_ticks = list(fetcher(trade_date=trade_date, session=session))
        except Exception as exc:  # noqa: BLE001
            logger.warning("竞价采集 fetcher 异常（不炸调度）: %s", exc, exc_info=True)
            return CollectReport(
                trade_date=trade_date,
                session=session,
                status="fetch_error",
                notes=(f"fetch_error: {exc}",),
            )

        if not raw_ticks:
            return CollectReport(trade_date=trade_date, session=session, status="empty")

        records: list[AuctionSnapshotRecord] = []
        rejections: list[TickRejection] = []
        seen: set[tuple[str, datetime.datetime]] = set()
        duplicates = 0
        for idx, raw in enumerate(raw_ticks):
            try:
                rec = validate_tick(raw, trade_date=trade_date, session=session, data_source=data_source)
            except InvalidAuctionTickError as exc:
                rejections.append(TickRejection(index=idx, reason=str(exc)))
                continue
            key = (rec.symbol, rec.ts)
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            records.append(rec)

        if not records:
            return CollectReport(
                trade_date=trade_date,
                session=session,
                fetched=len(raw_ticks),
                rejected=len(rejections),
                duplicates=duplicates,
                status="all_rejected",
                rejections=tuple(rejections),
            )

        batch = tuple(records)
        try:
            sink(batch)
        except Exception as exc:  # noqa: BLE001
            logger.warning("竞价落账 sink 异常（不炸调度）: %s", exc, exc_info=True)
            return CollectReport(
                trade_date=trade_date,
                session=session,
                fetched=len(raw_ticks),
                accepted=len(records),
                rejected=len(rejections),
                duplicates=duplicates,
                persisted=0,
                status="sink_error",
                rejections=tuple(rejections),
                notes=(f"sink_error: {exc}",),
            )

        return CollectReport(
            trade_date=trade_date,
            session=session,
            fetched=len(raw_ticks),
            accepted=len(records),
            rejected=len(rejections),
            duplicates=duplicates,
            persisted=len(records),
            status="ok",
            rejections=tuple(rejections),
        )

    # ── 回放供数 ──────────────────────────────────────────────────────

    def replay(
        self,
        *,
        trade_date: datetime.date,
        loader: Callable[..., Iterable[Any]],
        symbols: Sequence[str] | None = None,
        session: AuctionSession | None = None,
    ) -> ReplayReport:
        """命中率回放供数：loader → 轻校验/PIT → 排序去重 → 供下游消费。

        Args:
            trade_date: 交易日。
            loader: ``loader(trade_date=..., symbols=...) -> Iterable[Mapping|AuctionSnapshotRecord]``。
            symbols: 标的过滤（透传 loader，并对产物二次过滤）。
            session: 时段过滤（None=全部）。

        Returns:
            ReplayReport（loader 异常 → notes 留痕不抛）。

        Raises:
            AuctionDataManagerError: 用法非法。
        """
        if not isinstance(trade_date, datetime.date):
            raise AuctionDataManagerError(f"trade_date 须为 date: {type(trade_date).__name__}")
        if not callable(loader):
            raise AuctionDataManagerError("loader 必须为可调用对象")

        try:
            raw_rows = list(loader(trade_date=trade_date, symbols=symbols))
        except Exception as exc:  # noqa: BLE001
            logger.warning("竞价回放 loader 异常（不炸调度）: %s", exc, exc_info=True)
            return ReplayReport(trade_date=trade_date, notes=(f"loader_error: {exc}",))

        notes: list[str] = []
        records: list[AuctionSnapshotRecord] = []
        skipped = 0
        dedup = 0
        seen: set[tuple[str, datetime.datetime]] = set()
        symbol_filter = tuple(symbols) if symbols else None
        for raw in raw_rows:
            rec: AuctionSnapshotRecord | None = None
            if isinstance(raw, AuctionSnapshotRecord):
                rec = raw
                if rec.trade_date != trade_date:
                    rec = None
            else:
                try:
                    rec = validate_tick(raw, trade_date=trade_date, session=None)
                except InvalidAuctionTickError:
                    rec = None
            if rec is None:
                skipped += 1
                continue
            if session is not None and rec.session != session:
                skipped += 1
                continue
            if symbol_filter is not None and rec.symbol not in symbol_filter:
                skipped += 1
                continue
            key = (rec.symbol, rec.ts)
            if key in seen:
                dedup += 1
                continue
            seen.add(key)
            records.append(rec)

        if skipped:
            notes.append(f"skipped {skipped} invalid/out-of-scope rows")
        if dedup:
            notes.append(f"dedup {dedup} duplicated (symbol,ts) rows")

        records.sort(key=lambda r: (r.symbol, r.ts))
        return ReplayReport(
            trade_date=trade_date,
            records=tuple(records),
            skipped=skipped,
            notes=tuple(notes),
        )
