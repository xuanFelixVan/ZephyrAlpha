# [BLUEPRINT] MOD-SIGQC-003 | docs/03_modules/_domain_signal_quality/signal_dedup/blueprint.md
# [MODULE] zephyr.signal_quality.signal_dedup
# [DOMAIN] D_SIGQC
# [DEPENDENCIES] 无（去重核心纯内存；clock/audit_sink 全注入）
# [CONSUMERS] 运行时装配批（信号汇流入库前去重 / 串谋检测复查审计回放）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 指纹四元组(标的/方向/逻辑标签/参数桶)等权相似度; 相似度严格>阈值(默认0.9)且落在时间窗(默认1日)内方合并; 合并保留最高置信度(同置信度先入档者优先); 每次裁决落审计回调; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal_quality/signal_dedup/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SignalDedupError(占位 ZA-SIGQC-UNREGISTERED-SIGNAL-DEDUP)——空字段/置信度越界/signal_id冲突/非法阈值/非法时间窗时抛
# [TESTS] tests/signal_quality/test_signal_dedup.py
# [A_module] module_id=MOD-SIGQC-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""SignalDedup — 信号去重器（MOD-SIGQC-003）。

B11-02594（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SIGQC-002，A7 技能
signal-dedup）：信号指纹（标的/方向/逻辑标签/参数桶四元组）+ 相似度>0.9
合并（保留最高置信度）+ 时间窗去重（默认当日）+ 去重决策落审计回调供串
谋检测复查。

查重分工（蓝图 §0）：factor/analysis/correlation_dedup=因子值相关性去重
（D_FACTOR，pandas 相关矩阵贪心，对象为因子非信号）；degradation_detector
（MOD-SIGQC-001）=信号质量降级检测（零交集）；本件=信号级指纹去重，纯内
存不依赖 pandas。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DedupAction",
    "DedupDecision",
    "DedupSignal",
    "SignalDedup",
    "SignalDedupError",
]

#: 指纹四元组分量数（等权相似度分母）
_FINGERPRINT_PARTS: Final[int] = 4


class SignalDedupError(Exception):
    """信号去重输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIGQC-UNREGISTERED-SIGNAL-DEDUP。
    """


class DedupAction(str, Enum):
    """去重裁决动作。"""

    KEPT_NEW = "kept_new"  # 窗内无相似信号，新信号直接保留
    MERGED_EXISTING_KEPT = "merged_existing_kept"  # 并入既有代表（既有置信度 ≥ 新信号）
    MERGED_NEW_KEPT = "merged_new_kept"  # 新信号置信度更高，取代既有代表


@dataclass(frozen=True)
class DedupSignal:
    """待去重信号（frozen）。指纹四元组 = (symbol, direction, logic_tag, param_bucket)。"""

    signal_id: str
    symbol: str
    direction: str
    logic_tag: str
    param_bucket: str
    confidence: float
    emitted_at: datetime.datetime


@dataclass(frozen=True)
class DedupDecision:
    """去重裁决（审计载荷，frozen；供串谋检测复查回放）。"""

    signal_id: str
    fingerprint: tuple[str, str, str, str]
    action: DedupAction
    representative_id: str
    matched_signal_id: str | None
    similarity: float
    reason: str
    decided_at: datetime.datetime


