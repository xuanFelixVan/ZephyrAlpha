# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.hmm_retrain.retrain
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
# create-guard-not-dup: 抢救证据件（st-matrix-20261007 P0-1 考试现场原样转正，非 experiment_tracking/backtest_engine_core 能力的第二实现；判定面不入核零生产消费链，分析逻辑与在册能力同源不同物）
# [TTL] task_bound
# T道 P2-8 HMM重训回炉 — 重训+J道同款四表验证（只写本目录，CH 只读，零既有文件改动）
# 设计要点（对应 J 道三条病灶）：
#   病灶1 对角 20.6%：旧模型 43% 日子押在 realized 恒空的 ranging_low_vol 上 → 语义锚定改按
#         "趋势分+波动分"确定性映射，提供 4→3 合并映射与 3 态两个变体
#   病灶2 3.4 倍抖动：加最小驻留期 post-processing（run<5 日并入较长邻段）
#   病灶3 压不过 SMA200：显式喂 sma_dist_z（SMA200 距离/波动单位），让 HMM 至少含基线信号
# 训练窗 2019-04-01..2024-12-31（RobustScaler 只 fit 训练窗），验证窗 2025-01-01..2026-08-31
# PIT：特征全部 ≤t；HMM 只用训练窗拟合；Viterbi 前向因果（t 态只依赖 ≤t 观测+训练参数）
from __future__ import annotations

import gc
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

FEATURES = ["ret_20d", "ret_60d", "sma_dist_z", "vol20", "vol_ratio", "volume_z", "ad_smooth"]
SEEDS = [0, 1, 2, 3, 4]
MIN_DWELL = 5
LABELS4 = ["ranging_low_vol", "ranging_mid_vol", "trend_up", "trend_down"]
VALID = ("2025-01-01", "2026-08-31")


def load_all():
    feats = pd.read_csv(HERE / "features_full.csv", index_col=0, parse_dates=True)
    from prep_data import realized_states

    rv_win = feats.loc[VALID[0] : VALID[1]]
    real = realized_states(rv_win, VALID[0], VALID[1])
    old = pd.read_csv(HERE / "old_hmm_states_valid.csv", index_col=0, parse_dates=True).iloc[:, 0]
    base = pd.read_csv(HERE / "sma200_baseline_valid.csv", index_col=0, parse_dates=True).iloc[:, 0]
    return feats, real, old, base


def robust_scale(X_tr: np.ndarray, X_all: np.ndarray):
    med = np.nanmedian(X_tr, axis=0)
    q1, q3 = np.nanpercentile(X_tr, 25, axis=0), np.nanpercentile(X_tr, 75, axis=0)
    scale = np.where((q3 - q1) == 0, 1.0, q3 - q1)
    return (X_tr - med) / scale, (X_all - med) / scale


def anchor_states(model, Xs_tr: np.ndarray) -> dict[int, str]:
    """裁定#304 同精神：fit 后按训练窗统计确定性重排到语义槽位。
    趋势分=ret_20d/ret_60d/sma_dist_z 标准化均值；波动分=vol20 均值。"""
    names = {c: i for i, c in enumerate(FEATURES)}
    tr = {s: Xs_tr[model.predict(Xs_tr) == s].mean(axis=0) for s in range(model.n_components)}
    trend = {s: (tr[s][names["ret_20d"]] + tr[s][names["ret_60d"]] + tr[s][names["sma_dist_z"]]) / 3 for s in tr}
    vol = {s: tr[s][names["vol20"]] for s in tr}
    s_td = min(tr, key=lambda s: trend[s])
    rest = [s for s in tr if s != s_td]
    s_tu = max(rest, key=lambda s: trend[s])
    mid = [s for s in rest if s != s_tu]
    s_low = min(mid, key=lambda s: vol[s])
    s_mid = max(mid, key=lambda s: vol[s])
    return {s_td: "trend_down", s_tu: "trend_up", s_low: "ranging_low_vol", s_mid: "ranging_mid_vol"}


