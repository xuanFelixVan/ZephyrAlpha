# [TESTS] tests/signal_ashare/limit_up/test_event_axis.py
# [TTL] permanent
# 波10 G-B.3（MOD-SIG-146）事件轴显式层单测——纯函数零库依赖，tmp_path 不需要（无 IO）。

import math

import pytest

from zephyr.signal_ashare.limit_up.event_axis import (
    LimitUpEventType,
    classify_limit_up_event,
    derive_event_axis,
)


class TestClassify:
    def test_sealed_close_at_limit(self):
        # 收盘封住 → sealed（close==limit）
        assert classify_limit_up_event(10.0, 11.0, 10.0, 11.0, 11.0) is LimitUpEventType.SEALED

    def test_busted_open_at_limit_close_below(self):
        # 开盘即板被砸开、收盘未回封 → busted（broken 真子集，优先单列）
        assert classify_limit_up_event(11.0, 11.0, 10.2, 10.5, 11.0) is LimitUpEventType.BUSTED

    def test_broken_touch_limit_intraday_close_below(self):
        # 盘中触板、开盘未板、收盘未封 → broken
        assert classify_limit_up_event(10.5, 11.0, 10.3, 10.6, 11.0) is LimitUpEventType.BROKEN

    def test_no_touch_no_event(self):
        # 全天未触板 → None（不造事件）
        assert classify_limit_up_event(10.0, 10.5, 9.9, 10.2, 11.0) is None

    def test_eps_absorbs_float_noise_only(self):
        # eps=1e-6 吸收浮点表示误差：close 略低于 limit 但在容差带内仍判 sealed
        assert classify_limit_up_event(10.0, 11.0, 10.0, 10.999999, 11.0) is LimitUpEventType.SEALED
        # 超出容差带（口径性差距）不放宽：差 0.01 判 broken
        assert classify_limit_up_event(10.0, 11.0, 10.0, 10.99, 11.0) is LimitUpEventType.BROKEN

    def test_mutual_exclusivity_order(self):
        # 互斥单选：SEALED 优先——open/high/close 全在板上也只出 sealed
        assert classify_limit_up_event(11.0, 11.0, 11.0, 11.0, 11.0) is LimitUpEventType.SEALED

    def test_fail_closed_validation(self):
        with pytest.raises(ValueError):
            classify_limit_up_event(10.0, 9.0, 10.5, 10.2, 11.0)  # high<low
        with pytest.raises(ValueError):
            classify_limit_up_event(10.0, 11.0, 10.0, 11.0, -1.0)  # limit<=0
        with pytest.raises(ValueError):
            classify_limit_up_event(math.nan, 11.0, 10.0, 11.0, 11.0)  # 非有限值


class TestDeriveAxis:
    def _row(self, **kw):
        base = dict(
            symbol="000852",
            trade_date="2026-10-06",
            open=10.0,
            high=11.0,
            low=10.0,
            close=11.0,
            limit_price=11.0,
        )
        base.update(kw)
        return base

    def test_mixed_rows_counts(self):
        rows = [
            self._row(),  # sealed
            self._row(symbol="000001", open=11.0, close=10.5),  # busted
            self._row(symbol="600000", open=10.5, close=10.6),  # broken
            self._row(symbol="300001", high=10.8, close=10.2),  # 无事件
        ]
        report = derive_event_axis(rows)
        assert report.n_rows == 4
        assert len(report.events) == 3
        assert (report.n_sealed, report.n_busted, report.n_broken) == (1, 1, 1)
        assert [e.event_type for e in report.events] == ["sealed", "busted", "broken"]
        d = report.to_dict()
        assert d["n_rows"] == 4 and d["events"][0]["symbol"] == "000852"

    def test_object_rows_duck_typing(self):
        from types import SimpleNamespace

        rows = [SimpleNamespace(**self._row())]
        report = derive_event_axis(rows)
        assert report.n_sealed == 1

    def test_empty_rows(self):
        report = derive_event_axis([])
        assert report.n_rows == 0 and report.events == ()

    def test_fail_closed_missing_field(self):
        bad = self._row()
        del bad["limit_price"]
        with pytest.raises(ValueError, match="limit_price"):
            derive_event_axis([bad])

    def test_fail_closed_bad_date(self):
        with pytest.raises(ValueError):
            derive_event_axis([self._row(trade_date="2026/10/06")])

    def test_fail_closed_empty_symbol(self):
        with pytest.raises(ValueError):
            derive_event_axis([self._row(symbol="  ")])
