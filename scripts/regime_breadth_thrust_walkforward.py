#!/usr/bin/env python
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | 14 号 §4.5 / OVB-4 s2_breadth_thrust 清偿
# [MODULE] scripts.regime_breadth_thrust_walkforward
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.data.table_registry; zephyr.infrastructure.database_service; zephyr.regime.features.overlay_features; zephyr.regime.validation.overfitting_guard
# [CONSUMERS] 车道 st-qoder-t1a-20260915（人工运行）；报告 docs/_working/full-auto-chain/S11_assembled_backtest/breadth_thrust_walkforward_20260916.md；tests/regime/test_breadth_thrust_walkforward.py
# [STARTUP] manual
# [MATURITY] validation
# [INVARIANTS] 校准段/评估段严格分离（test 段永不参与选值）；网格与验收带先写死后跑数（PreRegistrationRegistry hash 锁）；
#   候选评分映射必须与生产 s2_breadth_thrust_score 逐日等值（mirror 自检，禁第二实现漂移）；
#   数据只读（CH reader role，表名经 TableRegistry 解析）；输出只落 .runtime/tmp，禁写 data/；
#   广度死日（补位后 adv+dec 仍为 0）不入统计母体，剔除数须随结果披露
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 段窗口无数据->ValueError；预注册名冲突->RuntimeError（继承 PreRegistrationRegistry）；
#   CH 不可达->异常直抛（本脚本是人工跑批，禁静默降级出"看起来对"的数）
# [TESTS] tests/regime/test_breadth_thrust_walkforward.py
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.12 #14_regime_s2_diagnosis §4.5 #OVB-4
# noqa: m11-perm-manual-legitimate  M11豁免: 阈值复研管线由车道按需手动触发（产报告供裁定，不产交易信号、不写 data/），非常驻服务亦无事件订阅义务
"""S2 breadth_thrust 阈值 walk-forward 重校管线（OVB-4 台账项 s2_breadth_thrust 清偿）。

病根：`overlay_features.s2_breadth_thrust_score` 的 0.615/0.40 是美股 NYSE 标准抄录，
台账长期挂 ALERT——"未经 A 股本土 walk-forward 复推"，且台账自述的分位（p88/p10）与
实测不符。本管线补的就是"预注册→样本外→不炸才用"这一闭环的证据链（仓库内唯一已跑通
该闭环的先例 = WYF-3 wyckoff，本文件镜像其结构）。

方法论（复用 capitulation/wyf3 栈，不另造轮子）：
  ① 预注册：`PREREG_GRID`（0.58-0.65 扫描区，台账处置段点名）+ `PREREG_ACCEPTANCE`
     （"top-few-percent 事件"双边界）先写死，经 `PreRegistrationRegistry` hash 锁定；
  ② walk-forward：expanding 训练段 + 紧邻评估段，评估段永不参与选值，逐折只跑一次；
  ③ 分位定位：现行阈值在 EMA 分布中的经验分位（p<sub>x</sub>）逐段报告——这是裁定
     "现行值是不是稀有事件"的直接量，比"命中率"更少被分布形状欺骗；
  ④ 事件研究：thrust 上穿日 5/20/60 日前向收益 vs 同段无条件基线（稀有但无方向=噪声）；
  ⑤ 裁定口径：现行值通过验收 → 缺陷是"台账 CLAIM 文案写错"，**不改生产阈值**，只把
     实测分位/窗口/样本/日期回填台账并撤 ALERT；不通过 → 报告给出候选值但仍须 Owner 门。

引擎真源纪律：候选评分映射 `score_for_config` 与生产函数逐日等值（`verify_mirror`），
不等值即 ValueError 中止——结构性防"诊断版与生产版漂移"。

依据: 14_regime_s2_diagnosis §4.5 / overlay_dims_mining §2#4 / THRESHOLD_CALIBRATION_LEDGER
Version: 0.1.0
# [ALGO_FLOW]
# I1: 399106 涨跌家数 + 000300 代理收盘（CH 只读/TableRegistry 解析，EQW_ALLA 补洞镜像 _load_breadth）
# F1: breadth_ema —— 生产同款 EMA10(adv/(adv+dec+1e-8))
# F2: score_for_config —— 候选 (thrust, washout) 映射，verify_mirror 对生产函数逐日等值自检
# F3: segment_metrics —— 分位定位 + on_share/full_thrust_share + thrust 上穿事件前向收益
# F4: run_walkforward —— 逐折"训练段选值→测试段只跑一次"+ 现值基线跨折稳定性
# O1: 逐折指标 + 全样本裁定 JSON 落 .runtime/tmp（报告真源）
# [/ALGO_FLOW]
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

import numpy as np
import pandas as pd

from zephyr.regime.features.overlay_features import s2_breadth_thrust_score
from zephyr.regime.validation.overfitting_guard import PreRegistrationRegistry

__all__ = [
    "CURRENT_THRUST",
    "CURRENT_WASHOUT",
    "DEFAULT_CONFIG",
    "PREREG_ACCEPTANCE",
    "PREREG_GRID",
    "PREREG_REPORT_WINDOWS",
    "PROD_EMA_WINDOW",
    "ThrustConfig",
    "WalkFold",
    "breadth_ema",
    "grid_points",
    "load_breadth",
    "make_folds",
    "onset_dates",
    "passes_acceptance",
    "percentile_of",
    "run_walkforward",
    "score_for_config",
    "segment_metrics",
    "select_in_train",
    "verify_mirror",
]

# ── 标的与数据源（与生产 overlay 完全一致）───────────────────────────────
MARKET_PROXY_SYMBOL: Final[str] = "000300"
BREADTH_SYMBOL: Final[str] = "399106"
BREADTH_FALLBACK_SYMBOL: Final[str] = "EQW_ALLA"

# 生产常量镜像（禁止裸写：改产阈值时本文件须同步，否则 verify_mirror 直接炸）
PROD_EMA_WINDOW: Final[int] = 10
PROD_IMPROVE_FLOOR: Final[float] = 0.55
CURRENT_THRUST: Final[float] = 0.615
CURRENT_WASHOUT: Final[float] = 0.40
#: EMA(10, adjust=False) 收敛 + rolling(10).min().shift(1) 所需预热；预热日不计任何统计
WARMUP_TRADE_DAYS: Final[int] = 60

# ── 预注册：窗口（看数据前写死）──────────────────────────────────────────
PREREG_SERIES_START: Final[str] = "2005-01-04"  # 代理与 399106 双活的最早公共日
PREREG_REPORT_WINDOWS: Final[dict[str, str]] = {
    "full": PREREG_SERIES_START,
    "post_2014": "2014-01-01",
    "post_2019": "2019-01-01",
}

# ── 预注册：网格（台账处置段点名的 0.58-0.65 区间；改动=新一次预注册，禁覆盖同名）
PREREG_GRID: Final[dict[str, Any]] = {
    "thrust": [0.58, 0.60, 0.615, 0.63, 0.65],
    "washout": [0.35, 0.40, 0.45],
}

# ── 预注册：验收带（写死，禁事后放宽凑数）───────────────────────────────
# 语义锚点：breadth_thrust 是 S2 confirm 的**析取腿**（keys_or_gte breadth_thrust>=60），
# 定义为"异常广度冲刺"= 头部少数事件。上界防误爆（天天在线=噪声污染每次 S2 confirm），
# 下界防恒零（稀有到不出现=维度不存在）。
PREREG_ACCEPTANCE: Final[dict[str, Any]] = {
    "on_share": [0.01, 0.10],  # ema>thrust 占比 ∈ [1%, 10%]
    "washout_share": [0.03, 0.25],  # ema<washout 占比 ∈ [3%, 25%]
    "full_thrust_share": [0.002, 0.05],  # 完整 thrust（washout→thrust 10 日内）∈ [0.2%, 5%]
    "onset_excess_20d_bps_min": -30.0,  # 上穿事件 20 日超额收益地板（-0.30%）：低于基线太多=反向噪声
    "fold_stability_max_ratio": 4.0,  # 跨折 on_share 极差/最小值 ≤4（防"某一时代才成立"）
}

HORIZONS: Final[tuple[int, ...]] = (5, 20, 60)


@dataclass(frozen=True)
class ThrustConfig:
    """一组候选 (thrust, washout)；默认值=生产现值。"""

    thrust: float = CURRENT_THRUST
    washout: float = CURRENT_WASHOUT
    improve: float = PROD_IMPROVE_FLOOR
    ema_window: int = PROD_EMA_WINDOW


@dataclass(frozen=True)
class WalkFold:
    """一折：训练段（选值）+ 紧邻评估段（只跑一次）。"""

    fold_id: str
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp

    def as_dict(self) -> dict[str, str]:
        return {
            "fold_id": self.fold_id,
            "train_start": str(self.train_start.date()),
            "train_end": str(self.train_end.date()),
            "test_start": str(self.test_start.date()),
            "test_end": str(self.test_end.date()),
        }


# ─────────────────────────────────────────────────────────────────────────
# 数据装载（CH 只读 + TableRegistry 真源解析，禁硬编码表名）
# ─────────────────────────────────────────────────────────────────────────
#: 生产现值配置（默认参数单例，避开 B008 可变默认）。
DEFAULT_CONFIG: Final[ThrustConfig] = ThrustConfig()


def load_breadth(
    *,
    proxy_symbol: str = MARKET_PROXY_SYMBOL,
    start: str = PREREG_SERIES_START,
    end: str | None = None,
    cache: str | Path | None = None,
    conn: Any | None = None,
) -> pd.DataFrame:
    """取 [代理交易日] 对齐的 adv/dec 与代理收盘，399106 死日由 EQW_ALLA 补位。

    镜像生产 `RegimeFeatureBuilder._load_breadth`：无数据日（adv<=0 且 dec<=0）
    回退 kline_index_calc 的 EQW_ALLA；补位后仍死的日保留 0（由调用方按
    `live` 列剔除出统计母体）。

    Args:
        proxy_symbol: 市场代理指数代码（决定交易日历与事件研究收益基准）。
        start: 序列起点（含）。
        end: 序列终点（含），None=库内最新。
        cache: parquet 缓存路径（临时区，禁写 data/）。
        conn: 注入 ClickHouse 连接（测试/复用用）。

    Returns:
        index=代理交易日，列 adv/dec/close/live（bool）。
    """
    cache_path = Path(cache) if cache else None
    if cache_path is not None and cache_path.exists():
        frame = pd.read_parquet(cache_path)
        frame.index = pd.to_datetime(frame.index)
        return frame.sort_index()

    from zephyr.data.table_registry import get_registry

    reg = get_registry()
    kline_index = reg.table("market_index_kline")
    kline_calc = reg.table("market_kline_index_calc")
    if conn is None:
        from zephyr.infrastructure.database_service import DatabaseService

        conn = DatabaseService().get_clickhouse_conn(role="reader")

    def _fetch(sql: str) -> pd.DataFrame:
        rows, cols = conn.execute(sql, {}, with_column_types=True)
        frame = pd.DataFrame(rows, columns=[c for c, _ in cols])
        if "trade_date" in frame.columns:
            frame["trade_date"] = pd.to_datetime(frame["trade_date"])
        return frame

    date_bound = f"AND trade_date <= toDate('{end}')" if end else ""
    _SQL_PROXY_CLOSE = (
        f"SELECT trade_date, close FROM {kline_index} "
        f"WHERE symbol = '{proxy_symbol}' AND trade_date >= toDate('{start}') {date_bound} "
        "ORDER BY trade_date"
    )
    proxy = _fetch(_SQL_PROXY_CLOSE).set_index("trade_date")

    _SQL_BREADTH_COUNTS = (
        f"SELECT trade_date, advance_count, decline_count FROM {kline_index} "
        f"WHERE symbol = '{BREADTH_SYMBOL}' AND trade_date >= toDate('{start}') {date_bound} "
        "ORDER BY trade_date"
    )
    breadth = _fetch(_SQL_BREADTH_COUNTS)
    breadth = breadth.groupby("trade_date")[["advance_count", "decline_count"]].max().sort_index()
    _SQL_EQW_COUNTS = (
        f"SELECT trade_date, advance_count, decline_count FROM {kline_calc} FINAL "
        f"WHERE symbol = '{BREADTH_FALLBACK_SYMBOL}' AND trade_date >= toDate('{start}') {date_bound} "
        "ORDER BY trade_date"
    )
    eqw = _fetch(_SQL_EQW_COUNTS)
    eqw = eqw.drop_duplicates("trade_date", keep="last").set_index("trade_date").sort_index()

    dates = pd.DatetimeIndex(proxy.index)
    adv = breadth["advance_count"].reindex(dates).astype(float).fillna(0.0)
    dec = breadth["decline_count"].reindex(dates).astype(float).fillna(0.0)
    dead = (adv <= 0.0) & (dec <= 0.0)
    if bool(dead.any()):
        fb_adv = eqw["advance_count"].reindex(dates).astype(float)
        fb_dec = eqw["decline_count"].reindex(dates).astype(float)
        use = dead & fb_adv.notna() & fb_dec.notna()
        adv = adv.where(~use, fb_adv)
        dec = dec.where(~use, fb_dec)

    frame = pd.DataFrame(
        {
            "adv": adv,
            "dec": dec,
            "close": proxy["close"].reindex(dates).astype(float),
            "live": (adv.fillna(0.0) + dec.fillna(0.0)) > 0.0,
        }
    )
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(cache_path)
    return frame.sort_index()


# ─────────────────────────────────────────────────────────────────────────
# 评分镜像（与生产逐日等值，verify_mirror 自检）
# ─────────────────────────────────────────────────────────────────────────
def breadth_ema(adv: pd.Series, dec: pd.Series, ema_window: int = PROD_EMA_WINDOW) -> pd.Series:
    """生产口径 EMA(adv/(adv+dec+1e-8))（`s2_breadth_thrust_score` 第一~三行）。"""
    total = adv + dec + 1e-8
    return (adv / total).ewm(span=ema_window, adjust=False).mean()


def score_for_config(
    adv: pd.Series,
    dec: pd.Series,
    cfg: ThrustConfig = DEFAULT_CONFIG,
) -> pd.Series:
    """候选 (thrust, washout) 下的 0/30/60/80 映射（生产函数的参数化镜像）。"""
    ema = breadth_ema(adv, dec, cfg.ema_window)
    was_washout = ema.rolling(cfg.ema_window).min().shift(1) < cfg.washout
    now_thrust = ema > cfg.thrust
    full_thrust = (was_washout & now_thrust).fillna(False)
    score = pd.Series(0.0, index=adv.index)
    score[ema > cfg.improve] = 30
    score[ema > cfg.thrust] = 60
    score[full_thrust] = 80
    return score


def verify_mirror(adv: pd.Series, dec: pd.Series, cfg: ThrustConfig = DEFAULT_CONFIG) -> int:
    """自检：现值参数下本文件映射必须与生产函数逐日相等，否则拒绝出报告。"""
    mine = score_for_config(adv, dec, cfg)
    prod = s2_breadth_thrust_score(adv, dec, ema_window=cfg.ema_window)
    diff = int((mine.reindex(prod.index).fillna(-1.0) != prod.fillna(-1.0)).sum())
    if diff:
        raise ValueError(f"score_for_config 与生产 s2_breadth_thrust_score 逐日不等（{diff} 日）→ 禁双实现")
    return int(len(prod))


def onset_dates(score: pd.Series, gate: float = 60.0) -> pd.DatetimeIndex:
    """评分上穿 gate 的日期（一次性事件语义，防"永远在线"当新信号）。"""
    on = (score >= gate).astype(bool)
    prev = on.shift(1, fill_value=False)
    return pd.DatetimeIndex(score.index[on & ~prev])


def _onsets_within(
    score: pd.Series,
    pop_index: pd.DatetimeIndex,
    gate: float = 60.0,
    *,
    max_horizon: int = max(HORIZONS),
) -> pd.DatetimeIndex:
    """母体内的上穿事件日，且要求 h 日前向窗完整落在母体末之内。

    训练段选值若允许事件日贴近段尾，前向收益会吃到段外价格（轻度未来函数）。此处直接
    砍掉尾部 max_horizon 个候选事件日 → 训练段判据只见训练段自己的价格。
    """
    onsets = onset_dates(score, gate)
    if onsets.empty or len(pop_index) <= max_horizon:
        return onsets
    last_allowed = pop_index[-max_horizon - 1]
    return onsets[onsets <= last_allowed]


def percentile_of(series: pd.Series, level: float) -> float:
    """`level` 在 series 经验分布中的分位（%≤level，即"现行值是第几百分位"）。"""
    vals = series.dropna()
    if vals.empty:
        raise ValueError("percentile_of 收到空样本")
    return float((vals <= level).mean() * 100.0)


def forward_returns(close: pd.Series, dates: pd.DatetimeIndex, horizons: Sequence[int]) -> pd.DataFrame:
    """事件日后 h 交易日累计收益（%）；越界 NaN。"""
    out: dict[int, list[float]] = {h: [] for h in horizons}
    pos = {d: i for i, d in enumerate(close.index)}
    values = close.to_numpy(dtype=float)
    for d in dates:
        i = pos.get(pd.Timestamp(d))
        for h in horizons:
            if i is None or i + h >= len(values) or values[i] == 0.0:
                out[h].append(np.nan)
            else:
                out[h].append((values[i + h] / values[i] - 1.0) * 100.0)
    return pd.DataFrame(out, index=list(dates))


# ─────────────────────────────────────────────────────────────────────────
# 段指标 / 折 / 选值 / 跑批
# ─────────────────────────────────────────────────────────────────────────
def make_folds(
    index: pd.DatetimeIndex,
    *,
    first_test_start: str | pd.Timestamp,
    test_years: int = 3,
    n_folds: int = 4,
) -> list[WalkFold]:
    """expanding 训练 + 紧邻 test 的 walk-forward 折序列（锚定起点，禁随机划分）。"""
    idx = pd.DatetimeIndex(index)
    anchor = pd.Timestamp(first_test_start)
    start = idx.min()
    folds: list[WalkFold] = []
    for k in range(n_folds):
        t0 = anchor + pd.DateOffset(years=k * test_years)
        t1 = anchor + pd.DateOffset(years=(k + 1) * test_years)
        if t0 >= idx.max():
            break
        train_end = idx[idx < t0].max()
        test_hi = min(t1 - pd.Timedelta(days=1), idx.max())
        test_days = idx[(idx >= t0) & (idx <= test_hi)]
        if len(test_days) == 0:
            break
        folds.append(
            WalkFold(
                fold_id=f"F{k + 1}",
                train_start=start,
                train_end=train_end,
                test_start=test_days.min(),
                test_end=test_days.max(),
            )
        )
    return folds


def segment_metrics(
    frame: pd.DataFrame,
    cfg: ThrustConfig,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> dict[str, Any]:
    """段内指标：阈值分位 + 稀有度 + 事件研究。

    EMA/评分在**整段连续序列**上算（与生产逐日同构：EMA/rolling 皆因果，切片即无未来
    信息），母体只取 [start, end] 内的 live 日且越过全局预热——避免"每段重新起算 EMA"
    造出生产里不存在的预热伪影。事件研究只取前向窗完整落在母体内的上穿日，故训练段
    选值永不窥视测试段。
    """
    ema_full = breadth_ema(frame["adv"], frame["dec"], cfg.ema_window)
    score_full = score_for_config(frame["adv"], frame["dec"], cfg)
    lo = pd.Timestamp(start) if start else frame.index.min()
    hi = pd.Timestamp(end) if end else frame.index.max()
    win = frame.loc[lo:hi]
    pop = win[win["live"].astype(bool)]
    if lo == frame.index.min():
        pop = pop.iloc[WARMUP_TRADE_DAYS:]
    if pop.empty:
        raise ValueError(f"段 [{start}, {end}] 无有效样本")
    idx = pop.index
    ema = ema_full.reindex(idx)
    score = score_full.reindex(idx)
    on = ema > cfg.thrust
    washout = ema < cfg.washout
    full = (score >= 80).astype(bool)
    onsets = _onsets_within(score, idx, 60.0, max_horizon=max(HORIZONS))
    fwd = forward_returns(pop["close"], onsets, HORIZONS)
    block: dict[str, Any] = {
        "n_days": int(len(pop)),
        "start": str(idx.min().date()),
        "end": str(idx.max().date()),
        "excluded_dead_days_in_window": int((~win["live"].astype(bool)).sum()),
        "ema_median": round(float(ema.median()), 4),
        "percentile_of_thrust": round(percentile_of(ema, cfg.thrust), 1),
        "percentile_of_washout": round(percentile_of(ema, cfg.washout), 1),
        "on_share": round(float(on.mean()), 4),
        "washout_share": round(float(washout.mean()), 4),
        "full_thrust_days": int(full.sum()),
        "full_thrust_share": round(float(full.mean()), 4),
        "score_ge60_days": int((score >= 60).sum()),
        "onset_events": int(len(onsets)),
        "uncond_fwd_20d_pct": round(_uncond_baseline(pop["close"], 20), 3),
    }
    for h in HORIZONS:
        vals = fwd[h].dropna().to_numpy() if h in fwd.columns else np.array([])
        block[f"event_fwd_{h}d_pct"] = round(float(np.mean(vals)), 3) if vals.size else None
        block[f"event_fwd_{h}d_n"] = int(vals.size)
    excess = _event_excess(fwd, pop["close"], 20)
    block["event_excess_20d_bps"] = None if excess is None else round(excess, 1)
    block["acceptance_pass"] = passes_acceptance(block)
    return block


def _uncond_baseline(close: pd.Series, horizon: int) -> float:
    """无条件 h 日累计收益均值（%）= 恒零维度的期望值，事件收益的对照。"""
    r = close.pct_change(horizon).dropna() * 100.0
    return float(r.mean()) if len(r) else float("nan")


def _event_excess(fwd: pd.DataFrame, close: pd.Series, horizon: int) -> float | None:
    """事件超额（bps）：mean(event h 日收益) − mean(同段无条件 h 日收益)。"""
    if fwd.empty or horizon not in fwd.columns:
        return None
    ev = fwd[horizon].dropna()
    if ev.empty:
        return None
    return float((ev.mean() - _uncond_baseline(close, horizon)) * 100.0)


def passes_acceptance(metrics: dict[str, Any], acc: dict[str, Any] = PREREG_ACCEPTANCE) -> bool:
    """机械判据：稀有度双边界 + 方向性地板（缺值即不过，禁"没测到=通过"）。"""
    ok = True
    for key in ("on_share", "washout_share", "full_thrust_share"):
        lo, hi = acc[key]
        val = metrics.get(key)
        ok = ok and val is not None and lo <= float(val) <= hi
    exc = metrics.get("event_excess_20d_bps")
    floor = acc["onset_excess_20d_bps_min"]
    ok = ok and exc is not None and float(exc) >= floor
    return bool(ok)


def grid_points() -> list[ThrustConfig]:
    """预注册网格笛卡尔积。"""
    return [ThrustConfig(thrust=t, washout=w) for t in PREREG_GRID["thrust"] for w in PREREG_GRID["washout"]]


def select_in_train(frame: pd.DataFrame) -> dict[str, Any]:
    """训练段选值：先过验收带，再取"命中率离带心最近"（目标=头部 5% 事件）。"""
    target = 0.05
    scored: list[tuple[float, str, ThrustConfig, dict[str, Any]]] = []
    for cfg in grid_points():
        m = segment_metrics(frame, cfg)
        if not m["acceptance_pass"]:
            continue
        scored.append((abs(m["on_share"] - target), f"{cfg.thrust}/{cfg.washout}", cfg, m))
    if not scored:
        return {"picked": None, "reason": "训练段无网格点通过验收带"}
    scored.sort(key=lambda x: (x[0], x[1]))
    _, _, cfg, m = scored[0]
    return {
        "picked": {"thrust": cfg.thrust, "washout": cfg.washout},
        "train_metrics": m,
    }


def run_walkforward(
    frame: pd.DataFrame,
    folds: Sequence[WalkFold],
    *,
    prereg: PreRegistrationRegistry | None = None,
    prereg_name: str = "s2_breadth_thrust_walkforward_v1",
) -> dict[str, Any]:
    """逐折"训练段选值→测试段只跑一次"，并给出生产现值跨折稳定性。"""
    if prereg is not None:
        payload = {"grid": PREREG_GRID, "acceptance": PREREG_ACCEPTANCE, "windows": PREREG_REPORT_WINDOWS}
        try:
            prereg.register(prereg_name, payload, note="OVB-4 s2_breadth_thrust 本土 walk-forward 复推")
        except RuntimeError:
            if not prereg.verify(prereg_name, payload):
                raise
    per_fold: list[dict[str, Any]] = []
    for fold in folds:
        train = frame.loc[fold.train_start : fold.train_end]
        test = frame.loc[fold.test_start : fold.test_end]
        picked = select_in_train(train)
        rec: dict[str, Any] = {
            "fold": fold.as_dict(),
            "train_days": int(train["live"].astype(bool).sum()),
            "test_days": int(test["live"].astype(bool).sum()),
            "current_in_train": segment_metrics(train, ThrustConfig()),
            "current_in_test": segment_metrics(test, ThrustConfig()),
            "train_pick": picked,
        }
        if picked["picked"] is not None:
            pcfg = ThrustConfig(**picked["picked"])
            rec["picked_in_test"] = segment_metrics(test, pcfg)
        per_fold.append(rec)

    on_shares = [float(r["current_in_test"]["on_share"]) for r in per_fold if r["test_days"] > 0]
    stability = None
    if on_shares and min(on_shares) > 0:
        stability = round(max(on_shares) / min(on_shares), 2)
    return {
        "folds": per_fold,
        "current_in_full_windows": {
            name: segment_metrics(frame, ThrustConfig(), start)
            for name, start in PREREG_REPORT_WINDOWS.items()
        },
        "cross_fold_on_share": on_shares,
        "cross_fold_stability_ratio": stability,
        "stability_limit": PREREG_ACCEPTANCE["fold_stability_max_ratio"],
    }


# ─────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────
def _default_cache_path() -> Path:
    return Path(".runtime/tmp/st-qoder-t1a-20260915/breadth_bars.parquet")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="S2 breadth_thrust 阈值 walk-forward 重校管线")
    ap.add_argument("--cache", default=str(_default_cache_path()), help="breadth parquet 缓存（临时区）")
    ap.add_argument("--out", default=".runtime/tmp/st-qoder-t1a-20260915/breadth_walkforward.json")
    ap.add_argument("--prereg", default=".runtime/tmp/st-qoder-t1a-20260915/breadth_prereg.json")
    ap.add_argument("--start", default=PREREG_SERIES_START)
    ap.add_argument("--end", default=None)
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--test-years", type=int, default=3)
    ap.add_argument("--first-test", default="2014-01-01")
    args = ap.parse_args(argv)

    frame = load_breadth(start=args.start, end=args.end, cache=args.cache)
    n_mirror = verify_mirror(frame["adv"], frame["dec"])
    folds = make_folds(
        pd.DatetimeIndex(frame.index),
        first_test_start=args.first_test,
        test_years=args.test_years,
        n_folds=args.folds,
    )
    result = run_walkforward(frame, folds, prereg=PreRegistrationRegistry(args.prereg))
    payload: dict[str, Any] = {
        "symbol": MARKET_PROXY_SYMBOL,
        "breadth_symbol": BREADTH_SYMBOL,
        "fallback_symbol": BREADTH_FALLBACK_SYMBOL,
        "data_range": [str(frame.index.min().date()), str(frame.index.max().date())],
        "n_days_raw": int(len(frame)),
        "n_days_live": int(frame["live"].astype(bool).sum()),
        "mirror_checked_days": n_mirror,
        "current_thresholds": {"thrust": CURRENT_THRUST, "washout": CURRENT_WASHOUT},
        "grid": PREREG_GRID,
        "acceptance": PREREG_ACCEPTANCE,
        "result": result,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"[breadth-wf] wrote {out_path}")
    print(json.dumps(_summary_for_print(result), ensure_ascii=False, indent=2, default=str))
    return 0


_SUMMARY_KEYS: Final[tuple[str, ...]] = (
    "n_days",
    "start",
    "end",
    "percentile_of_thrust",
    "percentile_of_washout",
    "on_share",
    "washout_share",
    "full_thrust_days",
    "full_thrust_share",
    "onset_events",
    "event_excess_20d_bps",
    "acceptance_pass",
)


def _summary_for_print(result: dict[str, Any]) -> dict[str, Any]:
    """CLI 摘要：每个报告窗口只留裁定要用的头条指标（全量在 JSON 落盘件里）。"""
    windows = {
        name: {k: block[k] for k in _SUMMARY_KEYS if k in block}
        for name, block in result["current_in_full_windows"].items()
    }
    return {
        "windows": windows,
        "per_fold_current_on_share": result["cross_fold_on_share"],
        "cross_fold_stability_ratio": result["cross_fold_stability_ratio"],
        "stability_limit": result["stability_limit"],
    }


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
