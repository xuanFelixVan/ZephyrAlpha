# [BLUEPRINT] MOD-BT-037 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.pilot_002_ma_cross
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C3 翻译试点；C4 快筛批测（is_sharpe 回填 strategy_screen）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日信号用 ≤T-1 收盘均线，T+1 收盘起算收益）；成本=冻结土规（佣金 2.5bp+印花 10bp 卖+滑点 5bp）；差异声明完整；持仓≤2 等权（原文 max_hold_stocknum=2）
# [MODIFY-GUARD] tests/backtest/test_translated_pilot_002.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_translated_pilot_002.py
# [A_module] module_id=MOD-BT-037 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C3 翻译试点第 2 条（第 1 条完成）：MA5/MA10 金叉死叉（聚宽 kuanke 模板→本项目权重函数）。

原文（2020年度精选策略/90，kuanke wizard 框架模板）:
  池=沪深300 成分过滤 ST/停牌/退市/涨停；每日开盘判断：MA5 上穿 MA10（金叉）→买入，
  MA5 下穿 MA10（死叉）→卖出；最多持 2 只等权（by_cap_mean）；佣金万 3 双边+印花千 1+滑点 0.02。
  样板说明：原文 454 行中约 400 行为 kuanke 框架空过滤器（financial/situation/pattern 全空壳），
  真实信号=MA_judge_jincha(s,5,10)/MA_judge_sicha(s,5,10) 两条。

译文（本项目实现）:
  池=沪深300 成分（index_constituent 快照，差异 D1）；信号=T-1 收盘 MA5/MA10 金叉死叉（PIT：
  T 日开盘执行用 ≤T-1 数据，等价于原文"开盘价信号"）；持仓状态机逐日维护，≤2 只等权；
  收益用 kline_daily_hfq 后复权 close，T+1 收盘起算；成本=佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp（冻结土规）。

翻译差异声明:
  D1 股票池: 原文沪深300 成分（聚宽实时成分） → index_constituent 表最新成分快照（历史成分回溯未核，
     成分漂移影响待 C4 批测统一口径）
  D2 执行时点: 原文开盘价成交 → 译文 T+1 收盘成交（向量化引擎口径，全 C4 批次统一，可比性保持）
  D3 滑点: 原文固定 0.02 元 → 译文 5bp 比例滑点（冻结土规线内）
  D4 因子登记: MA5/MA10 属技术指标（OHLCV 计算工具），按 factor_registry 定义"因子=alpha 来源，
     与技术指标正交"——不登记 factor_registry，翻译无新增因子。
  D5 框架样板: 原文约 400 行框架空壳（wizard 模板未启用的过滤器）不翻译——翻译只承载真实逻辑。
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
_MA_SHORT, _MA_LONG = 5, 10
_MAX_HOLD = 2


