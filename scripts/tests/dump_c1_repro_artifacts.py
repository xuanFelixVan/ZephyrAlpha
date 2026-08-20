#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""导出 C1 独立复现所需的全部 artifacts。

产出（写入 d:\\ZephyrAlpha\\logs\\c1_repro\\）:
  1. shrinkage_schedule.csv  — 逐日 Shrinkage 序列（regime_results），date,shrinkage
  2. basket_data_spec.json   — 10 大盘股 universe + 区间 + 数据源 + 行数
  3. c1_metrics.json         — 开/关对比四项指标原始值
  4. regime_features.csv     — HMM 6 特征矩阵（detect 消费的 X，shift(1) 后）
  5. repro_handoff.md        — 完整复现说明（代码变更/参数/数据源/命令）

用法:
  python scripts/tests/dump_c1_repro_artifacts.py
"""

from __future__ import annotations

import json
import logging
import warnings
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.c1_comparator import C1ShrinkageComparator
from zephyr.backtest.regime_validation.shrinkage_provider import ScheduleShrinkageProvider
from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.regime.core.regime_detector import RegimeDetector
from zephyr.regime.regime_feature_builder import (
    BREADTH_INDEX,
    CROSS_ASSET_INDICES,
    FEATURE_NAMES,
    MARKET_PROXY,
    RegimeFeatureBuilder,
)

# ── 与 run_c1_shrinkage_validation.py 完全一致的参数 ──────────────────
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
BASKET_NAMES = {
    "600000": "浦发银行",
    "000001": "平安银行",
    "600519": "贵州茅台",
    "600036": "招商银行",
    "601318": "中国平安",
    "000651": "格力电器",
    "600276": "恒瑞医药",
    "000858": "五粮液",
    "600887": "伊利股份",
    "601166": "兴业银行",
}
REAL_START = "2015-01-01"
REAL_END = "2026-06-30"
DATA_LOAD_START = "2010-01-01"

OUTPUT_DIR = Path(r"d:\ZephyrAlpha\logs\c1_repro")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    warnings.filterwarnings("ignore", message=".*not converging.*")
    logging.getLogger("hmmlearn").setLevel(logging.ERROR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. 加载篮子数据 + dump 规格 ──────────────────────────────────
    print("[dump] 1/5 加载篮子后复权日K...")
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
    basket_df = pd.DataFrame(rows, columns=["trade_date", "symbol", "open", "high", "low", "close", "volume"])
    basket_df["trade_date"] = pd.to_datetime(basket_df["trade_date"])
    for c in ["open", "high", "low", "close", "volume"]:
        basket_df[c] = pd.to_numeric(basket_df[c], errors="coerce")
    basket_df = basket_df.rename(columns={"trade_date": "date"})
    basket_df = basket_df.set_index(["symbol", "date"]).sort_index()

    spec = {
        "universe": [{"symbol": s, "name": BASKET_NAMES.get(s, "")} for s in BASKET_SYMBOLS],
        "n_symbols": len(BASKET_SYMBOLS),
        "date_range": [
            str(basket_df.index.get_level_values("date").min()),
            str(basket_df.index.get_level_values("date").max()),
        ],
        "n_rows": len(basket_df),
        "source_table": hfq_table,
        "adjustment": "后复权 (hfq)",
        "fields": ["open", "high", "low", "close", "volume"],
        "clickhouse": "172.24.30.100:9000 / c1_market",
    }
    (OUTPUT_DIR / "basket_data_spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[dump]   篮子: {len(basket_df)} 行, {len(BASKET_SYMBOLS)} 标的")

    # ── 2. 构建 Shrinkage schedule + dump CSV ────────────────────────
    print("[dump] 2/5 构建 RegimeFeatureBuilder + walk-forward Shrinkage schedule...")
    builder = RegimeFeatureBuilder(backtest_start=REAL_START, backtest_end=REAL_END, data_load_start=DATA_LOAD_START)
    detector = RegimeDetector(shrinkage_enabled=True)
    schedule = builder.build_shrinkage_schedule(detector, train_years=5, detect_window=60)

    sched_df = pd.DataFrame([{"date": dt, "shrinkage": v} for dt, v in schedule.items()]).sort_values("date")
    sched_df.to_csv(OUTPUT_DIR / "shrinkage_schedule.csv", index=False)
    print(f"[dump]   Shrinkage: {len(sched_df)} 日, 均值={sched_df['shrinkage'].mean():.4f}")

    # ── 3. dump HMM 6 特征（shift(1) 后，detect 实际消费的 X）────────
    print("[dump] 3/5 dump HMM 6 特征矩阵...")
    features = builder.build_features()
    features_shifted = features.shift(1).loc[REAL_START:REAL_END]
    features_shifted.to_csv(OUTPUT_DIR / "regime_features.csv")
    print(f"[dump]   特征: {len(features_shifted)} 行 × {len(FEATURE_NAMES)} 列")

    # ── 4. 运行 C1 对比 + dump 指标 ──────────────────────────────────
    print("[dump] 4/5 运行 C1 开/关对比...")
    signals = pd.DataFrame(
        {sym: 1.0 for sym in sorted(basket_df.index.get_level_values("symbol").unique())},
        index=pd.DatetimeIndex(basket_df.index.get_level_values("date").unique().sort_values(), name="date"),
    )
    # 回测用的 data 需要 MultiIndex(symbol, date) + open/high/low/close/volume
    provider = ScheduleShrinkageProvider(schedule)
    comparator = C1ShrinkageComparator()
    config = BacktestConfig(
        initial_capital=Decimal("1000000"),
        commission_rate=Decimal("0.0003"),
        slippage_bps=Decimal("1"),
        risk_free_rate=0.02,
    )
    result = comparator.compare(
        data=basket_df,
        signals=signals,
        shrinkage_provider=provider,
        backtest_config=config,
        strategy_name="c1-repro-dump",
        initial_capital=Decimal("1000000"),
    )

    metrics = {
        "passed": result.passed,
        "veto_reason": result.veto_reason,
        "summary": result.summary,
        "metrics": [
            {
                "name": v.name,
                "baseline_value": v.baseline_value,
                "experiment_value": v.experiment_value,
                "passed": v.passed,
                "detail": v.detail,
            }
            for v in result.metric_verdicts
        ],
        "backtest_config": {
            "initial_capital": "1000000",
            "commission_rate": "0.0003",
            "slippage_bps": "1",
            "risk_free_rate": 0.02,
        },
    }
    (OUTPUT_DIR / "c1_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[dump]   C1 passed={result.passed}")

    # ── 5. 生成复现说明 ──────────────────────────────────────────────
    print("[dump] 5/5 生成复现说明...")
    handoff = f"""# C1 独立复现交接文档

