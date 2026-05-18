# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.execution.model_serving_request

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l11_ml_platform

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
# ==== BEGIN CODGEN:CTR-P1-004 ====

from dataclasses import dataclass, field

@dataclass(frozen=True)
class ModelServingRequest:
    model_id: str
    model_version: str
    request_id: str
    idempotency_key: str
    input_features: dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-004 ====
