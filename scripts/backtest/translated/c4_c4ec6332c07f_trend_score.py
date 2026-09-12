# [BLUEPRINT] MOD-BT-070 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_c4ec6332c07f_trend_score
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-070 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 070: 趋与势量化定义——势分分位带择时（原文: 2023年度精选策略/80 趋与势的量化定义）。

原文逻辑: 标的 000300；score=close.rolling(60).apply(势分)——60 日窗内对
  normalize_compound(5)（0.5×(sign(ret)+sign(close-MA5)) 累计归一序列）取"absolute"势分
  （极值点标记序列的位移平方和，首尾极值时用 (尾-首)²，除以 (N-1)^1.5，同作者 82.势的度量 定义）；
  upper=score 的 20 日 85% 分位、lower=5% 分位；previous_score<previous_upper 且
  score>=upper → 持有；previous_score>previous_lower 且 score<=lower → 清仓；否则延续。
译文实现: 势分按 82 篇公式重实现（rolling 60 逐窗计算，性能可接受）；信号 T-1，T 收盘执行。
因子拆解: 势分（归一化序列拐点位移）——价格衍生，不入 factor_registry。
翻译差异声明:
  D1 标的: 000300 一致（指数收益模拟）
  D2 执行时点: 原文收盘信号当日生效 → T 日收盘（引擎 T+1 起算）
  D3 势分实现: 依同作者 82.势的度量 公式重实现（原 notebook 类管线不可直接 import）
  D4 因子登记: 势分不入 factor_registry
  D5 框架样板: 绘图壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import emit, load_index, run_backtest

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-c4ec6332c07f"
WINDOW_KIND = "index"
_SCORE_WIN, _Q_WIN, _UP, _LOW = 60, 20, 0.85, 0.05


def _trend_score(win: np.ndarray) -> float:
    s = pd.Series(win)
    ret_sign = np.sign(s.diff()).fillna(0.0)
    ma5_sign = np.sign(s - s.rolling(5).mean()).fillna(0.0)
    compound = ((ret_sign + ma5_sign) / 2.0).cumsum()
    x = compound.values
    n = len(x)
    if n < 3:
        return 0.0
    # 拐点标记（局部极大/极小 + 首尾）
    marks = [0]
    for i in range(1, n - 1):
        if (x[i] >= x[i - 1] and x[i] > x[i + 1]) or (x[i] <= x[i - 1] and x[i] < x[i + 1]):
            marks.append(i)
    marks.append(n - 1)
    pts = x[marks]
    imax, imin = int(np.argmax(x)), int(np.argmin(x))
    if imax in (0, n - 1) or imin in (0, n - 1):
        trend = float((x[-1] - x[0]) ** 2)
    else:
        trend = float(np.square(np.diff(pts)).sum())
    return trend / ((n - 1) ** 1.5)


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=int((_SCORE_WIN + _Q_WIN) * 3)))[:10]
    idx = load_index("000300", load_start, end, fields=("close",))
    c = idx["close"]
    score = c.rolling(_SCORE_WIN).apply(lambda m: _trend_score(np.asarray(m)), raw=True)
    upper = score.rolling(_Q_WIN).quantile(_UP)
    lower = score.rolling(_Q_WIN).quantile(_LOW)
    dates = idx.index[(idx.index >= pd.Timestamp(start)) & (idx.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    pos, prev_s, prev_u, prev_l = 0.0, None, None, None
    for dt in dates:
        s, u, l = score.shift(1).loc[dt], upper.shift(1).loc[dt], lower.shift(1).loc[dt]
        if pd.notna(s) and prev_s is not None:
            if prev_s > prev_l and s <= l:
                pos = 0.0
            elif prev_s < prev_u and s >= u:
                pos = 1.0
        if pd.notna(s):
            prev_s, prev_u, prev_l = float(s), float(u) if pd.notna(u) else prev_u, float(l) if pd.notna(l) else prev_l
        weights.loc[dt, "000300"] = pos
    closes = idx[["close"]].rename(columns={"close": "000300"})
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 指数一致", "D2 收盘口径", "D3 势分重实现",
                                               "D4 不入库", "D5 绘图壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
