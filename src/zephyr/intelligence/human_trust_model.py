# [BLUEPRINT] MOD-INT-HUMAN-TRUST | docs/03_modules/_domain_intelligence/human_trust_model/blueprint.md
# [MODULE] zephyr.intelligence.human_trust_model
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（信任模型核心纯内存；clock/audit_sink 全注入）
# [CONSUMERS] 运行时装配批（决策域阈值表装配 / 人工否决录入接 HITL 前端 / 分数变更审计接审计链）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 决策域词表注入闭合（未注册域 Fail-Closed）；auto>=confirm 阈值合法否则拒装；置信度/信任分恒在 [0,1]；否决原因分类非空；周期校准 period_id 每域唯一（重复拒绝）；分数变更必写审计；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/human_trust_model/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] HumanTrustError(占位 ZA-IT-UNREGISTERED-HUMAN-TRUST)——未知决策域/非法阈值表/非法置信度/空原因分类/重复校准周期时抛
# [TESTS] tests/intelligence/test_human_trust_model.py
# [A_module] module_id=MOD-INT-HUMAN-TRUST | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""HumanTrustModel — 人机信任模型（MOD-INT-HUMAN-TRUST）。

B1-00221（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-AISA-009，C2 C-031）：
AI 协作信任模型——置信度**三层路由**（自动执行 auto / 需人工确认 confirm /
禁止 forbidden，阈值表按决策域注入）+ **人工否决记录学习**（否决原因分类
统计 + 分域支配模式提取）+ **周期信任分校准**（按决策域分别校准，分数变
更写审计）。HITL 信任校准件，仅产出路由建议不直接下单。

查重分工（蓝图 §0）：risk_veto_engine=交易侧风控否决执行（本件=人机协作
信任分与路由，不执行否决）；reflctrl_gate=反思频率分层（零交集）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "HumanTrustError",
    "HumanTrustModel",
    "TrustRoute",
    "TrustScoreChange",
    "TrustThresholds",
    "VetoPattern",
    "VetoRecord",
]

#: 信任分下限/上限（校准后截断闭区间）
_SCORE_MIN: Final = 0.0
_SCORE_MAX: Final = 1.0


class HumanTrustError(Exception):
    """人机信任模型输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-IT-UNREGISTERED-HUMAN-TRUST。
    """


class TrustRoute(str, Enum):
    """置信度三层路由（词表闭合）。"""

    AUTO = "auto"
    CONFIRM = "confirm"
    FORBIDDEN = "forbidden"


@dataclass(frozen=True)
class TrustThresholds:
    """单决策域路由阈值表（frozen；auto_threshold >= confirm_threshold）。"""

    auto_threshold: float
    confirm_threshold: float
    initial_trust: float = 0.5


@dataclass(frozen=True)
class VetoRecord:
    """人工否决记录（学习样本，frozen）。"""

    domain: str
    reason_category: str
    detail: str
    recorded_at: datetime.datetime


@dataclass(frozen=True)
class VetoPattern:
    """分域否决模式提取结果（确定性排序）。"""

    domain: str
    total: int
    category_counts: tuple[tuple[str, int], ...]
    dominant_category: str | None


@dataclass(frozen=True)
class TrustScoreChange:
    """周期信任分校准变更（审计载荷，frozen）。"""

    domain: str
    period_id: str
    old_score: float
    new_score: float
    veto_rate: float
    decisions_observed: int
    changed_at: datetime.datetime


