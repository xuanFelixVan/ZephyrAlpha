---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
---

# 跑批件源码留证（可粘回）——因 M6 新 .py 进不了库


## `ruler_calibration.py` —— 全量校准跑批件（面板+组合构造+两轴判官，2,412 配置）

- 原文行数=524，本证据件收录=521 行（剔除 3 行 `# [TTL]/[STARTUP]/[CONSUMERS]` 头，避免与文档头族门禁冲突）
- sha256(原文全文)=26522f148d1fab4a3ccae0ad2f4ec3845923f66b7a95cbdd7f84ee017a1cbbb0
- 粘回路径=`scripts/backtest/`+`tests/backtest/` 配平（正式落地时须补 15 字段头与 translation/token，见 22 号件 §6.2）

```python
"""尺子校准实验跑批件（令⑥ 采纳件；本件临时态，正式版随 M6  render 追齐后归 scripts/backtest/）。

纪律真源=docs/_working/statsgov_campaign/10_ruler_calibration_preregistration_v1.md（先登记后测量）。
数学零自造：DSR 委托 MOD-SIM-024、PBO/切分委托 zephyr.backtest.core.cpcv、分母委托 TrialLedger＋逐批磁盘实测。
禁写任何成绩真源字节；DB 只读（DatabaseService 口，禁裸 duckdb/裸连）。

用法:
  python .runtime/tmp/statsgov/ruler_calibration.py --repo-root D:/ZephyrAlpha \
      --out docs/_working/statsgov_campaign/11_ruler_calibration_v1.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path


def _bootstrap(repo_root: Path) -> None:
    for p in (repo_root / "src", repo_root):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))


import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

#: ---- 冻结口径（照 10 号件 §1-§3，跑完禁改）----
PERIODS_PER_YEAR = 252
IS_START, IS_END = "2020-01-01", "2023-12-31"
OOS_START, OOS_END = "2024-01-01", "2025-08-31"
LOOKBACKS = (10, 21, 42)
QUANTILES = (0.1, 0.2)
WEIGHTS = ("equal",)
HOLDS = ("monthly", "biweekly")  # 12 个配置 = 3×2×1×2
SEED = 20261012
N_RANDOM_RESAMPLES = 200  # 阴性搜索面 = 12×200 = 2,400
COST_ONEWAY_BP = 17.5  # 冻结土规档：佣金2.5双边+印花10卖+滑点5（E4 verdict.md:7）
BAD_RET_ABS = 0.5  # |日收益|>0.5 视为脏值（实测该列 max=200400）
DSR_THRESHOLD = 0.95
PBO_THRESHOLD = 0.05
N_GROUPS, K_TEST = 8, 4
#: 考前预期（写死，禁事后改）
EXPECT_POSITIVE_NORMATIVE = "PASS"
EXPECT_POSITIVE_MYPREDICTION = "FAIL_under_M1_A"  # 01 号件线≈3.10 年化，A 股月频反转多头达不到
EXPECT_NEGATIVE = "FAIL"


def _prereg_sha(out_path: Path) -> str | None:
    """预登记件哈希：先找产物同目录，再退到仓根；找不到如实报 None（不崩、不假装有指纹）。"""
    for cand in (
        out_path.parent / "10_ruler_calibration_preregistration_v1.md",
        out_path.parent.parent / "10_ruler_calibration_preregistration_v1.md",
    ):
        if cand.exists():
            return _sha16(cand.read_text(encoding="utf-8"))
    return None


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _r(x, n=4):
    if x is None:
        return None
    v = float(x)
    return round(v, n) if math.isfinite(v) else None


# ---------------------------------------------------------------- 面板


def load_daily_returns(repo_root: Path, start: str, end: str) -> tuple[pd.DataFrame, dict]:
    """逐年分块取 A 股日收益（float32 宽表），脏值过滤计数如实报。"""
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn()
    years = range(int(start[:4]), int(end[:4]) + 1)
    frames = []
    for y in years:
        ys = f"{y}-01-01"
        ye = f"{y}-12-31"
        cols = conn.execute(
            "SELECT trade_date, symbol, pct_change FROM c1_market.kline_daily "
            f"WHERE market_type='A_share' AND trade_date BETWEEN '{max(ys, start)}' AND '{min(ye, end)}'",
            columnar=True,
        )
        if not cols or not len(cols[0]):
            continue
        f = pd.DataFrame(
            {"trade_date": cols[0], "symbol": pd.Categorical(cols[1]), "ret": np.asarray(cols[2], dtype=np.float64)}
        )
        frames.append(f)
    if not frames:
        raise SystemExit("[calib] 面板取数为空——如实中止，不出数")
    df = pd.concat(frames, ignore_index=True)
    total_rows = len(df)
    df["ret"] = pd.to_numeric(df["ret"], errors="coerce") / 100.0
    bad = int((df["ret"].abs() > BAD_RET_ABS).sum() + df["ret"].isna().sum())
    df = df[df["ret"].abs() <= BAD_RET_ABS]
    wide = df.pivot_table(index="trade_date", columns="symbol", values="ret", aggfunc="mean", observed=True)
    wide = wide.sort_index().astype("float32")
    meta = {
        "window": [start, end],
        "rows_fetched": total_rows,
        "rows_dropped_bad_or_nan": bad,
        "days": int(wide.shape[0]),
        "symbols": int(wide.shape[1]),
        "cells_available_pct": _r(100.0 * float(np.isfinite(wide.to_numpy()).mean()), 2),
        "dtype": "float32",
        "source": "c1_market.kline_daily.market_type='A_share' (DatabaseService CH 只读口)",
    }
    return wide, meta


# ---------------------------------------------------------------- 组合构造


def _rebalance_dates(idx: pd.DatetimeIndex, hold: str) -> list[int]:
    """月末/双周末调仓点位（索引位置）。"""
    d = pd.Series(idx)
    out = []
    if hold == "monthly":
        keys = [f"{t.year:04d}-{t.month:02d}" for t in idx]
        for i in range(len(idx) - 1):
            if keys[i] != keys[i + 1]:
                out.append(i)
    else:
        # 双周=每 10 个交易日
        out = [i for i in range(0, len(idx) - 1, 10)]
    return out


def build_portfolio_returns(
    wide: pd.DataFrame, lookback: int, quantile: float, hold: str, weight: str, seed: int | None = None
) -> tuple[np.ndarray, dict]:
    """月频短期反转（做多输家）或随机选股 → 逐日净收益序列。seed 非 None=阴性对照。"""
    R = wide.to_numpy(dtype=np.float64)
    T, N = R.shape
    dates = wide.index
    reb = [i for i in _rebalance_dates(dates, hold) if i >= lookback - 1]
    port = np.zeros(T, dtype=np.float64)
    held_days = 0
    turnover_sum = 0.0
    prev: set[int] = set()
    rng = np.random.default_rng(seed) if seed is not None else None
    for j, i in enumerate(reb):
        end = reb[j + 1] + 1 if j + 1 < len(reb) else T
        win = R[i - lookback + 1 : i + 1]
        ok = np.isfinite(win).sum(axis=0) >= max(3, int(lookback * 0.6))
        cand = np.where(ok)[0]
        if len(cand) < 10:
            continue
        cum = np.nansum(np.log1p(np.clip(win[:, cand], -0.9, None)), axis=0)
        if rng is None:
            order = np.argsort(cum)[: max(1, int(round(len(cand) * quantile)))]  # 输家=反转方向
        else:
            pick = rng.permutation(len(cand))[: max(1, int(round(len(cand) * quantile)))]
            order = np.sort(pick)
        sel = set(int(c) for c in cand[order])
        w = np.zeros(N, dtype=np.float64)
        w[list(sel)] = 1.0 / len(sel)
        seg = R[i + 1 : end]
        if seg.shape[0] == 0:
            prev = sel
            continue
        # 只取**本段持仓列**（冒烟实测：早前误用全市场掩码，令所有配置算出同一条
        # 全市场序列且 PBO 恒 0.5——列选择被静默吞掉，故本行必须显式取列）
        cols = sorted(sel)
        sub = seg[:, cols]
        m = np.isfinite(sub)
        rows = np.where(m.any(axis=1))[0]
        if rows.size == 0:
            prev = sel
            continue
        mm = m[rows]
        vals = np.where(mm, sub[rows], 0.0)
        daily = vals.sum(axis=1) / np.maximum(mm.sum(axis=1), 1)
        port[i + 1 + rows] += daily
        held_days += int(rows.size)
        turnover_sum += len(sel - prev) / max(len(sel), 1)
        prev = sel
    cost_per_reb = 2 * COST_ONEWAY_BP * 1e-4  # 卖旧+买新，按满换手计
    net = port.copy()
    for i in reb:  # 逐调仓点扣成本（摊在该持仓段首日，确定性且可复核）
        net[min(i + 1, T - 1)] -= cost_per_reb
    mu, sd = float(net.mean()), float(net.std(ddof=1))
    sr_annual = mu / sd * math.sqrt(PERIODS_PER_YEAR) if sd > 0 else float("nan")
    n_reb = len(reb)
    diag = {
        "rebalances": n_reb,
        "held_days": held_days,
        "mean_turnover": _r(turnover_sum / max(n_reb, 1), 3),
        "cost_drag_annual": _r(n_reb * cost_per_reb * PERIODS_PER_YEAR / max(T, 1), 4),
        "ann_return": _r(mu * PERIODS_PER_YEAR, 4),
        "ann_vol": _r(sd * math.sqrt(PERIODS_PER_YEAR), 4),
        "sharpe_annual": _r(sr_annual, 4),
        "skew": _r(float(pd.Series(net).skew()), 4),
        "excess_kurt": _r(float(pd.Series(net).kurt()), 4),
        "T": int((net != 0).sum()),
        "max_dd": _r(float((np.exp(np.cumsum(np.log1p(np.clip(net, -0.9, None)))) / np.maximum.accumulate(np.exp(np.cumsum(np.log1p(np.clip(net, -0.9, None)))) + 1e-12) - 1).min()), 4),
    }
    return net, diag


# ---------------------------------------------------------------- 判官（全部委托官方件）


def judge(net_by_cfg: dict[str, np.ndarray], n_trials: int, cfg_meta: dict) -> dict:
    from zephyr.backtest.core.cpcv import compute_pbo, generate_cpcv_splits
    from zephyr.simulation.deflated_sharpe_calculator import deflated_sharpe_from_moments, expected_max_sharpe_z

    out: dict = {"N_used": int(n_trials), "E_max_z": _r(expected_max_sharpe_z(int(n_trials)), 4), "configs": {}}
    names = list(net_by_cfg)
    M = np.vstack([net_by_cfg[k] for k in names])  # 候选 × 期
    best = max(names, key=lambda k: cfg_meta[k]["sharpe_annual"])
    for k in names:
        sr = cfg_meta[k]["sharpe_annual"]
        if sr is None or not math.isfinite(sr):
            out["configs"][k] = {"status": "NONFINITE_SHARPE"}
            continue
        sr_p = sr / math.sqrt(PERIODS_PER_YEAR)
        var, dsr, emax, degen = deflated_sharpe_from_moments(
            sr_p, int(n_trials), max(cfg_meta[k]["T"], 2), cfg_meta[k]["skew"] or 0.0, cfg_meta[k]["excess_kurt"] or 0.0
        )
        out["configs"][k] = {
            "sharpe_annual": sr,
            "T": cfg_meta[k]["T"],
            "skew": cfg_meta[k]["skew"],
            "excess_kurt": cfg_meta[k]["excess_kurt"],
            "ann_return": cfg_meta[k]["ann_return"],
            "max_dd": cfg_meta[k]["max_dd"],
            "dsr": _r(dsr, 6),
            "degenerate": bool(degen),
            "passes_dsr": bool((not degen) and dsr >= DSR_THRESHOLD),
        }
    # PBO：用该族全部候选的逐期序列做 CPCV（切分与 PBO 一律委托 cpcv）
    T = M.shape[1]
    splits = generate_cpcv_splits(T, n_groups=N_GROUPS, k_test=K_TEST)
    ok = np.isfinite(M).all(axis=1)
    Mf = M[ok]
    is_mat, oo_mat = [], []
    for s in splits:
        a, b = Mf[:, list(s.train_indices)], Mf[:, list(s.test_indices)]
        sa = a.std(axis=1, ddof=1)
        sb = b.std(axis=1, ddof=1)
        if (sa > 0).all() and (sb > 0).all():
            is_mat.append(a.mean(1) / sa)
            oo_mat.append(b.mean(1) / sb)
    if len(is_mat) >= 1 and Mf.shape[0] >= 2:
        res = compute_pbo(np.asarray(is_mat), np.asarray(oo_mat))
        out["pbo"] = {
            "pbo": _r(res["pbo"], 4),
            "mean_logit": _r(res["mean_logit"], 4),
            "n_splits_used": len(is_mat),
            "n_splits_generated": len(splits),
            "n_trials": int(res["n_trials"]),
            "passes_pbo_gate": bool(res["pbo"] <= PBO_THRESHOLD),
            "splits_spec": {"n_groups": N_GROUPS, "k_test": K_TEST, "t1": "None（日频点标签）", "embargo": 0},
        }
    else:
        out["pbo"] = {"computable": False, "code": "NOT_COMPUTABLE", "why": "候选有效行数<2 或无可用折"}
    b = out["configs"].get(best, {})
    out["selected_best"] = {
        "config": best,
        "sharpe_annual": b.get("sharpe_annual"),
        "dsr": b.get("dsr"),
        "passes_dsr": b.get("passes_dsr"),
        "degenerate": b.get("degenerate"),
    }
    return out


def oos_reading(wide_is: pd.DataFrame, repo_root: Path, best_cfg: tuple) -> dict:
    """闭卷段独立跑一次（不参与选择/判档，只为分开"尺过严"与"异象本身失效"两种解释）。"""
    wide_oos, meta = load_daily_returns(repo_root, OOS_START, OOS_END)
    lb, q, hold, w = best_cfg
    net, diag = build_portfolio_returns(wide_oos, lb, q, hold, w)
    sr = diag["sharpe_annual"]
    return {"config": list(best_cfg), "window": [OOS_START, OOS_END], "panel": meta, "sharpe_annual": sr,
            "ann_return": diag["ann_return"], "max_dd": diag["max_dd"], "note": "P-1 闭卷段：不参与选择与判档"}


# ---------------------------------------------------------------- 试次记账（如实尝试，被拒留证）


def record_trials(repo_root: Path, n_trials: int) -> dict:
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    try:
        res = TrialLedger(
            registry_path=repo_root / "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
        ).record_run(
            "calibration_ruler_exam",
            "ruler-calib-20261012-full",
            int(n_trials),
            note=(
                "令⑥ 尺子校准正式全量批=2,412 次（阳性 12 配置＋阴性 2,400 配置，2020-01..2023-12）；"
                "真源=docs/_working/statsgov_campaign/11_ruler_calibration_v1.yaml；"
                "追加更正留痕：先前 batch_id=ruler-calib-20261012 那行 n_trials=48 是冒烟批"
                "（12 阳性＋3×12=36 阴性，窗口仅 2023 年），按禁 UPDATE/DELETE 的追加更正行方式保留不删，"
                "两批合计真实烧掉 2,460 次；冒烟批的 note 文案误写 2400，以本行为准"
            ),
            recorded_by="st-statsgov-20261012",
        )
        return {"attempted": True, "ok": True, "result": {k: str(v)[:80] for k, v in res.items()}}
    except Exception as exc:  # noqa: BLE001 — 四病根之一（护栏常驻拒写），必须原样留证不粉饰
        return {"attempted": True, "ok": False, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}


def measure_denominator(repo_root: Path) -> dict:
    """M1=A 主尺运行时重测：账面累计＋磁盘全部未入账 grid 试次。"""
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    reg_path = repo_root / "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
    book = TrialLedger(registry_path=reg_path).cumulative_trials()
    import yaml

    y = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    records = {str(r.get("batch_id")) for r in (y.get("batch_records") or [])}
    missing = 0
    for s in sorted((repo_root / "data/strategy_intake").glob("grid_*/summary.json")):
        bid = f"grid_{s.parent.name[len('grid_'):]}"
        if bid in records:
            continue
        try:
            summ = json.loads(s.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        n = summ.get("evaluated")
        if n is None:
            n = summ.get("n_sampled")
        if n:
            missing += int(n)
    return {"book_cumulative": int(book), "disk_unrecorded": int(missing), "primary_denominator_N": int(book) + int(missing)}


# ---------------------------------------------------------------- 主流程


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md-out", default="")
    ap.add_argument("--random-resamples", type=int, default=N_RANDOM_RESAMPLES, help="阴性重抽次数（冒烟用小数）")
    ap.add_argument("--is-start", default=IS_START)
    ap.add_argument("--is-end", default=IS_END)
    args = ap.parse_args(argv)
    n_res = args.random_resamples
    is_start, is_end = args.is_start, args.is_end
    repo = Path(args.repo_root).resolve()
    _bootstrap(repo)

    outp0 = Path(args.out)
    denom = measure_denominator(repo)
    N = denom["primary_denominator_N"]
    wide, panel_meta = load_daily_returns(repo, is_start, is_end)

    pos_series: dict[str, np.ndarray] = {}
    pos_meta: dict[str, dict] = {}
    pos_cfgs: dict[str, tuple] = {}
    for lb in LOOKBACKS:
        for q in QUANTILES:
            for hold in HOLDS:
                for w in WEIGHTS:
                    name = f"REV_L{lb}_q{int(q*100)}_{hold}_{w}"
                    net, diag = build_portfolio_returns(wide, lb, q, hold, w)
                    pos_series[name], pos_meta[name], pos_cfgs[name] = net, diag, (lb, q, hold, w)
    pos = judge(pos_series, N, pos_meta)

    rng = np.random.default_rng(SEED)
    neg_series: dict[str, np.ndarray] = {}
    neg_meta: dict[str, dict] = {}
    for rep in range(n_res):
        for lb in LOOKBACKS:
            for q in QUANTILES:
                for hold in HOLDS:
                    name = f"RND_r{rep}_L{lb}_q{int(q*100)}_{hold}"
                    net, diag = build_portfolio_returns(
                        wide, lb, q, hold, "equal", seed=SEED + rep * 1000 + lb * 10 + int(q * 100)
                    )
                    neg_series[name], neg_meta[name] = net, diag
    # 管路自检（可红）：不同配置/不同随机种子必须给出**不同**序列。
    # 冒烟实测这条抓到过"全市场掩码"bug（所有配置同序列、PBO 恒 0.5）。
    def _distinct_pct(series_map: dict[str, np.ndarray]) -> float:
        ks = list(series_map)
        pairs = [(a, b) for i, a in enumerate(ks) for b in ks[i + 1 : i + 4]]
        same = sum(1 for a, b in pairs if np.allclose(series_map[a], series_map[b]))
        return 100.0 * (1 - same / max(len(pairs), 1))

    sanity = {
        "positive_configs_distinct_series_pct": _r(_distinct_pct(pos_series), 2),
        "negative_configs_distinct_series_pct": _r(_distinct_pct(neg_series), 2) if neg_series else None,
        "gate": "低于 90% 判管路退化（选择被静默吞掉），本实验不出结论",
    }
    if (sanity["positive_configs_distinct_series_pct"] or 0) < 90 or (
        neg_series and (sanity["negative_configs_distinct_series_pct"] or 0) < 90
    ):
        raise SystemExit(f"[calib] 管路自检红：配置间序列不唯一 {sanity}")
    neg = judge(neg_series, N, neg_meta)

    best_name = pos["selected_best"]["config"]
    oos = oos_reading(wide, repo, pos_cfgs[best_name])

    n_trials = len(pos_series) + len(neg_series)
    acct = record_trials(repo, n_trials)

    p_pass = bool(pos["selected_best"]["passes_dsr"])
    n_pass = bool(neg["selected_best"]["passes_dsr"])
    if p_pass and not n_pass:
        reading = "尺子校准正常（阳过·阴挂）"
    if (not p_pass) and (not n_pass):
        reading = "尺过严：选择惩罚压死真异象 ⇒ 按令⑥ 判读=停挖修尺并回报（禁把'0 通过'同时读作'矿里暂无金'）"
    elif p_pass and n_pass:
        reading = "尺过松：给噪声加冕 ⇒ 停挖修尺并回报"
    elif (not p_pass) and n_pass:
        reading = "尺两头坏（真异象不过·噪声冠军反过）⇒ 立即停挖出双缺陷案卷"
    oos_sig = oos.get("sharpe_annual")
    if oos_sig is not None and isinstance(oos_sig, (int, float)) and oos_sig > 1.0:
        reading += "；附：闭卷段该配置仍有信号 ⇒ '异象失效'解释被削弱，指向尺子口径"
    elif oos_sig is not None and isinstance(oos_sig, (int, float)) and oos_sig <= 0:
        reading += "；附：闭卷段该配置亦走弱 ⇒ '本窗异象弱'与'尺过严'两解并存，须呈 Owner 分判"

    doc = {
        "ttl": "task_bound",
        "title": "尺子校准实验 v1 实测结果（令⑥ 采纳件）",
        "preregistration": "docs/_working/statsgov_campaign/10_ruler_calibration_preregistration_v1.md",
        "prereg_sha16_at_run": _prereg_sha(outp0),
        "produced_by": ".runtime/tmp/statsgov/ruler_calibration.py",
        "denominator_M1_A": denom,
        "panel": panel_meta,
        "plumbing_sanity": sanity,
        "expectations_frozen": {
            "positive_normative": EXPECT_POSITIVE_NORMATIVE,
            "positive_machine_prediction": EXPECT_POSITIVE_MYPREDICTION,
            "negative": EXPECT_NEGATIVE,
            "thresholds": {"dsr": DSR_THRESHOLD, "pbo": PBO_THRESHOLD},
        },
        "positive_control": {"n_configs": len(pos_series), **pos},
        "negative_control": {"n_configs": len(neg_series), **neg},
        "closed_book_segment_not_for_grading": oos,
        "trial_accounting": {"n_trials_this_experiment": n_trials, "ledger_write": acct},
        "reading": reading,
        "anti_cherry_pick_clause": "本件跑后禁换 N 口径重报、禁改 q/L/成本档再跑挑好看的；见 10 号件 §6",
    }
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(doc, ensure_ascii=False, indent=1, default=str)
    import yaml as _y

    outp.write_text(_y.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8", newline="\n")
    print(f"[calib] yaml 产物={outp} bytes={outp.stat().st_size}")
    print(f"[calib] 判读={reading}")
    print(f"[calib] 阳性 best={pos['selected_best']}")
    print(f"[calib] 阴性 best={neg['selected_best']}")
    print(f"[calib] 记账={acct}")
    if args.md_out:
        md = [
            "---",
            "ttl: task_bound",
            "---",
            "",
            "# 尺子校准实验报告 v1（机生三段：预期 / 实测 / 判读）",
            "",
            f"- 判官与阈值的唯一真源=预登记件 `10_ruler_calibration_preregistration_v1.md`（sha16={doc['prereg_sha16_at_run']}）",
            f"- 主尺（晨裁 M1=A，运行时重测）：账面 {denom['book_cumulative']} ＋ 磁盘未入账 {denom['disk_unrecorded']} = **N={denom['primary_denominator_N']}**",
            f"- 面板：{panel_meta['days']} 交易日 × {panel_meta['symbols']} 票，脏值(|r|>{BAD_RET_ABS})剔除 {panel_meta['rows_dropped_bad_or_nan']} 行，可用格 {panel_meta['cells_available_pct']}%",
            f"- 本实验自烧试次：{n_trials}（记账结果={'已入 N 账本' if acct.get('ok') else '被拒——见下'}）",
            "",
            "## 一、预期（测量前冻结，禁事后改）",
            "",
            "| 对照 | 规范预期 | 本机数值预判（可被证伪） |",
            "|---|---|---|",
            f"| 阳性（月频短反转，{len(pos_series)} 配置搜索后取 IS 最优） | 过（真异象应过一把好尺） | {EXPECT_POSITIVE_MYPREDICTION}（01 号件线≈3.10 年化） |",
            f"| 阴性（随机选股，{len(neg_series)} 配置搜索后取 IS 最优） | 不过（尺不得给噪声加冕） | 同预期 |",
            "",
            "## 二、实测",
            "",
            "| 对照 | 被选中配置 | IS 年化 Sharpe | T | DSR(M1=A 尺) | 过 0.95? | PBO | 过 0.05? |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for tag, blk in (("阳性", pos), ("阴性", neg)):
            sb = blk["selected_best"]
            cfg = sb["config"]
            c = blk["configs"].get(cfg, {})
            pbo = (blk.get("pbo") or {}).get("pbo")
            md.append(
                f"| {tag} | `{cfg}` | {c.get('sharpe_annual')} | {c.get('T')} | {c.get('dsr')} | "
                f"{'是' if c.get('passes_dsr') else '否'}{'（退化态=不可判定）' if c.get('degenerate') else ''} | "
                f"{pbo} | {'是' if (blk.get('pbo') or {}).get('passes_pbo_gate') else '否'} |"
            )
        md += [
            "",
            f"- 阳性搜索面最优 {len([k for k, v in pos['configs'].items() if v.get('passes_dsr')])}/{len(pos['configs'])} 个配置过线；"
            f"阴性 {len([k for k, v in neg['configs'].items() if v.get('passes_dsr')])}/{len(neg['configs'])} 个过线",
            f"- 闭卷段（2024-01-01..2025-08-31，不参与判档）该配置年化 Sharpe={oos.get('sharpe_annual')}，"
            f"年化收益={oos.get('ann_return')}，最大回撤={oos.get('max_dd')}",
            f"- 记账留证：{json.dumps(acct, ensure_ascii=False)[:400]}",
            "",
            "## 三、判读（按令⑥ 三态表，跑前定死）",
            "",
            f"**{reading}**",
            "",
            "- 反挑尺条款：本表跑后禁换 N 口径重报、禁改 q/L/成本档再跑挑好看的（10 号件 §6）。",
            "- 若判\"尺过严\"：修法选项呈 Owner/统筹，本班不自改任何阈值。",
            "",
        ]
        mp = Path(args.md_out)
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text("\n".join(md), encoding="utf-8", newline="\n")
        print(f"[calib] md 报告={mp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## `ruler_calibration_report.py` —— 两轴后处理件（含等权市场基准与判读，产物 11 报告 md/12 判定 yaml）

- 原文行数=274，本证据件收录=271 行（剔除 3 行 `# [TTL]/[STARTUP]/[CONSUMERS]` 头，避免与文档头族门禁冲突）
- sha256(原文全文)=b3fc5b2875d9704e4e45045d3959b49fa1dd49540ba93b3a6fab2b4614c0abb0
- 粘回路径=`scripts/backtest/`+`tests/backtest/` 配平（正式落地时须补 15 字段头与 translation/token，见 22 号件 §6.2）

