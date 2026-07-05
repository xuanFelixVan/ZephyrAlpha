# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared.schema.base_config
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] shared.schema.schemas; gates.task_types; shared.schema.audit_types; kb.knowledge_types
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] BASE_CONFIG MUST align with  §4.2
# [MODIFY-GUARD]
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] N/A
# [TESTS] tests/test_schemas.py
# [A_module] module_id=MOD-SHR_base_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from enum import Enum

from pydantic import ConfigDict

__all__ = [
    "BASE_CONFIG",
    "Classification",
    "EvolutionPolicy",
]


class Classification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class EvolutionPolicy(str, Enum):
    FROZEN = "frozen"
    EXTENDABLE = "extendable"
    REWRITABLE = "rewritable"


BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    populate_by_name=True,
    validate_assignment=True,
)
