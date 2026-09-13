#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.eval_f2_fundamental_ic
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.factor.fundamentals; scipy
# [CONSUMERS] factor_registry FCT-FQ/FCT-GR 族晋级证据（SOP-B ④）；CLI 输出 JSON
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] PIT as-of：t 日截面只用 announce_date<=t 的可见最新版本（LIMIT 版本去重）；
#              前向收益=收盘价 t→t+20 交易日（标签，检验允许）；IC=月度截面 Spearman；
#              晋级门槛（预注册禁挪）：IS 2019-2023 |IC|均值>=0.02 且 t p<0.05 且覆盖>=60%；
#              D3 双登记对照=FQ-01 vs FQ-02 池化秩相关>=0.85 挂 variant_of
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据缺失->RuntimeError
# [TESTS] 纯统计流程（面板构造由 tests/factor/test_fundamentals.py 覆盖语义）；本脚本 --help 即用
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 因子晋级评估 CLI（A 类一次性运维，随晋级批次按需手动执行）
"""eval_f2_fundamental_ic.py — F2 财报八因子 IC 出证（SOP-B ④，晋级门槛评估）。

月度再平衡截面评估：每月末交易日，取每标的 announce_date<=t 的可见最新派生行算因子，
与后 20 交易日收益做截面 Spearman；输出 IC 序列均值/t 值/覆盖率，按 IS（2019-2023 晋级
窗口）与 OOS（2024+ 稳定性复核）分段——门槛=registry 头（2026-09-12 成文，禁挪）。

用法::

    python scripts/backtest/eval_f2_fundamental_ic.py            # 全评估，JSON 打印
    python scripts/backtest/eval_f2_fundamental_ic.py --out out.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

_IS = ("2019-01-01", "2023-12-31")
_OOS = ("2024-01-01", "2026-09-11")
_FWD = 20
_FACTOR_COLS = [
    "fq01_accrual", "fq02_cash_conversion", "fq03_gpoa", "fq04_delta_roe_q",
    "gr01_rev_q_yoy", "gr02_np_q_qoq", "fq05_info_quality", "fq06_fscore",
]


def load_factor_panel() -> pd.DataFrame:
    """派生面板 → 因子面板（每 (symbol, report_period) 一行=最新公告版本）。"""
    from zephyr.data import ch_reader
    from zephyr.factor import fundamentals as F  # ORPHAN-CONSUMER: 直连消费者（另见 tests/factor/test_fundamentals.py）
    from zephyr.factor.fundamentals import (  # noqa: F401 — ORPHAN-MODULE 直连导入锚点
        fq01_accrual, fq02_cash_conversion, fq03_gpoa, fq04_delta_roe_q,
        gr01_rev_q_yoy, gr02_np_q_qoq, fq05_info_quality, fq06_fscore)

    cols = ("symbol, report_period, announce_date, accrual_ttm, np_ttm, ocf_ttm, total_assets, "
            "gpoa_ttm, np_q, equity_incl_minority, rev_q_yoy, np_q_qoq, accounts_receivable, "
            "rev_ttm, eff_tax_rate_ttm, total_liabilities, total_current_assets, "
            "total_current_liabilities, total_shares, gross_margin_q")
    tsv = ch_reader.query(
        f"SELECT {cols} FROM c3_fundamental.financial_derived FINAL "
        "WHERE announce_date > toDate('1970-01-02') ORDER BY symbol, report_period, announce_date"
    )
    if not tsv or not tsv.strip():
        raise RuntimeError("financial_derived 无数据")
    rows = [line.split("\t") for line in tsv.strip().split("\n")]
    names = [c.split(" AS ")[0].strip() for c in cols.split(", ")]
    df = pd.DataFrame(rows, columns=names)
    for c in df.columns:
        if c not in ("symbol", "report_period", "announce_date"):
            df[c] = pd.to_numeric(df[c].replace("\\N", np.nan), errors="coerce")
    # 同报告期多公告版本 → 取最新公告版本（FINAL 后仍可能多版本行）
    df = df.sort_values(["symbol", "report_period", "announce_date"]).drop_duplicates(
        subset=["symbol", "report_period"], keep="last")
    panel = df.set_index(["symbol", "report_period"]).sort_index()
    panel["fq01_accrual"] = F.fq01_accrual(panel["accrual_ttm"])
    panel["fq02_cash_conversion"] = F.fq02_cash_conversion(
        panel["np_ttm"], panel["ocf_ttm"], panel["total_assets"])
    panel["fq03_gpoa"] = F.fq03_gpoa(panel["gpoa_ttm"])
    panel["fq04_delta_roe_q"] = F.fq04_delta_roe_q(panel["np_q"], panel["equity_incl_minority"])
    panel["gr01_rev_q_yoy"] = F.gr01_rev_q_yoy(panel["rev_q_yoy"])
    panel["gr02_np_q_qoq"] = F.gr02_np_q_qoq(panel["np_q_qoq"])
    panel["fq05_info_quality"] = F.fq05_info_quality(
        panel["accounts_receivable"], panel["rev_ttm"], panel["eff_tax_rate_ttm"])
    panel["fq06_fscore"] = F.fq06_fscore(
        panel["np_ttm"], panel["ocf_ttm"], panel["total_assets"], panel["total_liabilities"],
        panel["total_current_assets"], panel["total_current_liabilities"], panel["total_shares"],
        panel["rev_ttm"], panel["gross_margin_q"])
    panel["announce_date"] = pd.to_datetime(panel["announce_date"])
    return panel[["announce_date", "total_shares"] + _FACTOR_COLS]


def load_rebalance_prices(dates: list[str]) -> pd.DataFrame:
    """再平衡日与其后第 20 交易日的全市场收盘价。"""
    from zephyr.data import ch_reader

    quoted = ",".join(f"'{d}'" for d in dates)
    tsv = ch_reader.query(
        f"SELECT trade_date, symbol, toFloat64(close) AS close FROM c1_market.kline_daily "
        f"WHERE trade_date IN ({quoted})"
    )
    rows = [line.split("\t") for line in (tsv or "").strip().split("\n") if line]
    return pd.DataFrame(rows, columns=["td", "symbol", "close"]).assign(
        close=lambda d: pd.to_numeric(d["close"], errors="coerce"))


def main() -> int:
    parser = argparse.ArgumentParser(description="F2 财报八因子 IC 出证（SOP-B ④）")
    parser.add_argument("--out", default=None, help="结果 JSON 输出路径")
    args = parser.parse_args()

    from scipy.stats import ttest_1samp, spearmanr

    panel = load_factor_panel()
    print(f"面板：{len(panel)} 行（{panel.index.get_level_values('symbol').nunique()} 标的）", flush=True)

    cal = ch_reader_cal()
    month_ends = [d for d in cal if "2019-01-01" <= d <= "2026-08-31"
                  and _is_month_end(d, cal)]
    fwd_map = {d: cal[(cal.index(d) + _FWD) % len(cal)] if cal.index(d) + _FWD < len(cal) else None
               for d in month_ends}
    need = sorted({d for d in month_ends if fwd_map[d]} | {f for f in fwd_map.values() if f})
    px = load_rebalance_prices(need)
    px_by_date = {k: v.set_index("symbol")["close"] for k, v in px.groupby("td")}

    ann = panel["announce_date"]
    panel_sorted = panel.sort_values("announce_date")

    def cross_section(t: str) -> pd.DataFrame:
        """t 日截面：announce<=t 的每标的最新版本，索引=symbol（供与价格对齐）。"""
        ann_s = panel_sorted["announce_date"]
        vis = panel_sorted[ann_s <= pd.Timestamp(t)].groupby("symbol").tail(1)
        return vis.droplevel("report_period")

    def ic_series(seg: tuple[str, str]) -> dict:
        dates = [d for d in month_ends if seg[0] <= d <= seg[1] and fwd_map.get(d)]
        out = {f: [] for f in _FACTOR_COLS}
        cov = {f: [] for f in _FACTOR_COLS}
        for t in dates:
            f20 = fwd_map[t]
            if f20 not in px_by_date or t not in px_by_date:
                continue
            px_t, px_f = px_by_date[t], px_by_date[f20]
            fwd = (px_f.reindex(px_t.index) / px_t - 1.0).dropna()
            if len(fwd) < 100:
                continue
            vis = cross_section(t)
            vis = vis.reindex(fwd.index)
            for f in _FACTOR_COLS:
                pair = pd.concat([vis[f], fwd], axis=1).dropna()
                if len(pair) < 100:
                    continue
                out[f].append(float(spearmanr(pair.iloc[:, 0], pair.iloc[:, 1])[0]))
                cov[f].append(len(pair) / len(fwd))
        stats = {}
        for f in _FACTOR_COLS:
            s = np.array(out[f], dtype=float)
            if len(s) < 10:
                stats[f] = {"n": int(len(s)), "ic_mean": None, "t_p": None, "coverage": None}
                continue
            t_p = float(ttest_1samp(s, 0.0).pvalue)
            stats[f] = {"n": int(len(s)), "ic_mean": float(np.nanmean(s)),
                        "ic_ir": float(np.nanmean(s) / (np.nanstd(s, ddof=1) + 1e-12)),
                        "t_p": t_p, "coverage": float(np.nanmean(cov[f])),
                        "pass": bool(abs(np.nanmean(s)) >= 0.02 and t_p < 0.05
                                     and float(np.nanmean(cov[f])) >= 0.60)}
        return stats

    result = {"IS_2019_2023": ic_series(_IS), "OOS_2024": ic_series(_OOS)}

    # D3 双登记对照：FQ-01 vs FQ-02 池化秩相关
    pool = cross_section("2026-09-11")
    pair = pool[["fq01_accrual", "fq02_cash_conversion"]].dropna()
    d3 = {"n": int(len(pair)),
          "rank_corr": float(spearmanr(pair["fq01_accrual"], pair["fq02_cash_conversion"])[0])}
    result["D3_fq01_vs_fq02"] = d3

    text = json.dumps(result, ensure_ascii=False, indent=1)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0


def ch_reader_cal() -> list[str]:
    from zephyr.data import ch_reader

    tsv = ch_reader.query(
        "SELECT DISTINCT trade_date FROM c1_market.kline_daily WHERE trade_date >= '2019-01-01' "
        "AND trade_date <= '2026-09-11' ORDER BY trade_date FORMAT TSV")
    return [line.strip() for line in (tsv or "").split("\n") if line.strip()]


def _is_month_end(d: str, cal: list[str]) -> bool:
    i = cal.index(d)
    nxt = cal[i + 1] if i + 1 < len(cal) else None
    return nxt is None or nxt[:7] != d[:7]


if __name__ == "__main__":
    sys.exit(main())
