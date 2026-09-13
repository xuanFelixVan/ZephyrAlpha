# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §alt-regime
# [TTL] permanent
"""AltRegimeSignalProvider 单测——纯函数核 + stub 注入全链路（不依赖 CH/网络，FAIL-FAST）。

C-1 消费端首批（2026-09-14，docs/_working/alt_data_consumption_plan.md §7.3）。
"""
from __future__ import annotations

import sys
import types

import pandas as pd
import pytest

from zephyr.alt_data.alt_regime_signals import (
    _ALT_REGIME_CAPABILITIES,
    AltRegimeSignalProvider,
    fng_state,
    limitup_emotion_phase,
    limitup_streaks,
    momentum_zscore,
    ret_state,
    z_state,
)
from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import FetchPayload


# ---------- 纯函数核 ----------

def _series(values, index=None):
    return pd.Series(values, index=index or [f"2026-01-{i+1:02d}" for i in range(len(values))])


def test_momentum_zscore_warmup_and_value():
    s = _series([100.0] * 300)  # 常数序列 -> 动量 0、std 0
    z = momentum_zscore(s)
    assert z.iloc[280:].isna().all() or (z.iloc[280:] == 0).all()  # 常数序列 z=0 或 NaN
    varied = _series(list(range(300)), index=[f"d{i}" for i in range(300)])
    z2 = momentum_zscore(varied)
    assert z2.iloc[272:].notna().all()  # 暖机期后全有值
    assert z2.iloc[:270].isna().all()  # 暖机期内 NaN


def test_state_bands():
    assert z_state(1.5) == "risk_on"
    assert z_state(-1.2) == "risk_off"
    assert z_state(0.3) == "neutral"
    assert z_state(float("nan")) == "warmup"
    assert ret_state(5.0) == "risk_on"
    assert ret_state(-0.1) == "risk_off"
    assert fng_state(15) == "extreme_fear"
    assert fng_state(30) == "fear"
    assert fng_state(50) == "neutral"
    assert fng_state(70) == "greed"
    assert fng_state(95) == "extreme_greed"


def test_limitup_streaks_progress_and_reset():
    streaks = {"A": 2, "B": 1}
    new = limitup_streaks(streaks, {"A", "C"})  # A 续板，B 断，C 新板
    assert new == {"A": 3, "C": 1}


def test_limitup_phase_thresholds():
    assert limitup_emotion_phase(6, 0.65) == "高潮"
    assert limitup_emotion_phase(4, 0.45) == "发酵"
    assert limitup_emotion_phase(2, 0.2) == "退潮"
    assert limitup_emotion_phase(2, 0.5) == "中性"


# ---------- provider 声明与路由 ----------

def test_provider_meta():
    caps = {c.capability_id for c in AltRegimeSignalProvider.meta.capabilities}
    assert caps == _ALT_REGIME_CAPABILITIES == {"alt_regime_signal"}


def _payload(cap="alt_regime_signal") -> FetchPayload:
    return FetchPayload(
        table="c1_market.alt_regime_signal", symbols=None,
        start=None, end=None, incremental=False,
        extra={"capability": cap},
    )


def test_fetch_unknown_capability():
    p = AltRegimeSignalProvider()
    r = list(p.fetch(_payload("nope"), SourcePolicy()))[0]
    assert r.error and "unsupported" in r.error


# ---------- stub ch_reader 全链路 ----------

@pytest.fixture()
def stub_ch_reader(monkeypatch):
    """_compute_all_signals 内 `from zephyr.data import ch_reader` 的 stub 注入。"""
    import zephyr.data.ch_reader as cr

    def _install(queries: dict[str, str]):
        monkeypatch.setattr(cr, "query", lambda q: queries.get(q.strip(), ""), raising=False)
        return queries

    return _install


