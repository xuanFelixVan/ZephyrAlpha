# [BLUEPRINT] MOD-DATA_GOV-014 | docs/03_modules/_domain_data_governance/asset_auto_discovery/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_governance.test_asset_auto_discovery
# [TESTS] src/zephyr/data_governance/asset_auto_discovery.py
"""MOD-DATA_GOV-014 单元测试：asset_auto_discovery 数据资产自动发现器。

蓝图验收（B10-02326/CAND-DATGOV-011，A1 M8-NEW-07）：
三类 scanner 注入（ClickHouse表/因子注册表/信号注册表）+ 资产卡片生成
（asset_id/类型/owner/更新频率/质量分默认）+ 注册表回调 + 指纹 diff 增量
（只更新变更）。scanner/registry_sink/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_governance.asset_auto_discovery",
    reason="asset_auto_discovery not importable",
)

from zephyr.data_governance.asset_auto_discovery import (  # noqa: E402
    AssetAutoDiscovery,
    AssetCard,
    AssetDiscoveryError,
    AssetType,
    RawAssetInfo,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _ch_tables() -> list[RawAssetInfo]:
    return [RawAssetInfo("ch.market.kline", owner="data", update_frequency="1d", attributes={"rows": "1000"})]


def _factors() -> list[RawAssetInfo]:
    return [RawAssetInfo("factor.mom20", owner="quant", update_frequency="1d")]


def _signals() -> list[RawAssetInfo]:
    return [RawAssetInfo("signal.alpha", owner="quant", update_frequency="1h")]


def _discovery(registered: list | None = None, **kw) -> AssetAutoDiscovery:
    d = AssetAutoDiscovery(
        clock=lambda: _T0,
        registry_sink=registered.append if registered is not None else None,
        **kw,
    )
    d.register_scanner(AssetType.CLICKHOUSE_TABLE, _ch_tables)
    d.register_scanner(AssetType.FACTOR, _factors)
    d.register_scanner(AssetType.SIGNAL, _signals)
    return d


# ──────────────────────────────────────────────────────────────────────────────
# 构造与 scanner 注册
# ──────────────────────────────────────────────────────────────────────────────


class TestInitAndRegister:
    def test_quality_score_out_of_range_raises(self) -> None:
        with pytest.raises(AssetDiscoveryError):
            AssetAutoDiscovery(default_quality_score=1.5)
        with pytest.raises(AssetDiscoveryError):
            AssetAutoDiscovery(default_quality_score=-0.1)

    def test_vocab_outside_type_raises(self) -> None:
        d = AssetAutoDiscovery()
        with pytest.raises(AssetDiscoveryError):
            d.register_scanner("parquet_file", lambda: [])  # type: ignore[arg-type]

    def test_non_callable_scanner_raises(self) -> None:
        d = AssetAutoDiscovery()
        with pytest.raises(AssetDiscoveryError):
            d.register_scanner(AssetType.FACTOR, "not-a-fn")  # type: ignore[arg-type]

    def test_duplicate_scanner_type_raises(self) -> None:
        d = _discovery()
        with pytest.raises(AssetDiscoveryError):
            d.register_scanner(AssetType.FACTOR, _factors)

    def test_run_without_scanner_raises(self) -> None:
        d = AssetAutoDiscovery()
        with pytest.raises(AssetDiscoveryError):
            d.run()


# ──────────────────────────────────────────────────────────────────────────────
# 卡片生成
# ──────────────────────────────────────────────────────────────────────────────


class TestCardGeneration:
    def test_cards_for_three_types(self) -> None:
        report = _discovery().run()
        types = {c.asset_id: c.asset_type for c in report.cards}
        assert types == {
            "ch.market.kline": AssetType.CLICKHOUSE_TABLE,
            "factor.mom20": AssetType.FACTOR,
            "signal.alpha": AssetType.SIGNAL,
        }

    def test_card_fields_and_default_quality(self) -> None:
        report = _discovery(default_quality_score=0.8).run()
        card = next(c for c in report.cards if c.asset_id == "factor.mom20")
        assert card.owner == "quant"
        assert card.update_frequency == "1d"
        assert card.quality_score == 0.8
        assert card.fingerprint
        assert card.discovered_at == _T0

    def test_run_at_from_clock(self) -> None:
        report = _discovery().run()
        assert report.run_at == _T0

    def test_empty_asset_id_raises(self) -> None:
        d = AssetAutoDiscovery(clock=lambda: _T0)
        d.register_scanner(AssetType.FACTOR, lambda: [RawAssetInfo("")])
        with pytest.raises(AssetDiscoveryError):
            d.run()

    def test_scanner_exception_wrapped(self) -> None:
        d = AssetAutoDiscovery(clock=lambda: _T0)
        d.register_scanner(AssetType.SIGNAL, lambda: (_ for _ in ()).throw(OSError("ch down")))
        with pytest.raises(AssetDiscoveryError):
            d.run()

    def test_multiple_assets_per_scanner(self) -> None:
        d = AssetAutoDiscovery(clock=lambda: _T0)
        d.register_scanner(AssetType.FACTOR, lambda: [RawAssetInfo("f1"), RawAssetInfo("f2")])
        report = d.run()
        assert report.added == ("f1", "f2")


# ──────────────────────────────────────────────────────────────────────────────
# 指纹与增量 diff
# ──────────────────────────────────────────────────────────────────────────────


class TestFingerprintDiff:
    def test_fingerprint_deterministic_order_insensitive(self) -> None:
        a = RawAssetInfo("x", attributes={"k1": "v1", "k2": "v2"})
        b = RawAssetInfo("x", attributes={"k2": "v2", "k1": "v1"})
        assert AssetAutoDiscovery.fingerprint_of(a) == AssetAutoDiscovery.fingerprint_of(b)
        c = RawAssetInfo("x", attributes={"k1": "v9", "k2": "v2"})
        assert AssetAutoDiscovery.fingerprint_of(a) != AssetAutoDiscovery.fingerprint_of(c)

    def test_first_run_all_added_and_sink_called(self) -> None:
        registered: list[AssetCard] = []
        report = _discovery(registered).run()
        assert report.added == ("ch.market.kline", "factor.mom20", "signal.alpha")
        assert len(registered) == 3

    def test_identical_second_run_all_unchanged_sink_silent(self) -> None:
        registered: list[AssetCard] = []
        d = _discovery(registered)
        d.run()
        registered.clear()
        report = d.run()
        assert report.unchanged == ("ch.market.kline", "factor.mom20", "signal.alpha")
        assert report.added == () and report.updated == ()
        assert registered == []  # 指纹 diff：无变更不推注册表

    def test_changed_attribute_updated_and_pushed(self) -> None:
        registered: list[AssetCard] = []
        d = AssetAutoDiscovery(clock=lambda: _T0, registry_sink=registered.append)
        state = {"rows": "1000"}
        d.register_scanner(
            AssetType.CLICKHOUSE_TABLE, lambda: [RawAssetInfo("ch.market.kline", attributes={"rows": state["rows"]})]
        )
        d.run()
        registered.clear()
        state["rows"] = "2000"
        report = d.run()
        assert report.updated == ("ch.market.kline",)
        assert len(registered) == 1
        assert registered[0].fingerprint == report.cards[0].fingerprint

    def test_new_asset_added_on_second_run(self) -> None:
        d = AssetAutoDiscovery(clock=lambda: _T0)
        assets = [RawAssetInfo("f1")]
        d.register_scanner(AssetType.FACTOR, lambda: list(assets))
        d.run()
        assets.append(RawAssetInfo("f2"))
        report = d.run()
        assert report.added == ("f2",)
        assert report.unchanged == ("f1",)

    def test_sink_exception_wrapped(self) -> None:
        def bad_sink(card: AssetCard) -> None:
            raise OSError("registry down")

        d = AssetAutoDiscovery(clock=lambda: _T0, registry_sink=bad_sink)
        d.register_scanner(AssetType.FACTOR, _factors)
        with pytest.raises(AssetDiscoveryError):
            d.run()

    def test_report_sorted_deterministic(self) -> None:
        d = AssetAutoDiscovery(clock=lambda: _T0)
        d.register_scanner(AssetType.FACTOR, lambda: [RawAssetInfo("z.f"), RawAssetInfo("a.f"), RawAssetInfo("m.f")])
        report = d.run()
        assert report.added == ("a.f", "m.f", "z.f")
        assert [c.asset_id for c in report.cards] == ["a.f", "m.f", "z.f"]
