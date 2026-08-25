# [BLUEPRINT] MOD-MKT-007 | docs/03_modules/_domain_mkt_data/auction_data_manager/blueprint.md | §test
# [A_test] module_id: MOD-MKT-007 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AuctionDataManager 单元测试 (MOD-MKT-007, MVP)。

覆盖: 竞价时段判定（开盘 09:15-09:25/收盘 14:57-15:00 边界）/ 快照记录
Fail-Closed 校验（价量/撤单≤申报/PIT/session 匹配）/ tick 规范化（类型
 coercion、缺键、坏值）/ 采集编排（fetcher/sink 注入、去重、拒收留痕、
fetch/sink 异常不炸）/ 回放供数（排序、去重、session 过滤、PIT、loader
异常不炸）/ 用法 Fail-Closed / frozen。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

from zephyr.market_data.auction_data_manager import (
    OPEN_SNAPSHOT_CADENCE_SEC,
    SESSION_WINDOWS,
    AuctionDataManager,
    AuctionDataManagerError,
    AuctionSession,
    AuctionSnapshotRecord,
    InvalidAuctionTickError,
    session_of,
    validate_tick,
)

_TD = datetime.date(2026, 8, 25)


def _dt(hhmmss: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(f"2026-08-25 {hhmmss}")


def _tick(**overrides) -> dict:
    base = {
        "symbol": "600519",
        "ts": _dt("09:15:03"),
        "indicative_price": 1700.0,
        "indicative_volume": 1000.0,
    }
    base.update(overrides)
    return base


def _record(**overrides) -> AuctionSnapshotRecord:
    base = {
        "symbol": "600519",
        "trade_date": _TD,
        "ts": _dt("09:15:03"),
        "session": AuctionSession.OPEN_CALL,
        "indicative_price": 1700.0,
        "indicative_volume": 1000.0,
    }
    base.update(overrides)
    return AuctionSnapshotRecord(**base)


# ── 竞价时段判定 ──────────────────────────────────────────────────────────


class TestSessionWindows:
    def test_windows_declared(self) -> None:
        assert SESSION_WINDOWS[AuctionSession.OPEN_CALL] == ("09:15", "09:25")
        assert SESSION_WINDOWS[AuctionSession.CLOSE_CALL] == ("14:57", "15:00")
        assert OPEN_SNAPSHOT_CADENCE_SEC == 3

    @pytest.mark.parametrize(
        ("hhmmss", "expected"),
        [
            ("09:14:59", None),
            ("09:15:00", AuctionSession.OPEN_CALL),
            ("09:20:00", AuctionSession.OPEN_CALL),
            ("09:25:00", AuctionSession.OPEN_CALL),
            ("09:25:01", None),
            ("10:00:00", None),
            ("14:56:59", None),
            ("14:57:00", AuctionSession.CLOSE_CALL),
            ("15:00:00", AuctionSession.CLOSE_CALL),
            ("15:00:01", None),
        ],
    )
    def test_session_of_boundaries(self, hhmmss: str, expected) -> None:
        assert session_of(_dt(hhmmss)) == expected


# ── 快照记录校验（Fail-Closed） ───────────────────────────────────────────


class TestRecordValidation:
    def test_valid_record(self) -> None:
        rec = _record()
        assert rec.quality_flag == 1
        assert rec.auction_amount == 0.0
        assert rec.buy1_volume is None

    def test_price_must_be_positive(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            _record(indicative_price=0.0)

    def test_volume_must_be_non_negative(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            _record(indicative_volume=-1.0)

    def test_amount_must_be_non_negative(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            _record(auction_amount=-0.01)

    def test_canceled_not_above_placed(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            _record(placed_volume=100.0, canceled_volume=101.0)

    def test_canceled_equal_placed_ok(self) -> None:
        rec = _record(placed_volume=100.0, canceled_volume=100.0)
        assert rec.canceled_volume == 100.0

    def test_quality_flag_domain(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            _record(quality_flag=2)

    def test_symbol_non_empty(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            _record(symbol="")

    def test_pit_trade_date_match(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            _record(trade_date=datetime.date(2026, 8, 24))

    def test_session_match(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            _record(session=AuctionSession.CLOSE_CALL)  # ts 在开盘窗口

    def test_record_frozen(self) -> None:
        rec = _record()
        with pytest.raises(dataclasses.FrozenInstanceError):
            rec.quality_flag = 0  # type: ignore[misc]


# ── tick 规范化 ───────────────────────────────────────────────────────────


class TestValidateTick:
    def test_full_tick(self) -> None:
        rec = validate_tick(_tick(), trade_date=_TD, session=AuctionSession.OPEN_CALL, data_source="miniQMT")
        assert rec.symbol == "600519"
        assert rec.session == AuctionSession.OPEN_CALL
        assert rec.data_source == "miniQMT"
        assert rec.quality_flag == 1

    def test_missing_required_key(self) -> None:
        tick = _tick()
        del tick["indicative_price"]
        with pytest.raises(InvalidAuctionTickError):
            validate_tick(tick, trade_date=_TD, session=AuctionSession.OPEN_CALL)

    def test_ts_iso_str_parsed(self) -> None:
        rec = validate_tick(_tick(ts="2026-08-25 09:15:03"), trade_date=_TD, session=AuctionSession.OPEN_CALL)
        assert rec.ts == _dt("09:15:03")

    def test_ts_bad_str(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            validate_tick(_tick(ts="not-a-time"), trade_date=_TD, session=AuctionSession.OPEN_CALL)

    def test_numeric_str_parsed(self) -> None:
        rec = validate_tick(_tick(indicative_price="1700.5"), trade_date=_TD, session=AuctionSession.OPEN_CALL)
        assert rec.indicative_price == 1700.5

    def test_bool_numeric_rejected(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            validate_tick(_tick(indicative_price=True), trade_date=_TD, session=AuctionSession.OPEN_CALL)

    def test_out_of_window_rejected(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            validate_tick(_tick(ts=_dt("10:00:00")), trade_date=_TD, session=AuctionSession.OPEN_CALL)

    def test_wrong_date_rejected(self) -> None:
        with pytest.raises(InvalidAuctionTickError):
            validate_tick(_tick(ts=_dt("09:15:03").replace(day=24)), trade_date=_TD, session=AuctionSession.OPEN_CALL)

    def test_optional_fields_default(self) -> None:
        rec = validate_tick(_tick(), trade_date=_TD, session=AuctionSession.OPEN_CALL)
        assert rec.buy1_volume is None
        assert rec.placed_volume is None
        assert rec.canceled_volume is None
        assert rec.auction_amount == 0.0


# ── 采集编排 ──────────────────────────────────────────────────────────────


class TestCollectSession:
    def test_happy_path(self) -> None:
        ticks = [_tick(), _tick(ts=_dt("09:15:06")), _tick(ts=_dt("09:15:09"), symbol="000001")]
        sink_seen: list[tuple] = []
        report = AuctionDataManager().collect_session(
            trade_date=_TD,
            session=AuctionSession.OPEN_CALL,
            fetcher=lambda **_: ticks,
            sink=lambda records: sink_seen.append(records),
            data_source="miniQMT",
        )
        assert report.status == "ok"
        assert report.fetched == 3
        assert report.accepted == 3
        assert report.persisted == 3
        assert report.rejected == 0
        assert len(sink_seen) == 1
        assert len(sink_seen[0]) == 3
        assert all(r.data_source == "miniQMT" for r in sink_seen[0])

    def test_dedup_same_symbol_ts(self) -> None:
        ticks = [_tick(), _tick()]  # 同 (symbol, ts)
        sink_seen: list[tuple] = []
        report = AuctionDataManager().collect_session(
            trade_date=_TD,
            session=AuctionSession.OPEN_CALL,
            fetcher=lambda **_: ticks,
            sink=lambda records: sink_seen.append(records),
        )
        assert report.duplicates == 1
        assert report.persisted == 1
        assert len(sink_seen[0]) == 1

    def test_invalid_tick_rejected_with_reason(self) -> None:
        ticks = [_tick(), _tick(indicative_price=-1.0)]
        report = AuctionDataManager().collect_session(
            trade_date=_TD,
            session=AuctionSession.OPEN_CALL,
            fetcher=lambda **_: ticks,
            sink=lambda records: None,
        )
        assert report.accepted == 1
        assert report.rejected == 1
        assert len(report.rejections) == 1
        assert report.rejections[0].index == 1
        assert report.rejections[0].reason

    def test_fetcher_exception_not_raising(self) -> None:
        def _boom(**_kwargs):
            raise ConnectionError("xtdata down")

        report = AuctionDataManager().collect_session(
            trade_date=_TD,
            session=AuctionSession.OPEN_CALL,
            fetcher=_boom,
            sink=lambda records: None,
        )
        assert report.status == "fetch_error"
        assert report.persisted == 0
        assert report.notes
        assert "xtdata down" in report.notes[0]

    def test_sink_exception_not_raising(self) -> None:
        def _sink_boom(_records):
            raise RuntimeError("ch write fail")

        report = AuctionDataManager().collect_session(
            trade_date=_TD,
            session=AuctionSession.OPEN_CALL,
            fetcher=lambda **_: [_tick()],
            sink=_sink_boom,
        )
        assert report.status == "sink_error"
        assert report.accepted == 1
        assert report.persisted == 0

    def test_empty_fetch_skips_sink(self) -> None:
        sink_seen: list[tuple] = []
        report = AuctionDataManager().collect_session(
            trade_date=_TD,
            session=AuctionSession.OPEN_CALL,
            fetcher=lambda **_: [],
            sink=lambda records: sink_seen.append(records),
        )
        assert report.status == "empty"
        assert report.persisted == 0
        assert sink_seen == []

    def test_all_rejected_skips_sink(self) -> None:
        sink_seen: list[tuple] = []
        report = AuctionDataManager().collect_session(
            trade_date=_TD,
            session=AuctionSession.OPEN_CALL,
            fetcher=lambda **_: [_tick(indicative_price=-1.0)],
            sink=lambda records: sink_seen.append(records),
        )
        assert report.status == "all_rejected"
        assert sink_seen == []

    def test_non_callable_fetcher_fail_closed(self) -> None:
        with pytest.raises(AuctionDataManagerError):
            AuctionDataManager().collect_session(
                trade_date=_TD,
                session=AuctionSession.OPEN_CALL,
                fetcher="not-callable",  # type: ignore[arg-type]
                sink=lambda records: None,
            )

    def test_non_callable_sink_fail_closed(self) -> None:
        with pytest.raises(AuctionDataManagerError):
            AuctionDataManager().collect_session(
                trade_date=_TD,
                session=AuctionSession.OPEN_CALL,
                fetcher=lambda **_: [],
                sink=None,  # type: ignore[arg-type]
            )

    def test_bad_trade_date_fail_closed(self) -> None:
        with pytest.raises(AuctionDataManagerError):
            AuctionDataManager().collect_session(
                trade_date="2026-08-25",  # type: ignore[arg-type]
                session=AuctionSession.OPEN_CALL,
                fetcher=lambda **_: [],
                sink=lambda records: None,
            )


# ── 回放供数 ──────────────────────────────────────────────────────────────


class TestReplay:
    def test_sorted_by_symbol_ts(self) -> None:
        rows = [
            _tick(symbol="000001", ts=_dt("09:15:09")),
            _tick(symbol="600519", ts=_dt("09:15:09")),
            _tick(symbol="600519", ts=_dt("09:15:03")),
        ]
        report = AuctionDataManager().replay(
            trade_date=_TD,
            loader=lambda **_: rows,
        )
        assert len(report.records) == 3
        keys = [(r.symbol, r.ts) for r in report.records]
        assert keys == sorted(keys)
        # 同标的 ts 严格递增（MOD-SIG-089 消费前置条件）
        ts_600519 = [r.ts for r in report.records if r.symbol == "600519"]
        assert ts_600519 == sorted(ts_600519)

    def test_record_passthrough(self) -> None:
        rec = _record()
        report = AuctionDataManager().replay(trade_date=_TD, loader=lambda **_: [rec])
        assert report.records == (rec,)
        assert report.skipped == 0

    def test_dedup_keep_first(self) -> None:
        rows = [_tick(), _tick(indicative_price=1699.0)]
        report = AuctionDataManager().replay(trade_date=_TD, loader=lambda **_: rows)
        assert len(report.records) == 1
        assert report.records[0].indicative_price == 1700.0
        assert any("dedup" in n for n in report.notes)

    def test_invalid_row_skipped(self) -> None:
        rows = [_tick(), _tick(ts=_dt("10:00:00"))]  # 第二条窗口外
        report = AuctionDataManager().replay(trade_date=_TD, loader=lambda **_: rows)
        assert len(report.records) == 1
        assert report.skipped == 1
        assert any("skipped" in n for n in report.notes)

    def test_session_filter(self) -> None:
        rows = [_tick(ts=_dt("09:15:03")), _tick(ts=_dt("14:57:03"))]
        report = AuctionDataManager().replay(
            trade_date=_TD,
            loader=lambda **_: rows,
            session=AuctionSession.CLOSE_CALL,
        )
        assert len(report.records) == 1
        assert report.records[0].session == AuctionSession.CLOSE_CALL

    def test_derive_session_for_mapping(self) -> None:
        rows = [_tick(ts=_dt("14:57:03"))]
        report = AuctionDataManager().replay(trade_date=_TD, loader=lambda **_: rows)
        assert report.records[0].session == AuctionSession.CLOSE_CALL

    def test_loader_exception_not_raising(self) -> None:
        def _boom(**_kwargs):
            raise RuntimeError("ch read fail")

        report = AuctionDataManager().replay(trade_date=_TD, loader=_boom)
        assert report.records == ()
        assert any("loader_error" in n for n in report.notes)

    def test_non_callable_loader_fail_closed(self) -> None:
        with pytest.raises(AuctionDataManagerError):
            AuctionDataManager().replay(trade_date=_TD, loader=None)  # type: ignore[arg-type]

    def test_symbols_passed_to_loader(self) -> None:
        seen: dict = {}
        AuctionDataManager().replay(
            trade_date=_TD,
            loader=lambda **kw: seen.update(kw) or [],
            symbols=("600519",),
        )
        assert seen.get("symbols") == ("600519",)

    def test_report_frozen(self) -> None:
        report = AuctionDataManager().replay(trade_date=_TD, loader=lambda **_: [])
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.skipped = 1  # type: ignore[misc]