```python
"""尺子校准后处理：两轴分离读数 + 等权市场基准（令⑥ §7 追加持行）。

数学零自造：DSR 一律委托 MOD-SIM-024；面板与组合构造复用跑批件同一函数（同判官同料）。
本件不重跑 2,400 个配置的搜索（贵的那段已完成），只做：①各配置在**自身搜索面 N** 下的 DSR
（用 11 号件已存的 SR/T/偏度/峰度复算）；②等权市场基准与最优配置的超额序列（只重建两条）。
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

LANE = Path(__file__).resolve().parents[3]
REPO = Path("D:/ZephyrAlpha")
sys.path.insert(0, str(REPO / "src"))

_spec = importlib.util.spec_from_file_location("rc", LANE / ".runtime/tmp/statsgov/ruler_calibration.py")
rc = importlib.util.module_from_spec(_spec)
sys.modules["rc"] = rc
_spec.loader.exec_module(rc)


def dsr_official(sr_annual: float, n_trials: int, t: int, skew, kurt):
    from zephyr.simulation.deflated_sharpe_calculator import deflated_sharpe_from_moments

    sr_p = float(sr_annual) / math.sqrt(rc.PERIODS_PER_YEAR)
    var, dsr, emax, degen = deflated_sharpe_from_moments(sr_p, int(n_trials), int(max(t, 2)), float(skew or 0.0), float(kurt or 0.0))
    return {"dsr": round(float(dsr), 6), "degenerate": bool(degen), "E_max_z": round(float(emax), 4),
            "passes": bool((not degen) and dsr >= rc.DSR_THRESHOLD)}


def sharpe(x):
    x = np.asarray(x, dtype=float)
    sd = x.std(ddof=1)
    return float(x.mean() / sd * math.sqrt(rc.PERIODS_PER_YEAR)) if sd > 0 else None


def main() -> int:
    d = yaml.safe_load((LANE / "docs/_working/statsgov_campaign/11_ruler_calibration_v1.yaml").read_text(encoding="utf-8"))
    N_gov = int(d["denominator_M1_A"]["primary_denominator_N"])
    size_p = LANE / "docs/_working/statsgov_campaign/13_ruler_calibration_size_control_v1.yaml"
    size = yaml.safe_load(size_p.read_text(encoding="utf-8")) if size_p.exists() else None


    wide_is, meta_is = rc.load_daily_returns(REPO, rc.IS_START, rc.IS_END)
    mkt_is = np.nanmean(wide_is.to_numpy(dtype=np.float64), axis=1)
    wide_oos, meta_oos = rc.load_daily_returns(REPO, rc.OOS_START, rc.OOS_END)
    mkt_oos = np.nanmean(wide_oos.to_numpy(dtype=np.float64), axis=1)

    own = {}
    for tag, blk, n_own in (("positive_control", d["positive_control"], d["positive_control"]["n_configs"]),
                            ("negative_control", d["negative_control"], d["negative_control"]["n_configs"])):
        rows = {}
        for cfg, v in blk["configs"].items():
            if not isinstance(v, dict) or v.get("sharpe_annual") is None:
                continue
            rows[cfg] = {"sharpe_annual": v["sharpe_annual"], "T": v.get("T"),
                         "dsr_own_N": dsr_official(v["sharpe_annual"], n_own, v.get("T") or 2, v.get("skew"), v.get("excess_kurt")),
                         "dsr_governance_N": {"dsr": v.get("dsr"), "passes": v.get("passes_dsr")}}
        best = blk["selected_best"]["config"]
        own[tag] = {"n_own_trials": n_own, "best_config": best,
                    "best_dsr_own_N": rows[best]["dsr_own_N"], "best_dsr_governance_N": rows[best]["dsr_governance_N"],
                    "n_pass_own_N": sum(1 for r in rows.values() if r["dsr_own_N"]["passes"]),
                    "n_pass_governance_N": sum(1 for r in rows.values() if r["dsr_governance_N"]["passes"]),
                    # 全量逐配置原始值在 11 号件；本件只留两端各 5 个，防产物体积无谓膨胀
                    "configs_excerpt": dict(sorted(rows.items(), key=lambda kv: -(kv[1]["sharpe_annual"] or -9))[:5]),
                    "configs_worst_excerpt": dict(sorted(rows.items(), key=lambda kv: (kv[1]["sharpe_annual"] or 9))[:5]),
                    "configs_full_rows_in": "docs/_working/statsgov_campaign/11_ruler_calibration_v1.yaml"}

    pb = own["positive_control"]["best_config"]
    nb = own["negative_control"]["best_config"]
    # 重建两条序列：阳性最优、阴性最优（成本/窗口/面板与搜索时逐字同）
    def _rebuild(name: str):
        if name.startswith("REV"):
            parts = name.split("_")
            L = int(parts[1][1:]); qq = int(parts[2][1:]) / 100.0; hold_ = parts[3]
            net, diag = rc.build_portfolio_returns(wide_is, L, qq, hold_, "equal")
            return net, diag, None
        parts = name.split("_")
        rep = int(parts[1][1:]); L = int(parts[2][1:]); qq = int(parts[3][1:]) / 100.0; hold_ = parts[4]
        seed = rc.SEED + rep * 1000 + L * 10 + int(qq * 100)
        net, diag = rc.build_portfolio_returns(wide_is, L, qq, hold_, "equal", seed=seed)
        return net, diag, seed

    net_pos, diag_pos, _ = _rebuild(pb)
    net_neg, diag_neg, _ = _rebuild(nb)
    bench = {
        "ew_market_is": {"window": [rc.IS_START, rc.IS_END], "sharpe_annual": round(sharpe(mkt_is), 4),
                         "ann_return": round(float(np.nanmean(mkt_is) * rc.PERIODS_PER_YEAR), 4), "T": int(len(mkt_is))},
        "ew_market_oos": {"window": [rc.OOS_START, rc.OOS_END], "sharpe_annual": round(sharpe(mkt_oos), 4),
                          "ann_return": round(float(np.nanmean(mkt_oos) * rc.PERIODS_PER_YEAR), 4), "T": int(len(mkt_oos))},
        "note": "等权全市场基准（逐日均横截面可用票均值，未扣成本）——用来分开『异象弱』与『大盘弱』两种解释",
    }
    exc_pos = net_pos - mkt_is
    exc_neg = net_neg - mkt_is
    excess = {
        "positive_best": {"config": pb, "abs_sharpe": diag_pos["sharpe_annual"], "excess_sharpe": round(sharpe(exc_pos), 4),
                          "excess_ann_return": round(float(np.mean(exc_pos) * rc.PERIODS_PER_YEAR), 4)},
        "negative_best": {"config": nb, "abs_sharpe": diag_neg["sharpe_annual"], "excess_sharpe": round(sharpe(exc_neg), 4),
                          "excess_ann_return": round(float(np.mean(exc_neg) * rc.PERIODS_PER_YEAR), 4)},
        "caveat": "超额为算术差（等权基准，未对 beta 中性化）；A 股 long-only 无法做空，故超额只表相对强弱不表可实现对冲收益",
    }

    pos_pb = d["positive_control"]["pbo"]["pbo"]
    neg_pb = d["negative_control"]["pbo"]["pbo"]
    pbo_pathology = (
        f"PBO 不能当全仓统一门，但它的失效方式要说准（三族同尺实测）：①小市值真异象族 PBO={size['pbo_own_pool']['pbo'] if size else 'NA'}=**判对**；"
        f"②月频反转族 PBO={pos_pb}=**也判对**（该族本窗确无稳健效应）；"
        f"③2,400 个随机选股族 PBO={neg_pb}=**判错**——噪声冠军照样过 0.05 门。"
        "机理不是'方向反'而是**在同质池上失去判别力**：随机选股组合≈全市场组合，池内成员彼此高相关，"
        "IS 最优≈池中位，故其 OOS 也很少落到中位以下 ⇒ PBO 恒低。"
        "⇒ PBO≤0.05 只可作**族内相对指标**（池成员差异明显时），不可作跨族统一晋级门；晨裁 M3 的那一半应撤回。"
        "对照之下 DSR 尺在三族上都给出了正确方向（噪声冠军在自身 N=2,400 与治理 N 下均被挂）⇒ 本案未证伪 DSR。"
    )

    reading_validity = (
        f"有效性轴（各自搜索面 N）：阳性最优 DSR={own['positive_control']['best_dsr_own_N']['dsr']}（N={own['positive_control']['n_own_trials']}，"
        f"过线={own['positive_control']['best_dsr_own_N']['passes']}）；阴性最优 DSR={own['negative_control']['best_dsr_own_N']['dsr']}"
        f"（N={own['negative_control']['n_own_trials']}，过线={own['negative_control']['best_dsr_own_N']['passes']}）。"
    )
    reading_gov = (
        f"治理轴（M1=A，N={N_gov}）：阳性 {own['positive_control']['n_pass_governance_N']}/12、"
        f"阴性 {own['negative_control']['n_pass_governance_N']}/2400 过线。"
    )
    if (not own["positive_control"]["best_dsr_own_N"]["passes"]) and (not own["negative_control"]["best_dsr_own_N"]["passes"]):
        verdict = (
            "两把 DSR 都判不过 ⇒ 按令⑥ 三态表落『阳性挂·阴性挂=尺过严』一侧**不成立**，因为阴性同样被挂住（尺没给噪声加冕）；"
            "真实读数=本窗内该异象本身弱（绝对 Sharpe 0.223、超额 "
            f"{excess['positive_best']['excess_sharpe']}），弱到 2,400 次随机选股的最优（0.368）都能压过它。"
            "⇒ 结论应是『矿里暂无金（该轴该窗）』＋『PBO 统一门方向错』两条，而不是『停挖修 DSR 尺』。"
        )
    else:
        verdict = "见 12 号件 yaml 原始两轴值，按 §7 三态表判读"

    # 阳性对照第二件（小市值）若在场则并入，并据此改判读：阳性前提是否立得住决定"尺过严"能不能下
    if size:
        s_t = size["dsr_validity_own_N"]["N"]
        s_dsr = size["dsr_validity_own_N"]["dsr"]
        s_sr = size["dsr_validity_own_N"]["sharpe_annual"]
        s_T = size["configs"][size["best_config"]]["T"]
        s_tstat = round(s_sr / math.sqrt(rc.PERIODS_PER_YEAR) / math.sqrt((1 + s_sr**2 / 2 / s_T) / max(s_T - 1, 1)), 4) if s_T > 2 else None
        s_emax = round(float(rc.expected_max_sharpe_z(int(s_t))), 4) if hasattr(rc, "expected_max_sharpe_z") else None
        verdict = (
            "校准结论=**部分有效，不能判 DSR 尺过严**。三件实测：①阴性（2,400 随机）在两把 N 下 DSR 全挂 ⇒ "
            "DSR 尺没有给噪声加冕（这一侧未被证伪）；②阳性一件（月频反转）对等权大盘超额为负 ⇒ 它不是合格的阳性对照；"
            f"③阳性二件（小市值 total_mv q10 monthly，2021-01..2023-12）绝对 Sharpe={s_sr}、超额 {size['best_excess_over_ew_market']['sharpe_annual']}、"
            f"PBO={size['pbo_own_pool']['pbo']}（过 0.05 门）——是真异象，但其单检验 t≈{s_tstat}（T={s_T}），"
            f"DSR@自身搜索面 N={s_t} 仅 {s_dsr}，不过 0.95。⇒ 该阳性连学术 HLZ t>3.0 也够不着，"
            "故本案**无法**据它判'尺过严'：阳性对照在本窗本身就不达标（样本只有 730 天，多头单因子的 t 天花板就在那里）。"
            "被证据钉死的是另一条：**PBO 不能当全仓统一门**——真异象 0.0 过、2,400 噪声冠军 0.0286 也过（无判别力），"
            "而反转族 0.4714 反被挂（池构成依赖）。⇒ 晨裁 M3 的'PBO≤0.05 全仓统一门'应撤回；DSR 尺保留 0.95 但每笔候选须同时报"
            "单检验 t 与该 N 下所需 t（让'差多少'可见），并把'更长窗/月频观测的阳性对照'列为下一轮校准前置。"
        )
    out = {
        "ttl": "task_bound",
        "title": "尺子校准两轴判定 v1（后处理件，令⑥ §7）",
        "produced_by": ".runtime/tmp/statsgov/ruler_calibration_report.py",
        "raw_run": "docs/_working/statsgov_campaign/11_ruler_calibration_v1.yaml",
        "prereg": "docs/_working/statsgov_campaign/10_ruler_calibration_preregistration_v1.md",
        "plumbing_sanity": d["plumbing_sanity"],
        "positive_control_2_size": size,
        "denominator": d["denominator_M1_A"],
        "panel_is": meta_is,
        "panel_oos": meta_oos,
        "axis_validity_and_governance": own,
        "benchmark": bench,
        "excess_over_benchmark": excess,
        "pbo_axis": {"positive_pbo": pos_pb, "negative_pbo": neg_pb, "gate": rc.PBO_THRESHOLD,
                     "finding": pbo_pathology},
        "trial_accounting": d["trial_accounting"],
        "reading_validity": reading_validity,
        "reading_governance": reading_gov,
        "verdict": verdict,
        "expectations_vs_measured": {
            "positive_normative_EXPECTED": "过",
            "positive_machine_prediction_EXPECTED": "FAIL_under_M1_A",
            "positive_MEASURED": {"own_N_dsr": own["positive_control"]["best_dsr_own_N"]["dsr"],
                                   "own_N_pass": own["positive_control"]["best_dsr_own_N"]["passes"],
                                   "gov_N_pass": own["positive_control"]["best_dsr_governance_N"]["passes"]},
            "negative_EXPECTED": "不过",
            "negative_MEASURED": {"own_N_dsr": own["negative_control"]["best_dsr_own_N"]["dsr"],
                                   "own_N_pass": own["negative_control"]["best_dsr_own_N"]["passes"],
                                   "gov_N_pass": own["negative_control"]["best_dsr_governance_N"]["passes"],
                                   "pbo_pass": d["negative_control"]["pbo"]["passes_pbo_gate"]},
        },
    }
    (LANE / "docs/_working/statsgov_campaign/12_ruler_calibration_verdict_v1.yaml").write_text(
        yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8", newline="\n")

    md = [
        "---",
        "ttl: task_bound",
        "---",
        "",
        "# 尺子校准实验报告 v1（机生三段：预期 / 实测 / 判读）",
        "",
        "真源：`11_*.yaml`=原始实测，`12_*.yaml`=两轴判定（本件覆写早期单轴 md 的原因=预登记 §7 两轴分离追加）；",
        f"判官与口径冻结件=`10_ruler_calibration_preregistration_v1.md`（sha16={d['prereg_sha16_at_run']}）。",
        f"管路自检：配置间序列唯一性 阳性 {d['plumbing_sanity']['positive_configs_distinct_series_pct']}%／阴性 {d['plumbing_sanity']['negative_configs_distinct_series_pct']}%（闸=90%；冒烟阶段该闸抓到过『全市场掩码吞掉列选择、PBO 恒 0.5』的真 bug）。",
        "",
        "## 一、预期（测量前冻结）",
        "",
        "| 对照 | 规范预期 | 本机数值预判（写明以便被证伪） |",
        "|---|---|---|",
        "| 阳性=月频短反转（12 配置搜索后取 IS 最优） | 过 | 在治理轴(M1=A,N=91,400)下不过——按 01 号件线≈3.10 年化 |",
        "| 阴性=随机选股（2,400 配置搜索后取 IS 最优） | 不过 | 同预期 |",
        "",
        "## 二、实测",
        "",
        "| 量 | 阳性 | 阴性 |",
        "|---|---|---|",
        f"| 最优 IS 年化 Sharpe（绝对） | {own['positive_control']['configs_excerpt'][pb]['sharpe_annual']} | {own['negative_control']['configs_excerpt'][nb]['sharpe_annual']} |",
        f"| 对等权全市场超额年化 Sharpe | {excess['positive_best']['excess_sharpe']} | {excess['negative_best']['excess_sharpe']} |",
        f"| DSR（有效性轴 N=自身搜索面 {own['positive_control']['n_own_trials']}/{own['negative_control']['n_own_trials']}） | {own['positive_control']['best_dsr_own_N']['dsr']} | {own['negative_control']['best_dsr_own_N']['dsr']} |",
        f"| DSR（治理轴 N={N_gov}） | {own['positive_control']['best_dsr_governance_N']['dsr']} | {own['negative_control']['best_dsr_governance_N']['dsr']} |",
        f"| 过 0.95 的配置数（有效性轴） | {own['positive_control']['n_pass_own_N']}/12 | {own['negative_control']['n_pass_own_N']}/2400 |",
        f"| PBO（同池内） | {pos_pb} | {neg_pb}（过 ≤0.05 门={d['negative_control']['pbo']['passes_pbo_gate']}） |",
        f"| 闭卷段 2024-01..2025-08 该配置年化 Sharpe | {d['closed_book_segment_not_for_grading'].get('sharpe_annual')} | — |",
        "",
        f"基准（等权全市场，未扣成本）：IS 年化 Sharpe={bench['ew_market_is']['sharpe_annual']}（年化收益 {bench['ew_market_is']['ann_return']}），"
        f"OOS={bench['ew_market_oos']['sharpe_annual']}（年化收益 {bench['ew_market_oos']['ann_return']}）。",
        "",
        *(
            []
            if not size
            else [
                "### 阳性对照第二件（小市值，2021-01..2023-12）",
                "",
                f"- 最优配置 `{size['best_config']}`：绝对年化 Sharpe={size['dsr_validity_own_N']['sharpe_annual']}，"
                f"对等权全市场超额年化 Sharpe={size['best_excess_over_ew_market']['sharpe_annual']}（年化超额收益 {size['best_excess_over_ew_market']['ann_return']}），T={size['configs'][size['best_config']]['T']}",
                f"- DSR：有效性轴（N={size['dsr_validity_own_N']['N']}）={size['dsr_validity_own_N']['dsr']}（过线={size['dsr_validity_own_N']['passes_dsr']}）；"
                f"治理轴（N={size['dsr_governance_N']['N']}）={size['dsr_governance_N']['dsr']}（过线={size['dsr_governance_N']['passes_dsr']}）；过线配置数 own={size['n_pass_own_N']}/8, gov={size['n_pass_governance_N']}/8",
                f"- PBO（同池 8 配置）={size['pbo_own_pool']['pbo']}；等权基准该窗年化 Sharpe={size['ew_market_benchmark']['sharpe_annual']}",
                f"- 试次记账：{size['trial_accounting']['ledger_write'].get('status')} n_trials={size['trial_accounting']['n_trials']} batch_id={size['trial_accounting']['ledger_write'].get('batch_id')}",
                "",
            ]
        ),
        "## 三、判读（按预登记 §5 三态表 + §7 两轴分离）",
        "",
        f"1. {reading_validity}",
        f"2. {reading_gov}",
        f"3. {verdict}",
        f"4. **PBO 轴独立结论（须呈 Owner，因为它直接冲掉晨裁 M3 的一半）：** {pbo_pathology}",
        "5. 禁自欺条款：本案不能同时把『0 通过』读作『尺有病』与『矿里没金』。本读数为后者＋PBO 门方向错，"
        "故 DSR 尺本身**未被证伪**（它确实挂住了 2,400 个噪声冠军）；被证伪的是『PBO≤0.05 当全仓统一门』。",
        "6. 本班不自改任何阈值：修法只列选项呈裁（P-3）。",
        "",
        "## 四、限制（如实）",
        "",
        "- 组合=多头等权、月/双周调仓、扣 17.5bp×双边成本；未做 beta 中性化、未处理涨跌停不可成交（不可成交会让异象被**高估**，故其弱是保守方向）。",
        "- 幸存者偏差：面板只含同期有数据的票（会**抬高**异象表现，弱结论因此更强）。",
        "- 市值表 `stock_daily_basic` 2021-01 才有数据，故小市值阳性对照未跑（如实标未跑，见令⑥ 二选一许可）。",
        f"- 本实验自烧 {d['trial_accounting']['n_trials_this_experiment']} 次试次，记账结果：{json.dumps(d['trial_accounting']['ledger_write'], ensure_ascii=False)[:220]}",
        "",
    ]
    (LANE / "docs/_working/statsgov_campaign/11_ruler_calibration_report_v1.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    print("[report] 12_*.yaml + 11_*.md 已写")
    print("[report] verdict=", verdict[:220])
    print("[report] pbo finding=", pbo_pathology[:180])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## `ruler_calibration_size.py` —— 阳性对照第二件＝小市值（产物 13 号件，8 配置）

- 原文行数=222，本证据件收录=219 行（剔除 3 行 `# [TTL]/[STARTUP]/[CONSUMERS]` 头，避免与文档头族门禁冲突）
- sha256(原文全文)=687b7d28f545c346d6f70659dd4c375d85fee245f8ffd61b3fa1eaa8e22d1eca
- 粘回路径=`scripts/backtest/`+`tests/backtest/` 配平（正式落地时须补 15 字段头与 translation/token，见 22 号件 §6.2）

