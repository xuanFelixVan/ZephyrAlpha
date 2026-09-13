# [BLUEPRINT] MOD-BT-054 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_7f7e5f935dfc_dmi_timing
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
# [A_module] module_id=MOD-BT-054 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 054: DMI 大盘择时（原文: 2020年度精选策略/79，标的 399300=沪深300）。

原文逻辑: talib ADX(18)/PLUS_DI(18)/MINUS_DI(18)：ADX 上行 且 +DI>-DI → 全仓；
  ADX 下行 且 +DI<-DI → 清仓。
译文实现: kline_index 000300 日线，Wilder 平滑实现 ADX/DI；信号 T-1，T 收盘执行。
因子拆解: DMI（ADX/DI 趋向指标）——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 399300 → 000300 指数收益模拟
  D2 执行时点: 原文当日 → T 日收盘（引擎 T+1 起算收益）
  D3 DI 实现: Wilder 递推平滑（与 talib 一致口径）
  D4 因子登记: DMI 技术指标不入 factor_registry
  D5 框架样板: record 壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
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

STRATEGY_ID = "CAND-7f7e5f935dfc"
WINDOW_KIND = "index"
_PERIOD = 18


def _wilder_ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(alpha=1.0 / n, adjust=False).mean()


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=150))[:10]
    idx = load_index("000300", load_start, end, fields=("high", "low", "close"))
    h, l, c = idx["high"], idx["low"], idx["close"]
    up, dn = h.diff(), -l.diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=h.index)
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=h.index)
    tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    atr = _wilder_ema(tr, _PERIOD)
    pdi = 100 * _wilder_ema(plus_dm, _PERIOD) / atr
    mdi = 100 * _wilder_ema(minus_dm, _PERIOD) / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi)
    adx = _wilder_ema(dx, _PERIOD)
    long_sig = (adx > adx.shift(1)) & (pdi > mdi)
    exit_sig = (adx < adx.shift(1)) & (pdi < mdi)
    dates = idx.index[(idx.index >= pd.Timestamp(start)) & (idx.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    pos = 0.0
    for dt in dates:
        if bool(long_sig.loc[dt]):
            pos = 1.0
        elif bool(exit_sig.loc[dt]):
            pos = 0.0
        weights.loc[dt, "000300"] = pos
    closes = idx[["close"]].rename(columns={"close": "000300"})
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 指数收益模拟", "D2 收盘口径", "D3 Wilder实现",
                                               "D4 技术指标不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
