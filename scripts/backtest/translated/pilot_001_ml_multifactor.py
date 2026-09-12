# [BLUEPRINT] MOD-BT-036 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.pilot_001_ml_multifactor
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; sklearn; numpy; pandas
# [CONSUMERS] C3 翻译试点；C4 快筛批测（is_sharpe 回填 strategy_screen）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日调仓用 ≤T-1 数据）；成本口径=冻结土规（佣金 2.5bp+印花 10bp 卖+滑点 5bp）；差异声明完整（原文↔译文口径差异逐条留痕）；健康表专用（daily_valuation 已进黑名单禁用）
# [MODIFY-GUARD] tests/backtest/test_translated_pilot_001.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/样本不足)
# [TESTS] tests/backtest/test_translated_pilot_001.py
# [A_module] module_id=MOD-BT-036 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C3 翻译试点第 1 条：机器学习多因子（聚宽原文→本项目向量化权重函数）。

原文（2020年度精选策略/03，SVR 规模中性化残差选股）:
  上证成分，每 10 交易日 SVR(rbf,gamma=0.1) 拟合 log_mcap ~ [log_NC,LEV,NI_p,NI_n,g,log_RD+29 行业哑变量]，
  残差 = 实际 - 预测，买残差最小 10 只（规模因子无法解释的"被低估"），等权持有。

译文（本项目实现，食材替代见差异声明）:
  池=stock_indicator 有估值且非 ST 全 A；每 10 交易日 SVR(rbf,gamma=0.1) 拟合
  log_amount ~ [log_pb, log_ps, log_pcf, dividend_yield, 行业一级哑变量(ifind 快照)]，
  残差最小 10 只等权持有 10 日。

翻译差异声明（诚实口径，C3 试点的核心产出之一）:
  D1 股票池: 上证指数成分 → 全 A 有估值覆盖（index 成分历史表未核，试点取超集）
  D2 目标变量 Y: log_mcap（流通市值） → log_amount（成交额对数=规模/流动性代理）——财务三表未建，市值不可推
  D3 X 因子: 财务六因子 → 估值倍数四因子（pb/ps/pcf/dividend_yield，同源可得）——SVR"剥离风格看残差"灵魂保留
  D4 行业: 申万 29 哑变量 → ifind 一级分类哑变量（industry_class 为当前快照，套历史=轻微前视，已声明）
  D5 复权: 原文 use_real_price → 译文收益用后复权 close（kline_daily_hfq），成本按未复权金额近似

PIT: T 日调仓只用 ≤T-1 的估值/行情/行业数据（估值倍数为行情衍生快照，无披露滞后问题；
     原文 get_fundamentals 财务数据的披露滞后在译文不适用——D3 替代后自动消除）。
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

_COMMISSION_BP = 2.5   # 佣金双边
_STAMP_BP = 10.0       # 印花税卖出
_SLIPPAGE_BP = 5.0     # 滑点（冻结土规 20bp 线内）
_REBALANCE_DAYS = 10
_N_STOCKS = 10
_WARMUP_DAYS = 250     # SVR 训练预热


