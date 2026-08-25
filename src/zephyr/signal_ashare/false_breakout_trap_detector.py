# [BLUEPRINT] MOD-SIG-100 | docs/03_modules/_domain_signal/false_breakout_trap_detector/blueprint.md
# [MODULE] zephyr.signal_ashare.false_breakout_trap_detector
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（math/statistics/dataclasses）；OHLCV/压力位/CVD/时间戳鸭子类型注入，不 import 任何 zephyr 内部件
# [CONSUMERS] （候选：买入侧防伪门槛、突破质量卡；CVD 契约上游 MOD-SIG-093 intraday_volume_orderflow）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 假突破判定 N=3 日回落封闭规则；未决（后续根<3 且未回落）→ pending 不出伪判定；诱多三特征分=40/35/25 封闭集（缺数据腿 0 分降级+notes）；均量/前高窗前视（PIT）；滚动统计仅收已决事件（调用方契约）；false_rate∈[0,1]；frozen dataclass asdict JSON 可序列化；纯统计核不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01370 行 + 候选注册表 CAND-TESTB-015
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 K 线/非法压力位/越界 breakout_index/非正价格/负量/CVD 不等长/空事件列表/配置越界 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_false_breakout_trap_detector.py
# [A_module] module_id=MOD-SIG-100 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""假突破与诱多检测模型（MOD-SIG-100，B10-01370）。

场内对账（查重铁律④分工在案）：breakout_failure_detector（MOD-SELL-003）= 卖出侧
单次挑战成败检测（持仓止损）、unified_pattern_engine（MOD-SIG-091）= 图形模板库；
**假突破判定（N=3 日回落）/失败速度/诱多三特征评分/假突破率滚动统计（A股基线
40-50%）供买入侧防伪无实现**（深挖批 min_build_spec 明示缺口），本模块落地——
买入侧独立统计检测器（信号域），与图形库/SELL-003 均正交。CVD 腿消费
MOD-SIG-093 CVD 序列契约（鸭子类型注入，P1W02 fragment 既定计划）。

三件套：

- **突破确认**：close>压力位为突破；量 ≥1.5×前 20 根均量 → confirmed 放量确认。
- **假突破判定（N=3 日回落）**：突破根后首根 close<压力位 → false_breakout，
  fail_speed_days=距突破根根数（1=次日即回落=极弱）；3 根未回落 → 真突破；
  后续根不足 → pending 未决不出伪判定。
- **诱多三特征评分**（0-100，≥60 suspected）：缩量突破 40 + CVD 背离
  （突破根 CVD < 前 lookback 前高对应 CVD）35 + 尾盘突破（≥270 分钟，自 9:30）25。
- **假突破率滚动统计**：最近 stats_window 个已决事件 false_rate；>0.50 elevated
  （高于 A 股基线上沿）/<0.40 below_baseline；样本不足 sufficient=False 显式降级。

依据: AUD-DRAFT-001 深挖批 B10-01370（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-100
Version: 0.1.0

# [ALGO_FLOW]
# 输入: OHLCV 序列 + 压力位 + 突破根索引（可选 CVD 序列/突破分钟）/ 历史已决事件
# 特征: 前视均量 + 放量确认 + 回落速度 + 缩量/CVD背离/尾盘三特征 + 滚动假突破率
# 算法: 确认判定 → N 日回落检查 → 三特征评分 → 滚动统计基线比较
# 输出: BreakoutEvaluation（确认/假突破/速度/诱多/pending）+ FalseBreakoutStats
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "Bar",
    "BreakoutEvent",
    "BreakoutEvaluation",
    "FalseBreakoutConfig",
    "FalseBreakoutStats",
    "FalseBreakoutTrapDetector",
    "TrapFeatureScore",
]

# 诱多三特征分值（封闭集，可审计静态表）
_SHRINK_POINTS: Final = 40.0
_CVD_POINTS: Final = 35.0
_TAIL_POINTS: Final = 25.0


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class Bar:
    """单根 OHLCV（鸭子类型输入）。"""

    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class BreakoutEvent:
    """历史已评估突破事件（仅收已决：false_breakout 有定论）。"""

    false_breakout: bool


