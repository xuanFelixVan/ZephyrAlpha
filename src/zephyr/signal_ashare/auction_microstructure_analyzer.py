# [BLUEPRINT] MOD-SIG-089 | docs/03_modules/_domain_signal/auction_microstructure_analyzer/blueprint.md
# [MODULE] zephyr.signal_ashare.auction_microstructure_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数核，零 DB/行情/LLM）
# [CONSUMERS] （候选：盘前计划 D_PLAN、打板监控；与 MOD-PLAN-015 auction_hit_recorder 数据正交）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 行为四族封闭集（抢筹/诱多/压价/中性）；快照时间戳严格递增校验 fail-closed；撤单率分母为 0 → 0.0+notes 不外推；单快照退化 NEUTRAL；置信度=命中规则条数/该行为规则总数；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B1-00171 行 + 候选注册表 CAND-TESTB-004
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 symbol/空快照/时间戳非递增/负价量/撤单>申报/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_auction_microstructure_analyzer.py
# [A_module] module_id=MOD-SIG-089 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""开盘竞价微结构分析模型（MOD-SIG-089，B1-00171）。

竞价命中记录器在（MOD-PLAN-015），竞价信息提取/行为分类/信号生成未成
（深挖裁定理由）。本模块落竞价三件套：

1. **9:15-9:25 量价特征提取**（五族）：虚拟撮合价漂移、撮合量斜率、
   撤单率（累计撤单/累计申报）、封单变化（买一档量）、9:20 不可撤单段量占比
   + 早段漂移与后段封单塌陷（诱多识别专用两族）。
2. **行为分类**（规则引擎 MVP）：
   - 抢筹 GRAB：价漂移≥阈值 + 低撤单 + 封单增 → LONG；
   - 诱多 BAIT：早段价升 + 高撤单 + 9:20 后封单塌 → SHORT；
   - 压价 PRESS：价漂移≤负阈值 + 封单缩 → SHORT；
   - 无一全中 → NEUTRAL。置信度=命中规则条数/规则总数。
3. **竞价信号输出**：AuctionSignal（行为/方向/置信度/特征明细），候选消费方
   盘前计划与打板监控。

不做什么：不做竞价结果命中对账（MOD-PLAN-015 职责）、不直连行情源
（快照由上游注入）、不荐股。

依据: AUD-DRAFT-001 深挖批 B1-00171（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-089
Version: 0.1.0

# [ALGO_FLOW]
# 输入: symbol + list[AuctionSnapshot]（ts/虚拟撮合价量/买一档量/累计申报/累计撤单）
# 特征: 价漂移/量斜率/撤单率/封单变化/9:20后量占比/早段漂移/后段封单塌陷
# 算法: 快照校验 → 七族特征 → 三族行为规则打分 → 最优行为出信号
# 输出: AuctionSignal（behavior/direction/confidence/features/notes）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "AuctionBehavior",
    "AuctionFeatures",
    "AuctionMicroConfig",
    "AuctionMicrostructureAnalyzer",
    "AuctionSignal",
    "AuctionSnapshot",
    "analyze_auction",
]

#: 9:20（含）起为不可撤单段
_LATE_START_HHMM: Final = "09:20"


class AuctionBehavior(str, Enum):
    """竞价行为四族（封闭集）。"""

    GRAB = "抢筹"
    BAIT = "诱多"
    PRESS = "压价"
    NEUTRAL = "中性"


@dataclass(frozen=True, slots=True)
class AuctionSnapshot:
    """单时点竞价快照（placed/canceled 为当日累计口径）。"""

    ts: str  # ISO 时间戳（须含 HH:MM）
    indicative_price: float  # 虚拟撮合价
    indicative_volume: float  # 虚拟撮合量（累计）
    buy1_volume: float  # 买一档封单量
    placed_volume: float  # 累计申报量
    canceled_volume: float  # 累计撤单量

    def __post_init__(self) -> None:
        if not self.ts or len(self.ts) < 16:
            raise ValueError(f"ts 非法: {self.ts!r}")
        if self.indicative_price <= 0:
            raise ValueError(f"indicative_price 须>0: {self.indicative_price}")
        for name in ("indicative_volume", "buy1_volume", "placed_volume", "canceled_volume"):
            v = getattr(self, name)
            if v < 0:
                raise ValueError(f"{name} 须≥0: {v}")
        if self.canceled_volume > self.placed_volume:
            raise ValueError(f"撤单量({self.canceled_volume}) 不得大于申报量({self.placed_volume})")


