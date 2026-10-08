# [BLUEPRINT] MOD-L02-001 | docs/03_modules/MOD-L02-001/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [MODULE] scripts.matrix_rescued_tmp.rowvec.parity_check
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] 无（一次性考卷/对拍/计时证据件；随附数据在 docs/_working/matrix_campaign/rescued_tmp_20261007/）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 抢救证据件原样保留，判定面不入核；表名走 TableRegistry 真源
# [MODIFY-GUARD] freeze——抢救证据件禁改写业务逻辑（门禁合规头/noqa 除外）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 运行期异常如实抛出（证据件不吞错不改判）
# [TESTS] 无独立测试（一次性证据件，输出随件入册）
# [SHADOW] st-matrix-20261007 / M道：对拍+计时 harness（CH 只读，零写库，禁 git）
# [TTL] task_bound
# create-guard-not-dup: tmp 24h TTL 抢救转正件（st-matrix-20261007 P0-1 抢救面；转正退役语义见 L5 token merge_evaluation）
"""
parity_check — 生产路径 vs 影子路径全列对拍 + 耗时对比。

生产路径（原样调用，零改动）：
  InternalComputeProvider._read_kline_data → _merge_turnover_rate → _filter_symbol
  → _compute_all_indicators → iterrows() + _build_row()
影子路径：
  panelized_indicators.compute_indicator_matrix → materialize_rows_vectorized

对拍口径：数值列 |Δ|≤1e-9；NaN/None 模式全等（生产 None ⇔ 影子 None）；
元数据列（date/datetime/str）全等。逐列出对拍表 parity_table.tsv。
计时：两路径各预热 1 轮后计时 5 轮取中位数，全路径与物化段分开留档 timing.tsv。
"""

from __future__ import annotations

import datetime
import logging
import statistics
import sys
import time
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

from zephyr.data.table_registry import get_registry as _get_tbl_registry

# TABLE-NAME-REGISTRY 合规：表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5），抢救证据件同规
_TBL_TECH_IND = _get_tbl_registry().table("market_technical_indicator")

HERE = Path(__file__).resolve().parent
PROJ = Path(r"D:\ZephyrAlpha")
sys.path.insert(0, str(PROJ))  # schemas/ 顶层包（production _get_indicator_columns 依赖）
sys.path.insert(0, str(PROJ / "src"))
sys.path.insert(0, str(HERE))

SYMBOLS = ["001218", "603938"]
N_BARS = 500
REPS = 5
TOL = 1e-9
START = datetime.date(2024, 6, 1)  # 宽读窗，取数后逐标的裁最后 500 根
END = datetime.date(2026, 9, 30)

logging.basicConfig(level=logging.ERROR)  # 静音生产 INFO/WARN 日志防污染计时
for name in ("integrator.internal", "zephyr", "ch_writer", "ch_reader"):
    logging.getLogger(name).setLevel(logging.ERROR)


def build_input():
    """与生产逐字节同源的输入（直接调用生产读取链，零复制）。"""
    from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider
    from zephyr.data.provider_base import FetchPayload

    prov = InternalComputeProvider()
    payload = FetchPayload(
        table=_TBL_TECH_IND,
        symbols=list(SYMBOLS),
        start=START,
        end=END,
        incremental=False,
        extra={"period": "daily"},
    )
    kline = prov._read_kline_data(payload, "daily")
    assert not kline.empty, "CH 读数为空"
    kline = prov._merge_turnover_rate(kline, payload)

    per_symbol = {}
    for sym in SYMBOLS:
        sd = prov._filter_symbol(kline, sym, "daily")
        sd = sd.iloc[-N_BARS:]  # 近 500 根
        assert len(sd) == N_BARS, f"{sym} 不足 {N_BARS} 根: {len(sd)}"
        per_symbol[sym] = sd
    return prov, per_symbol


def prod_path_rows(prov, sym_data, sym, columns, registered):
    """生产路径：_compute_all_indicators + iterrows + _build_row（原样）。"""
    merged = prov._compute_all_indicators(sym_data, registered)
    rows = []
    for bar_ts, row_data in merged.iterrows():
        rows.append(prov._build_row(bar_ts, sym, "daily", row_data, columns))
    return merged, rows


def shadow_path_rows(sym_data, sym, columns, registered):
    """影子路径：compute_indicator_matrix + materialize_rows_vectorized。"""
    import panelized_indicators as pi

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


