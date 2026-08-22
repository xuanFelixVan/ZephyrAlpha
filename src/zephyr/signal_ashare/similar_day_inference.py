# [BLUEPRINT] MOD-SIG-063 | 待统筹登记（blueprint 未建，真源=44号备忘录 §9.3 + 92号清单 §8.1，M1-③ 剩余走势推演——相似日 KNN）
# [MODULE] zephyr.signal_ashare.similar_day_inference
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy; pandas; zephyr.signal_ashare.sentiment_cycle（28号五阶段定义 PHASE_ORDER/SentimentPhase 只读复用，不重复造）
# [CONSUMERS] （数据期前无——候选消费方：尾盘决策 closing_session_decision、M2 边界修正引擎（44号 §9.5）、prediction_log 落库（92号 §7.13））
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 不出点位只出三档情景概率（90号 §7 哲学，prob_strong+prob_flat+prob_weak=1，不预测点位/收益幅度）；历史不足 D<60 或近邻平均距离超阈 → 退化五阶段转移先验兜底；history_store 注入式（本模块零 SQL，生产=market_breadth_snapshot 读取器）；to_dict JSON 可序列化
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md §9.3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] today_series 为空/特征列全缺/可用历史不足/近邻距离超阈 → 退化先验兜底不抛（fallback_used=True+fallback_reason 留痕）；历史日缺 ts/index_price/有效点不足 → 该日剔除并计数不抛；ts 列缺失或含非法时刻值 → ValueError（调用方契约违例，fail-closed）
# [TESTS] tests/signal_ashare/test_similar_day_inference.py
# [A_module] module_id=MOD-SIG-063 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-063 — 相似日 KNN 剩余走势推演（44号备忘录 §9.3，M1-③；92号清单 §8.1）。

纪律（90号 §7 哲学）：只输出尾盘三档情景概率 P(走强/持平/转弱) + 五阶段转移概率，
不输出点位/收益幅度预测。是状态推演器不是因子（44号 §2.1 裁定：不登记 factor_registry）。

算法链路（44号 §9.3 逐条）：
  ① 特征向量：当日 09:30→当前时刻曲线族重采样到 30 个时点（等距时钟分钟网格，
     np.interp 线性插值；午休不剔除，按时钟分钟连续轴处理）：
     breadth_vel / lu_net / vol_extrap_ratio / yw_spread / if_basis 五维。
  ② 匹配：对历史 D 个交易日同时刻切片算相关性距离，取 k=10 近邻。
     距离选 Pearson 距离（1-corr）不选欧氏——理由：五维曲线量纲各异
     （家数/比值/价差/基差点），Pearson 对尺度与平移天然不变，免跨量纲归一化；
     且匹配语义是"曲线族协同形态相似"而非绝对水位一致（同为升势但水位不同的两日
     在欧氏距离下会被误判相异）；同时对齐 44号 §9.3 "相关性距离"原文。
  ③ 输出：P(尾盘走强/持平/转弱) = 近邻中剩余时段收益 >+0.3% / ±0.3% 内 / <-0.3%
     的占比；另输出五阶段转移概率（先验，28号阶段转移平滑口径；后验更新留数据期）。
  ④ 兜底：D<60 或近邻平均距离 > 阈值 → 退化五阶段转移先验（28号阶段转移表，
     复用 sentiment_cycle.PHASE_ORDER/SentimentPhase + diag=0.6 邻阶各 0.2 平滑参数）。
  ⑤ 纪律开关：walk-forward 验证命中率 <55% → 自动停用（enabled=False + disabled
     标注）；命中率统计接口留 stub（数据期接 prediction_log 校准）。

