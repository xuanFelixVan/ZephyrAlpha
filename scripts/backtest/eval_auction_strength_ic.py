# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md（CNS-11 取证面）
# [MODULE] scripts.backtest.eval_auction_strength_ic
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas; zephyr.factor.auction_strength(输入装配+打分委托); zephyr.infrastructure.database_service(只读); zephyr.data.table_registry
# [CONSUMERS] factor_registry FCT-INTRADAY-025 evidence（IC 证据回填位）; docs/_working/night_sweep/SW14 案卷
# [STARTUP] manual（python scripts/backtest/eval_auction_strength_ic.py --start --end --out-dir）
# [MATURITY] testing
# [TTL] task_bound
# [INVARIANTS] 禁内建时钟（--start/--end 显式）；取证只读零写库；min_symbols 短样本披露不凑样
#              （截面过窄的日如实丢弃并计数，禁静默并入）；IC=Spearman 截面秩相关
#              （与前视收益 close[t+1]/close[t]-1 口径，成交可行性与成本另案，本件不判盈亏）；
#              证据=逐日 IC CSV + 汇总 JSON（可复核），禁只留结论
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读数空->RuntimeError；输出目录不可写->IOError 透传
# [TESTS] tests/factor/test_eval_auction_strength_ic.py（合成帧端到端，零 CH）
# [A_module] module_id=scripts.backtest.eval_auction_strength_ic | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""竞价强度因子（BM-SEL-23-A-5）IC 回测取证（CNS-11 验收面，SW14 夜战 2026-09-29）。

对 factor_registry 注册条目的 evidence 位产出可复核证据：
逐日横截面 Spearman(auction_strength_score, fwd_ret_1d) → mean/ic_ir/t_stat/覆盖。

样本窗=c1_market.auction_snapshot 实有窗口（2026-07-21 起，SW14 实测 412 万行 auction_book /
26.6 万快照行）；窗口短为如实披露（不凑样、不外推结论）。

用法::

    python scripts/backtest/eval_auction_strength_ic.py \
        --start 2026-07-21 --end 2026-09-26 \
        --out-dir docs/_working/night_sweep/sw14_auction_ic_evidence
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src"))
sys.path.insert(0, str(_REPO))

_FWD_DAY = 1  # 前视窗口：次日 close-to-close（与 pattern_win_rate 同口径族）
_DEFAULT_MIN_CROSS_SECTION = 30  # 截面秩相关最小样本（短样本如实弃日）
_MIN_CROSS_SECTION = _DEFAULT_MIN_CROSS_SECTION
# 前视收益源（NO-BARE-SQL §5.160.2 集中化：format 模板常量）
_SQL_KLINE_WINDOW = (
    "SELECT symbol, trade_date, close FROM {t} "
    "WHERE trade_date >= toDate('{s}') AND trade_date <= toDate('{e}') AND close > 0"
)


def load_forward_returns(start: str, end: str, *, conn, fwd: int = _FWD_DAY) -> dict[tuple[str, str], float]:
    """kline_daily 收盘面板 → {(symbol, trade_date_iso): fwd_ret}（t+fwd close-to-close）。

    与 regime_validation.chart_cell_materializer 同口径族（shift(-w) 前视，未成熟自然缺席），
    此处按 (symbol, day) dict 直取（因子面 join 键不同，不跨域复用其 make_fwd_key 拼装）。
    """
    from zephyr.data.table_registry import get_registry

    tbl = get_registry().table("market_kline_daily")
    end_buf = (pd.Timestamp(end) + pd.Timedelta(days=10)).date().isoformat()
    rows = conn.execute(_SQL_KLINE_WINDOW.format(t=tbl, s=start, e=end_buf))
    if not rows:
        raise RuntimeError("kline_daily 读数空——前视收益不可得，禁造证据")
    kdf = pd.DataFrame(rows, columns=["symbol", "trade_date", "close"])
    close = kdf.pivot_table(index="trade_date", columns="symbol", values="close", aggfunc="last").sort_index()
    close.index = pd.to_datetime(close.index)
    fwd_panel = close.shift(-fwd).div(close).sub(1)
    out: dict[tuple[str, str], float] = {}
    # stack() 后 MultiIndex 级序=(trade_date, symbol)（pivot index 在前）——解包须对应
    for (day, sym), v in fwd_panel.stack().items():
        out[(str(sym), pd.Timestamp(day).date().isoformat())] = float(v)
    return out


