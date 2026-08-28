# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_sentiment_panel_provider
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.implementations.sentiment_panel_provider
# [CONSUMERS]
# [STARTUP] pytest
# [MATURITY] skeleton
# [INVARIANTS] 公开端点 mock 不依赖网络
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-010
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] mock 异常->AssertionError
# [TESTS] self
# [A_test] module_id: MOD-L00-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""币圈宏观情绪面板 Provider 单元测试（mock HTTP 层，不依赖网络）。"""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

from zephyr.data.implementations.sentiment_panel_provider import (
    _CMC_GLOBAL_URL,
    _FNG_URL,
    _SENTIMENT_COLUMNS,
    _SKELETON_NOTES,
    SentimentPanelProvider,
)
from zephyr.data.provider_base import FetchPayload


def _mock_fng_response(count: int = 3) -> MagicMock:
    """构造 alternative.me 恐惧贪婪指数 mock 响应（时间倒序）。"""
    base_ts = 1693526400  # 2023-09-01 00:00:00 UTC
    data = []
    classifications = ["Extreme Fear", "Fear", "Neutral"]
    for i in range(count):
        ts = base_ts - i * 86400  # 每天一条，倒序
        data.append({
            "value": str(20 + i * 10),
            "value_classification": classifications[i % len(classifications)],
            "timestamp": str(ts),
        })
    resp = MagicMock()
    resp.json.return_value = {"data": data, "metadata": {"error": None}}
    return resp


def _mock_cmc_global_response() -> MagicMock:
    """构造 CMC global-metrics mock 响应。"""
    resp = MagicMock()
    resp.json.return_value = {
        "status": {"error_code": 0, "error_message": None},
        "data": {"btc_dominance": 54.321, "eth_dominance": 17.2},
    }
    return resp


def _make_payload(capability: str, table: str = "c1_alt.crypto_macro_sentiment") -> FetchPayload:
    return FetchPayload(
        table=table,
        symbols=None,
        start=datetime.date(2023, 8, 30),
        end=datetime.date(2023, 9, 1),
        extra={"capability": capability},
    )


class TestSentimentPanelProviderMeta:
    """元数据声明验证。"""

    def test_source_name(self):
        p = SentimentPanelProvider()
        assert p.source_name == "crypto_sentiment_panel"

    def test_meta_name(self):
        assert SentimentPanelProvider.meta.name == "crypto_sentiment_panel"

    def test_meta_capabilities(self):
        caps = SentimentPanelProvider.meta.capabilities_as_strings()
        assert "crypto_fear_greed_index" in caps
        assert "crypto_btc_dominance" in caps
        assert "crypto_etf_flow" in caps
        assert "crypto_usdt_premium" in caps

    def test_capability_contract_market(self):
        for cap in ("crypto_fear_greed_index", "crypto_btc_dominance", "crypto_etf_flow", "crypto_usdt_premium"):
            contract = SentimentPanelProvider.meta.get_capability_contract(cap)
            assert contract is not None
            assert contract.expected_market == "crypto"
            assert contract.expected_variety == "sentiment"

    def test_sentiment_columns(self):
        assert "metric" in _SENTIMENT_COLUMNS
        assert "trade_date" in _SENTIMENT_COLUMNS
        assert "value" in _SENTIMENT_COLUMNS
        assert "value_classification" in _SENTIMENT_COLUMNS
        assert "source" in _SENTIMENT_COLUMNS

    def test_urls(self):
        assert "alternative.me" in _FNG_URL
        assert "coinmarketcap" in _CMC_GLOBAL_URL


class TestSentimentPanelProviderLifecycle:
    """生命周期测试。"""

    def test_connect_with_cmc_key(self):
        p = SentimentPanelProvider()
        with patch("zephyr.data.implementations.sentiment_panel_provider.get_secret_or_default", return_value="test_key"):
            p.connect()
            assert p._connected is True

    def test_connect_without_cmc_key(self):
        p = SentimentPanelProvider()
        with patch("zephyr.data.implementations.sentiment_panel_provider.get_secret_or_default", return_value=""):
            p.connect()
            assert p._connected is True

    def test_health_check_success(self):
        p = SentimentPanelProvider()
        with patch.object(p, "_http_get", return_value=_mock_fng_response(1)):
            assert p.health_check() is True

    def test_health_check_failure(self):
        p = SentimentPanelProvider()
        with patch.object(p, "_http_get", side_effect=Exception("network error")):
            assert p.health_check() is False

    def test_disconnect(self):
        p = SentimentPanelProvider()
        p._connected = True
        p.disconnect()
        assert p._connected is False


class TestSentimentPanelProviderFetchRouting:
    """fetch 路由测试。"""

    def test_fetch_not_connected(self):
        p = SentimentPanelProvider()
        results = list(p.fetch(_make_payload("crypto_fear_greed_index"), None))
        assert len(results) == 1
        assert results[0].error == "crypto_sentiment_panel 未连接"

    def test_fetch_unsupported_capability(self):
        p = SentimentPanelProvider()
        p._connected = True
        results = list(p.fetch(_make_payload("unsupported"), None))
        assert len(results) == 1
        assert "unsupported capability" in results[0].error


