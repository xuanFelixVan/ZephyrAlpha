# [BLUEPRINT] MOD-SIG-104 | docs/03_modules/_domain_signal/next_day_probability_gate/blueprint.md
# [MODULE] zephyr.signal_ashare.next_day_probability_gate
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（math/dataclasses）；p_up 概率鸭子类型注入（MOD-SIG-037 8态/密度预测/Brier 校准语义），不 import 任何 zephyr 内部件
# [CONSUMERS] （候选：决策链第一道门装配层、模块13 隔夜收益期望值 B10-01464；上游概率生产方 MOD-SIG-037 next_day_8state_forecast/conditional_density_predictor/plan_engine brier_calibration）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 动作分档封闭集（new_position/add_position/bottom_fishing/t_plus/t_minus）；方向概率口径（多头动作=p_up，t_minus=1−p_up）；动态偏移叠加求和后钳制 [floor,cap]；拦截必出归因原因（基准+偏移+缺口）；拦截统计内存累计（total/blocked/block_rate/avg_shortfall）+ 可选 sink 回写；门语义非异常（拦截不抛错）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01415 行 + 候选注册表 CAND-TESTB-021
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知动作/p_up 越界[0,1]或非有限/上下文冲突（牛熊同真、放量缩量同真）/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_next_day_probability_gate.py
# [A_module] module_id=MOD-SIG-104 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""次日上涨概率统一门槛模块（MOD-SIG-104，B10-01415，模块29）。

场内对账（查重铁律⑤探查在案）：next_day_8state_forecast（MOD-SIG-037）=8 态
概率分布生产方（只出概率不出信号）、conditional_density_predictor=密度预测、
plan_engine/brier_calibration=概率校准、expectation_governance（D_DATA_ENG）
=数据质量期望套件门控（数据域，语义正交）、筛选漏斗族（MOD-SIG-086/046）
=标的池排除与评分（非概率门槛）；**动作分档统一概率门槛（决策链第一道门）
+牛熊量能动态偏移+拦截归因与统计回写无实现**（深挖批 min_build_spec 明示
缺口），本模块落地。

口径（注册表 problem 既定）：

- **动作分档门槛**：新开仓≥0.65 / 加仓≥0.60 / 抄底≥0.70 / 正T≥0.55 /
  反T=P(跌)≥0.55（方向概率口径：多头动作=p_up，反T=1−p_up）。
- **动态偏移**（叠加求和，钳制 [0.50,0.95]）：牛−5% / 熊+5% / 放量−5% /
  缩量+10% / 利好落地前+10% / 黑天鹅+15% / 变盘日+5% / 情绪高位+5%。
- **拦截归因**（对标 Man Group 裁定口径）：拦截必输出基准门槛+各偏移+
  调整后门槛+缺口；拦截统计回写（计数/拦截率/平均缺口）供回测门槛合理性，
  sink 鸭子类型注入（生产 DB 接线留集成批）。

门语义非异常：拦截=passed=False+reason，不抛错；仅输入非法才 ValueError。

不做什么：不生产概率（上游注入）、不做 Platt 校准（brier_calibration 职责）、
不进入 L2-A→L2-B→L3 后续链路（本件仅为第一道门）、不荐股。

