# [BLUEPRINT] MOD-AUTO-L1-004 | docs/_working/automation/campaign/blueprints/onboard_source_blueprint.md | §测试
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] tests.data.test_fx_ecb_provider
# [DOMAIN] D_DATA
# [INVARIANTS] 零网络零 CH——monkeypatch _http_get_json 直喷 fetch/游标契约（宪法 §9.6）
# [TTL] permanent
"""L1.1 正门 provider 测试：capability 路由、never-raise 契约、保守游标、路由-meta 一致性。"""
from __future__ import annotations

import datetime

import pytest

from zephyr.data.implementations.fx_ecb_provider import (
    FxEcbProvider,
    parse_series,
)
from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import FetchPayload

POLICY = SourcePolicy(rpm=0, max_retries=0)


def _payload(**extra) -> FetchPayload:
    return FetchPayload(
        table="c1_market.alt_fx_rate_ecb",
        symbols=None,
        start=datetime.date(2026, 9, 10),
        end=datetime.date(2026, 9, 17),
        incremental=True,
        extra={"capability": "fx_ecb_daily", **extra},
    )


def _resp(rates: dict) -> dict:
    return {"base": "USD", "rates": rates}


class TestParseSeries:
    def test_holiday_gap_skipped(self):
        payload = _resp({"2026-09-10": {"CNY": 7.1}, "2026-09-11": {}})
        rows = parse_series(payload, [("USD", "CNY")])
        assert rows == [("2026-09-10", "USD", "CNY", 7.1)]

    def test_empty_payload(self):
        assert parse_series({}, [("USD", "CNY")]) == []


class TestFetchContract:
    def test_unsupported_capability_yields_error_not_raise(self):
        p = FxEcbProvider()
        p.connect()
        results = list(p.fetch(_payload(capability="wrong"), POLICY))
        assert len(results) == 1
        assert results[0].error and "unsupported capability" in results[0].error

    def test_network_failure_never_raises(self, monkeypatch):
        p = FxEcbProvider()
        p.connect()

        def boom(url):
            raise ConnectionError("dns down")

        monkeypatch.setattr(p, "_http_get_json", boom)
        results = list(p.fetch(_payload(), POLICY))
        assert len(results) == 1
        assert results[0].error
        assert results[0].rows == []

    def test_rows_shape_matches_insert_columns(self, monkeypatch):
        p = FxEcbProvider()
        p.connect()
        monkeypatch.setattr(
            p, "_http_get_json",
            lambda url: _resp({"2026-09-16": {"CNY": 7.05, "JPY": 147.2}}),
        )
        results = list(p.fetch(_payload(pairs=[("USD", "CNY"), ("USD", "JPY")]), POLICY))
        assert results[0].error is None
        assert results[0].columns == ["trade_date", "base", "quote", "rate"]
        assert results[0].rows[0] == ("2026-09-16", "USD", "CNY", 7.05)
        assert results[0].last_key == "2026-09-16"

    def test_conservative_cursor_blocks_on_lagging_pair(self, monkeypatch):
        """任一对缺最新价→游标只推进到最迟对，下一班回查（防对级数据洞）。"""
        p = FxEcbProvider()
        p.connect()

        def by_url(url):
            if "base=USD" in url:
                return _resp({"2026-09-17": {"CNY": 7.0}})
            return _resp({"2026-09-15": {"CNY": 7.8}})  # EUR 滞后两天

        monkeypatch.setattr(p, "_http_get_json", by_url)
        results = list(p.fetch(_payload(), POLICY))
        assert results[0].error is None  # 部分缺价不得带 error（调度器见 error 即 break 丢行）
        assert results[0].last_key == "2026-09-15"

    def test_partial_base_failure_no_batch_loss(self, monkeypatch):
        p = FxEcbProvider()
        p.connect()

        def flaky(url):
            if "base=EUR" in url:
                raise TimeoutError("europe slow")
            return _resp({"2026-09-16": {"CNY": 7.0, "JPY": 147.0}})

        monkeypatch.setattr(p, "_http_get_json", flaky)
        results = list(p.fetch(_payload(), POLICY))
        assert results[0].error is None
        assert len(results[0].rows) > 0


class TestRouteMetaConsistency:
    def test_provider_file_passes_gate(self):
        """CAP-CONSISTENCY 同款机械校验：路由 capability 与 meta 声明一一对应。"""
        import inspect
        from pathlib import Path

        from zephyr.data.capability_validator import check_route_meta_consistency_content

        path = Path(inspect.getfile(FxEcbProvider))
        assert check_route_meta_consistency_content(path.read_text(encoding="utf-8")) == []

    def test_scheduler_routes_alt_fx_ecb(self):
        import inspect

        from zephyr.data.scheduler import IntegratorScheduler

        content = inspect.getsource(IntegratorScheduler.create_provider)
        assert 'source == "alt_fx_ecb"' in content


@pytest.mark.parametrize("days", [1, 7])
def test_collect_rows_empty_window_ok(days):
    p = FxEcbProvider()
    p.connect()
    p._http_get_json = lambda url: _resp({})
    rows, failed = p.collect_rows(
        datetime.date(2026, 9, 12), datetime.date(2026, 9, 13), policy=POLICY
    )
    assert rows == [] and failed == []