快照序列 DataFrame 列契约（today_series 与历史日帧共用，生产=market_breadth_snapshot
分钟快照表，8.2 并行施工中；本模块按注入消费，不直查库）：
  - ts               快照时刻（pandas.Timestamp / datetime.time / "HH:MM" 字符串 /
                     数值分钟轴均可，统一折算当日时钟分钟）
  - breadth_vel      float，涨跌加速度曲线（涨跌家数净增的变化速率，口径由采集层定）
  - lu_net           float，涨停净数曲线（涨停数−跌停数）
  - vol_extrap_ratio float，量能外推比曲线（ŷ_full / 20 日均量，44号 §9.4 口径）
  - yw_spread        float，黄白线剪刀差曲线（加权指数收益−等权指数收益，小数）
  - if_basis         float，可选，IF 基差曲线（缺列 → 该维剔除并重配权重，notes 留痕）
  - index_price      float，仅历史日帧需要（剩余时段收益标签 = 收盘/当前−1；
                     today_series 无需此列，有则忽略）

history_store 契约：可迭代对象，逐元素=一个历史交易日的全时段分钟快照 DataFrame
（须覆盖 session_close 以计算标签；ts ≤ 当前时刻的部分参与同时刻切片匹配）。
生产实现=market_breadth_snapshot 读取器（后续波次接）；当前零数据积累 → 恒走兜底分支。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Final, Iterable, Optional

import numpy as np
import pandas as pd

from zephyr.signal_ashare.sentiment_cycle import PHASE_ORDER, SentimentPhase

# ------------------------------------------------------------------
# 常量（容器 Final）
# ------------------------------------------------------------------
TS_COLUMN: Final = "ts"
LABEL_PRICE_COLUMN: Final = "index_price"
BASE_FEATURE_COLUMNS: Final = ("breadth_vel", "lu_net", "vol_extrap_ratio", "yw_spread")
OPTIONAL_FEATURE_COLUMNS: Final = ("if_basis",)  # 缺列剔除并重配权重
FEATURE_COLUMNS: Final = BASE_FEATURE_COLUMNS + OPTIONAL_FEATURE_COLUMNS

STRONG_LABEL: Final = "走强"
FLAT_LABEL: Final = "持平"
WEAK_LABEL: Final = "转弱"

# 28号阶段转移平滑参数（对齐 sentiment_cycle._apply_transition_smoothing diag_weight=0.6：
# 对角线 0.6，相邻阶段各 0.2，边界自循环收编）——复用其口径不另造转移矩阵。
TRANSITION_DIAG_WEIGHT: Final = 0.6

# 相邻有向边方向注解（PHASE_ORDER 轴下标 (i→j)）：
# 升温边（→尾盘走强倾向）：冰点→反核→主升→疯狂；退潮→疯狂（反抽回暖）
_TRANSITION_WARMING_EDGES: Final = frozenset({(0, 1), (1, 2), (2, 3), (4, 3)})
# 降温边（→尾盘转弱倾向）：主升→反核→冰点；疯狂→退潮、疯狂→主升（见顶回落）
_TRANSITION_COOLING_EDGES: Final = frozenset({(1, 0), (2, 1), (3, 2), (3, 4)})


# ------------------------------------------------------------------
# 配置与输出
# ------------------------------------------------------------------
@dataclass(frozen=True)
class SimilarDayConfig:
    """相似日推演配置（frozen 容器）。"""

    k: int = 10  # 近邻数（44号 §9.3 k=10）
    min_history_days: int = 60  # D≥60 才启用 KNN，否则退化先验
    max_mean_distance: float = 0.35  # 近邻平均 Pearson 距离阈值（≈平均相关 0.65），超阈退化先验
    strong_threshold: float = 0.003  # 剩余时段收益 >+0.3% → 走强
    weak_threshold: float = -0.003  # 剩余时段收益 <-0.3% → 转弱
    grid_points: int = 30  # 重采样时点数（44号 §9.3 = 30）
    session_open: str = "09:30"
    session_close: str = "15:00"
    feature_weights: dict[str, float] = field(
        default_factory=lambda: {name: 1.0 / len(FEATURE_COLUMNS) for name in FEATURE_COLUMNS}
    )  # 默认五维等权；缺维时按剩余维重配归一
    current_phase: str | None = None  # 当前情绪阶段（SentimentPhase name 或中文值）；None → 均匀先验
    now: str | None = None  # 当前时刻 "HH:MM" 钉定（测试/回放用）；None → 取 today_series 最大 ts
    walkforward_hit_rate: float | None = None  # walk-forward 命中率（数据期回填）；<hit_rate_floor → 停用
    hit_rate_floor: float = 0.55  # 44号 §9.3 纪律：命中率 <55% → 自动停用


