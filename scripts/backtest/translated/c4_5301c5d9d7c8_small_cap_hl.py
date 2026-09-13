# [BLUEPRINT] MOD-BT-130 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_5301c5d9d7c8_small_cap_hl
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（信号 ≤T-1）；成本=冻结土规；风控状态机不可逐日独立判定
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-130 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 095: 小市值高收益低回撤（原文: 2025年度精选策略/47 高收益低回撤的小市值策略）。

原文: 每日 14:40：中小板综(399101) 成分、流通市值<100 亿→按流通市值升序前 10→剔 ST/停牌/涨跌停→
  前 5 等权；风控=000300 收盘/MA1000 比率带滞回双状态机（NORMAL→WARNING: >2.5 或 <0.30；
  WARNING→NORMAL: 0.35~0.7；WARNING 需 RSI60∈(47,99) 才可交易），风控不过→清仓不买。
译文实现: 流通市值=circ_mv（万元/1e4=亿）；MA1000=300 收盘千日均线（kline_index 2015 起 1200 天）；
  滞回状态机保留。
因子拆解: 市值排序——规模因子，不登记。
翻译差异声明:
  D1 池: 中小板综→全 A 近似; D2 14:40→T+1 收盘; D3 市值<100 亿=circ_mv/1e4<100; D4 不登记; D5 壳不译
"""

from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
from _c4_engine import (emit, filter_st, load_index, load_px, load_st_flags,
                        load_valuation, run_backtest, wide)

logger = logging.getLogger(__name__)
STRATEGY_ID = "CAND-5301c5d9d7c8"
WINDOW_KIND = "stock"
_TOP, _CAND, _MC_LIM = 5, 10, 100.0


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = "2015-01-01"
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    val = load_valuation(load_start, end, fields=("circ_mv",))
    cmv = (val["circ_mv"] / 1e4).reindex(closes.index).reindex(columns=closes.columns)
    idx = load_index("000300", load_start, end, fields=("close",))["close"]
    ma1000 = idx.rolling(1000, min_periods=600).mean()
    ma_rate = idx / ma1000
    # RSI60 on 000300
    delta = idx.diff()
    gain = delta.clip(lower=0).rolling(60).mean()
    loss = (-delta.clip(upper=0)).rolling(60).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    # 滞回状态机
    state = pd.Series("NORMAL", index=idx.index)
    for i in range(1, len(state)):
        r = ma_rate.iloc[i]
        prev = state.iloc[i - 1]
        if prev == "NORMAL" and (r > 2.5 or r < 0.30):
            state.iloc[i] = "WARNING"
        elif prev == "WARNING" and 0.35 <= r <= 0.7:
            state.iloc[i] = "NORMAL"
        else:
            state.iloc[i] = prev
    can_trade = ~((state == "WARNING") & ~((rsi > 47) & (rsi < 99)))

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    for k, dt in enumerate(dates):
        if dt not in can_trade.index or not can_trade.loc[dt]:
            continue
        row_mv = cmv.shift(1).iloc[k].dropna()
        small = row_mv[row_mv < _MC_LIM]
        if len(small) < _TOP:
            continue
        cand = list(small.sort_values().index[:_CAND])
        picks = cand[:_TOP]
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 中小板→全A", "D2 T+1收盘", "D3 市值亿",
        "D4 不登记", "D5 壳不译"]), ensure_ascii=False))
