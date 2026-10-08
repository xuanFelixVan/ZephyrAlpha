# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.parity_check
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.panelized_indicators; zephyr.data.implementations.internal_compute_provider; pandas(pip); numpy(pip)
# [CONSUMERS] 运维/切换验证通道（python -m zephyr.factor.technical_indicators.parity_check；行物化切挂前后回归）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 生产路径 vs 向量化路径全列对拍 harness：数值列 |Δ|≤1e-9、NaN/None 模式全等（生产 None ⇔ 向量化 None）、元数据列全等；CH 只读零写库；计时=两路径各预热 1 轮后计时 5 轮取中位数，全路径与物化段分开留档；退出码=对拍全过 0 否则 1
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 读数为空/标的根数不足→AssertionError 快速失败；对拍存在 FAIL 列→exit 1 并打印 FAIL 明细
# [TESTS] tests/zephyr/factor/technical_indicators/test_panelized_indicators.py
# [A_module] module_id=MOD-L02-TI-PARITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
parity_check — 生产路径 vs 向量化路径全列对拍 + 耗时对比（st-mx07-L5 转正）。

生产路径（原样调用，零改动）：
  InternalComputeProvider._read_kline_data → _merge_turnover_rate → _filter_symbol
  → _compute_all_indicators → iterrows() + _build_row()
向量化路径：
  panelized_indicators.compute_indicator_matrix → materialize_rows_vectorized

对拍口径：数值列 |Δ|≤1e-9；NaN/None 模式全等（生产 None ⇔ 向量化 None）；
元数据列（date/datetime/str）全等。逐列出对拍表 parity_table.tsv。
计时：两路径各预热 1 轮后计时 5 轮取中位数，全路径与物化段分开留档 timing.tsv。

用法：
  python -m zephyr.factor.technical_indicators.parity_check \
      [--symbols 001218 603938] [--bars 500] [--out .runtime/tmp/rowvec_parity]
