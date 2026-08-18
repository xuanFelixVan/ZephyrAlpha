# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# [MODULE] scripts.tests.run_c1_shrinkage_validation
# [DOMAIN] D_REGIME
# [STARTUP] manual
# [MATURITY] production
# [ARCH-REF] #11_regime_backtest_validation_plan #C1-shrinkage-comparator #MOD-REGIME-002
# [TTL] permanent
"""C1 Shrinkage 开/关对比验证执行脚本（11_regime_backtest_validation_plan Phase 1 核心验证）

一票否决：C1 不通过 = regime 检测器不部署（回退静态等权）。

两种模式：
  mock (默认): 合成 OHLCV + MockShrinkageProvider（波动率4档映射）
               → 冒烟：验证 C1 开/关对比流程端到端跑通（不代表真实效果）
  real       : 真实数据 + RegimeFeatureBuilder walk-forward HMM Shrinkage
               → 正式验证（regime 风险节流到底有没有效）

real 模式数据链（2015-2026）:
  ClickHouse → RegimeFeatureBuilder(指数K线+涨跌家数 → HMM 6特征 → walk-forward 季度
  重拟合 fit+detect → Shrinkage schedule) → ScheduleShrinkageProvider
  + 10 大盘股后复权(kline_daily_hfq) → 等权信号 → C1ShrinkageComparator.compare()

Usage:
  python scripts/tests/run_c1_shrinkage_validation.py             # mock 冒烟
  python scripts/tests/run_c1_shrinkage_validation.py --mode real # 真实数据 C1
  python scripts/tests/run_c1_shrinkage_validation.py --mode real --risk-mode full --overlay off  # Phase 2a

依据: 11_regime_backtest_validation_plan §4.3 C1 + §5 验证标准（Morwane OOS 行业基准）
"""
from __future__ import annotations

import argparse
import logging
import sys
import warnings
from datetime import datetime
from decimal import Decimal

import numpy as np
import pandas as pd

from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.c1_comparator import (
    C1ComparisonResult,
    C1ShrinkageComparator,
)
from zephyr.backtest.regime_validation.shrinkage_provider import (
    MockShrinkageProvider,
    ScheduleShrinkageProvider,
)

# real 模式才 import（避免 mock 模式依赖 ClickHouse/hmmlearn）
REAL_DEPS_OK = False
try:
    from zephyr.data import ch_reader
    from zephyr.data.table_registry import get_registry
    from zephyr.regime.core.regime_detector import RegimeDetector
    from zephyr.regime.features.regime_data_loader import RegimeDataLoader
    from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder
    REAL_DEPS_OK = True
except Exception as _exc:  # pragma: no cover
    _REAL_IMPORT_ERROR = _exc


# ── 真实数据 universe（10 大盘股，2015-2026 全历史，后复权）─────────────
BASKET_SYMBOLS = [
    "600000",  # 浦发银行
    "000001",  # 平安银行
    "600519",  # 贵州茅台
    "600036",  # 招商银行
    "601318",  # 中国平安
    "000651",  # 格力电器
    "600276",  # 恒瑞医药
    "000858",  # 五粮液
    "600887",  # 伊利股份
    "601166",  # 兴业银行
]
REAL_START = "2015-01-01"
REAL_END = "2026-06-30"
DATA_LOAD_START = "2010-01-01"  # walk-forward 5年训练历史


# ── 合成数据生成（mock 冒烟用）──────────────────────────────────────


