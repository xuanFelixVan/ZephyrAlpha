"""
Can-I-Deploy 预部署门禁（GATE-CDC-1）

依据：MOD-MASTER-001 蓝图 §十六 CT-CDC-001
4项预部署检查：consumer_expectations/schema_version/contract_consistency/health。
"""

from __future__ import annotations

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

    def check(self,
              consumer_expectations_ok: bool = True,
              schema_version_ok: bool = True,
              contract_consistency_ok: bool = True,
              health_ok: bool = True) -> CanIDeployResult:
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
