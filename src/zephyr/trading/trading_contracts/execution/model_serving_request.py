# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.model_serving_request
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] l11-ml-platform
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_model_serving_request | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