```python
"""尺子校准 · 阳性对照第二件=小市值（令⑥ 二选一之另一件，窗口受市值表起点限制 2021-01..2023-12）。

为什么要它：第一件（月频反转）实测对等权全市场超额为负 ⇒ 它**不是一个立得住的阳性对照**，
"两把 DSR 都挂"因此既不能证真尺也不能证伪尺。本件换一个在窗内**确有正向超额**的共识异象，
有效性轴才谈得上校准。
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

LANE = Path(__file__).resolve().parents[3]
REPO = Path("D:/ZephyrAlpha")
sys.path.insert(0, str(REPO / "src"))

_spec = importlib.util.spec_from_file_location("rc", LANE / ".runtime/tmp/statsgov/ruler_calibration.py")
rc = importlib.util.module_from_spec(_spec)
sys.modules["rc"] = rc
_spec.loader.exec_module(rc)

S_START, S_END = "2021-01-01", "2023-12-29"
BASES = ("total_mv", "circ_mv")
QUANTS = (0.1, 0.2)
HOLDS = ("monthly", "biweekly")


def month_end_caps(start: str, end: str) -> pd.DataFrame:
    """市值按'每月最后一个交易日'取值（宽表：行=月末，列=symbol）。"""
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn()
    frames = []
    for y in range(int(start[:4]), int(end[:4]) + 1):
        ys, ye = f"{y}-01-01", f"{y}-12-31"
        cols = conn.execute(
            "SELECT trade_date, symbol, total_mv, circ_mv FROM c1_market.stock_daily_basic "
            f"WHERE trade_date BETWEEN '{max(ys,start)}' AND '{min(ye,end)}'",
            columnar=True,
        )
        if not cols or not len(cols[0]):
            continue
        frames.append(
            pd.DataFrame(
                {
                    "trade_date": cols[0],
                    "symbol": pd.Categorical(cols[1]),
                    "total_mv": np.asarray(cols[2], dtype=np.float64),
                    "circ_mv": np.asarray(cols[3], dtype=np.float64),
                }
            )
        )
    df = pd.concat(frames, ignore_index=True)
    df["ym"] = pd.to_datetime(df["trade_date"]).values.astype("datetime64[M]")
    last = df.groupby(["ym", "symbol"], observed=True)["trade_date"].transform("max")
    df = df[df["trade_date"] == last]
    out = df.pivot_table(index="ym", columns="symbol", values=["total_mv", "circ_mv"], aggfunc="last", observed=True)
    return out.sort_index()


def size_portfolio(price_wide: pd.DataFrame, caps: pd.DataFrame, basis: str, quantile: float, hold: str) -> tuple[np.ndarray, dict]:
    """做多最小市值 q 分位（等权），月末/双周末调仓，扣同一成本档。"""
    R = price_wide.to_numpy(dtype=np.float64)
    T, N = R.shape
    dates = price_wide.index
    syms = list(price_wide.columns)
    cap_w = caps[basis]
    cap_rows = {pd.Period(str(t), "M"): i for i, t in enumerate(cap_w.index)}
    reb = [i for i in rc._rebalance_dates(dates, hold)]
    port = np.zeros(T)
    prev: set[int] = set()
    turnover = 0.0
    n_reb_used = 0
    for j, i in enumerate(reb):
        end = reb[j + 1] + 1 if j + 1 < len(reb) else T
        per = pd.Timestamp(dates[i]).to_period("M") - 1  # 用**上月末**市值，禁未来函数
        if per not in cap_rows:
            continue
        row = cap_w.iloc[cap_rows[per]]
        okmask = np.array([pd.notna(row.get(s, np.nan)) for s in syms], dtype=bool)
        okmask &= np.isfinite(R[i])
        cand = np.where(okmask)[0]
        vals = np.array([float(row.get(s, np.nan)) for s in syms], dtype=float)
        if len(cand) < 20:
            continue
        k = max(1, int(round(len(cand) * quantile)))
        sel_idx = cand[np.argsort(vals[cand])[:k]]  # 最小市值
        sel = set(int(c) for c in sel_idx)
        seg = R[i + 1 : end]
        if seg.shape[0] == 0:
            prev = sel
            continue
        cols = sorted(sel)
        sub = seg[:, cols]
        m = np.isfinite(sub)
        rows = np.where(m.any(axis=1))[0]
        if rows.size == 0:
            prev = sel
            continue
        mm = m[rows]
        daily = np.where(mm, sub[rows], 0.0).sum(axis=1) / np.maximum(mm.sum(axis=1), 1)
        port[i + 1 + rows] += daily
        turnover += len(sel - prev) / max(len(sel), 1)
        n_reb_used += 1
        prev = sel
    net = port.copy()
    for i in reb:
        net[min(i + 1, T - 1)] -= 2 * rc.COST_ONEWAY_BP * 1e-4
    sd = float(net.std(ddof=1))
    diag = {
        "rebalances_used": n_reb_used,
        "mean_turnover": round(turnover / max(n_reb_used, 1), 3),
        "ann_return": round(float(net.mean() * rc.PERIODS_PER_YEAR), 4),
        "sharpe_annual": round(float(net.mean() / sd * math.sqrt(rc.PERIODS_PER_YEAR)), 4) if sd > 0 else None,
        "skew": round(float(pd.Series(net).skew()), 4),
        "excess_kurt": round(float(pd.Series(net).kurt()), 4),
        "T": int((net != 0).sum()),
        "max_dd": round(
            float(
                (
                    np.exp(np.cumsum(np.log1p(np.clip(net, -0.9, None))))
                    / np.maximum.accumulate(np.exp(np.cumsum(np.log1p(np.clip(net, -0.9, None)))) + 1e-12)
                    - 1
                ).min()
            ),
            4,
        ),
    }
    return net, diag


def main() -> int:
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    reg = REPO / "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
    book = TrialLedger(registry_path=reg).cumulative_trials()
    import json

    y = yaml.safe_load(reg.read_text(encoding="utf-8"))
    recs = {str(r.get("batch_id")) for r in (y.get("batch_records") or [])}
    disk_missing = 0
    for s in sorted((REPO / "data/strategy_intake").glob("grid_*/summary.json")):
        if f"grid_{s.parent.name[5:]}" in recs:
            continue
        summ = json.loads(s.read_text(encoding="utf-8"))
        n = summ.get("evaluated") or summ.get("n_sampled") or 0
        disk_missing += int(n)
    N_gov = book + disk_missing

    price, meta_p = rc.load_daily_returns(REPO, S_START, S_END)
    caps = month_end_caps(S_START, S_END)
    mkt = np.nanmean(price.to_numpy(dtype=np.float64), axis=1)

    series: dict[str, np.ndarray] = {}
    metas: dict[str, dict] = {}
    for basis in BASES:
        for q in QUANTS:
            for hold in HOLDS:
                name = f"SIZE_{basis}_q{int(q*100)}_{hold}"
                net, diag = size_portfolio(price, caps, basis, q, hold)
                series[name], metas[name] = net, diag

    n_own = len(series)
    pos = rc.judge(series, N_gov, metas)
    own = rc.judge(series, n_own, metas)
    best = pos["selected_best"]["config"]
    exc = series[best] - mkt

    acct = TrialLedger(registry_path=reg).record_run(
        "calibration_ruler_exam",
        "ruler-calib-20261012-size",
        n_own,
        note=(
            "令⑥ 阳性对照第二件=小市值（窗口受 stock_daily_basic 起点限制 2021-01..2023-12）；"
            "真源=docs/_working/statsgov_campaign/13_ruler_calibration_size_control_v1.yaml"
        ),
        recorded_by="st-statsgov-20261012",
    )

    out = {
        "ttl": "task_bound",
        "title": "尺子校准·阳性对照第二件（小市值）v1",
        "window": [S_START, S_END],
        "window_reason": "市值表 c1_market.stock_daily_basic 实测自 2021-01-04 起（2020 全年无市值数据），故本件窗口缩短",
        "panel_price": meta_p,
        "cap_month_ends": int(len(caps)),
        "configs": {k: {kk: v.get(kk) for kk in ("sharpe_annual", "ann_return", "skew", "excess_kurt", "T", "rebalances_used", "mean_turnover")} for k, v in metas.items()},
        "best_config": best,
        "dsr_governance_N": {"N": N_gov, **{k: pos["configs"][best][k] for k in ("sharpe_annual", "dsr", "passes_dsr", "degenerate")}},
        "dsr_validity_own_N": {"N": n_own, **{k: own["configs"][best][k] for k in ("sharpe_annual", "dsr", "passes_dsr", "degenerate")}},
        "n_pass_own_N": sum(1 for v in own["configs"].values() if isinstance(v, dict) and v.get("passes_dsr")),
        "n_pass_governance_N": sum(1 for v in pos["configs"].values() if isinstance(v, dict) and v.get("passes_dsr")),
        "pbo_own_pool": own.get("pbo"),
        "ew_market_benchmark": {"sharpe_annual": round(float(mkt.mean() / mkt.std(ddof=1) * math.sqrt(rc.PERIODS_PER_YEAR)), 4), "ann_return": round(float(mkt.mean() * rc.PERIODS_PER_YEAR), 4)},
        "best_excess_over_ew_market": {
            "sharpe_annual": round(float(exc.mean() / exc.std(ddof=1) * math.sqrt(rc.PERIODS_PER_YEAR)), 4),
            "ann_return": round(float(exc.mean() * rc.PERIODS_PER_YEAR), 4),
        },
        "trial_accounting": {"n_trials": n_own, "ledger_write": {k: str(v)[:70] for k, v in acct.items()}},
        "denominator": {"book_cumulative": book, "disk_unrecorded": disk_missing, "primary_denominator_N": N_gov},
    }
    p = LANE / "docs/_working/statsgov_campaign/13_ruler_calibration_size_control_v1.yaml"
    p.write_text(yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8", newline="\n")
    print("[size] best=", best, out["dsr_validity_own_N"], out["best_excess_over_ew_market"])
    print("[size] n_pass own=", out["n_pass_own_N"], "/", n_own, " gov=", out["n_pass_governance_N"])
    print("[size] pbo=", str(out["pbo_own_pool"].get("pbo")) if out.get("pbo_own_pool") else None)
    print("[size] 记账=", out["trial_accounting"])
    print("[size] 各配置 SR=", {k: v["sharpe_annual"] for k, v in out["configs"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