class HumanTrustModel:
    """人机信任模型件（三层路由 + 否决学习 + 周期校准）。"""

    def __init__(
        self,
        *,
        thresholds: Mapping[str, TrustThresholds],
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[TrustScoreChange], None] | None = None,
    ) -> None:
        if not thresholds:
            raise HumanTrustError("thresholds 为空（无决策域阈值表）")
        for domain, th in thresholds.items():
            if not domain:
                raise HumanTrustError("决策域名为空")
            if not isinstance(th, TrustThresholds):
                raise HumanTrustError(f"非法阈值表: {domain!r}")
            for name, v in (
                ("auto_threshold", th.auto_threshold),
                ("confirm_threshold", th.confirm_threshold),
                ("initial_trust", th.initial_trust),
            ):
                if not (_SCORE_MIN <= v <= _SCORE_MAX):
                    raise HumanTrustError(f"{domain}.{name} 越界 [0,1]: {v!r}")
            if th.auto_threshold < th.confirm_threshold:
                raise HumanTrustError(
                    f"{domain} 阈值倒挂: auto {th.auto_threshold} < confirm {th.confirm_threshold}"
                )
        self._thresholds: dict[str, TrustThresholds] = dict(thresholds)
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._scores: dict[str, float] = {
            d: th.initial_trust for d, th in thresholds.items()
        }
        self._vetoes: dict[str, list[VetoRecord]] = {d: [] for d in thresholds}
        self._calibrated_periods: dict[str, set[str]] = {d: set() for d in thresholds}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_domain(self, domain: str) -> None:
        if domain not in self._thresholds:
            raise HumanTrustError(f"未知决策域: {domain!r}（未在阈值表注册）")

    # ── 三层路由 ──────────────────────────────────────────────────────────

    def route(self, domain: str, confidence: float) -> TrustRoute:
        """置信度路由：>=auto→AUTO；>=confirm→CONFIRM；否则 FORBIDDEN。"""
        self._require_domain(domain)
        if not (_SCORE_MIN <= confidence <= _SCORE_MAX):
            raise HumanTrustError(f"置信度越界 [0,1]: {confidence!r}")
        th = self._thresholds[domain]
        if confidence >= th.auto_threshold:
            return TrustRoute.AUTO
        if confidence >= th.confirm_threshold:
            return TrustRoute.CONFIRM
        return TrustRoute.FORBIDDEN

    # ── 人工否决记录学习 ──────────────────────────────────────────────────

    def record_veto(self, record: VetoRecord) -> None:
        """录入人工否决：决策域须已注册，原因分类非空。"""
        self._require_domain(record.domain)
        if not record.reason_category:
            raise HumanTrustError("否决原因分类为空")
        self._vetoes[record.domain].append(record)

    def veto_pattern(self, domain: str) -> VetoPattern:
        """分域否决原因分类统计 + 支配模式提取（并列按分类名序确定）。"""
        self._require_domain(domain)
        records = self._vetoes[domain]
        counts: dict[str, int] = {}
        for rec in records:
            counts[rec.reason_category] = counts.get(rec.reason_category, 0) + 1
        ordered = tuple(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
        dominant = ordered[0][0] if ordered else None
        return VetoPattern(
            domain=domain,
            total=len(records),
            category_counts=ordered,
            dominant_category=dominant,
        )

    # ── 周期信任分校准 ────────────────────────────────────────────────────

    def trust_score(self, domain: str) -> float:
        """当前分域信任分。"""
        self._require_domain(domain)
        return self._scores[domain]

    def recalibrate(
        self,
        domain: str,
        *,
        period_id: str,
        decisions_observed: int,
    ) -> TrustScoreChange:
        """周期校准：否决率=否决数/观测决策数；新分=旧分×(1-否决率) 截断 [0,1]。

        分数变更必写审计（audit_sink 注入时）；period_id 每域唯一，重复拒绝。
        """
        self._require_domain(domain)
        if not period_id:
            raise HumanTrustError("period_id 为空")
        if period_id in self._calibrated_periods[domain]:
            raise HumanTrustError(f"校准周期重复: {domain}/{period_id!r}")
        if decisions_observed <= 0:
            raise HumanTrustError(f"decisions_observed 非正: {decisions_observed!r}")
        veto_count = len(self._vetoes[domain])
        if veto_count > decisions_observed:
            raise HumanTrustError(
                f"否决数 {veto_count} 超过观测决策数 {decisions_observed}"
            )
        veto_rate = veto_count / decisions_observed
        old = self._scores[domain]
        new = min(_SCORE_MAX, max(_SCORE_MIN, old * (1.0 - veto_rate)))
        change = TrustScoreChange(
            domain=domain,
            period_id=period_id,
            old_score=old,
            new_score=new,
            veto_rate=veto_rate,
            decisions_observed=decisions_observed,
            changed_at=self._clock(),
        )
        self._scores[domain] = new
        self._calibrated_periods[domain].add(period_id)
        _log.info(
            "信任分校准: %s %s %.4f -> %.4f (veto_rate=%.4f)",
            domain, period_id, old, new, veto_rate,
        )
        if self._audit_sink is not None:
            self._audit_sink(change)
        return change
