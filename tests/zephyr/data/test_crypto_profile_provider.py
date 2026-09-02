# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_crypto_profile_provider
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.implementations.crypto_profile_provider
# [CONSUMERS]
# [STARTUP] pytest
# [MATURITY] planned
# [INVARIANTS] mock HTTP 层不依赖网络；统一行格式恒为 7 列
# [MODIFY-GUARD]
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] mock 异常->AssertionError
# [TESTS] self
# [A_test] module_id: MOD-L00-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""CryptoProfileProvider 单元测试（mock HTTP 层，不依赖网络）。"""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

from zephyr.data.implementations.crypto_profile_provider import (
    _CMC_INFO_URL,
    _CMC_QUOTES_URL,
    _COINGECKO_LIST_URL,
    _PROFILE_COLUMNS,
    CoinProfile,
    CryptoProfileProvider,
    _first_non_empty,
    _to_float,
)
from zephyr.data.provider_base import FetchPayload


def _json_response(data) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = data
    return resp


_GECKO_LIST = [
    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
    {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
    {"id": "tether", "symbol": "usdt", "name": "Tether"},
]

_GECKO_BTC_DETAIL = {
    "id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin",
    "genesis_date": "2009-01-03",
    "links": {
        "homepage": ["https://bitcoin.org", ""],
        "whitepaper": "https://bitcoin.org/bitcoin.pdf",
        "blockchain_site": ["https://blockchair.com/bitcoin/", "https://btc.com/"],
    },
    "market_data": {"circulating_supply": 19700000.0, "total_supply": 19700000.0},
}

_GECKO_USDT_DETAIL = {
    "id": "tether",
    "symbol": "usdt",
    "name": "Tether",
    "asset_platform_id": "ethereum",
    "contract_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "genesis_date": "2014-10-06",
    "links": {
        "homepage": ["https://tether.to"],
        "whitepaper": "https://tether.to/wp-content/uploads/2016/06/TetherWhitePaper.pdf",
        "blockchain_site": ["https://www.omniexplorer.info/asset/31"],
    },
    "market_data": {"circulating_supply": 118000000000.0, "total_supply": 120000000000.0},
}

_CMC_BTC_INFO = {
    "data": {
        "BTC": {
            "name": "Bitcoin",
            "date_added": "2013-04-28T00:00:00.000Z",
            "urls": {
                "website": ["https://bitcoin.org/"],
                "whitepaper": ["https://bitcoin.org/bitcoin.pdf"],
                "explorer": ["https://blockchain.info/"],
            },
            "contract_address": [],
        }
    }
}

_CMC_BTC_QUOTES = {
    "data": {
        "BTC": {
            "name": "Bitcoin",
            "circulating_supply": 19700000.0,
            "total_supply": 19700000.0,
        }
    }
}

_CMC_USDT_INFO = {
    "data": {
        "USDT": {
            "name": "Tether",
            "date_added": "2015-02-25T00:00:00.000Z",
            "urls": {
                "website": ["https://tether.to"],
                "whitepaper": [],
                "explorer": ["https://etherscan.io/token/0xdAC17F958D2ee523a2206206994597C13D831ec7"],
            },
            "contract_address": [
                {"contract_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "platform": {"name": "Ethereum"}}
            ],
        }
    }
}

_CMC_USDT_QUOTES = {
    "data": {
        "USDT": {
            "name": "Tether",
            "circulating_supply": 118000000000.0,
            "total_supply": 120000000000.0,
        }
    }
}


_DEFAULT_SYMBOLS = object()


def _make_payload(symbols=_DEFAULT_SYMBOLS, capability="coin_profile", source="coingecko") -> FetchPayload:
    return FetchPayload(
        table="c1_alt.crypto_profile",
        symbols=["BTC"] if symbols is _DEFAULT_SYMBOLS else symbols,
        start=datetime.date(2026, 8, 28),
        end=datetime.date(2026, 8, 28),
        extra={"capability": capability, "source": source},
    )


def _gecko_router(fn, policy, url: str, **kwargs) -> MagicMock:
    """按 URL 路由 CoinGecko mock 响应（side_effect 签名对齐 _call_with_policy(fn, policy, url, ...)）。"""
    if url == _COINGECKO_LIST_URL:
        return _json_response(_GECKO_LIST)
    if url.endswith("/coins/bitcoin"):
        return _json_response(_GECKO_BTC_DETAIL)
    if url.endswith("/coins/tether"):
        return _json_response(_GECKO_USDT_DETAIL)
    raise AssertionError(f"unexpected url: {url}")


def _cmc_router(fn, policy, url: str, **kwargs) -> MagicMock:
    """按 URL + symbol 路由 CoinMarketCap mock 响应（side_effect 签名对齐 _call_with_policy）。"""
    symbol = (kwargs.get("params") or {}).get("symbol", "")
    if url == _CMC_INFO_URL:
        return _json_response({"data": {"USDT": _CMC_USDT_INFO["data"], "BTC": _CMC_BTC_INFO["data"]}[symbol]})
    if url == _CMC_QUOTES_URL:
        return _json_response({"data": {"USDT": _CMC_USDT_QUOTES["data"], "BTC": _CMC_BTC_QUOTES["data"]}[symbol]})
    raise AssertionError(f"unexpected url: {url}")


def _make_connected_provider() -> CryptoProfileProvider:
    p = CryptoProfileProvider()
    p._connected = True
    return p


class TestCryptoProfileProviderMeta:
    """元数据声明验证。"""

    def test_source_name(self):
        p = CryptoProfileProvider()
        assert p.source_name == "crypto_profile"

    def test_meta_name(self):
        assert CryptoProfileProvider.meta.name == "crypto_profile"

    def test_meta_capabilities(self):
        caps = CryptoProfileProvider.meta.capabilities_as_strings()
        assert "coin_profile" in caps

    def test_capability_contract_market(self):
        contract = CryptoProfileProvider.meta.get_capability_contract("coin_profile")
        assert contract is not None
        assert contract.expected_market == "crypto"
        assert contract.expected_variety == "profile"
        assert contract.requires_date_range is False

    def test_profile_columns(self):
        assert _PROFILE_COLUMNS == [
            "symbol",
            "name",
            "launch_date",
            "circulating_supply",
            "total_supply",
            "website",
            "explorer",
        ]


class TestCryptoProfileProviderLifecycle:
    """生命周期测试（含 CMC key 注入接口）。"""

    def test_connect_without_cmc_key(self):
        p = CryptoProfileProvider()
        with patch("zephyr.data.implementations.crypto_profile_provider.get_service_secret", return_value=""):
            p.connect()
            assert p._connected is True
            assert p._cmc_api_key == ""

    def test_connect_with_cmc_key(self):
        p = CryptoProfileProvider()
        with patch(
            "zephyr.data.implementations.crypto_profile_provider.get_service_secret",
            return_value="cmc_key",
        ) as spy:
            p.connect()
            assert p._cmc_api_key == "cmc_key"
        spy.assert_called_once_with("CMC_API_KEY", "coinmarketcap", required=False)

    def test_health_check_success(self):
        p = CryptoProfileProvider()
        with patch.object(p, "_http_get", return_value=_json_response({"gecko_says": "(V3) To the Moon!"})):
            assert p.health_check() is True

    def test_health_check_failure(self):
        p = CryptoProfileProvider()
        with patch.object(p, "_http_get", side_effect=Exception("network error")):
            assert p.health_check() is False

    def test_disconnect(self):
        p = CryptoProfileProvider()
        p._connected = True
        p._cmc_api_key = "k"
        p._gecko_id_map = {"btc": "bitcoin"}
        p.disconnect()
        assert p._connected is False
        assert p._cmc_api_key == ""
        assert p._gecko_id_map == {}


class TestCryptoProfileProviderFetchRoute:
    """fetch 路由测试。"""

    def test_fetch_not_connected(self):
        p = CryptoProfileProvider()
        results = list(p.fetch(_make_payload(), None))
        assert len(results) == 1
        assert results[0].error == "crypto_profile 未连接"

    def test_fetch_unsupported_capability(self):
        p = _make_connected_provider()
        results = list(p.fetch(_make_payload(capability="ico_calendar"), None))
        assert len(results) == 1
        assert "unsupported capability" in results[0].error

    def test_fetch_no_symbols(self):
        p = _make_connected_provider()
        results = list(p.fetch(_make_payload(symbols=None), None))
        assert len(results) == 1
        assert "必须显式传 symbols" in results[0].error

    def test_fetch_unsupported_source(self):
        p = _make_connected_provider()
        results = list(p.fetch(_make_payload(source="binance"), None))
        assert len(results) == 1
        assert "unsupported source" in results[0].error


class TestCryptoProfileProviderGecko:
    """CoinGecko 免费源测试（mock HTTP 层）。"""

    def test_gecko_basic_row(self):
        p = _make_connected_provider()
        with patch.object(p, "_call_with_policy", side_effect=_gecko_router):
            results = list(p.fetch(_make_payload(), None))
        assert len(results) == 1
        r = results[0]
        assert r.error is None
        assert r.columns == _PROFILE_COLUMNS
        assert r.rows == [
            (
                "BTC",
                "Bitcoin",
                "2009-01-03",
                19700000.0,
                19700000.0,
                "https://bitcoin.org",
                "https://blockchair.com/bitcoin/",
            )
        ]
        assert r.last_key == "BTC"

    def test_gecko_row_unified_format(self):
        """统一格式恒为 (symbol, name, launch_date, circulating_supply, total_supply, website, explorer)。"""
        p = _make_connected_provider()
        with patch.object(p, "_call_with_policy", side_effect=_gecko_router):
            results = list(p.fetch(_make_payload(), None))
        row = results[0].rows[0]
        assert len(row) == 7
        assert isinstance(row[0], str) and isinstance(row[1], str) and isinstance(row[2], str)
        assert isinstance(row[3], float) and isinstance(row[4], float)
        assert isinstance(row[5], str) and isinstance(row[6], str)

    def test_gecko_token_contract_explorer(self):
        """代币合约地址 + 平台映射 → explorer 构造为代币级浏览器链接。"""
        p = _make_connected_provider()
        with patch.object(p, "_call_with_policy", side_effect=_gecko_router):
            results = list(p.fetch(_make_payload(symbols=["USDT"]), None))
        row = results[0].rows[0]
        assert row[0] == "USDT"
        assert row[1] == "Tether"
        assert row[2] == "2014-10-06"
        assert row[3] == 118000000000.0
        assert row[4] == 120000000000.0
        assert row[5] == "https://tether.to"
        assert row[6] == "https://etherscan.io/token/0xdAC17F958D2ee523a2206206994597C13D831ec7"

    def test_gecko_symbol_not_found(self):
        p = _make_connected_provider()
        with patch.object(p, "_call_with_policy", side_effect=_gecko_router):
            results = list(p.fetch(_make_payload(symbols=["NOPE"]), None))
        assert len(results) == 1
        assert results[0].rows == []
        assert "未找到 symbol" in results[0].error

    def test_gecko_network_error(self):
        p = _make_connected_provider()
        with patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            results = list(p.fetch(_make_payload(), None))
        assert len(results) == 1
        assert "coingecko API 请求失败" in results[0].error

    def test_gecko_bad_format(self):
        p = _make_connected_provider()
        with patch.object(p, "_call_with_policy", return_value=_json_response({"error": "bad"})):
            results = list(p.fetch(_make_payload(), None))
        assert len(results) == 1
        assert "响应格式异常" in results[0].error

    def test_gecko_id_map_cached(self):
        """/coins/list 进程内缓存：多 symbol 只拉一次映射表。"""
        p = _make_connected_provider()
        calls = []

        def _spy(fn, policy, url, **kwargs):
            calls.append(url)
            return _gecko_router(fn, policy, url, **kwargs)

        with patch.object(p, "_call_with_policy", side_effect=_spy):
            results = list(p.fetch(_make_payload(symbols=["BTC", "USDT"]), None))
        assert all(r.error is None for r in results)
        assert calls.count(_COINGECKO_LIST_URL) == 1

    def test_gecko_parse_whitepaper_and_contract(self):
        """白皮书/合约地址解析进 CoinProfile（不入 7 列统一行）。"""
        p = _make_connected_provider()
        profile = p._parse_gecko_profile("USDT", _GECKO_USDT_DETAIL)
        assert profile.whitepaper.endswith("TetherWhitePaper.pdf")
        assert profile.contract_address == "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        assert profile.source == "coingecko"
        assert profile.to_row()[6] == profile.explorer


class TestCryptoProfileProviderCmc:
    """CoinMarketCap 免费 tier 源测试（mock HTTP 层）。"""

    def test_cmc_requires_key(self):
        p = _make_connected_provider()
        results = list(p.fetch(_make_payload(source="coinmarketcap"), None))
        assert len(results) == 1
        assert results[0].rows == []
        assert "CMC_API_KEY" in results[0].error

    def test_cmc_basic_row(self):
        p = _make_connected_provider()
        p._cmc_api_key = "cmc_key"
        with patch.object(p, "_call_with_policy", side_effect=_cmc_router):
            results = list(p.fetch(_make_payload(source="coinmarketcap"), None))
        assert len(results) == 1
        r = results[0]
        assert r.error is None
        assert r.rows == [
            (
                "BTC",
                "Bitcoin",
                "2013-04-28",
                19700000.0,
                19700000.0,
                "https://bitcoin.org/",
                "https://blockchain.info/",
            )
        ]

    def test_cmc_date_added_truncated(self):
        """date_added ISO 时间戳截断为日期（launch_date）。"""
        p = _make_connected_provider()
        p._cmc_api_key = "cmc_key"
        with patch.object(p, "_call_with_policy", side_effect=_cmc_router):
            results = list(p.fetch(_make_payload(symbols=["USDT"], source="coinmarketcap"), None))
        assert results[0].rows[0][2] == "2015-02-25"

    def test_cmc_contract_address_parsed(self):
        p = _make_connected_provider()
        profile, error = p._parse_cmc_profile("USDT", _CMC_USDT_INFO, _CMC_USDT_QUOTES)
        assert error is None
        assert profile.contract_address == "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        assert profile.explorer.endswith("0xdAC17F958D2ee523a2206206994597C13D831ec7")
        assert profile.source == "coinmarketcap"

    def test_cmc_symbol_not_found(self):
        p = _make_connected_provider()
        profile, error = p._parse_cmc_profile("NOPE", {"data": {}}, {"data": {}})
        assert profile is None
        assert "未找到 symbol" in error

    def test_cmc_network_error(self):
        p = _make_connected_provider()
        p._cmc_api_key = "cmc_key"
        with patch.object(p, "_call_with_policy", side_effect=Exception("403 forbidden")):
            results = list(p.fetch(_make_payload(source="coinmarketcap"), None))
        assert len(results) == 1
        assert "coinmarketcap API 请求失败" in results[0].error


class TestHelpers:
    """辅助函数与数据类测试。"""

    def test_first_non_empty_list(self):
        assert _first_non_empty(["", "https://a", "https://b"]) == "https://a"
        assert _first_non_empty([]) == ""
        assert _first_non_empty([None, ""]) == ""

    def test_first_non_empty_scalar(self):
        assert _first_non_empty("https://a") == "https://a"
        assert _first_non_empty("") == ""
        assert _first_non_empty(None) == ""

    def test_to_float(self):
        assert _to_float(1.5) == 1.5
        assert _to_float("2.5") == 2.5
        assert _to_float(None) == 0.0
        assert _to_float("bad") == 0.0

    def test_coin_profile_to_row(self):
        profile = CoinProfile(
            symbol="BTC",
            name="Bitcoin",
            launch_date="2009-01-03",
            circulating_supply=19700000.0,
            total_supply=21000000.0,
            website="https://bitcoin.org",
            whitepaper="https://bitcoin.org/bitcoin.pdf",
            contract_address="",
            explorer="https://blockchair.com/bitcoin/",
            source="coingecko",
        )
        assert profile.to_row() == (
            "BTC",
            "Bitcoin",
            "2009-01-03",
            19700000.0,
            21000000.0,
            "https://bitcoin.org",
            "https://blockchair.com/bitcoin/",
        )
