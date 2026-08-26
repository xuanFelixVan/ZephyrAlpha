# [BLUEPRINT] MOD-SIGQC-006 | docs/03_modules/_domain_signal_quality/signal_explainability_guarantor/blueprint.md
# [MODULE] zephyr.signal_quality.signal_explainability_guarantor
# [DOMAIN] D_SIGQC
# [DEPENDENCIES] 无（保障核心纯内存；audit_sink/alert_sink/clock 全注入）
# [CONSUMERS] 运行时装配批（信号出站前强制校验 / 审计链 sink 装配 / 事后回放反查）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 理由链三要素(触发因子/规则命中/置信度依据)强制; 缺失即告警+阻断(抛Error); 齐全方入审计链sink与内存档案; audit_sink未注入/写失败Fail-Closed; 按signal_id反查回放; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal_quality/signal_explainability_guarantor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ExplainabilityGuarantorError(占位 ZA-SIGQC-UNREGISTERED-EXPLAINABILITY-GUARANTOR)——三要素缺失/空字段/置信度越界/signal_id冲突/audit_sink未注入或写失败/未知signal_id回放时抛
# [TESTS] tests/signal_quality/test_signal_explainability_guarantor.py
# [A_module] module_id=MOD-SIGQC-006 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""SignalExplainabilityGuarantor — 信号可解释性强制保障器（MOD-SIGQC-006）。

B2-05485（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SIGQC-005，B2
D-SIGNAL-211）：可解释性强制契约——信号输出必须携带理由链（触发因子 + 规
则命中 + 置信度依据三要素）+ 缺失即阻断 + 告警 + 解释字段入
decision_snapshot/signal_audit 链（注入 sink）+ 事后回放支持（按
signal_id 反查）。

查重分工（蓝图 §0）：decision_snapshot（D_FUNDAMENTAL_SIGNAL）=决策快照
存取设施（degraded 降级不阻塞）；本件=信号出站侧的强制门禁（缺失即阻断），
经注入 audit_sink 写入审计链，不自建存储设施。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ExplainabilityGuarantorError",
    "ExplainabilityViolation",
    "ExplanationRecord",
    "ReasonChain",
    "SignalExplainabilityGuarantor",
]


class ExplainabilityGuarantorError(Exception):
    """可解释性强制契约违反（Fail-Closed：缺失即阻断）。

    未登记错误码-申请中：占位 ZA-SIGQC-UNREGISTERED-EXPLAINABILITY-GUARANTOR。
    """


@dataclass(frozen=True)
class ReasonChain:
    """理由链三要素（frozen）：触发因子 + 规则命中 + 置信度依据。"""

    trigger_factors: tuple[str, ...]
    rule_hits: tuple[str, ...]
    confidence_basis: str


@dataclass(frozen=True)
class ExplainabilityViolation:
    """三要素缺失违规（告警载荷，frozen）。"""

    signal_id: str
    missing: tuple[str, ...]
    reason: str
    raised_at: datetime.datetime


@dataclass(frozen=True)
class ExplanationRecord:
    """可解释性档案（frozen；入审计链 + 按 signal_id 回放）。"""

    signal_id: str
    symbol: str
    direction: str
    confidence: float
    reason_chain: ReasonChain
    emitted_at: datetime.datetime
    recorded_at: datetime.datetime


