# [BLUEPRINT] MOD-SIG-087 | docs/03_modules/_domain_signal/signal_factory/blueprint.md
# [MODULE] zephyr.signal_ashare.signal_factory
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.conditional_density_predictor（MOD-SIG-043 DensityForecast 契约复用，prod）
# [CONSUMERS] （候选：selection_funnel_skeleton MOD-SIG-086 漏斗骨架、盘前/打板监控编排）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 9阶段封闭集；主链不可跳跃不可倒退（DRAFT→VALIDATED→DENSITY_ENHANCED→QUALITY_GATED→CROWDING_GATED→FUNNELED→RELEASED）；RELEASED→EXPIRED→RETIRED 终态链；质量门/拥挤度门阻断=不推进+notes留痕；frozen dataclass asdict JSON 可序列化；纯内存注册表不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B1-00149 行 + 候选注册表 CAND-TESTB-002
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 重复 signal_id/空 id/非法方向/强度越界/非法迁移/未知 id/缺 density → ValueError（fail-closed）；门阻断不抛异常（留 notes 返还原阶段记录）
# [TESTS] tests/signal_ashare/test_signal_factory.py
# [A_module] module_id=MOD-SIG-087 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""C-028 信号工厂（MOD-SIG-087，B1-00149）。

信号散件众多、9 阶段生命周期与密度预测增强输出未成统一工厂（深挖裁定理由）。
本模块收口信号从注册到入漏斗的全生命周期：

    DRAFT → VALIDATED → DENSITY_ENHANCED → QUALITY_GATED
          → CROWDING_GATED → FUNNELED → RELEASED → EXPIRED → RETIRED

- **9 阶段状态机**：主链 7 跳不可跳跃；EXPIRED/RETIRED 为终态分支。
- **信号注册表**：内存幂等键注册（重复 id fail-closed），全量记录可追溯。
- **密度增强**：消费 MOD-SIG-043 DensityForecast 契约（分位数落记录；
  degraded 桶置信度降档 0.5，正常 1.0——规则文档化，后续由标定批替换）。
- **质量门/拥挤度门**：分数注入（SIGQC/拥挤度模块挂接口），低于/高于
  阈值阻断推进并留 notes，不抛异常（门语义=拦截非错误）。
- **入漏斗**：funnel_batch 仅产出 FUNNELED 阶段信号，供 MOD-SIG-086 漏斗骨架消费。

不做什么：不实现漏斗逻辑（MOD-SIG-086 职责）、不重写密度算法（MOD-SIG-043）、
不直连 DB/不荐股。

依据: AUD-DRAFT-001 深挖批 B1-00149（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-087
Version: 0.1.0

# [ALGO_FLOW]
# 输入: SignalDraft（id/symbol/direction/strength/source）+ density/quality/crowding 注入
# 特征: 阶段机当前态 + 门分数
# 算法: 注册校验 → 逐跳推进（密度落分位数+置信度规则 → 质量门 → 拥挤度门）→ 漏斗批量
# 输出: SignalRecord（stage/quantiles/confidence/quality/crowding/history/notes）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from typing import Any, Final

from zephyr.signal_ashare.conditional_density_predictor import DensityForecast

logger = logging.getLogger(__name__)

__all__: Final = [
    "SignalDraft",
    "SignalFactory",
    "SignalFactoryConfig",
    "SignalRecord",
    "SignalStage",
]

_DIRECTIONS: Final = frozenset({"LONG", "SHORT"})
#: degraded 密度桶置信度降档系数（MVP 初拍值，待标定批替换）
_DEGRADED_CONFIDENCE: Final = 0.5


class SignalStage(str, Enum):
    """信号生命周期 9 阶段（主链 7 跳 + 终态 2 跳，封闭集）。"""

    DRAFT = "草稿"
    VALIDATED = "已校验"
    DENSITY_ENHANCED = "密度增强"
    QUALITY_GATED = "质量门通过"
    CROWDING_GATED = "拥挤度门通过"
    FUNNELED = "已入漏斗"
    RELEASED = "已发布"
    EXPIRED = "已过期"
    RETIRED = "已退役"


#: 正向主链（索引相邻=唯一合法迁移）
_MAIN_CHAIN: Final = (
    SignalStage.DRAFT,
    SignalStage.VALIDATED,
    SignalStage.DENSITY_ENHANCED,
    SignalStage.QUALITY_GATED,
    SignalStage.CROWDING_GATED,
    SignalStage.FUNNELED,
    SignalStage.RELEASED,
)


@dataclass(frozen=True, slots=True)
class SignalFactoryConfig:
    """信号工厂配置（MVP 初拍值，全可配）。"""

    min_quality_score: float = 0.4  # 质量门通过下限（0~1）
    max_crowding_score: float = 0.8  # 拥挤度门通过上限（0~1）

    def __post_init__(self) -> None:
        if not 0.0 <= self.min_quality_score <= 1.0:
            raise ValueError(f"min_quality_score 须∈[0,1]: {self.min_quality_score}")
        if not 0.0 <= self.max_crowding_score <= 1.0:
            raise ValueError(f"max_crowding_score 须∈[0,1]: {self.max_crowding_score}")


@dataclass(frozen=True, slots=True)
class SignalDraft:
    """信号注册草稿（入册前）。"""

    signal_id: str
    symbol: str
    direction: str  # LONG / SHORT
    strength: float  # 0~1
    source: str  # 产出散件标识（留痕）


