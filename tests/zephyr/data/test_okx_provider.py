# [BLUEPRINT] MOD-MKT-DATA | docs/03_modules/_domain_mkt_data/vendor_base/blueprint.md
# [MODULE] tests.zephyr.data.test_okx_provider
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.data.implementations.okx_provider
# [CONSUMERS]
# [STARTUP] pytest
# [MATURITY] planned
# [INVARIANTS] 公开端点 mock 不依赖网络
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-002
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] mock 异常->AssertionError
# [TESTS] self
# [A_test] module_id: MOD-MKT-DATA | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""OKX Provider 单元测试（mock HTTP 层，不依赖网络）。"""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

import pytest

from zephyr.data.implementations.okx_provider import (
    _BAR_MAP,
    _CANDLES_URL,
    _HISTORY_CANDLES_URL,
    _KLINE_COLUMNS,
    OkxProvider,
)
from zephyr.data.provider_base import FetchPayload


def _mock_candles_response(count: int = 3) -> MagicMock:
    """构造 OKX K 线 mock 响应。"""
    base_ts = 1693526400000  # 2023-09-01 00:00:00 UTC
    data = []
    for i in range(count):
        ts = base_ts - i * 86400000  # 每天一根，倒序
        data.append([
            str(ts),
            f"{40000.0 + i * 100}",
            f"{40100.0 + i * 100}",
            f"{39900.0 + i * 100}",
            f"{40050.0 + i * 100}",
            f"{10.5 + i}",
            f"{420000.0 + i * 1000}",
            f"{420000.0 + i * 1000}",
            "1",
        ])
    resp = MagicMock()
    resp.json.return_value = {"code": "0", "msg": "", "data": data}
    return resp


def _mock_empty_response() -> MagicMock:
    """构造 OKX 空数据 mock 响应（终止分页循环）。"""
    resp = MagicMock()
    resp.json.return_value = {"code": "0", "msg": "", "data": []}
    return resp


class TestOkxProviderMeta:
    """元数据声明验证。"""

    def test_source_name(self):
        p = OkxProvider()
        assert p.source_name == "okx"

    def test_meta_name(self):
        assert OkxProvider.meta.name == "okx"

    def test_meta_capabilities(self):
        caps = OkxProvider.meta.capabilities_as_strings()
        assert "kline_crypto" in caps

    def test_capability_contract_market(self):
        contract = OkxProvider.meta.get_capability_contract("kline_crypto")
        assert contract is not None
        assert contract.expected_market == "crypto"
        assert contract.expected_variety == "spot"

    def test_bar_map(self):
        assert _BAR_MAP["1d"] == "1D"
        assert _BAR_MAP["4h"] == "4H"
        assert _BAR_MAP["1h"] == "1H"

    def test_kline_columns(self):
        assert "symbol" in _KLINE_COLUMNS
        assert "trade_date" in _KLINE_COLUMNS
        assert "open" in _KLINE_COLUMNS
        assert "close" in _KLINE_COLUMNS
        assert "volume" in _KLINE_COLUMNS
        assert "bar" in _KLINE_COLUMNS


class TestOkxProviderLifecycle:
    """生命周期测试。"""

    def test_connect_with_api_key(self):
        p = OkxProvider()
        with patch("zephyr.data.implementations.okx_provider.get_secret_or_default", return_value="test_key"):
            p.connect()
            assert p._connected is True

    def test_connect_without_api_key(self):
        p = OkxProvider()
        with patch("zephyr.data.implementations.okx_provider.get_secret_or_default", return_value=""):
            p.connect()
            assert p._connected is True

    def test_health_check_success(self):
        p = OkxProvider()
        with patch.object(p, "_http_get", return_value=_mock_candles_response(1)):
            assert p.health_check() is True

    def test_health_check_failure(self):
        p = OkxProvider()
        with patch.object(p, "_http_get", side_effect=Exception("network error")):
            assert p.health_check() is False

    def test_disconnect(self):
        p = OkxProvider()
        p._connected = True
        p.disconnect()
        assert p._connected is False