@dataclass
class SimilarDayInference:
    """尾盘三档情景概率 + 五阶段转移概率输出（to_dict JSON 可序列化）。"""

    enabled: bool  # walk-forward 纪律开关（命中率<55% → False）
    disabled_reason: str | None
    fallback_used: bool  # True=退化五阶段转移先验分支
    fallback_reason: str | None
    prob_strong: float  # P(尾盘走强) = 近邻剩余收益 >+0.3% 占比
    prob_flat: float  # P(持平) = ±0.3% 内占比
    prob_weak: float  # P(转弱) = <-0.3% 占比
    dominant_scenario: str  # 走强/持平/转弱（argmax；平票宁标"持平"不编方向）
    n_history_days: int  # 参与匹配的有效历史日数 D
    n_neighbors: int  # 实际近邻数（KNN 路径=k，兜底=0）
    mean_neighbor_distance: float | None  # 近邻平均 Pearson 距离（兜底=None）
    features_used: list[str]  # 实际参与距离计算的特征维（缺维剔除后）
    current_phase: str | None  # 当前阶段中文值（None=未提供）
    phase_transition_prob: dict[str, float]  # 五阶段一步转移概率（先验；后验留数据期），key=阶段中文值
    notes: list[str]

    def to_dict(self) -> dict:
        """asdict 全基本类型，json.dumps 直序列化。"""
        return asdict(self)


# ------------------------------------------------------------------
# 命中率统计接口（stub——数据期校准，44号 §9.3 纪律）
# ------------------------------------------------------------------
def update_hit_rate_stats(
    predictions: list[SimilarDayInference],
    actual_tail_returns: list[float],
) -> float:
    """walk-forward 命中率统计 stub（数据期接 prediction_log 回放校准后回填实现）。

    口径预留：命中率 = 预测 dominant_scenario 与实际尾盘档位（±0.3% 阈值同 config）
    一致的比例；<55% → 生产配置应将 walkforward_hit_rate 回填触发 enabled=False。
    当前零数据积累，未实现。
    """
    raise NotImplementedError("命中率统计留数据期实现（接 prediction_log 回放，44号 §9.3）")


# ------------------------------------------------------------------
# 内部工具
# ------------------------------------------------------------------
def _ts_to_minutes(value) -> float:
    """快照时刻 → 当日时钟分钟（支持 Timestamp/datetime/time/"HH:MM"/数值分钟）。"""
    if isinstance(value, str):
        parts = value.split(":")
        return int(parts[0]) * 60.0 + int(parts[1])
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return float(value.hour) * 60.0 + float(value.minute) + float(getattr(value, "second", 0)) / 60.0
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    raise ValueError(f"非法 ts 时刻值: {value!r}（契约：Timestamp/time/'HH:MM'/分钟数）")


def _hhmm_to_minutes(hhmm: str) -> float:
    hh, mm = hhmm.split(":")[:2]
    return int(hh) * 60.0 + int(mm)


def _resample_to_grid(df: pd.DataFrame, value_col: str, grid: np.ndarray) -> np.ndarray | None:
    """单列曲线按时钟分钟轴线性插值重采样到 grid；列缺/有效点 <2 → None（剔除不抛）。"""
    if value_col not in df.columns or len(df) < 2:
        return None
    minutes = df[TS_COLUMN].map(_ts_to_minutes).to_numpy(dtype=float)
    values = df[value_col].to_numpy(dtype=float)
    mask = ~(np.isnan(minutes) | np.isnan(values))
    if mask.sum() < 2:
        return None
    order = np.argsort(minutes[mask])
    return np.interp(grid, minutes[mask][order], values[mask][order])


