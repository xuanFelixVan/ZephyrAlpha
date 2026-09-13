# [BLUEPRINT] MOD-BT-073 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_fdbc279fba99_rps_oinl
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
# [A_module] module_id=MOD-BT-073 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 073: 欧奈尔 RPS 相对强度选股（原文: 2025年度精选策略/91 欧奈尔 RPS选股战法回测）。

原文逻辑: 池=沪深300；每日对池内取 120 日收盘涨幅，剔除涨幅>50% 者；按涨幅降序排名
  rps=(1-rank/N)×100；rps>=85 者取前 10 只为候选；持仓≤5 只（剩余槽位均分现金）；
  卖出=90 日涨幅<30% 且 收盘<100 日均线（wizard 函数名语义，UNCERTAIN 已声明）。
译文实现: 全规则日线向量化；候选按排名序取前 5 等权（槽位语义：持仓不足 5 时买入，
  卖出条件独立触发）；信号 T-1，T 收盘执行。
因子拆解: 120 日相对价格强度 RPS——动量因子（公开方法论），不登记 factor_registry。
翻译差异声明:
  D1 股票池: 沪深300 成分快照
  D2 执行时点: 原文 14:25 → T+1 收盘成交
  D3 卖出规则: n_day_chg_xiaoyu/situation_filter_xiaoyu_ma 为 wizard 库函数（源不在文件内），
     按函数名+参数语义实现（90 日涨幅<0.3 且 close<MA100），UNCERTAIN 已登记
  D4 因子登记: 公开动量因子不登记
  D5 框架样板: kuanke wizard 空壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_hs300, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-fdbc279fba99"
WINDOW_KIND = "stock"
_RPS_WIN, _MIN_RPS, _MAX_HOLD = 120, 85, 5
_EXCL_GAIN, _SELL_WIN, _SELL_GAIN = 0.5, 90, 0.3


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=250))[:10]
    px = load_px(load_start, end, fields=("close",))
    hs = load_hs300()
    px = px[px["symbol"].isin(hs)]
    close = filter_st(wide(px).ffill(), load_st_flags(load_start, end))

    gain_rps = close / close.shift(_RPS_WIN) - 1.0
    rank_desc = gain_rps.rank(axis=1, ascending=False)
    rps = (1.0 - rank_desc / gain_rps.notna().sum(axis=1)) * 100.0
    cand = (rps >= _MIN_RPS) & (gain_rps <= _EXCL_GAIN)

    sell_sig = ((close / close.shift(_SELL_WIN) - 1.0) < _SELL_GAIN) & (close < close.rolling(100).mean())

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    c_idx = cand.shift(1).reindex(dates).fillna(False)
    g_idx = gain_rps.shift(1).reindex(dates)
    s_idx = sell_sig.shift(1).reindex(dates).fillna(False)
    holdings: list[str] = []
    for k, dt in enumerate(dates):
        for s in list(holdings):
            if bool(s_idx.iloc[k, close.columns.get_loc(s)]):
                holdings.remove(s)
        row = c_idx.iloc[k] & g_idx.iloc[k].notna().fillna(False)
        if bool(row.any()):
            ranked = g_idx.iloc[k][row].sort_values(ascending=False)
            for s in ranked.index:
                if len(holdings) >= _MAX_HOLD:
                    break
                if s not in holdings:
                    holdings.append(s)
        if holdings:
            weights.loc[dt, holdings] = 1.0 / len(holdings)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 成分快照", "D2 T+1收盘", "D3 wizard卖出语义UNCERTAIN",
                                               "D4 公开因子不登记", "D5 空壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
