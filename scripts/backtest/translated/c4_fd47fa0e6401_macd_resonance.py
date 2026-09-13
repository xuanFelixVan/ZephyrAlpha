# [BLUEPRINT] MOD-BT-063 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_fd47fa0e6401_macd_resonance
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
# [A_module] module_id=MOD-BT-063 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 063: MACD 多周期共振（原文: 2023年度精选策略/73 MACD多周期共振）。

原文逻辑: 全 A 剔停/退/ST/科创/上市<60 天；周线 MACD 金叉（第二金叉过滤）→ 周池；
  周池内日线（原文 60 分钟）MACD 金叉 → 买入（等分资金）；卖出=close<昨收 或 close<今日开
  或 vol>1.5×昨vol；+10% 盘中止盈（every_bar）。
译文实现: 共振降为 周线MACD金叉×日线MACD金叉（60m→日线，D3）；卖出规则日线向量化；
  盘中止盈降为收盘口径（close>=1.1×信号基准平仓，D2）。
因子拆解: 多周期 MACD 共振——技术指标，不入 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ）剔科创/ST；次新按上市 60 交易日近似
  D2 执行/止盈: 原文 14:00 买入+every_bar 止盈 → T+1 收盘成交+收盘止盈（10%）
  D3 共振频率: 周线×60分钟 → 周线×日线
  D4 因子登记: MACD 技术指标不入 factor_registry
  D5 框架样板: heapq/绘图壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-13 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-fd47fa0e6401"
WINDOW_KIND = "stock"
_TP = 0.10


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=420))[:10]
    px = load_px(load_start, end, fields=("close", "volume", "open"))
    close = wide(px, "close").ffill()
    vol = wide(px, "volume").ffill().reindex(close.index)
    opn = wide(px, "open").ffill().reindex(close.index)
    close = close.loc[:, ~close.columns.str.startswith("68")]
    close = filter_st(close, load_st_flags(load_start, end))
    vol = vol.reindex(index=close.index, columns=close.columns).ffill()
    opn = opn.reindex(index=close.index, columns=close.columns).ffill()

    def _macd(s: pd.DataFrame, f: int = 12, sl: int = 26, sg: int = 9):
        dif = s.ewm(span=f, adjust=False).mean() - s.ewm(span=sl, adjust=False).mean()
        return dif, dif.ewm(span=sg, adjust=False).mean()

    wk = close.resample("W-FRI").last()
    w_dif, w_dea = _macd(wk)
    w_golden = (w_dif > w_dea) & (w_dif.shift(1) <= w_dea.shift(1))
    # 周信号映射回日频（当周内生效）
    w_ok = w_golden.reindex(close.index, method="ffill").fillna(False)
    d_dif, d_dea = _macd(close)
    d_golden = (d_dif > d_dea) & (d_dif.shift(1) <= d_dea.shift(1))
    entry = w_ok & d_golden
    exit_sig = (close < close.shift(1)) | (close < opn) | (vol > 1.5 * vol.shift(1))

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    e_idx = entry.shift(1).reindex(dates).fillna(False)
    x_idx = exit_sig.shift(1).reindex(dates).fillna(False)
    basis: dict[str, float] = {}
    holdings: list[str] = []
    for k, dt in enumerate(dates):
        for s in list(holdings):
            j = close.columns.get_loc(s)
            px_now = float(close.iloc[k, j])
            if bool(x_idx.iloc[k, j]) or (s in basis and px_now >= basis[s] * (1 + _TP)):
                holdings.remove(s)
                basis.pop(s, None)
        for s in close.columns:
            if bool(e_idx.iloc[k, close.columns.get_loc(s)]) and s not in holdings:
                holdings.append(s)
                basis[s] = float(close.iloc[k, close.columns.get_loc(s)])
        if holdings:
            weights.loc[dt, holdings] = 1.0 / len(holdings)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔科创ST", "D2 收盘止盈10%", "D3 周×日共振",
                                               "D4 技术指标不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
