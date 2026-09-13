# [BLUEPRINT] MOD-BT-065 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_2b351fd05d5f_ultrashort_lowopen
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号；低开判断用 T 日开盘=执行前可知）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-065 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 065: MA 死叉+MACD 临界+低开变体（原文: 2022年度精选策略/80 短线策略 45%）。

原文逻辑: 与 042（CAND-4440d07f973f）同族四层过滤——MA5 下穿 MA10+量能纠错+MA20/30 抬升、
  MACD dif/dea>0 且 dif-dea∈(0,0.1)、昨日/前日涨跌一跌一涨；差异点=低开入场
  （day_open(T) < close(T-1)）；单票全仓按代码序取第一只，次日无条件清仓轮换。
译文实现: 同 042 引擎口径，gap 条件反向（低开）；1 日持仓轮换。
因子拆解: MA/MACD/量能——技术指标，不入 factor_registry。
翻译差异声明:
  D1 股票池: 全 A 主板剔 ST（停牌不可剔声明同 042）
  D2 执行时点: 原文开盘 → T+1 收盘成交（低开判断用 T 开盘，执行前可知，PIT 合规）
  D3 阈值尺度: MACD 绝对阈值 0.1 在复权价尺度存在漂移（同 042）
  D4 因子登记: 技术指标不入 factor_registry
  D5 框架样板: 框架壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-13 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
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

STRATEGY_ID = "CAND-2b351fd05d5f"
WINDOW_KIND = "stock"


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

    dx1 = (
        (ma5c.shift(1) < ma10c.shift(1)) & (ma5c.shift(2) > ma10c.shift(2))
        & (ma5v.shift(2) > ma10v.shift(2)) & (ma5v.shift(1) * 1.2 > ma10v.shift(1))
        & (ma20c.shift(1) > ma20c.shift(2)) & (ma30c.shift(1) > ma30c.shift(2))
    )
    dif = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    dea = dif.ewm(span=9, adjust=False).mean()
    dx2 = (dif.shift(1) > 0) & (dea.shift(1) > 0) & ((dif.shift(1) - dea.shift(1)) > 0) \
        & ((dif.shift(1) - dea.shift(1)) < 0.1)
    chg = close.pct_change()
    dx3 = ((chg.shift(1) > 0) & (chg.shift(2) < 0)) | ((chg.shift(1) < 0) & (chg.shift(2) > 0))
    gap_dn = opn < close.shift(1)
    cand = dx1 & dx2 & dx3 & gap_dn.reindex(close.index).fillna(False)

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
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 主板剔ST", "D2 T+1收盘低开判定", "D3 阈值尺度",
                                               "D4 技术指标不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
