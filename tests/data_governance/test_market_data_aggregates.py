# [BLUEPRINT] MOD-DATA_GOV-009 | docs/03_modules/_domain_data_governance/market_data_aggregates/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-009 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_governance.test_market_data_aggregates
# [TESTS] src/zephyr/data_governance/market_data_aggregates.py
"""MOD-DATA_GOV-009 单元测试：market_data_aggregates 行情聚合根与生命周期。

蓝图验收（B1-00648/CAND-DATGOV-006，C2 130~136）：
Bar/OHLCV/FinancialReport frozen 值对象 + 聚合根版本不变量（单调+1/乐观并发）
+ 仓储 get/save/snapshot 语义 + 保留归档策略协调表 + 恢复演练记录与逾期判定。
仓储/时钟全注入内存替身，不触网不触盘。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_governance.market_data_aggregates",
    reason="market_data_aggregates not importable",
)

from zephyr.data_governance.market_data_aggregates import (  # noqa: E402
    Bar,
    FinancialReport,
    InMemoryMarketDataRepository,
    Instrument,
    MarketData,
    MarketDataAggregateError,
    OHLCV,
    RecoveryDrillLog,
    RecoveryDrillRecord,
    RetentionPolicy,
    RetentionPolicyRegistry,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _bar(instrument: str = "600519.SH", ts: datetime.datetime = _T0) -> Bar:
    return Bar(
        instrument_id=instrument,
        ts=ts,
        ohlcv=OHLCV(open=1.0, high=2.0, low=0.5, close=1.5, volume=100.0),
    )


def _report(instrument: str = "600519.SH") -> FinancialReport:
    return FinancialReport(
        instrument_id=instrument,
        period="2026Q2",
        revenue=100.0,
        net_profit=30.0,
        published_at=_T0,
    )


def _policy(domain: str = "market", drill_days: int = 30) -> RetentionPolicy:
    return RetentionPolicy(domain=domain, ttl_days=90, archive_target="parquet_cold", drill_interval_days=drill_days)


# ──────────────────────────────────────────────────────────────────────────────
# 值对象 frozen
# ──────────────────────────────────────────────────────────────────────────────


class TestValueObjects:
    def test_ohlcv_frozen(self) -> None:
        o = OHLCV(open=1.0, high=2.0, low=0.5, close=1.5, volume=10.0)
        with pytest.raises(AttributeError):
            o.close = 9.9  # type: ignore[misc]

    def test_bar_frozen(self) -> None:
        b = _bar()
        with pytest.raises(AttributeError):
            b.instrument_id = "x"  # type: ignore[misc]

    def test_financial_report_frozen(self) -> None:
        r = _report()
        with pytest.raises(AttributeError):
            r.revenue = 0.0  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# 聚合根版本不变量
# ──────────────────────────────────────────────────────────────────────────────


class TestAggregates:
    def test_empty_instrument_id_raises(self) -> None:
        with pytest.raises(MarketDataAggregateError):
            MarketData("")

    def test_negative_version_raises(self) -> None:
        with pytest.raises(MarketDataAggregateError):
            MarketData("600519.SH", version=-1)

    def test_append_bar_bumps_version_and_immutable(self) -> None:
        agg = MarketData("600519.SH")
        agg2 = agg.append_bar(_bar())
        assert agg.version == 0 and agg.bars == ()
        assert agg2.version == 1 and len(agg2.bars) == 1

    def test_append_bar_wrong_instrument_raises(self) -> None:
        agg = MarketData("600519.SH")
        with pytest.raises(MarketDataAggregateError):
            agg.append_bar(_bar(instrument="000001.SZ"))

    def test_append_report_bumps_version(self) -> None:
        agg = MarketData("600519.SH").append_report(_report())
        assert agg.version == 1
        assert agg.reports[0].period == "2026Q2"

    def test_instrument_update_profile_bumps_version(self) -> None:
        ins = Instrument("600519.SH", symbol="贵州茅台", exchange="SSE")
        ins2 = ins.update_profile(symbol="贵州茅台", exchange="SSE")
        assert ins.version == 0
        assert ins2.version == 1

    def test_instrument_empty_fields_raise(self) -> None:
        with pytest.raises(MarketDataAggregateError):
            Instrument("600519.SH", symbol="", exchange="SSE")
        with pytest.raises(MarketDataAggregateError):
            Instrument("600519.SH", symbol="贵州茅台", exchange="")


# ──────────────────────────────────────────────────────────────────────────────
# 仓储协议（get/save/snapshot）
# ──────────────────────────────────────────────────────────────────────────────


class TestRepository:
    def test_save_get_roundtrip(self) -> None:
        repo = InMemoryMarketDataRepository()
        agg = MarketData("600519.SH").append_bar(_bar())
        repo.save(agg, expected_version=0)
        assert repo.get("600519.SH") is agg

    def test_get_unknown_returns_none(self) -> None:
        repo = InMemoryMarketDataRepository()
        assert repo.get("ghost") is None

    def test_get_empty_id_raises(self) -> None:
        repo = InMemoryMarketDataRepository()
        with pytest.raises(MarketDataAggregateError):
            repo.get("")

    def test_save_version_invariant_raises(self) -> None:
        repo = InMemoryMarketDataRepository()
        with pytest.raises(MarketDataAggregateError):  # 新建 expected_version 非 0
            repo.save(MarketData("600519.SH", version=2), expected_version=1)
        with pytest.raises(MarketDataAggregateError):  # version 跳号（非 +1）
            repo.save(MarketData("600519.SH", version=2), expected_version=0)

    def test_save_stale_expected_version_raises(self) -> None:
        repo = InMemoryMarketDataRepository()
        repo.save(MarketData("600519.SH", version=1), expected_version=0)
        with pytest.raises(MarketDataAggregateError):
            repo.save(MarketData("600519.SH", version=2), expected_version=0)  # 已存 v1

    def test_snapshot_deterministic_order(self) -> None:
        repo = InMemoryMarketDataRepository()
        repo.save(MarketData("b.SH", version=1), expected_version=0)
        repo.save(MarketData("a.SH", version=1), expected_version=0)
        assert list(repo.snapshot()) == ["a.SH", "b.SH"]


# ──────────────────────────────────────────────────────────────────────────────
# 保留归档策略协调表
# ──────────────────────────────────────────────────────────────────────────────


class TestRetentionPolicyRegistry:
    def test_register_and_get(self) -> None:
        reg = RetentionPolicyRegistry()
        reg.register(_policy())
        assert reg.get("market").ttl_days == 90

    def test_duplicate_domain_raises(self) -> None:
        reg = RetentionPolicyRegistry()
        reg.register(_policy())
        with pytest.raises(MarketDataAggregateError):
            reg.register(_policy())

    def test_invalid_policy_raises(self) -> None:
        reg = RetentionPolicyRegistry()
        with pytest.raises(MarketDataAggregateError):
            reg.register(RetentionPolicy("", 90, "parquet_cold", 30))
        with pytest.raises(MarketDataAggregateError):
            reg.register(RetentionPolicy("market", 0, "parquet_cold", 30))
        with pytest.raises(MarketDataAggregateError):
            reg.register(RetentionPolicy("market", 90, "", 30))
        with pytest.raises(MarketDataAggregateError):
            reg.register(RetentionPolicy("market", 90, "parquet_cold", 0))

    def test_unknown_domain_get_raises(self) -> None:
        reg = RetentionPolicyRegistry()
        with pytest.raises(MarketDataAggregateError):
            reg.get("ghost")

    def test_list_all_sorted(self) -> None:
        reg = RetentionPolicyRegistry()
        reg.register(_policy("signal"))
        reg.register(_policy("market"))
        assert [p.domain for p in reg.list_all()] == ["market", "signal"]


# ──────────────────────────────────────────────────────────────────────────────
# 恢复演练记录
# ──────────────────────────────────────────────────────────────────────────────


class TestRecoveryDrillLog:
    def _log(self, now: datetime.datetime = _T1) -> RecoveryDrillLog:
        reg = RetentionPolicyRegistry()
        reg.register(_policy("market", drill_days=30))
        reg.register(_policy("signal", drill_days=7))
        return RecoveryDrillLog(registry=reg, clock=lambda: now)

    def test_record_and_drills_for(self) -> None:
        log = self._log()
        r2 = RecoveryDrillRecord("d2", "market", _T0, _T0, True)
        r1 = RecoveryDrillRecord("d1", "market", _T0, _T0, True)
        log.record(r2)
        log.record(r1)
        assert [r.drill_id for r in log.drills_for("market")] == ["d1", "d2"]

    def test_record_unknown_domain_raises(self) -> None:
        log = self._log()
        with pytest.raises(MarketDataAggregateError):
            log.record(RecoveryDrillRecord("d1", "ghost", _T0, _T0, True))

    def test_record_invalid_raises(self) -> None:
        log = self._log()
        log.record(RecoveryDrillRecord("d1", "market", _T0, _T0, True))
        with pytest.raises(MarketDataAggregateError):  # drill_id 重复
            log.record(RecoveryDrillRecord("d1", "market", _T0, _T0, True))
        with pytest.raises(MarketDataAggregateError):  # 时间倒置
            log.record(RecoveryDrillRecord("d2", "market", _T1, _T0, True))

    def test_last_drill_none_when_empty(self) -> None:
        log = self._log()
        assert log.last_drill("market") is None

    def test_overdue_never_drilled(self) -> None:
        log = self._log()
        assert log.overdue_domains() == ("market", "signal")

    def test_overdue_fresh_drill_not_overdue(self) -> None:
        log = self._log(now=_T1)
        log.record(RecoveryDrillRecord("d1", "market", _T0, _T0 + datetime.timedelta(hours=1), True))
        log.record(RecoveryDrillRecord("d2", "signal", _T0, _T0 + datetime.timedelta(hours=1), True))
        assert log.overdue_domains() == ()

    def test_overdue_stale_drill(self) -> None:
        now = _T0 + datetime.timedelta(days=40)
        log = self._log(now=now)
        log.record(RecoveryDrillRecord("d1", "market", _T0, _T0, True))  # 40 天前 > 30
        log.record(RecoveryDrillRecord("d2", "signal", _T0, now - datetime.timedelta(days=1), True))
        assert log.overdue_domains() == ("market",)
