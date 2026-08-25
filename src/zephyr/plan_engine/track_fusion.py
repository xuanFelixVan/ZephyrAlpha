# [BLUEPRINT] MOD-PLAN-020 | docs/03_modules/_domain_plan_engine/track_fusion/blueprint.md
# [MODULE] zephyr.plan_engine.track_fusion
# [DOMAIN] D_PLAN
# [DEPENDENCIES]
# [CONSUMERS] 运行时装配批（四轨信号注入；FusedDirective 交 MOD-POS-001 精裁；verdict 供 MOD-POS-009 审计落库）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 优先级钉死: 轨道4应急>轨道3人工>轨道1/2自动; 自动双轨同向=强共振(weight取保守min)/单轨=中等/反向=不出指令升L6; AI发现轨信号必须needs_l6_review=True(不可豁免); 同轨多信号冲突/畸形输入Fail-Closed; 只出指令不下单不精裁
# [MODIFY-GUARD] tests/plan_engine/test_track_fusion.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TrackFusionError(未登记错误码-申请中)
# [TESTS] tests/plan_engine/test_track_fusion.py
# [A_module] module_id=MOD-PLAN-020 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: list[TrackSignal](track/direction/target_weight/source/ai_discovered)
# A1: 校验(同轨冲突Fail-Closed) + 分组(应急/人工/自动)
# A2: 优先级裁决(应急>人工>自动; 人工与自动冲突加L6标记)
# A3: 自动轨融合(双轨同向强共振min weight/单轨中等/反向CONFLICT_L6不出指令)
# O1: FusedDirective(direction/target_weight/priority_track/strength/needs_l6_review/reason)
# [/ALGO_FLOW]
"""四轨融合器（Multi-Track Fusion，v8.0）（MOD-PLAN-020）。

真源：construction_backlog_dig.tsv B10-01212（A1交易决策架构 §1.1，裁定=做 P1）
+ CAND-PLAN-014。TSV 现状注记：position_sizing_engine 头注明示"不包含(阶段2):
四轨融合(轨道2/3/4)"，轨道3人工/轨道4应急枚举已在 position_audit_logger
（审计分类），融合器本身是真实缺口——本模块补该缺口。

裁决规则（确定性纯函数）：
  ① 优先级：轨道4(EMERGENCY) > 轨道3(MANUAL) > 轨道1/2(AUTO)。应急在场直接
     胜出（EMERGENCY_OVERRIDE）；无应急有人工 → 人工胜出（与自动轨方向冲突
     → needs_l6_review=True 留痕）。
  ② 自动轨融合：轨道1+2 同向 → 强共振（STRONG_RESONANCE，target_weight 取
     保守=min）；单轨在场 → 中等（MEDIUM）；反向冲突 → 不出指令升 L6 审查
     （CONFLICT_L6，direction=None）。
  ③ AI 发现轨：任一在场信号 ai_discovered=True → needs_l6_review=True
     （只加审查标记，不影响优先级裁决，不可豁免）。

不做什么：不做 Kelly 精裁（归 MOD-POS-001）、不直接下单（只出 FusedDirective）、
不采集轨道信号（调用方注入）。

SSoT: docs/03_modules/_domain_plan_engine/track_fusion/blueprint.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Final, Sequence

__all__: Final = [
    "FusedDirective",
    "FusionStrength",
    "MultiTrackFusion",
    "TrackDirection",
    "TrackFusionError",
    "TrackId",
    "TrackSignal",
]


class TrackFusionError(Exception):
    """四轨融合错误（输入非法/同轨冲突）。"""

    error_code = "ZA-PLAN-0005"  # 2026-08-25 主代理正式登记（P1 R4W19）

    def __init__(self, *args: object, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


class TrackId(IntEnum):
    """四轨标识（v8.0）。"""

    AUTO_1 = 1  # 轨道1 自动信号（策略信号）
    AUTO_2 = 2  # 轨道2 自动信号（备用/第二信号族）
    MANUAL = 3  # 轨道3 人工指令
    EMERGENCY = 4  # 轨道4 应急指令


class TrackDirection(str, Enum):
    """轨道方向（统一指令语义）。"""

    LONG = "LONG"  # 做多/持有加仓方向
    REDUCE = "REDUCE"  # 减仓
    EXIT = "EXIT"  # 离场
    FLAT = "FLAT"  # 空仓/不动


class FusionStrength(str, Enum):
    """融合强度口径。"""

    EMERGENCY_OVERRIDE = "EMERGENCY_OVERRIDE"  # 应急压制
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"  # 人工优先
    STRONG_RESONANCE = "STRONG_RESONANCE"  # 自动双轨同向强共振
    MEDIUM = "MEDIUM"  # 自动单轨中等
    CONFLICT_L6 = "CONFLICT_L6"  # 冲突升 L6（不出指令）
    EMPTY = "EMPTY"  # 空信号集


@dataclass(frozen=True)
class TrackSignal:
    """单轨信号（不可变，调用方注入）。

    Attributes:
        track: 轨道（1/2 自动, 3 人工, 4 应急）
        direction: 方向
        target_weight: 目标仓位权重 ∈[0,1]（EXIT/FLAT 语义下应为 0，由消费方解释）
        source: 信号来源标识（审计留痕）
        ai_discovered: 是否 AI 发现轨信号（True → 强制 L6 审查标记）
    """

    track: TrackId
    direction: TrackDirection
    target_weight: float = 0.0
    source: str = ""
    ai_discovered: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.track, TrackId):
            raise TrackFusionError(f"track必须∈TrackId, got {self.track!r}")
        if not isinstance(self.direction, TrackDirection):
            raise TrackFusionError(f"direction必须∈TrackDirection, got {self.direction!r}")
        if not 0.0 <= self.target_weight <= 1.0:
            raise TrackFusionError(f"target_weight必须∈[0,1], got {self.target_weight}")
        if not self.source:
            raise TrackFusionError("source不能为空（审计留痕）")


@dataclass(frozen=True)
class FusedDirective:
    """四轨融合统一指令（不可变）。

    Attributes:
        direction: 统一方向（None=不出指令：空集/冲突）
        target_weight: 统一目标仓位权重（direction 为 None 时为 0）
        priority_track: 胜出轨道（空集为 None）
        strength: 融合强度
        needs_l6_review: 是否需升 L6 审查（冲突/AI 发现轨）
        reason: 裁决理由（审计留痕）
    """

    direction: TrackDirection | None
    target_weight: float
    priority_track: TrackId | None
    strength: FusionStrength
    needs_l6_review: bool
    reason: str


#: 方向冲突对（反向=不可共存）
_CONFLICT_PAIRS: Final[frozenset[frozenset[TrackDirection]]] = frozenset(
    {
        frozenset({TrackDirection.LONG, TrackDirection.REDUCE}),
        frozenset({TrackDirection.LONG, TrackDirection.EXIT}),
        frozenset({TrackDirection.LONG, TrackDirection.FLAT}),
    }
)


def _directions_conflict(a: TrackDirection, b: TrackDirection) -> bool:
    """两方向是否反向冲突（同向或 REDUCE↔EXIT 同侧保守不算冲突）。"""
    if a is b:
        return False
    return frozenset({a, b}) in _CONFLICT_PAIRS


class MultiTrackFusion:
    """四轨融合器：应急 > 人工 > 自动 优先级裁决。"""

    def fuse(self, signals: Sequence[TrackSignal]) -> FusedDirective:
        """融合在场轨道信号为统一指令（确定性纯函数）。"""
        for sig in signals:
            if not isinstance(sig, TrackSignal):
                raise TrackFusionError(f"信号必须是TrackSignal, got {type(sig)!r}")

        by_track: dict[TrackId, list[TrackSignal]] = {}
        for sig in signals:
            by_track.setdefault(sig.track, []).append(sig)
        # 同轨多信号：方向必须一致（同向多源取保守 min weight），反向冲突 Fail-Closed
        merged: dict[TrackId, TrackSignal] = {}
        for track, group in by_track.items():
            first = group[0]
            for other in group[1:]:
                if _directions_conflict(first.direction, other.direction):
                    raise TrackFusionError(
                        f"同轨{track.name}多信号方向冲突: {first.direction.value} vs {other.direction.value}"
                    )
            merged[track] = TrackSignal(
                track=track,
                direction=first.direction,
                target_weight=min(s.target_weight for s in group),
                source="+".join(sorted({s.source for s in group})),
                ai_discovered=any(s.ai_discovered for s in group),
            )

        ai_flag = any(s.ai_discovered for s in merged.values())

        if not merged:
            return FusedDirective(
                direction=None,
                target_weight=0.0,
                priority_track=None,
                strength=FusionStrength.EMPTY,
                needs_l6_review=False,
                reason="空信号集，不出指令",
            )

        # ① 轨道4 应急压制
        if TrackId.EMERGENCY in merged:
            em = merged[TrackId.EMERGENCY]
            return FusedDirective(
                direction=em.direction,
                target_weight=em.target_weight,
                priority_track=TrackId.EMERGENCY,
                strength=FusionStrength.EMERGENCY_OVERRIDE,
                needs_l6_review=ai_flag,
                reason="轨道4应急指令在场，直接压制全部低优先级轨道",
            )

        # ② 轨道3 人工优先（与自动轨冲突 → L6 标记）
        if TrackId.MANUAL in merged:
            man = merged[TrackId.MANUAL]
            autos = [merged[t] for t in (TrackId.AUTO_1, TrackId.AUTO_2) if t in merged]
            conflict = any(_directions_conflict(man.direction, a.direction) for a in autos)
            return FusedDirective(
                direction=man.direction,
                target_weight=man.target_weight,
                priority_track=TrackId.MANUAL,
                strength=FusionStrength.MANUAL_OVERRIDE,
                needs_l6_review=ai_flag or conflict,
                reason=(
                    "轨道3人工指令优先"
                    + ("；与自动轨方向冲突，升L6审查" if conflict else "；与自动轨无冲突")
                ),
            )

        # ③ 自动轨融合（轨道1/2）
        autos = [merged[t] for t in (TrackId.AUTO_1, TrackId.AUTO_2) if t in merged]
        if len(autos) == 2 and _directions_conflict(autos[0].direction, autos[1].direction):
            return FusedDirective(
                direction=None,
                target_weight=0.0,
                priority_track=None,
                strength=FusionStrength.CONFLICT_L6,
                needs_l6_review=True,
                reason=(
                    f"自动轨反向冲突({autos[0].direction.value} vs "
                    f"{autos[1].direction.value})，不出指令升L6审查"
                ),
            )
        priority = max(a.track for a in autos)
        if len(autos) == 2:
            strength = FusionStrength.STRONG_RESONANCE
            reason = "轨道1+2同向，强共振（weight取保守min）"
        else:
            strength = FusionStrength.MEDIUM
            reason = "单轨在场，中等强度"
        return FusedDirective(
            direction=autos[0].direction,
            target_weight=min(a.target_weight for a in autos),
            priority_track=priority,
            strength=strength,
            needs_l6_review=ai_flag,
            reason=reason,
        )