def make_synthetic_market(
    n_days: int = 504,          # 2 年交易日
    n_symbols: int = 3,
    seed: int = 42,
) -> pd.DataFrame:
    """生成合成 OHLCV（前半低波动 + 后半高波动，让 MockShrinkage 有变化）。

    返回 MultiIndex(symbol, date) DataFrame: open/high/low/close/volume。
    设计：前 252 天低波(σ=0.01)，后 252 天高波(σ=0.035)——模拟 regime 切换，
    让 MockShrinkageProvider 在高波期收缩、低波期满部署。
    """
    rng = np.random.default_rng(seed)
    symbols = [f"60000{i}" for i in range(1, n_symbols + 1)]
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    half = n_days // 2

    frames = []
    for sym in symbols:
        close = 100.0
        rows = []
        for t in range(n_days):
            vol = 0.01 if t < half else 0.035  # 前低波后高波
            ret = rng.normal(0.0005, vol)        # 微正漂移
            close = close * (1 + ret)
            rows.append({
                "symbol": sym,
                "date": dates[t],
                "open": close * (1 + rng.normal(0, 0.002)),
                "high": close * (1 + abs(rng.normal(0, 0.005))),
                "low": close * (1 - abs(rng.normal(0, 0.005))),
                "close": close,
                "volume": float(rng.integers(500_000, 2_000_000)),
            })
        frames.append(pd.DataFrame(rows))

    return pd.concat(frames, ignore_index=True).set_index(["symbol", "date"]).sort_index()


def make_equal_weight_signals(data: pd.DataFrame) -> pd.DataFrame:
    """等权信号：每个标的每天权重 = 1.0（引擎内部归一化为 Σ=1）。"""
    dates = data.index.get_level_values("date").unique().sort_values()
    symbols = sorted(data.index.get_level_values("symbol").unique())
    return pd.DataFrame(
        {sym: 1.0 for sym in symbols},
        index=pd.DatetimeIndex(dates, name="date"),
    )


def compute_market_volatility_schedule(
    data: pd.DataFrame, window: int = 20
) -> dict[datetime, float]:
    """算市场平均年化波动率序列（跨标的 20 日 rolling std 均值 × √252）。

    供 MockShrinkageProvider：年化 vol<15%→1.0 / 15-25%→0.85 / 25-40%→0.6 / ≥40%→0.3。
    """
    closes = data["close"].unstack("symbol")               # date × symbol
    returns = np.log(closes / closes.shift(1))
    rolling_vol = returns.rolling(window).std().mean(axis=1).dropna()
    annual_vol = rolling_vol * np.sqrt(252)                # 年化
    return {dt.to_pydatetime(): float(v) for dt, v in annual_vol.items()}


# ── 真实数据加载（real 模式）─────────────────────────────────────────


def load_basket_hfq(
    symbols: list[str], start: str, end: str
) -> pd.DataFrame:
    """从 ClickHouse 加载篮子股票后复权日K（real 模式可交易 universe）。

    Returns:
        MultiIndex(symbol, date) DataFrame: open/high/low/close/volume。
    """
    registry = get_registry()
    table = registry.table("market_kline_daily_hfq")
    syms_str = ", ".join([f"'{s}'" for s in symbols])
    sql = (
        f"SELECT trade_date, symbol, open, high, low, close, volume "
        f"FROM {table} FINAL "
        f"WHERE symbol IN ({syms_str}) "
        f"AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
        f"ORDER BY symbol, trade_date"
    )
    tsv = ch_reader.query(sql)
    if not tsv or not tsv.strip():
        raise RuntimeError(f"basket hfq 查询为空: symbols={symbols}, [{start},{end}]")
    rows = []
    for line in tsv.strip().split("\n"):
        line = line.rstrip("\r")
        if not line:
            continue
        vals = line.split("\t")
        if len(vals) < 7:
            continue
        rows.append(vals)
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "open", "high",
                                      "low", "close", "volume"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # 重命名 trade_date → date（对齐回测引擎期望的 index level 名）
    df = df.rename(columns={"trade_date": "date"})
    df = df.set_index(["symbol", "date"]).sort_index()
    logging.info("basket hfq 加载: %d 行, %d 标的, %s~%s",
                 len(df), df.index.get_level_values("symbol").nunique(),
                 df.index.get_level_values("date").min(),
                 df.index.get_level_values("date").max())
    return df


# ── 结果打印 ────────────────────────────────────────────────────────


