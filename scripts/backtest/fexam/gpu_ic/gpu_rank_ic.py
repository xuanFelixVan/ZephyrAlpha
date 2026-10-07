# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | IC核GPU移植numpy/cupy双后端（逐位0差对拍）
# [MODULE] scripts.backtest.fexam.gpu_ic.gpu_rank_ic.py
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
"""gpu_rank_ic — fast_rank_ic（scripts/backtest/fexam/ic_exam.py）的 xp 双后端同构移植。

数学（与 fast_rank_ic 逐位同构，对拍锁 max|dIC|<1e-9，见 parity_test.py）：
  1. 联合有效掩码先裁剪：panel/ret 任一 NaN → 双侧同置 NaN（防"先各自秩变换"的分母集偏）
  2. 行内 pct 秩变换：average 法并列均值 / 行有效数（= pandas rank(axis=1, pct=True)）
  3. 行内标准化（去行均值）→ IC = sum(zf*zr) / (||zf||*||zr||)，denom=0 → NaN
  4. 行有效对 <30 → 该日 NaN；返回 dropna 后逐日 IC Series（name="ic"，index=联合日期）

后端：xp="numpy"（默认，今晚真跑）| xp="cupy"（代码就绪，今晚【不】执行——GPU 被
st-t3series 车道占用，vram 独占纪律；cupy 走函数内懒加载，numpy 通道零 GPU 触碰）。
禁碰交易引擎（vectorized_engine）；本内核仅供评估侧（fexam）替换演练。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: 行有效对下限（对齐 fast_rank_ic 的 valid<30 置 NaN）
MIN_OBS = 30


def _resolve_xp(name: str):
    """后端解析。cupy 懒加载：仅显式 xp="cupy" 时才 import（防误触 GPU 的唯一入口）。"""
    if name == "numpy":
        return np
    if name == "cupy":
        import cupy  # 懒加载——本行只在调用方显式请求 cupy 后端时执行

        return cupy
    raise ValueError(f"未知 xp 后端: {name!r}（可选 numpy|cupy）")


def _row_rank_pct(xp, a, n):
    """行内 pct 秩（float64）：average 法并列秩 / 行有效数。

    实现：双稳定 argsort 定序 → 排序轴上按"与前值相等"切并列组 → 组起点/组终点
    各散射一次（每列恰一次写；非组界统一写哨兵列且同值，无写序歧义）→
    平均秩=(组起点+组终点)/2（连续整数组均值，与 sum/count 同一有理数的同一舍入）。
    NaN 排序在末且 NaN!=NaN 自成组，最后统一置 NaN。
    """
    rows, cols = a.shape
    order = xp.argsort(a, axis=1, kind="stable")
    srt = xp.take_along_axis(a, order, axis=1)
    same = srt[:, 1:] == srt[:, :-1]  # (rows, cols-1)；NaN!=NaN → False
    is_start = xp.concatenate([xp.ones((rows, 1), dtype=bool), ~same], axis=1)
    is_end = xp.concatenate([~same, xp.ones((rows, 1), dtype=bool)], axis=1)
    gid = xp.cumsum(is_start.astype(np.int64), axis=1) - 1  # (rows, cols) 组 id
    pos = xp.arange(1, cols + 1, dtype=np.float64)[None, :]
    sentinel = cols  # 哨兵列：非组界写入目标（值恒 0.0，多次写无歧义）
    starts = xp.full((rows, cols + 1), np.nan, dtype=np.float64)
    xp.put_along_axis(starts, xp.where(is_start, gid, sentinel), xp.where(is_start, pos, 0.0), axis=1)
    ends = xp.full((rows, cols + 1), np.nan, dtype=np.float64)
    xp.put_along_axis(ends, xp.where(is_end, gid, sentinel), xp.where(is_end, pos, 0.0), axis=1)
    avg = (xp.take_along_axis(starts, gid, axis=1) + xp.take_along_axis(ends, gid, axis=1)) / 2.0
    avg = xp.where(xp.isnan(srt), np.nan, avg)  # NaN 位秩=NaN
    ranks = xp.empty((rows, cols), dtype=np.float64)
    xp.put_along_axis(ranks, order, avg, axis=1)  # order 是置换，列索引唯一
    return ranks / xp.where(n > 0, n, 1).astype(np.float64)[:, None]


def rank_ic(panel: pd.DataFrame, ret: pd.DataFrame, xp: str = "numpy", min_obs: int = MIN_OBS) -> pd.Series:
    """向量秩 IC 双后端内核（fast_rank_ic 的 xp 同构；DataFrame 入，逐日 IC Series 出）。"""
    xpm = _resolve_xp(xp)
    common_cols = panel.columns.intersection(ret.columns)
    if len(common_cols) == 0:
        return pd.Series(dtype="float64", name="ic")
    common_idx = panel.index.intersection(ret.index)
    f_all = panel[common_cols].loc[common_idx]
    r_all = ret[common_cols].loc[common_idx]
    mask = (f_all.notna() & r_all.notna()).to_numpy()  # 联合有效掩码先裁剪（同构关键步）
    f_all = f_all.where(mask)
    r_all = r_all.where(mask)
    f_dev = xpm.asarray(f_all.to_numpy(dtype=np.float64))
    r_dev = xpm.asarray(r_all.to_numpy(dtype=np.float64))
    n_dev = xpm.asarray(mask.sum(axis=1))  # 行有效对数（host 计数，随掩码一致）

    f_pct = _row_rank_pct(xpm, f_dev, n_dev)
    r_pct = _row_rank_pct(xpm, r_dev, n_dev)
    zf = _row_center(xpm, f_pct, n_dev)
    zr = _row_center(xpm, r_pct, n_dev)
    denom_f = _row_norm(xpm, zf)
    denom_r = _row_norm(xpm, zr)
    ic = xpm.nansum(zf * zr, axis=1) / (denom_f * denom_r)
    ic = xpm.where(n_dev >= min_obs, ic, xpm.nan)
    ic_host = np.asarray(ic, dtype=np.float64)  # cupy 路经 __array__ 拉回 host
    return pd.Series(ic_host, index=common_idx, name="ic").dropna()


def _row_center(xp, pct, n):
    """行内去均值（skipna 同义：sum(有效)/有效数=n；全 NaN 行除数护栏为 1，结果仍全 NaN）。"""
    mean = xp.nansum(pct, axis=1) / xp.where(n > 0, n, 1).astype(np.float64)
    return pct - mean[:, None]


def _row_norm(xp, z):
    """行向量模长：sqrt(sum(z^2))，0 → NaN（对齐 .replace(0.0, np.nan)）。"""
    d = xp.sqrt(xp.nansum(z * z, axis=1))
    return xp.where(d == 0.0, np.nan, d)
