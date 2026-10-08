# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.bench_scaling
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.panelized_indicators; zephyr.factor.technical_indicators.parity_check; zephyr.data.implementations.internal_compute_provider; pandas(pip); numpy(pip)
# [CONSUMERS] 运维/性能回归通道（python -m zephyr.factor.technical_indicators.bench_scaling；行物化切换收益复核）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 回答两问：① 物化段提速随 T（行数）如何变化：真实 001218 整史（CH 只读）逐档计时；② windowvec（滑窗向量化替换 rolling.apply Python 回调）在什么 T 下开始盈利：合成 OHLC 序列微基准（仅计时不参与对拍）；附带整史全列对拍（与 500 日口径同规则）验证等值性不随 T 漂移；CPU 纯算零 GPU 依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 读数为空→AssertionError 快速失败；产物写 .runtime/tmp 失败→OSError 上抛
# [TESTS] tests/zephyr/factor/technical_indicators/test_panelized_indicators.py
# [A_module] module_id=MOD-L02-TI-BENCH | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
bench_scaling — 行物化向量化 T 规模缩放计时（st-mx07-L5 转正；影子期证据 12.3-31.5x）。

用法：
  python -m zephyr.factor.technical_indicators.bench_scaling [--out .runtime/tmp/rowvec_parity]
CH 只读，零写库；TSV 产物落 .runtime/tmp（禁入包目录/项目根）。

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/bench_scaling.yaml
"""

from __future__ import annotations

import argparse
import datetime
import logging
import statistics
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# 仓根引导（schemas/ 顶层包依赖；从仓内任意 cwd 调用均可达）
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.disable(logging.INFO)


def bench_materialize_scaling(out_dir: Path):
    """真实数据整史：T 档 ∈ {250, 500, 1000, 整史}，物化段+全路径计时。"""
    from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider
    from zephyr.data.provider_base import FetchPayload
    from zephyr.data.table_registry import get_registry
    from zephyr.factor.technical_indicators import panelized_indicators as pi
    from zephyr.factor.technical_indicators.parity_check import (
        build_input,
        compare_rows,
        prod_path_rows,
        timeit,
        vec_path_rows,
    )

    prov, _per_symbol = build_input(["001218"], 500)
    payload = FetchPayload(
        table=get_registry().table("market_technical_indicator"),
        symbols=["001218"],
        start=datetime.date(2000, 1, 1),
        end=datetime.date(2026, 9, 30),
        incremental=False,
        extra={"period": "daily"},
    )
    kline = prov._read_kline_data(payload, "daily")
    kline = prov._merge_turnover_rate(kline, payload)
    sym_data_full = prov._filter_symbol(kline, "001218", "daily")
    t_total = len(sym_data_full)
    print(f"\n=== 物化段缩放（真实 001218 daily，整史 T={t_total}） ===")
    columns = InternalComputeProvider._get_indicator_columns()
    registered = pi.ensure_registry()
    rows_out = []
    for t in (250, 500, 1000, t_total):
        sd = sym_data_full.iloc[-t:]
        merged_p, _ = prod_path_rows(prov, sd, "001218", columns, registered)
        merged_s, rows_s = vec_path_rows(sd, "001218", columns, registered)
        # 对拍（每档验一次，等值性不随 T 漂移）
        _, rows_p2 = prod_path_rows(prov, sd, "001218", columns, registered)
        tbl = compare_rows(rows_p2, rows_s, columns)
        n_fail = int((tbl.status == "FAIL").sum())

        tp = timeit(
            lambda: [prov._build_row(b, "001218", "daily", rd, columns) for b, rd in merged_p.iterrows()], reps=7
        )
        ts = timeit(lambda: pi.materialize_rows_vectorized(merged_s, "001218", "daily", columns), reps=7)
        med_p, med_s = statistics.median(tp) * 1e3, statistics.median(ts) * 1e3
        print(
            f"T={t:>5}: prod物化={med_p:8.1f}ms vec物化={med_s:6.2f}ms 提速={med_p / med_s:6.1f}x 对拍FAIL列={n_fail}"
        )
        rows_out.append(
            {
                "T": t,
                "prod_ms": f"{med_p:.2f}",
                "vec_ms": f"{med_s:.2f}",
                "speedup": f"{med_p / med_s:.1f}",
                "fail_cols": n_fail,
            }
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows_out).to_csv(out_dir / "bench_scaling.tsv", sep="\t", index=False)


def bench_windowvec_scaling(out_dir: Path):
    """合成序列微基准：trend._wma（生产 rolling.apply）vs _wma_vec。"""
    from zephyr.factor.technical_indicators import panelized_indicators as pi
    from zephyr.factor.technical_indicators import trend
    from zephyr.factor.technical_indicators.parity_check import timeit

    rng = np.random.default_rng(42)
    print("\n=== windowvec 微基准（_wma: rolling.apply(np.dot) vs 滑窗矩阵乘） ===")
    rows = []
    for t in (500, 2000, 8000):
        close = pd.Series(100 + np.cumsum(rng.normal(0, 1, t)), index=pd.date_range("2020-1-1", periods=t, freq="D"))
        tp = timeit(lambda: trend._wma(close, 10), reps=9)
        ts = timeit(lambda: pi._wma_vec(close, 10), reps=9)
        d = np.nanmax(np.abs(trend._wma(close, 10).to_numpy() - pi._wma_vec(close, 10).to_numpy()))
        mp, ms = statistics.median(tp) * 1e3, statistics.median(ts) * 1e3
        print(f"T={t:>5}: prod={mp:7.2f}ms vec={ms:7.3f}ms 提速={mp / ms:6.1f}x max|Δ|={d:.2e}")
        rows.append(
            {
                "T": t,
                "prod_ms": f"{mp:.3f}",
                "vec_ms": f"{ms:.3f}",
                "speedup": f"{mp / ms:.1f}",
                "max_delta": f"{d:.2e}",
            }
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_dir / "bench_windowvec.tsv", sep="\t", index=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="行物化向量化规模缩放计时（CH 只读）")
    parser.add_argument("--out", type=Path, default=Path(".runtime/tmp/rowvec_parity"))
    args = parser.parse_args(argv)
    out_dir = args.out if args.out.is_absolute() else _REPO_ROOT / args.out

    t0 = time.perf_counter()
    bench_materialize_scaling(out_dir)
    bench_windowvec_scaling(out_dir)
    print(f"\n总耗时 {time.perf_counter() - t0:.1f}s")
    return 0


# noqa: m11-perm-manual-legitimate  M11豁免: 行物化性能基准 runner，AI/CI 按需调用（python -m）非 cron 非 daemon 非常驻服务，TSV 产物落 .runtime/tmp
if __name__ == "__main__":
    sys.exit(main())
