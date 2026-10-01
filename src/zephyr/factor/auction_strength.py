# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.auction_strength
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas; zephyr.data.table_registry; zephyr.infrastructure.database_service(lazy); zephyr.signal_ashare.limit_up.youzi_relay_emotion_engine(lazy 打分委托)
# [CONSUMERS] scripts/backtest/eval_auction_strength_ic.py（IC 回测取证）; factor_registry FCT-INTRADAY-025（BM-SEL-23-A-5 注册 code_path 指向本件）;
#             daban 决策链 T 日竞价喂入为声明接线点（设计语义=T 当日 09:25 竞价，属策略侧盘中通道，非 T-1 负载批产字段——
#             daban_load_producer 不可产字段清单的此条由本件补源，见 §CNS-11 案卷）
# [STARTUP] imported
# [MATURITY] testing
# [TTL] permanent
# [INVARIANTS] 因子真源复用不重建：打分真源=youzi_relay_emotion_engine.score_auction_strength
#              （BM-SEL-23-A-5 production 引擎函数，24 号文 §1.1①/§3.8 源码真源裁定），本件零判据只装配；
#              竞价量比口径=注册表自declared（factor_registry 竞价 alpha_source："竞价量/前 5 日竞价均量"）；
#              终态真源=auction_snapshot（每股每日 argMax 终态，ch_auction_derive 派生语义）；pre_close
#              真源=auction_book argMax（ch_auction_derive 规则推导列，本件不再第二套推导）；
#              PIT：量比基线只用**严格早于**当日的竞价日（shift 滚动，禁含当日）；缺基线/缺昨收→None
#              （不可产省略，禁拍 0/1.0 中性值冒充——daban_load_producer 同纪律）；
#              唯一读通道=DatabaseService reader（DI conn 缝位，禁 ch_reader TSV 下标直取，W-180）；
#              表名真源=TableRegistry；禁内建时钟（窗口显式传参）
# [MODIFY-GUARD] tests/factor/test_auction_strength.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 事件/快照读数空->RuntimeError（查询失败≠无数据）；conn 缺失->lazy 真reader
# [TESTS] tests/factor/test_auction_strength.py（tmp 合成帧+fake conn，零 CH）
"""竞价强度因子输入装配（CNS-11 · BM-SEL-23-A-5 查询路径，SW14 夜战 2026-09-29）。

缺口（14 号文 CNS-11 + daban_load_producer 不可产字段清单实证）：auction_book 412 万行
在库，但"竞价数据 → youzi 引擎 auction_rise_pct/auction_volume_ratio 入参"这一段查询
装配路径不存在——因子函数在产（production），输入无源，等同空转。

本件补该段（装配/查询路径，禁造新指标）：

    auction_snapshot（终态） × auction_book（pre_close 推导列） × 前 5 竞价日基线
      → {(trade_date, symbol): auction_rise_pct, auction_volume_ratio}
      → score_auction_strength（委托 youzi 引擎，BM-SEL-23-A-5 判据真源）

口径注记（全部在册真源，非本件发明）：
    - auction_rise_pct = (auction_price/pre_close − 1) × 100（竞价涨幅%，引擎入参契约）
    - auction_volume_ratio = auction_volume / 前 5 个有数据竞价日均量
      （factor_registry 竞价 alpha_source 自declared 口径；引擎阈值 ≥2 加分的量纲即此）
    - 缺昨收/缺基线 → None（不可产省略，交引擎 dataclass 中性默认，禁拍假值）

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/auction_strength.yaml
"""

from __future__ import annotations

from typing import Any, Final

import pandas as pd

from zephyr.data.table_registry import get_registry

__all__: Final = ["fetch_auction_inputs", "auction_strength_score", "attach_scores"]

_TBL_SNAPSHOT = get_registry().table("market_auction_snapshot")
_TBL_BOOK = get_registry().table("market_auction_book")
_BASELINE_DAYS = 5

# 快照终态读数（终态列=auction_price/volume/amount，argMax 语义已由派生侧保证单行每股每日，
# 此处只取列不二次聚合；窗口显式传参禁内建时钟）
_SQL_SNAPSHOT = (
    "SELECT trade_date, symbol, auction_price, auction_volume, auction_amount "
    "FROM {table} WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}')"
)
# pre_close 真源=auction_book 规则推导列（ch_auction_derive _PRECLOSE_SUB 产物，禁第二套推导）
_SQL_PRECLOSE = (
    "SELECT trade_date, symbol, argMax(pre_close, timestamp) AS pre_close "
    "FROM {table} WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "GROUP BY trade_date, symbol"
)


