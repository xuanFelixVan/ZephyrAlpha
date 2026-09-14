#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.eval_exp_expectations
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.factor.expectations; zephyr.backtest.core.matching_logic; scipy
# [CONSUMERS] factor_registry FCT-EXP 族晋级证据（SOP-B ④⑤⑥ 单脚本链）；experiment_registry EXP-FACTOR-EVAL-*；CLI 输出 JSON
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] PIT as-of：因子输入=consensus_daily（publish_date<=trade_date 结构性保证，DS-229）；
#              前向收益=close t→t+20 交易日（标签，检验允许）；IC=月末截面 Spearman；
#              晋级门槛（预注册禁挪，registry 头 2026-09-12 成文）：IS 2019-2023 |IC|>=0.02 且 t p<0.05 且覆盖>=60%；
#              ⑥ 准入线=IS 超额 Sharpe>=0.5 且 OOS/IS>=0.7（FQ 同款）；滑点压力=cfg+{20,40,80}bp（§8.1 协议，
#              仅 cfg 档达标→cost-fragile 降级）；can_deploy 与 P0-003 解耦（裁定 2026-09-14）；
#              参数网格预注册（§8.2：k_td∈{20,60}×fy1）禁越界；动量相关性对照>=0.85 → variant_of/否决；
#              稠密日历重索引后逐标的调用 expectations 函数（k 期=交易日语义，非观测行数）；
#              SQL 集中化=模块级常量区（NO-BARE-SQL），查询语义与预注册判据一并固化
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] consensus_daily/kline 缺失->RuntimeError
# [TESTS] 纯统计流程（EXP 函数语义由 tests/factor/test_expectations.py 覆盖）；本脚本 --help 即用
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 因子晋级评估 CLI（A 类一次性运维，随晋级批次按需手动执行）
"""eval_exp_expectations.py — EXP 一致预期族 IC 出证（SOP-B ④⑤⑥，首跑 EXP-02）。

月度再平衡截面评估：月末交易日，取 consensus_daily fy1（>=当年最小预测年）快照，
逐标的稠密日历序列调用 expectations.exp02_revision_momentum（k 期=交易日），
与后 20 交易日收益做截面 Spearman；IS（2019-2023 晋级窗）/OOS（2024+ 复核）分段；
⑤ 五分位单调+分状态条件 IC（regime_state_anchored，上游 valid）+动量相关性对照；
⑥ Top50 等权月频多头（成本五项读 MatchingConfig #233 零硬编码，超额对 000300）
+滑点压力四档（cfg/20/40/80bp）。
预注册真源=docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md
（§8 预注册/§9 数据缺口档案，跑前冻结禁挪）。

用法::

    python scripts/backtest/eval_exp_expectations.py --factor exp02 --out out.json
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

_IS = ("2019-01-01", "2023-12-31")
_OOS = ("2024-01-01", "2026-09-11")
_FWD = 20
_K_GRID = (20, 60)              # §8.2 预注册（主档 20=1m，复核档 60=3m）
_TOP_N = 50
_SLIP_STRESS = (None, 20.0, 40.0, 80.0)   # None=MatchingConfig 原值 1bp（#233 真源）
_MIN_NAMES = 100
_PANEL_START = "2018-06-01"     # k=60 回看缓冲
_AUM = 1_000_000.0              # 组合名义额（最小佣金分摊基数；FQ 同款量级）

# —— SQL 常量区（NO-BARE-SQL 集中化；查询口径与 §8 预注册判据一并固化）——
_SQL_CONSENSUS_MONTH = (
    "SELECT symbol, trade_date, forecast_year, eps_consensus, eps_std "
    "FROM c3_fundamental.consensus_daily FINAL "
    "WHERE trade_date >= toDate('{y}-{m:02d}-01') "
    "AND trade_date <= toDate('{y}-{m:02d}-{last_day:02d}') FORMAT TSV")
_SQL_CALENDAR = (
    "SELECT DISTINCT cal_date FROM c1_market.trade_calendar FINAL "
    "WHERE exchange='SSE' AND is_open=1 AND cal_date >= toDate('2018-06-01') "
    "ORDER BY cal_date FORMAT TSV")
_SQL_PRICES_DATES = (
    "SELECT trade_date, symbol, toFloat64(close) AS close FROM c1_market.kline_daily "
    "WHERE trade_date IN ({quoted}) FORMAT TSV")
_SQL_BENCH = (
    "SELECT trade_date, toFloat64(close) AS close FROM c1_market.kline_index "
    "WHERE symbol='000300' AND trade_date >= toDate('" + _PANEL_START + "') "
    "ORDER BY trade_date FORMAT TSV")
_SQL_REGIME = (
    "SELECT trade_date, dominant FROM c1_backtest.regime_state_anchored FINAL FORMAT TSV")


def load_consensus_fy1() -> pd.DataFrame:
    """consensus_daily → fy1 快照长表（每股每日一行：>=当年最小预测年）。

    按月分块拉取（防御性；坏列名会被 TCP/HTTP 双通道报错掩盖成空串，逐块易定位），
    fy1 选择在客户端完成（forecast_year 升序取首行）。
    表无 eps_mean 列——窗口均值即 eps_consensus（DS-229 口径），客户端同名派生。
    """
    from zephyr.data import ch_reader

    frames = []
    ym = (2018, 6)
    while (ym[0], ym[1]) <= (2026, 9):
        y, m = ym
        last_day = [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
                    31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
        q = _SQL_CONSENSUS_MONTH.format(y=y, m=m, last_day=last_day)
        tsv = ch_reader.query(q, timeout=300)
        if tsv and tsv.strip():
            rows = [ln.split("\t") for ln in tsv.strip().split("\n")]
            frames.append(pd.DataFrame(rows, columns=["symbol", "td", "fy", "eps_consensus", "eps_std"]))
        ym = (y + 1, 1) if m == 12 else (y, m + 1)
    if not frames:
        raise RuntimeError("consensus_daily fy1 快照为空")
    df = pd.concat(frames, ignore_index=True)
    df["td"] = pd.to_datetime(df["td"])
    df["fy"] = pd.to_numeric(df["fy"], errors="coerce")
    for c in ("eps_consensus", "eps_std"):
        df[c] = pd.to_numeric(df[c].replace("\\N", np.nan), errors="coerce")
    df["eps_mean"] = df["eps_consensus"]  # 表内均值列=eps_consensus（exp02 分歧度分母）
    df = df[df["fy"] >= df["td"].dt.year].dropna(subset=["eps_consensus"])
    df = df.sort_values(["symbol", "td", "fy"]).drop_duplicates(["symbol", "td"], keep="first")
    return df.drop(columns=["fy"])


def load_calendar() -> list[str]:
    """交易日历（SSE，>=2018-06-01）。"""
    from zephyr.data import ch_reader

    return [ln.strip()[:10] for ln in ch_reader.query(_SQL_CALENDAR).strip().split("\n")]


def load_prices(needed_dates: list[str]) -> pd.DataFrame:
    """需要日期的全A收盘（FQ 同款日期白名单配方，避开结果集限额；日期分块防 URL 超长）。"""
    from zephyr.data import ch_reader

    frames = []
    for i in range(0, len(needed_dates), 50):
        chunk = needed_dates[i:i + 50]
        quoted = ",".join(f"'{d}'" for d in chunk)
        tsv = ch_reader.query(_SQL_PRICES_DATES.format(quoted=quoted), timeout=300)
        if tsv and tsv.strip():
            rows = [ln.split("\t") for ln in tsv.strip().split("\n")]
            frames.append(pd.DataFrame(rows, columns=["td", "symbol", "close"]))
    if not frames:
        raise RuntimeError("kline_daily 价格为空")
    px = pd.concat(frames, ignore_index=True)
    px["td"] = pd.to_datetime(px["td"])
    px["close"] = pd.to_numeric(px["close"], errors="coerce")
    return px


def load_bench() -> pd.Series:
    """000300 收盘（超额基准）。"""
    from zephyr.data import ch_reader

    bench_tsv = ch_reader.query(_SQL_BENCH)
    b = [ln.split("\t") for ln in bench_tsv.strip().split("\n")]
    return pd.Series({pd.Timestamp(r[0]): float(r[1]) for r in b}).sort_index()


def month_ends(cal: list[str], lo: str, hi: str) -> list[str]:
    """每月最后一个交易日（iso str）。"""
    last: dict[str, str] = {}
    for d in cal:
        if lo <= d <= hi:
            last[d[:7]] = d
    return sorted(last.values())


def compute_factor(df: pd.DataFrame, k: int) -> pd.DataFrame:
    """逐标的稠密日历序列调用 expectations.exp02_revision_momentum（k 期=交易日）。"""
    from zephyr.factor.expectations import exp02_revision_momentum

    cal_idx = sorted(df["td"].unique())
    out = []
    for sym, g in df.groupby("symbol"):
        s = g.set_index("td")[["eps_consensus", "eps_std", "eps_mean"]].reindex(cal_idx)
        f = exp02_revision_momentum(s["eps_consensus"], s["eps_std"], s["eps_mean"], k=k)
        out.append(pd.DataFrame({"td": cal_idx, "symbol": sym, "f": f.values}))
    res = pd.concat(out, ignore_index=True)
    return res.dropna()


def build_ic_table(fac_wide: pd.DataFrame, px_close: pd.DataFrame,
                   mes: list[str], fwd_map: dict, k: int) -> pd.DataFrame:
    """月末截面 IC 表（含动量对照列 mom_ic）。"""
    mom_wide = px_close / px_close.shift(k) - 1.0
    rows = []
    for t in mes:
        ts = pd.Timestamp(t)
        f20 = fwd_map.get(t)
        if f20 is None or ts not in fac_wide.index or ts not in px_close.index:
            continue
        f_t = fac_wide.loc[ts].dropna()
        px_t = px_close.loc[ts]
        px_f = px_close.loc[pd.Timestamp(f20)]
        r = px_f.reindex(px_t.index) / px_t - 1.0
        m_t = mom_wide.loc[ts].reindex(f_t.index) if ts in mom_wide.index else pd.Series(dtype=float)
        merged = pd.concat([f_t.rename("f"), r.rename("r"), m_t.rename("m")], axis=1).dropna(subset=["f", "r"])
        if len(merged) < _MIN_NAMES:
            continue
        rho, _ = stats.spearmanr(merged["f"], merged["r"])
        mom_rho = (stats.spearmanr(merged["f"], merged["m"])[0]
                   if merged["m"].notna().sum() > _MIN_NAMES else np.nan)
        rows.append({"td": t, "n": len(merged), "ic": float(rho), "mom_ic": float(mom_rho)})
    return pd.DataFrame(rows)


def _seg(d: pd.DataFrame) -> dict:
    if len(d) < 12:
        return {"n_months": int(len(d)), "ic_mean": None}
    tp = stats.ttest_1samp(d["ic"], 0.0)
    return {"n_months": int(len(d)), "ic_mean": round(float(d["ic"].mean()), 4),
            "t_p": round(float(tp.pvalue), 5),
            "coverage_mean": round(float(d["n"].mean()), 0),
            "mom_ic_mean": None if d["mom_ic"].isna().all() else round(float(d["mom_ic"].mean()), 4)}


def _prune_material(fac_wide: pd.DataFrame, px_close: pd.DataFrame,
                    mes: list[str], fwd_map: dict) -> dict:
    """⑤ 五分位单调性 + 分状态条件 IC（c1_backtest.regime_state_anchored）。"""
    from zephyr.data import ch_reader

    try:
        reg = ch_reader.query(_SQL_REGIME)
        reg_map = {ln.split("\t")[0][:10]: ln.split("\t")[1]
                   for ln in reg.strip().split("\n") if ln.strip()}
    except Exception:  # noqa: BLE001 — 上游态缺失不阻断主线 IC 出证
        reg_map = {}
    month_qcorr: list[float] = []
    cond: dict[str, list[float]] = {}
    for t in mes:
        ts = pd.Timestamp(t)
        f20 = fwd_map.get(t)
        if f20 is None or ts not in fac_wide.index or ts not in px_close.index:
            continue
        f_t = fac_wide.loc[ts].dropna()
        px_t = px_close.loc[ts]
        px_f = px_close.loc[pd.Timestamp(f20)]
        r = px_f.reindex(px_t.index) / px_t - 1.0
        merged = pd.concat([f_t.rename("f"), r.rename("r")], axis=1).dropna()
        if len(merged) < _MIN_NAMES:
            continue
        q = pd.qcut(merged["f"].rank(method="first"), 5, labels=False)
        q_means = [float(merged["r"][q == qi].mean()) for qi in range(5)]
        month_qcorr.append(float(stats.spearmanr(range(5), q_means)[0]))
        dom = reg_map.get(t)
        if dom:
            cond.setdefault(dom, []).append(float(stats.spearmanr(merged["f"], merged["r"])[0]))
    return {"quintile_monthly_rank_corr_mean": round(float(np.mean(month_qcorr)), 3)
            if month_qcorr else None,
            "regime_cond_ic": {k: round(float(np.mean(v)), 4) for k, v in cond.items()}}


def _narrow(fac_wide: pd.DataFrame, px_close: pd.DataFrame, bench: pd.Series,
            mes: list[str], fwd_map: dict) -> dict:
    """⑥ Top50 等权月频多头（成本五项读 MatchingConfig）+ 滑点四档压力，超额对 000300。"""
    import dataclasses

    from zephyr.backtest.core.matching_logic import MatchingConfig

    out: dict = {}
    valid_mes = [t for t in mes if fwd_map.get(t)]
    bench_ret = {}
    for j in range(len(valid_mes) - 1):
        t, nxt = valid_mes[j], valid_mes[j + 1]
        bt, bn = bench.reindex([pd.Timestamp(t), pd.Timestamp(nxt)])
        if pd.notna(bt) and pd.notna(bn) and bt > 0:
            bench_ret[t] = bn / bt - 1.0

    for slip in _SLIP_STRESS:
        cfg = MatchingConfig() if slip is None else dataclasses.replace(
            MatchingConfig(), slippage_bps=Decimal(str(slip)))
        one_side = float(cfg.commission_rate + cfg.transfer_fee_rate
                         + cfg.slippage_bps / Decimal(10000))
        sell_extra = float(cfg.stamp_tax_rate)
        min_comm = float(cfg.min_commission)
        per_trade = _AUM / _TOP_N
        comm_ratio = max(per_trade * float(cfg.commission_rate), min_comm) / per_trade

        rets: dict[str, float] = {}
        prev: set[str] = set()
        for j in range(len(valid_mes) - 1):
            t, nxt = valid_mes[j], valid_mes[j + 1]
            ts, tn = pd.Timestamp(t), pd.Timestamp(nxt)
            if ts not in fac_wide.index or ts not in px_close.index or tn not in px_close.index:
                continue
            f_t = fac_wide.loc[ts].dropna()
            px_t = px_close.loc[ts]
            px_f = px_close.loc[tn]
            r = px_f.reindex(px_t.index) / px_t - 1.0
            merged = pd.concat([f_t.rename("f"), r.rename("r")], axis=1).dropna()
            if len(merged) < _MIN_NAMES:
                continue
            picks = merged.nlargest(_TOP_N, "f").index
            gross = float(merged.loc[picks, "r"].mean())
            cur = set(picks)
            n_sell, n_buy = len(prev - cur), len(cur - prev)
            turnover = (n_sell + n_buy) / max(len(cur), 1)
            cost = (n_sell / max(len(cur), 1) * (comm_ratio + sell_extra + one_side)
                    + n_buy / max(len(cur), 1) * (comm_ratio + one_side))
            prev = cur
            rets[t] = gross - cost - bench_ret.get(t, 0.0)

        s = pd.Series(rets).sort_index()

        def _sharpe(seg: pd.Series) -> float | None:
            seg = seg.dropna()
            if len(seg) < 6 or seg.std(ddof=1) == 0:
                return None
            return round(float(seg.mean() / seg.std(ddof=1) * np.sqrt(12)), 3)

        isv = _sharpe(s[(s.index >= _IS[0]) & (s.index <= _IS[1])])
        oosv = _sharpe(s[s.index >= _OOS[0]])
        label = "cfg" if slip is None else str(int(slip))
        out[f"slip_{label}bp"] = {
            "excess_sharpe_is": isv, "excess_sharpe_oos": oosv,
            "oos_over_is": None if not isv or oosv is None else round(oosv / isv, 2),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP 族 SOP-B ④⑤⑥ 出证（§8 预注册判据，禁挪）")
    ap.add_argument("--factor", default="exp02", choices=["exp02"], help="评估因子（首跑 EXP-02）")
    ap.add_argument("--out", default=None, help="JSON 输出路径（缺省打印）")
    args = ap.parse_args()

    cons = load_consensus_fy1()
    cal = load_calendar()
    mes = month_ends(cal, _IS[0], _OOS[1])
    cal_pos = {d: i for i, d in enumerate(cal)}
    fwd_map = {d: (cal[cal_pos[d] + _FWD] if cal_pos[d] + _FWD < len(cal) else None)
               for d in mes}
    # 需要日期=月末 ∪ t+20（前向收益）∪ t-k（动量对照，k=各预注册回看窗）
    needed = set(mes) | {fwd_map[t] for t in mes if fwd_map[t]}
    for t in mes:
        for k in _K_GRID:
            j = cal_pos[t] - k
            if j >= 0:
                needed.add(cal[j])
    px = load_prices(sorted(needed))
    bench = load_bench()
    px_close = px.pivot(index="td", columns="symbol", values="close").reindex(
        pd.to_datetime(cal)).sort_index()

    report: dict = {"factor": args.factor, "is_window": list(_IS),
                    "oos_window": list(_OOS), "fwd_td": _FWD}
    trials = 0
    for k in _K_GRID:
        fac = compute_factor(cons, k)
        fac_wide = fac.pivot(index="td", columns="symbol", values="f").sort_index()
        icdf = build_ic_table(fac_wide, px_close, mes, fwd_map, k)
        seg = {"is": _seg(icdf[icdf["td"] <= _IS[1]]),
               "oos": _seg(icdf[icdf["td"] >= _OOS[0]])}
        if k == _K_GRID[0]:
            seg["prune_material"] = _prune_material(fac_wide, px_close, mes, fwd_map)
            seg["narrow_top50"] = _narrow(fac_wide, px_close, bench, mes, fwd_map)
            trials += len(_SLIP_STRESS)
        trials += 1
        report[f"k{k}td"] = seg

    report["n_trials"] = trials
    report["thresholds"] = {
        "ic_gate": "IS |IC|>=0.02 & t_p<0.05 & coverage>=60%（registry 头 2026-09-12 成文）",
        "narrow_gate": "IS 超额 Sharpe>=0.5 & OOS/IS>=0.7（FQ 同款）；can_deploy 与 P0-003 解耦",
    }
    line = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        Path(args.out).write_text(line, encoding="utf-8")
        print(f"WROTE {args.out}")
    else:
        print(line)


if __name__ == "__main__":
    main()
