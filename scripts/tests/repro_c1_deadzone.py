"""C1 死区优化对比——无死区 vs 有死区(deadzone=0.02)。

验证 DeadzoneShrinkageProvider 是否降低 Turnover + 不伤害 Sharpe/MaxDD。
基准组（关）两组相同（ConstShrinkageProvider(1.0)），差异在实验组（开）。
"""

from __future__ import annotations

import logging
import warnings
from decimal import Decimal
from pathlib import Path

import pandas as pd

from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.c1_runner import run_c1_with_provider
from zephyr.backtest.regime_validation.shrinkage_provider import (
    DeadzoneShrinkageProvider,
    ScheduleShrinkageProvider,
)
from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry

BASKET_SYMBOLS = [
    "600000",
    "000001",
    "600519",
    "600036",
    "601318",
    "000651",
    "600276",
    "000858",
    "600887",
    "601166",
]
REAL_START = "2015-01-01"
REAL_END = "2026-06-30"
REPRO_DIR = Path(r"d:\ZephyrAlpha\logs\c1_repro")


def load_basket_data() -> pd.DataFrame:
    registry = get_registry()
    hfq_table = registry.table("market_kline_daily_hfq")
    syms_str = ", ".join([f"'{s}'" for s in BASKET_SYMBOLS])
    sql = (
        f"SELECT trade_date, symbol, open, high, low, close, volume "
        f"FROM {hfq_table} FINAL WHERE symbol IN ({syms_str}) "
        f"AND trade_date >= toDate('{REAL_START}') AND trade_date <= toDate('{REAL_END}') "
        f"ORDER BY symbol, trade_date"
    )
    tsv = ch_reader.query(sql)
    rows = [l.split("\t") for l in tsv.strip().split("\n") if l.strip() and len(l.split("\t")) >= 7]
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "open", "high", "low", "close", "volume"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.rename(columns={"trade_date": "date"}).set_index(["symbol", "date"]).sort_index()
    return df


def load_schedule() -> dict:
    df = pd.read_csv(REPRO_DIR / "shrinkage_schedule.csv", parse_dates=["date"])
    return {pd.Timestamp(d).to_pydatetime(): float(v) for d, v in zip(df["date"], df["shrinkage"])}


def make_signals(data: pd.DataFrame) -> pd.DataFrame:
    dates = data.index.get_level_values("date").unique().sort_values()
    return pd.DataFrame({s: 1.0 for s in BASKET_SYMBOLS}, index=pd.DatetimeIndex(dates, name="date"))


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    warnings.filterwarnings("ignore")

    print("[deadzone] 加载数据 + Shrinkage 序列...")
    data = load_basket_data()
    schedule = load_schedule()
    signals = make_signals(data)
    cfg = BacktestConfig(initial_capital=Decimal("1000000"), risk_free_rate=0.02)

    print("[deadzone] 跑无死区 C1（原 baseline）...")
    r_no = run_c1_with_provider(
        data,
        signals,
        ScheduleShrinkageProvider(schedule),
        backtest_config=cfg,
    )

    print("[deadzone] 跑有死区 C1（deadzone=0.02）...")
    r_dz = run_c1_with_provider(
        data,
        signals,
        DeadzoneShrinkageProvider(ScheduleShrinkageProvider(schedule), deadzone=0.02),
        backtest_config=cfg,
    )

    print("\n" + "=" * 78)
    print("C1 死区优化对比（基准组'关'两组相同，差异在实验组'开'）")
    print("=" * 78)
    print(f"{'指标':<10} {'无死区 开':<14} {'有死区 开':<14} {'变化':<14} {'判定'}")
    print("-" * 78)
    for vn, vd in zip(r_no.metric_verdicts, r_dz.metric_verdicts):
        delta = vd.experiment_value - vn.experiment_value
        # Turnover 越低越好，其他越高越好
        better = delta < 0 if vn.name == "Turnover" else delta > 0
        flag = "✅改善" if better else ("≈持平" if abs(delta) < 0.005 else "⚠️退化")
        print(f"{vn.name:<10} {vn.experiment_value:<14.4f} {vd.experiment_value:<14.4f} {delta:+.4f}{'':<8} {flag}")
    print("-" * 78)
    print(
        f"trades(开): 无死区={r_no.experiment_result.trades_count}  有死区={r_dz.experiment_result.trades_count}"
        f"  (减少 {(1 - r_dz.experiment_result.trades_count / r_no.experiment_result.trades_count) * 100:.0f}%)"
    )
    print(
        f"Sharpe(开): 无死区={r_no.experiment_result.sharpe_ratio:.4f}  有死区={r_dz.experiment_result.sharpe_ratio:.4f}"
    )
    print(
        f"MaxDD(开):  无死区={r_no.experiment_result.max_drawdown:.4f}  有死区={r_dz.experiment_result.max_drawdown:.4f}"
    )
    print(f"passed:     无死区={r_no.passed}  有死区={r_dz.passed}")
    print("=" * 78)


if __name__ == "__main__":
    main()