class SignalExplainabilityGuarantor:
    """可解释性强制保障器（纯内存/DI；缺失即阻断）。

    强制契约：信号输出必须携带理由链三要素（触发因子/规则命中/置信度依据）。
    缺失 → 告警（alert_sink）+ 阻断（抛 ExplainabilityGuarantorError）；
    齐全 → 先入审计链（audit_sink，对齐 decision_snapshot/signal_audit 语
    义）再入内存档案，支持按 signal_id 反查回放。audit_sink 未注入或写失
    败均 Fail-Closed（解释未入审计链 = 保障失败）。
    """

    def __init__(
        self,
        *,
        audit_sink: Callable[[ExplanationRecord], None] | None,
        alert_sink: Callable[[ExplainabilityViolation], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if audit_sink is None:
            raise ExplainabilityGuarantorError(
                "audit_sink 未注入（强制契约：解释必须入审计链）"
            )
        self._audit_sink = audit_sink
        self._alert_sink = alert_sink
        self._clock = clock or datetime.datetime.now
        self._records: dict[str, ExplanationRecord] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _missing_elements(chain: ReasonChain) -> tuple[str, ...]:
        missing: list[str] = []
        if not chain.trigger_factors or any(not f for f in chain.trigger_factors):
            missing.append("触发因子")
        if not chain.rule_hits or any(not r for r in chain.rule_hits):
            missing.append("规则命中")
        if not chain.confidence_basis:
            missing.append("置信度依据")
        return tuple(missing)

    def _alert(self, violation: ExplainabilityViolation) -> None:
        _log.warning("可解释性违规: %s 缺失 %s", violation.signal_id, "/".join(violation.missing))
        if self._alert_sink is not None:
            try:
                self._alert_sink(violation)
            except Exception:  # noqa: BLE001 — 告警异常不改变阻断语义
                _log.exception("alert_sink 告警失败: %s", violation.signal_id)

    # ── 强制校验 ──────────────────────────────────────────────────────────

    def enforce(
        self,
        *,
        signal_id: str,
        symbol: str,
        direction: str,
        confidence: float,
        reason_chain: ReasonChain,
        emitted_at: datetime.datetime,
    ) -> ExplanationRecord:
        """强制校验：三要素缺失 → 告警+阻断；齐全 → 入审计链 + 档案。"""
        if not signal_id:
            raise ExplainabilityGuarantorError("signal_id 为空")
        if not symbol:
            raise ExplainabilityGuarantorError("symbol 为空")
        if not direction:
            raise ExplainabilityGuarantorError("direction 为空")
        if not 0.0 <= confidence <= 1.0:
            raise ExplainabilityGuarantorError(
                f"confidence 须在 [0,1]，实际 {confidence!r}"
            )
        if not isinstance(reason_chain, ReasonChain):
            raise ExplainabilityGuarantorError(f"非法理由链类型: {type(reason_chain)!r}")
        if not isinstance(emitted_at, datetime.datetime):
            raise ExplainabilityGuarantorError("emitted_at 须为 datetime")
        if signal_id in self._records:
            raise ExplainabilityGuarantorError(f"signal_id 冲突: {signal_id!r} 已入档")
        missing = self._missing_elements(reason_chain)
        if missing:
            reason = f"信号 {signal_id} 理由链三要素缺失: {'/'.join(missing)}（阻断）"
            self._alert(
                ExplainabilityViolation(
                    signal_id=signal_id,
                    missing=missing,
                    reason=reason,
                    raised_at=self._clock(),
                )
            )
            raise ExplainabilityGuarantorError(reason)
        record = ExplanationRecord(
            signal_id=signal_id,
            symbol=symbol,
            direction=direction,
            confidence=confidence,
            reason_chain=reason_chain,
            emitted_at=emitted_at,
            recorded_at=self._clock(),
        )
        try:
            self._audit_sink(record)
        except Exception as exc:  # 解释未入审计链 = 保障失败，Fail-Closed
            _log.exception("audit_sink 写入失败: %s", signal_id)
            raise ExplainabilityGuarantorError(
                f"解释入审计链失败: {signal_id!r}（{exc!r}）"
            ) from exc
        self._records[signal_id] = record
        return record

    # ── 回放反查 ──────────────────────────────────────────────────────────

    def replay(self, signal_id: str) -> ExplanationRecord:
        """按 signal_id 反查回放（未知 → Fail-Closed）。"""
        record = self._records.get(signal_id)
        if record is None:
            raise ExplainabilityGuarantorError(
                f"未知 signal_id: {signal_id!r}（无解释档案）"
            )
        return record

    def has(self, signal_id: str) -> bool:
        """signal_id 是否已入解释档案。"""
        return signal_id in self._records

    def records(self) -> list[ExplanationRecord]:
        """全部解释档案（按 (recorded_at, signal_id) 确定性排序）。"""
        return sorted(self._records.values(), key=lambda r: (r.recorded_at, r.signal_id))
