# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_onchain_provider
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.implementations.onchain_provider
# [CONSUMERS]
# [STARTUP] pytest
# [MATURITY] planned
# [INVARIANTS] mock 序列确定性（同输入恒同输出）不依赖网络
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-004
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] mock 异常->AssertionError
# [TESTS] self
# [A_test] module_id: MOD-L00-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""OnchainProvider 单元测试（mock HTTP 层 + 确定性 mock 序列，不依赖网络）。"""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

from zephyr.data.implementations.onchain_provider import (
    _CAPABILITY_KEYS,
    _CAPABILITY_ROUTES,
    _ONCHAIN_COLUMNS,
    OnchainProvider,
)
from zephyr.data.provider_base import FetchPayload


def _mock_live_response(count: int = 3) -> MagicMock:
    """构造 Glassnode 风格 mock 响应：[{t: ts_sec, v: value}, ...]。"""
    base_ts = 1693526400  # 2023-09-01 00:00:00 UTC
    data = [{"t": base_ts + i * 86400, "v": 100.0 + i * 10} for i in range(count)]
    resp = MagicMock()
    resp.json.return_value = data
    return resp


_DEFAULT_SYMBOLS = object()


def _make_payload(capability: str, symbols=_DEFAULT_SYMBOLS) -> FetchPayload:
    return FetchPayload(
        table="c1_alt.onchain_metrics",
        symbols=["BTC"] if symbols is _DEFAULT_SYMBOLS else symbols,
        start=datetime.date(2023, 9, 1),
        end=datetime.date(2023, 9, 3),
        extra={"capability": capability},
    )


class TestOnchainProviderMeta:
    """元数据声明验证。"""

    def test_source_name(self):
        p = OnchainProvider()
        assert p.source_name == "onchain"

    def test_meta_name(self):
        assert OnchainProvider.meta.name == "onchain"

    def test_meta_capabilities(self):
        caps = OnchainProvider.meta.capabilities_as_strings()
        assert "exchange_netflow" in caps
        assert "active_addresses" in caps
        assert "stablecoin_flows" in caps

    def test_capability_contract_market(self):
        contract = OnchainProvider.meta.get_capability_contract("exchange_netflow")
        assert contract is not None
        assert contract.expected_market == "crypto"
        assert contract.expected_variety == "onchain"

    def test_capability_routes(self):
        assert _CAPABILITY_ROUTES["exchange_netflow"][0] == "glassnode"
        assert _CAPABILITY_ROUTES["active_addresses"][0] == "glassnode"
        assert _CAPABILITY_ROUTES["stablecoin_flows"][0] == "cryptoquant"

    def test_capability_keys(self):
        assert _CAPABILITY_KEYS["exchange_netflow"] == ("glassnode", "GLASSNODE_API_KEY")
        assert _CAPABILITY_KEYS["stablecoin_flows"] == ("cryptoquant", "CRYPTOQUANT_API_KEY")

    def test_onchain_columns(self):
        assert _ONCHAIN_COLUMNS == ["metric", "asset", "trade_date", "value", "source", "is_mock"]


class TestOnchainProviderLifecycle:
    """生命周期测试（含付费 API 密钥注入接口）。"""

    def test_connect_without_api_key(self):
        p = OnchainProvider()
        with patch("zephyr.data.implementations.onchain_provider.get_service_secret", return_value=""):
            p.connect()
            assert p._connected is True
            assert p._api_keys == {}

    def test_connect_with_glassnode_key(self):
        p = OnchainProvider()

        def _fake_secret(key, service, required=True):
            return "glass_key" if service == "glassnode" else ""

        with patch("zephyr.data.implementations.onchain_provider.get_service_secret", side_effect=_fake_secret):
            p.connect()
            assert p._api_keys == {"glassnode": "glass_key"}

    def test_connect_calls_service_secret(self):
        p = OnchainProvider()
        calls = []

        def _spy_secret(key, service, required=True):
            calls.append((key, service))
            return ""

        with patch("zephyr.data.implementations.onchain_provider.get_service_secret", side_effect=_spy_secret):
            p.connect()
        assert ("GLASSNODE_API_KEY", "glassnode") in calls
        assert ("CRYPTOQUANT_API_KEY", "cryptoquant") in calls

    def test_health_check_mock_mode(self):
        p = OnchainProvider()
        p._api_keys = {}
        assert p.health_check() is True

    def test_health_check_live_success(self):
        p = OnchainProvider()
        p._api_keys = {"glassnode": "k"}
        with patch.object(p, "_http_get", return_value=_mock_live_response(1)):
            assert p.health_check() is True

    def test_health_check_live_failure(self):
        p = OnchainProvider()
        p._api_keys = {"glassnode": "k"}
        with patch.object(p, "_http_get", side_effect=Exception("network error")):
            assert p.health_check() is False

    def test_disconnect(self):
        p = OnchainProvider()
        p._connected = True
        p.disconnect()
        assert p._connected is False