@dataclass(frozen=True, slots=True)
class AuctionMicroConfig:
    """竞价微结构配置（MVP 初拍值待回验标定，全可配）。"""

    grab_min_drift_pct: float = 1.0  # 抢筹：价漂移下限 %
    grab_max_cancel_rate: float = 0.10  # 抢筹：撤单率上限
    grab_min_seal_change_pct: float = 50.0  # 抢筹：封单增幅下限 %
    bait_min_early_drift_pct: float = 1.0  # 诱多：早段漂移下限 %
    bait_min_cancel_rate: float = 0.30  # 诱多：撤单率下限
    bait_min_seal_drop_pct: float = 0.50  # 诱多：后段封单塌陷幅度下限（小数）
    press_max_drift_pct: float = -0.5  # 压价：价漂移上限 %
    press_max_seal_change_pct: float = -20.0  # 压价：封单变化上限 %

    def __post_init__(self) -> None:
        if not 0.0 <= self.grab_max_cancel_rate <= 1.0:
            raise ValueError(f"grab_max_cancel_rate 须∈[0,1]: {self.grab_max_cancel_rate}")
        if not 0.0 <= self.bait_min_cancel_rate <= 1.0:
            raise ValueError(f"bait_min_cancel_rate 须∈[0,1]: {self.bait_min_cancel_rate}")
        if not 0.0 <= self.bait_min_seal_drop_pct <= 1.0:
            raise ValueError(f"bait_min_seal_drop_pct 须∈[0,1]: {self.bait_min_seal_drop_pct}")


@dataclass(frozen=True, slots=True)
class AuctionFeatures:
    """竞价七族特征。"""

    price_drift_pct: float  # 首→末虚拟撮合价漂移 %
    volume_slope: float  # 撮合量斜率（量/分钟）
    cancel_rate: float  # 撤单率=累计撤单/累计申报
    seal_change_pct: float  # 封单变化 %（首→末买一档）
    late_volume_ratio: float  # 9:20 后量占比
    early_drift_pct: float  # 早段（9:20 前）价漂移 %
    seal_late_drop_pct: float  # 后段封单自早段峰值塌陷幅度（小数，负=未塌）

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AuctionSignal:
    """竞价信号输出。"""

    symbol: str
    behavior: AuctionBehavior
    direction: str  # LONG / SHORT / NEUTRAL
    confidence: float  # 命中规则条数/该行为规则总数
    features: AuctionFeatures
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["behavior"] = self.behavior.value
        return d


def _hhmm(ts: str) -> str:
    return ts[11:16]


def _minutes(ts: str) -> int:
    hhmm = _hhmm(ts)
    return int(hhmm[:2]) * 60 + int(hhmm[3:5])


def _extract_features(snaps: Sequence[AuctionSnapshot], notes: list[str]) -> AuctionFeatures:
    first, last = snaps[0], snaps[-1]
    price_drift_pct = (last.indicative_price - first.indicative_price) / first.indicative_price * 100.0
    span_min = max(_minutes(last.ts) - _minutes(first.ts), 1)
    volume_slope = (last.indicative_volume - first.indicative_volume) / span_min

    if last.placed_volume > 0:
        cancel_rate = last.canceled_volume / last.placed_volume
    else:
        cancel_rate = 0.0
        notes.append("申报量为0，撤单率按0.0处理")

    if first.buy1_volume > 0:
        seal_change_pct = (last.buy1_volume - first.buy1_volume) / first.buy1_volume * 100.0
    else:
        seal_change_pct = 0.0
        notes.append("首快照封单为0，封单变化按0.0处理")

    early = [s for s in snaps if _hhmm(s.ts) < _LATE_START_HHMM]
    if early and last.indicative_volume > 0:
        early_max_vol = max(s.indicative_volume for s in early)
        late_volume_ratio = max(0.0, (last.indicative_volume - early_max_vol)) / last.indicative_volume
    else:
        late_volume_ratio = 1.0 if not early else 0.0

    if len(early) >= 2:
        early_drift_pct = (early[-1].indicative_price - first.indicative_price) / first.indicative_price * 100.0
    else:
        early_drift_pct = 0.0

    if early:
        early_peak_seal = max(s.buy1_volume for s in early)
        seal_late_drop_pct = (early_peak_seal - last.buy1_volume) / early_peak_seal if early_peak_seal > 0 else 0.0
    else:
        seal_late_drop_pct = 0.0

    return AuctionFeatures(
        price_drift_pct=price_drift_pct,
        volume_slope=volume_slope,
        cancel_rate=cancel_rate,
        seal_change_pct=seal_change_pct,
        late_volume_ratio=late_volume_ratio,
        early_drift_pct=early_drift_pct,
        seal_late_drop_pct=seal_late_drop_pct,
    )


