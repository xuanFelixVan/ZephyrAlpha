# [BLUEPRINT] MOD-BT-038 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.pilot_003_zscore_meanrev
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C3 翻译试点；C4 快筛批测
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日信号用 ≤T-1 数据）；成本=冻结土规；差异声明完整；单标的择时（原文池=1 只）
# [MODIFY-GUARD] tests/backtest/test_translated_pilot_003.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_translated_pilot_003.py
# [A_module] module_id=MOD-BT-038 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C3 翻译试点第 3 条：zscore 均值回归（单标的择时，聚宽→本项目权重函数）。

原文（2020年度精选策略/12）:
  股票池=单只（601238 广汽集团）；信号=价格偏离 MA20 的差值在过去 60 日窗口的 zscore：
  zscore<=-2（超跌）买入、zscore>=+1（回归）卖出；最多持 1 只；每日开盘执行用昨日数据。
  （"胜率100%"为营销话术——实际是单标的超跌抄底+回归止盈，胜率依赖窗口。）

译文:
  同逻辑直译（zscore=(close-MA20) 在 rolling 60 窗口的标准化，窗口含 T-1，与原文同口径）；
  收益=kline_daily_hfq 后复权 close；T+1 收盘执行；冻结成本口径。

翻译差异声明:
  D1 执行: 原文开盘价成交 → 译文 T+1 收盘成交（C4 批次统一口径）
  D2 滑点: 原文默认（未显式设置） → 译文 5bp（冻结土规）
  D3 zscore 口径: 原文 std 为 60 窗口全样本 std（含最新值，轻微同义重复）→ 译文保持同口径（忠实优先）
  D4 因子登记: MA/zscore 属技术指标（OHLCV 计算），不入 factor_registry
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

_COMMISSION_BP = 2.5
_STAMP_BP = 10.0
_SLIPPAGE_BP = 5.0
_Z_WINDOW = 60
_MA_WINDOW = 20
_LOWER, _UPPER = -2.0, 1.0
_SYMBOL = "601238"


def _load_single(symbol: str, start: str, end: str) -> pd.DataFrame:
    from zephyr.data.ch_writer import get_client_strict

    c = get_client_strict()
    df = pd.DataFrame(c.execute(
        f"SELECT trade_date, toFloat64(close) AS close FROM c1_market.kline_daily_hfq "
        f"WHERE symbol = '{symbol}' AND trade_date >= '{start}' AND trade_date <= '{end}' AND close > 0"
    ), columns=["trade_date", "close"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df.set_index("trade_date").sort_index()


def generate_weights(closes: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """zscore 均值回归状态机：≤-2 入场、≥+1 离场（信号=T-1，权重=T 日持仓）。"""
    close = closes["close"]
    ma = close.rolling(_MA_WINDOW).mean()
    sub = close - ma
    z = (sub - sub.rolling(_Z_WINDOW).mean()) / sub.rolling(_Z_WINDOW).std()
    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.Series(0.0, index=dates)
    holding = False
    for dt in dates:
        pos = close.index.get_loc(dt)
        if pos < 1:
            continue
        z_prev = z.iloc[pos - 1]  # T 日执行用 T-1 信号
        if not holding and pd.notna(z_prev) and z_prev <= _LOWER:
            holding = True
        elif holding and pd.notna(z_prev) and z_prev >= _UPPER:
            holding = False
        weights.loc[dt] = 1.0 if holding else 0.0
    return weights.to_frame(name=_SYMBOL)


def run_backtest(weights: pd.DataFrame, closes: pd.DataFrame) -> dict[str, Any]:
    close = closes.reindex(weights.index).ffill()
    rets = close.iloc[:, 0].pct_change().fillna(0.0)
    w = weights[_SYMBOL]
    gross = w.shift(1).fillna(0.0) * rets
    turnover = (w - w.shift(1)).abs().fillna(0.0) / 2.0
    cost = turnover * (_COMMISSION_BP * 2 + _STAMP_BP + _SLIPPAGE_BP * 2) / 10000.0
    net = gross - cost
    equity = (1.0 + net).cumprod()
    years = max(len(net) / 244.0, 1e-9)
    sharpe = float(net.mean() / net.std() * np.sqrt(244)) if net.std() > 0 else 0.0
    mdd = float((equity / equity.cummax() - 1.0).min())
    win = float((net[w > 0] > 0).mean()) if (w > 0).any() else 0.0
    return {
        "days": int(len(net)), "sharpe": round(sharpe, 3),
        "ann_return": round(float(equity.iloc[-1] ** (1 / years) - 1.0), 4),
        "max_drawdown": round(mdd, 4), "holding_winrate": round(win, 3),
        "avg_turnover_1side": round(float(turnover.mean()), 4),
        "equity_final": round(float(equity.iloc[-1]), 4),
        "hold_days_pct": round(float((w > 0).mean()), 3),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="C3 试点第 3 条：zscore 均值回归（单标的，翻译实现）")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2023-12-31")
    args = parser.parse_args()
    load_start = str(pd.Timestamp(args.start) - pd.Timedelta(days=400))[:10]

    closes = _load_single(_SYMBOL, load_start, args.end)
    if closes.empty:
        raise RuntimeError(f"{_SYMBOL} 行情缺失")
    logger.info("行情: %d 日（%s~%s）", len(closes), closes.index.min().date(), closes.index.max().date())
    weights = generate_weights(closes, args.start, args.end)
    stats = run_backtest(weights, closes)
    print(json.dumps({
        "pilot": "003_zscore_meanrev", "source": "2020年度精选策略/12",
        "symbol": _SYMBOL, "window": [args.start, args.end],
        "translation_diffs": ["D1 T+1收盘执行", "D2 滑点5bp", "D3 zscore窗口含最新值同口径",
                              "D4 MA/zscore技术指标不入因子库"],
        "stats": stats,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
