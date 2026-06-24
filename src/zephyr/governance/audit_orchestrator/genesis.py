# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §3.1
# [MODULE] zephyr.governance.audit_trail.genesis
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestrator.__init__
# [CONSUMERS] audit-orchestrator.integrity; cold_start
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 创世块不可变; 建立后永不修改
# [MODIFY-GUARD] 创世块格式变更需Owner审批
# [STABILITY] frozen
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 创世块损坏返回恢复失败
# [TESTS] tests/audit-orchestrator/test_genesis.py
# [A_module] module_id=MOD-GOV_genesis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["GenesisBlock"]

DEFAULT_GENESIS_DIR = Path("data/audit_genesis")
GENESIS_FILE = "genesis_block.json"


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
            logger.error("Failed to read genesis block: %s", exc)
            return {"error": str(exc), "exists": False}

    def verify(self) -> dict[str, Any]:
        block = self.read()
        if not block.get("exists"):
            return {"valid": False, "reason": "Genesis block not found"}

        stored_hash = block.get("block_hash", "")
        block["block_hash"] = ""
        computed_hash = self._hash_block(block)

        return {
            "valid": stored_hash == computed_hash,
            "stored_hash": stored_hash,
            "computed_hash": computed_hash,
        }

    def _hash_block(self, block: dict[str, Any]) -> str:
        data = json.dumps(block, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _persist(self, block: dict[str, Any]) -> None:
        tmp_path = Path(str(self._genesis_path) + f".{os.getpid()}.tmp")
        try:
            tmp_path.write_text(
                json.dumps(block, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            os.replace(str(tmp_path), str(self._genesis_path))
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise
