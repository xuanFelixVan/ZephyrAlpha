---
module_id: KE-1832
status: active
title: 2.249 Decision Outcome Delay Attribution Registry - outcome_delay_attribution.py
category: module_blueprint
ttl: permanent
---

# 2.249 Decision Outcome Delay Attribution Registry - outcome_delay_attribution.py

2.249 Decision Outcome Delay Attribution Registry - outcome_delay_attribution.py (🆕 v0.23.0 - 盲点298 — FLE操作的延迟效应无法正确归因→强化的可能是错误的action)

**致命问题**：FLE的某些操作有延时效应。ADJUST_CONFIG连接池大小→第1天可能看不到效果→第3天内存使用率才下降→但到第3天FLE已经做了5个其他操作→当前效果到底归因于哪个？如果归因错误→FLE可能把延迟效应的功劳归给错误的action→强化错误的action模式→弱化真正有效的action→Action Model被毒化→长期性能退化。这是Reinforcement Learning中经典的Credit Assignment Problem在AIOps中的表现。
**对标**：DeepMind RUDDER Reward Redistribution + Google Rliable Benchmark + Deep RL Credit Assignment + Eligibility Traces TD(λ) + MC Dropout Uncertainty

```python
@dataclass
class PendingOutcome:
    action_id: str
    action_type: str
    expected_effect_lag_min: float   # 期望的影响延迟
    expected_max_lag_min: float      # 最晚显现时间
    current_wait_hours: float        # 已经等待了多久
    attribution_confidence: float    # 当前我们对因果链的信心
    registered_at: datetime
    outcome_manifested: bool
    attributed_correctly: bool | None  # None=还没显现

class OutcomeDelayAttributionRegistry:
    MAX_PENDING_REGISTRY_SIZE: int = 100
    ATTRIBUTION_TIMEOUT_MULTIPLIER: float = 3.0  # 3×expected_lag后仍不显现→标记TIMEOUT

    async def register_delayed_outcome(self, action_id: str) -> None:
        expected_lag = await self._estimate_effect_lag(action_id)
        self.pending_registry.append(PendingOutcome(
            action_id=action_id,
            action_type=await self._resolve_action_type(action_id),
            expected_effect_lag_min=expected_lag,
            expected_max_lag_min=expected_lag * self.ATTRIBUTION_TIMEOUT_MULTIPLIER,
            current_wait_hours=0.0,
            attribution_confidence=0.5,  # 初始50/50
            registered_at=datetime.now(),
            outcome_manifested=False,
            attributed_correctly=None))
        if len(self.pending_registry) > self.MAX_PENDING_REGISTRY_SIZE:
            oldest = self.pending_registry.pop(0)
            if not oldest.outcome_manifested:
                self.FLE.notify_owner("OUTCOME_TIMEOUT",
                    f"Action {oldest.action_id} ({oldest.action_type}) registered "
                    f"{oldest.current_wait_hours:.1f}h ago—outcome NEVER manifested. "
                    f"FLE will PENALIZE this action type's confidence score.")

    async def attribute_manifested_outcomes(self,
                                              current_system_state: dict) -> list[AttributionResult]:
        results = []
        for pending in list(self.pending_registry):
            pending.current_wait_hours = (datetime.now() - pending.registered_at).total_seconds() / 3600
            if pending.current_wait_hours > pending.expected_effect_lag_min:
                prob_causal = await self._compute_causal_probability(pending.action_id, current_system_state)
                if prob_causal > 0.7:
                    pending.outcome_manifested = True
                    pending.attributed_correctly = True
                    results.append(AttributionResult(action=pending, causal=True, confidence=prob_causal))
                elif pending.current_wait
