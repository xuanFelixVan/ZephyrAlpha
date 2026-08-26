# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
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
from unittest.mock import MagicMock, patch

import pytest

from src.zephyr.data.policy_registry import SourcePolicy
from src.zephyr.data.provider_base import FetchPayload, FetchResult


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
            assert p.tls.logged_in is True
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
            assert p.tls.logged_in is False
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
            # #ARCH-DATA-015：列名对齐 CH schema（trade_date/index_code/symbol/weight/action/data_source），
            # symbol 转 canonical 大写格式（sh.600000 → 600000.SH）
            assert results[0].columns == ["trade_date", "index_code", "symbol", "weight", "action", "data_source"]
            assert results[0].rows[0] == ("2026-07-06", "000300.SH", "600000.SH", 0, "", "baostock")

    def test_fetch_trade_calendar(self):
        """获取交易日历。"""
        bs = self._make_bs_mock(login_ok=True)
        mock_rs = MagicMock()
        mock_rs.error_code = "0"
        mock_rs.next.side_effect = [True, False]
        # baostock query_trade_dates 返回: [calendar_date, is_trading_day]
        mock_rs.get_row_data.side_effect = [
            ["2026-07-05", "1"],
        ]
        bs.query_trade_dates.return_value = mock_rs

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
            # #ARCH-DATA-015：列名对齐 CH schema（exchange/cal_date/is_open/pretrade_date），
            # 首个开市日 pretrade_date=自身
            assert results[0].columns == ["exchange", "cal_date", "is_open", "pretrade_date"]
            assert results[0].rows[0] == ("SSE", "2026-07-05", 1, "2026-07-05")

    def test_fetch_unsupported_capability(self):
        bs = self._make_bs_mock(login_ok=True)
        with patch.dict("sys.modules", {"baostock": bs}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="t",
                symbols=None,
                start=datetime.date(2026, 1, 1),
                end=datetime.date(2026, 1, 2),
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
        with patch.dict(os.environ, {"TUSHARE_TOKEN": "test_token"}), patch.dict("sys.modules", {"tushare": ts}):
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
        mock_df = pd.DataFrame(
            {
                "datetime": ["2026-07-05 10:00:00"],
                "news_id": ["n001"],
                "title": ["test news"],
                "content": ["content"],
                "src": ["sina"],
            }
        )
        pro.news_info.return_value = mock_df

        with patch.dict(os.environ, {"TUSHARE_TOKEN": "test_token"}), patch.dict("sys.modules", {"tushare": ts}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c3_fundamental.news_news_info",
                symbols=None,
                start=datetime.date(2026, 7, 5),
                end=datetime.date(2026, 7, 5),
                extra={"capability": "news_data"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 2  # news_data yields news_info + news_security
            assert results[0].error is None
            assert len(results[0].rows) == 1

    def test_fetch_unsupported(self):
        ts, pro = self._make_ts_mock()
        with patch.dict(os.environ, {"TUSHARE_TOKEN": "test_token"}), patch.dict("sys.modules", {"tushare": ts}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="t",
                symbols=None,
                start=datetime.date(2026, 1, 1),
                end=datetime.date(2026, 1, 2),
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
        mock_df = pd.DataFrame(
            {
                "date": ["2026-07-05"],
                "open": [150.0],
                "high": [155.0],
                "low": [149.0],
                "close": [153.0],
                "volume": [1000000],
            }
        )
        # connect() 设置 self._client = tf.TickFlow.free()，故 mock 路径需经过 TickFlow.free
        tf.TickFlow.free.return_value.klines.get.return_value = mock_df

        with patch.dict("sys.modules", {"tickflow": tf}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.us_daily_kline",
                symbols=["AAPL.US"],
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 5),
                extra={"capability": "kline_us_daily"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].rows) == 1
            assert results[0].rows[0][1] == "AAPL.US"

    def test_fetch_us_daily_kline_columns_match_ddl(self):
        """D1 回归：kline_us_daily 产出列名必须与 DDL 真源一致。

        原列名 code 与 kline_us_daily DDL 列名 symbol 不匹配，写入侧列过滤
        （BufferedWriter/ch_writer 按表列交集）丢弃 code 列值，symbol 落空串，
        致空 symbol 行每日 18:00 再生。锚定口径同 tracker #247（us_index）。
        """
        import pandas as pd

        tf = MagicMock()
        mock_df = pd.DataFrame(
            {
                "date": ["2026-07-05"],
                "open": [150.0],
                "high": [155.0],
                "low": [149.0],
                "close": [153.0],
                "volume": [1000000],
            }
        )
        tf.TickFlow.free.return_value.klines.get.return_value = mock_df

        with patch.dict("sys.modules", {"tickflow": tf}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.kline_us_daily",
                symbols=["AAPL.US"],
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 5),
                extra={"capability": "kline_us_daily"},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert results[0].error is None

            from schemas.categories.market_kline_us_daily import INSERT_COLUMNS

            ddl_cols = {c.strip() for c in INSERT_COLUMNS.strip("()").split(",")}
            r = results[0]
            # 产出列必须全部为 DDL 真实列名（写入列过滤不丢任何列）
            assert set(r.columns) <= ddl_cols
            assert r.columns[1] == "symbol"
            assert all(row[1] for row in r.rows)  # symbol 列非空

    def test_fetch_us_index(self):
        """获取美股指数（ETF替代）。"""
        import pandas as pd

        tf = MagicMock()
        mock_df = pd.DataFrame(
            {
                "date": ["2026-07-05"],
                "open": [400.0],
                "high": [405.0],
                "low": [399.0],
                "close": [403.0],
                "volume": [5000000],
            }
        )
        # connect() 设置 self._client = tf.TickFlow.free()，故 mock 路径需经过 TickFlow.free
        tf.TickFlow.free.return_value.klines.get.return_value = mock_df

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
            # tracker #247 回归：产出列必须与 us_index DDL INSERT_COLUMNS 真源一致
            # （symbol 填指数代码；原 index_code/etf_code 列与 DDL 不匹配导致 symbol 落空串）
            from schemas.categories.market_us_index import INSERT_COLUMNS

            ddl_cols = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
            symbols_seen = set()
            for r in results:
                assert r.columns == ddl_cols
                assert all(row[1] for row in r.rows)  # symbol 列非空
                symbols_seen.update(row[1] for row in r.rows)
            assert symbols_seen == {"SPX", "DJI", "IXIC"}


# ============== TDXProvider 测试 ==============


class TestTDXProvider:
    """TDXProvider 测试（通达信板块数据）。"""

    def _make_provider(self):
        from src.zephyr.data.implementations.tdx_provider import TDXProvider

        return TDXProvider()

    def _make_mootdx_mock(self):
        """构造 mootdx 模块 mock。"""
        import pandas as pd

        mootdx = MagicMock()
        mock_client = MagicMock()
        mootdx.quotes.Quotes.factory.return_value = mock_client
        # _verify_kline 调用 client.bars 验证K线能力，需返回非空 DataFrame
        mock_client.bars.return_value = pd.DataFrame({"close": [10.0]})
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
        """industry_class 已弃用（#ARCH-CH-INDUSTRY-CLASS-MIGRATE：tdx block() 语义错配，
        capability 迁 tushare）——回归保护：fetch 必须返回 unsupported capability 错误。"""
        mootdx, mock_client = self._make_mootdx_mock()
        import pandas as pd

        # mootdx block() 返回 DataFrame: [blockname, code]
        mock_client.block.return_value = pd.DataFrame(
            {
                "blockname": ["板块A", "板块B"],
                "code": ["600000", "600016"],
            }
        )

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
            assert "unsupported capability: industry_class" in (results[0].error or "")

    def test_fetch_sector_kline(self):
        """获取板块指数K线。"""
        mootdx, mock_client = self._make_mootdx_mock()
        import pandas as pd

        mock_client.index_bars.return_value = pd.DataFrame(
            {
                "datetime": ["2026-07-05"],
                "open": [1000],
                "high": [1010],
                "low": [995],
                "close": [1005],
                "vol": [50000],
                "amount": [5000000],
            }
        )

        with patch.dict("sys.modules", {"mootdx": mootdx, "mootdx.quotes": mootdx.quotes}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.sector_kline",
                symbols=["sh.880001"],
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 6),
                extra={"capability": "kline_sector", "count": 10},
            )
            results = list(p.fetch(payload, SourcePolicy()))
            assert len(results) == 1
            assert results[0].error is None
            assert len(results[0].rows) == 1

    # ---- 8803/8804 行业板分钟K线接线（T6 §七-7，2026-08-26）----

    def _fetch_with_resolved_symbols(self, resolved, extra):
        """公共装配：mock mootdx + 打桩 _resolve_sector_symbols，返回 index_bars 调用码表。"""
        mootdx, mock_client = self._make_mootdx_mock()
        import pandas as pd

        mock_client.index_bars.return_value = pd.DataFrame(
            {
                "datetime": ["2026-08-26 09:31:00"],
                "open": [1000],
                "high": [1010],
                "low": [995],
                "close": [1005],
                "vol": [50000],
                "amount": [5000000],
            }
        )
        from src.zephyr.data.implementations.tdx_provider import TDXProvider

        with patch.dict("sys.modules", {"mootdx": mootdx, "mootdx.quotes": mootdx.quotes}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="c1_market.kline_sector_intraday",
                symbols=None,
                start=datetime.date(2026, 8, 26),
                end=datetime.date(2026, 8, 26),
                extra=extra,
            )
            with patch.object(TDXProvider, "_resolve_sector_symbols", return_value=resolved):
                results = list(p.fetch(payload, SourcePolicy()))
        assert all(r.error is None for r in results)
        return [c.kwargs["symbol"] for c in mock_client.index_bars.call_args_list]

    def test_fetch_sector_kline_include_industry_boards(self):
        """extra.include_industry_boards=True 且 symbols=null 时，解析码集并入
        132 条 8803/8804 行业板（SSoT=sector_code_bridge.TDX_INDUSTRY_BOARDS）。"""
        from src.zephyr.data.implementations.sector_code_bridge import TDX_INDUSTRY_BOARDS

        called = self._fetch_with_resolved_symbols(
            ["880505", "880002"],
            {"capability": "kline_sector", "period": "1m", "count": 240, "include_industry_boards": True},
        )
        expect = {"880505", "880002"} | {b.code for b in TDX_INDUSTRY_BOARDS}
        assert set(called) == expect
        assert len(called) == len(expect)  # 无重复抓取

    def test_fetch_sector_kline_default_excludes_industry_boards(self):
        """默认（无 include_industry_boards）不抓 8803/8804——日K等既有任务行为不变。"""
        called = self._fetch_with_resolved_symbols(
            ["880505", "880002"],
            {"capability": "kline_sector", "period": "1m", "count": 240},
        )
        assert set(called) == {"880505", "880002"}

    def test_fetch_sector_kline_include_industry_boards_dedup(self):
        """sector_constituent 已含 8803 码时不重复抓取（去重保序）。"""
        called = self._fetch_with_resolved_symbols(
            ["880505", "880301"],
            {"capability": "kline_sector", "period": "1m", "count": 240, "include_industry_boards": True},
        )
        assert called.count("880301") == 1


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
            {"published": "2026-07-05", "title": "news1", "link": "http://1", "summary": "sum1"},
        ]
        fp.parse.return_value = mock_parsed

        with patch.dict(
            "sys.modules",
            {
                "feedparser": fp,
                "requests": requests_mock,
            },
        ):
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
            assert results[0].rows[0][2] == "news1"

    def test_fetch_unsupported(self):
        fp = MagicMock()
        with patch.dict("sys.modules", {"feedparser": fp}):
            p = self._make_provider()
            p.connect()
            payload = FetchPayload(
                table="t",
                symbols=None,
                start=datetime.date(2026, 1, 1),
                end=datetime.date(2026, 1, 2),
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
        RSSProvider.robots_cache.clear()
        # 测试 fail-open（robots.txt 读取失败 → 允许）
        with patch("urllib.robotparser.RobotFileParser.read", side_effect=Exception("net error")):
            assert p.is_allowed("https://example.com/feed.xml") is True

    def test_robots_403_disallow_all_fail_open(self):
        """401/403 on robots.txt → RobotFileParser 内部置 disallow_all=True（不抛异常），
        应按 fail-open 处理。模拟 Investing.com 等 Cloudflare 站点 robots.txt 返回 403 的场景：
        若不处理 disallow_all，can_fetch 会返回 False（误判全站禁止），导致 RSS 源被跳过。"""
        from src.zephyr.data.implementations.rss_provider import RSSProvider

        p = self._make_provider()
        RSSProvider.robots_cache.clear()

        def fake_read(self_rp):
            # 模拟 CPython RobotFileParser.read 对 401/403 的内部处理：置 disallow_all=True，不抛异常
            self_rp.disallow_all = True

        with patch("urllib.robotparser.RobotFileParser.read", fake_read):
            assert p.is_allowed("https://www.investing.com/rss/news_25.rss") is True

    def test_single_feed_failure_does_not_abort_others(self):
        """单源失败不中断整个任务：scheduler._fetch_and_write 遇 FetchResult.error 会 break，
        故 provider 对单 feed 失败不应 yield error（仅 log + 跳过）。验证：feed1 失败、feed2 成功时，
        结果中无 error FetchResult，且 feed2 的行被正确返回（模拟 domestic 源 503 后海外源仍能入库）。"""
        import pandas as pd  # noqa: F401  确保 pandas 可用

        requests_mock = MagicMock()
        ok_response = MagicMock()
        ok_response.content = b"<rss>...</rss>"
        ok_response.raise_for_status.return_value = None

        def fake_get(url, **kwargs):
            if "feed1.example.com" in url:
                raise Exception("503 Server Error: Service Unavailable")
            return ok_response

        requests_mock.get.side_effect = fake_get

        fp = MagicMock()
        mock_parsed = MagicMock()
        mock_parsed.entries = [
            {"published": "2026-07-05", "title": "news_ok", "link": "http://ok", "summary": "sum_ok"},
        ]
        fp.parse.return_value = mock_parsed

        with patch.dict(
            "sys.modules",
            {
                "feedparser": fp,
                "requests": requests_mock,
            },
        ):
            p = self._make_provider()
            p.connect()
            policy = SourcePolicy(respect_robots_txt=False)
            payload = FetchPayload(
                table="c3_fundamental.news_data",
                symbols=["https://feed1.example.com/fail.xml", "https://feed2.example.com/ok.xml"],
                start=datetime.date(2026, 7, 1),
                end=datetime.date(2026, 7, 6),
                extra={"capability": "news_data"},
            )
            results = list(p.fetch(payload, policy))

        # 关键断言：无 error FetchResult（scheduler._fetch_and_write 不会 break）
        assert all(r.error is None for r in results), f"单源失败不应 yield error，但得到: {[r.error for r in results]}"
        # feed2 的行被正确返回（失败的 feed1 被跳过）
        assert len(results) == 1
        assert len(results[0].rows) == 1
        assert results[0].rows[0][2] == "news_ok"