def print_result(result: C1ComparisonResult, mode: str) -> None:
    """打印 C1 对比结果。"""
    print("=" * 70)
    print(f"C1 Shrinkage 开/关对比结果（mode={mode}）")
    print("=" * 70)
    print()
    print(result.summary)
    print()
    print("─" * 70)
    print("四项指标判定：")
    print("─" * 70)
    for v in result.metric_verdicts:
        flag = "✅ 通过" if v.passed else "❌ 否决"
        print(f"  [{v.name}] {flag}")
        print(f"    {v.detail}")
        print()

    print("─" * 70)
    if result.passed:
        print("🎉 C1 通过——regime 风险节流有效，可进入 Phase 2 模型质量验证")
    else:
        print(f"⛔ C1 一票否决——{result.veto_reason}")
        if mode == "mock":
            print("   注：mock 冒烟数据不代表真实效果，流程跑通即成功")
    print("=" * 70)


# ── 主流程 ──────────────────────────────────────────────────────────


def run_mock_smoke() -> C1ComparisonResult:
    """mock 冒烟：合成数据 + MockShrinkageProvider（波动率4档映射）。

    目的：验证 C1 开/关对比流程端到端跑通，不代表真实 regime 效果。
    """
    print("[mock] 生成合成 OHLCV 数据（2年，3标的，前低波后高波）...")
    data = make_synthetic_market()
    signals = make_equal_weight_signals(data)

    print("[mock] 计算市场年化波动率序列（20日 rolling std × √252）...")
    vol_schedule = compute_market_volatility_schedule(data)
    print(f"[mock] 波动率序列：{len(vol_schedule)} 天，"
          f"年化 vol 范围 [{min(vol_schedule.values()):.4f}, {max(vol_schedule.values()):.4f}]")

    print("[mock] 构建 MockShrinkageProvider（年化 vol → 4档 Shrinkage）...")
    provider = MockShrinkageProvider(volatility_schedule=vol_schedule)

    print("[mock] 运行 C1ShrinkageComparator.compare()（开/关对比）...")
    comparator = C1ShrinkageComparator()
    # BacktestConfig 的资金/费率字段为 Decimal 类型，须用 Decimal 构造（float 会破坏撮合引擎契约）
    config = BacktestConfig(
        initial_capital=Decimal("1000000"),
        commission_rate=Decimal("0.0003"),    # 万三
        slippage_bps=Decimal("1"),            # 1bp
        risk_free_rate=0.02,
    )
    result = comparator.compare(
        data=data,
        signals=signals,
        shrinkage_provider=provider,
        backtest_config=config,
        strategy_name="c1-mock-smoke",
        initial_capital=Decimal("1000000"),
    )
    return result


