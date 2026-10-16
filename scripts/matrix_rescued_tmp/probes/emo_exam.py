# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.probes.emo_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] 无（一次性考卷/对拍/计时证据件；随附数据在 docs/04_research_records/data/matrix_campaign/rescued_tmp_20261007）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 抢救证据件原样保留，判定面不入核；表名走 TableRegistry 真源
# [MODIFY-GUARD] freeze——抢救证据件禁改写业务逻辑（门禁合规头/noqa 除外）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 运行期异常如实抛出（证据件不吞错不改判）
# [TESTS] 无独立测试（一次性证据件，输出随件入册）
# [TTL] task_bound
# emo_exam.py — O道·情绪指数首考四卷开跑（prereg 已冻结于 docs/_working/fexam/emotion_index_exam_v1.yaml）
# 纪律：CH 只读；判据按 prereg_v1 逐字执行；禁改判据。
from __future__ import annotations

import io
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

import numpy as np
import pandas as pd

from zephyr.data.table_registry import get_registry as _get_tbl_registry

# TABLE-NAME-REGISTRY 合规：表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5），抢救证据件同规
_TBL_KLINE_INDEX = _get_tbl_registry().table("market_index_kline")
_TBL_EMO_INDEX = _get_tbl_registry().table("market_emotion_index")
_TBL_TECH_IND = _get_tbl_registry().table("market_technical_indicator")

CH_BASE = "http://172.24.30.100:8123/"
_OPENER = request.build_opener(request.ProxyHandler({}))
W0, W1 = "2019-04-01", "2026-08-31"
OUT = Path(__file__).resolve().parent / "emo_results.json"


def q_df(sql: str) -> pd.DataFrame:
    if not sql.lstrip().lower().startswith(("select", "with", "describe")):
        raise RuntimeError(f"非只读: {sql[:60]}")
    req = request.Request(CH_BASE, data=sql.encode("utf-8"), method="POST")
    raw = _OPENER.open(req, timeout=180).read().decode("utf-8", errors="replace")
    if not raw.strip():
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(raw), sep="\t", dtype=str, quoting=3, keep_default_na=False)


def binom_p_ge(k: int, n: int, p0: float) -> float:
    """P(X>=k | Binom(n,p0)) 单侧。scipy 优先，缺库用正态近似（含连续性修正）。"""
    try:
        from scipy.stats import binomtest

        return float(binomtest(k, n, p0, alternative="greater").pvalue)
    except Exception:  # noqa: BLE001 — 抢救证据件原样保留（零行为变更）
        if n == 0:
            return float("nan")
        mu, sd = n * p0, math.sqrt(n * p0 * (1 - p0))
        return 0.5 * math.erfc(((n * p0 - k) - 0.5) / (sd * math.sqrt(2))) if sd > 0 else float("nan")


