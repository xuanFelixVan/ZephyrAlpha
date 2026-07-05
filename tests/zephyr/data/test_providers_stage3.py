"""阶段3 5 个新 Provider 单测（MOD-L00-004 阶段3）。

测试内容：
- BaostockProvider：thread_local 登录 / index_constituent / trade_calendar
- TushareProvider：token 认证 / news_news_info
- TickFlowProvider：匿名 / us_daily_kline / us_index
- TDXProvider：bestip / industry_class / sector_kline
- RSSProvider：匿名 / news_data / robots.txt 检查

不依赖真实 SDK，用 patch.dict("sys.modules", ...) 注入 mock 模块。
"""
import datetime
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

from src.zephyr.data.provider_base import FetchPayload, FetchResult
from src.zephyr.data.policy_registry import SourcePolicy


def _install_mock_module(name: str, mock: MagicMock | None = None) -> MagicMock:
    """构造一个 mock 模块并返回（用 sys.modules 注入）。"""
    if mock is None:
        mock = MagicMock()
    return mock


# ============== BaostockProvider 测试 ==============

class TestBaostockProvider:
    """BaostockProvider 测试（thread_local 登录模型）。"""

    def _make_provider(self):
        from src.zephyr.data.implementations.baostock_provider import BaostockProvider
        return BaostockProvider()

    def _make_bs_mock(self, login_ok=True):
        """构造 baostock mock 模块。"""
        bs = MagicMock()
        bs.login.return_value = MagicMock(
            error_code="0" if login_ok else "1",
            error_msg="" if login_ok else "login failed",
        )
        return bs

    def test_source_name(self):
        p = self._make_provider()
        assert p.source_name == "baostock"
        assert p.meta.thread_safety == "thread_local"

    def test_connect(self):
        """connect 为当前线程登录。"""
        bs = self._make_bs_mock(login_ok=True)
        with patch.dict("sys.modules", {"baostock": bs}):
            p = self._make_provider()
            p.connect()
            assert p.is_connected is True
            assert p._tls.logged_in is True
            bs.login.assert_called_once()

    def test_connect_login_failure(self):
        """login 失败抛 RuntimeError。"""
        bs = self._make_bs_mock(login_ok=False)
        with patch.dict("sys.modules", {"baostock": bs}):
            p = self._make_provider()
            with pytest.raises(RuntimeError, match="login failed"):
                p.connect()

    def test_disconnect(self):
        """disconnect 登出当前线程。"""
        bs = self._make_bs_mock(login_ok=True)
        with patch.dict("sys.modules", {"baostock": bs}):
            p = self._make_provider()
            p.connect()
            p.disconnect()
            assert p.is_connected is False
            assert p._tls.logged_in is False
            bs.logout.assert_called_once()

    def test_health_check_success(self):
        bs = self._make_bs_mock(login_ok=True)
        with patch.dict("sys.modules", {"baostock": bs}):
            p = self._make_provider()
            assert p.health_check() is True

    def test_health_check_no_sdk(self):
        """baostock 未安装时 health_check 返回 False。"""
        # 临时移除 sys.modules 中的 baostock，并让 import 抛 ImportError
        with patch.dict("sys.modules", {"baostock": None}):
            p = self._make_provider()
            assert p.health_check() is False

    def test_fetch_index_constituent(self):
        """获取沪深300成分股。"""
        bs = self._make_bs_mock(login_ok=True)
        # mock query_hs300_stocks 返回的 ResultSet
        mock_rs = MagicMock()
        mock_rs.error_code = "0"
        mock_rs.next.side_effect = [True, True, False]
        mock_rs.get_row_data.side_effect = [
            ["2026-07-06", "sh.600000", "浦发银行", "0.5"],
            ["2026-07-06", "sh.600016", "民生银行", "0.3"],
        ]
        bs.query_hs300_stocks.return_value = mock_rs

        with patch.dict("sys.modules", {"baostock": bs}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.index_constituent",
                symbols=None,
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 6),
                extra={"capability": "index_constituent"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].rows) == 2
            assert results[0].rows[0][1] == "sh.600000"

    def test_fetch_trade_calendar(self):
        """获取交易日历。"""
        bs = self._make_bs_mock(login_ok=True)
        mock_rs = MagicMock()
        mock_rs.error_code = "0"
        mock_rs.next.side_effect = [True, False]
        # baostock query_trade_date 返回: [product, calendar_date, is_trading_day]
        mock_rs.get_row_data.side_effect = [
            ["product", "2026-07-05", "1"],
        ]
        bs.query_trade_date.return_value = mock_rs

        with patch.dict("sys.modules", {"baostock": bs}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.trade_calendar",
                symbols=None,
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 6),
                extra={"capability": "trade_calendar"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert len(results[0].rows) == 1
            assert results[0].rows[0] == ("2026-07-05", 1)

    def test_fetch_unsupported_capability(self):
        bs = self._make_bs_mock(login_ok=True)
        with patch.dict("sys.modules", {"baostock": bs}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="t", symbols=None,
                start=datetime.date(2026, 1, 1), end=datetime.date(2026, 1, 2),
                extra={"capability": "unknown"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert "unsupported capability" in results[0].error


# ============== TushareProvider 测试 ==============

class TestTushareProvider:
    """TushareProvider 测试（token 认证）。"""

    def _make_provider(self):
        from src.zephyr.data.implementations.tushare_provider import TushareProvider
        return TushareProvider()

    def _make_ts_mock(self):
        ts = MagicMock()
        pro = MagicMock()
        ts.pro_api.return_value = pro
        return ts, pro

    def test_source_name(self):
        p = self._make_provider()
        assert p.source_name == "tushare"
        assert p.meta.auth_type == "token"

    def test_connect(self):
        """connect 读取 token 并初始化 pro_api。"""
        ts, pro = self._make_ts_mock()
        with patch.dict(os.environ, {"TUSHARE_TOKEN": "test_token"}), \
             patch.dict("sys.modules", {"tushare": ts}):
            p = self._make_provider()
            p.connect()
            assert p.is_connected is True
            ts.set_token.assert_called_once_with("test_token")
            ts.pro_api.assert_called_once()

    def test_connect_no_token(self):
        """token 缺失抛 RuntimeError。"""
        with patch.dict(os.environ, {}, clear=True):
            p = self._make_provider()
            with pytest.raises(RuntimeError, match="TUSHARE_TOKEN"):
                p.connect()

    def test_fetch_news_news_info(self):
        """获取新闻快讯。"""
        import pandas as pd
        ts, pro = self._make_ts_mock()
        mock_df = pd.DataFrame({
            "datetime": ["2026-07-05 10:00:00"],
            "news_id": ["n001"],
            "title": ["test news"],
            "content": ["content"],
            "src": ["sina"],
        })
        pro.news_info.return_value = mock_df

        with patch.dict(os.environ, {"TUSHARE_TOKEN": "test_token"}), \
             patch.dict("sys.modules", {"tushare": ts}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c3_fundamental.news_news_info",
                symbols=None,
                start=datetime.date(2026, 7, 5),
                end=datetime.date(2026, 7, 5),
                extra={"capability": "news_news_info"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].rows) == 1

    def test_fetch_unsupported(self):
        ts, pro = self._make_ts_mock()
        with patch.dict(os.environ, {"TUSHARE_TOKEN": "test_token"}), \
             patch.dict("sys.modules", {"tushare": ts}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="t", symbols=None,
                start=datetime.date(2026, 1, 1), end=datetime.date(2026, 1, 2),
                extra={"capability": "unknown"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert "unsupported" in results[0].error


# ============== TickFlowProvider 测试 ==============

class TestTickFlowProvider:
    """TickFlowProvider 测试（美股数据）。"""

    def _make_provider(self):
        from src.zephyr.data.implementations.tickflow_provider import TickFlowProvider
        return TickFlowProvider()

    def test_source_name(self):
        p = self._make_provider()
        assert p.source_name == "tickflow"
        assert p.meta.auth_type == "anonymous"

    def test_connect(self):
        tf = MagicMock()
        with patch.dict("sys.modules", {"tickflow": tf}):
            p = self._make_provider()
            p.connect()
            assert p.is_connected is True

    def test_health_check_success(self):
        tf = MagicMock()
        with patch.dict("sys.modules", {"tickflow": tf}):
            p = self._make_provider()
            assert p.health_check() is True

    def test_health_check_no_sdk(self):
        with patch.dict("sys.modules", {"tickflow": None}):
            p = self._make_provider()
            assert p.health_check() is False

    def test_fetch_us_daily_kline(self):
        """获取美股日K线。"""
        import pandas as pd
        tf = MagicMock()
        mock_df = pd.DataFrame({
            "date": ["2026-07-05"],
            "open": [150.0],
            "high": [155.0],
            "low": [149.0],
            "close": [153.0],
            "volume": [1000000],
        })
        tf.klines.get.return_value = mock_df

        with patch.dict("sys.modules", {"tickflow": tf}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.us_daily_kline",
                symbols=["AAPL.US"],
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 5),
                extra={"capability": "us_daily_kline"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].rows) == 1
            assert results[0].rows[0][1] == "AAPL.US"

    def test_fetch_us_index(self):
        """获取美股指数（ETF替代）。"""
        import pandas as pd
        tf = MagicMock()
        mock_df = pd.DataFrame({
            "date": ["2026-07-05"],
            "open": [400.0],
            "high": [405.0],
            "low": [399.0],
            "close": [403.0],
            "volume": [5000000],
        })
        tf.klines.get.return_value = mock_df

        with patch.dict("sys.modules", {"tickflow": tf}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.us_index",
                symbols=None,
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 5),
                extra={"capability": "us_index"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 3  # SPX/DJI/IXIC
            assert all(r.error is None for r in results)


# ============== TDXProvider 测试 ==============

class TestTDXProvider:
    """TDXProvider 测试（通达信板块数据）。"""

    def _make_provider(self):
        from src.zephyr.data.implementations.tdx_provider import TDXProvider
        return TDXProvider()

    def _make_mootdx_mock(self):
        """构造 mootdx 模块 mock。"""
        mootdx = MagicMock()
        mock_client = MagicMock()
        mootdx.quotes.Quotes.factory.return_value = mock_client
        return mootdx, mock_client

    def test_source_name(self):
        p = self._make_provider()
        assert p.source_name == "tdx"
        assert p.meta.thread_safety == "single_thread"

    def test_connect(self):
        mootdx, _ = self._make_mootdx_mock()
        # mootdx 需要子模块结构 mootdx.quotes.Quotes
        with patch.dict("sys.modules", {"mootdx": mootdx, "mootdx.quotes": mootdx.quotes}):
            p = self._make_provider()
            p.connect()
            assert p.is_connected is True
            mootdx.quotes.Quotes.factory.assert_called_once_with(market="std")

    def test_fetch_industry_class(self):
        """获取板块分类。"""
        mootdx, mock_client = self._make_mootdx_mock()
        # mootdx 返回格式：[(板块名, [(股票代码, 股票名称), ...]), ...]
        mock_client.get_stock_list_in_sector.return_value = [
            ("板块A", [("600000", "浦发银行"), ("600016", "民生银行")]),
        ]

        with patch.dict("sys.modules", {"mootdx": mootdx, "mootdx.quotes": mootdx.quotes}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c3_fundamental.industry_class",
                symbols=None,
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 6),
                extra={"capability": "industry_class"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].rows) == 2

    def test_fetch_sector_kline(self):
        """获取板块指数K线。"""
        mootdx, mock_client = self._make_mootdx_mock()
        mock_client.index_bars.return_value = [
            {"datetime": "2026-07-05", "open": 1000, "high": 1010,
             "low": 995, "close": 1005, "vol": 50000, "amount": 5000000},
        ]

        with patch.dict("sys.modules", {"mootdx": mootdx, "mootdx.quotes": mootdx.quotes}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.sector_kline",
                symbols=["sh.880001"],
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 6),
                extra={"capability": "sector_kline", "count": 10},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].rows) == 1


# ============== RSSProvider 测试 ==============

class TestRSSProvider:
    """RSSProvider 测试（财经新闻）。"""

    def _make_provider(self):
        from src.zephyr.data.implementations.rss_provider import RSSProvider
        return RSSProvider()

    def test_source_name(self):
        p = self._make_provider()
        assert p.source_name == "rss"
        assert p.meta.auth_type == "anonymous"

    def test_connect(self):
        fp = MagicMock()
        with patch.dict("sys.modules", {"feedparser": fp}):
            p = self._make_provider()
            p.connect()
            assert p.is_connected is True

    def test_health_check_success(self):
        fp = MagicMock()
        with patch.dict("sys.modules", {"feedparser": fp}):
            p = self._make_provider()
            assert p.health_check() is True

    def test_health_check_no_sdk(self):
        with patch.dict("sys.modules", {"feedparser": None}):
            p = self._make_provider()
            assert p.health_check() is False

    def test_fetch_news_data(self):
        """获取财经新闻。"""
        import pandas as pd  # noqa: F401  确保 pandas 可用
        # mock requests + feedparser
        requests_mock = MagicMock()
        mock_response = MagicMock()
        mock_response.content = b"<rss>...</rss>"
        mock_response.raise_for_status.return_value = None
        requests_mock.get.return_value = mock_response

        fp = MagicMock()
        mock_parsed = MagicMock()
        mock_parsed.entries = [
            {"published": "2026-07-05", "title": "news1",
             "link": "http://1", "summary": "sum1"},
        ]
        fp.parse.return_value = mock_parsed

        with patch.dict("sys.modules", {
            "feedparser": fp,
            "requests": requests_mock,
        }):
            p = self._make_provider()
            p.connect()
            # 禁用 robots.txt 检查
            policy = SourcePolicy(respect_robots_txt=False)
            payload = FetchPayload(
                table="c3_fundamental.news_data",
                symbols=["https://example.com/feed.xml"],
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 6),
                extra={"capability": "news_data"},
            )
            results = list(p.fetch(payload, policy))
            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].rows) == 1
            assert results[0].rows[0][1] == "news1"

    def test_fetch_unsupported(self):
        fp = MagicMock()
        with patch.dict("sys.modules", {"feedparser": fp}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="t", symbols=None,
                start=datetime.date(2026, 1, 1), end=datetime.date(2026, 1, 2),
                extra={"capability": "unknown"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert "unsupported" in results[0].error

    def test_robots_txt_cache(self):
        """robots.txt 缓存机制——fail-open（读取失败 → 允许）。"""
        from src.zephyr.data.implementations.rss_provider import RSSProvider
        p = self._make_provider()
        # 清空缓存
        RSSProvider._robots_cache.clear()
        # 测试 fail-open（robots.txt 读取失败 → 允许）
        with patch("urllib.robotparser.RobotFileParser.read", side_effect=Exception("net error")):
            assert p._is_allowed("https://example.com/feed.xml") is True
