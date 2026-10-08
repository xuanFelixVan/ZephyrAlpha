# [BLUEPRINT] MOD-L02-001 | docs/03_modules/MOD-L02-001/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [MODULE] scripts.matrix_rescued_tmp.rowvec.bench_scaling
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
# [SHADOW] st-matrix-20261007 / M道：T 规模缩放计时（真实数据整史 + 合成序列微基准）
# [TTL] task_bound
# create-guard-not-dup: tmp 24h TTL 抢救转正件（st-matrix-20261007 P0-1 抢救面；转正退役语义见 L5 token merge_evaluation）
"""
bench_scaling — 回答两个问题：
  1) 物化段提速随 T（行数）如何变化：真实 001218 整史（CH 只读）逐档计时；
  2) windowvec（滑窗向量化替换 rolling.apply Python 回调）在什么 T 下开始盈利：
     合成 OHLC 序列 T∈{500, 2000, 8000} 微基准（仅计时，不参与对拍）。
附带：整史全列对拍（与 500 日口径同规则），验证等值性不随 T 漂移。
"""

from __future__ import annotations

import datetime
import logging
import statistics
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PROJ = Path(r"D:\ZephyrAlpha")
sys.path.insert(0, str(PROJ))
sys.path.insert(0, str(PROJ / "src"))
sys.path.insert(0, str(HERE))

import panelized_indicators as pi
from parity_check import build_input, compare_rows, prod_path_rows, shadow_path_rows, timeit

from zephyr.data.table_registry import get_registry as _get_tbl_registry

# TABLE-NAME-REGISTRY 合规：表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5），抢救证据件同规
_TBL_TECH_IND = _get_tbl_registry().table("market_technical_indicator")

logging.disable(logging.INFO)


def bench_materialize_scaling():
    """真实数据整史：T 档 ∈ {250, 500, 1000, 整史}，物化段+全路径计时。"""
    from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider

    prov, per_symbol = build_input()
    sym_data_full = None
    from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider as ICP
    from zephyr.data.provider_base import FetchPayload

    payload = FetchPayload(
        table=_TBL_TECH_IND,
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
    columns = ICP._get_indicator_columns()
    registered = pi.ensure_registry()
    rows_out = []
    for t in (250, 500, 1000, t_total):
        sd = sym_data_full.iloc[-t:]
        merged_p, _ = prod_path_rows(prov, sd, "001218", columns, registered)
        merged_s, rows_s = shadow_path_rows(sd, "001218", columns, registered)
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
            f"T={t:>5}: prod物化={med_p:8.1f}ms shadow物化={med_s:6.2f}ms 提速={med_p / med_s:6.1f}x 对拍FAIL列={n_fail}"
        )
        rows_out.append(
            {
                "T": t,
                "prod_ms": f"{med_p:.2f}",
                "shadow_ms": f"{med_s:.2f}",
                "speedup": f"{med_p / med_s:.1f}",
                "fail_cols": n_fail,
            }
        )
    pd.DataFrame(rows_out).to_csv(HERE / "bench_scaling.tsv", sep="\t", index=False)


def bench_windowvec_scaling():
    """合成序列微基准：trend._wma（生产 rolling.apply）vs _wma_vec。"""
    from zephyr.factor.technical_indicators import trend

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
    pd.DataFrame(rows).to_csv(HERE / "bench_windowvec.tsv", sep="\t", index=False)


if __name__ == "__main__":
    t0 = time.perf_counter()
    bench_materialize_scaling()
    bench_windowvec_scaling()
    print(f"\n总耗时 {time.perf_counter() - t0:.1f}s")
