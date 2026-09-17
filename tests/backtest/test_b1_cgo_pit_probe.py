# [MODULE] tests.backtest.test_b1_cgo_pit_probe
# [DOMAIN] D_BACKTEST
# [TESTS] self
# [TTL] permanent
"""B1 前视探针（S14 战场）：c4_14d3e787ea4b_cgo_factor 生存乘积含未来换手率。

不变式：决策日 d ≤ X 的权重只许依赖 ≤ d-1 的数据——把 X 之后**一半标的**的
换手率改写（另一半不变），d ≤ X 的选股结果必须逐位不变。当前实现
surv[i]=∏_{j>i..窗末}(1-TR_j)（cgo_factor.py:66，生存乘积滚到窗口终点而非
t-1），参考价 rp[t] 因此携带 t 之后的换手率路径，本探针必然红。

红=实锤前视；绿=已修复（届时本探针转为回归守卫）。
纯合成数据，不连 CH（monkeypatch 数据腿）。12 标的 > _TOP_N=10，排名须真实竞争。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "backtest" / "translated"))

import c4_14d3e787ea4b_cgo_factor as cgo_mod  # noqa: E402

_DATES = pd.bdate_range("2022-01-03", periods=300)
_START = _DATES[160].strftime("%Y-%m-%d")
_END = _DATES[299].strftime("%Y-%m-%d")
_X = _DATES[230]  # 污染分界线：>X 的行才被改写
_SYMS = [f"{k:06d}" for k in range(12)]
_FLIPPED = set(_SYMS[6:])  # 仅后 6 只在 X 之后被改写换手率


def _fake_px(turnover_after_x: float):
    rows = []
    for i, d in enumerate(_DATES):
        for k, s in enumerate(_SYMS):
            close = 10.0 + 0.01 * i + 0.002 * k * i  # 逐标的斜率不同→cgo 排名敏感
            to = 5.0
            if d > _X and s in _FLIPPED:
                to = turnover_after_x
            rows.append((d, s, close, close * 1e5, 1e5, to))

    def _load(start, end, fields=("close",)):
        df = pd.DataFrame(rows, columns=["trade_date", "symbol", "close", "amount", "volume", "turnover"])
        return df[(df["trade_date"] >= pd.Timestamp(start)) & (df["trade_date"] <= pd.Timestamp(end))]

    return _load


def _build_with(turnover_after_x: float) -> pd.DataFrame:
    cgo_mod.load_px = _fake_px(turnover_after_x)
    cgo_mod.load_st_flags = lambda s, e: pd.DataFrame(columns=["trade_date", "symbol", "st_flag"])
    weights, _close = cgo_mod.build(_START, _END)
    return weights


def test_cgo_weights_before_x_must_not_depend_on_data_after_x():
    w_a = _build_with(5.0)    # 基线：全窗换手率不变
    w_b = _build_with(40.0)   # 只改 X 之后、且只改一半标的的换手率
    pre_a, pre_b = w_a.loc[:_X], w_b.loc[:_X]
    # 非空检验（防探针空转绿）：X 前必须有持仓、且存在落选标的（排名竞争真实）
    assert float(pre_a.sum().sum()) > 0.0, "探针空转：X 前无任何权重"
    assert (pre_a.sum(axis=1) == 0).any() or (pre_a.iloc[:, :] > 0).sum(axis=1).le(10).all()
    assert pre_a.equals(pre_b), (
        "PIT 违规实锤：决策日 ≤ %s 的选股被该日之后的换手率改写"
        "（cgo 生存乘积 ∏_{j>i} 跑到了窗口终点，c4_14d3e787ea4b_cgo_factor.py:66）" % _X.date()
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
