# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_crypto_universe_selector
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.crypto_universe_selector
# [CONSUMERS]
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] mock http_get 不依赖网络；覆盖主路径/兜底/阈值/排除/参数校验
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/95_crypto_system_blueprint.md §3.1
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] mock 异常->AssertionError
# [TESTS] self
# [A_test] module_id: MOD-L00-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""条件选币（市值前 20 框架）单元测试（mock HTTP 层，不依赖网络）。"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from zephyr.data.implementations.crypto_universe_selector import (
    DEFAULT_EXCLUDE_SYMBOLS,
    DEFAULT_STATIC_UNIVERSE,
    DEFAULT_TOP_N,
    SOURCE_CMC,
    SOURCE_STATIC,
    CryptoUniverseEntry,
    CryptoUniverseSelector,
)


def _mock_cmc_response(symbols_ranks: list[tuple[str, int]]) -> MagicMock:
    """构造 CMC listings mock 响应（[(symbol, cmc_rank)]，已按市值降序）。"""
    resp = MagicMock()
    resp.json.return_value = {
        "status": {"error_code": 0, "error_message": None},
        "data": [{"symbol": s, "cmc_rank": r, "name": s} for s, r in symbols_ranks],
    }
    return resp


def _make_cmc_fixture(count: int = 25) -> list[tuple[str, int]]:
    """默认 CMC 夹具：COIN1..COIN{count}（rank 1..count，无稳定币）。"""
    return [(f"COIN{i}", i) for i in range(1, count + 1)]


class TestSelectStaticPath:
    """静态配置路径（无 API key）。"""

    def test_no_key_uses_static_default_universe(self):
        sel = CryptoUniverseSelector(api_key="")
        result = sel.select()
        assert result.source == SOURCE_STATIC
        assert result.degraded is False  # 无 key 直走静态=正常配置路径
        assert result.api_error == ""
        assert result.top_n == DEFAULT_TOP_N
        assert len(result.entries) == DEFAULT_TOP_N
        assert all(e.source == SOURCE_STATIC for e in result.entries)

    def test_static_default_first_is_btc(self):
        result = CryptoUniverseSelector(api_key="").select()
        first = result.entries[0]
        assert first.symbol == "BTC"
        assert first.market_cap_rank == 1
        assert isinstance(first, CryptoUniverseEntry)

    def test_static_matches_default_snapshot_order(self):
        result = CryptoUniverseSelector(api_key="").select()
        assert [(e.symbol, e.market_cap_rank) for e in result.entries] == list(DEFAULT_STATIC_UNIVERSE)

    def test_static_excludes_stablecoins_from_snapshot(self):
        snapshot = (("BTC", 1), ("USDT", 2), ("ETH", 3))
        result = CryptoUniverseSelector(api_key="", static_universe=snapshot).select()
        assert [e.symbol for e in result.entries] == ["BTC", "ETH"]

    def test_static_custom_top_n_truncates(self):
        result = CryptoUniverseSelector(api_key="", top_n=3).select()
        assert len(result.entries) == 3
        assert [e.symbol for e in result.entries] == ["BTC", "ETH", "XRP"]

    def test_static_top_n_exceeds_snapshot_returns_all(self):
        snapshot = (("BTC", 1), ("ETH", 2))
        result = CryptoUniverseSelector(api_key="", top_n=20, static_universe=snapshot).select()
        assert len(result.entries) == 2


