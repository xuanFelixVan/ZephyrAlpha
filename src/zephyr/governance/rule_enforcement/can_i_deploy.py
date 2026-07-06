# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.can_i_deploy
# [DOMAIN] D_GOV_RULE
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
# [A_module] module_id=MOD-GOV_can_i_deploy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Can-I-Deploy 预部署门禁（GATE-CDC-1）

依据：MOD-MASTER-002 蓝图 §十六 CT-CDC-001
4项预部署检查：consumer_expectations/schema_version/contract_consistency/health。
"""

from enum import Enum

from pydantic import BaseModel, Field


class DeployCheck(str, Enum):
    CONSUMER_EXPECTATIONS = "consumer_expectations"
    SCHEMA_VERSION = "schema_version"
    CONTRACT_CONSISTENCY = "contract_consistency"
    HEALTH = "health"


class CanIDeployResult(BaseModel):
    allowed: bool
    checks: dict[str, bool] = Field(default_factory=dict)
    blockers: list[str] = Field(default_factory=list)


class CanIDeploy:
    def __init__(self):
        self._check_results: dict[str, bool] = {}

    def check(
        self,
        *,
        consumer_expectations_ok: bool = True,
        schema_version_ok: bool = True,
        contract_consistency_ok: bool = True,
        health_ok: bool = True,
    ) -> CanIDeployResult:
        checks = {
            "consumer_expectations": consumer_expectations_ok,
            "schema_version": schema_version_ok,
            "contract_consistency": contract_consistency_ok,
            "health": health_ok,
        }
        blockers = [k for k, v in checks.items() if not v]

        return CanIDeployResult(
            allowed=len(blockers) == 0,
            checks=checks,
            blockers=blockers,
        )
