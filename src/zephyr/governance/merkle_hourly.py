# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §8
# [MODULE] zephyr.governance.merkle_hourly
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] audit-orchestrator.integrity(完整性校验时验证小时根哈希)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现Merkle逻辑; 仅桥接HourlyMerkleAggregator
# [MODIFY-GUARD] HourlyMerkleAggregator API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回空结果
# [TESTS] tests/audit-orchestrator/test_merkle_hourly.py
# [A_module] module_id=MOD-GOV_merkle_hourly | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["MerkleHourlyBridge"]


class MerkleHourlyBridge:
    def __init__(self) -> None:
        self._aggregator = None
        self._available = False
        try:
            from zephyr.gov_audit.merkle_hourly import HourlyMerkleAggregator

            self._aggregator = HourlyMerkleAggregator()
            self._available = True
        except ImportError:
            logger.warning("HourlyMerkleAggregator not available")
        except Exception as exc:
            logger.warning("HourlyMerkleAggregator init failed: %s", exc, exc_info=True)

    def aggregate(self, hour_key: str | None = None) -> dict[str, Any] | None:
        if not self._available or self._aggregator is None:
            return None
        try:
            result = self._aggregator.aggregate(hour_key)
            if result is None:
                return None
            return result.model_dump()
        except Exception as exc:
            logger.error("MerkleHourlyBridge.aggregate failed: %s", exc, exc_info=True)
            return None

    def verify(self, hour_key: str, expected_root: str) -> bool:
        if not self._available or self._aggregator is None:
            return False
        try:
            result = self._aggregator.aggregate(hour_key)
            if result is None:
                return False
            return result.merkle_root == expected_root
        except Exception as exc:
            logger.error("MerkleHourlyBridge.verify failed: %s", exc, exc_info=True)
            return False

    def is_available(self) -> bool:
        return self._available