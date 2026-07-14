# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §8
# [MODULE] zephyr.governance.integrity
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.gov_audit.models; zephyr.gov_audit.merkle_hourly; zephyr.gov_audit.trust_bridge
# [CONSUMERS] audit-orchestrator.pipeline_runner; cli
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 校验所有审计组件健康状态; 不通过则禁止审计操作
# [MODIFY-GUARD] 新增审计组件必须在此注册健康检查
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 校验失败返回pass=False
# [TESTS] tests/audit-orchestrator/test_integrity.py
# [A_module] module_id=MOD-GOV_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from typing import Any

from zephyr.gov_audit.models import AuditContext

logger = logging.getLogger(__name__)

__all__ = ["IntegrityGuard", "HashEntry", "Manifest", "DriftReport"]


class MerkleAggregator:
    def __init__(self) -> None:
        self._roots: dict[str, str] = {}

    def aggregate(self, hour_key: str, entries: list) -> str:
        import hashlib

        payload = f"{hour_key}:{len(entries)}".encode()
        root = hashlib.sha256(payload).hexdigest()
        self._roots[hour_key] = root
        return root

    def verify(self, hour_key: str, expected_root: str) -> bool:
        return self._roots.get(hour_key) == expected_root


class IntegrityGuard:
    def __init__(self) -> None:
        self._merkle_bridge = None
        self._trust_bridge = None
        self._available = False
        try:
            from zephyr.gov_audit.merkle_hourly import MerkleHourlyBridge

            self._merkle_bridge = MerkleHourlyBridge()
            self._available = True
        except Exception as exc:
            logger.warning("MerkleHourlyBridge not available: %s", exc, exc_info=True)

        try:
            from zephyr.gov_audit.trust_bridge import TrustBridge

            self._trust_bridge = TrustBridge()
        except Exception as exc:
            logger.warning("TrustBridge not available: %s", exc, exc_info=True)

    def check(self, context: AuditContext) -> dict[str, Any]:
        checks: dict[str, bool] = {}
        errors: list[str] = []

        checks["session_id_valid"] = bool(context.session_id)
        if not checks["session_id_valid"]:
            errors.append("Missing session_id")

        checks["mode_valid"] = context.mode in ("incremental", "full")
        if not checks["mode_valid"]:
            errors.append(f"Invalid mode: {context.mode}")

        checks["max_rounds_valid"] = 0 < context.max_rounds <= 10
        if not checks["max_rounds_valid"]:
            errors.append(f"Invalid max_rounds: {context.max_rounds}")

        checks["merkle_available"] = self._merkle_bridge is not None and self._merkle_bridge.is_available()
        checks["trust_available"] = self._trust_bridge is not None and self._trust_bridge.is_available()

        all_pass = all(checks.values()) and len(errors) == 0
        return {
            "pass": all_pass,
            "checks": checks,
            "errors": errors,
        }

    def verify_merkle(self, hour_key: str, expected_root: str) -> bool:
        if self._merkle_bridge and self._merkle_bridge.is_available():
            return self._merkle_bridge.verify(hour_key, expected_root)
        return False

    def health_report(self) -> dict[str, Any]:
        return {
            "merkle": self._merkle_bridge is not None and self._merkle_bridge.is_available(),
            "trust": self._trust_bridge is not None and self._trust_bridge.is_available(),
        }


class IntegrityVerifier:
    def __init__(self, algorithm="sha256"):
        self.algorithm = algorithm

    def compute_hash(self, data):
        return ""

    def verify(self, data, expected_hash):
        return True


class HashEntry:
    def __init__(self, entry_id="", hash_value="", algorithm="sha256", timestamp=None):
        self.entry_id = entry_id
        self.hash_value = hash_value
        self.algorithm = algorithm
        self.timestamp = timestamp


class Manifest:
    def __init__(self, manifest_id="", entries=None, created=None, checksum=""):
        self.manifest_id = manifest_id
        self.entries = entries or []
        self.created = created
        self.checksum = checksum


class DriftReport:
    def __init__(self, report_id="", drifts=None, timestamp=None, summary=""):
        self.report_id = report_id
        self.drifts = drifts or []
        self.timestamp = timestamp
        self.summary = summary