@dataclass(frozen=True)
class FalseBreakoutConfig:
    """阈值配置（构造即校验，fail-closed）。"""

    confirm_volume_ratio: float = 1.5
    false_check_days: int = 3
    vol_avg_window: int = 20
    cvd_lookback: int = 20
    tail_breakout_minute: float = 270.0
    trap_threshold: float = 60.0
    stats_window: int = 20
    stats_min_events: int = 5
    baseline_low: float = 0.40
    baseline_high: float = 0.50

    def __post_init__(self) -> None:
        if self.confirm_volume_ratio <= 1.0:
            msg = f"confirm_volume_ratio 须>1，实得 {self.confirm_volume_ratio}"
            raise ValueError(msg)
        if self.false_check_days < 1:
            msg = f"false_check_days 须≥1，实得 {self.false_check_days}"
            raise ValueError(msg)
        if self.vol_avg_window < 5:
            msg = f"vol_avg_window 须≥5，实得 {self.vol_avg_window}"
            raise ValueError(msg)
        if self.cvd_lookback < 2:
            msg = f"cvd_lookback 须≥2，实得 {self.cvd_lookback}"
            raise ValueError(msg)
        if self.tail_breakout_minute < 0.0:
            msg = f"tail_breakout_minute 须≥0，实得 {self.tail_breakout_minute}"
            raise ValueError(msg)
        if not (0.0 < self.trap_threshold <= 100.0):
            msg = f"trap_threshold 须∈(0,100]，实得 {self.trap_threshold}"
            raise ValueError(msg)
        if self.stats_window < 5:
            msg = f"stats_window 须≥5，实得 {self.stats_window}"
            raise ValueError(msg)
        if self.stats_min_events < 1:
            msg = f"stats_min_events 须≥1，实得 {self.stats_min_events}"
            raise ValueError(msg)
        if not (0.0 < self.baseline_low < self.baseline_high < 1.0):
            msg = f"基线须 0<low<high<1，实得 {self.baseline_low}/{self.baseline_high}"
            raise ValueError(msg)


@dataclass(frozen=True)
class TrapFeatureScore:
    """诱多三特征评分输出。"""

    shrink_points: float
    cvd_points: float
    tail_points: float
    score: float
    suspected: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BreakoutEvaluation:
    """单突破事件评估输出。"""

    breakout: bool
    confirmed: bool
    false_breakout: bool | None
    fail_speed_days: int | None
    pending: bool
    trap: TrapFeatureScore
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["trap"] = self.trap.to_dict()
        return d