def _default_reader() -> Any:  # noqa: any-abuse  DI缝位:返回CH client连接对象(DatabaseService reader角色),无公共基类可注型
    from zephyr.infrastructure.database_service import DatabaseService

    return DatabaseService().get_clickhouse_conn(role="reader")


def fetch_auction_inputs(start: str, end: str, *, conn: Any | None = None) -> pd.DataFrame:  # noqa: any-abuse  DI缝位:conn由调用方注入(测试fake/真reader共型),缺省走_default_reader
    """窗口内竞价强度输入装配：(trade_date, symbol) → rise_pct/volume_ratio（DataFrame）。

    Args:
        start/end: 窗口（YYYY-MM-DD 显式传参；量比基线取窗口内每股自身前序竞价日，
            窗口首日基线不足 5 日如实 None——禁向前偷读改 PIT 语义）。
        conn: DatabaseService reader 替身（测试注入零 CH）。

    Returns:
        DataFrame[trade_date, symbol, auction_price, auction_volume, pre_close,
        auction_rise_pct, auction_volume_ratio]；缺昨收/缺基线的行对应列=None。
    Raises:
        RuntimeError: 快照读数空（查询失败与无数据不可混判）。
    """
    c = conn if conn is not None else _default_reader()
    snap = pd.DataFrame(
        c.execute(_SQL_SNAPSHOT.format(table=_TBL_SNAPSHOT, start=start, end=end)),
        columns=["trade_date", "symbol", "auction_price", "auction_volume", "auction_amount"],
    )
    if snap.empty:
        raise RuntimeError(f"auction_snapshot 读数空 [{start},{end}]——查询失败与无数据不可混判")
    pre = pd.DataFrame(
        c.execute(_SQL_PRECLOSE.format(table=_TBL_BOOK, start=start, end=end)),
        columns=["trade_date", "symbol", "pre_close"],
    )
    df = snap.merge(pre, on=["trade_date", "symbol"], how="left")
    df["pre_close"] = pd.to_numeric(df["pre_close"], errors="coerce")
    df["auction_price"] = pd.to_numeric(df["auction_price"], errors="coerce")
    # 竞价涨幅%（引擎入参契约）；昨收缺失/非正→None（不可产省略）
    df["auction_rise_pct"] = None
    ok = df["pre_close"].notna() & (df["pre_close"] > 0) & df["auction_price"].notna()
    df.loc[ok, "auction_rise_pct"] = (df.loc[ok, "auction_price"] / df.loc[ok, "pre_close"] - 1.0) * 100.0
    # 量比=竞价量/前 5 个有数据竞价日均量（PIT：严格早于当日；基线不足→None）
    df = df.sort_values(["symbol", "trade_date"]).reset_index(drop=True)
    prev = df.groupby("symbol")["auction_volume"].shift(1)
    df["_vol_prev"] = prev
    baseline = df.groupby("symbol")["_vol_prev"].transform(
        lambda s: s.rolling(_BASELINE_DAYS, min_periods=_BASELINE_DAYS).mean()
    )
    df["auction_volume_ratio"] = None
    okv = baseline.notna() & (baseline > 0) & df["auction_volume"].notna()
    df.loc[okv, "auction_volume_ratio"] = df.loc[okv, "auction_volume"] / baseline[okv]
    return df.drop(columns=["_vol_prev"])


def auction_strength_score(rise_pct: float | None, volume_ratio: float | None) -> dict[str, Any]:
    """BM-SEL-23-A-5 打分（委托 youzi 引擎真源，零判据复制）。

    Returns:
        {"score": float, "max": float, "detail": str}；任一输入 None → score=None
        （不可产如实，交上层省略——禁拍 0 分冒充"弱"）。
    """
    if rise_pct is None or volume_ratio is None:
        return {"score": None, "max": None, "detail": "竞价输入缺失（昨收/基线不足）——不可产省略"}
    from zephyr.signal_ashare.limit_up.youzi_relay_emotion_engine import YouziRelayEmotionEngine

    fs = YouziRelayEmotionEngine().score_auction_strength(float(rise_pct), float(volume_ratio))
    return {"score": float(fs.score), "max": float(fs.max_score), "detail": str(fs.detail)}


def attach_scores(inputs: pd.DataFrame) -> pd.DataFrame:
    """输入帧逐行附 BM-SEL-23-A-5 分（score/max/detail 列；缺输入行 score=None）。"""
    df = inputs.copy()
    scored = [
        auction_strength_score(r, v) for r, v in zip(df["auction_rise_pct"], df["auction_volume_ratio"], strict=True)
    ]
    df["auction_strength_score"] = [s["score"] for s in scored]
    df["score_max"] = [s["max"] for s in scored]
    df["score_detail"] = [s["detail"] for s in scored]
    return df