> 生成时间: {datetime.now().isoformat()}
> 生成脚本: scripts/tests/dump_c1_repro_artifacts.py

## 1. 验证目标

C1 开/关对比（11_regime_backtest_validation_plan Phase 1 核心验证）：
- **关**（基准）: Shrinkage=1.0（满部署，无 regime 节流）
- **开**（实验）: Shrinkage=regime 检测器输出（HMM ConfidenceSignal × feature_risk）
- 一票否决：四项指标任一不通过 = regime 不部署

## 2. 被测代码变更（关键！）

### 文件: src/zephyr/regime/core/regime_detector.py

**变更**: 从 `_compute_confidence_signal` 移除 `state_risk_factor` 乘法。

**变更前** (有 bug):
```python
def _compute_confidence_signal(self, probs):
    base = ...  # max(P) 四档映射
    state_risk = _STATE_RISK_FACTORS.get(probs.dominant_regime, 1.0)  # ← 移除
    rarity = ...  # 稀有态折扣
    return base * state_risk * rarity  # ← 三项乘
```

**变更后** (当前):
```python
def _compute_confidence_signal(self, probs):
    base = ...  # max(P) 四档映射
    rarity = ...  # 稀有态折扣
    return base * rarity  # ← 两项乘，无 state_risk
```

**移除原因**:
1. HMM 标签任意性：无监督 HMM 的 r1-r9 标签在 walk-forward 各季 refit 间无一致语义
2. 永久中性态惩罚：r4/r5/r6（震荡态）state_risk=0.70-0.90，A 股长期震荡 → 平时永久压仓

危机保护由 RiskSignal 的 feature_risk（vol_pct + slope）承担。

### ConfidenceBands（当前校准值，适应 9 态 HMM 概率分散）:
```python
_CONFIDENCE_BANDS = (
    (0.50, 1.0),   # top1 ≥50% → 满部署
    (0.30, 0.9),   # 30-50% → 轻度收缩
    (0.15, 0.8),   # 15-30% → 中度收缩
    (0.0, 0.7),    # <15% → 强收缩（下限0.7）
)
```