class SignalDedup:
    """信号指纹去重器（纯内存/DI）。

    - 相似度：指纹四元组等权匹配占比（4 分量全同=1.0，3 同=0.75 …）。
    - 合并：相似度**严格大于**阈值（默认 0.9）且 |emitted_at 差| ≤ 时间窗
      （默认 1 日）→ 合并；置信度最高者为代表（同置信度先入档者优先）。
    - 审计：每次 ingest 裁决（保留/合并）均落 audit_sink 供串谋检测复查；
      审计回调异常仅记日志，不阻断去重主链路。
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[DedupDecision], None] | None = None,
        similarity_threshold: float = 0.9,
        window: datetime.timedelta = datetime.timedelta(days=1),
    ) -> None:
        if not 0.0 < similarity_threshold <= 1.0:
            raise SignalDedupError(f"相似度阈值须在 (0,1]，实际 {similarity_threshold!r}")
        if window <= datetime.timedelta(0):
            raise SignalDedupError(f"时间窗须为正 timedelta，实际 {window!r}")
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._threshold = float(similarity_threshold)
        self._window = window
        self._kept: dict[str, DedupSignal] = {}  # 代表信号（插入序）
        self._merged: dict[str, str] = {}  # 被并 signal_id -> 代表 signal_id
        self._decisions: list[DedupDecision] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _validate(self, signal: DedupSignal) -> None:
        if not isinstance(signal, DedupSignal):
            raise SignalDedupError(f"非法信号类型: {type(signal)!r}")
        if not signal.signal_id:
            raise SignalDedupError("signal_id 为空")
        if not signal.symbol:
            raise SignalDedupError("标的 symbol 为空")
        if not signal.direction:
            raise SignalDedupError("方向 direction 为空")
        if not signal.logic_tag:
            raise SignalDedupError("逻辑标签 logic_tag 为空")
        if not isinstance(signal.emitted_at, datetime.datetime):
            raise SignalDedupError("emitted_at 须为 datetime")
        if not 0.0 <= signal.confidence <= 1.0:
            raise SignalDedupError(f"置信度须在 [0,1]，实际 {signal.confidence!r}")
        if signal.signal_id in self._kept or signal.signal_id in self._merged:
            raise SignalDedupError(f"signal_id 冲突: {signal.signal_id!r} 已入档")

    @staticmethod
    def _similarity(a: DedupSignal, b: DedupSignal) -> float:
        matches = (
            (a.symbol == b.symbol)
            + (a.direction == b.direction)
            + (a.logic_tag == b.logic_tag)
            + (a.param_bucket == b.param_bucket)
        )
        return matches / _FINGERPRINT_PARTS

    def _best_match(self, signal: DedupSignal) -> tuple[DedupSignal, float] | None:
        """窗内相似度超阈的最优代表（相似度降序，平手按 (emitted_at, signal_id)）。"""
        best: DedupSignal | None = None
        best_sim = 0.0
        for kept in self._kept.values():
            if abs(signal.emitted_at - kept.emitted_at) > self._window:
                continue
            sim = self._similarity(signal, kept)
            if sim <= self._threshold:
                continue
            if (
                best is None
                or sim > best_sim
                or (sim == best_sim and (kept.emitted_at, kept.signal_id) < (best.emitted_at, best.signal_id))
            ):
                best, best_sim = kept, sim
        if best is None:
            return None
        return best, best_sim

    def _audit(self, decision: DedupDecision) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(decision)
            except Exception:  # noqa: BLE001 — 审计异常不阻断去重主链路
                _log.exception("audit_sink 审计失败: %s", decision.signal_id)

    # ── 去重裁决 ──────────────────────────────────────────────────────────

    @staticmethod
    def fingerprint_of(signal: DedupSignal) -> tuple[str, str, str, str]:
        """信号指纹四元组（标的/方向/逻辑标签/参数桶）。"""
        return (signal.symbol, signal.direction, signal.logic_tag, signal.param_bucket)

    def ingest(self, signal: DedupSignal) -> DedupDecision:
        """去重裁决：校验（Fail-Closed）→ 窗内相似合并 → 裁决落审计。"""
        self._validate(signal)
        match = self._best_match(signal)
        if match is None:
            self._kept[signal.signal_id] = signal
            decision = DedupDecision(
                signal_id=signal.signal_id,
                fingerprint=self.fingerprint_of(signal),
                action=DedupAction.KEPT_NEW,
                representative_id=signal.signal_id,
                matched_signal_id=None,
                similarity=0.0,
                reason="窗内无相似信号，保留",
                decided_at=self._clock(),
            )
        else:
            kept, sim = match
            if signal.confidence > kept.confidence:
                del self._kept[kept.signal_id]
                self._kept[signal.signal_id] = signal
                self._merged[kept.signal_id] = signal.signal_id
                action = DedupAction.MERGED_NEW_KEPT
                representative_id = signal.signal_id
                reason = f"相似度 {sim:.2f} 超阈，新信号置信度更高取代代表"
            else:
                self._merged[signal.signal_id] = kept.signal_id
                action = DedupAction.MERGED_EXISTING_KEPT
                representative_id = kept.signal_id
                reason = f"相似度 {sim:.2f} 超阈，并入既有代表"
            decision = DedupDecision(
                signal_id=signal.signal_id,
                fingerprint=self.fingerprint_of(signal),
                action=action,
                representative_id=representative_id,
                matched_signal_id=kept.signal_id,
                similarity=sim,
                reason=reason,
                decided_at=self._clock(),
            )
        self._decisions.append(decision)
        self._audit(decision)
        return decision

    # ── 查询 ─────────────────────────────────────────────────────────────

    def is_merged(self, signal_id: str) -> bool:
        """signal_id 是否已被并入其他代表。"""
        return signal_id in self._merged

    def kept_signals(self) -> list[DedupSignal]:
        """当前代表信号（按 (emitted_at, signal_id) 确定性排序）。"""
        return sorted(self._kept.values(), key=lambda s: (s.emitted_at, s.signal_id))

    def decisions(self) -> list[DedupDecision]:
        """裁决历史（按 (decided_at, signal_id) 确定性排序）。"""
        return sorted(self._decisions, key=lambda d: (d.decided_at, d.signal_id))
