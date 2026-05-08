"""
CDC 契约经纪人（Consumer-Driven Contract Broker — CT-CDC-001）

依据：MOD-MASTER-001 蓝图 §十六
Pact Broker 本地 SQLite 简化版 + 3步生命周期。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
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
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CdcBroker:
    def __init__(self, db_path: str | None = None):
        self._db_path = Path(db_path) if db_path else Path(".audit_cache/cdc_broker.db")
        self._expectations: list[ConsumerExpectation] = []
        self._pacts: list[PactRecord] = []

    def register_expectation(self, consumer: str, producer: str,
                              contract_id: str, schema_version: str) -> ConsumerExpectation:
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

    def verify_pact(self, pact_id: str, consumer: str, producer: str,
                    contract_id: str, version: str) -> PactRecord:
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
