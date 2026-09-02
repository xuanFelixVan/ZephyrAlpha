# [BLUEPRINT] MOD-MKT-DATA | docs/03_modules/_domain_mkt_data/vendor_base/blueprint.md
# [MODULE] tests.zephyr.data.test_okx_swap_provider
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.data.implementations.okx_swap_provider
# [CONSUMERS]
# [STARTUP] pytest
# [MATURITY] planned
# [INVARIANTS] 公开端点 mock 不依赖网络
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.4 CAND-CRYPTO-003
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] mock 异常->AssertionError
# [TESTS] self
# [A_test] module_id: MOD-MKT-DATA | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""OKX 永续合约 Provider 单元测试（mock HTTP 层，不依赖网络）。

覆盖 CAND-CRYPTO-003 四类采集：资金费率历史 / 持仓量 OI / 标记价格 / 基差。
"""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

import pytest

from zephyr.data.implementations.okx_swap_provider import (
    _BASIS_COLUMNS,
    _FUNDING_RATE_COLUMNS,
    _MARK_PRICE_COLUMNS,
    _OPEN_INTEREST_COLUMNS,
    OkxSwapProvider,
)
from zephyr.data.provider_base import FetchPayload


def _mock_funding_history_response(count: int = 3) -> MagicMock:
    """构造 OKX 资金费率历史 mock 响应（时间倒序）。"""
    base_ts = 1693526400000  # 2023-09-01 00:00:00 UTC
    data = []
    for i in range(count):
        ts = base_ts - i * 28800000  # 每 8 小时一条，倒序
        data.append(
            {
                "instType": "SWAP",
                "instId": "BTC-USDT-SWAP",
                "fundingRate": f"{0.0001 + i * 0.00001}",
                "realizedRate": f"{0.0001 + i * 0.00001}",
                "fundingTime": str(ts),
                "method": "current_period",
            }
        )
    resp = MagicMock()
    resp.json.return_value = {"code": "0", "msg": "", "data": data}
    return resp


def _mock_funding_rate_response() -> MagicMock:
    """构造 OKX 当前资金费率 mock 响应（探活用）。"""
    resp = MagicMock()
    resp.json.return_value = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "instType": "SWAP",
                "instId": "BTC-USDT-SWAP",
                "fundingRate": "0.0001",
                "nextFundingRate": "0.00012",
                "fundingTime": "1693526400000",
                "nextFundingTime": "1693555200000",
            }
        ],
    }
    return resp


def _mock_open_interest_response() -> MagicMock:
    """构造 OKX 持仓量 OI mock 响应。"""
    resp = MagicMock()
    resp.json.return_value = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "instType": "SWAP",
                "instId": "BTC-USDT-SWAP",
                "oi": "10000",
                "oiCcy": "10000",
                "oiUsd": "400000000",
                "ts": "1693526400000",
            }
        ],
    }
    return resp


def _mock_mark_price_response() -> MagicMock:
    """构造 OKX 标记价格 mock 响应。"""
    resp = MagicMock()
    resp.json.return_value = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "instType": "SWAP",
                "instId": "BTC-USDT-SWAP",
                "markPx": "40050.5",
                "ts": "1693526400000",
            }
        ],
    }
    return resp


def _mock_index_tickers_response() -> MagicMock:
    """构造 OKX 现货指数价 mock 响应。"""
    resp = MagicMock()
    resp.json.return_value = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "instId": "BTC-USDT",
                "idxPx": "40000.0",
                "high24h": "40100",
                "low24h": "39900",
                "open24h": "40000",
                "sodUtc0": "40010",
                "sodUtc8": "40020",
                "ts": "1693526400000",
            }
        ],
    }
    return resp


def _mock_empty_response() -> MagicMock:
    """构造 OKX 空数据 mock 响应（终止分页循环）。"""
    resp = MagicMock()
    resp.json.return_value = {"code": "0", "msg": "", "data": []}
    return resp


def _mock_api_error_response(msg: str = "Service error") -> MagicMock:
    """构造 OKX API 错误 mock 响应（code != 0）。"""
    resp = MagicMock()
    resp.json.return_value = {"code": "50001", "msg": msg}
    return resp


def _make_provider() -> OkxSwapProvider:
    p = OkxSwapProvider()
    p._connected = True
    return p


_SYMBOLS_SENTINEL = object()


def _payload(capability: str, symbols=_SYMBOLS_SENTINEL) -> FetchPayload:
    # start 放宽到 2023-08-01：资金费率历史按 [start, end] 过滤，
    # mock 数据点围绕 2023-09-01，避免本地时区换算导致边界点被过滤
    return FetchPayload(
        table="c1_market.swap_test",
        symbols=["BTC-USDT-SWAP"] if symbols is _SYMBOLS_SENTINEL else symbols,
        start=datetime.date(2023, 8, 1),
        end=datetime.date(2023, 9, 3),
        extra={"capability": capability},
    )


class TestOkxSwapProviderMeta:
    """元数据声明验证。"""

    def test_source_name(self):
        p = OkxSwapProvider()
        assert p.source_name == "okx_swap"

    def test_meta_name(self):
        assert OkxSwapProvider.meta.name == "okx_swap"

    def test_meta_capabilities(self):
        caps = OkxSwapProvider.meta.capabilities_as_strings()
        assert "funding_rate_history" in caps
        assert "open_interest" in caps
        assert "mark_price" in caps
        assert "basis" in caps

    def test_capability_contract_market(self):
        for cap in ("funding_rate_history", "open_interest", "mark_price", "basis"):
            contract = OkxSwapProvider.meta.get_capability_contract(cap)
            assert contract is not None
            assert contract.expected_market == "crypto"
            assert contract.expected_variety == "swap"

    def test_funding_rate_columns(self):
        assert "symbol" in _FUNDING_RATE_COLUMNS
        assert "funding_time" in _FUNDING_RATE_COLUMNS
        assert "funding_rate" in _FUNDING_RATE_COLUMNS
        assert "realized_rate" in _FUNDING_RATE_COLUMNS

    def test_open_interest_columns(self):
        assert "symbol" in _OPEN_INTEREST_COLUMNS
        assert "oi" in _OPEN_INTEREST_COLUMNS
        assert "oi_ccy" in _OPEN_INTEREST_COLUMNS
        assert "oi_usd" in _OPEN_INTEREST_COLUMNS

    def test_mark_price_columns(self):
        assert "symbol" in _MARK_PRICE_COLUMNS
        assert "ts" in _MARK_PRICE_COLUMNS
        assert "mark_px" in _MARK_PRICE_COLUMNS

    def test_basis_columns(self):
        assert "symbol" in _BASIS_COLUMNS
        assert "mark_px" in _BASIS_COLUMNS
        assert "index_px" in _BASIS_COLUMNS
        assert "basis" in _BASIS_COLUMNS
        assert "basis_pct" in _BASIS_COLUMNS


class TestOkxSwapProviderLifecycle:
    """生命周期测试。"""

    def test_connect(self):
        p = OkxSwapProvider()
        p.connect()
        assert p._connected is True

    def test_health_check_success(self):
        p = OkxSwapProvider()
        with patch.object(p, "_http_get", return_value=_mock_funding_rate_response()):
            assert p.health_check() is True

    def test_health_check_failure(self):
        p = OkxSwapProvider()
        with patch.object(p, "_http_get", side_effect=Exception("network error")):
            assert p.health_check() is False

    def test_disconnect(self):
        p = OkxSwapProvider()
        p._connected = True
        p.disconnect()
        assert p._connected is False


class TestOkxSwapProviderFetch:
    """fetch 路由测试。"""

    def test_fetch_not_connected(self):
        p = OkxSwapProvider()
        results = list(p.fetch(_payload("funding_rate_history"), None))
        assert len(results) == 1
        assert results[0].error == "okx_swap 未连接"

    def test_fetch_unsupported_capability(self):
        p = _make_provider()
        results = list(p.fetch(_payload("unsupported"), None))
        assert len(results) == 1
        assert "unsupported capability" in results[0].error

    @pytest.mark.parametrize("cap", ["funding_rate_history", "open_interest", "mark_price", "basis"])
    def test_fetch_no_symbols(self, cap):
        p = _make_provider()
        results = list(p.fetch(_payload(cap, symbols=None), None))
        assert len(results) == 1
        assert "必须显式传 symbols" in results[0].error


class TestOkxSwapProviderFundingRate:
    """资金费率历史采集测试。"""

    def test_fetch_funding_rate_basic(self):
        p = _make_provider()
        with patch.object(
            p, "_call_with_policy", side_effect=[_mock_funding_history_response(3), _mock_empty_response()]
        ):
            results = list(p.fetch(_payload("funding_rate_history"), None))
            assert len(results) == 1
            r = results[0]
            assert r.error is None
            assert len(r.rows) == 3
            assert r.rows[0][0] == "BTC-USDT-SWAP"  # symbol
            assert isinstance(r.rows[0][2], float)  # funding_rate
            assert r.rows[0][4] == "current_period"  # method

    def test_fetch_funding_rate_row_format(self):
        p = _make_provider()
        with patch.object(
            p, "_call_with_policy", side_effect=[_mock_funding_history_response(1), _mock_empty_response()]
        ):
            results = list(p.fetch(_payload("funding_rate_history"), None))
            row = results[0].rows[0]
            assert len(row) == len(_FUNDING_RATE_COLUMNS)
            assert row[1].startswith("2023-09-01")  # funding_time ISO
            assert row[2] == pytest.approx(0.0001)  # funding_rate
            assert row[3] == pytest.approx(0.0001)  # realized_rate
            assert results[0].last_key == row[1]

    def test_fetch_funding_rate_api_error(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_api_error_response()):
            results = list(p.fetch(_payload("funding_rate_history"), None))
            assert len(results) == 1
            assert "OKX API 错误" in results[0].error

    def test_fetch_funding_rate_network_error(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            results = list(p.fetch(_payload("funding_rate_history"), None))
            assert len(results) == 1
            assert "OKX API 请求失败" in results[0].error


class TestOkxSwapProviderOpenInterest:
    """持仓量 OI 采集测试。"""

    def test_fetch_open_interest_basic(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_open_interest_response()):
            results = list(p.fetch(_payload("open_interest"), None))
            assert len(results) == 1
            r = results[0]
            assert r.error is None
            assert len(r.rows) == 1
            row = r.rows[0]
            assert len(row) == len(_OPEN_INTEREST_COLUMNS)
            assert row[0] == "BTC-USDT-SWAP"
            assert row[1].startswith("2023-09-01")  # ts ISO
            assert row[2] == 10000.0  # oi
            assert row[3] == 10000.0  # oi_ccy
            assert row[4] == 400000000.0  # oi_usd
            assert r.last_key == row[1]

    def test_fetch_open_interest_api_error(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_api_error_response()):
            results = list(p.fetch(_payload("open_interest"), None))
            assert len(results) == 1
            assert "OKX API 错误" in results[0].error

    def test_fetch_open_interest_network_error(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            results = list(p.fetch(_payload("open_interest"), None))
            assert len(results) == 1
            assert "OKX API 请求失败" in results[0].error


class TestOkxSwapProviderMarkPrice:
    """标记价格采集测试。"""

    def test_fetch_mark_price_basic(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_mark_price_response()):
            results = list(p.fetch(_payload("mark_price"), None))
            assert len(results) == 1
            r = results[0]
            assert r.error is None
            assert len(r.rows) == 1
            row = r.rows[0]
            assert len(row) == len(_MARK_PRICE_COLUMNS)
            assert row[0] == "BTC-USDT-SWAP"
            assert row[1].startswith("2023-09-01")  # ts ISO
            assert row[2] == 40050.5  # mark_px
            assert r.last_key == row[1]

    def test_fetch_mark_price_api_error(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_api_error_response()):
            results = list(p.fetch(_payload("mark_price"), None))
            assert len(results) == 1
            assert "OKX API 错误" in results[0].error

    def test_fetch_mark_price_network_error(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            results = list(p.fetch(_payload("mark_price"), None))
            assert len(results) == 1
            assert "OKX API 请求失败" in results[0].error


class TestOkxSwapProviderBasis:
    """基差采集测试（标记价格 - 现货指数价衍生）。"""

    def test_spot_index_inst_id(self):
        assert OkxSwapProvider._spot_index_inst_id("BTC-USDT-SWAP") == "BTC-USDT"
        assert OkxSwapProvider._spot_index_inst_id("ETH-USDT-SWAP") == "ETH-USDT"
        assert OkxSwapProvider._spot_index_inst_id("BTC-USDT") == "BTC-USDT"

    def test_fetch_basis_basic(self):
        p = _make_provider()
        with patch.object(
            p,
            "_call_with_policy",
            side_effect=[_mock_mark_price_response(), _mock_index_tickers_response()],
        ):
            results = list(p.fetch(_payload("basis"), None))
            assert len(results) == 1
            r = results[0]
            assert r.error is None
            assert len(r.rows) == 1
            row = r.rows[0]
            assert len(row) == len(_BASIS_COLUMNS)
            assert row[0] == "BTC-USDT-SWAP"
            assert row[1].startswith("2023-09-01")  # ts ISO
            assert row[2] == 40050.5  # mark_px
            assert row[3] == 40000.0  # index_px
            assert row[4] == pytest.approx(50.5)  # basis = mark_px - index_px
            assert row[5] == pytest.approx(50.5 / 40000.0)  # basis_pct
            assert r.last_key == row[1]

    def test_fetch_basis_api_error(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_api_error_response()):
            results = list(p.fetch(_payload("basis"), None))
            assert len(results) == 1
            assert "OKX API 错误" in results[0].error

    def test_fetch_basis_network_error(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            results = list(p.fetch(_payload("basis"), None))
            assert len(results) == 1
            assert "OKX API 请求失败" in results[0].error

    def test_fetch_basis_empty_data(self):
        p = _make_provider()
        with patch.object(p, "_call_with_policy", side_effect=[_mock_empty_response(), _mock_empty_response()]):
            results = list(p.fetch(_payload("basis"), None))
            assert len(results) == 1
            assert "空数据" in results[0].error