@dataclass(frozen=True)
class FalseBreakoutStats:
    """假突破率滚动统计输出。"""

    total: int
    false_count: int
    false_rate: float
    elevated: bool
    below_baseline: bool
    sufficient: bool
    degraded: bool
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ------------------------------------------------------------------
# 引擎
# ------------------------------------------------------------------
class FalseBreakoutTrapDetector:
    """假突破与诱多检测引擎（纯统计核，鸭子类型注入）。"""

    def __init__(self, config: FalseBreakoutConfig | None = None) -> None:
        self._config = config if config is not None else FalseBreakoutConfig()

    @property
    def config(self) -> FalseBreakoutConfig:
        return self._config

    # ── 单事件评估 ────────────────────────────────────────────────
    def evaluate(
        self,
        bars: Sequence[Bar],
        resistance: float,
        breakout_index: int,
        *,
        cvd: Sequence[float] | None = None,
        breakout_minute: float | None = None,
    ) -> BreakoutEvaluation:
        cfg = self._config
        if not bars:
            msg = "空 K 线序列"
            raise ValueError(msg)
        if not math.isfinite(resistance) or resistance <= 0.0:
            msg = f"resistance 须>0，实得 {resistance}"
            raise ValueError(msg)
        n = len(bars)
        if not (0 <= breakout_index < n):
            msg = f"breakout_index 越界: {breakout_index}（len={n}）"
            raise ValueError(msg)
        for i, b in enumerate(bars):
            if not all(math.isfinite(v) for v in (b.open, b.high, b.low, b.close, b.volume)):
                msg = f"bars[{i}] 含非有限值"
                raise ValueError(msg)
            if min(b.open, b.high, b.low, b.close) <= 0.0:
                msg = f"bars[{i}] 含非正价格"
                raise ValueError(msg)
            if b.volume < 0.0:
                msg = f"bars[{i}] 量为负"
                raise ValueError(msg)
        if cvd is not None:
            if len(cvd) != n:
                msg = f"CVD 与 K 线不等长: {len(cvd)} vs {n}"
                raise ValueError(msg)
            if not all(math.isfinite(v) for v in cvd):
                msg = "CVD 含非有限值"
                raise ValueError(msg)
        if breakout_minute is not None and not math.isfinite(breakout_minute):
            msg = "breakout_minute 非有限值"
            raise ValueError(msg)

        notes: list[str] = []
        bi = breakout_index
        bar = bars[bi]
        breakout = bar.close > resistance
        empty_trap = TrapFeatureScore(0.0, 0.0, 0.0, 0.0, False)
        if not breakout:
            return BreakoutEvaluation(
                breakout=False,
                confirmed=False,
                false_breakout=None,
                fail_speed_days=None,
                pending=False,
                trap=empty_trap,
                notes=("收盘未过压力位，非突破事件",),
            )

        # 前视均量（仅突破根之前，PIT）
        prior = bars[max(0, bi - cfg.vol_avg_window) : bi]
        avg_vol: float | None = None
        if prior:
            avg_vol = statistics.fmean(b.volume for b in prior)
        else:
            notes.append("突破根前无历史 K 线，均量腿降级（确认/缩量特征不可得）")
        confirmed = bool(avg_vol is not None and bar.volume >= cfg.confirm_volume_ratio * avg_vol)

        # 假突破判定（N=false_check_days 日回落）
        false_breakout: bool | None = None
        fail_speed: int | None = None
        pending = False
        for j in range(bi + 1, min(bi + cfg.false_check_days + 1, n)):
            if bars[j].close < resistance:
                false_breakout = True
                fail_speed = j - bi
                break
        if false_breakout is None:
            if n - 1 - bi >= cfg.false_check_days:
                false_breakout = False
            else:
                pending = True
                notes.append(f"后续根数 {n - 1 - bi}<{cfg.false_check_days}，假突破判定未决")

        # 诱多三特征
        shrink_pts = 0.0
        if avg_vol is not None and bar.volume < avg_vol:
            shrink_pts = _SHRINK_POINTS
        cvd_pts = 0.0
        if cvd is not None:
            ref_window = bars[max(0, bi - cfg.cvd_lookback) : bi]
            if ref_window:
                ref_idx = max(range(bi - len(ref_window), bi), key=lambda k: bars[k].close)
                if cvd[bi] < cvd[ref_idx]:
                    cvd_pts = _CVD_POINTS
            else:
                notes.append("突破根前无参考窗，CVD 背离腿降级")
        else:
            notes.append("未注入 CVD 序列，CVD 背离腿降级（0 分）")
        tail_pts = 0.0
        if breakout_minute is not None:
            if breakout_minute >= cfg.tail_breakout_minute:
                tail_pts = _TAIL_POINTS
        else:
            notes.append("未注入突破分钟，尾盘突破腿降级（0 分）")
        trap_score = shrink_pts + cvd_pts + tail_pts
        trap = TrapFeatureScore(
            shrink_points=shrink_pts,
            cvd_points=cvd_pts,
            tail_points=tail_pts,
            score=trap_score,
            suspected=trap_score >= cfg.trap_threshold,
        )
        return BreakoutEvaluation(
            breakout=True,
            confirmed=confirmed,
            false_breakout=false_breakout,
            fail_speed_days=fail_speed,
            pending=pending,
            trap=trap,
            notes=tuple(notes),
        )

    # ── 假突破率滚动统计 ───────────────────────────────────────────
    def rolling_stats(self, events: Sequence[BreakoutEvent]) -> FalseBreakoutStats:
        cfg = self._config
        if not events:
            msg = "空事件列表"
            raise ValueError(msg)
        window = list(events)[-cfg.stats_window :]
        total = len(window)
        falses = sum(1 for e in window if e.false_breakout)
        rate = falses / total
        sufficient = total >= cfg.stats_min_events
        notes: tuple[str, ...] = ()
        if not sufficient:
            notes = (f"已决事件 {total}<{cfg.stats_min_events}，统计显式降级",)
        return FalseBreakoutStats(
            total=total,
            false_count=falses,
            false_rate=rate,
            elevated=rate > cfg.baseline_high,
            below_baseline=rate < cfg.baseline_low,
            sufficient=sufficient,
            degraded=not sufficient,
            notes=notes,
        )
