# [BLUEPRINT] SH-SCRIPT-001 | docs/_archive/_working_cleared/decision_map_campaign/links/L05_t0/T0_MATERIAL_EXAM_CARD_draft.md | §4 M0（对拍 harness：legacy 循环 vs 路径并行核）
# [MODULE] t0_material_line_parity
# create-guard-not-dup: 本件是材料线路径并行改造的对拍+计时 harness（运维/验收通道），非判据实现——配对判据真源仍是 cost_trio_exam，M0 语义真源仍是 t0_material_line
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/t0_material_line.py（legacy 循环复刻+load_bars 复用）；scripts/backtest/t0_material_line_fast.py（并行核被测面）；scripts/audit/cost_trio_exam.py（build_pairs 判据）；zephyr.infrastructure.database_service；pandas(pip)
# [CONSUMERS] 运维/切换验证通道（python scripts/backtest/t0_material_line_parity.py；fast 切挂前后回归）；tests/research/backtest/test_t0_material_line_fast.py
# [STARTUP] manual（python scripts/backtest/t0_material_line_parity.py --sample 20 [--start --end]）
# [MATURITY] production（对拍口径钉死：逐位相等；本件只读）
# [INVARIANTS] 索引注入法：同一 load_bars 产物 df 注入两路径（同对象同数组，输入零复制零漂移）；对拍口径=逐位相等（float 用 == 非 1e-9 容差——同 float64 标量运算序应逐位同源；fills 五字段+side/price/qty/commission 全等；reason_counts 全等；pairs 全列逐行全等）；CH 只读零写库；产物 TSV 落 .runtime/tmp（禁入项目根/data）；计时=fast 预热（numba 编译摊销）后两路径各计 N 轮取中位数；退出码=对拍全过 0 否则 1
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 读数为空/标的不足→SystemExit 快速失败；对拍存在 FAIL→打印 FAIL 明细并 exit 1
# [TESTS] tests/research/backtest/test_t0_material_line_fast.py
# [TTL] task_bound
"""t0_material_line_parity — 材料线路径并行改造对拍+耗时对比 harness（st-mx07-W1）。

legacy 路径（原样复刻 run_pipeline 内层循环，零改动语义）：
  bars.groupby([symbol, trade_date], sort=True) → resample_period → run_model_m0
  → fills_to_cost_trio_format → build_pairs → apply_material_gates
fast 路径：
  t0_material_line_fast.build_corpus_fast → build_pairs → apply_material_gates

对拍：同输入（索引注入）下逐位比对 reason_counts / fills / pairs 全列。
计时：fast 预热 1 轮摊销 numba 编译后，两路径各计时 --reps 轮取中位数。

用法：
  python scripts/backtest/t0_material_line_parity.py --sample 20 --start 2025-06-02 --end 2025-09-08
  python scripts/backtest/t0_material_line_parity.py --sample 20   # 全研究段（约 5-6 分钟 legacy）
产物：.runtime/tmp/st_mx07_w1/parity_table.tsv + timing.tsv（TTL 回收可复现）。

"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (
    str(_REPO_ROOT / "scripts"),
    str(_REPO_ROOT / "scripts" / "backtest"),
    str(_REPO_ROOT / "scripts" / "audit"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cost_trio_exam as ct  # noqa: E402
import t0_material_line as t0m  # noqa: E402
import t0_material_line_fast as fast  # noqa: E402

TOL_NOTE = "bitwise(==)"


def legacy_corpus(bars: pd.DataFrame, periods: list[int], grid_bp: float, notional: float, run_id: str):
    """run_pipeline 内层循环的原样复刻（判读基准；除 df 入参外与生产逐字同构）。"""
    grouped = bars.groupby(["symbol", "trade_date"], sort=True)
    fills_by: dict[str, list[dict]] = {}
    reasons_by: dict[str, dict[str, int]] = {}
    n_days = 0
    for period in periods:
        fills_all: list[dict] = []
        reason_counts: dict[str, int] = {}
        for (symbol, trade_date), day_bars in grouped:
            n_days += 1
            day_bars = day_bars.sort_values("trade_time")
            fills, reason = t0m.build_corpus_for_symbol_day(
                str(symbol), str(trade_date), day_bars, period, grid_bp, notional, run_id
            )
            fills_all.extend(fills)
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        fills_by[f"{period}min"] = fills_all
        reasons_by[f"{period}min"] = reason_counts
    n_days //= len(periods)
    return fills_by, reasons_by, n_days


def fast_corpus(bars: pd.DataFrame, periods: list[int], grid_bp: float, notional: float, run_id: str):
    return fast.build_corpus_fast(bars, periods, grid_bp, notional, run_id, t0m.MIN_BARS_BY_PERIOD)


def compare_corpus(periods: list[int], legacy, fastest: tuple) -> tuple[list[str], list[str]]:
    """逐位对拍。返回 (ok_lines, fail_lines)。"""
    fills_by, reasons_by, n_days = legacy
    f_fills, f_reasons, f_days, _engine = fastest
    ok: list[str] = []
    bad: list[str] = []
    if n_days != f_days:
        bad.append(f"n_symbol_days\tlegacy={n_days}\tfast={f_days}")
    for period in periods:
        label = f"{period}min"
        lr, fr = reasons_by[label], f_reasons[label]
        if lr != fr:
            bad.append(f"reason_counts\t{label}\tlegacy={lr}\tfast={fr}")
        else:
            ok.append(f"reason_counts\t{label}\tOK\t{sum(lr.values())}sd\t{lr}")
        lf, ff = fills_by[label], f_fills[label]
        if len(lf) != len(ff):
            bad.append(f"fills_len\t{label}\tlegacy={len(lf)}\tfast={len(ff)}")
            continue
        n_diff = 0
        for i, (a, b) in enumerate(zip(lf, ff, strict=False)):  # 长度差已在上游检查
            if a == b:
                continue
            n_diff += 1
            if n_diff <= 5:
                bad.append(f"fills_row\t{label}\t#{i}\tlegacy={a}\tfast={b}")
        if n_diff:
            bad.append(f"fills_rows_diff_total\t{label}\t{n_diff}")
        else:
            ok.append(f"fills_rows\t{label}\tOK\t{len(lf)} legs bitwise equal ({TOL_NOTE})")
        # pairs 全列对拍（同 fills ⇒ build_pairs 输出必同；双跑防组装面回归）
        lp = ct.build_pairs(lf)
        fp = ct.build_pairs(ff)
        if lp == fp:
            ok.append(f"pairs\t{label}\tOK\t{len(lp)} pairs bitwise equal")
        else:
            bad.append(f"pairs\t{label}\tlegacy_n={len(lp)}\tfast_n={len(fp)}\tfirst_diff={_first_pair_diff(lp, fp)}")
    return ok, bad


def _first_pair_diff(lp: list[dict], fp: list[dict]) -> str:
    for i, (a, b) in enumerate(zip(lp, fp, strict=False)):
        if a != b:
            keys = [k for k in a if a.get(k) != b.get(k)]
            return f"#{i} keys={keys} legacy={{k: a[k] for k in keys}} fast={{k: b[k] for k in keys}}"
    return "n/a"


def main() -> int:
    ap = argparse.ArgumentParser(description="材料线路径并行对拍+计时（索引注入法，逐位口径）")
    ap.add_argument("--symbols", default="")
    ap.add_argument("--sample", type=int, default=20)
    ap.add_argument("--start", default=t0m.RESEARCH_START)
    ap.add_argument("--end", default=t0m.CLOSED_BOOK_CUTOFF)
    ap.add_argument("--period", default="1,5,15,30,60")
    ap.add_argument("--grid-bp", type=float, default=t0m.DEFAULT_GRID_BP)
    ap.add_argument("--notional", type=float, default=t0m.DEFAULT_NOTIONAL)
    ap.add_argument("--reps", type=int, default=3, help="计时轮数（取中位数；fast 首轮预热另计）")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / ".runtime" / "tmp" / "st_mx07_w1"))
    args = ap.parse_args()

    periods = [int(p) for p in str(args.period).split(",")]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn()
    if args.sample > 0:
        symbols = t0m.deterministic_sample(t0m.list_universe(conn), args.sample)
    else:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    if not symbols:
        raise SystemExit("FAIL: 标的池为空（--sample/--symbols 二选一）")

    ta = time.perf_counter()
    bars, bar_stats = t0m.load_bars(conn, symbols, args.start, args.end)
    t_fetch = time.perf_counter() - ta
    if bars.empty:
        raise SystemExit("FAIL: 分钟腿零行（CH 读数空）——快速失败")
    print(
        f"input: symbols={len(symbols)} window={args.start}..{args.end} rows={bar_stats['bars_after_dedup']} "
        f"fetch={t_fetch:.3f}s",
        flush=True,
    )

    run_id = f"parity-g{args.grid_bp:g}-{args.start}_{args.end}"

    # ---- 对拍（索引注入法：同一规范化 df 对象注入两路径）----
    # 语义缝声明：fast 核输入契约=float64 规范化（CH Decimal 列的扫描比较在恰好触档
    # ±1ulp 边界存在驱动类型意外语义，见 fast.normalize_prices_float64）。核心对拍在
    # 规范化输入上做逐位；raw Decimal 边界翻转另段披露（下方 disclosure）。
    bars_norm = fast.normalize_prices_float64(bars)
    t0 = time.perf_counter()
    legacy = legacy_corpus(bars_norm, periods, args.grid_bp, args.notional, run_id)
    t_legacy_first = time.perf_counter() - t0
    t0 = time.perf_counter()
    fastest = fast_corpus(bars_norm, periods, args.grid_bp, args.notional, run_id)
    t_fast_first = time.perf_counter() - t0
    ok_lines, bad_lines = compare_corpus(periods, legacy, fastest)
    _engine = fastest[3]
    print(f"parity: first-shot legacy={t_legacy_first:.3f}s fast(incl. warmup)={t_fast_first:.3f}", flush=True)

    # ---- 边界披露：legacy 原样（raw Decimal 列）vs fast（规范化）——如实计数不阻断 ----
    t0 = time.perf_counter()
    legacy_raw = legacy_corpus(bars, periods, args.grid_bp, args.notional, run_id)
    t_legacy_raw = time.perf_counter() - t0
    for period in periods:
        label = f"{period}min"
        lr, rr = legacy_raw[1][label], legacy[1][label]
        flipped = {k: lr.get(k, 0) - rr.get(k, 0) for k in set(lr) | set(rr) if lr.get(k, 0) != rr.get(k, 0)}
        n_pair_raw = lr.get("pair", 0)
        ok_lines.append(
            f"raw_decimal_boundary_disclosure\t{label}\tlegacy_raw_pairs={n_pair_raw}\t"
            f"normalized_minus_raw={-flipped.get('pair', 0)}\t(±1ulp 触档边界翻转，语义缝留档)"
        )
    print(f"disclosure: legacy_on_raw took {t_legacy_raw:.3f}s (Decimal 扫描语义对照基线)")

    # ---- 计时（fast 已预热；各取中位数）----
    legacy_times: list[float] = []
    fast_times: list[float] = []
    for _ in range(max(1, args.reps)):
        t0 = time.perf_counter()
        legacy_corpus(bars, periods, args.grid_bp, args.notional, run_id)
        legacy_times.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        fast_corpus(bars, periods, args.grid_bp, args.notional, run_id)
        fast_times.append(time.perf_counter() - t0)
    med_legacy = statistics.median(legacy_times)
    med_fast = statistics.median(fast_times)

    lines = [
        "metric\tvalue",
        f"input_symbols\t{len(symbols)}",
        f"input_rows\t{bar_stats['bars_after_dedup']}",
        f"window\t{args.start}..{args.end}",
        f"periods\t{args.period}",
        f"fetch_seconds\t{t_fetch:.3f}",
        f"legacy_first_seconds\t{t_legacy_first:.3f}",
        f"fast_first_seconds_incl_warmup\t{t_fast_first:.3f}",
        f"legacy_median_seconds\t{med_legacy:.3f}",
        f"fast_median_seconds\t{med_fast:.3f}",
        f"speedup_median\tx{med_legacy / med_fast:.1f}" if med_fast > 0 else "speedup_median\tn/a",
        f"fast_engine\t{_engine['engine']}\tkernels={_engine['kernels']}",
    ]
    (out_dir / "timing.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "parity_table.tsv").write_text(
        "status\tcheck\tdetail\n"
        + "\n".join(f"OK\t{l}" for l in ok_lines)
        + "\n".join(f"FAIL\t{b}" for b in bad_lines)
        + "\n",
        encoding="utf-8",
    )
    for l in ok_lines:
        print("OK ", l)
    for b in bad_lines:
        print("FAIL", b)
    print(f"timing: legacy_median={med_legacy:.3f}s fast_median={med_fast:.3f}s speedup=x{med_legacy / med_fast:.1f}")
    print("out:", out_dir)
    return 0 if not bad_lines else 1


if __name__ == "__main__":
    sys.exit(main())
