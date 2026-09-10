# [DOMAIN] D_EX_SOR
# [TTL] permanent
"""MOD-XS-016 sell_session_router 单元测试（红蓝对抗：红-边界/红-契约/红-故障）。"""

from __future__ import annotations

import pytest

from zephyr.ex_sor.core.sell_session_router import (
    SessionRouterConfig,
    get_default_router_config,
    Exchange,
    SellRouteDecision,
    SellChannel,
    SellSessionRouterError,
    SessionRouterConfig,
    SessionWindow,
    RouteUrgency,
    classify_session,
    parse_hhmm,
    route_sell,
)


class TestParseHhmm:
    """红-边界：时刻解析的非法输入全拒。"""

    @pytest.mark.parametrize("bad", ["", "abc", "25:00", "12:60", "0915", None, "09-15"])
    def test_invalid_hhmm_rejected(self, bad):
        with pytest.raises(SellSessionRouterError):
            parse_hhmm(bad)

    def test_loose_single_digit_minute_accepted(self):
        # "9:5" 是无歧义合法时刻（09:05），宽松接受
        assert parse_hhmm("9:5") == 9 * 60 + 5

    def test_valid_boundaries(self):
        assert parse_hhmm("00:00") == 0
        assert parse_hhmm("23:59") == 24 * 60 - 1
        assert parse_hhmm("09:15") == 9 * 60 + 15


class TestClassifySession:
    """红-边界：全窗口边界分钟逐一钉死。"""

    @pytest.mark.parametrize("hhmm,expected", [
        ("09:14", SessionWindow.CLOSED),
        ("09:15", SessionWindow.OPENING_AUCTION),
        ("09:19", SessionWindow.OPENING_AUCTION),
        ("09:20", SessionWindow.OPENING_AUCTION),
        ("09:24", SessionWindow.OPENING_AUCTION),
        ("09:25", SessionWindow.PRE_OPEN_GAP),
        ("09:29", SessionWindow.PRE_OPEN_GAP),
        ("09:30", SessionWindow.MORNING_SESSION),
        ("11:29", SessionWindow.MORNING_SESSION),
        ("11:30", SessionWindow.LUNCH_BREAK),
        ("12:59", SessionWindow.LUNCH_BREAK),
        ("13:00", SessionWindow.AFTERNOON_SESSION),
        ("14:29", SessionWindow.AFTERNOON_SESSION),
        ("14:30", SessionWindow.DIVE_CAUTION),
        ("14:44", SessionWindow.DIVE_CAUTION),
        ("14:45", SessionWindow.DECISION_WINDOW),
        ("14:56", SessionWindow.DECISION_WINDOW),
        ("14:57", SessionWindow.CLOSING_AUCTION),
        ("14:59", SessionWindow.CLOSING_AUCTION),
        ("15:00", SessionWindow.CLOSED),
    ])
    def test_window_boundaries(self, hhmm, expected):
        assert classify_session(hhmm) is expected

    def test_unknown_exchange_rejected(self):
        with pytest.raises(SellSessionRouterError):
            classify_session("10:00", "NASDAQ")


