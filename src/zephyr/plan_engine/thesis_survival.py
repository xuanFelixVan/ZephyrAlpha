# [BLUEPRINT] MOD-PLAN-024 | docs/03_modules/_domain_plan_engine/thesis_survival/blueprint.md
# [MODULE] zephyr.plan_engine.thesis_survival
# [DOMAIN] D_PLAN
# [DEPENDENCIES] 无（纯函数核，零 IO；持仓证据由调用方从行情/事件源算好注入）
# [CONSUMERS] TDM-P-P1-03（买入逻辑存活判定）；X 流离场评估（失效→转离场评估，待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 四类买入理由各自独立判据（打板查梯队/多因子查漂移/事件查衰减/做T查趋势）; 输出三态 ALIVE/WEAKENED/DEAD（失效=转离场评估）; 证据缺失(None)→WEAKENED（不确定但不武断判死）; DEAD 判定只来自明确证伪（梯队断/漂移超阈/兑现超阈/趋势破）; 同输入必同输出(frozen); 阈值 config 注入（经验拍定=proposed）
# [MODIFY-GUARD] 地图节点 TDM-P-P1-03
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 漂移/衰减比例越界 → ThesisSurvivalError（fail-closed）
# [TESTS] tests/plan_engine/test_thesis_survival.py
# [TTL] permanent
"""ThesisSurvival — 买入逻辑存活判定（MOD-PLAN-024，TDM-P-P1-03）。

节点语义逐条吸收（真源=TDM-P-P1-03 algo_note）——按买入理由逐仓回查：
- 打板仓：情绪梯队还在不在（板块还热吗）→ ladder_alive
- 多因子仓：因子暴露漂移（当初的因子还强吗）→ factor_exposure_drift
- 事件仓：事件衰减（利好兑现没）→ event_decay_ratio
- 做T底仓：趋势没破 → trend_broken
输出三态：成立（ALIVE）/ 弱化（WEAKENED）/ 失效（DEAD）；**失效=转离场评估**。

设计原则：
- 每仓只按其买入理由类型判定（打板仓不看因子漂移）——类型驱动分派；
- 证据缺失 → WEAKENED：不确定时降预期但不武断判死（判死=触发离场，代价高，
  需明确证伪：梯队断/漂移超阈/兑现超阈/趋势破）；
- 阈值经验拍定（proposed），回测校准后升级。

查重分工（蓝图 §1）：plan_deviation_monitor（MOD-PLAN-022）=计划**收益偏差**
z-score 监控（实际 vs 计划收益）；本件=买入**理由逻辑**存活回查（为什么买的
那个理由还在吗）。execution_deviation_attributor=执行偏差事后归因。三者正交。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ThesisSurvivalError(ValueError):
    """非法输入（fail-closed）：比例越界。"""


class ThesisType(str, Enum):
    """买入理由类型（逐仓标注，决定回查判据）。"""

    LIMIT_UP_CHASING = "LIMIT_UP_CHASING"  # 打板仓
    MULTI_FACTOR = "MULTI_FACTOR"  # 多因子仓
    EVENT_DRIVEN = "EVENT_DRIVEN"  # 事件仓
    T0_BASE = "T0_BASE"  # 做T底仓


class ThesisState(str, Enum):
    """存活三态：DEAD=转离场评估（X 流信号）。"""

    ALIVE = "ALIVE"
    WEAKENED = "WEAKENED"
    DEAD = "DEAD"


@dataclass(frozen=True)
class ThesisSurvivalConfig:
    """判定阈值（经验拍定=proposed，回测校准后升级）。"""

    factor_drift_weak: float = 0.30  # 多因子：漂移 >0.30 → 弱化
    factor_drift_dead: float = 0.60  # 多因子：漂移 >0.60 → 失效（原因子已失效）
    event_decay_alive: float = 0.50  # 事件：兑现 ≤50% → 成立
    event_decay_dead: float = 0.80  # 事件：兑现 >80% → 失效（利好兑现完）

    def __post_init__(self) -> None:
        for name in ("factor_drift_weak", "factor_drift_dead", "event_decay_alive", "event_decay_dead"):
            v = getattr(self, name)
            if v != v or not (0.0 < v < 1.0):
                raise ThesisSurvivalError(f"{name} 须 ∈ (0,1): {v}")
        if self.factor_drift_weak >= self.factor_drift_dead:
            raise ThesisSurvivalError("factor_drift_weak 必须 < factor_drift_dead")
        if self.event_decay_alive >= self.event_decay_dead:
            raise ThesisSurvivalError("event_decay_alive 必须 < event_decay_dead")


@dataclass(frozen=True)
class ThesisEvidence:
    """持仓证据快照（None=该维度暂无数据）。只填与买入理由类型相关字段。"""

    sentiment_ladder_alive: bool | None = None  # 打板：板块梯队还热
    factor_exposure_drift: float | None = None  # 多因子：暴露漂移 ∈[0,1]
    event_decay_ratio: float | None = None  # 事件：衰减/兑现度 ∈[0,1]
    trend_broken: bool | None = None  # 做T底仓：趋势破

    def __post_init__(self) -> None:
        for name in ("factor_exposure_drift", "event_decay_ratio"):
            v = getattr(self, name)
            if v is not None and (v != v or v < 0.0 or v > 1.0):
                raise ThesisSurvivalError(f"{name} 越界 [0,1]: {v}")


@dataclass(frozen=True)
class ThesisVerdict:
    """存活判定（frozen，可审计）。"""

    state: ThesisState
    reason: str  # 一句话判定依据


def evaluate_thesis(
    thesis_type: ThesisType | str,
    evidence: ThesisEvidence,
    config: ThesisSurvivalConfig | None = None,
) -> ThesisVerdict:
    """按买入理由类型回查逻辑存活（纯函数，同输入必同输出）。"""
    cfg = config or ThesisSurvivalConfig()
    try:
        t = ThesisType(thesis_type)
    except ValueError as exc:
        raise ThesisSurvivalError(f"未知买入理由类型: {thesis_type!r}") from exc
    if t is ThesisType.LIMIT_UP_CHASING:
        return _judge_limit_up(evidence)
    if t is ThesisType.MULTI_FACTOR:
        return _judge_multi_factor(evidence, cfg)
    if t is ThesisType.EVENT_DRIVEN:
        return _judge_event(evidence, cfg)
    return _judge_t0_base(evidence)


def _judge_limit_up(evidence: ThesisEvidence) -> ThesisVerdict:
    """打板仓：情绪梯队还在不在（板块还热吗）。"""
    if evidence.sentiment_ladder_alive is None:
        return ThesisVerdict(ThesisState.WEAKENED, "梯队热度未知——弱化处理")
    if evidence.sentiment_ladder_alive:
        return ThesisVerdict(ThesisState.ALIVE, "情绪梯队仍在，逻辑成立")
    return ThesisVerdict(ThesisState.DEAD, "情绪梯队已断——逻辑证伪")


def _judge_multi_factor(evidence: ThesisEvidence, cfg: ThesisSurvivalConfig) -> ThesisVerdict:
    """多因子仓：因子暴露漂移三段（可控/超弱化线/原因子失效）。"""
    d = evidence.factor_exposure_drift
    if d is None:
        return ThesisVerdict(ThesisState.WEAKENED, "因子暴露漂移未知——弱化处理")
    if d > cfg.factor_drift_dead:
        return ThesisVerdict(ThesisState.DEAD, f"因子漂移 {d:.0%} 超 {cfg.factor_drift_dead:.0%}——原因子失效")
    if d > cfg.factor_drift_weak:
        return ThesisVerdict(ThesisState.WEAKENED, f"因子漂移 {d:.0%} 超弱化线")
    return ThesisVerdict(ThesisState.ALIVE, f"因子暴露漂移 {d:.0%} 可控")


def _judge_event(evidence: ThesisEvidence, cfg: ThesisSurvivalConfig) -> ThesisVerdict:
    """事件仓：利好兑现度三段（发酵/动能衰减/完结）。"""
    r = evidence.event_decay_ratio
    if r is None:
        return ThesisVerdict(ThesisState.WEAKENED, "事件衰减未知——弱化处理")
    if r > cfg.event_decay_dead:
        return ThesisVerdict(ThesisState.DEAD, f"利好兑现 {r:.0%} 超阈——事件逻辑完结")
    if r > cfg.event_decay_alive:
        return ThesisVerdict(ThesisState.WEAKENED, f"利好已兑现 {r:.0%}——动能衰减")
    return ThesisVerdict(ThesisState.ALIVE, f"事件仍在发酵（兑现 {r:.0%}）")


def _judge_t0_base(evidence: ThesisEvidence) -> ThesisVerdict:
    """做T底仓：趋势破没破。"""
    if evidence.trend_broken is None:
        return ThesisVerdict(ThesisState.WEAKENED, "趋势状态未知——弱化处理")
    if evidence.trend_broken:
        return ThesisVerdict(ThesisState.DEAD, "底仓趋势已破——逻辑证伪")
    return ThesisVerdict(ThesisState.ALIVE, "底仓趋势完好")
