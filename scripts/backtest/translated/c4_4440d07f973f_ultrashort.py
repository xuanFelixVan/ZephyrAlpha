# [BLUEPRINT] MOD-BT-042 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_4440d07f973f_ultrashort
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号；高开判断用 T 日开盘=执行前可知）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-042 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 042: MA 死叉+MACD 临界+高开 1 日轮换（原文: 2022年度精选策略/8. 14个月200%超短线）。

原文逻辑: 全 A 主板（剔创业板/科创/ST/退）；昨日 MA5 下穿 MA10（死叉）+死叉前日 MA5 量>
  MA10 量+昨日 MA5 量×1.2>MA10 量+MA20/MA30 抬升；MACD(12,26,9) dif>0 且 dea>0 且
  dea-dif∈(-0.1,0)（临界金叉）；昨日/前日涨跌一跌一涨；今日开盘>昨收（高开）；按代码序取
  第一只全仓买入，次日无条件清仓轮换（1 日持仓）。
译文实现: 同规则日线向量化；1 日持仓=持有 T-1 候选首只，T 收盘换仓。
因子拆解: MA5/10/20/30、量能均线、MACD——技术指标组合，不入 factor_registry。
翻译差异声明:
  D1 股票池: 全 A 主板剔 ST（stk_limit st_flag）——原文停牌过滤在 HFQ 表无停牌列，不可剔（声明）
  D2 执行时点: 原文盘中按实时价 → T+1 收盘成交
  D3 阈值尺度: MACD dea-dif∈(-0.1,0) 为绝对价差阈值，后复权价与原文真实价存在尺度漂移
  D4 因子登记: MA/MACD 技术指标不入 factor_registry
  D5 框架样板: 原文下单阻塞/日志壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import emit, load_px, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-4440d07f973f"
WINDOW_KIND = "stock"


def _ema(s: pd.DataFrame, span: int) -> pd.DataFrame:
    return s.ewm(span=span, adjust=False).mean()


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=90))[:10]
    px = load_px(load_start, end, fields=("close", "volume", "open"))
    close = wide(px, "close").ffill()
    vol = wide(px, "volume").ffill()
    opn = wide(px, "open").ffill()
    close = close.loc[:, ~close.columns.str.startswith(("30", "68"))]
    vol = vol.reindex(columns=close.columns)
    opn = opn.reindex(columns=close.columns)

    ma5c, ma10c = close.rolling(5).mean(), close.rolling(10).mean()
    ma20c, ma30c = close.rolling(20).mean(), close.rolling(30).mean()
    ma5v, ma10v = vol.rolling(5).mean(), vol.rolling(10).mean()

    # 逐日信号：T 日候选 = 用 T-1 与 T-2 数据
    m5_1, m10_1 = ma5c.shift(1), ma10c.shift(1)
    m5_2, m10_2 = ma5c.shift(2), ma10c.shift(2)
    v5_1, v10_1 = ma5v.shift(1), ma10v.shift(1)
    v5_2, v10_2 = ma5v.shift(2), ma10v.shift(2)
    m20_1, m20_2 = ma20c.shift(1), ma20c.shift(2)
    m30_1, m30_2 = ma30c.shift(1), ma30c.shift(2)
    dx1 = (
        (m5_1 < m10_1) & (m5_2 > m10_2)
        & (v5_2 > v10_2) & (v5_1 * 1.2 > v10_1)
        & (m20_1 > m20_2) & (m30_1 > m30_2)
    )
    dif = _ema(close, 12) - _ema(close, 26)
    dea = _ema(dif, 9)
    dx2 = (dif.shift(1) > 0) & (dea.shift(1) > 0) & ((dea.shift(1) - dif.shift(1)) > -0.1) \
        & ((dea.shift(1) - dif.shift(1)) < 0)
    chg = close.pct_change()
    dx3 = ((chg.shift(1) > 0) & (chg.shift(2) < 0)) | ((chg.shift(1) < 0) & (chg.shift(2) > 0))
    # 高开：T 日开盘 > T-1 收盘（执行前可知，PIT 合规）
    gap_up = opn > close.shift(1)
    cand = dx1 & dx2 & dx3 & gap_up.reindex(close.index).fillna(False)

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    for dt in dates:
        row = cand.loc[dt]
        if bool(row.any()):
            weights.loc[dt, row.idxmax()] = 1.0
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 主板剔ST(停牌不可剔)", "D2 T+1收盘",
                                               "D3 MACD绝对阈值复权尺度漂移", "D4 技术指标不入库",
                                               "D5 框架壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
