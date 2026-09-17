# [MODULE] tests.backtest.test_b1_gftd_samebar_probe
# [DOMAIN] D_BACKTEST
# [TESTS] self
# [TTL] permanent
"""B1 前视探针（S14 战场）：c4_b37f550ba2af_gftd 同 bar 信号 stamping。

_c4_engine 约定「T 日信号用 ≤T-1 数据」（引擎 w.shift(1) 只供一格执行滞后）。
gftd 的 signal[dt] 用 closes/highs/lows 的 dt 当日值判定（win/c/h 切片含 t），
权重盖在 dt 当日 → 引擎 shift(1) 后等价「看着 dt 收盘按 dt 收盘成交」=同 bar 前视。

探针构造：第 41 日（X）variant A 收 10.35 触发第 4 次买入计数（signal[X]=1），
variant B 收 10.00 不触发。两数据集仅在 X 日 close/high/low 不同。
不变式：weights.loc[:X] 必须逐位相同（X 日权重只许依赖 ≤X-1）。
红=同 bar 实锤；绿=已修复。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "backtest" / "translated"))

import c4_b37f550ba2af_gftd as gftd_mod  # noqa: E402

_N = 60
_DATES = pd.bdate_range("2023-01-02", periods=_N)
_X = _DATES[41]
_START = _DATES[35].strftime("%Y-%m-%d")
_END = _DATES[-1].strftime("%Y-%m-%d")


def _closes(day41: float) -> list[float]:
    c = [10.0 + 0.01 * t for t in range(30)]                    # 0-29 缓升（状态机保持 empty）
    c += [10.30, 10.22, 10.14, 10.06, 9.98, 9.90, 9.82, 9.74]   # 30-37 八连阴触发 buy_count
    c += [10.05, 10.15, 10.25]                                  # 38-40 三连阳 buy_cnt→3
    c.append(day41)                                             # 41=X：触发日
    c += [day41] * (_N - 42)                                    # 尾部持平
    return c


def _build_with(day41: float) -> pd.DataFrame:
    c = _closes(day41)
    idx = pd.DataFrame({
        "close": c,
        "high": [v * 1.01 for v in c],
        "low": [v * 0.99 for v in c],
    }, index=_DATES)
    gftd_mod.load_index = lambda symbol, start, end, fields=("close",): idx
    weights, _closes_w = gftd_mod.build(_START, _END)
    return weights


@pytest.mark.xfail(strict=True, reason="B1-V2 实锤未修：gftd 同 bar 前视（修复后 XPASS-strict 自动报警）")
def test_gftd_signal_at_x_must_not_use_day_x_bar():
    w_a = _build_with(10.35)
    w_b = _build_with(10.00)
    # 非空检验：variant A 在 X 日必须真的触发买入（否则探针空转）
    assert float(w_a.loc[_X].iloc[0]) == 1.0, "探针构造失败：A 在 X 日未触发买入"
    assert w_a.loc[:_X].equals(w_b.loc[:_X]), (
        "同 bar 前视实锤：X 日权重被 X 日 close/high/low 改写"
        "（signal[dt] 用当日 bar 判定，引擎 shift(1) 后=看着收盘价按收盘价成交）"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