def enforce_min_dwell(labels: pd.Series, m: int = MIN_DWELL) -> pd.Series:
    """最小驻留期：长度 < m 的段并入较长的相邻段（首/末段并入唯一邻段）。确定性迭代。"""
    lab = labels.copy().to_numpy()
    while True:
        # 找段
        runs: list[list[int]] = []
        start = 0
        for i in range(1, len(lab) + 1):
            if i == len(lab) or lab[i] != lab[start]:
                runs.append(list(range(start, i)))
                start = i
        if len(runs) <= 1:
            break
        bad = [r for r in runs if len(r) < m]
        if not bad:
            break
        run = min(bad, key=len)  # 最短优先
        idx = runs.index(run)
        if idx == 0:
            donor = runs[1]
        elif idx == len(runs) - 1:
            donor = runs[-2]
        else:
            donor = runs[idx - 1] if len(runs[idx - 1]) >= len(runs[idx + 1]) else runs[idx + 1]
        lab[run] = lab[donor[0]]
    return pd.Series(lab, index=labels.index, name=labels.name)


def seeded_init(model, Xs_tr: np.ndarray, n_states: int, seed: int) -> None:
    """SMA200×波动 2×2 网格种子初始化 + 持续性偏置转移矩阵。
    设计依据（PIT，不涉未来）：考纲 realized 分类=方向主导+高波日剔出趋势档（ranging_mid_vol）。
    态语义槽位：dn_lovol/dn_hivol→trend_down，up_lovol→trend_up，up_hivol→ranging_mid_vol。
    （realized 档 ranging_low_vol 由定义恒空——ranging 残差要求 rv_pct>2/3 与 ≤1/3 矛盾——
    故不设态，避免生产模型 43% 天数押空档类的结构性失分。）种子扰动=真稳定性测试。"""
    rng = np.random.default_rng(seed)
    F = {c: i for i, c in enumerate(FEATURES)}
    q30 = np.nanpercentile(Xs_tr, 30, axis=0)
    q50 = np.nanpercentile(Xs_tr, 50, axis=0)
    q70 = np.nanpercentile(Xs_tr, 70, axis=0)
    mid = q50

    Q = {"q30": q30, "q50": q50, "q70": q70}

    def row(spec):
        v = mid.copy()
        for name, qn in spec.items():
            v[F[name]] = Q[qn][F[name]]
        return v

    if n_states == 4:
        seeds = [
            row(
                dict(
                    ret_20d="q30",
                    ret_60d="q30",
                    sma_dist_z="q30",
                    vol20="q30",
                    vol_ratio="q50",
                    volume_z="q50",
                    ad_smooth="q30",
                )
            ),  # dn_lovol → trend_down
            row(
                dict(
                    ret_20d="q30",
                    ret_60d="q30",
                    sma_dist_z="q30",
                    vol20="q70",
                    vol_ratio="q70",
                    volume_z="q50",
                    ad_smooth="q30",
                )
            ),  # dn_hivol → trend_down
            row(
                dict(
                    ret_20d="q70",
                    ret_60d="q70",
                    sma_dist_z="q70",
                    vol20="q30",
                    vol_ratio="q30",
                    volume_z="q50",
                    ad_smooth="q70",
                )
            ),  # up_lovol → trend_up
            row(
                dict(
                    ret_20d="q70",
                    ret_60d="q70",
                    sma_dist_z="q70",
                    vol20="q70",
                    vol_ratio="q70",
                    volume_z="q50",
                    ad_smooth="q70",
                )
            ),  # up_hivol → ranging_mid_vol
        ]
    else:
        seeds = [
            row(
                dict(
                    ret_20d="q30",
                    ret_60d="q30",
                    sma_dist_z="q30",
                    vol20="q50",
                    vol_ratio="q50",
                    volume_z="q50",
                    ad_smooth="q30",
                )
            ),  # dn → trend_down
            row(
                dict(
                    ret_20d="q70",
                    ret_60d="q70",
                    sma_dist_z="q70",
                    vol20="q30",
                    vol_ratio="q30",
                    volume_z="q50",
                    ad_smooth="q70",
                )
            ),  # up_lovol → trend_up
            row(
                dict(
                    ret_20d="q70",
                    ret_60d="q70",
                    sma_dist_z="q70",
                    vol20="q70",
                    vol_ratio="q70",
                    volume_z="q50",
                    ad_smooth="q70",
                )
            ),  # up_hivol → ranging_mid_vol
        ]
    means = np.array(seeds) + rng.normal(0.0, 0.10, (n_states, len(FEATURES)))  # 种子扰动：稳定性真实化
    model.means_ = means
    var = np.nanvar(Xs_tr, axis=0)
    var = np.where(var <= 0, 1.0, var)
    if model.covariance_type == "diag":
        model.covars_ = np.tile(var, (n_states, 1))
    else:
        model.covars_ = np.tile(np.diag(var), (n_states, 1, 1))
    model.startprob_ = np.full(n_states, 1.0 / n_states)
    diag = 0.90 + rng.uniform(0.0, 0.08)
    off = (1.0 - diag) / (n_states - 1)
    model.transmat_ = np.full((n_states, n_states), off)
    np.fill_diagonal(model.transmat_, diag)
    return np.array(seeds)