def main() -> None:
    res: dict = {"frozen_ref": "docs/_working/fexam/emotion_index_exam_v1.yaml prereg_v1"}
    res["generated_at_utc"] = datetime.now(timezone.utc).isoformat()

    # ---- 数据装载 ----
    k = q_df(
        f"SELECT trade_date, close FROM {_TBL_KLINE_INDEX} WHERE symbol='000300' ORDER BY trade_date FORMAT TSVWithNames"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
    )
    k["close"] = k["close"].astype(float)
    k["sma200"] = k["close"].rolling(200, min_periods=200).mean()
    k = k.reset_index(drop=True)
    k_idx = {d: i for i, d in enumerate(k["trade_date"])}

    emo = q_df(
        "SELECT trade_date, emotion_index, ts, ingest_ts, source, stage FROM {_TBL_EMO_INDEX}"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
        " WHERE stage='close_final' AND trade_date >= '2019-04-01' AND trade_date <= '2026-08-31'"
        " ORDER BY trade_date, ingest_ts FORMAT TSVWithNames"
    )
    emo = emo.drop_duplicates(subset=["trade_date"], keep="last")  # dedup 兜底（实测每键 1 行）
    emo["e"] = emo["emotion_index"].astype(float)

    w = emo.merge(k[["trade_date", "close", "sma200"]], on="trade_date", how="inner").reset_index(drop=True)
    pos = np.array([k_idx[d] for d in w["trade_date"]])
    closes_all = k["close"].to_numpy()

    def fwd(pos_arr: np.ndarray, h: int) -> np.ndarray:
        out = np.full(len(pos_arr), np.nan)
        j = pos_arr + h
        ok = j < len(closes_all)
        out[ok] = closes_all[j[ok]] / closes_all[pos_arr[ok]] - 1.0
        return out

    w["fwd5"] = fwd(pos, 5)
    w["fwd20"] = fwd(pos, 20)
    res["sample"] = {
        "emo_rows_window": int(len(emo)),
        "joined_rows": int(len(w)),
        "calendar_miss": int(len(emo) - len(w)),
        "fwd5_valid": int(w["fwd5"].notna().sum()),
        "fwd20_valid": int(w["fwd20"].notna().sum()),
        "source_mix": emo["source"].value_counts().to_dict(),
        "ingest_mix": emo["ingest_ts"].value_counts().to_dict(),
    }

    # ---- 基线（全窗） ----
    base = {}
    for h in (5, 20):
        s = w[f"fwd{h}"].dropna()
        base[f"fwd{h}"] = {
            "n": int(len(s)),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "p_neg": float((s < 0).mean()),
        }
    res["baseline"] = base

    # ---- 考卷① 极值分位择时（方向=反向，prereg） ----
    s90 = w[w["e"] >= 0.90]
    p1: dict = {"n_s90": int(len(s90))}
    for h in (5, 20):
        s = s90[f"fwd{h}"].dropna()
        p_neg = float((s < 0).mean())
        p1[f"fwd{h}"] = {
            "n": int(len(s)),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "p_neg": p_neg,
            "baseline_p_neg": base[f"fwd{h}"]["p_neg"],
            "beat_baseline": bool(p_neg > base[f"fwd{h}"]["p_neg"]),
            "hit_ge_55": bool(p_neg >= 0.55),
            "binom_p_vs_baseline": binom_p_ge(int((s < 0).sum()), len(s), base[f"fwd{h}"]["p_neg"]),
        }
    p1["pass"] = bool(
        p1["n_s90"] >= 30
        and p1["fwd5"]["n"] >= 30
        and p1["fwd20"]["n"] >= 30
        and p1["fwd5"]["hit_ge_55"]
        and p1["fwd20"]["hit_ge_55"]
        and p1["fwd5"]["beat_baseline"]
        and p1["fwd20"]["beat_baseline"]
    )
    # context: 冰点镜像 / 严格滞后变体
    ice = w[w["e"] <= 0.10]
    p1["ice_mirror_n"] = int(len(ice))
    if len(ice) >= 5:
        p1["ice_mirror"] = {h: float((ice[f"fwd{h}"].dropna() > 0).mean()) for h in (5, 20)}
    pos_s90 = np.array([k_idx[d] for d in s90["trade_date"]])
    strict = closes_all[pos_s90 + 21] / closes_all[pos_s90 + 1] - 1.0
    p1["strict_lag20_p_neg"] = float(np.mean(strict < 0))
    p1["strict_lag20_n"] = int(len(strict))
    res["paper1"] = p1

    # ---- 考卷② 情绪变化率 ----
    e_ser = w["e"].to_numpy()
    demo5 = np.full(len(w), np.nan)
    demo5[5:] = e_ser[5:] - e_ser[:-5]
    fwd5 = w["fwd5"].to_numpy()
    ret5_conc = np.full(len(w), np.nan)
    ret5_conc[5:] = closes_all[pos[5:]] / closes_all[pos[:-5]] - 1.0
    m = ~np.isnan(demo5) & ~np.isnan(fwd5)
    mc = ~np.isnan(demo5) & ~np.isnan(ret5_conc)
    d5v, f5v = demo5[m], fwd5[m]
    r_pearson = float(np.corrcoef(d5v, f5v)[0, 1])
    rank_d = pd.Series(d5v).rank().to_numpy()
    rank_f = pd.Series(f5v).rank().to_numpy()
    r_spear = float(np.corrcoef(rank_d, rank_f)[0, 1])
    r_conc = float(np.corrcoef(demo5[mc], ret5_conc[mc])[0, 1])
    # 滚动 60 日稳定性
    roll = pd.Series(d5v).rolling(60).corr(pd.Series(f5v)).dropna()
    p2 = {
        "n": int(m.sum()),
        "pearson": r_pearson,
        "spearman": r_spear,
        "concurrent_pearson": r_conc,
        "roll60_min": float(roll.min()),
        "roll60_max": float(roll.max()),
        "roll60_share_pos": float((roll > 0).mean()),
        "pass": bool(m.sum() >= 200 and abs(r_pearson) >= 0.15),
    }
    res["paper2"] = p2

    # ---- 考卷③ 体制增益 ----
    bull = w["close"] > w["sma200"]
    high = w["e"] >= 0.90
    low = w["e"] <= 0.40
    cells: dict = {}
    for rn, mask_r in (("bull", bull), ("bear", ~bull & w["sma200"].notna())):
        for bn, mask_b in (("high", high), ("low", low)):
            s = w[mask_r & mask_b]["fwd20"].dropna()
            cells[f"{rn}x{bn}"] = {"n": int(len(s)), "mean": float(s.mean()) if len(s) else None}
    s_bull_all = w[bull]["fwd20"].dropna()
    s_bear_all = w[~bull & w["sma200"].notna()]["fwd20"].dropna()
    S1 = float(s_bull_all.mean() - s_bear_all.mean())
    d_bull = cells["bullxlow"]["mean"] - cells["bullxhigh"]["mean"]
    d_bear = cells["bearxlow"]["mean"] - cells["bearxhigh"]["mean"]
    S2 = (d_bull + d_bear) / 2
    cells["S1_regime_spread"] = S1
    cells["d_bull"] = float(d_bull)
    cells["d_bear"] = float(d_bear)
    cells["S2_emo_spread_avg"] = float(S2)
    n_ok = all(cells[c]["n"] >= 30 for c in ("bullxhigh", "bullxlow", "bearxhigh", "bearxlow"))
    cells["n_ge30_all"] = bool(n_ok)
    cells["direction_ok"] = bool(d_bull > 0 and d_bear > 0)
    cells["gain_ok"] = bool(S2 > S1)
    cells["pass"] = bool(n_ok and d_bull > 0 and d_bear > 0 and S2 > S1)
    # context: fwd5 版
    for rn, mask_r in (("bull", bull), ("bear", ~bull & w["sma200"].notna())):
        for bn, mask_b in (("high", high), ("low", low)):
            s = w[mask_r & mask_b]["fwd5"].dropna()
            cells[f"fwd5_{rn}x{bn}"] = {"n": int(len(s)), "mean": float(s.mean()) if len(s) else None}
    res["paper3"] = cells

    # ---- 考卷④ PIT（a-c 原地复测，d/e 引冻结时事实） ----
    ts_bad = int((~emo["ts"].astype(str).str.endswith(" 15:10:00.000")).sum())
    date_bad = int((emo["ts"].astype(str).str[:10] != emo["trade_date"].astype(str)).sum())
    dup = emo.groupby("trade_date")["emotion_index"].nunique()
    dup_bad = int((dup > 1).sum())
    # asof 复扫
    comp = q_df(
        "SELECT trade_date, components FROM {_TBL_EMO_INDEX} WHERE stage='close_final'"  # noqa: bare-sql  抢救证据件SQL原样保留不改写（12字理由）
        " AND trade_date >= '2019-04-01' AND trade_date <= '2026-08-31' ORDER BY trade_date FORMAT TSVWithNames"
    )
    asof_bad = 0
    for _, row in comp.iterrows():
        td = str(row["trade_date"])
        for c in json.loads(str(row["components"]).replace("\\'", "'")):
            asof = str(c.get("asof", "") or "")
            if asof and asof > td:
                asof_bad += 1
    p4 = {
        "a_ts_violations_inwindow": ts_bad,
        "a_ts_date_mismatch": date_bad,
        "b_asof_future_violations": asof_bad,
        "c_inwindow_revision_keys": dup_bad,
        "d_construction_asof": "trailing250+拉窗止于当日+rolling/asof（builder 代码核验，冻结时事实）",
        "e_revision_capability": "pre_open 2026-10-02 双行异值(窗外重写实证)；考窗 1801 行=2026-09-23 单批 replay 建成，无逐日快照",
    }
    hard = ts_bad == 0 and date_bad == 0 and asof_bad == 0 and dup_bad == 0
    p4["pit_verdict"] = "clean" if hard and False else ("conditional_clean" if hard else "dirty")  # noqa: SIM223 — 抢救证据件原样保留（零行为变更）
    res["paper4"] = p4

    # ---- 总判（prereg verdict_rule） ----
    passes = [res["paper1"]["pass"], res["paper2"]["pass"], res["paper3"]["pass"]]
    pit = res["paper4"]["pit_verdict"]
    if sum(passes) >= 2 and pit == "clean":
        verdict = "合格"
    elif sum(passes) >= 2 and pit == "conditional_clean":
        verdict = "条件合格"
    else:
        verdict = "不合格"
    res["verdict"] = {"papers_pass": passes, "pit": pit, "n_pass": int(sum(passes)), "verdict": verdict}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
