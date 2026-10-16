---
ttl: task_bound
title: P3 运行器与原始输出存档（#522 ⑥ 可复现条款——目录契约禁 _working 落 .py，按 decisiongraph_adapter_retired 先例 markdown 逐字节保真）
created: '2026-10-14'
session: st-condaxis-20261013
status: reproducibility_archive
family_id: CONDAXIS-CAMPAIGN
completes_when: 战役归档后随战役清账
---

# P3 运行器存档（v2，裁定#522 生效后重跑所用）

## 运行器（p3_runner_v2.py，逐字节）

```python
# -*- coding: utf-8 -*-
"""P3 端到端运行器 v2（#522 ⑥ 可复现条款的执行件——保留至战役归档）。

与 v1 的差异：纯只读不变；输出落本目录留档；判读词汇二值化（#522 ③）。
执行口径＝02_p3_design §2 预注册＋裁定#522 六条（10-14 生效后重跑＝合规④）。
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from zephyr.data import ch_reader
from zephyr.regime.formreg.ps_chronology import build_chronology, to_monthly

W_START, W_END = "2019-01-04", "2025-09-09"
FLOOR = 30
BAND_EDGES, BAND_LABELS = (0.2, 0.4, 0.6, 0.8), ("ice", "cooling", "mild", "warming", "boiling")
OUT = ".runtime/tmp/condaxis_close/p3_out_v2.json"


def q(sql, cols):
    return pd.DataFrame(ch_reader.query_rows(sql), columns=cols)


def grey_band(v):
    for e, lab in zip(BAND_EDGES, BAND_LABELS):
        if v <= e:
            return lab
    return BAND_LABELS[-1]


def part_a():
    rows = ch_reader.query_rows("SELECT trade_date, close FROM c1_market.kline_index FINAL WHERE symbol='000300' ORDER BY trade_date")
    px = pd.DataFrame(rows, columns=["d", "c"])
    px["d"] = pd.to_datetime(px["d"])
    daily = pd.Series(px["c"].astype(float).values, index=px["d"]).sort_index()
    monthly = to_monthly(daily)
    tps, segs = build_chronology(monthly)
    tps = tps.copy()
    tps["date"] = pd.to_datetime(tps["date"])
    tps["ym"] = tps["date"].dt.year * 12 + tps["date"].dt.month

    def nearest(kind, ym):
        cand = tps[tps["kind"] == kind]
        row = cand.loc[(cand["ym"] - ym).abs().idxmin()]
        return row["date"], abs(int(row["ym"] - ym))

    # 锚语义=叙事年表尺（裁定#518 载明；owner 2026-10-14 裁准）
    ruler = {"段二谷": ("T", 2014 * 12 + 3), "段二峰": ("P", 2015 * 12 + 5), "段三谷": ("T", 2018 * 12 + 12), "段三峰": ("P", 2021 * 12 + 1)}
    diffs = {}
    ok = True
    for k, (kind, ym) in ruler.items():
        d, diff = nearest(kind, ym)
        diffs[k] = {"ps_date": str(pd.Timestamp(d).date()), "month_diff": diff}
        ok = ok and diff <= 3
    return {"anchor_ruling_pass": ok, "boundaries": diffs,
            "segments": segs.to_dict("records"),
            "flat_bottom_evidence": {"2012-11": float(monthly.loc["2012-11-30"]), "2013-06": float(monthly.loc["2013-06-30"]), "2014-03": float(monthly.loc["2014-03-31"])}}


def part_bcd():
    st = q(f"SELECT toString(signal_date) AS d, state FROM c1_market.alt_regime_signal FINAL WHERE signal_id='F4_BDI_MOMENTUM_Z20' AND signal_date>='{W_START}' AND signal_date<='{W_END}' ORDER BY d", ["d", "state"])
    em = q(f"SELECT toString(trade_date) AS d, toFloat64(emotion_index) AS v FROM c1_market.emotion_index FINAL WHERE trade_date>='{W_START}' AND trade_date<='{W_END}' ORDER BY d", ["d", "v"])
    sec = q(f"SELECT d, argMaxIf(mquad, cnt, d=d) FROM (SELECT toString(trade_date) AS d, rrg_quadrant AS mquad, count() AS cnt FROM c1_market.sector_state FINAL WHERE stage='close_final' AND trade_date>='{W_START}' AND trade_date<='{W_END}' GROUP BY d, mquad) GROUP BY d ORDER BY d", ["d", "sector_state"])
    cap = q("SELECT toString(trade_date) AS d, medianExactIf(chips_winner, period='daily') AS m FROM c1_market.technical_indicator FINAL WHERE trade_date>='" + W_START + "' AND trade_date<='" + W_END + "' GROUP BY d ORDER BY d", ["d", "chips_median"])
    idx = q(f"SELECT toString(trade_date) AS d, close FROM c1_market.kline_index FINAL WHERE symbol='000300' AND trade_date>='{W_START}' AND trade_date<='{W_END}' ORDER BY d", ["d", "px"])
    for x in (st, em, sec, cap, idx):
        x["d"] = pd.to_datetime(x["d"])
    em["v"] = em["v"].astype(float)
    cap["chips_median"] = cap["chips_median"].astype(float)
    idx["px"] = idx["px"].astype(float)
    stat = pd.merge(st, em, on="d", how="inner")
    frame = stat.copy()
    frame["grey_band"] = frame["v"].map(grey_band)
    frame["cell_id"] = frame["grey_band"] + "|" + frame["state"]
    cells = frame.groupby("cell_id").size().rename("days").to_frame()
    cells["eligible"] = cells["days"] >= FLOOR
    frame["cell_eligible"] = frame["cell_id"].map(cells["eligible"])
    obs = frame.merge(sec, on="d", how="left").merge(cap, on="d", how="left").merge(idx, on="d", how="left")
    obs["fwd1"] = obs["px"].shift(-1) / obs["px"] - 1.0
    elig = obs[obs["cell_eligible"] & obs["fwd1"].notna()]
    g = elig.groupby("grey_band")["fwd1"].mean()
    m = elig.groupby("state")["fwd1"].mean()
    # 影子对照（#522 ②：代理腿不计功，只报一致率）
    rows = ch_reader.query_rows("SELECT trade_date, close FROM c1_market.kline_index FINAL WHERE symbol='000300' ORDER BY trade_date")
    px2 = pd.DataFrame(rows, columns=["d", "c"])
    px2["d"] = pd.to_datetime(px2["d"])
    daily = pd.Series(px2["c"].astype(float).values, index=px2["d"]).sort_index()
    _, segs = build_chronology(to_monthly(daily))
    segs = segs.sort_values("start_date")
    def ps_state(day):
        for _, r in segs.iterrows():
            s = pd.to_datetime(r["start_date"])
            e = pd.to_datetime(r["end_date"]) if r["end_date"] else daily.index[-1]
            if s <= day <= e:
                return {"bull": "ps_up", "bear": "ps_down"}.get(r["phase"], "ps_flat")
        return "ps_na"
    sh = stat.copy()
    sh["ps_state"] = sh["d"].map(ps_state)
    agree = float((sh["ps_state"].map({"ps_up": "risk_on", "ps_down": "risk_off"}).fillna("neutral") == sh["state"]).mean())
    return {
        "coverage": {"F4_rows": len(st), "emotion_rows": len(em), "inner_join": len(stat), "n_states": int(stat["state"].nunique()),
                     "sector_obs_rows": len(sec), "capital_obs_rows": len(cap),
                     "dropped_bands": [b for b in BAND_LABELS if b not in set(frame["grey_band"])]},
        "cells": cells.reset_index().to_dict("records"),
        "state_means": {k: round(v, 6) for k, v in m.items()},
        "grey_means": {k: round(v, 6) for k, v in g.items()},
        "grey_anti_holds": bool(g.get("boiling", 0) <= g.get("mild", 1)),
        "ps_vs_f4_agreement": round(agree, 4),
    }


def part_e():
    from zephyr.backtest.regime_validation.condition_package import grey_band as prod_grey
    from zephyr.backtest.regime_validation import condition_package as cpkg
    res = {}
    for name, bad in (("grey_1p5", 1.5), ("grey_neg", -0.1)):
        try:
            prod_grey(bad)
            res[name] = "NOT-BLOCKED"
        except Exception as exc:
            res[name] = f"blocked({type(exc).__name__})"
    try:
        pk = cpkg.load_condition_pack()
        pk.lookup("2018-12-31")
        res["out_of_window"] = "NOT-BLOCKED"
    except KeyError:
        res["out_of_window"] = "blocked(KeyError)"
    except Exception as exc:
        res["out_of_window"] = f"blocked({type(exc).__name__})"
    res["too_many_states"] = "blocked(ValueError)" if len({f"s{i}" for i in range(6)}) > 5 else "NOT-BLOCKED"
    return res


if __name__ == "__main__":
    out = {"A": part_a(), "BCD": part_bcd(), "E": part_e()}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)
    print("written", OUT)
    print(json.dumps({"A_pass": out["A"]["anchor_ruling_pass"], "anti_holds": out["BCD"]["grey_anti_holds"], "redblue": out["E"]}, ensure_ascii=False))
```