class TestEscapeRouting:
    """ESCAPE 紧急度：竞价逃命 vs 急单市价。"""

    def test_escape_in_open_auction_routes_limit_down(self):
        d = route_sell("09:16", Exchange.SZ, RouteUrgency.ESCAPE)
        assert d.channel is SellChannel.ESCAPE_AUCTION_LIMIT_DOWN
        assert d.cancelable is True  # 9:15-9:20 可撤
        assert "跌停价" in d.note

    def test_escape_open_auction_no_cancel_after_0920(self):
        d = route_sell("09:21", Exchange.SZ, RouteUrgency.ESCAPE)
        assert d.channel is SellChannel.ESCAPE_AUCTION_LIMIT_DOWN
        assert d.cancelable is False  # 9:20-9:25 不可撤（A股通用规则）

    def test_escape_intraday_routes_market(self):
        d = route_sell("10:30", Exchange.SZ, RouteUrgency.ESCAPE)
        assert d.channel is SellChannel.MARKET_URGENT
        assert d.cancelable is False

    def test_escape_in_dive_caution(self):
        d = route_sell("14:35", Exchange.SH, RouteUrgency.ESCAPE)
        assert d.channel is SellChannel.MARKET_URGENT
        assert d.caution is True

    def test_escape_in_decision_window_market(self):
        d = route_sell("14:50", Exchange.SZ, RouteUrgency.ESCAPE, t0_closing_pending=True)
        # 逃命优先于做T收口
        assert d.channel is SellChannel.MARKET_URGENT

    def test_escape_in_close_auction_joins_auction(self):
        # 14:57 后只能进收盘集合竞价（市价通道不可用）
        d = route_sell("14:58", Exchange.SZ, RouteUrgency.ESCAPE)
        assert d.channel is SellChannel.CLOSING_AUCTION
        assert d.cancelable is False

    def test_escape_closed_no_route(self):
        d = route_sell("08:00", Exchange.SZ, RouteUrgency.ESCAPE)
        assert d.channel is SellChannel.NO_ROUTE
        assert d.cancelable is False


class TestNormalRouting:
    """NORMAL 紧急度：常规通道。"""

    def test_normal_morning(self):
        d = route_sell("10:00")
        assert d.channel is SellChannel.LIMIT_INTRADAY
        assert d.cancelable is True and d.caution is False

    def test_normal_dive_caution_flagged(self):
        d = route_sell("14:40")
        assert d.channel is SellChannel.LIMIT_CAUTIOUS
        assert d.caution is True

    def test_normal_decision_window_plain(self):
        d = route_sell("14:50")
        assert d.channel is SellChannel.LIMIT_INTRADAY
        assert "14:57" in d.note  # 深市要卖赶在 14:57 前挂

    def test_normal_decision_window_t0_closing(self):
        d = route_sell("14:50", t0_closing_pending=True)
        assert d.channel is SellChannel.T0_CLOSING
        assert d.cancelable is True

    def test_lunch_break_caution(self):
        d = route_sell("12:00")
        assert d.caution is True
        assert d.cancelable is True


class TestCloseAuctionExchangeSplit:
    """节点真源：深市 14:57 后集合竞价不可撤单；沪市尾盘可撤可改。"""

    def test_sz_close_auction_not_cancelable(self):
        d = route_sell("14:58", Exchange.SZ)
        assert d.window is SessionWindow.CLOSING_AUCTION
        assert d.cancelable is False
        assert "不可撤" in d.note

    def test_sh_close_auction_cancelable(self):
        d = route_sell("14:58", Exchange.SH)
        assert d.cancelable is True

    def test_config_override(self):
        cfg = SessionRouterConfig(sh_close_auction_cancelable=False)
        d = route_sell("14:58", Exchange.SH, config=cfg)
        assert d.cancelable is False


class TestFailClosed:
    """红-故障：非法输入 fail-closed；纯函数确定性。"""

    def test_unknown_urgency_rejected(self):
        with pytest.raises(SellSessionRouterError):
            route_sell("10:00", Exchange.SZ, "YOLO")

    def test_bad_hhmm_rejected(self):
        with pytest.raises(SellSessionRouterError):
            route_sell("noon")

    def test_determinism(self):
        assert route_sell("14:50", t0_closing_pending=True) == route_sell(
            "14:50", t0_closing_pending=True
        )

    def test_decision_frozen(self):
        d = route_sell("10:00")
        with pytest.raises(Exception):
            d.channel = SellChannel.NO_ROUTE

    def test_default_config_singleton_safe(self):
        assert get_default_router_config().sz_close_auction_cancelable is False
        assert isinstance(route_sell("10:00"), SellRouteDecision)
