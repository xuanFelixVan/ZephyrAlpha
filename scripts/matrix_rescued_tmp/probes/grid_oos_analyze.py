# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.probes.grid_oos_analyze
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] 无（一次性考卷/对拍/计时证据件；随附数据在 docs/_working/matrix_campaign/rescued_tmp_20261007/）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 抢救证据件原样保留，判定面不入核；表名走 TableRegistry 真源
# [MODIFY-GUARD] freeze——抢救证据件禁改写业务逻辑（门禁合规头/noqa 除外）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 运行期异常如实抛出（证据件不吞错不改判）
# [TESTS] 无独立测试（一次性证据件，输出随件入册）
# create-guard-not-dup: 抢救证据件（st-matrix-20261007 P0-1 考试现场原样转正，非 experiment_tracking/backtest_engine_core 能力的第二实现；判定面不入核零生产消费链，分析逻辑与在册能力同源不同物）
# [TTL] task_bound
# -*- coding: ascii -*-
# R-dao 324-grid OOS verdict analysis (temp script, .runtime/tmp only)
# prereg frozen at docs/_working/fexam/grid_oos_v1 prereg_v1 (2026-10-06T19:27Z)
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("D:/ZephyrAlpha")
OUT = REPO / ".runtime/tmp/st-matrix-20261007/oos_results.json"

ROOMS = {
    "std_device": "grid_20261006-201353",
    "b_topn_band": "grid_20261006-201854",
    "d1_freq_band": "grid_20261006-201935",
    "g_universe_band": "grid_20261006-202016",
    "a2_composite_band": "grid_20261006-202055",
}
BAND_DIM = {
    "std_device": None,
    "b_topn_band": "B_top_n",
    "d1_freq_band": "D1_rebalance_freq",
    "g_universe_band": "G_universe",
    "a2_composite_band": "A2_combine_weight",
}
OOS = ("2025-10-09", "2026-09-30")
IS = ("2018-01-02", "2025-09-30")
DD_FLOOR = -0.30


def oos_metrics(ret: pd.Series):
    r = ret.dropna().astype(float)
    t = len(r)
    sd = r.std(ddof=1)
    sharpe = float(r.mean() / sd * math.sqrt(252)) if sd and sd > 0 else float("nan")
    nav = (1.0 + r).cumprod()
    dd = float((nav / nav.cummax() - 1.0).min())
    ann = float(nav.iloc[-1] ** (252.0 / t) - 1.0) if t else float("nan")
    return sharpe, dd, ann, t


def curve_key(ret: pd.Series) -> str:
    import hashlib

    return hashlib.sha256(ret.round(10).to_numpy().tobytes()).hexdigest()[:16]


def verdict(oos_sh, oos_dd, is_sh):
    # prereg three-state; IS unavailable in this batch => no pass / no retire possible
    if is_sh is not None and oos_sh > 0 and is_sh > 0 and oos_dd >= DD_FLOOR:
        return "pass"
    if is_sh is not None and oos_sh < 0 and is_sh < 0:
        return "retire_candidate"
    if oos_sh > 0 and oos_dd >= DD_FLOOR:
        return "rework/is_pending_oos_ok"
    if oos_sh > 0:
        return "rework/is_pending_oos_dd_breach"
    return "rework/oos_negative"


rows = []
rooms_summary = {}
for room, gdir in ROOMS.items():
    base = REPO / "data/strategy_intake" / gdir
    man = pd.read_csv(base / "manifest.csv")
    nr = pd.read_parquet(base / "net_returns.parquet")
    assert len(man) == nr.shape[1], (room, len(man), nr.shape)
    idx_min = str(nr.index.min())[:10]
    idx_max = str(nr.index.max())[:10]
    assert (idx_min, idx_max) == OOS, (room, idx_min, idx_max)  # IS absent by fact
    sign_ok = dd_ok = 0
    for i in range(len(man)):
        m = man.iloc[i]
        params = json.loads(m["values_json"])
        sh, dd, ann, t = oos_metrics(nr.iloc[:, i])
        if not (math.isnan(sh) or math.isnan(m["sharpe"])) and (sh > 0) == (m["sharpe"] > 0):
            sign_ok += 1
        if abs(dd - m["max_drawdown"]) <= 1e-3:
            dd_ok += 1
        rows.append(
            {
                "room": room,
                "cell": i,
                "recipe_id": str(m["recipe_id"]),
                "params": params,
                "oos_sharpe": round(sh, 4),
                "oos_maxdd": round(dd, 4),
                "oos_ann_ret": round(ann, 4),
                "oos_days": t,
                "manifest_sharpe": float(m["sharpe"]),
                "is_sharpe": None,
                "verdict": verdict(sh, dd, None),
                "curve_key": curve_key(nr.iloc[:, i]),
            }
        )
    rooms_summary[room] = {
        "dir": f"data/strategy_intake/{gdir}",
        "n_cells": int(len(man)),
        "manifest_sign_consistent": f"{sign_ok}/{len(man)}",
        "dd_match_manifest_1e3": f"{dd_ok}/{len(man)}",
        "negatives_rows": 0,
    }