@dataclass(frozen=True, slots=True)
class SignalRecord:
    """单信号全生命周期记录。"""

    signal_id: str
    symbol: str
    direction: str
    strength: float
    source: str
    stage: SignalStage
    quantiles: dict[float, float] = field(default_factory=dict)
    confidence: float = 0.0
    quality_score: float = 0.0
    crowding_score: float = 0.0
    history: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["stage"] = self.stage.value
        d["quantiles"] = {str(k): v for k, v in self.quantiles.items()}
        return d


class SignalFactory:
    """C-028 信号工厂：注册表 + 9 阶段状态机 + 门挂接 + 漏斗产出。"""

    def __init__(self, config: SignalFactoryConfig | None = None) -> None:
        self._cfg = config or SignalFactoryConfig()
        self._registry: dict[str, SignalRecord] = {}

    # ── 注册 ─────────────────────────────────────────────
    def register(self, draft: SignalDraft) -> SignalRecord:
        """草稿入册为 DRAFT（幂等键=signal_id，重复 fail-closed）。"""
        if not draft.signal_id:
            raise ValueError("signal_id 不能为空")
        if not draft.symbol:
            raise ValueError("symbol 不能为空")
        if draft.direction not in _DIRECTIONS:
            raise ValueError(f"direction 须为 {sorted(_DIRECTIONS)}: {draft.direction}")
        if not 0.0 <= draft.strength <= 1.0:
            raise ValueError(f"strength 须∈[0,1]: {draft.strength}")
        if draft.signal_id in self._registry:
            raise ValueError(f"signal_id 重复注册: {draft.signal_id}")
        rec = SignalRecord(
            signal_id=draft.signal_id,
            symbol=draft.symbol,
            direction=draft.direction,
            strength=draft.strength,
            source=draft.source,
            stage=SignalStage.DRAFT,
            history=(SignalStage.DRAFT.value,),
        )
        self._registry[rec.signal_id] = rec
        logger.info("信号入册: %s (%s %s)", rec.signal_id, rec.symbol, rec.direction)
        return rec

    def get(self, signal_id: str) -> SignalRecord:
        """按 id 取记录（未知 id fail-closed）。"""
        try:
            return self._registry[signal_id]
        except KeyError:
            raise ValueError(f"未知 signal_id: {signal_id}") from None

    # ── 推进 ─────────────────────────────────────────────
    def advance(
        self,
        signal_id: str,
        *,
        density: DensityForecast | None = None,
        quality_score: float | None = None,
        crowding_score: float | None = None,
    ) -> SignalRecord:
        """沿主链推进一跳；门阻断=不推进+notes 留痕。"""
        rec = self.get(signal_id)
        if rec.stage not in _MAIN_CHAIN[:-1]:
            raise ValueError(f"阶段 {rec.stage.value} 不在主链可推进位")
        nxt = _MAIN_CHAIN[_MAIN_CHAIN.index(rec.stage) + 1]

        if nxt is SignalStage.DENSITY_ENHANCED:
            if density is None:
                raise ValueError("推进 DENSITY_ENHANCED 必须注入 density")
            rec = replace(
                rec,
                quantiles=dict(density.quantiles),
                confidence=_DEGRADED_CONFIDENCE if density.degraded else 1.0,
            )
        elif nxt is SignalStage.QUALITY_GATED:
            if quality_score is None or not 0.0 <= quality_score <= 1.0:
                raise ValueError(f"quality_score 须∈[0,1]: {quality_score}")
            rec = replace(rec, quality_score=quality_score)
            if quality_score < self._cfg.min_quality_score:
                rec = replace(
                    rec,
                    notes=rec.notes + (f"质量门阻断: {quality_score:.3f}<{self._cfg.min_quality_score}",),
                )
                self._registry[signal_id] = rec
                return rec
        elif nxt is SignalStage.CROWDING_GATED:
            if crowding_score is None or not 0.0 <= crowding_score <= 1.0:
                raise ValueError(f"crowding_score 须∈[0,1]: {crowding_score}")
            rec = replace(rec, crowding_score=crowding_score)
            if crowding_score > self._cfg.max_crowding_score:
                rec = replace(
                    rec,
                    notes=rec.notes + (f"拥挤度门阻断: {crowding_score:.3f}>{self._cfg.max_crowding_score}",),
                )
                self._registry[signal_id] = rec
                return rec

        rec = replace(rec, stage=nxt, history=rec.history + (nxt.value,))
        self._registry[signal_id] = rec
        return rec

    def expire(self, signal_id: str) -> SignalRecord:
        """RELEASED → EXPIRED（仅发布态可过期）。"""
        rec = self.get(signal_id)
        if rec.stage is not SignalStage.RELEASED:
            raise ValueError(f"仅 RELEASED 可过期，当前: {rec.stage.value}")
        return self._move(signal_id, SignalStage.EXPIRED)

    def retire(self, signal_id: str) -> SignalRecord:
        """EXPIRED → RETIRED（仅过期态可退役）。"""
        rec = self.get(signal_id)
        if rec.stage is not SignalStage.EXPIRED:
            raise ValueError(f"仅 EXPIRED 可退役，当前: {rec.stage.value}")
        return self._move(signal_id, SignalStage.RETIRED)

    def _move(self, signal_id: str, stage: SignalStage) -> SignalRecord:
        rec = self.get(signal_id)
        rec = replace(rec, stage=stage, history=rec.history + (stage.value,))
        self._registry[signal_id] = rec
        return rec

    # ── 漏斗产出 ─────────────────────────────────────────
    def funnel_batch(self) -> list[SignalRecord]:
        """产出全部 FUNNELED 阶段信号（供 MOD-SIG-086 漏斗骨架消费）。"""
        return [r for r in self._registry.values() if r.stage is SignalStage.FUNNELED]
