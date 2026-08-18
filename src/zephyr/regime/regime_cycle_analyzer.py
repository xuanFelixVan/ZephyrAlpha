# [BLUEPRINT] MOD-REGIME-006 | docs/03_modules/_domain_regime/regime_cycle_analyzer/blueprint.md
# [MODULE] zephyr.regime.regime_cycle_analyzer
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; scipy
# [CONSUMERS] 无（MVP 阶段输出供 regime 层时间窗口节流参考，接线属后续 WFA 验证达标后施工）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] PIT 严格（analyze(as_of=t) 只用 ≤t 的数据；日历前视是确定性信息非泄漏）; 统计不显著窗口 confidence=0.0 且 direction=neutral（下游禁止消费）; 同输入必同输出（零随机源）
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_cycle_analyzer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RegimeCycleError(ZA-REGIME-0030)
# [TESTS] tests/regime/test_regime_cycle_analyzer.py
# [A_module] module_id=MOD-REGIME-CYCLE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-120 #CAND-CYCLE-001 #REG-CYCLE-001

"""MOD-REGIME-006 RegimeCycleAnalyzer — 时间周期分析 MVP（辅助参考信号，非独立交易信号）。

定位（边界声明，防滥用）：
  本模块输出"何时可能变盘"的时间窗口辅助参考信号，服务 regime 层节流参数调整
  （变盘窗口前降仓/收紧）。**不是独立交易信号**：不生成买卖方向、不直接触发开仓；
  消费方仅限 regime 层节流参考。与 regime（市场状态=多谨慎）和
  emotion_cycle（sleeve 内择时=买卖什么）正交——本模块管时间窗口。
  统计不显著的时间窗口 confidence=0.0 且 direction=neutral，下游禁止消费。

MVP 范围（两件套，对齐 REG-CYCLE-001 注册表）：
  ① 日历效应统计（对齐 CYC-STAT-013）：月末/月初/节后三类 A 股经典日历效应，
     Welch t 检验 + Bonferroni 多重检验校正，显著性自证。
  ② 周年日效应（对齐 CYC-TIME-004）：历史显著高低点周年日 ±5 日窗口，
     以 |日收益| 抬升（变盘=波动聚集，方向中性）做显著性自证。

扩展口（blueprint §7 登记，MVP 不落码——证据强度不足不过度工程）：
  EXT-G  Gann 固定间隔 30/60/90 日（CYC-TIME-001~003）
  EXT-GEO Gann 角度线/九方图几何法（CYC-GEO-001/002）
  EXT-FFT FFT/自相关/聚类/机制切换统计周期（CYC-STAT-001~004）
  EXT-PRICE 波段对称/50% 回调带（CYC-PRICE-001/002）

依据: regime_cycle_registry.yaml v1.2.0 / CAND-CYCLE-001 / #ARCH-120
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as _stats

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

__all__: list[str] = [
    "CycleAnalysisResult",
    "CycleEvidence",
    "CycleWindow",
    "RegimeCycleAnalyzer",
    "RegimeCycleError",
    "anniversary_windows",
    "confidence_from_p_adj",
    "detect_swing_extremes",
    "event_study",
    "trading_day_features",
]


class RegimeCycleError(ZephyrBaseError):
    """ZA-REGIME-0030: 时间周期分析错误（输入数据不足/列缺失/日期非法）。"""

    error_code = "ZA-REGIME-0030"


# ──────────────────────────────────────────────────────────────────────────────
# 参数常量（blueprint §5 参数表唯一真源——改动必须同步蓝图）
# ──────────────────────────────────────────────────────────────────────────────

MIN_OBSERVATIONS = 60          # 输入序列最短交易日数（不足抛 ZA-REGIME-0030）
MIN_EVENTS = 8                 # 事件研究最少事件样本数（不足判不显著）
ALPHA_STRONG = 0.01            # 强显著阈值
ALPHA_MEDIUM = 0.05            # 中显著阈值（significant 判定线）
ALPHA_WEAK = 0.10              # 弱显著阈值
N_HYPOTHESES = 4               # Bonferroni 检验族大小：月末/月初/节后/周年日
MONTH_EDGE_K = 2               # 月末最后/月初前 K 个交易日（对齐 CYC-STAT-013 "月末最后两个交易日"）
POST_HOLIDAY_MIN_GAP_DAYS = 5  # 长假判定：相邻交易日历间隔 ≥5 自然日（春节/国庆）
ANNIVERSARY_TOLERANCE = 5      # 周年日窗口 ±5 自然日（对齐 CYC-TIME-004 params.tolerance=5）
ANNIVERSARY_MAX_YEARS = 10     # 周年回溯最大年数
SWING_LOOKBACK = 20            # 显著高低点局部极值窗口（±20 交易日）
SWING_MIN_MOVE_PCT = 0.20      # 显著性过滤：窗口内波段幅度 ≥20%
DEFAULT_HORIZON_DAYS = 10      # upcoming 窗口前视自然日数

_WINDOW_MONTH_END = "month_end"
_WINDOW_MONTH_START = "month_start"
_WINDOW_POST_HOLIDAY = "post_holiday"
_WINDOW_ANNIVERSARY_HIGH = "anniversary_high"
_WINDOW_ANNIVERSARY_LOW = "anniversary_low"

# window_kind → regime_cycle_registry cycle_id（库↔代码锚点）
_CYCLE_ID_MAP: dict[str, str] = {
    _WINDOW_MONTH_END: "CYC-STAT-013",
    _WINDOW_MONTH_START: "CYC-STAT-013",
    _WINDOW_POST_HOLIDAY: "CYC-STAT-013",
    _WINDOW_ANNIVERSARY_HIGH: "CYC-TIME-004",
    _WINDOW_ANNIVERSARY_LOW: "CYC-TIME-004",
}


# ──────────────────────────────────────────────────────────────────────────────
# 输出契约
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CycleEvidence:
    """事件研究统计证据（显著性自证）。

    p_adj 为 Bonferroni 校正后 p 值（检验族=N_HYPOTHESES）。
    significant=False 时 confidence 恒为 0.0（下游禁止消费）。
    """

    n_events: int
    mean_event: float          # 事件组均值（日历效应=日收益；周年日=|日收益|）
    mean_benchmark: float      # 基准组均值
    t_stat: float
    p_value: float
    p_adj: float
    significant: bool
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_events": self.n_events,
            "mean_event": self.mean_event,
            "mean_benchmark": self.mean_benchmark,
            "t_stat": self.t_stat,
            "p_value": self.p_value,
            "p_adj": self.p_adj,
            "significant": self.significant,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class CycleWindow:
    """时间窗口（变盘风险提示，非交易信号）。

    direction 语义：risk_on=统计效应方向偏多 / risk_off=统计效应方向偏空 /
    neutral=方向中性（周年日变盘=波动抬升无方向；或统计不显著）。
    """

    cycle_id: str
    window_kind: str
    start: pd.Timestamp
    end: pd.Timestamp
    direction: str
    confidence: float
    evidence: CycleEvidence

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "window_kind": self.window_kind,
            "start": self.start.strftime("%Y-%m-%d"),
            "end": self.end.strftime("%Y-%m-%d"),
            "direction": self.direction,
            "confidence": self.confidence,
            "evidence": self.evidence.to_dict(),
        }


@dataclass(frozen=True)
class CycleAnalysisResult:
    """analyze() 输出——辅助参考信号集合（is_advisory_only 恒 True，防滥用钉死）。"""

    as_of: pd.Timestamp
    active_windows: tuple[CycleWindow, ...] = field(default_factory=tuple)
    upcoming_windows: tuple[CycleWindow, ...] = field(default_factory=tuple)
    evidence_table: dict[str, CycleEvidence] = field(default_factory=dict)
    is_advisory_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of.strftime("%Y-%m-%d"),
            "active_windows": [w.to_dict() for w in self.active_windows],
            "upcoming_windows": [w.to_dict() for w in self.upcoming_windows],
            "evidence_table": {k: v.to_dict() for k, v in self.evidence_table.items()},
            "is_advisory_only": self.is_advisory_only,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 纯函数层（PIT 安全、零状态、零随机源）
# ──────────────────────────────────────────────────────────────────────────────


def confidence_from_p_adj(p_adj: float) -> float:
    """Bonferroni 校正后 p 值 → confidence 三档映射（不显著=0.0）。"""
    if p_adj <= ALPHA_STRONG:
        return 1.0
    if p_adj <= ALPHA_MEDIUM:
        return 0.6
    if p_adj <= ALPHA_WEAK:
        return 0.3
    return 0.0


def trading_day_features(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """交易日历结构特征：月末/月初/节后标记（纯日历派生，不依赖 calendar_event 表）。

    返回 DataFrame（index=dates），列：
      is_month_end    每月最后 MONTH_EDGE_K 个交易日
      is_month_start  每月前 MONTH_EDGE_K 个交易日
      is_post_holiday 前一交易日距今日历间隔 ≥POST_HOLIDAY_MIN_GAP_DAYS 自然日
      gap_days        距前一交易日的自然日数（首日=0）
    """
    if len(dates) == 0:
        raise RegimeCycleError("trading_day_features: 空交易日历")
    dates = pd.DatetimeIndex(dates).sort_values()
    idx = pd.Series(dates, index=dates)

    # 月末/月初：按 (year, month) 分组取组内序号
    period = dates.to_period("M")
    rank_asc = idx.groupby(period).rank(method="first", ascending=True)
    rank_desc = idx.groupby(period).rank(method="first", ascending=False)
    is_month_start = rank_asc <= MONTH_EDGE_K
    is_month_end = rank_desc <= MONTH_EDGE_K

    # 节后：相邻交易日历间隔
    gap_days = pd.Series(dates.to_series().diff().dt.days.fillna(0).astype(int).to_numpy(), index=dates)
    is_post_holiday = gap_days >= POST_HOLIDAY_MIN_GAP_DAYS

    return pd.DataFrame(
        {
            "is_month_end": is_month_end.to_numpy(),
            "is_month_start": is_month_start.to_numpy(),
            "is_post_holiday": is_post_holiday.to_numpy(),
            "gap_days": gap_days.to_numpy(),
        },
        index=dates,
    )


def event_study(
    metric: pd.Series,
    event_mask: pd.Series,
    *,
    n_hypotheses: int = N_HYPOTHESES,
    min_n: int = MIN_EVENTS,
) -> CycleEvidence:
    """Welch t 检验事件研究：事件组 metric 均值 vs 基准组，Bonferroni 校正。

    metric 语义由调用方决定（日历效应=日收益；周年日=|日收益|）。
    事件样本 < min_n 或零方差 → significant=False, confidence=0.0。
    """
    metric = metric.dropna()
    event_mask = event_mask.reindex(metric.index).fillna(False).astype(bool)
    event_vals = metric[event_mask].to_numpy(dtype=float)
    bench_vals = metric[~event_mask].to_numpy(dtype=float)

    n_events = int(event_vals.size)
    mean_event = float(event_vals.mean()) if n_events else 0.0
    mean_bench = float(bench_vals.mean()) if bench_vals.size else 0.0

    if n_events < min_n or bench_vals.size < min_n:
        return CycleEvidence(n_events, mean_event, mean_bench, 0.0, 1.0, 1.0, False, 0.0)

    t_stat, p_value = _stats.ttest_ind(event_vals, bench_vals, equal_var=False)
    t_stat = float(t_stat) if np.isfinite(t_stat) else 0.0
    p_value = float(p_value) if np.isfinite(p_value) else 1.0
    p_adj = float(min(1.0, p_value * n_hypotheses))
    significant = p_adj <= ALPHA_MEDIUM
    return CycleEvidence(
        n_events, mean_event, mean_bench, t_stat, p_value, p_adj, significant,
        confidence_from_p_adj(p_adj),
    )


def detect_swing_extremes(
    close: pd.Series,
    *,
    lookback: int = SWING_LOOKBACK,
    min_move_pct: float = SWING_MIN_MOVE_PCT,
) -> pd.DataFrame:
    """显著高低点识别：±lookback 窗口局部极值 + 波段幅度 ≥min_move_pct 过滤。

    返回 DataFrame[date, kind(high/low), price]，同一极值簇内只保留最极端的一点。
    """
    close = close.dropna().sort_index()
    if close.empty:
        return pd.DataFrame(columns=["date", "kind", "price"])

    values = close.to_numpy(dtype=float)
    dates = close.index
    n = len(values)
    records: list[tuple[pd.Timestamp, str, float]] = []

    for i in range(n):
        lo = max(0, i - lookback)
        hi = i + lookback + 1
        if hi > n:
            # 右窗未满=未确认极值（PIT：极值确认需 lookback 日后数据，未确认不采信）
            continue
        window = values[lo:hi]
        w_min = float(window.min())
        w_max = float(window.max())
        if w_min <= 0:
            continue
        amplitude = (w_max - w_min) / w_min
        if amplitude < min_move_pct:
            continue
        if values[i] == w_max:
            records.append((dates[i], "high", float(values[i])))
        elif values[i] == w_min:
            records.append((dates[i], "low", float(values[i])))

    if not records:
        return pd.DataFrame(columns=["date", "kind", "price"])

    df = pd.DataFrame(records, columns=["date", "kind", "price"])
    # 同类极值簇去重：lookback*2+1 日内只保留最极端点
    keep: list[int] = []
    for kind in ("high", "low"):
        sub = df[df["kind"] == kind].sort_values("date")
        last_kept_date: pd.Timestamp | None = None
        last_kept_idx = -1
        for row_idx, row in sub.iterrows():
            if last_kept_date is not None and (row["date"] - last_kept_date).days <= lookback * 2:
                better = row["price"] > sub.loc[last_kept_idx, "price"] if kind == "high" else row["price"] < sub.loc[last_kept_idx, "price"]
                if better:
                    keep.remove(last_kept_idx)
                    keep.append(row_idx)
                    last_kept_date = row["date"]
                    last_kept_idx = row_idx
            else:
                keep.append(row_idx)
                last_kept_date = row["date"]
                last_kept_idx = row_idx
    return df.loc[sorted(keep)].reset_index(drop=True)


def anniversary_windows(
    extremes: pd.DataFrame,
    *,
    tolerance: int = ANNIVERSARY_TOLERANCE,
    max_years: int = ANNIVERSARY_MAX_YEARS,
) -> pd.DataFrame:
    """显著高低点周年日窗口生成：每年周年日 ±tolerance 自然日。

    返回 DataFrame[start, end, kind, origin_date, year_offset]（全历史+未来窗口，
    窗口是否可消费由 analyze() 按 as_of/horizon 过滤——日历是确定性信息非泄漏）。
    """
    rows: list[dict[str, Any]] = []
    for row in extremes.itertuples(index=False):
        origin = pd.Timestamp(row.date)
        for year_offset in range(1, max_years + 1):
            anni = origin + pd.DateOffset(years=year_offset)
            rows.append(
                {
                    "start": anni - pd.Timedelta(days=tolerance),
                    "end": anni + pd.Timedelta(days=tolerance),
                    "kind": f"anniversary_{row.kind}",
                    "origin_date": origin,
                    "year_offset": year_offset,
                }
            )
    if not rows:
        return pd.DataFrame(columns=["start", "end", "kind", "origin_date", "year_offset"])
    return pd.DataFrame(rows).sort_values("start").reset_index(drop=True)


def _anniversary_event_mask(dates: pd.DatetimeIndex, windows: pd.DataFrame, as_of: pd.Timestamp) -> pd.Series:
    """历史周年窗口事件标记（仅 ≤as_of 已发生窗口参与统计——PIT）。"""
    mask = pd.Series(False, index=dates)
    past = windows[windows["end"] <= as_of]
    for row in past.itertuples(index=False):
        mask |= (dates >= row.start) & (dates <= row.end)
    return mask


# ──────────────────────────────────────────────────────────────────────────────
# 编排器
# ──────────────────────────────────────────────────────────────────────────────


class RegimeCycleAnalyzer:
    """时间周期分析编排器（MOD-REGIME-006）。

    Usage:
        analyzer = RegimeCycleAnalyzer()
        result = analyzer.analyze(ohlc, as_of="2026-08-18")
        # ohlc: DataFrame[close]，DatetimeIndex 或含 date 列
        # result.active_windows / upcoming_windows / evidence_table
    """

    def analyze(
        self,
        ohlc: pd.DataFrame,
        as_of: str | pd.Timestamp,
        *,
        horizon_days: int = DEFAULT_HORIZON_DAYS,
    ) -> CycleAnalysisResult:
        """两件套分析：日历效应统计 + 周年日窗口（PIT 严格，≤as_of）。"""
        as_of_ts = pd.Timestamp(as_of).normalize()
        close = self._extract_close(ohlc, as_of_ts)
        returns = close.pct_change()
        abs_returns = returns.abs()
        dates = close.index

        feats = trading_day_features(dates)

        # ① 日历效应：3 假设（有向，用日收益）
        cal_evidence: dict[str, CycleEvidence] = {}
        for kind, col in (
            (_WINDOW_MONTH_END, "is_month_end"),
            (_WINDOW_MONTH_START, "is_month_start"),
            (_WINDOW_POST_HOLIDAY, "is_post_holiday"),
        ):
            cal_evidence[kind] = event_study(returns, feats[col], n_hypotheses=N_HYPOTHESES)

        # ② 周年日效应：1 假设（变盘=波动抬升方向中性，用 |日收益|）
        extremes = detect_swing_extremes(close)
        windows_df = anniversary_windows(extremes)
        anni_mask = _anniversary_event_mask(dates, windows_df, as_of_ts)
        anni_evidence = event_study(abs_returns, anni_mask, n_hypotheses=N_HYPOTHESES)

        evidence_table: dict[str, CycleEvidence] = dict(cal_evidence)
        evidence_table["anniversary"] = anni_evidence

        active: list[CycleWindow] = []
        upcoming: list[CycleWindow] = []
        horizon_end = as_of_ts + pd.Timedelta(days=horizon_days)

        # 日历效应窗口（as_of 当日命中/horizon 内将命中）
        for kind, col in (
            (_WINDOW_MONTH_END, "is_month_end"),
            (_WINDOW_MONTH_START, "is_month_start"),
            (_WINDOW_POST_HOLIDAY, "is_post_holiday"),
        ):
            ev = cal_evidence[kind]
            hit_days = dates[(feats[col]) & (dates >= as_of_ts) & (dates <= horizon_end)]
            for day in hit_days:
                window = self._make_window(kind, day, day, ev)
                (active if day == as_of_ts else upcoming).append(window)

        # 周年日窗口（as_of 落入窗口 / horizon 内将开启）
        for row in windows_df.itertuples(index=False):
            if row.end < as_of_ts or row.start > horizon_end:
                continue
            window = self._make_window(row.kind, row.start, row.end, anni_evidence)
            (active if row.start <= as_of_ts <= row.end else upcoming).append(window)

        return CycleAnalysisResult(
            as_of=as_of_ts,
            active_windows=tuple(active),
            upcoming_windows=tuple(upcoming),
            evidence_table=evidence_table,
        )

    @staticmethod
    def _make_window(kind: str, start: pd.Timestamp, end: pd.Timestamp, ev: CycleEvidence) -> CycleWindow:
        """窗口构造 + 边界钉死：不显著 → confidence=0.0 且 direction=neutral。"""
        if not ev.significant:
            direction = "neutral"
            confidence = 0.0
        elif kind.startswith("anniversary"):
            direction = "neutral"  # 周年日=变盘风险提示，方向中性
            confidence = ev.confidence
        else:
            direction = "risk_on" if ev.mean_event > ev.mean_benchmark else "risk_off"
            confidence = ev.confidence
        return CycleWindow(
            cycle_id=_CYCLE_ID_MAP[kind],
            window_kind=kind,
            start=pd.Timestamp(start),
            end=pd.Timestamp(end),
            direction=direction,
            confidence=confidence,
            evidence=ev,
        )

    @staticmethod
    def _extract_close(ohlc: pd.DataFrame, as_of: pd.Timestamp) -> pd.Series:
        """输入校验 + PIT 截断（≤as_of）。"""
        if not isinstance(ohlc, pd.DataFrame) or ohlc.empty:
            raise RegimeCycleError("analyze: ohlc 为空或非 DataFrame")
        df = ohlc.copy()
        if not isinstance(df.index, pd.DatetimeIndex):
            if "date" not in df.columns:
                raise RegimeCycleError("analyze: ohlc 缺 DatetimeIndex 且不含 date 列")
            df = df.set_index(pd.to_datetime(df["date"]))
        if "close" not in df.columns:
            raise RegimeCycleError("analyze: ohlc 缺 close 列")
        close = df["close"].sort_index()
        close = close[close.index <= as_of]  # PIT：只用 ≤as_of 数据
        close = close.dropna()
        if len(close) < MIN_OBSERVATIONS:
            raise RegimeCycleError(
                f"analyze: ≤as_of 有效观测 {len(close)} < {MIN_OBSERVATIONS}（数据不足）"
            )
        return close