df = pd.DataFrame(rows)
all_summary = {
    "n_cells_total": int(len(df)),
    "n_unique_recipe_id": int(df.recipe_id.nunique()),
    "n_unique_curves": int(df.curve_key.nunique()),
    "verdict_counts": df.verdict.value_counts().to_dict(),
}

# per-room counts + top5 by oos sharpe (full params)
per_room = {}
for room in ROOMS:
    sub = df[df.room == room]
    top = sub.sort_values("oos_sharpe", ascending=False).head(5)
    per_room[room] = {
        "counts": sub.verdict.value_counts().to_dict(),
        "top5": [
            {
                "recipe_id": r.recipe_id,
                "oos_sharpe": r.oos_sharpe,
                "oos_maxdd": r.oos_maxdd,
                "oos_ann_ret": r.oos_ann_ret,
                "params": r.params,
            }
            for r in top.itertuples()
        ],
    }

# band pattern: paired grouping by all params except band dim
band_stats = {}
for room, dim in BAND_DIM.items():
    if dim is None:
        continue
    sub = df[df.room == room].copy()
    sub["band_val"] = sub.params.map(lambda p: p.get(dim))
    keys_wo = sub.params.map(lambda p: tuple(sorted((k, v) for k, v in p.items() if k != dim)))
    sub["grp"] = keys_wo
    gsize = sub.groupby("grp").size()
    complete = gsize[gsize == sub.band_val.nunique()]
    means = sub.groupby("band_val").oos_sharpe.mean().sort_values(ascending=False)
    med = sub.groupby("band_val").oos_sharpe.median().sort_values(ascending=False)
    pos = sub.groupby("band_val").oos_sharpe.apply(lambda s: (s > 0).mean())
    band_stats[room] = {
        "dim": dim,
        "n_band_values": int(sub.band_val.nunique()),
        "n_complete_paired_groups": int(len(complete)),
        "mean_oos_sharpe_by_band": {k: round(v, 4) for k, v in means.items()},
        "median_oos_sharpe_by_band": {k: round(v, 4) for k, v in med.items()},
        "share_oos_sharpe_gt0_by_band": {k: round(v, 3) for k, v in pos.items()},
    }

# global top5
gtop = df.sort_values("oos_sharpe", ascending=False).head(5)

result = {
    "all": all_summary,
    "rooms_check": rooms_summary,
    "per_room": per_room,
    "band_stats": band_stats,
    "global_top5": [
        {
            "room": r.room,
            "recipe_id": r.recipe_id,
            "oos_sharpe": r.oos_sharpe,
            "oos_maxdd": r.oos_maxdd,
            "oos_ann_ret": r.oos_ann_ret,
            "params": {k: v for k, v in r.params.items()},
        }
        for r in gtop.itertuples()
    ],
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

print("TOTAL", all_summary)
for room in ROOMS:
    rs = rooms_summary[room]
    print(
        room,
        rs["n_cells"],
        "sign",
        rs["manifest_sign_consistent"],
        "dd",
        rs["dd_match_manifest_1e3"],
        json.dumps(per_room[room]["counts"], ensure_ascii=False),
    )
for room, st in band_stats.items():
    print(
        "BAND",
        room,
        st["dim"],
        "paired_groups",
        st["n_complete_paired_groups"],
        json.dumps(st["mean_oos_sharpe_by_band"]),
    )
print("GLOBAL TOP5")
for g in result["global_top5"]:
    p = g["params"]
    brief = {
        k: p[k]
        for k in (
            "A1_factor_normalize",
            "A2_combine_weight",
            "B_top_n",
            "D1_rebalance_freq",
            "E_single_cap",
            "G_universe",
        )
        if k in p
    }
    print(" ", g["room"], g["recipe_id"][:10], g["oos_sharpe"], g["oos_maxdd"], json.dumps(brief))