依据: AUD-DRAFT-001 深挖批 B10-01415（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-104
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 动作（封闭集）+ p_up∈[0,1] + 可选 GateContext（牛熊/量能/事件标记）
# 特征: 方向概率（多头=p_up/反T=1−p_up）+ 偏移叠加
# 算法: 基准门槛查表 → 偏移求和 → 钳制 → 比较出放行/拦截（+归因）→ 统计累计
# 输出: GateDecision（动作/放行/方向概率/基准/偏移/调整后/原因）+ stats_snapshot
"""

from __future__ import annotations

import logging
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "GATE_ACTIONS",
    "ActionGateStats",
    "GateContext",
    "GateDecision",
    "GateStatsSnapshot",
    "NextDayProbabilityGate",
    "ProbabilityGateConfig",
]

#: 动作分档封闭集（候选注册表 CAND-TESTB-021 problem 既定口径）
GATE_ACTIONS: Final[tuple[str, ...]] = (
    "new_position",  # 新开仓 ≥0.65
    "add_position",  # 加仓 ≥0.60
    "bottom_fishing",  # 抄底 ≥0.70
    "t_plus",  # 正T ≥0.55
    "t_minus",  # 反T：P(跌)=1−p_up ≥0.55
)

#: 反T 类动作（方向概率=1−p_up）
_DOWN_SIDE_ACTIONS: Final = frozenset({"t_minus"})


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class ProbabilityGateConfig:
    """分档门槛+动态偏移+钳制配置（构造即校验，fail-closed）。"""

    new_position_threshold: float = 0.65
    add_position_threshold: float = 0.60
    bottom_fishing_threshold: float = 0.70
    t_plus_threshold: float = 0.55
    t_minus_threshold: float = 0.55
    bull_offset: float = -0.05
    bear_offset: float = 0.05
    volume_surge_offset: float = -0.05
    volume_shrink_offset: float = 0.10
    pre_news_offset: float = 0.10
    black_swan_offset: float = 0.15
    turn_day_offset: float = 0.05
    sentiment_high_offset: float = 0.05
    threshold_floor: float = 0.50
    threshold_cap: float = 0.95

    def __post_init__(self) -> None:
        for name in (
            "new_position_threshold", "add_position_threshold",
            "bottom_fishing_threshold", "t_plus_threshold", "t_minus_threshold",
        ):
            v = getattr(self, name)
            if not 0.0 < v < 1.0:
                msg = f"{name} 须∈(0,1)，实得 {v}"
                raise ValueError(msg)
        for name in (
            "bull_offset", "bear_offset", "volume_surge_offset",
            "volume_shrink_offset", "pre_news_offset", "black_swan_offset",
            "turn_day_offset", "sentiment_high_offset",
        ):
            v = getattr(self, name)
            if not -1.0 < v < 1.0:
                msg = f"{name} 须∈(−1,1)，实得 {v}"
                raise ValueError(msg)
        if not 0.0 < self.threshold_floor < self.threshold_cap < 1.0:
            msg = (
                f"钳制区间须 0<floor<cap<1：floor={self.threshold_floor} cap={self.threshold_cap}"
            )
            raise ValueError(msg)

    def base_threshold(self, action: str) -> float:
        return {
            "new_position": self.new_position_threshold,
            "add_position": self.add_position_threshold,
            "bottom_fishing": self.bottom_fishing_threshold,
            "t_plus": self.t_plus_threshold,
            "t_minus": self.t_minus_threshold,
        }[action]


@dataclass(frozen=True)
class GateContext:
    """动态偏移上下文标记（冲突组合 fail-closed）。"""

    bull: bool = False
    bear: bool = False
    volume_surge: bool = False
    volume_shrink: bool = False
    pre_news: bool = False
    black_swan: bool = False
    turn_day: bool = False
    sentiment_high: bool = False

    def __post_init__(self) -> None:
        if self.bull and self.bear:
            msg = "bull 与 bear 不可同真（牛熊冲突）"
            raise ValueError(msg)
        if self.volume_surge and self.volume_shrink:
            msg = "volume_surge 与 volume_shrink 不可同真（量能冲突）"
            raise ValueError(msg)


@dataclass(frozen=True)
class GateDecision:
    """门槛裁定（放行/拦截+归因）。"""

    action: str
    passed: bool
    direction_probability: float
    base_threshold: float
    offset_total: float
    adjusted_threshold: float
    applied_offsets: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActionGateStats:
    """单动作拦截统计。"""

    total: int
    blocked: int
    block_rate: float
    avg_shortfall: float  # 平均缺口（调整后门槛−方向概率，仅拦截样本）

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GateStatsSnapshot:
    """门槛统计快照（全动作）。"""

    actions: dict[str, ActionGateStats]

    def to_dict(self) -> dict[str, Any]:
        return {k: v.to_dict() for k, v in self.actions.items()}


# ------------------------------------------------------------------
# 门槛引擎
# ------------------------------------------------------------------
class NextDayProbabilityGate:
    """次日上涨概率统一门槛（决策链第一道门，纯函数核+内存统计）。"""

    def __init__(self, config: ProbabilityGateConfig | None = None) -> None:
        self._config = config if config is not None else ProbabilityGateConfig()
        self._stats: dict[str, dict[str, float]] = {
            a: {"total": 0, "blocked": 0, "shortfall_sum": 0.0} for a in GATE_ACTIONS
        }
        self._block_sink: Callable[[GateDecision], None] | None = None

    @property
    def config(self) -> ProbabilityGateConfig:
        return self._config

    def set_block_sink(self, sink: Callable[[GateDecision], None] | None) -> None:
        """注入拦截回写 sink（鸭子类型，生产 DB 接线留集成批）。"""
        self._block_sink = sink

    # ── 偏移计算 ─────────────────────────────────────────────────
    def _offsets(self, ctx: GateContext) -> tuple[float, list[str]]:
        cfg = self._config
        pairs = (
            ("bull", cfg.bull_offset),
            ("bear", cfg.bear_offset),
            ("volume_surge", cfg.volume_surge_offset),
            ("volume_shrink", cfg.volume_shrink_offset),
            ("pre_news", cfg.pre_news_offset),
            ("black_swan", cfg.black_swan_offset),
            ("turn_day", cfg.turn_day_offset),
            ("sentiment_high", cfg.sentiment_high_offset),
        )
        total = 0.0
        applied: list[str] = []
        for flag, offset in pairs:
            if getattr(ctx, flag):
                total += offset
                applied.append(flag)
        return total, applied

    # ── 主入口 ───────────────────────────────────────────────────
    def evaluate(
        self, action: str, p_up: float, context: GateContext | None = None
    ) -> GateDecision:
        if action not in GATE_ACTIONS:
            msg = f"未知动作（封闭集外）: {action!r}"
            raise ValueError(msg)
        if not math.isfinite(p_up) or not 0.0 <= p_up <= 1.0:
            msg = f"p_up 须∈[0,1] 且有限: {p_up!r}"
            raise ValueError(msg)
        ctx = context if context is not None else GateContext()
        cfg = self._config

        direction_probability = (1.0 - p_up) if action in _DOWN_SIDE_ACTIONS else p_up
        base = cfg.base_threshold(action)
        offset_total, applied = self._offsets(ctx)
        adjusted = min(max(base + offset_total, cfg.threshold_floor), cfg.threshold_cap)
        passed = direction_probability >= adjusted
        shortfall = max(adjusted - direction_probability, 0.0)
        offsets_desc = ",".join(applied) if applied else "无"
        if passed:
            reason = (
                f"通过：{action} 方向概率 {direction_probability:.3f}≥调整后门槛 "
                f"{adjusted:.3f}（基准 {base:.2f}，偏移 {offset_total:+.2f}[{offsets_desc}]）"
            )
        else:
            reason = (
                f"拦截：{action} 方向概率 {direction_probability:.3f}<调整后门槛 "
                f"{adjusted:.3f}（基准 {base:.2f}，偏移 {offset_total:+.2f}[{offsets_desc}]），"
                f"缺口 {shortfall:.3f}"
            )
        decision = GateDecision(
            action=action,
            passed=passed,
            direction_probability=direction_probability,
            base_threshold=base,
            offset_total=offset_total,
            adjusted_threshold=adjusted,
            applied_offsets=tuple(applied),
            reason=reason,
        )
        row = self._stats[action]
        row["total"] += 1
        if not passed:
            row["blocked"] += 1
            row["shortfall_sum"] += shortfall
            if self._block_sink is not None:
                self._block_sink(decision)
        return decision

    # ── 统计回写 ─────────────────────────────────────────────────
    def stats_snapshot(self) -> GateStatsSnapshot:
        actions: dict[str, ActionGateStats] = {}
        for action, row in self._stats.items():
            total = int(row["total"])
            blocked = int(row["blocked"])
            actions[action] = ActionGateStats(
                total=total,
                blocked=blocked,
                block_rate=(blocked / total) if total else 0.0,
                avg_shortfall=(row["shortfall_sum"] / blocked) if blocked else 0.0,
            )
        return GateStatsSnapshot(actions=actions)