def daily_cross_section_ic(df: pd.DataFrame, fwd_map: dict[tuple[str, str], float]) -> pd.DataFrame:
    """逐日截面 Spearman IC（score vs fwd_ret）；截面 < min 样本日如实弃（计数披露）。"""
    rows = []
    for day, sub in df.groupby("trade_date"):
        day_iso = pd.Timestamp(day).date().isoformat()
        pairs = [
            (r.auction_strength_score, fwd_map[(str(r.symbol), day_iso)])
            for r in sub.itertuples(index=False)
            if (str(r.symbol), day_iso) in fwd_map
            and r.auction_strength_score is not None
            and not pd.isna(r.auction_strength_score)
        ]
        n = len(pairs)
        if n < _MIN_CROSS_SECTION:
            rows.append({"trade_date": day_iso, "n": n, "ic": None})
            continue
        s = pd.DataFrame(pairs, columns=["score", "fwd"])
        ic = s["score"].corr(s["fwd"], method="spearman")
        rows.append({"trade_date": day_iso, "n": n, "ic": None if pd.isna(ic) else float(ic)})
    return pd.DataFrame(rows)


def summarize(ic_df: pd.DataFrame) -> dict:
    """IC 序列 → mean/ic_ir/t_stat/覆盖（None 日不计入统计只计入披露）。"""
    valid = ic_df.dropna(subset=["ic"])
    n = len(valid)
    out: dict = {
        "n_days_total": int(len(ic_df)),
        "n_days_effective": int(n),
        "n_days_dropped_short": int((ic_df["ic"].isna()).sum()),
        "min_cross_section": _MIN_CROSS_SECTION,
    }
    if n < 2:
        out.update({"ic_mean": None, "ic_ir": None, "t_stat": None, "disclosure": "有效日不足 2——短样本不凑数"})
        return out
    ic = valid["ic"]
    mean = float(ic.mean())
    std = float(ic.std(ddof=1))
    icir = mean / std if std > 0 else None
    t = mean / (std / math.sqrt(n)) if std > 0 else None
    out.update(
        {
            "ic_mean": round(mean, 6),
            "ic_ir": None if icir is None else round(icir, 4),
            "t_stat": None if t is None else round(t, 4),
        }
    )
    return out


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="竞价强度因子 IC 取证（CNS-11 验收面）")
    ap.add_argument("--start", required=True, help="窗口起（显式传参，禁内建时钟）")
    ap.add_argument("--end", required=True, help="窗口止")
    ap.add_argument("--out-dir", default="docs/_working/night_sweep/sw14_auction_ic_evidence")
    ap.add_argument("--min-cross-section", type=int, default=None)
    args = ap.parse_args(argv)
    global _MIN_CROSS_SECTION  # noqa: PLW0603 — CLI 覆盖证尺阈值（取证披露位，非判据变更）
    if args.min_cross_section is not None:
        _MIN_CROSS_SECTION = args.min_cross_section

    from zephyr.factor.auction_strength import attach_scores, fetch_auction_inputs
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn(role="reader")
    inputs = fetch_auction_inputs(args.start, args.end, conn=conn)
    scored = attach_scores(inputs)
    fwd_map = load_forward_returns(args.start, args.end, conn=conn)
    ic_df = daily_cross_section_ic(scored, fwd_map)
    summary = summarize(ic_df)
    summary.update(
        {
            "factor_id": "FCT-INTRADAY-025",
            "alias": "BM-SEL-23-A-5",
            "window": [args.start, args.end],
            "fwd_window_days": _FWD_DAY,
            "method": "daily cross-section Spearman IC vs t+1 close-to-close",
            "rows_scored": int(len(scored)),
            "rows_with_score": int(scored["auction_strength_score"].notna().sum()),
        }
    )
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ic_df.to_csv(out / "daily_ic.csv", index=False)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