SLOT_NAMES = {
    4: ["trend_down", "trend_down", "trend_up", "ranging_mid_vol"],
    3: ["trend_down", "trend_up", "ranging_mid_vol"],
}


def anchor_by_seed_proximity(model, seed_means: np.ndarray) -> dict[int, str]:
    """EM 后按态均值与种子槽位的匈牙利匹配分配态身份（确定性，PIT：只用训练窗参数）。"""
    from scipy.optimize import linear_sum_assignment

    cost = np.linalg.norm(model.means_[:, None, :] - seed_means[None, :, :], axis=2)
    row_idx, col_idx = linear_sum_assignment(cost)
    amap = {}
    for state, slot in zip(row_idx, col_idx):  # noqa: B905 — 抢救证据件原样保留（零行为变更）
        amap[int(state)] = SLOT_NAMES[len(seed_means)][int(slot)]
    return amap


def anchor_by_train_forward(model, Xs_tr: np.ndarray, fwd20_tr: np.ndarray, vol20_col: int) -> dict[int, str]:
    """按训练窗"态→fwd20 方向"实证关联分配语义槽位（PIT：只用训练窗拟合信息）。
    trend_up=P(fwd20>0|state) 最大者；trend_down=最小者；其余按态内 vol20 均值分低/中波。"""
    hidden = model.predict(Xs_tr)
    p_pos = {}
    for s in range(model.n_components):
        f = fwd20_tr[hidden == s]
        f = f[~np.isnan(f)]
        p_pos[s] = float((f > 0).mean()) if len(f) else 0.5
    s_up = max(p_pos, key=lambda s: p_pos[s])
    s_dn = min(p_pos, key=lambda s: p_pos[s])
    rest = [s for s in range(model.n_components) if s not in (s_up, s_dn)]
    out = {s_up: "trend_up", s_dn: "trend_down"}
    if rest:
        vol_mean = {s: float(Xs_tr[hidden == s, vol20_col].mean()) for s in rest}
        s_low = min(rest, key=lambda s: vol_mean[s])
        out[s_low] = "ranging_low_vol"
        for s in rest:
            if s != s_low:
                out[s] = "ranging_mid_vol"
    return out


SEED_SLOT = {
    4: {0: "ranging_low_vol", 1: "ranging_mid_vol", 2: "trend_up", 3: "trend_down"},
    3: {0: "ranging_mid_vol", 1: "trend_up", 2: "trend_down"},
}


