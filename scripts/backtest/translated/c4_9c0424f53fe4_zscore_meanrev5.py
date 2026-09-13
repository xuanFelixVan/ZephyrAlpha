# [BLUEPRINT] MOD-BT-046 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_9c0424f53fe4_zscore_meanrev5
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号）；成本=冻结土规；固定 5 标的与原文一致
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-046 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 046: 5 股固定池 zscore 均值回归（原文: 2020年度精选策略/18 均值回归策略分享）。

原文逻辑: 固定池 [002241,000333,002230,002747,002415]；zscore=(close-MA20) 的 60 日标准化；
  z<=-2 买入；卖出=z>=1 或 MA5<MA10（死叉）或 MACD 死叉或亏损>7%（avg_cost*0.93）或
  持仓高点回撤>15%；等权分散（maxnum=5）。
译文实现: 同规则逐标的向量化状态机（持仓期高点回撤替代 avg_cost 亏损口径，D3）；
  信号 T-1，T 收盘执行，等权持有触发者。
因子拆解: zscore 偏离（价格-MA20 标准化）+MA/MACD——技术指标组合，不入 factor_registry。
翻译差异声明:
  D1 标的池: 固定 5 只与原文一致（含已退市风险的代码由数据表自然处理）
  D2 执行时点: T+1 收盘成交（原文 open 价）
  D3 止损: 原文按持仓成本价（avg_cost）→ 译文按信号日收盘基准（向量化无逐笔成本）
  D4 因子登记: 技术指标组合不入 factor_registry
  D5 框架样板: record/send_message 日志壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, load_px, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-9c0424f53fe4"
WINDOW_KIND = "stock"
_POOL = ["002241", "000333", "002230", "002747", "002415"]
_ZWIN, _MAWIN, _LOWER, _UPPER = 60, 20, -2.0, 1.0
_STOP = 0.93


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=120))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = wide(px)
    closes = closes[[c for c in _POOL if c in closes.columns]]
    ma = closes.rolling(_MAWIN).mean()
    sub = closes - ma
    z = (sub - sub.rolling(_ZWIN).mean()) / sub.rolling(_ZWIN).std()
    ma5, ma10 = closes.rolling(5).mean(), closes.rolling(10).mean()
    dif = closes.ewm(span=12, adjust=False).mean() - closes.ewm(span=26, adjust=False).mean()
    dea = dif.ewm(span=9, adjust=False).mean()
    macd_dead = (dif < dea) & (dif.shift(1) >= dea.shift(1))
    buy_sig = z <= _LOWER
    sell_sig = (z >= _UPPER) | (ma5 < ma10) | macd_dead

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    holdings: dict[str, float] = {}  # symbol -> 基准价
    b_idx = buy_sig.shift(1).reindex(dates).fillna(False)
    s_idx = sell_sig.shift(1).reindex(dates).fillna(False)
    px_open_sig = closes.shift(1)  # T-1 收盘基准（D3）
    for k, dt in enumerate(dates):
        for s in list(holdings):
            j = closes.columns.get_loc(s)
            px_now = float(px_open_sig.iloc[k, j])
            if bool(s_idx.iloc[k, j]) or px_now < holdings[s] * _STOP:
                del holdings[s]
        for s in closes.columns:
            if s not in holdings and bool(b_idx.iloc[k, closes.columns.get_loc(s)]):
                holdings[s] = float(px_open_sig.iloc[k, closes.columns.get_loc(s)])
        if holdings:
            weights.loc[dt, list(holdings)] = 1.0 / len(holdings)
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 固定5股", "D2 T+1收盘", "D3 止损基准口径",
                                               "D4 技术指标不入库", "D5 日志壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
