# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.backtest.indicator_consumption_demo
# [DOMAIN] D_FACTOR
# [A_module] module_id=scripts-indicator-consumption-demo | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""技术指标消费模式样板（批 7 块 B，docs/_working/2026-09-14-tilib-batch7-wiring-plan.md）。

两个场景演示"经 indicator_reader 消费指标列"的标准姿势，后续因子/策略照抄：

  B1 波动率止损冒烟：atr_14 → 3×ATR 止损带；yang_zhang_20 → 年化波动参考
  B2 超买超卖因子输入：rsi_6/boll_pctb → 简单因子构造（均值回归 demo 因子）

用法：
    python scripts/backtest/indicator_consumption_demo.py --symbol 000852 --days 60
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd  # noqa: E402

from zephyr.factor.indicator_reader import read_indicator  # noqa: E402


def b1_volatility_stop(symbol: str, days: int) -> dict:
    """B1：ATR 止损带 + YZ 年化波动参考（趋势跟随止损范式）。

    数据纪律示范：指标列走 indicator_reader（指标表）；close 走 kline 表（价格归价格表）。
    """
    import datetime

    from zephyr.data import ch_reader

    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    ind = read_indicator_tail(symbol, days, ["atr_14", "yang_zhang_20"])
    kline_tsv = ch_reader.query(
        f"SELECT trade_date, close FROM c1_market.kline_daily "
        f"WHERE symbol = '{symbol}' AND trade_date >= '{start}' AND trade_date <= '{end}' "
        f"ORDER BY trade_date FORMAT TSV"
    )
    if ind.empty or not kline_tsv.strip():
        return {"symbol": symbol, "error": "无数据"}
    kline = pd.read_csv(io.StringIO(kline_tsv), sep="\t", header=None, names=["trade_date", "close"])
    merged = ind.merge(kline, on="trade_date", how="inner").dropna(subset=["atr_14"])
    if merged.empty:
        return {"symbol": symbol, "error": "指标与K线无对齐数据"}
    last = merged.iloc[-1]
    close = float(last["close"])
    atr = float(last["atr_14"])
    return {
        "symbol": symbol,
        "as_of": str(last["trade_date"]),
        "close": round(close, 2),
        "atr_14": round(atr, 4),
        "stop_long_3atr": round(close - 3 * atr, 2),
        "stop_short_3atr": round(close + 3 * atr, 2),
        "yz_vol_daily_pct": round(float(last["yang_zhang_20"]), 3),
    }


def b2_mean_reversion_factor(symbol: str, days: int) -> dict:
    """B2：均值回归 demo 因子 = 0.5×z(rsi_6 超卖缺口) + 0.5×%B 深度（因子输入接线范式）。"""
    df = read_indicator_tail(symbol, days, ["rsi_6", "boll_pctb"])
    if df.empty:
        return {"symbol": symbol, "error": "无数据"}
    tail = df.dropna()
    if len(tail) < 10:
        return {"symbol": symbol, "error": f"有效样本不足: {len(tail)}"}
    rsi_gap = max(0.0, (30 - float(tail["rsi_6"].iloc[-1])) / 30)  # RSI 深入超卖区程度 [0,1]
    pctb_depth = max(0.0, -float(tail["boll_pctb"].iloc[-1]))  # %B 跌破下轨深度
    score = float(0.5 * rsi_gap + 0.5 * min(pctb_depth, 1.0))
    return {
        "symbol": symbol,
        "as_of": str(tail["trade_date"].iloc[-1]),
        "rsi_6": round(float(tail["rsi_6"].iloc[-1]), 2),
        "boll_pctb": round(float(tail["boll_pctb"].iloc[-1]), 3),
        "mean_reversion_score": round(score, 4),
    }


def read_indicator_tail(symbol: str, days: int, columns: list[str]):
    """近 N 自然日尾部读取（demo 便捷封装；正式消费方直接用 read_indicator）。"""
    import datetime

    from zephyr.factor.indicator_reader import read_indicator

    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    return read_indicator(symbol, period="daily", columns=columns, start=start, end=end)


def main() -> int:
    ap = argparse.ArgumentParser(description="技术指标消费模式样板（B1 止损 + B2 因子输入）")
    ap.add_argument("--symbol", default="000852")
    ap.add_argument("--days", type=int, default=60)
    args = ap.parse_args()
    import json

    print(json.dumps(
        {"B1_volatility_stop": b1_volatility_stop(args.symbol, args.days),
         "B2_mean_reversion_factor": b2_mean_reversion_factor(args.symbol, args.days)},
        ensure_ascii=False, indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