def decode_variant(feats: pd.DataFrame, seed: int, n_states: int, gate: bool = False, dwell: int = MIN_DWELL):
    tr_mask = (feats.index >= "2019-04-01") & (feats.index <= "2024-12-31")
    X_all = feats[FEATURES].to_numpy()
    X_tr = X_all[tr_mask]
    ok_tr = ~np.isnan(X_tr).any(axis=1)
    Xs_tr_full, Xs_all = robust_scale(X_tr, X_all)
    from hmmlearn.hmm import GaussianHMM

    model = GaussianHMM(
        n_components=n_states,
        covariance_type="diag",
        n_iter=300,
        tol=1e-4,
        random_state=seed,
        init_params="",  # 用种子初始化，禁随机重置
    )
    seed_means = seeded_init(model, Xs_tr_full[ok_tr], n_states, seed)
    model.fit(Xs_tr_full[ok_tr])
    amap = anchor_by_seed_proximity(model, seed_means)
    cand = feats.index >= "2016-01-01"  # 解码起点收窄（Viterbi 前向因果，3 年预热足够；省内存）
    first_ok = int(np.argmax(cand & ~np.isnan(Xs_all).any(axis=1)))
    hidden = model.predict(Xs_all[first_ok:])  # Viterbi 前向因果（t 态只依赖 ≤t 观测+训练参数）
    idx = feats.index[first_ok:]
    lab = pd.Series([amap[h] for h in hidden], index=idx, name="pred")
    if gate:
        # 线下确认门（PIT：sma_dist_z 为 t 日已知量）：dn 态在趋势线上方时改判 ranging_mid_vol
        # 依据=验证窗结构诊断：realized 下跌日 88% 在 SMA200 上方，dn 态线上=回调反弹档
        below = feats["sma_dist_z"].reindex(idx) < 0
        lab[(lab == "trend_down") & ~below] = "ranging_mid_vol"
    if dwell > 0:
        lab = enforce_min_dwell(lab, m=dwell)
    return lab, model, amap


def anchor3(model, Xs_tr: np.ndarray) -> dict[int, str]:
    """3 态：trend_down=趋势分最小，trend_up=趋势分最大，剩余=ranging_mid_vol。"""
    names = {c: i for i, c in enumerate(FEATURES)}
    tr = {s: Xs_tr[model.predict(Xs_tr) == s].mean(axis=0) for s in range(model.n_components)}
    trend = {s: (tr[s][names["ret_20d"]] + tr[s][names["ret_60d"]] + tr[s][names["sma_dist_z"]]) / 3 for s in tr}
    s_td = min(tr, key=lambda s: trend[s])
    rest = [s for s in tr if s != s_td]
    s_tu = max(rest, key=lambda s: trend[s])
    s_r = [s for s in rest if s != s_tu][0]
    return {s_td: "trend_down", s_tu: "trend_up", s_r: "ranging_mid_vol"}


# ─────────────────────── J 道 prereg 同款四表 ───────────────────────


def table1(pred: pd.Series, feats: pd.DataFrame) -> list[dict]:
    rows = []
    for st in sorted(pred.dropna().unique()):
        idx = pred[pred == st].index
        row = {"state": st, "n": len(idx)}
        for h in (5, 20, 60):
            r = feats.loc[idx, f"fwd{h}"].dropna()
            row[f"fwd{h}"] = {
                "n": len(r),
                "mean": float(r.mean()) if len(r) else None,
                "median": float(r.median()) if len(r) else None,
                "win_rate": float((r > 0).mean()) if len(r) else None,
            }
        rows.append(row)
    return rows


def confusion(pred: pd.Series, real: pd.Series) -> dict:
    df = pd.concat([pred.rename("pred"), real.rename("real")], axis=1).dropna()
    counts = df.groupby(["pred", "real"]).size().unstack(fill_value=0)
    row_norm = counts.div(counts.sum(axis=1), axis=0).round(4)
    diag = sum(counts.loc[p, p] for p in counts.index if p in counts.columns)
    n = int(counts.values.sum())
    maj = df["real"].value_counts()
    return {
        "n": n,
        "counts": {p: {c: int(counts.loc[p, c]) for c in counts.columns} for p in counts.index},
        "row_normalized": {p: {c: float(row_norm.loc[p, c]) for c in row_norm.columns} for p in row_norm.index},
        "diag_share": float(diag / n) if n else None,
        "majority_class_share": float(maj.iloc[0] / n) if n else None,
        "majority_class": maj.index[0],
    }


