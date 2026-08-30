# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.llm_provider_integrity
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
LLM Provider Integrity — v0.15.0 R217

Blindspot: LLM provider may return compromised/manipulated responses; FLE assumes honest provider.
Risk: R217 — Man-in-the-middle poisons LLM API response; FLE executes poisoned diagnosis.

Mitigation: Multi-provider cross-validation of critical LLM responses.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: llm_provider_integrity.py
# 层: 算法
# - id: A1
#   name_zh: ① LLMProviderIntegrity
#   name_en: LLMProviderIntegrity
#   intro: class LLMProviderIntegrity 源码 L69-L91
#   desc: 公共方法（定义序）: record, consensus_ok；源码 L69-L91
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: LLMProviderIntegrity
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