def main():
    from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider

    print("=== 输入构建（生产读取链，CH 只读） ===")
    prov, per_symbol = build_input()
    columns = InternalComputeProvider._get_indicator_columns()
    import panelized_indicators as pi

    from zephyr.factor.technical_indicators import trend

    registered = pi.ensure_registry()
    # windowvec 激活断言：覆盖表命中本批注册指标 + 补丁域内模块函数确被替换
    reg_ids = {m.indicator_id for m in registered}
    assert {"cci", "aroon", "aroonosc", "connorsrsi", "rvgi", "wma", "hma", "inertia"} <= reg_ids
    assert set(pi._SHADOW_COMPUTE) <= reg_ids, "影子覆盖表含未注册指标"
    with pi._PatchedHelpers():
        assert trend._wma is pi._wma_vec and trend._linreg_endpoint is pi._linreg_endpoint_vec
    assert trend._wma is not pi._wma_vec, "补丁未还原（污染生产模块态）"
    print(f"标的={SYMBOLS} 每标的 {N_BARS} 根 | 表列 {len(columns)} | 注册指标 {len(registered)} | windowvec=激活")

    all_tables = []
    timing_rows = []
    for sym in SYMBOLS:
        sym_data = per_symbol[sym]
        print(f"\n=== {sym} 对拍（n={len(sym_data)}） ===")

        # --- 对拍（各跑一遍，逐列比对） ---
        merged_p, rows_p = prod_path_rows(prov, sym_data, sym, columns, registered)
        merged_s, rows_s = shadow_path_rows(sym_data, sym, columns, registered)
        assert list(merged_p.columns) == list(merged_s.columns), "merged 列集不一致"
        tbl = compare_rows(rows_p, rows_s, columns)
        tbl.insert(0, "symbol", sym)
        all_tables.append(tbl)
        n_pass = (tbl["status"] == "PASS").sum()
        print(f"列通过 {n_pass}/{len(tbl)} | FAIL 列: {tbl.loc[tbl.status == 'FAIL', 'column'].tolist()}")

        # --- 计时（预热 1 轮 + 5 轮取中位；全路径/计算段/物化段三层） ---
        import panelized_indicators as pi

        t_prod_full = timeit(lambda: prod_path_rows(prov, sym_data, sym, columns, registered))
        t_shad_full = timeit(lambda: shadow_path_rows(sym_data, sym, columns, registered))
        t_prod_comp = timeit(lambda: prov._compute_all_indicators(sym_data, registered))
        t_shad_comp = timeit(lambda: pi.compute_indicator_matrix(sym_data, registered))
        t_prod_mat = timeit(lambda: [prov._build_row(b, sym, "daily", rd, columns) for b, rd in merged_p.iterrows()])
        t_shad_mat = timeit(lambda: pi.materialize_rows_vectorized(merged_s, sym, "daily", columns))

        med = statistics.median
        ratio_full = med(t_prod_full) / med(t_shad_full)
        ratio_mat = med(t_prod_mat) / med(t_shad_mat)
        print(
            f"计时: 全路径 prod={med(t_prod_full) * 1e3:.1f}ms shadow={med(t_shad_full) * 1e3:.1f}ms"
            f" ({ratio_full:.1f}x) | 计算段 prod={med(t_prod_comp) * 1e3:.1f}ms"
            f" shadow={med(t_shad_comp) * 1e3:.1f}ms | 物化段 prod={med(t_prod_mat) * 1e3:.1f}ms"
            f" shadow={med(t_shad_mat) * 1e3:.1f}ms ({ratio_mat:.1f}x)"
        )
        timing_rows.append(
            {
                "symbol": sym,
                "n_rows": len(sym_data),
                "n_cols": len(columns),
                "prod_full_ms": f"{med(t_prod_full) * 1e3:.2f}",
                "shadow_full_ms": f"{med(t_shad_full) * 1e3:.2f}",
                "speedup_full": f"{ratio_full:.2f}",
                "prod_compute_ms": f"{med(t_prod_comp) * 1e3:.2f}",
                "shadow_compute_ms": f"{med(t_shad_comp) * 1e3:.2f}",
                "prod_materialize_ms": f"{med(t_prod_mat) * 1e3:.2f}",
                "shadow_materialize_ms": f"{med(t_shad_mat) * 1e3:.2f}",
                "speedup_materialize": f"{ratio_mat:.2f}",
                "prod_full_min_ms": f"{min(t_prod_full) * 1e3:.2f}",
                "shadow_full_min_ms": f"{min(t_shad_full) * 1e3:.2f}",
            }
        )

    # --- 落盘对拍表与计时表 ---
    parity = pd.concat(all_tables, ignore_index=True)
    parity.to_csv(HERE / "parity_table.tsv", sep="\t", index=False)
    pd.DataFrame(timing_rows).to_csv(HERE / "timing.tsv", sep="\t", index=False)

    total_cols = len(parity)
    pass_cols = (parity["status"] == "PASS").sum()
    print("\n=== 汇总 ===")
    print(f"对拍列通过率: {pass_cols}/{total_cols} ({pass_cols / total_cols * 100:.1f}%)")
    fail = parity[parity.status == "FAIL"]
    if not fail.empty:
        print(fail[["symbol", "column", "nan_mismatch", "val_mismatch", "max_abs_delta"]].to_string(index=False))
    print(f"对拍表 → {HERE / 'parity_table.tsv'}")
    print(f"计时表 → {HERE / 'timing.tsv'}")
    return 0 if pass_cols == total_cols else 1


if __name__ == "__main__":
    sys.exit(main())