def run_real(risk_mode: str = "simple", overlay: str = "off",
             temperature: float = 1.0) -> C1ComparisonResult:
    """真实模式：真实数据 + RegimeFeatureBuilder walk-forward HMM Shrinkage。

    数据链（2015-2026）:
      ① 10 大盘股后复权 → 等权信号（可交易 universe）
      ② 指数K线+涨跌家数 → HMM 6特征 → walk-forward 季度重拟合 → Shrinkage schedule
      ③ C1 开/关对比：基准(Shrinkage=1.0) vs 实验(regime schedule)

    Args:
        risk_mode: "simple"=Phase1简化版risk(1参数#1)；"full"=Phase2a全量(13参数)
        overlay:   "off"=无覆盖层(纯HMM)；"on"=Phase2b启用8转换overlay_signals
        temperature: HMM 概率温度缩放 T（13_regime_phase3_engineering_plan §2.2 P0-E2 Stage 1）。
            1.0=不缩放（基准）；>1 降温摊平 HMM 后验，验证 C1 不退化。
    """
    if not REAL_DEPS_OK:
        print(f"[real] 依赖导入失败: {_REAL_IMPORT_ERROR}")
        print("[real] 请确认 zephyr.regime / zephyr.data 模块可用")
        sys.exit(1)

    # 抑制 hmmlearn 收敛警告（fit 仍完成，仅噪音）
    warnings.filterwarnings("ignore", message=".*not converging.*")
    logging.getLogger("hmmlearn").setLevel(logging.ERROR)

    enable_full_risk = (risk_mode == "full")
    enable_overlay = (overlay == "on")
    print(f"[real] 配置: risk_mode={risk_mode}, overlay={overlay} "
          f"(enable_full_risk={enable_full_risk}, enable_overlay={enable_overlay})")

    print(f"[real] 加载篮子后复权日K（{len(BASKET_SYMBOLS)} 大盘股, "
          f"{REAL_START}~{REAL_END}）...")
    data = load_basket_hfq(BASKET_SYMBOLS, REAL_START, REAL_END)
    signals = make_equal_weight_signals(data)
    print(f"[real] 篮子: {len(data)} 行, {signals.shape[1]} 标的, "
          f"{signals.index.min()}~{signals.index.max()}")

    print("[real] 构建 RegimeFeatureBuilder + walk-forward HMM Shrinkage schedule...")
    print(f"[real]   （指数K线→6特征→季度重拟合5年训练→逐日detect，预计2-3分钟，T={temperature}）")
    data_loader = RegimeDataLoader(
        data_load_start=DATA_LOAD_START, backtest_end=REAL_END,
    )
    builder = RegimeFeatureBuilder(
        backtest_start=REAL_START, backtest_end=REAL_END, data_load_start=DATA_LOAD_START,
        enable_full_risk=enable_full_risk, enable_overlay=enable_overlay,
        enable_phase2c=True, data_loader=data_loader,
    )
    detector = RegimeDetector(shrinkage_enabled=True, temperature=temperature)
    schedule = builder.build_shrinkage_schedule(detector, train_years=5, detect_window=60)
    vals = np.array(list(schedule.values()))
    print(f"[real] Shrinkage schedule: {len(schedule)} 日, "
          f"均值={vals.mean():.3f}, <1.0占比={100*(vals<1.0).mean():.1f}%")
    provider = ScheduleShrinkageProvider(schedule)

    print("[real] 运行 C1ShrinkageComparator.compare()（开/关对比）...")
    comparator = C1ShrinkageComparator()
    config = BacktestConfig(
        initial_capital=Decimal("1000000"),
        commission_rate=Decimal("0.0003"),
        slippage_bps=Decimal("1"),
        risk_free_rate=0.02,
    )
    result = comparator.compare(
        data=data,
        signals=signals,
        shrinkage_provider=provider,
        backtest_config=config,
        strategy_name=f"c1-real-2015-2026-risk{risk_mode}-ovl{overlay}",
        initial_capital=Decimal("1000000"),
    )
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="C1 Shrinkage 开/关对比验证（11_regime_backtest_validation_plan Phase 1）"
    )
    parser.add_argument(
        "--mode", choices=["mock", "real"], default="mock",
        help="mock=合成数据冒烟（默认）；real=真实数据 2015-2026",
    )
    parser.add_argument(
        "--risk-mode", choices=["simple", "full"], default="full",
        help="risk参数模式：simple=Phase1简化版(1参数#1)；full=Phase2a全量(13参数，"
             "生产默认——#ARCH-REGIME-RISK-FULL-001 C1验证不退化)",
    )
    parser.add_argument(
        "--overlay", choices=["off", "on"], default="off",
        help="overlay信号开关：off=无覆盖层(纯HMM)；on=Phase2b启用8转换",
    )
    parser.add_argument(
        "--temperature", type=float, default=1.0,
        help="HMM 概率温度缩放 T（13_regime_phase3_engineering_plan §2.2 P0-E2）：1.0=不缩放（基准）；"
             ">1 降温摊平后验验证 C1 不退化；仅 real 模式生效",
    )
    args = parser.parse_args()

    if args.mode == "mock":
        result = run_mock_smoke()
    else:
        result = run_real(risk_mode=args.risk_mode, overlay=args.overlay,
                          temperature=args.temperature)

    print_result(result, args.mode)

    # 退出码：mock 冒烟跑通=0；real 模式 C1 通过=0/否决=1
    if args.mode == "mock":
        sys.exit(0)
    else:
        sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
