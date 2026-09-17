# [MODULE] tests.backtest.test_b1_fact_assemble_samebar_probe
# [DOMAIN] D_BACKTEST
# [TESTS] self
# [TTL] permanent
"""B1 前视探针（S14 战场）：factor_strategy_template.assemble_weights 同 bar stamping。

考卷族（c4_fact_*.py，6 件）权重由本函数统一承载：weights.loc[d] 用 d 当日
factor 截面排名选出（factor 特征含 close[d]/amount[d]/turnover[d]，见
lane_c_formula_miner.FEATURES），引擎 w.shift(1) 后等价「看着 d 收盘按 d 收盘
成交」——与模块 INVARIANTS 自述「T+1 收盘执行」矛盾（实际=信号日收盘成交）。

不变式：weights.loc[X] 只许依赖 ≤X-1 的 factor；只改 X 日 factor 排名，
X 日（及之前）权重必须逐位不变。红=同 bar 实锤；绿=已修复。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "backtest"))

import factor_strategy_template as fst  # noqa: E402

_DATES = pd.bdate_range("2023-03-01", periods=10)
_X = _DATES[5]
_SYMS = ["s1", "s2", "s3", "s4"]


def _feats(x_day_flip: bool) -> pd.DataFrame:
    rows = []
    for d in _DATES:
        for i, s in enumerate(_SYMS):
            # 常设排名 s1>s2>s3>s4；X 日 flip 变体改为 s4 居首
            f = (4 - i) * 1.0
            if x_day_flip and d == _X:
                f = (10.0 if s == "s4" else 4 - i)
            rows.append((d, s, 10.0, f))
    return pd.DataFrame(rows, columns=["date", "s", "close", "factor"])


@pytest.mark.xfail(strict=True, reason="B1-V3 实锤未修：assemble_weights 缺 ≤T-1 平移（修复后 XPASS-strict 自动报警）")
def test_assemble_weights_at_x_must_not_use_day_x_factor():
    w_a, _ = fst.assemble_weights(_feats(False), top_n=2)
    w_b, _ = fst.assemble_weights(_feats(True), top_n=2)
    # 非空检验：X 日两变体都必须有持仓
    assert float(w_a.loc[_X].sum()) > 0 and float(w_b.loc[_X].sum()) > 0, "探针空转"
    assert w_a.loc[:_X].equals(w_b.loc[:_X]), (
        "同 bar 前视实锤：X 日权重被 X 日 factor 截面改写"
        "（assemble_weights 未做 ≤T-1 平移，引擎单格 shift 不足以覆盖）"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
