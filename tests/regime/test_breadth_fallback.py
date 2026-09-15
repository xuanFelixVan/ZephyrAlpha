# [A_test] module_id: MOD-TEST-BREADTH-FB | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §5 _load_breadth FPB-1
# [MODULE] tests.regime.test_breadth_fallback
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.regime_feature_builder; pandas
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_breadth_fallback.py
# [A_module] module_id: MOD-TEST-BREADTH-FB | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #FPB-1 #docs/_working/full-auto-chain/S11_assembled_backtest/nodes/feature_pipeline_mining.md
# 覆盖：regime_feature_builder._load_breadth 的 EQW_ALLA 补洞逻辑（FPB-1）
"""_load_breadth 广度补洞单测（FPB-1，2026-09-15）。

399106 涨跌家数 2026-07-03 起结构性断更，无数据日回退 kline_index_calc
EQW_ALLA（全 A 家数）。本测试用 fake index_df + monkeypatch _safe_query
验证三场景：断更补位 / 全量有效不触发 fallback / fallback 失败维持 0 填充旧行为。
"""

from __future__ import annotations

import pandas as pd
import pytest

from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder


def _make_index_df(adv_dec_399106: list[tuple[float, float]]) -> pd.DataFrame:
    """构造 2 symbol × 3 日的 fake index_df（000300 代理 + 399106 广度）。"""
    dates = pd.to_datetime(["2026-09-01", "2026-09-02", "2026-09-03"])
    rows = []
    for d in dates:
        rows.append({"symbol": "000300", "trade_date": d, "close": 4000.0, "volume": 1e8,
                     "advance_count": 0, "decline_count": 0})
    for i, (a, dec) in enumerate(adv_dec_399106):
        rows.append({"symbol": "399106", "trade_date": dates[i], "close": 2000.0, "volume": 1e8,
                     "advance_count": a, "decline_count": dec})
    df = pd.DataFrame(rows)
    return df.set_index(["symbol", "trade_date"]).sort_index()


def _make_builder(monkeypatch: pytest.MonkeyPatch, tsv: str | None) -> RegimeFeatureBuilder:
    b = RegimeFeatureBuilder(backtest_start="2026-09-01", backtest_end="2026-09-03",
                             data_load_start="2026-01-01")
    monkeypatch.setattr(b, "_safe_query", lambda sql, context="": tsv or "")
    return b


def test_dead_days_filled_from_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """399106 后两日断更 → 由 EQW_ALLA 补位；首日有效值保持不变。"""
    index_df = _make_index_df([(1500.0, 1200.0), (0.0, 0.0), (0.0, 0.0)])
    # fallback TSV：EQW_ALLA 三日全 A 家数（首日数据无关紧要，仅死日被消费）
    tsv = "2026-09-01\t3000\t2400\n2026-09-02\t2800\t2300\n2026-09-03\t3100\t2100\n"
    b = _make_builder(monkeypatch, tsv)
    adv, dec = b._load_breadth(index_df)
    assert adv.iloc[0] == 1500.0  # 399106 有效日保持原值（补洞不覆盖）
    assert dec.iloc[0] == 1200.0
    assert adv.iloc[1] == 2800.0 and dec.iloc[1] == 2300.0  # 死日 → EQW_ALLA
    assert adv.iloc[2] == 3100.0 and dec.iloc[2] == 2100.0


def test_no_fallback_when_all_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """399106 全量有效 → 不触发 fallback（查询不被调用，历史行为零破坏）。"""
    index_df = _make_index_df([(1500.0, 1200.0), (1600.0, 1100.0), (1700.0, 1000.0)])

    def _boom(sql: str, context: str = "") -> str:
        raise AssertionError("全量有效时不应触发 fallback 查询")

    b = _make_builder(monkeypatch, "")
    monkeypatch.setattr(b, "_safe_query", _boom)
    adv, dec = b._load_breadth(index_df)
    assert list(adv) == [1500.0, 1600.0, 1700.0]
    assert list(dec) == [1200.0, 1100.0, 1000.0]


def test_fallback_failure_keeps_legacy_zero_fill(monkeypatch: pytest.MonkeyPatch) -> None:
    """fallback 查询失败/为空 → 维持 0 填充旧行为（降级不抛错）。"""
    index_df = _make_index_df([(1500.0, 1200.0), (0.0, 0.0), (0.0, 0.0)])
    b = _make_builder(monkeypatch, "")  # 空 TSV = 无补洞数据
    adv, dec = b._load_breadth(index_df)
    assert list(adv) == [1500.0, 0.0, 0.0]
    assert list(dec) == [1200.0, 0.0, 0.0]
