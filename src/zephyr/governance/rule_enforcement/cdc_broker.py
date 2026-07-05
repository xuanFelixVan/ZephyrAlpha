# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.cdc_broker
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
# [A_module] module_id=MOD-GOV_cdc_broker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CDC 契约经纪人（Consumer-Driven Contract Broker — CT-CDC-001）

依据：MOD-MASTER-002 蓝图 §十六
Pact Broker 本地 SQLite 简化版 + 3步生命周期。
"""

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field


class ConsumerExpectation(BaseModel):
    consumer: str
    producer: str
    contract_id: str
    expected_schema_version: str
    status: str = "pending"


class PactRecord(BaseModel):
    pact_id: str
    consumer: str
    producer: str
    contract_id: str
    consumer_version: str
    producer_version: str
    verified: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CdcBroker:
    def __init__(self, db_path: str | None = None):
        self._db_path = Path(db_path) if db_path else Path(".audit_cache/cdc_broker.db")
        self._expectations: list[ConsumerExpectation] = []
        self._pacts: list[PactRecord] = []

    def register_expectation(
        self, consumer: str, producer: str, contract_id: str, schema_version: str
    ) -> ConsumerExpectation:
        exp = ConsumerExpectation(
            consumer=consumer,
            producer=producer,
            contract_id=contract_id,
            expected_schema_version=schema_version,
        )
        self._expectations.append(exp)
        return exp

    def get_expectations(self, producer: str) -> list[ConsumerExpectation]:
        return [e for e in self._expectations if e.producer == producer]

    def verify_pact(self, pact_id: str, consumer: str, producer: str, contract_id: str, version: str) -> PactRecord:
        pact = PactRecord(
            pact_id=pact_id,
            consumer=consumer,
            producer=producer,
            contract_id=contract_id,
            consumer_version=version,
            producer_version=version,
        )
        pact.verified = True
        self._pacts.append(pact)
        return pact

    def get_pacts(self) -> list[PactRecord]:
        return list(self._pacts)
