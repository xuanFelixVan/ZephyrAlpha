# [BLUEPRINT] MOD-BT-047 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_e2e7f033d97c_kd_cross
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
# [A_module] module_id=MOD-BT-047 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 047: KD 指标金叉死叉择时（原文: 2020年度精选策略/29 KD指标量化交易策略）。

原文逻辑: 单标的 000016（原文写 000016.XSHE）；KD(9,3,3)：K 上穿 D 全仓买入，K 下穿 D 清仓。
译文实现: kline_daily_hfq 000016 日线；K=RSV 的 3 日 SMA、D=K 的 3 日 SMA；
  信号 T-1 确认，T 收盘执行全仓/清仓。
因子拆解: KD 随机指标（RSV 平滑）——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 原文 000016.XSHE 深市股票（聚宽代码后缀）→ 纯 6 位 000016
  D2 执行时点: 原文 open 价 → T+1 收盘成交
  D3 KD 口径: talib KD_judge 与 jqlib KD 平滑细节（SMA 递推 vs 滚动均值）存在实现差
  D4 因子登记: KD 技术指标不入 factor_registry
  D5 框架样板: send_message/log 壳不翻译
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

STRATEGY_ID = "CAND-e2e7f033d97c"
WINDOW_KIND = "stock"
_SYM = "000016"


def _kd(closes: pd.DataFrame, n: int = 9) -> tuple[pd.DataFrame, pd.DataFrame]:
    low_n = closes.rolling(n).min()
    high_n = closes.rolling(n).max()
    rsv = (closes - low_n) / (high_n - low_n) * 100.0
    k = rsv.ewm(alpha=1 / 3, adjust=False).mean()
    d = k.ewm(alpha=1 / 3, adjust=False).mean()
    return k, d


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = wide(px)
    closes = closes[closes.columns.intersection([_SYM])]
    k, d = _kd(closes)
    golden = (k > d) & (k.shift(1) <= d.shift(1))
    death = (k <= d) & (k.shift(1) > d.shift(1))
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    g_idx = golden.shift(1).reindex(dates).fillna(False).iloc[:, 0]
    d_idx = death.shift(1).reindex(dates).fillna(False).iloc[:, 0]
    pos = 0.0
    for dt in dates:
        if bool(g_idx.loc[dt]):
            pos = 1.0
        elif bool(d_idx.loc[dt]):
            pos = 0.0
        weights.loc[dt, :] = pos
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 代码归一", "D2 T+1收盘", "D3 KD实现差",
                                               "D4 技术指标不入库", "D5 日志壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