BDI_Q = "SELECT trade_date, value FROM c1_market.alt_shipping_index FINAL WHERE index_code='BDI' ORDER BY trade_date"
BTC_Q = "SELECT trade_date, close FROM c1_market.crypto_kline_daily FINAL WHERE symbol='BTCUSDT' ORDER BY trade_date"
FNG_Q = "SELECT trade_date, value FROM c1_market.sentiment_panel FINAL WHERE metric='fear_greed_index' ORDER BY trade_date"
LU_Q = "SELECT trade_date, symbol FROM c1_market.limit_up_down FINAL WHERE limit_type='涨停' ORDER BY trade_date"
LF_Q = "SELECT year, tcno, tc_cn_name, land_prov, land_lev FROM c1_market.alt_typhoon_landfall_history FINAL"
TK_Q = "SELECT toYear(parseDateTimeBestEffort(issue_ts)) AS y, tcno, min(toDate(parseDateTimeBestEffort(issue_ts))) AS first_date FROM c1_market.alt_typhoon_track FINAL WHERE tcno != '0000' GROUP BY y, tcno"


def _bdi_tsv(n=300):
    return "\n".join(f"2025-{(i//28)%12+1:02d}-{i%28+1:02d}\t{1000+i}" for i in range(n))


def test_fetch_full_chain(stub_ch_reader):
    bdi = "\n".join(f"2025-{(i//28)%12+1:02d}-{i%28+1:02d}\t{1000+i*3}" for i in range(300))
    btc = "\n".join(f"2025-{(i//28)%12+1:02d}-{i%28+1:02d}\t{50000+i*10}" for i in range(60))
    stub_ch_reader({
        BDI_Q: bdi,
        BTC_Q: btc,
        FNG_Q: "2026-09-10\t18",
        LU_Q: "2026-09-09\t000001\n2026-09-09\t000002\n2026-09-10\t000001\n2026-09-10\t000003",
        LF_Q: "2025\t9\t桦加沙\t广东\tSTY",
        TK_Q: "2025\t9\t2025-09-20",
    })
    p = AltRegimeSignalProvider()
    r = list(p.fetch(_payload(), SourcePolicy()))[0]
    assert r.error is None
    ids = {row[1] for row in r.rows}
    assert ids == {"F4_BDI_MOMENTUM_Z20", "F14_BTC_MOMENTUM_30D", "F15_FNG_INDEX",
                   "F23_LIMITUP_EMOTION", "F7_TYPHOON_EVENT"}
    f23 = [row for row in r.rows if row[1] == "F23_LIMITUP_EMOTION"]
    last = f23[-1]
    assert last[2] == 0.5  # 晋级率 = 今日{000001}∩昨日{000001,000002} / 2 = 0.5
    assert last[3] in {"中性", "退潮", "发酵", "高潮"}
    f7 = [row for row in r.rows if row[1] == "F7_TYPHOON_EVENT"][0]
    assert f7[0] == "2025-09-20" and f7[2] == 1.0 and "桦加沙" in f7[4]


def test_fetch_single_signal_failure_degrades(stub_ch_reader):
    """FNG 源表空 -> F15 缺席但其余信号正常产出（单信号降级）。"""
    stub_ch_reader({
        BDI_Q: _bdi_tsv(300),
        BTC_Q: "\n".join(f"2025-{(i//28)%12+1:02d}-{i%28+1:02d}\t{50000+i*10}" for i in range(60)),
        FNG_Q: "",
        LU_Q: "2026-09-10\t000001",
        LF_Q: "2025\t9\t桦加沙\t广东\tSTY",
        TK_Q: "2025\t9\t2025-09-20",
    })
    p = AltRegimeSignalProvider()
    r = list(p.fetch(_payload(), SourcePolicy()))[0]
    assert r.error is None  # 部分降级不算整体失败
    ids = {row[1] for row in r.rows}
    assert "F15_FNG_INDEX" not in ids
    assert "F4_BDI_MOMENTUM_Z20" in ids