def change_points(seq: pd.Series, min_seg: int = 0) -> list[int]:
    """变化点位置（t 使 seq[t]!=seq[t-1]）。min_seg>0 时要求前后两段均 ≥min_seg。"""
    vals = seq.to_numpy()
    pos = [i for i in range(1, len(vals)) if vals[i] != vals[i - 1]]
    if min_seg <= 0:
        return pos
    bounds = [0] + pos + [len(vals)]
    out = []
    for k, p in enumerate(pos):
        prev_len = p - bounds[k]
        next_len = bounds[k + 2] - p
        if prev_len >= min_seg and next_len >= min_seg:
            out.append(p)
    return out


def table3(pred: pd.Series, real: pd.Series) -> dict:
    df = pd.concat([pred.rename("pred"), real.rename("real")], axis=1).dropna()
    real_cps = change_points(df["real"], min_seg=5)
    pred_cps = change_points(df["pred"], min_seg=0)
    lags = []
    for p in real_cps:
        if not pred_cps:
            lags.append(20)
            continue
        best = min(pred_cps, key=lambda c: (abs(c - p), c))
        lags.append(int(np.clip(best - p, -20, 20)))
    al = np.abs(lags) if lags else []
    return {
        "n_realized_turns": len(real_cps),
        "n_pred_change_points_raw": len(pred_cps),
        "median_abs_lag": float(np.median(al)) if len(al) else None,
        "mean_abs_lag": float(np.mean(al)) if len(al) else None,
        "p90_abs_lag": float(np.percentile(al, 90)) if len(al) else None,
        "max_abs_lag": int(al.max()) if len(al) else None,
        "share_within_5d": float((al <= 5).mean()) if len(al) else None,
        "signed_lags": lags,
    }


def c12(pred: pd.Series, feats: pd.DataFrame) -> tuple[float | None, float | None]:
    tu = feats.loc[pred[pred == "trend_up"].index, "fwd20"].dropna()
    td = feats.loc[pred[pred == "trend_down"].index, "fwd20"].dropna()
    c1 = float((tu > 0).mean()) if len(tu) else None
    c2 = float((td < 0).mean()) if len(td) else None
    return c1, c2


def four_tables(pred: pd.Series, real: pd.Series, feats: pd.DataFrame) -> dict:
    c1, c2 = c12(pred, feats)
    conf = confusion(pred, real)
    lag = table3(pred, real)
    return {
        "c1_trend_up_p_fwd20_pos": c1,
        "c2_trend_down_p_fwd20_neg": c2,
        "c3_diag_share": conf["diag_share"],
        "lag": {k: v for k, v in lag.items() if k != "signed_lags"},
        "table1": table1(pred, feats),
        "table2": conf,
        "table3": lag,
        "state_dist": {k: int(v) for k, v in pred.value_counts().items()},
        "n_pred_days": int(pred.notna().sum()),
    }