class TestSelectCmcPath:
    """CMC 主路径（注入 mock http_get）。"""

    def test_cmc_success_returns_ranked_entries(self):
        sel = CryptoUniverseSelector(
            api_key="test-key",
            http_get=lambda *a, **kw: _mock_cmc_response(_make_cmc_fixture()),
        )
        result = sel.select()
        assert result.source == SOURCE_CMC
        assert result.degraded is False
        assert len(result.entries) == DEFAULT_TOP_N
        assert result.entries[0] == CryptoUniverseEntry(symbol="COIN1", market_cap_rank=1, source=SOURCE_CMC)

    def test_cmc_filters_stablecoins_and_refills_to_top_n(self):
        # 榜单前两位是稳定币 → 排除后仍须凑满 top_n（多拉取量兜底）
        fixture = [("USDT", 1), ("USDC", 2)] + [(f"COIN{i}", i + 2) for i in range(1, 26)]
        sel = CryptoUniverseSelector(
            api_key="k",
            top_n=5,
            http_get=lambda *a, **kw: _mock_cmc_response(fixture),
        )
        result = sel.select()
        assert [e.symbol for e in result.entries] == ["COIN1", "COIN2", "COIN3", "COIN4", "COIN5"]
        # cmc_rank 保留全榜真实名次
        assert result.entries[0].market_cap_rank == 3

    def test_cmc_exclude_override_disable(self):
        fixture = [("USDT", 1), ("BTC", 2)] + _make_cmc_fixture(25)
        sel = CryptoUniverseSelector(
            api_key="k",
            top_n=2,
            exclude_symbols=frozenset(),
            http_get=lambda *a, **kw: _mock_cmc_response(fixture),
        )
        result = sel.select()
        assert [e.symbol for e in result.entries] == ["USDT", "BTC"]

    def test_cmc_default_exclude_set_covers_known_stables(self):
        assert {"USDT", "USDC", "DAI", "WBTC", "STETH"} <= DEFAULT_EXCLUDE_SYMBOLS

    def test_cmc_http_failure_falls_back_static_degraded(self):
        def _boom(*a, **kw):
            raise ConnectionError("network down")

        result = CryptoUniverseSelector(api_key="k", http_get=_boom).select()
        assert result.source == SOURCE_STATIC
        assert result.degraded is True
        assert "network down" in result.api_error
        assert len(result.entries) == DEFAULT_TOP_N

    def test_cmc_api_error_code_falls_back_degraded(self):
        resp = MagicMock()
        resp.json.return_value = {"status": {"error_code": 401, "error_message": "invalid key"}, "data": None}
        result = CryptoUniverseSelector(api_key="bad", http_get=lambda *a, **kw: resp).select()
        assert result.degraded is True
        assert result.source == SOURCE_STATIC
        assert "invalid key" in result.api_error

    def test_cmc_malformed_payload_falls_back_degraded(self):
        resp = MagicMock()
        resp.json.return_value = {"status": {"error_code": 0}}  # 缺 data
        result = CryptoUniverseSelector(api_key="k", http_get=lambda *a, **kw: resp).select()
        assert result.degraded is True
        assert result.source == SOURCE_STATIC

    def test_cmc_entry_missing_rank_falls_back_degraded(self):
        resp = MagicMock()
        resp.json.return_value = {
            "status": {"error_code": 0},
            "data": [{"symbol": "BTC"}],  # 缺 cmc_rank
        }
        result = CryptoUniverseSelector(api_key="k", http_get=lambda *a, **kw: resp).select()
        assert result.degraded is True

    def test_cmc_empty_after_exclusion_falls_back_degraded(self):
        fixture = [("USDT", 1), ("USDC", 2)]
        result = CryptoUniverseSelector(
            api_key="k",
            http_get=lambda *a, **kw: _mock_cmc_response(fixture),
        ).select()
        assert result.degraded is True
        assert result.source == SOURCE_STATIC


class TestValidation:
    """参数校验（fail-closed）。"""

    def test_top_n_zero_raises(self):
        with pytest.raises(ValueError, match="top_n"):
            CryptoUniverseSelector(top_n=0)

    def test_top_n_negative_raises(self):
        with pytest.raises(ValueError, match="top_n"):
            CryptoUniverseSelector(top_n=-5)

    def test_result_as_of_is_iso_date(self):
        result = CryptoUniverseSelector(api_key="").select()
        assert len(result.as_of) == 10 and result.as_of[4] == "-"

    def test_custom_top_n(self):
        sel = CryptoUniverseSelector(api_key="", top_n=7)
        assert sel.top_n == 7
        assert len(sel.select().entries) == 7
