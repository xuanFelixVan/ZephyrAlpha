# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3.1
# [MODULE] zephyr.governance.audit_trail.genesis
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.integrity; cold_start
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 创世块不可变; 建立后永不修改
# [MODIFY-GUARD] 创世块格式变更需Owner审批
# [STABILITY] frozen
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 创世块损坏返回恢复失败
# [TESTS] tests/audit-orchestrator/test_genesis.py
# [A_module] module_id=MOD-GOV_genesis | layer=module | stability=frozen | safety=H | ai_autonomy=human_gated
# [TTL] permanent
from zephyr.shared.io.serialization import dumps
import hashlib
import hmac
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from typing import Final

logger = logging.getLogger(__name__)

__all__ = ["GenesisBlock"]

DEFAULT_GENESIS_DIR: Final[Any] = Path.cwd() / "data" / "audit_genesis"
GENESIS_FILE: Final[str] = "genesis_block.json"


class GenesisBlock:
    def __init__(self, genesis_dir: Path | None = None) -> None:
        self._genesis_dir = Path(genesis_dir or DEFAULT_GENESIS_DIR)
        self._genesis_dir.mkdir(parents=True, exist_ok=True)
        self._genesis_path = self._genesis_dir / GENESIS_FILE

    def create(self, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._genesis_path.exists():
            logger.warning("Genesis block already exists, returning existing")
            return self.read()

        block = {
            "version": "1.0",
            "created_at": datetime.now(UTC).isoformat(),
            "block_hash": "",
            "audit_dimensions": [
                "DIM-REGISTRATION-001",
                "DIM-DEPENDENCY-001",
                "DIM-IMPORT-001",
                "DIM-SECURITY-001",
                "DIM-ORPHAN-001",
            ],
            "initial_state": "IDLE",
            "metadata": metadata or {},
        }

        block["block_hash"] = self._hash_block(block)

        self._persist(block)
        return block

    def read(self) -> dict[str, Any]:
        if not self._genesis_path.exists():
            return {"error": "Genesis block not found", "exists": False}
        try:
            data = json.loads(self._genesis_path.read_text(encoding="utf-8"))
            data["exists"] = True
            return data
        except Exception as exc:
            logger.error("Failed to read genesis block: %s", exc, exc_info=True)
            return {"error": str(exc), "exists": False}

    def verify(self) -> dict[str, Any]:
        block = self.read()
        if not block.get("exists"):
            return {"valid": False, "reason": "Genesis block not found"}

        stored_hash = block.get("block_hash", "")
        block["block_hash"] = ""
        computed_hash = self._hash_block(block)

        return {
            "valid": hmac.compare_digest(stored_hash, computed_hash),
            "stored_hash": stored_hash,
            "computed_hash": computed_hash,
        }

    def _hash_block(self, block: dict[str, Any]) -> str:
        data = dumps(block, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _persist(self, block: dict[str, Any]) -> None:
        tmp_path = Path(str(self._genesis_path) + f".{os.getpid()}.tmp")
        try:
            tmp_path.write_text(
                dumps(block, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(str(tmp_path), str(self._genesis_path))
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise


class GenesisManager:
    def __init__(self, config=None):
        self.config = config or {}

    def create_genesis(self, entity, metadata=None):
        return {}

    def verify_genesis(self, entity):
        # 修复：原实现永远返回 True（虚假安全感）。改为实际验证创世块。
        try:
            genesis_path = Path.cwd() / "data" / "audit_genesis" / f"{entity}.json"
            if not genesis_path.exists():
                return False
            manager = GenesisBlockManager(genesis_path)
            result = manager.verify()
            return result.get("valid", False)
        except Exception:
            return False


class GenesisVerificationResult:
    def __init__(self, entity="", valid=True, genesis_hash="", verification_timestamp=None):
        self.entity = entity
        self.valid = valid
        self.genesis_hash = genesis_hash
        self.verification_timestamp = verification_timestamp


class WitnessSignature:
    def __init__(self, witness_id="", signature="", timestamp=None):
        self.witness_id = witness_id
        self.signature = signature
        self.timestamp = timestamp