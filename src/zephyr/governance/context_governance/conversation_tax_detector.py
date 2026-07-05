# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.conversation_tax_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_conversation_tax_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from dataclasses import dataclass, field


@dataclass
class TaxAssessment:
    content_drift: float
    efficiency_decay: float
    dead_conversation_prob: float
    cost_per_meaningful_reply: float
    should_summarize: bool
    should_terminate: bool
    recommendation: str
    timestamp: float = field(default_factory=time.time)


class ConversationTaxDetector:
    def __init__(self, drift_window: int = 10, decay_threshold: float = 0.6):
        self._drift_window = drift_window
        self._decay_threshold = decay_threshold
        self._reply_lengths: list[int] = []
        self._reply_times: list[float] = []
        self._meaningful_actions: int = 0
        self._total_cost: float = 0.0
        self._topic_embeddings: list[tuple[float, ...]] = []
        self._last_assessment: TaxAssessment | None = None

    def record_reply(self, output_length: int, cost: float, topic_vector: tuple[float, ...] | None = None) -> None:
        now = time.time()
        self._reply_lengths.append(output_length)
        self._reply_times.append(now)
        self._total_cost += cost
        if output_length > 20:
            self._meaningful_actions += 1
        if topic_vector:
            self._topic_embeddings.append(topic_vector)
            if len(self._topic_embeddings) > self._drift_window:
                self._topic_embeddings.pop(0)

    def assess(self) -> TaxAssessment:
        drift = self._compute_drift()
        decay = self._compute_efficiency_decay()
        dead_prob = self._compute_dead_conversation_prob()
        cost_per = self._total_cost / max(self._meaningful_actions, 1)
        should_summarize = drift > 0.5 or decay > self._decay_threshold
        should_terminate = dead_prob > 0.8

        if should_terminate:
            rec = "TERMINATE: 对话已无产出价值"
        elif should_summarize:
            rec = "SUMMARIZE: 建议压缩上下文保留关键信息"
        elif decay > 0.4:
            rec = "WARN: 效率下降，注意对话税"
        else:
            rec = "OK: 对话效率正常"

        self._last_assessment = TaxAssessment(
            content_drift=drift,
            efficiency_decay=decay,
            dead_conversation_prob=dead_prob,
            cost_per_meaningful_reply=cost_per,
            should_summarize=should_summarize,
            should_terminate=should_terminate,
            recommendation=rec,
        )
        return self._last_assessment

    def _compute_drift(self) -> float:
        if len(self._topic_embeddings) < 2:
            return 0.0
        recent = self._topic_embeddings[-self._drift_window // 2 :]
        older = self._topic_embeddings[: self._drift_window // 2]
        if not recent or not older:
            return 0.0
        recent_avg = tuple(sum(c) / len(c) for c in zip(*recent, strict=False))
        older_avg = tuple(sum(c) / len(c) for c in zip(*older, strict=False))
        diff = sum((a - b) ** 2 for a, b in zip(recent_avg, older_avg, strict=False)) ** 0.5
        return min(diff, 1.0)

    def _compute_efficiency_decay(self) -> float:
        if len(self._reply_lengths) < 3:
            return 0.0
        recent = self._reply_lengths[-3:]
        older = self._reply_lengths[: max(1, len(self._reply_lengths) - 3)]
        if not older:
            return 0.0
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        # 5.50.2 修复：原 == 0 浮点精确比较，older 含浮点求和产生 1e-17 残差时 == 0 失败，
        # 后续 recent_avg / older_avg 除以极小值产生 inf。改用容差比较。
        if abs(older_avg) < 1e-9:
            return 0.0
        decay = 1.0 - (recent_avg / older_avg)
        return max(0.0, decay)

    def _compute_dead_conversation_prob(self) -> float:
        if not self._reply_times:
            return 0.0
        now = time.time()
        time_since_last = now - self._reply_times[-1]
        if time_since_last > 600:
            return 0.9
        if time_since_last > 300:
            return 0.6
        if time_since_last > 120:
            return 0.3
        return 0.0

    def last_assessment(self) -> TaxAssessment | None:
        return self._last_assessment

    def reset(self) -> None:
        self._reply_lengths.clear()
        self._reply_times.clear()
        self._meaningful_actions = 0
        self._total_cost = 0.0
        self._topic_embeddings.clear()
        self._last_assessment = None
