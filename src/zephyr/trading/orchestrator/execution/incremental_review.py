from typing import Final

# [BLUEPRINT] SRC-018 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.trading.orchestrator.execution.incremental_review
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_incremental_review | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from dataclasses import dataclass


@dataclass
class ReviewChunk:
    level: str
    chunk_id: str
    time_budget_minutes: int = 30


REVIEW_DIMENSIONS: Final[dict[str, str]] = {
    "consistency": "语义割裂检测",
    "accuracy": "数字引用验证",
    "completeness": "context manifest字段全",
    "traceability": "正反向链路",
    "token_efficiency": "审查Token/成果",
    "no_regression": "无下降→对比上次",
}
