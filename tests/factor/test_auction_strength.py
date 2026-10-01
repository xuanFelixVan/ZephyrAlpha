# [TTL] permanent
"""auction_strength 证尺（CNS-11，SW14 2026-09-29）——tmp 合成帧+fake conn 零 CH。

- 输入装配：rise_pct 口径（涨幅%）、量比 5 日基线 PIT（严格前序日）、缺昨收/缺基线=None；
- 打分委托：真源=youzi 引擎 score_auction_strength（数值对拍）；缺输入=None 不拍 0。
"""

from __future__ import annotations

import pandas as pd

from zephyr.factor.auction_strength import (
    _BASELINE_DAYS,
    attach_scores,
    auction_strength_score,
    fetch_auction_inputs,
)

_D1, _D2, _D3, _D4, _D5, _D6, _D7 = (
    "2026-08-03",
    "2026-08-04",
    "2026-08-05",
    "2026-08-06",
    "2026-08-07",
    "2026-08-10",
    "2026-08-11",
)


class _FakeConn:
    """双查询替身：snapshot 行 + book pre_close 聚合行（零 CH）。"""

    def __init__(self, snap_rows, pre_rows):
        self.snap_rows = snap_rows
        self.pre_rows = pre_rows

    def execute(self, sql: str):  # noqa: A003 — DI 缝位同形
        if "auction_snapshot" in sql:
            return list(self.snap_rows)
        if "auction_book" in sql:
            return list(self.pre_rows)
        raise AssertionError(f"未知查询路由: {sql[:60]}")


def _snap_rows():
    # S1：量 100→200→300→400→500→600（第 6 日量比=600/均值(200..600 前5个前序)/…）
    rows = []
    vols = {  # symbol -> {day: (price, volume)}
        "S1": {
            _D1: (10.0, 100),
            _D2: (10.2, 200),
            _D3: (10.4, 300),
            _D4: (10.6, 400),
            _D5: (10.8, 500),
            _D6: (11.0, 600),
        },
        "S2": {_D6: (20.0, 1000)},  # 只 1 日：基线不足→量比 None
    }
    for sym, days in vols.items():
        for d, (p, v) in days.items():
            rows.append((d, sym, p, v, p * v))
    return rows


def _pre_rows():
    return [
        (_D1, "S1", 10.0),
        (_D2, "S1", 10.0),
        (_D3, "S1", 10.2),
        (_D4, "S1", 10.4),
        (_D5, "S1", 10.6),
        (_D6, "S1", 10.8),
        (_D6, "S2", 20.0),
        (_D6, "S3", 0.0),  # 零昨收→rise None（禁除零）
    ]


def _snap_with_s3():
    return _snap_rows() + [(_D6, "S3", 9.9, 800, 7920.0)]


def test_rise_pct_and_ratio_assembly():
    conn = _FakeConn(_snap_with_s3(), _pre_rows())
    df = fetch_auction_inputs(_D1, _D6, conn=conn)
    by = {(r["symbol"], r["trade_date"]): r for _, r in df.iterrows()}
    # S1 @D6：pre_close=10.8, price=11.0 → +1.8519%；量比=600/mean(200,300,400,500,前一日100?…)
    r = by[("S1", _D6)]
    assert r["auction_rise_pct"] == (11.0 / 10.8 - 1) * 100
    # D1..D5 的前序量序列（≤5 个）不足 min_periods=5 → 前 5 日 None，D6 恰好用满 5 个前序
    assert by[("S1", _D4)]["auction_volume_ratio"] is None
    prev5 = [100, 200, 300, 400, 500]
    assert r["auction_volume_ratio"] == 600 / (sum(prev5) / _BASELINE_DAYS)
    # S2 单日：基线不足 → None；S3 零昨收 → rise None
    assert by[("S2", _D6)]["auction_volume_ratio"] is None
    assert by[("S3", _D6)]["auction_rise_pct"] is None


def test_score_delegates_to_youzi_engine():
    from zephyr.signal_ashare.limit_up.youzi_relay_emotion_engine import YouziRelayEmotionEngine

    fs = YouziRelayEmotionEngine().score_auction_strength(6.0, 3.0)
    out = auction_strength_score(6.0, 3.0)
    assert out["score"] == float(fs.score) and out["max"] == float(fs.max_score)
    # 高开+放量=满分档；缺输入=None（禁拍 0 冒充弱）
    assert auction_strength_score(6.0, 3.0)["score"] == 10.0
    assert auction_strength_score(None, 3.0)["score"] is None


def test_attach_scores_column_contract():
    conn = _FakeConn(_snap_with_s3(), _pre_rows())
    df = attach_scores(fetch_auction_inputs(_D1, _D6, conn=conn))
    assert {"auction_strength_score", "score_max", "score_detail"} <= set(df.columns)
    assert df["auction_strength_score"].isna().sum() >= 1  # 缺输入行如实 None
    assert df["auction_strength_score"].notna().sum() >= 1
