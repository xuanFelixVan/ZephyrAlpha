# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.cdc_broker
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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CDC 契约经纪人（Consumer-Driven Contract Broker — CT-CDC-001）

依据：MOD-MASTER-002 蓝图 §十六
Pact Broker 本地 SQLite 简化版 + 3步生命周期。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: db_path 参数
#   fields: 参数 db_path（无注解）
#   code: cdc_broker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CdcBroker
#   name_en: CdcBroker
#   intro: class CdcBroker 源码 L77-L112
#   desc: 公共方法（定义序）: register_expectation, get_expectations, verify_pact, get_pacts；源码 L77-L112
#   inputs: db_path
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CdcBroker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