def _pearson_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson 距离 = 1-corr ∈ [0,2]；零方差守卫：双常数且相等 → 0，否则 → 1（最不相似）。"""
    if a.std() < 1e-12 or b.std() < 1e-12:
        return 0.0 if np.allclose(a, b) else 1.0
    return float(1.0 - np.corrcoef(a, b)[0, 1])


def _normalize_phase(phase: str | None) -> SentimentPhase | None:
    """current_phase 入参归一化：SentimentPhase / name / 中文值均可；非法 → ValueError。"""
    if phase is None or isinstance(phase, SentimentPhase):
        return phase
    for p in PHASE_ORDER:
        if phase in (p.name, p.value):
            return p
    raise ValueError(f"非法 current_phase: {phase!r}（契约：SentimentPhase name 或中文值）")


def _phase_transition_distribution(current: SentimentPhase | None) -> dict[str, float]:
    """五阶段一步转移分布（28号转移平滑口径：对角 0.6，邻阶各 0.2，边界自循环收编）。

    current=None → 均匀先验（0.2 各）。返回 key=阶段中文值，Σ=1。
    """
    if current is None:
        return {p.value: 1.0 / len(PHASE_ORDER) for p in PHASE_ORDER}
    n = len(PHASE_ORDER)
    i = PHASE_ORDER.index(current)
    dist = {p.value: 0.0 for p in PHASE_ORDER}
    dist[current.value] += TRANSITION_DIAG_WEIGHT
    neighbor_weight = (1.0 - TRANSITION_DIAG_WEIGHT) / 2
    if i > 0:
        dist[PHASE_ORDER[i - 1].value] += neighbor_weight
    else:
        dist[current.value] += neighbor_weight  # 边界自循环（对齐 sentiment_cycle 平滑语义）
    if i < n - 1:
        dist[PHASE_ORDER[i + 1].value] += neighbor_weight
    else:
        dist[current.value] += neighbor_weight
    return dist


def _prior_tail_probs(current: SentimentPhase | None) -> tuple[float, float, float]:
    """兜底三档概率 = 五阶段转移先验的方向映射（升温边→走强 / 停留→持平 / 降温边→转弱）。

    current=None（均匀先验）→ 三档各 1/3（无信息不编方向）。
    """
    if current is None:
        return 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0
    dist = _phase_transition_distribution(current)
    i = PHASE_ORDER.index(current)
    strong = sum(dist[PHASE_ORDER[j].value] for j in range(len(PHASE_ORDER)) if (i, j) in _TRANSITION_WARMING_EDGES)
    weak = sum(dist[PHASE_ORDER[j].value] for j in range(len(PHASE_ORDER)) if (i, j) in _TRANSITION_COOLING_EDGES)
    flat = dist[current.value]
    total = strong + flat + weak
    return strong / total, flat / total, weak / total


def _dominant(strong: float, flat: float, weak: float) -> str:
    # 持平置首：平票（如均匀先验 1/3）时宁标"持平"不编方向
    probs = {FLAT_LABEL: flat, STRONG_LABEL: strong, WEAK_LABEL: weak}
    return max(probs, key=probs.get)


def _fallback_inference(
    reason: str,
    cfg: SimilarDayConfig,
    current: SentimentPhase | None,
    n_history_days: int,
    features_used: list[str],
    notes: list[str],
    disabled_reason: str | None,
) -> SimilarDayInference:
    """退化五阶段转移先验兜底输出（D<60 / 距离超阈 / 数据缺陷 统一入口）。"""
    strong, flat, weak = _prior_tail_probs(current)
    return SimilarDayInference(
        enabled=disabled_reason is None,
        disabled_reason=disabled_reason,
        fallback_used=True,
        fallback_reason=reason,
        prob_strong=strong,
        prob_flat=flat,
        prob_weak=weak,
        dominant_scenario=_dominant(strong, flat, weak),
        n_history_days=n_history_days,
        n_neighbors=0,
        mean_neighbor_distance=None,
        features_used=features_used,
        current_phase=current.value if current is not None else None,
        phase_transition_prob=_phase_transition_distribution(current),
        notes=notes,
    )


# ------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------
def infer_remaining_session(
    today_series: pd.DataFrame | None,
    history_store: Iterable[pd.DataFrame] | None = None,
    config: SimilarDayConfig | None = None,
) -> SimilarDayInference:
    """相似日 KNN 尾盘三档情景概率推演（44号 §9.3 主入口）。

    Args:
        today_series: 当日 09:30→当前时刻快照序列 DataFrame（列契约见模块 docstring）。
        history_store: 历史日快照序列可迭代注入（测试=合成历史；生产=market_breadth_snapshot
            读取器，后续波次接）；None/空 → 恒走五阶段先验兜底分支（当前零数据积累常态）。
        config: SimilarDayConfig；None → 默认。

    Returns:
        SimilarDayInference（to_dict JSON 可序列化；只出三档概率不出点位）。
    """
    cfg = config or SimilarDayConfig()
    notes: list[str] = []
    current = _normalize_phase(cfg.current_phase)

    # ===== 纪律开关：walk-forward 命中率 <55% → 自动停用（仍出先验概率 + disabled 标注）=====
    disabled_reason: str | None = None
    if cfg.walkforward_hit_rate is not None and cfg.walkforward_hit_rate < cfg.hit_rate_floor:
        disabled_reason = (
            f"walkforward_hit_rate={cfg.walkforward_hit_rate:.3f} < {cfg.hit_rate_floor:.2f}，自动停用（44号 §9.3 纪律）"
        )
        notes.append(disabled_reason)

    # ===== 当日序列守卫 =====
    if today_series is None or len(today_series) == 0:
        return _fallback_inference(
            "today_series_empty", cfg, current, 0, [], notes + ["今日快照为空"], disabled_reason
        )
    if TS_COLUMN not in today_series.columns:
        raise ValueError(f"today_series 缺 {TS_COLUMN!r} 列（调用方契约违例）")

    open_min = _hhmm_to_minutes(cfg.session_open)
    close_min = _hhmm_to_minutes(cfg.session_close)
    now_min = _hhmm_to_minutes(cfg.now) if cfg.now is not None else float(
        today_series[TS_COLUMN].map(_ts_to_minutes).max()
    )
    if now_min <= open_min:
        return _fallback_inference(
            "now_before_open", cfg, current, 0, [], notes + [f"当前时刻 {now_min:.0f} ≤ 开盘 {open_min:.0f}"], disabled_reason
        )
    grid = np.linspace(open_min, now_min, cfg.grid_points)

    # ===== 特征维可用性（if_basis 等缺列 → 剔除并重配权重）=====
    features_used = [name for name in FEATURE_COLUMNS if name in today_series.columns]
    dropped = [name for name in FEATURE_COLUMNS if name not in today_series.columns]
    if dropped:
        notes.append(f"今日快照缺维剔除并重配权重: {dropped}")
    if not features_used:
        return _fallback_inference(
            "no_feature_columns", cfg, current, 0, [], notes + ["今日快照五维特征全缺"], disabled_reason
        )
    weight_total = sum(cfg.feature_weights.get(name, 0.0) for name in features_used)
    weights = {name: cfg.feature_weights.get(name, 0.0) / weight_total for name in features_used}

    today_vecs: dict[str, np.ndarray] = {}
    for name in features_used:
        vec = _resample_to_grid(today_series, name, grid)
        if vec is None:
            notes.append(f"今日特征 {name} 有效点 <2，剔除该维")
        else:
            today_vecs[name] = vec
    if not today_vecs:
        return _fallback_inference(
            "today_features_unusable", cfg, current, 0, features_used, notes, disabled_reason
        )
    features_used = [name for name in features_used if name in today_vecs]
    weight_total = sum(weights[name] for name in features_used)
    weights = {name: weights[name] / weight_total for name in features_used}

    # ===== 历史日遍历：同时刻切片 + 距离 + 标签 =====
    history_days = list(history_store) if history_store is not None else []
    neighbors: list[tuple[float, float, tuple[str, ...]]] = []  # (distance, remaining_ret, common_dims)
    skipped = 0
    for day_df in history_days:
        if TS_COLUMN not in day_df.columns or LABEL_PRICE_COLUMN not in day_df.columns or len(day_df) < 2:
            skipped += 1
            continue
        minutes = day_df[TS_COLUMN].map(_ts_to_minutes).to_numpy(dtype=float)
        sliced = day_df[minutes <= now_min + 1e-9]
        day_vecs = {name: _resample_to_grid(sliced, name, grid) for name in features_used}
        common = [name for name in features_used if day_vecs[name] is not None]
        if not common:
            skipped += 1
            continue
        prices = day_df[LABEL_PRICE_COLUMN].to_numpy(dtype=float)
        valid = ~(np.isnan(minutes) | np.isnan(prices))
        if valid.sum() < 2:
            skipped += 1
            continue
        order = np.argsort(minutes[valid])
        mins_v, prices_v = minutes[valid][order], prices[valid][order]
        p_now = float(np.interp(now_min, mins_v, prices_v))
        p_close = float(prices_v[-1]) if mins_v[-1] >= close_min else float("nan")
        if p_now <= 0 or np.isnan(p_close):
            skipped += 1  # 未覆盖收盘 → 无法出标签，剔除
            continue
        remaining_ret = p_close / p_now - 1.0
        common_weight = sum(weights[name] for name in common)
        distance = sum(weights[name] * _pearson_distance(today_vecs[name], day_vecs[name]) for name in common)
        neighbors.append((distance / common_weight, remaining_ret, tuple(common)))

    if skipped:
        notes.append(f"历史日剔除 {skipped} 个（缺 ts/index_price/有效点不足/未覆盖收盘）")
    n_valid = len(neighbors)
    if n_valid < cfg.min_history_days:
        return _fallback_inference(
            f"insufficient_history: 有效历史 D={n_valid} < {cfg.min_history_days}",
            cfg,
            current,
            n_valid,
            features_used,
            notes,
            disabled_reason,
        )

    # ===== k 近邻与距离阈值 =====
    neighbors.sort(key=lambda item: item[0])
    k_near = neighbors[: cfg.k]
    mean_distance = float(np.mean([d for d, _, _ in k_near]))
    if mean_distance > cfg.max_mean_distance:
        return _fallback_inference(
            f"mean_neighbor_distance={mean_distance:.3f} > 阈值 {cfg.max_mean_distance}",
            cfg,
            current,
            n_valid,
            features_used,
            notes,
            disabled_reason,
        )

    # features_used 收口到近邻实际参与维度（历史侧缺维 → 该维剔除，权重已在逐日距离内重配）
    used_dims = {name for _, _, common in k_near for name in common}
    if len(used_dims) < len(features_used):
        dropped_hist = [name for name in features_used if name not in used_dims]
        notes.append(f"历史侧缺维剔除: {dropped_hist}")
        features_used = [name for name in features_used if name in used_dims]

    # ===== 三档概率 = 近邻剩余时段收益分档占比（不出点位）=====
    n_k = len(k_near)
    n_strong = sum(1 for _, ret, _ in k_near if ret > cfg.strong_threshold)
    n_weak = sum(1 for _, ret, _ in k_near if ret < cfg.weak_threshold)
    n_flat = n_k - n_strong - n_weak
    prob_strong, prob_flat, prob_weak = n_strong / n_k, n_flat / n_k, n_weak / n_k
    return SimilarDayInference(
        enabled=disabled_reason is None,
        disabled_reason=disabled_reason,
        fallback_used=False,
        fallback_reason=None,
        prob_strong=prob_strong,
        prob_flat=prob_flat,
        prob_weak=prob_weak,
        dominant_scenario=_dominant(prob_strong, prob_flat, prob_weak),
        n_history_days=n_valid,
        n_neighbors=n_k,
        mean_neighbor_distance=mean_distance,
        features_used=features_used,
        current_phase=current.value if current is not None else None,
        phase_transition_prob=_phase_transition_distribution(current),  # 先验；后验更新留数据期
        notes=notes,
    )
