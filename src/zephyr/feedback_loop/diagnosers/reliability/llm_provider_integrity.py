# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.llm_provider_integrity
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_llm_provider_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""LLM Provider Integrity — v0.15.0 R217

Blindspot: LLM provider may return compromised/manipulated responses; FLE assumes honest provider.
Risk: R217 — Man-in-the-middle poisons LLM API response; FLE executes poisoned diagnosis.

Mitigation: Multi-provider cross-validation of critical LLM responses.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass
class ProviderResponse:
    provider: str
    query_hash: str
    response_hash: str
    timestamp: float = 0.0


@dataclass
class LLMProviderIntegrity:
    responses: dict[str, list[ProviderResponse]] = field(default_factory=dict)
    min_providers: int = 2
    hash_match_required: float = 0.5

    def record(self, query: str, response: str, provider: str) -> ProviderResponse:
        q_hash = hashlib.sha256(query.encode()).hexdigest()[:12]
        r_hash = hashlib.sha256(response.encode()).hexdigest()[:12]
        pr = ProviderResponse(provider=provider, query_hash=q_hash, response_hash=r_hash)
        key = q_hash
        if key not in self.responses:
            self.responses[key] = []
        self.responses[key].append(pr)
        return pr

    def consensus_ok(self, query: str) -> bool:
        q_hash = hashlib.sha256(query.encode()).hexdigest()[:12]
        records = self.responses.get(q_hash, [])
        if len(records) < self.min_providers:
            return False
        hashes = [r.response_hash for r in records]
        majority_count = max(hashes.count(h) for h in set(hashes))
        return majority_count / len(hashes) >= self.hash_match_required