def _load_data(start: str, end: str) -> tuple[pd.DataFrame, set[str]]:
    """后复权行情（池=沪深300 最新成分）。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    from clickhouse_driver import Client

    c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)), user=cfg.get("user", "default"),
               password=cfg.get("password", ""), connect_timeout=5)
    px = pd.DataFrame(c.execute(
        f"SELECT trade_date, symbol, toFloat64(close) AS close FROM c1_market.kline_daily_hfq "
        f"WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND close > 0"
    ), columns=["trade_date", "symbol", "close"])
    hs300: set[str] = set()
    try:
        # 成分股代码带后缀（000001.SZ），行情表为纯 6 位——取前 6 位归一；
        # 取最新有效快照（valid_to IS NULL 或最大 trade_date 的成分集合）
        rows = c.execute(
            "SELECT symbol_canonical FROM c1_market.index_constituent "
            "WHERE index_code = '000300.SH' AND valid_to IS NULL")
        hs300 = {(r[0] or "")[:6] for r in rows if r[0]}
        if not hs300:
            latest = c.execute(
                "SELECT max(trade_date) FROM c1_market.index_constituent WHERE index_code = '000300.SH'")[0][0]
            rows = c.execute(
                f"SELECT symbol FROM c1_market.index_constituent "
                f"WHERE index_code = '000300.SH' AND trade_date = '{latest}'")
            hs300 = {(r[0] or "")[:6] for r in rows if r[0]}
        logger.info("沪深300 成分快照: %d 只", len(hs300))
    except Exception as exc:  # noqa: BLE001 表结构差异时退化为全 A 池（差异声明 D1 降级）
        logger.warning("index_constituent 不可用(%s)，池退化为全 A（D1 降级）", exc)
    if px.empty:
        raise RuntimeError("kline_daily_hfq 数据缺失")
    px["trade_date"] = pd.to_datetime(px["trade_date"])
    return px, hs300


def generate_weights(px: pd.DataFrame, hs300: set[str], start: str, end: str) -> pd.DataFrame:
    """逐日权重矩阵：MA5/10 金叉死叉状态机，持仓≤2 等权。信号=T-1 收盘（PIT）。"""
    closes = px.pivot(index="trade_date", columns="symbol", values="close").sort_index()
    if hs300:
        closes = closes[[c for c in closes.columns if c in hs300]]
    ma_s = closes.rolling(_MA_SHORT).mean()
    ma_l = closes.rolling(_MA_LONG).mean()
    golden = (ma_s > ma_l) & (ma_s.shift(1) <= ma_l.shift(1))   # 金叉日
    death = (ma_s < ma_l) & (ma_s.shift(1) >= ma_l.shift(1))    # 死叉日
    # 金叉强度排序（MA5-MA10 差值标准化），同日多金叉时取最强 2 只
    strength = ((ma_s - ma_l) / ma_l).where(golden)

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    holdings: list[str] = []
    g_idx = golden.shift(1).reindex(dates).fillna(False)   # T 日执行用 T-1 信号
    d_idx = death.shift(1).reindex(dates).fillna(False)
    s_idx = strength.shift(1).reindex(dates)

    for dt in dates:
        for s in list(holdings):
            if bool(d_idx.loc[dt, s]) if s in d_idx.columns else True:
                holdings.remove(s)
        if len(holdings) < _MAX_HOLD:
            cand = s_idx.loc[dt].dropna()
            cand = cand[~cand.index.isin(holdings)].sort_values(ascending=False)
            for s in cand.index[: _MAX_HOLD - len(holdings)]:
                holdings.append(s)
        if holdings:
            weights.loc[dt, holdings] = 1.0 / len(holdings)
    return weights


def run_backtest(weights: pd.DataFrame, px: pd.DataFrame) -> dict[str, Any]:
    """T+1 收盘执行向量化回测（口径与 pilot_001 完全一致，保证 C4 批测可比）。"""
    closes = px.pivot(index="trade_date", columns="symbol", values="close").reindex(
        weights.index.union(weights.index)).ffill()
    rets = closes.pct_change()
    w = weights.reindex(closes.index).ffill().fillna(0.0)
    gross = (w.shift(1) * rets).sum(axis=1).fillna(0.0)
    turnover = (w - w.shift(1)).abs().sum(axis=1).fillna(0.0) / 2.0
    cost = turnover * (_COMMISSION_BP * 2 + _STAMP_BP + _SLIPPAGE_BP * 2) / 10000.0
    net = gross - cost
    equity = (1.0 + net).cumprod()
    years = max(len(net) / 244.0, 1e-9)
    sharpe = float(net.mean() / net.std() * np.sqrt(244)) if net.std() > 0 else 0.0
    mdd = float((equity / equity.cummax() - 1.0).min())
    return {
        "days": int(len(net)), "sharpe": round(sharpe, 3),
        "ann_return": round(float(equity.iloc[-1] ** (1 / years) - 1.0), 4),
        "max_drawdown": round(mdd, 4),
        "avg_turnover_1side": round(float(turnover.mean()), 4),
        "equity_final": round(float(equity.iloc[-1]), 4),
        "hold_days_pct": round(float((weights.sum(axis=1) > 0).mean()), 3),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="C3 试点第 2 条：MA5/10 金叉死叉（翻译实现）")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2023-12-31")
    args = parser.parse_args()
    load_start = str(pd.Timestamp(args.start) - pd.Timedelta(days=60))[:10]

    px, hs300 = _load_data(load_start, args.end)
    logger.info("数据: %d 行，池 %d 只（D1%s）", len(px), len(hs300) or "全A",
                "成分快照" if hs300 else "降级")
    weights = generate_weights(px, hs300, args.start, args.end)
    logger.info("权重矩阵: %d 日 × %d 标的", *weights.shape)
    stats = run_backtest(weights, px)
    print(json.dumps({
        "pilot": "002_ma_cross", "source": "2020年度精选策略/90",
        "window": [args.start, args.end],
        "translation_diffs": ["D1 池=成分快照", "D2 T+1收盘执行", "D3 滑点5bp",
                              "D4 MA系技术指标不入因子库", "D5 框架空壳不翻译"],
        "stats": stats,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