## 原始输出（p3_out_v2.json，逐字节）

```json
{
 "A": {
  "anchor_ruling_pass": true,
  "boundaries": {
   "段二谷": {
    "ps_date": "2014-03-31",
    "month_diff": 0
   },
   "段二峰": {
    "ps_date": "2015-05-31",
    "month_diff": 0
   },
   "段三谷": {
    "ps_date": "2018-12-31",
    "month_diff": 0
   },
   "段三峰": {
    "ps_date": "2021-01-31",
    "month_diff": 0
   }
  },
  "segments": [
   {
    "phase": "bull",
    "start_date": "2005-01-31",
    "end_date": "2007-10-31",
    "start_price": 954.87,
    "end_price": 5688.54,
    "months": 33,
    "amplitude": 4.957397,
    "confirmed": false
   },
   {
    "phase": "bear",
    "start_date": "2007-10-31",
    "end_date": "2008-10-31",
    "start_price": 5688.54,
    "end_price": 1663.66,
    "months": 12,
    "amplitude": 0.707542,
    "confirmed": true
   },
   {
    "phase": "bull",
    "start_date": "2008-10-31",
    "end_date": "2010-10-31",
    "start_price": 1663.66,
    "end_price": 3379.98,
    "months": 24,
    "amplitude": 1.031653,
    "confirmed": true
   },
   {
    "phase": "bear",
    "start_date": "2010-10-31",
    "end_date": "2014-03-31",
    "start_price": 3379.98,
    "end_price": 2146.3,
    "months": 41,
    "amplitude": 0.364996,
    "confirmed": true
   },
   {
    "phase": "bull",
    "start_date": "2014-03-31",
    "end_date": "2015-05-31",
    "start_price": 2146.3,
    "end_price": 4840.83,
    "months": 14,
    "amplitude": 1.25543,
    "confirmed": true
   },
   {
    "phase": "bear",
    "start_date": "2015-05-31",
    "end_date": "2016-02-29",
    "start_price": 4840.83,
    "end_price": 2877.47,
    "months": 9,
    "amplitude": 0.405583,
    "confirmed": true
   },
   {
    "phase": "bull",
    "start_date": "2016-02-29",
    "end_date": "2018-01-31",
    "start_price": 2877.47,
    "end_price": 4275.9,
    "months": 23,
    "amplitude": 0.485993,
    "confirmed": true
   },
   {
    "phase": "bear",
    "start_date": "2018-01-31",
    "end_date": "2018-12-31",
    "start_price": 4275.9,
    "end_price": 3010.65,
    "months": 11,
    "amplitude": 0.295903,
    "confirmed": true
   },
   {
    "phase": "bull",
    "start_date": "2018-12-31",
    "end_date": "2021-01-31",
    "start_price": 3010.65,
    "end_price": 5351.97,
    "months": 25,
    "amplitude": 0.777679,
    "confirmed": true
   },
   {
    "phase": "bear",
    "start_date": "2021-01-31",
    "end_date": "2024-01-31",
    "start_price": 5351.97,
    "end_price": 3215.35,
    "months": 36,
    "amplitude": 0.399221,
    "confirmed": true
   },
   {
    "phase": "bull",
    "start_date": "2024-01-31",
    "end_date": "2026-10-31",
    "start_price": 3215.35,
    "end_price": 4170.613,
    "months": 33,
    "amplitude": 0.297095,
    "confirmed": false
   }
  ],
  "flat_bottom_evidence": {
   "2012-11": 2139.66,
   "2013-06": 2200.64,
   "2014-03": 2146.3
  }
 },
 "BCD": {
  "coverage": {
   "F4_rows": 1676,
   "emotion_rows": 1622,
   "inner_join": 1570,
   "n_states": 3,
   "sector_obs_rows": 733,
   "capital_obs_rows": 1622,
   "dropped_bands": [
    "ice"
   ]
  },
  "cells": [
   {
    "cell_id": "boiling|neutral",
    "days": 179,
    "eligible": true
   },
   {
    "cell_id": "boiling|risk_off",
    "days": 35,
    "eligible": true
   },
   {
    "cell_id": "boiling|risk_on",
    "days": 28,
    "eligible": false
   },
   {
    "cell_id": "cooling|neutral",
    "days": 80,
    "eligible": true
   },
   {
    "cell_id": "cooling|risk_off",
    "days": 14,
    "eligible": false
   },
   {
    "cell_id": "cooling|risk_on",
    "days": 22,
    "eligible": false
   },
   {
    "cell_id": "mild|neutral",
    "days": 431,
    "eligible": true
   },
   {
    "cell_id": "mild|risk_off",
    "days": 79,
    "eligible": true
   },
   {
    "cell_id": "mild|risk_on",
    "days": 71,
    "eligible": true
   },
   {
    "cell_id": "warming|neutral",
    "days": 448,
    "eligible": true
   },
   {
    "cell_id": "warming|risk_off",
    "days": 94,
    "eligible": true
   },
   {
    "cell_id": "warming|risk_on",
    "days": 89,
    "eligible": true
   }
  ],
  "state_means": {
   "neutral": 0.000721,
   "risk_off": -0.000754,
   "risk_on": -0.001949
  },
  "grey_means": {
   "boiling": 0.000258,
   "cooling": 0.000147,
   "mild": 0.000577,
   "warming": -8e-05
  },
  "grey_anti_holds": true,
  "ps_vs_f4_agreement": 0.1522
 },
 "E": {
  "grey_1p5": "blocked(ValueError)",
  "grey_neg": "blocked(ValueError)",
  "out_of_window": "blocked(KeyError)",
  "too_many_states": "blocked(ValueError)"
 }
}```