def analyze_auction(
    symbol: str,
    snapshots: Sequence[AuctionSnapshot],
    config: AuctionMicroConfig | None = None,
) -> AuctionSignal:
    """竞价微结构主核（纯函数）：校验→特征→行为分类→信号。"""
    if not symbol:
        raise ValueError("symbol 不能为空")
    if not snapshots:
        raise ValueError("snapshots 不能为空")
    cfg = config or AuctionMicroConfig()
    for prev, cur in zip(snapshots, snapshots[1:]):
        if _minutes(cur.ts) <= _minutes(prev.ts):
            raise ValueError(f"快照时间戳须严格递增: {prev.ts} → {cur.ts}")

    if len(snapshots) == 1:
        feats = _extract_features(snapshots, notes := [])
        notes.append("单快照，特征不全，退化 NEUTRAL")
        return AuctionSignal(
            symbol=symbol,
            behavior=AuctionBehavior.NEUTRAL,
            direction="NEUTRAL",
            confidence=0.0,
            features=feats,
            notes=tuple(notes),
        )

    notes: list[str] = []
    f = _extract_features(snapshots, notes)

    # ── 三族行为规则（命中条数/总条数=置信度）──
    grab_hits = [
        f.price_drift_pct >= cfg.grab_min_drift_pct,
        f.cancel_rate <= cfg.grab_max_cancel_rate,
        f.seal_change_pct >= cfg.grab_min_seal_change_pct,
    ]
    bait_hits = [
        f.early_drift_pct >= cfg.bait_min_early_drift_pct,
        f.cancel_rate >= cfg.bait_min_cancel_rate,
        f.seal_late_drop_pct >= cfg.bait_min_seal_drop_pct,
    ]
    press_hits = [
        f.price_drift_pct <= cfg.press_max_drift_pct,
        f.seal_change_pct <= cfg.press_max_seal_change_pct,
    ]

    candidates: list[tuple[AuctionBehavior, str, float, bool]] = [
        (AuctionBehavior.GRAB, "LONG", sum(grab_hits) / len(grab_hits), all(grab_hits)),
        (AuctionBehavior.BAIT, "SHORT", sum(bait_hits) / len(bait_hits), all(bait_hits)),
        (AuctionBehavior.PRESS, "SHORT", sum(press_hits) / len(press_hits), all(press_hits)),
    ]
    full = [c for c in candidates if c[3]]
    if full:
        # 全中族取置信度最高；同分按 GRAB>BAIT>PRESS 静态序
        behavior, direction, confidence, _ = max(full, key=lambda c: c[2])
    else:
        behavior, direction, confidence = AuctionBehavior.NEUTRAL, "NEUTRAL", 0.0
        notes.append("无一行为规则全中，按 NEUTRAL 输出")

    logger.info("竞价微结构: %s 行为=%s 置信度=%.2f", symbol, behavior.value, confidence)
    return AuctionSignal(
        symbol=symbol,
        behavior=behavior,
        direction=direction,
        confidence=confidence,
        features=f,
        notes=tuple(notes),
    )


class AuctionMicrostructureAnalyzer:
    """竞价微结构分析器门面（配置持有 + analyze_auction 纯函数核委托）。"""

    def __init__(self, config: AuctionMicroConfig | None = None) -> None:
        self._cfg = config or AuctionMicroConfig()

    def analyze(self, symbol: str, snapshots: Sequence[AuctionSnapshot]) -> AuctionSignal:
        """竞价微结构分析（委托 analyze_auction 纯函数核）。"""
        return analyze_auction(symbol, snapshots, self._cfg)
