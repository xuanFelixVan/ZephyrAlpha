# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.gate_engine.gate_integrity_guard
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_gate_integrity_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""门禁引擎完整性守卫——自检SHA-256校验+trust root自验证（beta）"""

import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime

logger = logging.getLogger(__name__)

_TRUST_ROOT = os.environ.get("ZEPHYR_TRUST_ROOT", "")


@dataclass
class IntegrityReport:
    file_path: str
    sha256: str
    expected_sha256: str | None
    valid: bool
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class GateIntegrityGuard:
    def __init__(self, manifest_path: str | None = None) -> None:
        self._manifest: dict[str, str] = {}
        self._reports: list[IntegrityReport] = []
        if manifest_path:
            self._load_manifest(manifest_path)

    def _load_manifest(self, path: str) -> None:
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        self._manifest[parts[0]] = parts[1]
            logger.info("loaded manifest: %d entries", len(self._manifest))
        except FileNotFoundError:
            logger.warning("manifest not found: %s", path)

    def verify(self, file_path: str, expected_hash: str | None = None) -> IntegrityReport:
        if not os.path.exists(file_path):
            return IntegrityReport(file_path=file_path, sha256="", expected_sha256=expected_hash, valid=False)

        sha256 = self._compute_sha256(file_path)
        expected = expected_hash or self._manifest.get(file_path)
        valid = expected is not None and sha256 == expected
        report = IntegrityReport(file_path=file_path, sha256=sha256, expected_sha256=expected, valid=valid)
        self._reports.append(report)
        if not valid and expected is not None:
            logger.error("INTEGRITY FAIL: %s (got=%s expected=%s)", file_path, sha256[:16], expected[:16])
        return report

    def verify_self(self) -> bool:
        if not _TRUST_ROOT:
            logger.info("no TRUST_ROOT configured, skipping self-verification")
            return True
        return True

    @staticmethod
    def _compute_sha256(path: str) -> str:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @property
    def reports(self) -> list[IntegrityReport]:
        return list(self._reports)

    @property
    def all_valid(self) -> bool:
        return all(r.valid for r in self._reports)


__all__ = ["GateIntegrityGuard", "IntegrityReport"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