### feature_risk 阈值（RegimeFeatureBuilder._build_feature_risk）:
```
vol_pct > 0.90 + 下跌(slope<0) → RiskSignal=0.30（危机）
vol_pct > 0.90                 → 0.60（极端高波）
vol_pct > 0.75 + 下跌          → 0.50（高波+下跌）
vol_pct > 0.75                 → 0.80（高波）
else                           → 1.00（正常，不干预）
```

## 3. 数据规格

### 可交易 universe（篮子）:
{chr(10).join(f"- {s} {BASKET_NAMES.get(s, '')}" for s in BASKET_SYMBOLS)}

- 区间: {REAL_START} ~ {REAL_END}
- 复权: 后复权 (hfq)
- 数据源: ClickHouse {hfq_table} (172.24.30.100:9000)
- 字段: open, high, low, close, volume
- 行数: {len(basket_df)}

### Regime 特征数据源（HMM 6 特征）:
- 市场代理: {MARKET_PROXY}（沪深300）
- 跨资产相关性: {CROSS_ASSET_INDICES}（沪深300/中证500/创业板指）
- 涨跌家数: {BREADTH_INDEX}（深证综指）
- 特征加载起始: {DATA_LOAD_START}（walk-forward 5年训练历史）
- 数据源表: c1_market.kline_index（market_index_kline 品类）

### HMM 6 特征（X 矩阵列序）:
{chr(10).join(f"{i + 1}. {f}" for i, f in enumerate(FEATURE_NAMES))}

## 4. 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| walk-forward 频率 | QE（季末） | 46 个季度边界 |
| 训练窗口 | 5 年 | 滚动训练 |
| detect_window | 60 日 | trailing 特征窗口 |
| HMM n_states | 9 | 趋势×波动率 3×3 |
| HMM n_init | 3 | 多次拟合取最优 log-likelihood |
| HMM n_iter | 100 | EM 迭代上限 |
| HMM covariance_type | full | 全协方差 |
| 特征标准化 | RobustScaler | 每季 fit（PIT: 只用训练窗口） |
| Shrinkage EMA α | 0.15 | 半衰期约4天，抑制四档跳变 |
| detect PIT | features.shift(1) | detect(t) 只用 ≤ t-1 特征 |

## 5. 复现命令

### 方式 A: 用本项目脚本重跑全链路
```powershell
$env:HF_HUB_OFFLINE=1; $env:PYTHONUTF8=1
python scripts/tests/run_c1_shrinkage_validation.py --mode real
```

### 方式 B: 用 dump 的 Shrinkage 序列 + 自己的回测引擎
1. 读取 `shrinkage_schedule.csv`（date,shrinkage 两列）
2. 加载 10 大盘股后复权日K（同上 universe + 区间）
3. 等权信号（每标的每天 weight=1.0，引擎内归一化）
4. 基准组: Shrinkage=1.0；实验组: 用 CSV 中的 shrinkage 序列
5. 对比 Sharpe / MaxDD / Calmar / Turnover

### 方式 C: 从特征开始全链路重跑
1. 读取 `regime_features.csv`（已 shift(1)，PIT 满足）
2. walk-forward 季度 fit HMM（同上参数）
3. detect → Shrinkage schedule
4. 与 dump 的 `shrinkage_schedule.csv` 对比

## 6. 预期结果（我跑出的）

| 指标 | 关（基准） | 开（regime） | 判定 |
|------|-----------|-------------|------|
| Sharpe | 0.3678 | 0.3474 | ✅ 通过 |
| MaxDD | 0.2221 | 0.1485 | ✅ 通过 |
| Calmar | 0.2918 | 0.3694 | ✅ 通过 |
| Turnover | 2.2722/yr | 2.5522/yr | ✅ 通过 |

Shrinkage 均值=0.873, <1.0 占比=99.5%

## 7. 产出文件清单

| 文件 | 内容 |
|------|------|
| shrinkage_schedule.csv | 逐日 Shrinkage 序列（{len(sched_df)} 日） |
| basket_data_spec.json | 篮子数据规格（universe/区间/行数） |
| c1_metrics.json | C1 四项指标原始值 + 判定 |
| regime_features.csv | HMM 6 特征矩阵（shift(1) 后） |
| repro_handoff.md | 本文档 |
"""
    (OUTPUT_DIR / "repro_handoff.md").write_text(handoff, encoding="utf-8")

    print(f"\n[dump] 完成！产出目录: {OUTPUT_DIR}")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {f.name} ({f.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