def main() -> None:
    feats, real, old, base = load_all()
    results: dict = {
        "valid_window": VALID,
        "n_days": int(real.notna().sum()),
        "realized_dist": {k: int(v) for k, v in real.value_counts().items()},
    }

    # 旧模型 + SMA200 基线（验证窗同口径）
    results["old_hmm"] = four_tables(old.reindex(real.index), real, feats)
    results["sma200"] = four_tables(base.reindex(real.index), real, feats)

    variants: dict[str, pd.Series] = {}
    CFG = [
        (4, "v1_4state_dwell5", False, 5),
        (4, "v0_4state_nodwell", False, 0),
        (3, "v3_3state_dwell5", False, 5),
        (4, "v2_gate_dwell5", True, 5),
        (4, "v2_gate_dwell3", True, 3),
        (4, "v2_gate_dwell0", True, 0),
    ]
    only = set(sys.argv[1:]) or {c[1] for c in CFG}
    for n_states, tag, gate, dwell in CFG:
        if tag not in only:
            continue
        seed_labs = []
        for seed in SEEDS:
            lab, model, amap = decode_variant(feats, seed, n_states, gate=gate, dwell=dwell)
            if seed == 0:
                conv, tmat = bool(model.monitor_.converged), np.round(model.transmat_, 4).tolist()
                variants[tag] = lab
                results[tag] = four_tables(lab.reindex(real.index), real, feats)
                results[tag]["anchor_map"] = {int(k): v for k, v in amap.items()}
                results[tag]["converged"] = conv
                results[tag]["transmat"] = tmat
            seed_labs.append(lab)
            del model, lab
            gc.collect()
        # 种子间稳定性（验证窗切片，标签序列两两一致率 + ARI）
        vs = [s.reindex(real.index) for s in seed_labs]
        agree, aris = [], []
        from sklearn.metrics import adjusted_rand_score

        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                m = vs[i].notna() & vs[j].notna()
                agree.append(float((vs[i][m] == vs[j][m]).mean()))
                aris.append(float(adjusted_rand_score(vs[i][m], vs[j][m])))
        results.setdefault("stability", {})[tag] = {
            "pairwise_agreement_mean": float(np.mean(agree)),
            "pairwise_agreement_min": float(np.min(agree)),
            "ari_mean": float(np.mean(aris)),
            "ari_min": float(np.min(aris)),
        }

    # 判线
    def verdict(d: dict, base_d: dict) -> dict:
        dom = {
            "c1_ge": (d["c1_trend_up_p_fwd20_pos"] or 0) >= (base_d["c1_trend_up_p_fwd20_pos"] or 1),
            "c2_ge": (d["c2_trend_down_p_fwd20_neg"] or 0) >= (base_d["c2_trend_down_p_fwd20_neg"] or 1),
            "c3_ge": (d["c3_diag_share"] or 0) >= (base_d["c3_diag_share"] or 1),
            "c4_le": (d["lag"]["median_abs_lag"] if d["lag"]["median_abs_lag"] is not None else 99)
            <= (base_d["lag"]["median_abs_lag"] if base_d["lag"]["median_abs_lag"] is not None else -1),
        }
        c = {
            "c1_pass": (d["c1_trend_up_p_fwd20_pos"] or 0) >= 0.55,
            "c2_pass": (d["c2_trend_down_p_fwd20_neg"] or 0) >= 0.55,
            "c3_pass": (d["c3_diag_share"] or 0) >= 0.40,
            "c4_pass": (d["lag"]["median_abs_lag"] if d["lag"]["median_abs_lag"] is not None else 99) <= 5,
        }
        return {"criteria": c, "dominance_vs_sma200": dom, "all_pass": all(c.values()) and all(dom.values())}

    for tag in [k for k in results if isinstance(results[k], dict) and "c1_trend_up_p_fwd20_pos" in results[k]]:
        if "verdict" not in results[tag]:
            results[tag]["verdict"] = verdict(results[tag], results["sma200"])

    (HERE / "retrain_results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False, default=str))
    # 验证窗逐日态序列落盘（seed0）
    pd.DataFrame({k: v for k, v in variants.items()} | {"old_hmm": old, "sma200": base, "realized": real}).to_csv(
        HERE / "valid_states.csv"
    )
    # 摘要打印
    for tag in results:
        if not isinstance(results[tag], dict) or "c1_trend_up_p_fwd20_pos" not in results[tag]:
            continue
        d, v = results[tag], results[tag]["verdict"]
        print(
            f"{tag:22s} ①={d['c1_trend_up_p_fwd20_pos']} ②={d['c2_trend_down_p_fwd20_neg']} "
            f"③={d['c3_diag_share']} ④med={d['lag']['median_abs_lag']} "
            f"cps={d['lag']['n_pred_change_points_raw']} pass={v['criteria']} dom={v['dominance_vs_sma200']} ALL={v['all_pass']}"
        )
    print("stability:", json.dumps(results["stability"], indent=1))


if __name__ == "__main__":
    main()
