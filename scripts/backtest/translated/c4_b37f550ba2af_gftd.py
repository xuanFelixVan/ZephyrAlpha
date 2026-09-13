# [BLUEPRINT] MOD-BT-043 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_b37f550ba2af_gftd
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号）；成本=冻结土规；状态机与原文逐条对应
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-043 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 043: GFTD 指标择时（原文: 2020年度精选策略/78 GFTD第二版，标的=沪深300 指数）。

原文逻辑（TD-序列变体，n1=n2=n3=4, count_lag=2）:
  买入启动: 连续 4 日 close[i+4]<=close[i]（含当日共 8 日窗口）→ 进入买入计数；
  买入计数: close>=3日前high 且 high>昨日high 且 close>计数保存价 → 计数+1；计满 4 → 全仓买入；
  卖出侧镜像（close[i+4]>=close[i] 启动，close<=3日前low 且 low<昨日low 且 close<保存价 计数）；
  计满 4 → 清仓。交易对象 000300 指数（原文以指数直接成交，实为指数择时）。
译文实现: kline_index 000300 日线，状态机逐日推进，信号 T-1 确认 T 收盘执行。
因子拆解: GFTD（收盘价 4 日比较启动+计数突破）——纯价格形态计数，不入 factor_registry。
翻译差异声明:
  D1 标的: 原文指数直接下单（聚宽指数可交易近似）→ 译文以指数收益模拟（无对应 ETF 映射声明）
  D2 执行时点: 原文 handle_data 当日收盘价 → T 日收盘（同口径）
  D3 止损线: 原文 g.line 止损在注释块未启用 → 不翻译（只保留计数推进）
  D4 因子登记: GFTD 计数不入 factor_registry
  D5 手续费: 原文单笔 0.2% 双边 → 冻结土规（2.5bp+10bp+5bp）

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, load_index, run_backtest

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-b37f550ba2af"
WINDOW_KIND = "index"
_N1 = _N2 = _N3 = 4


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    idx = load_index("000300", load_start, end, fields=("close", "high", "low"))
    closes, highs, lows = idx["close"], idx["high"], idx["low"]
    n = len(closes)
    state, buy_cnt, sell_cnt = "empty", 0, 0
    save, line = 0.0, 0.0
    signal: dict[pd.Timestamp, float] = {}
    for t in range(_N1 + _N2, n):
        # 启动计数用 [t-7, t] 窗口（信号次日生效：t+1 执行）
        win = closes.iloc[t - _N1 - _N2 + 1: t + 1].values
        dt_sig = closes.index[t]
        if state in ("empty", "buy_count"):
            bi = sum(1 for i in range(_N2) if win[i + _N1] <= win[i])
            if bi == _N2 and state != "buy_count":
                state, save, buy_cnt = "buy_count", float(win[-1]), 0
                line = float(lows.iloc[t])
        if state == "buy_count":
            c = closes.iloc[t - 2: t + 1].values
            h = highs.iloc[t - 2: t + 1].values
            if c[-1] >= h[0] and h[-1] > h[-2] and c[-1] > save:
                save = float(c[-1])
                buy_cnt += 1
                line = min(line, float(lows.iloc[t]))
            if buy_cnt == _N3:
                signal[dt_sig] = 1.0
                state, buy_cnt = "full", 0
        if state in ("full", "sell_count"):
            win = closes.iloc[t - _N1 - _N2 + 1: t + 1].values
            si = sum(1 for i in range(_N2) if win[i + _N1] >= win[i])
            if si == _N2 and state != "sell_count":
                state, save, sell_cnt = "sell_count", float(win[-1]), 0
                line = float(highs.iloc[t])
        if state == "sell_count":
            c = closes.iloc[t - 2: t + 1].values
            l = lows.iloc[t - 2: t + 1].values
            if c[-1] <= l[0] and l[-1] < l[-2] and c[-1] < save:
                save = float(c[-1])
                sell_cnt += 1
                line = max(line, float(highs.iloc[t]))
            if sell_cnt == _N3:
                signal[dt_sig] = 0.0
                state, sell_cnt = "empty", 0
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    pos = 0.0
    for dt in dates:
        if dt in signal:
            pos = signal[dt]
        weights.loc[dt, "000300"] = pos
    closes_w = closes.to_frame(name="000300")
    return weights, closes_w


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 指数收益模拟", "D2 收盘口径", "D3 未启用止损不译",
                                               "D4 计数不入库", "D5 冻结成本"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