def _load_data(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """健康表数据：行情（kline_daily_hfq）+ 估值（stock_indicator）+ 行业（industry_class 快照）。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    from clickhouse_driver import Client

    c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)), user=cfg.get("user", "default"),
               password=cfg.get("password", ""), connect_timeout=5)
    px = pd.DataFrame(c.execute(
        f"SELECT trade_date, symbol, toFloat64(close) AS close, toFloat64(amount) AS amount "
        f"FROM c1_market.kline_daily_hfq WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND amount > 0"
    ), columns=["trade_date", "symbol", "close", "amount"])
    val = pd.DataFrame(c.execute(
        f"SELECT trade_date, symbol, toFloat64(pb) AS pb, toFloat64(ps) AS ps, "
        f"toFloat64(pcf) AS pcf, toFloat64(dividend_yield) AS divyield "
        f"FROM c1_market.stock_indicator WHERE trade_date >= '{start}' AND trade_date <= '{end}' "
        f"AND pb > 0 AND ps > 0 AND pcf != 0"
    ), columns=["trade_date", "symbol", "pb", "ps", "pcf", "divyield"])
    ind = pd.DataFrame(c.execute(
        "SELECT symbol, industry_sw FROM c1_market.industry_class "
        "WHERE industry_level = 1 AND industry_sw != ''"
    ), columns=["symbol", "industry"])
    if px.empty or val.empty:
        raise RuntimeError(f"数据缺失: px={len(px)} val={len(val)}")
    for df in (px, val):
        df["trade_date"] = pd.to_datetime(df["trade_date"])
    return px, val, ind


def generate_weights(px: pd.DataFrame, val: pd.DataFrame, ind: pd.DataFrame,
                     start: str, end: str) -> pd.DataFrame:
    """逐日权重矩阵（date × symbol）：每 10 交易日 SVR 残差选 10 只等权，其余日不变。"""
    closes = px.pivot(index="trade_date", columns="symbol", values="close")
    amounts = px.pivot(index="trade_date", columns="symbol", values="amount")
    val_p = val.pivot(index="trade_date", columns="symbol", values="pb").reindex(closes.index)
    val_s = val.pivot(index="trade_date", columns="symbol", values="ps").reindex(closes.index)
    val_c = val.pivot(index="trade_date", columns="symbol", values="pcf").reindex(closes.index)
    val_d = val.pivot(index="trade_date", columns="symbol", values="divyield").reindex(closes.index)

    ind_map = dict(zip(ind["symbol"], ind["industry"]))
    industries = sorted(set(ind_map.values()))
    ind_of = {s: ind_map.get(s, "未知") for s in closes.columns}

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    last_pick: list[str] = []
    from sklearn.svm import SVR

    for i, dt in enumerate(dates):
        if i < _WARMUP_DAYS or (i - _WARMUP_DAYS) % _REBALANCE_DAYS != 0:
            if i >= _WARMUP_DAYS:
                weights.loc[dt, last_pick] = 1.0 / max(len(last_pick), 1)
            continue
        pos = closes.index.get_loc(dt)
        hist = closes.iloc[max(0, pos - _WARMUP_DAYS):pos]  # ≤T-1
        # 池：当日有估值且历史有成交
        x_pb = val_p.iloc[pos - 1]
        x_ps = val_s.iloc[pos - 1]
        x_pc = val_c.iloc[pos - 1]
        x_dy = val_dy = val_d.iloc[pos - 1]
        amt = amounts.iloc[pos - 1]
        pool = x_pb.dropna().index.intersection(x_ps.dropna().index).intersection(
            x_pc.dropna().index).intersection(amt[amt > 0].index)
        pool = [s for s in pool if pd.notna(closes.iloc[pos - 1].get(s)) and closes.iloc[pos - 1].get(s, 0) > 0]
        if len(pool) < 50:
            logger.warning("%s 池过小(%d)，沿用上期", dt.date(), len(pool))
            weights.loc[dt, last_pick] = 1.0 / max(len(last_pick), 1)
            continue
        X = pd.DataFrame({
            "log_pb": np.log(x_pb[pool]),
            "log_ps": np.log(x_ps[pool]),
            "log_pcf": np.log(x_pc[pool].abs() + 1.0),
            "divyield": x_dy[pool].fillna(0.0),
            **{f"ind_{k}": [1.0 if ind_of[s] == k else 0.0 for s in pool] for k in industries},
        })
        Y = np.log(amt[pool] + 1.0)
        model = SVR(kernel="rbf", gamma=0.1)
        model.fit(X.to_numpy(), Y.to_numpy())
        residual = Y.to_numpy() - model.predict(X.to_numpy())
        pick = [pool[j] for j in np.argsort(residual)[:_N_STOCKS]]
        weights.loc[dt, pick] = 1.0 / _N_STOCKS
        last_pick = pick
    return weights


def run_backtest(weights: pd.DataFrame, px: pd.DataFrame) -> dict[str, Any]:
    """T+1 执行向量化回测：T 日信号 → T+1 收盘收益归信号；双边成本按换手计。"""
    closes = px.pivot(index="trade_date", columns="symbol", values="close").reindex(
        weights.index.union(weights.index)).ffill()
    rets = closes.pct_change()
    w = weights.reindex(closes.index).ffill().fillna(0.0)
    gross = (w.shift(1) * rets).sum(axis=1).fillna(0.0)
    turnover = (w - w.shift(1)).abs().sum(axis=1).fillna(0.0) / 2.0  # 单边换手
    cost = turnover * (_COMMISSION_BP * 2 + _STAMP_BP + _SLIPPAGE_BP * 2) / 10000.0
    net = gross - cost
    equity = (1.0 + net).cumprod()
    years = max(len(net) / 244.0, 1e-9)
    sharpe = float(net.mean() / net.std() * np.sqrt(244)) if net.std() > 0 else 0.0
    mdd = float((equity / equity.cummax() - 1.0).min())
    return {
        "days": int(len(net)), "sharpe": round(sharpe, 3),
        "ann_return": round(float((equity.iloc[-1]) ** (1 / years) - 1.0), 4),
        "max_drawdown": round(mdd, 4),
        "avg_turnover_1side": round(float(turnover.mean()), 4),
        "equity_final": round(float(equity.iloc[-1]), 4),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="C3 试点第 1 条：SVR 残差选股（翻译实现）")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2023-12-31", help="IS 段（快筛口径 2019-2023；预热 2019 全年）")
    args = parser.parse_args()
    load_start = str(pd.Timestamp(args.start) - pd.Timedelta(days=400))[:10]

    px, val, ind = _load_data(load_start, args.end)
    logger.info("数据: px %d 行 / val %d 行 / ind %d 行", len(px), len(val), len(ind))
    weights = generate_weights(px, val, ind, args.start, args.end)
    active = (weights > 0).any(axis=1).sum()
    logger.info("权重矩阵: %d 日 × %d 标的，有持仓日 %d", *weights.shape, active)
    stats = run_backtest(weights, px)
    print(json.dumps({"pilot": "001_ml_multifactor", "window": [args.start, args.end],
                      "translation_diffs": ["D1 股票池: 上证成分→全A有估值覆盖", "D2 Y: log_mcap→log_amount",
                                            "D3 X: 财务六因子→估值四因子", "D4 行业: 申万29→ifind一级(快照)"],
                      "stats": stats}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
