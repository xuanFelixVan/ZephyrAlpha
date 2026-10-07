# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | IC核对拍测试（逐位0差五用例）
# [MODULE] scripts.backtest.fexam.gpu_ic.parity_test.py
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
"""parity_test — rank_ic(numpy 后端) vs ic_exam.fast_rank_ic 逐位对拍。

今晚只跑 numpy 后端（GPU 被 st-t3series 车道占用——vram 独占纪律；cupy 冒烟走
smoke_gpu.py，quiet 窗口执行）。通过线：每例 max|dIC| < 1e-9，且 dropna 后有效日
索引集合完全一致（NaN 模式逐位同）。用例覆盖三类边角 + 2 列真实指标（ch_data）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[3]  # .../.runtime/tmp/st-matrix-20261006/gpu_ic → ZephyrAlpha
for _p in (str(_ROOT / "src"), str(_ROOT / "scripts" / "backtest" / "fexam"), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ch_data  # noqa: E402
from gpu_rank_ic import rank_ic  # noqa: E402
from ic_exam import fast_rank_ic  # noqa: E402

TOL = 1e-9

#: 真实小样本：roster 指标批机生解析出的 2 列 ch_backed 真实指标（c1_market.technical_indicator）
_REAL_PICKS = (
    (ch_data.T_TECHNICAL_INDICATOR, "md_14"),
    (ch_data.T_TECHNICAL_INDICATOR, "bbi"),
)


def _parity(panel: pd.DataFrame, ret: pd.DataFrame, label: str, backend: str) -> tuple[str, float]:
    ref = fast_rank_ic(panel, ret)
    got = rank_ic(panel, ret, xp=backend)
    if not ref.index.equals(got.index):
        only_ref = len(ref.index.difference(got.index))
        only_got = len(got.index.difference(ref.index))
        raise AssertionError(
            f"[{label}] 有效日集合不一致: ref={len(ref)}(仅ref+{only_ref}) got={len(got)}(仅got+{only_got})"
        )
    delta = float((ref - got).abs().max()) if len(ref) else 0.0
    if not delta < TOL:
        raise AssertionError(f"[{label}] max|dIC|={delta:.3e} >= {TOL:.0e}")
    print(f"  PASS {label}: backend={backend} n_days={len(ref)} max|dIC|={delta:.3e}")
    return label, delta


def _base_pair(seed: int, n_days: int = 260, n_sym: int = 40, skill: float = 0.3):
    """合成面板：因子含真实技能（IC 量级接近真实指标），ret=前向关联+噪声。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2025-01-01", periods=n_days)
    cols = [f"S{i:03d}" for i in range(n_sym)]
    panel = pd.DataFrame(rng.normal(size=(n_days, n_sym)), index=idx, columns=cols)
    ret = panel.shift(-5) * skill + pd.DataFrame(rng.normal(0, 1.2, (n_days, n_sym)), index=idx, columns=cols)
    return panel, ret


def case_nan_sprinkle(backend: str) -> tuple[str, float]:
    """边角1：双侧随机撒 NaN（覆盖联合掩码裁剪路径）。"""
    panel, ret = _base_pair(11)
    rng = np.random.default_rng(12)
    panel[rng.random(panel.shape) < 0.08] = np.nan
    ret[rng.random(ret.shape) < 0.05] = np.nan
    return _parity(panel, ret, "synth:nan_sprinkle", backend)


def case_short_rows(backend: str) -> tuple[str, float]:
    """边角2：有效对不足 30 的行（<30 → 双侧 NaN；恰 30 → 有效，边界两侧都要踩）。"""
    panel, ret = _base_pair(23)
    ret.iloc[50:66, 12:] = np.nan  # 12 个有效对 → 该 16 日双侧 NaN
    ret.iloc[70, 29:] = np.nan  # 恰 29 对 → NaN（<30 侧）
    ret.iloc[71, 30:] = np.nan  # 恰 30 对 → 有效（=30 侧）
    label, delta = _parity(panel, ret, "synth:short_rows", backend)
    ref = fast_rank_ic(panel, ret)
    idx = panel.index
    assert idx[70] not in ref.index, "29 对日应为 NaN（不在输出内）"
    assert idx[71] in ref.index, "30 对日应为有效"
    assert not any(idx[i] in ref.index for i in range(50, 66)), "12 对日应全为 NaN"
    return label, delta


def case_constant(backend: str) -> tuple[str, float]:
    """边角3：常数列 / 整行常数（denom=0 → NaN）/ 整行缺失。"""
    panel, ret = _base_pair(37)
    panel.iloc[:, 0] = 7.0  # 常数列（并列秩→中心化后 0，仅降自由度不改变余列 IC）
    panel.iloc[10, :] = 3.3  # 整行常数 → denom_f=0 → 该日 NaN
    panel.iloc[11, :] = np.nan  # 整行缺失 → 该日 NaN
    ret.iloc[:, 5] = 2.0  # ret 侧常数列
    return _parity(panel, ret, "synth:constant", backend)


def real_cases(backend: str) -> list[tuple[str, float]]:
    """真实小样本：ch_data 拉 2 列真实指标 × 5 日前向收益（WINDOW_UNION 全窗）。"""
    out: list[tuple[str, float]] = []
    close = ch_data.load_close(*ch_data.WINDOW_UNION)
    ret5 = ch_data.forward_returns(close, (5,))[5]
    for table, column in _REAL_PICKS:
        panel = ch_data.load_panel(table, column, *ch_data.WINDOW_UNION)
        panel = panel.dropna(how="all").dropna(axis=1, how="all")
        if panel.empty:
            raise RuntimeError(f"real:{column} CH 窗内空面板（fail-closed，禁伪造空数据冒充对拍）")
        out.append(_parity(panel, ret5, f"real:{column}", backend))
    return out


def run_all_cases(backend: str = "numpy") -> list[tuple[str, float]]:
    """全量对拍用例。backend 传给 rank_ic：numpy=今晚；cupy=smoke_gpu.py（quiet 窗口）。"""
    results = [case_nan_sprinkle(backend), case_short_rows(backend), case_constant(backend)]
    results.extend(real_cases(backend))
    return results


if __name__ == "__main__":
    res = run_all_cases("numpy")
    worst = max(d for _, d in res)
    print(f"PARITY-OK backend=numpy cases={len(res)} worst|dIC|={worst:.3e} tol={TOL:.0e}")