class TestOnchainProviderFetchRoute:
    """fetch 路由测试。"""

    def test_fetch_not_connected(self):
        p = OnchainProvider()
        results = list(p.fetch(_make_payload("exchange_netflow"), None))
        assert len(results) == 1
        assert results[0].error == "onchain 未连接"

    def test_fetch_unsupported_capability(self):
        p = OnchainProvider()
        p._connected = True
        results = list(p.fetch(_make_payload("mvrv_zscore"), None))
        assert len(results) == 1
        assert "unsupported capability" in results[0].error

    def test_fetch_no_symbols(self):
        p = OnchainProvider()
        p._connected = True
        results = list(p.fetch(_make_payload("exchange_netflow", symbols=None), None))
        assert len(results) == 1
        assert "必须显式传 symbols" in results[0].error


class TestOnchainProviderMockSeries:
    """mock 序列测试（无付费 key 场景）。"""

    def _make_provider(self) -> OnchainProvider:
        p = OnchainProvider()
        p._connected = True
        p._api_keys = {}
        return p

    def test_mock_rows_count(self):
        p = self._make_provider()
        results = list(p.fetch(_make_payload("exchange_netflow"), None))
        assert len(results) == 1
        r = results[0]
        assert r.error is None
        assert len(r.rows) == 3  # 2023-09-01 ~ 2023-09-03

    def test_mock_row_format(self):
        p = self._make_provider()
        results = list(p.fetch(_make_payload("active_addresses"), None))
        row = results[0].rows[0]
        assert len(row) == len(_ONCHAIN_COLUMNS)
        assert row[0] == "active_addresses"  # metric
        assert row[1] == "BTC"  # asset
        assert row[2] == "2023-09-01"  # trade_date
        assert isinstance(row[3], float)  # value
        assert row[4] == "glassnode"  # source
        assert row[5] == 1  # is_mock

    def test_mock_deterministic(self):
        p = self._make_provider()
        r1 = list(p.fetch(_make_payload("exchange_netflow"), None))[0]
        r2 = list(p.fetch(_make_payload("exchange_netflow"), None))[0]
        assert r1.rows == r2.rows

    def test_mock_stablecoin_source(self):
        p = self._make_provider()
        results = list(p.fetch(_make_payload("stablecoin_flows", symbols=["USDT"]), None))
        assert results[0].rows[0][4] == "cryptoquant"
        assert results[0].rows[0][5] == 1

    def test_mock_last_key(self):
        p = self._make_provider()
        results = list(p.fetch(_make_payload("exchange_netflow"), None))
        assert results[0].last_key == "2023-09-03"


class TestOnchainProviderLiveFetch:
    """真实端点测试（付费 key 已配置场景，mock HTTP 层）。"""

    def _make_provider(self, service: str = "glassnode") -> OnchainProvider:
        p = OnchainProvider()
        p._connected = True
        p._api_keys = {service: "test_key"}
        return p

    def test_live_fetch_basic(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_live_response(3)):
            results = list(p.fetch(_make_payload("exchange_netflow"), None))
            assert len(results) == 1
            r = results[0]
            assert r.error is None
            assert len(r.rows) == 3
            row = r.rows[0]
            assert row[0] == "exchange_netflow"
            assert row[2] == "2023-09-01"
            assert row[3] == 100.0
            assert row[4] == "glassnode"
            assert row[5] == 0  # is_mock=0 真实数据

    def test_live_fetch_network_error(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            results = list(p.fetch(_make_payload("exchange_netflow"), None))
            assert len(results) == 1
            assert "glassnode API 请求失败" in results[0].error

    def test_live_fetch_bad_format(self):
        p = self._make_provider()
        bad_resp = MagicMock()
        bad_resp.json.return_value = {"error": "invalid api key"}
        with patch.object(p, "_call_with_policy", return_value=bad_resp):
            results = list(p.fetch(_make_payload("active_addresses"), None))
            assert len(results) == 1
            assert "响应格式异常" in results[0].error

    def test_live_fetch_cryptoquant(self):
        p = self._make_provider(service="cryptoquant")
        with patch.object(p, "_call_with_policy", return_value=_mock_live_response(2)):
            results = list(p.fetch(_make_payload("stablecoin_flows", symbols=["USDT"]), None))
            assert results[0].error is None
            assert results[0].rows[0][4] == "cryptoquant"
            assert results[0].rows[0][5] == 0

    def test_glassnode_key_does_not_leak_to_cryptoquant(self):
        """glassnode key 配置后，cryptoquant capability 仍走 mock（key 按源隔离）。"""
        p = self._make_provider(service="glassnode")
        results = list(p.fetch(_make_payload("stablecoin_flows", symbols=["USDT"]), None))
        assert results[0].rows[0][5] == 1  # is_mock=1