class TestOkxProviderFetch:
    """fetch 路由测试。"""

    def test_fetch_not_connected(self):
        p = OkxProvider()
        payload = FetchPayload(
            table="c1_market.kline_crypto",
            symbols=["BTC-USDT"],
            start=datetime.date(2023, 9, 1),
            end=datetime.date(2023, 9, 3),
        )
        results = list(p.fetch(payload, None))
        assert len(results) == 1
        assert results[0].error == "okx 未连接"

    def test_fetch_unsupported_capability(self):
        p = OkxProvider()
        p._connected = True
        payload = FetchPayload(
            table="c1_market.kline_crypto",
            symbols=["BTC-USDT"],
            start=datetime.date(2023, 9, 1),
            end=datetime.date(2023, 9, 3),
            extra={"capability": "unsupported"},
        )
        results = list(p.fetch(payload, None))
        assert len(results) == 1
        assert "unsupported capability" in results[0].error

    def test_fetch_no_symbols(self):
        p = OkxProvider()
        p._connected = True
        payload = FetchPayload(
            table="c1_market.kline_crypto",
            symbols=None,
            start=datetime.date(2023, 9, 1),
            end=datetime.date(2023, 9, 3),
            extra={"capability": "kline_crypto"},
        )
        results = list(p.fetch(payload, None))
        assert len(results) == 1
        assert "必须显式传 symbols" in results[0].error


class TestOkxProviderFetchKline:
    """K 线拉取测试。"""

    def _make_provider(self) -> OkxProvider:
        p = OkxProvider()
        p._connected = True
        return p

    def test_fetch_kline_basic(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", side_effect=[_mock_candles_response(3), _mock_empty_response()]):
            payload = FetchPayload(
                table="c1_market.kline_crypto",
                symbols=["BTC-USDT"],
                start=datetime.date(2023, 9, 1),
                end=datetime.date(2023, 9, 3),
                extra={"capability": "kline_crypto", "bar": "1d"},
            )
            results = list(p.fetch(payload, None))
            assert len(results) == 1
            r = results[0]
            assert r.error is None
            assert len(r.rows) == 3
            assert r.rows[0][0] == "BTC-USDT"  # symbol
            assert isinstance(r.rows[0][2], float)  # open
            assert r.rows[0][8] == "1D"  # bar

    def test_fetch_kline_4h_bar(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", side_effect=[_mock_candles_response(2), _mock_empty_response()]):
            payload = FetchPayload(
                table="c1_market.kline_crypto",
                symbols=["ETH-USDT"],
                start=datetime.date(2023, 9, 1),
                end=datetime.date(2023, 9, 2),
                extra={"capability": "kline_crypto", "bar": "4h"},
            )
            results = list(p.fetch(payload, None))
            assert len(results) == 1
            assert results[0].rows[0][8] == "4H"

    def test_fetch_kline_api_error(self):
        p = self._make_provider()
        error_resp = MagicMock()
        error_resp.json.return_value = {"code": "50001", "msg": "Service error"}
        with patch.object(p, "_call_with_policy", return_value=error_resp):
            payload = FetchPayload(
                table="c1_market.kline_crypto",
                symbols=["BTC-USDT"],
                start=datetime.date(2023, 9, 1),
                end=datetime.date(2023, 9, 3),
                extra={"capability": "kline_crypto"},
            )
            results = list(p.fetch(payload, None))
            assert len(results) == 1
            assert "OKX API 错误" in results[0].error

    def test_fetch_kline_network_error(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            payload = FetchPayload(
                table="c1_market.kline_crypto",
                symbols=["BTC-USDT"],
                start=datetime.date(2023, 9, 1),
                end=datetime.date(2023, 9, 3),
                extra={"capability": "kline_crypto"},
            )
            results = list(p.fetch(payload, None))
            assert len(results) == 1
            assert "OKX API 请求失败" in results[0].error

    def test_fetch_kline_row_format(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", side_effect=[_mock_candles_response(1), _mock_empty_response()]):
            payload = FetchPayload(
                table="c1_market.kline_crypto",
                symbols=["BTC-USDT"],
                start=datetime.date(2023, 9, 1),
                end=datetime.date(2023, 9, 1),
                extra={"capability": "kline_crypto"},
            )
            results = list(p.fetch(payload, None))
            row = results[0].rows[0]
            assert len(row) == len(_KLINE_COLUMNS)
            assert row[1] == "2023-09-01"  # trade_date
            assert row[2] == 40000.0  # open
            assert row[3] == 40100.0  # high
            assert row[4] == 39900.0  # low
            assert row[5] == 40050.0  # close
            assert row[6] == 10.5  # volume
            assert row[9] == 1  # confirm
