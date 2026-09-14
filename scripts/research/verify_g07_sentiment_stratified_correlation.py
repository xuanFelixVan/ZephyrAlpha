#!/usr/bin/env python
# [BLUEPRINT] MOD-SIG-142 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/28_sentiment_cycle_trading.md §3.7
# [MODULE] scripts.research.verify_g07_sentiment_stratified_correlation
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sentiment.sentiment_cycle; zephyr.data.ch_config; clickhouse-driver; numpy; pandas
# [CONSUMERS] G07 相关性验证批次（2026-09-11 Owner 立项，人工运行）；报告 docs/_working/2026-09-11-g07-sentiment-validation.md
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 只读验证脚本：不写库、不改配置、不改 src/ 任何模块；每阶段样本 ≥30 天硬门槛（不足记 fail-open 不硬凑）；主判据=§3.7.2 分层相关性（<0.3 假设成立 / 0.3-0.6 部分成立 / >0.6 组合失效）；§3.7.4 Hawkes+block-bootstrap 2000 次为增补（失败标注"增补未跑"+理由）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据行数不足/定位器导入失败 → exit 2 + stderr 说明；Hawkes 增补失败不阻断主判据（JSON 内 status=skipped+reason）
# [TESTS] (研究验证脚本，无单元测试；以 limit_up_down 真值交叉校验作数据质量门)
# [TTL] task_bound
# （G07 一次性人工验证批 2026-09-11 Owner 立项，随批归档非永久系统）
"""G07 情绪周期分层相关性验证（28 号 memo §3.7.2 主判据 + §3.7.4 增补）。

验证假设：情绪周期是所有短周期策略的共同隐形驱动 → 策略间相关性可能高于直觉。
方法：三策略日收益 × 定位器每日 SentimentPhase 标签 → 按阶段分层算两两相关矩阵 → 对比全样本。
判据（§3.7.3 三态处置）：分层后 ρ_max <0.3 假设成立；0.3-0.6 部分成立（G13 加情绪暴露硬上限）；>0.6 组合失效。

第一轮口径=信号代理收益（backtest-based，结论须标注"待实盘复核"）：
  无现成三策略历史净值（c1_backtest 无台账、account_nav_daily 空表），按 Owner 2026-09-11 立项口径
  以"各 sleeve 信号在历史日线上的次日收益合成"作代理：
    - daban（打板代理）：T 日涨停代理池（剔除 ST/一字板/不可交易）等权，T+1 收盘买、T+2 收盘卖
    - multifactor（多因子代理）：T 日成交额 top30% ∩ 60 日波动率 bottom50% 取额 top20 等权
    - event_driven（事件驱动代理）：T 日成交额 top5%（活跃度/事件热度溢出）取额 top20 等权
  涨停代理：pct_change≥9.7%（创业板/科创板 ≥19.7%，按股票代码前缀），与 limit_up_down 真值交叉校验。

定位器输入（全市场日度聚合，盘后可观测口径，与 28 号 §3.3 输入契约对齐）：
  limit_up_count/limit_down_count=ST 感知涨停代理计数（主板 9.7%/ST 4.7%，创/科 19.7%）；
  consecutive_ladder=连续涨停天数梯队代理；explosion_count=touched 未封板家数（定位器内部算
  真定义炸板率）；daban_next_day_premium=T-1 涨停股 T 日平均收益（后复权）；
  amount_ratio=全市场成交额/20 日均量。avg_turnover_rate/dragon_tiger_net_buy_ratio/northbound_net_inflow
  传中性值 0.0（_score_phase 权重 0，不影响阶段标签；影响 position_scale 与 is_tradable，本验证不消费）。

用法：
  python scripts/research/verify_g07_sentiment_stratified_correlation.py \
      --start 2023-09-12 --end 2026-09-11 --n-bootstrap 2000 --block-size 5 \
      --json-out tmp/g07_result.json

SSoT: 28_sentiment_cycle_trading.md §3.7.2/§3.7.3/§3.7.4 + 30_multi_strategy_concurrency.md §6.2
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[2]  # sys.path 注入用（canonical REPO_ROOT 在 paths.py，勿重定义）
sys.path.insert(0, str(_SCRIPT_REPO_ROOT / "src"))

from zephyr.data.table_registry import get_registry  # noqa: E402

STRATEGIES = ("daban", "multifactor", "event_driven")  # noqa: gate-vocab  业务数据 schema（策略键名），非 knowledge_taxonomy 词表校验
MIN_PHASE_DAYS = 30  # §3.7.2 硬门槛：每阶段样本 ≥30 天
PHASE_ORDER = ("冰点", "反核", "主升", "疯狂", "退潮")

# 三态判据阈值（§3.7.3 处置表，任务口径以 ρ_max 为准）
RHO_PASS = 0.3
RHO_FAIL = 0.6


def get_ch():
    """ClickHouse 只读连接（RBAC reader 账号；连接统一治本 2026-09-14）。"""
    from zephyr.infrastructure.database_service import get_db_service

    return get_db_service().get_clickhouse_conn(role="reader")


def load_kline(ch, start: str, end: str) -> pd.DataFrame:
    """c1_market.kline_daily（ReplacingMergeTree→FINAL，对齐 ch_reader 惯例）拉宽表原料。

    返回长表: trade_date, symbol, open, high, close, hfq_close, pct_change, amount, adj_factor
    （pct_change 单位=百分比；hfq_close=close×adj_factor 后复权，收益计算用）。
    """
    rows = ch.execute(
        f"""
        SELECT trade_date, symbol, toFloat64(open), toFloat64(high), toFloat64(close),
               toFloat64(pct_change), toFloat64(amount), toFloat64(adj_factor)
        FROM {get_registry().table("market_kline_daily")} FINAL
        WHERE trade_date >= %(start)s AND trade_date <= %(end)s
          AND market_type = 'A_share' AND exchange IN ('SH', 'SZ')
        ORDER BY trade_date, symbol
        """,
        {"start": start, "end": end},
    )
    df = pd.DataFrame(
        rows,
        columns=["trade_date", "symbol", "open", "high", "close", "pct_change", "amount", "adj_factor"],
    )
    df["hfq_close"] = df["close"] * df["adj_factor"]
    return df


def load_st_flags(ch, start: str, end: str) -> pd.DataFrame:
    """c1_market.stock_basic 每日快照 → ST/退市整理 flag（name 含 'ST' 或 '退' 视为不可交易池）。"""
    rows = ch.execute(
        f"""
        SELECT trade_date, symbol,
               if(positionUTF8(name, 'ST') > 0 OR positionUTF8(name, '退') > 0, 1, 0) AS is_st
        FROM {get_registry().table("meta_stock_basic")} FINAL
        WHERE trade_date >= %(start)s AND trade_date <= %(end)s
        """,
        {"start": start, "end": end},
    )
    return pd.DataFrame(rows, columns=["trade_date", "symbol", "is_st"])


def load_lud_truth(ch) -> pd.DataFrame:
    """limit_up_down 真值日度计数（交叉校验用；覆盖 2026-08-03 起）。"""
    rows = ch.execute(
        f"""
        SELECT trade_date,
               countIf(limit_type = '涨停') AS lu, countIf(limit_type = '跌停') AS ld
        FROM {get_registry().table("market_limit_up_down")} FINAL
        GROUP BY trade_date ORDER BY trade_date
        """
    )
    return pd.DataFrame(rows, columns=["trade_date", "lu_truth", "ld_truth"])


def limit_thresholds(symbols) -> np.ndarray:
    """按板别给涨停代理阈值（百分比）：创业板(30)/科创板(68) 19.7%，主板 9.7%。"""
    return np.array([19.7 if str(s).startswith(("30", "68")) else 9.7 for s in symbols])


def limit_streak_matrix(is_lu: np.ndarray) -> np.ndarray:
    """连板代理：(T,N) bool → 截至 T 日连续涨停天数（逐日滚动，T 日断板归零）。"""
    t_n = is_lu.shape
    streak = np.zeros(t_n, dtype=np.int32)
    prev = np.zeros(t_n[1], dtype=np.int32)
    for i in range(t_n[0]):
        cur = np.where(is_lu[i], prev + 1, 0).astype(np.int32)
        streak[i] = cur
        prev = cur
    return streak


def wide_from_long(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df.pivot(index="trade_date", columns="symbol", values=col).sort_index()


def build_daily_inputs(df: pd.DataFrame, st: pd.DataFrame) -> dict:
    """全市场日度矩阵与定位器输入原料（全部 T 日盘后可得，无未来函数）。

    炸板代理用真定义口径：touched（盘中最高触及涨停价附近）未封板 /(touched + 封板)，
    其中 pre_close = close/(1+pct_change/100)（交易所口径 pre_close 反推，除权日自动对齐），
    touched 阈值 = 涨停阈值 - 0.2pp（容涨停价 0.01 元取整误差）。
    涨跌停阈值 ST 感知：主板 ST 5%板（4.7%阈值），创业板/科创板 20%（19.7%），其余主板 10%（9.7%）。
    """
    dates = sorted(df["trade_date"].unique())
    wide_close = wide_from_long(df, "close")
    wide_hfq = wide_from_long(df, "hfq_close")
    wide_open = wide_from_long(df, "open")
    wide_high = wide_from_long(df, "high")
    wide_pct = wide_from_long(df, "pct_change")
    wide_amt = wide_from_long(df, "amount")
    wide_amt = wide_amt.reindex(index=wide_close.index, columns=wide_close.columns)

    st_wide = st.pivot(index="trade_date", columns="symbol", values="is_st")
    st_wide = st_wide.reindex(index=wide_close.index, columns=wide_close.columns)
    # 快照缺失日（非快照日/新窗首日）沿用前值；首日缺失视 0（不剔除），两段式口径见 report
    st_wide = st_wide.ffill().fillna(0)
    st_avail_from = st["trade_date"].min()

    thr = limit_thresholds(wide_close.columns)
    is_main = np.array([not str(s).startswith(("30", "68")) for s in wide_close.columns])
    st_np = st_wide.values.astype(bool)
    # ST 感知有效阈值（T×N）：主板 ST 4.7%（5%板），其余按板别 9.7%/19.7%
    thr_eff = np.where(st_np & is_main[None, :], 4.7, thr[None, :])
    pct_np = wide_pct.values
    is_lu = pct_np >= thr_eff
    is_ld = pct_np <= -thr_eff
    # touched：盘中最高价触及涨停价附近（阈值-0.2pp 容取整误差）
    pre_close = wide_close / (1.0 + wide_pct / 100.0)
    wide_high_pct = (wide_high / pre_close - 1.0) * 100.0
    is_touch = wide_high_pct.values >= (thr_eff - 0.2)
    touched_not_sealed = is_touch & (~is_lu)
    exp_num = np.count_nonzero(touched_not_sealed, axis=1)
    exp_denom = exp_num + np.count_nonzero(is_lu, axis=1)
    explosion_rate = np.where(exp_denom > 0, exp_num / np.maximum(exp_denom, 1), 0.0)
    is_one_word = (wide_open.values >= wide_high.values - 1e-9) & is_lu  # 一字板≈开盘即封死（open==high）
    streak = limit_streak_matrix(is_lu)

    # 全市场成交额/20 日均量（含当日；窗口前 19 日 ratio 有偏，对齐期跳过）
    amt_sum = wide_amt.sum(axis=1, skipna=True)
    amt_ratio = amt_sum / amt_sum.rolling(20, min_periods=20).mean()

    return {
        "dates": dates,
        "wide_close": wide_close,
        "wide_hfq": wide_hfq,
        "wide_pct": wide_pct,
        "wide_amt": wide_amt,
        "is_lu": is_lu,
        "is_ld": is_ld,
        "is_one_word": is_one_word,
        "explosion_num": exp_num,
        "explosion_rate": explosion_rate,
        "streak": streak,
        "st_wide": st_wide,
        "st_avail_from": st_avail_from,
        "amt_ratio": amt_ratio,
        "amt_sum": amt_sum,
    }


def build_pools_and_returns(di: dict, args) -> tuple[dict[str, pd.Series], pd.Series, dict]:
    """三策略信号代理收益：T 日信号 → T+1 收盘买 → T+2 收盘卖；收益记账日=卖出日 T+2。

    两段式池选择：ST flag 覆盖起点（stock_basic 每日快照自 {st_avail_from}）前不剔除 ST，
    ST 覆盖期内剔除 ST/退市整理；起始对齐期=60 日波动率预热 + 20 日量比预热 + 2 日结算滞后。
    打板代理次日溢价（定位器 next_day_premium 输入，市场口径含一字板）同步产出。
    """
    dates = di["dates"]
    n = len(dates)
    idx = pd.Index(dates)
    hfq = di["wide_hfq"]
    ret1 = hfq.pct_change(fill_method=None)  # ret1[t] = close[t]/close[t-1]-1（后复权）

    is_lu = di["is_lu"]
    is_ld = di["is_ld"]
    is_ow = di["is_one_word"]
    streak = di["streak"]
    st = di["st_wide"].values.astype(bool)
    pct = di["wide_pct"]
    amt = di["wide_amt"]
    amt_ratio = di["amt_ratio"]

    vol60 = pct.rolling(60, min_periods=60).std()  # 60 日波动率（百分比收益）
    amt_rank_top30 = amt.rank(axis=1, pct=True, ascending=False) <= 0.30
    amt_rank_top5 = amt.rank(axis=1, pct=True, ascending=False) <= 0.05
    vol_bot50 = vol60.rank(axis=1, pct=True, ascending=True) <= 0.50

    # 连板梯队字典（T 日）：{连板数: 家数}（≥2 板）
    def ladder_at(t: int) -> dict[int, int]:
        row = streak[t]
        vals, counts = np.unique(row[row >= 2], return_counts=True)
        return {int(v): int(c) for v, c in zip(vals, counts)}

    strat_ret: dict[str, pd.Series] = {s: pd.Series(np.nan, index=idx) for s in STRATEGIES}
    pool_stats = {"daban": [], "multifactor": [], "event_driven": []}
    st_fallback_days = 0
    premium_series = pd.Series(np.nan, index=idx)  # 打板代理当日收益 = 次日溢价代理

    # 预转 numpy 加速日循环
    is_lu_np, is_ow_np = is_lu, is_ow
    amt_np = amt.values
    amt30_np = amt_rank_top30.values
    amt5_np = amt_rank_top5.values
    vol50_np = vol_bot50.values
    ret1_np = ret1.values
    hfq_np = hfq.values
    for t in range(2, n):
        d_t = dates[t]
        # 结算日 t 需要信号日 t-2 与买入日 t-1 均在窗内
        s = t - 2  # 信号日
        b = t - 1  # 买入日
        if s < 0 or b < 0:
            continue
        st_day_ok = d_t >= di["st_avail_from"]
        if not st_day_ok:
            st_fallback_days += 1
        st_s = st[s] if st_day_ok else np.zeros(is_lu_np.shape[1], dtype=bool)
        st_b = st[b] if st_day_ok else np.zeros(is_lu_np.shape[1], dtype=bool)

        trade_ok_b = np.isfinite(hfq_np[b]) & np.isfinite(hfq_np[t])
        can_buy_b = trade_ok_b & (~is_ow_np[b]) & (~st_b) if st_day_ok else trade_ok_b & (~is_ow_np[b])

        # ---- daban：T 日涨停（剔除 ST）→ T+1 可买（非一字/非 ST）→ 等权
        daban_sel = is_lu_np[s] & (~st_s) & can_buy_b
        # ---- multifactor：T 日额 top30% ∩ 60 日波动率 bottom50%，取额 top20
        mf_sel = amt30_np[s] & vol50_np[s] & (~st_s) & can_buy_b
        # ---- event_driven：T 日额 top5%（活跃度/事件热度），取额 top20
        ev_sel = amt5_np[s] & (~st_s) & can_buy_b

        for name, sel, topn in (
            ("daban", daban_sel, None),
            ("multifactor", mf_sel, args.multifactor_n),
            ("event_driven", ev_sel, args.event_n),
        ):
            k = int(np.count_nonzero(sel))
            if k == 0:
                continue
            if topn is not None and k > topn:
                # 池超容量 → 按信号日成交额取 topn
                a_row = np.where(np.isfinite(amt_np[s]), amt_np[s], -1.0)
                order = np.argsort(-a_row * sel)  # sel 外排 -1，不入选
                pick = order[:topn]
            else:
                pick = np.nonzero(sel)[0]
            r = np.nanmean(ret1_np[t, pick])  # T+1 收盘→T+2 收盘
            if np.isfinite(r):
                strat_ret[name].iloc[t] = r
            pool_stats[name].append((str(d_t), len(pick)))

        # 打板代理次日溢价（定位器 next_day_premium 输入，市场口径含一字板）：
        # T-1 日涨停股在 T 日的平均收益（close[T]/close[T-1]-1，后复权）
        prem_sel = is_lu_np[b] & (~st_b)
        if np.count_nonzero(prem_sel) > 0:
            pr = np.nanmean(ret1_np[t, np.nonzero(prem_sel)[0]])
            if np.isfinite(pr):
                premium_series.iloc[t] = pr

    meta = {
        "st_fallback_days": st_fallback_days,
        "st_avail_from": str(di["st_avail_from"]),
        "pool_size_last20": {
            name: [k for _, k in stats[-20:]] for name, stats in pool_stats.items()
        },
        "pool_days_nonempty": {
            name: len(stats) for name, stats in pool_stats.items()
        },
    }
    return strat_ret, premium_series, meta


def build_locator_inputs(di: dict, premium: pd.Series) -> list[dict]:
    """逐日组装 SentimentLocatorInput（28 号 §3.3 契约；neutral 输入见模块 docstring 披露）。"""
    dates = di["dates"]
    is_lu = di["is_lu"]
    is_ld = di["is_ld"]
    streak = di["streak"]
    amt_ratio = di["amt_ratio"]

    def ladder_dict(t: int) -> dict[int, int]:
        row = streak[t]
        vals, counts = np.unique(row[row >= 2], return_counts=True)
        return {int(v): int(c) for v, c in zip(vals, counts)}

    inputs: list[dict] = []
    for t, d in enumerate(dates):
        lu_n = int(np.count_nonzero(is_lu[t]))
        ld_n = int(np.count_nonzero(is_ld[t]))
        if t == 0:
            explosion = 0
            y_ladder: dict[int, int] = {}
        else:
            # 炸板代理 = T 日 touched 未封板家数（真定义：炸板/(炸板+涨停) 由定位器内部计算）
            explosion = int(di["explosion_num"][t])
            y_ladder = ladder_dict(t - 1)
        inputs.append(
            {
                "date": str(d),
                "limit_up_count": lu_n,
                "limit_down_count": ld_n,
                "explosion_count": explosion,
                "consecutive_ladder": ladder_dict(t),
                "yesterday_consecutive": y_ladder,
                "daban_next_day_premium": float(premium.iloc[t]) if np.isfinite(premium.iloc[t]) else 0.0,
                "avg_turnover_rate": 0.0,  # 中性：_score_phase 权重 0
                "market_amount_ratio_vs_ma20": float(amt_ratio.iloc[t]) if np.isfinite(amt_ratio.iloc[t]) else 1.0,
                "dragon_tiger_net_buy_ratio": 0.0,  # 中性：权重 0
                "northbound_net_inflow": 0.0,  # 中性：权重 0
            }
        )
    return inputs


def run_locator(locator_inputs: list[dict]) -> tuple[list[str], dict]:
    """sentiment_cycle.locate_sentiment_phase 逐日打标（同一段历史，消费昨日 phase_prob 先验）。"""
    from zephyr.signal_ashare.sentiment.sentiment_cycle import SentimentLocatorInput, locate_sentiment_phase

    labels: list[str] = []
    fallback_days = 0
    prev_prob = None
    for raw in locator_inputs:
        inp = SentimentLocatorInput(
            limit_up_count=raw["limit_up_count"],
            limit_down_count=raw["limit_down_count"],
            explosion_count=raw["explosion_count"],
            consecutive_ladder=raw["consecutive_ladder"],
            yesterday_consecutive=raw["yesterday_consecutive"],
            daban_next_day_premium=raw["daban_next_day_premium"],
            avg_turnover_rate=raw["avg_turnover_rate"],
            market_amount_ratio_vs_ma20=raw["market_amount_ratio_vs_ma20"],
            dragon_tiger_net_buy_ratio=raw["dragon_tiger_net_buy_ratio"],
            northbound_net_inflow=raw["northbound_net_inflow"],
            yesterday_phase_prob=prev_prob,
        )
        out = locate_sentiment_phase(inp)
        prev_prob = out.phase_prob
        labels.append(out.dominant_phase.value)
        fallback_days += int(out.fallback_triggered)
    dist = pd.Series(labels).value_counts().to_dict()
    return labels, {"fallback_days": fallback_days, "label_dist": dist}


def cross_check_lud(di: dict, ch) -> dict:
    """涨停代理 vs limit_up_down 真值（2026-08-03 起重叠期）：mean|代理−真值|/真值。"""
    truth = load_lud_truth(ch)
    if truth.empty:
        return {"status": "skipped", "reason": "limit_up_down 空"}
    dates = pd.Index(di["dates"])
    lu_proxy = pd.Series({d: int(np.count_nonzero(di["is_lu"][i])) for i, d in enumerate(dates)})
    ld_proxy = pd.Series({d: int(np.count_nonzero(di["is_ld"][i])) for i, d in enumerate(dates)})
    m = truth.set_index("trade_date").join(lu_proxy.rename("lu_proxy")).join(ld_proxy.rename("ld_proxy")).dropna()
    if m.empty:
        return {"status": "skipped", "reason": "无重叠期"}
    rel_lu = float(np.mean(np.abs(m["lu_proxy"] - m["lu_truth"]) / np.maximum(m["lu_truth"], 1)))
    rel_ld = float(np.mean(np.abs(m["ld_proxy"] - m["ld_truth"]) / np.maximum(m["ld_truth"], 1)))
    return {
        "status": "ok",
        "overlap_days": int(len(m)),
        "first": str(m.index.min()),
        "last": str(m.index.max()),
        "limit_up_proxy_mean_rel_err": round(rel_lu, 4),
        "limit_down_proxy_mean_rel_err": round(rel_ld, 4),
        "sample": [
            {
                "date": str(d),
                "lu_truth": int(r["lu_truth"]),
                "lu_proxy": int(r["lu_proxy"]),
                "ld_truth": int(r["ld_truth"]),
                "ld_proxy": int(r["ld_proxy"]),
            }
            for d, r in list(m.iterrows())[-5:]
        ],
    }


def corr_matrix(vals: dict[str, np.ndarray]) -> dict[str, dict[str, float]]:
    mat = {}
    for a in STRATEGIES:
        mat[a] = {}
        for b in STRATEGIES:
            mat[a][b] = round(float(np.corrcoef(vals[a], vals[b])[0, 1]), 4) if a != b else 1.0
    return mat


def rho_max_of(mat: dict[str, dict[str, float]]) -> float:
    return max(abs(mat[a][b]) for i, a in enumerate(STRATEGIES) for b in STRATEGIES[i + 1 :])


def stratified_validation(returns: dict[str, pd.Series], labels: list[str], dates: list[str]) -> dict:
    """§3.7.2 分层相关性（memo 伪代码等价实现，numpy 向量化）+ ≥30 天硬门槛 fail-open。"""
    df = pd.DataFrame(returns)
    df["phase"] = labels
    df.index = dates
    df = df.dropna()
    full = corr_matrix({s: df[s].values for s in STRATEGIES})
    out = {
        "n_days_used": int(len(df)),
        "full_sample_matrix": full,
        "full_sample_rho_max": round(rho_max_of(full), 4),
        "phases": {},
    }
    rho_maxes = []
    for ph in PHASE_ORDER:
        sub = df[df["phase"] == ph]
        n = int(len(sub))
        if n < MIN_PHASE_DAYS:
            out["phases"][ph] = {
                "n_days": n,
                "is_enough": False,
                "note": f"样本不足 {MIN_PHASE_DAYS} 天硬门槛，fail-open 不硬凑（不参与裁定）",
            }
            continue
        mat = corr_matrix({s: sub[s].values for s in STRATEGIES})
        rmax = round(rho_max_of(mat), 4)
        rho_maxes.append(rmax)
        out["phases"][ph] = {
            "n_days": n,
            "is_enough": True,
            "matrix": mat,
            "rho_max": rmax,
            "verdict": "pass" if rmax < RHO_PASS else ("partial" if rmax <= RHO_FAIL else "fail"),
        }
    # 三态裁定：取样本充足阶段的最高 ρ_max
    if rho_maxes:
        overall = max(rho_maxes)
        if overall < RHO_PASS:
            state = "假设成立"
            action = "情绪周期是隐形驱动且分层有效，三策略组合可施工（TDM-E-L2-05 具备转蓝数据依据）"
        elif overall <= RHO_FAIL:
            state = "部分成立"
            action = "G13 FirmRiskAggregator 加情绪周期暴露硬上限后组合可施工（TDM-E-L2-05 转蓝附条件）"
        else:
            state = "组合失效"
            action = "多策略实为情绪 beta 穿多件衣服，需重新审视策略组合（30 号 §6.2）"
        out["verdict"] = {
            "rho_max_over_enough_phases": overall,
            "state": state,
            "action": action,
            "enough_phases": [p for p in PHASE_ORDER if out["phases"][p]["is_enough"]],
        }
    else:
        out["verdict"] = {
            "rho_max_over_enough_phases": None,
            "state": "裁定不能",
            "action": "无任何阶段样本 ≥30 天（fail-open），本轮不出裁定",
            "enough_phases": [],
        }
    return out


def hawkes_supplement(returns: dict[str, pd.Series], di: dict, args) -> dict:
    """§3.7.4 增补：Hawkes 日度强度（事件=涨停代理数≥3 年 80 分位的高温日）+ block-bootstrap 2000 次。"""
    try:
        from zephyr.signal_ashare.sentiment.sentiment_cycle import (
            SentimentHawkesParams,
            analyze_sentiment_driven_correlation,
            compute_hawkes_intensity,
            estimate_hawkes_branching_ratio,
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": "skipped", "reason": f"sentiment_cycle §3.7.4 函数导入失败: {type(exc).__name__}: {exc}"}

    try:
        lu_counts = np.array([int(np.count_nonzero(di["is_lu"][i])) for i in range(len(di["dates"]))])
        thr = float(np.quantile(lu_counts, 0.80))
        event_days = [float(i) for i, c in enumerate(lu_counts) if c >= thr]
        params = SentimentHawkesParams(lambda_0=0.6, alpha=0.45, beta=0.9, critical_ratio=0.5)
        eta = estimate_hawkes_branching_ratio(event_days, params)
        n_days = len(di["dates"])
        lam = np.array([compute_hawkes_intensity(event_days, params, t + 0.5) for t in range(n_days)])

        dates_idx = pd.Index(di["dates"])
        aligned = {}
        for s in STRATEGIES:
            r = returns[s].reindex(dates_idx)
            aligned[s] = r.values
        valid = np.ones(n_days, dtype=bool)
        for s in STRATEGIES:
            valid &= np.isfinite(aligned[s])
        strat_vals = {s: aligned[s][valid] for s in STRATEGIES}
        lam_v = lam[valid]

        boot = analyze_sentiment_driven_correlation(
            strat_vals, list(lam_v), n_bootstrap=args.n_bootstrap, block_size=args.block_size
        )
        driver = {}
        for s in STRATEGIES:
            rho = boot["observed_rho"][s]
            level = "强驱动" if abs(rho) > 0.6 else ("中等驱动" if abs(rho) > 0.3 else "弱驱动")
            driver[s] = {
                "rho": round(rho, 4),
                "level": level,
                "p_value": round(boot["p_value"][s], 4),
                "is_significant": bool(boot["is_significant"][s]),
            }
        return {
            "status": "ok",
            "params": {"lambda_0": params.lambda_0, "alpha": params.alpha, "beta": params.beta},
            "branching_ratio_eta": round(float(eta), 4),
            "eta_reading": "超临界(>1)传染失控" if eta > 1 else ("临界(≈1)" if eta > 0.9 else "亚临界(<1)可衰减"),
            "events_def": f"涨停代理数 ≥ 80 分位({thr:.0f} 家)的高温日，共 {len(event_days)} 个事件",
            "n_days_used": int(valid.sum()),
            "driver_verdict": driver,
            "n_bootstrap": boot["n_bootstrap"],
            "block_size": args.block_size,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "skipped", "reason": f"{type(exc).__name__}: {exc}"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="G07 情绪周期分层相关性验证（§3.7.2 主判据 + §3.7.4 增补）")
    parser.add_argument("--start", default="2023-09-12")
    parser.add_argument("--end", default="2026-09-11")
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    parser.add_argument("--block-size", type=int, default=5)
    parser.add_argument("--multifactor-n", type=int, default=20)
    parser.add_argument("--event-n", type=int, default=20)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    t0 = time.time()
    ch = get_ch()
    print(f"[1/6] 拉取 kline_daily {args.start}~{args.end} ...", flush=True)
    df = load_kline(ch, args.start, args.end)
    if df.empty or df["trade_date"].nunique() < 80:
        print(f"数据不足: {df['trade_date'].nunique()} 个交易日", file=sys.stderr)
        return 2
    print(f"      {len(df):,} 行 × {df['symbol'].nunique()} 标的 × {df['trade_date'].nunique()} 日", flush=True)
    st = load_st_flags(ch, args.start, args.end)
    print(f"[2/6] 构建日度矩阵/池/收益（两段式 ST 口径）...", flush=True)
    di = build_daily_inputs(df, st)
    strat_ret, premium_series, pool_meta = build_pools_and_returns(di, args)
    complete = pd.DataFrame(strat_ret).dropna()
    if len(complete) < 120:
        print(f"对齐后收益样本不足: {len(complete)} 日", file=sys.stderr)
        return 2
    print(f"      三策略对齐收益 {len(complete)} 日", flush=True)

    print("[3/6] 定位器逐日打标 ...", flush=True)
    locator_inputs = build_locator_inputs(di, premium_series)
    labels, loc_meta = run_locator(locator_inputs)

    print("[4/6] 交叉校验涨停代理 vs limit_up_down ...", flush=True)
    xcheck = cross_check_lud(di, ch)

    print("[5/6] §3.7.2 分层相关性 + 三态裁定 ...", flush=True)
    strat_out = stratified_validation(strat_ret, labels, [str(d) for d in di["dates"]])

    print(f"[6/6] §3.7.4 Hawkes + block-bootstrap {args.n_bootstrap} 次 ...", flush=True)
    hawkes = hawkes_supplement(strat_ret, di, args)

    report = {
        "meta": {
            "start": args.start,
            "end": args.end,
            "n_days_window": len(di["dates"]),
            "n_days_returns_aligned": int(len(complete)),
            "n_symbols": int(df["symbol"].nunique()),
            "caliber": "信号代理收益（backtest-based，第一轮；结论待实盘复核）",
            "pool_defs": {
                "daban": "T 日涨停代理池（pct_change≥9.7%/19.7%，剔除 ST/一字板/不可交易）等权，T+1 收盘买、T+2 收盘卖",
                "multifactor": f"T 日成交额 top30% ∩ 60 日波动率 bottom50% 取额 top{args.multifactor_n} 等权",
                "event_driven": f"T 日成交额 top5%（活跃度/事件热度溢出）取额 top{args.event_n} 等权",
            },
            "two_stage_st_caliber": {
                "st_flag_avail_from": pool_meta["st_avail_from"],
                "st_fallback_days": pool_meta["st_fallback_days"],
                "note": "ST 快照覆盖起点前不剔除 ST（快照表每日覆盖自 2025-09-12 起），覆盖期内剔除",
            },
            "neutral_locator_inputs": "avg_turnover_rate/dragon_tiger_net_buy_ratio/northbound_net_inflow 传 0.0（_score_phase 权重 0，不影响阶段标签；影响 position_scale/is_tradable，本验证不消费）",
            "consecutive_ladder_caliber": "连板梯队=3 日滚动连续涨停代理（pct≥板别阈值连续天数，与真值连板同构）",
            "explosion_caliber": "炸板代理=touched 未封板/(touched+封板)，touched=盘中最高触及涨停价-0.2pp（OHLC 推算，pre_close 取交易所 pct 口径反推）",
            "alignment": "信号 T 日盘后可得 → T+1 收盘买入 → T+2 收盘卖出；收益按卖出日记账；分层标签=卖出日情绪阶段",
            "label_dist": loc_meta["label_dist"],
            "fallback_days": loc_meta["fallback_days"],
            "pool_days_nonempty": pool_meta["pool_days_nonempty"],
            "pool_size_last20": pool_meta["pool_size_last20"],
            "cross_check_limit_proxy_vs_truth": xcheck,
            "elapsed_sec": round(time.time() - t0, 1),
        },
        "stratified_372": strat_out,
        "hawkes_374_supplement": hawkes,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2, default=str)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
        print(f"JSON 报告 → {args.json_out}", flush=True)
    # stdout 摘要
    v = strat_out.get("verdict", {})
    print("=== G07 分层相关性摘要 ===")
    print(f"全样本 ρ_max={strat_out['full_sample_rho_max']}  n={strat_out['n_days_used']}")
    for ph, info in strat_out["phases"].items():
        if info.get("is_enough"):
            print(f"  {ph}: n={info['n_days']} ρ_max={info['rho_max']} → {info['verdict']}")
        else:
            print(f"  {ph}: n={info['n_days']} 样本不足 fail-open")
    print(f"裁定: {v.get('state')}  (ρ_max={v.get('rho_max_over_enough_phases')})")
    print(f"Hawkes 增补: {hawkes.get('status')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
