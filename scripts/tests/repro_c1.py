# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""C1 独立复现（方式 B）—— 用 dump 的 Shrinkage CSV + 本项目回测引擎对答案。

复用 dump 脚本的取数逻辑（确保数据一致），但用 c1_runner.run_c1_with_provider
（独立编排层）跑 C1 开/关对比，与另一个 AI 的 c1_metrics.json 对答案。

验证目标：
  - 给定相同 Shrinkage 序列 + 相同数据 + 相同信号，不同编排入口结果是否一致
  - 排查 orchestrator 层是否有数据挑选/区间优化
"""

from __future__ import annotations

import json
import logging
import warnings
from decimal import Decimal
from pathlib import Path

import pandas as pd

from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.c1_runner import run_c1_with_provider, save_c1_report
from zephyr.backtest.regime_validation.shrinkage_provider import ScheduleShrinkageProvider
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
    """复用 dump 脚本取数逻辑（registry.table + FINAL + 纯数字 symbol），确保数据一致。"""
    registry = get_registry()
    hfq_table = registry.table("market_kline_daily_hfq")
    syms_str = ", ".join([f"'{s}'" for s in BASKET_SYMBOLS])
    sql = (
        f"SELECT trade_date, symbol, open, high, low, close, volume "
        f"FROM {hfq_table} FINAL "
        f"WHERE symbol IN ({syms_str}) "
        f"AND trade_date >= toDate('{REAL_START}') AND trade_date <= toDate('{REAL_END}') "
        f"ORDER BY symbol, trade_date"
    )
    tsv = ch_reader.query(sql)
    rows = []
    for line in tsv.strip().split("\n"):
        line = line.rstrip("\r")
        if not line:
            continue
        vals = line.split("\t")
        if len(vals) < 7:
            continue
        rows.append(vals)
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "open", "high", "low", "close", "volume"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.rename(columns={"trade_date": "date"})
    df = df.set_index(["symbol", "date"]).sort_index()
    return df


def load_shrinkage_schedule() -> dict:
    """读 dump 的 shrinkage_schedule.csv → {datetime: float}。"""
    df = pd.read_csv(REPRO_DIR / "shrinkage_schedule.csv", parse_dates=["date"])
    return {pd.Timestamp(d).to_pydatetime(): float(v) for d, v in zip(df["date"], df["shrinkage"])}


def make_equal_weight_signals(data: pd.DataFrame) -> pd.DataFrame:
    """等权信号（date × symbol = 1.0，引擎内归一化）。"""
    dates = data.index.get_level_values("date").unique().sort_values()
    return pd.DataFrame({s: 1.0 for s in BASKET_SYMBOLS}, index=pd.DatetimeIndex(dates, name="date"))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    warnings.filterwarnings("ignore")
    logging.getLogger("hmmlearn").setLevel(logging.ERROR)

    print("[repro] 1/4 加载篮子后复权日K（复用 dump 取数逻辑）...")
    data = load_basket_data()
    n_sym = data.index.get_level_values("symbol").nunique()
    print(f"[repro]   篮子: {len(data)} 行, {n_sym} 标为")

    print("[repro] 2/4 加载 dump 的 Shrinkage 序列...")
    schedule = load_shrinkage_schedule()
    print(f"[repro]   Shrinkage: {len(schedule)} 日, 均值={sum(schedule.values()) / len(schedule):.4f}")

    print("[repro] 3/4 构造等权信号 + 跑 C1 开/关对比（c1_runner 独立编排）...")
    signals = make_equal_weight_signals(data)
    provider = ScheduleShrinkageProvider(schedule)
    cfg = BacktestConfig(initial_capital=Decimal("1000000"), risk_free_rate=0.02)
    result = run_c1_with_provider(
        data=data,
        signals=signals,
        shrinkage_provider=provider,
        backtest_config=cfg,
    )

    print("[repro] 4/4 与另一个 AI 的 c1_metrics.json 对答案...")
    with open(REPRO_DIR / "c1_metrics.json", encoding="utf-8") as f:
        expected = json.load(f)

    save_c1_report(
        result,
        REPRO_DIR / "c1_repro_report.md",
        mode="regime",
        meta={
            "universe": "10大盘股",
            "区间": f"{REAL_START}~{REAL_END}",
            "复现方式": "B(Shrinkage CSV + c1_runner 独立编排)",
        },
    )

    # 对比表
    print("\n" + "=" * 80)
    print(f"{'指标':<10} {'关(我)':<12} {'开(我)':<12} {'关(它)':<12} {'开(它)':<12} {'判定'}")
    print("-" * 80)
    all_match = True
    for v in result.metric_verdicts:
        exp = next(m for m in expected["metrics"] if m["name"] == v.name)
        diff_b = v.baseline_value - exp["baseline_value"]
        diff_e = v.experiment_value - exp["experiment_value"]
        match = abs(diff_b) < 0.01 and abs(diff_e) < 0.01
        all_match = all_match and match
        flag = "✅一致" if match else "❌差异"
        print(
            f"{v.name:<10} {v.baseline_value:<12.4f} {v.experiment_value:<12.4f} "
            f"{exp['baseline_value']:<12.4f} {exp['experiment_value']:<12.4f} {flag} "
            f"(Δ关={diff_b:+.4f} Δ开={diff_e:+.4f})"
        )
    print("=" * 80)
    print(f"passed(我)={result.passed}  passed(它)={expected['passed']}  四项指标全一致={all_match}")
    print(f"报告: {REPRO_DIR / 'c1_repro_report.md'}")


if __name__ == "__main__":
    main()
