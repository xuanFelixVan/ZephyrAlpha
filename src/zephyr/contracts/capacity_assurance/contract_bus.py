"""ContractBus loader — 加载全部44条容量保障契约的Pydantic v2 Schema（DD-9三批迁移）.

对标蓝图 §5.3 ContractBus 分三批迁移:
  批1 (15条): 基础设施层 — SLO/Error Budget/Token Budget/Kill Switch/Sandbox/Graceful Degradation
  批2 (15条): 治理层 — Provenance/AI审计守卫/TechStackValidator/Governance Loop
  批3 (14条): 集成层 — OTel/W3C/跨模块CT-1~4/DR/容量预测/语义缓存
"""

from typing import Dict, List, Optional, Type
from pydantic import BaseModel

from zephyr.contracts.capacity_assurance.batch1_infra import BATCH1_CONTRACTS
from zephyr.contracts.capacity_assurance.batch2_governance import BATCH2_CONTRACTS
from zephyr.contracts.capacity_assurance.batch3_integration import BATCH3_CONTRACTS


class ContractBusLoader:
    """ContractBus 契约加载器——加载并校验全部 44 条 Pydantic v2 契约 Schema."""

    def __init__(self):
        self._contracts: Dict[str, Type[BaseModel]] = {}
        self._load_all()

    def _load_all(self) -> None:
        for batch_contracts in [BATCH1_CONTRACTS, BATCH2_CONTRACTS, BATCH3_CONTRACTS]:
            for contract_id, model in batch_contracts.items():
                if contract_id in self._contracts:
                    raise ValueError(f"Duplicate contract ID: {contract_id}")
                self._contracts[contract_id] = model

    @property
    def contract_count(self) -> int:
        return len(self._contracts)

    @property
    def batch_summary(self) -> Dict[str, int]:
        return {
            "batch1_infra": len(BATCH1_CONTRACTS),
            "batch2_governance": len(BATCH2_CONTRACTS),
            "batch3_integration": len(BATCH3_CONTRACTS),
            "total": self.contract_count,
        }

    def get_contract(self, contract_id: str) -> Optional[Type[BaseModel]]:
        return self._contracts.get(contract_id)

    def list_contracts(self) -> List[str]:
        return sorted(self._contracts.keys())

    def validate_payload(self, contract_id: str, data: dict) -> BaseModel:
        model = self.get_contract(contract_id)
        if model is None:
            raise KeyError(f"Contract not found: {contract_id}")
        return model(**data)


_loader: Optional[ContractBusLoader] = None


def get_contract_bus_loader() -> ContractBusLoader:
    global _loader
    if _loader is None:
        _loader = ContractBusLoader()
    return _loader
