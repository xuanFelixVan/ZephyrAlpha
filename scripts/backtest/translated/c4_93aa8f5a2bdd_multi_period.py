# [BLUEPRINT] MOD-BT-072 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_93aa8f5a2bdd_multi_period
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
# [A_module] module_id=MOD-BT-072 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 072: 多期限均线因子 OLS 预测选股（原文: 2020年度精选策略/15 基于多期限的选股策略（一））。

原文逻辑: 池=上证180（000010.XSHG）；每 7 个交易日调仓；对每只股票用 12 个期限因子
  At=MA_n/最新close（n∈{3,5,10,20,30,60,90,120,180,240,270,300}）；以之前 25 个周度样本
  做 LinearRegression 拟合下周收益 rf，取预测收益最高 5 只等权。
  原文 rf 计算存在疑似列错位 bug（count=5 的 open/close 两列按列序均取到 open），
  按纪律照原样转录：rf=(open[t-2]-open[t-1])/open[t-1] 语义（周度 open 对 open 变化）。
译文实现: 12 因子整面向量化；训练集=过去 25 个周度截面（每周回退 7 自然日近似 5 交易日）；
  numpy lstsq 逐股 OLS（常数项+12 因子）；预测值降序前 5 等权。
因子拆解: 多期限均线比值因子组（12 个）——价格衍生因子组，公开方法论不登记 factor_registry。
翻译差异声明:
  D1 股票池: 上证180 成分快照（index_constituent 000010.SH，缺失时降级声明）
  D2 执行时点: 原文开盘 → T 日收盘
  D3 rf 列错位 bug 保真转录（UNCERTAIN 已在原文卡标注）
  D4 因子登记: 公开均线因子组不登记
  D5 框架样板: sklearn LinearRegression → numpy lstsq（数值等价）

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import emit, filter_st, load_index_constituents, load_px, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-93aa8f5a2bdd"
WINDOW_KIND = "stock"
_PERIODS = [3, 5, 10, 20, 30, 60, 90, 120, 180, 240, 270, 300]
_TRAIN_N, _TOP_N, _REBAL = 25, 5, 7


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=900))[:10]
    px = load_px(load_start, end, fields=("close", "open"))
    uni = load_index_constituents("000010.SH", start, end)
    px = px[px["symbol"].isin(uni)] if uni else px
    close = filter_st(wide(px, "close").ffill(), load_st_flags(load_start, end))
    opn = wide(px, "open").ffill().reindex(close.index).reindex(columns=close.columns)

    factors = {n: close.rolling(n).mean() / close for n in _PERIODS}
    weekly_ret = opn.pct_change(5)  # 周度 open→open 收益（rf bug 保真：open 对 open）

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    f_pred = pd.DataFrame(index=dates, columns=close.columns, dtype=float)
    for k in range(_TRAIN_N * _REBAL, len(dates)):
        dt = dates[k]
        if k % _REBAL != 0:
            continue
        X_rows, y_rows, syms = [], [], []
        for j in range(1, _TRAIN_N + 1):
            kd = dates[k - j * _REBAL]
            fv = np.array([factors[n].loc[kd] for n in _PERIODS]).T  # (c, 12)
            yv = weekly_ret.shift(-_REBAL).loc[kd] if (kd in weekly_ret.index) else None
            if yv is None:
                continue
            X_rows.append(fv)
            y_rows.append(yv.values)
        if not X_rows:
            continue
        X = np.concatenate(X_rows, axis=0)
        y = np.concatenate(y_rows, axis=0)
        mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
        X, y = X[mask], y[mask]
        if len(y) < _PERIODS.__len__() + 2:
            continue
        cur = np.array([factors[n].shift(1).loc[dt] for n in _PERIODS]).T  # (c,12) 截至昨日
        design = np.concatenate([np.ones((len(X), 1)), X], axis=1)
        beta, *_ = np.linalg.lstsq(design, y, rcond=None)
        cur_d = np.concatenate([np.ones((cur.shape[0], 1)), cur], axis=1)
        pred = pd.Series(cur_d @ beta, index=close.columns)
        f_pred.loc[dt] = pred
        picks = list(pred.dropna().sort_values(ascending=False).index)[:_TOP_N]
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 上证180快照", "D2 收盘口径", "D3 rf bug保真",
                                               "D4 公开因子组不登记", "D5 lstsq等价"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
