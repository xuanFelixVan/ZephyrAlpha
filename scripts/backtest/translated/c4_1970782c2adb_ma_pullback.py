# [BLUEPRINT] MOD-BT-062 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_1970782c2adb_ma_pullback
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
# [A_module] module_id=MOD-BT-062 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 062: 回踩均线搏反弹（原文: 2023年度精选策略/70 回踩均线搏反弹 测试第一弹）。

原文逻辑: 池=全 A 换手率 3%~10% 按换手降序，剔 688/上市<365 交易日/ST/退；
  条件（260 日窗）: 近 6 日中 MA21>MA55 至少 5 日 且 MA55>MA120 至少 5 日 且
  close>MA55 至少 5 日（比较含 2% 容差）；前日收阴 且 前日 close<=MA55（回踩）；
  昨日 close>MA55（拉升）且 MA55 上行。评分=box-array 升序取前 3 等权。
译文实现: 换手率用 kline turnover 字段；box=逐日(MA13,MA21,MA55) 三元组对其中位数的
  相对偏差平方和（近 20 日跳过最近 2 日求和）；array=近 5 日均线多头排列天数（简化，D3）；
  信号 T-1，T 收盘执行。
因子拆解: MA21/55/120 排列+回踩形态——价格衍生，不入 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表内）+换手过滤+次新近似（次新过滤按数据可得性降级）
  D2 执行时点: 原文 9:30 开盘 → T+1 收盘成交
  D3 评分: array 项取多头排列天数（原文为含幅度的排列强度比率，方向一致幅度近似）
  D4 因子登记: 均线形态不入 factor_registry
  D5 框架样板: log 壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-1970782c2adb"
WINDOW_KIND = "stock"
_TO_MIN, _TO_MAX = 3.0, 10.0
_TOP_N = 3


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=420))[:10]
    px = load_px(load_start, end, fields=("close", "open", "turnover"))
    close = wide(px, "close").ffill()
    opn = wide(px, "open").ffill().reindex(close.index)
    to = wide(px, "turnover").ffill().reindex(close.index)
    close = filter_st(close, load_st_flags(load_start, end))
    opn = opn.reindex(columns=close.columns)
    to = to.reindex(columns=close.columns)

    ma13, ma21, ma55, ma120 = (close.rolling(n).mean() for n in (13, 21, 55, 120))

    cnt_2155 = (ma21 > ma55 * 0.98).rolling(6).sum()
    cnt_55120 = (ma55 > ma120 * 0.98).rolling(6).sum()
    cnt_c55 = (close > ma55 * 0.98).rolling(6).sum()
    base_ok = (cnt_2155 >= 5) & (cnt_55120 >= 5) & (cnt_c55 >= 5)
    yin = close.shift(1) <= opn.shift(1)
    pullback = close.shift(1) <= ma55.shift(1)
    lift = close > ma55
    ma55_up = ma55 >= ma55.shift(1)
    sig = base_ok & yin & pullback & lift & ma55_up & (to > _TO_MIN) & (to <= _TO_MAX)

    tri = np.stack([ma13.values, ma21.values, ma55.values], axis=0)  # (3, t, c)
    med = np.median(tri, axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        box_day = np.square((tri - med) / med).mean(axis=0)
    box_day = pd.DataFrame(box_day, index=close.index, columns=close.columns)
    box = box_day.shift(2).rolling(20).sum()          # 近 20 日、跳过最近 2 日
    array = ((ma13 > ma21) & (ma21 > ma55)).astype(float).rolling(5).sum()
    score = box - array

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    s_idx = sig.shift(1).reindex(dates).fillna(False)
    sc_idx = score.shift(1).reindex(dates)
    for k, dt in enumerate(dates):
        row = s_idx.iloc[k] & sc_idx.iloc[k].gt(0).fillna(False)
        if not bool(row.any()):
            continue
        picks = list(sc_idx.iloc[k][row].sort_values().index)[:_TOP_N]
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A+换手过滤", "D2 T+1收盘", "D3 array评分近似",
                                               "D4 均线形态不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