class TestFearGreedIndex:
    """恐惧贪婪指数采集测试（alternative.me）。"""

    def _make_provider(self) -> SentimentPanelProvider:
        p = SentimentPanelProvider()
        p._connected = True
        return p

    def test_fetch_fear_greed_basic(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_fng_response(3)):
            results = list(p.fetch(_make_payload("crypto_fear_greed_index"), None))
            assert len(results) == 1
            r = results[0]
            assert r.error is None
            assert len(r.rows) == 3
            row = r.rows[0]
            assert row[0] == "fear_greed_index"  # metric
            assert row[1] == "2023-09-01"  # trade_date
            assert isinstance(row[2], float)  # value
            assert row[2] == 20.0
            assert row[3] == "Extreme Fear"  # classification
            assert row[4] == "alternative.me"  # source
            assert r.last_key == "2023-09-01"

    def test_fetch_fear_greed_date_filter(self):
        """超出 start/end 区间的条目被过滤。"""
        p = self._make_provider()
        resp = MagicMock()
        resp.json.return_value = {
            "data": [
                {"value": "50", "value_classification": "Neutral", "timestamp": "1693526400"},  # 2023-09-01 在区间
                {"value": "40", "value_classification": "Fear", "timestamp": "1691798400"},  # 2023-08-12 早于 start
            ],
            "metadata": {"error": None},
        }
        with patch.object(p, "_call_with_policy", return_value=resp):
            payload = FetchPayload(
                table="c1_alt.crypto_macro_sentiment",
                symbols=None,
                start=datetime.date(2023, 8, 30),
                end=datetime.date(2023, 9, 1),
                extra={"capability": "crypto_fear_greed_index"},
            )
            results = list(p.fetch(payload, None))
            assert len(results[0].rows) == 1
            assert results[0].rows[0][1] == "2023-09-01"

    def test_fetch_fear_greed_network_error(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            results = list(p.fetch(_make_payload("crypto_fear_greed_index"), None))
            assert len(results) == 1
            assert "alternative.me API 请求失败" in results[0].error

    def test_fetch_fear_greed_row_format(self):
        p = self._make_provider()
        with patch.object(p, "_call_with_policy", return_value=_mock_fng_response(1)):
            results = list(p.fetch(_make_payload("crypto_fear_greed_index"), None))
            row = results[0].rows[0]
            assert len(row) == len(_SENTIMENT_COLUMNS)


class TestBtcDominance:
    """BTC 占比采集测试（CoinMarketCap）。"""

    def _make_provider(self) -> SentimentPanelProvider:
        p = SentimentPanelProvider()
        p._connected = True
        return p

    def test_fetch_btc_dominance_success(self):
        p = self._make_provider()
        with patch(
            "zephyr.data.implementations.sentiment_panel_provider.get_secret_or_default",
            return_value="test_cmc_key",
        ), patch.object(p, "_call_with_policy", return_value=_mock_cmc_global_response()):
            results = list(p.fetch(_make_payload("crypto_btc_dominance"), None))
            assert len(results) == 1
            r = results[0]
            assert r.error is None
            assert len(r.rows) == 1
            row = r.rows[0]
            assert row[0] == "btc_dominance"
            assert row[2] == 54.321
            assert row[4] == "coinmarketcap"
            assert r.last_key == row[1]  # last_key=当日日期

    def test_fetch_btc_dominance_no_api_key(self):
        p = self._make_provider()
        with patch(
            "zephyr.data.implementations.sentiment_panel_provider.get_secret_or_default",
            return_value="",
        ):
            results = list(p.fetch(_make_payload("crypto_btc_dominance"), None))
            assert len(results) == 1
            assert "CMC_API_KEY 未配置" in results[0].error

    def test_fetch_btc_dominance_api_error(self):
        p = self._make_provider()
        error_resp = MagicMock()
        error_resp.json.return_value = {
            "status": {"error_code": 401, "error_message": "Invalid API key"},
        }
        with patch(
            "zephyr.data.implementations.sentiment_panel_provider.get_secret_or_default",
            return_value="bad_key",
        ), patch.object(p, "_call_with_policy", return_value=error_resp):
            results = list(p.fetch(_make_payload("crypto_btc_dominance"), None))
            assert len(results) == 1
            assert "CMC API 错误" in results[0].error

    def test_fetch_btc_dominance_network_error(self):
        p = self._make_provider()
        with patch(
            "zephyr.data.implementations.sentiment_panel_provider.get_secret_or_default",
            return_value="test_cmc_key",
        ), patch.object(p, "_call_with_policy", side_effect=Exception("timeout")):
            results = list(p.fetch(_make_payload("crypto_btc_dominance"), None))
            assert len(results) == 1
            assert "CMC API 请求失败" in results[0].error


class TestSkeletonCapabilities:
    """骨架能力测试（ETF 流量 / USDT 场外溢价——数据源待接入）。"""

    def _make_provider(self) -> SentimentPanelProvider:
        p = SentimentPanelProvider()
        p._connected = True
        return p

    def test_etf_flow_skeleton(self):
        p = self._make_provider()
        results = list(p.fetch(_make_payload("crypto_etf_flow"), None))
        assert len(results) == 1
        r = results[0]
        assert r.rows == []
        assert r.columns == _SENTIMENT_COLUMNS
        assert "骨架" in r.error
        assert r.error == _SKELETON_NOTES["crypto_etf_flow"]

    def test_usdt_premium_skeleton(self):
        p = self._make_provider()
        results = list(p.fetch(_make_payload("crypto_usdt_premium"), None))
        assert len(results) == 1
        r = results[0]
        assert r.rows == []
        assert r.columns == _SENTIMENT_COLUMNS
        assert "骨架" in r.error
        assert r.error == _SKELETON_NOTES["crypto_usdt_premium"]

    def test_skeleton_notes_cover_both(self):
        assert "crypto_etf_flow" in _SKELETON_NOTES
        assert "crypto_usdt_premium" in _SKELETON_NOTES
