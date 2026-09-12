# [BLUEPRINT] MOD-BT-068 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_e3da6fa71af1_panic_rebound
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号；T 日跌幅用 T 收盘=执行时点可知）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-068 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 068: 恐慌反弹持有 19 日（原文: 2022年度精选策略/57 别人恐惧我贪婪3——股债组合）。

原文逻辑: 信号源=上证指数；昨日跌幅<=-1.5% 且 今日 14:55 跌幅<=-1.4% → 卖债全仓买
  512100（中证1000ETF）；此后每 20 个交易日（day%20==0）卖股买回国债 ETF；
  复位后恐慌条件可再次触发。
译文实现: 14:55 tick 跌幅 → T 收盘跌幅（D2 声明近似，尾盘介入收益损失已声明）；
  512100 → 000852 中证1000 指数收益（D1）；国债腿 → 空仓（D3）；状态机照搬。
因子拆解: 恐慌跌幅+固定持有期——价格衍生，不入 factor_registry。
翻译差异声明:
  D1 标的: 512100 → 000852 指数收益替代
  D2 执行时点: 原文 14:55 tick → T 收盘（跌幅阈值同值应用于收盘涨跌幅）
  D3 防御腿: 511010 无数据 → 空仓
  D4 因子登记: 不入 factor_registry
  D5 框架样板: —
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

STRATEGY_ID = "CAND-e3da6fa71af1"
WINDOW_KIND = "index"
_DROP_PREV, _DROP_TODAY, _HOLD_N = -0.015, -0.014, 20


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    sh = load_index("000001", start, end, fields=("close",))
    ret = sh["close"].pct_change()
    panic = (ret.shift(1) <= _DROP_PREV) & (ret <= _DROP_TODAY)

    dates = sh.index
    weights = pd.DataFrame(0.0, index=dates, columns=["000852"])
    pos, day = 0.0, 0
    for dt in dates:
        if pos == 0.0:
            if bool(panic.loc[dt]):
                pos, day = 1.0, 1
        else:
            day += 1
            if day % _HOLD_N == 0:
                pos, day = 0.0, 0
        weights.loc[dt, "000852"] = pos
    idx1000 = load_index("000852", start, end, fields=("close",))[["close"]].rename(columns={"close": "000852"})
    return weights, idx1000


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 512100→000852", "D2 14:55→收盘", "D3 债腿→空仓",
                                               "D4 不入库", "D5 —"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
