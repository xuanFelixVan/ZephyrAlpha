# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | IC核numpy基线计时（20列基线留档）
# [MODULE] scripts.backtest.fexam.gpu_ic.bench_numpy.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] run_fexam.py 或手工 CLI
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] staging 转正件；判定面不入核
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见 docstring
# [TESTS] tests/backtest/fexam/
# [TTL] task_bound
# create-guard-not-dup: tmp 24h TTL 抢救转正件（Owner 批 P0-1），对拍结论已锁定随文件
# [LANE] st-matrix-20261006/gpu_ic | G道：IC 内核 GPU 移植（对拍版）
"""bench_numpy — rank_ic(numpy) 基线计时：5000 票 × 485 日 × 20 列（fexam WINDOW_UNION 同尺度）。

产出即 GPU 版将来对照基线（cupy 后端由 smoke_gpu.py 在 quiet 窗口补测同规模计时）。
计时前先做一次该规模对拍抽查（防计时口径偏离对拍内核）。
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[3]
for _p in (str(_ROOT / "src"), str(_ROOT / "scripts" / "backtest" / "fexam"), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from gpu_rank_ic import rank_ic  # noqa: E402
from ic_exam import fast_rank_ic  # noqa: E402

N_TICK, N_DAY, N_COL = 5000, 485, 20
REPEAT = 3
TOL = 1e-9


def build() -> tuple[list[pd.DataFrame], pd.DataFrame]:
    """合成 20 列因子面板（3% NaN）+ 共享 ret 面板（1% NaN）。"""
    rng = np.random.default_rng(7)
    idx = pd.bdate_range(end="2026-09-30", periods=N_DAY)
    cols = [f"S{i:05d}" for i in range(N_TICK)]
    ret = pd.DataFrame(rng.normal(0, 0.02, (N_DAY, N_TICK)), index=idx, columns=cols)
    ret[rng.random(ret.shape) < 0.01] = np.nan
    panels = []
    for _ in range(N_COL):
        p = pd.DataFrame(rng.normal(0, 1.0, (N_DAY, N_TICK)), index=idx, columns=cols)
        p[rng.random(p.shape) < 0.03] = np.nan
        panels.append(p)
    return panels, ret


def main() -> int:
    panels, ret = build()
    ref = fast_rank_ic(panels[0], ret)
    got = rank_ic(panels[0], ret, xp="numpy")
    delta = float((ref - got).abs().max()) if len(ref) else 0.0
    assert delta < TOL, f"bench 规模对拍失败 max|dIC|={delta:.3e}"
    print(f"preflight parity @bench scale: max|dIC|={delta:.3e}")

    rank_ic(panels[0], ret, xp="numpy")  # warmup（首次 import/分配不计时）
    totals = []
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        for p in panels:
            rank_ic(p, ret, xp="numpy")
        totals.append(time.perf_counter() - t0)
    best = min(totals)

    t0 = time.perf_counter()  # 参照：原版 fast_rank_ic（pandas）同机同规模，取 3 列均值
    for p in panels[:3]:
        fast_rank_ic(p, ret)
    ref_per_col = (time.perf_counter() - t0) / 3

    print(f"scale={N_TICK}tick x {N_DAY}day x {N_COL}col backend=numpy dtype=float64")
    print(
        f"rank_ic_numpy: best_total={best:.3f}s  per_col={best / N_COL * 1000:.1f}ms  repeats={[f'{t:.3f}' for t in totals]}"
    )
    print(f"fast_rank_ic_ref(pandas): per_col={ref_per_col * 1000:.1f}ms (3 列均值)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
