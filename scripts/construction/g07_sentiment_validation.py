# [BLUEPRINT] MOD-INF-005 | scripts/construction/g07_sentiment_validation.py | §
# [MODULE] scripts.construction.g07_sentiment_validation
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.data.ch_config; zephyr.signal_ashare.sentiment.sentiment_cycle（只读消费，禁改本体）
# [CONSUMERS] docs/_working/2026-09-11-g07-sentiment-validation.md（G07 报告）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读验证脚本（A 类一次性，零实盘副作用）；复用 sentiment_cycle production 函数不重复实现；禁碰 trading_decision_map.yaml
# [MODIFY-GUARD] G07 情绪验证批（st-g07-crypto-20260912）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据不足/连通失败时抛异常非零退出，不静默出结论
# [TESTS] 无（一次性施工验证脚本，结论以报告为准）
# [TTL] task_bound
"""g07_sentiment_validation.py — G07 情绪分层相关性验证（28 号 §3.7.2/§3.7.4，30 号 §6.2 施工前必做）。

问题：情绪周期是否为三策略（打板/多因子/事件驱动）的隐形驱动？
方法：①kline_daily 全市场日线聚合市场级情绪指标 → ②production 定位器逐日打五阶段标签 →
      ③三 sleeve 代理收益（次日收益口径）→ ④分层 vs 全样本相关矩阵 → 三态裁定。
判据（28 号 §3.7.3）：分层后 ρ_max <0.3 假设成立 / 0.3-0.6 部分成立（G13 加硬上限）/ >0.6 组合失效。

口径披露（报告必引）：
- 代理收益：非真实回测 PnL——各 sleeve 信号集合在 T+1 交易日的复权收益均值（backtest-based，待实盘复核）。
- 涨停判定近似：pct_change ≥ 9.8%（主板）/ ≥19.8%（创业科创 30/68 前缀）且收盘封住；ST 5% 档不可识别（漏判）。
- 定位器输入 dragon_tiger/northbound 历史缺失——两指标不参与 _score_phase 评分（权重 0），无影响。

用法：
  python scripts/construction/g07_sentiment_validation.py [--start 2022-09-01] [--end 2026-09-11]
  [--no-bootstrap]   # 跳过增补项（block-bootstrap 2000 次 + Hawkes 简化 MLE）
输出：tmp/g07_results.json + 控制台三态裁定摘要。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import numpy as np
import pandas as pd

from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
from zephyr.signal_ashare.sentiment.sentiment_cycle import (
    SentimentLocatorInput,
    SentimentPhase,
    _compute_corr_matrix,
    analyze_sentiment_driven_correlation,
    compute_sentiment_temperature,
    locate_sentiment_phase,
    validate_sentiment_hidden_driver,
)

PREHEAT_DAYS = 21  # 动量 20 日/成交额 MA20 预热期，窗口头部不产信号


def fetch_daily(start: str, end: str) -> pd.DataFrame:
    """全市场 A 股日线（复权因子 coalesce=1，Decimal cast Float64 降传输开销）。"""
    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    from clickhouse_driver import Client

    c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)), user=cfg.get("user", "default"),
               password=cfg.get("password", ""), connect_timeout=5)
    rows = c.execute(
        f"""
        SELECT trade_date, symbol,
               toFloat64(open)  AS o,
               toFloat64(high)  AS h,
               toFloat64(close) AS cl,
               toFloat64(pct_change) AS pc,
               coalesce(toFloat64(adj_factor), 1.0) AS af,
               toFloat64(amount) AS amt
        FROM c1_market.kline_daily
        WHERE trade_date >= '{start}' AND trade_date <= '{end}'
          AND market_type = 'A_share'
        ORDER BY trade_date, symbol
        """
    )
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "open", "high", "close", "pct_change", "adj_factor", "amount"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    if df.empty:
        raise RuntimeError("kline_daily 返回空数据集——检查窗口/表可用性")
    return df


def build_signals(df: pd.DataFrame) -> pd.DataFrame:
    """逐股构造：涨停判定/连板链/复权收益/动量/放量跳空信号位（长表，逐日逐股）。"""
    df = df.sort_values(["symbol", "trade_date"]).reset_index(drop=True)
    g = df.groupby("symbol", sort=False)
    df["prev_close"] = df["close"] / (1.0 + df["pct_change"] / 100.0)  # 未复权昨收反推
    df["limit_ratio"] = np.where(df["symbol"].str.startswith(("30", "68")), 0.20, 0.10)
    df["ret_fwd"] = g["close"].transform(lambda s: s.shift(-1) / s - 1.0)  # 未复权次日收益（占位）
    df["close_adj"] = df["close"] * df["adj_factor"]
    df["ret_fwd_adj"] = df.groupby("symbol", sort=False)["close_adj"].transform(lambda s: s.shift(-1) / s - 1.0)
    df["sealed"] = (df["pct_change"] >= (df["limit_ratio"] * 100 - 0.2)) & (
        (df["close"] / df["prev_close"] - 1.0) >= df["limit_ratio"] - 0.002
    )
    df["touched"] = (df["high"] / df["prev_close"] - 1.0) >= df["limit_ratio"] - 0.002  # 触及涨停
    df["sealed_prev"] = df.groupby("symbol", sort=False)["sealed"].transform(lambda s: s.shift(1).fillna(False))
    # 连板链：昨日封板则 +1，否则重置
    def _streak(s: pd.Series) -> pd.Series:
        out, cur = np.zeros(len(s), dtype=int), 0
        for i, v in enumerate(s.to_numpy()):
            cur = cur + 1 if v else 0
            out[i] = cur
        return pd.Series(out, index=s.index)

    df["consec"] = df.groupby("symbol", sort=False)["sealed"].transform(_streak)
    df["mom20"] = df.groupby("symbol", sort=False)["close_adj"].transform(lambda s: s / s.shift(20) - 1.0)
    df["gap_up"] = (df["open"] / df["prev_close"] - 1.0) >= 0.03
    df["amt_ma5"] = df.groupby("symbol", sort=False)["amount"].transform(lambda s: s.rolling(5).mean())
    df["amt_spike"] = df["amount"] >= df["amt_ma5"] * 2.5
    df["listed_days"] = df.groupby("symbol", sort=False).cumcount() + 1
    return df


def daily_market_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """逐日市场级情绪指标（定位器 6 评分输入 + 温度计 7 维输入）。"""
    day = df.groupby("trade_date")
    m = pd.DataFrame(index=day.size().index)
    m["sealed"] = day["sealed"].sum()
    m["touched"] = day["touched"].sum()
    m["explosion"] = m["touched"] - m["sealed"]
    m["limit_up"] = m["sealed"]  # 近似：封板数≈涨停家数（ST 5% 档漏判，报告披露）
    m["limit_down"] = day.apply(lambda x: (x["pct_change"] <= -(x["limit_ratio"] * 100 - 0.2)).sum(), include_groups=False)
    m["advancing"] = day.apply(lambda x: (x["pct_change"] > 0).sum(), include_groups=False)
    m["declining"] = day.apply(lambda x: (x["pct_change"] < 0).sum(), include_groups=False)
    m["amount_total"] = day["amount"].sum()
    m["amount_ma20"] = m["amount_total"].rolling(20).mean()
    m["amount_ratio"] = m["amount_total"] / m["amount_ma20"]
    m["avg_turnover_proxy"] = m["advancing"] / (m["advancing"] + m["declining"])  # 占位（不参与评分）
    # 打板次日溢价：前日封板股今日收益均值
    sealed_ret = df.loc[df["sealed_prev"], ["trade_date", "ret_fwd_adj"]].groupby("trade_date")["ret_fwd_adj"].mean()
    m["daban_premium"] = sealed_ret
    # 连板梯队
    sealed_df = df.loc[df["sealed"], ["trade_date", "symbol", "consec"]]
    m["highest_consec"] = sealed_df.groupby("trade_date")["consec"].max()
    ladder = sealed_df.groupby(["trade_date", "consec"]).size().unstack(fill_value=0)
    return m, ladder


def run_locator(m: pd.DataFrame, ladder: pd.DataFrame) -> pd.Series:
    """production 定位器逐日打标（先验链式传递）。返回 dominant_phase 序列。

    回放适配（不改本体）：兜底触发后 phase_prob 为 one-hot，PHASE_ORDER 首尾阶段
    （FREEZING/EBING）邻接单向 → 长序列回放先验锁死（首日触发兜底后全程锁死，
    实测 2022-10 起 4 年仅 EBING/FREEZING 两态）。先验做 50% 均匀混合稀释，
    保留惯性的同时允许 evidence 翻转；实盘语义影响=惯性减半，报告披露。
    """
    phases, prior = {}, None
    uniform = {p: 0.2 for p in SentimentPhase}
    for d in m.index:
        cons_today = {int(k): int(v) for k, v in (ladder.loc[d].items() if d in ladder.index else []) if v > 0 and k >= 1}
        cons_prev = {}
        loc = m.index.get_loc(d)
        if loc > 0:
            dp = m.index[loc - 1]
            if dp in ladder.index:
                cons_prev = {int(k): int(v) for k, v in ladder.loc[dp].items() if v > 0 and k >= 1}
        premium = float(m.at[d, "daban_premium"]) if not math.isnan(m.at[d, "daban_premium"]) else 0.0
        out = locate_sentiment_phase(
            SentimentLocatorInput(
                limit_up_count=int(m.at[d, "limit_up"]),
                limit_down_count=int(m.at[d, "limit_down"]),
                explosion_count=int(m.at[d, "explosion"]),
                consecutive_ladder=cons_today,
                yesterday_consecutive=cons_prev,
                daban_next_day_premium=premium,
                avg_turnover_rate=1.0,
                market_amount_ratio_vs_ma20=float(m.at[d, "amount_ratio"]) if not math.isnan(m.at[d, "amount_ratio"]) else 1.0,
                dragon_tiger_net_buy_ratio=0.0,  # 历史缺失；不参与 _score_phase 评分（权重 0）
                northbound_net_inflow=0.0,  # 2024-05 起停发；不参与评分
                yesterday_phase_prob=prior,
            )
        )
        phases[d] = out.dominant_phase
        # 兜底日标签改用 evidence argmax：dominant 被强制收缩态是实盘仓位保守设计，
        # 回放打标语义应为证据判定（evidence argmax）——2024-09-30 牛市引爆日实证：
        # evidence CONSENSUS 0.644 最高却被兜底成 FREEZING，导致长序列阶段分布病态。
        if out.fallback_triggered:
            phases[d] = SentimentPhase[max(out.evidence_scores, key=out.evidence_scores.get)]
        prior = {p: 0.5 * out.phase_prob[p] + 0.5 * uniform[p] for p in uniform}
    return pd.Series(phases)


def sleeve_returns(df: pd.DataFrame) -> pd.DataFrame:
    """三 sleeve 代理次日收益（T 日信号 → T+1 复权收益均值）。"""
    sig = df[df["listed_days"] > PREHEAT_DAYS]
    daban = sig.loc[sig["sealed"]].groupby("trade_date")["ret_fwd_adj"].mean()
    mom_ok = sig.loc[sig["mom20"].notna()].copy()
    top50 = mom_ok.groupby("trade_date", group_keys=False).apply(
        lambda x: x.nlargest(50, "mom20")[["ret_fwd_adj"]].mean(), include_groups=True
    )
    multi = top50["ret_fwd_adj"]
    event = sig.loc[sig["gap_up"] & sig["amt_spike"]].groupby("trade_date")["ret_fwd_adj"].mean()
    out = pd.DataFrame({"daban": daban, "multifactor": multi, "event": event})
    return out.dropna()


def hawkes_mle(event_days: np.ndarray) -> dict:
    """一维 Hawkes 简化 MLE（网格搜索；事件单位=交易日索引）。增补项，供参考。"""
    t = np.asarray(event_days, dtype=float)
    n, T = len(t), t[-1] - t[0] + 1.0
    best = None
    for beta in np.geomspace(0.1, 5.0, 30):
        diff = t[None, :] - t[:, None]
        e = np.triu(np.exp(-beta * diff), k=1).sum(axis=1)  # e_i = Σ_{j<i} exp(-β(t_i-t_j))
        integ_tail = (1.0 - np.exp(-beta * (T - (t - t[0])))).sum()
        for lam0 in np.geomspace(0.005, 0.5, 20):
            for alpha in np.geomspace(0.005, 1.2, 40):
                lam = lam0 + alpha * e
                ll = np.log(lam).sum() - lam0 * T - (alpha / beta) * integ_tail
                if best is None or ll > best["log_lik"]:
                    best = {"log_lik": float(ll), "lambda_0": float(lam0), "alpha": float(alpha),
                            "beta": float(beta), "eta": float(alpha / beta)}
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2022-09-01")
    ap.add_argument("--end", default="2026-09-11")
    ap.add_argument("--no-bootstrap", action="store_true", help="跳过增补项（bootstrap+Hawkes）")
    args = ap.parse_args()

    print(f"[1/6] 拉取日线 {args.start} ~ {args.end} ...")
    raw = fetch_daily(args.start, args.end)
    print(f"      rows={len(raw)} symbols={raw['symbol'].nunique()} days={raw['trade_date'].nunique()}")

    print("[2/6] 构造信号长表（涨停/连板/复权收益/动量/跳空）...")
    df = build_signals(raw)

    print("[3/6] 聚合日度市场指标 + production 定位器逐日打标 ...")
    m, ladder = daily_market_metrics(df)
    phase_by_day = run_locator(m, ladder)

    print("[4/6] 三 sleeve 代理次日收益 ...")
    sr = sleeve_returns(df)
    axis = sr.index[sr.index.isin(phase_by_day.index)]
    phases_axis = phase_by_day.loc[axis]
    returns = {k: sr.loc[axis, k].tolist() for k in sr.columns}
    phase_seq = [phases_axis.loc[d] for d in axis]
    print(f"      有效样本日={len(axis)}  阶段分布={pd.Series(phase_seq).value_counts().to_dict()}")

    print("[5/6] 全样本矩阵 + 分层隐驱动验证（28 号 §3.7.2）...")
    full_matrix = _compute_corr_matrix(returns, list(range(len(axis))))
    strat = validate_sentiment_hidden_driver(returns, phase_seq, correlation_threshold=0.6)

    result: dict = {
        "window": [args.start, args.end],
        "n_days": int(len(axis)),
        "n_symbols": int(raw["symbol"].nunique()),
        "phase_distribution": {k.name: int(v) for k, v in pd.Series(phase_seq).value_counts().items()},
        "full_matrix": full_matrix,
        "full_max_rho": max(abs(full_matrix[a][b]) for i, a in enumerate(returns) for j, b in enumerate(returns) if i < j),
        "stratified": {
            p.name: {
                "n_days": t.n_days,
                "matrix": t.correlation_matrix,
                "max_rho": (max((abs(t.correlation_matrix[a][b]) for i, a in enumerate(returns) for j, b in enumerate(returns) if i < j), default=None)
                            if t.correlation_matrix else None),
                "is_pass": t.is_pass,
            }
            for p, t in strat.items()
        },
    }

    # 三态裁定（28 号 §3.7.3）：取通过样本门槛（≥30 天）阶段的 ρ_max 最大值
    qualified = [v for v in result["stratified"].values() if v["n_days"] >= 30 and v["max_rho"] is not None]
    if not qualified:
        verdict = "INCONCLUSIVE"
        rho_overall = None
    else:
        rho_overall = max(v["max_rho"] for v in qualified)
        verdict = "HYPOTHESIS_HOLD" if rho_overall < 0.3 else ("PARTIAL" if rho_overall < 0.6 else "COMBINATION_INVALID")
    result["verdict"] = verdict
    result["rho_overall"] = rho_overall

    if not args.no_bootstrap:
        print("[6/6] 增补：block-bootstrap 2000 次 + Hawkes 简化 MLE ...")
        temp_by_day = {}
        for d in axis:
            row_ladder = {int(k): int(v) for k, v in (ladder.loc[d].items() if d in ladder.index else []) if v > 0 and k >= 2}
            temp_by_day[d] = compute_sentiment_temperature(
                int(m.at[d, "limit_up"]), int(m.at[d, "limit_down"]), int(m.at[d, "explosion"]),
                int(m.at[d, "sealed"]), row_ladder, int(m.at[d, "advancing"]), int(m.at[d, "declining"]),
            ).score
        intensity = [temp_by_day[d] / 100.0 for d in axis]
        result["bootstrap"] = analyze_sentiment_driven_correlation(returns, intensity, n_bootstrap=2000, block_size=5)
        thr = np.quantile(m.loc[axis, "sealed"].to_numpy(dtype=float), 0.90)
        burst = np.where((m.loc[axis, "sealed"].to_numpy(dtype=float) > max(thr, 20)))[0]
        if len(burst) >= 20:
            result["hawkes"] = hawkes_mle(burst.astype(float))
        else:
            result["hawkes"] = {"skipped": f"burst days={len(burst)} < 20"}
        print(f"      burst_days={len(burst)}  hawkes={result['hawkes']}")

    out_path = REPO / "tmp" / "g07_results.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print("\n===== G07 三态裁定 =====")
    print(f"窗口: {args.start}~{args.end}  样本日={len(axis)}")
    print(f"全样本 ρ_max = {result['full_max_rho']:.4f}")
    print(f"分层后 ρ_max（≥30 天阶段）= {rho_overall if rho_overall is not None else 'N/A'}")
    for p, v in result["stratified"].items():
        mr = f"{v['max_rho']:.4f}" if v["max_rho"] is not None else "-"
        print(f"  {p:<11} n={v['n_days']:>4}  ρ_max={mr:>8}  pass={v['is_pass']}")
    print(f"裁定: {verdict}  (HYPOTHESIS_HOLD<0.3 / PARTIAL 0.3-0.6 / COMBINATION_INVALID>0.6)")
    print(f"结果 JSON: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
