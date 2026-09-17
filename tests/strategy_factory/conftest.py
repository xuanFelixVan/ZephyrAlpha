"""S-OWNER-001 测试夹具——合成面板（零 DB 依赖，测试隔离铁律）。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.strategy_factory.owner_band_t.data_loader import aggregate_etf_daily


def make_synthetic_panel(n_days: int = 500, seed: int = 7) -> dict:
    """合成面板: 指数日线 + ETF 日线(由合成 60min 聚合) + regime 快照。

    结构保证:
      * 前 60 日近似缓涨（供 rolling 预热），随后均值回复震荡（触发 TD setup/布林）
      * ETF = 指数/1000 加微小噪声（基差），amount 单调大额（流动性 tier 稳定）
      * regime: 默认 r1 震荡（门开），中段插入 r3 高置信段（门关）
    """
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2015-01-01", periods=n_days)
    # 随机游走 + 均值回复
    ret = rng.normal(0.0003, 0.012, n_days)
    close = 3500 * np.exp(np.cumsum(ret))
    open_ = close * (1 + rng.normal(0, 0.003, n_days))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.004, n_days)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.004, n_days)))
    idx = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=days)

    # ETF 日线（执行面）: 指数/1000 加噪声
    etf_close = close / 1000 * (1 + rng.normal(0, 0.0008, n_days))
    etf_open = etf_close * (1 + rng.normal(0, 0.002, n_days))
    etf_high = np.maximum(etf_open, etf_close) * 1.002
    etf_low = np.minimum(etf_open, etf_close) * 0.998
    amount = np.full(n_days, 2.0e9) * (1 + rng.normal(0, 0.1, n_days))
    etf = pd.DataFrame(
        {
            "open": etf_open,
            "high": etf_high,
            "low": etf_low,
            "close": etf_close,
            "amount": amount,
            "n_bars": np.full(n_days, 4),
        },
        index=days,
    )

    # 合成 60min: 每日 4 根，bar0 收盘相对开盘 -0.6%（10 天一次）触发做T 动量
    rows = []
    for i, d in enumerate(days):
        o = etf_open[i]
        c = etf_close[i]
        dip = -0.006 if i % 10 == 0 else 0.001
        b0 = o * (1 + dip)
        b1 = b0 * (1 + 0.002)
        b2 = b1
        b3 = c
        for seq, px in enumerate([b0, b1, b2, b3]):
            rows.append({"trade_date": d, "bar_seq": seq, "open": px, "high": px, "low": px, "close": px, "amount": amount[i] / 4})
    hourly = pd.DataFrame(rows)

    # regime 快照: 前 1/3 无快照；中段 r3 高置信（门关）；其余 r1
    snap_start = int(n_days * 0.3)
    snap_end = int(n_days * 0.9)
    snap_days = days[snap_start:snap_end]
    dom = np.where((np.arange(snap_start, snap_end) > n_days * 0.5) & (np.arange(snap_start, snap_end) < n_days * 0.6), "r3", "r1")
    regime = pd.DataFrame(
        {"trade_date": snap_days, "dominant": dom, "confidence": np.where(dom == "r3", 0.9, 0.5)}
    )
    return {"idx": idx, "etf": etf, "hourly": hourly.set_index(["trade_date", "bar_seq"]).sort_index(), "regime": regime, "hourly_closes": hourly.groupby("trade_date")["close"].apply(list).to_dict()}


__all__ = ["make_synthetic_panel", "aggregate_etf_daily"]
