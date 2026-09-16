# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | 14 号 §4.5 / S11 节点 wyckoff_vix_mining §3
# [MODULE] zephyr.regime.validation.wyckoff_walkforward
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.regime.features.wyckoff_engine; zephyr.regime.features.market_features; zephyr.regime.validation.overfitting_guard; zephyr.data.table_registry; zephyr.infrastructure.database_service
# [CONSUMERS] WYF-3 重校施工（一次性 CLI 跑批）+ tests/regime/validation/test_wyckoff_walkforward.py
# [STARTUP] on_demand（离线校准，非运行时热路径）
# [MATURITY] validation
# [INVARIANTS] 校准段/评估段严格分离（test 段永不参与选值）; 决策日只用 ≤T-1（引擎 PIT + 段截断）; 网格与验收带先写死后跑数; 数据只读（CH reader role）; 输出只落 tmp/工作区，禁写 data/
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 段窗口无数据->ValueError; 预注册名冲突->RuntimeError（继承 PreRegistrationRegistry）; 网格点缺 key->KeyError
# [TESTS] tests/regime/validation/test_wyckoff_walkforward.py
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.12.2 #14_regime_s2_diagnosis §4.5 #WYF-3
"""
WYF-3：wyckoff 维度阈值 walk-forward 重校管线（MOD-REGIME-VAL，14 号 §4.5 方法论栈复用）。

病根：S2 confirm 的 wyckoff 析取腿（keys_or_gte wyckoff>=60）在真实数据上恒不触发
（WYF-1 双 bug 修复后仍 0 日 >=60），阈值系 2024 年拍脑袋值、从未经样本外校验。

方法论（复用本仓唯一跑过预注册闭环的 capitulation 栈，不另造轮子）：
  ① 预注册：`PREREG_GRID`/`PREREG_ACCEPTANCE` 先写死，经
     `overfitting_guard.PreRegistrationRegistry` hash 锁定，看结果前不可改；
  ② walk-forward：expanding 训练段 + 紧邻评估段，**评估段永不参与选值**，逐折只跑一次；
  ③ 事件研究：信号起始日（score 由 <gate 上穿 >=gate）的 5/20/60 日前向收益，
     与**同段无条件基线**对比（恒零维度的期望值就是该基线 → 差值即维度信息量）；
  ④ 防粘滞：S2 是一次性转换，score "永远在线" 等于噪声——故 on_share（占比）双边界
     写死为验收条件（下界防恒零、上界防误爆）；
  ⑤ WFE：逐折 OOS/IS 效率（`overfitting_guard.walk_forward_efficiency`）汇总裁定。

引擎真源纪律：候选参数一律经 `replace(DEFAULT_WYCKOFF_PARAMS, **grid_point)` 构造后
传入**生产函数** `detect_wyckoff_events`，本模块不复制判定逻辑（结构性防"诊断版与
生产版漂移"——上一代一次性诊断脚本 wyf3_lib.py 的教训）。

依据: S11 挖矿节点 wyckoff_vix_mining.md §3 / 14_regime_s2_diagnosis §4.5
Version: 0.1.0
# [ALGO_FLOW]
# I1: 000300 OHLCV（CH 只读/TableRegistry 解析）+ 生产同款派生 pct_change/vol_z
# I2: 预注册网格 PREREG_GRID + 验收带 PREREG_ACCEPTANCE + walk-forward 折定义 make_folds
# F1: 生产引擎 wyckoff_engine.detect_wyckoff_events(params=候选) 直接复用（禁诊断版双实现漂移）
# F2: segment_metrics —— 检出力/粘滞占比(on_share)/事件级前向收益 vs 无条件基线（恒零对照）
# F3: select_in_train —— 分层贪心（SC→AR→ST/Spring/Test→权重/记忆窗/门槛）+ 机械 tie-break
# F4: run_walkforward —— 逐折"训练段选值→测试段只跑一次"，WFE 汇总（overfitting_guard.assess_wfe 同族）
# F5: PreRegistrationRegistry hash 锁定网格与验收带（看数据前登记，禁事后改标准）
# O1: 逐折候选与样本外指标 DataFrame + JSON 落盘（报告真源）
# [/ALGO_FLOW]
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Final

import numpy as np
import pandas as pd

from zephyr.regime.features.market_features import volume_anomaly
from zephyr.regime.features.wyckoff_engine import (
    DEFAULT_WYCKOFF_PARAMS,
    WyckoffParams,
    detect_wyckoff_events,
    wyckoff_score_from_events,
)
from zephyr.regime.validation.overfitting_guard import PreRegistrationRegistry, walk_forward_efficiency

__all__ = [
    "PREREG_ACCEPTANCE",
    "PREREG_GRID",
    "PROBE_STAGES",
    "make_params",
    "score_from_events",
    "WalkFold",
    "build_engine_inputs",
    "evaluate_config",
    "load_market_proxy",
    "make_folds",
    "run_walkforward",
    "segment_metrics",
    "select_in_train",
]

# ── 标的与数据窗口（与生产 overlay 市场代理一致）─────────────────────────
MARKET_PROXY_SYMBOL: Final[str] = "000300"
#: 引擎内部滚动窗上限（vol_z 20 + SC 窗 ≤120 + 记忆窗 ≤250）所需预热；预热日不计任何统计
WARMUP_TRADE_DAYS: Final[int] = 260
#: PS/SC 的 low 滚动窗。不入 WyckoffParams——它是生产出口的位置参数：
#: `overlay_features.s2_wyckoff_score(..., window=60)` 默认值，且
#: `overlay_signals_builder` 调用时未覆盖 ⇒ 现网恒 60。校准必须镜像该值（禁裸写字面数）。
PROD_PS_WINDOW: Final[int] = 60

# ── 预注册：参数网格（看数据前写死；改动=新一次预注册，禁覆盖同名）────────
# 覆盖 WYF-3 §3 校准债清单 + 任务书点名轴：SC z/pct/window、AR 两道门（含消融）、
# ST/Spring 缩量系数、ST 回看窗拆分、Test 窗/放量系数、6 阶段权重、S2 confirm 门槛、
# 记忆窗（cummax 永久粘滞 → 有限窗，capitulation 同族治本）。
PREREG_GRID: Final[dict[str, Any]] = {
    "L0_sc_root": {
        "sc_vol_z": [0.0, 0.5, 1.0, 1.5, 1.8, 2.0],
        "sc_pct": [-0.03, -0.04, -0.05],
        "sc_window": [40, 60, 90, 120],
    },
    "L1_ar_doors": {
        "ar_sc_window": [10, 15, 20, 30],
        "ar_pct": [0.0, 0.005, 0.01],
        "ar_breakout_window": [5, 10, 20],
        "ar_doors": ["both", "pct_only", "breakout_only"],
    },
    "L2_st_spring_test": {
        "st_sc_window": [None, 15, 25, 40],
        "st_band": [0.02, 0.03, 0.05],
        "st_shrink": [0.7, 0.85, 1.0],
        "spring_shrink": [0.8, 1.0, 1.25],
        "test_spring_window": [20, 30, 40],
        "test_vol_ratio": [0.9, 1.0, 1.1],
    },
    "L3_score_gate": {
        "weight_variant": {
            # 变体名 → stage_weights 字典（None=沿用 DEFAULT 权重）
            "legacy": None,
            "no_ps": {"ps": 0.0, "sc": 30.0, "ar": 15.0, "st": 20.0, "spring": 40.0, "test": 20.0},
            "spring_decisive": {
                "ps": 5.0, "sc": 25.0, "ar": 10.0, "st": 15.0, "spring": 45.0, "test": 25.0,
            },
            "balanced6": {
                "ps": 10.0, "sc": 20.0, "ar": 15.0, "st": 15.0, "spring": 25.0, "test": 15.0,
            },
        },
        "memory_window": [None, 40, 60, 90, 120, 250],
        "s2_confirm_gate": [40.0, 50.0, 60.0, 70.0],
    },
}

# ── 预注册：验收带（写死，禁事后放宽凑数）───────────────────────────────
# 语义锚点：S2 是 CRISIS→RECOVERY 一次性转换。恒零=维度不存在（现状）；
# 恒一=误爆（比恒零更糟：污染每次 S2 confirm）。合格区间必须同时避开两端。
# 分层判据（关键设计）：L0-L2 是**事件集层**，此时评分门槛尚未定型，故只按
# 该层阶段的检出带+方向性判据（检出带归一到"每 1000 交易日"，随折长不变）；
# L3 是**评分/门槛层**，才用 on_share 双边界（下界防恒零、上界防误爆）。
# 排序客观量一律用该层事件（或起始事件）的前向收益 excess——不看样本外。
PREREG_ACCEPTANCE: Final[dict[str, Any]] = {
    # ── 事件集层（L0 SC / L1 AR / L2 ST·Spring·Test）──
    # 检出带 [每千日下限, 每千日上限]；Spring/Test 在短训练段可合法为 0（下限 0）
    "stage_bands_per_1000d": {
        "L0_sc_root": {"sc": [1.0, 120.0]},
        "L1_ar_doors": {"sc": [1.0, 120.0], "ar": [1.0, 200.0]},
        "L2_st_spring_test": {
            "sc": [1.0, 120.0], "ar": [1.0, 200.0], "st": [0.0, 250.0],
            "spring": [0.0, 250.0], "test": [0.0, 250.0],
        },
    },
    # 方向性（防"检出达标但语义反了"）：SC 日应为大跌，AR 日应为反弹
    "stage_pct_median": {"sc": (-9.99, -0.025), "ar": (0.003, 9.99)},
    # ── 评分/门槛层（L3）──
    "train_on_share": [0.005, 0.25],   # 占比带：下界防恒零，上界防误爆
    "train_min_onsets": 3,             # 至少 3 次独立起始事件才谈得上选值
    "test_on_share": [0.002, 0.25],
    "test_min_onsets": 2,
    # ── 信息量裁定（全折池化）──
    "horizons": [5, 20, 60],           # 前向收益交易日
    "primary_horizon": 20,
    "min_excess_bps": 0.0,             # 事件均值须严格优于同段无条件基线
    "min_hit_edge": 0.0,               # 命中率须严格优于基线命中率
    "min_t_stat": 2.0,                 # 池化 |t| >= 2 才允许"采纳阈值"（低于=证据不足）
    "min_fold_positive_ratio": 0.6,    # 至少 60% 折 excess>0
    "min_wfe": 0.6,                    # overfitting_guard 门槛（OOS/IS >=0.6 pass）
    "cluster_gap_trade_days": 20,      # 起始事件去相关合并窗（事件研究用）
    "false_recover_pct": -0.03,        # 误报定义：事件后 h 日仍跌 >=3%
}

_STAGE_COLS: Final[tuple[str, ...]] = ("ps", "sc", "ar", "st", "spring", "test")


# ─────────────────────────────────────────────────────────────────────────
# 数据装载（CH 只读 + TableRegistry 真源解析，禁硬编码表名）
# ─────────────────────────────────────────────────────────────────────────
def load_market_proxy(
    symbol: str = MARKET_PROXY_SYMBOL,
    *,
    cache: str | Path | None = None,
    conn: Any | None = None,
) -> pd.DataFrame:
    """拉取市场代理指数 OHLCV（默认 000300）。

    只读通道：`DatabaseService.get_clickhouse_conn(role="reader")`（readonly=1）；
    表名经 `TableRegistry.table("market_index_kline")` 解析（RULE-SSOT/RULE-DATA-OPS）。

    Args:
        symbol: 指数代码。
        cache: parquet 缓存路径；存在则读缓存，否则拉库后写缓存（缓存属临时区，
               由调用方指定 `.runtime/tmp/...`，禁写 `data/`）。
        conn: 注入 ClickHouse 连接（测试/复用用）。
    """
    cache_path = Path(cache) if cache else None
    if cache_path is not None and cache_path.exists():
        df = pd.read_parquet(cache_path)
        df.index = pd.to_datetime(df.index)
        return df.sort_index()

    from zephyr.data.table_registry import get_registry

    table = get_registry().table("market_index_kline")
    sql = (
        f"SELECT trade_date, open, high, low, close, volume FROM {table} "  # noqa: S608 - 表名来自 TableRegistry 真源
        "WHERE symbol = %(symbol)s ORDER BY trade_date"
    )
    if conn is None:
        from zephyr.infrastructure.database_service import DatabaseService

        conn = DatabaseService().get_clickhouse_conn(role="reader")
    rows, cols = conn.execute(sql, {"symbol": symbol}, with_column_types=True)
    frame = pd.DataFrame(rows, columns=[c for c, _ in cols])
    frame["trade_date"] = pd.to_datetime(frame["trade_date"])
    frame = frame.set_index("trade_date")
    for col in ("open", "high", "low", "close", "volume"):
        frame[col] = frame[col].astype(float)
    frame = frame.sort_index()
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(cache_path)
    return frame


def build_engine_inputs(df: pd.DataFrame) -> dict[str, pd.Series]:
    """OHLCV → 引擎入参（派生口径与生产逐项同构）。

    生产：`overlay_signals_builder._precompute` 用 close.pct_change() 与
    `volume_anomaly(volume, window=20)`（RegimeFeatureBuilder F5 默认窗）。
    """
    close = df["close"].astype(float)
    return {
        "close": close,
        "high": df["high"].astype(float),
        "low": df["low"].astype(float),
        "volume": df["volume"].astype(float),
        "pct_change": close.pct_change(),
        "vol_z": volume_anomaly(df["volume"].astype(float), window=20),
    }


# ─────────────────────────────────────────────────────────────────────────
# 候选参数构造 + 折定义
# ─────────────────────────────────────────────────────────────────────────
def make_params(grid_point: dict[str, Any], *, base: WyckoffParams | None = None) -> WyckoffParams:
    """网格点 → WyckoffParams（None 值=沿用基线；`ar_doors`/`weight_variant` 展开）。"""
    b = base or DEFAULT_WYCKOFF_PARAMS
    p = b.to_dict()
    for key, val in grid_point.items():
        if key == "ar_doors":
            p["ar_require_pct"] = val in ("both", "pct_only")
            p["ar_require_breakout"] = val in ("both", "breakout_only")
        elif key == "weight_variant":
            if val is not None:
                p["stage_weights"] = dict(val)
        elif val is None:
            continue  # None=沿用基线（如 sc_window=None → 用函数 window 入参）
        else:
            p[key] = val
    return replace(b, **p)


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


def make_folds(
    index: pd.DatetimeIndex,
    *,
    first_test_start: str | pd.Timestamp,
    test_years: int = 3,
    n_folds: int = 4,
) -> list[WalkFold]:
    """expanding 训练 + 紧邻 test 的 walk-forward 折序列（锚定起点，禁随机划分）。

    fold k: train = [series_start, test_start_k)，test = [test_start_k, test_end_k)。
    引擎内部滚动窗靠 **series 起点到 train 段之前**的历史预热（WARMUP_TRADE_DAYS），
    统计只取段窗口内的行 → 无未来信息（train 段之后的数据在选值时被物理截断）。
    """
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


def score_from_events(events: pd.DataFrame, params: WyckoffParams) -> pd.Series:
    """事件矩阵 → 评分序列。**直接委托**生产尾段 `wyckoff_score_from_events`。

    委托而非另写一遍：这样"校准口径 == 生产口径"是**结构性保证**（同一函数体），
    不再依赖 test_score_from_events_zero_drift_vs_production 的事后抓漏。
    尾段刻意不受 `_DIMENSION_STATUS` 影响（否则证伪落定后本管线无法重跑）。
    """
    return wyckoff_score_from_events(events, params)


def onset_dates(score: pd.Series, gate: float) -> pd.DatetimeIndex:
    """信号起始日：score 由 <gate 上穿 >=gate（状态机边沿，非电平）。"""
    on = score >= gate
    prev = on.shift(1, fill_value=False)
    return pd.DatetimeIndex(score.index[on & ~prev])


def merge_clusters(
    dates: pd.DatetimeIndex,
    gap_trade_days: int,
    full_index: pd.DatetimeIndex,
) -> pd.DatetimeIndex:
    """起始事件去相关：相邻间隔 <= gap_trade_days 个交易日的合并为一簇，保留簇首日。

    事件研究要求样本近似独立（前向窗 20 日内的连续起始日属同一"见底事件"，
    计两次会人为放大 t 值）。
    """
    if len(dates) == 0:
        return pd.DatetimeIndex([])
    pos = full_index.get_indexer(pd.DatetimeIndex(dates), method="ffill")
    kept: list[pd.Timestamp] = []
    last_pos = -(10**9)
    for d, i in zip(dates, pos, strict=True):
        if i - last_pos > gap_trade_days:
            kept.append(d)
            last_pos = i
    return pd.DatetimeIndex(kept)


def forward_returns(close: pd.Series, dates: pd.DatetimeIndex, horizons: Sequence[int]) -> pd.DataFrame:
    """事件日 → h 个交易日前向收益（严格只用 >t 的收盘，决策日 t 本身不含未来）。

    r_h(t) = close[t+h]/close[t] - 1；t+h 越界 → NaN（诚实缺失，禁回填）。
    """
    idx = close.index
    pos = idx.get_indexer(dates)
    vals = close.to_numpy(dtype=float)
    out = {}
    for h in horizons:
        arr = np.full(len(dates), np.nan)
        for k, i in enumerate(pos):
            j = i + int(h)
            if 0 <= i < len(vals) and j < len(vals) and vals[i] > 0:
                arr[k] = vals[j] / vals[i] - 1.0
        out[f"r{h}"] = arr
    return pd.DataFrame(out, index=dates)


def _event_study_block(
    close: pd.Series,
    event_days: pd.DatetimeIndex,
    base: pd.DataFrame,
    horizons: Sequence[int],
    false_recover_pct: float,
    *,
    prefix: str = "",
) -> dict[str, float]:
    """事件日集合 → 前向收益 vs 基线日集合的指标块（命中率/超额/t/误报率）。

    基线=同段**全部**交易日的无条件前向收益。恒零维度不改变任何条件集，其期望
    即该基线 → `excess{h}` 就是"该维度带来的信息量"，为 0/负即无信息（证伪）。
    """
    fwd = forward_returns(close, event_days, horizons) if len(event_days) else pd.DataFrame(
        columns=[f"r{h}" for h in horizons], index=pd.DatetimeIndex([])
    )
    out: dict[str, float] = {f"{prefix}events": float(len(event_days))}
    for h in horizons:
        col = f"r{h}"
        ev_r = fwd[col].dropna()
        base_r = base[col].dropna()
        ev_mean = float(ev_r.mean()) if len(ev_r) else float("nan")
        b_mean = float(base_r.mean()) if len(base_r) else float("nan")
        ev_hit = float((ev_r > 0).mean()) if len(ev_r) else float("nan")
        b_hit = float((base_r > 0).mean()) if len(base_r) else float("nan")
        sd = float(ev_r.std(ddof=1)) if len(ev_r) > 1 else float("nan")
        t_stat = (
            (ev_mean - b_mean) / (sd / np.sqrt(len(ev_r)))
            if len(ev_r) > 1 and sd == sd and sd > 0
            else float("nan")
        )
        out[f"{prefix}mean{h}"] = ev_mean
        out[f"{prefix}med{h}"] = float(ev_r.median()) if len(ev_r) else float("nan")
        out[f"{prefix}base_mean{h}"] = b_mean
        out[f"{prefix}excess{h}"] = ev_mean - b_mean if ev_mean == ev_mean and b_mean == b_mean else float("nan")
        out[f"{prefix}hit{h}"] = ev_hit
        out[f"{prefix}base_hit{h}"] = b_hit
        out[f"{prefix}hit_edge{h}"] = ev_hit - b_hit if ev_hit == ev_hit and b_hit == b_hit else float("nan")
        out[f"{prefix}t{h}"] = t_stat
        out[f"{prefix}fp{h}_rate"] = float((ev_r <= false_recover_pct).mean()) if len(ev_r) else float("nan")
    return out


def segment_metrics(
    inputs: dict[str, pd.Series],
    params: WyckoffParams,
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    warmup_days: int = WARMUP_TRADE_DAYS,
    horizons: Sequence[int] = (5, 20, 60),
    cluster_gap_trade_days: int = 20,
    false_recover_pct: float = -0.03,
    probe_stages: Sequence[str] = (),
    include_score: bool = True,
) -> dict[str, Any]:
    """一个段（训练或评估）的完整指标——**核心裁定口径**。

    口径：引擎在**全序列**上跑（保证 PIT 预热），统计只取 [start+warmup, end]。
    未来信息隔离靠调用方传入的 end（评估段之后的数据既不参与选值，其前向收益
    也被 `close.loc[:end]` 截断 → 训练段指标不会偷看评估段行情）。

    Args:
        probe_stages: 额外把这些阶段的**事件日**当作事件做研究（事件集层的排序客观量，
            输出前缀 `probe_<stage>_`）——上游冻结后本层检出阶段的自身信息量。
        include_score: False 时跳过评分层指标（事件集层不需要，省一半算力）。

    Returns 摘要：
      days               段内统计交易日数
      stage_days         6 阶段各自触发日数
      stage_pct_median   各阶段触发日的涨跌幅中位数（方向性判据）
      on_days/on_share   score>=gate 的日数与占比（误爆控制）
      n_events           合并后的起始事件数
      excess{h}/hit{h}/t{h}/fp{h}_rate  起始事件 vs 无条件基线（恒零=基线）
      probe_<stage>_*    probe_stages 各阶段事件日的同口径指标
      max_score          段内 score 峰值
    """
    close = inputs["close"]
    full = pd.DatetimeIndex(close.index)
    gate = params.s2_confirm_gate
    events = detect_wyckoff_events(
        inputs["close"], inputs["high"], inputs["low"], inputs["volume"],
        inputs["pct_change"], inputs["vol_z"], PROD_PS_WINDOW, params=params,
    )
    score = score_from_events(events, params)

    stat_days = full[(full >= start) & (full <= end)]
    # 预热日（段首 WARMUP_TRADE_DAYS）不参与统计：滚动窗未凑满，触发无意义
    seg_days = stat_days[warmup_days:] if warmup_days else stat_days
    if len(seg_days) == 0:
        msg = f"段 {start.date()}~{end.date()} 扣除 {warmup_days} 日预热后为空"
        raise ValueError(msg)
    seg = slice(seg_days[0], seg_days[-1])

    ev_seg = events.loc[seg]
    score_seg = score.loc[seg]
    close_seg = close.loc[:end]  # 前向收益不越段尾（训练段禁看后续行情）

    out: dict[str, Any] = {
        "days": int(len(seg_days)),
        "gate": float(gate),
        "memory_window": params.memory_window,
        "max_score": float(score_seg.max()) if len(score_seg) else 0.0,
        "stage_days": {c: float(ev_seg[c].sum()) for c in _STAGE_COLS},
        "stage_pct_median": {
            c: (
                float(inputs["pct_change"].loc[seg][ev_seg[c] > 0].median())
                if float(ev_seg[c].sum()) > 0
                else float("nan")
            )
            for c in _STAGE_COLS
        },
    }
    base = forward_returns(close_seg, seg_days, horizons)  # 无条件基线（恒零维度的期望）
    if include_score:
        on_days = int((score_seg >= gate).sum())
        evts = merge_clusters(onset_dates(score_seg, gate), cluster_gap_trade_days, score_seg.index)
        out["on_days"] = on_days
        out["on_share"] = on_days / max(len(seg_days), 1)
        out["n_events"] = int(len(evts))
        out.update(_event_study_block(close_seg, evts, base, horizons, false_recover_pct))
    for stage in probe_stages:
        stage_days = pd.DatetimeIndex(ev_seg.index[ev_seg[stage] > 0])
        out.update(
            _event_study_block(
                close_seg, stage_days, base, horizons, false_recover_pct,
                prefix=f"probe_{stage}_",
            )
        )
    return out


def latch_dichotomy(
    inputs: dict[str, pd.Series],
    params: WyckoffParams,
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    memory_windows: Sequence[int | None] = (None, 40, 60, 90, 120, 250),
    warmup_days: int = WARMUP_TRADE_DAYS,
    acc: dict[str, Any] = PREREG_ACCEPTANCE,
) -> pd.DataFrame:
    """同一事件集在"永久粘滞(cummax) vs 有限记忆窗"下的占比-信息量对照。

    结构证明用：memory_window=None 时 score 单调不减（阶段一旦出现过就永久计分），
    因此对任意事件集，`on_share` 只能取两端——事件集永不齐活 ⇒ 恒 0（维度死）；
    齐活过一次 ⇒ 该日之后恒在线（误爆，且与后续行情无关）。本函数把该二象性
    量化成表，是 WYF-3 "阈值救不了该维度"论证的直接证据。
    """
    h = acc["primary_horizon"]
    rows: list[dict[str, Any]] = []
    for mw in memory_windows:
        p = replace(params, memory_window=mw)
        m = segment_metrics(inputs, p, start=start, end=end, warmup_days=warmup_days, horizons=(h,))
        rows.append(
            {
                "memory_window": mw if mw is not None else "inf(cummax)",
                "on_days": m["on_days"],
                "on_share": m["on_share"],
                "n_events": m["n_events"],
                "max_score": m["max_score"],
                f"excess{h}": m[f"excess{h}"],
                f"hit{h}": m[f"hit{h}"],
                f"t{h}": m[f"t{h}"],
            }
        )
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────
# 机械选值（分层贪心，准则先写死）
# ─────────────────────────────────────────────────────────────────────────
@dataclass
class LayerResult:
    """一层的扫描结果（候选表 + 选值）。"""

    layer: str
    chosen: dict[str, Any]
    candidates: list[dict[str, Any]] = field(default_factory=list)
    passed: list[dict[str, Any]] = field(default_factory=list)


def _band_pass_stage(metrics: dict[str, Any], stage: str, band: Sequence[float], acc: dict[str, Any]) -> bool:
    """单阶段检出带（每千交易日归一）+ 方向性中位数带。"""
    days = metrics["stage_days"][stage]
    per_1000 = days / max(metrics["days"], 1) * 1000.0
    if not (band[0] <= per_1000 <= band[1]):
        return False
    dband = acc["stage_pct_median"].get(stage)
    if dband is not None and days > 0:
        med = metrics["stage_pct_median"][stage]
        if not (med == med and dband[0] <= med <= dband[1]):
            return False
    return True


def _passes_layer(
    layer: str,
    metrics: dict[str, Any],
    acc: dict[str, Any],
) -> bool:
    """分层判据（预注册）：事件集层看检出带/方向性；评分层看占比带/起始事件数。"""
    bands = acc["stage_bands_per_1000d"].get(layer)
    if bands is not None:
        return all(_band_pass_stage(metrics, st, bd, acc) for st, bd in bands.items())
    lo, hi = acc["train_on_share"]
    if not (lo <= metrics.get("on_share", 0.0) <= hi):
        return False
    return metrics.get("n_events", 0) >= acc["train_min_onsets"]


#: 每层的探测阶段（评分层无探测=用起始事件指标）
_EVENT_LAYERS: Final[frozenset[str]] = frozenset({"L0_sc_root", "L1_ar_doors", "L2_st_spring_test"})
PROBE_STAGES: Final[dict[str, tuple[str, ...]]] = {
    "L0_sc_root": ("sc",),
    "L1_ar_doors": ("ar",),
    "L2_st_spring_test": ("st", "spring", "test"),
    "L3_score_gate": (),
}


def _rank_objective(
    layer: str,
    metrics: dict[str, Any],
    h: int,
) -> float:
    """排序客观量：事件层=本层各阶段事件前向超额均值；评分层=起始事件前向超额。"""
    probes = PROBE_STAGES[layer]
    if probes:
        vals = [
            metrics[f"probe_{st}_excess{h}"]
            for st in probes
            if metrics.get(f"probe_{st}_events", 0.0) > 0
        ]
        vals = [float(v) for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")
    return float(metrics.get(f"excess{h}", float("nan")))


def _dev_from_default(point: dict[str, Any]) -> float:
    """与现值的标准化偏离（最小改动原则的 tie-break 度量）。"""
    base = DEFAULT_WYCKOFF_PARAMS.to_dict()
    total = 0.0
    for k, v in point.items():
        if k in ("weight_variant", "s2_confirm_gate") or v is None:
            total += 0.0 if v in (None, "legacy", "both") else 1.0
            continue
        cur = base.get(k)
        if isinstance(v, bool) or isinstance(cur, bool):
            total += float(bool(v) != bool(cur))
        elif isinstance(v, (int, float)) and isinstance(cur, (int, float)):
            total += min(abs(float(v) - float(cur)) / max(abs(float(cur)), 1e-9), 4.0)
    return total


def select_in_train(
    inputs: dict[str, pd.Series],
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    acc: dict[str, Any] = PREREG_ACCEPTANCE,
    grid: dict[str, Any] = PREREG_GRID,
) -> tuple[WyckoffParams, list[LayerResult]]:
    """训练段内分层贪心选值（SC→AR→ST/Spring/Test→权重/记忆窗/门槛）。

    准则（预注册，机械可重放）：
      1. 上游层选值冻结后只作常量传入下游层；
      2. 候选须过本层判据 `_passes_layer`；
      3. 合格者按 `_rank_objective`（本层事件的样本**内**前向超额）取最大；
      4. 并列取与现值偏离最小者（最小改动原则）；
      5. 本层无合格者 → 保持基线值并登记"该层重校失败"（合法终态，禁凑数）。
    评估段数据在本函数内被 `end` 物理截断，永不参与决策。
    """
    h = acc["primary_horizon"]
    trace: list[LayerResult] = []
    chosen: dict[str, Any] = {}

    def _sweep(layer: str, points: list[dict[str, Any]]) -> None:
        probes = PROBE_STAGES[layer]
        cands: list[dict[str, Any]] = []
        for pt in points:
            if _dedupe_skip(pt):
                continue
            merged = {**chosen, **pt}
            params = make_params(merged)
            m = segment_metrics(
                inputs, params, start=start, end=end, horizons=(h,),
                probe_stages=probes, include_score=layer not in _EVENT_LAYERS,
            )
            m["dev"] = _dev_from_default(pt)
            cands.append({"point": merged, "layer_point": pt, "params": params, "m": m})
        passed = [c for c in cands if _passes_layer(layer, c["m"], acc)]
        if passed:
            best = max(
                passed,
                key=lambda c: (_rank_objective(layer, c["m"], h), -c["m"]["dev"]),
            )
            chosen.update(best["layer_point"])
            trace.append(LayerResult(layer, dict(best["layer_point"]), cands, passed))
        else:
            trace.append(LayerResult(layer, {}, cands, []))

    _sweep("L0_sc_root", _cartesian(grid["L0_sc_root"]))
    _sweep("L1_ar_doors", _cartesian(grid["L1_ar_doors"]))
    _sweep("L2_st_spring_test", _cartesian(grid["L2_st_spring_test"]))
    _sweep(
        "L3_score_gate",
        _cartesian(
            {
                "weight_variant": list(grid["L3_score_gate"]["weight_variant"].values()),
                "memory_window": grid["L3_score_gate"]["memory_window"],
                "s2_confirm_gate": grid["L3_score_gate"]["s2_confirm_gate"],
            }
        ),
    )
    return make_params(chosen), trace


def _dedupe_skip(point: dict[str, Any]) -> bool:
    """门消融时无关参数去重（ar_doors=pct_only 时 ar_breakout_window 无意义）。"""
    if point.get("ar_doors") == "pct_only":
        return point.get("ar_breakout_window") != PREREG_GRID["L1_ar_doors"]["ar_breakout_window"][0]
    if point.get("ar_doors") == "breakout_only":
        return point.get("ar_pct") != PREREG_GRID["L1_ar_doors"]["ar_pct"][0]
    return False


def _cartesian(grid: dict[str, Sequence[Any]]) -> list[dict[str, Any]]:
    keys = list(grid)
    out: list[dict[str, Any]] = [{}]
    for k in keys:
        out = [{**acc, k: v} for acc in out for v in grid[k]]
    return out


# ─────────────────────────────────────────────────────────────────────────
# walk-forward 主流程
# ─────────────────────────────────────────────────────────────────────────
def evaluate_config(inputs: dict[str, pd.Series], params: WyckoffParams, fold: WalkFold) -> dict[str, Any]:
    """一折完整记录：训练段（选值依据）+ 评估段（样本外，只跑一次）。"""
    tr = segment_metrics(
        inputs, params, start=fold.train_start, end=fold.train_end,
        horizons=PREREG_ACCEPTANCE["horizons"],
    )
    te = segment_metrics(
        inputs, params, start=fold.test_start, end=fold.test_end,
        warmup_days=0,  # 评估段起点即引擎已预热处（全序列预热历史在 train 侧）
        horizons=PREREG_ACCEPTANCE["horizons"],
    )
    return {"fold": fold.as_dict(), "params": params.to_dict(), "train": tr, "test": te}


def run_walkforward(
    inputs: dict[str, pd.Series],
    folds: Sequence[WalkFold],
    *,
    acc: dict[str, Any] = PREREG_ACCEPTANCE,
    grid: dict[str, Any] = PREREG_GRID,
    prereg: PreRegistrationRegistry | None = None,
    prereg_name: str = "wyf3_lane_f_grid",
    fixed_params: WyckoffParams | None = None,
) -> dict[str, Any]:
    """跑全部折：逐折在**训练段**选值，随后在**紧邻评估段**只跑一次。

    Args:
        fixed_params: 给定时跳过选值，直接用该参数集在每折评估（用于"现值/终选值"
                      的对照复跑与证伪检验）。
    """
    if prereg is not None:
        payload = {"grid": grid, "acceptance": acc, "n_folds": len(folds)}
        try:
            prereg.register(prereg_name, payload, note="WYF-3 lane F 预注册（看数据前写死）")
        except RuntimeError:
            if not prereg.verify(prereg_name, payload):
                msg = f"预注册 '{prereg_name}' 内容与登记不一致（禁事后改标准）"
                raise RuntimeError(msg) from None
    per_fold: list[dict[str, Any]] = []
    for fold in folds:
        if fixed_params is not None:
            chosen, trace = fixed_params, []
        else:
            chosen, trace = select_in_train(
                inputs, start=fold.train_start, end=fold.train_end, acc=acc, grid=grid
            )
        rec = evaluate_config(inputs, chosen, fold)
        rec["selection"] = [
            {"layer": t.layer, "chosen": t.chosen, "n_cand": len(t.candidates), "n_pass": len(t.passed)}
            for t in trace
        ]
        per_fold.append(rec)
    return {"folds": per_fold, "summary": summarize(per_fold, acc)}


def _mean_finite(vals: Sequence[float]) -> float:
    """均值（跳过 NaN/None；全 NaN/空 → NaN，诚实标注不可判）。"""
    fin = [float(v) for v in vals if v is not None and v == v]
    return float(np.mean(fin)) if fin else float("nan")


def summarize(fold_results: Sequence[dict[str, Any]], acc: dict[str, Any] = PREREG_ACCEPTANCE) -> dict[str, Any]:
    """池化样本外裁定：excess>0 折占比、池化 t、WFE、误爆/恒零、采纳 or 证伪。

    裁定口径（预注册 §验收带，禁事后放宽）：
      adopt=True 需要同时满足——池化 excess_主期限 > 0、命中率优于基线、
      >=min_fold_positive_ratio 折为正、池化 t（各折带符号 t 的 Stouffer 合并）>= min_t_stat（证据强度）、
      无任何折恒零、无任何折误爆。任一不满足 → 证伪（阈值不可救）。
    """
    h = acc["primary_horizon"]
    ex_key, t_key, hit_key = f"excess{h}", f"t{h}", f"hit_edge{h}"
    te = [f["test"] for f in fold_results]
    tr = [f["train"] for f in fold_results]

    def ok(v: Any) -> bool:
        """可用数值（None=JSON 往返后的缺失，与 NaN 同列"不可判"）。"""
        return v is not None and v == v

    finite_te = [float(v) for v in (d[ex_key] for d in te) if ok(v)]
    pos_ratio = (sum(1 for v in finite_te if v > 0) / len(finite_te)) if finite_te else float("nan")
    n_events = sum(int(d["n_events"]) for d in te)
    pooled_mean = float(np.mean(finite_te)) if finite_te else float("nan")
    pooled_se = float(np.std(finite_te, ddof=1) / np.sqrt(len(finite_te))) if len(finite_te) > 1 else float("nan")
    # 池化 t：折间事件簇经 merge_clusters 去相关 ⇒ 近似独立，用 Stouffer 合并**带符号**的折 t：
    # Z = Σt_i/√k（k 单调、可为负；k=1 时退化为该折自身的 t）。禁只取正 t（那会把反证折丢掉）。
    ts = [float(d[t_key]) for d in te if ok(d[t_key])]
    pooled_t = float(np.sum(ts) / np.sqrt(len(ts))) if ts else float("nan")
    wfe = [
        walk_forward_efficiency(d_te[ex_key], d_tr[ex_key])
        for d_te, d_tr in zip(te, tr, strict=True)
        if ok(d_tr[ex_key]) and d_tr[ex_key] > 0 and ok(d_te[ex_key])
    ]
    shares_te = [float(d["on_share"]) for d in te]
    lo, hi = acc["test_on_share"]
    blast = [s_ for s_ in shares_te if s_ > hi]
    dead = [s_ for s_ in shares_te if s_ < lo]
    hit_edge_mean = _mean_finite([d[hit_key] for d in te])
    verdict: dict[str, Any] = {
        "primary_horizon": h,
        "n_folds": len(fold_results),
        "test_events_pooled": n_events,
        "test_excess_mean": pooled_mean,
        "test_excess_se": pooled_se,
        "test_fold_positive_ratio": pos_ratio,
        "pooled_t_approx": pooled_t,
        "test_hit_edge_mean": hit_edge_mean,
        "test_max_on_share": max(shares_te) if shares_te else float("nan"),
        "test_dead_folds": len(dead),
        "test_blast_folds": len(blast),
        "wfe_evaluable_folds": len(wfe),
        "wfe_mean": _mean_finite(wfe),
        "train_excess_mean": _mean_finite([d[ex_key] for d in tr]),
    }
    verdict["adopt"] = bool(
        pooled_mean == pooled_mean
        and pooled_mean > acc["min_excess_bps"]
        and hit_edge_mean == hit_edge_mean
        and hit_edge_mean > acc["min_hit_edge"]
        and pos_ratio == pos_ratio
        and pos_ratio >= acc["min_fold_positive_ratio"]
        and pooled_t == pooled_t
        and pooled_t >= acc["min_t_stat"]
        and not blast
        and not dead
    )
    verdict["n_test_events_floor_ok"] = n_events >= acc["test_min_onsets"]
    return verdict


# ─────────────────────────────────────────────────────────────────────────
# CLI（一次性跑批：拉数→预注册→扫描→JSON 落盘）
# ─────────────────────────────────────────────────────────────────────────
def _default_cache_path() -> Path:
    return Path(".runtime/tmp/lane_f_wyf3/hs300_proxy.parquet")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="WYF-3 wyckoff 阈值 walk-forward 重校管线")
    ap.add_argument("--cache", default=str(_default_cache_path()), help="OHLCV parquet 缓存（临时区）")
    ap.add_argument("--out", default=".runtime/tmp/lane_f_wyf3/wyf3_walkforward.json", help="结果 JSON")
    ap.add_argument("--prereg", default=".runtime/tmp/lane_f_wyf3/wyf3_prereg.json", help="预注册 JSON")
    ap.add_argument("--no-select", action="store_true", help="跳过选值，仅评估现值基线")
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--test-years", type=int, default=3)
    ap.add_argument("--first-test", default="2013-01-01")
    ap.add_argument("--symbol", default=MARKET_PROXY_SYMBOL)
    args = ap.parse_args(argv)

    df = load_market_proxy(args.symbol, cache=args.cache)
    inputs = build_engine_inputs(df)
    folds = make_folds(
        pd.DatetimeIndex(inputs["close"].index),
        first_test_start=args.first_test,
        test_years=args.test_years,
        n_folds=args.folds,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "symbol": args.symbol,
        "data_range": [str(df.index.min().date()), str(df.index.max().date())],
        "n_days": int(len(df)),
        "folds": [f.as_dict() for f in folds],
        "grid": PREREG_GRID,
        "acceptance": PREREG_ACCEPTANCE,
    }
    if args.no_select:
        recs = [evaluate_config(inputs, DEFAULT_WYCKOFF_PARAMS, f) for f in folds]
        payload["baseline_current_params"] = {"folds": recs, "summary": summarize(recs)}
    else:
        reg = PreRegistrationRegistry(args.prereg)
        payload.update(run_walkforward(inputs, folds, prereg=reg))
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"[wyf3] wrote {out_path}")
    print(json.dumps(payload.get("summary", {}), ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