CH 只读，零写库；TSV 产物落 .runtime/tmp（禁入包目录/项目根）。

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/parity_check.yaml
"""

from __future__ import annotations

import argparse
import datetime
import logging
import statistics
import sys
import time
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

# 仓根引导（schemas/ 顶层包依赖；从仓内任意 cwd 调用均可达）
_REPO_ROOT = Path(__file__).resolve().parents[4]
for _p in (str(_REPO_ROOT),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

DEFAULT_SYMBOLS: Final = ["001218", "603938"]
DEFAULT_N_BARS = 500
REPS = 5
TOL = 1e-9
START = datetime.date(2024, 6, 1)  # 宽读窗，取数后逐标的裁最后 N 根
END = datetime.date(2026, 9, 30)

logging.basicConfig(level=logging.ERROR)  # 静音生产 INFO/WARN 日志防污染计时
for name in ("integrator.internal", "zephyr", "ch_writer", "ch_reader"):
    logging.getLogger(name).setLevel(logging.ERROR)


def build_input(symbols: list[str], n_bars: int):
    """与生产逐字节同源的输入（直接调用生产读取链，零复制）。"""
    from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider
    from zephyr.data.provider_base import FetchPayload
    from zephyr.data.table_registry import get_registry

    prov = InternalComputeProvider()
    payload = FetchPayload(
        table=get_registry().table("market_technical_indicator"),
        symbols=list(symbols),
        start=START,
        end=END,
        incremental=False,
        extra={"period": "daily"},
    )
    kline = prov._read_kline_data(payload, "daily")
    assert not kline.empty, "CH 读数为空"
    kline = prov._merge_turnover_rate(kline, payload)

    per_symbol = {}
    for sym in symbols:
        sd = prov._filter_symbol(kline, sym, "daily")
        sd = sd.iloc[-n_bars:]  # 近 N 根
        assert len(sd) == n_bars, f"{sym} 不足 {n_bars} 根: {len(sd)}"
        per_symbol[sym] = sd
    return prov, per_symbol


def prod_path_rows(prov, sym_data, sym, columns, registered):
    """生产路径：_compute_all_indicators + iterrows + _build_row（原样）。"""
    merged = prov._compute_all_indicators(sym_data, registered)
    rows = []
    for bar_ts, row_data in merged.iterrows():
        rows.append(prov._build_row(bar_ts, sym, "daily", row_data, columns))
    return merged, rows


def vec_path_rows(sym_data, sym, columns, registered):
    """向量化路径：compute_indicator_matrix + materialize_rows_vectorized。"""
    from zephyr.factor.technical_indicators import panelized_indicators as pi

    merged = pi.compute_indicator_matrix(sym_data, registered)
    rows = pi.materialize_rows_vectorized(merged, sym, "daily", columns)
    return merged, rows


def compare_rows(rows_p, rows_s, columns):
    """逐列对拍：数值 |Δ|≤1e-9，NaN/None 模式全等，元数据全等。"""
    n = len(rows_p)
    table = []
    for j, col in enumerate(columns):
        n_match = 0
        n_none_both = 0
        n_nan_mism = 0
        n_val_mism = 0
        max_d = 0.0
        first_bad = None
        for t in range(n):
            a = rows_p[t][j]
            b = rows_s[t][j]
            a_none = a is None or (isinstance(a, float) and not np.isfinite(a))
            b_none = b is None or (isinstance(b, float) and not np.isfinite(b))
            if a_none and b_none:
                n_none_both += 1
                n_match += 1
            elif a_none != b_none:
                n_nan_mism += 1
                if first_bad is None:
                    first_bad = t
            elif isinstance(a, (int, float, np.floating, np.integer)) and isinstance(
                b, (int, float, np.floating, np.integer)
            ):
                d = abs(float(a) - float(b))
                max_d = max(max_d, d)
                if d <= TOL:
                    n_match += 1
                else:
                    n_val_mism += 1
                    if first_bad is None:
                        first_bad = t
            elif a == b:
                n_match += 1
            else:
                n_val_mism += 1
                if first_bad is None:
                    first_bad = t
        status = "PASS" if (n_nan_mism + n_val_mism) == 0 else "FAIL"
        table.append(
            {
                "column": col,
                "n": n,
                "match": n_match,
                "none_both": n_none_both,
                "nan_mismatch": n_nan_mism,
                "val_mismatch": n_val_mism,
                "max_abs_delta": f"{max_d:.3e}" if max_d > 0 else "0",
                "first_bad_row": first_bad if first_bad is not None else "",
                "status": status,
            }
        )
    return pd.DataFrame(table)


def timeit(fn, reps=REPS):
    fn()  # 预热
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return ts


def main(argv: list[str] | None = None) -> int:
    from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider

    parser = argparse.ArgumentParser(description="指标链行物化对拍+计时（CH 只读）")
    parser.add_argument("--symbols", nargs="+", default=DEFAULT_SYMBOLS)
    parser.add_argument("--bars", type=int, default=DEFAULT_N_BARS)
    parser.add_argument("--out", type=Path, default=Path(".runtime/tmp/rowvec_parity"))
    args = parser.parse_args(argv)

    from zephyr.factor.technical_indicators import panelized_indicators as pi
    from zephyr.factor.technical_indicators import trend

    print("=== 输入构建（生产读取链，CH 只读） ===")
    prov, per_symbol = build_input(args.symbols, args.bars)
    columns = InternalComputeProvider._get_indicator_columns()
    out_dir = args.out if args.out.is_absolute() else _REPO_ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    registered = pi.ensure_registry()
    # windowvec 激活断言：覆盖表命中本批注册指标 + 补丁域内模块函数确被替换
    reg_ids = {m.indicator_id for m in registered}
    assert {"cci", "aroon", "aroonosc", "connorsrsi", "rvgi", "wma", "hma", "inertia"} <= reg_ids
    assert set(pi._SHADOW_COMPUTE) <= reg_ids, "向量化覆盖表含未注册指标"
    with pi._PatchedHelpers():
        assert trend._wma is pi._wma_vec and trend._linreg_endpoint is pi._linreg_endpoint_vec
    assert trend._wma is not pi._wma_vec, "补丁未还原（污染生产模块态）"
    print(
        f"标的={args.symbols} 每标的 {args.bars} 根 | 表列 {len(columns)} | 注册指标 {len(registered)} | windowvec=激活"
    )

    all_tables = []
    timing_rows = []
    for sym in args.symbols:
        sym_data = per_symbol[sym]
        print(f"\n=== {sym} 对拍（n={len(sym_data)}） ===")

        # --- 对拍（各跑一遍，逐列比对） ---
        merged_p, rows_p = prod_path_rows(prov, sym_data, sym, columns, registered)
        merged_s, rows_s = vec_path_rows(sym_data, sym, columns, registered)
        assert list(merged_p.columns) == list(merged_s.columns), "merged 列集不一致"
        tbl = compare_rows(rows_p, rows_s, columns)
        tbl.insert(0, "symbol", sym)
        all_tables.append(tbl)
        n_pass = (tbl["status"] == "PASS").sum()
        print(f"列通过 {n_pass}/{len(tbl)} | FAIL 列: {tbl.loc[tbl.status == 'FAIL', 'column'].tolist()}")

        # --- 计时（预热 1 轮 + 5 轮取中位；全路径/计算段/物化段三层） ---
        t_prod_full = timeit(lambda: prod_path_rows(prov, sym_data, sym, columns, registered))
        t_vec_full = timeit(lambda: vec_path_rows(sym_data, sym, columns, registered))
        t_prod_comp = timeit(lambda: prov._compute_all_indicators(sym_data, registered))
        t_vec_comp = timeit(lambda: pi.compute_indicator_matrix(sym_data, registered))
        t_prod_mat = timeit(lambda: [prov._build_row(b, sym, "daily", rd, columns) for b, rd in merged_p.iterrows()])
        t_vec_mat = timeit(lambda: pi.materialize_rows_vectorized(merged_s, sym, "daily", columns))

        med = statistics.median
        ratio_full = med(t_prod_full) / med(t_vec_full)
        ratio_mat = med(t_prod_mat) / med(t_vec_mat)
        print(
            f"计时: 全路径 prod={med(t_prod_full) * 1e3:.1f}ms vec={med(t_vec_full) * 1e3:.1f}ms"
            f" ({ratio_full:.1f}x) | 计算段 prod={med(t_prod_comp) * 1e3:.1f}ms"
            f" vec={med(t_vec_comp) * 1e3:.1f}ms | 物化段 prod={med(t_prod_mat) * 1e3:.1f}ms"
            f" vec={med(t_vec_mat) * 1e3:.1f}ms ({ratio_mat:.1f}x)"
        )
        timing_rows.append(
            {
                "symbol": sym,
                "n_rows": len(sym_data),
                "n_cols": len(columns),
                "prod_full_ms": f"{med(t_prod_full) * 1e3:.2f}",
                "vec_full_ms": f"{med(t_vec_full) * 1e3:.2f}",
                "speedup_full": f"{ratio_full:.2f}",
                "prod_compute_ms": f"{med(t_prod_comp) * 1e3:.2f}",
                "vec_compute_ms": f"{med(t_vec_comp) * 1e3:.2f}",
                "prod_materialize_ms": f"{med(t_prod_mat) * 1e3:.2f}",
                "vec_materialize_ms": f"{med(t_vec_mat) * 1e3:.2f}",
                "speedup_materialize": f"{ratio_mat:.2f}",
                "prod_full_min_ms": f"{min(t_prod_full) * 1e3:.2f}",
                "vec_full_min_ms": f"{min(t_vec_full) * 1e3:.2f}",
            }
        )

    # --- 落盘对拍表与计时表 ---
    parity = pd.concat(all_tables, ignore_index=True)
    parity_path = out_dir / "parity_table.tsv"
    timing_path = out_dir / "timing.tsv"
    parity.to_csv(parity_path, sep="\t", index=False)
    pd.DataFrame(timing_rows).to_csv(timing_path, sep="\t", index=False)

    total_cols = len(parity)
    pass_cols = (parity["status"] == "PASS").sum()
    print("\n=== 汇总 ===")
    print(f"对拍列通过率: {pass_cols}/{total_cols} ({pass_cols / total_cols * 100:.1f}%)")
    fail = parity[parity.status == "FAIL"]
    if not fail.empty:
        print(fail[["symbol", "column", "nan_mismatch", "val_mismatch", "max_abs_delta"]].to_string(index=False))
    print(f"对拍表 → {parity_path}")
    print(f"计时表 → {timing_path}")
    return 0 if pass_cols == total_cols else 1


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 行物化切挂前后回归验收 runner，AI/CI 按需调用（python -m）非 cron 非 daemon 非常驻服务，产物落 .runtime/tmp
    sys.exit(main())
